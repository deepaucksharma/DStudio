---
title: Distributed Systems Patterns
description: Curated catalog of ~95 battle-tested patterns for building distributed
  systems
type: patterns-index
category: resilience
excellence_tier: silver
pattern_status: stable
---


# Distributed Systems Patterns

**~95 carefully curated patterns for building reliable, scalable distributed systems**

<div class="pattern-excellence-banner" style="background: linear-gradient(135deg, #FFD700 0%, #FFF8DC 100%); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
    <h3 style="margin-top: 0;">🏆 Excellence Tier System</h3>
    <p>Patterns are now classified by implementation maturity and real-world validation:</p>
    <div style="display: flex; gap: 2rem; margin-top: 1rem;">
        <span><strong>🥇 Gold</strong> - Battle-tested at FAANG scale</span>
        <span><strong>🥈 Silver</strong> - Proven in production</span>
        <span><strong>🥉 Bronze</strong> - Well-documented approach</span>
    </div>
</div>

!!! info "Pattern Curation"
    We've curated the most valuable patterns for modern distributed systems, focusing on practical, battle-tested solutions. Each pattern has been selected for its real-world applicability and proven impact in production systems.

!!! tip "Quick Navigation"
    - **[Pattern Catalog](#pattern-catalog)** - Sortable/filterable view
    - **[Excellence Guides](#excellence-guides)** - Best practices by tier
    - **[Pattern Packs](#pattern-packs)** - Pre-selected bundles
    - **[Pattern Health Dashboard](#pattern-health)** - Implementation metrics
    - **[By Problem Domain](#by-problem-domain)** - Organized by what you're building
    - **[By Challenge](#by-challenge)** - Find patterns for specific problems
    - **[Learning Paths](#learning-paths)** - Progressive learning tracks
    - **[Pattern Navigator](#pattern-navigator)** - Visual decision guide

## 🔍 Pattern Tier Filter

<div class="pattern-filter-container" style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
    <h4 style="margin-top: 0;">Filter Patterns by Excellence Tier:</h4>
    <div class="tier-filters" style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <label for="filter-gold" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="checkbox" id="filter-gold" checked onchange="applyFilters()"> 
            <span style="background: #FFD700; padding: 0.25rem 0.75rem; border-radius: 4px; transition: opacity 0.2s;">🥇 Gold (25 patterns)</span>
        </label>
        <label for="filter-silver" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="checkbox" id="filter-silver" checked onchange="applyFilters()"> 
            <span style="background: #C0C0C0; padding: 0.25rem 0.75rem; border-radius: 4px; transition: opacity 0.2s;">🥈 Silver (40 patterns)</span>
        </label>
        <label for="filter-bronze" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="checkbox" id="filter-bronze" checked onchange="applyFilters()"> 
            <span style="background: #CD7F32; padding: 0.25rem 0.75rem; border-radius: 4px; color: white; transition: opacity 0.2s;">🥉 Bronze (30 patterns)</span>
        </label>
    </div>
    <div style="margin-top: 1rem;">
        <button onclick="resetFilters()" style="background: #e5e7eb; color: #374151; padding: 0.5rem 1.5rem; border: none; border-radius: 4px; cursor: pointer;">Reset All Filters</button>
    </div>
</div>

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

## 📦 Pattern Packs

<div class="pattern-packs" style="margin: 2rem 0;">
    <h3>Pre-selected Pattern Bundles for Your Journey</h3>
    <div class="grid cards" markdown>
    
    - :material-rocket-launch:{ .lg .middle } **Starter Pack**
        
        ---
        
        **Perfect for**: New projects & MVPs  
        **Tier**: 🥇 Gold patterns only  
        **Time**: 2 weeks  
        
        **Includes**:
        - ✅ Circuit Breaker
        - ✅ Retry & Backoff
        - ✅ Health Check
        - ✅ Load Balancing
        - ✅ Basic Caching
        
        [🚀 Get Started](excellence/starter-pack.md)
    
    - :material-chart-line:{ .lg .middle } **Scale Pack**
        
        ---
        
        **Perfect for**: Growing from 1K to 100K users  
        **Tier**: 🥇 Gold + 🥈 Silver  
        **Time**: 4 weeks  
        
        **Includes**:
        - ✅ Sharding
        - ✅ CQRS
        - ✅ Service Mesh
        - ✅ Auto-scaling
        - ✅ Event Streaming
        
        [📈 Scale Up](excellence/scale-pack.md)
    
    - :material-office-building:{ .lg .middle } **Enterprise Pack**
        
        ---
        
        **Perfect for**: Mission-critical systems  
        **Tier**: All tiers with governance  
        **Time**: 8 weeks  
        
        **Includes**:
        - ✅ Multi-region
        - ✅ Cell-based Architecture
        - ✅ Saga Pattern
        - ✅ Zero-trust Security
        - ✅ Chaos Engineering
        
        [🏢 Go Enterprise](excellence/enterprise-pack.md)
    
    </div>
</div>

## 📊 Excellence Guides

<div class="excellence-guides" style="background: #f0f4f8; padding: 2rem; border-radius: 8px; margin: 2rem 0;">
    <h3>Pattern Implementation Best Practices by Tier</h3>
    <div class="grid cards" markdown>
    
    - :material-medal:{ .lg .middle } **Gold Tier Guide**
        
        ---
        
        **Standards**: FAANG-level implementation
        
        - Comprehensive monitoring
        - Graceful degradation
        - Zero-downtime deployment
        - Automated testing
        - Performance benchmarks
        
        [📖 Gold Standards](excellence/gold-tier-guide.md)
    
    - :material-medal-outline:{ .lg .middle } **Silver Tier Guide**
        
        ---
        
        **Standards**: Production-ready practices
        
        - Health checks & alerts
        - Configuration management
        - Rollback procedures
        - Integration testing
        - Documentation
        
        [📖 Silver Standards](excellence/silver-tier-guide.md)
    
    - :material-trophy-outline:{ .lg .middle } **Bronze Tier Guide**
        
        ---
        
        **Standards**: Solid foundations
        
        - Basic monitoring
        - Error handling
        - Unit testing
        - Code reviews
        - README files
        
        [📖 Bronze Standards](excellence/bronze-tier-guide.md)
    
    </div>
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

## 📈 Pattern Health Dashboard

<div class="pattern-health" style="background: #e8f5e9; padding: 2rem; border-radius: 8px; margin: 2rem 0;">
    <h3>Real-time Pattern Implementation Metrics</h3>
    <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #5448C8;">95</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Total Patterns</p>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #FFD700;">25</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Gold Tier</p>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #C0C0C0;">40</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Silver Tier</p>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #CD7F32;">30</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Bronze Tier</p>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #10b981;">87%</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Implementation Success</p>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 4px; text-align: center;">
            <h4 style="margin: 0; color: #3b82f6;">4.2/5</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Avg. Satisfaction</p>
        </div>
    </div>
    <div style="margin-top: 1.5rem; text-align: center;">
        <a href="excellence/pattern-health-dashboard.md" style="background: #5448C8; color: white; padding: 0.75rem 2rem; text-decoration: none; border-radius: 4px; display: inline-block;">View Full Dashboard →</a>
    </div>
</div>

## 📊 Pattern Comparison

### Consensus Patterns
| Pattern | Tier | Fault Tolerance | Performance | Complexity | Use Case |
|---------|------|----------------|-------------|------------|----------|
| [Raft](patterns/consensus) | 🥇 Gold | n/2 | Fast | Medium | General purpose |
| [Paxos](patterns/consensus) | 🥈 Silver | n/2 | Medium | High | Academic/proven |
| [PBFT](patterns/byzantine-fault-tolerance) | 🥉 Bronze | n/3 | Slow | Very High | Byzantine faults |
| [Gossip](patterns/emergent-leader) | 🥈 Silver | High | Variable | Low | Eventual consistency |

### Caching Patterns
| Pattern | Tier | Consistency | Complexity | Performance | Use Case |
|---------|------|------------|------------|-------------|----------|
| [Cache Aside](patterns/cache-aside) | 🥇 Gold | Eventual | Low | Good | Read heavy |
| [Read Through](patterns/read-through-cache) | 🥈 Silver | Eventual | Medium | Better | Transparent |
| [Write Through](patterns/write-through-cache) | 🥈 Silver | Strong | Medium | Slower | Consistency |
| [Write Behind](patterns/write-behind-cache) | 🥉 Bronze | Eventual | High | Fastest | Write heavy |

### Transaction Patterns
| Pattern | Tier | Consistency | Availability | Partition Tolerance | Use Case |
|---------|------|------------|--------------|-------------------|----------|
| [Saga](patterns/saga) | 🥈 Silver | Eventual | High | Yes | Multi-DC |
| [Saga](patterns/saga) | 🥈 Silver | Eventual | High | Yes | Microservices |
| [TCC](patterns/tcc) | 🥉 Bronze | Eventual | High | Yes | Business trans |
| [Outbox](patterns/outbox) | 🥈 Silver | Eventual | High | Yes | Event + DB |

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

<script>
// Pattern tier filtering functionality with localStorage persistence
function applyFilters() {
    const goldChecked = document.getElementById('filter-gold').checked;
    const silverChecked = document.getElementById('filter-silver').checked;
    const bronzeChecked = document.getElementById('filter-bronze').checked;
    
    // Save filter preferences
    localStorage.setItem('patternFilters', JSON.stringify({
        gold: goldChecked,
        silver: silverChecked,
        bronze: bronzeChecked
    }));
    
    const tables = document.querySelectorAll('table');
    let totalVisible = 0;
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            // Check if this table has a tier column
            const headers = table.querySelectorAll('th');
            let tierIndex = -1;
            headers.forEach((header, index) => {
                if (header.textContent.includes('Tier')) {
                    tierIndex = index;
                }
            });
            
            if (tierIndex !== -1) {
                const tierCell = row.cells[tierIndex]?.textContent || '';
                let shouldShow = false;
                
                if (goldChecked && tierCell.includes('Gold')) shouldShow = true;
                if (silverChecked && tierCell.includes('Silver')) shouldShow = true;
                if (bronzeChecked && tierCell.includes('Bronze')) shouldShow = true;
                
                // Add smooth transition
                if (shouldShow) {
                    row.style.display = '';
                    row.classList.add('pattern-visible');
                    totalVisible++;
                } else {
                    row.style.display = 'none';
                    row.classList.remove('pattern-visible');
                }
            }
        });
    });
    
    updatePatternCount(totalVisible);
    updateFilterBadges();
}

function resetFilters() {
    document.getElementById('filter-gold').checked = true;
    document.getElementById('filter-silver').checked = true;
    document.getElementById('filter-bronze').checked = true;
    localStorage.removeItem('patternFilters');
    applyFilters();
}

function updatePatternCount(count) {
    // Count total patterns across all tables
    let totalPatterns = 0;
    document.querySelectorAll('table').forEach(table => {
        const headers = table.querySelectorAll('th');
        let hasTierColumn = false;
        headers.forEach(header => {
            if (header.textContent.includes('Tier')) {
                hasTierColumn = true;
            }
        });
        if (hasTierColumn) {
            totalPatterns += table.querySelectorAll('tbody tr').length;
        }
    });
    
    const countElement = document.getElementById('pattern-count-display');
    if (!countElement) {
        const filterContainer = document.querySelector('.pattern-filter-container');
        const countDiv = document.createElement('div');
        countDiv.id = 'pattern-count-display';
        countDiv.style.cssText = 'margin-top: 1rem; font-weight: 500; color: #5448C8;';
        filterContainer.insertBefore(countDiv, filterContainer.querySelector('div[style*="margin-top: 1rem;"]'));
    }
    
    document.getElementById('pattern-count-display').innerHTML = `
        Showing <strong>${count || 0}</strong> of <strong>${totalPatterns}</strong> patterns
    `;
}

function updateFilterBadges() {
    const goldChecked = document.getElementById('filter-gold').checked;
    const silverChecked = document.getElementById('filter-silver').checked;
    const bronzeChecked = document.getElementById('filter-bronze').checked;
    
    // Update badge styles based on selection
    const goldBadge = document.querySelector('label[for="filter-gold"] span');
    const silverBadge = document.querySelector('label[for="filter-silver"] span');
    const bronzeBadge = document.querySelector('label[for="filter-bronze"] span');
    
    if (goldBadge) goldBadge.style.opacity = goldChecked ? '1' : '0.5';
    if (silverBadge) silverBadge.style.opacity = silverChecked ? '1' : '0.5';
    if (bronzeBadge) bronzeBadge.style.opacity = bronzeChecked ? '1' : '0.5';
}

// Pattern search functionality with highlighting
function searchPatterns(query) {
    const tables = document.querySelectorAll('table');
    const searchTerm = query.toLowerCase();
    let totalVisible = 0;
    
    // Also consider current tier filters
    const goldChecked = document.getElementById('filter-gold').checked;
    const silverChecked = document.getElementById('filter-silver').checked;
    const bronzeChecked = document.getElementById('filter-bronze').checked;
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        const headers = table.querySelectorAll('th');
        let tierIndex = -1;
        
        headers.forEach((header, index) => {
            if (header.textContent.includes('Tier')) {
                tierIndex = index;
            }
        });
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const tierCell = tierIndex !== -1 ? row.cells[tierIndex]?.textContent || '' : '';
            
            // Check if matches search
            const matchesSearch = !searchTerm || text.includes(searchTerm);
            
            // Check if matches tier filter
            let matchesTier = tierIndex === -1; // If no tier column, show all
            if (tierIndex !== -1) {
                if (goldChecked && tierCell.includes('Gold')) matchesTier = true;
                if (silverChecked && tierCell.includes('Silver')) matchesTier = true;
                if (bronzeChecked && tierCell.includes('Bronze')) matchesTier = true;
            }
            
            const shouldShow = matchesSearch && matchesTier;
            
            if (shouldShow) {
                row.style.display = '';
                row.classList.add('pattern-visible');
                totalVisible++;
            } else {
                row.style.display = 'none';
                row.classList.remove('pattern-visible');
            }
        });
    });
    
    updatePatternCount(totalVisible);
}

// Quick pattern selector by problem domain
function selectByProblem(problem) {
    const problemPatterns = {
        'performance': ['Caching', 'CDN', 'Edge Computing', 'Request Batching', 'Load Balancing', 'Auto-scaling', 'Materialized View'],
        'reliability': ['Circuit Breaker', 'Retry', 'Bulkhead', 'Failover', 'Health Check', 'Timeout', 'Graceful Degradation'],
        'scalability': ['Sharding', 'Load Balancing', 'Auto-scaling', 'Service Mesh', 'CDN', 'Edge Computing', 'Consistent Hashing'],
        'consistency': ['Saga', 'CQRS', 'Event Sourcing', 'Distributed Lock', 'Leader Election', 'Consensus', 'Logical Clocks'],
        'coordination': ['Leader Election', 'State Watch', 'Consensus', 'Distributed Lock', 'Saga', 'Lease', 'Generation Clock']
    };
    
    const patterns = problemPatterns[problem] || [];
    const tables = document.querySelectorAll('table');
    let totalVisible = 0;
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent;
            const shouldShow = patterns.some(p => text.includes(p));
            
            if (shouldShow) {
                row.style.display = '';
                row.classList.add('pattern-visible');
                totalVisible++;
            } else {
                row.style.display = 'none';
                row.classList.remove('pattern-visible');
            }
        });
    });
    
    updatePatternCount(totalVisible);
    
    // Clear search box when using problem selector
    const searchBox = document.getElementById('pattern-search');
    if (searchBox) searchBox.value = '';
}

// Load saved filters on page load
function loadSavedFilters() {
    const savedFilters = localStorage.getItem('patternFilters');
    if (savedFilters) {
        const filters = JSON.parse(savedFilters);
        document.getElementById('filter-gold').checked = filters.gold !== false;
        document.getElementById('filter-silver').checked = filters.silver !== false;
        document.getElementById('filter-bronze').checked = filters.bronze !== false;
        applyFilters();
    } else {
        // Default: all checked
        applyFilters();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add search box to tables with patterns
    const tables = document.querySelectorAll('table');
    let hasPatternTable = false;
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach(header => {
            if (header.textContent.includes('Pattern') || header.textContent.includes('Tier')) {
                hasPatternTable = true;
            }
        });
    });
    
    if (hasPatternTable && !document.getElementById('pattern-search')) {
        const firstPatternTable = document.querySelector('table');
        if (firstPatternTable) {
            const searchBox = document.createElement('div');
            searchBox.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <input type="text" id="pattern-search" placeholder="Search patterns by name, category, or description..." 
                           style="width: 100%; padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 4px; font-size: 1rem;"
                           onkeyup="searchPatterns(this.value)">
                </div>
            `;
            firstPatternTable.parentNode.insertBefore(searchBox, firstPatternTable);
        }
    }
    
    // Add problem domain quick filters
    const filterContainer = document.querySelector('.pattern-filter-container');
    if (filterContainer && !document.getElementById('problem-selector')) {
        const problemSelector = document.createElement('div');
        problemSelector.id = 'problem-selector';
        problemSelector.innerHTML = `
            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb;">
                <h4 style="margin-top: 0;">Quick Filter by Problem Domain:</h4>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                    <button onclick="selectByProblem('performance')" style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s;">⚡ Performance</button>
                    <button onclick="selectByProblem('reliability')" style="background: #ef4444; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s;">🛡️ Reliability</button>
                    <button onclick="selectByProblem('scalability')" style="background: #10b981; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s;">📈 Scalability</button>
                    <button onclick="selectByProblem('consistency')" style="background: #f59e0b; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s;">🔒 Consistency</button>
                    <button onclick="selectByProblem('coordination')" style="background: #8b5cf6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s;">🤝 Coordination</button>
                </div>
            </div>
        `;
        filterContainer.appendChild(problemSelector);
    }
    
    // Load saved filters
    loadSavedFilters();
    
    // Add hover effects to buttons
    const style = document.createElement('style');
    style.textContent = `
        .pattern-filter-container button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .pattern-filter-container button:active {
            transform: translateY(0);
        }
        .pattern-visible {
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        #pattern-search:focus {
            outline: none;
            border-color: #5448C8;
            box-shadow: 0 0 0 3px rgba(84, 72, 200, 0.1);
        }
        table tbody tr {
            transition: opacity 0.2s ease-in-out;
        }
    `;
    document.head.appendChild(style);
});
</script>