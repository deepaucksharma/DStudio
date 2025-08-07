---
title: "Pillar 1: Work Distribution - Quick Assessment"
description: Objective assessment on dividing and coordinating computational tasks in distributed systems
type: test
difficulty: advanced
time_limit: 25 minutes
question_count: 25
passing_score: 75
---

# Pillar 1: Work Distribution

⏱️ **Time:** 25 minutes | 📝 **25 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    Effectively dividing and coordinating computational tasks across distributed resources for optimal performance and resource utilization.

---

## Section A: Fundamentals (10 questions)

### 1. [Pattern Matching] Work Distribution Patterns
Match the pattern to its use case:
1. MapReduce        A. Parallel batch processing
2. Work Stealing    B. Dynamic load balancing
3. Fork-Join        C. Recursive decomposition
4. Pipeline         D. Sequential stages

**Answers:** 1-A, 2-B, 3-C, 4-D

### 2. [Multiple Choice] Load Balancing Algorithm
Which algorithm provides the best distribution for varying request costs?
- A) Round-robin
- B) Least connections ✓
- C) Random
- D) Fixed assignment

### 3. [True/False] Perfect Distribution
Work can always be perfectly evenly distributed across all nodes.
- **Answer:** False
- **Reason:** Task granularity, data locality, and varying node capabilities prevent perfect distribution.

### 4. [Fill in Blank] Amdahl's Law
Amdahl's Law states that speedup is limited by the _______ portion of the program.
- **Answer:** sequential (or serial)

### 5. [One-line] Work Stealing
What problem does work stealing solve in task distribution?
- **Answer:** Imbalanced load when some workers finish early

### 6. [Multiple Choice] Sharding Strategy
For even data distribution, the best sharding key is:
- A) Timestamp
- B) Uniformly distributed hash ✓
- C) Sequential ID
- D) User location

### 7. [Calculate] Parallel Speedup
If 80% of work is parallelizable across 4 cores, maximum speedup?
- **Answer:** 2.5x (using Amdahl's Law)

### 8. [True/False] Stateless Workers
Stateless workers always provide better work distribution.
- **Answer:** True
- **Reason:** Any worker can handle any request, maximizing flexibility.

### 9. [Fill in Blank] The _______ pattern divides work into fixed-size chunks processed independently.
- **Answer:** batch (or chunk)

### 10. [Multiple Choice] Task Granularity
Optimal task size for distribution is:
- A) As small as possible
- B) As large as possible
- C) Balanced with overhead costs ✓
- D) Always 1MB

---

## Section B: Implementation (10 questions)

### 11. [Multiple Choice] Consistent Hashing
Consistent hashing primarily solves:
- A) Security issues
- B) Redistribution when nodes join/leave ✓
- C) Network latency
- D) Data compression

### 12. [Pattern Match] Queue Types
Match queue type to characteristic:
1. FIFO Queue       A. Priority handling
2. Priority Queue   B. Fair processing
3. Work Queue      C. Task distribution
4. Delay Queue     D. Scheduled execution

**Answers:** 1-B, 2-A, 3-C, 4-D

### 13. [One-line] Hot Partition
What causes a "hot partition" in distributed systems?
- **Answer:** Uneven access patterns or poor key distribution

### 14. [True/False] Sticky Sessions
Sticky sessions improve work distribution efficiency.
- **Answer:** False
- **Reason:** They can cause uneven load and reduce flexibility.

### 15. [Multiple Choice] Backpressure Purpose
Backpressure mechanisms prevent:
- A) Data loss
- B) System overload ✓
- C) Network failures
- D) Security breaches

### 16. [Fill in Blank] In actor model, work is distributed through _______ passing.
- **Answer:** message

### 17. [Calculate] Worker Efficiency
If 10 workers process 1000 tasks/second total, per-worker throughput?
- **Answer:** 100 tasks/second

### 18. [Multiple Choice] Stream Processing
Stream processing distributes work by:
- A) Batch size
- B) Time windows and partitions ✓
- C) Random assignment
- D) Manual allocation

### 19. [Best Choice] Heterogeneous Cluster
For clusters with different node capabilities:
- A) Equal work distribution
- B) Weighted distribution by capacity ✓
- C) Only use identical nodes
- D) Random distribution

### 20. [True/False] Data Locality
Ignoring data locality in work distribution has no performance impact.
- **Answer:** False
- **Reason:** Network transfer costs can dominate processing time.

---

## Section C: Optimization (5 questions)

### 21. [Rank Order] Distribution Overhead
Order by overhead (lowest to highest):
- Shared memory
- Message passing
- RPC call
- Database coordination

**Answer:** Shared memory, Message passing, RPC call, Database coordination

### 22. [Multiple Choice] Straggler Mitigation
Best approach for handling slow workers:
- A) Wait for all to complete
- B) Speculative execution ✓
- C) Ignore slow workers
- D) Restart the job

### 23. [One-line] Circuit Breaker
How do circuit breakers affect work distribution?
- **Answer:** Temporarily remove failing nodes from rotation

### 24. [Best Choice] Batch vs Stream
For real-time analytics with late data:
- A) Pure batch processing
- B) Pure stream processing
- C) Lambda architecture (both) ✓
- D) Manual processing

### 25. [Identify] Anti-pattern
Which is a work distribution anti-pattern?
- A) Using consistent hashing
- B) Implementing work stealing
- C) Single global work queue bottleneck ✓
- D) Load-based routing

---

## Answer Key Summary

**Section A:** 1-(1-A,2-B,3-C,4-D), 2-B, 3-False, 4-sequential, 5-Imbalanced load, 6-B, 7-2.5x, 8-True, 9-batch, 10-C

**Section B:** 11-B, 12-(1-B,2-A,3-C,4-D), 13-Uneven access patterns, 14-False, 15-B, 16-message, 17-100, 18-B, 19-B, 20-False

**Section C:** 21-Memory/Message/RPC/Database, 22-B, 23-Remove failing nodes, 24-C, 25-C

---

## Quick Reference Card

### Work Distribution Patterns

| Pattern | Best For | Key Benefit |
|---------|----------|-------------|
| **MapReduce** | Batch processing | Massive parallelism |
| **Work Stealing** | Dynamic workloads | Auto-balancing |
| **Sharding** | Data partitioning | Horizontal scaling |
| **Pipeline** | Stream processing | Stage isolation |
| **Actor Model** | Concurrent tasks | Message isolation |

### Load Balancing Strategies

1. **Round-robin:** Simple, equal distribution
2. **Least connections:** Adaptive to load
3. **Weighted:** Accounts for capacity
4. **Consistent hashing:** Minimal redistribution
5. **Geographic:** Latency optimization

### Key Metrics

- **Utilization:** % of capacity in use
- **Throughput:** Tasks completed/time
- **Latency:** Task completion time
- **Queue depth:** Pending work
- **Load variance:** Distribution evenness

### Remember
- **Data locality matters** - Move computation to data
- **Avoid hotspots** - Monitor and rebalance
- **Handle stragglers** - Don't let one slow node delay all
- **Size tasks appropriately** - Balance granularity with overhead

---

*Continue to [Pillar 2: State Distribution →](state-distribution-test.md)*