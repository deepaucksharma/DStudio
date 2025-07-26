---
title: Pattern Selector Tool
description: Interactive decision tree to find the right distributed systems pattern for your problem
type: tool
---

# Pattern Selector Tool

**Find the right pattern for your specific problem**

## 🎯 Interactive Pattern Finder

<div class="pattern-selector" markdown>

### Start Here: What's Your Primary Challenge?

<div class="selector-cards grid" markdown>

-   **🔥 System Reliability**
    
    My system fails too often or cascades failures
    
    [→ Explore Reliability Patterns](#reliability-patterns)

-   **📈 Scalability Issues**
    
    Can't handle increasing load or data volume
    
    [→ Explore Scale Patterns](#scale-patterns)

-   **🔄 Data Consistency**
    
    Data conflicts or inconsistencies across nodes
    
    [→ Explore Consistency Patterns](#consistency-patterns)

-   **⚡ Performance Problems**
    
    Too slow, high latency, or poor throughput
    
    [→ Explore Performance Patterns](#performance-patterns)

</div>

</div>

---

## Reliability Patterns

### What type of reliability issue?

```mermaid
graph TD
    Start[Reliability Issue] --> Q1{What fails?}
    
    Q1 -->|Single Service| Single[Single Service Failures]
    Q1 -->|Multiple Services| Multiple[Cascading Failures]
    Q1 -->|Network| Network[Network Issues]
    Q1 -->|Overload| Overload[System Overload]
    
    Single --> S1[Health Check<br/>Monitor service health]
    Single --> S2[Timeout<br/>Prevent hanging]
    Single --> S3[Retry + Backoff<br/>Handle transients]
    
    Multiple --> M1[Circuit Breaker<br/>Stop cascades]
    Multiple --> M2[Bulkhead<br/>Isolate failures]
    Multiple --> M3[Service Mesh<br/>Manage all services]
    
    Network --> N1[Retry + Backoff<br/>Handle network blips]
    Network --> N2[Failover<br/>Use backup]
    Network --> N3[Multi-Region<br/>Geographic redundancy]
    
    Overload --> O1[Rate Limiting<br/>Control intake]
    Overload --> O2[Load Shedding<br/>Drop low priority]
    Overload --> O3[Auto-Scaling<br/>Add capacity]
    
    style Start fill:#ef4444,stroke:#dc2626
    style S1 fill:#10b981,stroke:#059669
    style M1 fill:#10b981,stroke:#059669
    style N1 fill:#10b981,stroke:#059669
    style O1 fill:#10b981,stroke:#059669
```

### Reliability Decision Matrix

| Your Situation | Primary Pattern | Also Consider | Complexity |
|----------------|----------------|---------------|------------|
| **Service keeps dying** | [Health Check](health-check) | [Timeout](timeout), [Retry](retry-backoff) | 🟢 Low |
| **One failure kills many** | [Circuit Breaker](circuit-breaker) | [Bulkhead](bulkhead), [Timeout](timeout) | 🟡 Medium |
| **Can't handle spikes** | [Rate Limiting](rate-limiting) | [Load Shedding](load-shedding), [Auto-Scaling](auto-scaling) | 🟡 Medium |
| **Need zero downtime** | [Blue-Green Deploy](blue-green-deployment) | [Canary](canary-deployment), [Feature Flags](feature-flags) | 🟡 Medium |
| **Geographic failures** | [Multi-Region](multi-region) | [Failover](failover), [Geo-Replication](geo-replication) | 🔴 High |

---

## Scale Patterns

### What needs to scale?

```mermaid
graph TD
    Start[Scale Challenge] --> Q1{What can't scale?}
    
    Q1 -->|Data Storage| Data[Data Won't Fit]
    Q1 -->|Request Load| Load[Too Many Requests]
    Q1 -->|Processing| Process[Processing Too Slow]
    Q1 -->|Geographic| Geo[Global Users]
    
    Data --> D1[Sharding<br/>Split data horizontally]
    Data --> D2[Partitioning<br/>Divide by key]
    Data --> D3[Consistent Hashing<br/>Dynamic sharding]
    
    Load --> L1[Load Balancing<br/>Distribute requests]
    Load --> L2[Caching<br/>Reduce DB hits]
    Load --> L3[CDN<br/>Edge caching]
    
    Process --> P1[Map-Reduce<br/>Parallel processing]
    Process --> P2[Stream Processing<br/>Real-time pipeline]
    Process --> P3[Batch Processing<br/>Offline compute]
    
    Geo --> G1[Geo-Replication<br/>Regional copies]
    Geo --> G2[Edge Computing<br/>Process at edge]
    Geo --> G3[Multi-Region<br/>Regional deployment]
    
    style Start fill:#3b82f6,stroke:#2563eb
    style D1 fill:#10b981,stroke:#059669
    style L1 fill:#10b981,stroke:#059669
    style P1 fill:#10b981,stroke:#059669
    style G1 fill:#10b981,stroke:#059669
```

### Scale Decision Matrix

| Your Situation | Primary Pattern | Also Consider | Complexity |
|----------------|----------------|---------------|------------|
| **Database too big** | [Sharding](sharding) | [Partitioning](partitioning), [Compression](compression) | 🔴 High |
| **Too many requests** | [Load Balancing](load-balancing) | [Caching](caching-strategies), [CDN](cdn) | 🟢 Low |
| **Slow queries** | [Caching](caching-strategies) | [Read Replicas](leader-follower), [Materialized Views](materialized-view) | 🟡 Medium |
| **Global users** | [CDN](cdn) | [Geo-Replication](geo-replication), [Edge Computing](edge-computing) | 🟡 Medium |
| **CPU bottleneck** | [Horizontal Scaling](auto-scaling) | [Async Processing](event-driven), [Batch Jobs](batch-processing) | 🟡 Medium |

---

## Consistency Patterns

### What consistency challenge?

```mermaid
graph TD
    Start[Consistency Issue] --> Q1{What's inconsistent?}
    
    Q1 -->|Multiple Writers| Writers[Concurrent Updates]
    Q1 -->|Distributed State| State[State Synchronization]
    Q1 -->|Transactions| Trans[Transaction Boundaries]
    Q1 -->|Ordering| Order[Event Ordering]
    
    Writers --> W1[Distributed Lock<br/>Mutual exclusion]
    Writers --> W2[CAS Operations<br/>Compare and swap]
    Writers --> W3[Leader Election<br/>Single writer]
    
    State --> S1[Consensus<br/>Agreement protocol]
    State --> S2[State Machine<br/>Replicated state]
    State --> S3[CRDTs<br/>Conflict-free]
    
    Trans --> T1[2PC<br/>Atomic commit]
    Trans --> T2[Saga<br/>Compensating trans]
    Trans --> T3[Event Sourcing<br/>Event-based]
    
    Order --> O1[Vector Clocks<br/>Causal ordering]
    Order --> O2[Logical Clocks<br/>Total ordering]
    Order --> O3[HLC<br/>Hybrid clocks]
    
    style Start fill:#f59e0b,stroke:#d97706
    style W1 fill:#10b981,stroke:#059669
    style S1 fill:#10b981,stroke:#059669
    style T1 fill:#10b981,stroke:#059669
    style O1 fill:#10b981,stroke:#059669
```

### Consistency Decision Matrix

| Your Situation | Primary Pattern | Also Consider | Complexity |
|----------------|----------------|---------------|------------|
| **Lost updates** | [Distributed Lock](distributed-lock) | [CAS](cas), [Leader Election](leader-election) | 🔴 High |
| **Out of sync data** | [Anti-Entropy](anti-entropy) | [Gossip](gossip-protocol), [Merkle Trees](merkle-trees) | 🟡 Medium |
| **Need transactions** | [Saga](saga) | [2PC](two-phase-commit), [Event Sourcing](event-sourcing) | 🔴 High |
| **Wrong order** | [Vector Clocks](vector-clocks) | [Logical Clocks](logical-clocks), [HLC](hlc) | 🔴 High |
| **Split brain** | [Consensus](consensus) | [Generation Clock](generation-clock), [Lease](lease) | 🔴 High |

---

## Performance Patterns

### What's slow?

```mermaid
graph TD
    Start[Performance Issue] --> Q1{Where's the bottleneck?}
    
    Q1 -->|Database| DB[Database Slow]
    Q1 -->|Network| Net[Network Latency]
    Q1 -->|Processing| Proc[CPU Bound]
    Q1 -->|Memory| Mem[Memory Issues]
    
    DB --> D1[Caching<br/>Reduce DB load]
    DB --> D2[Read Replicas<br/>Scale reads]
    DB --> D3[CQRS<br/>Separate read/write]
    
    Net --> N1[Batching<br/>Reduce round trips]
    Net --> N2[Compression<br/>Reduce size]
    Net --> N3[CDN<br/>Edge serving]
    
    Proc --> P1[Async Processing<br/>Non-blocking]
    Proc --> P2[Worker Pools<br/>Parallel work]
    Proc --> P3[Map-Reduce<br/>Distributed compute]
    
    Mem --> M1[Memory Pool<br/>Reuse objects]
    Mem --> M2[Streaming<br/>Process chunks]
    Mem --> M3[Compression<br/>Reduce footprint]
    
    style Start fill:#8b5cf6,stroke:#7c3aed
    style D1 fill:#10b981,stroke:#059669
    style N1 fill:#10b981,stroke:#059669
    style P1 fill:#10b981,stroke:#059669
    style M1 fill:#10b981,stroke:#059669
```

### Performance Decision Matrix

| Your Situation | Primary Pattern | Also Consider | Complexity |
|----------------|----------------|---------------|------------|
| **Slow DB queries** | [Caching](caching-strategies) | [Indexes](indexing), [Read Replicas](leader-follower) | 🟢 Low |
| **High latency** | [Edge Computing](edge-computing) | [CDN](cdn), [Caching](caching-strategies) | 🟡 Medium |
| **Too many requests** | [Batching](request-batching) | [Compression](compression), [HTTP/2](http2) | 🟢 Low |
| **CPU maxed out** | [Horizontal Scaling](auto-scaling) | [Async Processing](event-driven), [Worker Pools](worker-pool) | 🟡 Medium |
| **Memory pressure** | [Streaming](streaming) | [Pagination](pagination), [Compression](compression) | 🟡 Medium |

---

## 🎯 Pattern Combination Finder

### Common Pattern Combinations

<div class="pattern-combinations" markdown>

#### For E-Commerce Systems
```mermaid
graph LR
    Cart[Shopping Cart] --> CQRS[CQRS<br/>Read/Write Split]
    CQRS --> Cache[Cache<br/>Product Data]
    Cache --> CDN[CDN<br/>Images]
    
    Order[Order Processing] --> Saga[Saga<br/>Distributed Trans]
    Saga --> Event[Event Sourcing<br/>Audit Trail]
    Event --> Outbox[Outbox<br/>Guaranteed Delivery]
    
    style Cart fill:#10b981,stroke:#059669
    style Order fill:#3b82f6,stroke:#2563eb
```

**Patterns**: CQRS + Caching + CDN + Saga + Event Sourcing + Outbox

#### For Real-Time Systems
```mermaid
graph LR
    Stream[Data Stream] --> Kafka[Event Streaming<br/>Kafka/Pulsar]
    Kafka --> Process[Stream Processing<br/>Flink/Spark]
    Process --> State[State Store<br/>RocksDB]
    
    Client[Clients] --> WS[WebSocket<br/>Real-time]
    WS --> Push[Push Notifications<br/>Mobile]
    
    style Stream fill:#f59e0b,stroke:#d97706
    style Client fill:#8b5cf6,stroke:#7c3aed
```

**Patterns**: Event Streaming + Stream Processing + WebSockets + Push Notifications

#### For Global Applications
```mermaid
graph LR
    User[Global Users] --> CDN[CDN<br/>Static Assets]
    CDN --> Edge[Edge Computing<br/>Logic at Edge]
    Edge --> Region[Multi-Region<br/>Data Centers]
    
    Region --> Geo[Geo-Replication<br/>Data Sync]
    Geo --> CRDT[CRDTs<br/>Conflict Resolution]
    
    style User fill:#ef4444,stroke:#dc2626
```

**Patterns**: CDN + Edge Computing + Multi-Region + Geo-Replication + CRDTs

</div>

---

## 🔧 Implementation Difficulty Guide

### Pattern Complexity Levels

<div class="complexity-guide" markdown>

#### 🟢 Beginner Patterns (Days to implement)
- **Health Check**: Simple endpoint returning status
- **Timeout**: Wrapper around calls with time limit
- **Retry**: Retry logic with exponential backoff
- **Cache Aside**: Check cache, fallback to DB
- **Load Balancing**: Round-robin or random selection

#### 🟡 Intermediate Patterns (Weeks to implement)
- **Circuit Breaker**: State machine with failure tracking
- **Rate Limiting**: Token bucket or sliding window
- **Sharding**: Data partitioning strategy
- **CQRS**: Separate read/write models
- **Service Discovery**: Dynamic service registry

#### 🔴 Advanced Patterns (Months to implement)
- **Consensus**: Raft or Paxos implementation
- **Distributed Lock**: Coordination with timeout
- **Saga**: Distributed transaction orchestration
- **Event Sourcing**: Complete event-driven architecture
- **Service Mesh**: Full observability and control plane

</div>

---

## 📋 Quick Pattern Selector Checklist

### Answer these questions to find your patterns:

<div class="checklist" markdown>

**1. System Scale**
- [ ] < 100 requests/second → Start with monolith
- [ ] 100-10K req/s → Add caching, load balancing
- [ ] 10K-100K req/s → Consider sharding, microservices
- [ ] > 100K req/s → Need full distributed architecture

**2. Data Size**
- [ ] < 1 GB → Single database is fine
- [ ] 1-100 GB → Add read replicas
- [ ] 100 GB - 1 TB → Consider sharding
- [ ] > 1 TB → Must shard, consider data lake

**3. Geographic Distribution**
- [ ] Single region → Standard patterns
- [ ] Multi-region reads → Add CDN, caching
- [ ] Multi-region writes → Need conflict resolution
- [ ] Global → Full geo-replication strategy

**4. Consistency Requirements**
- [ ] Best effort → Use caching aggressively
- [ ] Eventual → CRDTs, anti-entropy
- [ ] Strong → Consensus, distributed locks
- [ ] Transactions → Saga or 2PC

**5. Team Size**
- [ ] 1-3 engineers → Keep it simple
- [ ] 4-10 engineers → Can handle medium complexity
- [ ] 11-50 engineers → Can build complex systems
- [ ] > 50 engineers → Can maintain any pattern

</div>

---

## 🎯 Pattern Decision Flowchart

```mermaid
graph TD
    Start[Start Here] --> Scale{What's your<br/>scale?}
    
    Scale -->|< 1K users| Small[Keep it Simple]
    Scale -->|1K-100K| Medium[Add Reliability]
    Scale -->|> 100K| Large[Full Distribution]
    
    Small --> S1[Monolith<br/>+ PostgreSQL<br/>+ Redis Cache]
    
    Medium --> M1[Load Balancer<br/>+ Read Replicas<br/>+ CDN]
    Medium --> M2[Circuit Breaker<br/>+ Rate Limiting<br/>+ Health Checks]
    
    Large --> L1[Microservices<br/>+ Service Mesh<br/>+ API Gateway]
    Large --> L2[Sharding<br/>+ CQRS<br/>+ Event Sourcing]
    Large --> L3[Multi-Region<br/>+ Edge Computing<br/>+ Geo-Replication]
    
    style Start fill:#5448C8,stroke:#fff,stroke-width:3px,color:#fff
    style S1 fill:#10b981,stroke:#059669
    style M1 fill:#3b82f6,stroke:#2563eb
    style M2 fill:#3b82f6,stroke:#2563eb
    style L1 fill:#f59e0b,stroke:#d97706
    style L2 fill:#f59e0b,stroke:#d97706
    style L3 fill:#f59e0b,stroke:#d97706
```

---

## Need More Help?

<div class="help-cards grid" markdown>

-   **📚 Study Examples**
    
    See how companies use these patterns
    
    [→ Case Studies](../case-studies/)

-   **💬 Ask Community**
    
    Get help from practitioners
    
    [→ Discussions](#)

-   **🧪 Try It Out**
    
    Experiment with implementations
    
    [→ Code Examples](pattern-implementations)

-   **📊 Compare Options**
    
    Detailed pattern comparisons
    
    [→ Pattern Matrix](pattern-matrix)

</div>

---

<div class="pattern-nav" markdown>
[← Back to Patterns](index) | [Pattern Comparison →](pattern-comparison) | [Pattern Quiz →](pattern-quiz)
</div>