# DStudio Documentation Migration Mapping Report

## Executive Summary

This report provides a comprehensive mapping for migrating the DStudio documentation from its current structure to the new 4-part architecture:

1. **Core Principles** (laws + pillars)
2. **Pattern Library** (categorized patterns) 
3. **Architect's Handbook** (case studies, playbooks, quantitative, human factors)
4. **Interview Prep** (general interview guidance)

### Migration Statistics
- **Total Files to Migrate**: 557 markdown files
- **Files to Merge**: ~50 (multi-part laws/pillars into single pages)
- **Files to Delete**: ~40 (duplicates, obsolete content, archived)
- **Orphaned Files to Integrate**: ~25 (examples, templates, misc content)
- **Company-specific Content to Generalize**: ~35 (Google/Amazon interview specific)

## Part 1: Core Principles Migration

### Current Structure → New Structure

#### Laws (7 Fundamental Laws)
**From**: `docs/part1-axioms/`  
**To**: `docs/core-principles/laws/`

| Current Location | New Location | Action | Notes |
|-----------------|--------------|--------|-------|
| `part1-axioms/index.md` | `core-principles/laws/index.md` | Move | Main laws overview |
| `part1-axioms/law-interactions.md` | `core-principles/laws/law-interactions.md` | Move | Keep as reference |
| `part1-axioms/synthesis.md` | `core-principles/laws/synthesis.md` | Move | Synthesis document |
| `part1-axioms/quiz.md` | `interview-prep/practice/laws-quiz.md` | Move | Better fit in interview prep |

##### Law 1 - Correlated Failure
| Current Location | New Location | Action | Notes |
|-----------------|--------------|--------|-------|
| `law1-failure/index.md` | `core-principles/laws/law1-correlated-failure.md` | **MERGE** | Combine all pages |
| `law1-failure/five-specters.md` | ↳ | Merge into main | Section in main doc |
| `law1-failure/architectural-lenses.md` | ↳ | Merge into main | Section in main doc |
| `law1-failure/operational-sight.md` | ↳ | Merge into main | Section in main doc |
| `law1-failure/examples.md` | ↳ | Merge into main | Examples section |
| `law1-failure/exercises.md` | `interview-prep/practice/law1-exercises.md` | Move | Interview prep |

##### Law 2 - Asynchronous Reality
| Current Location | New Location | Action | Notes |
|-----------------|--------------|--------|-------|
| `law2-asynchrony/index.md` | `core-principles/laws/law2-asynchronous-reality.md` | **MERGE** | Combine all pages |
| `law2-asynchrony/the-lens.md` | ↳ | Merge into main | |
| `law2-asynchrony/page2-specters.md` | ↳ | Merge into main | |
| `law2-asynchrony/page3-architecture.md` | ↳ | Merge into main | |
| `law2-asynchrony/page4-operations.md` | ↳ | Merge into main | |
| `law2-asynchrony/examples.md` | ↳ | Merge into main | |
| `law2-asynchrony/the-operations.md` | ↳ | Delete | Duplicate content |
| `law2-asynchrony/the-patterns.md` | ↳ | Delete | Duplicate content |

##### Laws 3-7 (Similar Pattern)
- **Law 3 - Emergent Chaos**: Merge 5 files → `law3-emergent-chaos.md`
- **Law 4 - Multidimensional Optimization**: Merge 6 files → `law4-multidimensional-optimization.md`
- **Law 5 - Distributed Knowledge**: Merge 6 files → `law5-distributed-knowledge.md`
- **Law 6 - Cognitive Load**: Merge 5 files → `law6-cognitive-load.md`
- **Law 7 - Economic Reality**: Merge 3 files → `law7-economic-reality.md`

##### Archive Content
| Current Location | Action | Notes |
|-----------------|--------|-------|
| `part1-axioms/archive-old-8-axiom-structure/*` | **DELETE** | Old structure, no longer needed |

#### Pillars (5 Foundational Pillars)
**From**: `docs/part2-pillars/`  
**To**: `docs/core-principles/pillars/`

| Current Location | New Location | Action | Notes |
|-----------------|--------------|--------|-------|
| `part2-pillars/index.md` | `core-principles/pillars/index.md` | Move | Main pillars overview |
| `part2-pillars/pillars-patterns-map.md` | `core-principles/pillars/pillars-patterns-map.md` | Move | Keep mapping |
| `part2-pillars/decision-tree.md` | `architects-handbook/decision-frameworks/pillar-decision-tree.md` | Move | Better in handbook |
| `part2-pillars/pattern-catalog-intro.md` | `pattern-library/index.md` | Merge | Into pattern library intro |
| `part2-pillars/pattern-legend.md` | `pattern-library/pattern-legend.md` | Move | Pattern library |
| `part2-pillars/pattern-matrix.md` | `pattern-library/pattern-matrix.md` | Move | Pattern library |
| `part2-pillars/models-collide.md` | `core-principles/pillars/models-collide.md` | Move | Keep in pillars |
| `part2-pillars/models-comparison.md` | `core-principles/pillars/models-comparison.md` | Move | Keep in pillars |
| `part2-pillars/tradeoff-calculus.md` | `architects-handbook/decision-frameworks/tradeoff-calculus.md` | Move | Handbook |
| `part2-pillars/pillar-checkpoint.md` | Delete | Obsolete |
| `part2-pillars/reflection-journal.md` | Delete | Obsolete |
| `part2-pillars/transition-part3.md` | Delete | Navigation artifact |

##### Individual Pillars
Each pillar follows same pattern:
- **Work Distribution**: Merge 3 files → `pillar1-work-distribution.md`
- **State Distribution**: Merge 3 files → `pillar2-state-distribution.md`
- **Truth Distribution**: Merge 3 files → `pillar3-truth-distribution.md`
- **Control Distribution**: Merge 3 files → `pillar4-control-distribution.md`
- **Intelligence Distribution**: Merge 3 files → `pillar5-intelligence-distribution.md`

## Part 2: Pattern Library Migration

### Current Structure → New Structure
**From**: `docs/patterns/`  
**To**: `docs/pattern-library/`

#### Pattern Organization by Category

##### Communication & Messaging (14 patterns)
| Pattern | From | To |
|---------|------|----| 
| API Gateway | `patterns/api-gateway.md` | `pattern-library/communication/api-gateway.md` |
| GraphQL Federation | `patterns/graphql-federation.md` | `pattern-library/communication/graphql-federation.md` |
| Service Mesh | `patterns/service-mesh.md` | `pattern-library/communication/service-mesh.md` |
| Publish-Subscribe | `patterns/publish-subscribe.md` | `pattern-library/communication/publish-subscribe.md` |
| WebSocket | `patterns/websocket.md` | `pattern-library/communication/websocket.md` |
| Request Routing | `patterns/request-routing.md` | `pattern-library/communication/request-routing.md` |
| Service Discovery | `patterns/service-discovery.md` | `pattern-library/communication/service-discovery.md` |
| Service Registry | `patterns/service-registry.md` | `pattern-library/communication/service-registry.md` |
| Ambassador | `patterns/ambassador.md` | `pattern-library/communication/ambassador.md` |
| Backends for Frontends | `patterns/backends-for-frontends.md` | `pattern-library/communication/backends-for-frontends.md` |
| Single Socket Channel | `patterns/single-socket-channel.md` | `pattern-library/communication/single-socket-channel.md` |
| Thick Client | `patterns/thick-client.md` | `pattern-library/communication/thick-client.md` |
| Event-Driven | `patterns/event-driven.md` | `pattern-library/communication/event-driven.md` |
| Choreography | `patterns/choreography.md` | `pattern-library/communication/choreography.md` |

##### Data Management (30 patterns)
| Pattern | From | To |
|---------|------|----| 
| Event Sourcing | `patterns/event-sourcing.md` | `pattern-library/data-management/event-sourcing.md` |
| CQRS | `patterns/cqrs.md` | `pattern-library/data-management/cqrs.md` |
| Saga | `patterns/saga.md` | `pattern-library/data-management/saga.md` |
| CDC | `patterns/cdc.md` | `pattern-library/data-management/cdc.md` |
| Outbox | `patterns/outbox.md` | `pattern-library/data-management/outbox.md` |
| Database per Service | `patterns/database-per-service.md` | `pattern-library/data-management/database-per-service.md` |
| Shared Database | `patterns/shared-database.md` | `pattern-library/data-management/shared-database.md` |
| Singleton Database | `patterns/singleton-database.md` | `pattern-library/data-management/singleton-database.md` |
| CRDT | `patterns/crdt.md` | `pattern-library/data-management/crdt.md` |
| Eventual Consistency | `patterns/eventual-consistency.md` | `pattern-library/data-management/eventual-consistency.md` |
| Materialized View | `patterns/materialized-view.md` | `pattern-library/data-management/materialized-view.md` |
| Polyglot Persistence | `patterns/polyglot-persistence.md` | `pattern-library/data-management/polyglot-persistence.md` |
| Read Repair | `patterns/read-repair.md` | `pattern-library/data-management/read-repair.md` |
| Tunable Consistency | `patterns/tunable-consistency.md` | `pattern-library/data-management/tunable-consistency.md` |
| WAL | `patterns/wal.md` | `pattern-library/data-management/wal.md` |
| Segmented Log | `patterns/segmented-log.md` | `pattern-library/data-management/segmented-log.md` |
| LSM Tree | `patterns/lsm-tree.md` | `pattern-library/data-management/lsm-tree.md` |
| Merkle Trees | `patterns/merkle-trees.md` | `pattern-library/data-management/merkle-trees.md` |
| Bloom Filter | `patterns/bloom-filter.md` | `pattern-library/data-management/bloom-filter.md` |
| Event Streaming | `patterns/event-streaming.md` | `pattern-library/data-management/event-streaming.md` |
| Kappa Architecture | `patterns/kappa-architecture.md` | `pattern-library/data-management/kappa-architecture.md` |
| Lambda Architecture | `patterns/lambda-architecture.md` | `pattern-library/data-management/lambda-architecture.md` |
| Data Lake | `patterns/data-lake.md` | `pattern-library/data-management/data-lake.md` |
| Data Mesh | `patterns/data-mesh.md` | `pattern-library/data-management/data-mesh.md` |
| Stored Procedures | `patterns/stored-procedures.md` | `pattern-library/data-management/stored-procedures.md` |
| Distributed Storage | `patterns/distributed-storage.md` | `pattern-library/data-management/distributed-storage.md` |
| Low High Water Marks | `patterns/low-high-water-marks.md` | `pattern-library/data-management/low-high-water-marks.md` |
| Deduplication | `patterns/deduplication.md` | `pattern-library/data-management/deduplication.md` |
| Delta Sync | `patterns/delta-sync.md` | `pattern-library/data-management/delta-sync.md` |
| State Watch | `patterns/state-watch.md` | `pattern-library/data-management/state-watch.md` |

##### Resilience & Fault Tolerance (20 patterns)
| Pattern | From | To |
|---------|------|----| 
| Circuit Breaker | `patterns/circuit-breaker.md` | `pattern-library/resilience/circuit-breaker.md` |
| Retry & Backoff | `patterns/retry-backoff.md` | `pattern-library/resilience/retry-backoff.md` |
| Timeout | `patterns/timeout.md` | `pattern-library/resilience/timeout.md` |
| Bulkhead | `patterns/bulkhead.md` | `pattern-library/resilience/bulkhead.md` |
| Health Check | `patterns/health-check.md` | `pattern-library/resilience/health-check.md` |
| Failover | `patterns/failover.md` | `pattern-library/resilience/failover.md` |
| Graceful Degradation | `patterns/graceful-degradation.md` | `pattern-library/resilience/graceful-degradation.md` |
| Heartbeat | `patterns/heartbeat.md` | `pattern-library/resilience/heartbeat.md` |
| Load Shedding | `patterns/load-shedding.md` | `pattern-library/resilience/load-shedding.md` |
| Split Brain | `patterns/split-brain.md` | `pattern-library/resilience/split-brain.md` |
| Fault Tolerance | `patterns/fault-tolerance.md` | `pattern-library/resilience/fault-tolerance.md` |
| Idempotent Receiver | `patterns/idempotent-receiver.md` | `pattern-library/resilience/idempotent-receiver.md` |
| Backpressure | `patterns/backpressure.md` | `pattern-library/resilience/backpressure.md` |
| Timeout Advanced | `patterns/timeout-advanced.md` | Merge with `timeout.md` |
| Anti-Corruption Layer | `patterns/anti-corruption-layer.md` | `pattern-library/resilience/anti-corruption-layer.md` |
| Valet Key | `patterns/valet-key.md` | `pattern-library/resilience/valet-key.md` |
| Lease | `patterns/lease.md` | `pattern-library/resilience/lease.md` |
| CAS | `patterns/cas.md` | `pattern-library/resilience/cas.md` |
| Distributed Lock | `patterns/distributed-lock.md` | `pattern-library/resilience/distributed-lock.md` |
| Emergent Leader | `patterns/emergent-leader.md` | `pattern-library/resilience/emergent-leader.md` |

##### Scaling & Performance (15 patterns)
| Pattern | From | To |
|---------|------|----| 
| Load Balancing | `patterns/load-balancing.md` | `pattern-library/scaling/load-balancing.md` |
| Sharding | `patterns/sharding.md` | `pattern-library/scaling/sharding.md` |
| Caching Strategies | `patterns/caching-strategies.md` | `pattern-library/scaling/caching-strategies.md` |
| Consistent Hashing | `patterns/consistent-hashing.md` | `pattern-library/scaling/consistent-hashing.md` |
| Auto-Scaling | `patterns/auto-scaling.md` | `pattern-library/scaling/auto-scaling.md` |
| Rate Limiting | `patterns/rate-limiting.md` | `pattern-library/scaling/rate-limiting.md` |
| Priority Queue | `patterns/priority-queue.md` | `pattern-library/scaling/priority-queue.md` |
| Request Batching | `patterns/request-batching.md` | `pattern-library/scaling/request-batching.md` |
| Scatter-Gather | `patterns/scatter-gather.md` | `pattern-library/scaling/scatter-gather.md` |
| Edge Computing | `patterns/edge-computing.md` | `pattern-library/scaling/edge-computing.md` |
| Multi-Region | `patterns/multi-region.md` | `pattern-library/scaling/multi-region.md` |
| Geo-Replication | `patterns/geo-replication.md` | `pattern-library/scaling/geo-replication.md` |
| Geo-Distribution | `patterns/geo-distribution.md` | `pattern-library/scaling/geo-distribution.md` |
| Geohashing | `patterns/geohashing.md` | `pattern-library/scaling/geohashing.md` |
| Tile Caching | `patterns/tile-caching.md` | `pattern-library/scaling/tile-caching.md` |

##### Architecture & Design (12 patterns)
| Pattern | From | To |
|---------|------|----| 
| Sidecar | `patterns/sidecar.md` | `pattern-library/architecture/sidecar.md` |
| Strangler Fig | `patterns/strangler-fig.md` | `pattern-library/architecture/strangler-fig.md` |
| Cell-Based | `patterns/cell-based.md` | `pattern-library/architecture/cell-based.md` |
| Serverless/FaaS | `patterns/serverless-faas.md` | `pattern-library/architecture/serverless-faas.md` |
| Shared Nothing | `patterns/shared-nothing.md` | `pattern-library/architecture/shared-nothing.md` |
| Actor Model | `patterns/actor-model.md` | `pattern-library/architecture/actor-model.md` |
| Blue-Green Deployment | `patterns/blue-green-deployment.md` | `pattern-library/architecture/blue-green-deployment.md` |
| Observability | `patterns/observability.md` | `pattern-library/architecture/observability.md` |
| Distributed Queue | `patterns/distributed-queue.md` | `pattern-library/architecture/distributed-queue.md` |
| Queues Streaming | `patterns/queues-streaming.md` | Merge with distributed-queue.md |
| Analytics Scale | `patterns/analytics-scale.md` | `pattern-library/architecture/analytics-scale.md` |
| ID Generation Scale | `patterns/id-generation-scale.md` | `pattern-library/architecture/id-generation-scale.md` |

##### Coordination & Consensus (10 patterns)
| Pattern | From | To |
|---------|------|----| 
| Consensus | `patterns/consensus.md` | `pattern-library/coordination/consensus.md` |
| Leader Election | `patterns/leader-election.md` | `pattern-library/coordination/leader-election.md` |
| Leader-Follower | `patterns/leader-follower.md` | `pattern-library/coordination/leader-follower.md` |
| HLC | `patterns/hlc.md` | `pattern-library/coordination/hlc.md` |
| Logical Clocks | `patterns/logical-clocks.md` | `pattern-library/coordination/logical-clocks.md` |
| Generation Clock | `patterns/generation-clock.md` | `pattern-library/coordination/generation-clock.md` |
| Clock Sync | `patterns/clock-sync.md` | `pattern-library/coordination/clock-sync.md` |
| Adaptive Scheduling | `patterns/adaptive-scheduling.md` | `pattern-library/coordination/adaptive-scheduling.md` |
| Time Series IDs | `patterns/time-series-ids.md` | `pattern-library/coordination/time-series-ids.md` |
| Chunking | `patterns/chunking.md` | `pattern-library/coordination/chunking.md` |

##### Specialized Patterns (5 patterns)
| Pattern | From | To |
|---------|------|----| 
| Spatial Indexing | `patterns/spatial-indexing.md` | `pattern-library/specialized/spatial-indexing.md` |
| URL Normalization | `patterns/url-normalization.md` | `pattern-library/specialized/url-normalization.md` |
| CAP Theorem | `patterns/cap-theorem.md` | Move to `architects-handbook/theory/cap-theorem.md` |
| Pattern Catalog | `patterns/pattern-catalog.md` | Delete - replaced by new structure |
| Pattern Relationships | `patterns/pattern-relationships.md` | `pattern-library/pattern-relationships.md` |

#### Pattern Support Files
| File | Action | Notes |
|------|--------|-------|
| `patterns/index.md` | Update | New pattern library index |
| `patterns/index-navigation.md` | Delete | Obsolete |
| `patterns/index-new.md` | Delete | Obsolete |
| `patterns/PATTERN_TEMPLATE.md` | Move to `pattern-library/PATTERN_TEMPLATE.md` | |
| `patterns/README.md` | Delete | Internal doc |
| `patterns/TRANSFORMATION_STATUS.md` | Delete | Migration artifact |
| `patterns/EXCELLENCE_METADATA_ENHANCEMENT_COMPLETE.md` | Delete | Migration artifact |
| `patterns/mkdocs-cleanup-summary.md` | Delete | Migration artifact |
| `patterns/pattern-selector-tool.md` | Move to `architects-handbook/tools/pattern-selector.md` | |
| `patterns/circuit-breaker-native.md` | Delete | Duplicate of circuit-breaker.md |

#### Excellence Framework Pattern Files
| File | New Location | Notes |
|------|--------------|-------|
| `patterns/excellence/*.md` | Move to `pattern-library/excellence-tiers/` | Keep tier guides |

## Part 3: Architect's Handbook Migration

### Current Structure → New Structure

#### Case Studies
**From**: `docs/case-studies/`  
**To**: `docs/architects-handbook/case-studies/`

##### System Design Case Studies (30 core studies)
| Category | Files | Action |
|----------|-------|--------|
| Messaging Systems | kafka.md, distributed-message-queue.md | Move to `case-studies/messaging/` |
| Databases | cassandra.md, redis.md, mongodb.md, etcd.md, spanner.md, dynamodb.md | Move to `case-studies/databases/` |
| Infrastructure | kubernetes.md, prometheus.md, vault.md, zookeeper.md | Move to `case-studies/infrastructure/` |
| Real-time Systems | uber-location.md, netflix-streaming.md, zoom-scaling.md, chat-system.md | Move to `case-studies/real-time/` |
| Social/Feed Systems | news-feed.md, social-graph.md, twitter-timeline.md | Move to `case-studies/social/` |
| Maps/Location | google-maps.md, apple-maps.md, uber-maps.md, openstreetmap.md | Move to `case-studies/location/` |
| E-commerce | payment-system.md, shopify-flash-sales.md, hotel-reservation.md | Move to `case-studies/ecommerce/` |
| Search/Discovery | elasticsearch.md, search-autocomplete.md | Move to `case-studies/search/` |
| Specialized | url-shortener.md, unique-id-generator.md, rate-limiter.md | Move to `case-studies/specialized/` |

##### Elite Engineering Studies
**From**: `docs/case-studies/elite-engineering/`  
**To**: `docs/architects-handbook/case-studies/elite-engineering/`
- Keep all 5 studies as-is (Netflix, Amazon, Discord, Figma, Stripe)

##### Google Systems Deep Dives
**From**: `docs/case-studies/google-systems/`  
**To**: Generalize and move to appropriate categories
- google-docs.md → `case-studies/collaboration/collaborative-editing.md`
- google-gmail.md → `case-studies/messaging/email-at-scale.md`
- google-maps-system.md → Merge with google-maps.md
- google-search.md → `case-studies/search/web-search-infrastructure.md`
- google-youtube.md → Merge with youtube.md

##### Case Study Support Files
| File | Action |
|------|--------|
| CASE_STUDY_TEMPLATE.md | Move to `architects-handbook/templates/` |
| STUB_CREATION_REPORT.md | Delete |
| CASE_STUDY_METADATA_PLAN.md | Delete |
| PATTERN_CASE_STUDY_LINKING_PLAN.md | Delete |

#### Human Factors
**From**: `docs/human-factors/`  
**To**: `docs/architects-handbook/human-factors/`
- Move all 12 files as-is

#### Quantitative Analysis
**From**: `docs/quantitative/`  
**To**: `docs/architects-handbook/quantitative-analysis/`

| Category | Files | Subdirectory |
|----------|-------|--------------|
| Core Laws | littles-law.md, amdahl-gustafson.md, universal-scalability.md, cap-theorem.md | `fundamentals/` |
| Performance | latency-ladder.md, performance-modeling.md, capacity-planning.md, queueing-models.md | `performance/` |
| Reliability | availability-math.md, failure-models.md, reliability-theory.md, mtbf-mttr.md | `reliability/` |
| Math/Theory | markov-chains.md, stochastic-processes.md, graph-theory.md, information-theory.md | `theory/` |
| Applied | network-theory.md, time-series.md, spatial-stats.md, computational-geometry.md | `applied/` |
| Specialized | battery-models.md, compression.md, probabilistic-structures.md | `specialized/` |

#### Excellence Framework
**From**: `docs/excellence/`  
**To**: `docs/architects-handbook/excellence-framework/`

Restructure into:
- `quick-start/` - Keep 4 quick start guides
- `implementation-guides/` - Keep all 10 guides
- `migration-center/` - All migration content
- `journeys/` - Excellence journeys
- `comparisons/` - Pattern comparisons
- `tools/` - Dashboard, wizard, etc.

#### Tools
**From**: `docs/tools/`  
**To**: `docs/architects-handbook/tools/`
- Move all 7 calculator tools

#### Reference Materials
Select files from `docs/reference/` to move:
- cheat-sheets.md → `architects-handbook/reference/cheat-sheets.md`
- glossary.md → `architects-handbook/reference/glossary.md`
- security.md → `architects-handbook/reference/security.md`
- pattern-health-dashboard.md → `architects-handbook/tools/pattern-health-dashboard.md`

## Part 4: Interview Prep Migration

### Current Structure → New Structure

#### Google Interview Content
**From**: `docs/google-interviews/`  
**To**: `docs/interview-prep/` (generalized)

| Current File | New Location | Action |
|--------------|--------------|--------|
| preparation-guide.md | `interview-prep/preparation-guide.md` | Generalize |
| architecture-patterns.md | `interview-prep/frameworks/architecture-patterns.md` | Generalize |
| scale-cheatsheet.md | `interview-prep/cheatsheets/scale-cheatsheet.md` | Keep |
| common-mistakes.md | `interview-prep/common-mistakes.md` | Generalize |
| evaluation-rubric.md | `interview-prep/frameworks/evaluation-rubric.md` | Generalize |
| tradeoff-analysis.md | `interview-prep/frameworks/tradeoff-analysis.md` | Keep |
| time-management.md | `interview-prep/time-management.md` | Keep |
| mock-questions.md | `interview-prep/practice/mock-questions.md` | Generalize |
| practice-problems.md | `interview-prep/practice/practice-problems.md` | Keep |
| visual-cheatsheets.md | `interview-prep/cheatsheets/visual-cheatsheets.md` | Keep |

**Google-specific content to archive or delete:**
- gmail.md, google-ads.md, google-assistant.md, google-calendar.md, etc.
- Company-specific walkthroughs
- Internal tech details

#### Amazon Interview Content
**From**: `docs/amazon-interviews/`  
**To**: Extract useful patterns, delete company-specific

| File | Action |
|------|--------|
| leadership-principles.md | Delete - company specific |
| amazon-ecommerce.md | Extract patterns → case studies |
| dynamodb.md | Already in case studies |
| s3.md | Extract patterns → case studies |

#### Learning Paths
**From**: `docs/learning-paths/`  
**To**: `docs/interview-prep/learning-paths/`
- Move all 9 files

#### Interview Exercises
Collect from various locations:
- All `exercises.md` files from laws/pillars → `interview-prep/practice/`
- `quantitative/problem-set.md` → `interview-prep/practice/quantitative-problems.md`
- Quiz files → `interview-prep/practice/`

## Orphaned Content Integration

### Examples Directory
**From**: `docs/examples/`
- Material showcase files → Delete (not needed)
- `circuit-breaker-annotated.md` → Merge into circuit breaker pattern
- `law1-failure-enhanced.md` → Merge into Law 1
- Layout/responsive guides → `architects-handbook/reference/layout-guide.md`

### Templates Directory
**From**: `docs/templates/`
- Pattern/law templates → Keep in respective library folders
- Homepage template → Delete
- Navigation templates → Delete

### Introduction Content
**From**: `docs/introduction/`
- Merge into new home page or quick start sections
- `philosophy.md` → `core-principles/philosophy.md`

### Miscellaneous
- `docs/includes/` → Delete (build artifacts)
- `docs/test-plan/` → Delete (internal)
- Old index files → Update for new structure

## Content Transformation Requirements

### 1. Merge Multi-part Content
- Combine 5-6 page laws into single comprehensive pages
- Merge 3-page pillars into single pages
- Keep sections but in one document

### 2. Generalize Company-specific Content
- Remove company names from titles
- Extract patterns and principles
- Focus on general system design

### 3. Update Cross-references
- Update all internal links
- Fix navigation paths
- Update pattern-to-law mappings

### 4. Standardize Frontmatter
- Ensure consistent metadata
- Add proper categories
- Include excellence tiers where applicable

### 5. Remove Obsolete Content
- Delete archived 8-axiom structure
- Remove duplicate patterns
- Clean up migration artifacts

## Implementation Priority

### Phase 1: Core Structure (Week 1)
1. Create new directory structure
2. Migrate Core Principles (laws + pillars)
3. Update navigation in mkdocs.yml

### Phase 2: Pattern Library (Week 2)
1. Categorize and move all patterns
2. Update pattern cross-references
3. Create category index pages

### Phase 3: Architect's Handbook (Week 3)
1. Migrate case studies
2. Move quantitative content
3. Organize excellence framework
4. Set up human factors

### Phase 4: Interview Prep & Cleanup (Week 4)
1. Generalize interview content
2. Organize practice materials
3. Delete obsolete files
4. Final cross-reference updates

## Success Metrics
- All 557 files properly categorized
- No broken links
- Clear 4-part navigation
- Reduced file count by ~15% through merging
- All company-specific content generalized