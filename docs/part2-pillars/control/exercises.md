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
[Home](../../index.md) → [Part II: Pillars](../index.md) → [Control](index.md) → **Control & Coordination Exercises**

# Control & Coordination Exercises

## Exercise 1: Design a Circuit Breaker System

**Challenge**: Create visual designs for a thread-safe circuit breaker with configurable thresholds.

**Design Tasks**:

1. **Create a Circuit Breaker State Machine**
   ```mermaid
   stateDiagram-v2
       [*] --> Closed: Initialize
       
       Closed --> Open: Failures ≥ Threshold
       Open --> HalfOpen: Recovery Timeout
       HalfOpen --> Open: Any Failure
       HalfOpen --> Closed: Success Count ≥ Threshold
       
       state Closed {
           [*] --> Monitoring
           Monitoring --> Counting: Request
           Counting --> Monitoring: Success
           Counting --> [*]: Failure Limit
       }
       
       state Open {
           [*] --> Rejecting
           Rejecting --> TimerCheck: Request
           TimerCheck --> Rejecting: Too Early
           TimerCheck --> [*]: Time Elapsed
       }
       
       state HalfOpen {
           [*] --> Testing
           Testing --> Tracking: Allow Request
           Tracking --> [*]: Evaluate Results
       }
   ```

2. **Design a Request Flow Diagram**
   ```mermaid
   flowchart TD
       Request[Incoming Request]
       
       Request --> GetState[Get Circuit State]
       GetState --> StateCheck{State?}
       
       StateCheck -->|Closed| Execute[Execute Function]
       StateCheck -->|Open| TimeCheck{Timeout<br/>Elapsed?}
       StateCheck -->|Half-Open| TestExecute[Test Execute]
       
       TimeCheck -->|No| ReturnFallback[Return Fallback]
       TimeCheck -->|Yes| TransitionHalf[Transition to<br/>Half-Open]
       
       Execute --> Result{Success?}
       Result -->|Yes| RecordSuccess[Record Success]
       Result -->|No| RecordFailure[Record Failure]
       
       RecordFailure --> CheckThreshold{Failures ≥<br/>Threshold?}
       CheckThreshold -->|Yes| OpenCircuit[Open Circuit]
       CheckThreshold -->|No| ReturnError[Return Error]
       
       TestExecute --> TestResult{Success?}
       TestResult -->|Yes| IncrementSuccess[Success++]
       TestResult -->|No| BackToOpen[Back to Open]
       
       IncrementSuccess --> CheckSuccess{Successes ≥<br/>Threshold?}
       CheckSuccess -->|Yes| CloseCircuit[Close Circuit]
       CheckSuccess -->|No| StayHalfOpen[Stay Half-Open]
       
       style ReturnFallback fill:#FFE4B5
       style OpenCircuit fill:#FFB6C1
       style CloseCircuit fill:#90EE90
   ```

3. **Create a Thread-Safety Design**
   ```mermaid
   graph LR
       subgraph "Concurrent Access Control"
           T1[Thread 1] --> Lock[Acquire Lock]
           T2[Thread 2] --> Lock
           T3[Thread 3] --> Lock
           
           Lock --> CS[Critical Section<br/>State Check/Update]
           CS --> Release[Release Lock]
       end
       
       subgraph "Atomic Operations"
           State[Circuit State<br/>Atomic Reference]
           Counter[Failure Counter<br/>Atomic Integer]
           Timer[Last Failure Time<br/>Atomic Long]
       end
       
       CS --> State & Counter & Timer
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

## Exercise 2: Design Rate Limiting Systems

**Challenge**: Create visual designs for multiple rate limiting algorithms.

**Design Tasks**:

1. **Compare Rate Limiting Algorithms**
   ```mermaid
   graph TB
       subgraph "Token Bucket"
           TB[Token Bucket<br/>Capacity: 100]
           TBRefill[+10 tokens/sec]
           TBReq[Request -1 token]
           
           TBRefill -->|Continuous| TB
           TB -->|Has tokens?| TBReq
       end
       
       subgraph "Sliding Window"
           SW[Window: 60s<br/>Limit: 100 req]
           SWTime[Current Time]
           SWCount[Count requests in<br/>last 60s]
           
           SWTime --> SWCount
           SWCount -->|< 100?| SWAllow[Allow]
       end
       
       subgraph "Leaky Bucket"
           LB[Queue<br/>Capacity: 100]
           LBIn[Requests In]
           LBOut[Process at<br/>10 req/sec]
           
           LBIn -->|Queue not full?| LB
           LB -->|Constant rate| LBOut
       end
   ```

2. **Design Token Bucket State Flow**
   ```mermaid
   flowchart TD
       Start[Request Arrives]
       Start --> Refill[Calculate Token Refill<br/>tokens += (now - lastUpdate) * rate]
       
       Refill --> Cap[Cap at Bucket Size<br/>tokens = min(tokens, capacity)]
       
       Cap --> Check{tokens ≥ 1?}
       
       Check -->|Yes| Consume[tokens -= 1<br/>Allow Request]
       Check -->|No| Reject[Reject Request]
       
       Consume --> Update1[lastUpdate = now]
       Reject --> Update2[lastUpdate = now]
       
       subgraph "Example State"
           State["Time: 10:00:05<br/>Tokens: 45/100<br/>Rate: 10/sec<br/>Last Update: 10:00:04"]
       end
       
       style Consume fill:#90EE90
       style Reject fill:#FFB6C1
   ```

3. **Create a Multi-User Rate Limiter Architecture**
   ```mermaid
   graph LR
       subgraph "Rate Limiter Service"
           subgraph "User Buckets"
               U1[User1<br/>Tokens: 80/100]
               U2[User2<br/>Tokens: 15/100]
               U3[User3<br/>Tokens: 95/100]
           end
           
           subgraph "Global Limits"
               Global[Global<br/>10K req/sec]
               PerIP[Per IP<br/>100 req/sec]
           end
       end
       
       subgraph "Request Flow"
           Req1[Request<br/>User: 1<br/>IP: 1.2.3.4]
           Req1 --> UC{User Check}
           UC --> IC{IP Check}
           IC --> GC{Global Check}
           GC --> Decision{All Pass?}
           Decision -->|Yes| Allow
           Decision -->|No| Deny
       end
       
       style Allow fill:#90EE90
       style Deny fill:#FFB6C1
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

## Exercise 3: Design a Distributed Lock System

**Challenge**: Create visual designs for a distributed lock with automatic expiry and fencing tokens.

**Design Tasks**:

1. **Design Lock Acquisition Flow**
   ```mermaid
   sequenceDiagram
       participant Client
       participant LockService
       participant Storage
       
       Client->>LockService: acquire("resource-1", ttl=30s)
       LockService->>Storage: SET resource-1 IF NOT EXISTS
       
       alt Lock Available
           Storage-->>LockService: Success
           LockService->>LockService: Generate Fencing Token
           LockService-->>Client: Token: 12345, Expires: 30s
       else Lock Held
           Storage-->>LockService: Key Exists
           LockService-->>Client: Lock Unavailable
           
           opt With Timeout
               loop Wait with backoff
                   Client->>LockService: Retry acquire
                   Note over Client: Until timeout or success
               end
           end
       end
   ```

2. **Create Fencing Token State Machine**
   ```mermaid
   stateDiagram-v2
       [*] --> Available: Lock Released
       
       Available --> Acquired: Client Acquires
       Acquired --> Extended: Client Extends TTL
       Extended --> Extended: Further Extensions
       Extended --> Released: Client Releases
       Acquired --> Released: Client Releases
       
       Acquired --> Expired: TTL Exceeded
       Extended --> Expired: TTL Exceeded
       Expired --> Available: Auto-Release
       
       state Acquired {
           [*] --> Active
           Active --> Checking: Heartbeat
           Checking --> Active: Valid Token
           Checking --> [*]: Invalid Token
       }
       
       note right of Expired: Prevents deadlocks from<br/>crashed clients
   ```

3. **Design Lock Safety with Fencing Tokens**
   ```mermaid
   flowchart LR
       subgraph "Unsafe Without Fencing"
           C1A[Client 1<br/>Acquires Lock]
           C1A --> Pause1[Network Pause]
           Pause1 --> Expire1[Lock Expires]
           Expire1 --> C2A[Client 2<br/>Acquires Lock]
           C2A --> C1W[Client 1 Writes<br/>DANGER!]
           C1W --> C2W[Client 2 Writes<br/>CONFLICT!]
           
           style C1W fill:#FF6B6B
           style C2W fill:#FF6B6B
       end
       
       subgraph "Safe With Fencing"
           C1B[Client 1<br/>Lock + Token:100]
           C1B --> Pause2[Network Pause]
           Pause2 --> Expire2[Lock Expires]
           Expire2 --> C2B[Client 2<br/>Lock + Token:101]
           C2B --> C1R[Client 1 Write<br/>Token:100]
           C1R --> Reject[Storage Rejects<br/>Token too old]
           
           style Reject fill:#90EE90
       end
   ```

## Exercise 4: Design Backpressure Mechanisms

**Challenge**: Create visual designs for a system that applies backpressure when overwhelmed.

**Design Tasks**:

1. **Design Backpressure State Machine**
   ```mermaid
   stateDiagram-v2
       [*] --> Accepting: Initial State
       
       Accepting --> Pressuring: Size > High Watermark (80%)
       Pressuring --> Rejecting: Size > Max (100%)
       
       Rejecting --> Pressuring: Size < Max
       Pressuring --> Accepting: Size < Low Watermark (60%)
       
       state Accepting {
           [*] --> Normal
           Normal --> Filling: Requests Coming
       end
       
       state Pressuring {
           [*] --> Signaling
           Signaling --> Slowing: Send Backpressure Signal
       end
       
       state Rejecting {
           [*] --> Full
           Full --> Dropping: Reject New Items
       end
   ```

2. **Create Backpressure Flow Diagram**
   ```mermaid
   flowchart TD
       subgraph "Producer"
           P1[Producer 1]
           P2[Producer 2]
           P3[Producer 3]
       end
       
       subgraph "Queue System"
           Queue[Queue<br/>Size: 850/1000]
           Check{Check Level}
           
           Queue --> Check
           Check -->|< 600| Green[Accept All<br/>Green Signal]
           Check -->|600-800| Yellow[Accept with Delay<br/>Yellow Signal]
           Check -->|> 800| Red[Reject New<br/>Red Signal]
       end
       
       subgraph "Consumer"
           C1[Consumer]
           C1 -->|Process| Queue
       end
       
       P1 & P2 & P3 --> Queue
       
       Green -->|Signal| P1 & P2 & P3
       Yellow -->|Signal| P1 & P2 & P3
       Red -->|Signal| P1 & P2 & P3
       
       style Green fill:#90EE90
       style Yellow fill:#FFE4B5
       style Red fill:#FFB6C1
   ```

3. **Design Multi-Level Backpressure Architecture**
   ```mermaid
   graph LR
       subgraph "Level 1: Application"
           App[Application<br/>Buffer: 70%]
       end
       
       subgraph "Level 2: Network"
           TCP[TCP Buffer<br/>85% Full]
       end
       
       subgraph "Level 3: OS"
           OS[OS Buffer<br/>95% Full]
       end
       
       subgraph "Backpressure Cascade"
           OS -->|Signal| TCP
           TCP -->|Signal| App
           App -->|Slow Down| Client[Client Requests]
       end
       
       subgraph "Responses"
           R1[429 Too Many Requests]
           R2[503 Service Unavailable]
           R3[TCP Window Shrink]
       end
       
       App -.->|HTTP| R1
       App -.->|Overload| R2
       TCP -.->|TCP| R3
   ```

## Exercise 5: Design Autoscaling System

**Challenge**: Visual design for autoscaler preventing flapping.

**Design Tasks**:

1. **Autoscaler Decision Flow**
   ```mermaid
   flowchart TD
       Metrics["CPU: 85%<br/>Mem: 60%<br/>RPS: 1200"]
       
       Metrics --> Eval{Evaluate}
       
       Eval -->|CPU > 80%| ScaleUp[Scale Up]
       Eval -->|CPU < 30%| ScaleDown[Scale Down]
       Eval -->|30-80%| Hold[Maintain]
       
       ScaleUp --> Cool{In Cooldown?}
       ScaleDown --> Cool
       
       Cool -->|Yes| Skip[Skip Action]
       Cool -->|No| Apply[Apply Change]
       
       Apply --> Cooldown[Start Cooldown<br/>3 minutes]
       
       style Apply fill:#90EE90
       style Skip fill:#FFE4B5
   ```

2. **Anti-Flapping State Machine**
   ```mermaid
   stateDiagram-v2
       [*] --> Stable
       
       Stable --> ScalingUp: Threshold exceeded
       ScalingUp --> Cooldown: Action taken
       
       Stable --> ScalingDown: Under-utilized
       ScalingDown --> Cooldown: Action taken
       
       Cooldown --> Stable: Timer expires
       
       state Cooldown {
           [*] --> Waiting
           Waiting --> [*]: 3 min
           
           note right of Waiting: Ignore metrics<br/>Prevent oscillation
       }
   ```

3. **Multi-Metric Scaling Grid**
   ```mermaid
   graph TB
       subgraph "Decision Matrix"
           M["CPU | Mem | RPS | Action<br/>----|-----|-----|--------<br/>90% | 50% | Low | Scale +2<br/>85% | 80% | High| Scale +3<br/>40% | 30% | Low | Scale -1<br/>20% | 20% | Low | Scale -2"]
       end
       
       subgraph "Instance Timeline"
           T1["10:00 - 5 instances"]
           T2["10:03 - 7 instances (+2)"]
           T3["10:06 - 7 instances (cooldown)"]
           T4["10:09 - 6 instances (-1)"]
       end
   ```

## Exercise 6: Design Gossip Protocol

**Challenge**: Visual design for gossip-based membership.

**Design Tasks**:

1. **Gossip Propagation Pattern**
   ```mermaid
   graph TB
       subgraph "Round 1"
           A1[A] -.->|gossip| C1[C]
           B1[B] -.->|gossip| D1[D]
       end
       
       subgraph "Round 2"
           C2[C] -.->|gossip| B2[B]
           D2[D] -.->|gossip| A2[A]
       end
       
       subgraph "Round 3"
           A3[A] -.->|gossip| B3[B]
           C3[C] -.->|gossip| D3[D]
       end
       
       Note1["Info spreads<br/>exponentially<br/>O(log N) rounds"]
   ```

2. **Membership State Merge**
   ```mermaid
   flowchart LR
       Local["Local State<br/>A: alive v5<br/>B: alive v3<br/>C: dead v2"]
       Remote["Remote State<br/>A: alive v4<br/>B: dead v4<br/>D: alive v1"]
       
       Local & Remote --> Merge{Version Compare}
       
       Merge --> Result["Merged State<br/>A: alive v5 (local)<br/>B: dead v4 (remote)<br/>C: dead v2 (local)<br/>D: alive v1 (new)"]
       
       style Result fill:#90EE90
   ```

3. **Failure Detection Timeline**
   ```mermaid
   gantt
       title Node Failure Detection
       dateFormat X
       axisFormat %s
       
       section Node A
       Alive :done, a1, 0, 10
       Suspect :active, a2, 10, 5
       Dead :crit, a3, 15, 10
       
       section Node B View
       Unknown :b1, 0, 3
       Alive :done, b2, 3, 7
       Suspect :active, b3, 10, 8
       Dead :crit, b4, 18, 7
       
       section Node C View
       Unknown :c1, 0, 5
       Alive :done, c2, 5, 5
       Suspect :active, c3, 10, 10
       Dead :crit, c4, 20, 5
   ```

## Exercise 7: Design Health Check System

**Challenge**: Visual design for configurable health checks.

**Design Tasks**:

1. **Health Check Architecture**
   ```mermaid
   graph TB
       subgraph "Health Checks"
           DB[DB Check<br/>Critical]
           API[API Check<br/>Critical]
           Cache[Cache Check<br/>Non-Critical]
           Queue[Queue Check<br/>Non-Critical]
       end
       
       subgraph "Aggregator"
           All[All Checks] --> Eval{Evaluate}
           Eval -->|All Critical Pass| Healthy
           Eval -->|Any Critical Fail| Unhealthy
           Eval -->|Only Non-Critical Fail| Degraded
       end
       
       subgraph "Response"
           Healthy["200 OK<br/>status: healthy"]
           Degraded["200 OK<br/>status: degraded"]
           Unhealthy["503 Unavailable<br/>status: unhealthy"]
       end
       
       style Healthy fill:#90EE90
       style Degraded fill:#FFE4B5
       style Unhealthy fill:#FFB6C1
   ```

2. **Health Check State Flow**
   ```mermaid
   stateDiagram-v2
       [*] --> Running
       
       Running --> Timeout: Exceeds limit
       Running --> Success: Check passes
       Running --> Failed: Check fails
       
       Success --> [*]
       Failed --> [*]
       Timeout --> [*]
       
       state Running {
           [*] --> Execute
           Execute --> Measure
           Measure --> Validate
       }
       
       note right of Timeout: Default 5s timeout<br/>Configurable per check
   ```

3. **Health Status Dashboard Design**
   ```mermaid
   graph LR
       subgraph "Service Health Matrix"
           Grid["Service | DB | API | Cache | Status<br/>--------|----|----|-------|-------<br/>Auth    | ✓  | ✓  |  ✓   | OK<br/>Orders  | ✓  | X  |  ✓   | FAIL<br/>Search  | ✓  | ✓  |  X   | DEGRADED"]
       end
       
       subgraph "Endpoints"
           E1["/health - Basic"]
           E2["/health/detailed - Full report"]
           E3["/health/ready - K8s readiness"]
           E4["/health/live - K8s liveness"]
       end
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
