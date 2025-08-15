#!/usr/bin/env python3
"""
Circuit Breaker with Advanced Retry Mechanisms
Retry patterns के साथ circuit breaker का intelligent combination

Retry और circuit breaker together use करने से graceful degradation मिलता है
Different retry strategies different scenarios के लिए suitable हैं
"""

import time
import random
import threading
import asyncio
from enum import Enum
from typing import Callable, Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
import json
import functools


class RetryStrategy(Enum):
    """Different retry strategies"""
    FIXED_DELAY = "fixed_delay"                # Fixed time between retries
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # Exponentially increasing delay
    LINEAR_BACKOFF = "linear_backoff"          # Linearly increasing delay
    RANDOM_JITTER = "random_jitter"            # Random delay within range
    FIBONACCI_BACKOFF = "fibonacci_backoff"    # Fibonacci sequence delays
    CUSTOM_INTERVALS = "custom_intervals"      # User-defined intervals


class RetryCondition(Enum):
    """Conditions under which to retry"""
    ALL_EXCEPTIONS = "all_exceptions"          # Retry on any exception
    SPECIFIC_EXCEPTIONS = "specific_exceptions"  # Retry only on specific exceptions
    HTTP_STATUS_CODES = "http_status_codes"    # Retry on specific HTTP status codes
    CUSTOM_CONDITION = "custom_condition"      # Custom retry condition function
    TRANSIENT_FAILURES = "transient_failures" # Common transient failure patterns


@dataclass
class RetryConfig:
    """Configuration for retry mechanism"""
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    jitter: bool = True
    jitter_range: tuple = (0.1, 0.9)  # Random multiplier range
    
    # Retry conditions
    retry_condition: RetryCondition = RetryCondition.TRANSIENT_FAILURES
    retryable_exceptions: List[type] = field(default_factory=lambda: [ConnectionError, TimeoutError])
    retryable_http_codes: List[int] = field(default_factory=lambda: [502, 503, 504])
    custom_intervals: List[float] = field(default_factory=list)
    custom_condition_func: Optional[Callable[[Exception], bool]] = None
    
    # Circuit breaker integration
    count_retries_as_failures: bool = False  # Whether retries count as circuit breaker failures
    stop_retries_when_circuit_open: bool = True  # Stop retrying when circuit opens
    
    # Adaptive retry
    enable_adaptive_retry: bool = False      # Adjust retry behavior based on success rate
    success_threshold: float = 0.8           # Success rate threshold for adaptation
    adaptation_window: int = 100             # Number of requests to consider for adaptation


@dataclass
class RetryMetrics:
    """Metrics for retry operations"""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    total_retries: int = 0
    avg_attempts_per_request: float = 0.0
    avg_retry_delay: float = 0.0
    retry_success_rate: float = 0.0
    adaptive_adjustments: int = 0
    retry_by_strategy: Dict[str, int] = field(default_factory=dict)


class RetryCircuitBreaker:
    """
    Advanced Circuit Breaker with sophisticated retry mechanisms
    यह implementation retry और circuit breaker को intelligently combine करती है
    """
    
    def __init__(
        self,
        name: str,
        retry_config: RetryConfig,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 30.0,
        enable_metrics: bool = True
    ):
        self.name = name
        self.retry_config = retry_config
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_recovery_timeout = circuit_recovery_timeout
        self.enable_metrics = enable_metrics
        
        # Circuit breaker state
        self.circuit_state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        # Retry metrics
        self.retry_metrics = RetryMetrics()
        
        # Adaptive retry tracking
        self.recent_requests = []  # Store recent request outcomes
        self.current_retry_config = retry_config  # May be adjusted adaptively
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"🔄 Retry Circuit Breaker '{name}' initialized")
        print(f"   - Max attempts: {retry_config.max_attempts}")
        print(f"   - Strategy: {retry_config.strategy.value}")
        print(f"   - Base delay: {retry_config.base_delay}s")
        print(f"   - Circuit failure threshold: {circuit_failure_threshold}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic and circuit breaker protection
        """
        with self._lock:
            # Check circuit state first
            if self._should_reject_due_to_circuit():
                raise CircuitBreakerOpenError(f"Circuit '{self.name}' is OPEN")
        
        # Execute with retries
        return self._execute_with_retries(func, args, kwargs)
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Async version of call method
        """
        with self._lock:
            if self._should_reject_due_to_circuit():
                raise CircuitBreakerOpenError(f"Circuit '{self.name}' is OPEN")
        
        return await self._execute_with_retries_async(func, args, kwargs)
    
    def _should_reject_due_to_circuit(self) -> bool:
        """Check if request should be rejected due to circuit state"""
        if self.circuit_state == "CLOSED":
            return False
        
        if self.circuit_state == "OPEN":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.circuit_recovery_timeout:
                    self.circuit_state = "HALF_OPEN"
                    self.success_count = 0
                    print(f"🟡 Circuit '{self.name}' moved to HALF_OPEN")
                    return False
            return True
        
        # HALF_OPEN state - allow requests but be ready to open again
        return False
    
    def _execute_with_retries(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """
        Execute function with retry logic
        """
        last_exception = None
        attempt_count = 0
        total_delay = 0.0
        
        # Update adaptive retry config if enabled
        if self.retry_config.enable_adaptive_retry:
            self._adapt_retry_config()
        
        config = self.current_retry_config
        
        for attempt in range(1, config.max_attempts + 1):
            attempt_count = attempt
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Success - handle metrics and circuit state
                execution_time = time.time() - start_time
                self._handle_success(attempt, execution_time, total_delay)
                
                if attempt > 1:
                    print(f"✅ Success after {attempt} attempts (total delay: {total_delay:.2f}s)")
                
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                last_exception = e
                
                # Check if we should retry
                should_retry = self._should_retry(e, attempt, config.max_attempts)
                
                if not should_retry:
                    # No more retries - handle failure
                    self._handle_failure(e, attempt, execution_time, total_delay)
                    break
                
                # Calculate retry delay
                retry_delay = self._calculate_retry_delay(attempt, config)
                total_delay += retry_delay
                
                print(f"❌ Attempt {attempt} failed: {str(e)[:40]} - Retrying in {retry_delay:.2f}s")
                
                # Check if circuit opened during execution
                with self._lock:
                    if (self.circuit_state == "OPEN" and 
                        self.retry_config.stop_retries_when_circuit_open):
                        print(f"🔴 Circuit opened - Stopping retries")
                        self._handle_failure(e, attempt, execution_time, total_delay)
                        break
                
                # Wait before retry
                time.sleep(retry_delay)
        
        # All retries exhausted
        self._handle_failure(last_exception, attempt_count, 0, total_delay)
        raise last_exception
    
    async def _execute_with_retries_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """
        Async version of retry execution
        """
        last_exception = None
        attempt_count = 0
        total_delay = 0.0
        
        config = self.current_retry_config
        
        for attempt in range(1, config.max_attempts + 1):
            attempt_count = attempt
            start_time = time.time()
            
            try:
                # Execute async function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    # Run sync function in executor
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, func, *args, **kwargs)
                
                execution_time = time.time() - start_time
                self._handle_success(attempt, execution_time, total_delay)
                
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                last_exception = e
                
                if not self._should_retry(e, attempt, config.max_attempts):
                    self._handle_failure(e, attempt, execution_time, total_delay)
                    break
                
                retry_delay = self._calculate_retry_delay(attempt, config)
                total_delay += retry_delay
                
                print(f"❌ Async attempt {attempt} failed: {str(e)[:40]} - Retrying in {retry_delay:.2f}s")
                
                await asyncio.sleep(retry_delay)
        
        self._handle_failure(last_exception, attempt_count, 0, total_delay)
        raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int, max_attempts: int) -> bool:
        """
        Determine if we should retry based on exception and configuration
        """
        if attempt >= max_attempts:
            return False
        
        condition = self.retry_config.retry_condition
        
        if condition == RetryCondition.ALL_EXCEPTIONS:
            return True
        
        elif condition == RetryCondition.SPECIFIC_EXCEPTIONS:
            return type(exception) in self.retry_config.retryable_exceptions
        
        elif condition == RetryCondition.HTTP_STATUS_CODES:
            # For HTTP status codes, check if exception has status code
            status_code = getattr(exception, 'status_code', None) or getattr(exception, 'code', None)
            if status_code:
                return status_code in self.retry_config.retryable_http_codes
            return False
        
        elif condition == RetryCondition.CUSTOM_CONDITION:
            if self.retry_config.custom_condition_func:
                return self.retry_config.custom_condition_func(exception)
            return False
        
        elif condition == RetryCondition.TRANSIENT_FAILURES:
            # Common transient failure patterns
            transient_patterns = [
                "timeout",
                "connection",
                "network",
                "temporary",
                "unavailable",
                "overloaded",
                "rate limit",
                "throttle"
            ]
            
            exception_str = str(exception).lower()
            return any(pattern in exception_str for pattern in transient_patterns)
        
        return False
    
    def _calculate_retry_delay(self, attempt: int, config: RetryConfig) -> float:
        """
        Calculate delay before next retry attempt
        """
        strategy = config.strategy
        base_delay = config.base_delay
        
        if strategy == RetryStrategy.FIXED_DELAY:
            delay = base_delay
        
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (config.multiplier ** (attempt - 1))
        
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * attempt
        
        elif strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = base_delay * self._fibonacci(attempt)
        
        elif strategy == RetryStrategy.RANDOM_JITTER:
            min_delay = base_delay * config.jitter_range[0]
            max_delay = base_delay * config.jitter_range[1]
            delay = random.uniform(min_delay, max_delay)
        
        elif strategy == RetryStrategy.CUSTOM_INTERVALS:
            if config.custom_intervals and attempt <= len(config.custom_intervals):
                delay = config.custom_intervals[attempt - 1]
            else:
                delay = base_delay
        
        else:
            delay = base_delay
        
        # Apply max delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter if enabled (except for RANDOM_JITTER which already has it)
        if config.jitter and strategy != RetryStrategy.RANDOM_JITTER:
            jitter_factor = random.uniform(config.jitter_range[0], config.jitter_range[1])
            delay *= jitter_factor
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth fibonacci number (for fibonacci backoff)"""
        if n <= 1:
            return 1
        if n == 2:
            return 1
        
        a, b = 1, 1
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b
    
    def _adapt_retry_config(self):
        """
        Adapt retry configuration based on recent success rates
        """
        if len(self.recent_requests) < self.retry_config.adaptation_window:
            return  # Not enough data
        
        # Calculate success rate from recent requests
        recent_window = self.recent_requests[-self.retry_config.adaptation_window:]
        success_rate = sum(1 for req in recent_window if req['success']) / len(recent_window)
        
        if success_rate < self.retry_config.success_threshold:
            # Success rate is low - increase retry attempts and delays
            new_max_attempts = min(self.current_retry_config.max_attempts + 1, 10)
            new_base_delay = min(self.current_retry_config.base_delay * 1.2, 10.0)
            
            if (new_max_attempts != self.current_retry_config.max_attempts or
                new_base_delay != self.current_retry_config.base_delay):
                
                print(f"📈 Adapting retry config: max_attempts: {self.current_retry_config.max_attempts} → {new_max_attempts}, "
                      f"base_delay: {self.current_retry_config.base_delay:.2f} → {new_base_delay:.2f}")
                
                # Create new config with adapted values
                import copy
                self.current_retry_config = copy.deepcopy(self.retry_config)
                self.current_retry_config.max_attempts = new_max_attempts
                self.current_retry_config.base_delay = new_base_delay
                self.retry_metrics.adaptive_adjustments += 1
        
        elif success_rate > 0.95:
            # Very high success rate - reduce retry aggressiveness
            new_max_attempts = max(self.current_retry_config.max_attempts - 1, 1)
            new_base_delay = max(self.current_retry_config.base_delay * 0.9, 0.1)
            
            if (new_max_attempts != self.current_retry_config.max_attempts or
                new_base_delay != self.current_retry_config.base_delay):
                
                print(f"📉 Reducing retry aggressiveness: max_attempts: {self.current_retry_config.max_attempts} → {new_max_attempts}, "
                      f"base_delay: {self.current_retry_config.base_delay:.2f} → {new_base_delay:.2f}")
                
                import copy
                self.current_retry_config = copy.deepcopy(self.retry_config)
                self.current_retry_config.max_attempts = new_max_attempts
                self.current_retry_config.base_delay = new_base_delay
                self.retry_metrics.adaptive_adjustments += 1
    
    def _handle_success(self, attempt_count: int, execution_time: float, total_delay: float):
        """Handle successful execution"""
        # Update retry metrics
        if self.enable_metrics:
            self.retry_metrics.total_attempts += attempt_count
            self.retry_metrics.successful_attempts += 1
            
            if attempt_count > 1:
                self.retry_metrics.total_retries += (attempt_count - 1)
            
            # Update averages
            total_requests = self.retry_metrics.successful_attempts + self.retry_metrics.failed_attempts
            if total_requests > 0:
                self.retry_metrics.avg_attempts_per_request = (
                    self.retry_metrics.total_attempts / total_requests
                )
                
                if self.retry_metrics.total_retries > 0:
                    self.retry_metrics.retry_success_rate = (
                        self.retry_metrics.successful_attempts / 
                        (self.retry_metrics.successful_attempts + self.retry_metrics.failed_attempts) * 100
                    )
        
        # Track for adaptive retry
        if self.retry_config.enable_adaptive_retry:
            self.recent_requests.append({
                'timestamp': time.time(),
                'success': True,
                'attempts': attempt_count,
                'total_delay': total_delay
            })
            
            # Keep only recent requests
            if len(self.recent_requests) > self.retry_config.adaptation_window * 2:
                self.recent_requests = self.recent_requests[-self.retry_config.adaptation_window:]
        
        # Circuit breaker state management
        if self.circuit_state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= 3:  # Need multiple successes to close
                self.circuit_state = "CLOSED"
                self.failure_count = 0
                print(f"✅ Circuit '{self.name}' CLOSED - Service recovered")
        elif self.circuit_state == "CLOSED":
            self.failure_count = 0  # Reset on success
    
    def _handle_failure(self, exception: Exception, attempt_count: int, execution_time: float, total_delay: float):
        """Handle failed execution"""
        # Update retry metrics
        if self.enable_metrics:
            self.retry_metrics.total_attempts += attempt_count
            self.retry_metrics.failed_attempts += 1
            
            if attempt_count > 1:
                self.retry_metrics.total_retries += (attempt_count - 1)
            
            # Update averages
            total_requests = self.retry_metrics.successful_attempts + self.retry_metrics.failed_attempts
            if total_requests > 0:
                self.retry_metrics.avg_attempts_per_request = (
                    self.retry_metrics.total_attempts / total_requests
                )
        
        # Track for adaptive retry
        if self.retry_config.enable_adaptive_retry:
            self.recent_requests.append({
                'timestamp': time.time(),
                'success': False,
                'attempts': attempt_count,
                'total_delay': total_delay,
                'error': str(exception)
            })
        
        # Circuit breaker failure handling
        if self.retry_config.count_retries_as_failures:
            # Count each retry as a failure
            self.failure_count += attempt_count
        else:
            # Count only the final failure
            self.failure_count += 1
        
        self.last_failure_time = time.time()
        
        # Check if circuit should be opened
        if self.circuit_state in ["CLOSED", "HALF_OPEN"] and self.failure_count >= self.circuit_failure_threshold:
            self.circuit_state = "OPEN"
            print(f"🔴 Circuit '{self.name}' OPENED after {self.failure_count} failures")
        elif self.circuit_state == "HALF_OPEN":
            self.circuit_state = "OPEN"
            self.success_count = 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        total_requests = self.retry_metrics.successful_attempts + self.retry_metrics.failed_attempts
        success_rate = (self.retry_metrics.successful_attempts / max(total_requests, 1)) * 100
        
        return {
            "name": self.name,
            "circuit_state": self.circuit_state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "retry_metrics": {
                "total_requests": total_requests,
                "successful_requests": self.retry_metrics.successful_attempts,
                "failed_requests": self.retry_metrics.failed_attempts,
                "success_rate": round(success_rate, 2),
                "total_attempts": self.retry_metrics.total_attempts,
                "total_retries": self.retry_metrics.total_retries,
                "avg_attempts_per_request": round(self.retry_metrics.avg_attempts_per_request, 2),
                "retry_success_rate": round(self.retry_metrics.retry_success_rate, 2),
                "adaptive_adjustments": self.retry_metrics.adaptive_adjustments
            },
            "current_config": {
                "strategy": self.current_retry_config.strategy.value,
                "max_attempts": self.current_retry_config.max_attempts,
                "base_delay": self.current_retry_config.base_delay,
                "max_delay": self.current_retry_config.max_delay,
                "multiplier": self.current_retry_config.multiplier
            },
            "adaptive_retry": {
                "enabled": self.retry_config.enable_adaptive_retry,
                "recent_requests_count": len(self.recent_requests),
                "adaptation_window": self.retry_config.adaptation_window
            }
        }
    
    def reset_adaptive_config(self):
        """Reset adaptive configuration to original"""
        self.current_retry_config = self.retry_config
        self.recent_requests.clear()
        print(f"🔄 Adaptive retry config reset for '{self.name}'")


class CircuitBreakerOpenError(Exception):
    """Circuit breaker is open"""
    pass


# Example services for testing different retry scenarios
def flaky_payment_service(payment_id: str, amount: float, failure_rate: float = 0.4) -> Dict[str, Any]:
    """Simulate a flaky payment service"""
    print(f"💳 Processing payment: {payment_id} (${amount})")
    
    # Simulate processing time
    time.sleep(random.uniform(0.5, 2.0))
    
    # Simulate different types of failures
    if random.random() < failure_rate:
        failure_types = [
            "Network timeout occurred",
            "Service temporarily unavailable", 
            "Connection refused by server",
            "Payment gateway overloaded",
            "Temporary database connection error"
        ]
        raise Exception(random.choice(failure_types))
    
    return {
        "payment_id": payment_id,
        "amount": amount,
        "status": "completed",
        "transaction_id": f"TXN_{int(time.time())}",
        "timestamp": datetime.now().isoformat()
    }


def unreliable_data_service(query: str, failure_rate: float = 0.5) -> Dict[str, Any]:
    """Simulate unreliable data service"""
    print(f"📊 Executing query: {query}")
    
    time.sleep(random.uniform(1.0, 3.0))
    
    if random.random() < failure_rate:
        # Simulate different error patterns
        errors = [
            "Database connection timeout",
            "Query execution timeout", 
            "Connection pool exhausted",
            "Network error occurred",
            "Service rate limit exceeded"
        ]
        raise Exception(random.choice(errors))
    
    return {
        "query": query,
        "results": f"Data for {query}",
        "rows": random.randint(10, 1000),
        "execution_time": random.uniform(0.1, 2.0)
    }


def test_retry_circuit_breaker():
    """Comprehensive test of retry mechanisms with circuit breaker"""
    print("🧪 Testing Retry Circuit Breaker")
    print("=" * 70)
    
    print("\n📊 Test 1: Exponential Backoff Retry")
    print("-" * 50)
    
    # Test exponential backoff
    retry_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=4,
        base_delay=0.5,
        max_delay=8.0,
        multiplier=2.0,
        jitter=True,
        retry_condition=RetryCondition.TRANSIENT_FAILURES
    )
    
    rcb = RetryCircuitBreaker("payment-service", retry_config, circuit_failure_threshold=3)
    
    # Test with moderate failure rate
    for i in range(8):
        try:
            result = rcb.call(flaky_payment_service, f"PAY_{i+1}", 100.0, 0.6)
            print(f"✅ Payment {i+1}: Success")
        except Exception as e:
            print(f"❌ Payment {i+1}: Failed - {str(e)[:40]}")
        
        time.sleep(1)
    
    print(f"\n📈 Exponential Backoff Metrics:")
    metrics = rcb.get_metrics()
    retry_metrics = metrics['retry_metrics']
    for key, value in retry_metrics.items():
        print(f"   {key}: {value}")
    
    print("\n📊 Test 2: Fixed Delay with Custom Conditions")
    print("-" * 50)
    
    # Custom retry condition
    def custom_retry_condition(exception: Exception) -> bool:
        error_str = str(exception).lower()
        return "timeout" in error_str or "connection" in error_str or "network" in error_str
    
    retry_config2 = RetryConfig(
        strategy=RetryStrategy.FIXED_DELAY,
        max_attempts=3,
        base_delay=1.0,
        retry_condition=RetryCondition.CUSTOM_CONDITION,
        custom_condition_func=custom_retry_condition
    )
    
    rcb2 = RetryCircuitBreaker("data-service", retry_config2, circuit_failure_threshold=4)
    
    for i in range(6):
        try:
            result = rcb2.call(unreliable_data_service, f"SELECT * FROM table_{i+1}", 0.5)
            print(f"✅ Query {i+1}: Success")
        except Exception as e:
            print(f"❌ Query {i+1}: Failed - {str(e)[:40]}")
        
        time.sleep(0.5)
    
    print("\n📊 Test 3: Adaptive Retry")
    print("-" * 50)
    
    # Adaptive retry configuration
    adaptive_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=2,
        base_delay=0.3,
        max_delay=5.0,
        enable_adaptive_retry=True,
        adaptation_window=10,
        success_threshold=0.7
    )
    
    adaptive_rcb = RetryCircuitBreaker("adaptive-service", adaptive_config, circuit_failure_threshold=5)
    
    # First phase - high failure rate to trigger adaptation
    print("Phase 1: High failure rate (should trigger adaptation)")
    for i in range(12):
        try:
            result = adaptive_rcb.call(flaky_payment_service, f"ADAPTIVE_{i+1}", 50.0, 0.8)
            print(f"✅ Adaptive {i+1}: Success")
        except Exception as e:
            print(f"❌ Adaptive {i+1}: Failed - {str(e)[:30]}")
        
        time.sleep(0.3)
    
    # Second phase - lower failure rate
    print("\nPhase 2: Lower failure rate (should optimize)")
    for i in range(15):
        try:
            result = adaptive_rcb.call(flaky_payment_service, f"ADAPTIVE2_{i+1}", 50.0, 0.2)
            print(f"✅ Adaptive2 {i+1}: Success")
        except Exception as e:
            print(f"❌ Adaptive2 {i+1}: Failed - {str(e)[:30]}")
        
        time.sleep(0.2)
    
    print("\n📊 Test 4: Custom Intervals Retry")
    print("-" * 50)
    
    custom_config = RetryConfig(
        strategy=RetryStrategy.CUSTOM_INTERVALS,
        max_attempts=4,
        custom_intervals=[0.5, 2.0, 5.0],  # Custom delay sequence
        retry_condition=RetryCondition.ALL_EXCEPTIONS
    )
    
    custom_rcb = RetryCircuitBreaker("custom-service", custom_config)
    
    for i in range(3):
        try:
            result = custom_rcb.call(unreliable_data_service, f"CUSTOM_QUERY_{i+1}", 0.7)
            print(f"✅ Custom {i+1}: Success")
        except Exception as e:
            print(f"❌ Custom {i+1}: Failed - {str(e)[:40]}")
        
        time.sleep(1)
    
    print("\n📊 Test 5: Fibonacci Backoff")
    print("-" * 50)
    
    fib_config = RetryConfig(
        strategy=RetryStrategy.FIBONACCI_BACKOFF,
        max_attempts=5,
        base_delay=0.2,
        max_delay=10.0
    )
    
    fib_rcb = RetryCircuitBreaker("fibonacci-service", fib_config)
    
    try:
        result = fib_rcb.call(unreliable_data_service, "FIBONACCI_QUERY", 0.9)  # High failure rate
        print("✅ Fibonacci test: Success")
    except Exception as e:
        print(f"❌ Fibonacci test: Failed - {str(e)[:40]}")
    
    print("\n📈 Final Metrics Summary:")
    print("=" * 50)
    
    services = [
        ("Payment Service (Exponential)", rcb),
        ("Data Service (Fixed)", rcb2),
        ("Adaptive Service", adaptive_rcb),
        ("Custom Service", custom_rcb),
        ("Fibonacci Service", fib_rcb)
    ]
    
    for service_name, service in services:
        print(f"\n{service_name}:")
        metrics = service.get_metrics()
        print(f"  Circuit State: {metrics['circuit_state']}")
        print(f"  Success Rate: {metrics['retry_metrics']['success_rate']:.1f}%")
        print(f"  Avg Attempts per Request: {metrics['retry_metrics']['avg_attempts_per_request']:.1f}")
        print(f"  Total Retries: {metrics['retry_metrics']['total_retries']}")
        if metrics['retry_metrics']['adaptive_adjustments'] > 0:
            print(f"  Adaptive Adjustments: {metrics['retry_metrics']['adaptive_adjustments']}")


async def test_async_retry():
    """Test async retry functionality"""
    print("\n🧪 Testing Async Retry")
    print("=" * 50)
    
    async def async_flaky_service(service_name: str, delay: float = 1.0, failure_rate: float = 0.5):
        print(f"⚡ Async call to {service_name}")
        await asyncio.sleep(delay)
        
        if random.random() < failure_rate:
            raise Exception(f"Async service {service_name} failed")
        
        return f"Async response from {service_name}"
    
    async_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=3,
        base_delay=0.5,
        multiplier=2.0
    )
    
    async_rcb = RetryCircuitBreaker("async-service", async_config)
    
    for i in range(5):
        try:
            result = await async_rcb.call_async(async_flaky_service, f"AsyncService_{i+1}", 0.5, 0.6)
            print(f"✅ Async {i+1}: {result}")
        except Exception as e:
            print(f"❌ Async {i+1}: Failed - {str(e)[:40]}")
        
        await asyncio.sleep(0.3)
    
    print(f"\n📈 Async Service Metrics:")
    async_metrics = async_rcb.get_metrics()
    for key, value in async_metrics['retry_metrics'].items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    # Test synchronous retry mechanisms
    test_retry_circuit_breaker()
    
    # Test async retry mechanisms
    asyncio.run(test_async_retry())