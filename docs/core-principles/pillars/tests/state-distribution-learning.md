---
title: "Pillar 2: State Distribution - Learning Module"
description: Comprehensive assessment on data management, replication, and consistency
type: learning-module
difficulty: intermediate-advanced
total_time: 45 minutes
sections: 3
passing_score: 75
---

# Pillar 2: State Distribution - Learning Module

⏱️ **Total Time:** 45 minutes | 📚 **3 Sections** | ✅ **Passing:** 75%

!!! info "Learning Objectives"
    By completing this module, you will:
    - Master replication strategies and consistency models
    - Understand partitioning schemes and their trade-offs
    - Learn conflict resolution and consensus mechanisms
    - Apply state distribution patterns to real systems

---

## Section A: Replication & Consistency (15 minutes, 20 questions)

### Replication Fundamentals

#### 1. [Multiple Choice] Replication Factor
For critical data with 99.99% availability requirement and 99% node reliability:
- A) 1 replica
- B) 2 replicas
- C) 3 replicas ✓
- D) 5 replicas

#### 2. [True/False] Synchronous Replication
Synchronous replication always provides better durability than asynchronous.
- **Answer:** True
- **Reason:** Data confirmed written before acknowledgment

#### 3. [Fill in Blank]
The _______ problem occurs when different replicas accept conflicting updates.
- **Answer:** split-brain

#### 4. [Pattern Match] Replication Types
Match replication type to characteristic:
1. Master-slave       A. All nodes can accept writes
2. Multi-master      B. One writer, many readers
3. Chain replication C. Sequential propagation
4. Quorum-based     D. Voting for consensus

**Answers:** 1-B, 2-A, 3-C, 4-D

### Consistency Models

#### 5. [Rank Order] Consistency Strength
Order from strongest to weakest:
- Linearizability
- Sequential consistency
- Causal consistency
- Eventual consistency

**Answer:** As listed (Linearizability → Sequential → Causal → Eventual)

#### 6. [Multiple Choice] CAP Choice
A globally distributed social media system should choose:
- A) CP (Consistency + Partition tolerance)
- B) AP (Availability + Partition tolerance) ✓
- C) CA (Consistency + Availability)
- D) None of the above

#### 7. [One-line] Read-after-Write
What does read-after-write consistency guarantee?
- **Answer:** Users see their own writes immediately

#### 8. [True/False] Strong Consistency
Strong consistency eliminates the need for conflict resolution.
- **Answer:** True
- **Reason:** Prevents conflicts from occurring

### Quorum Systems

#### 9. [Calculate] Quorum Size
For 7 replicas with write quorum W=4, minimum read quorum R for consistency?
- **Answer:** 4 (W + R > N, so 4 + 4 > 7)

#### 10. [Multiple Choice] Sloppy Quorum
Sloppy quorum improves:
- A) Consistency
- B) Availability ✓
- C) Partition tolerance
- D) Performance

#### 11. [Fill in Blank]
In quorum systems, _______ nodes ensure at least one node has the latest value.
- **Answer:** overlapping (or intersection)

#### 12. [True/False] Read Quorum
Larger read quorums always improve read performance.
- **Answer:** False
- **Reason:** Must wait for more nodes, increasing latency

### Conflict Resolution

#### 13. [Pattern Match] Resolution Strategies
Match strategy to use case:
1. Last-write-wins    A. Shopping cart merging
2. Vector clocks      B. Simple overwrites
3. CRDTs             C. Detecting concurrent updates
4. Application-specific D. Automatic convergence

**Answers:** 1-B, 2-C, 3-D, 4-A

#### 14. [Multiple Choice] Vector Clock Size
Vector clocks grow with:
- A) Data size
- B) Number of nodes ✓
- C) Time
- D) Network latency

#### 15. [One-line] Tombstones
Why are tombstones needed in distributed deletion?
- **Answer:** Distinguish deletion from absence/not-yet-replicated

#### 16. [True/False] CRDT Merge
CRDTs can be merged without coordination.
- **Answer:** True
- **Reason:** Designed for conflict-free merging

### Consensus Protocols

#### 17. [Multiple Choice] Paxos vs Raft
Main advantage of Raft over Paxos:
- A) Better performance
- B) Understandability ✓
- C) Less messages
- D) No leader needed

#### 18. [Calculate] Byzantine Fault Tolerance
System with 10 nodes. Maximum Byzantine nodes tolerated?
- **Answer:** 3 (less than N/3)

#### 19. [Fill in Blank]
_______ ensures all nodes agree on the same value despite failures.
- **Answer:** Consensus

#### 20. [True/False] 2PC Scalability
Two-phase commit scales well to hundreds of nodes.
- **Answer:** False
- **Reason:** Blocking protocol with O(N) messages

---

## Section B: Partitioning & Sharding (15 minutes, 20 questions)

### Partitioning Strategies

#### 21. [Multiple Choice] Time-Series Data
Best partitioning strategy for time-series data:
- A) Hash partitioning
- B) Range partitioning by time ✓
- C) Random partitioning
- D) Round-robin

#### 22. [Pattern Match] Partitioning Types
Match type to characteristic:
1. Range-based       A. Even distribution
2. Hash-based       B. Ordered access
3. Directory-based  C. Flexible mapping
4. Composite        D. Multi-dimensional

**Answers:** 1-B, 2-A, 3-C, 4-D

#### 23. [One-line] Hot Partition
How do you handle a hot partition problem?
- **Answer:** Split partition or replicate hot data

#### 24. [True/False] Perfect Hash
Perfect hash functions eliminate all hot partitions.
- **Answer:** False
- **Reason:** Access patterns can still create hotspots

### Consistent Hashing

#### 25. [Calculate] Data Movement
100 nodes, 10TB data. Adding 1 node moves approximately:
- **Answer:** 100GB (10TB/101 ≈ 1% of data)

#### 26. [Multiple Choice] Virtual Nodes Purpose
Virtual nodes in consistent hashing:
- A) Increase security
- B) Improve load distribution ✓
- C) Reduce latency
- D) Save memory

#### 27. [Fill in Blank]
_______ determines how many replicas are placed on adjacent nodes in the ring.
- **Answer:** Replication factor

#### 28. [True/False] Ring Topology
Consistent hashing requires physical ring network topology.
- **Answer:** False
- **Reason:** Ring is logical, not physical

### Cross-Partition Operations

#### 29. [Multiple Choice] Distributed Transaction Cost
Cross-partition transactions are expensive due to:
- A) Memory usage
- B) Coordination overhead ✓
- C) CPU usage
- D) Disk I/O

#### 30. [One-line] Denormalization
Why denormalize data in distributed systems?
- **Answer:** Avoid expensive cross-partition joins

#### 31. [Pattern Match] Transaction Patterns
Match pattern to approach:
1. Saga              A. Local transactions only
2. 2PC               B. Compensation-based
3. Event sourcing    C. Strong consistency
4. BASE              D. Event log as truth

**Answers:** 1-B, 2-C, 3-D, 4-A

#### 32. [True/False] ACID Guarantee
Distributed systems can provide full ACID guarantees efficiently.
- **Answer:** False
- **Reason:** Requires expensive coordination

### State Migration

#### 33. [Multiple Choice] Live Migration
During live migration, critical concern is:
- A) CPU usage
- B) Consistency during transfer ✓
- C) Network cable type
- D) Time of day

#### 34. [Calculate] Migration Time
1TB partition, 1Gbps network, what's minimum migration time?
- **Answer:** ~133 minutes (1TB × 8 / 1Gbps / 60)

#### 35. [Fill in Blank]
_______ migration copies data while serving requests, then switches.
- **Answer:** Live (or online)

#### 36. [True/False] Stop-the-World
Stop-the-world migration eliminates consistency issues.
- **Answer:** True
- **Reason:** No concurrent modifications during migration

### Caching Strategies

#### 37. [Multiple Choice] Cache-aside Pattern
Cache-aside pattern is best when:
- A) All data is accessed equally
- B) Read-heavy with sporadic writes ✓
- C) Write-heavy workload
- D) No patterns exist

#### 38. [Pattern Match] Cache Patterns
Match pattern to behavior:
1. Write-through     A. Write to cache and store
2. Write-behind      B. Write to cache, async to store
3. Read-through      C. Cache loads on miss
4. Refresh-ahead     D. Proactive cache warming

**Answers:** 1-A, 2-B, 3-C, 4-D

#### 39. [One-line] Cache Invalidation
Why is cache invalidation considered hard?
- **Answer:** Coordinating state across distributed caches

#### 40. [True/False] Cache Coherence
Distributed caches always maintain coherence automatically.
- **Answer:** False
- **Reason:** Requires explicit invalidation/update protocols

---

## Section C: Advanced Topics (15 minutes, 20 questions)

### Multi-Region Distribution

#### 41. [Multiple Choice] Cross-Region Replication
Primary challenge in geo-replication:
- A) Storage cost
- B) Network latency ✓
- C) CPU usage
- D) Disk speed

#### 42. [Best Choice] Global User Data
For global user profiles with regional access patterns:
- A) Single global database
- B) Regional primaries with global replication ✓
- C) No replication
- D) Cache everything everywhere

#### 43. [Calculate] Speed of Light
Minimum RTT between US East and Europe (~5000km):
- **Answer:** ~33ms (5000km × 2 / 300,000km/s)

#### 44. [True/False] Geo-Partitioning
Geo-partitioning eliminates all cross-region traffic.
- **Answer:** False
- **Reason:** Global users and services still need cross-region access

### State Machines

#### 45. [Multiple Choice] Replicated State Machine
Key requirement for replicated state machines:
- A) Fast network
- B) Deterministic operations ✓
- C) Large memory
- D) Single threading

#### 46. [One-line] Command Log
What does the command log provide in state machine replication?
- **Answer:** Ordered sequence of operations to replay

#### 47. [Fill in Blank]
_______ state machines apply same operations in same order.
- **Answer:** Replicated

#### 48. [True/False] State Machine Recovery
State machines can recover by replaying the log from beginning.
- **Answer:** True
- **Reason:** Deterministic operations produce same state

### Database Technologies

#### 49. [Pattern Match] Database Types
Match database to consistency model:
1. PostgreSQL        A. Eventual consistency
2. Cassandra        B. Strong consistency
3. DynamoDB         C. Tunable consistency
4. Spanner          D. Global consistency

**Answers:** 1-B, 2-C, 3-A, 4-D

#### 50. [Multiple Choice] NewSQL
NewSQL databases primarily solve:
- A) NoSQL limitations
- B) Scalability with ACID ✓
- C) Storage costs
- D) Query complexity

#### 51. [One-line] Polyglot Persistence
What is polyglot persistence?
- **Answer:** Using different databases for different data types

#### 52. [True/False] One-Size-Fits-All
One database technology can efficiently handle all use cases.
- **Answer:** False
- **Reason:** Different patterns require different optimizations

### Performance Optimization

#### 53. [Multiple Choice] Write Amplification
Write amplification is worst in:
- A) Append-only logs
- B) B-trees with many indexes ✓
- C) Hash tables
- D) Linked lists

#### 54. [Calculate] Read Amplification
LSM tree with 7 levels, worst-case read checks:
- **Answer:** 7 levels

#### 55. [Fill in Blank]
_______ compaction merges sorted runs in LSM trees.
- **Answer:** Merge (or leveled)

#### 56. [True/False] Compression
Compression always improves distributed storage performance.
- **Answer:** False
- **Reason:** CPU overhead may outweigh I/O savings

### Real-World Patterns

#### 57. [Best Choice] Social Media Feed
For social media timeline generation:
- A) Join at read time
- B) Precomputed per user ✓
- C) Single global list
- D) No storage, compute always

#### 58. [Multiple Choice] E-commerce Inventory
Inventory counts should use:
- A) Eventual consistency
- B) Strong consistency with reservations ✓
- C) No consistency
- D) Cache only

#### 59. [Scenario] Message Queue
Distributed message queue needs:
- A) Total ordering only
- B) Partitioned ordering with replication ✓
- C) No ordering
- D) Single node only

#### 60. [One-line] Event Sourcing
How does event sourcing handle state distribution?
- **Answer:** State derived from replicated event log

---

## Answer Key Summary

### Section A: Replication (Q1-20)
1-C, 2-True, 3-split-brain, 4-(1-B,2-A,3-C,4-D), 5-As listed, 6-B, 7-See own writes, 8-True, 9-4, 10-B, 11-overlapping, 12-False, 13-(1-B,2-C,3-D,4-A), 14-B, 15-Distinguish deletion, 16-True, 17-B, 18-3, 19-Consensus, 20-False

### Section B: Partitioning (Q21-40)
21-B, 22-(1-B,2-A,3-C,4-D), 23-Split/replicate, 24-False, 25-100GB, 26-B, 27-Replication factor, 28-False, 29-B, 30-Avoid joins, 31-(1-B,2-C,3-D,4-A), 32-False, 33-B, 34-133min, 35-Live, 36-True, 37-B, 38-(1-A,2-B,3-C,4-D), 39-Coordination, 40-False

### Section C: Advanced (Q41-60)
41-B, 42-B, 43-33ms, 44-False, 45-B, 46-Ordered operations, 47-Replicated, 48-True, 49-(1-B,2-C,3-A,4-D), 50-B, 51-Different databases, 52-False, 53-B, 54-7, 55-Merge, 56-False, 57-B, 58-B, 59-B, 60-From event log

---

## Quick Reference Card

### Consistency Models Spectrum
Strong → Weak:
1. **Linearizability** - Real-time ordering
2. **Sequential** - Program order
3. **Causal** - Happens-before
4. **Read-your-writes** - See own updates
5. **Eventual** - Eventually converges

### Replication Strategies
| Strategy | Write Latency | Durability | Use Case |
|----------|--------------|------------|----------|
| Sync | High | Strong | Financial |
| Async | Low | Weak | Analytics |
| Semi-sync | Medium | Good | General |
| Quorum | Medium | Tunable | Cassandra |

### Key Formulas
- **Quorum:** W + R > N (strong consistency)
- **Availability:** 1 - (1 - p)^n
- **Byzantine:** N > 3f (f = faulty nodes)

---

*Continue to [State Distribution Mastery Exam →](state-distribution-exam.md)*