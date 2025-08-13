#!/usr/bin/env python3
"""
Blockchain Consensus with Byzantine Fault Tolerance
Real-world application: Cryptocurrency networks and enterprise blockchain

यह implementation blockchain में Byzantine consensus को demonstrate करती है
जैसे कि Bitcoin, Ethereum, और Hyperledger में consensus achieve होती है
"""

import time
import threading
import hashlib
import json
import random
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import uuid
from decimal import Decimal

class NodeRole(Enum):
    MINER = "miner"              # Bitcoin-style miners
    VALIDATOR = "validator"       # PoS validators
    FULL_NODE = "full_node"      # Full nodes that validate
    LIGHT_NODE = "light_node"    # Light clients

class ConsensusType(Enum):
    PROOF_OF_WORK = "proof_of_work"
    PROOF_OF_STAKE = "proof_of_stake"
    PBFT = "pbft"
    RAFT = "raft"

@dataclass
class Transaction:
    """Blockchain transaction"""
    txn_id: str
    sender: str
    receiver: str
    amount: Decimal
    fee: Decimal
    timestamp: float
    nonce: int = 0
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            # Create transaction signature
            txn_data = f"{self.sender}:{self.receiver}:{self.amount}:{self.timestamp}:{self.nonce}"
            self.signature = hashlib.sha256(txn_data.encode()).hexdigest()[:16]
    
    def get_hash(self) -> str:
        """Get transaction hash"""
        txn_data = f"{self.txn_id}:{self.sender}:{self.receiver}:{self.amount}:{self.timestamp}"
        return hashlib.sha256(txn_data.encode()).hexdigest()

@dataclass 
class Block:
    """Blockchain block"""
    block_number: int
    previous_hash: str
    transactions: List[Transaction]
    timestamp: float
    miner: str
    nonce: int = 0
    merkle_root: str = ""
    block_hash: str = ""
    
    def __post_init__(self):
        if not self.merkle_root:
            self.merkle_root = self.calculate_merkle_root()
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
    
    def calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()
        
        hashes = [tx.get_hash() for tx in self.transactions]
        
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined = left + right
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level
        
        return hashes[0]
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = f"{self.block_number}:{self.previous_hash}:{self.merkle_root}:{self.timestamp}:{self.nonce}"
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Mine block with Proof of Work"""
        target = "0" * difficulty
        start_time = time.time()
        
        while not self.block_hash.startswith(target):
            self.nonce += 1
            self.block_hash = self.calculate_hash()
        
        mining_time = time.time() - start_time
        print(f"⛏️ Block {self.block_number} mined by {self.miner} in {mining_time:.2f}s (nonce: {self.nonce})")

@dataclass
class ConsensusMessage:
    """Consensus protocol message"""
    msg_type: str
    sender: str
    content: Any
    block_number: int
    timestamp: float
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            msg_data = f"{self.msg_type}:{self.sender}:{json.dumps(self.content, sort_keys=True, default=str)}"
            self.signature = hashlib.sha256(msg_data.encode()).hexdigest()[:12]

class BlockchainNode:
    """
    Blockchain node with Byzantine fault tolerance
    यह node Bitcoin या Ethereum network के node की तरह काम करता है
    """
    
    def __init__(self, node_id: str, role: NodeRole, is_byzantine: bool = False):
        self.node_id = node_id
        self.role = role
        self.is_byzantine = is_byzantine
        
        # Blockchain state
        self.blockchain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.utxo: Dict[str, Decimal] = {}  # Unspent transaction outputs
        self.mempool: Dict[str, Transaction] = {}  # Transaction pool
        
        # Consensus state
        self.current_round = 0
        self.votes: Dict[int, Dict[str, Any]] = {}  # round -> node -> vote
        self.consensus_type = ConsensusType.PBFT
        
        # Network
        self.network: Dict[str, 'BlockchainNode'] = {}
        self.connected_peers: Set[str] = set()
        
        # Mining/Validation
        self.mining_difficulty = 4
        self.stake_amount = Decimal('1000')  # For PoS
        self.is_mining = False
        
        # Byzantine behavior
        self.malicious_probability = 0.7 if is_byzantine else 0.0
        
        # Performance metrics
        self.blocks_mined = 0
        self.blocks_validated = 0
        self.transactions_processed = 0
        
        # Create genesis block if first node
        if not self.blockchain:
            self.create_genesis_block()
        
        print(f"⛓️ Blockchain node {node_id} ({role.value}) initialized")
        if is_byzantine:
            print(f"💀 WARNING: {node_id} configured as Byzantine node")
    
    def create_genesis_block(self):
        """Create genesis block"""
        genesis_tx = Transaction(
            txn_id="genesis_tx",
            sender="genesis",
            receiver=self.node_id,
            amount=Decimal('1000000'),  # Initial supply
            fee=Decimal('0'),
            timestamp=time.time()
        )
        
        genesis_block = Block(
            block_number=0,
            previous_hash="0" * 64,
            transactions=[genesis_tx],
            timestamp=time.time(),
            miner=self.node_id
        )
        
        self.blockchain.append(genesis_block)
        self.utxo[self.node_id] = Decimal('1000000')
        
        print(f"🎬 Genesis block created by {self.node_id}")
    
    def set_network(self, network: Dict[str, 'BlockchainNode']):
        """Set blockchain network"""
        self.network = network
        self.connected_peers = set(network.keys()) - {self.node_id}
    
    def submit_transaction(self, transaction: Transaction) -> bool:
        """Submit transaction to network"""
        # Validate transaction locally
        if not self.validate_transaction(transaction):
            print(f"❌ Transaction {transaction.txn_id} validation failed")
            return False
        
        # Add to mempool
        self.mempool[transaction.txn_id] = transaction
        
        # Broadcast to network
        self.broadcast_transaction(transaction)
        
        print(f"📤 Transaction {transaction.txn_id} submitted to network")
        return True
    
    def validate_transaction(self, transaction: Transaction) -> bool:
        """Validate transaction"""
        # Check sender balance
        sender_balance = self.utxo.get(transaction.sender, Decimal('0'))
        total_amount = transaction.amount + transaction.fee
        
        if sender_balance < total_amount:
            print(f"❌ Insufficient balance: {sender_balance} < {total_amount}")
            return False
        
        # Check for double spending
        if transaction.txn_id in [tx.txn_id for tx in self.pending_transactions]:
            print(f"❌ Double spending detected: {transaction.txn_id}")
            return False
        
        # Additional validation checks
        if transaction.amount <= 0:
            print(f"❌ Invalid amount: {transaction.amount}")
            return False
        
        return True
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast transaction to all peers"""
        for peer_id in self.connected_peers:
            if peer_id in self.network:
                peer = self.network[peer_id]
                threading.Thread(target=peer.receive_transaction, args=(transaction,)).start()
    
    def receive_transaction(self, transaction: Transaction):
        """Receive transaction from network"""
        if self.validate_transaction(transaction):
            if transaction.txn_id not in self.mempool:
                self.mempool[transaction.txn_id] = transaction
                self.pending_transactions.append(transaction)
                print(f"📥 Node {self.node_id}: Received valid transaction {transaction.txn_id}")
    
    def create_block(self, transactions: List[Transaction]) -> Block:
        """Create new block"""
        previous_block = self.blockchain[-1] if self.blockchain else None
        previous_hash = previous_block.block_hash if previous_block else "0" * 64
        block_number = len(self.blockchain)
        
        # Byzantine behavior: might create invalid block
        if self.is_byzantine and random.random() < self.malicious_probability:
            # Create block with invalid transactions or double spending
            malicious_tx = Transaction(
                txn_id=f"malicious_{int(time.time())}",
                sender="fake_sender",
                receiver=self.node_id,
                amount=Decimal('999999999'),  # Huge amount
                fee=Decimal('0'),
                timestamp=time.time()
            )
            transactions = [malicious_tx] + transactions[:2]  # Limit transactions
            print(f"💀 Byzantine node {self.node_id}: Creating malicious block")
        
        block = Block(
            block_number=block_number,
            previous_hash=previous_hash,
            transactions=transactions,
            timestamp=time.time(),
            miner=self.node_id
        )
        
        return block
    
    def mine_block(self) -> Optional[Block]:
        """Mine new block with PoW"""
        if not self.pending_transactions:
            return None
        
        # Select transactions from mempool
        selected_transactions = self.pending_transactions[:10]  # Block size limit
        
        # Create block
        block = self.create_block(selected_transactions)
        
        # Mine block (Proof of Work)
        if self.role == NodeRole.MINER:
            block.mine_block(self.mining_difficulty)
            self.blocks_mined += 1
            return block
        
        return None
    
    def propose_block(self, block: Block) -> bool:
        """Propose block to network for consensus"""
        print(f"\n🎯 Node {self.node_id}: Proposing block {block.block_number} with {len(block.transactions)} transactions")
        
        # Start consensus round
        self.current_round += 1
        
        # Broadcast block proposal
        proposal_msg = ConsensusMessage(
            msg_type="BLOCK_PROPOSAL",
            sender=self.node_id,
            content={
                "block": block,
                "round": self.current_round
            },
            block_number=block.block_number,
            timestamp=time.time()
        )
        
        self.broadcast_consensus_message(proposal_msg)
        
        # Wait for votes
        time.sleep(2)
        
        # Count votes
        return self.count_block_votes(self.current_round, block)
    
    def broadcast_consensus_message(self, message: ConsensusMessage):
        """Broadcast consensus message"""
        for peer_id in self.connected_peers:
            if peer_id in self.network:
                peer = self.network[peer_id]
                threading.Thread(target=peer.receive_consensus_message, args=(message,)).start()
    
    def receive_consensus_message(self, message: ConsensusMessage):
        """Receive and handle consensus message"""
        if message.msg_type == "BLOCK_PROPOSAL":
            self.handle_block_proposal(message)
        elif message.msg_type == "BLOCK_VOTE":
            self.handle_block_vote(message)
    
    def handle_block_proposal(self, message: ConsensusMessage):
        """Handle block proposal"""
        block = message.content["block"]
        round_number = message.content["round"]
        
        print(f"📨 Node {self.node_id}: Received block proposal {block.block_number} from {message.sender}")
        
        # Validate proposed block
        is_valid = self.validate_block(block)
        
        # Byzantine behavior: might vote randomly
        if self.is_byzantine and random.random() < self.malicious_probability:
            is_valid = random.choice([True, False])
            print(f"💀 Byzantine node {self.node_id}: Random vote for block {block.block_number}")
        
        # Send vote
        vote_msg = ConsensusMessage(
            msg_type="BLOCK_VOTE",
            sender=self.node_id,
            content={
                "block_number": block.block_number,
                "round": round_number,
                "vote": is_valid,
                "reason": "valid" if is_valid else "invalid"
            },
            block_number=block.block_number,
            timestamp=time.time()
        )
        
        # Send vote back to proposer
        if message.sender in self.network:
            proposer = self.network[message.sender]
            threading.Thread(target=proposer.receive_consensus_message, args=(vote_msg,)).start()
        
        print(f"🗳️ Node {self.node_id}: Voted {'APPROVE' if is_valid else 'REJECT'} for block {block.block_number}")
    
    def validate_block(self, block: Block) -> bool:
        """Validate proposed block"""
        # Check block number
        expected_block_number = len(self.blockchain)
        if block.block_number != expected_block_number:
            print(f"❌ Invalid block number: expected {expected_block_number}, got {block.block_number}")
            return False
        
        # Check previous hash
        if self.blockchain:
            expected_previous_hash = self.blockchain[-1].block_hash
            if block.previous_hash != expected_previous_hash:
                print(f"❌ Invalid previous hash")
                return False
        
        # Validate all transactions in block
        for transaction in block.transactions:
            if not self.validate_transaction(transaction):
                print(f"❌ Invalid transaction in block: {transaction.txn_id}")
                return False
        
        # Check proof of work
        target = "0" * self.mining_difficulty
        if not block.block_hash.startswith(target):
            print(f"❌ Invalid proof of work")
            return False
        
        # Check for malicious patterns
        if any(tx.sender == "fake_sender" for tx in block.transactions):
            print(f"❌ Malicious transaction detected")
            return False
        
        return True
    
    def handle_block_vote(self, message: ConsensusMessage):
        """Handle block vote"""
        round_number = message.content["round"]
        vote = message.content["vote"]
        voter = message.sender
        
        if round_number not in self.votes:
            self.votes[round_number] = {}
        
        self.votes[round_number][voter] = {
            "vote": vote,
            "reason": message.content.get("reason", ""),
            "timestamp": message.timestamp
        }
        
        print(f"📊 Node {self.node_id}: Received vote from {voter}: {'APPROVE' if vote else 'REJECT'}")
    
    def count_block_votes(self, round_number: int, block: Block) -> bool:
        """Count votes and decide on block acceptance"""
        if round_number not in self.votes:
            print(f"❌ No votes received for round {round_number}")
            return False
        
        votes = self.votes[round_number]
        approve_votes = sum(1 for vote_info in votes.values() if vote_info["vote"])
        total_votes = len(votes)
        
        # Need Byzantine majority (2f+1 out of 3f+1)
        required_majority = (len(self.connected_peers) // 2) + 1
        
        print(f"\n📊 Block {block.block_number} Consensus Results:")
        print(f"   Approve votes: {approve_votes}")
        print(f"   Total votes: {total_votes}")
        print(f"   Required majority: {required_majority}")
        
        if approve_votes >= required_majority:
            print(f"✅ Block {block.block_number} ACCEPTED by network consensus")
            self.add_block_to_chain(block)
            return True
        else:
            print(f"❌ Block {block.block_number} REJECTED by network consensus")
            return False
    
    def add_block_to_chain(self, block: Block):
        """Add accepted block to blockchain"""
        # Add block to chain
        self.blockchain.append(block)
        
        # Update UTXO set
        for transaction in block.transactions:
            # Debit sender
            if transaction.sender in self.utxo:
                self.utxo[transaction.sender] -= (transaction.amount + transaction.fee)
            
            # Credit receiver
            if transaction.receiver not in self.utxo:
                self.utxo[transaction.receiver] = Decimal('0')
            self.utxo[transaction.receiver] += transaction.amount
            
            # Remove from mempool and pending
            if transaction.txn_id in self.mempool:
                del self.mempool[transaction.txn_id]
            
            if transaction in self.pending_transactions:
                self.pending_transactions.remove(transaction)
        
        self.transactions_processed += len(block.transactions)
        self.blocks_validated += 1
        
        print(f"⛓️ Block {block.block_number} added to blockchain")
        print(f"   Transactions: {len(block.transactions)}")
        print(f"   Block hash: {block.block_hash[:16]}...")
    
    def get_balance(self, address: str) -> Decimal:
        """Get balance for address"""
        return self.utxo.get(address, Decimal('0'))
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information"""
        return {
            "node_id": self.node_id,
            "role": self.role.value,
            "is_byzantine": self.is_byzantine,
            "blockchain_length": len(self.blockchain),
            "pending_transactions": len(self.pending_transactions),
            "mempool_size": len(self.mempool),
            "blocks_mined": self.blocks_mined,
            "blocks_validated": self.blocks_validated,
            "transactions_processed": self.transactions_processed,
            "connected_peers": len(self.connected_peers)
        }

def simulate_cryptocurrency_network():
    """
    Simulate cryptocurrency network with Byzantine consensus
    यह simulation Bitcoin/Ethereum style network को demonstrate करता है
    """
    print("🇮🇳 Cryptocurrency Network - Byzantine Consensus Simulation")
    print("₿ Scenario: Decentralized digital currency with fault tolerance")
    print("=" * 70)
    
    # Create cryptocurrency network
    crypto_nodes = {
        "miner_delhi": BlockchainNode("miner_delhi", NodeRole.MINER),
        "miner_mumbai": BlockchainNode("miner_mumbai", NodeRole.MINER),
        "validator_bangalore": BlockchainNode("validator_bangalore", NodeRole.VALIDATOR),
        "validator_chennai": BlockchainNode("validator_chennai", NodeRole.VALIDATOR),
        "malicious_node": BlockchainNode("malicious_node", NodeRole.MINER, is_byzantine=True),
        "full_node_pune": BlockchainNode("full_node_pune", NodeRole.FULL_NODE)
    }
    
    # Set network connections
    for node in crypto_nodes.values():
        node.set_network(crypto_nodes)
    
    print(f"\n⛓️ Cryptocurrency Network ({len(crypto_nodes)} nodes):")
    for node_id, node in crypto_nodes.items():
        role_status = f"{node.role.value}"
        byzantine_status = " (BYZANTINE)" if node.is_byzantine else " (HONEST)"
        print(f"   {node_id}: {role_status}{byzantine_status}")
    
    # Create initial balances by distributing from genesis
    print(f"\n💰 Distributing initial balances...")
    
    genesis_node = crypto_nodes["miner_delhi"]
    initial_distributions = [
        Transaction(
            txn_id="init_001",
            sender="miner_delhi",
            receiver="user_rahul",
            amount=Decimal('100'),
            fee=Decimal('1'),
            timestamp=time.time()
        ),
        Transaction(
            txn_id="init_002", 
            sender="miner_delhi",
            receiver="user_priya",
            amount=Decimal('150'),
            fee=Decimal('1'),
            timestamp=time.time()
        ),
        Transaction(
            txn_id="init_003",
            sender="miner_delhi", 
            receiver="user_amit",
            amount=Decimal('200'),
            fee=Decimal('1'),
            timestamp=time.time()
        )
    ]
    
    # Submit initial transactions
    for tx in initial_distributions:
        success = genesis_node.submit_transaction(tx)
        if success:
            print(f"   ✅ Distributed ₹{tx.amount} to {tx.receiver}")
        time.sleep(0.2)
    
    time.sleep(1)  # Wait for propagation
    
    # Mine first block with initial distributions
    print(f"\n⛏️ Mining genesis distribution block...")
    
    block_1 = genesis_node.mine_block()
    if block_1:
        success = genesis_node.propose_block(block_1)
        if success:
            print(f"✅ Genesis distribution block accepted by network")
        else:
            print(f"❌ Genesis distribution block rejected")
    
    time.sleep(2)
    
    # Create user transactions
    print(f"\n💸 Creating user transactions...")
    
    user_transactions = [
        Transaction(
            txn_id="user_001",
            sender="user_rahul",
            receiver="user_priya", 
            amount=Decimal('25'),
            fee=Decimal('2'),
            timestamp=time.time()
        ),
        Transaction(
            txn_id="user_002",
            sender="user_priya",
            receiver="user_amit",
            amount=Decimal('40'),
            fee=Decimal('2'), 
            timestamp=time.time()
        ),
        Transaction(
            txn_id="user_003",
            sender="user_amit",
            receiver="user_rahul",
            amount=Decimal('15'),
            fee=Decimal('1'),
            timestamp=time.time()
        )
    ]
    
    # Submit user transactions through different nodes
    nodes_list = list(crypto_nodes.values())
    for i, tx in enumerate(user_transactions):
        submitting_node = nodes_list[i % len(nodes_list)]
        success = submitting_node.submit_transaction(tx)
        if success:
            print(f"   📤 {tx.sender} → {tx.receiver}: ₹{tx.amount} (via {submitting_node.node_id})")
        time.sleep(0.3)
    
    time.sleep(2)
    
    # Different miners compete to mine next block
    print(f"\n⛏️ Mining competition for block 2...")
    
    mining_nodes = [node for node in crypto_nodes.values() if node.role == NodeRole.MINER]
    mining_results = []
    
    # Start mining race
    def mine_block_async(node):
        block = node.mine_block()
        if block:
            mining_results.append((node, block))
    
    threads = []
    for miner in mining_nodes:
        thread = threading.Thread(target=mine_block_async, args=(miner,))
        threads.append(thread)
        thread.start()
    
    # Wait for first successful mine
    for thread in threads:
        thread.join()
    
    # First miner to complete gets to propose
    if mining_results:
        winning_miner, winning_block = mining_results[0]
        print(f"🏆 {winning_miner.node_id} won mining race!")
        
        success = winning_miner.propose_block(winning_block)
        if success:
            print(f"✅ Block 2 accepted by network consensus")
        else:
            print(f"❌ Block 2 rejected by network consensus")
    
    time.sleep(2)
    
    # Show final network state
    print(f"\n📊 Final Network State:")
    print("=" * 50)
    
    for node_id, node in crypto_nodes.items():
        info = node.get_blockchain_info()
        
        print(f"\n🖥️ {node_id} ({info['role']})")
        print(f"   Byzantine: {info['is_byzantine']}")
        print(f"   Blockchain length: {info['blockchain_length']}")
        print(f"   Blocks mined: {info['blocks_mined']}")
        print(f"   Transactions processed: {info['transactions_processed']}")
        print(f"   Pending transactions: {info['pending_transactions']}")
        
        # Show user balances from this node's perspective
        print(f"   User balances:")
        users = ["user_rahul", "user_priya", "user_amit"]
        for user in users:
            balance = node.get_balance(user)
            print(f"     {user}: ₹{balance}")
    
    # Verify blockchain consistency
    print(f"\n🔍 Blockchain Consistency Check:")
    reference_chain = crypto_nodes["miner_delhi"].blockchain
    consistent = True
    
    for node_id, node in crypto_nodes.items():
        if node.is_byzantine:
            continue  # Skip Byzantine nodes
            
        if len(node.blockchain) != len(reference_chain):
            print(f"   ❌ {node_id}: Chain length mismatch")
            consistent = False
        else:
            chain_match = all(
                node.blockchain[i].block_hash == reference_chain[i].block_hash
                for i in range(len(reference_chain))
            )
            if chain_match:
                print(f"   ✅ {node_id}: Blockchain consistent")
            else:
                print(f"   ❌ {node_id}: Blockchain inconsistent")
                consistent = False
    
    if consistent:
        print(f"\n🎉 Network achieved Byzantine fault tolerance!")
        print(f"🛡️ System remained secure despite {sum(1 for n in crypto_nodes.values() if n.is_byzantine)} Byzantine node(s)")
    else:
        print(f"\n⚠️ Blockchain inconsistency detected")

def simulate_enterprise_blockchain():
    """
    Simulate enterprise blockchain with permissioned consensus
    यह example Hyperledger Fabric style enterprise blockchain को demonstrate करता है
    """
    print("\n" + "="*70)
    print("🇮🇳 Enterprise Blockchain - Supply Chain Consensus")
    print("=" * 70)
    
    # Create enterprise consortium
    enterprise_nodes = {
        "supplier_tata": BlockchainNode("supplier_tata", NodeRole.VALIDATOR),
        "manufacturer_mahindra": BlockchainNode("manufacturer_mahindra", NodeRole.VALIDATOR),
        "distributor_reliance": BlockchainNode("distributor_reliance", NodeRole.VALIDATOR),
        "retailer_bigbasket": BlockchainNode("retailer_bigbasket", NodeRole.FULL_NODE),
        "auditor_kpmg": BlockchainNode("auditor_kpmg", NodeRole.FULL_NODE, is_byzantine=True)
    }
    
    for node in enterprise_nodes.values():
        node.set_network(enterprise_nodes)
        node.consensus_type = ConsensusType.PBFT  # Enterprise uses PBFT
        node.mining_difficulty = 2  # Lower difficulty for faster consensus
    
    print(f"\n🏭 Enterprise Consortium:")
    for node_id, node in enterprise_nodes.items():
        print(f"   {node_id}: {node.role.value}")
    
    # Supply chain transactions
    supply_chain_txns = [
        Transaction(
            txn_id="supply_001",
            sender="supplier_tata",
            receiver="manufacturer_mahindra",
            amount=Decimal('50000'),  # Raw materials
            fee=Decimal('100'),
            timestamp=time.time()
        ),
        Transaction(
            txn_id="supply_002",
            sender="manufacturer_mahindra", 
            receiver="distributor_reliance",
            amount=Decimal('75000'),  # Finished goods
            fee=Decimal('150'),
            timestamp=time.time()
        ),
        Transaction(
            txn_id="supply_003",
            sender="distributor_reliance",
            receiver="retailer_bigbasket",
            amount=Decimal('80000'),  # Retail distribution
            fee=Decimal('200'),
            timestamp=time.time()
        )
    ]
    
    print(f"\n📦 Processing supply chain transactions...")
    
    # Submit transactions
    tata_node = enterprise_nodes["supplier_tata"]
    for tx in supply_chain_txns:
        success = tata_node.submit_transaction(tx)
        if success:
            print(f"   ✅ Supply chain transaction: {tx.sender} → {tx.receiver} (₹{tx.amount})")
        time.sleep(0.5)
    
    time.sleep(2)
    
    # Mine and propose supply chain block
    supply_block = tata_node.mine_block()
    if supply_block:
        success = tata_node.propose_block(supply_block)
        if success:
            print(f"✅ Supply chain block accepted by consortium")
        else:
            print(f"❌ Supply chain block rejected")
    
    # Show final supply chain state
    print(f"\n📋 Final Supply Chain State:")
    for node_id, node in enterprise_nodes.items():
        if not node.is_byzantine:  # Only show honest nodes
            print(f"\n   {node_id}:")
            print(f"     Blockchain length: {len(node.blockchain)}")
            print(f"     Transactions processed: {node.transactions_processed}")

if __name__ == "__main__":
    # Run cryptocurrency network simulation
    simulate_cryptocurrency_network()
    
    # Run enterprise blockchain simulation
    simulate_enterprise_blockchain()
    
    print("\n" + "="*70)
    print("🇮🇳 Blockchain Byzantine Consensus Benefits:")
    print("1. Prevents double-spending attacks")
    print("2. Maintains network integrity despite malicious nodes")
    print("3. Enables trustless peer-to-peer transactions")
    print("4. Provides immutable transaction history")
    print("5. Supports decentralized governance")
    print("6. Enables smart contract execution")
    print("7. Provides cryptographic proof of consensus")