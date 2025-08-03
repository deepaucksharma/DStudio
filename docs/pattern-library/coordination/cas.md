---
title: CAS (Compare-and-Swap)
description: Lock-free atomic operation for concurrent data structures
type: pattern
category: coordination
difficulty: intermediate
reading_time: 25 min
prerequisites: 
  - concurrency
  - memory-models
excellence_tier: silver
pattern_status: use-with-caution
introduced: 1972-01
current_relevance: niche
essential_question: How do we achieve thread-safe updates without locks and their overhead?
tagline: Lock-free atomic operations with compare-and-swap semantics
trade_offs:
  pros:
    - "Lock-free performance eliminates blocking"
    - "No deadlock or priority inversion possible"
    - "Fine-grained concurrency control"
    - "Composable with other lock-free structures"
  cons:
    - "ABA problem creates subtle correctness issues"
    - "Limited to single-word atomic updates"
    - "Difficult debugging and reasoning"
    - "Livelock under high contention"
best_for: "High-performance counters, lock-free data structures, low-contention atomic updates"
related_laws:
  - law2-asynchrony
  - law4-optimization
  - law7-economics
related_pillars:
  - work
  - state
---

# CAS (Compare-and-Swap)

!!! info "🥈 Silver Tier Pattern"
    **Lock-free power with complexity** • Use for specific performance-critical needs
    
    CAS enables lock-free programming but comes with significant complexity. The ABA problem and debugging challenges mean traditional locks are often the better choice unless you have specific performance requirements and expertise.
    
    **Best For:** High-performance counters, specialized concurrent data structures where contention is moderate

## Essential Question

**How do we achieve thread-safe updates without locks and their overhead?**

## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Example | Impact |
|----------|---------|--------|
| **High-Performance Counters** | Metrics collection with millions of increments/sec | 10x faster than mutex-based counters |
| **Low-Contention Updates** | Configuration flags, status fields | Minimal retry loops, predictable performance |
| **Lock-Free Data Structures** | Concurrent stacks, queues for specialized use cases | Eliminate blocking, improve scalability |

### ❌ DON'T Use When

| Scenario | Why | Alternative |
|----------|-----|-------------|
| **High Contention** | Causes livelock and performance degradation | [Locks with backoff](../coordination/distributed-lock.md) |
| **Complex Operations** | Multi-step updates can't be atomic | [Transactional Memory](../coordination/stm.md) |
| **Team Inexperience** | Subtle bugs are hard to debug | Traditional synchronization primitives |
| **General Purpose** | Locks provide better guarantees | Standard mutex/semaphore patterns |

## Level 1: Intuition (5 min) {#intuition}

### The Story

Imagine updating a shared scoreboard at a sports stadium. The traditional approach requires locking the entire board, making your change, then unlocking it - causing everyone else to wait. CAS is like having a magic marker that only works if the current score matches what you expect. If someone else changed it while you were calculating, your marker won't write, and you need to check the new score and try again.

### Visual Metaphor

```mermaid
graph LR
    subgraph "CAS Operation"
        A[Read Value: 10] --> B{Compare: 10 == 10?}
        B -->|Yes| C[Swap to 15]
        B -->|No| D[Retry with new value]
        C --> E[Success]
        D --> A
    end
    
    subgraph "Lock-based"
        F[Acquire Lock] --> G[Read & Modify]
        G --> H[Release Lock]
        I[Other threads wait] -.-> F
    end
    
    style C fill:#81c784,stroke:#388e3c
    style E fill:#64b5f6,stroke:#1976d2
    style I fill:#ffcdd2,stroke:#d32f2f
```

### Core Insight

> **Key Takeaway:** CAS trades the guaranteed success of locks for optimistic, retry-based operations that avoid blocking but require careful handling of failures.

### In One Sentence

CAS atomically checks if a memory location contains an expected value and updates it to a new value, returning success/failure without blocking other threads.

## Level 2: Foundation (10 min) {#foundation}

### The Problem Space

<div class="failure-vignette">
<h4>🚨 What Happens With Lock Contention</h4>

**High-Frequency Trading System, 2021**: Order processing system used mutex-protected counters for tracking. Under peak load, lock contention caused 95th percentile latency to spike from 50μs to 15ms.

**Impact**: 12% reduction in successful trades, $8M daily revenue loss during market volatility periods when low latency was critical.
</div>

### How It Works

#### CAS Operation Flow

```mermaid
sequenceDiagram
    participant T1 as Thread 1
    participant T2 as Thread 2
    participant M as Memory Location
    
    Note over M: Initial value: 100
    
    T1->>M: Read value (100)
    T2->>M: Read value (100)
    
    Note over T1: Calculate new value: 105
    Note over T2: Calculate new value: 110
    
    T1->>M: CAS(expected: 100, new: 105)
    Note over M: 100 == 100 ✓, set to 105
    M-->>T1: Success ✅
    
    T2->>M: CAS(expected: 100, new: 110)
    Note over M: 105 != 100 ✗
    M-->>T2: Failure ❌
    
    T2->>M: Read new value (105)
    Note over T2: Recalculate: 105 + 10 = 115
    T2->>M: CAS(expected: 105, new: 115)
    M-->>T2: Success ✅
```

#### Key Components

| Component | Purpose | Responsibility |
|-----------|---------|----------------|
| **Expected Value** | Consistency check | Ensure no intermediate changes occurred |
| **New Value** | Update target | Value to store if comparison succeeds |
| **Return Status** | Operation result | Indicate success/failure for retry logic |
| **Memory Ordering** | Synchronization | Ensure proper visibility across threads |

### Basic Example

```cpp
// Simple CAS-based counter
class AtomicCounter {
    std::atomic<int> value{0};
    
public:
    int increment() {
        int current = value.load();
        int next;
        do {
            next = current + 1;
        } while (!value.compare_exchange_weak(current, next));
        return next;
    }
};
```

## Level 3: Deep Dive (15 min) {#deep-dive}

### Implementation Details

#### CAS vs Traditional Locking

```mermaid
graph TB
    subgraph "CAS Approach"
        C1[Thread reads value] --> C2[Computes new value]
        C2 --> C3{CAS succeeds?}
        C3 -->|Yes| C4[Operation complete]
        C3 -->|No| C1
    end
    
    subgraph "Lock Approach"
        L1[Thread acquires lock] --> L2[Reads & modifies]
        L2 --> L3[Releases lock]
        L4[Other threads blocked] -.-> L1
    end
    
    classDef primary fill:#5448C8,stroke:#3f33a6,color:#fff
    classDef secondary fill:#00BCD4,stroke:#0097a7,color:#fff
    classDef blocked fill:#ffcdd2,stroke:#d32f2f
    
    class C1,C2,C4 primary
    class L1,L2,L3 secondary
    class L4 blocked
```

#### Critical Design Decisions

| Decision | Options | Trade-off | Recommendation |
|----------|---------|-----------|----------------|
| **Memory Ordering** | Relaxed<br>Acquire-Release<br>Sequential | Relaxed: Faster, complex reasoning<br>Seq: Slower, easier reasoning | Acquire-Release for most cases |
| **Retry Strategy** | Immediate<br>Backoff<br>Yield | Immediate: Livelock risk<br>Backoff: Better under contention | Exponential backoff |
| **Failure Handling** | Loop until success<br>Limited retries | Loop: Guaranteed progress<br>Limited: Bounded latency | Context-dependent choice |

### Common Pitfalls

<div class="decision-box">
<h4>⚠️ Avoid These Mistakes</h4>

1. **ABA Problem**: Value changes A→B→A between read and CAS → Use versioned references
2. **Livelock**: High contention causes infinite retries → Implement exponential backoff
3. **Memory Ordering**: Wrong synchronization semantics → Use acquire-release semantics
</div>

### Production Considerations

#### Performance Characteristics

| Metric | Low Contention | Medium Contention | High Contention |
|--------|---------------|-------------------|-----------------|
| Latency | 1-5 ns | 10-50 ns | 100-1000 ns |
| Success Rate | >95% | 70-90% | <50% |
| CPU Usage | Minimal | Moderate | High (spinning) |
| Throughput | Excellent | Good | Poor |

## Level 4: Expert (20 min) {#expert}

### Advanced Techniques

#### Optimization Strategies

1. **Hazard Pointers for Memory Safety**
   - When to apply: Lock-free data structures with pointers
   - Impact: Safe memory reclamation without garbage collection
   - Trade-off: Additional complexity and memory overhead

2. **Tagged Pointers (ABA Solution)**
   - When to apply: Pointer-based data structures
   - Impact: Eliminates ABA problem completely
   - Trade-off: Requires extra bits for version tags

### Lock-Free Data Structures

```mermaid
graph TB
    subgraph "Lock-Free Stack"
        S1[Top Pointer] --> S2[Node 1]
        S2 --> S3[Node 2]
        S3 --> S4[Node 3]
        S4 --> S5[null]
        
        S6[Push: CAS top pointer] --> S1
        S7[Pop: CAS top to next] --> S1
    end
    
    subgraph "Lock-Free Queue"
        Q1[Head] --> Q2[Node A]
        Q2 --> Q3[Node B]
        Q3 --> Q4[Node C]
        Q5[Tail] --> Q4
        
        Q6[Enqueue: CAS tail->next] --> Q5
        Q7[Dequeue: CAS head pointer] --> Q1
    end
    
    classDef primary fill:#5448C8,stroke:#3f33a6,color:#fff
    classDef secondary fill:#00BCD4,stroke:#0097a7,color:#fff
    
    class S1,Q1,Q5 primary
    class S2,S3,S4,Q2,Q3,Q4 secondary
```

### Monitoring & Observability

#### Key Metrics to Track

| Metric | Alert Threshold | Dashboard Panel |
|--------|----------------|-----------------|
| CAS Success Rate | < 80% | Success rate histogram |
| Retry Count | > 10 per operation | Retry distribution chart |
| Contention Level | > 50% operations retrying | Contention heat map |
| Livelock Detection | Same thread retrying >1000x | Thread activity timeline |

## Level 5: Mastery (30 min) {#mastery}

### Real-World Case Studies

#### Case Study 1: Intel Performance Primitives

<div class="truth-box">
<h4>💡 Production Insights from Intel</h4>

**Challenge**: Atomic counters in high-performance computing libraries needed to scale across 100+ cores

**Implementation**: 
- Hardware-optimized CAS operations
- Hierarchical counting to reduce contention
- NUMA-aware data placement

**Results**: 
- **Scalability**: Linear scaling to 128 cores
- **Performance**: 40x faster than mutex-based counters
- **Adoption**: Used in TensorFlow, NumPy core operations

**Lessons Learned**: CAS excels in read-heavy scenarios with infrequent updates. Careful data placement is critical for NUMA systems.
</div>

### Pattern Evolution

#### From Locks to Lock-Free

```mermaid
graph LR
    A[Coarse-Grained<br/>Locks] -->|Step 1| B[Fine-Grained<br/>Locks]
    B -->|Step 2| C[Lock-Free<br/>CAS]
    C -->|Step 3| D[Wait-Free<br/>Algorithms]
    
    style A fill:#ffb74d,stroke:#f57c00
    style B fill:#fff176,stroke:#f57f17
    style C fill:#81c784,stroke:#388e3c
    style D fill:#64b5f6,stroke:#1976d2
```

#### Future Directions

| Trend | Impact on Pattern | Adaptation Strategy |
|-------|------------------|-------------------|
| **Hardware Transactional Memory** | May replace CAS for complex operations | Hybrid HTM/CAS approaches |
| **Many-Core Processors** | Higher contention scenarios | Hierarchical and distributed algorithms |
| **Persistent Memory** | Need for crash-consistent CAS | Integration with persistent memory primitives |

### Pattern Combinations

#### Works Well With

| Pattern | Combination Benefit | Integration Point |
|---------|-------------------|------------------|
| [Optimistic Locking](../data-management/optimistic-locking.md) | Version-based conflict resolution | CAS for version updates |
| [CRDT](../data-management/crdt.md) | Conflict-free concurrent updates | CAS for operation ordering |
| [Event Sourcing](../data-management/event-sourcing.md) | Append-only conflict resolution | CAS for sequence numbers |

## Quick Reference

### Decision Matrix

```mermaid
graph TD
    A[Need Atomic Update?] --> B{Contention Level?}
    B -->|Low| C[Use CAS]
    B -->|Medium| D{Operation Complexity?}
    B -->|High| E[Use Locks]
    
    D -->|Simple| F[CAS with backoff]
    D -->|Complex| G[Consider STM]
    
    C --> H[Atomic primitives]
    F --> I[Retry with exponential backoff]
    E --> J[Traditional synchronization]
    G --> K[Software Transactional Memory]
    
    classDef recommended fill:#81c784,stroke:#388e3c,stroke-width:2px
    classDef caution fill:#ffb74d,stroke:#f57c00,stroke-width:2px
    classDef avoid fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    
    class C,H recommended
    class F,I caution
    class E,J avoid
```

### Comparison with Alternatives

| Aspect | CAS | Mutex | Atomic Operations | Transactional Memory |
|--------|-----|-------|-------------------|---------------------|
| **Blocking** | No | Yes | No | No |
| **Deadlock Risk** | No | Yes | No | No |
| **Composability** | Limited | Good | Limited | Excellent |
| **Performance** | Variable | Predictable | Excellent | Good |
| **When to use** | Low contention | High contention | Simple operations | Complex operations |

### Implementation Checklist

**Pre-Implementation**
- [ ] Measured contention levels in target scenario
- [ ] Verified operations are simple enough for CAS
- [ ] Assessed team expertise with lock-free programming
- [ ] Considered ABA problem implications

**Implementation**
- [ ] Used proper memory ordering semantics
- [ ] Implemented retry logic with backoff
- [ ] Added contention monitoring
- [ ] Tested under realistic load patterns

**Post-Implementation**
- [ ] Validated performance improvements over locks
- [ ] Monitored for livelock scenarios
- [ ] Created debugging and profiling guides
- [ ] Documented memory model assumptions

### Related Resources

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **Related Patterns**
    
    ---
    
    - [Optimistic Locking](../data-management/optimistic-locking.md) - Database-level CAS
    - [CRDT](../data-management/crdt.md) - Conflict-free updates
    - [Atomic Broadcast](../coordination/atomic-broadcast.md) - Ordered operations

- :material-flask:{ .lg .middle } **Fundamental Laws**
    
    ---
    
    - [Law 2: Asynchronous Reality](../../part1-axioms/law2-asynchrony/) - Non-blocking nature
    - [Law 4: Multidimensional Optimization](../../part1-axioms/law4-optimization/) - Performance tradeoffs

- :material-pillar:{ .lg .middle } **Foundational Pillars**
    
    ---
    
    - [Work Distribution](../../part2-pillars/work/) - Lock-free task coordination
    - [State Distribution](../../part2-pillars/state/) - Atomic state updates

- :material-tools:{ .lg .middle } **Implementation Guides**
    
    ---
    
    - [Lock-Free Programming Guide](../../excellence/guides/lock-free-programming.md)
    - [Memory Model Tutorial](../../excellence/guides/memory-models.md)
    - [Performance Testing Guide](../../excellence/guides/concurrency-testing.md)

</div>