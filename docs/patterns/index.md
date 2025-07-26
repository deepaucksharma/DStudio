---
title: Distributed Systems Patterns
description: Curated catalog of ~95 battle-tested patterns for building distributed systems
type: patterns-index
---

# Distributed Systems Patterns

**~95 carefully curated patterns for building reliable, scalable distributed systems**

!!! info "Pattern Curation"
    We've curated the most valuable patterns for modern distributed systems, focusing on practical, battle-tested solutions. Each pattern has been selected for its real-world applicability and proven impact in production systems.

!!! tip "Quick Navigation"
    - **[By Problem Domain](#by-problem-domain)** - Organized by what you're building
    - **[By Challenge](#by-challenge)** - Find patterns for specific problems
    - **[Learning Paths](#learning-paths)** - Progressive learning tracks
    - **[Pattern Navigator](#pattern-navigator)** - Visual decision guide

## 📚 Prerequisites & Learning Path

<div class="grid cards" markdown>

- :material-clock-outline:{ .lg .middle } **Time Investment**
    
    ---
    
    **Total**: 40-60 hours  
    **Per Pattern**: 1-2 hours  
    **Difficulty**: 🟠 Advanced  
    **Prerequisites**: [7 Laws](part1-axioms) + [5 Pillars](part2-pillars)  

- :material-school-outline:{ .lg .middle } **What You'll Master**
    
    ---
    
    ✓ Production-ready solutions  
    ✓ Pattern selection criteria  
    ✓ Implementation trade-offs  
    ✓ Real-world optimizations  
    ✓ Debugging at scale  

- :material-map-marker-path:{ .lg .middle } **Your Journey So Far**
    
    ---
    
    **Completed**: ✅ Laws (Why)  
    **Completed**: ✅ Pillars (What)  
    **Current**: 🔵 Patterns (How)  
    **Next**: [→ Case Studies](case-studies) (Examples)  

- :material-target:{ .lg .middle } **Learning Goals**
    
    ---
    
    **Week 1-2**: Core patterns (5-10)  
    **Week 3-4**: Your domain patterns  
    **Week 5-6**: Advanced combinations  
    **Ongoing**: New patterns monthly  

</div>

## Pattern Navigator

```mermaid
graph TD
 Start["System Problem"] --> Scale{Scale?}
 
 Scale -->|"< 1K RPS"| Small[Small Scale]
 Scale -->|"1K-100K RPS"| Medium[Medium Scale]
 Scale -->|"> 100K RPS"| Large[Large Scale]
 
 Small --> S1{Issue Type?}
 S1 -->|Performance| SP["Caching<br/>CDN"]
 S1 -->|Reliability| SR["Circuit Breaker<br/>Retry"]
 S1 -->|Data| SD["Caching Strategies<br/>Materialized View"]
 
 Medium --> M1{Issue Type?}
 M1 -->|Performance| MP["Sharding<br/>Load Balancing<br/>Auto-scaling"]
 M1 -->|Reliability| MR["Circuit Breaker<br/>Bulkhead<br/>Rate Limiting"]
 M1 -->|Data| MD["CQRS<br/>Event Sourcing<br/>CDC"]
 
 Large --> L1{Issue Type?}
 L1 -->|Performance| LP["Edge Computing<br/>Geo-Replication<br/>Service Mesh"]
 L1 -->|Reliability| LR["Chaos Engineering<br/>Multi-Region<br/>Cell-Based"]
 L1 -->|Data| LD["Event Streaming<br/>Data Mesh<br/>Federated GraphQL"]
 
 style Start fill:#5448C8,color:#fff
 style SP fill:#e1f5fe
 style SR fill:#fee2e2
 style SD fill:#fff3e0
 style MP fill:#e1f5fe
 style MR fill:#fee2e2
 style MD fill:#fff3e0
 style LP fill:#e1f5fe
 style LR fill:#fee2e2
 style LD fill:#fff3e0
```

## 🚨 Pattern Emergency Room

!!! danger "System on Fire? Start Here!"

| Problem | Symptoms | Immediate Fix | Long-term Solution | Time to Relief |
|---------|----------|---------------|-------------------|----------------|
| **🔥 High Latency** | P99 > 1s, users complaining | Add Redis cache | CDN → Edge computing | 2 hours |
| **💥 Cascade Failures** | One service takes down 5 others | Deploy circuit breakers | Bulkhead isolation | 4 hours |
| **📈 Can't Scale** | CPU 100%, OOM errors | Vertical scaling | Sharding strategy | 1 day |
| **🔄 Data Conflicts** | Lost orders, wrong inventory | Add distributed locks | CQRS + Event Sourcing | 1 week |
| **🕸️ Complex Workflows** | Failed transactions, partial state | Add saga orchestrator | Event choreography | 2 weeks |
| **🕵️ Debugging Nightmare** | Can't trace errors | Add correlation IDs | Full observability stack | 3 days |


## Pattern ROI Calculator

| Pattern | Investment | Payback Period | 5-Year ROI | Real Example |
|---------|------------|----------------|------------|---------------|
| **Caching** | $10K (Redis cluster) | 2 months | 2,400% | Netflix: 90% cost reduction |
| **Circuit Breaker** | $5K (implementation) | 1 outage prevented | 5,000% | Amazon: $1M/hour downtime prevented |
| **CQRS** | $50K (refactoring) | 6 months | 800% | Uber: 10x read scaling |
| **Event Sourcing** | $100K (migration) | 1 year | 500% | PayPal: Complete audit trail |
| **Service Mesh** | $200K (Istio setup) | 8 months | 600% | Google: 50% ops reduction |
| **Sharding** | $150K (re-architecture) | 1 year | 1,000% | Discord: 100x growth enabled |


## Pattern Selection by Constraints

| If You Have... | Avoid These | Use These Instead | Why |
|----------------|-------------|-------------------|-----|
| < 3 engineers | Service Mesh, K8s | Monolith + CDN | Operational overhead |
| < $1K/month budget | Multi-region, Kafka | Single region + Redis | Cost efficiency |
| < 100 req/s | Microservices | Monolith | Premature optimization |
| Strict consistency | Eventual consistency patterns | 2PC, Distributed locks | Data integrity |
| < 1GB data | Sharding, NoSQL | PostgreSQL | Unnecessary complexity |


## Pattern Maturity & Adoption

```mermaid
graph LR
 subgraph "Emerging"
 E1[Data Mesh]
 E2[Cell-Based]
 E3[eBPF Observability]
 end
 
 subgraph "Growing"
 G1[Service Mesh]
 G2[Event Streaming]
 G3[GraphQL Federation]
 end
 
 subgraph "Mature"
 M1[Load Balancing]
 M2[Caching]
 M3[Circuit Breaker]
 end
 
 subgraph "Essential"
 ES1[Timeout]
 ES2[Health Check]
 ES3[Retry]
 end
 
 E1 --> G1 --> M1 --> ES1
 
 style E1 fill:#fef3c7
 style G1 fill:#dbeafe
 style M1 fill:#d1fae5
 style ES1 fill:#e0e7ff
```

## Pattern Stack by Growth Stage

### 🚀 Your Current Stage → Required Patterns

```mermaid
graph LR
    subgraph "Startup (0-1K users)"
        S1[Monolith]
        S2[PostgreSQL]
        S3[Redis Cache]
        S4[CDN]
    end
    
    subgraph "Growth (1K-100K users)"
        G1[Load Balancer]
        G2[Read Replicas]
        G3[Message Queue]
        G4[Circuit Breaker]
    end
    
    subgraph "Scale (100K-1M users)"
        SC1[Microservices]
        SC2[CQRS]
        SC3[Service Mesh]
        SC4[Multi-Region]
    end
    
    subgraph "Unicorn (1M+ users)"
        U1[Edge Computing]
        U2[Cell Architecture]
        U3[Chaos Engineering]
        U4[Custom Hardware]
    end
    
    S4 --> G1
    G4 --> SC1
    SC4 --> U1
    
    style S1 fill:#e8f5e9
    style G1 fill:#c3e9fd
    style SC1 fill:#fff3b8
    style U1 fill:#ffcdd2
```


## Pattern Categories

<div class="grid cards" markdown>

- :material-city:{ .lg .middle } **Core Patterns**

 ---

 **Complexity**: Medium-High 
 **Prerequisites**: Basic distributed systems 
 **Start with**: Queues & Streaming 
 **ROI Timeline**: 2-4 weeks

- :material-shield-check:{ .lg .middle } **Resilience Patterns**

 ---

 **Complexity**: Low-Medium 
 **Prerequisites**: Production experience 
 **Start with**: Circuit Breaker 
 **ROI Timeline**: 1-2 weeks

- :material-database:{ .lg .middle } **Data Patterns**

 ---

 **Complexity**: High 
 **Prerequisites**: Database fundamentals 
 **Start with**: Caching Strategies 
 **ROI Timeline**: 3-6 weeks

- :material-handshake:{ .lg .middle } **Coordination Patterns**

 ---

 **Complexity**: High 
 **Prerequisites**: Consensus algorithms 
 **Start with**: Leader Election 
 **ROI Timeline**: 4-8 weeks

- :material-cog:{ .lg .middle } **Operational Patterns**

 ---

 **Complexity**: Medium 
 **Prerequisites**: DevOps basics 
 **Start with**: Observability 
 **ROI Timeline**: 2-3 weeks

</div>

### Pattern Catalog

| Pattern | Category | Problem Solved | When to Use | Complexity | Link |
|---------|----------|----------------|-------------|------------|------|
| **Queues & Streaming** | 🏗️ Core | Coupling, backpressure | Async processing, > 1K msg/s | 🟡 Medium | [📬](queues-streaming.md) |
| **CQRS** | 🏗️ Core | Read/write scaling | 10:1 read ratio | 🔴 High | [🔀](cqrs.md) |
| **Event-Driven** | 🏗️ Core | Service coupling | > 5 services | 🟡 Medium | [⚡](event-driven.md) |
| **Event Sourcing** | 🏗️ Core | Audit trail | Compliance required | 🔴 High | [📜](event-sourcing.md) |
| **Saga** | 🏗️ Core | Distributed transactions | Multi-service workflows | 🔴 High | [🎭](saga.md) |
| **Service Mesh** | 🏗️ Core | Service communication | > 20 services | 🔴 High | [🕸️](service-mesh.md) |
| **Serverless/FaaS** | 🏗️ Core | Variable load | Sporadic traffic | 🟡 Medium | [λ](serverless-faas.md) |
| **Circuit Breaker** | 🛡️ Resilience | Cascade failures | External dependencies | 🟢 Low | [⚡](circuit-breaker.md) |
| **Retry & Backoff** | 🛡️ Resilience | Transient failures | Network calls | 🟢 Low | [🔄](retry-backoff.md) |
| **Bulkhead** | 🛡️ Resilience | Resource isolation | Multi-tenant | 🟡 Medium | [🚪](bulkhead.md) |
| **Rate Limiting** | 🛡️ Resilience | Overload | Public APIs | 🟡 Medium | [🚦](rate-limiting.md) |
| **CDC** | 💾 Data | Data sync | Real-time replication | 🔴 High | [🔄](cdc.md) |
| **Sharding** | 💾 Data | Data scale | > 1TB or > 10K TPS | 🔴 High | [🔪](sharding.md) |
| **Caching** | 💾 Data | Latency | Read-heavy load | 🟢 Low | [💾](caching-strategies.md) |
| **Request Batching** | 💾 Data | Overhead amortization | High frequency ops | 🟡 Medium | [📦](request-batching.md) |
| **Leader Election** | 🤝 Coordination | Single writer | Consensus needed | 🔴 High | [👑](leader-election.md) |
| **Distributed Lock** | 🤝 Coordination | Mutual exclusion | Critical sections | 🔴 High | [🔒](distributed-lock.md) |
| **State Watch** | 🤝 Coordination | Change notification | Real-time state updates | 🔴 High | [👁️](state-watch.md) |
| **Observability** | ⚙️ Operational | Visibility | Production systems | 🟡 Medium | [👁️](observability.md) |
| **Auto-scaling** | ⚙️ Operational | Variable load | Cloud deployments | 🟡 Medium | [📈](auto-scaling.md) |
| **Load Balancing** | ⚙️ Operational | Request distribution | > 1 server | 🟢 Low | [⚖️](load-balancing.md) |


### Pattern Combinations That Work

```mermaid
graph LR
 subgraph "Starter Pack"
 S1[Load Balancer]
 S2[Health Check]
 S3[Timeout]
 S1 --> S2 --> S3
 end
 
 subgraph "Reliability Pack"
 R1[Circuit Breaker]
 R2[Retry + Backoff]
 R3[Bulkhead]
 R1 --> R2 --> R3
 end
 
 subgraph "Data Pack"
 D1[CQRS]
 D2[Event Sourcing]
 D3[Saga]
 D1 --> D2 --> D3
 end
 
 subgraph "Scale Pack"
 SC1[Sharding]
 SC2[Caching]
 SC3[CDN]
 SC1 --> SC2 --> SC3
 end
 
 style S1 fill:#e0f2fe
 style R1 fill:#fee2e2
 style D1 fill:#fef3c7
 style SC1 fill:#dcfce7
```

## 🏢 Real-World Pattern Impact

| Company | Pattern | Scale | Result | Key Metric |
|---------|---------|-------|--------|------------|
| **Netflix** | Circuit Breaker | 100B req/day | Prevented cascades | 99.99% uptime |
| **LinkedIn** | CQRS | 1B reads/day | 10x performance | < 50ms p99 |
| **Walmart** | Event Sourcing | 100M orders/day | Audit trail | 0 lost orders |
| **Lyft** | Service Mesh | 100M req/sec | Observability | < 1ms overhead |
| **Uber** | Geo-sharding | 20M rides/day | Regional scale | 5x capacity |
| **Stripe** | Idempotency | $640B/year | Payment safety | 100% accuracy |


## 🎯 Structured Learning Paths

### Choose Your Path Based on Experience & Goals

<div class="grid cards" markdown>

- :material-numeric-1-circle:{ .lg .middle } **Foundation Path (Weeks 1-2)**
    
    ---
    
    **For**: Everyone starts here  
    **Patterns**: Essential reliability  
    
    **Week 1 - Basic Resilience**:
    1. [Retry & Backoff](retry-backoff.md) - Handle transients
    2. [Circuit Breaker](circuit-breaker.md) - Prevent cascades
    3. [Rate Limiting](rate-limiting.md) - Protect resources
    4. [Bulkhead](bulkhead.md) - Isolate failures
    
    **Week 2 - Performance**:
    5. [Caching](caching-strategies.md) - Speed up reads
    6. [Load Balancing](load-balancing.md) - Distribute work
    7. [Rate Limiting](rate-limiting.md) - Protect resources

- :material-numeric-2-circle:{ .lg .middle } **Scale Path (Weeks 3-4)**
    
    ---
    
    **For**: Growing systems  
    **Patterns**: Handle 10x-100x growth  
    
    **Week 3 - Data Scale**:
    1. [Sharding](sharding.md) - Partition data
    2. [CQRS](cqrs.md) - Separate concerns
    3. [Event Sourcing](event-sourcing.md) - Event log
    
    **Week 4 - Service Scale**:
    4. [Service Mesh](service-mesh.md) - Manage services
    5. [API Gateway](api-gateway.md) - Single entry
    6. [Auto-scaling](auto-scaling.md) - Dynamic capacity

- :material-numeric-3-circle:{ .lg .middle } **Advanced Path (Weeks 5-6)**
    
    ---
    
    **For**: Complex systems  
    **Patterns**: Enterprise scale  
    
    **Week 5 - Coordination**:
    1. [Saga](saga.md) - Distributed workflows
    2. [Leader Election](leader-election.md) - Single writer
    3. [Distributed Lock](distributed-lock.md) - Mutual exclusion
    
    **Week 6 - Global Scale**:
    4. [Multi-Region](multi-region.md) - Geographic distribution
    5. [Edge Computing](edge-computing.md) - Process at edge
    6. [Cell Architecture](cell-based.md) - Blast radius control

- :material-star:{ .lg .middle } **Specialization Paths**
    
    ---
    
    **Choose based on your domain**:
    
    **📦 E-commerce Track**:
    - Saga (payments)
    - Inventory management
    - Cart synchronization
    
    **📱 Real-time Track**:
    - WebSocket patterns
    - Event streaming
    - Push notifications
    
    **📊 Analytics Track**:
    - Lambda architecture
    - Stream processing
    - Time-series optimization

</div>

### 📈 Learning Progression Timeline

```mermaid
gantt
    title Pattern Learning Journey (6 Weeks)
    dateFormat YYYY-MM-DD
    
    section Foundation
    Resilience Patterns     :found1, 2024-01-01, 7d
    Performance Patterns    :found2, after found1, 7d
    
    section Scale
    Data Patterns          :scale1, after found2, 7d
    Service Patterns       :scale2, after scale1, 7d
    
    section Advanced
    Coordination Patterns  :adv1, after scale2, 7d
    Global Patterns       :adv2, after adv1, 7d
    
    section Practice
    Build Projects        :crit, 2024-01-08, 35d
    
    style found1 fill:#e0f2fe
    style scale1 fill:#fef3c7
    style adv1 fill:#fee2e2
```

## ⚠ Anti-Patterns to Avoid

| Anti-Pattern | Red Flag | Cost | Fix |
|--------------|-----------|------|-----|
| **Cargo Cult** | "Netflix does it" | 10x complexity | Start simple |
| **Premature Distribution** | < 100 req/s microservices | 20x overhead | Monolith first |
| **Consistency Theater** | Strong consistency for likes | 100x slower | Use eventual |
| **Resume-Driven** | K8s for 3 services | $10K/month | Right-size |
| **Infinite Scale** | No capacity plan | $100K surprise | Model growth |


## Pattern Success Metrics

| Pattern | Metric | 🟢 Good | 🟡 Great | 🔴 Elite |
|---------|--------|---------|----------|----------|
| **Circuit Breaker** | Cascades prevented/month | 10 | 100 | 1000+ |
| **Caching** | Hit ratio | 60% | 80% | 95%+ |
| **Load Balancing** | Distribution variance | < 20% | < 10% | < 5% |
| **Auto-scaling** | Response during spike | < 2x | < 1.5x | < 1.1x |
| **CQRS** | Read/write ratio | 10:1 | 100:1 | 1000:1 |


## Implementation Checklist

| Step | Question | Action | Common Mistake |
|------|----------|--------|----------------|
| 1️⃣ | Problem? | Write it down | Solution seeking problem |
| 2️⃣ | Scale? | Measure | Over-engineering |
| 3️⃣ | Team skills? | Assess honestly | Underestimating complexity |
| 4️⃣ | Total cost? | Include ops | Ignoring human cost |
| 5️⃣ | Rollback? | Test it | No escape route |


## 🔗 Navigation

### Pattern Resources
| Resource | Purpose | Time |
|----------|---------|------|
| [🎮 Pattern Selector Tool](pattern-selector-tool.md) | Interactive decision helper | 5 min |
| [📊 Pattern Navigator](#pattern-navigator) | Visual decision guide | 3 min |


### Patterns by Problem Domain
| Domain | Key Patterns | Start With |
|--------|--------------|------------|
| **🔴 Reliability** | Circuit Breaker, Bulkhead, Retry | [Circuit Breaker](circuit-breaker.md) |
| **⚡ Performance** | Caching, CDN, Edge Computing | [Caching](caching-strategies.md) |
| **📈 Scalability** | Sharding, Load Balancing, Auto-scaling | [Load Balancing](load-balancing.md) |
| **💾 Data** | CQRS, Event Sourcing, CDC | [CQRS](cqrs.md) |
| **🤝 Coordination** | Saga, Leader Election, Distributed Lock | [Saga](saga.md) |


### Case Studies
- [Netflix](case-studies/netflix-chaos) → Circuit Breaker, Chaos Engineering
- [Uber](case-studies/uber-location) → Edge Computing, Geo-sharding
- [Amazon](case-studies/amazon-dynamo) → Tunable Consistency, Sharding
- [PayPal](case-studies/paypal-payments) → Saga Pattern, Idempotency

## 📖 References

Key Papers & Resources:
- [CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf) - Young, 2010
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) - Fowler, 2005
- [Sagas](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf) - Garcia-Molina & Salem, 1987
- [Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Nygard, 2007
- [Dynamo Paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) - DeCandia et al., 2007
- [Raft Consensus](https://raft.github.io/raft.pdf) - Ongaro & Ousterhout, 2014

---

## 🎓 Next Steps: Apply Your Knowledge

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } **Start Building**
    
    ---
    
    **Mini Projects**:
    ✓ Build a circuit breaker library
    ✓ Implement distributed cache
    ✓ Create a load balancer
    ✓ Design a saga orchestrator
    
    [🛠️ Project Ideas](examples/)

- :material-certificate:{ .lg .middle } **Test Your Skills**
    
    ---
    
    **Knowledge Checks**:
    ✓ Pattern selection quiz
    ✓ Trade-off analysis
    ✓ Architecture review
    ✓ Debugging scenarios
    
    [🧑‍🎓 Test Your Knowledge](#progress-tracker)

- :material-account-group:{ .lg .middle } **Learn Together**
    
    ---
    
    **Community**:
    ✓ Pattern discussions
    ✓ Implementation help
    ✓ Code reviews
    ✓ War stories
    
    [👥 Join Community](https://github.com/deepaucksharma/DStudio/discussions)

- :material-trending-up:{ .lg .middle } **Level Up**
    
    ---
    
    **Advanced Topics**:
    ✓ Pattern combinations
    ✓ Performance tuning
    ✓ Failure analysis
    ✓ Cost optimization
    
    [📈 Advanced Patterns](#advanced-path-weeks-5-6)

</div>

### 📊 Progress Tracker

!!! info "Track Your Pattern Mastery"
    **Foundation Patterns** (Complete First):
    - [ ] Retry & Backoff - Transient failure recovery  
    - [ ] Circuit Breaker - Cascade prevention
    - [ ] Rate Limiting - Resource protection
    - [ ] Caching - Performance boost
    - [ ] Load Balancing - Work distribution
    - [ ] Observability - System monitoring
    
    **Scale Patterns** (After Foundation):
    - [ ] Sharding - Data partitioning
    - [ ] CQRS - Read/write separation
    - [ ] Service Mesh - Service management
    - [ ] Auto-scaling - Dynamic capacity
    
    **Advanced Patterns** (After Scale):
    - [ ] Saga - Distributed transactions
    - [ ] Event Sourcing - Event-driven design
    - [ ] Multi-Region - Geographic distribution
    - [ ] Cell Architecture - Blast radius control

*"The best pattern is often no pattern—until you need it."*

---

<div class="page-nav" markdown>
[:material-arrow-left: Part II - The 5 Pillars](part2-pillars) | 
[:material-arrow-up: Home](/) | 
[:material-arrow-right: Pattern Selector Tool](patterns/pattern-selector-tool)
</div>