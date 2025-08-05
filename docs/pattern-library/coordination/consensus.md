---
title: Consensus Pattern
description: Achieving agreement among distributed nodes in the presence of failures
type: pattern
difficulty: advanced
reading_time: 30 min
excellence_tier: gold
pattern_status: recommended
introduced: 1989-01
current_relevance: mainstream
related_laws:
  - asynchronous-reality
  - correlated-failure
  - distributed-knowledge
category: coordination
essential_question: How do we coordinate distributed components effectively using consensus pattern?
last_updated: 2025-07-20
modern_examples:
  - {'company': 'etcd', 'implementation': 'Raft consensus for Kubernetes configuration management', 'scale': 'Powers millions of Kubernetes clusters globally'}
  - {'company': 'Apache Kafka', 'implementation': 'KRaft consensus replacing Zookeeper dependency', 'scale': 'Manages metadata for trillions of messages/day'}
  - {'company': 'CockroachDB', 'implementation': 'Raft consensus for distributed SQL transactions', 'scale': 'Handles billions of transactions with strong consistency'}
prerequisites:
production_checklist:
  - Choose consensus algorithm (Raft preferred over Paxos)
  - Configure cluster size (3, 5, or 7 nodes typical)
  - Set election timeout (150-300ms recommended)
  - Implement leader lease for read optimization
  - Monitor leader stability and election frequency
  - Configure snapshot frequency for log compaction
  - Test network partition scenarios
  - Implement graceful node addition/removal
  - Set up monitoring for consensus health
  - Plan for split-brain prevention
related_pillars:
  - truth
  - control
status: complete
tagline: Master consensus pattern for distributed systems success
when_not_to_use: High-throughput data processing, eventually consistent systems
when_to_use: Leader election, distributed configuration, replicated state machines
---


## Essential Question

**How do we coordinate distributed components effectively using consensus pattern?**


# Consensus Pattern

!!! success "🏆 Gold Standard Pattern"
    **Distributed Agreement** • etcd, Kafka, CockroachDB proven
    
    The foundational pattern for achieving agreement in distributed systems. Consensus enables leader election, configuration management, and coordinated decision-making despite failures.
    
    **Key Success Metrics:**
    - etcd: Powers millions of Kubernetes clusters reliably
    - Kafka KRaft: Manages metadata for trillions of messages
    - CockroachDB: Strong consistency for global SQL databases

## The Essential Question

**How can distributed nodes agree on a single value when networks are unreliable, nodes can fail, and there's no global clock?**

## When to Use / When NOT to Use

<div class="decision-box">
<h4>🎯 Consensus Algorithm Selection</h4>

**Use Consensus When:**
- Leader election required (single coordinator)
- Configuration management (consistent view)
- Distributed transactions (atomic commit)
- Replicated state machines (log replication)
- Strong consistency essential (no split-brain)

**Don't Use Consensus When:**
- Eventually consistent is acceptable → Use CRDTs/Gossip
- Single node can decide → Use local algorithms
- Read-heavy workload → Use caching/replication
- Partition tolerance > consistency → Use AP systems
- Latency critical (< 10ms) → Use local decisions

**Algorithm Choice:**
- **Raft**: New systems, understandability critical
- **Multi-Paxos**: Proven systems, need flexibility
- **PBFT**: Byzantine faults possible
- **Blockchain**: Permissionless environments
</div>

### Decision Framework

**Choose your consensus algorithm:**
- **New systems**: Use Raft for simplicity
- **Existing Paxos expertise**: Use Multi-Paxos
- **Byzantine environment**: Use PBFT/Tendermint
- **High throughput**: Consider batching with any algorithm

---

## Visual Overview: Consensus Flow

**Core Process:**
1. **Propose** → Node suggests a value
2. **Promise** → Majority agrees to consider it
3. **Accept** → Majority accepts the value
4. **Commit** → Value is officially decided

## Level 1: Intuition

### The Essential Concepts

<div class="axiom-box">
<h4>🔬 Core Consensus Properties</h4>

1. **Agreement**: All nodes decide the same value
2. **Validity**: Decided value was proposed by someone
3. **Termination**: Eventually a decision is made
4. **Integrity**: Each node decides at most once

**The FLP Result**: In asynchronous systems with one faulty process, no algorithm can guarantee both safety (agreement) and liveness (termination). Real systems choose safety and use timeouts for practical liveness.
</div>

### Algorithm Comparison Matrix

| Aspect | Raft | Multi-Paxos | EPaxos | PBFT |
|--------|------|-------------|--------|------|
| **Understandability** | ✅ Excellent | 🟡 Complex | 🔴 Very Complex | 🔴 Very Complex |
| **Leader-based** | ✅ Yes (efficient) | ✅ Yes (efficient) | ❌ No (optimal latency) | ✅ Yes (primary) |
| **Byzantine Tolerance** | ❌ None | ❌ None | ❌ None | ✅ Full |
| **Message Complexity** | O(n) | O(n) | O(n) | O(n²) |
| **Latency (stable)** | 1 RTT | 1 RTT | 1 RTT | 2-3 RTT |
| **Conflict Resolution** | Leader decides | Leader decides | Complex ordering | View changes |
| **Production Use** | etcd, Consul | Chubby, Spanner | Research | Blockchain |

### Raft State Transitions

**Node States:**
- **Follower** → Receives heartbeats, converts to candidate on timeout
- **Candidate** → Requests votes, becomes leader with majority
- **Leader** → Replicates log entries, sends heartbeats

**Paxos vs Multi-Paxos Efficiency:**
- **Single Paxos**: 6 message rounds for 3 decisions (expensive)
- **Multi-Paxos**: 4 message rounds for 3 decisions (leader optimization)

### Implementation Strategy

| Need | Recommendation | Rationale |
|------|----------------|----------|
| **Production system** | Use etcd/Consul | Battle-tested, operational tools |
| **Learning/Research** | Study Paxos theory | Foundational understanding |
| **Custom system** | Implement Raft | Simpler than Paxos |
| **Byzantine faults** | Use Tendermint | Proven BFT implementation |

### Paxos Phases

**Phase 1 (Prepare):**
- Proposer sends prepare(n) to acceptors
- Acceptors promise not to accept proposals < n
- Return any previously accepted value

**Phase 2 (Accept):**  
- Proposer sends accept(n,v) to acceptors
- Acceptors accept if n ≥ promised number
- Majority acceptance = consensus achieved

**Multi-Paxos Optimization:**
- Elect stable leader once
- Skip Phase 1 for subsequent proposals
- Fast path: 1 round vs 2 rounds per decision

### Replicated Log Structure

**Log Organization:**
- Each slot runs separate Paxos instance
- Slots decided independently but in order
- Leader elected once, reused for all slots

**Example Log Entries:**
- Slot 0: Configuration change
- Slot 1: Set X=5  
- Slot 2: Set Y=10
- Slot 3: Delete Z
- Slot 4: Set X=7

## Algorithm Selection Guide

### Choose Based on Requirements

| Requirement | Algorithm | Reasoning |
|-------------|-----------|----------|
| **Simple to understand** | Raft | Clear leader election, log replication |
| **Network instability** | Multi-Paxos | Handles leader changes gracefully |
| **Byzantine faults** | PBFT/Tendermint | Tolerates malicious nodes |
| **Low latency** | EPaxos | Leaderless, optimal latency |
| **High throughput** | Batched Raft | Amortize consensus overhead |

### Performance Characteristics

**Crash Fault Tolerant:**
- Commit Latency = 1.5 × RTT (stable leader)
- Throughput ∝ Leader_CPU / Message_Size
- Election Time = Election_Timeout + RTT

**Byzantine Fault Tolerant:**
- Commit Latency = 3 × RTT (3-phase protocol)  
- Message Complexity = O(n²) per operation
- Throughput ∝ Network_Bandwidth / n²

### Algorithm Quick Reference

| Algorithm | Architecture | Best For | Trade-offs |
|-----------|-------------|----------|------------|
| **Raft** | Leader-based | New systems | Simple but leader bottleneck |
| **Multi-Paxos** | Leader-based | Production systems | Robust but complex |
| **PBFT** | Primary-backup | Byzantine faults | Secure but O(n²) messages |
| **EPaxos** | Leaderless | Low latency | Optimal latency but complex conflicts |

### Raft Election Process

**Election Steps:**
1. **Timeout**: Follower doesn't receive heartbeat → becomes candidate
2. **Campaign**: Candidate increments term, votes for self, requests votes
3. **Majority**: If majority votes received → becomes leader
4. **Heartbeats**: New leader sends heartbeats to maintain authority
5. **Accept**: Followers accept new leader, reset election timers

### Log Replication Mechanics

**Replication Flow:**
1. **Client request** arrives at leader
2. **Log entry** created with current term
3. **AppendEntries** sent to all followers  
4. **Majority confirmation** required for commit
5. **Apply to state machine** once committed

**Consistency Guarantees:**
- Log entries committed only after majority replication
- Followers that lag behind catch up automatically
- Term numbers ensure log consistency across leadership changes

### Byzantine Fault Tolerant Consensus

**Process Flow:**
1. Client initiates request
2. System processes request
3. Response returned with result


### Consensus Anti-Patterns

**Architecture Components:**
- Service layer
- Processing components
- Data storage
- External integrations


### Consensus Performance Tuning

**Architecture Components:**
- Service layer
- Processing components
- Data storage
- External integrations


### etcd Operation Flow

**Process Flow:**
1. Client initiates request
2. System processes request
3. Response returned with result


#### Production Examples
**Google Spanner:**
- Uses Paxos groups for each data shard
- TrueTime API provides global timestamps via GPS/atomic clocks  
- Two-phase commit coordinated across Paxos groups
- Wait for clock uncertainty before commit

**CockroachDB:**
- Multi-Raft: One Raft group per 64MB range
- Lease holder for reads (no consensus needed)
- Write intents + parallel commits for throughput
- Hybrid logical clocks for causality without TrueTime

## Theoretical Foundations

### FLP Impossibility Result

**The Problem:**
No deterministic consensus algorithm can guarantee both safety and liveness in asynchronous systems with even one faulty process.

**Why It Matters:**
- Cannot distinguish slow nodes from failed nodes
- No global clock for coordination
- Network delays can be unbounded

**Practical Solutions:**
- **Partial synchrony**: Assume eventual delivery (Paxos)
- **Randomization**: Probabilistic termination (Raft)
- **Failure detectors**: Unreliable but useful hints (PBFT)

### Advanced Protocol Variants

| Protocol | Latency | Complexity | Best For |
|----------|---------|------------|----------|
| **Classic Paxos** | 2 RTT | Medium | Learning |
| **Fast Paxos** | 1.5 RTT | High | Low latency |
| **EPaxos** | 1 RTT | Very High | Optimal latency |
| **Vertical Paxos** | Variable | High | Membership changes |

---

*"In distributed systems, consensus is the art of getting everyone to agree when no one trusts anyone completely."*

---

## Related Laws & Pillars

### Fundamental Laws
This pattern directly addresses:

- **[Law 1: Correlated Failure ⛓️](core-principles/laws/correlated-failure/)**: Consensus handles node failures and network partitions
- **[Law 2: Asynchronous Reality ⏱️](../../core-principles/laws/asynchronous-reality/)**: FLP impossibility shows async consensus limits
- **[Law 3: Emergent Chaos 🌪️](core-principles/laws/emergent-chaos/)**: Multiple consensus attempts create emergent behaviors
- **[Law 4: Multidimensional Optimization ⚖️](core-principles/laws/multidimensional-optimization/)**: CAP theorem trade-offs in consensus
- **[Law 5: Distributed Knowledge 🧠](core-principles/laws/distributed-knowledge/)**: No single node knows complete state

### Foundational Pillars
Consensus implements:

- **[Pillar 2: Distribution of State 🗃️](core-principles/core-principles/pillars/state-distribution/)**: Replicated state machines
- **[Pillar 3: Distribution of Truth 🔍](core-principles/core-principles/pillars/truth-distribution/)**: Agreement on single truth
- **[Pillar 4: Distribution of Control 🎮](core-principles/core-principles/pillars/control-distribution/)**: Leader election and coordination

## Related Patterns

### Core Dependencies
- **[Leader Election](pattern-library/leader-election)**: Uses consensus for choosing leaders
- **[Distributed Lock](pattern-library/distributed-lock)**: Built on consensus primitives
- **[Two-Phase Commit](pattern-library/two-phase-commit)**: Alternative for distributed transactions

### Complementary Patterns
- **[Circuit Breaker](pattern-library/circuit-breaker)**: Protects consensus operations
- **[Saga Pattern](pattern-library/saga)**: Alternative to consensus for long-running transactions
- **[Event Sourcing](pattern-library/event-sourcing)**: Can use consensus for ordering events

## Decision Matrix

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Patterns
- **[Write-Ahead Log](pattern-library/wal)**: Critical for consensus durability
- **[Gossip Protocol](pattern-library/gossip-protocol)**: Alternative for eventual consistency
- **[Vector Clocks](pattern-library/vector-clocks)**: Track causality without consensus

---

**Previous**: [← Circuit Breaker Pattern](../../pattern-library/resilience/circuit-breaker.md) | **Next**: [CQRS (Command Query Responsibility Segregation) →](../../pattern-library/data-management/cqrs.md)
