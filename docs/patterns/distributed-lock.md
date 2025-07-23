---
title: Distributed Lock Pattern
description: Pattern for distributed systems coordination and reliability
type: pattern
category: specialized
difficulty: advanced
reading_time: 35 min
prerequisites: []
when_to_use: When dealing with specialized challenges
when_not_to_use: When simpler solutions suffice
status: complete
last_updated: 2025-07-20
---
<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **Distributed Lock Pattern**

# Distributed Lock Pattern

**Mutual exclusion across distributed nodes**

> *"In a distributed system, acquiring a lock is easy—it's the releasing that's hard."*

---

## 🎯 Level 1: Intuition

### The Bathroom Stall Analogy

A distributed lock is like a public bathroom stall:
- **Lock acquisition**: Check if door is locked, if not, lock it
- **Lock holding**: Use the facility while others wait
- **Lock release**: Unlock when done
- **Lock timeout**: Janitor has master key for emergencies

The challenge: What if someone passes out inside? (node failure while holding lock)

### Basic Distributed Lock

```mermaid
flowchart LR
    subgraph "Lock Acquisition Flow"
        Client[Client Request]
        Check{Lock Available?}
        Acquire[Acquire Lock<br/>SET NX EX]
        Success[Return Lock ID]
        Failed[Return None]
        
        Client --> Check
        Check -->|Yes| Acquire
        Check -->|No| Failed
        Acquire --> Success
    end
    
    subgraph "Lock Release Flow"
        Release[Release Request]
        Verify{Own Lock?}
        Delete[Delete Lock Key]
        Released[Lock Released]
        Denied[Release Denied]
        
        Release --> Verify
        Verify -->|Yes| Delete
        Verify -->|No| Denied
        Delete --> Released
    end
    
    style Success fill:#10b981,stroke:#059669
    style Failed fill:#ef4444,stroke:#dc2626
    style Released fill:#10b981,stroke:#059669
    style Denied fill:#ef4444,stroke:#dc2626
```

### Distributed Lock State Machine

```mermaid
stateDiagram-v2
    [*] --> Available: Initial State
    
    Available --> Locked: Client acquires<br/>(SET NX EX)
    
    Locked --> Available: Lock released<br/>(DEL if owner)
    
    Locked --> Available: Lock expires<br/>(TTL timeout)
    
    Locked --> Locked: Renew lease<br/>(EXPIRE)
    
    note right of Locked
        Lock Info:
        • Owner ID
        • Expiry time
        • Resource name
    end note
    
    note left of Available
        Properties:
        • Mutual exclusion
        • Deadlock free
        • Fault tolerant
    end note
```

### Redis Lock Commands

| Operation | Redis Command | Purpose |
|-----------|---------------|----------|  
| **Acquire** | `SET lock:name uuid NX PX 5000` | Atomic set-if-not-exists with expiry |
| **Release** | Lua script | Atomic check-and-delete |
| **Extend** | `EXPIRE lock:name 5` | Extend TTL if still owner |
| **Check** | `GET lock:name` | Check current owner |

---

## 🏗️ Level 2: Foundation

### Distributed Lock Properties

| Property | Description | Why It Matters |
|----------|-------------|----------------|
| **Mutual Exclusion** | Only one holder at a time | Core requirement |
| **Deadlock Free** | Locks eventually expire | Prevents system freeze |
| **Fault Tolerant** | Survives node failures | Distributed reliability |
| **Non-Byzantine** | Assumes non-malicious nodes | Simplifies design |

### Lock Implementation Strategies

#### 1. Database-Based Locks

```mermaid
graph TB
    subgraph "Database Lock Table"
        Table[distributed_locks]
        C1[resource_name<br/>UNIQUE]
        C2[lock_holder]
        C3[acquired_at]
        C4[expires_at]
        
        Table --> C1
        Table --> C2
        Table --> C3
        Table --> C4
    end
    
    subgraph "Lock Operations"
        Insert[INSERT ... ON CONFLICT DO NOTHING]
        Delete[DELETE WHERE holder = me]
        Cleanup[DELETE WHERE expires_at < NOW()]
        
        Insert -->|Success| Acquired
        Insert -->|Conflict| NotAcquired
        Delete --> Released
        Cleanup --> ExpiredLocks
    end
    
    style C1 fill:#fbbf24,stroke:#f59e0b,stroke-width:2px
    style Acquired fill:#10b981,stroke:#059669
    style NotAcquired fill:#ef4444,stroke:#dc2626
```

#### 2. ZooKeeper-Based Locks

```mermaid
graph TB
    subgraph "ZooKeeper Lock Structure"
        Root["/locks"]
        Resource["/locks/resource-1"]
        
        subgraph "Sequential Nodes"
            N1["lock-0000000001<br/>(holder)"]
            N2["lock-0000000002<br/>(waiting)"]
            N3["lock-0000000003<br/>(waiting)"]
        end
        
        Root --> Resource
        Resource --> N1
        Resource --> N2
        Resource --> N3
        
        N1 -.->|watches| N2
        N2 -.->|watches| N3
    end
    
    subgraph "Lock Algorithm"
        Create[Create sequential<br/>ephemeral node]
        Check{Lowest<br/>sequence?}
        Hold[Hold lock]
        Watch[Watch previous node]
        
        Create --> Check
        Check -->|Yes| Hold
        Check -->|No| Watch
        Watch -->|Node deleted| Check
    end
    
    style N1 fill:#10b981,stroke:#059669,stroke-width:3px
    style Hold fill:#10b981,stroke:#059669
```

#### 3. Consensus-Based Locks

```mermaid
sequenceDiagram
    participant Client
    participant Leader
    participant Follower1
    participant Follower2
    participant LockTable
    
    Client->>Leader: Acquire lock "resource-X"
    
    rect rgb(240, 240, 255)
        Note over Leader,Follower2: Consensus Protocol
        Leader->>Leader: Create proposal
        Leader->>Follower1: Replicate: LOCK(resource-X, client-1)
        Leader->>Follower2: Replicate: LOCK(resource-X, client-1)
        
        Follower1-->>Leader: Ack
        Follower2-->>Leader: Ack
        
        Note over Leader: Majority achieved
    end
    
    Leader->>LockTable: Update: resource-X → client-1
    Leader-->>Client: Lock acquired
    
    Note over Client: Perform work...
    
    Client->>Leader: Release lock "resource-X"
    
    rect rgb(240, 255, 240)
        Note over Leader,Follower2: Consensus for release
        Leader->>Follower1: Replicate: UNLOCK(resource-X)
        Leader->>Follower2: Replicate: UNLOCK(resource-X)
        Follower1-->>Leader: Ack
        Follower2-->>Leader: Ack
    end
    
    Leader->>LockTable: Remove: resource-X
    Leader-->>Client: Lock released
```

### Lock Safety Properties

```mermaid
graph TB
    subgraph "Fencing Token Mechanism"
        Client1[Client 1<br/>Token: 42]
        Client2[Client 2<br/>Token: 43]
        Lock[Lock Service]
        Storage[Storage Service]
        
        Client1 -->|1. Acquire lock| Lock
        Lock -->|2. Token: 42| Client1
        
        Client1 -->|3. Write with token 42| Storage
        
        Note1[Network delay/GC pause]
        Note1 -.-> Client1
        
        Client2 -->|4. Acquire lock| Lock
        Lock -->|5. Token: 43| Client2
        
        Client1 -->|6. Write with token 42| Storage
        Storage -->|7. Reject: token 42 < 43| Client1
        
        Client2 -->|8. Write with token 43| Storage
        Storage -->|9. Accept| Client2
    end
    
    style Client1 fill:#fbbf24,stroke:#f59e0b
    style Client2 fill:#10b981,stroke:#059669
    style Note1 fill:#ef4444,stroke:#dc2626
```

### Lock Safety Guarantees

| Property | Without Fencing | With Fencing | Implementation |
|----------|-----------------|--------------|----------------|
| **Mutual Exclusion** | ✓ (mostly) | ✓ | One holder at a time |
| **Deadlock Free** | ✓ | ✓ | TTL expiration |
| **Fault Tolerant** | ✗ | ✓ | Survives delays |
| **Protection from Delays** | ✗ | ✓ | Monotonic tokens |

---

## 🔧 Level 3: Deep Dive

### The Redlock Algorithm

Martin Kleppmann's analysis of Redis Redlock revealed important limitations:

```mermaid
sequenceDiagram
    participant Client
    participant Redis1
    participant Redis2  
    participant Redis3
    participant Redis4
    participant Redis5
    
    Note over Client: Start time T0
    
    Client->>Redis1: SET lock:X uuid NX PX 30000
    Redis1-->>Client: OK
    
    Client->>Redis2: SET lock:X uuid NX PX 30000
    Redis2-->>Client: OK
    
    Client->>Redis3: SET lock:X uuid NX PX 30000
    Note over Redis3: Network delay
    
    Client->>Redis4: SET lock:X uuid NX PX 30000
    Redis4-->>Client: OK
    
    Client->>Redis5: SET lock:X uuid NX PX 30000
    Redis5-->>Client: FAIL (timeout)
    
    Redis3-->>Client: OK (delayed)
    
    Note over Client: End time T1
    Note over Client: Acquired on 4/5 nodes
    Note over Client: Validity = TTL - (T1-T0) - drift
    
    rect rgb(255, 240, 240)
        Note over Client,Redis5: DANGER ZONE
        Note over Client: GC pause / clock jump
        Note over Redis1,Redis5: Locks expire!
        Note over Client: Client thinks it has lock
    end
```

### Redlock Problems

```mermaid
graph TB
    subgraph "Timing Assumptions"
        P1[Process pauses<br/>unbounded]
        P2[Clock jumps<br/>NTP sync]
        P3[Network delays<br/>unbounded]
    end
    
    subgraph "Safety Violations"  
        V1[Lock expires during pause]
        V2[Clock drift calculation wrong]
        V3[Split brain possible]
    end
    
    subgraph "Better Alternatives"
        A1[Use consensus<br/>etcd/ZooKeeper]
        A2[Use fencing tokens]
        A3[Design for eventual<br/>consistency]
    end
    
    P1 --> V1
    P2 --> V2
    P3 --> V3
    
    V1 --> A1
    V2 --> A2
    V3 --> A3
    
    style P1 fill:#ef4444,stroke:#dc2626
    style P2 fill:#ef4444,stroke:#dc2626
    style P3 fill:#ef4444,stroke:#dc2626
```

### Problems with Distributed Locks

### Fencing Tokens for Safety

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant C2 as Client 2
    participant LM as Lock Manager
    participant DB as Database
    
    C1->>LM: Acquire lock(resource)
    LM->>LM: token = 42
    LM-->>C1: Lock + Token(42)
    
    C1->>DB: Write(data, token=42)
    DB->>DB: Store max_token=42
    DB-->>C1: Success
    
    Note over C1: GC pause / network issue
    
    C2->>LM: Acquire lock(resource)
    Note over LM: C1's lock expired
    LM->>LM: token = 43
    LM-->>C2: Lock + Token(43)
    
    C2->>DB: Write(data, token=43)
    DB->>DB: 43 > 42 ✓
    DB->>DB: Store max_token=43
    DB-->>C2: Success
    
    Note over C1: Resume from pause
    C1->>DB: Write(data, token=42)
    DB->>DB: 42 < 43 ✗
    DB-->>C1: Rejected - stale token
```

### Fencing Token Flow

```mermaid
graph LR
    subgraph "Lock Service"
        Counter[Token Counter<br/>Current: 43]
        LockTable[Lock Table]
    end
    
    subgraph "Protected Resource"
        MaxToken[Max Token Seen: 43]
        Data[Protected Data]
    end
    
    Client -->|1. Request lock| Counter
    Counter -->|2. Increment & return| Client
    Client -->|3. Operation + token| MaxToken
    MaxToken -->|4. If token >= max| Data
    MaxToken -->|5. If token < max| Reject
    
    style Reject fill:#ef4444,stroke:#dc2626
```
---

## 🚀 Level 4: Expert

### Production Distributed Lock Systems

#### Google's Chubby Lock Service

```mermaid
graph TB
    subgraph "Chubby Architecture"
        subgraph "Chubby Cell (5 replicas)"
            Master[Master<br/>Elected via Paxos]
            R1[Replica 1]
            R2[Replica 2] 
            R3[Replica 3]
            R4[Replica 4]
            
            Master <-->|Paxos| R1
            Master <-->|Paxos| R2
            Master <-->|Paxos| R3
            Master <-->|Paxos| R4
        end
        
        subgraph "Client Library"
            Cache[Local Cache]
            Session[Session Manager]
            KeepAlive[KeepAlive Thread]
        end
        
        Client[Application] --> Session
        Session --> Master
        KeepAlive -->|Periodic| Master
    end
    
    subgraph "Lock Hierarchy"
        Root["/ls"]
        Cell["/ls/cell"]
        Lock1["/ls/cell/service/master"]
        Lock2["/ls/cell/service/config"]
        
        Root --> Cell
        Cell --> Lock1
        Cell --> Lock2
    end
    
    style Master fill:#10b981,stroke:#059669,stroke-width:3px
```

### Chubby Session & Lock Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Lib as Chubby Library
    participant Master as Chubby Master
    participant Paxos as Paxos Group
    
    App->>Lib: Open("/ls/cell/lock")
    Lib->>Master: CreateSession()
    Master-->>Lib: SessionID + lease
    
    loop KeepAlive
        Lib->>Master: KeepAlive(SessionID)
        Master-->>Lib: Lease extension
    end
    
    App->>Lib: Acquire("/ls/cell/lock")
    Lib->>Master: AcquireLock(SessionID, path)
    
    Master->>Paxos: Propose lock acquisition
    Paxos-->>Master: Consensus achieved
    
    Master->>Master: Update lock table
    Master-->>Lib: Lock acquired
    Lib-->>App: Success
    
    Note over App: Hold lock...
    
    alt Session timeout
        Master->>Master: Detect missed KeepAlive
        Master->>Paxos: Propose session cleanup
        Master->>Master: Release all session locks
    else Normal release
        App->>Lib: Release("/ls/cell/lock")
        Lib->>Master: ReleaseLock(SessionID, path)
    end
```
#### etcd Distributed Locks

```mermaid
graph TB
    subgraph "etcd Lock Implementation"
        subgraph "Lock Components"
            Lease[Lease (TTL)]
            Key[Lock Key]
            Rev[Revision Number]
            
            Lease --> Key
            Key --> Rev
        end
        
        subgraph "Lock Algorithm"
            Create[Create key with<br/>lowest revision]
            Wait[Wait for lower<br/>revisions to delete]
            Hold[Hold lock]
            Delete[Delete key]
            
            Create --> Wait
            Wait --> Hold
            Hold --> Delete
        end
    end
    
    subgraph "Example Lock Queue"
        K1[key: /locks/x/000001<br/>holder: client-A]
        K2[key: /locks/x/000002<br/>holder: client-B]
        K3[key: /locks/x/000003<br/>holder: client-C]
        
        K1 -->|watches| K2
        K2 -->|watches| K3
        
        Note1[Client-A holds lock]
        Note2[Client-B waiting]
        Note3[Client-C waiting]
    end
    
    style K1 fill:#10b981,stroke:#059669,stroke-width:3px
    style Hold fill:#10b981,stroke:#059669
```

### etcd Lock Operations

| Operation | etcd Command | Description |
|-----------|--------------|-------------|  
| **Create Lock** | `PUT /locks/name/uuid --lease=id` | Create with lease |
| **List Waiters** | `GET /locks/name --prefix` | See all waiting |
| **Watch Previous** | `WATCH /locks/name/prev_uuid` | Wait for turn |
| **Release** | `DELETE /locks/name/uuid` | Explicit release |
| **Auto-Release** | Lease expires | Automatic on TTL |
### Real-World Case Study: Uber's Distributed Lock

```mermaid
graph TB
    subgraph "Uber's Lock Architecture"
        subgraph "Client Tier"
            App[Application]
            LocalCache[Local Cache<br/>Read Locks]
            Client[Lock Client]
        end
        
        subgraph "Lock Service Tier"
            LB[Load Balancer]
            LS1[Lock Server 1]
            LS2[Lock Server 2]
            LS3[Lock Server 3]
        end
        
        subgraph "Storage Tier"
            subgraph "Read Locks"
                Redis1[Redis Cluster]
            end
            subgraph "Write Locks"
                ZK[ZooKeeper Ensemble]
            end
        end
        
        App --> LocalCache
        LocalCache -->|miss| Client
        Client --> LB
        LB --> LS1
        LB --> LS2
        LB --> LS3
        
        LS1 --> Redis1
        LS2 --> ZK
        LS3 --> Redis1
    end
    
    subgraph "Optimization Strategies"
        O1[Read lock caching]
        O2[Write lock queueing]
        O3[Priority-based scheduling]
        O4[Deadlock detection]
    end
    
    style LocalCache fill:#10b981,stroke:#059669
    style O1 fill:#fbbf24,stroke:#f59e0b
```

### Lock Performance Metrics

```mermaid
graph LR
    subgraph "Key Metrics"
        Latency[Acquisition Latency<br/>P50: 1ms<br/>P99: 10ms]
        Contention[Lock Contention<br/>Rate: 5%]
        Timeouts[Timeout Rate<br/>0.1%]
        Cache[Cache Hit Rate<br/>Read: 95%]
    end
    
    subgraph "Monitoring"
        M1[Grafana Dashboard]
        M2[Alert on P99 > 50ms]
        M3[Alert on contention > 20%]
        M4[Deadlock detection]
    end
    
    Latency --> M1
    Contention --> M2
    Timeouts --> M3
    Cache --> M1
```
---

## 🎯 Level 5: Mastery

### Theoretical Foundations

#### The FLP Impossibility Result

```mermaid
graph TB
    subgraph "FLP Impossibility for Locks"
        FLP["No perfect distributed lock<br/>in asynchronous systems"]
        
        subgraph "Fundamental Problems"
            P1[Cannot distinguish<br/>slow from dead]
            P2[No synchronized<br/>clocks]
            P3[Network delays<br/>unbounded]
        end
        
        FLP --> P1
        FLP --> P2  
        FLP --> P3
    end
    
    subgraph "Real-World Implications"
        subgraph "Scenario 1: Process Pause"
            S1A[Client acquires lock]
            S1B[GC pause for 30s]
            S1C[Lock expires (TTL=10s)]
            S1D[Other client gets lock]
            S1E[Original client resumes]
            S1F[Two clients think they have lock!]
            
            S1A --> S1B --> S1C --> S1D --> S1E --> S1F
        end
        
        subgraph "Scenario 2: Clock Skew"
            S2A[Lock expires at T+30s]
            S2B[Node A: time is T+35s]
            S2C[Node B: time is T+25s]
            S2D[Who is right?]
            
            S2A --> S2B
            S2A --> S2C
            S2B --> S2D
            S2C --> S2D
        end
    end
    
    style FLP fill:#ef4444,stroke:#dc2626,stroke-width:3px
    style S1F fill:#ef4444,stroke:#dc2626
    style S2D fill:#f59e0b,stroke:#d97706
```
#### Optimal Lock Algorithms

```mermaid
graph TB
    subgraph "Theoretical Optimal Lock Design"
        subgraph "Components"
            VC[Vector Clocks<br/>Track causality]
            QS[Quorum System<br/>Fault tolerance]
            FT[Fencing Tokens<br/>Monotonic ordering]
            HB[Happens-Before<br/>Lamport ordering]
        end
        
        subgraph "Algorithm Flow"
            A1[Increment vector clock]
            A2[Broadcast to quorum]
            A3[Collect ACKs]
            A4{Quorum<br/>reached?}
            A5{Causality<br/>preserved?}
            A6[Grant lock]
            A7[Deny lock]
            
            A1 --> A2 --> A3 --> A4
            A4 -->|Yes| A5
            A4 -->|No| A7
            A5 -->|Yes| A6
            A5 -->|No| A7
        end
    end
    
    subgraph "Trade-offs"
        T1[Safety: ✓✓✓<br/>Never two holders]
        T2[Liveness: ✓✓<br/>Progress with quorum]
        T3[Performance: ✓<br/>O(n) messages]
        T4[Complexity: ✗<br/>Hard to implement]
    end
    
    style A6 fill:#10b981,stroke:#059669
    style A7 fill:#ef4444,stroke:#dc2626
```

### Lock Algorithm Comparison

| Algorithm | Safety | Liveness | Performance | Complexity |
|-----------|--------|----------|-------------|------------|
| **Simple TTL** | ✗ (process pauses) | ✓✓✓ | ✓✓✓ | ✓✓✓ |
| **Redlock** | ✗ (timing assumptions) | ✓✓ | ✓✓ | ✓✓ |
| **ZooKeeper** | ✓✓ | ✓✓ | ✓ | ✓ |
| **Chubby/etcd** | ✓✓✓ | ✓✓ | ✓ | ✓ |
| **Optimal + Fencing** | ✓✓✓ | ✓ | ✗ | ✗ |

### Future Directions

1. **Blockchain-Based Locks**: Using smart contracts for distributed locks
2. **ML-Optimized Locks**: Predicting contention and pre-acquiring locks
3. **Quantum Distributed Locks**: Leveraging quantum entanglement
4. **Conflict-Free Locks**: CRDT-based locking mechanisms

---

## 📋 Quick Reference

### Lock Selection Guide

| Use Case | Recommended Solution | Why |
|----------|---------------------|-----|
| Leader election | etcd/ZooKeeper | Built-in lease support |
| Resource pooling | Database locks | Simple, ACID guarantees |
| Distributed cron | Redis with Redlock | Good enough for most cases |
| Critical sections | Chubby/etcd | Strong consistency |
| Cache invalidation | Eventually consistent | Locks often overkill |

### Implementation Checklist

- [ ] Define lock granularity (resource level)
- [ ] Set appropriate timeouts
- [ ] Implement lock renewal for long operations
- [ ] Add monitoring and metrics
- [ ] Handle lock release on process crash
- [ ] Test with network partitions
- [ ] Document lock hierarchy to prevent deadlocks
- [ ] Implement deadlock detection

---

---

*"A distributed lock is a promise that's hard to keep and harder to break safely."*

---

**Previous**: [← CQRS (Command Query Responsibility Segregation)](cqrs.md) | **Next**: [Edge Computing/IoT Patterns →](edge-computing.md)

**Related**: [Leader Election](leader-election.md) • [Consensus](consensus.md)