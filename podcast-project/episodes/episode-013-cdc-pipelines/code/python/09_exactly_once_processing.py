#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 9: Exactly-Once Processing Pattern

यह example exactly-once processing guarantee करता है।
Paytm, PhonePe जैसे payment systems के लिए critical - duplicate transactions नहीं होने चाहिए।

Author: Distributed Systems Podcast Team
Context: Financial transactions, idempotency, deduplication
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import redis.asyncio as redis
from kafka import KafkaProducer, KafkaConsumer
from kafka.coordinator.assignors.range import RangePartitionAssignor
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import threading
from contextlib import contextmanager

# Hindi logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(processId)d:%(threadName)s]',
    handlers=[
        logging.FileHandler('exactly_once.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status for transactions"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"

@dataclass
class PaymentTransaction:
    """UPI payment transaction - Indian context"""
    transaction_id: str
    idempotency_key: str  # Client-generated unique key
    user_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    payment_method: str = "UPI"  # UPI, CARD, WALLET
    description: str = ""
    
    # Metadata
    source_system: str = "PhonePe"  # PhonePe, GPay, Paytm
    client_ip: str = ""
    device_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Processing tracking
    processing_attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    checksum: str = field(init=False)
    
    def __post_init__(self):
        # Generate checksum for integrity verification
        data = f"{self.transaction_id}:{self.amount}:{self.user_id}:{self.merchant_id}:{self.timestamp.isoformat()}"
        self.checksum = hashlib.sha256(data.encode()).hexdigest()

@dataclass
class ProcessingRecord:
    """Individual processing attempt record"""
    record_id: str
    transaction_id: str
    idempotency_key: str
    kafka_partition: int
    kafka_offset: int
    processing_node: str
    status: ProcessingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class IdempotencyManager:
    """
    Idempotency management for exactly-once processing
    Redis-based distributed locking के साथ
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.lock_timeout = 300  # 5 minutes
        self.record_ttl = 86400   # 24 hours
        
    async def check_and_lock(self, idempotency_key: str, processing_node: str) -> Dict[str, Any]:
        """
        Idempotency key check करके processing lock acquire करो
        """
        try:
            # Check if already processed
            existing_record = await self.redis.get(f"processed:{idempotency_key}")
            if existing_record:
                record_data = json.loads(existing_record)
                logger.info(f"🔄 Transaction already processed: {idempotency_key}")
                return {
                    'can_process': False,
                    'reason': 'already_processed',
                    'existing_result': record_data
                }
            
            # Try to acquire processing lock
            lock_key = f"processing:{idempotency_key}"
            lock_acquired = await self.redis.set(
                lock_key, 
                processing_node,
                ex=self.lock_timeout,
                nx=True  # Only set if not exists
            )
            
            if lock_acquired:
                logger.info(f"🔒 Processing lock acquired: {idempotency_key}")
                return {
                    'can_process': True,
                    'lock_key': lock_key
                }
            else:
                # Check who has the lock
                current_processor = await self.redis.get(lock_key)
                logger.warning(f"⚠️ Processing lock held by: {current_processor} for key: {idempotency_key}")
                return {
                    'can_process': False,
                    'reason': 'processing_in_progress',
                    'processor': current_processor.decode() if current_processor else 'unknown'
                }
                
        except Exception as e:
            logger.error(f"💥 Idempotency check failed: {str(e)}")
            return {
                'can_process': False,
                'reason': 'system_error',
                'error': str(e)
            }
    
    async def mark_completed(self, idempotency_key: str, result: Dict[str, Any]):
        """
        Processing complete होने पर mark करो
        """
        try:
            # Store completion record
            completion_record = {
                'idempotency_key': idempotency_key,
                'completed_at': datetime.now().isoformat(),
                'result': result,
                'status': 'COMPLETED'
            }
            
            await self.redis.setex(
                f"processed:{idempotency_key}",
                self.record_ttl,
                json.dumps(completion_record, default=str)
            )
            
            # Release processing lock
            await self.redis.delete(f"processing:{idempotency_key}")
            
            logger.info(f"✅ Processing completed and recorded: {idempotency_key}")
            
        except Exception as e:
            logger.error(f"💥 Failed to mark completion: {str(e)}")
    
    async def mark_failed(self, idempotency_key: str, error: str, retry_after: Optional[int] = None):
        """
        Processing failure को mark करो
        """
        try:
            failure_record = {
                'idempotency_key': idempotency_key,
                'failed_at': datetime.now().isoformat(),
                'error': error,
                'status': 'FAILED',
                'retry_after': retry_after
            }
            
            # Store failure record with shorter TTL for retry
            ttl = retry_after if retry_after else 3600  # 1 hour default
            await self.redis.setex(
                f"failed:{idempotency_key}",
                ttl,
                json.dumps(failure_record, default=str)
            )
            
            # Release processing lock
            await self.redis.delete(f"processing:{idempotency_key}")
            
            logger.warning(f"❌ Processing failed and recorded: {idempotency_key}")
            
        except Exception as e:
            logger.error(f"💥 Failed to mark failure: {str(e)}")
    
    async def release_lock(self, idempotency_key: str):
        """
        Processing lock को release करो (cleanup के लिए)
        """
        try:
            await self.redis.delete(f"processing:{idempotency_key}")
            logger.info(f"🔓 Processing lock released: {idempotency_key}")
        except Exception as e:
            logger.error(f"💥 Lock release failed: {str(e)}")

class DatabaseManager:
    """
    PostgreSQL database operations with transaction management
    """
    
    def __init__(self, connection_params: Dict[str, str]):
        self.connection_params = connection_params
        self.connection_pool = []
        self.max_connections = 10
        
    def get_connection(self):
        """Database connection get करो"""
        return psycopg2.connect(**self.connection_params)
    
    @contextmanager
    def get_transaction(self):
        """
        Database transaction context manager
        """
        conn = None
        try:
            conn = self.get_connection()
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def create_tables(self):
        """
        Required tables create करो
        """
        create_tables_sql = """
        -- Processing records table
        CREATE TABLE IF NOT EXISTS processing_records (
            record_id VARCHAR(50) PRIMARY KEY,
            transaction_id VARCHAR(50) NOT NULL,
            idempotency_key VARCHAR(100) NOT NULL UNIQUE,
            kafka_partition INTEGER,
            kafka_offset BIGINT,
            processing_node VARCHAR(100),
            status VARCHAR(20) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            checksum VARCHAR(64),
            
            INDEX (idempotency_key),
            INDEX (transaction_id),
            INDEX (status, started_at)
        );
        
        -- Payment transactions table
        CREATE TABLE IF NOT EXISTS payment_transactions (
            transaction_id VARCHAR(50) PRIMARY KEY,
            idempotency_key VARCHAR(100) NOT NULL UNIQUE,
            user_id VARCHAR(50) NOT NULL,
            merchant_id VARCHAR(50) NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'INR',
            payment_method VARCHAR(20) NOT NULL,
            description TEXT,
            source_system VARCHAR(50),
            client_ip INET,
            device_id VARCHAR(100),
            transaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            processing_attempts INTEGER DEFAULT 0,
            checksum VARCHAR(64),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            INDEX (user_id),
            INDEX (merchant_id),
            INDEX (idempotency_key),
            INDEX (transaction_timestamp)
        );
        
        -- Payment results table
        CREATE TABLE IF NOT EXISTS payment_results (
            result_id VARCHAR(50) PRIMARY KEY,
            transaction_id VARCHAR(50) NOT NULL,
            idempotency_key VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL,
            gateway_reference VARCHAR(100),
            processed_at TIMESTAMP WITH TIME ZONE NOT NULL,
            processing_time_ms INTEGER,
            
            FOREIGN KEY (transaction_id) REFERENCES payment_transactions(transaction_id),
            INDEX (idempotency_key),
            INDEX (status)
        );
        """
        
        try:
            with self.get_transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(create_tables_sql)
                logger.info("✅ Database tables created successfully")
                
        except Exception as e:
            logger.error(f"💥 Table creation failed: {str(e)}")
            raise
    
    def save_processing_record(self, record: ProcessingRecord) -> bool:
        """
        Processing record को database में save करो
        """
        try:
            with self.get_transaction() as conn:
                cursor = conn.cursor()
                
                insert_sql = """
                INSERT INTO processing_records 
                (record_id, transaction_id, idempotency_key, kafka_partition, kafka_offset,
                 processing_node, status, started_at, completed_at, error_message, retry_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idempotency_key) DO UPDATE SET
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                error_message = EXCLUDED.error_message,
                retry_count = EXCLUDED.retry_count
                """
                
                cursor.execute(insert_sql, (
                    record.record_id,
                    record.transaction_id,
                    record.idempotency_key,
                    record.kafka_partition,
                    record.kafka_offset,
                    record.processing_node,
                    record.status.value,
                    record.started_at,
                    record.completed_at,
                    record.error_message,
                    record.retry_count
                ))
                
                return True
                
        except Exception as e:
            logger.error(f"💥 Failed to save processing record: {str(e)}")
            return False
    
    def save_payment_transaction(self, transaction: PaymentTransaction) -> bool:
        """
        Payment transaction को database में save करो
        """
        try:
            with self.get_transaction() as conn:
                cursor = conn.cursor()
                
                insert_sql = """
                INSERT INTO payment_transactions
                (transaction_id, idempotency_key, user_id, merchant_id, amount, currency,
                 payment_method, description, source_system, client_ip, device_id,
                 transaction_timestamp, processing_attempts, checksum)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idempotency_key) DO NOTHING
                """
                
                cursor.execute(insert_sql, (
                    transaction.transaction_id,
                    transaction.idempotency_key,
                    transaction.user_id,
                    transaction.merchant_id,
                    transaction.amount,
                    transaction.currency,
                    transaction.payment_method,
                    transaction.description,
                    transaction.source_system,
                    transaction.client_ip,
                    transaction.device_id,
                    transaction.timestamp,
                    transaction.processing_attempts,
                    transaction.checksum
                ))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"💥 Failed to save payment transaction: {str(e)}")
            return False

class ExactlyOnceProcessor:
    """
    Exactly-once processing engine for payment transactions
    Mumbai की Paytm office से inspire होकर बनाया गया
    """
    
    def __init__(self, kafka_servers: List[str], redis_url: str, db_params: Dict[str, str]):
        self.kafka_servers = kafka_servers
        self.redis_url = redis_url
        self.db_params = db_params
        
        # Components
        self.kafka_consumer = None
        self.redis_client = None
        self.idempotency_manager = None
        self.db_manager = None
        
        # Processing state
        self.processing_node = f"processor-{uuid.uuid4().hex[:8]}"
        self.running = False
        self.processed_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        
        # Configuration
        self.max_processing_time = 30  # seconds
        self.max_retries = 3
        
    async def initialize(self):
        """
        System को initialize करो
        """
        logger.info(f"🚀 Initializing exactly-once processor: {self.processing_node}")
        
        try:
            # Redis client
            self.redis_client = await redis.from_url(self.redis_url)
            
            # Idempotency manager
            self.idempotency_manager = IdempotencyManager(self.redis_client)
            
            # Database manager
            self.db_manager = DatabaseManager(self.db_params)
            self.db_manager.create_tables()
            
            # Kafka consumer with exactly-once semantics
            self.kafka_consumer = KafkaConsumer(
                'payment-transactions',
                bootstrap_servers=self.kafka_servers,
                group_id='exactly-once-payment-processor',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8'),
                enable_auto_commit=False,  # Manual commit for exactly-once
                max_poll_records=1,  # Process one record at a time
                isolation_level='read_committed'  # Only read committed messages
            )
            
            logger.info("✅ Exactly-once processor initialized successfully")
            
        except Exception as e:
            logger.error(f"💥 Initialization failed: {str(e)}")
            raise
    
    async def start_processing(self):
        """
        Message processing start करो
        """
        logger.info("🎯 Starting exactly-once message processing")
        
        self.running = True
        
        try:
            while self.running:
                # Poll for messages
                message_batch = self.kafka_consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    await asyncio.sleep(0.1)
                    continue
                
                # Process each message individually for exactly-once guarantee
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            await self.process_message_exactly_once(message)
                            
                            # Commit offset only after successful processing
                            self.kafka_consumer.commit_async()
                            
                        except Exception as e:
                            logger.error(f"💥 Message processing failed: {str(e)}")
                            # Don't commit offset on failure - message will be reprocessed
                            break
                
                # Log metrics periodically
                if self.processed_count % 100 == 0:
                    await self.log_processing_metrics()
                
        except Exception as e:
            logger.error(f"💥 Processing loop failed: {str(e)}")
        finally:
            await self.cleanup()
    
    async def process_message_exactly_once(self, message):
        """
        Individual message को exactly-once guarantee के साथ process करो
        """
        try:
            # Parse message
            transaction_data = message.value
            transaction_id = transaction_data['transaction_id']
            idempotency_key = transaction_data['idempotency_key']
            
            logger.info(f"📨 Processing transaction: {transaction_id}")
            
            # Create processing record
            processing_record = ProcessingRecord(
                record_id=str(uuid.uuid4()),
                transaction_id=transaction_id,
                idempotency_key=idempotency_key,
                kafka_partition=message.partition,
                kafka_offset=message.offset,
                processing_node=self.processing_node,
                status=ProcessingStatus.PENDING,
                started_at=datetime.now()
            )
            
            # Check idempotency and acquire lock
            idempotency_check = await self.idempotency_manager.check_and_lock(
                idempotency_key, 
                self.processing_node
            )
            
            if not idempotency_check['can_process']:
                if idempotency_check['reason'] == 'already_processed':
                    logger.info(f"🔄 Duplicate transaction ignored: {transaction_id}")
                    self.duplicate_count += 1
                    processing_record.status = ProcessingStatus.DUPLICATE
                    self.db_manager.save_processing_record(processing_record)
                    return
                else:
                    logger.warning(f"⚠️ Cannot process transaction: {idempotency_check['reason']}")
                    return
            
            # Update processing status
            processing_record.status = ProcessingStatus.PROCESSING
            self.db_manager.save_processing_record(processing_record)
            
            # Create payment transaction object
            payment_transaction = PaymentTransaction(
                transaction_id=transaction_data['transaction_id'],
                idempotency_key=transaction_data['idempotency_key'],
                user_id=transaction_data['user_id'],
                merchant_id=transaction_data['merchant_id'],
                amount=float(transaction_data['amount']),
                currency=transaction_data.get('currency', 'INR'),
                payment_method=transaction_data['payment_method'],
                description=transaction_data.get('description', ''),
                source_system=transaction_data.get('source_system', 'Unknown'),
                client_ip=transaction_data.get('client_ip', ''),
                device_id=transaction_data.get('device_id', ''),
                timestamp=datetime.fromisoformat(transaction_data['timestamp'])
            )
            
            # Process the payment
            processing_start = time.time()
            result = await self.process_payment_transaction(payment_transaction)
            processing_time = int((time.time() - processing_start) * 1000)
            
            # Update processing record with result
            if result['success']:
                processing_record.status = ProcessingStatus.COMPLETED
                processing_record.completed_at = datetime.now()
                
                # Mark as completed in idempotency manager
                await self.idempotency_manager.mark_completed(idempotency_key, {
                    'transaction_id': transaction_id,
                    'result': result,
                    'processing_time_ms': processing_time,
                    'processed_by': self.processing_node
                })
                
                self.processed_count += 1
                logger.info(f"✅ Transaction processed successfully: {transaction_id}")
                
            else:
                processing_record.status = ProcessingStatus.FAILED
                processing_record.error_message = result.get('error', 'Unknown error')
                processing_record.retry_count += 1
                
                # Determine if should retry
                should_retry = processing_record.retry_count < self.max_retries
                retry_after = 60 * (2 ** processing_record.retry_count)  # Exponential backoff
                
                await self.idempotency_manager.mark_failed(
                    idempotency_key, 
                    result.get('error', 'Processing failed'),
                    retry_after if should_retry else None
                )
                
                self.error_count += 1
                logger.error(f"❌ Transaction processing failed: {transaction_id}")
            
            # Save final processing record
            self.db_manager.save_processing_record(processing_record)
            
        except Exception as e:
            logger.error(f"💥 Exactly-once processing error: {str(e)}")
            # Release lock in case of unexpected error
            if 'idempotency_key' in locals():
                await self.idempotency_manager.release_lock(idempotency_key)
            raise
    
    async def process_payment_transaction(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """
        Actual payment transaction process करो - business logic
        """
        try:
            # Save transaction to database first
            saved = self.db_manager.save_payment_transaction(transaction)
            if not saved:
                return {'success': False, 'error': 'Failed to save transaction'}
            
            # Simulate payment gateway processing
            await asyncio.sleep(0.1)  # Simulate network call
            
            # Simulate success/failure based on amount (for demo)
            if transaction.amount <= 0:
                return {'success': False, 'error': 'Invalid amount'}
            elif transaction.amount > 100000:  # Above 1 lakh INR
                return {'success': False, 'error': 'Amount exceeds limit'}
            elif transaction.user_id == 'blocked_user':
                return {'success': False, 'error': 'User blocked'}
            else:
                # Success case
                gateway_ref = f"GW{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
                
                # Save payment result
                self._save_payment_result(transaction, 'SUCCESS', gateway_ref)
                
                return {
                    'success': True,
                    'gateway_reference': gateway_ref,
                    'processed_amount': transaction.amount,
                    'currency': transaction.currency
                }
                
        except Exception as e:
            logger.error(f"💥 Payment processing error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _save_payment_result(self, transaction: PaymentTransaction, status: str, gateway_ref: str):
        """
        Payment result को database में save करो
        """
        try:
            with self.db_manager.get_transaction() as conn:
                cursor = conn.cursor()
                
                insert_sql = """
                INSERT INTO payment_results 
                (result_id, transaction_id, idempotency_key, status, gateway_reference, processed_at, processing_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (
                    str(uuid.uuid4()),
                    transaction.transaction_id,
                    transaction.idempotency_key,
                    status,
                    gateway_ref,
                    datetime.now(),
                    100  # Placeholder processing time
                ))
                
        except Exception as e:
            logger.error(f"💥 Failed to save payment result: {str(e)}")
    
    async def log_processing_metrics(self):
        """
        Processing metrics log करो
        """
        uptime = datetime.now()  # In production, track actual uptime
        
        metrics = {
            'processing_node': self.processing_node,
            'processed_transactions': self.processed_count,
            'duplicate_transactions': self.duplicate_count,
            'failed_transactions': self.error_count,
            'success_rate': round((self.processed_count / max(1, self.processed_count + self.error_count)) * 100, 2),
            'timestamp': uptime.isoformat()
        }
        
        logger.info(f"📊 Processing Metrics: {json.dumps(metrics)}")
        
        # Store metrics in Redis for monitoring
        await self.redis_client.setex(
            f"metrics:{self.processing_node}",
            300,  # 5 minutes TTL
            json.dumps(metrics, default=str)
        )
    
    async def cleanup(self):
        """
        System cleanup
        """
        logger.info("🧹 Cleaning up exactly-once processor")
        
        self.running = False
        
        if self.kafka_consumer:
            self.kafka_consumer.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ Cleanup completed")

class ExactlyOnceDemo:
    """
    Exactly-once processing का demo
    """
    
    def __init__(self):
        self.kafka_servers = ['localhost:9092']
        self.redis_url = 'redis://localhost:6379'
        self.db_params = {
            'host': 'localhost',
            'database': 'payment_processing',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        }
        
    def generate_test_transactions(self, count: int = 50) -> List[PaymentTransaction]:
        """
        Test transactions generate करो
        """
        transactions = []
        
        for i in range(count):
            # Deliberately create some duplicates for testing
            idempotency_key = f"PAY{i // 5:06d}"  # Every 5th transaction will have same key
            
            transaction = PaymentTransaction(
                transaction_id=f"TXN{datetime.now().strftime('%Y%m%d')}{i:06d}",
                idempotency_key=idempotency_key,
                user_id=f"user_{(i % 100) + 1:03d}",
                merchant_id=f"merchant_{(i % 20) + 1:03d}",
                amount=round(100 + (i % 5000) + (i * 0.37), 2),
                payment_method="UPI" if i % 2 == 0 else "CARD",
                source_system="PhonePe" if i % 3 == 0 else "GPay",
                description=f"Payment for order {i + 1000}",
                client_ip=f"192.168.1.{(i % 254) + 1}",
                device_id=f"device_{i % 50:03d}"
            )
            transactions.append(transaction)
        
        return transactions
    
    async def run_demo(self):
        """
        Complete exactly-once processing demo run करो
        """
        logger.info("🇮🇳 Starting Exactly-Once Processing Demo")
        
        # Initialize processor
        processor = ExactlyOnceProcessor(self.kafka_servers, self.redis_url, self.db_params)
        
        try:
            await processor.initialize()
            
            # Generate and send test transactions
            transactions = self.generate_test_transactions(20)
            await self.send_test_transactions(transactions)
            
            # Start processing
            logger.info("🎯 Starting message processing...")
            await processor.start_processing()
            
        except KeyboardInterrupt:
            logger.info("🛑 Demo interrupted by user")
        except Exception as e:
            logger.error(f"💥 Demo failed: {str(e)}")
        finally:
            await processor.cleanup()
    
    async def send_test_transactions(self, transactions: List[PaymentTransaction]):
        """
        Test transactions को Kafka में send करो
        """
        producer = KafkaProducer(
            bootstrap_servers=self.kafka_servers,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8')
        )
        
        try:
            for transaction in transactions:
                message_data = asdict(transaction)
                
                producer.send(
                    'payment-transactions',
                    key=transaction.idempotency_key,
                    value=message_data
                )
            
            producer.flush()
            logger.info(f"📤 Sent {len(transactions)} test transactions")
            
        except Exception as e:
            logger.error(f"💥 Failed to send test transactions: {str(e)}")
        finally:
            producer.close()

async def main():
    """Main function for demo"""
    demo = ExactlyOnceDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())

"""
Production Implementation Guide:

1. Kafka Configuration:
   - enable.idempotence=true on producers
   - isolation.level=read_committed on consumers  
   - Transaction support enabled
   - Proper partitioning strategy

2. Database Design:
   - UNIQUE constraints on idempotency keys
   - Proper indexing for fast lookups
   - Transaction isolation levels
   - Audit trails for compliance

3. Redis Configuration:
   - Persistence enabled (RDB + AOF)
   - Cluster setup for high availability
   - Memory policies for key eviction
   - Monitoring for key expiration

4. Monitoring & Alerting:
   - Duplicate detection metrics
   - Processing latency tracking
   - Error rate monitoring
   - Lock timeout alerts

5. Indian Financial Compliance:
   - RBI compliance for payment processing
   - PCI DSS requirements
   - Data localization requirements
   - Audit logging standards
"""