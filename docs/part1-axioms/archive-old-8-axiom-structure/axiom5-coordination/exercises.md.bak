---
title: "Axiom 5 Exercises: Master the Cost of Coordination"
description: "Hands-on labs to calculate coordination costs, implement consensus protocols, and design systems that minimize coordination overhead. Learn to make million-dollar architecture decisions."
type: axiom
difficulty: advanced
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure, axiom4-concurrency, axiom5-coordination]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](../../introduction/index.md) → [Part I: Axioms](../index.md) → [Axiom 5](index.md) → **Coordination Exercises**

# Coordination Exercises

**Master the economics of distributed agreement through hands-on practice**

---

## 🧪 Hands-On Labs

### Lab 1: Coordination Cost Calculator

**Build a real-world cost calculator for different coordination strategies**

#### Exercise 1.1: AWS Cost Calculator

```python
import math
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class ConsistencyLevel(Enum):
    EVENTUAL = "eventual"
    CAUSAL = "causal"
    SEQUENTIAL = "sequential"
    LINEARIZABLE = "linearizable"
    SERIALIZABLE = "serializable"

@dataclass
class AWSResources:
    """AWS resources needed for coordination"""
    ec2_instances: int
    instance_type: str = "m5.large"  # $0.096/hour
    rds_instances: int = 0
    elasticache_nodes: int = 0
    cross_region_gb: float = 0
    load_balancers: int = 0
    
class CoordinationCostCalculator:
    """Calculate real AWS costs for coordination patterns"""
    
    def __init__(self):
        # AWS Pricing (us-east-1, on-demand)
        self.pricing = {
            'ec2': {
                'm5.large': 0.096,
                'm5.xlarge': 0.192,
                'm5.2xlarge': 0.384,
                'c5.large': 0.085,
                'c5.xlarge': 0.170
            },
            'network': {
                'same_az': 0.01,  # $/GB
                'cross_az': 0.02,  # $/GB
                'cross_region': 0.09  # $/GB
            },
            'elb': 0.025,  # $/hour + data
            'rds': {
                'db.m5.large': 0.171,
                'db.m5.xlarge': 0.342
            },
            'elasticache': {
                'cache.m5.large': 0.156
            }
        }
        
    def calculate_monthly_cost(self, 
                             consistency: ConsistencyLevel,
                             transactions_per_second: int,
                             regions: List[str]) -> Dict:
        """Calculate monthly AWS bill for given coordination pattern"""
        
        # TODO: Implement cost calculation based on:
        # 1. Consistency level requirements
        # 2. Transaction volume
        # 3. Geographic distribution
        # 4. Message overhead for coordination
        
        # Your implementation here
        pass

# Test scenarios
scenarios = [
    {
        "name": "E-commerce Platform",
        "consistency": ConsistencyLevel.EVENTUAL,
        "tps": 1000,
        "regions": ["us-east-1", "eu-west-1", "ap-southeast-1"]
    },
    {
        "name": "Banking System",
        "consistency": ConsistencyLevel.SERIALIZABLE,
        "tps": 100,
        "regions": ["us-east-1", "us-west-2"]
    },
    {
        "name": "Social Media Feed",
        "consistency": ConsistencyLevel.CAUSAL,
        "tps": 10000,
        "regions": ["us-east-1", "eu-west-1", "ap-southeast-1", "sa-east-1"]
    }
]

# Exercise: Complete the calculator and analyze costs
for scenario in scenarios:
    calculator = CoordinationCostCalculator()
    cost = calculator.calculate_monthly_cost(
        consistency=scenario["consistency"],
        transactions_per_second=scenario["tps"],
        regions=scenario["regions"]
    )
    print(f"\n{scenario['name']}:")
    print(f"  Monthly cost: ${cost['total']:,.2f}")
    print(f"  Cost per transaction: ${cost['per_transaction']:.6f}")
```

#### Exercise 1.2: Coordination Trade-off Analyzer

```python
class CoordinationTradeoffAnalyzer:
    """Analyze trade-offs between consistency, availability, and cost"""
    
    def __init__(self):
        self.metrics = {
            'latency': {},
            'availability': {},
            'consistency': {},
            'cost': {}
        }
        
    def analyze_pattern(self, pattern_name: str, config: dict):
        """Analyze a coordination pattern"""
        
        # TODO: Calculate for each pattern:
        # 1. Average latency (ms)
        # 2. Availability (nines)
        # 3. Consistency guarantee
        # 4. Infrastructure cost
        # 5. Operational complexity
        
        pass
        
    def generate_report(self):
        """Generate comparison report"""
        # TODO: Create visualization comparing:
        # - Cost vs Consistency
        # - Latency vs Availability
        # - Complexity vs Scale
        pass

# Patterns to analyze
patterns = {
    "no_coordination": {
        "description": "Fire and forget",
        "example": "Logging, metrics"
    },
    "eventual_consistency": {
        "description": "Async replication",
        "example": "DynamoDB, Cassandra"
    },
    "quorum": {
        "description": "R + W > N",
        "example": "Riak, Voldemort"
    },
    "consensus": {
        "description": "Raft/Paxos",
        "example": "etcd, Consul"
    },
    "2pc": {
        "description": "Two-phase commit",
        "example": "Traditional databases"
    }
}
```

---

### Lab 2: Implement Coordination Protocols

**Build simplified versions of real coordination protocols**

#### Exercise 2.1: Gossip Protocol Implementation

```python
import random
import time
import asyncio
from typing import Set, Dict, Any
import hashlib

class GossipNode:
    """Implement a gossip protocol for eventual consistency"""
    
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.data = {}  # key -> (value, version, timestamp)
        self.message_count = 0
        self.convergence_time = None
        
    async def set_value(self, key: str, value: Any):
        """Set a value locally"""
        timestamp = time.time()
        version = hashlib.md5(f"{value}{timestamp}".encode()).hexdigest()[:8]
        
        self.data[key] = {
            'value': value,
            'version': version,
            'timestamp': timestamp,
            'source': self.node_id
        }
        
    async def gossip_round(self):
        """One round of gossip communication"""
        # TODO: Implement gossip protocol
        # 1. Select random subset of peers (fanout)
        # 2. Exchange state with selected peers
        # 3. Merge received state
        # 4. Track convergence metrics
        
        pass
        
    def merge_state(self, remote_data: Dict):
        """Merge remote state with local state"""
        # TODO: Implement merge logic
        # - Use version vectors or timestamps
        # - Handle conflicts (LWW, CRDT, etc)
        # - Track convergence progress
        
        pass

# Test: Measure convergence time
async def test_gossip_convergence():
    """Test how quickly gossip spreads information"""
    
    # Create network of 100 nodes
    nodes = []
    for i in range(100):
        peers = [f"node_{j}" for j in range(100) if j != i]
        node = GossipNode(f"node_{i}", peers)
        nodes.append(node)
    
    # Inject value at node 0
    await nodes[0].set_value("test_key", "test_value")
    
    # Run gossip rounds until convergence
    rounds = 0
    while not all_converged(nodes, "test_key"):
        await asyncio.gather(*[node.gossip_round() for node in nodes])
        rounds += 1
        
    print(f"Converged in {rounds} rounds")
    print(f"Total messages: {sum(n.message_count for n in nodes)}")
    
    # Compare with broadcast (all-to-all)
    broadcast_messages = len(nodes) * (len(nodes) - 1)
    print(f"Broadcast would need: {broadcast_messages} messages")
    print(f"Gossip efficiency: {broadcast_messages / sum(n.message_count for n in nodes):.2f}x")
```

#### Exercise 2.2: Simplified Raft Implementation

```python
from enum import Enum
import asyncio
import random

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
        self.log = []  # [(term, command)]
        self.commit_index = -1
        
        # Leader state
        self.next_index = {}  # peer -> next log index
        self.match_index = {}  # peer -> highest replicated index
        
        # Timing
        self.election_timeout = random.uniform(150, 300)  # ms
        self.heartbeat_interval = 50  # ms
        
    async def start_election(self):
        """Transition to candidate and start election"""
        # TODO: Implement leader election
        # 1. Increment current term
        # 2. Vote for self
        # 3. Send RequestVote RPCs to all peers
        # 4. Become leader if majority votes received
        
        pass
        
    async def append_entries(self, entries: List[tuple]):
        """Leader appends entries and replicates"""
        # TODO: Implement log replication
        # 1. Append to local log
        # 2. Send AppendEntries to all followers
        # 3. Wait for majority
        # 4. Update commit index
        # 5. Apply to state machine
        
        pass
        
    async def handle_request_vote(self, term: int, candidate_id: int, 
                                last_log_index: int, last_log_term: int):
        """Handle vote request from candidate"""
        # TODO: Implement voting logic
        # - Check term
        # - Check if already voted
        # - Check if candidate's log is up-to-date
        
        pass

# Exercise: Complete Raft implementation and test
class RaftCluster:
    """Test harness for Raft cluster"""
    
    def __init__(self, size: int = 5):
        self.nodes = []
        for i in range(size):
            peers = [j for j in range(size) if j != i]
            node = RaftNode(i, peers)
            self.nodes.append(node)
            
    async def test_leader_election(self):
        """Test that cluster elects a leader"""
        # TODO: Start nodes and verify leader election
        pass
        
    async def test_log_replication(self):
        """Test that logs replicate correctly"""
        # TODO: Submit commands and verify replication
        pass
        
    async def test_partition_tolerance(self):
        """Test behavior during network partition"""
        # TODO: Simulate partition and verify safety
        pass
```

---

### Lab 3: Zero-Coordination Design

**Design systems that minimize or eliminate coordination**

#### Exercise 3.1: CRDT Shopping Cart

```python
from typing import Dict, Set, Tuple
import uuid

class CRDTShoppingCart:
    """Conflict-free shopping cart that needs no coordination"""
    
    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        self.adds = {}  # item -> {(quantity, replica_id, timestamp)}
        self.removes = {}  # item -> {(quantity, replica_id, timestamp)}
        
    def add_item(self, item: str, quantity: int = 1):
        """Add item to cart - no coordination needed"""
        timestamp = time.time()
        unique_id = f"{self.replica_id}:{timestamp}"
        
        if item not in self.adds:
            self.adds[item] = set()
            
        self.adds[item].add((quantity, self.replica_id, timestamp))
        
    def remove_item(self, item: str, quantity: int = 1):
        """Remove item from cart - no coordination needed"""
        # TODO: Implement remove operation
        # Must handle concurrent add/remove correctly
        pass
        
    def get_contents(self) -> Dict[str, int]:
        """Get current cart contents"""
        # TODO: Calculate effective quantities
        # adds - removes for each item
        pass
        
    def merge(self, other: 'CRDTShoppingCart'):
        """Merge with another cart replica"""
        # TODO: Implement CRDT merge
        # - Union of all operations
        # - Commutative and associative
        # - Idempotent
        pass

# Test concurrent modifications
def test_crdt_cart():
    # User has cart on phone and laptop
    phone_cart = CRDTShoppingCart("phone")
    laptop_cart = CRDTShoppingCart("laptop")
    
    # Concurrent operations (no coordination)
    phone_cart.add_item("book", 2)
    laptop_cart.add_item("book", 1)
    phone_cart.add_item("pen", 5)
    laptop_cart.remove_item("book", 1)
    
    # Merge when devices sync
    phone_cart.merge(laptop_cart)
    laptop_cart.merge(phone_cart)
    
    # Both should show same contents
    assert phone_cart.get_contents() == laptop_cart.get_contents()
    print("Cart contents:", phone_cart.get_contents())
```

#### Exercise 3.2: Sharded Counter System

```python
class ShardedCounter:
    """Scalable counter with minimal coordination"""
    
    def __init__(self, num_shards: int = 100):
        self.shards = [0] * num_shards
        self.num_shards = num_shards
        
    def increment(self, amount: int = 1, key: str = None):
        """Increment counter - no global coordination"""
        # TODO: Implement sharded increment
        # 1. Hash key to shard (or random if no key)
        # 2. Increment only that shard
        # 3. No coordination with other shards
        pass
        
    def get_count(self) -> int:
        """Get total count across all shards"""
        # TODO: Sum all shards
        # May be slightly stale but no coordination
        pass
        
    def rebalance_shards(self, new_shard_count: int):
        """Dynamically adjust shard count"""
        # TODO: Implement shard rebalancing
        # Should work without stopping writes
        pass

# Benchmark sharded vs global counter
def benchmark_counters():
    import threading
    import time
    
    # Global counter (needs synchronization)
    global_counter = 0
    global_lock = threading.Lock()
    
    def increment_global(n):
        global global_counter
        for _ in range(n):
            with global_lock:
                global_counter += 1
    
    # Sharded counter (no global lock)
    sharded = ShardedCounter(100)
    
    def increment_sharded(n):
        for _ in range(n):
            sharded.increment()
    
    # Compare performance
    # TODO: Run benchmarks with multiple threads
    # Measure throughput difference
```

---

## 💪 Challenge Problems

### Challenge 1: Multi-Region Database Design

**Design a globally distributed database with tunable consistency**

```python
class MultiRegionDatabase:
    """Design a database that minimizes coordination costs"""
    
    def __init__(self, regions: List[str]):
        self.regions = regions
        self.consistency_levels = {
            'eventual': self.eventual_write,
            'bounded': self.bounded_staleness_write,
            'strong': self.strong_consistency_write,
            'consistent_prefix': self.consistent_prefix_write
        }
        
    # Your task: Implement each consistency level
    # Minimize coordination while meeting guarantees
    # Calculate the cost of each approach
    
    async def write(self, key: str, value: Any, 
                   consistency: str = 'eventual'):
        """Write with specified consistency level"""
        # TODO: Route to appropriate implementation
        pass

# Design challenges:
# 1. How to minimize cross-region coordination?
# 2. When is coordination unavoidable?
# 3. How to handle region failures?
# 4. What's the $ cost of each consistency level?
```

### Challenge 2: Coordination-Free Analytics

**Build an analytics system that scales without coordination**

```python
class DistributedAnalytics:
    """Real-time analytics without coordination bottlenecks"""
    
    def __init__(self):
        self.aggregators = {}  # metric -> aggregator
        self.time_windows = [60, 300, 3600]  # 1min, 5min, 1hour
        
    def track_event(self, event_type: str, value: float, 
                   dimensions: Dict[str, str]):
        """Track event without coordination"""
        # TODO: Design a system that:
        # 1. Handles 1M events/second
        # 2. Provides <1s query latency
        # 3. No coordination between nodes
        # 4. Approximate results OK (±1%)
        pass
        
    def query(self, metric: str, time_range: Tuple[int, int],
             group_by: List[str]):
        """Query analytics data"""
        # TODO: Implement distributed query
        # How to aggregate without coordination?
        pass

# Techniques to explore:
# - Probabilistic data structures
# - Sampling strategies  
# - Local aggregation + periodic merge
# - Sketch algorithms
```

### Challenge 3: The Billion-User Problem

```python
"""
Scenario: Design Facebook's "Like" counter

Requirements:
- 1 billion users
- 100 billion objects (posts, photos, etc)
- 10 million likes/second peak
- Show count in <100ms
- Tolerate ±1% error

Constraints:
- $10M/year budget
- 5 data centers globally
- Network partitions happen daily

Your task:
1. Design the system architecture
2. Choose coordination strategy
3. Calculate infrastructure costs
4. Handle failure scenarios
5. Prove it meets requirements
"""

class LikeCounter:
    # Your implementation here
    pass
```

---

## 🔬 Research Projects

### Project 1: Coordination Cost Visualizer

```python
"""
Build an interactive tool that visualizes:
1. Message flow in different protocols
2. Latency impact of coordination
3. Cost breakdown by component
4. Failure scenario impacts

Deliverables:
- Web-based visualization
- Real protocol traces
- Cost calculator integration
- What-if scenario tool
"""
```

### Project 2: Auto-Tuning Consistency

```python
"""
Create a system that automatically adjusts consistency based on:
1. Current load
2. Error budget remaining
3. Business value of operation
4. Infrastructure costs

Goal: Minimize cost while meeting SLAs
"""

class ConsistencyTuner:
    def __init__(self):
        self.sla_targets = {}
        self.error_budgets = {}
        self.cost_model = {}
        
    def recommend_consistency(self, operation_type: str, 
                            current_load: float) -> ConsistencyLevel:
        """ML model to recommend optimal consistency"""
        # TODO: Implement adaptive algorithm
        pass
```

### Project 3: Chaos Coordination Testing

```python
"""
Build a framework that:
1. Injects coordination failures
2. Measures system behavior
3. Finds coordination bottlenecks
4. Suggests optimizations

Test scenarios:
- Clock skew
- Network partitions
- Asymmetric partitions
- Cascading failures
"""
```

---

## 📡 Distributed Systems Design Exercise

### Design a Global Hotel Booking System

```yaml
Requirements:
  Scale:
    - 10M hotels worldwide
    - 100M daily searches  
    - 1M bookings/day
    - 200 countries
    
  Business Rules:
    - No double bookings (critical)
    - Price consistency (important)
    - Inventory accuracy (important)
    - Search freshness (nice-to-have)
    
  Budget:
    - $500K/month infrastructure
    - 10 engineers
    - 3 global regions

Your Task:
  1. Architecture Design:
     - How do you shard the data?
     - What consistency level for each operation?
     - How to handle conflicts?
     
  2. Cost Analysis:
     - Calculate infrastructure needs
     - Estimate coordination costs
     - Show cost per booking
     
  3. Failure Handling:
     - Region failure
     - Network partition  
     - Data corruption
     
  4. Optimization:
     - Where can you avoid coordination?
     - What can be eventually consistent?
     - How to reduce costs by 50%?
```

---

## 📑 Practical Coordination Patterns

### Pattern Reference Card

```python
# Quick reference for choosing coordination patterns

coordination_patterns = {
    "fire_and_forget": {
        "use_when": "Don't need confirmation",
        "consistency": "None",
        "cost": "$0.0001/op",
        "example": "Metrics, logs"
    },
    "async_replication": {
        "use_when": "Can tolerate stale reads",
        "consistency": "Eventual",
        "cost": "$0.001/op",
        "example": "User profiles, product catalog"
    },
    "read_repair": {
        "use_when": "Read heavy, eventual consistency OK",
        "consistency": "Eventual",
        "cost": "$0.005/op",
        "example": "Shopping carts"
    },
    "write_through": {
        "use_when": "Need read-after-write consistency",
        "consistency": "Strong for writer",
        "cost": "$0.01/op",
        "example": "User sessions"
    },
    "2pc": {
        "use_when": "ACID required",
        "consistency": "Serializable",
        "cost": "$0.50/op",
        "example": "Financial transactions"
    }
}

def choose_pattern(requirements):
    """Simple decision tree for coordination pattern"""
    if requirements['data_loss_ok']:
        return 'fire_and_forget'
    elif requirements['eventual_consistency_ok']:
        if requirements['read_heavy']:
            return 'read_repair'
        else:
            return 'async_replication'
    elif requirements['need_read_after_write']:
        return 'write_through'
    else:
        return '2pc'  # Most expensive option
```

---

## 🏆 Skills Assessment

Rate your understanding (1-5):
- [ ] Can calculate coordination costs in dollars
- [ ] Understand when to use each consistency level
- [ ] Can implement basic consensus protocol
- [ ] Know how to avoid coordination
- [ ] Can design geo-distributed systems
- [ ] Understand CRDT principles
- [ ] Can analyze coordination trade-offs
- [ ] Can optimize for cost vs consistency

**Score: ___/40** (32+ = Expert, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

## 🔄 Consistency Coordination Lab

### Lab 4: Implement Tunable Consistency

**Build a system that can dynamically adjust consistency levels based on requirements**

```python
from enum import Enum
from typing import Dict, List, Optional, Tuple
import asyncio
import time

class ConsistencyLevel(Enum):
    ONE = 1          # Write to one replica
    QUORUM = 2       # Write to majority
    ALL = 3          # Write to all replicas
    LOCAL_QUORUM = 4 # Quorum in local DC
    EACH_QUORUM = 5  # Quorum in each DC

class TunableConsistencySystem:
    """
    Implement a Cassandra-like tunable consistency system
    """
    
    def __init__(self, replicas: List[str], replication_factor: int = 3):
        self.replicas = replicas
        self.replication_factor = replication_factor
        self.data = {}  # replica -> {key: (value, timestamp)}
        
    async def write(self, key: str, value: str, 
                   consistency: ConsistencyLevel) -> bool:
        """
        TODO: Implement write with tunable consistency
        1. Calculate required acknowledgments
        2. Send write to replicas
        3. Wait for required ACKs
        4. Return success/failure
        """
        pass
        
    async def read(self, key: str, 
                  consistency: ConsistencyLevel) -> Optional[str]:
        """
        TODO: Implement read with tunable consistency
        1. Calculate required responses
        2. Query replicas
        3. Resolve conflicts if any
        4. Return latest value
        """
        pass
        
    def calculate_required_nodes(self, consistency: ConsistencyLevel, 
                               operation: str) -> int:
        """
        TODO: Calculate how many nodes needed for consistency level
        """
        pass

# Test scenarios
test_cases = [
    {
        "name": "Strong Consistency (Banking)",
        "write_cl": ConsistencyLevel.QUORUM,
        "read_cl": ConsistencyLevel.QUORUM,
        "expected_behavior": "Always read what you write"
    },
    {
        "name": "High Performance (Analytics)",
        "write_cl": ConsistencyLevel.ONE,
        "read_cl": ConsistencyLevel.ONE,
        "expected_behavior": "May read stale data"
    },
    {
        "name": "Write Heavy (Logging)",
        "write_cl": ConsistencyLevel.ONE,
        "read_cl": ConsistencyLevel.ALL,
        "expected_behavior": "Fast writes, consistent reads"
    }
]
```

### Exercise 4.1: Consistency vs Availability Trade-offs

```python
class ConsistencyAvailabilityAnalyzer:
    """
    Analyze the trade-offs between consistency and availability
    """
    
    def __init__(self, total_nodes: int = 5):
        self.total_nodes = total_nodes
        
    def calculate_availability(self, consistency_level: str, 
                             nodes_required: int,
                             node_failure_rate: float = 0.01) -> float:
        """
        TODO: Calculate system availability given:
        - Consistency requirements  
        - Individual node failure rate
        - Number of replicas
        
        Return probability that operation succeeds
        """
        pass
        
    def find_optimal_configuration(self, 
                                 target_availability: float,
                                 target_consistency: str) -> Dict:
        """
        TODO: Find the optimal number of replicas and 
        consistency levels to meet both targets
        """
        pass

# Scenarios to analyze
scenarios = [
    "Payment processing: 99.99% availability with strong consistency",
    "Social media feed: 99.999% availability with eventual consistency",
    "Configuration service: 99.9% availability with linearizability"
]
```

### Exercise 4.2: Implement Read Repair

```python
class ReadRepairCoordinator:
    """
    Implement read repair to fix inconsistencies during reads
    """
    
    def __init__(self, replicas: List[str]):
        self.replicas = replicas
        
    async def read_with_repair(self, key: str, 
                              consistency_level: ConsistencyLevel) -> Tuple[str, int]:
        """
        TODO: Implement read repair
        1. Read from multiple replicas
        2. Detect inconsistencies  
        3. Repair out-of-date replicas
        4. Return most recent value and number of repairs
        """
        pass
        
    def detect_inconsistency(self, responses: List[Tuple[str, int]]) -> bool:
        """
        TODO: Detect if replicas have different values
        """
        pass
        
    async def repair_replica(self, replica: str, key: str, 
                           correct_value: str, timestamp: int):
        """
        TODO: Update out-of-date replica
        """
        pass
```

### Exercise 4.3: Consistency Monitoring Dashboard

```python
class ConsistencyMonitor:
    """
    Build a monitoring system for consistency violations
    """
    
    def __init__(self):
        self.metrics = {
            'read_inconsistencies': 0,
            'write_failures': 0,
            'repair_operations': 0,
            'stale_reads': 0
        }
        
    def build_dashboard(self) -> str:
        """
        TODO: Create ASCII dashboard showing:
        1. Current consistency violations
        2. Replication lag by node
        3. Success rates by consistency level
        4. Recommended actions
        
        Example output:
        ╔══════════════════════════════════════╗
        ║   Consistency Monitoring Dashboard    ║
        ╠══════════════════════════════════════╣
        ║ Inconsistent Reads:  12 (0.01%)      ║
        ║ Replication Lag:                     ║
        ║   Node1: 5ms   Node2: 12ms          ║
        ║   Node3: 3ms   Node4: 45ms ⚠️       ║
        ║ Success Rates:                       ║
        ║   ONE: 99.99%  QUORUM: 99.95%       ║
        ║   ALL: 98.50%                        ║
        ╚══════════════════════════════════════╝
        """
        pass
```

### Lab 4 Grading Rubric

- [ ] Correctly implements tunable consistency (5 pts)
- [ ] Handles network failures gracefully (5 pts)
- [ ] Implements efficient read repair (5 pts)
- [ ] Monitoring accurately tracks violations (5 pts)
- [ ] Can explain consistency/availability trade-offs (5 pts)

**Total: ___/25 points**

---

## 🎯 Final Challenge: Production System Design

```python
"""
The Ultimate Test: Design Uber's Surge Pricing System

Requirements:
- Real-time supply/demand calculation
- City-level pricing decisions
- Prices visible within 2 seconds
- No pricing arbitrage between zones
- Handle city-wide events (concerts, sports)
- Work during network partitions

Scale:
- 10,000 cities
- 1M active drivers
- 10M active riders
- Price updates every 30 seconds

Your Solution Must:
1. Define coordination boundaries
2. Choose consistency model
3. Calculate infrastructure cost
4. Handle edge cases
5. Prove it scales

Bonus: How would you test this system?
"""

# Your implementation here
class SurgePricingSystem:
    pass
```

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 6: Observability](../axiom6-observability/index.md)

**Related**: [Consensus](../../patterns/consensus.md) • [Distributed Lock](../../patterns/distributed-lock.md) • [Leader Election](../../patterns/leader-election.md) • [Saga Pattern](../../patterns/saga.md) • [CQRS](../../patterns/cqrs.md)

## References

¹ [Harvest, Yield, and Scalable Tolerant Systems - Fox & Brewer (1999)](https://dl.acm.org/doi/10.5555/822076.822436)

² [Conflict-free Replicated Data Types - Shapiro et al. (2011)](https://hal.inria.fr/inria-00609399/document)

³ [In Search of an Understandable Consensus Algorithm (Raft) - Ongaro & Ousterhout (2014)](https://raft.github.io/raft.pdf)

⁴ [Dynamo: Amazon's Highly Available Key-value Store - DeCandia et al. (2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)

⁵ [Spanner: Google's Globally-Distributed Database - Corbett et al. (2012)](https://research.google/pubs/pub39966/)
