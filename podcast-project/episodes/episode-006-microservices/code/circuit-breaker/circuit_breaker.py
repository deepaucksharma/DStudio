#!/usr/bin/env python3
"""
Circuit Breaker Library - Production Ready Implementation

जैसे Mumbai local train में power failure के दौरान automatic circuit breakers
सभी trains को protect करते हैं, वैसे ही microservices में circuit breaker
failing services से system को protect करता है

Example Usage:
- IRCTC server down होने पर circuit breaker ticket booking को block कर देता है
- Zomato restaurant service down होने पर order placement को रोक देता है
- Paytm payment gateway down होने पर alternative payment methods को trigger करता है
"""

import asyncio
import time
import threading
import json
import logging
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import statistics
import redis
from datetime import datetime, timedelta

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CircuitBreaker")

class CircuitBreakerState(Enum):
    """
    Circuit breaker states - जैसे Mumbai local train signals
    GREEN = CLOSED (normal operation)
    YELLOW = HALF_OPEN (testing if service recovered) 
    RED = OPEN (service blocked)
    """
    CLOSED = "CLOSED"      # Green signal - service working
    OPEN = "OPEN"          # Red signal - service blocked
    HALF_OPEN = "HALF_OPEN"  # Yellow signal - testing recovery

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration - जैसे Mumbai power grid settings"""
    failure_threshold: int = 5          # Number of failures to open circuit
    recovery_timeout: int = 60          # Seconds to wait before trying recovery
    success_threshold: int = 3          # Successful calls needed to close circuit
    timeout: float = 30.0               # Request timeout in seconds
    expected_exception: tuple = (Exception,)  # Exceptions to count as failures
    fallback_function: Optional[Callable] = None  # Fallback when circuit is open
    
    # Advanced settings
    sliding_window_size: int = 100      # Size of sliding window for failure rate
    minimum_throughput: int = 10        # Minimum requests before calculating failure rate
    failure_rate_threshold: float = 0.5  # 50% failure rate to open circuit
    slow_call_threshold: float = 10.0   # Calls slower than this are considered slow
    slow_call_rate_threshold: float = 0.8  # 80% slow calls to open circuit
    
    # Monitoring
    enable_metrics: bool = True
    metric_window_duration: int = 300   # 5 minutes metric window

@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics - जैसे Mumbai local train performance dashboard"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    slow_requests: int = 0
    circuit_open_count: int = 0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_transition_count: int = 0

class CircuitBreakerException(Exception):
    """Circuit breaker specific exceptions"""
    def __init__(self, message: str, state: CircuitBreakerState, metrics: CircuitBreakerMetrics = None):
        super().__init__(message)
        self.state = state
        self.metrics = metrics

class CircuitBreakerOpenException(CircuitBreakerException):
    """Exception when circuit is open - जैसे train service suspended"""
    pass

class CircuitBreakerTimeoutException(CircuitBreakerException):
    """Exception when request times out - जैसे train delay announcement"""
    pass

class SlidingWindow:
    """Sliding window for tracking recent calls - जैसे Mumbai traffic monitoring"""
    
    def __init__(self, size: int):
        self.size = size
        self.calls = []
        self.lock = threading.RLock()
    
    def add_call(self, success: bool, duration: float, timestamp: float = None):
        """Add a call result to sliding window"""
        if timestamp is None:
            timestamp = time.time()
            
        call_data = {
            'success': success,
            'duration': duration,
            'timestamp': timestamp
        }
        
        with self.lock:
            self.calls.append(call_data)
            if len(self.calls) > self.size:
                self.calls.pop(0)  # Remove oldest call
    
    def get_failure_rate(self, min_calls: int = 1) -> float:
        """Calculate current failure rate"""
        with self.lock:
            if len(self.calls) < min_calls:
                return 0.0
            
            failed_calls = sum(1 for call in self.calls if not call['success'])
            return failed_calls / len(self.calls)
    
    def get_slow_call_rate(self, threshold: float) -> float:
        """Calculate rate of slow calls"""
        with self.lock:
            if not self.calls:
                return 0.0
            
            slow_calls = sum(1 for call in self.calls if call['duration'] > threshold)
            return slow_calls / len(self.calls)
    
    def get_average_duration(self) -> float:
        """Calculate average call duration"""
        with self.lock:
            if not self.calls:
                return 0.0
            
            durations = [call['duration'] for call in self.calls]
            return statistics.mean(durations)
    
    def clear(self):
        """Clear all call data"""
        with self.lock:
            self.calls.clear()

class CircuitBreaker:
    """
    Production-ready Circuit Breaker implementation
    जैसे Mumbai local train system में power protection
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None, redis_client: redis.Redis = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.redis_client = redis_client
        
        # State management
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
        self.last_success_time = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        
        # Sliding window for advanced failure detection
        self.sliding_window = SlidingWindow(self.config.sliding_window_size)
        
        # Metrics
        self.metrics = CircuitBreakerMetrics()
        self.lock = threading.RLock()
        
        # State persistence in Redis
        if self.redis_client:
            self._load_state_from_redis()
        
        logger.info(f"Circuit breaker '{name}' initialized - Ready to protect like Mumbai power grid!")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage - @circuit_breaker_instance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.async_call(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        जैसे Mumbai local train में safety check के साथ journey
        """
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if not self._should_attempt_reset():
                self._record_request(success=False, duration=0, blocked=True)
                if self.config.fallback_function:
                    logger.info(f"Circuit breaker '{self.name}' is OPEN, executing fallback")
                    return self.config.fallback_function(*args, **kwargs)
                
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN - Service blocked like train during power failure",
                    CircuitBreakerState.OPEN,
                    self.metrics
                )
            else:
                # Transition to HALF_OPEN for testing
                self._set_state(CircuitBreakerState.HALF_OPEN)
                logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN - Testing service recovery")
        
        # Execute the function with timeout and monitoring
        start_time = time.time()
        try:
            # Set timeout if configured
            if hasattr(func, '__timeout__'):
                result = func(*args, **kwargs)
            else:
                result = self._execute_with_timeout(func, self.config.timeout, *args, **kwargs)
            
            # Record successful call
            duration = time.time() - start_time
            self._record_request(success=True, duration=duration)
            
            # Handle state transitions on success
            self._handle_success()
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Check if this exception should count as failure
            if isinstance(e, self.config.expected_exception):
                self._record_request(success=False, duration=duration)
                self._handle_failure()
                logger.warning(f"Circuit breaker '{self.name}' recorded failure: {str(e)}")
            
            # Re-raise the exception
            raise e
    
    async def async_call(self, func: Callable, *args, **kwargs) -> Any:
        """Async version of call method - जैसे Mumbai Metro की async operations"""
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if not self._should_attempt_reset():
                self._record_request(success=False, duration=0, blocked=True)
                if self.config.fallback_function:
                    logger.info(f"Circuit breaker '{self.name}' is OPEN, executing async fallback")
                    if asyncio.iscoroutinefunction(self.config.fallback_function):
                        return await self.config.fallback_function(*args, **kwargs)
                    else:
                        return self.config.fallback_function(*args, **kwargs)
                
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN - Async service blocked",
                    CircuitBreakerState.OPEN,
                    self.metrics
                )
            else:
                self._set_state(CircuitBreakerState.HALF_OPEN)
        
        start_time = time.time()
        try:
            # Execute with async timeout
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
            
            duration = time.time() - start_time
            self._record_request(success=True, duration=duration)
            self._handle_success()
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self._record_request(success=False, duration=duration, timeout=True)
            self._handle_failure()
            raise CircuitBreakerTimeoutException(
                f"Circuit breaker '{self.name}' timeout after {self.config.timeout}s",
                self.state,
                self.metrics
            )
        except Exception as e:
            duration = time.time() - start_time
            if isinstance(e, self.config.expected_exception):
                self._record_request(success=False, duration=duration)
                self._handle_failure()
            raise e
    
    def _execute_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        """Execute function with timeout - Mumbai style efficient timing"""
        import signal
        
        def timeout_handler(signum, frame):
            raise CircuitBreakerTimeoutException(
                f"Circuit breaker '{self.name}' timeout after {timeout}s - Like Mumbai local delay",
                self.state,
                self.metrics
            )
        
        # Set timeout signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        except Exception:
            signal.alarm(0)  # Cancel timeout
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _handle_success(self):
        """Handle successful call - जैसे train on-time arrival"""
        with self.lock:
            self.consecutive_failures = 0
            self.consecutive_successes += 1
            self.last_success_time = time.time()
            
            # Transition from HALF_OPEN to CLOSED if enough successes
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.consecutive_successes >= self.config.success_threshold:
                    self._set_state(CircuitBreakerState.CLOSED)
                    logger.info(f"Circuit breaker '{self.name}' CLOSED - Service recovered like Mumbai after monsoon!")
    
    def _handle_failure(self):
        """Handle failed call - जैसे train cancellation due to technical issues"""
        with self.lock:
            self.consecutive_successes = 0
            self.consecutive_failures += 1
            self.last_failure_time = time.time()
            
            # Check if we should open the circuit
            should_open = False
            
            # Simple threshold-based opening
            if self.consecutive_failures >= self.config.failure_threshold:
                should_open = True
                logger.warning(f"Circuit breaker '{self.name}' opening due to {self.consecutive_failures} consecutive failures")
            
            # Advanced failure rate-based opening
            if self.config.minimum_throughput <= len(self.sliding_window.calls):
                failure_rate = self.sliding_window.get_failure_rate()
                if failure_rate >= self.config.failure_rate_threshold:
                    should_open = True
                    logger.warning(f"Circuit breaker '{self.name}' opening due to {failure_rate:.2%} failure rate")
                
                # Slow call rate check
                slow_rate = self.sliding_window.get_slow_call_rate(self.config.slow_call_threshold)
                if slow_rate >= self.config.slow_call_rate_threshold:
                    should_open = True
                    logger.warning(f"Circuit breaker '{self.name}' opening due to {slow_rate:.2%} slow calls")
            
            # Open circuit if conditions met
            if should_open and self.state != CircuitBreakerState.OPEN:
                self._set_state(CircuitBreakerState.OPEN)
                logger.error(f"Circuit breaker '{self.name}' OPENED - Service blocked like Harbour line during storms!")
    
    def _set_state(self, new_state: CircuitBreakerState):
        """Change circuit breaker state with persistence"""
        old_state = self.state
        self.state = new_state
        self.metrics.state_transition_count += 1
        
        if new_state == CircuitBreakerState.OPEN:
            self.metrics.circuit_open_count += 1
        
        # Persist state in Redis
        if self.redis_client:
            self._save_state_to_redis()
        
        logger.info(f"Circuit breaker '{self.name}' state changed: {old_state.value} → {new_state.value}")
    
    def _record_request(self, success: bool, duration: float, blocked: bool = False, timeout: bool = False):
        """Record request metrics"""
        with self.lock:
            self.metrics.total_requests += 1
            
            if blocked:
                # Request blocked by open circuit
                return
            
            if timeout:
                self.metrics.timeout_requests += 1
                success = False  # Timeouts are failures
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            if duration > self.config.slow_call_threshold:
                self.metrics.slow_requests += 1
            
            # Update average response time (exponential moving average)
            if self.metrics.average_response_time == 0:
                self.metrics.average_response_time = duration
            else:
                self.metrics.average_response_time = (
                    0.9 * self.metrics.average_response_time + 0.1 * duration
                )
            
            # Add to sliding window
            self.sliding_window.add_call(success, duration)
            
            # Update last failure/success times
            if success:
                self.metrics.last_success_time = datetime.now()
            else:
                self.metrics.last_failure_time = datetime.now()
    
    def _load_state_from_redis(self):
        """Load circuit breaker state from Redis"""
        try:
            state_key = f"circuit_breaker:{self.name}:state"
            metrics_key = f"circuit_breaker:{self.name}:metrics"
            
            # Load state
            state_data = self.redis_client.get(state_key)
            if state_data:
                state_info = json.loads(state_data)
                self.state = CircuitBreakerState(state_info.get('state', 'CLOSED'))
                self.consecutive_failures = state_info.get('consecutive_failures', 0)
                self.consecutive_successes = state_info.get('consecutive_successes', 0)
                self.last_failure_time = state_info.get('last_failure_time')
                self.last_success_time = state_info.get('last_success_time')
            
            # Load metrics
            metrics_data = self.redis_client.get(metrics_key)
            if metrics_data:
                metrics_info = json.loads(metrics_data)
                for key, value in metrics_info.items():
                    if hasattr(self.metrics, key):
                        setattr(self.metrics, key, value)
            
            logger.info(f"Loaded circuit breaker '{self.name}' state from Redis: {self.state.value}")
            
        except Exception as e:
            logger.error(f"Failed to load circuit breaker state from Redis: {e}")
    
    def _save_state_to_redis(self):
        """Save circuit breaker state to Redis"""
        try:
            state_key = f"circuit_breaker:{self.name}:state"
            metrics_key = f"circuit_breaker:{self.name}:metrics"
            
            # Save state
            state_data = {
                'state': self.state.value,
                'consecutive_failures': self.consecutive_failures,
                'consecutive_successes': self.consecutive_successes,
                'last_failure_time': self.last_failure_time,
                'last_success_time': self.last_success_time,
                'timestamp': time.time()
            }
            self.redis_client.setex(state_key, 3600, json.dumps(state_data))  # 1 hour TTL
            
            # Save metrics (convert datetime to timestamp for JSON serialization)
            metrics_data = asdict(self.metrics)
            if metrics_data.get('last_failure_time'):
                metrics_data['last_failure_time'] = metrics_data['last_failure_time'].timestamp()
            if metrics_data.get('last_success_time'):
                metrics_data['last_success_time'] = metrics_data['last_success_time'].timestamp()
            
            self.redis_client.setex(metrics_key, 3600, json.dumps(metrics_data))
            
        except Exception as e:
            logger.error(f"Failed to save circuit breaker state to Redis: {e}")
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self.state
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics"""
        return self.metrics
    
    def reset(self):
        """Manually reset circuit breaker - जैसे Mumbai power grid manual reset"""
        with self.lock:
            self._set_state(CircuitBreakerState.CLOSED)
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.sliding_window.clear()
            logger.info(f"Circuit breaker '{self.name}' manually reset - Like Mumbai local service restoration!")
    
    def force_open(self):
        """Manually open circuit breaker for maintenance"""
        with self.lock:
            self._set_state(CircuitBreakerState.OPEN)
            logger.warning(f"Circuit breaker '{self.name}' manually opened for maintenance")
    
    def health_check(self) -> Dict[str, Any]:
        """Get health status - जैसे Mumbai local train status board"""
        with self.lock:
            failure_rate = 0.0
            slow_call_rate = 0.0
            
            if len(self.sliding_window.calls) >= self.config.minimum_throughput:
                failure_rate = self.sliding_window.get_failure_rate()
                slow_call_rate = self.sliding_window.get_slow_call_rate(self.config.slow_call_threshold)
            
            return {
                'name': self.name,
                'state': self.state.value,
                'healthy': self.state != CircuitBreakerState.OPEN,
                'metrics': {
                    'total_requests': self.metrics.total_requests,
                    'success_rate': (
                        self.metrics.successful_requests / max(1, self.metrics.total_requests)
                    ),
                    'failure_rate': failure_rate,
                    'slow_call_rate': slow_call_rate,
                    'average_response_time': self.metrics.average_response_time,
                    'consecutive_failures': self.consecutive_failures,
                    'consecutive_successes': self.consecutive_successes,
                    'circuit_open_count': self.metrics.circuit_open_count
                },
                'last_failure': (
                    self.metrics.last_failure_time.isoformat() 
                    if self.metrics.last_failure_time else None
                ),
                'last_success': (
                    self.metrics.last_success_time.isoformat() 
                    if self.metrics.last_success_time else None
                ),
                'message': self._get_status_message()
            }
    
    def _get_status_message(self) -> str:
        """Get Mumbai-style status message"""
        if self.state == CircuitBreakerState.CLOSED:
            return f"Service running smoothly like Mumbai Dabbawalas - {self.metrics.successful_requests} successful calls"
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return f"Testing service recovery like Mumbai local trial run - {self.consecutive_successes} recent successes"
        else:
            return f"Service blocked like Harbour line during heavy rains - {self.consecutive_failures} consecutive failures"

# Decorator factory for easy usage
def circuit_breaker(name: str, **config_kwargs):
    """
    Decorator factory for circuit breaker
    
    Usage:
    @circuit_breaker("payment_service", failure_threshold=3, recovery_timeout=30)
    def process_payment(amount):
        # Payment processing logic
        pass
    """
    config = CircuitBreakerConfig(**config_kwargs)
    cb = CircuitBreaker(name, config)
    return cb

# Mumbai-specific circuit breakers for common use cases
class MumbaiCircuitBreakers:
    """Pre-configured circuit breakers for Mumbai-scale applications"""
    
    @staticmethod
    def irctc_booking_breaker(redis_client: redis.Redis = None) -> CircuitBreaker:
        """Circuit breaker for IRCTC-style booking systems"""
        config = CircuitBreakerConfig(
            failure_threshold=3,        # IRCTC fails quickly during high load
            recovery_timeout=120,       # 2 minutes recovery time
            timeout=30.0,              # 30 second timeout for bookings
            slow_call_threshold=15.0,   # Bookings slower than 15s are slow
            failure_rate_threshold=0.3  # 30% failure rate opens circuit
        )
        return CircuitBreaker("irctc_booking", config, redis_client)
    
    @staticmethod
    def payment_gateway_breaker(redis_client: redis.Redis = None) -> CircuitBreaker:
        """Circuit breaker for payment gateways like Paytm/PhonePe"""
        config = CircuitBreakerConfig(
            failure_threshold=2,        # Payment failures are critical
            recovery_timeout=60,        # 1 minute recovery
            timeout=45.0,              # 45 seconds for payment processing
            slow_call_threshold=20.0,   # Payments slower than 20s are concerning
            failure_rate_threshold=0.1  # Even 10% payment failures are serious
        )
        return CircuitBreaker("payment_gateway", config, redis_client)
    
    @staticmethod
    def food_delivery_breaker(redis_client: redis.Redis = None) -> CircuitBreaker:
        """Circuit breaker for food delivery services like Zomato/Swiggy"""
        config = CircuitBreakerConfig(
            failure_threshold=5,        # Food delivery can tolerate more failures
            recovery_timeout=90,        # 1.5 minutes recovery
            timeout=20.0,              # 20 seconds for order placement
            slow_call_threshold=10.0,   # Orders slower than 10s are slow
            failure_rate_threshold=0.4  # 40% failure rate for food delivery
        )
        return CircuitBreaker("food_delivery", config, redis_client)
    
    @staticmethod
    def cab_booking_breaker(redis_client: redis.Redis = None) -> CircuitBreaker:
        """Circuit breaker for cab booking services like Ola/Uber"""
        config = CircuitBreakerConfig(
            failure_threshold=4,        # Cab booking moderate tolerance
            recovery_timeout=45,        # Quick recovery for urgent bookings
            timeout=15.0,              # Fast booking expected
            slow_call_threshold=8.0,    # Bookings slower than 8s are slow
            failure_rate_threshold=0.35 # 35% failure rate threshold
        )
        return CircuitBreaker("cab_booking", config, redis_client)