---
title: Fault Tolerance Pattern
description: Building systems that continue operating properly despite failures of components
type: pattern
category: resilience
difficulty: intermediate
reading_time: 15 min
prerequisites:
  - failure-modes
  - redundancy-basics
  - error-handling
excellence_tier: silver
pattern_status: recommended
introduced: 1980-01
current_relevance: mainstream
essential_question: How do we build systems that continue operating correctly even when components fail?
tagline: Keep systems running despite component failures through redundancy and recovery
trade_offs:
  pros:
    - "Maintains service availability during failures"
    - "Prevents data loss through redundancy"
    - "Enables maintenance without downtime"
  cons:
    - "Significant cost overhead for redundancy"
    - "Increased system complexity"
    - "Potential performance impact from checks"
best_for: "Mission-critical systems, financial services, and any system requiring high availability"
related_laws: [law1-failure, law3-emergence, law7-economics]
related_pillars: [work, state, control]
---

# Fault Tolerance Pattern

!!! info "🥈 Silver Tier Pattern"
    **Keep systems running despite failures** • Foundation for high-availability architectures
    
    Comprehensive approach to building resilient systems through redundancy, isolation, and recovery. While essential for critical systems, the cost and complexity require careful consideration.
    
    **Best For:** Financial systems, healthcare platforms, critical infrastructure

## Essential Question

**How do we build systems that continue operating correctly even when components fail?**

## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| Mission-critical systems | Payment processing | Zero downtime requirement |
| Life safety systems | Medical devices, aviation | Failure means danger |
| High-value transactions | Trading platforms | Each second costs money |
| Regulatory compliance | Banking systems | Uptime SLAs required |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| Prototypes/MVPs | Over-engineering | Simple error handling |
| Read-only systems | Lower risk | Basic retry logic |
| Batch processing | Can restart | Checkpoint/resume |
| Cost-sensitive apps | Expensive redundancy | Best-effort approach |

## Level 1: Intuition (5 min) {#intuition}

### The Airplane Engine Analogy

```mermaid
graph TB
    subgraph "Single Engine = Single Point of Failure"
        P1[Plane] --> E1[Engine]
        E1 --> X[❌ Crash]
    end
    
    subgraph "Dual Engines = Fault Tolerance"
        P2[Plane] --> E2[Engine 1]
        P2 --> E3[Engine 2]
        E2 --> F[✈️ Keep Flying]
        E3 --> F
    end
    
    style X fill:#ff6b6b,stroke:#c92a2a
    style F fill:#51cf66,stroke:#2f9e44
```

### Core Insight
> **Key Takeaway:** Fault tolerance = Redundancy + Isolation + Detection + Recovery. No single failure should take down the system.

## Level 2: Foundation (10 min) {#foundation}

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens Without Fault Tolerance</h4>

**Knight Capital, 2012**: A single faulty software deployment caused uncontrolled trading. In 45 minutes, the company lost $440 million due to no fault isolation or circuit breakers.

**Impact**: Company nearly bankrupt, acquired at fraction of value, industry-wide regulatory changes
</div>

### Fault Tolerance Building Blocks

```mermaid
graph LR
    subgraph "Detection Layer"
        D1[Health Checks]
        D2[Monitoring]
        D3[Anomaly Detection]
    end
    
    subgraph "Prevention Layer"
        P1[Input Validation]
        P2[Rate Limiting]
        P3[Timeouts]
    end
    
    subgraph "Isolation Layer"
        I1[Bulkheads]
        I2[Circuit Breakers]
        I3[Failure Domains]
    end
    
    subgraph "Recovery Layer"
        R1[Retry Logic]
        R2[Failover]
        R3[Rollback]
    end
    
    D1 --> P1 --> I1 --> R1
    
    classDef detection fill:#e3f2fd,stroke:#1976d2
    classDef prevention fill:#f3e5f5,stroke:#7b1fa2
    classDef isolation fill:#fff3e0,stroke:#f57c00
    classDef recovery fill:#e8f5e9,stroke:#388e3c
    
    class D1,D2,D3 detection
    class P1,P2,P3 prevention
    class I1,I2,I3 isolation
    class R1,R2,R3 recovery
```

### Redundancy Models Comparison

| Model | Setup | Availability | Cost | Use Case |
|-------|-------|--------------|------|----------|
| **Active-Active** | Both process requests | 99.99% | 2x | Zero downtime required |
| **Active-Passive** | Standby ready | 99.9% | 1.5x | Cost-conscious HA |
| **N+1** | 1 spare for N units | 99.5% | 1.2x | Hardware redundancy |
| **N+M** | M spares for N units | 99.95% | 1.3x | Large clusters |

## Level 3: Deep Dive (15 min) {#deep-dive}

### Fault Detection & Response Matrix

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Degraded: Performance Drop
    Healthy --> Suspect: Missed Heartbeat
    Suspect --> Failed: Threshold Exceeded
    Suspect --> Healthy: Recovery
    Degraded --> Failed: Critical Threshold
    Degraded --> Healthy: Auto-healing
    Failed --> Isolating: Fault Detected
    Isolating --> Recovering: Isolation Complete
    Recovering --> Healthy: Recovery Success
    Recovering --> Failed: Recovery Failed
    
    note right of Degraded: Actions:<br/>- Alert ops<br/>- Reduce load<br/>- Start backup
    note right of Failed: Actions:<br/>- Stop traffic<br/>- Isolate component<br/>- Trigger failover
```

### Implementation Strategies

| Strategy | Detection Time | Recovery Time | Data Loss | Complexity |
|----------|---------------|---------------|-----------|------------|
| **Heartbeat + Restart** | 10-30s | 1-5 min | Possible | Low |
| **State Replication** | 1-5s | < 30s | Minimal | Medium |
| **Event Sourcing** | Real-time | < 10s | None | High |
| **Consensus (Raft)** | < 1s | < 5s | None | Very High |

### Common Pitfalls

<div class="decision-box">
<h4>⚠️ Avoid These Mistakes</h4>

1. **Cascade failures**: One failure triggers another → Use circuit breakers between components
2. **Split-brain**: Multiple masters during partition → Implement proper quorum/fencing
3. **Retry storms**: Aggressive retries overwhelm → Exponential backoff with jitter
4. **Silent failures**: Errors hidden/ignored → Fail fast with clear error propagation
</div>

## Level 4: Expert (20 min) {#expert}

### Multi-Layer Fault Tolerance Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1[Client Retry]
        C2[Client Cache]
        C3[Circuit Breaker]
    end
    
    subgraph "API Gateway"
        G1[Rate Limiting]
        G2[Request Routing]
        G3[Fallback Responses]
    end
    
    subgraph "Service Mesh"
        S1[Service A]
        S2[Service A Replica]
        S3[Service B]
        S4[Service B Replica]
        CB[Mesh Circuit Breaker]
    end
    
    subgraph "Data Layer"
        D1[Primary DB]
        D2[Replica DB]
        D3[Cache Layer]
        D4[Message Queue]
    end
    
    C1 --> G1
    G1 --> CB
    CB --> S1
    CB --> S2
    S1 --> D1
    S2 --> D2
    
    style C3 fill:#ff6b6b,stroke:#c92a2a
    style CB fill:#ff6b6b,stroke:#c92a2a
    
    classDef primary fill:#5448C8,stroke:#3f33a6,color:#fff
    classDef replica fill:#94a3b8,stroke:#64748b
    
    class S1,S3,D1 primary
    class S2,S4,D2 replica
```

### Fault Tolerance Patterns Stack

| Layer | Pattern | Purpose | Example |
|-------|---------|---------|---------|
| **Request** | Retry + Timeout | Handle transient failures | 3 retries with exponential backoff |
| **Circuit** | Circuit Breaker | Prevent cascade failures | Open after 5 failures in 10s |
| **Resource** | Bulkhead | Isolate resources | Separate thread pools per service |
| **Data** | Replication | Prevent data loss | Master-slave with <1s lag |
| **Service** | Health Checks | Detect failures | HTTP /health every 10s |

### Advanced Recovery Strategies

```yaml
recovery_strategies:
  checkpoint_restore:
    checkpoint_interval: 5m
    storage: distributed_fs
    restore_time: < 30s
    
  state_machine_replication:
    consensus: raft
    nodes: 5
    fault_tolerance: 2
    
  event_sourcing:
    event_store: kafka
    replay_speed: 100k_events/sec
    snapshot_interval: 1000_events
```

## Level 5: Mastery (25 min) {#mastery}

### Real-World Case Studies

<div class="truth-box">
<h4>💡 Netflix's Fault Tolerance Architecture</h4>

**Challenge**: Maintain streaming during any failure scenario

**Implementation**: 
- Hystrix circuit breakers on every service call
- Regional failover with <1 minute switchover
- Chaos Monkey randomly killing instances
- Fallback to cached content during outages

**Results**: 
- 99.99% availability globally
- Survived entire AWS region failures
- Reduced incident impact by 90%
- Built culture of resilience

**Key Learning**: Test fault tolerance continuously - "The best way to avoid failure is to fail constantly"
</div>

### Fault Tolerance Cost Analysis

| Approach | Redundancy | Availability | Monthly Cost | Cost per 9 |
|----------|------------|--------------|--------------|------------|
| **Single Instance** | None | 99% | $100 | $100 |
| **Active-Passive** | 2x | 99.9% | $150 | $50 |
| **Active-Active** | 2x | 99.99% | $200 | $20 |
| **Multi-Region** | 3x | 99.999% | $300 | $10 |

### Testing Fault Tolerance

```mermaid
graph LR
    subgraph "Chaos Testing Levels"
        L1[Component Failure<br/>Kill processes]
        L2[Resource Pressure<br/>CPU/Memory stress]
        L3[Network Chaos<br/>Latency/Partition]
        L4[Region Failure<br/>Full DC down]
    end
    
    L1 -->|Weekly| T1[Automated]
    L2 -->|Daily| T2[Automated]
    L3 -->|Weekly| T3[Controlled]
    L4 -->|Monthly| T4[Planned]
    
    style L4 fill:#ff6b6b,stroke:#c92a2a
```

## Quick Reference

### Decision Flowchart

```mermaid
graph TD
    A[System Criticality?] --> B{Mission Critical?}
    B -->|Yes| C[Full Fault Tolerance]
    B -->|No| D{High Value?}
    
    C --> E[Active-Active<br/>Multi-Region<br/>Zero RPO]
    
    D -->|Yes| F[Selective FT<br/>Key Components]
    D -->|No| G[Basic Resilience<br/>Retry + Timeout]
    
    F --> H[Active-Passive<br/>Circuit Breakers<br/>Regional]
    
    classDef critical fill:#ff6b6b,stroke:#c92a2a
    classDef important fill:#4dabf7,stroke:#339af0
    classDef basic fill:#69db7c,stroke:#51cf66
    
    class C,E critical
    class D,F,H important
    class G basic
```

### Implementation Checklist

**Pre-Implementation**
- [ ] Identify failure modes (FMEA analysis)
- [ ] Define availability targets (SLOs)
- [ ] Map critical paths
- [ ] Design redundancy strategy

**Implementation**
- [ ] Add health checks at all levels
- [ ] Implement circuit breakers
- [ ] Set up replication/backups
- [ ] Create runbooks

**Post-Implementation**
- [ ] Regular chaos testing
- [ ] Monitor error budgets
- [ ] Practice failure scenarios
- [ ] Review and improve

### Related Resources

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **Related Patterns**
    
    ---
    
    - [Circuit Breaker](./circuit-breaker.md) - Prevent cascade failures
    - [Bulkhead](./bulkhead.md) - Isolate failures
    - [Retry](./retry-backoff.md) - Handle transient failures

- :material-flask:{ .lg .middle } **Fundamental Laws**
    
    ---
    
    - [Law 1: Correlated Failure](../../part1-axioms/law1-failure/) - Design independent failure domains
    - [Law 3: Emergent Chaos](../../part1-axioms/law3-emergence/) - Complex failure modes
    - [Law 7: Economic Reality](../../part1-axioms/law7-economics/) - Cost vs. availability trade-offs

</div>