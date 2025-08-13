#!/usr/bin/env python3
"""
Choreography Saga Pattern Implementation
=======================================

Production-ready choreography-based saga implementation for distributed transactions.
In choreography pattern, each service knows what to do when it receives an event.

Mumbai Context: यह Mumbai local train system जैसा है! हर station independently
अपना काम करता है - signals, announcements, platform clearing. कोई central
controller नहीं है, but सब coordinated होता है through events!

Real-world usage:
- E-commerce order processing
- Payment systems
- Microservices orchestration
- Event-driven architectures
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from abc import ABC, abstractmethod
import queue
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Saga event types"""
    # Order events
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_VALIDATED = "ORDER_VALIDATED"
    ORDER_VALIDATION_FAILED = "ORDER_VALIDATION_FAILED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_COMPLETED = "ORDER_COMPLETED"
    
    # Payment events
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REFUNDED = "PAYMENT_REFUNDED"
    
    # Inventory events
    INVENTORY_RESERVED = "INVENTORY_RESERVED"
    INVENTORY_RESERVATION_FAILED = "INVENTORY_RESERVATION_FAILED"
    INVENTORY_RELEASED = "INVENTORY_RELEASED"
    INVENTORY_CONFIRMED = "INVENTORY_CONFIRMED"
    
    # Shipping events
    SHIPPING_INITIATED = "SHIPPING_INITIATED"
    SHIPPING_COMPLETED = "SHIPPING_COMPLETED"
    SHIPPING_FAILED = "SHIPPING_FAILED"
    SHIPPING_CANCELLED = "SHIPPING_CANCELLED"
    
    # Notification events
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    
    # Compensation events
    COMPENSATION_STARTED = "COMPENSATION_STARTED"
    COMPENSATION_COMPLETED = "COMPENSATION_COMPLETED"

@dataclass
class SagaEvent:
    """Saga event message"""
    event_id: str
    event_type: EventType
    saga_id: str
    timestamp: float
    source_service: str
    data: Dict[str, Any]
    correlation_id: str = ""
    retry_count: int = 0
    max_retries: int = 3

class EventBus:
    """
    Simple event bus for choreography saga
    
    Mumbai Metaphor: यह Mumbai के public announcement system जैसा है!
    हर station पर announcements होते हैं और सभी services सुनती हैं
    जो उनके relevant हैं.
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[SagaEvent] = []
        self.lock = threading.RLock()
    
    def subscribe(self, event_type: EventType, handler: Callable[[SagaEvent], None]):
        """Subscribe to an event type"""
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)
    
    def publish(self, event: SagaEvent):
        """Publish an event to all subscribers"""
        with self.lock:
            self.event_history.append(event)
            
            logger.info(f"📢 Publishing event: {event.event_type.value} for saga {event.saga_id}")
            
            # Notify all subscribers
            subscribers = self.subscribers.get(event.event_type, [])
            for handler in subscribers:
                try:
                    # Handle asynchronously to avoid blocking
                    threading.Thread(target=handler, args=(event,)).start()
                except Exception as e:
                    logger.error(f"❌ Error in event handler: {e}")
    
    def get_saga_events(self, saga_id: str) -> List[SagaEvent]:
        """Get all events for a saga"""
        return [event for event in self.event_history if event.saga_id == saga_id]

class SagaService(ABC):
    """Base class for saga services"""
    
    def __init__(self, service_name: str, event_bus: EventBus):
        self.service_name = service_name
        self.event_bus = event_bus
        self.state_db_path = f"{service_name.lower()}_state.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize service state database"""
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saga_state (
                    saga_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_state(self, saga_id: str, state: str, data: Dict[str, Any]):
        """Save saga state for this service"""
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO saga_state (saga_id, state, data)
                VALUES (?, ?, ?)
            """, (saga_id, state, json.dumps(data)))
    
    def get_state(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get saga state for this service"""
        with sqlite3.connect(self.state_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state, data FROM saga_state WHERE saga_id = ?", (saga_id,))
            result = cursor.fetchone()
            
            if result:
                state, data_json = result
                return {
                    'state': state,
                    'data': json.loads(data_json) if data_json else {}
                }
        return None
    
    def publish_event(self, event_type: EventType, saga_id: str, data: Dict[str, Any]):
        """Publish an event"""
        event = SagaEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            saga_id=saga_id,
            timestamp=time.time(),
            source_service=self.service_name,
            data=data
        )
        
        self.event_bus.publish(event)
    
    @abstractmethod
    def handle_event(self, event: SagaEvent):
        """Handle incoming events - implemented by each service"""
        pass

class OrderService(SagaService):
    """
    Order Service in choreography saga
    
    Mumbai Story: यह Zomato का order processing जैसा है! Customer order place
    करता है, service validate करती है, और बाकी services को events भेजती है.
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__("OrderService", event_bus)
        
        # Sample orders state
        self.orders: Dict[str, Dict[str, Any]] = {}
        
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.PAYMENT_COMPLETED, self.handle_event)
        self.event_bus.subscribe(EventType.PAYMENT_FAILED, self.handle_event)
        self.event_bus.subscribe(EventType.INVENTORY_RESERVATION_FAILED, self.handle_event)
        self.event_bus.subscribe(EventType.SHIPPING_COMPLETED, self.handle_event)
        self.event_bus.subscribe(EventType.COMPENSATION_COMPLETED, self.handle_event)
        
        logger.info("🛍️ OrderService initialized")
    
    def create_order(self, customer_id: str, items: List[Dict[str, Any]], 
                     total_amount: float) -> str:
        """Create a new order and start the saga"""
        saga_id = f"SAGA_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        order_data = {
            'customer_id': customer_id,
            'items': items,
            'total_amount': total_amount,
            'status': 'CREATED',
            'created_at': time.time()
        }
        
        # Store order
        self.orders[saga_id] = order_data
        self.save_state(saga_id, 'CREATED', order_data)
        
        # Validate order
        if self._validate_order(order_data):
            # Order is valid, publish event to continue saga
            self.publish_event(
                EventType.ORDER_VALIDATED,
                saga_id,
                {
                    'order_id': saga_id,
                    'customer_id': customer_id,
                    'items': items,
                    'total_amount': total_amount
                }
            )
            
            logger.info(f"✅ Order validated and saga started: {saga_id}")
        else:
            # Order validation failed
            self.orders[saga_id]['status'] = 'VALIDATION_FAILED'
            self.save_state(saga_id, 'VALIDATION_FAILED', order_data)
            
            self.publish_event(
                EventType.ORDER_VALIDATION_FAILED,
                saga_id,
                {'order_id': saga_id, 'reason': 'Invalid order data'}
            )
            
            logger.warning(f"❌ Order validation failed: {saga_id}")
        
        return saga_id
    
    def handle_event(self, event: SagaEvent):
        """Handle events related to orders"""
        saga_id = event.saga_id
        
        if saga_id not in self.orders:
            return
        
        if event.event_type == EventType.PAYMENT_COMPLETED:
            # Payment successful, wait for inventory and shipping
            self.orders[saga_id]['status'] = 'PAYMENT_COMPLETED'
            self.save_state(saga_id, 'PAYMENT_COMPLETED', self.orders[saga_id])
            logger.info(f"💰 Payment completed for order: {saga_id}")
        
        elif event.event_type == EventType.PAYMENT_FAILED:
            # Payment failed, cancel order
            self.orders[saga_id]['status'] = 'CANCELLED'
            self.save_state(saga_id, 'CANCELLED', self.orders[saga_id])
            
            self.publish_event(
                EventType.ORDER_CANCELLED,
                saga_id,
                {'order_id': saga_id, 'reason': 'Payment failed'}
            )
            
            logger.warning(f"❌ Order cancelled due to payment failure: {saga_id}")
        
        elif event.event_type == EventType.INVENTORY_RESERVATION_FAILED:
            # Inventory reservation failed, initiate compensation
            self.orders[saga_id]['status'] = 'CANCELLED'
            self.save_state(saga_id, 'CANCELLED', self.orders[saga_id])
            
            # Start compensation saga
            self.publish_event(
                EventType.COMPENSATION_STARTED,
                saga_id,
                {'order_id': saga_id, 'reason': 'Inventory not available'}
            )
            
            logger.warning(f"❌ Order cancelled due to inventory issue: {saga_id}")
        
        elif event.event_type == EventType.SHIPPING_COMPLETED:
            # Everything successful, complete order
            self.orders[saga_id]['status'] = 'COMPLETED'
            self.save_state(saga_id, 'COMPLETED', self.orders[saga_id])
            
            self.publish_event(
                EventType.ORDER_COMPLETED,
                saga_id,
                {'order_id': saga_id}
            )
            
            logger.info(f"🎉 Order completed successfully: {saga_id}")
    
    def _validate_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate order data"""
        # Basic validation
        if not order_data.get('customer_id'):
            return False
        
        items = order_data.get('items', [])
        if not items:
            return False
        
        total_amount = order_data.get('total_amount', 0)
        if total_amount <= 0:
            return False
        
        # Validate item prices (simplified)
        calculated_total = sum(item.get('price', 0) * item.get('quantity', 0) for item in items)
        if abs(calculated_total - total_amount) > 0.01:  # Allow small floating point differences
            return False
        
        return True
    
    def get_order_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get order status"""
        return self.orders.get(saga_id)

class PaymentService(SagaService):
    """
    Payment Service in choreography saga
    
    Mumbai Story: यह PayU/Razorpay जैसी payment gateway service है!
    Order validate होने पर payment process करती है.
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__("PaymentService", event_bus)
        
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.ORDER_VALIDATED, self.handle_event)
        self.event_bus.subscribe(EventType.COMPENSATION_STARTED, self.handle_event)
        
        # Mock payment state
        self.payments: Dict[str, Dict[str, Any]] = {}
        
        logger.info("💳 PaymentService initialized")
    
    def handle_event(self, event: SagaEvent):
        """Handle payment-related events"""
        saga_id = event.saga_id
        
        if event.event_type == EventType.ORDER_VALIDATED:
            # Process payment
            self._process_payment(saga_id, event.data)
        
        elif event.event_type == EventType.COMPENSATION_STARTED:
            # Refund payment if it was completed
            self._refund_payment(saga_id)
    
    def _process_payment(self, saga_id: str, order_data: Dict[str, Any]):
        """Process payment for order"""
        customer_id = order_data.get('customer_id')
        total_amount = order_data.get('total_amount', 0)
        
        # Simulate payment processing delay
        time.sleep(0.1)
        
        payment_data = {
            'customer_id': customer_id,
            'amount': total_amount,
            'status': 'PROCESSING',
            'processed_at': time.time()
        }
        
        self.payments[saga_id] = payment_data
        self.save_state(saga_id, 'PROCESSING', payment_data)
        
        # Simulate payment success/failure (90% success rate)
        payment_successful = (hash(saga_id) % 10) < 9
        
        if payment_successful:
            # Payment successful
            payment_data['status'] = 'COMPLETED'
            payment_data['transaction_id'] = f"PAY_{int(time.time() * 1000)}"
            
            self.save_state(saga_id, 'COMPLETED', payment_data)
            
            self.publish_event(
                EventType.PAYMENT_COMPLETED,
                saga_id,
                {
                    'payment_id': payment_data['transaction_id'],
                    'amount': total_amount,
                    'customer_id': customer_id
                }
            )
            
            logger.info(f"💰 Payment completed: {saga_id} - ₹{total_amount:.2f}")
        else:
            # Payment failed
            payment_data['status'] = 'FAILED'
            payment_data['failure_reason'] = 'Insufficient balance'
            
            self.save_state(saga_id, 'FAILED', payment_data)
            
            self.publish_event(
                EventType.PAYMENT_FAILED,
                saga_id,
                {
                    'reason': payment_data['failure_reason'],
                    'customer_id': customer_id
                }
            )
            
            logger.warning(f"❌ Payment failed: {saga_id}")
    
    def _refund_payment(self, saga_id: str):
        """Refund payment as compensation"""
        if saga_id not in self.payments:
            return
        
        payment_data = self.payments[saga_id]
        
        if payment_data['status'] == 'COMPLETED':
            # Process refund
            payment_data['status'] = 'REFUNDED'
            payment_data['refunded_at'] = time.time()
            
            self.save_state(saga_id, 'REFUNDED', payment_data)
            
            self.publish_event(
                EventType.PAYMENT_REFUNDED,
                saga_id,
                {
                    'refund_amount': payment_data['amount'],
                    'customer_id': payment_data['customer_id']
                }
            )
            
            logger.info(f"💸 Payment refunded: {saga_id} - ₹{payment_data['amount']:.2f}")

class InventoryService(SagaService):
    """
    Inventory Service in choreography saga
    
    Mumbai Story: यह Flipkart का inventory management system जैसा है!
    Payment complete होने पर items reserve करता है.
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__("InventoryService", event_bus)
        
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.PAYMENT_COMPLETED, self.handle_event)
        self.event_bus.subscribe(EventType.SHIPPING_COMPLETED, self.handle_event)
        self.event_bus.subscribe(EventType.COMPENSATION_STARTED, self.handle_event)
        
        # Mock inventory
        self.inventory = {
            'smartphone_xyz': 50,
            'laptop_abc': 25,
            'headphones_def': 100,
            'watch_ghi': 30,
            'tablet_jkl': 15
        }
        
        self.reservations: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("📦 InventoryService initialized")
    
    def handle_event(self, event: SagaEvent):
        """Handle inventory-related events"""
        saga_id = event.saga_id
        
        if event.event_type == EventType.PAYMENT_COMPLETED:
            # Reserve inventory
            self._reserve_inventory(saga_id, event)
        
        elif event.event_type == EventType.SHIPPING_COMPLETED:
            # Confirm inventory reservation (final step)
            self._confirm_inventory(saga_id)
        
        elif event.event_type == EventType.COMPENSATION_STARTED:
            # Release reserved inventory
            self._release_inventory(saga_id)
    
    def _reserve_inventory(self, saga_id: str, event: SagaEvent):
        """Reserve inventory items"""
        # Get order data from event history
        order_events = [e for e in self.event_bus.get_saga_events(saga_id) 
                       if e.event_type == EventType.ORDER_VALIDATED]
        
        if not order_events:
            logger.error(f"❌ No order data found for inventory reservation: {saga_id}")
            return
        
        items = order_events[0].data.get('items', [])
        reservations = []
        
        # Check and reserve each item
        for item in items:
            item_id = item.get('item_id')
            quantity = item.get('quantity', 0)
            
            if item_id in self.inventory and self.inventory[item_id] >= quantity:
                # Reserve the item
                self.inventory[item_id] -= quantity
                reservations.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'reserved_at': time.time()
                })
            else:
                # Not enough inventory - release already reserved items
                self._release_reservations(reservations)
                
                self.publish_event(
                    EventType.INVENTORY_RESERVATION_FAILED,
                    saga_id,
                    {
                        'failed_item': item_id,
                        'requested': quantity,
                        'available': self.inventory.get(item_id, 0)
                    }
                )
                
                logger.warning(f"❌ Inventory reservation failed: {saga_id} - {item_id}")
                return
        
        # All items reserved successfully
        self.reservations[saga_id] = reservations
        self.save_state(saga_id, 'RESERVED', {'reservations': reservations})
        
        self.publish_event(
            EventType.INVENTORY_RESERVED,
            saga_id,
            {'reserved_items': reservations}
        )
        
        logger.info(f"📦 Inventory reserved: {saga_id} - {len(reservations)} items")
    
    def _confirm_inventory(self, saga_id: str):
        """Confirm inventory reservation (final step)"""
        if saga_id in self.reservations:
            # Inventory is already deducted, just update state
            self.save_state(saga_id, 'CONFIRMED', {'reservations': self.reservations[saga_id]})
            
            self.publish_event(
                EventType.INVENTORY_CONFIRMED,
                saga_id,
                {'confirmed_items': self.reservations[saga_id]}
            )
            
            logger.info(f"✅ Inventory confirmed: {saga_id}")
            
            # Clean up reservations
            del self.reservations[saga_id]
    
    def _release_inventory(self, saga_id: str):
        """Release reserved inventory as compensation"""
        if saga_id in self.reservations:
            self._release_reservations(self.reservations[saga_id])
            del self.reservations[saga_id]
            
            self.save_state(saga_id, 'RELEASED', {})
            
            self.publish_event(
                EventType.INVENTORY_RELEASED,
                saga_id,
                {'released_items': self.reservations.get(saga_id, [])}
            )
            
            logger.info(f"🔄 Inventory released: {saga_id}")
    
    def _release_reservations(self, reservations: List[Dict[str, Any]]):
        """Helper to release inventory reservations"""
        for reservation in reservations:
            item_id = reservation['item_id']
            quantity = reservation['quantity']
            
            if item_id in self.inventory:
                self.inventory[item_id] += quantity
    
    def get_inventory_status(self) -> Dict[str, int]:
        """Get current inventory status"""
        return self.inventory.copy()

class ShippingService(SagaService):
    """
    Shipping Service in choreography saga
    
    Mumbai Story: यह Blue Dart/Delhivery जैसी shipping service है!
    Inventory reserve होने पर shipping initiate करती है.
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__("ShippingService", event_bus)
        
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.INVENTORY_RESERVED, self.handle_event)
        self.event_bus.subscribe(EventType.COMPENSATION_STARTED, self.handle_event)
        
        self.shipments: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🚚 ShippingService initialized")
    
    def handle_event(self, event: SagaEvent):
        """Handle shipping-related events"""
        saga_id = event.saga_id
        
        if event.event_type == EventType.INVENTORY_RESERVED:
            # Initiate shipping
            self._initiate_shipping(saga_id, event)
        
        elif event.event_type == EventType.COMPENSATION_STARTED:
            # Cancel shipping
            self._cancel_shipping(saga_id)
    
    def _initiate_shipping(self, saga_id: str, event: SagaEvent):
        """Initiate shipping process"""
        # Get customer info from order events
        order_events = [e for e in self.event_bus.get_saga_events(saga_id) 
                       if e.event_type == EventType.ORDER_VALIDATED]
        
        if not order_events:
            logger.error(f"❌ No order data found for shipping: {saga_id}")
            return
        
        customer_id = order_events[0].data.get('customer_id')
        reserved_items = event.data.get('reserved_items', [])
        
        # Simulate shipping processing
        time.sleep(0.1)
        
        shipping_data = {
            'customer_id': customer_id,
            'items': reserved_items,
            'status': 'INITIATED',
            'initiated_at': time.time(),
            'tracking_id': f"SHIP_{int(time.time() * 1000)}"
        }
        
        self.shipments[saga_id] = shipping_data
        self.save_state(saga_id, 'INITIATED', shipping_data)
        
        # Simulate shipping success/failure (95% success rate)
        shipping_successful = (hash(saga_id) % 20) < 19
        
        if shipping_successful:
            # Simulate shipping time
            time.sleep(0.2)
            
            shipping_data['status'] = 'COMPLETED'
            shipping_data['completed_at'] = time.time()
            
            self.save_state(saga_id, 'COMPLETED', shipping_data)
            
            self.publish_event(
                EventType.SHIPPING_COMPLETED,
                saga_id,
                {
                    'tracking_id': shipping_data['tracking_id'],
                    'customer_id': customer_id
                }
            )
            
            logger.info(f"🚚 Shipping completed: {saga_id} - {shipping_data['tracking_id']}")
        else:
            shipping_data['status'] = 'FAILED'
            shipping_data['failure_reason'] = 'Address not serviceable'
            
            self.save_state(saga_id, 'FAILED', shipping_data)
            
            # Start compensation
            self.publish_event(
                EventType.COMPENSATION_STARTED,
                saga_id,
                {'reason': 'Shipping failed'}
            )
            
            logger.warning(f"❌ Shipping failed: {saga_id}")
    
    def _cancel_shipping(self, saga_id: str):
        """Cancel shipping as compensation"""
        if saga_id in self.shipments:
            shipment = self.shipments[saga_id]
            
            if shipment['status'] == 'INITIATED':
                shipment['status'] = 'CANCELLED'
                shipment['cancelled_at'] = time.time()
                
                self.save_state(saga_id, 'CANCELLED', shipment)
                
                self.publish_event(
                    EventType.SHIPPING_CANCELLED,
                    saga_id,
                    {'tracking_id': shipment.get('tracking_id')}
                )
                
                logger.info(f"🚫 Shipping cancelled: {saga_id}")

def simulate_zomato_order_choreography():
    """
    Simulate Zomato order processing using choreography saga
    
    Mumbai Scenario: Customer Zomato पर order place करता है और multiple
    services choreography pattern में coordinate करती हैं - order validation,
    payment processing, restaurant preparation, delivery assignment!
    """
    logger.info("🍽️ Starting Zomato Order Choreography Saga simulation...")
    
    # Initialize event bus
    event_bus = EventBus()
    
    # Initialize all services
    order_service = OrderService(event_bus)
    payment_service = PaymentService(event_bus)
    inventory_service = InventoryService(event_bus)
    shipping_service = ShippingService(event_bus)
    
    logger.info("🎭 All services initialized and subscribed to events")
    
    # Simulate multiple concurrent orders
    orders = []
    
    # Sample orders
    sample_orders = [
        {
            'customer_id': 'customer_001',
            'items': [
                {'item_id': 'smartphone_xyz', 'name': 'Smartphone XYZ', 'quantity': 1, 'price': 15000.0},
                {'item_id': 'headphones_def', 'name': 'Wireless Headphones', 'quantity': 1, 'price': 3000.0}
            ],
            'total_amount': 18000.0
        },
        {
            'customer_id': 'customer_002',
            'items': [
                {'item_id': 'laptop_abc', 'name': 'Laptop ABC', 'quantity': 1, 'price': 45000.0}
            ],
            'total_amount': 45000.0
        },
        {
            'customer_id': 'customer_003',
            'items': [
                {'item_id': 'watch_ghi', 'name': 'Smart Watch', 'quantity': 2, 'price': 8000.0},
                {'item_id': 'tablet_jkl', 'name': 'Tablet JKL', 'quantity': 1, 'price': 20000.0}
            ],
            'total_amount': 36000.0
        },
        {
            'customer_id': 'customer_004',
            'items': [
                {'item_id': 'smartphone_xyz', 'name': 'Smartphone XYZ', 'quantity': 50, 'price': 15000.0}  # This will fail
            ],
            'total_amount': 750000.0
        }
    ]
    
    # Create orders with small delays
    for i, order_data in enumerate(sample_orders):
        saga_id = order_service.create_order(
            customer_id=order_data['customer_id'],
            items=order_data['items'],
            total_amount=order_data['total_amount']
        )
        orders.append(saga_id)
        
        logger.info(f"🛍️ Order {i+1} created: {saga_id} for {order_data['customer_id']}")
        time.sleep(0.5)  # Small delay between orders
    
    # Wait for all sagas to complete
    logger.info("⏳ Waiting for all sagas to complete...")
    time.sleep(3)
    
    # Check final results
    logger.info("\n📊 Final Order Status:")
    completed = 0
    cancelled = 0
    
    for saga_id in orders:
        order_status = order_service.get_order_status(saga_id)
        if order_status:
            status = order_status['status']
            customer_id = order_status['customer_id']
            total = order_status['total_amount']
            
            if status == 'COMPLETED':
                completed += 1
                logger.info(f"✅ {saga_id}: COMPLETED - {customer_id} (₹{total:.2f})")
            elif status in ['CANCELLED', 'VALIDATION_FAILED']:
                cancelled += 1
                logger.info(f"❌ {saga_id}: {status} - {customer_id} (₹{total:.2f})")
            else:
                logger.info(f"⏳ {saga_id}: {status} - {customer_id} (₹{total:.2f})")
    
    # Show inventory status
    inventory_status = inventory_service.get_inventory_status()
    logger.info(f"\n📦 Final Inventory Status:")
    for item_id, quantity in inventory_status.items():
        logger.info(f"  {item_id}: {quantity} units")
    
    # Show event summary
    total_events = len(event_bus.event_history)
    event_types = {}
    for event in event_bus.event_history:
        event_type = event.event_type.value
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    logger.info(f"\n📢 Event Summary ({total_events} total events):")
    for event_type, count in sorted(event_types.items()):
        logger.info(f"  {event_type}: {count}")
    
    logger.info(f"\n🎉 Choreography Saga Results:")
    logger.info(f"  Orders processed: {len(orders)}")
    logger.info(f"  Successfully completed: {completed}")
    logger.info(f"  Cancelled/Failed: {cancelled}")
    logger.info(f"  Success rate: {(completed / len(orders)) * 100:.2f}%")

if __name__ == "__main__":
    try:
        simulate_zomato_order_choreography()
        logger.info("\n🎊 Zomato Choreography Saga simulation completed!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()