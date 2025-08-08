---
title: The 7 Fundamental Laws
description: Immutable laws that govern all distributed systems
---

# The 7 Fundamental Laws

These laws are not guidelines or best practices - they are immutable constraints that govern every distributed system.

## The Laws

1. **[The Inevitability of Failure](laws/correlated-failure.md)**
   - Components will fail
   - Failures cascade and correlate
   - Perfect reliability is impossible

2. **[The Economics of Scale](laws/economic-reality.md)**
   - Resources are finite
   - Cost drives architectural decisions
   - Trade-offs are inevitable

3. **[The Constraints of Time](laws/temporal-constraints.md)**
   - Perfect synchronization is impossible
   - Time ordering is relative
   - Causality requires explicit tracking

4. **[The Reality of Networks](laws/asynchronous-reality.md)**
   - Networks partition
   - Latency is non-zero
   - Bandwidth is limited

5. **[The Human Factor](laws/cognitive-load.md)**
   - Humans have cognitive limits
   - Complexity must be managed
   - Operations require human understanding

6. **[The Nature of Knowledge](laws/distributed-knowledge.md)**
   - Global state is unknowable
   - Information propagates slowly
   - Decisions use partial information

7. **[The Emergence of Chaos](laws/emergent-chaos.md)**
   - Complex systems exhibit emergent behavior
   - Small changes have large effects
   - Predictability decreases with scale

## Understanding the Laws

Each law represents a fundamental constraint that cannot be overcome, only managed. Understanding these laws helps you:

- **Design realistic systems** that acknowledge fundamental limitations
- **Make informed trade-offs** between competing concerns
- **Predict failure modes** before they occur
- **Build resilient architectures** that embrace constraints

## Pattern Relationships

These laws directly influence pattern selection:

- **Failure patterns** emerge from Law 1
- **Optimization patterns** emerge from Law 2
- **Coordination patterns** emerge from Laws 3, 4, and 6
- **Operational patterns** emerge from Law 5
- **Adaptive patterns** emerge from Law 7

Continue to [The 5 Pillars](../pillars/) to see how these laws translate into architectural principles.

