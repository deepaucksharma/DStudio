#!/usr/bin/env python3
"""
Raft Consensus Algorithm - Log Replication Implementation
Real-world distributed database log replication like CockroachDB/TiDB

यह implementation Raft के log replication phase को show करती है
जैसे कि distributed databases में transactions को replicate करते हैं
"""

import json
import time
import threading
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    """Single log entry in Raft log"""
    term: int
    index: int
    command: Dict[str, Any]
    timestamp: float
    entry_id: str
    
    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = str(uuid.uuid4())[:8]

@dataclass
class AppendEntriesRequest:
    """Log replication request from leader"""
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int

@dataclass
class AppendEntriesResponse:
    """Response to append entries request"""
    term: int
    success: bool
    follower_id: str
    match_index: int
    conflict_index: Optional[int] = None

class RaftLogReplicator:
    """
    Raft node with log replication capability
    बिल्कुल वैसे ही जैसे Paytm के database cluster में transactions replicate होती हैं
    """
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.state = NodeState.FOLLOWER
        
        # Persistent state
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        
        # Volatile state
        self.commit_index = -1  # Index of last committed entry
        self.last_applied = -1  # Index of last applied entry
        
        # Leader state
        self.next_index: Dict[str, int] = {}    # Next entry to send to each follower
        self.match_index: Dict[str, int] = {}   # Highest entry replicated on each follower
        
        # Application state machine (यहाँ actual data store होता है)
        self.state_machine: Dict[str, Any] = {}
        
        # Network simulation
        self.network: Dict[str, 'RaftLogReplicator'] = {}
        self.is_running = True
        
        # Timers
        self.election_timer = None
        self.heartbeat_timer = None
        
        print(f"🚀 Raft node {self.node_id} initialized")
    
    def set_network(self, network: Dict[str, 'RaftLogReplicator']):
        """Set network reference"""
        self.network = network
    
    def become_leader(self):
        """Transition to leader and initialize leader state"""
        print(f"👑 Node {self.node_id}: Became leader for term {self.current_term}")
        self.state = NodeState.LEADER
        
        # Initialize next_index and match_index for all followers
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                self.next_index[node_id] = len(self.log)
                self.match_index[node_id] = -1
        
        # Start sending heartbeats
        self.start_heartbeat_timer()
        
        # Send initial heartbeat to establish leadership
        self.replicate_to_followers()
    
    def append_entry(self, command: Dict[str, Any]) -> bool:
        """
        Client request to append new entry (केवल leader पर)
        यह function तब call होता है जब client कोई operation करना चाहता है
        """
        if self.state != NodeState.LEADER:
            print(f"❌ Node {self.node_id}: Not leader, cannot accept writes")
            return False
        
        # Create new log entry
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log),
            command=command,
            timestamp=time.time(),
            entry_id=str(uuid.uuid4())[:8]
        )
        
        # Append to leader's log
        self.log.append(entry)
        
        print(f"📝 Leader {self.node_id}: Appended entry {entry.index}: {entry.command}")
        
        # Replicate to followers immediately
        self.replicate_to_followers()
        
        return True
    
    def replicate_to_followers(self):
        """Send append entries to all followers"""
        if self.state != NodeState.LEADER:
            return
        
        for node_id in self.cluster_nodes:
            if node_id != self.node_id and node_id in self.network:
                threading.Thread(
                    target=self.replicate_to_follower,
                    args=(node_id,)
                ).start()
    
    def replicate_to_follower(self, follower_id: str):
        """Send append entries to specific follower"""
        try:
            next_index = self.next_index[follower_id]
            
            # Determine entries to send
            entries_to_send = []
            if next_index < len(self.log):
                entries_to_send = self.log[next_index:]
            
            # Determine previous log entry
            prev_log_index = next_index - 1
            prev_log_term = 0
            if prev_log_index >= 0 and prev_log_index < len(self.log):
                prev_log_term = self.log[prev_log_index].term
            
            # Create append entries request
            request = AppendEntriesRequest(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=entries_to_send,
                leader_commit=self.commit_index
            )
            
            # Send request
            follower = self.network[follower_id]
            response = follower.handle_append_entries(request)
            self.handle_append_entries_response(follower_id, request, response)
            
        except Exception as e:
            print(f"❌ Leader {self.node_id}: Failed to replicate to {follower_id}: {e}")
    
    def handle_append_entries(self, request: AppendEntriesRequest) -> AppendEntriesResponse:
        """
        Handle append entries request from leader
        यह function followers पर execute होता है
        """
        # Reply false if term < currentTerm
        if request.term < self.current_term:
            return AppendEntriesResponse(
                term=self.current_term,
                success=False,
                follower_id=self.node_id,
                match_index=-1
            )
        
        # Update term and become follower if necessary
        if request.term > self.current_term:
            self.current_term = request.term
            self.voted_for = None
        
        self.state = NodeState.FOLLOWER
        self.reset_election_timer()
        
        # Check if log contains an entry at prevLogIndex with matching term
        if request.prev_log_index >= 0:
            if (request.prev_log_index >= len(self.log) or
                self.log[request.prev_log_index].term != request.prev_log_term):
                
                # Log inconsistency detected
                print(f"🔄 Follower {self.node_id}: Log inconsistency at index {request.prev_log_index}")
                
                # Find the first index of conflicting term
                conflict_index = min(len(self.log), request.prev_log_index)
                
                return AppendEntriesResponse(
                    term=self.current_term,
                    success=False,
                    follower_id=self.node_id,
                    match_index=-1,
                    conflict_index=conflict_index
                )
        
        # If an existing entry conflicts with a new one (same index but different terms),
        # delete the existing entry and all that follow it
        if request.entries:
            start_index = request.prev_log_index + 1
            
            for i, new_entry in enumerate(request.entries):
                entry_index = start_index + i
                
                # If log already has entry at this index, check for conflict
                if entry_index < len(self.log):
                    existing_entry = self.log[entry_index]
                    if existing_entry.term != new_entry.term:
                        # Conflict detected, delete this entry and all following
                        self.log = self.log[:entry_index]
                        print(f"🗑️ Follower {self.node_id}: Deleted conflicting entries from index {entry_index}")
                        break
                elif entry_index == len(self.log):
                    # Append new entry
                    break
            
            # Append new entries
            entries_to_append = request.entries[len(self.log) - start_index:]
            for entry in entries_to_append:
                self.log.append(entry)
                print(f"➕ Follower {self.node_id}: Appended entry {entry.index}: {entry.command}")
        
        # Update commit index
        if request.leader_commit > self.commit_index:
            old_commit = self.commit_index
            self.commit_index = min(request.leader_commit, len(self.log) - 1)
            
            # Apply newly committed entries
            self.apply_committed_entries()
            
            if self.commit_index > old_commit:
                print(f"✅ Follower {self.node_id}: Updated commit index to {self.commit_index}")
        
        match_index = len(self.log) - 1
        
        return AppendEntriesResponse(
            term=self.current_term,
            success=True,
            follower_id=self.node_id,
            match_index=match_index
        )
    
    def handle_append_entries_response(self, follower_id: str, 
                                     request: AppendEntriesRequest,
                                     response: AppendEntriesResponse):
        """Handle response from follower"""
        if self.state != NodeState.LEADER:
            return
        
        # If response term is higher, step down
        if response.term > self.current_term:
            self.current_term = response.term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            print(f"🔄 Leader {self.node_id}: Stepping down due to higher term")
            return
        
        if response.success:
            # Update next_index and match_index for follower
            self.next_index[follower_id] = response.match_index + 1
            self.match_index[follower_id] = response.match_index
            
            print(f"✅ Leader {self.node_id}: Successfully replicated to {follower_id} (match_index: {response.match_index})")
            
            # Try to update commit index
            self.update_commit_index()
            
        else:
            # Replication failed, decrement next_index and retry
            if response.conflict_index is not None:
                self.next_index[follower_id] = response.conflict_index
            else:
                self.next_index[follower_id] = max(0, self.next_index[follower_id] - 1)
            
            print(f"🔄 Leader {self.node_id}: Retrying replication to {follower_id} from index {self.next_index[follower_id]}")
            
            # Retry immediately
            threading.Thread(
                target=self.replicate_to_follower,
                args=(follower_id,)
            ).start()
    
    def update_commit_index(self):
        """Update commit index based on majority replication"""
        if self.state != NodeState.LEADER:
            return
        
        # Find the highest index replicated on majority of servers
        for index in range(len(self.log) - 1, self.commit_index, -1):
            if self.log[index].term != self.current_term:
                continue  # Only commit entries from current term
            
            # Count how many nodes have this entry
            replication_count = 1  # Leader has it
            for node_id in self.cluster_nodes:
                if node_id != self.node_id and node_id in self.match_index:
                    if self.match_index[node_id] >= index:
                        replication_count += 1
            
            # Check if we have majority
            majority = len(self.cluster_nodes) // 2 + 1
            if replication_count >= majority:
                old_commit = self.commit_index
                self.commit_index = index
                
                # Apply newly committed entries
                self.apply_committed_entries()
                
                print(f"🎯 Leader {self.node_id}: Committed entries up to index {self.commit_index} (replicated on {replication_count}/{len(self.cluster_nodes)} nodes)")
                break
    
    def apply_committed_entries(self):
        """Apply committed entries to state machine"""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            
            # Apply command to state machine
            self.apply_command(entry.command)
            
            print(f"🔧 Node {self.node_id}: Applied entry {self.last_applied}: {entry.command}")
    
    def apply_command(self, command: Dict[str, Any]):
        """
        Apply command to state machine
        यह function actual business logic execute करता है
        """
        cmd_type = command.get('type', '')
        
        if cmd_type == 'SET':
            # Set key-value pair (जैसे Redis में)
            key = command.get('key', '')
            value = command.get('value', '')
            self.state_machine[key] = value
            
        elif cmd_type == 'DELETE':
            # Delete key
            key = command.get('key', '')
            self.state_machine.pop(key, None)
            
        elif cmd_type == 'TRANSFER':
            # Money transfer (UPI style)
            from_account = command.get('from_account', '')
            to_account = command.get('to_account', '')
            amount = command.get('amount', 0)
            
            # Debit from source
            if from_account in self.state_machine:
                self.state_machine[from_account] = self.state_machine[from_account] - amount
            
            # Credit to destination
            if to_account not in self.state_machine:
                self.state_machine[to_account] = 0
            self.state_machine[to_account] = self.state_machine[to_account] + amount
    
    def reset_election_timer(self):
        """Reset election timeout"""
        if self.election_timer:
            self.election_timer.cancel()
        
        timeout = random.uniform(150, 300) / 1000.0  # 150-300ms
        self.election_timer = threading.Timer(timeout, self.start_election)
        self.election_timer.start()
    
    def start_election(self):
        """Start leader election"""
        # Simplified election logic (refer to 01_basic_raft_leader_election.py for full implementation)
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        
        # In a real implementation, we would send vote requests here
        # For this demo, we'll just assume this node becomes leader
        if random.random() > 0.5:  # 50% chance to become leader
            self.become_leader()
        else:
            self.reset_election_timer()
    
    def start_heartbeat_timer(self):
        """Start heartbeat timer for leader"""
        if self.state == NodeState.LEADER and self.is_running:
            self.heartbeat_timer = threading.Timer(0.05, self.heartbeat_routine)  # 50ms
            self.heartbeat_timer.start()
    
    def heartbeat_routine(self):
        """Send heartbeats regularly"""
        if self.state == NodeState.LEADER:
            self.replicate_to_followers()  # Heartbeat is just empty append entries
            self.start_heartbeat_timer()
    
    def get_status(self) -> Dict:
        """Get node status"""
        return {
            'node_id': self.node_id,
            'state': self.state.value,
            'term': self.current_term,
            'log_length': len(self.log),
            'commit_index': self.commit_index,
            'last_applied': self.last_applied,
            'state_machine_size': len(self.state_machine)
        }
    
    def stop(self):
        """Stop node"""
        self.is_running = False
        if self.election_timer:
            self.election_timer.cancel()
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

def simulate_paytm_transactions():
    """
    Simulate Paytm-style distributed transaction processing
    इस simulation में हम UPI payments का consistent replication देखेंगे
    """
    print("🇮🇳 Raft Log Replication - Paytm Distributed Payments")
    print("=" * 60)
    
    # Create cluster (Paytm के data centers)
    nodes = ['mumbai-dc', 'delhi-dc', 'bangalore-dc']
    
    # Initialize Raft cluster
    cluster = {}
    for node_id in nodes:
        cluster[node_id] = RaftLogReplicator(node_id, nodes)
    
    # Set network
    for node in cluster.values():
        node.set_network(cluster)
    
    # Make mumbai-dc the leader
    leader = cluster['mumbai-dc']
    leader.become_leader()
    
    print(f"\n👑 Leader: {leader.node_id}")
    
    # Simulate UPI transactions
    print("\n💳 Processing UPI Transactions...")
    
    transactions = [
        {'type': 'SET', 'key': 'user:rahul:balance', 'value': 10000, 'description': 'Initial balance - Rahul'},
        {'type': 'SET', 'key': 'user:priya:balance', 'value': 5000, 'description': 'Initial balance - Priya'},
        {'type': 'TRANSFER', 'from_account': 'user:rahul:balance', 'to_account': 'user:priya:balance', 'amount': 500, 'description': 'Rahul -> Priya: ₹500'},
        {'type': 'SET', 'key': 'merchant:zomato:balance', 'value': 0, 'description': 'Zomato merchant account'},
        {'type': 'TRANSFER', 'from_account': 'user:priya:balance', 'to_account': 'merchant:zomato:balance', 'amount': 250, 'description': 'Priya -> Zomato: ₹250'},
    ]
    
    # Process transactions
    for i, tx in enumerate(transactions):
        print(f"\n📱 Transaction {i+1}: {tx['description']}")
        success = leader.append_entry(tx)
        
        if success:
            # Wait for replication
            time.sleep(0.2)
            
            # Show cluster state
            print("   📊 Cluster Status:")
            for node_id, node in cluster.items():
                status = node.get_status()
                committed = len([e for e in node.log[:node.commit_index+1]])
                print(f"     {node_id}: {status['log_length']} entries, {committed} committed")
        
        time.sleep(0.5)
    
    # Wait for all transactions to commit
    print("\n⏳ Waiting for final commits...")
    time.sleep(2)
    
    # Show final state
    print("\n💰 Final Account Balances:")
    for node_id, node in cluster.items():
        print(f"\n   Node: {node_id}")
        for key, value in node.state_machine.items():
            print(f"     {key}: ₹{value}")
    
    # Verify consistency
    print("\n🔍 Consistency Check:")
    reference_state = list(cluster.values())[0].state_machine
    consistent = True
    
    for node_id, node in cluster.items():
        if node.state_machine != reference_state:
            print(f"   ❌ {node_id}: INCONSISTENT")
            consistent = False
        else:
            print(f"   ✅ {node_id}: CONSISTENT")
    
    if consistent:
        print("\n🎉 All nodes have consistent state!")
    
    # Cleanup
    for node in cluster.values():
        node.stop()

if __name__ == "__main__":
    simulate_paytm_transactions()
    
    print("\n" + "="*60)
    print("Key Learnings:")
    print("1. Leader replicates log entries to all followers")
    print("2. Entry is committed only when majority has replicated it")
    print("3. Followers apply committed entries to state machine")
    print("4. Log consistency is maintained through term numbers")
    print("5. Failed replications are automatically retried")