---
title: State Management Examples
description: "2007: Dynamo paper
├── Problem: Availability during failures  
└── Solution: Eventual consistency + vector clocks"
type: pillar
difficulty: intermediate
reading_time: 25 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [State](/part2-pillars/state/) → **State Management Examples**


# State Management Examples

## Real-World Case Studies

### 1. Amazon DynamoDB: Eventually Consistent by Design

**Problem**: Build a database that scales to millions of requests per second with predictable performance

**Architecture Evolution**:

```yaml
2004: Simple key-value store
├── Problem: Single master bottleneck
└── Solution: Consistent hashing

2007: Dynamo paper
├── Problem: Availability during failures  
└── Solution: Eventual consistency + vector clocks

2012: DynamoDB service
├── Problem: Vector clocks too complex for users
└── Solution: Last-write-wins + conditional writes

2018: Global tables
├── Problem: Cross-region replication
└── Solution: Conflict-free replicated data types (CRDTs)
```

**Key Design Decisions**:

```python
class DynamoNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.storage = {}
        self.vector_clock = VectorClock()
        
    def put(self, key, value, context=None):
        # Determine coordinate nodes
        preference_list = self.get_preference_list(key, N=3)
        
        # Update vector clock
        if context:
            clock = context.vector_clock.increment(self.node_id)
        else:
            clock = VectorClock().increment(self.node_id)
        
        # Store locally if coordinator
        if self.node_id in preference_list:
            self.storage[key] = {
                'value': value,
                'clock': clock,
                'version': self.generate_version()
            }
        
        # Replicate to N nodes
        write_results = []
        for node in preference_list:
            result = self.replicate_to(node, key, value, clock)
            write_results.append(result)
        
        # Return success if W writes succeed
        successful_writes = sum(1 for r in write_results if r.success)
        return successful_writes >= self.W
    
    def get(self, key):
        # Read from R nodes
        preference_list = self.get_preference_list(key, N=3)
        
        read_results = []
        for node in preference_list:
            result = self.read_from(node, key)
            if result:
                read_results.append(result)
        
        # Need at least R responses
        if len(read_results) < self.R:
            raise InsufficientReplicasException()
        
        # Resolve conflicts
        return self.resolve_conflicts(read_results)
    
    def resolve_conflicts(self, results):
        # Syntactic reconciliation (vector clocks)
        concurrent_versions = []
        
        for r1 in results:
            is_concurrent = True
            for r2 in results:
                if r1 != r2:
                    if r1.clock.happens_before(r2.clock):
                        is_concurrent = False
                        break
            if is_concurrent:
                concurrent_versions.append(r1)
        
        if len(concurrent_versions) == 1:
            return concurrent_versions[0]
        else:
            # Semantic reconciliation (application-specific)
            return self.merge_concurrent_versions(concurrent_versions)
```

**Lessons Learned**:
- Vector clocks are powerful but complex for developers
- Last-write-wins is often good enough with proper conflict detection
- Conditional writes can replace many vector clock use cases
- CRDTs enable truly conflict-free multi-region replication

### 2. Redis Cluster: Sharding with Availability

**Problem**: Scale Redis beyond single-machine memory limits while maintaining sub-millisecond latency

**Architecture**:

```text
Hash Slot Distribution (16,384 slots)
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Master A   │ │  Master B   │ │  Master C   │
│ Slots 0-5460│ │Slots 5461-  │ │Slots 10923- │
│             │ │    10922    │ │   16383     │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
│  Replica A  │ │  Replica B  │ │  Replica C  │
└─────────────┘ └─────────────┘ └─────────────┘
```

**Implementation Details**:

```python
class RedisClusterNode:
    def __init__(self, node_id, slots):
        self.node_id = node_id
        self.slots = slots  # Set of hash slots this node owns
        self.data = {}
        self.replicas = []
        
    def execute_command(self, command, key):
        # Calculate hash slot
        slot = crc16(key) & 16383
        
        # Check if we own this slot
        if slot not in self.slots:
            # Return MOVED redirect
            owner = self.cluster_state.get_slot_owner(slot)
            return MovedError(slot, owner.address)
        
        # Check if slot is migrating
        if slot in self.migrating_slots:
            if key not in self.data:
                # Key might be on target node
                target = self.migrating_slots[slot]
                return AskError(slot, target.address)
        
        # Execute command locally
        return self.execute_local(command, key)
    
    def migrate_slot(self, slot, target_node):
        """Live migration of a hash slot"""
        self.migrating_slots[slot] = target_node
        target_node.importing_slots[slot] = self
        
        # Get all keys in this slot
        keys = [k for k in self.data.keys() 
                if self.hash_slot(k) == slot]
        
        # Migrate keys in batches
        batch_size = 100
        for i in range(0, len(keys), batch_size):
            batch = keys[i:i + batch_size]
            
            # Atomic transfer
            pipeline = target_node.pipeline()
            for key in batch:
                value = self.data[key]
                ttl = self.get_ttl(key)
                
                pipeline.restore(key, value, ttl)
            
            # Execute on target
            pipeline.execute()
            
            # Delete from source
            for key in batch:
                del self.data[key]
        
        # Update cluster state
        self.slots.remove(slot)
        target_node.slots.add(slot)
        del self.migrating_slots[slot]
        del target_node.importing_slots[slot]
```

**Resharding Process**:

```python
class RedisClusterResharding:
    def __init__(self, cluster):
        self.cluster = cluster
        
    def rebalance(self):
        """Rebalance slots across all nodes"""
        nodes = self.cluster.master_nodes
        total_slots = 16384
        slots_per_node = total_slots // len(nodes)
        
        # Calculate moves needed
        moves = []
        for i, node in enumerate(nodes):
            target_slots = set(range(
                i * slots_per_node,
                (i + 1) * slots_per_node if i < len(nodes) - 1 else total_slots
            ))
            
            current_slots = node.slots
            
            # Slots to give away
            give_away = current_slots - target_slots
            for slot in give_away:
                moves.append((node, slot, None))  # Source determined later
            
            # Slots to receive
            receive = target_slots - current_slots
            for slot in receive:
                moves.append((None, slot, node))  # Target determined later
        
        # Match sources with targets
        sources = [m for m in moves if m[2] is None]
        targets = [m for m in moves if m[0] is None]
        
        final_moves = []
        for i in range(min(len(sources), len(targets))):
            source_node, slot, _ = sources[i]
            _, _, target_node = targets[i]
            final_moves.append((source_node, slot, target_node))
        
        # Execute moves
        for source, slot, target in final_moves:
            print(f"Moving slot {slot} from {source.id} to {target.id}")
            source.migrate_slot(slot, target)
```

### 3. Cassandra: Tunable Consistency

**Problem**: Provide tunable consistency levels per operation while maintaining high availability

**Consistency Levels**:

```python
class ConsistencyLevel(Enum):
    ANY = 0      # Write to any node (including hinted handoff)
    ONE = 1      # At least one replica
    TWO = 2      # At least two replicas
    THREE = 3    # At least three replicas
    QUORUM = 4   # Majority of replicas
    ALL = 5      # All replicas
    LOCAL_QUORUM = 6    # Majority in local DC
    EACH_QUORUM = 7     # Majority in each DC
    LOCAL_ONE = 8       # At least one in local DC

class CassandraCoordinator:
    def __init__(self):
        self.replication_factor = 3
        
    def write(self, key, value, consistency_level):
        replicas = self.get_replicas(key)
        required_acks = self.get_required_acks(consistency_level, replicas)
        
        # Send write to all replicas
        write_futures = []
        for replica in replicas:
            future = self.async_write(replica, key, value)
            write_futures.append((replica, future))
        
        # Wait for required acknowledgments
        acks_received = 0
        failed_writes = []
        
        for replica, future in write_futures:
            try:
                result = future.get(timeout=self.write_timeout)
                if result.success:
                    acks_received += 1
                    if acks_received >= required_acks:
                        # Return early if we have enough acks
                        return WriteResult(success=True)
            except TimeoutException:
                failed_writes.append(replica)
        
        # Check if we met consistency requirement
        if acks_received >= required_acks:
            return WriteResult(success=True)
        else:
            # Handle failed writes with hinted handoff
            for replica in failed_writes:
                self.store_hint(replica, key, value)
            
            raise InsufficientReplicasException(
                f"Only {acks_received}/{required_acks} replicas responded"
            )
    
    def read(self, key, consistency_level):
        replicas = self.get_replicas(key)
        required_responses = self.get_required_responses(consistency_level, replicas)
        
        # Determine how many replicas to query
        if consistency_level == ConsistencyLevel.ALL:
            query_replicas = replicas
        else:
            # Query enough to ensure consistency
            query_replicas = replicas[:required_responses]
        
        # Send read requests
        read_futures = []
        for replica in query_replicas:
            future = self.async_read(replica, key)
            read_futures.append((replica, future))
        
        # Collect responses
        responses = []
        for replica, future in read_futures:
            try:
                result = future.get(timeout=self.read_timeout)
                responses.append(result)
            except TimeoutException:
                continue
        
        # Check if we have enough responses
        if len(responses) < required_responses:
            raise InsufficientReplicasException()
        
        # Resolve conflicts and trigger read repair if needed
        winning_value = self.resolve_conflicts(responses)
        
        if self.needs_read_repair(responses):
            self.async_read_repair(key, winning_value, replicas)
        
        return winning_value
    
    def resolve_conflicts(self, responses):
        """Last-write-wins conflict resolution"""
        return max(responses, key=lambda r: r.timestamp).value
```

### 4. Elasticsearch: Distributed Search State

**Problem**: Maintain search indices across distributed nodes with real-time updates

**Architecture**:

```python
class ElasticsearchCluster:
    def __init__(self):
        self.indices = {}
        self.nodes = []
        self.master_node = None
        
    class Index:
        def __init__(self, name, settings):
            self.name = name
            self.settings = settings
            self.shards = []
            self.replicas = settings.get('replicas', 1)
            
        def create_shards(self, num_shards):
            for i in range(num_shards):
                primary = Shard(f"{self.name}_{i}", is_primary=True)
                self.shards.append(primary)
                
                # Create replicas
                for r in range(self.replicas):
                    replica = Shard(f"{self.name}_{i}_r{r}", is_primary=False)
                    replica.primary = primary
                    primary.replicas.append(replica)
    
    class Shard:
        def __init__(self, shard_id, is_primary):
            self.shard_id = shard_id
            self.is_primary = is_primary
            self.translog = TransactionLog()
            self.segments = []
            self.refresh_interval = 1  # seconds
            self.last_refresh = time.time()
            
        def index_document(self, doc_id, document):
            # Write to transaction log first
            self.translog.add({
                'op': 'index',
                'id': doc_id,
                'doc': document,
                'timestamp': time.time()
            })
            
            # Add to in-memory buffer
            self.buffer.add(doc_id, document)
            
            # Refresh if needed
            if time.time() - self.last_refresh > self.refresh_interval:
                self.refresh()
            
            # Replicate if primary
            if self.is_primary:
                for replica in self.replicas:
                    replica.replicate_operation('index', doc_id, document)
        
        def refresh(self):
            """Make buffered documents searchable"""
            if not self.buffer:
                return
            
            # Create new segment from buffer
            segment = self.create_segment(self.buffer)
            self.segments.append(segment)
            
            # Clear buffer
            self.buffer.clear()
            self.last_refresh = time.time()
            
            # Trigger merge if too many segments
            if len(self.segments) > 10:
                self.async_merge_segments()
        
        def search(self, query):
            # Search across all segments
            results = []
            
            for segment in self.segments:
                segment_results = segment.search(query)
                results.extend(segment_results)
            
            # Also search in-memory buffer
            buffer_results = self.buffer.search(query)
            results.extend(buffer_results)
            
            # Merge and rank results
            return self.merge_search_results(results)
```

### 5. Apache Kafka: Distributed Log State

**Problem**: Maintain a distributed, replicated log with strong ordering guarantees

**Core Concepts**:

```python
class KafkaPartition:
    def __init__(self, topic, partition_id):
        self.topic = topic
        self.partition_id = partition_id
        self.log = []
        self.log_start_offset = 0
        self.log_end_offset = 0
        self.leader_epoch = 0
        self.isr = set()  # In-sync replicas
        
    def append(self, messages, producer_id=None):
        """Leader appends messages"""
        if not self.is_leader():
            raise NotLeaderException()
        
        # Assign offsets
        batch = MessageBatch()
        for message in messages:
            offset = self.log_end_offset
            self.log_end_offset += 1
            
            # Add metadata
            record = LogRecord(
                offset=offset,
                timestamp=time.time(),
                key=message.key,
                value=message.value,
                headers=message.headers,
                producer_id=producer_id,
                leader_epoch=self.leader_epoch
            )
            
            batch.add(record)
            self.log.append(record)
        
        # Replicate to followers
        replication_futures = []
        for replica in self.isr:
            if replica != self.node_id:
                future = self.replicate_to_follower(replica, batch)
                replication_futures.append((replica, future))
        
        # Wait for replication based on acks setting
        if self.acks == 'all':
            # Wait for all ISR
            for replica, future in replication_futures:
                try:
                    future.get(timeout=self.replica_timeout)
                except TimeoutException:
                    # Remove from ISR
                    self.isr.remove(replica)
                    self.notify_controller_isr_change()
        
        return batch.base_offset
    
    def fetch(self, offset, max_bytes):
        """Fetch messages starting from offset"""
        if offset < self.log_start_offset:
            raise OffsetOutOfRangeException()
        
        messages = []
        bytes_read = 0
        
        for record in self.log[offset - self.log_start_offset:]:
            if bytes_read + record.size > max_bytes:
                break
            messages.append(record)
            bytes_read += record.size
        
        return FetchResponse(messages, high_water_mark=self.high_water_mark)
    
    def update_high_water_mark(self):
        """Update HWM based on ISR progress"""
        if not self.is_leader():
            return
        
        # Get minimum replicated offset across ISR
        min_offset = self.log_end_offset
        
        for replica in self.isr:
            if replica != self.node_id:
                replica_offset = self.get_replica_offset(replica)
                min_offset = min(min_offset, replica_offset)
        
        self.high_water_mark = min_offset
```

## State Patterns Implementation

### 1. Write-Ahead Log (WAL)

```python
class WriteAheadLog:
    def __init__(self, directory):
        self.directory = directory
        self.current_segment = None
        self.segments = []
        self.last_synced_offset = 0
        
    def append(self, entry):
        # Serialize entry
        serialized = self.serialize(entry)
        
        # Get or create current segment
        if not self.current_segment or self.current_segment.size > self.segment_size:
            self.roll_segment()
        
        # Write to segment
        offset = self.current_segment.append(serialized)
        
        # Sync based on policy
        if self.should_sync():
            self.sync()
        
        return offset
    
    def sync(self):
        """Fsync to ensure durability"""
        self.current_segment.sync()
        self.last_synced_offset = self.current_segment.end_offset
    
    def recover(self):
        """Recover state from WAL after crash"""
        state = {}
        
        # Read all segments in order
        for segment in sorted(self.segments):
            with open(segment.path, 'rb') as f:
                while True:
                    try:
                        entry = self.deserialize(f)
                        # Apply entry to state
                        state = self.apply_entry(state, entry)
                    except EOFError:
                        break
        
        return state
    
    def truncate(self, offset):
        """Truncate log after offset (for removing uncommitted entries)"""
        # Find segment containing offset
        for segment in reversed(self.segments):
            if segment.base_offset <= offset <= segment.end_offset:
                # Truncate this segment
                segment.truncate_after(offset)
                # Remove all later segments
                self.remove_segments_after(segment)
                break
```

### 2. Conflict-Free Replicated Data Types (CRDTs)

```python
class GCounter:
    """Grow-only counter CRDT"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.counts = defaultdict(int)
    
    def increment(self, amount=1):
        self.counts[self.node_id] += amount
    
    def value(self):
        return sum(self.counts.values())
    
    def merge(self, other):
        """Merge with another GCounter"""
        for node_id, count in other.counts.items():
            self.counts[node_id] = max(self.counts[node_id], count)
    
    def to_json(self):
        return dict(self.counts)

class PNCounter:
    """Increment/decrement counter CRDT"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.p = GCounter(node_id)  # Positive counts
        self.n = GCounter(node_id)  # Negative counts
    
    def increment(self, amount=1):
        self.p.increment(amount)
    
    def decrement(self, amount=1):
        self.n.increment(amount)
    
    def value(self):
        return self.p.value() - self.n.value()
    
    def merge(self, other):
        self.p.merge(other.p)
        self.n.merge(other.n)

class LWWRegister:
    """Last-write-wins register CRDT"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.value = None
        self.timestamp = 0
    
    def set(self, value):
        self.timestamp = time.time()
        self.value = value
    
    def get(self):
        return self.value
    
    def merge(self, other):
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
        elif other.timestamp == self.timestamp:
            # Tie-breaker using node_id
            if other.node_id > self.node_id:
                self.value = other.value

class ORSet:
    """Observed-Remove Set CRDT"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.elements = {}  # element -> set of unique tags
        self.tombstones = {}  # element -> set of removed tags
    
    def add(self, element):
        tag = f"{self.node_id}:{time.time()}"
        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add(tag)
    
    def remove(self, element):
        if element in self.elements:
            # Add all current tags to tombstones
            if element not in self.tombstones:
                self.tombstones[element] = set()
            self.tombstones[element].update(self.elements[element])
    
    def contains(self, element):
        if element not in self.elements:
            return False
        
        # Element exists if it has tags not in tombstones
        live_tags = self.elements[element] - self.tombstones.get(element, set())
        return len(live_tags) > 0
    
    def merge(self, other):
        # Merge elements
        for element, tags in other.elements.items():
            if element not in self.elements:
                self.elements[element] = set()
            self.elements[element].update(tags)
        
        # Merge tombstones
        for element, tags in other.tombstones.items():
            if element not in self.tombstones:
                self.tombstones[element] = set()
            self.tombstones[element].update(tags)
```

### 3. Multi-Version Concurrency Control (MVCC)

```python
class MVCCStore:
    def __init__(self):
        self.data = {}  # key -> list of versions
        self.transaction_counter = 0
        self.active_transactions = {}
        
    class Version:
        def __init__(self, value, created_by, deleted_by=None):
            self.value = value
            self.created_by = created_by
            self.deleted_by = deleted_by
    
    def begin_transaction(self):
        tx_id = self.transaction_counter
        self.transaction_counter += 1
        
        self.active_transactions[tx_id] = {
            'start_time': tx_id,
            'read_set': set(),
            'write_set': {}
        }
        
        return tx_id
    
    def read(self, tx_id, key):
        tx = self.active_transactions[tx_id]
        
        # Check write set first
        if key in tx['write_set']:
            return tx['write_set'][key]
        
        # Find visible version
        if key not in self.data:
            return None
        
        visible_version = None
        for version in reversed(self.data[key]):
            # Version is visible if:
            # 1. Created before or by this transaction
            # 2. Not deleted or deleted after this transaction
            if version.created_by <= tx_id:
                if version.deleted_by is None or version.deleted_by > tx_id:
                    visible_version = version
                    break
        
        if visible_version:
            tx['read_set'].add(key)
            return visible_version.value
        
        return None
    
    def write(self, tx_id, key, value):
        tx = self.active_transactions[tx_id]
        tx['write_set'][key] = value
    
    def commit(self, tx_id):
        tx = self.active_transactions[tx_id]
        
        # Validation phase (optimistic concurrency control)
        for key in tx['read_set']:
            if self.has_concurrent_modification(tx_id, key):
                # Abort transaction
                del self.active_transactions[tx_id]
                raise TransactionAbortedException()
        
        # Write phase
        commit_timestamp = self.transaction_counter
        self.transaction_counter += 1
        
        for key, value in tx['write_set'].items():
            if key not in self.data:
                self.data[key] = []
            
            # Mark old versions as deleted
            for version in self.data[key]:
                if version.deleted_by is None:
                    version.deleted_by = commit_timestamp
            
            # Add new version
            new_version = self.Version(value, commit_timestamp)
            self.data[key].append(new_version)
        
        # Cleanup
        del self.active_transactions[tx_id]
        return commit_timestamp
    
    def vacuum(self):
        """Remove old versions no longer visible to any transaction"""
        min_active_tx = min(self.active_transactions.keys()) if self.active_transactions else float('inf')
        
        for key, versions in self.data.items():
            # Keep only versions that might be visible
            self.data[key] = [
                v for v in versions
                if v.deleted_by is None or v.deleted_by >= min_active_tx
            ]
```

## Key Takeaways

1. **State distribution follows data access patterns** - Don't fight your workload

2. **Replication strategies depend on consistency needs** - Choose wisely

3. **Conflict resolution must be deterministic** - Last-write-wins, CRDTs, or vector clocks

4. **State recovery must be fast** - WAL, snapshots, and incremental recovery

5. **Sharding requires careful key selection** - Hot spots will find you

Remember: State is the hardest part of distributed systems. It's where all the trade-offs live.
