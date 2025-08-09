# Episode 24: Impossibility Results - Implementation Details

## Episode Metadata
- **Duration**: 60 minutes (Implementation Section)
- **Pillar**: Core Principles - Impossibility Results
- **Prerequisites**: Understanding of FLP impossibility, CAP theorem, Byzantine agreement
- **Learning Objectives**: 
  - [ ] Implement practical workarounds for theoretical impossibilities
  - [ ] Build production-ready systems that acknowledge fundamental limits
  - [ ] Create failure detectors and randomized consensus algorithms
  - [ ] Apply CAP theorem trade-offs in real distributed systems

## Part 2: Implementation Details (60 minutes)

### Working Around Impossibilities (15 minutes)

The beauty of impossibility results isn't that they stop us from building systems—they guide us toward practical solutions that acknowledge fundamental limits. Let's implement the core workarounds that production systems use.

#### Randomized Consensus Implementations

The FLP impossibility shows deterministic consensus is impossible in asynchronous systems with failures. Randomized algorithms provide a way forward with probabilistic guarantees.

```python
import random
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class ConsensusPhase(Enum):
    PROPOSE = "propose"
    VOTE = "vote"
    DECIDE = "decide"

@dataclass
class ConsensusMessage:
    sender_id: int
    phase: ConsensusPhase
    round_num: int
    value: Optional[int]
    coin_flip: Optional[bool] = None

class BenOrRandomizedConsensus:
    """
    Ben-Or's randomized consensus algorithm (1983)
    
    Key insight: Use shared random coins to break symmetry when needed.
    Guarantees:
    - Agreement: All correct processes decide the same value
    - Validity: If all processes start with v, then v is the only decision
    - Termination: Termination in finite expected time with probability 1
    """
    
    def __init__(self, process_id: int, n_processes: int, initial_value: int):
        self.process_id = process_id
        self.n_processes = n_processes
        self.initial_value = initial_value
        self.current_value = initial_value
        self.decided_value = None
        self.round_num = 1
        self.phase = ConsensusPhase.PROPOSE
        
        # Message buffers for each round and phase
        self.messages: Dict[int, Dict[ConsensusPhase, List[ConsensusMessage]]] = {}
        self.decided = False
        
        # Fault tolerance: can handle up to (n-1)/2 crash failures
        self.failure_threshold = (n_processes - 1) // 2
    
    def start_round(self) -> List[ConsensusMessage]:
        """Start a new round with proposal phase"""
        if self.round_num not in self.messages:
            self.messages[self.round_num] = {
                ConsensusPhase.PROPOSE: [],
                ConsensusPhase.VOTE: [],
                ConsensusPhase.DECIDE: []
            }
        
        # Phase 1: Propose current value
        proposal = ConsensusMessage(
            sender_id=self.process_id,
            phase=ConsensusPhase.PROPOSE,
            round_num=self.round_num,
            value=self.current_value
        )
        
        self.phase = ConsensusPhase.PROPOSE
        return [proposal]
    
    def receive_message(self, msg: ConsensusMessage):
        """Process incoming consensus message"""
        if msg.round_num not in self.messages:
            return
        
        self.messages[msg.round_num][msg.phase].append(msg)
    
    def process_proposal_phase(self) -> Optional[List[ConsensusMessage]]:
        """
        Phase 1: Collect proposals, count values
        """
        proposals = self.messages[self.round_num][ConsensusPhase.PROPOSE]
        
        # Wait for majority of proposals (fault tolerance)
        if len(proposals) < self.n_processes - self.failure_threshold:
            return None
        
        # Count values in proposals
        value_counts = {}
        for msg in proposals:
            if msg.value not in value_counts:
                value_counts[msg.value] = 0
            value_counts[msg.value] += 1
        
        # Check if any value has clear majority
        majority_threshold = self.n_processes - self.failure_threshold
        majority_value = None
        
        for value, count in value_counts.items():
            if count >= majority_threshold:
                majority_value = value
                break
        
        # Vote based on what we observed
        if majority_value is not None:
            vote_value = majority_value
        else:
            # No clear majority - keep current preference
            vote_value = self.current_value
        
        vote_msg = ConsensusMessage(
            sender_id=self.process_id,
            phase=ConsensusPhase.VOTE,
            round_num=self.round_num,
            value=vote_value
        )
        
        self.phase = ConsensusPhase.VOTE
        return [vote_msg]
    
    def process_vote_phase(self) -> Optional[List[ConsensusMessage]]:
        """
        Phase 2: Collect votes, make decision or use random coin
        """
        votes = self.messages[self.round_num][ConsensusPhase.VOTE]
        
        if len(votes) < self.n_processes - self.failure_threshold:
            return None
        
        # Count votes
        vote_counts = {}
        for msg in votes:
            if msg.value not in vote_counts:
                vote_counts[msg.value] = 0
            vote_counts[msg.value] += 1
        
        # Check for strong majority that allows decision
        decision_threshold = (2 * self.n_processes + self.failure_threshold) // 3
        
        for value, count in vote_counts.items():
            if count >= decision_threshold:
                # Strong majority - can decide safely
                self.decided_value = value
                self.decided = True
                
                decision_msg = ConsensusMessage(
                    sender_id=self.process_id,
                    phase=ConsensusPhase.DECIDE,
                    round_num=self.round_num,
                    value=value
                )
                
                return [decision_msg]
        
        # No strong majority - use shared coin flip
        # This is where randomization breaks the FLP impossibility
        shared_coin = self._generate_shared_coin()
        
        if shared_coin:
            self.current_value = 1  # Arbitrary choice for coin=heads
        else:
            self.current_value = 0  # Arbitrary choice for coin=tails
        
        # Advance to next round
        self.round_num += 1
        return self.start_round()
    
    def _generate_shared_coin(self) -> bool:
        """
        Generate shared random coin flip
        
        In practice, this would use:
        - Verifiable Random Functions (VRFs)
        - Threshold signatures
        - Commit-reveal schemes
        
        For simulation, we use process_id as seed for reproducibility
        """
        random.seed(self.round_num + self.process_id)
        return random.choice([True, False])
    
    def get_statistics(self) -> Dict:
        """Return algorithm performance statistics"""
        return {
            "rounds_completed": self.round_num - 1,
            "expected_rounds": "O(1) expected",
            "message_complexity": f"O({self.n_processes}²) per round",
            "failure_tolerance": f"up to {self.failure_threshold} crashes",
            "termination_guarantee": "probabilistic - finite expected time"
        }

def simulate_ben_or_consensus():
    """
    Simulate Ben-Or randomized consensus with crash failures
    """
    n_processes = 5
    initial_values = [1, 1, 0, 1, 0]  # Mixed initial values
    
    processes = []
    for i in range(n_processes):
        processes.append(BenOrRandomizedConsensus(
            process_id=i,
            n_processes=n_processes,
            initial_value=initial_values[i]
        ))
    
    # Simulate crash failures
    crashed_processes = {4}  # Process 4 crashes
    active_processes = [p for i, p in enumerate(processes) 
                       if i not in crashed_processes]
    
    print("=== Ben-Or Randomized Consensus Simulation ===")
    print(f"Processes: {n_processes}, Crashed: {len(crashed_processes)}")
    print(f"Initial values: {initial_values}")
    
    max_rounds = 10
    for round_num in range(1, max_rounds + 1):
        print(f"\n--- Round {round_num} ---")
        
        # Check if consensus reached
        if all(p.decided for p in active_processes):
            decided_values = [p.decided_value for p in active_processes]
            print(f"CONSENSUS REACHED: {decided_values[0]}")
            break
        
        # Execute proposal phase
        all_proposals = []
        for process in active_processes:
            proposals = process.start_round()
            all_proposals.extend(proposals)
        
        # Distribute proposals
        for process in active_processes:
            for msg in all_proposals:
                if msg.sender_id != process.process_id:
                    process.receive_message(msg)
        
        # Process proposals and generate votes
        all_votes = []
        for process in active_processes:
            votes = process.process_proposal_phase()
            if votes:
                all_votes.extend(votes)
        
        # Distribute votes
        for process in active_processes:
            for msg in all_votes:
                if msg.sender_id != process.process_id:
                    process.receive_message(msg)
        
        # Process votes
        for process in active_processes:
            result = process.process_vote_phase()
            if result and any(msg.phase == ConsensusPhase.DECIDE for msg in result):
                print(f"Process {process.process_id} decided: {process.decided_value}")
    
    # Print statistics
    if active_processes:
        stats = active_processes[0].get_statistics()
        print(f"\nPerformance Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

# Run the simulation
simulate_ben_or_consensus()
```

#### Eventually Consistent Systems

When strong consistency is impossible due to CAP theorem constraints, eventually consistent systems provide a practical alternative:

```python
import time
import uuid
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from threading import Lock, Thread
import random

@dataclass
class VectorClock:
    """Vector clock for causal ordering in eventually consistent systems"""
    clock: Dict[str, int] = field(default_factory=dict)
    
    def update(self, node_id: str):
        """Update local clock"""
        if node_id not in self.clock:
            self.clock[node_id] = 0
        self.clock[node_id] += 1
    
    def merge(self, other: 'VectorClock'):
        """Merge with another vector clock"""
        for node_id, timestamp in other.clock.items():
            if node_id not in self.clock:
                self.clock[node_id] = 0
            self.clock[node_id] = max(self.clock[node_id], timestamp)
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this event happened before other"""
        if not self.clock or not other.clock:
            return False
        
        all_less_equal = all(
            self.clock.get(node, 0) <= other.clock.get(node, 0)
            for node in set(self.clock.keys()) | set(other.clock.keys())
        )
        
        some_strictly_less = any(
            self.clock.get(node, 0) < other.clock.get(node, 0)
            for node in set(self.clock.keys()) | set(other.clock.keys())
        )
        
        return all_less_equal and some_strictly_less

@dataclass
class Operation:
    """Represents an operation in the eventually consistent store"""
    op_id: str
    node_id: str
    key: str
    value: any
    timestamp: VectorClock
    op_type: str  # 'put', 'delete'
    wall_clock: float = field(default_factory=time.time)

class EventuallyConsistentKVStore:
    """
    Eventually consistent key-value store implementing CRDT principles
    
    This demonstrates how to work around CAP theorem by choosing AP
    (Availability + Partition tolerance) over consistency.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: Dict[str, any] = {}
        self.vector_clock = VectorClock()
        self.operation_log: List[Operation] = []
        self.lock = Lock()
        
        # For anti-entropy (gossip) protocol
        self.peers: Set[str] = set()
        self.last_sync_clocks: Dict[str, VectorClock] = {}
        
        # Conflict resolution strategy
        self.conflict_resolver = LastWriterWinsResolver()
    
    def put(self, key: str, value: any) -> str:
        """
        Put operation - always succeeds (AP guarantee)
        Returns operation ID for tracking
        """
        with self.lock:
            # Update vector clock
            self.vector_clock.update(self.node_id)
            
            # Create operation
            op = Operation(
                op_id=str(uuid.uuid4()),
                node_id=self.node_id,
                key=key,
                value=value,
                timestamp=VectorClock(self.vector_clock.clock.copy()),
                op_type='put'
            )
            
            # Apply locally
            self._apply_operation(op)
            
            return op.op_id
    
    def get(self, key: str) -> Optional[any]:
        """
        Get operation - returns local view (may be stale)
        This demonstrates availability during partitions
        """
        with self.lock:
            return self.data.get(key)
    
    def delete(self, key: str) -> str:
        """Delete operation"""
        with self.lock:
            self.vector_clock.update(self.node_id)
            
            op = Operation(
                op_id=str(uuid.uuid4()),
                node_id=self.node_id,
                key=key,
                value=None,
                timestamp=VectorClock(self.vector_clock.clock.copy()),
                op_type='delete'
            )
            
            self._apply_operation(op)
            return op.op_id
    
    def _apply_operation(self, op: Operation):
        """Apply operation to local state"""
        self.operation_log.append(op)
        
        if op.op_type == 'put':
            self.data[op.key] = op.value
        elif op.op_type == 'delete':
            self.data.pop(op.key, None)
    
    def add_peer(self, peer_node_id: str):
        """Add peer for gossip protocol"""
        self.peers.add(peer_node_id)
        self.last_sync_clocks[peer_node_id] = VectorClock()
    
    def sync_with_peer(self, peer_store: 'EventuallyConsistentKVStore') -> int:
        """
        Anti-entropy gossip synchronization
        
        This is how eventual consistency is achieved - periodic sync
        between nodes to propagate updates and resolve conflicts.
        """
        operations_synced = 0
        
        with self.lock, peer_store.lock:
            # Get operations that peer hasn't seen
            peer_last_sync = self.last_sync_clocks.get(peer_store.node_id, VectorClock())
            
            ops_to_send = []
            for op in self.operation_log:
                if not peer_last_sync.happens_before(op.timestamp) and \
                   not op.timestamp.happens_before(peer_last_sync):
                    ops_to_send.append(op)
            
            # Send operations to peer
            for op in ops_to_send:
                if peer_store._should_accept_operation(op):
                    peer_store._receive_remote_operation(op)
                    operations_synced += 1
            
            # Update sync tracking
            self.last_sync_clocks[peer_store.node_id] = VectorClock(
                peer_store.vector_clock.clock.copy()
            )
        
        return operations_synced
    
    def _should_accept_operation(self, op: Operation) -> bool:
        """Check if we should accept a remote operation"""
        # Don't accept our own operations
        if op.node_id == self.node_id:
            return False
        
        # Check if we already have this operation
        for existing_op in self.operation_log:
            if existing_op.op_id == op.op_id:
                return False
        
        return True
    
    def _receive_remote_operation(self, op: Operation):
        """Receive and process operation from remote node"""
        # Update vector clock with remote timestamp
        self.vector_clock.merge(op.timestamp)
        
        # Check for conflicts
        conflicts = self._find_conflicts(op)
        
        if conflicts:
            # Resolve conflicts using strategy
            resolved_op = self.conflict_resolver.resolve(op, conflicts)
            if resolved_op:
                self._apply_operation(resolved_op)
        else:
            self._apply_operation(op)
    
    def _find_conflicts(self, op: Operation) -> List[Operation]:
        """Find conflicting operations for the same key"""
        conflicts = []
        
        for existing_op in self.operation_log:
            if (existing_op.key == op.key and 
                existing_op.op_id != op.op_id and
                not existing_op.timestamp.happens_before(op.timestamp) and
                not op.timestamp.happens_before(existing_op.timestamp)):
                conflicts.append(existing_op)
        
        return conflicts
    
    def get_consistency_info(self) -> Dict:
        """Get information about consistency state"""
        return {
            "node_id": self.node_id,
            "vector_clock": dict(self.vector_clock.clock),
            "operations_count": len(self.operation_log),
            "data_keys": list(self.data.keys()),
            "peer_count": len(self.peers),
            "consistency_model": "eventual_consistency"
        }

class LastWriterWinsResolver:
    """
    Simple conflict resolution: last writer wins based on wall clock
    
    Note: This can lead to lost updates, but provides simple semantics
    """
    
    def resolve(self, new_op: Operation, conflicting_ops: List[Operation]) -> Optional[Operation]:
        """Resolve conflicts using last-writer-wins"""
        all_ops = [new_op] + conflicting_ops
        
        # Sort by wall clock time, then by node_id for determinism
        all_ops.sort(key=lambda op: (op.wall_clock, op.node_id))
        
        # Return the "latest" operation
        return all_ops[-1]

def demonstrate_eventual_consistency():
    """
    Demonstrate how eventually consistent systems work around CAP theorem
    """
    print("=== Eventually Consistent Key-Value Store Demo ===")
    
    # Create three nodes
    node_a = EventuallyConsistentKVStore("node_a")
    node_b = EventuallyConsistentKVStore("node_b")  
    node_c = EventuallyConsistentKVStore("node_c")
    
    # Set up peer relationships
    node_a.add_peer("node_b")
    node_a.add_peer("node_c")
    node_b.add_peer("node_a")
    node_b.add_peer("node_c")
    node_c.add_peer("node_a")
    node_c.add_peer("node_b")
    
    print("\n1. Initial state - all nodes empty")
    for node in [node_a, node_b, node_c]:
        info = node.get_consistency_info()
        print(f"  {info['node_id']}: {len(info['data_keys'])} keys")
    
    # Simulate network partition: A and B can communicate, C is isolated
    print("\n2. Network partition occurs - Node C isolated")
    
    # Operations during partition
    print("\n3. Concurrent operations during partition:")
    
    # Nodes A and B can still serve requests (Availability)
    op1 = node_a.put("user:123", {"name": "Alice", "version": 1})
    op2 = node_b.put("user:456", {"name": "Bob", "version": 1})
    print(f"  Node A: PUT user:123 -> Alice (op: {op1[:8]}...)")
    print(f"  Node B: PUT user:456 -> Bob (op: {op2[:8]}...)")
    
    # Isolated node C continues serving with stale data
    val = node_c.get("user:123")
    print(f"  Node C: GET user:123 -> {val} (stale/missing)")
    
    # Node C accepts writes (remains available)
    op3 = node_c.put("user:789", {"name": "Charlie", "version": 1})
    print(f"  Node C: PUT user:789 -> Charlie (op: {op3[:8]}...)")
    
    # Sync between A and B (they're connected)
    synced = node_a.sync_with_peer(node_b)
    print(f"\n4. Sync A <-> B: {synced} operations exchanged")
    
    print("\n5. State after A-B sync:")
    for node in [node_a, node_b]:
        info = node.get_consistency_info()
        print(f"  {info['node_id']}: {info['data_keys']}")
    
    # Partition heals
    print("\n6. Network partition heals - Node C reconnects")
    
    # Full synchronization
    sync_ac = node_a.sync_with_peer(node_c)
    sync_bc = node_b.sync_with_peer(node_c)
    print(f"  A -> C: {sync_ac} operations")
    print(f"  B -> C: {sync_bc} operations")
    
    # Sync back from C
    sync_ca = node_c.sync_with_peer(node_a)
    print(f"  C -> A: {sync_ca} operations")
    
    print("\n7. Final consistent state (eventually):")
    for node in [node_a, node_b, node_c]:
        info = node.get_consistency_info()
        data_summary = {k: v for k, v in node.data.items()}
        print(f"  {info['node_id']}: {data_summary}")
    
    print(f"\n8. Consistency achieved through:")
    print(f"  - Anti-entropy gossip protocol")
    print(f"  - Vector clocks for causal ordering")
    print(f"  - Last-writer-wins conflict resolution")
    print(f"  - Trade-off: Temporary inconsistency for availability")

# Run the demonstration
demonstrate_eventual_consistency()
```

### Weak Consistency Models (15 minutes)

When linearizability is too expensive due to coordination costs, weaker consistency models provide better performance while still offering useful guarantees:

```python
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import threading
import time

class ConsistencyLevel(Enum):
    EVENTUAL = "eventual"
    CAUSAL = "causal"
    MONOTONIC_READ = "monotonic_read"
    MONOTONIC_WRITE = "monotonic_write"
    READ_YOUR_WRITES = "read_your_writes"

@dataclass
class ReadResult:
    value: any
    version: int
    consistency_level: ConsistencyLevel
    staleness_bound: Optional[float] = None

class WeakConsistencyStore:
    """
    Implements multiple weak consistency models to work around
    impossibility of strong consistency in partitioned systems
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: Dict[str, any] = {}
        self.versions: Dict[str, int] = {}
        self.causal_context: Dict[str, Set[str]] = {}  # Key -> set of dependent keys
        self.client_sessions: Dict[str, Dict[str, int]] = {}  # client_id -> key -> version_seen
        self.lock = threading.RLock()
        
        # For monotonic consistency tracking
        self.read_timestamps: Dict[str, float] = {}  # key -> last_read_time
        self.write_timestamps: Dict[str, float] = {}  # key -> last_write_time
    
    def put(self, key: str, value: any, client_id: str = None, 
            causal_dependencies: Set[str] = None) -> int:
        """
        Write with support for different consistency guarantees
        """
        with self.lock:
            # Update version
            current_version = self.versions.get(key, 0) + 1
            self.versions[key] = current_version
            
            # Store data
            self.data[key] = value
            self.write_timestamps[key] = time.time()
            
            # Handle causal dependencies
            if causal_dependencies:
                self.causal_context[key] = causal_dependencies.copy()
            
            # Track client session for read-your-writes
            if client_id:
                if client_id not in self.client_sessions:
                    self.client_sessions[client_id] = {}
                self.client_sessions[client_id][key] = current_version
            
            return current_version
    
    def get(self, key: str, consistency_level: ConsistencyLevel, 
            client_id: str = None) -> ReadResult:
        """
        Read with specified consistency level
        """
        with self.lock:
            current_time = time.time()
            
            if consistency_level == ConsistencyLevel.EVENTUAL:
                return self._eventual_read(key)
            
            elif consistency_level == ConsistencyLevel.CAUSAL:
                return self._causal_read(key)
            
            elif consistency_level == ConsistencyLevel.MONOTONIC_READ:
                return self._monotonic_read(key, current_time)
            
            elif consistency_level == ConsistencyLevel.READ_YOUR_WRITES:
                return self._read_your_writes(key, client_id)
            
            else:
                # Default to eventual
                return self._eventual_read(key)
    
    def _eventual_read(self, key: str) -> ReadResult:
        """
        Eventual consistency: Return any available value
        No ordering guarantees, maximum availability
        """
        value = self.data.get(key)
        version = self.versions.get(key, 0)
        
        return ReadResult(
            value=value,
            version=version,
            consistency_level=ConsistencyLevel.EVENTUAL,
            staleness_bound=None  # Unbounded staleness
        )
    
    def _causal_read(self, key: str) -> ReadResult:
        """
        Causal consistency: Ensure causally related operations are seen in order
        """
        # Check causal dependencies
        if key in self.causal_context:
            dependencies = self.causal_context[key]
            
            # Verify all causal dependencies are satisfied
            for dep_key in dependencies:
                if dep_key not in self.data:
                    # Dependency not yet available - this would typically
                    # require waiting or fetching from other nodes
                    pass
        
        value = self.data.get(key)
        version = self.versions.get(key, 0)
        
        # Update read timestamp for causal tracking
        self.read_timestamps[key] = time.time()
        
        return ReadResult(
            value=value,
            version=version,
            consistency_level=ConsistencyLevel.CAUSAL
        )
    
    def _monotonic_read(self, key: str, current_time: float) -> ReadResult:
        """
        Monotonic read consistency: Never read older versions
        """
        last_read_time = self.read_timestamps.get(key, 0)
        
        # In real implementation, this would ensure we don't read
        # a version older than what we've seen before
        if current_time < last_read_time:
            # This would typically require waiting or rejecting the read
            pass
        
        self.read_timestamps[key] = current_time
        
        value = self.data.get(key)
        version = self.versions.get(key, 0)
        
        return ReadResult(
            value=value,
            version=version,
            consistency_level=ConsistencyLevel.MONOTONIC_READ
        )
    
    def _read_your_writes(self, key: str, client_id: str) -> ReadResult:
        """
        Read-your-writes consistency: Client always sees their own writes
        """
        if not client_id:
            # Fall back to eventual consistency
            return self._eventual_read(key)
        
        # Check what version this client last wrote
        client_version = self.client_sessions.get(client_id, {}).get(key, 0)
        current_version = self.versions.get(key, 0)
        
        if current_version < client_version:
            # Current replica is behind client's writes
            # In real system, would need to:
            # 1. Wait for updates
            # 2. Read from another replica
            # 3. Return stale read warning
            pass
        
        value = self.data.get(key)
        
        return ReadResult(
            value=value,
            version=current_version,
            consistency_level=ConsistencyLevel.READ_YOUR_WRITES
        )

def demonstrate_weak_consistency():
    """
    Demonstrate different weak consistency models
    """
    print("=== Weak Consistency Models Demonstration ===")
    
    store = WeakConsistencyStore("replica_1")
    
    # Simulate different consistency scenarios
    print("\n1. Eventual Consistency:")
    store.put("counter", 5)
    result = store.get("counter", ConsistencyLevel.EVENTUAL)
    print(f"  Read: {result.value} (version {result.version})")
    print(f"  Guarantee: Eventually all replicas will converge")
    
    print("\n2. Causal Consistency:")
    # Create causal dependency: counter depends on user_count
    store.put("user_count", 100)
    store.put("counter", 6, causal_dependencies={"user_count"})
    
    result = store.get("counter", ConsistencyLevel.CAUSAL)
    print(f"  Read: {result.value} (version {result.version})")
    print(f"  Guarantee: If A caused B, all processes see A before B")
    
    print("\n3. Read-Your-Writes Consistency:")
    client_id = "user_123"
    store.put("profile", {"name": "Alice", "age": 25}, client_id=client_id)
    
    result = store.get("profile", ConsistencyLevel.READ_YOUR_WRITES, client_id)
    print(f"  Client {client_id} reads: {result.value}")
    print(f"  Guarantee: Clients see their own writes immediately")
    
    print("\n4. Monotonic Read Consistency:")
    result = store.get("counter", ConsistencyLevel.MONOTONIC_READ)
    print(f"  Read: {result.value} (version {result.version})")
    print(f"  Guarantee: Later reads never return earlier values")
    
    print(f"\nConsistency Model Trade-offs:")
    print(f"  Eventual: Maximum availability, minimal coordination")
    print(f"  Causal: Preserves cause-effect, moderate coordination")
    print(f"  Read-your-writes: Good UX, requires session tracking")
    print(f"  Monotonic: Prevents confusion, needs version tracking")

# Run demonstration
demonstrate_weak_consistency()
```

### Practical Failure Detectors (15 minutes)

Since perfect failure detection is impossible in asynchronous systems, we implement practical failure detectors with tunable properties:

```python
import time
import threading
import random
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class FailureDetectorType(Enum):
    PERFECT = "perfect"          # Impossible in async systems
    EVENTUALLY_PERFECT = "eventually_perfect"
    STRONG = "strong"            # Eventually complete and accurate
    WEAK = "weak"               # Eventually detects at least one failure
    OMEGA = "omega"             # Eventually elect correct leader

@dataclass
class SuspicionLevel:
    node_id: str
    suspicion: float  # 0.0 = trusted, 1.0 = definitely failed
    last_heartbeat: float
    timeout_count: int

class AccrualFailureDetector:
    """
    φ (Phi) Accrual Failure Detector
    
    Used in Cassandra and Akka - provides continuous failure suspicion
    rather than binary failed/alive decisions.
    
    Key insight: Use statistical analysis of heartbeat intervals
    to generate continuous suspicion levels.
    """
    
    def __init__(self, node_id: str, threshold: float = 8.0):
        self.node_id = node_id
        self.threshold = threshold  # φ threshold for failure detection
        self.heartbeat_history: Dict[str, List[float]] = {}  # node -> intervals
        self.last_heartbeats: Dict[str, float] = {}
        self.suspicion_levels: Dict[str, float] = {}
        self.max_sample_size = 1000
        self.lock = threading.Lock()
    
    def heartbeat_received(self, from_node: str, timestamp: float = None):
        """Record heartbeat from another node"""
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            if from_node in self.last_heartbeats:
                interval = timestamp - self.last_heartbeats[from_node]
                
                # Store interval for statistical analysis
                if from_node not in self.heartbeat_history:
                    self.heartbeat_history[from_node] = []
                
                history = self.heartbeat_history[from_node]
                history.append(interval)
                
                # Keep only recent samples
                if len(history) > self.max_sample_size:
                    history.pop(0)
            
            self.last_heartbeats[from_node] = timestamp
            # Reset suspicion on heartbeat
            self.suspicion_levels[from_node] = 0.0
    
    def calculate_phi(self, node_id: str) -> float:
        """
        Calculate φ (phi) value for a node
        
        φ = -log₁₀(P(t_now - t_last))
        where P is cumulative distribution of intervals
        """
        if node_id not in self.last_heartbeats:
            return float('inf')  # Never seen = definitely suspicious
        
        current_time = time.time()
        time_since_last = current_time - self.last_heartbeats[node_id]
        
        if node_id not in self.heartbeat_history:
            # No history yet - use default timeout
            expected_interval = 1.0  # 1 second default
            if time_since_last > expected_interval * 3:
                return 10.0  # High suspicion
            return 0.0
        
        intervals = self.heartbeat_history[node_id]
        if len(intervals) < 2:
            return 0.0
        
        # Calculate mean and standard deviation
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            # No variation - use simple timeout
            if time_since_last > mean_interval * 2:
                return 10.0
            return 0.0
        
        # Approximate normal distribution CDF
        # φ = -log10(P(time_since_last | normal(mean, std)))
        z_score = (time_since_last - mean_interval) / std_dev
        
        # Simplified phi calculation
        if z_score <= 0:
            return 0.0
        
        phi = z_score * 2  # Simplified approximation
        return min(phi, 100.0)  # Cap at reasonable maximum
    
    def is_suspected(self, node_id: str) -> bool:
        """Check if node is suspected of failure"""
        phi = self.calculate_phi(node_id)
        return phi > self.threshold
    
    def get_suspicion_level(self, node_id: str) -> float:
        """Get continuous suspicion level (0.0 to 1.0)"""
        phi = self.calculate_phi(node_id)
        return min(1.0, phi / 20.0)  # Normalize to 0-1 range
    
    def adjust_threshold(self, new_threshold: float):
        """Dynamically adjust failure detection threshold"""
        self.threshold = new_threshold

class OmegaFailureDetector:
    """
    Ω (Omega) Failure Detector - Eventually Strong Leader Election
    
    Guarantees:
    - Eventually, there is a time after which every correct process
      trusts the same correct process (eventual leader)
    - Used for consensus algorithms that need eventual leader election
    """
    
    def __init__(self, node_id: str, all_nodes: Set[str]):
        self.node_id = node_id
        self.all_nodes = all_nodes
        self.suspected_nodes: Set[str] = set()
        self.current_leader = min(all_nodes)  # Start with lowest ID
        self.leader_history: List[str] = []
        self.stability_period = 5.0  # Seconds of stability required
        self.last_leader_change = time.time()
        self.lock = threading.Lock()
    
    def suspect_node(self, node_id: str):
        """Mark a node as suspected"""
        with self.lock:
            if node_id not in self.suspected_nodes:
                self.suspected_nodes.add(node_id)
                self._update_leader()
    
    def trust_node(self, node_id: str):
        """Remove suspicion from a node"""
        with self.lock:
            if node_id in self.suspected_nodes:
                self.suspected_nodes.remove(node_id)
                self._update_leader()
    
    def _update_leader(self):
        """Update current leader based on suspicions"""
        # Choose lowest ID among non-suspected nodes
        available_nodes = self.all_nodes - self.suspected_nodes
        
        if available_nodes:
            new_leader = min(available_nodes)
            if new_leader != self.current_leader:
                self.current_leader = new_leader
                self.last_leader_change = time.time()
                self.leader_history.append(new_leader)
                print(f"Node {self.node_id}: Leader changed to {new_leader}")
    
    def get_leader(self) -> str:
        """Get current leader"""
        return self.current_leader
    
    def is_leader_stable(self) -> bool:
        """Check if leader has been stable for sufficient time"""
        return time.time() - self.last_leader_change > self.stability_period
    
    def get_statistics(self) -> Dict:
        """Get failure detector statistics"""
        return {
            "current_leader": self.current_leader,
            "suspected_nodes": list(self.suspected_nodes),
            "leader_changes": len(self.leader_history),
            "stability": self.is_leader_stable(),
            "time_since_change": time.time() - self.last_leader_change
        }

class HeartbeatService:
    """Service that sends heartbeats and manages failure detection"""
    
    def __init__(self, node_id: str, failure_detector: AccrualFailureDetector):
        self.node_id = node_id
        self.failure_detector = failure_detector
        self.peers: Set[str] = set()
        self.heartbeat_interval = 1.0  # seconds
        self.running = False
        self.thread = None
    
    def add_peer(self, peer_id: str):
        """Add peer to monitor"""
        self.peers.add(peer_id)
    
    def start(self):
        """Start heartbeat service"""
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop)
        self.thread.start()
    
    def stop(self):
        """Stop heartbeat service"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _heartbeat_loop(self):
        """Main heartbeat loop"""
        while self.running:
            # Send heartbeats (simulated by directly calling receive)
            current_time = time.time()
            
            for peer in self.peers:
                # Simulate network delays and failures
                if random.random() < 0.95:  # 95% success rate
                    delay = random.uniform(0.01, 0.1)  # 10-100ms delay
                    # In real system, this would be network send
                    # Here we simulate by calling peer's receive method
                    pass
            
            time.sleep(self.heartbeat_interval)

def demonstrate_failure_detectors():
    """
    Demonstrate practical failure detector implementations
    """
    print("=== Practical Failure Detector Demonstration ===")
    
    # Setup nodes
    nodes = {"node_a", "node_b", "node_c", "node_d"}
    
    # Create accrual failure detectors
    detectors = {}
    for node in nodes:
        detectors[node] = AccrualFailureDetector(node, threshold=5.0)
    
    # Create omega failure detector
    omega = OmegaFailureDetector("node_a", nodes)
    
    print(f"\n1. Initial state:")
    print(f"  Nodes: {nodes}")
    print(f"  Leader (Omega): {omega.get_leader()}")
    
    # Simulate heartbeat pattern
    print(f"\n2. Normal heartbeat pattern:")
    base_time = time.time()
    
    # Normal heartbeats
    for i in range(5):
        timestamp = base_time + i * 1.0  # 1 second intervals
        for node in nodes:
            if node != "node_a":
                detectors["node_a"].heartbeat_received(node, timestamp)
        
        time.sleep(0.1)  # Small delay for demo
    
    # Check suspicion levels
    for node in nodes:
        if node != "node_a":
            phi = detectors["node_a"].calculate_phi(node)
            suspected = detectors["node_a"].is_suspected(node)
            print(f"  {node}: φ={phi:.2f}, suspected={suspected}")
    
    # Simulate node failure
    print(f"\n3. Simulating node_c failure (stops sending heartbeats):")
    
    # Continue heartbeats but skip node_c
    for i in range(10):
        timestamp = base_time + 5 + i * 1.0
        for node in nodes:
            if node not in ["node_a", "node_c"]:  # node_c fails
                detectors["node_a"].heartbeat_received(node, timestamp)
        
        time.sleep(0.1)
        
        # Check suspicion after some time
        if i == 5:
            phi_c = detectors["node_a"].calculate_phi("node_c")
            suspected_c = detectors["node_a"].is_suspected("node_c")
            print(f"    After {i+1} missed heartbeats: φ={phi_c:.2f}, suspected={suspected_c}")
    
    # Update omega failure detector
    omega.suspect_node("node_c")
    
    print(f"\n4. After failure detection:")
    for node in nodes:
        if node != "node_a":
            phi = detectors["node_a"].calculate_phi(node)
            suspected = detectors["node_a"].is_suspected(node)
            suspicion = detectors["node_a"].get_suspicion_level(node)
            print(f"  {node}: φ={phi:.2f}, suspected={suspected}, suspicion={suspicion:.2f}")
    
    omega_stats = omega.get_statistics()
    print(f"  Omega leader: {omega_stats['current_leader']}")
    print(f"  Suspected nodes: {omega_stats['suspected_nodes']}")
    
    # Simulate recovery
    print(f"\n5. Node recovery:")
    recovery_time = base_time + 20
    detectors["node_a"].heartbeat_received("node_c", recovery_time)
    omega.trust_node("node_c")
    
    phi_c = detectors["node_a"].calculate_phi("node_c")
    suspected_c = detectors["node_a"].is_suspected("node_c")
    print(f"  node_c after recovery: φ={phi_c:.2f}, suspected={suspected_c}")
    
    print(f"\nKey Properties Demonstrated:")
    print(f"  - Accrual detection: Continuous suspicion levels vs binary")
    print(f"  - Statistical analysis: Uses heartbeat interval history")
    print(f"  - Tunable sensitivity: Threshold adjustment for false positives")
    print(f"  - Leader election: Eventual agreement on correct leader")
    print(f"  - Recovery handling: Suspicion resets on heartbeat")

# Run demonstration
demonstrate_failure_detectors()
```

### Production Workarounds (15 minutes)

Real systems use practical workarounds that acknowledge impossibility results while providing useful guarantees:

#### Timeouts and Retries

```python
import time
import random
import asyncio
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum

class TimeoutStrategy(Enum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential" 
    LINEAR = "linear"
    JITTERED_EXPONENTIAL = "jittered_exponential"

@dataclass
class RetryPolicy:
    max_attempts: int
    base_timeout: float
    max_timeout: float
    strategy: TimeoutStrategy
    jitter: bool = True
    backoff_multiplier: float = 2.0

class TimeoutManager:
    """
    Production timeout and retry system that works around
    FLP impossibility by adding timing assumptions
    """
    
    def __init__(self):
        self.operation_stats: Dict[str, List[float]] = {}
        self.adaptive_timeouts: Dict[str, float] = {}
        self.success_rates: Dict[str, float] = {}
    
    def calculate_timeout(self, operation: str, policy: RetryPolicy, 
                         attempt: int) -> float:
        """Calculate timeout for given attempt"""
        
        if policy.strategy == TimeoutStrategy.FIXED:
            return policy.base_timeout
        
        elif policy.strategy == TimeoutStrategy.LINEAR:
            timeout = policy.base_timeout + (attempt - 1) * policy.base_timeout
            
        elif policy.strategy == TimeoutStrategy.EXPONENTIAL:
            timeout = policy.base_timeout * (policy.backoff_multiplier ** (attempt - 1))
            
        elif policy.strategy == TimeoutStrategy.JITTERED_EXPONENTIAL:
            base_timeout = policy.base_timeout * (policy.backoff_multiplier ** (attempt - 1))
            jitter = random.uniform(0.5, 1.5) if policy.jitter else 1.0
            timeout = base_timeout * jitter
        
        else:
            timeout = policy.base_timeout
        
        # Apply bounds
        return min(timeout, policy.max_timeout)
    
    def adaptive_timeout(self, operation: str) -> float:
        """
        Calculate adaptive timeout based on historical performance
        
        This is how production systems work around timing assumptions:
        they adapt to observed network behavior
        """
        if operation not in self.operation_stats:
            return 5.0  # Default 5 second timeout
        
        stats = self.operation_stats[operation]
        if len(stats) < 10:
            return 5.0
        
        # Use 95th percentile + safety margin
        sorted_times = sorted(stats)
        p95_index = int(0.95 * len(sorted_times))
        p95_time = sorted_times[p95_index]
        
        # Add safety margin
        adaptive = p95_time * 1.5
        return min(adaptive, 30.0)  # Cap at 30 seconds
    
    def record_operation(self, operation: str, duration: float, success: bool):
        """Record operation performance for adaptive timeouts"""
        if operation not in self.operation_stats:
            self.operation_stats[operation] = []
        
        # Keep only recent history
        stats = self.operation_stats[operation]
        stats.append(duration)
        if len(stats) > 1000:
            stats.pop(0)
        
        # Update success rate
        if operation not in self.success_rates:
            self.success_rates[operation] = 1.0 if success else 0.0
        else:
            # Exponentially weighted moving average
            alpha = 0.1
            current = 1.0 if success else 0.0
            self.success_rates[operation] = (
                alpha * current + (1 - alpha) * self.success_rates[operation]
            )

async def with_timeout_retry(operation: Callable, 
                           operation_name: str,
                           policy: RetryPolicy,
                           timeout_manager: TimeoutManager) -> any:
    """
    Execute operation with timeout and retry logic
    
    This is the practical workaround for impossibility:
    - Assume eventual network stability
    - Use timeouts to detect likely failures
    - Retry with backoff to handle transient issues
    """
    
    last_exception = None
    
    for attempt in range(1, policy.max_attempts + 1):
        start_time = time.time()
        timeout = timeout_manager.calculate_timeout(operation_name, policy, attempt)
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(operation(), timeout=timeout)
            
            # Record success
            duration = time.time() - start_time
            timeout_manager.record_operation(operation_name, duration, True)
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            timeout_manager.record_operation(operation_name, duration, False)
            
            last_exception = TimeoutError(f"Operation {operation_name} timed out after {timeout:.2f}s")
            
            if attempt < policy.max_attempts:
                print(f"Attempt {attempt} failed with timeout, retrying...")
                await asyncio.sleep(timeout * 0.1)  # Brief pause before retry
            
        except Exception as e:
            duration = time.time() - start_time
            timeout_manager.record_operation(operation_name, duration, False)
            
            last_exception = e
            
            if attempt < policy.max_attempts:
                print(f"Attempt {attempt} failed with error: {e}, retrying...")
                await asyncio.sleep(timeout * 0.1)
    
    # All attempts failed
    raise last_exception

# Demo usage
async def unreliable_network_operation():
    """Simulate unreliable network operation"""
    # 30% chance of failure, variable latency
    if random.random() < 0.3:
        await asyncio.sleep(random.uniform(10, 20))  # Very long delay
        raise ConnectionError("Network timeout")
    
    # Normal case with some latency
    await asyncio.sleep(random.uniform(0.1, 2.0))
    return "Success!"

async def demonstrate_timeout_retry():
    """Demonstrate production timeout/retry patterns"""
    print("=== Timeout and Retry Demonstration ===")
    
    timeout_manager = TimeoutManager()
    
    # Conservative policy for critical operations
    critical_policy = RetryPolicy(
        max_attempts=5,
        base_timeout=2.0,
        max_timeout=10.0,
        strategy=TimeoutStrategy.EXPONENTIAL,
        jitter=True
    )
    
    # Aggressive policy for non-critical operations
    fast_policy = RetryPolicy(
        max_attempts=3,
        base_timeout=0.5,
        max_timeout=3.0,
        strategy=TimeoutStrategy.JITTERED_EXPONENTIAL
    )
    
    print("\n1. Testing with critical operation policy:")
    try:
        result = await with_timeout_retry(
            unreliable_network_operation,
            "critical_db_write",
            critical_policy,
            timeout_manager
        )
        print(f"   Success: {result}")
    except Exception as e:
        print(f"   Failed: {e}")
    
    print("\n2. Testing with fast operation policy:")
    try:
        result = await with_timeout_retry(
            unreliable_network_operation,
            "cache_lookup", 
            fast_policy,
            timeout_manager
        )
        print(f"   Success: {result}")
    except Exception as e:
        print(f"   Failed: {e}")
    
    # Show adaptive timeout learning
    print(f"\n3. Adaptive timeout learning:")
    adaptive_timeout = timeout_manager.adaptive_timeout("critical_db_write")
    print(f"   Learned timeout for critical_db_write: {adaptive_timeout:.2f}s")
    
    success_rate = timeout_manager.success_rates.get("critical_db_write", 0.0)
    print(f"   Success rate: {success_rate:.2%}")

# Run demo
# asyncio.run(demonstrate_timeout_retry())
```

#### Quorum Systems

```python
from typing import Set, List, Dict, Optional, Tuple
from dataclasses import dataclass
from math import ceil

@dataclass
class QuorumConfiguration:
    read_quorum: int
    write_quorum: int
    total_replicas: int
    
    def __post_init__(self):
        # Verify quorum intersection property: R + W > N
        # This ensures read quorum intersects with write quorum
        if self.read_quorum + self.write_quorum <= self.total_replicas:
            raise ValueError("Invalid quorum: R + W must be > N for consistency")

class QuorumSystem:
    """
    Implement quorum-based replication to work around CAP theorem
    
    Trade-off approach:
    - During partitions, choose either consistency OR availability
    - Quorum size determines the trade-off point
    - Larger quorums = more consistency, less availability
    """
    
    def __init__(self, node_id: str, config: QuorumConfiguration):
        self.node_id = node_id
        self.config = config
        self.data: Dict[str, any] = {}
        self.versions: Dict[str, int] = {}
        self.available_replicas: Set[str] = set()
        
        # All possible replica nodes
        self.all_replicas = set(f"replica_{i}" for i in range(config.total_replicas))
        self.available_replicas = self.all_replicas.copy()  # Start with all available
    
    def set_replica_status(self, replica_id: str, available: bool):
        """Simulate replica availability changes"""
        if available:
            self.available_replicas.add(replica_id)
        else:
            self.available_replicas.discard(replica_id)
    
    def select_read_replicas(self) -> Optional[Set[str]]:
        """Select replicas for read quorum"""
        if len(self.available_replicas) < self.config.read_quorum:
            return None  # Cannot form read quorum
        
        # Simple selection: take first R available replicas
        return set(list(self.available_replicas)[:self.config.read_quorum])
    
    def select_write_replicas(self) -> Optional[Set[str]]:
        """Select replicas for write quorum"""
        if len(self.available_replicas) < self.config.write_quorum:
            return None  # Cannot form write quorum
        
        return set(list(self.available_replicas)[:self.config.write_quorum])
    
    def quorum_read(self, key: str) -> Tuple[bool, any]:
        """
        Perform quorum read
        Returns: (success, value)
        """
        read_replicas = self.select_read_replicas()
        if not read_replicas:
            return False, None  # Not enough replicas - choose consistency over availability
        
        # Simulate reading from replicas
        responses = []
        for replica in read_replicas:
            # In real system, this would be network calls
            version = self.versions.get(key, 0)
            value = self.data.get(key)
            responses.append((version, value))
        
        # Return latest version (read repair would happen here)
        if responses:
            latest = max(responses, key=lambda x: x[0])
            return True, latest[1]
        
        return False, None
    
    def quorum_write(self, key: str, value: any) -> bool:
        """
        Perform quorum write
        Returns: success boolean
        """
        write_replicas = self.select_write_replicas()
        if not write_replicas:
            return False  # Not enough replicas - choose consistency over availability
        
        # Increment version
        new_version = self.versions.get(key, 0) + 1
        
        # Write to quorum replicas
        successful_writes = 0
        for replica in write_replicas:
            # In real system, this would be network calls
            # Here we simulate by updating local state
            if replica == self.node_id or random.random() < 0.9:  # 90% success rate
                self.data[key] = value
                self.versions[key] = new_version
                successful_writes += 1
        
        return successful_writes >= self.config.write_quorum
    
    def check_availability(self) -> Dict[str, bool]:
        """Check what operations are currently available"""
        return {
            "can_read": len(self.available_replicas) >= self.config.read_quorum,
            "can_write": len(self.available_replicas) >= self.config.write_quorum,
            "available_replicas": len(self.available_replicas),
            "total_replicas": self.config.total_replicas
        }

def demonstrate_quorum_systems():
    """
    Demonstrate how quorum systems handle CAP theorem trade-offs
    """
    print("=== Quorum System CAP Trade-offs Demonstration ===")
    
    # Create different quorum configurations
    configs = {
        "strong_consistency": QuorumConfiguration(
            read_quorum=3, write_quorum=3, total_replicas=5  # R=3, W=3, N=5
        ),
        "balanced": QuorumConfiguration(
            read_quorum=2, write_quorum=3, total_replicas=5  # R=2, W=3, N=5
        ),
        "read_optimized": QuorumConfiguration(
            read_quorum=1, write_quorum=4, total_replicas=5  # R=1, W=4, N=5
        )
    }
    
    for name, config in configs.items():
        print(f"\n--- {name.upper()} Configuration ---")
        print(f"Read Quorum: {config.read_quorum}, Write Quorum: {config.write_quorum}")
        
        system = QuorumSystem("coordinator", config)
        
        # Test normal operation
        print("1. Normal operation (all replicas available):")
        availability = system.check_availability()
        print(f"   Can read: {availability['can_read']}")
        print(f"   Can write: {availability['can_write']}")
        
        # Test write operation
        success = system.quorum_write("user:123", {"name": "Alice", "balance": 100})
        print(f"   Write success: {success}")
        
        # Test read operation  
        read_success, value = system.quorum_read("user:123")
        print(f"   Read success: {read_success}, Value: {value}")
        
        # Simulate network partition
        print("2. Network partition (2 replicas unreachable):")
        system.set_replica_status("replica_3", False)
        system.set_replica_status("replica_4", False)
        
        availability = system.check_availability()
        print(f"   Available replicas: {availability['available_replicas']}")
        print(f"   Can read: {availability['can_read']}")
        print(f"   Can write: {availability['can_write']}")
        
        # Test operations during partition
        write_success = system.quorum_write("user:456", {"name": "Bob"})
        read_success, _ = system.quorum_read("user:123")
        print(f"   Write during partition: {write_success}")
        print(f"   Read during partition: {read_success}")
        
        # Analyze trade-off
        print("3. CAP trade-off analysis:")
        if availability['can_read'] and availability['can_write']:
            print("   → Chooses AVAILABILITY (AP system)")
        else:
            print("   → Chooses CONSISTENCY (CP system)")
        
        # Reset for next test
        system.set_replica_status("replica_3", True)
        system.set_replica_status("replica_4", True)

# Run demonstration  
demonstrate_quorum_systems()
```

### Summary: Living with Impossibilities

The key insight from this implementation section is that impossibility results don't stop us from building systems—they guide our design decisions:

1. **FLP Impossibility** → Use timeouts, randomization, or failure detectors
2. **CAP Theorem** → Choose your trade-offs explicitly via quorum systems
3. **Two Generals** → Accept probabilistic rather than perfect coordination
4. **Byzantine Bounds** → Use cryptographic assumptions when needed

Production systems work **around** these impossibilities, not through them. The implementations above show practical patterns used in systems like:

- **Cassandra**: Quorum reads/writes with tunable consistency
- **DynamoDB**: Eventually consistent with strong consistency options  
- **Ethereum**: Practical Byzantine fault tolerance with economic incentives
- **Raft**: Randomized timeouts to work around FLP impossibility
- **CRDTs**: Eventually consistent data structures for partition tolerance

The mathematical impossibility results provide clarity about what's achievable and guide us toward practical engineering solutions that acknowledge fundamental limits while still providing useful guarantees.

---

*This completes the 60-minute implementation section focusing on practical workarounds for theoretical impossibilities in distributed systems.*