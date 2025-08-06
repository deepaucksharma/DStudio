---
title: Strangler Fig
description: Incrementally replace legacy systems by gradually routing functionality to new implementations
type: pattern
difficulty: advanced
reading_time: 20 min
excellence_tier: silver
pattern_status: recommended
best_for:
introduced: 2024-01
current_relevance: mainstream
category: architecture
essential_question: How do we structure our system architecture to leverage strangler fig?
last_updated: 2025-01-26
prerequisites:
  - API Gateway
  - Service Mesh
  - Anti-Corruption Layer
status: complete
tagline: Master strangler fig for distributed systems success
trade_offs:
  cons: []
  pros: []
when_not_to_use:
  - Greenfield applications
  - Simple system replacements
  - Urgent complete rewrites needed
  - Legacy system is well-maintained
when_to_use:
  - Migrating monoliths to microservices
  - Replacing legacy systems incrementally
  - Modernizing without big-bang rewrites
  - Risk-averse transformation required
---


## Essential Question
## When to Use / When NOT to Use

### When to Use

| Scenario | Why It Fits | Alternative If Not |
|----------|-------------|-------------------|
| High availability required | Pattern provides resilience | Consider simpler approach |
| Scalability is critical | Handles load distribution | Monolithic might suffice |
| Distributed coordination needed | Manages complexity | Centralized coordination |

### When NOT to Use

| Scenario | Why to Avoid | Better Alternative |
|----------|--------------|-------------------|
| Simple applications | Unnecessary complexity | Direct implementation |
| Low traffic systems | Overhead not justified | Basic architecture |
| Limited resources | High operational cost | Simpler patterns |
**How do we structure our system architecture to leverage strangler fig?**


# Strangler Fig Pattern

!!! info "The Botanical Metaphor"
    The strangler fig tree starts life as a seed deposited high in another tree. It sends roots down and vines up, gradually enveloping the host tree. Eventually, the host dies and decomposes, leaving the strangler fig standing independently—a perfect metaphor for legacy system replacement.

## Problem Statement

<div class="failure-vignette">
<h4>The Big Bang Disaster</h4>
<p>A major bank attempted a complete system rewrite over 3 years. On cutover weekend:</p>
<ul>
<li>40% of transactions failed silently</li>
<li>Customer data inconsistencies affected 2M accounts</li>
<li>Rollback took 72 hours of downtime</li>
<li>$50M in losses and regulatory fines</li>
</ul>
<p><strong>Root cause:</strong> Attempting to replace everything at once instead of incremental migration</p>
</div>

## Solution Overview




## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Strategies

### 1. Edge Proxy Strategy

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



### Strategy Comparison

| Feature | Edge Proxy | Branch by Abstraction | Parallel Run |
|---------|------------|----------------------|--------------|
| **Deployment Risk** | Low | Medium | Low |
| **Rollback Speed** | Instant | Code Deploy | Instant |
| **Performance Impact** | +5-10ms latency | Minimal | 2x resource usage |
| **Code Complexity** | External | Internal refactoring | Comparison logic |
| **Best For** | API-based systems | Monolithic codebases | Critical systems |

### Migration Decision Tree

### 2. Branch by Abstraction Strategy

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



### 3. Parallel Run Strategy

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



## Progressive Migration Patterns

### Database Strangling

### Feature Toggle Evolution

## Risk Mitigation Matrix

| Risk | Mitigation Strategy | Rollback Plan |
|------|-------------------|---------------|
| **Data Inconsistency** | Dual writes with reconciliation | Replay from event log |
| **Performance Degradation** | Shadow load testing | Route back to legacy |
| **Feature Parity Gap** | Parallel run comparison | Feature flags per endpoint |
| **Integration Failures** | Circuit breakers + fallbacks | Instant proxy reroute |
| **State Corruption** | Event sourcing + snapshots | Point-in-time recovery |

## Real-World Examples

### Example 1: Amazon Product Catalog Migration

<div class="decision-box">
<h4>Migration Strategy</h4>
<ul>
<li><strong>Duration:</strong> 18 months</li>
<li><strong>Approach:</strong> Category-by-category migration</li>
<li><strong>Key Success Factors:</strong>
  <ul>
  <li>Shadow traffic for 3 months per category</li>
  <li>Automated comparison of 100M+ requests daily</li>
  <li>Gradual traffic shift: 1% → 5% → 25% → 50% → 100%</li>
  </ul>
</li>
<li><strong>Result:</strong> Zero customer-facing incidents</li>
</ul>
</div>

### Example 2: Netflix Billing System Evolution

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



## Anti-Patterns to Avoid

### 1. The Incomplete Strangler

### 2. The Feature Disparity Trap

| Anti-Pattern | Symptoms | Solution |
|--------------|----------|----------|
| **Incomplete Feature Migration** | New system missing 20% features | Feature inventory before starting |
| **Data Model Mismatch** | Constant translation overhead | Gradual schema evolution |
| **Performance Regression** | New system 3x slower | Performance gates per migration |
| **Dependency Tangle** | Circular dependencies emerge | Clear bounded contexts |

## Integration with Other Patterns

### API Gateway Integration

### Service Mesh Enhancement

## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Checklist

<div class="decision-box">
<h4>Pre-Migration Checklist</h4>
<ul>
<li>☐ Complete feature inventory of legacy system</li>
<li>☐ Identify all integration points and dependencies</li>
<li>☐ Design routing/proxy layer architecture</li>
<li>☐ Establish metrics for comparison</li>
<li>☐ Create rollback procedures for each phase</li>
<li>☐ Set up parallel run infrastructure</li>
<li>☐ Define success criteria per component</li>
</ul>
</div>

<div class="decision-box">
<h4>During Migration Checklist</h4>
<ul>
<li>☐ Monitor error rates continuously</li>
<li>☐ Compare outputs in parallel run</li>
<li>☐ Validate data consistency daily</li>
<li>☐ Track performance metrics</li>
<li>☐ Maintain feature parity documentation</li>
<li>☐ Regular stakeholder communication</li>
<li>☐ Gradual traffic shift (1% → 5% → 25% → 50% → 100%)</li>
</ul>
</div>

## Monitoring and Observability

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



## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Error Rate** | < 0.01% increase | Compare legacy vs new |
| **Latency** | < 5% increase | p50, p95, p99 |
| **Consistency** | 99.999% match | Parallel run comparison |
| **Availability** | No degradation | Same SLA maintained |
| **Cost** | < 20% increase during migration | Include dual running |

## Related Patterns

- [API Gateway](../communication/api-gateway.md) - Front-door for routing during migration
- [Service Mesh](../communication/service-mesh.md) - Traffic management and observability
- [Anti-Corruption Layer](../architecture/anti-corruption-layer.md) - Protect new services from legacy
- [Event Sourcing](../data-management/event-sourcing.md) - Capture all changes for replay
- [Circuit Breaker](../resilience/circuit-breaker.md) - Protect during partial failures

## References

- Martin Fowler's original [Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html/)
- [Monolith to Microservices](https://www.oreilly.com/library/view/monolith-to-microservices/9781492047834/) by Sam Newman
- AWS [Strangler Fig Pattern Guide](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-aspnet-web-services/fig-pattern.html/)

