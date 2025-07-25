---
title: Responsive Pattern Showcase
description: Live examples of responsive layouts using Material for MkDocs
hide:
  - navigation
---

# Responsive Pattern Showcase

Live examples demonstrating full-width responsive layouts optimized for all devices.

## Navigation Cards

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg } **Quick Start**
  
  ---
  
  Get up and running in 5 minutes
  
  [:octicons-arrow-right-24: Begin](../introduction/getting-started.md)

- :material-school:{ .lg } **Learning Paths**
  
  ---
  
  Tailored guides for your experience level
  
  [:octicons-arrow-right-24: Choose path](../learning-paths/index.md)

- :material-book-open-variant:{ .lg } **Fundamentals**
  
  ---
  
  7 Laws & 5 Pillars of distributed systems
  
  [:octicons-arrow-right-24: Explore](../axioms/index.md)

- :material-puzzle:{ .lg } **Patterns**
  
  ---
  
  50+ proven architectural patterns
  
  [:octicons-arrow-right-24: Browse](../patterns/index.md)

- :material-calculator:{ .lg } **Tools**
  
  ---
  
  Interactive calculators & models
  
  [:octicons-arrow-right-24: Calculate](../tools/index.md)

- :material-briefcase:{ .lg } **Case Studies**
  
  ---
  
  Real-world system designs
  
  [:octicons-arrow-right-24: Study](../case-studies/index.md)

</div>

## Metrics Dashboard

<div class="grid cards" markdown>

- **Availability** · `99.999%` · ✅
- **Latency p99** · `23ms` · ⚡
- **Throughput** · `1.2M RPS` · 📈
- **Error Rate** · `0.001%` · ✓
- **Storage** · `8.4TB` · 💾
- **Cost/Month** · `$12,450` · 💰

</div>

## Feature Comparison

<div class="responsive-table" markdown>

| Feature | Monolith | Microservices | Serverless | Service Mesh |
|---------|:--------:|:-------------:|:----------:|:------------:|
| **Complexity** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost (Small)** | 💰 | 💰💰💰 | 💰 | 💰💰💰💰 |
| **Cost (Large)** | 💰💰💰💰 | 💰💰 | 💰💰 | 💰💰💰 |
| **Dev Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡ | ⚡⚡⚡⚡ | ⚡ |
| **Ops Overhead** | Low | High | Low | Very High |

</div>


## Pattern Decision Matrix

<div class="grid" markdown>

!!! question "High Latency?"
    
    **Symptoms:** p99 > 100ms
    
    **Solutions by scale:**
    
    - **< 1K RPS:** Cache + CDN
    - **1K-100K RPS:** + Sharding
    - **> 100K RPS:** + Edge Computing

!!! question "System Crashes?"
    
    **Symptoms:** Cascade failures
    
    **Solutions by impact:**
    
    - **Low:** Health checks
    - **Medium:** Circuit breaker
    - **High:** Bulkhead + Chaos

!!! question "Can't Scale?"
    
    **Symptoms:** CPU/Memory limits
    
    **Solutions by growth:**
    
    - **Linear:** Load balancing
    - **Exponential:** Auto-scaling
    - **Unbounded:** Cell-based

</div>

## Architecture Patterns Grid

<div class="grid cards" markdown>

- :material-api:{ .lg } **API Gateway**
  
  ---
  
  Single entry point for all clients
  
  **When to use:**
  - Multiple client types
  - Cross-cutting concerns
  - API composition needed

- :material-message:{ .lg } **Event Sourcing**
  
  ---
  
  Store state changes as events
  
  **When to use:**
  - Audit trail required
  - Time-travel debugging
  - Event-driven architecture

- :material-content-copy:{ .lg } **CQRS**
  
  ---
  
  Separate read and write models
  
  **When to use:**
  - Different read/write patterns
  - Complex domain logic
  - Read-heavy workloads

- :material-cached:{ .lg } **Cache Aside**
  
  ---
  
  Application manages cache
  
  **When to use:**
  - Read-heavy workloads
  - Tolerate stale data
  - Simple invalidation

- :material-call-split:{ .lg } **Circuit Breaker**
  
  ---
  
  Prevent cascade failures
  
  **When to use:**
  - External dependencies
  - Failure isolation
  - Fast fail scenarios

- :material-folder-multiple:{ .lg } **Sharding**
  
  ---
  
  Distribute data across nodes
  
  **When to use:**
  - Data > single node
  - Horizontal scaling
  - Geo-distribution

</div>

## Implementation Complexity

<div class="grid" markdown>

<div markdown>

### 🟢 Low Complexity

**Time:** Days · **Team:** 1-2

- Caching
- Load Balancing
- Health Checks
- Retry Logic
- Basic Monitoring

</div>

<div markdown>

### 🟡 Medium Complexity  

**Time:** Weeks · **Team:** 2-5

- Circuit Breaker
- Rate Limiting
- Service Discovery
- Message Queue
- API Gateway

</div>

<div markdown>

### 🔴 High Complexity

**Time:** Months · **Team:** 5+

- Service Mesh
- Event Sourcing
- Distributed Tracing
- Multi-Region
- Chaos Engineering

</div>

</div>

## Responsive Data Table

<div class="table-wrapper" markdown>

<div class="responsive-table" markdown>

| Pattern | Problem | Scale | Latency | Throughput | Consistency | Availability | Complexity | Cost |
|---------|---------|-------|---------|------------|-------------|--------------|------------|------|
| **Monolith** | Simple apps | Small | Low | Limited | Strong | Medium | ⭐ | $ |
| **Load Balancer** | Single point | Medium | Low | High | N/A | High | ⭐⭐ | $$ |
| **Cache** | Read latency | Any | Very Low | Very High | Eventual | High | ⭐⭐ | $$ |
| **CDN** | Global latency | Large | Very Low | Very High | Eventual | Very High | ⭐⭐ | $$$ |
| **Sharding** | Data size | Large | Medium | Very High | Varies | High | ⭐⭐⭐⭐ | $$$ |
| **Replication** | Read scale | Medium | Low | High | Eventual | Very High | ⭐⭐⭐ | $$$ |
| **Event Sourcing** | Audit trail | Any | High | Medium | Eventual | High | ⭐⭐⭐⭐ | $$ |
| **CQRS** | Read/Write split | Large | Low | Very High | Eventual | High | ⭐⭐⭐⭐ | $$$ |
| **Service Mesh** | Observability | Large | Medium | High | N/A | High | ⭐⭐⭐⭐⭐ | $$$$ |

</div>


</div>

## System Health Overview

<div class="grid cards" markdown>

- :material-check-circle:{ .lg style="color: #4CAF50;" } **API Gateway**
  
  ---
  
  - Status: `Healthy`
  - Uptime: `45 days`
  - Version: `v2.4.1`

- :material-alert-circle:{ .lg style="color: #FF9800;" } **Database**
  
  ---
  
  - Status: `Degraded`
  - Issue: `High CPU`
  - Action: `Scaling`

- :material-check-circle:{ .lg style="color: #4CAF50;" } **Cache Layer**
  
  ---
  
  - Status: `Healthy`
  - Hit Rate: `94.2%`
  - Memory: `62%`

- :material-check-circle:{ .lg style="color: #4CAF50;" } **Message Queue**
  
  ---
  
  - Status: `Healthy`
  - Lag: `< 1 sec`
  - Throughput: `84K/s`

</div>

## Mobile-Optimized Actions

<div class="grid cards" markdown>

- [:material-play: **Start Tutorial**](../introduction/getting-started.md){ .md-button .md-button--primary }

- [:material-calculator: **Open Calculator**](../tools/latency-calculator.md){ .md-button }

- [:material-download: **Download Guide**](#){ .md-button }

- [:material-help-circle: **Get Help**](#){ .md-button }

</div>

## Responsive Code Examples

=== "Mobile View"

    ```yaml
    # Optimized for small screens
    theme:
      features:
        - navigation.tabs
        - toc.integrate
    ```

=== "Desktop View"

    ```yaml
    # Full configuration for desktop
    theme:
      name: material
      features:
        - navigation.instant
        - navigation.tracking
        - navigation.tabs
        - navigation.tabs.sticky
        - navigation.sections
        - navigation.expand
        - navigation.indexes
        - toc.follow
        - toc.integrate
        - search.suggest
        - search.highlight
    ```

=== "Configuration"

    ```css
    /* Responsive breakpoints */
    @media (max-width: 76.1875em) {
      /* Mobile/Tablet */
    }
    
    @media (min-width: 76.25em) {
      /* Desktop/Wide */
    }
    ```

## Interactive Pattern Selector

!!! question "What's your primary concern?"

    === "Performance"
        
        <div class="grid cards" markdown>
        
        - **Caching** - Reduce latency
        - **CDN** - Global distribution  
        - **Sharding** - Horizontal scale
        - **Read Replicas** - Read throughput
        
        </div>

    === "Reliability"
        
        <div class="grid cards" markdown>
        
        - **Circuit Breaker** - Fault isolation
        - **Retry + Backoff** - Transient failures
        - **Health Checks** - Early detection
        - **Chaos Engineering** - Resilience testing
        
        </div>

    === "Scalability"
        
        <div class="grid cards" markdown>
        
        - **Load Balancing** - Distribute load
        - **Auto-scaling** - Dynamic capacity
        - **Service Mesh** - Service-to-service
        - **Event Streaming** - Async processing
        
        </div>

## Footer Navigation

<div class="grid cards" markdown>

- [:material-arrow-left: **Previous**](../patterns/index.md) · Patterns Overview

- [:material-home: **Home**](../index.md) · Back to Start

- [:material-arrow-right: **Next**](../quantitative/index.md) · Quantitative Tools

</div>

<style>
/* Ensure tables are responsive */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Optimize touch targets for mobile */
@media (max-width: 76.1875em) {
  .md-typeset .grid.cards .card {
    min-height: 80px;
  }
  
  .md-button {
    min-height: 48px;
    width: 100%;
    margin: 0.5rem 0;
  }
}

/* Full-width grids on ultra-wide */
@media (min-width: 100em) {
  .md-typeset .grid {
    max-width: none;
  }
}
</style>