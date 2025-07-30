---
title: Pattern Selection Cheatsheet
description: Quick reference guide for choosing the right distributed systems patterns
icon: material/clipboard-check
tags:
  - cheatsheet
  - patterns
  - selection-guide
---

# Pattern Selection Cheatsheet

Quick reference for choosing the right distributed systems patterns based on your specific challenges.

## 🎯 By Problem Domain

### Communication Challenges

| Problem | Gold Pattern | Why Use It | Alternative |
|---------|-------------|------------|-------------|
| Multiple microservices need unified interface | **API Gateway** | Single entry point, cross-cutting concerns | Direct service calls |
| Services need reliable messaging | **Message Queue** | Async communication, decoupling | Direct HTTP calls |
| Real-time bidirectional communication | **WebSocket** | Low latency, persistent connections | HTTP polling |
| Service discovery and routing | **Service Mesh** | Traffic management, observability | Load balancer |

### Resilience Challenges

| Problem | Gold Pattern | Why Use It | Alternative |
|---------|-------------|------------|-------------|
| Prevent cascade failures | **Circuit Breaker** | Fast failure, automatic recovery | Simple timeout |
| Handle transient failures | **Retry with Backoff** | Automatic recovery from glitches | No retry |
| Isolate failure domains | **Bulkhead** | Contain failures, resource isolation | Shared resources |
| Graceful service degradation | **Graceful Degradation** | Maintain core functionality | All-or-nothing |

### Scaling Challenges  

| Problem | Gold Pattern | Why Use It | Alternative |
|---------|-------------|------------|-------------|
| Distribute load across servers | **Load Balancing** | High availability, optimal utilization | Single server |
| Handle traffic spikes | **Auto-scaling** | Dynamic resource allocation | Fixed capacity |
| Reduce backend load | **Caching** | Faster responses, cost reduction | Always hit backend |
| Control request rates | **Rate Limiting** | Protect resources, fair usage | No limits |

### Data Management Challenges

| Problem | Gold Pattern | Why Use It | Alternative |
|---------|-------------|------------|-------------|
| Audit trail and compliance | **Event Sourcing** | Complete history, time travel | Change logs |
| Optimize reads and writes | **CQRS** | Independent scaling, multiple views | Single model |
| Distributed transactions | **Saga** | Eventual consistency, compensation | Two-phase commit |
| Data consistency across services | **CDC** | Real-time sync, minimal impact | Batch sync |

## 🏆 By Excellence Tier

### 🥇 Start Here (Gold Patterns)
**Battle-tested at massive scale - use these first**

#### Resilience (Must-Have)
- **Circuit Breaker**: Prevent cascade failures
- **Retry with Backoff**: Handle transient failures  
- **Health Check**: Monitor service health
- **Timeout**: Bound response times

#### Communication (Core Infrastructure)
- **API Gateway**: Unified service interface
- **Load Balancing**: Distribute traffic
- **Message Queue**: Async communication
- **Service Discovery**: Find services dynamically

#### Scaling (Growth Ready)
- **Caching**: Reduce latency and load
- **Auto-scaling**: Handle traffic spikes
- **CDN**: Global content delivery
- **Sharding**: Scale data horizontally

### 🥈 Domain-Specific (Silver Patterns)
**Use when Gold patterns don't fit your specific needs**

#### Advanced Data
- **CQRS**: Complex read/write optimization
- **Event Sourcing**: Complete audit trails
- **Materialized Views**: Fast complex queries
- **CDC**: Real-time data synchronization

#### Coordination
- **Saga**: Distributed transactions
- **Leader Election**: Consensus in clusters
- **Distributed Lock**: Coordinate access
- **Consensus**: Agreement in distributed systems

### 🥉 Avoid These (Bronze Patterns)
**Legacy patterns with better alternatives**

- **Two-Phase Commit** → Use Saga instead
- **Shared Database** → Use service per database
- **Synchronous Replication** → Use async patterns

## 🚀 By System Maturity

### Startup/MVP (< 10K users)
**Keep it simple, focus on features**

1. **Load Balancer** - Basic high availability
2. **Health Check** - Know when things break  
3. **Retry** - Handle network glitches
4. **Caching** - Basic performance boost

### Growth Stage (10K - 1M users)
**Add resilience and scalability**

5. **Circuit Breaker** - Prevent cascade failures
6. **API Gateway** - Unified service interface
7. **Auto-scaling** - Handle traffic growth
8. **Message Queue** - Decouple services

### Scale Stage (1M+ users)
**Advanced patterns for complex systems**

9. **Service Mesh** - Advanced traffic management
10. **Event Sourcing** - Audit and compliance
11. **CQRS** - Optimize reads and writes
12. **Saga** - Distributed transactions

## ⚡ Quick Decision Trees

### "My service keeps going down"
```
Service failing frequently?
├─ YES → External dependencies?
│   ├─ YES → Circuit Breaker + Fallback
│   └─ NO → Health Check + Auto-restart
└─ NO → Single point of failure?
    ├─ YES → Load Balancer + Redundancy
    └─ NO → Monitor and alerting
```

### "My system is too slow"
```
Performance issues?
├─ Database slow?
│   ├─ YES → Caching + Read Replicas
│   └─ NO → CDN + Load Balancer
└─ Complex queries?
    ├─ YES → CQRS + Materialized Views
    └─ NO → Profiling + Optimization
```

### "I need to scale"
```
Scaling challenges?
├─ Traffic spikes?
│   ├─ YES → Load Balancer + Auto-scaling
│   └─ NO → Horizontal scaling
└─ Data growth?
    ├─ YES → Sharding + CDC
    └─ NO → Caching + Optimization
```

## 📊 Pattern Combinations

### High Availability Stack
1. **Load Balancer** - Distribute traffic
2. **Circuit Breaker** - Handle failures
3. **Health Check** - Monitor status
4. **Auto-scaling** - Handle load

### Microservices Foundation
1. **API Gateway** - Single entry point
2. **Service Discovery** - Find services
3. **Circuit Breaker** - Resilience
4. **Message Queue** - Async communication

### Event-Driven Architecture
1. **Event Sourcing** - Capture all changes
2. **CQRS** - Separate read/write
3. **Saga** - Coordinate workflows
4. **CDC** - Sync data changes

## 🎭 By Use Case

### E-commerce Platform
**Essential patterns for online retail**

- **API Gateway** - Mobile/web interface
- **Circuit Breaker** - Payment reliability
- **Saga** - Order processing workflow
- **Event Sourcing** - Audit compliance
- **Caching** - Product catalog performance
- **Rate Limiting** - Prevent abuse

### Financial Services
**Patterns for banking and fintech**

- **Event Sourcing** - Regulatory compliance
- **Saga** - Transaction workflows
- **Circuit Breaker** - System reliability
- **Encryption** - Data protection
- **Audit Log** - Compliance tracking
- **Two-Person Rule** - Authorization

### Real-time Gaming  
**Patterns for low-latency systems**

- **WebSocket** - Real-time communication
- **Edge Computing** - Reduce latency
- **Load Balancing** - Handle player load
- **Circuit Breaker** - Service reliability
- **Caching** - Game state performance
- **Auto-scaling** - Handle events

### IoT Platform
**Patterns for device management**

- **Message Queue** - Device communication
- **Time Series DB** - Sensor data
- **Edge Computing** - Local processing
- **Circuit Breaker** - Device failures
- **Batch Processing** - Data analytics
- **Device Registry** - Device management

## ⚠️ Common Anti-Patterns

### What NOT to Do

❌ **Distributed Monolith**
- Using microservices but sharing databases
- **Fix**: Service per database pattern

❌ **Chatty Interfaces**
- Too many fine-grained API calls
- **Fix**: API Gateway with request aggregation

❌ **Shared Database Between Services**
- Multiple services accessing same DB
- **Fix**: Database per service + CDC

❌ **Synchronous Everything**
- All communication is blocking
- **Fix**: Message queues + async patterns

❌ **No Circuit Breakers**
- Direct calls to unreliable services
- **Fix**: Circuit breaker + fallbacks

## 📝 Implementation Priority

### Phase 1: Foundation (Week 1-2)
1. Load Balancer
2. Health Checks
3. Basic Retry Logic
4. Monitoring/Alerting

### Phase 2: Resilience (Week 3-4)
1. Circuit Breaker
2. Timeout Configuration
3. Graceful Degradation
4. Bulkhead Isolation

### Phase 3: Scalability (Week 5-8)
1. Auto-scaling
2. Caching Layer
3. CDN Integration
4. Database Optimization

### Phase 4: Advanced (Month 2-3)
1. Event Sourcing
2. CQRS Implementation
3. Saga Orchestration
4. Service Mesh

---

## 💾 Downloadable Resources

- **[Pattern Selection Matrix (PDF)](pattern-selection-matrix.pdf)** - Printable decision matrix
- **[Architecture Checklist (PDF)](architecture-checklist.pdf)** - Implementation checklist
- **[Troubleshooting Guide (PDF)](troubleshooting-guide.pdf)** - Common problems and solutions

---

*Use this cheatsheet to quickly identify the right patterns for your architecture challenges. For detailed implementation guides, visit the full pattern documentation.*