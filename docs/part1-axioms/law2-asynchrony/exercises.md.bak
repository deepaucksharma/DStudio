---
title: "Asynchrony Engineering Lab: Time, Ordering, and Distributed Snapshots"
description: Hands-on exercises to understand and implement asynchronous distributed systems
type: exercise
difficulty: expert
reading_time: 45 min
prerequisites: ["law2-asynchrony/index.md"]
status: complete
last_updated: 2025-07-23
---

# Asynchrony Engineering Lab: Time, Ordering, and Distributed Snapshots

## Exercise 1: Implementing Logical Clocks

### Objective
Build and compare different logical clock implementations to understand event ordering in distributed systems.

### Task 1: Lamport Timestamps
```python
import threading
import time
from collections import deque
from typing import Dict, List, Tuple, Optional

class LamportClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.time = 0
        self.lock = threading.Lock()
        
    def local_event(self) -> int:
        """Process a local event"""
        with self.lock:
            self.time += 1
            return self.time
    
    def send_event(self) -> Tuple[str, int]:
        """Prepare timestamp for sending a message"""
        with self.lock:
            self.time += 1
            return (self.node_id, self.time)
    
    def receive_event(self, sender_id: str, sender_time: int) -> int:
        """Update clock when receiving a message"""
        with self.lock:
            self.time = max(self.time, sender_time) + 1
            return self.time

# Test your implementation
def test_lamport_clocks():
    clock_a = LamportClock("A")
    clock_b = LamportClock("B")
    clock_c = LamportClock("C")
    
# Simulate distributed events
# A sends to B
    sender, ts = clock_a.send_event()
    clock_b.receive_event(sender, ts)
    
# B sends to C
    sender, ts = clock_b.send_event()
    clock_c.receive_event(sender, ts)
    
# Verify causality is preserved
    print(f"Clock A: {clock_a.time}")  # Should be 1
    print(f"Clock B: {clock_b.time}")  # Should be 2
    print(f"Clock C: {clock_c.time}")  # Should be 3
    assert clock_a.time < clock_b.time < clock_c.time, "Causality not preserved!"
```

### Task 2: Vector Clocks
```python
class VectorClock:
    def __init__(self, node_id: str, all_nodes: List[str]):
        self.node_id = node_id
        self.clock = {node: 0 for node in all_nodes}
        self.lock = threading.Lock()
    
    def local_event(self) -> Dict[str, int]:
        """Process a local event"""
        with self.lock:
            self.clock[self.node_id] += 1
            return self.clock.copy()
    
    def send_event(self) -> Dict[str, int]:
        """Prepare vector clock for sending"""
        with self.lock:
            self.clock[self.node_id] += 1
            return self.clock.copy()
    
    def receive_event(self, sender_vector: Dict[str, int]) -> Dict[str, int]:
        """Update vector clock on receive"""
        with self.lock:
# Merge: take max of each component
            for node in self.clock:
                self.clock[node] = max(self.clock[node], sender_vector.get(node, 0))
# Increment local counter
            self.clock[self.node_id] += 1
            return self.clock.copy()
    
    def happens_before(self, other: Dict[str, int]) -> bool:
        """Check if this clock happens-before other"""
        all_less_equal = all(self.clock[node] <= other.get(node, 0) 
                            for node in self.clock)
        exists_less = any(self.clock[node] < other.get(node, 0) 
                         for node in self.clock)
        return all_less_equal and exists_less
    
    def concurrent_with(self, other: Dict[str, int]) -> bool:
        """Check if events are concurrent"""
# TODO: Events are concurrent if neither happens-before the other
        pass

# Test concurrent event detection
def detect_concurrent_events():
    nodes = ["A", "B", "C"]
    clock_a = VectorClock("A", nodes)
    clock_b = VectorClock("B", nodes)
    
# Create concurrent events
# A performs local events
    vec_a1 = clock_a.local_event()
    vec_a2 = clock_a.local_event()
    
# B performs local events (concurrent with A)
    vec_b1 = clock_b.local_event()
    vec_b2 = clock_b.local_event()
    
# TODO: Verify these are concurrent
    assert clock_a.concurrent_with(vec_b1)
```

### Task 3: Hybrid Logical Clocks (HLC)
```python
class HybridLogicalClock:
    """Combines physical and logical time for better ordering"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.logical_time = 0
        self.logical_counter = 0
        self.lock = threading.Lock()
    
    def now(self) -> Tuple[int, int, str]:
        """Get current HLC timestamp"""
        with self.lock:
            physical_now = int(time.time() * 1000)  # milliseconds
            
            if physical_now > self.logical_time:
# Physical time has advanced
                self.logical_time = physical_now
                self.logical_counter = 0
            else:
# Physical time hasn't advanced, increment counter
                self.logical_counter += 1
            
            return (self.logical_time, self.logical_counter, self.node_id)
    
    def update(self, remote_time: int, remote_counter: int) -> Tuple[int, int, str]:
        """Update HLC with remote timestamp"""
# TODO: Implement HLC update algorithm
# - If remote_time > max(local_time, physical_now): use remote_time, counter=0
# - If remote_time = max(...): use max counter + 1
# - Otherwise: use max(...), counter + 1
        pass

# Compare clock drift
def measure_clock_skew():
    """Measure how HLC handles clock skew between nodes"""
# TODO: Simulate nodes with different clock speeds
# Show that HLC converges despite skew
    pass
```

## Exercise 2: Race Condition Detection

### Objective
Build tools to detect and visualize race conditions in distributed systems.

### Task 1: Distributed Counter with Race Conditions
```python
import asyncio
import random

class DistributedCounter:
    def __init__(self, nodes: List[str]):
        self.values = {node: 0 for node in nodes}
        self.message_queue = asyncio.Queue()
        
    async def increment(self, node: str):
        """Increment counter with network delay"""
# Read current value
        current = self.values[node]
        
# Simulate network delay for read
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
# Increment
        new_value = current + 1
        
# Simulate network delay for write
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
# Write back (RACE CONDITION HERE!)
        self.values[node] = new_value
        
        return new_value

# TODO: Run concurrent increments and detect lost updates
async def detect_lost_updates():
    counter = DistributedCounter(["A", "B", "C"])
    
# Run 100 concurrent increments
    tasks = []
    for i in range(100):
        node = random.choice(["A", "B", "C"])
        tasks.append(counter.increment(node))
    
    await asyncio.gather(*tasks)
    
# TODO: Check if sum equals 100 (it won't!)
    total = sum(counter.values.values())
    print(f"Expected: 100, Actual: {total}")
    print(f"Lost updates: {100 - total}")
```

### Task 2: Implement a Race Detector
```python
class RaceDetector:
    def __init__(self):
        self.access_log = []  # (timestamp, node, resource, op_type, value)
        self.vector_clocks = {}
        
    def log_access(self, timestamp, node, resource, op_type, value):
        """Log a resource access"""
        self.access_log.append({
            'timestamp': timestamp,
            'node': node,
            'resource': resource,
            'op_type': op_type,  # 'read' or 'write'
            'value': value
        })
    
    def detect_races(self) -> List[Dict]:
        """Detect potential race conditions"""
        races = []
        
# TODO: Implement race detection algorithm
# 1. Group accesses by resource
# 2. For each resource, find overlapping read/write or write/write
# 3. Check if operations are concurrent (using vector clocks)
# 4. Flag concurrent conflicting operations as races
        
# Hint: Two operations race if:
# - They access the same resource
# - At least one is a write
# - They are concurrent (neither happens-before the other)
        
        return races
    
    def visualize_races(self):
        """Create a timeline visualization of races"""
# TODO: Generate timeline showing:
# - Each node's operations over time
# - Highlight racing operations in red
# - Show happens-before arrows
        pass
```

## Exercise 3: Distributed Snapshots

### Objective
Implement the Chandy-Lamport algorithm for capturing consistent global snapshots.

### Task 1: Basic Snapshot Algorithm
```python
class DistributedNode:
    def __init__(self, node_id: str, neighbors: List[str]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.state = {"balance": 1000}  # Example state
        self.channels = {n: deque() for n in neighbors}  # Message channels
        self.recording = False
        self.snapshot = None
        self.channel_states = {}
        
    def initiate_snapshot(self):
        """Node initiates global snapshot"""
# 1. Save local state
        self.snapshot = self.state.copy()
        self.recording = True
        
# 2. Send marker to all neighbors
        marker = {"type": "MARKER", "from": self.node_id}
        for neighbor in self.neighbors:
# In real system, this would be network send
            self.send_marker_to(neighbor, marker)
        
# 3. Start recording incoming channels
        self.channel_states = {n: [] for n in self.neighbors}
    
    def receive_marker(self, from_node: str):
        """Receive snapshot marker from neighbor"""
        if not self.recording:
# First marker received
# 1. Save local state
            self.snapshot = self.state.copy()
            self.recording = True
            
# 2. Send marker to all OTHER neighbors
            marker = {"type": "MARKER", "from": self.node_id}
            for neighbor in self.neighbors:
                if neighbor != from_node:
                    self.send_marker_to(neighbor, marker)
            
# 3. Start recording all channels except from_node
            self.channel_states = {n: [] for n in self.neighbors if n != from_node}
# Channel from from_node is empty (marker arrived first)
            self.channel_states[from_node] = []
        else:
# Already recording
# Stop recording channel from from_node
# Channel state is whatever we recorded
            if from_node not in self.channel_states:
                self.channel_states[from_node] = []
    
    def receive_message(self, from_node: str, message: Dict):
        """Receive regular message"""
# If recording this channel, save message
        if self.recording and from_node in self.channel_states:
            if isinstance(self.channel_states[from_node], list):
                self.channel_states[from_node].append(message)
        
# Process message normally (update state, etc.)
        self.process_message(message)
    
    def is_snapshot_complete(self) -> bool:
        """Check if snapshot is complete"""
# Complete when received marker from all neighbors
        if not self.recording:
            return False
        return len(self.channel_states) == len(self.neighbors)

# Test snapshot consistency
def test_distributed_snapshot():
# Create a ring of nodes
    nodes = {
        "A": DistributedNode("A", ["B", "C"]),
        "B": DistributedNode("B", ["A", "C"]),
        "C": DistributedNode("C", ["A", "B"])
    }
    
# TODO: Simulate money transfers during snapshot
# Verify: Total money in system remains constant
# (No money created or destroyed during snapshot)
```

### Task 2: Snapshot with In-Flight Messages
```python
class BankingSystem:
    """Distributed banking with in-flight transfers"""
    def __init__(self, nodes: List[str]):
        self.nodes = {n: BankNode(n) for n in nodes}
        self.total_money = sum(node.balance for node in self.nodes.values())
    
    async def transfer(self, from_node: str, to_node: str, amount: int):
        """Transfer money between nodes"""
        sender = self.nodes[from_node]
        
# Deduct from sender
        if sender.balance >= amount:
            sender.balance -= amount
            
# Simulate network delay
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
# Add to receiver (money is "in flight" during delay)
            self.nodes[to_node].balance += amount
    
    def verify_snapshot_consistency(self, snapshot):
        """Verify snapshot captures all money"""
# TODO: Calculate total from:
# 1. Node balances in snapshot
# 2. In-flight messages in channel states
# Should equal initial total_money
        pass

class BankNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.balance = 1000
        self.snapshot_state = None
        self.recording_channels = set()
        self.channel_messages = {}
```

## Exercise 4: Timeout Strategies

### Objective
Design and test adaptive timeout strategies for unreliable networks.

### Task 1: Implement Adaptive Timeouts
```python
import numpy as np
from collections import deque

class AdaptiveTimeout:
    def __init__(self, initial_timeout: float = 1.0):
        self.initial_timeout = initial_timeout
        self.rtt_samples = deque(maxlen=100)
        self.srtt = initial_timeout  # Smoothed RTT
        self.rttvar = initial_timeout / 2  # RTT variance
        self.rto = initial_timeout  # Retransmission timeout
        
    def update(self, measured_rtt: float):
        """Update timeout based on new RTT measurement"""
# TODO: Implement TCP-style RTO calculation
# SRTT = (1-α) * SRTT + α * RTT
# RTTVAR = (1-β) * RTTVAR + β * |SRTT - RTT|
# RTO = SRTT + 4 * RTTVAR
        
        alpha = 0.125  # 1/8
        beta = 0.25   # 1/4
        
# Your implementation here
        pass
    
    def get_timeout(self) -> float:
        """Get current timeout value"""
        return self.rto
    
    def should_use_exponential_backoff(self, consecutive_timeouts: int) -> float:
        """Calculate timeout with exponential backoff"""
# TODO: Double timeout for each consecutive timeout
# Cap at maximum (e.g., 60 seconds)
        pass

# Test timeout adaptation
def simulate_variable_network():
    timeout = AdaptiveTimeout()
    
# Simulate network with variable latency
    latencies = []
    
# Normal conditions (50-100ms)
    latencies.extend(np.random.normal(75, 10, 50))
    
# Congestion spike (200-500ms)
    latencies.extend(np.random.normal(350, 50, 20))
    
# Return to normal
    latencies.extend(np.random.normal(75, 10, 30))
    
# TODO: Feed latencies to timeout algorithm
# Plot how timeout adapts to conditions
```

### Task 2: Timeout vs Retry Strategy
```python
class RetryStrategy:
    def __init__(self):
        self.timeout_calculator = AdaptiveTimeout()
        self.max_retries = 3
        self.hedge_delay = 0.01  # 10ms
        
    async def execute_with_retry(self, operation, *args):
        """Execute operation with retries"""
        attempts = 0
        errors = []
        
        while attempts < self.max_retries:
            try:
                timeout = self.timeout_calculator.get_timeout()
                if attempts > 0:
# Exponential backoff on retries
                    timeout *= (2 ** attempts)
                
# TODO: Execute with timeout
                result = await asyncio.wait_for(
                    operation(*args), 
                    timeout=timeout
                )
                return result
                
            except asyncio.TimeoutError:
                errors.append(f"Attempt {attempts + 1} timed out")
                attempts += 1
                
        raise Exception(f"All retries failed: {errors}")
    
    async def execute_with_hedging(self, replicas: List, operation, *args):
        """Execute with hedge requests to multiple replicas"""
# TODO: Implement hedged requests
# 1. Send to first replica
# 2. After hedge_delay, send to second replica
# 3. Return first successful response
# 4. Cancel other pending requests
        pass
```

## Exercise 5: Message Ordering Guarantees

### Objective
Implement different message ordering guarantees and understand their trade-offs.

### Task 1: FIFO Ordering
```python
class FIFOChannel:
    def __init__(self, sender_id: str, receiver_id: str):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.send_seq = 0
        self.recv_seq = 0
        self.out_of_order_buffer = {}
        
    def send(self, message: Any) -> Dict:
        """Send message with FIFO guarantee"""
# TODO: Add sequence number
        envelope = {
            'seq': self.send_seq,
            'sender': self.sender_id,
            'message': message
        }
        self.send_seq += 1
        return envelope
    
    def receive(self, envelope: Dict) -> Optional[Any]:
        """Receive message preserving FIFO order"""
# TODO: Implement FIFO delivery
# 1. If seq == expected, deliver and check buffer
# 2. If seq > expected, buffer for later
# 3. If seq < expected, duplicate (ignore)
        pass
```

### Task 2: Causal Ordering
```python
class CausalBroadcast:
    def __init__(self, node_id: str, all_nodes: List[str]):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id, all_nodes)
        self.delivery_buffer = []
        self.delivered = set()
        
    def broadcast(self, message: Any) -> Dict:
        """Broadcast with causal ordering"""
# TODO: Attach vector clock to message
        pass
    
    def receive(self, envelope: Dict):
        """Buffer received message"""
        self.delivery_buffer.append(envelope)
        self.try_deliver()
    
    def try_deliver(self):
        """Deliver messages that are causally ready"""
# TODO: Implement causal delivery condition
# Message m from j is deliverable if:
# 1. m.clock[j] = local.clock[j] + 1
# 2. For all k != j: m.clock[k] <= local.clock[k]
        pass
```

### Task 3: Total Ordering
```python
class TotalOrderBroadcast:
    def __init__(self, node_id: str, sequencer_node: str):
        self.node_id = node_id
        self.sequencer = sequencer_node
        self.seq_num = 0
        self.pending = {}  # seq -> message
        self.next_deliver = 0
        
    async def broadcast(self, message: Any):
        """Broadcast with total ordering via sequencer"""
        if self.node_id == self.sequencer:
# Sequencer assigns sequence number
            seq = self.seq_num
            self.seq_num += 1
# TODO: Broadcast (message, seq) to all
        else:
# TODO: Send to sequencer for ordering
            pass
    
    def handle_ordered_message(self, message: Any, seq: int):
        """Handle message with sequence number"""
# TODO: Deliver in sequence number order
# Buffer out-of-order messages
        pass
```

## Exercise 6: Clock Synchronization

### Objective
Implement and analyze clock synchronization algorithms.

### Task 1: Network Time Protocol (NTP) Basics
```python
class NTPClient:
    def __init__(self, local_clock_offset: float = 0.0):
        self.offset = local_clock_offset  # Local clock error
        self.drift_rate = random.uniform(-50, 50) / 1e6  # 50 ppm
        self.start_time = time.time()
        
    def local_time(self) -> float:
        """Get local time (with drift and offset)"""
        elapsed = time.time() - self.start_time
        drift = elapsed * self.drift_rate
        return time.time() + self.offset + drift
    
    def sync_with_server(self, server_time_func) -> float:
        """Perform NTP-style time sync"""
# TODO: Implement NTP algorithm
# 1. Record local time T1
# 2. Request server time
# 3. Server records T2 (receive) and T3 (send)
# 4. Record local time T4
# 5. Calculate offset and round-trip delay
        
        t1 = self.local_time()
# Simulate network delay
        time.sleep(random.uniform(0.01, 0.05))
        
        t2, t3 = server_time_func()
        
        time.sleep(random.uniform(0.01, 0.05))
        t4 = self.local_time()
        
# TODO: Calculate clock offset
# offset = ((t2 - t1) + (t3 - t4)) / 2
# delay = (t4 - t1) - (t3 - t2)
        
        return offset
```

### Task 2: Berkeley Algorithm
```python
class BerkeleyMaster:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        
    async def synchronize_clocks(self):
        """Coordinate clock synchronization"""
# TODO: Implement Berkeley algorithm
# 1. Poll all nodes for their time
# 2. Calculate average (excluding outliers)
# 3. Send adjustment to each node
        
        times = {}
        for node in self.nodes:
            times[node] = await self.get_node_time(node)
        
# TODO: Calculate fault-tolerant average
# Exclude times that differ too much
        
# TODO: Send adjustments
        pass
```

## Exercise 7: Distributed Consensus with Asynchrony

### Objective
Implement consensus algorithms that handle asynchronous networks.

### Task 1: Timeout-Based Consensus
```python
class TimeoutConsensus:
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.nodes = nodes
        self.timeout = AdaptiveTimeout()
        self.view = 0
        self.proposals = {}
        
    async def propose(self, value: Any):
        """Propose a value for consensus"""
        leader = self.nodes[self.view % len(self.nodes)]
        
        if self.node_id == leader:
# Leader broadcasts proposal
            await self.broadcast_proposal(value)
        else:
# Follower waits for proposal
            try:
                proposal = await asyncio.wait_for(
                    self.wait_for_proposal(),
                    timeout=self.timeout.get_timeout()
                )
# TODO: Validate and vote
            except asyncio.TimeoutError:
# TODO: Trigger view change
                self.view += 1
```

### Task 2: FLP Workaround - Randomization
```python
class RandomizedConsensus:
    """Use randomization to achieve consensus despite FLP"""
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.nodes = nodes
        self.round = 0
        self.estimate = None
        
    async def ben_or_consensus(self, initial_value: bool):
        """Ben-Or randomized consensus algorithm"""
        self.estimate = initial_value
        
        while True:
            self.round += 1
            
# Phase 1: Broadcast estimate
            votes = await self.collect_votes(self.estimate)
            
# TODO: Count votes
            if votes[True] > len(self.nodes) / 2:
                self.estimate = True
                if votes[True] > 2 * len(self.nodes) / 3:
                    return True  # Decide True
            elif votes[False] > len(self.nodes) / 2:
                self.estimate = False
                if votes[False] > 2 * len(self.nodes) / 3:
                    return False  # Decide False
            else:
# No majority - use randomization
                self.estimate = random.choice([True, False])
```

## Synthesis Questions

After completing these exercises, you should be able to answer:

1. **Why can't we have perfect time synchronization in distributed systems?**
2. **How do logical clocks help us reason about distributed system behavior?**
3. **What's the fundamental difference between "slow" and "failed"?**
4. **Why do timeout-based failure detectors have unavoidable false positives?**
5. **How does asynchrony make consensus impossible without additional assumptions?**

## Additional Challenges

1. **Build an Asynchrony Visualizer**: Create a tool that visualizes message delays, clock skew, and race conditions in a distributed system simulation

2. **Implement Hybrid Logical Clocks**: Build a production-ready HLC implementation that handles clock skew gracefully

3. **Design a Chaos Test**: Create chaos engineering tests that specifically target timing assumptions in your system

[**← Back to Law of Asynchrony**](index.md) | [**→ Next: Law of Emergence Exercises**](/part1-axioms/law3-emergence/exercises)