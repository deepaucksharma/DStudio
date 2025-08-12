#!/usr/bin/env python3
"""
CQRS (Command Query Responsibility Segregation) Pattern for Flipkart Inventory Management
Separate read and write operations for optimal performance and scalability

जैसे Mumbai local train में:
- Commands (Write): Ticket booking, seat reservation (heavy operations)
- Queries (Read): Train schedule check, seat availability (light operations)

CQRS separates these concerns for better performance at Mumbai scale!
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
from abc import ABC, abstractmethod
import redis
import asyncpg
import motor.motor_asyncio
from concurrent.futures import ThreadPoolExecutor

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FlipkartInventoryCQRS")

# Commands (Write Side) - Heavy operations like Mumbai traffic
class InventoryCommand(ABC):
    """Base class for inventory commands"""
    command_id: str
    timestamp: datetime
    user_id: str

@dataclass
class AddProductCommand(InventoryCommand):
    """Add new product to inventory"""
    command_id: str
    product_id: str
    product_name: str
    category: str
    price: float
    initial_quantity: int
    warehouse_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""

@dataclass
class UpdateQuantityCommand(InventoryCommand):
    """Update product quantity"""
    command_id: str
    product_id: str
    quantity_change: int  # Can be positive or negative
    reason: str  # restocking, sold, damaged, returned
    warehouse_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""

@dataclass
class ReserveInventoryCommand(InventoryCommand):
    """Reserve inventory for order"""
    command_id: str
    product_id: str
    quantity: int
    order_id: str
    expiry_time: datetime
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""

@dataclass
class ReleaseReservationCommand(InventoryCommand):
    """Release reserved inventory"""
    command_id: str
    reservation_id: str
    reason: str  # order_cancelled, order_completed, expired
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""

@dataclass
class TransferInventoryCommand(InventoryCommand):
    """Transfer inventory between warehouses"""
    command_id: str
    product_id: str
    quantity: int
    from_warehouse_id: str
    to_warehouse_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""

# Queries (Read Side) - Light operations like checking train schedules
@dataclass
class ProductAvailabilityQuery:
    """Check product availability"""
    product_id: str
    warehouse_id: Optional[str] = None
    region: str = "mumbai"

@dataclass
class InventoryLevelQuery:
    """Get current inventory levels"""
    product_ids: List[str] = field(default_factory=list)
    warehouse_id: Optional[str] = None
    category: Optional[str] = None
    low_stock_threshold: int = 10

@dataclass
class ReservationStatusQuery:
    """Check reservation status"""
    reservation_id: Optional[str] = None
    order_id: Optional[str] = None
    product_id: Optional[str] = None

@dataclass
class InventoryMovementQuery:
    """Get inventory movement history"""
    product_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100

# Events - What actually happened
class InventoryEventType(Enum):
    PRODUCT_ADDED = "product_added"
    QUANTITY_UPDATED = "quantity_updated"
    INVENTORY_RESERVED = "inventory_reserved"
    RESERVATION_RELEASED = "reservation_released"
    INVENTORY_TRANSFERRED = "inventory_transferred"
    LOW_STOCK_ALERT = "low_stock_alert"

@dataclass
class InventoryEvent:
    """Inventory domain event"""
    event_id: str
    event_type: InventoryEventType
    aggregate_id: str  # product_id usually
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int
    correlation_id: str = ""

# Write Side - Command Handlers and Domain Logic
class InventoryAggregate:
    """
    Inventory aggregate for write operations
    जैसे Mumbai warehouse का actual stock management
    """
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.product_name = ""
        self.category = ""
        self.price = 0.0
        self.warehouses = {}  # warehouse_id -> quantity
        self.reservations = {}  # reservation_id -> reservation details
        self.version = 0
        self.last_updated = datetime.now()
        
        # Mumbai-specific fields
        self.min_stock_level = 50  # Mumbai demand is high
        self.max_stock_level = 1000
        self.reorder_point = 100
    
    def add_product(self, command: AddProductCommand) -> List[InventoryEvent]:
        """Add new product to inventory"""
        if self.product_id and self.product_id != command.product_id:
            raise ValueError("Product already exists with different ID")
        
        self.product_id = command.product_id
        self.product_name = command.product_name
        self.category = command.category
        self.price = command.price
        self.warehouses[command.warehouse_id] = command.initial_quantity
        self.version += 1
        
        events = [
            InventoryEvent(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                event_type=InventoryEventType.PRODUCT_ADDED,
                aggregate_id=self.product_id,
                event_data={
                    "product_name": command.product_name,
                    "category": command.category,
                    "price": command.price,
                    "initial_quantity": command.initial_quantity,
                    "warehouse_id": command.warehouse_id
                },
                timestamp=command.timestamp,
                version=self.version,
                correlation_id=command.command_id
            )
        ]
        
        return events
    
    def update_quantity(self, command: UpdateQuantityCommand) -> List[InventoryEvent]:
        """Update product quantity"""
        if not self.product_id:
            raise ValueError("Product not found")
        
        warehouse_id = command.warehouse_id
        current_qty = self.warehouses.get(warehouse_id, 0)
        new_qty = current_qty + command.quantity_change
        
        if new_qty < 0:
            raise ValueError(f"Insufficient inventory: {current_qty} available, trying to remove {abs(command.quantity_change)}")
        
        self.warehouses[warehouse_id] = new_qty
        self.version += 1
        
        events = [
            InventoryEvent(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                event_type=InventoryEventType.QUANTITY_UPDATED,
                aggregate_id=self.product_id,
                event_data={
                    "warehouse_id": warehouse_id,
                    "previous_quantity": current_qty,
                    "quantity_change": command.quantity_change,
                    "new_quantity": new_qty,
                    "reason": command.reason
                },
                timestamp=command.timestamp,
                version=self.version,
                correlation_id=command.command_id
            )
        ]
        
        # Check for low stock alert - Mumbai scale needs quick restocking
        if new_qty <= self.min_stock_level:
            events.append(
                InventoryEvent(
                    event_id=f"evt_{uuid.uuid4().hex[:12]}",
                    event_type=InventoryEventType.LOW_STOCK_ALERT,
                    aggregate_id=self.product_id,
                    event_data={
                        "warehouse_id": warehouse_id,
                        "current_quantity": new_qty,
                        "min_stock_level": self.min_stock_level,
                        "urgency": "high" if new_qty <= 10 else "medium"
                    },
                    timestamp=command.timestamp,
                    version=self.version
                )
            )
        
        return events
    
    def reserve_inventory(self, command: ReserveInventoryCommand) -> List[InventoryEvent]:
        """Reserve inventory for order"""
        total_available = sum(self.warehouses.values())
        
        if total_available < command.quantity:
            raise ValueError(f"Insufficient inventory to reserve: {total_available} available, {command.quantity} requested")
        
        # Find warehouse with sufficient quantity
        warehouse_id = None
        for wh_id, qty in self.warehouses.items():
            if qty >= command.quantity:
                warehouse_id = wh_id
                break
        
        if not warehouse_id:
            # Try to aggregate from multiple warehouses
            raise ValueError("Cannot reserve from single warehouse, multi-warehouse reservation not implemented")
        
        reservation_id = f"res_{command.order_id}_{uuid.uuid4().hex[:8]}"
        
        self.reservations[reservation_id] = {
            "product_id": command.product_id,
            "quantity": command.quantity,
            "order_id": command.order_id,
            "warehouse_id": warehouse_id,
            "reserved_at": command.timestamp,
            "expiry_time": command.expiry_time,
            "status": "active"
        }
        
        # Reduce available quantity
        self.warehouses[warehouse_id] -= command.quantity
        self.version += 1
        
        return [
            InventoryEvent(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                event_type=InventoryEventType.INVENTORY_RESERVED,
                aggregate_id=self.product_id,
                event_data={
                    "reservation_id": reservation_id,
                    "product_id": command.product_id,
                    "quantity": command.quantity,
                    "order_id": command.order_id,
                    "warehouse_id": warehouse_id,
                    "expiry_time": command.expiry_time.isoformat()
                },
                timestamp=command.timestamp,
                version=self.version,
                correlation_id=command.command_id
            )
        ]

class InventoryCommandHandler:
    """
    Command handler for inventory operations (Write side)
    जैसे Mumbai warehouse manager जो actual operations handle करता है
    """
    
    def __init__(self, event_store, write_db_pool):
        self.event_store = event_store
        self.write_db_pool = write_db_pool
        self.aggregates = {}  # Cache for aggregates
    
    async def handle_add_product(self, command: AddProductCommand) -> List[InventoryEvent]:
        """Handle add product command"""
        logger.info(f"Handling add product command: {command.product_id}")
        
        aggregate = await self.get_aggregate(command.product_id)
        events = aggregate.add_product(command)
        
        # Persist events and update aggregate
        for event in events:
            await self.event_store.append_event(event)
        
        # Store in write database
        await self.persist_aggregate_snapshot(aggregate)
        
        return events
    
    async def handle_update_quantity(self, command: UpdateQuantityCommand) -> List[InventoryEvent]:
        """Handle quantity update command"""
        logger.info(f"Handling quantity update: {command.product_id}, change: {command.quantity_change}")
        
        aggregate = await self.get_aggregate(command.product_id)
        events = aggregate.update_quantity(command)
        
        for event in events:
            await self.event_store.append_event(event)
        
        await self.persist_aggregate_snapshot(aggregate)
        
        return events
    
    async def handle_reserve_inventory(self, command: ReserveInventoryCommand) -> List[InventoryEvent]:
        """Handle inventory reservation command"""
        logger.info(f"Handling inventory reservation: {command.product_id}, qty: {command.quantity}")
        
        aggregate = await self.get_aggregate(command.product_id)
        events = aggregate.reserve_inventory(command)
        
        for event in events:
            await self.event_store.append_event(event)
        
        await self.persist_aggregate_snapshot(aggregate)
        
        return events
    
    async def get_aggregate(self, product_id: str) -> InventoryAggregate:
        """Get or create aggregate"""
        if product_id in self.aggregates:
            return self.aggregates[product_id]
        
        # Try to load from snapshot first
        aggregate = await self.load_aggregate_snapshot(product_id)
        
        if not aggregate:
            aggregate = InventoryAggregate(product_id)
        
        # Apply any new events since snapshot
        events = await self.event_store.get_events_since(product_id, aggregate.version)
        for event in events:
            aggregate.apply_event(event)
        
        self.aggregates[product_id] = aggregate
        return aggregate
    
    async def load_aggregate_snapshot(self, product_id: str) -> Optional[InventoryAggregate]:
        """Load aggregate snapshot from write database"""
        async with self.write_db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM inventory_snapshots WHERE product_id = $1",
                product_id
            )
            
            if row:
                aggregate = InventoryAggregate(product_id)
                aggregate.product_name = row['product_name']
                aggregate.category = row['category']
                aggregate.price = row['price']
                aggregate.warehouses = json.loads(row['warehouses'])
                aggregate.reservations = json.loads(row['reservations'])
                aggregate.version = row['version']
                aggregate.last_updated = row['last_updated']
                return aggregate
        
        return None
    
    async def persist_aggregate_snapshot(self, aggregate: InventoryAggregate):
        """Persist aggregate snapshot to write database"""
        async with self.write_db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO inventory_snapshots 
                (product_id, product_name, category, price, warehouses, reservations, version, last_updated)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (product_id) DO UPDATE SET
                product_name = $2, category = $3, price = $4, warehouses = $5, 
                reservations = $6, version = $7, last_updated = $8
                """,
                aggregate.product_id, aggregate.product_name, aggregate.category,
                aggregate.price, json.dumps(aggregate.warehouses),
                json.dumps(aggregate.reservations, default=str), 
                aggregate.version, aggregate.last_updated
            )

# Read Side - Query Handlers and Projections
class InventoryReadModel:
    """
    Read model for inventory queries
    जैसे Mumbai local train time table - optimized for quick reads
    """
    
    def __init__(self, read_db_client):
        self.read_db = read_db_client
    
    async def get_product_availability(self, query: ProductAvailabilityQuery) -> Dict[str, Any]:
        """Get product availability information"""
        filter_criteria = {"product_id": query.product_id}
        
        if query.warehouse_id:
            filter_criteria["warehouse_id"] = query.warehouse_id
        
        # Query from read database (MongoDB for fast reads)
        cursor = self.read_db.inventory_availability.find(filter_criteria)
        
        results = []
        total_available = 0
        
        async for doc in cursor:
            results.append({
                "warehouse_id": doc["warehouse_id"],
                "available_quantity": doc["available_quantity"],
                "reserved_quantity": doc.get("reserved_quantity", 0),
                "last_updated": doc["last_updated"]
            })
            total_available += doc["available_quantity"]
        
        return {
            "product_id": query.product_id,
            "total_available": total_available,
            "warehouses": results,
            "in_stock": total_available > 0,
            "can_fulfill_order": total_available >= 1,  # Basic check
            "region": query.region
        }
    
    async def get_inventory_levels(self, query: InventoryLevelQuery) -> List[Dict[str, Any]]:
        """Get inventory levels with low stock alerts"""
        filter_criteria = {}
        
        if query.product_ids:
            filter_criteria["product_id"] = {"$in": query.product_ids}
        
        if query.warehouse_id:
            filter_criteria["warehouse_id"] = query.warehouse_id
        
        if query.category:
            filter_criteria["category"] = query.category
        
        cursor = self.read_db.inventory_levels.find(filter_criteria).limit(100)
        
        results = []
        async for doc in cursor:
            total_quantity = doc["available_quantity"] + doc.get("reserved_quantity", 0)
            is_low_stock = total_quantity <= query.low_stock_threshold
            
            results.append({
                "product_id": doc["product_id"],
                "product_name": doc["product_name"],
                "category": doc["category"],
                "warehouse_id": doc["warehouse_id"],
                "available_quantity": doc["available_quantity"],
                "reserved_quantity": doc.get("reserved_quantity", 0),
                "total_quantity": total_quantity,
                "is_low_stock": is_low_stock,
                "last_restocked": doc.get("last_restocked"),
                "last_updated": doc["last_updated"]
            })
        
        return sorted(results, key=lambda x: x["total_quantity"])
    
    async def get_reservation_status(self, query: ReservationStatusQuery) -> List[Dict[str, Any]]:
        """Get reservation status"""
        filter_criteria = {}
        
        if query.reservation_id:
            filter_criteria["reservation_id"] = query.reservation_id
        
        if query.order_id:
            filter_criteria["order_id"] = query.order_id
        
        if query.product_id:
            filter_criteria["product_id"] = query.product_id
        
        cursor = self.read_db.inventory_reservations.find(filter_criteria)
        
        results = []
        async for doc in cursor:
            expiry_time = doc.get("expiry_time")
            is_expired = expiry_time and datetime.fromisoformat(expiry_time) < datetime.now()
            
            results.append({
                "reservation_id": doc["reservation_id"],
                "product_id": doc["product_id"],
                "quantity": doc["quantity"],
                "order_id": doc["order_id"],
                "warehouse_id": doc["warehouse_id"],
                "status": doc["status"],
                "reserved_at": doc["reserved_at"],
                "expiry_time": expiry_time,
                "is_expired": is_expired
            })
        
        return results
    
    async def get_inventory_movements(self, query: InventoryMovementQuery) -> List[Dict[str, Any]]:
        """Get inventory movement history"""
        filter_criteria = {}
        
        if query.product_id:
            filter_criteria["product_id"] = query.product_id
        
        if query.warehouse_id:
            filter_criteria["warehouse_id"] = query.warehouse_id
        
        if query.start_date and query.end_date:
            filter_criteria["timestamp"] = {
                "$gte": query.start_date.isoformat(),
                "$lte": query.end_date.isoformat()
            }
        
        cursor = (self.read_db.inventory_movements
                 .find(filter_criteria)
                 .sort("timestamp", -1)
                 .limit(query.limit))
        
        results = []
        async for doc in cursor:
            results.append({
                "movement_id": doc["_id"],
                "product_id": doc["product_id"],
                "warehouse_id": doc.get("warehouse_id"),
                "movement_type": doc["movement_type"],
                "quantity_change": doc["quantity_change"],
                "reason": doc.get("reason"),
                "timestamp": doc["timestamp"],
                "reference_id": doc.get("reference_id")  # order_id, transfer_id etc.
            })
        
        return results

class InventoryProjectionHandler:
    """
    Projection handler to update read models from events
    जैसे Mumbai train display board को real-time update करना
    """
    
    def __init__(self, read_db_client):
        self.read_db = read_db_client
    
    async def handle_event(self, event: InventoryEvent):
        """Handle inventory event and update read models"""
        logger.info(f"Updating projections for event: {event.event_type.value}")
        
        if event.event_type == InventoryEventType.PRODUCT_ADDED:
            await self.handle_product_added(event)
        elif event.event_type == InventoryEventType.QUANTITY_UPDATED:
            await self.handle_quantity_updated(event)
        elif event.event_type == InventoryEventType.INVENTORY_RESERVED:
            await self.handle_inventory_reserved(event)
        elif event.event_type == InventoryEventType.LOW_STOCK_ALERT:
            await self.handle_low_stock_alert(event)
    
    async def handle_product_added(self, event: InventoryEvent):
        """Handle product added event"""
        data = event.event_data
        
        # Update availability projection
        await self.read_db.inventory_availability.insert_one({
            "product_id": event.aggregate_id,
            "product_name": data["product_name"],
            "category": data["category"],
            "warehouse_id": data["warehouse_id"],
            "available_quantity": data["initial_quantity"],
            "reserved_quantity": 0,
            "last_updated": event.timestamp.isoformat()
        })
        
        # Update levels projection
        await self.read_db.inventory_levels.insert_one({
            "product_id": event.aggregate_id,
            "product_name": data["product_name"],
            "category": data["category"],
            "warehouse_id": data["warehouse_id"],
            "available_quantity": data["initial_quantity"],
            "reserved_quantity": 0,
            "price": data["price"],
            "last_restocked": event.timestamp.isoformat(),
            "last_updated": event.timestamp.isoformat()
        })
    
    async def handle_quantity_updated(self, event: InventoryEvent):
        """Handle quantity updated event"""
        data = event.event_data
        
        # Update availability
        await self.read_db.inventory_availability.update_one(
            {
                "product_id": event.aggregate_id,
                "warehouse_id": data["warehouse_id"]
            },
            {
                "$set": {
                    "available_quantity": data["new_quantity"],
                    "last_updated": event.timestamp.isoformat()
                }
            }
        )
        
        # Update levels
        await self.read_db.inventory_levels.update_one(
            {
                "product_id": event.aggregate_id,
                "warehouse_id": data["warehouse_id"]
            },
            {
                "$set": {
                    "available_quantity": data["new_quantity"],
                    "last_updated": event.timestamp.isoformat()
                }
            }
        )
        
        # Add movement record
        await self.read_db.inventory_movements.insert_one({
            "product_id": event.aggregate_id,
            "warehouse_id": data["warehouse_id"],
            "movement_type": "quantity_update",
            "quantity_change": data["quantity_change"],
            "reason": data["reason"],
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.event_id
        })
    
    async def handle_inventory_reserved(self, event: InventoryEvent):
        """Handle inventory reserved event"""
        data = event.event_data
        
        # Update reserved quantity in availability
        await self.read_db.inventory_availability.update_one(
            {
                "product_id": event.aggregate_id,
                "warehouse_id": data["warehouse_id"]
            },
            {
                "$inc": {"reserved_quantity": data["quantity"]},
                "$set": {"last_updated": event.timestamp.isoformat()}
            }
        )
        
        # Create reservation record
        await self.read_db.inventory_reservations.insert_one({
            "reservation_id": data["reservation_id"],
            "product_id": event.aggregate_id,
            "quantity": data["quantity"],
            "order_id": data["order_id"],
            "warehouse_id": data["warehouse_id"],
            "status": "active",
            "reserved_at": event.timestamp.isoformat(),
            "expiry_time": data["expiry_time"]
        })
    
    async def handle_low_stock_alert(self, event: InventoryEvent):
        """Handle low stock alert event"""
        data = event.event_data
        
        # Create alert record
        await self.read_db.stock_alerts.insert_one({
            "product_id": event.aggregate_id,
            "warehouse_id": data["warehouse_id"],
            "current_quantity": data["current_quantity"],
            "min_stock_level": data["min_stock_level"],
            "urgency": data["urgency"],
            "alert_time": event.timestamp.isoformat(),
            "status": "open"
        })

class EventStore:
    """Simple event store using Redis Streams"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def append_event(self, event: InventoryEvent):
        """Append event to event store"""
        stream_name = f"inventory_events:{event.aggregate_id}"
        
        event_data = asdict(event)
        event_data['timestamp'] = event.timestamp.isoformat()
        event_data['event_type'] = event.event_type.value
        
        self.redis_client.xadd(stream_name, event_data)
        
        # Also add to global stream for projections
        self.redis_client.xadd("inventory_events:all", {
            "aggregate_id": event.aggregate_id,
            "event_type": event.event_type.value,
            "event_id": event.event_id
        })
    
    async def get_events_since(self, aggregate_id: str, version: int) -> List[InventoryEvent]:
        """Get events since specific version"""
        stream_name = f"inventory_events:{aggregate_id}"
        
        try:
            events_data = self.redis_client.xrange(stream_name)
            
            events = []
            for event_id, fields in events_data:
                event_dict = {k.decode(): v.decode() if isinstance(v, bytes) else v 
                             for k, v in fields.items()}
                
                if int(event_dict.get('version', 0)) > version:
                    event_dict['event_data'] = json.loads(event_dict['event_data'])
                    event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
                    event_dict['event_type'] = InventoryEventType(event_dict['event_type'])
                    
                    events.append(InventoryEvent(**event_dict))
            
            return sorted(events, key=lambda e: e.version)
            
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return []

async def demo_flipkart_inventory_cqrs():
    """
    Demonstrate CQRS pattern with Flipkart inventory management
    Mumbai scale inventory के साथ separate read/write operations
    """
    print("\n=== Flipkart Inventory CQRS Demo ===")
    print("Mumbai-style inventory management with separated read/write operations!")
    
    # Initialize components
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Mock database connections
    write_db_pool = None  # Would be PostgreSQL connection pool
    read_db_client = None  # Would be MongoDB client
    
    # For demo, create simplified versions
    class MockWriteDB:
        def __init__(self):
            self.snapshots = {}
        
        async def acquire(self):
            return self
        
        async def fetchrow(self, query, *args):
            product_id = args[0]
            return self.snapshots.get(product_id)
        
        async def execute(self, query, *args):
            if "INSERT" in query and "inventory_snapshots" in query:
                product_id = args[0]
                self.snapshots[product_id] = {
                    'product_name': args[1],
                    'category': args[2],
                    'price': args[3],
                    'warehouses': args[4],
                    'reservations': args[5],
                    'version': args[6],
                    'last_updated': args[7]
                }
    
    class MockReadDB:
        def __init__(self):
            self.inventory_availability = MockCollection()
            self.inventory_levels = MockCollection()
            self.inventory_reservations = MockCollection()
            self.inventory_movements = MockCollection()
            self.stock_alerts = MockCollection()
    
    class MockCollection:
        def __init__(self):
            self.data = []
        
        def find(self, criteria=None):
            return MockCursor(self.data, criteria)
        
        async def insert_one(self, doc):
            self.data.append(doc)
        
        async def update_one(self, criteria, update):
            # Simple mock update
            for doc in self.data:
                if self._matches(doc, criteria):
                    if "$set" in update:
                        doc.update(update["$set"])
                    if "$inc" in update:
                        for key, value in update["$inc"].items():
                            doc[key] = doc.get(key, 0) + value
                    break
        
        def _matches(self, doc, criteria):
            if not criteria:
                return True
            for key, value in criteria.items():
                if doc.get(key) != value:
                    return False
            return True
    
    class MockCursor:
        def __init__(self, data, criteria):
            self.data = [item for item in data if self._matches(item, criteria)] if criteria else data
            self.index = 0
        
        def _matches(self, doc, criteria):
            if not criteria:
                return True
            for key, value in criteria.items():
                if isinstance(value, dict):
                    if "$in" in value:
                        if doc.get(key) not in value["$in"]:
                            return False
                elif doc.get(key) != value:
                    return False
            return True
        
        def limit(self, n):
            self.data = self.data[:n]
            return self
        
        def sort(self, key, direction):
            reverse = direction == -1
            self.data.sort(key=lambda x: x.get(key.replace(".", "_"), ""), reverse=reverse)
            return self
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if self.index >= len(self.data):
                raise StopAsyncIteration
            item = self.data[self.index]
            self.index += 1
            return item
    
    # Initialize components
    event_store = EventStore(redis_client)
    write_db_pool = MockWriteDB()
    read_db_client = MockReadDB()
    
    command_handler = InventoryCommandHandler(event_store, write_db_pool)
    read_model = InventoryReadModel(read_db_client)
    projection_handler = InventoryProjectionHandler(read_db_client)
    
    print("\n--- Demo Scenario: Mumbai Electronics Store ---")
    
    # Command Side - Heavy write operations
    print("\n1. Adding Products (Command Side - Write Operations)")
    
    # Add products
    products = [
        AddProductCommand(
            command_id="cmd_001",
            product_id="PHONE_ONEPLUS_12",
            product_name="OnePlus 12 (256GB)",
            category="smartphones",
            price=65999.0,
            initial_quantity=100,
            warehouse_id="MUM_WH_001",
            user_id="admin_mumbai"
        ),
        AddProductCommand(
            command_id="cmd_002",
            product_id="LAPTOP_MACBOOK_AIR",
            product_name="MacBook Air M2",
            category="laptops",
            price=119900.0,
            initial_quantity=50,
            warehouse_id="MUM_WH_001",
            user_id="admin_mumbai"
        )
    ]
    
    for product in products:
        events = await command_handler.handle_add_product(product)
        print(f"✅ Added {product.product_name} - Generated {len(events)} events")
        
        # Update projections
        for event in events:
            await projection_handler.handle_event(event)
    
    # Update quantities (simulating sales and restocking)
    print("\n2. Inventory Updates (Command Side)")
    updates = [
        UpdateQuantityCommand(
            command_id="cmd_003",
            product_id="PHONE_ONEPLUS_12",
            quantity_change=-25,  # 25 phones sold
            reason="sold",
            warehouse_id="MUM_WH_001",
            user_id="sales_system"
        ),
        UpdateQuantityCommand(
            command_id="cmd_004",
            product_id="PHONE_ONEPLUS_12",
            quantity_change=200,  # Restocking
            reason="restocking",
            warehouse_id="MUM_WH_001",
            user_id="warehouse_manager"
        )
    ]
    
    for update in updates:
        events = await command_handler.handle_update_quantity(update)
        action = "sold" if update.quantity_change < 0 else "restocked"
        print(f"✅ {action.title()} {abs(update.quantity_change)} units of {update.product_id}")
        
        for event in events:
            await projection_handler.handle_event(event)
    
    # Reserve inventory for orders
    print("\n3. Inventory Reservations (Command Side)")
    reservation_cmd = ReserveInventoryCommand(
        command_id="cmd_005",
        product_id="PHONE_ONEPLUS_12",
        quantity=5,
        order_id="ORDER_MUM_12345",
        expiry_time=datetime.now() + timedelta(minutes=15),
        user_id="order_system"
    )
    
    events = await command_handler.handle_reserve_inventory(reservation_cmd)
    print(f"✅ Reserved {reservation_cmd.quantity} units for order {reservation_cmd.order_id}")
    
    for event in events:
        await projection_handler.handle_event(event)
    
    # Query Side - Fast read operations
    print("\n--- Query Side - Read Operations (Optimized for Speed) ---")
    
    # 1. Check product availability
    print("\n1. Product Availability Query (Like checking train seat availability)")
    availability_query = ProductAvailabilityQuery(
        product_id="PHONE_ONEPLUS_12",
        region="mumbai"
    )
    
    availability = await read_model.get_product_availability(availability_query)
    print(f"Product: {availability['product_id']}")
    print(f"Total Available: {availability['total_available']}")
    print(f"In Stock: {availability['in_stock']}")
    print(f"Can Fulfill Order: {availability['can_fulfill_order']}")
    
    for warehouse in availability['warehouses']:
        print(f"  Warehouse {warehouse['warehouse_id']}: {warehouse['available_quantity']} available, {warehouse['reserved_quantity']} reserved")
    
    # 2. Get inventory levels
    print("\n2. Inventory Levels Query (Like train capacity dashboard)")
    levels_query = InventoryLevelQuery(
        product_ids=["PHONE_ONEPLUS_12", "LAPTOP_MACBOOK_AIR"],
        low_stock_threshold=50
    )
    
    levels = await read_model.get_inventory_levels(levels_query)
    for level in levels:
        stock_status = "🔴 LOW STOCK" if level['is_low_stock'] else "✅ GOOD STOCK"
        print(f"{level['product_name']}: {level['total_quantity']} total ({level['available_quantity']} available) - {stock_status}")
    
    # 3. Check reservation status
    print("\n3. Reservation Status Query (Like ticket booking status)")
    reservation_query = ReservationStatusQuery(
        order_id="ORDER_MUM_12345"
    )
    
    reservations = await read_model.get_reservation_status(reservation_query)
    for reservation in reservations:
        expiry_status = "EXPIRED" if reservation['is_expired'] else "ACTIVE"
        print(f"Reservation {reservation['reservation_id']}: {reservation['quantity']} units, Status: {expiry_status}")
    
    # 4. Get movement history
    print("\n4. Inventory Movement History (Like train movement log)")
    movement_query = InventoryMovementQuery(
        product_id="PHONE_ONEPLUS_12",
        limit=10
    )
    
    movements = await read_model.get_inventory_movements(movement_query)
    print(f"Recent movements for PHONE_ONEPLUS_12:")
    for movement in movements:
        change_type = "➕" if movement['quantity_change'] > 0 else "➖"
        print(f"  {change_type} {abs(movement['quantity_change'])} units - {movement['reason']} ({movement['timestamp'][:19]})")
    
    print("\n--- CQRS Benefits Demonstrated ---")
    print("✅ Write Side (Commands):")
    print("   - Complex business logic for inventory management")
    print("   - Event sourcing for complete audit trail")
    print("   - Strong consistency for critical operations")
    print("   - Like Mumbai warehouse operations - accurate and reliable")
    
    print("\n✅ Read Side (Queries):")
    print("   - Optimized projections for fast queries")
    print("   - Multiple specialized read models")
    print("   - Eventually consistent but highly available")
    print("   - Like Mumbai local train display - fast and accessible")
    
    print(f"\n🚂 CQRS Pattern successfully demonstrated!")
    print(f"   Command operations: Heavy but consistent")
    print(f"   Query operations: Fast and scalable")
    print(f"   Perfect separation of concerns - Mumbai efficiency style!")

if __name__ == "__main__":
    print("Starting Flipkart Inventory CQRS Demo...")
    asyncio.run(demo_flipkart_inventory_cqrs())