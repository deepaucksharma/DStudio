---
title: Pattern Relationship Map - Visual Guide to Pattern Connections
description: Interactive visual maps showing how distributed systems patterns relate and work together
icon: material/graph
tags:
  - patterns
  - relationships
  - architecture
  - visual-guide
---

# Pattern Relationship Map

Understanding how patterns relate is crucial for building effective distributed systems. This visual guide shows the connections between patterns.

## 🌐 Master Relationship Map

This comprehensive map shows all major pattern relationships:

```mermaid
graph TB
    subgraph "Entry Points"
        Client[Client Request]
        Event[Event/Message]
        Data[Data Change]
    end
    
    subgraph "Communication Layer"
        AG[API Gateway]
        LB[Load Balancer]
        SM[Service Mesh]
        MQ[Message Queue]
        PS[Pub/Sub]
        WS[WebSocket]
    end
    
    subgraph "Resilience Layer"
        CB[Circuit Breaker]
        RT[Retry]
        TO[Timeout]
        BH[Bulkhead]
        GD[Graceful Degradation]
        HC[Health Check]
    end
    
    subgraph "Data Layer"
        ES[Event Sourcing]
        CQRS[CQRS]
        CDC[CDC]
        Saga[Saga]
        Cache[Cache]
        Shard[Sharding]
    end
    
    subgraph "Coordination Layer"
        LE[Leader Election]
        DL[Distributed Lock]
        CON[Consensus]
        DQ[Distributed Queue]
    end
    
    subgraph "Scale Layer"
        AS[Auto-scaling]
        CDN[CDN]
        EC[Edge Computing]
        RL[Rate Limiting]
    end
    
    %% Entry connections
    Client --> AG
    Client --> LB
    Event --> MQ
    Event --> PS
    Data --> CDC
    
    %% Communication to Resilience
    AG --> CB
    LB --> HC
    SM --> CB
    SM --> RT
    
    %% Resilience combinations
    CB -.-> RT
    RT -.-> TO
    CB --> GD
    
    %% Communication to Data
    AG --> Cache
    MQ --> ES
    PS --> ES
    
    %% Data relationships
    ES --> CQRS
    CQRS --> Saga
    CDC --> ES
    
    %% Scale relationships
    LB --> AS
    Cache --> CDN
    CDN --> EC
    AG --> RL
    
    %% Coordination usage
    Saga --> DL
    Shard --> LE
    ES --> DQ
    
    classDef communication fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef resilience fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef data fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    classDef coordination fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    classDef scale fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    
    class AG,LB,SM,MQ,PS,WS communication
    class CB,RT,TO,BH,GD,HC resilience
    class ES,CQRS,CDC,Saga,Cache,Shard data
    class LE,DL,CON,DQ coordination
    class AS,CDN,EC,RL scale
```

## 🔗 Key Pattern Relationships

### 1. The Resilience Chain
**Patterns that work together to prevent failures**

```mermaid
graph LR
    subgraph "Detection"
        HC[Health Check]
        TO[Timeout]
    end
    
    subgraph "Response"
        CB[Circuit Breaker]
        RT[Retry]
    end
    
    subgraph "Fallback"
        GD[Graceful Degradation]
        Cache[Cache]
    end
    
    HC -->|monitors| Service[Service]
    TO -->|detects slow| Service
    
    Service -->|fails| CB
    CB -->|closed| RT
    CB -->|open| GD
    
    RT -->|exhausted| GD
    GD -->|uses| Cache
    
    style HC fill:#4caf50
    style CB fill:#f44336
    style GD fill:#ff9800
```

**How they work together**:
- Health Check continuously monitors service health
- Timeout prevents operations from hanging indefinitely
- Circuit Breaker prevents cascade failures
- Retry handles transient failures (when circuit is closed)
- Graceful Degradation provides fallback functionality
- Cache provides stale but available data

### 2. The Data Consistency Journey
**Patterns for managing distributed data**

```mermaid
graph TD
    subgraph "Write Path"
        Write[Write Request] --> ES[Event Sourcing]
        ES --> EventStore[(Event Store)]
    end
    
    subgraph "Propagation"
        EventStore --> CDC[CDC]
        EventStore --> MQ[Message Queue]
        CDC --> Projections[Projections]
        MQ --> Projections
    end
    
    subgraph "Read Path"
        Projections --> CQRS[CQRS Read Model]
        CQRS --> Cache[Cache]
        Cache --> Read[Read Request]
    end
    
    subgraph "Transactions"
        ES -.-> Saga[Saga]
        Saga -.-> Compensation[Compensation]
    end
    
    style ES fill:#2196f3
    style CQRS fill:#4caf50
    style Saga fill:#ff9800
```

### 3. The Scale Architecture
**Patterns that enable horizontal scaling**

```mermaid
graph TB
    subgraph "Traffic Distribution"
        DNS[GeoDNS] --> CDN[CDN]
        CDN --> LB[Load Balancer]
        LB --> AG[API Gateway]
    end
    
    subgraph "Service Layer"
        AG --> SM[Service Mesh]
        SM --> Services[Services]
        Services --> AS[Auto-scaling]
    end
    
    subgraph "Data Distribution"
        Services --> Shard[Sharding]
        Shard --> Partition[Partitioning]
        Services --> Cache[Distributed Cache]
    end
    
    subgraph "Edge"
        CDN -.-> EC[Edge Computing]
        EC -.-> Cache
    end
    
    AS <-.-> Metrics[Metrics]
    
    style CDN fill:#ff9800
    style LB fill:#2196f3
    style Shard fill:#4caf50
```

## 🧩 Pattern Combinations by Use Case

### E-Commerce Platform
```mermaid
graph LR
    User[User] --> CDN[CDN<br/>Static Assets]
    CDN --> AG[API Gateway<br/>Single Entry]
    AG --> CB[Circuit Breaker<br/>Resilience]
    
    AG --> Cart[Cart Service]
    AG --> Product[Product Service]
    AG --> Payment[Payment Service]
    
    Cart --> Cache1[Redis Cache]
    Product --> Cache2[Redis Cache]
    Payment --> Saga[Saga<br/>Transactions]
    
    Saga --> ES[Event Sourcing<br/>Audit Trail]
    ES --> MQ[Message Queue]
    MQ --> Analytics[Analytics]
    
    style AG fill:#2196f3
    style Saga fill:#ff9800
    style ES fill:#4caf50
```

### Real-Time Chat System
```mermaid
graph LR
    Mobile[Mobile App] --> WS[WebSocket<br/>Real-time]
    Web[Web App] --> WS
    
    WS --> LB[Load Balancer<br/>Sticky Sessions]
    LB --> Gateway[Gateway Servers]
    
    Gateway --> PS[Pub/Sub<br/>Message Routing]
    PS --> MQ[Message Queue<br/>Persistence]
    
    Gateway --> Presence[Presence Service]
    Presence --> DL[Distributed Lock<br/>Consistency]
    
    MQ --> History[Message History]
    History --> ES[Event Sourcing]
    
    style WS fill:#ff9800
    style PS fill:#2196f3
    style ES fill:#4caf50
```

### Financial Trading System
```mermaid
graph TB
    Orders[Orders] --> Validate[Validation<br/>Service]
    
    Validate --> DL[Distributed Lock<br/>Prevent Duplicates]
    DL --> ES[Event Sourcing<br/>Audit Log]
    
    ES --> Saga[Saga<br/>Transaction Flow]
    Saga --> Risk[Risk Check]
    Saga --> Ledger[Ledger Update]
    Saga --> Notify[Notifications]
    
    Risk --> CB[Circuit Breaker]
    Ledger --> CQRS[CQRS<br/>Read/Write Split]
    
    CQRS --> Reports[Reporting<br/>Service]
    Reports --> MV[Materialized Views]
    
    style ES fill:#f44336
    style Saga fill:#2196f3
    style DL fill:#ff9800
```

## 🔄 Pattern Dependencies

### Hard Dependencies (Required)
```mermaid
graph LR
    subgraph "Must Have Together"
        LB[Load Balancer] -->|requires| HC[Health Check]
        SM[Service Mesh] -->|requires| SD[Service Discovery]
        AS[Auto-scaling] -->|requires| Metrics[Metrics]
        Saga -->|requires| Compensation[Compensation Logic]
        CQRS -->|requires| ES[Event Store/Source]
    end
```

### Soft Dependencies (Recommended)
```mermaid
graph LR
    subgraph "Work Better Together"
        CB[Circuit Breaker] -.->|enhances| RT[Retry]
        Cache -.->|supports| GD[Graceful Degradation]
        ES[Event Sourcing] -.->|enables| TT[Time Travel]
        CDC -.->|feeds| Search[Search Index]
        AG[API Gateway] -.->|benefits from| RL[Rate Limiting]
    end
```

## 🎯 Pattern Selection by Problem

### "My service is slow"
```mermaid
graph TD
    Slow[Service is Slow] --> Q1{Database<br/>queries slow?}
    
    Q1 -->|Yes| Cache[Add Caching]
    Cache --> CQRS[Consider CQRS]
    CQRS --> MV[Materialized Views]
    
    Q1 -->|No| Q2{Network<br/>latency?}
    
    Q2 -->|Yes| CDN[Add CDN]
    CDN --> EC[Edge Computing]
    
    Q2 -->|No| Q3{CPU bound?}
    
    Q3 -->|Yes| AS[Auto-scaling]
    AS --> LB[Load Balancer]
    
    Q3 -->|No| Profile[Profile Code]
```

### "My system keeps crashing"
```mermaid
graph TD
    Crash[System Crashes] --> Q1{Cascade<br/>failures?}
    
    Q1 -->|Yes| CB[Circuit Breaker]
    CB --> BH[Bulkhead]
    
    Q1 -->|No| Q2{Resource<br/>exhaustion?}
    
    Q2 -->|Yes| RL[Rate Limiting]
    RL --> AS[Auto-scaling]
    
    Q2 -->|No| Q3{Dependencies<br/>failing?}
    
    Q3 -->|Yes| TO[Timeouts]
    TO --> RT[Retry Logic]
    TO --> GD[Graceful Degradation]
```

## 🏗️ Building Blocks: Pattern Stacks

### The Reliability Stack
```
Foundation → Enhancement → Advanced
    ↓             ↓            ↓
Health Check → Timeout → Circuit Breaker
    +             +            +
  Retry      Backoff    Graceful Degradation
```

### The Performance Stack
```
Foundation → Enhancement → Advanced
    ↓             ↓            ↓
  Cache   →     CDN    →  Edge Computing
    +             +            +
Load Balancer  Sharding   Read Replicas
```

### The Data Stack
```
Foundation → Enhancement → Advanced
    ↓             ↓            ↓
Database   →   CQRS    → Event Sourcing
    +             +            +
  Backup        CDC         Saga
```

## 📈 Evolution Path

### Phase 1: Monolith
```mermaid
graph LR
    Client --> LB[Load Balancer]
    LB --> App[Monolith App]
    App --> DB[(Database)]
    App --> Cache[Cache]
```

### Phase 2: Simple Microservices
```mermaid
graph LR
    Client --> AG[API Gateway]
    AG --> Service1[Service 1]
    AG --> Service2[Service 2]
    AG --> Service3[Service 3]
    
    Service1 --> DB1[(DB 1)]
    Service2 --> DB2[(DB 2)]
    Service3 --> DB3[(DB 3)]
    
    Service1 -.-> Cache
    Service2 -.-> Cache
```

### Phase 3: Advanced Architecture
```mermaid
graph TB
    Client --> CDN
    CDN --> AG[API Gateway]
    
    AG --> SM[Service Mesh]
    
    SM --> Services[Microservices]
    Services --> ES[Event Sourcing]
    ES --> CQRS
    
    Services --> Saga[Saga Orchestration]
    
    CQRS --> Cache[Distributed Cache]
    ES --> MQ[Message Queue]
    MQ --> Analytics[Analytics Pipeline]
```

## 🔍 Pattern Discovery Questions

To find the right patterns, ask:

1. **What fails?** → Resilience patterns
2. **What's slow?** → Performance patterns
3. **What doesn't scale?** → Scaling patterns
4. **What's inconsistent?** → Data patterns
5. **What can't communicate?** → Communication patterns
6. **What needs coordination?** → Coordination patterns

---

*Use this relationship map to understand how patterns work together. Remember: patterns are most powerful when combined correctly.*