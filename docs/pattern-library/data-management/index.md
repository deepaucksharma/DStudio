# Data Management Patterns

Patterns for storage, replication, consistency, and caching in distributed systems.

## Overview

Data management patterns address the complex challenges of storing, accessing, and maintaining data across distributed nodes. These patterns help you navigate trade-offs between:

- **Consistency** - Keeping data synchronized
- **Availability** - Ensuring data access
- **Partition Tolerance** - Handling network splits
- **Performance** - Optimizing data operations

## Pattern Categories

### Storage Patterns
- **Shared Database** - Single logical database
- **Database per Service** - Service autonomy
- **Polyglot Persistence** - Right tool for each job
- **Data Lake** - Centralized raw data storage

### Replication Patterns
- **Master-Slave** - Read scaling with single writer
- **Multi-Master** - Multiple write nodes
- **Chain Replication** - Sequential replication
- **Quorum Replication** - Voting-based consistency

### Consistency Patterns
- **Saga** - Distributed transactions
- **Two-Phase Commit** - Strong consistency
- **Event Sourcing** - Event-based state
- **CQRS** - Separate read/write models

### Caching Patterns
- **Cache-Aside** - Application-managed cache
- **Read-Through** - Transparent cache loading
- **Write-Through** - Synchronous cache updates
- **Write-Behind** - Asynchronous cache writes

## Quick Decision Guide

| Need | Pattern |
|------|---------|
| Strong consistency | Two-Phase Commit |
| Eventually consistent transactions | Saga |
| Read performance | Read replicas + Caching |
| Write performance | Sharding + Write-Behind |
| Audit trail | Event Sourcing |
| Complex queries | CQRS |

## CAP Theorem Implications

Each pattern makes different CAP trade-offs:

- **CP Systems**: Favor consistency over availability
- **AP Systems**: Favor availability over consistency
- **CA Systems**: Not possible in distributed systems

---

*Browse individual patterns below or return to the [Pattern Library](../).*