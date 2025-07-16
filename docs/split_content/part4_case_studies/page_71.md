Page 71: Cache Economics Sheet
When caching saves money
CACHE BREAK-EVEN FORMULA
Cache is profitable when:
(Cache Cost) < (Saved Backend Cost) + (Saved Latency Cost)

Where:
Cache Cost = Memory$ + CPU$ + Network$
Saved Backend = (Hit Rate) × (Requests) × (Backend $/request)
Saved Latency = (Hit Rate) × (Requests) × (Latency Reduction) × ($/ms)
CACHE SIZING ECONOMICS
Memory Cost Analysis
Redis cluster:
- 100GB memory: $500/month
- 1 billion keys: 100 bytes each
- Cost per key: $0.0000005/month

Database query:
- Cost: $0.001 per query
- Break-even: 2000 queries/key/month
- Daily requirement: 67 queries/key
Hit Rate Impact
Hit Rate    Backend Savings    ROI
--------    ---------------    ---
50%         50%                -20% (loss)
70%         70%                +15%
80%         80%                +45%
90%         90%                +125%
95%         95%                +200%
99%         99%                +400%
CACHE PATTERN ECONOMICS
Cache-Aside ROI
Costs:
- 2 operations on miss (check + load)
- 1 operation on hit
- Cache infrastructure

Benefits:
- Reduced backend load
- Lower latency

Break-even hit rate: 60-70%
Write-Through ROI
Costs:
- Every write goes to both
- More complex code
- Consistency management

Benefits:
- Always fresh cache
- No cache misses

Break-even when read/write > 3:1
REAL-WORLD CACHE ECONOMICS
CDN Edge Caching
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
Application Cache Tiers
L1: Local memory (free, 128MB)
    Hit rate: 30%
    Latency: 0.1ms

L2: Redis ($$, 10GB)
    Hit rate: 60%
    Latency: 1ms

L3: Database
    Latency: 20ms

Effective latency:
0.3×0.1 + 0.6×1 + 0.1×20 = 2.63ms
Without cache: 20ms
Improvement: 87%
CACHE INVALIDATION COSTS
TTL-Based
Pros: Simple, no coordination
Cons: Stale data window

Cost model:
Stale data incidents × Business impact
vs
Complex invalidation infrastructure
Event-Based
Infrastructure:
- Message queue: $100/month
- Invalidation service: $200/month
- Monitoring: $50/month

Break-even:
When stale data costs > $350/month
CACHE OPTIMIZATION STRATEGIES
Adaptive TTL
High-value keys: Longer TTL
Frequently changing: Shorter TTL
Cost calculation: Value × Change Rate
Selective Caching
Cache only if:
- Query cost > threshold
- Access frequency > minimum
- Result size < maximum
Pre-warming
Cost: Upfront computation
Benefit: 100% hit rate initially
ROI positive when: Traffic spike value > warming cost