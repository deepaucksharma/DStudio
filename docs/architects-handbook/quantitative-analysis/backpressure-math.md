# Backpressure Mathematics

## Overview

Backpressure is a flow control mechanism that prevents system overload by propagating capacity constraints upstream. This page explores the mathematical models underlying backpressure systems.

## Core Concepts

### Flow Control Theory

Backpressure ensures that:
- Producers slow down when consumers can't keep up
- Buffers don't overflow
- System remains stable under load

### Mathematical Foundation

Based on queueing theory and control systems:
- **Arrival rate**: λ (lambda)
- **Service rate**: μ (mu)
- **Utilization**: ρ = λ/μ
- **Stability condition**: ρ < 1

## Backpressure Models

### Token Bucket Algorithm

```
Tokens added at rate: r tokens/second
Bucket capacity: b tokens
Data allowed if tokens ≥ packet_size
```

**Mathematics:**
- Max burst size: b
- Sustained rate: r
- Time to accumulate n tokens: n/r

### Leaky Bucket Algorithm

```
Input rate: variable
Output rate: constant r
Buffer size: b
```

**Overflow condition:**
- Input > Output for time t
- Accumulated excess > b

### Credit-Based Flow Control

```
Credits = Buffer_Space_Available
Send_Window = min(Credits, Congestion_Window)
```

**Credit dynamics:**
- Credits decrease on send
- Credits increase on ACK
- Prevents buffer overflow

## Mathematical Analysis

### Little's Law Application

For backpressure systems:
```
L = λ × W
```
Where:
- L = number in system
- λ = arrival rate
- W = time in system

**With backpressure:**
- λ_effective = min(λ_offered, μ)
- System remains stable

### Queue Growth Rate

Without backpressure:
```
dQ/dt = λ - μ
```

With backpressure:
```
dQ/dt = min(λ, μ + ε) - μ
```
Where ε is the backpressure threshold.

## Backpressure Strategies

### Static Backpressure

**High/Low Watermarks:**
```
if queue_size > high_watermark:
    stop_accepting()
elif queue_size < low_watermark:
    start_accepting()
```

**Hysteresis gap:**
- Prevents oscillation
- Gap = high_watermark - low_watermark
- Typical: 20-30% of capacity

### Dynamic Backpressure

**Adaptive thresholds:**
```
threshold = α × capacity × (1 - ρ)
```
Where:
- α = aggressiveness factor (0.5-0.9)
- ρ = current utilization

### Propagation Models

**Hop-by-hop:**
```
Delay = Σ(processing_time_i + propagation_delay_i)
Total latency = n × avg_hop_delay
```

**End-to-end:**
```
RTT = 2 × (propagation_delay + processing_delay)
Feedback latency = RTT/2
```

## Performance Metrics

### Throughput Under Backpressure

```
Throughput = min(λ, μ) × (1 - P_drop)
```
Where P_drop is the drop probability.

### Latency Impact

**Without backpressure:**
- Latency → ∞ as ρ → 1

**With backpressure:**
- Latency bounded by: W_max = B/μ
- Where B is buffer size

### Buffer Sizing

**Bandwidth-Delay Product:**
```
Buffer_Size = Bandwidth × RTT
```

**With backpressure:**
```
Effective_Buffer = Buffer_Size × (1 - backpressure_threshold)
```

## Implementation Models

### Reactive Streams

**Demand-based:**
```
Publisher: can_send = subscriber_demand > 0
Subscriber: demand = buffer_capacity - buffer_used
```

**Mathematics:**
- Send rate ≤ demand_rate
- Buffer occupancy ≤ capacity

### TCP Congestion Control

**Window-based:**
```
cwnd = min(rwnd, cwnd)
send_rate = cwnd / RTT
```

**Backpressure via:**
- Receive window (rwnd)
- Congestion window (cwnd)
- ACK pacing

### Credit Systems

**Initial credits:**
```
C_0 = Buffer_Size
```

**Credit dynamics:**
```
C(t+1) = C(t) - sent(t) + freed(t)
```

## Stability Analysis

### Lyapunov Function

For queue stability:
```
V(Q) = (1/2) × Q²
```

**Drift:**
```
ΔV = E[V(Q(t+1)) - V(Q(t))]
```

**Stable if:** ΔV < 0 for Q > threshold

### Control Theory

**Transfer function:**
```
H(s) = K / (1 + sT)
```
Where:
- K = gain
- T = time constant

**Stability criterion:**
- All poles in left half-plane
- Phase margin > 45°

## Real-World Examples

### Kafka Backpressure

```
Consumer lag = Latest_Offset - Consumer_Offset
Backpressure when: lag > threshold
Action: Pause fetching
```

### Akka Streams

```
Strategy: Pull-based
Demand signaling: Request(n)
Buffer size: 16 (default)
Overflow strategy: Backpressure/Drop/Fail
```

### Network Switches

```
Pause frames (802.3x)
Priority flow control (802.1Qbb)
ECN marking threshold: 70-80% buffer
```

## Design Calculations

### Buffer Sizing

**For stability:**
```
Buffer_Size ≥ Bandwidth × RTT × (1 + α)
```
Where α is safety margin (0.2-0.5)

### Watermark Settings

**High watermark:**
```
HWM = Buffer_Size × 0.8
```

**Low watermark:**
```
LWM = Buffer_Size × 0.6
```

**Rationale:**
- 20% headroom for bursts
- 20% hysteresis gap

### Response Time

**Backpressure activation:**
```
T_activate = (HWM - current) / (λ - μ)
```

**System recovery:**
```
T_recover = (current - LWM) / (μ - λ)
```

## Common Pitfalls

### Deadlock Scenarios

**Circular dependencies:**
```
A waits for B's buffer
B waits for A's buffer
Result: Deadlock
```

**Prevention:**
- Timeout mechanisms
- Priority ordering
- Deadlock detection

### Livelock Conditions

**Oscillating backpressure:**
- Rapid on/off cycling
- No forward progress
- Solution: Hysteresis

### Cascade Effects

**Backpressure propagation:**
```
Delay_total = Σ(delay_i) × amplification_factor
```

**Mitigation:**
- Circuit breakers
- Bulkheads
- Timeout budgets

## Advanced Topics

### Multi-Level Backpressure

```
Level 1: Memory pressure (90%)
Level 2: CPU pressure (80%)
Level 3: Disk I/O pressure (70%)
Combined: min(all levels)
```

### Predictive Backpressure

**Using forecasting:**
```
λ_predicted(t+Δt) = α×λ(t) + (1-α)×λ_avg
Trigger if: λ_predicted > μ
```

### Fairness Algorithms

**Weighted fair queuing:**
```
Service_rate_i = weight_i × total_capacity / Σ(weights)
```

## Related Topics

- [Queueing Theory](/architects-handbook/quantitative-analysis/queueing-models/)
- [Flow Control Patterns](../pattern-library/scaling/backpressure.md)
- [Little's Law](/architects-handbook/quantitative-analysis/littles-law/)
- [Performance Modeling](/architects-handbook/quantitative-analysis/performance-modeling/)