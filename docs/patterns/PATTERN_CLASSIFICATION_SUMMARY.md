# Pattern Classification Summary - Quick Reference

## Classification Overview

### 🏆 Gold Patterns (32 + 6 to restore = 38 total)
**Definition**: Used by 3+ elite companies, proven at 100M+ scale, active development, clear playbooks

**Must-Have Patterns**:
- **Resilience**: circuit-breaker, retry-backoff, timeout*, health-check*, graceful-degradation
- **Data**: consistent-hashing, sharding, caching-strategies, cdc, crdt*, bloom-filter*
- **Architecture**: service-mesh, event-driven, cqrs, event-sourcing, saga
- **Coordination**: leader-election, distributed-lock, consensus
- **Scale**: load-balancing, auto-scaling, multi-region, edge-computing

*Patterns to restore from archive

### 🥈 Silver Patterns (38)
**Definition**: Widely used but with trade-offs, context-dependent, may be transitioning

**Notable Patterns**:
- **Emerging**: data-mesh, cell-based, graphql-federation
- **Specialized**: serverless-faas, bulkhead, priority-queue
- **Infrastructure**: blue-green-deployment, sidecar, ambassador

### 🥉 Bronze Patterns (25)
**Definition**: Legacy patterns, better alternatives exist, kept for educational value

**Common Anti-patterns**:
- **Too Generic**: fault-tolerance, distributed-storage, analytics-scale
- **Superseded**: lambda-architecture, kappa-architecture, polyglot-persistence
- **Educational Only**: cap-theorem, shared-nothing

## Immediate Actions Required

1. **Restore 6 Gold Patterns from Archive**:
   ```bash
   # Move these patterns back to main directory
   timeout.md       # Every RPC needs timeouts
   health-check.md  # Load balancer requirement
   crdt.md         # Conflict-free replication
   hlc.md          # Distributed timestamps
   merkle-trees.md # Data verification
   bloom-filter.md # Probabilistic membership
   ```

2. **Create Pattern Packs**:
   - **Starter Pack**: timeout + health-check + retry-backoff + circuit-breaker
   - **Scale Pack**: sharding + caching + load-balancing + auto-scaling
   - **Data Pack**: cqrs + event-sourcing + cdc + saga
   - **Resilience Pack**: All Gold resilience patterns

3. **Archive Bronze Patterns**:
   - Move overly generic patterns to theory section
   - Consolidate redundant patterns
   - Add deprecation notices with modern alternatives

## Pattern Selection Quick Guide

### By Company Size
- **Startup (<100 RPS)**: Focus on Starter Pack only
- **Growth (100-10K RPS)**: Add Scale Pack
- **Scale (10K-100K RPS)**: Add Data Pack + service-mesh
- **Enterprise (>100K RPS)**: All Gold patterns

### By Problem Domain
- **High Availability**: circuit-breaker + retry + timeout + health-check
- **Global Scale**: multi-region + edge + geo-replication + caching
- **Data Consistency**: cqrs + event-sourcing + saga + distributed-lock
- **Microservices**: service-mesh + api-gateway + distributed-tracing

### By Maturity Stage
1. **Essential** (Day 1): timeout, health-check, retry, load-balancing
2. **Growth** (Month 1-6): caching, circuit-breaker, rate-limiting
3. **Scale** (Month 6-12): sharding, cqrs, service-mesh
4. **Advanced** (Year 2+): cell-based, edge-computing, chaos-engineering

## Success Metrics

- **Gold Pattern Adoption**: Track % of systems using each Gold pattern
- **Pattern ROI**: Measure impact (uptime, performance, cost)
- **Developer Satisfaction**: Survey on pattern documentation quality
- **Time to Implementation**: Average time from learning to production

## Next Steps

1. Review and approve classification
2. Execute pattern restoration (6 patterns)
3. Create visual pattern selector tool
4. Update documentation navigation
5. Develop pattern maturity roadmap
6. Create company-specific case studies for Gold patterns