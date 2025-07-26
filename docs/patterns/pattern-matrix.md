---
title: Pattern Selection Matrix
description: Visual decision framework for choosing distributed system patterns
type: reference
category: patterns
difficulty: intermediate
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-01-26
---

# Pattern Selection Matrix

!!! abstract "Quick Decision Framework"
    🎯 **Find your pattern in 10 seconds using our visual matrices**

## Master Pattern Matrix

```mermaid
graph TD
    subgraph "Start Here"
        Q[What's breaking?]
    end
    
    subgraph "Failure Domain"
        Q -->|External APIs| CB[Circuit Breaker]
        Q -->|Database overload| CACHE[Caching]
        Q -->|Service discovery| SM[Service Mesh]
        Q -->|Data inconsistency| ES[Event Sourcing]
        Q -->|Transaction failures| SAGA[Saga Pattern]
    end
    
    subgraph "Complexity Level"
        CB -->|"⭐⭐"| CB_D[2 days to implement]
        CACHE -->|"⭐"| CACHE_D[1 day to implement]
        SM -->|"⭐⭐⭐⭐⭐"| SM_D[1 month to implement]
        ES -->|"⭐⭐⭐⭐"| ES_D[2 weeks to implement]
        SAGA -->|"⭐⭐⭐"| SAGA_D[1 week to implement]
    end
    
    style CB fill:#9f6
    style CACHE fill:#9f6
    style SM fill:#f96
    style ES fill:#fc6
    style SAGA fill:#fc6
```

## Pattern Decision Table

| Your Problem | Best Pattern | Complexity | Time to Value | When NOT to Use |
|--------------|--------------|------------|---------------|-----------------|
| **External service failing** | Circuit Breaker | ⭐⭐ | 1 day | Internal method calls |
| **Database overloaded** | Cache-Aside | ⭐ | 4 hours | Write-heavy (>50%) |
| **Distributed transactions** | Saga | ⭐⭐⭐ | 1 week | Can use single DB |
| **Need audit trail** | Event Sourcing | ⭐⭐⭐⭐ | 2 weeks | Simple CRUD |
| **Service discovery chaos** | Service Mesh | ⭐⭐⭐⭐⭐ | 1 month | <10 services |
| **Inconsistent reads** | CQRS | ⭐⭐⭐ | 1 week | Simple domain |
| **Traffic spikes** | Rate Limiting | ⭐⭐ | 1 day | Internal services |
| **Cascading failures** | Bulkhead | ⭐⭐ | 2 days | Single service |

## Visual Pattern Relationships

```mermaid
graph LR
    subgraph "Resilience Patterns"
        CB[Circuit Breaker] --> RT[Retry]
        RT --> BH[Bulkhead]
        BH --> TO[Timeout]
    end
    
    subgraph "Data Patterns"
        CA[Cache] --> ES[Event Sourcing]
        ES --> CQRS[CQRS]
        CQRS --> MS[Materialized View]
    end
    
    subgraph "Coordination"
        SAGA[Saga] --> 2PC[2PC]
        2PC --> CON[Consensus]
        CON --> LOCK[Distributed Lock]
    end
    
    CB -.->|protects| CA
    SAGA -.->|uses| CB
    ES -.->|enables| SAGA
    
    style CB fill:#9f6
    style CA fill:#69f
    style SAGA fill:#fc6
```

## Pattern Compatibility Matrix

| Pattern A | Pattern B | Compatibility | Why |
|-----------|-----------|---------------|-----|
| Circuit Breaker | Retry | ✅ Excellent | CB prevents retry storms |
| Cache | Event Sourcing | ✅ Good | ES can populate cache |
| Saga | 2PC | ❌ Avoid | Conflicting approaches |
| Service Mesh | API Gateway | ⚠️ Overlap | Redundant features |
| CQRS | Cache | ✅ Excellent | Natural fit |
| Rate Limiting | Circuit Breaker | ✅ Excellent | Defense in depth |

## Implementation Effort vs Impact

```mermaid
scatter
    title "Pattern ROI Analysis"
    x-axis "Implementation Days" [0, 30]
    y-axis "Impact Score" [0, 10]
    
    "Cache-Aside": [1, 8]
    "Circuit Breaker": [2, 9]
    "Retry Logic": [0.5, 6]
    "Rate Limiting": [1, 7]
    "Saga": [7, 7]
    "Event Sourcing": [14, 8]
    "Service Mesh": [30, 9]
    "CQRS": [7, 6]
```

## Quick Decision Rules

### 🚀 Start With These (Easy Wins)
1. **Circuit Breaker** - Always add to external calls
2. **Cache-Aside** - If read/write ratio > 10:1
3. **Retry with Backoff** - For transient failures
4. **Health Checks** - Basic but critical

### ⚠️ Think Twice Before These
1. **Service Mesh** - Massive operational overhead
2. **Event Sourcing** - Complex queries, storage cost
3. **2PC** - Usually wrong choice
4. **Blockchain** - Almost never the answer

### 🎯 Pattern Combinations That Work
- **The Reliability Stack**: Circuit Breaker + Retry + Timeout + Bulkhead
- **The Performance Stack**: Cache + CDN + Load Balancer + Sharding
- **The Consistency Stack**: Event Sourcing + CQRS + Saga
- **The Scale Stack**: Service Mesh + API Gateway + Message Queue

## Migration Paths

```mermaid
graph LR
    subgraph "Evolution Journey"
        M[Monolith] --> M_LB[+ Load Balancer]
        M_LB --> M_C[+ Cache]
        M_C --> M_MS[→ Microservices]
        M_MS --> M_SM[+ Service Mesh]
        M_SM --> M_ES[+ Event Driven]
    end
    
    subgraph "Complexity"
        C1[Low] --> C2[Medium] --> C3[High] --> C4[Very High] --> C5[Expert]
    end
    
    M -.-> C1
    M_LB -.-> C2
    M_C -.-> C2
    M_MS -.-> C3
    M_SM -.-> C4
    M_ES -.-> C5
```

## Pattern Anti-Patterns

| Anti-Pattern | Why It's Bad | What to Do Instead |
|--------------|--------------|-------------------|
| **Distributed Monolith** | Complexity without benefits | True service boundaries |
| **Sync Everything** | Cascading failures | Async where possible |
| **No Circuit Breakers** | One service kills all | Always protect calls |
| **Cache Everything** | Stale data, complexity | Cache strategically |
| **Over-engineering** | Months to deliver | Start simple, evolve |

## Next Steps

1. **Identify your bottleneck** using the problem column
2. **Check complexity** against your team's skills
3. **Estimate effort** using the time column
4. **Start simple** with easy wins
5. **Evolve gradually** following migration paths

---

[← Back to Patterns](/patterns/) | [Pattern Details →](/patterns/circuit-breaker/)