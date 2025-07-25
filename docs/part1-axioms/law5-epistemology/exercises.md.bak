# Exercises: The Law of Distributed Knowledge

## Overview

These exercises will help you understand how knowledge is distributed across systems and how nodes reach consensus despite partial information. You'll implement fundamental distributed algorithms and data structures.

## Exercise 1: Byzantine Generals Protocol

### Background
The Byzantine Generals Problem illustrates the challenge of reaching consensus in a distributed system where some nodes may be faulty or malicious.

### Task
Implement a simple Byzantine Generals protocol where generals must agree on whether to attack or retreat.

```python
import random
from typing import List, Dict, Tuple
from collections import defaultdict

class General:
    def __init__(self, id: int, is_traitor: bool = False):
        self.id = id
        self.is_traitor = is_traitor
        self.received_messages = defaultdict(list)
        
    def send_order(self, order: str, recipients: List['General']):
        """Commander sends initial order to all lieutenants"""
        for recipient in recipients:
            if self.is_traitor:
# Traitor sends conflicting orders
                conflicting_order = "retreat" if order == "attack" else "attack"
                order_to_send = random.choice([order, conflicting_order])
            else:
                order_to_send = order
            recipient.receive_order(self.id, order_to_send)
    
    def receive_order(self, sender_id: int, order: str):
        """Receive an order from another general"""
        self.received_messages[sender_id].append(order)
    
    def relay_orders(self, recipients: List['General']):
        """Relay received orders to other generals"""
        for sender_id, orders in self.received_messages.items():
            for recipient in recipients:
                if recipient.id != self.id and recipient.id != sender_id:
                    for order in orders:
                        if self.is_traitor:
# Traitor may corrupt the message
                            order_to_relay = random.choice(["attack", "retreat"])
                        else:
                            order_to_relay = order
                        recipient.receive_order(sender_id, order_to_relay)
    
    def decide(self) -> str:
        """Make a decision based on received messages"""
        all_orders = []
        for orders in self.received_messages.values():
            all_orders.extend(orders)
        
        if not all_orders:
            return "retreat"  # Default to safe option
        
# Use majority voting
        attack_count = all_orders.count("attack")
        retreat_count = all_orders.count("retreat")
        
        return "attack" if attack_count > retreat_count else "retreat"

def byzantine_generals_protocol(num_generals: int, num_traitors: int) -> Dict[int, str]:
    """
    Simulate Byzantine Generals Protocol
    
    TODO: Complete this implementation
    1. Create generals (including traitors)
    2. Commander sends initial order
    3. Lieutenants relay orders to each other
    4. Each lieutenant makes a decision
    5. Return the decisions of all loyal generals
    """
# Your implementation here
    pass

# Test your implementation
def test_byzantine_generals():
# Test case 1: 4 generals, 1 traitor
    decisions = byzantine_generals_protocol(4, 1)
    print(f"4 generals, 1 traitor: {decisions}")
    
# Test case 2: 7 generals, 2 traitors
    decisions = byzantine_generals_protocol(7, 2)
    print(f"7 generals, 2 traitors: {decisions}")
    
# Verify consensus among loyal generals
# TODO: Add assertions to verify correctness

if __name__ == "__main__":
    test_byzantine_generals()
```

### Questions
1. What is the minimum number of generals needed to tolerate `f` traitors?
2. How does message complexity grow with the number of generals?
3. What happens if network messages can be lost or delayed?

## Exercise 2: Building CRDTs (Conflict-free Replicated Data Types)

### Task A: Implement a G-Counter (Grow-only Counter)

```python
from typing import Dict, Set
import copy

class GCounter:
    """
    A grow-only counter CRDT that can only increment
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: Dict[str, int] = {node_id: 0}
    
    def increment(self, value: int = 1):
        """Increment the counter for this node"""
        if value < 0:
            raise ValueError("G-Counter can only grow")
        self.counts[self.node_id] += value
    
    def value(self) -> int:
        """Get the current value of the counter"""
        return sum(self.counts.values())
    
    def merge(self, other: 'GCounter'):
        """Merge another G-Counter into this one"""
# TODO: Implement merge operation
# Hint: Take the maximum count for each node
        pass
    
    def __repr__(self):
        return f"GCounter({self.node_id}: {self.counts})"

# Test your G-Counter implementation
def test_g_counter():
# Create counters for different nodes
    counter_a = GCounter("A")
    counter_b = GCounter("B")
    counter_c = GCounter("C")
    
# Simulate concurrent increments
    counter_a.increment(5)
    counter_b.increment(3)
    counter_c.increment(2)
    
# Simulate network partitions and merges
# TODO: Test merge operations and verify convergence
    
    print(f"Counter A: {counter_a.value()}")
    print(f"Counter B: {counter_b.value()}")
    print(f"Counter C: {counter_c.value()}")
```

### Task B: Implement a PN-Counter (Positive-Negative Counter)

```python
class PNCounter:
    """
    A counter CRDT that supports both increment and decrement
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.p_counter = GCounter(node_id)  # Positive counter
        self.n_counter = GCounter(node_id)  # Negative counter
    
    def increment(self, value: int = 1):
        """Increment the counter"""
        if value < 0:
            raise ValueError("Use decrement for negative values")
# TODO: Implement increment
        pass
    
    def decrement(self, value: int = 1):
        """Decrement the counter"""
        if value < 0:
            raise ValueError("Use increment for negative values")
# TODO: Implement decrement
        pass
    
    def value(self) -> int:
        """Get the current value of the counter"""
# TODO: Calculate value from p_counter and n_counter
        pass
    
    def merge(self, other: 'PNCounter'):
        """Merge another PN-Counter into this one"""
# TODO: Implement merge operation
        pass

# Test your PN-Counter implementation
def test_pn_counter():
# Create counters for different nodes
    counter_a = PNCounter("A")
    counter_b = PNCounter("B")
    
# Test increment and decrement
    counter_a.increment(10)
    counter_a.decrement(3)
    counter_b.increment(5)
    counter_b.decrement(7)
    
# Test merge and convergence
# TODO: Complete the test
```

### Task C: Implement an OR-Set (Observed-Remove Set)

```python
import uuid
from typing import Set, Tuple, Any

class ORSet:
    """
    An OR-Set CRDT that supports concurrent add and remove operations
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.elements: Set[Tuple[Any, str]] = set()  # (element, unique_id)
        self.tombstones: Set[Tuple[Any, str]] = set()  # Removed elements
    
    def add(self, element: Any):
        """Add an element to the set"""
        unique_id = f"{self.node_id}:{uuid.uuid4()}"
# TODO: Implement add operation
        pass
    
    def remove(self, element: Any):
        """Remove an element from the set"""
# TODO: Implement remove operation
# Hint: Move all instances of element to tombstones
        pass
    
    def contains(self, element: Any) -> bool:
        """Check if element is in the set"""
# TODO: Implement contains check
        pass
    
    def values(self) -> Set[Any]:
        """Get all elements currently in the set"""
# TODO: Return unique elements not in tombstones
        pass
    
    def merge(self, other: 'ORSet'):
        """Merge another OR-Set into this one"""
# TODO: Implement merge operation
# Hint: Union elements, union tombstones, then apply tombstones
        pass

# Test your OR-Set implementation
def test_or_set():
    set_a = ORSet("A")
    set_b = ORSet("B")
    
# Concurrent adds
    set_a.add("apple")
    set_b.add("apple")
    set_b.add("banana")
    
# Concurrent add/remove
    set_a.remove("apple")
    set_b.add("apple")  # This should win (add-wins semantics)
    
# Test merge and convergence
# TODO: Complete the test
```

## Exercise 3: Distributed Consensus Simulator

### Task
Build a simple Raft consensus simulator to understand leader election and log replication.

```python
import time
import random
from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass

class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

@dataclass
class LogEntry:
    term: int
    command: str
    index: int

class RaftNode:
    def __init__(self, node_id: int, peers: List[int]):
        self.node_id = node_id
        self.peers = peers
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(0.15, 0.3)
        self.votes_received = 0
        
    def start_election(self):
        """Start a new election"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1  # Vote for self
        
# TODO: Request votes from peers
        print(f"Node {self.node_id}: Starting election for term {self.current_term}")
    
    def request_vote(self, candidate_id: int, term: int, 
                    last_log_index: int, last_log_term: int) -> Tuple[int, bool]:
        """Handle vote request from candidate"""
# TODO: Implement vote request handling
# Consider:
# 1. Is the term valid?
# 2. Have we already voted in this term?
# 3. Is the candidate's log at least as up-to-date as ours?
        pass
    
    def append_entries(self, term: int, leader_id: int, prev_log_index: int,
                      prev_log_term: int, entries: List[LogEntry], 
                      leader_commit: int) -> Tuple[int, bool]:
        """Handle append entries RPC from leader"""
# TODO: Implement log replication
# Consider:
# 1. Is the term valid?
# 2. Does our log match at prev_log_index?
# 3. How to handle conflicts?
        pass
    
    def tick(self):
        """Process one time unit"""
        current_time = time.time()
        
        if self.state == NodeState.FOLLOWER:
# Check for election timeout
            if current_time - self.last_heartbeat > self.election_timeout:
                self.start_election()
        
        elif self.state == NodeState.CANDIDATE:
# TODO: Handle election timeout and retry
            pass
        
        elif self.state == NodeState.LEADER:
# TODO: Send periodic heartbeats
            pass

def simulate_raft_cluster(num_nodes: int, duration: float):
    """
    Simulate a Raft cluster
    
    TODO: Complete this simulation
    1. Create nodes
    2. Simulate network communication
    3. Inject failures and partitions
    4. Verify safety properties (only one leader per term)
    5. Verify liveness properties (eventually elects a leader)
    """
    nodes = []
    for i in range(num_nodes):
        peers = [j for j in range(num_nodes) if j != i]
        nodes.append(RaftNode(i, peers))
    
# Run simulation
    start_time = time.time()
    while time.time() - start_time < duration:
        for node in nodes:
            node.tick()
        time.sleep(0.01)  # Small delay
    
# Analyze results
# TODO: Print statistics about elections, leaders, etc.

# Test your implementation
if __name__ == "__main__":
    simulate_raft_cluster(5, 10.0)  # 5 nodes for 10 seconds
```

## Exercise 4: Gossip Protocol Implementation

### Task
Implement a gossip protocol for information dissemination in a distributed system.

```python
import random
import time
from typing import Set, Dict, Any, List
from dataclasses import dataclass

@dataclass
class GossipMessage:
    node_id: str
    data: Any
    version: int
    timestamp: float

class GossipNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state: Dict[str, GossipMessage] = {}
        self.version_vector: Dict[str, int] = {node_id: 0}
        self.fanout = 3  # Number of peers to gossip to
        self.gossip_interval = 0.5  # seconds
        
    def update_local_state(self, key: str, value: Any):
        """Update local state and increment version"""
        self.version_vector[self.node_id] += 1
        self.state[key] = GossipMessage(
            node_id=self.node_id,
            data=value,
            version=self.version_vector[self.node_id],
            timestamp=time.time()
        )
    
    def select_gossip_targets(self) -> List[str]:
        """Select random peers for gossip"""
# TODO: Implement peer selection
# Consider: random selection, round-robin, or weighted by staleness
        pass
    
    def create_gossip_payload(self) -> Dict[str, Any]:
        """Create payload to send to peers"""
# TODO: Create efficient gossip payload
# Include: state updates, version vector
        pass
    
    def receive_gossip(self, sender_id: str, payload: Dict[str, Any]):
        """Process received gossip message"""
# TODO: Implement gossip reception
# Consider:
# 1. How to detect and handle newer information?
# 2. How to merge version vectors?
# 3. How to handle conflicts?
        pass
    
    def anti_entropy(self, peer_id: str):
        """Perform anti-entropy with a specific peer"""
# TODO: Implement anti-entropy protocol
# Exchange version vectors and sync missing updates
        pass

def simulate_gossip_protocol():
    """
    Simulate information spread through gossip
    
    TODO: Complete this simulation
    1. Create a network of gossip nodes
    2. Inject information at random nodes
    3. Measure convergence time
    4. Simulate network partitions and healing
    """
# Create nodes
    num_nodes = 10
    nodes = {}
    node_ids = [f"node_{i}" for i in range(num_nodes)]
    
    for node_id in node_ids:
        peers = [id for id in node_ids if id != node_id]
        nodes[node_id] = GossipNode(node_id, peers)
    
# Inject some data
    nodes["node_0"].update_local_state("config", {"replicas": 3})
    nodes["node_5"].update_local_state("status", "healthy")
    
# Run gossip rounds
# TODO: Implement gossip rounds and measure convergence
    
# Verify eventual consistency
# TODO: Check that all nodes eventually have the same state

# Test your implementation
if __name__ == "__main__":
    simulate_gossip_protocol()
```

## Exercise 5: Simple Blockchain Implementation

### Task
Build a simple blockchain to understand distributed consensus and cryptographic linking.

```python
import hashlib
import json
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: float

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """Calculate the hash of this block"""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [asdict(t) for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine(self, difficulty: int):
        """Mine the block with proof-of-work"""
# TODO: Implement mining algorithm
# Find nonce such that hash starts with 'difficulty' zeros
        pass

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = 100.0
        
# Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0"
        )
        genesis.hash = genesis.calculate_hash()
        self.chain.append(genesis)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        """Add a transaction to pending transactions"""
# TODO: Validate transaction before adding
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self, mining_reward_address: str):
        """Mine a new block with pending transactions"""
# TODO: Implement mining process
# 1. Create reward transaction
# 2. Create new block with pending transactions
# 3. Mine the block
# 4. Add to chain and clear pending transactions
        pass
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
# TODO: Implement chain validation
# Check:
# 1. Each block's hash is correct
# 2. Previous hash links are valid
# 3. Proof-of-work is valid
        pass
    
    def get_balance(self, address: str) -> float:
        """Calculate balance for an address"""
# TODO: Scan all transactions to calculate balance
        pass

class DistributedBlockchain(Blockchain):
    """Extended blockchain with network consensus"""
    
    def __init__(self, node_id: str, difficulty: int = 4):
        super().__init__(difficulty)
        self.node_id = node_id
        self.peers: List['DistributedBlockchain'] = []
    
    def add_peer(self, peer: 'DistributedBlockchain'):
        """Add a peer node"""
        self.peers.append(peer)
    
    def broadcast_block(self, block: Block):
        """Broadcast a new block to all peers"""
# TODO: Implement block broadcasting
        pass
    
    def receive_block(self, block: Block, sender_id: str):
        """Receive a block from a peer"""
# TODO: Validate and add block
# Handle fork resolution if necessary
        pass
    
    def consensus(self):
        """Achieve consensus with peers (longest chain rule)"""
# TODO: Implement consensus algorithm
# 1. Query all peers for their chains
# 2. Validate received chains
# 3. Replace chain if a longer valid chain is found
        pass

# Test your implementation
def test_blockchain():
# Create a simple blockchain
    blockchain = Blockchain(difficulty=4)
    
# Add some transactions
    blockchain.add_transaction(Transaction("Alice", "Bob", 50, time.time()))
    blockchain.add_transaction(Transaction("Bob", "Charlie", 25, time.time()))
    
# Mine a block
    print("Mining block...")
    blockchain.mine_pending_transactions("Miner1")
    
# Validate the chain
    print(f"Is chain valid? {blockchain.validate_chain()}")
    
# Test distributed blockchain
    node1 = DistributedBlockchain("Node1", difficulty=4)
    node2 = DistributedBlockchain("Node2", difficulty=4)
    node3 = DistributedBlockchain("Node3", difficulty=4)
    
# Connect nodes
    node1.add_peer(node2)
    node1.add_peer(node3)
    node2.add_peer(node1)
    node2.add_peer(node3)
    node3.add_peer(node1)
    node3.add_peer(node2)
    
# Simulate concurrent mining and consensus
# TODO: Complete the distributed test

if __name__ == "__main__":
    test_blockchain()
```

## Synthesis Questions

After completing these exercises, consider these questions:

1. **Partial Knowledge**: How do systems make decisions with incomplete information? Compare the approaches in Byzantine Generals vs. Raft consensus.

2. **Eventual Consistency**: How do CRDTs guarantee convergence? What are the trade-offs between strong and eventual consistency?

3. **Consensus Performance**: What factors affect consensus latency? How does the number of nodes impact performance?

4. **Failure Handling**: How do these protocols handle different types of failures (crash, Byzantine, network partition)?

5. **Scalability**: Which approaches scale better? Compare gossip protocols vs. consensus protocols for different use cases.

## Advanced Challenges

1. **Hybrid Approaches**: Combine CRDTs with consensus for a hybrid consistency model.

2. **Network Simulation**: Add realistic network delays and partitions to your simulations.

3. **Visualization**: Create visualizations showing how knowledge propagates through the system.

4. **Performance Analysis**: Measure and graph the relationship between nodes, failures, and convergence time.

5. **Real-World Application**: Design a distributed key-value store using the techniques learned.

## Resources for Further Study

- [Raft Visualization](https://raft.github.io/)
- [CRDT Resources](https://crdt.tech/)
- [Byzantine Generals Paper](https://lamport.azurewebsites.net/pubs/byz.pdf)
- [Gossip Protocol Survey](https://www.cs.cornell.edu/home/rvr/papers/GossipSurvey.pdf)
- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)