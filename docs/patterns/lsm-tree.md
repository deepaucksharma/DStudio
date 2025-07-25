---
title: LSM Tree (Log-Structured Merge Tree)
description: Write-optimized storage engine that converts random writes to sequential writes through buffering and merging
type: pattern
category: data-management
difficulty: intermediate
reading_time: 40 min
prerequisites: [storage-engines, wal, sorting-algorithms]
when_to_use: When you need high write throughput, can tolerate read amplification, and have write-heavy workloads
when_not_to_use: When you need consistent read performance or immediate read-after-write consistency
status: complete
last_updated: 2025-01-23
---


# LSM Tree (Log-Structured Merge Tree)

<div class="pattern-header">
  <div class="pattern-type">Data Management Pattern</div>
  <div class="pattern-summary">Transform random writes into sequential writes by buffering in memory and periodically merging sorted files, achieving high write throughput at the cost of read complexity.</div>
</div>

## Problem Context

<div class="problem-box">
<h3>🎯 The Challenge</h3>

Traditional B-tree based storage engines face write amplification:
- **Random I/O is expensive** on both HDDs and SSDs
- **In-place updates** require reading, modifying, and writing back
- **Write amplification** - writing 1KB might cause 4KB or more I/O
- **SSD wear** - limited write cycles make amplification costly
- **Concurrent writes** create lock contention

LSM trees solve this by making all writes sequential.
</div>

## Core Architecture

```mermaid
graph TB
    subgraph "LSM Tree Structure"
        subgraph "Memory"
            MT[MemTable<br/>Active Writes]
            IMT[Immutable<br/>MemTable]
        end
        
        subgraph "Level 0"
            L0F1[SSTable]
            L0F2[SSTable]
            L0F3[SSTable]
        end
        
        subgraph "Level 1"
            L1F1[Sorted<br/>SSTable]
            L1F2[Sorted<br/>SSTable]
        end
        
        subgraph "Level 2"
            L2F1[Larger<br/>SSTable]
        end
        
        Write[Writes] --> MT
        MT -->|Full| IMT
        IMT -->|Flush| L0F1
        
        L0F1 -->|Compact| L1F1
        L0F2 -->|Compact| L1F1
        L1F1 -->|Compact| L2F1
    end
    
    style MT fill:#5448C8,color:#fff
    style Write fill:#4CAF50,color:#fff
```

## How LSM Trees Work

### 1. Write Path

```mermaid
sequenceDiagram
    participant Client
    participant WAL as Write-Ahead Log
    participant MT as MemTable
    participant BG as Background Thread
    participant Disk as Disk (SSTables)
    
    Client->>WAL: 1. Write to WAL
    WAL-->>Client: Ack (Durable)
    
    Client->>MT: 2. Insert into MemTable
    Note over MT: In-memory<br/>sorted structure<br/>(e.g., skip list)
    
    MT-->>Client: Write Complete
    
    Note over MT: When MemTable full...
    
    MT->>BG: Trigger flush
    BG->>MT: Make immutable
    BG->>Disk: Write SSTable
    Note over Disk: Sequential write<br/>of sorted data
```

### 2. Read Path

```mermaid
graph TD
    subgraph "Read Path (Newest to Oldest)"
        Read[Read Request] --> MT{Check<br/>MemTable}
        MT -->|Found| Return1[Return Value]
        MT -->|Not Found| IMT{Check Immutable<br/>MemTable}
        IMT -->|Found| Return2[Return Value]
        IMT -->|Not Found| L0{Check Level 0<br/>SSTables}
        L0 -->|Found| Return3[Return Value]
        L0 -->|Not Found| L1{Check Level 1<br/>SSTables}
        L1 -->|Found| Return4[Return Value]
        L1 -->|Not Found| Continue[...]
    end
    
    style Read fill:#ff6b6b
    style Return1 fill:#4CAF50
    style Return2 fill:#4CAF50
    style Return3 fill:#4CAF50
    style Return4 fill:#4CAF50
```

## Key Components

### 1. MemTable Implementation

```python
class MemTable:
    def __init__(self, size_limit=64 * 1024 * 1024):  # 64MB
        self.data = {}  # In practice: Skip list or RB tree
        self.size = 0
        self.size_limit = size_limit
        self.wal = WriteAheadLog()
        
    def put(self, key, value):
# Write to WAL first for durability
        self.wal.append(('PUT', key, value))
        
# Update in-memory structure
        old_size = len(self.data.get(key, ''))
        self.data[key] = value
        self.size += len(value) - old_size
        
# Check if flush needed
        if self.size >= self.size_limit:
            return 'NEEDS_FLUSH'
        return 'OK'
    
    def get(self, key):
        return self.data.get(key)
    
    def delete(self, key):
# Deletion is just a special value (tombstone)
        self.put(key, '__DELETED__')
    
    def to_sstable(self):
        """Convert to sorted SSTable"""
        sorted_data = sorted(self.data.items())
        return SSTable(sorted_data)
```

### 2. SSTable Structure

```mermaid
graph LR
    subgraph "SSTable File Format"
        subgraph "Data Blocks"
            B1[Block 1<br/>Key-Value Pairs]
            B2[Block 2<br/>Key-Value Pairs]
            B3[Block N<br/>Key-Value Pairs]
        end
        
        subgraph "Index"
            I1[Block 1 Offset<br/>First Key]
            I2[Block 2 Offset<br/>First Key]
            I3[Block N Offset<br/>First Key]
        end
        
        subgraph "Metadata"
            BF[Bloom Filter]
            Stats[Statistics]
            Footer[Footer]
        end
    end
    
    B1 --> I1
    B2 --> I2
    B3 --> I3
```

### 3. Bloom Filter Optimization

```python
class BloomFilter:
    def __init__(self, expected_items, false_positive_rate=0.01):
# Calculate optimal size and hash functions
        self.size = int(-expected_items * math.log(false_positive_rate) / (math.log(2) ** 2))
        self.hash_count = int(self.size / expected_items * math.log(2))
        self.bits = bitarray(self.size)
        self.bits.setall(0)
    
    def add(self, key):
        for seed in range(self.hash_count):
            index = hash((key, seed)) % self.size
            self.bits[index] = 1
    
    def might_contain(self, key):
        for seed in range(self.hash_count):
            index = hash((key, seed)) % self.size
            if not self.bits[index]:
                return False  # Definitely not in set
        return True  # Might be in set
```

## Compaction Strategies

### 1. Size-Tiered Compaction

```mermaid
graph TD
    subgraph "Size-Tiered Compaction"
        subgraph "Before"
            S1[4MB] 
            S2[4MB]
            S3[4MB]
            S4[4MB]
            M1[16MB]
            M2[16MB]
        end
        
        subgraph "After"
            NS1[16MB<br/>Merged]
            M1C[16MB]
            M2C[16MB]
        end
        
        S1 -->|Merge| NS1
        S2 -->|Merge| NS1
        S3 -->|Merge| NS1
        S4 -->|Merge| NS1
    end
```

### 2. Leveled Compaction

```python
class LeveledCompaction:
    def __init__(self, level_multiplier=10):
        self.levels = []
        self.level_multiplier = level_multiplier
        self.l0_size = 10 * 1024 * 1024  # 10MB
        
    def get_level_size(self, level):
        """Each level is multiplier times larger"""
        if level == 0:
            return self.l0_size
        return self.l0_size * (self.level_multiplier ** level)
    
    def compact_level(self, level):
        """Compact level into level+1"""
        if self.get_level_total_size(level) > self.get_level_size(level):
# Select overlapping files from level and level+1
            files_to_compact = self.select_compaction_files(level)
            
# Merge sort all selected files
            merged = self.merge_sorted_files(files_to_compact)
            
# Write back to level+1
            self.write_to_level(merged, level + 1)
            
# Delete old files
            self.delete_files(files_to_compact)
```

### 3. Compaction Comparison

<div class="comparison-table">
<table>
<thead>
<tr>
<th>Strategy</th>
<th>Write Amp</th>
<th>Read Amp</th>
<th>Space Amp</th>
<th>Use Case</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Size-Tiered</strong></td>
<td>Low</td>
<td>High</td>
<td>High (2x)</td>
<td>Write-heavy</td>
</tr>
<tr>
<td><strong>Leveled</strong></td>
<td>High</td>
<td>Low</td>
<td>Low (1.1x)</td>
<td>Read-heavy</td>
</tr>
<tr>
<td><strong>Time-Window</strong></td>
<td>Medium</td>
<td>Medium</td>
<td>Medium</td>
<td>Time-series</td>
</tr>
</tbody>
</table>
</div>

## Performance Characteristics

### Write Performance

```mermaid
graph LR
    subgraph "Write Path Performance"
        W1[Client Write] -->|Immediate| WAL[WAL Append<br/>~0.1ms]
        WAL -->|Immediate| Mem[MemTable Insert<br/>~0.01ms]
        Mem -->|Async| Flush[Background Flush<br/>No client impact]
        Flush -->|Async| Compact[Background Compaction<br/>No client impact]
    end
    
    style W1 fill:#4CAF50
    style WAL fill:#2196F3
    style Mem fill:#2196F3
```

### Read Performance Analysis

```python
def analyze_read_performance(lsm_tree, key):
    """Analyze read amplification"""
    checks = []
    
# Check MemTable (fastest)
    if lsm_tree.memtable.contains(key):
        checks.append(('MemTable', 0.01))  # ~0.01ms
        return checks
    
# Check each level (increasingly slower)
    for level in range(lsm_tree.num_levels):
        sstables = lsm_tree.get_level_sstables(level)
        
        for sstable in sstables:
# Bloom filter check (fast)
            if sstable.bloom_filter.might_contain(key):
                checks.append((f'L{level} Bloom', 0.001))
                
# Actual disk read (slow)
                if sstable.contains(key):
                    checks.append((f'L{level} Read', 1.0))
                    return checks
    
    return checks  # Key not found

# Worst case: Check all levels
# Read amplification = num_levels * files_per_level
```

## Real-World Implementations

### RocksDB Architecture

<div class="example-card">
<h4>Facebook's RocksDB</h4>

```mermaid
graph TB
    subgraph "RocksDB Architecture"
        subgraph "Write Path"
            WB[Write Batch] --> WAL[WAL]
            WAL --> MT[MemTable]
            MT --> IMT[Immutable<br/>MemTables]
        end
        
        subgraph "Storage"
            IMT --> L0[L0: Overlapping]
            L0 --> L1[L1: Non-overlapping]
            L1 --> L2[L2: 10x larger]
            L2 --> L3[L3: 10x larger]
        end
        
        subgraph "Read Path"
            BC[Block Cache]
            RC[Row Cache]
            BF[Bloom Filters]
        end
    end
```

- Column families for multi-tenancy
- Pluggable compaction strategies
- Direct I/O support
- Compression per level
</div>

### Apache Cassandra

<div class="example-card">
<h4>Cassandra's LSM Implementation</h4>

- Size-tiered compaction by default
- Time-window compaction for time-series
- Off-heap memory for bloom filters
- Incremental repair with Merkle trees
- Compression and encryption support
</div>

## Optimizations

### 1. Write Batching

```python
class BatchedLSMTree:
    def __init__(self):
        self.write_buffer = []
        self.buffer_size = 0
        self.max_buffer_size = 1024 * 1024  # 1MB
        
    def batch_write(self, writes):
        """Batch multiple writes for efficiency"""
        with self.wal.batch():
            for key, value in writes:
                self.wal.append(key, value)
                self.write_buffer.append((key, value))
                self.buffer_size += len(key) + len(value)
        
# Apply to MemTable in batch
        self.memtable.batch_insert(self.write_buffer)
        self.write_buffer.clear()
        self.buffer_size = 0
```

### 2. Monkey Optimization

<div class="formula-box">
<h4>Optimal Level Sizes</h4>

Given:
- T: Level multiplier
- L: Number of levels
- N: Total data size

Optimal configuration minimizes: Write Amp + λ × Read Amp

Where λ is the read/write ratio
</div>

### 3. Hardware Optimizations

```python
class SSDOptimizedLSM:
    def __init__(self):
        self.zone_size = 256 * 1024 * 1024  # 256MB zones
        self.current_zone = 0
        
    def allocate_sstable(self, size):
        """Zone-aware allocation for ZNS SSDs"""
        if self.current_zone_remaining() < size:
            self.current_zone += 1
            
        return self.zone_address(self.current_zone)
    
    def compact_with_zones(self, files):
        """Align compaction with zone boundaries"""
# Compact entire zones together
# Minimize zone rewrites
        pass
```

## Trade-offs and Considerations

<div class="trade-off-matrix">
<table>
<thead>
<tr>
<th>Aspect</th>
<th>Benefits</th>
<th>Drawbacks</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Write Performance</strong></td>
<td>Sequential writes only<br/>No write amplification<br/>High throughput</td>
<td>Compaction overhead<br/>Background CPU usage</td>
</tr>
<tr>
<td><strong>Read Performance</strong></td>
<td>Bloom filters help<br/>Block cache effective</td>
<td>Multiple files to check<br/>Read amplification</td>
</tr>
<tr>
<td><strong>Space Usage</strong></td>
<td>Compression friendly<br/>Old versions cleanable</td>
<td>Temporary space for compaction<br/>Tombstone accumulation</td>
</tr>
<tr>
<td><strong>Consistency</strong></td>
<td>Point-in-time snapshots<br/>MVCC support</td>
<td>Eventual compaction<br/>Tombstone visibility</td>
</tr>
</tbody>
</table>
</div>

## Common Pitfalls

### 1. Write Stalls

<div class="failure-vignette">
<h4>⚠️ Compaction Can't Keep Up</h4>

**Scenario**: Write rate exceeds compaction rate
**Result**: L0 fills up, writes stall
**Solution**: 
- More compaction threads
- Larger L0 size
- Rate limiting writes
</div>

### 2. Tombstone Accumulation

```python
def handle_tombstones(self):
    """Special handling for deletes"""
# Problem: Tombstones must be kept until
# they've been compacted to bottom level
    
# Solution 1: Single delete optimization
    if self.is_single_delete_safe(key):
# Can drop tombstone early
        pass
    
# Solution 2: Delete compaction
    if self.tombstone_ratio > 0.5:
        self.trigger_delete_compaction()
```

## When to Use LSM Trees

✅ **Good Fit**:
- Write-heavy workloads
- Append-mostly data (logs, events)
- Large datasets that don't fit in memory
- SSD-based storage
- Time-series data

❌ **Poor Fit**:
- Read-heavy with random access
- Low-latency read requirements
- Small datasets that fit in memory
- Frequent updates to same keys

## Implementation Checklist

- [ ] Design MemTable structure (skip list, B-tree)
- [ ] Implement WAL for durability
- [ ] Design SSTable format with index
- [ ] Add bloom filters for read optimization
- [ ] Choose compaction strategy
- [ ] Implement block cache
- [ ] Add compression support
- [ ] Handle deletions (tombstones)
- [ ] Monitor read/write amplification
- [ ] Tune level sizes and multipliers

## Related Patterns

- Write-Ahead Log (WAL) (Coming Soon) - Durability mechanism
- [Bloom Filter](bloom-filter.md) - Read optimization for LSM trees
- [Sharding](sharding.md) - Distributing LSM trees across nodes
- [Consistent Hashing](/case-studies/consistent-hashing) - Key distribution

## References

- "The Log-Structured Merge-Tree (LSM-Tree)" - O'Neil et al.
- RocksDB Documentation and Tuning Guide
- Cassandra Storage Engine Deep Dive
- "LSM-based Storage Techniques: A Survey" - Chen Luo & Carey