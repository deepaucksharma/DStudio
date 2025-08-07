---
title: "Pillar 5: Intelligence Distribution - Quick Assessment"
description: Objective assessment on distributing logic, decision-making, and computation across system components
type: test
difficulty: advanced
time_limit: 25 minutes
question_count: 25
passing_score: 75
---

# Pillar 5: Intelligence Distribution

⏱️ **Time:** 25 minutes | 📝 **25 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Strategically placing computation, decision logic, and intelligence across distributed components to optimize performance, resilience, and autonomy.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] Edge Computing
Where should retry logic ideally live?
- A) Client only
- B) Server only
- C) Load balancer
- D) Client with server backpressure ✓

### 2. [True/False] Smart Endpoints
Smart endpoints and dumb pipes is a microservices principle.
- **Answer:** True
- **Reason:** Puts intelligence at service boundaries, not infrastructure.

### 3. [Fill in Blank] _______ computing moves processing closer to data sources.
- **Answer:** Edge (or fog)

### 4. [Pattern Matching] Intelligence Placement
Match computation to optimal location:
1. User personalization    A. Edge/CDN
2. Static content          B. Client device
3. Real-time analytics     C. Stream processor
4. Privacy-sensitive       D. Application server

**Answers:** 1-D, 2-A, 3-C, 4-B

### 5. [One-line] Federated Learning
What problem does federated learning solve?
- **Answer:** Training ML models without centralizing data

### 6. [Multiple Choice] Caching Decisions
Cache invalidation logic should be:
- A) Only at cache layer
- B) Distributed across producers and consumers ✓
- C) Only at database
- D) Manual only

### 7. [Calculate] Edge Nodes
If 100ms RTT to cloud, edge nodes at 10ms save what % latency?
- **Answer:** 90%

### 8. [True/False] Centralized Intelligence
Centralized intelligence always provides better decisions.
- **Answer:** False
- **Reason:** Lacks local context and adds latency.

### 9. [Fill in Blank] _______ batching aggregates requests to improve efficiency.
- **Answer:** Adaptive (or dynamic)

### 10. [Multiple Choice] Decision Delegation
Delegating decisions to edge nodes improves:
- A) Only latency
- B) Latency and resilience ✓
- C) Only cost
- D) Only security

---

## Section B: Implementation (10 questions)

### 11. [Multiple Choice] Feature Flags
Feature flag decisions should be made:
- A) Always server-side
- B) At appropriate layer based on need ✓
- C) Always client-side
- D) Only at deployment

### 12. [Pattern Match] Processing Models
Match processing model to characteristic:
1. Batch processing     A. Low latency
2. Stream processing    B. High throughput
3. Microbatch          C. Balance of both
4. Request-response    D. Immediate

**Answers:** 1-B, 2-A, 3-C, 4-D

### 13. [One-line] Sidecar Pattern
What intelligence does sidecar pattern add?
- **Answer:** Cross-cutting concerns without application changes

### 14. [True/False] Stored Procedures
Database stored procedures are ideal for distributing all business logic.
- **Answer:** False
- **Reason:** Creates tight coupling and limits scalability.

### 15. [Fill in Blank] _______ gateways aggregate multiple service calls.
- **Answer:** API (or Backend-for-Frontend/BFF)

### 16. [Multiple Choice] ML Model Serving
For real-time ML inference, deploy models:
- A) Only in central cloud
- B) At edge for latency-sensitive cases ✓
- C) Only on client devices
- D) Only in databases

### 17. [Calculate] Aggregation Benefit
Aggregating 10 requests into 1 reduces overhead by what factor?
- **Answer:** 10x (approximately)

### 18. [Multiple Choice] Query Pushdown
Query pushdown optimization moves computation to:
- A) Application layer
- B) Data layer ✓
- C) Network layer
- D) Client layer

### 19. [Best Choice] IoT Intelligence
For IoT devices, intelligence distribution should be:
- A) All cloud processing
- B) Hierarchical: device, edge, cloud ✓
- C) All device processing
- D) Random distribution

### 20. [True/False] Stateless Functions
Stateless functions can be deployed anywhere without concern.
- **Answer:** True
- **Reason:** No state dependencies enable flexible placement.

---

## Section C: Optimization (5 questions)

### 21. [Rank Order] Intelligence Hierarchy
Order from most local to most centralized:
- Browser cache
- CDN edge
- Regional datacenter
- Global cloud

**Answer:** Browser cache, CDN edge, Regional datacenter, Global cloud

### 22. [Multiple Choice] Compute vs Data Movement
When data is large and computation small:
- A) Move data to compute
- B) Move compute to data ✓
- C) Replicate everything
- D) Don't process

### 23. [One-line] Lambda Architecture
What does Lambda architecture separate?
- **Answer:** Batch and stream processing paths

### 24. [Best Choice] Global User Preferences
User preference computation should be:
- A) Always centralized
- B) Cached at edge with periodic sync ✓
- C) Computed on every request
- D) Never cached

### 25. [Identify] Anti-pattern
Which is an intelligence distribution anti-pattern?
- A) Edge caching
- B) Federated learning
- C) All logic in a single monolithic service ✓
- D) API aggregation

---

## Answer Key Summary

**Section A:** 1-D, 2-True, 3-Edge, 4-(1-D,2-A,3-C,4-B), 5-Training ML without centralizing data, 6-B, 7-90%, 8-False, 9-Adaptive, 10-B

**Section B:** 11-B, 12-(1-B,2-A,3-C,4-D), 13-Cross-cutting concerns, 14-False, 15-API, 16-B, 17-10x, 18-B, 19-B, 20-True

**Section C:** 21-Browser/CDN/Regional/Global, 22-B, 23-Batch and stream processing, 24-B, 25-C

---

## Quick Reference Card

### Intelligence Placement Strategy

| Location | Best For | Latency | Cost |
|----------|----------|---------|------|
| **Client** | Privacy, offline | Lowest | Free |
| **Edge** | Regional logic | Low | Low |
| **Cloud** | Complex computation | High | Variable |
| **Hybrid** | Balanced approach | Medium | Optimized |

### Processing Patterns

1. **Edge Computing:** Process near source
2. **Fog Computing:** Intermediate processing
3. **Serverless:** Event-driven functions
4. **Federated:** Distributed learning
5. **Hierarchical:** Layered intelligence

### Decision Factors

- **Latency Requirements:** Closer = faster
- **Data Volume:** Move compute to data
- **Privacy:** Keep sensitive data local
- **Cost:** Balance compute vs transfer
- **Reliability:** Distribute for resilience

### Remember
- **Push intelligence to edges** - For responsiveness
- **Keep pipes dumb** - Intelligence at endpoints
- **Cache aggressively** - But invalidate wisely
- **Compute follows data** - When data is large

---

*Completed! Continue to [Update Navigation →](../../../mkdocs.yml) to add all test links.*