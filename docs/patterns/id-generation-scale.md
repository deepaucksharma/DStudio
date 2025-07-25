---
title: ID Generation at Scale
description: Strategies for generating unique identifiers in distributed systems at massive scale
type: pattern
category: specialized
difficulty: intermediate
reading_time: 30 min
prerequisites: [distributed-systems-basics, sharding, time-synchronization]
when_to_use: URL shorteners, social media platforms, e-commerce systems requiring billions of unique IDs
when_not_to_use: Single-node applications, low-throughput systems, when UUIDs suffice
status: complete
last_updated: 2025-07-24
---

# ID Generation at Scale


## Overview

Generating unique identifiers at massive scale presents fundamental challenges in distributed systems. Systems like Twitter, Instagram, and URL shorteners must generate billions of unique IDs while maintaining uniqueness, ordering, and high performance.

<div class="law-box">
<strong>Core Constraint</strong>: At scale, centralized ID generation becomes a bottleneck. The system must balance uniqueness guarantees with performance requirements.
</div>

## The Challenge

Traditional approaches fail at scale:

```python
# ❌ Database auto-increment - bottleneck
CREATE TABLE posts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    content TEXT
);

# ❌ UUID - too large, no ordering
import uuid
id = uuid.uuid4()  # 128 bits, random ordering
```

**Requirements at Scale**:
- **Uniqueness**: Global uniqueness across all nodes
- **Ordering**: Roughly time-ordered for better DB performance
- **Performance**: Generate millions of IDs per second
- **Compact**: Fit in 64 bits for efficiency
- **Availability**: No single point of failure

## Snowflake Algorithm

Twitter's Snowflake generates 64-bit IDs with embedded timestamp:

```
|1|         41        |  10  |    12    |
|0|    timestamp       | node |  sequence |
```

### Implementation

```python
import time
import threading

class SnowflakeGenerator:
    def __init__(self, node_id):
        self.node_id = node_id & 0x3FF  # 10 bits
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()
        
        # Custom epoch (Twitter uses 2010-11-04 01:42:54 UTC)
        self.epoch = 1288834974657
    
    def generate(self):
        with self.lock:
            timestamp = int(time.time() * 1000)  # milliseconds
            
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards")
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
                if self.sequence == 0:
                    # Sequence overflow, wait for next millisecond
                    timestamp = self._wait_next_millis(timestamp)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # Combine components
            id = ((timestamp - self.epoch) << 22) | \
                 (self.node_id << 12) | \
                 self.sequence
            
            return id
    
    def _wait_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp

# Usage
generator = SnowflakeGenerator(node_id=1)
id = generator.generate()
print(f"Generated ID: {id}")  # e.g., 175928847299117824
```

### Advantages
- **Ordered**: Roughly time-ordered
- **Compact**: 64-bit integers
- **Fast**: No network calls required
- **Unique**: Guaranteed uniqueness

### Limitations
- **Clock dependency**: Requires synchronized clocks
- **Node management**: Must assign unique node IDs
- **Sequence overflow**: Limited to 4096 IDs per millisecond per node

## Instagram's Approach

Modified Snowflake with database sharding awareness:

```sql
-- Two sequences per logical shard
CREATE OR REPLACE FUNCTION insta_id(OUT result bigint) AS $$
DECLARE
    our_epoch bigint := 1314220021721;  -- Instagram epoch
    seq_id bigint;
    now_millis bigint;
    shard_id int := 5;  -- Shard number
BEGIN
    -- Get milliseconds since epoch
    SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;
    
    -- Get sequence number
    SELECT nextval('insta_sequence') % 1024 INTO seq_id;
    
    result := (now_millis - our_epoch) << 23;
    result := result | (shard_id << 10);
    result := result | (seq_id);
END;
$$ LANGUAGE plpgsql;
```

## MongoDB ObjectId

12-byte identifier with embedded metadata:

```javascript
// ObjectId structure (12 bytes = 96 bits)
// |  4 bytes  |  5 bytes  | 3 bytes |
// | timestamp | random    | counter |

class ObjectId {
    constructor() {
        this.timestamp = Math.floor(Date.now() / 1000);  // 4 bytes
        this.random = this.generateRandom(5);            // 5 bytes
        this.counter = ObjectId.getNextCounter();        // 3 bytes
    }
    
    static getNextCounter() {
        ObjectId._counter = (ObjectId._counter + 1) % 0xFFFFFF;
        return ObjectId._counter;
    }
    
    generateRandom(bytes) {
        // Generate random bytes (machine ID + process ID)
        const crypto = require('crypto');
        return crypto.randomBytes(bytes);
    }
    
    toString() {
        // Convert to 24-character hex string
        const timestamp = this.timestamp.toString(16).padStart(8, '0');
        const random = this.random.toString('hex');
        const counter = this.counter.toString(16).padStart(6, '0');
        return timestamp + random + counter;
    }
}

ObjectId._counter = Math.floor(Math.random() * 0xFFFFFF);
```

## ULID (Universally Unique Lexicographically Sortable Identifier)

Combines timestamp and randomness for sortability:

```python
import time
import random
import base32_crockford

class ULID:
    def __init__(self):
        self.encoding = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    
    def generate(self):
        # 48-bit timestamp (milliseconds)
        timestamp = int(time.time() * 1000)
        
        # 80-bit randomness
        randomness = random.getrandbits(80)
        
        # Encode to base32
        timestamp_str = self._encode_timestamp(timestamp)
        random_str = self._encode_randomness(randomness)
        
        return timestamp_str + random_str
    
    def _encode_timestamp(self, timestamp):
        # Convert to 10-character base32 string
        result = ""
        for _ in range(10):
            result = self.encoding[timestamp % 32] + result
            timestamp //= 32
        return result
    
    def _encode_randomness(self, randomness):
        # Convert to 16-character base32 string
        result = ""
        for _ in range(16):
            result = self.encoding[randomness % 32] + result
            randomness //= 32
        return result

# Usage
ulid = ULID()
id = ulid.generate()
print(f"ULID: {id}")  # e.g., 01ARZ3NDEKTSV4RRFFQ69G5FAV
```

## Sonyflake (Sony's Variation)

39-bit timestamp, 16-bit sequence, 8-bit machine ID:

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Sonyflake struct {
    mutex     sync.Mutex
    startTime int64
    machineID uint16
    sequence  uint16
    lastTime  int64
}

func NewSonyflake(machineID uint8) *Sonyflake {
    return &Sonyflake{
        startTime: time.Date(2014, 9, 1, 0, 0, 0, 0, time.UTC).Unix(),
        machineID: uint16(machineID),
        sequence:  0,
        lastTime:  -1,
    }
}

func (sf *Sonyflake) NextID() (uint64, error) {
    sf.mutex.Lock()
    defer sf.mutex.Unlock()
    
    now := time.Now().Unix()
    
    if now < sf.lastTime {
        return 0, fmt.Errorf("clock moved backwards")
    }
    
    if now == sf.lastTime {
        sf.sequence = (sf.sequence + 1) & 0xFFFF
        if sf.sequence == 0 {
            // Wait for next second
            for now <= sf.lastTime {
                time.Sleep(time.Millisecond)
                now = time.Now().Unix()
            }
        }
    } else {
        sf.sequence = 0
    }
    
    sf.lastTime = now
    
    // Combine components (63 bits total)
    id := uint64((now-sf.startTime)&0x7FFFFFFFFF) << 24  // 39 bits
    id |= uint64(sf.sequence&0xFFFF) << 8                // 16 bits
    id |= uint64(sf.machineID & 0xFF)                    // 8 bits
    
    return id, nil
}
```

## Flake ID (Boundary's Approach)

128-bit IDs for even higher scale:

```python
import struct
import socket
import os
import time

class FlakeID:
    def __init__(self):
        self.worker_id = self._generate_worker_id()
        self.sequence = 0
        self.last_timestamp = 0
    
    def _generate_worker_id(self):
        # Combine hostname and process ID
        hostname = socket.gethostname()
        pid = os.getpid()
        combined = f"{hostname}-{pid}"
        return hash(combined) & 0xFFFF  # 16 bits
    
    def generate(self):
        timestamp = int(time.time() * 1000)  # milliseconds
        
        if timestamp < self.last_timestamp:
            raise ValueError("Clock moved backwards")
        
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF
            if self.sequence == 0:
                # Wait for next millisecond
                while timestamp <= self.last_timestamp:
                    timestamp = int(time.time() * 1000)
        else:
            self.sequence = 0
        
        self.last_timestamp = timestamp
        
        # 128-bit ID structure
        # 64-bit timestamp + 16-bit worker + 12-bit sequence + 36-bit random
        random_bits = os.urandom(5)  # 40 bits, use 36
        
        high_64 = timestamp << 16 | self.worker_id
        low_64 = self.sequence << 36 | (int.from_bytes(random_bits, 'big') & 0xFFFFFFFFF)
        
        return (high_64 << 64) | low_64

# Usage
flake = FlakeID()
id = flake.generate()
print(f"FlakeID: {id:032x}")  # 128-bit hex
```

## Performance Comparison

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def benchmark_generator(generator_class, iterations=1000000):
    generator = generator_class()
    
    start_time = time.time()
    
    def generate_batch(count):
        for _ in range(count):
            generator.generate()
    
    # Multi-threaded test
    with ThreadPoolExecutor(max_workers=10) as executor:
        batch_size = iterations // 10
        futures = [
            executor.submit(generate_batch, batch_size) 
            for _ in range(10)
        ]
        
        for future in futures:
            future.result()
    
    duration = time.time() - start_time
    ids_per_second = iterations / duration
    
    return ids_per_second

# Results (approximate)
# Snowflake: ~2M IDs/second
# ULID: ~500K IDs/second
# ObjectId: ~800K IDs/second
# UUID4: ~300K IDs/second
```

## URL Shortener Specific Considerations

For URL shorteners, additional requirements:

### Base62 Encoding for Short URLs

```python
class Base62Encoder:
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = len(ALPHABET)
    
    @classmethod
    def encode(cls, num):
        if num == 0:
            return cls.ALPHABET[0]
        
        result = ""
        while num > 0:
            result = cls.ALPHABET[num % cls.BASE] + result
            num //= cls.BASE
        return result
    
    @classmethod
    def decode(cls, encoded):
        result = 0
        for char in encoded:
            result = result * cls.BASE + cls.ALPHABET.index(char)
        return result

# Snowflake ID to short URL
snowflake_id = 175928847299117824
short_url = Base62Encoder.encode(snowflake_id)
print(f"Short URL: {short_url}")  # e.g., "dQw4w9WgXcQ"
```

### Custom Short ID Generation

```python
class ShortIDGenerator:
    def __init__(self, node_id, min_length=7):
        self.node_id = node_id
        self.min_length = min_length
        self.counter = 0
        self.last_timestamp = 0
    
    def generate_short_id(self):
        # Generate Snowflake-style ID
        timestamp = int(time.time() * 1000)
        
        if timestamp == self.last_timestamp:
            self.counter += 1
        else:
            self.counter = 0
            self.last_timestamp = timestamp
        
        # Compact ID: 32-bit timestamp + 16-bit node + 16-bit counter
        compact_id = ((timestamp & 0xFFFFFFFF) << 32) | \
                    ((self.node_id & 0xFFFF) << 16) | \
                    (self.counter & 0xFFFF)
        
        # Encode to base62
        short_id = Base62Encoder.encode(compact_id)
        
        # Ensure minimum length for consistency
        while len(short_id) < self.min_length:
            short_id = "0" + short_id
        
        return short_id

# Usage
generator = ShortIDGenerator(node_id=1)
short_id = generator.generate_short_id()
print(f"Short ID: {short_id}")  # e.g., "0dQw4w9"
```

## Collision Detection and Handling

```python
import hashlib
import redis

class CollisionSafeGenerator:
    def __init__(self, primary_generator, collision_store):
        self.primary = primary_generator
        self.store = collision_store  # Redis instance
    
    def generate_with_collision_check(self, max_retries=3):
        for attempt in range(max_retries):
            # Generate ID using primary method
            candidate_id = self.primary.generate()
            
            # Check for collision
            if not self.store.exists(f"id:{candidate_id}"):
                # Reserve the ID
                self.store.setex(f"id:{candidate_id}", 86400, "reserved")
                return candidate_id
            
            # Collision detected, add entropy
            self.primary.sequence += hash(str(attempt)) & 0xFF
        
        raise Exception("Failed to generate unique ID after retries")

# Usage with Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
snowflake = SnowflakeGenerator(node_id=1)
safe_generator = CollisionSafeGenerator(snowflake, redis_client)

unique_id = safe_generator.generate_with_collision_check()
```

## Advanced Patterns

### Hierarchical IDs
```python
# Format: datacenter.rack.node.timestamp.sequence
# Example: 01.05.003.1640995200000.00001

class HierarchicalID:
    def __init__(self, datacenter_id, rack_id, node_id):
        self.datacenter_id = datacenter_id & 0xFF    # 8 bits
        self.rack_id = rack_id & 0xFF                # 8 bits  
        self.node_id = node_id & 0xFF                # 8 bits
        self.sequence = 0
        self.last_timestamp = 0
    
    def generate(self):
        timestamp = int(time.time() * 1000)
        
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFFF
        else:
            self.sequence = 0
            self.last_timestamp = timestamp
        
        # 64-bit hierarchical ID
        id = (self.datacenter_id << 56) | \
             (self.rack_id << 48) | \
             (self.node_id << 40) | \
             ((timestamp & 0xFFFFFFFF) << 8) | \
             (self.sequence & 0xFF)
        
        return id
```

### Time-Bucketed IDs
```python
class TimeBucketedID:
    def __init__(self, node_id, bucket_size_ms=1000):
        self.node_id = node_id
        self.bucket_size = bucket_size_ms
        self.current_bucket = 0
        self.bucket_sequence = 0
    
    def generate(self):
        timestamp = int(time.time() * 1000)
        bucket = timestamp // self.bucket_size
        
        if bucket != self.current_bucket:
            self.current_bucket = bucket
            self.bucket_sequence = 0
        
        self.bucket_sequence += 1
        
        # ID includes bucket number for better sharding
        id = (bucket << 32) | (self.node_id << 16) | self.bucket_sequence
        return id
```

<div class="decision-box">
<strong>Decision Framework</strong>:

- **High throughput, ordering important**: Snowflake
- **Database-friendly, moderate scale**: MongoDB ObjectId  
- **Lexicographic sorting needed**: ULID
- **URL shortening**: Custom base62 with collision detection
- **Multi-datacenter**: Hierarchical IDs
- **Extremely high scale**: 128-bit Flake IDs
- **Simple, no coordination**: UUID4
</div>

## Trade-offs

| Approach | Uniqueness | Ordering | Size | Performance | Complexity |
|----------|------------|----------|------|-------------|------------|
| Snowflake | Guaranteed | Time-ordered | 64-bit | Very High | Medium |
| ObjectId | Guaranteed | Time-ordered | 96-bit | High | Low |
| ULID | Guaranteed | Lexicographic | 128-bit | Medium | Low |
| UUID4 | Very High | Random | 128-bit | High | Very Low |
| FlakeID | Guaranteed | Time-ordered | 128-bit | Very High | High |

## Failure Modes

1. **Clock Skew**: Timestamps drift between nodes
   - **Solution**: NTP synchronization, clock skew detection

2. **Sequence Overflow**: Too many IDs per time unit
   - **Solution**: Wait for next time unit, increase sequence bits

3. **Node ID Conflicts**: Multiple nodes use same ID
   - **Solution**: Central node registry, MAC address derivation

4. **Network Partitions**: Coordination service unavailable
   - **Solution**: Pre-allocated ranges, graceful degradation

## Related Patterns
- [Time Series IDs](time-series-ids.md) - Time-based ID variations
- [Sharding](sharding.md) - ID-based data partitioning
- [Consistent Hashing](/case-studies/consistent-hashing) - ID distribution
- [URL Shortener](/case-studies/url-shortener) - Complete implementation

## References
- [Twitter Snowflake](https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html)
- [Instagram Engineering](https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c)
- [MongoDB ObjectId Specification](https://docs.mongodb.com/manual/reference/method/ObjectId/)
- [ULID Specification](https://github.com/ulid/spec)