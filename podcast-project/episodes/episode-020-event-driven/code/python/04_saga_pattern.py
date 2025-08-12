#!/usr/bin/env python3
"""
Saga Pattern Implementation for Distributed Transactions
उदाहरण: BigBasket online grocery order के लिए distributed transaction

Setup:
pip install asyncio enum dataclasses

Indian Context: BigBasket पर जब customer order place करता है,
multiple services को coordinate करना पड़ता है:
1. Inventory service - stock check and reserve
2. Payment service - payment processing
3. Delivery service - slot booking
4. Loyalty service - points deduction/addition
5. Notification service - customer updates

अगर कोई step fail हो जाए तो compensating actions चलाने पड़ते हैं
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import logging
import random

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SagaStatus(Enum):
    """Saga execution status"""
    STARTED = "started"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

class StepStatus(Enum):
    """Individual step status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    """Individual step in saga"""
    step_id: str
    step_name: str
    service_name: str
    action: Callable
    compensation: Callable
    status: StepStatus = StepStatus.PENDING
    result: Dict[str, Any] = None
    error: str = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.result is None:
            self.result = {}

@dataclass
class SagaExecution:
    """Saga execution state"""
    saga_id: str
    order_id: str
    customer_id: str
    status: SagaStatus = SagaStatus.STARTED
    steps: List[SagaStep] = None
    current_step_index: int = 0
    started_at: str = None
    completed_at: str = None
    error_message: str = None
    compensation_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()
        if self.compensation_data is None:
            self.compensation_data = {}

class SagaOrchestrator:
    """
    Saga pattern orchestrator
    Film director की तरह - sabko coordinate करता है
    """
    
    def __init__(self):
        self.active_sagas: Dict[str, SagaExecution] = {}
        self.saga_history: List[SagaExecution] = []
    
    async def start_saga(self, order_id: str, customer_id: str, steps: List[SagaStep]) -> str:
        """Saga execution start karna"""
        saga_id = f"SAGA_{uuid.uuid4().hex[:8].upper()}"
        
        saga = SagaExecution(
            saga_id=saga_id,
            order_id=order_id,
            customer_id=customer_id,
            steps=steps
        )
        
        self.active_sagas[saga_id] = saga
        
        logger.info(f"🎬 Saga started: {saga_id} for order {order_id}")
        logger.info(f"   📋 Steps: {len(steps)}")
        
        # Async execution start karna
        asyncio.create_task(self._execute_saga(saga))
        
        return saga_id
    
    async def _execute_saga(self, saga: SagaExecution):
        """Saga execute karna - step by step"""
        try:
            saga.status = SagaStatus.EXECUTING
            
            for i, step in enumerate(saga.steps):
                saga.current_step_index = i
                step.status = StepStatus.EXECUTING
                
                logger.info(f"⚙️ Executing step {i+1}/{len(saga.steps)}: {step.step_name}")
                
                # Step execute karna with retries
                success = await self._execute_step_with_retry(step, saga)
                
                if success:
                    step.status = StepStatus.COMPLETED
                    logger.info(f"✅ Step completed: {step.step_name}")
                else:
                    step.status = StepStatus.FAILED
                    logger.error(f"❌ Step failed: {step.step_name} - {step.error}")
                    
                    # Compensation शुरू करना
                    await self._compensate_saga(saga, i)
                    return
            
            # सभी steps successful
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now().isoformat()
            
            logger.info(f"🎉 Saga completed successfully: {saga.saga_id}")
            
        except Exception as e:
            logger.error(f"❌ Saga execution failed: {saga.saga_id} - {e}")
            saga.status = SagaStatus.FAILED
            saga.error_message = str(e)
        finally:
            # Active से remove करके history में move करना
            if saga.saga_id in self.active_sagas:
                del self.active_sagas[saga.saga_id]
            self.saga_history.append(saga)
    
    async def _execute_step_with_retry(self, step: SagaStep, saga: SagaExecution) -> bool:
        """Step को retry logic के साथ execute karna"""
        for attempt in range(step.max_retries + 1):
            try:
                # Step action execute karna
                result = await step.action(saga)
                step.result = result
                return True
                
            except Exception as e:
                step.retry_count = attempt + 1
                step.error = str(e)
                
                logger.warning(f"⚠️ Step {step.step_name} failed (attempt {attempt + 1}): {e}")
                
                if attempt < step.max_retries:
                    # Exponential backoff
                    delay = 2 ** attempt
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ Step {step.step_name} failed after {step.max_retries + 1} attempts")
                    return False
        
        return False
    
    async def _compensate_saga(self, saga: SagaExecution, failed_step_index: int):
        """
        Saga compensation - rollback actions
        Train accident के बाद passengers को वापस भेजना
        """
        logger.warning(f"🔄 Starting compensation for saga {saga.saga_id}")
        saga.status = SagaStatus.COMPENSATING
        
        # Reverse order mein compensation execute karna
        for i in range(failed_step_index - 1, -1, -1):
            step = saga.steps[i]
            
            if step.status == StepStatus.COMPLETED:
                logger.info(f"🔄 Compensating step: {step.step_name}")
                step.status = StepStatus.COMPENSATING
                
                try:
                    compensation_result = await step.compensation(saga, step.result)
                    step.status = StepStatus.COMPENSATED
                    
                    logger.info(f"✅ Step compensated: {step.step_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Compensation failed for {step.step_name}: {e}")
                    # Compensation failure को handle करना critical है
        
        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.now().isoformat()
        
        logger.info(f"🔄 Saga compensation completed: {saga.saga_id}")
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Saga status check karna"""
        # Active sagas mein check करना
        if saga_id in self.active_sagas:
            saga = self.active_sagas[saga_id]
        else:
            # History mein check करना
            saga = next((s for s in self.saga_history if s.saga_id == saga_id), None)
        
        if saga:
            return {
                'saga_id': saga.saga_id,
                'order_id': saga.order_id,
                'status': saga.status.value,
                'current_step': saga.current_step_index + 1,
                'total_steps': len(saga.steps),
                'steps': [
                    {
                        'step_name': step.step_name,
                        'status': step.status.value,
                        'retry_count': step.retry_count
                    }
                    for step in saga.steps
                ]
            }
        return None

# BigBasket order processing services

class InventoryService:
    """Inventory management service"""
    
    def __init__(self):
        self.service_name = "Inventory Service"
        self.stock_db = {
            "RICE_5KG": {"available": 100, "reserved": 0},
            "WHEAT_FLOUR_1KG": {"available": 200, "reserved": 0},
            "SUGAR_1KG": {"available": 150, "reserved": 0},
            "OIL_1L": {"available": 80, "reserved": 0},
            "MILK_1L": {"available": 50, "reserved": 0}
        }
    
    async def reserve_items(self, saga: SagaExecution) -> Dict[str, Any]:
        """Items ko reserve karna"""
        order_data = saga.compensation_data.get('order_items', [])
        reserved_items = []
        
        logger.info(f"📦 {self.service_name}: Reserving items for order {saga.order_id}")
        
        for item in order_data:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if product_id in self.stock_db:
                stock = self.stock_db[product_id]
                
                if stock['available'] >= quantity:
                    # Stock reserve karna
                    stock['available'] -= quantity
                    stock['reserved'] += quantity
                    
                    reserved_items.append({
                        'product_id': product_id,
                        'quantity': quantity,
                        'reservation_id': f"RES_{uuid.uuid4().hex[:8]}"
                    })
                    
                    logger.info(f"   ✅ Reserved {quantity}x {product_id}")
                else:
                    # Stock nahi hai
                    raise Exception(f"Insufficient stock for {product_id}: {stock['available']} < {quantity}")
            else:
                raise Exception(f"Product not found: {product_id}")
        
        # Simulation delay
        await asyncio.sleep(0.3)
        
        return {'reserved_items': reserved_items}
    
    async def compensate_reservation(self, saga: SagaExecution, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Reservation cancel karna - compensation"""
        reserved_items = step_result.get('reserved_items', [])
        
        logger.info(f"🔄 {self.service_name}: Cancelling reservations for order {saga.order_id}")
        
        for item in reserved_items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if product_id in self.stock_db:
                stock = self.stock_db[product_id]
                # Stock को वापस available में डालना
                stock['available'] += quantity
                stock['reserved'] -= quantity
                
                logger.info(f"   🔄 Released {quantity}x {product_id}")
        
        return {'cancelled_reservations': reserved_items}

class PaymentService:
    """Payment processing service"""
    
    def __init__(self):
        self.service_name = "Payment Service"
        self.customer_wallets = {
            "CUST001": 5000.0,
            "CUST002": 8000.0,
            "CUST003": 3000.0
        }
    
    async def process_payment(self, saga: SagaExecution) -> Dict[str, Any]:
        """Payment process karna"""
        order_total = saga.compensation_data.get('order_total', 0.0)
        customer_id = saga.customer_id
        
        logger.info(f"💳 {self.service_name}: Processing payment for order {saga.order_id}")
        logger.info(f"   💰 Amount: ₹{order_total}")
        
        if customer_id not in self.customer_wallets:
            raise Exception(f"Customer wallet not found: {customer_id}")
        
        wallet_balance = self.customer_wallets[customer_id]
        
        if wallet_balance < order_total:
            raise Exception(f"Insufficient wallet balance: ₹{wallet_balance} < ₹{order_total}")
        
        # Payment simulation delay
        await asyncio.sleep(0.5)
        
        # 10% chance of payment failure (for demo)
        if random.random() < 0.1:
            raise Exception("Payment gateway timeout")
        
        # Wallet से amount deduct karna
        self.customer_wallets[customer_id] -= order_total
        
        transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"✅ Payment successful: {transaction_id}")
        
        return {
            'transaction_id': transaction_id,
            'amount': order_total,
            'remaining_balance': self.customer_wallets[customer_id]
        }
    
    async def compensate_payment(self, saga: SagaExecution, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Payment refund karna - compensation"""
        amount = step_result.get('amount', 0.0)
        customer_id = saga.customer_id
        transaction_id = step_result.get('transaction_id')
        
        logger.info(f"🔄 {self.service_name}: Refunding payment for order {saga.order_id}")
        logger.info(f"   💰 Refund Amount: ₹{amount}")
        
        # Wallet mein amount वापस करना
        self.customer_wallets[customer_id] += amount
        
        refund_id = f"REF_{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"✅ Payment refunded: {refund_id}")
        
        return {
            'refund_id': refund_id,
            'original_transaction_id': transaction_id,
            'refunded_amount': amount
        }

class DeliveryService:
    """Delivery slot booking service"""
    
    def __init__(self):
        self.service_name = "Delivery Service"
        self.available_slots = {
            "SLOT_1": {"time": "09:00-12:00", "capacity": 10, "booked": 0},
            "SLOT_2": {"time": "12:00-15:00", "capacity": 15, "booked": 0},
            "SLOT_3": {"time": "15:00-18:00", "capacity": 12, "booked": 0},
            "SLOT_4": {"time": "18:00-21:00", "capacity": 8, "booked": 0}
        }
    
    async def book_delivery_slot(self, saga: SagaExecution) -> Dict[str, Any]:
        """Delivery slot book karna"""
        preferred_slot = saga.compensation_data.get('preferred_delivery_slot', 'SLOT_2')
        delivery_address = saga.compensation_data.get('delivery_address', 'Mumbai')
        
        logger.info(f"🚛 {self.service_name}: Booking delivery slot for order {saga.order_id}")
        logger.info(f"   📍 Address: {delivery_address}")
        logger.info(f"   🕐 Preferred: {preferred_slot}")
        
        # Preferred slot check karna
        if preferred_slot in self.available_slots:
            slot = self.available_slots[preferred_slot]
            
            if slot['booked'] < slot['capacity']:
                # Slot book karna
                slot['booked'] += 1
                
                booking_id = f"DEL_{uuid.uuid4().hex[:8].upper()}"
                
                # Simulation delay
                await asyncio.sleep(0.4)
                
                logger.info(f"✅ Delivery slot booked: {slot['time']} - {booking_id}")
                
                return {
                    'booking_id': booking_id,
                    'slot_id': preferred_slot,
                    'delivery_time': slot['time'],
                    'delivery_address': delivery_address
                }
            else:
                raise Exception(f"Delivery slot {preferred_slot} is full")
        else:
            raise Exception(f"Invalid delivery slot: {preferred_slot}")
    
    async def compensate_delivery_booking(self, saga: SagaExecution, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Delivery booking cancel karna - compensation"""
        slot_id = step_result.get('slot_id')
        booking_id = step_result.get('booking_id')
        
        logger.info(f"🔄 {self.service_name}: Cancelling delivery booking for order {saga.order_id}")
        logger.info(f"   📋 Booking: {booking_id}")
        
        if slot_id in self.available_slots:
            # Slot को free करना
            self.available_slots[slot_id]['booked'] -= 1
            
            logger.info(f"✅ Delivery booking cancelled: {booking_id}")
            
            return {
                'cancelled_booking_id': booking_id,
                'freed_slot': slot_id
            }
        
        return {}

class LoyaltyService:
    """Customer loyalty points service"""
    
    def __init__(self):
        self.service_name = "Loyalty Service"
        self.customer_points = {
            "CUST001": 2500,
            "CUST002": 1800,
            "CUST003": 950
        }
    
    async def apply_loyalty_points(self, saga: SagaExecution) -> Dict[str, Any]:
        """Loyalty points apply/deduct karna"""
        order_total = saga.compensation_data.get('order_total', 0.0)
        points_to_use = saga.compensation_data.get('loyalty_points_to_use', 0)
        customer_id = saga.customer_id
        
        logger.info(f"🏆 {self.service_name}: Processing loyalty points for order {saga.order_id}")
        logger.info(f"   👤 Customer: {customer_id}")
        logger.info(f"   🎯 Points to use: {points_to_use}")
        
        if customer_id not in self.customer_points:
            # New customer - initialize with 0 points
            self.customer_points[customer_id] = 0
        
        available_points = self.customer_points[customer_id]
        
        if points_to_use > available_points:
            raise Exception(f"Insufficient loyalty points: {available_points} < {points_to_use}")
        
        # Points deduct karna
        self.customer_points[customer_id] -= points_to_use
        
        # New points earn karna (1 point per ₹10)
        points_earned = int(order_total / 10)
        self.customer_points[customer_id] += points_earned
        
        # Simulation delay
        await asyncio.sleep(0.2)
        
        logger.info(f"✅ Loyalty points processed: Used {points_to_use}, Earned {points_earned}")
        
        return {
            'points_used': points_to_use,
            'points_earned': points_earned,
            'current_balance': self.customer_points[customer_id]
        }
    
    async def compensate_loyalty_points(self, saga: SagaExecution, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Loyalty points को revert karna - compensation"""
        points_used = step_result.get('points_used', 0)
        points_earned = step_result.get('points_earned', 0)
        customer_id = saga.customer_id
        
        logger.info(f"🔄 {self.service_name}: Reverting loyalty points for order {saga.order_id}")
        
        # Used points को वापस करना
        self.customer_points[customer_id] += points_used
        
        # Earned points को remove करना
        self.customer_points[customer_id] -= points_earned
        
        logger.info(f"✅ Loyalty points reverted: +{points_used} used, -{points_earned} earned")
        
        return {
            'reverted_used_points': points_used,
            'reverted_earned_points': points_earned
        }

async def bigbasket_order_demo():
    """BigBasket order processing saga demo"""
    print("🛒 BigBasket Order Processing Saga Demo")
    print("=" * 50)
    
    # Services initialize karna
    inventory_service = InventoryService()
    payment_service = PaymentService()
    delivery_service = DeliveryService()
    loyalty_service = LoyaltyService()
    
    # Saga orchestrator
    orchestrator = SagaOrchestrator()
    
    # Sample order data
    order_data = {
        'order_items': [
            {'product_id': 'RICE_5KG', 'quantity': 2, 'price': 350.0},
            {'product_id': 'WHEAT_FLOUR_1KG', 'quantity': 3, 'price': 45.0},
            {'product_id': 'SUGAR_1KG', 'quantity': 1, 'price': 55.0},
            {'product_id': 'OIL_1L', 'quantity': 2, 'price': 120.0}
        ],
        'order_total': 970.0,
        'customer_id': 'CUST001',
        'delivery_address': 'Andheri West, Mumbai',
        'preferred_delivery_slot': 'SLOT_2',
        'loyalty_points_to_use': 500  # ₹50 discount
    }
    
    customer_id = order_data['customer_id']
    order_id = f"BB_{uuid.uuid4().hex[:8].upper()}"
    
    print(f"🛍️ Order ID: {order_id}")
    print(f"👤 Customer: {customer_id}")
    print(f"💰 Order Total: ₹{order_data['order_total']}")
    print(f"🎯 Loyalty Points to Use: {order_data['loyalty_points_to_use']}")
    print()
    
    # Saga steps define karna
    steps = [
        SagaStep(
            step_id="1",
            step_name="Reserve Inventory",
            service_name="Inventory Service",
            action=inventory_service.reserve_items,
            compensation=inventory_service.compensate_reservation
        ),
        SagaStep(
            step_id="2",
            step_name="Process Payment",
            service_name="Payment Service",
            action=payment_service.process_payment,
            compensation=payment_service.compensate_payment
        ),
        SagaStep(
            step_id="3",
            step_name="Book Delivery Slot",
            service_name="Delivery Service",
            action=delivery_service.book_delivery_slot,
            compensation=delivery_service.compensate_delivery_booking
        ),
        SagaStep(
            step_id="4",
            step_name="Apply Loyalty Points",
            service_name="Loyalty Service",
            action=loyalty_service.apply_loyalty_points,
            compensation=loyalty_service.compensate_loyalty_points
        )
    ]
    
    # Order data को saga mein pass karna
    for step in steps:
        step.result = {'order_data': order_data}
    
    # Saga execution start karna
    saga_id = await orchestrator.start_saga(order_id, customer_id, steps)
    
    # Context data set karna
    saga = orchestrator.active_sagas[saga_id]
    saga.compensation_data.update(order_data)
    
    print(f"🎬 Saga started: {saga_id}")
    print("⏳ Processing order...")
    
    # Wait for saga completion
    for i in range(30):  # 30 seconds max wait
        await asyncio.sleep(1)
        
        status = orchestrator.get_saga_status(saga_id)
        if status and status['status'] in ['completed', 'failed', 'compensated']:
            break
    
    # Final status check karna
    final_status = orchestrator.get_saga_status(saga_id)
    
    if final_status:
        print(f"\n📊 Final Saga Status: {final_status['status'].upper()}")
        print(f"📋 Steps Completed: {final_status['current_step']}/{final_status['total_steps']}")
        
        print("\n📝 Step Details:")
        for i, step_info in enumerate(final_status['steps'], 1):
            status_emoji = "✅" if step_info['status'] == 'completed' else \
                          "🔄" if step_info['status'] == 'compensated' else \
                          "❌" if step_info['status'] == 'failed' else "⏳"
            
            print(f"   {status_emoji} Step {i}: {step_info['step_name']} - {step_info['status']}")
            if step_info['retry_count'] > 0:
                print(f"      🔄 Retries: {step_info['retry_count']}")
    
    # System state check karna
    print(f"\n💾 System State After Order:")
    print(f"   💰 Customer {customer_id} wallet: ₹{payment_service.customer_wallets.get(customer_id, 0)}")
    print(f"   🏆 Customer {customer_id} points: {loyalty_service.customer_points.get(customer_id, 0)}")
    
    print("   📦 Stock Status:")
    for product, stock in inventory_service.stock_db.items():
        print(f"      {product}: {stock['available']} available, {stock['reserved']} reserved")
    
    print("   🚛 Delivery Slots:")
    for slot_id, slot in delivery_service.available_slots.items():
        print(f"      {slot_id} ({slot['time']}): {slot['booked']}/{slot['capacity']} booked")

# Demo with failure scenario
async def failure_scenario_demo():
    """Failure scenario demo - payment failure के साथ"""
    print("\n" + "="*60)
    print("🚨 Failure Scenario Demo - Payment Gateway Issues")
    print("="*60)
    
    # Services with modified payment service (higher failure rate)
    inventory_service = InventoryService()
    
    class FailurePaymentService(PaymentService):
        async def process_payment(self, saga: SagaExecution) -> Dict[str, Any]:
            # Force payment failure for demo
            raise Exception("Payment gateway is down - maintenance mode")
    
    payment_service = FailurePaymentService()
    delivery_service = DeliveryService()
    loyalty_service = LoyaltyService()
    
    orchestrator = SagaOrchestrator()
    
    # Same order setup
    order_data = {
        'order_items': [
            {'product_id': 'MILK_1L', 'quantity': 5, 'price': 60.0}
        ],
        'order_total': 300.0,
        'customer_id': 'CUST002',
        'delivery_address': 'Bandra West, Mumbai',
        'preferred_delivery_slot': 'SLOT_3',
        'loyalty_points_to_use': 100
    }
    
    order_id = f"BB_FAIL_{uuid.uuid4().hex[:8].upper()}"
    
    print(f"🛍️ Order ID: {order_id}")
    print(f"💰 Order Total: ₹{order_data['order_total']}")
    print("⚠️ Expected: Payment will fail and trigger compensation")
    print()
    
    # Same steps setup
    steps = [
        SagaStep(
            step_id="1",
            step_name="Reserve Inventory",
            service_name="Inventory Service",
            action=inventory_service.reserve_items,
            compensation=inventory_service.compensate_reservation
        ),
        SagaStep(
            step_id="2",
            step_name="Process Payment",
            service_name="Payment Service",
            action=payment_service.process_payment,
            compensation=payment_service.compensate_payment
        ),
        SagaStep(
            step_id="3",
            step_name="Book Delivery Slot",
            service_name="Delivery Service",
            action=delivery_service.book_delivery_slot,
            compensation=delivery_service.compensate_delivery_booking
        )
    ]
    
    saga_id = await orchestrator.start_saga(order_id, order_data['customer_id'], steps)
    saga = orchestrator.active_sagas[saga_id]
    saga.compensation_data.update(order_data)
    
    # Wait for completion/compensation
    for i in range(20):
        await asyncio.sleep(1)
        status = orchestrator.get_saga_status(saga_id)
        if status and status['status'] in ['compensated', 'failed']:
            break
    
    # Results
    final_status = orchestrator.get_saga_status(saga_id)
    print(f"\n📊 Final Status: {final_status['status'].upper()}")
    print("✅ Compensation completed - all changes reverted!")

if __name__ == "__main__":
    asyncio.run(bigbasket_order_demo())
    asyncio.run(failure_scenario_demo())