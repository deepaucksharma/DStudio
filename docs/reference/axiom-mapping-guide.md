---
title: Axiom Mapping Reference Guide
description: Complete mapping between old 8-axiom structure and new 7-law framework
type: reference
difficulty: intermediate
reading_time: 5 min
status: complete
last_updated: 2025-01-23
---

# Axiom Mapping Reference Guide

This guide provides a complete mapping between the old 8-axiom structure and the new 7-law framework to help update cross-references throughout the documentation.

## Quick Reference Table

| Old Axiom | New Law | Key Concept Change |
|-----------|---------|-------------------|
| Axiom 1: Latency | Law 2: Asynchronous Reality ⏳ | From speed limits to information uncertainty |
| Axiom 2: Capacity | Law 4: Multidimensional Optimization ⚖️ | From resource limits to n-dimensional trade-offs |
| Axiom 3: Failure | Law 1: Correlated Failure ⛓️ | From independent to correlated failures |
| Axiom 4: Concurrency | Law 3: Emergent Chaos 🌪️ | From race conditions to emergent complexity |
| Axiom 5: Coordination | Law 4: Multidimensional Optimization ⚖️ | From coordination costs to trade-off space |
| Axiom 6: Observability | Law 5: Distributed Knowledge 🧠 | From monitoring to epistemology |
| Axiom 7: Human Interface | Law 6: Cognitive Load 🤯 | From constraints to mental models |
| Axiom 8: Economics | Law 7: Economic Reality 💰 | Enhanced with TCO and FinOps |

## Detailed Mappings

### Law 1: Correlated Failure ⛓️ (from old Axiom 3)
**Old focus**: Components fail independently  
**New focus**: Failures correlate through shared dependencies
- Metastable failures
- Gray failures
- Cascade effects
- Dependency graphs

### Law 2: Asynchronous Reality ⏳ (from old Axiom 1)
**Old focus**: Latency as speed-of-light limit  
**New focus**: Information uncertainty and temporal logic
- FLP impossibility
- Happens-before relations
- Eventual consistency as reality
- Bandwidth-delay product

### Law 3: Emergent Chaos 🌪️ (NEW - aspects from old Axiom 4)
**Old focus**: Concurrency and race conditions  
**New focus**: Emergent behaviors at scale
- Phase transitions
- Self-organized criticality
- State space explosion
- Non-linear dynamics

### Law 4: Multidimensional Optimization ⚖️ (from old Axioms 2 & 5)
**Old focus**: Capacity limits and coordination costs  
**New focus**: N-dimensional trade-off space
- Beyond CAP theorem
- Harvest vs yield model
- Cost vs complexity vs operability
- Non-linear trade-offs

### Law 5: Distributed Knowledge 🧠 (from old Axiom 6)
**Old focus**: Limited observability  
**New focus**: Epistemology and knowledge theory
- Belief vs knowledge vs common knowledge
- Byzantine epistemology
- Probabilistic certainty
- Local truth

### Law 6: Cognitive Load 🤯 (from old Axiom 7)
**Old focus**: Human interface constraints  
**New focus**: Mental models and operator experience
- 7±2 rule
- Pit of success design
- Error message quality
- Observability as UI

### Law 7: Economic Reality 💰 (from old Axiom 8)
**Old focus**: Everything has a cost  
**New focus**: Architecture as financial decision
- Total Cost of Ownership (TCO)
- Build vs buy calculus
- Performance per dollar
- FinOps modeling

## Pattern Reference Updates

When updating pattern documentation:

### Patterns primarily affected by Law 1 (Correlated Failure):
- Circuit Breaker
- Bulkhead
- Health Check
- Graceful Degradation

### Patterns primarily affected by Law 2 (Asynchronous Reality):
- Caching Strategies
- CDN/Edge Computing
- Timeout patterns
- Async messaging

### Patterns primarily affected by Law 3 (Emergent Chaos):
- Chaos Engineering
- Auto-scaling
- Load shedding
- Backpressure

### Patterns primarily affected by Law 4 (Multidimensional Optimization):
- Sharding
- Consensus protocols
- Saga pattern
- CQRS

### Patterns primarily affected by Law 5 (Distributed Knowledge):
- Event Sourcing
- Observability patterns
- Distributed tracing
- Service discovery

### Patterns primarily affected by Law 6 (Cognitive Load):
- Service Mesh
- API Gateway
- Runbook automation
- Error handling

### Patterns primarily affected by Law 7 (Economic Reality):
- FinOps patterns
- Serverless/FaaS
- Multi-region strategies
- Resource optimization

## Migration Checklist

When updating a file that references axioms:

1. **Identify old axiom references** - Look for "Axiom N" or specific axiom names
2. **Map to new law** - Use the quick reference table above
3. **Update concept focus** - Shift from simple constraint to deeper theory
4. **Add emoji indicator** - Each law has an associated emoji
5. **Update links** - Change axiom paths to new structure:
   - Old: `../part1-axioms/axiom1-latency/`
   - New: `../part1-axioms/axiom2-asynchrony/`

## Common Updates

### Before
```markdown
According to Axiom 1 (Latency), the speed of light limits...
[See Axiom 1](../part1-axioms/axiom1-latency/index.md)
```

### After
```markdown
According to Law 2 (Asynchronous Reality ⏳), information uncertainty means...
[See Law 2](../part1-axioms/axiom2-asynchrony/index.md)
```

## Notes

- The new framework is more theoretical and advanced
- Some old axioms map to multiple new laws
- Law 3 (Emergent Chaos) is entirely new
- Focus has shifted from constraints to fundamental laws
- Each law now includes deeper mathematical foundations