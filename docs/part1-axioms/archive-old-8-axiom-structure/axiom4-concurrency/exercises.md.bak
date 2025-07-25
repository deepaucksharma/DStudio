---
title: "Axiom 4 Exercises: Master Concurrent Thinking"
description: "Hands-on labs to build your intuition for race conditions, deadlocks, and distributed coordination. Learn to think concurrently through practical exercises."
type: axiom
difficulty: intermediate
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure, axiom4-concurrency]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](../../introduction/index.md) → [Part I: Axioms](../index.md) → [Axiom 4](index.md) → **Concurrency Exercises**

# Concurrency Exercises

**Master the art of juggling distributed timelines through hands-on practice**

---

## 🧪 Hands-On Labs

### Lab 1: Race Condition Hunting

**Find and fix race conditions in real-world scenarios**

#### Exercise 1.1: The Banking Bug

```python
import threading
import time
import random

# BUGGY CODE - Find the race condition!
class BuggyBank:
    def __init__(self):
        self.accounts = {
            'alice': 1000,
            'bob': 1000,
            'charlie': 1000
        }
        self.transaction_log = []
        
    def transfer(self, from_acc, to_acc, amount):
        # Check balance
        if self.accounts[from_acc] >= amount:
            # Simulate processing delay
            time.sleep(0.001)
            
            # Deduct from sender
            self.accounts[from_acc] -= amount
            
            # Another delay (network, processing)
            time.sleep(0.001)
            
            # Add to receiver
            self.accounts[to_acc] += amount
            
            # Log transaction
            self.transaction_log.append({
                'from': from_acc,
                'to': to_acc,
                'amount': amount,
                'timestamp': time.time()
            })
            return True
        return False
    
    def get_total_money(self):
        return sum(self.accounts.values())

# Your task: Run this stress test and find the bug
def stress_test_bank():
    bank = BuggyBank()
    initial_total = bank.get_total_money()
    print(f"Initial total: ${initial_total}")
    
    def random_transfers():
        for _ in range(100):
            accounts = list(bank.accounts.keys())
            from_acc = random.choice(accounts)
            to_acc = random.choice([a for a in accounts if a != from_acc])
            amount = random.randint(1, 100)
            bank.transfer(from_acc, to_acc, amount)
    
    # Launch multiple threads
    threads = []
    for _ in range(10):
        t = threading.Thread(target=random_transfers)
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    final_total = bank.get_total_money()
    print(f"Final total: ${final_total}")
    print(f"Money {'LOST' if final_total < initial_total else 'CREATED'}: ${abs(final_total - initial_total)}")
    
    # Analyze the damage
    return bank

# TODO: Implement these fixes
class FixedBank:
    """Implement at least 3 different concurrency control strategies:
    1. Coarse-grained locking (one lock for all accounts)
    2. Fine-grained locking (one lock per account)
    3. Optimistic concurrency control
    
    Compare their performance!
    """
    pass
```

#### Exercise 1.2: The Inventory Nightmare

```python
# E-commerce inventory system with race conditions
class InventorySystem:
    def __init__(self):
        self.products = {
            'laptop': {'stock': 50, 'reserved': 0},
            'mouse': {'stock': 200, 'reserved': 0},
            'keyboard': {'stock': 150, 'reserved': 0}
        }
        
    def check_availability(self, product, quantity):
        item = self.products[product]
        available = item['stock'] - item['reserved']
        return available >= quantity
    
    def reserve_item(self, product, quantity):
        # RACE CONDITION: Check and reserve are not atomic!
        if self.check_availability(product, quantity):
            time.sleep(0.001)  # Simulate API call
            self.products[product]['reserved'] += quantity
            return True
        return False
    
    def purchase_item(self, product, quantity):
        item = self.products[product]
        if item['reserved'] >= quantity:
            item['stock'] -= quantity
            item['reserved'] -= quantity
            return True
        return False

# Challenge: Create a test that demonstrates overselling
# Then implement a fix using different strategies:
# 1. Pessimistic locking
# 2. Optimistic locking with version numbers
# 3. Compare-and-swap operations
```

---

### Lab 2: Distributed Locking Olympics

**Compare different locking strategies under various conditions**

#### Exercise 2.1: Lock Performance Benchmark

```python
import time
import threading
import multiprocessing
from abc import ABC, abstractmethod

class LockStrategy(ABC):
    @abstractmethod
    def acquire(self, resource_id):
        pass
    
    @abstractmethod
    def release(self, resource_id):
        pass

class PessimisticLock(LockStrategy):
    def __init__(self):
        self.locks = {}
        self.lock_creation_lock = threading.Lock()
        
    def acquire(self, resource_id):
        with self.lock_creation_lock:
            if resource_id not in self.locks:
                self.locks[resource_id] = threading.Lock()
        
        self.locks[resource_id].acquire()
        
    def release(self, resource_id):
        self.locks[resource_id].release()

class OptimisticLock(LockStrategy):
    def __init__(self):
        self.versions = {}
        self.lock = threading.Lock()
        
    def acquire(self, resource_id):
        with self.lock:
            if resource_id not in self.versions:
                self.versions[resource_id] = 0
            return self.versions[resource_id]
    
    def try_update(self, resource_id, expected_version, new_value):
        with self.lock:
            if self.versions.get(resource_id, 0) == expected_version:
                self.versions[resource_id] += 1
                return True
            return False

# Your task: Implement and benchmark these scenarios
class LockingBenchmark:
    def __init__(self, strategy: LockStrategy):
        self.strategy = strategy
        self.operations_completed = 0
        
    def run_benchmark(self, num_threads, num_operations, contention_level):
        """
        Benchmark different contention scenarios:
        - Low contention (100 resources, 10 threads)
        - Medium contention (10 resources, 10 threads)
        - High contention (1 resource, 10 threads)
        """
        # TODO: Implement the benchmark
        # Measure: throughput, latency distribution, fairness
        pass

# Scenarios to test:
scenarios = [
    {"name": "Low Contention", "resources": 100, "threads": 10},
    {"name": "Medium Contention", "resources": 10, "threads": 10},
    {"name": "High Contention", "resources": 1, "threads": 10},
    {"name": "Read Heavy", "read_ratio": 0.9, "threads": 20},
    {"name": "Write Heavy", "read_ratio": 0.1, "threads": 20}
]
```

#### Exercise 2.2: Distributed Lock Manager

```python
import redis
import time
import uuid
from contextlib import contextmanager

class DistributedLockManager:
    """Build a production-ready distributed lock manager"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.owned_locks = {}  # lock_name -> (identifier, expiry)
        
    @contextmanager
    def lock(self, name, timeout=10, blocking=True, blocking_timeout=None):
        """
        TODO: Implement a distributed lock with:
        1. Auto-renewal for long-running operations
        2. Deadlock detection
        3. Lock queuing with fairness
        4. Monitoring and metrics
        """
        acquired = self.acquire(name, timeout, blocking, blocking_timeout)
        try:
            yield acquired
        finally:
            if acquired:
                self.release(name)
    
    def acquire(self, name, timeout, blocking, blocking_timeout):
        # TODO: Implement acquisition logic
        pass
    
    def release(self, name):
        # TODO: Implement safe release
        pass
    
    def extend(self, name, additional_timeout):
        """Extend lock timeout for long operations"""
        # TODO: Implement lock extension
        pass

# Test scenarios:
class DistributedLockTests:
    def test_mutual_exclusion(self):
        """Verify only one client holds lock at a time"""
        pass
    
    def test_lock_expiry(self):
        """Verify locks expire and can be reacquired"""
        pass
    
    def test_owner_only_release(self):
        """Verify only lock owner can release"""
        pass
    
    def test_network_partition(self):
        """Test behavior during network splits"""
        pass
```

---

### Lab 3: Vector Clock Workshop

**Build a distributed version control system using vector clocks**

```python
from typing import Dict, List, Tuple, Optional
import json

class VectorClock:
    def __init__(self, node_id: str, initial_clock: Optional[Dict[str, int]] = None):
        self.node_id = node_id
        self.clock = initial_clock or {}
        
    def increment(self):
        """Increment local component"""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
        
    def update(self, other_clock: Dict[str, int]):
        """Update with received clock"""
        for node, timestamp in other_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), timestamp)
        self.increment()
        
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if self happens-before other"""
        if self.clock == other.clock:
            return False
            
        for node in set(self.clock.keys()) | set(other.clock.keys()):
            if self.clock.get(node, 0) > other.clock.get(node, 0):
                return False
        return True
        
    def concurrent_with(self, other: 'VectorClock') -> bool:
        """Check if events are concurrent"""
        return not self.happens_before(other) and not other.happens_before(self)

# Exercise: Build a distributed document editor
class DistributedDocument:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id)
        self.operations = []  # List of (vector_clock, operation)
        self.document = ""
        
    def insert(self, position: int, text: str):
        """Insert text at position"""
        self.vector_clock.increment()
        operation = {
            'type': 'insert',
            'position': position,
            'text': text,
            'clock': self.vector_clock.clock.copy()
        }
        self.apply_operation(operation)
        return operation
        
    def delete(self, position: int, length: int):
        """Delete text at position"""
        # TODO: Implement delete operation
        pass
        
    def receive_operation(self, operation: dict):
        """Receive and merge remote operation"""
        # TODO: Implement CRDT merge logic
        # Handle concurrent operations
        # Ensure convergence
        pass
        
    def apply_operation(self, operation: dict):
        """Apply operation to document"""
        # TODO: Transform operations if needed
        pass

# Challenge: Implement these test cases
class VectorClockTests:
    def test_concurrent_edits(self):
        """Test document convergence with concurrent edits"""
        doc1 = DistributedDocument("node1")
        doc2 = DistributedDocument("node2")
        doc3 = DistributedDocument("node3")
        
        # Simulate concurrent edits
        op1 = doc1.insert(0, "Hello ")
        op2 = doc2.insert(0, "World")
        op3 = doc3.insert(0, "!")
        
        # Exchange operations
        doc1.receive_operation(op2)
        doc1.receive_operation(op3)
        doc2.receive_operation(op1)
        doc2.receive_operation(op3)
        doc3.receive_operation(op1)
        doc3.receive_operation(op2)
        
        # Verify convergence
        assert doc1.document == doc2.document == doc3.document
```

---

## 💪 Challenge Problems

### Challenge 1: Build a Lock-Free Data Structure

```python
import threading
from typing import Optional, Any

class LockFreeStack:
    """Implement a lock-free stack using compare-and-swap"""
    
    class Node:
        def __init__(self, value: Any, next_node: Optional['Node'] = None):
            self.value = value
            self.next = next_node
    
    def __init__(self):
        self._top = None
        
    def push(self, value: Any):
        """Push value onto stack without locks"""
        # TODO: Implement using CAS
        # Handle the ABA problem!
        pass
        
    def pop(self) -> Optional[Any]:
        """Pop value from stack without locks"""
        # TODO: Implement using CAS
        pass

# Bonus: Implement a lock-free queue
class LockFreeQueue:
    """Michael & Scott lock-free queue"""
    # TODO: This is significantly harder!
    pass
```

### Challenge 2: Deadlock-Free Dining Philosophers

```python
import threading
import time
import random

class DiningPhilosophers:
    """Solve the classic dining philosophers problem"""
    
    def __init__(self, num_philosophers: int = 5):
        self.num_philosophers = num_philosophers
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.eating_count = [0] * num_philosophers
        self.thinking_count = [0] * num_philosophers
        self.hungry_count = [0] * num_philosophers
        
    def philosopher(self, philosopher_id: int):
        """Philosopher lifecycle: think -> hungry -> eat -> repeat"""
        # TODO: Implement a deadlock-free solution
        # Options:
        # 1. Resource hierarchy (always pick up lower-numbered fork first)
        # 2. Arbitrator solution (waiter)
        # 3. Chandy/Misra solution (clean/dirty forks)
        # 4. Limit concurrent diners
        pass
    
    def get_stats(self):
        """Return fairness metrics"""
        return {
            'total_meals': sum(self.eating_count),
            'starvation_index': max(self.eating_count) - min(self.eating_count),
            'efficiency': sum(self.eating_count) / sum(self.hungry_count)
        }

# Test your implementation
def test_dining_philosophers():
    table = DiningPhilosophers(5)
    
    # Run for 10 seconds
    threads = []
    for i in range(5):
        t = threading.Thread(target=table.philosopher, args=(i,))
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(10)
    
    stats = table.get_stats()
    print(f"Fairness test: {stats}")
    
    # Good solution should have:
    # - No deadlocks (program doesn't hang)
    # - Low starvation index (< 10% of total meals)
    # - High efficiency (> 40%)
```

### Challenge 3: Distributed Consensus Implementation

```python
import asyncio
import random
from enum import Enum
from typing import List, Optional

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"

class RaftNode:
    """Simplified Raft consensus implementation"""
    
    def __init__(self, node_id: int, peers: List[int]):
        self.node_id = node_id
        self.peers = peers
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        
    async def election_timeout(self):
        """Start election when timeout expires"""
        # TODO: Implement leader election
        # 1. Increment term
        # 2. Vote for self
        # 3. Send RequestVote to all peers
        # 4. Become leader if majority votes
        pass
        
    async def append_entries(self, entries, leader_term):
        """Handle AppendEntries from leader"""
        # TODO: Implement log replication
        # 1. Verify term
        # 2. Check log consistency
        # 3. Append new entries
        # 4. Update commit index
        pass
        
    async def request_vote(self, candidate_id, candidate_term):
        """Handle vote request"""
        # TODO: Implement voting logic
        # 1. Check term
        # 2. Check if already voted
        # 3. Check log up-to-date
        # 4. Grant or deny vote
        pass

# Build a test cluster
class RaftCluster:
    def __init__(self, num_nodes: int = 5):
        self.nodes = [RaftNode(i, list(range(num_nodes))) for i in range(num_nodes)]
        
    async def simulate_network_partition(self):
        """Test consensus during network partition"""
        # TODO: Partition nodes and verify:
        # 1. Minority partition cannot elect leader
        # 2. Majority partition elects new leader
        # 3. System recovers when partition heals
        pass
```

---

## 🤔 Thought Experiments

### Experiment 1: The Time-Traveling Database

```yaml
Scenario: Multi-Master Replication Across Continents

Setup:
  - 3 database masters: NYC, London, Tokyo
  - Each can accept writes
  - Replication lag: 50-200ms
  - Clock skew: up to 5 seconds

Question 1: Concurrent Updates
  Alice (NYC): UPDATE users SET status='active' WHERE id=123 at T1
  Bob (Tokyo): UPDATE users SET status='deleted' WHERE id=123 at T1+100ms
  
  But due to clock skew, Tokyo thinks its update happened first!
  
  How do you resolve this?
  a) Last-writer-wins (wall clock)
  b) Last-writer-wins (logical clock) 
  c) Vector clocks
  d) Conflict-free replicated data types (CRDTs)
  
  What are the trade-offs of each approach?

Question 2: The Birthday Paradox
  You use UUIDs to avoid ID conflicts.
  With 1 million records/day across 3 regions:
  - What's the probability of collision?
  - When should you worry?
  - How would you handle a collision?

Question 3: Causality Violations  
  1. User creates account (Tokyo)
  2. User uploads photo (London, 50ms later)
  3. User deletes account (NYC, 100ms later)
  
  Due to replication lag, London sees:
  - Delete account (arrives first)
  - Create account (arrives second)
  - Now there's an orphaned photo!
  
  Design a system that preserves causality.
```

### Experiment 2: The Distributed Counter Conundrum

```python
# Design challenge: Accurate distributed counting

"""
Requirements:
- Count events across 1000 servers
- Handle 1M events/second total
- Accuracy within 0.1%
- Real-time results (< 1 second delay)
- Survive server failures

Approach comparison:

1. Centralized Counter
   Pros: Simple, accurate
   Cons: Single point of failure, bottleneck
   
2. Sharded Counters
   Pros: Scales well
   Cons: How to query total? Rebalancing?
   
3. Gossip Protocol
   Pros: Fault tolerant
   Cons: Eventual consistency, bandwidth
   
4. CRDT Counter
   Pros: Conflict-free
   Cons: Grows unbounded, overhead
   
5. Probabilistic (HyperLogLog)
   Pros: Fixed memory
   Cons: Approximate only

Which would you choose and why?
How would you handle these failure modes:
- Network partition
- Clock skew  
- Byzantine failures
- Cascading failures
"""

# Implement your solution here
class DistributedCounter:
    pass
```

### Experiment 3: The Blockchain Ordering Problem

```yaml
Scenario: Decentralized Exchange Order Book

Problem:
  - No central authority
  - Orders from around the world
  - Must establish global order
  - Fairness is critical (no front-running)
  
Constraints:
  - Network delay: 10-500ms
  - Block time: 10 seconds
  - Throughput: 10,000 orders/second
  
Questions:
  
  1. Order Submission:
     Alice: BUY 1 BTC @ $50,000 (sent at T+0)
     Bob: SELL 1 BTC @ $49,999 (sent at T+0)
     
     Alice's order reaches miner M1 first
     Bob's order reaches miner M2 first
     
     Who gets the better price?
     
  2. Time Fairness:
     How do you prevent miners from:
     - Reordering transactions for profit
     - Inserting their own transactions first
     - Delaying certain transactions
     
  3. Flash Boys Problem:
     High-frequency traders have faster connections
     They see orders and race to profit
     
     Design mechanisms to level the playing field.
```

---

## 🔬 Research Projects

### Project 1: Concurrent Data Structure Library

```python
"""
Build a production-ready concurrent data structure library

Requirements:
1. Thread-safe
2. High performance
3. Composable
4. Deadlock-free

Data structures to implement:
- ConcurrentHashMap
- ConcurrentSkipList  
- ConcurrentQueue
- ConcurrentBloomFilter

Benchmark against:
- Python's threading.Lock
- multiprocessing.Queue
- Redis
- Your own lock-free versions
"""

class ConcurrentHashMap:
    """High-performance concurrent hash map"""
    # TODO: Implement with:
    # - Segmented locking
    # - Lock-free reads
    # - Atomic resize
    # - Memory ordering guarantees
    pass
```

### Project 2: Distributed Lock Visualizer

```python
"""
Build a web-based visualizer for distributed locking

Features:
1. Show lock acquisition/release in real-time
2. Detect and highlight deadlocks
3. Display wait queues
4. Performance metrics
5. Time-travel debugging

Architecture:
- Backend: Capture lock events
- Stream processing: Analyze patterns
- Frontend: D3.js visualization
- Storage: Time-series database
"""
```

### Project 3: Chaos Testing Framework

```python
"""
Build a framework to test concurrent code

Features:
1. Deterministic thread scheduling
2. Systematic exploration of interleavings
3. Race condition detection
4. Deadlock detection
5. Performance regression testing

Example usage:

@chaos_test(threads=5, iterations=1000)
def test_concurrent_map():
    m = ConcurrentMap()
    
    @concurrent_operation
    def writer(thread_id):
        for i in range(100):
            m.put(f"key_{thread_id}_{i}", i)
    
    @concurrent_operation
    def reader(thread_id):
        for i in range(100):
            m.get(f"key_{thread_id}_{i}")
    
    @invariant
    def no_lost_writes():
        # Verify all writes are visible
        pass
"""
```

---

## 📊 Performance Analysis Lab

### Measure the Cost of Concurrency

```python
# Benchmark different synchronization primitives

import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

class ConcurrencyBenchmark:
    def __init__(self):
        self.results = {}
        
    def benchmark_lock_overhead(self):
        """Measure the cost of acquiring/releasing locks"""
        # TODO: Benchmark:
        # - Uncontended lock
        # - Contended lock (2, 4, 8, 16 threads)
        # - Reader-writer lock
        # - Spinlock vs mutex
        pass
        
    def benchmark_atomic_operations(self):
        """Compare atomic vs locked operations"""
        # TODO: Benchmark:
        # - Atomic increment
        # - Compare-and-swap
        # - Memory barriers
        # - Lock-free vs locked counter
        pass
        
    def benchmark_message_passing(self):
        """Measure inter-thread communication cost"""
        # TODO: Benchmark:
        # - Queue.put/get
        # - Pipe communication  
        # - Shared memory
        # - Domain sockets
        pass

# Visualize results
def plot_scalability(benchmark_results):
    """
    Create plots showing:
    1. Throughput vs thread count
    2. Latency distribution
    3. Cache misses vs contention
    4. Amdahl's law vs reality
    """
    pass
```

---

## 🎯 Final Challenge: Build a Distributed Game

```python
"""
Multiplayer Distributed Tic-Tac-Toe

Requirements:
1. Support 3+ players (3D tic-tac-toe)
2. Players can be on different continents
3. Handle network failures gracefully
4. Prevent cheating
5. Ensure all players see consistent state
6. Sub-second move latency

Challenges to solve:
- Move ordering
- Conflict resolution  
- State synchronization
- Disconnection handling
- Fairness (no player advantage)

Extensions:
- Support 1000+ concurrent games
- Add AI players
- Tournament mode
- Replay system
"""

class DistributedTicTacToe:
    # Your implementation here
    pass
```

---

## 🏆 Skills Assessment

Rate your mastery (1-5):
- [ ] Can identify race conditions
- [ ] Understand happens-before relationships
- [ ] Can implement mutex from scratch
- [ ] Know when to use optimistic vs pessimistic locking
- [ ] Can debug deadlocks
- [ ] Understand memory ordering
- [ ] Can implement lock-free algorithms
- [ ] Can reason about distributed state

**Score: ___/40** (32+ = Concurrency Master, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 5: Coordination](../axiom5-coordination/index.md)

**Related**: [Distributed Lock](../../patterns/distributed-lock.md) • [Leader Election](../../patterns/leader-election.md) • [Saga](../../patterns/saga.md) • [Consensus](../../patterns/consensus.md)

## References

¹ [The Art of Multiprocessor Programming - Maurice Herlihy & Nir Shavit](https://dl.acm.org/doi/10.5555/2385452)

² [Time, Clocks, and the Ordering of Events in a Distributed System - Leslie Lamport](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) 

³ [The Dining Philosophers Problem - E.W. Dijkstra](https://www.cs.utexas.edu/users/EWD/transcriptions/EWD03xx/EWD310.html)

⁴ [In Search of an Understandable Consensus Algorithm (Raft) - Ongaro & Ousterhout](https://raft.github.io/raft.pdf)

⁵ [Conflict-free Replicated Data Types - Shapiro et al.](https://hal.inria.fr/inria-00609399/document)
