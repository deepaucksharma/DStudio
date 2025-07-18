# Axiom 3: Partial Failure

!!! info "Prerequisites"
    - [Axiom 1: Latency](../axiom-1-latency/index.md)
    - [Axiom 2: Capacity](../axiom-2-capacity/index.md)
    - Understanding of distributed systems basics

!!! tip "Quick Navigation"
    [← Axiom 2](../axiom-2-capacity/index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Concurrency](../axiom-4-concurrency/index.md)

!!! target "Learning Objective"
    In distributed systems, failure is partial, not binary.

## Metaphysical Foundation

<div class="axiom-box">

### Deductive Origin

This axiom emerges necessarily from **Axiom Zero-B: Time is Asymmetric** (specifically, the Law of Entropy)

**The Chain of Reasoning**:
1. The Second Law of Thermodynamics: Entropy always increases
2. A distributed system is a highly ordered, low-entropy configuration
3. Without constant energy input, systems decay toward disorder
4. Components fail independently at different rates
5. **Therefore**: Failure is the default state; functioning is the exception

**The Architect's Burden**: You are not preventing failure—that would violate thermodynamics. You are managing the inevitable decay, creating pockets of temporary order in an ocean of entropy.

</div>

## Core Concept

<div class="axiom-box">

**The Fundamental Difference:**

```
Monolithic Failure:  Works OR Dead (binary)
Distributed Failure: Works AND Broken (superposition)

"A distributed system is one where a machine you've
never heard of can cause your app to fail."
```

**Inevitable Consequences**:
- Failure is not IF but WHEN
- Perfect reliability is thermodynamically impossible
- The larger the system, the higher the failure rate
- Resilience requires continuous energy (maintenance)

</div>

## The Entropy Gradient

!!! quote "Thermodynamic Truth"
    Every component has a "failure potential energy" that increases over time. Like a ball rolling uphill, maintaining order requires constant work. Stop pushing, and the system rolls back to its natural state: broken.

## The Failure Boundary Matrix

| Failure Domain | Blast Radius | Recovery Time | Example |
|----------------|--------------|---------------|---------|
| **Process** | 1 container | Seconds | OOM kill |
| **Container** | 1 pod | Seconds | Crash |
| **Pod** | 1 service | Minutes | Node drain |
| **Node** | N pods | Minutes | Hardware |
| **Rack** | 1 AZ % | Minutes | Switch fail |
| **Zone** | 1 region % | Hours | Power loss |
| **Region** | Global % | Hours | Fiber cut |
| **Provider** | Everything | Days | AWS outage |

## Types of Partial Failures

1. **Slow Failure**: Works but 10x slower
2. **Intermittent**: Fails 1% of requests randomly
3. **Degraded**: Returns stale/partial data
4. **Asymmetric**: A can talk to B, B can't talk to A
5. **Split Brain**: Two nodes think they're primary
6. **Gray Failure**: Appears healthy to monitors, broken to users

<div class="decision-box">

**🎯 Decision Framework: Isolation Strategy**

```
DETECT: What indicates partial failure?
├─ Latency > p99 threshold
├─ Error rate > baseline
├─ Queue depth growing
└─ Health check flapping

ISOLATE: How to contain blast radius?
├─ Thread pool isolation (Hystrix pattern)
├─ Network segmentation (bulkheads)  
├─ Separate failure domains (AZs)
└─ Circuit breakers (fail fast)

RECOVER: How to heal?
├─ Retry with backoff
├─ Fallback to cache/default
├─ Degrade gracefully
└─ Shed load (drop requests)
```

</div>

## Probability Math for Partial Failures

```
P(system works) = P(all critical components work)

Series (AND): P = P₁ × P₂ × P₃
Parallel (OR): P = 1 - (1-P₁) × (1-P₂) × (1-P₃)

Example: 3 replicas, each 99% available
- Need all 3: 0.99³ = 97% available (worse!)
- Need any 1: 1 - 0.01³ = 99.999% (better!)
```

<div class="truth-box">

**Counter-Intuitive Truth 💡**

"A 99.9% reliable service called 1000 times has only 37% chance of success. Distributed systems multiply failures, not reliability."

</div>

## Visual Failure Hierarchy

```
                    System
                 ╱         ╲
            Region A      Region B
           ╱    |    ╲        |
        AZ1    AZ2    AZ3    AZ1
       ╱ |      |      |      |
    Rack1 R2    R1     R1     R1
    ╱ ╲   |     |      |      |
  N1  N2  N1    N1     N1     N1
  |   |   |     |      |      |
 Pod Pod Pod   Pod    Pod    Pod
```

## Timeout Strategy Matrix

| Layer | Timeout | Rationale |
|-------|---------|-----------|
| **User → LB** | 30s | Human patience limit |
| **LB → Service** | 10s | Allow for retries |
| **Service → Svc** | 3s | Intra-DC speed |
| **Service → DB** | 1s | Query should be fast |
| **Service → Cache** | 100ms | Cache must be faster |
| **Circuit Open** | 5s | Recovery probe interval |

## Timeout Coordination Problem

```yaml
WRONG (Timeout Inversion):
Client timeout:   5s
Service timeout:  10s  
Result: Client gives up, service keeps trying

RIGHT (Nested Timeouts):
Client timeout:   10s
Service timeout:  3s
Retry budget:     3 × 3s = 9s < 10s ✓
```

## Key Patterns for Handling Partial Failures

### 1. Circuit Breakers

Prevent cascade failures by failing fast when a dependency is unhealthy.

### 2. Bulkheads

Isolate failures to prevent them from affecting the entire system.

### 3. Timeouts & Deadlines

Bound the impact of slow operations.

### 4. Retries with Backoff

Recover from transient failures without overwhelming the system.

### 5. Graceful Degradation

Provide reduced functionality rather than complete failure.

## Common Anti-Patterns

### ❌ Treating Partial as Total

Assuming a slow response means the service is down.

### ❌ Retry Amplification

Retrying too aggressively, creating thundering herds.

### ❌ Timeout Inversion

Child timeouts longer than parent timeouts.

### ❌ Ignoring Gray Failures

Only monitoring binary up/down states.

## Related Concepts

- **[Axiom 2: Capacity](../axiom-2-capacity/index.md)**: Partial failures often stem from capacity issues
- **[Axiom 4: Concurrency](../axiom-4-concurrency/index.md)**: Race conditions cause partial states
- **[Truth Distribution](../../part2-pillars/pillar-3-truth/index.md)**: Managing state during failures

## Key Takeaways

!!! success "Remember"
    
    1. **Failure is a spectrum** - Not just up or down
    2. **Blast radius matters** - Contain failures with bulkheads
    3. **Detection is hard** - Gray failures hide from monitors
    4. **Timeouts cascade** - Coordinate them carefully
    5. **Plan for partial** - Design assuming components half-work

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Failure Examples & Stories](examples.md) →
    
    **Practice**: [Failure Handling Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 4: Concurrency](../axiom-4-concurrency/index.md) →
    
    **Jump to**: [Chaos Engineering Tools](../../tools/chaos-toolkit.md) | [Part II](../../part2-pillars/index.md)