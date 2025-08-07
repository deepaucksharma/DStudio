---
title: "Pillar 2: State Distribution - Quick Assessment"
description: Objective assessment on managing and replicating data across distributed nodes
type: test
difficulty: advanced
time_limit: 25 minutes
question_count: 25
passing_score: 75
---

# Pillar 2: State Distribution

⏱️ **Time:** 25 minutes | 📝 **25 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Managing data placement, replication, and consistency across distributed nodes to ensure durability, availability, and performance.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] Replication Factor
Which replication factor provides best balance of durability and cost?
- A) 1 (no replication)
- B) 2 (one replica)
- C) 3 (two replicas) ✓
- D) 5+ (many replicas)

### 2. [True/False] Synchronous Replication
Synchronous replication always provides better durability than asynchronous.
- **Answer:** True
- **Reason:** Data is confirmed written to replicas before acknowledging.

### 3. [Fill in Blank] The _______ theorem defines trade-offs between consistency, availability, and partition tolerance.
- **Answer:** CAP

### 4. [Pattern Matching] Consistency Models
Match consistency model to guarantee:
1. Linearizability     A. Reads see all prior writes
2. Sequential         B. Real-time ordering
3. Causal            C. Program order preserved
4. Eventual          D. Convergence over time

**Answers:** 1-B, 2-C, 3-A, 4-D

### 5. [One-line] Split-brain
What causes split-brain in distributed state?
- **Answer:** Network partition with multiple masters

### 6. [Multiple Choice] Quorum Reads
In a 5-replica system, quorum reads require:
- A) 1 replica
- B) 2 replicas
- C) 3 replicas ✓
- D) 5 replicas

### 7. [Calculate] Write Availability
With 3 replicas and quorum writes (2), what % of nodes can fail?
- **Answer:** 33% (1 node)

### 8. [True/False] Primary-replica
Primary-replica replication eliminates all consistency issues.
- **Answer:** False
- **Reason:** Replication lag causes temporary inconsistency.

### 9. [Fill in Blank] _______ partitioning distributes data based on key ranges.
- **Answer:** Range (or horizontal)

### 10. [Multiple Choice] Conflict Resolution
Last-write-wins conflict resolution risks:
- A) Performance issues
- B) Lost updates ✓
- C) Network overhead
- D) Storage waste

---

## Section B: Implementation (10 questions)

### 11. [Multiple Choice] Sharding Strategy
Best sharding approach for time-series data:
- A) Hash-based
- B) Time-range based ✓
- C) Random
- D) Geographic

### 12. [One-line] Hot Key Problem
How do you handle frequently accessed keys in sharding?
- **Answer:** Replicate hot keys or split into sub-keys

### 13. [True/False] Cross-shard Transactions
Distributed transactions across shards are as efficient as local transactions.
- **Answer:** False
- **Reason:** Require coordination protocols with significant overhead.

### 14. [Pattern Match] Storage Types
Match storage type to use case:
1. Key-value       A. Document storage
2. Column-family   B. Simple lookups
3. Document store  C. Time-series data
4. Graph database  D. Relationships

**Answers:** 1-B, 2-C, 3-A, 4-D

### 15. [Fill in Blank] Vector clocks detect _______ relationships between updates.
- **Answer:** causal (or concurrent)

### 16. [Multiple Choice] Read Repair
Read repair in eventually consistent systems:
- A) Prevents all inconsistencies
- B) Fixes inconsistencies when detected ✓
- C) Slows down reads significantly
- D) Requires strong consistency

### 17. [Calculate] Storage Overhead
With 3-way replication and 1TB data, total storage needed?
- **Answer:** 3TB

### 18. [Multiple Choice] Consensus for State
Which consensus algorithm is simplest to understand?
- A) Paxos
- B) Raft ✓
- C) PBFT
- D) Viewstamped Replication

### 19. [Best Choice] Session State
For web session state, best approach is:
- A) Local server storage
- B) Sticky sessions
- C) Distributed cache with TTL ✓
- D) Replicate to all servers

### 20. [True/False] Tombstones
Tombstones in distributed systems can be deleted immediately.
- **Answer:** False
- **Reason:** Must be retained until all replicas acknowledge deletion.

---

## Section C: Optimization (5 questions)

### 21. [Rank Order] Consistency Strength
Order from strongest to weakest consistency:
- Linearizability
- Sequential consistency
- Causal consistency
- Eventual consistency

**Answer:** Linearizability, Sequential, Causal, Eventual

### 22. [Multiple Choice] Cache Invalidation
Hardest problem in distributed caching:
- A) Cache sizing
- B) Cache invalidation ✓
- C) Cache warming
- D) Cache sharding

### 23. [One-line] Write Amplification
What causes write amplification in replicated systems?
- **Answer:** Multiple copies written for each logical write

### 24. [Best Choice] Global Database
For a globally distributed database, optimize for:
- A) Strong global consistency
- B) Regional consistency with async replication ✓
- C) No replication
- D) Full mesh replication

### 25. [Identify] Anti-pattern
Which is a state distribution anti-pattern?
- A) Sharding by consistent hash
- B) Storing session in distributed cache
- C) Synchronous replication across continents ✓
- D) Using read replicas

---

## Answer Key Summary

**Section A:** 1-C, 2-True, 3-CAP, 4-(1-B,2-C,3-A,4-D), 5-Network partition with multiple masters, 6-C, 7-33%, 8-False, 9-Range, 10-B

**Section B:** 11-B, 12-Replicate or split hot keys, 13-False, 14-(1-B,2-C,3-A,4-D), 15-causal, 16-B, 17-3TB, 18-B, 19-C, 20-False

**Section C:** 21-Linear/Sequential/Causal/Eventual, 22-B, 23-Multiple copies per write, 24-B, 25-C

---

## Quick Reference Card

### Replication Strategies

| Strategy | Consistency | Performance | Use Case |
|----------|------------|-------------|----------|
| **Synchronous** | Strong | Lower write | Financial |
| **Asynchronous** | Eventual | Higher write | Analytics |
| **Semi-sync** | Bounded | Balanced | General |
| **Quorum** | Tunable | Moderate | Cassandra |

### Partitioning Schemes

1. **Range:** Ordered data, range queries
2. **Hash:** Even distribution, point queries
3. **List:** Known categories
4. **Composite:** Multi-dimensional
5. **Consistent Hash:** Dynamic clusters

### Consistency Spectrum

Strong → Eventual:
- Linearizability (real-time)
- Sequential (program order)
- Causal (happens-before)
- Read-your-writes
- Monotonic reads
- Eventual (convergence)

### Remember
- **Replication ≠ Backup** - Different purposes
- **Consistency has cost** - Choose appropriately
- **Partition for scalability** - But mind the joins
- **Cache carefully** - Invalidation is hard

---

*Continue to [Pillar 3: Truth Distribution →](truth-distribution-test.md)*