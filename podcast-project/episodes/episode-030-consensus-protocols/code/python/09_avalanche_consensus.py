#!/usr/bin/env python3
"""
Avalanche Consensus Implementation
=================================

Snow* family consensus protocols - Mumbai social consensus!
Just like Mumbai neighborhoods reach consensus through social influence,
Avalanche uses repeated sampling to achieve probabilistic consensus.

Features:
- Snowball sampling consensus
- Probabilistic finality
- High throughput
- Network effect amplification
- Mumbai social network simulation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import uuid
import math

class ConsensusState(Enum):
    """Consensus states in Avalanche"""
    UNKNOWN = "unknown"
    PREFERRED = "preferred"
    ACCEPTED = "accepted"
    FINALIZED = "finalized"

class NodeColor(Enum):
    """Node colors for binary consensus"""
    RED = "red"
    BLUE = "blue"
    UNCOLORED = "uncolored"

@dataclass
class Transaction:
    """
    Transaction in Avalanche
    """
    tx_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    nonce: int = 0
    
    def get_hash(self) -> str:
        """Calculate transaction hash"""
        data = f"{self.sender}:{self.receiver}:{self.amount}:{self.nonce}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def conflicts_with(self, other: 'Transaction') -> bool:
        """Check if this transaction conflicts with another"""
        # Simplified conflict detection (same sender, overlapping amounts)
        return (self.sender == other.sender and 
                abs(self.timestamp - other.timestamp) < 1.0)

@dataclass
class AvalancheNode:
    """
    Avalanche consensus node - Mumbai social influencer
    """
    node_id: str
    stake: float = 100.0  # Staking weight
    
    def __post_init__(self):
        # Consensus parameters
        self.alpha = 0.8  # Threshold for preference (80%)
        self.k = 10       # Sample size for querying
        self.beta_1 = 150  # Threshold for acceptance
        self.beta_2 = 200  # Threshold for finalization
        
        # Node state
        self.preferences: Dict[str, str] = {}  # tx_id -> preferred_choice
        self.confidence: Dict[str, int] = defaultdict(int)  # confidence counters
        self.accepted_transactions: Set[str] = set()
        self.finalized_transactions: Set[str] = set()
        
        # Network state
        self.neighbors: List[str] = []
        self.reputation: float = random.uniform(0.8, 1.0)
        
        # Mumbai characteristics
        self.social_influence = random.uniform(0.6, 0.95)
        self.response_reliability = random.uniform(0.85, 0.99)
        self.network_connectivity = random.uniform(0.9, 1.0)
        
        # Performance metrics
        self.queries_sent = 0
        self.queries_received = 0
        self.decisions_made = 0
        self.consensus_rounds = 0
        
        print(f"🗣️ Avalanche Node {node_id} initialized (stake: {stake})")
    
    def add_neighbor(self, neighbor_id: str):
        """Add neighbor node - Mumbai social connection"""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)
    
    def sample_neighbors(self, k: Optional[int] = None) -> List[str]:
        """
        Sample k random neighbors - Mumbai social polling
        """
        k = k or self.k
        if len(self.neighbors) <= k:
            return self.neighbors[:]
        
        return random.sample(self.neighbors, k)
    
    def query_neighbors(self, transaction: Transaction, 
                       neighbors: List[str]) -> Dict[str, bool]:
        """
        Query neighbors about transaction preference
        Mumbai social influence polling
        """
        self.queries_sent += 1
        responses = {}
        
        for neighbor_id in neighbors:
            # Simulate network delay and reliability
            if random.random() > self.network_connectivity:
                continue  # Network failure
            
            # Simulate neighbor response (would be actual network call)
            response = self.simulate_neighbor_response(neighbor_id, transaction)
            responses[neighbor_id] = response
        
        return responses
    
    def simulate_neighbor_response(self, neighbor_id: str, 
                                 transaction: Transaction) -> bool:
        """
        Simulate neighbor response - Mumbai social opinion
        """
        # Simplified response simulation
        # In real implementation, this would query actual neighbor node
        
        # Base preference influenced by transaction characteristics
        base_preference = 0.6
        
        # Social influence factor
        influence_factor = self.social_influence * random.uniform(0.8, 1.2)
        
        # Network effect - popular transactions get more support
        network_effect = min(1.0, len(self.preferences) / 100.0)
        
        final_score = base_preference * influence_factor + network_effect * 0.2
        
        return final_score > 0.7
    
    def update_preference(self, transaction: Transaction, 
                         query_responses: Dict[str, bool]):
        """
        Update preference based on neighbor responses
        Mumbai social consensus update
        """
        if not query_responses:
            return
        
        # Count positive responses
        positive_responses = sum(1 for response in query_responses.values() if response)
        total_responses = len(query_responses)
        
        # Calculate support ratio
        support_ratio = positive_responses / total_responses if total_responses > 0 else 0
        
        tx_id = transaction.tx_id
        
        # Update preference if threshold met
        if support_ratio >= self.alpha:
            # Prefer this transaction
            old_preference = self.preferences.get(tx_id, "none")
            self.preferences[tx_id] = "accept"
            
            # Increment confidence if preference strengthened
            if old_preference != "accept":
                self.confidence[tx_id] += 1
            else:
                self.confidence[tx_id] += 1
            
            print(f"   👍 {self.node_id} prefers tx {tx_id[:8]} (support: {support_ratio:.2%})")
            
        else:
            # Don't prefer this transaction
            self.preferences[tx_id] = "reject"
            self.confidence[tx_id] = max(0, self.confidence[tx_id] - 1)
            
            print(f"   👎 {self.node_id} rejects tx {tx_id[:8]} (support: {support_ratio:.2%})")
    
    def check_acceptance(self, transaction: Transaction) -> bool:
        """
        Check if transaction should be accepted
        """
        tx_id = transaction.tx_id
        confidence = self.confidence.get(tx_id, 0)
        
        if confidence >= self.beta_1 and tx_id not in self.accepted_transactions:
            self.accepted_transactions.add(tx_id)
            print(f"   ✅ {self.node_id} ACCEPTED tx {tx_id[:8]} (confidence: {confidence})")
            return True
        
        return False
    
    def check_finalization(self, transaction: Transaction) -> bool:
        """
        Check if transaction should be finalized
        """
        tx_id = transaction.tx_id
        confidence = self.confidence.get(tx_id, 0)
        
        if confidence >= self.beta_2 and tx_id not in self.finalized_transactions:
            self.finalized_transactions.add(tx_id)
            print(f"   🏆 {self.node_id} FINALIZED tx {tx_id[:8]} (confidence: {confidence})")
            return True
        
        return False
    
    def process_transaction_consensus(self, transaction: Transaction) -> str:
        """
        Process single transaction through Avalanche consensus
        Mumbai social decision making
        """
        tx_id = transaction.tx_id
        
        print(f"\n🔄 {self.node_id} processing consensus for tx {tx_id[:8]}")
        
        # Sample neighbors
        neighbors = self.sample_neighbors()
        if not neighbors:
            print(f"   ❌ No neighbors to query")
            return ConsensusState.UNKNOWN.value
        
        # Query neighbors
        responses = self.query_neighbors(transaction, neighbors)
        
        # Update preference
        self.update_preference(transaction, responses)
        
        # Check for acceptance
        self.check_acceptance(transaction)
        
        # Check for finalization
        self.check_finalization(transaction)
        
        self.consensus_rounds += 1
        
        # Return current state
        confidence = self.confidence.get(tx_id, 0)
        if tx_id in self.finalized_transactions:
            return ConsensusState.FINALIZED.value
        elif tx_id in self.accepted_transactions:
            return ConsensusState.ACCEPTED.value
        elif confidence > 0:
            return ConsensusState.PREFERRED.value
        else:
            return ConsensusState.UNKNOWN.value
    
    def respond_to_query(self, transaction: Transaction) -> bool:
        """
        Respond to query from another node
        """
        self.queries_received += 1
        
        # Check reliability
        if random.random() > self.response_reliability:
            return False  # Failed to respond
        
        tx_id = transaction.tx_id
        
        # Base response on current preference
        if tx_id in self.preferences:
            return self.preferences[tx_id] == "accept"
        
        # If no preference, base on transaction validity and social factors
        return self.evaluate_transaction_default(transaction)
    
    def evaluate_transaction_default(self, transaction: Transaction) -> bool:
        """
        Default evaluation for transactions without existing preference
        """
        # Simple heuristic evaluation
        factors = {
            "amount_reasonable": transaction.amount <= 1000.0,  # Reasonable amount
            "recent_timestamp": (time.time() - transaction.timestamp) < 3600,  # Recent
            "valid_addresses": len(transaction.sender) > 0 and len(transaction.receiver) > 0,
            "social_factor": random.random() < self.social_influence
        }
        
        positive_factors = sum(1 for factor in factors.values() if factor)
        return positive_factors >= 3  # Majority of factors positive
    
    def get_node_stats(self) -> Dict:
        """Get node performance statistics"""
        return {
            "node_id": self.node_id,
            "stake": self.stake,
            "neighbors": len(self.neighbors),
            "preferences": len(self.preferences),
            "accepted_transactions": len(self.accepted_transactions),
            "finalized_transactions": len(self.finalized_transactions),
            "queries_sent": self.queries_sent,
            "queries_received": self.queries_received,
            "consensus_rounds": self.consensus_rounds,
            "reputation": self.reputation,
            "social_influence": self.social_influence,
            "response_reliability": self.response_reliability
        }

class AvalancheNetwork:
    """
    Avalanche consensus network - Mumbai social network
    """
    
    def __init__(self, num_nodes: int = 20):
        self.nodes: Dict[str, AvalancheNode] = {}
        self.num_nodes = num_nodes
        
        # Network topology
        self.connection_density = 0.3  # 30% connectivity
        
        # Consensus tracking
        self.pending_transactions: List[Transaction] = []
        self.finalized_transactions: Set[str] = set()
        
        # Performance metrics
        self.total_consensus_rounds = 0
        self.successful_finalizations = 0
        
        print(f"🌐 Avalanche Network initialized with {num_nodes} nodes")
        
        self.create_nodes()
        self.create_network_topology()
    
    def create_nodes(self):
        """Create network nodes with Mumbai characteristics"""
        mumbai_areas = [
            "Bandra", "Andheri", "Borivali", "Thane", "Kurla", "Worli", "Colaba",
            "Powai", "Vikhroli", "Malad", "Kandivali", "Dahisar", "Mulund",
            "Chembur", "Ghatkopar", "Santacruz", "Vile_Parle", "Khar", "Juhu", "Goregaon"
        ]
        
        for i in range(self.num_nodes):
            area_name = mumbai_areas[i] if i < len(mumbai_areas) else f"Area_{i}"
            
            # Varying stakes based on area characteristics
            stake = random.uniform(50, 200)  # Different economic zones
            
            node = AvalancheNode(f"node_{area_name}", stake)
            self.nodes[node.node_id] = node
    
    def create_network_topology(self):
        """
        Create network topology - Mumbai social connections
        """
        print("🔗 Creating network topology...")
        
        node_ids = list(self.nodes.keys())
        
        for node_id in node_ids:
            node = self.nodes[node_id]
            
            # Each node connects to random subset of other nodes
            potential_neighbors = [nid for nid in node_ids if nid != node_id]
            num_connections = int(len(potential_neighbors) * self.connection_density)
            
            if num_connections > 0:
                neighbors = random.sample(potential_neighbors, 
                                        min(num_connections, len(potential_neighbors)))
                
                for neighbor_id in neighbors:
                    node.add_neighbor(neighbor_id)
                    # Bidirectional connection
                    self.nodes[neighbor_id].add_neighbor(node_id)
        
        # Print connectivity stats
        avg_connections = sum(len(node.neighbors) for node in self.nodes.values()) / len(self.nodes)
        print(f"   Average connections per node: {avg_connections:.1f}")
    
    def submit_transaction(self, transaction: Transaction):
        """
        Submit transaction to network
        """
        self.pending_transactions.append(transaction)
        print(f"📝 Transaction {transaction.tx_id[:8]} submitted to network")
    
    def run_consensus_round(self, transaction: Transaction) -> Dict[str, str]:
        """
        Run consensus round across all nodes
        Mumbai social consensus wave
        """
        print(f"\n🌊 CONSENSUS WAVE for tx {transaction.tx_id[:8]}")
        print("=" * 50)
        
        round_results = {}
        
        # All nodes process transaction simultaneously
        for node_id, node in self.nodes.items():
            try:
                state = node.process_transaction_consensus(transaction)
                round_results[node_id] = state
                
            except Exception as e:
                print(f"   ❌ {node_id} consensus error: {str(e)}")
                round_results[node_id] = ConsensusState.UNKNOWN.value
        
        # Analyze round results
        state_counts = Counter(round_results.values())
        
        print(f"\n📊 Round Results:")
        for state, count in state_counts.items():
            percentage = (count / len(self.nodes)) * 100
            print(f"   {state.title()}: {count} nodes ({percentage:.1f}%)")
        
        return round_results
    
    def simulate_avalanche_consensus(self, transactions: List[Transaction], 
                                   max_rounds: int = 20) -> Dict:
        """
        Simulate complete Avalanche consensus process
        Mumbai social consensus simulation
        """
        print(f"\n❄️ AVALANCHE CONSENSUS SIMULATION")
        print(f"Transactions: {len(transactions)}")
        print(f"Max rounds per transaction: {max_rounds}")
        print("=" * 60)
        
        consensus_results = []
        
        for tx_idx, transaction in enumerate(transactions):
            print(f"\n{'='*60}")
            print(f"TRANSACTION {tx_idx + 1}/{len(transactions)}")
            print(f"{'='*60}")
            print(f"TX ID: {transaction.tx_id}")
            print(f"Amount: {transaction.amount}")
            print(f"Sender: {transaction.sender} → Receiver: {transaction.receiver}")
            
            tx_consensus_data = {
                "transaction_id": transaction.tx_id,
                "rounds": [],
                "final_state": "unknown",
                "finalization_round": None,
                "acceptance_round": None
            }
            
            # Run consensus rounds until finalization or max rounds
            for round_num in range(max_rounds):
                round_results = self.run_consensus_round(transaction)
                
                # Record round data
                round_data = {
                    "round": round_num + 1,
                    "state_distribution": dict(Counter(round_results.values())),
                    "finalized_nodes": len([s for s in round_results.values() 
                                          if s == ConsensusState.FINALIZED.value]),
                    "accepted_nodes": len([s for s in round_results.values() 
                                         if s == ConsensusState.ACCEPTED.value])
                }
                
                tx_consensus_data["rounds"].append(round_data)
                
                # Check for network-wide acceptance
                finalized_count = round_data["finalized_nodes"]
                accepted_count = round_data["accepted_nodes"]
                
                finalization_threshold = int(len(self.nodes) * 0.8)  # 80% threshold
                acceptance_threshold = int(len(self.nodes) * 0.6)    # 60% threshold
                
                if finalized_count >= finalization_threshold:
                    tx_consensus_data["final_state"] = "finalized"
                    tx_consensus_data["finalization_round"] = round_num + 1
                    self.finalized_transactions.add(transaction.tx_id)
                    self.successful_finalizations += 1
                    
                    print(f"   🏆 TRANSACTION FINALIZED in round {round_num + 1}")
                    break
                    
                elif accepted_count >= acceptance_threshold and not tx_consensus_data["acceptance_round"]:
                    tx_consensus_data["acceptance_round"] = round_num + 1
                    print(f"   ✅ TRANSACTION ACCEPTED in round {round_num + 1}")
                
                # Small delay between rounds
                time.sleep(0.1)
            
            else:
                # Max rounds reached without finalization
                print(f"   ⏰ Max rounds reached without finalization")
                
                # Determine final state
                final_round = tx_consensus_data["rounds"][-1] if tx_consensus_data["rounds"] else {}
                finalized_nodes = final_round.get("finalized_nodes", 0)
                accepted_nodes = final_round.get("accepted_nodes", 0)
                
                if finalized_nodes > len(self.nodes) // 2:
                    tx_consensus_data["final_state"] = "likely_finalized"
                elif accepted_nodes > len(self.nodes) // 2:
                    tx_consensus_data["final_state"] = "accepted"
                else:
                    tx_consensus_data["final_state"] = "rejected"
            
            consensus_results.append(tx_consensus_data)
            self.total_consensus_rounds += len(tx_consensus_data["rounds"])
            
            # Brief pause between transactions
            time.sleep(0.5)
        
        return {
            "total_transactions": len(transactions),
            "successful_finalizations": self.successful_finalizations,
            "finalization_rate": (self.successful_finalizations / len(transactions)) * 100,
            "average_rounds": self.total_consensus_rounds / len(transactions),
            "transaction_details": consensus_results
        }
    
    def get_network_stats(self) -> Dict:
        """Get network performance statistics"""
        node_stats = [node.get_node_stats() for node in self.nodes.values()]
        
        total_queries = sum(node.queries_sent for node in self.nodes.values())
        total_responses = sum(node.queries_received for node in self.nodes.values())
        avg_neighbors = sum(len(node.neighbors) for node in self.nodes.values()) / len(self.nodes)
        
        return {
            "total_nodes": len(self.nodes),
            "average_neighbors": avg_neighbors,
            "total_queries": total_queries,
            "total_responses": total_responses,
            "successful_finalizations": self.successful_finalizations,
            "total_consensus_rounds": self.total_consensus_rounds,
            "finalized_transactions": len(self.finalized_transactions),
            "node_details": node_stats
        }

def create_sample_transactions() -> List[Transaction]:
    """
    Create sample transactions - Mumbai commerce
    """
    mumbai_users = [
        "Ravi_Bandra", "Priya_Andheri", "Amit_Borivali", "Sunita_Thane",
        "Kiran_Kurla", "Deepak_Worli", "Meera_Colaba", "Vikram_Powai"
    ]
    
    transactions = []
    
    for i in range(12):
        sender = random.choice(mumbai_users)
        receiver = random.choice([u for u in mumbai_users if u != sender])
        amount = random.uniform(10, 500)
        
        tx = Transaction(
            tx_id=f"tx_mumbai_{i:03d}_{int(time.time())}",
            sender=sender,
            receiver=receiver,
            amount=amount,
            nonce=i
        )
        
        transactions.append(tx)
    
    return transactions

if __name__ == "__main__":
    print("🚀 AVALANCHE CONSENSUS PROTOCOL")
    print("Mumbai Social Network Consensus Simulation")
    print("=" * 70)
    
    try:
        # Create Avalanche network
        network = AvalancheNetwork(num_nodes=15)
        
        # Show initial network state
        initial_stats = network.get_network_stats()
        print(f"\n📊 INITIAL NETWORK STATE")
        print("-" * 40)
        print(f"Total nodes: {initial_stats['total_nodes']}")
        print(f"Average neighbors: {initial_stats['average_neighbors']:.1f}")
        
        # Create sample transactions
        transactions = create_sample_transactions()
        print(f"\n📝 Created {len(transactions)} sample transactions")
        
        # Run Avalanche consensus simulation
        simulation_results = network.simulate_avalanche_consensus(
            transactions, max_rounds=15
        )
        
        # Analyze results
        print(f"\n📈 SIMULATION RESULTS")
        print("=" * 50)
        print(f"Total transactions: {simulation_results['total_transactions']}")
        print(f"Successful finalizations: {simulation_results['successful_finalizations']}")
        print(f"Finalization rate: {simulation_results['finalization_rate']:.1f}%")
        print(f"Average rounds per transaction: {simulation_results['average_rounds']:.1f}")
        
        # Show transaction details
        print(f"\n🔍 TRANSACTION BREAKDOWN")
        print("-" * 40)
        for tx_data in simulation_results['transaction_details'][:5]:  # Show first 5
            tx_id = tx_data['transaction_id'][:8]
            final_state = tx_data['final_state']
            rounds = len(tx_data['rounds'])
            finalization_round = tx_data['finalization_round']
            
            print(f"{tx_id}: {final_state} in {rounds} rounds" + 
                  (f" (finalized in round {finalization_round})" if finalization_round else ""))
        
        # Final network statistics
        final_stats = network.get_network_stats()
        
        print(f"\n🏆 FINAL NETWORK STATISTICS")
        print("-" * 40)
        print(f"Total queries sent: {final_stats['total_queries']}")
        print(f"Total responses: {final_stats['total_responses']}")
        print(f"Query response rate: {final_stats['total_responses']/max(1,final_stats['total_queries'])*100:.1f}%")
        
        print("\n🎯 Key Insights:")
        print("• Avalanche achieves probabilistic consensus through sampling")
        print("• Network effects amplify preferences quickly")
        print("• High throughput with eventual consistency")
        print("• Like Mumbai social networks - influence spreads through connections!")
        
        print("\n🎊 AVALANCHE CONSENSUS SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in Avalanche simulation: {e}")
        raise