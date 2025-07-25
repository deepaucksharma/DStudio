---
title: Leader-Follower Pattern
description: Coordination pattern for managing distributed state with a single source of truth
type: pattern
category: coordination
difficulty: intermediate
reading_time: 25 min
prerequisites: [consensus, distributed-state]
when_to_use: When you need strong consistency and coordinated updates
when_not_to_use: When eventual consistency is acceptable or single leader becomes bottleneck
status: complete
last_updated: 2025-01-23
---


# Leader-Follower Pattern

<div class="pattern-header">
  <div class="pattern-type">Coordination Pattern</div>
  <div class="pattern-summary">Designate one node as leader to coordinate all writes, ensuring consistency while followers serve reads for scalability.</div>
</div>

## Problem Context

<div class="problem-box">
<h3>🎯 The Challenge</h3>

In distributed systems, when multiple nodes can accept writes:
- **Conflicts arise** from concurrent updates
- **Ordering is ambiguous** without coordination
- **Split-brain scenarios** cause data divergence
- **Consistency is hard** to maintain

The leader-follower pattern solves this by establishing a single source of truth.
</div>

## Solution Architecture

```mermaid
graph TB
    subgraph "Write Path"
        Client1[Client 1] -->|Write| Leader[Leader Node]
        Client2[Client 2] -->|Write| Leader
        Client3[Client 3] -->|Write| Leader
    end
    
    subgraph "Replication"
        Leader -->|Replicate| F1[Follower 1]
        Leader -->|Replicate| F2[Follower 2]
        Leader -->|Replicate| F3[Follower 3]
    end
    
    subgraph "Read Path"
        Client4[Client 4] -->|Read| F1
        Client5[Client 5] -->|Read| F2
        Client6[Client 6] -->|Read| F3
    end
    
    classDef leader fill:#5448C8,stroke:#333,stroke-width:3px,color:#fff
    classDef follower fill:#00BCD4,stroke:#333,stroke-width:2px,color:#fff
    classDef client fill:#FFF3E0,stroke:#333,stroke-width:2px
    
    class Leader leader
    class F1,F2,F3 follower
    class Client1,Client2,Client3,Client4,Client5,Client6 client
```

## How It Works

### 1. Leader Election Process

```mermaid
stateDiagram-v2
    [*] --> Follower: Start
    Follower --> Candidate: Election timeout
    Candidate --> Leader: Receive majority votes
    Candidate --> Follower: Lose election
    Leader --> Follower: Discover higher term
    Follower --> Follower: Receive heartbeat
    Leader --> Leader: Send heartbeats
    
    note right of Candidate
        Request votes from
        other nodes
    end note
    
    note right of Leader
        Periodically send
        heartbeats to maintain
        leadership
    end note
```

### 2. Write Operation Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant L as Leader
    participant F1 as Follower 1
    participant F2 as Follower 2
    participant F3 as Follower 3
    
    C->>L: Write Request
    L->>L: Append to log
    
    par Replication
        L->>F1: Replicate entry
        and
        L->>F2: Replicate entry
        and
        L->>F3: Replicate entry
    end
    
    F1-->>L: Ack
    F2-->>L: Ack
    F3-->>L: Ack
    
    Note over L: Majority achieved
    L->>L: Commit entry
    L-->>C: Success
    
    L->>F1: Commit notification
    L->>F2: Commit notification
    L->>F3: Commit notification
```

### 3. Read Strategies

<div class="strategy-comparison">
<table>
<thead>
<tr>
<th>Strategy</th>
<th>Consistency</th>
<th>Performance</th>
<th>Use Case</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Read from Leader</strong></td>
<td>Strong</td>
<td>Lower (bottleneck)</td>
<td>Financial data</td>
</tr>
<tr>
<td><strong>Read from Followers</strong></td>
<td>Eventual</td>
<td>Higher (distributed)</td>
<td>Product catalog</td>
</tr>
<tr>
<td><strong>Read Your Writes</strong></td>
<td>Session</td>
<td>Medium</td>
<td>User profiles</td>
</tr>
<tr>
<td><strong>Quorum Reads</strong></td>
<td>Strong</td>
<td>Medium</td>
<td>Critical queries</td>
</tr>
</tbody>
</table>
</div>

## Implementation Patterns

### Pattern 1: Synchronous Replication

```python
class SynchronousLeader:
    def write(self, key, value):
        # Write to leader's log
        self.log.append((key, value))
        
        # Replicate to all followers
        acks = 0
        for follower in self.followers:
            if follower.replicate(key, value):
                acks += 1
        
        # Wait for majority
        if acks >= len(self.followers) // 2:
            self.commit(key, value)
            return True
        else:
            self.rollback(key)
            return False
```

### Pattern 2: Asynchronous Replication

```python
class AsynchronousLeader:
    def write(self, key, value):
        # Write locally first
        self.commit(key, value)
        
        # Replicate in background
        for follower in self.followers:
            self.replication_queue.put({
                'follower': follower,
                'operation': (key, value)
            })
        
        return True  # Immediate success
```

### Pattern 3: Chain Replication

```mermaid
graph LR
    Client -->|Write| Head[Head<br/>Leader]
    Head -->|Replicate| M1[Middle 1]
    M1 -->|Replicate| M2[Middle 2]
    M2 -->|Replicate| Tail[Tail]
    Tail -->|Ack| Client
    
    Client2[Read Client] -->|Read| Tail
    
    style Head fill:#5448C8,color:#fff
    style Tail fill:#4CAF50,color:#fff
```

## Failure Handling

### Leader Failure Detection

```mermaid
graph TB
    subgraph "Heartbeat Mechanism"
        Leader[Leader] -->|Heartbeat| F1[Follower 1]
        Leader -->|Heartbeat| F2[Follower 2]
        Leader -->|Timeout!| F3[Follower 3]
        
        F3 -->|Start Election| Election[New Leader Election]
    end
    
    style F3 fill:#ff6b6b
    style Election fill:#ffd700
```

### Split Brain Prevention

<div class="decision-box">
<h4>🧠 Preventing Split Brain</h4>

**Problem**: Network partition creates two leaders

**Solutions**:
1. **Quorum-based decisions**: Require majority for any operation
2. **Fencing tokens**: Monotonically increasing leader epochs
3. **External arbitrator**: ZooKeeper or etcd for coordination
4. **Lease-based leadership**: Time-bound leader terms

```mermaid
graph TB
    subgraph "Partition A"
        L1[Old Leader<br/>3 nodes]
    end
    
    subgraph "Partition B"
        L2[New Leader<br/>2 nodes]
    end
    
    L1 -->|Has Majority| Active[Remains Active]
    L2 -->|No Majority| Inactive[Steps Down]
    
    style L1 fill:#4CAF50,color:#fff
    style L2 fill:#ff6b6b,color:#fff
```
</div>

## Performance Considerations

### Scalability Limits

```mermaid
graph LR
    subgraph "Bottlenecks"
        WB[Write Bottleneck<br/>Single Leader]
        RB[Replication Lag<br/>Network Delay]
        FB[Failover Time<br/>Detection + Election]
    end
    
    subgraph "Mitigations"
        Shard[Sharding<br/>Multiple Leaders]
        Async[Async Replication<br/>Trade Consistency]
        Fast[Fast Elections<br/>Pre-voting]
    end
    
    WB --> Shard
    RB --> Async
    FB --> Fast
```

### Optimization Strategies

1. **Batching**: Group multiple writes for efficient replication
2. **Pipelining**: Send next batch before previous acknowledges
3. **Compression**: Reduce replication bandwidth
4. **Read replicas**: Scale read capacity horizontally

## Real-World Examples

### 1. Database Systems

<div class="example-card">
<h4>MySQL/PostgreSQL Replication</h4>

```mermaid
graph TB
    Master[(Master DB)] -->|Binary Log| Slave1[(Slave 1)]
    Master -->|Binary Log| Slave2[(Slave 2)]
    
    App[Application] -->|Writes| Master
    App -->|Reads| LB[Load Balancer]
    LB --> Slave1
    LB --> Slave2
```

- Single master for writes
- Multiple slaves for read scaling
- Binary log for replication
- Configurable consistency levels
</div>

### 2. Consensus Systems

<div class="example-card">
<h4>Raft Consensus</h4>

- Leaders elected by majority vote
- All changes go through leader
- Log replication ensures consistency
- Automatic failover on leader failure
</div>

### 3. Distributed Coordination

<div class="example-card">
<h4>Apache Kafka</h4>

- Partition leaders handle all writes
- In-sync replicas (ISR) for durability
- Controller manages leader election
- Consumers can read from followers
</div>

## Trade-offs Analysis

<div class="trade-off-matrix">
<table>
<thead>
<tr>
<th>Aspect</th>
<th>Advantages</th>
<th>Disadvantages</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Consistency</strong></td>
<td>Strong consistency for writes<br/>Clear ordering guarantees</td>
<td>Read consistency depends on strategy<br/>Replication lag issues</td>
</tr>
<tr>
<td><strong>Availability</strong></td>
<td>Read availability scales<br/>Automatic failover possible</td>
<td>Write availability limited to leader<br/>Failover causes downtime</td>
</tr>
<tr>
<td><strong>Performance</strong></td>
<td>Read scaling with followers<br/>Simple conflict resolution</td>
<td>Write bottleneck at leader<br/>Replication overhead</td>
</tr>
<tr>
<td><strong>Complexity</strong></td>
<td>Conceptually simple<br/>Clear responsibility</td>
<td>Leader election complexity<br/>Split-brain handling</td>
</tr>
</tbody>
</table>
</div>

## When to Use

✅ **Good Fit**:
- Need strong consistency
- Read-heavy workloads
- Clear write patterns
- Can tolerate brief unavailability

❌ **Poor Fit**:
- Write-heavy workloads
- Need 100% write availability
- Geographically distributed writes
- Cannot tolerate replication lag

## Implementation Checklist

- [ ] Leader election mechanism
- [ ] Heartbeat/failure detection
- [ ] Replication protocol
- [ ] Consistency guarantees
- [ ] Split-brain prevention
- [ ] Monitoring and alerting
- [ ] Failover procedures
- [ ] Read routing strategy

## Related Patterns

- [Leader Election](leader-election.md) - Choosing the leader
- [Consensus](consensus.md) - Agreement protocols
- [Primary-Backup](primary-backup.md) - Similar but simpler
- [Multi-Master](multi-master.md) - Alternative approach
- [Chain Replication](chain-replication.md) - Variation

## Law Connections

- **[Law 1: Correlated Failure](/part1-axioms/law1-failure/)**: Leader failure affects all writes
- **[Law 4: Trade-offs](/part1-axioms/law4-tradeoffs/)**: Consistency vs availability balance
- **[Law 5: Distributed Knowledge](/part1-axioms/law5-epistemology/)**: Split-brain from partial knowledge