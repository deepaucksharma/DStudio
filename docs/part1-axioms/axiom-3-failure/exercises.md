# Partial Failure Exercises

!!! info "Prerequisites"
    - [Axiom 3: Partial Failure Core Concepts](index.md)
    - [Failure Examples](examples.md)
    - Basic understanding of distributed systems

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Failure Home](index.md) |
    [→ Next Axiom](../axiom-4-concurrency/index.md)

## Exercise 1: Build a Circuit Breaker

### 🔧 Try This: Implement a Circuit Breaker

```python
import time
import random
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold=5,
                 success_threshold=2,
                 timeout=60,
                 expected_exception=Exception):
        # TODO: Initialize the circuit breaker
        # Track: state, failures, successes, last_failure_time
        pass
    
    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        
        TODO: Implement state machine:
        - CLOSED: Execute normally, count failures
        - OPEN: Fail fast, check timeout
        - HALF_OPEN: Test with limited requests
        """
        pass
    
    def _record_success(self):
        # TODO: Handle successful calls
        pass
    
    def _record_failure(self):
        # TODO: Handle failed calls
        pass
    
    def get_state(self):
        # TODO: Return current state and metrics
        pass

# Test your implementation
def flaky_service(failure_rate=0.3):
    """Simulates a flaky service"""
    if random.random() < failure_rate:
        raise Exception("Service temporarily unavailable")
    return "Success!"

# Exercise: Test the circuit breaker
breaker = CircuitBreaker(failure_threshold=3, timeout=5)

for i in range(20):
    try:
        result = breaker.call(flaky_service, failure_rate=0.5)
        print(f"Call {i}: {result}")
    except Exception as e:
        print(f"Call {i}: Failed - {e}")
    
    time.sleep(0.5)
    
    # Print state after each call
    state = breaker.get_state()
    print(f"  State: {state}")
```

<details>
<summary>Solution</summary>

```python
import time
import random
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold=5,
                 success_threshold=2,
                 timeout=60,
                 expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = Lock()
        
        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_circuit_opens = 0
    
    def call(self, func, *args, **kwargs):
        with self.lock:
            self.total_calls += 1
            
            # Check if we should attempt reset
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self.failure_count = 0
                else:
                    raise Exception(f"Circuit breaker is OPEN (will retry after {self.timeout}s)")
        
        # Execute the function
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception as e:
            self._record_failure()
            raise e
    
    def _should_attempt_reset(self):
        return (
            self.last_failure_time and 
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _record_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    print(f"  Circuit CLOSED after {self.success_count} successes")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0  # Reset on success
    
    def _record_failure(self):
        with self.lock:
            self.total_failures += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.total_circuit_opens += 1
                print(f"  Circuit OPEN (half-open test failed)")
            elif self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.total_circuit_opens += 1
                    print(f"  Circuit OPEN after {self.failure_count} failures")
    
    def get_state(self):
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'total_calls': self.total_calls,
                'total_failures': self.total_failures,
                'failure_rate': self.total_failures / max(1, self.total_calls),
                'circuit_opens': self.total_circuit_opens
            }

# Enhanced test
def flaky_service(failure_rate=0.3):
    if random.random() < failure_rate:
        raise Exception("Service temporarily unavailable")
    time.sleep(0.01)  # Simulate some work
    return "Success!"

# Test with varying failure rates
breaker = CircuitBreaker(failure_threshold=3, success_threshold=2, timeout=5)

print("Testing circuit breaker with varying failure rates...\n")

# Phase 1: Normal operation
print("Phase 1: Normal operation (30% failure rate)")
for i in range(10):
    try:
        result = breaker.call(flaky_service, failure_rate=0.3)
        print(f"Call {i}: Success")
    except Exception as e:
        print(f"Call {i}: Failed - {e}")
    time.sleep(0.2)

print(f"\nState: {breaker.get_state()}\n")

# Phase 2: High failure rate
print("Phase 2: High failure rate (80% failure rate)")
for i in range(10, 20):
    try:
        result = breaker.call(flaky_service, failure_rate=0.8)
        print(f"Call {i}: Success")
    except Exception as e:
        print(f"Call {i}: Failed - {e}")
    time.sleep(0.2)

print(f"\nState: {breaker.get_state()}\n")

# Phase 3: Wait for timeout
print("Phase 3: Waiting for timeout...")
time.sleep(5)

# Phase 4: Recovery
print("\nPhase 4: Recovery (10% failure rate)")
for i in range(20, 30):
    try:
        result = breaker.call(flaky_service, failure_rate=0.1)
        print(f"Call {i}: Success")
    except Exception as e:
        print(f"Call {i}: Failed - {e}")
    time.sleep(0.2)

print(f"\nFinal State: {breaker.get_state()}")
```

</details>

## Exercise 2: Implement Retry with Backoff

### 🔧 Try This: Smart Retry Logic

```python
import time
import random

class RetryPolicy:
    def __init__(self,
                 max_attempts=3,
                 initial_delay=0.1,
                 max_delay=10,
                 exponential_base=2,
                 jitter=True):
        # TODO: Initialize retry policy
        pass
    
    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute function with retry logic
        
        TODO: Implement:
        1. Exponential backoff
        2. Jitter to prevent thundering herd
        3. Max delay cap
        4. Return result or raise last exception
        """
        pass
    
    def calculate_delay(self, attempt):
        """
        Calculate delay for given attempt number
        
        TODO: Implement exponential backoff with jitter
        """
        pass

# Test scenarios
def unreliable_service(success_chance=0.3):
    """Service that fails 70% of the time"""
    if random.random() < success_chance:
        return {"status": "success", "data": "Important data"}
    else:
        raise Exception("Service unavailable")

# Exercise: Compare different retry strategies
policies = {
    "no_retry": RetryPolicy(max_attempts=1),
    "fixed_delay": RetryPolicy(max_attempts=3, exponential_base=1),
    "exponential": RetryPolicy(max_attempts=3, exponential_base=2),
    "exponential_jitter": RetryPolicy(max_attempts=3, exponential_base=2, jitter=True)
}

# Run simulation
for name, policy in policies.items():
    print(f"\nTesting {name}:")
    # TODO: Run 100 trials and measure:
    # - Success rate
    # - Average time to success
    # - Total time spent
```

<details>
<summary>Solution</summary>

```python
import time
import random
import statistics

class RetryPolicy:
    def __init__(self,
                 max_attempts=3,
                 initial_delay=0.1,
                 max_delay=10,
                 exponential_base=2,
                 jitter=True):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        
        # Metrics
        self.total_attempts = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_delay_time = 0
    
    def execute_with_retry(self, func, *args, **kwargs):
        last_exception = None
        start_time = time.time()
        
        for attempt in range(self.max_attempts):
            self.total_attempts += 1
            
            try:
                result = func(*args, **kwargs)
                self.successful_calls += 1
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    self.total_delay_time += delay
                    time.sleep(delay)
        
        self.failed_calls += 1
        raise last_exception
    
    def calculate_delay(self, attempt):
        # Exponential backoff
        delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        # Add jitter
        if self.jitter:
            # Full jitter: delay = random(0, calculated_delay)
            delay = random.uniform(0, delay)
        
        return delay
    
    def get_stats(self):
        total_calls = self.successful_calls + self.failed_calls
        return {
            'success_rate': self.successful_calls / max(1, total_calls),
            'avg_attempts': self.total_attempts / max(1, total_calls),
            'total_delay': self.total_delay_time,
            'avg_delay': self.total_delay_time / max(1, total_calls)
        }

# Enhanced unreliable service
class UnreliableService:
    def __init__(self, success_chance=0.3):
        self.success_chance = success_chance
        self.call_count = 0
    
    def call(self):
        self.call_count += 1
        if random.random() < self.success_chance:
            return {"status": "success", "data": f"Call {self.call_count}"}
        else:
            raise Exception(f"Service unavailable (call {self.call_count})")

# Compare retry strategies
def compare_retry_strategies():
    policies = {
        "no_retry": RetryPolicy(max_attempts=1),
        "fixed_delay": RetryPolicy(max_attempts=3, exponential_base=1, initial_delay=0.5),
        "exponential": RetryPolicy(max_attempts=3, exponential_base=2, initial_delay=0.1),
        "exponential_jitter": RetryPolicy(max_attempts=3, exponential_base=2, initial_delay=0.1, jitter=True),
        "aggressive": RetryPolicy(max_attempts=5, exponential_base=1.5, initial_delay=0.05)
    }
    
    results = {}
    
    for name, policy in policies.items():
        print(f"\nTesting {name}:")
        service = UnreliableService(success_chance=0.3)
        
        trial_times = []
        
        for trial in range(100):
            start = time.time()
            try:
                policy.execute_with_retry(service.call)
                trial_times.append(time.time() - start)
            except:
                trial_times.append(time.time() - start)
        
        stats = policy.get_stats()
        stats['avg_time'] = statistics.mean(trial_times)
        stats['p95_time'] = statistics.quantiles(trial_times, n=20)[18]  # 95th percentile
        
        results[name] = stats
        
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg attempts: {stats['avg_attempts']:.2f}")
        print(f"  Avg time: {stats['avg_time']*1000:.1f}ms")
        print(f"  P95 time: {stats['p95_time']*1000:.1f}ms")
        print(f"  Total delay: {stats['total_delay']:.1f}s")
    
    # Visualize comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"{'Strategy':<20} {'Success':<10} {'Avg Time':<10} {'P95 Time':<10}")
    print("-"*60)
    
    for name, stats in results.items():
        print(f"{name:<20} {stats['success_rate']:<10.1%} "
              f"{stats['avg_time']*1000:<10.1f}ms "
              f"{stats['p95_time']*1000:<10.1f}ms")
    
    print("\nInsights:")
    print("- No retry: Fast but low success rate")
    print("- Fixed delay: Better success but predictable load spikes")
    print("- Exponential: Good balance of success and time")
    print("- Jitter: Prevents thundering herd, best for scale")
    print("- Aggressive: Highest success but longest delays")

compare_retry_strategies()
```

</details>

## Exercise 3: Timeout Coordination

### 🔧 Try This: Design Hierarchical Timeouts

```python
import asyncio
import time
from typing import Optional

class TimeoutCoordinator:
    def __init__(self, total_budget: float):
        self.total_budget = total_budget
        self.start_time = time.time()
        
    def get_remaining_budget(self) -> float:
        elapsed = time.time() - self.start_time
        return max(0, self.total_budget - elapsed)
    
    def child_timeout(self, operation_fraction: float = 0.8) -> float:
        """
        Calculate timeout for child operation
        
        TODO: Implement logic that:
        1. Never exceeds remaining budget
        2. Leaves room for retries
        3. Accounts for network overhead
        """
        pass

# Simulated service calls
async def database_query(timeout: float):
    try:
        await asyncio.wait_for(
            asyncio.sleep(0.5),  # Simulate query
            timeout=timeout
        )
        return {"status": "success"}
    except asyncio.TimeoutError:
        raise Exception("Database timeout")

async def cache_lookup(timeout: float):
    try:
        await asyncio.wait_for(
            asyncio.sleep(0.05),  # Cache is fast
            timeout=timeout
        )
        return {"cached": False}
    except asyncio.TimeoutError:
        raise Exception("Cache timeout")

async def api_call(timeout: float):
    try:
        await asyncio.wait_for(
            asyncio.sleep(0.2),  # External API
            timeout=timeout
        )
        return {"data": "result"}
    except asyncio.TimeoutError:
        raise Exception("API timeout")

# Exercise: Implement service with coordinated timeouts
async def complex_operation(user_timeout: float = 3.0):
    """
    Implement a service that:
    1. Checks cache (fast)
    2. If miss, queries database
    3. Enriches with API call
    4. Has retry logic
    5. Respects total timeout budget
    """
    coordinator = TimeoutCoordinator(user_timeout)
    
    # TODO: Implement the operation with proper timeout coordination
    pass

# Test the implementation
async def test_timeout_coordination():
    # Test various scenarios
    scenarios = [
        ("Normal operation", 3.0),
        ("Tight deadline", 1.0),
        ("Generous timeout", 10.0)
    ]
    
    for name, timeout in scenarios:
        print(f"\n{name} (timeout={timeout}s):")
        try:
            start = time.time()
            result = await complex_operation(timeout)
            elapsed = time.time() - start
            print(f"  Success in {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  Failed after {elapsed:.2f}s: {e}")

# Run the test
asyncio.run(test_timeout_coordination())
```

<details>
<summary>Solution</summary>

```python
import asyncio
import time
from typing import Optional

class TimeoutCoordinator:
    def __init__(self, total_budget: float):
        self.total_budget = total_budget
        self.start_time = time.time()
        self.operations = []
        
    def get_remaining_budget(self) -> float:
        elapsed = time.time() - self.start_time
        return max(0, self.total_budget - elapsed)
    
    def child_timeout(self, 
                     operation_name: str,
                     operation_fraction: float = 0.8,
                     min_timeout: float = 0.1) -> float:
        """Calculate timeout for child operation"""
        remaining = self.get_remaining_budget()
        
        # Record operation for debugging
        self.operations.append({
            'name': operation_name,
            'remaining_budget': remaining,
            'timestamp': time.time() - self.start_time
        })
        
        if remaining <= 0:
            raise Exception("Timeout budget exhausted")
        
        # Reserve some time for overhead (20%)
        usable_time = remaining * operation_fraction
        
        # Ensure minimum timeout
        timeout = max(usable_time, min_timeout)
        
        # But don't exceed remaining budget
        timeout = min(timeout, remaining)
        
        return timeout
    
    def get_summary(self):
        return {
            'total_budget': self.total_budget,
            'time_used': time.time() - self.start_time,
            'operations': self.operations
        }

# Enhanced service calls with random delays
async def database_query(timeout: float):
    delay = 0.3 + random.uniform(0, 0.4)  # 300-700ms
    try:
        await asyncio.wait_for(asyncio.sleep(delay), timeout=timeout)
        return {"status": "success", "data": "db_result"}
    except asyncio.TimeoutError:
        raise Exception(f"Database timeout (needed {delay:.2f}s, had {timeout:.2f}s)")

async def cache_lookup(timeout: float):
    delay = 0.01 + random.uniform(0, 0.04)  # 10-50ms
    try:
        await asyncio.wait_for(asyncio.sleep(delay), timeout=timeout)
        # 30% cache hit rate
        return {"cached": random.random() < 0.3, "data": "cached_result" if random.random() < 0.3 else None}
    except asyncio.TimeoutError:
        raise Exception(f"Cache timeout")

async def api_call(timeout: float):
    delay = 0.1 + random.uniform(0, 0.3)  # 100-400ms
    try:
        await asyncio.wait_for(asyncio.sleep(delay), timeout=timeout)
        return {"data": "api_result"}
    except asyncio.TimeoutError:
        raise Exception(f"API timeout (needed {delay:.2f}s, had {timeout:.2f}s)")

async def complex_operation(user_timeout: float = 3.0):
    """Service with coordinated timeouts and retries"""
    coordinator = TimeoutCoordinator(user_timeout)
    
    try:
        # Step 1: Check cache (should be fast)
        cache_timeout = coordinator.child_timeout("cache_lookup", 
                                                 operation_fraction=0.1,
                                                 min_timeout=0.1)
        
        cache_result = await cache_lookup(cache_timeout)
        
        if cache_result["cached"]:
            return {"source": "cache", "data": cache_result["data"]}
        
        # Step 2: Query database (might need retry)
        db_result = None
        db_attempts = 0
        max_db_attempts = 2
        
        while db_attempts < max_db_attempts and db_result is None:
            try:
                db_timeout = coordinator.child_timeout(
                    f"database_query_attempt_{db_attempts + 1}",
                    operation_fraction=0.6,  # DB gets most time
                    min_timeout=0.5
                )
                
                db_result = await database_query(db_timeout)
                
            except Exception as e:
                db_attempts += 1
                if db_attempts >= max_db_attempts:
                    raise Exception(f"Database failed after {db_attempts} attempts: {e}")
                
                # Brief pause before retry
                await asyncio.sleep(0.1)
        
        # Step 3: Enrich with API call (optional)
        api_result = None
        try:
            api_timeout = coordinator.child_timeout(
                "api_enrichment",
                operation_fraction=0.5,  # Use half of remaining
                min_timeout=0.2
            )
            
            if api_timeout > 0.2:  # Only try if we have reasonable time
                api_result = await api_call(api_timeout)
        except Exception:
            # API enrichment is optional, don't fail the whole operation
            pass
        
        return {
            "source": "database",
            "data": db_result["data"],
            "enriched": api_result is not None,
            "timing": coordinator.get_summary()
        }
        
    except Exception as e:
        # Log what happened before failing
        summary = coordinator.get_summary()
        raise Exception(f"{e} - Timing: {summary}")

async def test_timeout_coordination():
    scenarios = [
        ("Normal operation", 3.0),
        ("Tight deadline", 1.0),
        ("Generous timeout", 10.0),
        ("Very tight deadline", 0.5)
    ]
    
    for name, timeout in scenarios:
        print(f"\n{name} (timeout={timeout}s):")
        print("-" * 40)
        
        # Run multiple times to see variation
        successes = 0
        total_time = 0
        
        for i in range(5):
            try:
                start = time.time()
                result = await complex_operation(timeout)
                elapsed = time.time() - start
                successes += 1
                total_time += elapsed
                
                print(f"  Run {i+1}: Success in {elapsed:.2f}s from {result['source']}")
                
                if i == 0 and 'timing' in result:
                    print(f"  Operations:")
                    for op in result['timing']['operations']:
                        print(f"    - {op['name']}: "
                              f"at {op['timestamp']:.2f}s, "
                              f"budget: {op['remaining_budget']:.2f}s")
                        
            except Exception as e:
                elapsed = time.time() - start
                print(f"  Run {i+1}: Failed after {elapsed:.2f}s - {str(e)[:50]}...")
        
        if successes > 0:
            print(f"  Summary: {successes}/5 succeeded, avg time: {total_time/successes:.2f}s")
        else:
            print(f"  Summary: All failed")

# Add proper imports at the top
import random

# Run the test
asyncio.run(test_timeout_coordination())
```

</details>

## Exercise 4: Bulkhead Pattern

### 🔧 Try This: Implement Resource Isolation

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import queue
import threading

class BulkheadManager:
    def __init__(self):
        self.bulkheads = {}
        
    def create_bulkhead(self, name: str, size: int, queue_size: int = 10):
        """
        Create an isolated resource pool
        
        TODO: Implement bulkhead with:
        1. Limited thread pool
        2. Bounded queue
        3. Rejection when full
        4. Metrics tracking
        """
        pass
    
    def execute(self, bulkhead_name: str, func, *args, timeout=None, **kwargs):
        """
        Execute function in specified bulkhead
        
        TODO: Implement execution with:
        1. Queue rejection if full
        2. Timeout support
        3. Metrics collection
        4. Graceful degradation
        """
        pass
    
    def get_metrics(self, bulkhead_name: str = None):
        """Get metrics for bulkhead(s)"""
        pass

# Exercise: Create bulkheads for different services
manager = BulkheadManager()

# Create isolated pools
manager.create_bulkhead("database", size=10, queue_size=20)
manager.create_bulkhead("cache", size=50, queue_size=100)  
manager.create_bulkhead("external_api", size=5, queue_size=10)

# Simulate different workloads
def slow_database_query(query_id):
    time.sleep(0.5)  # Slow query
    return f"Result {query_id}"

def fast_cache_lookup(key):
    time.sleep(0.01)  # Fast operation
    return f"Value for {key}"

def unreliable_api_call(endpoint):
    time.sleep(random.uniform(0.1, 2.0))  # Variable latency
    if random.random() < 0.3:
        raise Exception("API error")
    return f"API response from {endpoint}"

# TODO: Test bulkhead isolation
# 1. Flood one bulkhead and verify others still work
# 2. Measure rejection rates
# 3. Verify timeout handling
```

<details>
<summary>Solution</summary>

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError, Future
import queue
import threading
import time
import random
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any

@dataclass
class BulkheadMetrics:
    name: str
    size: int
    queue_size: int
    active_threads: int = 0
    queued_tasks: int = 0
    completed_tasks: int = 0
    rejected_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    
    def success_rate(self) -> float:
        total = self.completed_tasks + self.failed_tasks
        return self.completed_tasks / max(1, total)
    
    def rejection_rate(self) -> float:
        total = self.completed_tasks + self.failed_tasks + self.rejected_tasks
        return self.rejected_tasks / max(1, total)
    
    def avg_execution_time(self) -> float:
        return self.total_execution_time / max(1, self.completed_tasks)

class Bulkhead:
    def __init__(self, name: str, size: int, queue_size: int):
        self.name = name
        self.executor = ThreadPoolExecutor(max_workers=size, thread_name_prefix=f"bulkhead-{name}")
        self.semaphore = threading.BoundedSemaphore(size + queue_size)
        self.metrics = BulkheadMetrics(name=name, size=size, queue_size=queue_size)
        self.lock = threading.Lock()
        
    def submit(self, func: Callable, *args, **kwargs) -> Optional[Future]:
        # Try to acquire semaphore (non-blocking)
        acquired = self.semaphore.acquire(blocking=False)
        
        if not acquired:
            with self.lock:
                self.metrics.rejected_tasks += 1
            raise queue.Full(f"Bulkhead '{self.name}' is full")
        
        def wrapped_func():
            start_time = time.time()
            try:
                with self.lock:
                    self.metrics.active_threads += 1
                    self.metrics.queued_tasks = self.executor._threads
                
                result = func(*args, **kwargs)
                
                with self.lock:
                    self.metrics.completed_tasks += 1
                    self.metrics.total_execution_time += time.time() - start_time
                
                return result
                
            except Exception as e:
                with self.lock:
                    self.metrics.failed_tasks += 1
                raise e
                
            finally:
                with self.lock:
                    self.metrics.active_threads -= 1
                self.semaphore.release()
        
        return self.executor.submit(wrapped_func)
    
    def shutdown(self):
        self.executor.shutdown(wait=True)

class BulkheadManager:
    def __init__(self):
        self.bulkheads: Dict[str, Bulkhead] = {}
        
    def create_bulkhead(self, name: str, size: int, queue_size: int = 10):
        if name in self.bulkheads:
            raise ValueError(f"Bulkhead '{name}' already exists")
        
        self.bulkheads[name] = Bulkhead(name, size, queue_size)
        print(f"Created bulkhead '{name}' with size={size}, queue_size={queue_size}")
        
    def execute(self, bulkhead_name: str, func, *args, timeout=None, **kwargs):
        if bulkhead_name not in self.bulkheads:
            raise ValueError(f"Bulkhead '{bulkhead_name}' not found")
        
        bulkhead = self.bulkheads[bulkhead_name]
        
        try:
            future = bulkhead.submit(func, *args, **kwargs)
            if future is None:
                return None
                
            result = future.result(timeout=timeout)
            return result
            
        except queue.Full:
            print(f"Bulkhead '{bulkhead_name}' full - request rejected")
            raise
        except TimeoutError:
            print(f"Operation in bulkhead '{bulkhead_name}' timed out")
            raise
        except Exception as e:
            print(f"Operation in bulkhead '{bulkhead_name}' failed: {e}")
            raise
    
    def get_metrics(self, bulkhead_name: str = None):
        if bulkhead_name:
            if bulkhead_name not in self.bulkheads:
                return None
            return self.bulkheads[bulkhead_name].metrics
        
        return {name: bulkhead.metrics for name, bulkhead in self.bulkheads.items()}
    
    def shutdown_all(self):
        for bulkhead in self.bulkheads.values():
            bulkhead.shutdown()

# Test implementation
def test_bulkhead_isolation():
    manager = BulkheadManager()
    
    # Create isolated pools
    manager.create_bulkhead("database", size=5, queue_size=5)
    manager.create_bulkhead("cache", size=20, queue_size=30)
    manager.create_bulkhead("external_api", size=3, queue_size=2)
    
    # Service simulations
    def slow_database_query(query_id):
        time.sleep(0.5)
        return f"DB Result {query_id}"
    
    def fast_cache_lookup(key):
        time.sleep(0.01)
        return f"Cached: {key}"
    
    def unreliable_api_call(endpoint):
        time.sleep(random.uniform(0.1, 2.0))
        if random.random() < 0.3:
            raise Exception("API error")
        return f"API: {endpoint}"
    
    print("\n=== Phase 1: Normal Operation ===")
    # Normal operation
    results = []
    for i in range(5):
        try:
            results.append(manager.execute("database", slow_database_query, i))
            results.append(manager.execute("cache", fast_cache_lookup, f"key_{i}"))
            results.append(manager.execute("external_api", unreliable_api_call, f"endpoint_{i}"))
        except Exception as e:
            print(f"Error: {e}")
    
    time.sleep(1)  # Let some complete
    
    print("\n=== Phase 2: Flood Database Bulkhead ===")
    # Flood database bulkhead
    db_futures = []
    rejected_count = 0
    
    for i in range(20):
        try:
            future = manager.bulkheads["database"].submit(slow_database_query, f"flood_{i}")
            db_futures.append(future)
        except queue.Full:
            rejected_count += 1
    
    print(f"Database bulkhead: {len(db_futures)} accepted, {rejected_count} rejected")
    
    # Verify other bulkheads still work
    print("\nTesting other bulkheads while database is flooded:")
    
    for i in range(10):
        try:
            cache_result = manager.execute("cache", fast_cache_lookup, f"test_{i}", timeout=0.1)
            print(f"  Cache still working: {cache_result}")
        except Exception as e:
            print(f"  Cache error: {e}")
    
    print("\n=== Phase 3: Metrics Report ===")
    time.sleep(3)  # Let operations complete
    
    all_metrics = manager.get_metrics()
    
    print(f"\n{'Bulkhead':<15} {'Size':<6} {'Queue':<6} {'Active':<8} {'Complete':<10} {'Failed':<8} {'Rejected':<10} {'Success%':<10} {'Reject%':<10} {'Avg Time':<10}")
    print("-" * 120)
    
    for name, metrics in all_metrics.items():
        print(f"{metrics.name:<15} {metrics.size:<6} {metrics.queue_size:<6} "
              f"{metrics.active_threads:<8} {metrics.completed_tasks:<10} "
              f"{metrics.failed_tasks:<8} {metrics.rejected_tasks:<10} "
              f"{metrics.success_rate():<10.1%} {metrics.rejection_rate():<10.1%} "
              f"{metrics.avg_execution_time:<10.3f}s")
    
    print("\n=== Phase 4: Timeout Testing ===")
    
    def hanging_operation():
        time.sleep(5)  # Longer than timeout
        return "Should not see this"
    
    try:
        result = manager.execute("external_api", hanging_operation, timeout=1.0)
    except TimeoutError:
        print("Timeout handled correctly")
    
    # Cleanup
    manager.shutdown_all()
    
    print("\n=== Insights ===")
    print("1. Database bulkhead protected other services during flood")
    print("2. Cache operations continued despite database overload")
    print("3. Rejection is better than system-wide slowdown")
    print("4. Proper sizing prevents most rejections")

# Run the test
test_bulkhead_isolation()
```

</details>

## Exercise 5: Chaos Engineering

### 🔧 Try This: Build a Chaos Injector

```python
import random
import functools
import time

class ChaosInjector:
    def __init__(self):
        self.failure_modes = {
            'latency': self.inject_latency,
            'error': self.inject_error,
            'partial': self.inject_partial_response,
            'timeout': self.inject_timeout
        }
        self.enabled = True
        
    def inject_latency(self, func, min_delay=0.1, max_delay=2.0):
        """Add random latency to function calls"""
        # TODO: Implement latency injection
        pass
    
    def inject_error(self, func, error_rate=0.1):
        """Randomly fail function calls"""
        # TODO: Implement error injection
        pass
    
    def inject_partial_response(self, func, truncate_rate=0.1):
        """Return partial/corrupted responses"""
        # TODO: Implement partial response
        pass
    
    def inject_timeout(self, func, timeout_rate=0.1):
        """Simulate timeouts"""
        # TODO: Implement timeout simulation
        pass
    
    def chaos(self, failure_mode='random', **kwargs):
        """Decorator to add chaos to functions"""
        # TODO: Implement decorator that applies chaos
        pass

# Exercise: Test system resilience
chaos = ChaosInjector()

# Normal service
@chaos.chaos(failure_mode='latency', min_delay=0.5, max_delay=2.0)
def fetch_user_data(user_id):
    # Simulate database lookup
    return {"id": user_id, "name": f"User{user_id}", "balance": 1000}

@chaos.chaos(failure_mode='error', error_rate=0.2)
def process_payment(amount):
    # Simulate payment processing
    return {"status": "success", "transaction_id": random.randint(1000, 9999)}

@chaos.chaos(failure_mode='partial', truncate_rate=0.1)
def get_recommendations(user_id):
    # Simulate recommendation service
    items = [f"item_{i}" for i in range(10)]
    return {"user_id": user_id, "items": items}

# TODO: Build a resilient client that handles chaos
class ResilientClient:
    def __init__(self):
        # Add resilience patterns
        pass
    
    def get_user_dashboard(self, user_id):
        """
        Fetch user dashboard with:
        1. User data (required)
        2. Recent transactions (optional)
        3. Recommendations (optional)
        
        Should degrade gracefully under chaos
        """
        pass

# Test under different chaos scenarios
```

<details>
<summary>Solution</summary>

```python
import random
import functools
import time
import threading
from typing import Any, Callable, Optional
import json

class ChaosInjector:
    def __init__(self):
        self.failure_modes = {
            'latency': self.inject_latency,
            'error': self.inject_error,
            'partial': self.inject_partial_response,
            'timeout': self.inject_timeout,
            'random': self.inject_random
        }
        self.enabled = True
        self.failure_log = []
        self.lock = threading.Lock()
        
    def log_failure(self, mode: str, details: dict):
        with self.lock:
            self.failure_log.append({
                'timestamp': time.time(),
                'mode': mode,
                'details': details
            })
    
    def inject_latency(self, func, *args, min_delay=0.1, max_delay=2.0, **kwargs):
        """Add random latency to function calls"""
        delay = random.uniform(min_delay, max_delay)
        self.log_failure('latency', {'delay': delay, 'function': func.__name__})
        time.sleep(delay)
        return func(*args, **kwargs)
    
    def inject_error(self, func, *args, error_rate=0.1, error_type=None, **kwargs):
        """Randomly fail function calls"""
        if random.random() < error_rate:
            error = error_type or Exception(f"Chaos: {func.__name__} failed")
            self.log_failure('error', {'function': func.__name__, 'error': str(error)})
            raise error
        return func(*args, **kwargs)
    
    def inject_partial_response(self, func, *args, truncate_rate=0.1, **kwargs):
        """Return partial/corrupted responses"""
        result = func(*args, **kwargs)
        
        if random.random() < truncate_rate:
            self.log_failure('partial', {'function': func.__name__, 'original_type': type(result).__name__})
            
            if isinstance(result, dict):
                # Remove random keys
                keys = list(result.keys())
                if keys:
                    remove_count = random.randint(1, max(1, len(keys) // 2))
                    for _ in range(remove_count):
                        if keys:
                            key = random.choice(keys)
                            keys.remove(key)
                            result.pop(key, None)
            
            elif isinstance(result, list):
                # Truncate list
                if result:
                    truncate_at = random.randint(1, max(1, len(result) // 2))
                    result = result[:truncate_at]
            
            elif isinstance(result, str):
                # Truncate string
                if result:
                    truncate_at = random.randint(1, max(1, len(result) // 2))
                    result = result[:truncate_at] + "..."
        
        return result
    
    def inject_timeout(self, func, *args, timeout_rate=0.1, timeout_delay=5.0, **kwargs):
        """Simulate timeouts"""
        if random.random() < timeout_rate:
            self.log_failure('timeout', {'function': func.__name__, 'delay': timeout_delay})
            time.sleep(timeout_delay)
            raise TimeoutError(f"Chaos: {func.__name__} timed out")
        return func(*args, **kwargs)
    
    def inject_random(self, func, *args, **kwargs):
        """Randomly choose a failure mode"""
        modes = ['latency', 'error', 'partial', 'timeout', 'success']
        mode = random.choice(modes)
        
        if mode == 'success':
            return func(*args, **kwargs)
        elif mode == 'latency':
            return self.inject_latency(func, *args, **kwargs)
        elif mode == 'error':
            return self.inject_error(func, *args, error_rate=1.0, **kwargs)
        elif mode == 'partial':
            return self.inject_partial_response(func, *args, truncate_rate=1.0, **kwargs)
        elif mode == 'timeout':
            return self.inject_timeout(func, *args, timeout_rate=1.0, timeout_delay=1.0, **kwargs)
    
    def chaos(self, failure_mode='random', **kwargs):
        """Decorator to add chaos to functions"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **wrapper_kwargs):
                if not self.enabled:
                    return func(*args, **wrapper_kwargs)
                
                injector = self.failure_modes.get(failure_mode, self.inject_random)
                return injector(func, *args, **{**kwargs, **wrapper_kwargs})
            
            return wrapper
        return decorator
    
    def get_failure_summary(self):
        with self.lock:
            summary = {}
            for failure in self.failure_log:
                mode = failure['mode']
                summary[mode] = summary.get(mode, 0) + 1
            return summary

# Create chaos injector
chaos = ChaosInjector()

# Services with chaos
@chaos.chaos(failure_mode='latency', min_delay=0.5, max_delay=2.0)
def fetch_user_data(user_id):
    return {"id": user_id, "name": f"User{user_id}", "balance": 1000}

@chaos.chaos(failure_mode='error', error_rate=0.2)
def process_payment(amount):
    return {"status": "success", "transaction_id": random.randint(1000, 9999)}

@chaos.chaos(failure_mode='partial', truncate_rate=0.3)
def get_recommendations(user_id):
    items = [f"item_{i}" for i in range(10)]
    return {"user_id": user_id, "items": items, "score": 0.95}

@chaos.chaos(failure_mode='timeout', timeout_rate=0.15, timeout_delay=2.0)
def get_transaction_history(user_id):
    return {
        "user_id": user_id,
        "transactions": [
            {"id": i, "amount": random.randint(10, 100), "date": "2024-01-01"}
            for i in range(5)
        ]
    }

# Resilient client implementation
class ResilientClient:
    def __init__(self):
        self.timeout_default = 1.0
        self.cache = {}
        self.circuit_breakers = {}
        
    def with_fallback(self, func, fallback_value, timeout=None):
        """Execute function with fallback on failure"""
        try:
            return func()
        except Exception as e:
            print(f"  Failed: {func.__name__} - {e}, using fallback")
            return fallback_value
    
    def with_cache(self, key, func, ttl=60):
        """Cache successful responses"""
        if key in self.cache:
            cached_value, cached_time = self.cache[key]
            if time.time() - cached_time < ttl:
                print(f"  Cache hit for {key}")
                return cached_value
        
        try:
            value = func()
            self.cache[key] = (value, time.time())
            return value
        except Exception:
            if key in self.cache:
                print(f"  Using stale cache for {key}")
                return self.cache[key][0]
            raise
    
    def get_user_dashboard(self, user_id):
        """Fetch user dashboard with graceful degradation"""
        print(f"\nFetching dashboard for user {user_id}...")
        
        dashboard = {
            "user_id": user_id,
            "timestamp": time.time(),
            "partial_failure": False
        }
        
        # 1. User data (required) - with retry and cache
        user_data = None
        for attempt in range(3):
            try:
                user_data = self.with_cache(
                    f"user_{user_id}",
                    lambda: fetch_user_data(user_id),
                    ttl=300
                )
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  CRITICAL: Could not fetch user data after 3 attempts")
                    return None  # Can't build dashboard without user data
                print(f"  Retry {attempt + 1} for user data...")
                time.sleep(0.1 * (attempt + 1))
        
        dashboard["user"] = user_data
        
        # 2. Transaction history (optional) - with timeout
        dashboard["transactions"] = self.with_fallback(
            lambda: get_transaction_history(user_id),
            fallback_value={"transactions": [], "error": "temporarily unavailable"}
        )
        
        if "error" in dashboard["transactions"]:
            dashboard["partial_failure"] = True
        
        # 3. Recommendations (optional) - can fail completely
        dashboard["recommendations"] = self.with_fallback(
            lambda: get_recommendations(user_id),
            fallback_value={"items": [], "error": "service unavailable"}
        )
        
        if "error" in dashboard["recommendations"]:
            dashboard["partial_failure"] = True
        
        # 4. Payment status (optional) - simulate a check
        dashboard["payment_enabled"] = self.with_fallback(
            lambda: process_payment(0)["status"] == "success",
            fallback_value=None
        )
        
        return dashboard

# Test the system
def test_chaos_resilience():
    client = ResilientClient()
    
    print("=== Testing System Under Chaos ===\n")
    
    # Test multiple users
    successful_dashboards = 0
    partial_dashboards = 0
    failed_dashboards = 0
    
    for user_id in range(1, 11):
        dashboard = client.get_user_dashboard(user_id)
        
        if dashboard is None:
            failed_dashboards += 1
            print(f"Result: FAILED - No dashboard returned")
        elif dashboard.get("partial_failure"):
            partial_dashboards += 1
            print(f"Result: PARTIAL - Dashboard with degraded features")
            print(f"  User: {dashboard['user']}")
            print(f"  Transactions: {'Available' if dashboard['transactions'].get('transactions') else 'Unavailable'}")
            print(f"  Recommendations: {'Available' if dashboard['recommendations'].get('items') else 'Unavailable'}")
        else:
            successful_dashboards += 1
            print(f"Result: SUCCESS - Full dashboard")
        
        time.sleep(0.5)  # Space out requests
    
    print("\n=== Chaos Summary ===")
    failure_summary = chaos.get_failure_summary()
    for mode, count in failure_summary.items():
        print(f"{mode}: {count} incidents")
    
    print(f"\n=== Results ===")
    print(f"Successful dashboards: {successful_dashboards}")
    print(f"Partial dashboards: {partial_dashboards}")
    print(f"Failed dashboards: {failed_dashboards}")
    print(f"Success rate: {(successful_dashboards + partial_dashboards) / 10:.1%}")
    
    print("\n=== Insights ===")
    print("1. Critical data (user) has retry logic and caching")
    print("2. Optional features degrade gracefully")
    print("3. Partial success is better than complete failure")
    print("4. Chaos testing reveals system weak points")

# Run the test
test_chaos_resilience()

# Bonus: Test with chaos disabled
print("\n\n=== Testing with Chaos Disabled ===")
chaos.enabled = False
client2 = ResilientClient()
for user_id in range(1, 4):
    dashboard = client2.get_user_dashboard(user_id)
    print(f"User {user_id}: All features available")
```

</details>

## Challenge Problems

### 1. The Distributed Lock Problem 🔒

Design a distributed lock that handles:
- Network partitions
- Process crashes
- Clock skew
- Byzantine failures

### 2. The Graceful Degradation System 📉

Build a service that automatically:
- Detects feature health
- Disables unhealthy features
- Maintains core functionality
- Re-enables when healthy

### 3. The Intelligent Retry System 🔄

Create a retry system that:
- Learns from failure patterns
- Adjusts strategies dynamically
- Prevents thundering herds
- Minimizes wasted work

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Building circuit breakers
    - ✅ Implementing smart retries
    - ✅ Coordinating timeouts
    - ✅ Isolating with bulkheads
    - ✅ Testing with chaos engineering

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 4: Concurrency](../axiom-4-concurrency/index.md) →
    
    **Back to**: [Failure Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Chaos Tools](../../tools/chaos-toolkit.md) | [Part II](../../part2-pillars/index.md)