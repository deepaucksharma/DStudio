---
type: pattern
category: coordination
title: Index
description: 'Patterns for consensus, time synchronization, and resource coordination in distributed systems.'
---

# Coordination Patterns

Patterns for consensus, synchronization, and distributed algorithms.

## Overview

Coordination patterns solve the fundamental challenge of getting distributed nodes to work together coherently. These patterns address problems like:

- **Consensus** - Agreement among nodes
- **Time Synchronization** - Coordinated clocks and ordering
- **Leader Election** - Choosing coordinators
- **Resource Coordination** - Managing shared resources

## Available Patterns

### Consensus & Agreement
- **[Consensus](../coordination/consensus.md)** - Achieving agreement among distributed nodes (Paxos, Raft, PBFT)
- **[Leader Election](../coordination/leader-election.md)** - Selecting a single node for coordination
- **[Generation Clock](../coordination/generation-clock.md)** - Monotonic counter for detecting stale leaders

### Time & Ordering
- **[Logical Clocks](../coordination/logical-clocks.md)** - Lamport clocks for causal ordering without physical time
- **[Hybrid Logical Clocks (HLC)](../coordination/hlc.md)** - Combining physical and logical time
- **[Clock Synchronization](../coordination/clock-sync.md)** - Synchronizing physical clocks across nodes

### Resource Management
- **[Distributed Lock](../coordination/distributed-lock.md)** - Mutual exclusion across distributed nodes
- **[Lease](../coordination/lease.md)** - Time-bound resource ownership with automatic expiration

## Quick Decision Guide

| Need | Pattern |
|------|---------|
| Strong consistency | Paxos/Raft |
| Resource locking | Distributed Lock |
| Single coordinator | Leader Election |
| Causality tracking | Vector Clocks |
| Automatic conflict resolution | CRDTs |

## CAP Considerations

Coordination patterns make different trade-offs:

- **Strong Coordination**: Sacrifices availability during partitions
- **Weak Coordination**: Allows progress with potential conflicts
- **Optimistic Coordination**: Assumes success, handles conflicts later
- **Pessimistic Coordination**: Prevents conflicts upfront

---

*Explore individual patterns below or return to the [Pattern Library](../).*
- [Emergent Leader](emergent-leader.md)
- [Distributed Queue](distributed-queue.md)
- [Leader Follower](leader-follower.md)
- [Two Phase Commit](two-phase-commit.md)
- [Cas](cas.md)
- [State Watch](state-watch.md)
- [Actor Model](actor-model.md)
- [Low High Water Marks](low-high-water-marks.md)

## Patterns
