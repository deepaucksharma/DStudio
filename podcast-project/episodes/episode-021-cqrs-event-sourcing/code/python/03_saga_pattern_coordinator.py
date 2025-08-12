"""
Saga Pattern Coordinator - Flipkart Order Processing के लिए
यह example दिखाता है कि कैसे distributed transactions को handle करते हैं
"""

import asyncio
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SagaStepStatus(Enum):
    """Saga step का status"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"

class SagaStatus(Enum):
    """पूरे Saga का status"""
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"

@dataclass
class SagaStep:
    """Saga का एक step"""
    step_id: str
    name: str
    status: SagaStepStatus = SagaStepStatus.PENDING
    execute_command: Dict[str, Any] = None
    compensate_command: Dict[str, Any] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class Saga:
    """Complete Saga definition"""
    saga_id: str
    name: str
    status: SagaStatus = SagaStatus.STARTED
    steps: List[SagaStep] = None
    context: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.context is None:
            self.context = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

# Mock External Services - Flipkart के micro-services
class InventoryService:
    """Inventory management service"""
    
    def __init__(self):
        self.inventory = {
            "MOBILE_001": {"available": 50, "reserved": 0},
            "LAPTOP_002": {"available": 20, "reserved": 0},
            "BOOK_003": {"available": 100, "reserved": 0}
        }
    
    async def reserve_item(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Product को reserve करता है"""
        await asyncio.sleep(0.5)  # Network latency simulate करते हैं
        
        if product_id not in self.inventory:
            raise ValueError(f"Product {product_id} नहीं मिला")
        
        item = self.inventory[product_id]
        if item["available"] < quantity:
            raise ValueError(f"केवल {item['available']} items available हैं")
        
        # Reserve करते हैं
        item["available"] -= quantity
        item["reserved"] += quantity
        
        logger.info(f"✅ Reserved {quantity} units of {product_id} for order {order_id}")
        return True
    
    async def release_reservation(self, product_id: str, quantity: int, order_id: str) -> bool:
        """Reservation को release करता है"""
        await asyncio.sleep(0.3)
        
        if product_id in self.inventory:
            item = self.inventory[product_id]
            item["available"] += quantity
            item["reserved"] -= quantity
            
            logger.info(f"🔄 Released reservation for {quantity} units of {product_id}")
        
        return True

class PaymentService:
    """Payment processing service"""
    
    def __init__(self):
        self.transactions = {}
        self.user_balances = {
            "USER_123": 50000.0,  # ₹50,000 balance
            "USER_456": 25000.0,
            "USER_789": 75000.0
        }
    
    async def process_payment(self, user_id: str, amount: float, order_id: str) -> str:
        """Payment को process करता है"""
        await asyncio.sleep(1.0)  # Payment gateway delay
        
        if user_id not in self.user_balances:
            raise ValueError(f"User {user_id} नहीं मिला")
        
        if self.user_balances[user_id] < amount:
            raise ValueError(f"Insufficient balance. Available: ₹{self.user_balances[user_id]}")
        
        # Payment process करते हैं
        transaction_id = f"TXN_{uuid.uuid4().hex[:8]}"
        self.user_balances[user_id] -= amount
        self.transactions[transaction_id] = {
            "user_id": user_id,
            "amount": amount,
            "order_id": order_id,
            "status": "COMPLETED",
            "timestamp": datetime.now()
        }
        
        logger.info(f"💳 Payment processed: ₹{amount} from {user_id}, TXN: {transaction_id}")
        return transaction_id
    
    async def refund_payment(self, transaction_id: str) -> bool:
        """Payment को refund करता है"""
        await asyncio.sleep(0.8)
        
        if transaction_id not in self.transactions:
            logger.warning(f"Transaction {transaction_id} नहीं मिला")
            return False
        
        txn = self.transactions[transaction_id]
        self.user_balances[txn["user_id"]] += txn["amount"]
        txn["status"] = "REFUNDED"
        
        logger.info(f"💰 Refund processed: ₹{txn['amount']} to {txn['user_id']}")
        return True

class DeliveryService:
    """Delivery/Shipping service"""
    
    def __init__(self):
        self.shipments = {}
    
    async def create_shipment(self, order_id: str, address: str, items: List[Dict]) -> str:
        """Shipment create करता है"""
        await asyncio.sleep(0.7)
        
        shipment_id = f"SHIP_{uuid.uuid4().hex[:8]}"
        self.shipments[shipment_id] = {
            "order_id": order_id,
            "address": address,
            "items": items,
            "status": "CREATED",
            "estimated_delivery": datetime.now() + timedelta(days=3)
        }
        
        logger.info(f"📦 Shipment created: {shipment_id} for order {order_id}")
        return shipment_id
    
    async def cancel_shipment(self, shipment_id: str) -> bool:
        """Shipment को cancel करता है"""
        await asyncio.sleep(0.5)
        
        if shipment_id in self.shipments:
            self.shipments[shipment_id]["status"] = "CANCELLED"
            logger.info(f"❌ Shipment cancelled: {shipment_id}")
        
        return True

class OrderService:
    """Order management service"""
    
    def __init__(self):
        self.orders = {}
    
    async def create_order(self, user_id: str, items: List[Dict], total_amount: float) -> str:
        """Order create करता है"""
        await asyncio.sleep(0.3)
        
        order_id = f"ORD_{uuid.uuid4().hex[:8]}"
        self.orders[order_id] = {
            "user_id": user_id,
            "items": items,
            "total_amount": total_amount,
            "status": "CREATED",
            "created_at": datetime.now()
        }
        
        logger.info(f"📋 Order created: {order_id} for ₹{total_amount}")
        return order_id
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Order status update करता है"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            logger.info(f"📝 Order {order_id} status updated to {status}")
        
        return True
    
    async def cancel_order(self, order_id: str) -> bool:
        """Order को cancel करता है"""
        return await self.update_order_status(order_id, "CANCELLED")

# Saga Coordinator - मुख्य orchestrator
class SagaCoordinator:
    """Saga को coordinate करता है"""
    
    def __init__(self):
        self.sagas: Dict[str, Saga] = {}
        self.running_sagas: Dict[str, asyncio.Task] = {}
        
        # External services setup करते हैं
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.delivery_service = DeliveryService()
        self.order_service = OrderService()
    
    def create_flipkart_order_saga(self, user_id: str, items: List[Dict], 
                                 delivery_address: str) -> Saga:
        """Flipkart order के लिए complete saga create करता है"""
        
        saga_id = f"SAGA_{uuid.uuid4().hex[:8]}"
        total_amount = sum(item["price"] * item["quantity"] for item in items)
        
        saga = Saga(
            saga_id=saga_id,
            name="FLIPKART_ORDER_PROCESSING",
            context={
                "user_id": user_id,
                "items": items,
                "delivery_address": delivery_address,
                "total_amount": total_amount,
                "order_id": None,
                "transaction_id": None,
                "shipment_id": None
            }
        )
        
        # Saga steps define करते हैं
        saga.steps = [
            SagaStep(
                step_id="CREATE_ORDER",
                name="Create Order",
                execute_command={
                    "service": "order",
                    "method": "create_order",
                    "params": {
                        "user_id": user_id,
                        "items": items,
                        "total_amount": total_amount
                    }
                },
                compensate_command={
                    "service": "order",
                    "method": "cancel_order",
                    "params": {"order_id": "{order_id}"}
                }
            ),
            
            SagaStep(
                step_id="RESERVE_INVENTORY",
                name="Reserve Inventory",
                execute_command={
                    "service": "inventory",
                    "method": "reserve_items",
                    "params": {
                        "items": items,
                        "order_id": "{order_id}"
                    }
                },
                compensate_command={
                    "service": "inventory", 
                    "method": "release_reservations",
                    "params": {
                        "items": items,
                        "order_id": "{order_id}"
                    }
                }
            ),
            
            SagaStep(
                step_id="PROCESS_PAYMENT",
                name="Process Payment",
                execute_command={
                    "service": "payment",
                    "method": "process_payment",
                    "params": {
                        "user_id": user_id,
                        "amount": total_amount,
                        "order_id": "{order_id}"
                    }
                },
                compensate_command={
                    "service": "payment",
                    "method": "refund_payment", 
                    "params": {"transaction_id": "{transaction_id}"}
                }
            ),
            
            SagaStep(
                step_id="CREATE_SHIPMENT",
                name="Create Shipment",
                execute_command={
                    "service": "delivery",
                    "method": "create_shipment",
                    "params": {
                        "order_id": "{order_id}",
                        "address": delivery_address,
                        "items": items
                    }
                },
                compensate_command={
                    "service": "delivery",
                    "method": "cancel_shipment",
                    "params": {"shipment_id": "{shipment_id}"}
                }
            ),
            
            SagaStep(
                step_id="CONFIRM_ORDER",
                name="Confirm Order",
                execute_command={
                    "service": "order",
                    "method": "update_order_status",
                    "params": {
                        "order_id": "{order_id}",
                        "status": "CONFIRMED"
                    }
                },
                compensate_command={
                    "service": "order",
                    "method": "update_order_status",
                    "params": {
                        "order_id": "{order_id}",
                        "status": "CANCELLED"
                    }
                }
            )
        ]
        
        self.sagas[saga_id] = saga
        return saga
    
    async def execute_saga(self, saga_id: str) -> bool:
        """Saga को execute करता है"""
        saga = self.sagas.get(saga_id)
        if not saga:
            raise ValueError(f"Saga {saga_id} नहीं मिला")
        
        logger.info(f"🚀 Starting saga execution: {saga.name} ({saga_id})")
        saga.status = SagaStatus.IN_PROGRESS
        
        try:
            # सभी steps को execute करते हैं
            for step in saga.steps:
                success = await self._execute_step(saga, step)
                if not success:
                    # Step fail हो गया, compensation करते हैं
                    await self._compensate_saga(saga, step)
                    return False
            
            # सभी steps successful हैं
            saga.status = SagaStatus.COMPLETED
            saga.updated_at = datetime.now()
            logger.info(f"✅ Saga completed successfully: {saga_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Saga execution failed: {str(e)}")
            saga.status = SagaStatus.FAILED
            await self._compensate_saga(saga)
            return False
    
    async def _execute_step(self, saga: Saga, step: SagaStep) -> bool:
        """एक step को execute करता है"""
        logger.info(f"⏳ Executing step: {step.name}")
        
        step.status = SagaStepStatus.PENDING
        step.started_at = datetime.now()
        
        try:
            # Command में context variables को replace करते हैं
            command = self._resolve_command_params(step.execute_command, saga.context)
            
            # Service call करते हैं
            result = await self._call_service(command)
            
            # Result को context में store करते हैं
            if step.step_id == "CREATE_ORDER":
                saga.context["order_id"] = result
            elif step.step_id == "PROCESS_PAYMENT":
                saga.context["transaction_id"] = result
            elif step.step_id == "CREATE_SHIPMENT":
                saga.context["shipment_id"] = result
            
            step.status = SagaStepStatus.COMPLETED
            step.completed_at = datetime.now()
            logger.info(f"✅ Step completed: {step.name}")
            return True
            
        except Exception as e:
            step.status = SagaStepStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.now()
            logger.error(f"❌ Step failed: {step.name} - {str(e)}")
            return False
    
    async def _compensate_saga(self, saga: Saga, failed_step: SagaStep = None):
        """Saga का compensation करता है"""
        logger.info(f"🔄 Starting saga compensation: {saga.saga_id}")
        
        saga.status = SagaStatus.COMPENSATING
        
        # Failed step के पहले के सभी completed steps को compensate करते हैं
        steps_to_compensate = []
        for step in saga.steps:
            if step == failed_step:
                break
            if step.status == SagaStepStatus.COMPLETED:
                steps_to_compensate.append(step)
        
        # Reverse order में compensation करते हैं
        for step in reversed(steps_to_compensate):
            await self._compensate_step(saga, step)
        
        saga.status = SagaStatus.COMPENSATED
        saga.updated_at = datetime.now()
        logger.info(f"🔄 Saga compensation completed: {saga.saga_id}")
    
    async def _compensate_step(self, saga: Saga, step: SagaStep):
        """एक step का compensation करता है"""
        if not step.compensate_command:
            logger.info(f"⚠️  No compensation defined for step: {step.name}")
            return
        
        logger.info(f"🔄 Compensating step: {step.name}")
        
        try:
            command = self._resolve_command_params(step.compensate_command, saga.context)
            await self._call_service(command)
            
            step.status = SagaStepStatus.COMPENSATED
            logger.info(f"✅ Step compensated: {step.name}")
            
        except Exception as e:
            logger.error(f"❌ Step compensation failed: {step.name} - {str(e)}")
    
    def _resolve_command_params(self, command: Dict, context: Dict) -> Dict:
        """Command parameters में context variables को resolve करता है"""
        resolved_command = json.loads(json.dumps(command))
        
        def replace_placeholders(obj):
            if isinstance(obj, str) and obj.startswith("{") and obj.endswith("}"):
                key = obj[1:-1]
                return context.get(key, obj)
            elif isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            return obj
        
        return replace_placeholders(resolved_command)
    
    async def _call_service(self, command: Dict) -> Any:
        """Service को call करता है"""
        service_name = command["service"]
        method_name = command["method"]
        params = command["params"]
        
        # Service को map करते हैं
        service_map = {
            "order": self.order_service,
            "inventory": self.inventory_service,
            "payment": self.payment_service,
            "delivery": self.delivery_service
        }
        
        service = service_map.get(service_name)
        if not service:
            raise ValueError(f"Service {service_name} नहीं मिली")
        
        # Special handling for inventory operations
        if service_name == "inventory":
            if method_name == "reserve_items":
                items = params["items"]
                order_id = params["order_id"]
                for item in items:
                    await service.reserve_item(
                        item["product_id"], 
                        item["quantity"], 
                        order_id
                    )
                return True
            elif method_name == "release_reservations":
                items = params["items"]
                order_id = params["order_id"]
                for item in items:
                    await service.release_reservation(
                        item["product_id"], 
                        item["quantity"], 
                        order_id
                    )
                return True
        
        # Normal method call करते हैं
        method = getattr(service, method_name)
        return await method(**params)
    
    def get_saga_status(self, saga_id: str) -> Dict:
        """Saga का current status return करता है"""
        saga = self.sagas.get(saga_id)
        if not saga:
            return {"error": "Saga नहीं मिला"}
        
        return {
            "saga_id": saga.saga_id,
            "name": saga.name,
            "status": saga.status.value,
            "context": saga.context,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "error_message": step.error_message
                }
                for step in saga.steps
            ],
            "created_at": saga.created_at.isoformat(),
            "updated_at": saga.updated_at.isoformat()
        }

# Demo और Testing
async def demo_flipkart_order_saga():
    """Flipkart order processing का demo"""
    print("🛒 Flipkart Order Saga Pattern Demo शुरू कर रहे हैं...")
    
    coordinator = SagaCoordinator()
    
    # Sample order data
    items = [
        {"product_id": "MOBILE_001", "name": "iPhone 15", "quantity": 1, "price": 79900.0},
        {"product_id": "BOOK_003", "name": "Python Programming", "quantity": 2, "price": 599.0}
    ]
    
    user_id = "USER_123"
    delivery_address = "Flat 201, Akshaya Nagar, Bengaluru - 560037"
    
    print(f"\n📱 Order Details:")
    print(f"User: {user_id}")
    print(f"Items: {len(items)} items")
    for item in items:
        print(f"  - {item['name']}: {item['quantity']} x ₹{item['price']}")
    print(f"Delivery Address: {delivery_address}")
    print(f"Total Amount: ₹{sum(item['price'] * item['quantity'] for item in items)}")
    
    # Saga create करते हैं
    saga = coordinator.create_flipkart_order_saga(user_id, items, delivery_address)
    print(f"\n🚀 Saga created: {saga.saga_id}")
    
    # Progress monitor करने के लिए
    async def monitor_progress():
        while True:
            status = coordinator.get_saga_status(saga.saga_id)
            print(f"\n📊 Saga Status: {status['status']}")
            
            for step in status['steps']:
                status_emoji = {
                    "PENDING": "⏳",
                    "COMPLETED": "✅", 
                    "FAILED": "❌",
                    "COMPENSATED": "🔄"
                }.get(step['status'], "❓")
                
                print(f"  {status_emoji} {step['name']}: {step['status']}")
                if step.get('error_message'):
                    print(f"    Error: {step['error_message']}")
            
            if status['status'] in ['COMPLETED', 'FAILED', 'COMPENSATED']:
                break
            
            await asyncio.sleep(2)
    
    # Saga execute करते हैं और monitor करते हैं
    print(f"\n🏁 Saga execution शुरू कर रहे हैं...")
    
    # Monitor task start करते हैं
    monitor_task = asyncio.create_task(monitor_progress())
    
    # Saga execute करते हैं
    success = await coordinator.execute_saga(saga.saga_id)
    
    # Monitor task को complete करते हैं
    await monitor_task
    
    # Final result
    if success:
        print(f"\n🎉 Order successfully processed!")
        print(f"Order ID: {saga.context.get('order_id')}")
        print(f"Transaction ID: {saga.context.get('transaction_id')}")
        print(f"Shipment ID: {saga.context.get('shipment_id')}")
    else:
        print(f"\n💔 Order processing failed but compensation completed")
    
    return saga

async def demo_saga_failure_scenario():
    """Failure scenario का demo"""
    print("\n" + "="*60)
    print("🚨 Failure Scenario Demo - Payment Failed")
    print("="*60)
    
    coordinator = SagaCoordinator()
    
    # Payment fail करने के लिए high amount order
    items = [
        {"product_id": "LAPTOP_002", "name": "MacBook Pro", "quantity": 2, "price": 150000.0}  # Total: ₹3,00,000
    ]
    
    user_id = "USER_456"  # इस user के पास केवल ₹25,000 है
    delivery_address = "Office 5A, Cyber City, Gurgaon - 122001"
    
    print(f"\n💰 Order Amount: ₹{sum(item['price'] * item['quantity'] for item in items)}")
    print(f"💳 User Balance: ₹{coordinator.payment_service.user_balances[user_id]}")
    print("🔮 Expected: Payment will fail due to insufficient balance")
    
    # Saga create और execute करते हैं
    saga = coordinator.create_flipkart_order_saga(user_id, items, delivery_address)
    success = await coordinator.execute_saga(saga.saga_id)
    
    # Final status check करते हैं
    status = coordinator.get_saga_status(saga.saga_id)
    print(f"\n📋 Final Saga Status: {status['status']}")
    
    print(f"\n🔍 Step-by-step breakdown:")
    for step in status['steps']:
        print(f"  - {step['name']}: {step['status']}")
        if step.get('error_message'):
            print(f"    ⚠️ Error: {step['error_message']}")
    
    print(f"\n✅ Compensation successful - all allocated resources released!")

if __name__ == "__main__":
    import asyncio
    
    print("Saga Pattern Coordinator Demo")
    print("="*50)
    
    # Success scenario
    asyncio.run(demo_flipkart_order_saga())
    
    # Failure scenario  
    asyncio.run(demo_saga_failure_scenario())