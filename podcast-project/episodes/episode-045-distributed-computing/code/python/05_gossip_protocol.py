#!/usr/bin/env python3
"""
Gossip Protocol Implementation for Distributed Systems
Gossip protocol - जैसे कि WhatsApp के message propagation में use होता है

यह example दिखाता है कि कैसे gossip protocol work करती है distributed systems में।
Indian companies जैसे WhatsApp India, Signal, Telegram इसे use करती हैं
message propagation और cluster membership के लिए।

Production context: WhatsApp propagates 100+ billion messages daily using gossip-style protocols
Scale: Information spreads exponentially across thousands of servers
Challenge: Ensuring eventual consistency while minimizing network overhead
"""

import random
import time
import threading
import json
import hashlib
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import copy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of gossip messages"""
    GOSSIP = "gossip"
    ACK = "ack"
    MEMBERSHIP = "membership"
    HEARTBEAT = "heartbeat"
    DATA_UPDATE = "data_update"

class NodeState(Enum):
    """Node states in the gossip cluster"""
    ALIVE = "alive"
    SUSPECTED = "suspected"
    FAILED = "failed"
    JOINING = "joining"
    LEAVING = "leaving"

@dataclass
class GossipMessage:
    """Represents a message in the gossip protocol"""
    message_id: str
    message_type: MessageType
    sender_id: str
    content: Dict[str, Any]
    timestamp: float
    ttl: int = 10  # Time to live (hop count)
    sequence_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "sequence_number": self.sequence_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GossipMessage':
        return cls(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            content=data["content"],
            timestamp=data["timestamp"],
            ttl=data.get("ttl", 10),
            sequence_number=data.get("sequence_number", 0)
        )

@dataclass
class NodeInfo:
    """Information about a node in the cluster"""
    node_id: str
    host: str
    port: int
    state: NodeState
    last_seen: float
    heartbeat_count: int = 0
    version: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "state": self.state.value,
            "last_seen": self.last_seen,
            "heartbeat_count": self.heartbeat_count,
            "version": self.version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeInfo':
        return cls(
            node_id=data["node_id"],
            host=data["host"],
            port=data["port"],
            state=NodeState(data["state"]),
            last_seen=data["last_seen"],
            heartbeat_count=data.get("heartbeat_count", 0),
            version=data.get("version", 0),
            metadata=data.get("metadata", {})
        )

class WhatsAppGossipNode:
    """
    WhatsApp-style gossip node for message propagation
    हर node एक WhatsApp server है जो messages को efficiently propagate करता है
    """
    
    def __init__(self, node_id: str, host: str, port: int, region: str = "india"):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.region = region
        
        # Node state
        self.state = NodeState.ALIVE
        self.heartbeat_count = 0
        self.sequence_number = 0
        
        # Cluster membership
        self.membership: Dict[str, NodeInfo] = {}
        self.suspected_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
        
        # Message handling
        self.message_cache: Dict[str, GossipMessage] = {}
        self.received_messages: Set[str] = set()
        self.data_store: Dict[str, Any] = {}
        
        # Gossip protocol settings
        self.gossip_interval = 1.0  # 1 second
        self.failure_detection_interval = 5.0  # 5 seconds
        self.cleanup_interval = 30.0  # 30 seconds
        self.fanout = 3  # Number of nodes to gossip to
        self.failure_timeout = 15.0  # 15 seconds to detect failure
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "gossip_rounds": 0,
            "data_updates": 0,
            "membership_changes": 0
        }
        
        # Threading
        self.is_running = False
        self.lock = threading.RLock()
        self.gossip_thread: Optional[threading.Thread] = None
        self.failure_detector_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Add self to membership
        self.membership[self.node_id] = NodeInfo(
            node_id=self.node_id,
            host=self.host,
            port=self.port,
            state=self.state,
            last_seen=time.time(),
            metadata={"region": self.region}
        )
        
        logger.info(f"WhatsApp gossip node {node_id} initialized at {host}:{port} ({region})")
    
    def start(self) -> None:
        """Start the gossip node"""
        with self.lock:
            if self.is_running:
                return
            
            self.is_running = True
            
            # Start gossip thread
            self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
            self.gossip_thread.start()
            
            # Start failure detector thread
            self.failure_detector_thread = threading.Thread(target=self._failure_detector_loop, daemon=True)
            self.failure_detector_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            
            logger.info(f"Node {self.node_id} started gossip protocol")
    
    def stop(self) -> None:
        """Stop the gossip node"""
        with self.lock:
            if not self.is_running:
                return
            
            self.is_running = False
            
            # Update state to leaving
            self.state = NodeState.LEAVING
            self.membership[self.node_id].state = NodeState.LEAVING
            
            # Send leaving announcement
            self._broadcast_membership_change()
            
            # Wait for threads to finish
            if self.gossip_thread:
                self.gossip_thread.join(timeout=2)
            if self.failure_detector_thread:
                self.failure_detector_thread.join(timeout=2)
            if self.cleanup_thread:
                self.cleanup_thread.join(timeout=2)
            
            logger.info(f"Node {self.node_id} stopped gossip protocol")
    
    def join_cluster(self, seed_nodes: List[Tuple[str, str, int]]) -> None:
        """Join a cluster using seed nodes"""
        self.state = NodeState.JOINING
        self.membership[self.node_id].state = NodeState.JOINING
        
        # Contact seed nodes to get membership information
        for node_id, host, port in seed_nodes:
            if node_id != self.node_id:
                self._add_node_to_membership(node_id, host, port, NodeState.ALIVE)
        
        # Announce joining
        self._broadcast_membership_change()
        
        # Wait a bit for membership to propagate
        time.sleep(2)
        
        self.state = NodeState.ALIVE
        self.membership[self.node_id].state = NodeState.ALIVE
        
        logger.info(f"Node {self.node_id} joined cluster with {len(self.membership)} members")
    
    def leave_cluster(self) -> None:
        """Gracefully leave the cluster"""
        self.state = NodeState.LEAVING
        self.membership[self.node_id].state = NodeState.LEAVING
        
        # Announce leaving
        self._broadcast_membership_change()
        
        # Wait for announcement to propagate
        time.sleep(2)
        
        self.stop()
    
    def send_whatsapp_message(self, chat_id: str, message_content: str, message_type: str = "text") -> bool:
        """
        Send a WhatsApp-style message through the gossip network
        """
        message_id = self._generate_message_id()
        
        # Create message content
        whatsapp_message = {
            "type": "whatsapp_message",
            "chat_id": chat_id,
            "message_id": message_id,
            "content": message_content,
            "message_type": message_type,
            "sender_node": self.node_id,
            "timestamp": time.time(),
            "delivery_status": "sent"
        }
        
        # Store locally
        self.data_store[f"msg:{message_id}"] = whatsapp_message
        
        # Propagate through gossip
        return self._gossip_data_update("whatsapp_message", whatsapp_message)
    
    def update_user_status(self, user_id: str, status: str, status_message: str = "") -> bool:
        """
        Update user status (online, offline, typing, etc.)
        """
        status_update = {
            "type": "user_status",
            "user_id": user_id,
            "status": status,
            "status_message": status_message,
            "node_id": self.node_id,
            "timestamp": time.time()
        }
        
        # Store locally
        self.data_store[f"status:{user_id}"] = status_update
        
        # Propagate through gossip
        return self._gossip_data_update("user_status", status_update)
    
    def sync_chat_metadata(self, chat_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Sync chat metadata across the cluster
        """
        chat_sync = {
            "type": "chat_metadata",
            "chat_id": chat_id,
            "metadata": metadata,
            "node_id": self.node_id,
            "timestamp": time.time()
        }
        
        # Store locally
        self.data_store[f"chat:{chat_id}"] = chat_sync
        
        # Propagate through gossip
        return self._gossip_data_update("chat_metadata", chat_sync)
    
    def _add_node_to_membership(self, node_id: str, host: str, port: int, state: NodeState) -> None:
        """Add a node to the membership list"""
        with self.lock:
            if node_id not in self.membership:
                self.membership[node_id] = NodeInfo(
                    node_id=node_id,
                    host=host,
                    port=port,
                    state=state,
                    last_seen=time.time()
                )
                self.stats["membership_changes"] += 1
                logger.info(f"Added node {node_id} to membership")
    
    def _gossip_data_update(self, update_type: str, data: Dict[str, Any]) -> bool:
        """Gossip a data update to the cluster"""
        message_id = self._generate_message_id()
        
        gossip_content = {
            "update_type": update_type,
            "data": data,
            "origin_node": self.node_id,
            "timestamp": time.time()
        }
        
        message = GossipMessage(
            message_id=message_id,
            message_type=MessageType.DATA_UPDATE,
            sender_id=self.node_id,
            content=gossip_content,
            timestamp=time.time(),
            sequence_number=self._next_sequence_number()
        )
        
        return self._send_gossip_message(message)
    
    def _send_gossip_message(self, message: GossipMessage) -> bool:
        """Send a gossip message to random nodes"""
        with self.lock:
            # Add to our cache
            self.message_cache[message.message_id] = message
            self.received_messages.add(message.message_id)
            
            # Select random nodes to gossip to
            target_nodes = self._select_gossip_targets()
            
            if not target_nodes:
                return False
            
            # Simulate sending to target nodes
            success_count = 0
            for target_node_id in target_nodes:
                if self._simulate_message_send(target_node_id, message):
                    success_count += 1
            
            self.stats["messages_sent"] += len(target_nodes)
            self.stats["gossip_rounds"] += 1
            
            logger.debug(f"Node {self.node_id} sent gossip message {message.message_id} to {len(target_nodes)} nodes")
            
            return success_count > 0
    
    def _select_gossip_targets(self) -> List[str]:
        """Select random nodes to gossip to"""
        alive_nodes = [
            node_id for node_id, node_info in self.membership.items()
            if node_info.state == NodeState.ALIVE and node_id != self.node_id
        ]
        
        if len(alive_nodes) <= self.fanout:
            return alive_nodes
        
        return random.sample(alive_nodes, self.fanout)
    
    def _simulate_message_send(self, target_node_id: str, message: GossipMessage) -> bool:
        """Simulate sending a message to another node"""
        # In a real implementation, this would be actual network communication
        # For simulation, we assume 90% success rate with some network delay
        
        time.sleep(random.uniform(0.01, 0.05))  # Simulate network delay
        
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            # In real implementation, target node would receive and process the message
            # For simulation, we just log it
            logger.debug(f"Message {message.message_id} sent to {target_node_id}")
        
        return success
    
    def receive_gossip_message(self, message_data: Dict[str, Any]) -> bool:
        """Receive and process a gossip message"""
        try:
            message = GossipMessage.from_dict(message_data)
            
            with self.lock:
                # Check if we've already seen this message
                if message.message_id in self.received_messages:
                    return False
                
                # Check TTL
                if message.ttl <= 0:
                    logger.debug(f"Message {message.message_id} TTL expired")
                    return False
                
                # Mark as received
                self.received_messages.add(message.message_id)
                self.message_cache[message.message_id] = message
                self.stats["messages_received"] += 1
                
                # Process message based on type
                self._process_received_message(message)
                
                # Forward message with decreased TTL
                message.ttl -= 1
                if message.ttl > 0:
                    # Select fewer nodes for forwarding to prevent message explosion
                    forward_count = max(1, self.fanout // 2)
                    target_nodes = self._select_gossip_targets()[:forward_count]
                    
                    for target_node_id in target_nodes:
                        self._simulate_message_send(target_node_id, message)
                
                return True
                
        except Exception as e:
            logger.error(f"Error processing gossip message: {e}")
            return False
    
    def _process_received_message(self, message: GossipMessage) -> None:
        """Process a received gossip message"""
        if message.message_type == MessageType.DATA_UPDATE:
            self._process_data_update(message)
        elif message.message_type == MessageType.MEMBERSHIP:
            self._process_membership_update(message)
        elif message.message_type == MessageType.HEARTBEAT:
            self._process_heartbeat(message)
    
    def _process_data_update(self, message: GossipMessage) -> None:
        """Process a data update message"""
        content = message.content
        update_type = content.get("update_type")
        data = content.get("data", {})
        
        if update_type == "whatsapp_message":
            # Store WhatsApp message
            msg_id = data.get("message_id")
            if msg_id:
                self.data_store[f"msg:{msg_id}"] = data
                logger.info(f"Received WhatsApp message {msg_id} for chat {data.get('chat_id')}")
        
        elif update_type == "user_status":
            # Update user status
            user_id = data.get("user_id")
            if user_id:
                self.data_store[f"status:{user_id}"] = data
                logger.info(f"Updated status for user {user_id}: {data.get('status')}")
        
        elif update_type == "chat_metadata":
            # Update chat metadata
            chat_id = data.get("chat_id")
            if chat_id:
                self.data_store[f"chat:{chat_id}"] = data
                logger.info(f"Updated metadata for chat {chat_id}")
        
        self.stats["data_updates"] += 1
    
    def _process_membership_update(self, message: GossipMessage) -> None:
        """Process a membership update message"""
        content = message.content
        node_updates = content.get("membership", {})
        
        for node_id, node_data in node_updates.items():
            if node_id == self.node_id:
                continue
            
            node_info = NodeInfo.from_dict(node_data)
            
            with self.lock:
                existing_node = self.membership.get(node_id)
                
                if existing_node is None or node_info.version > existing_node.version:
                    self.membership[node_id] = node_info
                    self.stats["membership_changes"] += 1
                    
                    logger.info(f"Updated membership for node {node_id}: {node_info.state.value}")
    
    def _process_heartbeat(self, message: GossipMessage) -> None:
        """Process a heartbeat message"""
        sender_id = message.sender_id
        
        with self.lock:
            if sender_id in self.membership:
                self.membership[sender_id].last_seen = time.time()
                self.membership[sender_id].heartbeat_count += 1
                
                # Remove from suspected if it was suspected
                self.suspected_nodes.discard(sender_id)
    
    def _broadcast_membership_change(self) -> None:
        """Broadcast membership changes"""
        message_id = self._generate_message_id()
        
        membership_data = {}
        for node_id, node_info in self.membership.items():
            membership_data[node_id] = node_info.to_dict()
        
        message = GossipMessage(
            message_id=message_id,
            message_type=MessageType.MEMBERSHIP,
            sender_id=self.node_id,
            content={"membership": membership_data},
            timestamp=time.time(),
            sequence_number=self._next_sequence_number()
        )
        
        self._send_gossip_message(message)
    
    def _gossip_loop(self) -> None:
        """Main gossip loop"""
        while self.is_running:
            try:
                # Send heartbeat
                self._send_heartbeat()
                
                # Gossip random data
                self._gossip_random_data()
                
                time.sleep(self.gossip_interval)
                
            except Exception as e:
                logger.error(f"Error in gossip loop: {e}")
    
    def _send_heartbeat(self) -> None:
        """Send heartbeat to random nodes"""
        self.heartbeat_count += 1
        
        message_id = self._generate_message_id()
        message = GossipMessage(
            message_id=message_id,
            message_type=MessageType.HEARTBEAT,
            sender_id=self.node_id,
            content={
                "heartbeat_count": self.heartbeat_count,
                "timestamp": time.time()
            },
            timestamp=time.time(),
            sequence_number=self._next_sequence_number()
        )
        
        self._send_gossip_message(message)
    
    def _gossip_random_data(self) -> None:
        """Gossip random data items to maintain eventual consistency"""
        with self.lock:
            if not self.data_store:
                return
            
            # Select a random data item to gossip
            random_key = random.choice(list(self.data_store.keys()))
            random_data = self.data_store[random_key]
            
            # Determine update type based on key prefix
            if random_key.startswith("msg:"):
                update_type = "whatsapp_message"
            elif random_key.startswith("status:"):
                update_type = "user_status"
            elif random_key.startswith("chat:"):
                update_type = "chat_metadata"
            else:
                update_type = "generic"
            
            self._gossip_data_update(update_type, random_data)
    
    def _failure_detector_loop(self) -> None:
        """Failure detection loop"""
        while self.is_running:
            try:
                current_time = time.time()
                
                with self.lock:
                    for node_id, node_info in self.membership.items():
                        if node_id == self.node_id:
                            continue
                        
                        time_since_last_seen = current_time - node_info.last_seen
                        
                        if node_info.state == NodeState.ALIVE:
                            if time_since_last_seen > self.failure_timeout:
                                # Suspect the node
                                node_info.state = NodeState.SUSPECTED
                                self.suspected_nodes.add(node_id)
                                logger.warning(f"Node {node_id} suspected (no heartbeat for {time_since_last_seen:.1f}s)")
                        
                        elif node_info.state == NodeState.SUSPECTED:
                            if time_since_last_seen > self.failure_timeout * 2:
                                # Mark as failed
                                node_info.state = NodeState.FAILED
                                self.failed_nodes.add(node_id)
                                self.suspected_nodes.discard(node_id)
                                logger.error(f"Node {node_id} marked as failed")
                
                time.sleep(self.failure_detection_interval)
                
            except Exception as e:
                logger.error(f"Error in failure detection: {e}")
    
    def _cleanup_loop(self) -> None:
        """Cleanup old messages and failed nodes"""
        while self.is_running:
            try:
                current_time = time.time()
                
                with self.lock:
                    # Clean up old messages (older than 5 minutes)
                    old_messages = [
                        msg_id for msg_id, msg in self.message_cache.items()
                        if current_time - msg.timestamp > 300
                    ]
                    
                    for msg_id in old_messages:
                        del self.message_cache[msg_id]
                        self.received_messages.discard(msg_id)
                    
                    # Clean up failed nodes (after 10 minutes)
                    failed_to_remove = [
                        node_id for node_id, node_info in self.membership.items()
                        if node_info.state == NodeState.FAILED and 
                        current_time - node_info.last_seen > 600
                    ]
                    
                    for node_id in failed_to_remove:
                        del self.membership[node_id]
                        self.failed_nodes.discard(node_id)
                        logger.info(f"Removed failed node {node_id} from membership")
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return hashlib.md5(f"{self.node_id}:{time.time()}:{random.random()}".encode()).hexdigest()[:16]
    
    def _next_sequence_number(self) -> int:
        """Get next sequence number"""
        self.sequence_number += 1
        return self.sequence_number
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status"""
        with self.lock:
            alive_nodes = [n for n in self.membership.values() if n.state == NodeState.ALIVE]
            suspected_nodes = [n for n in self.membership.values() if n.state == NodeState.SUSPECTED]
            failed_nodes = [n for n in self.membership.values() if n.state == NodeState.FAILED]
            
            return {
                "node_id": self.node_id,
                "state": self.state.value,
                "membership_size": len(self.membership),
                "alive_nodes": len(alive_nodes),
                "suspected_nodes": len(suspected_nodes),
                "failed_nodes": len(failed_nodes),
                "data_items": len(self.data_store),
                "cached_messages": len(self.message_cache),
                "stats": self.stats.copy()
            }

def demonstrate_whatsapp_gossip_protocol():
    """
    Demonstrate WhatsApp-style gossip protocol
    """
    print("\n💬 WhatsApp-Style Gossip Protocol Demo")
    print("=" * 50)
    
    # Create WhatsApp gossip nodes
    nodes = []
    
    # Mumbai servers
    mumbai_nodes = [
        WhatsAppGossipNode("whatsapp-mum-01", "10.1.1.10", 5000, "mumbai"),
        WhatsAppGossipNode("whatsapp-mum-02", "10.1.1.11", 5000, "mumbai"),
    ]
    
    # Delhi servers
    delhi_nodes = [
        WhatsAppGossipNode("whatsapp-del-01", "10.2.1.10", 5000, "delhi"),
        WhatsAppGossipNode("whatsapp-del-02", "10.2.1.11", 5000, "delhi"),
    ]
    
    # Bangalore servers
    bangalore_nodes = [
        WhatsAppGossipNode("whatsapp-blr-01", "10.3.1.10", 5000, "bangalore"),
        WhatsAppGossipNode("whatsapp-blr-02", "10.3.1.11", 5000, "bangalore"),
    ]
    
    all_nodes = mumbai_nodes + delhi_nodes + bangalore_nodes
    
    print(f"\n🏢 Setting up WhatsApp gossip cluster...")
    for node in all_nodes:
        node.start()
        print(f"✅ Started node: {node.node_id} ({node.region})")
    
    # Create cluster by having nodes join
    print(f"\n🔗 Forming gossip cluster...")
    
    # Create seed node list
    seed_nodes = [(node.node_id, node.host, node.port) for node in all_nodes[:2]]
    
    # Have all nodes join the cluster
    for node in all_nodes:
        if node not in all_nodes[:2]:  # Skip seed nodes
            node.join_cluster(seed_nodes)
            time.sleep(0.5)
    
    # Allow cluster to stabilize
    print(f"\n⏳ Allowing cluster to stabilize...")
    time.sleep(5)
    
    # Display initial cluster status
    print(f"\n📊 Initial Cluster Status:")
    for node in all_nodes:
        status = node.get_cluster_status()
        print(f"  {status['node_id']}: {status['alive_nodes']} alive nodes, "
              f"{status['data_items']} data items")
    
    # Simulate WhatsApp message propagation
    print(f"\n💬 Simulating WhatsApp message propagation...")
    
    # Send messages from different nodes
    messages = [
        ("mumbai_friends", "Hey everyone! How's the weather in Mumbai?", "text"),
        ("delhi_family", "Just landed in Delhi airport! 🛬", "text"),
        ("bangalore_work", "Team meeting at 3 PM today", "text"),
        ("cricket_group", "India vs Australia match starting now! 🏏", "text"),
        ("food_lovers", "Found an amazing restaurant in Bangalore!", "text")
    ]
    
    for i, (chat_id, message, msg_type) in enumerate(messages):
        sender_node = all_nodes[i % len(all_nodes)]
        
        print(f"📤 {sender_node.node_id} sending message to {chat_id}: \"{message}\"")
        sender_node.send_whatsapp_message(chat_id, message, msg_type)
        time.sleep(1)
    
    # Simulate user status updates
    print(f"\n👤 Simulating user status updates...")
    
    status_updates = [
        ("user_rahul", "online", "Available"),
        ("user_priya", "typing", ""),
        ("user_arjun", "away", "In a meeting"),
        ("user_sneha", "online", ""),
        ("user_amit", "offline", "")
    ]
    
    for i, (user_id, status, status_msg) in enumerate(status_updates):
        update_node = all_nodes[i % len(all_nodes)]
        
        print(f"📱 {update_node.node_id} updating {user_id} status: {status}")
        update_node.update_user_status(user_id, status, status_msg)
        time.sleep(0.5)
    
    # Simulate chat metadata sync
    print(f"\n💾 Simulating chat metadata synchronization...")
    
    chat_metadata = [
        ("mumbai_friends", {"participants": 5, "admin": "user_rahul", "muted": False}),
        ("delhi_family", {"participants": 8, "admin": "user_priya", "muted": True}),
        ("bangalore_work", {"participants": 12, "admin": "user_arjun", "archived": False}),
    ]
    
    for i, (chat_id, metadata) in enumerate(chat_metadata):
        sync_node = all_nodes[i % len(all_nodes)]
        
        print(f"🔄 {sync_node.node_id} syncing metadata for {chat_id}")
        sync_node.sync_chat_metadata(chat_id, metadata)
        time.sleep(0.5)
    
    # Allow gossip to propagate
    print(f"\n🌊 Allowing gossip propagation...")
    time.sleep(10)
    
    # Check message propagation
    print(f"\n📋 Message Propagation Results:")
    for node in all_nodes:
        status = node.get_cluster_status()
        print(f"\n{node.node_id} ({node.region}):")
        print(f"  Data items: {status['data_items']}")
        print(f"  Messages sent: {status['stats']['messages_sent']}")
        print(f"  Messages received: {status['stats']['messages_received']}")
        print(f"  Gossip rounds: {status['stats']['gossip_rounds']}")
        
        # Show some data items
        with node.lock:
            msg_count = len([k for k in node.data_store.keys() if k.startswith("msg:")])
            status_count = len([k for k in node.data_store.keys() if k.startswith("status:")])
            chat_count = len([k for k in node.data_store.keys() if k.startswith("chat:")])
            
            print(f"  WhatsApp messages: {msg_count}")
            print(f"  User statuses: {status_count}")
            print(f"  Chat metadata: {chat_count}")
    
    # Simulate node failure
    print(f"\n💥 Simulating node failure...")
    failing_node = all_nodes[0]
    print(f"Stopping node: {failing_node.node_id}")
    failing_node.stop()
    
    # Wait for failure detection
    print(f"\n🔍 Waiting for failure detection...")
    time.sleep(20)
    
    # Check cluster status after failure
    print(f"\n📊 Cluster Status After Node Failure:")
    for node in all_nodes[1:]:  # Skip the failed node
        status = node.get_cluster_status()
        print(f"  {status['node_id']}: {status['alive_nodes']} alive, "
              f"{status['suspected_nodes']} suspected, {status['failed_nodes']} failed")
    
    # Test message propagation with failed node
    print(f"\n💬 Testing message propagation with failed node...")
    remaining_nodes = all_nodes[1:]
    test_node = remaining_nodes[0]
    
    test_node.send_whatsapp_message("post_failure_chat", 
                                   "This message sent after node failure", "text")
    
    time.sleep(5)
    
    # Check propagation
    print(f"\n📈 Post-failure propagation results:")
    for node in remaining_nodes:
        with node.lock:
            post_failure_msgs = [
                k for k in node.data_store.keys() 
                if k.startswith("msg:") and "post_failure" in str(node.data_store.get(k, {}))
            ]
            print(f"  {node.node_id}: {len(post_failure_msgs)} post-failure messages")
    
    # Production insights
    print(f"\n💡 Production Insights:")
    print(f"- Gossip protocol enables WhatsApp to propagate 100B+ messages daily")
    print(f"- Epidemic-style spreading ensures message delivery despite failures")
    print(f"- TTL prevents infinite message loops and controls network traffic")
    print(f"- Failure detection maintains cluster health and membership accuracy")
    print(f"- Eventually consistent: all nodes converge to same state over time")
    print(f"- Fanout parameter controls trade-off between speed and network load")
    print(f"- Regional deployment reduces latency for local users")
    print(f"- Self-healing: cluster continues operating despite node failures")
    print(f"- Scales to thousands of nodes with logarithmic message complexity")
    
    # Cleanup
    print(f"\n🧹 Cleaning up cluster...")
    for node in remaining_nodes:
        node.stop()
    
    print("WhatsApp gossip protocol demo completed!")

if __name__ == "__main__":
    demonstrate_whatsapp_gossip_protocol()