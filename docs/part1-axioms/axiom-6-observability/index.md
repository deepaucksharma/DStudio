# Axiom 6: Observability

!!! info "Prerequisites"
    - [Axiom 5: Coordination](../axiom-5-coordination/index.md)
    - Understanding of monitoring basics
    - Experience debugging distributed systems

!!! tip "Quick Navigation"
    [← Axiom 5](../axiom-5-coordination/index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Human Interface](../axiom-7-human-interface/index.md)

!!! target "Learning Objective"
    You can't debug what you can't see; distributed systems multiply blindness.

## Core Concept

<div class="axiom-box">

**The Heisenberg Principle of Systems**:

```
Observer Effect: The act of observing a distributed system changes its behavior
- Logging adds latency
- Metrics consume CPU
- Tracing uses network bandwidth
- All observation has cost

Uncertainty Principle: You cannot simultaneously know:
- Exact state of all nodes (snapshot inconsistency)
- Complete ordering of all events (clock skew)
- Full causality chain (trace sampling)
```

</div>

## The Three Pillars of Observability

```yaml
1. LOGS (Events)
   What: Discrete events with context
   When: Something interesting happens
   Cost: High (storage, ingestion)
   Use: Debugging specific issues

2. METRICS (Aggregates)  
   What: Numeric values over time
   When: Continuous system health
   Cost: Low (pre-aggregated)
   Use: Alerting, capacity planning

3. TRACES (Flows)
   What: Request path through system
   When: Understanding latency, dependencies
   Cost: Medium (sampling required)
   Use: Performance optimization, debugging
```

## The Observability Cost Equation

```
Total Cost = Collection + Transport + Storage + Query + Human Analysis

Where:
- Collection: CPU/memory on each node
- Transport: Network bandwidth × distance
- Storage: Size × retention × replication
- Query: Compute for aggregation/search
- Human: Engineer time (highest cost!)

Example (1000-node cluster):
- Logs: 10GB/node/day = 10TB/day = $900/day
- Metrics: 1000 metrics × 10s × 8 bytes = 70GB/day = $7/day  
- Traces: 1% sampling × 1KB/trace × 1M req/sec = 860GB/day = $80/day
- Engineers debugging without good data = $10,000/day
```

<div class="decision-box">

**🎯 Decision Tree: What to Instrument**

```
START: Should I add observability here?
│
├─ Is this on the critical path?
│  └─ YES → Add metrics + traces
│
├─ Can this fail independently?
│  └─ YES → Add error logs + metrics
│
├─ Does this affect user experience?
│  └─ YES → Add SLI metrics
│
├─ Is this a resource boundary?
│  └─ YES → Add utilization metrics
│
├─ Is this a system boundary?
│  └─ YES → Add traces
│
└─ Otherwise → Sample logs only
```

</div>

## Anti-Patterns in Observability

1. **Log Everything**: Drowns signal in noise
2. **Average Everything**: Hides spikes and outliers
3. **Never Delete**: Infinite retention = infinite cost
4. **Dashboard Sprawl**: 1000 dashboards = 0 useful dashboards
5. **Alert Fatigue**: Everything pages = nothing matters
6. **No Correlation IDs**: Can't trace requests across services

## The RIGHT Observability

```yaml
For each service:
- 4 Golden Signals (see below)
- Error logs with context
- Trace sampling (adaptive)
- Business metrics that matter

Per request:
- Correlation ID
- User ID (if applicable)  
- Key business context
- Timing at boundaries

Retention policy:
- Raw logs: 7 days
- Metrics: 13 months (year-over-year)
- Traces: 30 days (sampled)
- Aggregates: Forever
```

## The Four Golden Signals

Every service should track these as the foundation:

### 1. LATENCY (Response Time)
- P50: Typical user experience
- P95: Power users / complex queries
- P99: Worst case that happens regularly
- P99.9: The pathological cases

### 2. TRAFFIC (Request Rate)
- Request rate (req/s)
- Bandwidth (MB/s)
- Active connections
- Request types distribution

### 3. ERRORS (Failure Rate)
- Client errors (4xx): Not your fault, but monitor
- Server errors (5xx): Your fault, alert!
- Timeout errors: Often capacity issues
- Business errors: Valid but failed operations

### 4. SATURATION (Resource Usage)
- CPU: First to saturate usually
- Memory: Causes GC pressure
- Network: Often forgotten
- Disk I/O: Database bottleneck
- Application-specific: Thread pools, connections

<div class="dashboard-box">

```
┌─────────────────────── Service Health Dashboard ───────────────────────┐
│                                                                         │
│  1. LATENCY (Response Time)                                           │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  P50: 45ms  P95: 120ms  P99: 450ms  P99.9: 1.2s           │    │
│  │  ▁▂▁▂▃▂▁▂▁▂▃▄▅▄▃▂▁▂▁▂▃▂▁▂ ← Live graph               │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  2. TRAFFIC (Request Rate)                                            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Current: 8.5K req/s  Peak today: 12K req/s                │    │
│  │  ████████████▌               Capacity: 15K req/s           │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  3. ERRORS (Failure Rate)                                             │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Rate: 0.12%  SLO: <0.1%  🔴 VIOLATING SLO                │    │
│  │  Top errors: [504 Gateway Timeout: 0.08%]                  │    │
│  │              [429 Too Many Requests: 0.03%]                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  4. SATURATION (Resource Usage)                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  CPU: ████████░░ 78%    Memory: ██████░░░░ 62%           │    │
│  │  Disk I/O: ███░░░░░░░ 31%   Network: █████░░░░░ 53%      │    │
│  │  Thread Pool: ████████░░ 81% ⚠️                           │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

</div>

## Observability Trade-offs

### Signal vs Noise
- More data ≠ better observability
- Focus on actionable insights
- Sample intelligently

### Cost vs Coverage
- 100% coverage is prohibitively expensive
- Use sampling for high-volume data
- Keep aggregates, discard raw data

### Real-time vs Historical
- Real-time costs more
- Most debugging needs recent data
- Archive older data cheaply

<div class="truth-box">

**Counter-Intuitive Truth 💡**

The best observability often comes from less data, not more. A few well-chosen metrics beat thousands of logs. Quality over quantity.

</div>

## Related Concepts

- **[Axiom 3: Partial Failure](../axiom-3-failure/index.md)**: Need observability to detect
- **[Axiom 7: Human Interface](../axiom-7-human-interface/index.md)**: Humans consume observability
- **[Control Patterns](../../part2-pillars/pillar-4-control/index.md)**: Observability enables control

## Key Takeaways

!!! success "Remember"
    
    1. **Observer effect is real** - Monitoring impacts performance
    2. **Three pillars complement** - Logs, metrics, traces together
    3. **Cost grows exponentially** - Be selective in what you observe
    4. **Averages lie** - Always use percentiles
    5. **Correlation IDs are essential** - Thread the needle across services

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Observability Examples & Failures](examples.md) →
    
    **Practice**: [Observability Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 7: Human Interface](../axiom-7-human-interface/index.md) →
    
    **Jump to**: [Monitoring Tools](../../tools/monitoring-setup.md) | [Part II](../../part2-pillars/index.md)