# Axiom 3: Partial Failure

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: In distributed systems, failure is partial, not binary.
  </div>
</div>

## Core Principle

```
Monolithic Failure:  Works OR Dead (binary)
Distributed Failure: Works AND Broken (superposition)

A distributed system is one where a machine you've
never heard of can cause your app to fail.
```

## 🎬 Failure Vignette: The Retry Storm of 2022

```
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
Fix: Circuit breakers, bulkheads, adaptive timeouts
```

## The Failure Boundary Matrix

```
Failure Domain    Blast Radius    Recovery Time    Example
--------------    ------------    -------------    -------
Process           1 container     Seconds          OOM kill
Container         1 pod           Seconds          Crash
Pod               1 service       Minutes          Node drain
Node              N pods          Minutes          Hardware
Rack              1 AZ %          Minutes          Switch fail
Zone              1 region %      Hours            Power loss
Region            Global %        Hours            Fiber cut
Provider          Everything      Days             AWS outage
```

## Partial Failure Patterns

1. **Slow Failure**: Works but 10x slower
2. **Intermittent**: Fails 1% of requests randomly
3. **Degraded**: Returns stale/partial data
4. **Asymmetric**: A can talk to B, B can't talk to A
5. **Split Brain**: Two nodes think they're primary
6. **Gray Failure**: Appears healthy to monitors, broken to users

## 🎯 Decision Framework: Isolation Strategy

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

## Probability Math for Partial Failures

```
P(system works) = P(all critical components work)

Series (AND): P = P₁ × P₂ × P₃
Parallel (OR): P = 1 - (1-P₁) × (1-P₂) × (1-P₃)

Example: 3 replicas, each 99% available
- Need all 3: 0.99³ = 97% available (worse!)
- Need any 1: 1 - 0.01³ = 99.999% (better!)
```

## 🔧 Try This: Chaos Experiment

```bash
# Simulate partial network failure (Linux)
# Add 200ms delay to 25% of packets
sudo tc qdisc add dev eth0 root netem delay 200ms 50ms 25%

# Simulate packet loss
sudo tc qdisc add dev eth0 root netem loss 1%

# Clean up
sudo tc qdisc del dev eth0 root
```

## Counter-Intuitive Truth 💡

"A 99.9% reliable service called 1000 times has only 37% chance of success. Distributed systems multiply failures, not reliability."

## Failure-Domain Tree + Timeouts

### Visual Failure Hierarchy

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

### Timeout Strategy Matrix

```
Layer           Timeout    Rationale
-----           -------    ---------
User → LB       30s        Human patience limit
LB → Service    10s        Allow for retries
Service → Svc   3s         Intra-DC speed
Service → DB    1s         Query should be fast
Service → Cache 100ms      Cache must be faster
Circuit Open    5s         Recovery probe interval
```

### Timeout Coordination Problem

```
WRONG (Timeout Inversion):
Client timeout:   5s
Service timeout:  10s  
Result: Client gives up, service keeps trying

RIGHT (Nested Timeouts):
Client timeout:   10s
Service timeout:  3s
Retry budget:     3 × 3s = 9s < 10s ✓
```

## Cross-References

- → [Axiom 2: Capacity](../axiom2-capacity/index.md): How capacity limits trigger failures
<!-- - → [Circuit Breakers](../../patterns/circuit-breaker): Preventing cascade failures -->
- → [Axiom 4: Concurrency](../axiom4-concurrency/index.md): Race conditions in failure scenarios

---

**Next**: [Axiom 4: Concurrency →](../axiom4-concurrency/index.md)

*"In distributed systems, partial failure is the only kind of failure."*