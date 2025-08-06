---
title: Pattern Discovery
description: Find the perfect distributed systems patterns for your specific needs
---

# Pattern Discovery

Find the perfect patterns for your distributed systems challenges.

## Filter by Excellence Tier

<div class="grid cards" markdown>

- **Gold Patterns (38)**
    
    ---
    
    Battle-tested at scale by FAANG companies. These patterns have proven reliability and performance at massive scale.
    
    [:octicons-search-24: View Gold Patterns](#gold-patterns){ .md-button }

- **Silver Patterns (46)**
    
    ---
    
    Production-ready for specialized use cases. Well-documented with clear implementation guidelines.
    
    [:octicons-search-24: View Silver Patterns](#silver-patterns){ .md-button }

- **Bronze Patterns (7)**
    
    ---
    
    Legacy or transitional patterns. Includes migration paths to modern alternatives.
    
    [:octicons-search-24: View Bronze Patterns](#bronze-patterns){ .md-button }

</div>

## Filter by Problem Domain

<div class="grid cards" markdown>

- **Service Communication**
    
    ---
    
    Patterns for inter-service communication, API design, and protocol selection.
    
    - API Gateway
    - Service Mesh
    - GraphQL Federation
    - gRPC

- **Data Management**
    
    ---
    
    Patterns for distributed data consistency, storage, and synchronization.
    
    - Event Sourcing
    - CQRS
    - Saga Pattern
    - Change Data Capture

- **Resilience & Reliability**
    
    ---
    
    Patterns for building fault-tolerant and self-healing systems.
    
    - Circuit Breaker
    - Bulkhead
    - Retry with Backoff
    - Health Checks

- **Performance & Scale**
    
    ---
    
    Patterns for optimizing performance and handling massive scale.
    
    - Sharding
    - Caching Strategies
    - Load Balancing
    - Read Replicas

</div>

## Quick Pattern Selector

### I need patterns for...

=== "High Availability"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [Circuit Breaker](../../pattern-library/resilience/circuit-breaker/index.md) | Gold | Prevent cascading failures |
    | [Health Checks](../../pattern-library/resilience/health-check/index.md) | Gold | Monitor service health |
    | [Failover](../../pattern-library/resilience/failover/index.md) | Gold | Automatic failure recovery |
    | [Bulkhead](../../pattern-library/resilience/bulkhead/index.md) | Silver | Isolate failures |

=== "Real-time Processing"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [Event Streaming](../../pattern-library/architecture/event-streaming/index.md) | Gold | Process data in real-time |
    | [Pub-Sub](../../pattern-library/communication/publish-subscribe/index.md) | Gold | Decouple producers/consumers |
    | [WebSocket](../../pattern-library/communication/websocket/index.md) | Silver | Bidirectional communication |
    | Server-Sent Events | Silver | Server push updates |

=== "Microservices"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [API Gateway](../../pattern-library/communication/api-gateway/index.md) | Gold | Single entry point |
    | [Service Mesh](../../pattern-library/communication/service-mesh/index.md) | Gold | Service-to-service communication |
    | [Saga](../../pattern-library/data-management/saga/index.md) | Gold | Distributed transactions |
    | [Sidecar](../../pattern-library/architecture/sidecar/index.md) | Silver | Extend service capabilities |

=== "Data Consistency"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [Event Sourcing](../../pattern-library/data-management/event-sourcing/index.md) | Gold | Audit trail and replay |
    | [CQRS](../../pattern-library/data-management/cqrs/index.md) | Gold | Separate read/write models |
    | [Distributed Lock](../../pattern-library/coordination/distributed-lock/index.md) | Silver | Coordinate access |
    | Two-Phase Commit | Bronze | Strong consistency |

## Pattern Selection Matrix

### By Scale Requirements

| Scale | Recommended Patterns | Key Considerations |
|-------|---------------------|-------------------|
| **Startup** (<10K users) | Monolith-First, Simple Caching, Basic Load Balancing | Focus on development speed |
| **Growth** (10K-100K) | API Gateway, Circuit Breaker, Read Replicas | Add resilience patterns |
| **Enterprise** (100K-1M) | Service Mesh, Event Streaming, Sharding | Invest in infrastructure |
| **Hyperscale** (>1M) | Multi-region, Edge Computing, Custom Solutions | Optimize everything |

### By Consistency Requirements

| Requirement | Recommended Patterns | Trade-offs |
|------------|---------------------|------------|
| **Strong Consistency** | Distributed Lock, Two-Phase Commit | Higher latency, lower availability |
| **Eventual Consistency** | Event Sourcing, CQRS, Saga | Better performance, complex reconciliation |
| **Causal Consistency** | Vector Clocks, Lamport Timestamps | Moderate complexity |
| **Read Your Writes** | Session Consistency, Sticky Sessions | Client affinity required |

## Pattern Comparison Tool

!!! tip "Compare Similar Patterns"
    Need help choosing between similar patterns? Use our comparison tool to see side-by-side analysis.
    
    [Pattern Comparison Tool →](../comparisons/index.md){ .md-button }

## Implementation Effort Calculator

Estimate the effort required to implement patterns in your system:

- **Team Size**: Number of engineers available
- **Experience Level**: Team's distributed systems expertise
- **Current Architecture**: Monolith, microservices, or hybrid
- **Scale Requirements**: Current and projected user base

[Calculate Implementation Effort →](../latency-calculator.md){ .md-button }

## Pattern Health Dashboard

View real-time adoption metrics and trends for all patterns:

[View Pattern Health Dashboard →](../reference/pattern-health-dashboard.md){ .md-button }

## All Patterns by Category

### Gold Patterns

!!! success "Battle-tested at scale"
    These patterns are proven in production at companies like Google, Amazon, Netflix, and Meta.

| Pattern | Category | Companies Using | Learn More |
|---------|----------|----------------|------------|
| API Gateway | Communication | Netflix, Amazon | [Details →](../../pattern-library/communication/api-gateway/index.md) |
| Circuit Breaker | Resilience | Netflix, Uber | [Details →](../../pattern-library/resilience/circuit-breaker/index.md) |
| Event Streaming | Data | LinkedIn, Uber | [Details →](../../pattern-library/architecture/event-streaming/index.md) |
| Service Mesh | Communication | Google, Lyft | [Details →](../../pattern-library/communication/service-mesh/index.md) |
| Sharding | Performance | Facebook, Discord | [Details →](../../pattern-library/scaling/sharding/index.md) |

[View all 38 Gold Patterns →](gold-patterns/index.md){ .md-button }

### Silver Patterns

!!! info "Production-ready for specialized use cases"
    These patterns are reliable for specific scenarios with clear implementation guidelines.

| Pattern | Category | Best For | Learn More |
|---------|----------|----------|------------|
| GraphQL Federation | Communication | API composition | [Details →](../../pattern-library/architecture/graphql-federation/index.md) |
| Distributed Lock | Data | Coordination | [Details →](../../pattern-library/coordination/distributed-lock/index.md) |
| Priority Queue | Performance | Task scheduling | [Details →](../../pattern-library/scaling/priority-queue/index.md) |
| Request-Reply | Communication | Synchronous calls | [Details →](../../pattern-library/communication/request-reply/index.md) |
| Consistent Hashing | Data | Stable distribution | [Details →](../../pattern-library/data-management/consistent-hashing/index.md) |

[View all 46 Silver Patterns →](silver-patterns/index.md){ .md-button }

### Bronze Patterns

!!! warning "Legacy patterns with migration paths"
    These patterns are being phased out. Each includes a migration guide to modern alternatives.

| Pattern | Category | Migrate To | Learn More |
|---------|----------|------------|------------|
| Shared Database | Data | Service-per-DB | [Migration →](../../pattern-library/data-management/shared-database/index.md) |
| Actor Model | Coordination | Event-Driven | [Migration →](../../pattern-library/coordination/actor-model/index.md) |
| Lambda Architecture | Architecture | Kappa/Streaming | [Migration →](../../pattern-library/architecture/lambda-architecture/index.md) |
| Kappa Architecture | Architecture | Event Streaming | [Migration →](../../pattern-library/architecture/kappa-architecture/index.md) |
| Choreography | Architecture | Orchestration | [Migration →](../../pattern-library/architecture/choreography/index.md) |

[View all 7 Bronze Patterns →](bronze-patterns/index.md){ .md-button }

## Next Steps

<div class="grid cards" markdown>

- **Ready to implement?**
    
    ---
    
    Browse our implementation guides for step-by-step instructions.
    
    [:octicons-book-24: Implementation Guides](../implementation-guides/index.md){ .md-button }

- **Need help choosing?**
    
    ---
    
    Use our pattern selection wizard for personalized recommendations.
    
    [:octicons-wand-24: Selection Wizard](../index.md){ .md-button }

- **Want to see examples?**
    
    ---
    
    Explore real-world case studies from top tech companies.
    
    [:octicons-briefcase-24: Case Studies](../index.md){ .md-button }

</div>