---
title: State Management Exercises
description: Advanced exercises for mastering distributed state management patterns
type: pillar
difficulty: advanced
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../../index.md) → [Part II: Pillars](../index.md) → [State](index.md) → **State Management Exercises**

# State Management Exercises

## Exercise 1: Design a Distributed Key-Value Store Architecture

**Challenge**: Create a visual architecture design for a distributed key-value store with the following features:
- Consistent hashing for data distribution
- Replication factor of 3
- Read/write quorums
- Basic failure handling

**Design Tasks**:

1. **Draw a Consistent Hash Ring Diagram**
   ```mermaid
   graph LR
       subgraph "Hash Ring (0-360°)"
           N1[Node 1<br/>45°] --> N2[Node 2<br/>120°]
           N2 --> N3[Node 3<br/>200°]
           N3 --> N4[Node 4<br/>290°]
           N4 --> N1
           
           K1((Key: user:123<br/>Hash: 75°))
           K2((Key: order:456<br/>Hash: 150°))
           K3((Key: product:789<br/>Hash: 250°))
       end
   ```
   - Show how keys map to nodes
   - Illustrate replication to N successor nodes
   - Demonstrate what happens when a node fails

2. **Create a Quorum-Based Read/Write Flow Diagram**
   ```mermaid
   sequenceDiagram
       participant Client
       participant Coordinator
       participant Replica1
       participant Replica2
       participant Replica3
       
       Note over Client,Replica3: Write Operation (Quorum = 2)
       Client->>Coordinator: PUT(key, value)
       Coordinator->>Replica1: Write Request
       Coordinator->>Replica2: Write Request
       Coordinator->>Replica3: Write Request
       Replica1-->>Coordinator: ACK
       Replica2-->>Coordinator: ACK
       Note over Coordinator: Quorum reached (2/3)
       Coordinator-->>Client: Success
       Replica3-->>Coordinator: ACK (late)
   ```

3. **Design a State Machine for Node Failure Handling**
   ```mermaid
   stateDiagram-v2
       [*] --> Healthy
       Healthy --> Suspected: Missed Heartbeat
       Suspected --> Healthy: Heartbeat Received
       Suspected --> Failed: Timeout Exceeded
       Failed --> Recovering: Node Rejoins
       Recovering --> Healthy: Data Synced
       
       Failed --> [*]: Permanent Removal
       
       state Failed {
           [*] --> DetectMissingReplicas
           DetectMissingReplicas --> SelectNewNodes
           SelectNewNodes --> CopyData
           CopyData --> UpdateMetadata
       }
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

## Exercise 2: Design Vector Clock Visualization

**Challenge**: Create visual representations for vector clocks tracking causality in distributed systems.

**Design Tasks**:

1. **Create a Vector Clock Evolution Diagram**
   ```mermaid
   graph TD
       subgraph "Node A Timeline"
           A1["A: {A:1}"]
           A2["A: {A:2, B:1}"]
           A3["A: {A:3, B:1, C:1}"]
       end
       
       subgraph "Node B Timeline"
           B1["B: {B:1}"]
           B2["B: {A:1, B:2}"]
           B3["B: {A:1, B:3, C:1}"]
       end
       
       subgraph "Node C Timeline"
           C1["C: {C:1}"]
           C2["C: {A:2, B:1, C:2}"]
       end
       
       A1 --> A2
       B1 --> B2
       C1 --> C2
       
       A1 -.->|message| B2
       B2 -.->|message| A2
       A2 -.->|message| C2
       C2 -.->|message| A3
       B2 -.->|message| B3
   ```

2. **Design a Causality Relationship Flowchart**
   ```mermaid
   flowchart LR
       subgraph "Happens-Before Detection"
           E1["Event 1<br/>{A:2, B:1}"] 
           E2["Event 2<br/>{A:3, B:2}"]
           
           E1 -->|"A:2 ≤ A:3 ✓<br/>B:1 ≤ B:2 ✓<br/>At least one < ✓"| HB[Happens-Before]
       end
       
       subgraph "Concurrent Detection"
           E3["Event 3<br/>{A:2, B:3}"]
           E4["Event 4<br/>{A:3, B:2}"]
           
           E3 -->|"A:2 < A:3 but<br/>B:3 > B:2"| CC[Concurrent]
           E4 -->|"A:3 > A:2 but<br/>B:2 < B:3"| CC
       end
   ```

3. **Create a Visual Algorithm for Vector Clock Updates**
   ```mermaid
   flowchart TD
       Start([Receive Message with VC])
       Start --> Merge["For each node in clocks"]
       Merge --> Max["Take max(local[node], received[node])"]
       Max --> Inc["Increment own node's counter"]
       Inc --> Done([Updated Vector Clock])
       
       style Start fill:#90EE90
       style Done fill:#87CEEB
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

## Exercise 3: Design a Distributed Lock Manager Architecture

**Task**: Design the architecture for a distributed lock manager that handles:
- Mutual exclusion across nodes
- Lock timeouts
- Deadlock detection
- Fair queueing

**Design Tasks**:

1. **Create a Lock State Machine Diagram**
   ```mermaid
   stateDiagram-v2
       [*] --> Available
       Available --> Locked: Client Acquires
       Locked --> Available: Client Releases
       Locked --> Available: Timeout Expires
       Locked --> Locked: Client Extends
       
       state Locked {
           [*] --> Held
           Held --> Expiring: Near Timeout
           Expiring --> Held: Extended
           Expiring --> [*]: Expired
       }
       
       state Queue {
           [*] --> Waiting
           Waiting --> NextInLine: Previous Released
           NextInLine --> [*]: Granted Lock
       }
   ```

2. **Design a Deadlock Detection Graph**
   ```mermaid
   graph LR
       subgraph "Wait-For Graph"
           C1[Client 1] -->|waits for| L1[Lock A]
           L1 -->|held by| C2[Client 2]
           C2 -->|waits for| L2[Lock B]
           L2 -->|held by| C3[Client 3]
           C3 -->|waits for| L3[Lock C]
           L3 -->|held by| C1
           
           style C1 fill:#ffcccc
           style C2 fill:#ffcccc
           style C3 fill:#ffcccc
       end
       
       subgraph "Cycle Detection"
           Det["Cycle: C1→L1→C2→L2→C3→L3→C1<br/>DEADLOCK DETECTED!"]
       end
   ```

3. **Create a Fair Queueing Flow Diagram**
   ```mermaid
   flowchart TD
       subgraph "Lock Request Processing"
           Req[Lock Request Arrives]
           Req --> Check{Lock Available?}
           Check -->|Yes| Grant[Grant Lock]
           Check -->|No| Queue[Add to Queue]
           
           Queue --> Position[Assign Queue Position]
           Position --> Wait[Wait for Turn]
           
           Release[Lock Released]
           Release --> Next{Queue Empty?}
           Next -->|No| Dequeue[Grant to First in Queue]
           Next -->|Yes| MakeAvail[Mark Lock Available]
       end
       
       style Grant fill:#90EE90
       style MakeAvail fill:#90EE90
   ```

## Exercise 4: Design Raft Consensus Visual Model

**Challenge**: Create visual representations of the Raft consensus algorithm.

**Design Tasks**:

1. **Create a Raft State Transition Diagram**
   ```mermaid
   stateDiagram-v2
       [*] --> Follower: Start
       
       Follower --> Candidate: Election Timeout
       Candidate --> Follower: Discover Higher Term
       Candidate --> Candidate: Split Vote<br/>Start New Election
       Candidate --> Leader: Receive Majority Votes
       Leader --> Follower: Discover Higher Term
       
       state Follower {
           [*] --> Listening
           Listening --> Listening: Receive Heartbeat
           Listening --> [*]: Timeout
       }
       
       state Leader {
           [*] --> SendingHeartbeats
           SendingHeartbeats --> ReplicatingLogs: New Entry
           ReplicatingLogs --> SendingHeartbeats: Replicated
       }
   ```

2. **Design a Leader Election Sequence Diagram**
   ```mermaid
   sequenceDiagram
       participant F1 as Follower 1
       participant C as Candidate
       participant F2 as Follower 2
       participant F3 as Follower 3
       
       Note over F1,F3: Election Timeout Occurs
       C->>C: Increment Term<br/>Vote for Self
       C->>F1: RequestVote(term=2)
       C->>F2: RequestVote(term=2)
       C->>F3: RequestVote(term=2)
       
       F1-->>C: VoteGranted
       F2-->>C: VoteGranted
       Note over C: Majority Achieved (3/4)
       C->>C: Become Leader
       
       C->>F1: AppendEntries(heartbeat)
       C->>F2: AppendEntries(heartbeat)
       C->>F3: AppendEntries(heartbeat)
   ```

3. **Create a Log Replication Flow Diagram**
   ```mermaid
   flowchart LR
       subgraph "Leader Log"
           L1[1: x←3] --> L2[2: y←5] --> L3[3: z←8]
       end
       
       subgraph "Follower 1 Log"
           F1L1[1: x←3] --> F1L2[2: y←5] --> F1L3[3: z←8]
       end
       
       subgraph "Follower 2 Log (Lagging)"
           F2L1[1: x←3] --> F2L2[2: y←5]
       end
       
       Leader -->|AppendEntries<br/>prevIndex=2<br/>entries=[3:z←8]| Follower2
       
       style L3 fill:#90EE90
       style F1L3 fill:#90EE90
   ```

## Exercise 5: Design Cache Coherence Protocol Visualization

**Task**: Create visual models for a cache coherence protocol (MSI - Modified, Shared, Invalid).

**Design Tasks**:

1. **Create MSI State Transition Diagram**
   ```mermaid
   stateDiagram-v2
       [*] --> Invalid
       
       Invalid --> Shared: Read Miss<br/>(Fetch from Memory)
       Invalid --> Modified: Write Miss<br/>(Fetch & Modify)
       
       Shared --> Shared: Read Hit
       Shared --> Modified: Write Hit<br/>(Invalidate Others)
       Shared --> Invalid: Other Core Writes
       
       Modified --> Modified: Read/Write Hit
       Modified --> Shared: Other Core Reads<br/>(Write Back)
       Modified --> Invalid: Other Core Writes<br/>(Write Back)
       
       style Invalid fill:#ffcccc
       style Shared fill:#ffffcc
       style Modified fill:#ccffcc
   ```

2. **Design a Cache Coherence Action Flow**
   ```mermaid
   flowchart TD
       subgraph "Core 1 Writes to Address X"
           C1Write[Core 1: Write X]
           C1Write --> Check1{State of X<br/>in Core 1?}
           Check1 -->|Invalid| FetchMod[Fetch X, Set Modified]
           Check1 -->|Shared| Invalidate[Invalidate Others, Set Modified]
           Check1 -->|Modified| WriteLocal[Write Locally]
       end
       
       subgraph "Broadcast to Other Cores"
           Invalidate --> BC[Send Invalidate X]
           BC --> C2[Core 2: X→Invalid]
           BC --> C3[Core 3: X→Invalid]
       end
       
       style FetchMod fill:#90EE90
       style WriteLocal fill:#90EE90
   ```

3. **Create a Multi-Core Cache State Table Visualization**
   ```mermaid
   graph LR
       subgraph "Time T0: Initial State"
           T0C1[Core 1<br/>X: Invalid]
           T0C2[Core 2<br/>X: Invalid]
           T0C3[Core 3<br/>X: Invalid]
           T0Mem[Memory<br/>X: 100]
       end
       
       subgraph "Time T1: Core 1 Reads X"
           T1C1[Core 1<br/>X: Shared<br/>Val: 100]
           T1C2[Core 2<br/>X: Invalid]
           T1C3[Core 3<br/>X: Invalid]
           T1Mem[Memory<br/>X: 100]
       end
       
       subgraph "Time T2: Core 2 Writes X=200"
           T2C1[Core 1<br/>X: Invalid]
           T2C2[Core 2<br/>X: Modified<br/>Val: 200]
           T2C3[Core 3<br/>X: Invalid]
           T2Mem[Memory<br/>X: 100 (stale)]
       end
       
       T0C1 -.->|Read X| T1C1
       T1C2 -.->|Write X=200| T2C2
       T1C1 -.->|Invalidate| T2C1
   ```

## Exercise 6: Design Time-Series Database Architecture

**Challenge**: Create architectural diagrams for a time-series database that:
- Handles 1M writes/second
- Supports efficient range queries
- Implements downsampling
- Manages retention policies

**Design Tasks**:

1. **Create a Time-Series Storage Layout Diagram**
   ```mermaid
   graph TD
       subgraph "Write Path"
           Writer[Incoming Writes<br/>1M/sec] --> WAL[Write-Ahead Log]
           WAL --> MemTable[In-Memory Table<br/>Recent Data]
           MemTable -->|Flush| SSTable[SSTable Files<br/>Time-Partitioned]
       end
       
       subgraph "Storage Tiers"
           Hot[Hot Storage<br/>1 hour blocks<br/>No compression]
           Warm[Warm Storage<br/>1 day blocks<br/>Compressed]
           Cold[Cold Storage<br/>1 week blocks<br/>Heavy compression]
           
           SSTable --> Hot
           Hot -->|Age > 24h| Warm
           Warm -->|Age > 30d| Cold
           Cold -->|Age > 1y| Delete[Delete]
       end
       
       style Writer fill:#ffcc00
       style Delete fill:#ff6666
   ```

2. **Design a Downsampling Pipeline Flow**
   ```mermaid
   flowchart LR
       subgraph "Raw Data (1s resolution)"
           R1[10:00:01 - 100]
           R2[10:00:02 - 102]
           R3[10:00:03 - 98]
           R4[10:00:04 - 103]
           R5[10:00:05 - 99]
       end
       
       subgraph "1-Minute Aggregation"
           M1["10:00 - Avg: 100.4<br/>Min: 98<br/>Max: 103"]
       end
       
       subgraph "1-Hour Aggregation"
           H1["10:00 - Avg: 101.2<br/>P95: 108<br/>P99: 112"]
       end
       
       R1 & R2 & R3 & R4 & R5 -->|Downsample| M1
       M1 -->|Further Downsample| H1
   ```

3. **Create a Query Execution Plan Visualization**
   ```mermaid
   flowchart TD
       Query["SELECT avg(cpu)<br/>WHERE time > now-24h<br/>GROUP BY 5m"]
       
       Query --> Parser[Parse Query]
       Parser --> Plan{Time Range?}
       
       Plan -->|Last 1h| MemTable[Query MemTable]
       Plan -->|1h-24h| Hot[Query Hot Storage]
       Plan -->|Older| Warm[Query Warm Storage]
       
       MemTable --> Merge[Merge Results]
       Hot --> Merge
       Warm --> Merge
       
       Merge --> Aggregate[Apply 5m Aggregation]
       Aggregate --> Result[Return Results]
       
       style Query fill:#e6f3ff
       style Result fill:#90EE90
   ```

## Exercise 7: Design Distributed Transaction Coordinator

**Task**: Create visual models for a two-phase commit protocol coordinator.

**Design Tasks**:

1. **Create a Two-Phase Commit State Machine**
   ```mermaid
   stateDiagram-v2
       [*] --> Init: Begin Transaction
       
       Init --> Preparing: Send Prepare
       Preparing --> Prepared: All Vote Yes
       Preparing --> Aborted: Any Vote No
       Preparing --> Aborted: Timeout
       
       Prepared --> Committing: Send Commit
       Committing --> Committed: All ACK
       Committing --> Uncertain: Some ACK Missing
       
       Aborted --> [*]: Send Abort
       Committed --> [*]: Success
       
       state Uncertain {
           [*] --> Retrying
           Retrying --> Retrying: Retry Commit
           Retrying --> [*]: All ACK
       }
   ```

2. **Design a 2PC Sequence Diagram**
   ```mermaid
   sequenceDiagram
       participant TC as Transaction<br/>Coordinator
       participant P1 as Participant 1
       participant P2 as Participant 2
       participant P3 as Participant 3
       
       Note over TC,P3: Phase 1: Prepare
       TC->>TC: Log START
       TC->>P1: PREPARE
       TC->>P2: PREPARE
       TC->>P3: PREPARE
       
       P1->>P1: Log READY
       P1-->>TC: VOTE YES
       P2->>P2: Log READY
       P2-->>TC: VOTE YES
       P3->>P3: Log READY
       P3-->>TC: VOTE YES
       
       Note over TC,P3: Phase 2: Commit
       TC->>TC: Log COMMIT
       TC->>P1: COMMIT
       TC->>P2: COMMIT
       TC->>P3: COMMIT
       
       P1->>P1: Log COMMIT
       P1-->>TC: ACK
       P2->>P2: Log COMMIT
       P2-->>TC: ACK
       P3->>P3: Log COMMIT
       P3-->>TC: ACK
       
       TC->>TC: Log COMPLETE
   ```

3. **Create a Failure Recovery Flow Diagram**
   ```mermaid
   flowchart TD
       subgraph "Coordinator Recovery"
           CStart[Coordinator Restarts]
           CStart --> CCheck{Check Last Log}
           CCheck -->|START only| CAbort[Send ABORT to all]
           CCheck -->|COMMIT logged| CRetry[Retry COMMIT to all]
           CCheck -->|COMPLETE logged| CDone[Transaction Done]
       end
       
       subgraph "Participant Recovery"
           PStart[Participant Restarts]
           PStart --> PCheck{Check Last Log}
           PCheck -->|No READY| PWait[Wait for Coordinator]
           PCheck -->|READY logged| PAsk[Ask Coordinator Status]
           PCheck -->|COMMIT logged| PExec[Execute Commit]
       end
       
       style CDone fill:#90EE90
       style PExec fill:#90EE90
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
