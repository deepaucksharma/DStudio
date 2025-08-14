#!/usr/bin/env python3
"""
Domain-Driven Design: Saga Pattern - PhonePe Transaction Processing
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Saga pattern का इस्तेमाल करके
PhonePe के long-running transactions को handle करते हैं। 
Multiple services में distributed transactions manage करना।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import json
import asyncio

# ====================================================================
# SAGA FRAMEWORK - Generic Saga Implementation
# ====================================================================

class SagaStepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

class SagaStatus(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    """Individual step in saga"""
    step_id: str
    name: str
    action: Callable[..., Dict[str, Any]]  # Forward action
    compensation: Callable[..., Dict[str, Any]]  # Rollback action
    timeout_seconds: int = 30
    retry_count: int = 3
    status: SagaStepStatus = SagaStepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SagaOrchestrator:
    """
    Saga Orchestrator - Manages distributed transactions
    Saga orchestrator - distributed transactions को manage करता है
    """
    
    def __init__(self, saga_id: str, saga_name: str):
        self._saga_id = saga_id
        self._saga_name = saga_name
        self._steps: List[SagaStep] = []
        self._status = SagaStatus.STARTED
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._context: Dict[str, Any] = {}
        self._compensation_order: List[SagaStep] = []
        
        print(f"🎭 Saga started: {saga_name} ({saga_id})")
    
    @property
    def saga_id(self) -> str:
        return self._saga_id
    
    @property
    def status(self) -> SagaStatus:
        return self._status
    
    @property
    def context(self) -> Dict[str, Any]:
        return self._context.copy()
    
    def add_step(self, step: SagaStep) -> 'SagaOrchestrator':
        """Add step to saga"""
        self._steps.append(step)
        print(f"➕ Added step: {step.name}")
        return self
    
    def set_context(self, key: str, value: Any) -> None:
        """Set context data"""
        self._context[key] = value
        self._updated_at = datetime.now()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self._context.get(key, default)
    
    async def execute(self) -> bool:
        """
        Execute saga steps in order
        Saga steps को order में execute करना
        """
        print(f"\n🏃 Executing saga: {self._saga_name}")
        print(f"   Steps: {len(self._steps)}")
        
        self._status = SagaStatus.IN_PROGRESS
        self._updated_at = datetime.now()
        
        try:
            # Execute steps in forward order
            for i, step in enumerate(self._steps):
                print(f"\n🔄 Step {i+1}/{len(self._steps)}: {step.name}")
                
                success = await self._execute_step(step)
                if success:
                    self._compensation_order.insert(0, step)  # LIFO for compensation
                else:
                    # Step failed, start compensation
                    print(f"❌ Step failed: {step.name}")
                    await self._compensate()
                    return False
            
            # All steps completed successfully
            self._status = SagaStatus.COMPLETED
            self._updated_at = datetime.now()
            
            print(f"\n✅ Saga completed successfully: {self._saga_name}")
            return True
            
        except Exception as e:
            print(f"❌ Saga execution error: {e}")
            self._status = SagaStatus.FAILED
            await self._compensate()
            return False
    
    async def _execute_step(self, step: SagaStep) -> bool:
        """Execute individual saga step with retry logic"""
        step.started_at = datetime.now()
        
        for attempt in range(step.retry_count):
            try:
                if attempt > 0:
                    print(f"   🔄 Retry {attempt + 1}/{step.retry_count}")
                
                # Execute step action
                result = await asyncio.wait_for(
                    asyncio.to_thread(step.action, self._context),
                    timeout=step.timeout_seconds
                )
                
                # Step succeeded
                step.status = SagaStepStatus.COMPLETED
                step.completed_at = datetime.now()
                step.result = result
                
                # Update context with step result
                if result and isinstance(result, dict):
                    self._context.update(result)
                
                duration = (step.completed_at - step.started_at).total_seconds()
                print(f"   ✅ Completed in {duration:.2f}s")
                
                return True
                
            except asyncio.TimeoutError:
                print(f"   ⏰ Step timeout (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    step.status = SagaStepStatus.FAILED
                    step.error = "Timeout"
                    return False
                    
            except Exception as e:
                print(f"   ❌ Step error: {e} (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    step.status = SagaStepStatus.FAILED
                    step.error = str(e)
                    return False
                
                # Wait before retry
                await asyncio.sleep(1)
        
        return False
    
    async def _compensate(self) -> None:
        """
        Compensate completed steps in reverse order
        Completed steps को reverse order में compensate करना
        """
        print(f"\n🔙 Starting compensation for saga: {self._saga_name}")
        
        self._status = SagaStatus.COMPENSATING
        self._updated_at = datetime.now()
        
        # Compensate in reverse order (LIFO)
        for step in self._compensation_order:
            if step.status == SagaStepStatus.COMPLETED:
                print(f"🔄 Compensating: {step.name}")
                
                try:
                    compensation_result = await asyncio.wait_for(
                        asyncio.to_thread(step.compensation, self._context),
                        timeout=step.timeout_seconds
                    )
                    
                    step.status = SagaStepStatus.COMPENSATED
                    print(f"   ✅ Compensated successfully")
                    
                except Exception as e:
                    print(f"   ❌ Compensation failed: {e}")
                    # Log compensation failure but continue
        
        self._status = SagaStatus.COMPENSATED
        self._updated_at = datetime.now()
        
        print(f"🔙 Compensation completed for saga: {self._saga_name}")
    
    def get_saga_summary(self) -> Dict[str, Any]:
        """Get comprehensive saga summary"""
        return {
            "saga_id": self._saga_id,
            "saga_name": self._saga_name,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error": step.error
                }
                for step in self._steps
            ],
            "context": self._context
        }

# ====================================================================
# PHONEPE BUSINESS DOMAIN
# ====================================================================

# Domain Events and Exceptions
class PhonePeException(Exception):
    pass

class InsufficientBalanceException(PhonePeException):
    pass

class InvalidBeneficiaryException(PhonePeException):
    pass

class BankServiceException(PhonePeException):
    pass

class NotificationException(PhonePeException):
    pass

# Value Objects
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

@dataclass(frozen=True)
class BankAccount:
    account_number: str
    ifsc_code: str
    bank_name: str
    account_holder_name: str
    
    def __post_init__(self):
        if len(self.account_number) < 9 or len(self.account_number) > 18:
            raise ValueError("Invalid account number")
        if len(self.ifsc_code) != 11:
            raise ValueError("Invalid IFSC code")

@dataclass(frozen=True)
class UPIId:
    value: str
    
    def __post_init__(self):
        if "@" not in self.value or len(self.value) < 5:
            raise ValueError("Invalid UPI ID")

# Mock External Services
class WalletService:
    """PhonePe Wallet Service"""
    
    @staticmethod
    def check_balance(user_id: str) -> Dict[str, Any]:
        """Check wallet balance"""
        print(f"💰 Checking wallet balance for user: {user_id}")
        
        # Simulate balance check
        import random
        balance = Decimal(str(random.randint(100, 5000)))
        
        return {
            "user_id": user_id,
            "balance": balance,
            "currency": "INR",
            "status": "success"
        }
    
    @staticmethod
    def debit_wallet(user_id: str, amount: Decimal, transaction_id: str) -> Dict[str, Any]:
        """Debit amount from wallet"""
        print(f"💸 Debiting ₹{amount} from wallet: {user_id}")
        
        # Simulate wallet debit
        balance_info = WalletService.check_balance(user_id)
        if balance_info["balance"] < amount:
            raise InsufficientBalanceException(f"Insufficient balance. Available: ₹{balance_info['balance']}")
        
        new_balance = balance_info["balance"] - amount
        
        return {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "debited_amount": amount,
            "remaining_balance": new_balance,
            "status": "success"
        }
    
    @staticmethod
    def credit_wallet(user_id: str, amount: Decimal, transaction_id: str) -> Dict[str, Any]:
        """Credit amount to wallet (compensation)"""
        print(f"💰 Crediting ₹{amount} back to wallet: {user_id}")
        
        return {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "credited_amount": amount,
            "status": "success"
        }

class BankingService:
    """External Banking Service Integration"""
    
    @staticmethod
    def validate_beneficiary(account: BankAccount) -> Dict[str, Any]:
        """Validate beneficiary account details"""
        print(f"🏦 Validating beneficiary: {account.account_number}")
        
        # Simulate beneficiary validation
        import random
        if random.random() > 0.05:  # 95% success rate
            return {
                "account_number": account.account_number,
                "account_holder_name": account.account_holder_name,
                "bank_name": account.bank_name,
                "is_valid": True,
                "status": "verified"
            }
        else:
            raise InvalidBeneficiaryException("Invalid beneficiary account")
    
    @staticmethod
    def transfer_funds(
        from_account: str,
        to_account: BankAccount,
        amount: Decimal,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Transfer funds to beneficiary account"""
        print(f"🏧 Transferring ₹{amount} to {to_account.account_number}")
        
        # Simulate fund transfer
        import random
        if random.random() > 0.1:  # 90% success rate
            return {
                "transaction_id": transaction_id,
                "from_account": from_account,
                "to_account": to_account.account_number,
                "amount": amount,
                "bank_reference": f"BNK_{int(datetime.now().timestamp())}",
                "status": "success"
            }
        else:
            raise BankServiceException("Bank transfer failed")
    
    @staticmethod
    def reverse_transfer(
        transaction_id: str,
        bank_reference: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Reverse fund transfer (compensation)"""
        print(f"🔙 Reversing bank transfer: {bank_reference}")
        
        return {
            "original_transaction_id": transaction_id,
            "bank_reference": bank_reference,
            "reversed_amount": amount,
            "status": "reversed"
        }

class NotificationService:
    """Notification Service for SMS/Push"""
    
    @staticmethod
    def send_transaction_sms(
        phone_number: str,
        transaction_id: str,
        amount: Decimal,
        beneficiary_name: str
    ) -> Dict[str, Any]:
        """Send transaction confirmation SMS"""
        print(f"📱 Sending SMS to {phone_number}")
        
        # Simulate SMS sending
        import random
        if random.random() > 0.02:  # 98% success rate
            return {
                "phone_number": phone_number,
                "message_id": f"SMS_{uuid4()}",
                "status": "sent"
            }
        else:
            raise NotificationException("SMS sending failed")
    
    @staticmethod
    def send_failure_notification(
        phone_number: str,
        transaction_id: str,
        failure_reason: str
    ) -> Dict[str, Any]:
        """Send failure notification"""
        print(f"📱 Sending failure notification to {phone_number}")
        
        return {
            "phone_number": phone_number,
            "message_id": f"SMS_{uuid4()}",
            "status": "sent",
            "message_type": "failure"
        }

class TransactionRecordService:
    """Transaction Record Management"""
    
    @staticmethod
    def create_transaction_record(
        transaction_id: str,
        user_id: str,
        amount: Decimal,
        beneficiary_account: BankAccount,
        transaction_type: str
    ) -> Dict[str, Any]:
        """Create transaction record"""
        print(f"📝 Creating transaction record: {transaction_id}")
        
        return {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "beneficiary": beneficiary_account.account_number,
            "type": transaction_type,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
    
    @staticmethod
    def update_transaction_status(
        transaction_id: str,
        status: str,
        bank_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update transaction status"""
        print(f"📝 Updating transaction status: {transaction_id} -> {status}")
        
        return {
            "transaction_id": transaction_id,
            "status": status,
            "bank_reference": bank_reference,
            "updated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def mark_transaction_failed(
        transaction_id: str,
        failure_reason: str
    ) -> Dict[str, Any]:
        """Mark transaction as failed (compensation)"""
        print(f"📝 Marking transaction failed: {transaction_id}")
        
        return {
            "transaction_id": transaction_id,
            "status": "failed",
            "failure_reason": failure_reason,
            "updated_at": datetime.now().isoformat()
        }

# ====================================================================
# PHONEPE MONEY TRANSFER SAGA
# ====================================================================

class PhonePeMoneyTransferSaga:
    """
    PhonePe Money Transfer Saga
    PhonePe money transfer के लिए complete saga implementation
    """
    
    def __init__(
        self,
        user_id: str,
        beneficiary_account: BankAccount,
        amount: Money,
        phone_number: str,
        transaction_id: Optional[str] = None
    ):
        self._user_id = user_id
        self._beneficiary_account = beneficiary_account
        self._amount = amount
        self._phone_number = phone_number
        self._transaction_id = transaction_id or f"TXN_{uuid4()}"
        
        # Initialize saga orchestrator
        self._saga = SagaOrchestrator(
            saga_id=f"SAGA_{self._transaction_id}",
            saga_name="PhonePe Money Transfer"
        )
        
        # Set context
        self._saga.set_context("user_id", self._user_id)
        self._saga.set_context("transaction_id", self._transaction_id)
        self._saga.set_context("amount", self._amount.amount)
        self._saga.set_context("beneficiary_account", asdict(self._beneficiary_account))
        self._saga.set_context("phone_number", self._phone_number)
        
        # Add saga steps
        self._setup_saga_steps()
    
    def _setup_saga_steps(self) -> None:
        """Setup all saga steps"""
        
        # Step 1: Create Transaction Record
        self._saga.add_step(SagaStep(
            step_id="create_transaction",
            name="Create Transaction Record",
            action=self._create_transaction_record,
            compensation=self._mark_transaction_failed,
            timeout_seconds=10
        ))
        
        # Step 2: Validate Beneficiary
        self._saga.add_step(SagaStep(
            step_id="validate_beneficiary",
            name="Validate Beneficiary",
            action=self._validate_beneficiary,
            compensation=self._no_compensation,  # No compensation needed
            timeout_seconds=15
        ))
        
        # Step 3: Check and Debit Wallet
        self._saga.add_step(SagaStep(
            step_id="debit_wallet",
            name="Debit User Wallet",
            action=self._debit_wallet,
            compensation=self._credit_wallet_back,
            timeout_seconds=20
        ))
        
        # Step 4: Transfer to Bank
        self._saga.add_step(SagaStep(
            step_id="bank_transfer",
            name="Transfer to Bank Account",
            action=self._transfer_to_bank,
            compensation=self._reverse_bank_transfer,
            timeout_seconds=60
        ))
        
        # Step 5: Update Transaction Status
        self._saga.add_step(SagaStep(
            step_id="update_transaction",
            name="Update Transaction Status",
            action=self._update_transaction_success,
            compensation=self._update_transaction_failure,
            timeout_seconds=10
        ))
        
        # Step 6: Send Confirmation SMS
        self._saga.add_step(SagaStep(
            step_id="send_sms",
            name="Send Confirmation SMS",
            action=self._send_confirmation_sms,
            compensation=self._send_failure_notification,
            timeout_seconds=30
        ))
    
    # Saga Step Actions
    
    def _create_transaction_record(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Create transaction record"""
        return TransactionRecordService.create_transaction_record(
            transaction_id=context["transaction_id"],
            user_id=context["user_id"],
            amount=context["amount"],
            beneficiary_account=BankAccount(**context["beneficiary_account"]),
            transaction_type="money_transfer"
        )
    
    def _validate_beneficiary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Validate beneficiary account"""
        beneficiary = BankAccount(**context["beneficiary_account"])
        validation_result = BankingService.validate_beneficiary(beneficiary)
        
        # Update context with validation details
        return {
            "beneficiary_validated": True,
            "validated_name": validation_result["account_holder_name"]
        }
    
    def _debit_wallet(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Debit user wallet"""
        return WalletService.debit_wallet(
            user_id=context["user_id"],
            amount=context["amount"],
            transaction_id=context["transaction_id"]
        )
    
    def _transfer_to_bank(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Transfer funds to bank"""
        beneficiary = BankAccount(**context["beneficiary_account"])
        
        return BankingService.transfer_funds(
            from_account="PHONEPE_POOLED_ACCOUNT",
            to_account=beneficiary,
            amount=context["amount"],
            transaction_id=context["transaction_id"]
        )
    
    def _update_transaction_success(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Update transaction as successful"""
        bank_reference = context.get("bank_reference")
        
        return TransactionRecordService.update_transaction_status(
            transaction_id=context["transaction_id"],
            status="completed",
            bank_reference=bank_reference
        )
    
    def _send_confirmation_sms(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Send confirmation SMS"""
        return NotificationService.send_transaction_sms(
            phone_number=context["phone_number"],
            transaction_id=context["transaction_id"],
            amount=context["amount"],
            beneficiary_name=context.get("validated_name", "Beneficiary")
        )
    
    # Compensation Actions
    
    def _mark_transaction_failed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensation: Mark transaction as failed"""
        return TransactionRecordService.mark_transaction_failed(
            transaction_id=context["transaction_id"],
            failure_reason="Transaction creation failed"
        )
    
    def _credit_wallet_back(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensation: Credit wallet back"""
        return WalletService.credit_wallet(
            user_id=context["user_id"],
            amount=context["amount"],
            transaction_id=context["transaction_id"]
        )
    
    def _reverse_bank_transfer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensation: Reverse bank transfer"""
        bank_reference = context.get("bank_reference")
        
        if bank_reference:
            return BankingService.reverse_transfer(
                transaction_id=context["transaction_id"],
                bank_reference=bank_reference,
                amount=context["amount"]
            )
        
        return {"status": "no_reversal_needed"}
    
    def _update_transaction_failure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensation: Update transaction as failed"""
        return TransactionRecordService.update_transaction_status(
            transaction_id=context["transaction_id"],
            status="failed"
        )
    
    def _send_failure_notification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensation: Send failure notification"""
        return NotificationService.send_failure_notification(
            phone_number=context["phone_number"],
            transaction_id=context["transaction_id"],
            failure_reason="Transaction failed"
        )
    
    def _no_compensation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """No compensation needed"""
        return {"status": "no_compensation_needed"}
    
    async def execute(self) -> bool:
        """Execute the money transfer saga"""
        return await self._saga.execute()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get saga execution summary"""
        return self._saga.get_saga_summary()

# ====================================================================
# USAGE EXAMPLES AND TESTING
# ====================================================================

async def simulate_successful_transfer():
    """Simulate successful money transfer"""
    
    print("💰 Simulating Successful PhonePe Transfer")
    print("=" * 45)
    
    # Create beneficiary account
    beneficiary = BankAccount(
        account_number="1234567890",
        ifsc_code="SBIN0001234",
        bank_name="State Bank of India",
        account_holder_name="Priya Sharma"
    )
    
    # Create saga
    saga = PhonePeMoneyTransferSaga(
        user_id="USER_12345",
        beneficiary_account=beneficiary,
        amount=Money(Decimal("500.00")),
        phone_number="9876543210"
    )
    
    # Execute saga
    success = await saga.execute()
    
    print(f"\n📊 Saga Result: {'SUCCESS' if success else 'FAILED'}")
    
    # Get summary
    summary = saga.get_summary()
    print(f"\n📋 Saga Summary:")
    print(f"   Status: {summary['status']}")
    print(f"   Steps completed: {sum(1 for step in summary['steps'] if step['status'] == 'completed')}/{len(summary['steps'])}")
    
    return success, summary

async def simulate_failed_transfer():
    """Simulate failed money transfer with compensation"""
    
    print("\n💸 Simulating Failed PhonePe Transfer")
    print("=" * 42)
    
    # Create beneficiary account
    beneficiary = BankAccount(
        account_number="9999999999",  # This might cause validation failure
        ifsc_code="SBIN0009999",
        bank_name="State Bank of India", 
        account_holder_name="Invalid Account"
    )
    
    # Create saga
    saga = PhonePeMoneyTransferSaga(
        user_id="USER_67890",
        beneficiary_account=beneficiary,
        amount=Money(Decimal("1000.00")),
        phone_number="9876543211"
    )
    
    # Execute saga
    success = await saga.execute()
    
    print(f"\n📊 Saga Result: {'SUCCESS' if success else 'FAILED'}")
    
    # Get summary
    summary = saga.get_summary()
    print(f"\n📋 Saga Summary:")
    print(f"   Status: {summary['status']}")
    print(f"   Steps completed: {sum(1 for step in summary['steps'] if step['status'] == 'completed')}/{len(summary['steps'])}")
    print(f"   Steps compensated: {sum(1 for step in summary['steps'] if step['status'] == 'compensated')}")
    
    return success, summary

async def simulate_multiple_transfers():
    """Simulate multiple concurrent transfers"""
    
    print("\n🔄 Simulating Multiple Concurrent Transfers")
    print("=" * 48)
    
    # Create multiple transfer sagas
    sagas = []
    
    for i in range(3):
        beneficiary = BankAccount(
            account_number=f"123456789{i}",
            ifsc_code="HDFC0001234",
            bank_name="HDFC Bank",
            account_holder_name=f"Beneficiary {i+1}"
        )
        
        saga = PhonePeMoneyTransferSaga(
            user_id=f"USER_{12345 + i}",
            beneficiary_account=beneficiary,
            amount=Money(Decimal(f"{200 + i*100}.00")),
            phone_number=f"987654321{i}"
        )
        
        sagas.append(saga)
    
    # Execute all sagas concurrently
    print(f"🚀 Starting {len(sagas)} concurrent transfers...")
    
    results = await asyncio.gather(*[saga.execute() for saga in sagas])
    
    # Analyze results
    successful = sum(results)
    failed = len(results) - successful
    
    print(f"\n📊 Concurrent Transfer Results:")
    print(f"   Successful: {successful}/{len(sagas)}")
    print(f"   Failed: {failed}/{len(sagas)}")
    
    # Show individual summaries
    for i, saga in enumerate(sagas):
        summary = saga.get_summary()
        print(f"\n   Transfer {i+1}: {summary['status']}")
        print(f"     Transaction ID: {summary['context']['transaction_id']}")

async def main():
    """Main function to demonstrate PhonePe Saga pattern"""
    
    print("🏛️ PhonePe Saga Pattern - DDD Example")
    print("=" * 45)
    
    # Test scenarios
    await simulate_successful_transfer()
    await simulate_failed_transfer()
    await simulate_multiple_transfers()
    
    print(f"\n✨ Saga Pattern Benefits Demonstrated:")
    print(f"   ✅ Long-running transactions managed")
    print(f"   ✅ Automatic compensation on failures")
    print(f"   ✅ Distributed transaction coordination")
    print(f"   ✅ Fault tolerance with retries")
    print(f"   ✅ Complete audit trail maintained")
    
    print(f"\n✨ Ready for production PhonePe-scale system!")
    print(f"✨ Handles complex distributed transactions reliably!")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())