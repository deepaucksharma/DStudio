#!/usr/bin/env python3
"""
Byzantine Fault Tolerance (BFT) Implementation
Byzantine fault tolerance - जैसे कि UPI transactions में security के लिए use होता है

यह example दिखाता है कि कैसे Byzantine fault tolerance work करती है
distributed financial systems में। Indian payment companies जैसे PhonePe, 
GPay, Paytm इसे use करती हैं to ensure transaction integrity even when
some nodes are malicious or compromised.

Production context: UPI processes 12+ billion transactions monthly with BFT consensus
Scale: Ensures financial integrity across hundreds of bank nodes
Challenge: Preventing double spending and fraud while maintaining high availability
"""

import hashlib
import json
import random
import time
import threading
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import copy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeType(Enum):
    """Types of nodes in the BFT system"""
    HONEST = "honest"
    FAULTY = "faulty"
    MALICIOUS = "malicious"

class MessageType(Enum):
    """Types of BFT messages"""
    REQUEST = "request"
    PREPARE = "prepare"
    COMMIT = "commit"
    REPLY = "reply"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"

class TransactionStatus(Enum):
    """Transaction processing status"""
    PENDING = "pending"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"

@dataclass
class UPITransaction:
    """Represents a UPI transaction"""
    transaction_id: str
    sender_vpa: str
    receiver_vpa: str
    amount: float
    timestamp: float
    bank_sender: str
    bank_receiver: str
    description: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "sender_vpa": self.sender_vpa,
            "receiver_vpa": self.receiver_vpa,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "bank_sender": self.bank_sender,
            "bank_receiver": self.bank_receiver,
            "description": self.description,
            "status": self.status.value
        }
    
    def get_hash(self) -> str:
        """Get transaction hash for integrity verification"""
        content = f"{self.transaction_id}{self.sender_vpa}{self.receiver_vpa}{self.amount}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass
class BFTMessage:
    """Represents a message in the BFT protocol"""
    message_type: MessageType
    view_number: int
    sequence_number: int
    sender_id: str
    transaction: Optional[UPITransaction]
    digest: str
    timestamp: float
    signature: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_type": self.message_type.value,
            "view_number": self.view_number,
            "sequence_number": self.sequence_number,
            "sender_id": self.sender_id,
            "transaction": self.transaction.to_dict() if self.transaction else None,
            "digest": self.digest,
            "timestamp": self.timestamp,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BFTMessage':
        transaction = None
        if data.get("transaction"):
            tx_data = data["transaction"]
            transaction = UPITransaction(
                transaction_id=tx_data["transaction_id"],
                sender_vpa=tx_data["sender_vpa"],
                receiver_vpa=tx_data["receiver_vpa"],
                amount=tx_data["amount"],
                timestamp=tx_data["timestamp"],
                bank_sender=tx_data["bank_sender"],
                bank_receiver=tx_data["bank_receiver"],
                description=tx_data.get("description", ""),
                status=TransactionStatus(tx_data["status"])
            )
        
        return cls(
            message_type=MessageType(data["message_type"]),
            view_number=data["view_number"],
            sequence_number=data["sequence_number"],
            sender_id=data["sender_id"],
            transaction=transaction,
            digest=data["digest"],
            timestamp=data["timestamp"],
            signature=data.get("signature", "")
        )

class UPIBankNode:
    """
    UPI Bank Node with Byzantine Fault Tolerance
    हर node एक bank का UPI server है जो transactions को securely process करता है
    """
    
    def __init__(self, node_id: str, bank_name: str, node_type: NodeType = NodeType.HONEST):
        self.node_id = node_id
        self.bank_name = bank_name
        self.node_type = node_type
        
        # BFT Protocol state
        self.view_number = 0
        self.sequence_number = 0
        self.is_primary = False
        
        # Transaction processing
        self.pending_transactions: Dict[str, UPITransaction] = {}
        self.prepared_transactions: Dict[str, UPITransaction] = {}
        self.committed_transactions: Dict[str, UPITransaction] = {}
        self.transaction_log: List[UPITransaction] = []
        
        # Account balances (simplified)
        self.account_balances: Dict[str, float] = {}
        
        # Message handling
        self.received_messages: Dict[str, BFTMessage] = {}
        self.prepare_messages: Dict[str, List[BFTMessage]] = defaultdict(list)
        self.commit_messages: Dict[str, List[BFTMessage]] = defaultdict(list)
        
        # Cluster configuration
        self.cluster_nodes: Set[str] = set()
        self.faulty_threshold = 0  # Will be set when cluster is configured
        
        # Threading and state
        self.lock = threading.RLock()
        self.is_running = False
        self.message_queue: List[BFTMessage] = []
        
        # Statistics
        self.stats = {
            "transactions_processed": 0,
            "transactions_committed": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "view_changes": 0,
            "byzantine_attacks_detected": 0
        }
        
        # Initialize sample accounts
        self._initialize_sample_accounts()
        
        logger.info(f"UPI Bank Node {node_id} ({bank_name}) initialized as {node_type.value}")
    
    def _initialize_sample_accounts(self) -> None:
        """Initialize sample UPI accounts with balances"""
        sample_accounts = [
            "rahul@icici", "priya@hdfc", "arjun@sbi", "sneha@axis",
            "amit@kotak", "deepika@pnb", "vikash@bob", "kiran@canara"
        ]
        
        for vpa in sample_accounts:
            # Random initial balance between 10K to 1L
            self.account_balances[vpa] = random.uniform(10000, 100000)
    
    def configure_cluster(self, cluster_nodes: Set[str]) -> None:
        """Configure the BFT cluster"""
        self.cluster_nodes = cluster_nodes.copy()
        self.faulty_threshold = (len(cluster_nodes) - 1) // 3  # f = (n-1)/3
        
        # Determine if this node is primary (simplified: first node alphabetically)
        sorted_nodes = sorted(cluster_nodes)
        self.is_primary = (self.node_id == sorted_nodes[0])
        
        logger.info(f"Node {self.node_id} configured for cluster of {len(cluster_nodes)} nodes, "
                   f"fault threshold: {self.faulty_threshold}, primary: {self.is_primary}")
    
    def start(self) -> None:
        """Start the BFT node"""
        with self.lock:
            if self.is_running:
                return
            
            self.is_running = True
            
            # Start message processing thread
            threading.Thread(target=self._message_processing_loop, daemon=True).start()
            
            logger.info(f"UPI Bank Node {self.node_id} started")
    
    def stop(self) -> None:
        """Stop the BFT node"""
        with self.lock:
            self.is_running = False
            logger.info(f"UPI Bank Node {self.node_id} stopped")
    
    def submit_transaction(self, transaction: UPITransaction) -> bool:
        """Submit a UPI transaction for processing"""
        if not self.is_primary:
            logger.warning(f"Node {self.node_id} is not primary, cannot submit transaction")
            return False
        
        with self.lock:
            # Validate transaction
            if not self._validate_transaction(transaction):
                logger.error(f"Transaction validation failed: {transaction.transaction_id}")
                return False
            
            # Add to pending transactions
            self.pending_transactions[transaction.transaction_id] = transaction
            
            # Create and broadcast prepare message
            self.sequence_number += 1
            
            prepare_message = BFTMessage(
                message_type=MessageType.PREPARE,
                view_number=self.view_number,
                sequence_number=self.sequence_number,
                sender_id=self.node_id,
                transaction=transaction,
                digest=transaction.get_hash(),
                timestamp=time.time()
            )
            
            self._broadcast_message(prepare_message)
            
            logger.info(f"Primary {self.node_id} initiated transaction: {transaction.transaction_id}")
            return True
    
    def _validate_transaction(self, transaction: UPITransaction) -> bool:
        """Validate UPI transaction"""
        # Check if sender has sufficient balance
        sender_balance = self.account_balances.get(transaction.sender_vpa, 0)
        
        if sender_balance < transaction.amount:
            logger.warning(f"Insufficient balance for {transaction.sender_vpa}: "
                          f"has {sender_balance}, needs {transaction.amount}")
            return False
        
        # Check amount is positive
        if transaction.amount <= 0:
            logger.warning(f"Invalid amount: {transaction.amount}")
            return False
        
        # Check if transaction already exists
        if transaction.transaction_id in self.committed_transactions:
            logger.warning(f"Duplicate transaction: {transaction.transaction_id}")
            return False
        
        return True
    
    def receive_message(self, message: BFTMessage) -> None:
        """Receive and queue a BFT message"""
        with self.lock:
            self.message_queue.append(message)
            self.stats["messages_received"] += 1
    
    def _message_processing_loop(self) -> None:
        """Main message processing loop"""
        while self.is_running:
            try:
                with self.lock:
                    if not self.message_queue:
                        time.sleep(0.1)
                        continue
                    
                    message = self.message_queue.pop(0)
                
                self._process_message(message)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def _process_message(self, message: BFTMessage) -> None:
        """Process a BFT message based on its type"""
        # Byzantine behavior simulation
        if self.node_type == NodeType.MALICIOUS and random.random() < 0.3:
            self._simulate_byzantine_behavior(message)
            return
        
        if self.node_type == NodeType.FAULTY and random.random() < 0.1:
            # Faulty node might drop messages
            logger.debug(f"Faulty node {self.node_id} dropped message")
            return
        
        if message.message_type == MessageType.PREPARE:
            self._handle_prepare_message(message)
        elif message.message_type == MessageType.COMMIT:
            self._handle_commit_message(message)
        elif message.message_type == MessageType.REPLY:
            self._handle_reply_message(message)
    
    def _handle_prepare_message(self, message: BFTMessage) -> None:
        """Handle prepare message (Phase 1 of BFT)"""
        transaction_id = message.transaction.transaction_id if message.transaction else "unknown"
        
        logger.debug(f"Node {self.node_id} received PREPARE for transaction {transaction_id}")
        
        # Validate message
        if not self._validate_prepare_message(message):
            logger.warning(f"Invalid PREPARE message for transaction {transaction_id}")
            return
        
        # Store prepare message
        self.prepare_messages[transaction_id].append(message)
        
        # Check if we have enough prepare messages (2f+1)
        required_prepares = 2 * self.faulty_threshold + 1
        
        if len(self.prepare_messages[transaction_id]) >= required_prepares:
            # Move to prepared state and send commit
            if message.transaction:
                self.prepared_transactions[transaction_id] = message.transaction
                message.transaction.status = TransactionStatus.PREPARED
            
            # Send commit message
            commit_message = BFTMessage(
                message_type=MessageType.COMMIT,
                view_number=self.view_number,
                sequence_number=message.sequence_number,
                sender_id=self.node_id,
                transaction=message.transaction,
                digest=message.digest,
                timestamp=time.time()
            )
            
            self._broadcast_message(commit_message)
            
            logger.info(f"Node {self.node_id} prepared transaction {transaction_id}")
    
    def _handle_commit_message(self, message: BFTMessage) -> None:
        """Handle commit message (Phase 2 of BFT)"""
        transaction_id = message.transaction.transaction_id if message.transaction else "unknown"
        
        logger.debug(f"Node {self.node_id} received COMMIT for transaction {transaction_id}")
        
        # Store commit message
        self.commit_messages[transaction_id].append(message)
        
        # Check if we have enough commit messages (2f+1)
        required_commits = 2 * self.faulty_threshold + 1
        
        if len(self.commit_messages[transaction_id]) >= required_commits:
            # Execute transaction
            if message.transaction:
                success = self._execute_transaction(message.transaction)
                
                if success:
                    self.committed_transactions[transaction_id] = message.transaction
                    self.transaction_log.append(message.transaction)
                    message.transaction.status = TransactionStatus.COMMITTED
                    
                    # Clean up pending and prepared
                    self.pending_transactions.pop(transaction_id, None)
                    self.prepared_transactions.pop(transaction_id, None)
                    
                    self.stats["transactions_committed"] += 1
                    
                    logger.info(f"Node {self.node_id} committed transaction {transaction_id}")
                else:
                    logger.error(f"Failed to execute transaction {transaction_id}")
    
    def _execute_transaction(self, transaction: UPITransaction) -> bool:
        """Execute the UPI transaction (update balances)"""
        try:
            # Check balances again (double-check)
            sender_balance = self.account_balances.get(transaction.sender_vpa, 0)
            
            if sender_balance < transaction.amount:
                logger.error(f"Insufficient balance during execution: {transaction.sender_vpa}")
                return False
            
            # Perform the transfer
            self.account_balances[transaction.sender_vpa] -= transaction.amount
            
            if transaction.receiver_vpa not in self.account_balances:
                self.account_balances[transaction.receiver_vpa] = 0
            
            self.account_balances[transaction.receiver_vpa] += transaction.amount
            
            logger.info(f"Transaction executed: {transaction.amount} from "
                       f"{transaction.sender_vpa} to {transaction.receiver_vpa}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return False
    
    def _validate_prepare_message(self, message: BFTMessage) -> bool:
        """Validate a prepare message"""
        if not message.transaction:
            return False
        
        # Check digest
        expected_digest = message.transaction.get_hash()
        if message.digest != expected_digest:
            logger.warning(f"Digest mismatch in prepare message")
            return False
        
        # Check sequence number
        if message.sequence_number <= 0:
            return False
        
        return True
    
    def _broadcast_message(self, message: BFTMessage) -> None:
        """Broadcast message to all nodes in the cluster"""
        # In a real implementation, this would send over network
        # For simulation, we'll use a global message dispatcher
        
        self.stats["messages_sent"] += 1
        
        # Simulate network delay
        time.sleep(random.uniform(0.01, 0.05))
        
        logger.debug(f"Node {self.node_id} broadcasting {message.message_type.value} message")
    
    def _simulate_byzantine_behavior(self, message: BFTMessage) -> None:
        """Simulate various Byzantine (malicious) behaviors"""
        behavior_type = random.choice([
            "message_corruption", "double_spending", "wrong_signature", 
            "replay_attack", "timing_attack"
        ])
        
        self.stats["byzantine_attacks_detected"] += 1
        
        if behavior_type == "message_corruption":
            # Corrupt the message digest
            logger.warning(f"Byzantine node {self.node_id} corrupting message digest")
            if message.transaction:
                message.digest = "corrupted_" + message.digest
        
        elif behavior_type == "double_spending":
            # Try to spend the same money twice
            logger.warning(f"Byzantine node {self.node_id} attempting double spending")
            if message.transaction:
                # Create a conflicting transaction
                conflicting_tx = copy.deepcopy(message.transaction)
                conflicting_tx.transaction_id = "fake_" + conflicting_tx.transaction_id
                conflicting_tx.receiver_vpa = "attacker@evil"
        
        elif behavior_type == "wrong_signature":
            # Provide wrong signature
            logger.warning(f"Byzantine node {self.node_id} providing wrong signature")
            message.signature = "fake_signature_" + str(random.randint(1000, 9999))
        
        elif behavior_type == "replay_attack":
            # Try to replay old messages
            logger.warning(f"Byzantine node {self.node_id} attempting replay attack")
            message.timestamp = time.time() - 3600  # 1 hour old
        
        elif behavior_type == "timing_attack":
            # Delay messages to disrupt timing
            logger.warning(f"Byzantine node {self.node_id} performing timing attack")
            time.sleep(random.uniform(1, 3))
    
    def _handle_reply_message(self, message: BFTMessage) -> None:
        """Handle reply message from nodes"""
        # Implementation for client responses
        pass
    
    def get_account_balance(self, vpa: str) -> float:
        """Get account balance for a VPA"""
        with self.lock:
            return self.account_balances.get(vpa, 0.0)
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get node statistics"""
        with self.lock:
            return {
                "node_id": self.node_id,
                "bank_name": self.bank_name,
                "node_type": self.node_type.value,
                "is_primary": self.is_primary,
                "view_number": self.view_number,
                "sequence_number": self.sequence_number,
                "pending_transactions": len(self.pending_transactions),
                "prepared_transactions": len(self.prepared_transactions),
                "committed_transactions": len(self.committed_transactions),
                "total_accounts": len(self.account_balances),
                "stats": self.stats.copy()
            }

class UPIBFTCluster:
    """
    UPI Byzantine Fault Tolerant Cluster
    Multiple bank nodes working together to process UPI transactions securely
    """
    
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.nodes: Dict[str, UPIBankNode] = {}
        self.message_dispatcher = MessageDispatcher()
        
        logger.info(f"UPI BFT Cluster '{cluster_name}' initialized")
    
    def add_node(self, node: UPIBankNode) -> None:
        """Add a node to the cluster"""
        self.nodes[node.node_id] = node
        self.message_dispatcher.add_node(node)
        
        # Reconfigure all nodes with updated cluster membership
        node_ids = set(self.nodes.keys())
        for existing_node in self.nodes.values():
            existing_node.configure_cluster(node_ids)
        
        logger.info(f"Added node {node.node_id} to cluster '{self.cluster_name}'")
    
    def start_cluster(self) -> None:
        """Start all nodes in the cluster"""
        for node in self.nodes.values():
            node.start()
        
        self.message_dispatcher.start()
        
        logger.info(f"Started UPI BFT cluster '{self.cluster_name}' with {len(self.nodes)} nodes")
    
    def stop_cluster(self) -> None:
        """Stop all nodes in the cluster"""
        for node in self.nodes.values():
            node.stop()
        
        self.message_dispatcher.stop()
        
        logger.info(f"Stopped UPI BFT cluster '{self.cluster_name}'")
    
    def submit_transaction(self, transaction: UPITransaction) -> bool:
        """Submit transaction to the primary node"""
        primary_node = self._get_primary_node()
        
        if primary_node:
            return primary_node.submit_transaction(transaction)
        else:
            logger.error("No primary node found")
            return False
    
    def _get_primary_node(self) -> Optional[UPIBankNode]:
        """Get the current primary node"""
        for node in self.nodes.values():
            if node.is_primary:
                return node
        return None
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get cluster-wide statistics"""
        total_committed = sum(node.stats["transactions_committed"] for node in self.nodes.values())
        total_messages = sum(node.stats["messages_sent"] + node.stats["messages_received"] 
                           for node in self.nodes.values())
        
        byzantine_attacks = sum(node.stats["byzantine_attacks_detected"] for node in self.nodes.values())
        
        node_types = Counter(node.node_type.value for node in self.nodes.values())
        
        return {
            "cluster_name": self.cluster_name,
            "total_nodes": len(self.nodes),
            "node_types": dict(node_types),
            "total_committed_transactions": total_committed,
            "total_messages": total_messages,
            "byzantine_attacks_detected": byzantine_attacks,
            "fault_tolerance": (len(self.nodes) - 1) // 3
        }

class MessageDispatcher:
    """
    Simulates network message passing between nodes
    """
    
    def __init__(self):
        self.nodes: Dict[str, UPIBankNode] = {}
        self.is_running = False
        self.message_queue: List[Tuple[str, BFTMessage]] = []
        self.lock = threading.Lock()
    
    def add_node(self, node: UPIBankNode) -> None:
        """Add a node to the dispatcher"""
        self.nodes[node.node_id] = node
        
        # Override the node's broadcast method to use our dispatcher
        original_broadcast = node._broadcast_message
        
        def patched_broadcast(message: BFTMessage):
            original_broadcast(message)
            self.dispatch_message(node.node_id, message)
        
        node._broadcast_message = patched_broadcast
    
    def start(self) -> None:
        """Start the message dispatcher"""
        self.is_running = True
        threading.Thread(target=self._dispatch_loop, daemon=True).start()
    
    def stop(self) -> None:
        """Stop the message dispatcher"""
        self.is_running = False
    
    def dispatch_message(self, sender_id: str, message: BFTMessage) -> None:
        """Dispatch a message from sender to all other nodes"""
        with self.lock:
            for node_id, node in self.nodes.items():
                if node_id != sender_id:
                    self.message_queue.append((node_id, message))
    
    def _dispatch_loop(self) -> None:
        """Main dispatch loop"""
        while self.is_running:
            try:
                with self.lock:
                    if not self.message_queue:
                        time.sleep(0.01)
                        continue
                    
                    node_id, message = self.message_queue.pop(0)
                
                # Simulate network delay
                time.sleep(random.uniform(0.01, 0.1))
                
                # Simulate message loss (5% chance)
                if random.random() > 0.05:
                    if node_id in self.nodes:
                        self.nodes[node_id].receive_message(message)
                
            except Exception as e:
                logger.error(f"Error in message dispatch: {e}")

def demonstrate_upi_byzantine_fault_tolerance():
    """
    Demonstrate Byzantine Fault Tolerance in UPI systems
    """
    print("\n💳 UPI Byzantine Fault Tolerance Demo")
    print("=" * 50)
    
    # Create UPI BFT cluster
    cluster = UPIBFTCluster("UPI-India-Cluster")
    
    # Create bank nodes with different types
    print("\n🏦 Setting up UPI bank nodes...")
    
    # Honest nodes (majority)
    honest_nodes = [
        UPIBankNode("sbi-node-01", "State Bank of India", NodeType.HONEST),
        UPIBankNode("hdfc-node-01", "HDFC Bank", NodeType.HONEST),
        UPIBankNode("icici-node-01", "ICICI Bank", NodeType.HONEST),
        UPIBankNode("axis-node-01", "Axis Bank", NodeType.HONEST),
    ]
    
    # Faulty node (hardware/network issues)
    faulty_nodes = [
        UPIBankNode("pnb-node-01", "Punjab National Bank", NodeType.FAULTY),
    ]
    
    # Malicious node (compromised)
    malicious_nodes = [
        UPIBankNode("fake-node-01", "Malicious Bank", NodeType.MALICIOUS),
    ]
    
    all_nodes = honest_nodes + faulty_nodes + malicious_nodes
    
    # Add nodes to cluster
    for node in all_nodes:
        cluster.add_node(node)
        print(f"✅ Added {node.bank_name} ({node.node_type.value}): {node.node_id}")
    
    # Start cluster
    cluster.start_cluster()
    
    # Show initial cluster configuration
    cluster_stats = cluster.get_cluster_stats()
    print(f"\n📊 Cluster Configuration:")
    print(f"Total nodes: {cluster_stats['total_nodes']}")
    print(f"Node types: {cluster_stats['node_types']}")
    print(f"Byzantine fault tolerance: can handle {cluster_stats['fault_tolerance']} faulty nodes")
    
    # Display account balances
    print(f"\n💰 Initial Account Balances:")
    primary_node = cluster._get_primary_node()
    if primary_node:
        for vpa, balance in list(primary_node.account_balances.items())[:5]:
            print(f"  {vpa}: ₹{balance:,.2f}")
    
    # Process UPI transactions
    print(f"\n💸 Processing UPI transactions through BFT consensus...")
    
    transactions = [
        UPITransaction(
            transaction_id="UPI001",
            sender_vpa="rahul@icici",
            receiver_vpa="priya@hdfc",
            amount=5000.0,
            timestamp=time.time(),
            bank_sender="ICICI",
            bank_receiver="HDFC",
            description="Rent payment"
        ),
        UPITransaction(
            transaction_id="UPI002",
            sender_vpa="arjun@sbi",
            receiver_vpa="sneha@axis",
            amount=1500.0,
            timestamp=time.time(),
            bank_sender="SBI",
            bank_receiver="AXIS",
            description="Food bill split"
        ),
        UPITransaction(
            transaction_id="UPI003",
            sender_vpa="amit@kotak",
            receiver_vpa="deepika@pnb",
            amount=25000.0,
            timestamp=time.time(),
            bank_sender="KOTAK",
            bank_receiver="PNB",
            description="Loan repayment"
        ),
        UPITransaction(
            transaction_id="UPI004",
            sender_vpa="vikash@bob",
            receiver_vpa="kiran@canara",
            amount=800.0,
            timestamp=time.time(),
            bank_sender="BOB",
            bank_receiver="CANARA",
            description="Book purchase"
        ),
    ]
    
    # Submit transactions
    for transaction in transactions:
        print(f"\n💳 Submitting transaction {transaction.transaction_id}:")
        print(f"   {transaction.sender_vpa} → {transaction.receiver_vpa}: ₹{transaction.amount}")
        print(f"   Description: {transaction.description}")
        
        success = cluster.submit_transaction(transaction)
        if success:
            print(f"   ✅ Transaction submitted to BFT consensus")
        else:
            print(f"   ❌ Transaction submission failed")
        
        # Allow time for BFT consensus
        time.sleep(3)
    
    # Allow final processing
    print(f"\n⏳ Allowing BFT consensus to complete...")
    time.sleep(5)
    
    # Show node statistics
    print(f"\n📈 Node Statistics After Processing:")
    for node in all_nodes:
        stats = node.get_node_stats()
        status_emoji = {
            "honest": "✅",
            "faulty": "⚠️",
            "malicious": "🚨"
        }[stats["node_type"]]
        
        print(f"\n{status_emoji} {stats['bank_name']} ({stats['node_id']}):")
        print(f"   Type: {stats['node_type']}")
        print(f"   Primary: {stats['is_primary']}")
        print(f"   Committed transactions: {stats['committed_transactions']}")
        print(f"   Messages sent: {stats['stats']['messages_sent']}")
        print(f"   Messages received: {stats['stats']['messages_received']}")
        if stats['stats']['byzantine_attacks_detected'] > 0:
            print(f"   🚨 Byzantine attacks detected: {stats['stats']['byzantine_attacks_detected']}")
    
    # Check final balances
    print(f"\n💰 Final Account Balances (from primary node):")
    if primary_node:
        for vpa, balance in list(primary_node.account_balances.items())[:8]:
            print(f"  {vpa}: ₹{balance:,.2f}")
    
    # Show transaction log
    print(f"\n📜 Committed Transaction Log:")
    if primary_node:
        for i, tx in enumerate(primary_node.transaction_log, 1):
            print(f"{i}. {tx.transaction_id}: ₹{tx.amount} "
                  f"({tx.sender_vpa} → {tx.receiver_vpa})")
    
    # Final cluster statistics
    final_stats = cluster.get_cluster_stats()
    print(f"\n📊 Final Cluster Statistics:")
    print(f"Total committed transactions: {final_stats['total_committed_transactions']}")
    print(f"Total messages exchanged: {final_stats['total_messages']}")
    print(f"Byzantine attacks detected: {final_stats['byzantine_attacks_detected']}")
    
    # Demonstrate attack resistance
    print(f"\n🛡️  Byzantine Fault Tolerance Analysis:")
    honest_count = final_stats['node_types'].get('honest', 0)
    faulty_count = final_stats['node_types'].get('faulty', 0)
    malicious_count = final_stats['node_types'].get('malicious', 0)
    
    print(f"Honest nodes: {honest_count}")
    print(f"Faulty nodes: {faulty_count}")
    print(f"Malicious nodes: {malicious_count}")
    print(f"Required for safety: ≤{final_stats['fault_tolerance']} Byzantine nodes")
    
    if (faulty_count + malicious_count) <= final_stats['fault_tolerance']:
        print("✅ System maintains safety and liveness guarantees")
    else:
        print("❌ Too many Byzantine nodes - system safety compromised")
    
    # Production insights
    print(f"\n💡 Production Insights for UPI-scale Systems:")
    print(f"- BFT consensus ensures transaction integrity despite node compromises")
    print(f"- UPI processes 12B+ monthly transactions using Byzantine fault tolerance")
    print(f"- 3f+1 nodes required to tolerate f Byzantine failures")
    print(f"- Prevents double spending attacks and malicious modifications")
    print(f"- Critical for financial systems where trust cannot be assumed")
    print(f"- Higher message complexity (O(n²)) trade-off for security")
    print(f"- Essential for inter-bank transaction processing")
    print(f"- Protects against compromised nodes and insider attacks")
    print(f"- Maintains availability even during coordinated attacks")
    
    # Cleanup
    print(f"\n🧹 Shutting down UPI BFT cluster...")
    cluster.stop_cluster()
    
    print("UPI Byzantine Fault Tolerance demo completed!")

if __name__ == "__main__":
    demonstrate_upi_byzantine_fault_tolerance()