---
title: Distributed Systems Glossary
description: Comprehensive definitions of terms used throughout The Compendium of Distributed Systems.
type: reference
difficulty: advanced
reading_time: 10 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Reference](index.md) → **Distributed Systems Glossary**

# Distributed Systems Glossary

---

## A

### Law (Law)
Fundamental constraint that cannot be violated in distributed systems. The Compendium identifies 7 core laws (formerly laws).

**Examples**: [Asynchronous Reality ⏳](../part1-laws/axiom2-asynchrony/index.md), [Multidimensional Optimization ⚖️](../part1-laws/axiom4-tradeoffs/index.md)

### At-Least-Once Delivery
Messages may be delivered multiple times but will not be lost. Requires idempotent processing.

**Trade-offs**: Higher reliability vs. duplicate handling complexity

**Related**: [Idempotent Receiver](../patterns/idempotent-receiver.md), [Outbox Pattern](../patterns/outbox.md)

### Availability
Percentage of time a system is operational. Often measured as "nines".

**Formula**: `Availability = MTBF / (MTBF + MTTR)`

**Examples**: 99.9% = 8.77 hours/year, 99.99% = 52.6 minutes/year

## B

### Bulkhead Pattern
Isolation pattern preventing failures from spreading between components.

**Implementation**: Separate thread pools, connection pools, compute resources

**Related**: [Circuit Breaker](../patterns/circuit-breaker.md), [Correlated Failure ⛓️](../part1-laws/axiom1-failure/index.md)

### Byzantine Fault
Components behave arbitrarily, sending conflicting information to different parts.

**Examples**: Malicious actors, hardware corruption, inconsistent software behavior

**Related**: [Correlated Failure ⛓️](../part1-laws/axiom1-failure/index.md), consensus algorithms

## C

### CAP Theorem
Distributed systems can provide at most two of: Consistency, Availability, Partition tolerance.

**Implication**: Must choose between consistency and availability during partitions

**Related**: [Truth Pillar](../part2-pillars/truth/index.md), [Multidimensional Optimization ⚖️](../part1-laws/axiom4-tradeoffs/index.md)

### Circuit Breaker
Prevents cascade failures by failing fast when error thresholds exceeded.

**States**: Closed (normal), Open (failing fast), Half-Open (testing recovery)

**Implementation**: [Circuit Breaker Pattern](../patterns/circuit-breaker.md)

### Consensus
**Definition**: Agreement among distributed nodes on a single value or state, even in the presence of failures.

**Algorithms**: Raft, Paxos, PBFT

**Trade-offs**: Strong consistency vs. availability and performance

**Related**: [Multidimensional Optimization ⚖️](../part1-laws/axiom4-tradeoffs/index.md), [Leader Election](../patterns/leader-election.md)

### Consistent Hashing
Distributes data across nodes with minimal disruption when adding/removing nodes.

**Benefits**: Minimal data movement, even load distribution

**Use Cases**: Distributed caches, data partitioning

### CQRS (Command Query Responsibility Segregation)
Separates read and write operations into different models.

**Benefits**: Optimized read/write paths, scalability, flexibility

**Implementation**: [CQRS Pattern](../patterns/cqrs.md)

### CRDT (Conflict-free Replicated Data Type)
Replicated data structure updated independently without coordination.

**Types**: G-Counter, PN-Counter, OR-Set, LWW-Register

**Use Cases**: Collaborative editing, distributed databases

## D

### Distributed Transaction
Transaction spanning multiple databases/services requiring coordination.

**Patterns**: Two-Phase Commit, Saga, Outbox

**Challenges**: Network failures, partial commits, performance

### DynamoDB
**Definition**: Amazon's highly available key-value database designed around the principles from the original Dynamo paper.

**Key Features**: Eventually consistent, consistent hashing, automatic scaling

**Case Study**: [Amazon's Dynamo Database](../case-studies/amazon-dynamo.md)

## E

### Eventually Consistent
System becomes consistent given no new updates.

**Benefits**: High availability, partition tolerance, performance

**Examples**: DNS, shopping carts, social media feeds

### Event Sourcing
Stores state changes as sequence of events rather than current state.

**Benefits**: Audit trail, temporal queries, replay capability

**Implementation**: [Event Sourcing Pattern](../patterns/event-sourcing.md)

## F

### Failure Detector
Monitors system health and determines node/service failures.

**Types**: Perfect (impossible), Eventually Perfect, Strong, Weak

**Implementation**: Heartbeats, timeouts, gossip protocols

### Fallacies of Distributed Computing
Eight false assumptions that lead to poor designs: Network is reliable, latency is zero, bandwidth is infinite, network is secure, topology doesn't change, one administrator, transport cost is zero, network is homogeneous.

**Reference**: [8 Fallacies Section](../introduction/index.md#fallacies)

## G

### Gossip Protocol
Nodes periodically exchange state with random peers for eventual propagation.

**Benefits**: Scalable, fault-tolerant, self-healing

**Use Cases**: Failure detection, membership management, data replication

## H

### Hinted Handoff
Temporarily stores data for failed nodes, delivering upon recovery.

**Benefits**: Improved availability, eventual consistency

**Use Cases**: Distributed databases, cache systems

### Happens-Before Relation
**Definition**: Partial ordering of events in a distributed system that captures potential causality relationships.

**Notation**: a → b (event a happens before event b)

**Implementation**: Logical clocks, vector clocks

## I

### Idempotency
Applying operation multiple times has same effect as once.

**Importance**: Critical for retry mechanisms and at-least-once delivery

**Implementation**: [Idempotent Receiver Pattern](../patterns/idempotent-receiver.md)

### Isolation Levels
**ACID**: Read Uncommitted, Read Committed, Repeatable Read, Serializable

**Distributed**: Eventual, Causal, Strong

## J

### Jitter
Random timing variation to prevent synchronized behavior.

**Use Cases**: Retry backoff, heartbeat intervals, cache refresh

**Benefits**: Prevents thundering herd, spreads load

## L

### Leader Election
Choosing single coordinator node to avoid split-brain.

**Algorithms**: Bully, Ring, Raft

**Implementation**: [Leader Election Pattern](../patterns/leader-election.md)

### Little's Law
**Formula**: L = λW (queue length = arrival rate × wait time)

**Applications**: Capacity planning, performance analysis

**Related**: [Quantitative Toolkit](../quantitative/littles-law.md)

### Logical Clock
Orders events without physical time synchronization.

**Types**: Lamport timestamps, vector clocks

**Purpose**: Establish causality, maintain event ordering

## M

### Microservices
Small, independently deployable services.

**Benefits**: Independent scaling, technology diversity, fault isolation

**Challenges**: Network complexity, distributed debugging, data consistency

### MTBF (Mean Time Between Failures)
Average time between failures.

**Formula**: Total operational time / number of failures

### MTTR (Mean Time To Repair)
Average repair time.

**Components**: Detection + diagnosis + fix + recovery time

## O

### Outbox Pattern
Stores outgoing messages in same transaction as business data.

**Benefits**: Transactional guarantees, reliable delivery

**Implementation**: [Outbox Pattern](../patterns/outbox.md)

## P

### Partition Tolerance
Continues operating despite network partitions.

**CAP Theorem**: Choose between consistency and availability during partitions

**Strategies**: Quorum consensus, graceful degradation

### Pillar
Five foundational concepts: Work, State, Truth, Control, Intelligence.

**Reference**: [Part II: Pillars](../part2-pillars/index.md)

## Q

### Quorum
Minimum nodes required for valid operation.

**Formula**: (N/2) + 1 for N nodes

**Example**: 3 of 5 nodes must agree

## R

### Raft Consensus
Understandable consensus algorithm.

**Components**: Leader election, log replication, safety

**Implementation**: [Leader Election pattern](../patterns/leader-election.md)

### Read Repair
Fixes inconsistencies during reads by updating stale replicas.

**Types**: Synchronous (blocking), asynchronous (background)

### Replica
Data copy maintained on multiple nodes.

**Types**: Master-slave, master-master, leaderless

**Consistency**: Strong, eventual, causal

## S

### Saga Pattern
Manages distributed transactions through local transactions with compensations.

**Types**: Choreography (event-driven), Orchestration (centralized)

**Implementation**: [Saga Pattern](../patterns/saga.md)

### Sharding
Horizontal partitioning across databases/servers.

**Strategies**: Range-based, hash-based, directory-based

**Challenges**: Rebalancing, cross-shard queries, hot spots

### Split-Brain
System splits into parts each believing it's the only operational component.

**Causes**: Network partitions, timing failures

**Prevention**: Quorum requirements, external coordination

## T

### Two-Phase Commit (2PC)
Ensures all participants commit or abort transaction.

**Phases**: Prepare (vote), Commit/Abort (decision)

**Problems**: Blocking, coordinator failure, performance

## V

### Vector Clock
Captures causality relationships between events.

**Format**: Array of counters, one per node

**Implementation**: [Emergent Chaos 🌪️](../part1-laws/axiom3-emergence/index.md)

## W

### Write-Ahead Log (WAL)
Changes logged before applying to database.

**Benefits**: Durability, crash recovery, replication

**Use Cases**: Databases, message queues, consensus algorithms

---

## Acronyms Quick Reference

- **ACID**: Atomicity, Consistency, Isolation, Durability
- **BASE**: Basically Available, Soft state, Eventual consistency
- **CAP**: Consistency, Availability, Partition tolerance
- **CRDT**: Conflict-free Replicated Data Type
- **CQRS**: Command Query Responsibility Segregation
- **DNS**: Domain Name System
- **MTBF**: Mean Time Between Failures
- **MTTR**: Mean Time To Repair
- **PACELC**: Partition tolerance, Availability, Consistency, Else Latency, Consistency
- **RBAC**: Role-Based Access Control
- **RPC**: Remote Procedure Call
- **SLA**: Service Level Agreement
- **SLI**: Service Level Indicator
- **SLO**: Service Level Objective
- **WAL**: Write-Ahead Log

---

