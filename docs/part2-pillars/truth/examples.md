---
title: Truth & Consensus Examples
description: "Real-world examples and case studies demonstrating the concepts in practice"
type: pillar
difficulty: advanced
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-28
---

# Truth & Consensus Examples

<div class="truth-box">
<h2>⚡ The Reality Check</h2>
<p><strong>These aren't theoretical examples—they're production war stories.</strong></p>
<p>Each case study represents millions of dollars saved (or lost) based on truth design choices.</p>
</div>

## 🌍 Google Spanner: Engineering Global Truth

```
┌─────────────────────────────────────────────────────────────┐
│         THE PROBLEM: GLOBAL BANK TRANSFERS                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ TOKYO          NEW YORK        LONDON                       │
│ 09:00:00.123   20:00:00.456   01:00:00.789                │
│ Transfer $1M   Transfer $2M    Transfer $3M                 │
│                                                             │
│ QUESTION: What order did these happen? 🤷                   │
│                                                             │
│ OLD WAY: Pick arbitrary order = WRONG BALANCES 💀           │
│ SPANNER: True global ordering = CORRECT ALWAYS ✅           │
└─────────────────────────────────────────────────────────────┘
```

### The TrueTime Magic

```
┌─────────────────────────────────────────────────────────────┐
│                  TRUETIME ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ DATACENTER A         DATACENTER B         DATACENTER C      │
│ ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│ │ GPS RECEIVER│     │ GPS RECEIVER│     │ GPS RECEIVER│   │
│ │ ATOMIC CLOCK│     │ ATOMIC CLOCK│     │ ATOMIC CLOCK│   │
│ └──────┬──────┘     └──────┬──────┘     └──────┬──────┘   │
│        │                    │                    │          │
│        ▼                    ▼                    ▼          │
│   TIME MASTER          TIME MASTER          TIME MASTER    │
│        │                    │                    │          │
│   ┌────┴─────────────────────┴────────────────────┴────┐   │
│   │              TRUETIME API GUARANTEE                 │   │
│   │     now() → [earliest, latest] where ε ≤ 7ms      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│ THE COMMIT PROTOCOL:                                        │
│ 1. ts = TrueTime.now().latest                             │
│ 2. Wait until TrueTime.now().earliest > ts                │
│ 3. Commit with timestamp ts                                │
│                                                             │
│ RESULT: True external consistency at global scale!         │
└─────────────────────────────────────────────────────────────┘
```

### Production Impact

```
BEFORE SPANNER (Multi-Master MySQL):
• Reconciliation jobs: 24/7 
• Data inconsistencies: Daily
• Engineer hours: 200/month
• Customer complaints: Regular

AFTER SPANNER:
• Reconciliation: NONE NEEDED
• Inconsistencies: ZERO
• Engineer hours: 5/month
• Customer complaints: None

COST: 7ms average commit latency
BENEFIT: Perfect global consistency
```

## ⚡ Bitcoin: The $1 Trillion Consensus

```
┌─────────────────────────────────────────────────────────────┐
│              BITCOIN'S CONSENSUS INNOVATION                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ THE IMPOSSIBLE PROBLEM:                                     │
│ • No trusted parties                                        │
│ • Anyone can participate                                    │
│ • Byzantine actors expected                                 │
│ • Must agree on money! 💰                                   │
│                                                             │
│ THE SOLUTION: PROOF OF WORK                                 │
│                                                             │
│ Block N       Block N+1      Block N+2                      │
│ ┌─────────┐   ┌─────────┐   ┌─────────┐                   │
│ │Nonce:   │──►│Nonce:   │──►│Nonce:   │                   │
│ │74619284 │   │92847561 │   │???????? │                   │
│ │Hash:    │   │Hash:    │   │Mining... │                   │
│ │00000af3 │   │00000b91 │   │          │                   │
│ └─────────┘   └─────────┘   └─────────┘                   │
│                                                             │
│ CONSENSUS RULE: Longest chain wins                         │
│                                                             │
│ ATTACK COST:                                                │
│ 51% attack = $30 BILLION in hardware + electricity         │
└─────────────────────────────────────────────────────────────┘
```

### Probabilistic Finality in Action

```
┌─────────────────────────────────────────────────────────────┐
│              CONFIRMATION CONFIDENCE LEVELS                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 0 conf  ████░░░░░░░░░░░░░░  25%  "Seen in mempool"        │
│ 1 conf  ███████████░░░░░░░  60%  "In a block"             │
│ 2 conf  ████████████████░░  90%  "Probably safe"          │
│ 3 conf  █████████████████░  97%  "Very likely safe"       │
│ 6 conf  ███████████████████  99.9% "Bitcoin standard"     │
│                                                             │
│ REAL WORLD MAPPING:                                         │
│ • Coffee shop: 0 confirmations (instant)                   │
│ • Online store: 1-2 confirmations (10-20 min)             │
│ • Car dealership: 3 confirmations (30 min)                │
│ • Real estate: 6 confirmations (1 hour)                   │
│ • Exchange deposit: 10+ confirmations                      │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Kafka: 7 Trillion Messages of Truth

```
┌─────────────────────────────────────────────────────────────┐
│            KAFKA'S LOG-BASED TRUTH MODEL                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ TRADITIONAL DATABASE HELL:                                  │
│                                                             │
│ Service A ←─READ──┐                                         │
│ Service B ←─READ──┼── DATABASE ──WRITE─→ Service D         │
│ Service C ←─READ──┘                    └─WRITE─→ Service E │
│                                                             │
│ PROBLEMS: Coupling, contention, SPOF, no history           │
│                                                             │
│ KAFKA'S SOLUTION: THE IMMUTABLE LOG                        │
│                                                             │
│ Producers          THE LOG              Consumers          │
│ ┌────────┐        ┌─┬─┬─┬─┬─┐         ┌─────────┐        │
│ │Order Svc├──────►│1│2│3│4│5│────────►│Analytics│        │
│ └────────┘        └─┴─┴─┴─┴─┘         └─────────┘        │
│ ┌────────┐              ▲              ┌─────────┐        │
│ │User Svc ├─────────────┘   └─────────►│Billing  │        │
│ └────────┘                             └─────────┘        │
│                                        ┌─────────┐        │
│                              └─────────►│Search   │        │
│                                        └─────────┘        │
│                                                             │
│ BENEFITS:                                                   │
│ • Decoupled: Services don't know about each other         │
│ • Replayable: Can rebuild any service from log            │
│ • Ordered: Events have definitive sequence                │
│ • Scalable: Partitioned for 1M+ events/second             │
└─────────────────────────────────────────────────────────────┘
```

### LinkedIn's Production Numbers

```
Daily Volume:     7,000,000,000,000 messages
Peak Throughput:  100,000,000 messages/second
Clusters:         100+ production clusters  
Retention:        7-30 days of history
Use Cases:        
  • Activity tracking
  • Metrics pipeline
  • Log aggregation
  • Stream processing
  • Event sourcing

KEY INSIGHT: Log = Single source of truth
```

## 🔐 ZooKeeper: The Coordination Backbone

```
┌─────────────────────────────────────────────────────────────┐
│            ZOOKEEPER POWERS HALF THE INTERNET               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ WHAT IT DOES:                                               │
│                                                             │
│ /kafka                    /hbase                            │
│   /brokers                 /master                          │
│     /1 → host:port          → host:port                     │
│     /2 → host:port        /region-servers                   │
│     /3 → host:port          /1 → metadata                   │
│   /topics                   /2 → metadata                   │
│     /orders                                                 │
│       /0 → leader:1       /solr                            │
│       /1 → leader:2         /collections                    │
│                              /search → config               │
│                                                             │
│ ONE ZOOKEEPER COORDINATES:                                  │
│ • Kafka broker discovery & topic metadata                  │
│ • HBase master election & region assignment                │
│ • Solr/Elasticsearch cluster state                         │
│ • Distributed locks for 1000s of services                  │
│                                                             │
│ THE MAGIC: Strong consistency with watches                 │
└─────────────────────────────────────────────────────────────┘
```

### ZooKeeper in Action: Distributed Lock

```
┌─────────────────────────────────────────────────────────────┐
│                  DISTRIBUTED LOCK RECIPE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. CREATE SEQUENTIAL EPHEMERAL NODE:                       │
│    /locks/mylock/lock-0000000001 (by Client A)            │
│    /locks/mylock/lock-0000000002 (by Client B)            │
│    /locks/mylock/lock-0000000003 (by Client C)            │
│                                                             │
│ 2. LIST CHILDREN, FIND YOUR POSITION:                      │
│    Client A: I'm #1 → I HAVE THE LOCK! ✅                 │
│    Client B: I'm #2 → Watch #1                            │
│    Client C: I'm #3 → Watch #2                            │
│                                                             │
│ 3. WHEN CLIENT A FINISHES:                                 │
│    - Deletes lock-0000000001                              │
│    - Client B gets notification                            │
│    - Client B now has lowest number → LOCK ACQUIRED!      │
│                                                             │
│ GUARANTEES:                                                 │
│ • Fair ordering (FIFO)                                     │
│ • No thundering herd                                       │
│ • Automatic cleanup on failure (ephemeral)                │
└─────────────────────────────────────────────────────────────┘
```

## ⚛️ Ethereum: Computing Consensus at Scale

```
┌─────────────────────────────────────────────────────────────┐
│         ETHEREUM'S WORLD COMPUTER CONSENSUS                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ THE CHALLENGE: Agree on computation, not just data         │
│                                                             │
│ TRANSACTION:                    EVM EXECUTION:              │
│ ┌─────────────────┐            ┌──────────────────┐       │
│ │To: Contract      │            │PUSH 20           │       │
│ │Data: transfer()  │───────────►│PUSH addr         │       │
│ │Value: 0          │            │BALANCE           │       │
│ │Gas: 21000        │            │DUP1              │       │
│ └─────────────────┘            │PUSH amount       │       │
│                                 │GT                │       │
│                                 │JUMPI fail        │       │
│                                 └──────────────────┘       │
│                                          │                  │
│                                          ▼                  │
│                                 ┌──────────────────┐       │
│                                 │STATE CHANGES:    │       │
│                                 │Sender: -100 ETH  │       │
│                                 │Receiver: +100 ETH│       │
│                                 │Gas used: 21000   │       │
│                                 └──────────────────┘       │
│                                                             │
│ CONSENSUS: All nodes must get EXACT same result            │
│                                                             │
│ PRODUCTION SCALE:                                           │
│ • 1.5M transactions/day                                    │
│ • 10,000+ nodes validating                                 │
│ • $400B secured                                            │
└─────────────────────────────────────────────────────────────┘
```

## 🪲 CockroachDB: SQL Meets Distributed Truth

```
┌─────────────────────────────────────────────────────────────┐
│            COCKROACHDB'S HYBRID APPROACH                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ THE IMPOSSIBLE ASK:                                         │
│ "Give me PostgreSQL but distributed globally"              │
│                                                             │
│ THE SOLUTION: RAFT + HYBRID LOGICAL CLOCKS                 │
│                                                             │
│         SQL Query                                           │
│            │                                                │
│            ▼                                                │
│    ┌───────────────┐                                       │
│    │ SQL PARSER    │                                       │
│    └───────┬───────┘                                       │
│            │                                                │
│            ▼                                                │
│    ┌───────────────┐     Range 1    Range 2    Range 3    │
│    │ DISTRIBUTION  │     ┌──────┐   ┌──────┐   ┌──────┐  │
│    │    LAYER      ├────►│RAFT  │   │RAFT  │   │RAFT  │  │
│    └───────────────┘     │Leader│   │Leader│   │Leader│  │
│                          └──┬───┘   └──┬───┘   └──┬───┘  │
│                             │          │          │        │
│                          ┌──┴───┐   ┌──┴───┐   ┌──┴───┐  │
│                          │Follow│   │Follow│   │Follow│  │
│                          └──┬───┘   └──┬───┘   └──┬───┘  │
│                             │          │          │        │
│                          ┌──┴───┐   ┌──┴───┐   ┌──┴───┐  │
│                          │Follow│   │Follow│   │Follow│  │
│                          └──────┘   └──────┘   └──────┘  │
│                                                             │
│ PRODUCTION ACHIEVEMENT:                                     │
│ • ACID transactions across continents                      │
│ • 99.999% availability                                     │
│ • Linear scalability to 100s of nodes                      │
└─────────────────────────────────────────────────────────────┘
```

### Real Customer Impact

```
COMPANY: Global Betting Platform
BEFORE: PostgreSQL with read replicas
  • Replication lag: 2-10 seconds
  • Split-brain during failures
  • Manual failover: 30 minutes
  • Data loss: Several incidents/year

AFTER: CockroachDB
  • Replication lag: <5ms (synchronous)
  • Automatic consensus prevents split-brain
  • Automatic failover: <10 seconds
  • Data loss: ZERO in 3 years

"CockroachDB saved us $2M in prevented outages"
```

## 🔑 Key Lessons from Production

```
┌─────────────────────────────────────────────────────────────┐
│                  TRUTH DESIGN DECISIONS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ GOOGLE SPANNER:                                             │
│ Lesson: Hardware investment (GPS) enables new possibilities │
│ Trade-off: 7ms latency for perfect global consistency      │
│                                                             │
│ BITCOIN:                                                    │
│ Lesson: Economic incentives can replace trust              │
│ Trade-off: 10 min finality for permissionless consensus    │
│                                                             │
│ KAFKA:                                                      │
│ Lesson: Log-based truth enables massive scale              │
│ Trade-off: Storage cost for replayability                  │
│                                                             │
│ ZOOKEEPER:                                                  │
│ Lesson: Small, consistent core can coordinate large system │
│ Trade-off: Becomes bottleneck if overused                  │
│                                                             │
│ ETHEREUM:                                                   │
│ Lesson: Deterministic execution enables compute consensus   │
│ Trade-off: Every node runs every computation               │
│                                                             │
│ COCKROACHDB:                                                │
│ Lesson: SQL semantics possible in distributed systems      │
│ Trade-off: Complex routing and coordination                │
└─────────────────────────────────────────────────────────────┘
```


## Consensus Algorithm Implementations

### 1. Paxos Implementation

```mermaid
sequenceDiagram
    participant Proposer
    participant Acceptor1
    participant Acceptor2
    participant Acceptor3
    
    Note over Proposer: Phase 1: Prepare
    Proposer->>Acceptor1: Prepare(n)
    Proposer->>Acceptor2: Prepare(n)
    Proposer->>Acceptor3: Prepare(n)
    
    Acceptor1-->>Proposer: Promise(n, null)
    Acceptor2-->>Proposer: Promise(n, accepted_value)
    Note over Acceptor3: Already promised n+1
    Acceptor3-->>Proposer: Reject
    
    Note over Proposer: Majority reached (2/3)
    Note over Proposer: Use highest accepted value
    
    Note over Proposer: Phase 2: Accept
    Proposer->>Acceptor1: Accept(n, value)
    Proposer->>Acceptor2: Accept(n, value)
    Proposer->>Acceptor3: Accept(n, value)
    
    Acceptor1-->>Proposer: Accepted(n)
    Acceptor2-->>Proposer: Accepted(n)
    Acceptor3-->>Proposer: Reject
    
    Note over Proposer: Consensus reached!
```

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    state Proposer {
        Idle --> Preparing: propose(value)
        Preparing --> WaitingPromises: send prepare(n)
        WaitingPromises --> Accepting: majority promises
        WaitingPromises --> Failed: no majority
        Accepting --> WaitingAccepts: send accept(n,v)
        WaitingAccepts --> Success: majority accepts
        WaitingAccepts --> Failed: no majority
        Failed --> Idle: retry
        Success --> Idle: done
    }
    
    state Acceptor {
        Ready --> Promised: prepare(n) & n > promised
        Promised --> Accepted: accept(n,v) & n >= promised
        Accepted --> Promised: prepare(n') & n' > promised
    }
```

| Phase | Message | Acceptor Action | Required for Progress |
|-------|---------|-----------------|----------------------|
| 1a | Prepare(n) | Promise if n > highest promised | - |
| 1b | Promise(n, v) | Return any accepted value | Majority promises |
| 2a | Accept(n, v) | Accept if n >= promised | - |
| 2b | Accepted(n) | Confirm acceptance | Majority accepts |


### 2. Byzantine Fault Tolerant Consensus

```mermaid
sequenceDiagram
    participant Client
    participant Primary
    participant Replica1
    participant Replica2
    participant Replica3
    participant Byzantine
    
    Client->>Primary: Request(operation)
    
    Note over Primary: Phase 1: Pre-prepare
    Primary->>Replica1: PrePrepare(v,n,op)
    Primary->>Replica2: PrePrepare(v,n,op)
    Primary->>Replica3: PrePrepare(v,n,op)
    Primary->>Byzantine: PrePrepare(v,n,op)
    
    Note over Replica1,Byzantine: Phase 2: Prepare
    Replica1->>Primary: Prepare(v,n,digest)
    Replica1->>Replica2: Prepare(v,n,digest)
    Replica1->>Replica3: Prepare(v,n,digest)
    Replica1->>Byzantine: Prepare(v,n,digest)
    
    Replica2->>Primary: Prepare(v,n,digest)
    Replica2->>Replica1: Prepare(v,n,digest)
    Replica2->>Replica3: Prepare(v,n,digest)
    Replica2->>Byzantine: Prepare(v,n,digest)
    
    Replica3->>Primary: Prepare(v,n,digest)
    Replica3->>Replica1: Prepare(v,n,digest)
    Replica3->>Replica2: Prepare(v,n,digest)
    Replica3->>Byzantine: Prepare(v,n,digest)
    
    Note over Byzantine: Sends nothing or garbage
    
    Note over Primary,Replica3: 2f prepares collected
    
    Note over Primary,Byzantine: Phase 3: Commit
    Primary->>Replica1: Commit(v,n,digest)
    Primary->>Replica2: Commit(v,n,digest)
    Primary->>Replica3: Commit(v,n,digest)
    
    Replica1->>Client: Reply(result)
    Replica2->>Client: Reply(result)
    Replica3->>Client: Reply(result)
    
    Note over Client: Accept after f+1 matching replies
```

```mermaid
graph TB
    subgraph "PBFT Safety Requirements"
        N[N nodes total]
        F[f Byzantine nodes]
        REQ1[N ≥ 3f + 1]
        REQ2[2f + 1 for commit]
        REQ3[f + 1 matching replies]
        
        N --> REQ1
        F --> REQ1
        REQ1 --> REQ2
        REQ1 --> REQ3
        
        style REQ1 fill:#ffccbc,stroke:#d84315,stroke-width:3px
    end
    
    subgraph "Example: f=1"
        NODES[4 nodes total]
        BYZ[1 Byzantine max]
        PREP[Need 2 prepares]
        COMM[Need 3 commits]
        REPL[Need 2 replies]
        
        NODES --> PREP
        NODES --> COMM
        COMM --> REPL
        
        style NODES fill:#e8f5e9
    end
```

| Phase | Messages Required | Purpose | Byzantine Tolerance |
|-------|------------------|---------|--------------------|
| Pre-prepare | 1 (from primary) | Order assignment | Primary can be Byzantine |
| Prepare | 2f | Agreement on order | Tolerates f Byzantine |
| Commit | 2f + 1 | Agreement on execution | Ensures total order |
| Reply | f + 1 | Client confidence | At least 1 correct reply |


### 3. Blockchain Consensus Variants

```mermaid
graph TB
    subgraph "Proof of Stake Consensus"
        EPOCH[Epoch Start] --> RAND[RANDAO Reveal]
        RAND --> SELECT[Select Proposers]
        SELECT --> PROPOSE[Propose Blocks]
        PROPOSE --> ATTEST[Validators Attest]
        ATTEST --> FINALIZE[Finalize Checkpoints]
        
        style RAND fill:#fff3e0,stroke:#ff6f00,stroke-width:3px
        style FINALIZE fill:#c8e6c9
    end
    
    subgraph "Validator Lifecycle"
        DEPOSIT[32 ETH Deposit] --> PENDING[Pending]
        PENDING --> ACTIVE[Active Validator]
        ACTIVE --> EXIT[Voluntary Exit]
        ACTIVE --> SLASHED[Slashed]
        EXIT --> WITHDRAWN[Stake Withdrawn]
        SLASHED --> WITHDRAWN2[Partial Withdrawal]
        
        style DEPOSIT fill:#e3f2fd
        style ACTIVE fill:#c8e6c9
        style SLASHED fill:#ffcdd2
    end
```

```mermaid
sequenceDiagram
    participant Slot
    participant Proposer
    participant Committee1
    participant Committee2
    participant Network
    
    Note over Slot: Slot n begins (12 seconds)
    
    Slot->>Proposer: Selected via RANDAO
    Proposer->>Proposer: Create block
    Proposer->>Network: Broadcast block
    
    Network->>Committee1: Block received
    Network->>Committee2: Block received
    
    Committee1->>Committee1: Validate block
    Committee2->>Committee2: Validate block
    
    Committee1->>Network: Attestation
    Committee2->>Network: Attestation
    
    Note over Network: Aggregate attestations
    
    alt Supermajority (>2/3)
        Note over Network: Block accepted
    else
        Note over Network: Block rejected
    end
```

| Slashing Condition | Penalty | Description | Protection |
|-------------------|---------|-------------|------------|
| Double Voting | 1-5% of stake | Voting for two blocks at same height | Store last vote |
| Surround Voting | 1-3% of stake | Conflicting attestations | Track vote history |
| Inactivity Leak | Gradual | Offline during finality crisis | Stay online |
| Proposer Equivocation | 2-5% of stake | Proposing multiple blocks | One block per slot |


## Truth Maintenance Systems

### 1. Distributed Version Vectors

```mermaid
graph LR
    subgraph "Version Vector Evolution"
        VV1["A:1, B:0"] -->|Node A writes| VV2["A:2, B:0"]
        VV1 -->|Node B writes| VV3["A:1, B:1"]
        VV2 -->|Merge| VV4["A:2, B:1"]
        VV3 -->|Merge| VV4
        
        style VV1 fill:#e3f2fd
        style VV2 fill:#bbdefb
        style VV3 fill:#bbdefb
        style VV4 fill:#64b5f6
    end
```

```mermaid
sequenceDiagram
    participant Client
    participant NodeA
    participant NodeB
    participant NodeC
    
    Note over NodeA,NodeC: Initial state: value=X, VV={}
    
    Client->>NodeA: Write(Y)
    NodeA->>NodeA: value=Y, VV={A:1}
    
    Client->>NodeB: Write(Z)
    NodeB->>NodeB: value=Z, VV={B:1}
    
    Note over NodeA,NodeB: Concurrent writes!
    
    NodeA->>NodeC: Replicate(Y, {A:1})
    NodeB->>NodeC: Replicate(Z, {B:1})
    
    Note over NodeC: Detects concurrent values
    NodeC->>NodeC: values=[Y,Z], VV={A:1,B:1}
    
    Client->>NodeC: Read()
    NodeC-->>Client: Concurrent: [Y,Z]
    
    Client->>NodeC: Write(W, context={A:1,B:1})
    NodeC->>NodeC: value=W, VV={A:1,B:1,C:1}
    Note over NodeC: Resolves conflict
```

```mermaid
graph TB
    subgraph "Version Vector Relationships"
        subgraph "Ordering"
            DF[Descends From]
            CONC[Concurrent]
            EQ[Equal]
        end
        
        subgraph "Examples"
            EX1["{A:2,B:1} > {A:1,B:1}"]
            EX2["{A:2,B:1} || {A:1,B:2}"]
            EX3["{A:2,B:2} = {A:2,B:2}"]
            
            EX1 --> DF
            EX2 --> CONC
            EX3 --> EQ
        end
        
        style DF fill:#c8e6c9
        style CONC fill:#fff9c4
        style EQ fill:#e1bee7
    end
```

| Scenario | Vector State | Relationship | Action Required |
|----------|--------------|--------------|----------------|
| Sequential Updates | {A:2} → {A:3} | Descends from | Replace old value |
| Concurrent Updates | {A:2,B:1} vs {A:1,B:2} | Concurrent | Keep both values |
| Synchronized | {A:2,B:2} = {A:2,B:2} | Equal | Same value |
| Partial Knowledge | {A:2} vs {A:2,B:1} | Ancestor | Update to newer |


## Key Takeaways

1. **Truth is expensive** - Consensus requires multiple round trips

2. **Different truths for different needs** - Strong, eventual, causal consistency

3. **Time is fundamental** - Can't order events without time

4. **Byzantine failures change everything** - 3f+1 nodes needed for f failures

5. **Probabilistic consensus can be enough** - Bitcoin proves it

Remember: Perfect truth is impossible in distributed systems. Choose the level of truth your application actually needs.