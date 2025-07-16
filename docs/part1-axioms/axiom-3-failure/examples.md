# Partial Failure Examples & Stories

!!! info "Prerequisites"
    - [Axiom 3: Partial Failure Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Failure Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Failure Stories

<div class="failure-vignette">

### 🎬 The Retry Storm of 2022

```yaml
Setting: Social media platform, 100M daily active users
Initial trigger: One DB replica 20% slower (bad disk)

Timeline:
T+0s:   App servers detect slow responses
T+1s:   Client timeout at 1 second, retry triggered
T+2s:   2x load on all replicas due to retries
T+3s:   Healthy replicas now slow due to 2x load
T+4s:   More timeouts, more retries (4x original)
T+10s:  Exponential retry storm: 32x load
T+30s:  All replicas saturated
T+60s:  Full outage

Root cause: Treated partial failure as total failure

Fix: 
- Circuit breakers with failure threshold
- Bulkheads to isolate bad replicas
- Adaptive timeouts based on recent latency
- Exponential backoff with jitter
```

</div>

<div class="failure-vignette">

### 🎬 The Split-Brain Election Disaster

```yaml
Company: Financial Trading Platform
Date: Market open, Monday morning
System: Primary/Secondary database with auto-failover

The Partial Failure:
08:29:00: Network partition between primary and secondary
08:29:05: Secondary can't reach primary
08:29:10: Secondary promotes itself to primary
08:29:11: Original primary still accepting writes
08:29:12: TWO PRIMARIES ACTIVE (split-brain)

08:30:00: Market opens
08:30:01: Trade A written to Primary-1: Buy 1000 AAPL
08:30:01: Trade B written to Primary-2: Sell 1000 AAPL
08:30:02: Account shows different balances on different nodes

08:35:00: Network partition heals
08:35:01: Conflict detected
08:35:02: Automatic resolution fails
08:35:03: MANUAL INTERVENTION REQUIRED

Damage:
- $12M in disputed trades
- 4 hour market halt for reconciliation
- SEC investigation
- CTO resignation

Fix:
- Quorum-based consensus (3+ nodes)
- Generation numbers for split-brain detection
- Manual approval for split-brain recovery
- Stonith (Shoot The Other Node In The Head)
```

</div>

<div class="failure-vignette">

### 🎬 The Cascading Timeout Failure

```yaml
Architecture: Microservices (A → B → C → Database)
Normal operation: 50ms total latency

The Setup:
- Service A: 1s timeout to B
- Service B: 2s timeout to C  
- Service C: 3s timeout to DB
- Database: Slow query taking 4s

What happened:
1. Database query slow (4s)
2. Service C waits full 3s, then fails
3. Service B retries 3 times: 3 × 3s = 9s
4. Service A times out after 1s
5. User retries request
6. Now 2x load on already slow database
7. Database gets slower (8s queries)
8. More timeouts, more retries
9. Complete system meltdown

The irony: 
- A gives up after 1s
- B keeps trying for 9s
- Resources wasted on doomed requests

Fix:
- Hierarchical timeouts: A(3s) > B(1s) > C(300ms)
- Deadline propagation
- Circuit breakers at each level
- Request hedging instead of retry
```

</div>

## Types of Partial Failures in Detail

### 1. Slow Failures (Performance Degradation)

#### The CDN Brown-Out

```yaml
Scenario: Major news website during breaking news
CDN behavior:
- Normal: 10ms response time
- During event: 500ms response time
- Still "working" but 50x slower

Impact cascade:
1. Page load time: 200ms → 10s
2. Users hit refresh repeatedly
3. 10x more requests
4. CDN gets even slower
5. Origin servers get hit directly
6. Complete outage

Lesson: Slow can be worse than down
```

### 2. Gray Failures (Observability Gaps)

#### The Invisible Database Corruption

```python
# Health check says: HEALTHY
def health_check():
    return db.execute("SELECT 1").success

# But reality:
# - 10% of queries return wrong data
# - Specific table corrupted
# - Affects only user queries, not health checks

# Results:
# - Monitoring: ✅ All green
# - Users: "My balance is wrong!"
# - Support: "System shows healthy"
# - Duration: 3 days undetected
```

### 3. Asymmetric Failures (One-Way Communication)

#### The Firewall Rule Mishap

```
Normal state:
Service A ←→ Service B (bidirectional)

After firewall change:
Service A → Service B ✓ (works)
Service A ← Service B ✗ (blocked)

Symptoms:
- A sends requests to B successfully
- B processes requests
- B can't send responses back
- A times out waiting
- A marks B as "down"
- But B is actually healthy!

Debug nightmare:
- B logs show requests processed
- A logs show timeouts
- Network team says "routing works"
- Took 6 hours to find asymmetric rule
```

### 4. Byzantine Failures (Incorrect Behavior)

#### The Bit-Flip Cache Disaster

```yaml
Component: Distributed cache cluster
Failure: Memory corruption from cosmic ray

Normal behavior:
GET user:123 → {"name": "Alice", "balance": 1000}

Byzantine behavior:
GET user:123 → {"name": "Alice", "balance": 1000000}

The twist:
- Cache returns data successfully
- No errors in logs
- Checksums not used (performance reasons)
- Data looks plausible

Discovered when:
- User withdrew $999,000
- Audit found impossible balance
- Cache refresh fixed it
- But damage was done
```

## Partial Failure Patterns & Solutions

### Pattern 1: Circuit Breaker Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                
            raise e

# Usage
db_breaker = CircuitBreaker()

def get_user(user_id):
    return db_breaker.call(db.query, f"SELECT * FROM users WHERE id={user_id}")
```

### Pattern 2: Bulkhead Isolation

```java
// Thread pool isolation
public class BulkheadService {
    private final ExecutorService dbPool = 
        Executors.newFixedThreadPool(10);  // DB bulkhead
    
    private final ExecutorService apiPool = 
        Executors.newFixedThreadPool(50);  // API bulkhead
    
    private final ExecutorService cachePool = 
        Executors.newFixedThreadPool(20);  // Cache bulkhead
    
    public CompletableFuture<User> getUser(String id) {
        // If DB is slow, only 10 threads affected
        return CompletableFuture.supplyAsync(() -> {
            return database.query(id);
        }, dbPool);
    }
    
    public CompletableFuture<Data> callAPI(Request req) {
        // API issues don't affect DB queries
        return CompletableFuture.supplyAsync(() -> {
            return api.call(req);
        }, apiPool);
    }
}
```

### Pattern 3: Adaptive Timeout

```go
type AdaptiveTimeout struct {
    baseTimeout    time.Duration
    recentLatencies []time.Duration
    mu             sync.Mutex
}

func (at *AdaptiveTimeout) Calculate() time.Duration {
    at.mu.Lock()
    defer at.mu.Unlock()
    
    if len(at.recentLatencies) < 10 {
        return at.baseTimeout
    }
    
    // Calculate P95 of recent latencies
    sorted := make([]time.Duration, len(at.recentLatencies))
    copy(sorted, at.recentLatencies)
    sort.Slice(sorted, func(i, j int) bool {
        return sorted[i] < sorted[j]
    })
    
    p95Index := int(float64(len(sorted)) * 0.95)
    p95Latency := sorted[p95Index]
    
    // Timeout = 2 * P95 latency
    return p95Latency * 2
}

func (at *AdaptiveTimeout) Record(latency time.Duration) {
    at.mu.Lock()
    defer at.mu.Unlock()
    
    at.recentLatencies = append(at.recentLatencies, latency)
    if len(at.recentLatencies) > 100 {
        at.recentLatencies = at.recentLatencies[1:]
    }
}
```

### Pattern 4: Request Hedging

```python
async def hedged_request(primary, secondary, delay=0.05):
    """
    Send request to primary, and if no response
    within delay, send to secondary too
    """
    async def primary_request():
        return await primary.request()
    
    async def secondary_request():
        await asyncio.sleep(delay)
        return await secondary.request()
    
    # Race both requests
    tasks = [
        asyncio.create_task(primary_request()),
        asyncio.create_task(secondary_request())
    ]
    
    # Return first successful response
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # Cancel pending request
    for task in pending:
        task.cancel()
    
    return done.pop().result()
```

## Debugging Partial Failures

### The Partial Failure Checklist

```yaml
Detection:
□ Check error rates by endpoint
□ Compare latency percentiles (P50 vs P99)
□ Look for bimodal distributions
□ Check specific error messages
□ Monitor queue depths
□ Watch for timeout patterns

Diagnosis:
□ Correlate with deploys/changes
□ Check for resource exhaustion
□ Look for network partitions
□ Verify timeout configurations
□ Check for thundering herds
□ Look for dependency failures

Response:
□ Activate circuit breakers
□ Increase timeouts temporarily
□ Shed non-critical load
□ Scale affected components
□ Isolate failing instances
□ Prepare rollback
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Slow is the new down** - Performance degradation cascades
    2. **Retries amplify** - Good intentions make things worse
    3. **Timeouts must align** - Parent > child always
    4. **Partial states spread** - One slow node infects others
    5. **Monitors lie** - Health checks miss gray failures

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Failure Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 4: Concurrency](../axiom-4-concurrency/index.md) →
    
    **Tools**: [Chaos Engineering Toolkit](../../tools/chaos-toolkit.md)