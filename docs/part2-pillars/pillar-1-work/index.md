# Pillar I: Distribution of Work

!!! info "Prerequisites"
    - Completed [Part I: Axioms](../../part1-axioms/index.md)
    - Understanding of [Axiom 2: Capacity](../../part1-axioms/axiom-2-capacity/index.md)
    - Familiarity with [Axiom 3: Failure](../../part1-axioms/axiom-3-failure/index.md)

!!! tip "Quick Navigation"
    [← Part II Overview](../index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Distribution of State](../pillar-2-state/index.md)

!!! target "Learning Objective"
    Master the art of spreading computation without spreading complexity.

## Core Concept

<div class="axiom-box">

**First Principle of Work Distribution**:

```
Work should flow to where it can be processed most efficiently,
considering:
- Physical location (latency)
- Available capacity
- Required resources
- Failure domains
```

</div>

## The Statelessness Imperative

<div class="comparison-box">

=== "Stateless Service Properties"
    ✅ Any request to any instance  
    ✅ Instances interchangeable  
    ✅ Horizontal scaling trivial  
    ✅ Failure recovery simple  
    ✅ Load balancing easy

=== "Stateful Service Properties"
    ❌ Requests tied to instances  
    ❌ Complex scaling (resharding)  
    ❌ Failure means data loss  
    ❌ Load balancing tricky  
    ❌ Coordination required

</div>

## Work Distribution Patterns Hierarchy

<div class="pattern-hierarchy">

```
Level 1: Random Distribution
- Round-robin
- Random selection
- DNS load balancing
Efficiency: 60-70%

Level 2: Smart Distribution
- Least connections
- Weighted round-robin
- Response time based
Efficiency: 70-85%

Level 3: Affinity-Based
- Session affinity
- Consistent hashing
- Geographic routing
Efficiency: 80-90%

Level 4: Adaptive Distribution
- Predictive routing
- Cost-aware placement
- SLO-based routing
Efficiency: 90-95%
```

</div>

## The Autoscaling Mathematics

<div class="formula-box">

```
Optimal Instance Count = ceil(
    (Arrival Rate × Processing Time) / 
    (Target Utilization)
)

Example:
- Arrival: 1000 requests/second
- Processing: 100ms/request
- Target utilization: 70%

Instances = ceil((1000 × 0.1) / 0.7) = ceil(142.8) = 143
```

</div>

## Autoscaling Response Curves

<div class="graph-box">

```
Instances
    ↑
150 |            ┌─────────── (Overprovisioned)
    |          ╱
100 |        ╱─── (Ideal)
    |      ╱
 50 |    ╱╱ ← (Reactive scaling)
    |  ╱╱
  0 |╱________________________
    0   500   1000   1500  Load (req/s)
```

</div>

## Work Distribution Anti-Patterns

<div class="anti-pattern-box">

**1. Hot Shard Problem**:
```
Hash(UserID) % N can create:
- Celebrity user → overloaded shard
- Power law distribution → uneven load
Fix: Virtual shards, consistent hashing
```

**2. Thundering Herd**:
```
All instances start simultaneously:
- Cache empty → database overload
- Health checks → false failures
Fix: Staggered starts, cache priming
```

**3. Work Duplication**:
```
Multiple workers process same item:
- No coordination → wasted work
- Optimistic locking → conflict storms
Fix: Work stealing, leases
```

</div>

## The Control Theory of Autoscaling

<div class="control-diagram">

```
                     Target
                       ↓
Error = Target - Current
         ↓
    PID Controller
         ↓
Scale Decision = Kp×Error + Ki×∫Error + Kd×(dError/dt)
         ↓
    Add/Remove Instances
         ↓
    Measure Current ←────┘
```

</div>

## Autoscaling Strategies Compared

| Strategy | Response Time | Stability | Cost |
|----------|---------------|-----------|------|
| Reactive | Slow (minutes) | Good | Low |
| Predictive | Fast (seconds) | Medium | Medium |
| Scheduled | Instant | High | Medium |
| ML-based | Fast | Low-Med | High |

## Back-Pressure Mechanisms

<div class="mechanism-box">

**1. Token Bucket**:
```
Tokens added at fixed rate → [||||||||  ]
Request consumes token    → [|||||||   ]
No tokens = reject        → [          ] → 429 Error

Config:
- Bucket size: Burst capacity
- Refill rate: Sustained capacity
- Token cost: Per request or per byte
```

**2. Sliding Window**:
```
Time window: [===========]
              ↑         ↑
           10s ago    Now

Requests in window: 847/1000 allowed
New request: Check if under limit
```

**3. Adaptive Concurrency (BBR-style)**:
```
Gradient descent on concurrency limit:
1. Measure: RTT and throughput
2. Probe: Increase limit slightly
3. Observe: Did throughput increase?
4. Adjust: If latency spiked, back off

Finds optimal concurrency automatically!
```

</div>

## Back-Pressure Propagation

<div class="flow-diagram">

```
User → API Gateway → Service A → Service B → Database
  ↑        ↑            ↑           ↑          ↑
  └────────┴────────────┴───────────┴──────────┘
         Back-pressure flows upstream
```

</div>

<div class="truth-box">

**Counter-Intuitive Truth 💡**

Perfect work distribution is often worse than good-enough distribution. The coordination cost of achieving perfect balance can exceed the efficiency gains. Aim for "roughly right" rather than "exactly perfect."

</div>

## Common Back-Pressure Mistakes

!!! warning "Avoid These"
    
    1. **No Timeout Coordination**: Upstream timeout < downstream
    2. **Buffer Bloat**: Queues too large, hide problems
    3. **Unfair Rejection**: No priority/fairness
    4. **No Gradient**: Binary accept/reject vs gradual

## Related Concepts

- **[Axiom 2: Capacity](../../part1-axioms/axiom-2-capacity/index.md)**: Work distribution manages finite capacity
- **[Axiom 3: Failure](../../part1-axioms/axiom-3-failure/index.md)**: Distribution creates failure domains
- **[Axiom 4: Concurrency](../../part1-axioms/axiom-4-concurrency/index.md)**: Parallel work needs coordination

## Key Takeaways

!!! success "Remember"
    
    1. **Stateless scales, stateful struggles** - Design for statelessness
    2. **Work flows like water** - It finds the path of least resistance
    3. **Back-pressure prevents collapse** - Build it in early
    4. **Perfect balance is expensive** - Good enough is often better
    5. **Autoscaling needs damping** - Or it oscillates wildly

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Work Distribution Examples](examples.md) →
    
    **Practice**: [Work Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of State](../pillar-2-state/index.md) →
    
    **Jump to**: [Part II Overview](../index.md) | [Axioms](../../part1-axioms/index.md)