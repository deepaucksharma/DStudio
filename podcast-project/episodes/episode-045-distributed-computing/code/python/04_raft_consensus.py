#!/usr/bin/env python3
"""
Raft Consensus Algorithm Implementation
Raft consensus - distributed systems में leader election और log replication

यह example दिखाता है कि कैसे multiple servers के बीच consensus बनाते हैं
Raft algorithm use करके। Indian companies जैसे PhonePe, GPay इसे use करती हैं
payment processing में consistency ensure करने के लिए।

Production context: PhonePe processes 8+ billion transactions using consensus protocols
Scale: Handles partition tolerance while maintaining strong consistency
Cost benefit: Prevents double spending and ensures transaction integrity
"""

import random
import time
import threading
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeState(Enum):
    """Raft node states"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    """
    Raft log entry
    """
    term: int
    index: int
    command: str
    data: Any
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "index": self.index,
            "command": self.command,
            "data": self.data,
            "timestamp": self.timestamp
        }

@dataclass
class VoteRequest:
    """
    Raft vote request message
    """
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

@dataclass
class VoteResponse:
    """
    Raft vote response message
    """
    term: int
    vote_granted: bool
    voter_id: str

@dataclass
class AppendEntriesRequest:
    """
    Raft append entries request (heartbeat + log replication)
    """
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int

@dataclass
class AppendEntriesResponse:
    """
    Raft append entries response
    """
    term: int
    success: bool
    follower_id: str
    match_index: int = 0

class PhonePeTransactionNode:
    """
    PhonePe-style transaction processing node using Raft consensus
    हर node एक payment processor है जो transactions को consistently process करता है
    """
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        """
        Initialize a Raft node for transaction processing
        
        Args:
            node_id: Unique identifier for this node
            cluster_nodes: List of all node IDs in the cluster
        """
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.other_nodes = [n for n in cluster_nodes if n != node_id]
        
        # Raft state
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Timing
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(5.0, 10.0)  # 5-10 seconds
        self.heartbeat_interval = 2.0  # 2 seconds
        
        # Transaction state machine
        self.wallet_balances: Dict[str, float] = defaultdict(float)
        self.processed_transactions: List[Dict[str, Any]] = []
        
        # Threading
        self.running = False
        self.lock = threading.RLock()
        self.election_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # Network simulation
        self.network_partition = False
        self.message_delay = 0.1  # 100ms network delay
        
        logger.info(f"PhonePe transaction node {node_id} initialized")
    
    def start(self) -> None:
        """
        Start the Raft node
        """
        with self.lock:
            if self.running:
                return
            
            self.running = True
            self.last_heartbeat = time.time()
            
            # Start election timeout thread
            self.election_thread = threading.Thread(target=self._election_timeout_loop, daemon=True)
            self.election_thread.start()
            
            logger.info(f"Node {self.node_id} started as {self.state.value}")
    
    def stop(self) -> None:
        """
        Stop the Raft node
        """
        with self.lock:
            self.running = False
            if self.heartbeat_thread:
                self.heartbeat_thread.join(timeout=1)
            if self.election_thread:
                self.election_thread.join(timeout=1)
            
            logger.info(f"Node {self.node_id} stopped")
    
    def process_payment(self, from_wallet: str, to_wallet: str, amount: float) -> bool:
        """
        Process a payment transaction through Raft consensus
        
        Args:
            from_wallet: Source wallet ID
            to_wallet: Destination wallet ID
            amount: Transfer amount
            
        Returns:
            True if transaction was committed successfully
        """
        if self.state != NodeState.LEADER:
            logger.warning(f"Node {self.node_id} is not leader, cannot process payment")
            return False
        
        # Create transaction command
        transaction_id = str(uuid.uuid4())
        command_data = {
            "type": "payment",
            "transaction_id": transaction_id,
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "timestamp": time.time()
        }
        
        # Create log entry
        log_entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command="process_payment",
            data=command_data
        )
        
        return self._append_and_commit_entry(log_entry)
    
    def add_wallet_balance(self, wallet_id: str, amount: float) -> bool:
        """
        Add balance to a wallet (like money loading)
        """
        if self.state != NodeState.LEADER:
            logger.warning(f"Node {self.node_id} is not leader, cannot add balance")
            return False
        
        command_data = {
            "type": "add_balance",
            "wallet_id": wallet_id,
            "amount": amount,
            "timestamp": time.time()
        }
        
        log_entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            command="add_balance",
            data=command_data
        )
        
        return self._append_and_commit_entry(log_entry)
    
    def get_wallet_balance(self, wallet_id: str) -> float:
        """
        Get current wallet balance
        """
        with self.lock:
            return self.wallet_balances.get(wallet_id, 0.0)
    
    def request_vote(self, vote_request: VoteRequest) -> VoteResponse:
        """
        Handle vote request from candidate
        """
        with self.lock:
            vote_granted = False
            
            # If term is outdated, reject
            if vote_request.term < self.current_term:
                return VoteResponse(self.current_term, False, self.node_id)
            
            # If term is newer, become follower
            if vote_request.term > self.current_term:
                self.current_term = vote_request.term
                self.voted_for = None
                self.state = NodeState.FOLLOWER
            
            # Check if we can vote for this candidate
            if (self.voted_for is None or self.voted_for == vote_request.candidate_id):
                # Check if candidate's log is at least as up-to-date as ours
                last_log_term = self.log[-1].term if self.log else 0
                last_log_index = len(self.log)
                
                if (vote_request.last_log_term > last_log_term or 
                    (vote_request.last_log_term == last_log_term and 
                     vote_request.last_log_index >= last_log_index)):
                    
                    vote_granted = True
                    self.voted_for = vote_request.candidate_id
                    self.last_heartbeat = time.time()  # Reset election timeout
            
            logger.info(f"Node {self.node_id} voted {'for' if vote_granted else 'against'} {vote_request.candidate_id} in term {vote_request.term}")
            return VoteResponse(self.current_term, vote_granted, self.node_id)
    
    def append_entries(self, request: AppendEntriesRequest) -> AppendEntriesResponse:
        """
        Handle append entries request from leader (heartbeat + log replication)
        """
        with self.lock:
            success = False
            
            # If term is outdated, reject
            if request.term < self.current_term:
                return AppendEntriesResponse(self.current_term, False, self.node_id)
            
            # Valid leader contact, reset election timeout
            self.last_heartbeat = time.time()
            
            # If term is newer, become follower
            if request.term > self.current_term:
                self.current_term = request.term
                self.voted_for = None
                
            self.state = NodeState.FOLLOWER
            
            # Check log consistency
            if request.prev_log_index == 0:
                # This is the first entry or heartbeat
                success = True
            elif request.prev_log_index <= len(self.log):
                # Check if previous log entry matches
                prev_entry = self.log[request.prev_log_index - 1]
                if prev_entry.term == request.prev_log_term:
                    success = True
                    
                    # Remove conflicting entries
                    self.log = self.log[:request.prev_log_index]
            
            if success and request.entries:
                # Append new entries
                self.log.extend(request.entries)
                
                # Update commit index
                if request.leader_commit > self.commit_index:
                    self.commit_index = min(request.leader_commit, len(self.log))
                    self._apply_committed_entries()
            
            match_index = len(self.log) if success else 0
            
            logger.debug(f"Node {self.node_id} append_entries from {request.leader_id}: success={success}, match_index={match_index}")
            return AppendEntriesResponse(self.current_term, success, self.node_id, match_index)
    
    def _append_and_commit_entry(self, entry: LogEntry) -> bool:
        """
        Append entry to log and try to commit it
        """
        with self.lock:
            if self.state != NodeState.LEADER:
                return False
            
            # Add to our log
            self.log.append(entry)
            self.match_index[self.node_id] = len(self.log)
            
            logger.info(f"Leader {self.node_id} appended entry: {entry.command}")
            
            # Try to replicate to majority
            return self._replicate_to_followers()
    
    def _replicate_to_followers(self) -> bool:
        """
        Replicate log entries to followers
        """
        if self.state != NodeState.LEADER:
            return False
        
        # Simulate sending to followers
        successful_replications = 1  # Include self
        
        for follower_id in self.other_nodes:
            if self._send_append_entries_to_follower(follower_id):
                successful_replications += 1
        
        # Check if we have majority
        majority = (len(self.cluster_nodes) // 2) + 1
        if successful_replications >= majority:
            # Update commit index
            new_commit_index = len(self.log)
            if new_commit_index > self.commit_index:
                self.commit_index = new_commit_index
                self._apply_committed_entries()
                logger.info(f"Leader {self.node_id} committed entry at index {new_commit_index}")
                return True
        
        return False
    
    def _send_append_entries_to_follower(self, follower_id: str) -> bool:
        """
        Send append entries to a specific follower
        """
        # Simulate network delay and potential failures
        if self.network_partition or random.random() < 0.1:  # 10% failure rate
            return False
        
        time.sleep(self.message_delay)
        
        # In a real implementation, this would be an actual network call
        # For simulation, we assume success based on follower state
        return random.random() > 0.2  # 80% success rate
    
    def _apply_committed_entries(self) -> None:
        """
        Apply committed log entries to the state machine
        """
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            
            # Apply the command to state machine
            if entry.command == "process_payment":
                self._apply_payment(entry.data)
            elif entry.command == "add_balance":
                self._apply_balance_addition(entry.data)
            
            logger.info(f"Node {self.node_id} applied entry {self.last_applied}: {entry.command}")
    
    def _apply_payment(self, data: Dict[str, Any]) -> None:
        """
        Apply payment transaction to wallet balances
        """
        from_wallet = data["from_wallet"]
        to_wallet = data["to_wallet"]
        amount = data["amount"]
        
        # Check if sender has sufficient balance
        if self.wallet_balances[from_wallet] >= amount:
            self.wallet_balances[from_wallet] -= amount
            self.wallet_balances[to_wallet] += amount
            
            self.processed_transactions.append({
                "transaction_id": data["transaction_id"],
                "from_wallet": from_wallet,
                "to_wallet": to_wallet,
                "amount": amount,
                "timestamp": data["timestamp"],
                "status": "completed"
            })
            
            logger.info(f"Payment processed: ₹{amount} from {from_wallet} to {to_wallet}")
        else:
            logger.warning(f"Payment failed: insufficient balance in {from_wallet}")
    
    def _apply_balance_addition(self, data: Dict[str, Any]) -> None:
        """
        Apply balance addition to wallet
        """
        wallet_id = data["wallet_id"]
        amount = data["amount"]
        
        self.wallet_balances[wallet_id] += amount
        logger.info(f"Added ₹{amount} to wallet {wallet_id}")
    
    def _election_timeout_loop(self) -> None:
        """
        Main election timeout loop
        """
        while self.running:
            try:
                time.sleep(1.0)  # Check every second
                
                with self.lock:
                    if self.state == NodeState.LEADER:
                        self._send_heartbeats()
                    elif time.time() - self.last_heartbeat > self.election_timeout:
                        self._start_election()
                        
            except Exception as e:
                logger.error(f"Error in election timeout loop: {e}")
    
    def _start_election(self) -> None:
        """
        Start leader election
        """
        if not self.running:
            return
        
        self.current_term += 1
        self.state = NodeState.CANDIDATE
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(5.0, 10.0)
        
        logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
        
        # Vote for self
        votes_received = 1
        
        # Request votes from other nodes
        last_log_term = self.log[-1].term if self.log else 0
        last_log_index = len(self.log)
        
        vote_request = VoteRequest(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=last_log_index,
            last_log_term=last_log_term
        )
        
        # Simulate vote collection
        for node_id in self.other_nodes:
            if self._request_vote_from_node(node_id, vote_request):
                votes_received += 1
        
        # Check if won election
        majority = (len(self.cluster_nodes) // 2) + 1
        if votes_received >= majority:
            self._become_leader()
        else:
            self.state = NodeState.FOLLOWER
            logger.info(f"Node {self.node_id} lost election with {votes_received} votes")
    
    def _request_vote_from_node(self, node_id: str, vote_request: VoteRequest) -> bool:
        """
        Request vote from a specific node
        """
        # Simulate network delay and potential failures
        if self.network_partition or random.random() < 0.1:
            return False
        
        time.sleep(self.message_delay)
        
        # Simulate vote response (in real implementation, this would be network call)
        return random.random() > 0.3  # 70% chance of positive vote
    
    def _become_leader(self) -> None:
        """
        Become the leader
        """
        self.state = NodeState.LEADER
        
        # Initialize leader state
        for node_id in self.other_nodes:
            self.next_index[node_id] = len(self.log) + 1
            self.match_index[node_id] = 0
        
        logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
        
        # Start sending heartbeats
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def _send_heartbeats(self) -> None:
        """
        Send heartbeats to all followers
        """
        if self.state != NodeState.LEADER:
            return
        
        for follower_id in self.other_nodes:
            # Send empty append entries as heartbeat
            prev_log_index = len(self.log)
            prev_log_term = self.log[-1].term if self.log else 0
            
            request = AppendEntriesRequest(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=[],
                leader_commit=self.commit_index
            )
            
            self._send_append_entries_to_follower(follower_id)
    
    def _heartbeat_loop(self) -> None:
        """
        Heartbeat sending loop for leader
        """
        while self.running and self.state == NodeState.LEADER:
            try:
                self._send_heartbeats()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    def get_node_status(self) -> Dict[str, Any]:
        """
        Get current node status
        """
        with self.lock:
            return {
                "node_id": self.node_id,
                "state": self.state.value,
                "current_term": self.current_term,
                "voted_for": self.voted_for,
                "log_length": len(self.log),
                "commit_index": self.commit_index,
                "last_applied": self.last_applied,
                "wallet_count": len(self.wallet_balances),
                "total_balance": sum(self.wallet_balances.values()),
                "processed_transactions": len(self.processed_transactions)
            }

def demonstrate_phonePe_raft_consensus():
    """
    Demonstrate Raft consensus with PhonePe-style payment processing
    """
    print("\n💳 PhonePe Payment Processing with Raft Consensus")
    print("=" * 60)
    
    # Create cluster of payment processing nodes
    cluster_nodes = ["mumbai-pay-01", "delhi-pay-01", "bangalore-pay-01"]
    nodes = {}
    
    print(f"\n🏢 Setting up PhonePe payment cluster...")
    for node_id in cluster_nodes:
        node = PhonePeTransactionNode(node_id, cluster_nodes)
        nodes[node_id] = node
        node.start()
        print(f"✅ Started payment node: {node_id}")
    
    try:
        # Wait for leader election
        print(f"\n🗳️  Waiting for leader election...")
        time.sleep(8)
        
        # Find the leader
        leader_node = None
        for node in nodes.values():
            status = node.get_node_status()
            print(f"Node {status['node_id']}: {status['state']} (term {status['current_term']})")
            if status['state'] == 'leader':
                leader_node = node
        
        if not leader_node:
            # Force one to become leader for demo
            leader_node = list(nodes.values())[0]
            leader_node._become_leader()
            print(f"Manually promoted {leader_node.node_id} to leader for demo")
        
        # Add initial wallet balances
        print(f"\n💰 Adding initial wallet balances...")
        wallets = [
            ("rahul_mumbai", 10000.0),
            ("priya_delhi", 8000.0),
            ("arjun_bangalore", 12000.0),
            ("sneha_chennai", 6000.0)
        ]
        
        for wallet_id, amount in wallets:
            success = leader_node.add_wallet_balance(wallet_id, amount)
            if success:
                print(f"✅ Added ₹{amount} to {wallet_id}")
            else:
                print(f"❌ Failed to add balance to {wallet_id}")
            time.sleep(0.5)  # Small delay for consensus
        
        # Wait for consensus
        time.sleep(2)
        
        # Show balances across all nodes
        print(f"\n💳 Wallet balances across all nodes:")
        for node_id, node in nodes.items():
            print(f"\nNode {node_id}:")
            for wallet_id, _ in wallets:
                balance = node.get_wallet_balance(wallet_id)
                print(f"  {wallet_id}: ₹{balance}")
        
        # Process payments through consensus
        print(f"\n💸 Processing payments through Raft consensus...")
        payments = [
            ("rahul_mumbai", "priya_delhi", 2000.0),
            ("arjun_bangalore", "sneha_chennai", 1500.0),
            ("priya_delhi", "rahul_mumbai", 500.0)
        ]
        
        for from_wallet, to_wallet, amount in payments:
            print(f"\nProcessing payment: ₹{amount} from {from_wallet} to {to_wallet}")
            
            # Show balances before
            from_balance_before = leader_node.get_wallet_balance(from_wallet)
            to_balance_before = leader_node.get_wallet_balance(to_wallet)
            print(f"Before: {from_wallet}=₹{from_balance_before}, {to_wallet}=₹{to_balance_before}")
            
            # Process payment
            success = leader_node.process_payment(from_wallet, to_wallet, amount)
            
            if success:
                time.sleep(1)  # Wait for consensus
                
                # Show balances after
                from_balance_after = leader_node.get_wallet_balance(from_wallet)
                to_balance_after = leader_node.get_wallet_balance(to_wallet)
                print(f"After:  {from_wallet}=₹{from_balance_after}, {to_wallet}=₹{to_balance_after}")
                print("✅ Payment processed successfully")
            else:
                print("❌ Payment failed")
        
        # Verify consistency across all nodes
        print(f"\n🔍 Verifying consistency across all nodes...")
        consistent = True
        reference_balances = {}
        
        # Get balances from leader as reference
        for wallet_id, _ in wallets:
            reference_balances[wallet_id] = leader_node.get_wallet_balance(wallet_id)
        
        # Check other nodes
        for node_id, node in nodes.items():
            if node == leader_node:
                continue
                
            node_consistent = True
            for wallet_id in reference_balances:
                node_balance = node.get_wallet_balance(wallet_id)
                if node_balance != reference_balances[wallet_id]:
                    node_consistent = False
                    consistent = False
                    print(f"❌ Inconsistency in {node_id}: {wallet_id} has ₹{node_balance}, expected ₹{reference_balances[wallet_id]}")
            
            if node_consistent:
                print(f"✅ Node {node_id} is consistent with leader")
        
        if consistent:
            print("✅ All nodes are consistent!")
        
        # Show final cluster statistics
        print(f"\n📊 Final Cluster Statistics:")
        for node_id, node in nodes.items():
            status = node.get_node_status()
            print(f"Node {node_id}:")
            print(f"  State: {status['state']}")
            print(f"  Term: {status['current_term']}")
            print(f"  Log entries: {status['log_length']}")
            print(f"  Committed: {status['commit_index']}")
            print(f"  Processed transactions: {status['processed_transactions']}")
            print(f"  Total wallet balance: ₹{status['total_balance']}")
        
        # Production insights
        print(f"\n💡 Production Insights:")
        print(f"- Raft ensures strong consistency across payment nodes")
        print(f"- Leader election prevents split-brain scenarios")
        print(f"- Log replication guarantees transaction durability")
        print(f"- Handles network partitions gracefully")
        print(f"- Scales to 5-7 nodes typically (odd numbers preferred)")
        print(f"- Provides linearizable reads and writes")
        print(f"- Essential for financial applications requiring ACID properties")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up nodes...")
        for node in nodes.values():
            node.stop()

if __name__ == "__main__":
    demonstrate_phonePe_raft_consensus()