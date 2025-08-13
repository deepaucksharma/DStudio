#!/usr/bin/env python3
"""
Retry Mechanism with Exponential Backoff - Episode 50: System Design Interview Mastery
Flipkart Order Processing Retry System

Retry mechanism जैसे Mumbai local train wait करना है।
पहली train miss हुई तो 2 minute wait, फिर 4 minute, फिर 8 minute...

Author: Hindi Podcast Series
Topic: Retry Patterns with Exponential Backoff for Indian APIs
"""

import time
import random
import threading
import asyncio
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
from datetime import datetime, timedelta
import functools
import inspect

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Retry strategy types"""
    FIXED_DELAY = "fixed_delay"                    # Fixed interval
    LINEAR_BACKOFF = "linear_backoff"              # Linear increase
    EXPONENTIAL_BACKOFF = "exponential_backoff"    # Exponential increase
    JITTERED_BACKOFF = "jittered_backoff"         # Exponential + random jitter
    FIBONACCI_BACKOFF = "fibonacci_backoff"        # Fibonacci sequence

class RetryableException(Exception):
    """Base class for retryable exceptions"""
    pass

class TransientException(RetryableException):
    """Temporary failure - should retry"""
    pass

class PermanentException(Exception):
    """Permanent failure - should not retry"""
    pass

@dataclass
class RetryConfig:
    """Retry mechanism configuration"""
    max_attempts: int = 3                          # Maximum retry attempts
    base_delay: float = 1.0                       # Base delay in seconds
    max_delay: float = 60.0                       # Maximum delay cap
    backoff_multiplier: float = 2.0               # Backoff multiplication factor
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter_range: float = 0.1                     # Jitter percentage (0.1 = 10%)
    timeout_per_attempt: float = 30.0             # Timeout for each attempt
    
    # Retry conditions
    retryable_exceptions: List[type] = field(default_factory=lambda: [
        TransientException, ConnectionError, TimeoutError, 
        IOError, OSError
    ])
    
    non_retryable_exceptions: List[type] = field(default_factory=lambda: [
        PermanentException, ValueError, TypeError, AttributeError
    ])
    
    # HTTP status codes to retry (for API calls)
    retryable_status_codes: List[int] = field(default_factory=lambda: [
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504   # Gateway Timeout
    ])

@dataclass
class RetryAttempt:
    """Information about a retry attempt"""
    attempt_number: int
    start_time: float
    end_time: float = 0.0
    success: bool = False
    error: Optional[Exception] = None
    delay_before: float = 0.0
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.end_time == 0.0:
            self.end_time = time.time()
        self.response_time = self.end_time - self.start_time

class RetryStats:
    """Statistics tracking for retry operations"""
    
    def __init__(self):
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.total_attempts = 0
        self.retry_attempts = 0
        self.total_delay_time = 0.0
        self.total_execution_time = 0.0
        self.exception_counts = defaultdict(int)
        self.attempt_history = deque(maxlen=1000)  # Keep last 1000 operations
        self.lock = threading.Lock()
    
    def record_operation(self, attempts: List[RetryAttempt], final_success: bool):
        """Record an operation with all its attempts"""
        with self.lock:
            self.total_operations += 1
            self.total_attempts += len(attempts)
            
            if final_success:
                self.successful_operations += 1
            else:
                self.failed_operations += 1
            
            # Calculate metrics
            total_delay = sum(attempt.delay_before for attempt in attempts)
            total_execution = sum(attempt.response_time for attempt in attempts)
            
            self.total_delay_time += total_delay
            self.total_execution_time += total_execution
            
            # Count retry attempts (all attempts except the first)
            self.retry_attempts += len(attempts) - 1
            
            # Count exceptions
            for attempt in attempts:
                if attempt.error:
                    self.exception_counts[type(attempt.error).__name__] += 1
            
            # Store in history
            self.attempt_history.append({
                'timestamp': time.time(),
                'attempts': len(attempts),
                'success': final_success,
                'total_delay': total_delay,
                'total_time': total_execution
            })
    
    def get_stats(self) -> Dict:
        """Get retry statistics"""
        with self.lock:
            success_rate = (self.successful_operations / self.total_operations * 100 
                          if self.total_operations > 0 else 0)
            
            avg_attempts = (self.total_attempts / self.total_operations 
                          if self.total_operations > 0 else 0)
            
            avg_delay = (self.total_delay_time / self.total_operations 
                        if self.total_operations > 0 else 0)
            
            return {
                'total_operations': self.total_operations,
                'successful_operations': self.successful_operations,
                'failed_operations': self.failed_operations,
                'success_rate': success_rate,
                'total_attempts': self.total_attempts,
                'retry_attempts': self.retry_attempts,
                'average_attempts_per_operation': avg_attempts,
                'average_delay_per_operation': avg_delay,
                'total_delay_time': self.total_delay_time,
                'total_execution_time': self.total_execution_time,
                'exception_counts': dict(self.exception_counts)
            }

class RetryMechanism:
    """Retry mechanism with various backoff strategies"""
    
    def __init__(self, config: RetryConfig = None):
        """Initialize retry mechanism"""
        self.config = config or RetryConfig()
        self.stats = RetryStats()
        
        logger.info(f"🔄 Retry mechanism initialized - Strategy: {self.config.strategy.value}")
        logger.info(f"   Max attempts: {self.config.max_attempts}")
        logger.info(f"   Base delay: {self.config.base_delay}s")
    
    def _calculate_delay(self, attempt_number: int) -> float:
        """Calculate delay based on retry strategy"""
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt_number
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt_number - 1))
        
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            fib_sequence = self._fibonacci_sequence(attempt_number)
            delay = self.config.base_delay * fib_sequence
        
        elif self.config.strategy == RetryStrategy.JITTERED_BACKOFF:
            exponential_delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt_number - 1))
            jitter = exponential_delay * self.config.jitter_range * (2 * random.random() - 1)
            delay = exponential_delay + jitter
        
        else:
            delay = self.config.base_delay
        
        # Apply maximum delay cap
        delay = min(delay, self.config.max_delay)
        
        # Ensure minimum delay
        delay = max(delay, 0.1)
        
        return delay
    
    def _fibonacci_sequence(self, n: int) -> int:
        """Generate nth Fibonacci number"""
        if n <= 1:
            return 1
        elif n == 2:
            return 1
        
        a, b = 1, 1
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if exception is retryable"""
        # Check if it's explicitly non-retryable
        for non_retryable_type in self.config.non_retryable_exceptions:
            if isinstance(exception, non_retryable_type):
                return False
        
        # Check if it's explicitly retryable
        for retryable_type in self.config.retryable_exceptions:
            if isinstance(exception, retryable_type):
                return True
        
        # Check HTTP status codes if it's an HTTP exception
        if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
            status_code = exception.response.status_code
            return status_code in self.config.retryable_status_codes
        
        # Default: don't retry unknown exceptions
        return False
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        attempts = []
        last_exception = None
        
        for attempt_num in range(1, self.config.max_attempts + 1):
            attempt_start = time.time()
            
            # Calculate delay for this attempt (0 for first attempt)
            delay = 0.0 if attempt_num == 1 else self._calculate_delay(attempt_num)
            
            # Apply delay before attempt (except for first attempt)
            if delay > 0:
                logger.debug(f"Waiting {delay:.2f}s before attempt {attempt_num}")
                time.sleep(delay)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Success!
                attempt = RetryAttempt(
                    attempt_number=attempt_num,
                    start_time=attempt_start,
                    end_time=time.time(),
                    success=True,
                    delay_before=delay
                )
                attempts.append(attempt)
                
                logger.debug(f"Success on attempt {attempt_num}")
                self.stats.record_operation(attempts, True)
                
                return result
            
            except Exception as e:
                attempt_end = time.time()
                last_exception = e
                
                attempt = RetryAttempt(
                    attempt_number=attempt_num,
                    start_time=attempt_start,
                    end_time=attempt_end,
                    success=False,
                    error=e,
                    delay_before=delay
                )
                attempts.append(attempt)
                
                logger.debug(f"Attempt {attempt_num} failed: {e}")
                
                # Check if we should retry
                if attempt_num < self.config.max_attempts and self._is_retryable_exception(e):
                    logger.debug(f"Exception is retryable, will retry (attempt {attempt_num + 1})")
                    continue
                else:
                    # No more retries or non-retryable exception
                    break
        
        # All attempts failed
        self.stats.record_operation(attempts, False)
        
        logger.warning(f"All {len(attempts)} attempts failed. Last error: {last_exception}")
        raise last_exception
    
    def get_stats(self) -> Dict:
        """Get retry statistics"""
        return self.stats.get_stats()

def retry(config: RetryConfig = None):
    """Decorator for adding retry functionality to functions"""
    
    def decorator(func: Callable) -> Callable:
        retry_mechanism = RetryMechanism(config)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_mechanism.execute(func, *args, **kwargs)
        
        # Add stats method to decorated function
        wrapper.get_retry_stats = retry_mechanism.get_stats
        
        return wrapper
    
    return decorator

class FlipkartOrderProcessor:
    """Flipkart Order Processing with Retry Mechanisms"""
    
    def __init__(self):
        """Initialize Flipkart order processor"""
        
        # Different retry configurations for different operations
        self.retry_configs = {
            'inventory_check': RetryConfig(
                max_attempts=5,
                base_delay=0.5,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_multiplier=1.5
            ),
            'payment_processing': RetryConfig(
                max_attempts=3,
                base_delay=2.0,
                strategy=RetryStrategy.JITTERED_BACKOFF,
                max_delay=30.0
            ),
            'shipping_label': RetryConfig(
                max_attempts=4,
                base_delay=1.0,
                strategy=RetryStrategy.FIBONACCI_BACKOFF,
                max_delay=60.0
            ),
            'notification_send': RetryConfig(
                max_attempts=6,
                base_delay=0.3,
                strategy=RetryStrategy.LINEAR_BACKOFF,
                max_delay=10.0
            )
        }
        
        # Initialize retry mechanisms
        self.retry_mechanisms = {}
        for operation, config in self.retry_configs.items():
            self.retry_mechanisms[operation] = RetryMechanism(config)
        
        # Order processing statistics
        self.processing_stats = defaultdict(int)
        
        print("🛍️ Flipkart Order Processor initialized with retry mechanisms")
        for operation in self.retry_configs:
            print(f"   {operation}: {self.retry_configs[operation].strategy.value}")
    
    def _simulate_inventory_check(self, product_id: str, quantity: int) -> Dict:
        """Simulate inventory check with potential failures"""
        # Simulate network latency
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate different failure scenarios
        failure_chance = random.random()
        
        if failure_chance < 0.15:  # 15% timeout
            raise TimeoutError(f"Inventory service timeout for product {product_id}")
        elif failure_chance < 0.25:  # 10% connection error
            raise ConnectionError(f"Cannot connect to inventory service")
        elif failure_chance < 0.30:  # 5% temporary service error
            raise TransientException(f"Inventory service temporarily unavailable")
        
        # Success case
        available_stock = random.randint(0, 100)
        
        return {
            'product_id': product_id,
            'requested_quantity': quantity,
            'available_stock': available_stock,
            'stock_sufficient': available_stock >= quantity,
            'check_timestamp': time.time()
        }
    
    def _simulate_payment_processing(self, order_id: str, amount: float, payment_method: str) -> Dict:
        """Simulate payment processing with potential failures"""
        time.sleep(random.uniform(0.5, 1.5))
        
        failure_chance = random.random()
        
        if failure_chance < 0.20:  # 20% payment gateway errors
            if payment_method == 'credit_card':
                raise TransientException("Credit card gateway temporarily down")
            elif payment_method == 'upi':
                raise TransientException("UPI service unavailable")
            else:
                raise TransientException("Payment processing failed")
        elif failure_chance < 0.25:  # 5% permanent failures
            raise PermanentException("Invalid payment details")
        
        # Success case
        transaction_id = f"TXN_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return {
            'order_id': order_id,
            'transaction_id': transaction_id,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status': 'success',
            'processed_at': time.time()
        }
    
    def _simulate_shipping_label_generation(self, order_id: str, address: Dict) -> Dict:
        """Simulate shipping label generation with potential failures"""
        time.sleep(random.uniform(0.3, 0.8))
        
        failure_chance = random.random()
        
        if failure_chance < 0.18:  # 18% shipping service errors
            raise TransientException("Shipping label service overloaded")
        elif failure_chance < 0.22:  # 4% address validation errors
            raise PermanentException(f"Invalid shipping address for order {order_id}")
        
        # Success case
        tracking_number = f"FK{random.randint(100000000000, 999999999999)}"
        
        return {
            'order_id': order_id,
            'tracking_number': tracking_number,
            'shipping_partner': random.choice(['Ekart', 'BlueDart', 'DTDC']),
            'estimated_delivery': 'Tomorrow',
            'label_generated_at': time.time()
        }
    
    def _simulate_notification_send(self, user_id: str, message: str, channel: str) -> Dict:
        """Simulate notification sending with potential failures"""
        time.sleep(random.uniform(0.1, 0.3))
        
        failure_chance = random.random()
        
        if failure_chance < 0.12:  # 12% notification service errors
            if channel == 'sms':
                raise TransientException("SMS gateway rate limited")
            elif channel == 'email':
                raise TransientException("Email service temporarily down")
            else:
                raise TransientException("Push notification service unavailable")
        
        # Success case
        return {
            'user_id': user_id,
            'message': message,
            'channel': channel,
            'sent_at': time.time(),
            'status': 'delivered'
        }
    
    def process_order(self, order: Dict) -> Dict:
        """Process complete order with retry mechanisms"""
        order_id = order['order_id']
        start_time = time.time()
        
        try:
            logger.info(f"🛒 Processing order {order_id}")
            
            # Step 1: Check inventory with retry
            logger.debug(f"Checking inventory for order {order_id}")
            inventory_result = self.retry_mechanisms['inventory_check'].execute(
                self._simulate_inventory_check,
                order['product_id'],
                order['quantity']
            )
            
            if not inventory_result['stock_sufficient']:
                raise PermanentException(f"Insufficient stock for product {order['product_id']}")
            
            # Step 2: Process payment with retry
            logger.debug(f"Processing payment for order {order_id}")
            payment_result = self.retry_mechanisms['payment_processing'].execute(
                self._simulate_payment_processing,
                order_id,
                order['amount'],
                order['payment_method']
            )
            
            # Step 3: Generate shipping label with retry
            logger.debug(f"Generating shipping label for order {order_id}")
            shipping_result = self.retry_mechanisms['shipping_label'].execute(
                self._simulate_shipping_label_generation,
                order_id,
                order['shipping_address']
            )
            
            # Step 4: Send confirmation notification with retry
            logger.debug(f"Sending confirmation for order {order_id}")
            notification_result = self.retry_mechanisms['notification_send'].execute(
                self._simulate_notification_send,
                order['user_id'],
                f"Order {order_id} confirmed! Tracking: {shipping_result['tracking_number']}",
                'sms'
            )
            
            # Order processed successfully
            processing_time = time.time() - start_time
            self.processing_stats['successful_orders'] += 1
            
            logger.info(f"✅ Order {order_id} processed successfully in {processing_time:.2f}s")
            
            return {
                'order_id': order_id,
                'status': 'success',
                'processing_time': processing_time,
                'inventory_check': inventory_result,
                'payment': payment_result,
                'shipping': shipping_result,
                'notification': notification_result
            }
        
        except Exception as e:
            processing_time = time.time() - start_time
            self.processing_stats['failed_orders'] += 1
            
            logger.error(f"❌ Order {order_id} processing failed: {e}")
            
            return {
                'order_id': order_id,
                'status': 'failed',
                'processing_time': processing_time,
                'error': str(e)
            }
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed retry statistics for all operations"""
        detailed_stats = {
            'order_processing': dict(self.processing_stats),
            'retry_mechanisms': {}
        }
        
        for operation, retry_mechanism in self.retry_mechanisms.items():
            detailed_stats['retry_mechanisms'][operation] = retry_mechanism.get_stats()
        
        return detailed_stats

def demonstrate_retry_strategies():
    """Demonstrate different retry strategies"""
    print("🔄 Retry Strategies Demo - Different Backoff Patterns")
    print("=" * 60)
    
    strategies = [
        RetryStrategy.FIXED_DELAY,
        RetryStrategy.LINEAR_BACKOFF, 
        RetryStrategy.EXPONENTIAL_BACKOFF,
        RetryStrategy.JITTERED_BACKOFF,
        RetryStrategy.FIBONACCI_BACKOFF
    ]
    
    def failing_service() -> str:
        """Service that always fails for demonstration"""
        raise TransientException("Service consistently failing")
    
    print("\n📊 Comparing Retry Delay Patterns (5 attempts each):")
    print("-" * 55)
    
    for strategy in strategies:
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            strategy=strategy,
            backoff_multiplier=2.0
        )
        
        retry_mechanism = RetryMechanism(config)
        
        print(f"\n{strategy.value.upper()}:")
        delays = []
        
        for attempt in range(1, 6):
            if attempt == 1:
                delay = 0.0
            else:
                delay = retry_mechanism._calculate_delay(attempt)
            delays.append(delay)
            print(f"   Attempt {attempt}: {delay:.2f}s delay")
        
        total_delay = sum(delays)
        print(f"   Total delay: {total_delay:.2f}s")

def demonstrate_flipkart_order_processing():
    """Demonstrate Flipkart order processing with retries"""
    print("\n🛍️ Flipkart Order Processing Demo - E-commerce with Retries")
    print("=" * 65)
    
    # Initialize order processor
    processor = FlipkartOrderProcessor()
    
    # Sample orders with different characteristics
    sample_orders = [
        {
            'order_id': 'FK_ORDER_001',
            'user_id': 'user_9876543210',
            'product_id': 'MOBILE_IPHONE15',
            'quantity': 1,
            'amount': 79900.0,
            'payment_method': 'upi',
            'shipping_address': {
                'name': 'Rajesh Kumar',
                'address': '123, MG Road, Bangalore',
                'pincode': '560001',
                'phone': '+91 9876543210'
            }
        },
        {
            'order_id': 'FK_ORDER_002',
            'user_id': 'user_8765432109',
            'product_id': 'BOOK_ATOMIC_HABITS',
            'quantity': 2,
            'amount': 799.0,
            'payment_method': 'credit_card',
            'shipping_address': {
                'name': 'Priya Sharma',
                'address': '456, Bandra West, Mumbai',
                'pincode': '400050',
                'phone': '+91 8765432109'
            }
        },
        {
            'order_id': 'FK_ORDER_003',
            'user_id': 'user_7654321098',
            'product_id': 'LAPTOP_DELL',
            'quantity': 1,
            'amount': 55000.0,
            'payment_method': 'netbanking',
            'shipping_address': {
                'name': 'Amit Patel',
                'address': '789, Connaught Place, Delhi',
                'pincode': '110001',
                'phone': '+91 7654321098'
            }
        }
    ]
    
    print(f"\n📦 Processing {len(sample_orders)} orders with retry protection:")
    print("-" * 60)
    
    results = []
    
    for order in sample_orders:
        result = processor.process_order(order)
        results.append(result)
        
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"   {status_emoji} {result['order_id']}: {result['status'].upper()} "
              f"({result['processing_time']:.2f}s)")
        
        if result['status'] == 'failed':
            print(f"      Error: {result['error']}")
        
        time.sleep(0.5)  # Small delay between orders
    
    # Show processing summary
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len(results) - successful
    
    print(f"\n📈 Order Processing Summary:")
    print("-" * 30)
    print(f"   Total Orders: {len(results)}")
    print(f"   Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"   Failed: {failed} ({failed/len(results)*100:.1f}%)")
    
    # Show detailed retry statistics
    detailed_stats = processor.get_detailed_stats()
    
    print(f"\n🔄 Detailed Retry Statistics:")
    print("-" * 35)
    
    for operation, stats in detailed_stats['retry_mechanisms'].items():
        print(f"\n   {operation.upper()}:")
        print(f"     Total Operations: {stats['total_operations']}")
        print(f"     Success Rate: {stats['success_rate']:.1f}%")
        print(f"     Average Attempts: {stats['average_attempts_per_operation']:.1f}")
        print(f"     Total Retry Attempts: {stats['retry_attempts']}")
        print(f"     Average Delay: {stats['average_delay_per_operation']:.2f}s")
        
        if stats['exception_counts']:
            print(f"     Exception Types:")
            for exception_type, count in stats['exception_counts'].items():
                print(f"       {exception_type}: {count}")
    
    return processor

def demonstrate_decorator_usage():
    """Demonstrate retry decorator usage"""
    print("\n🎯 Retry Decorator Demo - Simplified Retry Usage")
    print("=" * 55)
    
    # Configure retry for different scenarios
    @retry(RetryConfig(
        max_attempts=4,
        base_delay=0.5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    ))
    def unreliable_api_call(api_endpoint: str, data: Dict) -> Dict:
        """Simulate unreliable API call"""
        time.sleep(random.uniform(0.2, 0.8))
        
        if random.random() < 0.4:  # 40% failure rate
            raise TransientException(f"API {api_endpoint} temporarily unavailable")
        
        return {
            'status': 'success',
            'endpoint': api_endpoint,
            'response_data': f"Processed {len(data)} items",
            'timestamp': time.time()
        }
    
    @retry(RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        strategy=RetryStrategy.JITTERED_BACKOFF
    ))
    def database_operation(query: str) -> Dict:
        """Simulate database operation with retries"""
        time.sleep(random.uniform(0.1, 0.5))
        
        if random.random() < 0.3:  # 30% failure rate
            raise ConnectionError("Database connection lost")
        
        return {
            'query': query,
            'rows_affected': random.randint(1, 100),
            'execution_time': random.uniform(0.1, 0.5)
        }
    
    print(f"\n🔌 Testing API calls with exponential backoff:")
    print("-" * 50)
    
    api_calls = [
        ('user_service/create', {'name': 'John', 'email': 'john@example.com'}),
        ('payment_service/process', {'amount': 1000, 'currency': 'INR'}),
        ('notification_service/send', {'type': 'sms', 'message': 'Hello'})
    ]
    
    for endpoint, data in api_calls:
        try:
            result = unreliable_api_call(endpoint, data)
            print(f"   ✅ {endpoint}: {result['response_data']}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Failed after retries - {e}")
    
    print(f"\n💾 Testing database operations with jittered backoff:")
    print("-" * 55)
    
    db_queries = [
        "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')",
        "UPDATE orders SET status = 'confirmed' WHERE id = 12345",
        "DELETE FROM temp_data WHERE created_at < '2024-01-01'"
    ]
    
    for query in db_queries:
        try:
            result = database_operation(query)
            print(f"   ✅ Query executed: {result['rows_affected']} rows affected")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    
    # Show decorator stats
    print(f"\n📊 Decorator Retry Statistics:")
    print("-" * 30)
    
    try:
        api_stats = unreliable_api_call.get_retry_stats()
        print(f"   API Calls:")
        print(f"     Success Rate: {api_stats['success_rate']:.1f}%")
        print(f"     Average Attempts: {api_stats['average_attempts_per_operation']:.1f}")
        print(f"     Total Retry Attempts: {api_stats['retry_attempts']}")
    except:
        print("   API stats not available")
    
    try:
        db_stats = database_operation.get_retry_stats()
        print(f"   Database Operations:")
        print(f"     Success Rate: {db_stats['success_rate']:.1f}%")
        print(f"     Average Attempts: {db_stats['average_attempts_per_operation']:.1f}")
        print(f"     Total Retry Attempts: {db_stats['retry_attempts']}")
    except:
        print("   Database stats not available")

def demonstrate_high_load_retry_scenario():
    """Demonstrate retry mechanism under high load"""
    print("\n⚡ High Load Retry Demo - Big Billion Day Traffic")
    print("=" * 55)
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Create high-load retry configuration
    high_load_config = RetryConfig(
        max_attempts=3,
        base_delay=0.2,
        strategy=RetryStrategy.JITTERED_BACKOFF,
        max_delay=5.0,
        jitter_range=0.3
    )
    
    retry_mechanism = RetryMechanism(high_load_config)
    
    def simulate_high_load_service(request_id: int) -> Dict:
        """Simulate service under high load"""
        # Higher failure rate during high load
        failure_rate = 0.4
        
        # Simulate variable response time
        time.sleep(random.uniform(0.05, 0.3))
        
        if random.random() < failure_rate:
            error_types = [
                TransientException("Service overloaded"),
                TimeoutError("Request timeout due to high load"),
                ConnectionError("Too many connections")
            ]
            raise random.choice(error_types)
        
        return {
            'request_id': request_id,
            'status': 'success',
            'processed_at': time.time()
        }
    
    print(f"🎯 Simulating Big Billion Day traffic (200 concurrent requests)...")
    
    start_time = time.time()
    successful_requests = 0
    failed_requests = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all requests
        futures = [
            executor.submit(retry_mechanism.execute, simulate_high_load_service, i)
            for i in range(200)
        ]
        
        # Process results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                successful_requests += 1
            except Exception as e:
                failed_requests += 1
            
            if (successful_requests + failed_requests) % 50 == 0:
                print(f"   Progress: {successful_requests + failed_requests}/200 requests processed")
    
    end_time = time.time()
    
    print(f"\n📊 High Load Test Results:")
    print("-" * 30)
    print(f"   Total Requests: 200")
    print(f"   Successful: {successful_requests} ({successful_requests/200*100:.1f}%)")
    print(f"   Failed: {failed_requests} ({failed_requests/200*100:.1f}%)")
    print(f"   Total Time: {end_time - start_time:.2f}s")
    print(f"   Throughput: {200/(end_time - start_time):.1f} requests/sec")
    
    # Show retry statistics
    final_stats = retry_mechanism.get_stats()
    print(f"\n🔄 Retry Performance:")
    print("-" * 20)
    print(f"   Total Operations: {final_stats['total_operations']}")
    print(f"   Total Attempts: {final_stats['total_attempts']}")
    print(f"   Retry Attempts: {final_stats['retry_attempts']}")
    print(f"   Average Attempts per Operation: {final_stats['average_attempts_per_operation']:.1f}")
    print(f"   Total Delay Time: {final_stats['total_delay_time']:.1f}s")
    print(f"   Average Delay per Operation: {final_stats['average_delay_per_operation']:.2f}s")

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_retry_strategies()
    
    print("\n" + "="*80 + "\n")
    
    flipkart_processor = demonstrate_flipkart_order_processing()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_decorator_usage()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_high_load_retry_scenario()
    
    print(f"\n✅ Retry Mechanism with Exponential Backoff Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Exponential Backoff - Increasing delay between retries")
    print(f"   • Jittered Backoff - Random variation to prevent thundering herd") 
    print(f"   • Linear/Fixed Backoff - Alternative delay strategies")
    print(f"   • Fibonacci Backoff - Fibonacci sequence delays")
    print(f"   • Retry Conditions - Retryable vs non-retryable exceptions")
    print(f"   • Statistics Tracking - Success rates and retry metrics")
    print(f"   • Decorator Pattern - Easy retry integration")
    print(f"   • Indian Context - Flipkart orders, UPI payments, API services")
    print(f"   • High Load Handling - Concurrent retry operations")