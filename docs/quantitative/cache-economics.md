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
[Home](../index.md) → [Part IV: Quantitative](index.md) → **Cache Economics Sheet**

# Cache Economics Sheet

**When caching saves money**

## Cache Break-Even Formula

The fundamental equation for cache profitability:

<div class="axiom-box">
<h4>💰 Cache Break-Even Formula</h4>

<div style="background: #F3E5F5; padding: 20px; border-radius: 8px;">
  <div style="background: white; padding: 15px; border-radius: 5px; font-family: monospace; text-align: center; margin-bottom: 15px;">
    <strong style="font-size: 1.2em; color: #5448C8;">Cache is profitable when:</strong><br>
    <span style="font-size: 1.1em;">(Cache Cost) < (Saved Backend Cost) + (Saved Latency Cost)</span>
  </div>
  
  <table style="width: 100%; background: white; border-radius: 5px;">
    <tr style="background: #E8E5F5;">
      <th style="padding: 12px; text-align: left;">Component</th>
      <th style="padding: 12px;">Formula</th>
    </tr>
    <tr>
      <td style="padding: 10px;"><strong>Cache Cost</strong></td>
      <td style="padding: 10px; font-family: monospace;">Memory$ + CPU$ + Network$</td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px;"><strong>Saved Backend</strong></td>
      <td style="padding: 10px; font-family: monospace;">(Hit Rate) × (Requests) × (Backend $/request)</td>
    </tr>
    <tr>
      <td style="padding: 10px;"><strong>Saved Latency</strong></td>
      <td style="padding: 10px; font-family: monospace;">(Hit Rate) × (Requests) × (Latency Reduction) × ($/ms)</td>
    </tr>
  </table>
</div>
</div>

## Cache Sizing Economics

### Memory Cost Analysis
<div class="truth-box">
<h4>💾 Memory Cost Analysis Example</h4>

<div style="background: #E3F2FD; padding: 20px; border-radius: 8px;">
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div>
      <h5 style="margin: 0 0 10px 0; color: #1565C0;">Redis Cluster Costs</h5>
      <table style="width: 100%; background: white; border-radius: 5px;">
        <tr style="background: #BBDEFB;">
          <td style="padding: 8px;"><strong>Memory</strong></td>
          <td style="padding: 8px; text-align: right;">100GB</td>
        </tr>
        <tr>
          <td style="padding: 8px;"><strong>Monthly cost</strong></td>
          <td style="padding: 8px; text-align: right; color: #1976D2;">$500</td>
        </tr>
        <tr style="background: #F5F5F5;">
          <td style="padding: 8px;"><strong>Total keys</strong></td>
          <td style="padding: 8px; text-align: right;">1 billion</td>
        </tr>
        <tr>
          <td style="padding: 8px;"><strong>Avg key size</strong></td>
          <td style="padding: 8px; text-align: right;">100 bytes</td>
        </tr>
        <tr style="background: #E3F2FD;">
          <td style="padding: 8px;"><strong>Cost per key</strong></td>
          <td style="padding: 8px; text-align: right; font-weight: bold;">$0.0000005</td>
        </tr>
      </table>
    </div>
    
    <div>
      <h5 style="margin: 0 0 10px 0; color: #E65100;">Database Query Costs</h5>
      <table style="width: 100%; background: white; border-radius: 5px;">
        <tr style="background: #FFE0B2;">
          <td style="padding: 8px;"><strong>Query cost</strong></td>
          <td style="padding: 8px; text-align: right; color: #E65100;">$0.001</td>
        </tr>
        <tr>
          <td style="padding: 8px;"><strong>vs Cache</strong></td>
          <td style="padding: 8px; text-align: right;">2000x more</td>
        </tr>
        <tr style="background: #FFF3E0;">
          <td style="padding: 8px;"><strong>Break-even</strong></td>
          <td style="padding: 8px; text-align: right; font-weight: bold;">2000 queries/key/month</td>
        </tr>
        <tr>
          <td style="padding: 8px;"><strong>Daily needed</strong></td>
          <td style="padding: 8px; text-align: right; color: #E65100; font-weight: bold;">67 queries/key</td>
        </tr>
      </table>
    </div>
  </div>
  
  <div style="margin-top: 20px; background: #FFF; padding: 15px; border-radius: 5px; text-align: center;">
    <strong>Decision Rule:</strong> If a key is accessed more than <span style="color: #E65100; font-weight: bold;">67 times per day</span>, caching saves money!
  </div>
</div>
</div>

### Hit Rate Impact
<div class="decision-box">
<h4>🎯 Hit Rate Impact on ROI</h4>

<div style="background: #E8F5E9; padding: 20px; border-radius: 8px;">
  <table style="width: 100%; background: white; border-radius: 5px; border-collapse: collapse;">
    <tr style="background: #C8E6C9;">
      <th style="padding: 12px; text-align: left;">Hit Rate</th>
      <th style="padding: 12px;">Backend Savings</th>
      <th style="padding: 12px;">ROI</th>
      <th style="padding: 12px;">Visual ROI</th>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>50%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">50%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #F44336;">-20% (loss)</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #F44336; width: 20%; height: 15px; margin-left: auto;"></div>
      </td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>70%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">70%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #FF9800;">+15%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #FF9800; width: 15%; height: 15px;"></div>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>80%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">80%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #4CAF50;">+45%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #4CAF50; width: 45%; height: 15px;"></div>
      </td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>90%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">90%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #2E7D32;">+125%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #2E7D32; width: 80%; height: 15px;"></div>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>95%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">95%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #1B5E20;">+200%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #1B5E20; width: 90%; height: 15px;"></div>
      </td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px; border: 1px solid #E0E0E0;"><strong>99%</strong></td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">99%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0; color: #1B5E20;">+400%</td>
      <td style="padding: 10px; border: 1px solid #E0E0E0;">
        <div style="background: #1B5E20; width: 100%; height: 15px;"></div>
      </td>
    </tr>
  </table>
  
  <div style="margin-top: 20px; text-align: center;">
    <svg viewBox="0 0 400 250" style="width: 100%; max-width: 400px;">
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

<div class="key-insight" style="margin-top: 15px;">
💡 <strong>Critical Insight</strong>: Below 70% hit rate, caching often loses money. Aim for 80%+ hit rates!
</div>
</div>

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
<div class="decision-box">
<h4>⏱️ Adaptive TTL Strategy</h4>

<div style="background: #E8F5E9; padding: 20px; border-radius: 8px;">
  <div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
    <pre style="margin: 0; overflow-x: auto;"><code>def calculate_ttl(key, access_pattern):
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

    return ttl</code></pre>
  </div>
  
  <table style="width: 100%; background: white; border-radius: 5px;">
    <tr style="background: #C8E6C9;">
      <th style="padding: 12px; text-align: left;">Key Type</th>
      <th style="padding: 12px;">TTL Strategy</th>
      <th style="padding: 12px;">Example TTL</th>
      <th style="padding: 12px;">Reasoning</th>
    </tr>
    <tr>
      <td style="padding: 10px;"><strong>Expensive queries</strong></td>
      <td style="padding: 10px;">4x base</td>
      <td style="padding: 10px; color: #2E7D32;">4 hours</td>
      <td style="padding: 10px;">Maximize cost savings</td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px;"><strong>Frequently updated</strong></td>
      <td style="padding: 10px;">0.25x base</td>
      <td style="padding: 10px; color: #FF5722;">15 minutes</td>
      <td style="padding: 10px;">Minimize staleness</td>
    </tr>
    <tr>
      <td style="padding: 10px;"><strong>Periodic access</strong></td>
      <td style="padding: 10px;">1.5x period</td>
      <td style="padding: 10px; color: #2196F3;">Variable</td>
      <td style="padding: 10px;">Match access pattern</td>
    </tr>
    <tr style="background: #F5F5F5;">
      <td style="padding: 10px;"><strong>Default</strong></td>
      <td style="padding: 10px;">1x base</td>
      <td style="padding: 10px;">1 hour</td>
      <td style="padding: 10px;">Balanced approach</td>
    </tr>
  </table>
</div>

<div class="key-insight" style="margin-top: 15px;">
💡 <strong>Pro Tip</strong>: Monitor actual hit rates and adjust TTL accordingly. Start conservative and increase gradually.
</div>
</div>

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
<div class="decision-box">
<h4>📈 Memory vs Hit Rate Trade-offs</h4>

<div style="background: #E8F5E9; padding: 20px; border-radius: 8px;">
  <table style="width: 100%; background: white; border-radius: 5px; margin-bottom: 20px;">
    <tr style="background: #C8E6C9;">
      <th style="padding: 12px;">Cache Size</th>
      <th style="padding: 12px;">Hit Rate</th>
      <th style="padding: 12px;">Cost/month</th>
      <th style="padding: 12px;">Benefit/month</th>
      <th style="padding: 12px;">Net Value</th>
    </tr>
    <tr>
      <td style="padding: 10px; text-align: center;"><strong>1GB</strong></td>
      <td style="padding: 10px; text-align: center;">60%</td>
      <td style="padding: 10px; text-align: center; color: #4CAF50;">$10</td>
      <td style="padding: 10px; text-align: center;">$600</td>
      <td style="padding: 10px; text-align: center; color: #2E7D32; font-weight: bold;">+$590</td>
    </tr>
    <tr style="background: #F1F8E9;">
      <td style="padding: 10px; text-align: center;"><strong>10GB</strong></td>
      <td style="padding: 10px; text-align: center;">85%</td>
      <td style="padding: 10px; text-align: center; color: #66BB6A;">$100</td>
      <td style="padding: 10px; text-align: center;">$850</td>
      <td style="padding: 10px; text-align: center; color: #2E7D32; font-weight: bold;">+$750</td>
    </tr>
    <tr>
      <td style="padding: 10px; text-align: center;"><strong>100GB</strong></td>
      <td style="padding: 10px; text-align: center;">95%</td>
      <td style="padding: 10px; text-align: center; color: #FF9800;">$1,000</td>
      <td style="padding: 10px; text-align: center;">$950</td>
      <td style="padding: 10px; text-align: center; color: #F44336; font-weight: bold;">-$50</td>
    </tr>
    <tr style="background: #FFEBEE;">
      <td style="padding: 10px; text-align: center;"><strong>1TB</strong></td>
      <td style="padding: 10px; text-align: center;">99%</td>
      <td style="padding: 10px; text-align: center; color: #F44336;">$10,000</td>
      <td style="padding: 10px; text-align: center;">$990</td>
      <td style="padding: 10px; text-align: center; color: #B71C1C; font-weight: bold;">-$9,010</td>
    </tr>
  </table>
  
  <div style="text-align: center; margin-bottom: 20px;">
    <svg viewBox="0 0 500 300" style="width: 100%; max-width: 500px;">
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
  </div>
  
  <div style="background: #C8E6C9; padding: 15px; border-radius: 5px; text-align: center;">
    <strong style="font-size: 1.2em;">🎯 Sweet Spot: 10-100GB for most applications</strong>
    <div style="margin-top: 10px;">Balances hit rate improvement with diminishing returns on investment</div>
  </div>
</div>
</div>

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
<div class="failure-vignette">
<h4>🛍️ E-commerce Cache ROI Example</h4>

<div style="background: #FFEBEE; padding: 20px; border-radius: 8px;">
  <h5 style="margin: 0 0 15px 0;">Product Catalog Caching Scenario</h5>
  
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
    <div style="background: white; padding: 15px; border-radius: 5px;">
      <h6 style="margin: 0 0 10px 0; color: #C62828;">Traffic & Performance</h6>
      <table style="width: 100%;">
        <tr><td>Requests/month:</td><td style="text-align: right; font-weight: bold;">100M</td></tr>
        <tr><td>Hit rate:</td><td style="text-align: right; font-weight: bold; color: #4CAF50;">90%</td></tr>
        <tr><td>Latency reduction:</td><td style="text-align: right; font-weight: bold;">50ms</td></tr>
      </table>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 5px;">
      <h6 style="margin: 0 0 10px 0; color: #C62828;">Cost Parameters</h6>
      <table style="width: 100%;">
        <tr><td>Backend cost:</td><td style="text-align: right;">$0.001/req</td></tr>
        <tr><td>Cache cost:</td><td style="text-align: right;">$2,000/mo</td></tr>
        <tr><td>Latency value:</td><td style="text-align: right;">$0.00001/ms</td></tr>
      </table>
    </div>
  </div>
  
  <div style="background: white; padding: 20px; border-radius: 5px;">
    <h6 style="margin: 0 0 15px 0; text-align: center;">Savings Calculation</h6>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center;">
      <div style="background: #E8F5E9; padding: 15px; border-radius: 5px;">
        <div style="font-size: 0.9em; color: #666;">Backend Savings</div>
        <div style="font-size: 0.85em; margin: 5px 0;">100M × 0.9 × $0.001</div>
        <div style="font-size: 1.5em; font-weight: bold; color: #2E7D32;">$90,000</div>
      </div>
      
      <div style="background: #E3F2FD; padding: 15px; border-radius: 5px;">
        <div style="font-size: 0.9em; color: #666;">Latency Savings</div>
        <div style="font-size: 0.85em; margin: 5px 0;">100M × 0.9 × 50ms × $0.00001</div>
        <div style="font-size: 1.5em; font-weight: bold; color: #1976D2;">$45,000</div>
      </div>
      
      <div style="background: #FFF3E0; padding: 15px; border-radius: 5px;">
        <div style="font-size: 0.9em; color: #666;">Total Savings</div>
        <div style="font-size: 0.85em; margin: 5px 0;">&nbsp;</div>
        <div style="font-size: 1.5em; font-weight: bold; color: #E65100;">$135,000</div>
      </div>
    </div>
    
    <div style="margin-top: 20px; text-align: center; background: #4CAF50; color: white; padding: 20px; border-radius: 5px;">
      <div style="font-size: 1.2em;">Return on Investment</div>
      <div style="font-size: 2.5em; font-weight: bold;">6,650%</div>
      <div style="font-size: 0.9em; margin-top: 10px;">($135,000 - $2,000) / $2,000</div>
    </div>
  </div>
</div>

<div class="insight-note" style="margin-top: 15px; background: #E8F5E9; padding: 15px; border-left: 4px solid #4CAF50;">
💡 <strong>Key Takeaway</strong>: Even expensive cache infrastructure pays for itself many times over with good hit rates!
</div>
</div>

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
