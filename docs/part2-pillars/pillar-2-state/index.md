# Pillar II: Distribution of State

!!! info "Prerequisites"
    - [Pillar 1: Distribution of Work](../pillar-1-work/index.md)
    - Understanding of [Axiom 3: Failure](../../part1-axioms/axiom-3-failure/index.md)
    - Basics of database systems

!!! tip "Quick Navigation"
    [← Pillar 1](../pillar-1-work/index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Distribution of Truth](../pillar-3-truth/index.md)

!!! target "Learning Objective"
    State is where distributed systems get hard; master the trade-offs.

## Core Concept

State distribution is the heart of distributed systems complexity. Unlike stateless work distribution, state has persistence, consistency requirements, and failure recovery challenges.

## The State Distribution Trilemma

<div class="trilemma-diagram">

```
        Consistency
            / \
           /   \
          /     \
         /       \
    Availability  Partition Tolerance
    
Pick 2, but P is mandatory in distributed systems,
so really: Choose between C and A when partitioned
```

</div>

## State Distribution Strategies

<div class="strategy-cards">

=== "Partitioning (Sharding)"
    ```
    Data universe: [A-Z]
    ├─ Shard 1: [A-H]
    ├─ Shard 2: [I-P]  
    └─ Shard 3: [Q-Z]
    
    Pros: Linear scalability
    Cons: Cross-shard queries expensive
    When: Clear partition key exists
    ```

=== "Replication"
    ```
    Master: [Complete Dataset] ← Writes
       ↓ Async replication
    Replica 1: [Complete Dataset] ← Reads
    Replica 2: [Complete Dataset] ← Reads
    
    Pros: Read scalability, fault tolerance
    Cons: Write bottleneck, lag
    When: Read-heavy workloads
    ```

=== "Caching"
    ```
    Client → Cache → Database
             ↓   ↑
          [Hot Data]
    
    Pros: Massive read performance
    Cons: Consistency complexity
    When: Temporal locality exists
    ```

</div>

## State Consistency Spectrum

<div class="consistency-spectrum">

```
Strong ←──────────────────────────────→ Eventual
  │                                          │
Linearizable                            DNS
  │                                          │
Sequential                              S3
  │                                          │
Causal                                  DynamoDB
  │                                          │
FIFO                                    Cassandra

Cost: $$$$                            $
Latency: High                         Low
Availability: Lower                   Higher
```

</div>

## The Hidden Costs of State Distribution

<div class="cost-analysis">

```
1. COGNITIVE OVERHEAD
   Single DB: Simple mental model
   Distributed: Where is this data?

2. OPERATIONAL COMPLEXITY  
   Single DB: One backup, one failover
   Distributed: N backups, complex recovery

3. CONSISTENCY GYMNASTICS
   Single DB: ACID transactions
   Distributed: Sagas, compensation

4. DEBUGGING NIGHTMARE
   Single DB: One log to check
   Distributed: Correlation across N logs
```

</div>

## Data Model Selection Matrix

<div class="data-store-matrix">

| Use Case | Best Fit | Why |
|----------|----------|-----|
| User profiles | Document DB | Flexible schema |
| Financial ledger | RDBMS | ACID required |
| Time series | TSDB | Optimized storage |
| Shopping cart | Redis | Temporary, fast |
| Log search | Elasticsearch | Full-text search |
| Social graph | Graph DB | Relationship queries |
| Analytics | Column store | Aggregation optimized |
| Files | Object store | Cheap, scalable |

</div>

## Data Model Transformation Costs

<div class="transformation-matrix">

| From → To | Difficulty | Example |
|-----------|------------|---------|
| Relational → KV | Easy | User table → user:123 |
| Relational → Doc | Medium | Denormalize joins |
| Relational → Graph | Hard | Edges from FKs |
| Document → Relation | Hard | Normalize nested |
| Graph → Relational | Very Hard | Recursive queries |
| Any → Time Series | Easy | Add timestamp |

</div>

## Polyglot Persistence Decision Framework

<div class="decision-box">

```
START: What's your primary access pattern?
│
├─ Key lookup?
│  ├─ Needs persistence? → Redis with AOF
│  └─ Cache only? → Memcached
│
├─ Complex queries?
│  ├─ Transactions? → PostgreSQL
│  ├─ Analytics? → ClickHouse
│  └─ Search? → Elasticsearch
│
├─ Relationships?
│  ├─ Social graph? → Neo4j
│  └─ Hierarchical? → Document DB
│
├─ Time-based?
│  ├─ Metrics? → Prometheus
│  └─ Events? → Kafka + S3
│
└─ Large objects?
   ├─ Frequent access? → CDN
   └─ Archive? → Glacier
```

</div>

## Sharding Strategies

### 1. Range-Based Sharding
```
User IDs 1-1M → Shard 1
User IDs 1M-2M → Shard 2
User IDs 2M-3M → Shard 3

Pros: Simple, range queries possible
Cons: Uneven distribution, hot spots
```

### 2. Hash-Based Sharding
```
shard = hash(user_id) % num_shards

Pros: Even distribution
Cons: No range queries, resharding hard
```

### 3. Consistent Hashing
```
Virtual nodes on a ring
Minimal data movement on scale

Pros: Elastic scaling
Cons: More complex
```

### 4. Geographic Sharding
```
US users → US shards
EU users → EU shards

Pros: Data locality, compliance
Cons: Cross-region queries
```

## Replication Topologies

<div class="replication-patterns">

```
1. Master-Slave
   Master → Slave1
         → Slave2
         → Slave3

2. Master-Master
   Master1 ←→ Master2

3. Chain Replication
   Head → Middle → Tail

4. Quorum-Based
   Client → {N1, N2, N3}
   W=2, R=2, N=3
```

</div>

<div class="truth-box">

**Counter-Intuitive Truth 💡**

The easiest way to scale state is to eliminate it. Every piece of state you add multiplies complexity. Before distributing state, ask: "Can this be stateless?" Often, the answer is yes with clever design.

</div>

## Common State Distribution Anti-Patterns

!!! warning "Avoid These"
    
    1. **Distributed Monolith**: Every service shares the same database
    2. **Chatty Services**: Excessive cross-service database calls
    3. **Two-Phase Commit**: Distributed transactions that block
    4. **Cache Stampede**: All instances refresh cache simultaneously
    5. **Split Brain**: Multiple masters accepting writes

## Related Concepts

- **[Axiom 2: Capacity](../../part1-axioms/axiom-2-capacity/index.md)**: State consumes finite storage
- **[Axiom 3: Failure](../../part1-axioms/axiom-3-failure/index.md)**: State must survive failures
- **[Axiom 5: Coordination](../../part1-axioms/axiom-5-coordination/index.md)**: State requires consensus

## Key Takeaways

!!! success "Remember"
    
    1. **CAP is a spectrum, not a binary** - Choose your consistency level
    2. **Sharding is powerful but complex** - Get your partition key right
    3. **Replication has lag** - Design for eventual consistency
    4. **Polyglot persistence is reality** - Right tool for right job
    5. **State coordination is expensive** - Minimize when possible

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [State Distribution Examples](examples.md) →
    
    **Practice**: [State Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of Truth](../pillar-3-truth/index.md) →
    
    **Jump to**: [Pillars Overview](../index.md) | [Tools](../../tools/index.md)