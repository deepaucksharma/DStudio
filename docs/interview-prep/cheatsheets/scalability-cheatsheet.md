# Scalability Cheatsheet

## 📊 Latency Numbers Every Architect Should Know (2024)

### Memory & CPU Operations
| Operation | Time | Human Scale | Notes |
|-----------|------|-------------|-------|
| L1 cache reference | 0.5 ns | 0.5 seconds | |
| Branch mispredict | 5 ns | 5 seconds | 10x L1 cache |
| L2 cache reference | 7 ns | 7 seconds | 14x L1 cache |
| Mutex lock/unlock | 25 ns | 25 seconds | |
| Main memory reference | 100 ns | 1.5 minutes | 20x L2 cache |

### I/O Operations
| Operation | Time | Human Scale | Notes |
|-----------|------|-------------|-------|
| Compress 1KB (Zippy) | 3 μs | 50 minutes | |
| Send 1KB over 1 Gbps | 10 μs | 3 hours | |
| Read 4KB from SSD | 150 μs | 1.5 days | |
| Read 1MB from memory | 250 μs | 3 days | |
| Round trip in datacenter | 500 μs | 6 days | |
| Read 1MB from SSD | 1 ms | 11 days | 4x memory |
| Disk seek | 10 ms | 4 months | 20x SSD |
| Read 1MB from disk | 20 ms | 8 months | 80x memory |
| Send packet CA→EU→CA | 150 ms | 5 years | |

## 🚀 Throughput Benchmarks

### Database Operations
| System | Read QPS | Write QPS | Notes |
|--------|----------|-----------|-------|
| MySQL (single) | 10K | 5K | Depends on query complexity |
| PostgreSQL (single) | 15K | 8K | With connection pooling |
| Redis | 100K | 100K | Single threaded |
| Cassandra (node) | 50K | 20K | Eventually consistent |
| DynamoDB | Unlimited* | Unlimited* | Pay per request |

### Message Queue Throughput
| System | Messages/sec | Latency | Use Case |
|--------|--------------|---------|----------|
| RabbitMQ | 50K | 1-10ms | Reliable delivery |
| Kafka | 1M+ | 2-5ms | Event streaming |
| Redis Pub/Sub | 100K | <1ms | Simple pub/sub |
| SQS | 300K | 10-100ms | Managed queue |
| Kinesis | 1M+ | 200ms | Stream processing |

### Web Server Capacity
| Server Type | Requests/sec | Concurrent | Notes |
|-------------|--------------|------------|-------|
| Nginx (static) | 50K | 100K | Static files |
| Nginx (proxy) | 20K | 50K | Reverse proxy |
| Node.js | 10K | 10K | Single threaded |
| Go HTTP | 30K | 100K | Goroutines |
| Java (Spring) | 15K | 5K | Thread pool |

## 📐 System Limits

### Operating System
| Resource | Typical Limit | Notes |
|----------|---------------|-------|
| File descriptors | 65K | Per process |
| TCP connections | 65K | Per IP (port limit) |
| Threads | 10K | Practical limit |
| Memory per process | 128GB | Depends on system |

### Network Limits
| Type | Bandwidth | Packets/sec | Latency |
|------|-----------|-------------|---------|
| 1 Gbps NIC | 125 MB/s | 1.5M | 0.1ms |
| 10 Gbps NIC | 1.25 GB/s | 15M | 0.01ms |
| AWS instance | 25 Gbps | 37M | Variable |
| Cross-region | Variable | Variable | 10-150ms |

### Storage IOPS
| Storage Type | Read IOPS | Write IOPS | Throughput |
|--------------|-----------|------------|------------|
| HDD | 100 | 100 | 100 MB/s |
| SSD SATA | 50K | 30K | 500 MB/s |
| SSD NVMe | 500K | 200K | 3 GB/s |
| EBS gp3 | 16K | 16K | 1 GB/s |
| EBS io2 | 256K | 256K | 4 GB/s |

## 🧮 Quick Estimation Formulas

### Traffic Estimation
```
Daily Active Users (DAU) = Total Users × 0.1-0.3
Peak QPS = (DAU × Actions/Day) / 86400 × 3
Bandwidth = QPS × Average Request Size
Storage/Year = Daily Data × 365 × Retention
```

### Capacity Planning
```
Servers Needed = Peak QPS / Server Capacity
Cache Size = Working Set × 1.2
Database Size = (Records × Record Size) × (1 + Index Overhead)
Network Bandwidth = (Ingress + Egress) × Peak Factor
```

### Availability Calculation
```
Availability = MTBF / (MTBF + MTTR)
Compound Availability = A1 × A2 × ... × An
Redundant Availability = 1 - (1-A)^n

99.9% = 43.8 minutes/month = 8.76 hours/year
99.99% = 4.38 minutes/month = 52.56 minutes/year
99.999% = 26 seconds/month = 5.26 minutes/year
```

### Little's Law
```
L = λ × W
where:
L = Average number in system
λ = Average arrival rate
W = Average time in system

Example: 100 req/s × 0.1s latency = 10 concurrent requests
```

## 📏 Rules of Thumb

### Database Scaling
- **Read-heavy**: 80% reads → Read replicas
- **Write-heavy**: >20% writes → Sharding
- **Cache hit rate**: Target >90% for hot data
- **Connection pool**: 10-20 connections per core

### Caching
- **80/20 Rule**: 20% of data serves 80% of requests
- **TTL**: Set to 10% of update frequency
- **Cache size**: 20% of total dataset typically sufficient
- **Warming**: Pre-load critical data on startup

### API Design
- **Pagination**: 20-100 items per page
- **Timeout**: 95th percentile latency × 3
- **Retry**: 3 attempts with exponential backoff
- **Rate limit**: 10x average usage per client

### Microservices
- **Service size**: 1-3 weeks for rewrite
- **Team size**: 5-8 people per service
- **Dependencies**: Max 3-5 direct dependencies
- **Startup time**: Under 30 seconds

## 🎯 Scaling Milestones

| Users | Architecture | Key Challenges |
|-------|--------------|----------------|
| 0-100 | Monolith on single server | Getting started |
| 100-1K | Separate web/DB servers | Basic reliability |
| 1K-10K | Load balancer + cache | Database load |
| 10K-100K | Read replicas + CDN | Write scaling |
| 100K-1M | Sharding + microservices | Complexity |
| 1M-10M | Multi-region + cell arch | Global latency |
| 10M-100M | Edge computing | Cost optimization |
| 100M+ | Custom everything | Novel problems |

## ⚡ Performance Tips

### Quick Wins
1. **Add caching**: 10-100x improvement
2. **Database indexes**: 10-1000x for queries
3. **Connection pooling**: 5-10x throughput
4. **Compression**: 2-10x bandwidth saving
5. **CDN**: 50% latency reduction

### Common Bottlenecks
1. **Database**: Single writer limitation
2. **Network**: Bandwidth or latency
3. **CPU**: Inefficient algorithms
4. **Memory**: Large working sets
5. **Disk I/O**: Random access patterns

### Optimization Priority
1. **Measure first**: Profile before optimizing
2. **Biggest impact**: Focus on slowest operations
3. **Architectural**: Better than code optimization
4. **Caching**: Easiest high-impact change
5. **Async processing**: Improve perceived performance