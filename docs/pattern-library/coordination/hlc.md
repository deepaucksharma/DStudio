---
category: coordination
current_relevance: mainstream
description: Combine physical timestamps with logical counters to achieve causally
  consistent timestamps that are close to wall-clock time while handling clock skew
difficulty: advanced
essential_question: How do we coordinate distributed components effectively using
  hybrid logical clocks (hlc)?
excellence_tier: gold
introduced: 2014-01
last-updated: 2025-07-26
modern-examples:
- company: CockroachDB
  implementation: HLC for distributed SQL with global consistency
  scale: Petabyte-scale clusters with microsecond precision
- company: MongoDB
  implementation: Cluster-wide logical timestamps for causal consistency
  scale: Millions of operations/sec with session guarantees
- company: YugabyteDB
  implementation: HLC-based multi-version concurrency control
  scale: Global deployments with consistent snapshots
pattern_status: recommended
prerequisites:
- logical-clocks
- vector-clocks
- clock-sync
- distributed-systems
production-checklist:
- Configure NTP with tight bounds (<100ms drift)
- Set appropriate clock uncertainty windows
- Implement clock jump detection and handling
- Monitor clock skew between nodes
- Configure HLC tick interval (typically 1-10ms)
- Implement timestamp persistence across restarts
- Test behavior under clock adjustments
- Set up alerts for excessive clock drift
- Plan for timestamp overflow (64-bit limits)
- Document timestamp ordering guarantees
reading-time: 35 min
status: complete
tagline: Master hybrid logical clocks (hlc) for distributed systems success
tags:
- time-synchronization
- causality
- distributed-clocks
- hybrid-time
- global-transactions
title: Hybrid Logical Clocks (HLC)
type: pattern
when-not-to-use: When pure logical ordering suffices, systems with perfect clock sync,
  when vector clock overhead is acceptable
when-to-use: When you need both wall-clock time approximation and causal consistency,
  distributed databases with global transactions, event ordering with human-readable
  timestamps
---

## Essential Question

**How do we coordinate distributed components effectively using hybrid logical clocks (hlc)?**


# Hybrid Logical Clocks (HLC) Pattern

!!! success "🏆 Gold Standard Pattern"
    **Best of Both Worlds: Physical Time + Logical Ordering**
    
    HLC solves the distributed timestamp problem by combining wall-clock time with logical counters. Used by CockroachDB (petabyte scale), MongoDB (millions ops/sec), and YugabyteDB (global ACID).

!!! question "Essential Questions for Modern Distributed Systems"
    - **Q: How do you get both wall-clock time AND causal consistency?**  
      A: Combine physical timestamp with logical counter in single 64-bit value
    - **Q: What happens when clocks drift between nodes?**  
      A: HLC absorbs drift up to configured bounds while maintaining causality
    - **Q: How does this compare to Google's TrueTime?**  
      A: Similar guarantees without specialized hardware - trades wait time for logical counter

<div class="decision-box">
<h3>🎯 When to Use HLC</h3>

```mermaid
graph TD
    Start[Need Distributed<br/>Timestamps?] --> Wall{Need Wall<br/>Clock Time?}
    Wall -->|No| Lamport[Use Lamport Clocks]
    Wall -->|Yes| Causal{Need Causal<br/>Consistency?}
    Causal -->|No| NTP[Use NTP Timestamps]
    Causal -->|Yes| Hardware{Have Special<br/>Hardware?}
    Hardware -->|Yes| TT[Use TrueTime]
    Hardware -->|No| HLC[✓ Use HLC]
    
    style HLC fill:#90EE90
```
</div>

## The Problem: Physical vs Logical Time

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

```mermaid
graph LR
    subgraph "Physical Clocks"
        P1[Node 1: 10:00:00]
        P2[Node 2: 10:00:05]
        P3[Node 3: 09:59:58]
        ProbP[❌ Clock Skew<br/>❌ Wrong Ordering<br/>❌ Causality Violations]
    end
    
    subgraph "Logical Clocks"
        L1[Node 1: LC=100]
        L2[Node 2: LC=200]
        L3[Node 3: LC=150]
        ProbL[❌ No Real Time<br/>❌ Not Human Readable<br/>❌ Can't Correlate Events]
    end
    
    subgraph "HLC Solution"
        H1[Node 1: 10:00:00.001]
        H2[Node 2: 10:00:00.002]
        H3[Node 3: 10:00:00.003]
        Sol[✓ Close to Real Time<br/>✓ Preserves Causality<br/>✓ Total Ordering]
    end
    
    style ProbP fill:#FFB6C1
    style ProbL fill:#FFB6C1
    style Sol fill:#90EE90
```

</details>

## HLC Core Concept

<div class="axiom-box">
<h4>💡 The HLC Formula</h4>

**HLC Timestamp = Physical Time + Logical Counter**

- **Physical Part (48 bits)**: Milliseconds since epoch (close to wall clock)
- **Logical Part (16 bits)**: Disambiguates events at same physical time
- **Format**: `physical_time.logical_counter` (e.g., `1706280000.42`)

</div>

## The Three HLC Rules

### Visual Algorithm

```mermaid
sequenceDiagram
    participant A as Node A
    participant B as Node B
    participant C as Node C
    
    Note over A,C: Initial: All at physical time 100
    
    A->>A: Local Event<br/>now=101 > pt=100<br/>HLC: 101.0
    
    A->>B: Send msg @ 101.0
    Note over B: Receive @ now=100<br/>max(100,101,100)=101<br/>Same as received<br/>HLC: 101.1
    
    B->>C: Send msg @ 101.1
    Note over C: Receive @ now=102<br/>max(100,101,102)=102<br/>Physical time wins<br/>HLC: 102.0
```

### The Three Rules

| Event | Rule | HLC Update |
|-------|------|------------|
| **Local Event** | `if now > pt: pt=now, c=0 else: c++` | Advance physical or logical |
| **Send Message** | `update_local(); attach(pt,c)` | Update then send |
| **Receive Message** | `pt = max(pt_local, pt_msg, now)` | Take maximum, increment logical |

## Key Properties

### Property 1: Bounded Drift

<div class="axiom-box">
<h4>📏 Drift Bound Guarantee</h4>

**|HLC_time - Physical_time| ≤ ε**

Where ε = max_clock_error + max_message_delay

- **Datacenter**: ε ≈ 11ms (1ms clock + 10ms network)
- **Cloud**: ε ≈ 110ms (10ms clock + 100ms network)
- **GPS-synced**: ε ≈ 10.1ms (100μs clock + 10ms network)
</div>

### Property 2: Causality Preservation

```mermaid
graph LR
    A[Event A: HLC=100.5] -->|causes| B[Event B: HLC=100.8]
    B -->|causes| C[Event C: HLC=101.0]
    
    Result[✓ Causality: 100.5 < 100.8 < 101.0]
    
    A --> Result
    B --> Result
    C --> Result
    
    style Result fill:#90EE90
```

## Clock Type Comparison

| Feature | Physical | Lamport | Vector | **HLC** |
|---------|----------|---------|---------|---------|
| **Wall Time** | ✓ Exact | ✗ None | ✗ None | ✓ Approximate |
| **Causality** | ✗ May violate | ✓ Preserves | ✓ Detects concurrent | ✓ Preserves |
| **Size** | 8 bytes | 4-8 bytes | O(n) × 8 bytes | 8 bytes |
| **Clock Sync** | Required | Not needed | Not needed | Beneficial |
| **Best For** | Timestamps | Event ordering | Conflict detection | **Modern databases** |

## Simple Implementation

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

```python
class HLC:
    def __init__(self):
        self.pt = 0  # physical time
        self.c = 0   # logical counter
    
    def update(self, msg_pt=None, msg_c=None):
        """Update HLC for local event or message"""
        now = current_time_ms()
        
        if msg_pt is None:  # Local event
            if now > self.pt:
                self.pt = now
                self.c = 0
            else:
                self.c += 1
        else:  # Receive message
            new_pt = max(self.pt, msg_pt, now)
            
            if new_pt == now:
                self.c = 0
            elif new_pt == self.pt == msg_pt:
                self.c = max(self.c, msg_c) + 1
            else:
                self.c = (self.c if new_pt == self.pt else msg_c) + 1
            
            self.pt = new_pt
        
        return (self.pt, self.c)
```

</details>

## Production Considerations

<div class="grid">
<div class="card">
<h4>⚠️ Counter Overflow</h4>

**Problem**: 16-bit counter = 65,535 max  
**At 1M events/sec**: Overflow in 65ms  
**Solution**: Wait for physical time tick  
**Better**: Use microsecond precision
</div>

<div class="card">
<h4>💾 Persistence</h4>

**Problem**: Clock reset on restart  
**Impact**: Causality violations  
**Solution**: Save HLC to disk  
**On restart**: max(saved, current_time)
</div>

<div class="card">
<h4>🕐 Clock Jumps</h4>

**Problem**: NTP adjustments  
**Forward jump**: Accept if < 1 min  
**Backward jump**: Keep using old time  
**Monitor**: Alert on large jumps
</div>
</div>

## Real-World Examples

### Production Usage Patterns

| System | HLC Usage | Scale | Key Benefit |
|--------|-----------|-------|-------------|
| **CockroachDB** | MVCC timestamps | Petabyte clusters | Global consistency |
| **MongoDB** | Session consistency | Millions ops/sec | Causal reads |
| **YugabyteDB** | Transaction ordering | Global deployment | ACID guarantees |
| **Kafka** | Event timestamps | Trillion events/day | Order preservation |

### Visual: HLC in Distributed Database

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

```mermaid
graph TB
    subgraph "Write Transaction"
        W1[Client Write]
        W2[Assign HLC: 1000.5]
        W3[Replicate with HLC]
        W4[Commit at HLC]
    end
    
    subgraph "Read Transaction"
        R1[Client Read]
        R2[Choose HLC: 1000.3]
        R3[Read MVCC at HLC]
        R4[Consistent Snapshot]
    end
    
    W1 --> W2 --> W3 --> W4
    R1 --> R2 --> R3 --> R4
    
    Note[HLC ensures read sees<br/>consistent snapshot]
    
    style W2 fill:#87CEEB
    style R2 fill:#87CEEB
```

</details>

## HLC vs TrueTime

<div class="axiom-box">
<h4>🆚 Key Difference</h4>

**TrueTime**: Uses specialized hardware (GPS/atomic clocks) to bound uncertainty, then waits out the uncertainty interval

**HLC**: Uses standard NTP clocks with logical counters to handle uncertainty without waiting

Trade-off: TrueTime guarantees external consistency, HLC provides best-effort with no special hardware
</div>

| Feature | TrueTime | HLC |
|---------|----------|-----|
| **Hardware** | GPS + Atomic clocks | Standard NTP |
| **Commit Latency** | Wait 2×ε (14ms typical) | No wait |
| **Guarantees** | External consistency | Causal consistency |
| **Cost** | Very high | Low |
| **Complexity** | High | Medium |

## Common Pitfalls

| Mistake | Problem | Solution |
|---------|---------|----------|
| **Assume tight clock sync** | ±30s+ skew reality | Monitor actual drift |
| **Ignore counter overflow** | 65K events/65ms limit | Use microsecond precision |
| **Mix HLC with wall clock** | HLC can be "ahead" | Use HLC consistently |

## Summary

<div class="axiom-box">
<h3>🎯 HLC Design Principles</h3>

1. **Best of Both Worlds**: Combines wall-clock approximation with logical consistency
2. **Bounded Uncertainty**: Drift from physical time is bounded by clock error + network delay
3. **Causality Preservation**: Always respects happens-before relationships
4. **Constant Overhead**: Fixed 64-bit size regardless of cluster size
5. **Practical Consistency**: Achieves consistency without specialized hardware

</div>

### When to Use HLC

✅ **Perfect for:**
- Distributed databases requiring global timestamps
- Event streaming with causal ordering
- Systems needing human-readable timestamps
- Multi-region deployments with clock skew

❌ **Avoid when:**
- Need to detect concurrent updates (use vector clocks)
- Have perfect clock synchronization
- Only need logical ordering (use Lamport clocks)
- Building single-node systems

#
## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Checklist

| ✓ | Task | Why Important |
|---|------|---------------|
| ☐ | Choose time precision (ms/μs/ns) | Affects overflow rate |
| ☐ | Implement counter overflow handling | Prevents stalls |
| ☐ | Add persistence across restarts | Maintains monotonicity |
| ☐ | Monitor clock synchronization | Ensures bounded drift |
| ☐ | Handle backward time jumps | Prevents violations |
| ☐ | Add comprehensive metrics | Production visibility |

## Related Patterns

- [Logical Clocks](logical-clocks.md) - Simpler causality tracking
- [Vector Clocks](vector-clocks.md) - Full concurrency detection
- [Clock Synchronization](clock-sync.md) - Physical time coordination
- [Event Sourcing](event-sourcing.md) - Event streams with HLC
- [Consensus](consensus.md) - Often combined with HLC

## References

- [Logical Physical Clocks and Consistent Snapshots](https://cse.buffalo.edu/tech-reports/2014-04.pdf) - Original HLC paper
- [CockroachDB Clock Synchronization](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer.html#time-and-hybrid-logical-clocks) 
- [YugabyteDB Hybrid Time](https://docs.yugabyte.com/preview/architecture/transactions/transactions-overview/#hybrid-time-as-an-mvcc-timestamp)
- [Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) - Lamport's foundational work
- [Spanner: Google's Globally-Distributed Database](https://research.google/pubs/pub39966/) - TrueTime comparison