# Work Distribution Examples & Case Studies

!!! info "Prerequisites"
    - [Distribution of Work Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Work Distribution Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Pillars Overview](../index.md)

## Real-World Work Distribution Failures

<div class="failure-vignette">

### 🎬 The Reddit "Hug of Death" Pattern

```yaml
Company: Popular startup featured on Reddit
Date: Multiple incidents 2018-2023
Pattern: Sudden 1000× traffic spike

What happens:
1. Reddit post goes viral
2. Traffic spike: 100 req/s → 100,000 req/s
3. Autoscaling triggers (5-10 min delay)
4. But database connection pool exhausted
5. App servers spinning up but can't connect
6. Health checks fail → instances terminated
7. Death spiral begins

The cascade:
Minute 0: Post hits front page
Minute 1: Response times increase 10×
Minute 2: Connection pool exhausted
Minute 3: New instances fail health checks
Minute 4: Existing instances marked unhealthy
Minute 5: Complete outage

Fix implemented:
- Circuit breaker at app level
- Read replica pool with overflow
- Cache warming on instance start
- Gradual health check ramp-up
- Pre-scaled "surge capacity" pool

Result: Survived next Reddit hug
Cost: 3× infrastructure for 1% of time
```

</div>

<div class="failure-vignette">

### 🎬 The Distributed Monolith Anti-Pattern

```yaml
Company: Enterprise moving to microservices
Year: 2020
Services: 47 "micro" services

Architecture smell:
- Every request touches 15+ services
- Synchronous calls everywhere
- No service can work independently
- 99.9% × 15 = 98.5% availability

Real incident:
- User service adds 50ms latency
- Payment service timeout: 45ms
- Payment starts failing
- Order service depends on payment
- Cascade failure across system

Performance analysis:
- Simple request: 47 network hops
- Total latency: 2.3 seconds
- Theoretical minimum: 200ms

Refactoring approach:
1. Identify true service boundaries
2. Merge chatty services
3. Async where possible
4. Local caching for read data
5. Bulk operations

Result: 47 services → 8 services
Latency: 2.3s → 180ms
Availability: 98.5% → 99.95%
```

</div>

<div class="failure-vignette">

### 🎬 The Work-Stealing Success Story

```yaml
Company: Video processing platform
Challenge: Unpredictable job sizes (1MB-10GB videos)

Original design:
- Round-robin job distribution
- Problem: 1 large job blocks worker
- Other workers idle
- Processing time unpredictable

Work-stealing implementation:
class VideoProcessor:
    def __init__(self):
        self.local_queues = [deque() for _ in workers]
        self.steal_threshold = 2
        
    def process(self, worker_id):
        queue = self.local_queues[worker_id]
        
        while True:
            # Try local queue
            if queue:
                job = queue.popleft()
                process_video(job)
            else:
                # Try stealing
                victim = find_busiest_queue()
                if len(victim) > self.steal_threshold:
                    stolen = victim.pop()  # Steal from back
                    queue.append(stolen)
                else:
                    wait()

Results:
- Worker utilization: 45% → 89%
- P99 processing time: 45min → 12min
- Predictable completion times
- No head-of-line blocking
```

</div>

## Work Distribution Patterns in Practice

### 1. The Consistent Hashing Implementation

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, virtual_nodes=150):
        self.nodes = nodes or []
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _build_ring(self):
        self.ring = {}
        self.sorted_keys = []
        
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node
                self.sorted_keys.append(hash_value)
        
        self.sorted_keys.sort()
    
    def get_node(self, key):
        if not self.ring:
            return None
            
        hash_value = self._hash(key)
        
        # Find first node clockwise from hash
        index = bisect.bisect_right(self.sorted_keys, hash_value)
        if index == len(self.sorted_keys):
            index = 0
            
        return self.ring[self.sorted_keys[index]]
    
    def add_node(self, node):
        self.nodes.append(node)
        self._build_ring()
    
    def remove_node(self, node):
        self.nodes.remove(node)
        self._build_ring()

# Usage example
hash_ring = ConsistentHash(['server1', 'server2', 'server3'])

# Distribute work
for user_id in range(1000):
    node = hash_ring.get_node(f"user_{user_id}")
    print(f"User {user_id} → {node}")

# Add new node (minimal redistribution)
hash_ring.add_node('server4')
```

### 2. The Circuit Breaker Pattern

```python
import time
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold=5, 
                 recovery_timeout=60,
                 expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = Lock()
    
    def call(self, func, *args, **kwargs):
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self):
        return (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.recovery_timeout)
    
    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

def call_flaky_service():
    # Simulated flaky service
    if random.random() < 0.3:
        raise Exception("Service unavailable")
    return "Success"

# Protected call
try:
    result = breaker.call(call_flaky_service)
except Exception as e:
    # Handle gracefully - maybe return cached data
    result = get_cached_response()
```

### 3. Adaptive Load Balancing

```python
import statistics
import time
from collections import deque
from threading import Lock

class AdaptiveLoadBalancer:
    def __init__(self, backends):
        self.backends = {}
        for backend in backends:
            self.backends[backend] = {
                'response_times': deque(maxlen=100),
                'error_count': 0,
                'last_error': None,
                'score': 1.0
            }
        self._lock = Lock()
    
    def select_backend(self):
        with self._lock:
            # Calculate scores based on performance
            scores = {}
            for backend, stats in self.backends.items():
                # Skip recently failed backends
                if (stats['last_error'] and 
                    time.time() - stats['last_error'] < 30):
                    continue
                
                # Calculate score
                if stats['response_times']:
                    avg_response = statistics.mean(stats['response_times'])
                    p95_response = statistics.quantiles(
                        stats['response_times'], n=20
                    )[-1] if len(stats['response_times']) > 5 else avg_response
                    
                    # Lower response time = higher score
                    base_score = 1.0 / (1.0 + p95_response)
                    
                    # Penalize errors
                    error_penalty = stats['error_count'] * 0.1
                    scores[backend] = max(0.1, base_score - error_penalty)
                else:
                    # New backend gets average score
                    scores[backend] = 0.5
            
            if not scores:
                raise Exception("No healthy backends")
            
            # Weighted random selection
            total_score = sum(scores.values())
            rand = random.uniform(0, total_score)
            
            cumulative = 0
            for backend, score in scores.items():
                cumulative += score
                if rand <= cumulative:
                    return backend
            
            return list(scores.keys())[0]
    
    def record_response(self, backend, response_time, success=True):
        with self._lock:
            stats = self.backends[backend]
            
            if success:
                stats['response_times'].append(response_time)
                stats['error_count'] = max(0, stats['error_count'] - 1)
            else:
                stats['error_count'] += 1
                stats['last_error'] = time.time()

# Usage
balancer = AdaptiveLoadBalancer(['api1', 'api2', 'api3'])

def make_request():
    backend = balancer.select_backend()
    start = time.time()
    
    try:
        response = requests.get(f"http://{backend}/api")
        response_time = time.time() - start
        balancer.record_response(backend, response_time, success=True)
        return response
    except Exception as e:
        response_time = time.time() - start
        balancer.record_response(backend, response_time, success=False)
        raise
```

## Work Distribution at Scale

### Netflix's Request Routing

```yaml
Scale: 200M+ subscribers, 1M+ requests/second

Architecture:
1. Edge Layer (Zuul)
   - Geographic routing
   - Device-specific routing
   - A/B test routing
   
2. Mid-tier Services
   - Service mesh (internal)
   - Circuit breakers everywhere
   - Adaptive concurrency limits
   
3. Data Layer
   - Sharded by user ID
   - Read replicas per region
   - Caching at every level

Key innovations:
- Predictive scaling based on viewing patterns
- Chaos engineering to test distribution
- Fallback to cached/degraded responses
```

### Uber's Dispatch System

```yaml
Challenge: Match riders with drivers optimally

Work distribution approach:
1. Geographic Sharding
   - City divided into hexagonal cells
   - Each cell has dedicated workers
   - Adjacent cells share state
   
2. Dynamic Rebalancing
   - High-demand areas get more workers
   - Predictive allocation for events
   - Real-time load balancing

3. Work Stealing
   - Idle cells help busy neighbors
   - Prevents local hotspots
   - Maintains response time SLAs

Results:
- 95% matches in <15 seconds
- Even distribution of driver utilization
- Handles 10× surge during events
```

## Anti-Pattern Gallery

### 1. The Retry Storm

```python
# WRONG: Exponential retry storm
def bad_retry():
    for i in range(10):
        try:
            return make_request()
        except:
            time.sleep(0.1 * (2 ** i))  # 0.1, 0.2, 0.4... 102.4s!

# RIGHT: Capped exponential backoff with jitter
def good_retry():
    max_retries = 5
    base_delay = 0.1
    max_delay = 5.0
    
    for i in range(max_retries):
        try:
            return make_request()
        except Exception as e:
            if i == max_retries - 1:
                raise
            
            delay = min(base_delay * (2 ** i), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            time.sleep(delay + jitter)
```

### 2. The Coordinated Omission

```python
# WRONG: Measures only successful requests
response_times = []
for _ in range(1000):
    start = time.time()
    try:
        make_request()
        response_times.append(time.time() - start)
    except:
        pass  # Ignores failed requests!

print(f"Average: {statistics.mean(response_times)}")  # Misleading!

# RIGHT: Include timeouts in metrics
response_times = []
timeout_count = 0

for _ in range(1000):
    start = time.time()
    try:
        make_request()
        response_times.append(time.time() - start)
    except TimeoutError:
        response_times.append(TIMEOUT_VALUE)  # Include in stats
        timeout_count += 1
    except:
        pass  # Other errors

print(f"P50: {statistics.median(response_times)}")
print(f"P99: {statistics.quantiles(response_times, n=100)[98]}")
print(f"Timeout rate: {timeout_count/1000:.1%}")
```

## Key Insights

!!! danger "Common Patterns in Failures"
    
    1. **Cascade failures from synchronous calls** - One slow service kills all
    2. **Retry storms amplify problems** - Bad retries make outages worse
    3. **Uneven distribution from poor hashing** - Hot shards are inevitable
    4. **Coordination overhead exceeds benefits** - Perfect balance too expensive
    5. **Missing back-pressure causes collapse** - Systems need escape valves

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Work Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of State](../pillar-2-state/index.md) →
    
    **Related**: [Capacity Management](../../part1-axioms/axiom-2-capacity/index.md)