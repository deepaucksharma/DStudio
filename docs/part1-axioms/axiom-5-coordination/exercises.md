# Coordination Cost Exercises

!!! info "Prerequisites"
    - [Axiom 5: Coordination Core Concepts](index.md)
    - [Coordination Examples](examples.md)
    - Understanding of consensus protocols

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Coordination Home](index.md) |
    [→ Next Axiom](../axiom-6-observability/index.md)

## Exercise 1: Calculate Coordination Costs

### 🔧 Try This: Build a Cost Calculator

```python
import time
import threading
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CoordinationMetrics:
    messages_sent: int = 0
    bytes_sent: int = 0
    round_trips: int = 0
    time_spent_ms: float = 0
    failures: int = 0

class CoordinationCalculator:
    def __init__(self, nodes: int, rtt_ms: float, message_size_bytes: int = 1024):
        self.nodes = nodes
        self.rtt_ms = rtt_ms
        self.message_size_bytes = message_size_bytes
        
    def calculate_2pc_cost(self, transactions: int) -> CoordinationMetrics:
        """
        TODO: Calculate the cost of 2PC
        - 3 phases of messages
        - Account for coordinator
        - Consider failure/retry cases
        """
        pass
    
    def calculate_paxos_cost(self, operations: int, failure_rate: float = 0.01) -> CoordinationMetrics:
        """
        TODO: Calculate Paxos/Raft cost
        - Normal case: 2 RTT
        - Leader election on failure
        - Account for heartbeats
        """
        pass
    
    def calculate_gossip_cost(self, fanout: int, rounds: int) -> CoordinationMetrics:
        """
        TODO: Calculate gossip protocol cost
        - Each node contacts 'fanout' others
        - Information spreads exponentially
        - Calculate convergence time
        """
        pass
    
    def calculate_quorum_cost(self, operations: int, read_quorum: int, write_quorum: int) -> CoordinationMetrics:
        """
        TODO: Calculate quorum-based system cost
        - Parallel requests to quorum
        - Max latency of quorum responses
        - R + W > N for consistency
        """
        pass

# Exercise: Compare protocols for different scenarios
scenarios = [
    {"name": "Small cluster", "nodes": 3, "operations": 1000},
    {"name": "Medium cluster", "nodes": 7, "operations": 10000},
    {"name": "Large cluster", "nodes": 21, "operations": 100000},
]

# TODO: Calculate and compare costs for each protocol
# Consider: latency, bandwidth, message count, dollar cost
```

<details>
<summary>Solution</summary>

```python
import time
import threading
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import random

@dataclass
class CoordinationMetrics:
    messages_sent: int = 0
    bytes_sent: int = 0
    round_trips: int = 0
    time_spent_ms: float = 0
    failures: int = 0
    
    def add_message(self, count: int, size_bytes: int):
        self.messages_sent += count
        self.bytes_sent += count * size_bytes
    
    def add_round_trip(self, count: int, rtt_ms: float):
        self.round_trips += count
        self.time_spent_ms += count * rtt_ms
    
    def bandwidth_cost_usd(self, price_per_gb: float = 0.02) -> float:
        gb_sent = self.bytes_sent / (1024 ** 3)
        return gb_sent * price_per_gb
    
    def summary(self) -> Dict:
        return {
            'messages': self.messages_sent,
            'bandwidth_mb': self.bytes_sent / (1024 ** 2),
            'round_trips': self.round_trips,
            'latency_ms': self.time_spent_ms,
            'failures': self.failures,
            'bandwidth_cost_usd': self.bandwidth_cost_usd()
        }

class CoordinationCalculator:
    def __init__(self, nodes: int, rtt_ms: float, message_size_bytes: int = 1024):
        self.nodes = nodes
        self.rtt_ms = rtt_ms
        self.message_size_bytes = message_size_bytes
        
    def calculate_2pc_cost(self, transactions: int, failure_rate: float = 0.01) -> CoordinationMetrics:
        """Calculate the cost of 2PC"""
        metrics = CoordinationMetrics()
        
        for _ in range(transactions):
            # Phase 1: Prepare
            # Coordinator sends to all participants
            metrics.add_message(self.nodes - 1, self.message_size_bytes)
            metrics.add_round_trip(1, self.rtt_ms)
            
            # Participants respond with votes
            metrics.add_message(self.nodes - 1, self.message_size_bytes)
            metrics.add_round_trip(1, self.rtt_ms)
            
            # Simulate failures
            if random.random() < failure_rate:
                metrics.failures += 1
                # Abort message to all
                metrics.add_message(self.nodes - 1, self.message_size_bytes)
                metrics.add_round_trip(1, self.rtt_ms)
            else:
                # Phase 2: Commit
                metrics.add_message(self.nodes - 1, self.message_size_bytes)
                metrics.add_round_trip(1, self.rtt_ms)
        
        return metrics
    
    def calculate_paxos_cost(self, operations: int, failure_rate: float = 0.01) -> CoordinationMetrics:
        """Calculate Paxos/Raft cost"""
        metrics = CoordinationMetrics()
        
        # Heartbeat overhead (once per second for duration)
        operation_time_s = (operations * 2 * self.rtt_ms) / 1000
        heartbeats = int(operation_time_s)
        metrics.add_message(heartbeats * (self.nodes - 1), 64)  # Small heartbeat
        
        for i in range(operations):
            if random.random() < failure_rate:
                # Leader election
                metrics.failures += 1
                
                # Election timeout
                metrics.time_spent_ms += 150  # Typical election timeout
                
                # RequestVote RPCs
                metrics.add_message((self.nodes - 1) * 2, self.message_size_bytes)
                metrics.add_round_trip(2, self.rtt_ms)
                
                # New leader announcement
                metrics.add_message(self.nodes - 1, self.message_size_bytes)
                metrics.add_round_trip(1, self.rtt_ms)
            
            # Normal operation
            # Leader replication to majority
            majority = (self.nodes // 2) + 1
            metrics.add_message(majority - 1, self.message_size_bytes)
            metrics.add_round_trip(1, self.rtt_ms)
            
            # Acknowledgments
            metrics.add_message(majority - 1, 64)  # Small ack
            metrics.add_round_trip(1, self.rtt_ms)
        
        return metrics
    
    def calculate_gossip_cost(self, fanout: int, rounds: int) -> CoordinationMetrics:
        """Calculate gossip protocol cost"""
        metrics = CoordinationMetrics()
        
        # Epidemic spread model
        infected = 1
        
        for round in range(rounds):
            # Each infected node contacts fanout others
            messages_this_round = min(infected * fanout, self.nodes * fanout)
            metrics.add_message(messages_this_round, self.message_size_bytes)
            metrics.add_round_trip(1, self.rtt_ms)
            
            # Estimate newly infected (probabilistic)
            newly_infected = min(infected * fanout * 0.7, self.nodes - infected)
            infected = min(infected + int(newly_infected), self.nodes)
            
            # Check convergence
            if infected >= self.nodes * 0.99:
                break
        
        return metrics
    
    def calculate_quorum_cost(self, operations: int, read_quorum: int, write_quorum: int) -> CoordinationMetrics:
        """Calculate quorum-based system cost"""
        metrics = CoordinationMetrics()
        
        # Verify valid quorum configuration
        assert read_quorum + write_quorum > self.nodes, "R + W must be > N"
        
        for _ in range(operations):
            # Randomly choose read or write
            if random.random() < 0.8:  # 80% reads
                # Read from R nodes in parallel
                metrics.add_message(read_quorum, self.message_size_bytes)
                # Latency is max of quorum responses
                metrics.add_round_trip(1, self.rtt_ms * 1.2)  # 20% slower node
            else:
                # Write to W nodes in parallel
                metrics.add_message(write_quorum, self.message_size_bytes)
                metrics.add_round_trip(1, self.rtt_ms * 1.3)  # 30% slower for writes
        
        return metrics
    
    def calculate_no_coordination_cost(self, operations: int) -> CoordinationMetrics:
        """Baseline: No coordination"""
        metrics = CoordinationMetrics()
        metrics.time_spent_ms = operations * 0.1  # Local operation only
        return metrics

# Comprehensive comparison
def compare_coordination_protocols():
    print("=== Coordination Protocol Cost Analysis ===\n")
    
    scenarios = [
        {"name": "Small cluster", "nodes": 3, "operations": 1000, "rtt_ms": 1},
        {"name": "Regional cluster", "nodes": 7, "operations": 10000, "rtt_ms": 10},
        {"name": "Global cluster", "nodes": 21, "operations": 100000, "rtt_ms": 100},
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Nodes: {scenario['nodes']}, Operations: {scenario['operations']:,}, RTT: {scenario['rtt_ms']}ms\n")
        
        calc = CoordinationCalculator(
            nodes=scenario['nodes'],
            rtt_ms=scenario['rtt_ms']
        )
        
        protocols = {
            "No Coordination": calc.calculate_no_coordination_cost(scenario['operations']),
            "2PC": calc.calculate_2pc_cost(scenario['operations']),
            "Paxos/Raft": calc.calculate_paxos_cost(scenario['operations']),
            "Gossip": calc.calculate_gossip_cost(fanout=3, rounds=20),
            "Quorum (R=2,W=2)": calc.calculate_quorum_cost(
                scenario['operations'], 
                read_quorum=2, 
                write_quorum=2
            ) if scenario['nodes'] >= 3 else None,
        }
        
        # Print comparison table
        print(f"{'Protocol':<20} {'Latency(s)':<12} {'Messages':<12} {'Bandwidth(MB)':<15} {'Cost(USD)':<12}")
        print("-" * 80)
        
        for name, metrics in protocols.items():
            if metrics:
                summary = metrics.summary()
                print(f"{name:<20} "
                      f"{summary['latency_ms']/1000:<12.2f} "
                      f"{summary['messages']:<12,} "
                      f"{summary['bandwidth_mb']:<15.2f} "
                      f"${summary['bandwidth_cost_usd']:<11.4f}")
    
    print("\n=== Key Insights ===")
    print("1. No coordination is always fastest but provides no consistency")
    print("2. 2PC has highest message count (3N messages per transaction)")
    print("3. Paxos/Raft is efficient for normal operations but costly during elections")
    print("4. Gossip has probabilistic convergence, good for eventual consistency")
    print("5. Quorum systems balance consistency and availability")
    print("6. Global clusters (100ms RTT) make coordination extremely expensive")

# Run the comparison
compare_coordination_protocols()

# Detailed cost breakdown for specific scenario
print("\n\n=== Detailed Cost Breakdown: Global 2PC ===")

calc = CoordinationCalculator(nodes=5, rtt_ms=170, message_size_bytes=1024)
metrics = calc.calculate_2pc_cost(transactions=1000000)  # 1M transactions

print(f"Configuration: 5 global regions, 170ms RTT")
print(f"Transactions: 1,000,000")
print(f"\nResults:")
print(f"  Total messages: {metrics.messages_sent:,}")
print(f"  Total bandwidth: {metrics.bytes_sent / (1024**3):.2f} GB")
print(f"  Total time in coordination: {metrics.time_spent_ms / (1000 * 60 * 60):.2f} hours")
print(f"  Bandwidth cost: ${metrics.bandwidth_cost_usd():,.2f}")
print(f"  Cost per transaction: ${metrics.bandwidth_cost_usd() / 1000000:.6f}")

# Monthly projection
monthly_transactions = 100_000_000
monthly_cost = (metrics.bandwidth_cost_usd() / 1000000) * monthly_transactions
print(f"\nMonthly projection (100M transactions): ${monthly_cost:,.2f}")
```

</details>

## Exercise 2: Implement a Simple Consensus

### 🔧 Try This: Build a Basic Paxos

```python
import threading
import time
import random
from enum import Enum

class ProposalNumber:
    def __init__(self, number: int, node_id: int):
        self.number = number
        self.node_id = node_id
    
    def __gt__(self, other):
        # TODO: Implement comparison for proposal numbers
        pass

class PaxosNode:
    def __init__(self, node_id: int, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        
        # Proposer state
        self.proposal_number = 0
        
        # Acceptor state
        self.promised_proposal = None
        self.accepted_proposal = None
        self.accepted_value = None
        
    def propose(self, value):
        """
        TODO: Implement Paxos proposer logic
        Phase 1: Prepare
        - Generate proposal number
        - Send prepare(n) to majority
        - Wait for promises
        
        Phase 2: Accept
        - Send accept(n, v) to majority
        - Wait for accepted
        """
        pass
    
    def handle_prepare(self, proposal_number):
        """
        TODO: Implement acceptor logic for prepare
        - If n > promised, update promise
        - Return promise with any accepted value
        """
        pass
    
    def handle_accept(self, proposal_number, value):
        """
        TODO: Implement acceptor logic for accept
        - If n >= promised, accept value
        - Return accepted
        """
        pass

# Exercise: Implement and test consensus
def test_basic_consensus():
    # Create 3 nodes
    # Have them reach consensus on a value
    # Simulate failures and retries
    pass
```

<details>
<summary>Solution</summary>

```python
import threading
import time
import random
from enum import Enum
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import queue

@dataclass
class ProposalNumber:
    number: int
    node_id: int
    
    def __gt__(self, other):
        if other is None:
            return True
        return (self.number, self.node_id) > (other.number, other.node_id)
    
    def __ge__(self, other):
        if other is None:
            return True
        return (self.number, self.node_id) >= (other.number, other.node_id)
    
    def __str__(self):
        return f"{self.number}.{self.node_id}"

@dataclass
class Message:
    msg_type: str
    from_node: int
    to_node: int
    proposal: Optional[ProposalNumber] = None
    value: Optional[str] = None
    promised_proposal: Optional[ProposalNumber] = None
    accepted_proposal: Optional[ProposalNumber] = None
    accepted_value: Optional[str] = None

class PaxosNode:
    def __init__(self, node_id: int, peers: List[int], message_queue: Dict[int, queue.Queue]):
        self.node_id = node_id
        self.peers = peers
        self.message_queue = message_queue
        self.lock = threading.Lock()
        
        # Proposer state
        self.proposal_counter = 0
        self.current_proposal = None
        self.promises_received = {}
        self.accepts_received = {}
        
        # Acceptor state
        self.promised_proposal = None
        self.accepted_proposal = None
        self.accepted_value = None
        
        # Learner state
        self.learned_value = None
        
        # Metrics
        self.messages_sent = 0
        self.rounds_attempted = 0
        
    def propose(self, value: str) -> Optional[str]:
        """Propose a value using Paxos"""
        self.rounds_attempted += 1
        
        # Phase 1: Prepare
        proposal = self._generate_proposal_number()
        self.current_proposal = proposal
        self.promises_received = {}
        
        print(f"Node {self.node_id}: Proposing '{value}' with proposal {proposal}")
        
        # Send prepare to all nodes (including self)
        for peer in self.peers + [self.node_id]:
            self._send_message(Message(
                msg_type="prepare",
                from_node=self.node_id,
                to_node=peer,
                proposal=proposal
            ))
        
        # Wait for majority promises
        majority = (len(self.peers) + 1) // 2 + 1
        timeout = time.time() + 2.0  # 2 second timeout
        
        while len(self.promises_received) < majority and time.time() < timeout:
            self._process_messages()
            time.sleep(0.01)
        
        if len(self.promises_received) < majority:
            print(f"Node {self.node_id}: Failed to get majority promises")
            return None
        
        # Check if any acceptor has already accepted a value
        highest_accepted_proposal = None
        highest_accepted_value = None
        
        for promise in self.promises_received.values():
            if promise['accepted_proposal'] and (
                highest_accepted_proposal is None or 
                promise['accepted_proposal'] > highest_accepted_proposal
            ):
                highest_accepted_proposal = promise['accepted_proposal']
                highest_accepted_value = promise['accepted_value']
        
        # Use previously accepted value if exists
        if highest_accepted_value is not None:
            value = highest_accepted_value
            print(f"Node {self.node_id}: Using previously accepted value '{value}'")
        
        # Phase 2: Accept
        self.accepts_received = {}
        
        # Send accept to all nodes
        for peer in self.peers + [self.node_id]:
            self._send_message(Message(
                msg_type="accept",
                from_node=self.node_id,
                to_node=peer,
                proposal=proposal,
                value=value
            ))
        
        # Wait for majority accepts
        timeout = time.time() + 2.0
        
        while len(self.accepts_received) < majority and time.time() < timeout:
            self._process_messages()
            time.sleep(0.01)
        
        if len(self.accepts_received) >= majority:
            self.learned_value = value
            print(f"Node {self.node_id}: Consensus reached on '{value}'")
            
            # Notify all nodes about the decision
            for peer in self.peers:
                self._send_message(Message(
                    msg_type="decided",
                    from_node=self.node_id,
                    to_node=peer,
                    value=value
                ))
            
            return value
        else:
            print(f"Node {self.node_id}: Failed to get majority accepts")
            return None
    
    def _generate_proposal_number(self) -> ProposalNumber:
        with self.lock:
            self.proposal_counter += 1
            return ProposalNumber(self.proposal_counter, self.node_id)
    
    def _send_message(self, msg: Message):
        self.messages_sent += 1
        if msg.to_node in self.message_queue:
            self.message_queue[msg.to_node].put(msg)
    
    def _process_messages(self):
        try:
            while True:
                msg = self.message_queue[self.node_id].get_nowait()
                
                if msg.msg_type == "prepare":
                    self._handle_prepare(msg)
                elif msg.msg_type == "promise":
                    self._handle_promise(msg)
                elif msg.msg_type == "accept":
                    self._handle_accept(msg)
                elif msg.msg_type == "accepted":
                    self._handle_accepted(msg)
                elif msg.msg_type == "decided":
                    self._handle_decided(msg)
        except queue.Empty:
            pass
    
    def _handle_prepare(self, msg: Message):
        with self.lock:
            if msg.proposal >= self.promised_proposal:
                self.promised_proposal = msg.proposal
                
                # Send promise
                self._send_message(Message(
                    msg_type="promise",
                    from_node=self.node_id,
                    to_node=msg.from_node,
                    proposal=msg.proposal,
                    accepted_proposal=self.accepted_proposal,
                    accepted_value=self.accepted_value
                ))
    
    def _handle_promise(self, msg: Message):
        if msg.proposal == self.current_proposal:
            self.promises_received[msg.from_node] = {
                'accepted_proposal': msg.accepted_proposal,
                'accepted_value': msg.accepted_value
            }
    
    def _handle_accept(self, msg: Message):
        with self.lock:
            if msg.proposal >= self.promised_proposal:
                self.promised_proposal = msg.proposal
                self.accepted_proposal = msg.proposal
                self.accepted_value = msg.value
                
                # Send accepted
                self._send_message(Message(
                    msg_type="accepted",
                    from_node=self.node_id,
                    to_node=msg.from_node,
                    proposal=msg.proposal
                ))
    
    def _handle_accepted(self, msg: Message):
        if msg.proposal == self.current_proposal:
            self.accepts_received[msg.from_node] = True
    
    def _handle_decided(self, msg: Message):
        with self.lock:
            self.learned_value = msg.value
            print(f"Node {self.node_id}: Learned decision '{msg.value}'")
    
    def run(self):
        """Run the node, processing messages"""
        while True:
            self._process_messages()
            time.sleep(0.01)

# Test implementation
def test_paxos_consensus():
    print("=== Testing Basic Paxos Implementation ===\n")
    
    # Create message queues
    num_nodes = 5
    message_queues = {i: queue.Queue() for i in range(num_nodes)}
    
    # Create nodes
    nodes = []
    for i in range(num_nodes):
        peers = [j for j in range(num_nodes) if j != i]
        node = PaxosNode(i, peers, message_queues)
        nodes.append(node)
    
    # Start node threads
    threads = []
    for node in nodes:
        t = threading.Thread(target=node.run, daemon=True)
        threads.append(t)
        t.start()
    
    print("Test 1: Single proposer")
    print("-" * 40)
    result = nodes[0].propose("value_A")
    print(f"Result: {result}")
    time.sleep(0.5)
    
    # Check all nodes learned the same value
    learned_values = [node.learned_value for node in nodes]
    print(f"All nodes learned: {learned_values}")
    assert all(v == "value_A" for v in learned_values)
    print("✅ Test 1 passed\n")
    
    print("Test 2: Concurrent proposers")
    print("-" * 40)
    
    # Reset nodes
    for node in nodes:
        node.learned_value = None
        node.accepted_value = None
        node.accepted_proposal = None
    
    # Multiple nodes propose concurrently
    results = [None] * 3
    
    def propose_value(node_idx, value, result_idx):
        results[result_idx] = nodes[node_idx].propose(value)
    
    threads = []
    proposals = [(0, "value_X", 0), (1, "value_Y", 1), (2, "value_Z", 2)]
    
    for node_idx, value, result_idx in proposals:
        t = threading.Thread(target=propose_value, args=(node_idx, value, result_idx))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    time.sleep(0.5)
    
    # Check that all nodes agreed on one value
    learned_values = [node.learned_value for node in nodes if node.learned_value]
    print(f"Results: {results}")
    print(f"Learned values: {learned_values}")
    
    if learned_values:
        consensus_value = learned_values[0]
        assert all(v == consensus_value for v in learned_values)
        print(f"✅ Test 2 passed - Consensus on '{consensus_value}'\n")
    
    # Print metrics
    print("Metrics:")
    print("-" * 40)
    total_messages = sum(node.messages_sent for node in nodes)
    total_rounds = sum(node.rounds_attempted for node in nodes)
    print(f"Total messages sent: {total_messages}")
    print(f"Total rounds attempted: {total_rounds}")
    print(f"Messages per round: {total_messages / total_rounds:.1f}")

# Run the test
test_paxos_consensus()
```

</details>

## Exercise 3: Coordination-Free Design

### 🔧 Try This: Design Without Coordination

```python
class CoordinationFreeCounter:
    """
    Design a distributed counter that:
    - Supports increment/decrement from any node
    - Eventually converges to correct total
    - Requires NO coordination between nodes
    - Handles network partitions
    
    Hint: This is a CRDT (Conflict-free Replicated Data Type)
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        # TODO: Design data structure
        pass
    
    def increment(self, amount: int = 1):
        # TODO: Local increment
        pass
    
    def merge(self, other_state):
        # TODO: Merge states from another node
        pass
    
    def get_value(self) -> int:
        # TODO: Calculate current value
        pass

# Exercise: Implement and test convergence
def test_coordination_free():
    # Create nodes
    # Perform operations
    # Partition and merge
    # Verify convergence
    pass
```

<details>
<summary>Solution</summary>

```python
from typing import Dict, Set, Tuple, List
import random
import copy

class GCounter:
    """Grow-only counter CRDT"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: Dict[str, int] = {node_id: 0}
    
    def increment(self, amount: int = 1):
        if amount < 0:
            raise ValueError("GCounter only supports positive increments")
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + amount
    
    def merge(self, other: 'GCounter'):
        # Take maximum of each node's count
        for node_id, count in other.counts.items():
            self.counts[node_id] = max(self.counts.get(node_id, 0), count)
    
    def get_value(self) -> int:
        return sum(self.counts.values())
    
    def __repr__(self):
        return f"GCounter({self.node_id}: {self.counts})"

class PNCounter:
    """Increment/decrement counter using two GCounters"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.positive = GCounter(node_id + "_pos")
        self.negative = GCounter(node_id + "_neg")
    
    def increment(self, amount: int = 1):
        if amount >= 0:
            self.positive.increment(amount)
        else:
            self.negative.increment(-amount)
    
    def merge(self, other: 'PNCounter'):
        self.positive.merge(other.positive)
        self.negative.merge(other.negative)
    
    def get_value(self) -> int:
        return self.positive.get_value() - self.negative.get_value()

class ORSet:
    """Observed-Remove Set CRDT"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.elements: Dict[any, Set[Tuple[str, int]]] = {}  # elem -> {(node, timestamp)}
        self.tombstones: Set[Tuple[any, str, int]] = set()  # (elem, node, timestamp)
        self.timestamp = 0
    
    def add(self, element):
        self.timestamp += 1
        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add((self.node_id, self.timestamp))
    
    def remove(self, element):
        if element in self.elements:
            # Add all unique tags to tombstones
            for tag in self.elements[element]:
                self.tombstones.add((element, tag[0], tag[1]))
    
    def contains(self, element) -> bool:
        if element not in self.elements:
            return False
        
        # Element exists if any tag is not in tombstones
        for tag in self.elements[element]:
            if (element, tag[0], tag[1]) not in self.tombstones:
                return True
        return False
    
    def merge(self, other: 'ORSet'):
        # Merge elements
        for elem, tags in other.elements.items():
            if elem not in self.elements:
                self.elements[elem] = set()
            self.elements[elem].update(tags)
        
        # Merge tombstones
        self.tombstones.update(other.tombstones)
        
        # Update timestamp
        self.timestamp = max(self.timestamp, other.timestamp)
    
    def get_elements(self) -> Set:
        return {elem for elem in self.elements if self.contains(elem)}

class LWWRegister:
    """Last-Write-Wins Register CRDT"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.value = None
        self.timestamp = 0
    
    def set(self, value):
        self.timestamp += 1
        self.value = value
    
    def merge(self, other: 'LWWRegister'):
        if other.timestamp > self.timestamp or (
            other.timestamp == self.timestamp and other.node_id > self.node_id
        ):
            self.value = other.value
            self.timestamp = other.timestamp
    
    def get(self):
        return self.value

# Comprehensive test
def test_coordination_free_datatypes():
    print("=== Testing Coordination-Free Data Types (CRDTs) ===\n")
    
    # Test 1: GCounter convergence
    print("Test 1: Grow-only Counter")
    print("-" * 40)
    
    # Three nodes increment independently
    node_a = GCounter("A")
    node_b = GCounter("B")
    node_c = GCounter("C")
    
    node_a.increment(5)
    node_b.increment(3)
    node_c.increment(7)
    
    print(f"Before merge:")
    print(f"  Node A: {node_a.get_value()} {node_a.counts}")
    print(f"  Node B: {node_b.get_value()} {node_b.counts}")
    print(f"  Node C: {node_c.get_value()} {node_c.counts}")
    
    # Simulate partial synchronization
    node_a.merge(node_b)  # A learns about B
    node_b.merge(node_c)  # B learns about C
    node_c.merge(node_a)  # C learns about A (which knows about B)
    
    print(f"\nAfter partial sync:")
    print(f"  Node A: {node_a.get_value()} {node_a.counts}")
    print(f"  Node B: {node_b.get_value()} {node_b.counts}")
    print(f"  Node C: {node_c.get_value()} {node_c.counts}")
    
    # Complete synchronization
    node_a.merge(node_b)
    node_a.merge(node_c)
    node_b.merge(node_a)
    node_c.merge(node_a)
    
    print(f"\nAfter complete sync:")
    print(f"  Node A: {node_a.get_value()}")
    print(f"  Node B: {node_b.get_value()}")
    print(f"  Node C: {node_c.get_value()}")
    
    assert node_a.get_value() == node_b.get_value() == node_c.get_value() == 15
    print("✅ GCounter converged correctly\n")
    
    # Test 2: PN Counter with decrements
    print("Test 2: PN Counter (with decrements)")
    print("-" * 40)
    
    pn_a = PNCounter("A")
    pn_b = PNCounter("B")
    
    # Node A: +10, -3 = 7
    pn_a.increment(10)
    pn_a.increment(-3)
    
    # Node B: +5, -2 = 3
    pn_b.increment(5)
    pn_b.increment(-2)
    
    print(f"Before merge: A={pn_a.get_value()}, B={pn_b.get_value()}")
    
    # Merge
    pn_a.merge(pn_b)
    pn_b.merge(pn_a)
    
    print(f"After merge: A={pn_a.get_value()}, B={pn_b.get_value()}")
    assert pn_a.get_value() == pn_b.get_value() == 10
    print("✅ PNCounter converged correctly\n")
    
    # Test 3: OR-Set with concurrent add/remove
    print("Test 3: OR-Set (Observed-Remove Set)")
    print("-" * 40)
    
    set_a = ORSet("A")
    set_b = ORSet("B")
    
    # Both add "X"
    set_a.add("X")
    set_b.add("X")
    
    # A removes X (only knows about its own add)
    set_a.remove("X")
    
    # B adds Y
    set_b.add("Y")
    
    print(f"Before merge:")
    print(f"  Set A: {set_a.get_elements()}")
    print(f"  Set B: {set_b.get_elements()}")
    
    # Merge
    set_a.merge(set_b)
    set_b.merge(set_a)
    
    print(f"After merge:")
    print(f"  Set A: {set_a.get_elements()}")
    print(f"  Set B: {set_b.get_elements()}")
    
    # X should exist (B's add not removed), Y should exist
    assert set_a.get_elements() == set_b.get_elements() == {"X", "Y"}
    print("✅ OR-Set converged correctly\n")
    
    # Test 4: Network partition simulation
    print("Test 4: Network Partition Simulation")
    print("-" * 40)
    
    # Create 5 nodes
    counters = {f"Node{i}": GCounter(f"Node{i}") for i in range(5)}
    
    # Simulate operations during partition
    # Partition 1: Node0, Node1
    # Partition 2: Node2, Node3, Node4
    
    print("During partition:")
    # Partition 1 operations
    counters["Node0"].increment(10)
    counters["Node1"].increment(20)
    counters["Node0"].merge(counters["Node1"])
    counters["Node1"].merge(counters["Node0"])
    
    # Partition 2 operations
    counters["Node2"].increment(30)
    counters["Node3"].increment(40)
    counters["Node4"].increment(50)
    
    # Sync within partition 2
    for i in [2, 3, 4]:
        for j in [2, 3, 4]:
            if i != j:
                counters[f"Node{i}"].merge(counters[f"Node{j}"])
    
    print(f"  Partition 1 sum: {counters['Node0'].get_value()}")
    print(f"  Partition 2 sum: {counters['Node2'].get_value()}")
    
    # Heal partition
    print("\nAfter partition heals:")
    for i in range(5):
        for j in range(5):
            if i != j:
                counters[f"Node{i}"].merge(counters[f"Node{j}"])
    
    # All should converge to same value
    values = [counter.get_value() for counter in counters.values()]
    print(f"  All nodes: {values}")
    assert all(v == 150 for v in values)
    print("✅ Converged after partition heal\n")
    
    print("=== Summary ===")
    print("CRDTs provide coordination-free convergence through:")
    print("1. Commutative merge operations")
    print("2. Idempotent updates")
    print("3. Monotonic growth (or controlled shrinking)")
    print("4. No coordination overhead - just merge states!")

# Run the test
test_coordination_free_datatypes()
```

</details>

## Exercise 4: Measure Real Coordination

### 🔧 Try This: Benchmark Coordination Overhead

```python
import time
import threading
from queue import Queue

def benchmark_coordination():
    """
    Compare performance with different coordination levels:
    1. No coordination (embarrassingly parallel)
    2. Coarse-grained locking
    3. Fine-grained locking  
    4. Lock-free with CAS
    5. Message passing
    
    Measure: throughput, latency, CPU usage
    """
    
    # TODO: Implement benchmarks
    # Measure the actual cost of coordination
    pass

# Exercise: Find the coordination sweet spot
# When does coordination cost more than it saves?
```

<details>
<summary>Solution</summary>

```python
import time
import threading
import multiprocessing
from queue import Queue
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable
import psutil
import os

class CoordinationBenchmark:
    def __init__(self, num_workers: int = 4, operations: int = 100000):
        self.num_workers = num_workers
        self.operations = operations
        self.results = {}
        
    def measure_performance(self, name: str, setup_func: Callable, 
                          work_func: Callable, cleanup_func: Callable = None):
        """Measure performance of a coordination strategy"""
        print(f"\nBenchmarking: {name}")
        print("-" * 50)
        
        # Setup
        context = setup_func()
        
        # Measure CPU before
        process = psutil.Process(os.getpid())
        cpu_before = process.cpu_percent(interval=0.1)
        
        # Start timing
        start_time = time.time()
        
        # Run workers
        threads = []
        ops_per_worker = self.operations // self.num_workers
        
        for i in range(self.num_workers):
            t = threading.Thread(
                target=work_func,
                args=(context, i, ops_per_worker)
            )
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        
        # Measure CPU after
        cpu_after = process.cpu_percent(interval=0.1)
        avg_cpu = (cpu_before + cpu_after) / 2
        
        # Cleanup if needed
        if cleanup_func:
            cleanup_func(context)
        
        # Calculate metrics
        throughput = self.operations / total_time
        latency_us = (total_time / self.operations) * 1_000_000
        
        self.results[name] = {
            'total_time': total_time,
            'throughput': throughput,
            'latency_us': latency_us,
            'cpu_percent': avg_cpu
        }
        
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Throughput: {throughput:,.0f} ops/sec")
        print(f"  Latency: {latency_us:.2f} μs/op")
        print(f"  CPU usage: {avg_cpu:.1f}%")

def run_coordination_benchmarks():
    benchmark = CoordinationBenchmark(num_workers=4, operations=1000000)
    
    # 1. No Coordination (Embarrassingly Parallel)
    def no_coord_setup():
        return {'counters': [0] * benchmark.num_workers}
    
    def no_coord_work(context, worker_id, ops):
        # Each worker has its own counter
        for _ in range(ops):
            context['counters'][worker_id] += 1
    
    benchmark.measure_performance(
        "No Coordination",
        no_coord_setup,
        no_coord_work
    )
    
    # 2. Coarse-Grained Locking
    def coarse_lock_setup():
        return {
            'counter': 0,
            'lock': threading.Lock()
        }
    
    def coarse_lock_work(context, worker_id, ops):
        for _ in range(ops):
            with context['lock']:
                context['counter'] += 1
    
    benchmark.measure_performance(
        "Coarse-Grained Lock",
        coarse_lock_setup,
        coarse_lock_work
    )
    
    # 3. Fine-Grained Locking (Multiple Locks)
    def fine_lock_setup():
        num_locks = 16
        return {
            'counters': [0] * num_locks,
            'locks': [threading.Lock() for _ in range(num_locks)]
        }
    
    def fine_lock_work(context, worker_id, ops):
        num_locks = len(context['locks'])
        for i in range(ops):
            lock_idx = i % num_locks
            with context['locks'][lock_idx]:
                context['counters'][lock_idx] += 1
    
    benchmark.measure_performance(
        "Fine-Grained Locks (16 locks)",
        fine_lock_setup,
        fine_lock_work
    )
    
    # 4. Lock-Free with Atomic Operations
    def atomic_setup():
        # Using multiprocessing.Value for atomic operations
        return {
            'counter': multiprocessing.Value('i', 0)
        }
    
    def atomic_work(context, worker_id, ops):
        counter = context['counter']
        for _ in range(ops):
            with counter.get_lock():
                counter.value += 1
    
    benchmark.measure_performance(
        "Atomic Operations",
        atomic_setup,
        atomic_work
    )
    
    # 5. Message Passing
    def message_setup():
        input_queues = [Queue() for _ in range(benchmark.num_workers)]
        output_queue = Queue()
        
        # Start aggregator thread
        aggregator_done = threading.Event()
        
        def aggregator():
            total = 0
            expected = benchmark.operations
            while total < expected:
                total += output_queue.get()
            aggregator_done.set()
        
        aggregator_thread = threading.Thread(target=aggregator)
        aggregator_thread.start()
        
        return {
            'input_queues': input_queues,
            'output_queue': output_queue,
            'aggregator_thread': aggregator_thread,
            'aggregator_done': aggregator_done
        }
    
    def message_work(context, worker_id, ops):
        output_queue = context['output_queue']
        local_sum = 0
        
        for _ in range(ops):
            local_sum += 1
            
            # Batch sends to reduce overhead
            if local_sum % 1000 == 0:
                output_queue.put(1000)
                local_sum = 0
        
        # Send remaining
        if local_sum > 0:
            output_queue.put(local_sum)
    
    def message_cleanup(context):
        context['aggregator_thread'].join()
    
    benchmark.measure_performance(
        "Message Passing (batched)",
        message_setup,
        message_work,
        message_cleanup
    )
    
    # 6. Thread Pool with Futures
    def futures_setup():
        return {
            'executor': ThreadPoolExecutor(max_workers=benchmark.num_workers),
            'counter': 0,
            'lock': threading.Lock()
        }
    
    def futures_work(context, worker_id, ops):
        def increment():
            with context['lock']:
                context['counter'] += 1
        
        # Submit all tasks
        futures = []
        for _ in range(ops):
            future = context['executor'].submit(increment)
            futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result()
    
    def futures_cleanup(context):
        context['executor'].shutdown()
    
    # Skip futures test for large operation counts (too slow)
    if benchmark.operations <= 10000:
        benchmark.measure_performance(
            "Thread Pool Futures",
            futures_setup,
            futures_work,
            futures_cleanup
        )
    
    # Print comparison
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)
    print(f"{'Strategy':<25} {'Time(s)':<10} {'Throughput':<15} {'Latency(μs)':<12} {'CPU%':<8}")
    print("-" * 70)
    
    # Sort by throughput
    sorted_results = sorted(
        benchmark.results.items(),
        key=lambda x: x[1]['throughput'],
        reverse=True
    )
    
    for name, metrics in sorted_results:
        print(f"{name:<25} "
              f"{metrics['total_time']:<10.3f} "
              f"{metrics['throughput']:<15,.0f} "
              f"{metrics['latency_us']:<12.2f} "
              f"{metrics['cpu_percent']:<8.1f}")
    
    # Calculate coordination overhead
    if "No Coordination" in benchmark.results:
        no_coord_throughput = benchmark.results["No Coordination"]["throughput"]
        
        print("\n" + "=" * 70)
        print("COORDINATION OVERHEAD")
        print("=" * 70)
        
        for name, metrics in sorted_results:
            if name != "No Coordination":
                overhead = ((no_coord_throughput / metrics['throughput']) - 1) * 100
                print(f"{name:<25} {overhead:>6.1f}% slower than no coordination")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("1. No coordination is fastest but limits consistency")
    print("2. Coarse-grained locking has highest contention")
    print("3. Fine-grained locking reduces contention at complexity cost")
    print("4. Lock-free approaches balance performance and correctness")
    print("5. Message passing avoids shared state but adds communication overhead")
    print("6. Choose based on consistency requirements and contention level")

# Run the benchmarks
run_coordination_benchmarks()

# Additional analysis: Scaling behavior
def analyze_scaling():
    print("\n\n" + "=" * 70)
    print("SCALING ANALYSIS")
    print("=" * 70)
    
    worker_counts = [1, 2, 4, 8]
    operations = 100000
    
    for strategy_name, strategy_setup, strategy_work in [
        ("No Coordination", 
         lambda: {'counters': [0] * 16},
         lambda ctx, wid, ops: sum(1 for _ in range(ops))),
        
        ("Coarse Lock",
         lambda: {'counter': 0, 'lock': threading.Lock()},
         lambda ctx, wid, ops: [ctx['lock'].acquire() or ctx.__setitem__('counter', ctx['counter'] + 1) or ctx['lock'].release() for _ in range(ops)]),
    ]:
        print(f"\n{strategy_name} Scaling:")
        print(f"{'Workers':<10} {'Time(s)':<10} {'Speedup':<10} {'Efficiency':<10}")
        print("-" * 40)
        
        baseline_time = None
        
        for workers in worker_counts:
            benchmark = CoordinationBenchmark(num_workers=workers, operations=operations)
            
            # Run benchmark
            start = time.time()
            context = strategy_setup()
            
            threads = []
            ops_per_worker = operations // workers
            
            for i in range(workers):
                t = threading.Thread(target=strategy_work, args=(context, i, ops_per_worker))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            elapsed = time.time() - start
            
            if baseline_time is None:
                baseline_time = elapsed
            
            speedup = baseline_time / elapsed
            efficiency = speedup / workers
            
            print(f"{workers:<10} {elapsed:<10.3f} {speedup:<10.2f} {efficiency:<10.2%}")

analyze_scaling()
```

</details>

## Exercise 5: Design a Coordination Strategy

### 🔧 Try This: Choose the Right Protocol

```python
def design_coordination_strategy(requirements):
    """
    Given system requirements, design optimal coordination strategy
    
    Requirements:
    - consistency_level: "strong" | "eventual" | "causal"
    - operation_rate: operations per second
    - node_count: number of nodes
    - network_latency: RTT between nodes
    - failure_rate: probability of node failure
    - cost_budget: maximum $/month
    
    Output:
    - Recommended protocol
    - Expected latency
    - Expected cost
    - Trade-offs
    """
    
    # TODO: Implement decision logic
    # Consider all factors
    # Calculate costs
    # Recommend optimal strategy
    pass

# Exercise: Test with different scenarios
scenarios = [
    {
        "name": "Financial Ledger",
        "consistency_level": "strong",
        "operation_rate": 1000,
        "node_count": 5,
        "network_latency": 10,
        "failure_rate": 0.001,
        "cost_budget": 10000
    },
    {
        "name": "Social Media Feed",
        "consistency_level": "eventual",
        "operation_rate": 100000,
        "node_count": 50,
        "network_latency": 100,
        "failure_rate": 0.01,
        "cost_budget": 50000
    },
    # Add more scenarios
]
```

<details>
<summary>Solution</summary>

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math

@dataclass
class CoordinationStrategy:
    protocol: str
    expected_latency_ms: float
    expected_cost_usd: float
    availability: float
    trade_offs: List[str]
    implementation_notes: List[str]

class CoordinationStrategyDesigner:
    def __init__(self):
        # Protocol characteristics
        self.protocols = {
            "no_coordination": {
                "consistency": "none",
                "latency_factor": 0,
                "message_factor": 0,
                "complexity": 1,
                "availability": 0.999
            },
            "eventual_consistency": {
                "consistency": "eventual",
                "latency_factor": 0.1,
                "message_factor": 0.5,
                "complexity": 2,
                "availability": 0.999
            },
            "causal_consistency": {
                "consistency": "causal",
                "latency_factor": 0.3,
                "message_factor": 1.0,
                "complexity": 3,
                "availability": 0.99
            },
            "quorum": {
                "consistency": "strong",
                "latency_factor": 1.0,
                "message_factor": 0.6,
                "complexity": 3,
                "availability": 0.99
            },
            "2pc": {
                "consistency": "strong",
                "latency_factor": 3.0,
                "message_factor": 3.0,
                "complexity": 4,
                "availability": 0.95
            },
            "paxos": {
                "consistency": "strong",
                "latency_factor": 2.0,
                "message_factor": 2.0,
                "complexity": 5,
                "availability": 0.99
            },
            "chain_replication": {
                "consistency": "strong",
                "latency_factor": 0.5,  # For reads
                "message_factor": 1.0,
                "complexity": 3,
                "availability": 0.98
            }
        }
    
    def calculate_protocol_cost(self, protocol: str, requirements: Dict) -> Tuple[float, float]:
        """Calculate latency and monetary cost for a protocol"""
        proto = self.protocols[protocol]
        
        # Latency calculation
        base_latency = requirements['network_latency'] * proto['latency_factor']
        
        # Add processing overhead based on complexity
        processing_overhead = proto['complexity'] * 2  # 2ms per complexity unit
        total_latency = base_latency + processing_overhead
        
        # Cost calculation
        messages_per_op = proto['message_factor'] * requirements['node_count']
        total_messages = messages_per_op * requirements['operation_rate'] * 86400 * 30  # Monthly
        
        # Assume 1KB per message, $0.02 per GB
        bandwidth_gb = (total_messages * 1024) / (1024 ** 3)
        bandwidth_cost = bandwidth_gb * 0.02
        
        # Add compute cost based on complexity
        compute_cost = proto['complexity'] * requirements['node_count'] * 50  # $50/month per node per complexity
        
        # Add operational cost (monitoring, debugging)
        operational_cost = proto['complexity'] * 100  # $100/month per complexity
        
        total_cost = bandwidth_cost + compute_cost + operational_cost
        
        return total_latency, total_cost
    
    def calculate_availability(self, protocol: str, requirements: Dict) -> float:
        """Calculate expected availability"""
        base_availability = self.protocols[protocol]['availability']
        
        # Adjust for node count (more nodes = more failure points for some protocols)
        if protocol in ['2pc', 'chain_replication']:
            # These require all nodes
            node_availability = 1 - requirements['failure_rate']
            system_availability = node_availability ** requirements['node_count']
        else:
            # These can tolerate some failures
            system_availability = base_availability
        
        return system_availability
    
    def design_coordination_strategy(self, requirements: Dict) -> CoordinationStrategy:
        """Design optimal coordination strategy based on requirements"""
        
        candidates = []
        
        # Filter protocols by consistency requirement
        for protocol_name, protocol_info in self.protocols.items():
            # Check consistency match
            if requirements['consistency_level'] == 'strong' and protocol_info['consistency'] != 'strong':
                continue
            if requirements['consistency_level'] == 'causal' and protocol_info['consistency'] not in ['causal', 'strong']:
                continue
            
            # Calculate metrics
            latency, cost = self.calculate_protocol_cost(protocol_name, requirements)
            availability = self.calculate_availability(protocol_name, requirements)
            
            # Check if within budget
            if cost <= requirements['cost_budget']:
                candidates.append({
                    'protocol': protocol_name,
                    'latency': latency,
                    'cost': cost,
                    'availability': availability
                })
        
        if not candidates:
            return self._suggest_compromise(requirements)
        
        # Score candidates
        best_candidate = None
        best_score = float('-inf')
        
        for candidate in candidates:
            # Scoring function (customize based on priorities)
            latency_score = 1000 / (candidate['latency'] + 1)  # Lower is better
            cost_score = requirements['cost_budget'] / (candidate['cost'] + 1)  # Lower is better
            availability_score = candidate['availability'] * 1000  # Higher is better
            
            # Weighted score
            if requirements['consistency_level'] == 'strong':
                # Prioritize correctness and availability
                score = latency_score + cost_score + availability_score * 2
            else:
                # Prioritize performance and cost
                score = latency_score * 2 + cost_score * 2 + availability_score
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        # Generate recommendation
        return self._create_recommendation(best_candidate, requirements)
    
    def _suggest_compromise(self, requirements: Dict) -> CoordinationStrategy:
        """Suggest compromises when requirements can't be met"""
        trade_offs = ["Cannot meet all requirements within budget"]
        
        if requirements['consistency_level'] == 'strong':
            trade_offs.append("Consider eventual consistency to reduce costs")
            trade_offs.append("Or increase budget for strong consistency")
        
        if requirements['node_count'] > 10:
            trade_offs.append("Consider sharding to reduce coordination scope")
        
        return CoordinationStrategy(
            protocol="eventual_consistency",
            expected_latency_ms=requirements['network_latency'] * 0.5,
            expected_cost_usd=requirements['cost_budget'],
            availability=0.99,
            trade_offs=trade_offs,
            implementation_notes=["Compromise solution - adjust requirements"]
        )
    
    def _create_recommendation(self, candidate: Dict, requirements: Dict) -> CoordinationStrategy:
        """Create detailed recommendation"""
        protocol = candidate['protocol']
        
        trade_offs = []
        implementation_notes = []
        
        # Protocol-specific recommendations
        if protocol == "2pc":
            trade_offs.append("Blocking protocol - coordinator failure stops progress")
            implementation_notes.append("Implement coordinator failover")
            implementation_notes.append("Use timeouts to detect failures")
        
        elif protocol == "paxos":
            trade_offs.append("Complex implementation - higher bug risk")
            implementation_notes.append("Use established library (etcd, Zookeeper)")
            implementation_notes.append("Implement comprehensive monitoring")
        
        elif protocol == "quorum":
            trade_offs.append("Read/write availability trade-off")
            implementation_notes.append(f"Suggested: R={requirements['node_count']//2+1}, W={requirements['node_count']//2+1}")
            implementation_notes.append("Consider read repair for consistency")
        
        elif protocol == "eventual_consistency":
            trade_offs.append("Temporary inconsistencies possible")
            implementation_notes.append("Use vector clocks for causality")
            implementation_notes.append("Implement conflict resolution")
        
        # General recommendations based on requirements
        if requirements['operation_rate'] > 10000:
            implementation_notes.append("Consider caching to reduce coordination")
            implementation_notes.append("Batch operations where possible")
        
        if requirements['network_latency'] > 50:
            implementation_notes.append("Consider regional sharding")
            implementation_notes.append("Use local coordination where possible")
        
        if requirements['failure_rate'] > 0.01:
            implementation_notes.append("Implement aggressive health checking")
            implementation_notes.append("Use circuit breakers")
        
        return CoordinationStrategy(
            protocol=protocol,
            expected_latency_ms=candidate['latency'],
            expected_cost_usd=candidate['cost'],
            availability=candidate['availability'],
            trade_offs=trade_offs,
            implementation_notes=implementation_notes
        )

# Test the designer
def test_coordination_designer():
    designer = CoordinationStrategyDesigner()
    
    scenarios = [
        {
            "name": "Financial Ledger",
            "consistency_level": "strong",
            "operation_rate": 1000,
            "node_count": 5,
            "network_latency": 10,
            "failure_rate": 0.001,
            "cost_budget": 10000
        },
        {
            "name": "Social Media Feed",
            "consistency_level": "eventual",
            "operation_rate": 100000,
            "node_count": 50,
            "network_latency": 100,
            "failure_rate": 0.01,
            "cost_budget": 50000
        },
        {
            "name": "Gaming Leaderboard",
            "consistency_level": "causal",
            "operation_rate": 50000,
            "node_count": 20,
            "network_latency": 50,
            "failure_rate": 0.005,
            "cost_budget": 20000
        },
        {
            "name": "IoT Sensor Data",
            "consistency_level": "eventual",
            "operation_rate": 1000000,
            "node_count": 100,
            "network_latency": 200,
            "failure_rate": 0.02,
            "cost_budget": 100000
        },
        {
            "name": "Distributed Lock Service",
            "consistency_level": "strong",
            "operation_rate": 10000,
            "node_count": 7,
            "network_latency": 5,
            "failure_rate": 0.001,
            "cost_budget": 30000
        }
    ]
    
    print("=== Coordination Strategy Recommendations ===\n")
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario['name']}")
        print(f"{'='*60}")
        
        print(f"\nRequirements:")
        print(f"  Consistency: {scenario['consistency_level']}")
        print(f"  Operations/sec: {scenario['operation_rate']:,}")
        print(f"  Nodes: {scenario['node_count']}")
        print(f"  Network RTT: {scenario['network_latency']}ms")
        print(f"  Failure rate: {scenario['failure_rate']:.1%}")
        print(f"  Budget: ${scenario['cost_budget']:,}/month")
        
        strategy = designer.design_coordination_strategy(scenario)
        
        print(f"\nRecommendation: {strategy.protocol.upper()}")
        print(f"  Expected latency: {strategy.expected_latency_ms:.1f}ms")
        print(f"  Expected cost: ${strategy.expected_cost_usd:,.2f}/month")
        print(f"  Availability: {strategy.availability:.3%}")
        
        if strategy.trade_offs:
            print(f"\nTrade-offs:")
            for trade_off in strategy.trade_offs:
                print(f"  - {trade_off}")
        
        if strategy.implementation_notes:
            print(f"\nImplementation notes:")
            for note in strategy.implementation_notes:
                print(f"  - {note}")

# Run the test
test_coordination_designer()
```

</details>

## Challenge Problems

### 1. The Zero-Coordination Database 💾

Design a database that requires zero coordination between nodes:
- Supports all CRUD operations
- Eventually consistent
- Handles conflicts automatically
- Scales linearly

### 2. The Coordination Cost Visualizer 📊

Build a tool that:
- Visualizes message flow between nodes
- Shows coordination hotspots
- Calculates real-time costs
- Suggests optimizations

### 3. The Adaptive Protocol Selector 🎯

Create a system that:
- Monitors coordination costs
- Switches protocols dynamically
- Optimizes for current workload
- Maintains consistency guarantees

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Calculating coordination costs
    - ✅ Implementing consensus protocols
    - ✅ Designing coordination-free systems
    - ✅ Measuring real overhead
    - ✅ Choosing optimal strategies

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 6: Observability](../axiom-6-observability/index.md) →
    
    **Back to**: [Coordination Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Consensus Patterns](../../patterns/consensus-patterns.md) | [Part II](../../part2-pillars/index.md)