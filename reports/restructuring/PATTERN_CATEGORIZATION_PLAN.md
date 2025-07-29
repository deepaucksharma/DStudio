# Pattern Library Categorization Plan

## Overview
Total patterns analyzed: 105 (excluding index and meta files)
Target structure: 6 primary categories in pattern-library/

## Category Distribution

### 1. Communication Patterns (19 patterns)
Patterns for inter-service communication, messaging, and API management.

#### Gold Tier (7)
- **API Gateway Pattern** (`api-gateway.md`) - Central entry point for microservices
- **Distributed Queue** (`distributed-queue.md`) - Reliable message queuing
- **Event Sourcing** (`event-sourcing.md`) - State as event stream
- **Publish-Subscribe** (`publish-subscribe.md`) - Decoupled messaging
- **Queues & Stream Processing** (`queues-streaming.md`) - Message processing patterns
- **Sidecar Pattern** (`sidecar.md`) - Auxiliary service container
- **WebSocket Pattern** (`websocket.md`) - Real-time bidirectional communication

#### Silver Tier (12)
- **Ambassador Pattern** (`ambassador.md`) - Proxy for external services
- **Anti-Corruption Layer** (`anti-corruption-layer.md`) - Legacy system integration
- **Backends For Frontends** (`backends-for-frontends.md`) - Client-specific APIs
- **Data Mesh Pattern** (`data-mesh.md`) - Decentralized data architecture
- **Event Streaming** (`event-streaming.md`) - Continuous event processing
- **Event-Driven Architecture** (`event-driven.md`) - Event-based systems
- **Eventual Consistency** (`eventual-consistency.md`) - Relaxed consistency model
- **GraphQL Federation** (`graphql-federation.md`) - Distributed GraphQL
- **Priority Queue** (`priority-queue.md`) - Prioritized message processing
- **Request Batching** (`request-batching.md`) - Batch request optimization
- **Request Routing** (`request-routing.md`) - Dynamic request dispatch
- **Service Mesh** (`service-mesh.md`) - Infrastructure layer for services

### 2. Resilience Patterns (13 patterns)
Patterns for fault tolerance, error handling, and system stability.

#### Gold Tier (4)
- **Circuit Breaker** (`circuit-breaker.md`) - Prevent cascading failures
- **Health Check** (`health-check.md`) - Service health monitoring
- **Retry & Backoff** (`retry-backoff.md`) - Intelligent retry strategies
- **Timeout** (`timeout.md`) - Request timeout management

#### Silver Tier (9)
- **Backpressure** (`backpressure.md`) - Flow control mechanism
- **Bulkhead** (`bulkhead.md`) - Resource isolation
- **Circuit Breaker Native** (`circuit-breaker-native.md`) - Platform-specific implementation
- **Failover** (`failover.md`) - Automatic failure recovery
- **Fault Tolerance** (`fault-tolerance.md`) - General resilience strategies
- **Graceful Degradation** (`graceful-degradation.md`) - Reduced functionality mode
- **Heartbeat** (`heartbeat.md`) - Liveness detection
- **Load Shedding** (`load-shedding.md`) - Overload protection
- **Timeout Advanced** (`timeout-advanced.md`) - Complex timeout scenarios

### 3. Data Management Patterns (15 patterns)
Patterns for data consistency, storage, and transactions.

#### Gold Tier (4)
- **CRDT** (`crdt.md`) - Conflict-free replicated data types
- **Database per Service** (`database-per-service.md`) - Service data isolation
- **Materialized View** (`materialized-view.md`) - Precomputed query results
- **Saga Pattern** (`saga.md`) - Distributed transactions

#### Silver Tier (8)
- **CQRS** (`cqrs.md`) - Command query separation
- **Change Data Capture** (`cdc.md`) - Data change tracking
- **Distributed Storage** (`distributed-storage.md`) - Distributed data storage
- **Outbox Pattern** (`outbox.md`) - Reliable event publishing
- **Polyglot Persistence** (`polyglot-persistence.md`) - Multiple database types
- **Read Repair** (`read-repair.md`) - Consistency repair mechanism
- **Tunable Consistency** (`tunable-consistency.md`) - Adjustable consistency levels
- **Write-Ahead Log** (`wal.md`) - Durability mechanism

#### Bronze Tier (3)
- **Data Lake** (`data-lake.md`) - Large-scale data storage
- **Shared Database** (`shared-database.md`) - Shared data antipattern
- **Singleton Database** (`singleton-database.md`) - Single database instance

### 4. Scaling Patterns (15 patterns)
Patterns for horizontal scaling, partitioning, and geographic distribution.

#### Gold Tier (5)
- **Edge Computing** (`edge-computing.md`) - Distributed edge processing
- **Geo-Replication** (`geo-replication.md`) - Geographic data replication
- **ID Generation at Scale** (`id-generation-scale.md`) - Distributed ID generation
- **Load Balancing** (`load-balancing.md`) - Request distribution
- **Sharding** (`sharding.md`) - Data partitioning

#### Silver Tier (10)
- **Analytics Scale** (`analytics-scale.md`) - Large-scale analytics
- **Auto-scaling** (`auto-scaling.md`) - Dynamic resource scaling
- **Cell-Based Architecture** (`cell-based.md`) - Isolated deployment cells
- **Chunking** (`chunking.md`) - Data chunking strategies
- **Consistent Hashing** (`consistent-hashing.md`) - Distributed hashing
- **Geo-Distribution** (`geo-distribution.md`) - Geographic distribution
- **Geohashing** (`geohashing.md`) - Spatial data indexing
- **Multi-Region** (`multi-region.md`) - Multi-region deployment
- **Scatter-Gather** (`scatter-gather.md`) - Parallel processing
- **Serverless/FaaS** (`serverless-faas.md`) - Function-based scaling

### 5. Architecture Patterns (29 patterns)
High-level structural and design patterns.

#### Gold Tier (6)
- **Bloom Filter** (`bloom-filter.md`) - Probabilistic data structure
- **Caching Strategies** (`caching-strategies.md`) - Cache patterns
- **Idempotent Receiver** (`idempotent-receiver.md`) - Duplicate handling
- **Merkle Trees** (`merkle-trees.md`) - Data verification
- **Rate Limiting** (`rate-limiting.md`) - Request throttling
- **Tile Caching** (`tile-caching.md`) - Spatial data caching

#### Silver Tier (17)
- **Adaptive Scheduling** (`adaptive-scheduling.md`) - Dynamic scheduling
- **Blue-Green Deployment** (`blue-green-deployment.md`) - Zero-downtime deployment
- **CAS** (`cas.md`) - Compare-and-swap operations
- **Deduplication** (`deduplication.md`) - Duplicate removal
- **LSM Tree** (`lsm-tree.md`) - Log-structured storage
- **Low/High Water Marks** (`low-high-water-marks.md`) - Flow control
- **Observability** (`observability.md`) - System monitoring
- **Segmented Log** (`segmented-log.md`) - Log segmentation
- **Service Discovery** (`service-discovery.md`) - Service location
- **Service Registry** (`service-registry.md`) - Service registration
- **Shared Nothing** (`shared-nothing.md`) - Isolated architecture
- **Single-Socket Channel** (`single-socket-channel.md`) - Connection pattern
- **Spatial Indexing** (`spatial-indexing.md`) - Geographic indexing
- **Strangler Fig** (`strangler-fig.md`) - Legacy migration
- **Time Series IDs** (`time-series-ids.md`) - Time-based identifiers
- **URL Normalization** (`url-normalization.md`) - URL standardization
- **Valet Key** (`valet-key.md`) - Temporary access tokens

#### Bronze Tier (6)
- **Actor Model** (`actor-model.md`) - Actor-based concurrency
- **CAP Theorem** (`cap-theorem.md`) - Consistency trade-offs
- **Kappa Architecture** (`kappa-architecture.md`) - Stream processing
- **Lambda Architecture** (`lambda-architecture.md`) - Batch + stream
- **Stored Procedures** (`stored-procedures.md`) - Database logic
- **Thick Client** (`thick-client.md`) - Client-side processing

### 6. Coordination Patterns (14 patterns)
Patterns for distributed coordination, consensus, and synchronization.

#### Gold Tier (5)
- **Consensus** (`consensus.md`) - Distributed agreement
- **Distributed Lock** (`distributed-lock.md`) - Distributed mutual exclusion
- **Hybrid Logical Clocks** (`hlc.md`) - Time synchronization
- **Leader Election** (`leader-election.md`) - Leader selection
- **State Watch** (`state-watch.md`) - State change notification

#### Silver Tier (8)
- **Clock Synchronization** (`clock-sync.md`) - Time synchronization
- **Delta Sync** (`delta-sync.md`) - Incremental synchronization
- **Emergent Leader** (`emergent-leader.md`) - Dynamic leadership
- **Generation Clock** (`generation-clock.md`) - Version tracking
- **Leader-Follower** (`leader-follower.md`) - Replication pattern
- **Lease** (`lease.md`) - Time-bound resources
- **Logical Clocks** (`logical-clocks.md`) - Causal ordering
- **Split-Brain Resolution** (`split-brain.md`) - Partition handling

#### Bronze Tier (1)
- **Choreography** (`choreography.md`) - Decentralized workflow

## Patterns to Merge/Consolidate

### Circuit Breaker Variants
- Merge `circuit-breaker.md` (gold) with `circuit-breaker-native.md` (silver)
- Keep as single comprehensive pattern with platform-specific sections

### Timeout Patterns
- Merge `timeout.md` (gold) with `timeout-advanced.md` (silver)
- Create single pattern with basic and advanced sections

### Geographic Distribution
- Consolidate `geo-distribution.md`, `geo-replication.md`, and `multi-region.md`
- Create comprehensive geo-distribution pattern with sub-sections

### Service Discovery/Registry
- Merge `service-discovery.md` and `service-registry.md`
- Single pattern covering both discovery and registration

### Event Patterns
- Consider consolidating `event-driven.md`, `event-streaming.md`, and `event-sourcing.md`
- Or clearly differentiate their specific use cases

### Database Patterns
- Merge `shared-database.md` and `singleton-database.md` (both bronze/legacy)
- Present as anti-patterns with modern alternatives

### Queue Patterns
- Evaluate merging `distributed-queue.md` and `queues-streaming.md`
- May be distinct enough to keep separate

## Implementation Notes

1. **Cross-Category Patterns**: Some patterns could fit multiple categories:
   - Distributed Queue/Storage → Could be Communication or Coordination
   - Consistent Hashing → Could be Scaling or Data Management
   - Event patterns → Could be Communication or Architecture

2. **Navigation Structure**: Consider sub-categories within each main category:
   - Communication: Messaging, API Management, Event-Based
   - Resilience: Fault Tolerance, Recovery, Protection
   - Data Management: Consistency, Storage, Transactions
   - Scaling: Partitioning, Geographic, Dynamic
   - Architecture: Structural, Deployment, Optimization
   - Coordination: Consensus, Synchronization, Leadership

3. **Pattern Relationships**: Many patterns work together:
   - Circuit Breaker + Retry + Timeout (Resilience suite)
   - Event Sourcing + CQRS + Saga (Event-driven suite)
   - Service Mesh + Service Discovery + Load Balancing (Service suite)

4. **Migration Path**: For the reorganization:
   - Create new pattern-library structure
   - Move patterns to appropriate categories
   - Update all internal cross-references
   - Create category index pages with pattern summaries
   - Add navigation breadcrumbs