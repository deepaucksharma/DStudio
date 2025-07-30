---
title: Pattern Combination Recipes - Proven Architectural Stacks
description: Battle-tested pattern combinations used by Netflix, Uber, Amazon and other tech giants
icon: material/chef-hat
tags:
  - patterns
  - combinations
  - recipes
  - architecture
---

# Pattern Combination Recipes

Learn from proven pattern combinations that power the world's largest distributed systems.

## 🍳 Quick Recipe Finder

<div class="recipe-finder">
    <div class="recipe-categories">
        <button class="recipe-cat-btn active" onclick="filterRecipes('all')">🌐 All Recipes</button>
        <button class="recipe-cat-btn" onclick="filterRecipes('resilience')">🛡️ Resilience</button>
        <button class="recipe-cat-btn" onclick="filterRecipes('scale')">🚀 Scale</button>
        <button class="recipe-cat-btn" onclick="filterRecipes('realtime')">⚡ Real-time</button>
        <button class="recipe-cat-btn" onclick="filterRecipes('data')">💾 Data</button>
        <button class="recipe-cat-btn" onclick="filterRecipes('migration')">🔄 Migration</button>
    </div>
</div>

## 🏆 Battle-Tested Stacks

### The Netflix Resilience Stack
**Used for: 200M+ subscribers, 100B+ requests/day**

```mermaid
graph TB
    subgraph "Edge Layer"
        Z[Zuul API Gateway]
    end
    
    subgraph "Resilience Layer"
        H[Hystrix Circuit Breaker]
        R[Ribbon Load Balancer]
        E[Eureka Service Discovery]
    end
    
    subgraph "Data Layer"
        EV[EVCache]
        C[Cassandra]
    end
    
    subgraph "Streaming Layer"
        K[Kafka]
        F[Flink]
    end
    
    Z --> H
    H --> R
    R --> E
    H --> EV
    EV --> C
    K --> F
    
    style Z fill:#e74c3c
    style H fill:#3498db
    style K fill:#2ecc71
```

**Pattern Combination:**
1. 🌐 **API Gateway** (Zuul) - Single entry point
2. 🛡️ **Circuit Breaker** (Hystrix) - Prevent cascade failures
3. ⚖️ **Load Balancer** (Ribbon) - Distribute traffic
4. 🔍 **Service Discovery** (Eureka) - Dynamic routing
5. 📦 **Distributed Cache** (EVCache) - Reduce latency
6. 📨 **Event Streaming** (Kafka) - Async communication

**Key Success Factors:**
- Circuit breakers on all service calls
- Aggressive caching (90%+ cache hit rate)
- Graceful degradation for non-critical features
- Chaos engineering to test resilience

### The Uber Real-Time Stack
**Used for: 25M+ rides/day, sub-second dispatch**

```mermaid
graph LR
    subgraph "Mobile Layer"
        M[Mobile Apps]
    end
    
    subgraph "Real-time Layer"
        W[WebSocket Gateway]
        G[Geo-Sharding]
        P[Pub/Sub]
    end
    
    subgraph "Compute Layer"
        D[Dispatch Service]
        ML[ML Predictions]
    end
    
    subgraph "Storage Layer"
        S[Schemaless]
        R[Redis]
    end
    
    M --> W
    W --> P
    P --> G
    G --> D
    D --> ML
    D --> S
    P --> R
    
    style W fill:#f39c12
    style G fill:#9b59b6
    style ML fill:#1abc9c
```

**Pattern Combination:**
1. 🔌 **WebSocket** - Real-time bidirectional communication
2. 🌍 **Geo-Sharding** - Location-based partitioning
3. 📢 **Pub/Sub** - Event distribution
4. 🧩 **Cell-Based Architecture** - Isolated failure domains
5. 🎯 **Consistent Hashing** - Dynamic scaling
6. 📦 **In-Memory Cache** (Redis) - Ultra-low latency

**Key Success Factors:**
- Geo-sharding for locality
- WebSocket with fallback to polling
- Cell isolation prevents global failures
- Predictive scaling based on ML

### The Amazon E-Commerce Stack
**Used for: 300M+ customers, Prime Day scale**

```mermaid
graph TB
    subgraph "Frontend"
        CF[CloudFront CDN]
        AG[API Gateway]
    end
    
    subgraph "Compute"
        L[Lambda Functions]
        EC2[Auto-scaling EC2]
    end
    
    subgraph "Storage"
        D[DynamoDB]
        S3[S3 Object Store]
    end
    
    subgraph "Messaging"
        SQS[SQS Queues]
        K[Kinesis Streams]
    end
    
    CF --> AG
    AG --> L
    AG --> EC2
    L --> D
    EC2 --> D
    L --> SQS
    SQS --> K
    D --> S3
    
    style CF fill:#ff9800
    style D fill:#4caf50
    style SQS fill:#2196f3
```

**Pattern Combination:**
1. 🌐 **CDN** (CloudFront) - Global static content
2. 🚀 **Auto-scaling** - Handle traffic spikes
3. 📦 **NoSQL** (DynamoDB) - Unlimited scale
4. 📨 **Message Queue** (SQS) - Decouple services
5. 🌊 **Stream Processing** (Kinesis) - Real-time analytics
6. ☁️ **Serverless** (Lambda) - Event-driven compute

## 📖 Recipe Categories

### 🛡️ Resilience Recipes

#### Recipe: "The Unbreakable Service"
**Problem**: Service with 99.99% uptime requirement

```yaml
Ingredients:
  - Circuit Breaker (prevent cascades)
  - Retry with Exponential Backoff (handle transients)
  - Timeout (bound operations)
  - Bulkhead (isolate failures)
  - Health Check (detect issues)
  - Graceful Degradation (fallback behavior)

Instructions:
  1. Wrap all external calls with Circuit Breaker
  2. Add Retry inside Circuit Breaker (3 attempts max)
  3. Set Timeouts: 1s for critical, 5s for normal
  4. Use Bulkhead to isolate thread pools
  5. Implement Health Checks at /health endpoint
  6. Define degraded behavior for each feature

Serves: 10M+ requests/day with <50ms p99 latency
```

#### Recipe: "Chaos-Ready Architecture"
**Problem**: System that survives any failure

```yaml
Ingredients:
  - Multi-region deployment
  - Cell-based architecture
  - Chaos engineering tools
  - Comprehensive monitoring
  - Automated failover

Instructions:
  1. Deploy across 3+ regions
  2. Implement cell isolation (100 cells max)
  3. Run chaos experiments weekly
  4. Monitor all golden signals
  5. Automate failover (<30s RTO)

Serves: Netflix-scale resilience
```

### 🚀 Scale Recipes

#### Recipe: "0 to 1M Users"
**Problem**: Rapid growth from startup to scale

```yaml
Phase 1 (0-10K users):
  - Load Balancer + 2 servers
  - Basic caching (Redis)
  - CDN for static assets
  - Simple monitoring

Phase 2 (10K-100K users):
  - Auto-scaling groups
  - Read replicas for database
  - API Gateway
  - Distributed caching

Phase 3 (100K-1M users):
  - Microservices architecture
  - Message queues for async
  - Database sharding
  - Multi-region deployment

Time: 6-12 months per phase
```

#### Recipe: "Infinite Scale"
**Problem**: Google/Facebook scale architecture

```yaml
Ingredients:
  - Geo-distributed architecture
  - Custom protocols (not HTTP)
  - Purpose-built databases
  - Edge computing nodes
  - ML-driven optimization

Instructions:
  1. Build custom RPC framework
  2. Implement geo-replication
  3. Deploy edge nodes globally
  4. Use ML for traffic prediction
  5. Optimize down to microseconds

Serves: 1B+ users globally
```

### ⚡ Real-Time Recipes

#### Recipe: "Sub-Second Latency"
**Problem**: Real-time trading/gaming platform

```yaml
Ingredients:
  - WebSocket connections
  - In-memory data grids
  - Event sourcing
  - CQRS read models
  - Edge computing

Instructions:
  1. Establish WebSocket with fallback
  2. Keep hot data in memory
  3. Use event sourcing for writes
  4. Pre-compute read models
  5. Deploy compute to edge

Latency: <100ms globally
```

### 💾 Data Consistency Recipes

#### Recipe: "Eventually Consistent E-Commerce"
**Problem**: Shopping cart across devices

```yaml
Ingredients:
  - Event sourcing (cart events)
  - CQRS (separate read/write)
  - Saga (order processing)
  - CDC (inventory sync)
  - Conflict resolution (CRDTs)

Instructions:
  1. Model cart as event stream
  2. Build materialized views per device
  3. Use Saga for checkout flow
  4. Sync inventory via CDC
  5. Resolve conflicts with LWW-CRDT

Consistency: ~1 second globally
```

### 🔄 Migration Recipes

#### Recipe: "Monolith to Microservices"
**Problem**: Breaking down a large monolith

```yaml
Week 1-2: Foundation
  - Add API Gateway in front
  - Implement service discovery
  - Set up message queue

Week 3-8: Extraction
  - Use Strangler Fig pattern
  - Extract auth service first
  - Then user service
  - Database per service

Week 9-12: Optimization
  - Add circuit breakers
  - Implement caching
  - Set up monitoring

Risk: Low with gradual approach
```

## 🎯 Anti-Recipes (What NOT to Do)

### ❌ The "Everything Everywhere" Anti-Pattern
```yaml
Bad Ingredients:
  - Every pattern in the book
  - No clear architecture
  - Premature optimization
  - Resume-driven development

Result: Unmaintainable complexity
```

### ❌ The "Distributed Monolith"
```yaml
Bad Ingredients:
  - Microservices sharing databases
  - Synchronous everything
  - No service boundaries
  - Chatty interfaces

Result: Worst of both worlds
```

## 🔧 Implementation Guide

### How to Apply a Recipe

1. **Assess Current State**
   - What patterns do you have?
   - What problems are you solving?
   - What's your scale?

2. **Choose Recipe**
   - Match your problem
   - Consider your scale
   - Check prerequisites

3. **Implement Gradually**
   - Start with foundation
   - Add patterns incrementally
   - Measure impact

4. **Customize**
   - Adapt to your context
   - Remove unnecessary parts
   - Add missing pieces

## 📊 Success Metrics

### How to Know Your Recipe Works

| Metric | Good | Great | Elite |
|--------|------|-------|-------|
| Availability | 99.9% | 99.99% | 99.999% |
| Latency (p99) | <1s | <200ms | <50ms |
| Error Rate | <1% | <0.1% | <0.01% |
| Deploy Frequency | Weekly | Daily | Hourly |
| MTTR | <1hr | <15min | <5min |

## 🌟 Recipe Maturity Model

```mermaid
graph LR
    subgraph "Level 1: Basic"
        L1[Load Balancer<br/>+ Monitoring]
    end
    
    subgraph "Level 2: Resilient"
        L2[+ Circuit Breaker<br/>+ Retry]
    end
    
    subgraph "Level 3: Scalable"
        L3[+ Auto-scaling<br/>+ Caching]
    end
    
    subgraph "Level 4: Distributed"
        L4[+ Microservices<br/>+ Messaging]
    end
    
    subgraph "Level 5: Elite"
        L5[+ Multi-region<br/>+ Chaos Engineering]
    end
    
    L1 --> L2 --> L3 --> L4 --> L5
    
    style L1 fill:#3498db
    style L5 fill:#e74c3c
```

---

*These recipes are extracted from real production systems. Adapt them to your specific needs, and remember: start simple, evolve gradually.*
