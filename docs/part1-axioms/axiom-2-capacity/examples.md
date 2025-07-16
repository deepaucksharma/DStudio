# Capacity Examples & Failure Stories

!!! info "Prerequisites"
    - [Axiom 2: Capacity Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Capacity Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Failure Stories

<div class="failure-vignette">

### 🎬 Black Friday Database Meltdown

```yaml
Company: Major retailer, $2B revenue
Date: Black Friday 2021, 6:00 AM EST

Sequence:
  06:00: Marketing sends "50% off everything" email
  06:01: 2M users click simultaneously  
  06:02: API servers scale from 100 to 1000 pods
  06:03: Each pod opens 10 connections to DB
  06:04: Database connection limit: 5000
  06:05: 10,000 connections attempted
  06:06: Database rejects new connections
  06:07: Health checks fail, cascading restarts
  06:15: Site completely down
  08:00: Manual intervention restores service
  
Loss: $50M in sales, brand damage

Root Cause: Scaled compute, forgot DB connections are finite

Fix: 
- Connection pooling
- Admission control
- Backpressure mechanisms
- Database proxy layer
```

</div>

<div class="failure-vignette">

### 🎬 Uber's Surge Pricing Algorithm (2018)

```yaml
Setting: New Year's Eve, Times Square
Problem: Driver utilization approaching 100%

Timeline:
Normal operations:
  - 70% driver utilization
  - 2 min average wait time
  - Happy customers

10 PM (rush begins):
  - 85% utilization
  - 5 min wait time
  - Some complaints

11 PM (approaching midnight):
  - 95% utilization
  - 20 min wait time
  - Mass cancellations

11:45 PM (system breaks):
  - 99% utilization
  - Infinite wait (no available drivers)
  - App shows "No cars available"

Midnight (complete failure):
  - Angry customers stranded
  - Viral social media backlash
  - Competitors gain market share

Solution: Dynamic surge pricing
- Reduces demand (λ)
- Increases supply (more drivers)
- Maintains 85% utilization max
```

</div>

<div class="failure-vignette">

### 🎬 The Kubernetes etcd Meltdown

```yaml
Company: Cloud Native Startup
Year: 2023
Setup: Single Kubernetes cluster for everything

Growth timeline:
Month 1: 
  - 10 nodes, 100 pods
  - etcd latency: 5ms
  - All good

Month 6:
  - 100 nodes, 2000 pods
  - etcd latency: 50ms
  - Occasional timeouts

Month 12:
  - 1000 nodes, 30000 pods
  - etcd latency: 500ms
  - Frequent leader elections

The breaking point:
  - 2000 nodes attempted
  - etcd write timeout
  - Consensus breaks down
  - Entire cluster unresponsive
  - 6 hour outage

Root cause analysis:
- etcd has finite write throughput
- Every node heartbeat = etcd write
- 2000 nodes × heartbeat/sec > etcd capacity

Fix:
- Multiple smaller clusters
- Federated architecture
- etcd performance tuning
- Reduce heartbeat frequency

Lesson: Even distributed systems have centralized bottlenecks
```

</div>

## Capacity in Different Contexts

### Database Connection Pools

#### The Hidden Multiplier Effect

```
Microservices: 50 services
Instances per service: 10
Connections per instance: 10
Total connections: 50 × 10 × 10 = 5000

PostgreSQL max_connections: 100 (default)
Result: EXPLOSION 💥
```

#### Real Connection Limits by Database

| Database | Default Limit | Practical Max | Notes |
|----------|---------------|---------------|-------|
| PostgreSQL | 100 | 5000 | Each connection uses memory |
| MySQL | 151 | 10000 | Threads get expensive |
| Oracle | 150 | 2000 | License costs! |
| MongoDB | 64000 | 5000 | File descriptor limits |
| Redis | 10000 | 100000 | Single-threaded anyway |

### Memory: The Silent Killer

#### JVM Heap Death Spiral

```java
// The innocent-looking code
List<User> users = new ArrayList<>();
while (hasMoreUsers()) {
    users.add(loadNextUser());  // Memory leak!
}

// What happens:
// Heap: 50% → 70% → 85% → GC Storm → OOM
```

#### Memory Capacity Planning

| Component | Warning Signs | Action Required |
|-----------|---------------|-----------------|
| Heap usage > 85% | Frequent GC | Increase heap or fix leak |
| Page cache < 20% | High disk I/O | Add RAM |
| Swap usage > 0 | Performance degradation | Add RAM immediately |
| OOM kills | Container restarts | Set proper limits |

### Network Bandwidth Saturation

#### The Video Streaming Surprise

```yaml
Scenario: Internal all-hands meeting
Platform: Self-hosted video

Calculation failure:
- 1000 employees
- 1080p stream = 5 Mbps
- Total bandwidth: 5 Gbps
- Office connection: 1 Gbps
- Result: Nobody can watch

Quick fix: 
- Drop to 480p (1 Mbps)
- Still saturated
- Emergency YouTube stream

Long-term fix:
- CDN for internal video
- Multicast for live events
- Bandwidth reservation
```

### Thread Pool Exhaustion

#### The Slow Dependency Cascade

```python
# Thread pool size: 200
# Normal operation: 50 threads busy

# One slow dependency:
def handle_request():
    user = fetch_user()  # 50ms
    orders = fetch_orders()  # 50ms  
    shipping = fetch_shipping()  # 10 seconds! (slow)
    return combine(user, orders, shipping)

# Result:
# Threads waiting on shipping: 200
# New requests: Rejected
# Health checks: Timeout
# Container: Restarted
```

## Common Patterns & Solutions

### Pattern 1: Backpressure

```java
// Bad: Unbounded queue
Queue<Request> queue = new LinkedList<>();

// Good: Bounded queue with backpressure
BlockingQueue<Request> queue = 
    new ArrayBlockingQueue<>(1000);

// Better: Backpressure with feedback
if (!queue.offer(request, 100, MILLISECONDS)) {
    return Response.status(503)
        .header("Retry-After", "5")
        .build();
}
```

### Pattern 2: Circuit Breakers

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=0.5, 
                 timeout=60, min_calls=100):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.min_calls = min_calls
        self.state = "CLOSED"
        
    def call(self, func, *args):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError()
                
        try:
            result = func(*args)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
```

### Pattern 3: Adaptive Concurrency

```go
// Adjust concurrency based on response times
type AdaptiveLimiter struct {
    current    int32
    min        int32
    max        int32
    targetRT   time.Duration
}

func (a *AdaptiveLimiter) Acquire(ctx context.Context) error {
    for {
        current := atomic.LoadInt32(&a.current)
        if current >= a.max {
            return ErrCapacityExceeded
        }
        if atomic.CompareAndSwapInt32(&a.current, 
                                      current, current+1) {
            return nil
        }
    }
}

func (a *AdaptiveLimiter) Release(responseTime time.Duration) {
    atomic.AddInt32(&a.current, -1)
    
    // Adjust limits based on response time
    if responseTime > a.targetRT*2 {
        // System overloaded, reduce max
        atomic.AddInt32(&a.max, -1)
    } else if responseTime < a.targetRT/2 {
        // System underutilized, increase max
        atomic.AddInt32(&a.max, 1)
    }
}
```

## Capacity Anti-Patterns

### ❌ The "Infinite Scale" Fallacy

```yaml
Myth: "Just add more servers"
Reality:
  - Database connections: FINITE
  - Network bandwidth: FINITE  
  - Coordination overhead: INCREASES
  - Debugging complexity: EXPONENTIAL
```

### ❌ The "It Works on My Machine" Capacity

```yaml
Development:
  - 1 user
  - 10 requests/minute
  - SQLite database
  - Unlimited time

Production:
  - 1M users
  - 100K requests/second
  - Distributed database
  - 100ms SLA
```

### ❌ Ignoring Coordinated Omission

```python
# Wrong: Measures only successful requests
start = time.time()
make_request()
latency = time.time() - start

# Right: Includes failed/dropped requests
intended_start = time.time()
try:
    make_request()
except Timeout:
    pass  # Still counts!
actual_latency = time.time() - intended_start
```

## Measuring Real Capacity

### Load Testing That Actually Works

```bash
# Step 1: Find baseline
./load-test.sh --users 1 --duration 60s

# Step 2: Find the knee
for users in 10 50 100 200 500 1000; do
    ./load-test.sh --users $users --duration 300s
    # Watch for response time spike
done

# Step 3: Find the cliff  
./load-test.sh --users 2000 --duration 300s
# Watch it burn 🔥

# Step 4: Set limits at 70% of cliff
```

### Capacity Monitoring

```yaml
Key Metrics:
  - Utilization (< 70% good)
  - Saturation (queue depth)
  - Errors (rejection rate)
  - Latency percentiles (P99)

RED Method:
  - Rate: requests/second
  - Errors: failure rate
  - Duration: response time

USE Method:
  - Utilization: % busy
  - Saturation: queue length
  - Errors: error count
```

## Key Insights from Failures

!!! danger "Repeated Patterns"
    
    1. **Hidden multipliers**: Microservices multiply everything
    2. **Central bottlenecks**: Even distributed systems have them
    3. **The cliff is sudden**: 90% → 100% happens fast
    4. **Cascading failures**: One limit triggers others
    5. **Capacity != Performance**: Slow systems hit limits faster

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Capacity Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 3: Partial Failure](../axiom-3-failure/index.md) →
    
    **Tools**: [Capacity Planning Calculator](../../tools/capacity-planner.md)