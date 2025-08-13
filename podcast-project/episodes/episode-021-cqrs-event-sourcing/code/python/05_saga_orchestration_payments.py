#!/usr/bin/env python3
"""
Episode 21: CQRS/Event Sourcing - Saga Orchestration for Paytm Payment Processing
Author: Code Developer Agent
Description: Production-ready Saga pattern for distributed payment transactions

Saga Pattern manages distributed transactions across multiple services
Paytm payments में multiple steps होते हैं - wallet debit, merchant credit, commission, etc.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Transaction Status
class TransactionStatus(Enum):
    STARTED = "started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

class PaymentMethod(Enum):
    WALLET = "wallet"
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"

class SagaStepStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

# Domain Models
@dataclass
class PaymentRequest:
    """Paytm payment request"""
    payment_id: str
    user_id: str
    merchant_id: str
    amount: float
    payment_method: PaymentMethod
    merchant_category: str
    order_id: str
    description: str
    metadata: Dict[str, Any]

@dataclass
class SagaStep:
    """Individual step in payment saga"""
    step_id: str
    step_name: str
    step_type: str  # action, compensation
    service_name: str
    status: SagaStepStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    timeout_seconds: int

@dataclass
class PaymentSaga:
    """Payment processing saga"""
    saga_id: str
    payment_id: str
    user_id: str
    merchant_id: str
    amount: float
    status: TransactionStatus
    steps: List[SagaStep]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

# Domain Events
@dataclass
class SagaStartedEvent:
    saga_id: str
    payment_id: str
    user_id: str
    merchant_id: str
    amount: float
    payment_method: str
    timestamp: datetime

@dataclass
class SagaStepCompletedEvent:
    saga_id: str
    step_id: str
    step_name: str
    output_data: Dict[str, Any]
    timestamp: datetime

@dataclass
class SagaStepFailedEvent:
    saga_id: str
    step_id: str
    step_name: str
    error_message: str
    retry_count: int
    timestamp: datetime

@dataclass
class SagaCompletedEvent:
    saga_id: str
    payment_id: str
    final_status: TransactionStatus
    timestamp: datetime

# Service Interfaces
class PaymentService:
    """Mock payment service"""
    
    async def validate_payment(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Validate payment request"""
        await asyncio.sleep(0.1)  # Simulate service call
        
        # Mock validation logic
        if payment_request.amount <= 0:
            raise ValueError("Amount must be positive")
        
        if payment_request.amount > 100000:
            raise ValueError("Amount exceeds daily limit")
        
        return {
            "validation_id": str(uuid.uuid4()),
            "status": "validated",
            "risk_score": 0.1,
            "validation_time": datetime.now().isoformat()
        }
    
    async def reserve_funds(self, user_id: str, amount: float, payment_method: PaymentMethod) -> Dict[str, Any]:
        """Reserve funds in user's wallet/account"""
        await asyncio.sleep(0.2)
        
        # Mock fund reservation
        if payment_method == PaymentMethod.WALLET:
            # Check wallet balance (simplified)
            wallet_balance = 50000.0  # Mock balance
            if amount > wallet_balance:
                raise ValueError("Insufficient wallet balance")
        
        reservation_id = f"RSV_{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "reservation_id": reservation_id,
            "amount": amount,
            "payment_method": payment_method.value,
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    
    async def release_funds(self, reservation_id: str) -> Dict[str, Any]:
        """Release reserved funds (compensation)"""
        await asyncio.sleep(0.1)
        
        return {
            "reservation_id": reservation_id,
            "status": "released",
            "released_at": datetime.now().isoformat()
        }

class MerchantService:
    """Mock merchant service"""
    
    async def validate_merchant(self, merchant_id: str, amount: float) -> Dict[str, Any]:
        """Validate merchant can receive payment"""
        await asyncio.sleep(0.1)
        
        # Mock merchant validation
        active_merchants = ["MERCHANT001", "MERCHANT002", "MERCHANT003"]
        
        if merchant_id not in active_merchants:
            raise ValueError("Merchant not active")
        
        return {
            "merchant_id": merchant_id,
            "status": "active",
            "settlement_account": f"ACC_{merchant_id}",
            "commission_rate": 0.02  # 2% commission
        }
    
    async def credit_merchant(self, merchant_id: str, amount: float, transaction_id: str) -> Dict[str, Any]:
        """Credit amount to merchant account"""
        await asyncio.sleep(0.3)
        
        return {
            "merchant_id": merchant_id,
            "credited_amount": amount,
            "transaction_id": transaction_id,
            "settlement_id": f"SETTLE_{uuid.uuid4().hex[:8].upper()}",
            "credited_at": datetime.now().isoformat()
        }
    
    async def debit_merchant(self, settlement_id: str, amount: float) -> Dict[str, Any]:
        """Debit from merchant account (compensation)"""
        await asyncio.sleep(0.2)
        
        return {
            "settlement_id": settlement_id,
            "debited_amount": amount,
            "status": "debited",
            "debited_at": datetime.now().isoformat()
        }

class CommissionService:
    """Mock commission service"""
    
    async def calculate_commission(self, merchant_id: str, amount: float) -> Dict[str, Any]:
        """Calculate Paytm commission"""
        await asyncio.sleep(0.1)
        
        # Different commission rates for different merchant categories
        commission_rates = {
            "grocery": 0.015,  # 1.5%
            "food": 0.02,      # 2%
            "transport": 0.01, # 1%
            "ecommerce": 0.025 # 2.5%
        }
        
        commission_rate = commission_rates.get("ecommerce", 0.02)  # Default 2%
        commission_amount = amount * commission_rate
        
        return {
            "commission_id": f"COMM_{uuid.uuid4().hex[:8].upper()}",
            "commission_amount": commission_amount,
            "commission_rate": commission_rate,
            "calculated_at": datetime.now().isoformat()
        }
    
    async def collect_commission(self, commission_id: str, amount: float) -> Dict[str, Any]:
        """Collect commission"""
        await asyncio.sleep(0.1)
        
        return {
            "commission_id": commission_id,
            "collected_amount": amount,
            "status": "collected",
            "collected_at": datetime.now().isoformat()
        }
    
    async def refund_commission(self, commission_id: str) -> Dict[str, Any]:
        """Refund commission (compensation)"""
        await asyncio.sleep(0.1)
        
        return {
            "commission_id": commission_id,
            "status": "refunded",
            "refunded_at": datetime.now().isoformat()
        }

class NotificationService:
    """Mock notification service"""
    
    async def send_payment_notification(self, user_id: str, merchant_id: str, 
                                      amount: float, status: str) -> Dict[str, Any]:
        """Send payment notification"""
        await asyncio.sleep(0.05)
        
        return {
            "notification_id": f"NOTIF_{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "merchant_id": merchant_id,
            "amount": amount,
            "status": status,
            "sent_at": datetime.now().isoformat()
        }

# Saga Orchestrator
class PaymentSagaOrchestrator:
    """Orchestrates payment saga steps"""
    
    def __init__(self):
        self.payment_service = PaymentService()
        self.merchant_service = MerchantService()
        self.commission_service = CommissionService()
        self.notification_service = NotificationService()
        self.sagas: Dict[str, PaymentSaga] = {}
        self.event_handlers: List[Callable] = []
    
    def add_event_handler(self, handler: Callable):
        """Add event handler for saga events"""
        self.event_handlers.append(handler)
    
    async def _publish_event(self, event: Any):
        """Publish domain event"""
        for handler in self.event_handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"⚠️ Event handler error: {e}")
    
    async def start_payment_saga(self, payment_request: PaymentRequest) -> str:
        """Start payment processing saga"""
        saga_id = str(uuid.uuid4())
        
        # Create saga with all steps
        saga = PaymentSaga(
            saga_id=saga_id,
            payment_id=payment_request.payment_id,
            user_id=payment_request.user_id,
            merchant_id=payment_request.merchant_id,
            amount=payment_request.amount,
            status=TransactionStatus.STARTED,
            steps=self._create_saga_steps(saga_id, payment_request),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=None,
            error_message=None
        )
        
        self.sagas[saga_id] = saga
        
        # Publish saga started event
        await self._publish_event(SagaStartedEvent(
            saga_id=saga_id,
            payment_id=payment_request.payment_id,
            user_id=payment_request.user_id,
            merchant_id=payment_request.merchant_id,
            amount=payment_request.amount,
            payment_method=payment_request.payment_method.value,
            timestamp=datetime.now()
        ))
        
        # Start processing
        asyncio.create_task(self._process_saga(saga_id))
        
        print(f"🚀 Started payment saga {saga_id} for payment {payment_request.payment_id}")
        return saga_id
    
    def _create_saga_steps(self, saga_id: str, payment_request: PaymentRequest) -> List[SagaStep]:
        """Create all saga steps"""
        steps = []
        
        # Step 1: Validate Payment
        steps.append(SagaStep(
            step_id=f"{saga_id}_VALIDATE",
            step_name="validate_payment",
            step_type="action",
            service_name="payment_service",
            status=SagaStepStatus.PENDING,
            input_data=asdict(payment_request),
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 2: Validate Merchant
        steps.append(SagaStep(
            step_id=f"{saga_id}_VALIDATE_MERCHANT",
            step_name="validate_merchant",
            step_type="action",
            service_name="merchant_service",
            status=SagaStepStatus.PENDING,
            input_data={"merchant_id": payment_request.merchant_id, "amount": payment_request.amount},
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 3: Reserve Funds
        steps.append(SagaStep(
            step_id=f"{saga_id}_RESERVE_FUNDS",
            step_name="reserve_funds",
            step_type="action",
            service_name="payment_service",
            status=SagaStepStatus.PENDING,
            input_data={
                "user_id": payment_request.user_id,
                "amount": payment_request.amount,
                "payment_method": payment_request.payment_method.value
            },
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 4: Calculate Commission
        steps.append(SagaStep(
            step_id=f"{saga_id}_CALCULATE_COMMISSION",
            step_name="calculate_commission",
            step_type="action",
            service_name="commission_service",
            status=SagaStepStatus.PENDING,
            input_data={"merchant_id": payment_request.merchant_id, "amount": payment_request.amount},
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 5: Credit Merchant
        steps.append(SagaStep(
            step_id=f"{saga_id}_CREDIT_MERCHANT",
            step_name="credit_merchant",
            step_type="action",
            service_name="merchant_service",
            status=SagaStepStatus.PENDING,
            input_data={
                "merchant_id": payment_request.merchant_id,
                "amount": payment_request.amount,
                "transaction_id": payment_request.payment_id
            },
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 6: Collect Commission
        steps.append(SagaStep(
            step_id=f"{saga_id}_COLLECT_COMMISSION",
            step_name="collect_commission",
            step_type="action",
            service_name="commission_service",
            status=SagaStepStatus.PENDING,
            input_data={},  # Will be populated from previous step
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        # Step 7: Send Notification
        steps.append(SagaStep(
            step_id=f"{saga_id}_NOTIFY",
            step_name="send_notification",
            step_type="action",
            service_name="notification_service",
            status=SagaStepStatus.PENDING,
            input_data={
                "user_id": payment_request.user_id,
                "merchant_id": payment_request.merchant_id,
                "amount": payment_request.amount,
                "status": "completed"
            },
            output_data=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            timeout_seconds=30
        ))
        
        return steps
    
    async def _process_saga(self, saga_id: str):
        """Process saga steps sequentially"""
        saga = self.sagas[saga_id]
        saga.status = TransactionStatus.PROCESSING
        
        try:
            for step in saga.steps:
                if step.step_type == "action":
                    success = await self._execute_step(saga, step)
                    if not success:
                        # Step failed, start compensation
                        await self._compensate_saga(saga)
                        return
            
            # All steps completed successfully
            saga.status = TransactionStatus.COMPLETED
            saga.completed_at = datetime.now()
            
            await self._publish_event(SagaCompletedEvent(
                saga_id=saga_id,
                payment_id=saga.payment_id,
                final_status=TransactionStatus.COMPLETED,
                timestamp=datetime.now()
            ))
            
            print(f"✅ Saga {saga_id} completed successfully")
            
        except Exception as e:
            saga.status = TransactionStatus.FAILED
            saga.error_message = str(e)
            print(f"❌ Saga {saga_id} failed: {e}")
            
            await self._compensate_saga(saga)
    
    async def _execute_step(self, saga: PaymentSaga, step: SagaStep) -> bool:
        """Execute individual saga step"""
        step.status = SagaStepStatus.EXECUTING
        
        try:
            # Execute step based on step name
            if step.step_name == "validate_payment":
                payment_request = PaymentRequest(**step.input_data)
                result = await self.payment_service.validate_payment(payment_request)
            
            elif step.step_name == "validate_merchant":
                result = await self.merchant_service.validate_merchant(
                    step.input_data["merchant_id"], 
                    step.input_data["amount"]
                )
            
            elif step.step_name == "reserve_funds":
                result = await self.payment_service.reserve_funds(
                    step.input_data["user_id"],
                    step.input_data["amount"],
                    PaymentMethod(step.input_data["payment_method"])
                )
            
            elif step.step_name == "calculate_commission":
                result = await self.commission_service.calculate_commission(
                    step.input_data["merchant_id"],
                    step.input_data["amount"]
                )
            
            elif step.step_name == "credit_merchant":
                result = await self.merchant_service.credit_merchant(
                    step.input_data["merchant_id"],
                    step.input_data["amount"],
                    step.input_data["transaction_id"]
                )
            
            elif step.step_name == "collect_commission":
                # Get commission data from previous step
                commission_step = next(s for s in saga.steps if s.step_name == "calculate_commission")
                commission_data = commission_step.output_data
                
                result = await self.commission_service.collect_commission(
                    commission_data["commission_id"],
                    commission_data["commission_amount"]
                )
            
            elif step.step_name == "send_notification":
                result = await self.notification_service.send_payment_notification(
                    step.input_data["user_id"],
                    step.input_data["merchant_id"],
                    step.input_data["amount"],
                    step.input_data["status"]
                )
            
            else:
                raise ValueError(f"Unknown step: {step.step_name}")
            
            # Step completed successfully
            step.status = SagaStepStatus.COMPLETED
            step.output_data = result
            
            await self._publish_event(SagaStepCompletedEvent(
                saga_id=saga.saga_id,
                step_id=step.step_id,
                step_name=step.step_name,
                output_data=result,
                timestamp=datetime.now()
            ))
            
            print(f"✅ Step {step.step_name} completed for saga {saga.saga_id}")
            return True
            
        except Exception as e:
            step.status = SagaStepStatus.FAILED
            step.error_message = str(e)
            step.retry_count += 1
            
            await self._publish_event(SagaStepFailedEvent(
                saga_id=saga.saga_id,
                step_id=step.step_id,
                step_name=step.step_name,
                error_message=str(e),
                retry_count=step.retry_count,
                timestamp=datetime.now()
            ))
            
            # Retry if under max retries
            if step.retry_count < step.max_retries:
                print(f"🔄 Retrying step {step.step_name} (attempt {step.retry_count + 1})")
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                return await self._execute_step(saga, step)
            
            print(f"❌ Step {step.step_name} failed permanently for saga {saga.saga_id}: {e}")
            return False
    
    async def _compensate_saga(self, saga: PaymentSaga):
        """Execute compensation for completed steps"""
        saga.status = TransactionStatus.COMPENSATING
        
        print(f"🔄 Starting compensation for saga {saga.saga_id}")
        
        # Compensate in reverse order
        completed_steps = [s for s in reversed(saga.steps) if s.status == SagaStepStatus.COMPLETED]
        
        for step in completed_steps:
            try:
                await self._compensate_step(step)
            except Exception as e:
                print(f"⚠️ Compensation failed for step {step.step_name}: {e}")
        
        saga.status = TransactionStatus.COMPENSATED
        
        await self._publish_event(SagaCompletedEvent(
            saga_id=saga.saga_id,
            payment_id=saga.payment_id,
            final_status=TransactionStatus.COMPENSATED,
            timestamp=datetime.now()
        ))
        
        print(f"🔄 Saga {saga.saga_id} compensation completed")
    
    async def _compensate_step(self, step: SagaStep):
        """Execute compensation for individual step"""
        step.status = SagaStepStatus.COMPENSATING
        
        try:
            if step.step_name == "reserve_funds":
                reservation_id = step.output_data["reservation_id"]
                await self.payment_service.release_funds(reservation_id)
            
            elif step.step_name == "credit_merchant":
                settlement_id = step.output_data["settlement_id"]
                amount = step.output_data["credited_amount"]
                await self.merchant_service.debit_merchant(settlement_id, amount)
            
            elif step.step_name == "collect_commission":
                commission_id = step.output_data["commission_id"]
                await self.commission_service.refund_commission(commission_id)
            
            # Other steps might not need compensation
            
            step.status = SagaStepStatus.COMPENSATED
            print(f"🔄 Compensated step {step.step_name}")
            
        except Exception as e:
            print(f"❌ Compensation failed for step {step.step_name}: {e}")
            raise
    
    def get_saga_status(self, saga_id: str) -> Optional[PaymentSaga]:
        """Get current saga status"""
        return self.sagas.get(saga_id)

# Event Handlers
async def saga_event_handler(event: Any):
    """Handle saga events for logging/monitoring"""
    if isinstance(event, SagaStartedEvent):
        print(f"📋 Saga started: {event.saga_id} for payment {event.payment_id}")
    elif isinstance(event, SagaStepCompletedEvent):
        print(f"✅ Step completed: {event.step_name} in saga {event.saga_id}")
    elif isinstance(event, SagaStepFailedEvent):
        print(f"❌ Step failed: {event.step_name} in saga {event.saga_id} - {event.error_message}")
    elif isinstance(event, SagaCompletedEvent):
        print(f"🎉 Saga completed: {event.saga_id} with status {event.final_status.value}")

# Demo Function
async def demonstrate_payment_saga():
    """Demonstrate Paytm payment saga orchestration"""
    print("💳 Paytm Payment Saga Orchestration Demo")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = PaymentSagaOrchestrator()
    orchestrator.add_event_handler(saga_event_handler)
    
    # Create payment request
    payment_request = PaymentRequest(
        payment_id=f"PAY{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
        user_id="USER001",
        merchant_id="MERCHANT001",
        amount=2500.0,
        payment_method=PaymentMethod.WALLET,
        merchant_category="ecommerce",
        order_id="ORDER123456",
        description="Purchase from Flipkart",
        metadata={"app": "paytm", "version": "1.2.3"}
    )
    
    try:
        # Start saga
        saga_id = await orchestrator.start_payment_saga(payment_request)
        
        # Wait for completion
        await asyncio.sleep(3)
        
        # Check final status
        saga = orchestrator.get_saga_status(saga_id)
        if saga:
            print(f"\n📊 Final Saga Status:")
            print(f"  Saga ID: {saga.saga_id}")
            print(f"  Payment ID: {saga.payment_id}")
            print(f"  Status: {saga.status.value}")
            print(f"  Total Steps: {len(saga.steps)}")
            
            completed_steps = [s for s in saga.steps if s.status == SagaStepStatus.COMPLETED]
            failed_steps = [s for s in saga.steps if s.status == SagaStepStatus.FAILED]
            compensated_steps = [s for s in saga.steps if s.status == SagaStepStatus.COMPENSATED]
            
            print(f"  Completed Steps: {len(completed_steps)}")
            print(f"  Failed Steps: {len(failed_steps)}")
            print(f"  Compensated Steps: {len(compensated_steps)}")
            
            if saga.error_message:
                print(f"  Error: {saga.error_message}")
        
        print("\n✅ Payment Saga Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    """
    Key Saga Pattern Benefits:
    1. Distributed Transaction Management: Multiple services coordination
    2. Compensation Logic: Automatic rollback on failures
    3. Fault Tolerance: Retry mechanisms और error recovery
    4. Observability: Complete transaction visibility
    5. Scalability: Asynchronous processing
    6. Business Logic Isolation: Clear separation of concerns
    """
    asyncio.run(demonstrate_payment_saga())