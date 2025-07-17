# Axiom 1: Latency (Speed of Light)

!!! info "Prerequisites"
    - [Core Philosophy](../../introduction/philosophy.md)
    - Basic understanding of networks

!!! tip "Quick Navigation"
    [← Axioms Overview](../index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Capacity](../axiom-2-capacity/index.md)

!!! target "Learning Objective"
    Internalize that latency is physics, not engineering. You can optimize but never eliminate the speed of light constraint.

## Why Should I Care?

!!! question "Real Impact on Your Systems"
    - **User Experience**: 53% of mobile users abandon sites that take >3 seconds to load
    - **Revenue**: Amazon loses $1.6B per year for each second of load time
    - **SEO**: Google uses page speed as a ranking factor
    - **Architecture**: You can't put all your servers in one location and serve global users
    - **Cost**: Ignoring physics leads to expensive band-aid solutions

## Core Concept

<div class="axiom-box">

**Definition:**

```
Latency := Time for information to travel from point A to point B
Minimum Bound: distance / speed_of_light
In fiber: ~200,000 km/s (2/3 of c due to refractive index)
```

</div>

## The Physics Foundation

| Medium | Speed | Note |
|--------|-------|------|
| Light in vacuum | 299,792 km/s | Theoretical maximum |
| Fiber optic cable | ~200,000 km/s | Refractive index slowdown |
| Copper wire | ~200,000 km/s | Electromagnetic wave |

!!! danger "Fundamental Insight"
    No engineering can overcome physics. This is not a problem to solve but a constraint to accept and design around.

## The Latency Ladder 🪜

<div class="latency-ladder">

```
Same rack:          0.5 ms    ▓
Same DC:            1-2 ms    ▓▓
Same region:        10 ms     ▓▓▓▓▓
Cross-continent:    100 ms    ▓▓▓▓▓▓▓▓▓▓
Opposite globe:     200+ ms   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
Geosync satellite:  500+ ms   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
Mars (best case):   4 min     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

</div>

## Why This Matters

### User Experience Impact

| Latency | User Perception |
|---------|-----------------|
| 0-100ms | Instant |
| 100-300ms | Slight delay |
| 300-1000ms | Noticeable lag |
| >1000ms | Mental context switch |
| >10s | Abandonment |

### Business Impact

- **Amazon**: Every 100ms latency → 1% sales loss
- **Google**: 500ms delay → 20% traffic drop
- **Financial Trading**: 1ms advantage → millions in profit

## Latency Mathematics

### Round Trip Time (RTT)

```
Total Latency = Network RTT + Processing Time + Queueing Delay

Where:
- Network RTT = 2 × (distance / speed_of_light_in_medium)
- Processing Time = Compute time at each hop
- Queueing Delay = Wait time in buffers
```

### Geographic Calculations

```python
def minimum_latency_ms(distance_km):
    """Calculate theoretical minimum latency"""
    SPEED_OF_LIGHT_FIBER = 200_000  # km/s
    return (distance_km / SPEED_OF_LIGHT_FIBER) * 1000

# Examples
NYC_to_LA = 3_944  # km
print(f"NYC ↔ LA: {minimum_latency_ms(NYC_to_LA):.1f}ms minimum")
# Output: NYC ↔ LA: 19.7ms minimum

NYC_to_London = 5_585  # km
print(f"NYC ↔ London: {minimum_latency_ms(NYC_to_London):.1f}ms minimum")
# Output: NYC ↔ London: 27.9ms minimum
```

## Caching: The Latency Workaround

Since we can't make light faster, we move data closer:

<div class="decision-box">

**🎯 Decision Tree: Cache vs No Cache**

```
START: Is latency a problem?
│
├─ NO → Don't add complexity
│
└─ YES → Can data be stale?
         │
         ├─ NO → Must go to source
         │
         └─ YES → What's the update frequency?
                  │
                  ├─ Seconds → Cache with short TTL
                  ├─ Minutes → Standard caching
                  ├─ Hours → CDN appropriate
                  └─ Days → Static hosting
```

</div>

## Common Misconceptions

### ❌ "5G/6G will eliminate latency"
**Reality**: Wireless adds latency, doesn't reduce speed of light

### ❌ "Quantum networking will be instant"
**Reality**: Information still can't exceed c

### ❌ "Better servers reduce network latency"
**Reality**: Processing ≠ propagation delay

### ❌ "Parallel requests eliminate latency"
**Reality**: Critical path still bound by physics

## Design Patterns

### 1. Edge Computing
Move computation to data rather than data to computation

### 2. Predictive Prefetching
Guess what users need before they ask

### 3. Regional Sharding
Keep related data in same geographic region

### 4. Eventual Consistency
Accept stale data to avoid round trips

## Real-World Applications

### CDN Architecture
```
User → Edge Server (5ms) → Origin (100ms)
         ↓
    Cached Content
```

### Multi-Region Databases
```
Write to local region → Async replicate globally
Read from local replica → Avoid cross-region latency
```

### Video Streaming
```
Adaptive bitrate based on RTT measurements
Buffer ahead based on latency predictions
```

<div class="truth-box">

**Counter-Intuitive Truth 💡**

Adding more servers can INCREASE latency if it adds more hops. The fastest distributed system is often the one with fewer, better-placed nodes.

</div>

## Measuring Latency

### Key Metrics

- **Average**: Misleading for user experience
- **Median (P50)**: Typical user experience
- **P95/P99**: Tail latency, worst case
- **P99.9**: The pathological cases

### Tools & Techniques

```bash
# Basic latency test
ping -c 10 google.com

# Trace route path
traceroute google.com

# Application-level timing
curl -w "@curl-format.txt" -o /dev/null -s https://example.com
```

## Related Concepts

- **[Axiom 2: Capacity](../axiom-2-capacity/index.md)**: Latency increases with load
- **[Axiom 5: Coordination](../axiom-5-coordination/index.md)**: Consensus requires multiple round trips
- **[Work Distribution](../../part2-pillars/pillar-1-work/index.md)**: Routing affects latency

## Key Takeaways

!!! success "Remember"
    
    1. **Physics sets the floor** - You can approach but never beat light speed
    2. **Distance equals delay** - Geography matters in system design
    3. **Cache or suffer** - Move data close to users
    4. **Measure percentiles** - Averages hide the pain
    5. **Design for physics** - Work with constraints, not against them

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Latency Examples & Failures](examples.md) →
    
    **Practice**: [Latency Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 2: Finite Capacity](../axiom-2-capacity/index.md) →
    
    **Jump to**: [Part II: Pillars](../../part2-pillars/index.md) | [Tools](../../tools/latency-calculator.md)