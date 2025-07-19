# Axiom 4: Concurrency

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Concurrent operations create states that don't exist in sequential execution.
  </div>
</div>

## Core Principle

```
Sequential: A then B = predictable
Concurrent: A while B = 
  - A then B
  - B then A  
  - A interleaved with B (multiple ways!)
  - Partial A, partial B, explosion of states
```

## 🎬 Failure Vignette: The Double-Booked Airplane Seat

```
Airline: Major US carrier
Date: December 23, 2019 (peak travel)
System: Seat assignment during online check-in

Race Condition:
T1 00:00.000: Alice views seat map, 14A shows available
T1 00:00.000: Bob views seat map, 14A shows available
T1 00:00.100: Alice clicks "Select 14A"
T1 00:00.150: Bob clicks "Select 14A"
T1 00:00.200: System checks 14A available for Alice ✓
T1 00:00.250: System checks 14A available for Bob ✓
T1 00:00.300: System assigns 14A to Alice
T1 00:00.350: System assigns 14A to Bob
T1 00:00.400: Database now shows Bob in 14A

At the gate:
- Both passengers have boarding passes for 14A
- Alice boards first, sits down
- Bob boards, confrontation ensues
- Flight delayed 40 minutes for resolution

Fix: Distributed lock with atomic compare-and-swap
```

## Concurrency Control Mechanisms

```
1. PESSIMISTIC LOCKING
   BEGIN;
   SELECT * FROM seats WHERE id = '14A' FOR UPDATE;
   -- Lock held until commit
   UPDATE seats SET passenger = 'Alice' WHERE id = '14A';
   COMMIT;
   
   Pro: Guarantees consistency
   Con: Reduces concurrency, can deadlock

2. OPTIMISTIC LOCKING (CAS)
   SELECT version FROM seats WHERE id = '14A'; -- Returns v1
   UPDATE seats 
   SET passenger = 'Alice', version = v2
   WHERE id = '14A' AND version = v1;
   -- Check affected rows, retry if 0
   
   Pro: Better concurrency
   Con: Retry storms under contention

3. MVCC (Multi-Version Concurrency)
   Each transaction sees consistent snapshot
   Conflicts detected at commit time
   
   Pro: Readers don't block writers
   Con: Complex implementation
```

## 🎯 Decision Tree: Lock vs CAS vs Queue

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

## Concurrency Bugs Taxonomy

1. **Race Condition**: Outcome depends on timing
2. **Deadlock**: Circular wait for resources
3. **Livelock**: Threads actively doing nothing
4. **Starvation**: Some threads never get resources
5. **ABA Problem**: Value changes A→B→A between checks
6. **Priority Inversion**: Low priority blocks high

## 🔧 Try This: Demonstrate a Race

```python
import threading
import time

# Shared counter without protection
counter = 0

def increment():
    global counter
    for _ in range(1000000):
        temp = counter
        # Simulate some work
        temp = temp + 1
        counter = temp

# Run two threads
t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)

t1.start(); t2.start()
t1.join(); t2.join()

print(f"Counter: {counter}")  # Should be 2,000,000
print(f"Lost updates: {2000000 - counter}")
```

## Space-Time Diagram & Vector Clock Intro

### Visual Representation of Distributed Time

```
Process A  ─────●─────────●───────────●────→ time
                │ e1      │ e3        │ e5
                ↓         ↓           ↓
Process B  ───────────●───────●───────────→ time
                      │ e2    │ e4
                      
Happens-before: e1 → e2 → e3 → e4 → e5
Concurrent: (e1 || e4), (e3 || e4)
```

### Vector Clocks Explained

```
Each process maintains vector: [A_count, B_count, C_count]

Process A: [1,0,0] → sends message → [2,0,0]
Process B: [0,0,0] → receives → [2,1,0] → sends → [2,2,0]
Process C: [0,0,1] → receives → [2,2,1]

Comparing vectors:
[2,1,0] happens-before [2,2,1] ✓
[2,1,0] concurrent-with [1,0,2] ✓
```

**Practical Use**: Detect causality violations in distributed systems

## Cross-References

- → [Axiom 3: Partial Failure](../axiom3-failure/index.md): Concurrent failures
- → [Axiom 5: Coordination](../axiom5-coordination/index.md): Cost of preventing races
<!-- - → [ACID Properties](../../patterns/acid): Consistency guarantees -->

---

**Next**: [Axiom 5: Coordination →](../axiom5-coordination/index.md)

*"Concurrency is not parallelism; it's dealing with lots of things at once, not doing lots of things at once."*