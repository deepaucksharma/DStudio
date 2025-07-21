# Design a Nearby Friends System

!!! info "Case Study Overview"
    **System**: Real-time location sharing for finding friends nearby  
    **Scale**: 500M+ users, continuous location updates, privacy-first  
    **Challenges**: Real-time updates, battery efficiency, privacy controls, scale  
    **Key Patterns**: Pub/sub, geofencing, location quantization, privacy zones

*Estimated reading time: 40 minutes*

## Introduction

Nearby Friends represents one of the most challenging location-based services: continuously tracking and sharing user locations while maintaining privacy, battery efficiency, and real-time performance. Unlike static POI searches, this system must handle hundreds of millions of users constantly moving, with friend relationships creating a complex graph of who can see whom. From Snapchat's Snap Map to Facebook's Nearby Friends, these systems must balance the physics of continuous location updates with the human need for privacy and control. Let's explore how distributed systems principles enable finding friends in real-time while respecting boundaries.

## Part 1: Concept Map - The Physics of Moving Friends

### Axiom 1: Latency - Real-time Friend Discovery

Location updates must propagate fast enough to show friends' movements in near real-time.

```mermaid
graph LR
    subgraph "Update Propagation Pipeline"
        GPS[GPS Update<br/>1-5 sec] --> CLIENT[Client Filter<br/>10ms]
        CLIENT --> PUBLISH[Publish Location<br/>50ms]
        PUBLISH --> MATCH[Friend Matching<br/>20ms]
        MATCH --> NOTIFY[Push Notification<br/>100ms]
        NOTIFY --> DISPLAY[Friend Display<br/>10ms]
    end
```

**Latency Budget Breakdown:**

| Component | Target Latency | Optimization Strategy |
|-----------|---------------|----------------------|
| Location Acquisition | 1-5 seconds | Fused location providers |
| Update Batching | 100ms | Intelligent batching |
| Network Transit | 20-50ms | Regional endpoints |
| Friend Matching | 10-30ms | Geohash indexing |
| Notification Delivery | 50-200ms | Push notification services |
| End-to-End | < 2 seconds | Parallel processing |

**Battery vs Latency Trade-offs:**

```mermaid
graph TB
    subgraph "Update Frequency Strategies"
        STATIC[Static<br/>No movement<br/>Update: 5 min] 
        WALKING[Walking<br/>3-5 km/h<br/>Update: 30 sec]
        DRIVING[Driving<br/>30+ km/h<br/>Update: 10 sec]
        
        STATIC --> BATTERY1[Battery: 1%/day]
        WALKING --> BATTERY2[Battery: 5%/day]
        DRIVING --> BATTERY3[Battery: 15%/day]
    end
```

### Axiom 2: Capacity - The N×M Friend Location Problem

Each user has M friends, creating N×M potential location relationships to track.

```mermaid
graph TB
    subgraph "Scaling Challenge"
        U1[User 1<br/>200 friends] --> LOC1[Location Updates]
        U2[User 2<br/>150 friends] --> LOC2[Location Updates]
        UN[User N<br/>Avg 130 friends] --> LOCN[Location Updates]
        
        LOC1 & LOC2 & LOCN --> MATCHER[Friend Matcher<br/>N × M checks]
        
        MATCHER --> INDEX[Spatial Index<br/>Optimize lookups]
    end
```

**Capacity Planning:**

| Metric | Scale | Impact |
|--------|-------|--------|
| Active Users | 500M | Base load |
| Average Friends | 130 | Relationship complexity |
| Location Updates/User/Day | 288 (every 5 min) | Write load |
| Total Updates/Day | 144B | System throughput |
| Storage per Update | 100 bytes | 14.4TB/day |
| Query Load | 1M QPS | Read amplification |

**Data Reduction Strategies:**

```mermaid
graph LR
    subgraph "Optimization Techniques"
        RAW[Raw GPS<br/>~200 bytes] --> QUANTIZE[Location Quantization<br/>~50 bytes]
        QUANTIZE --> COMPRESS[Delta Compression<br/>~20 bytes]
        COMPRESS --> DEDUPE[Deduplication<br/>~10 bytes]
        
        RAW -.->|95% reduction| DEDUPE
    end
```

### Axiom 3: Failure - Privacy-First Failure Modes

System must fail closed - never expose location without explicit permission.

```mermaid
graph TB
    subgraph "Privacy-Safe Failures"
        UPDATE[Location Update] --> CHECK{Permission Valid?}
        CHECK -->|Yes| PROCEED[Process Update]
        CHECK -->|No/Unknown| BLOCK[Block Update]
        
        PROCEED --> VERIFY{Friend Status?}
        VERIFY -->|Confirmed| SHARE[Share Location]
        VERIFY -->|Uncertain| HIDE[Hide Location]
        
        BLOCK & HIDE --> LOG[Audit Log]
    end
```

**Failure Scenarios and Privacy:**

| Failure Type | Privacy Impact | Mitigation |
|--------------|---------------|------------|
| Permission Service Down | Could expose location | Fail closed - hide all |
| Friend Graph Inconsistent | Wrong people see location | Cache last known good state |
| Location Service Error | Stale locations shown | Clear TTL, show uncertainty |
| Notification Failure | Friends unaware of presence | Retry with backoff |
| Regional Outage | Friends appear offline | Graceful degradation |

### Axiom 4: Concurrency - Millions Moving Simultaneously

Handle concurrent location updates from millions of users efficiently.

```mermaid
graph TB
    subgraph "Concurrent Update Processing"
        subgraph "Sharded by User"
            SHARD1[Shard 1<br/>Users A-F] --> WORKER1[Workers 1-10]
            SHARD2[Shard 2<br/>Users G-M] --> WORKER2[Workers 11-20]
            SHARDN[Shard N<br/>Users T-Z] --> WORKERN[Workers 91-100]
        end
        
        subgraph "Location Pipeline"
            WORKER1 --> SPATIAL[Spatial Index Update]
            WORKER2 --> SPATIAL
            WORKERN --> SPATIAL
            
            SPATIAL --> PUBSUB[Pub/Sub System]
            PUBSUB --> SUBSCRIBERS[Friend Subscribers]
        end
    end
```

**Concurrency Patterns:**

| Pattern | Use Case | Throughput |
|---------|----------|------------|
| User Sharding | Partition by user ID | 1M updates/sec |
| Location Bucketing | Group nearby updates | 10x efficiency |
| Batch Processing | Aggregate updates | 5x throughput |
| Read Replicas | Scale friend queries | 10M reads/sec |
| Write-Through Cache | Recent locations | 90% cache hit |

### Axiom 5: Coordination - Global Friend Graph Consistency

Maintaining consistent friend relationships and permissions across regions.

```mermaid
graph TB
    subgraph "Multi-Region Coordination"
        subgraph "US Region"
            US_USER[US Users] --> US_GRAPH[Friend Graph]
            US_GRAPH --> US_PERMS[Permissions]
        end
        
        subgraph "EU Region"
            EU_USER[EU Users] --> EU_GRAPH[Friend Graph]
            EU_GRAPH --> EU_PERMS[Permissions]
        end
        
        US_GRAPH <-->|Sync| GLOBAL[Global Graph Service]
        EU_GRAPH <-->|Sync| GLOBAL
        
        GLOBAL --> CONFLICT[Conflict Resolution<br/>Last Write Wins]
    end
```

**Consistency Requirements:**

| Data Type | Consistency Model | Sync Latency | Rationale |
|-----------|------------------|--------------|-----------|
| Friend Relationships | Strong | Immediate | Privacy critical |
| Location Sharing Permissions | Strong | Immediate | Privacy critical |
| Current Location | Eventual | < 5 seconds | Performance trade-off |
| Location History | Eventual | < 1 minute | Not real-time critical |
| Presence Status | Causal | < 10 seconds | User experience |

### Axiom 6: Observability - Privacy-Aware Monitoring

Monitor system health without compromising user privacy.

```mermaid
graph LR
    subgraph "Privacy-Preserving Metrics"
        RAW[Raw Events] --> ANONYMIZE[Anonymizer]
        ANONYMIZE --> AGG[Aggregator]
        AGG --> METRICS[System Metrics]
        
        METRICS --> DASH[Dashboard]
        METRICS --> ALERT[Alerts]
        
        RAW -.->|No Direct Access| DASH
    end
```

**Key Metrics (Privacy-Safe):**

| Metric Category | Examples | Privacy Considerations |
|----------------|----------|----------------------|
| System Health | Update latency, Error rates | No user identifiers |
| Usage Patterns | Updates/hour, Active regions | Aggregated only |
| Privacy Controls | Permission changes/day | Anonymous counts |
| Battery Impact | Update frequency distribution | Device-type aggregated |
| Friend Graph | Average friend count | Statistical only |

### Axiom 7: Human Interface - Privacy and Control

Give users intuitive control over their location sharing.

```mermaid
graph TB
    subgraph "Privacy Controls"
        USER[User] --> GLOBAL{Global Toggle}
        GLOBAL -->|On| GRANULAR[Granular Controls]
        GLOBAL -->|Off| HIDDEN[Completely Hidden]
        
        GRANULAR --> TIME[Time-based<br/>"Next 1 hour"]
        GRANULAR --> PEOPLE[People-based<br/>"Close friends only"]
        GRANULAR --> LOCATION[Location-based<br/>"Not at home"]
        GRANULAR --> PRECISION[Precision<br/>"City-level only"]
    end
```

**Privacy Feature Matrix:**

| Feature | Implementation | User Benefit |
|---------|---------------|--------------|
| Ghost Mode | Hide from everyone | Complete privacy |
| Selective Sharing | Choose specific friends | Granular control |
| Location Fuzzing | Reduce precision | Privacy with sharing |
| Time Limits | Auto-expire sharing | Temporary sharing |
| Geofencing | Hide in certain areas | Location-based privacy |
| Activity-based | Hide when stationary | Context awareness |

### Axiom 8: Economics - Balancing Features and Costs

Optimize costs while providing free service to hundreds of millions.

```mermaid
graph TB
    subgraph "Cost Model"
        USERS[500M Users] --> UPDATES[144B Updates/Day]
        UPDATES --> COSTS[Infrastructure Costs]
        
        COSTS --> COMPUTE[Compute: $2M/month]
        COSTS --> STORAGE[Storage: $500K/month]
        COSTS --> NETWORK[Network: $1M/month]
        
        REVENUE[Revenue Streams] --> ADS[Location Ads]
        REVENUE --> PREMIUM[Premium Features]
        REVENUE --> DATA[Anonymous Analytics]
    end
```

**Cost Optimization Strategies:**

| Strategy | Implementation | Savings |
|----------|---------------|---------|
| Update Batching | Combine nearby updates | 60% network |
| Location Quantization | Reduce precision | 70% storage |
| Inactive User Pruning | Archive old data | 40% storage |
| Edge Computing | Process locally | 50% compute |
| Adaptive Frequency | Movement-based updates | 80% battery/data |

## Part 2: Comprehensive Axiom Analysis Matrix

### Axiom Mapping for Core Design Decisions

| Design Decision | Axiom 1: Latency | Axiom 2: Capacity | Axiom 3: Failure | Axiom 4: Concurrency | Axiom 5: Coordination | Axiom 6: Observability | Axiom 7: Human Interface | Axiom 8: Economics |
|----------------|------------------|-------------------|------------------|---------------------|---------------------|---------------------|------------------------|-------------------|
| **Pub/Sub Architecture** | ✅ Real-time delivery<br/>Push model | ⚠️ Fan-out overhead<br/>N×M messages | ✅ Graceful degradation<br/>Queue persistence | ✅ Parallel delivery<br/>Natural decoupling | ⚠️ Ordering challenges<br/>Cross-region sync | ✅ Clear flow<br/>Message tracing | ✅ Instant updates<br/>Live experience | ⚠️ Infrastructure cost<br/>Message volume |
| **Geohash Clustering** | ✅ Fast friend lookup<br/>O(1) operations | ✅ Spatial efficiency<br/>Reduce comparisons | ✅ Simple recovery<br/>Stateless design | ✅ Parallel processing<br/>Independent cells | ✅ Natural sharding<br/>Geographic bounds | ✅ Clear metrics<br/>Cell-based stats | ⚠️ Grid boundaries<br/>Edge cases | ✅ Efficient indexing<br/>Low compute |
| **Privacy Zones** | ⚠️ Extra checks<br/>Small overhead | ⚠️ More metadata<br/>Zone definitions | ✅ Fail-safe design<br/>Default hidden | ✅ Zone checks parallel<br/>No blocking | ✅ Consistent rules<br/>Global policies | ⚠️ Complex tracking<br/>Zone violations | ✅ User control<br/>Clear boundaries | ✅ Reduces updates<br/>In private zones |
| **Adaptive Updates** | ✅ Optimize frequency<br/>Based on movement | ✅ Reduce volume<br/>80% fewer updates | ✅ Fallback rates<br/>Never lose user | ✅ Independent logic<br/>Per-user rates | ⚠️ Rate sync issues<br/>Clock skew | ✅ Movement patterns<br/>Clear analytics | ✅ Battery saving<br/>User happiness | ✅ Major savings<br/>Compute and network |
| **Friend Graph Cache** | ✅ Instant lookup<br/>Memory speed | ⚠️ Memory usage<br/>Redundant storage | ✅ Stale but safe<br/>Old permissions OK | ✅ Read scaling<br/>No graph locks | ⚠️ Cache coherency<br/>Update propagation | ✅ Hit rates<br/>Cache effectiveness | ✅ Fast friend list<br/>Smooth UX | ✅ Reduce DB load<br/>90% fewer queries |

### Axiom Interaction Complexity

```mermaid
graph TB
    subgraph "Nearby Friends Axiom Tensions"
        L[Low Latency] <-->|Conflicts| P[Privacy Checks]
        P <-->|Requires| C[Coordination]
        C <-->|Impacts| L
        
        B[Battery Life] <-->|Limits| U[Update Frequency]
        U <-->|Affects| L
        
        S[Scale] <-->|Drives| E[Economics]
        E <-->|Constrains| F[Features]
        F <-->|Demands| S
        
        style L fill:#ff6b6b
        style P fill:#4ecdc4
        style B fill:#95e1d3
    end
```

## Part 3: Architecture - Building Real-time Location Sharing

### Current Architecture: Pub/Sub with Spatial Indexing

```mermaid
graph TB
    subgraph "Client Layer"
        APP[Mobile App] --> LOC[Location Service]
        LOC --> FILTER[Movement Filter]
        FILTER --> BATCH[Update Batcher]
    end
    
    subgraph "Ingestion Layer"
        BATCH --> LB[Load Balancer]
        LB --> INGEST1[Ingestion Server 1]
        LB --> INGEST2[Ingestion Server 2]
        LB --> INGESTN[Ingestion Server N]
    end
    
    subgraph "Processing Layer"
        INGEST1 --> VALIDATE[Permission Validator]
        VALIDATE --> QUANTIZE[Location Quantizer]
        QUANTIZE --> INDEX[Spatial Indexer]
        
        INDEX --> GEOHASH[(Geohash Index)]
        INDEX --> PUBSUB[Pub/Sub System]
    end
    
    subgraph "Distribution Layer"
        PUBSUB --> MATCHER[Friend Matcher]
        MATCHER --> NOTIFY[Notification Service]
        NOTIFY --> PUSH[Push to Friends]
        
        MATCHER --> CACHE[(Location Cache)]
        CACHE --> API[Query API]
    end
```

### Alternative Architecture 1: Peer-to-Peer Location Sharing

```mermaid
graph TB
    subgraph "P2P Architecture"
        USER1[User 1] <-->|Direct Connection| USER2[User 2]
        USER1 <-->|Direct Connection| USER3[User 3]
        USER2 <-->|Direct Connection| USER3
        
        USER1 --> DHT[DHT Registry]
        DHT --> DISCOVER[Peer Discovery]
        
        BACKUP[Backup Server] -.->|Offline Friends| USER1
    end
```

**Trade-offs:**

| Aspect | Benefit | Challenge |
|--------|---------|-----------|
| Privacy | No central storage | Trust between peers |
| Latency | Direct connections | NAT traversal |
| Scale | Infinite | Connection management |
| Battery | Worse (always on) | Constant networking |
| Reliability | Poor | Peer churn |

### Alternative Architecture 2: Edge-Based Processing

```mermaid
graph TB
    subgraph "Edge Architecture"
        USERS[Local Users] --> EDGE[Edge Node<br/>Cell Tower]
        EDGE --> PROCESS[Local Processing]
        PROCESS --> LOCAL[Local Matching]
        
        EDGE <--> EDGE2[Nearby Edge Node]
        EDGE -.->|Overflow| CENTRAL[Central Cloud]
        
        LOCAL --> NOTIFY[Direct Notification]
    end
```

**Trade-offs:**

| Aspect | Benefit | Challenge |
|--------|---------|-----------|
| Latency | Ultra-low locally | Edge deployment |
| Privacy | Data stays local | Edge security |
| Scale | Distributed load | Many edge nodes |
| Cost | Reduced central load | Edge infrastructure |
| Complexity | High | Coordination |

### Alternative Architecture 3: Blockchain-Based

```mermaid
graph TB
    subgraph "Blockchain Location"
        USER[User] --> ENCRYPT[Encrypt Location]
        ENCRYPT --> SMART[Smart Contract]
        SMART --> CHAIN[Blockchain]
        
        FRIEND[Friend] --> REQUEST[Request Access]
        REQUEST --> VERIFY[Verify Permission]
        VERIFY --> DECRYPT[Decrypt Location]
    end
```

**Trade-offs:**

| Aspect | Benefit | Challenge |
|--------|---------|-----------|
| Privacy | Cryptographic guarantees | Key management |
| Trust | Zero trust | Slow consensus |
| Audit | Complete trail | Storage costs |
| Latency | Poor | Block time |
| Scale | Limited | Transaction fees |

### Alternative Architecture 4: Federated System

```mermaid
graph TB
    subgraph "Federated Architecture"
        subgraph "Provider A"
            USERS_A[Users A] --> SERVER_A[Server A]
        end
        
        subgraph "Provider B"
            USERS_B[Users B] --> SERVER_B[Server B]
        end
        
        SERVER_A <-->|Federation Protocol| SERVER_B
        SERVER_A <-->|Standards-based| SERVER_N[Other Servers]
    end
```

**Trade-offs:**

| Aspect | Benefit | Challenge |
|--------|---------|-----------|
| Privacy | User choice | Varying policies |
| Control | Decentralized | Protocol agreement |
| Scale | Distributed | Interoperability |
| Innovation | Multiple approaches | Lowest common denominator |
| Cost | Shared | Business model |

### Recommended Architecture: Hybrid Privacy-First System

```mermaid
graph TB
    subgraph "Privacy-First Hybrid"
        subgraph "Client Intelligence"
            APP[App] --> SMART[Smart Client]
            SMART --> LOCAL_MATCH[Local Friend Match]
            SMART --> PRECISE[Precision Control]
        end
        
        subgraph "Regional Processing"
            SMART --> REGIONAL[Regional Server]
            REGIONAL --> SPATIAL[Spatial Index]
            SPATIAL --> PRIV_FILTER[Privacy Filter]
            
            REGIONAL <--> PEER_REGION[Peer Regions]
        end
        
        subgraph "Friend Notification"
            PRIV_FILTER --> RELEVANCE[Relevance Scorer]
            RELEVANCE --> PUSH_DECIDE{Push?}
            PUSH_DECIDE -->|Important| IMMEDIATE[Immediate Push]
            PUSH_DECIDE -->|Normal| BATCH_PUSH[Batched Push]
            PUSH_DECIDE -->|Low| PULL[Available on Pull]
        end
        
        subgraph "Privacy Controls"
            PERMS[Permission Service] --> PRIV_FILTER
            ZONES[Privacy Zones] --> PRIV_FILTER
            SCHEDULE[Time Rules] --> PRIV_FILTER
        end
    end
```

## Part 4: Comparative Analysis

### Architecture Comparison Matrix

| Architecture | Privacy | Latency | Scale | Battery | Cost | Complexity |
|--------------|---------|---------|-------|---------|------|------------|
| **Pub/Sub + Spatial** | ✅✅✅ Good controls | ✅✅✅✅ < 2 sec | ✅✅✅✅✅ Billions | ✅✅✅ Adaptive | $$$ | Medium |
| **P2P** | ✅✅✅✅✅ Excellent | ✅✅✅✅✅ Direct | ✅✅ Limited | ❌ Always on | $ | High |
| **Edge-Based** | ✅✅✅✅ Local data | ✅✅✅✅✅ < 500ms | ✅✅✅✅ Good | ✅✅✅✅ Efficient | $$$$ | Very High |
| **Blockchain** | ✅✅✅✅✅ Cryptographic | ❌ Minutes | ❌ Very limited | ❌❌ Proof of work | $$$$$ | High |
| **Federated** | ✅✅✅ Variable | ✅✅✅ Good | ✅✅✅✅ Good | ✅✅✅ Standard | $$ | Medium |
| **Hybrid** | ✅✅✅✅✅ Best in class | ✅✅✅✅ < 1 sec | ✅✅✅✅✅ Billions | ✅✅✅✅✅ Optimized | $$$ | High |

### Privacy Feature Comparison

| Feature | Current | P2P | Edge | Blockchain | Federated | Hybrid |
|---------|---------|-----|------|------------|-----------|--------|
| Ghost Mode | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Selective Sharing | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Location Fuzzing | ✅ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ |
| Time Limits | ✅ | ❌ | ✅ | ✅ | ⚠️ | ✅ |
| Privacy Zones | ✅ | ❌ | ✅ | ⚠️ | ❌ | ✅ |
| Audit Trail | ⚠️ | ❌ | ⚠️ | ✅ | ⚠️ | ✅ |

### Performance Analysis

```mermaid
graph LR
    subgraph "Latency vs Scale Trade-off"
        A[P2P<br/>50ms<br/>1K users] 
        B[Edge<br/>200ms<br/>1M users]
        C[Current<br/>1s<br/>100M users]
        D[Hybrid<br/>500ms<br/>1B users]
        E[Federated<br/>2s<br/>10M users]
        F[Blockchain<br/>60s<br/>10K users]
        
        A --> B --> C --> D
        E -.-> C
        F -.-> A
    end
```

### Cost Analysis by Scale

| Users | Current | P2P | Edge | Blockchain | Federated | Hybrid |
|-------|---------|-----|------|------------|-----------|--------|
| 1M | $50K/mo | $10K/mo | $200K/mo | $500K/mo | $30K/mo | $100K/mo |
| 10M | $300K/mo | $50K/mo | $1M/mo | N/A | $200K/mo | $400K/mo |
| 100M | $2M/mo | N/A | $8M/mo | N/A | $1.5M/mo | $2.5M/mo |
| 1B | $15M/mo | N/A | $50M/mo | N/A | $10M/mo | $12M/mo |

### Decision Framework

```mermaid
graph TD
    START[Start] --> Q1{Scale Required?}
    
    Q1 -->|< 1M users| Q2{Privacy Critical?}
    Q2 -->|Yes| P2P[P2P Architecture]
    Q2 -->|No| CURRENT[Current Architecture]
    
    Q1 -->|1M - 100M| Q3{Latency Critical?}
    Q3 -->|< 500ms| EDGE[Edge Architecture]
    Q3 -->|< 2s OK| Q4{Cost Sensitive?}
    Q4 -->|Yes| FEDERATED[Federated]
    Q4 -->|No| CURRENT2[Current Architecture]
    
    Q1 -->|> 100M| Q5{Privacy Paramount?}
    Q5 -->|Yes| HYBRID[Hybrid Architecture]
    Q5 -->|Standard| CURRENT3[Current + Optimizations]
    
    style HYBRID fill:#4ecdc4
    style P2P fill:#95e1d3
```

## Implementation Best Practices

### Privacy-First Design Principles

1. **Default to Private**: Location sharing off by default
2. **Explicit Consent**: Clear opt-in for each friend
3. **Granular Control**: Time, location, and precision limits
4. **Audit Trail**: User can see who viewed their location
5. **Easy Off Switch**: One-tap to go completely private

### Battery Optimization Strategies

| Strategy | Implementation | Battery Savings |
|----------|---------------|-----------------|
| Movement Detection | Accelerometer-based | 50% GPS reduction |
| Adaptive Frequency | Speed-based updates | 70% update reduction |
| Batching | Combine updates | 30% network savings |
| Geofencing | WiFi/Cell triggers | 80% in stationary |
| Background Limits | OS integration | 40% overall |

### Scaling Strategies

1. **Geographic Sharding**: Keep friends in same region on same shards
2. **Friend Graph Caching**: Precompute friend clusters
3. **Location Quantization**: Reduce precision for distant friends
4. **Update Coalescing**: Combine rapid movements
5. **Tiered Storage**: Hot (1 day), Warm (1 week), Cold (archive)

## Conclusion

Nearby Friends systems demonstrate the complex interplay between real-time performance, privacy protection, and battery efficiency at massive scale. The hybrid architecture balances these concerns by using client-side intelligence for privacy controls, regional processing for low latency, and adaptive update strategies for battery efficiency. The key insight is that different use cases (close friends vs. acquaintances, stationary vs. moving) require different update strategies and privacy levels. Success comes from giving users granular control while making the default experience both private and performant, ensuring that finding friends nearby enhances social connections without compromising personal boundaries.