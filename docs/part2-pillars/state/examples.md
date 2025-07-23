---
title: State Management Examples
description: "Real-world examples of state management patterns in distributed systems including Dynamo, Spanner, and modern approaches"
type: pillar
difficulty: intermediate
reading_time: 25 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../../introduction/index.md) → [Part II: Pillars](../index.md) → [State](index.md) → **State Management Examples**

# State Management Examples

## Real-World Case Studies

### 1. Amazon DynamoDB: Eventually Consistent by Design

**Problem**: Build a database that scales to millions of requests per second with predictable performance

**Architecture Evolution**:

```mermaid
graph TD
    subgraph "2004: Simple Key-Value Store"
        A1[Single Master] -->|bottleneck| A2[Consistent Hashing Solution]
    end
    
    subgraph "2007: Dynamo Paper"
        B1[Availability During Failures] -->|addressed by| B2[Eventual Consistency]
        B2 --> B3[Vector Clocks]
    end
    
    subgraph "2012: DynamoDB Service"
        C1[Complex Vector Clocks] -->|simplified to| C2[Last-Write-Wins]
        C2 --> C3[Conditional Writes]
    end
    
    subgraph "2018: Global Tables"
        D1[Cross-Region Replication] -->|solved with| D2[CRDTs]
    end
    
    A2 --> B1
    B3 --> C1
    C3 --> D1
    
    style A1 fill:#ff9999
    style B1 fill:#ff9999
    style C1 fill:#ff9999
    style D1 fill:#ff9999
    style A2 fill:#99ff99
    style B2 fill:#99ff99
    style B3 fill:#99ff99
    style C2 fill:#99ff99
    style C3 fill:#99ff99
    style D2 fill:#99ff99
```

**Key Design Decisions**:

```mermaid
sequenceDiagram
    participant Client
    participant Coordinator as Coordinator Node
    participant N1 as Node 1
    participant N2 as Node 2
    participant N3 as Node 3
    
    Note over Coordinator: PUT Operation (N=3, W=2)
    Client->>Coordinator: PUT(key, value)
    Coordinator->>Coordinator: Update vector clock
    Coordinator->>Coordinator: Store locally
    
    par Replication
        Coordinator->>N1: Replicate(key, value, clock)
        and
        Coordinator->>N2: Replicate(key, value, clock)
        and
        Coordinator->>N3: Replicate(key, value, clock)
    end
    
    N1-->>Coordinator: ACK
    N2-->>Coordinator: ACK
    Note over Coordinator: W=2 writes succeeded
    Coordinator-->>Client: Success
    
    Note over Coordinator: GET Operation (N=3, R=2)
    Client->>Coordinator: GET(key)
    
    par Read from R nodes
        Coordinator->>N1: Read(key)
        and
        Coordinator->>N2: Read(key)
    end
    
    N1-->>Coordinator: value + vector_clock
    N2-->>Coordinator: value + vector_clock
    
    Coordinator->>Coordinator: Resolve conflicts using vector clocks
    Note over Coordinator: Check happens-before relationship
    Coordinator-->>Client: Resolved value
```

### DynamoDB Quorum Configuration

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| N | Number of replicas | 3 |
| W | Write quorum | 2 |
| R | Read quorum | 2 |
| DW | Durable write quorum | 1 |
| RW | Read-write quorum | N |

### Consistency Guarantees

| Configuration | Consistency Level | Use Case |
|---------------|-------------------|----------|
| W + R > N | Strong consistency | Critical data |
| W + R ≤ N | Eventual consistency | High availability |
| W = N | Read availability during failures | Write-heavy workloads |
| R = N | Write availability during failures | Read-heavy workloads |

**Lessons Learned**:
- Vector clocks are powerful but complex for developers
- Last-write-wins is often good enough with proper conflict detection
- Conditional writes can replace many vector clock use cases
- CRDTs enable truly conflict-free multi-region replication

### 2. Redis Cluster: Sharding with Availability

**Problem**: Scale Redis beyond single-machine memory limits while maintaining sub-millisecond latency

**Architecture**:

```mermaid
graph TB
    subgraph "Hash Slot Distribution (16,384 slots)"
        MA[Master A<br/>Slots 0-5460]
        MB[Master B<br/>Slots 5461-10922]
        MC[Master C<br/>Slots 10923-16383]
        
        RA[Replica A]
        RB[Replica B]
        RC[Replica C]
        
        MA -.->|replication| RA
        MB -.->|replication| RB
        MC -.->|replication| RC
    end
    
    subgraph "Client Request Routing"
        Client[Client] -->|CRC16(key) % 16384| Slot[Hash Slot]
        Slot -->|Slot Mapping| Master[Appropriate Master]
    end
    
    style MA fill:#ff9999
    style MB fill:#99ff99
    style MC fill:#9999ff
    style RA fill:#ffcccc
    style RB fill:#ccffcc
    style RC fill:#ccccff
```

**Implementation Details**:

```mermaid
stateDiagram-v2
    [*] --> Normal: Slot owned by node
    
    Normal --> Migrating: migrate_slot() called
    Migrating --> KeyCheck: Client request
    
    KeyCheck --> ExecuteLocal: Key exists locally
    KeyCheck --> ASK_Redirect: Key not found
    
    ASK_Redirect --> TargetNode: Client follows ASK
    
    Migrating --> BatchTransfer: Migration process
    BatchTransfer --> BatchTransfer: Transfer next batch
    BatchTransfer --> UpdateClusterState: All keys transferred
    
    UpdateClusterState --> [*]: Migration complete
    
    Normal --> MOVED_Redirect: Wrong slot owner
    MOVED_Redirect --> CorrectNode: Client follows MOVED
```

### Redis Cluster Slot Migration Process

| Phase | Source Node | Target Node | Client Behavior |
|-------|-------------|-------------|----------------|
| 1. Pre-migration | Owns slot | - | Routes to source |
| 2. Migration starts | MIGRATING state | IMPORTING state | May get ASK redirects |
| 3. Key transfer | Transfers keys in batches | Receives keys | Handles both nodes |
| 4. Post-migration | - | Owns slot | Routes to target |

### Redirect Types

| Type | Meaning | Client Action | Persistence |
|------|---------|---------------|-------------|
| MOVED | Slot permanently moved | Update slot mapping | Permanent |
| ASK | Key might be migrating | One-time redirect | Temporary |

**Resharding Process**:

```mermaid
flowchart TD
    Start([Rebalancing Start]) --> Calculate[Calculate target distribution]
    Calculate --> Analyze[Analyze current vs target]
    
    Analyze --> Identify{Identify moves}
    Identify -->|Slots to give| Sources[Source nodes list]
    Identify -->|Slots to receive| Targets[Target nodes list]
    
    Sources --> Match[Match sources with targets]
    Targets --> Match
    
    Match --> Execute[Execute migrations]
    Execute --> Migration1[Migrate slot X: A→B]
    Execute --> Migration2[Migrate slot Y: B→C]
    Execute --> Migration3[Migrate slot Z: C→A]
    
    Migration1 --> Complete
    Migration2 --> Complete
    Migration3 --> Complete[Rebalancing Complete]
```

### Slot Distribution Example (3 nodes → 4 nodes)

| Node | Before (3 nodes) | After (4 nodes) | Slots to Move |
|------|------------------|-----------------|---------------|
| A | 0-5461 (5462 slots) | 0-4095 (4096 slots) | Give: 1366 |
| B | 5462-10922 (5461 slots) | 4096-8191 (4096 slots) | Give: 1365 |
| C | 10923-16383 (5461 slots) | 8192-12287 (4096 slots) | Give: 1365 |
| D | - | 12288-16383 (4096 slots) | Receive: 4096 |

### 3. Cassandra: Tunable Consistency

**Problem**: Provide tunable consistency levels per operation while maintaining high availability

**Consistency Levels**:

### Cassandra Consistency Levels

| Level | Write Requirement | Read Requirement | Use Case |
|-------|------------------|------------------|----------|
| ANY | Any node (including hints) | N/A | Maximum availability |
| ONE | 1 replica | 1 replica | High performance |
| TWO | 2 replicas | 2 replicas | Moderate consistency |
| THREE | 3 replicas | 3 replicas | Higher consistency |
| QUORUM | ⌊RF/2⌋ + 1 | ⌊RF/2⌋ + 1 | Strong consistency |
| ALL | All replicas | All replicas | Maximum consistency |
| LOCAL_QUORUM | Majority in local DC | Majority in local DC | Multi-DC strong consistency |
| EACH_QUORUM | Majority in each DC | N/A | Global strong writes |
| LOCAL_ONE | 1 in local DC | 1 in local DC | DC-aware performance |

```mermaid
sequenceDiagram
    participant Client
    participant Coordinator
    participant R1 as Replica 1
    participant R2 as Replica 2
    participant R3 as Replica 3
    
    Note over Client,R3: Write with QUORUM (RF=3, need 2 acks)
    
    Client->>Coordinator: Write(key, value, QUORUM)
    
    par Parallel writes to all replicas
        Coordinator->>R1: Write(key, value)
        and
        Coordinator->>R2: Write(key, value)
        and
        Coordinator->>R3: Write(key, value)
    end
    
    R1-->>Coordinator: ACK
    R2-->>Coordinator: ACK
    Note over Coordinator: 2 ACKs received (meets QUORUM)
    Coordinator-->>Client: Success
    
    R3-->>Coordinator: ACK (late)
    Note over Coordinator: Already returned to client
    
    Note over Client,R3: Read with QUORUM (need 2 responses)
    
    Client->>Coordinator: Read(key, QUORUM)
    
    par Query minimum replicas
        Coordinator->>R1: Read(key)
        and
        Coordinator->>R2: Read(key)
    end
    
    R1-->>Coordinator: value(t1)
    R2-->>Coordinator: value(t2)
    
    Coordinator->>Coordinator: Resolve conflicts (LWW)
    Note over Coordinator: t2 > t1, so use value(t2)
    
    Coordinator->>R3: Async read repair
    Coordinator-->>Client: value(t2)
```

### Consistency Arithmetic

| Scenario | Formula | Result |
|----------|---------|--------|  
| Strong Consistency | W + R > RF | Always see latest write |
| Eventual Consistency | W + R ≤ RF | May see stale data |
| Read Heavy | W = 1, R = RF | Fast writes, consistent reads |
| Write Heavy | W = RF, R = 1 | Consistent writes, fast reads |

### 4. Elasticsearch: Distributed Search State

**Problem**: Maintain search indices across distributed nodes with real-time updates

**Architecture**:

```mermaid
graph TB
    subgraph "Elasticsearch Index Architecture"
        Index[Index: products]
        Index --> PS1[Primary Shard 0]
        Index --> PS2[Primary Shard 1]
        Index --> PS3[Primary Shard 2]
        
        PS1 --> RS1A[Replica 0_0]
        PS1 --> RS1B[Replica 0_1]
        
        PS2 --> RS2A[Replica 1_0]
        PS2 --> RS2B[Replica 1_1]
        
        PS3 --> RS3A[Replica 2_0]
        PS3 --> RS3B[Replica 2_1]
    end
    
    subgraph "Document Indexing Flow"
        Doc[Document] --> TLog[Transaction Log]
        TLog --> Buffer[In-Memory Buffer]
        Buffer -->|refresh interval| Segment[Lucene Segment]
        Segment -->|merge policy| Merged[Merged Segment]
    end
    
    subgraph "Search Flow"
        Query[Search Query] --> Coordinator[Coordinator Node]
        Coordinator --> S1[Search Shard 1]
        Coordinator --> S2[Search Shard 2]
        Coordinator --> S3[Search Shard 3]
        S1 --> Results1[Partial Results]
        S2 --> Results2[Partial Results]
        S3 --> Results3[Partial Results]
        Results1 --> Merge[Merge & Rank]
        Results2 --> Merge
        Results3 --> Merge
        Merge --> Final[Final Results]
    end
```

### Elasticsearch State Components

| Component | Purpose | Durability | Performance Impact |
|-----------|---------|------------|-------------------|
| Transaction Log | Durability, crash recovery | Fsync to disk | Write latency |
| In-Memory Buffer | Batching writes | Lost on crash | High write throughput |
| Lucene Segments | Immutable search structures | Persistent | Read performance |
| Segment Merging | Optimize search performance | Background process | I/O intensive |

### Refresh vs Flush

| Operation | What it does | Frequency | Impact |
|-----------|--------------|-----------|--------|  
| Refresh | Buffer → Searchable segment | Every 1s (default) | Makes docs searchable |
| Flush | Commit point + clear translog | Every 30min or 512MB | Ensures durability |

### 5. Apache Kafka: Distributed Log State

**Problem**: Maintain a distributed, replicated log with strong ordering guarantees

**Core Concepts**:

```mermaid
stateDiagram-v2
    [*] --> Leader: Elected by controller
    Leader --> Append: Producer sends messages
    Append --> AssignOffsets: Assign sequential offsets
    AssignOffsets --> WriteLog: Write to local log
    WriteLog --> Replicate: Send to ISR followers
    
    Replicate --> WaitAcks: acks=all
    Replicate --> ReturnOffset: acks=1
    
    WaitAcks --> AllISRAck: All replicas respond
    WaitAcks --> Timeout: Some replicas timeout
    
    Timeout --> RemoveFromISR: Update ISR list
    RemoveFromISR --> ReturnOffset
    AllISRAck --> UpdateHWM: Update high water mark
    UpdateHWM --> ReturnOffset: Return offset to producer
    
    Leader --> Follower: Leader fails
    Follower --> FetchFromLeader: Continuously fetch
    FetchFromLeader --> ApplyToLog: Apply to local log
    ApplyToLog --> SendAck: Acknowledge to leader
```

### Kafka Partition Key Concepts

| Concept | Description | Purpose |
|---------|-------------|---------|  
| Log Start Offset (LSO) | First available message offset | Log retention boundary |
| Log End Offset (LEO) | Next offset to be assigned | Write position |
| High Water Mark (HWM) | Min replicated offset across ISR | Consumer read boundary |
| In-Sync Replicas (ISR) | Replicas caught up with leader | Durability guarantee |
| Leader Epoch | Generation number of leader | Prevent split-brain |

### Kafka Replication Protocol

```mermaid
sequenceDiagram
    participant Producer
    participant Leader
    participant Follower1
    participant Follower2
    participant Consumer
    
    Producer->>Leader: Produce(messages, acks=all)
    Leader->>Leader: Assign offsets 100-102
    Leader->>Leader: Write to log
    
    par Replication
        Leader->>Follower1: Replicate(100-102)
        and
        Leader->>Follower2: Replicate(100-102)
    end
    
    Follower1->>Follower1: Write to log
    Follower1-->>Leader: ACK(102)
    
    Follower2->>Follower2: Write to log  
    Follower2-->>Leader: ACK(102)
    
    Leader->>Leader: Update HWM to 102
    Leader-->>Producer: Success(offset=100)
    
    Consumer->>Leader: Fetch(offset=100)
    Leader-->>Consumer: Messages(100-102, HWM=102)
```

## State Patterns Implementation

### 1. Write-Ahead Log (WAL)

```mermaid
flowchart TD
    subgraph "Write-Ahead Log Structure"
        Entry[New Entry] --> Serialize[Serialize Entry]
        Serialize --> CheckSegment{Current segment full?}
        CheckSegment -->|Yes| Roll[Roll to new segment]
        CheckSegment -->|No| Append[Append to segment]
        Roll --> Append
        Append --> CheckSync{Should sync?}
        CheckSync -->|Yes| Fsync[Fsync to disk]
        CheckSync -->|No| Return[Return offset]
        Fsync --> Return
    end
    
    subgraph "Recovery Process"
        Crash[System Crash] --> ScanSegments[Scan all segments]
        ScanSegments --> ReadSegment[Read segment N]
        ReadSegment --> Deserialize[Deserialize entries]
        Deserialize --> ApplyState[Apply to state]
        ApplyState --> NextSegment{More segments?}
        NextSegment -->|Yes| ReadSegment
        NextSegment -->|No| Recovered[State recovered]
    end
    
    subgraph "Truncation (Rollback)"
        Uncommitted[Uncommitted entries] --> FindOffset[Find target offset]
        FindOffset --> TruncateSegment[Truncate segment]
        TruncateSegment --> RemoveLater[Remove later segments]
        RemoveLater --> Clean[Clean state]
    end
```

### WAL Design Decisions

| Aspect | Options | Trade-offs |
|--------|---------|------------|  
| Sync Policy | Every write | Durability vs Performance |
| | Periodic (time-based) | Bounded data loss |
| | Size-based | Batch efficiency |
| Segment Size | Small (e.g., 64MB) | Faster recovery, more files |
| | Large (e.g., 1GB) | Fewer files, slower recovery |
| Compression | None | Fast writes, more space |
| | Snappy/LZ4 | Space efficient, CPU cost |

### 2. Conflict-Free Replicated Data Types (CRDTs)

### Conflict-Free Replicated Data Types (CRDTs)

```mermaid
graph TB
    subgraph "CRDT Types"
        State[State-based CRDTs]
        Op[Operation-based CRDTs]
        
        State --> GCounter[G-Counter<br/>Grow-only]
        State --> PNCounter[PN-Counter<br/>Inc/Dec]
        State --> LWWReg[LWW-Register<br/>Last-Write-Wins]
        State --> ORSet[OR-Set<br/>Observed-Remove]
        
        Op --> OpCounter[Op-Counter]
        Op --> OpSet[Op-Set]
    end
    
    subgraph "Merge Semantics"
        Node1[Node A State] --> Merge{Merge Function}
        Node2[Node B State] --> Merge
        Merge --> Converged[Converged State]
        
        Note1[Always Commutative] -.-> Merge
        Note2[Always Idempotent] -.-> Merge
        Note3[Always Associative] -.-> Merge
    end
```

### CRDT Comparison

| CRDT Type | Operations | Merge Rule | Use Case |
|-----------|------------|------------|----------|
| G-Counter | increment() | max(a,b) per node | Page views, likes |
| PN-Counter | inc(), dec() | P.merge(), N.merge() | Account balance |
| LWW-Register | set(value) | Latest timestamp wins | User preferences |
| OR-Set | add(), remove() | Union tags - tombstones | Shopping cart |
| 2P-Set | add(), remove() | Union both sets | Membership |

### G-Counter Example

```mermaid
sequenceDiagram
    participant A as Node A
    participant B as Node B
    participant C as Node C
    
    Note over A,C: Initial state: all {}
    
    A->>A: increment(5)
    Note over A: {A:5}
    
    B->>B: increment(3)
    Note over B: {B:3}
    
    C->>C: increment(2)
    Note over C: {C:2}
    
    A->>B: Send state {A:5}
    B->>B: Merge: {A:5, B:3}
    Note over B: Value = 8
    
    B->>C: Send state {A:5, B:3}
    C->>C: Merge: {A:5, B:3, C:2}
    Note over C: Value = 10
    
    C->>A: Send state {A:5, B:3, C:2}
    A->>A: Merge: {A:5, B:3, C:2}
    Note over A: Value = 10
    
    Note over A,C: All nodes converged to 10
```

### OR-Set Mechanics

```mermaid
stateDiagram-v2
    [*] --> Empty: Initialize
    Empty --> HasElements: add(X) with tag
    HasElements --> HasElements: add(X) with new tag
    HasElements --> Tombstoned: remove(X) moves tags
    Tombstoned --> HasElements: add(X) with new tag
    
    note right of HasElements
        Elements: {X: {t1, t2}}
        Tombstones: {}
    end note
    
    note right of Tombstoned
        Elements: {X: {t1, t2}}
        Tombstones: {X: {t1, t2}}
        contains(X) = false
    end note
```

### 3. Multi-Version Concurrency Control (MVCC)

### Multi-Version Concurrency Control (MVCC)

```mermaid
graph TB
    subgraph "Version Chain for Key 'X'"
        V1[Version 1<br/>Value: A<br/>Created: T1<br/>Deleted: T3]
        V2[Version 2<br/>Value: B<br/>Created: T3<br/>Deleted: T5]
        V3[Version 3<br/>Value: C<br/>Created: T5<br/>Deleted: null]
        
        V1 --> V2
        V2 --> V3
    end
    
    subgraph "Transaction Views"
        T2[Transaction T2<br/>Sees: A] -.-> V1
        T4[Transaction T4<br/>Sees: B] -.-> V2
        T6[Transaction T6<br/>Sees: C] -.-> V3
    end
```

### MVCC Transaction Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Begin: begin_transaction()
    Begin --> Active: Assigned TX_ID
    
    Active --> Reading: read(key)
    Reading --> Active: Add to read_set
    
    Active --> Writing: write(key, value)
    Writing --> Active: Add to write_set
    
    Active --> Validation: commit()
    
    Validation --> CheckConflicts: Validate read_set
    CheckConflicts --> Abort: Concurrent modification
    CheckConflicts --> WritePhase: No conflicts
    
    WritePhase --> CreateVersions: Write new versions
    CreateVersions --> Committed: Success
    
    Abort --> [*]: Rollback
    Committed --> [*]: Complete
```

### MVCC Visibility Rules

| Scenario | Version Created | Version Deleted | Visible to TX? |
|----------|----------------|-----------------|----------------|
| Normal read | Before TX | After TX or NULL | ✓ Yes |
| Too new | After TX | Any | ✗ No |
| Already deleted | Before TX | Before TX | ✗ No |
| Own write | By TX | Any | ✓ Yes |

### Concurrent Transaction Example

```mermaid
sequenceDiagram
    participant T1 as Transaction 1
    participant T2 as Transaction 2
    participant DB as MVCC Store
    
    T1->>DB: begin_transaction() → TX1
    T2->>DB: begin_transaction() → TX2
    
    T1->>DB: read(X) → "A"
    Note over DB: T1 read_set = {X}
    
    T2->>DB: read(X) → "A"
    Note over DB: T2 read_set = {X}
    
    T1->>DB: write(X, "B")
    Note over DB: T1 write_set = {X: "B"}
    
    T2->>DB: write(X, "C")
    Note over DB: T2 write_set = {X: "C"}
    
    T1->>DB: commit()
    DB->>DB: Validate: No conflicts
    DB->>DB: Create version (X, "B", TX3)
    DB-->>T1: Success
    
    T2->>DB: commit()
    DB->>DB: Validate: X modified by T1!
    DB-->>T2: Abort - Write conflict
```

### MVCC Storage Overhead

| Aspect | Impact | Mitigation |
|--------|--------|------------|  
| Multiple versions | Space overhead | Vacuum old versions |
| Version chains | Lookup overhead | Index on latest |
| Long transactions | Prevent cleanup | Transaction timeout |
| Read tracking | Memory overhead | Bloom filters |

## Key Takeaways

1. **State distribution follows data access patterns** - Don't fight your workload

2. **Replication strategies depend on consistency needs** - Choose wisely

3. **Conflict resolution must be deterministic** - Last-write-wins, CRDTs, or vector clocks

4. **State recovery must be fast** - WAL, snapshots, and incremental recovery

5. **Sharding requires careful key selection** - Hot spots will find you

Remember: State is the hardest part of distributed systems. It's where all the trade-offs live.
