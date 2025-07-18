# Network Optimization Guide

!!! tip "Quick Navigation"
    [← Reference Home](index.md) | 
    [Formulas](formulas.md) |
    [Performance Tuning](performance-tuning.md)

## Overview

Network optimization is crucial for distributed systems performance. This guide covers techniques to minimize latency, maximize throughput, and efficiently use bandwidth.

## Latency Optimization

### 1. Geographic Distribution

#### CDN Strategy
Place content closer to users to reduce propagation delay.

```yaml
CDN Configuration:
  Origins:
    - region: us-east-1
      endpoint: origin.example.com
  
  Edge Locations:
    - region: us-west-2
      cache_ttl: 3600
    - region: eu-west-1
      cache_ttl: 3600
    - region: ap-southeast-1
      cache_ttl: 3600
```

#### Edge Computing
Move computation closer to data sources.

**Benefits**:
- Reduced round-trip times
- Lower bandwidth costs
- Better user experience

### 2. Protocol Optimization

#### HTTP/2 and HTTP/3
Leverage modern protocols for better performance.

**HTTP/2 Benefits**:
- Multiplexing
- Header compression
- Server push
- Stream prioritization

**HTTP/3 (QUIC) Benefits**:
- 0-RTT connection establishment
- Improved packet loss handling
- Connection migration

#### TCP Tuning
Optimize TCP parameters for your use case.

```bash
# Increase TCP buffer sizes
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"

# Enable TCP Fast Open
sysctl -w net.ipv4.tcp_fastopen=3

# Optimize for low latency
sysctl -w net.ipv4.tcp_low_latency=1
```

### 3. Connection Management

#### Connection Pooling
Reuse connections to avoid handshake overhead.

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=Retry(total=3, backoff_factor=0.3)
)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

#### Keep-Alive
Maintain persistent connections.

```
Connection: keep-alive
Keep-Alive: timeout=5, max=1000
```

## Bandwidth Optimization

### 1. Data Compression

#### Algorithm Selection
Choose appropriate compression based on data type.

| Data Type | Algorithm | Compression Ratio | Speed |
|-----------|-----------|------------------|--------|
| Text/JSON | Gzip | High (5-10x) | Medium |
| Text/JSON | Brotli | Very High (10-20x) | Slow |
| Binary | LZ4 | Medium (2-4x) | Very Fast |
| Images | WebP | High | Medium |
| Video | H.265/AV1 | Very High | Slow |

#### Implementation Example
```python
import gzip
import json

def compress_json_response(data):
    json_str = json.dumps(data)
    compressed = gzip.compress(json_str.encode('utf-8'))
    
    # Compression ratio
    ratio = len(json_str) / len(compressed)
    
    return compressed, ratio
```

### 2. Payload Optimization

#### Protocol Buffers
Use binary serialization for efficiency.

```protobuf
syntax = "proto3";

message User {
  uint64 id = 1;
  string name = 2;
  string email = 3;
  
  // Use smaller types when possible
  uint32 age = 4;  // vs int64
  bool active = 5;
}
```

**Size Comparison**:
- JSON: ~120 bytes
- Protocol Buffers: ~40 bytes
- MessagePack: ~60 bytes

#### GraphQL
Fetch only required data.

```graphql
# Instead of fetching entire user object
query {
  user(id: "123") {
    id
    name
    # Only fields we need
  }
}
```

### 3. Caching Strategies

#### Cache Headers
Proper cache control reduces redundant transfers.

```python
@app.route('/static/<path>')
def serve_static(path):
    response = send_file(path)
    
    # Immutable resources (with version in URL)
    if 'v=' in request.url:
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    else:
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['ETag'] = generate_etag(path)
    
    return response
```

## Throughput Optimization

### 1. Batching

#### Request Batching
Combine multiple operations into single request.

```python
# Instead of:
for item_id in item_ids:
    response = api.get(f'/items/{item_id}')

# Use:
response = api.post('/items/batch', json={'ids': item_ids})
```

#### Write Batching
Buffer writes for efficiency.

```python
class BatchWriter:
    def __init__(self, batch_size=100, flush_interval=1.0):
        self.batch = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.last_flush = time.time()
    
    def write(self, item):
        self.batch.append(item)
        
        if len(self.batch) >= self.batch_size or \
           time.time() - self.last_flush > self.flush_interval:
            self.flush()
    
    def flush(self):
        if self.batch:
            bulk_write(self.batch)
            self.batch = []
            self.last_flush = time.time()
```

### 2. Parallel Processing

#### Connection Multiplexing
Use multiple connections for parallel transfers.

```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()
```

### 3. Traffic Shaping

#### Rate Limiting
Prevent network congestion.

```python
from datetime import datetime, timedelta
import time

class TokenBucket:
    def __init__(self, capacity, fill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.fill_rate = fill_rate
        self.last_update = time.time()
    
    def consume(self, tokens=1):
        self.tokens += (time.time() - self.last_update) * self.fill_rate
        self.tokens = min(self.tokens, self.capacity)
        self.last_update = time.time()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

## Monitoring & Diagnostics

### Network Metrics to Track

1. **Latency Metrics**
   - RTT (Round Trip Time)
   - Connection establishment time
   - Time to first byte (TTFB)
   - Total request time

2. **Throughput Metrics**
   - Requests per second
   - Bytes per second
   - Active connections
   - Connection pool utilization

3. **Error Metrics**
   - Timeout rate
   - Connection failures
   - Retry rate
   - Packet loss

### Diagnostic Tools

```bash
# Latency measurement
ping -c 10 example.com
traceroute example.com
mtr --report example.com

# Bandwidth testing
iperf3 -c server.example.com

# TCP analysis
ss -i  # Socket statistics
tcpdump -i any -w capture.pcap

# HTTP performance
curl -w "@curl-format.txt" -o /dev/null -s https://example.com
```

## Best Practices Checklist

### Design Time
- [ ] Choose appropriate protocols (HTTP/2, gRPC, WebSocket)
- [ ] Plan geographic distribution strategy
- [ ] Design for connection reuse
- [ ] Implement proper caching strategy
- [ ] Use efficient serialization formats

### Implementation
- [ ] Enable compression
- [ ] Implement connection pooling
- [ ] Use async I/O where appropriate
- [ ] Batch operations when possible
- [ ] Handle retries with exponential backoff

### Operations
- [ ] Monitor network metrics
- [ ] Set up alerts for anomalies
- [ ] Regular performance testing
- [ ] Capacity planning based on growth
- [ ] Document network topology

## Common Pitfalls

### 1. Chatty Applications
**Problem**: Too many small requests
**Solution**: Batch, cache, or redesign API

### 2. Large Payloads
**Problem**: Transferring unnecessary data
**Solution**: Pagination, filtering, compression

### 3. Connection Churn
**Problem**: Creating new connections for each request
**Solution**: Connection pooling, keep-alive

### 4. Ignoring Geography
**Problem**: All traffic routes through single region
**Solution**: Multi-region deployment, CDN

### 5. No Compression
**Problem**: Sending uncompressed text data
**Solution**: Enable gzip/brotli compression

!!! tip "Golden Rules"
    1. **Measure first** - Don't optimize blindly
    2. **Cache aggressively** - But invalidate correctly
    3. **Batch when possible** - Reduce round trips
    4. **Compress always** - Bandwidth is expensive
    5. **Monitor continuously** - Networks change