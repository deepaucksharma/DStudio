---
title: Deduplication
description: Eliminate duplicate data through content-based identification and storage
  optimization
type: pattern
category: data-management
difficulty: intermediate
reading-time: 30 min
prerequisites:
- hashing
- content-addressing
- distributed-systems
when-to-use: Storage systems, backup solutions, message processing, data pipelines
  with duplicate data
when-not-to-use: Real-time systems with strict latency requirements, small datasets,
  when duplicates are rare
status: complete
last-updated: 2025-01-26
excellence_tier: silver
pattern_status: use-with-expertise
introduced: 2008-01
current_relevance: mainstream
trade-offs:
  pros:
  - Significant storage savings (often 10-100x)
  - Reduced network bandwidth for transfers
  - Improved cache efficiency
  cons:
  - CPU overhead for fingerprinting/hashing
  - Complex garbage collection and reference counting
  - Potential for hash collisions requiring verification
best-for:
- Backup and archival systems
- Cloud storage providers reducing costs
- Message queues preventing duplicate processing
---


# Deduplication

!!! warning "🥈 Silver Tier Pattern"
    **Massive storage savings with processing overhead** • Use when duplicate data is common and storage costs matter
    
    Deduplication can reduce storage by 90%+ in backup systems but requires CPU for hashing, complex reference tracking, and careful handling of hash collisions. Best suited for write-once, read-many workloads where storage efficiency outweighs processing costs.

## Overview

Deduplication identifies and eliminates redundant copies of data, storing each unique piece only once. This pattern is crucial for efficient storage systems, backup solutions, and message processing pipelines.

## Core Concepts

### Deduplication Strategies

```mermaid
graph TB
    subgraph "File-Level"
        F1[File A] -->|Hash| H1[SHA-256: abc123]
        F2[File A Copy] -->|Hash| H2[SHA-256: abc123]
        H1 --> S1[Store Once]
        H2 -.->|Reference| S1
    end
    
    subgraph "Block-Level"
        B1[Block 1] -->|Hash| BH1[Hash: def456]
        B2[Block 2] -->|Hash| BH2[Hash: ghi789]
        B3[Block 1 Dup] -->|Hash| BH3[Hash: def456]
        BH1 --> BS1[Store Block 1]
        BH2 --> BS2[Store Block 2]
        BH3 -.->|Reference| BS1
    end
    
    subgraph "Variable-Size Chunking"
        V1[Content] -->|Rolling Hash| C1[Chunk Boundaries]
        C1 --> VC1[Variable Chunks]
    end
```

| Strategy | Granularity | Dedup Ratio | CPU Cost | Use Case |
|----------|-------------|-------------|----------|----------|
| **File-Level** | Entire files | Low | Minimal | Simple backups |
| **Fixed-Block** | Fixed chunks | Medium | Low | Block storage |
| **Variable-Block** | Content-defined | High | Medium | Efficient storage |
| **Byte-Level** | Individual bytes | Maximum | Very High | Specialized |

### Content Fingerprinting

```mermaid
flowchart LR
    Data[Input Data] --> Hash{Hash Function}
    
    Hash --> MD5[MD5<br/>128-bit<br/>Fast, Weak]
    Hash --> SHA1[SHA-1<br/>160-bit<br/>Deprecated]
    Hash --> SHA256[SHA-256<br/>256-bit<br/>Secure]
    Hash --> XXH[xxHash<br/>64-bit<br/>Very Fast]
    
    SHA256 --> FP[Fingerprint]
    FP --> Lookup{Exists?}
    Lookup -->|Yes| Ref[Add Reference]
    Lookup -->|No| Store[Store New]
```

## Implementation Patterns

### Inline vs Post-Process Deduplication

| Approach | When Dedup Occurs | Pros | Cons |
|----------|-------------------|------|------|
| **Inline** | During write | Immediate savings | Higher write latency |
| **Post-Process** | After write | Fast writes | Temporary 2x storage |
| **Near-line** | Shortly after | Balanced | Complex scheduling |

### Reference Management

```mermaid
graph TB
    subgraph "Reference Counting"
        D1[Data Block] -->|Ref: 3| R1[File A]
        D1 --> R2[File B]
        D1 --> R3[File C]
        R3 -->|Delete| D1
        D1 -->|Ref: 2| D1
    end
    
    subgraph "Garbage Collection"
        GC[GC Process] -->|Mark| Live[Live Blocks]
        GC -->|Sweep| Dead[Dead Blocks]
        Dead -->|Reclaim| Free[Free Space]
    end
```

## Deduplication Algorithms

### Content-Defined Chunking (CDC)

```mermaid
flowchart TD
    Start[Data Stream] --> Window[Sliding Window]
    Window --> Hash[Rolling Hash]
    Hash --> Check{Boundary<br/>Condition?}
    Check -->|Yes| Cut[Create Chunk]
    Check -->|No| Slide[Slide Window]
    Slide --> Hash
    Cut --> Fingerprint[Generate SHA-256]
    Fingerprint --> Store{New<br/>Chunk?}
    Store -->|Yes| Save[Store Chunk]
    Store -->|No| Reference[Update References]
```

**Rabin Fingerprinting Example**:
- Average chunk size: 8KB
- Min chunk: 2KB
- Max chunk: 64KB
- Boundary when: `hash & 0x1FFF == 0x1FFF`

### Delta Compression

```mermaid
graph LR
    V1[Version 1] --> Delta[Compute Delta]
    V2[Version 2] --> Delta
    Delta --> D[Delta Block]
    V1 --> Store[(Storage)]
    D --> Store
    
    Restore[Restore V2] --> V1
    Restore --> D
    Restore --> V2R[Version 2 Restored]
```

## Performance Optimization

### Deduplication Index

```mermaid
graph TB
    subgraph "Hierarchical Index"
        L1[L1: Memory<br/>Hot Entries]
        L2[L2: SSD<br/>Warm Entries]
        L3[L3: Disk<br/>Cold Entries]
        
        Query[Fingerprint Query] --> L1
        L1 -->|Miss| L2
        L2 -->|Miss| L3
        L3 -->|Miss| NewEntry[New Entry]
    end
    
    subgraph "Bloom Filters"
        BF[Bloom Filter<br/>Probabilistic] -->|Maybe| Index[Check Index]
        BF -->|Definitely Not| Skip[Skip Lookup]
    end
```

### Sampling Strategies

| Strategy | Description | Dedup Ratio | Performance |
|----------|-------------|-------------|-------------|
| **Full** | Check every block | 100% | Slowest |
| **Sampling** | Check subset | 85-95% | Faster |
| **Similarity** | Group similar | 90-98% | Balanced |
| **Sketch-based** | MinHash/SimHash | 80-90% | Fastest |

## Real-World Implementations

### Storage Systems

```mermaid
graph TB
    subgraph "ZFS Dedup"
        Z1[Write] -->|SHA256| Z2[DDT<br/>Dedup Table]
        Z2 -->|Exists| Z3[Reference]
        Z2 -->|New| Z4[Store]
    end
    
    subgraph "Data Domain"
        D1[Stream] -->|Segment| D2[Variable Chunks]
        D2 -->|Fingerprint| D3[Index Lookup]
        D3 -->|Inline| D4[Compress & Store]
    end
    
    subgraph "Veeam"
        V1[Backup] -->|Source-side| V2[Dedup]
        V2 -->|WAN| V3[Target]
        V3 -->|Verify| V4[Store]
    end
```

### Message Deduplication

```mermaid
sequenceDiagram
    participant P as Producer
    participant Q as Queue
    participant C as Consumer
    participant S as State Store
    
    P->>Q: Message(ID: 123)
    Q->>S: Check ID 123
    S-->>Q: Not Seen
    Q->>S: Store ID 123
    Q->>C: Deliver Message
    
    P->>Q: Message(ID: 123) Retry
    Q->>S: Check ID 123
    S-->>Q: Already Seen
    Q->>Q: Drop Duplicate
```

## Common Pitfalls

!!! danger "Anti-Patterns"
    - **Weak hashes**: MD5 for security-critical dedup
    - **No verification**: Trusting hashes without collision handling
    - **Unbounded index**: Memory exhaustion from fingerprint index
    - **Aggressive dedup**: CPU overhead exceeds storage savings

## Design Decisions

### Choosing Deduplication Strategy

```mermaid
flowchart TD
    Start[Data Characteristics] --> Type{Data Type?}
    Type -->|Structured| Block[Block-Level]
    Type -->|Unstructured| Content[Content-Defined]
    Type -->|Messages| Exact[Exact Match]
    
    Block --> Size{Change Size?}
    Size -->|Small| Fixed[Fixed Blocks]
    Size -->|Large| Variable[Variable Blocks]
    
    Content --> Pattern{Access Pattern?}
    Pattern -->|Sequential| Stream[Stream-based]
    Pattern -->|Random| Index[Index-based]
```

### Implementation Checklist

- [ ] Choose appropriate hash algorithm (security vs speed)
- [ ] Design chunk size strategy (fixed vs variable)
- [ ] Implement reference counting or GC
- [ ] Build efficient fingerprint index
- [ ] Add collision detection/handling
- [ ] Plan for index scaling
- [ ] Monitor dedup ratio and CPU usage
- [ ] Handle hash collisions gracefully
- [ ] Implement data verification
- [ ] Design backup/restore with dedup

## Monitoring and Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Dedup Ratio** | (Original / Stored) Size | > 5:1 |
| **Hash Time** | Time per MB hashed | < 10ms |
| **Index Lookups** | Lookups per second | > 100K |
| **Collision Rate** | Hash collisions found | < 0.001% |
| **GC Overhead** | Time spent in GC | < 5% |

## Related Patterns
- [Content-Addressed Storage](patterns/cas)
- [Caching Strategies](patterns/caching-strategies)

## References
- [Google Drive Case Study](case-studies/google-drive)