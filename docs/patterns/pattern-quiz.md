---
title: Pattern Catalog Quiz
description: "Interactive quiz to test your understanding of distributed system patterns and their appropriate use cases"
type: pattern
difficulty: intermediate
reading_time: 5 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Pattern Catalog Quiz**

# Pattern Catalog Quiz

**Test Your Pattern Knowledge**

## Quiz Questions

### 1. Your payment service times out occasionally. You should implement:
   - a) Bulkhead isolation
   - b) Circuit breaker ✓
   - c) Event sourcing
   - d) Service mesh

**Answer: b) Circuit breaker**
*Explanation: Circuit breakers prevent cascading failures by failing fast when a service is struggling.*

### 2. You need to sync data from OLTP to OLAP. Best pattern:
   - a) Saga
   - b) CQRS
   - c) CDC ✓
   - d) GraphQL

**Answer: c) CDC (Change Data Capture)**
*Explanation: CDC captures database changes in real-time for streaming to analytics systems.*

### 3. Cross-region users complain about latency. Primary solution:
   - a) Bigger servers
   - b) Geo-replication ✓
   - c) Circuit breakers
   - d) Sharding

**Answer: b) Geo-replication**
*Explanation: Geo-replication puts data closer to users, reducing latency from geographic distance.*

### 4. Your monolith can't scale anymore. First step:
   - a) Microservices
   - b) Serverless
   - c) Identify boundaries ✓
   - d) Add cache

**Answer: c) Identify boundaries**
*Explanation: Before splitting a monolith, you must identify proper service boundaries based on business domains.*

### 5. Debugging distributed requests is hard. You need:
   - a) More logs
   - b) Distributed tracing ✓
   - c) Better dashboards
   - d) Service mesh

**Answer: b) Distributed tracing**
*Explanation: Distributed tracing follows requests across multiple services to understand flow and latency.*

### 6. Database writes are becoming slow. Consider:
   - a) CQRS ✓
   - b) GraphQL
   - c) Serverless
   - d) Circuit breaker

**Answer: a) CQRS**
*Explanation: CQRS separates read and write models, allowing optimization of each independently.*

### 7. You have N services calling each other. Complexity reducer:
   - a) Service mesh ✓
   - b) Sharding
   - c) Caching
   - d) CDC

**Answer: a) Service mesh**
*Explanation: Service mesh handles cross-cutting concerns like discovery, security, and observability uniformly.*

### 8. Batch job costs are too high. Switch to:
   - a) Reserved instances
   - b) Spot instances ✓
   - c) Bigger instances
   - d) Serverless

**Answer: b) Spot instances**
*Explanation: Spot instances offer up to 90% savings for interruptible batch workloads.*

### 9. Services keep calling dead dependencies. Implement:
   - a) Retries
   - b) Circuit breaker ✓
   - c) Saga
   - d) Bulkhead

**Answer: b) Circuit breaker**
*Explanation: Circuit breakers stop calling failing services, preventing resource exhaustion.*

### 10. Need exactly-once payment processing. Use:
   - a) Retries
   - b) Idempotency keys ✓
   - c) Circuit breakers
   - d) Event sourcing

**Answer: b) Idempotency keys**
*Explanation: Idempotency keys ensure operations can be safely retried without duplication.*

## Scoring Guide

- **8-10 correct**: Pattern Master - You deeply understand distributed patterns
- **6-7 correct**: Pattern Practitioner - Good grasp, some areas to review
- **4-5 correct**: Pattern Learner - Keep studying the patterns
- **<4 correct**: Review patterns again - Focus on understanding the problems each pattern solves

## Key Takeaways

1. **Match pattern to problem**: Each pattern solves specific distributed systems challenges
2. **Understand trade-offs**: Every pattern has costs and complexity
3. **Combine patterns**: Real systems often need multiple patterns working together
4. **Start simple**: Don't over-engineer; add patterns as problems emerge
5. **Measure impact**: Validate that patterns actually solve your problems

## Pattern Selection Matrix

| Problem | Primary Pattern | Supporting Patterns |
|---------|----------------|-------------------|
| Service failures | Circuit Breaker | Retry, Bulkhead |
| High latency | Caching | CDN, Geo-replication |
| Data sync | CDC | Event Sourcing, CQRS |
| Complex transactions | Saga | Event Sourcing |
| Service communication | Service Mesh | Circuit Breaker |
| Variable load | Serverless | Auto-scaling |
| Global users | Geo-replication | Edge Computing |
| Cost control | FinOps | Spot Instances |

## Next Steps

Having tested your pattern knowledge, Part IV will provide the mathematical toolkit to:
- Calculate theoretical limits
- Model system behavior
- Predict scaling characteristics
- Optimize cost-performance trade-offs
- Capacity plan with confidence

The math that matters for distributed systems...

---

**Previous**: [← Outbox Pattern](outbox.md) | **Next**: [Queues & Stream-Processing →](queues-streaming.md)
