#!/usr/bin/env python3
"""
Real-time Streaming ETL - UPI Transaction Processing with Kafka
==============================================================

जैसे UPI में real-time payment processing होती है (immediate debit/credit),
वैसे ही streaming ETL करेंगे Kafka के साथ।

Real-world scale: NPCI processes 12 billion+ UPI transactions per month
Peak load: 1M+ transactions per minute during festivals

Author: DStudio Engineering Team  
Episode: 11 - ETL & Data Integration Patterns
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Kafka imports
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError

# Database imports
import redis
import psycopg2
from psycopg2.extras import execute_batch
from pymongo import MongoClient

# Validation और utilities
import uuid
from decimal import Decimal
import hashlib
import hmac

@dataclass
class UPITransaction:
    """UPI Transaction structure - NPCI standards के अनुसार"""
    transaction_id: str
    payer_vpa: str           # Virtual Payment Address (user@bank)
    payee_vpa: str
    amount: Decimal
    currency: str = "INR"
    transaction_type: str = "P2P"  # P2P, P2M, etc.
    bank_ref_no: str = ""
    merchant_code: Optional[str] = None
    category_code: str = ""
    timestamp: datetime = None
    status: str = "PENDING"   # PENDING, SUCCESS, FAILED
    failure_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if not self.bank_ref_no:
            self.bank_ref_no = f"BR{uuid.uuid4().hex[:12].upper()}"

@dataclass
class ProcessedTransaction:
    """Processed transaction with enriched data"""
    original_transaction: UPITransaction
    processing_timestamp: datetime
    fraud_score: float
    risk_category: str
    customer_segment: str
    transaction_pattern: str
    bank_processing_time_ms: int
    network_latency_ms: int

class UPIStreamingETL:
    """
    UPI Real-time Streaming ETL Pipeline
    ===================================
    
    NPCI जैसी real-time transaction processing:
    1. Kafka से transaction events consume करना
    2. Real-time fraud detection और validation
    3. Multiple destinations में parallel load करना
    """
    
    def __init__(self, kafka_config: Dict, redis_config: Dict, 
                 postgres_config: Dict, mongo_config: Dict):
        self.kafka_config = kafka_config
        self.redis_config = redis_config
        self.postgres_config = postgres_config
        self.mongo_config = mongo_config
        
        # Connections initialization
        self.producer = None
        self.consumer = None
        self.redis_client = None
        self.postgres_conn = None
        self.mongo_client = None
        
        self.logger = self._setup_logging()
        self.is_running = False
        
        # Processing statistics
        self.stats = {
            'processed_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'fraud_detected': 0,
            'start_time': None
        }
        
        # UPI business rules - RBI guidelines
        self.BUSINESS_RULES = {
            'max_transaction_amount': Decimal('200000'),  # 2 लाख limit per transaction
            'daily_transaction_limit': Decimal('1000000'), # 10 लाख daily limit
            'max_transactions_per_minute': 20,             # Rate limiting
            'fraud_threshold_score': 0.7,                 # Fraud detection threshold
            'high_value_threshold': Decimal('50000'),      # 50k+ needs extra validation
            'settlement_time_minutes': 2,                 # Max settlement time
            'retry_attempts': 3                           # Failed transaction retries
        }
        
    def _setup_logging(self):
        """Production-grade logging setup"""
        logger = logging.getLogger("UPIStreamingETL")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(
                f"upi_streaming_etl_{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [TXN:%(txn_id)s] - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def initialize_connections(self):
        """All connections को initialize करना"""
        try:
            # Kafka Producer - High throughput configuration
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: str(x).encode('utf-8'),
                compression_type='snappy',  # Better compression
                acks='all',                 # Ensure durability
                retries=3,
                batch_size=16384,          # Batching for efficiency
                linger_ms=10,              # Small delay for batching
                buffer_memory=33554432     # 32MB buffer
            )
            
            # Kafka Consumer - Real-time processing
            self.consumer = KafkaConsumer(
                'upi-transactions-raw',
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                auto_offset_reset='latest',  # Only new messages
                enable_auto_commit=True,
                group_id='upi-etl-processor',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000,   # 1 second timeout
                fetch_min_bytes=1024,       # Minimum fetch size
                max_poll_records=500        # Batch processing
            )
            
            # Redis - For caching और real-time lookups
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                db=self.redis_config['db'],
                password=self.redis_config.get('password'),
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # PostgreSQL - OLTP database for transactions
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            self.postgres_conn.autocommit = False  # Manual transaction control
            
            # MongoDB - Document store for analytics
            self.mongo_client = MongoClient(
                host=self.mongo_config['host'],
                port=self.mongo_config['port'],
                username=self.mongo_config.get('username'),
                password=self.mongo_config.get('password'),
                serverSelectionTimeoutMS=5000
            )
            
            self.logger.info("✅ All connections initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Connection initialization failed: {str(e)}")
            raise

    def validate_transaction(self, txn: UPITransaction) -> Dict:
        """
        UPI Transaction Validation - RBI compliance checks
        =================================================
        
        NPCI guidelines के अनुसार validation करना।
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. Amount validation
            if txn.amount <= 0:
                validation_result['errors'].append("Invalid amount: must be positive")
                validation_result['is_valid'] = False
            
            if txn.amount > self.BUSINESS_RULES['max_transaction_amount']:
                validation_result['errors'].append(f"Amount exceeds limit: ₹{txn.amount}")
                validation_result['is_valid'] = False
            
            # 2. VPA format validation
            def validate_vpa(vpa: str) -> bool:
                """VPA format: user@bank"""
                return '@' in vpa and len(vpa.split('@')) == 2
            
            if not validate_vpa(txn.payer_vpa):
                validation_result['errors'].append(f"Invalid payer VPA: {txn.payer_vpa}")
                validation_result['is_valid'] = False
                
            if not validate_vpa(txn.payee_vpa):
                validation_result['errors'].append(f"Invalid payee VPA: {txn.payee_vpa}")
                validation_result['is_valid'] = False
            
            # 3. Self-transaction check
            if txn.payer_vpa == txn.payee_vpa:
                validation_result['errors'].append("Self transaction not allowed")
                validation_result['is_valid'] = False
            
            # 4. Currency validation
            if txn.currency != 'INR':
                validation_result['errors'].append(f"Unsupported currency: {txn.currency}")
                validation_result['is_valid'] = False
            
            # 5. Transaction ID uniqueness (Redis check)
            if self.redis_client.exists(f"txn:{txn.transaction_id}"):
                validation_result['errors'].append("Duplicate transaction ID")
                validation_result['is_valid'] = False
            
            # 6. Rate limiting check - per user
            user_key = f"rate_limit:{txn.payer_vpa}"
            current_minute = datetime.now().strftime("%Y%m%d%H%M")
            rate_key = f"{user_key}:{current_minute}"
            
            current_count = self.redis_client.get(rate_key) or 0
            if int(current_count) >= self.BUSINESS_RULES['max_transactions_per_minute']:
                validation_result['errors'].append("Rate limit exceeded")
                validation_result['is_valid'] = False
            
            # 7. Daily limit check
            daily_key = f"daily_limit:{txn.payer_vpa}:{datetime.now().strftime('%Y%m%d')}"
            daily_amount = Decimal(self.redis_client.get(daily_key) or 0)
            
            if daily_amount + txn.amount > self.BUSINESS_RULES['daily_transaction_limit']:
                validation_result['errors'].append("Daily transaction limit exceeded")
                validation_result['is_valid'] = False
            
            # 8. High-value transaction warning
            if txn.amount >= self.BUSINESS_RULES['high_value_threshold']:
                validation_result['warnings'].append("High-value transaction - requires additional verification")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation system error: {str(e)}")
            return validation_result

    def calculate_fraud_score(self, txn: UPITransaction) -> float:
        """
        ML-based Fraud Detection Score
        =============================
        
        Real-time fraud detection - multiple parameters analyze करना।
        """
        try:
            fraud_factors = []
            
            # 1. Transaction amount pattern
            if txn.amount >= Decimal('100000'):  # 1 लाख+
                fraud_factors.append(0.3)
            elif txn.amount >= Decimal('50000'):   # 50k+
                fraud_factors.append(0.1)
            
            # 2. Time-based analysis
            hour = txn.timestamp.hour
            if hour < 6 or hour > 23:  # Late night transactions
                fraud_factors.append(0.2)
            
            # 3. User behavior pattern (Redis cache से)
            user_history_key = f"user_pattern:{txn.payer_vpa}"
            user_data = self.redis_client.hgetall(user_history_key)
            
            if user_data:
                avg_amount = float(user_data.get('avg_amount', 0))
                if float(txn.amount) > avg_amount * 5:  # 5x average amount
                    fraud_factors.append(0.4)
                
                last_txn_time = user_data.get('last_transaction_time')
                if last_txn_time:
                    time_diff = (datetime.now() - datetime.fromisoformat(last_txn_time)).seconds
                    if time_diff < 30:  # Very frequent transactions
                        fraud_factors.append(0.3)
            
            # 4. Geographical analysis (based on VPA bank)
            payer_bank = txn.payer_vpa.split('@')[1]
            payee_bank = txn.payee_vpa.split('@')[1]
            
            # Cross-bank transactions are slightly riskier
            if payer_bank != payee_bank:
                fraud_factors.append(0.05)
            
            # 5. Merchant transaction patterns
            if txn.transaction_type == 'P2M' and txn.merchant_code:
                merchant_risk = self.redis_client.get(f"merchant_risk:{txn.merchant_code}")
                if merchant_risk and float(merchant_risk) > 0.5:
                    fraud_factors.append(0.3)
            
            # Calculate final score
            base_score = sum(fraud_factors[:3])  # Main factors
            additional_score = sum(fraud_factors[3:]) * 0.5  # Secondary factors
            
            final_score = min(base_score + additional_score, 1.0)
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"❌ Fraud score calculation failed: {str(e)}")
            return 0.5  # Default medium risk

    def enrich_transaction(self, txn: UPITransaction) -> ProcessedTransaction:
        """
        Transaction enrichment - Additional business intelligence
        =======================================================
        
        Customer profiling, pattern analysis, performance metrics।
        """
        processing_start = time.time()
        
        try:
            # 1. Customer segmentation
            customer_key = f"customer_profile:{txn.payer_vpa}"
            customer_data = self.redis_client.hgetall(customer_key)
            
            if customer_data:
                total_transactions = int(customer_data.get('total_transactions', 0))
                if total_transactions > 1000:
                    customer_segment = 'VIP'
                elif total_transactions > 100:
                    customer_segment = 'Premium'
                elif total_transactions > 10:
                    customer_segment = 'Regular'
                else:
                    customer_segment = 'New'
            else:
                customer_segment = 'New'
            
            # 2. Transaction pattern analysis
            hour = txn.timestamp.hour
            if 9 <= hour <= 18:
                transaction_pattern = 'Business Hours'
            elif 18 <= hour <= 22:
                transaction_pattern = 'Evening Peak'
            elif 6 <= hour <= 9:
                transaction_pattern = 'Morning Rush'
            else:
                transaction_pattern = 'Off Hours'
            
            # 3. Performance metrics simulation
            bank_processing_time = 50 + (hash(txn.payer_vpa.split('@')[1]) % 100)  # 50-150ms
            network_latency = 10 + (hash(txn.transaction_id) % 40)  # 10-50ms
            
            # 4. Fraud score calculation
            fraud_score = self.calculate_fraud_score(txn)
            
            # 5. Risk categorization
            if fraud_score >= self.BUSINESS_RULES['fraud_threshold_score']:
                risk_category = 'HIGH'
            elif fraud_score >= 0.4:
                risk_category = 'MEDIUM'  
            else:
                risk_category = 'LOW'
            
            # Create processed transaction
            processed_txn = ProcessedTransaction(
                original_transaction=txn,
                processing_timestamp=datetime.now(),
                fraud_score=fraud_score,
                risk_category=risk_category,
                customer_segment=customer_segment,
                transaction_pattern=transaction_pattern,
                bank_processing_time_ms=bank_processing_time,
                network_latency_ms=network_latency
            )
            
            processing_time = (time.time() - processing_start) * 1000
            self.logger.info(f"✅ Transaction enriched in {processing_time:.2f}ms", 
                           extra={'txn_id': txn.transaction_id})
            
            return processed_txn
            
        except Exception as e:
            self.logger.error(f"❌ Transaction enrichment failed: {str(e)}", 
                            extra={'txn_id': txn.transaction_id})
            raise

    def update_user_patterns(self, txn: UPITransaction):
        """User behavior patterns को update करना - Real-time learning"""
        try:
            user_key = f"user_pattern:{txn.payer_vpa}"
            
            # Get current stats
            current_data = self.redis_client.hgetall(user_key)
            
            # Update stats
            new_data = {
                'last_transaction_time': txn.timestamp.isoformat(),
                'last_amount': str(txn.amount),
                'total_transactions': int(current_data.get('total_transactions', 0)) + 1,
                'total_amount': str(Decimal(current_data.get('total_amount', 0)) + txn.amount),
            }
            
            # Calculate average
            new_data['avg_amount'] = str(Decimal(new_data['total_amount']) / new_data['total_transactions'])
            
            # Update Redis with TTL (30 days)
            self.redis_client.hmset(user_key, new_data)
            self.redis_client.expire(user_key, 30 * 24 * 60 * 60)
            
            # Update rate limiting counters
            current_minute = datetime.now().strftime("%Y%m%d%H%M")
            rate_key = f"rate_limit:{txn.payer_vpa}:{current_minute}"
            self.redis_client.incr(rate_key)
            self.redis_client.expire(rate_key, 60)  # 1 minute TTL
            
            # Update daily limits
            daily_key = f"daily_limit:{txn.payer_vpa}:{datetime.now().strftime('%Y%m%d')}"
            self.redis_client.incrbyfloat(daily_key, float(txn.amount))
            self.redis_client.expire(daily_key, 24 * 60 * 60)  # 1 day TTL
            
        except Exception as e:
            self.logger.warning(f"⚠️ User pattern update failed: {str(e)}")

    def save_to_postgres(self, processed_txn: ProcessedTransaction):
        """PostgreSQL में transaction save करना - ACID compliance"""
        try:
            cursor = self.postgres_conn.cursor()
            
            # SQL query with proper indexing
            insert_query = """
            INSERT INTO upi_transactions (
                transaction_id, payer_vpa, payee_vpa, amount, currency,
                transaction_type, bank_ref_no, merchant_code, category_code,
                transaction_timestamp, processing_timestamp, status,
                fraud_score, risk_category, customer_segment,
                transaction_pattern, bank_processing_time_ms, network_latency_ms
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (transaction_id) DO NOTHING
            """
            
            txn = processed_txn.original_transaction
            cursor.execute(insert_query, (
                txn.transaction_id, txn.payer_vpa, txn.payee_vpa,
                float(txn.amount), txn.currency, txn.transaction_type,
                txn.bank_ref_no, txn.merchant_code, txn.category_code,
                txn.timestamp, processed_txn.processing_timestamp, txn.status,
                processed_txn.fraud_score, processed_txn.risk_category,
                processed_txn.customer_segment, processed_txn.transaction_pattern,
                processed_txn.bank_processing_time_ms, processed_txn.network_latency_ms
            ))
            
            self.postgres_conn.commit()
            
        except Exception as e:
            self.postgres_conn.rollback()
            self.logger.error(f"❌ PostgreSQL save failed: {str(e)}")
            raise

    def save_to_mongodb(self, processed_txn: ProcessedTransaction):
        """MongoDB में analytics data save करना - Flexible schema"""
        try:
            db = self.mongo_client['upi_analytics']
            collection = db['transaction_analytics']
            
            # Convert to MongoDB document
            doc = {
                '_id': processed_txn.original_transaction.transaction_id,
                'transaction_data': asdict(processed_txn.original_transaction),
                'processing_data': {
                    'processing_timestamp': processed_txn.processing_timestamp,
                    'fraud_score': processed_txn.fraud_score,
                    'risk_category': processed_txn.risk_category,
                    'customer_segment': processed_txn.customer_segment,
                    'transaction_pattern': processed_txn.transaction_pattern,
                    'performance_metrics': {
                        'bank_processing_time_ms': processed_txn.bank_processing_time_ms,
                        'network_latency_ms': processed_txn.network_latency_ms,
                        'total_processing_time_ms': processed_txn.bank_processing_time_ms + processed_txn.network_latency_ms
                    }
                },
                'metadata': {
                    'processed_date': processed_txn.processing_timestamp.strftime('%Y-%m-%d'),
                    'processed_hour': processed_txn.processing_timestamp.hour,
                    'payer_bank': processed_txn.original_transaction.payer_vpa.split('@')[1],
                    'payee_bank': processed_txn.original_transaction.payee_vpa.split('@')[1]
                }
            }
            
            collection.replace_one({'_id': doc['_id']}, doc, upsert=True)
            
        except Exception as e:
            self.logger.error(f"❌ MongoDB save failed: {str(e)}")
            # Don't raise - MongoDB failure shouldn't stop processing

    def publish_processed_transaction(self, processed_txn: ProcessedTransaction):
        """Processed transaction को downstream systems के लिए publish करना"""
        try:
            # Different topics for different purposes
            topics = {
                'upi-transactions-processed': processed_txn,  # General processed data
                'upi-fraud-alerts': processed_txn if processed_txn.risk_category == 'HIGH' else None,
                'upi-high-value': processed_txn if processed_txn.original_transaction.amount >= Decimal('50000') else None
            }
            
            for topic, data in topics.items():
                if data:
                    message = {
                        'transaction_id': data.original_transaction.transaction_id,
                        'timestamp': data.processing_timestamp.isoformat(),
                        'data': asdict(data)
                    }
                    
                    self.producer.send(
                        topic,
                        key=data.original_transaction.transaction_id,
                        value=message
                    )
            
            # Ensure messages are sent
            self.producer.flush()
            
        except Exception as e:
            self.logger.error(f"❌ Kafka publish failed: {str(e)}")

    def process_transaction(self, raw_transaction: Dict) -> bool:
        """Single transaction processing - Complete ETL pipeline"""
        transaction_id = raw_transaction.get('transaction_id', 'unknown')
        
        try:
            # 1. Parse raw transaction
            txn = UPITransaction(
                transaction_id=raw_transaction['transaction_id'],
                payer_vpa=raw_transaction['payer_vpa'],
                payee_vpa=raw_transaction['payee_vpa'],
                amount=Decimal(str(raw_transaction['amount'])),
                currency=raw_transaction.get('currency', 'INR'),
                transaction_type=raw_transaction.get('transaction_type', 'P2P'),
                merchant_code=raw_transaction.get('merchant_code'),
                category_code=raw_transaction.get('category_code', ''),
                timestamp=datetime.fromisoformat(raw_transaction['timestamp'])
            )
            
            # 2. Validate transaction
            validation_result = self.validate_transaction(txn)
            if not validation_result['is_valid']:
                self.logger.warning(f"⚠️ Transaction validation failed: {validation_result['errors']}", 
                                  extra={'txn_id': transaction_id})
                txn.status = 'FAILED'
                txn.failure_reason = '; '.join(validation_result['errors'])
                self.stats['failed_count'] += 1
                return False
            
            # 3. Enrich transaction
            processed_txn = self.enrich_transaction(txn)
            
            # 4. Update user patterns (async)
            self.update_user_patterns(txn)
            
            # 5. Save to multiple destinations
            # PostgreSQL (OLTP)
            self.save_to_postgres(processed_txn)
            
            # MongoDB (Analytics) 
            self.save_to_mongodb(processed_txn)
            
            # 6. Publish to downstream systems
            self.publish_processed_transaction(processed_txn)
            
            # 7. Update statistics
            self.stats['success_count'] += 1
            
            if processed_txn.risk_category == 'HIGH':
                self.stats['fraud_detected'] += 1
                self.logger.warning(f"🚨 Fraud alert: {transaction_id} - Score: {processed_txn.fraud_score}", 
                                  extra={'txn_id': transaction_id})
            
            self.logger.info(f"✅ Transaction processed successfully - Risk: {processed_txn.risk_category}", 
                           extra={'txn_id': transaction_id})
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Transaction processing failed: {str(e)}", 
                            extra={'txn_id': transaction_id})
            self.stats['failed_count'] += 1
            return False
        finally:
            self.stats['processed_count'] += 1

    def run_streaming_etl(self):
        """
        Main streaming ETL loop - Continuous processing
        =============================================
        
        Real-time UPI transaction processing loop।
        """
        self.logger.info("🚀 Starting UPI Streaming ETL Pipeline...")
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        try:
            self.initialize_connections()
            
            self.logger.info("🔄 Starting transaction consumption...")
            
            for message in self.consumer:
                if not self.is_running:
                    break
                
                try:
                    # Process transaction
                    raw_transaction = message.value
                    success = self.process_transaction(raw_transaction)
                    
                    # Performance logging (every 100 transactions)
                    if self.stats['processed_count'] % 100 == 0:
                        self._log_performance_stats()
                    
                except Exception as e:
                    self.logger.error(f"❌ Message processing failed: {str(e)}")
                    continue
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Received shutdown signal")
        except Exception as e:
            self.logger.error(f"💥 Streaming ETL failed: {str(e)}")
            raise
        finally:
            self.cleanup()

    def _log_performance_stats(self):
        """Performance statistics logging"""
        if self.stats['start_time']:
            duration = (datetime.now() - self.stats['start_time']).total_seconds()
            tps = self.stats['processed_count'] / duration if duration > 0 else 0
            success_rate = (self.stats['success_count'] / self.stats['processed_count'] * 100) if self.stats['processed_count'] > 0 else 0
            
            self.logger.info(f"📊 Performance Stats - TPS: {tps:.2f}, Success Rate: {success_rate:.1f}%, Fraud Detected: {self.stats['fraud_detected']}")

    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()
        if self.postgres_conn:
            self.postgres_conn.close()
        if self.mongo_client:
            self.mongo_client.close()
        if self.redis_client:
            self.redis_client.close()
        
        self.logger.info("🧹 Cleanup completed")

def main():
    """
    Production UPI Streaming ETL
    ===========================
    
    NPCI scale real-time transaction processing।
    """
    
    print("💳 UPI Real-time Streaming ETL Pipeline")
    print("=" * 45)
    
    # Production configurations
    kafka_config = {
        'bootstrap_servers': ['kafka1.upi.npci.gov.in:9092', 'kafka2.upi.npci.gov.in:9092']
    }
    
    redis_config = {
        'host': 'redis-cluster.upi.npci.gov.in',
        'port': 6379,
        'db': 0,
        'password': 'redis_secure_password'
    }
    
    postgres_config = {
        'host': 'postgres-primary.upi.npci.gov.in',
        'port': 5432,
        'database': 'upi_transactions',
        'user': 'upi_etl_user',
        'password': 'secure_etl_password'
    }
    
    mongo_config = {
        'host': 'mongodb-cluster.analytics.npci.gov.in',
        'port': 27017,
        'username': 'analytics_user',
        'password': 'mongo_secure_password'
    }
    
    # Initialize ETL pipeline
    etl_pipeline = UPIStreamingETL(kafka_config, redis_config, postgres_config, mongo_config)
    
    try:
        # Run streaming ETL
        etl_pipeline.run_streaming_etl()
        
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline stopped by user")
    except Exception as e:
        print(f"\n💥 Pipeline failed: {str(e)}")
        return False
    
    # Final statistics
    print(f"\n📊 Final Statistics:")
    print(f"   - Processed: {etl_pipeline.stats['processed_count']:,} transactions")
    print(f"   - Success: {etl_pipeline.stats['success_count']:,}")
    print(f"   - Failed: {etl_pipeline.stats['failed_count']:,}")
    print(f"   - Fraud Detected: {etl_pipeline.stats['fraud_detected']:,}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


# Production Deployment Architecture:
"""
🏗️ Production Architecture - NPCI Scale:

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bank Systems  │────│  Kafka Cluster  │────│  ETL Processors │
│                 │    │                 │    │                 │
│ • SBI           │    │ • 50+ Brokers   │    │ • 100+ Workers  │
│ • HDFC          │    │ • 3 AZ Setup    │    │ • Auto-scaling  │
│ • ICICI         │    │ • Replication=3 │    │ • Load Balanced │
│ • 200+ Banks    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Destinations                            │
│                                                                 │
│  PostgreSQL (OLTP)     Redis (Cache)      MongoDB (Analytics)  │
│  • Master-Slave        • Cluster Mode     • Replica Sets       │
│  • 99.99% Uptime       • Sub-ms latency   • Flexible Schema    │
│  • ACID Compliance     • Pattern Storage  • Real-time Analytics│
└─────────────────────────────────────────────────────────────────┘

📊 Scale Numbers:
- 12 billion+ transactions/month
- 1M+ peak TPS during festivals  
- 50TB+ data per day
- 200+ participating banks
- 99.99% availability requirement

💰 Cost Optimization:
- Kafka: ₹50 lakhs/month (managed service)
- Redis: ₹25 lakhs/month (cluster mode)
- PostgreSQL: ₹75 lakhs/month (managed)
- MongoDB: ₹40 lakhs/month (Atlas)
- ETL Compute: ₹60 lakhs/month (auto-scaling)

Total Monthly Cost: ₹2.5 crores for processing 12 billion transactions! 

UPI की speed और scale - यही है Digital India का power! 🇮🇳💥
"""