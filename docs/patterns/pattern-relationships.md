---
title: Pattern Relationship Map
description: Visual guide to pattern dependencies, combinations, and evolution paths in distributed systems
---

# Pattern Relationship Map

**Navigate the interconnected world of distributed systems patterns**

## Core Pattern Clusters

<div class="axiom-box">
<h3>🎯 Pattern Ecosystems</h3>
<p>Patterns rarely exist in isolation. Understanding their relationships is key to building robust distributed systems.</p>
</div>

### Foundation Layer Patterns

```mermaid
graph TB
    subgraph "Core Communication"
        LB[Load Balancing]
        AG[API Gateway]
        SR[Service Registry]
        SD[Service Discovery]
    end
    
    subgraph "Reliability Foundation"
        CB[Circuit Breaker]
        RT[Retry & Backoff]
        TO[Timeout]
        HC[Health Check]
    end
    
    subgraph "Data Foundation"
        SH[Sharding]
        CH[Consistent Hashing]
        CA[Caching]
        WAL[Write-Ahead Log]
    end
    
    LB --> AG
    SR --> SD
    SD --> LB
    AG --> CB
    CB --> RT
    RT --> TO
    HC --> LB
    HC --> CB
    SH --> CH
    CA --> CH
    WAL --> SH
```

## Pattern Dependencies

### Resilience Chain

```mermaid
graph LR
    subgraph "Basic"
        T[Timeout]
        R[Retry]
    end
    
    subgraph "Intermediate"
        CB[Circuit Breaker]
        BH[Bulkhead]
    end
    
    subgraph "Advanced"
        LS[Load Shedding]
        BP[Backpressure]
        GD[Graceful Degradation]
    end
    
    T --> R
    R --> CB
    CB --> BH
    BH --> LS
    LS --> BP
    BP --> GD
    
    style T fill:#e1f5fe
    style R fill:#e1f5fe
    style CB fill:#fff8dc
    style BH fill:#fff8dc
    style LS fill:#ffebee
    style BP fill:#ffebee
    style GD fill:#ffebee
```

### Data Consistency Evolution

```mermaid
graph TD
    subgraph "Single Node"
        ACID[ACID Transactions]
    end
    
    subgraph "Distributed Basics"
        2PC[Two-Phase Commit]
        DL[Distributed Lock]
    end
    
    subgraph "Modern Patterns"
        SAGA[Saga Pattern]
        ES[Event Sourcing]
        CQRS[CQRS]
    end
    
    subgraph "Eventually Consistent"
        EC[Eventual Consistency]
        CRDT[CRDTs]
        MT[Merkle Trees]
    end
    
    ACID --> 2PC
    ACID --> DL
    2PC --> SAGA
    DL --> LE[Leader Election]
    SAGA --> ES
    ES --> CQRS
    CQRS --> EC
    EC --> CRDT
    EC --> MT
```

## Common Pattern Combinations

### For High-Traffic APIs

| Pattern Set | Purpose | Scale |
|------------|---------|-------|
| API Gateway + Load Balancing + Circuit Breaker | Entry point resilience | Medium-Large |
| + Rate Limiting + Caching | Traffic control | Large |
| + Service Mesh + Observability | Complete management | Very Large |

```mermaid
graph LR
    Client --> AG[API Gateway]
    AG --> RL[Rate Limiter]
    RL --> CB[Circuit Breaker]
    CB --> LB[Load Balancer]
    LB --> S1[Service 1]
    LB --> S2[Service 2]
    LB --> S3[Service 3]
    
    AG -.-> Cache
    Cache -.-> AG
    
    style AG fill:#ffd700
    style RL fill:#ffd700
    style CB fill:#ffd700
    style LB fill:#ffd700
```

### For Distributed Transactions

| Pattern Set | Purpose | Use Case |
|------------|---------|----------|
| Saga + Event Sourcing + Outbox | Distributed transactions | E-commerce orders |
| + Idempotency + Retry | Reliability | Payment processing |
| + CQRS + Materialized Views | Read optimization | Complex queries |

```mermaid
graph TB
    subgraph "Write Path"
        CMD[Command] --> SAGA[Saga Orchestrator]
        SAGA --> ES[Event Store]
        ES --> OB[Outbox]
        OB --> MQ[Message Queue]
    end
    
    subgraph "Read Path"
        MQ --> EP[Event Processor]
        EP --> MV[Materialized View]
        MV --> QUERY[Query Service]
    end
    
    style SAGA fill:#c0c0c0
    style ES fill:#c0c0c0
    style OB fill:#c0c0c0
    style MV fill:#c0c0c0
```

### For Real-Time Systems

| Pattern Set | Purpose | Examples |
|------------|---------|----------|
| WebSocket + Pub-Sub + Event Streaming | Real-time updates | Chat, Live sports |
| + Backpressure + Circuit Breaker | Flow control | Video streaming |
| + Edge Computing + CDN | Low latency | Gaming |

## Anti-Pattern Combinations

<div class="failure-vignette">
<h3>⚠️ Dangerous Combinations</h3>
<p>Some patterns conflict and should not be used together:</p>
</div>

| Don't Combine | Why | Alternative |
|---------------|-----|-------------|
| Distributed Lock + Event Sourcing | Locks block event flow | Use Saga pattern |
| 2PC + Microservices | Tight coupling | Use Saga or eventual consistency |
| Synchronous Chain + Auto-scaling | Cascade failures | Use async messaging |
| Strong Consistency + Geo-distribution | Physics limits | Use eventual consistency |

## Evolution Paths

### Scaling Journey

```mermaid
graph LR
    subgraph "Small Scale"
        M[Monolith]
        DB[Single Database]
    end
    
    subgraph "Medium Scale"
        MS[Microservices]
        LF[Leader-Follower]
        C[Caching]
    end
    
    subgraph "Large Scale"
        SM[Service Mesh]
        SH[Sharding]
        ES[Event Streaming]
    end
    
    subgraph "Global Scale"
        MR[Multi-Region]
        CB[Cell-Based]
        EC[Edge Computing]
    end
    
    M --> MS
    DB --> LF
    MS --> SM
    LF --> SH
    C --> ES
    SM --> MR
    SH --> CB
    ES --> EC
    
    style M fill:#cd7f32
    style MS fill:#c0c0c0
    style SM fill:#ffd700
    style MR fill:#ffd700
```

### Consistency Evolution

```mermaid
graph TD
    subgraph "Strong Consistency"
        SYNC[Synchronous Replication]
        2PC[2-Phase Commit]
    end
    
    subgraph "Relaxed Consistency"
        ASYNC[Async Replication]
        TC[Tunable Consistency]
    end
    
    subgraph "Eventual Consistency"
        EC[Event-Driven]
        CRDT[CRDTs]
    end
    
    SYNC --> ASYNC
    2PC --> TC
    ASYNC --> EC
    TC --> CRDT
    
    SYNC -.->|"Performance Issues"| ASYNC
    2PC -.->|"Availability Issues"| TC
    TC -.->|"Conflict Resolution"| CRDT
```

## Domain-Specific Combinations

### E-Commerce Platform

```mermaid
graph TB
    subgraph "Frontend"
        CDN[CDN]
        BFF[Backend for Frontend]
    end
    
    subgraph "API Layer"
        AG[API Gateway]
        RL[Rate Limiting]
    end
    
    subgraph "Business Logic"
        SAGA[Saga]
        CQRS[CQRS]
        ES[Event Sourcing]
    end
    
    subgraph "Data Layer"
        PP[Polyglot Persistence]
        CDC[Change Data Capture]
        CACHE[Distributed Cache]
    end
    
    CDN --> BFF
    BFF --> AG
    AG --> RL
    RL --> SAGA
    SAGA --> ES
    ES --> CQRS
    CQRS --> PP
    PP --> CDC
    PP --> CACHE
```

### Real-Time Analytics

```mermaid
graph LR
    subgraph "Ingestion"
        KA[Kafka]
        BP[Backpressure]
    end
    
    subgraph "Processing"
        LA[Lambda Architecture]
        WM[Windowing]
    end
    
    subgraph "Storage"
        TS[Time-Series DB]
        DL[Data Lake]
    end
    
    subgraph "Serving"
        MV[Materialized Views]
        OLAP[OLAP Cubes]
    end
    
    KA --> BP
    BP --> LA
    LA --> WM
    WM --> TS
    WM --> DL
    TS --> MV
    DL --> OLAP
```

## Quick Reference Tables

### "If Using X, Consider Y"

| If Using | Also Consider | Why |
|----------|---------------|-----|
| Circuit Breaker | Retry + Backoff | Handle transient failures |
| API Gateway | Rate Limiting | Protect backend |
| Sharding | Consistent Hashing | Dynamic rebalancing |
| Event Sourcing | CQRS | Optimize reads |
| Service Mesh | Distributed Tracing | Observability |
| Multi-Region | Geo-Replication | Data locality |
| Microservices | Service Registry | Discovery |
| Saga | Outbox Pattern | Transactional messaging |
| WebSocket | Backpressure | Flow control |
| Leader Election | Lease | Time-bound leadership |

### "Replace A with B When Scaling"

| Current Pattern | Replace With | When |
|----------------|--------------|------|
| Monolith | Microservices | Team size > 10 |
| Single DB | Leader-Follower | Read heavy load |
| Leader-Follower | Sharding | Write heavy load |
| REST | Event Streaming | Real-time needs |
| Synchronous | Asynchronous | Decoupling needed |
| Strong Consistency | Eventual | Going global |
| Manual Scaling | Auto-scaling | Variable load |
| Single Region | Multi-Region | Global users |

### "Combine C+D for Requirement E"

| Requirement | Pattern Combination | Example |
|------------|-------------------|---------|
| Zero downtime deployment | Blue-Green + Feature Flags | SaaS updates |
| Exactly-once processing | Idempotency + Outbox | Payment systems |
| Global low latency | CDN + Edge Computing | Gaming |
| Fault isolation | Bulkhead + Circuit Breaker | Netflix |
| Data consistency | Saga + Event Sourcing | E-commerce |
| Real-time analytics | Stream + Lambda Architecture | LinkedIn |
| Elastic scaling | Auto-scaling + Load Balancing | Black Friday |
| Distributed consensus | Raft + Leader Election | etcd |

## Pattern Maturity Model

```mermaid
graph TD
    subgraph "Level 1: Basic"
        L1[Load Balancing<br/>Caching<br/>Timeouts]
    end
    
    subgraph "Level 2: Resilient"
        L2[Circuit Breaker<br/>Retry Logic<br/>Health Checks]
    end
    
    subgraph "Level 3: Distributed"
        L3[Service Mesh<br/>Event-Driven<br/>Saga]
    end
    
    subgraph "Level 4: Global"
        L4[Multi-Region<br/>Edge Computing<br/>Cell-Based]
    end
    
    subgraph "Level 5: Autonomous"
        L5[Self-Healing<br/>ML-Driven Scaling<br/>Predictive Failure]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    
    style L1 fill:#cd7f32
    style L2 fill:#c0c0c0
    style L3 fill:#ffd700
    style L4 fill:#e5e4e2
    style L5 fill:#b9f2ff
```

## Pattern Selection Decision Tree

```mermaid
graph TD
    START[Start] --> SCALE{What's your scale?}
    
    SCALE -->|"< 1K RPS"| SIMPLE[Simple Stack:<br/>Monolith + Cache]
    SCALE -->|"1K-100K RPS"| MEDIUM[Medium Stack:<br/>Microservices + LB]
    SCALE -->|"> 100K RPS"| LARGE[Large Stack:<br/>Service Mesh + Sharding]
    
    MEDIUM --> RELIABILITY{Reliability Needs?}
    RELIABILITY -->|High| ADDCB[Add Circuit Breaker<br/>+ Retry Logic]
    RELIABILITY -->|Critical| ADDFULL[Add Bulkhead<br/>+ Saga Pattern]
    
    LARGE --> GLOBAL{Global?}
    GLOBAL -->|Yes| ADDGEO[Add Multi-Region<br/>+ Edge Computing]
    GLOBAL -->|No| OPTIMIZE[Optimize:<br/>Cell-Based + CDN]
```

## Related Resources

- [Pattern Catalog](pattern-catalog.md) - Complete pattern list
- [Pattern Selector Tool](pattern-selector-tool.md) - Interactive selection
- [Architecture Examples](../case-studies/) - Real implementations
- [Anti-Patterns](../reference/anti-patterns.md) - What to avoid

---

<div class="page-nav" markdown>
[:material-arrow-left: Pattern Catalog](pattern-catalog.md) | 
[:material-arrow-up: Patterns](index.md) | 
[:material-arrow-right: Pattern Selector](pattern-selector-tool.md)
</div>