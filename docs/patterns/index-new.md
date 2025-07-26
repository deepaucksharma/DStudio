---
title: Distributed Systems Patterns
description: Curated catalog of ~95 battle-tested patterns for building distributed systems
type: patterns-index
---

# Distributed Systems Patterns

**~95 carefully curated patterns for building reliable, scalable distributed systems**

!!! info "Pattern Curation"
    We've curated the most valuable patterns for modern distributed systems, focusing on practical, battle-tested solutions. Each pattern has been selected for its real-world applicability and proven impact in production systems.

!!! tip "Quick Navigation"
    - **[By Problem Domain](#by-problem-domain)** - Organized by what you're building
    - **[By Challenge](#by-challenge)** - Find patterns for specific problems
    - **[Learning Paths](#learning-paths)** - Progressive learning tracks
    - **[Pattern Navigator](#pattern-navigator)** - Visual decision guide

## 🎯 Pattern Finder

<div class="grid cards" markdown>

-   :material-magnify: **What problem are you solving?**
    
    - [High Availability → Circuit Breaker, Failover](#high-availability)
    - [Scalability → Sharding, Caching](#scalability)
    - [Consistency → Consensus, Saga](#consistency)
    - [Performance → Batching, CDN](#performance)

-   :material-school: **What's your experience level?**
    
    - [Beginner → Start with basics](#beginner-path)
    - [Intermediate → Core patterns](#intermediate-path)
    - [Advanced → Complex patterns](#advanced-path)
    - [Expert → Cutting edge](#expert-path)

-   :material-layers: **Where in your stack?**
    
    - [Infrastructure → Storage, Network](#infrastructure-layer)
    - [Platform → Service Mesh, Gateway](#platform-layer)
    - [Application → CQRS, Saga](#application-layer)
    - [Cross-cutting → Security, Monitoring](#cross-cutting)

-   :material-book-open: **Learn by example?**
    
    - [Case Studies](case-studies/)
    - [Implementation Guides](patterns/pattern-implementations)
    - [Anti-patterns](patterns/anti-patterns)

</div>

---

## 📚 By Problem Domain

### Core Distributed Primitives
*Fundamental building blocks that other patterns depend on*

<div class="grid cards" markdown>

-   **Consensus & Coordination**
    
    - [Consensus](patterns/consensus) - Agreement in distributed systems
    - [Leader Election](patterns/leader-election) - Choosing a coordinator
    - [Distributed Lock](patterns/distributed-lock) - Mutual exclusion
    - [Lease](patterns/lease) - Time-bound ownership
    - [Generation Clock](patterns/generation-clock) - Epoch tracking
    - [Emergent Leader](patterns/emergent-leader) - Gossip-based leadership

-   **Time & Ordering**
    
    - [Logical Clocks](patterns/logical-clocks) - Event ordering
    - [Logical Clocks](patterns/logical-clocks) - Event ordering and causality
    - [Clock Sync](patterns/clock-sync) - Time synchronization

-   **Communication**
    
    - [Heartbeat](patterns/heartbeat) - Failure detection
    - [Single-Socket Channel](patterns/single-socket-channel) - Multiplexing
    - [Request Batching](patterns/request-batching) - Performance boost

</div>

### Data Management

<div class="grid cards" markdown>

-   **Storage & Persistence**
    
    - [WAL](patterns/wal) - Write-ahead logging
    - [Segmented Log](patterns/segmented-log) - Log management
    - [LSM Tree](patterns/lsm-tree) - Write optimization
    - [Distributed Storage](patterns/distributed-storage) - Multi-node

-   **Replication & Consistency**
    
    - [Leader-Follower](patterns/leader-follower) - Primary-backup
    - [State Watch](patterns/state-watch) - Change notifications
    - [Read Repair](patterns/read-repair) - Repair divergence
    - [Low/High-Water Marks](patterns/low-high-water-marks) - Flow control
    - [Eventual Consistency](patterns/eventual-consistency) - Convergence
    - [Tunable Consistency](patterns/tunable-consistency) - Configurable

-   **Partitioning**
    
    - [Sharding](patterns/sharding) - Horizontal partitioning
    - [Consistent Hashing](patterns/consistent-hashing) - Dynamic partition
    - [Shared Nothing](patterns/shared-nothing) - Isolation
    - [Cell-Based](patterns/cell-based) - Blast radius control

-   **Transactions**
    
    - [Saga](patterns/saga) - Distributed workflows
    - [Outbox](patterns/outbox) - Transactional messaging
    - [Idempotent Receiver](patterns/idempotent-receiver) - Exactly-once processing

</div>

### Resilience & Fault Tolerance

<div class="grid cards" markdown>

-   **Circuit Protection**
    
    - [Circuit Breaker](patterns/circuit-breaker) - Failure isolation
    - [Bulkhead](patterns/bulkhead) - Resource isolation
    - [Retry with Backoff](patterns/retry-backoff) - Smart retries

-   **Load Management**
    
    - [Rate Limiting](patterns/rate-limiting) - Request throttling
    - [Load Shedding](patterns/load-shedding) - Overload protection
    - [Backpressure](patterns/backpressure) - Flow control
    - [Graceful Degradation](patterns/graceful-degradation) - Feature reduction

-   **Fault Recovery**
    
    - [Failover](patterns/failover) - Backup activation
    - [Fault Tolerance](patterns/fault-tolerance) - Comprehensive guide

</div>

### Performance & Caching

<div class="grid cards" markdown>

-   **Caching Strategies**
    
    - [Cache Aside](patterns/cache-aside) - Lazy loading
    - [Read-Through](patterns/read-through-cache) - Transparent reads
    - [Write-Through](patterns/write-through-cache) - Sync writes
    - [Write-Behind](patterns/write-behind-cache) - Async writes
    - [Caching Strategies](patterns/caching-strategies) - Complete guide

-   **Performance Optimization**
    
    - [Bloom Filter](patterns/bloom-filter) - Set membership
    - [Materialized View](patterns/materialized-view) - Precomputed
    - [Request Routing](patterns/request-routing) - Smart routing
    - [Auto-Scaling](patterns/auto-scaling) - Dynamic capacity

</div>

### Architectural Patterns

<div class="grid cards" markdown>

-   **Microservices**
    
    - [Service Mesh](patterns/service-mesh) - Service communication
    - [API Gateway](patterns/api-gateway) - Single entry
    - [Service Registry](patterns/service-registry) - Discovery
    - [Sidecar](patterns/sidecar) - Proxy pattern
    - [Ambassador](patterns/ambassador) - Remote proxy
    - [BFF](patterns/backends-for-frontends) - Backend for Frontend

-   **Event-Driven**
    
    - [Event Sourcing](patterns/event-sourcing) - Event storage
    - [CQRS](patterns/cqrs) - Read/write separation
    - [Event Streaming](patterns/event-streaming) - Real-time
    - [CDC](patterns/cdc) - Change capture
    - [Choreography](patterns/choreography) - Decentralized

-   **Data Architecture**
    
    - [Data Lake](patterns/data-lake) - Raw storage
    - [Data Mesh](patterns/data-mesh) - Domain-oriented
    - [Lambda Architecture](patterns/lambda-architecture) - Batch+stream
    - [Kappa Architecture](patterns/kappa-architecture) - Stream-only
    - [Polyglot Persistence](patterns/polyglot-persistence) - Multi-DB

</div>

### Specialized Domains

<div class="grid cards" markdown>

-   **Edge & IoT**
    
    - [Edge Computing](patterns/edge-computing) - Distributed edge
    - [Delta Sync](patterns/delta-sync) - Efficient sync
    - [Battery Optimization](patterns/battery-optimization) - Power
    - [Network Optimization](patterns/network-optimization) - Bandwidth

-   **Geospatial**
    
    - [Geohashing](patterns/geohashing) - Spatial indexing
    - [Tile Pyramid](patterns/tile-pyramid) - Map tiles
    - [Vector Tiles](patterns/vector-tiles) - Efficient maps
    - [Geofencing](patterns/geofencing) - Location bounds

-   **Security & Privacy**
    
    - [Valet Key](patterns/valet-key) - Temporary access
    - [E2E Encryption](patterns/e2e-encryption) - End-to-end
    - [Key Management](patterns/key-management) - Crypto keys
    - [Consent Management](patterns/consent-management) - Privacy

</div>

---

## 🎓 Learning Paths

### Beginner Path
*Start here if you're new to distributed systems*

```mermaid
graph LR
    A[Health Check] --> B[Timeout]
    B --> C[Retry]
    C --> D[Circuit Breaker]
    D --> E[Rate Limiting]
    E --> F[Load Balancing]
    F --> G[Caching]
    
    style A fill:#10b981,stroke:#059669
    style G fill:#3b82f6,stroke:#2563eb
```

<div class="grid cards" markdown>

-   **Week 1: Basics**
    1. [Health Check](patterns/health-check) - Monitor services
    2. [Timeout](patterns/timeout) - Prevent hanging
    3. [Retry](patterns/retry-backoff) - Handle transient failures

-   **Week 2: Protection**
    4. [Circuit Breaker](patterns/circuit-breaker) - Stop cascading failures
    5. [Rate Limiting](patterns/rate-limiting) - Control request flow
    6. [Bulkhead](patterns/bulkhead) - Isolate resources

-   **Week 3: Performance**
    7. [Cache Aside](patterns/cache-aside) - Basic caching
    8. [Load Balancing](patterns/load-balancing) - Distribute load
    9. [Request Batching](patterns/request-batching) - Reduce overhead

-   **Week 4: Reliability**
    10. [Leader-Follower](patterns/leader-follower) - Basic replication
    11. [Failover](patterns/failover) - Handle failures
    12. [Health Check](patterns/health-check) - Monitor health

</div>

### Intermediate Path
*For engineers with distributed systems experience*

<div class="grid cards" markdown>

-   **Consensus & Coordination**
    - [Consensus](patterns/consensus) fundamentals
    - [Leader Election](patterns/leader-election) patterns
    - [Distributed Lock](patterns/distributed-lock) implementation
    - [Generation Clock](patterns/generation-clock) for epochs

-   **Data Distribution**
    - [Sharding](patterns/sharding) strategies
    - [Consistent Hashing](patterns/consistent-hashing)
    - [Replication](patterns/leader-follower) patterns
    - [Logical Clocks](patterns/logical-clocks) for causality

-   **Event Architecture**
    - [Event Sourcing](patterns/event-sourcing) basics
    - [CQRS](patterns/cqrs) implementation
    - [Saga](patterns/saga) patterns
    - [Outbox](patterns/outbox) for consistency

-   **Service Architecture**
    - [Service Mesh](patterns/service-mesh) concepts
    - [API Gateway](patterns/api-gateway) patterns
    - [Service Discovery](patterns/service-discovery)
    - [Sidecar](patterns/sidecar) pattern

</div>

### Advanced Path
*For experienced distributed systems engineers*

<div class="grid cards" markdown>

-   **Complex Coordination**
    - [Saga](patterns/saga) for distributed workflows
    - [Byzantine Fault Tolerance](patterns/byzantine-fault-tolerance)
    - [Emergent Leader](patterns/emergent-leader)
    - [CRDTs](patterns/crdt)

-   **Advanced Data**
    - [Anti-Entropy](patterns/anti-entropy)
    - [Merkle Trees](patterns/merkle-trees)
    - [LSM Trees](patterns/lsm-tree)
    - [Segmented Log](patterns/segmented-log)

-   **Architecture Patterns**
    - [Data Mesh](patterns/data-mesh)
    - [Lambda Architecture](patterns/lambda-architecture)
    - [Cell-Based Architecture](patterns/cell-based)
    - [Polyglot Persistence](patterns/polyglot-persistence)

-   **Specialized**
    - [ML Pipeline](patterns/ml-pipeline)
    - [Time Series](patterns/time-series-ids)
    - [Blockchain](patterns/blockchain-patterns)
    - [Quantum-Ready](patterns/quantum-ready)

</div>

---

## 🔍 By Challenge

### High Availability
*"How do I keep my system running?"*

| Challenge | Primary Patterns | Supporting Patterns |
|-----------|-----------------|-------------------|
| **Single point of failure** | [Leader-Follower](patterns/leader-follower), [Failover](patterns/failover) | [Health Check](patterns/health-check), [Heartbeat](patterns/heartbeat) |
| **Cascading failures** | [Circuit Breaker](patterns/circuit-breaker), [Bulkhead](patterns/bulkhead) | [Timeout](patterns/timeout), [Retry](patterns/retry-backoff) |
| **Overload** | [Load Shedding](patterns/load-shedding), [Rate Limiting](patterns/rate-limiting) | [Backpressure](patterns/backpressure), [Auto-Scaling](patterns/auto-scaling) |
| **Network partitions** | [Split-Brain](patterns/split-brain), [Consensus](patterns/consensus) | [Generation Clock](patterns/generation-clock), [Lease](patterns/lease) |

### Scalability
*"How do I handle more load?"*

| Challenge | Primary Patterns | Supporting Patterns |
|-----------|-----------------|-------------------|
| **Data volume** | [Sharding](patterns/sharding), [Partitioning](patterns/sharding) | [Consistent Hashing](patterns/consistent-hashing) |
| **Request volume** | [Load Balancing](patterns/load-balancing), [Caching](patterns/caching-strategies) | [CDN](patterns/cdn), [Edge Computing](patterns/edge-computing) |
| **Geographic scale** | [Geo-Replication](patterns/geo-replication), [Multi-Region](patterns/multi-region) | [Eventual Consistency](patterns/eventual-consistency) |
| **Cost at scale** | [FinOps](patterns/finops), [Serverless](patterns/serverless-faas) | [Auto-Scaling](patterns/auto-scaling), [Spot Instances](patterns/spot-instances) |

### Consistency
*"How do I keep data correct?"*

| Challenge | Primary Patterns | Supporting Patterns |
|-----------|-----------------|-------------------|
| **Distributed state** | [Consensus](patterns/consensus), [Saga](patterns/saga) | [Logical Clocks](patterns/logical-clocks), [State Watch](patterns/state-watch) |
| **Concurrent updates** | [CAS](patterns/cas), [Generation Clock](patterns/generation-clock) | [Event Sourcing](patterns/event-sourcing) |
| **Eventual consistency** | [Anti-Entropy](patterns/anti-entropy), [CRDTs](patterns/crdt) | [Gossip](patterns/gossip-protocol), [Merkle Trees](patterns/merkle-trees) |
| **Transaction boundaries** | [Saga](patterns/saga), [Outbox](patterns/outbox) | [Event Sourcing](patterns/event-sourcing) |

### Performance
*"How do I make it faster?"*

| Challenge | Primary Patterns | Supporting Patterns |
|-----------|-----------------|-------------------|
| **Latency** | [Caching](patterns/caching-strategies), [CDN](patterns/cdn) | [Edge Computing](patterns/edge-computing) |
| **Throughput** | [Batching](patterns/request-batching), [Async Processing](patterns/async-processing) | [Pipeline](patterns/pipeline) |
| **Database load** | [Read Replicas](patterns/leader-follower), [Materialized Views](patterns/materialized-view) | [CQRS](patterns/cqrs) |
| **Network overhead** | [Compression](patterns/compression), [Protocol Buffers](patterns/protobuf) | [Single-Socket](patterns/single-socket-channel) |

---

## 🏗️ By System Layer

### Infrastructure Layer
*Low-level distributed systems primitives*

- **Storage**: [WAL](patterns/wal), [LSM Tree](patterns/lsm-tree), [B-Tree](patterns/btree)
- **Network**: [Gossip](patterns/gossip-protocol), [Heartbeat](patterns/heartbeat), [RPC](patterns/rpc)
- **Consensus**: [Raft](patterns/raft), [Paxos](patterns/paxos), [PBFT](patterns/pbft)
- **Time**: [Clock Sync](patterns/clock-sync), [Logical Clocks](patterns/logical-clocks)

### Platform Layer
*Building blocks for distributed applications*

- **Service Mesh**: [Envoy](patterns/service-mesh), [Istio patterns](patterns/istio-patterns)
- **Orchestration**: [Leader Election](patterns/leader-election), [Scheduler](patterns/scheduler)
- **Messaging**: [Pub-Sub](patterns/pub-sub), [Message Queue](patterns/distributed-queue)
- **Monitoring**: [Distributed Tracing](patterns/distributed-tracing), [Metrics](patterns/metrics)

### Application Layer
*Application-level patterns*

- **Architecture**: [Microservices](patterns/microservices), [Serverless](patterns/serverless-faas)
- **Data**: [CQRS](patterns/cqrs), [Event Sourcing](patterns/event-sourcing), [Saga](patterns/saga)
- **API**: [GraphQL](patterns/graphql-federation), [REST](patterns/rest-patterns), [gRPC](patterns/grpc)
- **Frontend**: [BFF](patterns/backends-for-frontends), [Edge Rendering](patterns/edge-rendering)

---

## 📊 Pattern Comparison

### Consensus Patterns
| Pattern | Fault Tolerance | Performance | Complexity | Use Case |
|---------|----------------|-------------|------------|----------|
| [Raft](patterns/consensus) | n/2 | Fast | Medium | General purpose |
| [Paxos](patterns/consensus) | n/2 | Medium | High | Academic/proven |
| [PBFT](patterns/byzantine-fault-tolerance) | n/3 | Slow | Very High | Byzantine faults |
| [Gossip](patterns/emergent-leader) | High | Variable | Low | Eventual consistency |

### Caching Patterns
| Pattern | Consistency | Complexity | Performance | Use Case |
|---------|------------|------------|-------------|----------|
| [Cache Aside](patterns/cache-aside) | Eventual | Low | Good | Read heavy |
| [Read Through](patterns/read-through-cache) | Eventual | Medium | Better | Transparent |
| [Write Through](patterns/write-through-cache) | Strong | Medium | Slower | Consistency |
| [Write Behind](patterns/write-behind-cache) | Eventual | High | Fastest | Write heavy |

### Transaction Patterns
| Pattern | Consistency | Availability | Partition Tolerance | Use Case |
|---------|------------|--------------|-------------------|----------|
| [Saga](patterns/saga) | Eventual | High | Yes | Multi-DC |
| [Saga](patterns/saga) | Eventual | High | Yes | Microservices |
| [TCC](patterns/tcc) | Eventual | High | Yes | Business trans |
| [Outbox](patterns/outbox) | Eventual | High | Yes | Event + DB |

---

## 🚫 Anti-Patterns

### Common Mistakes

<div class="grid cards" markdown>

-   **Premature Distribution**
    
    Using distributed patterns when monolithic would work
    
    ❌ **Wrong**: Microservices for 10 users  
    ✅ **Right**: Start monolithic, split when needed

-   **Pattern Overload**
    
    Applying too many patterns at once
    
    ❌ **Wrong**: Service Mesh + CQRS + Event Sourcing day 1  
    ✅ **Right**: Add patterns as problems arise

-   **Wrong Pattern**
    
    Using consensus when eventual consistency suffices
    
    ❌ **Wrong**: Paxos for shopping cart  
    ✅ **Right**: CRDTs or last-write-wins

-   **Missing Basics**
    
    Advanced patterns without fundamentals
    
    ❌ **Wrong**: Kafka without health checks  
    ✅ **Right**: Timeouts → Retries → Circuit Breaker → Kafka

</div>

---

## 🎯 Quick Decision Guide

```mermaid
graph TD
    Start[What's your problem?] --> Availability{Need High<br/>Availability?}
    Start --> Scale{Need to<br/>Scale?}
    Start --> Consistency{Need Strong<br/>Consistency?}
    Start --> Performance{Need Better<br/>Performance?}
    
    Availability -->|Yes| HA[Circuit Breaker<br/>Failover<br/>Health Checks]
    Scale -->|Yes| SC[Sharding<br/>Load Balancing<br/>Caching]
    Consistency -->|Yes| CO[Consensus<br/>2PC<br/>Distributed Lock]
    Performance -->|Yes| PE[Caching<br/>Batching<br/>Async Processing]
    
    style Start fill:#e0e7ff,stroke:#6366f1,stroke-width:3px
    style HA fill:#10b981,stroke:#059669
    style SC fill:#3b82f6,stroke:#2563eb
    style CO fill:#f59e0b,stroke:#d97706
    style PE fill:#8b5cf6,stroke:#7c3aed
```

---

## 📚 Additional Resources

### Tools & References
- [Pattern Selector Tool](patterns/pattern-selector) - Interactive decision tree
- [Pattern Matrix](patterns/pattern-matrix) - Complete comparison table
- [Pattern Relationships](patterns/pattern-relationships) - Dependency graph
- [Implementation Guide](patterns/pattern-implementations) - Code examples

### Learning Resources
- [Pattern Selector Tool](patterns/pattern-selector-tool) - Find the right pattern
- [Case Studies](case-studies/) - Real-world examples
- [Anti-Patterns](patterns/anti-patterns) - What not to do
- [Pattern Combinations](patterns/pattern-combinations) - Common groupings

### Related Topics
- [The 7 Laws](part1-axioms/) - Fundamental principles
- [The 5 Pillars](part2-pillars/) - Core concepts
- [Quantitative Analysis](quantitative/) - Math behind patterns
- [Human Factors](human-factors/) - Operational excellence

---

<div class="pattern-nav" markdown>
[← Back to Home](/) | [The 7 Laws →](part1-axioms/) | [The 5 Pillars →](part2-pillars/)
</div>