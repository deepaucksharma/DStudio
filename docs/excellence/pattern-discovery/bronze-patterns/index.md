---
title: Bronze Patterns - Legacy & Migration Targets
description: Patterns to migrate away from, with clear paths to modern alternatives
---

# 🥉 Bronze Patterns - Legacy & Migration Targets

**7 patterns that served us well but now have better alternatives. Learn what to migrate from and how.**

<div class="bronze-intro">
    <p class="lead">Bronze patterns are legacy solutions that were once best practices but have been superseded by better approaches. Understanding them is crucial for maintaining existing systems and planning migrations.</p>
</div>

## ⚠️ Why Bronze Patterns Matter

<div class="bronze-importance">

### Don't Ignore Them
- **Legacy Systems**: Millions of systems still use these patterns
- **Migration Knowledge**: Understanding them enables smooth transitions
- **Historical Context**: Learn why they existed and why we moved on
- **Risk Awareness**: Know what problems to expect

### Bronze Pattern Characteristics
- 🔄 **Better Alternatives Exist** - Gold/Silver patterns do it better
- 📉 **70% Success Rate** - More prone to issues
- 🚧 **High Maintenance** - Require more operational effort
- 🎯 **Specific Niches** - May still be valid in narrow contexts

</div>

## 🚨 The 7 Bronze Patterns

### 🏛️ Architecture Patterns

<div class="pattern-category bronze-arch">

#### [CAP Theorem](../../pattern-library/architecture.md/cap-theorem/index.md)
**Choose 2 of 3: Consistency, Availability, Partition Tolerance**
- ⚠️ **Issues**: Oversimplified model, misleading trade-offs
- ✅ **Migrate to**: PACELC theorem for nuanced understanding
- 📊 **Migration Effort**: Low (conceptual shift)
- 💡 **Still Valid For**: Initial system design discussions

#### [Choreography](../../pattern-library/architecture.md/choreography/index.md)
**Services coordinate through events without central control**
- ⚠️ **Issues**: Hard to debug, no clear flow visibility
- ✅ **Migrate to**: [Saga](../../pattern-library/data-management.md/saga/index.md) orchestration or hybrid approach
- 📊 **Migration Effort**: Medium-High
- 💡 **Still Valid For**: Simple, linear workflows

#### [Lambda Architecture](../../pattern-library/architecture.md/lambda-architecture/index.md)
**Batch + streaming layers for data processing**
- ⚠️ **Issues**: Complexity, duplicate logic, maintenance overhead
- ✅ **Migrate to**: [Kappa Architecture](../../pattern-library/architecture.md/kappa-architecture/index.md) or unified streaming
- 📊 **Migration Effort**: High
- 💡 **Still Valid For**: Specific batch/stream hybrid needs

#### [Kappa Architecture](../../pattern-library/architecture.md/kappa-architecture/index.md)
**Everything is a stream**
- ⚠️ **Issues**: Not suitable for all use cases, reprocessing challenges
- ✅ **Migrate to**: Modern stream processing with proper batch support
- 📊 **Migration Effort**: Medium
- 💡 **Still Valid For**: Pure streaming scenarios

</div>

### 🗄️ Data Management Patterns

<div class="pattern-category bronze-data">

#### [Shared Database](../../pattern-library/data-management.md/shared-database/index.md)
**Multiple services share one database**
- ⚠️ **Issues**: Tight coupling, no isolation, scaling limits
- ✅ **Migrate to**: [CQRS](../../pattern-library/data-management.md/cqrs/index.md) + Service Isolation
- 📊 **Migration Effort**: Very High
- 💡 **Still Valid For**: Small, simple systems

#### [Data Lake](../../pattern-library/data-management.md/data-lake/index.md)
**Store everything, figure it out later**
- ⚠️ **Issues**: Data swamp risk, governance challenges
- ✅ **Migrate to**: Data Mesh or structured lakehouse architecture
- 📊 **Migration Effort**: High
- 💡 **Still Valid For**: Research/exploration environments

</div>

### 🔄 Coordination Patterns

<div class="pattern-category bronze-coord">

#### [Actor Model](../../pattern-library/coordination.md/actor-model/index.md)
**Isolated actors communicate via messages**
- ⚠️ **Issues**: Debugging complexity, state management
- ✅ **Migrate to**: Event-driven microservices with clear boundaries
- 📊 **Migration Effort**: High
- 💡 **Still Valid For**: Erlang/Elixir ecosystems, specific use cases

</div>

## 📋 Bronze Pattern Migration Priority

| Pattern | Risk Level | Migration Urgency | Alternative |
|---------|------------|-------------------|-------------|
| Shared Database | 🔴 High | Immediate | CQRS + Service DB |
| CAP Theorem | 🟡 Medium | As Needed | PACELC Understanding |
| Lambda Architecture | 🟡 Medium | Planned | Unified Streaming |
| Data Lake | 🟡 Medium | Planned | Data Mesh |
| Choreography | 🟢 Low | Opportunistic | Orchestration |
| Kappa Architecture | 🟢 Low | Evaluate | Modern Streaming |
| Actor Model | 🟢 Low | Stable Systems | Keep if Working |

## 🎯 Migration Best Practices

### Before Migration
1. **Document Current State** - Understand what you have
2. **Measure Impact** - Know your metrics
3. **Identify Dependencies** - Map all connections
4. **Plan Rollback** - Have an escape route

### During Migration
1. **Incremental Changes** - Small, safe steps
2. **Feature Flags** - Control rollout
3. **Parallel Run** - Validate before switching
4. **Monitor Everything** - Watch for issues

### After Migration
1. **Clean Up** - Remove old code
2. **Document Lessons** - Share knowledge
3. **Update Monitoring** - New patterns, new metrics
4. **Train Team** - Ensure everyone understands

## 🏁 Next Steps

<div class="next-steps">

**Ready to migrate?** Check out our detailed migration guides:

- [Monolith to Microservices](../../migrations/monolith-to-microservices/index.md)
- [Shared Database to Service Isolation](../../migrations/shared-database-to-microservices/index.md)
- [Batch to Streaming](../../migrations/batch-to-streaming/index.md)

**Need the modern alternatives?** Explore our Gold and Silver patterns:

- [View Gold Patterns](../../gold-patterns/index.md) - Battle-tested solutions
- [View Silver Patterns](../../silver-patterns/index.md) - Specialized patterns

</div>