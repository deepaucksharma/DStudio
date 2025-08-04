---
best-for:
- Message queues and event stores
- Database write-ahead logs
- Time-series data storage
- Distributed logs like Kafka
category: data-management
current_relevance: mainstream
description: Breaking append-only logs into manageable segments for efficient storage,
  compaction, and retention
essential_question: How do we ensure data consistency and reliability with segmented
  log?
excellence_tier: silver
introduced: 2004-11
pattern_status: recommended
tagline: Master segmented log for distributed systems success
title: Segmented Log
trade-offs:
  cons:
  - Additional complexity vs single file
  - Segment management overhead
  - Cross-segment query complexity
  - Metadata management required
  pros:
  - Efficient old data cleanup via segment deletion
  - Parallel operations on different segments
  - Bounded recovery time per segment
  - Natural unit for replication and backup
---


# Segmented Log Pattern

!!! info "🥈 Silver Tier Pattern"
    **Log Scalability Champion** • Kafka, RocksDB, Cassandra proven
    
    Essential pattern for managing continuously growing append-only logs. Enables efficient cleanup, parallel operations, and bounded recovery times by splitting logs into fixed-size segments.
    
    **Key Success Metrics:**
    - Kafka: 7 trillion messages/day across segments
    - RocksDB: Powers Meta's massive databases
    - Cassandra: Petabyte-scale with segment compaction

## Essential Question

**How do we manage infinitely growing append-only logs while enabling efficient cleanup, compaction, and bounded operations?**

## When to Use / When NOT to Use

### Use Segmented Log When ✅

| Scenario | Why | Example |
|----------|-----|---------|
| **Continuous growth** | Can't keep everything in one file | Message queues, event logs |
| **Retention policies** | Delete old data efficiently | "Keep 7 days" - delete old segments |
| **Log compaction needed** | Remove duplicates/tombstones | Key-value stores, Kafka |
| **Parallel operations** | Read/write different segments | Multi-threaded recovery |
| **Bounded recovery** | Limit replay scope | Database WAL recovery |

### DON'T Use When ❌

| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Small logs** | Overhead not justified | Single file |
| **Random access needed** | Sequential segments | B-tree, LSM-tree |
| **Frequent updates** | Append-only design | Update-in-place storage |
| **Simple use case** | Complexity overhead | Basic file append |

## Level 1: Intuition (5 min)

### The Newspaper Archive Analogy

<div class="axiom-box">
<h4>🔬 Law 5: Distributed Knowledge</h4>

Segmented logs recognize that not all data has equal value over time. Recent data is hot, old data is cold, and infinite retention is impossible.

**Key Insight**: Breaking logs into time or size-based chunks enables independent lifecycle management.
</div>

### Visual Architecture

```mermaid
graph LR
    subgraph "Single Log (Problems)"
        W1[Writers] --> L1[Giant Log File]
        L1 --> P1[Can't delete middle]
        L1 --> P2[Slow recovery]
        L1 --> P3[Unbounded growth]
    end
    
    subgraph "Segmented Log (Solution)"
        W2[Writers] --> AC[Active Segment]
        AC --> S1[Segment 1<br/>Sealed]
        S1 --> S2[Segment 2<br/>Sealed]
        S2 --> S3[Segment 3<br/>Sealed]
        
        S1 --> D[Delete old]
        S2 --> C[Compact]
        AC --> R[Fast recovery]
    end
```

## Level 2: Foundation (10 min)

### Core Architecture

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
    subgraph "Write Path"
        W[Writer] --> AS[Active Segment]
        AS -->|Size/Time Limit| SEAL[Seal Segment]
        SEAL --> NEW[New Active Segment]
        SEAL --> IDX[Update Index]
    end
    
    subgraph "Segments"
        S0[segment_0000.log<br/>0-1M]
        S1[segment_0001.log<br/>1M-2M]
        S2[segment_0002.log<br/>2M-3M]
        ACTIVE[segment_0003.log<br/>3M-current]
    end
    
    subgraph "Management"
        IDX[Segment Index] --> MAP[Offset → File Map]
        POL[Retention Policy] --> DEL[Delete Old]
        COMP[Compaction] --> MERGE[Merge/Clean]
    end
```

</details>

### Key Design Decisions

| Decision | Options | Trade-offs |
|----------|---------|------------|
| **Segment size** | Time-based vs Size-based | Predictability vs Uniformity |
| **Naming scheme** | Sequential vs Timestamp | Ordering vs Time correlation |
| **Index structure** | Memory vs Disk | Speed vs Durability |
| **Compaction strategy** | Online vs Offline | Availability vs Efficiency |

### Segment Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active: Create
    Active --> Sealed: Size/Time limit
    Sealed --> Compacting: Compaction triggered
    Compacting --> Compacted: Merge complete
    Sealed --> Deleted: Retention expired
    Compacted --> Deleted: Retention expired
    Deleted --> [*]
```

## Level 3: Deep Dive (15 min)

### Segment Operations

```mermaid
sequenceDiagram
    participant W as Writer
    participant AS as Active Segment
    participant IDX as Segment Index
    participant POL as Retention Policy
    
    W->>AS: Append record
    AS->>AS: Check size limit
    alt Segment full
        AS->>AS: Seal segment
        AS->>IDX: Update index
        AS->>AS: Create new active
    end
    
    POL->>IDX: Check old segments
    IDX->>POL: Return expired
    POL->>POL: Delete segments
```

### Key Implementation Decisions

| Decision | Options | Trade-off |
|----------|---------|-----------|
| **Segment trigger** | Size (1GB) vs Time (1hr) | Predictability vs Uniformity |
| **Index location** | Memory vs Disk | Speed vs Durability |
| **Compaction** | Online vs Offline | Availability vs Efficiency |
| **File format** | Raw vs Compressed | Speed vs Space |

### Compaction Strategies

<div class="decision-box">
<h4>🎯 Compaction Approaches</h4>

**Log Compaction** (Kafka-style)
- Keep only latest value per key
- Good for: Key-value stores, config

**Time-based Compaction**
- Merge segments within time window
- Good for: Time-series data

**Size-based Compaction**
- Merge small segments
- Good for: Write-heavy workloads

**Tiered Compaction**
- Different strategies by age
- Good for: Mixed workloads
</div>

### Production Patterns

```yaml
# Kafka-style configuration
log:
  segment:
    bytes: 1073741824  # 1GB
    ms: 604800000      # 7 days
    
  retention:
    bytes: -1          # No limit
    ms: 604800000      # 7 days
    check_interval_ms: 300000
    
  compaction:
    enabled: true
    min_cleanable_ratio: 0.5
    threads: 1
    
  index:
    interval_bytes: 4096
    size_max_bytes: 10485760
```

## Level 4: Expert (20 min)

### Advanced Techniques

| Technique | Purpose | Implementation |
|-----------|---------|----------------|
| **Memory-mapped segments** | Fast random access | mmap() sealed segments |
| **Parallel compaction** | Reduce downtime | Background thread pool |
| **Compression** | Reduce storage | Compress sealed segments |
| **Encryption** | Security | Encrypt at rest |
| **Cloud tiering** | Cost optimization | Old segments to S3 |

### Performance Optimizations

| Technique | Implementation | Benefit |
|-----------|----------------|---------|
| **Memory-mapping** | mmap() sealed segments | 10x read speed |
| **Batch writes** | Buffer before flush | 5x write throughput |
| **Parallel compaction** | Background threads | Zero downtime |
| **Compression** | LZ4 on sealed segments | 70% space saving |
| **Zero-copy** | sendfile() for reads | CPU efficiency |

### Key Metrics

| Metric | Alert When | Action |
|--------|------------|--------|
| **Segment count** | > 10,000 | Increase segment size |
| **Compaction lag** | > 1 hour | Add compaction threads |
| **Recovery time** | > SLA | Reduce segment size |
| **Fragmentation** | > 50% | Trigger compaction |

## Level 5: Mastery (30 min)

### Case Study: Apache Kafka's Segment Implementation

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
    subgraph "Kafka Partition"
        P[Producer] --> L[Leader]
        
        subgraph "Log Structure"
            L --> AS[Active Segment]
            AS --> S1[segment_0000.log<br/>+ .index<br/>+ .timeindex]
            S1 --> S2[segment_0001.log<br/>+ .index<br/>+ .timeindex]
            S2 --> S3[segment_0002.log<br/>+ .index<br/>+ .timeindex]
        end
        
        subgraph "Background Tasks"
            LC[Log Cleaner] --> S1
            LC --> S2
            RET[Retention] --> S3
        end
    end
    
    subgraph "Replication"
        L --> F1[Follower 1]
        L --> F2[Follower 2]
    end
```

</details>

**Kafka's Design Decisions**:
- 1GB default segment size
- Separate index files for offset/timestamp lookup
- Memory-mapped index files
- Zero-copy transfer for reads
- Log compaction for keyed topics

**Results at Scale**:
- 7 trillion messages/day at LinkedIn
- Petabyte-scale storage
- Millisecond latency
- Automatic rebalancing

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
def segment_size_optimizer(
    write_rate_mb_per_sec,
    retention_days,
    recovery_time_sla_minutes
):
    """Calculate optimal segment size"""
    
    # Smaller segments = faster recovery but more files
    max_segment_for_recovery = (recovery_time_sla_minutes * 60) * 100  # 100MB/s read
    
    # Larger segments = fewer files but slower operations
    files_per_day = (write_rate_mb_per_sec * 86400) / segment_size_mb
    total_files = files_per_day * retention_days
    
    # Find balance
    optimal_size = min(
        max_segment_for_recovery,
        1024,  # 1GB max for manageability
        max(128, 86400 / 1000)  # At least 128MB, at most 1000 files/day
    )
    
    return {
        'optimal_segment_mb': optimal_size,
        'files_per_day': files_per_day,
        'recovery_time_minutes': optimal_size / 100 / 60
    }
```

</details>

## Quick Reference

### Decision Matrix

```mermaid
graph TD
    Start[Design log storage] --> Q1{Unbounded<br/>growth?}
    Q1 -->|No| Single[Single file<br/>sufficient]
    Q1 -->|Yes| Q2{Need<br/>retention?}
    
    Q2 -->|No| Q3{Random<br/>access?}
    Q2 -->|Yes| Segment[Use segmented<br/>log]
    
    Q3 -->|Yes| LSM[Consider<br/>LSM tree]
    Q3 -->|No| Segment
```

### Implementation Checklist ✓

- [ ] Define segment size strategy (time vs size)
- [ ] Implement segment rolling logic
- [ ] Create index for offset lookup
- [ ] Add retention policy enforcement
- [ ] Implement compaction (if needed)
- [ ] Set up monitoring for segments
- [ ] Plan recovery procedures
- [ ] Test segment deletion
- [ ] Document operational procedures

### Configuration Template

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

```yaml
segmented_log:
  segments:
    size_bytes: 1073741824      # 1GB
    time_ms: 86400000           # 24 hours
    index_interval: 4096        # Bytes between index entries
    
  retention:
    time_ms: 604800000          # 7 days
    size_bytes: 107374182400    # 100GB
    check_interval: 300000      # 5 minutes
    
  compaction:
    enabled: true
    strategy: "delete"          # or "compact"
    min_ratio: 0.5
    threads: 2
    
  performance:
    mmap_indices: true
    zero_copy: true
    compression: "lz4"          # For sealed segments
```

</details>

## Related Patterns

### Foundation Patterns
- **[Write-Ahead Log](./wal.md)**: Often implemented as segmented
- **[Append-Only Store](../patterns/append-only.md)**: Base concept
- **[Log Structured Storage](./lsm-tree.md)**: Uses segments internally

### Complementary Patterns
- **[Snapshot](../patterns/snapshot.md)**: Reduce recovery time
- **[Compaction](../patterns/compaction.md)**: Clean up segments
- **[Replication Log](../patterns/replication-log.md)**: Segment-based replication

### Applications
- **[Kafka](../case-studies/kafka.md)**: Canonical implementation
- **[RocksDB](../case-studies/rocksdb.md)**: LSM with segments
- **[Cassandra](../case-studies/cassandra.md)**: SSTables as segments

## Further Reading

- [Kafka Log Implementation](https://kafka.apache.org/documentation/#log)
- [The Log: What every software engineer should know](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying)
- [RocksDB Architecture](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)

### Implementation Resources
- [Building a Distributed Log](https://bravenewgeek.com/building-a-distributed-log-from-scratch-part-1-storage-mechanics/)
- [Segment Compaction Strategies](https://www.confluent.io/blog/log-compaction-highlights-in-the-apache-kafka-and-stream-processing-community/)
- [Storage Engine Design](https://www.databass.dev/)