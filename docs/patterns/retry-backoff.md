# Retry & Backoff Strategies

**If at first you don't succeed, wait and try again (smartly)**

## THE PROBLEM

```
Transient failures are common:
- Network blip → Request fails
- Service restarting → 503 error
- Rate limit hit → 429 error
- Database deadlock → Retry needed

But blind retries make things worse!
```

## THE SOLUTION

```
Smart retry strategies:

Attempt 1: Failed → Wait 100ms
Attempt 2: Failed → Wait 200ms
Attempt 3: Failed → Wait 400ms
Attempt 4: Failed → Wait 800ms + jitter
Attempt 5: Failed → Give up

Don't hammer a struggling service!
```

## Backoff Strategies

```
1. FIXED: Always wait same time
2. LINEAR: 1s, 2s, 3s, 4s...
3. EXPONENTIAL: 1s, 2s, 4s, 8s...
4. EXPONENTIAL + JITTER: Randomized to prevent thundering herd
5. DECORRELATED JITTER: Even better distribution
```

## IMPLEMENTATION

```python
import asyncio
import random
import time
from typing import TypeVar, Callable, Optional, Union, List
from functools import wraps

T = TypeVar('T')

class RetryStrategy:
    """Base retry strategy"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.max_delay = max_delay
        self.exceptions = exceptions
        
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if we should retry"""
        return (
            attempt < self.max_attempts and
            isinstance(exception, self.exceptions)
        )
        
    def get_delay(self, attempt: int) -> float:
        """Get delay before next attempt"""
        raise NotImplementedError

class FixedBackoff(RetryStrategy):
    """Fixed delay between retries"""
    
    def __init__(self, delay: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.delay = delay
        
    def get_delay(self, attempt: int) -> float:
        return self.delay

class LinearBackoff(RetryStrategy):
    """Linear increase in delay"""
    
    def __init__(self, initial_delay: float = 1.0, increment: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.initial_delay = initial_delay
        self.increment = increment
        
    def get_delay(self, attempt: int) -> float:
        delay = self.initial_delay + (attempt - 1) * self.increment
        return min(delay, self.max_delay)

class ExponentialBackoff(RetryStrategy):
    """Exponential increase in delay"""
    
    def __init__(self, base: float = 2.0, initial_delay: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.base = base
        self.initial_delay = initial_delay
        
    def get_delay(self, attempt: int) -> float:
        delay = self.initial_delay * (self.base ** (attempt - 1))
        return min(delay, self.max_delay)

class ExponentialBackoffWithJitter(ExponentialBackoff):
    """Exponential backoff with random jitter"""
    
    def __init__(self, jitter_type: str = 'full', **kwargs):
        super().__init__(**kwargs)
        self.jitter_type = jitter_type
        
    def get_delay(self, attempt: int) -> float:
        base_delay = super().get_delay(attempt)
        
        if self.jitter_type == 'full':
            # Full jitter: random between 0 and base_delay
            return random.uniform(0, base_delay)
            
        elif self.jitter_type == 'equal':
            # Equal jitter: base_delay/2 + random(0, base_delay/2)
            return base_delay / 2 + random.uniform(0, base_delay / 2)
            
        elif self.jitter_type == 'decorrelated':
            # Decorrelated jitter: even better distribution
            if not hasattr(self, '_last_delay'):
                self._last_delay = self.initial_delay
                
            self._last_delay = min(
                self.max_delay,
                random.uniform(self.initial_delay, self._last_delay * 3)
            )
            return self._last_delay
            
        return base_delay

# Retry decorator
def retry(strategy: RetryStrategy):
    """Decorator for retrying functions"""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, strategy.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except strategy.exceptions as e:
                    last_exception = e
                    
                    if not strategy.should_retry(attempt, e):
                        raise
                        
                    if attempt < strategy.max_attempts:
                        delay = strategy.get_delay(attempt)
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                        
            raise last_exception
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, strategy.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except strategy.exceptions as e:
                    last_exception = e
                    
                    if not strategy.should_retry(attempt, e):
                        raise
                        
                    if attempt < strategy.max_attempts:
                        delay = strategy.get_delay(attempt)
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        
            raise last_exception
            
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

# Advanced retry with circuit breaker integration
class SmartRetry:
    def __init__(
        self,
        strategy: RetryStrategy,
        circuit_breaker: Optional['CircuitBreaker'] = None,
        on_retry: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        self.strategy = strategy
        self.circuit_breaker = circuit_breaker
        self.on_retry = on_retry
        self.on_failure = on_failure
        
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute with smart retry logic"""
        
        last_exception = None
        start_time = time.time()
        
        for attempt in range(1, self.strategy.max_attempts + 1):
            try:
                # Check circuit breaker first
                if self.circuit_breaker and self.circuit_breaker.is_open:
                    raise CircuitOpenError("Circuit breaker is open")
                    
                # Execute function
                result = await func(*args, **kwargs)
                
                # Success - notify circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                    
                return result
                
            except Exception as e:
                last_exception = e
                elapsed = time.time() - start_time
                
                # Record failure
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()
                    
                # Check if we should retry
                if not self.strategy.should_retry(attempt, e):
                    if self.on_failure:
                        await self.on_failure(e, attempt, elapsed)
                    raise
                    
                if attempt < self.strategy.max_attempts:
                    delay = self.strategy.get_delay(attempt)
                    
                    if self.on_retry:
                        await self.on_retry(e, attempt, delay)
                        
                    await asyncio.sleep(delay)
                    
        # All retries exhausted
        if self.on_failure:
            await self.on_failure(last_exception, self.strategy.max_attempts, 
                                time.time() - start_time)
        raise last_exception

# Retry with different strategies for different errors
class AdaptiveRetry:
    def __init__(self):
        self.strategies = {}
        
    def add_strategy(self, exception_type: type, strategy: RetryStrategy):
        """Add strategy for specific exception type"""
        self.strategies[exception_type] = strategy
        
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute with adaptive retry"""
        
        attempt = 0
        last_exception = None
        
        while True:
            attempt += 1
            
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Find matching strategy
                strategy = None
                for exc_type, strat in self.strategies.items():
                    if isinstance(e, exc_type):
                        strategy = strat
                        break
                        
                if not strategy:
                    raise  # No strategy for this exception
                    
                if not strategy.should_retry(attempt, e):
                    raise
                    
                delay = strategy.get_delay(attempt)
                await asyncio.sleep(delay)

# Retry budget to prevent retry storms
class RetryBudget:
    def __init__(self, tokens_per_second: float = 10, max_tokens: float = 100):
        self.tokens_per_second = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
    async def acquire(self) -> bool:
        """Try to acquire retry token"""
        async with self.lock:
            # Replenish tokens
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + elapsed * self.tokens_per_second
            )
            self.last_update = now
            
            # Try to acquire token
            if self.tokens >= 1:
                self.tokens -= 1
                return True
                
            return False

class BudgetedRetry(RetryStrategy):
    def __init__(self, strategy: RetryStrategy, budget: RetryBudget):
        self.strategy = strategy
        self.budget = budget
        
    async def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Check if retry is allowed by budget"""
        
        if not self.strategy.should_retry(attempt, exception):
            return False
            
        # Check budget
        has_token = await self.budget.acquire()
        if not has_token:
            print("Retry budget exhausted, failing fast")
            return False
            
        return True
```

## Practical Examples

```python
# Example 1: HTTP client with retry
@retry(ExponentialBackoffWithJitter(max_attempts=5, jitter_type='full'))
async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

# Example 2: Database operation with specific retries
db_retry = AdaptiveRetry()
db_retry.add_strategy(
    psycopg2.OperationalError,
    ExponentialBackoff(max_attempts=5, initial_delay=0.1)
)
db_retry.add_strategy(
    psycopg2.IntegrityError,
    FixedBackoff(max_attempts=3, delay=0.5)
)

async def update_user(user_id: int, data: dict):
    async def _update():
        async with get_db_connection() as conn:
            await conn.execute(
                "UPDATE users SET data = $1 WHERE id = $2",
                data, user_id
            )
    
    await db_retry.execute(_update)

# Example 3: Retry with telemetry
class TelemetryRetry(SmartRetry):
    def __init__(self, *args, metrics_client, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = metrics_client
        
    async def on_retry(self, error, attempt, delay):
        self.metrics.increment('retry.attempt', tags={
            'error_type': type(error).__name__,
            'attempt': attempt
        })
        
    async def on_failure(self, error, attempts, duration):
        self.metrics.increment('retry.exhausted', tags={
            'error_type': type(error).__name__,
            'total_attempts': attempts,
            'duration_ms': int(duration * 1000)
        })
```

## ✓ CHOOSE THIS WHEN:
• Handling transient failures
• Network operations
• Rate limit handling
• External service calls
• Database deadlocks

## ⚠️ BEWARE OF:
• Retry storms/amplification
• Not retrying idempotent operations
• Too aggressive retry timing
• Missing retry budgets
• Retrying non-transient errors

## REAL EXAMPLES
• **AWS SDK**: Built-in exponential backoff
• **Google Cloud**: Adaptive retry strategies
• **Stripe API**: Smart retry with backoff