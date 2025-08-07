---
title: "Law 5: Distributed Knowledge - Quick Assessment"
description: Objective assessment on partial knowledge and consensus in distributed systems
type: test
difficulty: advanced
time_limit: 30 minutes
question_count: 30
passing_score: 75
---

# Law 5: The Law of Distributed Knowledge

⏱️ **Time:** 30 minutes | 📝 **30 questions** | ✅ **Passing:** 75%

!!! abstract "Core Principle"
    No single component can know the complete state of a distributed system. Each node operates with partial, potentially outdated knowledge.

---

## Section A: Fundamentals (10 questions)

### 1. [Multiple Choice] Local Knowledge
What percentage of system state can any single node know with certainty?
- A) 100%
- B) 50%
- C) Only its local state ✓
- D) Depends on network speed

### 2. [Fill in Blank] Consensus Purpose
In distributed systems, _______ algorithms are used to achieve agreement despite partial knowledge.
- **Answer:** Consensus

### 3. [True/False] Global State
A distributed system can maintain a perfectly consistent global state view at all times.
- **Answer:** False
- **Reason:** Network delays and partitions prevent instant global state knowledge.

### 4. [Multiple Choice] Information Propagation
How does information typically spread in distributed systems?
- A) Instantly to all nodes
- B) Through gradual propagation with delays ✓
- C) Only through a central coordinator
- D) Not at all

### 5. [One-line] Byzantine Problem
What does the Byzantine Generals Problem illustrate about distributed knowledge?
- **Answer:** Achieving consensus with unreliable communication/nodes

### 6. [Multiple Choice] Knowledge Staleness
In a distributed system, a node's view of another node's state is:
- A) Always current
- B) Potentially outdated by network delay ✓
- C) Guaranteed fresh within 1 second
- D) Synchronized every millisecond

### 7. [Fill in Blank] Split Brain
A _______ situation occurs when network partition causes nodes to have conflicting views of system state.
- **Answer:** split-brain

### 8. [True/False] Gossip Protocols
Gossip protocols guarantee that all nodes receive information simultaneously.
- **Answer:** False
- **Reason:** Gossip protocols spread information gradually with probabilistic guarantees.

### 9. [Multiple Choice] Partial Failure
What makes partial failures particularly challenging?
- A) They're rare
- B) Nodes have inconsistent views of what failed ✓
- C) They're easy to detect
- D) They affect all nodes equally

### 10. [One-line] FLP Impossibility
What does the FLP theorem prove about consensus?
- **Answer:** Impossible to guarantee consensus with one faulty process

---

## Section B: Application (10 questions)

### 11. [Pattern Matching] Consensus Algorithms
Match the consensus algorithm to its characteristic:
1. Paxos              A. Leader-based, understandable
2. Raft               B. Byzantine fault tolerant
3. PBFT               C. Mathematically proven, complex
4. Gossip             D. Eventually consistent propagation

**Answers:** 1-C, 2-A, 3-B, 4-D

### 12. [Multiple Choice] Quorum Size
In a 5-node cluster, what's the minimum quorum size for consensus?
- A) 1
- B) 2
- C) 3 ✓
- D) 5

### 13. [True/False] Leader Knowledge
In leader-based systems, the leader has complete knowledge of all follower states.
- **Answer:** False
- **Reason:** Leader only knows last acknowledged state, not current state.

### 14. [Calculate] Majority Calculation
For a 7-node cluster, minimum nodes needed for majority consensus?
- **Answer:** 4

### 15. [Multiple Choice] Vector Clocks
Vector clocks help solve the distributed knowledge problem by:
- A) Synchronizing physical time
- B) Tracking causal relationships between events ✓
- C) Preventing all conflicts
- D) Providing global ordering

### 16. [Fill in Blank] Membership
Distributed _______ protocols manage which nodes are part of the active cluster.
- **Answer:** membership (or discovery)

### 17. [One-line] Heartbeat Purpose
What knowledge problem do heartbeats solve in distributed systems?
- **Answer:** Detecting node failures/liveness

### 18. [Multiple Choice] Eventual Consistency
Eventual consistency accepts that:
- A) Nodes never agree
- B) Nodes temporarily have different views ✓
- C) Consistency is not important
- D) All nodes are always synchronized

### 19. [True/False] Snapshot Isolation
Distributed snapshot algorithms can capture exact global state at a point in time.
- **Answer:** False
- **Reason:** Captures consistent cut, not instantaneous global state.

### 20. [Pattern Match] Knowledge Problems
Match the problem to its solution:
1. Stale cache          A. Gossip protocol
2. Node discovery       B. TTL/invalidation
3. Leader election      C. Consensus algorithm
4. State propagation    D. Service discovery

**Answers:** 1-B, 2-D, 3-C, 4-A

---

## Section C: Trade-offs & Design (10 questions)

### 21. [Best Choice] Configuration Management
For distributed configuration, which approach is most reliable?
- A) Hard-code in each service
- B) Centralized configuration service with local caching ✓
- C) Peer-to-peer sharing
- D) Manual updates

### 22. [Multiple Choice] Coordination Service
ZooKeeper/etcd primarily solve which knowledge problem?
- A) Data storage
- B) Distributed coordination and configuration ✓
- C) Message queuing
- D) Load balancing

### 23. [Rank Order] Information Freshness
Order by information freshness (most fresh first):
- Local state
- Cached remote state
- Synchronous RPC result
- Eventually consistent replica

**Answer:** Local state, Synchronous RPC result, Cached remote state, Eventually consistent replica

### 24. [One-line] Lamport Clocks
What problem do Lamport clocks solve?
- **Answer:** Ordering events without synchronized clocks

### 25. [True/False] Consensus Cost
Achieving consensus across N nodes requires O(N²) messages in worst case.
- **Answer:** True
- **Reason:** All-to-all communication in some consensus protocols.

### 26. [Multiple Choice] Service Discovery
Dynamic service discovery addresses:
- A) Network latency
- B) Changing cluster membership ✓
- C) Data consistency
- D) Load balancing

### 27. [Best Choice] Health Checking
For service health checks in a large system:
- A) Direct peer-to-peer checks
- B) Centralized health aggregator with local agents ✓
- C) No health checks
- D) Manual monitoring

### 28. [Fill in Blank] Observability
Distributed _______ provides partial views that must be aggregated for system understanding.
- **Answer:** tracing (or telemetry)

### 29. [Multiple Choice] Clock Synchronization
NTP typically provides clock synchronization within:
- A) Nanoseconds
- B) Microseconds
- C) Milliseconds ✓
- D) Seconds

### 30. [Identify] Anti-pattern
Which is an anti-pattern violating Law 5?
- A) Using consensus for critical decisions
- B) Assuming all nodes have current global state ✓
- C) Implementing heartbeat mechanisms
- D) Using eventual consistency

---

## Answer Key Summary

**Section A (Fundamentals):** 1-C, 2-Consensus, 3-False, 4-B, 5-Achieving consensus with unreliable nodes, 6-B, 7-split-brain, 8-False, 9-B, 10-Impossible to guarantee consensus with one faulty process

**Section B (Application):** 11-(1-C,2-A,3-B,4-D), 12-C, 13-False, 14-4, 15-B, 16-membership, 17-Detecting node failures, 18-B, 19-False, 20-(1-B,2-D,3-C,4-A)

**Section C (Trade-offs):** 21-B, 22-B, 23-Local/Sync RPC/Cached/Eventual, 24-Ordering events without synchronized clocks, 25-True, 26-B, 27-B, 28-tracing, 29-C, 30-B

---

## Quick Reference Card

### Key Concepts

| Concept | Impact on Knowledge |
|---------|-------------------|
| **Network Delay** | Information always outdated by propagation time |
| **Partial Failure** | Different nodes see different failures |
| **Network Partition** | Splits system into isolated knowledge domains |
| **Byzantine Faults** | Nodes may lie about their knowledge |
| **Consensus** | Agreement despite partial knowledge |

### Common Patterns

1. **Gossip Protocol:** Probabilistic information spread
2. **Consensus Algorithm:** Agreement on shared state
3. **Vector Clocks:** Track causal relationships
4. **Heartbeats:** Detect liveness
5. **Service Discovery:** Track membership changes

### Design Principles

- **Assume partial knowledge** - Design for incomplete information
- **Make local decisions** - Don't wait for global state
- **Use timeouts** - Bound waiting for knowledge
- **Cache with TTL** - Accept controlled staleness
- **Implement consensus carefully** - It's expensive

### Remember
- **No node knows everything** - Design for partial knowledge
- **Information has latency** - Knowledge is always somewhat stale
- **Consensus is expensive** - Use it only when necessary
- **Local decisions scale** - Global coordination doesn't

---

*Continue to [Law 6: Cognitive Load →](cognitive-load-test.md)*