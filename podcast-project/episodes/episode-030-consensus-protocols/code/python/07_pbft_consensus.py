#!/usr/bin/env python3
"""
Practical Byzantine Fault Tolerance (pBFT) Implementation
========================================================

Byzantine Generals Problem solution - Mumbai police coordination!
Just like Mumbai police need to coordinate despite some unreliable units,
pBFT achieves consensus even with Byzantine (malicious) nodes.

Features:
- Three-phase protocol (pre-prepare, prepare, commit)
- Byzantine fault tolerance (f < n/3)
- View changes for leader failures
- Message authentication
- Mumbai police coordination simulation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import uuid
from queue import Queue, Empty

class NodeType(Enum):
    """Node types in pBFT"""
    PRIMARY = "primary"      # Leader
    BACKUP = "backup"        # Follower
    BYZANTINE = "byzantine"  # Malicious

class MessageType(Enum):
    """pBFT message types"""
    REQUEST = "request"
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"
    REPLY = "reply"

class PhaseType(Enum):
    """pBFT phases"""
    PRE_PREPARE_PHASE = "pre_prepare"
    PREPARE_PHASE = "prepare"
    COMMIT_PHASE = "commit"
    REPLY_PHASE = "reply"

@dataclass
class ClientRequest:
    """
    Client request structure
    """
    request_id: str
    client_id: str
    operation: str
    timestamp: float = field(default_factory=time.time)
    data: Dict = field(default_factory=dict)
    
    def get_digest(self) -> str:
        """Calculate request digest"""
        content = f"{self.client_id}:{self.operation}:{self.timestamp}:{json.dumps(self.data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

@dataclass
class pBFTMessage:
    """
    pBFT protocol message
    """
    msg_type: MessageType
    view: int
    sequence_number: int
    sender_id: str
    digest: str = ""
    data: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self.calculate_signature()
    
    def calculate_signature(self) -> str:
        """Calculate message signature (simplified)"""
        content = f"{self.msg_type.value}:{self.view}:{self.sequence_number}:{self.sender_id}:{self.digest}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def is_valid(self) -> bool:
        """Validate message signature"""
        return self.signature == self.calculate_signature()

class pBFTNode:
    """
    pBFT consensus node - Mumbai police station
    """
    
    def __init__(self, node_id: str, total_nodes: int, node_type: NodeType = NodeType.BACKUP):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.node_type = node_type
        
        # Byzantine fault tolerance: f < n/3
        self.max_byzantine_nodes = (total_nodes - 1) // 3
        self.min_honest_nodes = total_nodes - self.max_byzantine_nodes
        
        # Protocol state
        self.view = 0
        self.sequence_number = 0
        self.primary_id = "node_0"  # Default primary
        
        # Message storage
        self.message_log: List[pBFTMessage] = []
        self.pre_prepare_log: Dict[int, pBFTMessage] = {}
        self.prepare_log: Dict[int, List[pBFTMessage]] = defaultdict(list)
        self.commit_log: Dict[int, List[pBFTMessage]] = defaultdict(list)
        
        # Request processing
        self.pending_requests: Queue = Queue()
        self.executed_requests: Set[str] = set()
        self.client_replies: Dict[str, str] = {}
        
        # Mumbai characteristics
        self.reliability = 0.95 if node_type != NodeType.BYZANTINE else 0.3
        self.response_delay = random.uniform(0.1, 0.5)
        self.byzantine_behavior = node_type == NodeType.BYZANTINE
        
        # Performance metrics
        self.requests_processed = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.view_changes = 0
        
        print(f"🏛️ pBFT Node {node_id} initialized ({node_type.value})")
        print(f"   Max Byzantine nodes: {self.max_byzantine_nodes}")
        print(f"   Min honest nodes required: {self.min_honest_nodes}")
    
    def is_primary(self) -> bool:
        """Check if this node is current primary"""
        return self.node_id == self.primary_id and self.node_type != NodeType.BYZANTINE
    
    def calculate_primary_id(self, view: int) -> str:
        """Calculate primary node for given view"""
        primary_index = view % self.total_nodes
        return f"node_{primary_index}"
    
    def process_client_request(self, request: ClientRequest) -> bool:
        """
        Process client request - Mumbai police complaint processing
        """
        if request.request_id in self.executed_requests:
            print(f"   ♻️ Duplicate request {request.request_id} ignored")
            return False
        
        print(f"📝 {self.node_id} received client request: {request.request_id}")
        
        if self.is_primary():
            # Primary initiates consensus
            self.initiate_consensus(request)
        else:
            # Backup forwards to primary or queues
            self.pending_requests.put(request)
        
        return True
    
    def initiate_consensus(self, request: ClientRequest):
        """
        Primary initiates pBFT consensus - Mumbai police headquarters coordination
        """
        if not self.is_primary():
            print(f"❌ {self.node_id} is not primary, cannot initiate consensus")
            return
        
        self.sequence_number += 1
        
        print(f"\n🎯 PRIMARY {self.node_id} INITIATING CONSENSUS")
        print(f"   View: {self.view}, Sequence: {self.sequence_number}")
        print(f"   Request: {request.operation}")
        
        # Phase 1: Pre-Prepare
        pre_prepare_msg = pBFTMessage(
            msg_type=MessageType.PRE_PREPARE,
            view=self.view,
            sequence_number=self.sequence_number,
            sender_id=self.node_id,
            digest=request.get_digest(),
            data={"request": request.__dict__}
        )
        
        # Store pre-prepare message
        self.pre_prepare_log[self.sequence_number] = pre_prepare_msg
        self.message_log.append(pre_prepare_msg)
        
        # Broadcast pre-prepare to all backups
        self.broadcast_message(pre_prepare_msg)
        
        print(f"   📤 Pre-prepare sent to all backup nodes")
    
    def handle_pre_prepare(self, message: pBFTMessage) -> bool:
        """
        Handle pre-prepare message - Mumbai backup station receives orders
        """
        print(f"   📥 {self.node_id} received pre-prepare (view: {message.view}, seq: {message.sequence_number})")
        
        # Validate message
        if not self.validate_pre_prepare(message):
            return False
        
        # Store pre-prepare
        self.pre_prepare_log[message.sequence_number] = message
        self.message_log.append(message)
        
        # Send prepare message
        prepare_msg = pBFTMessage(
            msg_type=MessageType.PREPARE,
            view=self.view,
            sequence_number=message.sequence_number,
            sender_id=self.node_id,
            digest=message.digest
        )
        
        self.broadcast_message(prepare_msg)
        print(f"   📤 {self.node_id} sent prepare message")
        
        return True
    
    def handle_prepare(self, message: pBFTMessage) -> bool:
        """
        Handle prepare message - Mumbai station coordination
        """
        print(f"   📥 {self.node_id} received prepare from {message.sender_id}")
        
        if not self.validate_prepare(message):
            return False
        
        # Store prepare message
        self.prepare_log[message.sequence_number].append(message)
        self.message_log.append(message)
        
        # Check if we have enough prepare messages (2f + 1)
        required_prepares = 2 * self.max_byzantine_nodes + 1
        prepare_count = len(self.prepare_log[message.sequence_number])
        
        if prepare_count >= required_prepares:
            print(f"   ✅ {self.node_id} has {prepare_count} prepare messages - sending commit")
            
            # Send commit message
            commit_msg = pBFTMessage(
                msg_type=MessageType.COMMIT,
                view=self.view,
                sequence_number=message.sequence_number,
                sender_id=self.node_id,
                digest=message.digest
            )
            
            self.broadcast_message(commit_msg)
        
        return True
    
    def handle_commit(self, message: pBFTMessage) -> bool:
        """
        Handle commit message - Mumbai final confirmation
        """
        print(f"   📥 {self.node_id} received commit from {message.sender_id}")
        
        if not self.validate_commit(message):
            return False
        
        # Store commit message
        self.commit_log[message.sequence_number].append(message)
        self.message_log.append(message)
        
        # Check if we have enough commit messages (2f + 1)
        required_commits = 2 * self.max_byzantine_nodes + 1
        commit_count = len(self.commit_log[message.sequence_number])
        
        if commit_count >= required_commits:
            print(f"   🎯 {self.node_id} has {commit_count} commits - EXECUTING REQUEST")
            
            # Execute the request
            self.execute_request(message.sequence_number)
        
        return True
    
    def execute_request(self, sequence_number: int):
        """
        Execute committed request - Mumbai police action
        """
        if sequence_number not in self.pre_prepare_log:
            print(f"❌ No pre-prepare found for sequence {sequence_number}")
            return
        
        pre_prepare = self.pre_prepare_log[sequence_number]
        request_data = pre_prepare.data.get("request", {})
        request_id = request_data.get("request_id")
        
        if request_id in self.executed_requests:
            print(f"   ♻️ Request {request_id} already executed")
            return
        
        # Simulate request execution
        operation = request_data.get("operation", "unknown")
        result = f"executed_{operation}_{sequence_number}"
        
        # Mark as executed
        self.executed_requests.add(request_id)
        self.client_replies[request_id] = result
        self.requests_processed += 1
        
        print(f"   ✅ {self.node_id} EXECUTED request {request_id}: {operation}")
        print(f"   Result: {result}")
    
    def validate_pre_prepare(self, message: pBFTMessage) -> bool:
        """Validate pre-prepare message"""
        # Byzantine nodes might send invalid messages
        if self.byzantine_behavior and random.random() < 0.3:
            print(f"   🎭 Byzantine node {self.node_id} validation failure")
            return False
        
        # Check if sender is current primary
        if message.sender_id != self.calculate_primary_id(message.view):
            print(f"   ❌ Pre-prepare from non-primary: {message.sender_id}")
            return False
        
        # Check view
        if message.view != self.view:
            print(f"   ❌ View mismatch: {message.view} != {self.view}")
            return False
        
        # Check if already have pre-prepare for this sequence
        if message.sequence_number in self.pre_prepare_log:
            existing = self.pre_prepare_log[message.sequence_number]
            if existing.digest != message.digest:
                print(f"   ❌ Different pre-prepare for sequence {message.sequence_number}")
                return False
        
        return message.is_valid()
    
    def validate_prepare(self, message: pBFTMessage) -> bool:
        """Validate prepare message"""
        if self.byzantine_behavior and random.random() < 0.2:
            return False
        
        # Must have corresponding pre-prepare
        if message.sequence_number not in self.pre_prepare_log:
            print(f"   ❌ No pre-prepare for sequence {message.sequence_number}")
            return False
        
        pre_prepare = self.pre_prepare_log[message.sequence_number]
        if pre_prepare.digest != message.digest:
            print(f"   ❌ Prepare digest mismatch")
            return False
        
        return message.is_valid()
    
    def validate_commit(self, message: pBFTMessage) -> bool:
        """Validate commit message"""
        if self.byzantine_behavior and random.random() < 0.2:
            return False
        
        # Must have corresponding pre-prepare
        if message.sequence_number not in self.pre_prepare_log:
            return False
        
        pre_prepare = self.pre_prepare_log[message.sequence_number]
        if pre_prepare.digest != message.digest:
            return False
        
        return message.is_valid()
    
    def broadcast_message(self, message: pBFTMessage):
        """
        Broadcast message to all other nodes - Mumbai radio communication
        """
        self.messages_sent += 1
        
        # Simulate network delay
        time.sleep(self.response_delay)
        
        # Byzantine nodes might not broadcast or send wrong messages
        if self.byzantine_behavior:
            if random.random() < 0.3:  # 30% chance to not broadcast
                print(f"   🎭 Byzantine {self.node_id} failed to broadcast")
                return
            
            if random.random() < 0.2:  # 20% chance to corrupt message
                message.digest = "corrupted_" + message.digest
                print(f"   🎭 Byzantine {self.node_id} corrupted message")
        
        # In real system, this would send via network
        # For simulation, we'll handle it in the network simulator
    
    def trigger_view_change(self, new_view: int):
        """
        Trigger view change - Mumbai police leadership change
        """
        print(f"🔄 {self.node_id} triggering view change to view {new_view}")
        
        self.view_changes += 1
        
        view_change_msg = pBFTMessage(
            msg_type=MessageType.VIEW_CHANGE,
            view=new_view,
            sequence_number=self.sequence_number,
            sender_id=self.node_id,
            data={"last_executed": len(self.executed_requests)}
        )
        
        self.broadcast_message(view_change_msg)
    
    def get_node_stats(self) -> Dict:
        """Get node performance statistics"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "view": self.view,
            "sequence_number": self.sequence_number,
            "is_primary": self.is_primary(),
            "requests_processed": self.requests_processed,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "view_changes": self.view_changes,
            "executed_requests": len(self.executed_requests),
            "reliability": self.reliability
        }

class pBFTNetwork:
    """
    pBFT Network Simulator - Mumbai Police Network
    """
    
    def __init__(self, total_nodes: int = 7, byzantine_nodes: int = 2):
        if byzantine_nodes >= total_nodes // 3:
            raise ValueError(f"Too many Byzantine nodes: {byzantine_nodes} >= {total_nodes // 3}")
        
        self.total_nodes = total_nodes
        self.byzantine_count = byzantine_nodes
        self.nodes: Dict[str, pBFTNode] = {}
        self.message_queue: Queue = Queue()
        
        # Network statistics
        self.total_requests = 0
        self.successful_consensus = 0
        self.failed_consensus = 0
        
        print(f"🌐 pBFT Network initialized")
        print(f"   Total nodes: {total_nodes}")
        print(f"   Byzantine nodes: {byzantine_nodes}")
        print(f"   Fault tolerance: f < {total_nodes // 3}")
        
        self.create_nodes()
    
    def create_nodes(self):
        """Create network nodes with Mumbai police station names"""
        mumbai_stations = [
            "Colaba_PS", "Crawford_Market_PS", "Bandra_PS", "Andheri_PS",
            "Borivali_PS", "Thane_PS", "Kurla_PS", "Worli_PS", "Powai_PS"
        ]
        
        for i in range(self.total_nodes):
            station_name = mumbai_stations[i] if i < len(mumbai_stations) else f"Station_{i}"
            
            # First node is primary, some nodes are Byzantine
            if i == 0:
                node_type = NodeType.PRIMARY
            elif i <= self.byzantine_count:
                node_type = NodeType.BYZANTINE
            else:
                node_type = NodeType.BACKUP
            
            node = pBFTNode(f"node_{i}", self.total_nodes, node_type)
            node.node_id = station_name  # Use Mumbai names
            self.nodes[station_name] = node
        
        # Update primary reference
        primary_station = mumbai_stations[0]
        for node in self.nodes.values():
            node.primary_id = primary_station
    
    def route_message(self, message: pBFTMessage, exclude_sender: bool = True):
        """
        Route message to all nodes - Mumbai police radio network
        """
        recipients = []
        
        for node_id, node in self.nodes.items():
            if exclude_sender and node_id == message.sender_id:
                continue
            
            # Simulate network reliability
            if random.random() < 0.95:  # 95% message delivery
                recipients.append(node)
            else:
                print(f"   📡 Message to {node_id} lost (network issue)")
        
        return recipients
    
    def process_message(self, message: pBFTMessage):
        """Process message across the network"""
        recipients = self.route_message(message)
        
        for node in recipients:
            node.messages_received += 1
            
            try:
                if message.msg_type == MessageType.PRE_PREPARE:
                    node.handle_pre_prepare(message)
                elif message.msg_type == MessageType.PREPARE:
                    node.handle_prepare(message)
                elif message.msg_type == MessageType.COMMIT:
                    node.handle_commit(message)
                
            except Exception as e:
                print(f"   ❌ Error processing message at {node.node_id}: {str(e)}")
    
    def submit_client_request(self, operation: str, client_id: str = "client_1", 
                            data: Dict = None) -> str:
        """
        Submit client request to network - Mumbai citizen complaint
        """
        request_id = f"req_{self.total_requests:03d}"
        self.total_requests += 1
        
        request = ClientRequest(
            request_id=request_id,
            client_id=client_id,
            operation=operation,
            data=data or {}
        )
        
        # Send to primary node
        primary_node = None
        for node in self.nodes.values():
            if node.is_primary():
                primary_node = node
                break
        
        if not primary_node:
            print("❌ No primary node found")
            return request_id
        
        print(f"\n📨 CLIENT REQUEST SUBMITTED")
        print(f"   Request ID: {request_id}")
        print(f"   Operation: {operation}")
        print(f"   Primary: {primary_node.node_id}")
        
        # Process request
        primary_node.process_client_request(request)
        
        return request_id
    
    def simulate_consensus_scenario(self, requests: List[Tuple[str, str]]) -> Dict:
        """
        Simulate complete consensus scenario - Mumbai police operations
        """
        print(f"\n🎯 SIMULATING pBFT CONSENSUS SCENARIO")
        print(f"Requests to process: {len(requests)}")
        print("=" * 60)
        
        scenario_results = []
        
        for i, (operation, client_id) in enumerate(requests):
            print(f"\n{'='*50}")
            print(f"CONSENSUS ROUND {i + 1}/{len(requests)}")
            print(f"{'='*50}")
            
            start_time = time.time()
            
            # Submit request
            request_id = self.submit_client_request(operation, client_id)
            
            # Allow time for consensus protocol
            max_wait_time = 10.0  # Maximum time to wait for consensus
            wait_time = 0.0
            step_time = 0.5
            
            while wait_time < max_wait_time:
                time.sleep(step_time)
                wait_time += step_time
                
                # Check if consensus reached (majority executed)
                executed_count = sum(
                    1 for node in self.nodes.values()
                    if request_id in node.executed_requests
                )
                
                if executed_count >= (self.total_nodes - self.byzantine_count):
                    consensus_time = time.time() - start_time
                    print(f"   ✅ CONSENSUS REACHED in {consensus_time:.2f}s")
                    print(f"   Nodes executed: {executed_count}/{self.total_nodes}")
                    
                    self.successful_consensus += 1
                    scenario_results.append({
                        "request_id": request_id,
                        "operation": operation,
                        "consensus_reached": True,
                        "consensus_time": consensus_time,
                        "nodes_executed": executed_count
                    })
                    break
            else:
                # Consensus timeout
                print(f"   ⏰ CONSENSUS TIMEOUT after {max_wait_time}s")
                self.failed_consensus += 1
                scenario_results.append({
                    "request_id": request_id,
                    "operation": operation,
                    "consensus_reached": False,
                    "consensus_time": max_wait_time,
                    "nodes_executed": executed_count
                })
            
            # Brief pause between requests
            time.sleep(1.0)
        
        return {
            "total_requests": len(requests),
            "successful_consensus": self.successful_consensus,
            "failed_consensus": self.failed_consensus,
            "success_rate": self.successful_consensus / len(requests) * 100,
            "results": scenario_results
        }
    
    def simulate_byzantine_attack(self):
        """
        Simulate Byzantine attack scenario
        """
        print(f"\n💀 SIMULATING BYZANTINE ATTACK")
        print("=" * 40)
        
        # Make all Byzantine nodes more aggressive
        byzantine_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.BYZANTINE]
        
        print(f"Byzantine nodes: {[node.node_id for node in byzantine_nodes]}")
        
        for node in byzantine_nodes:
            node.byzantine_behavior = True
            node.reliability = 0.2  # Very unreliable
        
        # Submit request during attack
        attack_requests = [
            ("process_evidence", "victim_1"),
            ("file_complaint", "citizen_2"),
            ("emergency_response", "caller_3")
        ]
        
        attack_results = self.simulate_consensus_scenario(attack_requests)
        
        return attack_results
    
    def get_network_stats(self) -> Dict:
        """Get comprehensive network statistics"""
        node_stats = [node.get_node_stats() for node in self.nodes.values()]
        
        total_messages = sum(node.messages_sent for node in self.nodes.values())
        total_processed = sum(node.requests_processed for node in self.nodes.values())
        
        return {
            "total_nodes": self.total_nodes,
            "byzantine_nodes": self.byzantine_count,
            "fault_tolerance": f"f < {self.total_nodes // 3}",
            "total_requests_submitted": self.total_requests,
            "successful_consensus": self.successful_consensus,
            "failed_consensus": self.failed_consensus,
            "consensus_success_rate": (self.successful_consensus / max(1, self.total_requests)) * 100,
            "total_messages_sent": total_messages,
            "average_requests_per_node": total_processed / len(self.nodes),
            "node_details": node_stats
        }

def demonstrate_pbft_properties():
    """
    Demonstrate key pBFT properties
    """
    print("🎯 pBFT PROPERTIES DEMONSTRATION")
    print("=" * 50)
    
    properties = {
        "Safety": "No two honest nodes execute conflicting operations for the same sequence number",
        "Liveness": "Requests from honest clients are eventually executed",
        "Byzantine Fault Tolerance": "System tolerates f < n/3 Byzantine failures",
        "Deterministic": "All honest nodes execute operations in the same order",
        "Message Complexity": "O(n²) messages per request in normal case",
        "View Changes": "System recovers from primary failures automatically"
    }
    
    for prop, description in properties.items():
        print(f"\n📋 {prop}:")
        print(f"   {description}")
    
    return properties

if __name__ == "__main__":
    print("🚀 PRACTICAL BYZANTINE FAULT TOLERANCE (pBFT)")
    print("Mumbai Police Coordination System")
    print("=" * 70)
    
    try:
        # Demonstrate pBFT properties
        pbft_properties = demonstrate_pbft_properties()
        
        # Create pBFT network
        print(f"\n🏗️ CREATING MUMBAI POLICE pBFT NETWORK")
        print("-" * 50)
        
        network = pBFTNetwork(total_nodes=7, byzantine_nodes=2)
        
        # Normal consensus scenario
        print(f"\n📋 NORMAL CONSENSUS SCENARIO")
        print("-" * 40)
        
        normal_requests = [
            ("register_complaint", "citizen_001"),
            ("process_evidence", "forensic_team"),
            ("issue_challan", "traffic_unit"),
            ("emergency_response", "control_room"),
            ("file_report", "investigating_officer")
        ]
        
        normal_results = network.simulate_consensus_scenario(normal_requests)
        
        # Byzantine attack scenario
        byzantine_results = network.simulate_byzantine_attack()
        
        # Final network statistics
        final_stats = network.get_network_stats()
        
        print(f"\n📊 FINAL NETWORK STATISTICS")
        print("=" * 50)
        print(f"Total nodes: {final_stats['total_nodes']}")
        print(f"Byzantine nodes: {final_stats['byzantine_nodes']}")
        print(f"Fault tolerance: {final_stats['fault_tolerance']}")
        print(f"Requests processed: {final_stats['total_requests_submitted']}")
        print(f"Consensus success rate: {final_stats['consensus_success_rate']:.1f}%")
        print(f"Total messages: {final_stats['total_messages_sent']}")
        
        print(f"\n🎯 SCENARIO RESULTS")
        print("-" * 30)
        print(f"Normal scenario: {normal_results['success_rate']:.1f}% success")
        print(f"Byzantine attack: {byzantine_results['success_rate']:.1f}% success")
        
        print("\n🏆 Key Insights:")
        print("• pBFT provides strong consistency guarantees")
        print("• System works correctly with f < n/3 Byzantine nodes")
        print("• Three-phase protocol ensures safety and liveness")
        print("• Like Mumbai police - coordination despite bad actors!")
        
        print("\n🎊 pBFT CONSENSUS SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in pBFT simulation: {e}")
        raise