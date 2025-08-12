#!/usr/bin/env python3
"""
CQRS (Command Query Responsibility Segregation) Pattern
उदाहरण: Amazon India के product catalog के लिए CQRS implementation

Setup:
pip install asyncio dataclasses sqlite3

Indian Context: Amazon India app में:
- Write Side: Product updates, inventory changes, pricing updates
- Read Side: Product search, recommendations, analytics queries
- Event Store: सभी changes को events के रूप में store करना

CQRS Benefits:
- Read/Write optimized separately
- Complex queries without affecting writes
- Different databases for different needs
- Event-driven synchronization
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
import random

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Command types for write operations"""
    CREATE_PRODUCT = "create_product"
    UPDATE_PRICE = "update_price"
    UPDATE_INVENTORY = "update_inventory"
    UPDATE_PRODUCT_INFO = "update_product_info"
    DEACTIVATE_PRODUCT = "deactivate_product"

class EventType(Enum):
    """Event types generated from commands"""
    PRODUCT_CREATED = "product_created"
    PRICE_UPDATED = "price_updated"
    INVENTORY_UPDATED = "inventory_updated"
    PRODUCT_INFO_UPDATED = "product_info_updated"
    PRODUCT_DEACTIVATED = "product_deactivated"

@dataclass
class Command:
    """Command structure for write operations"""
    command_id: str
    command_type: CommandType
    aggregate_id: str  # Product ID
    payload: Dict[str, Any]
    user_id: str
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Event:
    """Event structure for event store"""
    event_id: str
    event_type: EventType
    aggregate_id: str
    event_data: Dict[str, Any]
    version: int
    timestamp: str = None
    correlation_id: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Product:
    """Product aggregate for write model"""
    product_id: str
    seller_id: str
    name: str
    description: str
    category: str
    price: float
    inventory: int
    is_active: bool = True
    version: int = 0
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class EventStore:
    """
    Event store for CQRS
    Bank passbook की तरह - हर transaction का record
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize event store database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                event_data TEXT NOT NULL,
                version INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                correlation_id TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_aggregate_events ON events(aggregate_id, version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Event store initialized")
    
    async def append_event(self, event: Event) -> bool:
        """Append event to store"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (event_id, event_type, aggregate_id, event_data, version, timestamp, correlation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.event_type.value,
                event.aggregate_id,
                json.dumps(event.event_data),
                event.version,
                event.timestamp,
                event.correlation_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📝 Event stored: {event.event_type.value} for {event.aggregate_id}")
            return True
            
        except sqlite3.IntegrityError:
            logger.error(f"❌ Duplicate event: {event.event_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to store event: {e}")
            return False
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for aggregate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_id, event_type, aggregate_id, event_data, version, timestamp, correlation_id
            FROM events
            WHERE aggregate_id = ? AND version > ?
            ORDER BY version ASC
        ''', (aggregate_id, from_version))
        
        events = []
        for row in cursor.fetchall():
            event = Event(
                event_id=row[0],
                event_type=EventType(row[1]),
                aggregate_id=row[2],
                event_data=json.loads(row[3]),
                version=row[4],
                timestamp=row[5],
                correlation_id=row[6]
            )
            events.append(event)
        
        conn.close()
        return events
    
    async def get_all_events(self, limit: int = 100) -> List[Event]:
        """Get all events for read model projection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_id, event_type, aggregate_id, event_data, version, timestamp, correlation_id
            FROM events
            ORDER BY id ASC
            LIMIT ?
        ''', (limit,))
        
        events = []
        for row in cursor.fetchall():
            event = Event(
                event_id=row[0],
                event_type=EventType(row[1]),
                aggregate_id=row[2],
                event_data=json.loads(row[3]),
                version=row[4],
                timestamp=row[5],
                correlation_id=row[6]
            )
            events.append(event)
        
        conn.close()
        return events

class WriteModel:
    """
    Write model - handles commands and generates events
    Amazon warehouse की तरह - products को add/update करना
    """
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.products: Dict[str, Product] = {}  # In-memory aggregate store
    
    async def handle_command(self, command: Command) -> bool:
        """Handle write commands"""
        logger.info(f"⚙️ Handling command: {command.command_type.value} for {command.aggregate_id}")
        
        try:
            if command.command_type == CommandType.CREATE_PRODUCT:
                return await self._handle_create_product(command)
            elif command.command_type == CommandType.UPDATE_PRICE:
                return await self._handle_update_price(command)
            elif command.command_type == CommandType.UPDATE_INVENTORY:
                return await self._handle_update_inventory(command)
            elif command.command_type == CommandType.UPDATE_PRODUCT_INFO:
                return await self._handle_update_product_info(command)
            elif command.command_type == CommandType.DEACTIVATE_PRODUCT:
                return await self._handle_deactivate_product(command)
            else:
                logger.error(f"❌ Unknown command type: {command.command_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Command handling failed: {e}")
            return False
    
    async def _handle_create_product(self, command: Command) -> bool:
        """Handle product creation"""
        payload = command.payload
        product_id = command.aggregate_id
        
        # Validation
        if product_id in self.products:
            raise Exception(f"Product already exists: {product_id}")
        
        # Create product aggregate
        product = Product(
            product_id=product_id,
            seller_id=payload['seller_id'],
            name=payload['name'],
            description=payload['description'],
            category=payload['category'],
            price=payload['price'],
            inventory=payload['inventory']
        )
        
        # Generate event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRODUCT_CREATED,
            aggregate_id=product_id,
            event_data=asdict(product),
            version=1,
            correlation_id=command.command_id
        )
        
        # Store event
        success = await self.event_store.append_event(event)
        if success:
            self.products[product_id] = product
            logger.info(f"✅ Product created: {product.name} by {product.seller_id}")
        
        return success
    
    async def _handle_update_price(self, command: Command) -> bool:
        """Handle price update"""
        product_id = command.aggregate_id
        new_price = command.payload['new_price']
        
        # Get current product state
        product = await self._get_or_rebuild_product(product_id)
        if not product:
            raise Exception(f"Product not found: {product_id}")
        
        if not product.is_active:
            raise Exception(f"Cannot update price for inactive product: {product_id}")
        
        old_price = product.price
        product.price = new_price
        product.version += 1
        product.updated_at = datetime.now().isoformat()
        
        # Generate event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRICE_UPDATED,
            aggregate_id=product_id,
            event_data={
                'old_price': old_price,
                'new_price': new_price,
                'updated_by': command.user_id
            },
            version=product.version,
            correlation_id=command.command_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            self.products[product_id] = product
            logger.info(f"💰 Price updated: {product.name} ₹{old_price} → ₹{new_price}")
        
        return success
    
    async def _handle_update_inventory(self, command: Command) -> bool:
        """Handle inventory update"""
        product_id = command.aggregate_id
        quantity_change = command.payload['quantity_change']
        
        product = await self._get_or_rebuild_product(product_id)
        if not product:
            raise Exception(f"Product not found: {product_id}")
        
        old_inventory = product.inventory
        new_inventory = old_inventory + quantity_change
        
        if new_inventory < 0:
            raise Exception(f"Insufficient inventory: {old_inventory} + {quantity_change} < 0")
        
        product.inventory = new_inventory
        product.version += 1
        product.updated_at = datetime.now().isoformat()
        
        # Generate event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.INVENTORY_UPDATED,
            aggregate_id=product_id,
            event_data={
                'old_inventory': old_inventory,
                'new_inventory': new_inventory,
                'quantity_change': quantity_change,
                'updated_by': command.user_id
            },
            version=product.version,
            correlation_id=command.command_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            self.products[product_id] = product
            logger.info(f"📦 Inventory updated: {product.name} {old_inventory} → {new_inventory}")
        
        return success
    
    async def _handle_update_product_info(self, command: Command) -> bool:
        """Handle product information update"""
        product_id = command.aggregate_id
        payload = command.payload
        
        product = await self._get_or_rebuild_product(product_id)
        if not product:
            raise Exception(f"Product not found: {product_id}")
        
        # Update fields
        changes = {}
        if 'name' in payload and payload['name'] != product.name:
            changes['old_name'] = product.name
            changes['new_name'] = payload['name']
            product.name = payload['name']
        
        if 'description' in payload and payload['description'] != product.description:
            changes['old_description'] = product.description
            changes['new_description'] = payload['description']
            product.description = payload['description']
        
        if 'category' in payload and payload['category'] != product.category:
            changes['old_category'] = product.category
            changes['new_category'] = payload['category']
            product.category = payload['category']
        
        if not changes:
            logger.info("ℹ️ No changes detected in product info update")
            return True
        
        product.version += 1
        product.updated_at = datetime.now().isoformat()
        
        # Generate event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRODUCT_INFO_UPDATED,
            aggregate_id=product_id,
            event_data={
                'changes': changes,
                'updated_by': command.user_id
            },
            version=product.version,
            correlation_id=command.command_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            self.products[product_id] = product
            logger.info(f"📝 Product info updated: {product.name}")
        
        return success
    
    async def _handle_deactivate_product(self, command: Command) -> bool:
        """Handle product deactivation"""
        product_id = command.aggregate_id
        
        product = await self._get_or_rebuild_product(product_id)
        if not product:
            raise Exception(f"Product not found: {product_id}")
        
        if not product.is_active:
            logger.info(f"ℹ️ Product already inactive: {product_id}")
            return True
        
        product.is_active = False
        product.version += 1
        product.updated_at = datetime.now().isoformat()
        
        # Generate event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRODUCT_DEACTIVATED,
            aggregate_id=product_id,
            event_data={
                'reason': command.payload.get('reason', 'Not specified'),
                'deactivated_by': command.user_id
            },
            version=product.version,
            correlation_id=command.command_id
        )
        
        success = await self.event_store.append_event(event)
        if success:
            self.products[product_id] = product
            logger.info(f"🚫 Product deactivated: {product.name}")
        
        return success
    
    async def _get_or_rebuild_product(self, product_id: str) -> Optional[Product]:
        """Get product from memory or rebuild from events"""
        if product_id in self.products:
            return self.products[product_id]
        
        # Rebuild from events
        events = await self.event_store.get_events(product_id)
        if not events:
            return None
        
        product = None
        for event in events:
            if event.event_type == EventType.PRODUCT_CREATED:
                product = Product(**event.event_data)
            elif product and event.event_type == EventType.PRICE_UPDATED:
                product.price = event.event_data['new_price']
                product.version = event.version
            elif product and event.event_type == EventType.INVENTORY_UPDATED:
                product.inventory = event.event_data['new_inventory']
                product.version = event.version
            elif product and event.event_type == EventType.PRODUCT_INFO_UPDATED:
                changes = event.event_data['changes']
                if 'new_name' in changes:
                    product.name = changes['new_name']
                if 'new_description' in changes:
                    product.description = changes['new_description']
                if 'new_category' in changes:
                    product.category = changes['new_category']
                product.version = event.version
            elif product and event.event_type == EventType.PRODUCT_DEACTIVATED:
                product.is_active = False
                product.version = event.version
        
        if product:
            self.products[product_id] = product
        
        return product

class ReadModel:
    """
    Read model - optimized for queries
    Amazon search page की तरह - fast product searches
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_read_database()
    
    def _init_read_database(self):
        """Initialize read model database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Product view table - optimized for searches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_view (
                product_id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                inventory INTEGER NOT NULL,
                is_active BOOLEAN NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER NOT NULL
            )
        ''')
        
        # Analytics view table - for reporting
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_analytics (
                product_id TEXT PRIMARY KEY,
                total_price_changes INTEGER DEFAULT 0,
                total_inventory_changes INTEGER DEFAULT 0,
                last_price_change TEXT,
                last_inventory_change TEXT,
                price_history TEXT,  -- JSON array
                inventory_history TEXT  -- JSON array
            )
        ''')
        
        # Indexes for fast searches
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON product_view(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_seller ON product_view(seller_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price ON product_view(price)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_active ON product_view(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name_search ON product_view(name)')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Read model database initialized")
    
    async def project_event(self, event: Event):
        """Project event to read model"""
        if event.event_type == EventType.PRODUCT_CREATED:
            await self._project_product_created(event)
        elif event.event_type == EventType.PRICE_UPDATED:
            await self._project_price_updated(event)
        elif event.event_type == EventType.INVENTORY_UPDATED:
            await self._project_inventory_updated(event)
        elif event.event_type == EventType.PRODUCT_INFO_UPDATED:
            await self._project_product_info_updated(event)
        elif event.event_type == EventType.PRODUCT_DEACTIVATED:
            await self._project_product_deactivated(event)
        
        logger.info(f"📊 Projected event: {event.event_type.value} for {event.aggregate_id}")
    
    async def _project_product_created(self, event: Event):
        """Project product creation"""
        product_data = event.event_data
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO product_view 
            (product_id, seller_id, name, description, category, price, inventory, 
             is_active, created_at, updated_at, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_data['product_id'],
            product_data['seller_id'],
            product_data['name'],
            product_data['description'],
            product_data['category'],
            product_data['price'],
            product_data['inventory'],
            product_data['is_active'],
            product_data['created_at'],
            product_data['updated_at'],
            product_data['version']
        ))
        
        # Initialize analytics
        cursor.execute('''
            INSERT INTO product_analytics 
            (product_id, price_history, inventory_history)
            VALUES (?, ?, ?)
        ''', (
            product_data['product_id'],
            json.dumps([product_data['price']]),
            json.dumps([product_data['inventory']])
        ))
        
        conn.commit()
        conn.close()
    
    async def _project_price_updated(self, event: Event):
        """Project price update"""
        event_data = event.event_data
        product_id = event.aggregate_id
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update product view
        cursor.execute('''
            UPDATE product_view 
            SET price = ?, updated_at = ?, version = ?
            WHERE product_id = ?
        ''', (
            event_data['new_price'],
            event.timestamp,
            event.version,
            product_id
        ))
        
        # Update analytics
        cursor.execute('SELECT price_history, total_price_changes FROM product_analytics WHERE product_id = ?', 
                      (product_id,))
        row = cursor.fetchone()
        
        if row:
            price_history = json.loads(row[0])
            price_history.append(event_data['new_price'])
            
            cursor.execute('''
                UPDATE product_analytics 
                SET total_price_changes = ?, last_price_change = ?, price_history = ?
                WHERE product_id = ?
            ''', (
                row[1] + 1,
                event.timestamp,
                json.dumps(price_history),
                product_id
            ))
        
        conn.commit()
        conn.close()
    
    async def _project_inventory_updated(self, event: Event):
        """Project inventory update"""
        event_data = event.event_data
        product_id = event.aggregate_id
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update product view
        cursor.execute('''
            UPDATE product_view 
            SET inventory = ?, updated_at = ?, version = ?
            WHERE product_id = ?
        ''', (
            event_data['new_inventory'],
            event.timestamp,
            event.version,
            product_id
        ))
        
        # Update analytics
        cursor.execute('SELECT inventory_history, total_inventory_changes FROM product_analytics WHERE product_id = ?', 
                      (product_id,))
        row = cursor.fetchone()
        
        if row:
            inventory_history = json.loads(row[0])
            inventory_history.append(event_data['new_inventory'])
            
            cursor.execute('''
                UPDATE product_analytics 
                SET total_inventory_changes = ?, last_inventory_change = ?, inventory_history = ?
                WHERE product_id = ?
            ''', (
                row[1] + 1,
                event.timestamp,
                json.dumps(inventory_history),
                product_id
            ))
        
        conn.commit()
        conn.close()
    
    async def _project_product_info_updated(self, event: Event):
        """Project product info update"""
        changes = event.event_data['changes']
        product_id = event.aggregate_id
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if 'new_name' in changes:
            updates.append('name = ?')
            params.append(changes['new_name'])
        
        if 'new_description' in changes:
            updates.append('description = ?')
            params.append(changes['new_description'])
        
        if 'new_category' in changes:
            updates.append('category = ?')
            params.append(changes['new_category'])
        
        updates.extend(['updated_at = ?', 'version = ?'])
        params.extend([event.timestamp, event.version, product_id])
        
        if updates:
            query = f"UPDATE product_view SET {', '.join(updates)} WHERE product_id = ?"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    async def _project_product_deactivated(self, event: Event):
        """Project product deactivation"""
        product_id = event.aggregate_id
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE product_view 
            SET is_active = 0, updated_at = ?, version = ?
            WHERE product_id = ?
        ''', (event.timestamp, event.version, product_id))
        
        conn.commit()
        conn.close()
    
    # Query methods for read operations
    
    async def search_products(self, query: str = None, category: str = None, 
                            seller_id: str = None, max_price: float = None,
                            active_only: bool = True) -> List[Dict[str, Any]]:
        """Search products with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_clauses = []
        params = []
        
        if active_only:
            where_clauses.append('is_active = 1')
        
        if query:
            where_clauses.append('(name LIKE ? OR description LIKE ?)')
            params.extend([f'%{query}%', f'%{query}%'])
        
        if category:
            where_clauses.append('category = ?')
            params.append(category)
        
        if seller_id:
            where_clauses.append('seller_id = ?')
            params.append(seller_id)
        
        if max_price:
            where_clauses.append('price <= ?')
            params.append(max_price)
        
        where_sql = 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''
        
        query_sql = f'''
            SELECT product_id, seller_id, name, description, category, price, inventory, 
                   is_active, created_at, updated_at
            FROM product_view 
            {where_sql}
            ORDER BY updated_at DESC
            LIMIT 20
        '''
        
        cursor.execute(query_sql, params)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'product_id': row[0],
                'seller_id': row[1],
                'name': row[2],
                'description': row[3],
                'category': row[4],
                'price': row[5],
                'inventory': row[6],
                'is_active': bool(row[7]),
                'created_at': row[8],
                'updated_at': row[9]
            })
        
        conn.close()
        return products
    
    async def get_product_analytics(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, a.total_price_changes, a.total_inventory_changes,
                   a.last_price_change, a.last_inventory_change,
                   a.price_history, a.inventory_history
            FROM product_view p
            LEFT JOIN product_analytics a ON p.product_id = a.product_id
            WHERE p.product_id = ?
        ''', (product_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'product_id': row[0],
            'name': row[2],
            'category': row[4],
            'current_price': row[5],
            'current_inventory': row[6],
            'total_price_changes': row[10] or 0,
            'total_inventory_changes': row[11] or 0,
            'last_price_change': row[12],
            'last_inventory_change': row[13],
            'price_history': json.loads(row[14]) if row[14] else [],
            'inventory_history': json.loads(row[15]) if row[15] else []
        }

class EventProjector:
    """
    Event projector - syncs write model events to read model
    Mumbai local train announcements की तरह - हर station को update मिलता है
    """
    
    def __init__(self, event_store: EventStore, read_model: ReadModel):
        self.event_store = event_store
        self.read_model = read_model
        self.last_processed_event = 0
    
    async def project_all_events(self):
        """Project all events to read model"""
        events = await self.event_store.get_all_events(1000)
        
        logger.info(f"📊 Projecting {len(events)} events to read model...")
        
        for event in events:
            await self.read_model.project_event(event)
        
        logger.info("✅ All events projected to read model")

async def amazon_cqrs_demo():
    """Amazon India CQRS demo"""
    print("🛒 Amazon India CQRS Pattern Demo")
    print("=" * 50)
    
    # Initialize CQRS components
    event_store = EventStore("amazon_events.db")
    write_model = WriteModel(event_store)
    read_model = ReadModel("amazon_read.db")
    projector = EventProjector(event_store, read_model)
    
    print("🏗️ CQRS Architecture initialized")
    print("   📝 Write Model: Command handling + Event generation")
    print("   📊 Read Model: Optimized queries + Analytics")
    print("   🔄 Event Projector: Sync write→read")
    print()
    
    # Sample products for Indian market
    products = [
        {
            'product_id': 'AMZN_PHONE_001',
            'seller_id': 'SELLER_SAMSUNG',
            'name': 'Samsung Galaxy M34 5G',
            'description': 'Latest Samsung smartphone with 50MP camera',
            'category': 'Electronics',
            'price': 18999.0,
            'inventory': 150
        },
        {
            'product_id': 'AMZN_BOOK_001', 
            'seller_id': 'SELLER_PENGUIN',
            'name': 'Atomic Habits by James Clear',
            'description': 'Life-changing book about building good habits',
            'category': 'Books',
            'price': 399.0,
            'inventory': 500
        },
        {
            'product_id': 'AMZN_FOOD_001',
            'seller_id': 'SELLER_ORGANIC',
            'name': 'Organic Basmati Rice 5kg',
            'description': 'Premium quality organic basmati rice',
            'category': 'Grocery',
            'price': 850.0,
            'inventory': 200
        },
        {
            'product_id': 'AMZN_CLOTH_001',
            'seller_id': 'SELLER_FASHION',
            'name': 'Cotton Kurta for Men',
            'description': 'Traditional Indian cotton kurta',
            'category': 'Clothing',
            'price': 799.0,
            'inventory': 75
        }
    ]
    
    # WRITE SIDE: Create products using commands
    print("📝 WRITE SIDE: Creating products via commands")
    print("-" * 40)
    
    for product in products:
        command = Command(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.CREATE_PRODUCT,
            aggregate_id=product['product_id'],
            payload=product,
            user_id="ADMIN_USER"
        )
        
        success = await write_model.handle_command(command)
        if success:
            print(f"✅ Created: {product['name']} (₹{product['price']})")
        else:
            print(f"❌ Failed: {product['name']}")
    
    print()
    
    # Project events to read model
    print("🔄 PROJECTING: Events to read model")
    await projector.project_all_events()
    print()
    
    # READ SIDE: Query products
    print("📊 READ SIDE: Querying products")
    print("-" * 40)
    
    # Search all active products
    all_products = await read_model.search_products()
    print(f"🛍️ All Products ({len(all_products)}):")
    for product in all_products:
        print(f"   📱 {product['name']} - ₹{product['price']} ({product['inventory']} in stock)")
    print()
    
    # Search by category
    electronics = await read_model.search_products(category='Electronics')
    print(f"📱 Electronics ({len(electronics)}):")
    for product in electronics:
        print(f"   {product['name']} - ₹{product['price']}")
    print()
    
    # WRITE SIDE: Update operations
    print("📝 WRITE SIDE: Updating products")
    print("-" * 40)
    
    # Update price
    price_command = Command(
        command_id=str(uuid.uuid4()),
        command_type=CommandType.UPDATE_PRICE,
        aggregate_id='AMZN_PHONE_001',
        payload={'new_price': 17999.0},  # Price drop
        user_id="SELLER_SAMSUNG"
    )
    
    await write_model.handle_command(price_command)
    
    # Update inventory (sale simulation)
    inventory_command = Command(
        command_id=str(uuid.uuid4()),
        command_type=CommandType.UPDATE_INVENTORY,
        aggregate_id='AMZN_PHONE_001',
        payload={'quantity_change': -10},  # 10 units sold
        user_id="SYSTEM_SALE"
    )
    
    await write_model.handle_command(inventory_command)
    
    # Update product info
    info_command = Command(
        command_id=str(uuid.uuid4()),
        command_type=CommandType.UPDATE_PRODUCT_INFO,
        aggregate_id='AMZN_BOOK_001',
        payload={
            'name': 'Atomic Habits by James Clear (Bestseller)',
            'description': 'Life-changing book about building good habits - #1 Bestseller'
        },
        user_id="SELLER_PENGUIN"
    )
    
    await write_model.handle_command(info_command)
    
    print()
    
    # Project updates to read model
    print("🔄 PROJECTING: Updates to read model")
    await projector.project_all_events()
    print()
    
    # READ SIDE: See updated data
    print("📊 READ SIDE: Updated product data")
    print("-" * 40)
    
    # Check updated phone price
    updated_electronics = await read_model.search_products(category='Electronics')
    print("📱 Updated Electronics:")
    for product in updated_electronics:
        print(f"   {product['name']} - ₹{product['price']} ({product['inventory']} in stock)")
    print()
    
    # Analytics view
    print("📈 ANALYTICS: Product insights")
    print("-" * 40)
    
    phone_analytics = await read_model.get_product_analytics('AMZN_PHONE_001')
    if phone_analytics:
        print(f"📊 {phone_analytics['name']}:")
        print(f"   💰 Current Price: ₹{phone_analytics['current_price']}")
        print(f"   📦 Current Stock: {phone_analytics['current_inventory']}")
        print(f"   📈 Price Changes: {phone_analytics['total_price_changes']}")
        print(f"   📉 Inventory Changes: {phone_analytics['total_inventory_changes']}")
        print(f"   💹 Price History: {phone_analytics['price_history']}")
        print(f"   📊 Stock History: {phone_analytics['inventory_history']}")
    print()
    
    # Complex queries
    print("🔍 COMPLEX QUERIES: Advanced search")
    print("-" * 40)
    
    # Search by name
    books = await read_model.search_products(query='Atomic')
    print(f"📚 Books matching 'Atomic': {len(books)}")
    for book in books:
        print(f"   {book['name']} - ₹{book['price']}")
    print()
    
    # Price range filter
    budget_products = await read_model.search_products(max_price=1000.0)
    print(f"💰 Products under ₹1000: {len(budget_products)}")
    for product in budget_products:
        print(f"   {product['name']} - ₹{product['price']}")
    print()
    
    print("🎯 CQRS Benefits Demonstrated:")
    print("   ✅ Write model optimized for business logic")
    print("   ✅ Read model optimized for queries")
    print("   ✅ Event sourcing for complete audit trail")
    print("   ✅ Analytics without affecting write performance")
    print("   ✅ Independent scaling of read/write sides")
    print("   ✅ Complex queries on denormalized data")

if __name__ == "__main__":
    asyncio.run(amazon_cqrs_demo())