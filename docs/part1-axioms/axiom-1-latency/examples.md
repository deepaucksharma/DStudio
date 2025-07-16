# Latency Examples & Failure Stories

!!! info "Prerequisites"
    - [Axiom 1: Latency Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Latency Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Failure Stories

<div class="failure-vignette">

### 🎬 The Tokyo Checkout Disaster

```yaml
Company: Major US e-commerce platform
Date: Black Friday 2019
Incident: 67% cart abandonment in Asia

Setup:
- Primary datacenter: US West Coast
- "Optimization": Route all Asian traffic to new Tokyo DC
- Problem: Inventory database remained in US

The Failure:
1. User in Tokyo adds item to cart (5ms to Tokyo DC)
2. Tokyo DC checks inventory in US (150ms RTT)
3. Add to cart requires 3 DB calls
4. Total time: 3 × 150ms = 450ms just for network
5. Plus processing: 750ms+ per cart operation
6. Mobile users on 4G: Additional 50-100ms

Impact:
- Cart operations feel sluggish
- Users assume site is broken
- 67% abandon their carts
- $12M lost revenue in 6 hours

Root Cause: 
- Assumed frontend latency was the only issue
- Didn't consider backend data locality
- Physics: Can't cache real-time inventory

Fix:
1. Regional inventory sharding
2. Predictive inventory pre-allocation
3. Eventual consistency for non-critical data
4. Result: <100ms operations globally

Lesson: Speed of light is a budget you must account for in every operation
```

</div>

<div class="failure-vignette">

### 🎬 The Satellite Internet Disaster

```yaml
Company: Rural Internet Startup
Year: 2021
Promise: "High-speed internet everywhere"

The Physics They Ignored:
- Geostationary orbit: 35,786 km altitude
- Round trip: 4 × 35,786 km = 143,144 km
- Minimum latency: 143,144 / 300,000 = 477ms
- Reality with routing: 600-800ms

What Happened:
1. Deployed in rural schools for "modern education"
2. Video calls impossible (need <150ms)
3. Interactive websites frustrating
4. Cloud-based tools unusable
5. Students couldn't participate in online learning

Specific Failures:
- Google Docs: Each keystroke = round trip = 600ms
- Zoom: Audio delay made conversation impossible
- Online tests: Timed-out due to latency
- Gaming: Completely unplayable

Financial Impact:
- $50M in cancelled contracts
- Class action lawsuit
- Company pivoted to IoT/sensors only

Lesson: Some use cases have hard latency requirements that physics won't allow
```

</div>

<div class="failure-vignette">

### 🎬 The Cross-Region Database Sync Nightmare

```yaml
Company: Global Social Media Platform
Incident: "The Great Timeline Corruption"
Date: March 2022

Architecture:
- Users globally distributed
- 5 regional databases
- "Strong consistency" requirement
- Synchronous replication

The Cascading Failure:
1. User posts in Sydney
2. Must replicate to all regions before confirming
3. Latencies:
   - Sydney → Singapore: 90ms
   - Sydney → Frankfurt: 280ms
   - Sydney → Virginia: 200ms
   - Sydney → São Paulo: 320ms
4. Total write time: 320ms + processing
5. Under load: 500ms-2s per post

User Impact:
- "Post" button seems broken
- Multiple clicks = duplicate posts
- Angry users = more posts about outage
- Viral complaint storm

The Meltdown:
- Queue depth increases
- Latency spirals up
- Timeouts trigger retries
- Retry storm amplifies load
- Complete system collapse

Fix Attempted:
- Increased timeouts (made it worse)
- Added more servers (didn't help)
- Tried caching (can't cache writes)

Real Fix:
- Eventual consistency
- Regional primary architecture
- Async replication
- Local write confirmation

Cost:
- 14 hours downtime
- $180M market cap loss
- 3% user churn
- CTO resigned

Lesson: Synchronous global operations violate physics
```

</div>

## Latency in Different Contexts

### Web Applications

#### The 100ms Budget Breakdown
```
User clicks (0ms)
├─ Browser processing (5ms)
├─ DNS lookup (20ms cached, 50ms+ cold)
├─ TCP handshake (1 RTT)
├─ TLS negotiation (1-2 RTT)
├─ HTTP request (1 RTT)
├─ Server processing (X ms)
├─ HTTP response (1 RTT)
└─ Browser rendering (10-50ms)

Total RTTs: 4-5 minimum
At 30ms RTT: 120-150ms gone before your code runs!
```

### Video Streaming

#### Why Netflix Works
```
Traditional: User → Server → Video
Latency: 100ms+ per chunk = buffering

Netflix: User → Nearest Edge → Cached Video
Latency: <10ms per chunk = smooth playback

Edge Locations: 200+ globally
Cache Hit Rate: >95%
Result: Start playing in <2 seconds globally
```

### Financial Trading

#### The Million-Dollar Millisecond
```
Chicago → New York: 
- Standard internet: 16ms
- Dedicated fiber: 13ms  
- Microwave relay: 8.5ms
- Theoretical minimum: 7.9ms

Cost of 4.5ms advantage:
- Infrastructure: $300M
- Annual profit: $100M+
- ROI: 3 years
```

### Gaming

#### Why Geolocation Matters
```
Acceptable Latency by Game Type:
- Turn-based: <1000ms
- RTS: <200ms
- MOBA: <100ms
- FPS: <50ms
- Fighting: <16ms (1 frame at 60fps)

Solution: Regional game servers
- US East, US West
- Europe, Asia, etc.
- Match players by region
```

## Common Patterns & Solutions

### Pattern 1: Cache Hierarchy
```
Browser Cache (0ms)
    ↓ miss
CDN Edge (5ms)
    ↓ miss
Regional Cache (20ms)
    ↓ miss
Origin (100ms+)
```

### Pattern 2: Predictive Prefetching
```python
# Example: Prefetch next likely page
def prefetch_next_page(current_page, user_history):
    predictions = ml_model.predict_next(current_page, user_history)
    for page, probability in predictions:
        if probability > 0.7:
            cache.preload(page)  # Load before user asks
```

### Pattern 3: Regional Affinity
```yaml
User Location: Tokyo
Preferred Region: asia-northeast1
Fallback Regions: 
  1. asia-southeast1 (+20ms)
  2. us-west1 (+100ms)
  3. us-east1 (+150ms)
```

### Pattern 4: Batching to Amortize Latency
```python
# Bad: Individual requests
for item in items:
    result = api.process(item)  # 50ms each
# Total: 50ms * 100 items = 5 seconds

# Good: Batch request
results = api.process_batch(items)  # 100ms total
# Total: 100ms (50x faster!)
```

## Latency Comparison Table

| Operation | Latency | Analogy |
|-----------|---------|---------|
| L1 cache | 0.5 ns | 0.5 seconds |
| L2 cache | 7 ns | 7 seconds |
| RAM access | 100 ns | 1.7 minutes |
| SSD read | 150 μs | 2.5 days |
| HDD seek | 10 ms | 3.8 months |
| CA → Netherlands | 150 ms | 4.8 years |
| TCP packet retry | 3 s | 95 years |

## Interactive Examples

### Calculate Your Latency Budget

```javascript
// Latency Budget Calculator
function calculateBudget(userExpectation, operations) {
    let budget = userExpectation;
    let spent = 0;
    
    operations.forEach(op => {
        spent += op.latency;
        console.log(`${op.name}: ${op.latency}ms (${budget - spent}ms remaining)`);
    });
    
    if (spent > budget) {
        console.error(`OVER BUDGET by ${spent - budget}ms!`);
    }
    return budget - spent;
}

// Example: E-commerce checkout
const operations = [
    { name: "Load page", latency: 50 },
    { name: "Validate cart", latency: 30 },
    { name: "Check inventory", latency: 100 },
    { name: "Process payment", latency: 200 },
    { name: "Send confirmation", latency: 50 }
];

calculateBudget(1000, operations); // 1 second budget
```

### Real RTT Measurements

```bash
# Measure actual RTT to popular services
for host in google.com amazon.com facebook.com; do
    echo "=== $host ==="
    ping -c 5 $host | grep "min/avg/max"
done

# Trace the path
traceroute -n google.com

# Application-level latency
time curl -o /dev/null -s -w "Total time: %{time_total}s\n" https://example.com
```

## Key Insights from Failures

!!! danger "Repeated Patterns"
    
    1. **Ignoring Physics**: Assuming engineering can overcome light speed
    2. **Hidden Round Trips**: Each operation may require multiple network calls
    3. **Synchronous Global Ops**: Forcing worldwide consistency
    4. **Cascade Effects**: Latency causing timeouts causing retries
    5. **User Psychology**: Perception matters more than reality

## Mitigation Strategies

### 1. Design for Physics
- Know your distances
- Calculate minimum possible latency
- Design within those constraints

### 2. Minimize Round Trips
- Batch operations
- Pipeline requests
- Use HTTP/2 multiplexing

### 3. Strategic Caching
- Cache at every level
- Use appropriate TTLs
- Consider staleness tolerance

### 4. Async When Possible
- Return immediately
- Process in background
- Notify when complete

### 5. Regional Architecture
- Deploy close to users
- Shard by geography
- Accept eventual consistency

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Latency Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 2: Finite Capacity](../axiom-2-capacity/index.md) →
    
    **Tools**: [Latency Budget Calculator](../../tools/latency-calculator.md)