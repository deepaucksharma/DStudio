---
title: CQRS (Command Query Responsibility Segregation)
description: Separate read and write models for optimized performance and scalability
type: pattern
category: architectural
difficulty: advanced
reading_time: 30 min
prerequisites: 
when_to_use: High-performance reads, complex domain logic, different read/write scaling needs
when_not_to_use: Simple CRUD applications, low traffic systems, small teams
status: complete
last_updated: 2025-07-25
---

# CQRS (Command Query Responsibility Segregation)

<div class="pattern-card">
  <span class="pattern-card__category">Architectural Pattern</span>
  <div class="pattern-card__content">
    <p class="pattern-card__description">
      Separate read and write models to independently optimize complex business operations and high-performance queries.
    </p>
    <div class="pattern-card__laws">
      <span class="pattern-card__law-badge">Law 2: Asynchronous Reality</span>
      <span class="pattern-card__law-badge">Law 4: Multidimensional Optimization</span>
    </div>
  </div>
</div>

## Problem Statement

**How can we optimize both complex business operations and high-performance queries when they have fundamentally different requirements?**

!!! tip "When to Use This Pattern"
    | Scenario | Use CQRS | Alternative |
    |----------|----------|-------------|
    | Read/write ratio > 10:1 | ✅ Yes | Consider read replicas |
    | Complex domain logic | ✅ Yes | Traditional layered architecture |
    | Different scaling needs | ✅ Yes | Vertical scaling |
    | Multiple query views needed | ✅ Yes | Database views |
    | Audit trail required | ✅ Yes | Simple logging |
    | Simple CRUD operations | ❌ No | Traditional CRUD |
    | Small teams (< 3 developers) | ❌ No | Monolithic architecture |
    | Low traffic (< 1K requests/day) | ❌ No | Simple database |

## Solution Architecture

```mermaid
graph TB
    subgraph "Write Side (Command)"
        CMD[Commands] --> CH[Command Handlers]
        CH --> DM[Domain Model]
        DM --> ES[Event Store]
        ES --> EB[Event Bus]
    end
    
    subgraph "Read Side (Query)"
        EB --> P1[User View Projector]
        EB --> P2[Search Projector]
        EB --> P3[Analytics Projector]
        
        P1 --> RM1[(User Views)]
        P2 --> RM2[(Search Index)]
        P3 --> RM3[(Analytics DB)]
        
        QH[Query Handlers] --> RM1
        QH --> RM2
        QH --> RM3
    end
    
    U[Users] --> CMD
    U --> QH
    
    style DM fill:#e3f2fd
    style ES fill:#bbdefb
    style EB fill:#90caf9
    style RM1 fill:#c8e6c9
    style RM2 fill:#c8e6c9
    style RM3 fill:#c8e6c9
```

## Implementation Considerations

### Trade-offs

<table class="responsive-table">
<thead>
  <tr>
    <th>Aspect</th>
    <th>Benefit</th>
    <th>Cost</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td data-label="Aspect">Performance</td>
    <td data-label="Benefit">Independent optimization</td>
    <td data-label="Cost">Eventual consistency</td>
  </tr>
  <tr>
    <td data-label="Aspect">Scalability</td>
    <td data-label="Benefit">Scale reads/writes separately</td>
    <td data-label="Cost">Infrastructure complexity</td>
  </tr>
  <tr>
    <td data-label="Aspect">Development</td>
    <td data-label="Benefit">Clear separation of concerns</td>
    <td data-label="Cost">Event synchronization logic</td>
  </tr>
  <tr>
    <td data-label="Aspect">Query Flexibility</td>
    <td data-label="Benefit">Multiple optimized views</td>
    <td data-label="Cost">Projection maintenance</td>
  </tr>
</tbody>
</table>

### Key Metrics

<div class="grid" markdown>
  <div class="card">
    <div class="card__title">Write Latency</div>
    <div class="card__description">P99: < 200ms</div>
  </div>
  <div class="card">
    <div class="card__title">Read Latency</div>
    <div class="card__description">P99: < 50ms</div>
  </div>
  <div class="card">
    <div class="card__title">Projection Lag</div>
    <div class="card__description">< 5 seconds</div>
  </div>
  <div class="card">
    <div class="card__title">Consistency</div>
    <div class="card__description">Eventually consistent</div>
  </div>
</div>

## Real-World Examples

!!! abstract "Production Implementation"
    - **LinkedIn**: Used CQRS for their feed system, handling 1B+ reads/day with < 50ms P99 latency
    - **Netflix**: Implemented CQRS for their viewing history, enabling personalized recommendations at scale
    - **Uber**: Applied CQRS to their trip data, supporting real-time analytics while maintaining transactional integrity
    - **Amazon**: Uses CQRS for product catalog, serving millions of queries while processing inventory updates

## Common Pitfalls

!!! danger "What Can Go Wrong"
    1. **Synchronous Projections**: Updating read models in write transaction eliminates performance benefits. Use asynchronous event processing instead.
    2. **Missing Event Versioning**: Schema changes break event replay. Implement event versioning from day one.
    3. **Over-Engineering**: Applying CQRS to simple CRUD operations adds unnecessary complexity. Start with traditional architecture for simple domains.
    4. **Ignoring Consistency Requirements**: Some operations need immediate consistency. Use consistency tokens or polling for critical reads.
    5. **Poor Error Handling**: Failed projections create data inconsistencies. Implement dead letter queues and replay mechanisms.

## Related Patterns

- [Event Sourcing](event-sourcing.md) - Natural companion for event-driven CQRS
- [Saga Pattern](saga.md) - Handling distributed transactions with CQRS
- [Event-Driven Architecture](event-driven.md) - Foundation for CQRS communication
- [Service Mesh](service-mesh.md) - Infrastructure for distributed CQRS systems

## Further Reading

- [Greg Young's CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf) - Original CQRS papers
- [Martin Fowler's CQRS Article](https://martinfowler.com/bliki/CQRS.html) - Clear introduction
- [Microsoft CQRS Journey](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10)) - Detailed implementation guide



























