---
title: "Case Studies: Laws in Action"
description: Real-world distributed systems analyzed through the lens of laws and pillars
type: case-study
difficulty: advanced
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Case Studies](index.md) → **Case Studies: Laws in Action**

# Case Studies: Laws in Action

Learn how the 7 fundamental laws and 5 pillars apply to real-world systems through detailed analysis of production architectures and their trade-offs.

---

## 📚 Available Case Studies

### [Uber: Real-Time Location System](uber-location.md)
**Scale**: 40M concurrent users | **Challenge**: Sub-100ms global location updates  
**Key Insights**: H3 hexagonal grid system, edge computing, eventual consistency trade-offs  
**Laws in Focus**: [Asynchronous Reality ⏳](../part1-laws/axiom2-asynchrony/index.md), [Multidimensional Optimization ⚖️](../part1-laws/axiom4-tradeoffs/index.md), [State Distribution](../part2-pillars/state/index.md)  
**Related Patterns**: [Edge Computing](../patterns/edge-computing.md) | [Geo-Replication](../patterns/geo-replication.md) | [Load Balancing](../patterns/load-balancing.md)

### [Amazon DynamoDB: Eventually Consistent by Design](amazon-dynamo.md)
**Scale**: 105M requests/second | **Challenge**: 99.999% availability globally  
**Key Insights**: Masterless architecture, vector clocks, consistent hashing, anti-entropy  
**Laws in Focus**: [Correlated Failure ⛓️](../part1-laws/axiom1-failure/index.md), [Multidimensional Optimization ⚖️](../part1-laws/axiom4-tradeoffs/index.md), Availability Trade-offs  
**Related Patterns**: [Tunable Consistency](../patterns/tunable-consistency.md) | [Sharding](../patterns/sharding.md) | [Circuit Breaker](../patterns/circuit-breaker.md)

### [Spotify: ML-Powered Recommendations](spotify-recommendations.md)
**Scale**: 5B recommendations/day | **Challenge**: Personalization at scale  
**Key Insights**: Hybrid online/offline processing, feature stores, A/B testing infrastructure  
**Laws in Focus**: [State Distribution](../part2-pillars/state/index.md), [Intelligence Distribution](../part2-pillars/intelligence/index.md), [Work Distribution](../part2-pillars/work/index.md)  
**Related Patterns**: [CQRS](../patterns/cqrs.md) | [Event-Driven Architecture](../patterns/event-driven.md) | [Caching Strategies](../patterns/caching-strategies.md)

### [PayPal: Distributed Payment Processing](paypal-payments.md)
**Scale**: $1.36T/year | **Challenge**: Zero transaction loss with global scale  
**Key Insights**: Distributed sagas, idempotency, compensating transactions  
**Laws in Focus**: [Truth Distribution](../part2-pillars/truth/index.md), [Control Distribution](../part2-pillars/control/index.md), [Economic Reality 💰](../part1-laws/axiom7-economics/index.md)  
**Related Patterns**: [Saga Pattern](../patterns/saga.md) | [Idempotent Receiver](../patterns/idempotent-receiver.md) | [Event Sourcing](../patterns/event-sourcing.md)

---

## 📊 Common Patterns Across Industries

### Architecture Evolution Patterns

| Stage | Characteristics | Common Solutions |
|-------|----------------|------------------|
| **Startup** | Single server, <1K users | Monolith, RDBMS |
| **Growth** | 10K-100K users | Load balancers, read replicas |
| **Scale** | 1M+ users | Microservices, NoSQL |
| **Hyperscale** | 100M+ users | Cell architecture, edge computing |

### Trade-off Decisions

| System | Chose | Over | Because |
|--------|-------|------|---------|
| **Uber** | Eventual consistency | Strong consistency | Real-time updates matter more |
| **DynamoDB** | Availability | Consistency | Can't lose sales |
| **PayPal** | Consistency | Speed | Money must be accurate |
| **Fortnite** | Client prediction | Server authority | Player experience |
| **SpaceX** | Triple redundancy | Cost savings | Human lives at stake |

### Key Success Factors

1. **Start Simple**: All systems began with straightforward architectures
2. **Measure Everything**: Data-driven decision making
3. **Plan for Failure**: Build resilience from day one
4. **Iterate Quickly**: Learn from production
5. **Automate Operations**: Reduce human error

---

## 🎯 Learning Paths by Role

### For Backend Engineers
1. Start with [Uber's Location System](uber-location.md) - Classic distributed systems challenges
2. Study [DynamoDB](amazon-dynamo.md) - Database internals
3. Explore [PayPal](paypal-payments.md) - Transaction processing

### For ML Engineers
1. Begin with [Spotify Recommendations](spotify-recommendations.md) - ML at scale
2. Review [Uber's Location](uber-location.md) - Real-time features
3. Examine feature stores and pipelines

### For Gaming Engineers
1. Focus on **Fortnite** - State synchronization (coming soon)
2. Study [Uber](uber-location.md) - Real-time systems
3. Learn about edge computing patterns

### For Reliability Engineers
1. Start with **SpaceX** - Safety-critical systems (coming soon)
2. Study [DynamoDB](amazon-dynamo.md) - High availability
3. Review all failure handling strategies

---

## 🔗 Quick Reference

### By Primary Law Focus

| Case Study | Primary Laws | Key Innovation |
|------------|---------------|----------------|
| **Uber** | Asynchronous Reality ⏳, Multidimensional Optimization ⚖️ | H3 hexagonal grid |
| **DynamoDB** | Correlated Failure ⛓️, Multidimensional Optimization ⚖️ | Vector clocks |
| **Spotify** | Distributed Knowledge 🧠, Economic Reality 💰 | Hybrid ML architecture |
| **PayPal** | Distributed Knowledge 🧠, Economic Reality 💰 | Distributed sagas |
| **Fortnite** | Asynchronous Reality ⏳, Emergent Chaos 🌪️ | Client prediction |
| **SpaceX** | Correlated Failure ⛓️, Cognitive Load 🤯 | Formal verification |

### By Scale Metrics

| System | Peak Load | Data Volume | Availability |
|--------|-----------|-------------|--------------|
| **Uber** | 40M concurrent users | 100TB/day | 99.97% |
| **DynamoDB** | 105M requests/sec | Exabytes | 99.999% |
| **Spotify** | 5B recommendations/day | Petabytes | 99.95% |
| **PayPal** | $1.36T/year | 100TB | 99.999% |
| **Fortnite** | 12.3M concurrent | 50TB/day | 99.9% |
| **SpaceX** | 10K metrics/sec | 1TB/mission | 100% |

---

---

## 🔗 Quick Navigation

### Understanding the Theory
- [7 Fundamental Laws](../part1-laws/index.md) - The constraints these systems navigate
- [5 Foundational Pillars](../part2-pillars/index.md) - How these systems organize solutions
- [Modern Patterns](../patterns/index.md) - The patterns these systems implement

### Case Studies by Primary Focus
**Latency & Performance**
- [Uber Location](uber-location.md) - Sub-100ms global updates
- Coming Soon: Fortnite - Real-time game state

**Availability & Resilience**
- [Amazon DynamoDB](amazon-dynamo.md) - 99.999% availability
- Coming Soon: SpaceX - Safety-critical systems

**Scale & Intelligence**
- [Spotify Recommendations](spotify-recommendations.md) - 5B recommendations/day
- [PayPal Payments](paypal-payments.md) - $1.36T/year processing

### Patterns Demonstrated
- **[Edge Computing](../patterns/edge-computing.md)**: Uber's location system
- **[Tunable Consistency](../patterns/tunable-consistency.md)**: DynamoDB's approach
- **[Saga Pattern](../patterns/saga.md)**: PayPal's distributed transactions
- **[CQRS](../patterns/cqrs.md)**: Spotify's ML pipeline

---

*"The best architects learn from others' production experiences. These case studies represent decades of collective wisdom."*
