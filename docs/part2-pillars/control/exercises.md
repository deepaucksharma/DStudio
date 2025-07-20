---
title: Control & Coordination Exercises
description: <details>
<summary>Solution</summary>
type: pillar
difficulty: intermediate
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Control](/part2-pillars/control/) → **Control & Coordination Exercises**

# Control & Coordination Exercises

## Exercise 1: Build a Circuit Breaker

**Challenge**: Implement a thread-safe circuit breaker with configurable thresholds.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception types to count as failures
        """
        # TODO: Initialize state machine
        # States: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
        pass

    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker

        TODO:
        1. Check current state
        2. Execute function if allowed
        3. Track success/failure
        4. Transition states as needed
        """
        pass

    def record_success(self):
        """Record successful call"""
        pass

    def record_failure(self):
        """Record failed call"""
        pass

    def reset(self):
        """Manual reset of circuit breaker"""
        pass
```

<details>
<summary>Solution</summary>

```python
import time
import threading
from enum import Enum
from datetime import datetime, timedelta

class State(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._state = State.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._lock = threading.RLock()

        # Metrics
        self._success_count = 0
        self._total_calls = 0

    @property
    def state(self):
        with self._lock:
            if self._state == State.OPEN:
                if self._should_attempt_reset():
                    self._state = State.HALF_OPEN
            return self._state

    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        with self._lock:
            self._total_calls += 1

            if self.state == State.OPEN:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN. Failures: {self._failure_count}"
                )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result

        except self.expected_exception as e:
            self.record_failure()
            raise e

    def record_success(self):
        """Record successful call"""
        with self._lock:
            self._success_count += 1

            if self._state == State.HALF_OPEN:
                # Success in half-open state, close the circuit
                self._state = State.CLOSED
                self._failure_count = 0
                self._last_failure_time = None
                print(f"Circuit breaker CLOSED after successful recovery")

    def record_failure(self):
        """Record failed call"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == State.HALF_OPEN:
                # Failure in half-open state, re-open the circuit
                self._state = State.OPEN
                print(f"Circuit breaker RE-OPENED after recovery failure")

            elif self._failure_count >= self.failure_threshold:
                # Too many failures, open the circuit
                self._state = State.OPEN
                print(f"Circuit breaker OPENED after {self._failure_count} failures")

    def reset(self):
        """Manual reset of circuit breaker"""
        with self._lock:
            self._state = State.CLOSED
            self._failure_count = 0
            self._last_failure_time = None
            self._success_count = 0
            print("Circuit breaker manually RESET")

    def _should_attempt_reset(self):
        """Check if enough time has passed to try recovery"""
        return (
            self._last_failure_time and
            time.time() - self._last_failure_time >= self.recovery_timeout
        )

    def get_stats(self):
        """Get circuit breaker statistics"""
        with self._lock:
            success_rate = (
                self._success_count / self._total_calls
                if self._total_calls > 0 else 0
            )

            return {
                'state': self._state.value,
                'failure_count': self._failure_count,
                'success_count': self._success_count,
                'total_calls': self._total_calls,
                'success_rate': success_rate,
                'last_failure_time': self._last_failure_time
            }

class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is open"""
    pass

# Advanced circuit breaker with multiple failure types
class AdvancedCircuitBreaker(CircuitBreaker):
    def __init__(self, failure_threshold=5, recovery_timeout=60,
                 expected_exceptions=None, exclude_exceptions=None):
        super().__init__(failure_threshold, recovery_timeout, Exception)
        self.expected_exceptions = expected_exceptions or [Exception]
        self.exclude_exceptions = exclude_exceptions or []

        # Per-exception tracking
        self._exception_counts = {}

    def call(self, func, *args, **kwargs):
        """Execute with exception filtering"""
        with self._lock:
            self._total_calls += 1

            if self.state == State.OPEN:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN"
                )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result

        except Exception as e:
            # Check if we should count this exception
            if self._should_count_exception(e):
                self.record_failure()
                self._track_exception(e)
            raise e

    def _should_count_exception(self, exception):
        """Determine if exception should trigger circuit breaker"""
        # Exclude specific exceptions
        for exclude_type in self.exclude_exceptions:
            if isinstance(exception, exclude_type):
                return False

        # Include specific exceptions
        for expected_type in self.expected_exceptions:
            if isinstance(exception, expected_type):
                return True

        return False

    def _track_exception(self, exception):
        """Track exception types for debugging"""
        exc_type = type(exception).__name__
        if exc_type not in self._exception_counts:
            self._exception_counts[exc_type] = 0
        self._exception_counts[exc_type] += 1

# Test the circuit breaker
def test_circuit_breaker():
    def flaky_service(should_fail=False):
        if should_fail:
            raise ConnectionError("Service unavailable")
        return "Success!"

    # Create circuit breaker
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=5,
        expected_exception=ConnectionError
    )

    # Test normal operation
    print("Testing normal operation...")
    for i in range(5):
        try:
            result = cb.call(flaky_service, should_fail=False)
            print(f"Call {i+1}: {result}")
        except Exception as e:
            print(f"Call {i+1} failed: {e}")

    print(f"\nStats: {cb.get_stats()}")

    # Test circuit opening
    print("\nTesting circuit opening...")
    for i in range(5):
        try:
            result = cb.call(flaky_service, should_fail=True)
            print(f"Call {i+1}: {result}")
        except CircuitBreakerOpenException as e:
            print(f"Call {i+1}: Circuit breaker open!")
        except Exception as e:
            print(f"Call {i+1} failed: {e}")

    print(f"\nStats: {cb.get_stats()}")

    # Wait for recovery
    print("\nWaiting for recovery timeout...")
    time.sleep(6)

    # Test half-open state
    print("\nTesting half-open state...")
    try:
        result = cb.call(flaky_service, should_fail=False)
        print(f"Recovery successful: {result}")
    except Exception as e:
        print(f"Recovery failed: {e}")

    print(f"\nFinal stats: {cb.get_stats()}")

if __name__ == "__main__":
    test_circuit_breaker()
```

</details>

## Exercise 2: Implement a Rate Limiter

**Challenge**: Build multiple rate limiting algorithms.

```python
class RateLimiter:
    """Base class for rate limiters"""
    def allow_request(self, key):
        raise NotImplementedError

class TokenBucketLimiter(RateLimiter):
    def __init__(self, rate, capacity):
        """
        Token bucket rate limiter

        Args:
            rate: Tokens added per second
            capacity: Maximum tokens in bucket
        """
        # TODO: Implement token bucket algorithm
        pass

class SlidingWindowLimiter(RateLimiter):
    def __init__(self, requests_per_window, window_size):
        """
        Sliding window rate limiter

        Args:
            requests_per_window: Max requests in window
            window_size: Window size in seconds
        """
        # TODO: Implement sliding window algorithm
        pass

class LeakyBucketLimiter(RateLimiter):
    def __init__(self, rate, capacity):
        """
        Leaky bucket rate limiter

        Args:
            rate: Requests processed per second
            capacity: Queue capacity
        """
        # TODO: Implement leaky bucket algorithm
        pass
```

<details>
<summary>Solution</summary>

```python
import time
import threading
from collections import deque, defaultdict

class RateLimiter:
    """Base class for rate limiters"""
    def allow_request(self, key):
        raise NotImplementedError

class TokenBucketLimiter(RateLimiter):
    def __init__(self, rate, capacity):
        """Token bucket rate limiter"""
        self.rate = rate  # Tokens per second
        self.capacity = capacity
        self.buckets = defaultdict(lambda: {
            'tokens': capacity,
            'last_update': time.time()
        })
        self.lock = threading.Lock()

    def allow_request(self, key):
        with self.lock:
            bucket = self.buckets[key]
            now = time.time()

            # Refill tokens
            elapsed = now - bucket['last_update']
            tokens_to_add = elapsed * self.rate
            bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
            bucket['last_update'] = now

            # Check if request allowed
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                return True

            return False

    def get_wait_time(self, key):
        """Get time to wait for next token"""
        with self.lock:
            bucket = self.buckets[key]
            if bucket['tokens'] >= 1:
                return 0

            tokens_needed = 1 - bucket['tokens']
            wait_time = tokens_needed / self.rate
            return wait_time

class SlidingWindowLimiter(RateLimiter):
    def __init__(self, requests_per_window, window_size):
        """Sliding window rate limiter"""
        self.requests_per_window = requests_per_window
        self.window_size = window_size  # seconds
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()

    def allow_request(self, key):
        with self.lock:
            now = time.time()
            window_start = now - self.window_size

            # Remove old requests outside window
            request_times = self.requests[key]
            while request_times and request_times[0] < window_start:
                request_times.popleft()

            # Check if under limit
            if len(request_times) < self.requests_per_window:
                request_times.append(now)
                return True

            return False

    def get_request_count(self, key):
        """Get current request count in window"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size

            # Clean old requests
            request_times = self.requests[key]
            while request_times and request_times[0] < window_start:
                request_times.popleft()

            return len(request_times)

class LeakyBucketLimiter(RateLimiter):
    def __init__(self, rate, capacity):
        """Leaky bucket rate limiter"""
        self.rate = rate  # Requests processed per second
        self.capacity = capacity
        self.queues = defaultdict(lambda: {
            'queue': deque(),
            'last_leak': time.time()
        })
        self.lock = threading.Lock()

    def allow_request(self, key):
        with self.lock:
            bucket = self.queues[key]
            now = time.time()

            # Process leaked requests
            elapsed = now - bucket['last_leak']
            leaked = int(elapsed * self.rate)

            if leaked > 0:
                # Remove leaked requests
                for _ in range(min(leaked, len(bucket['queue']))):
                    bucket['queue'].popleft()
                bucket['last_leak'] = now

            # Check if we can add request
            if len(bucket['queue']) < self.capacity:
                bucket['queue'].append(now)
                return True

            return False

# Advanced: Distributed rate limiter using Redis-like interface
class DistributedRateLimiter:
    def __init__(self, redis_client, rate, window_size):
        self.redis = redis_client
        self.rate = rate
        self.window_size = window_size

    def allow_request(self, key):
        """Sliding window using Redis sorted sets"""
        now = time.time()
        window_start = now - self.window_size

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count requests in window
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(now): now})

        # Set expiry
        pipe.expire(key, self.window_size + 1)

        results = pipe.execute()

        current_requests = results[1]

        if current_requests < self.rate:
            return True
        else:
            # Remove the request we just added
            self.redis.zrem(key, str(now))
            return False

# Hybrid rate limiter with multiple strategies
class HybridRateLimiter:
    def __init__(self):
        # Short-term burst protection
        self.burst_limiter = TokenBucketLimiter(
            rate=100,      # 100 requests/second refill
            capacity=200   # Allow burst of 200
        )

        # Long-term rate limit
        self.sustained_limiter = SlidingWindowLimiter(
            requests_per_window=1000,  # 1000 requests
            window_size=60            # per minute
        )

        # Per-IP limits
        self.ip_limiter = SlidingWindowLimiter(
            requests_per_window=100,
            window_size=60
        )

    def allow_request(self, user_id, ip_address):
        """Check all rate limits"""
        # Check burst limit
        if not self.burst_limiter.allow_request(user_id):
            return False, "Burst limit exceeded"

        # Check sustained limit
        if not self.sustained_limiter.allow_request(user_id):
            return False, "Sustained rate limit exceeded"

        # Check IP limit
        if not self.ip_limiter.allow_request(ip_address):
            return False, "IP rate limit exceeded"

        return True, "OK"

# Test rate limiters
def test_rate_limiters():
    print("Testing Token Bucket...")
    tb = TokenBucketLimiter(rate=10, capacity=20)

    # Use up initial capacity
    successes = 0
    for i in range(25):
        if tb.allow_request("user1"):
            successes += 1
    print(f"Initial burst: {successes}/25 requests allowed")

    # Wait for refill
    time.sleep(1)
    successes = 0
    for i in range(15):
        if tb.allow_request("user1"):
            successes += 1
    print(f"After 1s: {successes}/15 requests allowed")

    print("\nTesting Sliding Window...")
    sw = SlidingWindowLimiter(requests_per_window=10, window_size=5)

    # Fill window
    for i in range(10):
        result = sw.allow_request("user1")
        print(f"Request {i+1}: {'Allowed' if result else 'Denied'}")

    # Try one more
    result = sw.allow_request("user1")
    print(f"Request 11: {'Allowed' if result else 'Denied'}")

    print(f"Current count: {sw.get_request_count('user1')}")

if __name__ == "__main__":
    test_rate_limiters()
```

</details>

## Exercise 3: Build a Distributed Lock

**Challenge**: Implement a distributed lock with automatic expiry and fencing tokens.

```python
class DistributedLock:
    def __init__(self, name, ttl=30):
        """
        Distributed lock implementation

        Args:
            name: Lock name
            ttl: Time to live in seconds
        """
        self.name = name
        self.ttl = ttl

    def acquire(self, timeout=None):
        """
        Acquire lock with optional timeout

        TODO:
        1. Try to acquire lock atomically
        2. Set expiry to prevent deadlocks
        3. Return fencing token if successful
        """
        pass

    def release(self, token):
        """
        Release lock if we own it

        TODO:
        1. Verify token matches
        2. Release atomically
        """
        pass

    def extend(self, token, extension):
        """Extend lock TTL"""
        pass
```

## Exercise 4: Implement Backpressure

**Challenge**: Build a system that applies backpressure when overwhelmed.

```python
class BackpressureQueue:
    def __init__(self, max_size, high_watermark=0.8, low_watermark=0.6):
        """
        Queue with backpressure signaling

        Args:
            max_size: Maximum queue size
            high_watermark: Threshold to start backpressure
            low_watermark: Threshold to stop backpressure
        """
        # TODO: Implement queue with backpressure
        pass

    def put(self, item):
        """Add item, may block or reject based on backpressure"""
        pass

    def get(self):
        """Get item from queue"""
        pass

    def is_accepting(self):
        """Check if queue is accepting new items"""
        pass
```

## Exercise 5: Build an Autoscaler

**Challenge**: Implement an autoscaler that prevents flapping.

```python
class Autoscaler:
    def __init__(self, min_instances=1, max_instances=10):
        self.min_instances = min_instances
        self.max_instances = max_instances

    def decide_scaling(self, metrics):
        """
        Decide whether to scale up, down, or maintain

        Args:
            metrics: Dict with 'cpu', 'memory', 'requests_per_second', etc.

        TODO:
        1. Implement scaling logic
        2. Prevent flapping
        3. Consider multiple metrics
        """
        pass

    def calculate_desired_instances(self, current_instances, metrics):
        """Calculate target instance count"""
        pass
```

## Exercise 6: Gossip Protocol

**Challenge**: Implement a gossip protocol for membership detection.

```python
class GossipNode:
    def __init__(self, node_id, seed_nodes):
        self.node_id = node_id
        self.seed_nodes = seed_nodes
        self.members = {}  # node_id -> {'status': 'alive', 'version': 0}

    def start(self):
        """Start gossiping"""
        # TODO: Implement gossip protocol
        pass

    def gossip_round(self):
        """Perform one round of gossip"""
        # TODO: Select random peers and exchange state
        pass

    def merge_state(self, remote_state):
        """Merge remote state with local state"""
        # TODO: Implement vector clock or version merging
        pass
```

## Exercise 7: Implement Health Checks

**Challenge**: Build a health check system with configurable checks.

```python
class HealthChecker:
    def __init__(self):
        self.checks = {}

    def register_check(self, name, check_func, critical=True):
        """Register a health check"""
        # TODO: Store check with metadata
        pass

    def run_checks(self):
        """
        Run all health checks

        TODO:
        1. Execute checks with timeout
        2. Aggregate results
        3. Determine overall health
        """
        pass

    def get_health_status(self):
        """Return detailed health status"""
        pass
```

## Thought Experiments

### 1. The Thundering Herd Problem
Your cache expires and 10,000 clients simultaneously try to refresh it.
- How do you prevent all 10,000 from hitting the backend?
- Design a solution using distributed locks or probabilistic approaches.

### 2. The Cascading Timeout
Service A calls B with 5s timeout. B calls C with 5s timeout. C takes 4s.
- What happens when multiple requests stack up?
- How do you set timeouts in a call chain?

### 3. The Split-Brain Coordinator
Your coordinator uses a simple majority for decisions. The network partitions 3-2.
- What happens to each partition?
- How do you prevent conflicting decisions?
- Design a solution that maximizes availability.

## Practical Scenarios

### Scenario 1: API Gateway
Design a control system for an API gateway that:
- Rate limits per user and globally
- Routes based on load
- Handles circuit breaking per backend
- Provides authentication/authorization

### Scenario 2: Deployment Controller
Build a controller that:
- Rolls out new versions gradually
- Monitors error rates
- Automatically rolls back on failures
- Maintains desired replica count

### Scenario 3: Traffic Shaper
Create a system that:
- Prioritizes traffic types
- Applies bandwidth limits
- Handles burst traffic
- Ensures fairness

## Research Questions

1. **Why do control systems oscillate?**
   - What causes flapping in autoscalers?
   - How do you dampen oscillations?

2. **When should you use push vs. pull control?**
   - Compare Kubernetes (pull) vs. traditional orchestrators (push)
   - What are the trade-offs?

3. **How do you coordinate without consensus?**
   - When is eventual consistency enough?
   - What are the limits of gossip protocols?

## Key Concepts to Master

1. **Feedback Loops**
   - Negative feedback for stability
   - Positive feedback dangers
   - Control lag and overshoot

2. **Hysteresis**
   - Preventing flapping
   - Different thresholds for scale-up/down
   - Time-based dampening

3. **Hierarchical Control**
   - Local vs. global decisions
   - Delegation and autonomy
   - Information hiding

## Reflection

After completing these exercises:

1. What makes distributed control harder than centralized control?

2. How do you handle partial failures in control systems?

3. When should you use reactive vs. proactive control?

4. What role does observability play in control?

Remember: Control systems shape behavior. Design them to encourage the outcomes you want while being resilient to the failures you'll face.
