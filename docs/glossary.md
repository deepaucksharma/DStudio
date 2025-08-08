# Distributed Systems Glossary

## Overview
This glossary provides concise definitions for technical terms used throughout the Distributed Systems Framework documentation. Terms are organized alphabetically within categories for easy reference.

## Canonical Law Names

### Fundamental Laws
- **Law of Asynchronous Reality**: The fundamental constraint that distributed systems cannot guarantee simultaneous state changes across nodes due to network delays and processing variations.
- **Law of Cognitive Load**: Human operators can only effectively manage 7±2 concepts simultaneously, with exponential performance degradation under stress.
- **Law of Correlated Failure**: Failures in distributed systems exhibit correlation coefficients (ρ) between 0.3-0.7, creating cascading effects when shared dependencies fail.
- **Law of Distributed Knowledge**: Information cannot propagate faster than network latency permits, making global consensus fundamentally impossible in finite time.
- **Law of Economic Reality**: System design decisions are ultimately constrained by total cost of ownership (TCO), requiring trade-offs between technical optimality and economic viability.
- **Law of Emergent Behavior**: Complex systems exhibit behaviors that cannot be predicted from individual component analysis, requiring holistic system thinking.
- **Law of Persistent Uncertainty**: Complete system state knowledge is impossible in distributed systems, requiring designs that embrace partial information.

## Technical Terms

### A-C

**Amdahl's Law**: Formula defining the theoretical speedup limit of parallel processing: Speedup = 1 / (S + P/N), where S is sequential fraction, P is parallel fraction, N is processors.

**Backpressure**: Flow control mechanism where downstream components signal upstream to slow down when overwhelmed, preventing resource exhaustion.

**Byzantine Fault**: Failure mode where components may act arbitrarily or maliciously, sending different information to different parts of the system.

**CAP Theorem**: Consistency, Availability, Partition tolerance - pick two. Fundamental trade-off in distributed systems design proven by Brewer/Gilbert/Lynch.

**Cascading Failure**: Progressive system degradation where failure of one component triggers failures in dependent components, potentially causing total system collapse.

**Causality**: Relationship between events where one event influences another, tracked in distributed systems using vector clocks or similar mechanisms.

**Circuit Breaker**: Pattern that prevents cascading failures by monitoring error rates and temporarily blocking requests to failing services.

**Clock Drift**: Gradual divergence of system clocks from true time, typically 10-100 ppm in commodity hardware, requiring synchronization protocols.

**Consensus**: Agreement among distributed processes on a single value, fundamental to coordination but impossible to guarantee in asynchronous networks (FLP theorem).

**Consistent Hashing**: Distributed hashing scheme minimizing key remapping when nodes join/leave, essential for scalable distributed caches and databases.

**Convergent Replicated Data Types (CRDTs)**: Data structures that automatically resolve conflicts in distributed systems without coordination.

### D-H

**Distributed Transaction**: Operation spanning multiple nodes requiring ACID properties across network boundaries, typically using 2PC or saga patterns.

**Eventual Consistency**: Consistency model guaranteeing all nodes will converge to the same state given no new updates, trading immediate consistency for availability.

**Failure Domain**: Set of resources sharing a common failure mode, used to design blast radius containment and fault isolation boundaries.

**Fanout**: Number of downstream services called by a single request, critical factor in latency amplification and failure propagation.

**FLP Impossibility**: Fischer-Lynch-Paterson theorem proving consensus is impossible in asynchronous systems with even one faulty process.

**Gossip Protocol**: Epidemic communication pattern where nodes randomly exchange information, providing eventual consistency with probabilistic guarantees.

**Gray Failure**: Subtle performance degradation not detected by binary health checks, often causing more damage than complete failures.

**Happens-Before Relation**: Partial ordering of events in distributed systems, fundamental to understanding causality and consistency.

**Head-of-Line Blocking**: Performance degradation when a slow request blocks subsequent faster requests in a queue.

**Heartbeat**: Periodic signal indicating liveness, used for failure detection with typical intervals of 1-10 seconds in production systems.

**Hot Partition**: Data partition receiving disproportionate traffic, causing performance bottlenecks and potential cascading failures.

### I-M

**Idempotency**: Property where multiple identical requests produce the same result, essential for safe retries in distributed systems.

**Intelligence Distribution**: Architectural patterns for distributing decision-making logic across system boundaries to optimize for latency, bandwidth, and autonomy.

**Jitter**: Random delay added to prevent synchronized behavior (thundering herd), typically 0-25% of base interval.

**Lamport Clock**: Logical clock providing partial ordering of events in distributed systems using monotonic counters.

**Linearizability**: Strongest consistency model where operations appear instantaneous and atomic at some point between invocation and response.

**Little's Law**: L = λW, relating system size (L), arrival rate (λ), and wait time (W), fundamental to capacity planning.

**Load Shedding**: Deliberate rejection of requests to maintain system stability under overload, prioritizing critical traffic.

**Logical Clock**: Abstract time mechanism for ordering events without synchronized physical clocks, includes Lamport and vector clocks.

**Membership Protocol**: Mechanism for tracking active nodes in a cluster, handling joins, leaves, and failures with eventual convergence.

**Metastable Failure**: System state where minor disruptions cause severe performance degradation, often triggered at 70-80% utilization.

### N-Q

**Network Partition**: Communication failure splitting a distributed system into isolated segments, inevitable in distributed systems (CAP theorem).

**Observability**: System property enabling understanding of internal state from external outputs, beyond traditional monitoring.

**Optimistic Concurrency Control**: Allowing concurrent operations assuming no conflicts, rolling back on actual conflicts.

**Partial Failure**: Distributed system state where some components fail while others continue, creating inconsistent global state.

**Percolation Threshold**: Critical point (~59.3% in 2D lattices) where local failures create system-wide connectivity loss.

**Pessimistic Concurrency Control**: Preventing conflicts through locking, trading performance for consistency guarantees.

**Phi Accrual Failure Detector**: Adaptive failure detection outputting suspicion levels rather than binary alive/dead decisions.

**Poison Pill**: Deliberately malformed message causing receiver failure, used for controlled shutdown or testing.

**Quorum**: Minimum number of nodes required for valid operations, typically majority (N/2 + 1) for strong consistency.

### R-T

**Race Condition**: Timing-dependent bug where operation correctness depends on event ordering, common in concurrent systems.

**Raft Consensus**: Understandable consensus algorithm dividing problem into leader election, log replication, and safety.

**Read Repair**: Consistency mechanism fixing inconsistencies during read operations by comparing and updating replicas.

**Replica**: Copy of data or service for availability, performance, or fault tolerance, requiring consistency protocols.

**Retry Storm**: Cascading overload from synchronized retry attempts after failure recovery, mitigated by exponential backoff with jitter.

**Sagas**: Long-running transactions composed of compensatable steps, providing eventual consistency without distributed locks.

**Shard**: Horizontal data partition distributing load across nodes, requiring careful key selection to avoid hotspots.

**Split Brain**: Network partition causing multiple nodes to believe they're the leader, potentially causing data inconsistency.

**State Distribution**: Patterns for managing and synchronizing state across distributed components while maintaining consistency guarantees.

**Stragglers**: Slowest tasks in parallel operations determining overall latency, addressed through speculative execution or hedged requests.

**Thundering Herd**: Synchronized surge of activity overwhelming resources, often after cache expiration or service recovery.

**Timeout**: Maximum wait duration before considering an operation failed, requiring careful tuning to balance responsiveness and false positives.

**Truth Distribution**: Architectural patterns for establishing and maintaining consistent truth across distributed components despite partial failures.

**Two-Phase Commit (2PC)**: Atomic commitment protocol ensuring all-or-nothing semantics across distributed resources, vulnerable to coordinator failure.

### U-Z

**Vector Clock**: Data structure tracking causality between events using per-node logical timestamps, enabling conflict detection.

**Version Vector**: Compact representation of version history for conflict resolution in eventually consistent systems.

**Virtual Nodes**: Technique mapping multiple logical partitions to physical nodes, enabling better load distribution and easier scaling.

**Work Distribution**: Patterns for dividing and coordinating computational tasks across distributed workers while managing failures and stragglers.

**Write Amplification**: Ratio of physical writes to logical writes, critical performance factor in distributed storage systems.

**Zero-Copy**: Data transfer optimization avoiding CPU-mediated copying between memory regions, essential for high-performance systems.

**Zipf's Law**: Power law distribution where frequency ∝ 1/rank, describing access patterns in many real-world systems.

**Zone**: Failure isolation boundary, typically representing a data center hall or availability zone in cloud environments.

## Measurement Units

### Time
- **RTT (Round-Trip Time)**: Network round-trip latency, typically 0.5ms (same DC) to 150ms (intercontinental)
- **Clock Drift Rate**: 10-100 ppm (parts per million) for commodity hardware
- **Heartbeat Interval**: 1-10 seconds in production systems
- **Timeout Values**: 100ms (local), 1s (regional), 10s (global) typical defaults

### Scale
- **Replication Factor**: Number of data copies, typically 3 for durability, 5+ for read-heavy workloads
- **Fanout Degree**: 10-100 for microservices, 1000+ for search systems
- **Shard Count**: 10-10,000 depending on data size and access patterns
- **Cluster Size**: 3-5 (minimum HA), 100-1000 (typical production), 10,000+ (hyperscale)

### Reliability
- **Availability**: Measured in "nines" - 99.9% (three nines) = 8.76 hours downtime/year
- **MTBF (Mean Time Between Failures)**: Average operational time between failures
- **MTTR (Mean Time To Recovery)**: Average time to restore service after failure
- **Failure Rate**: λ = 1/MTBF, used in reliability calculations

## Acronyms

- **ACID**: Atomicity, Consistency, Isolation, Durability
- **BASE**: Basically Available, Soft state, Eventual consistency
- **CQRS**: Command Query Responsibility Segregation
- **CRDT**: Conflict-free/Convergent Replicated Data Type
- **DC**: Data Center
- **FLP**: Fischer-Lynch-Paterson (impossibility theorem)
- **HA**: High Availability
- **HLC**: Hybrid Logical Clock
- **MVCC**: Multi-Version Concurrency Control
- **PACELC**: Extension of CAP adding latency/consistency trade-off
- **RPC**: Remote Procedure Call
- **SLA**: Service Level Agreement
- **SLI**: Service Level Indicator
- **SLO**: Service Level Objective
- **TCO**: Total Cost of Ownership
- **WAL**: Write-Ahead Log

## Pattern Categories

### Resilience Patterns
Patterns focused on system stability and recovery: Circuit Breaker, Retry, Timeout, Bulkhead, Load Shedding

### Consistency Patterns
Patterns managing distributed state: Saga, Event Sourcing, CQRS, Outbox, Two-Phase Commit

### Scalability Patterns
Patterns for system growth: Sharding, Consistent Hashing, Cache-Aside, Read Replicas, CDN

### Coordination Patterns
Patterns for distributed agreement: Leader Election, Distributed Locking, Consensus, Gossip Protocol

### Observability Patterns
Patterns for system understanding: Distributed Tracing, Structured Logging, Metrics Aggregation, Health Checks

## References

This glossary is maintained as part of the Distributed Systems Framework. For detailed explanations and examples, refer to the specific pattern, law, or pillar documentation.

Last Updated: 2024
Version: 1.0