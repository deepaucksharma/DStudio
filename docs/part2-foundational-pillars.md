# PART II: Foundational Pillars & Modern Extensions

!!! info "Prerequisites"
    This section builds upon the 8 fundamental axioms from Part I. If you haven't read it yet:
    
    **[← Part I: The 8 Axioms](distributed-systems-book.md)**

## Page 21: Why Pillars?

!!! target "Learning Objective"
    Understand how axioms combine to create fundamental architectural patterns.

<div class="axiom-box">

**The Emergence Principle**:

```
Axioms = Constraints (what you cannot change)
Pillars = Patterns (how you work within constraints)

Just as chemistry emerges from physics, and biology from chemistry,
distributed system patterns emerge from fundamental constraints.
```

</div>

### The Three Core + Two Extension Model

<div class="pillar-architecture">

```
                    AXIOMS (Constraints)
                           ↓
    ┌────────────────────────────────────────────┐
    │            CORE PILLARS                     │
    │                                             │
    │  Work         State          Truth         │
    │  Distribution Distribution   Distribution  │
    │     ↑            ↑              ↑          │
    │  Capacity    Capacity      Coordination   │
    │  Latency     Latency       Concurrency    │
    │              Failure       Partial Fail    │
    └────────────────────────────────────────────┘
                           ↓
    ┌────────────────────────────────────────────┐
    │         EXTENSION PILLARS                   │
    │                                             │
    │     Control           Intelligence         │
    │     Distribution      Distribution         │
    │         ↑                   ↑              │
    │    Human Interface    All Axioms +        │
    │    Observability      Feedback Loops       │
    └────────────────────────────────────────────┘
```

</div>

### Why These Five?

**Coverage Analysis**:

| System Aspect | Covered By Pillar |
|---------------|-------------------|
| Request handling | → Work Distribution |
| Data persistence | → State Distribution |
| Consistency | → Truth Distribution |
| Operations | → Control Distribution |
| Adaptation | → Intelligence Distribution |

✅ **Completeness check**: All aspects covered  
✅ **Minimality check**: No redundant pillars  
✅ **Orthogonality check**: Pillars independent

### Historical Evolution

<div class="timeline-box">

```
1960s: Mainframes (no distribution needed)
1970s: Client-server (Work distribution emerges)
1980s: Databases (State distribution emerges)
1990s: Internet (Truth distribution critical)
2000s: Web-scale (Control distribution needed)
2010s: Cloud (All pillars mature)
2020s: AI/Edge (Intelligence distribution emerges)
```

</div>

### The Pillar Interaction Model

```
Work × State = Stateless vs Stateful services
Work × Truth = Consistency models for compute
State × Truth = CAP theorem territory
Control × All = Orchestration patterns
Intelligence × All = Self-healing systems
```

<div class="mental-model-box">

**Mental Model: The Distributed Systems House**

```
     Intelligence (Roof - Protects/Adapts)
           /                    \
    Control                    Control
    (Walls)                    (Walls)
      |                          |
Work--+--------State--------+---Work
      |                     |
      |        Truth        |
      |      (Foundation)   |
      +---------------------+
```

</div>

---

## Page 22: PILLAR I – Distribution of Work

!!! target "Learning Objective"
    Master the art of spreading computation without spreading complexity.

<div class="axiom-box">

**First Principle of Work Distribution**:

```
Work should flow to where it can be processed most efficiently,
considering:
- Physical location (latency)
- Available capacity
- Required resources
- Failure domains
```

</div>

### The Statelessness Imperative

<div class="comparison-box">

=== "Stateless Service Properties"

    ✅ Any request to any instance  
    ✅ Instances interchangeable  
    ✅ Horizontal scaling trivial  
    ✅ Failure recovery simple  
    ✅ Load balancing easy

=== "Stateful Service Properties"

    ❌ Requests tied to instances  
    ❌ Complex scaling (resharding)  
    ❌ Failure means data loss  
    ❌ Load balancing tricky  
    ❌ Coordination required

</div>

### Work Distribution Patterns Hierarchy

<div class="pattern-hierarchy">

```
Level 1: Random Distribution
- Round-robin
- Random selection
- DNS load balancing
Efficiency: 60-70%

Level 2: Smart Distribution
- Least connections
- Weighted round-robin
- Response time based
Efficiency: 70-85%

Level 3: Affinity-Based
- Session affinity
- Consistent hashing
- Geographic routing
Efficiency: 80-90%

Level 4: Adaptive Distribution
- Predictive routing
- Cost-aware placement
- SLO-based routing
Efficiency: 90-95%
```

</div>

### The Autoscaling Mathematics

<div class="formula-box">

```
Optimal Instance Count = ceil(
    (Arrival Rate × Processing Time) / 
    (Target Utilization)
)

Example:
- Arrival: 1000 requests/second
- Processing: 100ms/request
- Target utilization: 70%

Instances = ceil((1000 × 0.1) / 0.7) = ceil(142.8) = 143
```

</div>

### Autoscaling Response Curves

<div class="graph-box">

```
Instances
    ↑
150 |            ┌─────────── (Overprovisioned)
    |          ╱
100 |        ╱─── (Ideal)
    |      ╱
 50 |    ╱╱ ← (Reactive scaling)
    |  ╱╱
  0 |╱________________________
    0   500   1000   1500  Load (req/s)
```

</div>

### Work Distribution Anti-Patterns

<div class="anti-pattern-box">

**1. Hot Shard Problem**:
```
Hash(UserID) % N can create:
- Celebrity user → overloaded shard
- Power law distribution → uneven load
Fix: Virtual shards, consistent hashing
```

**2. Thundering Herd**:
```
All instances start simultaneously:
- Cache empty → database overload
- Health checks → false failures
Fix: Staggered starts, cache priming
```

**3. Work Duplication**:
```
Multiple workers process same item:
- No coordination → wasted work
- Optimistic locking → conflict storms
Fix: Work stealing, leases
```

</div>

!!! example "🔧 Try This: Build a Work Stealer"

    ```python
    import time
    import random
    from multiprocessing import Process, Queue, Value

    class WorkStealer:
        def __init__(self, num_workers=4):
            self.work_queue = Queue()
            self.steal_queue = Queue()
            self.completed = Value('i', 0)
            self.workers = []
            
        def worker(self, worker_id, local_queue):
            while True:
                # Try local queue first
                if not local_queue.empty():
                    work = local_queue.get()
                # Try stealing if local empty
                elif not self.steal_queue.empty():
                    work = self.steal_queue.get()
                else:
                    time.sleep(0.01)
                    continue
                    
                if work is None:
                    break
                    
                # Simulate work
                time.sleep(random.uniform(0.01, 0.1))
                with self.completed.get_lock():
                    self.completed.value += 1
        
        def distribute_work(self, items):
            # Create local queues
            local_queues = [Queue() for _ in range(len(self.workers))]
            
            # Initial distribution
            for i, item in enumerate(items):
                if i < len(items) // 2:
                    # First half goes to workers
                    local_queues[i % len(self.workers)].put(item)
                else:
                    # Second half goes to steal queue
                    self.steal_queue.put(item)
            
            # Start workers
            for i, q in enumerate(local_queues):
                p = Process(target=self.worker, args=(i, q))
                p.start()
                self.workers.append(p)
            
            # Wait for completion
            start = time.time()
            while self.completed.value < len(items):
                time.sleep(0.1)
            
            # Cleanup
            for q in local_queues:
                q.put(None)
            for w in self.workers:
                w.join()
                
            return time.time() - start

    # Compare with and without work stealing
    stealer = WorkStealer()
    elapsed = stealer.distribute_work(list(range(100)))
    print(f"With work stealing: {elapsed:.2f}s")
    ```

---

## Page 23: Autoscaling & Back-Pressure

### The Control Theory of Autoscaling

<div class="control-diagram">

```
                     Target
                       ↓
Error = Target - Current
         ↓
    PID Controller
         ↓
Scale Decision = Kp×Error + Ki×∫Error + Kd×(dError/dt)
         ↓
    Add/Remove Instances
         ↓
    Measure Current ←────┘
```

</div>

### Autoscaling Strategies Compared

| Strategy | Response Time | Stability | Cost |
|----------|---------------|-----------|------|
| Reactive | Slow (minutes) | Good | Low |
| Predictive | Fast (seconds) | Medium | Medium |
| Scheduled | Instant | High | Medium |
| ML-based | Fast | Low-Med | High |

### Back-Pressure Mechanisms

<div class="mechanism-box">

**1. Token Bucket**:
```
Tokens added at fixed rate → [||||||||  ]
Request consumes token    → [|||||||   ]
No tokens = reject        → [          ] → 429 Error

Config:
- Bucket size: Burst capacity
- Refill rate: Sustained capacity
- Token cost: Per request or per byte
```

**2. Sliding Window**:
```
Time window: [===========]
              ↑         ↑
           10s ago    Now

Requests in window: 847/1000 allowed
New request: Check if under limit
```

**3. Adaptive Concurrency (BBR-style)**:
```
Gradient descent on concurrency limit:
1. Measure: RTT and throughput
2. Probe: Increase limit slightly
3. Observe: Did throughput increase?
4. Adjust: If latency spiked, back off

Finds optimal concurrency automatically!
```

</div>

!!! example "Real Implementation: Go Rate Limiter"

    ```go
    type RateLimiter struct {
        tokens    float64
        capacity  float64
        rate      float64
        lastRefill time.Time
        mu        sync.Mutex
    }

    func (rl *RateLimiter) Allow() bool {
        rl.mu.Lock()
        defer rl.mu.Unlock()
        
        // Refill tokens
        now := time.Now()
        elapsed := now.Sub(rl.lastRefill).Seconds()
        rl.tokens = min(rl.capacity, rl.tokens + elapsed*rl.rate)
        rl.lastRefill = now
        
        // Try to consume
        if rl.tokens >= 1.0 {
            rl.tokens--
            return true
        }
        return false
    }
    ```

### Back-Pressure Propagation

<div class="flow-diagram">

```
User → API Gateway → Service A → Service B → Database
  ↑        ↑            ↑           ↑          ↑
  └────────┴────────────┴───────────┴──────────┘
         Back-pressure flows upstream
```

</div>

!!! warning "Common Back-Pressure Mistakes"

    1. **No Timeout Coordination**: Upstream timeout < downstream
    2. **Buffer Bloat**: Queues too large, hide problems
    3. **Unfair Rejection**: No priority/fairness
    4. **No Gradient**: Binary accept/reject vs gradual

---

## Page 24: Work-Stealing Animation

### Visual Step-Through of Work Stealing

<div class="animation-box">

**Step 1: Initial State (Uneven Distribution)**
```
Worker 1: [████████████████] 16 tasks
Worker 2: [████] 4 tasks  
Worker 3: [██] 2 tasks
Worker 4: [ ] 0 tasks
```

**Step 2: Worker 4 Steals from Worker 1**
```
Worker 1: [████████] 8 tasks (stolen!)
Worker 2: [████] 4 tasks
Worker 3: [██] 2 tasks  
Worker 4: [████████] 8 tasks
```

**Step 3: Worker 3 Steals from Worker 1**
```
Worker 1: [████] 4 tasks
Worker 2: [████] 4 tasks
Worker 3: [██████] 6 tasks
Worker 4: [████████] 8 tasks
```

**Step 4: Balanced State**
```
Worker 1: [█████] 5 tasks
Worker 2: [█████] 5 tasks
Worker 3: [██████] 6 tasks
Worker 4: [██████] 6 tasks

Total time: 6 units (vs 16 without stealing)
```

</div>

### Work Stealing Decision Logic

<div class="decision-flow">

```
WORKER LOOP:
1. Check local queue
   ├─ Has work? → Process it
   └─ Empty? → Continue to 2

2. Check steal candidates
   ├─ Find busiest worker
   ├─ Steal half their queue
   └─ No candidates? → Sleep briefly

3. Stealing strategy
   ├─ Steal from back (LIFO) for cache locality
   ├─ Steal in batches to reduce contention
   └─ Exponential backoff on conflict
```

</div>

### Performance Comparison

<div class="comparison-chart">

```
Scenario: 1000 tasks, varying sizes

No Stealing:          Work Stealing:
Worker 1: ████████    Worker 1: ████
Worker 2: ██          Worker 2: ████  
Worker 3: ████        Worker 3: ████
Worker 4: ██████      Worker 4: ████

Time: 800ms           Time: 400ms
Efficiency: 50%       Efficiency: 95%
```

</div>

---

## Page 25: PILLAR II – Distribution of State

!!! target "Learning Objective"
    State is where distributed systems get hard; master the trade-offs.

### The State Distribution Trilemma

<div class="trilemma-diagram">

```
        Consistency
            / \
           /   \
          /     \
         /       \
    Availability  Partition Tolerance
    
Pick 2, but P is mandatory in distributed systems,
so really: Choose between C and A when partitioned
```

</div>

### State Distribution Strategies

<div class="strategy-cards">

=== "Partitioning (Sharding)"

    ```
    Data universe: [A-Z]
    ├─ Shard 1: [A-H]
    ├─ Shard 2: [I-P]  
    └─ Shard 3: [Q-Z]

    Pros: Linear scalability
    Cons: Cross-shard queries expensive
    When: Clear partition key exists
    ```

=== "Replication"

    ```
    Master: [Complete Dataset] ← Writes
       ↓ Async replication
    Replica 1: [Complete Dataset] ← Reads
    Replica 2: [Complete Dataset] ← Reads

    Pros: Read scalability, fault tolerance
    Cons: Write bottleneck, lag
    When: Read-heavy workloads
    ```

=== "Caching"

    ```
    Client → Cache → Database
             ↓   ↑
          [Hot Data]

    Pros: Massive read performance
    Cons: Consistency complexity
    When: Temporal locality exists
    ```

</div>

### State Consistency Spectrum

<div class="consistency-spectrum">

```
Strong ←──────────────────────────────→ Eventual
  │                                          │
Linearizable                            DNS
  │                                          │
Sequential                              S3
  │                                          │
Causal                                  DynamoDB
  │                                          │
FIFO                                    Cassandra

Cost: $$$$                            $
Latency: High                         Low
Availability: Lower                   Higher
```

</div>

<div class="failure-vignette">

**🎬 Real-World Example: Reddit's Sharding Journey**

```yaml
2010: Single PostgreSQL (100GB)
- Problem: CPU maxed, can't scale up more

2011: Functional sharding
- User data: DB1
- Posts: DB2  
- Comments: DB3
- Problem: Joins impossible

2012: Horizontal sharding
- Users: Shard by user_id % 16
- Posts: Shard by subreddit
- Problem: Hot subreddits (/r/funny)

2013: Virtual shards
- 1000 virtual shards → 16 physical
- Rebalance virtual → physical mapping
- Problem: Operational complexity

2015: Cassandra migration
- Eventually consistent
- Geographic distribution
- Trade-off: No transactions
```

</div>

### The Hidden Costs of State Distribution

<div class="cost-analysis">

```
1. COGNITIVE OVERHEAD
   Single DB: Simple mental model
   Distributed: Where is this data?

2. OPERATIONAL COMPLEXITY  
   Single DB: One backup, one failover
   Distributed: N backups, complex recovery

3. CONSISTENCY GYMNASTICS
   Single DB: ACID transactions
   Distributed: Sagas, compensation

4. DEBUGGING NIGHTMARE
   Single DB: One log to check
   Distributed: Correlation across N logs
```

</div>

!!! example "🔧 Try This: Consistent Hashing"

    ```python
    import hashlib
    import bisect

    class ConsistentHash:
        def __init__(self, nodes=None, virtual_nodes=150):
            self.nodes = nodes or []
            self.virtual_nodes = virtual_nodes
            self.ring = {}
            self._sorted_keys = []
            self._build_ring()
        
        def _hash(self, key):
            return int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        def _build_ring(self):
            self.ring = {}
            self._sorted_keys = []
            
            for node in self.nodes:
                for i in range(self.virtual_nodes):
                    virtual_key = f"{node}:{i}"
                    hash_value = self._hash(virtual_key)
                    self.ring[hash_value] = node
                    self._sorted_keys.append(hash_value)
            
            self._sorted_keys.sort()
        
        def add_node(self, node):
            self.nodes.append(node)
            self._build_ring()
        
        def remove_node(self, node):
            self.nodes.remove(node)
            self._build_ring()
        
        def get_node(self, key):
            if not self.ring:
                return None
            
            hash_value = self._hash(key)
            index = bisect.bisect_right(self._sorted_keys, hash_value)
            
            if index == len(self._sorted_keys):
                index = 0
                
            return self.ring[self._sorted_keys[index]]

    # Test distribution
    ch = ConsistentHash(['db1', 'db2', 'db3'])

    # Check distribution
    distribution = {}
    for i in range(10000):
        node = ch.get_node(f"user_{i}")
        distribution[node] = distribution.get(node, 0) + 1

    print("Distribution:", distribution)

    # Simulate node failure
    ch.remove_node('db2')
    moved = 0
    for i in range(10000):
        old_node = 'db2' if i % 3 == 1 else ch.get_node(f"user_{i}")
        new_node = ch.get_node(f"user_{i}")
        if old_node != new_node:
            moved += 1

    print(f"Keys moved: {moved}/10000 ({moved/100:.1f}%)")
    ```

---

## Page 26: Data-Modelling Matrix

### The Right Data Store for the Right Job

<div class="data-store-matrix">

| Use Case | Best Fit | Why |
|----------|----------|-----|
| User profiles | Document DB | Flexible schema |
| Financial ledger | RDBMS | ACID required |
| Time series | TSDB | Optimized storage |
| Shopping cart | Redis | Temporary, fast |
| Log search | Elasticsearch | Full-text search |
| Social graph | Graph DB | Relationship queries |
| Analytics | Column store | Aggregation optimized |
| Files | Object store | Cheap, scalable |

</div>

### Data Model Transformation Costs

<div class="transformation-matrix">

| From → To | Difficulty | Example |
|-----------|------------|---------|
| Relational → KV | Easy | User table → user:123 |
| Relational → Doc | Medium | Denormalize joins |
| Relational → Graph | Hard | Edges from FKs |
| Document → Relation | Hard | Normalize nested |
| Graph → Relational | Very Hard | Recursive queries |
| Any → Time Series | Easy | Add timestamp |

</div>

### Polyglot Persistence Decision Framework

<div class="decision-box">

```
START: What's your primary access pattern?
│
├─ Key lookup?
│  ├─ Needs persistence? → Redis with AOF
│  └─ Cache only? → Memcached
│
├─ Complex queries?
│  ├─ Transactions? → PostgreSQL
│  ├─ Analytics? → ClickHouse
│  └─ Search? → Elasticsearch
│
├─ Relationships?
│  ├─ Social graph? → Neo4j
│  └─ Hierarchical? → Document DB
│
├─ Time-based?
│  ├─ Metrics? → Prometheus
│  └─ Events? → Kafka + S3
│
└─ Large objects?
   ├─ Frequent access? → CDN
   └─ Archive? → Glacier
```

</div>

### Real-World Polyglot Example: E-commerce

<div class="polyglot-architecture">

| System Component | Data Store | Reasoning |
|------------------|------------|-----------|
| Product catalog | Elasticsearch | Full-text search |
| User profiles | DynamoDB | Fast lookup, global |
| Shopping cart | Redis | Session state |
| Order history | PostgreSQL | Transactions |
| Recommendations | Neo4j | Graph algorithms |
| Product images | S3 + CloudFront | Blob storage + CDN |
| Clickstream | Kinesis → S3 | Analytics pipeline |
| Metrics | Prometheus | Time-series |

</div>

---

## Page 27: PILLAR III – Distribution of Truth

!!! target "Learning Objective"
    In distributed systems, truth is negotiated, not declared.

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

</div>

### Consensus Algorithms Landscape

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

### Quorum Mathematics

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

### CAP Theorem Visualized

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

### Truth Coordination Patterns

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

<div class="failure-vignette">

**🎬 Real Incident: Split-Brain at Scale**

```yaml
Company: Major social network
Incident: Network partition splits datacenter

West Coast DC          East Coast DC
[Master thinks         [Master thinks
 it's primary]         it's primary]
     ↓                      ↓
Accepts writes         Accepts writes
     ↓                      ↓
User posts             User posts
diverge               diverge

Duration: 12 minutes
Impact: 
- 100K posts on each side
- Friends see different timelines
- Likes/comments on phantom posts

Resolution attempt #1: Last-write-wins
Problem: Angry users, "lost" posts

Resolution attempt #2: Merge everything
Problem: Duplicate posts, broken threads

Final resolution: 
- Show both versions with "conflict" banner
- Let users choose version to keep
- Took 3 weeks to fully resolve

Lesson: Some conflicts need human resolution
```

</div>

!!! example "🔧 Try This: Simple Raft Leader Election"

    ```python
    import random
    import time
    from enum import Enum

    class State(Enum):
        FOLLOWER = 1
        CANDIDATE = 2
        LEADER = 3

    class RaftNode:
        def __init__(self, node_id, all_nodes):
            self.id = node_id
            self.state = State.FOLLOWER
            self.term = 0
            self.voted_for = None
            self.leader = None
            self.all_nodes = all_nodes
            self.election_timeout = random.uniform(1.5, 3.0)
            self.last_heartbeat = time.time()
        
        def start_election(self):
            self.state = State.CANDIDATE
            self.term += 1
            self.voted_for = self.id
            votes = 1  # Vote for self
            
            print(f"Node {self.id} starting election for term {self.term}")
            
            # Request votes from others
            for node in self.all_nodes:
                if node.id != self.id:
                    if node.grant_vote(self.term, self.id):
                        votes += 1
            
            # Check if won
            if votes > len(self.all_nodes) // 2:
                self.become_leader()
            else:
                self.state = State.FOLLOWER
        
        def grant_vote(self, term, candidate_id):
            if term > self.term:
                self.term = term
                self.voted_for = None
            
            if self.voted_for is None:
                self.voted_for = candidate_id
                return True
            return False
        
        def become_leader(self):
            self.state = State.LEADER
            self.leader = self.id
            print(f"Node {self.id} became leader for term {self.term}")
            
            # Notify others
            for node in self.all_nodes:
                if node.id != self.id:
                    node.accept_leader(self.id, self.term)
        
        def accept_leader(self, leader_id, term):
            if term >= self.term:
                self.term = term
                self.state = State.FOLLOWER
                self.leader = leader_id
                self.last_heartbeat = time.time()
    ```

---

## Page 28: Consistency Dial Slider

### The Consistency Spectrum Interface

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

### Consistency Levels Explained

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

### Real-World Consistency Trade-offs

<div class="tradeoff-examples">

| System | Consistency Level | Trade-off |
|--------|------------------|-----------|
| YouTube View Counter | Eventual | Updates batched hourly<br>Accuracy for scale |
| Bank Balance | Strong | Every read sees all writes<br>Scale for correctness |
| Twitter Timeline | Causal | Replies after original tweets<br>Some ordering for speed |
| Shopping Cart | Session | User sees own updates<br>Global consistency for UX |

</div>

---

## Page 29: EXTENSION PILLAR IV – Control

!!! target "Learning Objective"
    Control planes are the nervous system of distributed systems.

### Control Plane vs Data Plane

<div class="plane-diagram">

```
┌─────────────────────────────────────┐
│         CONTROL PLANE               │
│  • Service discovery                │
│  • Configuration management         │
│  • Health monitoring               │
│  • Traffic routing rules           │
│  • Autoscaling decisions          │
└────────────┬───────────────────────┘
             │ Commands
             ↓
┌─────────────────────────────────────┐
│          DATA PLANE                 │
│  • Handle user requests            │
│  • Process data                    │
│  • Forward packets                 │
│  • Execute business logic          │
│  • Store and retrieve              │
└─────────────────────────────────────┘
```

</div>

### Orchestration vs Choreography

<div class="pattern-comparison">

=== "Orchestration (Central Conductor)"

    ```
                     Orchestrator
                    /     |      \
                 /        |         \
              /           |            \
        Service A    Service B    Service C
             ↑            ↑            ↑
             └────────────┴────────────┘
                Commands flow down
    ```
    
    **Examples**: Kubernetes, Airflow, Temporal

=== "Choreography (Peer Dance)"

    ```
        Service A ←→ Service B
             ↓  ↖    ↗  ↓
               Service C
         
         Events trigger reactions
    ```
    
    **Examples**: Event-driven, Pub/sub, Actors

</div>

### Decision Framework

<div class="decision-box">

```
Choose ORCHESTRATION when:
- Clear workflow steps
- Central visibility needed
- Rollback requirements
- Complex error handling

Choose CHOREOGRAPHY when:
- Loose coupling required
- Services independently owned
- Event-driven nature
- Scale requirements high
```

</div>

### Control Loop Dynamics

<div class="control-loop">

```
Observe → Orient → Decide → Act
   ↑                          ↓
   └──────── Feedback ────────┘

Observe: Metrics, logs, traces
Orient: Anomaly detection
Decide: Policy engine
Act: API calls, configs
```

</div>

!!! example "🔧 Try This: Build a Service Registry"

    ```python
    import time
    import threading
    from datetime import datetime

    class ServiceRegistry:
        def __init__(self, ttl=30):
            self.services = {}
            self.ttl = ttl
            self.lock = threading.Lock()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
        
        def register(self, name, host, port, metadata=None):
            with self.lock:
                self.services[name] = self.services.get(name, [])
                
                # Update or add instance
                instance = {
                    'host': host,
                    'port': port,
                    'metadata': metadata or {},
                    'last_heartbeat': time.time(),
                    'healthy': True
                }
                
                # Find and update existing
                found = False
                for i, svc in enumerate(self.services[name]):
                    if svc['host'] == host and svc['port'] == port:
                        self.services[name][i] = instance
                        found = True
                        break
                
                if not found:
                    self.services[name].append(instance)
        
        def discover(self, name, healthy_only=True):
            with self.lock:
                if name not in self.services:
                    return []
                
                instances = self.services[name]
                if healthy_only:
                    instances = [i for i in instances if i['healthy']]
                
                return instances
        
        def heartbeat(self, name, host, port):
            with self.lock:
                if name in self.services:
                    for instance in self.services[name]:
                        if (instance['host'] == host and 
                            instance['port'] == port):
                            instance['last_heartbeat'] = time.time()
                            instance['healthy'] = True
        
        def _cleanup_loop(self):
            while True:
                time.sleep(5)
                with self.lock:
                    now = time.time()
                    
                    for name, instances in list(self.services.items()):
                        # Mark unhealthy
                        for instance in instances:
                            if now - instance['last_heartbeat'] > self.ttl:
                                instance['healthy'] = False
                        
                        # Remove long-dead instances
                        self.services[name] = [
                            i for i in instances 
                            if now - i['last_heartbeat'] < self.ttl * 3
                        ]
                        
                        # Clean up empty services
                        if not self.services[name]:
                            del self.services[name]

    # Usage example
    registry = ServiceRegistry(ttl=10)

    # Service registers itself
    registry.register('api', 'host1', 8080, {'version': '1.2.3'})
    registry.register('api', 'host2', 8080, {'version': '1.2.3'})

    # Client discovers services
    services = registry.discover('api')
    print(f"Found {len(services)} healthy instances")

    # Simulate heartbeats
    for _ in range(3):
        time.sleep(3)
        registry.heartbeat('api', 'host1', 8080)
        # host2 stops heartbeating
        
    # Check health after timeout
    time.sleep(12)
    healthy = registry.discover('api', healthy_only=True)
    print(f"Healthy instances: {len(healthy)}")
    ```

---

## Page 30: Control-Plane vs Data-Plane Diagram

### Service Mesh Architecture Example

<div class="service-mesh-diagram">

```
┌─────────────────────── CONTROL PLANE ───────────────────────┐
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Policy Engine│  │Config Server │  │ Service Registry │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                  │                    │           │
│         └──────────────────┼────────────────────┘           │
│                            ↓                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Control Plane API (gRPC)                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ xDS APIs
═══════════════════════════════╪═══════════════════════════════
                              ↓
┌─────────────────────── DATA PLANE ──────────────────────────┐
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Service A     │  │   Service B     │                  │
│  │  ┌───────────┐ │  │  ┌───────────┐ │                  │
│  │  │   App     │ │  │  │   App     │ │                  │
│  │  └─────┬─────┘ │  │  └─────┬─────┘ │                  │
│  │        ↓       │  │        ↓       │                  │
│  │  ┌───────────┐ │  │  ┌───────────┐ │                  │
│  │  │Envoy Proxy│ │  │  │Envoy Proxy│ │                  │
│  │  └─────┬─────┘ │  │  └─────┬─────┘ │                  │
│  └────────┼────────┘  └────────┼────────┘                  │
│           │                    │                            │
│           └────────────────────┘                            │
│                   Traffic Flow                              │
└──────────────────────────────────────────────────────────────┘
```

</div>

### Control/Data Plane Separation Benefits

<div class="benefit-list">

1. **Independent scaling**: Control plane can be smaller
2. **Failure isolation**: Data plane continues if control fails
3. **Update safety**: Control changes don't affect traffic
4. **Security**: Different access controls

</div>

!!! example "Real Example: Envoy Configuration"

    ```yaml
    # Control Plane pushes this config
    static_resources:
      listeners:
      - name: listener_0
        address:
          socket_address:
            address: 0.0.0.0
            port_value: 10000
        filter_chains:
        - filters:
          - name: envoy.http_connection_manager
            typed_config:
              route_config:
                virtual_hosts:
                - name: backend
                  domains: ["*"]
                  routes:
                  - match: 
                      prefix: "/"
                    route:
                      weighted_clusters:
                        clusters:
                        - name: service_blue
                          weight: 90
                        - name: service_green
                          weight: 10  # Canary!
    ```

---

## Page 31: EXTENSION PILLAR V – Intelligence

!!! target "Learning Objective"
    Systems that adapt survive; systems that learn thrive.

### The Intelligence Stack

<div class="intelligence-hierarchy">

```
Level 4: Predictive
- Forecast failures
- Preemptive scaling
- Anomaly prevention

Level 3: Adaptive  
- Self-tuning parameters
- Dynamic routing
- Learned patterns

Level 2: Reactive
- Auto-scaling
- Circuit breakers
- Simple thresholds

Level 1: Static
- Fixed configs
- Manual intervention
- No learning
```

</div>

### Edge Intelligence Patterns

<div class="edge-patterns">

=== "Federated Learning"

    ```
    ┌─────┐ ┌─────┐ ┌─────┐
    │Edge1│ │Edge2│ │Edge3│
    └──┬──┘ └──┬──┘ └──┬──┘
       │       │       │
       │  Gradients    │
       └───────┼───────┘
               ↓
        ┌─────────────┐
        │Central Model│
        └─────────────┘
               ↓
         Updated Model
    ```

=== "Edge Inference"

    ```
    User → Edge Device → Inference → Response
              ↓                ↑
         [Local Model]    [Periodic Update]
                               ↑
                          Central Training
    ```

</div>

### AIOps Feedback Loop

<div class="aiops-loop">

```
┌─────────────────────────────────────┐
│           OBSERVE                   │
│  Metrics, Logs, Traces, Events     │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│           ANALYZE                   │
│  Anomaly Detection, Correlation    │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│           DECIDE                    │
│  ML Models, Policy Engine          │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│            ACT                      │
│  Scale, Reroute, Restart, Alert    │
└─────────────────────────────────────┘
```

</div>

<div class="ml-example">

**🎬 Real ML-Driven Optimization**:

```yaml
Netflix Adaptive Bitrate (Simplified):

Traditional: Fixed quality levels
- 480p: 1 Mbps
- 720p: 2.5 Mbps  
- 1080p: 5 Mbps
- 4K: 15 Mbps

ML-Driven: Per-content optimization
- Action movie, high motion: +30% bitrate
- Dialog scene, low motion: -40% bitrate
- Dark scenes: Special encoding
- User's network learned over time

Results:
- 30% bandwidth reduction
- Better perceived quality
- Fewer rebuffers
```

</div>

!!! warning "Intelligence Anti-Patterns"

    1. **Over-optimization**: ML where simple rules work
    2. **Black box ops**: Can't explain decisions
    3. **Feedback loops**: ML amplifies biases
    4. **Cold start**: No data to learn from
    5. **Adversarial**: System gamed by users

---

## Page 32: Feedback-Control Loop Figure

### Classic Control Theory Applied

<div class="control-theory">

```
                 Setpoint (Desired State)
                         ↓
Error = Setpoint - Measured
                         ↓
            ┌────────────────────────┐
            │   PID Controller       │
            │                        │
            │ P: Proportional        │
            │ I: Integral           │
            │ D: Derivative         │
            └────────────┬───────────┘
                         ↓
                 Control Signal
                         ↓
               ┌─────────────────┐
               │     System      │
               └────────┬────────┘
                        ↓
                 Measured Output
                        ↓
                    Feedback ←──┘
```

</div>

!!! example "Applied to Autoscaling"

    ```python
    class PIDAutoscaler:
        def __init__(self, kp=1.0, ki=0.1, kd=0.05):
            self.kp = kp  # Proportional gain
            self.ki = ki  # Integral gain
            self.kd = kd  # Derivative gain
            
            self.integral = 0
            self.last_error = 0
            
        def compute(self, setpoint, measured):
            # Error
            error = setpoint - measured
            
            # Proportional term
            p_term = self.kp * error
            
            # Integral term
            self.integral += error
            i_term = self.ki * self.integral
            
            # Derivative term
            derivative = error - self.last_error
            d_term = self.kd * derivative
            
            # Control output
            output = p_term + i_term + d_term
            
            self.last_error = error
            
            return output

    # Usage
    autoscaler = PIDAutoscaler(kp=2.0, ki=0.5, kd=0.1)
    target_cpu = 70  # 70% target

    while True:
        current_cpu = get_cpu_usage()
        adjustment = autoscaler.compute(target_cpu, current_cpu)
        
        if adjustment > 0:
            scale_up(int(adjustment / 10))
        elif adjustment < 0:
            scale_down(int(-adjustment / 10))
        
        time.sleep(30)
    ```

---

## Summary: From Axioms to Architecture

### The Journey So Far

You've now seen how:

1. **8 Fundamental Axioms** (Part I) define the immutable constraints
2. **5 Foundational Pillars** (Part II) emerge from these constraints
3. **Patterns and Anti-patterns** arise from pillar interactions

### Key Takeaways

<div class="takeaway-grid">

| Pillar | Core Insight | Remember |
|--------|--------------|----------|
| **Work Distribution** | Stateless scales, stateful coordinates | Work stealing beats static allocation |
| **State Distribution** | CAP theorem is non-negotiable | Choose consistency model wisely |
| **Truth Distribution** | Consensus has fundamental costs | Quorums provide tunable consistency |
| **Control Distribution** | Separate control from data plane | Orchestration vs choreography depends on coupling |
| **Intelligence Distribution** | Feedback loops enable adaptation | Simple PID often beats complex ML |

</div>

### The Mental Models

<div class="mental-model-box">

```
Remember these three models:

1. The House: Intelligence protects (roof), Control supports (walls), 
   Truth foundations, Work and State are the living spaces

2. The Gradient: Every decision trades off between competing concerns
   (latency vs consistency, cost vs reliability, etc.)

3. The Loop: Observe → Orient → Decide → Act → Feedback
   (applies to autoscaling, monitoring, and system evolution)
```

</div>

### What's Next?

Having mastered the foundational theory, you're ready for:

- **Pattern Deep Dives**: Specific implementations of each pillar
- **Case Studies**: Real-world applications and failures
- **Quantitative Tools**: Calculators and decision frameworks

---

!!! success "Congratulations!"
    
    You've completed the theoretical foundation of distributed systems. The patterns you'll encounter in practice are simply combinations and applications of these fundamental principles.
    
    **[← Back to Part I: The 8 Axioms](distributed-systems-book.md)** | **[↑ Back to Home](index.md)**