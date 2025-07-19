# Axiom 1: Latency (Speed of Light)

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Internalize that latency is physics, not engineering.
  </div>
</div>

## Core Definition

<div class="definition-box">
<strong>Latency</strong> := Time for information to travel from point A to point B

**Minimum Bound**: distance / speed_of_light

**In fiber**: ~200,000 km/s (2/3 of c due to refractive index)
</div>

## The Physics Foundation

Light—and therefore information—has a speed limit:

- **Light in vacuum**: 299,792 km/s
- **In fiber optic cable**: ~200,000 km/s  
- **In copper wire**: ~200,000 km/s (electromagnetic wave)

💡 **Fundamental Insight**: No engineering can overcome physics. You cannot patch the speed of light.

## The Latency Ladder

Understanding latency starts with knowing the fundamental delays at each scale:

```
Same rack:          0.5 ms    ████
Same DC:            1-2 ms    ████████
Same region:        10 ms     ████████████████████
Cross-continent:    100 ms    ████████████████████████████████████████
Opposite globe:     200+ ms   ████████████████████████████████████████████████████████████████████████
Geosync satellite:  500+ ms   ████████████████████████████████████████████████████████████████████████████████████████████████████████████
Mars (best case):   4 min     ∞ (off the chart)
```

## 🎬 Failure Vignette: The Tokyo Checkout Disaster

**Company**: Major US E-commerce Platform  
**Date**: Black Friday 2019  
**Impact**: $12M lost revenue

**The Setup**: 
- "Smart" optimization routes all Asian traffic to Tokyo DC
- San Francisco inventory database is source of truth
- Checkout requires inventory verification

**The Physics**:
```
Tokyo ↔ San Francisco: 5,000 miles
Theoretical minimum: 5,000 / 124,000 mph = 40ms one-way
Actual RTT: 250ms (includes routing, processing)
```

**The Disaster**:
- Each checkout needs 3 database calls
- 250ms × 3 = 750ms just in physics tax
- Add processing: 1.2 seconds total
- **Result**: 67% cart abandonment

**The Fix**: Regional inventory caches with eventual consistency

**Lesson**: Speed of light is a budget, not a suggestion.

## Decision Framework

<div class="decision-box">
<h3>🎯 Cache vs Replica Decision Tree</h3>

```python
if latency_budget < physics_minimum:
    if data_changes_rarely:
        use_cache(ttl = change_frequency)
    elif eventual_consistency_ok:
        use_read_replica(async_replication)
    else:
        # Cannot satisfy requirements
        REDESIGN to avoid remote calls
else:
    use_remote_calls(
        margin = latency_budget - physics_minimum
    )
```
</div>

## 🔧 Try This: Measure Your Physics Tax

```bash
# 1. Measure your physics tax
ping -c 10 google.com | grep "min/avg/max"
traceroute google.com | tail -5

# 2. Calculate efficiency
# actual_latency / theoretical_minimum = efficiency
# If efficiency > 2.0, you have optimization opportunities
```

**What you'll learn**: Your actual latency includes routing inefficiency, not just physics.

## The Latency Budget Worksheet

Every operation has a latency budget. Here's how to allocate it:

<div class="worksheet">
<h3>📊 Latency P&L Statement</h3>

**REVENUE (Total Budget)**
- User Expectation: `[___]` ms
- Minus Browser Render: `-50` ms  
- Minus Network Last Mile: `-20` ms
- **= Backend Budget**: `[___]` ms

**EXPENSES (Allocations)**
- Load Balancer: `[___]` ms (typical: 1-2)
- API Gateway: `[___]` ms (typical: 2-5)
- Service Mesh: `[___]` ms (typical: 1-3)
- Business Logic: `[___]` ms (varies)
- Database Call: `[___]` ms (typical: 5-50)
- Cache Check: `[___]` ms (typical: 0.5-2)
- **Total Spent**: `[___]` ms

**MARGIN**: `[___]` ms (must be > 0!)
</div>

## Counter-Intuitive Truths

<div class="insight-box">
<h3>💡 Adding Servers Can Increase Latency</h3>

More servers = more hops = more latency

The fastest distributed system is often the one with fewer, better-placed nodes, not more nodes.

Example: Adding a caching layer adds a network hop. If cache hit rate < 90%, you may increase average latency.
</div>

## Worked Example: Photo Sharing App

<div class="example-box">
<h3>🧮 Latency Budget Allocation</h3>

**Requirement**: User uploads photo, expects thumbnail in < 2 seconds

```
Budget Allocation:
- Upload to CDN edge:       100 ms  (physics: user to edge)
- Edge to origin DC:         50 ms  (physics: edge to DC)  
- Queue wait time:          200 ms  (p95 during peak)
- Resize processing:        500 ms  (CPU bound)
- Thumbnail generation:     300 ms  (GPU accelerated)
- Write to 3 replicas:      150 ms  (parallel writes)
- CDN cache population:     200 ms  (push to edges)
- Response to user:         100 ms  (physics: edge to user)
TOTAL:                    1,600 ms  ✓ (400ms margin)

Optimization opportunities:
1. Pre-warm GPU containers (-200ms cold start)
2. Regional processing (-50ms physics tax)  
3. Optimistic UI (-1600ms perceived!)
```
</div>

## Common Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Latency Violations to Avoid</h3>

1. **Death by Thousand Cuts**: Each service "only" adds 5ms
2. **Retry Multiplication**: 3 retries × 100ms = 300ms gone
3. **Serial Staircase**: Waterfall instead of parallel calls
4. **Cold Start Surprise**: Lambda/container warm-up time
5. **GC Pause Gambling**: 99th percentile GC stops
</div>

## Measurement Points

<div class="measure-this">
<h3>📊 What to Instrument</h3>

```python
# Add these measurements to your system:
@latency_budget("database_query", budget_ms=50)
def get_user_data(user_id):
    # Your code here
    pass

# Alerts when budget violated:
- p50 latency > budget * 0.5
- p95 latency > budget * 0.9  
- p99 latency > budget * 1.5
```
</div>

## Cross-References

<div class="cross-links">
<h3>🔗 Related Concepts</h3>

- → [Caching Hierarchies](../../patterns/caching): Implementation patterns
- → [Geo-Replication](../../patterns/geo-replication): Multi-region strategies
- → [Axiom 5: Coordination](../axiom5-coordination/): Why consensus is slow
- → [Axiom 8: Economics](../axiom8-economics/): Dollar cost of milliseconds
</div>

## Summary: Key Takeaways

1. **Latency is physics**, not engineering
2. **Budget latency** like money—you can only spend it once
3. **Measure everything**—you can't optimize what you don't see
4. **Geography matters**—you cannot cache distance
5. **Design for physics**—work with constraints, not against them

## Quick Reference Card

<div class="reference-card">
<h3>📋 Latency Quick Reference</h3>

**Typical Operations**:
- L1 cache: 0.5 ns
- L2 cache: 7 ns
- RAM: 100 ns
- SSD: 150 μs
- HDD: 10 ms
- Network same DC: 0.5 ms
- Network cross-region: 50 ms

**Rule of thumb**: 
- If `distance > 1000 km`, latency dominates design
- If `operation_count > 10`, parallelize or batch
- If `budget < 100ms`, avoid cross-region calls
</div>

---

**Next**: [Axiom 2: Finite Capacity →](../axiom2-capacity/)

*"You can't fight physics, but you can design around it."*