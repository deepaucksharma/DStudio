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
    - **[Tunable Consistency](tunable-consistency.md)** for flexible trade-offs
    - **[Consensus Patterns](consensus.md)** for agreement protocols
    - **[Multi-Region Architecture](multi-region.md)** for real-world CAP decisions

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
    subgraph "CAP Triangle"
        C[Consistency<br/>All nodes see same data]
        A[Availability<br/>System remains operational]
        P[Partition Tolerance<br/>Survives network failures]
        
        C ---|Choose 2| A
        A ---|Choose 2| P
        P ---|Choose 2| C
        
        style C fill:#f96,stroke:#333,stroke-width:2px
        style A fill:#9f6,stroke:#333,stroke-width:2px
        style P fill:#69f,stroke:#333,stroke-width:2px
    end
    
    subgraph "Real World Choices"
        CP[CP Systems<br/>Strong Consistency<br/>May be unavailable]
        AP[AP Systems<br/>Always Available<br/>May be inconsistent]
        CA[CA Systems<br/>Consistent & Available<br/>Single node only]
    end
```

</details>

---

## Level 2: Foundation

### The Three Properties Explained

#### 1. Consistency (C)
All nodes see the same data at the same time. After a write completes, all subsequent reads will return that value.

```mermaid
sequenceDiagram
    participant Client
    participant Node1
    participant Node2
    participant Node3
    
    Client->>Node1: Write X=1
    Node1->>Node2: Replicate X=1
    Node1->>Node3: Replicate X=1
    Node2-->>Node1: ACK
    Node3-->>Node1: ACK
    Node1-->>Client: Write Complete
    
    Note over Node1,Node3: All nodes have X=1
    
    Client->>Node2: Read X
    Node2-->>Client: X=1 ✓
```

#### 2. Availability (A)
Every request receives a response (without guarantee that it contains the most recent write).

```mermaid
graph LR
    subgraph "Available System"
        C1[Client 1] -->|Write| N1[Node 1]
        C2[Client 2] -->|Read| N2[Node 2]
        C3[Client 3] -->|Write| N3[Node 3]
        
        N1 -->|Response| C1
        N2 -->|Response| C2
        N3 -->|Response| C3
    end
    
    style N1 fill:#9f6
    style N2 fill:#9f6
    style N3 fill:#9f6
```

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Network Partition"
        subgraph "Partition A"
            N1[Node 1]
            N2[Node 2]
            N1 <--> N2
        end
        
        subgraph "Partition B"
            N3[Node 3]
            N4[Node 4]
            N3 <--> N4
        end
        
        N1 -.X.- N3
        N1 -.X.- N4
        N2 -.X.- N3
        N2 -.X.- N4
    end
    
    style N1 fill:#69f
    style N2 fill:#69f
    style N3 fill:#f96
    style N4 fill:#f96
```

</details>

---

## Interactive Decision Support Tools

### CAP Trade-off Decision Tree

```mermaid
flowchart TD
    Start[Design Decision] --> Q1{Can tolerate<br/>network partitions?}
    
    Q1 -->|No| CA[CA System<br/>Single Node Only]
    Q1 -->|Yes| Q2{Primary Requirement?}
    
    Q2 -->|Data Correctness| CP[CP System]
    Q2 -->|Always Online| AP[AP System]
    
    CP --> CPEx[Examples:<br/>• Banking<br/>• Inventory<br/>• Configuration]
    AP --> APEx[Examples:<br/>• Social Media<br/>• CDN<br/>• Shopping Cart]
    CA --> CAEx[Examples:<br/>• Traditional RDBMS<br/>• Single Server Apps]
    
    style CP fill:#f96,stroke:#333,stroke-width:2px
    style AP fill:#9f6,stroke:#333,stroke-width:2px
    style CA fill:#fc6,stroke:#333,stroke-width:2px
```

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

```mermaid
graph TD
    subgraph "Consistency Spectrum"
        SC[Strong Consistency<br/>Linearizable]
        EC[Eventual Consistency<br/>Convergent]
        CC[Causal Consistency<br/>Ordered]
        RC[Read Your Writes<br/>Session]
        MC[Monotonic Reads<br/>No rollback]
    end
    
    SC -->|Relaxing| CC
    CC -->|Relaxing| RC
    RC -->|Relaxing| MC
    MC -->|Relaxing| EC
    
    SC -.->|Banking| B1[Zero tolerance<br/>for inconsistency]
    CC -.->|Social| B2[Comments appear<br/>in order]
    EC -.->|Analytics| B3[Eventually accurate<br/>counts OK]
```

### Availability vs Consistency Trade-off Visualizer

```mermaid
graph LR
    subgraph "Trade-off Space"
        A1[100% Available<br/>0% Consistent] 
        A2[90% Available<br/>50% Consistent]
        A3[70% Available<br/>90% Consistent]
        A4[50% Available<br/>100% Consistent]
        
        A1 -->|More Consistency| A2
        A2 -->|More Consistency| A3
        A3 -->|More Consistency| A4
    end
    
    A1 -.->|Use Cases| UC1[Caching<br/>Analytics<br/>Logging]
    A2 -.->|Use Cases| UC2[Social Media<br/>Shopping]
    A3 -.->|Use Cases| UC3[Inventory<br/>Booking]
    A4 -.->|Use Cases| UC4[Banking<br/>Trading]
    
    style A1 fill:#9f6
    style A4 fill:#f96
```

---

## Level 3: Deep Dive

### Real-World CAP Implementations

#### CP Systems Example: Zookeeper/etcd

```mermaid
sequenceDiagram
    participant Client
    participant Leader
    participant Follower1
    participant Follower2
    
    Note over Leader,Follower2: Network Partition Occurs
    
    Client->>Leader: Write request
    Leader->>Follower1: Replicate
    Leader->>Follower2: Replicate (fails)
    Follower1-->>Leader: ACK
    
    Note over Leader: Only 2/3 nodes = No quorum
    Leader-->>Client: Write REJECTED
    
    Note over Client,Follower2: Consistent but Unavailable
```

#### AP Systems Example: Cassandra

```mermaid
sequenceDiagram
    participant Client
    participant Node1
    participant Node2
    participant Node3
    
    Note over Node1,Node3: Network Partition
    
    Client->>Node1: Write X=1
    Node1->>Node1: Store locally
    Node1-->>Client: Write accepted
    
    Client->>Node3: Write X=2
    Node3->>Node3: Store locally
    Node3-->>Client: Write accepted
    
    Note over Node1,Node3: Conflicting values!
    Note over Node1,Node3: Available but Inconsistent
```

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Hybrid System"
        subgraph "CP Subsystem"
            CP1[Configuration Service]
            CP2[User Authentication]
            CP3[Payment Processing]
        end
        
        subgraph "AP Subsystem"
            AP1[Product Catalog]
            AP2[User Activity Feed]
            AP3[Recommendations]
        end
        
        Client[Client Request] --> GW[Gateway]
        GW --> CP1
        GW --> AP1
    end
    
    style CP1 fill:#f96
    style CP2 fill:#f96
    style CP3 fill:#f96
    style AP1 fill:#9f6
    style AP2 fill:#9f6
    style AP3 fill:#9f6
```

</details>

---

## Level 4: Expert Considerations

### Beyond CAP: PACELC

PACELC extends CAP by considering latency:
- **If Partition** (P): Choose Availability (A) or Consistency (C)
- **Else** (E): Choose Latency (L) or Consistency (C)

```mermaid
graph TD
    P[System State] --> Q1{Network Partition?}
    
    Q1 -->|Yes| PC[P: Partition Scenario]
    Q1 -->|No| EL[E: Normal Operation]
    
    PC --> Q2{Choose Priority}
    Q2 -->|Availability| PA[PA System<br/>Available during partition]
    Q2 -->|Consistency| PC2[PC System<br/>Consistent during partition]
    
    EL --> Q3{Choose Priority}
    Q3 -->|Low Latency| EL2[EL System<br/>Fast when healthy]
    Q3 -->|Consistency| EC[EC System<br/>Consistent when healthy]
    
    PA --> PAEL[PA/EL: Cassandra]
    PA --> PAEC[PA/EC: DynamoDB]
    PC2 --> PCEL[PC/EL: MongoDB]
    PC2 --> PCEC[PC/EC: HBase]
```

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

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Service Mesh"
        subgraph "CP Services"
            Auth[Auth Service]
            Payment[Payment Service]
        end
        
        subgraph "AP Services"
            Catalog[Catalog Service]
            Recommend[Recommendation Service]
        end
        
        subgraph "Infrastructure"
            LB[Load Balancer]
            CB[Circuit Breaker]
            RT[Retry Logic]
        end
    end
    
    Client --> LB
    LB --> Auth
    LB --> Catalog
    
    CB --> Payment
    RT --> Recommend
    
    style Auth fill:#f96
    style Payment fill:#f96
    style Catalog fill:#9f6
    style Recommend fill:#9f6
```

</details>

## Quick Reference

### Decision Matrix

```mermaid
graph TD
    A["Need distributed system?"] --> B{"Can tolerate partitions?"}
    B -->|No| C["Single-node system<br/>(Not truly distributed)"]
    B -->|Yes| D{"Business Priority?"}
    
    D -->|"Data Correctness"| E["CP System<br/>Strong consistency"]
    D -->|"Always Available"| F["AP System<br/>Eventual consistency"]
    D -->|"Mixed Requirements"| G["Hybrid System<br/>Per-service choices"]
    
    E --> H["ZooKeeper, etcd<br/>Banking, Config"]
    F --> I["Cassandra, DynamoDB<br/>Social, Analytics"]
    G --> J["Netflix, Amazon<br/>E-commerce, Streaming"]
    
    classDef recommended fill:#81c784,stroke:#388e3c,stroke-width:2px
    classDef caution fill:#ffb74d,stroke:#f57c00,stroke-width:2px
    
    class G,J recommended
    class C caution
```

### Comparison with Alternatives

| Aspect | CAP Theorem | PACELC | Tunable Consistency | CRDTs |
|--------|-------------|--------|-------------------|-------|
| Complexity | Simple | Medium | High | Very High |
| Practicality | Educational | High | Very High | Specialized |
| Latency Focus | No | Yes | Yes | Yes |
| Conflict Handling | None | Limited | Configurable | Automatic |
| When to use | Learning | Architecture design | Production systems | Collaborative apps |

### Implementation Checklist

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
    
    - [Eventual Consistency](../data-management/eventual-consistency.md) - AP system implementation
    - [Consensus](../coordination/consensus.md) - CP system coordination
    - [Circuit Breaker](../resilience/circuit-breaker.md) - Partition handling

- :material-flask:{ .lg .middle } **Fundamental Laws**
    
    ---
    
    - [Law 2: Asynchronous Reality](../../part1-axioms/law2/) - Network delays
    - [Law 3: Emergent Chaos](../../part1-axioms/law3/) - Partition inevitability

- :material-pillar:{ .lg .middle } **Foundational Pillars**
    
    ---
    
    - [State Distribution](../../part2-pillars/state/) - Data consistency models
    - [Truth Distribution](../../part2-pillars/truth/) - Consensus mechanisms

- :material-tools:{ .lg .middle } **Modern Alternatives**
    
    ---
    
    - [PACELC Analysis Guide](../../excellence/guides/pacelc-analysis.md)
    - [Tunable Consistency Setup](../../excellence/guides/tunable-consistency.md)
    - [CRDT Implementation Guide](../../excellence/guides/crdt-setup.md)

</div>

---