# Truth Distribution Examples & Case Studies

!!! info "Prerequisites"
    - [Distribution of Truth Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Truth Distribution Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Pillars Overview](../index.md)

## Real-World Truth Distribution Failures

<div class="failure-vignette">

### 🎬 The Split-Brain Social Network Disaster

```yaml
Company: Major social network
Date: November 2019
Duration: 12 minutes
Impact: 100K+ conflicting posts

What happened:
- Routine network maintenance
- Firewall rule change gone wrong
- East/West datacenters disconnected

The split:
West Coast DC          East Coast DC
[Master thinks         [Master thinks
 it's primary]         it's primary]
     ↓                      ↓
Accepts writes         Accepts writes
     ↓                      ↓
User posts             User posts
diverge                diverge

Timeline of chaos:
10:15 - Network partition begins
10:16 - Automatic failover triggers
10:17 - BOTH sides think they're master
10:18 - Users start posting to both
10:27 - Ops team notices the split
10:28 - Attempt to reconnect fails

The damage:
- 50K posts on West Coast
- 50K posts on East Coast  
- Friends seeing different timelines
- Comments on posts that "don't exist"
- Likes counting differently

Resolution attempts:
Attempt 1: Last-write-wins
- Picked East Coast as winner
- West Coast posts "vanished"
- User revolt on Twitter

Attempt 2: Merge everything
- Duplicate posts appeared
- Broken conversation threads
- Inconsistent like counts

Final resolution:
- Custom UI showing both versions
- "This post has conflicts" banner
- Let users choose version
- 3 weeks to fully resolve
- Some data permanently inconsistent

Lessons learned:
1. Automatic failover can cause split-brain
2. Some conflicts need human judgment
3. Network partitions are not theoretical
4. Design for partition tolerance
5. Have a conflict resolution strategy
```

</div>

<div class="failure-vignette">

### 🎬 The Bitcoin Double-Spend Attempt

```yaml
Incident: Bitcoin Blockchain Fork
Date: March 2013
Duration: 6 hours
Impact: 24 blocks on different chains

What happened:
- Bitcoin v0.8 released
- Different database (LevelDB)
- Larger blocks now possible
- Old nodes rejected large blocks

The fork:
Miners on v0.7          Miners on v0.8
     ↓                       ↓
Small blocks            Large blocks
     ↓                       ↓
Chain A                 Chain B
(shorter)               (longer)

Consensus breakdown:
- Two valid chains existed
- Merchants accepting different truth
- Double-spend window opened
- $10,000 successfully double-spent

Emergency response:
1. Core developers alerted
2. Major mining pools contacted
3. Agreed to mine on v0.7 chain
4. v0.8 miners downgraded
5. v0.8 chain abandoned

Resolution:
- 24 blocks orphaned
- Some transactions lost
- Merchants ate the losses
- Consensus restored

Lessons:
1. Consensus rules must be explicit
2. Backwards compatibility critical
3. Social consensus can override code
4. Truth can temporarily fork
```

</div>

<div class="failure-vignette">

### 🎬 The Elasticsearch Split-Brain Syndrome

```yaml
Company: E-commerce platform
Service: Product search
Date: Black Friday 2020

Architecture:
- 5-node Elasticsearch cluster
- Master election quorum: 3 nodes
- Network: Spanning 2 racks

What went wrong:
- Rack switch failure
- Cluster split: 3 nodes | 2 nodes
- BOTH sides had quorum of 3!
- (Misconfigured: counted non-voting nodes)

The divergence:
Rack A (3 nodes)        Rack B (2 nodes)
- Sees 3/5 nodes        - Sees 3/5 nodes (!)
- Elects master A       - Elects master B
- Accepts updates       - Accepts updates
- Indexes products      - Indexes products

Customer impact:
- Search results inconsistent
- Products appearing/disappearing
- Inventory counts wrong
- Prices showing differently

Discovery timeline:
Hour 1: "Search seems flaky"
Hour 2: "Must be caching issues"
Hour 3: "Why are metrics different?"
Hour 4: "OH NO - split brain!"

Recovery nightmare:
- 4 hours of divergent updates
- Which side is "truth"?
- Can't merge indices easily
- Black Friday traffic ongoing!

Emergency fix:
1. Route all traffic to Rack A
2. Snapshot Rack B data
3. Manual reconciliation
4. Fix quorum configuration
5. Rebuild cluster topology

Permanent fix:
minimum_master_nodes: 3  # Actual voting nodes
discovery.zen.ping.unicast.hosts: 
  - Only voting nodes listed
cluster.fault_detection.leader_check.interval: 1s

Cost:
- $2M in lost sales
- 48 hours of engineering time
- Customer trust damaged
```

</div>

## Consensus Implementation Examples

### 1. Simplified Raft Implementation

```python
import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    command: str
    index: int

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state = NodeState.FOLLOWER
        
        # Persistent state
        self.current_term = 0
        self.voted_for = None
        self.log: List[LogEntry] = []
        
        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index = {}
        self.match_index = {}
        
        # Timing
        self.election_timeout = self._random_timeout()
        self.last_heartbeat = time.time()
        
    def _random_timeout(self):
        """Generate random election timeout between 150-300ms"""
        return random.uniform(0.15, 0.3)
    
    def start_election(self):
        """Transition to candidate and start election"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.election_timeout = self._random_timeout()
        
        print(f"Node {self.node_id} starting election for term {self.current_term}")
        
        # Request votes from all peers
        votes_received = 1  # Vote for self
        
        for peer in self.peers:
            vote_granted = self._request_vote(peer)
            if vote_granted:
                votes_received += 1
                
        # Check if won election
        if votes_received > (len(self.peers) + 1) // 2:
            self.become_leader()
        else:
            self.state = NodeState.FOLLOWER
            
    def _request_vote(self, peer: str) -> bool:
        """Request vote from peer (simulated)"""
        request = {
            'term': self.current_term,
            'candidate_id': self.node_id,
            'last_log_index': len(self.log) - 1,
            'last_log_term': self.log[-1].term if self.log else 0
        }
        
        # Simulate network call
        # In real implementation, this would be RPC
        response = self._simulate_vote_response(peer, request)
        
        if response['term'] > self.current_term:
            self.current_term = response['term']
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            
        return response['vote_granted']
    
    def become_leader(self):
        """Transition to leader state"""
        self.state = NodeState.LEADER
        print(f"Node {self.node_id} became leader for term {self.current_term}")
        
        # Initialize leader state
        for peer in self.peers:
            self.next_index[peer] = len(self.log)
            self.match_index[peer] = 0
            
        # Send initial heartbeat
        self.send_heartbeat()
        
    def send_heartbeat(self):
        """Send heartbeat to all followers"""
        for peer in self.peers:
            self._append_entries(peer, heartbeat=True)
            
    def replicate_entry(self, command: str):
        """Leader replicates a new entry"""
        if self.state != NodeState.LEADER:
            return False
            
        # Append to own log
        entry = LogEntry(
            term=self.current_term,
            command=command,
            index=len(self.log)
        )
        self.log.append(entry)
        
        # Replicate to followers
        successful_replications = 1  # Count self
        
        for peer in self.peers:
            if self._append_entries(peer):
                successful_replications += 1
                
        # Commit if replicated to majority
        if successful_replications > (len(self.peers) + 1) // 2:
            self.commit_index = entry.index
            return True
            
        return False
    
    def _append_entries(self, peer: str, heartbeat=False) -> bool:
        """Send AppendEntries RPC to peer"""
        prev_log_index = self.next_index[peer] - 1
        prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0
        
        entries = []
        if not heartbeat and self.next_index[peer] < len(self.log):
            entries = self.log[self.next_index[peer]:]
            
        request = {
            'term': self.current_term,
            'leader_id': self.node_id,
            'prev_log_index': prev_log_index,
            'prev_log_term': prev_log_term,
            'entries': entries,
            'leader_commit': self.commit_index
        }
        
        # Simulate network call
        response = self._simulate_append_response(peer, request)
        
        if response['success']:
            if entries:
                self.next_index[peer] += len(entries)
                self.match_index[peer] = self.next_index[peer] - 1
            return True
        else:
            # Decrement next_index and retry
            self.next_index[peer] = max(0, self.next_index[peer] - 1)
            return False

# Usage example
nodes = []
node_ids = ['node1', 'node2', 'node3', 'node4', 'node5']

for node_id in node_ids:
    peers = [n for n in node_ids if n != node_id]
    nodes.append(RaftNode(node_id, peers))

# Simulate election
nodes[0].start_election()

# Leader replicates entries
if nodes[0].state == NodeState.LEADER:
    nodes[0].replicate_entry("SET x=1")
    nodes[0].replicate_entry("SET y=2")
```

### 2. Vector Clock Implementation

```python
from collections import defaultdict
from typing import Dict, Tuple, Optional

class VectorClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock: Dict[str, int] = defaultdict(int)
        
    def increment(self):
        """Increment own clock value"""
        self.clock[self.node_id] += 1
        
    def update(self, other_clock: Dict[str, int]):
        """Update clock based on received clock"""
        # Take maximum of each component
        for node, timestamp in other_clock.items():
            self.clock[node] = max(self.clock[node], timestamp)
            
        # Increment own component
        self.increment()
        
    def compare(self, other: 'VectorClock') -> str:
        """Compare two vector clocks"""
        self_greater = False
        other_greater = False
        
        all_nodes = set(self.clock.keys()) | set(other.clock.keys())
        
        for node in all_nodes:
            self_val = self.clock.get(node, 0)
            other_val = other.clock.get(node, 0)
            
            if self_val > other_val:
                self_greater = True
            elif other_val > self_val:
                other_greater = True
                
        if self_greater and not other_greater:
            return "happens-after"
        elif other_greater and not self_greater:
            return "happens-before"
        elif not self_greater and not other_greater:
            return "equal"
        else:
            return "concurrent"
    
    def merge(self, other: 'VectorClock'):
        """Merge two vector clocks (take component-wise maximum)"""
        all_nodes = set(self.clock.keys()) | set(other.clock.keys())
        
        for node in all_nodes:
            self.clock[node] = max(
                self.clock.get(node, 0),
                other.clock.get(node, 0)
            )

class VectorClockDB:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id)
        self.data: Dict[str, Tuple[any, VectorClock]] = {}
        
    def put(self, key: str, value: any):
        """Write with vector clock"""
        self.vector_clock.increment()
        self.data[key] = (value, VectorClock(self.node_id))
        self.data[key][1].clock = self.vector_clock.clock.copy()
        
    def get(self, key: str) -> Optional[Tuple[any, Dict[str, int]]]:
        """Read with vector clock"""
        if key in self.data:
            value, vc = self.data[key]
            return (value, vc.clock)
        return None
        
    def merge_remote(self, key: str, remote_value: any, 
                     remote_clock: Dict[str, int]):
        """Merge remote update"""
        remote_vc = VectorClock(self.node_id)
        remote_vc.clock = remote_clock.copy()
        
        if key not in self.data:
            # New key
            self.data[key] = (remote_value, remote_vc)
            self.vector_clock.update(remote_clock)
        else:
            local_value, local_vc = self.data[key]
            comparison = local_vc.compare(remote_vc)
            
            if comparison == "happens-before":
                # Remote is newer
                self.data[key] = (remote_value, remote_vc)
                self.vector_clock.update(remote_clock)
            elif comparison == "concurrent":
                # Conflict! Need resolution
                resolved = self.resolve_conflict(
                    key, local_value, local_vc,
                    remote_value, remote_vc
                )
                self.data[key] = resolved
                self.vector_clock.update(remote_clock)
            # else local is newer, keep it
            
    def resolve_conflict(self, key: str, 
                        local_value: any, local_vc: VectorClock,
                        remote_value: any, remote_vc: VectorClock):
        """Resolve concurrent updates"""
        # Application-specific resolution
        # Here we'll merge both values
        merged_value = {
            'local': local_value,
            'remote': remote_value,
            'conflict': True
        }
        
        # Merge vector clocks
        merged_vc = VectorClock(self.node_id)
        merged_vc.clock = local_vc.clock.copy()
        merged_vc.merge(remote_vc)
        merged_vc.increment()
        
        return (merged_value, merged_vc)

# Example usage
db1 = VectorClockDB("node1")
db2 = VectorClockDB("node2")

# Concurrent updates
db1.put("user:123", {"name": "Alice", "age": 30})
db2.put("user:123", {"name": "Alice", "age": 31})

# Exchange updates
value1, clock1 = db1.get("user:123")
value2, clock2 = db2.get("user:123")

db1.merge_remote("user:123", value2, clock2)
db2.merge_remote("user:123", value1, clock1)

# Both detect conflict
print(db1.get("user:123"))  # Shows conflict
print(db2.get("user:123"))  # Shows conflict
```

### 3. CRDT Implementation (G-Counter)

```python
class GCounter:
    """Grow-only counter CRDT"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: Dict[str, int] = defaultdict(int)
        
    def increment(self, value: int = 1):
        """Increment counter"""
        if value < 0:
            raise ValueError("GCounter can only grow")
        self.counts[self.node_id] += value
        
    def value(self) -> int:
        """Get current counter value"""
        return sum(self.counts.values())
        
    def merge(self, other: 'GCounter'):
        """Merge with another GCounter"""
        for node_id, count in other.counts.items():
            self.counts[node_id] = max(
                self.counts[node_id],
                count
            )
            
    def compare(self, other: 'GCounter') -> bool:
        """Check if this counter >= other"""
        for node_id, count in other.counts.items():
            if self.counts.get(node_id, 0) < count:
                return False
        return True

class PNCounter:
    """Increment/decrement counter using two GCounters"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.positive = GCounter(node_id)
        self.negative = GCounter(node_id)
        
    def increment(self, value: int = 1):
        """Increment counter"""
        if value >= 0:
            self.positive.increment(value)
        else:
            self.negative.increment(-value)
            
    def value(self) -> int:
        """Get current value"""
        return self.positive.value() - self.negative.value()
        
    def merge(self, other: 'PNCounter'):
        """Merge with another PNCounter"""
        self.positive.merge(other.positive)
        self.negative.merge(other.negative)

# Usage example
# Node 1 increments by 5
counter1 = PNCounter("node1")
counter1.increment(5)

# Node 2 increments by 3
counter2 = PNCounter("node2")
counter2.increment(3)

# Node 3 decrements by 2
counter3 = PNCounter("node3")
counter3.increment(-2)

# Merge all states
counter1.merge(counter2)
counter1.merge(counter3)

counter2.merge(counter1)
counter2.merge(counter3)

counter3.merge(counter1)
counter3.merge(counter2)

# All nodes converge to same value
print(f"Counter1: {counter1.value()}")  # 6
print(f"Counter2: {counter2.value()}")  # 6
print(f"Counter3: {counter3.value()}")  # 6
```

## Production Truth Systems

### Google's Chubby Lock Service

```yaml
Purpose: Distributed lock service
Based on: Paxos consensus

Architecture:
- 5 replicas (tolerates 2 failures)
- Master elected via Paxos
- All writes through master
- Reads can be from any replica

Key features:
- Coarse-grained locks (held for hours/days)
- Small files (configuration)
- Event notifications
- Session-based

Interesting details:
- Master lease: 12 seconds
- Client cache with invalidation
- Graceful master failover
- Used by GFS, Bigtable, etc.

Lessons:
1. Consensus for control plane, not data plane
2. Caching critical for performance
3. Session semantics prevent split-brain
4. Master lease prevents dueling masters
```

### etcd in Kubernetes

```yaml
Role: Configuration store for Kubernetes
Based on: Raft consensus

Design choices:
- Strong consistency (linearizable)
- Watch API for changes
- Transaction support
- TTL for ephemeral data

Scale limits:
- Database size: 8GB default
- Request size: 1.5MB
- 1000 writes/second sustained

Optimizations:
- Lease-based TTLs
- Batch commits
- Snapshot compression
- Incremental snapshots

Common issues:
1. Large objects (ConfigMaps)
2. Too many watchers
3. Disk latency sensitivity
4. Memory pressure from snapshots
```

### Amazon DynamoDB Global Tables

```yaml
Feature: Multi-region active-active
Consistency: Eventual with LWW

How it works:
1. Each region accepts writes
2. Changes streamed via DynamoDB Streams
3. Cross-region replication ~1 second
4. Conflict resolution: Last-writer-wins

Conflict detection:
- Item-level timestamps
- Microsecond precision
- Region ID for tie-breaking

Use cases:
- User profiles
- Product catalogs  
- Session data
- Gaming leaderboards

Limitations:
- No transactions across regions
- No strong consistency globally
- LWW may lose updates
- Cost of replication
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Split-brain is inevitable** - Design assuming it will happen
    2. **Automatic failover can make things worse** - Sometimes manual intervention is better
    3. **Consensus doesn't mean correctness** - You can agree on the wrong thing
    4. **Clocks lie** - Never trust timestamps alone
    5. **Conflicts need business logic** - Technical resolution isn't enough

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Truth Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of Control](../pillar-4-control/index.md) →
    
    **Related**: [Coordination Cost](../../part1-axioms/axiom-5-coordination/index.md)