#!/usr/bin/env python3
"""
Practical Byzantine Fault Tolerance (PBFT) Implementation
Real-world application: Hyperledger Fabric and enterprise blockchain systems

यह implementation PBFT algorithm को demonstrate करती है
जैसे कि enterprise blockchain में fast finality के लिए इस्तेमाल होती है
"""

import time
import threading
import json
import hashlib
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
from collections import defaultdict, Counter

class NodeState(Enum):
    NORMAL = "normal"
    VIEW_CHANGE = "view_change"
    RECOVERY = "recovery"

class MessageType(Enum):
    REQUEST = "request"
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"

@dataclass
class PBFTMessage:
    """PBFT protocol message"""
    msg_type: MessageType
    view: int
    sequence: int
    sender_id: str
    content: Any
    timestamp: float
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            # Create message signature for authenticity
            msg_data = f"{self.msg_type.value}:{self.view}:{self.sequence}:{self.sender_id}:{json.dumps(self.content, sort_keys=True)}"
            self.signature = hashlib.sha256(msg_data.encode()).hexdigest()[:16]

@dataclass
class ClientRequest:
    """Client request to be processed"""
    client_id: str
    request_id: str
    operation: Dict[str, Any]
    timestamp: float

@dataclass
class NodeInfo:
    """Information about a PBFT node"""
    node_id: str
    is_primary: bool = False
    is_byzantine: bool = False
    malicious_probability: float = 0.0

class PBFTNode:
    """
    Practical Byzantine Fault Tolerance Node
    बिल्कुल Hyperledger Fabric के endorsing peers की तरह
    """
    
    def __init__(self, node_id: str, all_nodes: List[str], is_byzantine: bool = False):
        self.node_id = node_id
        self.all_nodes = all_nodes
        self.n = len(all_nodes)  # Total number of nodes
        self.f = (self.n - 1) // 3  # Maximum Byzantine nodes tolerated
        
        # Node state
        self.current_view = 0
        self.state = NodeState.NORMAL
        self.is_byzantine = is_byzantine
        self.malicious_probability = 0.8 if is_byzantine else 0.0
        
        # PBFT state
        self.sequence_number = 0
        self.log: Dict[int, PBFTMessage] = {}  # sequence -> message
        self.prepare_log: Dict[int, Dict[str, PBFTMessage]] = defaultdict(dict)  # seq -> node -> msg
        self.commit_log: Dict[int, Dict[str, PBFTMessage]] = defaultdict(dict)   # seq -> node -> msg
        
        # Request processing
        self.executed_requests: Set[Tuple[str, str]] = set()  # (client_id, request_id)
        self.pending_requests: List[ClientRequest] = []
        
        # State machine (actual data storage)
        self.state_machine: Dict[str, Any] = {}
        
        # Network simulation
        self.network: Dict[str, 'PBFTNode'] = {}
        self.message_queue: List[PBFTMessage] = []
        self.is_running = True
        
        # View change
        self.view_change_timer = None
        self.view_change_timeout = 5.0  # seconds
        
        print(f"🏛️ PBFT Node {node_id} initialized ({'Byzantine' if is_byzantine else 'Honest'})")
    
    def set_network(self, network: Dict[str, 'PBFTNode']):
        """Set network connections"""
        self.network = network
    
    def is_primary(self) -> bool:
        """Check if this node is the primary for current view"""
        primary_index = self.current_view % self.n
        primary_node = self.all_nodes[primary_index]
        return primary_node == self.node_id
    
    def get_primary_node(self) -> str:
        """Get primary node ID for current view"""
        primary_index = self.current_view % self.n
        return self.all_nodes[primary_index]
    
    def submit_request(self, client_request: ClientRequest) -> bool:
        """
        Submit client request to the network (only to primary)
        यह function client applications से requests receive करता है
        """
        if not self.is_primary():
            print(f"❌ Node {self.node_id}: Not primary, forwarding request to {self.get_primary_node()}")
            # Forward to primary
            primary = self.network.get(self.get_primary_node())
            if primary:
                return primary.submit_request(client_request)
            return False
        
        print(f"📝 Primary {self.node_id}: Received client request {client_request.request_id}")
        
        # Check if request already processed
        request_key = (client_request.client_id, client_request.request_id)
        if request_key in self.executed_requests:
            print(f"⚠️ Primary {self.node_id}: Request {client_request.request_id} already processed")
            return True
        
        # Add to pending requests
        self.pending_requests.append(client_request)
        
        # Start PBFT consensus
        self.start_consensus(client_request)
        
        return True
    
    def start_consensus(self, client_request: ClientRequest):
        """Start PBFT three-phase consensus"""
        if not self.is_primary():
            return
        
        self.sequence_number += 1
        sequence = self.sequence_number
        
        print(f"🎯 Primary {self.node_id}: Starting consensus for sequence {sequence}")
        
        # Phase 1: Pre-prepare
        self.send_pre_prepare(client_request, sequence)
        
        # Start view change timer
        self.reset_view_change_timer()
    
    def send_pre_prepare(self, client_request: ClientRequest, sequence: int):
        """Send pre-prepare message to all backups"""
        # Byzantine behavior: might send different requests to different nodes
        content = client_request
        
        if self.is_byzantine and random.random() < self.malicious_probability:
            # Create conflicting request
            content = ClientRequest(
                client_id=client_request.client_id,
                request_id=client_request.request_id + "_MALICIOUS",
                operation={"type": "MALICIOUS", "data": "corrupted"},
                timestamp=client_request.timestamp
            )
            print(f"💀 Byzantine primary {self.node_id}: Sending malicious pre-prepare")
        
        pre_prepare_msg = PBFTMessage(
            msg_type=MessageType.PRE_PREPARE,
            view=self.current_view,
            sequence=sequence,
            sender_id=self.node_id,
            content=content
        )
        
        # Store in log
        self.log[sequence] = pre_prepare_msg
        
        # Send to all backup nodes
        self.broadcast_message(pre_prepare_msg)
        
        print(f"📤 Primary {self.node_id}: Sent pre-prepare for sequence {sequence}")
    
    def handle_pre_prepare(self, message: PBFTMessage):
        """Handle pre-prepare message from primary"""
        if self.is_primary():
            return  # Primary doesn't process its own pre-prepare
        
        sequence = message.sequence
        view = message.view
        
        print(f"📨 Backup {self.node_id}: Received pre-prepare for sequence {sequence}")
        
        # Validate pre-prepare
        if not self.validate_pre_prepare(message):
            print(f"❌ Backup {self.node_id}: Invalid pre-prepare for sequence {sequence}")
            return
        
        # Store pre-prepare
        self.log[sequence] = message
        
        # Send prepare message
        self.send_prepare(sequence, view, message.content)
    
    def validate_pre_prepare(self, message: PBFTMessage) -> bool:
        """Validate pre-prepare message"""
        sequence = message.sequence
        view = message.view
        
        # Check if from correct primary
        expected_primary = self.get_primary_node()
        if message.sender_id != expected_primary:
            return False
        
        # Check view
        if view != self.current_view:
            return False
        
        # Check sequence number
        if sequence <= 0:
            return False
        
        # Check if already have different pre-prepare for this sequence
        if sequence in self.log and self.log[sequence].content != message.content:
            return False
        
        return True
    
    def send_prepare(self, sequence: int, view: int, content: Any):
        """Send prepare message to all nodes"""
        # Byzantine behavior: might send wrong content
        if self.is_byzantine and random.random() < self.malicious_probability:
            content = {"type": "BYZANTINE_PREPARE", "original": content}
            print(f"💀 Byzantine node {self.node_id}: Sending malicious prepare")
        
        prepare_msg = PBFTMessage(
            msg_type=MessageType.PREPARE,
            view=view,
            sequence=sequence,
            sender_id=self.node_id,
            content=content
        )
        
        # Store our own prepare
        self.prepare_log[sequence][self.node_id] = prepare_msg
        
        # Send to all nodes
        self.broadcast_message(prepare_msg)
        
        print(f"📤 Node {self.node_id}: Sent prepare for sequence {sequence}")
    
    def handle_prepare(self, message: PBFTMessage):
        """Handle prepare message"""
        sequence = message.sequence
        
        print(f"📨 Node {self.node_id}: Received prepare from {message.sender_id} for sequence {sequence}")
        
        # Store prepare message
        self.prepare_log[sequence][message.sender_id] = message
        
        # Check if we have enough prepare messages (2f)
        if self.check_prepared(sequence):
            print(f"✅ Node {self.node_id}: Prepared for sequence {sequence}")
            self.send_commit(sequence, message.view, message.content)
    
    def check_prepared(self, sequence: int) -> bool:
        """Check if request is prepared (have pre-prepare + 2f prepares)"""
        if sequence not in self.log:
            return False
        
        # Count matching prepare messages
        pre_prepare_content = self.log[sequence].content
        matching_prepares = 0
        
        for prepare_msg in self.prepare_log[sequence].values():
            if self.content_matches(prepare_msg.content, pre_prepare_content):
                matching_prepares += 1
        
        # Need 2f prepare messages (including our own if we sent one)
        return matching_prepares >= 2 * self.f
    
    def send_commit(self, sequence: int, view: int, content: Any):
        """Send commit message to all nodes"""
        # Byzantine behavior
        if self.is_byzantine and random.random() < self.malicious_probability:
            content = {"type": "BYZANTINE_COMMIT", "original": content}
            print(f"💀 Byzantine node {self.node_id}: Sending malicious commit")
        
        commit_msg = PBFTMessage(
            msg_type=MessageType.COMMIT,
            view=view,
            sequence=sequence,
            sender_id=self.node_id,
            content=content
        )
        
        # Store our own commit
        self.commit_log[sequence][self.node_id] = commit_msg
        
        # Send to all nodes
        self.broadcast_message(commit_msg)
        
        print(f"📤 Node {self.node_id}: Sent commit for sequence {sequence}")
    
    def handle_commit(self, message: PBFTMessage):
        """Handle commit message"""
        sequence = message.sequence
        
        print(f"📨 Node {self.node_id}: Received commit from {message.sender_id} for sequence {sequence}")
        
        # Store commit message
        self.commit_log[sequence][message.sender_id] = message
        
        # Check if we can commit
        if self.check_committed(sequence):
            self.execute_request(sequence)
    
    def check_committed(self, sequence: int) -> bool:
        """Check if request is committed (have 2f+1 commits)"""
        if sequence not in self.log:
            return False
        
        # Must be prepared first
        if not self.check_prepared(sequence):
            return False
        
        # Count matching commit messages
        pre_prepare_content = self.log[sequence].content
        matching_commits = 0
        
        for commit_msg in self.commit_log[sequence].values():
            if self.content_matches(commit_msg.content, pre_prepare_content):
                matching_commits += 1
        
        # Need 2f+1 commit messages
        return matching_commits >= 2 * self.f + 1
    
    def execute_request(self, sequence: int):
        """Execute the committed request"""
        if sequence not in self.log:
            return
        
        request = self.log[sequence].content
        
        # Check if already executed
        if isinstance(request, ClientRequest):
            request_key = (request.client_id, request.request_id)
            if request_key in self.executed_requests:
                return
            
            # Execute the operation
            self.apply_operation(request.operation)
            
            # Mark as executed
            self.executed_requests.add(request_key)
            
            print(f"🎯 Node {self.node_id}: Executed request {request.request_id} (sequence {sequence})")
        
        # Cancel view change timer if running
        if self.view_change_timer:
            self.view_change_timer.cancel()
    
    def apply_operation(self, operation: Dict[str, Any]):
        """Apply operation to state machine"""
        op_type = operation.get("type", "")
        
        if op_type == "SET":
            key = operation.get("key", "")
            value = operation.get("value", "")
            self.state_machine[key] = value
            
        elif op_type == "DELETE":
            key = operation.get("key", "")
            self.state_machine.pop(key, None)
            
        elif op_type == "TRANSFER":
            # Banking transfer operation
            from_account = operation.get("from_account", "")
            to_account = operation.get("to_account", "")
            amount = operation.get("amount", 0)
            
            # Debit from source
            if from_account in self.state_machine:
                self.state_machine[from_account] = self.state_machine[from_account] - amount
            
            # Credit to destination
            if to_account not in self.state_machine:
                self.state_machine[to_account] = 0
            self.state_machine[to_account] = self.state_machine[to_account] + amount
    
    def content_matches(self, content1: Any, content2: Any) -> bool:
        """Check if two message contents match"""
        try:
            return json.dumps(content1, sort_keys=True) == json.dumps(content2, sort_keys=True)
        except:
            return content1 == content2
    
    def broadcast_message(self, message: PBFTMessage):
        """Broadcast message to all nodes"""
        for node_id in self.all_nodes:
            if node_id != self.node_id and node_id in self.network:
                node = self.network[node_id]
                threading.Thread(target=node.receive_message, args=(message,)).start()
    
    def receive_message(self, message: PBFTMessage):
        """Receive and route message based on type"""
        try:
            if message.msg_type == MessageType.PRE_PREPARE:
                self.handle_pre_prepare(message)
            elif message.msg_type == MessageType.PREPARE:
                self.handle_prepare(message)
            elif message.msg_type == MessageType.COMMIT:
                self.handle_commit(message)
            # Add other message type handlers as needed
                
        except Exception as e:
            print(f"❌ Node {self.node_id}: Error processing message: {e}")
    
    def reset_view_change_timer(self):
        """Reset view change timer"""
        if self.view_change_timer:
            self.view_change_timer.cancel()
        
        self.view_change_timer = threading.Timer(self.view_change_timeout, self.start_view_change)
        self.view_change_timer.start()
    
    def start_view_change(self):
        """Start view change process (simplified)"""
        print(f"⚠️ Node {self.node_id}: Starting view change due to timeout")
        self.current_view += 1
        self.state = NodeState.VIEW_CHANGE
        
        # In a full implementation, would send view-change messages
        # For simplicity, just transition back to normal
        time.sleep(1)
        self.state = NodeState.NORMAL
    
    def get_state(self) -> Dict[str, Any]:
        """Get current node state"""
        return {
            'node_id': self.node_id,
            'is_primary': self.is_primary(),
            'is_byzantine': self.is_byzantine,
            'current_view': self.current_view,
            'sequence_number': self.sequence_number,
            'executed_requests': len(self.executed_requests),
            'state_machine_size': len(self.state_machine)
        }

def simulate_pbft_banking_consensus():
    """
    Simulate PBFT consensus for banking operations
    यह simulation enterprise banking में transaction processing को show करता है
    """
    print("🇮🇳 PBFT Banking Consensus - Enterprise Transaction Processing")
    print("🏦 Scenario: Multi-bank consortium processing cross-bank transfers")
    print("=" * 70)
    
    # Create banking nodes (consortium members)
    bank_nodes = ['SBI-Mumbai', 'HDFC-Delhi', 'ICICI-Bangalore', 'Axis-Chennai']
    byzantine_count = 1  # 1 Byzantine node (can tolerate with 4 total nodes)
    
    # Initialize PBFT nodes
    pbft_network = {}
    for i, node_id in enumerate(bank_nodes):
        is_byzantine = i < byzantine_count
        pbft_network[node_id] = PBFTNode(node_id, bank_nodes, is_byzantine)
    
    # Set network connections
    for node in pbft_network.values():
        node.set_network(pbft_network)
    
    print(f"🏛️ Created {len(pbft_network)} banking nodes:")
    for node_id, node in pbft_network.items():
        node_type = "Byzantine" if node.is_byzantine else "Honest"
        primary_status = "PRIMARY" if node.is_primary() else "BACKUP"
        print(f"   {node_id}: {node_type} ({primary_status})")
    
    # Simulate banking transactions
    print(f"\n💳 Processing cross-bank transactions...")
    
    # Find primary node
    primary_node = None
    for node in pbft_network.values():
        if node.is_primary():
            primary_node = node
            break
    
    if not primary_node:
        print("❌ No primary node found!")
        return
    
    # Create banking transactions
    banking_transactions = [
        ClientRequest(
            client_id="customer001",
            request_id="txn001",
            operation={
                "type": "SET",
                "key": "account:rahul:sbi", 
                "value": 100000,
                "description": "Initial balance - Rahul SBI"
            },
            timestamp=time.time()
        ),
        ClientRequest(
            client_id="customer002", 
            request_id="txn002",
            operation={
                "type": "SET",
                "key": "account:priya:hdfc",
                "value": 75000, 
                "description": "Initial balance - Priya HDFC"
            },
            timestamp=time.time()
        ),
        ClientRequest(
            client_id="customer001",
            request_id="txn003", 
            operation={
                "type": "TRANSFER",
                "from_account": "account:rahul:sbi",
                "to_account": "account:priya:hdfc",
                "amount": 25000,
                "description": "Rahul -> Priya: ₹25,000"
            },
            timestamp=time.time()
        ),
        ClientRequest(
            client_id="merchant001",
            request_id="txn004",
            operation={
                "type": "SET", 
                "key": "account:amazon:icici",
                "value": 0,
                "description": "Amazon merchant account"
            },
            timestamp=time.time()
        ),
        ClientRequest(
            client_id="customer002",
            request_id="txn005",
            operation={
                "type": "TRANSFER",
                "from_account": "account:priya:hdfc", 
                "to_account": "account:amazon:icici",
                "amount": 5000,
                "description": "Priya -> Amazon: ₹5,000"
            },
            timestamp=time.time()
        )
    ]
    
    # Process transactions through PBFT
    for i, transaction in enumerate(banking_transactions):
        print(f"\n🔄 Transaction {i+1}: {transaction.operation['description']}")
        
        success = primary_node.submit_request(transaction)
        
        if success:
            print(f"   📝 Submitted to primary {primary_node.node_id}")
        else:
            print(f"   ❌ Failed to submit transaction")
        
        # Wait for consensus
        time.sleep(2)
    
    # Wait for all transactions to be processed
    print(f"\n⏳ Waiting for all transactions to commit...")
    time.sleep(3)
    
    # Show final state across all nodes
    print(f"\n💰 Final Account Balances Across Banking Network:")
    
    reference_state = None
    consistent = True
    
    for node_id, node in pbft_network.items():
        state_info = node.get_state()
        print(f"\n🏦 {node_id} ({'Byzantine' if node.is_byzantine else 'Honest'}):")
        print(f"   Executed requests: {state_info['executed_requests']}")
        print(f"   State machine entries: {state_info['state_machine_size']}")
        
        # Show account balances
        print(f"   Account balances:")
        for account, balance in node.state_machine.items():
            print(f"     {account}: ₹{balance}")
        
        # Check consistency
        if reference_state is None:
            reference_state = dict(node.state_machine)
        elif reference_state != dict(node.state_machine):
            consistent = False
    
    # Verify consensus
    print(f"\n🔍 Consensus Verification:")
    if consistent:
        print(f"✅ All honest nodes have consistent state!")
        print(f"🎉 PBFT consensus successfully achieved despite Byzantine node!")
    else:
        print(f"❌ Inconsistent state detected across nodes!")
    
    # Show consensus statistics
    print(f"\n📊 PBFT Consensus Statistics:")
    for node_id, node in pbft_network.items():
        state_info = node.get_state()
        print(f"   {node_id}:")
        print(f"     Primary: {state_info['is_primary']}")
        print(f"     View: {state_info['current_view']}")
        print(f"     Sequence: {state_info['sequence_number']}")
        print(f"     Byzantine: {state_info['is_byzantine']}")

def simulate_hyperledger_endorsement():
    """
    Simulate Hyperledger Fabric-style endorsement process using PBFT
    यह example enterprise blockchain के endorsement policy को demonstrate करता है
    """
    print("\n" + "="*70)
    print("🇮🇳 Hyperledger Fabric Endorsement - Supply Chain Consensus")
    print("=" * 70)
    
    # Create endorsing peers
    endorser_peers = ['Peer-Supplier', 'Peer-Manufacturer', 'Peer-Distributor', 'Peer-Retailer']
    
    # Initialize endorser network
    endorsers = {}
    byzantine_endorsers = 1
    
    for i, peer_id in enumerate(endorser_peers):
        is_byzantine = i < byzantine_endorsers
        endorsers[peer_id] = PBFTNode(peer_id, endorser_peers, is_byzantine)
    
    # Set network
    for endorser in endorsers.values():
        endorser.set_network(endorsers)
    
    print(f"🔗 Supply Chain Endorsement Network:")
    for peer_id, endorser in endorsers.items():
        peer_type = "Byzantine" if endorser.is_byzantine else "Honest"
        print(f"   {peer_id}: {peer_type}")
    
    # Find primary endorser
    primary_endorser = None
    for endorser in endorsers.values():
        if endorser.is_primary():
            primary_endorser = endorser
            break
    
    # Supply chain transactions
    supply_chain_requests = [
        ClientRequest(
            client_id="supplier001",
            request_id="sc001",
            operation={
                "type": "SET",
                "key": "product:wheat:batch001",
                "value": {
                    "quantity": 1000,
                    "origin": "Punjab",
                    "quality": "A+",
                    "price": 2500
                },
                "description": "Wheat batch from Punjab supplier"
            },
            timestamp=time.time()
        ),
        ClientRequest(
            client_id="manufacturer001",
            request_id="sc002", 
            operation={
                "type": "SET",
                "key": "product:flour:batch001",
                "value": {
                    "input": "product:wheat:batch001",
                    "quantity": 900,
                    "process_date": "2024-01-15",
                    "price": 3000
                },
                "description": "Flour manufactured from wheat batch"
            },
            timestamp=time.time()
        )
    ]
    
    print(f"\n📦 Processing supply chain transactions...")
    
    for i, request in enumerate(supply_chain_requests):
        print(f"\n🔄 Supply Chain Transaction {i+1}")
        success = primary_endorser.submit_request(request)
        time.sleep(2)
    
    # Wait for processing
    time.sleep(3)
    
    print(f"\n📋 Final Supply Chain State:")
    for peer_id, endorser in endorsers.items():
        print(f"\n🏢 {peer_id}:")
        for product_key, product_info in endorser.state_machine.items():
            print(f"   {product_key}: {product_info}")

if __name__ == "__main__":
    # Run PBFT banking consensus simulation
    simulate_pbft_banking_consensus()
    
    # Run Hyperledger endorsement simulation
    simulate_hyperledger_endorsement()
    
    print("\n" + "="*70)
    print("🇮🇳 PBFT Key Features and Benefits:")
    print("1. Fast finality - no need to wait for multiple confirmations")
    print("2. Deterministic - guaranteed agreement in bounded time")
    print("3. Tolerates up to (n-1)/3 Byzantine nodes")
    print("4. Three-phase protocol: pre-prepare, prepare, commit")
    print("5. Used in enterprise blockchains like Hyperledger Fabric")
    print("6. Suitable for permissioned networks with known participants")
    print("7. Lower energy consumption compared to Proof-of-Work")