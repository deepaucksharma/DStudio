#!/usr/bin/env python3
"""
Change Data Capture (CDC) with Debezium - Real-time Sync
========================================================

जैसे WhatsApp में message instantly सभी devices पर sync हो जाते हैं,
वैसे ही database changes को real-time में capture करके sync करना।

Real-world use case: Banking transaction sync across systems
Challenge: 0 data loss, microsecond latency, ACID compliance

Author: DStudio Engineering Team
Episode: 11 - ETL & Data Integration Patterns
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Kafka and Debezium
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError

# Database connectors
import psycopg2
import mysql.connector
from pymongo import MongoClient
import redis

# Schema handling
import avro.schema
import avro.io
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.avro import AvroConsumer, AvroProducer

@dataclass
class CDCEvent:
    """CDC event structure - Database change का representation"""
    event_id: str
    source_system: str
    database: str
    table: str
    operation: str  # INSERT, UPDATE, DELETE
    primary_key: str
    before_data: Optional[Dict] = None
    after_data: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)
    transaction_id: Optional[str] = None
    schema_version: int = 1
    
    def to_dict(self) -> Dict:
        """Convert CDC event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'source_system': self.source_system,
            'database': self.database,
            'table': self.table,
            'operation': self.operation,
            'primary_key': self.primary_key,
            'before_data': self.before_data,
            'after_data': self.after_data,
            'timestamp': self.timestamp.isoformat(),
            'transaction_id': self.transaction_id,
            'schema_version': self.schema_version
        }

@dataclass
class CDCMetrics:
    """CDC pipeline performance और health metrics"""
    pipeline_start_time: datetime
    events_processed: int = 0
    events_failed: int = 0
    events_skipped: int = 0
    inserts_captured: int = 0
    updates_captured: int = 0
    deletes_captured: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    last_event_timestamp: Optional[datetime] = None
    
    def success_rate(self) -> float:
        """CDC success rate percentage"""
        total = self.events_processed + self.events_failed
        return (self.events_processed / total * 100) if total > 0 else 0.0
    
    def throughput_per_second(self) -> float:
        """Events processed per second"""
        duration = (datetime.now() - self.pipeline_start_time).total_seconds()
        return self.events_processed / duration if duration > 0 else 0.0

class DebeziumCDCPipeline:
    """
    Debezium-based Change Data Capture Pipeline
    ==========================================
    
    Real-time database synchronization:
    1. Capture database changes using Debezium connectors
    2. Stream changes through Kafka topics
    3. Apply changes to target systems (PostgreSQL, MongoDB, etc.)
    4. Handle schema evolution और conflict resolution
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = self._setup_logging()
        
        # Pipeline state
        self.is_running = False
        self.metrics = CDCMetrics(pipeline_start_time=datetime.now())
        self.pipeline_id = f"CDC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Connections
        self.kafka_consumer = None
        self.kafka_producer = None
        self.schema_registry_client = None
        self.target_connections = {}
        
        # CDC configuration
        self.cdc_config = {
            'source_db_type': 'mysql',  # mysql, postgresql, mongodb
            'debezium_server_url': 'http://localhost:8083',
            'kafka_bootstrap_servers': ['localhost:9092'],
            'schema_registry_url': 'http://localhost:8081',
            'target_systems': ['postgresql', 'mongodb', 'elasticsearch'],
            'batch_size': 1000,
            'commit_interval_ms': 5000,
            'max_poll_records': 500
        }
        
        # Business rules for CDC
        self.business_rules = {
            'ignore_system_tables': True,
            'capture_ddl_changes': False,  # Only DML changes
            'enable_schema_evolution': True,
            'conflict_resolution': 'last_write_wins',  # timestamp-based
            'data_masking_enabled': True,
            'audit_logging_enabled': True
        }
        
    def _setup_logging(self):
        """Production-grade CDC logging"""
        logger = logging.getLogger("DebeziumCDC")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler for audit trail
            file_handler = logging.FileHandler(
                f"cdc_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
            )
            console_handler = logging.StreamHandler()
            
            # Detailed formatter for CDC events
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [CDC:%(pipeline_id)s] - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def initialize_debezium_connectors(self):
        """
        Debezium connectors को initialize करना
        ====================================
        
        Source databases के लिए CDC connectors setup करना।
        """
        self.logger.info("🔧 Initializing Debezium connectors...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        # MySQL connector configuration for banking transactions
        mysql_connector_config = {
            "name": "banking-mysql-connector",
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "tasks.max": "1",
                "database.hostname": "mysql-primary.bank.com",
                "database.port": "3306", 
                "database.user": "debezium_user",
                "database.password": "secure_debezium_password",
                "database.server.id": "1001",
                "database.server.name": "banking_mysql",
                
                # Database और tables selection
                "database.include.list": "banking_core,customer_data,transaction_log",
                "table.include.list": "banking_core.accounts,banking_core.transactions,customer_data.customers,transaction_log.audit_trail",
                
                # CDC behavior
                "database.history.kafka.bootstrap.servers": "kafka1:9092,kafka2:9092,kafka3:9092",
                "database.history.kafka.topic": "banking.schema.history",
                "include.schema.changes": "false",
                "snapshot.mode": "when_needed",  # Initial snapshot if needed
                "snapshot.locking.mode": "minimal",
                
                # Performance tuning
                "max.batch.size": "2048",
                "max.queue.size": "81920",
                "poll.interval.ms": "100",
                
                # Data transformation
                "column.include.list": "banking_core.transactions.transaction_id,banking_core.transactions.account_id,banking_core.transactions.amount,banking_core.transactions.transaction_timestamp,banking_core.transactions.transaction_type",
                "column.mask.with.8.chars": "customer_data.customers.aadhaar_number,customer_data.customers.pan_number",
                
                # Binary log configuration
                "binlog.buffer.size": "32768",
                "connect.keep.alive": "true",
                "connect.timeout.ms": "30000",
                
                # Topic naming
                "topic.prefix": "banking",
                "topic.creation.enable": "true"
            }
        }
        
        # PostgreSQL connector for analytics database
        postgres_connector_config = {
            "name": "analytics-postgres-connector",
            "config": {
                "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                "database.hostname": "postgres-analytics.bank.com",
                "database.port": "5432",
                "database.user": "debezium_user", 
                "database.password": "secure_debezium_password",
                "database.dbname": "analytics_db",
                "database.server.name": "analytics_postgres",
                
                # WAL configuration
                "slot.name": "debezium_analytics_slot",
                "plugin.name": "pgoutput",
                "publication.name": "debezium_publication",
                
                # Schema and table selection
                "schema.include.list": "customer_analytics,transaction_analytics",
                "table.include.list": "customer_analytics.customer_360,transaction_analytics.daily_metrics",
                
                # Snapshot configuration
                "snapshot.mode": "initial",
                "snapshot.include.collection.list": "customer_analytics.customer_360",
                
                # Performance settings
                "max.batch.size": "2048",
                "poll.interval.ms": "100",
                
                # Topic configuration
                "topic.prefix": "analytics",
                "topic.creation.enable": "true"
            }
        }
        
        try:
            # Register connectors with Debezium Connect
            import requests
            
            connectors = [mysql_connector_config, postgres_connector_config]
            
            for connector in connectors:
                response = requests.post(
                    f"{self.cdc_config['debezium_server_url']}/connectors",
                    headers={'Content-Type': 'application/json'},
                    json=connector,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"✅ Connector {connector['name']} registered successfully", 
                                   extra={'pipeline_id': self.pipeline_id})
                else:
                    self.logger.error(f"❌ Failed to register connector {connector['name']}: {response.text}", 
                                    extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.logger.error(f"❌ Connector initialization failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def initialize_kafka_connections(self):
        """Kafka consumer और producer connections"""
        try:
            # Kafka Consumer for CDC events
            self.kafka_consumer = KafkaConsumer(
                'banking.banking_core.transactions',
                'banking.customer_data.customers', 
                'analytics.customer_analytics.customer_360',
                bootstrap_servers=self.cdc_config['kafka_bootstrap_servers'],
                auto_offset_reset='earliest',  # Process from beginning for initial sync
                enable_auto_commit=False,  # Manual commit for exactly-once processing
                group_id='cdc-processor-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000,
                max_poll_records=self.cdc_config['max_poll_records'],
                fetch_min_bytes=1024,
                fetch_max_wait_ms=500
            )
            
            # Kafka Producer for processed events
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.cdc_config['kafka_bootstrap_servers'],
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: str(x).encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3,
                batch_size=16384,
                linger_ms=5,  # Small delay for batching
                compression_type='snappy'
            )
            
            # Schema Registry client for Avro schemas
            self.schema_registry_client = SchemaRegistryClient({
                'url': self.cdc_config['schema_registry_url']
            })
            
            self.logger.info("✅ Kafka connections initialized", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.logger.error(f"❌ Kafka connection failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def initialize_target_connections(self):
        """Target systems के लिए database connections"""
        try:
            # PostgreSQL target (Data warehouse)
            self.target_connections['postgresql'] = psycopg2.connect(
                host='postgres-warehouse.bank.com',
                port=5432,
                database='banking_warehouse',
                user='cdc_user',
                password='secure_cdc_password',
                application_name='CDC_Pipeline'
            )
            
            # MongoDB target (Real-time analytics)  
            self.target_connections['mongodb'] = MongoClient(
                'mongodb://cdc_user:secure_password@mongo-cluster.bank.com:27017/banking_realtime?replicaSet=rs0'
            )
            
            # Redis target (Caching और real-time lookups)
            self.target_connections['redis'] = redis.Redis(
                host='redis-cluster.bank.com',
                port=6379,
                db=0,
                password='redis_secure_password',
                decode_responses=True
            )
            
            self.logger.info("✅ Target system connections established", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.logger.error(f"❌ Target connection failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def parse_debezium_event(self, raw_event: Dict) -> Optional[CDCEvent]:
        """
        Debezium event को parse करके CDCEvent में convert करना
        =====================================================
        
        Debezium के complex event format को simplify करना।
        """
        try:
            # Debezium event structure
            payload = raw_event.get('payload', {})
            source = payload.get('source', {})
            
            # Extract operation type
            operation = payload.get('op')
            if operation is None:
                return None
            
            operation_mapping = {
                'c': 'INSERT',  # Create
                'u': 'UPDATE',  # Update
                'd': 'DELETE',  # Delete
                'r': 'READ'     # Read (snapshot)
            }
            
            mapped_operation = operation_mapping.get(operation, 'UNKNOWN')
            if mapped_operation == 'UNKNOWN':
                self.logger.warning(f"Unknown operation type: {operation}", 
                                  extra={'pipeline_id': self.pipeline_id})
                return None
            
            # Extract table information
            database = source.get('db', '')
            table = source.get('table', '')
            
            # Skip system tables if configured
            if self.business_rules['ignore_system_tables'] and table.startswith('sys_'):
                return None
            
            # Extract data
            before_data = payload.get('before')
            after_data = payload.get('after')
            
            # Get primary key (assuming first field is PK)
            primary_key = None
            if after_data:
                primary_key = list(after_data.keys())[0] if after_data else None
            elif before_data:
                primary_key = list(before_data.keys())[0] if before_data else None
            
            # Create CDC event
            cdc_event = CDCEvent(
                event_id=f"{source.get('server', '')}.{source.get('ts_ms', 0)}",
                source_system=source.get('server', 'unknown'),
                database=database,
                table=table,
                operation=mapped_operation,
                primary_key=str(primary_key) if primary_key else '',
                before_data=before_data,
                after_data=after_data,
                timestamp=datetime.fromtimestamp(source.get('ts_ms', 0) / 1000),
                transaction_id=source.get('txId'),
                schema_version=1
            )
            
            # Apply data masking if enabled
            if self.business_rules['data_masking_enabled']:
                cdc_event = self._apply_data_masking(cdc_event)
            
            return cdc_event
            
        except Exception as e:
            self.logger.error(f"❌ Event parsing failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            return None
    
    def _apply_data_masking(self, event: CDCEvent) -> CDCEvent:
        """Sensitive data को mask करना - PII protection"""
        
        # Define sensitive fields
        sensitive_fields = {
            'aadhaar_number': lambda x: 'XXXX-XXXX-' + str(x)[-4:] if x else None,
            'pan_number': lambda x: 'XXXXX' + str(x)[5:] if x else None,
            'phone_number': lambda x: 'XXXXX' + str(x)[-5:] if x else None,
            'email': lambda x: 'XXXXX@' + str(x).split('@')[1] if x and '@' in str(x) else None,
            'account_number': lambda x: 'XXXXXXXX' + str(x)[-4:] if x else None
        }
        
        try:
            # Mask before_data
            if event.before_data:
                for field, mask_func in sensitive_fields.items():
                    if field in event.before_data and event.before_data[field]:
                        event.before_data[field] = mask_func(event.before_data[field])
            
            # Mask after_data
            if event.after_data:
                for field, mask_func in sensitive_fields.items():
                    if field in event.after_data and event.after_data[field]:
                        event.after_data[field] = mask_func(event.after_data[field])
            
            return event
            
        except Exception as e:
            self.logger.error(f"❌ Data masking failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            return event
    
    def apply_to_postgresql(self, event: CDCEvent):
        """PostgreSQL target में CDC event apply करना"""
        try:
            conn = self.target_connections['postgresql']
            cursor = conn.cursor()
            
            # Table mapping for warehouse
            table_mapping = {
                'transactions': 'fact_transactions',
                'customers': 'dim_customers',
                'accounts': 'dim_accounts'
            }
            
            target_table = table_mapping.get(event.table, f"cdc_{event.table}")
            
            if event.operation == 'INSERT':
                # Insert new record
                if event.after_data:
                    columns = list(event.after_data.keys())
                    values = list(event.after_data.values())
                    
                    # Add CDC metadata
                    columns.extend(['_cdc_timestamp', '_cdc_operation', '_source_system'])
                    values.extend([event.timestamp, event.operation, event.source_system])
                    
                    placeholders = ', '.join(['%s'] * len(values))
                    columns_str = ', '.join(columns)
                    
                    insert_sql = f"""
                    INSERT INTO {target_table} ({columns_str})
                    VALUES ({placeholders})
                    ON CONFLICT ({event.primary_key}) 
                    DO UPDATE SET
                        {', '.join([f"{col} = EXCLUDED.{col}" for col in columns[:-3]])},
                        _cdc_timestamp = EXCLUDED._cdc_timestamp,
                        _cdc_operation = EXCLUDED._cdc_operation
                    """
                    
                    cursor.execute(insert_sql, values)
                    
            elif event.operation == 'UPDATE':
                # Update existing record
                if event.after_data:
                    set_clauses = []
                    values = []
                    
                    for key, value in event.after_data.items():
                        if key != event.primary_key:  # Don't update primary key
                            set_clauses.append(f"{key} = %s")
                            values.append(value)
                    
                    # Add CDC metadata
                    set_clauses.extend(['_cdc_timestamp = %s', '_cdc_operation = %s'])
                    values.extend([event.timestamp, event.operation])
                    
                    # Primary key for WHERE clause
                    values.append(event.after_data[event.primary_key])
                    
                    update_sql = f"""
                    UPDATE {target_table}
                    SET {', '.join(set_clauses)}
                    WHERE {event.primary_key} = %s
                    """
                    
                    cursor.execute(update_sql, values)
                    
            elif event.operation == 'DELETE':
                # Soft delete (mark as deleted)
                if event.before_data and event.primary_key in event.before_data:
                    delete_sql = f"""
                    UPDATE {target_table}
                    SET 
                        _is_deleted = true,
                        _cdc_timestamp = %s,
                        _cdc_operation = %s
                    WHERE {event.primary_key} = %s
                    """
                    
                    cursor.execute(delete_sql, [
                        event.timestamp,
                        event.operation,
                        event.before_data[event.primary_key]
                    ])
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"❌ PostgreSQL apply failed for {event.event_id}: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def apply_to_mongodb(self, event: CDCEvent):
        """MongoDB target में CDC event apply करना"""
        try:
            mongo_client = self.target_connections['mongodb']
            db = mongo_client['banking_realtime']
            collection = db[event.table]
            
            if event.operation == 'INSERT':
                if event.after_data:
                    document = event.after_data.copy()
                    document.update({
                        '_cdc_timestamp': event.timestamp,
                        '_cdc_operation': event.operation,
                        '_source_system': event.source_system
                    })
                    
                    # Upsert operation
                    filter_query = {event.primary_key: document[event.primary_key]}
                    collection.replace_one(filter_query, document, upsert=True)
                    
            elif event.operation == 'UPDATE':
                if event.after_data:
                    filter_query = {event.primary_key: event.after_data[event.primary_key]}
                    
                    update_doc = {
                        '$set': event.after_data,
                        '$currentDate': {'_cdc_timestamp': True},
                        '$set': {
                            '_cdc_operation': event.operation,
                            '_source_system': event.source_system
                        }
                    }
                    
                    collection.update_one(filter_query, update_doc, upsert=True)
                    
            elif event.operation == 'DELETE':
                if event.before_data:
                    filter_query = {event.primary_key: event.before_data[event.primary_key]}
                    
                    # Soft delete in MongoDB
                    update_doc = {
                        '$set': {
                            '_is_deleted': True,
                            '_cdc_timestamp': event.timestamp,
                            '_cdc_operation': event.operation
                        }
                    }
                    
                    collection.update_one(filter_query, update_doc)
            
        except Exception as e:
            self.logger.error(f"❌ MongoDB apply failed for {event.event_id}: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def apply_to_redis(self, event: CDCEvent):
        """Redis में real-time caching के लिए CDC event apply करना"""
        try:
            redis_client = self.target_connections['redis']
            
            # Redis key pattern: table:primary_key
            cache_key = f"{event.table}:{event.after_data.get(event.primary_key) if event.after_data else event.before_data.get(event.primary_key)}"
            
            if event.operation in ['INSERT', 'UPDATE']:
                if event.after_data:
                    # Store as hash for efficient field access
                    redis_client.hmset(cache_key, event.after_data)
                    
                    # Set expiration (24 hours for most data)
                    expiration_hours = 24
                    if event.table == 'transactions':
                        expiration_hours = 1  # Transaction cache expires quickly
                    
                    redis_client.expire(cache_key, expiration_hours * 3600)
                    
                    # Update global counters
                    redis_client.incr(f"cdc:stats:{event.table}:{event.operation.lower()}")
                    
            elif event.operation == 'DELETE':
                # Remove from cache
                redis_client.delete(cache_key)
                redis_client.incr(f"cdc:stats:{event.table}:delete")
            
            # Update last processed timestamp
            redis_client.set(f"cdc:last_processed:{event.source_system}", 
                           event.timestamp.isoformat())
            
        except Exception as e:
            self.logger.error(f"❌ Redis apply failed for {event.event_id}: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            # Redis failures are not critical, continue processing
            pass
    
    def process_cdc_events(self):
        """
        Main CDC event processing loop
        =============================
        
        Kafka से CDC events consume करके target systems में apply करना।
        """
        self.logger.info("🔄 Starting CDC event processing...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        self.is_running = True
        batch_events = []
        last_commit_time = time.time()
        
        try:
            while self.is_running:
                # Poll for new messages
                message_batch = self.kafka_consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    # No new messages, check if we need to commit
                    if time.time() - last_commit_time > self.cdc_config['commit_interval_ms'] / 1000:
                        if batch_events:
                            self._commit_batch(batch_events)
                            batch_events.clear()
                            last_commit_time = time.time()
                    continue
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            event_start_time = time.time()
                            
                            # Parse Debezium event
                            cdc_event = self.parse_debezium_event(message.value)
                            if not cdc_event:
                                self.metrics.events_skipped += 1
                                continue
                            
                            # Apply to all target systems in parallel
                            with ThreadPoolExecutor(max_workers=3) as executor:
                                futures = []
                                
                                # PostgreSQL
                                if 'postgresql' in self.cdc_config['target_systems']:
                                    futures.append(executor.submit(self.apply_to_postgresql, cdc_event))
                                
                                # MongoDB
                                if 'mongodb' in self.cdc_config['target_systems']:
                                    futures.append(executor.submit(self.apply_to_mongodb, cdc_event))
                                
                                # Redis
                                if 'redis' in self.cdc_config['target_systems']:
                                    futures.append(executor.submit(self.apply_to_redis, cdc_event))
                                
                                # Wait for all applications to complete
                                for future in futures:
                                    try:
                                        future.result(timeout=5)  # 5 second timeout per target
                                    except Exception as e:
                                        self.logger.error(f"❌ Target system apply failed: {str(e)}", 
                                                        extra={'pipeline_id': self.pipeline_id})
                                        self.metrics.events_failed += 1
                                        continue
                            
                            # Update metrics
                            processing_time = (time.time() - event_start_time) * 1000
                            self.metrics.events_processed += 1
                            self.metrics.last_event_timestamp = cdc_event.timestamp
                            
                            # Update operation counters
                            if cdc_event.operation == 'INSERT':
                                self.metrics.inserts_captured += 1
                            elif cdc_event.operation == 'UPDATE':
                                self.metrics.updates_captured += 1
                            elif cdc_event.operation == 'DELETE':
                                self.metrics.deletes_captured += 1
                            
                            # Update latency metrics
                            self.metrics.avg_latency_ms = (
                                (self.metrics.avg_latency_ms * (self.metrics.events_processed - 1) + processing_time) 
                                / self.metrics.events_processed
                            )
                            self.metrics.max_latency_ms = max(self.metrics.max_latency_ms, processing_time)
                            
                            batch_events.append(message)
                            
                            # Log progress every 1000 events
                            if self.metrics.events_processed % 1000 == 0:
                                self._log_processing_stats()
                            
                        except Exception as e:
                            self.logger.error(f"❌ Event processing failed: {str(e)}", 
                                            extra={'pipeline_id': self.pipeline_id})
                            self.metrics.events_failed += 1
                
                # Commit batch if size limit reached or time elapsed
                if (len(batch_events) >= self.cdc_config['batch_size'] or 
                    time.time() - last_commit_time > self.cdc_config['commit_interval_ms'] / 1000):
                    self._commit_batch(batch_events)
                    batch_events.clear()
                    last_commit_time = time.time()
                    
        except KeyboardInterrupt:
            self.logger.info("⏹️ CDC processing stopped by user", 
                           extra={'pipeline_id': self.pipeline_id})
        except Exception as e:
            self.logger.error(f"💥 CDC processing failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
        finally:
            # Final commit
            if batch_events:
                self._commit_batch(batch_events)
            self.is_running = False
    
    def _commit_batch(self, batch_events: List):
        """Batch commit for exactly-once processing"""
        try:
            self.kafka_consumer.commit()
            self.logger.debug(f"✅ Committed batch of {len(batch_events)} events", 
                            extra={'pipeline_id': self.pipeline_id})
        except Exception as e:
            self.logger.error(f"❌ Batch commit failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
    
    def _log_processing_stats(self):
        """Processing statistics logging"""
        self.logger.info(f"📊 CDC Stats - Processed: {self.metrics.events_processed:,}, "
                        f"Success Rate: {self.metrics.success_rate():.2f}%, "
                        f"TPS: {self.metrics.throughput_per_second():.2f}, "
                        f"Avg Latency: {self.metrics.avg_latency_ms:.2f}ms", 
                        extra={'pipeline_id': self.pipeline_id})
    
    def run_cdc_pipeline(self):
        """
        Complete CDC Pipeline Execution
        ==============================
        
        End-to-end CDC pipeline run करना।
        """
        self.logger.info("🚀 Starting Debezium CDC Pipeline...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        try:
            # Initialize all components
            self.logger.info("📍 Step 1/4: Initializing Debezium connectors", 
                           extra={'pipeline_id': self.pipeline_id})
            self.initialize_debezium_connectors()
            
            self.logger.info("📍 Step 2/4: Setting up Kafka connections", 
                           extra={'pipeline_id': self.pipeline_id})
            self.initialize_kafka_connections()
            
            self.logger.info("📍 Step 3/4: Connecting to target systems", 
                           extra={'pipeline_id': self.pipeline_id})
            self.initialize_target_connections()
            
            self.logger.info("📍 Step 4/4: Starting event processing", 
                           extra={'pipeline_id': self.pipeline_id})
            
            # Start CDC processing
            self.process_cdc_events()
            
            # Final statistics
            self._log_final_stats()
            
        except Exception as e:
            self.logger.error(f"💥 CDC Pipeline failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
        finally:
            self._cleanup_connections()
    
    def _log_final_stats(self):
        """Final pipeline statistics"""
        duration = datetime.now() - self.metrics.pipeline_start_time
        
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
        self.logger.info("📋 CDC PIPELINE FINAL STATISTICS", extra={'pipeline_id': self.pipeline_id})
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Pipeline Duration: {duration}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Events Processed: {self.metrics.events_processed:,}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Success Rate: {self.metrics.success_rate():.2f}%", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Average Throughput: {self.metrics.throughput_per_second():.2f} events/sec", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Average Latency: {self.metrics.avg_latency_ms:.2f}ms", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Operations - Inserts: {self.metrics.inserts_captured:,}, "
                        f"Updates: {self.metrics.updates_captured:,}, "
                        f"Deletes: {self.metrics.deletes_captured:,}", 
                        extra={'pipeline_id': self.pipeline_id})
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
    
    def _cleanup_connections(self):
        """Cleanup all connections"""
        if self.kafka_consumer:
            self.kafka_consumer.close()
        if self.kafka_producer:
            self.kafka_producer.close()
        
        for name, conn in self.target_connections.items():
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except:
                pass
        
        self.logger.info("🧹 All connections cleaned up", 
                        extra={'pipeline_id': self.pipeline_id})

def main():
    """
    Production CDC Pipeline with Debezium
    ====================================
    
    Banking scale real-time synchronization।
    """
    
    print("🔄 Debezium Change Data Capture Pipeline")
    print("=" * 50)
    
    # Production configuration
    cdc_config = {
        'debezium_server_url': 'http://debezium-connect.bank.com:8083',
        'kafka_bootstrap_servers': [
            'kafka1.bank.com:9092',
            'kafka2.bank.com:9092', 
            'kafka3.bank.com:9092'
        ],
        'schema_registry_url': 'http://schema-registry.bank.com:8081',
        'target_systems': ['postgresql', 'mongodb', 'redis'],
        'batch_size': 1000,
        'commit_interval_ms': 5000
    }
    
    # Initialize CDC pipeline
    cdc_pipeline = DebeziumCDCPipeline(cdc_config)
    
    try:
        # Run CDC pipeline
        cdc_pipeline.run_cdc_pipeline()
        
    except KeyboardInterrupt:
        print("\n⏹️ CDC Pipeline stopped by user")
    except Exception as e:
        print(f"\n💥 CDC Pipeline failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


# Production Architecture Guide:
"""
🏗️ Production CDC Architecture - Banking Scale:

┌─────────────────────────────────────────────────────────────────┐
│                    Source Databases                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MySQL (Primary)          PostgreSQL (Analytics)               │
│  • Binlog enabled         • WAL enabled                        │
│  • GTID replication       • Logical replication                │
│  • Row-based format       • pgoutput plugin                    │
│  • 10M+ transactions/day  • Real-time metrics                  │
│                                                                 │
└─────────────┬───────────────────────────┬─────────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Debezium Connect Cluster                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • MySQL Connector         • PostgreSQL Connector              │
│  • Schema Evolution        • Data Transformation               │
│  • Exactly-once processing • Fault tolerance                   │
│  • Offset management       • Monitoring & Alerting             │
│                                                                 │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kafka Cluster                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • 50+ Brokers (Multi-AZ)  • Schema Registry                   │
│  • Replication Factor: 3   • Avro/JSON schemas                 │
│  • 1M+ messages/second     • Topic partitioning                │
│  • Compacted topics        • Retention: 7 days                 │
│                                                                 │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Target Systems (Sync)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PostgreSQL Warehouse     MongoDB Real-time     Redis Cache    │
│  • OLAP queries         • Document store        • Sub-ms reads │
│  • Historical data      • Real-time analytics   • Session data │
│  • Batch processing     • Flexible schema       • Counters     │
│  • Compliance reports   • Geospatial queries    • Leaderboards │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

📊 Scale & Performance:
- Source databases: 10M+ transactions/day
- CDC latency: <100ms end-to-end
- Kafka throughput: 1M+ messages/second
- Target systems: 3-5 destinations per change
- Data consistency: Exactly-once processing
- High availability: 99.99% uptime SLA

💰 Cost Breakdown (Monthly):
- Debezium Connect cluster: ₹5 lakhs
- Kafka cluster (50 brokers): ₹15 lakhs
- Target system compute: ₹8 lakhs
- Network & storage: ₹4 lakhs
- Monitoring & ops: ₹3 lakhs
- Total: ₹35 lakhs/month

⚡ Key Benefits:
1. **Real-time**: Changes reflected within 100ms
2. **Zero downtime**: Online schema migrations  
3. **Exactly-once**: No duplicate or lost events
4. **Scalable**: Handles 1M+ TPS easily
5. **Flexible**: Multiple target systems
6. **Auditable**: Complete change history

Real-time sync - यही है modern banking का backbone! 🏛️💨
"""