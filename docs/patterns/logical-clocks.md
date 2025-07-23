---
title: Logical Clocks (Lamport Clocks)
description: Order events in distributed systems without synchronized physical clocks
type: pattern
category: specialized
difficulty: intermediate
reading_time: 30 min
prerequisites: [distributed-systems-basics]
when_to_use: When dealing with specialized challenges
when_not_to_use: When simpler solutions suffice
status: stub
last_updated: 2025-01-23
---
<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **Logical Clocks (Lamport Clocks)**

# Logical Clocks (Lamport Clocks)

**Ordering events without synchronized clocks**

> *This pattern is currently under development. Content will be added soon.*

## Overview

Logical clocks, introduced by Leslie Lamport, provide a way to order events in a distributed system without requiring synchronized physical clocks. They establish a happens-before relationship between events.

## Lamport Clock Rules

1. **Local Event**: Increment clock by 1
2. **Send Message**: Increment clock, attach timestamp
3. **Receive Message**: Set clock to max(local_clock, message_timestamp) + 1

## Properties

- **Happens-Before**: If A → B, then Clock(A) < Clock(B)
- **Partial Ordering**: Can't distinguish concurrent events
- **Monotonic**: Clock values always increase

## Implementation Example

```text
Process P1: C1=0
Process P2: C2=0

P1: Local event (C1=1)
P1: Send message to P2 with timestamp 1
P2: Receive (C2 = max(0,1)+1 = 2)
P2: Local event (C2=3)
```

## Use Cases

- Event ordering in distributed logs
- Distributed debugging
- Causal consistency
- Database replication

## Limitations

- Can't detect concurrent events
- No notion of real time
- Requires message passing for synchronization

## Related Patterns

- [Vector Clocks](vector-clocks.md) - Extension for concurrency detection
- [Consensus](consensus.md)
- [Event Sourcing](event-sourcing.md)

---

*This is a stub page. Full content coming soon.*