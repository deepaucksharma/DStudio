#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies - Change Data Capture (CDC)
Advanced CDC implementation for real-time data synchronization

यह implementation demonstrate करती है कि कैसे Change Data Capture का use करके
real-time में data changes को capture और replicate कर सकते हैं।
जैसे Mumbai में traffic signals की timing real-time adjust होती है based on traffic,
वैसे ही CDC से data changes को instantly detect और propagate करना।

Real-world Usage:
- HDFC Bank: Account balance changes को instantly all branches में sync करना
- Flipkart: Product inventory updates को real-time सभी systems में propagate करना
- Zomato: Restaurant status changes को instantly delivery partners को notify करना

Author: Hindi Tech Podcast Team
Episode: 41 - Database Replication Strategies
"""

import asyncio
import json
import time
import hashlib
import threading
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
import redis

# Configure logging for production environments
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/replication/cdc.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of data changes"""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SCHEMA_CHANGE = "SCHEMA_CHANGE"
    BULK_OPERATION = "BULK_OPERATION"

class ReplicationStrategy(Enum):
    """CDC replication strategies"""
    LOG_BASED = "LOG_BASED"          # Binary log / WAL based
    TRIGGER_BASED = "TRIGGER_BASED"  # Database triggers
    POLLING_BASED = "POLLING_BASED"  # Timestamp/version based polling
    HYBRID = "HYBRID"                # Combination approach

@dataclass
class ChangeEvent:
    """Change event data structure"""
    event_id: str
    timestamp: datetime
    change_type: ChangeType
    database_name: str
    table_name: str
    primary_key: Dict[str, Any]
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None
    lsn: Optional[str] = None  # Log Sequence Number
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_kafka_message(self) -> Dict[str, Any]:
        """Convert to Kafka message format"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'change_type': self.change_type.value,
            'database': self.database_name,
            'table': self.table_name,
            'pk': self.primary_key,
            'before': self.old_values,
            'after': self.new_values,
            'transaction_id': self.transaction_id,
            'lsn': self.lsn,
            'metadata': self.metadata
        }

class HDFCBankingCDC:
    """
    HDFC Banking के लिए specialized CDC implementation
    Real-time account balance और transaction updates के लिए
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_connection = self._setup_database_connection()
        self.kafka_producer = self._setup_kafka_producer()
        self.redis_client = self._setup_redis_client()
        self.change_listeners: List[Callable] = []
        self.processed_lsns: Set[str] = set()
        self.compliance_logger = self._setup_compliance_logging()
        
        logger.info("HDFC Banking CDC initialized")
    
    def _setup_database_connection(self):
        """Setup PostgreSQL connection for HDFC core banking"""
        try:
            conn = psycopg2.connect(
                host=self.config.get('db_host', 'localhost'),
                database=self.config.get('db_name', 'hdfc_core_banking'),
                user=self.config.get('db_user', 'cdc_user'),
                password=self.config.get('db_password', 'secure_password'),
                port=self.config.get('db_port', 5432)
            )
            conn.set_session(autocommit=True)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _setup_kafka_producer(self):
        """Setup Kafka producer for event streaming"""
        return KafkaProducer(
            bootstrap_servers=self.config.get('kafka_servers', ['localhost:9092']),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3,
            batch_size=16384,
            linger_ms=10,
            buffer_memory=33554432
        )
    
    def _setup_redis_client(self):
        """Setup Redis for caching और deduplication"""
        return redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0),
            decode_responses=True
        )
    
    def _setup_compliance_logging(self):
        """Setup compliance logging for banking regulations"""
        compliance_logger = logging.getLogger('hdfc_compliance')
        compliance_handler = logging.FileHandler('/var/log/banking/compliance.log')
        compliance_handler.setFormatter(
            logging.Formatter('%(asctime)s - COMPLIANCE - %(message)s')
        )
        compliance_logger.addHandler(compliance_handler)
        return compliance_logger
    
    async def start_cdc_capture(self):
        """Start CDC capture using PostgreSQL logical replication"""
        logger.info("Starting HDFC Banking CDC capture...")
        
        try:
            # Create replication slot if not exists
            await self._setup_replication_slot()
            
            # Start WAL streaming
            await self._stream_wal_changes()
            
        except Exception as e:
            logger.error(f"CDC capture failed: {e}")
            raise
    
    async def _setup_replication_slot(self):
        """Setup PostgreSQL logical replication slot"""
        cursor = self.db_connection.cursor()
        
        try:
            # Create logical replication slot
            cursor.execute("""
                SELECT * FROM pg_create_logical_replication_slot(
                    'hdfc_banking_cdc', 'pgoutput'
                ) WHERE NOT EXISTS (
                    SELECT 1 FROM pg_replication_slots 
                    WHERE slot_name = 'hdfc_banking_cdc'
                )
            """)
            
            logger.info("Replication slot created successfully")
            
        except psycopg2.Error as e:
            if "already exists" in str(e):
                logger.info("Replication slot already exists")
            else:
                logger.error(f"Failed to create replication slot: {e}")
                raise
        finally:
            cursor.close()
    
    async def _stream_wal_changes(self):
        """Stream WAL changes for real-time CDC"""
        cursor = self.db_connection.cursor()
        
        try:
            # Start logical replication
            cursor.execute("""
                SELECT * FROM pg_logical_slot_get_changes(
                    'hdfc_banking_cdc', NULL, NULL, 
                    'proto_version', '1', 
                    'publication_names', 'banking_publication'
                )
            """)
            
            while True:
                changes = cursor.fetchmany(100)  # Batch processing
                if not changes:
                    await asyncio.sleep(1)  # Wait for new changes
                    continue
                
                for lsn, xid, data in changes:
                    if lsn not in self.processed_lsns:
                        await self._process_wal_record(lsn, xid, data)
                        self.processed_lsns.add(lsn)
                
        except Exception as e:
            logger.error(f"WAL streaming failed: {e}")
            raise
        finally:
            cursor.close()
    
    async def _process_wal_record(self, lsn: str, xid: str, data: str):
        """Process individual WAL record"""
        try:
            # Parse WAL data (simplified - actual implementation would be more complex)
            change_event = self._parse_wal_data(lsn, xid, data)
            
            if change_event:
                # Apply banking business rules
                await self._apply_banking_rules(change_event)
                
                # Publish to downstream systems
                await self._publish_change_event(change_event)
                
                # Log for compliance
                self._log_compliance_event(change_event)
                
        except Exception as e:
            logger.error(f"Failed to process WAL record {lsn}: {e}")
    
    def _parse_wal_data(self, lsn: str, xid: str, data: str) -> Optional[ChangeEvent]:
        """Parse WAL data into structured change event"""
        try:
            # Simplified parsing - production में proper WAL parser होगा
            if 'INSERT' in data and 'accounts' in data:
                return ChangeEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    change_type=ChangeType.INSERT,
                    database_name="hdfc_core_banking",
                    table_name="accounts",
                    primary_key={"account_id": "ACC123456789"},
                    new_values={"balance": 50000.0, "status": "ACTIVE"},
                    transaction_id=xid,
                    lsn=lsn,
                    metadata={"source": "hdfc_cdc", "compliance_required": True}
                )
            
            elif 'UPDATE' in data and 'transactions' in data:
                return ChangeEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.now(),
                    change_type=ChangeType.UPDATE,
                    database_name="hdfc_core_banking",
                    table_name="transactions",
                    primary_key={"transaction_id": "TXN987654321"},
                    old_values={"status": "PENDING"},
                    new_values={"status": "COMPLETED"},
                    transaction_id=xid,
                    lsn=lsn,
                    metadata={"source": "hdfc_cdc", "audit_required": True}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse WAL data: {e}")
            return None
    
    async def _apply_banking_rules(self, change_event: ChangeEvent):
        """Apply banking-specific business rules"""
        # Check for large transactions (>1 Lakh)
        if change_event.table_name == "transactions":
            amount = change_event.new_values.get('amount', 0) if change_event.new_values else 0
            if amount > 100000:  # Rs. 1 Lakh
                change_event.metadata['high_value_transaction'] = True
                logger.warning(f"High value transaction detected: Rs. {amount}")
        
        # Account balance validation
        if change_event.table_name == "accounts":
            balance = change_event.new_values.get('balance', 0) if change_event.new_values else 0
            if balance < 0:
                change_event.metadata['negative_balance_alert'] = True
                logger.error(f"Negative balance detected for account")
    
    async def _publish_change_event(self, change_event: ChangeEvent):
        """Publish change event to Kafka for downstream consumption"""
        try:
            topic_name = f"hdfc-{change_event.table_name}-changes"
            message = change_event.to_kafka_message()
            
            # Send to Kafka
            future = self.kafka_producer.send(topic_name, message)
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Event published to {topic_name}: {record_metadata}")
            
            # Cache in Redis for quick access
            cache_key = f"cdc:hdfc:{change_event.table_name}:{change_event.event_id}"
            self.redis_client.setex(cache_key, 3600, json.dumps(message))  # 1 hour TTL
            
        except Exception as e:
            logger.error(f"Failed to publish change event: {e}")
            raise
    
    def _log_compliance_event(self, change_event: ChangeEvent):
        """Log event for banking compliance"""
        compliance_data = {
            'event_id': change_event.event_id,
            'timestamp': change_event.timestamp.isoformat(),
            'table': change_event.table_name,
            'change_type': change_event.change_type.value,
            'transaction_id': change_event.transaction_id,
            'compliance_tags': change_event.metadata
        }
        
        self.compliance_logger.info(json.dumps(compliance_data))

class FlipkartInventoryCDC:
    """
    Flipkart inventory management के लिए CDC implementation
    Real-time inventory updates during flash sales
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.change_buffer = []
        self.batch_size = config.get('batch_size', 1000)
        self.flush_interval = config.get('flush_interval', 5)  # seconds
        self.kafka_producer = self._setup_kafka_producer()
        self.inventory_cache = defaultdict(dict)
        self.flash_sale_active = False
        
        logger.info("Flipkart Inventory CDC initialized")
    
    def _setup_kafka_producer(self):
        """Setup high-throughput Kafka producer for inventory updates"""
        return KafkaProducer(
            bootstrap_servers=self.config.get('kafka_servers', ['localhost:9092']),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',  # Compression for high volume
            batch_size=65536,  # Larger batch size for inventory
            linger_ms=100,  # Higher linger for better batching
            buffer_memory=67108864  # 64MB buffer
        )
    
    async def capture_inventory_changes(self):
        """Capture inventory changes using polling-based CDC"""
        logger.info("Starting Flipkart Inventory CDC...")
        
        # Start background tasks
        tasks = [
            self._poll_inventory_changes(),
            self._flush_change_buffer_periodically(),
            self._monitor_flash_sale_events()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _poll_inventory_changes(self):
        """Poll inventory table for changes using timestamp-based approach"""
        last_check_time = datetime.now()
        
        while True:
            try:
                current_time = datetime.now()
                
                # Query for changes since last check
                changes = await self._query_inventory_changes(last_check_time, current_time)
                
                for change in changes:
                    change_event = self._create_inventory_change_event(change)
                    
                    # Add to buffer for batch processing
                    self.change_buffer.append(change_event)
                    
                    # Update local cache
                    self._update_inventory_cache(change_event)
                    
                    # Check for flash sale scenarios
                    if self.flash_sale_active:
                        await self._handle_flash_sale_inventory(change_event)
                
                last_check_time = current_time
                await asyncio.sleep(self.config.get('poll_interval', 1))
                
            except Exception as e:
                logger.error(f"Inventory polling failed: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _query_inventory_changes(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Query inventory changes from database"""
        # Simulated database query - production में actual DB query होगी
        import random
        
        changes = []
        if random.random() < 0.7:  # 70% chance of having changes
            num_changes = random.randint(1, 10)
            for i in range(num_changes):
                changes.append({
                    'product_id': f'FKRT{random.randint(1000000000, 9999999999)}',
                    'warehouse_id': f'WH_MUM_{random.randint(1, 5):03d}',
                    'old_quantity': random.randint(0, 1000),
                    'new_quantity': random.randint(0, 1000),
                    'updated_at': end_time,
                    'price': random.uniform(100, 10000),
                    'category': random.choice(['Electronics', 'Fashion', 'Books', 'Home'])
                })
        
        return changes
    
    def _create_inventory_change_event(self, change: Dict[str, Any]) -> ChangeEvent:
        """Create change event from inventory change data"""
        return ChangeEvent(
            event_id=str(uuid.uuid4()),
            timestamp=change['updated_at'],
            change_type=ChangeType.UPDATE,
            database_name="flipkart_inventory",
            table_name="product_inventory",
            primary_key={
                "product_id": change['product_id'],
                "warehouse_id": change['warehouse_id']
            },
            old_values={"quantity": change['old_quantity']},
            new_values={
                "quantity": change['new_quantity'],
                "price": change['price'],
                "category": change['category']
            },
            metadata={
                "source": "flipkart_cdc",
                "flash_sale": self.flash_sale_active
            }
        )
    
    def _update_inventory_cache(self, change_event: ChangeEvent):
        """Update inventory cache for quick lookups"""
        pk = change_event.primary_key
        cache_key = f"{pk['product_id']}:{pk['warehouse_id']}"
        
        self.inventory_cache[cache_key] = {
            'quantity': change_event.new_values['quantity'],
            'price': change_event.new_values['price'],
            'category': change_event.new_values['category'],
            'last_updated': change_event.timestamp
        }
    
    async def _handle_flash_sale_inventory(self, change_event: ChangeEvent):
        """Special handling for flash sale inventory changes"""
        new_quantity = change_event.new_values.get('quantity', 0)
        
        # Alert for low stock during flash sale
        if new_quantity < 10:
            alert_event = ChangeEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                change_type=ChangeType.UPDATE,
                database_name="flipkart_alerts",
                table_name="inventory_alerts",
                primary_key=change_event.primary_key,
                new_values={
                    "alert_type": "LOW_STOCK",
                    "severity": "HIGH",
                    "message": f"Low stock during flash sale: {new_quantity} items left"
                },
                metadata={"flash_sale_alert": True}
            )
            
            self.change_buffer.append(alert_event)
            logger.warning(f"Flash sale low stock alert: {change_event.primary_key}")
    
    async def _flush_change_buffer_periodically(self):
        """Periodically flush change buffer to Kafka"""
        while True:
            try:
                if len(self.change_buffer) >= self.batch_size:
                    await self._flush_change_buffer()
                
                await asyncio.sleep(self.flush_interval)
                
                # Flush remaining changes
                if self.change_buffer:
                    await self._flush_change_buffer()
                    
            except Exception as e:
                logger.error(f"Buffer flushing failed: {e}")
    
    async def _flush_change_buffer(self):
        """Flush accumulated changes to Kafka"""
        if not self.change_buffer:
            return
        
        try:
            # Group changes by table for efficient processing
            changes_by_table = defaultdict(list)
            for change in self.change_buffer:
                changes_by_table[change.table_name].append(change)
            
            # Send to appropriate Kafka topics
            for table_name, changes in changes_by_table.items():
                topic_name = f"flipkart-{table_name}-changes"
                
                for change in changes:
                    message = change.to_kafka_message()
                    self.kafka_producer.send(topic_name, message)
            
            # Wait for all messages to be sent
            self.kafka_producer.flush()
            
            logger.info(f"Flushed {len(self.change_buffer)} changes to Kafka")
            self.change_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush changes to Kafka: {e}")
            raise
    
    async def _monitor_flash_sale_events(self):
        """Monitor for flash sale events to adjust CDC behavior"""
        while True:
            try:
                # Check for flash sale events (simplified - production में event system से आएगा)
                current_hour = datetime.now().hour
                
                # Flash sale during 12-2 PM और 6-8 PM
                if (12 <= current_hour <= 14) or (18 <= current_hour <= 20):
                    if not self.flash_sale_active:
                        self.flash_sale_active = True
                        logger.info("Flash sale mode activated - increasing CDC frequency")
                else:
                    if self.flash_sale_active:
                        self.flash_sale_active = False
                        logger.info("Flash sale mode deactivated - normal CDC frequency")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Flash sale monitoring failed: {e}")

class ZomatoRestaurantStatusCDC:
    """
    Zomato restaurant status changes के लिए CDC
    Real-time restaurant availability और menu updates
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.trigger_handlers = {}
        self.webhook_endpoints = config.get('webhook_endpoints', [])
        self.notification_service = self._setup_notification_service()
        self.restaurant_cache = {}
        
        logger.info("Zomato Restaurant Status CDC initialized")
    
    def _setup_notification_service(self):
        """Setup notification service for delivery partners"""
        # Simplified notification service
        return {
            'push_notifications': True,
            'email_alerts': True,
            'sms_alerts': False,
            'webhook_delivery': True
        }
    
    def setup_database_triggers(self):
        """Setup database triggers for restaurant status changes"""
        triggers = [
            self._create_restaurant_status_trigger(),
            self._create_menu_availability_trigger(),
            self._create_delivery_partner_trigger()
        ]
        
        for trigger in triggers:
            self.trigger_handlers[trigger['name']] = trigger['handler']
            logger.info(f"Database trigger setup: {trigger['name']}")
    
    def _create_restaurant_status_trigger(self):
        """Create trigger for restaurant status changes"""
        return {
            'name': 'restaurant_status_change',
            'sql': """
                CREATE OR REPLACE FUNCTION notify_restaurant_status_change()
                RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('restaurant_status_change', 
                        json_build_object(
                            'restaurant_id', NEW.id,
                            'old_status', OLD.status,
                            'new_status', NEW.status,
                            'timestamp', NOW()
                        )::text
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS restaurant_status_trigger ON restaurants;
                CREATE TRIGGER restaurant_status_trigger
                    AFTER UPDATE OF status ON restaurants
                    FOR EACH ROW EXECUTE FUNCTION notify_restaurant_status_change();
            """,
            'handler': self._handle_restaurant_status_change
        }
    
    def _create_menu_availability_trigger(self):
        """Create trigger for menu item availability changes"""
        return {
            'name': 'menu_availability_change',
            'sql': """
                CREATE OR REPLACE FUNCTION notify_menu_availability_change()
                RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('menu_availability_change',
                        json_build_object(
                            'restaurant_id', NEW.restaurant_id,
                            'menu_item_id', NEW.id,
                            'old_available', OLD.available,
                            'new_available', NEW.available,
                            'timestamp', NOW()
                        )::text
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS menu_availability_trigger ON menu_items;
                CREATE TRIGGER menu_availability_trigger
                    AFTER UPDATE OF available ON menu_items
                    FOR EACH ROW EXECUTE FUNCTION notify_menu_availability_change();
            """,
            'handler': self._handle_menu_availability_change
        }
    
    def _create_delivery_partner_trigger(self):
        """Create trigger for delivery partner status changes"""
        return {
            'name': 'delivery_partner_status',
            'sql': """
                CREATE OR REPLACE FUNCTION notify_delivery_partner_status()
                RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('delivery_partner_status',
                        json_build_object(
                            'partner_id', NEW.id,
                            'old_status', OLD.status,
                            'new_status', NEW.status,
                            'location', NEW.current_location,
                            'timestamp', NOW()
                        )::text
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS delivery_partner_trigger ON delivery_partners;
                CREATE TRIGGER delivery_partner_trigger
                    AFTER UPDATE OF status ON delivery_partners
                    FOR EACH ROW EXECUTE FUNCTION notify_delivery_partner_status();
            """,
            'handler': self._handle_delivery_partner_status
        }
    
    async def _handle_restaurant_status_change(self, notification_data: Dict[str, Any]):
        """Handle restaurant status change notifications"""
        restaurant_id = notification_data['restaurant_id']
        old_status = notification_data['old_status']
        new_status = notification_data['new_status']
        
        logger.info(f"Restaurant {restaurant_id} status changed: {old_status} -> {new_status}")
        
        # Create change event
        change_event = ChangeEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            change_type=ChangeType.UPDATE,
            database_name="zomato_operations",
            table_name="restaurants",
            primary_key={"restaurant_id": restaurant_id},
            old_values={"status": old_status},
            new_values={"status": new_status},
            metadata={
                "notification_required": True,
                "priority": "HIGH" if new_status in ["CLOSED", "TEMPORARILY_UNAVAILABLE"] else "NORMAL"
            }
        )
        
        # Send notifications to delivery partners
        await self._notify_delivery_partners(change_event)
        
        # Update customer app
        await self._update_customer_app(change_event)
    
    async def _handle_menu_availability_change(self, notification_data: Dict[str, Any]):
        """Handle menu availability change notifications"""
        restaurant_id = notification_data['restaurant_id']
        menu_item_id = notification_data['menu_item_id']
        old_available = notification_data['old_available']
        new_available = notification_data['new_available']
        
        logger.info(f"Menu item {menu_item_id} availability changed: {old_available} -> {new_available}")
        
        change_event = ChangeEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            change_type=ChangeType.UPDATE,
            database_name="zomato_operations",
            table_name="menu_items",
            primary_key={"restaurant_id": restaurant_id, "menu_item_id": menu_item_id},
            old_values={"available": old_available},
            new_values={"available": new_available},
            metadata={
                "real_time_update": True,
                "customer_notification": new_available == False  # Notify if item becomes unavailable
            }
        )
        
        # Update menu cache
        await self._update_menu_cache(change_event)
        
        # Notify customers with pending orders
        if not new_available:
            await self._notify_affected_customers(change_event)
    
    async def _handle_delivery_partner_status(self, notification_data: Dict[str, Any]):
        """Handle delivery partner status change notifications"""
        partner_id = notification_data['partner_id']
        old_status = notification_data['old_status']
        new_status = notification_data['new_status']
        location = notification_data.get('location')
        
        logger.info(f"Delivery partner {partner_id} status changed: {old_status} -> {new_status}")
        
        change_event = ChangeEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            change_type=ChangeType.UPDATE,
            database_name="zomato_operations",
            table_name="delivery_partners",
            primary_key={"partner_id": partner_id},
            old_values={"status": old_status},
            new_values={"status": new_status, "location": location},
            metadata={
                "location_based": True,
                "order_assignment_impact": True
            }
        )
        
        # Update partner availability for order assignment
        await self._update_partner_availability(change_event)
    
    async def _notify_delivery_partners(self, change_event: ChangeEvent):
        """Notify delivery partners about restaurant status changes"""
        try:
            notification_message = {
                'type': 'restaurant_status_change',
                'restaurant_id': change_event.primary_key['restaurant_id'],
                'new_status': change_event.new_values['status'],
                'timestamp': change_event.timestamp.isoformat(),
                'action_required': change_event.new_values['status'] == 'CLOSED'
            }
            
            # Send push notification to nearby delivery partners
            # Production में actual push notification service use होगी
            logger.info(f"Notification sent to delivery partners: {notification_message}")
            
        except Exception as e:
            logger.error(f"Failed to notify delivery partners: {e}")
    
    async def _update_customer_app(self, change_event: ChangeEvent):
        """Update customer app with restaurant status changes"""
        try:
            # Update real-time restaurant listing
            update_message = {
                'type': 'restaurant_update',
                'restaurant_id': change_event.primary_key['restaurant_id'],
                'status': change_event.new_values['status'],
                'timestamp': change_event.timestamp.isoformat()
            }
            
            # Send to customer app via WebSocket/Server-Sent Events
            logger.info(f"Customer app update: {update_message}")
            
        except Exception as e:
            logger.error(f"Failed to update customer app: {e}")
    
    async def _update_menu_cache(self, change_event: ChangeEvent):
        """Update menu availability cache"""
        restaurant_id = change_event.primary_key['restaurant_id']
        menu_item_id = change_event.primary_key['menu_item_id']
        
        cache_key = f"menu:{restaurant_id}:{menu_item_id}"
        self.restaurant_cache[cache_key] = {
            'available': change_event.new_values['available'],
            'last_updated': change_event.timestamp
        }
        
        logger.debug(f"Menu cache updated: {cache_key}")
    
    async def _notify_affected_customers(self, change_event: ChangeEvent):
        """Notify customers affected by menu item unavailability"""
        # Find customers with pending orders containing this menu item
        # Production में actual order database query होगी
        
        notification = {
            'type': 'menu_item_unavailable',
            'restaurant_id': change_event.primary_key['restaurant_id'],
            'menu_item_id': change_event.primary_key['menu_item_id'],
            'message': 'Sorry, this item is currently unavailable',
            'timestamp': change_event.timestamp.isoformat()
        }
        
        logger.info(f"Customer notification for unavailable item: {notification}")
    
    async def _update_partner_availability(self, change_event: ChangeEvent):
        """Update delivery partner availability for order assignment"""
        partner_id = change_event.primary_key['partner_id']
        new_status = change_event.new_values['status']
        location = change_event.new_values.get('location')
        
        availability_update = {
            'partner_id': partner_id,
            'available': new_status == 'ACTIVE',
            'location': location,
            'last_updated': change_event.timestamp
        }
        
        # Update partner availability cache
        cache_key = f"partner_availability:{partner_id}"
        self.restaurant_cache[cache_key] = availability_update
        
        logger.info(f"Partner availability updated: {partner_id} -> {new_status}")

class CDCOrchestrator:
    """
    Central orchestrator for managing multiple CDC systems
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cdc_systems = {}
        self.monitoring_stats = defaultdict(int)
        self.health_checks = {}
        
        # Initialize CDC systems
        self._initialize_cdc_systems()
        
        logger.info("CDC Orchestrator initialized")
    
    def _initialize_cdc_systems(self):
        """Initialize all CDC systems"""
        # HDFC Banking CDC
        banking_config = self.config.get('banking', {})
        self.cdc_systems['banking'] = HDFCBankingCDC(banking_config)
        
        # Flipkart Inventory CDC
        inventory_config = self.config.get('inventory', {})
        self.cdc_systems['inventory'] = FlipkartInventoryCDC(inventory_config)
        
        # Zomato Restaurant CDC
        restaurant_config = self.config.get('restaurant', {})
        self.cdc_systems['restaurant'] = ZomatoRestaurantStatusCDC(restaurant_config)
    
    async def start_all_cdc_systems(self):
        """Start all CDC systems concurrently"""
        logger.info("Starting all CDC systems...")
        
        tasks = [
            self._run_banking_cdc(),
            self._run_inventory_cdc(),
            self._run_restaurant_cdc(),
            self._monitor_system_health()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_banking_cdc(self):
        """Run banking CDC system"""
        try:
            await self.cdc_systems['banking'].start_cdc_capture()
        except Exception as e:
            logger.error(f"Banking CDC failed: {e}")
            self.health_checks['banking'] = 'FAILED'
    
    async def _run_inventory_cdc(self):
        """Run inventory CDC system"""
        try:
            await self.cdc_systems['inventory'].capture_inventory_changes()
        except Exception as e:
            logger.error(f"Inventory CDC failed: {e}")
            self.health_checks['inventory'] = 'FAILED'
    
    async def _run_restaurant_cdc(self):
        """Run restaurant CDC system"""
        try:
            # Setup triggers first
            self.cdc_systems['restaurant'].setup_database_triggers()
            
            # Start listening for notifications (simplified implementation)
            await self._listen_for_restaurant_notifications()
        except Exception as e:
            logger.error(f"Restaurant CDC failed: {e}")
            self.health_checks['restaurant'] = 'FAILED'
    
    async def _listen_for_restaurant_notifications(self):
        """Listen for restaurant database notifications"""
        while True:
            try:
                # Simulate receiving database notifications
                await asyncio.sleep(5)
                
                # Process sample notification
                sample_notification = {
                    'restaurant_id': 'REST123',
                    'old_status': 'OPEN',
                    'new_status': 'CLOSED',
                    'timestamp': datetime.now()
                }
                
                await self.cdc_systems['restaurant']._handle_restaurant_status_change(sample_notification)
                self.monitoring_stats['restaurant_notifications'] += 1
                
            except Exception as e:
                logger.error(f"Restaurant notification processing failed: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
    async def _monitor_system_health(self):
        """Monitor health of all CDC systems"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                health_report = {
                    'timestamp': datetime.now().isoformat(),
                    'systems': self.health_checks.copy(),
                    'statistics': dict(self.monitoring_stats),
                    'overall_status': 'HEALTHY' if not any(
                        status == 'FAILED' for status in self.health_checks.values()
                    ) else 'DEGRADED'
                }
                
                logger.info(f"CDC Health Report: {json.dumps(health_report, indent=2)}")
                
            except Exception as e:
                logger.error(f"Health monitoring failed: {e}")

async def main():
    """
    Main function demonstrating CDC implementation
    """
    print("📊 Change Data Capture (CDC) Implementation")
    print("Episode 41: Real-time Data Replication")
    print("=" * 50)
    
    # Configuration for all CDC systems
    config = {
        'banking': {
            'db_host': 'localhost',
            'db_name': 'hdfc_core_banking',
            'kafka_servers': ['localhost:9092'],
            'redis_host': 'localhost'
        },
        'inventory': {
            'batch_size': 100,
            'flush_interval': 5,
            'poll_interval': 1,
            'kafka_servers': ['localhost:9092']
        },
        'restaurant': {
            'webhook_endpoints': ['http://delivery-service/webhook'],
            'notification_service': 'firebase'
        }
    }
    
    # Initialize and start CDC orchestrator
    orchestrator = CDCOrchestrator(config)
    
    try:
        print("Starting CDC systems for Indian Banking, E-commerce, and Food Delivery...")
        
        # Run for demo duration
        demo_task = asyncio.create_task(orchestrator.start_all_cdc_systems())
        await asyncio.sleep(60)  # Run for 60 seconds
        
        demo_task.cancel()
        
        print("\n📈 CDC Demo Summary:")
        print(f"Systems Monitored: {len(orchestrator.cdc_systems)}")
        print(f"Health Status: {orchestrator.health_checks}")
        print(f"Statistics: {dict(orchestrator.monitoring_stats)}")
        
    except KeyboardInterrupt:
        print("\nCDC systems stopped by user")
    except Exception as e:
        logger.error(f"Main execution error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

"""
Key Learning Points from Change Data Capture:

1. **Real-time Data Synchronization**:
   - WAL-based CDC for banking systems (strong consistency)
   - Polling-based CDC for inventory management (high throughput)
   - Trigger-based CDC for operational systems (immediate response)

2. **Indian Context Applications**:
   - HDFC Banking: Real-time transaction processing और compliance
   - Flipkart: Flash sale inventory management
   - Zomato: Restaurant status और delivery partner coordination

3. **Production Considerations**:
   - Multiple CDC strategies for different use cases
   - Error handling और retry mechanisms
   - Performance optimization for high-volume scenarios

4. **System Integration**:
   - Kafka for event streaming
   - Redis for caching और deduplication
   - Database triggers for immediate notifications

This implementation shows how CDC can be used to build real-time,
event-driven architectures that can handle Indian scale requirements.
"""