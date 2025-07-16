Page 25: PILLAR II – Distribution of State
Learning Objective: State is where distributed systems get hard; master the trade-offs.
The State Distribution Trilemma:
        Consistency
            / \
           /   \
          /     \
         /       \
    Availability  Partition Tolerance
    
Pick 2, but P is mandatory in distributed systems,
so really: Choose between C and A when partitioned
State Distribution Strategies:
1. Partitioning (Sharding):
Data universe: [A-Z]
├─ Shard 1: [A-H]
├─ Shard 2: [I-P]  
└─ Shard 3: [Q-Z]

Pros: Linear scalability
Cons: Cross-shard queries expensive
When: Clear partition key exists
2. Replication:
Master: [Complete Dataset] ← Writes
   ↓ Async replication
Replica 1: [Complete Dataset] ← Reads
Replica 2: [Complete Dataset] ← Reads

Pros: Read scalability, fault tolerance
Cons: Write bottleneck, lag
When: Read-heavy workloads
3. Caching:
Client → Cache → Database
         ↓   ↑
      [Hot Data]

Pros: Massive read performance
Cons: Consistency complexity
When: Temporal locality exists
State Consistency Spectrum:
Strong ←──────────────────────────────→ Eventual
  │                                          │
Linearizable                            DNS
  │                                          │
Sequential                              S3
  │                                          │
Causal                                  DynamoDB
  │                                          │
FIFO                                    Cassandra

Cost: $$$$                              $
Latency: High                           Low
Availability: Lower                     Higher
🎬 Real-World Example: Reddit's Sharding Journey
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
The Hidden Costs of State Distribution:
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
🔧 Try This: Consistent Hashing
pythonimport hashlib
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