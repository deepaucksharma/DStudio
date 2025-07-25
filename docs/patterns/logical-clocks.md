---
title: Logical Clocks (Lamport Clocks)
description: Order events in distributed systems without synchronized physical clocks using happens-before relationships
type: pattern
category: coordination
difficulty: intermediate
reading_time: 35 min
prerequisites: [distributed-systems-basics, causality, event-ordering]
when_to_use: When you need causal ordering of events, don't need wall-clock time, and want a simple solution
when_not_to_use: When you need to detect concurrent events (use vector clocks) or need actual timestamps
status: complete
last_updated: 2025-01-23
---


# Logical Clocks (Lamport Clocks) Pattern

<div class="pattern-header">
  <div class="pattern-type">Coordination Pattern</div>
  <div class="pattern-summary">Establish a partial ordering of events in a distributed system using logical timestamps that respect causality without requiring synchronized physical clocks.</div>
</div>

## Problem Context

<div class="problem-box">
<h3>🎯 The Challenge</h3>

In distributed systems, we often need to order events, but:
- **Physical clocks are unreliable**: They drift and require synchronization
- **Network delays are variable**: Can't use arrival time for ordering
- **Causality matters**: If event A caused event B, A must come before B
- **Total ordering needed**: For replicated state machines, logs, etc.

Lamport clocks solve this by creating a logical notion of time based on causality.
</div>

## Core Concept

### The Happens-Before Relation (→)

```mermaid
graph TD
    subgraph "Happens-Before Definition"
        A[Event A] -->|1. Same Process| B[Event B]
        C[Send Message] -->|2. Communication| D[Receive Message]
        E[Event E] -->|3. Transitivity| F[Event F]
        F --> G[Event G]
        E --> G
    end
    
    subgraph "Examples"
        P1E1[P1: Write X] --> P1E2[P1: Write Y]
        P1E3[P1: Send M] --> P2E1[P2: Receive M]
        P2E1 --> P2E2[P2: Write Z]
        P1E3 --> P2E2
    end
```

<div class="law-box">
<h3>🔑 Lamport's Insight</h3>

If we can't synchronize physical clocks perfectly, let's abandon physical time altogether and use logical time based on causality:

**If A → B (A happens-before B), then Clock(A) < Clock(B)**

This preserves causality without needing synchronized clocks!
</div>

## How Lamport Clocks Work

### Algorithm Rules

```python
class LamportClock:
    def __init__(self):
        self.clock = 0
        
    def local_event(self):
        """Rule 1: Before any local event, increment clock"""
        self.clock += 1
        return self.clock
    
    def send_message(self, message):
        """Rule 2: Before sending, increment clock and attach timestamp"""
        self.clock += 1
        message['timestamp'] = self.clock
        return message
    
    def receive_message(self, message):
        """Rule 3: On receive, update clock to max(local, received) + 1"""
        self.clock = max(self.clock, message['timestamp']) + 1
        return self.clock
```

### Visual Example

```mermaid
sequenceDiagram
    participant P1
    participant P2
    participant P3
    
    Note over P1,P3: Initial clocks: 0
    
    P1->>P1: Local event<br/>C1 = 1
    P2->>P2: Local event<br/>C2 = 1
    
    P1->>P2: Send M1<br/>timestamp = 1
    Note over P2: Receive M1<br/>C2 = max(1,1)+1 = 2
    
    P2->>P3: Send M2<br/>timestamp = 3
    P2->>P2: Local event<br/>C2 = 4
    
    Note over P3: Receive M2<br/>C3 = max(0,3)+1 = 4
    
    P3->>P1: Send M3<br/>timestamp = 5
    Note over P1: Receive M3<br/>C1 = max(1,5)+1 = 6
```

## Implementation

### Basic Lamport Clock

```python
import threading
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Event:
    process_id: str
    event_type: str
    timestamp: int
    data: Any = None

class DistributedProcess:
    def __init__(self, process_id: str):
        self.process_id = process_id
        self.clock = LamportClock()
        self.event_log = []
        self.lock = threading.Lock()
        
    def execute_local_operation(self, operation: str) -> Event:
        """Execute a local operation"""
        with self.lock:
            timestamp = self.clock.local_event()
            event = Event(
                process_id=self.process_id,
                event_type="local",
                timestamp=timestamp,
                data=operation
            )
            self.event_log.append(event)
            return event
    
    def send_message(self, recipient: 'DistributedProcess', 
                    content: Any) -> Event:
        """Send a message to another process"""
        with self.lock:
            message = {'content': content}
            self.clock.send_message(message)
            
            event = Event(
                process_id=self.process_id,
                event_type="send",
                timestamp=message['timestamp'],
                data={'to': recipient.process_id, 'content': content}
            )
            self.event_log.append(event)
            
# Simulate network delay
        recipient.receive_message(self.process_id, message)
        return event
    
    def receive_message(self, sender_id: str, message: Dict) -> Event:
        """Receive a message from another process"""
        with self.lock:
            timestamp = self.clock.receive_message(message)
            
            event = Event(
                process_id=self.process_id,
                event_type="receive",
                timestamp=timestamp,
                data={'from': sender_id, 'content': message['content']}
            )
            self.event_log.append(event)
            return event
```

### Total Ordering with Process IDs

```python
class TotallyOrderedLamportClock(LamportClock):
    """Extended Lamport Clock with total ordering"""
    
    def __init__(self, process_id: int):
        super().__init__()
        self.process_id = process_id
        
    def get_timestamp(self) -> tuple:
        """Return (clock, process_id) for total ordering"""
        return (self.clock, self.process_id)
    
    def compare_events(self, e1: Event, e2: Event) -> int:
        """
        Compare two events for total ordering
        Returns: -1 if e1 < e2, 0 if equal, 1 if e1 > e2
        """
# First compare logical timestamps
        if e1.timestamp < e2.timestamp:
            return -1
        elif e1.timestamp > e2.timestamp:
            return 1
        else:
# Break ties with process ID
            if e1.process_id < e2.process_id:
                return -1
            elif e1.process_id > e2.process_id:
                return 1
            else:
                return 0
```

## Practical Applications

### 1. Distributed Mutual Exclusion

```python
class LamportMutex:
    """Lamport's distributed mutual exclusion algorithm"""
    
    def __init__(self, process_id: int, num_processes: int):
        self.process_id = process_id
        self.clock = TotallyOrderedLamportClock(process_id)
        self.request_queue = []  # Priority queue of requests
        self.replies_received = set()
        self.num_processes = num_processes
        
    def request_critical_section(self):
        """Request access to critical section"""
# 1. Send timestamped request to all processes
        timestamp = self.clock.local_event()
        request = {
            'type': 'REQUEST',
            'process_id': self.process_id,
            'timestamp': timestamp
        }
        
        self.request_queue.append(request)
        self.request_queue.sort(key=lambda r: (r['timestamp'], r['process_id']))
        
# Broadcast request to all other processes
        self.broadcast(request)
        
# 2. Wait for replies from all processes
        while len(self.replies_received) < self.num_processes - 1:
            time.sleep(0.01)
            
# 3. Enter CS when request is at head of queue
        while (self.request_queue[0]['process_id'] != self.process_id or
               not self.all_replies_received()):
            time.sleep(0.01)
            
    def release_critical_section(self):
        """Release critical section"""
# Remove own request from queue
        self.request_queue = [r for r in self.request_queue 
                            if r['process_id'] != self.process_id]
        
# Send RELEASE to all processes
        release_msg = {
            'type': 'RELEASE',
            'process_id': self.process_id,
            'timestamp': self.clock.local_event()
        }
        self.broadcast(release_msg)
        
        self.replies_received.clear()
```

### 2. Consistent Snapshots

```python
class SnapshotProcess:
    """Process participating in consistent snapshot algorithm"""
    
    def __init__(self, process_id: str):
        self.process_id = process_id
        self.clock = LamportClock()
        self.state = {}
        self.snapshot_clock = None
        self.recorded_state = None
        
    def initiate_snapshot(self):
        """Initiate a consistent snapshot"""
        self.snapshot_clock = self.clock.clock
        self.recorded_state = self.state.copy()
        
# Send marker messages to all neighbors
        marker = {
            'type': 'MARKER',
            'snapshot_id': f"{self.process_id}:{self.snapshot_clock}"
        }
        self.broadcast_marker(marker)
        
    def receive_marker(self, marker, sender_id):
        """Handle snapshot marker"""
        if self.snapshot_clock is None:
# First marker: record local state
            self.snapshot_clock = self.clock.clock
            self.recorded_state = self.state.copy()
            
# Forward marker to all other neighbors
            self.broadcast_marker(marker)
        
# Record channel state (messages in transit)
        self.record_channel_state(sender_id)
```

## Limitations and Solutions

### Limitation 1: Can't Detect Concurrent Events

```mermaid
graph TD
    subgraph "Concurrent Events Problem"
        P1A[P1: Event A<br/>Clock = 1]
        P2B[P2: Event B<br/>Clock = 1]
        
        Note1[A and B are concurrent<br/>but have same timestamp!]
    end
    
    subgraph "Solution: Vector Clocks"
        P1A2[P1: Event A<br/>VC = [1,0]]
        P2B2[P2: Event B<br/>VC = [0,1]]
        
        Note2[Vector clocks can<br/>detect concurrency]
    end
```

### Limitation 2: Clock Values Grow Unbounded

```python
class BoundedLamportClock(LamportClock):
    """Lamport clock with periodic reset"""
    
    def __init__(self, epoch_size=1000000):
        super().__init__()
        self.epoch = 0
        self.epoch_size = epoch_size
        
    def increment(self):
        """Increment with epoch management"""
        self.clock += 1
        
        if self.clock >= self.epoch_size:
# Start new epoch
            self.epoch += 1
            self.clock = 0
            
    def get_full_timestamp(self):
        """Return (epoch, clock) tuple"""
        return (self.epoch, self.clock)
```

## Comparison with Other Clock Types

<div class="comparison-table">
<table>
<thead>
<tr>
<th>Feature</th>
<th>Physical Clocks</th>
<th>Lamport Clocks</th>
<th>Vector Clocks</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Purpose</strong></td>
<td>Wall-clock time</td>
<td>Causal ordering</td>
<td>Detect concurrency</td>
</tr>
<tr>
<td><strong>Space</strong></td>
<td>O(1)</td>
<td>O(1)</td>
<td>O(N)</td>
</tr>
<tr>
<td><strong>Sync Required</strong></td>
<td>Yes</td>
<td>No</td>
<td>No</td>
</tr>
<tr>
<td><strong>Concurrent Events</strong></td>
<td>Same time</td>
<td>Arbitrary order</td>
<td>Detected</td>
</tr>
<tr>
<td><strong>Use Case</strong></td>
<td>Timestamps</td>
<td>Total order</td>
<td>Conflict detection</td>
</tr>
</tbody>
</table>
</div>

## Best Practices

<div class="truth-box">
<h4>🎯 Lamport Clock Guidelines</h4>

1. **Increment before events**: Never forget to increment
2. **Thread safety**: Protect clock updates in concurrent systems
3. **Message validation**: Check timestamp validity on receive
4. **Overflow handling**: Plan for clock value overflow
5. **Total ordering**: Use process IDs to break ties
6. **Persistence**: Save clock value across restarts
7. **Monitoring**: Track clock skew between processes
</div>

## Real-World Usage

### Amazon DynamoDB

```python
class DynamoDBVersionVector:
    """Simplified version of DynamoDB's versioning"""
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.clock = LamportClock()
        self.vector = {}  # node_id -> clock value
        
    def update(self, key, value):
        """Update with version vector"""
        timestamp = self.clock.local_event()
        self.vector[self.node_id] = timestamp
        
        return {
            'key': key,
            'value': value,
            'version': self.vector.copy(),
            'timestamp': timestamp
        }
```

### Distributed Databases

```python
class DistributedTransaction:
    """Transaction with Lamport timestamp ordering"""
    
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id
        self.timestamp = None
        self.operations = []
        
    def begin(self, clock):
        """Begin transaction with timestamp"""
        self.timestamp = clock.local_event()
        
    def add_operation(self, op):
        """Add operation to transaction"""
        self.operations.append({
            'op': op,
            'timestamp': self.timestamp
        })
        
    def commit_order(self, other_txn):
        """Determine commit order based on timestamps"""
        if self.timestamp < other_txn.timestamp:
            return -1  # This transaction first
        elif self.timestamp > other_txn.timestamp:
            return 1   # Other transaction first
        else:
# Use transaction ID to break ties
            return -1 if self.transaction_id < other_txn.transaction_id else 1
```

## Key Insights

<div class="decision-box">
<h4>When to Use Lamport Clocks</h4>

✅ **Use when**:
- Need total ordering of events
- Don't need to detect concurrent events
- Want simple, low-overhead solution
- Building replicated state machines

❌ **Don't use when**:
- Need to detect concurrent updates (use vector clocks)
- Need actual wall-clock time (use NTP)
- System has high churn (clock values lost)
</div>

## Implementation Checklist

- [ ] Implement basic clock increment rules
- [ ] Add thread safety for concurrent access
- [ ] Handle message timestamps properly
- [ ] Implement total ordering with process IDs
- [ ] Add persistence across restarts
- [ ] Monitor clock values for overflow
- [ ] Test with concurrent operations
- [ ] Document ordering guarantees

## Related Patterns

- [Vector Clocks](vector-clocks.md) - Detect concurrent events
- [Clock Synchronization](clock-sync.md) - Physical time sync
- Hybrid Logical Clocks (Coming Soon) - Combine physical and logical
- [Event Sourcing](event-sourcing.md) - Ordered event streams

## References

- "Time, Clocks, and the Ordering of Events in a Distributed System" - Leslie Lamport (1978)
- "Distributed Systems: Principles and Paradigms" - Tanenbaum & Van Steen
- "Distributed Mutual Exclusion Algorithms" - Singhal & Shivaratri

## Use Cases

- Event ordering in distributed logs
- Distributed debugging
- Causal consistency
- Database replication

## Limitations

- Can't detect concurrent events
- No notion of real time
- Requires message passing for synchronization

## Related Patterns

- [Vector Clocks](vector-clocks.md) - Extension for concurrency detection
- [Consensus](consensus.md)
- [Event Sourcing](event-sourcing.md)

---

*This is a stub page. Full content coming soon.*