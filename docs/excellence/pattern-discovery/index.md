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

- **Silver Patterns (38)**
    
    ---
    
    Production-ready for specialized use cases. Well-documented with clear implementation guidelines.
    
    [:octicons-search-24: View Silver Patterns](#silver-patterns){ .md-button }

- **Bronze Patterns (25)**
    
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
    | [Circuit Breaker](../../patterns/circuit-breaker) | Gold | Prevent cascading failures |
    | [Health Checks](../../patterns/health-checks) | Gold | Monitor service health |
    | [Failover](../../patterns/failover) | Gold | Automatic failure recovery |
    | [Bulkhead](../../patterns/bulkhead) | Silver | Isolate failures |

=== "Real-time Processing"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [Event Streaming](../../patterns/event-streaming) | Gold | Process data in real-time |
    | [Pub-Sub](../../patterns/pub-sub) | Gold | Decouple producers/consumers |
    | [WebSocket](../../patterns/websocket) | Silver | Bidirectional communication |
    | [Server-Sent Events](../../patterns/server-sent-events) | Silver | Server push updates |

=== "Microservices"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [API Gateway](../../patterns/api-gateway) | Gold | Single entry point |
    | [Service Mesh](../../patterns/service-mesh) | Gold | Service-to-service communication |
    | [Saga](../../patterns/saga) | Gold | Distributed transactions |
    | [Sidecar](../../patterns/sidecar) | Silver | Extend service capabilities |

=== "Data Consistency"

    **Recommended Patterns:**
    
    | Pattern | Tier | Use Case |
    |---------|------|----------|
    | [Event Sourcing](../../patterns/event-sourcing) | Gold | Audit trail and replay |
    | [CQRS](../../patterns/cqrs) | Gold | Separate read/write models |
    | [Distributed Lock](../../patterns/distributed-lock) | Silver | Coordinate access |
    | [Two-Phase Commit](../../patterns/two-phase-commit) | Bronze | Strong consistency |

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
    
    [Pattern Comparison Tool →](../comparisons){ .md-button }

## Implementation Effort Calculator

Estimate the effort required to implement patterns in your system:

- **Team Size**: Number of engineers available
- **Experience Level**: Team's distributed systems expertise
- **Current Architecture**: Monolith, microservices, or hybrid
- **Scale Requirements**: Current and projected user base

[Calculate Implementation Effort →](calculator){ .md-button }

## Pattern Health Dashboard

View real-time adoption metrics and trends for all patterns:

[View Pattern Health Dashboard →](../../reference/pattern-health-dashboard){ .md-button }

## All Patterns by Category

### Gold Patterns

!!! success "Battle-tested at scale"
    These patterns are proven in production at companies like Google, Amazon, Netflix, and Meta.

| Pattern | Category | Companies Using | Learn More |
|---------|----------|----------------|------------|
| API Gateway | Communication | Netflix, Amazon | [Details →](../../patterns/api-gateway) |
| Circuit Breaker | Resilience | Netflix, Uber | [Details →](../../patterns/circuit-breaker) |
| Event Streaming | Data | LinkedIn, Uber | [Details →](../../patterns/event-streaming) |
| Service Mesh | Communication | Google, Lyft | [Details →](../../patterns/service-mesh) |
| Sharding | Performance | Facebook, Discord | [Details →](../../patterns/sharding) |

[View all 38 Gold Patterns →](../../patterns#gold-tier){ .md-button }

### Silver Patterns

!!! info "Production-ready for specialized use cases"
    These patterns are reliable for specific scenarios with clear implementation guidelines.

| Pattern | Category | Best For | Learn More |
|---------|----------|----------|------------|
| GraphQL Federation | Communication | API composition | [Details →](../../patterns/graphql-federation) |
| Feature Flags | Operations | Progressive rollouts | [Details →](../../patterns/feature-flags) |
| Blue-Green Deploy | Operations | Zero-downtime updates | [Details →](../../patterns/blue-green-deployment) |
| Distributed Lock | Data | Coordination | [Details →](../../patterns/distributed-lock) |
| Priority Queue | Performance | Task scheduling | [Details →](../../patterns/priority-queue) |

[View all 38 Silver Patterns →](../../patterns#silver-tier){ .md-button }

### Bronze Patterns

!!! warning "Legacy patterns with migration paths"
    These patterns are being phased out. Each includes a migration guide to modern alternatives.

| Pattern | Category | Migrate To | Learn More |
|---------|----------|------------|------------|
| Two-Phase Commit | Data | Saga Pattern | [Migration →](../../patterns/two-phase-commit) |
| Shared Database | Data | Service-per-DB | [Migration →](../../patterns/shared-database) |
| Distributed Monolith | Architecture | True Microservices | [Migration →](../../patterns/distributed-monolith) |
| Fat Client | Architecture | API-First | [Migration →](../../patterns/fat-client) |
| Database Triggers | Data | Event Streaming | [Migration →](../../patterns/database-triggers) |

[View all 25 Bronze Patterns →](../../patterns#bronze-tier){ .md-button }

## Next Steps

<div class="grid cards" markdown>

- **Ready to implement?**
    
    ---
    
    Browse our implementation guides for step-by-step instructions.
    
    [:octicons-book-24: Implementation Guides](../implementation-guides){ .md-button }

- **Need help choosing?**
    
    ---
    
    Use our pattern selection wizard for personalized recommendations.
    
    [:octicons-wand-24: Selection Wizard](../pattern-selection-wizard){ .md-button }

- **Want to see examples?**
    
    ---
    
    Explore real-world case studies from top tech companies.
    
    [:octicons-briefcase-24: Case Studies](../real-world-excellence){ .md-button }

</div>