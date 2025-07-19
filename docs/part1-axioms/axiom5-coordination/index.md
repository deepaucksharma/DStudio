# Axiom 5: Cost of Coordination

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Coordination is expensive in time, money, and complexity.
  </div>
</div>

## Core Principle

```
Total Cost = Communication Cost + Consensus Cost + Failure Handling Cost

Where:
- Communication = N × (N-1) × message_cost
- Consensus = rounds × round_trip_time × N
- Failure = retry_probability × recovery_cost
```

## 🎬 Failure Vignette: The $2M Two-Phase Commit

```
Company: Global financial services
Scenario: Cross-region transaction coordination
Architecture: 2PC across 5 data centers

Per Transaction Cost:
- Singapore ↔ London: 170ms RTT
- London ↔ New York: 70ms RTT  
- New York ↔ SF: 65ms RTT
- SF ↔ Tokyo: 100ms RTT
- Tokyo ↔ Singapore: 75ms RTT

2PC Phases:
1. Prepare: Coordinator → All (parallel): 170ms
2. Vote collection: All → Coordinator: 170ms
3. Commit: Coordinator → All: 170ms
Total: 510ms minimum per transaction

Monthly volume: 100M transactions
Time cost: 510ms × 100M = 14,000 hours of coordination
AWS cross-region traffic: $0.02/GB
Message size: 1KB × 3 phases × 5 regions = 15KB
Monthly bill: 15KB × 100M × $0.02 = $30M

Actual bill (with retries, monitoring): $2M/month

Solution: Eventual consistency with regional aggregation
New cost: $50K/month (40x reduction)
```

## Coordination Patterns Ranked by Cost

```
Pattern              Time Cost    Money Cost    Complexity
-------              ---------    ----------    ----------
No coordination      0            $0            Simple
Gossip protocol      O(log N)     Low           Medium
Leader election      O(1) amort   Medium        Medium
Quorum (majority)    O(1)         Medium        Medium
2PC                  O(N)         High          High
3PC                  O(N)         Very High     Very High
Paxos/Raft          O(1) amort   Medium        High
Byzantine (PBFT)     O(N²)        Extreme       Extreme
```

## 🎯 Decision Framework: Coordination Necessity

```
Do you REALLY need coordination?
├─ Can you tolerate inconsistency?
│  └─ YES → Use eventual consistency
├─ Can you partition the problem?
│  └─ YES → Coordinate within partitions only
├─ Can you use a single writer?
│  └─ YES → No coordination needed
├─ Can you use conflict-free data types?
│  └─ YES → Merge without coordination
└─ NO to all → Accept the coordination cost
              └─ Choose cheapest sufficient protocol
```

## The Hidden Costs

1. **Developer Time**: Complex protocols = bugs
2. **Operational**: More moving parts = more failures  
3. **Latency**: Every round trip adds delay
4. **Availability**: More participants = lower availability
5. **Debugging**: Distributed traces are expensive

## 🔧 Try This: Measure Coordination Overhead

```python
import time
import threading
from queue import Queue

def no_coordination(n_workers):
    """Workers process independently"""
    def worker():
        total = sum(range(1000000))
    
    threads = [threading.Thread(target=worker) 
               for _ in range(n_workers)]
    start = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    return time.time() - start

def with_coordination(n_workers):
    """Workers coordinate through queue"""
    queue = Queue()
    results = Queue()
    
    def worker():
        while True:
            item = queue.get()
            if item is None: break
            results.put(sum(range(item, item + 1000)))
            queue.task_done()
    
    threads = [threading.Thread(target=worker) 
               for _ in range(n_workers)]
    for t in threads: t.start()
    
    start = time.time()
    for i in range(0, 1000000, 1000):
        queue.put(i)
    
    queue.join()
    for _ in range(n_workers):
        queue.put(None)
    for t in threads: t.join()
    
    return time.time() - start

# Compare
workers = 4
t1 = no_coordination(workers)
t2 = with_coordination(workers)
print(f"No coordination: {t1:.3f}s")
print(f"With coordination: {t2:.3f}s")  
print(f"Overhead: {(t2/t1 - 1)*100:.1f}%")
```

## Coordination Estimator Cheat-Table

### Quick Reference Cost Calculator

```
Scenario                          Formula                      Example (5 nodes, 50ms RTT)
--------                          -------                      -------------------------
Async fire-and-forget            0                            0ms
Quorum read (majority)           RTT × ceil(N/2)              50ms × 3 = 150ms
Quorum write                     RTT × ceil(N/2)              150ms
Read-your-writes                 RTT × write_replicas         50ms × 3 = 150ms
Linearizable read                RTT × N (worst case)         50ms × 5 = 250ms
2PC transaction                  3 × RTT × N                  3 × 50ms × 5 = 750ms
Paxos/Raft (normal)             2 × RTT                      100ms
Paxos/Raft (leader change)      4 × RTT + election_timeout   200ms + 150ms = 350ms
Chain replication               RTT × N (sequential)          250ms
Byzantine consensus             O(N²) messages                25 × 50ms = 1250ms
```

### Cost Multipliers

- Retries: × (1 + retry_rate)
- Failures: + (failure_rate × detection_time)
- Monitoring: × 1.1 (10% overhead typical)
- Encryption: × 1.05 (TLS overhead)
- Compression: × 0.8 (if payload > 1KB)

## Cross-References

- → [Axiom 1: Latency](../axiom1-latency/index.md): Physical limits on coordination
- → [Axiom 4: Concurrency](../axiom4-concurrency/index.md): Why coordination is needed
<!-- - → [Consensus Protocols](../../patterns/consensus): Implementation patterns -->

---

**Next**: [Axiom 6: Observability →](../axiom6-observability/index.md)

*"The cost of coordination is the tax you pay for distributed systems."*