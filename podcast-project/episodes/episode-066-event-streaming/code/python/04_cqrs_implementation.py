"""
Event Streaming Episode - CQRS (Command Query Responsibility Segregation) Implementation
Production-ready CQRS pattern with separate read/write models for Flipkart-like e-commerce

Author: Hindi Tech Podcast Series
"""

import json
import uuid
import logging
import asyncio
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Command और Event definitions
class CommandType(Enum):
    """Command types for e-commerce operations"""
    CREATE_PRODUCT = "CREATE_PRODUCT"
    UPDATE_INVENTORY = "UPDATE_INVENTORY"
    PLACE_ORDER = "PLACE_ORDER"
    CANCEL_ORDER = "CANCEL_ORDER"
    UPDATE_PRICE = "UPDATE_PRICE"
    ADD_REVIEW = "ADD_REVIEW"

class EventType(Enum):
    """Event types generated from commands"""
    PRODUCT_CREATED = "PRODUCT_CREATED"
    INVENTORY_UPDATED = "INVENTORY_UPDATED"
    ORDER_PLACED = "ORDER_PLACED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    PRICE_UPDATED = "PRICE_UPDATED"
    REVIEW_ADDED = "REVIEW_ADDED"

@dataclass
class Command:
    """
    Command - Write operations के लिए
    CQRS में commands state को modify करने के लिए use होते हैं
    """
    command_id: str
    command_type: CommandType
    aggregate_id: str
    payload: Dict[str, Any]
    user_id: str
    timestamp: str
    correlation_id: Optional[str] = None

@dataclass 
class Event:
    """
    Event - State changes को represent करने के लिए
    Commands successfully execute होने पर events generate होते हैं
    """
    event_id: str
    event_type: EventType
    aggregate_id: str
    event_data: Dict[str, Any]
    timestamp: str
    user_id: str
    correlation_id: Optional[str] = None
    version: int = 1

# Command Handlers - Write Side
class CommandHandler(ABC):
    """Abstract base class for command handlers"""
    
    @abstractmethod
    def handle(self, command: Command) -> List[Event]:
        """Command को handle करके events return करते हैं"""
        pass

class ProductCommandHandler(CommandHandler):
    """
    Product related commands handle करता है
    Write side का part है - state modifications के लिए
    """
    
    def __init__(self):
        self.products = {}  # In-memory store for demo, production में database होगा
        logger.info("🛍️ Product Command Handler initialized")
    
    def handle(self, command: Command) -> List[Event]:
        """Product commands को handle करके appropriate events generate करते हैं"""
        try:
            if command.command_type == CommandType.CREATE_PRODUCT:
                return self._handle_create_product(command)
            elif command.command_type == CommandType.UPDATE_INVENTORY:
                return self._handle_update_inventory(command)
            elif command.command_type == CommandType.UPDATE_PRICE:
                return self._handle_update_price(command)
            else:
                logger.error(f"Unsupported command type: {command.command_type}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error handling command {command.command_id}: {e}")
            return []
    
    def _handle_create_product(self, command: Command) -> List[Event]:
        """नया product create करने का command handle करते हैं"""
        payload = command.payload
        product_id = command.aggregate_id
        
        # Validation
        if product_id in self.products:
            logger.error(f"Product {product_id} already exists")
            return []
        
        # Product create करें
        product = {
            'product_id': product_id,
            'name': payload['name'],
            'category': payload['category'],
            'brand': payload['brand'],
            'price': payload['price'],
            'inventory': payload.get('inventory', 0),
            'description': payload.get('description', ''),
            'created_at': command.timestamp,
            'created_by': command.user_id
        }
        
        self.products[product_id] = product
        
        # Event generate करें
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRODUCT_CREATED,
            aggregate_id=product_id,
            event_data=product,
            timestamp=command.timestamp,
            user_id=command.user_id,
            correlation_id=command.correlation_id
        )
        
        logger.info(f"✅ Product created: {payload['name']} (ID: {product_id})")
        return [event]
    
    def _handle_update_inventory(self, command: Command) -> List[Event]:
        """Inventory update करने का command handle करते हैं"""
        product_id = command.aggregate_id
        payload = command.payload
        
        if product_id not in self.products:
            logger.error(f"Product {product_id} not found")
            return []
        
        old_inventory = self.products[product_id]['inventory']
        new_inventory = payload['new_inventory']
        operation = payload.get('operation', 'SET')  # SET, ADD, SUBTRACT
        
        if operation == 'ADD':
            new_inventory = old_inventory + payload['quantity']
        elif operation == 'SUBTRACT':
            new_inventory = max(0, old_inventory - payload['quantity'])
        
        self.products[product_id]['inventory'] = new_inventory
        
        event_data = {
            'product_id': product_id,
            'old_inventory': old_inventory,
            'new_inventory': new_inventory,
            'operation': operation,
            'reason': payload.get('reason', 'MANUAL_UPDATE')
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.INVENTORY_UPDATED,
            aggregate_id=product_id,
            event_data=event_data,
            timestamp=command.timestamp,
            user_id=command.user_id,
            correlation_id=command.correlation_id
        )
        
        logger.info(f"📦 Inventory updated: {product_id} ({old_inventory} → {new_inventory})")
        return [event]
    
    def _handle_update_price(self, command: Command) -> List[Event]:
        """Price update करने का command handle करते हैं"""
        product_id = command.aggregate_id
        payload = command.payload
        
        if product_id not in self.products:
            logger.error(f"Product {product_id} not found")
            return []
        
        old_price = self.products[product_id]['price']
        new_price = payload['new_price']
        
        self.products[product_id]['price'] = new_price
        
        event_data = {
            'product_id': product_id,
            'old_price': old_price,
            'new_price': new_price,
            'reason': payload.get('reason', 'PRICE_UPDATE'),
            'discount_percentage': payload.get('discount_percentage', 0)
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRICE_UPDATED,
            aggregate_id=product_id,
            event_data=event_data,
            timestamp=command.timestamp,
            user_id=command.user_id,
            correlation_id=command.correlation_id
        )
        
        logger.info(f"💰 Price updated: {product_id} (₹{old_price} → ₹{new_price})")
        return [event]

class OrderCommandHandler(CommandHandler):
    """
    Order related commands handle करता है
    Complex business logic के साथ order processing
    """
    
    def __init__(self, product_handler: ProductCommandHandler):
        self.orders = {}
        self.product_handler = product_handler
        logger.info("🛒 Order Command Handler initialized")
    
    def handle(self, command: Command) -> List[Event]:
        """Order commands को handle करते हैं"""
        try:
            if command.command_type == CommandType.PLACE_ORDER:
                return self._handle_place_order(command)
            elif command.command_type == CommandType.CANCEL_ORDER:
                return self._handle_cancel_order(command)
            else:
                logger.error(f"Unsupported command type: {command.command_type}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error handling order command {command.command_id}: {e}")
            return []
    
    def _handle_place_order(self, command: Command) -> List[Event]:
        """Order placement का complex logic handle करते हैं"""
        payload = command.payload
        order_id = command.aggregate_id
        
        # Order validation
        items = payload['items']
        total_amount = 0
        events = []
        
        # हर item के लिए inventory check करें
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if product_id not in self.product_handler.products:
                logger.error(f"Product {product_id} not found")
                return []
            
            product = self.product_handler.products[product_id]
            
            # Inventory check
            if product['inventory'] < quantity:
                logger.error(f"Insufficient inventory for {product_id}: "
                           f"requested {quantity}, available {product['inventory']}")
                return []
            
            total_amount += product['price'] * quantity
        
        # Order create करें
        order = {
            'order_id': order_id,
            'user_id': command.user_id,
            'items': items,
            'total_amount': total_amount,
            'status': 'PLACED',
            'delivery_address': payload['delivery_address'],
            'payment_method': payload['payment_method'],
            'created_at': command.timestamp
        }
        
        self.orders[order_id] = order
        
        # Order placed event
        order_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ORDER_PLACED,
            aggregate_id=order_id,
            event_data=order,
            timestamp=command.timestamp,
            user_id=command.user_id,
            correlation_id=command.correlation_id
        )
        
        events.append(order_event)
        
        # Inventory decrease करने के लिए commands generate करें
        for item in items:
            inventory_command = Command(
                command_id=str(uuid.uuid4()),
                command_type=CommandType.UPDATE_INVENTORY,
                aggregate_id=item['product_id'],
                payload={
                    'operation': 'SUBTRACT',
                    'quantity': item['quantity'],
                    'reason': f'ORDER_PLACED_{order_id}'
                },
                user_id=command.user_id,
                timestamp=command.timestamp,
                correlation_id=order_id
            )
            
            # Inventory update events generate करें
            inventory_events = self.product_handler.handle(inventory_command)
            events.extend(inventory_events)
        
        logger.info(f"🛒 Order placed: {order_id} with {len(items)} items, "
                   f"total ₹{total_amount}")
        return events
    
    def _handle_cancel_order(self, command: Command) -> List[Event]:
        """Order cancellation handle करते हैं with inventory restoration"""
        order_id = command.aggregate_id
        payload = command.payload
        
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return []
        
        order = self.orders[order_id]
        
        if order['status'] != 'PLACED':
            logger.error(f"Order {order_id} cannot be cancelled, status: {order['status']}")
            return []
        
        # Order status update करें
        order['status'] = 'CANCELLED'
        order['cancelled_at'] = command.timestamp
        order['cancellation_reason'] = payload.get('reason', 'USER_CANCELLED')
        
        events = []
        
        # Order cancelled event
        cancel_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ORDER_CANCELLED,
            aggregate_id=order_id,
            event_data={
                'order_id': order_id,
                'cancellation_reason': order['cancellation_reason'],
                'cancelled_at': command.timestamp,
                'refund_amount': order['total_amount']
            },
            timestamp=command.timestamp,
            user_id=command.user_id,
            correlation_id=command.correlation_id
        )
        
        events.append(cancel_event)
        
        # Inventory restore करने के लिए commands generate करें
        for item in order['items']:
            inventory_command = Command(
                command_id=str(uuid.uuid4()),
                command_type=CommandType.UPDATE_INVENTORY,
                aggregate_id=item['product_id'],
                payload={
                    'operation': 'ADD',
                    'quantity': item['quantity'],
                    'reason': f'ORDER_CANCELLED_{order_id}'
                },
                user_id=command.user_id,
                timestamp=command.timestamp,
                correlation_id=order_id
            )
            
            inventory_events = self.product_handler.handle(inventory_command)
            events.extend(inventory_events)
        
        logger.info(f"❌ Order cancelled: {order_id}, inventory restored")
        return events

# Read Models - Query Side
class ProductReadModel:
    """
    Product का read-optimized model
    Query performance के लिए denormalized data
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        logger.info("📚 Product Read Model initialized")
    
    def _init_database(self):
        """Read model database schema initialize करें"""
        with sqlite3.connect(self.db_path) as conn:
            # Products table - Query optimized
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products_read (
                    product_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    price REAL NOT NULL,
                    inventory INTEGER NOT NULL,
                    description TEXT,
                    rating REAL DEFAULT 0.0,
                    review_count INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT,
                    
                    -- Denormalized fields for fast queries
                    is_available BOOLEAN DEFAULT TRUE,
                    price_category TEXT,  -- BUDGET, MID_RANGE, PREMIUM
                    popularity_score REAL DEFAULT 0.0
                )
            """)
            
            # Indexes for fast queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON products_read (category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_brand ON products_read (brand)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price ON products_read (price)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_availability ON products_read (is_available)")
            
            # Order summary table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS order_summary_read (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    item_count INTEGER NOT NULL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_orders ON order_summary_read (user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_order_status ON order_summary_read (status)")
            
            conn.commit()
    
    def update_from_event(self, event: Event):
        """Event से read model को update करते हैं"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    if event.event_type == EventType.PRODUCT_CREATED:
                        self._handle_product_created(conn, event)
                    elif event.event_type == EventType.INVENTORY_UPDATED:
                        self._handle_inventory_updated(conn, event)
                    elif event.event_type == EventType.PRICE_UPDATED:
                        self._handle_price_updated(conn, event)
                    elif event.event_type == EventType.ORDER_PLACED:
                        self._handle_order_placed(conn, event)
                    elif event.event_type == EventType.ORDER_CANCELLED:
                        self._handle_order_cancelled(conn, event)
                    
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"❌ Error updating read model from event {event.event_id}: {e}")
    
    def _handle_product_created(self, conn, event: Event):
        """Product creation event handle करते हैं"""
        data = event.event_data
        
        # Price category determine करें
        price_category = "BUDGET" if data['price'] < 1000 else \
                        "MID_RANGE" if data['price'] < 5000 else "PREMIUM"
        
        conn.execute("""
            INSERT INTO products_read 
            (product_id, name, category, brand, price, inventory, description,
             created_at, updated_at, is_available, price_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['product_id'], data['name'], data['category'], data['brand'],
            data['price'], data['inventory'], data['description'],
            data['created_at'], event.timestamp,
            data['inventory'] > 0, price_category
        ))
        
        logger.info(f"📚 Read model updated: Product {data['product_id']} created")
    
    def _handle_inventory_updated(self, conn, event: Event):
        """Inventory update event handle करते हैं"""
        data = event.event_data
        product_id = data['product_id']
        new_inventory = data['new_inventory']
        
        conn.execute("""
            UPDATE products_read 
            SET inventory = ?, is_available = ?, updated_at = ?
            WHERE product_id = ?
        """, (new_inventory, new_inventory > 0, event.timestamp, product_id))
        
        logger.info(f"📦 Read model updated: Inventory for {product_id} = {new_inventory}")
    
    def _handle_price_updated(self, conn, event: Event):
        """Price update event handle करते हैं"""
        data = event.event_data
        product_id = data['product_id']
        new_price = data['new_price']
        
        # Price category recalculate करें
        price_category = "BUDGET" if new_price < 1000 else \
                        "MID_RANGE" if new_price < 5000 else "PREMIUM"
        
        conn.execute("""
            UPDATE products_read 
            SET price = ?, price_category = ?, updated_at = ?
            WHERE product_id = ?
        """, (new_price, price_category, event.timestamp, product_id))
        
        logger.info(f"💰 Read model updated: Price for {product_id} = ₹{new_price}")
    
    def _handle_order_placed(self, conn, event: Event):
        """Order placement event handle करते हैं"""
        data = event.event_data
        
        # Order summary add करें
        conn.execute("""
            INSERT INTO order_summary_read 
            (order_id, user_id, total_amount, status, item_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['order_id'], data['user_id'], data['total_amount'],
            data['status'], len(data['items']), data['created_at'], event.timestamp
        ))
        
        # Product popularity score update करें
        for item in data['items']:
            conn.execute("""
                UPDATE products_read 
                SET popularity_score = popularity_score + ?
                WHERE product_id = ?
            """, (item['quantity'] * 0.1, item['product_id']))  # Simple popularity scoring
        
        logger.info(f"🛒 Read model updated: Order {data['order_id']} placed")
    
    def _handle_order_cancelled(self, conn, event: Event):
        """Order cancellation event handle करते हैं"""
        data = event.event_data
        order_id = data['order_id']
        
        conn.execute("""
            UPDATE order_summary_read 
            SET status = 'CANCELLED', updated_at = ?
            WHERE order_id = ?
        """, (event.timestamp, order_id))
        
        logger.info(f"❌ Read model updated: Order {order_id} cancelled")
    
    # Query methods - Read side optimized queries
    def search_products(self, query: str = "", category: str = "", 
                       brand: str = "", min_price: float = 0, 
                       max_price: float = float('inf'),
                       available_only: bool = True) -> List[Dict[str, Any]]:
        """
        Product search with multiple filters
        Read model optimized query performance के लिए
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                sql = "SELECT * FROM products_read WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND (name LIKE ? OR description LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                if brand:
                    sql += " AND brand = ?"
                    params.append(brand)
                
                if min_price > 0:
                    sql += " AND price >= ?"
                    params.append(min_price)
                
                if max_price < float('inf'):
                    sql += " AND price <= ?"
                    params.append(max_price)
                
                if available_only:
                    sql += " AND is_available = TRUE"
                
                sql += " ORDER BY popularity_score DESC, rating DESC"
                
                cursor = conn.execute(sql, params)
                results = [dict(row) for row in cursor.fetchall()]
                
                logger.info(f"🔍 Product search completed: {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"❌ Error in product search: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Single product retrieve करते हैं by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute(
                    "SELECT * FROM products_read WHERE product_id = ?",
                    (product_id,)
                )
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"❌ Error getting product {product_id}: {e}")
            return None
    
    def get_user_orders(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """User के orders retrieve करते हैं"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM order_summary_read 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
                
                results = [dict(row) for row in cursor.fetchall()]
                
                logger.info(f"📋 Retrieved {len(results)} orders for user {user_id}")
                return results
                
        except Exception as e:
            logger.error(f"❌ Error getting orders for user {user_id}: {e}")
            return []

class CQRSEventBus:
    """
    Event Bus - Commands को handle करके events को read models में propagate करता है
    CQRS pattern का central coordination point
    """
    
    def __init__(self):
        self.command_handlers = {}
        self.event_handlers = []
        self.event_store = []  # Simple in-memory store for demo
        self.executor = ThreadPoolExecutor(max_workers=4)
        logger.info("🚌 CQRS Event Bus initialized")
    
    def register_command_handler(self, command_type: CommandType, 
                                handler: CommandHandler):
        """Command handler register करते हैं"""
        self.command_handlers[command_type] = handler
        logger.info(f"📝 Command handler registered for {command_type.value}")
    
    def register_event_handler(self, handler):
        """Event handler register करते हैं (read models को update करने के लिए)"""
        self.event_handlers.append(handler)
        logger.info(f"📖 Event handler registered: {handler.__class__.__name__}")
    
    def send_command(self, command: Command) -> bool:
        """
        Command send करते हैं और processing initiate करते हैं
        CQRS write side का entry point
        """
        try:
            if command.command_type not in self.command_handlers:
                logger.error(f"No handler found for command {command.command_type}")
                return False
            
            handler = self.command_handlers[command.command_type]
            
            logger.info(f"📨 Processing command: {command.command_type.value} "
                       f"(ID: {command.command_id})")
            
            # Command handle करके events generate करें
            events = handler.handle(command)
            
            if not events:
                logger.warning(f"No events generated for command {command.command_id}")
                return False
            
            # Events को store करें और propagate करें
            for event in events:
                self._store_event(event)
                self._propagate_event(event)
            
            logger.info(f"✅ Command processed successfully: {command.command_id}, "
                       f"generated {len(events)} events")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing command {command.command_id}: {e}")
            return False
    
    def _store_event(self, event: Event):
        """Event को store में save करते हैं"""
        self.event_store.append(event)
        logger.debug(f"💾 Event stored: {event.event_type.value} (ID: {event.event_id})")
    
    def _propagate_event(self, event: Event):
        """
        Event को सभी registered handlers में propagate करते हैं
        Read models को asynchronously update करने के लिए
        """
        for handler in self.event_handlers:
            # Async में event handling करें performance के लिए
            self.executor.submit(self._handle_event_async, handler, event)
    
    def _handle_event_async(self, handler, event: Event):
        """Event को asynchronously handle करते हैं"""
        try:
            handler.update_from_event(event)
            logger.debug(f"📖 Event handled by {handler.__class__.__name__}: "
                        f"{event.event_type.value}")
        except Exception as e:
            logger.error(f"❌ Error handling event {event.event_id} "
                        f"in {handler.__class__.__name__}: {e}")
    
    def get_events(self, aggregate_id: str = None) -> List[Event]:
        """Events retrieve करते हैं debugging या replay के लिए"""
        if aggregate_id:
            return [e for e in self.event_store if e.aggregate_id == aggregate_id]
        return self.event_store.copy()

def simulate_flipkart_cqrs_operations():
    """
    Flipkart जैसे e-commerce platform के CQRS operations simulate करते हैं
    Complete write और read side demonstration के साथ
    """
    print("🛍️ Starting Flipkart CQRS Implementation Simulation...")
    print("📝 Command Query Responsibility Segregation Pattern")
    print("-" * 60)
    
    # CQRS system initialize करें
    event_bus = CQRSEventBus()
    
    # Command handlers setup करें (Write side)
    product_handler = ProductCommandHandler()
    order_handler = OrderCommandHandler(product_handler)
    
    event_bus.register_command_handler(CommandType.CREATE_PRODUCT, product_handler)
    event_bus.register_command_handler(CommandType.UPDATE_INVENTORY, product_handler)
    event_bus.register_command_handler(CommandType.UPDATE_PRICE, product_handler)
    event_bus.register_command_handler(CommandType.PLACE_ORDER, order_handler)
    event_bus.register_command_handler(CommandType.CANCEL_ORDER, order_handler)
    
    # Read models setup करें (Query side)
    product_read_model = ProductReadModel("flipkart_cqrs.db")
    event_bus.register_event_handler(product_read_model)
    
    try:
        # 1. Products create करें
        print("\n1️⃣ Creating products (Write side - Commands)...")
        
        products_to_create = [
            {
                'product_id': 'flipkart_mobile_001',
                'name': 'iPhone 15 Pro Max',
                'category': 'Electronics',
                'brand': 'Apple',
                'price': 159900.0,
                'inventory': 50,
                'description': 'Latest iPhone with A17 Pro chip'
            },
            {
                'product_id': 'flipkart_mobile_002',
                'name': 'Samsung Galaxy S24 Ultra',
                'category': 'Electronics',
                'brand': 'Samsung',
                'price': 124999.0,
                'inventory': 75,
                'description': 'Premium Android smartphone with S Pen'
            },
            {
                'product_id': 'flipkart_book_001',
                'name': 'Clean Code',
                'category': 'Books',
                'brand': 'Pearson',
                'price': 599.0,
                'inventory': 200,
                'description': 'A Handbook of Agile Software Craftsmanship'
            }
        ]
        
        for product_data in products_to_create:
            command = Command(
                command_id=str(uuid.uuid4()),
                command_type=CommandType.CREATE_PRODUCT,
                aggregate_id=product_data['product_id'],
                payload=product_data,
                user_id='admin_001',
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            success = event_bus.send_command(command)
            print(f"   {'✅' if success else '❌'} Product: {product_data['name']}")
        
        # 2. Query products (Read side)
        print("\n2️⃣ Querying products (Read side - Queries)...")
        
        # Search all products
        all_products = product_read_model.search_products()
        print(f"   📱 Total products: {len(all_products)}")
        
        for product in all_products:
            print(f"      {product['name']} - ₹{product['price']} "
                 f"(Stock: {product['inventory']})")
        
        # Search by category
        electronics = product_read_model.search_products(category="Electronics")
        print(f"   🔌 Electronics: {len(electronics)} products")
        
        # Search by price range
        budget_products = product_read_model.search_products(max_price=1000)
        print(f"   💰 Budget products (< ₹1000): {len(budget_products)} products")
        
        # 3. Update inventory और prices
        print("\n3️⃣ Updating inventory and prices (Write side)...")
        
        # Inventory update
        inventory_command = Command(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.UPDATE_INVENTORY,
            aggregate_id='flipkart_mobile_001',
            payload={
                'operation': 'SUBTRACT',
                'quantity': 10,
                'reason': 'BULK_SALE'
            },
            user_id='admin_001',
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        success = event_bus.send_command(inventory_command)
        print(f"   {'✅' if success else '❌'} Inventory updated for iPhone")
        
        # Price update (festival sale)
        price_command = Command(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.UPDATE_PRICE,
            aggregate_id='flipkart_mobile_002',
            payload={
                'new_price': 99999.0,
                'reason': 'DIWALI_SALE',
                'discount_percentage': 20
            },
            user_id='admin_001',
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        success = event_bus.send_command(price_command)
        print(f"   {'✅' if success else '❌'} Price updated for Samsung Galaxy")
        
        # 4. Place orders
        print("\n4️⃣ Placing orders (Write side - Complex commands)...")
        
        order_command = Command(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.PLACE_ORDER,
            aggregate_id='order_flipkart_001',
            payload={
                'items': [
                    {'product_id': 'flipkart_mobile_001', 'quantity': 1},
                    {'product_id': 'flipkart_book_001', 'quantity': 2}
                ],
                'delivery_address': 'Mumbai, Bandra West, 400050',
                'payment_method': 'UPI'
            },
            user_id='user_mumbai_001',
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        success = event_bus.send_command(order_command)
        print(f"   {'✅' if success else '❌'} Order placed with multiple items")
        
        # 5. Check updated product data (Read side)
        print("\n5️⃣ Checking updated data (Read side - Post-transaction queries)...")
        
        # Check inventory after order
        iphone = product_read_model.get_product_by_id('flipkart_mobile_001')
        if iphone:
            print(f"   📱 iPhone inventory after order: {iphone['inventory']} units")
        
        # Check user orders
        user_orders = product_read_model.get_user_orders('user_mumbai_001')
        print(f"   🛒 User orders: {len(user_orders)}")
        
        for order in user_orders:
            print(f"      Order {order['order_id']}: ₹{order['total_amount']} "
                 f"({order['status']})")
        
        # 6. Cancel an order
        print("\n6️⃣ Cancelling order (Write side - Compensating action)...")
        
        cancel_command = Command(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.CANCEL_ORDER,
            aggregate_id='order_flipkart_001',
            payload={
                'reason': 'USER_CANCELLED'
            },
            user_id='user_mumbai_001',
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        success = event_bus.send_command(cancel_command)
        print(f"   {'✅' if success else '❌'} Order cancelled")
        
        # Check inventory restoration
        iphone_after_cancel = product_read_model.get_product_by_id('flipkart_mobile_001')
        if iphone_after_cancel:
            print(f"   📱 iPhone inventory after cancellation: "
                 f"{iphone_after_cancel['inventory']} units")
        
        # 7. Event sourcing demonstration
        print("\n7️⃣ Event Sourcing View (Complete audit trail)...")
        
        all_events = event_bus.get_events()
        print(f"   📚 Total events in system: {len(all_events)}")
        
        # Group events by type
        event_counts = {}
        for event in all_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print("   📊 Event breakdown:")
        for event_type, count in event_counts.items():
            print(f"      {event_type}: {count} events")
        
        # Show recent events
        print("   ⏰ Recent events:")
        for event in all_events[-5:]:
            print(f"      {event.timestamp[:19]} - {event.event_type.value} "
                 f"(Aggregate: {event.aggregate_id})")
        
        print(f"\n✅ CQRS Implementation demonstration completed!")
        print(f"💡 Key benefits demonstrated:")
        print(f"   - Separate write and read models for optimal performance")
        print(f"   - Command/Query separation for better scalability")
        print(f"   - Event-driven architecture for loose coupling")
        print(f"   - Complete audit trail through event sourcing")
        print(f"   - Read model optimization for query performance")
        
    except Exception as e:
        logger.error(f"❌ Error in CQRS simulation: {e}")
        print(f"❌ Simulation failed: {e}")

if __name__ == "__main__":
    simulate_flipkart_cqrs_operations()