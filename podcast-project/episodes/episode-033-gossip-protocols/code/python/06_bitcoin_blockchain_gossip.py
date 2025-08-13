#!/usr/bin/env python3
"""
Bitcoin Blockchain Transaction Gossip Protocol
==============================================

Bitcoin Network में Transaction Propagation: जब आप Bitcoin send करते हैं
तो कैसे वो transaction पूरे network में पहुंचती है gossip के through?

This simulates how Bitcoin nodes use gossip protocol to propagate
transactions and blocks across the peer-to-peer network.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import hashlib
import asyncio
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class TransactionStatus(Enum):
    """Bitcoin transaction states"""
    PENDING = "pending"         # Transaction created
    MEMPOOL = "mempool"        # In memory pool
    CONFIRMED = "confirmed"     # In a block
    REJECTED = "rejected"       # Invalid transaction


@dataclass
class BitcoinTransaction:
    """Bitcoin transaction structure"""
    tx_id: str
    sender: str
    receiver: str
    amount: float
    fee: float
    timestamp: float
    nonce: int = 0
    status: TransactionStatus = TransactionStatus.PENDING
    confirmations: int = 0
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        tx_string = f"{self.sender}{self.receiver}{self.amount}{self.fee}{self.nonce}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()
        
    def is_valid(self) -> bool:
        """Validate transaction (simplified)"""
        if self.amount <= 0 or self.fee < 0:
            return False
        if self.sender == self.receiver:
            return False
        if len(self.sender) < 10 or len(self.receiver) < 10:
            return False
        return True


@dataclass
class BitcoinBlock:
    """Bitcoin block structure"""
    block_id: str
    previous_hash: str
    transactions: List[BitcoinTransaction]
    timestamp: float
    nonce: int = 0
    difficulty: int = 4
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        tx_hashes = [tx.calculate_hash() for tx in self.transactions]
        block_string = f"{self.previous_hash}{''.join(tx_hashes)}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
        
    def mine_block(self) -> str:
        """Simple proof of work mining"""
        target = "0" * self.difficulty
        
        while True:
            block_hash = self.calculate_hash()
            if block_hash.startswith(target):
                return block_hash
            self.nonce += 1
            
            # Prevent infinite loop in simulation
            if self.nonce > 10000:
                break
                
        return self.calculate_hash()


class BitcoinNode:
    """
    Bitcoin Network Node
    
    हर node एक participant है जो transactions और blocks को
    network में gossip करता है
    """
    
    def __init__(self, node_id: str, region: str, is_miner: bool = False):
        self.node_id = node_id
        self.region = region
        self.is_miner = is_miner
        
        # Network connectivity
        self.peers: Set[str] = set()
        self.connection_quality: Dict[str, float] = {}
        
        # Transaction and block storage
        self.mempool: Dict[str, BitcoinTransaction] = {}
        self.blockchain: List[BitcoinBlock] = []
        self.known_transactions: Set[str] = set()
        self.known_blocks: Set[str] = set()
        
        # Gossip protocol settings
        self.max_peers = 8  # Bitcoin typically maintains 8 outbound connections
        self.gossip_fanout = 3
        self.inventory_limit = 50000  # Max items to track
        
        # Performance metrics
        self.transactions_propagated = 0
        self.blocks_propagated = 0
        self.bandwidth_used = 0
        self.latency_sum = 0
        self.latency_count = 0
        
        # Mining (if miner)
        self.mining_power = random.uniform(0.1, 2.0) if is_miner else 0.0
        self.mining_reward = 6.25  # Current Bitcoin reward
        
        # Relay policies
        self.min_fee_rate = 1.0  # Minimum fee per byte
        self.relay_dust_limit = 546  # Satoshis
        
    def add_peer(self, peer_id: str, quality: float = 1.0):
        """Add peer connection"""
        if len(self.peers) < self.max_peers:
            self.peers.add(peer_id)
            self.connection_quality[peer_id] = quality
            
    def create_transaction(self, receiver: str, amount: float, fee: float) -> BitcoinTransaction:
        """Create new Bitcoin transaction"""
        tx_id = hashlib.sha256(f"{self.node_id}{receiver}{amount}{time.time()}".encode()).hexdigest()
        
        transaction = BitcoinTransaction(
            tx_id=tx_id,
            sender=self.node_id,
            receiver=receiver,
            amount=amount,
            fee=fee,
            timestamp=time.time()
        )
        
        if transaction.is_valid():
            self.add_transaction_to_mempool(transaction)
            return transaction
        else:
            transaction.status = TransactionStatus.REJECTED
            return transaction
            
    def add_transaction_to_mempool(self, transaction: BitcoinTransaction):
        """Add transaction to mempool"""
        if transaction.tx_id not in self.known_transactions and transaction.is_valid():
            self.mempool[transaction.tx_id] = transaction
            self.known_transactions.add(transaction.tx_id)
            transaction.status = TransactionStatus.MEMPOOL
            
            print(f"💰 Node {self.node_id} added transaction to mempool: "
                  f"{transaction.amount} BTC (fee: {transaction.fee})")
                  
    def validate_transaction(self, transaction: BitcoinTransaction) -> bool:
        """Validate incoming transaction"""
        # Basic validation
        if not transaction.is_valid():
            return False
            
        # Fee validation
        if transaction.fee < self.min_fee_rate:
            return False
            
        # Dust limit check
        if transaction.amount * 100000000 < self.relay_dust_limit:  # Convert to satoshis
            return False
            
        # Double spending check (simplified)
        if transaction.tx_id in self.known_transactions:
            return False
            
        return True
        
    def receive_transaction(self, transaction: BitcoinTransaction, from_peer: str) -> bool:
        """
        Receive transaction from peer
        Returns True if transaction is new and valid
        """
        if transaction.tx_id in self.known_transactions:
            return False  # Already known
            
        if not self.validate_transaction(transaction):
            print(f"❌ Node {self.node_id} rejected invalid transaction {transaction.tx_id[:8]}")
            return False
            
        # Add to mempool
        self.add_transaction_to_mempool(transaction)
        
        # Track propagation latency
        if hasattr(transaction, 'created_time'):
            latency = time.time() - transaction.created_time
            self.latency_sum += latency
            self.latency_count += 1
            
        return True
        
    def receive_block(self, block: BitcoinBlock, from_peer: str) -> bool:
        """
        Receive block from peer
        Returns True if block is new and valid
        """
        block_hash = block.calculate_hash()
        
        if block_hash in self.known_blocks:
            return False  # Already known
            
        # Validate block (simplified)
        if not self.validate_block(block):
            print(f"❌ Node {self.node_id} rejected invalid block {block_hash[:8]}")
            return False
            
        # Add to blockchain
        self.blockchain.append(block)
        self.known_blocks.add(block_hash)
        
        # Remove confirmed transactions from mempool
        for tx in block.transactions:
            if tx.tx_id in self.mempool:
                del self.mempool[tx.tx_id]
                tx.status = TransactionStatus.CONFIRMED
                tx.confirmations = 1
                
        print(f"🧱 Node {self.node_id} accepted new block with {len(block.transactions)} transactions")
        return True
        
    def validate_block(self, block: BitcoinBlock) -> bool:
        """Validate incoming block"""
        # Check if previous hash matches
        if self.blockchain and block.previous_hash != self.blockchain[-1].calculate_hash():
            return False
            
        # Validate all transactions in block
        for tx in block.transactions:
            if not tx.is_valid():
                return False
                
        # Check proof of work (simplified)
        block_hash = block.calculate_hash()
        if not block_hash.startswith("0" * block.difficulty):
            return False
            
        return True
        
    def select_peers_for_relay(self, item_type: str) -> List[str]:
        """Select peers to relay transaction/block to"""
        if not self.peers:
            return []
            
        # For transactions: relay to subset of peers
        if item_type == "transaction":
            num_peers = min(self.gossip_fanout, len(self.peers))
            
        # For blocks: relay to all peers (high priority)
        else:  # block
            num_peers = len(self.peers)
            
        # Weight by connection quality
        weighted_peers = [
            (peer_id, self.connection_quality.get(peer_id, 1.0))
            for peer_id in self.peers
        ]
        
        # Sort by quality and select top peers
        weighted_peers.sort(key=lambda x: x[1], reverse=True)
        selected_peers = [peer_id for peer_id, _ in weighted_peers[:num_peers]]
        
        return selected_peers
        
    def attempt_mining(self) -> Optional[BitcoinBlock]:
        """Attempt to mine a new block (simplified)"""
        if not self.is_miner or len(self.mempool) < 1:
            return None
            
        # Mining success probability based on mining power
        mining_probability = self.mining_power / 100.0  # Normalize
        
        if random.random() < mining_probability:
            # Select transactions for block (by fee priority)
            transactions = list(self.mempool.values())
            transactions.sort(key=lambda tx: tx.fee, reverse=True)
            
            # Take top transactions (max block size limit)
            block_transactions = transactions[:2000]  # Simplified limit
            
            # Create coinbase transaction (mining reward)
            coinbase_tx = BitcoinTransaction(
                tx_id=f"coinbase_{self.node_id}_{int(time.time())}",
                sender="coinbase",
                receiver=self.node_id,
                amount=self.mining_reward,
                fee=0.0,
                timestamp=time.time(),
                status=TransactionStatus.CONFIRMED
            )
            
            block_transactions.insert(0, coinbase_tx)
            
            # Create block
            previous_hash = self.blockchain[-1].calculate_hash() if self.blockchain else "0" * 64
            
            block = BitcoinBlock(
                block_id=f"block_{len(self.blockchain)}_{self.node_id}",
                previous_hash=previous_hash,
                transactions=block_transactions,
                timestamp=time.time()
            )
            
            # Mine the block
            block_hash = block.mine_block()
            
            print(f"⛏️  Node {self.node_id} mined new block! Hash: {block_hash[:16]}...")
            return block
            
        return None
        
    def gossip_round(self) -> Dict:
        """
        Perform gossip round for transactions and blocks
        Returns dict of peer_id -> items to send
        """
        gossip_plan = {}
        
        # Relay recent transactions
        recent_transactions = [
            tx for tx in self.mempool.values()
            if time.time() - tx.timestamp < 60.0  # Last minute
        ]
        
        if recent_transactions:
            tx_peers = self.select_peers_for_relay("transaction")
            for peer_id in tx_peers:
                if peer_id not in gossip_plan:
                    gossip_plan[peer_id] = {"transactions": [], "blocks": []}
                gossip_plan[peer_id]["transactions"].extend(recent_transactions[:10])
                
        # Relay recent blocks
        recent_blocks = [
            block for block in self.blockchain
            if time.time() - block.timestamp < 600.0  # Last 10 minutes
        ]
        
        if recent_blocks:
            block_peers = self.select_peers_for_relay("block")
            for peer_id in block_peers:
                if peer_id not in gossip_plan:
                    gossip_plan[peer_id] = {"transactions": [], "blocks": []}
                gossip_plan[peer_id]["blocks"].extend(recent_blocks[:3])
                
        # Update bandwidth usage
        for peer_id, items in gossip_plan.items():
            tx_count = len(items["transactions"])
            block_count = len(items["blocks"])
            self.bandwidth_used += (tx_count * 250) + (block_count * 1000000)  # Rough bytes
            
        return gossip_plan
        
    def get_node_stats(self) -> Dict:
        """Get node performance statistics"""
        avg_latency = (self.latency_sum / self.latency_count) if self.latency_count > 0 else 0
        
        return {
            "node_id": self.node_id,
            "region": self.region,
            "is_miner": self.is_miner,
            "peers": len(self.peers),
            "mempool_size": len(self.mempool),
            "blockchain_length": len(self.blockchain),
            "transactions_propagated": self.transactions_propagated,
            "blocks_propagated": self.blocks_propagated,
            "bandwidth_used_mb": self.bandwidth_used / (1024 * 1024),
            "avg_latency_ms": avg_latency * 1000,
            "mining_power": self.mining_power
        }


class BitcoinNetwork:
    """Bitcoin P2P Network Simulator"""
    
    def __init__(self):
        self.nodes: Dict[str, BitcoinNode] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_round = 0
        self.genesis_block = None
        
    def create_bitcoin_network(self, num_nodes: int = 20, num_miners: int = 4):
        """Create Bitcoin network topology"""
        # Global regions for Bitcoin nodes
        regions = [
            "North_America", "Europe", "Asia_Pacific", "South_America",
            "Africa", "Middle_East", "India", "China"
        ]
        
        # Create nodes
        miners_created = 0
        for i in range(num_nodes):
            node_id = f"node_{i+1:03d}"
            region = random.choice(regions)
            is_miner = miners_created < num_miners and random.random() < 0.3
            
            if is_miner:
                miners_created += 1
                
            self.nodes[node_id] = BitcoinNode(node_id, region, is_miner)
            
        # Create network topology (small world network)
        node_ids = list(self.nodes.keys())
        
        for node_id in node_ids:
            # Connect to random peers (Bitcoin-like topology)
            num_connections = random.randint(3, 8)
            potential_peers = [nid for nid in node_ids if nid != node_id]
            
            selected_peers = random.sample(
                potential_peers, 
                min(num_connections, len(potential_peers))
            )
            
            for peer_id in selected_peers:
                self.add_connection(node_id, peer_id)
                
        # Create genesis block
        self.create_genesis_block()
        
    def add_connection(self, node1: str, node2: str):
        """Add bidirectional connection between nodes"""
        if node1 in self.nodes and node2 in self.nodes:
            # Connection quality based on geographic proximity (simplified)
            quality = random.uniform(0.7, 1.0)
            
            self.nodes[node1].add_peer(node2, quality)
            self.nodes[node2].add_peer(node1, quality)
            
            if (node1, node2) not in self.connections and (node2, node1) not in self.connections:
                self.connections.append((node1, node2))
                
    def create_genesis_block(self):
        """Create genesis block for all nodes"""
        genesis_tx = BitcoinTransaction(
            tx_id="genesis_tx",
            sender="genesis",
            receiver="satoshi",
            amount=50.0,
            fee=0.0,
            timestamp=time.time(),
            status=TransactionStatus.CONFIRMED
        )
        
        self.genesis_block = BitcoinBlock(
            block_id="genesis_block",
            previous_hash="0" * 64,
            transactions=[genesis_tx],
            timestamp=time.time()
        )
        
        # Add genesis block to all nodes
        for node in self.nodes.values():
            node.blockchain.append(self.genesis_block)
            node.known_blocks.add(self.genesis_block.calculate_hash())
            
    def inject_transactions(self, num_transactions: int = 5):
        """Inject random transactions into the network"""
        node_ids = list(self.nodes.keys())
        
        for _ in range(num_transactions):
            sender_id = random.choice(node_ids)
            receiver_id = random.choice([nid for nid in node_ids if nid != sender_id])
            
            amount = random.uniform(0.1, 10.0)
            fee = random.uniform(0.001, 0.01)
            
            sender_node = self.nodes[sender_id]
            transaction = sender_node.create_transaction(receiver_id, amount, fee)
            
            if transaction.status != TransactionStatus.REJECTED:
                transaction.created_time = time.time()
                print(f"💸 New transaction: {sender_id} → {receiver_id}: {amount:.3f} BTC")
                
    def simulate_round(self) -> Dict:
        """Simulate one round of network activity"""
        self.simulation_round += 1
        
        round_stats = {
            "transactions_propagated": 0,
            "blocks_propagated": 0,
            "new_blocks_mined": 0
        }
        
        # Mining attempts
        for node in self.nodes.values():
            if node.is_miner:
                new_block = node.attempt_mining()
                if new_block:
                    # Add block to miner's blockchain
                    node.receive_block(new_block, node.node_id)
                    round_stats["new_blocks_mined"] += 1
                    
        # Collect gossip plans
        all_gossip_plans = {}
        for node_id, node in self.nodes.items():
            gossip_plan = node.gossip_round()
            if gossip_plan:
                all_gossip_plans[node_id] = gossip_plan
                
        # Execute gossip (relay transactions and blocks)
        for sender_id, peer_plans in all_gossip_plans.items():
            for peer_id, items in peer_plans.items():
                if peer_id in self.nodes:
                    peer_node = self.nodes[peer_id]
                    
                    # Relay transactions
                    for tx in items.get("transactions", []):
                        if peer_node.receive_transaction(tx, sender_id):
                            round_stats["transactions_propagated"] += 1
                            
                    # Relay blocks
                    for block in items.get("blocks", []):
                        if peer_node.receive_block(block, sender_id):
                            round_stats["blocks_propagated"] += 1
                            
        return round_stats


async def main():
    """Main simulation function"""
    print("🇮🇳 Bitcoin Network Gossip Protocol Simulation")
    print("=" * 50)
    
    # Create Bitcoin network
    network = BitcoinNetwork()
    network.create_bitcoin_network(20, 4)
    
    print(f"Created Bitcoin network with {len(network.nodes)} nodes")
    print(f"Miners: {len([n for n in network.nodes.values() if n.is_miner])}")
    print(f"Total connections: {len(network.connections)}")
    
    # Simulate for 15 rounds
    for round_num in range(15):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Inject transactions periodically
        if round_num % 3 == 0:
            network.inject_transactions(3)
            
        # Simulate network gossip
        round_stats = network.simulate_round()
        
        print(f"Round stats: {round_stats}")
        
        # Print network status every few rounds
        if round_num % 4 == 0:
            print(f"\n📊 Network Status:")
            
            # Overall statistics
            total_mempool = sum(len(node.mempool) for node in network.nodes.values())
            total_blockchain_length = sum(len(node.blockchain) for node in network.nodes.values())
            
            print(f"  Total mempool transactions: {total_mempool}")
            print(f"  Average blockchain length: {total_blockchain_length / len(network.nodes):.1f}")
            
            # Top performing nodes
            top_nodes = sorted(
                network.nodes.values(),
                key=lambda n: n.transactions_propagated + n.blocks_propagated,
                reverse=True
            )[:3]
            
            print(f"  Top propagation nodes:")
            for i, node in enumerate(top_nodes, 1):
                stats = node.get_node_stats()
                print(f"    {i}. {node.node_id} ({node.region}): "
                      f"TX={stats['transactions_propagated']}, "
                      f"Blocks={stats['blocks_propagated']}")
                      
        await asyncio.sleep(0.5)
        
    # Final network analysis
    print(f"\n📈 Final Network Analysis:")
    
    # Calculate network-wide metrics
    all_stats = [node.get_node_stats() for node in network.nodes.values()]
    
    avg_bandwidth = sum(stats['bandwidth_used_mb'] for stats in all_stats) / len(all_stats)
    avg_latency = sum(stats['avg_latency_ms'] for stats in all_stats if stats['avg_latency_ms'] > 0)
    avg_latency = avg_latency / len([s for s in all_stats if s['avg_latency_ms'] > 0]) if avg_latency > 0 else 0
    
    total_blocks = sum(stats['blockchain_length'] for stats in all_stats) / len(all_stats)
    
    print(f"Average bandwidth usage: {avg_bandwidth:.2f} MB per node")
    print(f"Average transaction latency: {avg_latency:.1f} ms")
    print(f"Average blockchain length: {total_blocks:.1f} blocks")
    
    # Mining statistics
    miners = [node for node in network.nodes.values() if node.is_miner]
    if miners:
        print(f"\n⛏️  Mining Performance:")
        for miner in miners:
            blocks_mined = len([b for b in miner.blockchain if b.block_id.endswith(miner.node_id)])
            print(f"  {miner.node_id}: {blocks_mined} blocks mined, "
                  f"power: {miner.mining_power:.2f}")


if __name__ == "__main__":
    asyncio.run(main())