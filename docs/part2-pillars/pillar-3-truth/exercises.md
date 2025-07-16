# Truth Distribution Exercises

!!! info "Prerequisites"
    - Completed [Truth Distribution Concepts](index.md)
    - Reviewed [Truth Distribution Examples](examples.md)
    - Understanding of consensus algorithms

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Pillars Overview](../index.md) |
    [→ Next: Distribution of Control](../pillar-4-control/index.md)

## Exercise 1: Implement a Basic Paxos

### Objective
Build a simplified Paxos implementation to understand consensus fundamentals.

### Requirements
- Support propose/accept phases
- Handle multiple proposers
- Ensure safety (only one value chosen)
- Support basic failure scenarios

### Starter Implementation
```python
from dataclasses import dataclass
from typing import Optional, Dict, Set
import time

@dataclass
class Proposal:
    number: int
    value: any

class PaxosNode:
    def __init__(self, node_id: str, all_nodes: Set[str]):
        self.node_id = node_id
        self.all_nodes = all_nodes
        
        # Proposer state
        self.proposal_number = 0
        
        # Acceptor state
        self.promised_proposal: Optional[int] = None
        self.accepted_proposal: Optional[Proposal] = None
        
    def propose(self, value: any) -> bool:
        """Try to get a value accepted"""
        # Phase 1: Prepare
        self.proposal_number += 1
        proposal_num = self.proposal_number
        
        # Send prepare to all acceptors
        promises = self._send_prepare(proposal_num)
        
        # Need majority
        if len(promises) <= len(self.all_nodes) // 2:
            return False
            
        # Find highest numbered accepted proposal
        highest_accepted = None
        for promise in promises:
            if promise['accepted'] and (
                not highest_accepted or 
                promise['accepted'].number > highest_accepted.number
            ):
                highest_accepted = promise['accepted']
                
        # Phase 2: Accept
        if highest_accepted:
            # Must propose the already accepted value
            propose_value = highest_accepted.value
        else:
            # Can propose our value
            propose_value = value
            
        proposal = Proposal(proposal_num, propose_value)
        accepts = self._send_accept(proposal)
        
        # Need majority to accept
        return len(accepts) > len(self.all_nodes) // 2
        
    def handle_prepare(self, proposal_number: int) -> Dict:
        """Handle prepare request as acceptor"""
        # TODO: Implement prepare phase logic
        # - Check if can promise
        # - Return promise with any accepted value
        pass
        
    def handle_accept(self, proposal: Proposal) -> bool:
        """Handle accept request as acceptor"""
        # TODO: Implement accept phase logic
        # - Check if promised to higher proposal
        # - Accept if valid
        pass
        
    def _send_prepare(self, proposal_number: int) -> list:
        """Simulate sending prepare to all nodes"""
        promises = []
        for node_id in self.all_nodes:
            # Simulate network call
            # In reality, this would be RPC
            response = self._simulate_prepare_response(node_id, proposal_number)
            if response['promised']:
                promises.append(response)
        return promises
        
    def _send_accept(self, proposal: Proposal) -> list:
        """Simulate sending accept to all nodes"""
        # TODO: Implement accept phase communication
        pass

# Test your Paxos implementation
nodes = {f"node{i}": PaxosNode(f"node{i}", set()) for i in range(5)}
for node in nodes.values():
    node.all_nodes = set(nodes.keys())

# Multiple proposers trying to propose different values
result1 = nodes["node1"].propose("value_A")
result2 = nodes["node2"].propose("value_B")

# Only one should succeed, or both should agree on same value
```

### Expected Behavior
- Multiple concurrent proposals should converge
- Once a value is chosen, it cannot change
- System makes progress if majority is available

## Exercise 2: Build a Raft Log Replication

### Objective
Implement Raft's log replication mechanism with leader election.

### Requirements
- Leader election with randomized timeouts
- Log replication with consistency checks
- Commit when majority replicates
- Handle leader failures

### Complete Implementation Framework
```python
import asyncio
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class NodeState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

@dataclass
class LogEntry:
    term: int
    index: int
    command: any

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state = NodeState.FOLLOWER
        
        # Persistent state (survives restart)
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        
        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        self.leader_id: Optional[str] = None
        
        # Leader only state
        self.next_index = {peer: 1 for peer in peers}
        self.match_index = {peer: 0 for peer in peers}
        
        # Election state
        self.election_timeout = None
        self.reset_election_timer()
        
    def reset_election_timer(self):
        """Reset election timeout to random value"""
        self.election_timeout = random.uniform(150, 300)  # milliseconds
        self.last_heartbeat = asyncio.get_event_loop().time()
        
    async def run(self):
        """Main node loop"""
        while True:
            if self.state == NodeState.LEADER:
                # Send heartbeats
                await self.send_heartbeats()
                await asyncio.sleep(0.05)  # 50ms heartbeat interval
            else:
                # Check election timeout
                elapsed = asyncio.get_event_loop().time() - self.last_heartbeat
                if elapsed * 1000 > self.election_timeout:
                    await self.start_election()
                await asyncio.sleep(0.01)
                
    async def start_election(self):
        """Start leader election"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.reset_election_timer()
        
        print(f"{self.node_id} starting election for term {self.current_term}")
        
        # Request votes in parallel
        votes = 1  # Vote for self
        vote_tasks = []
        
        for peer in self.peers:
            task = asyncio.create_task(self.request_vote(peer))
            vote_tasks.append(task)
            
        # Wait for responses
        responses = await asyncio.gather(*vote_tasks, return_exceptions=True)
        
        for response in responses:
            if isinstance(response, dict) and response.get('vote_granted'):
                votes += 1
                
        # Check if won
        if votes > (len(self.peers) + 1) // 2:
            await self.become_leader()
        else:
            self.state = NodeState.FOLLOWER
            
    async def become_leader(self):
        """Transition to leader"""
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        
        # Reinitialize leader state
        for peer in self.peers:
            self.next_index[peer] = len(self.log) + 1
            self.match_index[peer] = 0
            
        print(f"{self.node_id} became leader for term {self.current_term}")
        
        # Send initial empty AppendEntries
        await self.send_heartbeats()
        
    async def send_heartbeats(self):
        """Send heartbeats/log entries to all followers"""
        tasks = []
        for peer in self.peers:
            task = asyncio.create_task(self.send_append_entries(peer))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def send_append_entries(self, peer: str) -> bool:
        """Send AppendEntries RPC to peer"""
        # TODO: Implement log replication logic
        # - Include new entries if any
        # - Handle response
        # - Update match_index and next_index
        pass
        
    async def request_vote(self, peer: str) -> dict:
        """Request vote from peer"""
        # TODO: Implement RequestVote RPC
        pass
        
    async def handle_append_entries(self, request: dict) -> dict:
        """Handle incoming AppendEntries"""
        # TODO: Implement follower logic
        # - Check term
        # - Verify log consistency
        # - Append new entries
        # - Update commit index
        pass
        
    async def replicate_command(self, command: any) -> bool:
        """Replicate a command (leader only)"""
        if self.state != NodeState.LEADER:
            return False
            
        # Append to own log
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command=command
        )
        self.log.append(entry)
        
        # Replicate to followers
        # TODO: Send to all followers and wait for majority
        
        return True

# Create a cluster
async def run_cluster():
    nodes = {}
    node_ids = ['node1', 'node2', 'node3', 'node4', 'node5']
    
    for node_id in node_ids:
        peers = [n for n in node_ids if n != node_id]
        nodes[node_id] = RaftNode(node_id, peers)
        
    # Run all nodes
    tasks = [node.run() for node in nodes.values()]
    await asyncio.gather(*tasks)

# Test election and replication
# asyncio.run(run_cluster())
```

## Exercise 3: Implement Vector Clocks with Conflict Detection

### Objective
Build a distributed key-value store using vector clocks for conflict detection.

### Requirements
- Track causality between updates
- Detect concurrent updates
- Provide conflict resolution API
- Support node failures/additions

### Implementation
```python
from typing import Dict, List, Tuple, Optional, Callable

class VectorClockStore:
    def __init__(self, node_id: str, conflict_resolver: Optional[Callable] = None):
        self.node_id = node_id
        self.clock = VectorClock(node_id)
        self.store: Dict[str, List[VersionedValue]] = {}
        self.conflict_resolver = conflict_resolver or self._default_resolver
        
    def put(self, key: str, value: any, context: Optional[VectorClock] = None):
        """Write with causality tracking"""
        # Increment clock
        self.clock.increment()
        
        if context:
            # This is an update based on previous read
            self.clock.update_from(context)
            
        versioned = VersionedValue(
            value=value,
            clock=self.clock.copy(),
            node_id=self.node_id
        )
        
        if key not in self.store:
            self.store[key] = [versioned]
        else:
            # Remove causally dominated versions
            self._prune_dominated(key, versioned)
            self.store[key].append(versioned)
            
    def get(self, key: str) -> Tuple[any, VectorClock]:
        """Read with conflict detection"""
        if key not in self.store:
            return (None, VectorClock(self.node_id))
            
        versions = self.store[key]
        
        if len(versions) == 1:
            # No conflicts
            return (versions[0].value, versions[0].clock)
        else:
            # Multiple versions - conflict!
            resolved = self.conflict_resolver(key, versions)
            # Replace with resolved version
            self.store[key] = [resolved]
            return (resolved.value, resolved.clock)
            
    def _prune_dominated(self, key: str, new_version: VersionedValue):
        """Remove versions that are causally dominated"""
        remaining = []
        
        for existing in self.store[key]:
            relation = existing.clock.compare(new_version.clock)
            if relation != "happens-before":
                # Keep if concurrent or happens-after
                remaining.append(existing)
                
        self.store[key] = remaining
        
    def _default_resolver(self, key: str, versions: List[VersionedValue]):
        """Default conflict resolution - merge all values"""
        merged_values = [v.value for v in versions]
        merged_clock = versions[0].clock.copy()
        
        for v in versions[1:]:
            merged_clock.merge(v.clock)
            
        return VersionedValue(
            value={'conflict': True, 'values': merged_values},
            clock=merged_clock,
            node_id=self.node_id
        )
        
    def sync_with(self, other: 'VectorClockStore'):
        """Synchronize with another node"""
        # Exchange all data
        for key in set(self.store.keys()) | set(other.store.keys()):
            if key in self.store and key in other.store:
                # Merge versions from both sides
                all_versions = self.store[key] + other.store[key]
                # Remove dominated versions
                unique_versions = self._find_concurrent_versions(all_versions)
                self.store[key] = unique_versions
                other.store[key] = unique_versions.copy()
            elif key in other.store:
                # Copy from other
                self.store[key] = other.store[key].copy()
            else:
                # Copy to other
                other.store[key] = self.store[key].copy()
                
    def _find_concurrent_versions(self, versions: List[VersionedValue]):
        """Find all concurrent (non-dominated) versions"""
        # TODO: Implement algorithm to find minimal set
        # of concurrent versions
        pass

# Test concurrent updates
store1 = VectorClockStore("node1")
store2 = VectorClockStore("node2")

# Concurrent updates to same key
store1.put("config", {"theme": "dark"})
store2.put("config", {"theme": "light"})

# Sync and detect conflict
store1.sync_with(store2)

# Both nodes see conflict
print(store1.get("config"))  # Shows conflict
print(store2.get("config"))  # Shows conflict
```

## Exercise 4: Build a CRDT-based Collaborative Editor

### Objective
Implement a collaborative text editor using CRDTs for automatic conflict resolution.

### Requirements
- Support concurrent edits without conflicts
- Automatic merging of changes
- Preserve user intentions
- Handle offline edits

### CRDT Text Editor
```python
from dataclasses import dataclass
from typing import List, Tuple, Optional
import uuid

@dataclass
class CharacterID:
    """Unique ID for each character"""
    position: List[int]  # Position in tree
    site_id: str        # Node that created it
    
    def __lt__(self, other):
        # Compare positions element by element
        for i in range(min(len(self.position), len(other.position))):
            if self.position[i] != other.position[i]:
                return self.position[i] < other.position[i]
        
        # If equal so far, shorter position comes first
        if len(self.position) != len(other.position):
            return len(self.position) < len(other.position)
            
        # If positions equal, compare site IDs
        return self.site_id < other.site_id

@dataclass
class Character:
    id: CharacterID
    value: str
    visible: bool = True

class CRDTDocument:
    def __init__(self, site_id: str):
        self.site_id = site_id
        self.characters: List[Character] = []
        self.counter = 0
        
    def insert(self, index: int, char: str):
        """Insert character at index"""
        # Generate position between neighbors
        left_pos = self._get_position(index - 1) if index > 0 else []
        right_pos = self._get_position(index) if index < len(self.text()) else []
        
        new_pos = self._generate_position_between(left_pos, right_pos)
        
        char_id = CharacterID(new_pos, self.site_id)
        character = Character(char_id, char)
        
        # Insert in sorted order
        self._insert_character(character)
        
        # Return operation for replication
        return {
            'type': 'insert',
            'character': character
        }
        
    def delete(self, index: int):
        """Delete character at index"""
        visible_chars = [c for c in self.characters if c.visible]
        if 0 <= index < len(visible_chars):
            char_to_delete = visible_chars[index]
            char_to_delete.visible = False
            
            # Return operation for replication
            return {
                'type': 'delete',
                'char_id': char_to_delete.id
            }
            
    def apply_operation(self, operation: dict):
        """Apply remote operation"""
        if operation['type'] == 'insert':
            self._insert_character(operation['character'])
        elif operation['type'] == 'delete':
            self._delete_by_id(operation['char_id'])
            
    def _insert_character(self, character: Character):
        """Insert character maintaining sorted order"""
        # Binary search for insertion point
        left, right = 0, len(self.characters)
        while left < right:
            mid = (left + right) // 2
            if self.characters[mid].id < character.id:
                left = mid + 1
            else:
                right = mid
        self.characters.insert(left, character)
        
    def _delete_by_id(self, char_id: CharacterID):
        """Mark character as deleted"""
        for char in self.characters:
            if char.id == char_id:
                char.visible = False
                break
                
    def _generate_position_between(self, left: List[int], right: List[int]):
        """Generate position between two positions"""
        # TODO: Implement position generation algorithm
        # This is the key to CRDT correctness
        pass
        
    def text(self) -> str:
        """Get current document text"""
        return ''.join(c.value for c in self.characters if c.visible)
        
    def merge(self, other: 'CRDTDocument'):
        """Merge another document"""
        # Combine all characters
        all_chars = {}
        
        # Add our characters
        for char in self.characters:
            all_chars[char.id] = char
            
        # Add their characters
        for char in other.characters:
            if char.id in all_chars:
                # Same character - take deleted state if any
                if not char.visible:
                    all_chars[char.id].visible = False
            else:
                all_chars[char.id] = char
                
        # Sort and store
        self.characters = sorted(all_chars.values(), key=lambda c: c.id)

# Test collaborative editing
doc1 = CRDTDocument("user1")
doc2 = CRDTDocument("user2")

# User 1 types "Hello"
ops1 = []
for i, char in enumerate("Hello"):
    op = doc1.insert(i, char)
    ops1.append(op)

# User 2 types "World"
ops2 = []
for i, char in enumerate("World"):
    op = doc2.insert(i, char)
    ops2.append(op)

# Exchange operations
for op in ops1:
    doc2.apply_operation(op)
for op in ops2:
    doc1.apply_operation(op)

# Both should have same merged text
print(f"Doc1: {doc1.text()}")
print(f"Doc2: {doc2.text()}")
```

## Exercise 5: Implement Byzantine Fault Tolerant Consensus

### Objective
Build a simplified PBFT (Practical Byzantine Fault Tolerance) system.

### Requirements
- Tolerate f Byzantine failures with 3f+1 nodes
- Three-phase protocol (pre-prepare, prepare, commit)
- View changes for faulty primary
- Message authentication

### Byzantine Consensus Implementation
```python
from cryptography.hazmat.primitives import hashes, hmac
from dataclasses import dataclass
from enum import Enum
import json

class MessageType(Enum):
    PRE_PREPARE = "pre-prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    VIEW_CHANGE = "view-change"

@dataclass
class Message:
    type: MessageType
    view: int
    sequence: int
    digest: str
    node_id: str
    signature: str

class PBFTNode:
    def __init__(self, node_id: str, nodes: List[str], f: int):
        self.node_id = node_id
        self.nodes = nodes
        self.f = f  # Number of faulty nodes to tolerate
        self.view = 0
        self.sequence = 0
        self.is_primary = (self.view % len(nodes)) == nodes.index(node_id)
        
        # Message logs
        self.pre_prepare_log = {}
        self.prepare_log = defaultdict(set)
        self.commit_log = defaultdict(set)
        
        # State
        self.prepared = set()
        self.committed = set()
        
    def request(self, operation: any):
        """Client request - only primary processes"""
        if not self.is_primary:
            # Forward to primary or return error
            return False
            
        # Create pre-prepare message
        self.sequence += 1
        digest = self._compute_digest(operation)
        
        message = Message(
            type=MessageType.PRE_PREPARE,
            view=self.view,
            sequence=self.sequence,
            digest=digest,
            node_id=self.node_id,
            signature=self._sign(digest)
        )
        
        # Log and broadcast
        self.pre_prepare_log[(self.view, self.sequence)] = message
        self._broadcast(message)
        
        # Also send prepare as non-primary would
        self._send_prepare(self.view, self.sequence, digest)
        
    def handle_pre_prepare(self, message: Message):
        """Handle pre-prepare from primary"""
        # Verify primary sent it
        expected_primary = self.nodes[self.view % len(self.nodes)]
        if message.node_id != expected_primary:
            return
            
        # Verify signature
        if not self._verify_signature(message):
            return
            
        # Check not already accepted different pre-prepare
        key = (message.view, message.sequence)
        if key in self.pre_prepare_log:
            if self.pre_prepare_log[key].digest != message.digest:
                # Conflicting pre-prepare - Byzantine primary!
                self._initiate_view_change()
                return
        else:
            self.pre_prepare_log[key] = message
            
        # Send prepare
        self._send_prepare(message.view, message.sequence, message.digest)
        
    def _send_prepare(self, view: int, sequence: int, digest: str):
        """Send prepare message"""
        message = Message(
            type=MessageType.PREPARE,
            view=view,
            sequence=sequence,
            digest=digest,
            node_id=self.node_id,
            signature=self._sign(digest)
        )
        
        self._broadcast(message)
        # Also log our own prepare
        self.prepare_log[(view, sequence)].add(self.node_id)
        
    def handle_prepare(self, message: Message):
        """Handle prepare message"""
        # TODO: Implement prepare phase
        # - Verify message
        # - Log prepare
        # - Check if prepared (2f prepares)
        # - Send commit if prepared
        pass
        
    def handle_commit(self, message: Message):
        """Handle commit message"""
        # TODO: Implement commit phase
        # - Verify message
        # - Log commit
        # - Check if committed (2f+1 commits)
        # - Execute operation if committed
        pass
        
    def _initiate_view_change(self):
        """Start view change protocol"""
        # TODO: Implement view change
        # - Increment view
        # - Send view-change message
        # - Collect view-change messages
        # - Become primary if appropriate
        pass

# Test Byzantine consensus
nodes = [f"node{i}" for i in range(4)]  # 3f+1 with f=1
pbft_nodes = {}

for node_id in nodes:
    pbft_nodes[node_id] = PBFTNode(node_id, nodes, f=1)

# Client request to primary
primary = pbft_nodes["node0"]
primary.request({"action": "transfer", "amount": 100})

# Simulate Byzantine node behavior
byzantine_node = pbft_nodes["node3"]
# Byzantine node could:
# - Send conflicting messages
# - Not respond
# - Send invalid signatures
```

## Project: Build a Distributed Lock Manager

### Objective
Design and implement a distributed lock manager with strong consistency.

### Requirements
1. **Mutual exclusion** - Only one holder per lock
2. **Deadlock detection** - Detect and resolve deadlocks
3. **Fault tolerance** - Survive node failures
4. **Fair queuing** - FIFO lock acquisition
5. **Lock expiration** - Prevent permanent locks

### System Design
```python
class DistributedLockManager:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.locks = {}  # lock_id -> LockInfo
        self.lock_queues = defaultdict(deque)  # lock_id -> waiting clients
        self.client_locks = defaultdict(set)  # client_id -> held locks
        
        # Use Raft for consensus
        self.raft = RaftNode(node_id, peers)
        
    async def acquire(self, client_id: str, lock_id: str, 
                     timeout: Optional[float] = None) -> bool:
        """Acquire a lock"""
        # Check if already held
        if lock_id in self.locks:
            current_holder = self.locks[lock_id].holder
            if current_holder == client_id:
                # Reentrant lock
                self.locks[lock_id].count += 1
                return True
            else:
                # Add to wait queue
                self.lock_queues[lock_id].append({
                    'client_id': client_id,
                    'timestamp': time.time(),
                    'timeout': timeout
                })
                
                # Check for deadlock
                if self._detect_deadlock(client_id, lock_id):
                    # Implement deadlock resolution
                    pass
                    
                return False
        else:
            # Grant lock
            self._grant_lock(client_id, lock_id, timeout)
            return True
            
    def _detect_deadlock(self, client_id: str, requested_lock: str) -> bool:
        """Detect deadlock using wait-for graph"""
        # Build wait-for graph
        # Check for cycles
        # TODO: Implement cycle detection
        pass
        
    def _grant_lock(self, client_id: str, lock_id: str, 
                    timeout: Optional[float]):
        """Grant lock to client"""
        # TODO: Replicate through Raft
        pass

# Implement the complete lock manager with:
# - Raft-based replication
# - Deadlock detection algorithm
# - Lock expiration handling
# - Client failure detection
# - Performance optimizations
```

### Evaluation Criteria
- Correctness under concurrent access
- Performance (locks/second)
- Fault tolerance (node failures)
- Deadlock handling
- Fair scheduling

## Reflection Questions

After completing exercises:

1. **Consensus Trade-offs**: When is strong consistency worth the cost?

2. **Byzantine vs Crash Failures**: How does Byzantine tolerance change the design?

3. **CRDT Limitations**: What operations cannot be expressed as CRDTs?

4. **Clock Assumptions**: How do your algorithms handle clock skew?

5. **Scalability**: How do consensus protocols scale with node count?

## Navigation

!!! tip "Continue Learning"
    
    **Next Pillar**: [Distribution of Control](../pillar-4-control/index.md) →
    
    **Related Topics**: [Coordination](../../part1-axioms/axiom-5-coordination/index.md) | [State Distribution](../pillar-2-state/index.md)
    
    **Back to**: [Pillars Overview](../index.md)