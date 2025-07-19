# Circuit Breaker

**Fail fast, recover gracefully**

## THE PROBLEM

```
When a service is down:
Service A → Service B (timeout 30s)
         → Service B (timeout 30s)
         → Service B (timeout 30s)
         → ... 1000 requests waiting

Result: A is now down too!
```

## THE SOLUTION

```
Circuit breaker stops the bleeding:

CLOSED (normal) → failures → OPEN (fail fast)
                               ↓
                          wait timeout
                               ↓
                          HALF-OPEN (test)
                               ↓
                    success? → CLOSED
                    failure? → OPEN
```

## States Explained

```
1. CLOSED: Normal operation
   - Requests pass through
   - Count failures
   
2. OPEN: Service is down
   - Fail immediately
   - Don't even try
   
3. HALF-OPEN: Testing recovery
   - Allow few requests
   - Check if healthy
```

## IMPLEMENTATION

```python
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from typing import Callable, Optional, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exception: type = Exception,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker"""
        
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitOpenError(
                        f"Circuit breaker is OPEN. Retry after {self._time_until_reset()}s"
                    )
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Record success
            await self._on_success()
            return result
            
        except self.expected_exception as e:
            # Record failure
            await self._on_failure()
            raise
    
    async def _on_success(self):
        """Handle successful call"""
        async with self.lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                
                if self.success_count >= self.success_threshold:
                    # Enough successes, close circuit
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failed in half-open, go back to open
                self.state = CircuitState.OPEN
                
            elif self.failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should try half-open"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )
    
    def _time_until_reset(self) -> float:
        """Time until circuit can attempt reset"""
        if not self.last_failure_time:
            return 0
            
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, self.recovery_timeout - elapsed)
    
    @property
    def current_state(self) -> str:
        """Get current circuit state"""
        return self.state.value
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None
        }

# Advanced circuit breaker with sliding window
class SlidingWindowCircuitBreaker:
    def __init__(
        self,
        failure_threshold_percentage: float = 50,
        minimum_throughput: int = 10,
        window_size: int = 10,
        recovery_timeout: int = 30
    ):
        self.failure_threshold_percentage = failure_threshold_percentage
        self.minimum_throughput = minimum_throughput
        self.window_size = window_size
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.sliding_window = collections.deque(maxlen=window_size)
        self.last_failure_time = None
        
    async def call(self, func: Callable, *args, **kwargs):
        """Execute with sliding window tracking"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")
        
        start_time = time.time()
        success = False
        
        try:
            result = await func(*args, **kwargs)
            success = True
            return result
            
        finally:
            # Record result
            duration = time.time() - start_time
            self.sliding_window.append({
                'success': success,
                'duration': duration,
                'timestamp': time.time()
            })
            
            # Evaluate circuit state
            self._evaluate_state()
    
    def _evaluate_state(self):
        """Evaluate if circuit should change state"""
        
        if len(self.sliding_window) < self.minimum_throughput:
            return  # Not enough data
            
        # Calculate failure percentage
        failures = sum(1 for r in self.sliding_window if not r['success'])
        failure_percentage = (failures / len(self.sliding_window)) * 100
        
        if self.state == CircuitState.CLOSED:
            if failure_percentage >= self.failure_threshold_percentage:
                self.state = CircuitState.OPEN
                self.last_failure_time = datetime.now()
                
        elif self.state == CircuitState.HALF_OPEN:
            if failure_percentage < self.failure_threshold_percentage:
                self.state = CircuitState.CLOSED
            else:
                self.state = CircuitState.OPEN
                self.last_failure_time = datetime.now()

# Circuit breaker with fallback
class CircuitBreakerWithFallback:
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.fallback_functions = {}
        
    def register_fallback(self, func_name: str, fallback: Callable):
        """Register fallback for function"""
        self.fallback_functions[func_name] = fallback
        
    async def call(self, func: Callable, *args, **kwargs):
        """Call with fallback on circuit open"""
        
        try:
            return await self.circuit_breaker.call(func, *args, **kwargs)
            
        except CircuitOpenError:
            # Try fallback if available
            func_name = func.__name__
            if func_name in self.fallback_functions:
                fallback = self.fallback_functions[func_name]
                return await fallback(*args, **kwargs)
            raise

# Distributed circuit breaker
class DistributedCircuitBreaker:
    """Circuit breaker with shared state across instances"""
    
    def __init__(self, redis_client, service_name: str, **kwargs):
        self.redis = redis_client
        self.service_name = service_name
        self.local_breaker = CircuitBreaker(**kwargs)
        self.sync_interval = 1  # seconds
        self._start_sync()
        
    def _start_sync(self):
        """Start background state sync"""
        asyncio.create_task(self._sync_loop())
        
    async def _sync_loop(self):
        """Sync state with Redis"""
        while True:
            try:
                # Get global state
                global_state = await self.redis.hgetall(f"circuit:{self.service_name}")
                
                if global_state:
                    # Update local state if global is more severe
                    if (global_state['state'] == 'open' and 
                        self.local_breaker.state != CircuitState.OPEN):
                        
                        self.local_breaker.state = CircuitState.OPEN
                        self.local_breaker.last_failure_time = datetime.fromisoformat(
                            global_state['last_failure']
                        )
                
                # Push local state if we opened circuit
                if self.local_breaker.state == CircuitState.OPEN:
                    await self.redis.hset(
                        f"circuit:{self.service_name}",
                        mapping={
                            'state': 'open',
                            'last_failure': self.local_breaker.last_failure_time.isoformat(),
                            'instance': socket.gethostname()
                        }
                    )
                    await self.redis.expire(f"circuit:{self.service_name}", 60)
                    
            except Exception:
                # Don't let sync failures break the breaker
                pass
                
            await asyncio.sleep(self.sync_interval)

# HTTP client with circuit breaker
class ResilientHTTPClient:
    def __init__(self):
        self.circuit_breakers = {}
        self.default_timeout = 5
        
    def _get_circuit_breaker(self, host: str) -> CircuitBreaker:
        """Get or create circuit breaker for host"""
        if host not in self.circuit_breakers:
            self.circuit_breakers[host] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30,
                expected_exception=aiohttp.ClientError
            )
        return self.circuit_breakers[host]
    
    async def get(self, url: str, **kwargs):
        """HTTP GET with circuit breaker"""
        
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        circuit_breaker = self._get_circuit_breaker(host)
        
        async def _make_request():
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
        
        return await circuit_breaker.call(_make_request)
```

## Usage Example

```python
# Basic usage
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=RequestException
)

async def call_flaky_service():
    return await circuit_breaker.call(
        flaky_service.make_request,
        param1="value1"
    )

# With fallback
breaker_with_fallback = CircuitBreakerWithFallback(circuit_breaker)

async def fallback_response(*args, **kwargs):
    return {"status": "degraded", "cached_data": "..."}

breaker_with_fallback.register_fallback(
    "make_request", 
    fallback_response
)

# Monitor circuit state
print(f"Circuit state: {circuit_breaker.current_state}")
print(f"Stats: {circuit_breaker.get_stats()}")
```

## ✓ CHOOSE THIS WHEN:
• Calling external services
• Preventing cascade failures
• Need fast failure detection
• Want automatic recovery
• Protecting resources

## ⚠️ BEWARE OF:
• Setting thresholds too low
• Recovery timeout too short
• Not monitoring state changes
• Missing fallback strategies
• Shared state complexity

## REAL EXAMPLES
• **Netflix Hystrix**: Original circuit breaker
• **Resilience4j**: Modern Java library
• **py-breaker**: Python implementation