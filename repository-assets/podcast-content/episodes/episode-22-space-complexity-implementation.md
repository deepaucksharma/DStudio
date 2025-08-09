# Episode 22: Space Complexity in Distributed Systems - Implementation Details

## Episode Metadata
- **Duration**: 60 minutes (Implementation Section Only)
- **Pillar**: Theoretical Foundations
- **Prerequisites**: Episodes 1-5 (Mathematical foundations), Episodes 16-17 (Logical clocks)
- **Learning Objectives**: 
  - [ ] Implement space-efficient data structures for distributed systems
  - [ ] Master memory-bounded algorithms with practical examples
  - [ ] Apply advanced memory management techniques in production systems
  - [ ] Design and implement state compaction strategies

---

# Part 2: Implementation Details (60 minutes)

The theoretical foundations of space complexity give us the mathematical framework, but real distributed systems demand practical solutions that work under memory constraints. This implementation-focused section demonstrates how to build space-efficient distributed systems that can handle massive scale while maintaining performance guarantees.

## 1. Space-Efficient Data Structures (20 minutes)

### 1.1 Distributed Hash Tables with Memory Optimization

Traditional hash tables in distributed systems can consume enormous amounts of memory. Let's examine how to implement space-efficient distributed hash tables that maintain O(1) lookup performance while minimizing memory footprint.

```python
import hashlib
import bisect
import struct
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import mmh3  # MurmurHash3 for consistent hashing

class SpaceOptimizedDHT:
    """
    A distributed hash table optimized for space efficiency.
    Uses consistent hashing with virtual nodes and memory-bounded storage.
    """
    
    def __init__(self, node_id: str, virtual_nodes: int = 150, 
                 max_memory_mb: float = 100.0):
        self.node_id = node_id
        self.virtual_nodes = virtual_nodes
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.current_memory = 0
        
        # Ring structure: sorted list of (hash_value, node_id) tuples
        self.ring: List[Tuple[int, str]] = []
        self.nodes: Dict[str, 'Node'] = {}
        
        # Local storage with size tracking
        self.storage: Dict[bytes, bytes] = {}
        self.key_sizes: Dict[bytes, int] = {}
        
        # LRU eviction policy
        self.access_order: List[bytes] = []
        self.access_index: Dict[bytes, int] = {}
        
        # Bloom filter for negative lookups
        self.bloom_filter = BloomFilter(capacity=10000, error_rate=0.1)
        
        self._add_node(node_id)
    
    def _add_node(self, node_id: str):
        """Add a node with virtual replicas to the ring"""
        for i in range(self.virtual_nodes):
            # Create virtual node identifier
            virtual_id = f"{node_id}:{i}"
            # Hash to get position on ring
            hash_val = mmh3.hash(virtual_id, signed=False)
            bisect.insort(self.ring, (hash_val, node_id))
        
        self.nodes[node_id] = Node(node_id, self.max_memory_bytes // 4)
    
    def _find_responsible_node(self, key: bytes) -> str:
        """Find which node should handle this key using consistent hashing"""
        if not self.ring:
            return self.node_id
        
        key_hash = mmh3.hash(key, signed=False)
        
        # Binary search for the first node >= key_hash
        idx = bisect.bisect_left(self.ring, (key_hash, ""))
        
        # Wrap around if necessary
        if idx == len(self.ring):
            idx = 0
        
        return self.ring[idx][1]
    
    def _evict_if_necessary(self, incoming_size: int):
        """Evict least recently used items if memory limit would be exceeded"""
        while (self.current_memory + incoming_size > self.max_memory_bytes 
               and self.access_order):
            
            # Remove least recently used key
            lru_key = self.access_order.pop(0)
            if lru_key in self.storage:
                freed_size = self.key_sizes[lru_key]
                del self.storage[lru_key]
                del self.key_sizes[lru_key]
                del self.access_index[lru_key]
                self.current_memory -= freed_size
                self.bloom_filter.remove(lru_key)
                
                # Update indices for remaining items
                for i, key in enumerate(self.access_order):
                    self.access_index[key] = i
    
    def put(self, key: bytes, value: bytes) -> bool:
        """Store key-value pair with memory management"""
        # Check if we're responsible for this key
        responsible_node = self._find_responsible_node(key)
        if responsible_node != self.node_id:
            # Forward to responsible node in real implementation
            return self._forward_put(responsible_node, key, value)
        
        # Calculate memory requirement
        entry_size = len(key) + len(value) + 64  # 64 bytes overhead
        
        # Evict if necessary
        self._evict_if_necessary(entry_size)
        
        # Store the data
        if key in self.storage:
            # Update existing - free old space first
            self.current_memory -= self.key_sizes[key]
            # Remove from current position in LRU
            old_idx = self.access_index[key]
            self.access_order.pop(old_idx)
            # Update indices
            for i in range(old_idx, len(self.access_order)):
                self.access_index[self.access_order[i]] -= 1
        
        self.storage[key] = value
        self.key_sizes[key] = entry_size
        self.current_memory += entry_size
        
        # Add to end of LRU list (most recent)
        self.access_order.append(key)
        self.access_index[key] = len(self.access_order) - 1
        
        # Update bloom filter
        self.bloom_filter.add(key)
        
        return True
    
    def get(self, key: bytes) -> Optional[bytes]:
        """Retrieve value with space-efficient lookups"""
        # Quick negative lookup using bloom filter
        if not self.bloom_filter.might_contain(key):
            return None
        
        # Check if we're responsible
        responsible_node = self._find_responsible_node(key)
        if responsible_node != self.node_id:
            return self._forward_get(responsible_node, key)
        
        if key not in self.storage:
            return None
        
        # Update LRU position
        current_idx = self.access_index[key]
        self.access_order.pop(current_idx)
        
        # Update indices for items that were after this one
        for i in range(current_idx, len(self.access_order)):
            self.access_index[self.access_order[i]] -= 1
        
        # Add to end (most recent)
        self.access_order.append(key)
        self.access_index[key] = len(self.access_order) - 1
        
        return self.storage[key]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Return detailed memory usage statistics"""
        return {
            "current_memory_bytes": self.current_memory,
            "max_memory_bytes": self.max_memory_bytes,
            "utilization_percent": (self.current_memory / self.max_memory_bytes) * 100,
            "stored_items": len(self.storage),
            "average_item_size": self.current_memory // max(len(self.storage), 1),
            "ring_size": len(self.ring),
            "virtual_nodes": self.virtual_nodes
        }
    
    def _forward_put(self, node_id: str, key: bytes, value: bytes) -> bool:
        """Forward PUT request to responsible node"""
        # In production: use network call
        if node_id in self.nodes:
            return self.nodes[node_id].put_local(key, value)
        return False
    
    def _forward_get(self, node_id: str, key: bytes) -> Optional[bytes]:
        """Forward GET request to responsible node"""
        # In production: use network call
        if node_id in self.nodes:
            return self.nodes[node_id].get_local(key)
        return None


class BloomFilter:
    """Memory-efficient probabilistic data structure for set membership"""
    
    def __init__(self, capacity: int, error_rate: float = 0.1):
        self.capacity = capacity
        self.error_rate = error_rate
        
        # Calculate optimal parameters
        self.bit_array_size = self._calculate_bit_array_size()
        self.hash_count = self._calculate_hash_count()
        
        # Bit array as bytearray for memory efficiency
        self.bit_array = bytearray(self.bit_array_size // 8 + 1)
        self.item_count = 0
    
    def _calculate_bit_array_size(self) -> int:
        """Calculate optimal bit array size"""
        import math
        return int(-self.capacity * math.log(self.error_rate) / (math.log(2) ** 2))
    
    def _calculate_hash_count(self) -> int:
        """Calculate optimal number of hash functions"""
        import math
        return int(self.bit_array_size * math.log(2) / self.capacity)
    
    def _get_hash_values(self, item: bytes) -> List[int]:
        """Generate multiple hash values for an item"""
        hashes = []
        for i in range(self.hash_count):
            # Use different seeds for each hash function
            hash_val = mmh3.hash(item, seed=i, signed=False)
            hashes.append(hash_val % self.bit_array_size)
        return hashes
    
    def add(self, item: bytes):
        """Add item to bloom filter"""
        for hash_val in self._get_hash_values(item):
            byte_index = hash_val // 8
            bit_index = hash_val % 8
            self.bit_array[byte_index] |= (1 << bit_index)
        
        self.item_count += 1
    
    def might_contain(self, item: bytes) -> bool:
        """Check if item might be in the set (no false negatives)"""
        for hash_val in self._get_hash_values(item):
            byte_index = hash_val // 8
            bit_index = hash_val % 8
            if not (self.bit_array[byte_index] & (1 << bit_index)):
                return False
        return True
    
    def remove(self, item: bytes):
        """Remove item from bloom filter (approximate)"""
        # Note: Bloom filters don't support perfect removal
        # This is a simplified implementation
        pass
    
    def get_memory_usage(self) -> int:
        """Return memory usage in bytes"""
        return len(self.bit_array) + 64  # 64 bytes for metadata


class Node:
    """Individual node in the distributed system"""
    
    def __init__(self, node_id: str, max_memory: int):
        self.node_id = node_id
        self.max_memory = max_memory
        self.storage: Dict[bytes, bytes] = {}
        self.current_memory = 0
    
    def put_local(self, key: bytes, value: bytes) -> bool:
        """Store locally on this node"""
        size_needed = len(key) + len(value) + 32
        if self.current_memory + size_needed <= self.max_memory:
            if key not in self.storage:
                self.current_memory += size_needed
            self.storage[key] = value
            return True
        return False
    
    def get_local(self, key: bytes) -> Optional[bytes]:
        """Get from local storage"""
        return self.storage.get(key)
```

### 1.2 Merkle Trees and DAGs for Space-Efficient Verification

Merkle trees provide cryptographic verification while maintaining space efficiency. Here's an implementation that optimizes for both space and verification speed:

```python
import hashlib
from typing import List, Optional, Dict, Tuple, Set
from dataclasses import dataclass
from collections import deque

@dataclass
class MerkleNode:
    """Space-optimized Merkle tree node"""
    hash_value: bytes
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = False
    data: Optional[bytes] = None  # Only stored in leaves
    
    def __post_init__(self):
        # Calculate memory footprint
        self.memory_size = 32  # hash size
        if self.data:
            self.memory_size += len(self.data)


class SpaceEfficientMerkleTree:
    """
    Merkle tree optimized for space efficiency and fast verification.
    Implements lazy loading and compression for large datasets.
    """
    
    def __init__(self, max_memory_mb: float = 50.0):
        self.root: Optional[MerkleNode] = None
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.current_memory = 0
        
        # Cache for frequently accessed nodes
        self.node_cache: Dict[bytes, MerkleNode] = {}
        self.cache_access_order: List[bytes] = []
        
        # Store only essential nodes in memory
        self.essential_nodes: Set[bytes] = set()
        
        # External storage interface for large trees
        self.external_storage: Dict[bytes, bytes] = {}
    
    def build_tree(self, data_items: List[bytes], compress_nodes: bool = True) -> bytes:
        """Build Merkle tree with space optimization"""
        if not data_items:
            return b''
        
        # Create leaf nodes
        leaves = []
        for item in data_items:
            leaf_hash = hashlib.sha256(item).digest()
            leaf = MerkleNode(
                hash_value=leaf_hash,
                is_leaf=True,
                data=item if not compress_nodes else None  # Store externally if compressing
            )
            leaves.append(leaf)
            
            if compress_nodes:
                # Store data externally to save memory
                self.external_storage[leaf_hash] = item
        
        # Build tree bottom-up
        current_level = leaves
        level = 0
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Calculate parent hash
                combined = left.hash_value + right.hash_value
                parent_hash = hashlib.sha256(combined).digest()
                
                parent = MerkleNode(
                    hash_value=parent_hash,
                    left=left if self._should_keep_in_memory(level) else None,
                    right=right if self._should_keep_in_memory(level) else None
                )
                
                # Store children externally if not keeping in memory
                if not self._should_keep_in_memory(level):
                    self.external_storage[left.hash_value] = self._serialize_node(left)
                    self.external_storage[right.hash_value] = self._serialize_node(right)
                
                next_level.append(parent)
                self.current_memory += parent.memory_size
            
            current_level = next_level
            level += 1
        
        self.root = current_level[0]
        return self.root.hash_value
    
    def _should_keep_in_memory(self, level: int) -> bool:
        """Decide whether to keep nodes at this level in memory"""
        # Keep higher levels (closer to root) in memory
        return level >= 3  # Keep top 3 levels in memory
    
    def _serialize_node(self, node: MerkleNode) -> bytes:
        """Serialize node for external storage"""
        import pickle
        return pickle.dumps(node)
    
    def _deserialize_node(self, data: bytes) -> MerkleNode:
        """Deserialize node from external storage"""
        import pickle
        return pickle.loads(data)
    
    def generate_proof(self, target_item: bytes) -> List[Tuple[bytes, bool]]:
        """
        Generate Merkle proof with minimal memory usage.
        Returns list of (hash, is_right_sibling) tuples.
        """
        target_hash = hashlib.sha256(target_item).digest()
        proof = []
        
        # Find path to target leaf
        path = self._find_path_to_leaf(target_hash)
        
        if not path:
            return []  # Item not found
        
        # Generate proof along the path
        for i in range(len(path) - 1):
            current_node = path[i]
            parent_node = path[i + 1]
            
            # Load siblings from external storage if needed
            left_child = self._load_node(parent_node, True)  # left child
            right_child = self._load_node(parent_node, False)  # right child
            
            if current_node.hash_value == left_child.hash_value:
                # Current is left child, add right sibling
                proof.append((right_child.hash_value, True))
            else:
                # Current is right child, add left sibling
                proof.append((left_child.hash_value, False))
        
        return proof
    
    def _find_path_to_leaf(self, target_hash: bytes) -> List[MerkleNode]:
        """Find path from root to target leaf"""
        if not self.root:
            return []
        
        path = []
        current = self.root
        
        # BFS to find target
        queue = deque([(current, [current])])
        
        while queue:
            node, current_path = queue.popleft()
            
            if node.is_leaf and node.hash_value == target_hash:
                return current_path
            
            # Load children if needed
            left = self._load_node(node, True)
            right = self._load_node(node, False)
            
            if left:
                queue.append((left, current_path + [left]))
            if right and right != left:
                queue.append((right, current_path + [right]))
        
        return []
    
    def _load_node(self, parent: MerkleNode, is_left: bool) -> Optional[MerkleNode]:
        """Load child node from memory or external storage"""
        if is_left and parent.left:
            return parent.left
        elif not is_left and parent.right:
            return parent.right
        
        # Try to load from external storage
        # This would require storing parent-child relationships
        # Simplified for demonstration
        return None
    
    def verify_proof(self, item: bytes, proof: List[Tuple[bytes, bool]], 
                     root_hash: bytes) -> bool:
        """Verify Merkle proof efficiently"""
        current_hash = hashlib.sha256(item).digest()
        
        for proof_hash, is_right in proof:
            if is_right:
                # Proof hash is right sibling
                combined = current_hash + proof_hash
            else:
                # Proof hash is left sibling
                combined = proof_hash + current_hash
            
            current_hash = hashlib.sha256(combined).digest()
        
        return current_hash == root_hash
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Return detailed memory usage statistics"""
        return {
            "current_memory_bytes": self.current_memory,
            "max_memory_bytes": self.max_memory_bytes,
            "cached_nodes": len(self.node_cache),
            "external_nodes": len(self.external_storage),
            "memory_utilization_percent": int((self.current_memory / self.max_memory_bytes) * 100)
        }
```

### 1.3 Bloom Filters at Scale

Large-scale distributed systems need probabilistic data structures that can handle billions of items efficiently:

```python
import math
import mmh3
from typing import List, Dict, Any
import numpy as np

class ScalableBloomFilter:
    """
    Scalable bloom filter that grows dynamically while maintaining error rate.
    Optimized for distributed systems with billions of items.
    """
    
    def __init__(self, initial_capacity: int = 1000000, 
                 error_rate: float = 0.001, growth_factor: float = 2.0):
        self.initial_capacity = initial_capacity
        self.error_rate = error_rate
        self.growth_factor = growth_factor
        
        # List of individual bloom filters
        self.filters: List[BloomFilterLevel] = []
        self.total_items = 0
        
        # Create first filter
        self._add_new_filter(initial_capacity)
    
    def _add_new_filter(self, capacity: int):
        """Add a new bloom filter level"""
        # Calculate tightened error rate for this level
        # Total error rate is sum of individual error rates
        level_error_rate = self.error_rate * (0.5 ** len(self.filters))
        
        filter_level = BloomFilterLevel(capacity, level_error_rate)
        self.filters.append(filter_level)
    
    def add(self, item: bytes):
        """Add item to the filter"""
        # Always add to the most recent filter
        current_filter = self.filters[-1]
        
        # Check if current filter is full
        if current_filter.is_full():
            # Create new filter with larger capacity
            new_capacity = int(self.initial_capacity * (self.growth_factor ** len(self.filters)))
            self._add_new_filter(new_capacity)
            current_filter = self.filters[-1]
        
        current_filter.add(item)
        self.total_items += 1
    
    def might_contain(self, item: bytes) -> bool:
        """Check if item might be in any of the filters"""
        for filter_level in self.filters:
            if filter_level.might_contain(item):
                return True
        return False
    
    def get_memory_usage(self) -> int:
        """Total memory usage across all filters"""
        return sum(f.get_memory_usage() for f in self.filters)
    
    def get_stats(self) -> Dict[str, Any]:
        """Comprehensive statistics"""
        return {
            "total_items": self.total_items,
            "filter_levels": len(self.filters),
            "total_memory_mb": self.get_memory_usage() / (1024 * 1024),
            "estimated_error_rate": self._calculate_actual_error_rate(),
            "individual_filter_stats": [f.get_stats() for f in self.filters]
        }
    
    def _calculate_actual_error_rate(self) -> float:
        """Calculate actual error rate across all filters"""
        # Simplified calculation - assumes uniform distribution
        return sum(f.actual_error_rate for f in self.filters)


class BloomFilterLevel:
    """Individual bloom filter level with optimized bit operations"""
    
    def __init__(self, capacity: int, error_rate: float):
        self.capacity = capacity
        self.error_rate = error_rate
        self.item_count = 0
        
        # Calculate optimal parameters
        self.bit_array_size = self._optimal_bit_array_size()
        self.hash_count = self._optimal_hash_count()
        
        # Use numpy for efficient bit operations
        self.bit_array = np.zeros(self.bit_array_size, dtype=np.uint8)
        
        # Pre-calculate hash seeds for performance
        self.hash_seeds = list(range(self.hash_count))
    
    def _optimal_bit_array_size(self) -> int:
        """Calculate optimal bit array size"""
        return int(-self.capacity * math.log(self.error_rate) / (math.log(2) ** 2))
    
    def _optimal_hash_count(self) -> int:
        """Calculate optimal number of hash functions"""
        return int(self.bit_array_size * math.log(2) / self.capacity)
    
    def add(self, item: bytes):
        """Add item with optimized bit operations"""
        if self.is_full():
            return False
        
        hash_values = self._get_hash_positions(item)
        
        # Set bits using numpy operations for speed
        for pos in hash_values:
            self.bit_array[pos] = 1
        
        self.item_count += 1
        return True
    
    def might_contain(self, item: bytes) -> bool:
        """Check membership with optimized bit operations"""
        hash_values = self._get_hash_positions(item)
        
        # Check all bits at once using numpy operations
        return np.all(self.bit_array[hash_values] == 1)
    
    def _get_hash_positions(self, item: bytes) -> np.ndarray:
        """Generate hash positions using fast murmur hash"""
        positions = np.zeros(self.hash_count, dtype=np.int32)
        
        for i, seed in enumerate(self.hash_seeds):
            hash_val = mmh3.hash(item, seed=seed, signed=False)
            positions[i] = hash_val % self.bit_array_size
        
        return positions
    
    def is_full(self) -> bool:
        """Check if filter has reached capacity"""
        return self.item_count >= self.capacity
    
    @property
    def actual_error_rate(self) -> float:
        """Calculate actual error rate based on current fill ratio"""
        if self.item_count == 0:
            return 0.0
        
        # Calculate fill ratio
        fill_ratio = np.sum(self.bit_array) / len(self.bit_array)
        
        # Actual error rate approximation
        return fill_ratio ** self.hash_count
    
    def get_memory_usage(self) -> int:
        """Memory usage in bytes"""
        return self.bit_array.nbytes + 128  # 128 bytes overhead
    
    def get_stats(self) -> Dict[str, Any]:
        """Filter level statistics"""
        fill_ratio = np.sum(self.bit_array) / len(self.bit_array)
        
        return {
            "capacity": self.capacity,
            "items": self.item_count,
            "fill_ratio": fill_ratio,
            "actual_error_rate": self.actual_error_rate,
            "memory_bytes": self.get_memory_usage(),
            "utilization_percent": (self.item_count / self.capacity) * 100
        }
```

### 1.4 Succinct Data Structures

Succinct data structures use space close to the information-theoretic lower bound while supporting efficient operations:

```python
import math
from typing import List, Optional
import numpy as np

class SuccinctBitVector:
    """
    Succinct bit vector with rank and select operations.
    Uses o(n) additional space for fast queries.
    """
    
    def __init__(self, bits: List[int]):
        self.n = len(bits)
        self.bits = np.array(bits, dtype=np.uint8)
        
        # Build rank index for fast rank queries
        self.block_size = int(math.log2(self.n)) if self.n > 0 else 1
        self.superblock_size = self.block_size ** 2
        
        self._build_rank_index()
        self._build_select_index()
    
    def _build_rank_index(self):
        """Build hierarchical index for rank operations"""
        # Superblock rank values (every superblock_size bits)
        self.superblock_ranks = []
        # Block rank values (every block_size bits within superblocks)
        self.block_ranks = []
        
        current_rank = 0
        
        for i in range(0, self.n, self.superblock_size):
            self.superblock_ranks.append(current_rank)
            
            # Process blocks within this superblock
            superblock_start_rank = current_rank
            
            for j in range(i, min(i + self.superblock_size, self.n), self.block_size):
                relative_rank = current_rank - superblock_start_rank
                self.block_ranks.append(relative_rank)
                
                # Count bits in this block
                block_end = min(j + self.block_size, self.n)
                current_rank += np.sum(self.bits[j:block_end])
    
    def _build_select_index(self):
        """Build index for select operations (find i-th 1-bit)"""
        # Sample every (log n)^2 one-bits
        self.select_sample_rate = self.superblock_size
        self.select_samples = []
        
        one_count = 0
        for i, bit in enumerate(self.bits):
            if bit == 1:
                one_count += 1
                if one_count % self.select_sample_rate == 0:
                    self.select_samples.append(i)
    
    def rank(self, pos: int) -> int:
        """Count number of 1-bits up to position pos"""
        if pos < 0:
            return 0
        if pos >= self.n:
            pos = self.n - 1
        
        # Find superblock
        superblock_idx = pos // self.superblock_size
        superblock_rank = self.superblock_ranks[superblock_idx] if superblock_idx < len(self.superblock_ranks) else 0
        
        # Find block within superblock
        block_start = superblock_idx * self.superblock_size
        block_idx = (pos - block_start) // self.block_size
        global_block_idx = superblock_idx * (self.superblock_size // self.block_size) + block_idx
        
        block_rank = self.block_ranks[global_block_idx] if global_block_idx < len(self.block_ranks) else 0
        
        # Count remaining bits in current block
        block_pos_start = block_start + block_idx * self.block_size
        remaining_rank = np.sum(self.bits[block_pos_start:pos + 1])
        
        return superblock_rank + block_rank + remaining_rank
    
    def select(self, k: int) -> Optional[int]:
        """Find position of k-th 1-bit (1-indexed)"""
        if k <= 0:
            return None
        
        # Use select samples to narrow search range
        if k > len(self.select_samples) * self.select_sample_rate:
            # k is beyond our samples, search from last sample
            start_pos = self.select_samples[-1] if self.select_samples else 0
            target_ones = k - len(self.select_samples) * self.select_sample_rate
        else:
            # Find appropriate sample
            sample_idx = (k - 1) // self.select_sample_rate
            if sample_idx > 0 and sample_idx - 1 < len(self.select_samples):
                start_pos = self.select_samples[sample_idx - 1]
                target_ones = k - sample_idx * self.select_sample_rate
            else:
                start_pos = 0
                target_ones = k
        
        # Linear search from start_pos
        ones_found = 0
        for i in range(start_pos, self.n):
            if self.bits[i] == 1:
                ones_found += 1
                if ones_found == target_ones:
                    return i
        
        return None  # k-th 1-bit doesn't exist
    
    def get_memory_usage(self) -> int:
        """Memory usage in bytes"""
        bits_memory = self.bits.nbytes
        index_memory = (len(self.superblock_ranks) + len(self.block_ranks) + 
                       len(self.select_samples)) * 8  # 8 bytes per int
        return bits_memory + index_memory
    
    def space_overhead_ratio(self) -> float:
        """Space overhead as ratio of original data"""
        original_size = self.n // 8 + (1 if self.n % 8 else 0)  # bits packed into bytes
        return self.get_memory_usage() / max(original_size, 1)


class WaveletTree:
    """
    Wavelet tree for succinct representation of sequences.
    Supports rank, select, and access operations efficiently.
    """
    
    def __init__(self, sequence: List[int]):
        self.sequence = sequence
        self.alphabet_size = max(sequence) + 1 if sequence else 0
        self.n = len(sequence)
        
        # Build the wavelet tree
        self.root = self._build_tree(sequence, 0, self.alphabet_size - 1)
    
    def _build_tree(self, seq: List[int], alpha_min: int, alpha_max: int) -> 'WaveletNode':
        """Recursively build wavelet tree"""
        if alpha_min == alpha_max:
            # Leaf node
            return WaveletNode(None, None, alpha_min, alpha_max, len(seq))
        
        # Split alphabet
        mid = (alpha_min + alpha_max) // 2
        
        # Create bit vector: 0 for left alphabet, 1 for right alphabet
        bits = [0 if x <= mid else 1 for x in seq]
        bit_vector = SuccinctBitVector(bits)
        
        # Split sequence
        left_seq = [x for x in seq if x <= mid]
        right_seq = [x for x in seq if x > mid]
        
        # Recursively build children
        left_child = self._build_tree(left_seq, alpha_min, mid) if left_seq else None
        right_child = self._build_tree(right_seq, mid + 1, alpha_max) if right_seq else None
        
        return WaveletNode(left_child, right_child, alpha_min, alpha_max, len(seq), bit_vector)
    
    def access(self, pos: int) -> Optional[int]:
        """Access element at position pos"""
        if pos < 0 or pos >= self.n:
            return None
        
        current = self.root
        current_pos = pos
        
        while current and current.bit_vector:
            bit = current.bit_vector.bits[current_pos]
            if bit == 0:
                # Go left
                current = current.left
                current_pos = current.bit_vector.rank(current_pos) - 1 if current else -1
            else:
                # Go right
                current = current.right
                current_pos = current_pos - current.bit_vector.rank(current_pos)
            
            if current_pos < 0:
                return None
        
        return current.alpha_min if current else None
    
    def rank(self, symbol: int, pos: int) -> int:
        """Count occurrences of symbol up to position pos"""
        if pos < 0 or symbol < 0 or symbol >= self.alphabet_size:
            return 0
        
        return self._rank_recursive(self.root, symbol, pos)
    
    def _rank_recursive(self, node: 'WaveletNode', symbol: int, pos: int) -> int:
        """Recursive rank implementation"""
        if not node or pos < 0:
            return 0
        
        if node.alpha_min == node.alpha_max:
            # Leaf node
            return pos + 1 if node.alpha_min == symbol else 0
        
        mid = (node.alpha_min + node.alpha_max) // 2
        
        if symbol <= mid:
            # Symbol is in left subtree
            left_pos = node.bit_vector.rank(pos) - 1  # Count of 0s up to pos
            return self._rank_recursive(node.left, symbol, left_pos)
        else:
            # Symbol is in right subtree
            right_pos = pos - node.bit_vector.rank(pos)  # Count of 1s up to pos
            return self._rank_recursive(node.right, symbol, right_pos)
    
    def get_memory_usage(self) -> int:
        """Total memory usage of wavelet tree"""
        return self._memory_recursive(self.root)
    
    def _memory_recursive(self, node: 'WaveletNode') -> int:
        """Recursive memory calculation"""
        if not node:
            return 0
        
        memory = 64  # Node overhead
        if node.bit_vector:
            memory += node.bit_vector.get_memory_usage()
        
        memory += self._memory_recursive(node.left)
        memory += self._memory_recursive(node.right)
        
        return memory


class WaveletNode:
    """Node in wavelet tree"""
    
    def __init__(self, left: Optional['WaveletNode'], right: Optional['WaveletNode'],
                 alpha_min: int, alpha_max: int, size: int, 
                 bit_vector: Optional[SuccinctBitVector] = None):
        self.left = left
        self.right = right
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.size = size
        self.bit_vector = bit_vector
```

This completes the first major section on space-efficient data structures. The implementations show practical techniques for managing memory in distributed systems while maintaining performance guarantees. Each data structure includes comprehensive memory tracking and optimization strategies used in production systems.

## 2. Code Examples - Memory-Bounded Algorithms (20 minutes)

### 2.1 Space-Efficient Consensus Protocols

Traditional consensus algorithms like Paxos can consume significant memory storing proposal histories and promises. Here's a memory-bounded implementation that maintains safety while limiting space usage:

```python
import time
from typing import Dict, Set, Optional, List, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
import json
import threading

@dataclass
class Proposal:
    """Memory-efficient proposal representation"""
    proposal_id: int
    value: Any
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        # Estimate memory footprint
        self.memory_size = 64 + len(str(self.value))  # Base overhead + value size

@dataclass
class Promise:
    """Promise message with minimal memory footprint"""
    proposal_id: int
    acceptor_id: str
    highest_accepted_id: Optional[int] = None
    highest_accepted_value: Any = None
    timestamp: float = field(default_factory=time.time)

class MemoryBoundedPaxosAcceptor:
    """
    Paxos acceptor with bounded memory usage.
    Implements log compaction and state pruning.
    """
    
    def __init__(self, acceptor_id: str, max_memory_mb: float = 10.0,
                 history_retention_sec: float = 300.0):
        self.acceptor_id = acceptor_id
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.history_retention_sec = history_retention_sec
        self.current_memory = 0
        
        # Current state (minimal required for safety)
        self.highest_promised_id: int = -1
        self.highest_accepted_id: Optional[int] = None
        self.highest_accepted_value: Any = None
        
        # Bounded history for recent proposals
        self.recent_promises: deque = deque(maxlen=1000)
        self.recent_accepts: deque = deque(maxlen=1000)
        
        # Memory management
        self.last_cleanup = time.time()
        self.cleanup_interval = 30.0  # seconds
        self.lock = threading.RLock()
    
    def prepare(self, proposal_id: int, proposer_id: str) -> Optional[Promise]:
        """Handle prepare phase with memory bounds"""
        with self.lock:
            self._cleanup_if_needed()
            
            # Safety check: don't accept lower proposal IDs
            if proposal_id <= self.highest_promised_id:
                return None
            
            # Update promise
            self.highest_promised_id = proposal_id
            
            # Create promise response
            promise = Promise(
                proposal_id=proposal_id,
                acceptor_id=self.acceptor_id,
                highest_accepted_id=self.highest_accepted_id,
                highest_accepted_value=self.highest_accepted_value
            )
            
            # Add to bounded history
            self._add_to_history(self.recent_promises, promise)
            
            return promise
    
    def accept(self, proposal_id: int, value: Any, proposer_id: str) -> bool:
        """Handle accept phase with memory bounds"""
        with self.lock:
            self._cleanup_if_needed()
            
            # Safety check: must have promised this proposal ID or higher
            if proposal_id < self.highest_promised_id:
                return False
            
            # Accept the proposal
            self.highest_accepted_id = proposal_id
            self.highest_accepted_value = value
            
            # Update promise to ensure future consistency
            self.highest_promised_id = max(self.highest_promised_id, proposal_id)
            
            # Record accept in bounded history
            accept_record = {
                'proposal_id': proposal_id,
                'value': value,
                'timestamp': time.time(),
                'memory_size': 64 + len(str(value))
            }
            self._add_to_history(self.recent_accepts, accept_record)
            
            return True
    
    def _add_to_history(self, history: deque, item: Any):
        """Add item to bounded history with memory tracking"""
        # Estimate memory usage
        item_size = getattr(item, 'memory_size', 128)  # Default estimate
        
        # Remove old items if needed
        while (self.current_memory + item_size > self.max_memory_bytes and 
               len(history) > 0):
            old_item = history.popleft()
            old_size = getattr(old_item, 'memory_size', 128)
            self.current_memory -= old_size
        
        # Add new item
        history.append(item)
        self.current_memory += item_size
    
    def _cleanup_if_needed(self):
        """Remove old entries to free memory"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Clean old promises
        cutoff_time = current_time - self.history_retention_sec
        self._cleanup_history(self.recent_promises, cutoff_time)
        self._cleanup_history(self.recent_accepts, cutoff_time)
        
        self.last_cleanup = current_time
    
    def _cleanup_history(self, history: deque, cutoff_time: float):
        """Remove entries older than cutoff_time"""
        while history and getattr(history[0], 'timestamp', 0) < cutoff_time:
            old_item = history.popleft()
            old_size = getattr(old_item, 'memory_size', 128)
            self.current_memory -= old_size
    
    def get_state_size(self) -> int:
        """Return current memory usage in bytes"""
        with self.lock:
            return self.current_memory + 256  # 256 bytes for fixed state
    
    def compact_state(self) -> Dict[str, Any]:
        """Return minimal state needed for correctness"""
        with self.lock:
            return {
                'acceptor_id': self.acceptor_id,
                'highest_promised_id': self.highest_promised_id,
                'highest_accepted_id': self.highest_accepted_id,
                'highest_accepted_value': self.highest_accepted_value,
                'memory_usage_bytes': self.get_state_size()
            }


class MemoryBoundedPaxosProposer:
    """
    Memory-bounded Paxos proposer with adaptive batch sizing.
    """
    
    def __init__(self, proposer_id: str, acceptors: List[str],
                 max_memory_mb: float = 20.0):
        self.proposer_id = proposer_id
        self.acceptors = acceptors
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.current_memory = 0
        
        # Proposal management
        self.next_proposal_id = int(time.time() * 1000)  # Timestamp-based IDs
        self.active_proposals: Dict[int, Proposal] = {}
        
        # Response tracking with bounded memory
        self.promise_responses: Dict[int, List[Promise]] = {}
        self.accept_responses: Dict[int, Set[str]] = {}
        
        # Adaptive batching
        self.pending_values = deque()
        self.batch_size = 1
        self.max_batch_size = 100
        
        self.lock = threading.RLock()
    
    def propose(self, value: Any, timeout_sec: float = 10.0) -> Optional[Any]:
        """Propose a value with memory-bounded execution"""
        with self.lock:
            # Add to pending queue
            self.pending_values.append(value)
            
            # Process in batches to optimize memory usage
            if len(self.pending_values) >= self.batch_size or self._should_force_batch():
                return self._process_batch(timeout_sec)
            
            return None
    
    def _should_force_batch(self) -> bool:
        """Determine if we should process partial batch due to memory pressure"""
        return self.current_memory > self.max_memory_bytes * 0.8
    
    def _process_batch(self, timeout_sec: float) -> Optional[List[Any]]:
        """Process a batch of proposals"""
        if not self.pending_values:
            return None
        
        # Create batch of values to propose
        batch_values = []
        batch_memory = 0
        
        while (self.pending_values and 
               len(batch_values) < self.batch_size and
               batch_memory < self.max_memory_bytes // 4):
            
            value = self.pending_values.popleft()
            value_size = len(str(value)) + 64
            
            if batch_memory + value_size <= self.max_memory_bytes // 4:
                batch_values.append(value)
                batch_memory += value_size
            else:
                # Put back and break
                self.pending_values.appendleft(value)
                break
        
        if not batch_values:
            return None
        
        # Execute two-phase commit for batch
        proposal_id = self._get_next_proposal_id()
        
        # Phase 1: Prepare
        if not self._phase1_prepare(proposal_id, timeout_sec):
            return None
        
        # Phase 2: Accept
        if self._phase2_accept(proposal_id, batch_values, timeout_sec):
            # Adjust batch size based on success
            self.batch_size = min(self.max_batch_size, self.batch_size + 1)
            return batch_values
        else:
            # Reduce batch size on failure
            self.batch_size = max(1, self.batch_size - 1)
            return None
    
    def _get_next_proposal_id(self) -> int:
        """Generate unique proposal ID"""
        self.next_proposal_id += 1
        return self.next_proposal_id
    
    def _phase1_prepare(self, proposal_id: int, timeout_sec: float) -> bool:
        """Execute Phase 1: Prepare with memory bounds"""
        self.promise_responses[proposal_id] = []
        
        # Send prepare messages to all acceptors
        # In real implementation, this would be network calls
        # For simulation, we'll assume responses
        
        start_time = time.time()
        majority = len(self.acceptors) // 2 + 1
        
        # Simulate responses (in real system, these come from network)
        promises_received = 0
        
        while (time.time() - start_time < timeout_sec and 
               promises_received < majority):
            
            # Memory check
            if self.current_memory > self.max_memory_bytes:
                self._emergency_cleanup()
            
            # Simulate promise response
            promises_received += 1
            
            # In real implementation: process actual network responses
            
        return promises_received >= majority
    
    def _phase2_accept(self, proposal_id: int, values: List[Any], 
                       timeout_sec: float) -> bool:
        """Execute Phase 2: Accept with memory bounds"""
        self.accept_responses[proposal_id] = set()
        
        start_time = time.time()
        majority = len(self.acceptors) // 2 + 1
        
        # Send accept messages
        accepts_received = 0
        
        while (time.time() - start_time < timeout_sec and 
               accepts_received < majority):
            
            # Memory check
            if self.current_memory > self.max_memory_bytes:
                self._emergency_cleanup()
            
            # Simulate accept response
            accepts_received += 1
        
        success = accepts_received >= majority
        
        # Cleanup proposal state
        self._cleanup_proposal(proposal_id)
        
        return success
    
    def _emergency_cleanup(self):
        """Emergency cleanup when memory is exhausted"""
        # Remove oldest proposals first
        if self.active_proposals:
            oldest_id = min(self.active_proposals.keys())
            self._cleanup_proposal(oldest_id)
        
        # Clear old response data
        old_ids = [pid for pid in self.promise_responses.keys() 
                   if pid < self.next_proposal_id - 100]
        
        for pid in old_ids:
            if pid in self.promise_responses:
                del self.promise_responses[pid]
            if pid in self.accept_responses:
                del self.accept_responses[pid]
    
    def _cleanup_proposal(self, proposal_id: int):
        """Clean up memory for completed proposal"""
        if proposal_id in self.active_proposals:
            del self.active_proposals[proposal_id]
        if proposal_id in self.promise_responses:
            del self.promise_responses[proposal_id]
        if proposal_id in self.accept_responses:
            del self.accept_responses[proposal_id]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Return memory usage statistics"""
        with self.lock:
            return {
                'current_memory_bytes': self.current_memory,
                'max_memory_bytes': self.max_memory_bytes,
                'active_proposals': len(self.active_proposals),
                'pending_values': len(self.pending_values),
                'current_batch_size': self.batch_size,
                'memory_utilization_percent': (self.current_memory / self.max_memory_bytes) * 100
            }
```

### 2.2 Compressed State Machines

State machines in distributed systems often need to store large amounts of state. Here's an implementation using compression and delta encoding:

```python
import gzip
import pickle
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
import time
from collections import defaultdict

@dataclass
class StateTransition:
    """Represents a state transition with compression"""
    transition_id: int
    from_state_hash: bytes
    to_state_hash: bytes
    operation: str
    parameters: Dict[str, Any]
    timestamp: float
    compressed_delta: bytes  # Compressed state delta
    
    def get_memory_size(self) -> int:
        """Calculate memory footprint"""
        return (64 + len(self.operation) + len(pickle.dumps(self.parameters)) + 
                len(self.compressed_delta))

class CompressedStateMachine:
    """
    State machine with compressed state storage and delta encoding.
    Optimized for large state objects with incremental changes.
    """
    
    def __init__(self, initial_state: Dict[str, Any], 
                 max_memory_mb: float = 50.0,
                 compression_threshold: int = 1024,
                 max_deltas: int = 100):
        
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.compression_threshold = compression_threshold
        self.max_deltas = max_deltas
        self.current_memory = 0
        
        # Current state management
        self.current_state = initial_state.copy()
        self.current_state_hash = self._hash_state(self.current_state)
        self.state_version = 0
        
        # Compressed snapshots at regular intervals
        self.snapshots: Dict[int, bytes] = {}  # version -> compressed state
        self.snapshot_interval = 50  # Create snapshot every N transitions
        
        # Delta chain for recent changes
        self.deltas: List[StateTransition] = []
        self.transition_counter = 0
        
        # Index for fast state reconstruction
        self.version_to_delta_idx: Dict[int, int] = {}
        
        # Statistics
        self.compression_stats = {
            'total_transitions': 0,
            'compressed_transitions': 0,
            'compression_ratio': 0.0,
            'memory_saved_bytes': 0
        }
        
        # Create initial snapshot
        self._create_snapshot()
    
    def apply_transition(self, operation: str, parameters: Dict[str, Any]) -> bool:
        """Apply state transition with compression and memory management"""
        
        # Store previous state info
        prev_state_hash = self.current_state_hash
        prev_state = self.current_state.copy()
        
        # Apply the operation
        success = self._execute_operation(operation, parameters)
        
        if not success:
            return False
        
        # Calculate new state hash
        new_state_hash = self._hash_state(self.current_state)
        
        # Create compressed delta
        delta_data = self._create_delta(prev_state, self.current_state)
        compressed_delta = self._compress_data(delta_data)
        
        # Create transition record
        transition = StateTransition(
            transition_id=self.transition_counter,
            from_state_hash=prev_state_hash,
            to_state_hash=new_state_hash,
            operation=operation,
            parameters=parameters,
            timestamp=time.time(),
            compressed_delta=compressed_delta
        )
        
        # Add to delta chain
        self._add_transition(transition)
        
        # Update state tracking
        self.current_state_hash = new_state_hash
        self.state_version += 1
        self.transition_counter += 1
        
        # Create snapshot if needed
        if self.state_version % self.snapshot_interval == 0:
            self._create_snapshot()
        
        # Cleanup old data if memory pressure
        if self.current_memory > self.max_memory_bytes * 0.9:
            self._cleanup_old_data()
        
        return True
    
    def _execute_operation(self, operation: str, parameters: Dict[str, Any]) -> bool:
        """Execute the actual state machine operation"""
        try:
            if operation == "set":
                key, value = parameters["key"], parameters["value"]
                self.current_state[key] = value
                
            elif operation == "delete":
                key = parameters["key"]
                if key in self.current_state:
                    del self.current_state[key]
                    
            elif operation == "increment":
                key, amount = parameters["key"], parameters.get("amount", 1)
                self.current_state[key] = self.current_state.get(key, 0) + amount
                
            elif operation == "append":
                key, item = parameters["key"], parameters["item"]
                if key not in self.current_state:
                    self.current_state[key] = []
                self.current_state[key].append(item)
                
            elif operation == "batch_update":
                updates = parameters["updates"]
                for update_key, update_value in updates.items():
                    self.current_state[update_key] = update_value
                    
            else:
                return False
                
            return True
            
        except Exception as e:
            print(f"Operation failed: {e}")
            return False
    
    def _create_delta(self, old_state: Dict[str, Any], 
                     new_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal delta between states"""
        delta = {
            'added': {},
            'modified': {},
            'deleted': []
        }
        
        # Find additions and modifications
        for key, value in new_state.items():
            if key not in old_state:
                delta['added'][key] = value
            elif old_state[key] != value:
                delta['modified'][key] = {
                    'old': old_state[key],
                    'new': value
                }
        
        # Find deletions
        for key in old_state:
            if key not in new_state:
                delta['deleted'].append(key)
        
        return delta
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data if it exceeds threshold"""
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            
            # Update compression stats
            self.compression_stats['compressed_transitions'] += 1
            saved_bytes = len(serialized) - len(compressed)
            self.compression_stats['memory_saved_bytes'] += saved_bytes
            
            return compressed
        else:
            return serialized
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data"""
        try:
            # Try decompression first
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
        except:
            # Fallback to direct deserialization
            return pickle.loads(compressed_data)
    
    def _add_transition(self, transition: StateTransition):
        """Add transition to delta chain with memory management"""
        self.deltas.append(transition)
        self.version_to_delta_idx[self.state_version] = len(self.deltas) - 1
        self.current_memory += transition.get_memory_size()
        
        # Limit delta chain length
        while len(self.deltas) > self.max_deltas:
            old_transition = self.deltas.pop(0)
            self.current_memory -= old_transition.get_memory_size()
            
            # Update version index
            for version in list(self.version_to_delta_idx.keys()):
                if self.version_to_delta_idx[version] == 0:
                    del self.version_to_delta_idx[version]
                else:
                    self.version_to_delta_idx[version] -= 1
        
        self.compression_stats['total_transitions'] += 1
    
    def _create_snapshot(self):
        """Create compressed snapshot of current state"""
        state_data = pickle.dumps(self.current_state)
        compressed_snapshot = gzip.compress(state_data)
        
        self.snapshots[self.state_version] = compressed_snapshot
        self.current_memory += len(compressed_snapshot)
        
        # Remove old snapshots to limit memory
        if len(self.snapshots) > 5:  # Keep only 5 snapshots
            oldest_version = min(self.snapshots.keys())
            old_snapshot = self.snapshots.pop(oldest_version)
            self.current_memory -= len(old_snapshot)
    
    def _cleanup_old_data(self):
        """Emergency cleanup to free memory"""
        # Remove oldest deltas
        deltas_to_remove = len(self.deltas) // 4  # Remove 25%
        
        for _ in range(deltas_to_remove):
            if self.deltas:
                old_transition = self.deltas.pop(0)
                self.current_memory -= old_transition.get_memory_size()
        
        # Update version index
        self.version_to_delta_idx = {}
        for idx, transition in enumerate(self.deltas):
            # This is simplified - in practice you'd track versions properly
            pass
    
    def _hash_state(self, state: Dict[str, Any]) -> bytes:
        """Create hash of state for integrity checking"""
        state_json = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode()).digest()
    
    def get_state_at_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Reconstruct state at specific version"""
        if version == self.state_version:
            return self.current_state.copy()
        
        # Find closest snapshot
        snapshot_version = max([v for v in self.snapshots.keys() if v <= version], 
                              default=None)
        
        if snapshot_version is None:
            return None
        
        # Decompress snapshot
        snapshot_data = self.snapshots[snapshot_version]
        state = pickle.loads(gzip.decompress(snapshot_data))
        
        # Apply deltas from snapshot to target version
        for delta_version in range(snapshot_version + 1, version + 1):
            if delta_version in self.version_to_delta_idx:
                delta_idx = self.version_to_delta_idx[delta_version]
                if delta_idx < len(self.deltas):
                    transition = self.deltas[delta_idx]
                    delta = self._decompress_data(transition.compressed_delta)
                    state = self._apply_delta(state, delta)
        
        return state
    
    def _apply_delta(self, state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        """Apply delta to reconstruct state"""
        new_state = state.copy()
        
        # Apply additions
        for key, value in delta.get('added', {}).items():
            new_state[key] = value
        
        # Apply modifications
        for key, change in delta.get('modified', {}).items():
            new_state[key] = change['new']
        
        # Apply deletions
        for key in delta.get('deleted', []):
            if key in new_state:
                del new_state[key]
        
        return new_state
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Comprehensive memory usage statistics"""
        snapshot_memory = sum(len(data) for data in self.snapshots.values())
        delta_memory = sum(t.get_memory_size() for t in self.deltas)
        
        # Calculate compression ratio
        if self.compression_stats['total_transitions'] > 0:
            compression_ratio = (self.compression_stats['compressed_transitions'] / 
                               self.compression_stats['total_transitions'])
        else:
            compression_ratio = 0.0
        
        return {
            'total_memory_bytes': self.current_memory,
            'max_memory_bytes': self.max_memory_bytes,
            'snapshot_memory_bytes': snapshot_memory,
            'delta_memory_bytes': delta_memory,
            'current_state_version': self.state_version,
            'num_snapshots': len(self.snapshots),
            'num_deltas': len(self.deltas),
            'compression_ratio': compression_ratio,
            'memory_saved_bytes': self.compression_stats['memory_saved_bytes'],
            'memory_utilization_percent': (self.current_memory / self.max_memory_bytes) * 100
        }
    
    def force_compaction(self) -> Dict[str, int]:
        """Force state compaction to free memory"""
        initial_memory = self.current_memory
        
        # Create new snapshot
        self._create_snapshot()
        
        # Clear old deltas
        old_delta_memory = sum(t.get_memory_size() for t in self.deltas)
        self.deltas.clear()
        self.version_to_delta_idx.clear()
        self.current_memory -= old_delta_memory
        
        # Keep only recent snapshots
        if len(self.snapshots) > 2:
            versions_to_remove = sorted(self.snapshots.keys())[:-2]
            for version in versions_to_remove:
                old_snapshot = self.snapshots.pop(version)
                self.current_memory -= len(old_snapshot)
        
        return {
            'initial_memory_bytes': initial_memory,
            'final_memory_bytes': self.current_memory,
            'freed_memory_bytes': initial_memory - self.current_memory,
            'compression_ratio_percent': int(((initial_memory - self.current_memory) / initial_memory) * 100)
        }
```

### 2.3 Delta-Encoding for Replication

Efficient replication requires minimizing data transfer. Delta encoding reduces bandwidth and memory requirements:

```python
import zlib
import struct
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import time
import hashlib

class DeltaType(Enum):
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    BATCH = 4

@dataclass
class DeltaOperation:
    """Individual delta operation"""
    op_type: DeltaType
    key: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class DeltaEncoder:
    """
    Efficient delta encoding for distributed replication.
    Minimizes memory and network overhead.
    """
    
    def __init__(self, max_delta_size_mb: float = 5.0,
                 compression_enabled: bool = True,
                 batch_threshold: int = 100):
        
        self.max_delta_size_bytes = int(max_delta_size_mb * 1024 * 1024)
        self.compression_enabled = compression_enabled
        self.batch_threshold = batch_threshold
        
        # State tracking
        self.current_state: Dict[str, Any] = {}
        self.state_version = 0
        self.state_checksum = b''
        
        # Delta batching
        self.pending_deltas: List[DeltaOperation] = []
        self.current_batch_size = 0
        
        # Statistics
        self.stats = {
            'deltas_created': 0,
            'bytes_saved': 0,
            'compression_ratio': 0.0
        }
    
    def create_delta(self, new_state: Dict[str, Any]) -> Optional[bytes]:
        """Create compressed delta between current and new state"""
        deltas = []
        
        # Find all changes
        all_keys = set(self.current_state.keys()) | set(new_state.keys())
        
        for key in all_keys:
            old_value = self.current_state.get(key)
            new_value = new_state.get(key)
            
            if old_value is None and new_value is not None:
                # Insert operation
                deltas.append(DeltaOperation(DeltaType.INSERT, key, None, new_value))
                
            elif old_value is not None and new_value is None:
                # Delete operation
                deltas.append(DeltaOperation(DeltaType.DELETE, key, old_value, None))
                
            elif old_value != new_value:
                # Update operation
                deltas.append(DeltaOperation(DeltaType.UPDATE, key, old_value, new_value))
        
        if not deltas:
            return None
        
        # Batch deltas if beneficial
        if len(deltas) > self.batch_threshold:
            batched_delta = self._create_batch_delta(deltas)
            encoded_delta = self._encode_delta(batched_delta)
        else:
            encoded_delta = self._encode_deltas(deltas)
        
        # Update state
        self.current_state = new_state.copy()
        self.state_version += 1
        self.state_checksum = self._calculate_checksum(self.current_state)
        
        return encoded_delta
    
    def _create_batch_delta(self, deltas: List[DeltaOperation]) -> DeltaOperation:
        """Create a single batch operation from multiple deltas"""
        batch_data = {
            'operations': [],
            'total_changes': len(deltas)
        }
        
        for delta in deltas:
            batch_data['operations'].append({
                'type': delta.op_type.value,
                'key': delta.key,
                'old_value': delta.old_value,
                'new_value': delta.new_value,
                'timestamp': delta.timestamp
            })
        
        return DeltaOperation(DeltaType.BATCH, '__batch__', None, batch_data)
    
    def _encode_deltas(self, deltas: List[DeltaOperation]) -> bytes:
        """Encode list of deltas efficiently"""
        encoded_parts = []
        
        # Header: version, delta count, checksum
        header = struct.pack('!III', self.state_version, len(deltas), 
                           int.from_bytes(self.state_checksum[:4], 'big'))
        encoded_parts.append(header)
        
        # Encode each delta
        for delta in deltas:
            encoded_delta = self._encode_delta(delta)
            encoded_parts.append(struct.pack('!H', len(encoded_delta)))  # Length prefix
            encoded_parts.append(encoded_delta)
        
        # Combine all parts
        raw_data = b''.join(encoded_parts)
        
        # Apply compression if beneficial
        if self.compression_enabled:
            compressed = zlib.compress(raw_data, level=6)
            if len(compressed) < len(raw_data):
                self.stats['bytes_saved'] += len(raw_data) - len(compressed)
                return b'\x01' + compressed  # \x01 indicates compressed
        
        return b'\x00' + raw_data  # \x00 indicates uncompressed
    
    def _encode_delta(self, delta: DeltaOperation) -> bytes:
        """Encode single delta operation"""
        parts = []
        
        # Operation type (1 byte)
        parts.append(struct.pack('!B', delta.op_type.value))
        
        # Timestamp (8 bytes)
        parts.append(struct.pack('!d', delta.timestamp))
        
        # Key (length-prefixed string)
        key_bytes = delta.key.encode('utf-8')
        parts.append(struct.pack('!H', len(key_bytes)))
        parts.append(key_bytes)
        
        # Values (using efficient serialization)
        if delta.old_value is not None:
            old_value_bytes = self._serialize_value(delta.old_value)
            parts.append(struct.pack('!I', len(old_value_bytes)))
            parts.append(old_value_bytes)
        else:
            parts.append(struct.pack('!I', 0))
        
        if delta.new_value is not None:
            new_value_bytes = self._serialize_value(delta.new_value)
            parts.append(struct.pack('!I', len(new_value_bytes)))
            parts.append(new_value_bytes)
        else:
            parts.append(struct.pack('!I', 0))
        
        return b''.join(parts)
    
    def _serialize_value(self, value: Any) -> bytes:
        """Efficient value serialization"""
        if isinstance(value, str):
            return b'S' + value.encode('utf-8')
        elif isinstance(value, int):
            return b'I' + struct.pack('!q', value)
        elif isinstance(value, float):
            return b'F' + struct.pack('!d', value)
        elif isinstance(value, bool):
            return b'B' + struct.pack('!?', value)
        elif isinstance(value, (list, dict)):
            import json
            json_str = json.dumps(value, separators=(',', ':'))
            return b'J' + json_str.encode('utf-8')
        else:
            # Fallback to pickle
            import pickle
            return b'P' + pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from bytes"""
        if not data:
            return None
        
        type_marker = data[0:1]
        value_data = data[1:]
        
        if type_marker == b'S':
            return value_data.decode('utf-8')
        elif type_marker == b'I':
            return struct.unpack('!q', value_data)[0]
        elif type_marker == b'F':
            return struct.unpack('!d', value_data)[0]
        elif type_marker == b'B':
            return struct.unpack('!?', value_data)[0]
        elif type_marker == b'J':
            import json
            return json.loads(value_data.decode('utf-8'))
        elif type_marker == b'P':
            import pickle
            return pickle.loads(value_data)
        else:
            raise ValueError(f"Unknown type marker: {type_marker}")
    
    def decode_delta(self, encoded_delta: bytes) -> Tuple[int, List[DeltaOperation]]:
        """Decode delta back to operations"""
        if not encoded_delta:
            return self.state_version, []
        
        # Check compression flag
        is_compressed = encoded_delta[0] == 1
        data = encoded_delta[1:]
        
        if is_compressed:
            data = zlib.decompress(data)
        
        # Parse header
        version, delta_count, checksum_part = struct.unpack('!III', data[:12])
        offset = 12
        
        # Parse deltas
        deltas = []
        for _ in range(delta_count):
            # Read delta length
            delta_length = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            
            # Read delta data
            delta_data = data[offset:offset+delta_length]
            offset += delta_length
            
            delta = self._decode_single_delta(delta_data)
            deltas.append(delta)
        
        return version, deltas
    
    def _decode_single_delta(self, data: bytes) -> DeltaOperation:
        """Decode single delta operation"""
        offset = 0
        
        # Operation type
        op_type = DeltaType(struct.unpack('!B', data[offset:offset+1])[0])
        offset += 1
        
        # Timestamp
        timestamp = struct.unpack('!d', data[offset:offset+8])[0]
        offset += 8
        
        # Key
        key_length = struct.unpack('!H', data[offset:offset+2])[0]
        offset += 2
        key = data[offset:offset+key_length].decode('utf-8')
        offset += key_length
        
        # Old value
        old_value_length = struct.unpack('!I', data[offset:offset+4])[0]
        offset += 4
        old_value = None
        if old_value_length > 0:
            old_value = self._deserialize_value(data[offset:offset+old_value_length])
            offset += old_value_length
        
        # New value
        new_value_length = struct.unpack('!I', data[offset:offset+4])[0]
        offset += 4
        new_value = None
        if new_value_length > 0:
            new_value = self._deserialize_value(data[offset:offset+new_value_length])
        
        return DeltaOperation(op_type, key, old_value, new_value, timestamp)
    
    def apply_delta(self, state: Dict[str, Any], 
                   encoded_delta: bytes) -> Dict[str, Any]:
        """Apply delta to state"""
        version, deltas = self.decode_delta(encoded_delta)
        new_state = state.copy()
        
        for delta in deltas:
            if delta.op_type == DeltaType.BATCH:
                # Handle batch operation
                batch_data = delta.new_value
                for op in batch_data['operations']:
                    self._apply_single_operation(new_state, op)
            else:
                # Handle individual operation
                self._apply_single_delta(new_state, delta)
        
        return new_state
    
    def _apply_single_delta(self, state: Dict[str, Any], delta: DeltaOperation):
        """Apply single delta to state"""
        if delta.op_type == DeltaType.INSERT or delta.op_type == DeltaType.UPDATE:
            state[delta.key] = delta.new_value
        elif delta.op_type == DeltaType.DELETE:
            if delta.key in state:
                del state[delta.key]
    
    def _apply_single_operation(self, state: Dict[str, Any], op: Dict[str, Any]):
        """Apply single operation from batch"""
        op_type = DeltaType(op['type'])
        key = op['key']
        
        if op_type == DeltaType.INSERT or op_type == DeltaType.UPDATE:
            state[key] = op['new_value']
        elif op_type == DeltaType.DELETE:
            if key in state:
                del state[key]
    
    def _calculate_checksum(self, state: Dict[str, Any]) -> bytes:
        """Calculate state checksum for integrity"""
        import json
        state_json = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(state_json.encode()).digest()
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Return compression and efficiency statistics"""
        return {
            'deltas_created': self.stats['deltas_created'],
            'bytes_saved_compression': self.stats['bytes_saved'],
            'current_state_size': len(self.current_state),
            'state_version': self.state_version,
            'pending_deltas': len(self.pending_deltas),
            'compression_enabled': self.compression_enabled
        }
```

This completes the second major section on code examples with memory-bounded algorithms. These implementations demonstrate practical techniques for building space-efficient distributed systems that maintain performance while operating under strict memory constraints. Each algorithm includes comprehensive memory tracking, compression strategies, and adaptive optimization techniques used in production distributed systems.

## 3. Memory Management Techniques (20 minutes)

### 3.1 Garbage Collection in Distributed Systems

Distributed systems face unique garbage collection challenges due to cross-node references and coordination requirements. Here's a comprehensive implementation of distributed garbage collection:

```python
import time
import threading
import weakref
from typing import Dict, Set, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import uuid
import json

class ObjectState(Enum):
    ACTIVE = "active"
    MARKED = "marked"
    SWEEPING = "sweeping"
    COLLECTED = "collected"

@dataclass
class DistributedReference:
    """Reference to an object that may exist on another node"""
    object_id: str
    node_id: str
    ref_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    is_weak: bool = False

@dataclass
class GCObject:
    """Object tracked by distributed garbage collector"""
    object_id: str
    node_id: str
    data: Any
    references_to: Set[str] = field(default_factory=set)
    referenced_by: Set[str] = field(default_factory=set)
    state: ObjectState = ObjectState.ACTIVE
    created_time: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    memory_size: int = 0
    
    def __post_init__(self):
        if self.memory_size == 0:
            self.memory_size = self._estimate_size()
    
    def _estimate_size(self) -> int:
        """Estimate memory footprint of object"""
        try:
            import sys
            return sys.getsizeof(self.data) + 256  # 256 bytes overhead
        except:
            return 1024  # Default estimate

class DistributedGarbageCollector:
    """
    Distributed garbage collector using mark-and-sweep algorithm
    with cross-node coordination and memory pressure handling.
    """
    
    def __init__(self, node_id: str, max_memory_mb: float = 100.0,
                 gc_threshold_percent: float = 80.0,
                 collection_interval_sec: float = 30.0):
        
        self.node_id = node_id
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.gc_threshold_bytes = int(self.max_memory_bytes * (gc_threshold_percent / 100))
        self.collection_interval = collection_interval_sec
        
        # Object tracking
        self.objects: Dict[str, GCObject] = {}
        self.remote_references: Dict[str, DistributedReference] = {}
        self.root_objects: Set[str] = set()
        
        # Memory tracking
        self.current_memory = 0
        self.peak_memory = 0
        self.collections_performed = 0
        
        # Cross-node coordination
        self.peer_nodes: Set[str] = set()
        self.pending_mark_messages: Dict[str, Set[str]] = defaultdict(set)
        self.pending_sweep_confirmations: Dict[str, Set[str]] = defaultdict(set)
        
        # Collection state
        self.collection_in_progress = False
        self.collection_epoch = 0
        self.marked_objects: Set[str] = set()
        
        # Background collection thread
        self.gc_thread = None
        self.stop_gc = threading.Event()
        self.gc_lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'objects_created': 0,
            'objects_collected': 0,
            'memory_reclaimed_bytes': 0,
            'collection_time_ms': 0,
            'cross_node_messages': 0
        }
        
        self._start_background_gc()
    
    def allocate_object(self, data: Any, object_id: Optional[str] = None) -> str:
        """Allocate new object with GC tracking"""
        with self.gc_lock:
            if object_id is None:
                object_id = str(uuid.uuid4())
            
            gc_object = GCObject(
                object_id=object_id,
                node_id=self.node_id,
                data=data
            )
            
            self.objects[object_id] = gc_object
            self.current_memory += gc_object.memory_size
            self.peak_memory = max(self.peak_memory, self.current_memory)
            self.stats['objects_created'] += 1
            
            # Trigger GC if memory pressure
            if self.current_memory > self.gc_threshold_bytes:
                self._schedule_collection()
            
            return object_id
    
    def add_reference(self, from_obj_id: str, to_obj_id: str, 
                     to_node_id: Optional[str] = None) -> bool:
        """Add reference between objects (possibly cross-node)"""
        with self.gc_lock:
            if to_node_id is None or to_node_id == self.node_id:
                # Local reference
                if from_obj_id in self.objects and to_obj_id in self.objects:
                    self.objects[from_obj_id].references_to.add(to_obj_id)
                    self.objects[to_obj_id].referenced_by.add(from_obj_id)
                    return True
            else:
                # Cross-node reference
                if from_obj_id in self.objects:
                    self.objects[from_obj_id].references_to.add(to_obj_id)
                    
                    # Track remote reference
                    ref_key = f"{to_node_id}:{to_obj_id}"
                    if ref_key not in self.remote_references:
                        self.remote_references[ref_key] = DistributedReference(
                            object_id=to_obj_id,
                            node_id=to_node_id
                        )
                    
                    self.remote_references[ref_key].ref_count += 1
                    
                    # Notify remote node
                    self._send_reference_message(to_node_id, 'ADD_REF', {
                        'from_node': self.node_id,
                        'from_object': from_obj_id,
                        'to_object': to_obj_id
                    })
                    return True
            
            return False
    
    def remove_reference(self, from_obj_id: str, to_obj_id: str,
                        to_node_id: Optional[str] = None) -> bool:
        """Remove reference between objects"""
        with self.gc_lock:
            if to_node_id is None or to_node_id == self.node_id:
                # Local reference
                if from_obj_id in self.objects and to_obj_id in self.objects:
                    self.objects[from_obj_id].references_to.discard(to_obj_id)
                    self.objects[to_obj_id].referenced_by.discard(from_obj_id)
                    return True
            else:
                # Cross-node reference
                if from_obj_id in self.objects:
                    self.objects[from_obj_id].references_to.discard(to_obj_id)
                    
                    ref_key = f"{to_node_id}:{to_obj_id}"
                    if ref_key in self.remote_references:
                        self.remote_references[ref_key].ref_count -= 1
                        
                        if self.remote_references[ref_key].ref_count <= 0:
                            del self.remote_references[ref_key]
                        
                        # Notify remote node
                        self._send_reference_message(to_node_id, 'REMOVE_REF', {
                            'from_node': self.node_id,
                            'from_object': from_obj_id,
                            'to_object': to_obj_id
                        })
                        return True
            
            return False
    
    def mark_as_root(self, object_id: str):
        """Mark object as root (never collected)"""
        with self.gc_lock:
            if object_id in self.objects:
                self.root_objects.add(object_id)
    
    def unmark_as_root(self, object_id: str):
        """Remove root marking from object"""
        with self.gc_lock:
            self.root_objects.discard(object_id)
    
    def force_collection(self) -> Dict[str, Any]:
        """Force immediate garbage collection"""
        with self.gc_lock:
            start_time = time.time()
            initial_memory = self.current_memory
            
            collected_objects = self._perform_collection()
            
            collection_time = (time.time() - start_time) * 1000  # milliseconds
            memory_freed = initial_memory - self.current_memory
            
            self.stats['collection_time_ms'] += collection_time
            self.stats['memory_reclaimed_bytes'] += memory_freed
            
            return {
                'objects_collected': len(collected_objects),
                'memory_freed_bytes': memory_freed,
                'collection_time_ms': collection_time,
                'remaining_objects': len(self.objects),
                'current_memory_bytes': self.current_memory
            }
    
    def _perform_collection(self) -> Set[str]:
        """Perform mark-and-sweep collection"""
        if self.collection_in_progress:
            return set()
        
        self.collection_in_progress = True
        self.collection_epoch += 1
        self.marked_objects.clear()
        
        try:
            # Phase 1: Mark reachable objects
            self._mark_phase()
            
            # Phase 2: Coordinate with remote nodes
            self._coordinate_distributed_mark()
            
            # Phase 3: Sweep unreachable objects
            collected = self._sweep_phase()
            
            self.collections_performed += 1
            return collected
            
        finally:
            self.collection_in_progress = False
    
    def _mark_phase(self):
        """Mark all reachable objects starting from roots"""
        # Start from root objects
        work_queue = deque(self.root_objects)
        
        # Add objects with external references
        for obj_id, obj in self.objects.items():
            if obj.referenced_by:  # Has incoming references
                work_queue.append(obj_id)
        
        # Mark reachable objects
        while work_queue:
            obj_id = work_queue.popleft()
            
            if obj_id in self.marked_objects or obj_id not in self.objects:
                continue
            
            self.marked_objects.add(obj_id)
            obj = self.objects[obj_id]
            obj.state = ObjectState.MARKED
            
            # Add referenced objects to queue
            for ref_id in obj.references_to:
                if ref_id not in self.marked_objects:
                    work_queue.append(ref_id)
    
    def _coordinate_distributed_mark(self):
        """Coordinate marking phase across distributed nodes"""
        # Send mark requests for cross-node references
        mark_requests = defaultdict(set)
        
        for obj_id in self.marked_objects:
            obj = self.objects[obj_id]
            for ref_id in obj.references_to:
                # Check if reference is to remote object
                for remote_key, remote_ref in self.remote_references.items():
                    if remote_ref.object_id == ref_id:
                        mark_requests[remote_ref.node_id].add(ref_id)
        
        # Send mark requests
        for node_id, objects_to_mark in mark_requests.items():
            self._send_gc_message(node_id, 'MARK_REQUEST', {
                'epoch': self.collection_epoch,
                'objects': list(objects_to_mark),
                'requesting_node': self.node_id
            })
            self.stats['cross_node_messages'] += 1
    
    def _sweep_phase(self) -> Set[str]:
        """Sweep unmarked objects"""
        collected_objects = set()
        
        # Find objects to collect
        to_collect = []
        for obj_id, obj in self.objects.items():
            if (obj_id not in self.marked_objects and 
                obj_id not in self.root_objects and
                obj.state != ObjectState.COLLECTED):
                
                to_collect.append(obj_id)
        
        # Collect objects
        for obj_id in to_collect:
            if self._collect_object(obj_id):
                collected_objects.add(obj_id)
        
        return collected_objects
    
    def _collect_object(self, obj_id: str) -> bool:
        """Collect individual object"""
        if obj_id not in self.objects:
            return False
        
        obj = self.objects[obj_id]
        obj.state = ObjectState.COLLECTED
        
        # Remove from memory tracking
        self.current_memory -= obj.memory_size
        
        # Clean up references
        for ref_id in obj.references_to:
            if ref_id in self.objects:
                self.objects[ref_id].referenced_by.discard(obj_id)
        
        for ref_id in obj.referenced_by:
            if ref_id in self.objects:
                self.objects[ref_id].references_to.discard(obj_id)
        
        # Remove object
        del self.objects[obj_id]
        self.stats['objects_collected'] += 1
        
        return True
    
    def _start_background_gc(self):
        """Start background garbage collection thread"""
        def gc_worker():
            while not self.stop_gc.wait(self.collection_interval):
                try:
                    if self.current_memory > self.gc_threshold_bytes:
                        self.force_collection()
                except Exception as e:
                    print(f"GC error: {e}")
        
        self.gc_thread = threading.Thread(target=gc_worker, daemon=True)
        self.gc_thread.start()
    
    def _schedule_collection(self):
        """Schedule immediate collection due to memory pressure"""
        if not self.collection_in_progress:
            threading.Thread(target=self.force_collection, daemon=True).start()
    
    def _send_reference_message(self, node_id: str, message_type: str, data: Dict[str, Any]):
        """Send reference management message to remote node"""
        # In production: implement actual network communication
        message = {
            'type': message_type,
            'from_node': self.node_id,
            'data': data,
            'timestamp': time.time()
        }
        # Simulate network call
        pass
    
    def _send_gc_message(self, node_id: str, message_type: str, data: Dict[str, Any]):
        """Send GC coordination message to remote node"""
        # In production: implement actual network communication
        message = {
            'type': message_type,
            'from_node': self.node_id,
            'data': data,
            'timestamp': time.time()
        }
        # Simulate network call
        pass
    
    def handle_remote_message(self, message: Dict[str, Any]):
        """Handle incoming message from remote node"""
        msg_type = message.get('type')
        from_node = message.get('from_node')
        data = message.get('data', {})
        
        if msg_type == 'ADD_REF':
            self._handle_add_reference(from_node, data)
        elif msg_type == 'REMOVE_REF':
            self._handle_remove_reference(from_node, data)
        elif msg_type == 'MARK_REQUEST':
            self._handle_mark_request(from_node, data)
        elif msg_type == 'MARK_RESPONSE':
            self._handle_mark_response(from_node, data)
    
    def _handle_add_reference(self, from_node: str, data: Dict[str, Any]):
        """Handle incoming reference addition"""
        to_object = data.get('to_object')
        if to_object in self.objects:
            # Add external reference tracking
            self.objects[to_object].referenced_by.add(f"{from_node}:external")
    
    def _handle_remove_reference(self, from_node: str, data: Dict[str, Any]):
        """Handle incoming reference removal"""
        to_object = data.get('to_object')
        if to_object in self.objects:
            self.objects[to_object].referenced_by.discard(f"{from_node}:external")
    
    def _handle_mark_request(self, from_node: str, data: Dict[str, Any]):
        """Handle mark request from remote node"""
        epoch = data.get('epoch')
        objects_to_mark = data.get('objects', [])
        
        marked_objects = []
        for obj_id in objects_to_mark:
            if obj_id in self.objects:
                self.objects[obj_id].state = ObjectState.MARKED
                marked_objects.append(obj_id)
        
        # Send response
        self._send_gc_message(from_node, 'MARK_RESPONSE', {
            'epoch': epoch,
            'marked_objects': marked_objects,
            'responding_node': self.node_id
        })
    
    def _handle_mark_response(self, from_node: str, data: Dict[str, Any]):
        """Handle mark response from remote node"""
        epoch = data.get('epoch')
        marked_objects = data.get('marked_objects', [])
        
        if epoch == self.collection_epoch:
            # Update our tracking of remotely marked objects
            for obj_id in marked_objects:
                self.marked_objects.add(f"{from_node}:{obj_id}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Comprehensive memory and GC statistics"""
        with self.gc_lock:
            return {
                'current_memory_bytes': self.current_memory,
                'max_memory_bytes': self.max_memory_bytes,
                'peak_memory_bytes': self.peak_memory,
                'memory_utilization_percent': (self.current_memory / self.max_memory_bytes) * 100,
                'total_objects': len(self.objects),
                'root_objects': len(self.root_objects),
                'remote_references': len(self.remote_references),
                'collections_performed': self.collections_performed,
                'objects_created': self.stats['objects_created'],
                'objects_collected': self.stats['objects_collected'],
                'memory_reclaimed_total_bytes': self.stats['memory_reclaimed_bytes'],
                'average_collection_time_ms': (self.stats['collection_time_ms'] / 
                                              max(self.collections_performed, 1)),
                'cross_node_messages': self.stats['cross_node_messages'],
                'collection_in_progress': self.collection_in_progress
            }
    
    def shutdown(self):
        """Shutdown garbage collector"""
        self.stop_gc.set()
        if self.gc_thread and self.gc_thread.is_alive():
            self.gc_thread.join(timeout=5.0)
```

### 3.2 Memory Pressure Handling

Advanced memory pressure detection and mitigation strategies for distributed systems:

```python
import psutil
import threading
import time
from typing import Dict, List, Callable, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, deque

class PressureLevel(Enum):
    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PressureAction(Enum):
    CACHE_EVICT = "cache_evict"
    BUFFER_FLUSH = "buffer_flush"
    GC_FORCE = "gc_force"
    CONN_LIMIT = "connection_limit"
    REQUEST_THROTTLE = "request_throttle"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class PressureThreshold:
    """Memory pressure threshold configuration"""
    level: PressureLevel
    memory_percent: float
    swap_percent: float = 0.0
    actions: List[PressureAction] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []

@dataclass
class MemoryConsumer:
    """Represents a memory-consuming component"""
    name: str
    current_usage: int
    max_usage: int
    priority: int  # Higher = more important
    eviction_callback: Optional[Callable[[int], int]] = None  # Returns bytes freed
    flush_callback: Optional[Callable[[], int]] = None
    shutdown_callback: Optional[Callable[[], None]] = None

class MemoryPressureManager:
    """
    Advanced memory pressure detection and response system.
    Provides tiered response to memory pressure conditions.
    """
    
    def __init__(self, check_interval_sec: float = 1.0):
        self.check_interval = check_interval_sec
        
        # Pressure configuration
        self.thresholds = [
            PressureThreshold(PressureLevel.LOW, 70.0, 10.0, 
                            [PressureAction.CACHE_EVICT]),
            PressureThreshold(PressureLevel.MEDIUM, 80.0, 25.0,
                            [PressureAction.CACHE_EVICT, PressureAction.BUFFER_FLUSH]),
            PressureThreshold(PressureLevel.HIGH, 90.0, 50.0,
                            [PressureAction.CACHE_EVICT, PressureAction.BUFFER_FLUSH,
                             PressureAction.GC_FORCE, PressureAction.CONN_LIMIT]),
            PressureThreshold(PressureLevel.CRITICAL, 95.0, 75.0,
                            [PressureAction.CACHE_EVICT, PressureAction.BUFFER_FLUSH,
                             PressureAction.GC_FORCE, PressureAction.REQUEST_THROTTLE])
        ]
        
        # Memory consumers registry
        self.consumers: Dict[str, MemoryConsumer] = {}
        
        # Current state
        self.current_level = PressureLevel.NORMAL
        self.previous_level = PressureLevel.NORMAL
        self.pressure_history = deque(maxlen=60)  # Last 60 readings
        
        # Action state
        self.active_mitigations: Set[PressureAction] = set()
        self.action_cooldowns: Dict[PressureAction, float] = {}
        self.cooldown_periods = {
            PressureAction.CACHE_EVICT: 5.0,
            PressureAction.BUFFER_FLUSH: 10.0,
            PressureAction.GC_FORCE: 15.0,
            PressureAction.CONN_LIMIT: 30.0,
            PressureAction.REQUEST_THROTTLE: 60.0
        }
        
        # Statistics
        self.stats = {
            'pressure_events': defaultdict(int),
            'bytes_freed': defaultdict(int),
            'mitigation_count': defaultdict(int),
            'false_alarms': 0,
            'critical_events': 0
        }
        
        # Monitoring thread
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()
        self.pressure_lock = threading.RLock()
        
        # Callbacks for pressure level changes
        self.pressure_callbacks: Dict[PressureLevel, List[Callable]] = defaultdict(list)
        
        self._start_monitoring()
    
    def register_consumer(self, consumer: MemoryConsumer):
        """Register a memory consumer for pressure management"""
        with self.pressure_lock:
            self.consumers[consumer.name] = consumer
    
    def unregister_consumer(self, name: str):
        """Unregister a memory consumer"""
        with self.pressure_lock:
            if name in self.consumers:
                del self.consumers[name]
    
    def register_pressure_callback(self, level: PressureLevel, 
                                 callback: Callable[[PressureLevel], None]):
        """Register callback for pressure level changes"""
        self.pressure_callbacks[level].append(callback)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'memory_percent': memory.percent,
            'memory_available_bytes': memory.available,
            'memory_used_bytes': memory.used,
            'memory_total_bytes': memory.total,
            'swap_percent': swap.percent,
            'swap_used_bytes': swap.used,
            'swap_total_bytes': swap.total,
            'pressure_level': self.current_level.value,
            'active_mitigations': [action.value for action in self.active_mitigations]
        }
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        def monitor_worker():
            while not self.stop_monitoring.wait(self.check_interval):
                try:
                    self._check_pressure()
                except Exception as e:
                    logging.error(f"Memory pressure monitoring error: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitor_thread.start()
    
    def _check_pressure(self):
        """Check current memory pressure and respond"""
        with self.pressure_lock:
            # Get current memory stats
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Record pressure reading
            pressure_reading = {
                'timestamp': time.time(),
                'memory_percent': memory.percent,
                'swap_percent': swap.percent,
                'available_bytes': memory.available
            }
            self.pressure_history.append(pressure_reading)
            
            # Determine current pressure level
            new_level = self._calculate_pressure_level(memory.percent, swap.percent)
            
            # Handle pressure level change
            if new_level != self.current_level:
                self._handle_pressure_change(self.current_level, new_level)
                self.previous_level = self.current_level
                self.current_level = new_level
            
            # Execute mitigation actions if needed
            if self.current_level != PressureLevel.NORMAL:
                self._execute_mitigations(new_level)
    
    def _calculate_pressure_level(self, memory_percent: float, 
                                swap_percent: float) -> PressureLevel:
        """Calculate pressure level based on thresholds"""
        # Check thresholds in reverse order (highest first)
        for threshold in reversed(self.thresholds):
            if (memory_percent >= threshold.memory_percent or 
                swap_percent >= threshold.swap_percent):
                return threshold.level
        
        return PressureLevel.NORMAL
    
    def _handle_pressure_change(self, old_level: PressureLevel, 
                              new_level: PressureLevel):
        """Handle pressure level changes"""
        self.stats['pressure_events'][new_level.value] += 1
        
        # Log significant changes
        if new_level == PressureLevel.CRITICAL:
            self.stats['critical_events'] += 1
            logging.critical(f"Memory pressure reached CRITICAL level")
        elif old_level == PressureLevel.CRITICAL and new_level != PressureLevel.CRITICAL:
            logging.info(f"Memory pressure reduced from CRITICAL to {new_level.value}")
        
        # Call registered callbacks
        for callback in self.pressure_callbacks[new_level]:
            try:
                callback(new_level)
            except Exception as e:
                logging.error(f"Pressure callback error: {e}")
    
    def _execute_mitigations(self, pressure_level: PressureLevel):
        """Execute mitigation actions for current pressure level"""
        threshold = next((t for t in self.thresholds if t.level == pressure_level), None)
        
        if not threshold:
            return
        
        current_time = time.time()
        
        for action in threshold.actions:
            # Check cooldown
            if (action in self.action_cooldowns and 
                current_time - self.action_cooldowns[action] < self.cooldown_periods[action]):
                continue
            
            # Execute action
            bytes_freed = self._execute_action(action, pressure_level)
            
            if bytes_freed > 0:
                self.stats['bytes_freed'][action.value] += bytes_freed
                self.stats['mitigation_count'][action.value] += 1
                self.action_cooldowns[action] = current_time
                self.active_mitigations.add(action)
                
                logging.info(f"Executed {action.value}, freed {bytes_freed} bytes")
            else:
                # Remove from active mitigations if no longer effective
                self.active_mitigations.discard(action)
    
    def _execute_action(self, action: PressureAction, 
                       pressure_level: PressureLevel) -> int:
        """Execute specific mitigation action"""
        bytes_freed = 0
        
        if action == PressureAction.CACHE_EVICT:
            bytes_freed = self._evict_caches(pressure_level)
            
        elif action == PressureAction.BUFFER_FLUSH:
            bytes_freed = self._flush_buffers()
            
        elif action == PressureAction.GC_FORCE:
            bytes_freed = self._force_garbage_collection()
            
        elif action == PressureAction.CONN_LIMIT:
            self._limit_connections(pressure_level)
            
        elif action == PressureAction.REQUEST_THROTTLE:
            self._throttle_requests(pressure_level)
            
        elif action == PressureAction.EMERGENCY_SHUTDOWN:
            self._emergency_shutdown()
        
        return bytes_freed
    
    def _evict_caches(self, pressure_level: PressureLevel) -> int:
        """Evict data from caches based on pressure level"""
        total_freed = 0
        
        # Calculate eviction percentage based on pressure
        eviction_percentages = {
            PressureLevel.LOW: 10,
            PressureLevel.MEDIUM: 25,
            PressureLevel.HIGH: 50,
            PressureLevel.CRITICAL: 75
        }
        
        eviction_percent = eviction_percentages.get(pressure_level, 10)
        
        # Sort consumers by priority (lower priority evicted first)
        sorted_consumers = sorted(self.consumers.values(), 
                                key=lambda x: x.priority)
        
        for consumer in sorted_consumers:
            if consumer.eviction_callback:
                try:
                    target_bytes = (consumer.current_usage * eviction_percent) // 100
                    freed = consumer.eviction_callback(target_bytes)
                    total_freed += freed
                    consumer.current_usage -= freed
                except Exception as e:
                    logging.error(f"Cache eviction error for {consumer.name}: {e}")
        
        return total_freed
    
    def _flush_buffers(self) -> int:
        """Flush buffers to free memory"""
        total_freed = 0
        
        for consumer in self.consumers.values():
            if consumer.flush_callback:
                try:
                    freed = consumer.flush_callback()
                    total_freed += freed
                    consumer.current_usage -= freed
                except Exception as e:
                    logging.error(f"Buffer flush error for {consumer.name}: {e}")
        
        return total_freed
    
    def _force_garbage_collection(self) -> int:
        """Force garbage collection"""
        import gc
        
        # Get memory before GC
        memory_before = psutil.virtual_memory().used
        
        # Force collection
        collected = gc.collect()
        
        # Calculate freed memory (approximate)
        memory_after = psutil.virtual_memory().used
        freed = max(0, memory_before - memory_after)
        
        logging.info(f"Forced GC collected {collected} objects, freed ~{freed} bytes")
        
        return freed
    
    def _limit_connections(self, pressure_level: PressureLevel):
        """Limit new connections based on pressure level"""
        # This would integrate with connection management systems
        connection_limits = {
            PressureLevel.MEDIUM: 1000,
            PressureLevel.HIGH: 500,
            PressureLevel.CRITICAL: 100
        }
        
        limit = connection_limits.get(pressure_level, 1000)
        logging.info(f"Limited connections to {limit} due to memory pressure")
        
        # In production: update connection pool limits, load balancer configs, etc.
    
    def _throttle_requests(self, pressure_level: PressureLevel):
        """Throttle incoming requests"""
        throttle_rates = {
            PressureLevel.HIGH: 0.5,  # 50% of normal rate
            PressureLevel.CRITICAL: 0.1  # 10% of normal rate
        }
        
        rate = throttle_rates.get(pressure_level, 1.0)
        logging.warning(f"Throttling requests to {rate * 100}% due to memory pressure")
        
        # In production: integrate with rate limiting systems
    
    def _emergency_shutdown(self):
        """Emergency shutdown of non-critical components"""
        logging.critical("Executing emergency shutdown due to critical memory pressure")
        
        # Sort consumers by priority (shutdown lowest priority first)
        sorted_consumers = sorted(self.consumers.values(), key=lambda x: x.priority)
        
        for consumer in sorted_consumers:
            if consumer.priority < 5:  # Only shutdown non-critical components
                if consumer.shutdown_callback:
                    try:
                        consumer.shutdown_callback()
                        logging.warning(f"Emergency shutdown of {consumer.name}")
                    except Exception as e:
                        logging.error(f"Emergency shutdown error for {consumer.name}: {e}")
    
    def get_pressure_trends(self) -> Dict[str, Any]:
        """Analyze pressure trends from history"""
        if len(self.pressure_history) < 2:
            return {}
        
        recent_readings = list(self.pressure_history)[-10:]  # Last 10 readings
        
        memory_trend = self._calculate_trend([r['memory_percent'] for r in recent_readings])
        swap_trend = self._calculate_trend([r['swap_percent'] for r in recent_readings])
        
        return {
            'memory_trend': memory_trend,
            'swap_trend': swap_trend,
            'readings_count': len(self.pressure_history),
            'pressure_increasing': memory_trend > 0.5,
            'estimated_critical_time_sec': self._estimate_critical_time() if memory_trend > 0 else None
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_vals = list(range(n))
        
        # Simple linear regression
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _estimate_critical_time(self) -> Optional[float]:
        """Estimate time until critical pressure level"""
        if len(self.pressure_history) < 5:
            return None
        
        recent_readings = list(self.pressure_history)[-10:]
        memory_values = [r['memory_percent'] for r in recent_readings]
        
        trend = self._calculate_trend(memory_values)
        
        if trend <= 0:
            return None  # Not increasing
        
        current_memory = memory_values[-1]
        critical_threshold = 95.0  # Critical level threshold
        
        if current_memory >= critical_threshold:
            return 0.0  # Already critical
        
        # Linear extrapolation
        time_intervals = len(recent_readings) * self.check_interval
        time_to_critical = (critical_threshold - current_memory) / (trend * time_intervals)
        
        return max(0.0, time_to_critical)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics and status"""
        stats = self.get_memory_stats()
        trends = self.get_pressure_trends()
        
        stats.update({
            'pressure_trends': trends,
            'mitigation_stats': dict(self.stats['mitigation_count']),
            'bytes_freed_stats': dict(self.stats['bytes_freed']),
            'pressure_event_counts': dict(self.stats['pressure_events']),
            'critical_events': self.stats['critical_events'],
            'registered_consumers': len(self.consumers),
            'active_mitigations': [action.value for action in self.active_mitigations],
            'monitoring_enabled': not self.stop_monitoring.is_set()
        })
        
        return stats
    
    def shutdown(self):
        """Shutdown pressure manager"""
        self.stop_monitoring.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
```

This completes the comprehensive implementation of memory management techniques for distributed systems. The code demonstrates practical approaches to garbage collection coordination, memory pressure detection, and automated response strategies that are essential for production distributed systems operating under memory constraints.

The implementations provide a solid foundation for building memory-efficient distributed systems that can automatically adapt to varying memory pressures while maintaining performance and reliability guarantees.

---

This concludes the 5000-word Implementation Details section for Episode 22: Space Complexity in Distributed Systems. The content covers practical space optimization techniques with comprehensive working examples, demonstrating real-world approaches to managing memory efficiently in distributed environments.