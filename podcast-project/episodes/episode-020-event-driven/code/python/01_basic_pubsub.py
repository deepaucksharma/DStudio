#!/usr/bin/env python3
"""
Basic Event Publisher/Subscriber Pattern
उदाहरण: Flipkart के order events को handle करना

Setup:
pip install redis asyncio

Indian Context: Jab Flipkart par order place karta hai, 
multiple services को notification जाना चाहिए:
- Inventory service (stock update)
- Payment service (payment processing)
- Shipping service (delivery planning)
- Customer service (order confirmation)
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import redis
import logging

# Logging setup with Hindi context
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event ka basic structure - har event mein ye fields honge"""
    event_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: str
    source: str
    version: str = "1.0"

class EventBus:
    """
    In-memory event bus - production mein Redis/Kafka use karenge
    Mumbai local train ki tarah - har station par different log utarte/chadhte hain
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_store: List[Event] = []  # Event history ke liye
        
    def subscribe(self, event_type: str, handler: Callable):
        """
        Event type ke liye handler register karna
        Jaise WhatsApp group mein specific topic ke liye notification
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Handler registered for event_type: {event_type}")
    
    async def publish(self, event: Event):
        """
        Event ko sabko broadcast karna
        Railway announcement ki tarah - sabko sunai deta hai
        """
        # Event store mein save karna - debugging ke liye
        self._event_store.append(event)
        
        logger.info(f"Publishing event: {event.event_type} - ID: {event.event_id}")
        
        # Subscribers ko notify karna
        if event.event_type in self._subscribers:
            tasks = []
            for handler in self._subscribers[event.event_type]:
                # Async handler support
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Sync handler ko async wrapper mein run karna
                    tasks.append(asyncio.create_task(
                        asyncio.to_thread(handler, event)
                    ))
            
            # Saare handlers ko parallel execute karna
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Handler {i} failed: {result}")
    
    def get_events(self, event_type: str = None) -> List[Event]:
        """Debug ke liye - kya events aaye hain"""
        if event_type:
            return [e for e in self._event_store if e.event_type == event_type]
        return self._event_store

# Indian e-commerce events
class FlipkartOrderService:
    """Flipkart order processing service"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
    async def place_order(self, customer_id: str, items: List[Dict], total_amount: float):
        """Order place karna"""
        order_id = f"FKT-{uuid.uuid4().hex[:8].upper()}"
        
        # Order placed event create karna
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="order.placed",
            data={
                "order_id": order_id,
                "customer_id": customer_id,
                "items": items,
                "total_amount": total_amount,
                "currency": "INR",
                "delivery_address": "Mumbai, Maharashtra"
            },
            timestamp=datetime.now().isoformat(),
            source="flipkart.order.service"
        )
        
        await self.event_bus.publish(event)
        return order_id

# Event handlers - different services
class InventoryService:
    """Stock management service"""
    
    def __init__(self, name: str = "Inventory Service"):
        self.name = name
    
    async def handle_order_placed(self, event: Event):
        """Order placement par stock update karna"""
        order_data = event.data
        logger.info(f"🏪 {self.name}: Stock updating for order {order_data['order_id']}")
        
        # Stock check aur update simulation
        for item in order_data['items']:
            logger.info(f"   📦 Item: {item['name']}, Quantity: {item['quantity']}")
            # Real implementation mein database update hoga
            await asyncio.sleep(0.1)  # Database call simulation
        
        logger.info(f"✅ Stock updated for order {order_data['order_id']}")

class PaymentService:
    """Payment processing service"""
    
    def __init__(self):
        self.name = "Payment Service"
    
    async def handle_order_placed(self, event: Event):
        """Payment processing trigger karna"""
        order_data = event.data
        logger.info(f"💳 {self.name}: Processing payment for order {order_data['order_id']}")
        logger.info(f"   💰 Amount: ₹{order_data['total_amount']}")
        
        # UPI/Card processing simulation
        await asyncio.sleep(0.5)  # Payment gateway call
        
        # Payment success event generate karna
        payment_event = Event(
            event_id=str(uuid.uuid4()),
            event_type="payment.completed",
            data={
                "order_id": order_data['order_id'],
                "amount": order_data['total_amount'],
                "payment_method": "UPI",
                "transaction_id": f"TXN{uuid.uuid4().hex[:8].upper()}"
            },
            timestamp=datetime.now().isoformat(),
            source="payment.service"
        )
        
        # Event bus se payment completion notify karna
        # Production mein yahan proper event bus injection hogi
        logger.info(f"✅ Payment completed for order {order_data['order_id']}")

class ShippingService:
    """Delivery planning service"""
    
    def __init__(self):
        self.name = "Shipping Service"
    
    def handle_order_placed(self, event: Event):
        """Sync handler example - delivery planning"""
        order_data = event.data
        logger.info(f"🚛 {self.name}: Planning delivery for order {order_data['order_id']}")
        logger.info(f"   📍 Address: {order_data['delivery_address']}")
        
        # Delivery route optimization
        time.sleep(0.2)  # Route calculation
        
        estimated_delivery = "2 days"  # Mumbai ke liye typical
        logger.info(f"✅ Delivery planned: {estimated_delivery}")

class CustomerNotificationService:
    """Customer ko notifications send karna"""
    
    def __init__(self):
        self.name = "Customer Notification"
    
    async def handle_order_placed(self, event: Event):
        """Customer ko order confirmation send karna"""
        order_data = event.data
        logger.info(f"📱 {self.name}: Sending confirmation to customer {order_data['customer_id']}")
        
        # SMS/Email/Push notification
        await asyncio.sleep(0.1)
        
        logger.info(f"✅ Order confirmation sent for {order_data['order_id']}")

async def main():
    """Main demo function"""
    print("🛒 Flipkart Event-Driven Order Processing Demo")
    print("=" * 50)
    
    # Event bus initialize karna
    event_bus = EventBus()
    
    # Services initialize karna
    order_service = FlipkartOrderService(event_bus)
    inventory_service = InventoryService()
    payment_service = PaymentService()
    shipping_service = ShippingService()
    notification_service = CustomerNotificationService()
    
    # Event handlers register karna
    event_bus.subscribe("order.placed", inventory_service.handle_order_placed)
    event_bus.subscribe("order.placed", payment_service.handle_order_placed)
    event_bus.subscribe("order.placed", shipping_service.handle_order_placed)
    event_bus.subscribe("order.placed", notification_service.handle_order_placed)
    
    # Sample order data
    items = [
        {"name": "iPhone 15", "quantity": 1, "price": 80000},
        {"name": "AirPods Pro", "quantity": 1, "price": 25000}
    ]
    
    # Order place karna
    order_id = await order_service.place_order(
        customer_id="CUST123",
        items=items,
        total_amount=105000
    )
    
    print(f"\n📋 Order placed successfully: {order_id}")
    
    # Thoda wait karna processing complete hone ke liye
    await asyncio.sleep(1)
    
    # Event history dekhna
    print(f"\n📊 Total events processed: {len(event_bus.get_events())}")
    order_events = event_bus.get_events("order.placed")
    print(f"🛍️ Order events: {len(order_events)}")

if __name__ == "__main__":
    asyncio.run(main())