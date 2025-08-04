---
category: data-management
current_relevance: mainstream
description: Data synchronization pattern that captures and propagates database changes
  in real-time
essential_question: How do we ensure data consistency and reliability with change
  data capture (cdc)?
excellence_tier: gold
introduced: 2008-03
modern-examples:
- company: Netflix
  implementation: Captures MySQL/Cassandra changes for real-time personalization
  scale: 4 trillion events/day enabling sub-second updates
- company: Airbnb
  implementation: SpinalTap CDC system for cross-service data synchronization
  scale: 2B+ changes daily with sub-second latency
- company: Uber
  implementation: Schemaless database with CDC for global replication
  scale: Petabyte-scale cross-region replication
pattern_status: recommended
production-checklist:
- Choose CDC method based on database capabilities
- Handle schema evolution gracefully
- Implement exactly-once or at-least-once delivery
- Monitor replication lag continuously
- Plan for initial data loads and backfills
- Set up dead letter queues for failures
- Test failover and recovery scenarios
- Document data lineage and dependencies
tagline: Master change data capture (cdc) for distributed systems success
title: Change Data Capture (CDC)
---


# Change Data Capture (CDC)

!!! success "🏆 Gold Standard Pattern"
    **Real-Time Data Synchronization** • Netflix, Airbnb, Uber proven
    
    The essential pattern for streaming database changes to downstream systems. CDC enables real-time data pipelines, cache invalidation, and cross-service synchronization with minimal latency.
    
    **Key Success Metrics:**
    - Netflix: 4 trillion events/day for personalization
    - Airbnb: 2B+ changes daily, sub-second latency
    - Uber: Petabyte-scale cross-region replication

## Essential Question

**How can we reliably capture every database change and stream it to multiple consumers without impacting source performance?**

## When to Use / When NOT to Use

### Use CDC When ✅

| Scenario | Why | Example |
|----------|-----|---------|
| **Real-time sync needed** | Millisecond propagation | Cache invalidation, search index updates |
| **Multiple consumers** | Decouple sources from sinks | Analytics, ML pipelines, audit logs |
| **Cross-service data sharing** | Avoid direct DB access | Microservices data distribution |
| **Event-driven architecture** | Database as event source | Order events trigger fulfillment |
| **Zero-downtime migrations** | Dual writes during cutover | Database migrations, re-platforming |

### DON'T Use When ❌

| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Batch sufficient** | Real-time overhead unjustified | ETL/ELT pipelines |
| **Simple point queries** | Direct access simpler | API calls, read replicas |
| **Transactional consistency** | CDC is eventually consistent | Distributed transactions |
| **Small data volume** | Complexity not worth it | Direct replication |

## Level 1: Intuition (5 min)

### The Security Camera Analogy

<div class="axiom-box">
<h4>🔬 Law 5: Distributed Knowledge</h4>

CDC treats the database transaction log as the source of truth, turning state changes into an event stream that can be consumed by any system.

**Key Insight**: Every database write already creates a log entry. CDC just exposes this existing stream.
</div>

### Visual Architecture

```mermaid
graph LR
    subgraph "Traditional Batch"
        DB1[(Database)] -->|Daily ETL| DW1[(Data Warehouse)]
        DB1 -->|Polling| C1[Cache]
        DB1 -->|Batch| S1[Search]
    end
    
    subgraph "CDC Pattern"
        DB2[(Database)] -->|Transaction Log| CDC[CDC Processor]
        CDC -->|Stream| K[Kafka]
        K --> DW2[(Data Warehouse)]
        K --> C2[Cache Invalidation]
        K --> S2[Search Index]
        K --> ML[ML Pipeline]
    end
```

## Level 2: Foundation (10 min)

### CDC Methods Comparison

| Method | How it Works | Pros | Cons | Use When |
|--------|--------------|------|------|----------|
| **Log-based** | Read transaction log | Low impact, reliable | DB-specific | Supported DBs |
| **Trigger-based** | Database triggers | Works anywhere | Performance impact | Legacy systems |
| **Query-based** | Poll with timestamps | Simple | Misses deletes, lag | Low volume |
| **Timestamp-based** | Track modified_at | Easy setup | Can miss updates | Audit not critical |

### Architecture Components

```mermaid
graph TB
    subgraph "Source"
        APP[Application] --> DB[(Database)]
        DB --> LOG[Transaction Log]
    end
    
    subgraph "CDC Pipeline"
        LOG --> READER[Log Reader]
        READER --> PARSER[Event Parser]
        PARSER --> ROUTER[Event Router]
        ROUTER --> BUFFER[Buffer/Queue]
    end
    
    subgraph "Consumers"
        BUFFER --> ES[Elasticsearch]
        BUFFER --> CACHE[Redis Cache]
        BUFFER --> DW[Data Warehouse]
        BUFFER --> STREAM[Stream Processing]
    end
```

### Key Design Decisions

<div class="decision-box">
<h4>🎯 CDC Design Choices</h4>

**Delivery Guarantees**
- At-most-once: Accept data loss
- At-least-once: Handle duplicates
- Exactly-once: Complex but clean

**Data Format**
- Full row: Complete state
- Delta only: Just changes
- Before+After: Most flexible

**Schema Evolution**
- Backward compatible only
- Forward compatible
- Full compatibility
</div>

## Level 3: Deep Dive (15 min)

### CDC Implementation Flow

```mermaid
sequenceDiagram
    participant DB as Database
    participant LOG as Transaction Log
    participant CDC as CDC Processor
    participant K as Kafka
    participant C as Consumers
    
    DB->>LOG: Write transaction
    LOG->>CDC: Read binlog/WAL
    CDC->>CDC: Parse & Transform
    CDC->>K: Publish event
    K->>C: Distribute to consumers
    
    Note over LOG: Zero impact on DB
    Note over K: Decouple producers/consumers
```

### CDC Event Format

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

```json
{
  "schema": {
    "type": "struct",
    "name": "order_change",
    "version": 1
  },
  "payload": {
    "before": {
      "order_id": 12345,
      "status": "pending",
      "total": 99.99
    },
    "after": {
      "order_id": 12345,
      "status": "confirmed",
      "total": 99.99
    },
    "source": {
      "database": "orders",
      "table": "orders",
      "server_id": 223344,
      "binlog_file": "mysql-bin.000003",
      "binlog_position": 154789,
      "timestamp": 1634567890
    },
    "op": "u",
    "ts_ms": 1634567890000
  }
}
```

</details>

### Common Patterns

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Outbox Pattern** | Transactional guarantees | Write events to outbox table |
| **Snapshot + CDC** | Initial load + streaming | Bulk load then stream changes |
| **Filter & Route** | Selective propagation | Topic/queue per table or pattern |
| **Transform** | Data enrichment | Stream processing on CDC events |

## Level 4: Expert (20 min)

### CDC Pipeline Configuration

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Source** | Binlog position tracking | Resume after failure |
| **Parallelism** | 16 threads | Scale throughput |
| **Filtering** | Table/operation patterns | Reduce noise |
| **Enrichment** | Join with cache | Add context |
| **Masking** | PII fields | Compliance |
| **Routing** | Topic per table | Organized consumption |

### Performance Optimization

| Optimization | Technique | Impact |
|--------------|-----------|--------|
| **Batching** | Group changes | 10x throughput |
| **Compression** | Snappy/LZ4 | 70% bandwidth reduction |
| **Partitioning** | By table/key | Linear scaling |
| **Filtering** | Early in pipeline | Reduce load |
| **Caching** | Recent positions | Fast recovery |

### Critical CDC Metrics

| Metric | Alert Threshold | Impact |
|--------|----------------|--------|
| **Replication lag** | > 60 seconds | Stale data |
| **Error rate** | > 0.1% | Data loss risk |
| **Throughput drop** | < 80% baseline | Bottleneck |
| **Queue depth** | > 100k events | Memory pressure |

## Level 5: Mastery (30 min)

### Case Study: Netflix's CDC Pipeline

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
    subgraph "Source Databases"
        MySQL[(MySQL)]
        CASS[(Cassandra)]
        DDB[(DynamoDB)]
    end
    
    subgraph "CDC Layer"
        MySQL --> DBZ[Debezium]
        CASS --> CSC[Cassandra CDC]
        DDB --> DS[DynamoDB Streams]
        
        DBZ --> KC[Kafka Connect]
        CSC --> KC
        DS --> KC
    end
    
    subgraph "Stream Processing"
        KC --> KAFKA[Kafka<br/>4T events/day]
        KAFKA --> FLINK[Flink]
        FLINK --> FILTER[Filter/Route]
        FILTER --> ENRICH[Enrichment]
    end
    
    subgraph "Consumers"
        ENRICH --> ES[Elasticsearch<br/>Search]
        ENRICH --> RS[Recommendations<br/>Real-time]
        ENRICH --> CACHE[EVCache<br/>Invalidation]
        ENRICH --> S3[S3<br/>Data Lake]
    end
```

</details>

**Scale Achievements**:
- 4 trillion events/day
- Sub-second end-to-end latency
- 99.99% delivery guarantee
- Automatic schema evolution

### Economic Analysis

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

```python
def cdc_vs_batch_roi(
    daily_changes,
    data_freshness_value_per_hour,
    num_consumers
):
    # Batch approach
    batch_delay_hours = 12  # Twice daily
    batch_lost_value = batch_delay_hours * data_freshness_value_per_hour
    batch_infra_cost = 1000  # Simplified
    
    # CDC approach  
    cdc_delay_minutes = 1
    cdc_lost_value = (cdc_delay_minutes/60) * data_freshness_value_per_hour
    cdc_infra_cost = 3000  # Higher infrastructure
    
    # ROI calculation
    value_gain = batch_lost_value - cdc_lost_value
    cost_increase = cdc_infra_cost - batch_infra_cost
    
    return {
        'monthly_value_gain': value_gain * 30,
        'monthly_cost_increase': cost_increase,
        'roi_months': cost_increase / (value_gain * 30),
        'worth_it': value_gain > cost_increase
    }
```

</details>

## Quick Reference

### Decision Matrix

```mermaid
graph TD
    Start[Analyze needs] --> Q1{Real-time<br/>required?}
    Q1 -->|No| Batch[Use ETL/ELT]
    Q1 -->|Yes| Q2{Source DB<br/>supports CDC?}
    
    Q2 -->|No| Q3{Can add<br/>triggers?}
    Q2 -->|Yes| LogCDC[Use log-based<br/>CDC]
    
    Q3 -->|No| Poll[Timestamp<br/>polling]
    Q3 -->|Yes| Trigger[Trigger-based<br/>CDC]
    
    LogCDC --> Q4{Multiple<br/>consumers?}
    Q4 -->|Yes| Stream[Add streaming<br/>platform]
    Q4 -->|No| Direct[Direct<br/>connection]
```

### Implementation Checklist ✓

- [ ] Choose CDC method based on source database
- [ ] Design event schema with versioning
- [ ] Set up initial snapshot process
- [ ] Implement position tracking for recovery
- [ ] Add monitoring for lag and errors
- [ ] Test schema evolution scenarios
- [ ] Plan for handling large transactions
- [ ] Document data lineage
- [ ] Set up alerting for failures
- [ ] Test disaster recovery

### Common Tools

| Database | CDC Tool | Method | Notes |
|----------|----------|--------|-------|
| **MySQL** | Debezium, Maxwell | Binlog | Most mature |
| **PostgreSQL** | Debezium, wal2json | WAL | Logical replication |
| **MongoDB** | Change Streams | Oplog | Built-in |
| **SQL Server** | Debezium, CT | Change Tracking | Enterprise features |
| **Oracle** | GoldenGate, XStream | Redo logs | Licensed |

## Related Patterns

### Core Combinations
- **[Event Sourcing](./event-sourcing.md)**: CDC provides the events
- **[Outbox Pattern](../pattern-library/data-management/outbox.md)**: Transactional CDC
- **[Saga Pattern](./saga.md)**: CDC triggers distributed transactions

### Supporting Patterns
- **[Stream Processing](../patterns/stream-processing.md)**: Process CDC events
- **[CQRS](./cqrs.md)**: CDC updates read models
- **[Cache Invalidation](../patterns/cache-invalidation.md)**: Real-time cache updates

### Alternatives
- **[Batch ETL](../patterns/etl.md)**: When real-time not needed
- **[Database Replication](../patterns/replication.md)**: Full database sync
- **[Polling](../patterns/polling.md)**: Simple but less efficient

## Further Reading

- [Debezium Documentation](https://debezium.io/documentation/)
- [Kafka Connect CDC](https://docs.confluent.io/kafka-connect/current/)
- [AWS DMS CDC](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_CDC.html)
- [Change Data Capture Patterns](https://www.confluent.io/blog/cdc-and-streaming-analytics/)

### Case Studies
- [Netflix: DBLog Framework](https://netflixtechblog.com/dblog-a-generic-change-data-capture-framework-69351fb9099b)
- [Airbnb: SpinalTap](https://medium.com/airbnb-engineering/capturing-data-evolution-in-a-service-oriented-architecture-72f7c643ee6f)
- [Uber: Schemaless CDC](https://eng.uber.com/schemaless-rewrite/)