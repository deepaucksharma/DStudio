# State Distribution Exercises

!!! info "Prerequisites"
    - Completed [State Distribution Concepts](index.md)
    - Reviewed [State Distribution Examples](examples.md)
    - Understanding of CAP theorem

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Pillars Overview](../index.md) |
    [→ Next: Distribution of Truth](../pillar-3-truth/index.md)

## Exercise 1: Build a Consistent Hashing System

### Objective
Implement a production-ready consistent hashing system with virtual nodes.

### Requirements
- Support adding/removing nodes without massive redistribution
- Handle node weights (some nodes have more capacity)
- Provide replication (each key on N nodes)
- Track data movement metrics

### Starter Implementation
```python
import hashlib
import bisect
from collections import defaultdict

class ConsistentHashRing:
    def __init__(self, virtual_nodes_per_node=150, replication_factor=3):
        self.vnodes_per_node = virtual_nodes_per_node
        self.replication_factor = replication_factor
        self.ring = {}  # hash -> physical_node
        self.sorted_hashes = []
        self.nodes = {}  # node -> weight
        
    def _hash(self, key):
        """Generate hash for a key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node, weight=1.0):
        """Add node with weight (weight affects vnode count)"""
        if node in self.nodes:
            raise ValueError(f"Node {node} already exists")
            
        self.nodes[node] = weight
        vnodes = int(self.vnodes_per_node * weight)
        
        # Add virtual nodes
        for i in range(vnodes):
            vnode_key = f"{node}:vnode{i}"
            hash_val = self._hash(vnode_key)
            self.ring[hash_val] = node
            bisect.insort(self.sorted_hashes, hash_val)
    
    def remove_node(self, node):
        """Remove node and return affected keys"""
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found")
            
        # TODO: Implement node removal
        # Track which keys need to move
        pass
    
    def get_nodes(self, key):
        """Get N nodes for a key (for replication)"""
        if not self.ring:
            return []
            
        hash_val = self._hash(key)
        
        # TODO: Find N distinct physical nodes
        # Starting from the key's position on the ring
        pass
    
    def get_key_distribution(self, num_keys=10000):
        """Analyze key distribution across nodes"""
        distribution = defaultdict(int)
        
        for i in range(num_keys):
            key = f"key_{i}"
            nodes = self.get_nodes(key)
            for node in nodes:
                distribution[node] += 1
                
        return dict(distribution)
    
    def rebalance_analysis(self, node_to_add=None, node_to_remove=None):
        """Analyze impact of adding/removing a node"""
        # TODO: Calculate how many keys would move
        # Useful for capacity planning
        pass

# Test your implementation
ring = ConsistentHashRing(replication_factor=3)
ring.add_node("server1", weight=1.0)
ring.add_node("server2", weight=2.0)  # 2x capacity
ring.add_node("server3", weight=0.5)  # Half capacity

# Check distribution
distribution = ring.get_key_distribution()
print("Key distribution:", distribution)

# Test replication
key = "user:12345"
replicas = ring.get_nodes(key)
print(f"Key '{key}' replicated to: {replicas}")
```

### Expected Behavior
- Keys should distribute proportionally to weights
- Each key should have exactly N replicas
- Adding a node should only move ~1/N keys

## Exercise 2: Implement a Write-Ahead Log (WAL)

### Objective
Build a WAL for crash recovery in a distributed database.

### Requirements
- Durability guarantees before acknowledgment
- Support for checkpointing
- Replay capability after crash
- Bounded growth with cleanup

### Implementation Framework
```python
import os
import json
import time
from threading import Lock
from dataclasses import dataclass
from typing import Optional

@dataclass
class LogEntry:
    lsn: int  # Log Sequence Number
    timestamp: float
    operation: str
    data: dict
    
class WriteAheadLog:
    def __init__(self, log_dir, checkpoint_interval=1000):
        self.log_dir = log_dir
        self.checkpoint_interval = checkpoint_interval
        self.current_lsn = 0
        self.last_checkpoint_lsn = 0
        self.lock = Lock()
        self.current_log_file = None
        self.memory_buffer = []
        
        # Recovery on startup
        self.recover()
        
    def append(self, operation, data):
        """Append operation to WAL"""
        with self.lock:
            self.current_lsn += 1
            entry = LogEntry(
                lsn=self.current_lsn,
                timestamp=time.time(),
                operation=operation,
                data=data
            )
            
            # Write to disk (ensure durability)
            self._write_to_disk(entry)
            
            # Add to memory buffer
            self.memory_buffer.append(entry)
            
            # Check if checkpoint needed
            if self.current_lsn - self.last_checkpoint_lsn >= self.checkpoint_interval:
                self.checkpoint()
                
            return entry.lsn
    
    def _write_to_disk(self, entry):
        """Ensure entry is persisted"""
        # TODO: Implement actual disk writing
        # Consider fsync for durability
        pass
    
    def checkpoint(self):
        """Create a checkpoint for faster recovery"""
        # TODO: Implement checkpointing
        # 1. Snapshot current state
        # 2. Write checkpoint marker
        # 3. Clean old log files
        pass
    
    def recover(self):
        """Recover state from WAL after crash"""
        # TODO: Implement recovery
        # 1. Find last checkpoint
        # 2. Replay log from checkpoint
        # 3. Rebuild in-memory state
        pass
    
    def replay_from(self, start_lsn: int):
        """Replay operations from given LSN"""
        # TODO: Implement replay logic
        pass
    
    def truncate_before(self, lsn: int):
        """Remove old log entries before LSN"""
        # TODO: Safe cleanup of old logs
        pass

# Test crash recovery
wal = WriteAheadLog("/tmp/wal")

# Simulate operations
wal.append("INSERT", {"key": "user:1", "value": {"name": "Alice"}})
wal.append("UPDATE", {"key": "user:1", "value": {"name": "Alice Smith"}})
wal.append("DELETE", {"key": "user:2"})

# Simulate crash and recovery
del wal  # "Crash"
wal2 = WriteAheadLog("/tmp/wal")  # Recovery
```

## Exercise 3: Build a Quorum-Based Replicated Store

### Objective
Implement a distributed key-value store with configurable consistency.

### Requirements
- Support W + R > N quorum
- Handle node failures gracefully
- Provide eventual consistency with anti-entropy
- Vector clocks for conflict detection

### Complete Implementation
```python
import asyncio
import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

class ConsistencyLevel(Enum):
    ONE = 1
    QUORUM = 2
    ALL = 3

@dataclass
class VersionedValue:
    value: any
    vector_clock: Dict[str, int]
    timestamp: float

class QuorumStore:
    def __init__(self, node_id: str, all_nodes: List[str], n_replicas: int = 3):
        self.node_id = node_id
        self.all_nodes = all_nodes
        self.n_replicas = n_replicas
        self.local_store: Dict[str, VersionedValue] = {}
        self.vector_clock = {node: 0 for node in all_nodes}
        
    def get_replicas(self, key: str) -> List[str]:
        """Determine which nodes should store this key"""
        # Simple hash-based selection
        hash_val = hash(key)
        start_idx = hash_val % len(self.all_nodes)
        
        replicas = []
        for i in range(self.n_replicas):
            idx = (start_idx + i) % len(self.all_nodes)
            replicas.append(self.all_nodes[idx])
            
        return replicas
    
    async def put(self, key: str, value: any, consistency: ConsistencyLevel):
        """Write with specified consistency level"""
        replicas = self.get_replicas(key)
        required_acks = self._get_required_acks(consistency, len(replicas))
        
        # Increment vector clock
        self.vector_clock[self.node_id] += 1
        
        versioned_value = VersionedValue(
            value=value,
            vector_clock=self.vector_clock.copy(),
            timestamp=time.time()
        )
        
        # Write locally if we're a replica
        if self.node_id in replicas:
            self.local_store[key] = versioned_value
            acks = 1
        else:
            acks = 0
        
        # Write to other replicas
        write_tasks = []
        for replica in replicas:
            if replica != self.node_id:
                task = self._write_to_replica(replica, key, versioned_value)
                write_tasks.append(task)
        
        # Wait for required acknowledgments
        if write_tasks:
            done, pending = await asyncio.wait(
                write_tasks,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=5.0
            )
            acks += len(done)
        
        if acks < required_acks:
            raise Exception(f"Insufficient replicas: {acks}/{required_acks}")
            
        return True
    
    async def get(self, key: str, consistency: ConsistencyLevel):
        """Read with specified consistency level"""
        replicas = self.get_replicas(key)
        required_reads = self._get_required_reads(consistency, len(replicas))
        
        # Read from local if we have it
        values = []
        if self.node_id in replicas and key in self.local_store:
            values.append(self.local_store[key])
            
        # Read from other replicas
        read_tasks = []
        for replica in replicas:
            if replica != self.node_id:
                task = self._read_from_replica(replica, key)
                read_tasks.append(task)
        
        # Collect required responses
        if read_tasks:
            done, pending = await asyncio.wait(
                read_tasks,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=5.0
            )
            for task in done:
                result = await task
                if result:
                    values.append(result)
        
        if len(values) < required_reads:
            raise Exception(f"Insufficient replicas: {len(values)}/{required_reads}")
        
        # Resolve conflicts
        return self._resolve_conflicts(values)
    
    def _resolve_conflicts(self, values: List[VersionedValue]):
        """Resolve conflicts using vector clocks"""
        if not values:
            return None
            
        if len(values) == 1:
            return values[0].value
            
        # TODO: Implement vector clock comparison
        # For now, last-write-wins
        return max(values, key=lambda v: v.timestamp).value
    
    def _get_required_acks(self, consistency: ConsistencyLevel, n_replicas: int):
        if consistency == ConsistencyLevel.ONE:
            return 1
        elif consistency == ConsistencyLevel.QUORUM:
            return (n_replicas // 2) + 1
        else:  # ALL
            return n_replicas
    
    def _get_required_reads(self, consistency: ConsistencyLevel, n_replicas: int):
        # Same as writes for now
        return self._get_required_acks(consistency, n_replicas)
    
    async def _write_to_replica(self, replica: str, key: str, value: VersionedValue):
        """Simulate network write to replica"""
        # TODO: Implement actual network call
        await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulate latency
        return True
    
    async def _read_from_replica(self, replica: str, key: str):
        """Simulate network read from replica"""
        # TODO: Implement actual network call
        await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulate latency
        return None

# Test quorum operations
async def test_quorum():
    nodes = ['node1', 'node2', 'node3', 'node4', 'node5']
    store = QuorumStore('node1', nodes, n_replicas=3)
    
    # Write with quorum
    await store.put('user:123', {'name': 'Alice'}, ConsistencyLevel.QUORUM)
    
    # Read with different consistency levels
    value_one = await store.get('user:123', ConsistencyLevel.ONE)
    value_quorum = await store.get('user:123', ConsistencyLevel.QUORUM)
    value_all = await store.get('user:123', ConsistencyLevel.ALL)
```

## Exercise 4: Implement Saga Pattern

### Objective
Build a distributed transaction coordinator using the Saga pattern.

### Requirements
- Support multi-step transactions across services
- Implement compensation for rollback
- Handle partial failures gracefully
- Provide observability

### Saga Coordinator
```python
class SagaCoordinator:
    def __init__(self):
        self.saga_definitions = {}
        self.running_sagas = {}
        
    def define_saga(self, saga_type, steps):
        """Define a saga with its steps and compensations"""
        self.saga_definitions[saga_type] = steps
        
    async def start_saga(self, saga_type, initial_data):
        """Start a new saga instance"""
        saga_id = generate_unique_id()
        saga = {
            'id': saga_id,
            'type': saga_type,
            'state': 'running',
            'completed_steps': [],
            'data': initial_data,
            'started_at': time.time()
        }
        
        self.running_sagas[saga_id] = saga
        
        try:
            # Execute steps in order
            steps = self.saga_definitions[saga_type]
            for step in steps:
                await self._execute_step(saga, step)
                
            saga['state'] = 'completed'
            return saga_id
            
        except Exception as e:
            # Compensate in reverse order
            await self._compensate_saga(saga)
            saga['state'] = 'compensated'
            raise
    
    async def _execute_step(self, saga, step):
        """Execute a single saga step"""
        # TODO: Implement step execution
        # 1. Call the service
        # 2. Record success
        # 3. Update saga state
        pass
    
    async def _compensate_saga(self, saga):
        """Run compensation for all completed steps"""
        # TODO: Implement compensation
        # Run in reverse order
        pass

# Define an order processing saga
coordinator = SagaCoordinator()

order_saga_steps = [
    {
        'name': 'reserve_inventory',
        'service': 'inventory',
        'action': 'reserve',
        'compensation': 'release'
    },
    {
        'name': 'charge_payment',
        'service': 'payment',
        'action': 'charge',
        'compensation': 'refund'
    },
    {
        'name': 'create_shipment',
        'service': 'shipping',
        'action': 'create',
        'compensation': 'cancel'
    }
]

coordinator.define_saga('process_order', order_saga_steps)
```

## Exercise 5: Build a Multi-Version Concurrency Control (MVCC) System

### Objective
Implement MVCC for snapshot isolation in a distributed database.

### Requirements
- Multiple versions of each key
- Point-in-time queries
- Garbage collection of old versions
- Conflict detection for writes

### MVCC Implementation
```python
class MVCCStore:
    def __init__(self):
        self.data = defaultdict(list)  # key -> [(version, value, deleted)]
        self.transaction_counter = 0
        self.active_transactions = set()
        self.lock = Lock()
        
    def begin_transaction(self):
        """Start a new transaction"""
        with self.lock:
            tx_id = self.transaction_counter
            self.transaction_counter += 1
            self.active_transactions.add(tx_id)
            return Transaction(self, tx_id)
    
    def get(self, key, tx_id):
        """Read the version visible to transaction"""
        versions = self.data.get(key, [])
        
        # Find the latest version visible to this transaction
        for version, value, deleted in reversed(versions):
            if version < tx_id:
                if deleted:
                    return None
                return value
                
        return None
    
    def put(self, key, value, tx_id):
        """Write a new version"""
        with self.lock:
            # Check for write-write conflicts
            if self._has_conflict(key, tx_id):
                raise Exception("Write conflict detected")
                
            self.data[key].append((tx_id, value, False))
    
    def delete(self, key, tx_id):
        """Mark key as deleted"""
        with self.lock:
            if self._has_conflict(key, tx_id):
                raise Exception("Write conflict detected")
                
            self.data[key].append((tx_id, None, True))
    
    def _has_conflict(self, key, tx_id):
        """Check if another transaction modified this key"""
        versions = self.data.get(key, [])
        for version, _, _ in versions:
            if version >= tx_id:
                return True
        return False
    
    def garbage_collect(self):
        """Remove old versions no longer needed"""
        with self.lock:
            min_active_tx = min(self.active_transactions) if self.active_transactions else self.transaction_counter
            
            for key in list(self.data.keys()):
                versions = self.data[key]
                # Keep only versions that might be needed
                kept_versions = []
                
                for i, (version, value, deleted) in enumerate(versions):
                    # Keep if it's the latest or might be seen by active tx
                    if version >= min_active_tx or i == len(versions) - 1:
                        kept_versions.append((version, value, deleted))
                
                if kept_versions:
                    self.data[key] = kept_versions
                else:
                    del self.data[key]

class Transaction:
    def __init__(self, store, tx_id):
        self.store = store
        self.tx_id = tx_id
        self.writes = []
        self.committed = False
        
    def get(self, key):
        # Check local writes first
        for write_key, write_value, is_delete in reversed(self.writes):
            if write_key == key:
                return None if is_delete else write_value
                
        # Then check store
        return self.store.get(key, self.tx_id)
    
    def put(self, key, value):
        self.writes.append((key, value, False))
    
    def delete(self, key):
        self.writes.append((key, None, True))
    
    def commit(self):
        """Commit all writes atomically"""
        # TODO: Implement 2-phase commit for distributed version
        for key, value, is_delete in self.writes:
            if is_delete:
                self.store.delete(key, self.tx_id)
            else:
                self.store.put(key, value, self.tx_id)
                
        self.store.active_transactions.remove(self.tx_id)
        self.committed = True

# Test MVCC
store = MVCCStore()

# Transaction 1
tx1 = store.begin_transaction()
tx1.put("balance", 100)
tx1.commit()

# Transaction 2 (concurrent)
tx2 = store.begin_transaction()
tx3 = store.begin_transaction()

# Both read the same value
print(tx2.get("balance"))  # 100
print(tx3.get("balance"))  # 100

# Both try to update
tx2.put("balance", 150)
tx3.put("balance", 200)

# One will succeed, one will fail
tx2.commit()  # Success
tx3.commit()  # Conflict!
```

## Project: Design a Geo-Distributed Database

### Objective
Design and implement core components of a globally distributed database.

### Requirements
1. **Multi-region replication** with configurable consistency
2. **Conflict resolution** for concurrent updates
3. **Geo-partitioning** for data locality
4. **Cross-region transactions** using 2PC or Saga
5. **Read replicas** with bounded staleness

### System Architecture
```python
class GeoDistributedDB:
    def __init__(self, regions):
        self.regions = regions
        self.local_region = detect_local_region()
        self.replication_topology = self.build_topology()
        
    def put(self, key, value, options=None):
        """Write with geo-replication"""
        # Determine home region for key
        home_region = self.get_home_region(key)
        
        if options and options.get('consistency') == 'strong':
            # Synchronous replication
            return self.sync_replicate(key, value, home_region)
        else:
            # Async replication
            return self.async_replicate(key, value, home_region)
    
    def get(self, key, options=None):
        """Read with consistency guarantees"""
        if options and options.get('read_region') == 'local':
            # Read from local replica
            return self.local_read(key)
        else:
            # Read from home region
            home_region = self.get_home_region(key)
            return self.remote_read(key, home_region)
    
    def start_transaction(self):
        """Begin a geo-distributed transaction"""
        return GeoTransaction(self)

# Implement the components
# - Region detection and routing
# - Replication protocols
# - Conflict resolution strategies
# - Transaction coordination
```

### Evaluation Criteria
- Correctness under network partitions
- Performance (latency and throughput)
- Consistency guarantees met
- Failure recovery capabilities
- Operational complexity

## Reflection Questions

After completing exercises:

1. **CAP Trade-offs**: Where did you choose consistency vs availability?

2. **Sharding Strategy**: How did you handle hot shards and rebalancing?

3. **Conflict Resolution**: What strategy works best for your use case?

4. **Operational Complexity**: How would you monitor and debug this system?

5. **Cost Implications**: What are the resource requirements at scale?

## Navigation

!!! tip "Continue Learning"
    
    **Next Pillar**: [Distribution of Truth](../pillar-3-truth/index.md) →
    
    **Related Topics**: [Consensus](../pillar-3-truth/index.md) | [Coordination](../../part1-axioms/axiom-5-coordination/index.md)
    
    **Back to**: [Pillars Overview](../index.md)