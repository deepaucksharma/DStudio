---
title: Two-Phase Commit (2PC)
description: Distributed transaction protocol ensuring atomicity across multiple resources
type: pattern
difficulty: advanced
reading_time: 25 min
prerequisites: 
  - "Distributed transactions basics"
  - "ACID properties"
  - "Network partitions"
pattern_type: "coordination"
when_to_use: "Strong consistency requirements, financial transactions, inventory management"
when_not_to_use: "High-performance systems, microservices, eventual consistency acceptable"
related_axioms:
  - coordination
  - failure
  - latency
related_patterns:
  - "Saga Pattern"
  - "Outbox Pattern"
  - "Event Sourcing"
status: draft
last_updated: 2025-07-21
---

# Two-Phase Commit (2PC)

<div class="navigation-breadcrumb">
<a href="/">Home</a> > <a href="/patterns/">Patterns</a> > Two-Phase Commit
</div>

> "Two-phase commit is the protocol that refuses to die"
> — Pat Helland

## ⚠️ Pattern Under Construction

This pattern documentation is currently being developed. The Two-Phase Commit pattern is a fundamental distributed transaction protocol that ensures atomicity across multiple resources through a prepare and commit phase.

### Coming Soon

- **Core Concepts**: Understanding the prepare and commit phases
- **Implementation Details**: Coordinator and participant roles
- **Failure Scenarios**: Handling coordinator and participant failures
- **Performance Analysis**: Latency implications and blocking behavior
- **Alternatives**: When to use Saga pattern or eventual consistency instead
- **Real-World Examples**: Banking systems and distributed databases

### Quick Overview

Two-Phase Commit (2PC) is a distributed algorithm that coordinates all processes participating in a distributed transaction on whether to commit or abort the transaction. It consists of:

1. **Prepare Phase**: Coordinator asks all participants to prepare
2. **Commit Phase**: Based on responses, coordinator decides commit or abort

### Key Challenges

- Blocking protocol (participants wait for coordinator)
- Single point of failure (coordinator)
- Performance overhead from multiple round trips
- Complexity of failure recovery

---

## Related Resources

### Patterns
- [Saga Pattern](/patterns/saga/) - Alternative for long-running transactions
- [Outbox Pattern](/patterns/outbox/) - Ensuring consistency with messaging
- [Event Sourcing](/patterns/event-sourcing/) - Event-based consistency

### Axioms
- [Coordination Axiom](/part1-axioms/axiom5-coordination/) - Consensus fundamentals
- [Failure Axiom](/part1-axioms/axiom3-failure/) - Handling distributed failures
- [Latency Axiom](/part1-axioms/axiom1-latency/) - Performance implications

---

<div class="navigation-links">
<div class="prev-link">
<a href="/patterns/tunable-consistency/">← Previous: Tunable Consistency</a>
</div>
<div class="next-link">
<a href="/patterns/">Back to Patterns →</a>
</div>
</div>