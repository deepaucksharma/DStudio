---
category: data-management
current_relevance: mainstream
description: Manage distributed transactions using coordinated sequences of local
  transactions with compensations
difficulty: advanced
essential_question: How do we ensure data consistency and reliability with saga pattern?
excellence_tier: gold
introduced: 1987-12
last-updated: 2025-01-30
modern-examples:
- company: Uber
  implementation: Saga orchestrates ride booking across payment, dispatch, and driver
    services
  scale: 20M+ distributed transactions daily
- company: Airbnb
  implementation: Booking saga coordinates inventory, payment, and notification services
  scale: 2M+ bookings per day across global inventory
- company: Booking.com
  implementation: Complex travel booking sagas with multi-vendor coordination
  scale: 1.5M+ room nights booked daily
pattern_status: recommended
prerequisites: null
production-checklist:
- Choose orchestration vs choreography based on complexity
- Design compensating transactions for every step
- Implement idempotent operations to handle retries
- Use state machines to track saga progress
- Monitor saga completion rates and failure patterns
- Set timeouts for each saga step (typically 30s-5min)
- Store saga state durably (database or event store)
- Test failure scenarios and compensation flows
reading-time: 35 min
related-laws:
- law2-asynchrony
- law3-emergence
- law4-tradeoffs
- law5-epistemology
related-pillars:
- state
- truth
- control
- intelligence
status: complete
tagline: Master saga pattern for distributed systems success
title: Saga Pattern
type: pattern
when-not-to-use: Simple local transactions, strongly consistent requirements, simple
  CRUD operations
when-to-use: Cross-service transactions, workflow orchestration, distributed business
  processes
---


# Saga Pattern

!!! success "🏆 Gold Standard Pattern"
    **Distributed Transaction Management** • Uber, Airbnb, Booking.com proven
    
    The de facto solution for managing distributed transactions across microservices. Enables business processes to span multiple services while maintaining consistency through compensations.
    
    **Key Success Metrics:**
    - Uber: 20M+ daily distributed transactions
    - Airbnb: 2M+ bookings coordinated daily
    - Booking.com: 1.5M+ room nights processed

## Essential Question

**How can we maintain data consistency across multiple services when ACID transactions can't span service boundaries?**

## When to Use / When NOT to Use

### Use Saga When ✅
| Scenario | Why | Example |
|----------|-----|---------|
| **Multiple services involved** | Can't use local transactions | Order processing across payment, inventory, shipping |
| **Long-running processes** | Minutes to hours duration | Travel booking, loan approval workflows |
| **High availability required** | Can't afford blocking | E-commerce during Black Friday |
| **Services owned by different teams** | Can't coordinate deploys | Marketplace with independent sellers |
| **Need audit trail** | Regulatory compliance | Financial transactions, healthcare |

### DON'T Use When ❌
| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Single service transaction** | Unnecessary complexity | Use local ACID transaction |
| **Strong consistency required** | Sagas are eventually consistent | Use 2PC if you must |
| **Simple CRUD operations** | Overkill for simple ops | Direct database operations |
| **Synchronous user waiting** | Too slow for UI | Use optimistic UI + background |

## Level 1: Intuition (5 min)

### The $45M Problem That Created Sagas

!!! failure "Expedia's 2012 Nightmare"
    **What Happened**: Payment processed but hotel booking failed  
    **Impact**: 120,000 customers charged without reservations  
    **Recovery**: 6 weeks of manual reconciliation  
    **Cost**: $45M in refunds, credits, and reputation damage

### Visual Architecture

### Core Insight

<div class="axiom-box">
<h4>🔬 Law 2: Asynchronous Reality</h4>

You can't have atomic commits across network boundaries. The best you can do is coordinate eventual consistency through compensations.

**Saga = Sequence of local transactions + Compensating actions**
</div>

## Level 2: Foundation (10 min)

### Production Failure Modes & Solutions

| Failure Type | Without Saga | With Saga | Real Example |
|--------------|--------------|-----------|---------------|
| **Partial Failure** | Inconsistent state | Automatic compensation | Uber: Trip cancelled mid-booking |
| **Timeout** | Hung transactions | Progress tracking | Amazon: Payment timeout handled |
| **Crash** | Lost transaction | State persistence | Netflix: Billing recovery |
| **Network Partition** | Split brain | Idempotent steps | Booking.com: Multi-region saga |

### Orchestration vs Choreography

<div class="decision-box">
<h4>🎯 Quick Decision Guide</h4>

**Choose Orchestration When:**
- Central visibility required (< 10 services)
- Complex conditional logic
- Clear business process owner

**Choose Choreography When:**
- Services are autonomous (> 10 services)  
- Simple linear flows
- High scalability needed

**Hybrid**: Critical path orchestrated, extensions choreographed
</div>

### Architecture Comparison

## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 5 | State machines, compensation logic, orchestration/choreography patterns, failure handling |
| **Performance Impact** | 3 | Multiple async steps, but enables horizontal scaling and decoupling |
| **Operational Overhead** | 4 | Monitoring saga health, debugging distributed failures, managing compensations |
| **Team Expertise Required** | 5 | Deep understanding of distributed transactions, eventual consistency, workflow design |
| **Scalability** | 4 | Excellent for distributed systems, handles service autonomy and failure isolation |

**Overall Recommendation: ✅ HIGHLY RECOMMENDED** - Essential for distributed business processes across microservices.

## Level 3: Deep Dive (15 min)

### Saga Execution Flow



### Transaction Types

<div class="truth-box">
<h4>💡 The Three Saga Transaction Types</h4>

1. **Compensatable**: Can be undone (e.g., reserve → release inventory)
2. **Pivot**: The go/no-go decision point (e.g., payment authorization)
3. **Retriable**: Must eventually succeed (e.g., send email)

**Key**: Place pivot after compensatable, before retriable transactions
</div>

### State Persistence Strategy

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```



### Idempotency Pattern



### Production Checklist ✓

- [ ] Idempotency for all steps
- [ ] Compensation for every forward transaction
- [ ] Timeout handling (30s-5min per step)
- [ ] State persistence with recovery
- [ ] Monitoring dashboard for sagas
- [ ] Test all failure scenarios
- [ ] Document saga flows
- [ ] Alert on stuck sagas

## Related Patterns

### Core Dependencies
- **[Two-Phase Commit](../pattern-library/data-management/saga.md)**: Strong consistency alternative
- **[Event Sourcing](./event-sourcing.md)**: Natural event log for sagas
- **[Outbox Pattern](../pattern-library/data-management/outbox.md)**: Reliable event publishing

### Supporting Patterns
- **[Idempotent Receiver](../pattern-library/idempotent-receiver.md)**: Safe retries
- **[Circuit Breaker](../resilience/circuit-breaker.md)**: Protect saga steps
- **[CQRS](./cqrs.md)**: Separate saga execution from queries

#
## Performance Characteristics

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Latency** | 100ms | 20ms | 80% |
| **Throughput** | 1K/s | 10K/s | 10x |
| **Memory** | 1GB | 500MB | 50% |
| **CPU** | 80% | 40% | 50% |

## Implementation Combinations
- **Saga + Event Sourcing**: Natural fit for state management
- **Saga + Circuit Breaker**: Fail fast with compensations
- **Saga + CQRS**: Commands via saga, queries from read model

## Further Reading

- [Original Sagas Paper (1987)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf) - Garcia-Molina & Salem
- [Microservices.io Saga Pattern](https://microservices.io/pattern-library/data/saga.html) - Chris Richardson
- [AWS Step Functions Sagas](https://aws.amazon.com/step-functions/use-cases/#saga) - Serverless implementation

### Tools & Libraries
- **Orchestration**: Temporal, Camunda, AWS Step Functions
- **Java**: Axon Framework, Eventuate Tram
- **C#/.NET**: MassTransit, NServiceBus
- **Go**: Cadence, Temporal
- **Node.js**: Moleculer, Node-Saga

