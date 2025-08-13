#!/usr/bin/env python3
"""
Advanced ETL Error Handling & Retry Patterns - Episode 11
Production-ready ETL with comprehensive error handling, circuit breakers, and retry mechanisms

यह production-grade ETL pipeline में complete error handling और retry patterns दिखाता है।
Real-world scenarios में data corruption, network failures, और timeout issues handle करना essential है।

Indian Context: IRCTC booking system style resilience for payment processing ETL
"""

import asyncio
import time
import json
import logging
import traceback
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random
import uuid
import hashlib
from contextlib import asynccontextmanager
import sqlite3
import aiohttp
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import backoff

# Configure logging - हिंदी comments के लिए UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_error_handling.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Error types for categorization"""
    TRANSIENT = "transient"  # Network timeouts, temporary DB locks
    PERMANENT = "permanent"  # Data validation failures, missing fields
    RESOURCE = "resource"    # Memory/disk full, connection pool exhausted
    BUSINESS = "business"    # Business rule violations
    UNKNOWN = "unknown"      # Unclassified errors

@dataclass
class ETLError:
    """ETL error information"""
    error_id: str
    error_type: ErrorType
    message: str
    context: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    is_recoverable: bool = True
    suggested_action: str = ""

@dataclass
class ProcessingResult:
    """Result of ETL processing"""
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    errors: List[ETLError] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class CircuitBreakerState(Enum):
    """Circuit breaker states - IRCTC payment gateway style"""
    CLOSED = "closed"      # Normal operation - सब ठीक है
    OPEN = "open"         # Failing fast - system down है
    HALF_OPEN = "half_open"  # Testing recovery - check kar रहे हैं

class CircuitBreaker:
    """
    Circuit breaker pattern for ETL operations
    IRCTC payment gateway जैसा behavior - अगर payment gateway down है तो immediately fail करो
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker moving to HALF_OPEN state - testing recovery")
            else:
                raise Exception(f"Circuit breaker OPEN - failing fast (failures: {self.failure_count})")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if not self.last_failure_time:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful operation"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info("Circuit breaker reset to CLOSED - recovery successful")
    
    def _on_failure(self):
        """Handle failure and update circuit breaker state"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(f"Circuit breaker OPEN - too many failures ({self.failure_count})")

class DeadLetterQueue:
    """
    Dead letter queue for failed ETL records
    Zomato order processing जैसा - अगर order process नहीं हो सकता तो DLQ में भेज दो
    """
    
    def __init__(self, db_path: str = "dlq.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize DLQ database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dead_letters (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_retry_at TIMESTAMP,
                is_resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_failed_record(self, record: Dict[str, Any], error: ETLError):
        """Add failed record to DLQ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        record_id = str(uuid.uuid4())
        data_json = json.dumps(record, default=str)
        
        cursor.execute('''
            INSERT INTO dead_letters (id, data, error_type, error_message, retry_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (record_id, data_json, error.error_type.value, error.message, error.retry_count))
        
        conn.commit()
        conn.close()
        
        logger.warning(f"Record added to DLQ: {record_id} - {error.message}")
        return record_id
    
    def get_retry_candidates(self, max_retry_count: int = 3) -> List[Tuple[str, Dict]]:
        """Get records eligible for retry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, data FROM dead_letters
            WHERE retry_count < ? AND is_resolved = FALSE
            AND (last_retry_at IS NULL OR last_retry_at < datetime('now', '-1 hour'))
        ''', (max_retry_count,))
        
        candidates = [(row[0], json.loads(row[1])) for row in cursor.fetchall()]
        conn.close()
        
        return candidates
    
    def mark_resolved(self, record_id: str):
        """Mark DLQ record as resolved"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE dead_letters SET is_resolved = TRUE WHERE id = ?
        ''', (record_id,))
        conn.commit()
        conn.close()

class DataValidator:
    """
    Comprehensive data validation for ETL
    Paytm transaction validation जैसा - हर field को thoroughly validate करो
    """
    
    @staticmethod
    def validate_payment_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate payment transaction record - Paytm style"""
        errors = []
        
        # Required fields validation
        required_fields = ['transaction_id', 'user_id', 'amount', 'currency', 'timestamp']
        for field in required_fields:
            if field not in record or not record[field]:
                errors.append(f"Missing required field: {field}")
        
        # Amount validation
        try:
            amount = float(record.get('amount', 0))
            if amount <= 0:
                errors.append("Amount must be positive")
            if amount > 100000:  # 1 lakh limit
                errors.append("Amount exceeds maximum limit (₹1,00,000)")
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        # Currency validation
        valid_currencies = ['INR', 'USD', 'EUR']
        if record.get('currency') not in valid_currencies:
            errors.append(f"Invalid currency. Must be one of: {valid_currencies}")
        
        # User ID validation (Indian mobile number format)
        user_id = record.get('user_id', '')
        if not user_id.startswith('+91') or len(user_id) != 13:
            errors.append("Invalid user_id format. Must be +91XXXXXXXXXX")
        
        # Timestamp validation
        try:
            timestamp = pd.to_datetime(record.get('timestamp'))
            if timestamp.year < 2020 or timestamp > pd.Timestamp.now():
                errors.append("Invalid timestamp - must be between 2020 and now")
        except:
            errors.append("Invalid timestamp format")
        
        return len(errors) == 0, errors

class AdvancedETLPipeline:
    """
    Production-ready ETL pipeline with comprehensive error handling
    
    यह pipeline real production scenarios handle करता है:
    - Network timeouts (IRCTC server busy)
    - Data corruption (incomplete transactions)
    - Resource exhaustion (memory/connection limits)
    - Business rule violations (invalid amounts)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60)
        )
        self.dlq = DeadLetterQueue()
        self.validator = DataValidator()
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'retried': 0,
            'dlq_sent': 0
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def extract_data_with_retry(self, source: str) -> List[Dict[str, Any]]:
        """
        Extract data with automatic retry for transient errors
        IRCTC API call जैसा - कभी कभी timeout होता है, retry करना पड़ता है
        """
        logger.info(f"Extracting data from source: {source}")
        
        try:
            # Simulate various extraction scenarios
            if source == "payment_api":
                return await self._extract_payment_data()
            elif source == "user_database":
                return await self._extract_user_data()
            elif source == "transaction_logs":
                return await self._extract_transaction_logs()
            else:
                raise ValueError(f"Unknown data source: {source}")
                
        except Exception as e:
            error = ETLError(
                error_id=str(uuid.uuid4()),
                error_type=self._classify_error(e),
                message=f"Data extraction failed: {str(e)}",
                context={'source': source},
                timestamp=datetime.now()
            )
            logger.error(f"Extraction error: {error.message}")
            raise e
    
    async def _extract_payment_data(self) -> List[Dict[str, Any]]:
        """Simulate payment API data extraction with potential failures"""
        
        # Simulate network issues (30% chance)
        if random.random() < 0.3:
            await asyncio.sleep(2)  # Simulate slow API
            if random.random() < 0.5:
                raise ConnectionError("Payment API connection timeout - server busy")
        
        # Generate sample payment data
        sample_data = []
        for i in range(100):
            # Introduce some invalid data (10% chance)
            if random.random() < 0.1:
                # Invalid record - missing required fields
                record = {
                    'transaction_id': f'TXN_{i}',
                    'amount': '',  # Missing amount
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Valid record
                record = {
                    'transaction_id': f'TXN_{i:06d}',
                    'user_id': f'+91{random.randint(7000000000, 9999999999)}',
                    'amount': round(random.uniform(100, 50000), 2),
                    'currency': 'INR',
                    'merchant': random.choice(['Zomato', 'Flipkart', 'Amazon', 'Swiggy']),
                    'payment_method': random.choice(['UPI', 'Card', 'Wallet']),
                    'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1440))).isoformat()
                }
            sample_data.append(record)
        
        logger.info(f"Extracted {len(sample_data)} payment records")
        return sample_data
    
    async def _extract_user_data(self) -> List[Dict[str, Any]]:
        """Simulate user database extraction"""
        # Simulate database connection issues
        if random.random() < 0.2:
            raise ConnectionError("Database connection pool exhausted")
        
        # Return sample user data
        return [
            {
                'user_id': f'+91{random.randint(7000000000, 9999999999)}',
                'name': f'User_{i}',
                'email': f'user{i}@example.com',
                'kyc_status': random.choice(['verified', 'pending', 'rejected']),
                'registration_date': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            }
            for i in range(50)
        ]
    
    async def _extract_transaction_logs(self) -> List[Dict[str, Any]]:
        """Simulate transaction log extraction"""
        await asyncio.sleep(0.5)  # Simulate file reading time
        return [
            {
                'log_id': str(uuid.uuid4()),
                'transaction_id': f'TXN_{i:06d}',
                'status': random.choice(['SUCCESS', 'FAILED', 'PENDING']),
                'processing_time': random.uniform(0.1, 2.0),
                'error_code': random.choice([None, 'E001', 'E002', 'E003']),
                'timestamp': datetime.now().isoformat()
            }
            for i in range(100)
        ]
    
    def transform_with_error_handling(self, records: List[Dict[str, Any]]) -> ProcessingResult:
        """
        Transform data with comprehensive error handling
        हर record को carefully process करते हैं - validation, business rules, etc.
        """
        result = ProcessingResult()
        start_time = time.time()
        
        for record in records:
            try:
                # Data validation - Paytm style strict validation
                is_valid, validation_errors = self.validator.validate_payment_record(record)
                
                if not is_valid:
                    error = ETLError(
                        error_id=str(uuid.uuid4()),
                        error_type=ErrorType.BUSINESS,
                        message=f"Validation failed: {'; '.join(validation_errors)}",
                        context={'record_id': record.get('transaction_id', 'unknown')},
                        timestamp=datetime.now(),
                        is_recoverable=False,
                        suggested_action="Fix data source validation"
                    )
                    result.errors.append(error)
                    result.failure_count += 1
                    
                    # Send to DLQ for manual review
                    self.dlq.add_failed_record(record, error)
                    continue
                
                # Business rule validation
                transformed_record = self._apply_business_rules(record)
                
                if transformed_record is None:
                    result.skipped_count += 1
                    continue
                
                # Successful transformation
                result.success_count += 1
                
            except Exception as e:
                error = ETLError(
                    error_id=str(uuid.uuid4()),
                    error_type=self._classify_error(e),
                    message=str(e),
                    context={'record': record},
                    timestamp=datetime.now()
                )
                result.errors.append(error)
                result.failure_count += 1
                
                # Add to DLQ if recoverable
                if error.is_recoverable:
                    self.dlq.add_failed_record(record, error)
        
        result.processing_time = time.time() - start_time
        logger.info(f"Transformation completed - Success: {result.success_count}, Failed: {result.failure_count}, Skipped: {result.skipped_count}")
        
        return result
    
    def _apply_business_rules(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply business rules and transformations
        Flipkart order processing जैसे business rules
        """
        
        # Skip test transactions
        if record.get('transaction_id', '').startswith('TEST_'):
            return None
        
        # Currency conversion if needed
        amount = float(record['amount'])
        if record['currency'] != 'INR':
            # Simulate currency conversion
            conversion_rates = {'USD': 82.0, 'EUR': 89.0}
            amount = amount * conversion_rates.get(record['currency'], 1.0)
            record['original_amount'] = record['amount']
            record['original_currency'] = record['currency']
            record['amount'] = amount
            record['currency'] = 'INR'
        
        # Add derived fields
        record['amount_category'] = self._categorize_amount(amount)
        record['risk_score'] = self._calculate_risk_score(record)
        record['processed_at'] = datetime.now().isoformat()
        record['etl_version'] = '2.1.0'
        
        # Generate unique hash for deduplication
        record_hash = hashlib.md5(
            f"{record['transaction_id']}{record['user_id']}{record['amount']}".encode()
        ).hexdigest()
        record['record_hash'] = record_hash
        
        return record
    
    def _categorize_amount(self, amount: float) -> str:
        """Categorize transaction amount - Indian context"""
        if amount < 100:
            return 'micro'      # छोटी amount - tea/coffee
        elif amount < 1000:
            return 'small'      # Regular amount - food delivery
        elif amount < 10000:
            return 'medium'     # Shopping - clothes, electronics
        elif amount < 50000:
            return 'large'      # Big purchases - appliances
        else:
            return 'jumbo'      # Very high - property, gold
    
    def _calculate_risk_score(self, record: Dict[str, Any]) -> float:
        """Calculate fraud risk score"""
        risk_score = 0.0
        
        # High amount risk
        amount = float(record['amount'])
        if amount > 25000:
            risk_score += 0.3
        
        # Late night transactions (Indian time zone)
        try:
            tx_time = pd.to_datetime(record['timestamp'])
            if tx_time.hour < 6 or tx_time.hour > 22:
                risk_score += 0.2
        except:
            pass
        
        # New user risk (simulate)
        if random.random() < 0.1:  # 10% new users
            risk_score += 0.25
        
        return min(risk_score, 1.0)
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=300
    )
    async def load_with_circuit_breaker(self, records: List[Dict[str, Any]], destination: str) -> ProcessingResult:
        """
        Load data with circuit breaker protection
        Database या warehouse में data load करते समय circuit breaker use करते हैं
        """
        
        def _load_batch():
            """Internal load function protected by circuit breaker"""
            logger.info(f"Loading {len(records)} records to {destination}")
            
            # Simulate various loading scenarios
            if random.random() < 0.1:  # 10% chance of failure
                if random.random() < 0.5:
                    raise ConnectionError(f"Connection to {destination} failed")
                else:
                    raise Exception(f"Warehouse {destination} storage full")
            
            # Simulate successful load
            time.sleep(0.5)  # Simulate processing time
            logger.info(f"Successfully loaded {len(records)} records to {destination}")
            return len(records)
        
        try:
            loaded_count = self.circuit_breaker.call(_load_batch)
            return ProcessingResult(success_count=loaded_count)
            
        except Exception as e:
            error = ETLError(
                error_id=str(uuid.uuid4()),
                error_type=self._classify_error(e),
                message=f"Load failed: {str(e)}",
                context={'destination': destination, 'record_count': len(records)},
                timestamp=datetime.now()
            )
            
            result = ProcessingResult(failure_count=len(records))
            result.errors.append(error)
            
            logger.error(f"Load failed: {error.message}")
            return result
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type for appropriate handling"""
        error_message = str(error).lower()
        
        if any(keyword in error_message for keyword in ['timeout', 'connection', 'network']):
            return ErrorType.TRANSIENT
        elif any(keyword in error_message for keyword in ['validation', 'format', 'required']):
            return ErrorType.BUSINESS
        elif any(keyword in error_message for keyword in ['memory', 'disk', 'pool']):
            return ErrorType.RESOURCE
        elif any(keyword in error_message for keyword in ['permission', 'access', 'auth']):
            return ErrorType.PERMANENT
        else:
            return ErrorType.UNKNOWN
    
    async def run_pipeline_with_monitoring(self, sources: List[str]) -> Dict[str, Any]:
        """
        Run complete ETL pipeline with comprehensive monitoring and error handling
        Production-ready pipeline जो सभी scenarios handle करता है
        """
        
        pipeline_start = time.time()
        overall_result = {
            'pipeline_id': str(uuid.uuid4()),
            'start_time': datetime.now().isoformat(),
            'sources': sources,
            'results': {},
            'errors': [],
            'summary': {}
        }
        
        logger.info(f"Starting ETL pipeline for sources: {sources}")
        
        for source in sources:
            source_start = time.time()
            
            try:
                # Extract phase with retry
                logger.info(f"Processing source: {source}")
                raw_data = await self.extract_data_with_retry(source)
                
                # Transform phase with error handling
                transform_result = self.transform_with_error_handling(raw_data)
                
                # Load phase with circuit breaker
                if transform_result.success_count > 0:
                    # Create sample transformed records for loading
                    load_result = await self.load_with_circuit_breaker(
                        records=[f"transformed_record_{i}" for i in range(transform_result.success_count)],
                        destination=f"{source}_warehouse"
                    )
                else:
                    load_result = ProcessingResult()
                
                # Store source results
                overall_result['results'][source] = {
                    'extract_count': len(raw_data),
                    'transform_result': {
                        'success': transform_result.success_count,
                        'failed': transform_result.failure_count,
                        'skipped': transform_result.skipped_count,
                        'processing_time': transform_result.processing_time
                    },
                    'load_result': {
                        'success': load_result.success_count,
                        'failed': load_result.failure_count
                    },
                    'processing_time': time.time() - source_start,
                    'errors': [
                        {
                            'error_id': error.error_id,
                            'type': error.error_type.value,
                            'message': error.message,
                            'is_recoverable': error.is_recoverable
                        }
                        for error in transform_result.errors + load_result.errors
                    ]
                }
                
                # Update stats
                self.processing_stats['total_processed'] += len(raw_data)
                self.processing_stats['successful'] += transform_result.success_count
                self.processing_stats['failed'] += transform_result.failure_count
                
                logger.info(f"Completed processing source: {source}")
                
            except Exception as e:
                error = ETLError(
                    error_id=str(uuid.uuid4()),
                    error_type=self._classify_error(e),
                    message=f"Pipeline failed for source {source}: {str(e)}",
                    context={'source': source},
                    timestamp=datetime.now()
                )
                
                overall_result['errors'].append({
                    'source': source,
                    'error_id': error.error_id,
                    'type': error.error_type.value,
                    'message': error.message,
                    'traceback': traceback.format_exc()
                })
                
                logger.error(f"Pipeline failed for source {source}: {e}")
        
        # Pipeline summary
        total_time = time.time() - pipeline_start
        overall_result['end_time'] = datetime.now().isoformat()
        overall_result['total_processing_time'] = total_time
        overall_result['summary'] = {
            'total_sources': len(sources),
            'successful_sources': len([s for s in sources if s in overall_result['results']]),
            'failed_sources': len(overall_result['errors']),
            'overall_stats': self.processing_stats.copy(),
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'dlq_entries': len(self.dlq.get_retry_candidates(max_retry_count=10))
        }
        
        logger.info(f"ETL Pipeline completed in {total_time:.2f}s - Stats: {self.processing_stats}")
        
        return overall_result
    
    async def retry_dlq_records(self) -> Dict[str, Any]:
        """
        Process records from dead letter queue
        DLQ से records को retry करने का process - Paytm failed payment retry जैसा
        """
        
        logger.info("Starting DLQ retry process")
        retry_candidates = self.dlq.get_retry_candidates()
        
        retry_results = {
            'total_candidates': len(retry_candidates),
            'successful_retries': 0,
            'failed_retries': 0,
            'results': []
        }
        
        for record_id, record_data in retry_candidates:
            try:
                # Re-validate and transform
                is_valid, validation_errors = self.validator.validate_payment_record(record_data)
                
                if is_valid:
                    transformed = self._apply_business_rules(record_data)
                    if transformed:
                        # Attempt to load
                        load_result = await self.load_with_circuit_breaker([transformed], "retry_warehouse")
                        
                        if load_result.success_count > 0:
                            self.dlq.mark_resolved(record_id)
                            retry_results['successful_retries'] += 1
                            logger.info(f"Successfully retried DLQ record: {record_id}")
                        else:
                            retry_results['failed_retries'] += 1
                    else:
                        # Record should be skipped
                        self.dlq.mark_resolved(record_id)
                        retry_results['successful_retries'] += 1
                else:
                    # Still invalid - keep in DLQ
                    retry_results['failed_retries'] += 1
                    logger.warning(f"DLQ record still invalid: {record_id} - {validation_errors}")
                    
            except Exception as e:
                retry_results['failed_retries'] += 1
                logger.error(f"DLQ retry failed for {record_id}: {e}")
        
        logger.info(f"DLQ retry completed - Success: {retry_results['successful_retries']}, Failed: {retry_results['failed_retries']}")
        return retry_results

async def main():
    """
    Main function demonstrating advanced ETL error handling
    Production-ready pipeline का complete demo
    """
    
    # Configuration - Production settings
    config = {
        'failure_threshold': 3,      # Circuit breaker threshold
        'recovery_timeout': 30,      # Circuit breaker recovery time
        'max_retry_attempts': 3,     # Maximum retry attempts
        'batch_size': 1000,         # Processing batch size
        'enable_monitoring': True,   # Enable detailed monitoring
        'dlq_enabled': True         # Enable dead letter queue
    }
    
    # Initialize ETL pipeline
    pipeline = AdvancedETLPipeline(config)
    
    logger.info("🚀 Starting Advanced ETL Pipeline with Error Handling")
    logger.info("यह pipeline production-ready है और सभी error scenarios handle करता है")
    
    try:
        # Run main ETL pipeline
        sources = ['payment_api', 'user_database', 'transaction_logs']
        pipeline_result = await pipeline.run_pipeline_with_monitoring(sources)
        
        # Print results
        print("\n" + "="*80)
        print("📊 ETL PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Pipeline ID: {pipeline_result['pipeline_id']}")
        print(f"Total Processing Time: {pipeline_result['total_processing_time']:.2f} seconds")
        print(f"Sources Processed: {pipeline_result['summary']['successful_sources']}/{pipeline_result['summary']['total_sources']}")
        
        print(f"\n🔢 PROCESSING STATISTICS:")
        stats = pipeline_result['summary']['overall_stats']
        print(f"  • Total Records: {stats['total_processed']}")
        print(f"  • Successful: {stats['successful']}")
        print(f"  • Failed: {stats['failed']}")
        print(f"  • DLQ Entries: {pipeline_result['summary']['dlq_entries']}")
        
        print(f"\n⚡ CIRCUIT BREAKER STATUS:")
        print(f"  • Current State: {pipeline_result['summary']['circuit_breaker_state'].upper()}")
        
        # Show detailed results for each source
        print(f"\n📋 DETAILED SOURCE RESULTS:")
        for source, result in pipeline_result['results'].items():
            print(f"\n  {source}:")
            print(f"    Extracted: {result['extract_count']} records")
            print(f"    Transformed: {result['transform_result']['success']} success, {result['transform_result']['failed']} failed")
            print(f"    Loaded: {result['load_result']['success']} success")
            print(f"    Processing Time: {result['processing_time']:.2f}s")
            
            if result['errors']:
                print(f"    Errors ({len(result['errors'])}):")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"      - {error['type']}: {error['message'][:100]}...")
        
        # Show pipeline errors
        if pipeline_result['errors']:
            print(f"\n❌ PIPELINE ERRORS:")
            for error in pipeline_result['errors']:
                print(f"  • {error['source']}: {error['message']}")
        
        print(f"\n🔄 PROCESSING DLQ RETRIES...")
        # Process DLQ retries
        retry_results = await pipeline.retry_dlq_records()
        print(f"DLQ Retry Results:")
        print(f"  • Candidates: {retry_results['total_candidates']}")
        print(f"  • Successful: {retry_results['successful_retries']}")
        print(f"  • Failed: {retry_results['failed_retries']}")
        
        print(f"\n✅ Advanced ETL Pipeline demonstration completed successfully!")
        print("यह production-grade ETL pipeline है जो real-world scenarios handle करता है।")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        print("Check logs for detailed error information.")

if __name__ == "__main__":
    # Run the advanced ETL pipeline
    asyncio.run(main())