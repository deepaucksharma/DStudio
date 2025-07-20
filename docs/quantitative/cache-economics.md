---
title: Cache Economics Sheet
description: "The fundamental equation for cache profitability:"
type: quantitative
difficulty: beginner
reading_time: 40 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part IV: Quantitative](/quantitative/) → **Cache Economics Sheet**

# Cache Economics Sheet

**When caching saves money**

## Cache Break-Even Formula

The fundamental equation for cache profitability:

```python
Cache is profitable when:
(Cache Cost) < (Saved Backend Cost) + (Saved Latency Cost)

Where:
Cache Cost = Memory$ + CPU$ + Network$
Saved Backend = (Hit Rate) × (Requests) × (Backend $/request)
Saved Latency = (Hit Rate) × (Requests) × (Latency Reduction) × ($/ms)
```

## Cache Sizing Economics

### Memory Cost Analysis
```bash
Redis cluster:
- 100GB memory: $500/month
- 1 billion keys: 100 bytes each
- Cost per key: $0.0000005/month

Database query:
- Cost: $0.001 per query
- Break-even: 2000 queries/key/month
- Daily requirement: 67 queries/key
```

### Hit Rate Impact
```python
Hit Rate    Backend Savings    ROI
--------    ---------------    ---
50%         50%                -20% (loss)
70%         70%                +15%
80%         80%                +45%
90%         90%                +125%
95%         95%                +200%
99%         99%                +400%
```

## Cache Pattern Economics

### Cache-Aside ROI
```python
Costs:
- 2 operations on miss (check + load)
- 1 operation on hit
- Cache infrastructure

Benefits:
- Reduced backend load
- Lower latency

Break-even hit rate: 60-70%
```

### Write-Through ROI
```python
Costs:
- Every write goes to both
- More complex code
- Consistency management

Benefits:
- Always fresh cache
- No cache misses

Break-even when read/write > 3:1
```

### Write-Back ROI
```python
Costs:
- Risk of data loss
- Complex recovery
- Eventual consistency

Benefits:
- Massive write performance
- Backend protection

Break-even when write-heavy + tolerates loss
```

## Real-World Cache Economics

### CDN Edge Caching
```bash
CloudFront pricing:
- Cache storage: $0.085/GB
- Cache hits: $0.01/10k requests
- Origin fetch: $0.02/GB + origin costs

Example site:
- 1TB cached content
- 1B requests/month
- 90% hit rate

CDN cost: $85 + $100 = $185
Origin savings: $18,000
ROI: 9,700%
```

### Application Cache Tiers
```python
L1: Local memory (free, 128MB)
    Hit rate: 30%
    Latency: 0.1ms

L2: Redis ($, 10GB)
    Hit rate: 60%
    Latency: 1ms

L3: Database
    Latency: 20ms

Effective latency:
0.3×0.1 + 0.6×1 + 0.1×20 = 2.63ms
Without cache: 20ms
Improvement: 87%
```

### Database Query Cache
```bash
Query cost breakdown:
- CPU time: $0.0001
- I/O operations: $0.0008
- Network transfer: $0.0001
Total: $0.001 per query

Cache cost:
- Redis instance: $100/month
- Max queries cached: 10M
- Cost per cached query: $0.00001

Savings: 100x when hit!
```

## Cache Invalidation Costs

### TTL-Based
```text
Pros: Simple, no coordination
Cons: Stale data window

Cost model:
Stale data incidents × Business impact
vs
Complex invalidation infrastructure

Example:
- Product prices: 5 min TTL OK
- Inventory: Real-time needed
- User profiles: 1 hour TTL OK
```

### Event-Based
```text
Infrastructure:
- Message queue: $100/month
- Invalidation service: $200/month
- Monitoring: $50/month

Break-even:
When stale data costs > $350/month

Example: E-commerce inventory
- Oversell cost: $50 per incident
- Incidents with TTL: 10/month
- Cost: $500/month > $350
- Event-based invalidation justified
```

### Tag-Based Invalidation
```python
Implementation:
- Tag index storage: O(tags × keys)
- Invalidation time: O(keys per tag)

Economics:
- Extra storage: ~20% overhead
- CPU for tagging: ~5% overhead
- Benefit: Precise invalidation

Worth it when:
- Complex dependencies
- Costly stale data
- Frequent partial updates
```

## Cache Optimization Strategies

### Adaptive TTL
```python
def calculate_ttl(key, access_pattern):
    base_ttl = 3600  # 1 hour

    # High-value keys: Longer TTL
    if is_expensive_query(key):
        ttl = base_ttl * 4

    # Frequently changing: Shorter TTL
    elif high_update_frequency(key):
        ttl = base_ttl / 4

    # Access pattern based
    elif access_pattern.is_periodic():
        ttl = access_pattern.period * 1.5

    return ttl
```

### Selective Caching
```python
def should_cache(query_cost, access_frequency, result_size):
    # Cache only if profitable
    cache_cost_per_hour = result_size * memory_cost_per_gb
    saved_per_hour = access_frequency * query_cost

    return saved_per_hour > cache_cost_per_hour * 2  # 2x margin
```

### Pre-warming Economics
```bash
Scenario: Black Friday sale
- Expected traffic: 100x normal
- Cache misses would kill database
- Pre-warming cost: 2 hours of compute

Cost analysis:
- Pre-warming: $500 (compute time)
- Without: Site down, $50K lost sales
- ROI: 100x
```

## Cache Sizing Optimization

### Working Set Analysis
```redis
Pareto principle (80/20 rule):
- 20% of keys get 80% of requests
- Focus cache on hot keys

Implementation:
1. Track access frequency
2. Cache top 20% by frequency
3. 80% hit rate with 20% memory
```

### Memory vs Hit Rate
```bash
Cache Size    Hit Rate    Cost    Benefit
----------    --------    ----    -------
1GB           60%         $10     $600
10GB          85%         $100    $850
100GB         95%         $1000   $950
1TB           99%         $10000  $990

Sweet spot: 10-100GB for most apps
```

### Multi-Level Cache Sizing
```python
def optimize_cache_sizes(budget, access_pattern):
    # L1: CPU cache (free but tiny)
    l1_size = min(cpu_cache_available, hot_working_set)

    # L2: Application memory
    l2_cost_per_gb = $5
    l2_size = optimize_for_hit_rate(
        budget * 0.3,  # 30% of budget
        l2_cost_per_gb
    )

    # L3: Redis
    l3_cost_per_gb = $50
    l3_size = optimize_for_hit_rate(
        budget * 0.7,  # 70% of budget
        l3_cost_per_gb
    )

    return (l1_size, l2_size, l3_size)
```

## Cache ROI Calculator

### Input Parameters
```python
Monthly request volume: R
Cache hit rate: H
Backend cost per request: B
Cache infrastructure cost: C
Average request latency: L
Latency cost per ms: V

ROI = ((R × H × B) + (R × H × L × V) - C) / C × 100%
```

### Example Calculation
```bash
E-commerce product catalog:
- Requests: 100M/month
- Hit rate: 90%
- Backend cost: $0.001/request
- Cache cost: $2000/month
- Latency reduction: 50ms
- Latency value: $0.00001/ms

Savings:
- Backend: 100M × 0.9 × $0.001 = $90,000
- Latency: 100M × 0.9 × 50 × $0.00001 = $45,000
- Total: $135,000

ROI: ($135,000 - $2,000) / $2,000 = 6,650%
```

## Key Decision Factors

1. **Access Pattern**
   - Random: Lower hit rates
   - Temporal locality: Higher hit rates
   - Zipfian: Cache very effective

2. **Data Volatility**
   - Static: Cache everything
   - Slowly changing: Long TTL
   - Rapidly changing: Selective caching

3. **Query Cost**
   - Expensive queries: Always cache
   - Cheap queries: Cache if frequent
   - Complex joins: Definitely cache

4. **Business Impact**
   - Revenue-critical: Over-provision
   - Internal tools: Optimize cost
   - Customer-facing: Optimize latency

## Key Takeaways

1. **80% hit rate is the sweet spot** - Below this, ROI drops quickly
2. **Cache hot data only** - Full dataset caching rarely profitable
3. **Multiple tiers multiply benefits** - L1 + L2 + L3 > L3 alone
4. **Invalidation strategy matters** - Wrong choice negates savings
5. **Measure actual hit rates** - Predictions often optimistic

Remember: Caching is not free. Calculate ROI before scaling cache infrastructure.
