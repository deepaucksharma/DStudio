---
title: Two-Phase Commit (2PC)
description: Distributed transaction coordination with atomic commit protocol
category: coordination
tags: ["coordination", "patterns"]
---

# Two-Phase Commit (2PC)

!!! info "Pattern Overview"
    **Category**: coordination  
    **Complexity**: Medium  
    **Use Cases**: distributed transactions, data consistency, financial systems

## Problem

Maintaining ACID properties across multiple distributed systems requires coordination to ensure all participants either commit or abort together. Without proper coordination, partial failures can lead to inconsistent state.

## Solution

2PC uses a coordinator to manage a two-phase protocol: prepare phase (vote to commit) and commit phase (actual commit). All participants must agree before any commits, ensuring atomicity across distributed resources.

## Implementation

```python
# Example implementation
class TwoPhaseCommitCoordinator:
    def __init__(self):
        pass
    
    def execute(self):
        # Implementation details
        pass
```

## Trade-offs

**Pros:**
- Provides strong consistency guarantees
- Enables ACID transaction support
- Improves well-understood semantics

**Cons:**
- Increases blocking on coordinator failure
- Requires high latency overhead
- May impact poor scalability

## When to Use

- When you need financial transactions
- For systems that require strong consistency requirements
- In scenarios with small-scale distributed systems

## Related Patterns

- [Pattern 1](../related-pattern-1.md) - Complementary pattern
- [Pattern 2](../related-pattern-2.md) - Alternative approach
- [Pattern 3](../related-pattern-3.md) - Building block pattern

## References

- [External Resource 1](#)
- [External Resource 2](#)
- [Case Study Example](../../case-studies/example.md)
