---
title: Strangler Fig
description: Incrementally replace legacy systems by gradually routing functionality to new implementations
type: pattern
category: architectural
difficulty: advanced
reading_time: 20 min
prerequisites: 
  - API Gateway
  - Service Mesh
  - Anti-Corruption Layer
when_to_use: 
  - Migrating monoliths to microservices
  - Replacing legacy systems incrementally
  - Modernizing without big-bang rewrites
  - Risk-averse transformation required
when_not_to_use: 
  - Greenfield applications
  - Simple system replacements
  - Urgent complete rewrites needed
  - Legacy system is well-maintained
status: complete
last_updated: 2025-01-26
---

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

```mermaid
graph TB
    subgraph "Phase 1: Initial State"
        U1[Users] --> L1[Legacy System]
    end
    
    subgraph "Phase 2: Introduce Façade"
        U2[Users] --> F[Façade/Router]
        F --> L2[Legacy System]
    end
    
    subgraph "Phase 3: Gradual Migration"
        U3[Users] --> R[Router]
        R -->|80%| L3[Legacy]
        R -->|20%| N1[New Service A]
    end
    
    subgraph "Phase 4: Majority Migrated"
        U4[Users] --> R2[Router]
        R2 -->|20%| L4[Legacy]
        R2 -->|80%| N2[New Services]
    end
    
    subgraph "Phase 5: Complete"
        U5[Users] --> N3[New System]
    end
    
    style L1 fill:#ff6b6b
    style L2 fill:#ff6b6b
    style L3 fill:#ffa94d
    style L4 fill:#ffd43b
    style N1 fill:#51cf66
    style N2 fill:#51cf66
    style N3 fill:#51cf66
```

## Implementation Strategies

### 1. Edge Proxy Strategy

```mermaid
graph LR
    subgraph "Client Layer"
        C[Clients]
    end
    
    subgraph "Proxy Layer"
        P[Edge Proxy]
        RT[Route Table]
        P --> RT
    end
    
    subgraph "Service Layer"
        L[Legacy System]
        N1[New Service 1]
        N2[New Service 2]
        N3[New Service 3]
    end
    
    C --> P
    P -->|"/orders/*"| N1
    P -->|"/inventory/*"| N2
    P -->|"/customers/*"| L
    P -->|"/*"| L
    
    style P fill:#4c6ef5
    style L fill:#ff6b6b
    style N1 fill:#51cf66
    style N2 fill:#51cf66
```

| Feature | Edge Proxy | Branch by Abstraction | Parallel Run |
|---------|------------|----------------------|--------------|
| **Deployment Risk** | Low | Medium | Low |
| **Rollback Speed** | Instant | Code Deploy | Instant |
| **Performance Impact** | +5-10ms latency | Minimal | 2x resource usage |
| **Code Complexity** | External | Internal refactoring | Comparison logic |
| **Best For** | API-based systems | Monolithic codebases | Critical systems |

### 2. Branch by Abstraction Strategy

```mermaid
graph TB
    subgraph "Step 1: Create Abstraction"
        C1[Client Code] --> O1[Order Logic]
    end
    
    subgraph "Step 2: Introduce Interface"
        C2[Client Code] --> I[IOrderService]
        I --> O2[Order Logic]
    end
    
    subgraph "Step 3: Toggle Implementation"
        C3[Client Code] --> I2[IOrderService]
        I2 --> T[Toggle]
        T -->|"flag=old"| O3[Legacy Order]
        T -->|"flag=new"| N[New Order Service]
    end
    
    subgraph "Step 4: Remove Legacy"
        C4[Client Code] --> I3[IOrderService]
        I3 --> N2[New Order Service]
    end
```

### 3. Parallel Run Strategy

```mermaid
graph TB
    subgraph "Production Traffic"
        R[Request] --> D[Dispatcher]
        D --> L[Legacy System]
        D --> N[New System]
        
        L --> LC[Legacy Response]
        N --> NC[New Response]
        
        LC --> C[Comparator]
        NC --> C
        
        C --> M[Metrics]
        C --> A[Alerts]
        
        LC --> CR[Client Response]
    end
    
    style D fill:#4c6ef5
    style C fill:#fab005
    style L fill:#ff6b6b
    style N fill:#51cf66
```

## Progressive Migration Patterns

### Database Strangling

```mermaid
graph TB
    subgraph "Phase 1: Shared Database"
        LS1[Legacy Service] --> DB1[(Shared DB)]
        NS1[New Service] --> DB1
    end
    
    subgraph "Phase 2: Synchronized Databases"
        LS2[Legacy Service] --> LDB[(Legacy DB)]
        NS2[New Service] --> NDB[(New DB)]
        LDB <--> S[Sync] <--> NDB
    end
    
    subgraph "Phase 3: New Primary"
        NS3[New Service] --> NDB2[(New DB)]
        LS3[Legacy Service] --> API[API Calls]
        API --> NS3
    end
```

### Feature Toggle Evolution

```mermaid
graph LR
    subgraph "Toggle Configuration"
        TC[Toggle Config]
        TC --> F1[Feature A: 10%]
        TC --> F2[Feature B: 50%]
        TC --> F3[Feature C: 100%]
        TC --> F4[Feature D: 0%]
    end
    
    subgraph "Traffic Distribution"
        F1 --> P1[10% New / 90% Legacy]
        F2 --> P2[50% New / 50% Legacy]
        F3 --> P3[100% New]
        F4 --> P4[100% Legacy]
    end
```

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
timeline
    title Netflix Billing System Migration Timeline
    
    2018 Q1 : Monolithic Billing System
            : 15M subscribers
            : 99.9% availability
    
    2018 Q3 : Introduce API Gateway
            : Route 100% through proxy
            : No functional changes
    
    2019 Q1 : Extract Payment Service
            : 5% traffic to new service
            : Parallel run validation
    
    2019 Q3 : Extract Subscription Service
            : 40% traffic migrated
            : Legacy handling edge cases
    
    2020 Q1 : Extract Invoice Service
            : 80% traffic on new platform
            : Legacy for reconciliation only
    
    2020 Q3 : Complete Migration
            : 100% microservices
            : 99.99% availability
            : 200M subscribers
```

## Anti-Patterns to Avoid

### 1. The Incomplete Strangler

```mermaid
graph TB
    subgraph "Anti-Pattern: Abandoned Migration"
        U[Users] --> P[Proxy]
        P --> L[Legacy 60%]
        P --> N[New 40%]
        
        L -.-> X1[Never Migrated]
        N -.-> X2[Permanent Dual Maintenance]
    end
    
    style X1 fill:#ff6b6b,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style X2 fill:#ff6b6b,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

### 2. The Feature Disparity Trap

| Anti-Pattern | Symptoms | Solution |
|--------------|----------|----------|
| **Incomplete Feature Migration** | New system missing 20% features | Feature inventory before starting |
| **Data Model Mismatch** | Constant translation overhead | Gradual schema evolution |
| **Performance Regression** | New system 3x slower | Performance gates per migration |
| **Dependency Tangle** | Circular dependencies emerge | Clear bounded contexts |

## Integration with Other Patterns

### API Gateway Integration

```mermaid
graph TB
    subgraph "API Gateway Pattern"
        AG[API Gateway]
        AG --> RT[Route Table]
        AG --> RL[Rate Limiter]
        AG --> AU[Auth]
    end
    
    subgraph "Strangler Implementation"
        RT --> OLD[Legacy Routes<br/>70%]
        RT --> NEW[New Routes<br/>30%]
    end
    
    AG --> M[Metrics]
    M --> D[Migration Dashboard]
```

### Service Mesh Enhancement

```mermaid
graph LR
    subgraph "Service Mesh"
        SM[Sidecar Proxy]
        SM --> TC[Traffic Control]
        SM --> CB[Circuit Breaker]
        SM --> RT[Retry Logic]
    end
    
    TC --> LS[Legacy Service<br/>Weight: 60]
    TC --> NS[New Service<br/>Weight: 40]
    
    SM --> T[Telemetry]
    T --> G[Grafana Dashboard]
```

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
graph TB
    subgraph "Key Metrics"
        M1[Request Success Rate]
        M2[Response Time p99]
        M3[Error Rate Delta]
        M4[Data Consistency]
        M5[Resource Usage]
    end
    
    subgraph "Dashboards"
        D1[Migration Progress]
        D2[Comparison Results]
        D3[Performance Trends]
        D4[Rollback Triggers]
    end
    
    M1 --> D1
    M2 --> D3
    M3 --> D2
    M4 --> D2
    M5 --> D3
    
    D1 --> A1[Progress Alerts]
    D2 --> A2[Inconsistency Alerts]
    D3 --> A3[Performance Alerts]
    D4 --> A4[Auto Rollback]
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

- [API Gateway](api-gateway.md) - Front-door for routing during migration
- [Service Mesh](service-mesh.md) - Traffic management and observability
- [Anti-Corruption Layer](anti-corruption-layer.md) - Protect new services from legacy
- [Event Sourcing](event-sourcing.md) - Capture all changes for replay
- [Circuit Breaker](circuit-breaker.md) - Protect during partial failures

## References

- Martin Fowler's original [Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Monolith to Microservices](https://www.oreilly.com/library/view/monolith-to-microservices/9781492047834/) by Sam Newman
- AWS [Strangler Fig Pattern Guide](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-aspnet-web-services/fig-pattern.html)