---
title: "Law 4: Multidimensional Optimization - Quick Assessment"
description: Objective assessment on the unavoidable trade-offs in distributed systems
type: test
difficulty: advanced
time_limit: 30 minutes
question_count: 30
passing_score: 75
---

# Law 4: The Law of Multidimensional Optimization

⏱️ **Time:** 30 minutes | 📝 **30 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    You cannot optimize everything simultaneously. Every distributed system design involves trading off latency, throughput, consistency, availability, and cost.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] CAP Theorem Trade-off
In CAP theorem, if you choose Availability and Partition tolerance, what must you sacrifice?
- A) Latency
- B) Consistency ✓
- C) Throughput  
- D) Durability

### 2. [True/False] Perfect Optimization
You can optimize latency, throughput, and consistency simultaneously without trade-offs.
- **Answer:** False
- **Reason:** Fundamental trade-offs exist per Law 4 - improving one dimension often degrades others.

### 3. [Fill in Blank] PACELC Extension
In the PACELC theorem, the "ELC" stands for: "Else, choose between _______ and _______."
- **Answer:** Latency, Consistency

### 4. [Multiple Choice] Latency vs Throughput
Which statement best describes the latency-throughput trade-off?
- A) They are independent metrics
- B) Batching improves throughput but increases latency ✓
- C) Lower latency always means higher throughput
- D) They can both be minimized simultaneously

### 5. [True/False] Cost Trade-offs
Adding more replicas always improves both availability and read performance without downsides.
- **Answer:** False
- **Reason:** More replicas increase cost and consistency complexity.

### 6. [One-line] Primary Trade-off
Name the primary trade-off when moving from strong to eventual consistency.
- **Answer:** Data freshness for availability

### 7. [Multiple Choice] Availability Cost
What's the typical cost multiplier for each additional "9" of availability?
- A) 2x
- B) 5x
- C) 10x ✓
- D) 100x

### 8. [Fill in Blank] Optimization Dimensions
The five primary dimensions in distributed system optimization are: latency, throughput, consistency, availability, and _______.
- **Answer:** cost

### 9. [True/False] Linearizability
Linearizability provides the strongest consistency guarantee with no performance impact.
- **Answer:** False
- **Reason:** Linearizability requires coordination, increasing latency.

### 10. [Multiple Choice] Trade-off Triangle
In the "fast, cheap, good" triangle, you can typically achieve:
- A) All three simultaneously
- B) Any two at the expense of the third ✓
- C) Only one at a time
- D) None reliably

---

## Section B: Application (10 questions)

### 11. [Pattern Matching] Consistency Models
Match the consistency model to its trade-off profile:
1. Strong Consistency      A. Low latency, potential stale reads
2. Eventual Consistency    B. High latency, always fresh data
3. Read-after-Write        C. Moderate complexity, session guarantees
4. Bounded Staleness       D. Time-bounded freshness

**Answers:** 1-B, 2-A, 3-C, 4-D

### 12. [Multiple Choice] Read vs Write Optimization
A system optimized for reads typically uses:
- A) Single master with no replicas
- B) Multiple read replicas with eventual consistency ✓
- C) Strong consistency everywhere
- D) No caching

### 13. [Calculate] Replication Factor
If you need 99.99% availability and each node has 99% availability, minimum replication factor?
- **Answer:** 3 (gives 99.9999%)

### 14. [One-line] Sharding Trade-off
What's the main trade-off when increasing the number of shards?
- **Answer:** Better parallelism but harder cross-shard queries

### 15. [Multiple Choice] Cache Trade-off
Adding a cache layer primarily trades:
- A) Consistency for performance ✓
- B) Availability for cost
- C) Throughput for latency
- D) Durability for speed

### 16. [True/False] Async Processing
Asynchronous processing always improves both latency and throughput.
- **Answer:** False
- **Reason:** Async improves throughput but may increase end-to-end latency.

### 17. [Identify Failure] Trade-off Violation
Scenario: "System guarantees <1ms latency, 100% consistency, across global regions"
- **Answer:** Physically impossible due to speed of light

### 18. [Multiple Choice] Batch Size Optimization
Increasing batch size generally:
- A) Reduces latency, reduces throughput
- B) Reduces latency, increases throughput
- C) Increases latency, increases throughput ✓
- D) Increases latency, reduces throughput

### 19. [Fill in Blank] Consistency Window
In a system with 5-second eventual consistency, the _______ window is 5 seconds.
- **Answer:** inconsistency (or staleness)

### 20. [Pattern Match] Use Case to Trade-off
Match use case to acceptable trade-off:
1. Social media likes     A. Eventual consistency OK
2. Bank transfers         B. Strong consistency required
3. Product catalog        C. Read-optimized, stale OK
4. Stock trading          D. Low latency critical

**Answers:** 1-A, 2-B, 3-C, 4-D

---

## Section C: Trade-offs & Optimization (10 questions)

### 21. [Best Choice] E-commerce Cart
For an e-commerce shopping cart, which optimization is typically best?
- A) Strong consistency globally
- B) Session consistency with eventual propagation ✓
- C) No consistency guarantees
- D) Synchronous replication everywhere

### 22. [Rank Order] Latency Priority
Order these operations by typical latency (fastest first):
- Memory cache
- Local disk
- Network call to same DC
- Cross-region replication

**Answer:** Memory cache, Local disk, Network call to same DC, Cross-region replication

### 23. [Multiple Choice] Tunable Consistency
Which database offers tunable consistency levels per operation?
- A) Traditional SQL only
- B) Cassandra ✓
- C) Redis only
- D) File systems

### 24. [One-line] SLA Trade-off
What's the main trade-off when promising a stricter SLA (99.99% vs 99.9%)?
- **Answer:** Higher operational cost and complexity

### 25. [True/False] Microservices Trade-off
Microservices improve all dimensions: latency, consistency, and operational simplicity.
- **Answer:** False
- **Reason:** Microservices increase complexity and network latency.

### 26. [Calculate] Cost Optimization
If read replicas cost $100/month each and serve 1000 req/s, what's the cost per million requests?
- **Answer:** $0.04 (approximately)

### 27. [Multiple Choice] Quorum Trade-off
In a 5-node cluster with quorum reads/writes (3 nodes), you're trading:
- A) Availability for consistency ✓
- B) Consistency for availability
- C) Cost for performance
- D) Nothing - it's optimal

### 28. [Identify] Anti-pattern
Which is an anti-pattern violating Law 4?
- A) Caching frequently accessed data
- B) Using eventual consistency for analytics
- C) Requiring global strong consistency for all operations ✓
- D) Regional data partitioning

### 29. [Best Choice] IoT Telemetry
For IoT telemetry data, optimize for:
- A) Strong consistency
- B) High write throughput with eventual consistency ✓
- C) Synchronous processing
- D) Immediate global visibility

### 30. [Rank] Optimization Priority
For a video streaming service, rank optimization priorities:
1. Throughput
2. Latency  
3. Consistency
4. Cost

**Typical Answer:** 1. Throughput, 2. Cost, 3. Latency, 4. Consistency

---

## Answer Key Summary

**Section A (Fundamentals):** 1-B, 2-False, 3-Latency/Consistency, 4-B, 5-False, 6-Data freshness for availability, 7-C, 8-cost, 9-False, 10-B

**Section B (Application):** 11-(1-B,2-A,3-C,4-D), 12-B, 13-3, 14-Better parallelism but harder cross-shard queries, 15-A, 16-False, 17-Physically impossible, 18-C, 19-inconsistency, 20-(1-A,2-B,3-C,4-D)

**Section C (Trade-offs):** 21-B, 22-Memory/Local/Network/Cross-region, 23-B, 24-Higher cost/complexity, 25-False, 26-$0.04, 27-A, 28-C, 29-B, 30-Throughput/Cost/Latency/Consistency

---

## Quick Reference Card

### The Trade-off Matrix

| If You Want... | You Must Accept... |
|----------------|-------------------|
| **Strong Consistency** | Higher latency, lower availability |
| **High Availability** | Eventual consistency, split-brain risk |
| **Low Latency** | Local decisions, potential inconsistency |
| **High Throughput** | Batching delays, higher latency |
| **Low Cost** | Reduced redundancy, lower availability |

### Common Optimization Patterns

1. **Read-Heavy:** Multiple replicas, caching, eventual consistency
2. **Write-Heavy:** Sharding, async processing, write buffers
3. **Global Scale:** Regional partitions, eventual consistency, CDNs
4. **Financial:** Strong consistency, higher costs, lower throughput
5. **Analytics:** Batch processing, eventual consistency, high throughput

### Remember
- **You can't have it all** - every choice has a trade-off
- **Optimize for your use case** - not all systems need strong consistency
- **Cost is a dimension too** - technical excellence must be economically viable
- **Measure and iterate** - trade-offs change as systems evolve

---

*Ready for the next law? Continue to [Law 5: Distributed Knowledge →](distributed-knowledge-test.md)*