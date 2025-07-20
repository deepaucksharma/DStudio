---
title: Immutable Laws Quiz
description: Test your understanding of the fundamental axioms with these questions.
type: axiom
difficulty: advanced
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part I: Axioms](index.md) → **Immutable Laws Quiz**

# Immutable Laws Quiz

Test your understanding of the fundamental axioms with these questions.

## Sample Questions

### Question 1
Your service makes 3 sequential calls to a database 100ms away. Minimum possible latency?

a) 100ms (parallel calls)
b) 150ms (connection reuse)
c) 300ms (speed of light) ✓
d) 600ms (round trips)

**Explanation**: Sequential calls cannot be parallelized. Each call requires a round trip (request + response), so 3 calls = 3 × 100ms = 300ms minimum due to physics.

### Question 2
You have 99.9% reliable components. Probability that a 10-component serial system works?

a) 99.9% (weakest link)
b) 99.0% (rough estimate)
c) 99.0% (0.999^10) ✓
d) 90.0% (10% failure)

**Explanation**: In a serial system, all components must work. Probability = 0.999^10 ≈ 0.990 or 99.0%

### Question 3
Your queue is 80% utilized. A 10% traffic increase will increase response time by:

a) 10% (linear)
b) 50% (sublinear)
c) 100% (double) ✓
d) 500% (exponential)

**Explanation**: Using M/M/1 queue theory: At 80% utilization, wait time = 4 × service time. At 88% utilization (80% × 1.1), wait time = 8 × service time. This is a 100% increase.

### Question 4
Which coordination pattern has the lowest latency cost?

a) Two-phase commit
b) Paxos/Raft
c) Gossip protocol ✓
d) Byzantine consensus

**Explanation**: Gossip protocols have O(log N) convergence time and don't require synchronous coordination, making them lowest latency but with eventual consistency trade-off.

### Question 5
A system with partial failure is best described as:

a) Completely broken
b) Completely working
c) Working AND broken ✓
d) About to fail

**Explanation**: Distributed systems can be in superposition - some parts working while others have failed, creating complex failure modes.

### Question 6
The observer effect in distributed systems means:

a) You need more engineers
b) Monitoring changes system behavior ✓
c) Logs are unreliable
d) Metrics are always delayed

**Explanation**: Adding observability (logs, metrics, traces) consumes resources and adds latency, changing the system's behavior.

### Question 7
Human error rate increases most with:

a) System complexity
b) Time of day
c) Stress ✓
d) Experience level

**Explanation**: Under stress (like during an outage), human error rates can increase from 1 in 1000 to 1 in 100 actions.

### Question 8
The hidden cost multiplier in serverless often comes from:

a) Cold starts
b) Memory allocation
c) Retries ✓
d) Deployment time

**Explanation**: Retries can multiply costs dramatically - 5 retries means 6x the invocations, 6x the cost.

### Question 9
Which axiom most directly leads to eventual consistency?

a) Latency ✓
b) Capacity
c) Failure
d) Economics

**Explanation**: Latency constraints make synchronous global consistency too slow, leading to eventual consistency as a practical choice.

### Question 10
The CAP theorem is best understood as a consequence of:

a) Poor design
b) Physics and axioms ✓
c) Database limitations
d) Network protocols

**Explanation**: CAP emerges from the fundamental axioms - latency makes partitions inevitable, forcing a choice between consistency and availability.

## More Practice Questions

Want more questions? Each axiom section includes specific exercises and scenarios to test your understanding.

## Study Tips

1. **Understand the why**: Don't memorize formulas - understand the physics
2. **Work through examples**: Each axiom has "Try This" exercises
3. **Apply to your system**: Use the reflection journal to connect theory to practice
4. **Question everything**: Can you find counter-examples or edge cases?

Remember: These aren't trivia questions - they test whether you truly understand the fundamental constraints that govern all distributed systems.
