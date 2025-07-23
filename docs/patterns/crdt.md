---
title: CRDT (Conflict-free Replicated Data Types)
description: Data structures that automatically resolve conflicts in distributed systems
type: pattern
difficulty: advanced
reading_time: 40 min
prerequisites: [eventual-consistency, vector-clocks]
pattern_type: "data-structure"
status: stub
last_updated: 2025-01-23
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **CRDT**

# CRDT (Conflict-free Replicated Data Types)

**Automatic conflict resolution for distributed data**

> *This pattern is currently under development. Content will be added soon.*

## Overview

CRDTs are data structures that can be replicated across multiple nodes in a distributed system, where updates can be applied concurrently without coordination, and conflicts are automatically resolved.

## Types of CRDTs

### State-based CRDTs (CvRDT)
- Merge concurrent states
- Requires commutative merge operation
- Examples: G-Counter, PN-Counter

### Operation-based CRDTs (CmRDT)
- Replicate operations
- Requires commutative operations
- Examples: OR-Set, LWW-Register

## Common CRDT Types

- **G-Counter**: Grow-only counter
- **PN-Counter**: Increment/decrement counter
- **G-Set**: Grow-only set
- **OR-Set**: Observed-Remove set
- **LWW-Register**: Last-Write-Wins register

## Use Cases

- Collaborative editing
- Distributed databases
- Shopping carts
- Real-time synchronization
- Offline-first applications

## Trade-offs

- ✅ No coordination needed
- ✅ Automatic conflict resolution
- ✅ High availability
- ❌ Limited operations
- ❌ Memory overhead
- ❌ Eventual consistency only

## Related Patterns

- [Eventual Consistency](eventual-consistency.md)
- [Vector Clocks](vector-clocks.md)
- [Gossip Protocol](gossip-protocol.md)

---

*This is a stub page. Full content coming soon.*