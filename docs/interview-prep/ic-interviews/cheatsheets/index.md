---
title: Cheatsheets
description: Cheatsheets overview and navigation
---

# System Design Cheatsheets

Quick reference guides for system design interviews.

## Overview

These cheatsheets provide rapid access to key information during interviews. Print them out or keep them handy for quick reference.

## 📚 Essential Cheatsheets

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } **[Scalability Cheatsheet](../../../architects-handbook/quantitative-analysis/latency-numbers.md)**
    
    ---
    
    Key numbers every architect should know: latency, throughput, system limits, and quick estimation formulas
    
    Perfect for capacity planning and performance discussions

- :material-checkbox-multiple-marked:{ .lg .middle } **[System Design Checklist](system-design-checklist.md)**
    
    ---
    
    Comprehensive checklist for any system design interview from requirements to deployment
    
    Never miss a critical component again

- :material-vector-arrange:{ .lg .middle } **[Common Patterns Reference](../../../../pattern-library/index.md)**
    
    ---
    
    Quick reference for pattern selection, common combinations, and anti-pattern warnings
    
    Make informed architecture decisions quickly

</div>

## 📊 Numbers Every Engineer Should Know

### Latency Numbers (2024)
| Operation | Time | Notes |
|-----------|------|-------|
| L1 cache reference | 0.5 ns | |
| Branch mispredict | 5 ns | |
| L2 cache reference | 7 ns | 14x L1 cache |
| Mutex lock/unlock | 25 ns | |
| Main memory reference | 100 ns | 20x L2 cache |
| Compress 1KB (Zippy) | 3 μs | |
| Send 1KB over 1 Gbps | 10 μs | |
| Read 4KB from SSD | 150 μs | |
| Read 1MB from memory | 250 μs | |
| Round trip in datacenter | 500 μs | |
| Read 1MB from SSD | 1 ms | 4x memory |
| Disk seek | 10 ms | 20x SSD |
| Read 1MB from disk | 20 ms | 80x memory |
| Send packet CA→Netherlands→CA | 150 ms | |

### Capacity Planning
| Scale | Storage | Bandwidth | Compute |
|-------|---------|-----------|---------|
| 1K users | 1 GB | 10 Mbps | 1 server |
| 10K users | 10 GB | 100 Mbps | 2-5 servers |
| 100K users | 100 GB | 1 Gbps | 10-20 servers |
| 1M users | 1 TB | 10 Gbps | 50-100 servers |
| 10M users | 10 TB | 100 Gbps | 200-500 servers |
| 100M users | 100 TB | 1 Tbps | 1000+ servers |

### Data Sizes
| Type | Size | Example |
|------|------|---------|
| Character | 1 byte | 'a' |
| Integer | 4 bytes | 42 |
| UUID | 16 bytes | User ID |
| Timestamp | 8 bytes | Unix time |
| Short text | 100 bytes | Tweet |
| Long text | 1 KB | Email |
| Image (thumb) | 10 KB | Profile pic |
| Image (full) | 1 MB | Photo |
| Video (SD) | 100 MB | 10 min |
| Video (HD) | 1 GB | 10 min |

## 🏗️ System Design Patterns

### Scalability Patterns
| Pattern | Use Case | Trade-off |
|---------|----------|-----------|
| Load Balancer | Distribute requests | Added latency |
| Caching | Reduce DB load | Consistency |
| CDN | Static content | Cost |
| Sharding | Database scaling | Complexity |
| Replication | Read scaling | Consistency |

### Reliability Patterns
| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| Circuit Breaker | Prevent cascades | Fail fast |
| Retry | Handle transients | Exponential backoff |
| Timeout | Bound wait time | Set limits |
| Bulkhead | Isolate resources | Thread pools |
| Health Check | Detect failures | Periodic pings |

### Data Patterns
| Pattern | Consistency | Use Case |
|---------|-------------|----------|
| Master-Slave | Eventual | Read heavy |
| Multi-Master | Eventual | Write heavy |
| 2PC | Strong | Transactions |
| Saga | Eventual | Long transactions |
| Event Sourcing | Eventual | Audit trail |

## 🎯 Decision Trees

### Database Selection
```
Need ACID?
├─ Yes → SQL?
│   ├─ Yes → PostgreSQL/MySQL
│   └─ No → MongoDB (with transactions)
└─ No → Access Pattern?
    ├─ Key-Value → Redis/DynamoDB
    ├─ Document → MongoDB/CouchDB
    ├─ Graph → Neo4j/Neptune
    └─ Time-Series → InfluxDB/Prometheus
```

### Caching Strategy
```
Data Type?
├─ Static → CDN
├─ User Session → Redis
├─ Database Query → Memcached
└─ Computation → Application Cache
```

### Communication Pattern
```
Synchronous Required?
├─ Yes → Latency Critical?
│   ├─ Yes → gRPC
│   └─ No → REST
└─ No → Ordering Required?
    ├─ Yes → Message Queue (Kafka)
    └─ No → Pub/Sub
```

## 📐 Architecture Templates

### Basic 3-Tier
```
[Client] → [Load Balancer] → [App Servers] → [Database]
                ↓
            [Cache Layer]
```

### Microservices
```
[API Gateway] → [Service Mesh] → [Services] → [Databases]
       ↓              ↓               ↓
  [Auth Service]  [Discovery]   [Message Bus]
```

### Real-time System
```
[Clients] ←→ [WebSocket Gateway] ←→ [App Servers]
                     ↓                    ↓
              [Message Queue]      [State Store]
```

## 🔧 Technology Choices

### Message Queues
| Technology | Best For | Throughput |
|------------|----------|------------|
| RabbitMQ | Reliability | 50K msg/s |
| Kafka | Streaming | 1M msg/s |
| Redis Pub/Sub | Simple | 100K msg/s |
| SQS | Managed | 300K msg/s |

### Databases
| Type | Examples | Use Case |
|------|----------|----------|
| RDBMS | PostgreSQL, MySQL | ACID transactions |
| NoSQL | MongoDB, Cassandra | Scale, flexibility |
| Cache | Redis, Memcached | Low latency |
| Search | Elasticsearch | Full-text search |
| Graph | Neo4j | Relationships |

### Load Balancers
| Type | Examples | Features |
|------|----------|----------|
| Hardware | F5, Citrix | High performance |
| Software | HAProxy, Nginx | Flexible, cheap |
| Cloud | ELB, GLB | Managed, scalable |

## ⚡ Quick Formulas

### Availability
```
Availability = MTBF / (MTBF + MTTR)
99.9% = 8.76 hours/year downtime
99.99% = 52.56 minutes/year downtime
```

### Little's Law
```
L = λ × W
L = number in system
λ = arrival rate
W = time in system
```

### Storage
```
Storage = Users × Data/User × Retention × Replication
```

### Bandwidth
```
Bandwidth = Requests/sec × Size/Request
```

## 🚀 Interview Tips

### Do's
- ✅ Start with requirements
- ✅ Make assumptions explicit
- ✅ Draw diagrams
- ✅ Consider trade-offs
- ✅ Think about scale

### Don'ts
- ❌ Over-engineer early
- ❌ Ignore constraints
- ❌ Forget monitoring
- ❌ Skip error handling
- ❌ Assume perfection

---

*Print these cheatsheets or keep them open during practice sessions. For detailed explanations, refer to the main documentation.*