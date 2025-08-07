---
title: Consensus Patterns
description: Achieve agreement in distributed systems
---

## The Complete Blueprint

Consensus patterns enable distributed systems to achieve agreement on shared state even in the presence of network partitions, node failures, and message delays, forming the foundation for strongly consistent distributed databases, configuration management systems, and leader election protocols. These algorithms solve one of the most fundamental problems in distributed computing: how multiple nodes can agree on a single value or sequence of operations while tolerating failures and maintaining system availability. At the heart of consensus lies the challenge of the CAP theorem - balancing consistency, availability, and partition tolerance - with algorithms like Raft, Paxos, and PBFT providing different trade-offs and guarantees. The consensus process typically involves a leader or proposer node coordinating with a majority quorum of followers or acceptors to ensure that once a value is chosen, it remains stable and consistent across all nodes. Modern implementations power critical infrastructure including etcd for Kubernetes configuration, Apache Kafka's controller election, CockroachDB's transaction coordination, and blockchain networks where consensus ensures the immutable ordering of transactions across a decentralized network of untrusted nodes.

```mermaid
graph TB
    subgraph "Consensus Pattern Complete System"
        subgraph "Node Roles"
            Leader["Leader Node<br/>Coordinates Proposals<br/>Handles Client Requests"]
            Follower1["Follower 1<br/>Accepts/Rejects<br/>Replicates State"]
            Follower2["Follower 2<br/>Accepts/Rejects<br/>Replicates State"]
            Follower3["Follower 3<br/>Accepts/Rejects<br/>Replicates State"]
            Follower4["Follower 4<br/>Accepts/Rejects<br/>Replicates State"]
        end
        
        subgraph "Consensus Phases"
            Phase1["Phase 1: Prepare<br/>Request Promise<br/>Find Latest Value"]
            Phase2["Phase 2: Accept<br/>Propose Value<br/>Get Majority Commit"]
            Phase3["Phase 3: Commit<br/>Apply to State<br/>Notify Clients"]
        end
        
        Client[Client Request] --> Leader
        Leader --> Phase1
        Phase1 --> Follower1
        Phase1 --> Follower2
        Phase1 --> Follower3
        
        Follower1 --> Phase2
        Follower2 --> Phase2
        Follower3 --> Phase2
        
        Phase2 --> Phase3
        Phase3 --> StateLog[Replicated Log<br/>Consistent State]
        
        FailureDetector[Failure Detector] -.-> Leader
        FailureDetector -.-> Follower4
        Election[Leader Election] -.-> Leader
        
        style Leader fill:#51cf66
        style Follower1 fill:#74c0fc
        style Follower2 fill:#74c0fc
        style Follower3 fill:#74c0fc
        style Follower4 fill:#ffd43b
        style StateLog fill:#ff8cc8
    end
```

### What You'll Master

!!! success "By understanding Consensus patterns, you'll be able to:"
    - **Achieve strong consistency** - Ensure all nodes agree on the same state and ordering
    - **Handle network partitions** - Maintain correctness even when nodes can't communicate
    - **Implement leader election** - Coordinate distributed systems with elected coordinators
    - **Build distributed databases** - Create systems with ACID guarantees across multiple nodes
    - **Manage configuration systems** - Ensure consistent configuration across distributed services
    - **Design fault-tolerant systems** - Build systems that continue operating despite node failures

# Consensus Patterns

Consensus algorithms like Raft and Paxos

## See Also

- [Eventual Consistency](/pattern-library/data-management/eventual-consistency)
- [Event Streaming](/pattern-library/architecture/event-streaming)
- [Rate Limiting Pattern](/pattern-library/scaling/rate-limiting)
