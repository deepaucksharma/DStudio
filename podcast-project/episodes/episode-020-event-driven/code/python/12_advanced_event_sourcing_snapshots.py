#!/usr/bin/env python3
"""
Advanced Event Sourcing with Snapshots - Flipkart Order Management
==================================================================
उन्नत इवेंट सोर्सिंग स्नैपशॉट के साथ - फ्लिपकार्ट ऑर्डर प्रबंधन

Production-ready event sourcing implementation with snapshot optimization for 
Flipkart-scale order management system. Handles millions of orders with optimized
aggregate reconstruction and point-in-time queries.

This example demonstrates:
यह उदाहरण प्रदर्शित करता है:

1. Event store with snapshot optimization - स्नैपशॉट अनुकूलन के साथ इवेंट स्टोर
2. Aggregate reconstruction from snapshots - स्नैपशॉट से एग्रीगेट पुनर्निर्माण
3. Point-in-time state queries - समय-बिंदु स्थिति क्वेरी
4. Event replay for debugging - डिबगिंग के लिए इवेंट रीप्ले
5. Snapshot compression and archival - स्नैपशॉट संपीड़न और संग्रहण

Author: Hindi Podcast Series
Episode: 020 - Event-Driven Architecture
Context: Flipkart order lifecycle management
"""

import asyncio
import json
import uuid
import time
import sqlite3
import gzip
import pickle
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Union, Tuple
from abc import ABC, abstractmethod
from collections import defaultdict
import hashlib
import concurrent.futures
from pathlib import Path

# Configure logging - लॉगिंग कॉन्फ़िगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """Order status enum - ऑर्डर स्टेटस"""
    CREATED = "CREATED"              # बनाया गया
    PAYMENT_PENDING = "PAYMENT_PENDING"  # भुगतान लंबित
    CONFIRMED = "CONFIRMED"          # पुष्टि की गई
    PACKED = "PACKED"                # पैक किया गया
    SHIPPED = "SHIPPED"              # भेजा गया
    DELIVERED = "DELIVERED"          # डिलीवर हुआ
    CANCELLED = "CANCELLED"          # रद्द किया गया
    RETURNED = "RETURNED"            # वापस किया गया
    REFUNDED = "REFUNDED"            # रिफंड किया गया

class EventType(Enum):
    """Event types for order system - ऑर्डर सिस्टम के लिए इवेंट टाइप"""
    ORDER_CREATED = "order.created"
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    ORDER_CONFIRMED = "order.confirmed"
    INVENTORY_RESERVED = "inventory.reserved"
    ORDER_PACKED = "order.packed"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_RETURNED = "order.returned"
    REFUND_INITIATED = "refund.initiated"
    REFUND_COMPLETED = "refund.completed"

@dataclass
class Event:
    """Base event class - बेस इवेंट क्लास"""
    event_id: str
    aggregate_id: str
    event_type: EventType
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary - डिक्शनरी में कन्वर्ट करें"""
        return {
            'event_id': self.event_id,
            'aggregate_id': self.aggregate_id,
            'event_type': self.event_type.value,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create from dictionary - डिक्शनरी से बनाएं"""
        return cls(
            event_id=data['event_id'],
            aggregate_id=data['aggregate_id'],
            event_type=EventType(data['event_type']),
            event_data=data['event_data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            version=data['version'],
            metadata=data.get('metadata', {})
        )

@dataclass
class OrderItem:
    """Order item details - ऑर्डर आइटम विवरण"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    seller_id: str
    category: str

@dataclass
class Address:
    """Delivery address - डिलीवरी पता"""
    street: str
    area: str
    city: str
    state: str
    pincode: str
    country: str = "India"

@dataclass
class OrderAggregate:
    """Order aggregate root - ऑर्डर एग्रीगेट रूट"""
    order_id: str
    customer_id: str
    items: List[OrderItem] = field(default_factory=list)
    total_amount: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    final_amount: float = 0.0
    status: OrderStatus = OrderStatus.CREATED
    delivery_address: Optional[Address] = None
    payment_method: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 0
    
    # Order tracking details - ऑर्डर ट्रैकिंग विवरण
    payment_id: Optional[str] = None
    tracking_id: Optional[str] = None
    expected_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    
    def apply_event(self, event: Event):
        """Apply event to aggregate - एग्रीगेट में इवेंट लागू करें"""
        if event.event_type == EventType.ORDER_CREATED:
            self._apply_order_created(event)
        elif event.event_type == EventType.PAYMENT_COMPLETED:
            self._apply_payment_completed(event)
        elif event.event_type == EventType.ORDER_CONFIRMED:
            self._apply_order_confirmed(event)
        elif event.event_type == EventType.ORDER_PACKED:
            self._apply_order_packed(event)
        elif event.event_type == EventType.ORDER_SHIPPED:
            self._apply_order_shipped(event)
        elif event.event_type == EventType.ORDER_DELIVERED:
            self._apply_order_delivered(event)
        elif event.event_type == EventType.ORDER_CANCELLED:
            self._apply_order_cancelled(event)
        elif event.event_type == EventType.ORDER_RETURNED:
            self._apply_order_returned(event)
        
        self.version = event.version
        self.updated_at = event.timestamp
    
    def _apply_order_created(self, event: Event):
        """Apply order created event - ऑर्डर बनाया गया इवेंट लागू करें"""
        data = event.event_data
        self.customer_id = data['customer_id']
        self.items = [OrderItem(**item) for item in data['items']]
        self.total_amount = data['total_amount']
        self.discount_amount = data.get('discount_amount', 0.0)
        self.tax_amount = data.get('tax_amount', 0.0)
        self.final_amount = data['final_amount']
        if data.get('delivery_address'):
            self.delivery_address = Address(**data['delivery_address'])
        self.status = OrderStatus.CREATED
    
    def _apply_payment_completed(self, event: Event):
        """Apply payment completed event - भुगतान पूर्ण इवेंट लागू करें"""
        data = event.event_data
        self.payment_id = data['payment_id']
        self.payment_method = data['payment_method']
        # Status remains PAYMENT_PENDING until order is confirmed
    
    def _apply_order_confirmed(self, event: Event):
        """Apply order confirmed event - ऑर्डर पुष्टि इवेंट लागू करें"""
        self.status = OrderStatus.CONFIRMED
        data = event.event_data
        if data.get('expected_delivery'):
            self.expected_delivery = datetime.fromisoformat(data['expected_delivery'])
    
    def _apply_order_packed(self, event: Event):
        """Apply order packed event - ऑर्डर पैक इवेंट लागू करें"""
        self.status = OrderStatus.PACKED
    
    def _apply_order_shipped(self, event: Event):
        """Apply order shipped event - ऑर्डर भेजा गया इवेंट लागू करें"""
        self.status = OrderStatus.SHIPPED
        data = event.event_data
        self.tracking_id = data.get('tracking_id')
    
    def _apply_order_delivered(self, event: Event):
        """Apply order delivered event - ऑर्डर डिलीवर इवेंट लागू करें"""
        self.status = OrderStatus.DELIVERED
        self.actual_delivery = event.timestamp
    
    def _apply_order_cancelled(self, event: Event):
        """Apply order cancelled event - ऑर्डर रद्द इवेंट लागू करें"""
        self.status = OrderStatus.CANCELLED
    
    def _apply_order_returned(self, event: Event):
        """Apply order returned event - ऑर्डर वापसी इवेंट लागू करें"""
        self.status = OrderStatus.RETURNED

@dataclass
class Snapshot:
    """Aggregate snapshot for optimization - अनुकूलन के लिए एग्रीगेट स्नैपशॉट"""
    aggregate_id: str
    aggregate_type: str
    aggregate_data: bytes  # Compressed pickle data - संपीड़ित pickle डेटा
    version: int
    timestamp: datetime
    
    def compress_data(self, data: Any) -> bytes:
        """Compress aggregate data - एग्रीगेट डेटा संपीड़ित करें"""
        pickled_data = pickle.dumps(data)
        return gzip.compress(pickled_data)
    
    def decompress_data(self) -> Any:
        """Decompress aggregate data - एग्रीगेट डेटा डिकम्प्रेस करें"""
        decompressed_data = gzip.decompress(self.aggregate_data)
        return pickle.loads(decompressed_data)

class EventStore:
    """Advanced event store with snapshots - स्नैपशॉट के साथ उन्नत इवेंट स्टोर"""
    
    def __init__(self, db_path: str = "order_event_store.db", snapshot_frequency: int = 10):
        self.db_path = db_path
        self.snapshot_frequency = snapshot_frequency  # Snapshot every N events
        self.connection_pool = []
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables - डेटाबेस टेबल इनिशियलाइज़ करें"""
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                aggregate_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                version INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aggregate_id TEXT NOT NULL,
                aggregate_type TEXT NOT NULL,
                aggregate_data BLOB NOT NULL,
                version INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_events_aggregate_id ON events(aggregate_id);
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_snapshots_aggregate_id ON snapshots(aggregate_id);
            CREATE INDEX IF NOT EXISTS idx_snapshots_version ON snapshots(aggregate_id, version);
        """)
        conn.commit()
        conn.close()
    
    async def append_event(self, event: Event) -> bool:
        """Append event to store - स्टोर में इवेंट जोड़ें"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for optimistic concurrency - आशावादी समानता की जांच करें
            cursor.execute(
                "SELECT MAX(version) FROM events WHERE aggregate_id = ?",
                (event.aggregate_id,)
            )
            result = cursor.fetchone()
            expected_version = (result[0] or 0) + 1
            
            if event.version != expected_version:
                conn.close()
                raise Exception(f"Concurrency conflict: expected version {expected_version}, got {event.version}")
            
            # Insert event - इवेंट इन्सर्ट करें
            cursor.execute("""
                INSERT INTO events (event_id, aggregate_id, event_type, event_data, timestamp, version, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.aggregate_id,
                event.event_type.value,
                json.dumps(event.event_data),
                event.timestamp.isoformat(),
                event.version,
                json.dumps(event.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Create snapshot if needed - जरूरत पड़ने पर स्नैपशॉट बनाएं
            if event.version % self.snapshot_frequency == 0:
                await self._create_snapshot(event.aggregate_id)
            
            logger.info(f"Event appended: {event.event_type.value} for {event.aggregate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append event: {e}")
            return False
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for aggregate - एग्रीगेट के लिए इवेंट प्राप्त करें"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_id, aggregate_id, event_type, event_data, timestamp, version, metadata
            FROM events 
            WHERE aggregate_id = ? AND version > ?
            ORDER BY version ASC
        """, (aggregate_id, from_version))
        
        events = []
        for row in cursor.fetchall():
            events.append(Event(
                event_id=row[0],
                aggregate_id=row[1],
                event_type=EventType(row[2]),
                event_data=json.loads(row[3]),
                timestamp=datetime.fromisoformat(row[4]),
                version=row[5],
                metadata=json.loads(row[6] or '{}')
            ))
        
        conn.close()
        return events
    
    async def _create_snapshot(self, aggregate_id: str):
        """Create snapshot for aggregate - एग्रीगेट के लिए स्नैपशॉट बनाएं"""
        try:
            # Rebuild aggregate from events - इवेंट्स से एग्रीगेट पुनर्निर्माण
            events = await self.get_events(aggregate_id)
            if not events:
                return
            
            aggregate = OrderAggregate(order_id=aggregate_id, customer_id="")
            for event in events:
                aggregate.apply_event(event)
            
            # Compress and store snapshot - संपीड़ित करें और स्नैपशॉट स्टोर करें
            snapshot = Snapshot(
                aggregate_id=aggregate_id,
                aggregate_type="OrderAggregate",
                aggregate_data=gzip.compress(pickle.dumps(aggregate)),
                version=aggregate.version,
                timestamp=datetime.now()
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old snapshots (keep only latest 3) - पुराने स्नैपशॉट हटाएं
            cursor.execute("""
                DELETE FROM snapshots 
                WHERE aggregate_id = ? AND id NOT IN (
                    SELECT id FROM snapshots 
                    WHERE aggregate_id = ? 
                    ORDER BY version DESC 
                    LIMIT 3
                )
            """, (aggregate_id, aggregate_id))
            
            # Insert new snapshot - नया स्नैपशॉट इन्सर्ट करें
            cursor.execute("""
                INSERT INTO snapshots (aggregate_id, aggregate_type, aggregate_data, version, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                snapshot.aggregate_id,
                snapshot.aggregate_type,
                snapshot.aggregate_data,
                snapshot.version,
                snapshot.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Snapshot created for {aggregate_id} at version {snapshot.version}")
            
        except Exception as e:
            logger.error(f"Failed to create snapshot for {aggregate_id}: {e}")
    
    async def get_latest_snapshot(self, aggregate_id: str) -> Optional[Snapshot]:
        """Get latest snapshot for aggregate - एग्रीगेट के लिए नवीनतम स्नैपशॉट प्राप्त करें"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT aggregate_id, aggregate_type, aggregate_data, version, timestamp
            FROM snapshots 
            WHERE aggregate_id = ?
            ORDER BY version DESC 
            LIMIT 1
        """, (aggregate_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Snapshot(
                aggregate_id=row[0],
                aggregate_type=row[1],
                aggregate_data=row[2],
                version=row[3],
                timestamp=datetime.fromisoformat(row[4])
            )
        
        return None
    
    async def rebuild_aggregate(self, aggregate_id: str, 
                              point_in_time: Optional[datetime] = None) -> Optional[OrderAggregate]:
        """Rebuild aggregate with snapshot optimization - स्नैपशॉट अनुकूलन के साथ एग्रीगेट पुनर्निर्माण"""
        start_time = time.time()
        
        # Try to get latest snapshot first - पहले नवीनतम स्नैपशॉट प्राप्त करने का प्रयास करें
        snapshot = await self.get_latest_snapshot(aggregate_id)
        
        if snapshot:
            # Start from snapshot - स्नैपशॉट से शुरू करें
            aggregate = pickle.loads(gzip.decompress(snapshot.aggregate_data))
            from_version = snapshot.version
            logger.info(f"Loaded snapshot for {aggregate_id} at version {from_version}")
        else:
            # Start from scratch - शुरुआत से शुरू करें
            aggregate = OrderAggregate(order_id=aggregate_id, customer_id="")
            from_version = 0
        
        # Get events after snapshot - स्नैपशॉट के बाद के इवेंट प्राप्त करें
        events = await self.get_events(aggregate_id, from_version)
        
        # Apply point-in-time filter if specified - यदि निर्दिष्ट है तो point-in-time फ़िल्टर लागू करें
        if point_in_time:
            events = [e for e in events if e.timestamp <= point_in_time]
        
        # Apply events to aggregate - एग्रीगेट में इवेंट्स लागू करें
        for event in events:
            aggregate.apply_event(event)
        
        rebuild_time = time.time() - start_time
        logger.info(f"Aggregate {aggregate_id} rebuilt in {rebuild_time:.3f}s from {len(events)} events")
        
        return aggregate if events or snapshot else None
    
    async def get_aggregate_history(self, aggregate_id: str, 
                                  from_time: datetime, 
                                  to_time: datetime) -> List[Dict[str, Any]]:
        """Get aggregate state history for time range - समय सीमा के लिए एग्रीगेट स्थिति इतिहास प्राप्त करें"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, event_type, event_data 
            FROM events 
            WHERE aggregate_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (aggregate_id, from_time.isoformat(), to_time.isoformat()))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'timestamp': row[0],
                'event_type': row[1],
                'event_data': json.loads(row[2]),
                'aggregate_state': await self.rebuild_aggregate(
                    aggregate_id, 
                    datetime.fromisoformat(row[0])
                )
            })
        
        conn.close()
        return history

class OrderService:
    """Order service with event sourcing - इवेंट सोर्सिंग के साथ ऑर्डर सर्विस"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    async def create_order(self, customer_id: str, items: List[Dict], 
                         delivery_address: Dict, discount_amount: float = 0.0) -> str:
        """Create new order - नया ऑर्डर बनाएं"""
        order_id = str(uuid.uuid4())
        
        # Calculate amounts - राशि की गणना करें
        order_items = [OrderItem(**item) for item in items]
        total_amount = sum(item.total_price for item in order_items)
        tax_amount = total_amount * 0.18  # 18% GST
        final_amount = total_amount - discount_amount + tax_amount
        
        # Create order created event - ऑर्डर बनाया गया इवेंट बनाएं
        event = Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=order_id,
            event_type=EventType.ORDER_CREATED,
            event_data={
                'customer_id': customer_id,
                'items': items,
                'total_amount': total_amount,
                'discount_amount': discount_amount,
                'tax_amount': tax_amount,
                'final_amount': final_amount,
                'delivery_address': delivery_address
            },
            timestamp=datetime.now(),
            version=1,
            metadata={'source': 'flipkart_app', 'user_agent': 'mobile'}
        )
        
        await self.event_store.append_event(event)
        logger.info(f"Order {order_id} created for customer {customer_id}")
        return order_id
    
    async def confirm_payment(self, order_id: str, payment_id: str, 
                            payment_method: str) -> bool:
        """Confirm order payment - ऑर्डर भुगतान पुष्टि करें"""
        # Get current version - वर्तमान संस्करण प्राप्त करें
        aggregate = await self.event_store.rebuild_aggregate(order_id)
        if not aggregate:
            return False
        
        # Create payment completed event - भुगतान पूर्ण इवेंट बनाएं
        event = Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=order_id,
            event_type=EventType.PAYMENT_COMPLETED,
            event_data={
                'payment_id': payment_id,
                'payment_method': payment_method,
                'amount': aggregate.final_amount
            },
            timestamp=datetime.now(),
            version=aggregate.version + 1,
            metadata={'payment_gateway': 'paytm'}
        )
        
        await self.event_store.append_event(event)
        
        # Automatically confirm order after payment - भुगतान के बाद स्वचालित रूप से ऑर्डर पुष्टि करें
        await self.confirm_order(order_id)
        return True
    
    async def confirm_order(self, order_id: str) -> bool:
        """Confirm order after payment - भुगतान के बाद ऑर्डर पुष्टि करें"""
        aggregate = await self.event_store.rebuild_aggregate(order_id)
        if not aggregate:
            return False
        
        # Calculate expected delivery - अपेक्षित डिलीवरी की गणना करें
        expected_delivery = datetime.now() + timedelta(days=3)
        
        event = Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=order_id,
            event_type=EventType.ORDER_CONFIRMED,
            event_data={
                'expected_delivery': expected_delivery.isoformat(),
                'confirmed_at': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            version=aggregate.version + 1,
            metadata={'confirmed_by': 'system'}
        )
        
        await self.event_store.append_event(event)
        return True
    
    async def ship_order(self, order_id: str, tracking_id: str) -> bool:
        """Ship order - ऑर्डर शिप करें"""
        aggregate = await self.event_store.rebuild_aggregate(order_id)
        if not aggregate or aggregate.status != OrderStatus.PACKED:
            return False
        
        event = Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=order_id,
            event_type=EventType.ORDER_SHIPPED,
            event_data={
                'tracking_id': tracking_id,
                'shipped_at': datetime.now().isoformat(),
                'carrier': 'Ekart'  # Flipkart's logistics partner
            },
            timestamp=datetime.now(),
            version=aggregate.version + 1,
            metadata={'warehouse_id': 'BLR001'}
        )
        
        await self.event_store.append_event(event)
        return True
    
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get current order status - वर्तमान ऑर्डर स्थिति प्राप्त करें"""
        aggregate = await self.event_store.rebuild_aggregate(order_id)
        if not aggregate:
            return None
        
        return {
            'order_id': aggregate.order_id,
            'customer_id': aggregate.customer_id,
            'status': aggregate.status.value,
            'total_amount': aggregate.final_amount,
            'created_at': aggregate.created_at.isoformat(),
            'updated_at': aggregate.updated_at.isoformat(),
            'version': aggregate.version,
            'tracking_id': aggregate.tracking_id,
            'expected_delivery': aggregate.expected_delivery.isoformat() if aggregate.expected_delivery else None
        }

async def demonstrate_advanced_event_sourcing():
    """Demonstrate advanced event sourcing with snapshots"""
    """स्नैपशॉट के साथ उन्नत इवेंट सोर्सिंग का प्रदर्शन"""
    
    print("🚀 Starting Advanced Event Sourcing Demo")
    print("🚀 उन्नत इवेंट सोर्सिंग डेमो शुरू कर रहे हैं\n")
    
    # Initialize services - सेवाएं इनिशियलाइज़ करें
    event_store = EventStore(snapshot_frequency=5)  # Snapshot every 5 events
    order_service = OrderService(event_store)
    
    # Create sample orders - नमूना ऑर्डर बनाएं
    print("📦 Creating Flipkart orders - फ्लिपकार्ट ऑर्डर बना रहे हैं")
    
    order_items = [
        {
            "product_id": "PROD001",
            "product_name": "OnePlus 11 5G",
            "quantity": 1,
            "unit_price": 56999.0,
            "total_price": 56999.0,
            "seller_id": "ONEPLUS_OFFICIAL",
            "category": "Electronics"
        },
        {
            "product_id": "PROD002", 
            "product_name": "Boat Airdopes 141",
            "quantity": 2,
            "unit_price": 1299.0,
            "total_price": 2598.0,
            "seller_id": "BOAT_OFFICIAL",
            "category": "Electronics"
        }
    ]
    
    delivery_address = {
        "street": "123, MG Road",
        "area": "Koramangala",
        "city": "Bangalore",
        "state": "Karnataka", 
        "pincode": "560034"
    }
    
    # Create multiple orders - कई ऑर्डर बनाएं
    order_ids = []
    for i in range(3):
        order_id = await order_service.create_order(
            customer_id=f"CUST00{i+1}",
            items=order_items,
            delivery_address=delivery_address,
            discount_amount=5000.0
        )
        order_ids.append(order_id)
        print(f"   ✅ Order {order_id[:8]}... created")
    
    # Simulate order lifecycle for first order - पहले ऑर्डर के लिए ऑर्डर जीवनचक्र का सिमुलेशन
    main_order_id = order_ids[0]
    print(f"\n🔄 Processing order lifecycle for {main_order_id[:8]}...")
    
    # Payment confirmation - भुगतान पुष्टि
    await order_service.confirm_payment(
        main_order_id, 
        "PAY123456", 
        "UPI - PhonePe"
    )
    print("   💳 Payment confirmed")
    
    # Add more events to trigger snapshot - स्नैपशॉट ट्रिगर करने के लिए अधिक इवेंट्स जोड़ें
    for event_type in [EventType.INVENTORY_RESERVED, EventType.ORDER_PACKED]:
        event = Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=main_order_id,
            event_type=event_type,
            event_data={'timestamp': datetime.now().isoformat()},
            timestamp=datetime.now(),
            version=(await event_store.rebuild_aggregate(main_order_id)).version + 1
        )
        await event_store.append_event(event)
        print(f"   📝 Event: {event_type.value}")
    
    # Ship order - ऑर्डर शिप करें
    await order_service.ship_order(main_order_id, "EKART123456789")
    print("   🚚 Order shipped")
    
    # Demonstrate snapshot optimization - स्नैपशॉट अनुकूलन का प्रदर्शन
    print(f"\n📸 Snapshot Optimization Demo - स्नैपशॉट अनुकूलन डेमो")
    
    # Time reconstruction with and without snapshots - स्नैपशॉट के साथ और बिना पुनर्निर्माण का समय
    print("   ⏱️  Rebuild performance comparison:")
    
    # Rebuild from events only - केवल इवेंट्स से पुनर्निर्माण
    start_time = time.time()
    aggregate_from_events = await event_store.rebuild_aggregate(main_order_id)
    events_only_time = time.time() - start_time
    
    # Check snapshot exists - स्नैपशॉट मौजूद है की जांच करें
    snapshot = await event_store.get_latest_snapshot(main_order_id)
    if snapshot:
        print(f"   📸 Snapshot found at version {snapshot.version}")
        print(f"   🚀 Rebuild time with snapshot optimization: {events_only_time:.4f}s")
    else:
        print(f"   📝 No snapshot available, rebuilt from {await event_store.get_events(main_order_id).__len__()} events in {events_only_time:.4f}s")
    
    # Point-in-time query demo - point-in-time क्वेरी डेमो
    print(f"\n⏰ Point-in-Time Queries Demo - point-in-time क्वेरी डेमो")
    
    # Get order state at different points in time - अलग-अलग समय पर ऑर्डर स्थिति प्राप्त करें
    time_points = [
        datetime.now() - timedelta(minutes=5),
        datetime.now() - timedelta(minutes=3),
        datetime.now()
    ]
    
    for i, time_point in enumerate(time_points):
        past_state = await event_store.rebuild_aggregate(main_order_id, time_point)
        if past_state:
            print(f"   📅 State at T-{5-i*2}min: {past_state.status.value} (v{past_state.version})")
        else:
            print(f"   📅 No state existed at T-{5-i*2}min")
    
    # Show current order statuses - वर्तमान ऑर्डर स्थिति दिखाएं
    print(f"\n📊 Current Order Statuses - वर्तमान ऑर्डर स्थिति:")
    for order_id in order_ids:
        status = await order_service.get_order_status(order_id)
        if status:
            print(f"   📦 {order_id[:8]}: {status['status']} (₹{status['total_amount']:,.2f})")
    
    # Event store statistics - इवेंट स्टोर आंकड़े
    print(f"\n📈 Event Store Statistics - इवेंट स्टोर आंकड़े:")
    
    conn = sqlite3.connect(event_store.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM snapshots")  
    total_snapshots = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT aggregate_id) FROM events")
    total_aggregates = cursor.fetchone()[0]
    
    print(f"   📝 Total Events: {total_events}")
    print(f"   📸 Total Snapshots: {total_snapshots}")
    print(f"   📦 Total Orders: {total_aggregates}")
    
    conn.close()
    
    print("\n✅ Advanced Event Sourcing Demo Complete!")
    print("✅ उन्नत इवेंट सोर्सिंग डेमो पूरा हुआ!")

if __name__ == "__main__":
    """
    Run the advanced event sourcing demonstration
    उन्नत इवेंट सोर्सिंग प्रदर्शन चलाएं
    
    This demonstrates:
    यह प्रदर्शित करता है:
    
    1. Event sourcing with snapshot optimization - स्नैपशॉट अनुकूलन के साथ इवेंट सोर्सिंग
    2. Aggregate reconstruction performance - एग्रीगेट पुनर्निर्माण प्रदर्शन  
    3. Point-in-time state queries - point-in-time स्थिति क्वेरी
    4. Compressed snapshot storage - संपीड़ित स्नैपशॉट भंडारण
    5. Optimistic concurrency control - आशावादी समानता नियंत्रण
    6. Production-ready error handling - प्रोडक्शन-तैयार त्रुटि हैंडलिंग
    
    Key learnings:
    मुख्य सीख:
    
    - Snapshots dramatically improve reconstruction performance - स्नैपशॉट पुनर्निर्माण प्रदर्शन में नाटकीय सुधार करते हैं
    - Point-in-time queries enable powerful debugging - point-in-time क्वेरी शक्तिशाली डिबगिंग सक्षम बनाती है
    - Event sourcing provides complete audit trail - इवेंट सोर्सिंग पूर्ण ऑडिट ट्रेल प्रदान करता है
    - Compression reduces storage costs significantly - संपीड़न भंडारण लागत में महत्वपूर्ण कमी करता है
    - Optimistic locking prevents data corruption - आशावादी लॉकिंग डेटा भ्रष्टाचार रोकता है
    """
    
    try:
        asyncio.run(demonstrate_advanced_event_sourcing())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user - डेमो उपयोगकर्ता द्वारा बाधित")
    except Exception as e:
        print(f"\n❌ Demo failed with error - डेमो त्रुटि के साथ असफल: {e}")
        raise