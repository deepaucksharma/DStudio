---
title: "Pillar 1: Work Distribution - Mastery Exam"
description: Advanced exam testing deep understanding of work distribution concepts
type: mastery-exam
difficulty: expert
time_limit: 60 minutes
question_count: 40
passing_score: 80
---

# Pillar 1: Work Distribution - Mastery Exam

⏱️ **Time:** 60 minutes | 📝 **40 questions** | ✅ **Passing:** 80%

!!! warning "Exam Conditions"
    - This is a closed-book exam format
    - 80% score required to pass
    - Tests synthesis and application of concepts
    - No partial credit for multi-part questions

---

## Part 1: Conceptual Mastery (20 questions, 30 minutes)

### 1. [Multiple Choice] Load Balancer Failure
When a load balancer fails in an active-passive setup, typical failover time is:
- A) < 1 second
- B) 1-5 seconds ✓
- C) 30-60 seconds
- D) > 5 minutes

### 2. [True/False] Consistent Hashing
Consistent hashing with virtual nodes guarantees perfectly uniform distribution.
- **Answer:** False
- **Reason:** Improves but doesn't guarantee perfect uniformity

### 3. [Calculate] Work Efficiency
If 16 workers complete a job in 10 minutes that takes 120 minutes serially, efficiency?
- **Answer:** 75% (120/(16×10) = 0.75)

### 4. [Pattern Match] Failure Modes
Match failure mode to mitigation:
1. Worker crash        A. Heartbeat detection
2. Network partition   B. Quorum decisions
3. Slow worker        C. Speculative execution
4. Corrupted data     D. Checksum validation

**Answers:** 1-A, 2-B, 3-C, 4-D

### 5. [One-line] Two-Phase Commit
Why is 2PC problematic for work distribution?
- **Answer:** Blocking protocol that doesn't scale

### 6. [Multiple Choice] Tail Latency
P99 latency is most affected by:
- A) Average processing time
- B) Stragglers and outliers ✓
- C) Network bandwidth
- D) CPU count

### 7. [Fill in Blank]
The _______ effect occurs when bursty traffic overwhelms buffers.
- **Answer:** bufferbloat

### 8. [Best Choice] Global Work Queue
For a global work distribution system across regions:
- A) Single global queue
- B) Hierarchical queues with regional coordinators ✓
- C) Fully distributed with no coordination
- D) Manual assignment

### 9. [True/False] Work Stealing Scalability
Work stealing scales linearly with worker count.
- **Answer:** False
- **Reason:** Steal attempts create overhead that grows with system size

### 10. [Calculate] Partition Rebalance
System with 1000 partitions across 10 nodes. If 2 nodes fail, partitions per remaining node?
- **Answer:** 125 (1000/8)

### 11. [Multiple Choice] Batch Window
Optimal batch window size is determined by:
- A) Only latency requirements
- B) Only throughput needs
- C) Balance of latency, throughput, and resource constraints ✓
- D) Random selection

### 12. [One-line] Backpressure
What does backpressure prevent in work distribution?
- **Answer:** Resource exhaustion and cascading failures

### 13. [Rank Order] Distribution Strategies
Order by fault tolerance (most to least):
- Stateless random distribution
- Consistent hashing with replicas
- Static assignment
- Single master coordinator

**Answer:** Stateless random, Consistent hashing, Static assignment, Single master

### 14. [True/False] Deterministic Routing
Deterministic routing always improves cache hit rates.
- **Answer:** True
- **Reason:** Same requests go to same workers, improving cache locality

### 15. [Fill in Blank]
_______ scheduling ensures tasks meet their deadlines.
- **Answer:** Deadline-aware (or EDF - Earliest Deadline First)

### 16. [Multiple Choice] Shuffle Phase
In MapReduce, the shuffle phase is typically bounded by:
- A) CPU
- B) Memory
- C) Network ✓
- D) Disk

### 17. [Calculate] Queue Theory
M/M/1 queue with λ=80/sec, μ=100/sec. Average queue length?
- **Answer:** 4 (using ρ/(1-ρ) where ρ=0.8)

### 18. [Pattern Match] Scheduling Algorithms
Match algorithm to characteristic:
1. FIFO              A. Prevents starvation
2. Shortest Job First B. Minimizes average wait
3. Round Robin       C. Fair time sharing
4. Multi-level       D. Different priority classes

**Answers:** 1-A, 2-B, 3-C, 4-D

### 19. [Best Choice] Stream Partitioning
For user session analytics, partition by:
- A) Timestamp
- B) Session ID ✓
- C) Random
- D) Geographic region

### 20. [True/False] Zero-Copy
Zero-copy techniques eliminate all data movement overhead.
- **Answer:** False
- **Reason:** Still requires pointer/reference updates and cache effects

---

## Part 2: Applied Scenarios (20 questions, 30 minutes)

### 21. [Scenario] E-commerce Flash Sale
During a flash sale, best work distribution strategy:
- A) Round-robin all requests
- B) Pre-allocate inventory quotas per worker ✓
- C) Single serialized queue
- D) Random distribution

### 22. [Calculate] Throughput Planning
System needs 1M requests/sec. Each worker handles 1000/sec. With 20% overhead, workers needed?
- **Answer:** 1250 workers (1M/1000 × 1.25)

### 23. [Debug] Uneven Load
Workers show 90%, 10%, 15%, 12% CPU. Most likely cause:
- A) Network issues
- B) Hash function creating hot keys ✓
- C) Hardware differences
- D) OS scheduling

### 24. [True/False] Sticky Sessions
Sticky sessions are compatible with auto-scaling.
- **Answer:** False
- **Reason:** New instances won't receive traffic from existing sessions

### 25. [Design] Real-time Gaming
For multiplayer game state distribution:
- A) All state on single server
- B) Spatial partitioning by game region ✓
- C) Random distribution
- D) Client-side only

### 26. [Multiple Choice] CDC Processing
Change Data Capture streams should be partitioned by:
- A) Timestamp
- B) Table and primary key ✓
- C) Operation type
- D) Random

### 27. [Calculate] Replication Factor
Need 99.999% availability, each node 99% available. Minimum replicas?
- **Answer:** 3 replicas (99.9999% availability)

### 28. [One-line] Hotspot Mitigation
How do you handle a suddenly popular item in a distributed cache?
- **Answer:** Replicate hot items to multiple nodes

### 29. [Pattern Match] Industry Examples
Match company to their work distribution innovation:
1. Google MapReduce    A. Large-scale batch processing
2. Amazon SQS          B. Managed queue service
3. Uber H3             C. Spatial indexing
4. Netflix Hystrix     D. Circuit breaking

**Answers:** 1-A, 2-B, 3-C, 4-D

### 30. [True/False] Lambda Architecture
Lambda architecture eliminates the need for batch processing.
- **Answer:** False
- **Reason:** Combines both batch and stream processing

### 31. [Scenario] Log Processing
For processing 100TB of logs daily:
- A) Single powerful machine
- B) Distributed batch processing ✓
- C) Real-time stream only
- D) Manual analysis

### 32. [Multiple Choice] Kafka Partitions
Kafka partition count should be based on:
- A) Number of topics
- B) Target throughput and consumer count ✓
- C) Disk size
- D) Network bandwidth

### 33. [Calculate] Cost Optimization
Spot instances 70% cheaper but 10% failure rate. Cost efficiency vs on-demand?
- **Answer:** ~67% cost reduction accounting for retries

### 34. [Debug] Cascading Failure
Workers failing in sequence. Most likely cause:
- A) Hardware issues
- B) Retry storms overwhelming system ✓
- C) Network cable
- D) Solar flares

### 35. [Best Choice] ML Training
For distributed ML model training:
- A) Parameter server architecture ✓
- B) Single GPU
- C) CPU only
- D) Manual distribution

### 36. [One-line] Shuffle Optimization
What's the primary optimization for shuffle-heavy workloads?
- **Answer:** Combiners to reduce data movement

### 37. [True/False] Exactly-Once
Exactly-once processing requires distributed transactions.
- **Answer:** False
- **Reason:** Can use idempotency with deduplication

### 38. [Scenario] IoT Ingestion
Millions of IoT devices sending data:
- A) Direct database writes
- B) Queue with batched processing ✓
- C) Synchronous API calls
- D) File uploads

### 39. [Multiple Choice] Fork-Join Pool
Fork-Join pools are best for:
- A) I/O bound tasks
- B) CPU-bound recursive tasks ✓
- C) Network operations
- D) Database queries

### 40. [Calculate] Batch vs Stream
Batch every hour vs stream processing. If each event is 1KB and 1M events/hour, memory difference?
- **Answer:** Batch needs ~1GB buffer, stream needs minimal buffer

---

## Answer Key

### Part 1: Conceptual (Q1-20)
1-B, 2-False, 3-75%, 4-(1-A,2-B,3-C,4-D), 5-Blocking/doesn't scale, 6-B, 7-bufferbloat, 8-B, 9-False, 10-125, 11-C, 12-Resource exhaustion, 13-Listed order, 14-True, 15-Deadline-aware, 16-C, 17-4, 18-(1-A,2-B,3-C,4-D), 19-B, 20-False

### Part 2: Applied (Q21-40)
21-B, 22-1250, 23-B, 24-False, 25-B, 26-B, 27-3, 28-Replicate hot items, 29-(1-A,2-B,3-C,4-D), 30-False, 31-B, 32-B, 33-67%, 34-B, 35-A, 36-Combiners, 37-False, 38-B, 39-B, 40-1GB vs minimal

---

## Performance Evaluation

### Score Interpretation
- **32-40 correct (80-100%):** Expert level - Ready for production systems
- **28-31 correct (70-79%):** Proficient - Need more practice
- **24-27 correct (60-69%):** Developing - Review fundamentals
- **< 24 correct (<60%):** Beginner - Start with learning module

### Key Areas to Review if Failed
1. **Load Balancing:** Algorithms, failure modes, sticky sessions
2. **Partitioning:** Consistent hashing, hot spots, rebalancing
3. **Queue Theory:** Little's Law, M/M/1 queues, backpressure
4. **Distributed Processing:** MapReduce, streaming, actor model
5. **Fault Tolerance:** Replication, speculation, checkpointing

---

*Continue to [Pillar 2: State Distribution →](state-distribution-learning.md)*