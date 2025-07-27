---
title: Shared Database Pattern
description: Multiple services share a single database instance for data persistence
type: pattern
category: distributed-data
difficulty: beginner
reading_time: 15 min
prerequisites: [database-basics, service-architecture, data-modeling]
when_to_use: Small systems, tight budgets, simple data sharing needs, monolith-to-microservices transition
when_not_to_use: Microservices architecture, high scale systems, when services need autonomy, polyglot persistence requirements
status: complete
last_updated: 2025-01-27
tags: [anti-pattern, legacy, data-coupling, monolithic]
excellence_tier: bronze
pattern_status: legacy
introduced: 1990-01
current_relevance: declining
modern_alternatives: 
  - "Database per Service pattern"
  - "Event-driven data sharing"
  - "API-based data access"
  - "CQRS with separate read models"
deprecation_reason: "Creates tight coupling between services, violates microservices principles, causes scaling bottlenecks, and prevents independent deployments"
migration_guide: "[Migrate to Database per Service](../excellence/migrations/shared-database-to-microservices.md)"
---

# Shared Database Pattern

!!! danger "🥉 Bronze Tier Pattern"
    **Legacy Pattern** • Consider modern alternatives
    
    While still in use in legacy systems, this pattern has been superseded by database-per-service and event-driven architectures. See migration guides for transitioning to modern approaches.

**The anti-pattern that refuses to die**

## Visual Architecture

```mermaid
graph TB
    subgraph "Services"
        S1[Order Service]
        S2[Inventory Service]
        S3[Customer Service]
        S4[Payment Service]
    end
    
    subgraph "Shared Database"
        DB[(Single Database)]
        T1[Orders Table]
        T2[Inventory Table]
        T3[Customers Table]
        T4[Payments Table]
    end
    
    S1 --> DB
    S2 --> DB
    S3 --> DB
    S4 --> DB
    
    DB --> T1
    DB --> T2
    DB --> T3
    DB --> T4
    
    style DB fill:#FF6B6B
    style S1 fill:#FFE4B5
    style S2 fill:#FFE4B5
    style S3 fill:#FFE4B5
    style S4 fill:#FFE4B5
```

## Why This Pattern is Problematic

| Problem | Impact | Modern Solution |
|---------|--------|-----------------|
| **Tight Coupling** | Services can't evolve independently | Database per service |
| **No Autonomy** | Teams block each other | API contracts |
| **Scaling Bottleneck** | All services hit same DB | Distributed data |
| **Schema Conflicts** | Version coordination nightmare | Service ownership |
| **Performance Issues** | Noisy neighbor problems | Isolated resources |
| **Testing Complexity** | Can't test in isolation | Service virtualization |

## Common Symptoms of Shared Database Problems

<div class="failure-vignette">
<h4>💥 The Deployment Coordination Dance</h4>

**What Happens**: 
- Team A needs to add a column
- Team B's code breaks with new column
- Team C is in the middle of a release
- All teams must coordinate deployment

**Result**: 3-week deployment cycles, midnight releases

**Better Approach**: Each service owns its data and schema
</div>

## Migration Strategy

```mermaid
graph LR
    subgraph "Phase 1: Identify"
        A1[Map Service<br/>Dependencies]
        A2[Identify<br/>Shared Tables]
        A3[Find Cross-Service<br/>Queries]
    end
    
    subgraph "Phase 2: Decouple"
        B1[Add Service<br/>APIs]
        B2[Replace Direct<br/>DB Access]
        B3[Implement<br/>Events]
    end
    
    subgraph "Phase 3: Separate"
        C1[Create Service<br/>Databases]
        C2[Migrate Data]
        C3[Remove Shared<br/>Access]
    end
    
    A1 --> B1
    B1 --> C1
    
    style A1 fill:#FFE4B5
    style B1 fill:#87CEEB
    style C1 fill:#90EE90
```

## When Shared Database Might Be Acceptable

<div class="decision-box">
<h4>🎯 Limited Acceptable Use Cases</h4>

1. **Transitional State**
   - During monolith decomposition
   - Temporary measure with clear timeline

2. **Read-Only Analytics**
   - Shared read replicas for reporting
   - No write operations from services

3. **Legacy System Constraints**
   - When refactoring cost exceeds benefit
   - With clear isolation boundaries

**Even then**: Plan for eventual separation
</div>

## Modern Alternatives Comparison

| Pattern | Data Consistency | Autonomy | Complexity | Use When |
|---------|-----------------|----------|------------|----------|
| **Database per Service** | Eventual | High | Medium | Default for microservices |
| **Event Sourcing** | Eventual | High | High | Audit requirements |
| **CQRS** | Eventual | High | High | Complex queries |
| **API Gateway** | Request-time | Medium | Low | Simple data needs |
| **Data Mesh** | Federated | Very High | Very High | Large organizations |

## Anti-Pattern Indicators

- [ ] Multiple services directly query same tables
- [ ] Schema changes require multi-team coordination  
- [ ] "God tables" with 50+ columns
- [ ] Database becomes single point of failure
- [ ] Can't scale services independently
- [ ] Test data conflicts between teams
- [ ] Performance degradation affects all services
- [ ] Security boundaries are unclear

## Related Patterns

- [Database per Service](database-per-service.md) - The correct approach
- [Event-Driven](event-driven.md) - For data synchronization
- [API Gateway](api-gateway.md) - For data aggregation
- [CQRS](cqrs.md) - For query separation
- [Saga](saga.md) - For distributed transactions