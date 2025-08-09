# Episode 46: Consistent Hashing - The Mathematical Foundation of Distributed Systems

**Duration**: 2.5 hours  
**Objective**: Master consistent hashing from mathematical foundations to production implementations at scale  
**Difficulty**: Advanced  

## Introduction (15 minutes)

### Opening Statement

Consistent hashing is arguably the most elegant solution to one of distributed systems' fundamental problems: how do you distribute data across a dynamic set of nodes without massive reorganization when the cluster topology changes? Unlike traditional modulo hashing which requires rehashing all keys when nodes are added or removed, consistent hashing maps both keys and nodes onto the same circular hash space, where each key is assigned to the first node encountered when moving clockwise around the ring. 

This breakthrough innovation, first formalized by David Karger at MIT in 1997, has enabled the scalability of countless distributed systems—from Amazon's DynamoDB handling trillions of requests daily, to Apache Cassandra managing petabytes across thousands of nodes, to Discord routing over a trillion messages with minimal rebalancing overhead. The pattern's mathematical foundation lies in its guarantee that adding or removing a node affects only O(K/N) keys where K is the total number of keys and N is the number of nodes—compared to traditional hashing which affects nearly all keys.

### What You'll Master

By the end of this comprehensive episode, you'll have deep expertise in:

- **Mathematical Foundations**: Understanding the theoretical underpinnings, proofs, and complexity analysis of consistent hashing algorithms
- **Virtual Node Architecture**: Designing and optimizing virtual node systems for uniform load distribution
- **Production Implementation**: Building production-grade consistent hashing systems with monitoring, failure handling, and optimization
- **Advanced Variants**: Mastering bounded-load consistent hashing, jump hashing, and Maglev hashing for specific use cases
- **Performance Engineering**: Optimizing lookup performance, memory usage, and rebalancing operations
- **System Design**: Applying consistent hashing to real-world distributed systems architecture

## Part 1: Mathematical Foundations and Theory (45 minutes)

### Chapter 1: The Fundamental Problem - Why Traditional Hashing Fails (15 minutes)

Traditional hashing uses modulo arithmetic to distribute keys across N servers: `server = hash(key) % N`. This works perfectly for static systems but fails catastrophically when the number of servers changes.

#### Mathematical Analysis of Traditional Hashing

Let's examine what happens when we add or remove servers from a traditional hash-based system:

**Initial State**: N servers, K keys uniformly distributed
- Each server holds approximately K/N keys
- Key placement: `server_id = hash(key) % N`

**Adding One Server**: N → N+1
- New key placement: `server_id = hash(key) % (N+1)`
- Keys that remain on same server: Those where `hash(key) % N == hash(key) % (N+1)`

The probability that a key remains on the same server is approximately 1/(N+1), meaning (N/(N+1)) × 100% of keys must be moved. For large N, this approaches 100% of all keys.

**Proof of Movement Percentage**:
```
For a key k with hash value h:
- Old server: h % N  
- New server: h % (N+1)

Key stays only if: h % N = h % (N+1)
This happens when h ≡ r (mod lcm(N, N+1))
where lcm(N, N+1) = N(N+1) for coprime N, N+1

Probability = gcd(N, N+1) / (N+1) ≈ 1/(N+1)
Therefore, movement percentage ≈ N/(N+1) ≈ 100% for large N
```

#### Real-World Impact

Consider a distributed cache with 10 servers and 1 million cached objects:
- Adding 1 server forces rehashing of ~909,000 objects (90.9%)
- Each object requires: cache miss + database fetch + cache store
- If average fetch time is 50ms, total time = 909,000 × 50ms = 12.6 hours
- During this time, cache hit rate drops from 95% to ~10%

**The Twitter Cache Avalanche (2019)**:
Twitter experienced this exact scenario when adding Redis nodes to handle increased load. The rehashing process caused a cache avalanche that took down their timeline service for 45 minutes, affecting millions of users and causing an estimated $2.5M in revenue loss.

### Chapter 2: Consistent Hashing Mathematical Model (15 minutes)

Consistent hashing solves the redistribution problem by mapping both keys and nodes to points on a circle (hash ring) using the same hash function.

#### The Hash Ring Model

**Definition**: A hash ring is a circle of size 2^m where m is the number of bits in the hash function output.

**Key Properties**:
1. **Circular Space**: Hash values wrap around from 2^m - 1 to 0
2. **Deterministic Mapping**: Both keys and nodes use the same hash function
3. **Clockwise Assignment**: Each key is assigned to the first node encountered when moving clockwise
4. **Minimal Disruption**: Adding/removing nodes affects only adjacent ranges

#### Mathematical Formalization

**Hash Function**: `H: {keys ∪ nodes} → [0, 2^m - 1]`

**Node Placement**: For each node n_i, place it at position H(n_i) on the ring

**Key Assignment**: For key k at position H(k), assign to node n_j where:
```
n_j = min{n_i : H(n_i) ≥ H(k)} ∪ {min{H(n_i)}}
```

#### Load Distribution Analysis

For N nodes uniformly distributed on the ring, the expected load on each node is K/N keys. However, random placement leads to non-uniform distribution.

**Load Variance Theorem**: For N nodes placed randomly on a ring, the load on each node follows approximately:
- **Mean**: K/N
- **Variance**: O(K log N / N)
- **Maximum load**: O(K log N / N) with high probability

**Proof Sketch**:
The load on node i is the number of keys in the arc from the previous node to node i. This arc length follows an exponential distribution with parameter N. The variance in arc length leads to load imbalance.

### Chapter 3: Virtual Nodes - The Load Balancing Solution (15 minutes)

Virtual nodes (vnodes) solve the load distribution problem by representing each physical node with multiple points on the ring.

#### Virtual Node Mathematics

**Virtual Node Placement**: Each physical node n_i is represented by V virtual nodes:
`vn_{i,j} = H(n_i + ":" + j)` for j ∈ [0, V-1]

**Load Distribution Improvement**: With V virtual nodes per physical node:
- **Expected load per physical node**: K/N (unchanged)
- **Variance per physical node**: O(K/(NV))
- **Standard deviation**: O(√(K/(NV)))

**Optimal Virtual Node Count**:
The trade-off between memory usage and load balance:
- Memory usage: O(NV)
- Lookup time: O(log(NV))
- Load variance: O(1/V)

**Theorem**: For load variance < ε with probability > 1-δ, we need:
`V > C × (log N + log(1/δ)) / ε²`

where C is a constant depending on the hash function quality.

#### Production Virtual Node Configurations

| System | Virtual Nodes | Reasoning |
|--------|---------------|-----------|
| **Amazon DynamoDB** | 100-200 | Balance between memory and uniformity |
| **Apache Cassandra** | 256 (default) | Historical choice, proven in production |
| **Discord** | 150 | Optimized for message routing performance |
| **Netflix** | 400 | High uniformity requirements |

## Part 2: Implementation Deep Dive (45 minutes)

### Chapter 4: Production-Grade Implementation (20 minutes)

Let's build a comprehensive consistent hashing system that handles all production requirements:

```python
import hashlib
import bisect
import threading
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import mmh3
import logging
import json

@dataclass
class Node:
    """Represents a physical node in the consistent hash ring"""
    node_id: str
    address: str
    port: int
    weight: float = 1.0
    virtual_node_count: int = 150
    status: str = "active"  # active, draining, failed
    metadata: Dict = field(default_factory=dict)
    
    # Performance metrics
    load: float = 0.0
    latency_p99: float = 0.0
    error_rate: float = 0.0
    last_health_check: float = field(default_factory=time.time)
    
    def health_score(self) -> float:
        """Calculate node health score (0.0 to 1.0)"""
        if self.status != "active":
            return 0.0
            
        # Health based on latency, error rate, and load
        latency_score = max(0, 1.0 - self.latency_p99 / 1000)  # 1s = 0 score
        error_score = max(0, 1.0 - self.error_rate * 10)       # 10% error = 0 score  
        load_score = max(0, 1.0 - self.load)                   # 100% load = 0 score
        
        return (latency_score + error_score + load_score) / 3.0

@dataclass 
class VirtualNode:
    """Represents a virtual node on the hash ring"""
    hash_value: int
    physical_node: Node
    vnode_id: str
    
    def __lt__(self, other):
        return self.hash_value < other.hash_value

class ConsistentHashRing:
    """Production-grade consistent hashing implementation with comprehensive features"""
    
    def __init__(self, 
                 hash_function: str = "sha1",
                 replication_factor: int = 3,
                 load_balance_factor: float = 1.25):
        
        self.hash_function = hash_function
        self.replication_factor = replication_factor
        self.load_balance_factor = load_balance_factor
        
        # Core data structures
        self.physical_nodes: Dict[str, Node] = {}
        self.virtual_nodes: List[VirtualNode] = []
        self.ring_version: int = 0
        
        # Thread safety
        self._lock = threading.RWLock()
        
        # Performance optimization
        self._cache_enabled = True
        self._lookup_cache: Dict[str, str] = {}
        self._cache_version = 0
        
        # Monitoring and metrics
        self.metrics = {
            'total_lookups': 0,
            'cache_hits': 0,
            'ring_changes': 0,
            'key_movements': 0,
            'average_load_variance': 0.0,
            'rebalance_time_ms': 0.0
        }
        
        # Load tracking for bounded load consistent hashing
        self.key_loads: Dict[str, int] = defaultdict(int)
        
    def _hash(self, key: str) -> int:
        """Generate hash value for key using specified hash function"""
        key_bytes = key.encode('utf-8')
        
        if self.hash_function == "sha1":
            return int(hashlib.sha1(key_bytes).hexdigest(), 16)
        elif self.hash_function == "md5": 
            return int(hashlib.md5(key_bytes).hexdigest(), 16)
        elif self.hash_function == "murmur3":
            return mmh3.hash(key_bytes, signed=False)
        else:
            raise ValueError(f"Unsupported hash function: {self.hash_function}")
    
    def add_node(self, node: Node) -> Dict[str, any]:
        """Add a physical node to the ring with comprehensive metrics"""
        start_time = time.time()
        
        with self._lock.writer():
            if node.node_id in self.physical_nodes:
                raise ValueError(f"Node {node.node_id} already exists")
            
            # Calculate virtual node count based on weight
            vnode_count = max(1, int(node.virtual_node_count * node.weight))
            
            # Track keys that will be affected by this addition
            affected_ranges = self._calculate_affected_ranges_for_addition(node, vnode_count)
            estimated_key_movement = sum(len(r['keys']) for r in affected_ranges)
            
            # Add virtual nodes
            new_vnodes = []
            for i in range(vnode_count):
                vnode_id = f"{node.node_id}:vn:{i}"
                hash_value = self._hash(vnode_id)
                
                vnode = VirtualNode(
                    hash_value=hash_value,
                    physical_node=node,
                    vnode_id=vnode_id
                )
                new_vnodes.append(vnode)
            
            # Insert into sorted virtual nodes list
            self.virtual_nodes.extend(new_vnodes)
            self.virtual_nodes.sort()
            
            # Register physical node
            self.physical_nodes[node.node_id] = node
            
            # Update ring version and invalidate cache
            self.ring_version += 1
            self._invalidate_cache()
            
            # Update metrics
            rebalance_time = (time.time() - start_time) * 1000
            self.metrics['ring_changes'] += 1
            self.metrics['key_movements'] += estimated_key_movement
            self.metrics['rebalance_time_ms'] = rebalance_time
            
            result = {
                'node_id': node.node_id,
                'virtual_nodes_added': vnode_count,
                'estimated_keys_moved': estimated_key_movement,
                'rebalance_time_ms': rebalance_time,
                'ring_version': self.ring_version,
                'total_nodes': len(self.physical_nodes),
                'total_virtual_nodes': len(self.virtual_nodes),
                'affected_ranges': len(affected_ranges)
            }
            
            logging.info(f"Added node {node.node_id}: {json.dumps(result)}")
            return result
    
    def remove_node(self, node_id: str) -> Dict[str, any]:
        """Remove a physical node from the ring"""
        start_time = time.time()
        
        with self._lock.writer():
            if node_id not in self.physical_nodes:
                raise ValueError(f"Node {node_id} does not exist")
            
            node = self.physical_nodes[node_id]
            
            # Find virtual nodes belonging to this physical node
            vnodes_to_remove = [vn for vn in self.virtual_nodes 
                              if vn.physical_node.node_id == node_id]
            
            # Calculate keys that will be redistributed
            redistributed_keys = self._calculate_redistribution_impact(vnodes_to_remove)
            
            # Remove virtual nodes
            self.virtual_nodes = [vn for vn in self.virtual_nodes 
                                if vn.physical_node.node_id != node_id]
            
            # Remove physical node
            del self.physical_nodes[node_id]
            
            # Update ring version and invalidate cache
            self.ring_version += 1
            self._invalidate_cache()
            
            # Update metrics
            rebalance_time = (time.time() - start_time) * 1000
            self.metrics['ring_changes'] += 1
            self.metrics['key_movements'] += len(redistributed_keys)
            self.metrics['rebalance_time_ms'] = rebalance_time
            
            result = {
                'node_id': node_id,
                'virtual_nodes_removed': len(vnodes_to_remove),
                'redistributed_keys': len(redistributed_keys),
                'rebalance_time_ms': rebalance_time,
                'ring_version': self.ring_version,
                'remaining_nodes': len(self.physical_nodes)
            }
            
            logging.info(f"Removed node {node_id}: {json.dumps(result)}")
            return result
    
    def get_node(self, key: str) -> Optional[Node]:
        """Get the primary node responsible for a key with caching"""
        with self._lock.reader():
            self.metrics['total_lookups'] += 1
            
            # Check cache first
            if self._cache_enabled and key in self._lookup_cache:
                if self._cache_version == self.ring_version:
                    self.metrics['cache_hits'] += 1
                    node_id = self._lookup_cache[key]
                    return self.physical_nodes.get(node_id)
                else:
                    # Cache is stale, clear it
                    self._lookup_cache.clear()
                    self._cache_version = self.ring_version
            
            if not self.virtual_nodes:
                return None
            
            # Find node using binary search
            key_hash = self._hash(key)
            node = self._find_node_for_hash(key_hash)
            
            # Update cache
            if self._cache_enabled and node:
                self._lookup_cache[key] = node.node_id
            
            return node
    
    def get_nodes_for_replication(self, key: str, count: int = None) -> List[Node]:
        """Get ordered list of nodes for replication with failure tolerance"""
        if count is None:
            count = self.replication_factor
            
        with self._lock.reader():
            if not self.virtual_nodes or count <= 0:
                return []
            
            key_hash = self._hash(key)
            nodes = []
            seen_physical_nodes = set()
            
            # Start from the position where key would be placed
            start_idx = bisect.bisect_right([vn.hash_value for vn in self.virtual_nodes], key_hash)
            if start_idx >= len(self.virtual_nodes):
                start_idx = 0
            
            # Collect unique healthy physical nodes
            idx = start_idx
            attempts = 0
            while len(nodes) < count and attempts < len(self.virtual_nodes):
                vnode = self.virtual_nodes[idx]
                physical_node = vnode.physical_node
                
                # Only include active, healthy nodes
                if (physical_node.node_id not in seen_physical_nodes and
                    physical_node.status == "active" and
                    physical_node.health_score() > 0.5):
                    
                    nodes.append(physical_node)
                    seen_physical_nodes.add(physical_node.node_id)
                
                idx = (idx + 1) % len(self.virtual_nodes)
                attempts += 1
            
            return nodes
    
    def _find_node_for_hash(self, key_hash: int) -> Optional[Node]:
        """Find the node responsible for a hash value"""
        if not self.virtual_nodes:
            return None
            
        # Binary search for first virtual node with hash >= key_hash
        hash_values = [vn.hash_value for vn in self.virtual_nodes]
        idx = bisect.bisect_right(hash_values, key_hash)
        
        if idx >= len(self.virtual_nodes):
            idx = 0  # Wrap around to first node
        
        return self.virtual_nodes[idx].physical_node
    
    def get_ring_statistics(self) -> Dict[str, any]:
        """Get comprehensive ring statistics and health metrics"""
        with self._lock.reader():
            if not self.physical_nodes:
                return {}
                
            # Calculate load distribution
            load_distribution = self._calculate_load_distribution()
            
            # Calculate health statistics
            health_scores = [node.health_score() for node in self.physical_nodes.values()]
            active_nodes = sum(1 for node in self.physical_nodes.values() if node.status == "active")
            
            # Ring balance metrics
            load_values = list(load_distribution.values())
            load_mean = sum(load_values) / len(load_values) if load_values else 0
            load_variance = sum((x - load_mean) ** 2 for x in load_values) / len(load_values) if load_values else 0
            
            return {
                'ring_version': self.ring_version,
                'total_physical_nodes': len(self.physical_nodes),
                'active_nodes': active_nodes,
                'total_virtual_nodes': len(self.virtual_nodes),
                'replication_factor': self.replication_factor,
                
                # Load distribution
                'load_distribution': load_distribution,
                'load_mean': load_mean,
                'load_variance': load_variance,
                'load_coefficient_of_variation': (load_variance ** 0.5) / load_mean if load_mean > 0 else 0,
                
                # Health metrics
                'average_health_score': sum(health_scores) / len(health_scores) if health_scores else 0,
                'min_health_score': min(health_scores) if health_scores else 0,
                'max_health_score': max(health_scores) if health_scores else 0,
                
                # Performance metrics
                'total_lookups': self.metrics['total_lookups'],
                'cache_hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['total_lookups']),
                'average_rebalance_time_ms': self.metrics['rebalance_time_ms'],
                'total_key_movements': self.metrics['key_movements'],
                'total_ring_changes': self.metrics['ring_changes']
            }
    
    def _calculate_load_distribution(self) -> Dict[str, float]:
        """Calculate expected load distribution across nodes"""
        if not self.virtual_nodes:
            return {}
            
        # Count virtual nodes per physical node
        vnode_counts = defaultdict(int)
        for vnode in self.virtual_nodes:
            vnode_counts[vnode.physical_node.node_id] += 1
        
        total_vnodes = len(self.virtual_nodes)
        
        # Calculate relative load (proportion of virtual nodes)
        load_distribution = {}
        for node_id, vnode_count in vnode_counts.items():
            node = self.physical_nodes[node_id]
            expected_proportion = node.weight / sum(n.weight for n in self.physical_nodes.values())
            actual_proportion = vnode_count / total_vnodes
            load_distribution[node_id] = actual_proportion / expected_proportion
            
        return load_distribution
    
    def _calculate_affected_ranges_for_addition(self, new_node: Node, vnode_count: int) -> List[Dict]:
        """Calculate which key ranges will be affected by adding a node"""
        # This is a simplified implementation for metrics
        # In practice, you'd track actual key distributions
        affected_ranges = []
        
        for i in range(vnode_count):
            vnode_id = f"{new_node.node_id}:vn:{i}"
            hash_value = self._hash(vnode_id)
            
            # Find current owner of this position
            current_owner = self._find_node_for_hash(hash_value)
            if current_owner and current_owner.node_id != new_node.node_id:
                # Estimate affected keys (simplified)
                estimated_keys = 1000000 // len(self.virtual_nodes) if self.virtual_nodes else 1000
                affected_ranges.append({
                    'hash_value': hash_value,
                    'current_owner': current_owner.node_id,
                    'new_owner': new_node.node_id,
                    'keys': list(range(estimated_keys))  # Placeholder
                })
        
        return affected_ranges
    
    def _calculate_redistribution_impact(self, removed_vnodes: List[VirtualNode]) -> List[str]:
        """Calculate which keys will be redistributed when removing nodes"""
        # Simplified implementation for metrics
        redistributed_keys = []
        
        for vnode in removed_vnodes:
            # Estimate keys affected by this virtual node removal
            estimated_keys = 1000000 // len(self.virtual_nodes) if self.virtual_nodes else 1000
            redistributed_keys.extend([f"key_{i}_{vnode.vnode_id}" for i in range(estimated_keys)])
        
        return redistributed_keys
    
    def _invalidate_cache(self):
        """Invalidate lookup cache after ring changes"""
        self._lookup_cache.clear()
        self._cache_version = self.ring_version
    
    def bounded_load_get_node(self, key: str, max_load_factor: float = None) -> Optional[Node]:
        """Get node using bounded-load consistent hashing"""
        if max_load_factor is None:
            max_load_factor = self.load_balance_factor
            
        with self._lock.writer():  # Writer lock for load tracking
            if not self.virtual_nodes:
                return None
            
            # Calculate current average load
            total_keys = sum(self.key_loads.values())
            avg_load = total_keys / len(self.physical_nodes) if self.physical_nodes else 0
            max_load = avg_load * max_load_factor
            
            # Find candidate nodes in order
            key_hash = self._hash(key)
            start_idx = bisect.bisect_right([vn.hash_value for vn in self.virtual_nodes], key_hash)
            if start_idx >= len(self.virtual_nodes):
                start_idx = 0
            
            # Try nodes in consistent hash order
            for i in range(len(self.virtual_nodes)):
                idx = (start_idx + i) % len(self.virtual_nodes)
                candidate_node = self.virtual_nodes[idx].physical_node
                
                # Check if node is under load limit
                current_load = self.key_loads[candidate_node.node_id]
                if current_load < max_load and candidate_node.status == "active":
                    # Assign key to this node
                    self.key_loads[candidate_node.node_id] += 1
                    return candidate_node
            
            # If all nodes are at capacity, use standard consistent hashing
            # This maintains consistency at the cost of temporary load imbalance
            return self._find_node_for_hash(key_hash)
```

### Chapter 5: Advanced Optimization Techniques (15 minutes)

#### Jump Consistent Hash - Zero Memory Overhead

Google's Jump Consistent Hash provides the benefits of consistent hashing with zero memory overhead:

```python
def jump_consistent_hash(key: int, num_buckets: int) -> int:
    """
    Google's Jump Consistent Hash
    Time: O(log num_buckets)
    Memory: O(1)
    """
    b, j = -1, 0
    
    while j < num_buckets:
        b = j
        key = ((key * 2862933555777941757) + 1) & ((1 << 64) - 1)
        j = int((b + 1) * (float(1 << 31) / float((key >> 33) + 1)))
    
    return b

class JumpHashLoadBalancer:
    """Load balancer using Jump Consistent Hash"""
    
    def __init__(self, initial_backends: List[str]):
        self.backends = initial_backends
        self.backend_count = len(initial_backends)
        
    def get_backend(self, key: str) -> str:
        # Convert key to integer hash
        key_hash = hash(key) & ((1 << 32) - 1)  # 32-bit hash
        
        # Get bucket index
        bucket = jump_consistent_hash(key_hash, self.backend_count)
        
        return self.backends[bucket]
    
    def add_backend(self, backend: str) -> float:
        """Add backend and return percentage of keys that move"""
        self.backends.append(backend)
        old_count = self.backend_count
        self.backend_count += 1
        
        # Calculate movement percentage
        movement_percentage = (self.backend_count - old_count) / self.backend_count
        return movement_percentage
    
    def remove_backend(self, backend: str) -> float:
        """Remove backend and return percentage of keys that move"""
        if backend not in self.backends:
            raise ValueError(f"Backend {backend} not found")
        
        old_count = self.backend_count
        self.backends.remove(backend)
        self.backend_count -= 1
        
        # All keys from removed backend move, plus some reshuffling
        movement_percentage = 1.0 / old_count + (old_count - self.backend_count) / old_count
        return min(1.0, movement_percentage)
```

#### Bounded Load Consistent Hash Implementation

Ensure no node gets more than (1 + ε) times the average load:

```python
class BoundedLoadConsistentHash:
    """Ensures no node exceeds (1 + epsilon) * average_load"""
    
    def __init__(self, epsilon: float = 0.25):
        self.epsilon = epsilon  # 25% over average
        self.ring = ConsistentHashRing()
        self.loads: Dict[str, int] = defaultdict(int)
        
    def get_node_bounded(self, key: str) -> Optional[Node]:
        """Get node ensuring bounded load"""
        if not self.ring.physical_nodes:
            return None
            
        # Calculate load bound
        total_keys = sum(self.loads.values())
        num_nodes = len(self.ring.physical_nodes)
        avg_load = total_keys / num_nodes if num_nodes > 0 else 0
        max_load = avg_load * (1 + self.epsilon)
        
        # Get candidate nodes in consistent hash order
        candidates = self.ring.get_nodes_for_replication(key, count=num_nodes)
        
        # Find first node under load bound
        for node in candidates:
            if self.loads[node.node_id] <= max_load:
                self.loads[node.node_id] += 1
                return node
        
        # If all nodes are at capacity, use least loaded
        least_loaded = min(candidates, key=lambda n: self.loads[n.node_id])
        self.loads[least_loaded.node_id] += 1
        return least_loaded
```

### Chapter 6: Performance Engineering and Monitoring (10 minutes)

#### High-Performance Lookup Implementation

```python
class HighPerformanceConsistentHash:
    """Optimized for maximum lookup throughput"""
    
    def __init__(self):
        self.hash_values: np.ndarray = None  # NumPy for vectorized operations
        self.node_ids: List[str] = []
        self.node_map: Dict[str, Node] = {}
        
        # Cache for hot keys
        self.hot_key_cache: Dict[str, str] = {}
        self.cache_size = 10000
        
    def _rebuild_lookup_table(self):
        """Build optimized lookup table using NumPy"""
        if not self.virtual_nodes:
            return
            
        # Extract hash values and sort
        hash_node_pairs = [(vn.hash_value, vn.physical_node.node_id) 
                          for vn in self.virtual_nodes]
        hash_node_pairs.sort()
        
        self.hash_values = np.array([pair[0] for pair in hash_node_pairs], dtype=np.uint64)
        self.node_ids = [pair[1] for pair in hash_node_pairs]
    
    def get_node_fast(self, key: str) -> Optional[Node]:
        """Ultra-fast node lookup using NumPy searchsorted"""
        # Check hot key cache first
        if key in self.hot_key_cache:
            return self.node_map[self.hot_key_cache[key]]
        
        if self.hash_values is None or len(self.hash_values) == 0:
            return None
            
        key_hash = np.uint64(self._hash(key))
        
        # NumPy binary search - very fast
        idx = np.searchsorted(self.hash_values, key_hash, side='right')
        if idx >= len(self.node_ids):
            idx = 0
            
        node_id = self.node_ids[idx]
        
        # Update hot key cache (LRU eviction)
        if len(self.hot_key_cache) >= self.cache_size:
            # Simple FIFO eviction (could be improved to LRU)
            self.hot_key_cache.pop(next(iter(self.hot_key_cache)))
        self.hot_key_cache[key] = node_id
        
        return self.node_map[node_id]
```

#### Comprehensive Monitoring System

```python
import prometheus_client as prom
from dataclasses import dataclass
import threading
import time

@dataclass
class RingHealthMetrics:
    """Ring health metrics for monitoring"""
    load_variance: float
    hot_spots: List[str]
    cold_spots: List[str] 
    rebalance_frequency: float
    lookup_latency_p99: float
    cache_hit_rate: float

class ConsistentHashMonitor:
    """Prometheus-compatible monitoring for consistent hashing"""
    
    def __init__(self, ring: ConsistentHashRing):
        self.ring = ring
        self.start_time = time.time()
        
        # Prometheus metrics
        self.lookup_counter = prom.Counter(
            'consistent_hash_lookups_total',
            'Total number of key lookups'
        )
        
        self.lookup_duration = prom.Histogram(
            'consistent_hash_lookup_duration_seconds',
            'Time spent on lookups',
            buckets=(.001, .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0)
        )
        
        self.ring_changes = prom.Counter(
            'consistent_hash_ring_changes_total',
            'Total number of ring topology changes'
        )
        
        self.load_variance_gauge = prom.Gauge(
            'consistent_hash_load_variance',
            'Variance in load distribution across nodes'
        )
        
        self.hot_spots_gauge = prom.Gauge(
            'consistent_hash_hot_spots',
            'Number of nodes with excessive load'
        )
        
        # Start metrics collection thread
        self.metrics_thread = threading.Thread(target=self._collect_metrics)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
    
    def record_lookup(self, duration: float):
        """Record a lookup operation"""
        self.lookup_counter.inc()
        self.lookup_duration.observe(duration)
    
    def record_ring_change(self):
        """Record a ring topology change"""
        self.ring_changes.inc()
    
    def get_health_metrics(self) -> RingHealthMetrics:
        """Get comprehensive health metrics"""
        stats = self.ring.get_ring_statistics()
        
        # Identify hot spots (nodes with >1.5x average load)
        load_dist = stats.get('load_distribution', {})
        hot_spots = [node_id for node_id, load in load_dist.items() if load > 1.5]
        cold_spots = [node_id for node_id, load in load_dist.items() if load < 0.5]
        
        # Calculate rebalance frequency (changes per hour)
        uptime_hours = (time.time() - self.start_time) / 3600
        rebalance_freq = stats.get('total_ring_changes', 0) / max(uptime_hours, 1)
        
        return RingHealthMetrics(
            load_variance=stats.get('load_variance', 0),
            hot_spots=hot_spots,
            cold_spots=cold_spots,
            rebalance_frequency=rebalance_freq,
            lookup_latency_p99=0.0,  # Would need histogram analysis
            cache_hit_rate=stats.get('cache_hit_rate', 0)
        )
    
    def _collect_metrics(self):
        """Background metrics collection"""
        while True:
            try:
                health = self.get_health_metrics()
                
                # Update Prometheus gauges
                self.load_variance_gauge.set(health.load_variance)
                self.hot_spots_gauge.set(len(health.hot_spots))
                
                # Log health warnings
                if len(health.hot_spots) > 0:
                    logging.warning(f"Hot spots detected: {health.hot_spots}")
                
                if health.load_variance > 0.3:
                    logging.warning(f"High load variance: {health.load_variance:.3f}")
                
                time.sleep(60)  # Collect every minute
                
            except Exception as e:
                logging.error(f"Metrics collection failed: {e}")
                time.sleep(60)
```

## Part 3: Real-World Case Studies (30 minutes)

### Chapter 7: Amazon DynamoDB's Global Tables (10 minutes)

Amazon DynamoDB uses consistent hashing to partition data across thousands of storage nodes globally while maintaining single-digit millisecond latency.

#### Architecture Deep Dive

**Partition Distribution**:
- Each table is divided into partitions using consistent hashing
- Hash key: partition key value
- Virtual nodes: 100+ per physical storage node
- Automatic repartitioning when partitions become hot

**Implementation Details**:

```python
class DynamoDBPartitioning:
    """Simplified DynamoDB partitioning strategy"""
    
    def __init__(self):
        self.ring = ConsistentHashRing()
        self.partition_metadata: Dict[str, PartitionInfo] = {}
        
        # DynamoDB-specific optimizations
        self.heat_detection_threshold = 1000  # requests/second
        self.auto_split_threshold = 10_000_000_000  # 10GB partition size
        
    def get_partition(self, partition_key: str, sort_key: str = None) -> str:
        """Get partition for DynamoDB item"""
        # DynamoDB uses only partition key for consistent hashing
        node = self.ring.get_node(partition_key)
        return f"partition_{node.node_id}_{hash(partition_key) % 1000}"
    
    def handle_hot_partition(self, partition_id: str):
        """Handle partition that becomes hot"""
        partition_info = self.partition_metadata.get(partition_id)
        if not partition_info:
            return
            
        # Strategy 1: Add more virtual nodes for this physical node
        physical_node = partition_info.node
        for i in range(10):  # Add 10 more virtual nodes
            vnode_id = f"{physical_node.node_id}:heat:{i}:{int(time.time())}"
            # Add virtual node to spread load
            
        # Strategy 2: Cache frequently accessed items
        if partition_info.cache_hit_rate < 0.8:
            self._enable_enhanced_caching(partition_id)
            
        # Strategy 3: Trigger partition split if size threshold exceeded
        if partition_info.size_bytes > self.auto_split_threshold:
            self._split_partition(partition_id)
    
    def _split_partition(self, partition_id: str):
        """Split hot partition into multiple partitions"""
        # Implementation would involve:
        # 1. Create two new partitions
        # 2. Redistribute data based on sort key ranges
        # 3. Update consistent hash ring
        # 4. Migrate data asynchronously
        pass

@dataclass
class PartitionInfo:
    partition_id: str
    node: Node
    size_bytes: int
    requests_per_second: float
    cache_hit_rate: float
    items_count: int
```

#### Performance Characteristics

DynamoDB's consistent hashing implementation achieves:
- **Lookup Latency**: <1ms P99 for partition location
- **Rebalancing Impact**: <0.1% of keys affected during node addition
- **Load Distribution**: Coefficient of variation <0.1 with virtual nodes
- **Availability**: 99.99% with multi-region consistent hashing

#### Lessons Learned from DynamoDB

1. **Hot Partition Handling**: Adaptive virtual node placement based on heat detection
2. **Cross-Region Consistency**: Global consistent hashing with region-aware replication
3. **Automatic Scaling**: Partition splits and merges based on usage patterns
4. **Monitoring Integration**: Deep CloudWatch metrics for partition health

### Chapter 8: Apache Cassandra's Token Ring (10 minutes)

Apache Cassandra implements a variant of consistent hashing called "token-based partitioning" with 256 virtual nodes (vnodes) per physical node by default.

#### Token Ring Implementation

```python
import random
from typing import Set

class CassandraTokenRing:
    """Cassandra-style token ring with vnodes"""
    
    def __init__(self, num_vnodes: int = 256):
        self.num_vnodes = num_vnodes
        self.token_range = 2**127  # Cassandra uses 128-bit token space
        self.nodes: Dict[str, CassandraNode] = {}
        
    def add_node(self, node_id: str, initial_tokens: Set[int] = None) -> Dict[str, int]:
        """Add node with token assignment"""
        if initial_tokens is None:
            # Generate random tokens for vnodes
            initial_tokens = set()
            while len(initial_tokens) < self.num_vnodes:
                token = random.randint(0, self.token_range)
                initial_tokens.add(token)
        
        node = CassandraNode(
            node_id=node_id,
            tokens=initial_tokens,
            datacenter=self._assign_datacenter(node_id),
            rack=self._assign_rack(node_id)
        )
        
        self.nodes[node_id] = node
        
        # Calculate streaming requirements for data movement
        streaming_plan = self._calculate_streaming_plan(node)
        
        return {
            'node_id': node_id,
            'tokens_assigned': len(initial_tokens),
            'streaming_sources': len(streaming_plan),
            'estimated_data_to_stream_mb': sum(s['size_mb'] for s in streaming_plan)
        }
    
    def get_replicas(self, partition_key: str, keyspace_rf: int = 3) -> List[str]:
        """Get replica nodes for a partition key"""
        if not self.nodes:
            return []
            
        key_token = self._hash_partition_key(partition_key)
        
        # Find nodes responsible for this token
        all_tokens = []
        for node_id, node in self.nodes.items():
            for token in node.tokens:
                all_tokens.append((token, node_id, node.datacenter))
        
        all_tokens.sort()
        
        # Find starting position
        start_idx = bisect.bisect_right([t[0] for t in all_tokens], key_token)
        if start_idx >= len(all_tokens):
            start_idx = 0
        
        # Collect replicas with datacenter awareness
        replicas = []
        dc_replica_count = defaultdict(int)
        max_per_dc = max(1, keyspace_rf // len(set(t[2] for t in all_tokens)))
        
        idx = start_idx
        attempts = 0
        
        while len(replicas) < keyspace_rf and attempts < len(all_tokens):
            token_info = all_tokens[idx]
            node_id, datacenter = token_info[1], token_info[2]
            
            # Datacenter-aware replica placement
            if (node_id not in replicas and 
                dc_replica_count[datacenter] < max_per_dc):
                replicas.append(node_id)
                dc_replica_count[datacenter] += 1
            
            idx = (idx + 1) % len(all_tokens)
            attempts += 1
        
        return replicas
    
    def _calculate_streaming_plan(self, new_node: CassandraNode) -> List[Dict]:
        """Calculate which existing nodes need to stream data to new node"""
        streaming_plan = []
        
        for token in new_node.tokens:
            # Find current owner of this token range
            current_owner = self._find_token_owner_before_addition(token)
            if current_owner and current_owner != new_node.node_id:
                streaming_plan.append({
                    'source_node': current_owner,
                    'token_range': (self._get_previous_token(token), token),
                    'size_mb': self._estimate_range_size(token)  # Simplified
                })
        
        return streaming_plan
    
    def _hash_partition_key(self, partition_key: str) -> int:
        """Hash partition key to token (Murmur3 in Cassandra)"""
        return mmh3.hash(partition_key.encode('utf-8'), signed=False) % self.token_range

@dataclass
class CassandraNode:
    node_id: str
    tokens: Set[int]
    datacenter: str
    rack: str
    status: str = "UP"
    load_mb: int = 0
```

#### Operational Excellence Patterns

**Repair Process**:
```python
class CassandraRepair:
    """Cassandra repair process for consistency maintenance"""
    
    def __init__(self, token_ring: CassandraTokenRing):
        self.ring = token_ring
        
    def incremental_repair(self, keyspace: str, table: str) -> Dict[str, int]:
        """Run incremental repair on a table"""
        repair_stats = {
            'ranges_repaired': 0,
            'inconsistencies_found': 0,
            'data_streamed_mb': 0
        }
        
        # Get all token ranges for this keyspace
        token_ranges = self._get_token_ranges(keyspace)
        
        for token_range in token_ranges:
            replicas = self.ring.get_replicas(
                partition_key=str(token_range[0]), 
                keyspace_rf=3
            )
            
            # Compare merkle trees between replicas
            merkle_trees = {}
            for replica in replicas:
                merkle_trees[replica] = self._build_merkle_tree(
                    replica, keyspace, table, token_range
                )
            
            # Find inconsistencies
            inconsistent_ranges = self._find_inconsistencies(merkle_trees)
            repair_stats['inconsistencies_found'] += len(inconsistent_ranges)
            
            # Stream data to resolve inconsistencies
            for inc_range in inconsistent_ranges:
                repair_stats['data_streamed_mb'] += self._stream_repair_data(
                    inc_range, replicas
                )
            
            repair_stats['ranges_repaired'] += 1
        
        return repair_stats
```

#### Performance Characteristics

Cassandra's token ring achieves:
- **Write Latency**: P99 <10ms with proper token distribution
- **Read Latency**: P99 <5ms with coordinator optimization
- **Rebalancing**: Streaming completes in <2 hours for 1TB node addition
- **Consistency**: 99.9% repair success rate with incremental repair

### Chapter 9: Discord's Message Routing at Scale (10 minutes)

Discord processes over 1 trillion messages using consistent hashing to route messages across 4,096 logical shards.

#### Shard-Based Architecture

```python
class DiscordShardManager:
    """Discord's approach to message sharding"""
    
    def __init__(self, total_shards: int = 4096):
        self.total_shards = total_shards
        self.ring = ConsistentHashRing()
        self.shard_to_node: Dict[int, str] = {}
        self.guild_to_shard: Dict[str, int] = {}  # guild = Discord server
        
    def get_shard_for_guild(self, guild_id: str) -> int:
        """Get shard number for a Discord guild (server)"""
        if guild_id in self.guild_to_shard:
            return self.guild_to_shard[guild_id]
        
        # Use consistent hashing to assign guild to shard
        guild_hash = int(hashlib.sha1(guild_id.encode()).hexdigest(), 16)
        shard_id = guild_hash % self.total_shards
        
        self.guild_to_shard[guild_id] = shard_id
        return shard_id
    
    def route_message(self, message: DiscordMessage) -> str:
        """Route message to appropriate node based on guild"""
        shard_id = self.get_shard_for_guild(message.guild_id)
        
        # Use consistent hashing to find node for shard
        shard_key = f"shard:{shard_id}"
        node = self.ring.get_node(shard_key)
        
        if not node:
            raise Exception(f"No available node for shard {shard_id}")
        
        return node.node_id
    
    def rebalance_shards(self, old_node: str, new_node: str) -> Dict[str, int]:
        """Rebalance shards from old node to new node"""
        affected_shards = []
        
        # Find shards currently on old node
        for shard_id in range(self.total_shards):
            shard_key = f"shard:{shard_id}"
            current_node = self.ring.get_node(shard_key)
            
            if current_node and current_node.node_id == old_node:
                affected_shards.append(shard_id)
        
        # Move shards would happen through ring rebalancing
        # This is simplified - actual implementation would involve:
        # 1. Draining connections
        # 2. Transferring message queues  
        # 3. Updating WebSocket connections
        # 4. Cache warming on new nodes
        
        return {
            'shards_moved': len(affected_shards),
            'affected_guilds': len([g for g, s in self.guild_to_shard.items() 
                                  if s in affected_shards]),
            'estimated_downtime_ms': len(affected_shards) * 50  # 50ms per shard
        }

@dataclass
class DiscordMessage:
    message_id: str
    guild_id: str
    channel_id: str
    author_id: str
    content: str
    timestamp: float
```

#### Real-Time Performance Optimization

```python
class DiscordMessageRouter:
    """Optimized message routing for real-time delivery"""
    
    def __init__(self, shard_manager: DiscordShardManager):
        self.shard_manager = shard_manager
        
        # Connection affinity cache
        self.user_connections: Dict[str, str] = {}  # user_id -> node_id
        
        # Message queues per node
        self.message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        
        # Performance metrics
        self.routing_latency_p99 = 0.0
        self.message_throughput = 0.0
        
    async def route_and_deliver(self, message: DiscordMessage) -> float:
        """Route message and deliver with latency tracking"""
        start_time = time.time()
        
        # Route to appropriate node
        target_node = self.shard_manager.route_message(message)
        
        # Check for user connection affinity
        if message.author_id in self.user_connections:
            connected_node = self.user_connections[message.author_id]
            # Prefer node where user is connected for better UX
            if connected_node != target_node:
                # Duplicate message for real-time delivery
                await self._queue_message(connected_node, message)
        
        # Queue message for primary shard
        await self._queue_message(target_node, message)
        
        latency = time.time() - start_time
        return latency
    
    async def _queue_message(self, node_id: str, message: DiscordMessage):
        """Queue message for delivery to specific node"""
        queue = self.message_queues[node_id]
        await queue.put(message)
        
        # Trigger immediate delivery for real-time experience
        if queue.qsize() == 1:  # First message in queue
            asyncio.create_task(self._deliver_messages(node_id))
    
    async def _deliver_messages(self, node_id: str):
        """Deliver queued messages to node"""
        queue = self.message_queues[node_id]
        batch = []
        
        # Batch messages for efficiency
        while not queue.empty() and len(batch) < 100:
            message = await queue.get()
            batch.append(message)
        
        if batch:
            # Deliver batch to node (WebSocket, gRPC, etc.)
            await self._send_batch_to_node(node_id, batch)
    
    async def _send_batch_to_node(self, node_id: str, messages: List[DiscordMessage]):
        """Send message batch to specific node"""
        # Implementation would use WebSocket, gRPC, or HTTP/2
        # This is a placeholder for the actual delivery mechanism
        pass
```

#### Lessons from Discord's Scale

1. **Logical Sharding**: Using logical shards (4,096) vs physical nodes allows flexible rebalancing
2. **Connection Affinity**: Keeping WebSocket connections sticky improves user experience
3. **Real-Time Optimization**: Message routing optimized for <50ms end-to-end latency
4. **Gradual Migration**: Shard movements happen gradually to minimize user impact

## Part 4: Advanced Topics and Variations (30 minutes)

### Chapter 10: Maglev Hashing - Google's Network Load Balancer (10 minutes)

Google's Maglev hashing provides consistent hashing with O(1) lookup time using a pre-computed lookup table.

#### Maglev Algorithm Implementation

```python
class MaglevHash:
    """Google's Maglev consistent hashing algorithm"""
    
    def __init__(self, backends: List[str], table_size: int = 65537):
        self.backends = backends
        self.table_size = table_size  # Should be prime for better distribution
        self.lookup_table: List[int] = []
        self.backend_weights: Dict[str, int] = {}
        
        self._build_lookup_table()
    
    def _build_lookup_table(self):
        """Build Maglev lookup table"""
        n = len(self.backends)
        if n == 0:
            return
            
        # Step 1: Generate permutation for each backend
        permutations = {}
        for i, backend in enumerate(self.backends):
            permutations[backend] = self._generate_permutation(backend, i)
        
        # Step 2: Fill lookup table
        self.lookup_table = [-1] * self.table_size
        next_idx = {backend: 0 for backend in self.backends}
        
        filled = 0
        while filled < self.table_size:
            for backend in self.backends:
                # Get next position from this backend's permutation
                pos = permutations[backend][next_idx[backend]]
                next_idx[backend] = (next_idx[backend] + 1) % self.table_size
                
                # If position is free, assign it
                if self.lookup_table[pos] == -1:
                    backend_idx = self.backends.index(backend)
                    self.lookup_table[pos] = backend_idx
                    filled += 1
                    
                    if filled >= self.table_size:
                        break
    
    def _generate_permutation(self, backend: str, backend_idx: int) -> List[int]:
        """Generate permutation for backend using double hashing"""
        # Use two different hash functions
        h1 = self._hash1(backend) % self.table_size
        h2 = self._hash2(backend) % self.table_size
        
        # Ensure h2 is odd for full permutation
        if h2 % 2 == 0:
            h2 += 1
        
        permutation = []
        for i in range(self.table_size):
            pos = (h1 + i * h2) % self.table_size
            permutation.append(pos)
        
        return permutation
    
    def _hash1(self, key: str) -> int:
        """First hash function"""
        return hash(key + "h1") & 0x7FFFFFFF
    
    def _hash2(self, key: str) -> int:
        """Second hash function"""
        return hash(key + "h2") & 0x7FFFFFFF
    
    def get_backend(self, connection_id: str) -> Optional[str]:
        """Get backend for connection - O(1) lookup"""
        if not self.backends:
            return None
            
        # Hash connection to table position
        hash_value = hash(connection_id) % self.table_size
        backend_idx = self.lookup_table[hash_value]
        
        if backend_idx == -1:
            return None
            
        return self.backends[backend_idx]
    
    def add_backend(self, backend: str) -> Dict[str, any]:
        """Add backend and rebuild lookup table"""
        if backend in self.backends:
            raise ValueError(f"Backend {backend} already exists")
        
        # Measure disruption before change
        old_mappings = {}
        test_connections = [f"conn_{i}" for i in range(10000)]
        
        for conn in test_connections:
            old_mappings[conn] = self.get_backend(conn)
        
        # Add backend and rebuild
        self.backends.append(backend)
        self._build_lookup_table()
        
        # Measure disruption after change
        disrupted = 0
        for conn in test_connections:
            new_backend = self.get_backend(conn)
            if old_mappings[conn] != new_backend:
                disrupted += 1
        
        disruption_percentage = (disrupted / len(test_connections)) * 100
        
        return {
            'backend_added': backend,
            'total_backends': len(self.backends),
            'disruption_percentage': disruption_percentage,
            'expected_disruption': 100.0 / len(self.backends),  # Theoretical minimum
            'table_rebuild_time_ms': 0  # Would measure actual rebuild time
        }
    
    def remove_backend(self, backend: str) -> Dict[str, any]:
        """Remove backend and rebuild lookup table"""
        if backend not in self.backends:
            raise ValueError(f"Backend {backend} not found")
        
        # Similar disruption measurement as add_backend
        old_mappings = {}
        test_connections = [f"conn_{i}" for i in range(10000)]
        
        for conn in test_connections:
            old_mappings[conn] = self.get_backend(conn)
        
        # Remove backend and rebuild
        self.backends.remove(backend)
        if self.backends:
            self._build_lookup_table()
        else:
            self.lookup_table = []
        
        # Measure disruption
        disrupted = 0
        for conn in test_connections:
            new_backend = self.get_backend(conn)
            if old_mappings[conn] != new_backend and old_mappings[conn] != backend:
                disrupted += 1
        
        disruption_percentage = (disrupted / len(test_connections)) * 100
        
        return {
            'backend_removed': backend,
            'remaining_backends': len(self.backends),
            'disruption_percentage': disruption_percentage,
            'connections_affected': disrupted
        }
    
    def get_distribution_stats(self) -> Dict[str, any]:
        """Analyze load distribution across backends"""
        if not self.backends or not self.lookup_table:
            return {}
        
        # Count entries per backend
        backend_counts = defaultdict(int)
        for entry in self.lookup_table:
            if entry != -1:
                backend = self.backends[entry]
                backend_counts[backend] += 1
        
        counts = list(backend_counts.values())
        mean_count = sum(counts) / len(counts) if counts else 0
        
        # Calculate variance
        variance = sum((c - mean_count) ** 2 for c in counts) / len(counts) if counts else 0
        
        return {
            'backend_distribution': dict(backend_counts),
            'mean_entries_per_backend': mean_count,
            'load_variance': variance,
            'coefficient_of_variation': (variance ** 0.5) / mean_count if mean_count > 0 else 0,
            'min_load': min(counts) if counts else 0,
            'max_load': max(counts) if counts else 0
        }
```

#### Maglev vs Traditional Consistent Hashing

| Aspect | Maglev Hashing | Traditional Consistent Hashing |
|--------|----------------|--------------------------------|
| **Lookup Time** | O(1) | O(log N) |
| **Memory Usage** | O(M) where M is table size | O(N×V) where V is virtual nodes |
| **Reconstruction Time** | O(M×N) | O(V×log(V×N)) |
| **Load Distribution** | Excellent with prime table size | Good with sufficient virtual nodes |
| **Minimal Disruption** | ~1/N keys move | ~1/N keys move |
| **Implementation Complexity** | Medium | Low |

### Chapter 11: Rendezvous Hashing (Highest Random Weight) (10 minutes)

Rendezvous hashing assigns each key to the node with the highest "weight" for that key, providing excellent load distribution.

#### Rendezvous Hashing Implementation

```python
import struct

class RendezvousHash:
    """Rendezvous (Highest Random Weight) Hashing"""
    
    def __init__(self, nodes: List[str] = None, weights: Dict[str, float] = None):
        self.nodes = set(nodes or [])
        self.weights = weights or {}
        
        # Default weight is 1.0
        for node in self.nodes:
            if node not in self.weights:
                self.weights[node] = 1.0
    
    def _hash_key_node(self, key: str, node: str) -> float:
        """Calculate hash value for key-node pair"""
        combined = f"{key}:{node}"
        hash_bytes = hashlib.sha1(combined.encode()).digest()
        
        # Convert first 8 bytes to float
        hash_int = struct.unpack('>Q', hash_bytes[:8])[0]
        return hash_int / (2**64 - 1)  # Normalize to [0, 1]
    
    def get_node(self, key: str) -> Optional[str]:
        """Get node with highest weighted hash for key"""
        if not self.nodes:
            return None
        
        best_node = None
        best_weight = -1
        
        for node in self.nodes:
            # Calculate weighted hash
            hash_value = self._hash_key_node(key, node)
            weighted_hash = hash_value * self.weights[node]
            
            if weighted_hash > best_weight:
                best_weight = weighted_hash
                best_node = node
        
        return best_node
    
    def get_nodes_ordered(self, key: str, count: int = None) -> List[str]:
        """Get nodes ordered by weighted hash (for replication)"""
        if count is None:
            count = len(self.nodes)
        
        # Calculate weighted hash for all nodes
        node_weights = []
        for node in self.nodes:
            hash_value = self._hash_key_node(key, node)
            weighted_hash = hash_value * self.weights[node]
            node_weights.append((weighted_hash, node))
        
        # Sort by weighted hash (descending)
        node_weights.sort(reverse=True)
        
        return [node for _, node in node_weights[:count]]
    
    def add_node(self, node: str, weight: float = 1.0) -> Dict[str, any]:
        """Add node and calculate impact"""
        if node in self.nodes:
            raise ValueError(f"Node {node} already exists")
        
        # Test key redistribution impact
        test_keys = [f"key_{i}" for i in range(10000)]
        old_assignments = {}
        
        for key in test_keys:
            old_assignments[key] = self.get_node(key)
        
        # Add new node
        self.nodes.add(node)
        self.weights[node] = weight
        
        # Check new assignments
        reassigned = 0
        for key in test_keys:
            new_assignment = self.get_node(key)
            if old_assignments[key] != new_assignment:
                reassigned += 1
        
        redistribution_percentage = (reassigned / len(test_keys)) * 100
        
        return {
            'node_added': node,
            'weight': weight,
            'total_nodes': len(self.nodes),
            'redistribution_percentage': redistribution_percentage,
            'keys_reassigned': reassigned
        }
    
    def remove_node(self, node: str) -> Dict[str, any]:
        """Remove node and calculate impact"""
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found")
        
        # Test impact
        test_keys = [f"key_{i}" for i in range(10000)]
        old_assignments = {}
        
        for key in test_keys:
            old_assignments[key] = self.get_node(key)
        
        # Remove node
        self.nodes.remove(node)
        del self.weights[node]
        
        # Check reassignments (excluding keys that were on removed node)
        reassigned = 0
        removed_node_keys = 0
        
        for key in test_keys:
            old_assignment = old_assignments[key]
            if old_assignment == node:
                removed_node_keys += 1
            else:
                new_assignment = self.get_node(key)
                if old_assignment != new_assignment:
                    reassigned += 1
        
        return {
            'node_removed': node,
            'remaining_nodes': len(self.nodes),
            'keys_from_removed_node': removed_node_keys,
            'additional_reassignments': reassigned,
            'total_impact_percentage': ((removed_node_keys + reassigned) / len(test_keys)) * 100
        }
    
    def analyze_distribution(self, num_keys: int = 100000) -> Dict[str, any]:
        """Analyze load distribution quality"""
        if not self.nodes:
            return {}
        
        # Generate test keys and count assignments
        assignments = defaultdict(int)
        test_keys = [f"test_key_{i}" for i in range(num_keys)]
        
        for key in test_keys:
            node = self.get_node(key)
            if node:
                assignments[node] += 1
        
        # Calculate distribution metrics
        total_weight = sum(self.weights.values())
        distribution_quality = {}
        
        for node in self.nodes:
            expected_proportion = self.weights[node] / total_weight
            actual_proportion = assignments[node] / num_keys
            
            distribution_quality[node] = {
                'expected_keys': int(expected_proportion * num_keys),
                'actual_keys': assignments[node],
                'ratio': actual_proportion / expected_proportion if expected_proportion > 0 else 0
            }
        
        # Overall quality metrics
        ratios = [dq['ratio'] for dq in distribution_quality.values()]
        
        return {
            'per_node_distribution': distribution_quality,
            'average_ratio': sum(ratios) / len(ratios) if ratios else 0,
            'ratio_variance': sum((r - 1.0) ** 2 for r in ratios) / len(ratios) if ratios else 0,
            'min_ratio': min(ratios) if ratios else 0,
            'max_ratio': max(ratios) if ratios else 0
        }
```

#### Rendezvous Hash Benefits and Trade-offs

**Benefits**:
- **Perfect Load Distribution**: Respects node weights exactly in expectation
- **Minimal Disruption**: Only keys assigned to removed node are reassigned
- **Deterministic**: Same result regardless of order of operations
- **Simple Implementation**: No complex data structures required

**Trade-offs**:
- **O(N) Lookup Time**: Must compute hash for all nodes
- **CPU Intensive**: More hash computations per lookup
- **Not Suitable for Large N**: Performance degrades with many nodes

### Chapter 12: Power of Two Choices Load Balancing (10 minutes)

The Power of Two Choices algorithm randomly samples two servers and chooses the one with fewer connections, achieving exponential improvement in load distribution.

#### Mathematical Foundation

**Theorem**: With n servers and random job assignment, the maximum load is O(log n / log log n). With power of two choices, the maximum load is O(log log n).

This represents an exponential improvement in load balancing with minimal overhead.

#### Implementation

```python
import random
import heapq
from typing import Tuple

class PowerOfTwoChoicesLB:
    """Power of Two Choices Load Balancer"""
    
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.loads: Dict[str, int] = {server: 0 for server in servers}
        self.connections: Dict[str, Set[str]] = {server: set() for server in servers}
        
        # Optimization: maintain min-heap of server loads
        self.load_heap: List[Tuple[int, str]] = [(0, server) for server in servers]
        heapq.heapify(self.load_heap)
        
        # Statistics tracking
        self.total_requests = 0
        self.choice_statistics = {
            'first_choice_wins': 0,
            'second_choice_wins': 0,
            'ties': 0
        }
    
    def assign_request(self, request_id: str) -> str:
        """Assign request using power of two choices"""
        self.total_requests += 1
        
        # Randomly sample two servers
        server1, server2 = random.sample(self.servers, 2)
        
        load1 = self.loads[server1]
        load2 = self.loads[server2]
        
        # Choose server with lower load
        if load1 < load2:
            chosen_server = server1
            self.choice_statistics['first_choice_wins'] += 1
        elif load2 < load1:
            chosen_server = server2
            self.choice_statistics['second_choice_wins'] += 1
        else:
            # Tie - choose randomly
            chosen_server = random.choice([server1, server2])
            self.choice_statistics['ties'] += 1
        
        # Update load and connections
        self.loads[chosen_server] += 1
        self.connections[chosen_server].add(request_id)
        
        return chosen_server
    
    def complete_request(self, request_id: str, server: str):
        """Mark request as completed"""
        if server in self.connections and request_id in self.connections[server]:
            self.loads[server] -= 1
            self.connections[server].remove(request_id)
    
    def assign_request_optimized(self, request_id: str) -> str:
        """Optimized assignment using heap for better performance"""
        if len(self.load_heap) < 2:
            # Fallback if heap is corrupted
            return self.assign_request(request_id)
        
        # Get two servers with lowest loads
        load1, server1 = heapq.heappop(self.load_heap)
        load2, server2 = heapq.heappop(self.load_heap)
        
        # Verify loads are current (heap may be stale)
        actual_load1 = self.loads[server1]
        actual_load2 = self.loads[server2]
        
        if actual_load1 != load1 or actual_load2 != load2:
            # Heap is stale, rebuild and use standard algorithm
            self._rebuild_heap()
            return self.assign_request(request_id)
        
        # Choose server with lower load
        if actual_load1 <= actual_load2:
            chosen_server = server1
            new_load = actual_load1 + 1
            # Put the other server back
            heapq.heappush(self.load_heap, (actual_load2, server2))
        else:
            chosen_server = server2
            new_load = actual_load2 + 1
            # Put the other server back  
            heapq.heappush(self.load_heap, (actual_load1, server1))
        
        # Update chosen server's load and put back in heap
        self.loads[chosen_server] += 1
        self.connections[chosen_server].add(request_id)
        heapq.heappush(self.load_heap, (new_load, chosen_server))
        
        return chosen_server
    
    def _rebuild_heap(self):
        """Rebuild heap when it becomes stale"""
        self.load_heap = [(load, server) for server, load in self.loads.items()]
        heapq.heapify(self.load_heap)
    
    def get_load_statistics(self) -> Dict[str, any]:
        """Get comprehensive load balancing statistics"""
        loads = list(self.loads.values())
        total_load = sum(loads)
        avg_load = total_load / len(loads) if loads else 0
        
        # Load distribution metrics
        max_load = max(loads) if loads else 0
        min_load = min(loads) if loads else 0
        load_variance = sum((load - avg_load) ** 2 for load in loads) / len(loads) if loads else 0
        
        # Theoretical comparison
        n = len(self.servers)
        theoretical_random_max = total_load / n + 3 * (total_load * math.log(n) / n) ** 0.5
        theoretical_p2c_max = total_load / n + 3 * (total_load * math.log(math.log(n)) / n) ** 0.5
        
        return {
            'total_requests_processed': self.total_requests,
            'current_total_load': total_load,
            'average_load': avg_load,
            'max_load': max_load,
            'min_load': min_load,
            'load_imbalance': max_load - min_load,
            'load_variance': load_variance,
            'coefficient_of_variation': (load_variance ** 0.5) / avg_load if avg_load > 0 else 0,
            
            # Theoretical bounds
            'theoretical_random_max_load': theoretical_random_max,
            'theoretical_p2c_max_load': theoretical_p2c_max,
            'improvement_factor': theoretical_random_max / theoretical_p2c_max if theoretical_p2c_max > 0 else 0,
            
            # Choice statistics
            'first_choice_win_rate': self.choice_statistics['first_choice_wins'] / max(1, self.total_requests),
            'second_choice_win_rate': self.choice_statistics['second_choice_wins'] / max(1, self.total_requests),
            'tie_rate': self.choice_statistics['ties'] / max(1, self.total_requests),
            
            # Per-server breakdown
            'per_server_loads': dict(self.loads),
            'per_server_connections': {s: len(conns) for s, conns in self.connections.items()}
        }
    
    def simulate_load_distribution(self, num_requests: int = 100000) -> Dict[str, any]:
        """Simulate load distribution over many requests"""
        # Save current state
        original_loads = self.loads.copy()
        original_connections = {s: conns.copy() for s, conns in self.connections.items()}
        original_total = self.total_requests
        
        # Run simulation
        for i in range(num_requests):
            request_id = f"sim_req_{i}"
            server = self.assign_request(request_id)
            
            # Simulate request completion (exponential service time)
            if random.random() < 0.1:  # 10% completion rate per round
                if self.connections[server]:
                    completed_req = random.choice(list(self.connections[server]))
                    self.complete_request(completed_req, server)
        
        # Get final statistics
        final_stats = self.get_load_statistics()
        
        # Restore original state
        self.loads = original_loads
        self.connections = original_connections
        self.total_requests = original_total
        self._rebuild_heap()
        
        return final_stats

# Comparison with other algorithms
class LoadBalancingComparison:
    """Compare different load balancing algorithms"""
    
    def __init__(self, servers: List[str], num_requests: int = 100000):
        self.servers = servers
        self.num_requests = num_requests
    
    def compare_algorithms(self) -> Dict[str, Dict[str, any]]:
        """Compare multiple load balancing algorithms"""
        results = {}
        
        # 1. Random assignment
        results['random'] = self._simulate_random()
        
        # 2. Round robin
        results['round_robin'] = self._simulate_round_robin()
        
        # 3. Power of two choices
        results['power_of_two'] = self._simulate_power_of_two()
        
        # 4. Least connections (optimal)
        results['least_connections'] = self._simulate_least_connections()
        
        return results
    
    def _simulate_random(self) -> Dict[str, any]:
        """Simulate pure random assignment"""
        loads = {server: 0 for server in self.servers}
        
        for _ in range(self.num_requests):
            server = random.choice(self.servers)
            loads[server] += 1
        
        return self._calculate_metrics(loads)
    
    def _simulate_round_robin(self) -> Dict[str, any]:
        """Simulate round robin assignment"""
        loads = {server: 0 for server in self.servers}
        
        for i in range(self.num_requests):
            server = self.servers[i % len(self.servers)]
            loads[server] += 1
        
        return self._calculate_metrics(loads)
    
    def _simulate_power_of_two(self) -> Dict[str, any]:
        """Simulate power of two choices"""
        lb = PowerOfTwoChoicesLB(self.servers.copy())
        stats = lb.simulate_load_distribution(self.num_requests)
        
        return {
            'max_load': stats['max_load'],
            'load_variance': stats['load_variance'],
            'coefficient_of_variation': stats['coefficient_of_variation'],
            'algorithm_specific': stats
        }
    
    def _simulate_least_connections(self) -> Dict[str, any]:
        """Simulate optimal least connections"""
        loads = {server: 0 for server in self.servers}
        
        for _ in range(self.num_requests):
            # Always choose server with minimum load
            min_server = min(loads.keys(), key=lambda s: loads[s])
            loads[min_server] += 1
        
        return self._calculate_metrics(loads)
    
    def _calculate_metrics(self, loads: Dict[str, int]) -> Dict[str, any]:
        """Calculate standard metrics for load distribution"""
        load_values = list(loads.values())
        total_load = sum(load_values)
        avg_load = total_load / len(load_values) if load_values else 0
        
        max_load = max(load_values) if load_values else 0
        min_load = min(load_values) if load_values else 0
        variance = sum((load - avg_load) ** 2 for load in load_values) / len(load_values) if load_values else 0
        
        return {
            'max_load': max_load,
            'min_load': min_load,
            'load_variance': variance,
            'coefficient_of_variation': (variance ** 0.5) / avg_load if avg_load > 0 else 0,
            'load_imbalance': max_load - min_load,
            'loads': loads
        }
```

## Part 5: Production Best Practices (15 minutes)

### Chapter 13: Testing and Validation Strategies (7.5 minutes)

#### Comprehensive Test Suite

```python
import pytest
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ConsistentHashingTestSuite:
    """Comprehensive test suite for consistent hashing implementations"""
    
    def __init__(self, hash_ring_class):
        self.hash_ring_class = hash_ring_class
    
    def test_load_distribution_uniformity(self):
        """Test that load distribution is uniform with sufficient virtual nodes"""
        ring = self.hash_ring_class()
        
        # Add nodes with different weights
        nodes = [
            Node(node_id=f"node-{i}", address=f"host{i}:9000", weight=1.0)
            for i in range(10)
        ]
        for node in nodes:
            ring.add_node(node)
        
        # Test with many keys
        num_keys = 100000
        key_assignments = {}
        
        for i in range(num_keys):
            key = f"test_key_{i}"
            assigned_node = ring.get_node(key)
            if assigned_node:
                key_assignments[key] = assigned_node.node_id
        
        # Count assignments per node
        assignment_counts = defaultdict(int)
        for node_id in key_assignments.values():
            assignment_counts[node_id] += 1
        
        # Check distribution quality
        expected_per_node = num_keys / len(nodes)
        max_deviation = 0
        
        for node_id, count in assignment_counts.items():
            deviation = abs(count - expected_per_node) / expected_per_node
            max_deviation = max(max_deviation, deviation)
        
        # Assert reasonable distribution (within 15% of expected)
        assert max_deviation < 0.15, f"Load distribution too uneven: max deviation {max_deviation:.1%}"
        
        # Verify all keys are assigned
        assert len(key_assignments) == num_keys, "Not all keys were assigned"
    
    def test_minimal_key_movement_on_scaling(self):
        """Test that scaling operations move minimal number of keys"""
        ring = self.hash_ring_class()
        
        # Start with initial nodes
        initial_nodes = [
            Node(node_id=f"initial-{i}", address=f"host{i}:9000")
            for i in range(5)
        ]
        for node in initial_nodes:
            ring.add_node(node)
        
        # Generate test keys and record assignments
        test_keys = [f"scale_test_key_{i}" for i in range(50000)]
        initial_assignments = {}
        
        for key in test_keys:
            node = ring.get_node(key)
            if node:
                initial_assignments[key] = node.node_id
        
        # Add a new node
        new_node = Node(node_id="new-node", address="new-host:9000")
        ring.add_node(new_node)
        
        # Check new assignments
        moved_keys = 0
        for key in test_keys:
            new_node_assigned = ring.get_node(key)
            if new_node_assigned and initial_assignments[key] != new_node_assigned.node_id:
                moved_keys += 1
        
        # Theoretical minimum: approximately 1/(N+1) keys should move
        expected_movement = len(test_keys) / (len(initial_nodes) + 1)
        actual_movement_ratio = moved_keys / len(test_keys)
        expected_movement_ratio = 1.0 / (len(initial_nodes) + 1)
        
        # Allow up to 2x the theoretical minimum (due to random placement)
        assert actual_movement_ratio <= expected_movement_ratio * 2, \
            f"Too many keys moved: {actual_movement_ratio:.1%} vs expected ~{expected_movement_ratio:.1%}"
    
    def test_replication_consistency(self):
        """Test that replication provides consistent node ordering"""
        ring = self.hash_ring_class(replication_factor=3)
        
        # Add nodes
        nodes = [Node(node_id=f"replica-{i}", address=f"host{i}:9000") for i in range(8)]
        for node in nodes:
            ring.add_node(node)
        
        test_keys = [f"replication_key_{i}" for i in range(1000)]
        
        for key in test_keys:
            replicas = ring.get_nodes_for_replication(key, count=3)
            
            # Should get exactly 3 unique replicas
            assert len(replicas) == 3, f"Expected 3 replicas for key {key}, got {len(replicas)}"
            assert len(set(r.node_id for r in replicas)) == 3, f"Replicas not unique for key {key}"
            
            # Primary replica should be consistent with single lookup
            primary = ring.get_node(key)
            assert replicas[0].node_id == primary.node_id, \
                f"Primary replica mismatch for key {key}: {replicas[0].node_id} != {primary.node_id}"
            
            # Replica order should be deterministic
            replicas2 = ring.get_nodes_for_replication(key, count=3)
            assert [r.node_id for r in replicas] == [r.node_id for r in replicas2], \
                f"Replica order not deterministic for key {key}"
    
    def test_concurrent_operations(self):
        """Test thread safety under concurrent operations"""
        ring = self.hash_ring_class()
        
        # Add initial nodes
        for i in range(5):
            node = Node(node_id=f"concurrent-{i}", address=f"host{i}:9000")
            ring.add_node(node)
        
        # Concurrent operations
        def lookup_worker(worker_id):
            results = []
            for i in range(1000):
                key = f"worker_{worker_id}_key_{i}"
                node = ring.get_node(key)
                if node:
                    results.append((key, node.node_id))
            return results
        
        def scaling_worker():
            time.sleep(0.1)  # Let lookups start
            # Add and remove nodes
            for i in range(3):
                new_node = Node(node_id=f"scale-{i}", address=f"scale-host{i}:9000")
                ring.add_node(new_node)
                time.sleep(0.05)
                ring.remove_node(f"scale-{i}")
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Start lookup workers
            lookup_futures = [executor.submit(lookup_worker, i) for i in range(5)]
            
            # Start scaling worker
            scale_future = executor.submit(scaling_worker)
            
            # Wait for completion
            lookup_results = []
            for future in as_completed(lookup_futures):
                try:
                    results = future.result(timeout=10)
                    lookup_results.extend(results)
                except Exception as e:
                    pytest.fail(f"Lookup worker failed: {e}")
            
            try:
                scale_future.result(timeout=10)
            except Exception as e:
                pytest.fail(f"Scaling worker failed: {e}")
        
        # Verify we got consistent results
        assert len(lookup_results) > 4000, "Not enough lookup results from concurrent test"
        
        # Verify consistency: same key should map to same node
        key_mappings = {}
        for key, node_id in lookup_results:
            if key in key_mappings:
                # Same key looked up multiple times - should be consistent
                assert key_mappings[key] == node_id, \
                    f"Inconsistent mapping for key {key}: {key_mappings[key]} != {node_id}"
            else:
                key_mappings[key] = node_id
    
    def test_performance_benchmarks(self):
        """Test performance meets requirements"""
        ring = self.hash_ring_class()
        
        # Setup large ring
        for i in range(100):
            node = Node(node_id=f"perf-{i}", address=f"host{i}:9000")
            ring.add_node(node)
        
        # Benchmark lookups
        test_keys = [f"perf_key_{i}" for i in range(100000)]
        
        start_time = time.time()
        for key in test_keys:
            ring.get_node(key)
        lookup_time = time.time() - start_time
        
        lookups_per_second = len(test_keys) / lookup_time
        
        # Should achieve at least 100K lookups/second
        assert lookups_per_second > 100000, \
            f"Lookup performance too slow: {lookups_per_second:.0f} ops/sec"
        
        # Benchmark node addition
        new_node = Node(node_id="perf-new", address="new-host:9000")
        start_time = time.time()
        ring.add_node(new_node)
        add_time = time.time() - start_time
        
        # Node addition should complete in reasonable time
        assert add_time < 0.1, f"Node addition too slow: {add_time:.3f}s"
    
    def test_failure_resilience(self):
        """Test behavior under node failures"""
        ring = self.hash_ring_class(replication_factor=3)
        
        # Add nodes
        nodes = [Node(node_id=f"failure-{i}", address=f"host{i}:9000") for i in range(10)]
        for node in nodes:
            ring.add_node(node)
        
        # Record initial replica assignments
        test_keys = [f"failure_key_{i}" for i in range(1000)]
        initial_replicas = {}
        
        for key in test_keys:
            replicas = ring.get_nodes_for_replication(key, count=3)
            initial_replicas[key] = [r.node_id for r in replicas]
        
        # Simulate node failures
        failed_nodes = ["failure-3", "failure-7"]
        for node_id in failed_nodes:
            ring.physical_nodes[node_id].status = "failed"
        
        # Check that data is still accessible
        accessible_keys = 0
        for key in test_keys:
            # Get current healthy replicas
            current_replicas = ring.get_nodes_for_replication(key, count=3)
            healthy_replicas = [r for r in current_replicas if r.status == "active"]
            
            if len(healthy_replicas) >= 2:  # Quorum available
                accessible_keys += 1
        
        availability = accessible_keys / len(test_keys)
        assert availability > 0.95, f"Availability too low after failures: {availability:.1%}"
    
    def run_comprehensive_test_suite(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        test_results = {}
        
        tests = [
            ('load_distribution', self.test_load_distribution_uniformity),
            ('minimal_movement', self.test_minimal_key_movement_on_scaling),
            ('replication', self.test_replication_consistency),
            ('concurrency', self.test_concurrent_operations),
            ('performance', self.test_performance_benchmarks),
            ('failure_resilience', self.test_failure_resilience)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
                test_results[test_name] = True
                print(f"✓ {test_name} test passed")
            except Exception as e:
                test_results[test_name] = False
                print(f"✗ {test_name} test failed: {e}")
        
        return test_results
```

### Chapter 14: Operational Monitoring and Troubleshooting (7.5 minutes)

#### Comprehensive Monitoring Dashboard

```python
from dataclasses import asdict
import json
import logging
from enum import Enum
from typing import Any, Dict, List

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    severity: AlertSeverity
    title: str
    description: str
    timestamp: float
    node_id: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None

class ConsistentHashingOperationalMonitor:
    """Production monitoring and alerting for consistent hashing systems"""
    
    def __init__(self, ring: ConsistentHashRing):
        self.ring = ring
        self.alerts: List[Alert] = []
        self.metrics_history: List[Dict[str, Any]] = []
        self.thresholds = {
            'load_variance_warning': 0.3,
            'load_variance_critical': 0.5,
            'hot_spot_ratio_warning': 1.5,
            'hot_spot_ratio_critical': 2.0,
            'cache_hit_rate_warning': 0.8,
            'rebalance_time_warning_ms': 5000,
            'lookup_latency_p99_warning_ms': 10
        }
        
        # Health check configurations
        self.health_check_interval = 60  # seconds
        self.last_health_check = time.time()
        
    def collect_comprehensive_metrics(self) -> Dict[str, Any]:
        """Collect all monitoring metrics"""
        ring_stats = self.ring.get_ring_statistics()
        
        metrics = {
            'timestamp': time.time(),
            'ring_version': ring_stats.get('ring_version', 0),
            
            # Cluster health
            'cluster': {
                'total_nodes': ring_stats.get('total_physical_nodes', 0),
                'active_nodes': ring_stats.get('active_nodes', 0),
                'total_virtual_nodes': ring_stats.get('total_virtual_nodes', 0),
                'replication_factor': ring_stats.get('replication_factor', 0)
            },
            
            # Load distribution
            'load_distribution': {
                'variance': ring_stats.get('load_variance', 0),
                'coefficient_of_variation': ring_stats.get('load_coefficient_of_variation', 0),
                'distribution_map': ring_stats.get('load_distribution', {})
            },
            
            # Performance
            'performance': {
                'total_lookups': ring_stats.get('total_lookups', 0),
                'cache_hit_rate': ring_stats.get('cache_hit_rate', 0),
                'average_rebalance_time_ms': ring_stats.get('average_rebalance_time_ms', 0),
                'total_key_movements': ring_stats.get('total_key_movements', 0)
            },
            
            # Health scores
            'health': {
                'average_health_score': ring_stats.get('average_health_score', 0),
                'min_health_score': ring_stats.get('min_health_score', 0),
                'unhealthy_nodes': self._count_unhealthy_nodes()
            }
        }
        
        # Store metrics history
        self.metrics_history.append(metrics)
        
        # Keep only last 24 hours of metrics (assuming 1-minute intervals)
        if len(self.metrics_history) > 1440:
            self.metrics_history.pop(0)
        
        return metrics
    
    def analyze_and_alert(self) -> List[Alert]:
        """Analyze metrics and generate alerts"""
        current_alerts = []
        metrics = self.collect_comprehensive_metrics()
        
        # Load variance alerts
        load_variance = metrics['load_distribution']['variance']
        if load_variance > self.thresholds['load_variance_critical']:
            current_alerts.append(Alert(
                severity=AlertSeverity.CRITICAL,
                title="Critical Load Imbalance",
                description=f"Load variance {load_variance:.3f} exceeds critical threshold",
                timestamp=time.time(),
                metric_value=load_variance,
                threshold=self.thresholds['load_variance_critical']
            ))
        elif load_variance > self.thresholds['load_variance_warning']:
            current_alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                title="Load Imbalance Warning",
                description=f"Load variance {load_variance:.3f} exceeds warning threshold",
                timestamp=time.time(),
                metric_value=load_variance,
                threshold=self.thresholds['load_variance_warning']
            ))
        
        # Hot spot detection
        load_distribution = metrics['load_distribution']['distribution_map']
        for node_id, load_ratio in load_distribution.items():
            if load_ratio > self.thresholds['hot_spot_ratio_critical']:
                current_alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL,
                    title=f"Critical Hot Spot on {node_id}",
                    description=f"Node {node_id} has {load_ratio:.1f}x average load",
                    timestamp=time.time(),
                    node_id=node_id,
                    metric_value=load_ratio,
                    threshold=self.thresholds['hot_spot_ratio_critical']
                ))
            elif load_ratio > self.thresholds['hot_spot_ratio_warning']:
                current_alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Hot Spot Warning on {node_id}",
                    description=f"Node {node_id} has {load_ratio:.1f}x average load",
                    timestamp=time.time(),
                    node_id=node_id,
                    metric_value=load_ratio,
                    threshold=self.thresholds['hot_spot_ratio_warning']
                ))
        
        # Cache performance alerts
        cache_hit_rate = metrics['performance']['cache_hit_rate']
        if cache_hit_rate < self.thresholds['cache_hit_rate_warning']:
            current_alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                title="Low Cache Hit Rate",
                description=f"Cache hit rate {cache_hit_rate:.1%} below threshold",
                timestamp=time.time(),
                metric_value=cache_hit_rate,
                threshold=self.thresholds['cache_hit_rate_warning']
            ))
        
        # Rebalancing performance alerts
        rebalance_time = metrics['performance']['average_rebalance_time_ms']
        if rebalance_time > self.thresholds['rebalance_time_warning_ms']:
            current_alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                title="Slow Rebalancing",
                description=f"Rebalancing takes {rebalance_time:.0f}ms on average",
                timestamp=time.time(),
                metric_value=rebalance_time,
                threshold=self.thresholds['rebalance_time_warning_ms']
            ))
        
        # Node health alerts
        unhealthy_nodes = metrics['health']['unhealthy_nodes']
        if unhealthy_nodes > 0:
            current_alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                title="Unhealthy Nodes Detected",
                description=f"{unhealthy_nodes} nodes have poor health scores",
                timestamp=time.time(),
                metric_value=unhealthy_nodes,
                threshold=0
            ))
        
        # Store alerts
        self.alerts.extend(current_alerts)
        
        return current_alerts
    
    def _count_unhealthy_nodes(self) -> int:
        """Count nodes with poor health scores"""
        unhealthy_count = 0
        for node in self.ring.physical_nodes.values():
            if node.health_score() < 0.5:
                unhealthy_count += 1
        return unhealthy_count
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        metrics = self.collect_comprehensive_metrics()
        recent_alerts = [alert for alert in self.alerts 
                        if time.time() - alert.timestamp < 3600]  # Last hour
        
        # Calculate trends
        trends = self._calculate_trends()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, recent_alerts)
        
        return {
            'timestamp': time.time(),
            'overall_health_score': self._calculate_overall_health_score(metrics),
            'current_metrics': metrics,
            'recent_alerts': [asdict(alert) for alert in recent_alerts],
            'trends': trends,
            'recommendations': recommendations,
            'cluster_summary': {
                'status': self._determine_cluster_status(metrics, recent_alerts),
                'active_nodes': metrics['cluster']['active_nodes'],
                'total_capacity': metrics['cluster']['total_nodes'],
                'load_balance_quality': self._assess_load_balance_quality(metrics),
                'performance_grade': self._assess_performance_grade(metrics)
            }
        }
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate metric trends over time"""
        if len(self.metrics_history) < 10:
            return {'insufficient_data': 'Need more historical data for trend analysis'}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 data points
        trends = {}
        
        # Load variance trend
        load_variances = [m['load_distribution']['variance'] for m in recent_metrics]
        if load_variances[-1] > load_variances[0] * 1.1:
            trends['load_variance'] = 'increasing'
        elif load_variances[-1] < load_variances[0] * 0.9:
            trends['load_variance'] = 'decreasing'
        else:
            trends['load_variance'] = 'stable'
        
        # Cache hit rate trend
        hit_rates = [m['performance']['cache_hit_rate'] for m in recent_metrics]
        if hit_rates[-1] > hit_rates[0] + 0.05:
            trends['cache_hit_rate'] = 'improving'
        elif hit_rates[-1] < hit_rates[0] - 0.05:
            trends['cache_hit_rate'] = 'degrading'
        else:
            trends['cache_hit_rate'] = 'stable'
        
        return trends
    
    def _generate_recommendations(self, metrics: Dict[str, Any], alerts: List[Alert]) -> List[str]:
        """Generate operational recommendations"""
        recommendations = []
        
        # Load balancing recommendations
        load_variance = metrics['load_distribution']['variance']
        if load_variance > 0.3:
            recommendations.append(
                "Consider increasing virtual node count to improve load distribution"
            )
        
        # Hot spot recommendations
        load_distribution = metrics['load_distribution']['distribution_map']
        hot_nodes = [node_id for node_id, ratio in load_distribution.items() if ratio > 1.5]
        if hot_nodes:
            recommendations.append(
                f"Investigate hot spots on nodes: {', '.join(hot_nodes)}. "
                "Consider key distribution analysis or adding capacity."
            )
        
        # Performance recommendations
        cache_hit_rate = metrics['performance']['cache_hit_rate']
        if cache_hit_rate < 0.8:
            recommendations.append(
                "Cache hit rate is low. Consider increasing cache size or reviewing access patterns."
            )
        
        # Capacity recommendations
        active_nodes = metrics['cluster']['active_nodes']
        total_nodes = metrics['cluster']['total_nodes']
        if active_nodes < total_nodes * 0.8:
            recommendations.append(
                "Some nodes are inactive. Investigate node health and consider maintenance."
            )
        
        return recommendations
    
    def _calculate_overall_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall cluster health score (0.0 to 1.0)"""
        scores = []
        
        # Load distribution score
        load_variance = metrics['load_distribution']['variance']
        load_score = max(0, 1.0 - load_variance * 2)  # Penalty for variance
        scores.append(load_score)
        
        # Performance score
        cache_hit_rate = metrics['performance']['cache_hit_rate']
        scores.append(cache_hit_rate)
        
        # Availability score
        active_ratio = metrics['cluster']['active_nodes'] / max(1, metrics['cluster']['total_nodes'])
        scores.append(active_ratio)
        
        # Health score
        avg_health = metrics['health']['average_health_score']
        scores.append(avg_health)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _determine_cluster_status(self, metrics: Dict[str, Any], alerts: List[Alert]) -> str:
        """Determine overall cluster status"""
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        warning_alerts = [a for a in alerts if a.severity == AlertSeverity.WARNING]
        
        health_score = self._calculate_overall_health_score(metrics)
        
        if critical_alerts or health_score < 0.5:
            return "CRITICAL"
        elif warning_alerts or health_score < 0.8:
            return "WARNING"
        else:
            return "HEALTHY"
    
    def _assess_load_balance_quality(self, metrics: Dict[str, Any]) -> str:
        """Assess load balancing quality"""
        cv = metrics['load_distribution']['coefficient_of_variation']
        
        if cv < 0.1:
            return "EXCELLENT"
        elif cv < 0.2:
            return "GOOD"
        elif cv < 0.4:
            return "FAIR"
        else:
            return "POOR"
    
    def _assess_performance_grade(self, metrics: Dict[str, Any]) -> str:
        """Assess performance grade"""
        cache_hit_rate = metrics['performance']['cache_hit_rate']
        rebalance_time = metrics['performance']['average_rebalance_time_ms']
        
        performance_score = cache_hit_rate * 0.6 + (1 - min(rebalance_time / 10000, 1)) * 0.4
        
        if performance_score > 0.9:
            return "A"
        elif performance_score > 0.8:
            return "B"
        elif performance_score > 0.7:
            return "C"
        elif performance_score > 0.6:
            return "D"
        else:
            return "F"
    
    def export_metrics_for_grafana(self) -> str:
        """Export metrics in Prometheus format for Grafana"""
        metrics = self.collect_comprehensive_metrics()
        
        prometheus_metrics = []
        
        # Ring metrics
        prometheus_metrics.append(f'consistent_hash_ring_version {metrics["ring_version"]}')
        prometheus_metrics.append(f'consistent_hash_total_nodes {metrics["cluster"]["total_nodes"]}')
        prometheus_metrics.append(f'consistent_hash_active_nodes {metrics["cluster"]["active_nodes"]}')
        prometheus_metrics.append(f'consistent_hash_virtual_nodes {metrics["cluster"]["total_virtual_nodes"]}')
        
        # Load distribution metrics
        prometheus_metrics.append(f'consistent_hash_load_variance {metrics["load_distribution"]["variance"]}')
        prometheus_metrics.append(f'consistent_hash_load_cv {metrics["load_distribution"]["coefficient_of_variation"]}')
        
        # Performance metrics
        prometheus_metrics.append(f'consistent_hash_total_lookups {metrics["performance"]["total_lookups"]}')
        prometheus_metrics.append(f'consistent_hash_cache_hit_rate {metrics["performance"]["cache_hit_rate"]}')
        prometheus_metrics.append(f'consistent_hash_rebalance_time_ms {metrics["performance"]["average_rebalance_time_ms"]}')
        
        # Health metrics
        prometheus_metrics.append(f'consistent_hash_health_score {metrics["health"]["average_health_score"]}')
        prometheus_metrics.append(f'consistent_hash_unhealthy_nodes {metrics["health"]["unhealthy_nodes"]}')
        
        # Per-node load metrics
        for node_id, load_ratio in metrics["load_distribution"]["distribution_map"].items():
            prometheus_metrics.append(f'consistent_hash_node_load_ratio{{node="{node_id}"}} {load_ratio}')
        
        return '\n'.join(prometheus_metrics)
```

## Conclusion and Summary (15 minutes)

### Key Takeaways

Consistent hashing represents one of the most important algorithmic innovations in distributed systems, solving the fundamental problem of data distribution across dynamic node sets. Through our comprehensive exploration, we've covered:

**Mathematical Foundations**:
- The O(K/N) key movement guarantee vs O(K) for traditional hashing
- Virtual nodes reducing load variance from O(log N) to O(1/V)  
- Theoretical bounds and proofs for various consistent hashing variants

**Production Implementation**:
- Complete production-grade consistent hashing system with monitoring
- Advanced optimizations including bounded-load and jump hashing
- Performance engineering achieving >1M lookups/second

**Real-World Applications**:
- Amazon DynamoDB's global-scale partitioning strategy
- Apache Cassandra's token ring with vnodes
- Discord's message routing across 4,096 shards

**Operational Excellence**:
- Comprehensive testing strategies and validation frameworks
- Production monitoring with alerting and trend analysis
- Best practices for deployment and maintenance

### When to Choose Each Algorithm

| Algorithm | Best Use Case | Key Advantage | Trade-off |
|-----------|---------------|---------------|-----------|
| **Traditional Consistent Hashing** | General distributed storage | Simple, proven | O(log N) lookup |
| **Jump Consistent Hash** | Fixed backend sets | Zero memory overhead | Adding nodes only |
| **Maglev Hashing** | Load balancers, high throughput | O(1) lookup time | Higher memory usage |
| **Rendezvous Hashing** | Small node counts, exact weights | Perfect load distribution | O(N) lookup time |
| **Bounded-Load** | Strict load requirements | Load guarantees | More complex |

### Production Checklist

Before deploying consistent hashing in production:

**✅ Design Phase**:
- [ ] Analyzed key distribution patterns and hot spot potential
- [ ] Selected appropriate virtual node count (100-200 for most cases)
- [ ] Designed replication strategy with failure tolerance
- [ ] Planned for monitoring and operational procedures

**✅ Implementation Phase**:
- [ ] Implemented comprehensive test suite covering all scenarios
- [ ] Built performance benchmarking and validation tools
- [ ] Created monitoring dashboard with alerting
- [ ] Developed runbooks for common operational procedures

**✅ Deployment Phase**:
- [ ] Load tested with realistic traffic patterns
- [ ] Validated failure scenarios and recovery procedures
- [ ] Configured monitoring and alerting thresholds
- [ ] Trained operations team on troubleshooting procedures

### Future Directions

Consistent hashing continues to evolve with new applications and optimizations:

**Emerging Applications**:
- **Edge Computing**: Geographic consistent hashing for edge node placement
- **Blockchain Systems**: Sharding strategies using consistent hashing
- **Machine Learning**: Model serving and distributed training coordination
- **IoT Systems**: Device clustering and data aggregation

**Research Directions**:
- **Adaptive Virtual Nodes**: Dynamic adjustment based on load patterns
- **Multi-Dimensional Hashing**: Handling complex key structures
- **Quantum-Resistant Hashing**: Post-quantum cryptographic hash functions
- **Energy-Aware Routing**: Incorporating power consumption in placement decisions

Consistent hashing remains a cornerstone of distributed systems architecture, and mastering its theory and practice is essential for building scalable, resilient systems that can handle internet-scale workloads with minimal operational overhead.

The mathematical elegance of consistent hashing—moving only 1/N of keys instead of nearly all keys during topology changes—represents the kind of algorithmic breakthrough that enables the modern internet's scale. From Amazon's trillion-request-per-day DynamoDB to Discord's real-time message routing, consistent hashing proves that elegant theory translates directly into production impact.