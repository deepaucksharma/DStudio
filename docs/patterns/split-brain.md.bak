---
title: Split Brain
description: Prevent and handle network partitions that cause clusters to split into multiple independent groups, each believing they are the only valid cluster
type: pattern
category: resilience
difficulty: advanced
reading_time: 40 min
prerequisites: [consensus, leader-election, quorum, distributed-lock]
when_to_use: Multi-node clusters, distributed databases, high-availability systems requiring strong consistency
when_not_to_use: Single-node systems, eventually consistent systems, systems that can tolerate inconsistency
status: complete
last_updated: 2025-07-24
---

# Split Brain


## Overview

Split-brain occurs when a distributed system's nodes are partitioned by network failures, causing multiple groups to operate independently. Each partition believes it's the only valid cluster, leading to data inconsistency, conflicting decisions, and potential data corruption. This pattern covers prevention and resolution strategies.

<div class="axiom-box">
<strong>Axiom 3: Failure Resilience</strong>: Network partitions are inevitable in distributed systems. Split-brain prevention requires careful coordination mechanisms to ensure only one partition can make decisions, even when communication fails.
</div>

## The Split-Brain Problem

Network partitions create independent cluster segments:

```python
# ❌ Naive cluster without split-brain protection
class NaiveCluster:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.is_leader = False
        self.data = {}
    
    def elect_leader(self):
# Dangerous: each partition will elect its own leader
        reachable_peers = self.get_reachable_peers()
        if len(reachable_peers) > 0:
            self.is_leader = (self.node_id == min([self.node_id] + reachable_peers))
        else:
            self.is_leader = True  # ❌ Becomes leader when isolated!
    
    def write_data(self, key, value):
        if self.is_leader:
            self.data[key] = value
# ❌ Multiple leaders can write conflicting data
            return True
        return False

# Network partition scenario:
# Cluster: [A, B, C, D, E] splits into [A, B] and [C, D, E]
# Result: Both partitions elect leaders and accept writes
# Problem: Data diverges and conflicts arise
```

**Split-Brain Consequences**:
- **Data Inconsistency**: Different partitions make conflicting updates
- **Duplicate Processing**: Same tasks executed multiple times
- **Resource Conflicts**: Multiple nodes claiming exclusive resources
- **Service Unavailability**: System becomes unreliable
- **Data Loss**: Partition merging requires conflict resolution

## Core Prevention Strategies

### Quorum-Based Split-Brain Prevention

```python
import time
import threading
import random
from typing import Set, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"
    ISOLATED = "isolated"

@dataclass
class ClusterNode:
    node_id: str
    state: NodeState = NodeState.FOLLOWER
    term: int = 0
    voted_for: Optional[str] = None
    last_heartbeat: float = 0.0
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class QuorumBasedCluster:
    """Cluster with quorum-based split-brain prevention"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.cluster_size = len(cluster_nodes)
        self.quorum_size = (self.cluster_size // 2) + 1
        
# Node state
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        
# Cluster state
        self.leader_id = None
        self.last_heartbeat = time.time()
        self.reachable_nodes: Set[str] = set()
        
# Data storage
        self.data = {}
        self.pending_writes = []
        
# Configuration
        self.heartbeat_interval = 1.0
        self.election_timeout = random.uniform(3.0, 5.0)
        
# Threading
        self._running = True
        self._lock = threading.RLock()
        
# Start background processes
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start heartbeat and election timeout threads"""
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        threading.Thread(target=self._election_timeout_loop, daemon=True).start()
    
    def _heartbeat_loop(self):
        """Send heartbeats if leader, check heartbeats if follower"""
        while self._running:
            with self._lock:
                if self.state == NodeState.LEADER:
                    self._send_heartbeats()
                elif self.state == NodeState.FOLLOWER:
                    self._check_leader_heartbeat()
            
            time.sleep(self.heartbeat_interval)
    
    def _election_timeout_loop(self):
        """Start election if no heartbeat received"""
        while self._running:
            time.sleep(self.election_timeout)
            
            with self._lock:
                if (self.state in [NodeState.FOLLOWER, NodeState.CANDIDATE] and
                    time.time() - self.last_heartbeat > self.election_timeout):
                    self._start_election()
    
    def _send_heartbeats(self):
        """Send heartbeats to all cluster members"""
        self.reachable_nodes = set()
        
        for node in self.cluster_nodes:
            if node != self.node_id:
                if self._send_heartbeat_to_node(node):
                    self.reachable_nodes.add(node)
        
# Check if we still have quorum
        total_reachable = len(self.reachable_nodes) + 1  # +1 for self
        if total_reachable < self.quorum_size:
            print(f"Leader {self.node_id} lost quorum ({total_reachable}/{self.quorum_size})")
            self._step_down()
    
    def _send_heartbeat_to_node(self, node_id: str) -> bool:
        """Send heartbeat to specific node"""
        try:
# Simulate network call
            success = self._simulate_network_call(node_id, {
                'type': 'heartbeat',
                'term': self.current_term,
                'leader_id': self.node_id
            })
            return success
        except Exception:
            return False
    
    def _check_leader_heartbeat(self):
        """Check if leader heartbeat is recent"""
        if time.time() - self.last_heartbeat > self.election_timeout:
            print(f"Node {self.node_id} detected leader failure")
            self._start_election()
    
    def _start_election(self):
        """Start leader election with quorum requirement"""
        print(f"Node {self.node_id} starting election for term {self.current_term + 1}")
        
# Become candidate
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()
        
# Count votes (start with self)
        votes = 1
        
# Request votes from other nodes
        for node in self.cluster_nodes:
            if node != self.node_id:
                if self._request_vote(node):
                    votes += 1
        
        print(f"Node {self.node_id} received {votes}/{self.cluster_size} votes")
        
# Check if we have majority (quorum)
        if votes >= self.quorum_size:
            self._become_leader()
        else:
            print(f"Node {self.node_id} failed to get quorum, stepping down")
            self.state = NodeState.FOLLOWER
            self.voted_for = None
    
    def _request_vote(self, node_id: str) -> bool:
        """Request vote from specific node"""
        try:
            response = self._simulate_network_call(node_id, {
                'type': 'vote_request',
                'term': self.current_term,
                'candidate_id': self.node_id
            })
            return response.get('vote_granted', False)
        except Exception:
            return False
    
    def _become_leader(self):
        """Become cluster leader"""
        print(f"Node {self.node_id} became leader for term {self.current_term}")
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        
# Process any pending writes
        self._process_pending_writes()
    
    def _step_down(self):
        """Step down from leadership"""
        print(f"Node {self.node_id} stepping down from leadership")
        self.state = NodeState.FOLLOWER
        self.leader_id = None
    
    def write_data(self, key: str, value: any) -> bool:
        """Write data with quorum consensus"""
        with self._lock:
            if self.state != NodeState.LEADER:
                return False
            
# Check if we have quorum
            reachable_count = len(self.reachable_nodes) + 1  # +1 for self
            if reachable_count < self.quorum_size:
                print(f"Write rejected: insufficient quorum ({reachable_count}/{self.quorum_size})")
                return False
            
# Replicate to quorum
            replicas = 1  # Count self
            for node in self.reachable_nodes:
                if self._replicate_write(node, key, value):
                    replicas += 1
                
                if replicas >= self.quorum_size:
                    break
            
            if replicas >= self.quorum_size:
# Commit write locally
                self.data[key] = value
                print(f"Write committed: {key}={value} (replicas: {replicas})")
                return True
            else:
                print(f"Write failed: insufficient replicas ({replicas}/{self.quorum_size})")
                return False
    
    def _replicate_write(self, node_id: str, key: str, value: any) -> bool:
        """Replicate write to specific node"""
        try:
            response = self._simulate_network_call(node_id, {
                'type': 'replicate',
                'term': self.current_term,
                'key': key,
                'value': value
            })
            return response.get('success', False)
        except Exception:
            return False
    
    def _process_pending_writes(self):
        """Process writes that were queued during election"""
        for write_op in self.pending_writes:
            self.write_data(write_op['key'], write_op['value'])
        self.pending_writes.clear()
    
    def _simulate_network_call(self, node_id: str, message: dict) -> dict:
        """Simulate network call to another node"""
# Simulate network partition (some nodes unreachable)
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Network timeout")
        
# Simulate processing delay
        time.sleep(0.01)
        
# Mock response based on message type
        if message['type'] == 'heartbeat':
            return {'success': True}
        elif message['type'] == 'vote_request':
            return {'vote_granted': random.random() < 0.8}  # 80% chance
        elif message['type'] == 'replicate':
            return {'success': True}
        
        return {'success': False}
    
    def get_cluster_status(self) -> dict:
        """Get current cluster status"""
        with self._lock:
            return {
                'node_id': self.node_id,
                'state': self.state.value,
                'term': self.current_term,
                'leader': self.leader_id,
                'quorum_size': self.quorum_size,
                'reachable_nodes': len(self.reachable_nodes) + 1,
                'has_quorum': len(self.reachable_nodes) + 1 >= self.quorum_size,
                'data_items': len(self.data)
            }

# Usage example
def simulate_cluster():
    """Simulate cluster with potential split-brain"""
    
    cluster_nodes = ['node_1', 'node_2', 'node_3', 'node_4', 'node_5']
    nodes = {}
    
# Create cluster nodes
    for node_id in cluster_nodes:
        nodes[node_id] = QuorumBasedCluster(node_id, cluster_nodes)
    
# Let cluster stabilize
    time.sleep(2)
    
# Find current leader
    leader = None
    for node in nodes.values():
        status = node.get_cluster_status()
        print(f"{status['node_id']}: {status['state']} (term {status['term']})")
        if status['state'] == 'leader':
            leader = node
    
    if leader:
        print(f"\nLeader: {leader.node_id}")
        
# Try some writes
        leader.write_data('key1', 'value1')
        leader.write_data('key2', 'value2')
    
    return nodes

# Run simulation
# nodes = simulate_cluster()
```

### Witness/Arbiter Node Pattern

```python
class WitnessNode:
    """Lightweight node that participates in quorum but doesn't store data"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.current_term = 0
        self.voted_for = None
        self.active_leader = None
        
    def handle_vote_request(self, candidate_id: str, term: int) -> bool:
        """Vote in leader election"""
        
# Only vote once per term
        if term > self.current_term:
            self.current_term = term
            self.voted_for = candidate_id
            print(f"Witness {self.node_id} voted for {candidate_id} in term {term}")
            return True
        elif term == self.current_term and self.voted_for == candidate_id:
            return True
        
        return False
    
    def handle_heartbeat(self, leader_id: str, term: int):
        """Acknowledge leader heartbeat"""
        if term >= self.current_term:
            self.current_term = term
            self.active_leader = leader_id
            return True
        return False

class WitnessEnabledCluster(QuorumBasedCluster):
    """Cluster with witness nodes for tie-breaking"""
    
    def __init__(self, node_id: str, data_nodes: List[str], witness_nodes: List[str]):
        self.data_nodes = data_nodes
        self.witness_nodes = witness_nodes
        all_nodes = data_nodes + witness_nodes
        
        super().__init__(node_id, all_nodes)
        
# Witness nodes for quorum calculation
        self.witnesses = {}
        if node_id in witness_nodes:
            self.is_witness = True
        else:
            self.is_witness = False
    
    def _calculate_quorum_size(self) -> int:
        """Calculate quorum including witness nodes"""
        total_nodes = len(self.data_nodes) + len(self.witness_nodes)
        return (total_nodes // 2) + 1
    
    def write_data(self, key: str, value: any) -> bool:
        """Witnesses don't store data, only participate in consensus"""
        if self.is_witness:
            return False  # Witnesses can't write data
        
        return super().write_data(key, value)

# Example: 2 data nodes + 1 witness prevents split-brain
data_nodes = ['data_1', 'data_2']
witness_nodes = ['witness_1']

# Even if data nodes are partitioned, witness acts as tie-breaker
cluster_a = WitnessEnabledCluster('data_1', data_nodes, witness_nodes)
cluster_b = WitnessEnabledCluster('data_2', data_nodes, witness_nodes)
witness = WitnessEnabledCluster('witness_1', data_nodes, witness_nodes)
```

## Advanced Split-Brain Prevention

### Disk-Based Quorum (STONITH)

```python
import os
import fcntl
import time
from pathlib import Path

class DiskBasedQuorum:
    """Use shared disk for quorum decisions (STONITH - Shoot The Other Node In The Head)"""
    
    def __init__(self, node_id: str, quorum_disk_path: str):
        self.node_id = node_id
        self.quorum_disk_path = Path(quorum_disk_path)
        self.lock_file = self.quorum_disk_path / f"quorum.lock"
        self.node_file = self.quorum_disk_path / f"node_{node_id}.heartbeat"
        
# Ensure quorum directory exists
        self.quorum_disk_path.mkdir(parents=True, exist_ok=True)
        
        self.is_active = False
        self.lock_fd = None
    
    def acquire_quorum_lock(self) -> bool:
        """Acquire exclusive lock on shared disk"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            
# Try to acquire exclusive lock (non-blocking)
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
# Write our node ID to lock file
            self.lock_fd.write(f"{self.node_id}:{time.time()}\\n")
            self.lock_fd.flush()
            
            self.is_active = True
            print(f"Node {self.node_id} acquired quorum lock")
            return True
            
        except (IOError, OSError) as e:
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            print(f"Node {self.node_id} failed to acquire quorum lock: {e}")
            return False
    
    def release_quorum_lock(self):
        """Release quorum lock"""
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
                self.is_active = False
                print(f"Node {self.node_id} released quorum lock")
            except Exception as e:
                print(f"Error releasing lock: {e}")
            finally:
                self.lock_fd = None
    
    def update_heartbeat(self):
        """Update node heartbeat file"""
        try:
            with open(self.node_file, 'w') as f:
                f.write(f"{time.time()}\\n")
        except Exception as e:
            print(f"Failed to update heartbeat: {e}")
    
    def check_other_nodes(self) -> List[str]:
        """Check which other nodes are active"""
        active_nodes = []
        current_time = time.time()
        
        for heartbeat_file in self.quorum_disk_path.glob("node_*.heartbeat"):
            if heartbeat_file.name == f"node_{self.node_id}.heartbeat":
                continue
                
            try:
                with open(heartbeat_file, 'r') as f:
                    timestamp = float(f.read().strip())
                    
# Consider node active if heartbeat is less than 30 seconds old
                if current_time - timestamp < 30:
                    node_id = heartbeat_file.stem.replace('node_', '')
                    active_nodes.append(node_id)
                    
            except (ValueError, FileNotFoundError):
                continue
        
        return active_nodes
    
    def fence_other_nodes(self):
        """Fence other nodes (in real implementation, would power them off)"""
        print(f"Node {self.node_id} would fence other nodes (STONITH)")
        
# In production, this would:
# 1. Send power-off commands to other nodes
# 2. Disable their network access
# 3. Force them to stop processing
        
# For simulation, just remove their heartbeat files
        for heartbeat_file in self.quorum_disk_path.glob("node_*.heartbeat"):
            if heartbeat_file.name != f"node_{self.node_id}.heartbeat":
                try:
                    heartbeat_file.unlink()
                    print(f"Fenced node: {heartbeat_file.stem}")
                except Exception as e:
                    print(f"Failed to fence {heartbeat_file.stem}: {e}")

class STONITHCluster:
    """Cluster with STONITH-based split-brain prevention"""
    
    def __init__(self, node_id: str, quorum_disk: str):
        self.node_id = node_id
        self.quorum = DiskBasedQuorum(node_id, quorum_disk)
        self.is_leader = False
        self.data = {}
        self._running = True
        
# Start monitoring thread
        threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def _monitor_loop(self):
        """Monitor cluster state and handle split-brain"""
        while self._running:
# Update our heartbeat
            self.quorum.update_heartbeat()
            
# Check if we have quorum lock
            if not self.quorum.is_active:
                if self.quorum.acquire_quorum_lock():
                    self._become_active()
                else:
                    self._become_standby()
            
# If we're active, check for split-brain
            if self.is_leader:
                other_nodes = self.quorum.check_other_nodes()
                if len(other_nodes) > 0:
                    print(f"Detected potential split-brain with nodes: {other_nodes}")
                    self.quorum.fence_other_nodes()
            
            time.sleep(5)
    
    def _become_active(self):
        """Become active node"""
        if not self.is_leader:
            print(f"Node {self.node_id} becoming active")
            self.is_leader = True
    
    def _become_standby(self):
        """Become standby node"""
        if self.is_leader:
            print(f"Node {self.node_id} becoming standby")
            self.is_leader = False
    
    def write_data(self, key: str, value: any) -> bool:
        """Write data only if we're the active node"""
        if not self.is_leader:
            return False
        
        self.data[key] = value
        print(f"Active node {self.node_id} wrote {key}={value}")
        return True

# Example usage with shared disk
# stonith_node_1 = STONITHCluster('node_1', '/shared/quorum')
# stonith_node_2 = STONITHCluster('node_2', '/shared/quorum')
```

### Application-Level Split-Brain Detection

```python
import hashlib
import json
from typing import Dict, List, Tuple

class StateHashMonitor:
    """Monitor system state to detect split-brain conditions"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state_history: List[Tuple[float, str]] = []
        self.peer_states: Dict[str, List[Tuple[float, str]]] = {}
    
    def record_state(self, state_data: dict):
        """Record current system state"""
        timestamp = time.time()
        state_hash = self._hash_state(state_data)
        
        self.state_history.append((timestamp, state_hash))
        
# Keep only recent history (last 100 entries)
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def receive_peer_state(self, peer_id: str, timestamp: float, state_hash: str):
        """Receive state information from peer"""
        if peer_id not in self.peer_states:
            self.peer_states[peer_id] = []
        
        self.peer_states[peer_id].append((timestamp, state_hash))
        
# Keep only recent peer history
        if len(self.peer_states[peer_id]) > 100:
            self.peer_states[peer_id] = self.peer_states[peer_id][-100:]
    
    def detect_split_brain(self, time_window: float = 300) -> Dict[str, List[str]]:
        """Detect split-brain by comparing state histories"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
# Get our recent states
        our_recent_states = [
            (ts, hash_val) for ts, hash_val in self.state_history
            if ts >= cutoff_time
        ]
        
        if not our_recent_states:
            return {}
        
# Compare with each peer
        conflicts = {}
        
        for peer_id, peer_history in self.peer_states.items():
            peer_recent_states = [
                (ts, hash_val) for ts, hash_val in peer_history
                if ts >= cutoff_time
            ]
            
            if not peer_recent_states:
                continue
            
# Find overlapping time periods
            conflicts[peer_id] = self._find_conflicts(
                our_recent_states,
                peer_recent_states
            )
        
        return {peer: conflict_list for peer, conflict_list in conflicts.items() if conflict_list}
    
    def _hash_state(self, state_data: dict) -> str:
        """Create hash of system state"""
# Sort keys for consistent hashing
        sorted_state = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(sorted_state.encode()).hexdigest()[:16]
    
    def _find_conflicts(self, our_states: List[Tuple[float, str]], 
                       peer_states: List[Tuple[float, str]]) -> List[str]:
        """Find conflicting states between nodes"""
        conflicts = []
        
# Create time-based windows for comparison
        for our_time, our_hash in our_states:
# Find peer states in similar time window (±10 seconds)
            matching_peer_states = [
                (peer_time, peer_hash) for peer_time, peer_hash in peer_states
                if abs(peer_time - our_time) <= 10
            ]
            
            for peer_time, peer_hash in matching_peer_states:
                if our_hash != peer_hash:
                    conflicts.append(f"Time {our_time}: our_state={our_hash}, peer_state={peer_hash}")
        
        return conflicts

class SplitBrainDetector:
    """Comprehensive split-brain detection system"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state_monitor = StateHashMonitor(node_id)
        self.cluster_view = {}
        self.split_brain_detected = False
        
    def update_system_state(self, data: dict, metadata: dict):
        """Update system state and check for split-brain"""
        
# Record our state
        full_state = {
            'data': data,
            'metadata': metadata,
            'timestamp': time.time(),
            'node_id': self.node_id
        }
        
        self.state_monitor.record_state(full_state)
        
# Check for split-brain
        conflicts = self.state_monitor.detect_split_brain()
        
        if conflicts:
            self._handle_split_brain_detection(conflicts)
    
    def _handle_split_brain_detection(self, conflicts: Dict[str, List[str]]):
        """Handle detected split-brain condition"""
        
        if not self.split_brain_detected:
            print(f"SPLIT-BRAIN DETECTED by node {self.node_id}!")
            print("Conflicts found:")
            
            for peer_id, conflict_list in conflicts.items():
                print(f"  With {peer_id}:")
                for conflict in conflict_list[:3]:  # Show first 3 conflicts
                    print(f"    {conflict}")
                if len(conflict_list) > 3:
                    print(f"    ... and {len(conflict_list) - 3} more")
            
            self.split_brain_detected = True
            
# Take corrective action
            self._initiate_split_brain_recovery()
    
    def _initiate_split_brain_recovery(self):
        """Initiate split-brain recovery process"""
        
        print(f"Node {self.node_id} initiating split-brain recovery...")
        
# Strategy 1: Stop processing new requests
        self._stop_new_requests()
        
# Strategy 2: Initiate cluster reconciliation
        self._request_cluster_reconciliation()
        
# Strategy 3: If configured, fence other nodes
# self._fence_conflicting_nodes()
    
    def _stop_new_requests(self):
        """Stop processing new requests until split-brain is resolved"""
        print(f"Node {self.node_id} stopping new request processing")
# Implementation would set a flag to reject new writes
    
    def _request_cluster_reconciliation(self):
        """Request cluster-wide reconciliation"""
        print(f"Node {self.node_id} requesting cluster reconciliation")
# Implementation would trigger consensus protocol restart

# Usage example
detector = SplitBrainDetector('node_1')

# Simulate normal operation
detector.update_system_state(
    {'key1': 'value1', 'key2': 'value2'},
    {'leader': 'node_1', 'term': 5}
)

# Simulate conflicting state from peer
detector.state_monitor.receive_peer_state(
    'node_2',
    time.time(),
    'different_hash_indicating_split_brain'
)
```

## Split-Brain Resolution Strategies

### Automatic Reconciliation

```python
class SplitBrainReconciler:
    """Automatically reconcile split-brain conditions"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.resolution_strategies = [
            self._resolve_by_timestamp,
            self._resolve_by_node_priority,
            self._resolve_by_data_completeness,
            self._resolve_by_manual_intervention
        ]
    
    def reconcile_split_brain(self, our_state: dict, peer_states: Dict[str, dict]) -> dict:
        """Reconcile conflicting states from split-brain"""
        
        print(f"Node {self.node_id} starting split-brain reconciliation")
        
        all_states = {'our_node': our_state}
        all_states.update(peer_states)
        
# Try each resolution strategy
        for strategy in self.resolution_strategies:
            try:
                resolved_state = strategy(all_states)
                if resolved_state:
                    print(f"Split-brain resolved using {strategy.__name__}")
                    return resolved_state
            except Exception as e:
                print(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        raise Exception("Unable to resolve split-brain automatically")
    
    def _resolve_by_timestamp(self, states: Dict[str, dict]) -> Optional[dict]:
        """Resolve by choosing state with latest timestamp"""
        
        latest_time = 0
        latest_state = None
        
        for node_id, state in states.items():
            timestamp = state.get('timestamp', 0)
            if timestamp > latest_time:
                latest_time = timestamp
                latest_state = state
        
        if latest_state:
            print(f"Resolved by timestamp: choosing state from {latest_time}")
            return latest_state
        
        return None
    
    def _resolve_by_node_priority(self, states: Dict[str, dict]) -> Optional[dict]:
        """Resolve by node priority (alphabetically first node wins)"""
        
# Sort nodes by priority (could be configured)
        sorted_nodes = sorted(states.keys())
        priority_node = sorted_nodes[0]
        
        print(f"Resolved by priority: choosing state from {priority_node}")
        return states[priority_node]
    
    def _resolve_by_data_completeness(self, states: Dict[str, dict]) -> Optional[dict]:
        """Resolve by choosing state with most complete data"""
        
        max_data_size = 0
        best_state = None
        
        for node_id, state in states.items():
            data_size = len(str(state.get('data', {})))
            if data_size > max_data_size:
                max_data_size = data_size
                best_state = state
        
        if best_state:
            print(f"Resolved by data completeness: {max_data_size} bytes")
            return best_state
        
        return None
    
    def _resolve_by_manual_intervention(self, states: Dict[str, dict]) -> Optional[dict]:
        """Require manual intervention for resolution"""
        
        print("Split-brain requires manual intervention!")
        print("Available states:")
        
        for node_id, state in states.items():
            print(f"  {node_id}: {json.dumps(state, indent=2)[:200]}...")
        
# In production, this would:
# 1. Send alerts to operators
# 2. Provide UI for manual resolution
# 3. Wait for admin decision
        
# For demo, just choose first state
        return list(states.values())[0]

# Integration with cluster
class ReconciliationEnabledCluster(QuorumBasedCluster):
    """Cluster with automatic split-brain reconciliation"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        super().__init__(node_id, cluster_nodes)
        self.reconciler = SplitBrainReconciler(node_id)
        self.split_brain_detected = False
    
    def detect_and_resolve_split_brain(self):
        """Detect and automatically resolve split-brain"""
        
# Gather states from all reachable nodes
        peer_states = {}
        
        for node in self.reachable_nodes:
            try:
                peer_state = self._get_peer_state(node)
                if peer_state:
                    peer_states[node] = peer_state
            except Exception as e:
                print(f"Failed to get state from {node}: {e}")
        
        if not peer_states:
            return  # No peers to compare with
        
# Check for conflicts
        our_state = {
            'data': self.data,
            'term': self.current_term,
            'timestamp': time.time(),
            'node_id': self.node_id
        }
        
# Simple conflict detection (in practice, would be more sophisticated)
        conflicts_detected = False
        for peer_id, peer_state in peer_states.items():
            if (peer_state.get('term') == our_state['term'] and
                peer_state.get('data') != our_state['data']):
                conflicts_detected = True
                break
        
        if conflicts_detected:
            print(f"Split-brain detected, starting reconciliation...")
            
            try:
                resolved_state = self.reconciler.reconcile_split_brain(
                    our_state, peer_states
                )
                
# Apply resolved state
                self.data = resolved_state.get('data', {})
                self.current_term = resolved_state.get('term', self.current_term)
                
                print("Split-brain reconciliation completed")
                
            except Exception as e:
                print(f"Split-brain reconciliation failed: {e}")
# Could trigger manual intervention or cluster restart
    
    def _get_peer_state(self, peer_id: str) -> Optional[dict]:
        """Get state from peer node"""
        try:
            response = self._simulate_network_call(peer_id, {
                'type': 'get_state'
            })
            return response.get('state')
        except Exception:
            return None
```

<div class="decision-box">
<strong>Prevention Strategy Selection</strong>:

- **High availability**: Quorum-based with witness nodes
- **Strong consistency**: Disk-based quorum (STONITH)
- **Cloud environments**: Application-level detection
- **Legacy systems**: Automatic reconciliation
- **Mission critical**: Manual intervention required
- **Geographically distributed**: Multiple quorum strategies
</div>

## Real-World Split-Brain Scenarios

### Database Split-Brain

```python
class DatabaseSplitBrainPrevention:
    """Prevent split-brain in database clusters"""
    
    def __init__(self, db_node_id: str, replica_nodes: List[str]):
        self.db_node_id = db_node_id
        self.replica_nodes = replica_nodes
        self.is_primary = False
        self.read_only_mode = False
        
# Track replica health
        self.healthy_replicas = set()
        self.min_replicas_for_writes = len(replica_nodes) // 2 + 1
    
    def check_replica_health(self):
        """Check health of replica nodes"""
        healthy_count = 0
        
        for replica in self.replica_nodes:
            if self._ping_replica(replica):
                self.healthy_replicas.add(replica)
                healthy_count += 1
            else:
                self.healthy_replicas.discard(replica)
        
# Enter read-only mode if we don't have enough replicas
        if healthy_count < self.min_replicas_for_writes:
            if not self.read_only_mode:
                print(f"DB {self.db_node_id} entering read-only mode")
                self.read_only_mode = True
        else:
            if self.read_only_mode:
                print(f"DB {self.db_node_id} resuming write operations")
                self.read_only_mode = False
    
    def execute_write(self, query: str) -> bool:
        """Execute write with split-brain protection"""
        
        if self.read_only_mode:
            raise Exception("Database in read-only mode due to insufficient replicas")
        
        if not self.is_primary:
            raise Exception("Only primary can execute writes")
        
# Ensure we can replicate to majority
        if len(self.healthy_replicas) < self.min_replicas_for_writes:
            raise Exception("Insufficient healthy replicas for safe write")
        
# Execute write on primary
        success_count = 1  # Count primary
        
# Replicate to replicas
        for replica in self.healthy_replicas:
            if self._replicate_to_replica(replica, query):
                success_count += 1
                
# Stop when we have majority
                if success_count >= self.min_replicas_for_writes:
                    break
        
        if success_count >= self.min_replicas_for_writes:
            print(f"Write replicated to {success_count} nodes")
            return True
        else:
            raise Exception("Failed to replicate to minimum number of replicas")
    
    def _ping_replica(self, replica_id: str) -> bool:
        """Check if replica is healthy"""
# Simulate health check
        return random.random() > 0.1  # 90% success rate
    
    def _replicate_to_replica(self, replica_id: str, query: str) -> bool:
        """Replicate write to specific replica"""
# Simulate replication
        return random.random() > 0.05  # 95% success rate

# Usage
db_primary = DatabaseSplitBrainPrevention('primary', ['replica1', 'replica2', 'replica3'])
db_primary.is_primary = True

try:
    db_primary.check_replica_health()
    db_primary.execute_write("INSERT INTO users VALUES (...)")
except Exception as e:
    print(f"Write failed: {e}")
```

## Monitoring and Alerting

```python
class SplitBrainMonitor:
    """Monitor cluster for split-brain conditions"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.metrics = {
            'split_brain_events': 0,
            'quorum_losses': 0,
            'reconciliation_attempts': 0,
            'manual_interventions': 0
        }
        self.alerts_sent = set()
    
    def record_split_brain_event(self, severity: str, details: dict):
        """Record split-brain event"""
        
        self.metrics['split_brain_events'] += 1
        
        event = {
            'timestamp': time.time(),
            'node_id': self.node_id,
            'severity': severity,
            'details': details
        }
        
# Send alert if not already sent
        alert_key = f"{severity}_{hash(str(details))}"
        if alert_key not in self.alerts_sent:
            self._send_alert(event)
            self.alerts_sent.add(alert_key)
        
# Log event
        print(f"SPLIT-BRAIN EVENT: {json.dumps(event, indent=2)}")
    
    def _send_alert(self, event: dict):
        """Send alert to monitoring system"""
        
# In production, would send to:
# - PagerDuty/OpsGenie
# - Slack/Teams
# - Email
# - Prometheus/Grafana
        
        print(f"ALERT: Split-brain detected on {event['node_id']}")
        print(f"Severity: {event['severity']}")
        print(f"Details: {event['details']}")
    
    def get_split_brain_metrics(self) -> dict:
        """Get split-brain related metrics"""
        return {
            **self.metrics,
            'node_id': self.node_id,
            'timestamp': time.time()
        }

# Integration example
monitor = SplitBrainMonitor('node_1')

# Record different types of events
monitor.record_split_brain_event('HIGH', {
    'type': 'data_divergence',
    'affected_keys': ['user_123', 'order_456'],
    'peer_nodes': ['node_2', 'node_3']
})

monitor.record_split_brain_event('CRITICAL', {
    'type': 'dual_leadership',
    'leaders': ['node_1', 'node_3'],
    'duration_seconds': 45
})
```

## Related Patterns
- [Consensus](consensus.md) - Distributed agreement protocols
- [Leader Election](leader-election.md) - Choosing single leader
- [Quorum](quorum.md) - Majority-based decisions
- [Circuit Breaker](circuit-breaker.md) - Failure detection
- [Health Check](health-check.md) - Node health monitoring

## References
- [Raft Consensus Algorithm](https://raft.github.io/)
- [STONITH Fencing](https://clusterlabs.org/pacemaker/doc/en-US/Pacemaker/2.0/html/Clusters_from_Scratch/ch05.html)
- [Split-Brain in Distributed Systems](https://en.wikipedia.org/wiki/Split-brain_(computing))
- [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)