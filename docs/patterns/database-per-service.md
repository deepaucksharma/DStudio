---
title: Database per Service Pattern
description: Each microservice owns and encapsulates its own database instance
type: pattern
category: distributed-data
difficulty: intermediate
reading_time: 25 min
prerequisites: [microservices, data-modeling, distributed-systems, api-design]
when_to_use: Microservices architecture, team autonomy needed, polyglot persistence, independent scaling requirements
when_not_to_use: Small applications, tight data consistency needs, complex transactions, limited operational expertise
status: complete
last_updated: 2025-01-27
tags: [microservices, data-isolation, autonomy, polyglot-persistence]
excellence_tier: gold
pattern_status: recommended
introduced: 2012-01
current_relevance: mainstream
modern_examples:
  - company: Netflix
    implementation: "Each service owns its data in Cassandra, DynamoDB, or MySQL"
    scale: "1000+ microservices with independent databases"
  - company: Uber
    implementation: "Service-specific databases with Schemaless for flexibility"
    scale: "4000+ microservices, petabytes of data"
related_laws:
  - law1-failure
  - law4-tradeoffs
  - law5-epistemology
related_pillars:
  - state
  - truth
  - work
---

# Database per Service Pattern

!!! success "🥇 Gold Standard Pattern"
    **Recommended for microservices** • Enables true service autonomy
    
    This pattern is the foundation of successful microservices architectures, enabling independent deployment, scaling, and technology choices.

**Freedom through isolation, complexity through distribution**

## Visual Architecture

```mermaid
graph TB
    subgraph "Database per Service Architecture"
        subgraph "Order Service"
            OS[Order Service]
            ODB[(Order DB)]
            OS --> ODB
        end
        
        subgraph "Customer Service"
            CS[Customer Service]
            CDB[(Customer DB)]
            CS --> CDB
        end
        
        subgraph "Inventory Service"
            IS[Inventory Service]
            IDB[(Inventory DB)]
            IS --> IDB
        end
        
        subgraph "Payment Service"
            PS[Payment Service]
            PDB[(Payment DB)]
            PS --> PDB
        end
        
        API[API Gateway]
        
        API --> OS
        API --> CS
        API --> IS
        API --> PS
    end
    
    style OS fill:#90EE90
    style CS fill:#90EE90
    style IS fill:#90EE90
    style PS fill:#90EE90
```

## Benefits vs Challenges

| Benefits | Challenges | Mitigation Strategies |
|----------|------------|----------------------|
| **Service Autonomy** | Data consistency | Event-driven eventual consistency |
| **Independent Scaling** | Distributed queries | CQRS, materialized views |
| **Technology Freedom** | Distributed transactions | Saga pattern |
| **Team Independence** | Data duplication | Bounded contexts |
| **Fault Isolation** | Operational complexity | Service mesh, observability |
| **Security Boundaries** | Network latency | Caching, data locality |

## Data Consistency Strategies

```mermaid
graph TB
    subgraph "Consistency Approaches"
        E[Events]
        S[Saga]
        C[CQRS]
        O[Outbox]
        
        E --> Eventual[Eventual<br/>Consistency]
        S --> Distributed[Distributed<br/>Transactions]
        C --> Read[Read Model<br/>Synchronization]
        O --> Reliable[Reliable<br/>Publishing]
    end
    
    style Eventual fill:#87CEEB
    style Distributed fill:#FFE4B5
    style Read fill:#90EE90
    style Reliable fill:#E6E6FA
```

## Implementation Patterns

<div class="decision-box">
<h4>🎯 Key Implementation Decisions</h4>

1. **Data Ownership**
   - Service owns schema
   - No shared database access
   - API-only data access

2. **Cross-Service Queries**
   - API composition
   - CQRS read models
   - GraphQL federation

3. **Data Synchronization**
   - Event streaming
   - Change data capture
   - Scheduled syncs

4. **Transaction Management**
   - Saga orchestration
   - Event choreography
   - Compensating transactions
</div>

## Polyglot Persistence Example

```mermaid
graph LR
    subgraph "Service-Specific Databases"
        US[User Service] --> PG[(PostgreSQL<br/>Relational)]
        PS[Product Service] --> ES[(Elasticsearch<br/>Search)]
        CS[Cart Service] --> RD[(Redis<br/>Cache)]
        AS[Analytics Service] --> CH[(ClickHouse<br/>OLAP)]
        MS[Message Service] --> MG[(MongoDB<br/>Document)]
    end
    
    style PG fill:#336791
    style ES fill:#F5BA1A
    style RD fill:#DC382D
    style CH fill:#FFCC00
    style MG fill:#47A248
```

## Anti-Patterns to Avoid

<div class="failure-vignette">
<h4>💥 The Shared Database Backdoor</h4>

**What Happens**: 
- Teams start with database per service
- "Just this once" shared table access
- More services access shared tables
- Back to monolithic database coupling

**Result**: Lost service autonomy, deployment coordination

**Prevention**: 
- Strict API boundaries
- No database credentials sharing
- Automated compliance checks
</div>

## Data Query Patterns

| Pattern | Use Case | Implementation | Trade-offs |
|---------|----------|----------------|------------|
| **API Composition** | Simple joins | Gateway aggregates | Multiple network calls |
| **CQRS** | Complex queries | Dedicated read model | Eventual consistency |
| **Event Sourcing** | Audit trails | Event store | Complex rebuilding |
| **Data Lake** | Analytics | Batch ETL | Not real-time |
| **GraphQL Federation** | Flexible queries | Schema stitching | Complex setup |

## Migration Strategy from Shared Database

```mermaid
graph TD
    Start[Shared Database] --> Identify[Identify Service<br/>Boundaries]
    
    Identify --> API[Create Service<br/>APIs]
    
    API --> Strangler[Strangler Fig<br/>Pattern]
    
    Strangler --> Extract[Extract Service<br/>Data]
    
    Extract --> Sync[Dual Write/<br/>Sync Period]
    
    Sync --> Cutover[Cutover to<br/>Service DB]
    
    Cutover --> Remove[Remove Shared<br/>Access]
    
    style Start fill:#FF6B6B
    style Remove fill:#90EE90
```

## Handling Distributed Queries

<div class="truth-box">
<h4>💡 The JOIN Problem</h4>

**In Monolithic DB**:
```sql
SELECT * FROM orders o 
JOIN customers c ON o.customer_id = c.id
```

**In Microservices**:
1. Query Order Service
2. Extract customer IDs
3. Query Customer Service
4. Combine in application

**Better Approach**: Denormalize for read, normalize for write
</div>

## Real-World Implementation

```mermaid
graph TB
    subgraph "Netflix Architecture"
        subgraph "Viewing History"
            VH[Service] --> C1[(Cassandra)]
        end
        
        subgraph "Recommendations"
            RS[Service] --> C2[(Cassandra)]
        end
        
        subgraph "User Profiles"
            UP[Service] --> MY[(MySQL)]
        end
        
        subgraph "Search"
            SS[Service] --> ES[(Elasticsearch)]
        end
        
        K[Kafka Events] 
        
        VH --> K
        K --> RS
        K --> SS
    end
    
    style VH fill:#90EE90
    style RS fill:#90EE90
    style UP fill:#90EE90
    style SS fill:#90EE90
```

## Operational Considerations

- [ ] Each service has dedicated database credentials
- [ ] Automated database provisioning per service
- [ ] Service-specific backup strategies
- [ ] Independent scaling policies
- [ ] Separate monitoring and alerting
- [ ] Database version management per service
- [ ] Schema migration ownership
- [ ] Cost allocation per service

## Security Benefits

<div class="axiom-box">
<h4>🔒 Security Through Isolation</h4>

**Database per Service Security**:
- Blast radius containment
- Principle of least privilege
- Service-specific encryption
- Audit trails per service
- Compliance boundaries

**vs Shared Database**:
- One breach = all data exposed
- Shared credentials
- Complex access control
</div>

## Related Patterns

- [Saga](saga.md) - Distributed transactions
- [CQRS](cqrs.md) - Query separation
- [Event Sourcing](event-sourcing.md) - Event-driven consistency
- [API Gateway](api-gateway.md) - Query aggregation
- [Outbox](outbox.md) - Reliable event publishing
- [Shared Database](shared-database.md) - The anti-pattern to avoid