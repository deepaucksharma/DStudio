---
title: CQRS Pattern
description: Command Query Responsibility Segregation for scalable systems
---

# CQRS Pattern

## The Complete Blueprint

Command Query Responsibility Segregation (CQRS) is an architectural pattern that separates read and write operations into distinct models, optimizing each for their specific concerns. Instead of using a single data model for both reading and writing, CQRS uses separate command models (optimized for writes, business logic, and consistency) and query models (optimized for reads, denormalized for fast queries). This separation enables independent scaling, different consistency requirements, and specialized optimization for each operation type.

```mermaid
graph TB
    subgraph "CQRS Architecture Blueprint"
        subgraph "Client Applications"
            WebApp[Web Application]
            MobileApp[Mobile App]
            API[External API]
        end
        
        subgraph "Command Side (Write)"
            CommandAPI[Command API]
            CommandHandlers[Command Handlers]
            DomainModels[Domain Models/Aggregates]
            WriteDB[Write Database<br/>Normalized, ACID]
        end
        
        subgraph "Event Infrastructure"
            EventBus[Event Bus]
            EventStore[Event Store]
        end
        
        subgraph "Query Side (Read)"
            QueryAPI[Query API]
            ReadModels[Read Models/Views]
            ReadDB1[Read DB 1<br/>Denormalized]
            ReadDB2[Read DB 2<br/>Search Index]
            ReadDB3[Read DB 3<br/>Analytics]
        end
        
        subgraph "Synchronization"
            EventHandlers[Event Handlers]
            Projections[Projection Builders]
        end
        
        WebApp -->|Commands| CommandAPI
        MobileApp -->|Commands| CommandAPI
        API -->|Commands| CommandAPI
        
        WebApp -->|Queries| QueryAPI
        MobileApp -->|Queries| QueryAPI
        API -->|Queries| QueryAPI
        
        CommandAPI --> CommandHandlers
        CommandHandlers --> DomainModels
        DomainModels --> WriteDB
        DomainModels -->|Domain Events| EventBus
        
        EventBus --> EventStore
        EventBus --> EventHandlers
        EventHandlers --> Projections
        Projections --> ReadDB1
        Projections --> ReadDB2
        Projections --> ReadDB3
        
        QueryAPI --> ReadModels
        ReadModels --> ReadDB1
        ReadModels --> ReadDB2
        ReadModels --> ReadDB3
        
        style CommandAPI fill:#FF5722,stroke:#D84315,stroke-width:2px
        style QueryAPI fill:#4CAF50,stroke:#388E3C,stroke-width:2px
        style EventBus fill:#2196F3,stroke:#1976D2,stroke-width:3px
        style WriteDB fill:#FF9800,stroke:#F57C00,stroke-width:2px
        style ReadDB1 fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px
    end
```

### What You'll Master

- **Command-Query Separation**: Design systems with clear boundaries between write operations (commands) and read operations (queries)
- **Independent Scaling**: Scale read and write sides independently based on different load patterns and performance requirements
- **Optimized Data Models**: Create write models focused on business rules and read models optimized for specific query patterns
- **Event-Driven Synchronization**: Implement reliable mechanisms to keep read models eventually consistent with write models
- **Polyglot Persistence**: Use different databases optimized for writes vs reads (SQL for writes, NoSQL for reads, search engines for full-text)
- **Complex Query Optimization**: Build sophisticated read models that support complex reporting, analytics, and search requirements

CQRS pattern separates read and write models

## See Also

- [Eventual Consistency](/pattern-library/data-management/eventual-consistency)
- [Event Streaming](/pattern-library/architecture/event-streaming)
- [Rate Limiting Pattern](/pattern-library/scaling/rate-limiting)
