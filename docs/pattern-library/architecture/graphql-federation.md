---
title: GraphQL Federation
description: Compose multiple GraphQL services into a unified API gateway to reduce client round trips
type: pattern
difficulty: intermediate
reading_time: 20 min
excellence_tier: silver
pattern_status: use-with-caution
best_for: API gateways, mobile apps needing flexible data fetching
introduced: 2019-07
current_relevance: growing
category: architecture
essential_question: How do we structure our system architecture to leverage graphql federation?
implementations:
  - {'company': 'Netflix', 'scale': 'Federation for internal microservices'}
  - {'company': 'Airbnb', 'scale': 'GraphQL gateway for mobile apps'}
  - {'company': 'PayPal', 'scale': 'Federated APIs across business units'}
last_updated: 2025-07-21
prerequisites:
status: complete
tagline: Master graphql federation for distributed systems success
trade_offs:
  cons: ['Performance concerns at scale', 'Complex caching strategies', 'Debugging federated queries is difficult']
  pros: ['Single endpoint for multiple services', 'Reduced client complexity', 'Flexible data fetching']
when_not_to_use: When simpler solutions suffice
when_to_use: When dealing with communication challenges
---


## Essential Question

**How do we structure our system architecture to leverage graphql federation?**


# GraphQL Federation

!!! warning "🥈 Silver Tier Pattern"
    **Modern API approach with performance considerations**
    
    GraphQL Federation elegantly solves API composition but can introduce performance bottlenecks and debugging complexity at scale. Requires careful query optimization and monitoring.
    
    **Best suited for:**
    - Mobile applications with varying data needs
    - API gateways unifying microservices
    - Internal service composition
    - Teams with GraphQL expertise

**One graph to rule them all - Composing distributed APIs into a unified experience**

> *"The best API is not one that does everything, but one that appears to do everything while elegantly delegating to specialized services."*

---

## The Essential Question

**How do we compose multiple GraphQL services into a unified API without creating a monolithic gateway or sacrificing performance?**

## When to Use / When NOT to Use

### ✅ Use GraphQL Federation When

| Scenario | Why Federation Helps | Example |
|----------|---------------------|----------|
| **10+ Microservices** | Unified schema across services | Netflix: 100+ services, one graph |
| **Mobile Optimization** | Reduce API calls & bandwidth | Airbnb: 10 calls → 1 query |
| **Polyglot Services** | Language-agnostic composition | GitHub: Ruby, Go, Java services |
| **Team Autonomy** | Services evolve independently | Spotify: Squad ownership model |
| **Complex Data Needs** | Flexible client queries | Shopify: Merchant dashboards |

### ❌ Don't Use Federation When

| Scenario | Why It's Wrong | Better Alternative |
|----------|----------------|--------------------|
| **< 5 Services** | Overhead exceeds benefit | GraphQL monolith or REST |
| **Simple CRUD** | Over-engineering | REST with OpenAPI |
| **Ultra-low latency** | Extra hop adds 10-50ms | Direct service calls |
| **No GraphQL expertise** | Steep learning curve | REST or gRPC |
| **Tight coupling required** | Federation enforces boundaries | Shared database |

### Decision Matrix

---

### The Orchestra Metaphor

<div class="axiom-box">
<h4>🎼 The API Orchestra</h4>

Imagine an orchestra where each section (strings, brass, woodwinds) plays independently but creates unified music. The conductor (gateway) doesn't play instruments but coordinates the performance.

**GraphQL Federation = Conductor coordinating service orchestras**
</div>

### Visual Comparison


### Real Impact Example

**System Flow:** Input → Processing → Output


### Basic Federation Example

**System Flow:** Input → Processing → Output


---

### Query Planning & Execution

**System Flow:** Input → Processing → Output


### Performance Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------||
| **DataLoader Pattern** | Batch entity lookups | N+1 queries → 1 batch query |
| **Query Complexity** | Limit depth & breadth | Prevent expensive queries |
| **APQ (Persisted Queries)** | Send hash not query | 95% bandwidth reduction |
| **Edge Caching** | Cache at CDN | 10ms response for repeat queries |
| **Schema Registry** | Central schema store | Faster startup, validation |

#### 1. Entity Resolution with Caching

**System Flow:** Input → Processing → Output


<div class="failure-vignette">
<h4>💥 Netflix's Federation Migration (2019-2021)</h4>

**Challenge**: 700+ microservices, 100+ client teams, multiple languages

**Solution Architecture**:
- Phased migration over 18 months
- Service-by-service federation
- Backwards compatible REST wrapper
- Gradual client migration

**Results**:
- 60% reduction in client-server traffic
- 80% faster feature development
- 90% reduction in client bugs
- $2M annual savings in bandwidth

**Key Learning**: "Start with high-value, low-risk services"
</div>

#### GitHub's Federation Strategy

| Service | Ownership | Entities | Extensions |
|---------|-----------|----------|------------|
| **Core** | Git team | Repository, Commit, Branch | - |
| **Issues** | Issues team | Issue, PullRequest | Repository.issues |
| **Users** | Identity team | User, Organization | - |
| **Actions** | CI/CD team | Workflow, Job | Repository.workflows |
| **Packages** | Registry team | Package | Repository.packages |

#### 1. Automatic Persisted Queries (APQ)

**System Flow:** Input → Processing → Output


---

### Theoretical Foundations

<div class="axiom-box">
<h4>🔬 Federation as Distributed Type System</h4>

GraphQL Federation implements a distributed type system where:
- **Types** are distributed ownership boundaries
- **Fields** are service capabilities
- **Resolvers** are distributed functions
- **Schema** is the emergent API contract

This maps to category theory where services are categories and federation is a functor preserving morphisms (relationships).
</div>

#### 1. Multi-Region Federation

**System Flow:** Input → Processing → Output


#### 2. Schema Evolution Strategies

| Strategy | When to Use | Example |
|----------|-------------|----------|
| **Field Deprecation** | Removing fields | `@deprecated(reason: "Use newField")` |
| **Type Extension** | Adding capabilities | `extend type User` |
| **Interface Evolution** | Changing contracts | Version interfaces |
| **Federation Migration** | Service boundaries | Gradual ownership transfer |


---

## 📚 Quick Reference

### Federation Cheat Sheet

**System Flow:** Input → Processing → Output


### Common Pitfalls & Solutions

| Pitfall | Symptom | Solution |
|---------|---------|----------||
| **N+1 Queries** | Slow nested queries | DataLoader pattern |
| **Over-federation** | Complex debugging | Start with monolith |
| **Missing Keys** | Failed entity resolution | Consistent ID strategy |
| **Circular Dependencies** | Schema won't compose | Clear service boundaries |
| **Performance Degradation** | Slow responses | Query complexity limits |

### Performance Benchmarks

| Metric | Without Federation | With Federation | Improvement |
|--------|-------------------|-----------------|-------------|
| **API Calls** | 10-15 per screen | 1 query | 90% reduction |
| **Bandwidth** | 50KB average | 5KB average | 90% reduction |
| **Latency** | 500ms (sequential) | 150ms (parallel) | 70% faster |
| **Client Code** | 500 lines | 50 lines | 90% less |

---

## Related Patterns

- [API Gateway](../architecture/api-gateway.md) - Simpler alternative for REST APIs
- [Service Mesh](../architecture/service-mesh.md) - Network-level service composition
- [CQRS](../architecture/cqrs.md) - Separate read/write models
- [Event Sourcing](../architecture/event-sourcing.md) - Event-driven composition
- [BFF Pattern](../architecture/bff.md) - Backend for Frontend alternative

---

**Previous**: [← API Gateway](../architecture/api-gateway.md) | **Next**: [Event Streaming →](../architecture/event-streaming.md)

