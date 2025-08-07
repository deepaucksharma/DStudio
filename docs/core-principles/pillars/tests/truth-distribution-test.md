---
title: "Pillar 3: Truth Distribution - Quick Assessment"
description: Objective assessment on achieving consensus and maintaining truth in distributed systems
type: test
difficulty: advanced
time_limit: 25 minutes
question_count: 25
passing_score: 75
---

# Pillar 3: Truth Distribution

⏱️ **Time:** 25 minutes | 📝 **25 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Establishing and maintaining a consistent view of truth across distributed components through consensus, ordering, and conflict resolution.

---

## Section A: Fundamentals (10 questions)

### 1. [True/False] Single Source
Paxos and Raft solve the same fundamental problem.
- **Answer:** True
- **Reason:** Both solve distributed consensus.

### 2. [Fill in Blank] Byzantine fault tolerance handles up to _______ of nodes being malicious.
- **Answer:** 1/3 (one-third)

### 3. [Multiple Choice] Consensus Requirement
Minimum nodes needed for consensus in a cluster:
- A) 2
- B) 3 ✓
- C) 5
- D) 7

### 4. [Pattern Matching] Clock Types
Match clock type to purpose:
1. Physical clock      A. Causal ordering
2. Logical clock       B. Global ordering
3. Vector clock        C. Wall time
4. Hybrid clock        D. Best of both

**Answers:** 1-C, 2-B, 3-A, 4-D

### 5. [One-line] Total Order
What guarantees does total order broadcast provide?
- **Answer:** All nodes see messages in same order

### 6. [Multiple Choice] Leader Election
Split-brain in leader election causes:
- A) Performance issues
- B) Multiple leaders simultaneously ✓
- C) No leaders
- D) Memory leaks

### 7. [True/False] Lamport Timestamps
Lamport timestamps can determine if events are concurrent.
- **Answer:** False
- **Reason:** They provide total order but can't detect concurrency.

### 8. [Calculate] Byzantine Nodes
In a 10-node Byzantine system, maximum Byzantine nodes tolerated?
- **Answer:** 3 nodes

### 9. [Fill in Blank] The _______ problem demonstrates impossibility of consensus with unreliable communication.
- **Answer:** Two Generals (or Byzantine Generals)

### 10. [Multiple Choice] Happens-before
Event A happens-before B means:
- A) A occurred first in wall time
- B) A causally precedes B ✓
- C) A and B are concurrent
- D) B depends on A's completion

---

## Section B: Implementation (10 questions)

### 11. [Multiple Choice] Raft Leader
In Raft, a leader is elected based on:
- A) Lowest ID
- B) Highest term and most recent log ✓
- C) Random selection
- D) Network speed

### 12. [Pattern Match] Consensus Use Cases
Match consensus algorithm to use case:
1. ZAB (Zookeeper)     A. Blockchain
2. PBFT                B. Configuration management
3. Proof of Work       C. Byzantine environments
4. Raft                D. General purpose

**Answers:** 1-B, 2-C, 3-A, 4-D

### 13. [One-line] Clock Skew
How does clock skew affect distributed systems?
- **Answer:** Causes incorrect event ordering and timeouts

### 14. [True/False] Eventual Consistency
Eventual consistency guarantees all nodes will have identical state immediately.
- **Answer:** False
- **Reason:** Convergence happens over time, not immediately.

### 15. [Fill in Blank] CRDTs achieve consistency through _______ operations.
- **Answer:** commutative (or conflict-free)

### 16. [Multiple Choice] Quorum Intersection
Why must read and write quorums intersect?
- A) Performance optimization
- B) Guarantee seeing latest write ✓
- C) Network efficiency
- D) Storage optimization

### 17. [Calculate] Quorum Size
For 7 nodes with W+R>N guarantee, if W=4, minimum R?
- **Answer:** 4 (since 4+4>7)

### 18. [Multiple Choice] Version Vectors
Version vectors are superior to timestamps because:
- A) They're smaller
- B) They detect concurrent updates ✓
- C) They're faster
- D) They use less network

### 19. [Best Choice] Global Transaction
For global distributed transactions, best approach:
- A) Two-phase commit
- B) Saga pattern ✓
- C) No transactions
- D) Single global lock

### 20. [True/False] Consensus Performance
Consensus protocols have constant time complexity.
- **Answer:** False
- **Reason:** Typically O(n) or O(n²) message complexity.

---

## Section C: Advanced Concepts (5 questions)

### 21. [Rank Order] Consensus Latency
Order by typical latency (fastest to slowest):
- Single node decision
- Raft consensus
- Byzantine consensus
- Blockchain consensus

**Answer:** Single node, Raft, Byzantine, Blockchain

### 22. [Multiple Choice] Linearizability Point
The linearization point of an operation is:
- A) When it starts
- B) When it completes
- C) Single instant it appears to occur ✓
- D) Average of start and end

### 23. [One-line] FLP Theorem
What does FLP theorem prove about asynchronous consensus?
- **Answer:** Impossible to guarantee with one faulty process

### 24. [Best Choice] Time Synchronization
For distributed system time sync, use:
- A) Manual clock setting
- B) NTP/PTP protocols ✓
- C) GPS only
- D) No synchronization

### 25. [Identify] Anti-pattern
Which violates truth distribution principles?
- A) Using logical clocks
- B) Implementing Raft
- C) Assuming synchronized physical clocks ✓
- D) Using CRDTs

---

## Answer Key Summary

**Section A:** 1-True, 2-1/3, 3-B, 4-(1-C,2-B,3-A,4-D), 5-All nodes see same order, 6-B, 7-False, 8-3, 9-Two Generals, 10-B

**Section B:** 11-B, 12-(1-B,2-C,3-A,4-D), 13-Incorrect ordering/timeouts, 14-False, 15-commutative, 16-B, 17-4, 18-B, 19-B, 20-False

**Section C:** 21-Single/Raft/Byzantine/Blockchain, 22-C, 23-Impossible with faulty process, 24-B, 25-C

---

## Quick Reference Card

### Consensus Algorithms

| Algorithm | Fault Model | Use Case | Complexity |
|-----------|------------|----------|------------|
| **Paxos** | Crash | Academic/Proof | Complex |
| **Raft** | Crash | Production | Simple |
| **PBFT** | Byzantine | Security-critical | High |
| **ZAB** | Crash | Zookeeper | Moderate |

### Clock Types

1. **Physical:** Wall clock time, NTP sync
2. **Logical:** Lamport timestamps, total order
3. **Vector:** Detect causality and concurrency
4. **Hybrid:** Combines physical + logical

### Truth Patterns

- **Single Source:** One authoritative copy
- **Consensus:** Agreement on value
- **CRDTs:** Merge without conflict
- **Event Sourcing:** Truth from event log
- **Blockchain:** Immutable shared truth

### Remember
- **Consensus is expensive** - Use wisely
- **Time is relative** - Don't trust clocks
- **Impossibility results exist** - Know the limits
- **Truth can be eventual** - Not always immediate

---

*Continue to [Pillar 4: Control Distribution →](control-distribution-test.md)*