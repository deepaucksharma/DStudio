---
title: "Pillar 1: Work Distribution - Learning Module"
description: Comprehensive objective assessment with progressive difficulty levels
type: learning-module
difficulty: intermediate-advanced
total_time: 45 minutes
sections: 3
passing_score: 75
---

# Pillar 1: Work Distribution - Learning Module

⏱️ **Total Time:** 45 minutes | 📚 **3 Sections** | ✅ **Passing:** 75%

!!! info "Learning Objectives"
    By completing this module, you will:
    - Master work distribution patterns and their trade-offs
    - Understand load balancing strategies and algorithms
    - Learn to handle data locality and task granularity
    - Identify and mitigate common distribution problems

---

## Section A: Foundation Concepts (15 minutes, 20 questions)

### Load Balancing Fundamentals

#### 1. [Multiple Choice] Algorithm Selection
For a system with varying request processing times, which load balancing algorithm is most appropriate?
- A) Round-robin
- B) Random selection
- C) Least outstanding requests ✓
- D) Hash-based routing

#### 2. [True/False] Sticky Sessions
Sticky sessions improve load distribution by ensuring even traffic distribution.
- **Answer:** False
- **Reason:** Sticky sessions can cause uneven load and hot spots

#### 3. [Fill in Blank]
The _______ problem occurs when all clients simultaneously choose the same server.
- **Answer:** thundering herd

#### 4. [Pattern Match] Load Balancing Types
Match the load balancing type to its characteristic:
1. DNS load balancing      A. Application layer decisions
2. Hardware load balancer  B. Geographic distribution
3. Software load balancer  C. Line-rate performance
4. Global load balancer    D. Flexible and programmable

**Answers:** 1-B, 2-C, 3-D, 4-A

### Work Partitioning Strategies

#### 5. [Multiple Choice] Data Sharding
Which sharding strategy provides the most even distribution?
- A) Range-based sharding
- B) Consistent hashing ✓
- C) Directory-based sharding
- D) Geographic sharding

#### 6. [Calculate] Partition Count
For 1TB of data with 100GB partitions, how many partitions needed?
- **Answer:** 10 partitions

#### 7. [One-line] Hot Partition
What causes a hot partition in distributed systems?
- **Answer:** Skewed access patterns or poor key distribution

#### 8. [True/False] Perfect Distribution
Work can always be perfectly evenly distributed across all workers.
- **Answer:** False
- **Reason:** Task indivisibility and varying execution times prevent perfect distribution

### Parallelization Patterns

#### 9. [Multiple Choice] Amdahl's Law
If 90% of a program is parallelizable, maximum speedup with infinite processors is:
- A) 9x
- B) 10x ✓
- C) 90x
- D) Infinite

#### 10. [Fill in Blank]
The _______ pattern divides work into map and reduce phases.
- **Answer:** MapReduce

#### 11. [Pattern Match] Work Patterns
Match pattern to use case:
1. Pipeline          A. Independent task processing
2. Work stealing     B. Sequential stage processing
3. Fork-join        C. Dynamic load balancing
4. Scatter-gather   D. Parallel aggregation

**Answers:** 1-B, 2-C, 3-A, 4-D

### Queue Management

#### 12. [Multiple Choice] Queue Selection
For fair task processing with priorities, use:
- A) FIFO queue
- B) LIFO queue
- C) Priority queue ✓
- D) Circular queue

#### 13. [True/False] Unbounded Queues
Unbounded queues prevent system overload.
- **Answer:** False
- **Reason:** Can cause memory exhaustion and hide backpressure

#### 14. [Calculate] Little's Law
If arrival rate = 100/sec and response time = 2 sec, queue length?
- **Answer:** 200 items

#### 15. [One-line] Work Stealing
What problem does work stealing solve?
- **Answer:** Load imbalance when workers finish at different rates

### Coordination Overhead

#### 16. [Rank Order] Communication Cost
Order by communication overhead (lowest to highest):
- Shared memory
- Local socket
- Network RPC
- Cross-datacenter call

**Answer:** Shared memory, Local socket, Network RPC, Cross-datacenter

#### 17. [Multiple Choice] Coordination-Free
Which operation is naturally coordination-free?
- A) Distributed sum
- B) Distributed maximum
- C) Commutative operations ✓
- D) Ordered operations

#### 18. [Fill in Blank]
The _______ pattern processes data where it resides to minimize movement.
- **Answer:** data locality (or compute-to-data)

#### 19. [True/False] Synchronization Cost
Synchronization cost grows linearly with worker count.
- **Answer:** False
- **Reason:** Often grows quadratically due to all-to-all communication

#### 20. [Calculate] Efficiency
If 8 workers achieve 6x speedup, parallel efficiency is?
- **Answer:** 75% (6/8)

---

## Section B: Implementation Patterns (15 minutes, 20 questions)

### Consistent Hashing

#### 21. [Multiple Choice] Virtual Nodes
Virtual nodes in consistent hashing improve:
- A) Security
- B) Load distribution ✓
- C) Network speed
- D) Storage capacity

#### 22. [Calculate] Node Addition
In consistent hashing with 100 keys and 4 nodes, adding 1 node moves approximately how many keys?
- **Answer:** 20 keys (100/5)

#### 23. [True/False] Hash Collisions
Consistent hashing eliminates all hash collisions.
- **Answer:** False
- **Reason:** Collisions still possible but impact is localized

#### 24. [One-line] Ring Position
How are nodes positioned on a consistent hash ring?
- **Answer:** By hashing node identifier to ring position

### Stream Processing

#### 25. [Pattern Match] Processing Types
Match processing type to characteristic:
1. Batch            A. Continuous processing
2. Stream          B. Periodic large jobs
3. Micro-batch     C. Real-time events
4. Lambda          D. Hybrid approach

**Answers:** 1-B, 2-C, 3-A, 4-D

#### 26. [Multiple Choice] Watermarks
Watermarks in stream processing track:
- A) Memory usage
- B) Event time progress ✓
- C) Network bandwidth
- D) CPU utilization

#### 27. [Fill in Blank]
_______ partitioning ensures related events go to same processor.
- **Answer:** Key-based (or semantic)

#### 28. [True/False] Exactly-Once
Exactly-once processing is easily achievable in distributed streams.
- **Answer:** False
- **Reason:** Requires complex coordination and state management

### Actor Model

#### 29. [Multiple Choice] Actor Communication
Actors communicate exclusively through:
- A) Shared memory
- B) Direct method calls
- C) Message passing ✓
- D) Global variables

#### 30. [One-line] Actor Isolation
What does actor isolation guarantee?
- **Answer:** No shared state between actors

#### 31. [True/False] Actor Ordering
Messages between two actors always arrive in send order.
- **Answer:** True (typically)
- **Reason:** Most actor systems guarantee pairwise ordering

#### 32. [Pattern Match] Actor Patterns
Match pattern to purpose:
1. Supervisor       A. Request routing
2. Router          B. State aggregation
3. Aggregator      C. Failure handling
4. Worker pool     D. Parallel processing

**Answers:** 1-C, 2-A, 3-B, 4-D

### Batch Processing

#### 33. [Multiple Choice] Batch Size
Optimal batch size balances:
- A) Only throughput
- B) Only latency
- C) Throughput and latency ✓
- D) Only memory usage

#### 34. [Calculate] Batch Efficiency
Processing 1000 items in 10 batches vs 1 batch, if per-batch overhead is 100ms?
- **Answer:** 1 second overhead vs 100ms (10x difference)

#### 35. [Fill in Blank]
_______ execution reruns tasks on different workers for fault tolerance.
- **Answer:** Speculative

#### 36. [True/False] Batch Atomicity
All batch processing systems guarantee atomic batch completion.
- **Answer:** False
- **Reason:** Partial failures can occur requiring checkpointing

### Task Scheduling

#### 37. [Multiple Choice] Scheduler Goals
Primary task scheduler goal is:
- A) Minimize makespan ✓
- B) Maximize CPU temperature
- C) Minimize memory usage
- D) Maximize network traffic

#### 38. [Rank Order] Scheduling Priority
Order scheduling strategies by fairness:
- FIFO
- Priority-based
- Fair share
- Deadline-based

**Answer:** Fair share, FIFO, Deadline-based, Priority-based

#### 39. [One-line] Gang Scheduling
What is gang scheduling used for?
- **Answer:** Co-scheduling related tasks together

#### 40. [True/False] Preemption
Task preemption always improves system throughput.
- **Answer:** False
- **Reason:** Context switch overhead can reduce throughput

---

## Section C: Advanced Topics & Troubleshooting (15 minutes, 20 questions)

### Performance Optimization

#### 41. [Multiple Choice] Stragglers
Best mitigation for straggler tasks:
- A) Wait indefinitely
- B) Restart all tasks
- C) Speculative execution ✓
- D) Ignore stragglers

#### 42. [Calculate] Tail Latency
If 99% of requests take 10ms and 1% take 1000ms, average latency?
- **Answer:** 19.9ms

#### 43. [Pattern Match] Optimization Techniques
Match technique to benefit:
1. Batching         A. Reduce per-item overhead
2. Pipelining       B. Hide latency
3. Caching          C. Avoid recomputation
4. Prefetching      D. Anticipate needs

**Answers:** 1-A, 2-B, 3-C, 4-D

#### 44. [True/False] Work Stealing Overhead
Work stealing has zero overhead when load is balanced.
- **Answer:** False
- **Reason:** Periodic steal attempts still occur

### Fault Tolerance

#### 45. [Multiple Choice] Checkpointing
Optimal checkpoint frequency depends on:
- A) Only failure rate
- B) Only checkpoint cost
- C) Failure rate and checkpoint cost ✓
- D) Only recovery time

#### 46. [One-line] Idempotency
Why is idempotency important for work distribution?
- **Answer:** Enables safe retry without side effects

#### 47. [Fill in Blank]
The _______ problem occurs when workers repeatedly fail on the same task.
- **Answer:** poison pill

#### 48. [True/False] Deterministic Execution
Deterministic execution simplifies fault recovery.
- **Answer:** True
- **Reason:** Can replay from checkpoints without divergence

### Monitoring & Debugging

#### 49. [Multiple Choice] Key Metric
Most important work distribution metric:
- A) Total throughput
- B) Worker utilization variance ✓
- C) Network bandwidth
- D) Memory usage

#### 50. [Pattern Match] Problem Indicators
Match symptom to likely cause:
1. Uneven CPU usage      A. Poor partitioning
2. High queue depth      B. Insufficient workers
3. Low throughput        C. Bottleneck stage
4. Frequent timeouts     D. Overloaded workers

**Answers:** 1-A, 2-B, 3-C, 4-D

#### 51. [One-line] Queue Monitoring
What does growing queue depth indicate?
- **Answer:** Arrival rate exceeds processing rate

#### 52. [True/False] Metrics Overhead
Detailed metrics collection has negligible performance impact.
- **Answer:** False
- **Reason:** Can add significant overhead especially for fine-grained tasks

### Anti-patterns & Pitfalls

#### 53. [Identify] Anti-pattern
Which is a work distribution anti-pattern?
- A) Using consistent hashing
- B) Implementing backpressure
- C) Single global task queue for all workers ✓
- D) Local work stealing

#### 54. [Multiple Choice] Convoy Effect
The convoy effect occurs when:
- A) Tasks arrive in groups
- B) Long task blocks short tasks ✓
- C) Workers form clusters
- D) Network packets bunch up

#### 55. [True/False] Naive Sharding
Sharding by user ID always provides good distribution.
- **Answer:** False
- **Reason:** Power users can create hot shards

#### 56. [One-line] Head-of-line Blocking
How does head-of-line blocking affect work distribution?
- **Answer:** One slow task delays all subsequent tasks

### Real-world Scenarios

#### 57. [Best Choice] Video Transcoding
For video transcoding farm, best work distribution:
- A) Round-robin by video
- B) Segment videos into chunks ✓
- C) One video per worker
- D) Random assignment

#### 58. [Multiple Choice] Web Crawling
For distributed web crawling, partition by:
- A) URL hash
- B) Domain ✓
- C) Document size
- D) Random

#### 59. [Calculate] MapReduce Splits
For 10TB data with 128MB splits, number of map tasks?
- **Answer:** ~80,000 tasks

#### 60. [Best Choice] Real-time Analytics
For real-time analytics on user events:
- A) Batch hourly
- B) Stream with windows ✓
- C) Process individually
- D) Store and analyze offline

---

## Answer Key Summary

### Section A: Foundations (Q1-20)
1-C, 2-False, 3-thundering herd, 4-(1-B,2-C,3-D,4-A), 5-B, 6-10, 7-Skewed access, 8-False, 9-B, 10-MapReduce, 11-(1-B,2-C,3-A,4-D), 12-C, 13-False, 14-200, 15-Load imbalance, 16-Listed order, 17-C, 18-data locality, 19-False, 20-75%

### Section B: Implementation (Q21-40)
21-B, 22-20, 23-False, 24-Hash to position, 25-(1-B,2-C,3-A,4-D), 26-B, 27-Key-based, 28-False, 29-C, 30-No shared state, 31-True, 32-(1-C,2-A,3-B,4-D), 33-C, 34-10x, 35-Speculative, 36-False, 37-A, 38-Listed order, 39-Co-scheduling, 40-False

### Section C: Advanced (Q41-60)
41-C, 42-19.9ms, 43-(1-A,2-B,3-C,4-D), 44-False, 45-C, 46-Safe retry, 47-poison pill, 48-True, 49-B, 50-(1-A,2-B,3-C,4-D), 51-Overload, 52-False, 53-C, 54-B, 55-False, 56-Delays queue, 57-B, 58-B, 59-80000, 60-B

---

## Quick Reference Card

### Essential Formulas
- **Little's Law:** L = λW (Queue length = Arrival rate × Wait time)
- **Amdahl's Law:** Speedup = 1/((1-P) + P/N)
- **Efficiency:** E = Speedup / Number of processors
- **Load Factor:** ρ = λ/μ (Arrival rate / Service rate)

### Key Patterns
1. **MapReduce:** Parallel map, shuffle, reduce
2. **Work Stealing:** Dynamic load balancing
3. **Pipeline:** Sequential stage processing
4. **Scatter-Gather:** Fan-out aggregation
5. **Actor Model:** Message-based isolation

### Common Problems & Solutions
| Problem | Solution |
|---------|----------|
| Hot partitions | Consistent hashing, key splitting |
| Stragglers | Speculative execution, timeouts |
| Queue overflow | Backpressure, admission control |
| Uneven load | Work stealing, dynamic partitioning |
| Coordination overhead | Batch operations, local decisions |

---

*Ready for the exam? Continue to [Work Distribution Mastery Exam →](work-distribution-exam.md)*