#!/usr/bin/env python3
"""
Event Sourcing Implementation for Flipkart-style Order Tracking
Complete order lifecycle through events with replay capability

जैसे Mumbai local train की journey में हर station का record रखा जाता है,
वैसे ही हर order की journey में हर event का record रखते हैं
- Order placed, payment processed, shipped, delivered etc.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import redis
from abc import ABC, abstractmethod

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FlipkartOrderEvents")

class EventType(Enum):
    """Event types in order lifecycle - जैसे train stations"""
    ORDER_PLACED = "order_placed"
    ORDER_VALIDATED = "order_validated"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    INVENTORY_RESERVED = "inventory_reserved"
    INVENTORY_UNAVAILABLE = "inventory_unavailable"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_IN_TRANSIT = "order_in_transit"
    ORDER_OUT_FOR_DELIVERY = "order_out_for_delivery"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REFUNDED = "order_refunded"
    ORDER_RETURNED = "order_returned"

class OrderStatus(Enum):
    """Current order status derived from events"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"

@dataclass
class Event:
    """Base event structure"""
    event_id: str
    aggregate_id: str  # Order ID
    event_type: EventType
    event_data: Dict[str, Any]
    event_version: int
    timestamp: datetime
    user_id: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type.value,
            "event_data": self.event_data,
            "event_version": self.event_version,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        return cls(
            event_id=data["event_id"],
            aggregate_id=data["aggregate_id"],
            event_type=EventType(data["event_type"]),
            event_data=data["event_data"],
            event_version=data["event_version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data.get("user_id", ""),
            correlation_id=data.get("correlation_id", ""),
            causation_id=data.get("causation_id", ""),
            metadata=data.get("metadata", {})
        )

@dataclass
class OrderAggregate:
    """
    Order aggregate state reconstructed from events
    जैसे Mumbai local train की पूरी journey का summary
    """
    order_id: str
    user_id: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    total_amount: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: Dict[str, Any] = field(default_factory=dict)
    payment_method: str = ""
    transaction_id: str = ""
    tracking_id: str = ""
    version: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Event-sourced fields
    events_applied: List[str] = field(default_factory=list)
    payment_attempts: int = 0
    cancellation_reason: str = ""
    delivery_attempts: int = 0
    
    def apply_event(self, event: Event):
        """
        Apply event to aggregate state
        जैसे train journey में नया station arrive करने पर status update
        """
        if event.event_id in self.events_applied:
            logger.warning(f"Event {event.event_id} already applied to order {self.order_id}")
            return
        
        logger.debug(f"Applying event {event.event_type.value} to order {self.order_id}")
        
        # Update version and timestamp
        self.version = event.event_version
        self.updated_at = event.timestamp
        
        # Apply event based on type
        if event.event_type == EventType.ORDER_PLACED:
            self._apply_order_placed(event)
        elif event.event_type == EventType.ORDER_VALIDATED:
            self._apply_order_validated(event)
        elif event.event_type == EventType.PAYMENT_INITIATED:
            self._apply_payment_initiated(event)
        elif event.event_type == EventType.PAYMENT_COMPLETED:
            self._apply_payment_completed(event)
        elif event.event_type == EventType.PAYMENT_FAILED:
            self._apply_payment_failed(event)
        elif event.event_type == EventType.INVENTORY_RESERVED:
            self._apply_inventory_reserved(event)
        elif event.event_type == EventType.ORDER_CONFIRMED:
            self._apply_order_confirmed(event)
        elif event.event_type == EventType.ORDER_SHIPPED:
            self._apply_order_shipped(event)
        elif event.event_type == EventType.ORDER_DELIVERED:
            self._apply_order_delivered(event)
        elif event.event_type == EventType.ORDER_CANCELLED:
            self._apply_order_cancelled(event)
        elif event.event_type == EventType.ORDER_REFUNDED:
            self._apply_order_refunded(event)
        
        # Track applied events
        self.events_applied.append(event.event_id)
        
        logger.info(f"Applied {event.event_type.value} to order {self.order_id} - Status: {self.status.value}")
    
    def _apply_order_placed(self, event: Event):
        """Apply order placed event"""
        data = event.event_data
        self.user_id = data.get("user_id", "")
        self.items = data.get("items", [])
        self.total_amount = data.get("total_amount", 0.0)
        self.shipping_address = data.get("shipping_address", {})
        self.payment_method = data.get("payment_method", "")
        self.status = OrderStatus.PENDING
        self.created_at = event.timestamp
    
    def _apply_order_validated(self, event: Event):
        """Apply order validation event"""
        # Order validation doesn't change status but confirms order is valid
        pass
    
    def _apply_payment_initiated(self, event: Event):
        """Apply payment initiation event"""
        self.payment_attempts += 1
        self.status = OrderStatus.PROCESSING
    
    def _apply_payment_completed(self, event: Event):
        """Apply payment completion event"""
        data = event.event_data
        self.transaction_id = data.get("transaction_id", "")
        # Status will be updated to CONFIRMED by inventory reservation
    
    def _apply_payment_failed(self, event: Event):
        """Apply payment failure event"""
        data = event.event_data
        failure_reason = data.get("failure_reason", "Payment failed")
        if self.payment_attempts >= 3:  # Max retry attempts
            self.status = OrderStatus.CANCELLED
            self.cancellation_reason = f"Payment failed after {self.payment_attempts} attempts: {failure_reason}"
    
    def _apply_inventory_reserved(self, event: Event):
        """Apply inventory reservation event"""
        # If payment is complete and inventory reserved, order is confirmed
        if self.transaction_id:
            self.status = OrderStatus.CONFIRMED
    
    def _apply_order_confirmed(self, event: Event):
        """Apply order confirmation event"""
        self.status = OrderStatus.CONFIRMED
    
    def _apply_order_shipped(self, event: Event):
        """Apply order shipped event"""
        data = event.event_data
        self.tracking_id = data.get("tracking_id", "")
        self.status = OrderStatus.SHIPPED
    
    def _apply_order_delivered(self, event: Event):
        """Apply order delivery event"""
        data = event.event_data
        self.delivery_attempts = data.get("delivery_attempt", 1)
        self.status = OrderStatus.DELIVERED
    
    def _apply_order_cancelled(self, event: Event):
        """Apply order cancellation event"""
        data = event.event_data
        self.cancellation_reason = data.get("reason", "Order cancelled")
        self.status = OrderStatus.CANCELLED
    
    def _apply_order_refunded(self, event: Event):
        """Apply order refund event"""
        self.status = OrderStatus.REFUNDED

class EventStore:
    """
    Event store for persisting and retrieving events
    जैसे Mumbai railway log book में सभी train movements record करते हैं
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.stream_prefix = "order_events"
        
    async def append_event(self, event: Event):
        """
        Append event to event store
        जैसे train journey में नया station entry add करना
        """
        try:
            # Store event in Redis stream
            stream_name = f"{self.stream_prefix}:{event.aggregate_id}"
            event_data = event.to_dict()
            
            # Add to stream with event ID as message ID
            self.redis_client.xadd(
                stream_name,
                event_data,
                id=f"{int(event.timestamp.timestamp() * 1000)}-0"
            )
            
            # Also store in global events stream for querying
            self.redis_client.xadd(
                f"{self.stream_prefix}:all",
                {
                    "aggregate_id": event.aggregate_id,
                    "event_type": event.event_type.value,
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat()
                }
            )
            
            # Store event by ID for direct lookup
            self.redis_client.setex(
                f"event:{event.event_id}",
                86400,  # 24 hours TTL
                json.dumps(event_data)
            )
            
            logger.info(f"Stored event {event.event_type.value} for order {event.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to store event: {str(e)}")
            raise
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """
        Get all events for an aggregate
        जैसे specific train की पूरी journey history निकालना
        """
        try:
            stream_name = f"{self.stream_prefix}:{aggregate_id}"
            
            # Read all events from stream
            events_data = self.redis_client.xrange(stream_name)
            
            events = []
            for event_id, fields in events_data:
                event_dict = {k.decode(): v.decode() if isinstance(v, bytes) else v 
                             for k, v in fields.items()}
                event_dict["event_data"] = json.loads(event_dict["event_data"])
                event_dict["metadata"] = json.loads(event_dict.get("metadata", "{}"))
                
                event = Event.from_dict(event_dict)
                
                if event.event_version >= from_version:
                    events.append(event)
            
            return sorted(events, key=lambda e: e.event_version)
            
        except Exception as e:
            logger.error(f"Failed to retrieve events for {aggregate_id}: {str(e)}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get specific event by ID"""
        try:
            event_data = self.redis_client.get(f"event:{event_id}")
            if event_data:
                event_dict = json.loads(event_data)
                return Event.from_dict(event_dict)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve event {event_id}: {str(e)}")
            return None

class OrderEventService:
    """
    Service for handling order events and state reconstruction
    जैसे Mumbai railway control room जो सभी trains को track करता है
    """
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.snapshots = {}  # In-memory cache for performance
    
    async def handle_command(self, command_type: str, aggregate_id: str, 
                           command_data: Dict[str, Any], user_id: str = "") -> Event:
        """
        Handle command and generate corresponding event
        जैसे train driver का instruction receive करके action लेना
        """
        # Get current aggregate state
        aggregate = await self.get_order_aggregate(aggregate_id)
        
        # Validate command based on current state
        if not self._validate_command(command_type, aggregate, command_data):
            raise ValueError(f"Command {command_type} not valid for order {aggregate_id} in state {aggregate.status.value}")
        
        # Create event based on command
        event = await self._create_event_from_command(
            command_type, aggregate, command_data, user_id
        )
        
        # Store event
        await self.event_store.append_event(event)
        
        # Apply event to aggregate and cache
        aggregate.apply_event(event)
        self.snapshots[aggregate_id] = aggregate
        
        return event
    
    def _validate_command(self, command_type: str, aggregate: OrderAggregate, 
                         command_data: Dict[str, Any]) -> bool:
        """
        Validate if command can be applied to current aggregate state
        जैसे train का next station validation
        """
        current_status = aggregate.status
        
        if command_type == "place_order" and current_status != OrderStatus.PENDING:
            return len(aggregate.events_applied) == 0  # Only for new orders
            
        elif command_type == "initiate_payment" and current_status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return False
            
        elif command_type == "complete_payment" and current_status != OrderStatus.PROCESSING:
            return False
            
        elif command_type == "ship_order" and current_status != OrderStatus.CONFIRMED:
            return False
            
        elif command_type == "deliver_order" and current_status != OrderStatus.SHIPPED:
            return False
            
        elif command_type == "cancel_order" and current_status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]:
            return False
            
        return True
    
    async def _create_event_from_command(self, command_type: str, aggregate: OrderAggregate,
                                       command_data: Dict[str, Any], user_id: str) -> Event:
        """Create event from command"""
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        correlation_id = command_data.get("correlation_id", f"cmd_{uuid.uuid4().hex[:8]}")
        
        # Map commands to event types
        command_to_event = {
            "place_order": EventType.ORDER_PLACED,
            "validate_order": EventType.ORDER_VALIDATED,
            "initiate_payment": EventType.PAYMENT_INITIATED,
            "complete_payment": EventType.PAYMENT_COMPLETED,
            "fail_payment": EventType.PAYMENT_FAILED,
            "reserve_inventory": EventType.INVENTORY_RESERVED,
            "confirm_order": EventType.ORDER_CONFIRMED,
            "ship_order": EventType.ORDER_SHIPPED,
            "deliver_order": EventType.ORDER_DELIVERED,
            "cancel_order": EventType.ORDER_CANCELLED,
            "refund_order": EventType.ORDER_REFUNDED
        }
        
        event_type = command_to_event.get(command_type)
        if not event_type:
            raise ValueError(f"Unknown command type: {command_type}")
        
        # Enhance event data based on command type
        event_data = command_data.copy()
        if command_type == "place_order":
            event_data.update({
                "order_placed_at": datetime.now().isoformat(),
                "source": "flipkart_app",
                "region": "mumbai"
            })
        elif command_type == "ship_order":
            event_data.update({
                "shipped_at": datetime.now().isoformat(),
                "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat(),
                "carrier": "mumbai_delivery_partners"
            })
        
        return Event(
            event_id=event_id,
            aggregate_id=aggregate.order_id,
            event_type=event_type,
            event_data=event_data,
            event_version=aggregate.version + 1,
            timestamp=datetime.now(),
            user_id=user_id,
            correlation_id=correlation_id,
            metadata={
                "command_type": command_type,
                "ip_address": "mumbai_datacenter_ip",
                "user_agent": "flipkart_mobile_app"
            }
        )
    
    async def get_order_aggregate(self, order_id: str) -> OrderAggregate:
        """
        Get order aggregate by replaying all events
        जैसे train की पूरी journey reconstruct करना logbook से
        """
        # Check cache first
        if order_id in self.snapshots:
            cached_aggregate = self.snapshots[order_id]
            
            # Get new events since last snapshot
            new_events = await self.event_store.get_events(order_id, cached_aggregate.version + 1)
            
            if new_events:
                for event in new_events:
                    cached_aggregate.apply_event(event)
                
            return cached_aggregate
        
        # Replay from event store
        events = await self.event_store.get_events(order_id)
        
        if not events:
            # New order
            aggregate = OrderAggregate(order_id=order_id, user_id="")
        else:
            # Reconstruct from events
            first_event = events[0]
            aggregate = OrderAggregate(
                order_id=order_id,
                user_id=first_event.event_data.get("user_id", "")
            )
            
            # Apply all events
            for event in events:
                aggregate.apply_event(event)
        
        # Cache the aggregate
        self.snapshots[order_id] = aggregate
        
        return aggregate
    
    async def get_order_history(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Get complete order history with all events
        जैसे train journey की detailed timeline
        """
        events = await self.event_store.get_events(order_id)
        
        history = []
        for event in events:
            history.append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "description": self._get_event_description(event),
                "details": event.event_data,
                "user_id": event.user_id
            })
        
        return history
    
    def _get_event_description(self, event: Event) -> str:
        """Get human-readable event description"""
        descriptions = {
            EventType.ORDER_PLACED: "आपका order successfully place हो गया है",
            EventType.ORDER_VALIDATED: "Order validation completed - सभी details correct हैं",
            EventType.PAYMENT_INITIATED: "Payment processing शुरू हो गया है",
            EventType.PAYMENT_COMPLETED: "Payment successful - ₹{amount} charged",
            EventType.PAYMENT_FAILED: "Payment failed - कृपया फिर से try करें",
            EventType.INVENTORY_RESERVED: "Items reserved - आपके लिए products hold किए गए हैं",
            EventType.ORDER_CONFIRMED: "Order confirmed - अब packing शुरू होगा",
            EventType.ORDER_SHIPPED: "Order shipped - Tracking ID: {tracking_id}",
            EventType.ORDER_DELIVERED: "Order delivered successfully - Mumbai Dabbawalas style!",
            EventType.ORDER_CANCELLED: "Order cancelled - Refund process शुरू कर दिया गया है",
            EventType.ORDER_REFUNDED: "Refund completed - Amount credited to your account"
        }
        
        template = descriptions.get(event.event_type, "Order status updated")
        
        # Format with event data
        try:
            return template.format(**event.event_data)
        except (KeyError, ValueError):
            return template
    
    async def get_orders_by_status(self, status: OrderStatus) -> List[str]:
        """Get all order IDs with specific status"""
        # In production, this would use a projection/read model
        # For demo, we'll scan active orders
        matching_orders = []
        
        for order_id, aggregate in self.snapshots.items():
            if aggregate.status == status:
                matching_orders.append(order_id)
        
        return matching_orders

async def demo_flipkart_order_events():
    """
    Demonstrate Flipkart order event sourcing system
    Mumbai style order journey के साथ complete event history
    """
    print("\n=== Flipkart Order Event Sourcing Demo ===")
    print("Mumbai-style order tracking with complete event history!")
    
    # Initialize components
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    event_store = EventStore(redis_client)
    order_service = OrderEventService(event_store)
    
    # Demo order
    order_id = f"FLIP_ORDER_MUM_{uuid.uuid4().hex[:8].upper()}"
    user_id = "user_mumbai_123"
    
    print(f"\n--- Order Journey for {order_id} ---")
    
    # Step 1: Place Order
    print("\n1. Placing Order (जैसे Mumbai में online shopping)")
    order_data = {
        "user_id": user_id,
        "items": [
            {"product_id": "mobile_001", "name": "OnePlus 12", "price": 65999, "quantity": 1},
            {"product_id": "case_001", "name": "Phone Case", "price": 1299, "quantity": 1}
        ],
        "total_amount": 67298,
        "shipping_address": {
            "name": "Raj Sharma",
            "address": "Flat 3B, Dadar East, Mumbai 400014",
            "phone": "+91-9876543210"
        },
        "payment_method": "UPI"
    }
    
    event1 = await order_service.handle_command("place_order", order_id, order_data, user_id)
    print(f"✅ Order Placed - Event ID: {event1.event_id}")
    
    # Step 2: Validate Order
    await asyncio.sleep(0.5)
    print("\n2. Validating Order (जैसे Mumbai shop में stock check)")
    event2 = await order_service.handle_command("validate_order", order_id, {
        "validation_result": "success",
        "estimated_delivery": "3-4 days"
    }, "system")
    print(f"✅ Order Validated - Event ID: {event2.event_id}")
    
    # Step 3: Initiate Payment
    await asyncio.sleep(0.3)
    print("\n3. Initiating Payment (जैसे PhonePe/GooglePay में payment)")
    event3 = await order_service.handle_command("initiate_payment", order_id, {
        "payment_method": "UPI",
        "payment_gateway": "razorpay",
        "attempt_number": 1
    }, user_id)
    print(f"✅ Payment Initiated - Event ID: {event3.event_id}")
    
    # Step 4: Complete Payment
    await asyncio.sleep(1.0)  # Payment takes time
    print("\n4. Completing Payment (जैसे UPI success message)")
    event4 = await order_service.handle_command("complete_payment", order_id, {
        "transaction_id": f"TXN_{uuid.uuid4().hex[:12].upper()}",
        "amount": 67298,
        "payment_method": "UPI",
        "bank_reference": f"BNK_{uuid.uuid4().hex[:8].upper()}"
    }, user_id)
    print(f"✅ Payment Completed - Event ID: {event4.event_id}")
    
    # Step 5: Reserve Inventory
    await asyncio.sleep(0.4)
    print("\n5. Reserving Inventory (जैसे Mumbai warehouse में items pick)")
    event5 = await order_service.handle_command("reserve_inventory", order_id, {
        "warehouse_id": "MUM_WH_001",
        "items_reserved": order_data["items"],
        "reservation_id": f"RES_{uuid.uuid4().hex[:8].upper()}"
    }, "system")
    print(f"✅ Inventory Reserved - Event ID: {event5.event_id}")
    
    # Step 6: Confirm Order
    await asyncio.sleep(0.2)
    print("\n6. Confirming Order (जैसे Mumbai में final booking confirmation)")
    event6 = await order_service.handle_command("confirm_order", order_id, {
        "confirmed_by": "auto_system",
        "confirmation_number": f"CONF_{uuid.uuid4().hex[:10].upper()}"
    }, "system")
    print(f"✅ Order Confirmed - Event ID: {event6.event_id}")
    
    # Step 7: Ship Order
    await asyncio.sleep(2.0)  # Packaging takes time
    print("\n7. Shipping Order (जैसे Mumbai Dabbawalas delivery network)")
    event7 = await order_service.handle_command("ship_order", order_id, {
        "tracking_id": f"TRACK_{uuid.uuid4().hex[:12].upper()}",
        "carrier": "Mumbai Express Delivery",
        "estimated_delivery_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "warehouse_location": "Mumbai Distribution Center"
    }, "system")
    print(f"✅ Order Shipped - Event ID: {event7.event_id}")
    
    # Wait and then deliver
    await asyncio.sleep(1.0)
    print("\n8. Delivering Order (जैसे Mumbai में घर तक delivery)")
    event8 = await order_service.handle_command("deliver_order", order_id, {
        "delivered_at": datetime.now().isoformat(),
        "delivery_person": "Ramesh Kumar",
        "delivery_attempt": 1,
        "signature_received": True,
        "delivery_location": "Customer Address - Dadar East"
    }, "delivery_person_001")
    print(f"✅ Order Delivered - Event ID: {event8.event_id}")
    
    # Get current order state
    print(f"\n--- Final Order State ---")
    final_aggregate = await order_service.get_order_aggregate(order_id)
    print(f"Order ID: {final_aggregate.order_id}")
    print(f"Status: {final_aggregate.status.value}")
    print(f"Total Amount: ₹{final_aggregate.total_amount}")
    print(f"Transaction ID: {final_aggregate.transaction_id}")
    print(f"Tracking ID: {final_aggregate.tracking_id}")
    print(f"Events Applied: {len(final_aggregate.events_applied)}")
    print(f"Version: {final_aggregate.version}")
    
    # Show complete order history
    print(f"\n--- Complete Order History ---")
    history = await order_service.get_order_history(order_id)
    
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['timestamp'][:19]} - {entry['event_type']}")
        print(f"   Description: {entry['description']}")
        if entry.get('user_id'):
            print(f"   By: {entry['user_id']}")
    
    # Demonstrate event replay by reconstructing order from scratch
    print(f"\n--- Event Replay Demonstration ---")
    print("Clearing cache and reconstructing order from events...")
    
    # Clear cache
    order_service.snapshots.clear()
    
    # Reconstruct order
    reconstructed_aggregate = await order_service.get_order_aggregate(order_id)
    
    print(f"Reconstructed order status: {reconstructed_aggregate.status.value}")
    print(f"Events replayed: {len(reconstructed_aggregate.events_applied)}")
    print(f"Order total: ₹{reconstructed_aggregate.total_amount}")
    
    # Verify state is identical
    assert final_aggregate.status == reconstructed_aggregate.status
    assert final_aggregate.version == reconstructed_aggregate.version
    print("✅ Event replay successful - Order state perfectly reconstructed!")
    
    print(f"\n--- Demo Summary ---")
    print(f"Successfully demonstrated Flipkart-style event sourcing:")
    print(f"- Complete order lifecycle with {len(history)} events")
    print(f"- Event replay and state reconstruction")
    print(f"- Audit trail और complete history tracking")
    print(f"- Mumbai-style reliable order tracking जैसे Dabbawalas!")

if __name__ == "__main__":
    print("Starting Flipkart Order Event Sourcing Demo...")
    asyncio.run(demo_flipkart_order_events())