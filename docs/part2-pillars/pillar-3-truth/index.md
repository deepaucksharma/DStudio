# Pillar III: Distribution of Truth

!!! info "Prerequisites"
    - [Pillar 2: Distribution of State](../pillar-2-state/index.md)
    - Understanding of [Axiom 5: Coordination](../../part1-axioms/axiom-5-coordination/index.md)
    - Basic distributed systems concepts

!!! tip "Quick Navigation"
    [← Pillar 2](../pillar-2-state/index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Distribution of Control](../pillar-4-control/index.md)

!!! target "Learning Objective"
    In distributed systems, truth is negotiated, not declared.

## Core Concept

<div class="axiom-box">

**The Fundamental Question**:

```
"What's the current state?" seems simple until:
- Nodes have different views
- Messages arrive out of order  
- Clocks aren't synchronized
- Failures are partial
- Network partitions happen
```

Truth in distributed systems isn't absolute—it's a consensus among participants.

</div>

## Consensus Algorithms Landscape

<div class="algorithm-tree">

```
2-Phase Commit (2PC)
├─ Blocking protocol
├─ Coordinator bottleneck
└─ Used in: Traditional databases

3-Phase Commit (3PC)  
├─ Non-blocking (in theory)
├─ Extra round trip
└─ Used in: Almost nowhere (too complex)

Paxos
├─ Proven correct
├─ Hard to understand
└─ Used in: Chubby, Spanner

Raft
├─ Understandable
├─ Leader-based
└─ Used in: etcd, Consul

Byzantine (PBFT, BFT)
├─ Tolerates malicious nodes
├─ O(n²) messages
└─ Used in: Blockchain
```

</div>

## Quorum Mathematics

<div class="formula-box">

```
For N replicas:
Write quorum (W) + Read quorum (R) > N

Examples:
N=3: W=2, R=2 (strict quorum)
N=5: W=3, R=3 (majority quorum)
N=5: W=1, R=5 (read-heavy optimization)
N=5: W=5, R=1 (write-heavy optimization)
```

</div>

## CAP Theorem Visualized

<div class="cap-visualization">

```
Network Partition Occurs:
        [A,B]  ~~~X~~~  [C,D,E]
      (2 nodes)      (3 nodes)

Choice 1: Maintain Consistency
- Reject writes to [A,B] minority
- System partially unavailable
- Example: Bank accounts

Choice 2: Maintain Availability  
- Accept writes on both sides
- Divergent state (resolve later)
- Example: Shopping cart
```

</div>

## Truth Coordination Patterns

<div class="pattern-cards">

=== "Last Write Wins (LWW)"
    ```
    Node A: Set X=5 at time 100
    Node B: Set X=7 at time 99
    Result: X=5 (highest timestamp wins)
    
    Pros: Simple, automatic
    Cons: Lost updates, clock dependent
    ```

=== "Vector Clocks"
    ```
    Node A: X=5, version=[A:1, B:0]
    Node B: X=7, version=[A:0, B:1]
    Merge: Conflict detected! 
    
    Pros: Detects all conflicts
    Cons: Requires resolution logic
    ```

=== "CRDTs"
    ```
    Counter CRDT:
    Node A: +3
    Node B: +2
    Merge: +5 (commutative!)
    
    Pros: Automatic merge
    Cons: Limited operations
    ```

</div>

## The Consistency Spectrum

<div class="consistency-slider">

```
Consistency Level Selector:
STRONG ●────────────────────○ EVENTUAL
       ↑                    ↑
    Your DB              Your Cache

[================|----] 80% Strong

Settings:
├─ Read Preference:  [Primary Only ▼]
├─ Write Concern:    [Majority     ▼]
├─ Read Concern:     [Linearizable ▼]
└─ Timeout:          [5000ms       ]

Trade-offs at current setting:
✓ Guaranteed latest data
✓ No stale reads
✗ Higher latency (200ms vs 20ms)
✗ Lower availability (99.9% vs 99.99%)
✗ Higher cost ($$ vs $)
```

</div>

## Consistency Levels Explained

<div class="consistency-levels">

```
1. LINEARIZABLE (Strongest)
   - Real-time ordering
   - Like single-threaded execution
   - Cost: Multiple round trips
   - Use: Financial transactions

2. SEQUENTIAL  
   - Operations appear in program order
   - May not reflect real-time
   - Cost: Coordination per client
   - Use: User session state

3. CAUSAL
   - Preserves cause → effect
   - Allows concurrent operations
   - Cost: Vector clocks
   - Use: Social media comments

4. EVENTUAL (Weakest)
   - Converges eventually
   - No ordering guarantees
   - Cost: Minimal
   - Use: View counters
```

</div>

## Real-World Consistency Trade-offs

<div class="tradeoff-examples">

| System | Consistency Level | Trade-off |
|--------|------------------|-----------|
| YouTube View Counter | Eventual | Updates batched hourly<br>Accuracy for scale |
| Bank Balance | Strong | Every read sees all writes<br>Scale for correctness |
| Twitter Timeline | Causal | Replies after original tweets<br>Some ordering for speed |
| Shopping Cart | Session | User sees own updates<br>Global consistency for UX |

</div>

## Consensus Protocol Comparison

| Protocol | Fault Tolerance | Performance | Complexity | Use Case |
|----------|----------------|-------------|------------|-----------|
| 2PC | None (blocking) | Fast | Simple | Single DC transactions |
| Paxos | f failures with 2f+1 nodes | Medium | Very Complex | Critical infrastructure |
| Raft | f failures with 2f+1 nodes | Medium | Moderate | General purpose |
| PBFT | f Byzantine with 3f+1 nodes | Slow | Complex | Untrusted environments |

## The Split-Brain Problem

<div class="split-brain-diagram">

```
Before Partition:
[Master] ←→ [Replica1] ←→ [Replica2]
    ↓
All writes go here

During Partition:
[Master] ←X→ [Replica1] ←→ [Replica2]
    ↓               ↓
Writes here    Replica1 promotes itself!
               Writes here too!

Result: Two masters, divergent data
```

</div>

<div class="truth-box">

**Counter-Intuitive Truth 💡**

Perfect consistency is often unnecessary. Many successful systems use eventual consistency for 99% of operations and reserve strong consistency only for critical paths (payments, authentication). The key is knowing which is which.

</div>

## Common Truth Distribution Anti-Patterns

!!! warning "Avoid These"
    
    1. **Assuming Clocks are Synchronized**: They never are perfectly
    2. **Ignoring Byzantine Failures**: Nodes can lie or act maliciously
    3. **Over-Coordinating**: Not everything needs consensus
    4. **Under-Specifying Conflicts**: "It won't happen" always does
    5. **Manual Conflict Resolution**: Doesn't scale

## Related Concepts

- **[Axiom 4: Concurrency](../../part1-axioms/axiom-4-concurrency/index.md)**: Time is relative
- **[Axiom 5: Coordination](../../part1-axioms/axiom-5-coordination/index.md)**: Agreement has costs
- **[Pillar 2: State](../pillar-2-state/index.md)**: Truth about state

## Key Takeaways

!!! success "Remember"
    
    1. **Truth is expensive** - Consensus requires multiple round trips
    2. **CAP is real** - You can't have it all during partitions
    3. **Eventual is often enough** - Strong consistency for critical paths only
    4. **Conflicts are inevitable** - Design resolution strategies upfront
    5. **Leader election is hard** - Use proven algorithms, don't roll your own

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Truth Distribution Examples](examples.md) →
    
    **Practice**: [Truth Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of Control](../pillar-4-control/index.md) →
    
    **Jump to**: [Consensus Tools](../../tools/consensus-tools.md) | [Reference](../../reference/index.md)