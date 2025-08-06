---
title: Cache Economics Sheet
description: 'The fundamental equation for cache profitability:'
type: quantitative
difficulty: beginner
reading_time: 40 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Cache Economics Sheet



## Overview

Cache Economics Sheet
description: 'The fundamental equation for cache profitability:'
type: quantitative
difficulty: beginner
reading_time: 40 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Cache Economics Sheet

## Table of Contents

- [Cache Break-Even Formula](#cache-break-even-formula)
- [Cache Sizing Economics](#cache-sizing-economics)
  - [Memory Cost Analysis](#memory-cost-analysis)
  - [Hit Rate Impact](#hit-rate-impact)
- [Cache Pattern Economics](#cache-pattern-economics)
- [Cache-Aside ROI](#cache-aside-roi)
- [Write-Through ROI](#write-through-roi)
- [Write-Back ROI](#write-back-roi)
- [Real-World Cache Economics](#real-world-cache-economics)
  - [CDN Edge Caching](#cdn-edge-caching)
  - [Application Cache Tiers](#application-cache-tiers)
  - [Database Query Cache](#database-query-cache)
- [Cache Invalidation Costs](#cache-invalidation-costs)
- [Cache Optimization Strategies](#cache-optimization-strategies)
  - [Adaptive TTL](#adaptive-ttl)
  - [Selective Caching](#selective-caching)
  - [Pre-warming Economics](#pre-warming-economics)
- [Cache Sizing Optimization](#cache-sizing-optimization)
  - [Working Set Analysis](#working-set-analysis)
  - [Memory vs Hit Rate](#memory-vs-hit-rate)
  - [Multi-Level Cache Sizing](#multi-level-cache-sizing)
- [L1: CPU cache (free but tiny)](#l1-cpu-cache-free-but-tiny)
- [L2: Application memory](#l2-application-memory)
- [L3: Redis](#l3-redis)
- [Cache ROI Calculator](#cache-roi-calculator)
  - [Input Parameters](#input-parameters)
  - [Example Calculation](#example-calculation)
- [Key Decision Factors](#key-decision-factors)
- [Key Takeaways](#key-takeaways)



**When caching saves money**

## Cache Break-Even Formula

! Cache Break-Even Formula"

 <div>
 <div>
 <strong>Cache is profitable when:</strong><br>
 <span>(Cache Cost) < (Saved Backend Cost) + (Saved Latency Cost)</span>
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Component</th>
 <th>Formula</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Component"><strong>Cache Cost</strong></td>
 <td data-label="Formula">Memory$ + CPU$ + Network$</td>
 </tr>
 <tr>
 <td data-label="Component"><strong>Saved Backend</strong></td>
 <td data-label="Formula">(Hit Rate) × (Requests) × (Backend $/request)</td>
 </tr>
 <tr>
 <td data-label="Component"><strong>Saved Latency</strong></td>
 <td data-label="Formula">(Hit Rate) × (Requests) × (Latency Reduction) × ($/ms)</td>
 </tr>
 </tbody>
</table>
</div>
</div>

## Cache Sizing Economics

### Memory Cost Analysis
!

**Reading time:** ~11 minutes

## Table of Contents

- [Cache Break-Even Formula](#cache-break-even-formula)
- [Cache Sizing Economics](#cache-sizing-economics)
  - [Memory Cost Analysis](#memory-cost-analysis)
  - [Hit Rate Impact](#hit-rate-impact)
- [Cache Pattern Economics](#cache-pattern-economics)
- [Cache-Aside ROI](#cache-aside-roi)
- [Write-Through ROI](#write-through-roi)
- [Write-Back ROI](#write-back-roi)
- [Real-World Cache Economics](#real-world-cache-economics)
  - [CDN Edge Caching](#cdn-edge-caching)
  - [Application Cache Tiers](#application-cache-tiers)
  - [Database Query Cache](#database-query-cache)
- [Cache Invalidation Costs](#cache-invalidation-costs)
- [Cache Optimization Strategies](#cache-optimization-strategies)
  - [Adaptive TTL](#adaptive-ttl)
  - [Selective Caching](#selective-caching)
  - [Pre-warming Economics](#pre-warming-economics)
- [Cache Sizing Optimization](#cache-sizing-optimization)
  - [Working Set Analysis](#working-set-analysis)
  - [Memory vs Hit Rate](#memory-vs-hit-rate)
  - [Multi-Level Cache Sizing](#multi-level-cache-sizing)
- [L1: CPU cache (free but tiny)](#l1-cpu-cache-free-but-tiny)
- [L2: Application memory](#l2-application-memory)
- [L3: Redis](#l3-redis)
- [Cache ROI Calculator](#cache-roi-calculator)
  - [Input Parameters](#input-parameters)
  - [Example Calculation](#example-calculation)
- [Key Decision Factors](#key-decision-factors)
- [Key Takeaways](#key-takeaways)



**When caching saves money**

## Cache Break-Even Formula

!!! abstract "💰 Cache Break-Even Formula"

 <div>
 <div>
 <strong>Cache is profitable when:</strong><br>
 <span>(Cache Cost) < (Saved Backend Cost) + (Saved Latency Cost)</span>
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Component</th>
 <th>Formula</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Component"><strong>Cache Cost</strong></td>
 <td data-label="Formula">Memory$ + CPU$ + Network$</td>
 </tr>
 <tr>
 <td data-label="Component"><strong>Saved Backend</strong></td>
 <td data-label="Formula">(Hit Rate) × (Requests) × (Backend $/request)</td>
 </tr>
 <tr>
 <td data-label="Component"><strong>Saved Latency</strong></td>
 <td data-label="Formula">(Hit Rate) × (Requests) × (Latency Reduction) × ($/ms)</td>
 </tr>
 </tbody>
</table>
</div>
</div>

## Cache Sizing Economics

### Memory Cost Analysis
!!! info "💾 Memory Cost Analysis Example"
 <div>
 <div>
 <div>
 <h5>Redis Cluster Costs</h5>
 <table class="responsive-table">
 <tr>
 <td><strong>Memory</strong></td>
 <td>100GB</td>
 </tr>
 <tr>
 <td><strong>Monthly cost</strong></td>
 <td>$500</td>
 </tr>
 <tr>
 <td><strong>Total keys</strong></td>
 <td>1 billion</td>
 </tr>
 <tr>
 <td><strong>Avg key size</strong></td>
 <td>100 bytes</td>
 </tr>
 <tr>
 <td><strong>Cost per key</strong></td>
 <td>$0.0000005</td>
 </tr>
 </table>
 
 <div>
 <h5>Database Query Costs</h5>
 <table class="responsive-table">
 <tr>
 <td><strong>Query cost</strong></td>
 <td>$0.001</td>
 </tr>
 <tr>
 <td><strong>vs Cache</strong></td>
 <td>2000x more</td>
 </tr>
 <tr>
 <td><strong>Break-even</strong></td>
 <td>2000 queries/key/month</td>
 </tr>
 <tr>
 <td><strong>Daily needed</strong></td>
 <td>67 queries/key</td>
 </tr>
 </table>
 </div>
 </div>
 
 <div>
 <strong>Decision Rule:</strong> If a key is accessed more than <span>67 times per day</span>, caching saves money!
 </div>
</div>
</div>

### Hit Rate Impact
!!! note "🎯 Hit Rate Impact on ROI"
 <div>
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Hit Rate</th>
 <th>Backend Savings</th>
 <th>ROI</th>
 <th>Visual ROI</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Hit Rate"><strong>50%</strong></td>
 <td data-label="Backend Savings">50%</td>
 <td data-label="ROI">-20% (loss)</td>
 <td data-label="Visual ROI">
 <div>
 </td>
 </tr>
 <tr>
 <td data-label="Hit Rate"><strong>70%</strong></td>
 <td data-label="Backend Savings">70%</td>
 <td data-label="ROI">+15%</td>
 <td data-label="Visual ROI">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Hit Rate"><strong>80%</strong></td>
 <td data-label="Backend Savings">80%</td>
 <td data-label="ROI">+45%</td>
 <td data-label="Visual ROI">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Hit Rate"><strong>90%</strong></td>
 <td data-label="Backend Savings">90%</td>
 <td data-label="ROI">+125%</td>
 <td data-label="Visual ROI">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Hit Rate"><strong>95%</strong></td>
 <td data-label="Backend Savings">95%</td>
 <td data-label="ROI">+200%</td>
 <td data-label="Visual ROI">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Hit Rate"><strong>99%</strong></td>
 <td data-label="Backend Savings">99%</td>
 <td data-label="ROI">+400%</td>
 <td data-label="Visual ROI">
 <div></div>
 </td>
 </tr>
 </tbody>
</table>
 
 <div>
 <svg viewBox="0 0 400 250" role="img" aria-label="Chart showing cache return on investment percentage increasing with hit rate">
 <title>Cache ROI by Hit Rate</title>
 <desc>Curve chart demonstrating how cache ROI grows exponentially as hit rate increases, breaking even around 70% and reaching 400% ROI at 99% hit rate</desc>
 <text x="200" y="20" text-anchor="middle" font-weight="bold">Cache ROI by Hit Rate</text>
 
 <!-- Axes -->
 <line x1="50" y1="200" x2="350" y2="200" stroke="#333" stroke-width="2"/>
 <line x1="50" y1="200" x2="50" y2="50" stroke="#333" stroke-width="2"/>
 
 <!-- Break-even line -->
 <line x1="50" y1="150" x2="350" y2="150" stroke="#666" stroke-width="1" stroke-dasharray="5,5"/>
 <text x="355" y="155" font-size="10" fill="#666">Break-even</text>
 
 <!-- ROI curve -->
 <path d="M 50 200 Q 150 180, 250 100 T 350 50" 
 stroke="#4CAF50" stroke-width="3" fill="none"/>
 
 <!-- Labels -->
 <text x="50" y="220" text-anchor="middle" font-size="10">50%</text>
 <text x="150" y="220" text-anchor="middle" font-size="10">70%</text>
 <text x="250" y="220" text-anchor="middle" font-size="10">90%</text>
 <text x="350" y="220" text-anchor="middle" font-size="10">99%</text>
 <text x="200" y="240" text-anchor="middle" font-size="12">Hit Rate</text>
 
 <text x="30" y="200" text-anchor="middle" font-size="10">0%</text>
 <text x="30" y="100" text-anchor="middle" font-size="10">200%</text>
 <text x="30" y="50" text-anchor="middle" font-size="10">400%</text>
 <text x="20" y="125" text-anchor="middle" font-size="12" transform="rotate(-90 20 125)">ROI</text>
 </svg>
 </div>
</div>

!!! info
 💡 <strong>Critical Insight</strong>: Below 70% hit rate, caching often loses money. Aim for 80%+ hit rates!
</div>

## Cache Pattern Economics

```python
## Cache-Aside ROI
Costs: 2 ops on miss, 1 on hit, infrastructure
Benefits: Reduced backend load, lower latency
Break-even hit rate: 60-70%

## Write-Through ROI
Costs: Double writes, consistency management
Benefits: Always fresh, no misses
Break-even: read/write > 3:1

## Write-Back ROI
Costs: Data loss risk, complex recovery
Benefits: Write performance, backend protection
Break-even: write-heavy + loss-tolerant
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

```text
TTL-Based:
- Cost: Stale data incidents × Business impact
- Example: Product prices (5min), Inventory (real-time), Profiles (1hr)

Event-Based ($350/month):
- Message queue: $100/month
- Invalidation service: $200/month 
- Monitoring: $50/month
- Break-even: When stale data costs > $350/month

Tag-Based:
- Storage: O(tags × keys), ~20% overhead
- CPU: ~5% overhead
- Worth it: Complex dependencies + costly stale data
```

## Cache Optimization Strategies

### Adaptive TTL
!!! note "⏱️ Adaptive TTL Strategy"
 <div>
 <div>
 <pre><code>def calculate_ttl(key, access_pattern):
 base_ttl = 3600 # 1 hour
 # High-value keys: Longer TTL
 if is_expensive_query(key):
 ttl = base_ttl * 4
 # Frequently changing: Shorter TTL
 elif high_update_frequency(key):
 ttl = base_ttl / 4
 # Access pattern based
 elif access_pattern.is_periodic():
 ttl = access_pattern.period * 1.5
 return ttl</code></pre>
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Key Type</th>
 <th>TTL Strategy</th>
 <th>Example TTL</th>
 <th>Reasoning</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Key Type"><strong>Expensive queries</strong></td>
 <td data-label="TTL Strategy">4x base</td>
 <td data-label="Example TTL">4 hours</td>
 <td data-label="Reasoning">Maximize cost savings</td>
 </tr>
 <tr>
 <td data-label="Key Type"><strong>Frequently updated</strong></td>
 <td data-label="TTL Strategy">0.25x base</td>
 <td data-label="Example TTL">15 minutes</td>
 <td data-label="Reasoning">Minimize staleness</td>
 </tr>
 <tr>
 <td data-label="Key Type"><strong>Periodic access</strong></td>
 <td data-label="TTL Strategy">1.5x period</td>
 <td data-label="Example TTL">Variable</td>
 <td data-label="Reasoning">Match access pattern</td>
 </tr>
 <tr>
 <td data-label="Key Type"><strong>Default</strong></td>
 <td data-label="TTL Strategy">1x base</td>
 <td data-label="Example TTL">1 hour</td>
 <td data-label="Reasoning">Balanced approach</td>
 </tr>
 </tbody>
</table>
</div>

!!! info
 💡 <strong>Pro Tip</strong>: Monitor actual hit rates and adjust TTL accordingly. Start conservative and increase gradually.
</div>

### Selective Caching
```python
def should_cache(query_cost, access_frequency, result_size):
 cache_cost_per_hour = result_size * memory_cost_per_gb
 saved_per_hour = access_frequency * query_cost
 return saved_per_hour > cache_cost_per_hour * 2 # 2x margin
```

### Pre-warming Economics
```bash
Black Friday: 100x traffic
Pre-warming cost: $500 (2hr compute)
Without pre-warming: $50K lost sales
ROI: 100x
```

## Cache Sizing Optimization

### Working Set Analysis
```redis
Pareto: 20% of keys = 80% of requests
→ Cache top 20% by frequency
→ 80% hit rate with 20% memory
```

### Memory vs Hit Rate
!!! note "📈 Memory vs Hit Rate Trade-offs"
 <div>
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Cache Size</th>
 <th>Hit Rate</th>
 <th>Cost/month</th>
 <th>Benefit/month</th>
 <th>Net Value</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Cache Size"><strong>1GB</strong></td>
 <td data-label="Hit Rate">60%</td>
 <td data-label="Cost/month">$10</td>
 <td data-label="Benefit/month">$600</td>
 <td data-label="Net Value">+$590</td>
 </tr>
 <tr>
 <td data-label="Cache Size"><strong>10GB</strong></td>
 <td data-label="Hit Rate">85%</td>
 <td data-label="Cost/month">$100</td>
 <td data-label="Benefit/month">$850</td>
 <td data-label="Net Value">+$750</td>
 </tr>
 <tr>
 <td data-label="Cache Size"><strong>100GB</strong></td>
 <td data-label="Hit Rate">95%</td>
 <td data-label="Cost/month">$1,000</td>
 <td data-label="Benefit/month">$950</td>
 <td data-label="Net Value">-$50</td>
 </tr>
 <tr>
 <td data-label="Cache Size"><strong>1TB</strong></td>
 <td data-label="Hit Rate">99%</td>
 <td data-label="Cost/month">$10,000</td>
 <td data-label="Benefit/month">$990</td>
 <td data-label="Net Value">-$9,010</td>
 </tr>
 </tbody>
 </table>
 <div>
 <svg viewBox="0 0 500 300" role="img" aria-label="Chart comparing cache size, hit rate percentage, and net value to identify optimal cache sizing">
 <title>Cache Size vs Hit Rate vs Value</title>
 <desc>Visualization showing the relationship between cache size (1GB to 1TB), hit rate curve, and net value curve, identifying a sweet spot between 10-100GB for most applications</desc>
 <text x="250" y="20" text-anchor="middle" font-weight="bold">Cache Size vs Hit Rate vs Value</text>
 <!-- Axes -->
 <line x1="50" y1="250" x2="450" y2="250" stroke="#333" stroke-width="2"/>
 <line x1="50" y1="250" x2="50" y2="50" stroke="#333" stroke-width="2"/>
 <!-- Hit rate curve -->
 <path d="M 100 200 Q 200 120, 300 80 T 400 60"
 stroke="#2196F3" stroke-width="3" fill="none"/>
 <text x="410" y="60" font-size="10" fill="#2196F3">Hit Rate</text>
 <!-- Value curve -->
 <path d="M 100 100 Q 200 80, 300 120 T 400 200"
 stroke="#4CAF50" stroke-width="3" fill="none"/>
 <text x="410" y="200" font-size="10" fill="#4CAF50">Net Value</text>
 <!-- Sweet spot area -->
 <rect x="150" y="50" width="100" height="200" fill="#4CAF50" opacity="0.1"/>
 <text x="200" y="40" text-anchor="middle" font-size="12" fill="#2E7D32">Sweet Spot</text>
 <!-- X-axis labels -->
 <text x="100" y="270" text-anchor="middle" font-size="10">1GB</text>
 <text x="200" y="270" text-anchor="middle" font-size="10">10GB</text>
 <text x="300" y="270" text-anchor="middle" font-size="10">100GB</text>
 <text x="400" y="270" text-anchor="middle" font-size="10">1TB</text>
 </svg>
 
 <div>
 <strong>🎯 Sweet Spot: 10-100GB for most applications</strong>
 <div>Balances hit rate improvement with diminishing returns on investment</div>
 </div>
</div>
</div>

### Multi-Level Cache Sizing
```python
def optimize_cache_sizes(budget, access_pattern):
## L1: CPU cache (free but tiny)
 l1_size = min(cpu_cache_available, hot_working_set)

## L2: Application memory
 l2_cost_per_gb = $5
 l2_size = optimize_for_hit_rate(
 budget * 0.3, # 30% of budget
 l2_cost_per_gb
 )

## L3: Redis
 l3_cost_per_gb = $50
 l3_size = optimize_for_hit_rate(
 budget * 0.7, # 70% of budget
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
!!! danger "🛍️ E-commerce Cache ROI Example"
 <div>
 <h5>Product Catalog Caching Scenario</h5>
 <div>
 <div>
 <h6>Traffic & Performance</h6>
 <table class="responsive-table">
 <tr><td>Requests/month:</td><td>100M</td></tr>
 <tr><td>Hit rate:</td><td>90%</td></tr>
 <tr><td>Latency reduction:</td><td>50ms</td></tr>
 </table>
 
 <div>
 <h6>Cost Parameters</h6>
 <table class="responsive-table">
 <tr><td>Backend cost:</td><td>$0.001/req</td></tr>
 <tr><td>Cache cost:</td><td>$2,000/mo</td></tr>
 <tr><td>Latency value:</td><td>$0.00001/ms</td></tr>
 </table>
 </div>
 </div>
 
 <div>
 <h6>Savings Calculation</h6>
 
 <div>
 <div>
 <div>Backend Savings</div>
 <div>100M × 0.9 × $0.001</div>
 <div>$90,000</div>
 </div>
 
 <div>
 <div>Latency Savings</div>
 <div>100M × 0.9 × 50ms × $0.00001</div>
 <div>$45,000</div>
 </div>
 
 <div>
 <div>Total Savings</div>
 <div>&nbsp;</div>
 <div>$135,000</div>
 </div>
 </div>
 
 <div>
 <div>Return on Investment</div>
 <div>6,650%</div>
 <div>($135,000 - $2,000) / $2,000</div>
 </div>
 </div>
</div>

!!! info
 💡 <strong>Key Takeaway</strong>: Even expensive cache infrastructure pays for itself many times over with good hit rates!
</div>

## Key Decision Factors

1. **Access Pattern**: Random (low hit rate) → Temporal → Zipfian (high hit rate)
2. **Data Volatility**: Static (cache all) → Slow (long TTL) → Rapid (selective)
3. **Query Cost**: Expensive/Complex joins → Always cache; Cheap → Cache if frequent
4. **Business Impact**: Revenue-critical → Over-provision; Internal → Optimize cost

## Key Takeaways

1. **80% hit rate = sweet spot** (ROI drops below)
2. **Cache hot data only** (full dataset rarely profitable)
3. **Multiple tiers multiply benefits** (L1+L2+L3 > L3)
4. **Invalidation strategy matters** (wrong choice negates savings)
5. **Measure actual hit rates** (predictions often optimistic)
