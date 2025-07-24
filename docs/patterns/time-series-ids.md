---
title: Time Series IDs
description: ID generation strategies optimized for time-series data with chronological ordering and efficient storage
type: pattern
category: specialized
difficulty: intermediate
reading_time: 30 min
prerequisites: [distributed-systems-basics, time-synchronization, storage-optimization]
when_to_use: IoT systems, monitoring platforms, event logs, financial trading systems requiring time-ordered data
when_not_to_use: Non-time-sensitive data, when storage efficiency isn't critical, simple applications
status: complete
last_updated: 2025-07-24
---

# Time Series IDs

<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **Time Series IDs**

## Overview

Time series IDs are specialized identifiers designed for systems that generate massive amounts of time-ordered data. Unlike general-purpose IDs, they optimize for chronological ordering, storage efficiency, and query performance on temporal ranges.

<div class="law-box">
<strong>Time Ordering Constraint</strong>: Time series systems must maintain strict chronological ordering while handling massive throughput across distributed nodes.
</div>

## The Time Series Challenge

Traditional IDs fail for time series workloads:

```python
# ❌ Random UUIDs - poor locality
import uuid
event_id = uuid.uuid4()  # Random distribution hurts range queries

# ❌ Simple timestamps - no uniqueness
import time
event_id = int(time.time() * 1000)  # Collisions at high throughput

# ❌ Auto-increment - not distributed
# Single bottleneck, no cross-node ordering
```

**Time Series Requirements**:
- **Chronological Ordering**: IDs sort by time
- **High Throughput**: Millions of events per second
- **Range Queries**: Efficient time-based lookups
- **Storage Efficiency**: Minimize index size
- **Distributed Generation**: No coordination bottlenecks

## TSID (Time-Sorted Unique Identifier)

High-performance time series IDs with embedded timestamps:

```
|     48 bits     |    16 bits    |
|   timestamp_ms  |   random      |
```

### Implementation

```python
import time
import random
import threading
from typing import Optional

class TSIDGenerator:
    def __init__(self, node_id: Optional[int] = None):
        self.node_id = node_id or self._generate_node_id()
        self.last_timestamp = 0
        self.counter = 0
        self.lock = threading.Lock()
        
        # Custom epoch to extend timestamp range
        self.epoch = 946684800000  # 2000-01-01 00:00:00 UTC
    
    def _generate_node_id(self) -> int:
        """Generate node ID from MAC address and process ID"""
        import hashlib
        import os
        import socket
        
        data = f"{socket.gethostname()}-{os.getpid()}".encode()
        return int(hashlib.md5(data).hexdigest()[:4], 16)
    
    def generate(self) -> int:
        """Generate time-sorted unique identifier"""
        with self.lock:
            timestamp = int(time.time() * 1000) - self.epoch
            
            if timestamp == self.last_timestamp:
                self.counter = (self.counter + 1) & 0xFFFF
                if self.counter == 0:
                    # Counter overflow, wait for next millisecond
                    while timestamp <= self.last_timestamp:
                        timestamp = int(time.time() * 1000) - self.epoch
            else:
                self.counter = random.randint(0, 0xFFFF)
            
            self.last_timestamp = timestamp
            
            # 64-bit TSID: 48-bit timestamp + 16-bit counter/random
            tsid = (timestamp << 16) | self.counter
            return tsid
    
    def extract_timestamp(self, tsid: int) -> int:
        """Extract timestamp from TSID"""
        return ((tsid >> 16) + self.epoch)
    
    def generate_range(self, start_time: int, end_time: int) -> tuple:
        """Generate TSID range for time-based queries"""
        start_tsid = ((start_time - self.epoch) << 16)
        end_tsid = ((end_time - self.epoch) << 16) | 0xFFFF
        return (start_tsid, end_tsid)

# Usage
generator = TSIDGenerator()
tsid = generator.generate()
timestamp = generator.extract_timestamp(tsid)

print(f"TSID: {tsid}")
print(f"Timestamp: {timestamp}")
print(f"Time: {time.ctime(timestamp/1000)}")
```

### Advantages
- **Perfect Ordering**: Chronologically sorted
- **Range Queries**: Efficient time-based lookups
- **Compact**: 64-bit integers
- **High Performance**: No coordination required

## InfluxDB's Approach

Optimized for high-cardinality time series:

```python
import struct
import hashlib
from typing import Dict, Any

class InfluxTSID:
    def __init__(self, measurement: str, tags: Dict[str, str]):
        self.measurement = measurement
        self.tags = tags
        self.series_key = self._generate_series_key()
    
    def _generate_series_key(self) -> bytes:
        """Generate deterministic series key from measurement+tags"""
        # Sort tags for consistent ordering
        sorted_tags = sorted(self.tags.items())
        key_parts = [self.measurement] + [f"{k}={v}" for k, v in sorted_tags]
        key_string = ",".join(key_parts)
        
        return hashlib.sha256(key_string.encode()).digest()[:8]  # 64-bit
    
    def generate_point_id(self, timestamp_ns: int, field_key: str) -> bytes:
        """Generate unique point ID"""
        # Series key (8 bytes) + timestamp (8 bytes) + field hash (8 bytes)
        field_hash = hashlib.sha256(field_key.encode()).digest()[:8]
        
        point_id = struct.pack('>QQQ', 
                              int.from_bytes(self.series_key, 'big'),
                              timestamp_ns,
                              int.from_bytes(field_hash, 'big'))
        
        return point_id

# Usage for IoT sensor data
tags = {"sensor_id": "temp_001", "location": "datacenter_1", "rack": "A1"}
tsid_gen = InfluxTSID("temperature", tags)

timestamp_ns = time.time_ns()
point_id = tsid_gen.generate_point_id(timestamp_ns, "celsius")
```

## Prometheus Time Series IDs

Label-based series identification:

```python
import hashlib
import struct
from typing import Dict, List, Tuple

class PrometheusSeriesID:
    def __init__(self):
        self.series_cache = {}  # Cache for series ID lookups
    
    def generate_series_id(self, metric_name: str, labels: Dict[str, str]) -> int:
        """Generate deterministic series ID from metric name and labels"""
        # Create deterministic key
        key_parts = [metric_name]
        key_parts.extend([f"{k}={v}" for k, v in sorted(labels.items())])
        series_key = "\n".join(key_parts)
        
        # Use consistent hashing for series ID
        hash_bytes = hashlib.sha256(series_key.encode()).digest()
        series_id = struct.unpack('>Q', hash_bytes[:8])[0]
        
        # Cache the mapping
        self.series_cache[series_id] = (metric_name, labels)
        
        return series_id
    
    def generate_sample_refs(self, series_id: int, 
                           timestamps: List[int]) -> List[Tuple[int, int]]:
        """Generate sample references for time-based storage"""
        refs = []
        for ts in timestamps:
            # Encode series ID and timestamp for efficient lookup
            # High bits: series_id, Low bits: timestamp bucket
            bucket = ts // 1000  # 1-second buckets
            ref = (series_id, bucket)
            refs.append(ref)
        
        return refs

# Usage for monitoring metrics
prom_gen = PrometheusSeriesID()

# HTTP request metrics
labels = {
    "method": "GET",
    "status": "200", 
    "handler": "/api/users"
}
series_id = prom_gen.generate_series_id("http_requests_total", labels)

timestamps = [int(time.time() * 1000) + i*1000 for i in range(10)]
sample_refs = prom_gen.generate_sample_refs(series_id, timestamps)
```

## OpenTSDB Row Keys

Structured time series storage:

```python
import struct
import hashlib
from typing import Dict

class OpenTSDBRowKey:
    def __init__(self, salt_width: int = 1):
        self.salt_width = salt_width  # For better distribution
    
    def generate_row_key(self, metric: str, timestamp: int, 
                        tags: Dict[str, str]) -> bytes:
        """Generate OpenTSDB-style row key"""
        
        # 1. Generate metric UID (3 bytes)
        metric_uid = self._get_metric_uid(metric)
        
        # 2. Timestamp (4 bytes, hour precision for hot data)
        ts_hour = timestamp // 3600  # Hour-level bucketing
        ts_bytes = struct.pack('>I', ts_hour)
        
        # 3. Generate tag UIDs
        tag_uids = []
        for tag_name, tag_value in sorted(tags.items()):
            name_uid = self._get_tag_uid(tag_name)
            value_uid = self._get_tag_uid(tag_value)
            tag_uids.extend([name_uid, value_uid])
        
        # 4. Optional salt for better distribution
        salt = self._generate_salt(metric_uid + ts_bytes) if self.salt_width > 0 else b''
        
        # Combine: salt + metric_uid + timestamp + tag_uids
        row_key = salt + metric_uid + ts_bytes + b''.join(tag_uids)
        
        return row_key
    
    def _get_metric_uid(self, metric: str) -> bytes:
        """Generate 3-byte UID for metric name"""
        hash_val = hashlib.sha256(metric.encode()).digest()
        return hash_val[:3]
    
    def _get_tag_uid(self, tag: str) -> bytes:
        """Generate 3-byte UID for tag name/value"""
        hash_val = hashlib.sha256(tag.encode()).digest()
        return hash_val[:3]
    
    def _generate_salt(self, data: bytes) -> bytes:
        """Generate salt for better HBase distribution"""
        if self.salt_width == 0:
            return b''
        
        hash_val = hashlib.sha256(data).digest()
        return hash_val[:self.salt_width]
    
    def parse_row_key(self, row_key: bytes) -> Dict:
        """Parse components from row key"""
        offset = 0
        
        # Salt
        if self.salt_width > 0:
            salt = row_key[offset:offset + self.salt_width]
            offset += self.salt_width
        
        # Metric UID
        metric_uid = row_key[offset:offset + 3]
        offset += 3
        
        # Timestamp
        timestamp = struct.unpack('>I', row_key[offset:offset + 4])[0]
        offset += 4
        
        # Tag UIDs (remaining bytes, in pairs)
        tag_uids = []
        while offset < len(row_key):
            name_uid = row_key[offset:offset + 3]
            value_uid = row_key[offset + 3:offset + 6]
            tag_uids.append((name_uid, value_uid))
            offset += 6
        
        return {
            'metric_uid': metric_uid,
            'timestamp': timestamp,
            'tag_uids': tag_uids
        }

# Usage for system metrics
tsdb_gen = OpenTSDBRowKey(salt_width=1)

tags = {
    "host": "web01",
    "interface": "eth0",
    "direction": "in"
}

timestamp = int(time.time())
row_key = tsdb_gen.generate_row_key("network.bytes", timestamp, tags)
parsed = tsdb_gen.parse_row_key(row_key)

print(f"Row key: {row_key.hex()}")
print(f"Parsed: {parsed}")
```

## Time Series Sharding

Distribute time series data across nodes:

```python
import hashlib
import struct
from datetime import datetime, timedelta
from typing import List, Tuple

class TimeSeriesSharder:
    def __init__(self, num_shards: int, time_partition_hours: int = 24):
        self.num_shards = num_shards
        self.time_partition_hours = time_partition_hours
    
    def get_shard_assignment(self, series_id: int, timestamp: int) -> Tuple[int, str]:
        """Get shard and partition for a time series point"""
        
        # Temporal partitioning
        dt = datetime.fromtimestamp(timestamp)
        partition_start = dt.replace(
            hour=(dt.hour // self.time_partition_hours) * self.time_partition_hours,
            minute=0, second=0, microsecond=0
        )
        partition_key = partition_start.strftime("%Y%m%d_%H")
        
        # Hash-based sharding within partition
        shard_hash = hashlib.sha256(
            struct.pack('>QQ', series_id, int(partition_start.timestamp()))
        ).digest()
        
        shard_id = int.from_bytes(shard_hash[:4], 'big') % self.num_shards
        
        return shard_id, partition_key
    
    def get_query_shards(self, series_ids: List[int], 
                        start_time: int, end_time: int) -> Dict[int, List[str]]:
        """Get all shards and partitions needed for a query"""
        shard_partitions = {}
        
        # Generate all time partitions in range
        start_dt = datetime.fromtimestamp(start_time)
        end_dt = datetime.fromtimestamp(end_time)
        
        current = start_dt.replace(
            hour=(start_dt.hour // self.time_partition_hours) * self.time_partition_hours,
            minute=0, second=0, microsecond=0
        )
        
        partitions = []
        while current <= end_dt:
            partitions.append(current.strftime("%Y%m%d_%H"))
            current += timedelta(hours=self.time_partition_hours)
        
        # Map series to shards for each partition
        for series_id in series_ids:
            for partition in partitions:
                partition_ts = int(datetime.strptime(partition, "%Y%m%d_%H").timestamp())
                shard_id, _ = self.get_shard_assignment(series_id, partition_ts)
                
                if shard_id not in shard_partitions:
                    shard_partitions[shard_id] = set()
                shard_partitions[shard_id].add(partition)
        
        # Convert sets to lists
        return {shard: list(parts) for shard, parts in shard_partitions.items()}

# Usage for distributed time series query
sharder = TimeSeriesSharder(num_shards=16, time_partition_hours=6)

# Query multiple series over time range
series_ids = [12345, 67890, 13579]
start_time = int(time.time()) - 86400  # 24 hours ago
end_time = int(time.time())

query_plan = sharder.get_query_shards(series_ids, start_time, end_time)
print(f"Query plan: {query_plan}")
```

## Performance Optimizations

### Batch Generation
```python
class BatchTSIDGenerator:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.generator = TSIDGenerator()
        self.pre_generated = []
        self.index = 0
    
    def generate_batch(self) -> List[int]:
        """Pre-generate batch of TSIDs"""
        batch = []
        base_timestamp = int(time.time() * 1000)
        
        for i in range(self.batch_size):
            # Add microsecond precision within millisecond
            timestamp_offset = i * 1000  # microseconds
            tsid = self.generator.generate()
            batch.append(tsid)
        
        return batch
    
    def next_id(self) -> int:
        """Get next ID from pre-generated batch"""
        if self.index >= len(self.pre_generated):
            self.pre_generated = self.generate_batch()
            self.index = 0
        
        tsid = self.pre_generated[self.index]
        self.index += 1
        return tsid

# High-throughput usage
batch_gen = BatchTSIDGenerator(batch_size=10000)

# Generate millions of IDs efficiently
start_time = time.time()
ids = [batch_gen.next_id() for _ in range(1000000)]
duration = time.time() - start_time

print(f"Generated 1M IDs in {duration:.2f}s ({1000000/duration:.0f} IDs/sec)")
```

### Memory-Efficient Storage
```python
import struct
from typing import List, Iterator

class CompressedTSID:
    def __init__(self):
        self.base_timestamp = None
        self.deltas = []
    
    def compress_sequence(self, tsids: List[int]) -> bytes:
        """Compress sequence of TSIDs using delta encoding"""
        if not tsids:
            return b''
        
        # Extract timestamps
        timestamps = [(tsid >> 16) for tsid in tsids]
        
        # Delta encode timestamps
        self.base_timestamp = timestamps[0]
        deltas = [timestamps[i] - timestamps[i-1] 
                 for i in range(1, len(timestamps))]
        
        # Pack efficiently
        compressed = struct.pack('>Q', self.base_timestamp)  # Base timestamp
        compressed += struct.pack('>H', len(deltas))         # Count
        
        # Variable-length encoding for deltas
        for delta in deltas:
            if delta < 256:
                compressed += struct.pack('>BB', 1, delta)    # 1-byte delta
            elif delta < 65536:
                compressed += struct.pack('>BH', 2, delta)    # 2-byte delta
            else:
                compressed += struct.pack('>BI', 4, delta)    # 4-byte delta
        
        return compressed
    
    def decompress_sequence(self, compressed: bytes) -> List[int]:
        """Decompress TSID sequence"""
        offset = 0
        
        # Read base timestamp
        base_timestamp = struct.unpack('>Q', compressed[offset:offset+8])[0]
        offset += 8
        
        # Read count
        count = struct.unpack('>H', compressed[offset:offset+2])[0]
        offset += 2
        
        # Reconstruct timestamps
        timestamps = [base_timestamp]
        current = base_timestamp
        
        for _ in range(count):
            size = struct.unpack('>B', compressed[offset:offset+1])[0]
            offset += 1
            
            if size == 1:
                delta = struct.unpack('>B', compressed[offset:offset+1])[0]
            elif size == 2:
                delta = struct.unpack('>H', compressed[offset:offset+2])[0]
            else:  # size == 4
                delta = struct.unpack('>I', compressed[offset:offset+4])[0]
            
            offset += size
            current += delta
            timestamps.append(current)
        
        # Convert back to TSIDs (simplified - assumes random parts)
        tsids = [(ts << 16) for ts in timestamps]
        return tsids

# Usage for archival storage
compressor = CompressedTSID()

# Generate sequence of TSIDs
generator = TSIDGenerator()
original_tsids = [generator.generate() for _ in range(10000)]

# Compress
compressed = compressor.compress_sequence(original_tsids)
decompressed = compressor.decompress_sequence(compressed)

compression_ratio = len(compressed) / (len(original_tsids) * 8)
print(f"Compression ratio: {compression_ratio:.2f}")
```

<div class="decision-box">
<strong>Decision Framework</strong>:

- **High-throughput logs**: TSID with batch generation
- **Multi-tenant metrics**: Prometheus-style series IDs  
- **IoT sensor data**: InfluxDB approach with tags
- **Large-scale monitoring**: OpenTSDB row keys with salting
- **Financial data**: Hierarchical time buckets
- **Query-heavy workloads**: Time-partitioned sharding
</div>

## Trade-offs

| Approach | Ordering | Query Performance | Storage Efficiency | Throughput | Complexity |
|----------|----------|------------------|-------------------|------------|------------|
| TSID | Perfect | Excellent | High | Very High | Low |
| InfluxDB | Perfect | Excellent | High | High | Medium |
| Prometheus | By Series | Good | Medium | High | Medium |
| OpenTSDB | Perfect | Excellent | Medium | Very High | High |
| Sharded | Perfect | Excellent | High | Very High | High |

## Common Pitfalls

1. **Clock Synchronization**: Distributed nodes with unsynchronized clocks
   - **Solution**: Use NTP, logical clocks, or time oracles

2. **Hot Partitions**: All recent data goes to same partition
   - **Solution**: Add randomness or hash-based distribution

3. **Query Fanout**: Time range queries hit too many shards
   - **Solution**: Optimize time partitioning granularity

4. **Storage Bloat**: Inefficient encoding of time series data
   - **Solution**: Delta compression, columnar storage

## Related Patterns
- [ID Generation at Scale](id-generation-scale.md) - General ID generation
- [Event Sourcing](event-sourcing.md) - Event ordering patterns
- [Sharding](sharding.md) - Data distribution strategies
- [LSM Tree](lsm-tree.md) - Time-series storage engines

## References
- [TSID Specification](https://github.com/f4b6a3/tsid-creator)
- [InfluxDB Storage Engine](https://docs.influxdata.com/influxdb/v2.0/reference/internals/storage-engine/)
- [Prometheus TSDB](https://prometheus.io/docs/prometheus/latest/storage/)
- [OpenTSDB Architecture](http://opentsdb.net/docs/build/html/user_guide/backends/hbase.html)