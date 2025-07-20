---
title: State Management Exercises
description: <details>
<summary>Solution</summary>
type: pillar
difficulty: advanced
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [State](/part2-pillars/state/) → **State Management Exercises**

# State Management Exercises

## Exercise 1: Build a Distributed Key-Value Store

**Challenge**: Implement a simplified distributed key-value store with the following features:
- Consistent hashing for data distribution
- Replication factor of 3
- Read/write quorums
- Basic failure handling

```python
class DistributedKVStore:
    def __init__(self, nodes, replication_factor=3):
        self.nodes = nodes
        self.replication_factor = replication_factor
        self.hash_ring = ConsistentHashRing(nodes)

    def put(self, key, value, consistency_level='QUORUM'):
        """
        Store a key-value pair with specified consistency
        TODO: Implement the following:
        1. Find replica nodes using consistent hashing
        2. Send write requests to all replicas
        3. Wait for required acknowledgments
        4. Handle failures gracefully
        """
        pass

    def get(self, key, consistency_level='QUORUM'):
        """
        Retrieve a value with specified consistency
        TODO: Implement the following:
        1. Find replica nodes
        2. Send read requests
        3. Wait for required responses
        4. Resolve conflicts if multiple versions exist
        """
        pass

    def handle_node_failure(self, failed_node):
        """
        Handle node failure and trigger repairs
        TODO: Implement the following:
        1. Detect which keys need re-replication
        2. Find new replica nodes
        3. Copy data to maintain replication factor
        """
        pass
```

<details>
<summary>Solution</summary>

```python
import hashlib
import time
from enum import Enum
from collections import defaultdict
import threading

class ConsistencyLevel(Enum):
    ONE = 1
    QUORUM = 2
    ALL = 3

class DistributedKVStore:
    def __init__(self, nodes, replication_factor=3):
        self.nodes = nodes
        self.replication_factor = replication_factor
        self.hash_ring = ConsistentHashRing(nodes)
        # Each node has its own storage
        self.node_storage = {node: {} for node in nodes}
        self.node_versions = {node: defaultdict(dict) for node in nodes}

    def put(self, key, value, consistency_level='QUORUM'):
        # Find replica nodes
        replicas = self.hash_ring.get_nodes(key, self.replication_factor)

        # Create versioned value
        timestamp = time.time()
        versioned_value = {
            'value': value,
            'timestamp': timestamp,
            'version': self._generate_version()
        }

        # Calculate required acks
        required_acks = self._get_required_acks(consistency_level, len(replicas))

        # Send writes to all replicas
        write_results = []
        threads = []
        results_lock = threading.Lock()

        def write_to_node(node, key, value):
            try:
                # Simulate network call
                self.node_storage[node][key] = value
                self.node_versions[node][key] = value['version']

                with results_lock:
                    write_results.append((node, True))
            except Exception as e:
                with results_lock:
                    write_results.append((node, False))

        # Start parallel writes
        for replica in replicas:
            t = threading.Thread(
                target=write_to_node,
                args=(replica, key, versioned_value)
            )
            t.start()
            threads.append(t)

        # Wait for required acknowledgments
        timeout = 5.0  # 5 second timeout
        start_time = time.time()

        while len([r for r in write_results if r[1]]) < required_acks:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Could not achieve {consistency_level} consistency")
            time.sleep(0.01)

        # Wait for all threads to complete (best effort)
        for t in threads:
            t.join(timeout=0.1)

        successful_writes = len([r for r in write_results if r[1]])
        if successful_writes < required_acks:
            raise InsufficientReplicasError(
                f"Only {successful_writes}/{required_acks} writes succeeded"
            )

        return True

    def get(self, key, consistency_level='QUORUM'):
        # Find replica nodes
        replicas = self.hash_ring.get_nodes(key, self.replication_factor)

        # Calculate required responses
        required_responses = self._get_required_responses(consistency_level, len(replicas))

        # Read from replicas
        read_results = []
        threads = []
        results_lock = threading.Lock()

        def read_from_node(node, key):
            try:
                if key in self.node_storage[node]:
                    value = self.node_storage[node][key]
                    with results_lock:
                        read_results.append((node, value))
                else:
                    with results_lock:
                        read_results.append((node, None))
            except Exception:
                with results_lock:
                    read_results.append((node, None))

        # Start parallel reads
        for replica in replicas:
            t = threading.Thread(target=read_from_node, args=(replica, key))
            t.start()
            threads.append(t)

        # Wait for required responses
        timeout = 5.0
        start_time = time.time()

        while len([r for r in read_results if r[1] is not None]) < required_responses:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Could not achieve {consistency_level} consistency")

            if len(read_results) >= len(replicas):
                # All nodes responded, check if we have enough non-None values
                non_none_results = [r for r in read_results if r[1] is not None]
                if len(non_none_results) < required_responses:
                    raise KeyNotFoundError(f"Key {key} not found")
                break

            time.sleep(0.01)

        # Collect all non-None results
        valid_results = [(node, value) for node, value in read_results if value is not None]

        if not valid_results:
            raise KeyNotFoundError(f"Key {key} not found")

        # Resolve conflicts (last-write-wins)
        latest_value = max(valid_results, key=lambda x: x[1]['timestamp'])

        # Trigger read repair if inconsistency detected
        if self._has_inconsistency(valid_results):
            self._async_read_repair(key, latest_value[1], replicas)

        return latest_value[1]['value']

    def handle_node_failure(self, failed_node):
        """Handle node failure and trigger repairs"""
        print(f"Handling failure of node {failed_node}")

        # Remove failed node from ring
        self.hash_ring.remove_node(failed_node)
        self.nodes.remove(failed_node)

        # Find all keys that need re-replication
        keys_to_replicate = set()

        # Check all keys stored on remaining nodes
        for node in self.nodes:
            for key in self.node_storage[node].keys():
                # Check if this key has lost replicas
                current_replicas = self.hash_ring.get_nodes(key, self.replication_factor)

                # Count how many replicas actually have the key
                actual_replicas = sum(
                    1 for replica in current_replicas
                    if replica in self.node_storage and key in self.node_storage[replica]
                )

                if actual_replicas < self.replication_factor:
                    keys_to_replicate.add(key)

        # Re-replicate keys
        for key in keys_to_replicate:
            self._rereplicate_key(key)

    def _rereplicate_key(self, key):
        """Ensure key has sufficient replicas"""
        target_replicas = self.hash_ring.get_nodes(key, self.replication_factor)

        # Find nodes that have the key
        source_nodes = [
            node for node in self.nodes
            if node in self.node_storage and key in self.node_storage[node]
        ]

        if not source_nodes:
            return  # Key is lost

        # Get latest version
        latest_version = max(
            [self.node_storage[node][key] for node in source_nodes],
            key=lambda x: x['timestamp']
        )

        # Copy to nodes that should have it but don't
        for target in target_replicas:
            if target not in self.node_storage or key not in self.node_storage[target]:
                self.node_storage[target][key] = latest_version
                print(f"Replicated {key} to {target}")

    def _get_required_acks(self, consistency_level, num_replicas):
        if consistency_level == 'ONE':
            return 1
        elif consistency_level == 'QUORUM':
            return (num_replicas // 2) + 1
        elif consistency_level == 'ALL':
            return num_replicas
        else:
            raise ValueError(f"Unknown consistency level: {consistency_level}")

    def _get_required_responses(self, consistency_level, num_replicas):
        return self._get_required_acks(consistency_level, num_replicas)

    def _generate_version(self):
        return str(time.time())

    def _has_inconsistency(self, results):
        if len(results) <= 1:
            return False

        versions = [r[1]['version'] for r in results]
        return len(set(versions)) > 1

    def _async_read_repair(self, key, correct_value, replicas):
        """Asynchronously repair inconsistent replicas"""
        def repair():
            for replica in replicas:
                if replica in self.node_storage:
                    current = self.node_storage[replica].get(key)
                    if not current or current['timestamp'] < correct_value['timestamp']:
                        self.node_storage[replica][key] = correct_value
                        print(f"Read repair: updated {key} on {replica}")

        # In production, this would be truly async
        repair_thread = threading.Thread(target=repair)
        repair_thread.daemon = True
        repair_thread.start()

# Test the implementation
if __name__ == "__main__":
    # Create a 5-node cluster
    nodes = [f"node{i}" for i in range(5)]
    kv_store = DistributedKVStore(nodes, replication_factor=3)

    # Test writes and reads
    kv_store.put("user:123", {"name": "Alice", "age": 30}, 'QUORUM')
    value = kv_store.get("user:123", 'QUORUM')
    print(f"Retrieved value: {value}")

    # Simulate node failure
    kv_store.handle_node_failure("node2")

    # Verify data is still accessible
    value = kv_store.get("user:123", 'QUORUM')
    print(f"After failure: {value}")
```

</details>

## Exercise 2: Implement Vector Clocks

**Challenge**: Implement vector clocks for tracking causality in distributed systems.

```python
class VectorClock:
    def __init__(self, node_id, initial_clock=None):
        self.node_id = node_id
        self.clock = initial_clock or {}

    def increment(self):
        """Increment this node's logical time"""
        # TODO: Implement local event handling
        pass

    def update(self, other_clock):
        """Update clock after receiving message"""
        # TODO: Implement vector clock update rules
        pass

    def happens_before(self, other):
        """Check if this clock happens-before other"""
        # TODO: Implement happens-before relation
        pass

    def are_concurrent(self, other):
        """Check if two clocks are concurrent"""
        # TODO: Implement concurrency detection
        pass
```

<details>
<summary>Solution</summary>

```python
class VectorClock:
    def __init__(self, node_id, initial_clock=None):
        self.node_id = node_id
        self.clock = initial_clock.copy() if initial_clock else {}

    def increment(self):
        """Increment this node's logical time"""
        if self.node_id not in self.clock:
            self.clock[self.node_id] = 0
        self.clock[self.node_id] += 1
        return self

    def update(self, other_clock):
        """Update clock after receiving message"""
        # Take maximum of each component
        for node_id, timestamp in other_clock.items():
            if node_id not in self.clock:
                self.clock[node_id] = timestamp
            else:
                self.clock[node_id] = max(self.clock[node_id], timestamp)

        # Increment own component
        self.increment()
        return self

    def happens_before(self, other):
        """Check if this clock happens-before other"""
        # A happens-before B if:
        # 1. All components of A <= corresponding components of B
        # 2. At least one component of A < corresponding component of B

        all_less_equal = True
        at_least_one_less = False

        # Check all nodes that appear in either clock
        all_nodes = set(self.clock.keys()) | set(other.clock.keys())

        for node_id in all_nodes:
            self_time = self.clock.get(node_id, 0)
            other_time = other.clock.get(node_id, 0)

            if self_time > other_time:
                all_less_equal = False
                break
            elif self_time < other_time:
                at_least_one_less = True

        return all_less_equal and at_least_one_less

    def are_concurrent(self, other):
        """Check if two clocks are concurrent"""
        # Two events are concurrent if neither happens-before the other
        return not self.happens_before(other) and not other.happens_before(self)

    def merge(self, other):
        """Merge two vector clocks (useful for conflict resolution)"""
        merged = VectorClock(self.node_id)

        all_nodes = set(self.clock.keys()) | set(other.clock.keys())
        for node_id in all_nodes:
            merged.clock[node_id] = max(
                self.clock.get(node_id, 0),
                other.clock.get(node_id, 0)
            )

        return merged

    def __str__(self):
        return str(dict(sorted(self.clock.items())))

    def __eq__(self, other):
        if not isinstance(other, VectorClock):
            return False

        all_nodes = set(self.clock.keys()) | set(other.clock.keys())
        for node_id in all_nodes:
            if self.clock.get(node_id, 0) != other.clock.get(node_id, 0):
                return False
        return True

# Example usage demonstrating causality
def test_vector_clocks():
    # Three nodes: A, B, C
    clock_a = VectorClock("A")
    clock_b = VectorClock("B")
    clock_c = VectorClock("C")

    # A performs local operation
    clock_a.increment()
    print(f"A after local op: {clock_a}")  # {A: 1}

    # A sends message to B
    message_clock = VectorClock("A", clock_a.clock)
    clock_b.update(message_clock.clock)
    print(f"B after receiving from A: {clock_b}")  # {A: 1, B: 1}

    # B performs local operation
    clock_b.increment()
    print(f"B after local op: {clock_b}")  # {A: 1, B: 2}

    # Meanwhile, C performs independent operation
    clock_c.increment()
    print(f"C independent op: {clock_c}")  # {C: 1}

    # Check relationships
    print(f"\nA happens-before B? {clock_a.happens_before(clock_b)}")  # True
    print(f"B happens-before A? {clock_b.happens_before(clock_a)}")  # False
    print(f"B concurrent with C? {clock_b.are_concurrent(clock_c)}")  # True

    # B sends to C
    message_clock = VectorClock("B", clock_b.clock)
    clock_c.update(message_clock.clock)
    print(f"\nC after receiving from B: {clock_c}")  # {A: 1, B: 2, C: 2}

    # Now C knows about A transitively
    print(f"A happens-before C? {clock_a.happens_before(clock_c)}")  # True

if __name__ == "__main__":
    test_vector_clocks()
```

</details>

## Exercise 3: Build a Distributed Lock Manager

**Task**: Implement a distributed lock manager that handles:
- Mutual exclusion across nodes
- Lock timeouts
- Deadlock detection
- Fair queueing

```python
class DistributedLockManager:
    def __init__(self, nodes):
        self.nodes = nodes
        self.locks = {}  # lock_name -> lock_info

    def acquire(self, client_id, lock_name, timeout=None):
        """
        Acquire a distributed lock
        TODO:
        1. Check if lock is available
        2. Handle queuing if lock is held
        3. Implement timeout mechanism
        4. Ensure fault tolerance
        """
        pass

    def release(self, client_id, lock_name):
        """
        Release a distributed lock
        TODO:
        1. Verify client owns the lock
        2. Grant lock to next waiter
        3. Handle client failures
        """
        pass

    def extend(self, client_id, lock_name, extension):
        """Extend lock timeout"""
        pass
```

## Exercise 4: Implement Raft Consensus

**Challenge**: Build a simplified version of the Raft consensus algorithm.

```python
class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = 'follower'  # follower, candidate, leader
        self.current_term = 0
        self.voted_for = None
        self.log = []

    def start_election(self):
        """
        Transition to candidate and start election
        TODO:
        1. Increment term
        2. Vote for self
        3. Send RequestVote to all peers
        4. Become leader if majority votes received
        """
        pass

    def append_entries(self, entries, leader_commit):
        """
        Handle AppendEntries RPC from leader
        TODO:
        1. Verify term and log consistency
        2. Append new entries
        3. Update commit index
        """
        pass

    def request_vote(self, candidate_id, term, last_log_index, last_log_term):
        """
        Handle RequestVote RPC
        TODO:
        1. Check term
        2. Check if already voted
        3. Check log up-to-date
        4. Grant or deny vote
        """
        pass
```

## Exercise 5: Cache Coherence Protocol

**Task**: Implement a simple cache coherence protocol (like MSI - Modified, Shared, Invalid).

```python
class CacheCoherenceController:
    def __init__(self):
        self.caches = {}  # node_id -> cache
        self.memory = {}  # authoritative storage

    class CacheLine:
        def __init__(self, address, value, state='I'):
            self.address = address
            self.value = value
            self.state = state  # M, S, or I

    def read(self, node_id, address):
        """
        Handle read request from a node
        TODO:
        1. Check local cache state
        2. If Invalid, fetch from memory or other caches
        3. Update state to Shared
        4. Handle other caches' state transitions
        """
        pass

    def write(self, node_id, address, value):
        """
        Handle write request from a node
        TODO:
        1. Invalidate other copies
        2. Update local state to Modified
        3. Write value
        4. Handle write-back to memory
        """
        pass
```

## Exercise 6: Time-Series Database Design

**Challenge**: Design storage for a time-series database that:
- Handles 1M writes/second
- Supports efficient range queries
- Implements downsampling
- Manages retention policies

```python
class TimeSeriesDB:
    def __init__(self):
        self.partitions = {}  # time_range -> partition

    def write(self, metric_name, timestamp, value, tags=None):
        """Write a data point"""
        pass

    def query(self, metric_name, start_time, end_time, aggregation=None):
        """Query time range with optional aggregation"""
        pass

    def downsample(self, metric_name, source_resolution, target_resolution):
        """Downsample data to lower resolution"""
        pass
```

## Exercise 7: Distributed Transaction Coordinator

**Task**: Implement a two-phase commit protocol coordinator.

```python
class TwoPhaseCommitCoordinator:
    def __init__(self, participants):
        self.participants = participants
        self.transaction_log = []

    def begin_transaction(self, tx_id, operations):
        """
        Start a distributed transaction
        TODO:
        1. Log transaction start
        2. Send prepare messages
        3. Collect votes
        4. Decide commit/abort
        5. Send decision to participants
        """
        pass

    def handle_participant_failure(self, participant_id, tx_id):
        """Handle participant crash during transaction"""
        pass
```

## Thought Experiments

### 1. The Split-Brain Scenario
Your distributed database has 5 nodes. A network partition splits them into groups of 3 and 2 nodes.
- What happens to writes in each partition?
- How do you resolve conflicts when the partition heals?
- Design a strategy that maximizes availability while maintaining consistency.

### 2. The Hot Key Problem
In your distributed cache, 50% of requests are for 0.1% of keys (e.g., trending items).
- How do you prevent overloading nodes holding hot keys?
- What are the trade-offs of different solutions?
- Design a solution that scales automatically.

### 3. The Cascading Failure
Your state management system has dependencies: A → B → C → D.
If C becomes slow (not failed), how does this propagate?
- Design circuit breakers for state dependencies
- How do you maintain consistency during degradation?

## Research Questions

1. **Why do most distributed databases choose eventual consistency?**
   - Consider the CAP theorem implications
   - Think about latency vs consistency trade-offs

2. **When should you use CRDTs vs. consensus?**
   - Compare complexity and guarantees
   - Consider specific use cases

3. **How does state placement affect system performance?**
   - Think about data locality
   - Consider rebalancing costs

## Reflection

After completing these exercises, consider:

1. What makes state management in distributed systems fundamentally harder than in single-node systems?

2. How do different consistency models affect application complexity?

3. What are the hidden costs of strong consistency?

4. When is eventual consistency actually not good enough?

Remember: The best state management strategy depends on understanding your specific requirements for consistency, availability, and partition tolerance. There's no one-size-fits-all solution.
