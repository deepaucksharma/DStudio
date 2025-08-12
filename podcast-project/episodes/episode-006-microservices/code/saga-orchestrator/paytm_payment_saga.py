#!/usr/bin/env python3
"""
PayTM-style Payment Saga Orchestrator
Complex payment processing with multiple services and rollback capabilities

जैसे PayTM में payment process करने के लिए multiple steps होते हैं -
Bank validation, KYC check, wallet balance, merchant verification etc.
अगर कोई step fail हो जाए तो सभी previous steps को safely rollback करना होता है
"""

import asyncio
import time
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import aioredis
import random

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PayTMSaga")

class SagaStatus(Enum):
    """Saga execution status - जैसे Mumbai local train का status"""
    INITIATED = "initiated"       # Journey started
    IN_PROGRESS = "in_progress"   # Running like express train
    COMPENSATING = "compensating" # Rolling back like return journey
    COMPLETED = "completed"       # Reached destination successfully
    FAILED = "failed"             # Journey cancelled due to issues
    TIMEOUT = "timeout"           # Delayed beyond acceptable limits

class PaymentMethod(Enum):
    """Payment methods supported by PayTM"""
    UPI = "upi"                   # UPI payments - most popular in India
    WALLET = "paytm_wallet"       # PayTM wallet balance
    CREDIT_CARD = "credit_card"   # Credit card payments
    DEBIT_CARD = "debit_card"     # Debit card payments
    NET_BANKING = "net_banking"   # Internet banking
    EMI = "emi"                   # EMI payments

@dataclass
class PaymentRequest:
    """Payment request details"""
    payment_id: str
    user_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    payment_method: PaymentMethod = PaymentMethod.UPI
    description: str = ""
    callback_url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SagaStep:
    """Individual saga step definition"""
    name: str
    action_func: Callable
    compensation_func: Callable
    timeout_seconds: int = 30
    retry_count: int = 3
    is_critical: bool = True  # If false, failure won't trigger compensation

@dataclass
class StepResult:
    """Result of saga step execution"""
    step_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SagaExecution:
    """Complete saga execution context"""
    saga_id: str
    payment_request: PaymentRequest
    status: SagaStatus = SagaStatus.INITIATED
    current_step: int = 0
    completed_steps: List[StepResult] = field(default_factory=list)
    saga_data: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_amount_reserved: float = 0.0
    compensation_completed: bool = False

class PayTMPaymentSaga:
    """
    PayTM-style payment saga orchestrator
    जैसे Mumbai में train journey का coordination - har station pe specific process
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.active_sagas: Dict[str, SagaExecution] = {}
        self.saga_timeout_seconds = 300  # 5 minutes max for payment saga
        
        # Define payment saga steps - PayTM style flow
        self.payment_saga_steps = [
            SagaStep("validate_user", self.validate_user_step, self.compensate_user_validation),
            SagaStep("check_kyc", self.check_kyc_step, self.compensate_kyc_check),
            SagaStep("validate_merchant", self.validate_merchant_step, self.compensate_merchant_validation),
            SagaStep("check_fraud", self.check_fraud_step, self.compensate_fraud_check),
            SagaStep("reserve_funds", self.reserve_funds_step, self.compensate_fund_reservation),
            SagaStep("process_payment", self.process_payment_step, self.compensate_payment_processing),
            SagaStep("update_wallet", self.update_wallet_step, self.compensate_wallet_update),
            SagaStep("notify_merchant", self.notify_merchant_step, self.compensate_merchant_notification, is_critical=False),
            SagaStep("send_receipt", self.send_receipt_step, self.compensate_receipt_sending, is_critical=False),
            SagaStep("update_analytics", self.update_analytics_step, self.compensate_analytics_update, is_critical=False)
        ]
        
        logger.info("PayTM Payment Saga orchestrator initialized - Ready for Mumbai-scale transactions!")
    
    async def start_payment_saga(self, payment_request: PaymentRequest) -> str:
        """
        Start payment processing saga
        जैसे Mumbai local में journey शुरू करना - सभी preparations के साथ
        """
        saga_id = f"PAYMENT_{payment_request.payment_id}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Starting payment saga {saga_id} for amount ₹{payment_request.amount} via {payment_request.payment_method.value}")
        
        saga = SagaExecution(
            saga_id=saga_id,
            payment_request=payment_request,
            saga_data={
                "original_amount": payment_request.amount,
                "payment_gateway": "paytm",
                "region": "mumbai",
                "attempt_count": 1
            }
        )
        
        self.active_sagas[saga_id] = saga
        
        # Persist saga state in Redis
        if self.redis_client:
            await self._persist_saga_state(saga)
        
        # Start saga execution asynchronously
        asyncio.create_task(self._execute_saga(saga))
        
        return saga_id
    
    async def _execute_saga(self, saga: SagaExecution):
        """
        Execute all saga steps sequentially
        जैसे train journey में har station pe रुकना और process करना
        """
        logger.info(f"Executing payment saga {saga.saga_id} - Starting PayTM payment journey!")
        
        saga.status = SagaStatus.IN_PROGRESS
        
        try:
            # Set overall saga timeout
            saga_task = asyncio.create_task(self._run_saga_steps(saga))
            timeout_task = asyncio.create_task(asyncio.sleep(self.saga_timeout_seconds))
            
            done, pending = await asyncio.wait(
                [saga_task, timeout_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            if timeout_task in done:
                # Saga timed out
                logger.error(f"Saga {saga.saga_id} timed out after {self.saga_timeout_seconds}s")
                saga.status = SagaStatus.TIMEOUT
                await self._compensate_saga(saga)
                return
            
            # Check if saga completed successfully
            if saga.status == SagaStatus.IN_PROGRESS:
                saga.status = SagaStatus.COMPLETED
                saga.end_time = datetime.now()
                logger.info(f"Payment saga {saga.saga_id} completed successfully - Payment processed like efficient Mumbai Dabbawalas!")
            
        except Exception as e:
            logger.error(f"Saga {saga.saga_id} failed with error: {str(e)}")
            saga.status = SagaStatus.FAILED
            await self._compensate_saga(saga)
        
        finally:
            # Update final state
            if self.redis_client:
                await self._persist_saga_state(saga)
    
    async def _run_saga_steps(self, saga: SagaExecution):
        """Run all saga steps in sequence"""
        
        for i, step in enumerate(self.payment_saga_steps):
            saga.current_step = i
            logger.info(f"Executing step {i+1}/{len(self.payment_saga_steps)}: {step.name} for saga {saga.saga_id}")
            
            # Execute step with retry logic
            step_result = await self._execute_step_with_retry(saga, step)
            saga.completed_steps.append(step_result)
            
            if not step_result.success:
                if step.is_critical:
                    logger.error(f"Critical step {step.name} failed in saga {saga.saga_id}: {step_result.error_message}")
                    saga.status = SagaStatus.FAILED
                    await self._compensate_saga(saga)
                    return
                else:
                    logger.warning(f"Non-critical step {step.name} failed in saga {saga.saga_id}, continuing...")
            
            # Update saga state after each step
            if self.redis_client:
                await self._persist_saga_state(saga)
            
            # Small delay between steps for realistic processing
            await asyncio.sleep(0.1)
    
    async def _execute_step_with_retry(self, saga: SagaExecution, step: SagaStep) -> StepResult:
        """Execute step with retry mechanism"""
        
        for attempt in range(step.retry_count):
            try:
                start_time = time.time()
                
                # Execute step with timeout
                result = await asyncio.wait_for(
                    step.action_func(saga),
                    timeout=step.timeout_seconds
                )
                
                execution_time = int((time.time() - start_time) * 1000)
                
                if result:
                    return StepResult(
                        step_name=step.name,
                        success=True,
                        data=result,
                        execution_time_ms=execution_time
                    )
                else:
                    if attempt == step.retry_count - 1:  # Last attempt
                        return StepResult(
                            step_name=step.name,
                            success=False,
                            error_message=f"Step {step.name} returned False after {step.retry_count} attempts",
                            execution_time_ms=execution_time
                        )
                    
                    logger.warning(f"Step {step.name} failed, retrying... ({attempt + 1}/{step.retry_count})")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                
            except asyncio.TimeoutError:
                execution_time = int(step.timeout_seconds * 1000)
                if attempt == step.retry_count - 1:
                    return StepResult(
                        step_name=step.name,
                        success=False,
                        error_message=f"Step {step.name} timed out after {step.timeout_seconds}s",
                        execution_time_ms=execution_time
                    )
                logger.warning(f"Step {step.name} timed out, retrying... ({attempt + 1}/{step.retry_count})")
                
            except Exception as e:
                execution_time = int((time.time() - start_time) * 1000)
                if attempt == step.retry_count - 1:
                    return StepResult(
                        step_name=step.name,
                        success=False,
                        error_message=f"Step {step.name} error: {str(e)}",
                        execution_time_ms=execution_time
                    )
                logger.warning(f"Step {step.name} error: {str(e)}, retrying... ({attempt + 1}/{step.retry_count})")
                await asyncio.sleep(0.5 * (attempt + 1))
        
        # Should never reach here
        return StepResult(step_name=step.name, success=False, error_message="Unknown error")
    
    # Saga step implementations
    
    async def validate_user_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 1: Validate user credentials and status
        जैसे Mumbai local में season pass validate करना
        """
        payment_req = saga.payment_request
        
        # Simulate user validation process
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        # Check user status (simulated)
        if payment_req.user_id.startswith("BLOCKED_"):
            raise Exception(f"User {payment_req.user_id} is blocked")
        
        if payment_req.user_id.startswith("SUSPENDED_"):
            raise Exception(f"User {payment_req.user_id} account suspended")
        
        # Simulate some failures for demo
        if random.random() < 0.05:  # 5% failure rate
            raise Exception("User validation service temporarily unavailable")
        
        user_details = {
            "user_id": payment_req.user_id,
            "user_status": "active",
            "account_type": "premium" if payment_req.amount > 10000 else "regular",
            "risk_score": random.randint(1, 100),
            "last_login": datetime.now().isoformat()
        }
        
        saga.saga_data["user_details"] = user_details
        logger.info(f"User {payment_req.user_id} validated successfully - account type: {user_details['account_type']}")
        
        return user_details
    
    async def check_kyc_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 2: Check KYC compliance
        जैसे Mumbai में बैंक account open करते time KYC verification
        """
        payment_req = saga.payment_request
        user_details = saga.saga_data.get("user_details", {})
        
        await asyncio.sleep(random.uniform(0.3, 1.0))
        
        # KYC requirements based on amount
        if payment_req.amount > 50000:  # High value transaction
            kyc_required = "full_kyc"
            if user_details.get("risk_score", 50) > 70:
                raise Exception("High risk user requires manual KYC verification")
        elif payment_req.amount > 10000:
            kyc_required = "basic_kyc"
        else:
            kyc_required = "minimal_kyc"
        
        # Simulate KYC failures
        if random.random() < 0.03:  # 3% failure rate
            raise Exception("KYC verification service down")
        
        kyc_status = {
            "kyc_level": kyc_required,
            "kyc_status": "verified",
            "kyc_completed_date": datetime.now().isoformat(),
            "documents_verified": ["pan_card", "aadhar_card"] if kyc_required != "minimal_kyc" else ["phone"]
        }
        
        saga.saga_data["kyc_status"] = kyc_status
        logger.info(f"KYC verification completed - level: {kyc_required}")
        
        return kyc_status
    
    async def validate_merchant_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 3: Validate merchant details and status
        जैसे Mumbai में shop का license check करना
        """
        payment_req = saga.payment_request
        
        await asyncio.sleep(random.uniform(0.2, 0.6))
        
        # Simulate merchant validation
        if payment_req.merchant_id.startswith("INVALID_"):
            raise Exception(f"Merchant {payment_req.merchant_id} not found")
        
        if payment_req.merchant_id.startswith("SUSPENDED_"):
            raise Exception(f"Merchant {payment_req.merchant_id} account suspended")
        
        # Random merchant service failures
        if random.random() < 0.02:  # 2% failure rate
            raise Exception("Merchant validation service unavailable")
        
        merchant_details = {
            "merchant_id": payment_req.merchant_id,
            "merchant_name": f"Mumbai Store {payment_req.merchant_id[-3:]}",
            "merchant_category": "retail",
            "status": "active",
            "settlement_account": f"BANK_AC_{payment_req.merchant_id}",
            "transaction_limits": {
                "daily_limit": 1000000,
                "per_transaction_limit": 100000
            }
        }
        
        # Check transaction limits
        if payment_req.amount > merchant_details["transaction_limits"]["per_transaction_limit"]:
            raise Exception(f"Amount exceeds merchant transaction limit of ₹{merchant_details['transaction_limits']['per_transaction_limit']}")
        
        saga.saga_data["merchant_details"] = merchant_details
        logger.info(f"Merchant {payment_req.merchant_id} validated successfully")
        
        return merchant_details
    
    async def check_fraud_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 4: Fraud detection and risk assessment
        जैसे Mumbai police का security check
        """
        payment_req = saga.payment_request
        user_details = saga.saga_data.get("user_details", {})
        
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Fraud check takes time
        
        # Fraud detection logic
        risk_factors = []
        risk_score = user_details.get("risk_score", 50)
        
        # Amount-based risk
        if payment_req.amount > 25000:
            risk_score += 20
            risk_factors.append("high_amount")
        
        # Time-based risk (late night transactions are riskier)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 15
            risk_factors.append("odd_hours")
        
        # Payment method risk
        if payment_req.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.EMI]:
            risk_score += 10
            risk_factors.append("credit_based")
        
        # Simulate fraud detection failures
        if random.random() < 0.01:  # 1% fraud detection service failure
            raise Exception("Fraud detection service temporarily down")
        
        # Block high risk transactions
        if risk_score > 85:
            raise Exception(f"Transaction blocked due to high fraud risk (score: {risk_score})")
        
        fraud_check = {
            "risk_score": min(risk_score, 100),
            "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low",
            "risk_factors": risk_factors,
            "fraud_detected": False,
            "check_timestamp": datetime.now().isoformat()
        }
        
        saga.saga_data["fraud_check"] = fraud_check
        logger.info(f"Fraud check completed - risk level: {fraud_check['risk_level']} (score: {risk_score})")
        
        return fraud_check
    
    async def reserve_funds_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 5: Reserve funds from user account/wallet
        जैसे Mumbai local ticket counter में पैसे hold करना
        """
        payment_req = saga.payment_request
        
        await asyncio.sleep(random.uniform(0.4, 1.2))
        
        # Simulate fund reservation based on payment method
        if payment_req.payment_method == PaymentMethod.WALLET:
            # Check wallet balance (simulated)
            wallet_balance = random.uniform(1000, 100000)
            if wallet_balance < payment_req.amount:
                raise Exception(f"Insufficient wallet balance: ₹{wallet_balance:.2f} available, ₹{payment_req.amount} required")
        
        elif payment_req.payment_method == PaymentMethod.UPI:
            # UPI bank balance check (simulated)
            if random.random() < 0.05:  # 5% insufficient balance
                raise Exception("Insufficient bank account balance for UPI transaction")
        
        # Simulate reservation service failures
        if random.random() < 0.02:  # 2% reservation service failure
            raise Exception("Fund reservation service temporarily unavailable")
        
        reservation_id = f"RES_{payment_req.payment_id}_{uuid.uuid4().hex[:8]}"
        
        fund_reservation = {
            "reservation_id": reservation_id,
            "amount": payment_req.amount,
            "payment_method": payment_req.payment_method.value,
            "reserved_at": datetime.now().isoformat(),
            "expiry_time": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "currency": payment_req.currency
        }
        
        saga.saga_data["fund_reservation"] = fund_reservation
        saga.total_amount_reserved = payment_req.amount
        
        logger.info(f"Funds reserved successfully - ₹{payment_req.amount} via {payment_req.payment_method.value}")
        
        return fund_reservation
    
    async def process_payment_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 6: Process actual payment transaction
        जैसे actual money transfer in Mumbai hawala system
        """
        payment_req = saga.payment_request
        fund_reservation = saga.saga_data.get("fund_reservation", {})
        
        await asyncio.sleep(random.uniform(1.0, 3.0))  # Payment processing takes time
        
        # Simulate payment processing failures
        if random.random() < 0.03:  # 3% payment processing failure
            raise Exception("Payment processing gateway temporarily unavailable")
        
        # Simulate bank/network failures
        if random.random() < 0.02:  # 2% bank connectivity issues
            raise Exception("Bank network connectivity issue - please try again")
        
        transaction_id = f"TXN_{payment_req.payment_id}_{uuid.uuid4().hex[:8]}"
        
        payment_result = {
            "transaction_id": transaction_id,
            "payment_id": payment_req.payment_id,
            "status": "success",
            "amount": payment_req.amount,
            "currency": payment_req.currency,
            "payment_method": payment_req.payment_method.value,
            "processed_at": datetime.now().isoformat(),
            "bank_reference": f"BNK_{random.randint(100000, 999999)}",
            "gateway_response": "Payment processed successfully"
        }
        
        saga.saga_data["payment_result"] = payment_result
        logger.info(f"Payment processed successfully - Transaction ID: {transaction_id}")
        
        return payment_result
    
    async def update_wallet_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 7: Update wallet balances
        जैसे Mumbai local ticket machine में balance update
        """
        payment_req = saga.payment_request
        payment_result = saga.saga_data.get("payment_result", {})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Simulate wallet update failures
        if random.random() < 0.01:  # 1% wallet service failure
            raise Exception("Wallet service temporarily unavailable for balance update")
        
        wallet_update = {
            "user_wallet_debited": payment_req.amount if payment_req.payment_method == PaymentMethod.WALLET else 0,
            "merchant_wallet_credited": payment_req.amount * 0.97,  # After 3% commission
            "paytm_commission": payment_req.amount * 0.03,
            "updated_at": datetime.now().isoformat(),
            "balance_sync_id": f"SYNC_{uuid.uuid4().hex[:8]}"
        }
        
        saga.saga_data["wallet_update"] = wallet_update
        logger.info(f"Wallet balances updated - Commission: ₹{wallet_update['paytm_commission']:.2f}")
        
        return wallet_update
    
    async def notify_merchant_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 8: Notify merchant about payment (non-critical)
        जैसे Mumbai shop को payment notification भेजना
        """
        payment_req = saga.payment_request
        payment_result = saga.saga_data.get("payment_result", {})
        
        await asyncio.sleep(random.uniform(0.2, 0.6))
        
        # Simulate notification failures (non-critical)
        if random.random() < 0.10:  # 10% notification failure - but non-critical
            return False
        
        notification = {
            "merchant_id": payment_req.merchant_id,
            "notification_type": "payment_received",
            "transaction_id": payment_result.get("transaction_id"),
            "amount": payment_req.amount,
            "sent_at": datetime.now().isoformat(),
            "delivery_status": "delivered"
        }
        
        saga.saga_data["merchant_notification"] = notification
        logger.info(f"Merchant notification sent successfully")
        
        return notification
    
    async def send_receipt_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 9: Send payment receipt to user (non-critical)
        जैसे Mumbai shop से bill/receipt मिलना
        """
        payment_req = saga.payment_request
        payment_result = saga.saga_data.get("payment_result", {})
        
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Simulate receipt service failures (non-critical)
        if random.random() < 0.08:  # 8% receipt service failure
            return False
        
        receipt = {
            "receipt_id": f"RCPT_{payment_req.payment_id}",
            "transaction_id": payment_result.get("transaction_id"),
            "user_id": payment_req.user_id,
            "amount": payment_req.amount,
            "payment_method": payment_req.payment_method.value,
            "timestamp": datetime.now().isoformat(),
            "receipt_url": f"https://paytm.com/receipts/{payment_req.payment_id}",
            "sent_via": ["sms", "email", "app_notification"]
        }
        
        saga.saga_data["receipt"] = receipt
        logger.info(f"Payment receipt sent to user")
        
        return receipt
    
    async def update_analytics_step(self, saga: SagaExecution) -> Dict[str, Any]:
        """
        Step 10: Update analytics and reporting (non-critical)
        जैसे Mumbai traffic data collect करना
        """
        payment_req = saga.payment_request
        
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Analytics update rarely fails but non-critical
        if random.random() < 0.02:  # 2% analytics failure
            return False
        
        analytics = {
            "transaction_count": 1,
            "amount": payment_req.amount,
            "payment_method": payment_req.payment_method.value,
            "region": saga.saga_data.get("region", "mumbai"),
            "success_rate": 1.0,
            "updated_at": datetime.now().isoformat()
        }
        
        saga.saga_data["analytics"] = analytics
        logger.info(f"Analytics updated for payment trend analysis")
        
        return analytics
    
    # Compensation functions
    
    async def _compensate_saga(self, saga: SagaExecution):
        """
        Compensate/rollback completed saga steps
        जैसे Mumbai local journey cancel होने पर refund process
        """
        logger.warning(f"Starting compensation for saga {saga.saga_id} - Rolling back like train refund process")
        
        saga.status = SagaStatus.COMPENSATING
        
        # Compensate in reverse order of execution
        completed_steps = [step for step in saga.completed_steps if step.success]
        
        for step_result in reversed(completed_steps):
            try:
                # Find the corresponding step definition
                step_def = None
                for step in self.payment_saga_steps:
                    if step.name == step_result.step_name:
                        step_def = step
                        break
                
                if step_def:
                    logger.info(f"Compensating step: {step_result.step_name}")
                    await step_def.compensation_func(saga, step_result)
                    
            except Exception as e:
                logger.error(f"Compensation failed for step {step_result.step_name}: {str(e)}")
                # Continue with other compensations
        
        saga.compensation_completed = True
        saga.end_time = datetime.now()
        logger.info(f"Saga compensation completed for {saga.saga_id}")
    
    async def compensate_user_validation(self, saga: SagaExecution, step_result: StepResult):
        """Compensate user validation - cleanup any locks or temporary data"""
        # In production, this might release user session locks, etc.
        logger.info(f"Compensated user validation for user {saga.payment_request.user_id}")
    
    async def compensate_kyc_check(self, saga: SagaExecution, step_result: StepResult):
        """Compensate KYC check"""
        logger.info(f"Compensated KYC check - no specific action needed")
    
    async def compensate_merchant_validation(self, saga: SagaExecution, step_result: StepResult):
        """Compensate merchant validation"""
        logger.info(f"Compensated merchant validation for {saga.payment_request.merchant_id}")
    
    async def compensate_fraud_check(self, saga: SagaExecution, step_result: StepResult):
        """Compensate fraud check"""
        logger.info(f"Compensated fraud check - releasing any temporary blocks")
    
    async def compensate_fund_reservation(self, saga: SagaExecution, step_result: StepResult):
        """
        Compensate fund reservation - CRITICAL compensation
        जैसे reserved money को वापस user के account में release करना
        """
        fund_reservation = saga.saga_data.get("fund_reservation", {})
        if fund_reservation:
            reservation_id = fund_reservation.get("reservation_id")
            amount = fund_reservation.get("amount", 0)
            
            # Release the reserved funds
            await asyncio.sleep(random.uniform(0.2, 0.8))  # Simulate release operation
            
            saga.total_amount_reserved = 0
            logger.info(f"CRITICAL: Released reserved funds ₹{amount} - reservation {reservation_id}")
        
    async def compensate_payment_processing(self, saga: SagaExecution, step_result: StepResult):
        """
        Compensate payment processing - CRITICAL compensation
        जैसे successful payment को reverse करना (refund)
        """
        payment_result = saga.saga_data.get("payment_result", {})
        if payment_result:
            transaction_id = payment_result.get("transaction_id")
            amount = payment_result.get("amount", 0)
            
            # Initiate refund
            await asyncio.sleep(random.uniform(1.0, 2.5))  # Refund takes time
            
            refund_id = f"REFUND_{transaction_id}_{uuid.uuid4().hex[:8]}"
            saga.saga_data["refund_initiated"] = {
                "refund_id": refund_id,
                "original_transaction_id": transaction_id,
                "refund_amount": amount,
                "refund_status": "initiated",
                "refund_time": datetime.now().isoformat()
            }
            
            logger.info(f"CRITICAL: Initiated refund ₹{amount} for transaction {transaction_id}")
    
    async def compensate_wallet_update(self, saga: SagaExecution, step_result: StepResult):
        """Compensate wallet update - reverse wallet balance changes"""
        wallet_update = saga.saga_data.get("wallet_update", {})
        if wallet_update:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            logger.info(f"Compensated wallet balance changes - amounts reversed")
    
    async def compensate_merchant_notification(self, saga: SagaExecution, step_result: StepResult):
        """Send merchant cancellation notification"""
        # Send cancellation notification to merchant
        logger.info(f"Sent payment cancellation notification to merchant")
    
    async def compensate_receipt_sending(self, saga: SagaExecution, step_result: StepResult):
        """Send cancellation receipt to user"""
        logger.info(f"Sent payment cancellation receipt to user")
    
    async def compensate_analytics_update(self, saga: SagaExecution, step_result: StepResult):
        """Update analytics with failure data"""
        logger.info(f"Updated analytics with payment failure data")
    
    async def _persist_saga_state(self, saga: SagaExecution):
        """Persist saga state to Redis for recovery"""
        if not self.redis_client:
            return
        
        try:
            saga_data = asdict(saga)
            # Convert datetime objects to strings for JSON serialization
            saga_data['start_time'] = saga.start_time.isoformat()
            if saga.end_time:
                saga_data['end_time'] = saga.end_time.isoformat()
            
            await self.redis_client.setex(
                f"saga:{saga.saga_id}",
                3600,  # 1 hour TTL
                json.dumps(saga_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to persist saga state: {str(e)}")
    
    def get_saga_status(self, saga_id: str) -> Optional[SagaExecution]:
        """Get current saga status"""
        return self.active_sagas.get(saga_id)
    
    def list_active_sagas(self) -> List[str]:
        """List all active saga IDs"""
        return list(self.active_sagas.keys())

async def demo_paytm_payment_saga():
    """
    Demonstrate PayTM payment saga with various scenarios
    Mumbai scale payment processing के साथ realistic failures
    """
    print("\n=== PayTM Payment Saga Orchestrator Demo ===")
    print("Mumbai-style payment processing with rollback protection!")
    
    # Initialize saga orchestrator
    saga_orchestrator = PayTMPaymentSaga()
    
    # Demo scenarios
    demo_payments = [
        PaymentRequest(
            payment_id="PAY_001",
            user_id="user_mumbai_123",
            merchant_id="merchant_dadar_456",
            amount=1500.0,
            payment_method=PaymentMethod.UPI,
            description="Vada Pav order - Mumbai special"
        ),
        PaymentRequest(
            payment_id="PAY_002", 
            user_id="user_bandra_789",
            merchant_id="merchant_andheri_321",
            amount=25000.0,
            payment_method=PaymentMethod.WALLET,
            description="Mobile phone purchase"
        ),
        PaymentRequest(
            payment_id="PAY_003",
            user_id="BLOCKED_user_999",  # This will fail in user validation
            merchant_id="merchant_fort_111",
            amount=5000.0,
            payment_method=PaymentMethod.CREDIT_CARD,
            description="This should fail and rollback"
        )
    ]
    
    # Process payments
    saga_ids = []
    
    print("\n--- Starting Payment Sagas ---")
    for payment in demo_payments:
        saga_id = await saga_orchestrator.start_payment_saga(payment)
        saga_ids.append(saga_id)
        print(f"Started saga {saga_id} for payment ₹{payment.amount} via {payment.payment_method.value}")
    
    # Wait for sagas to complete
    print("\n--- Waiting for saga completion ---")
    await asyncio.sleep(8)  # Give time for sagas to execute
    
    # Check final status
    print("\n--- Final Saga Status ---")
    for saga_id in saga_ids:
        saga = saga_orchestrator.get_saga_status(saga_id)
        if saga:
            print(f"\nSaga {saga_id}:")
            print(f"  Status: {saga.status.value}")
            print(f"  Steps completed: {len(saga.completed_steps)}")
            print(f"  Success rate: {sum(1 for s in saga.completed_steps if s.success)}/{len(saga.completed_steps)}")
            
            if saga.total_amount_reserved > 0:
                print(f"  ⚠️ Amount still reserved: ₹{saga.total_amount_reserved}")
            
            if saga.compensation_completed:
                print(f"  ✅ Compensation completed - All rollbacks successful!")
            
            if saga.status == SagaStatus.COMPLETED:
                payment_result = saga.saga_data.get("payment_result", {})
                if payment_result:
                    print(f"  💰 Payment successful - Transaction ID: {payment_result.get('transaction_id')}")
            
            # Show step-by-step execution
            print(f"  Step execution details:")
            for step in saga.completed_steps:
                status = "✅" if step.success else "❌"
                print(f"    {status} {step.step_name} ({step.execution_time_ms}ms)")
                if not step.success:
                    print(f"      Error: {step.error_message}")
    
    print(f"\n--- Demo Summary ---")
    completed = len([s for s in saga_orchestrator.active_sagas.values() if s.status == SagaStatus.COMPLETED])
    failed = len([s for s in saga_orchestrator.active_sagas.values() if s.status in [SagaStatus.FAILED, SagaStatus.TIMEOUT]])
    
    print(f"Total sagas: {len(saga_ids)}")
    print(f"Completed successfully: {completed}")
    print(f"Failed with rollback: {failed}")
    print(f"\nPayTM-style saga orchestration completed!")
    print(f"जैसे Mumbai local train system में safety के साथ efficiency!")

if __name__ == "__main__":
    print("Starting PayTM Payment Saga Demo...")
    asyncio.run(demo_paytm_payment_saga())