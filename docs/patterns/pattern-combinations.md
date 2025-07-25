---
title: Pattern Combination Guide
description: Combine distributed systems patterns effectively for real-world architectures
type: pattern
category: specialized
difficulty: advanced
reading_time: 45 min
prerequisites: ["Understanding of individual patterns"]
when_to_use: When dealing with specialized challenges
when_not_to_use: When simpler solutions suffice
status: complete
last_updated: 2025-07-23
---

# Pattern Combination Guide

> *"Individual patterns are like musical notes. The magic happens when you compose them into a symphony."*

## 🎼 The Art of Pattern Composition

### Why Combine Patterns?

Real systems face multiple challenges simultaneously: Performance AND Reliability, Scale AND Consistency, Cost AND Complexity.

### Three Laws of Pattern Combination

1. **Law of Synergy**: Combined patterns enhance each other's strengths
2. **Law of Simplicity**: Each pattern must justify its complexity
3. **Law of Harmony**: Patterns must not conflict fundamentally

---

## 🗺️ Visual Pattern Relationship Map

```mermaid
graph TB
    subgraph "Foundation Layer"
        LB[Load Balancer]
        SD[Service Discovery]
        SR[Service Registry]
    end
    
    subgraph "Communication Layer"
        AG[API Gateway]
        SM[Service Mesh]
        MQ[Message Queue]
        EB[Event Bus]
    end
    
    subgraph "Data Layer"
        CQRS[CQRS]
        ES[Event Sourcing]
        CDC[CDC]
        SH[Sharding]
        CACHE[Caching]
    end
    
    subgraph "Resilience Layer"
        CB[Circuit Breaker]
        RT[Retry & Backoff]
        BH[Bulkhead]
        TO[Timeout]
        RL[Rate Limiting]
    end
    
    subgraph "Coordination Layer"
        SAGA[Saga]
        LE[Leader Election]
        DL[Distributed Lock]
        OUT[Outbox]
    end
    
    subgraph "Scale Layer"
        AS[Auto-Scaling]
        EC[Edge Computing]
        GR[Geo-Replication]
        CDN[CDN]
    end
    
    %% Foundation connections
    LB --> AG
    SD --> SR
    SR --> SM
    
    %% Communication connections
    AG --> SM
    SM --> MQ
    MQ --> EB
    EB --> ES
    
    %% Data connections
    ES --> CQRS
    CQRS --> CDC
    CDC --> CACHE
    CACHE --> SH
    
    %% Resilience connections
    CB --> RT
    RT --> BH
    BH --> TO
    TO --> RL
    
    %% Coordination connections
    SAGA --> OUT
    OUT --> ES
    LE --> DL
    
    %% Scale connections
    AS --> EC
    EC --> GR
    GR --> CDN
    
    %% Cross-layer connections
    SM -.-> CB
    SM -.-> RL
    AG -.-> RL
    CQRS -.-> SAGA
    ES -.-> OUT
    
    style LB fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style AG fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style CQRS fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style CB fill:#ffebee,stroke:#c62828,stroke-width:2px
    style SAGA fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style AS fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

### Pattern Dependency Matrix

| Pattern | Requires | Works Well With | Conflicts With |
|---------|----------|-----------------|----------------|
| **CQRS** | Event Store or Separate DBs | Event Sourcing, CDC, Saga | Synchronous Projections |
| **Event Sourcing** | Event Store, Idempotent Handlers | CQRS, Saga, Outbox | Direct State Updates |
| **Saga** | Message Queue/Event Bus | Event Sourcing, Outbox | Two-Phase Commit |
| **Service Mesh** | Service Registry | Circuit Breaker, Rate Limiting | Direct Service Calls |
| **Circuit Breaker** | Monitoring, Metrics | Retry, Timeout, Bulkhead | Unbounded Retries |
| **Sharding** | Consistent Hashing | CQRS, Caching | Cross-Shard Joins |
| **Edge Computing** | CDN, Geographic Distribution | Geo-Replication, Caching | Centralized Processing |

---

## 🏗️ Foundational Combinations

### The Classic Trio: CQRS + Event Sourcing + Saga

The most powerful combination for complex business domains.

```mermaid
graph TB
    subgraph "Write Side"
        CMD[Commands] --> AGG[Aggregates]
        AGG --> ES[Event Store]
        ES --> OUT[Outbox]
    end
    
    subgraph "Read Side"
        ES --> PROJ[Projections]
        PROJ --> READ[Read Models]
        READ --> CACHE[Cache]
    end
    
    subgraph "Process Management"
        ES --> SAGA[Saga Manager]
        SAGA --> CMD2[New Commands]
    end
    
    style ES fill:#f96,stroke:#333,stroke-width:4px
    style SAGA fill:#69f,stroke:#333,stroke-width:4px
```

**Why This Works:** Event Sourcing provides write model + audit trail • CQRS optimizes reads • Saga manages long-running processes • Each addresses different concerns

**Implementation Example:**

```python
class OrderSystem:
    """E-commerce order system using CQRS + ES + Saga"""
    
    def __init__(self):
        self.event_store = EventStore()
        self.read_store = ReadModelStore()
        self.saga_manager = SagaManager()
        
    async def handle_create_order(self, command: CreateOrderCommand):
        # 1. Command handling (Write side)
        order = Order(command.order_id)
        events = order.create(command.items, command.customer_id)
        
        # 2. Event Sourcing
        await self.event_store.append(order.id, events)
        
        # 3. Update read models (CQRS)
        for event in events:
            await self.read_store.project(event)
        
        # 4. Start saga for order fulfillment
        if isinstance(event, OrderCreatedEvent):
            await self.saga_manager.start_saga(
                OrderFulfillmentSaga(order.id)
            )
```

### The Resilience Stack: Circuit Breaker + Retry + Timeout + Bulkhead

Essential for any system with external dependencies.

```mermaid
graph LR
    REQ[Request] --> TO[Timeout]
    TO --> BH[Bulkhead]
    BH --> CB[Circuit Breaker]
    CB --> RT[Retry Logic]
    RT --> SVC[External Service]
    
    CB --> FB[Fallback]
    
    style CB fill:#f96,stroke:#333,stroke-width:4px
    style BH fill:#69f,stroke:#333,stroke-width:4px
```

**Layered Implementation:**

```python
class ResilientServiceClient:
    """Resilient client with all protection patterns"""
    
    def __init__(self, service_url: str):
        self.service_url = service_url
        
        # Layer 1: Bulkhead (resource isolation)
        self.bulkhead = Bulkhead(
            max_concurrent_calls=100,
            max_wait_duration=timedelta(seconds=1)
        )
        
        # Layer 2: Circuit Breaker (failure detection)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=timedelta(seconds=30),
            expected_exception=ServiceException
        )
        
        # Layer 3: Retry (transient failure handling)
        self.retry_policy = RetryPolicy(
            max_attempts=3,
            backoff=ExponentialBackoff(base=2, max=10)
        )
        
        # Layer 4: Timeout (latency control)
        self.timeout = timedelta(seconds=5)
    
    @resilient  # Combines all patterns
    async def call_service(self, request: dict) -> dict:
        async with self.bulkhead:
            return await self.circuit_breaker.call(
                lambda: self.retry_policy.execute(
                    lambda: self._make_request_with_timeout(request)
                )
            )
```

---

## 🌍 Global Scale Combinations

### The Geographic Trinity: Geo-Replication + Edge Computing + CDN

For worldwide low-latency access.

```mermaid
graph TB
    subgraph "Users"
        US[US Users]
        EU[EU Users]
        AS[Asia Users]
    end
    
    subgraph "Edge Layer"
        CDN1[CDN PoP US]
        CDN2[CDN PoP EU]
        CDN3[CDN PoP Asia]
        
        EC1[Edge Compute US]
        EC2[Edge Compute EU]
        EC3[Edge Compute Asia]
    end
    
    subgraph "Regional Replicas"
        DB1[(US Database)]
        DB2[(EU Database)]
        DB3[(Asia Database)]
    end
    
    US --> CDN1 --> EC1 --> DB1
    EU --> CDN2 --> EC2 --> DB2
    AS --> CDN3 --> EC3 --> DB3
    
    DB1 -.->|Geo-replication| DB2
    DB2 -.->|Geo-replication| DB3
    DB3 -.->|Geo-replication| DB1
```

**Implementation Strategy:**

```python
class GlobalArchitecture:
    """Global scale with edge + CDN + geo-replication"""
    
    def __init__(self):
        self.regions = {
            'us-east': Region('us-east-1'),
            'eu-west': Region('eu-west-1'),
            'ap-south': Region('ap-south-1')
        }
        
        # Configure geo-replication
        self.setup_geo_replication()
        
        # Deploy edge functions
        self.deploy_edge_compute()
        
        # Configure CDN
        self.setup_cdn()
    
    async def handle_request(self, request: Request) -> Response:
        # 1. CDN handles static content
        if self.is_cacheable(request):
            return await self.cdn.serve(request)
        
        # 2. Edge compute for dynamic but stateless
        if self.is_edge_compatible(request):
            return await self.edge.process(request)
        
        # 3. Route to nearest region for data operations
        region = self.get_nearest_region(request.client_location)
        return await region.handle(request)
```

### The Data Pipeline: CDC + Streaming + CQRS

For real-time analytics and reporting.

```mermaid
graph LR
    subgraph "Operational Systems"
        DB[(OLTP Database)]
        APP[Applications] --> DB
    end
    
    subgraph "Data Pipeline"
        DB --> CDC[CDC Connector]
        CDC --> STREAM[Event Stream]
        STREAM --> PROC[Stream Processor]
    end
    
    subgraph "Analytics"
        PROC --> DW[(Data Warehouse)]
        PROC --> RT[Real-time Views]
        PROC --> ML[ML Pipeline]
    end
    
    style CDC fill:#f96,stroke:#333,stroke-width:4px
    style STREAM fill:#69f,stroke:#333,stroke-width:4px
```

---

## 🔄 Event-Driven Combinations

### The Reliable Event Bus: Outbox + Idempotent Receiver + Dead Letter Queue

Guarantees exactly-once processing in distributed systems.

```python
class ReliableEventBus:
    """Reliable event processing with exactly-once semantics"""
    
    def __init__(self):
        self.outbox = TransactionalOutbox()
        self.receiver = IdempotentReceiver()
        self.dlq = DeadLetterQueue()
    
    async def publish_event(self, event: Event, tx: Transaction):
        """Publish with transactional guarantee"""
        # Save to outbox in same transaction
        await self.outbox.save(event, tx)
    
    async def process_event(self, event: Event):
        """Process with idempotency guarantee"""
        try:
            # Check if already processed
            result = await self.receiver.process(
                event.id,
                self._handle_event,
                event
            )
            return result
            
        except Exception as e:
            # Send to DLQ after retries exhausted
            if event.retry_count >= MAX_RETRIES:
                await self.dlq.send(event, error=str(e))
            else:
                # Retry with exponential backoff
                await self.schedule_retry(event)
```

### The Microservices Foundation: Service Mesh + API Gateway + Event Bus

The complete microservices communication layer.

```mermaid
graph TB
    subgraph "External"
        CLIENT[Clients]
        MOBILE[Mobile Apps]
    end
    
    subgraph "API Layer"
        GW[API Gateway]
        GW --> AUTH[Auth Service]
        GW --> RL[Rate Limiter]
    end
    
    subgraph "Service Mesh"
        SVC1[Service A]
        SVC2[Service B]
        SVC3[Service C]
        
        PROXY1[Sidecar]
        PROXY2[Sidecar]
        PROXY3[Sidecar]
        
        SVC1 --- PROXY1
        SVC2 --- PROXY2
        SVC3 --- PROXY3
        
        PROXY1 -.-> PROXY2
        PROXY2 -.-> PROXY3
    end
    
    subgraph "Async Communication"
        BUS[Event Bus]
        SVC1 --> BUS
        SVC2 --> BUS
        SVC3 --> BUS
    end
    
    CLIENT --> GW
    MOBILE --> GW
    GW --> PROXY1
    GW --> PROXY2
```

---

## 🎯 Domain-Specific Combinations

### E-Commerce Platform

| Component | Pattern | Purpose |
|-----------|---------|----------|
| Catalog | CQRS | Read-heavy optimization |
| Orders | Event Sourcing | Audit trail |
| Checkout | Saga | Distributed transaction |
| Events | Outbox | Reliable delivery |
| Users | Sharding | Scale data |
| Products | Caching | Performance |
| Payments | Circuit Breaker | Resilience |

### Financial Trading System

| Component | Pattern | Purpose |
|-----------|---------|----------|
| Audit Log | Event Sourcing | Compliance |
| Positions | CQRS | Real-time tracking |
| Order Matching | Leader Election | Determinism |
| Risk Management | Bulkhead | Isolation |
| Market Data | Circuit Breaker | Feed resilience |
| Order Processing | Idempotent Receiver | Exactly-once |

### IoT Platform

| Component | Pattern | Purpose |
|-----------|---------|----------|
| Local Processing | Edge Computing | Reduce latency |
| Telemetry | Event Streaming | High-volume ingestion |
| Storage | Sharded Time-series DB | Scale metrics |
| Device Control | Rate Limiting | Prevent overload |
| Commands | Circuit Breaker | Handle failures |
| Sync | CDC | Data propagation |

---

## ⚠️ Anti-Pattern Combinations

### Dangerous Combinations to Avoid

#### ❌ Synchronous Saga + Two-Phase Commit

```python
# DON'T DO THIS
class BadSaga:
    async def execute_step(self):
        # Saga should be eventually consistent
        # 2PC defeats the purpose
        with TwoPhaseCommit() as tpc:  # ❌ Wrong!
            await service1.update()
            await service2.update()
```

**Why it's bad:**
- Combines disadvantages of both patterns
- Loses saga's failure isolation
- Adds 2PC's availability problems

#### ❌ Caching + Strong Consistency

```python
# DON'T DO THIS
class BadCache:
    async def read(self, key):
        # Can't have cache AND strong consistency
        value = await cache.get(key)  # ❌ Might be stale!
        if not value:
            value = await db.read_with_lock(key)  # Strong consistency
        return value
```

**Why it's bad:**
- Cache inherently serves stale data
- Strong consistency requires fresh reads
- Contradictory requirements

#### ❌ Event Sourcing + Synchronous Projections

```python
# DON'T DO THIS
class BadEventSourcing:
    async def save_event(self, event):
        await event_store.append(event)
        # Synchronous projection defeats ES benefits
        await update_all_read_models(event)  # ❌ Wrong!
        return "success"
```

**Why it's bad:**
- Loses event sourcing's performance benefits
- Creates tight coupling
- Makes system fragile

---

## 🏆 Best Practice Combinations

### The Reliability Sandwich

Layer patterns inside-out:

```python
@bulkhead          # 4. Isolate resources (outermost)
@circuit_breaker   # 3. Prevent cascades
@retry             # 2. Handle transient failures
@timeout(5)        # 1. Fail fast (innermost)
async def call_service(self):
    return await external_service.call()
```

### The Data Consistency Hierarchy

| Data Type | Consistency Pattern | Supporting Pattern |
|-----------|--------------------|-----------------|
| Financial | Strong consistency | Event sourcing |
| User profiles | Session consistency | Caching |
| Analytics | Eventual consistency | CDC |
| Counters | CRDTs | Eventual consistency |

---

## 📈 Evolution Patterns

### Growing from Monolith to Microservices

**Phase 1**: Monolith  
**Phase 2**: Monolith + Cache  
**Phase 3**: Monolith + Queue + Workers  
**Phase 4**: API Gateway + Services  
**Phase 5**: Service Mesh + Event Bus

### Pattern Addition Timeline

| Users | Add Patterns | Why |
|-------|-------------|-----|
| 10K | Caching, CDN | Reduce load |
| 100K | Queue, Workers | Handle peaks |
| 1M | CQRS, Sharding | Scale R/W |
| 10M | Service Mesh, Event Sourcing | Manage complexity |
| 100M | Edge Computing, Geo-replication | Global scale |

---

## 🔧 Implementation Strategies

### The Strangler Fig Pattern

Gradually replace monolith with pattern-based architecture:

```python
class StranglerFigMigration:
    """Gradually migrate to new patterns"""
    
    def __init__(self, legacy_system, new_system):
        self.legacy = legacy_system
        self.new = new_system
        self.router = TrafficRouter()
    
    async def handle_request(self, request):
        # Route based on migration progress
        if self.is_migrated(request.feature):
            return await self.new.handle(request)
        else:
            # Still use legacy
            response = await self.legacy.handle(request)
            
            # But capture events for new system
            await self.capture_legacy_events(request, response)
            
            return response
    
    def migrate_feature(self, feature: str):
        """Gradually move traffic to new system"""
        for percentage in [5, 25, 50, 90, 100]:
            self.router.set_split(feature, new=percentage)
            self.monitor_metrics()
            if not self.is_healthy():
                self.router.rollback(feature)
                break
            time.sleep(hours=24)
```

---

## 📊 Combination Metrics

### Measuring Pattern Effectiveness

Key metrics for pattern combinations:

```python
class PatternCombinationMetrics:
    """Track effectiveness of pattern combinations"""
    
    def __init__(self):
        self.metrics = {
            # Reliability combination metrics
            'circuit_breaker_opens': Counter(),
            'retry_success_rate': Gauge(),
            'bulkhead_rejections': Counter(),
            
            # Performance combination metrics
            'cache_hit_rate': Gauge(),
            'cqrs_lag': Histogram(),
            'event_processing_time': Histogram(),
            
            # Scale combination metrics
            'shard_distribution': Gauge(),
            'cross_region_latency': Histogram(),
            'edge_cache_hits': Counter()
        }
    
    def calculate_combination_effectiveness(self):
        """Measure how well patterns work together"""
        
        # Resilience score (CB + Retry + Bulkhead)
        resilience = (
            self.get_availability() * 0.4 +
            self.get_recovery_time() * 0.3 +
            self.get_isolation_effectiveness() * 0.3
        )
        
        # Performance score (CQRS + Cache + CDN)
        performance = (
            self.get_response_time_improvement() * 0.5 +
            self.get_throughput_increase() * 0.5
        )
        
        return {
            'resilience_score': resilience,
            'performance_score': performance,
            'overall_health': (resilience + performance) / 2
        }
```

---

## 🏛️ Layered Architecture Pattern Integration

### Complete System Architecture with Patterns

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App]
        MOB[Mobile App]
        API[External APIs]
    end
    
    subgraph "Gateway Layer"
        subgraph "API Gateway"
            AUTH[Authentication]
            RL[Rate Limiting]
            ROUTE[Routing]
            TRANS[Transformation]
        end
    end
    
    subgraph "Service Layer"
        subgraph "Service A"
            SA[Business Logic]
            SCA[Sidecar Proxy]
        end
        
        subgraph "Service B"
            SB[Business Logic]
            SCB[Sidecar Proxy]
        end
        
        subgraph "Service C"
            SC[Business Logic]
            SCC[Sidecar Proxy]
        end
    end
    
    subgraph "Data Layer"
        subgraph "Write Path"
            CMD[Commands]
            AGG[Aggregates]
            EVT[Event Store]
            OUT[Outbox]
        end
        
        subgraph "Read Path"
            PROJ[Projections]
            READ[Read Models]
            CACHE[Cache Layer]
        end
    end
    
    subgraph "Infrastructure Layer"
        MQ[Message Queue]
        SD[Service Discovery]
        CONFIG[Configuration]
        METRICS[Metrics/Monitoring]
    end
    
    %% Client connections
    WEB --> AUTH
    MOB --> AUTH
    API --> AUTH
    
    %% Gateway to services
    ROUTE --> SCA
    ROUTE --> SCB
    ROUTE --> SCC
    
    %% Service mesh
    SCA <--> SCB
    SCB <--> SCC
    SCA <--> SCC
    
    %% Write path
    SA --> CMD
    CMD --> AGG
    AGG --> EVT
    EVT --> OUT
    OUT --> MQ
    
    %% Read path
    MQ --> PROJ
    PROJ --> READ
    READ --> CACHE
    
    %% Service connections
    SB --> READ
    SC --> CACHE
    
    %% Infrastructure
    SCA --> SD
    SCB --> SD
    SCC --> SD
    SA --> CONFIG
    SB --> CONFIG
    SC --> CONFIG
    
    style AUTH fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    style EVT fill:#c8e6c9,stroke:#4caf50,stroke-width:2px
    style MQ fill:#e1bee7,stroke:#9c27b0,stroke-width:2px
    style CACHE fill:#ffecb3,stroke:#ff9800,stroke-width:2px
```

### Pattern Integration Points

| Layer | Primary Patterns | Integration Patterns | Key Considerations |
|-------|-----------------|---------------------|--------------------|
| **Client** | BFF, Client Library | Retry, Circuit Breaker | User experience, Network reliability |
| **Gateway** | API Gateway, Rate Limiting | Authentication, Routing | Security, Traffic management |
| **Service** | Service Mesh, Sidecar | Circuit Breaker, Bulkhead | Inter-service communication |
| **Data Write** | Event Sourcing, CQRS | Saga, Outbox | Consistency, Audit trail |
| **Data Read** | Materialized Views, Cache | CDC, Projections | Performance, Staleness |
| **Infrastructure** | Service Discovery, Config | Monitoring, Logging | Observability, Management |

---

## 🔄 Migration Paths Between Patterns

### Progressive Pattern Evolution

```mermaid
graph LR
    subgraph "Phase 1: Monolith"
        M[Monolithic App]
    end
    
    subgraph "Phase 2: Modular"
        M --> MM[Modular Monolith]
        MM --> C1[Add Caching]
        C1 --> Q1[Add Queue]
    end
    
    subgraph "Phase 3: Services"
        Q1 --> MS[Microservices]
        MS --> AG[API Gateway]
        AG --> CB[Circuit Breaker]
    end
    
    subgraph "Phase 4: Event-Driven"
        CB --> ES[Event Sourcing]
        ES --> CQRS[CQRS]
        CQRS --> SAGA[Saga Pattern]
    end
    
    subgraph "Phase 5: Mesh"
        SAGA --> SM[Service Mesh]
        SM --> EC[Edge Computing]
        EC --> GEO[Geo-Distribution]
    end
    
    style M fill:#ffebee,stroke:#f44336,stroke-width:2px
    style MS fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style ES fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style SM fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style GEO fill:#fff3e0,stroke:#ff9800,stroke-width:2px
```

### Migration Decision Framework

| Current State | Pain Points | Next Pattern | Implementation Effort |
|--------------|-------------|--------------|----------------------|
| **Monolith** | Slow deployments | Modular Monolith | Low ⭐⭐ |
| **Monolith** | Performance issues | Add Caching | Low ⭐⭐ |
| **Modular Monolith** | Team conflicts | Microservices | High ⭐⭐⭐⭐ |
| **Microservices** | Service failures | Circuit Breaker | Medium ⭐⭐⭐ |
| **Microservices** | Complex workflows | Saga Pattern | High ⭐⭐⭐⭐ |
| **Services + Events** | Network complexity | Service Mesh | High ⭐⭐⭐⭐ |
| **Service Mesh** | Global latency | Edge Computing | Very High ⭐⭐⭐⭐⭐ |

---

## ⚠️ Anti-Pattern Combinations Deep Dive

### Detailed Anti-Pattern Analysis

```mermaid
graph TB
    subgraph "Anti-Pattern: Distributed Monolith"
        S1[Service 1] -->|Sync| S2[Service 2]
        S2 -->|Sync| S3[Service 3]
        S3 -->|Sync| S4[Service 4]
        S4 -->|Sync| S1
    end
    
    subgraph "Anti-Pattern: Chatty Services"
        A[Service A] -->|100 calls/request| B[Service B]
        B -->|50 calls/request| C[Service C]
        C -->|200 calls/request| A
    end
    
    subgraph "Anti-Pattern: Shared Database"
        MS1[Microservice 1] --> DB[(Shared DB)]
        MS2[Microservice 2] --> DB
        MS3[Microservice 3] --> DB
        MS4[Microservice 4] --> DB
    end
    
    style S1 fill:#ffcdd2,stroke:#d32f2f,stroke-width:3px
    style A fill:#ffcdd2,stroke:#d32f2f,stroke-width:3px
    style DB fill:#ffcdd2,stroke:#d32f2f,stroke-width:3px
```

### Anti-Pattern Remediation Guide

| Anti-Pattern | Symptoms | Solution Patterns | Migration Steps |
|--------------|----------|------------------|----------------|
| **Distributed Monolith** | Cascading failures, Synchronized deployments | Event-Driven, Saga, Async messaging | 1. Identify boundaries<br>2. Add message queue<br>3. Convert sync to async<br>4. Implement saga |
| **Chatty Services** | High latency, Network congestion | BFF, GraphQL, CQRS | 1. Analyze call patterns<br>2. Create aggregation layer<br>3. Implement caching<br>4. Batch requests |
| **Shared Database** | Schema conflicts, Coupling | Database per service, Event Sourcing, CDC | 1. Identify ownership<br>2. Split by subdomain<br>3. Implement CDC<br>4. Eventual consistency |
| **Synchronous Event Processing** | Poor performance, Tight coupling | Async messaging, Event streaming | 1. Add message broker<br>2. Make handlers async<br>3. Implement backpressure<br>4. Add monitoring |

---

## 🎯 Problem-to-Pattern Quick Reference

### Common Scenarios and Pattern Solutions

```mermaid
graph TD
    Start[Problem] --> Type{Problem Type?}
    
    Type -->|Performance| Perf{Specific Issue?}
    Perf -->|High Latency| PerfSol1[Caching + CDN]
    Perf -->|Low Throughput| PerfSol2[CQRS + Sharding]
    Perf -->|Slow Queries| PerfSol3[Materialized Views + Indexes]
    
    Type -->|Reliability| Rel{Failure Type?}
    Rel -->|Service Failures| RelSol1[Circuit Breaker + Retry]
    Rel -->|Data Loss| RelSol2[Event Sourcing + Outbox]
    Rel -->|Cascading Failures| RelSol3[Bulkhead + Timeout]
    
    Type -->|Scale| Scale{Scale Dimension?}
    Scale -->|Users| ScaleSol1[Load Balancing + Auto-scaling]
    Scale -->|Data| ScaleSol2[Sharding + Partitioning]
    Scale -->|Geographic| ScaleSol3[Edge Computing + Geo-replication]
    
    Type -->|Consistency| Cons{Requirements?}
    Cons -->|Strong| ConsSol1[2PC / Distributed Lock]
    Cons -->|Eventual| ConsSol2[Saga + Event Sourcing]
    Cons -->|Flexible| ConsSol3[CRDT + Tunable Consistency]
    
    style Start fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PerfSol1 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style RelSol1 fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    style ScaleSol1 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style ConsSol1 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

---

## 🎓 Key Takeaways

### Golden Rules

1. **Start Simple** - One pattern, add as needed
2. **Measure Everything** - Validate combinations help
3. **Respect Dependencies** - Some patterns require others
4. **Avoid Conflicts** - Don't mix opposing goals
5. **Plan Evolution** - Design for gradual adoption

### Ultimate Combinations

- **Reliability**: Circuit Breaker + Retry + Timeout + Bulkhead
- **Performance**: CQRS + Caching + CDN + Edge Computing  
- **Scale**: Sharding + Service Mesh + Event Streaming
- **Consistency**: Event Sourcing + Saga + Outbox + Idempotent Receiver

### Pattern Combination Checklist

**Before Combining:**
- [ ] Understand each pattern individually
- [ ] Identify pattern dependencies
- [ ] Check for conflicts
- [ ] Assess team capabilities
- [ ] Calculate complexity cost

**During Implementation:**
- [ ] Start with core pattern
- [ ] Add supporting patterns incrementally
- [ ] Monitor metrics at each step
- [ ] Document integration points
- [ ] Train team on operations

**After Implementation:**
- [ ] Measure combined effectiveness
- [ ] Identify operational challenges
- [ ] Optimize configuration
- [ ] Plan next evolution
- [ ] Share learnings

---

*"Great architecture is not about using all the patterns, but about using the right patterns together."*

---

**Previous**: [← Pattern Selector](pattern-selector.md) | **Next**: [Pattern Index →](index.md)