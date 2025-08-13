#!/usr/bin/env python3
"""
Raft Consensus Algorithm - Leader Election Implementation
Inspired by MongoDB replica sets and Elasticsearch cluster management

यह implementation Raft algorithm के leader election phase को demonstrate करती है
जैसे कि MongoDB में replica set के master election में होता है
"""

import random
import time
import threading
import json
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"

@dataclass
class VoteRequest:
    """Vote request message for leader election"""
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

@dataclass
class VoteResponse:
    """Vote response message"""
    term: int
    vote_granted: bool
    voter_id: str

@dataclass
class AppendEntriesRequest:
    """Heartbeat/log append request"""
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[Dict]
    leader_commit: int

class RaftNode:
    """
    Raft consensus node implementation
    हर node MongoDB की तरह three states में रह सकता है: follower, candidate, leader
    """
    
    def __init__(self, node_id: str, cluster_nodes: List[str], election_timeout_range=(150, 300)):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.state = NodeState.FOLLOWER
        
        # Persistent state (यह data disk पर store होता है)
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict] = []
        
        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state (केवल leader के पास valid होता है)
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Election और heartbeat timers
        self.election_timeout_range = election_timeout_range
        self.election_timer = None
        self.heartbeat_timer = None
        
        # Vote tracking
        self.votes_received = set()
        
        # Simulated network (production में यह actual HTTP/gRPC calls होंगे)
        self.network = {}
        self.is_running = True
        
        print(f"🚀 Node {self.node_id} initialized in cluster {cluster_nodes}")
    
    def set_network(self, network: Dict[str, 'RaftNode']):
        """Set network reference for communication"""
        self.network = network
    
    def reset_election_timer(self):
        """Reset election timer with random timeout"""
        if self.election_timer:
            self.election_timer.cancel()
        
        # Random timeout to prevent split votes (Raft का key feature)
        timeout = random.uniform(*self.election_timeout_range) / 1000.0
        self.election_timer = threading.Timer(timeout, self.start_election)
        self.election_timer.start()
        
        print(f"📅 Node {self.node_id}: Election timer reset to {timeout:.2f}s")
    
    def start_election(self):
        """
        Start leader election process
        यह function तब call होता है जब election timeout expire हो जाता है
        """
        if not self.is_running:
            return
            
        print(f"🗳️ Node {self.node_id}: Starting election for term {self.current_term + 1}")
        
        # Candidate state में transition
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}  # Vote for self
        
        # Reset election timer
        self.reset_election_timer()
        
        # Send vote requests to all other nodes
        self.send_vote_requests()
    
    def send_vote_requests(self):
        """Send RequestVote RPCs to all other nodes"""
        last_log_index = len(self.log) - 1
        last_log_term = self.log[-1]['term'] if self.log else 0
        
        vote_request = VoteRequest(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=last_log_index,
            last_log_term=last_log_term
        )
        
        for node_id in self.cluster_nodes:
            if node_id != self.node_id and node_id in self.network:
                # Async vote request (production में यह network call होगी)
                threading.Thread(
                    target=self.request_vote_from_node,
                    args=(node_id, vote_request)
                ).start()
    
    def request_vote_from_node(self, node_id: str, vote_request: VoteRequest):
        """Request vote from a specific node"""
        try:
            # Simulate network delay
            time.sleep(random.uniform(0.01, 0.05))
            
            node = self.network[node_id]
            response = node.handle_vote_request(vote_request)
            self.handle_vote_response(response)
            
        except Exception as e:
            print(f"❌ Node {self.node_id}: Failed to get vote from {node_id}: {e}")
    
    def handle_vote_request(self, request: VoteRequest) -> VoteResponse:
        """
        Handle incoming vote request
        MongoDB replica set election में similar logic होती है
        """
        print(f"📬 Node {self.node_id}: Received vote request from {request.candidate_id} for term {request.term}")
        
        # If candidate's term is older, reject
        if request.term < self.current_term:
            return VoteResponse(
                term=self.current_term,
                vote_granted=False,
                voter_id=self.node_id
            )
        
        # If candidate's term is newer, update our term and become follower
        if request.term > self.current_term:
            self.current_term = request.term
            self.voted_for = None
            self.state = NodeState.FOLLOWER
            print(f"🔄 Node {self.node_id}: Updated to term {self.current_term}, becoming follower")
        
        # Check if we can grant vote
        vote_granted = False
        
        # Grant vote if we haven't voted or voted for same candidate
        if (self.voted_for is None or self.voted_for == request.candidate_id):
            # Check if candidate's log is at least as up-to-date as ours
            our_last_log_term = self.log[-1]['term'] if self.log else 0
            our_last_log_index = len(self.log) - 1
            
            candidate_log_ok = (
                request.last_log_term > our_last_log_term or
                (request.last_log_term == our_last_log_term and 
                 request.last_log_index >= our_last_log_index)
            )
            
            if candidate_log_ok:
                vote_granted = True
                self.voted_for = request.candidate_id
                self.reset_election_timer()  # Reset timer after granting vote
                print(f"✅ Node {self.node_id}: Granted vote to {request.candidate_id}")
        
        return VoteResponse(
            term=self.current_term,
            vote_granted=vote_granted,
            voter_id=self.node_id
        )
    
    def handle_vote_response(self, response: VoteResponse):
        """Handle vote response from other nodes"""
        if self.state != NodeState.CANDIDATE:
            return
        
        # If responder has higher term, become follower
        if response.term > self.current_term:
            self.current_term = response.term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.reset_election_timer()
            print(f"🔄 Node {self.node_id}: Stepping down due to higher term {response.term}")
            return
        
        # Count the vote
        if response.vote_granted and response.term == self.current_term:
            self.votes_received.add(response.voter_id)
            print(f"📊 Node {self.node_id}: Received vote from {response.voter_id} ({len(self.votes_received)}/{len(self.cluster_nodes)})")
            
            # Check if we have majority
            majority = len(self.cluster_nodes) // 2 + 1
            if len(self.votes_received) >= majority:
                self.become_leader()
    
    def become_leader(self):
        """Transition to leader state"""
        if self.state != NodeState.CANDIDATE:
            return
            
        print(f"👑 Node {self.node_id}: Became LEADER for term {self.current_term}")
        self.state = NodeState.LEADER
        
        # Cancel election timer
        if self.election_timer:
            self.election_timer.cancel()
        
        # Initialize leader state
        next_index = len(self.log)
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                self.next_index[node_id] = next_index
                self.match_index[node_id] = 0
        
        # Start sending heartbeats
        self.send_heartbeats()
        self.schedule_heartbeats()
    
    def send_heartbeats(self):
        """Send heartbeat (empty AppendEntries) to all followers"""
        if self.state != NodeState.LEADER or not self.is_running:
            return
            
        heartbeat = AppendEntriesRequest(
            term=self.current_term,
            leader_id=self.node_id,
            prev_log_index=len(self.log) - 1,
            prev_log_term=self.log[-1]['term'] if self.log else 0,
            entries=[],
            leader_commit=self.commit_index
        )
        
        for node_id in self.cluster_nodes:
            if node_id != self.node_id and node_id in self.network:
                threading.Thread(
                    target=self.send_heartbeat_to_node,
                    args=(node_id, heartbeat)
                ).start()
    
    def send_heartbeat_to_node(self, node_id: str, heartbeat: AppendEntriesRequest):
        """Send heartbeat to specific node"""
        try:
            node = self.network[node_id]
            response = node.handle_append_entries(heartbeat)
            # Handle heartbeat response if needed
            
        except Exception as e:
            print(f"💔 Node {self.node_id}: Heartbeat to {node_id} failed: {e}")
    
    def handle_append_entries(self, request: AppendEntriesRequest) -> Dict:
        """Handle heartbeat/append entries from leader"""
        # If request term is older, reject
        if request.term < self.current_term:
            return {
                'term': self.current_term,
                'success': False
            }
        
        # If request term is newer or equal, accept leader
        if request.term >= self.current_term:
            self.current_term = request.term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.reset_election_timer()
            
            # यह heartbeat है, so we know leader is alive
            if not request.entries:  # Empty entries = heartbeat
                print(f"💓 Node {self.node_id}: Heartbeat from leader {request.leader_id}")
        
        return {
            'term': self.current_term,
            'success': True
        }
    
    def schedule_heartbeats(self):
        """Schedule regular heartbeat sending"""
        if self.state == NodeState.LEADER and self.is_running:
            self.heartbeat_timer = threading.Timer(0.05, self.heartbeat_routine)  # 50ms heartbeat
            self.heartbeat_timer.start()
    
    def heartbeat_routine(self):
        """Regular heartbeat routine"""
        if self.state == NodeState.LEADER:
            self.send_heartbeats()
            self.schedule_heartbeats()
    
    def get_status(self) -> Dict:
        """Get current node status"""
        return {
            'node_id': self.node_id,
            'state': self.state.value,
            'term': self.current_term,
            'voted_for': self.voted_for,
            'log_length': len(self.log),
            'votes_received': len(self.votes_received) if self.state == NodeState.CANDIDATE else 0
        }
    
    def stop(self):
        """Stop the node"""
        self.is_running = False
        if self.election_timer:
            self.election_timer.cancel()
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

def simulate_raft_election():
    """
    Simulate Raft leader election
    यह simulation MongoDB replica set election की तरह काम करती है
    """
    print("🇮🇳 Raft Election Simulation - Indian Banking Cluster")
    print("=" * 50)
    
    # Create cluster nodes (Indian bank branches की तरह)
    nodes = ['mumbai-branch', 'delhi-branch', 'bangalore-branch', 'chennai-branch', 'kolkata-branch']
    
    # Initialize Raft nodes
    raft_cluster = {}
    for node_id in nodes:
        raft_cluster[node_id] = RaftNode(node_id, nodes)
    
    # Set network connections
    for node in raft_cluster.values():
        node.set_network(raft_cluster)
    
    # Start election timers
    print("\n🚀 Starting Raft cluster...")
    for node in raft_cluster.values():
        node.reset_election_timer()
    
    # Monitor election process
    print("\n📊 Monitoring election process...")
    start_time = time.time()
    
    while time.time() - start_time < 10:  # Monitor for 10 seconds
        # Print cluster status
        leaders = [node for node in raft_cluster.values() if node.state == NodeState.LEADER]
        candidates = [node for node in raft_cluster.values() if node.state == NodeState.CANDIDATE]
        followers = [node for node in raft_cluster.values() if node.state == NodeState.FOLLOWER]
        
        print(f"\n📈 Cluster Status (t={time.time() - start_time:.1f}s):")
        print(f"   Leaders: {[n.node_id for n in leaders]}")
        print(f"   Candidates: {[n.node_id for n in candidates]}")
        print(f"   Followers: {[n.node_id for n in followers]}")
        
        if leaders:
            leader = leaders[0]
            print(f"   👑 Current Leader: {leader.node_id} (Term: {leader.current_term})")
            
            if len(leaders) == 1:
                print("   ✅ Stable leadership achieved!")
                break
        
        time.sleep(1)
    
    # Simulate leader failure
    if leaders:
        print(f"\n💥 Simulating leader failure: {leaders[0].node_id} going down...")
        leaders[0].stop()
        
        # Monitor re-election
        print("📊 Monitoring re-election...")
        start_reelection = time.time()
        
        while time.time() - start_reelection < 5:
            active_leaders = [n for n in raft_cluster.values() 
                            if n.is_running and n.state == NodeState.LEADER]
            
            if active_leaders:
                print(f"   👑 New Leader elected: {active_leaders[0].node_id} (Term: {active_leaders[0].current_term})")
                break
            
            time.sleep(0.5)
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    for node in raft_cluster.values():
        node.stop()
    
    print("✅ Raft election simulation completed!")

if __name__ == "__main__":
    # Run the simulation
    simulate_raft_election()
    
    print("\n" + "="*50)
    print("Key Learnings:")
    print("1. Raft ensures only one leader per term")
    print("2. Random election timeouts prevent split votes")
    print("3. Leader sends regular heartbeats to maintain authority")
    print("4. Failed leader triggers new election automatically")
    print("5. Majority vote required for leadership")