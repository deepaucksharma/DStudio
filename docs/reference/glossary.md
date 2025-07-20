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
[Home](/) → [Reference](/reference/) → **Distributed Systems Glossary**

# Distributed Systems Glossary

Comprehensive definitions of terms used throughout The Compendium of Distributed Systems.

---

## A

### Axiom
**Definition**: A fundamental constraint or law that cannot be violated in distributed systems. The Compendium identifies 8 core axioms that drive all distributed systems behavior.

**Examples**: [Latency Axiom](../part1-axioms/axiom1-latency/index.md) (speed of light), [Capacity Axiom](../part1-axioms/axiom2-capacity/index.md) (finite resources)

**Usage**: "All patterns emerge from the 8 axioms of distributed systems."

### At-Least-Once Delivery
**Definition**: A message delivery guarantee where messages may be delivered multiple times but will not be lost. Requires idempotent processing.

**Trade-offs**: Higher reliability vs. complexity of handling duplicates

**Related**: [Idempotent Receiver Pattern](../patterns/idempotent-receiver.md), [Outbox Pattern](../patterns/outbox.md)

### Availability
**Definition**: The percentage of time a system is operational and accessible. Often measured as "nines" (99.9% = "three nines").

**Calculation**: `Availability = MTBF / (MTBF + MTTR)` where MTBF = Mean Time Between Failures, MTTR = Mean Time To Repair

**Examples**: 99.9% = 8.77 hours downtime/year, 99.99% = 52.6 minutes downtime/year

## B

### Bulkhead Pattern
**Definition**: Isolation pattern that prevents failures in one component from affecting others, like watertight compartments in a ship.

**Implementation**: Separate thread pools, connection pools, or compute resources for different operations

**Related**: [Circuit Breaker](../patterns/circuit-breaker.md), [Failure Axiom](../part1-axioms/axiom3-failure/index.md)

### Byzantine Fault
**Definition**: A failure mode where components can behave arbitrarily, including sending conflicting information to different parts of the system.

**Examples**: Malicious actors, hardware corruption, software bugs causing inconsistent behavior

**Related**: [Failure Axiom](../part1-axioms/axiom3-failure/index.md), consensus algorithms

## C

### CAP Theorem
**Definition**: Fundamental theorem stating that distributed systems can provide at most two of: Consistency, Availability, and Partition tolerance.

**Practical Implication**: Since network partitions are inevitable, systems must choose between consistency and availability

**Related**: [Truth Pillar](../part2-pillars/truth/index.md), [Coordination Axiom](../part1-axioms/axiom5-coordination/index.md)

### Circuit Breaker
**Definition**: Pattern that prevents cascade failures by failing fast when error thresholds are exceeded, like an electrical circuit breaker.

**States**: Closed (normal), Open (failing fast), Half-Open (testing recovery)

**Implementation**: [Circuit Breaker Pattern](../patterns/circuit-breaker.md)

### Consensus
**Definition**: Agreement among distributed nodes on a single value or state, even in the presence of failures.

**Algorithms**: Raft, Paxos, PBFT

**Trade-offs**: Strong consistency vs. availability and performance

**Related**: [Coordination Axiom](../part1-axioms/axiom5-coordination/index.md), [Leader Election](../patterns/leader-election.md)

### Consistent Hashing
**Definition**: Technique for distributing data across nodes where adding/removing nodes minimally disrupts existing assignments.

**Benefits**: Minimal data movement, even load distribution

**Use Cases**: Distributed caches, data partitioning

### CQRS (Command Query Responsibility Segregation)
**Definition**: Pattern separating read and write operations into different models to optimize each independently.

**Benefits**: Optimized read/write paths, scalability, flexibility

**Implementation**: [CQRS Pattern](../patterns/cqrs.md)

### CRDT (Conflict-free Replicated Data Type)
**Definition**: Data structure that can be replicated across multiple nodes and updated independently without coordination, guaranteeing eventual consistency.

**Types**: G-Counter, PN-Counter, OR-Set, LWW-Register

**Use Cases**: Collaborative editing, distributed databases

## D

### Distributed Transaction
**Definition**: Transaction that spans multiple databases or services, requiring coordination to maintain ACID properties.

**Patterns**: Two-Phase Commit, Saga Pattern, Outbox Pattern

**Challenges**: Network failures, partial commits, performance overhead

### DynamoDB
**Definition**: Amazon's highly available key-value database designed around the principles from the original Dynamo paper.

**Key Features**: Eventually consistent, consistent hashing, automatic scaling

**Case Study**: [Amazon's Dynamo Database](../case-studies/index.md#amazon-dynamo)

## E

### Eventually Consistent
**Definition**: Consistency model where the system will become consistent given no new updates, but may be temporarily inconsistent.

**Benefits**: High availability, partition tolerance, performance

**Trade-offs**: Complexity in handling temporary inconsistencies

**Examples**: DNS, shopping carts, social media feeds

### Event Sourcing
**Definition**: Pattern storing changes to application state as a sequence of events rather than storing current state.

**Benefits**: Complete audit trail, temporal queries, replay capability

**Challenges**: Event schema evolution, snapshot management

**Implementation**: [Event Sourcing Pattern](../patterns/event-sourcing.md)

## F

### Failure Detector
**Definition**: Component that monitors system health and determines when nodes or services have failed.

**Types**: Perfect (impossible), Eventually Perfect, Strong, Weak

**Implementation**: Heartbeats, timeouts, gossip protocols

### Fallacies of Distributed Computing
**Definition**: Eight common but false assumptions developers make about distributed systems that lead to poor designs.

**List**: Network is reliable, latency is zero, bandwidth is infinite, network is secure, topology doesn't change, one administrator, transport cost is zero, network is homogeneous

**Reference**: [8 Fallacies Section](../introduction/index.md#fallacies)

## G

### Gossip Protocol
**Definition**: Communication protocol where nodes periodically exchange state information with random peers, ensuring eventual propagation.

**Benefits**: Scalable, fault-tolerant, self-healing

**Use Cases**: Failure detection, membership management, data replication

## H

### Hinted Handoff
**Definition**: Technique where a node temporarily stores data intended for a failed node, delivering it when the node recovers.

**Benefits**: Improved availability, eventual consistency

**Use Cases**: Distributed databases, cache systems

### Happens-Before Relation
**Definition**: Partial ordering of events in a distributed system that captures potential causality relationships.

**Notation**: a → b (event a happens before event b)

**Implementation**: Logical clocks, vector clocks

## I

### Idempotency
**Definition**: Property where applying an operation multiple times has the same effect as applying it once.

**Importance**: Critical for retry mechanisms and at-least-once delivery

**Implementation**: [Idempotent Receiver Pattern](../patterns/idempotent-receiver.md)

### Isolation Levels
**Definition**: Degrees of consistency guarantees in concurrent systems.

**ACID Levels**: Read Uncommitted, Read Committed, Repeatable Read, Serializable

**Distributed**: Eventual, Causal, Strong

## J

### Jitter
**Definition**: Random variation in timing, often added intentionally to prevent synchronized behavior that could cause system overload.

**Use Cases**: Retry backoff, heartbeat intervals, cache refresh

**Benefits**: Prevents thundering herd, spreads load

## L

### Leader Election
**Definition**: Process of choosing a single coordinator node from a group of candidates to avoid split-brain scenarios.

**Algorithms**: Bully algorithm, Ring algorithm, Raft election

**Implementation**: [Leader Election Pattern](../patterns/leader-election.md)

### Little's Law
**Definition**: Fundamental queueing theory formula: L = λW (average queue length = arrival rate × average wait time).

**Applications**: Capacity planning, performance analysis

**Related**: [Quantitative Toolkit](../quantitative/littles-law.md)

### Logical Clock
**Definition**: Mechanism for ordering events in distributed systems without relying on physical time synchronization.

**Types**: Lamport timestamps, vector clocks

**Purpose**: Establish causality, maintain event ordering

## M

### Microservices
**Definition**: Architectural pattern decomposing applications into small, independently deployable services.

**Benefits**: Independent scaling, technology diversity, fault isolation

**Challenges**: Network complexity, distributed debugging, data consistency

### MTBF (Mean Time Between Failures)
**Definition**: Average time elapsed between failures in a system.

**Calculation**: Total operational time / number of failures

**Related**: Availability calculations, reliability engineering

### MTTR (Mean Time To Repair)
**Definition**: Average time required to repair a failed component and restore service.

**Components**: Detection time + diagnosis time + fix time + recovery time

**Related**: Availability calculations, incident response

## O

### Outbox Pattern
**Definition**: Pattern ensuring reliable message publishing by storing outgoing messages in the same database transaction as business data.

**Benefits**: Transactional guarantees, reliable delivery

**Implementation**: [Outbox Pattern](../patterns/outbox.md)

## P

### Partition Tolerance
**Definition**: System's ability to continue operating despite network partitions that prevent communication between nodes.

**CAP Theorem**: Must choose between consistency and availability when partitions occur

**Strategies**: Quorum consensus, graceful degradation

### Pillar
**Definition**: One of five foundational concepts that support distributed systems architecture: Work, State, Truth, Control, Intelligence.

**Purpose**: Framework for systematic system design

**Reference**: [Part II: Pillars](../part2-pillars/index.md)

## Q

### Quorum
**Definition**: Minimum number of nodes that must participate in an operation for it to be considered valid.

**Formula**: Typically (N/2) + 1 for N total nodes

**Use Cases**: Consensus, read/write consistency

**Example**: 3 of 5 nodes must agree for operation to succeed

## R

### Raft Consensus
**Definition**: Consensus algorithm designed to be more understandable than Paxos while providing the same guarantees.

**Components**: Leader election, log replication, safety

**Benefits**: Strong consistency, partition tolerance

**Implementation**: [Raft consensus in Leader Election pattern](../patterns/leader-election.md)

### Read Repair
**Definition**: Process of fixing inconsistencies detected during read operations by updating stale replicas.

**Types**: Synchronous (blocking), asynchronous (background)

**Benefits**: Self-healing, eventual consistency

### Replica
**Definition**: Copy of data maintained on multiple nodes for availability and fault tolerance.

**Types**: Master-slave, master-master, leaderless

**Consistency**: Strong, eventual, causal

## S

### Saga Pattern
**Definition**: Pattern for managing distributed transactions through a sequence of local transactions with compensating actions.

**Types**: Choreography (event-driven), Orchestration (centralized coordinator)

**Benefits**: Avoid distributed locks, better availability

**Implementation**: [Saga Pattern](../patterns/saga.md)

### Sharding
**Definition**: Horizontal partitioning technique that distributes data across multiple databases or servers.

**Strategies**: Range-based, hash-based, directory-based

**Challenges**: Rebalancing, cross-shard queries, hot spots

### Split-Brain
**Definition**: Situation where a distributed system splits into multiple independent parts, each believing it's the only operational component.

**Causes**: Network partitions, timing failures

**Prevention**: Quorum requirements, external coordination

## T

### Two-Phase Commit (2PC)
**Definition**: Distributed transaction protocol ensuring all participants either commit or abort a transaction.

**Phases**: Prepare (vote), Commit/Abort (decision)

**Problems**: Blocking, coordinator failure, performance

**Alternatives**: Saga pattern, eventual consistency

## V

### Vector Clock
**Definition**: Logical clock mechanism that captures causality relationships between events in distributed systems.

**Format**: Array of counters, one per node

**Benefits**: Detects concurrent events, maintains causality

**Implementation**: [Vector Clock implementation in Concurrency axiom](../part1-axioms/axiom4-concurrency/index.md)

## W

### Write-Ahead Log (WAL)
**Definition**: Logging technique where changes are written to a log before being applied to the database.

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

*This glossary is continuously updated as new concepts are added to the Compendium. Last updated with navigation enhancements and comprehensive pattern definitions.*
