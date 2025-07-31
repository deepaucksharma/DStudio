---
title: Event-Driven Architecture
category: architecture
excellence_tier: silver
pattern_status: recommended
description: Architectural pattern where components communicate through events, enabling
  loose coupling and scalability
introduced: 2024-01
current_relevance: mainstream
trade-offs:
  pros: []
  cons: []
best-for: []
---




# Event-Driven Architecture

!!! success "🏆 Gold Standard Pattern"
    **Asynchronous Service Communication** • LinkedIn, Uber, Netflix proven
    
    The foundation for building scalable, loosely-coupled systems. Event-driven architecture enables services to react to changes without direct dependencies, processing trillions of events daily at scale.
    
    **Key Success Metrics:**
    - LinkedIn Kafka: 7 trillion messages/day with millisecond latency
    - Uber Events: 25B+ events/day coordinating global rides
    - Netflix Streaming: 500B+ events/day driving personalization

## Essential Questions

**1. Do multiple services need to react to the same business changes?**
- YES → Event-driven enables publish once, consume many
- NO → Direct API calls may be simpler

**2. Can your operations tolerate eventual consistency?**
- YES → Events provide natural decoupling
- NO → Synchronous patterns required

**3. Do you need an audit trail of all changes?**
- YES → Event sourcing provides complete history
- NO → Traditional state storage sufficient

---

## When to Use / When NOT to Use

### ✅ Use Event-Driven When

| Scenario | Why It Works | Example |
|----------|--------------|---------||
| **Multiple consumers** | One event → many reactions | Order placed → inventory, payment, email, analytics |
| **Temporal decoupling** | Producer/consumer work at different speeds | Batch processing, async workflows |
| **Loose coupling required** | Services evolve independently | Microservices communication |
| **Audit requirements** | Natural event log | Financial transactions, compliance |
| **Real-time streaming** | Continuous data flow | IoT sensors, live analytics |

### ❌ DON'T Use When

| Scenario | Why It Fails | Alternative |
|----------|--------------|-------------|
| **Immediate consistency** | Events are eventually consistent | Synchronous APIs, 2PC |
| **Simple request-response** | Overkill for basic queries | REST/GraphQL APIs |
| **< 5 services** | Complexity exceeds benefits | Direct service calls |
| **Ordered processing critical** | Global ordering expensive | Database transactions |
| **Team lacks experience** | Debugging async is hard | Start with simpler patterns |

## Level 1: Intuition

<div class="axiom-box">
<h4>⚛️ Law 2: Asynchronous Reality</h4>

Event-driven architecture embraces the fundamental truth that in distributed systems, everything is asynchronous. Rather than fighting this reality with synchronous calls that can fail or timeout, events let services communicate through time - a service can publish an event now and interested services can process it when they're ready.

**Key Insight**: Events naturally handle the speed-of-light problem in distributed systems - you can't wait for a response from a service on another continent, but you can tell it what happened.
</div>

### The News Broadcasting Analogy

```
Traditional (Request-Response):          Event-Driven:

📱 Phone Calls                          📻 Radio Broadcast
Person A → calls → Person B             Station → broadcasts → Many listeners
Person A → calls → Person C             
Person A → calls → Person D             Events flow to all interested parties
                                        
Problems:                               Benefits:
- A must know B, C, D exist            - Listeners tune in when ready
- Sequential, slow                      - Broadcaster doesn't know listeners
- If B is busy, A waits                - Parallel, fast
- Tight coupling                        - Loose coupling
```

```
Synchronous Architecture:               Event-Driven Architecture:

Order Service                          Order Service
    ↓                                      ↓
    ├→ Payment Service                [Order Placed Event]
    |     ↓                                ↓    ↓    ↓
    ├→ Inventory Service            Payment  Inventory  Email
    |     ↓                         Service  Service   Service
    └→ Email Service                (async)  (async)   (async)

Chain of dependencies                 Independent reactions
```

### Real-World Examples

| System | Events | Scale |
|--------|--------|-------|
| **Netflix** | Video started, paused, completed | 150B events/day |
| **Uber** | Trip requested, driver assigned, trip completed | 50M trips/day |
| **LinkedIn** | Post created, connection made, message sent | 1B+ events/day |
| **Spotify** | Song played, playlist created, artist followed | 100M+ users |


### Event Flow Visualization

```mermaid
sequenceDiagram
    participant OS as Order Service
    participant EB as Event Bus
    participant PS as Payment Service
    participant IS as Inventory Service
    participant ES as Email Service
    participant AS as Analytics Service
    
    OS->>EB: Publish(OrderPlaced)
    Note over EB: Event Router
    
    par Parallel Processing
        EB->>PS: OrderPlaced Event
        PS->>PS: Process Payment
        PS->>EB: Publish(PaymentCompleted)
    and
        EB->>IS: OrderPlaced Event
        IS->>IS: Reserve Inventory
        IS->>EB: Publish(InventoryReserved)
    and
        EB->>ES: OrderPlaced Event
        ES->>ES: Send Confirmation
    and
        EB->>AS: OrderPlaced Event
        AS->>AS: Update Metrics
    end
    
    Note over OS,AS: All handlers process independently
```

### Event-Driven Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Event Notification** | Simple "something happened" | User logged in |
| **Event-Carried State Transfer** | Full data in event | Order details in OrderPlaced |
| **Event Sourcing** | Events as source of truth | Audit trail, replay |
| **CQRS** | Separate read/write models | High-performance queries |
| **Saga** | Distributed transactions | Multi-service workflows |


### Architecture Comparison

```mermaid
graph TB
    subgraph "Traditional Request-Response"
        O1[Order Service] -->|API Call| P1[Payment Service]
        P1 -->|Response| O1
        O1 -->|API Call| I1[Inventory Service]
        I1 -->|Response| O1
        O1 -->|API Call| E1[Email Service]
        E1 -->|Response| O1
        
        Note1[Sequential, Blocking,<br/>Tightly Coupled]
    end
    
    subgraph "Event-Driven Architecture"
        O2[Order Service] -->|Publish Event| EB[Event Bus]
        EB -->|Async| P2[Payment Service]
        EB -->|Async| I2[Inventory Service]
        EB -->|Async| E2[Email Service]
        EB -->|Async| A2[Analytics Service]
        
        Note2[Parallel, Non-blocking,<br/>Loosely Coupled]
    end
    
    style EB fill:#818cf8,stroke:#6366f1,stroke-width:3px
    style Note1 fill:#fee2e2
    style Note2 fill:#dcfce7
```

### Event-Driven Decision Matrix

| Pattern | When to Use | Complexity | Consistency | Performance |
|---------|-------------|------------|-------------|-------------|
| **Event Notification** | Simple state changes | Low | Eventual | High |
| **Event-Carried State** | Reduce queries | Medium | Eventual | Very High |
| **Event Sourcing** | Audit requirements | High | Strong* | Medium |
| **CQRS** | Read/write separation | High | Eventual | Very High |
| **Saga** | Distributed transactions | Very High | Eventual | Medium |

*With proper implementation

---

## Level 2: Foundation

### Core Concepts

#### Event Types and Patterns

```mermaid
graph TD
    subgraph "Event Types"
        E1[Domain Events<br/>Business facts]
        E2[Integration Events<br/>Cross-service]
        E3[System Events<br/>Technical]
    end
    
    subgraph "Communication Patterns"
        P1[Event Notification<br/>Something happened]
        P2[Event-Carried State<br/>Here's the data]
        P3[Event Sourcing<br/>Events as truth]
    end
    
    subgraph "Delivery Guarantees"
        D1[At-most-once<br/>Fire and forget]
        D2[At-least-once<br/>May duplicate]
        D3[Exactly-once<br/>Complex]
    end
    
    E1 --> P1
    E2 --> P2
    E3 --> P3
    
    P1 --> D1
    P2 --> D2
    P3 --> D3
```

#### Event Design Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Immutability** | Events represent facts, never change | OrderPlaced can't be modified |
| **Self-Contained** | Include all necessary data | Don't force lookups |
| **Time-Ordered** | Clear temporal sequence | Use timestamps/versions |
| **Business-Focused** | Model domain concepts | OrderShipped not RecordUpdated |
| **Versioned** | Support schema evolution | Include version in metadata |


### Event Store Architecture

```mermaid
graph TB
    subgraph "Event Store Pattern"
        CMD[Command] --> AGG[Aggregate]
        AGG --> EVT[Events]
        EVT --> ES[(Event Store)]
        ES --> PROJ[Projections]
        PROJ --> READ[Read Models]
        
        ES --> REPLAY[Event Replay]
        REPLAY --> AGG
        
        subgraph "Event Stream"
            ES --> E1[Event 1: OrderCreated]
            E1 --> E2[Event 2: ItemAdded]
            E2 --> E3[Event 3: PaymentReceived]
            E3 --> E4[Event 4: OrderShipped]
        end
    end
    
    style ES fill:#bbf,stroke:#333,stroke-width:3px
    style AGG fill:#f9f,stroke:#333,stroke-width:2px
```

### Key Architecture Decisions

| Decision | Options | Trade-offs |
|----------|---------|------------|
| **Event Bus** | Kafka, RabbitMQ, AWS EventBridge | Throughput vs simplicity |
| **Serialization** | JSON, Avro, Protobuf | Readability vs performance |
| **Ordering** | Per-partition, Global, None | Consistency vs scalability |
| **Retention** | 7 days, 30 days, Forever | Cost vs replay capability |
| **Delivery** | At-least-once, At-most-once | Duplicates vs data loss |

### Event Processing Patterns

```mermaid
graph LR
    subgraph "Delivery Guarantees"
        AM[At-Most-Once<br/>Fire & Forget<br/>May lose events]
        AL[At-Least-Once<br/>Retry on failure<br/>May duplicate]
        EO[Exactly-Once<br/>Idempotency required<br/>Most complex]
    end
    
    subgraph "Processing Models"
        SP[Single Processor<br/>Simple, ordered<br/>Limited scale]
        CP[Competing Consumers<br/>Parallel processing<br/>Load balanced]
        PS[Partitioned Stream<br/>Ordered per key<br/>Scalable]
    end
```

| Pattern | Guarantee | Use Case | Implementation |
|---------|-----------|----------|----------------|
| **Fire & Forget** | None | Logging, metrics | No acks, no retries |
| **At-Least-Once** | Delivery | Most systems | Acks + retries |
| **Exactly-Once** | Processing | Financial | Idempotency keys |
| **Ordered** | Sequence | Event sourcing | Single partition |

### Event-Driven Saga Pattern

```mermaid
stateDiagram-v2
    [*] --> Started: Saga Initiated
    Started --> Processing: Begin Execution
    
    Processing --> InventoryReserved: Reserve Inventory
    InventoryReserved --> PaymentProcessed: Process Payment
    PaymentProcessed --> OrderConfirmed: Confirm Order
    OrderConfirmed --> Completed: Success
    
    Processing --> Compensating: Any Step Fails
    InventoryReserved --> Compensating: Payment Fails
    PaymentProcessed --> Compensating: Confirmation Fails
    
    Compensating --> Failed: After Compensation
    Completed --> [*]: Success End
    Failed --> [*]: Failure End
    
    note right of Compensating
        Reverse all completed
        steps in order
    end note
```

```mermaid
sequenceDiagram
    participant S as Saga Coordinator
    participant IS as Inventory Service
    participant PS as Payment Service
    participant OS as Order Service
    
    S->>IS: ReserveInventory Command
    IS-->>S: InventoryReserved Event
    
    S->>PS: ProcessPayment Command
    PS-->>S: PaymentProcessed Event
    
    S->>OS: ConfirmOrder Command
    
    alt Success
        OS-->>S: OrderConfirmed Event
        S->>S: Mark Completed
    else Failure
        OS-->>S: OrderFailed Event
        S->>S: Begin Compensation
        S->>PS: RefundPayment Command
        S->>IS: ReleaseInventory Command
    end
```

### Saga Pattern Comparison

| Saga Type | Coordination | Complexity | Use Case |
|-----------|--------------|------------|----------|
| **Orchestration** | Central coordinator | Medium | Well-defined workflows |
| **Choreography** | Event-driven | High | Loosely coupled services |
| **Hybrid** | Mixed approach | Very High | Complex requirements |

---

## Level 3: Deep Dive

<div class="failure-vignette">
<h4>💥 The Knight Capital Event-Driven Disaster (2012)</h4>

**What Happened**: Knight Capital lost $440 million in 45 minutes due to an event processing bug in their algorithmic trading system

**Root Cause**: 
- Old code accidentally reactivated during deployment
- System started processing market events as if it were 8 years in the past
- Events triggered massive buy orders for 150 stocks
- Each event amplified the next in a runaway feedback loop
- No circuit breakers on event-driven trading logic

**Impact**: 
- $440M loss in 45 minutes
- 10% of NYSE daily volume
- Company bankruptcy within days
- Thousands of jobs lost

**Lessons Learned**:
- Event handlers must be idempotent 
- Event versioning is critical for system evolution
- Circuit breakers essential in event chains
- Event replay capability requires careful state management
- Dead letter queues prevent infinite retry loops
</div>

<div class="decision-box">
<h4>🎯 Event-Driven Implementation Strategy</h4>

**Start Simple - Notification Pattern:**
- Events contain minimal data (just IDs)
- Consumers fetch details as needed
- Easier to implement and debug
- Natural rate limiting through pull model

**Scale Up - Event-Carried State Transfer:**
- Events contain all necessary data
- Eliminates synchronous dependencies
- Higher throughput but larger events
- Schema evolution becomes critical

**Go Full-Scale - Event Sourcing:**
- Events as the single source of truth
- Complete audit trail and replay capability
- Most complex but most powerful
- Requires sophisticated tooling

**Hybrid Approach - Smart Routing:**
- Critical events carry full state
- Bulk events use notification pattern
- Analytics events use different retention
- Optimize per use case

**Key Decision Factors:**
- Team experience with eventual consistency
- Performance requirements (latency vs throughput)
- Data consistency requirements
- Infrastructure complexity tolerance
- Debugging and operational capabilities
</div>

### Advanced Event Patterns

### CQRS with Event Sourcing

```mermaid
graph TB
    subgraph "Write Side"
        CMD[Commands] --> AGG[Domain Model]
        AGG --> ES[(Event Store)]
    end
    
    subgraph "Read Side"
        ES --> PROJ[Projection Handler]
        PROJ --> V1[Customer View]
        PROJ --> V2[Order List View]
        PROJ --> V3[Analytics View]
    end
    
    subgraph "Query Side"
        Q[Queries] --> V1
        Q --> V2
        Q --> V3
    end
    
    style ES fill:#818cf8,stroke:#6366f1,stroke-width:3px
```

| Component | Purpose | Storage | Update Frequency |
|-----------|---------|---------|------------------|
| **Event Store** | Source of truth | Append-only | Real-time |
| **Projections** | Optimized queries | Denormalized | Eventual |
| **Snapshots** | Performance | Point-in-time | Periodic |
| **Read Models** | UI/API serving | Various DBs | Near real-time |

### Complex Event Processing Patterns

```mermaid
graph LR
    subgraph "Event Patterns"
        S[Simple Event<br/>Single occurrence]
        C[Complex Event<br/>Pattern matching]
        D[Derived Event<br/>Calculated from others]
    end
    
    subgraph "Detection Windows"
        T[Tumbling<br/>Non-overlapping]
        SL[Sliding<br/>Overlapping]
        SE[Session<br/>Activity-based]
    end
    
    subgraph "Actions"
        A[Alert]
        F[Filter]
        E[Enrich]
        R[Route]
    end
```

| Use Case | Pattern Type | Window | Example |
|----------|--------------|--------|---------||
| **Fraud Detection** | Threshold + Correlation | 5 min sliding | 5+ payments, 3+ cards |
| **System Monitoring** | Sequence | 1 min tumbling | Error → Retry → Fail |
| **User Analytics** | Session | Activity-based | Click → View → Purchase |
| **Anomaly Detection** | Statistical | 1 hour sliding | 3σ deviation |

### Stream Processing Architecture

```mermaid
graph LR
    subgraph "Stream Processing Pipeline"
        I[Input<br/>Events] --> F[Filter<br/>Select relevant]
        F --> M[Map<br/>Transform]
        M --> W[Window<br/>Group by time]
        W --> A[Aggregate<br/>Calculate]
        A --> O[Output<br/>Results]
    end
    
    subgraph "Window Types"
        W --> TW[Tumbling<br/>Fixed, non-overlap]
        W --> SW[Sliding<br/>Fixed, overlap]
        W --> SES[Session<br/>Activity gap]
    end
```

---

## Level 4: Expert

### Production Case Study: LinkedIn's Kafka Platform

<div class="decision-box">
<h4>🏢 LinkedIn Event Architecture</h4>

**Scale**: 7 trillion messages/day across 100+ Kafka clusters

**Architecture Tiers**:
1. **Local Kafka** (per data center)
   - 6-hour retention, LZ4 compression
   - Handles regional traffic
   
2. **Regional Kafka** (aggregation)
   - 3-day retention, Zstd compression
   - Cross-datacenter replication
   
3. **Hadoop** (long-term storage)
   - 365-day retention, Avro format
   - Historical analysis

**Key Design Decisions**:
- Partition by entity type (member, job, company)
- Separate streams for different use cases
- Multi-tier storage for cost optimization
- Exactly-once semantics for critical flows
</div>

### Event Ordering Strategies

| Strategy | Use Case | Trade-offs |
|----------|----------|------------|
| **Key-based** | User actions | Hotspots possible |
| **Round-robin** | Metrics, logs | No ordering |
| **Hash-based** | Even distribution | Ordering per key |
| **Custom** | Business logic | Complex to manage |

### Event Store Design Decisions

```mermaid
graph TB
    subgraph "Storage Strategy"
        ES[(Event Store)]
        ES --> HOT[Hot Storage<br/>Recent events<br/>SSD, 7 days]
        ES --> WARM[Warm Storage<br/>Recent history<br/>HDD, 30 days]
        ES --> COLD[Cold Storage<br/>Archive<br/>S3, Forever]
    end
    
    subgraph "Optimization"
        SNAP[Snapshots<br/>Every 100 events]
        PROJ[Projections<br/>Read models]
        IDX[Indexes<br/>By time, type]
    end
```

| Storage Tier | Retention | Access Pattern | Cost |
|--------------|-----------|----------------|------|
| **Hot** | 7 days | Real-time queries | $$$ |
| **Warm** | 30 days | Recent history | $$ |
| **Cold** | Forever | Compliance/replay | $ |
| **Snapshots** | Latest | Fast rebuilds | $$ |

### Production Monitoring Strategy

```mermaid
graph TB
    subgraph "Key Metrics"
        M1[Event Rate<br/>Events/sec]
        M2[Processing Latency<br/>p50, p95, p99]
        M3[Consumer Lag<br/>Messages behind]
        M4[Error Rate<br/>Failed events]
    end
    
    subgraph "Alerts"
        A1[Lag > 100k]
        A2[Latency > 1s]
        A3[Errors > 1%]
        A4[DLQ growing]
    end
    
    subgraph "Dashboards"
        D1[Event Flow]
        D2[Service Health]
        D3[Performance]
    end
```

### Critical Monitoring Points

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **Consumer Lag** | > 10k | > 100k | Scale consumers |
| **Processing Time** | > 500ms | > 1s | Optimize handlers |
| **Error Rate** | > 0.1% | > 1% | Check logs |
| **DLQ Size** | > 100 | > 1000 | Manual intervention |

---

## Level 5: Mastery

### Theoretical Foundations

### Event Ordering Guarantees

```mermaid
graph LR
    subgraph "Ordering Types"
        NO[No Ordering<br/>Best performance]
        PK[Partition Key<br/>Order per key]
        GO[Global Ordering<br/>Total order]
    end
    
    subgraph "Implementation"
        NO --> P1[Parallel partitions]
        PK --> P2[Hash partitioning]
        GO --> P3[Single partition]
    end
    
    subgraph "Trade-offs"
        P1 --> T1[Max throughput<br/>No guarantees]
        P2 --> T2[Good throughput<br/>Partial order]
        P3 --> T3[Limited throughput<br/>Total order]
    end
```

### Performance Modeling

| Model | Formula | Use Case |
|-------|---------|----------|
| **Little's Law** | L = λW | Queue length from rate & wait time |
| **M/M/1 Queue** | ρ = λ/μ | Single processor utilization |
| **M/M/n Queue** | Complex | Multi-processor systems |
| **Amdahl's Law** | S = 1/((1-P)+P/N) | Parallel processing speedup |

### Capacity Planning

```mermaid
graph LR
    subgraph "Input Metrics"
        AR[Arrival Rate<br/>1000 events/sec]
        PR[Processing Rate<br/>100 events/sec/handler]
        RT[Response Time<br/>< 100ms target]
    end
    
    subgraph "Calculations"
        U[Utilization = AR/(n*PR)]
        N[Handlers = ceil(AR/PR * 1.5)]
        Q[Queue Length = ρ²/(1-ρ)]
    end
    
    subgraph "Output"
        H[Need 15 handlers]
        E[Expected 67% utilization]
        L[Avg queue: 5 events]
    end
```

### Future Directions

### Event Mesh Architecture (Future)

```mermaid
graph TB
    subgraph "Edge Layer"
        E1[IoT Devices]
        E2[Mobile Apps]
        E3[Edge Compute]
    end
    
    subgraph "Gateway Layer"
        G1[5G Towers]
        G2[CDN PoPs]
        G3[Edge Aggregators]
    end
    
    subgraph "Regional Layer"
        R1[Stream Processing]
        R2[ML Inference]
        R3[Regional Storage]
    end
    
    subgraph "Global Layer"
        C1[Central Analytics]
        C2[Long-term Storage]
        C3[Global Coordination]
    end
    
    E1 & E2 & E3 --> G1 & G2 & G3
    G1 & G2 & G3 --> R1 & R2 & R3
    R1 & R2 & R3 --> C1 & C2 & C3
```

### AI-Enhanced Event Processing

| Capability | Technology | Use Case |
|------------|------------|----------|
| **Anomaly Detection** | Isolation Forest | Fraud, system failures |
| **Pattern Prediction** | LSTM/Transformer | Capacity planning |
| **Auto-scaling** | Reinforcement Learning | Resource optimization |
| **Event Classification** | Deep Learning | Routing, prioritization |

### ROI Analysis

| Factor | Traditional | Event-Driven | Savings |
|--------|-------------|--------------|----------|
| **Coupling incidents** | 10/year @ $50k | 2/year @ $50k | $400k/year |
| **Scaling efficiency** | 40% over-provisioned | 10% over-provisioned | $300k/year |
| **Feature velocity** | 30 days | 10 days | $480k/year |
| **Operations** | 40 hrs/week | 20 hrs/week | $150k/year |

**Total Annual Savings**: $1.33M  
**Investment**: $650k  
**Payback Period**: 6 months  
**5-Year ROI**: 925%

---

## Quick Reference

<div class="truth-box">
<h4>💡 Event-Driven Architecture Insights</h4>

**The Event Ordering Paradox:**
- Most events don't need strict ordering, but the 5% that do are critical
- Partition keys provide order within stream, but can create hotspots
- Global ordering is expensive - use only when business requires it

**Eventual Consistency Reality:**
- 95% of business operations can tolerate eventual consistency
- The other 5% need careful design with compensation patterns
- Most "real-time" requirements are actually "fast enough" requirements

**Event Storage Economics:**
- Kafka retention costs: ~$0.10/GB/month
- Traditional database storage: ~$1.00/GB/month  
- Event replay value: Often worth 10x storage cost during incidents

**Production Wisdom:**
> "Event-driven systems amplify both good design and bad design. There's no middle ground."

**The Three Laws of Event Evolution:**
1. Events will grow larger over time (plan for schema evolution)
2. Consumers will multiply faster than expected (design for fan-out)
3. Event ordering requirements emerge late (prepare for partitioning changes)
</div>

### Decision Framework

| Question | Yes → Event-Driven | No → Alternative |
|----------|-------------------|------------------|
| Multiple services need same data? | ✅ Publish events | ⚠️ Direct API calls |
| Need loose coupling? | ✅ Event bus | ⚠️ Shared database |
| Async processing acceptable? | ✅ Event queues | ⚠️ Synchronous APIs |
| Need audit trail? | ✅ Event sourcing | ⚠️ Traditional logging |
| Complex workflows? | ✅ Event-driven saga | ⚠️ Orchestration service |


### Implementation Checklist

- [ ] Define event schema and versioning strategy
- [ ] Choose event bus/broker (Kafka, RabbitMQ, etc.)
- [ ] Implement event publishing with retries
- [ ] Create event handlers with idempotency
- [ ] Set up event store if using event sourcing
- [ ] Configure dead letter queues
- [ ] Implement monitoring and tracing
- [ ] Plan for event replay capability
- [ ] Document event flows
- [ ] Test failure scenarios

### Common Anti-Patterns

1. **Event spaghetti** - Too many fine-grained events
2. **Missing schemas** - No event versioning strategy
3. **Synchronous events** - Using events for request-response
4. **Fat events** - Including entire aggregate state
5. **No idempotency** - Handlers not handling duplicates

---

## 🎓 Key Takeaways

1. **Events enable autonomy** - Services can evolve independently
2. **Async by default** - Embrace eventual consistency
3. **Events are facts** - Immutable, business-focused
4. **Order matters sometimes** - Use partitioning strategically
5. **Monitor everything** - Event flows need observability

---

*"In an event-driven architecture, the question isn't 'what should I call?' but 'who should I tell?'"*

---

**Previous**: [← Edge Computing/IoT Patterns](edge-computing.md) | **Next**: [Event Sourcing Pattern →](event-sourcing.md)