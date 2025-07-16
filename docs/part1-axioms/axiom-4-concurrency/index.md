# Axiom 4: Concurrency

!!! info "Prerequisites"
    - [Axiom 3: Partial Failure](../axiom-3-failure/index.md)
    - Understanding of threads and processes
    - Basic knowledge of databases

!!! tip "Quick Navigation"
    [← Axiom 3](../axiom-3-failure/index.md) | 
    [Examples →](examples.md) | 
    [Exercises →](exercises.md) |
    [→ Next: Coordination](../axiom-5-coordination/index.md)

!!! target "Learning Objective"
    Concurrent operations create states that don't exist in sequential execution.

## Core Concept

<div class="axiom-box">

**Core Paradox:**

```
Sequential: A then B = predictable
Concurrent: A while B = 
  - A then B
  - B then A  
  - A interleaved with B (multiple ways!)
  - Partial A, partial B, explosion of states
```

</div>

## Why Concurrency Is Hard

### State Space Explosion

With just 2 threads and 3 operations each:
- Sequential: 2 possible orderings
- Concurrent: 20 possible interleavings!

With N threads and M operations each:
- Possible interleavings: (N×M)! / (M!)^N

## Concurrency Bugs Taxonomy

1. **Race Condition**: Outcome depends on timing
2. **Deadlock**: Circular wait for resources
3. **Livelock**: Threads actively doing nothing
4. **Starvation**: Some threads never get resources
5. **ABA Problem**: Value changes A→B→A between checks
6. **Priority Inversion**: Low priority blocks high

## Concurrency Control Mechanisms

### 1. Pessimistic Locking

```sql
BEGIN;
SELECT * FROM seats WHERE id = '14A' FOR UPDATE;
-- Lock held until commit
UPDATE seats SET passenger = 'Alice' WHERE id = '14A';
COMMIT;

-- Pro: Guarantees consistency
-- Con: Reduces concurrency, can deadlock
```

### 2. Optimistic Locking (CAS)

```sql
SELECT version FROM seats WHERE id = '14A'; -- Returns v1
UPDATE seats 
SET passenger = 'Alice', version = v2
WHERE id = '14A' AND version = v1;
-- Check affected rows, retry if 0

-- Pro: Better concurrency
-- Con: Retry storms under contention
```

### 3. MVCC (Multi-Version Concurrency)

```sql
-- Each transaction sees consistent snapshot
-- Conflicts detected at commit time

-- Pro: Readers don't block writers
-- Con: Complex implementation
```

<div class="decision-box">

**🎯 Decision Tree: Lock vs CAS vs Queue**

```
What's the contention level?
├─ LOW (<10% conflicts)
│  └─ Use optimistic locking (CAS)
├─ MEDIUM (10-50% conflicts)  
│  ├─ Short operation? → Pessimistic lock
│  └─ Long operation? → Queue + single worker
└─ HIGH (>50% conflicts)
   └─ Redesign to avoid contention
      ├─ Partition the resource
      ├─ Use conflict-free replicated data types
      └─ Event sourcing with eventual consistency
```

</div>

## Space-Time Diagrams

Understanding distributed time:

```
Process A  ─────●─────────●───────────●────→ time
                │ e1      │ e3        │ e5
                ↓         ↓           ↓
Process B  ───────────●───────●───────────→ time
                      │ e2    │ e4
                      
Happens-before: e1 → e2 → e3 → e4 → e5
Concurrent: (e1 || e4), (e3 || e4)
```

## Vector Clocks

Track causality in distributed systems:

```yaml
Each process maintains vector: [A_count, B_count, C_count]

Process A: [1,0,0] → sends message → [2,0,0]
Process B: [0,0,0] → receives → [2,1,0] → sends → [2,2,0]
Process C: [0,0,1] → receives → [2,2,1]

Comparing vectors:
[2,1,0] happens-before [2,2,1] ✓
[2,1,0] concurrent-with [1,0,2] ✓
```

## Common Patterns

### 1. Lock-Free Data Structures

Use atomic operations instead of locks.

### 2. Actor Model

Isolate state within actors, communicate via messages.

### 3. Software Transactional Memory

Treat memory operations like database transactions.

### 4. Event Sourcing

Store events, not state. Natural concurrency control.

### 5. CRDTs

Conflict-free Replicated Data Types merge automatically.

## Concurrency vs Parallelism

!!! info "Key Distinction"
    - **Concurrency**: Dealing with lots of things at once (design)
    - **Parallelism**: Doing lots of things at once (execution)
    
    You can have concurrency without parallelism!

## Memory Models & Guarantees

### Visibility Guarantees

| Level | Guarantee | Use Case |
|-------|-----------|----------|
| **Relaxed** | No ordering | Counters |
| **Acquire/Release** | Synchronizes-with | Locks |
| **Sequential Consistency** | Total order | Critical sections |
| **Strict Consistency** | Instant visibility | Rarely needed |

<div class="truth-box">

**Counter-Intuitive Truth 💡**

Adding more threads often makes programs slower due to:
- Cache coherence overhead
- Lock contention
- Context switching
- False sharing

The fastest concurrent program often uses fewer threads than cores.

</div>

## Related Concepts

- **[Axiom 5: Coordination](../axiom-5-coordination/index.md)**: Concurrency requires coordination
- **[State Management](../../part2-pillars/pillar-2-state/index.md)**: Managing concurrent state
- **[Truth Distribution](../../part2-pillars/pillar-3-truth/index.md)**: Consensus with concurrency

## Key Takeaways

!!! success "Remember"
    
    1. **Concurrency is not parallelism** - Design vs execution
    2. **State space explodes** - Testing can't cover all cases
    3. **Timing is everything** - And you can't control it
    4. **Locks are not enough** - Need proper synchronization
    5. **Simpler is better** - Reduce shared state

## Navigation

!!! tip "Continue Learning"
    
    **Deep Dive**: [Concurrency Examples & Failures](examples.md) →
    
    **Practice**: [Concurrency Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 5: Coordination Cost](../axiom-5-coordination/index.md) →
    
    **Jump to**: [Concurrency Patterns](../../patterns/concurrency-patterns.md) | [Part II](../../part2-pillars/index.md)