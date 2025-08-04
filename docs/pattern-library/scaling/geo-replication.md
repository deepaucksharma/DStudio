---
category: scaling
current_relevance: mainstream
description: Replicate data across geographical regions for global availability and
  disaster recovery
essential_question: How do we handle increasing load without sacrificing performance
  using geo-replication pattern?
excellence_tier: gold
introduced: 2007-05
modern_examples:
- company: Netflix
  implementation: Multi-region active-active deployment across 190+ countries
  scale: 200M+ subscribers with <100ms latency globally
- company: CockroachDB
  implementation: Geo-partitioned replicas with configurable replication zones
  scale: Serves global banks with 99.999% availability
- company: DynamoDB Global Tables
  implementation: Multi-master replication across all AWS regions
  scale: Petabytes of data with single-digit millisecond latency
pattern_status: recommended
production_checklist:
- Design conflict resolution strategy (LWW, CRDT, or custom)
- Configure replication topology (master-slave, multi-master, or hierarchical)
- Set up monitoring for replication lag across all regions
- Implement region failover with <5 minute RTO
- Plan for network partitions between regions
- Configure read/write routing based on user geography
- Test disaster recovery procedures quarterly
- Monitor cross-region bandwidth costs and optimize
tagline: Master geo-replication pattern for distributed systems success
title: Geo-Replication Pattern
---


# Geo-Replication Pattern

!!! success "🏆 Gold Standard Pattern"
    **Global Scale with Local Performance** • Netflix, CockroachDB, DynamoDB proven
    
    Essential for truly global applications, geo-replication enables Netflix to serve 200M+ subscribers across 190 countries with <100ms latency while providing disaster recovery and compliance capabilities.

## Essential Questions

!!! question "Critical Geo-Replication Decisions"
    1. **What's your consistency requirement?** Strong, Causal, Eventual, or Custom?
    2. **How will you handle conflicts?** Last-write-wins, CRDTs, or manual resolution?
    3. **What's your partition strategy?** Geographic, user-based, or data-type?
    4. **How much replication lag can you tolerate?** <100ms, <1s, or minutes?
    5. **What's your failover RTO?** Seconds, minutes, or hours?
    6. **Which regions need data residency?** GDPR, CCPA, or other compliance?

## When to Use / When NOT to Use

### Use Geo-Replication When:

| Indicator | Threshold | Example |
|-----------|-----------|---------|
| **Global Users** | >20% users outside home region | SaaS with international customers |
| **Latency Requirements** | <100ms response time needed | Real-time collaboration tools |
| **Availability Target** | >99.95% uptime required | Financial services, healthcare |
| **Disaster Recovery** | <1 hour RTO required | Mission-critical applications |
| **Compliance** | Data residency laws apply | GDPR, CCPA, financial regulations |

### DON'T Use When:

| Scenario | Why Avoid | Alternative |
|----------|-----------|-------------|
| **Single Region Users** | Unnecessary complexity | Single region + CDN |
| **Strong Consistency Required** | Physics limitations | Active-passive replication |
| **Budget Constraints** | 3-5x infrastructure cost | Read replicas only |
| **Small Dataset** | <100GB doesn't justify cost | Database backups |
| **Simple Apps** | MVP/prototype stage | Focus on core features first |

## Architecture Decision Matrix

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TD
    Start[Need Global Data?] --> Users{User Distribution?}
    
    Users -->|Regional| Regional[Multi-Region<br/>within Continent]
    Users -->|Global| Consistency{Consistency Need?}
    
    Consistency -->|Strong| Strong[Primary-Replica<br/>Synchronous]
    Consistency -->|Eventual| Eventual[Multi-Master<br/>Asynchronous]
    Consistency -->|Causal| Causal[Vector Clocks<br/>Dependency Tracking]
    
    Strong --> Latency1{Latency Tolerance?}
    Eventual --> Conflicts{Conflict Resolution?}
    
    Latency1 -->|<100ms| Quorum[Quorum Consensus<br/>Majority Replicas]
    Latency1 -->|>500ms| Chain[Chain Replication<br/>Sequential Updates]
    
    Conflicts -->|Automatic| CRDT[CRDTs<br/>Conflict-Free Types]
    Conflicts -->|Manual| LWW[Last-Write-Wins<br/>Timestamp Ordering]
    
    style Strong fill:#FF6B6B
    style Eventual fill:#4ECDC4
    style Causal fill:#45B7D1
    style CRDT fill:#96CEB4
```

</details>

## Core Replication Strategies

### Strategy Comparison Matrix

| Strategy | Write Latency | Consistency | Data Loss Risk | Complexity | Best For |
|----------|---------------|-------------|----------------|------------|----------|
| **Primary-Replica** | Low (single write) | Strong | Low | Medium | Financial data |
| **Multi-Master** | Low (local write) | Eventual | Medium | High | Social media |
| **Chain Replication** | Medium | Strong | Very Low | Medium | Log storage |
| **Quorum** | Medium | Strong | Low | High | Distributed databases |
| **CRDT** | Low | Eventual | None | Very High | Collaborative editing |

### Replication Topology Patterns

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Primary-Replica (Star)"
        P1[Primary US] --> R1[Replica EU]
        P1 --> R2[Replica Asia]
        P1 --> R3[Replica AU]
    end
    
    subgraph "Multi-Master (Mesh)"
        M1[Master US] <--> M2[Master EU]
        M2 <--> M3[Master Asia]
        M3 <--> M1
    end
    
    subgraph "Chain Replication"
        C1[Head US] --> C2[Middle EU] --> C3[Tail Asia]
        C3 -.->|ACK| C1
    end
    
    subgraph "Hierarchical"
        H1[Global Primary]
        H1 --> H2[Regional US]
        H1 --> H3[Regional EU]
        H2 --> H4[Local East]
        H2 --> H5[Local West]
    end
    
    style P1 fill:#FF6B6B
    style M1 fill:#4ECDC4
    style M2 fill:#4ECDC4
    style M3 fill:#4ECDC4
    style C1 fill:#45B7D1
```

</details>

## Geographic Latency Reality

### Inter-Region Network Latencies

| Route | Distance | Latency | Bandwidth | Cost/GB |
|-------|----------|---------|-----------|---------|
| **US East ↔ US West** | 4,500km | ~70ms | 100Gbps+ | $0.02 |
| **US East ↔ EU West** | 6,500km | ~80ms | 40Gbps | $0.05 |
| **US East ↔ Asia Pacific** | 17,000km | ~180ms | 10Gbps | $0.12 |
| **EU West ↔ Asia Pacific** | 12,000km | ~160ms | 20Gbps | $0.08 |
| **Within Region** | <2,000km | <20ms | 1Tbps+ | $0.01 |

### Consistency vs Latency Trade-offs

```mermaid
graph LR
    subgraph "Write Latency Impact"
        A[Synchronous<br/>300ms] -->|All regions ACK| B[Strong Consistency]
        C[Asynchronous<br/>5ms] -->|Local ACK only| D[Eventual Consistency]
        E[Quorum<br/>150ms] -->|Majority ACK| F[Tunable Consistency]
    end
    
    subgraph "Read Performance"
        B --> G[Reads can be stale<br/>until sync complete]
        D --> H[Reads always fast<br/>but may be stale]
        F --> I[Reads fast from majority<br/>consistent replicas]
    end
    
    style A fill:#FF6B6B
    style C fill:#4ECDC4
    style E fill:#FFD93D
```

## Conflict Resolution Strategies

### When Conflicts Occur

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

<details>
<summary>View implementation code</summary>

```mermaid
sequenceDiagram
    participant US as US User
    participant EU as EU User  
    participant USD as US Database
    participant EUD as EU Database
    
    Note over US,EUD: User profile: {name: "John", age: 25}
    
    US->>USD: Update age to 26
    EU->>EUD: Update name to "Johnny"
    
    USD-->>EUD: Replicate: age=26
    EUD-->>USD: Replicate: name="Johnny"
    
    Note over USD,EUD: CONFLICT: Different fields updated simultaneously
    
    rect rgb(255, 200, 200)
        USD->>USD: Apply resolution strategy
        EUD->>EUD: Apply resolution strategy
    end
    
    Note over USD,EUD: Final: {name: "Johnny", age: 26}
```

</details>

### Resolution Strategy Comparison

| Strategy | Complexity | Data Loss | Use Case | Example |
|----------|------------|-----------|----------|---------|
| **Last-Write-Wins** | Low | High | Simple KV stores | Redis, DynamoDB |
| **Vector Clocks** | Medium | Low | Version tracking | Riak, Voldemort |
| **CRDTs** | High | None | Collaborative apps | YJS, Automerge |
| **Application Logic** | Very High | None | Business rules | Custom resolution |
| **Manual Resolution** | Low | None | Critical data | Git merge conflicts |

### CRDT Examples for Common Data Types

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "G-Counter (Increment Only)"
        GC1[Node A: 5] --> GC3[Merge: max(5,3) = 5]
        GC2[Node B: 3] --> GC3
    end
    
    subgraph "PN-Counter (Inc/Dec)"
        PC1[Node A: +7, -2] --> PC3[Merge: (+10,-2) = 8]
        PC2[Node B: +3, -0] --> PC3
    end
    
    subgraph "OR-Set (Add/Remove)"
        OS1[Node A: {add:x, remove:y}] --> OS3[Merge: {x} ∪ {} = {x}]
        OS2[Node B: {add:z, remove:x}] --> OS3
    end
    
    subgraph "LWW-Register (Timestamped)"
        LW1[Node A: val=X, ts=100] --> LW3[Merge: latest timestamp wins]
        LW2[Node B: val=Y, ts=95] --> LW3
    end
```

</details>

## Production Implementation Patterns

### Netflix: Content Distribution Architecture

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Netflix Global CDN"
        Origin[Origin Servers<br/>US Central]
        
        subgraph "Regional Caches"
            US[US Edge Servers<br/>100+ locations]
            EU[EU Edge Servers<br/>50+ locations]  
            Asia[Asia Edge Servers<br/>30+ locations]
        end
        
        subgraph "ISP Caches"
            ISP1[Comcast Open Connect]
            ISP2[Verizon Open Connect]
            ISP3[Deutsche Telekom]
        end
        
        Origin --> US & EU & Asia
        US --> ISP1 & ISP2
        EU --> ISP3
        
        Users1[US Users] --> ISP1
        Users2[EU Users] --> ISP3
    end
    
    style Origin fill:#FF6B6B
    style US fill:#4ECDC4
    style EU fill:#4ECDC4
    style Asia fill:#4ECDC4
```

</details>

**Key Metrics:**
- 15,000+ content servers globally
- 200+ Tbps total capacity
- <10ms latency to 90% of users
- 99.99% availability target

### Database Geo-Replication: CockroachDB

| Feature | Implementation | Benefit |
|---------|----------------|---------|
| **Geo-Partitioning** | Pin data to regions | Compliance + performance |
| **Consensus Replication** | Raft across replicas | Strong consistency |
| **Zone Survival** | 3+ replicas per region | Datacenter failures |
| **Global Transactions** | Two-phase commit | ACID across regions |
| **Follower Reads** | Read from nearest replica | Low latency reads |

```yaml
# CockroachDB Geo-Partitioning Example
CREATE TABLE users (
    id UUID PRIMARY KEY,
    region STRING NOT NULL,
    email STRING,
    data JSONB,
    INDEX region_idx (region)
) PARTITION BY LIST (region) (
    PARTITION us VALUES IN ('us-east', 'us-west'),
    PARTITION eu VALUES IN ('eu-west', 'eu-central'),
    PARTITION asia VALUES IN ('ap-southeast', 'ap-northeast')
);

ALTER PARTITION us CONFIGURE ZONE USING
    constraints = '[+region=us]';
ALTER PARTITION eu CONFIGURE ZONE USING  
    constraints = '[+region=eu]';
ALTER PARTITION asia CONFIGURE ZONE USING
    constraints = '[+region=asia]';
```

## Cost Optimization Strategies

### Cost Breakdown Analysis

| Cost Component | Percentage | Optimization Strategy |
|----------------|------------|----------------------|
| **Cross-Region Bandwidth** | 40-60% | Data compression, selective replication |
| **Additional Infrastructure** | 30-40% | Right-sizing, spot instances |
| **Operational Complexity** | 10-20% | Automation, monitoring tools |
| **Development Time** | 5-15% | Use managed services, proven patterns |

### ROI Calculation Framework

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

<details>
<summary>View implementation code</summary>

```mermaid
graph LR
    subgraph "Costs"
        C1[Infrastructure<br/>$100K/year]
        C2[Bandwidth<br/>$50K/year]
        C3[Operations<br/>$200K/year]
        C1 & C2 & C3 --> TC[Total Cost<br/>$350K/year]
    end
    
    subgraph "Benefits"
        B1[Latency Reduction<br/>+$500K revenue]
        B2[Availability Gain<br/>-$100K downtime]
        B3[Compliance Value<br/>+$200K business]
        B1 & B2 & B3 --> TB[Total Benefit<br/>$800K/year]
    end
    
    TC & TB --> ROI[ROI: 128%<br/>Payback: 6 months]
    
    style TC fill:#FF6B6B
    style TB fill:#4ECDC4
    style ROI fill:#96CEB4
```

</details>

## Monitoring & Operations

### Critical Metrics Dashboard

| Metric Category | Key Indicators | Alert Thresholds |
|-----------------|----------------|------------------|
| **Replication Health** | Lag time, success rate | >1s lag, <99% success |
| **Regional Performance** | Latency p95/p99, error rate | >200ms, >0.1% errors |
| **Consistency** | Conflict rate, resolution time | >0.01% conflicts |
| **Cost** | Bandwidth usage, compute cost | >20% budget variance |
| **Availability** | Region uptime, failover time | <99.9%, >5min failover |

### Disaster Recovery Procedures

```mermaid
stateDiagram-v2
    [*] --> Healthy: Normal Operations
    Healthy --> Degraded: Region Issues
    Healthy --> Emergency: Region Failure
    
    Degraded --> Investigating: Monitor & Assess
    Emergency --> Failover: Automatic/Manual
    
    Investigating --> Healthy: Issues Resolved
    Investigating --> Emergency: Escalation
    
    Failover --> Recovery: Primary Restored
    Recovery --> Healthy: Sync Complete
    
    note right of Failover: RTO Target: <5 minutes
    note right of Recovery: RPO Target: <1 minute
```

## Common Pitfalls & Solutions

| Pitfall | Impact | Root Cause | Solution |
|---------|---------|------------|----------|
| **Split-Brain Scenarios** | Data corruption | Network partitions | Implement quorum voting |
| **Cascading Failures** | Global outage | Region dependencies | Circuit breakers between regions |
| **Clock Drift** | Ordering issues | System clock skew | Use logical clocks (HLC) |
| **Bandwidth Explosion** | High costs | Full dataset replication | Selective/filtered replication |
| **Operational Complexity** | Human errors | Too many moving parts | Automation and runbooks |


## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Roadmap

### Phase 1: Foundation (Month 1-2)
- [ ] Deploy secondary region (read-only)
- [ ] Implement basic replication
- [ ] Set up monitoring and alerting
- [ ] Test failover procedures

### Phase 2: Multi-Region Writes (Month 3-4)  
- [ ] Enable writes in secondary regions
- [ ] Implement conflict resolution
- [ ] Add geo-routing logic
- [ ] Load test across regions

### Phase 3: Optimization (Month 5-6)
- [ ] Optimize replication lag
- [ ] Implement selective replication
- [ ] Add compliance controls
- [ ] Cost optimization review

## Decision Framework

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TD
    A[Global Application?] --> B{User Distribution?}
    B -->|Single Continent| C[Multi-AZ in Region]
    B -->|Global| D{Consistency Requirements?}
    
    D -->|Strong| E[Primary-Replica<br/>Synchronous]
    D -->|Eventual| F{Conflict Tolerance?}
    D -->|Session| G[Sticky Sessions<br/>+ Async Replication]
    
    F -->|Low| H[Last-Write-Wins]
    F -->|High| I[CRDTs or<br/>Application Logic]
    
    E --> J[Implement Geo-Replication]
    G --> J
    H --> J  
    I --> J
    
    style C fill:#90EE90
    style E fill:#FFD700
    style H fill:#87CEEB
    style I fill:#DDA0DD
```

</details>

## Quick Reference

### Regional Latency Expectations

| Source → Destination | Expected RTT | Replication Lag |
|---------------------|--------------|----------------|
| **US East → US West** | ~70ms | <100ms |
| **US → Europe** | ~80ms | <150ms |
| **US → Asia** | ~180ms | <250ms |
| **Europe → Asia** | ~160ms | <200ms |

### Replication Strategy Selection

| If You Need... | Use This Strategy | Trade-off |
|----------------|------------------|-----------|
| **Strong consistency** | Primary-replica sync | Higher latency |
| **Low write latency** | Multi-master async | Conflict resolution |
| **Zero data loss** | Chain replication | Sequential bottleneck |
| **Automatic conflicts** | CRDTs | Limited data types |
| **Simple implementation** | Last-write-wins | Potential data loss |

---

*"In geo-replication, the speed of light isn't just physics—it's your SLA."*

---

**Related Patterns**: [Multi-Region](multi-region.md) | [CDN](../performance/cdn.md) | [Event Sourcing](../data-management/event-sourcing.md)

**Next**: [ID Generation at Scale →](id-generation-scale.md)