# Common Patterns Reference

## 🎯 Pattern Selection Matrix

### By Problem Domain

| Problem | Primary Patterns | Supporting Patterns | Anti-patterns to Avoid |
|---------|-----------------|---------------------|----------------------|
| **High Traffic** | Load Balancer, CDN, Cache-Aside | Circuit Breaker, Rate Limiter | Single server, No caching |
| **High Availability** | Multi-Region, Health Checks | Failover, Blue-Green Deploy | Single point of failure |
| **Data Consistency** | Saga, Event Sourcing | CQRS, Outbox | Two-phase commit at scale |
| **Real-time Updates** | WebSocket, Server-Sent Events | Pub/Sub, Change Data Capture | Polling at high frequency |
| **Heavy Computation** | Map-Reduce, Worker Queue | Batch Processing, Caching | Synchronous processing |
| **Microservices Comm** | Service Mesh, API Gateway | Circuit Breaker, Retry | Direct service calls |

### By Quality Attribute

| Quality | Essential Patterns | Optional Patterns | Considerations |
|---------|-------------------|-------------------|----------------|
| **Scalability** | Sharding, Load Balancing, Caching | Auto-scaling, Cell-based | State management |
| **Reliability** | Circuit Breaker, Retry, Timeout | Bulkhead, Health Check | Cascading failures |
| **Performance** | Caching, CDN, Read Replicas | Materialized Views, Denormalization | Cache invalidation |
| **Security** | API Gateway, OAuth2, Rate Limiting | mTLS, Zero Trust | Defense in depth |
| **Maintainability** | API Versioning, Blue-Green, Feature Flags | Strangler Fig, Branch by Abstraction | Technical debt |

## 🏗️ Common Pattern Combinations

### 1. **Web Application Stack**
```
CDN → Load Balancer → Cache → App Servers → Database
         ↓                         ↓
    Rate Limiter              Message Queue → Workers
```
**Patterns**: CDN + Load Balancing + Cache-Aside + Master-Slave Replication + Queue-Worker

### 2. **Microservices Architecture**
```
API Gateway → Service Mesh → Services → Databases
     ↓              ↓            ↓
Auth Service   Discovery    Event Bus → Event Store
```
**Patterns**: API Gateway + Service Mesh + Service Discovery + Event Sourcing + CQRS

### 3. **Real-time System**
```
Clients ←→ WebSocket Gateway ←→ Pub/Sub ←→ Services
                                  ↓
                            State Store
```
**Patterns**: WebSocket + Pub/Sub + State Synchronization + Circuit Breaker

### 4. **Data Pipeline**
```
Sources → Ingestion → Stream Processing → Data Lake
            ↓               ↓                ↓
        Validation      Real-time         Batch Processing
                       Analytics              ↓
                                          Data Warehouse
```
**Patterns**: Change Data Capture + Stream Processing + Lambda Architecture + ETL

### 5. **E-commerce Platform**
```
Users → CDN → LB → API Gateway → Services
                        ↓
                 [Catalog] [Orders] [Payment]
                     ↓        ↓         ↓
                  Cache    Saga    External API
```
**Patterns**: CDN + API Gateway + Saga + Cache-Aside + Idempotency

## 📊 Pattern Decision Trees

### Caching Strategy Selection
```
Is data user-specific?
├─ Yes → Session Cache
│   └─ High update rate?
│       ├─ Yes → Write-Through
│       └─ No → Cache-Aside
└─ No → Shared Cache
    └─ Frequently updated?
        ├─ Yes → Write-Behind with TTL
        └─ No → Cache-Aside with long TTL
```

### Database Pattern Selection
```
Need ACID transactions?
├─ Yes → SQL Database
│   └─ Read heavy?
│       ├─ Yes → Master-Slave Replication
│       └─ No → Write heavy?
│           ├─ Yes → Sharding
│           └─ No → Single Master
└─ No → NoSQL Options
    └─ Access pattern?
        ├─ Key-Value → Redis/DynamoDB
        ├─ Document → MongoDB
        ├─ Graph → Neo4j
        └─ Wide Column → Cassandra
```

### Communication Pattern Selection
```
Need response immediately?
├─ Yes → Synchronous
│   └─ Performance critical?
│       ├─ Yes → gRPC
│       └─ No → REST/GraphQL
└─ No → Asynchronous
    └─ Need ordering?
        ├─ Yes → Message Queue (Kafka)
        └─ No → Pub/Sub or Event Bus
```

### Deployment Pattern Selection
```
Can tolerate downtime?
├─ Yes → Big Bang Deployment
└─ No → Zero downtime needed?
    └─ Progressive rollout needed?
        ├─ Yes → Canary or Feature Flags
        └─ No → Blue-Green or Rolling
```

## 🔍 Pattern Details Quick Reference

### Scalability Patterns

#### Load Balancing
- **When**: Traffic > single server capacity
- **Types**: Round-robin, Least connections, IP hash
- **Combine with**: Health checks, Auto-scaling
- **Avoid**: Session affinity if possible

#### Caching
- **When**: Repeated reads, expensive computations
- **Levels**: Browser → CDN → App → Database
- **Strategies**: Cache-aside, Write-through, Write-behind
- **Challenge**: Cache invalidation

#### Sharding
- **When**: Data > single database capacity
- **Strategies**: Range, Hash, Geographic
- **Combine with**: Consistent hashing
- **Challenge**: Cross-shard queries

### Reliability Patterns

#### Circuit Breaker
- **When**: Calling external services
- **States**: Closed → Open → Half-Open
- **Combine with**: Retry, Timeout, Fallback
- **Configure**: Failure threshold, timeout, reset

#### Retry
- **When**: Transient failures expected
- **Strategies**: Fixed, Exponential backoff, Jitter
- **Combine with**: Circuit breaker, Idempotency
- **Limit**: Max attempts, total timeout

#### Bulkhead
- **When**: Isolating resources/failures
- **Types**: Thread pool, Semaphore, Connection pool
- **Combine with**: Circuit breaker, Timeout
- **Size**: Based on downstream capacity

### Data Management Patterns

#### Event Sourcing
- **When**: Audit trail needed, time-travel queries
- **Store**: Append-only event log
- **Combine with**: CQRS, Snapshots
- **Challenge**: Event schema evolution

#### CQRS
- **When**: Different read/write patterns
- **Models**: Separate read and write models
- **Combine with**: Event sourcing, Read replicas
- **Sync**: Eventually consistent

#### Saga
- **When**: Distributed transactions
- **Types**: Choreography, Orchestration
- **Combine with**: Compensation, Idempotency
- **Challenge**: Partial failure handling

### Communication Patterns

#### API Gateway
- **When**: Multiple microservices
- **Features**: Routing, Auth, Rate limiting
- **Combine with**: Service discovery, Circuit breaker
- **Avoid**: Business logic in gateway

#### Message Queue
- **When**: Async processing, decoupling
- **Types**: Point-to-point, Pub/sub
- **Combine with**: Dead letter queue, Retry
- **Choose**: RabbitMQ, Kafka, SQS

#### Service Mesh
- **When**: Many microservices
- **Features**: mTLS, Observability, Traffic management
- **Combine with**: Sidecar proxy
- **Options**: Istio, Linkerd, Consul

## ⚡ Quick Decision Guide

### For New Systems
1. Start with: Monolith + Load Balancer + Cache + Single DB
2. Add: CDN for static content
3. Scale: Read replicas, then sharding
4. Evolve: Extract microservices as needed

### For Existing Systems
1. Measure: Find actual bottlenecks
2. Quick wins: Add caching, indexes
3. Reliability: Add circuit breakers
4. Scale: Based on bottleneck type

### Pattern Priority
1. **Must Have**: Load balancing, Caching, Monitoring
2. **Should Have**: Circuit breaker, Queue, CDN
3. **Nice to Have**: Service mesh, Event sourcing
4. **Situational**: Sharding, CQRS, Saga

## 🚫 Anti-Pattern Warnings

### Common Anti-Patterns
| Anti-Pattern | Why It's Bad | Use Instead |
|--------------|--------------|-------------|
| Shared Database | Coupling, scaling limits | Service-specific DBs |
| Distributed Monolith | Complexity without benefits | True microservices |
| Chatty Services | Network overhead | Batch APIs, GraphQL |
| No Circuit Breaker | Cascading failures | Circuit breaker pattern |
| Sync Everything | Poor performance | Async where possible |
| No Monitoring | Blind to issues | Comprehensive observability |

### Pattern Overuse
- **Too Much Caching**: Stale data, complexity
- **Too Many Microservices**: Operational overhead
- **Premature Optimization**: Wasted effort
- **Over-engineering**: Unnecessary complexity

## 📈 Pattern Evolution Path

### Typical Evolution
```
1. Monolith
   ↓
2. Monolith + Cache + CDN
   ↓
3. Services + Load Balancer + Queue
   ↓
4. Microservices + API Gateway + Service Mesh
   ↓
5. Multi-region + Event-driven + Cell-based
```

### When to Evolve
- **Monolith → Services**: Team size > 10
- **Services → Microservices**: Clear bounded contexts
- **Single → Multi-region**: Global users
- **REST → Event-driven**: Complex workflows

## 🎯 Interview Tips

### Pattern Discussion Framework
1. **Problem**: What problem does it solve?
2. **Solution**: How does it work?
3. **Trade-offs**: What are pros/cons?
4. **Alternatives**: What else could we use?
5. **Example**: Real-world usage

### Red Flags to Avoid
- Using patterns without understanding why
- Not discussing trade-offs
- Over-complicating simple problems
- Ignoring operational aspects
- Missing failure scenarios