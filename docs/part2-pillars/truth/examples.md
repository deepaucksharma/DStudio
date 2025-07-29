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

## ⚡ The One-Inch Punch

<div class="axiom-box">
<h3>💥 Truth Paradox</h3>
<p><strong>"The more nodes agree on truth, / the less true / it needs to be."</strong></p>
<p>That's why Bitcoin works: agreement matters more than accuracy.</p>
</div>

<div class="truth-box">
<h2>⚡ The Reality Check</h2>
<p><strong>These aren't theoretical examples—they're production war stories.</strong></p>
<p>Each case study represents millions of dollars saved (or lost) based on truth design choices.</p>
</div>

## 🧭 Your 10-Second Understanding

```
LOCAL TRUTH (1 node)              DISTRIBUTED TRUTH (1000 nodes)
═══════════════════               ═════════════════════════════

┌────────┐                        ┌────┐ ┌────┐ ┌────┐ ┌────┐
│DATABASE│                        │NODE│ │NODE│ │NODE│ │NODE│
│        │                        └──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘
│TRUTH=42│                           │      │      │      │
└────────┘                           └──────┴──────┴──────┘
                                            CONSENSUS
                                          
Easy: Just read it               Hard: Must agree first
Fast: Nanoseconds               Slow: Milliseconds to minutes
Simple: It's right there        Complex: Byzantine generals
```

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


## 🧮 Consensus Patterns in Practice

### Paxos: The Original (Complex) Truth

```
┌─────────────────────────────────────────────────────────────┐
│                   PAXOS IN PRACTICE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ WHY PAXOS IS HARD TO UNDERSTAND:                           │
│                                                             │
│ PHASE 1: PREPARE                  PHASE 2: ACCEPT          │
│ Proposer──┐                       Proposer──┐              │
│     │     │                            │     │              │
│     ▼     ▼                            ▼     ▼              │
│ Prepare(n=42)                     Accept(n=42,v=X)         │
│     │                                  │                    │
│ ┌───┴───┬────┬────┐              ┌───┴───┬────┬────┐     │
│ ▼       ▼    ▼    ▼              ▼       ▼    ▼    ▼     │
│ A1      A2   A3   A4             A1      A2   A3   A4     │
│ │       │    │    X              │       │    │    X      │
│ Promise Promise  (fail)          Accept Accept   (fail)    │
│ (n=42)  (n=42,                   (n=42) (n=42)            │
│         v=OLD)                                             │
│                                                             │
│ MAJORITY = 3/4 needed                                       │
│                                                             │
│ THE COMPLEXITY:                                             │
│ • Must track highest proposal number seen                  │
│ • Must remember accepted values                            │
│ • Two phases for one decision                              │
│ • Liveness not guaranteed (dueling proposers)              │
└─────────────────────────────────────────────────────────────┘
```

### Byzantine Consensus: When Nodes Lie

```
┌─────────────────────────────────────────────────────────────┐
│              PBFT: PRACTICAL BYZANTINE FT                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ THE 3-PHASE DANCE (with 1 Byzantine node):                 │
│                                                             │
│ PRE-PREPARE          PREPARE              COMMIT           │
│ Primary──┐           All──┐               All──┐           │
│     │    │              │  │                 │  │           │
│     ▼    ▼              ▼  ▼                 ▼  ▼           │
│ "Do X at #5"        "I saw X@5"         "Let's do X@5"     │
│     │                   │                    │              │
│ ┌───┴────┬───┬───┐ ┌───┴────┬───┬───┐ ┌───┴────┬───┬───┐ │
│ ▼        ▼   ▼   ▼ ▼        ▼   ▼   ▼ ▼        ▼   ▼   ▼ │
│ R1       R2  R3  B R1       R2  R3  B  R1       R2  R3  B │
│ ✓        ✓   ✓   ? ✓        ✓   ✓   ❌ ✓        ✓   ✓   ❌ │
│                                                             │
│ Need 2f+1 = 3 prepares, 2f+1 = 3 commits                  │
│                                                             │
│ CLIENT SEES: 3 identical responses = TRUTH                 │
└─────────────────────────────────────────────────────────────┘
```

### Blockchain Evolution: From PoW to PoS

```
┌─────────────────────────────────────────────────────────────┐
│              CONSENSUS EVOLUTION AT SCALE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ PROOF OF WORK (Bitcoin/Old Ethereum):                      │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│ │ MINER 1 │  │ MINER 2 │  │ MINER 3 │                     │
│ │CPU: 100%│  │CPU: 100%│  │CPU: 100%│                     │
│ │Power:2MW│  │Power:2MW│  │Power:2MW│                     │
│ └────┬────┘  └────┬────┘  └────┬────┘                     │
│      │            │            │                            │
│      └────────────┴────────────┘                           │
│                   │                                         │
│            FIND NONCE < TARGET                              │
│                   │                                         │
│            Winner takes all!                                │
│                                                             │
│ PROOF OF STAKE (Ethereum 2.0):                             │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│ │VALIDATOR│  │VALIDATOR│  │VALIDATOR│                     │
│ │32 ETH   │  │32 ETH   │  │32 ETH   │                     │
│ │CPU: 5%  │  │CPU: 5%  │  │CPU: 5%  │                     │
│ └────┬────┘  └────┬────┘  └────┬────┘                     │
│      │            │            │                            │
│      └────────────┴────────────┘                           │
│                   │                                         │
│          SELECTED BY RANDAO                                 │
│                   │                                         │
│         Propose & Attest blocks                             │
│                                                             │
│ ENERGY SAVINGS: 99.95% 🌱                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔬 Truth Verification in Production

### Merkle Trees: Proving Truth Efficiently

```
┌─────────────────────────────────────────────────────────────┐
│                MERKLE TREE VERIFICATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     ROOT HASH                               │
│                    H(H12 + H34)                            │
│                         │                                   │
│            ┌────────────┴────────────┐                     │
│            │                         │                      │
│          H12                       H34                      │
│        H(H1+H2)                 H(H3+H4)                   │
│            │                         │                      │
│      ┌─────┴─────┐            ┌─────┴─────┐               │
│      │           │            │           │                │
│     H1          H2           H3          H4                │
│   H(TX1)      H(TX2)       H(TX3)      H(TX4)             │
│      │           │            │           │                │
│    TX1         TX2          TX3         TX4                │
│                                                             │
│ TO PROVE TX2 IS IN BLOCK:                                  │
│ Send: TX2, H1, H34 → Verify: H(H(H1+H(TX2))+H34) = ROOT  │
│                                                             │
│ PROOF SIZE: O(log n) instead of O(n)! 🎯                   │
└─────────────────────────────────────────────────────────────┘
```

### Version Vectors: Tracking Concurrent Truth

```
┌─────────────────────────────────────────────────────────────┐
│           VERSION VECTORS IN DYNAMO/RIAK                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ SCENARIO: Shopping cart concurrent updates                  │
│                                                             │
│ Time  Node A         Node B         Node C                 │
│ ────  ─────────      ─────────      ─────────              │
│ T1    Cart: [Book]   Cart: []       Cart: []              │
│       VV: {A:1}      VV: {}         VV: {}                │
│                                                             │
│ T2    Cart: [Book]   Cart: [Pen]    Cart: []              │
│       VV: {A:1}      VV: {B:1}      VV: {}                │
│                                                             │
│ T3    Sync from B    ─────────►     Cart: [Pen]           │
│                                     VV: {B:1}              │
│                                                             │
│ T4    Sync to C      ─────────►     CONFLICT!             │
│                                     Cart: [[Book],[Pen]]   │
│                                     VV: {A:1,B:1}         │
│                                                             │
│ T5    Client resolves conflict:     Cart: [Book,Pen]      │
│                                     VV: {A:1,B:1,C:1}     │
│                                                             │
│ KEY: Version vectors detect concurrent updates!            │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Truth Patterns Summary

```
┌─────────────────────────────────────────────────────────────┐
│                 WHEN TO USE EACH PATTERN                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ PATTERN          USE WHEN              AVOID WHEN           │
│ ═══════════════════════════════════════════════════════════ │
│ RAFT            • Need understandable  • Byzantine nodes    │
│                 • Leader-based OK      • Global scale       │
│                                                             │
│ PAXOS           • Need proven theory   • Team learning      │
│                 • Complex is OK        • Quick prototype    │
│                                                             │
│ PBFT            • Byzantine possible   • > 20 nodes         │
│                 • Fixed node set       • High throughput    │
│                                                             │
│ BLOCKCHAIN      • No trust             • Low latency        │
│                 • Audit critical       • Private network    │
│                                                             │
│ CRDT            • Conflict-free        • Strong consistency │
│                 • Partition tolerant   • Complex invariants │
│                                                             │
│ VECTOR CLOCKS   • Track causality      • > 10 nodes         │
│                 • Detect concurrency   • Space constrained  │
│                                                             │
│ 2PC             • ACID required        • Partition likely   │
│                 • Short transactions   • Node failures      │
└─────────────────────────────────────────────────────────────┘
```

## 💡 The Master Insight

```
┌─────────────────────────────────────────────────────────────┐
│                    THE TRUTH PARADOX                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   "The more nodes agree on truth,                          │
│    the less true it needs to be."                          │
│                                                             │
│   LOCAL TRUTH:  100% accurate, 1 node                      │
│   EVENTUAL:     ~99% accurate, 100 nodes                   │
│   CONSENSUS:    95% accurate, 1000 nodes                   │
│   BLOCKCHAIN:   90% accurate*, 10000 nodes                 │
│                                                             │
│   * "Accurate" = matches physical reality                   │
│                                                             │
│   THE LESSON:                                               │
│   Distributed truth is about agreement, not accuracy.      │
│   Choose the right level of "wrongness" for your scale.    │
└─────────────────────────────────────────────────────────────┘
```

---

**Next**: [Back to Truth Overview](index) | [Try the Exercises →](exercises)

*"In production, truth is what the majority believes—until the partition heals."*