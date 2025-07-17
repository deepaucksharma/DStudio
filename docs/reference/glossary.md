# Distributed Systems Glossary

!!! info "Comprehensive Glossary"
    Key terms, acronyms, and concepts used throughout distributed systems literature and practice.

!!! tip "Quick Navigation"
    [← Reference Home](index.md) |
    [A-F](#a-f) | [G-L](#g-l) | [M-R](#m-r) | [S-Z](#s-z) |
    [Cheat Sheets →](cheat-sheets.md)

## A-F

### A

**ACID**
: Atomicity, Consistency, Isolation, Durability - properties of traditional database transactions

**Anti-Entropy**
: Process of comparing and synchronizing replicas to ensure eventual consistency

**Anycast**
: Network addressing method where data is routed to the topologically nearest node in a group

**Availability**
: The proportion of time a system is operational and accessible (A in CAP theorem)

**Availability Zone (AZ)**
: Isolated location within a cloud region with independent power, cooling, and networking

### B

**Backpressure**
: Flow control mechanism where downstream services signal upstream to slow down

**BASE**
: Basically Available, Soft state, Eventually consistent - alternative to ACID for distributed systems

**Byzantine Failure**
: A node behaving arbitrarily or maliciously, sending different information to different nodes. Named after Byzantine Generals Problem where generals must coordinate attack but some may be traitors. Requires 3f+1 nodes to tolerate f Byzantine nodes

**Byzantine Fault Tolerance (BFT)**
: Ability to function correctly even when some nodes exhibit Byzantine failures

### C

**CAP Theorem**
: States that distributed systems can guarantee at most two of: Consistency, Availability, Partition tolerance

**Cache**
: Temporary storage of frequently accessed data to reduce latency and load

**Causality**
: The relationship between events where one event is the consequence of another

**Circuit Breaker**
: Pattern that prevents cascading failures by stopping calls to failing services

**Clock Skew**
: Difference in time between different nodes' clocks in a distributed system

**Consensus**
: Agreement among distributed nodes on a single data value or state

**Consistency**
: All nodes see the same data at the same time (C in CAP theorem)

**Consistent Hashing**
: Distributed hashing scheme that minimizes remapping when nodes are added/removed

**CRDT**
: Conflict-free Replicated Data Type - data structures that can be replicated and merged without coordination. Examples include G-Counter (grow-only counter), PN-Counter (increment/decrement), OR-Set (observed-remove set). Enables eventual consistency without conflicts

### D

**Data Locality**
: Principle of processing data near where it's stored to minimize movement

**Deadlock**
: State where processes are blocked, each waiting for resources held by others

**Distributed Transaction**
: Transaction spanning multiple nodes requiring coordination for ACID properties

**DNS**
: Domain Name System - hierarchical distributed naming system for resources

### E

**Epoch**
: A period of time used for versioning in distributed systems

**Eventual Consistency**
: Guarantee that all nodes will converge to the same state given enough time

**Exponential Backoff**
: Retry strategy where wait time increases exponentially between attempts

### F

**Failover**
: Process of switching to a redundant system when the primary fails

**Failure Detector**
: Component that identifies when nodes have failed in a distributed system

**Fan-out**
: Pattern where one request triggers multiple downstream requests

**Fault Tolerance**
: Ability to continue operating properly despite failures

**Federation**
: Splitting databases by function to scale beyond single database limits

**Five Nines (99.999%)**
: Availability target allowing only 5.26 minutes downtime per year

## G-L

### G

**Gossip Protocol**
: Peer-to-peer communication protocol for spreading information in distributed systems

**Graceful Degradation**
: Maintaining partial functionality when some components fail

### H

**Health Check**
: Regular verification that a service is operational and responsive

**Heartbeat**
: Periodic signal sent between nodes to indicate they're alive

**Horizontal Scaling**
: Adding more machines to handle increased load (scale-out)

**Hot Spot**
: Concentration of load on a particular node or partition

### I

**Idempotency**
: Property where operation can be applied multiple times without changing result

**Isolation Level**
: Degree to which concurrent transactions are isolated from each other

### J

**Jitter**
: Variability in latency over time; also random delay added to prevent thundering herd

### K

**Kubernetes (K8s)**
: Container orchestration platform for automating deployment and scaling

### L

**Lamport Clock**
: Logical clock for ordering events in distributed systems

**Latency**
: Time delay between request and response

**Leader Election**
: Process of choosing one node to coordinate activities

**Linearizability**
: Strongest consistency model where operations appear instantaneous

**Little's Law**
: L = λW (items in system = arrival rate × time in system). Fundamental queueing theory result that applies to all stable systems regardless of arrival/service distributions. Example: 100 req/s arriving, 200ms avg response time = 20 requests in system on average

**Load Balancer**
: Distributes incoming requests across multiple servers

**Log-Structured Storage**
: Append-only storage pattern for high write throughput

## M-R

### M

**MapReduce**
: Programming model for processing large data sets in parallel

**Memcached**
: Distributed memory caching system

**Message Queue**
: Asynchronous communication buffer between services

**Microservices**
: Architectural style structuring applications as loosely coupled services

**MTBF**
: Mean Time Between Failures - average time between system failures

**MTTR**
: Mean Time To Repair - average time to restore service after failure

**M/M/1 Queue**
: Queueing model with Markovian (exponential) arrivals, Markovian service times, and 1 server. At utilization ρ, average wait time = ρ/(1-ρ) × service time. Shows why systems cliff at high utilization

**Multi-Master**
: Replication topology where multiple nodes can accept writes

**Mutex**
: Mutual exclusion lock preventing concurrent access to shared resources

**MVCC (Multi-Version Concurrency Control)**
: Technique where database maintains multiple versions of data to allow readers to see consistent snapshots without blocking writers. Used in PostgreSQL, Oracle

### N

**Network Partition**
: Network failure causing nodes to be unable to communicate

**Node**
: Individual machine or process in a distributed system

### O

**Observability**
: Ability to understand system state from external outputs

**Optimistic Concurrency Control**
: Assumes conflicts are rare, validates at commit time

**Orchestration**
: Automated configuration, coordination, and management of systems

### P

**PACELC**
: Extension of CAP theorem adding latency/consistency tradeoff

**Paxos**
: Consensus protocol for reaching agreement in distributed systems. Guarantees safety (no two nodes decide differently) but not liveness (may not terminate). Complex to understand but mathematically proven. Used in systems like Google's Chubby

**Pessimistic Concurrency Control**
: Locks resources before use to prevent conflicts

**PBFT (Practical Byzantine Fault Tolerance)**
: Consensus algorithm tolerating Byzantine failures. Requires 3f+1 nodes to tolerate f Byzantine nodes. More complex than crash-fault protocols like Raft but handles malicious nodes. Uses three phases: pre-prepare, prepare, commit

**Pub/Sub**
: Publish-Subscribe messaging pattern

### Q

**Quorum**
: Minimum number of nodes that must agree for operation to proceed

**Queue**
: FIFO data structure for managing work items

### R

**Race Condition**
: Bug occurring when timing of events affects program correctness

**Raft**
: Consensus algorithm designed to be understandable alternative to Paxos. Uses leader election, log replication, and safety mechanisms. Breaks consensus into three subproblems: leader election, log replication, and safety. Used in etcd, Consul

**Read Replica**
: Database copy that handles read queries to reduce load

**Replication**
: Copying data to multiple nodes for fault tolerance

**Request-Response**
: Synchronous communication pattern

**Resilience**
: Ability to recover from failures and continue operating

**RPC**
: Remote Procedure Call - calling functions on remote systems

## S-Z

### S

**Saga**
: Long-lived transaction pattern using compensating transactions

**Scalability**
: Ability to handle increased load by adding resources

**Serializability**
: Guarantee that concurrent transaction execution equals some serial order

**Service Discovery**
: Mechanism for services to find and communicate with each other

**Service Mesh**
: Infrastructure layer for service-to-service communication

**Shard**
: Horizontal partition of data in a database

**SLA**
: Service Level Agreement - contract defining expected service performance

**SLI**
: Service Level Indicator - metric measuring service performance

**SLO**
: Service Level Objective - target value for an SLI

**Split Brain**
: Condition where cluster partitions into subgroups thinking others failed

**Stateful**
: Service that maintains client session state between requests

**Stateless**
: Service that doesn't maintain client state between requests

**Strong Consistency**
: All nodes see the same data value at the same time

### T

**Throttling**
: Limiting request rate to prevent overload

**Throughput**
: Rate of successful message delivery or processing

**Timeout**
: Maximum time to wait for operation completion

**TLS**
: Transport Layer Security - cryptographic protocol for secure communication

**Tombstone**
: Marker indicating deleted data in eventually consistent systems

**Two-Phase Commit (2PC)**
: Protocol ensuring all nodes commit or abort distributed transaction. Works in two phases: 1) Voting phase where coordinator asks all participants if they can commit, 2) Commit phase where coordinator tells all to commit or abort based on votes. Main drawback: blocks if coordinator fails

### U

**UUID**
: Universally Unique Identifier - 128-bit identifier

### V

**Vector Clock**
: Data structure for capturing causality between events

**Vertical Scaling**
: Adding more power (CPU, RAM) to existing machines (scale-up)

### W

**WAL**
: Write-Ahead Logging - durability technique writing changes before applying

**Weak Consistency**
: No guarantees about when all nodes will see the same data

**Write Amplification**
: Ratio of physical writes to logical writes

### Z

**Zookeeper**
: Centralized service for configuration, naming, and synchronization

**Zero-Copy**
: Data transfer without copying between memory areas

**Zipkin**
: Distributed tracing system

---

## Acronym Quick Reference

| Acronym | Full Form |
|---------|-----------|
| ACID | Atomicity, Consistency, Isolation, Durability |
| API | Application Programming Interface |
| BASE | Basically Available, Soft state, Eventually consistent |
| BFT | Byzantine Fault Tolerance |
| CAP | Consistency, Availability, Partition tolerance |
| CDN | Content Delivery Network |
| CQRS | Command Query Responsibility Segregation |
| CRDT | Conflict-free Replicated Data Type |
| DDoS | Distributed Denial of Service |
| FIFO | First In, First Out |
| GRPC | Google Remote Procedure Call |
| HTTP | HyperText Transfer Protocol |
| LIFO | Last In, First Out |
| MTBF | Mean Time Between Failures |
| MTTR | Mean Time To Repair |
| P2P | Peer-to-Peer |
| QPS | Queries Per Second |
| REST | Representational State Transfer |
| RPC | Remote Procedure Call |
| RTT | Round-Trip Time |
| SLA | Service Level Agreement |
| TCP | Transmission Control Protocol |
| TPS | Transactions Per Second |
| UDP | User Datagram Protocol |
| WAL | Write-Ahead Log |

## Related Resources

- [Cheat Sheets](cheat-sheets.md) - Quick reference cards
- [Formulas](formulas.md) - Mathematical formulas
- [Patterns Reference](patterns-reference.md) - Common patterns