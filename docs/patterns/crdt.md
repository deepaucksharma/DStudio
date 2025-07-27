---
title: CRDT (Conflict-free Replicated Data Types)
description: Data structures that automatically resolve conflicts in distributed systems
type: pattern
category: distributed-data
difficulty: advanced
reading_time: 40 min
prerequisites: [eventual-consistency, vector-clocks]
when_to_use: When you need automatic conflict resolution without coordination
when_not_to_use: When strong consistency is required or simpler solutions suffice
status: complete
last_updated: 2025-01-23
excellence_tier: gold
pattern_status: recommended
introduced: 2011-01
current_relevance: mainstream
modern_examples:
  - company: Figma
    implementation: "CRDTs power real-time collaborative design editing"
    scale: "Millions of concurrent design sessions"
  - company: Riak
    implementation: "Built-in CRDT support for distributed data"
    scale: "Petabyte-scale deployments with automatic conflict resolution"
  - company: Redis
    implementation: "Redis CRDT for geo-distributed active-active databases"
    scale: "Sub-millisecond replication across continents"
production_checklist:
  - "Choose appropriate CRDT type for your use case"
  - "Implement garbage collection for tombstones"
  - "Monitor memory growth from metadata"
  - "Plan for causal delivery of operations"
  - "Test convergence under network partitions"
  - "Implement state compression techniques"
  - "Configure anti-entropy protocols"
  - "Document merge semantics for developers"
  - "Monitor divergence metrics between replicas"
  - "Plan for CRDT type migrations"
---

# CRDT (Conflict-free Replicated Data Types)

!!! success "🏆 Gold Standard Pattern"
    **Automatic Conflict Resolution** • Figma, Riak, Redis proven
    
    The breakthrough pattern for conflict-free collaboration. CRDTs enable real-time collaborative applications and geo-distributed databases by mathematically guaranteeing convergence without coordination.
    
    **Key Success Metrics:**
    - Figma: Powers real-time design collaboration for millions
    - Riak: Petabyte-scale with automatic conflict resolution
    - Redis CRDT: Active-active replication across continents

**Automatic conflict resolution for distributed data**

!!! abstract "The CRDT Convergence Theorem"
 <p>CRDTs guarantee that all replicas will eventually converge to the same state without requiring coordination, as long as all updates are eventually delivered to all replicas. This property, called Strong Eventual Consistency (SEC), is stronger than regular eventual consistency.</p>

## CRDT Properties at a Glance

| Property | Guarantee | Benefit |
|----------|-----------|----------|
| **Convergence** | All replicas reach same state | No divergence |
| **Coordination-free** | No consensus/locking | High availability |
| **Always writable** | Accept updates anytime | No blocking |
| **Partition tolerant** | Works during splits | Network resilience |
| **Auto conflict resolution** | Mathematical merge | No manual intervention |

## Visual CRDT Type Hierarchy

```mermaid
graph TB
 CRDT[CRDT<br/>Conflict-free Replicated Data Type]
 
 CRDT --> StateBased[State-based<br/>CvRDT]
 CRDT --> OpBased[Operation-based<br/>CmRDT]
 CRDT --> DeltaBased[Delta-based<br/>δ-CRDT]
 
 StateBased --> GCounter[G-Counter<br/>Grow-only Counter]
 StateBased --> PNCounter[PN-Counter<br/>Positive-Negative Counter]
 StateBased --> GSet[G-Set<br/>Grow-only Set]
 StateBased --> TwoPSet[2P-Set<br/>Two-Phase Set]
 StateBased --> LWWReg[LWW-Register<br/>Last-Write-Wins]
 StateBased --> MVReg[MV-Register<br/>Multi-Value]
 
 OpBased --> ORSet[OR-Set<br/>Observed-Remove Set]
 OpBased --> RGA[RGA<br/>Replicated Growing Array]
 OpBased --> Treedoc[Treedoc<br/>Tree-based Sequence]
 
 DeltaBased --> DeltaCounter[Delta Counter]
 DeltaBased --> DeltaMap[Delta Map]
 
 style CRDT fill:#e8f5e9
 style StateBased fill:#e3f2fd
 style OpBased fill:#fff3e0
 style DeltaBased fill:#fce4ec
```

## CRDT Types and Convergence

### State-based CRDTs (CvRDT)

### State vs Operation vs Delta CRDTs

| Type | Mechanism | Network Cost | Delivery Requirement |
|------|-----------|--------------|---------------------|
| **State-based (CvRDT)** | Send full state | O(state size) | Idempotent |
| **Operation-based (CmRDT)** | Send operations | O(op size) | Exactly-once, causal |
| **Delta-based (δ-CRDT)** | Send state changes | O(delta size) | Idempotent |

#### Join Semilattice Structure

```mermaid
graph BT
 Empty["{}"]
 A["{A}"]
 B["{B}"]
 C["{C}"]
 AB["{A,B}"]
 AC["{A,C}"]
 BC["{B,C}"]
 ABC["{A,B,C}"]
 
 Empty --> A
 Empty --> B
 Empty --> C
 A --> AB
 A --> AC
 B --> AB
 B --> BC
 C --> AC
 C --> BC
 AB --> ABC
 AC --> ABC
 BC --> ABC
 
 style ABC fill:#4caf50,color:#fff
 style Empty fill:#f44336,color:#fff
```

### Operation-based CRDTs (CmRDT)

#### How Operation-based CRDTs Work

```mermaid
sequenceDiagram
 participant R1 as Replica 1
 participant R2 as Replica 2
 participant R3 as Replica 3
 participant Network as Network Layer
 
 Note over R1,R3: Initial: All replicas empty
 
 R1->>Network: op: add("X", timestamp1)
 R2->>Network: op: add("Y", timestamp2)
 
 Network->>R1: deliver: add("Y", timestamp2)
 Network->>R2: deliver: add("X", timestamp1)
 Network->>R3: deliver: add("X", timestamp1)
 Network->>R3: deliver: add("Y", timestamp2)
 
 Note over R1,R3: All operations commute
 Note over R1,R3: Final state: {X, Y} at all replicas
```

## Detailed CRDT Type Implementations

### 1. G-Counter (Grow-only Counter)

#### Visual Representation

```mermaid
graph LR
 subgraph "Replica A"
 A1["A: 5<br/>B: 0<br/>C: 0<br/>Total: 5"]
 end
 
 subgraph "Replica B"
 B1["A: 0<br/>B: 3<br/>C: 0<br/>Total: 3"]
 end
 
 subgraph "Replica C"
 C1["A: 0<br/>B: 0<br/>C: 2<br/>Total: 2"]
 end
 
 subgraph "After Merge"
 M["A: 5<br/>B: 3<br/>C: 2<br/>Total: 10"]
 end
 
 A1 --> M
 B1 --> M
 C1 --> M
 
 style M fill:#4caf50,color:#fff
```

### G-Counter Implementation Pattern

```mermaid
graph LR
    subgraph "Node State"
        A["Node A: {A:5, B:0, C:0}"]
        B["Node B: {A:0, B:3, C:0}"]
        C["Node C: {A:0, B:0, C:2}"]
    end
    
    subgraph "Merge Operation"
        M["merge(a,b) = max(a[i], b[i])"]
    end
    
    subgraph "Result"
        R["All Nodes: {A:5, B:3, C:2}<br/>Total: 10"]
    end
    
    A --> M
    B --> M
    C --> M
    M --> R
    
    style R fill:#4caf50,color:#fff
```

**Key insight**: Each node tracks all node counts; merge takes maximum per node.

### 2. PN-Counter (Positive-Negative Counter)

#### Visual Representation

```mermaid
graph TB
 subgraph "PN-Counter Structure"
 PNC[PN-Counter]
 PNC --> P[P: Positive Counter<br/>G-Counter]
 PNC --> N[N: Negative Counter<br/>G-Counter]
 
 Value["Value = P.value() - N.value()"]
 end
 
 subgraph "Operations"
 Inc[increment()] --> P
 Dec[decrement()] --> N
 end
 
 P --> Value
 N --> Value
```

### PN-Counter = Two G-Counters

| Component | Purpose | Operation |
|-----------|---------|----------|  
| **P-Counter** | Track increments | `increment()` → P.add |
| **N-Counter** | Track decrements | `decrement()` → N.add |
| **Value** | Current count | P.value() - N.value() |
| **Merge** | Combine states | P.merge(), N.merge() |

### 3. OR-Set (Observed-Remove Set)

#### Convergence Visualization

```mermaid
sequenceDiagram
 participant R1 as Replica 1
 participant R2 as Replica 2
 
 Note over R1,R2: Both start with {A}
 
 R1->>R1: add(B, uid1)
 R2->>R2: remove(A)
 
 Note over R1: {A, B}
 Note over R2: {}
 
 R1->>R2: sync: add(B, uid1)
 R2->>R1: sync: remove(A)
 
 Note over R1,R2: After sync: {B}
 Note over R1,R2: Add wins over concurrent remove
```

### OR-Set Mechanics

```mermaid
flowchart LR
    subgraph "Add Operation"
        A1["add('X')"] --> A2["Store ('X', UUID1)"]
    end
    
    subgraph "Remove Operation"
        R1["remove('X')"] --> R2["Find all ('X', *)"]
        R2 --> R3["Move to tombstones"]
    end
    
    subgraph "Merge Resolution"
        M1["Elements ∪ Elements"] --> M2["Subtract Tombstones"]
        M2 --> M3["Final Set"]
    end
    
    style A2 fill:#4caf50
    style R3 fill:#f44336
    style M3 fill:#2196f3
```

**Key**: Unique IDs allow concurrent add/remove of same element without conflicts.

### 4. LWW-Register (Last-Write-Wins Register)

#### Conflict Resolution Visualization

```mermaid
graph LR
 subgraph "Time-based Resolution"
 W1["Write 'A'<br/>Time: 100"] 
 W2["Write 'B'<br/>Time: 150"]
 W3["Write 'C'<br/>Time: 120"]
 
 Result["Final Value: 'B'<br/>(highest timestamp)"]
 
 W1 --> Result
 W2 --> Result
 W3 --> Result
 end
 
 style W2 fill:#4caf50
 style Result fill:#4caf50,color:#fff
```

### LWW-Register Conflict Resolution

| Scenario | Resolution Rule | Example |
|----------|----------------|----------|
| **Different timestamps** | Higher timestamp wins | T2 > T1 → use T2 value |
| **Same timestamp** | Node ID breaks tie | T1 = T2 → compare node IDs |
| **Clock skew** | Still deterministic | Works despite time drift |

```mermaid
graph LR
    W1["Write A @ T=100"] --> C{Compare}
    W2["Write B @ T=150"] --> C
    W3["Write C @ T=120"] --> C
    C --> R["Result: B<br/>(highest timestamp)"]
    style R fill:#4caf50,color:#fff
```

### 5. MV-Register (Multi-Value Register)

#### Concurrent Value Handling

```mermaid
graph TB
 subgraph "Concurrent Writes"
 R1["Replica 1<br/>writes 'A'"]
 R2["Replica 2<br/>writes 'B'"]
 end
 
 subgraph "MV-Register State"
 MV["Values: {'A', 'B'}<br/>Concurrent values preserved"]
 end
 
 subgraph "Resolution"
 App["Application chooses:<br/>- Show both<br/>- User picks<br/>- Domain logic"]
 end
 
 R1 --> MV
 R2 --> MV
 MV --> App
```

## CRDT Comparison Table

| CRDT Type | Operations | Use Case | Memory Overhead | Convergence Speed |
|-----------|------------|----------|-----------------|------------------|
| **G-Counter** | increment only | Page views, likes | Low (O(nodes)) | Fast |
| **PN-Counter** | increment, decrement | Account balances | Medium (2×G-Counter) | Fast |
| **G-Set** | add only | Append-only logs | Grows unbounded | Fast |
| **2P-Set** | add, remove once | Tombstoned items | Grows unbounded | Fast |
| **OR-Set** | add, remove | Shopping carts | High (unique IDs) | Fast |
| **LWW-Register** | set | Last value wins | Low | Fast |
| **MV-Register** | set | Preserve conflicts | Medium | Fast |
| **RGA** | insert, delete | Text editing | High | Medium |


## Network Partition Scenarios

### Partition Tolerance Visualization

```mermaid
graph TB
 subgraph "Before Partition"
 N1A[Node 1] <--> N2A[Node 2]
 N2A <--> N3A[Node 3]
 N1A <--> N3A
 end
 
 subgraph "During Partition"
 subgraph "Partition A"
 N1B[Node 1]
 N2B[Node 2]
 N1B <--> N2B
 end
 
 subgraph "Partition B"
 N3B[Node 3]
 end
 
 N1B -.X.- N3B
 N2B -.X.- N3B
 end
 
 subgraph "After Healing"
 N1C[Node 1] <--> N2C[Node 2]
 N2C <--> N3C[Node 3]
 N1C <--> N3C
 Note["CRDTs automatically converge<br/>No conflicts or data loss"]
 end
```

### Handling Network Partitions

```python
class PartitionTolerantCounter:
 """Example showing CRDT behavior during partition"""
 
 def simulate_partition():
# Three nodes start synchronized
 node1 = GCounter("node1")
 node2 = GCounter("node2")
 node3 = GCounter("node3")
 
# Initial increments
 node1.increment(10)
 
# Sync before partition
 node2 = node2.merge(node1)
 node3 = node3.merge(node1)
 
 print("Before partition:", node1.value())
 
# PARTITION OCCURS
# Nodes 1,2 can communicate
# Node 3 is isolated
 
# Operations during partition
 node1.increment(5) # Only seen by node1,2
 node2.increment(3) # Only seen by node1,2
 node3.increment(7) # Only seen by node3
 
# Partial sync (1 and 2 only)
 node1 = node1.merge(node2)
 node2 = node2.merge(node1)
 
 print("During partition:")
 print(f"Nodes 1,2: {node1.value()}")
 print(f"Node 3: {node3.value()}")
 
# PARTITION HEALS
# Full sync
 merged = node1.merge(node3)
 node1 = node2 = node3 = merged
 
 print(f"After healing: {merged.value()}")
 print("All nodes converged!")
```

## Mathematical Properties

### Convergence Properties Visualized

```mermaid
graph LR
 subgraph "Commutativity"
 C1["A ⊕ B = B ⊕ A"]
 end
 
 subgraph "Associativity"
 A1["(A ⊕ B) ⊕ C = A ⊕ (B ⊕ C)"]
 end
 
 subgraph "Idempotence"
 I1["A ⊕ A = A"]
 end
 
 subgraph "Result"
 R["Strong Eventual Consistency"]
 end
 
 C1 --> R
 A1 --> R
 I1 --> R
 
 style R fill:#4caf50,color:#fff
```

### Join Semilattice Requirements

| Property | Definition | Example (Set Union) |
|----------|------------|--------------------|
| **Commutativity** | `a ⊔ b = b ⊔ a` | `{1,2} ∪ {3} = {3} ∪ {1,2}` |
| **Associativity** | `(a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)` | `({1} ∪ {2}) ∪ {3} = {1} ∪ ({2} ∪ {3})` |
| **Idempotence** | `a ⊔ a = a` | `{1,2} ∪ {1,2} = {1,2}` |


## Real-World Applications

### 1. Collaborative Text Editing

#### RGA (Replicated Growing Array) Structure

```mermaid
graph LR
 subgraph "Document Structure"
 Start["◆"] --> H["H<br/>id:1.1"]
 H --> E["e<br/>id:1.2"]
 E --> L1["l<br/>id:1.3"]
 L1 --> L2["l<br/>id:1.4"]
 L2 --> O["o<br/>id:1.5"]
 O --> End["◆"]
 end
 
 subgraph "Concurrent Insert"
 User1["User 1: insert 'i' after 'H'"]
 User2["User 2: insert 'a' after 'H'"]
 
 Result["'H' → 'a' → 'i' → 'e' → 'l' → 'l' → 'o'<br/>(deterministic ordering by ID)"]
 end
 
 User1 --> Result
 User2 --> Result
```

### Real-World CRDT Applications

| Use Case | CRDT Type | Companies | Scale |
|----------|-----------|-----------|-------|
| **Collaborative Editing** | RGA/Treedoc | Figma, Google Docs | Millions concurrent |
| **Shopping Cart** | OR-Set + PN-Counter | Amazon, Riak | Global scale |
| **User Presence** | LWW-Register | Discord, Slack | Real-time updates |
| **Like Counters** | G-Counter | Twitter, Facebook | Billions/day |
| **Distributed Cache** | LWW-Map | Redis CRDT | Multi-region |
| **Session Storage** | OR-Set | Cloudflare | Edge computing |

### CRDT Design Patterns

| Pattern | Composition | Use Case |
|---------|-------------|----------|  
| **Composed CRDT** | Multiple basic CRDTs | Shopping cart (OR-Set + PN-Counter) |
| **Embedded CRDT** | CRDT inside CRDT | Map of Counters |
| **Causal CRDT** | Add happens-before | Message ordering |
| **Pure Op-Based** | No state transfer | Low bandwidth |
| **Delta-State** | Incremental sync | Large datasets |
| **Merkle-CRDT** | Efficient sync | Minimize transfers |

## Performance Characteristics

### CRDT Performance Profile

| CRDT Type | Space | Update | Merge | Query | Garbage Collection |
|-----------|-------|--------|-------|-------|-------------------|
| **G-Counter** | O(n) nodes | O(1) | O(n) | O(n) | Not needed |
| **PN-Counter** | O(n) nodes | O(1) | O(n) | O(n) | Not needed |
| **OR-Set** | O(m×u) elem×ids | O(1) | O(m) | O(1) | Critical (tombstones) |
| **LWW-Register** | O(1) | O(1) | O(1) | O(1) | Not needed |
| **RGA** | O(m) positions | O(m) | O(m) | O(1) | Optional |


### Bandwidth Usage Patterns

```mermaid
graph LR
 subgraph "State-based CRDTs"
 S1["Full State<br/>O(state size)"]
 S2["Anti-entropy<br/>Periodic sync"]
 end
 
 subgraph "Operation-based CRDTs"
 O1["Operations only<br/>O(op size)"]
 O2["Causal delivery<br/>required"]
 end
 
 subgraph "Delta-based CRDTs"
 D1["State deltas<br/>O(changes)"]
 D2["Best of both<br/>worlds"]
 end
 
 style D1 fill:#4caf50
 style D2 fill:#4caf50
```

## Implementation Best Practices

### 1. Choosing the Right CRDT

```mermaid
graph TD
 Start[Choose CRDT Type]
 
 Start --> DataType{What data type?}
 
 DataType -->|Counter| CounterCheck{Need decrement?}
 CounterCheck -->|No| GCounter[G-Counter]
 CounterCheck -->|Yes| PNCounter[PN-Counter]
 
 DataType -->|Set| SetCheck{Need remove?}
 SetCheck -->|No| GSet[G-Set]
 SetCheck -->|Yes, once| TwoPSet[2P-Set]
 SetCheck -->|Yes, multiple| ORSet[OR-Set]
 
 DataType -->|Register| RegCheck{Conflict resolution?}
 RegCheck -->|Last write wins| LWWReg[LWW-Register]
 RegCheck -->|Keep all values| MVReg[MV-Register]
 
 DataType -->|Sequence| SeqCheck{Complexity tolerance?}
 SeqCheck -->|High| RGA[RGA/Treedoc]
 SeqCheck -->|Low| Transform[Operational Transform]
```

### Garbage Collection Strategies

| Strategy | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| **Timeout-based** | Remove after TTL | Simple | Unsafe if delayed |
| **Version Vector** | Track causal history | Safe | Memory overhead |
| **Consensus GC** | Agree on cutoff | Very safe | Coordination required |
| **Hybrid** | Local + periodic consensus | Balanced | Complex |
| **Bloom Filter** | Probabilistic tracking | Space efficient | False positives |

### Optimization Techniques

| Technique | Purpose | Trade-off |
|-----------|---------|-----------|  
| **Batching** | Reduce sync frequency | Latency vs efficiency |
| **Compression** | Reduce state size | CPU vs bandwidth |
| **Hierarchical** | Local + global CRDTs | Complexity vs scale |
| **Lazy propagation** | Delay non-critical updates | Consistency lag |
| **State pruning** | Remove old history | Safety vs space |
| **Delta compression** | Send only changes | Requires reliable delivery |

## Trade-offs and Limitations

### CRDT vs Other Consistency Models

| Aspect | CRDTs | Consensus (Raft/Paxos) | Last-Write-Wins | Vector Clocks |
|--------|-------|------------------------|-----------------|---------------|
| **Availability** | Always available | Requires majority | Always available | Always available |
| **Partition Tolerance** | Full tolerance | Majority partition | Full tolerance | Full tolerance |
| **Consistency** | Eventual (SEC) | Strong | Eventual | Causal |
| **Conflict Resolution** | Automatic | N/A (prevents conflicts) | Data loss possible | Manual required |
| **Latency** | Low (local ops) | High (coordination) | Low | Low |
| **Complexity** | Medium | High | Low | Medium |
| **Memory Overhead** | Can be high | Low | Low | Medium |


### CRDT Limitations Matrix

| Limitation | Why | Alternative |
|------------|-----|-------------|
| **No strong consistency** | Eventually consistent only | Use consensus (Raft/Paxos) |
| **No global invariants** | Can't enforce constraints | Use transactions |
| **Memory growth** | Metadata accumulates | Implement GC carefully |
| **Complex to reason about** | Non-intuitive behavior | Extensive testing needed |
| **Limited operations** | Not all ops have CRDT | Design around available types |
| **Network overhead** | State/metadata transfer | Use delta-CRDTs |

## Related Patterns

- [Eventual Consistency](eventual-consistency.md) - The consistency model CRDTs provide
- [Vector Clocks](vector-clocks.md) - Used in some CRDT implementations
- Gossip Protocol (Coming Soon) - Common dissemination method
- Anti-Entropy (Coming Soon) - Synchronization mechanism

## References

1. "Conflict-free Replicated Data Types" - Shapiro et al.
2. "A Comprehensive Study of CRDTs" - Shapiro, Preguiça, Baquero, Zawirski
3. "Delta State Replicated Data Types" - Almeida, Shoker, Baquero
4. "Efficient State-based CRDTs by Delta-Mutation" - Riak implementation

---

*Next: [Vector Clocks](vector-clocks.md) - Understanding causality in distributed systems*