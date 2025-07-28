# Content Files List - Part 2: Patterns (101 Patterns)

## Patterns Core (10 files)

| File Path | Type | Nav Status | Purpose/Category |
|-----------|------|------------|------------------|
| `/home/deepak/DStudio/docs/patterns/index.md` | Index | ✅ In Nav | Main patterns overview page |
| `/home/deepak/DStudio/docs/patterns/index-new.md` | Index | ⚠️ Orphaned | Alternative patterns index |
| `/home/deepak/DStudio/docs/patterns/index-navigation.md` | Index | ⚠️ Orphaned | Navigation-specific index |
| `/home/deepak/DStudio/docs/patterns/README.md` | Guide | ⚠️ Orphaned | Repository documentation |
| `/home/deepak/DStudio/docs/patterns/PATTERN_TEMPLATE.md` | Template | ⚠️ Orphaned | Pattern authoring template |
| `/home/deepak/DStudio/docs/patterns/pattern-catalog.md` | Tool | ✅ In Nav | Comprehensive pattern catalog |
| `/home/deepak/DStudio/docs/patterns/pattern-relationships.md` | Tool | ✅ In Nav | Pattern interconnection analysis |
| `/home/deepak/DStudio/docs/patterns/pattern-selector-tool.md` | Tool | ✅ In Nav | Interactive pattern selection |
| `/home/deepak/DStudio/docs/patterns/EXCELLENCE_METADATA_ENHANCEMENT_COMPLETE.md` | Status | ⚠️ Orphaned | Enhancement completion report |
| `/home/deepak/DStudio/docs/patterns/TRANSFORMATION_STATUS.md` | Status | ⚠️ Orphaned | Transformation tracking document |

## Excellence Framework Integration (6 files)

| File Path | Type | Nav Status | Purpose/Category |
|-----------|------|------------|------------------|
| `/home/deepak/DStudio/docs/patterns/excellence/bronze-tier-guide.md` | Guide | ✅ In Nav | Bronze tier pattern guide |
| `/home/deepak/DStudio/docs/patterns/excellence/enterprise-pack.md` | Pack | ⚠️ Orphaned | Enterprise-focused pattern collection |
| `/home/deepak/DStudio/docs/patterns/excellence/gold-tier-guide.md` | Guide | ✅ In Nav | Gold tier pattern guide |
| `/home/deepak/DStudio/docs/patterns/excellence/scale-pack.md` | Pack | ⚠️ Orphaned | Scaling-focused pattern collection |
| `/home/deepak/DStudio/docs/patterns/excellence/silver-tier-guide.md` | Guide | ✅ In Nav | Silver tier pattern guide |
| `/home/deepak/DStudio/docs/patterns/excellence/starter-pack.md` | Pack | ✅ In Nav | Beginner-friendly pattern collection |

## Gold Tier Patterns (38 files) - Battle-tested, production-ready
```
# Communication & Messaging
docs/patterns/api-gateway.md                    # API Gateway
docs/patterns/event-driven.md                   # Event-driven Architecture
docs/patterns/publish-subscribe.md              # Publish-Subscribe
docs/patterns/request-routing.md                # Request Routing
docs/patterns/service-discovery.md              # Service Discovery
docs/patterns/websocket.md                      # WebSocket

# Resilience & Reliability
docs/patterns/circuit-breaker.md                # Circuit Breaker
docs/patterns/circuit-breaker-enhanced.md       # Enhanced Circuit Breaker
docs/patterns/circuit-breaker-native.md         # Native Circuit Breaker
docs/patterns/bulkhead.md                       # Bulkhead
docs/patterns/graceful-degradation.md           # Graceful Degradation
docs/patterns/health-check.md                   # Health Check
docs/patterns/heartbeat.md                      # Heartbeat
docs/patterns/retry-backoff.md                  # Retry with Backoff
docs/patterns/timeout.md                        # Timeout

# Data & Storage
docs/patterns/caching-strategies.md             # Caching Strategies
docs/patterns/database-per-service.md           # Database per Service
docs/patterns/event-sourcing.md                 # Event Sourcing
docs/patterns/materialized-view.md              # Materialized View
docs/patterns/sharding.md                       # Sharding

# Scalability & Performance
docs/patterns/auto-scaling.md                   # Auto Scaling
docs/patterns/load-balancing.md                 # Load Balancing
docs/patterns/rate-limiting.md                  # Rate Limiting
docs/patterns/consistent-hashing.md             # Consistent Hashing

# Deployment & Operations
docs/patterns/blue-green-deployment.md          # Blue-Green Deployment
docs/patterns/observability.md                  # Observability
docs/patterns/service-mesh.md                   # Service Mesh

# Coordination & Consensus
docs/patterns/leader-election.md                # Leader Election
docs/patterns/consensus.md                      # Consensus
docs/patterns/distributed-lock.md               # Distributed Lock

# Data Consistency
docs/patterns/saga.md                           # Saga Pattern
docs/patterns/saga-enhanced.md                  # Enhanced Saga
docs/patterns/eventual-consistency.md           # Eventual Consistency
docs/patterns/tunable-consistency.md            # Tunable Consistency

# Architecture Patterns
docs/patterns/backends-for-frontends.md         # Backends for Frontends
docs/patterns/sidecar.md                        # Sidecar
docs/patterns/ambassador.md                     # Ambassador
docs/patterns/strangler-fig.md                  # Strangler Fig

# Modern Patterns
docs/patterns/serverless-faas.md                # Serverless/FaaS
docs/patterns/edge-computing.md                 # Edge Computing
```

## Silver Tier Patterns (38 files) - Specialized use cases
```
# Advanced Communication
docs/patterns/choreography.md                   # Choreography
docs/patterns/graphql-federation.md             # GraphQL Federation
docs/patterns/single-socket-channel.md          # Single Socket Channel

# Advanced Resilience
docs/patterns/backpressure.md                   # Backpressure
docs/patterns/failover.md                       # Failover
docs/patterns/fault-tolerance.md                # Fault Tolerance
docs/patterns/load-shedding.md                  # Load Shedding
docs/patterns/split-brain.md                    # Split Brain
docs/patterns/timeout-advanced.md               # Advanced Timeout

# Advanced Data Patterns
docs/patterns/cqrs.md                           # CQRS
docs/patterns/outbox.md                         # Outbox Pattern
docs/patterns/cdc.md                            # Change Data Capture
docs/patterns/data-lake.md                      # Data Lake
docs/patterns/data-mesh.md                      # Data Mesh
docs/patterns/deduplication.md                  # Deduplication
docs/patterns/delta-sync.md                     # Delta Sync
docs/patterns/merkle-trees.md                   # Merkle Trees
docs/patterns/read-repair.md                    # Read Repair

# Advanced Storage & Access
docs/patterns/bloom-filter.md                   # Bloom Filter
docs/patterns/lsm-tree.md                       # LSM Tree
docs/patterns/wal.md                            # Write-Ahead Log
docs/patterns/segmented-log.md                  # Segmented Log
docs/patterns/low-high-water-marks.md           # Low/High Water Marks

# Architecture & Design
docs/patterns/actor-model.md                    # Actor Model
docs/patterns/anti-corruption-layer.md          # Anti-Corruption Layer
docs/patterns/polyglot-persistence.md           # Polyglot Persistence
docs/patterns/valet-key.md                      # Valet Key

# Coordination & Time
docs/patterns/logical-clocks.md                 # Logical Clocks
docs/patterns/hlc.md                            # Hybrid Logical Clocks
docs/patterns/clock-sync.md                     # Clock Synchronization
docs/patterns/lease.md                          # Lease

# Specialized Architecture
docs/patterns/kappa-architecture.md             # Kappa Architecture
docs/patterns/lambda-architecture.md            # Lambda Architecture
docs/patterns/multi-region.md                   # Multi-Region
docs/patterns/geo-distribution.md               # Geo Distribution
docs/patterns/geo-replication.md                # Geo Replication
docs/patterns/cell-based.md                     # Cell-based Architecture

# Processing Patterns
docs/patterns/request-batching.md               # Request Batching
docs/patterns/scatter-gather.md                 # Scatter-Gather
docs/patterns/priority-queue.md                 # Priority Queue
docs/patterns/distributed-queue.md              # Distributed Queue
```

## Bronze Tier Patterns (25 files) - Legacy or specialized
```
# Legacy Data Patterns
docs/patterns/shared-database.md                # Shared Database
docs/patterns/stored-procedures.md              # Stored Procedures
docs/patterns/singleton-database.md             # Singleton Database
docs/patterns/thick-client.md                   # Thick Client

# Legacy Architecture
docs/patterns/shared-nothing.md                 # Shared Nothing
docs/patterns/leader-follower.md                # Leader-Follower

# Specialized Patterns
docs/patterns/adaptive-scheduling.md            # Adaptive Scheduling
docs/patterns/analytics-scale.md                # Analytics at Scale
docs/patterns/cas.md                            # Compare-and-Swap
docs/patterns/chunking.md                       # Chunking
docs/patterns/crdt.md                           # CRDT
docs/patterns/distributed-storage.md            # Distributed Storage
docs/patterns/emergent-leader.md                # Emergent Leader
docs/patterns/event-streaming.md                # Event Streaming
docs/patterns/generation-clock.md               # Generation Clock
docs/patterns/geohashing.md                     # Geohashing
docs/patterns/id-generation-scale.md            # ID Generation at Scale
docs/patterns/idempotent-receiver.md            # Idempotent Receiver
docs/patterns/queues-streaming.md               # Queues vs Streaming
docs/patterns/service-registry.md               # Service Registry
docs/patterns/spatial-indexing.md               # Spatial Indexing
docs/patterns/state-watch.md                    # State Watch
docs/patterns/tile-caching.md                   # Tile Caching
docs/patterns/time-series-ids.md                # Time Series IDs
docs/patterns/url-normalization.md              # URL Normalization
```

## Archived Patterns (37 files) - Deprecated or moved
```
docs/patterns/archive/AUDIT_REPORT.md
docs/patterns/archive/DEPRECATION_NOTICE.md
docs/patterns/archive/FINAL_STATUS_REPORT.md
docs/patterns/archive/MIGRATION_REFERENCES_COMPLETE.md
docs/patterns/archive/anti-entropy.md
docs/patterns/archive/byzantine-fault-tolerance.md
docs/patterns/archive/cache-aside.md
docs/patterns/archive/consent-management.md
docs/patterns/archive/distributed-transactions.md
docs/patterns/archive/e2e-encryption.md
docs/patterns/archive/finops.md
docs/patterns/archive/gossip-protocol.md
docs/patterns/archive/key-management.md
docs/patterns/archive/location-privacy.md
docs/patterns/archive/pattern-combinations.md
docs/patterns/archive/pattern-comparison.md
docs/patterns/archive/pattern-matrix.md
docs/patterns/archive/pattern-quiz.md
docs/patterns/archive/pattern-relationships.md
docs/patterns/archive/pattern-selector.md
docs/patterns/archive/politeness.md
docs/patterns/archive/quality-check-report.md
docs/patterns/archive/read-through-cache.md
docs/patterns/archive/security-shortener.md
docs/patterns/archive/two-phase-commit.md
docs/patterns/archive/url-frontier.md
docs/patterns/archive/vector-clocks.md
docs/patterns/archive/write-behind-cache.md
docs/patterns/archive/write-through-cache.md

---

## Navigation Status Summary

### Pattern Distribution by Navigation Status
- **✅ In Nav**: 103 patterns actively included in site navigation
- **⚠️ Orphaned**: 8 pattern core files (discoverable via direct link only)
- **Archive**: 37 archived patterns (historical content, expected to be orphaned)

### Legend
- **✅ In Nav**: File is included in site navigation and discoverable through menu
- **⚠️ Orphaned**: File exists but not in navigation (discoverable via direct link only)
- **Archive**: Historical content, intentionally removed from navigation

### Pattern Quality Tiers
- **Gold Tier (38 patterns)**: Battle-tested, production-ready patterns
- **Silver Tier (38 patterns)**: Specialized use cases, advanced implementations
- **Bronze Tier (25 patterns)**: Legacy patterns or highly specialized scenarios

### Content Organization Notes
- All active patterns are included in navigation for optimal discoverability
- Pattern excellence framework provides clear tier-based organization
- Archive section maintains historical patterns for reference
- Core files include essential tools (catalog, relationships, selector) for pattern discovery