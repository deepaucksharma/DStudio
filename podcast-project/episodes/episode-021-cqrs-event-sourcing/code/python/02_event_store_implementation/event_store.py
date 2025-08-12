"""
Event Store Implementation - Zerodha Trading के लिए
यह example दिखाता है कि कैसे events को store और retrieve करते हैं
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Event Base Class - सभी events इससे inherit करेंगे
@dataclass
class BaseEvent:
    """Base class for all events"""
    event_id: str
    aggregate_id: str  # Entity का ID (जैसे user_id, order_id)
    event_type: str
    timestamp: datetime
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# Trading Events - Zerodha के context में
@dataclass
class OrderPlacedEvent(BaseEvent):
    """जब नया order place होता है"""
    def __init__(self, aggregate_id: str, symbol: str, quantity: int, 
                 price: float, order_type: str, user_id: str):
        super().__init__(
            event_id=str(uuid.uuid4()),
            aggregate_id=aggregate_id,
            event_type="ORDER_PLACED",
            timestamp=datetime.now(),
            version=1,
            data={
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,  # BUY, SELL
                "user_id": user_id,
                "status": "PENDING"
            },
            metadata={
                "source": "zerodha_kite",
                "session_id": str(uuid.uuid4())
            }
        )

@dataclass
class OrderExecutedEvent(BaseEvent):
    """जब order execute हो जाता है"""
    def __init__(self, aggregate_id: str, executed_price: float, 
                 executed_quantity: int, execution_time: datetime = None):
        super().__init__(
            event_id=str(uuid.uuid4()),
            aggregate_id=aggregate_id,
            event_type="ORDER_EXECUTED",
            timestamp=execution_time or datetime.now(),
            version=1,
            data={
                "executed_price": executed_price,
                "executed_quantity": executed_quantity,
                "execution_id": str(uuid.uuid4())
            },
            metadata={
                "exchange": "NSE",
                "broker": "zerodha"
            }
        )

@dataclass
class OrderCancelledEvent(BaseEvent):
    """जब order cancel हो जाता है"""
    def __init__(self, aggregate_id: str, reason: str, cancelled_by: str):
        super().__init__(
            event_id=str(uuid.uuid4()),
            aggregate_id=aggregate_id,
            event_type="ORDER_CANCELLED",
            timestamp=datetime.now(),
            version=1,
            data={
                "reason": reason,
                "cancelled_by": cancelled_by  # USER, SYSTEM, EXCHANGE
            },
            metadata={
                "cancellation_fee": 0.0
            }
        )

# Event Store Interface
class IEventStore(ABC):
    """Event Store का interface"""
    
    @abstractmethod
    async def append_event(self, event: BaseEvent) -> bool:
        """Event को store में add करता है"""
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[BaseEvent]:
        """Aggregate के सभी events लाता है"""
        pass
    
    @abstractmethod
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[BaseEvent]:
        """Event type के हिसाब से events लाता है"""
        pass

# SQLite Event Store Implementation
class SQLiteEventStore(IEventStore):
    """SQLite के साथ Event Store का implementation"""
    
    def __init__(self, db_path: str = "zerodha_events.db"):
        self.db_path = db_path
        self.lock = threading.Lock()  # Thread safety के लिए
        self._initialize_db()
    
    def _initialize_db(self):
        """Database tables बनाता है"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    aggregate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_aggregate_id (aggregate_id),
                    INDEX idx_event_type (event_type),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            # Event को serialize करने के लिए JSON functions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    aggregate_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
        logger.info("Event Store database initialized successfully")
    
    def _event_to_dict(self, event: BaseEvent) -> Dict:
        """Event को dictionary में convert करता है"""
        return {
            'event_id': event.event_id,
            'aggregate_id': event.aggregate_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'version': event.version,
            'data': json.dumps(event.data),
            'metadata': json.dumps(event.metadata) if event.metadata else None
        }
    
    def _dict_to_event(self, event_dict: Dict) -> BaseEvent:
        """Dictionary को Event में convert करता है"""
        return BaseEvent(
            event_id=event_dict['event_id'],
            aggregate_id=event_dict['aggregate_id'],
            event_type=event_dict['event_type'],
            timestamp=datetime.fromisoformat(event_dict['timestamp']),
            version=event_dict['version'],
            data=json.loads(event_dict['data']),
            metadata=json.loads(event_dict['metadata']) if event_dict['metadata'] else {}
        )
    
    async def append_event(self, event: BaseEvent) -> bool:
        """Event को database में store करता है"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    event_dict = self._event_to_dict(event)
                    
                    # Optimistic concurrency control - version check करते हैं
                    cursor = conn.execute(
                        "SELECT MAX(version) FROM events WHERE aggregate_id = ?",
                        (event.aggregate_id,)
                    )
                    max_version = cursor.fetchone()[0] or 0
                    
                    if event.version <= max_version:
                        raise ValueError(f"Event version conflict. Expected > {max_version}, got {event.version}")
                    
                    # Event insert करते हैं
                    conn.execute("""
                        INSERT INTO events (event_id, aggregate_id, event_type, timestamp, version, data, metadata)
                        VALUES (:event_id, :aggregate_id, :event_type, :timestamp, :version, :data, :metadata)
                    """, event_dict)
                    
                    logger.info(f"Event stored: {event.event_type} for aggregate {event.aggregate_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to append event: {str(e)}")
            raise
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[BaseEvent]:
        """Aggregate के सभी events retrieve करता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Dict-like access के लिए
                
                cursor = conn.execute("""
                    SELECT * FROM events 
                    WHERE aggregate_id = ? AND version > ?
                    ORDER BY version ASC
                """, (aggregate_id, from_version))
                
                events = []
                for row in cursor.fetchall():
                    event = self._dict_to_event(dict(row))
                    events.append(event)
                
                logger.info(f"Retrieved {len(events)} events for aggregate {aggregate_id}")
                return events
                
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            raise
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[BaseEvent]:
        """Event type के हिसाब से events लाता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM events 
                    WHERE event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (event_type, limit))
                
                events = []
                for row in cursor.fetchall():
                    event = self._dict_to_event(dict(row))
                    events.append(event)
                
                logger.info(f"Retrieved {len(events)} events of type {event_type}")
                return events
                
        except Exception as e:
            logger.error(f"Failed to get events by type: {str(e)}")
            raise
    
    async def get_all_events_stream(self, batch_size: int = 1000):
        """सभी events का stream - event replay के लिए"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                offset = 0
                while True:
                    cursor = conn.execute("""
                        SELECT * FROM events 
                        ORDER BY timestamp ASC
                        LIMIT ? OFFSET ?
                    """, (batch_size, offset))
                    
                    rows = cursor.fetchall()
                    if not rows:
                        break
                    
                    for row in rows:
                        yield self._dict_to_event(dict(row))
                    
                    offset += batch_size
                    
        except Exception as e:
            logger.error(f"Failed to stream events: {str(e)}")
            raise

# Trading Order Aggregate - Business logic के लिए
class TradingOrder:
    """Trading order का aggregate root"""
    
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.version = 0
        self.status = "PENDING"
        self.symbol = None
        self.quantity = 0
        self.price = 0.0
        self.order_type = None
        self.user_id = None
        self.executed_quantity = 0
        self.executed_price = 0.0
        self.events = []  # Uncommitted events
    
    def place_order(self, symbol: str, quantity: int, price: float, 
                   order_type: str, user_id: str):
        """नया order place करता है"""
        if self.status != "PENDING":
            raise ValueError("Order already processed नहीं कर सकते")
        
        event = OrderPlacedEvent(
            self.order_id, symbol, quantity, price, order_type, user_id
        )
        
        self._apply_event(event)
        self.events.append(event)
    
    def execute_order(self, executed_price: float, executed_quantity: int):
        """Order को execute करता है"""
        if self.status != "PLACED":
            raise ValueError("Order execute करने के लिए PLACED status चाहिए")
        
        if executed_quantity > self.quantity:
            raise ValueError("Executed quantity, order quantity से ज्यादा नहीं हो सकती")
        
        event = OrderExecutedEvent(
            self.order_id, executed_price, executed_quantity
        )
        
        self._apply_event(event)
        self.events.append(event)
    
    def cancel_order(self, reason: str, cancelled_by: str):
        """Order को cancel करता है"""
        if self.status in ["EXECUTED", "CANCELLED"]:
            raise ValueError(f"Cannot cancel order in {self.status} status")
        
        event = OrderCancelledEvent(self.order_id, reason, cancelled_by)
        
        self._apply_event(event)
        self.events.append(event)
    
    def _apply_event(self, event: BaseEvent):
        """Event को current state पर apply करता है"""
        if event.event_type == "ORDER_PLACED":
            self.symbol = event.data["symbol"]
            self.quantity = event.data["quantity"]
            self.price = event.data["price"]
            self.order_type = event.data["order_type"]
            self.user_id = event.data["user_id"]
            self.status = "PLACED"
            
        elif event.event_type == "ORDER_EXECUTED":
            self.executed_price = event.data["executed_price"]
            self.executed_quantity = event.data["executed_quantity"]
            self.status = "EXECUTED"
            
        elif event.event_type == "ORDER_CANCELLED":
            self.status = "CANCELLED"
        
        self.version += 1
    
    def load_from_history(self, events: List[BaseEvent]):
        """Event history से state बनाता है"""
        for event in events:
            self._apply_event(event)
        self.events = []  # History events को clear करते हैं
    
    def get_uncommitted_events(self) -> List[BaseEvent]:
        """अभी तक save नहीं हुए events return करता है"""
        return self.events.copy()
    
    def mark_events_as_committed(self):
        """Events को committed mark करता है"""
        self.events.clear()

# Repository Pattern - Event Store के साथ
class TradingOrderRepository:
    """Trading Order का repository"""
    
    def __init__(self, event_store: IEventStore):
        self.event_store = event_store
    
    async def save(self, order: TradingOrder):
        """Order के events को save करता है"""
        uncommitted_events = order.get_uncommitted_events()
        
        for event in uncommitted_events:
            await self.event_store.append_event(event)
        
        order.mark_events_as_committed()
        logger.info(f"Saved {len(uncommitted_events)} events for order {order.order_id}")
    
    async def get_by_id(self, order_id: str) -> Optional[TradingOrder]:
        """Order ID से order को load करता है"""
        events = await self.event_store.get_events(order_id)
        
        if not events:
            return None
        
        order = TradingOrder(order_id)
        order.load_from_history(events)
        
        return order

# Demo और Testing
async def demo_zerodha_trading():
    """Zerodha trading का demo"""
    print("🏪 Zerodha Trading Event Store Demo शुरू कर रहे हैं...")
    
    # Event store setup करते हैं
    event_store = SQLiteEventStore("zerodha_demo.db")
    repository = TradingOrderRepository(event_store)
    
    # नया order बनाते हैं
    order_id = "ORD_" + str(uuid.uuid4())[:8]
    order = TradingOrder(order_id)
    
    print(f"\n📋 Order {order_id} बना रहे हैं...")
    
    # Order place करते हैं
    order.place_order(
        symbol="RELIANCE",
        quantity=10,
        price=2500.0,
        order_type="BUY",
        user_id="USER_123"
    )
    
    print(f"✅ Order placed: {order.symbol} - {order.quantity} shares @ ₹{order.price}")
    
    # Repository में save करते हैं
    await repository.save(order)
    
    # Order को execute करते हैं
    order.execute_order(executed_price=2505.0, executed_quantity=10)
    print(f"🎯 Order executed: ₹{order.executed_price} पर {order.executed_quantity} shares")
    
    # फिर से save करते हैं
    await repository.save(order)
    
    # Events retrieve करके check करते हैं
    print(f"\n📜 Order {order_id} का event history:")
    events = await event_store.get_events(order_id)
    for i, event in enumerate(events, 1):
        print(f"{i}. {event.event_type}: {event.data}")
    
    # Order को दोबारा load करके verify करते हैं
    print(f"\n🔄 Order को दोबारा load कर रहे हैं...")
    loaded_order = await repository.get_by_id(order_id)
    print(f"Loaded order status: {loaded_order.status}")
    print(f"Loaded order symbol: {loaded_order.symbol}")
    print(f"Loaded order executed price: ₹{loaded_order.executed_price}")
    
    # Event type wise query करते हैं
    print(f"\n📊 सभी ORDER_EXECUTED events:")
    executed_events = await event_store.get_events_by_type("ORDER_EXECUTED")
    for event in executed_events:
        print(f"- Order {event.aggregate_id}: ₹{event.data['executed_price']}")

if __name__ == "__main__":
    import asyncio
    
    print("Event Store Implementation Demo")
    print("=" * 50)
    
    asyncio.run(demo_zerodha_trading())