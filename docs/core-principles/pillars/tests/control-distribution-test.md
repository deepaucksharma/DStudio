---
title: "Pillar 4: Control Distribution - Quick Assessment"
description: Objective assessment on coordinating actions and decisions across distributed components
type: test
difficulty: advanced
time_limit: 25 minutes
question_count: 25
passing_score: 75
---

# Pillar 4: Control Distribution

⏱️ **Time:** 25 minutes | 📝 **25 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Coordinating actions, managing decisions, and handling control flow across distributed components while maintaining system coherence.

---

## Section A: Fundamentals (10 questions)

### 1. [One-line] Orchestration vs Choreography
Name the key difference between orchestration and choreography.
- **Answer:** Central coordinator vs peer-to-peer events

### 2. [Multiple Choice] Control Plane Role
The control plane in distributed systems handles:
- A) Data processing
- B) Configuration and coordination ✓
- C) User traffic
- D) Storage only

### 3. [True/False] Centralized Control
Fully centralized control always provides better consistency.
- **Answer:** True
- **Reason:** Single point of control eliminates coordination issues.

### 4. [Fill in Blank] _______ election ensures only one node acts as coordinator.
- **Answer:** Leader

### 5. [Pattern Matching] Coordination Patterns
Match pattern to characteristic:
1. Primary-replica    A. Peer equality
2. Token ring        B. Hierarchical control
3. Gossip protocol   C. Sequential access
4. Mesh             D. Epidemic spread

**Answers:** 1-B, 2-C, 3-D, 4-A

### 6. [Multiple Choice] Distributed Lock Purpose
Distributed locks primarily prevent:
- A) Network failures
- B) Concurrent modifications ✓
- C) Data loss
- D) Performance issues

### 7. [Calculate] Token Ring Nodes
In a token ring with 10 nodes, maximum hops for token?
- **Answer:** 9 hops

### 8. [True/False] Coordination-free
Coordination-free algorithms always have lower latency.
- **Answer:** True
- **Reason:** No synchronization overhead.

### 9. [One-line] Saga Pattern
What problem does the Saga pattern solve?
- **Answer:** Distributed transactions without 2PC

### 10. [Fill in Blank] Circuit breakers prevent _______ failures.
- **Answer:** cascading

---

## Section B: Implementation (10 questions)

### 11. [Multiple Choice] Service Mesh Control
Service mesh primarily provides:
- A) Data storage
- B) Traffic management and observability ✓
- C) Database connections
- D) User authentication only

### 12. [Pattern Match] Failure Handling
Match strategy to scenario:
1. Retry            A. Permanent failure
2. Circuit breaker  B. Transient failure
3. Fallback        C. Repeated failures
4. Hedging         D. Slow response

**Answers:** 1-B, 2-C, 3-A, 4-D

### 13. [True/False] Timeouts
Infinite timeouts eliminate timeout-related failures.
- **Answer:** False
- **Reason:** Can cause indefinite blocking and resource exhaustion.

### 14. [Multiple Choice] Bulkhead Pattern
The bulkhead pattern isolates:
- A) Network traffic
- B) Failure domains ✓
- C) User sessions
- D) Database queries

### 15. [One-line] Backpressure
What does backpressure signal in distributed systems?
- **Answer:** Consumer overwhelmed, slow down producer

### 16. [Fill in Blank] _______ routing sends requests to multiple backends simultaneously.
- **Answer:** Hedged (or speculative)

### 17. [Calculate] Timeout Budget
If total timeout is 10s across 3 sequential services, per-service timeout?
- **Answer:** ~3.3 seconds

### 18. [Multiple Choice] Rate Limiting Location
Rate limiting is most effective at:
- A) Database
- B) API gateway ✓
- C) Cache layer
- D) Message queue

### 19. [Best Choice] Global Coordination
For global coordination across regions:
- A) Synchronous coordination
- B) Hierarchical with regional coordinators ✓
- C) No coordination
- D) Full mesh coordination

### 20. [True/False] Async Benefits
Asynchronous control flow always improves system resilience.
- **Answer:** True
- **Reason:** Decouples components and prevents blocking.

---

## Section C: Advanced Control (5 questions)

### 21. [Rank Order] Control Latency
Order by control latency (fastest to slowest):
- Local decision
- Regional coordinator
- Global consensus
- Human approval

**Answer:** Local, Regional, Global, Human

### 22. [Multiple Choice] Workflow Engine
Workflow engines provide:
- A) Data storage
- B) Orchestrated task execution ✓
- C) Network routing
- D) Cache management

### 23. [One-line] Admission Control
What's the purpose of admission control?
- **Answer:** Prevent overload by rejecting excess requests

### 24. [Best Choice] Microservices Control
For microservices coordination, prefer:
- A) Tight coupling
- B) Event-driven choreography ✓
- C) Shared database
- D) Synchronous calls only

### 25. [Identify] Anti-pattern
Which is a control distribution anti-pattern?
- A) Circuit breakers
- B) Timeout hierarchies
- C) Distributed monolith with synchronous calls ✓
- D) Bulkhead isolation

---

## Answer Key Summary

**Section A:** 1-Central coordinator vs peer-to-peer, 2-B, 3-True, 4-Leader, 5-(1-B,2-C,3-D,4-A), 6-B, 7-9, 8-True, 9-Distributed transactions without 2PC, 10-cascading

**Section B:** 11-B, 12-(1-B,2-C,3-A,4-D), 13-False, 14-B, 15-Consumer overwhelmed, 16-Hedged, 17-3.3s, 18-B, 19-B, 20-True

**Section C:** 21-Local/Regional/Global/Human, 22-B, 23-Prevent overload, 24-B, 25-C

---

## Quick Reference Card

### Control Patterns

| Pattern | Use Case | Trade-off |
|---------|----------|-----------|
| **Orchestration** | Complex workflows | Central bottleneck |
| **Choreography** | Loose coupling | Complex debugging |
| **Saga** | Distributed transactions | Compensation logic |
| **Circuit Breaker** | Failure isolation | Availability vs accuracy |

### Coordination Strategies

1. **Leader-based:** Single coordinator
2. **Token-based:** Rotating control
3. **Gossip-based:** Epidemic spread
4. **Consensus-based:** Group agreement
5. **Lock-free:** Optimistic control

### Resilience Patterns

- **Timeout:** Bound waiting time
- **Retry:** Handle transients
- **Circuit Breaker:** Fail fast
- **Bulkhead:** Isolate failures
- **Rate Limiting:** Prevent overload

### Remember
- **Avoid synchronous chains** - They compound failure
- **Fail fast** - Don't wait indefinitely
- **Isolate failures** - Prevent cascades
- **Local decisions scale** - Global coordination doesn't

---

*Continue to [Pillar 5: Intelligence Distribution →](intelligence-distribution-test.md)*