---
best-for:
- Large-scale data that exceeds single node capacity
- Systems requiring 99.99%+ availability
- Global applications needing data locality
category: data-management
current_relevance: mainstream
description: Patterns and techniques for storing and managing data across multiple
  nodes in distributed systems
difficulty: intermediate
essential_question: How do we ensure data consistency and reliability with distributed
  storage?
excellence_tier: silver
introduced: 2003-10
last-updated: 2025-01-23
pattern_status: use-with-expertise
prerequisites:
- consistency-models
- replication
- partitioning
reading-time: 45 min
status: complete
tagline: Master distributed storage for distributed systems success
title: Distributed Storage
trade-offs:
  cons:
  - Complex consistency and coordination challenges
  - Higher operational overhead and costs
  - Network partitions and split-brain scenarios
  pros:
  - Horizontal scalability beyond single-node limits
  - High availability through replication
  - Geographic distribution for locality
type: pattern
when-not-to-use: When data fits on single node and downtime is acceptable
when-to-use: When data exceeds single node capacity or requires high availability
  and fault tolerance
---

## Essential Question

**How do we ensure data consistency and reliability with distributed storage?**

# Distributed Storage

## 🤔 Essential Questions

<div class="decision-box">
<h4>How do you store petabytes of data reliably when any single machine can fail?</h4>

**The Challenge**: Single machines have limited capacity and are single points of failure

**The Pattern**: Distribute data across many machines with replication and coordination

**Critical Decision**: How to balance consistency, availability, and partition tolerance?
</div>

!!! warning "🥈 Silver Tier Pattern"
    **Infinite scale with infinite complexity** • Use when single-node limits are truly exceeded
    
    Distributed storage enables petabyte-scale systems but brings CAP theorem trade-offs, complex failure modes, and significant operational overhead.
    
    **Trade-offs**:
    - ✅ Scale beyond any single machine
    - ✅ Survive multiple failures
    - ❌ Complex consistency guarantees
    - ❌ Network partition handling

[Home](/) > [Patterns](../patterns/) > [Data Patterns](../patterns/index.md#data-patterns) > Distributed Storage

## When to Use / When NOT to Use

<div class="decision-box">
<h4>🎯 Decision Guide</h4>

**Perfect for:**
- Data exceeding single machine capacity (>10TB)
- Global applications needing data locality
- Systems requiring 99.99%+ availability
- Write-heavy workloads needing horizontal scaling
- Cost-effective cold storage at scale

**Avoid when:**
- Data fits on a single machine (<1TB)
- Strong consistency is critical
- Simple master-slave replication suffices
- Operational complexity exceeds team capability
- Cost of distribution exceeds benefits

**Key trade-off**: Massive scale and availability vs. consistency guarantees and operational complexity
</div>

## Level 1: Core Concepts

### Storage Architecture Comparison

| Architecture | Consistency | Scalability | Complexity | Use Case |
|-------------|-------------|-------------|------------|----------|
| **Single Node** | Strong | None | Simple | Small apps |
| **Master-Slave** | Strong | Read only | Medium | Read-heavy |
| **Sharded** | Varies | High | High | Large datasets |
| **Distributed** | Eventual | Infinite | Very High | Global scale |

### Data Distribution Flow

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
flowchart TB
    subgraph "Write Path"
        Client[Client Write] --> Router[Storage Router]
        Router --> Hash[Consistent Hash]
        Hash --> Primary[Primary Node]
        Primary --> Rep1[Replica 1]
        Primary --> Rep2[Replica 2]
        Primary --> Ack[Acknowledge]
    end
    
    subgraph "Read Path"
        ReadClient[Client Read] --> ReadRouter[Storage Router]
        ReadRouter --> Quorum[Quorum Read]
        Quorum --> N1[Node 1]
        Quorum --> N2[Node 2]
        Quorum --> N3[Node 3]
        Quorum --> Reconcile[Reconcile Versions]
    end
    
    subgraph "Failure Handling"
        Monitor[Health Monitor] --> Detect[Detect Failure]
        Detect --> Reroute[Reroute Traffic]
        Detect --> Replicate[Re-replicate Data]
    end
```

</details>

## Level 2: Distribution Strategies

### Partitioning Methods

```mermaid
graph TB
    subgraph "Hash Partitioning"
        HK[Key: user123] --> HF[Hash Function]
        HF --> HP[Partition 7]
        HP --> HN[Node C]
    end
    
    subgraph "Range Partitioning"
        RK[Key: user123] --> RR[Range A-M]
        RR --> RP[Partition 1]
        RP --> RN[Node A]
    end
    
    subgraph "Geographic Partitioning"
        GK[Key: us-west-user] --> GR[Region: US-West]
        GR --> GP[West Coast Nodes]
    end
```

### Replication Strategies

| Strategy | Consistency | Performance | Complexity | When to Use |
|----------|-------------|-------------|------------|-------------|
| **Primary-Backup** | Strong | Good reads | Simple | Small clusters |
| **Chain Replication** | Strong | Balanced | Medium | Ordered data |
| **Quorum** | Tunable | Tunable | Medium | Flexible needs |
| **Erasure Coding** | Eventual | Space efficient | High | Cold storage |

## Level 3: Implementation Patterns

### Quorum-Based Storage

```mermaid
flowchart LR
    subgraph "Write Quorum (W=2)"
        W[Write Request] --> W1[Node 1 ✓]
        W --> W2[Node 2 ✓]
        W --> W3[Node 3 ✗]
        W1 --> WS[Success]
        W2 --> WS
    end
    
    subgraph "Read Quorum (R=2)"
        R[Read Request] --> R1[Node 1: v2]
        R --> R2[Node 2: v2]
        R --> R3[Node 3: v1]
        R1 --> RR[Return v2]
        R2 --> RR
        RR --> RRepair[Repair Node 3]
    end
```

### Consistency Levels

| Level | Write | Read | Latency | Consistency | Use Case |
|-------|-------|------|---------|-------------|----------|
| **ONE** | 1 node | 1 node | Lowest | Weak | Logs, metrics |
| **QUORUM** | N/2+1 | N/2+1 | Medium | Strong | User data |
| **ALL** | N nodes | N nodes | Highest | Strongest | Critical data |
| **LOCAL_ONE** | 1 in DC | 1 in DC | Low | DC-local | Multi-DC |

### Storage Efficiency Comparison

```mermaid
graph TB
    subgraph "3x Replication"
        D1[1GB Data] --> R1[Node 1: 1GB]
        D1 --> R2[Node 2: 1GB]
        D1 --> R3[Node 3: 1GB]
        R1 --> T1[Total: 3GB]
    end
    
    subgraph "Erasure Coding (6+3)"
        D2[1GB Data] --> Split[Split into 6 parts]
        Split --> P1[Data 1: 167MB]
        Split --> P2[Data 2: 167MB]
        Split --> P3[Data 3: 167MB]
        Split --> P4[Data 4: 167MB]
        Split --> P5[Data 5: 167MB]
        Split --> P6[Data 6: 167MB]
        Split --> Parity[3 Parity: 500MB]
        P6 --> T2[Total: 1.5GB]
    end
```

## Level 4: Real-World Systems

### System Architecture Comparison

| System | Distribution | Consistency | Scale | Best For |
|--------|-------------|-------------|-------|----------|
| **HDFS** | Block-based | Strong | PB | Analytics |
| **Cassandra** | Ring/Tokens | Eventual | PB | Time-series |
| **S3** | Object | Eventual | EB | Objects |
| **Ceph** | CRUSH map | Strong | PB | Block/Object/File |
| **GlusterFS** | DHT | Strong | PB | POSIX files |

### Failure Scenarios

```mermaid
flowchart TB
    subgraph "Node Failure"
        NF[Node Dies] --> Detect[Detection: 10s]
        Detect --> Mark[Mark Dead]
        Mark --> Rereplicate[Re-replicate: 1-60min]
    end
    
    subgraph "Network Partition"
        Part[Network Split] --> Brain[Split Brain]
        Brain --> Quorum[Quorum Decision]
        Quorum --> Minority[Minority: Read Only]
        Quorum --> Majority[Majority: Read/Write]
    end
    
    subgraph "Corruption"
        Corrupt[Data Corruption] --> Checksum[Checksum Fail]
        Checksum --> Replica[Use Replica]
        Replica --> Repair[Repair Corrupt]
    end
```

## Level 5: Production Considerations

### Operational Checklist

```mermaid
flowchart TD
    Deploy[Deploy Storage] --> Monitor
    
    Monitor[Monitor Health] --> Metrics{Key Metrics}
    Metrics --> Disk[Disk Usage > 80%?]
    Metrics --> Replication[Replication Lag?]
    Metrics --> Failures[Node Failures?]
    
    Disk --> AddNodes[Add Nodes]
    Replication --> Investigate[Check Network]
    Failures --> Replace[Replace Nodes]
    
    AddNodes --> Rebalance[Rebalance Data]
    Replace --> Rebalance
    Rebalance --> Monitor
```

### Cost Analysis

| Factor | 3x Replication | Erasure Coding | Trade-off |
|--------|----------------|----------------|-----------|
| **Storage Cost** | 300% overhead | 50% overhead | EC wins |
| **CPU Cost** | Low | High (encode/decode) | Replication wins |
| **Network Cost** | 3x writes | 1.5x writes | EC wins |
| **Rebuild Cost** | Read 1 replica | Read 6+ nodes | Replication wins |
| **Access Latency** | Direct read | Decode required | Replication wins |

### Monitoring Dashboard

```mermaid
graph LR
    subgraph "Health Metrics"
        Nodes[Active Nodes: 47/50]
        Space[Used Space: 78%]
        Repl[Under-replicated: 2.1%]
    end
    
    subgraph "Performance"
        Read[Read Latency: 12ms p99]
        Write[Write Latency: 45ms p99]
        Through[Throughput: 1.2GB/s]
    end
    
    subgraph "Alerts"
        DiskAlert[❗ Node23: 92% full]
        RepAlert[❗ 1,234 blocks under-replicated]
    end
```

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Hotspots** | Node overload | Better key distribution |
| **Cascading failures** | Total outage | Circuit breakers, backpressure |
| **Split brain** | Data loss | Proper quorum configuration |
| **Replication storms** | Network saturation | Rate limit re-replication |
| **Zombie data** | Wasted space | Garbage collection process |


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

## Implementation Decision Tree

```mermaid
flowchart TD
    Start[Need Distributed Storage?] --> Size{Data Size?}
    
    Size -->|< 1TB| Single[Use Single Node + Backup]
    Size -->|1-10TB| Replicated[Use Simple Replication]
    Size -->|10TB-1PB| Sharded[Use Sharding + Replication]
    Size -->|> 1PB| Full[Full Distributed System]
    
    Full --> Consistency{Consistency Needs?}
    Consistency -->|Strong| HBase[HBase/Spanner]
    Consistency -->|Eventual| Cassandra[Cassandra/S3]
    
    Full --> Access{Access Pattern?}
    Access -->|File| HDFS[HDFS/Ceph]
    Access -->|Object| S3Style[S3/Swift]
    Access -->|Block| Ceph[Ceph/EBS]
```

## 🎓 Key Takeaways

1. **CAP theorem is unavoidable** - Choose your trade-offs wisely
2. **Replication ≠ Backup** - Different failures need different solutions
3. **Monitor everything** - You can't fix what you can't see
4. **Plan for failure** - Hardware fails, networks partition, software has bugs
5. **Start simple** - Don't use distributed storage until you need it

## Related Patterns

- [Consistent Hashing](consistent-hashing.md) - Distribute data evenly
- [Eventual Consistency](eventual-consistency.md) - Consistency models
- [CRDT](crdt.md) - Conflict-free data types
- [Sharding](../scaling/sharding.md) - Partition strategies
- [Leader-Follower](../coordination/leader-follower.md) - Replication patterns

---

*Next: [Eventual Consistency](eventual-consistency.md) - Managing consistency in distributed systems*