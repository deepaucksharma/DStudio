---
category: architecture
current_relevance: niche
deprecation-reason: Consider modern alternatives for new implementations
description: Understanding the fundamental trade-offs in distributed systems design
difficulty: intermediate
educational-value: Important for understanding distributed systems theory but not
  directly actionable
essential_question: How do we structure our system architecture to leverage cap theorem?
excellence_tier: bronze
introduced: 2000-07
last-updated: 2025-01-23
modern-alternatives: []
modern-context:
- PACELC theorem provides more nuanced view
- Modern systems offer tunable consistency
- Cloud providers abstract many CAP concerns
pattern_status: use-with-caution
prerequisites: []
reading-time: 30 min
status: complete
tagline: Master cap theorem for distributed systems success
title: CAP Theorem
type: pattern
when-not-to-use: When working with single-node systems
when-to-use: When designing distributed systems architecture
---


## Essential Question
## When to Use / When NOT to Use

### When to Use

| Scenario | Why It Fits | Alternative If Not |
|----------|-------------|-------------------|
| High availability required | Pattern provides resilience | Consider simpler approach |
| Scalability is critical | Handles load distribution | Monolithic might suffice |
| Distributed coordination needed | Manages complexity | Centralized coordination |

### When NOT to Use

| Scenario | Why to Avoid | Better Alternative |
|----------|--------------|-------------------|
| Simple applications | Unnecessary complexity | Direct implementation |
| Low traffic systems | Overhead not justified | Basic architecture |
| Limited resources | High operational cost | Simpler patterns |
**How do we structure our system architecture to leverage cap theorem?**


# CAP Theorem

!!! info "🥉 Bronze Tier Pattern"
    **Educational concept, not actionable pattern**
    
    CAP theorem is important for understanding distributed systems theory but doesn't provide actionable guidance. Modern systems offer more nuanced approaches like tunable consistency and PACELC considerations.
    
    **For practical guidance, see:**
    - **[Tunable Consistency](../../pattern-library/data-management/tunable-consistency.md)** for flexible trade-offs
    - **[Consensus Patterns](../../pattern-library/coordination/consensus.md)** for agreement protocols
    - **[Multi-Region Architecture](../../pattern-library/scaling/multi-region.md)** for real-world CAP decisions

**You can't have your cake and eat it too - The fundamental trade-off in distributed systems**

> *"In a distributed system, you can have at most two of: Consistency, Availability, and Partition tolerance. Choose wisely."* - Eric Brewer

---

## Level 1: Intuition

### The Restaurant Chain Analogy

Imagine a restaurant chain with locations worldwide:
- **Consistency**: All locations have the same menu and prices
- **Availability**: Every location is always open
- **Partition Tolerance**: Locations operate even when they can't communicate

When the phone lines go down (network partition), each location must choose:
- Stay open with potentially outdated menus (AP - Available but Inconsistent)
- Close until communication restored (CP - Consistent but Unavailable)

### Visual Understanding



---

## Level 2: Foundation

### The Three Properties Explained

#### 1. Consistency (C)
All nodes see the same data at the same time. After a write completes, all subsequent reads will return that value.

#### 2. Availability (A)
Every request receives a response (without guarantee that it contains the most recent write).

#### 3. Partition Tolerance (P)
The system continues to operate despite network failures between nodes.

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```



---

## Interactive Decision Support Tools

### CAP Trade-off Decision Tree

### CAP Trade-off Calculator

| System Characteristic | CP Choice | AP Choice | Your Priority (1-10) |
|----------------------|-----------|-----------|---------------------|
| **Data Consistency** | ✅ Strong | ❌ Eventual | ___ |
| **Write Availability** | ❌ May Reject | ✅ Always Accept | ___ |
| **Read Availability** | ❌ May Timeout | ✅ Always Respond | ___ |
| **Latency** | 🟡 Higher | ✅ Lower | ___ |
| **Complexity** | 🟡 Medium | 🔴 High | ___ |
| **Data Loss Risk** | ✅ None | 🟡 Possible | ___ |
| **Conflict Resolution** | ✅ Automatic | 🔴 Manual | ___ |
| **Use Cases** | Financial, Inventory | Social, Analytics | |


**Score Calculation:**
- CP Score = (Consistency × 10) + (Data Loss × 8) - (Availability × 5)
- AP Score = (Availability × 10) + (Latency × 7) - (Consistency × 5)

### Consistency Model Selector

### Availability vs Consistency Trade-off Visualizer

---

## Level 3: Deep Dive

### Real-World CAP Implementations

#### CP Systems Example: Zookeeper/etcd

#### AP Systems Example: Cassandra

### Practical Implementation Patterns

#### 1. Tunable Consistency
Many systems allow you to tune consistency per operation:

| Operation | Consistency Level | Availability | Use Case |
|-----------|------------------|--------------|----------|
| Write ONE | Lowest | Highest | Logging, metrics |
| Write QUORUM | Medium | Medium | User data |
| Write ALL | Highest | Lowest | Critical config |
| Read ONE | Lowest | Highest | Cache warming |
| Read QUORUM | Medium | Medium | User queries |
| Read ALL | Highest | Lowest | Financial data |


#### 2. Hybrid Approaches

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```



---

## Level 4: Expert Considerations

### Beyond CAP: PACELC

PACELC extends CAP by considering latency:
- **If Partition** (P): Choose Availability (A) or Consistency (C)
- **Else** (E): Choose Latency (L) or Consistency (C)

### CAP in Modern Architectures

#### Microservices and CAP

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```



## Quick Reference

### Decision Matrix

### Comparison with Alternatives

| Aspect | CAP Theorem | PACELC | Tunable Consistency | CRDTs |
|--------|-------------|--------|-------------------|-------|
| Complexity | Simple | Medium | High | Very High |
| Practicality | Educational | High | Very High | Specialized |
| Latency Focus | No | Yes | Yes | Yes |
| Conflict Handling | None | Limited | Configurable | Automatic |
| When to use | Learning | Architecture design | Production systems | Collaborative apps |

#
## Performance Characteristics

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Latency** | 100ms | 20ms | 80% |
| **Throughput** | 1K/s | 10K/s | 10x |
| **Memory** | 1GB | 500MB | 50% |
| **CPU** | 80% | 40% | 50% |

## Implementation Checklist

**Pre-Implementation**
- [ ] Identified which data requires strong consistency
- [ ] Mapped network partition scenarios for your infrastructure
- [ ] Defined acceptable availability targets per service
- [ ] Chosen appropriate consistency models per use case

**Implementation**
- [ ] Implemented partition detection mechanisms
- [ ] Added graceful degradation during partitions
- [ ] Built conflict resolution strategies
- [ ] Added monitoring for consistency/availability metrics

**Post-Implementation**
- [ ] Tested partition scenarios in staging environment
- [ ] Trained team on CAP trade-offs and monitoring
- [ ] Documented consistency guarantees per API
- [ ] Established runbooks for partition handling

### Related Resources

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **Related Patterns**
    
    ---
    
    - [Eventual Consistency](../../pattern-library/data-management/eventual-consistency.md) - AP system implementation
    - [Consensus](../../pattern-library/coordination/consensus.md) - CP system coordination
    - [Circuit Breaker](../../pattern-library/resilience/circuit-breaker.md) - Partition handling

- :material-flask:{ .lg .middle } **Fundamental Laws**
    
    ---
    
    - [Law 2: Asynchronous Reality](../../core-principles/laws/law2/) - Network delays
    - [Law 3: Emergent Chaos](../../core-principles/laws/law3/) - Partition inevitability

- :material-pillar:{ .lg .middle } **Foundational Pillars**
    
    ---
    
    - [State Distribution](../../core-principles/pillars/state-distribution/) - Data consistency models
    - [Truth Distribution](../../core-principles/pillars/truth-distribution/) - Consensus mechanisms

- :material-tools:{ .lg .middle } **Modern Alternatives**
    
    ---
    
    - [PACELC Analysis Guide](../../excellence/guides/pacelc-analysis.md)
    - [Tunable Consistency Setup](../../excellence/guides/tunable-consistency.md)
    - [CRDT Implementation Guide](../../excellence/guides/crdt-setup.md)

</div>

---

