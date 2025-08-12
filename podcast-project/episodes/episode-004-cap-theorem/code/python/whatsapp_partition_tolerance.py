#!/usr/bin/env python3
"""
WhatsApp-style Partition Tolerance System - Episode 4
Mobile messaging में partition tolerance का practical implementation

यह system demonstrate करता है कि कैसे WhatsApp जैसे messaging apps
network partitions को handle करते हैं Indian mobile network conditions में:

- Frequent network switches (Jio/Airtel/Vi/BSNL)
- Poor connectivity in rural areas
- Metro tunnel disconnections  
- International roaming scenarios
- Festival traffic congestion

CAP Trade-off: Availability + Partition Tolerance (AP System)
Messages should reach eventually, consistency can be relaxed.
"""

import time
import threading
import uuid
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import random
import hashlib
import queue

class MessageType(Enum):
    """WhatsApp message types"""
    TEXT = "text"                    # Plain text message
    IMAGE = "image"                  # Photo message
    AUDIO = "audio"                  # Voice note
    VIDEO = "video"                  # Video message
    DOCUMENT = "document"            # Document sharing
    LOCATION = "location"            # Location sharing
    CONTACT = "contact"              # Contact card
    STATUS_UPDATE = "status_update"  # WhatsApp status
    GROUP_ADMIN = "group_admin"      # Group admin messages

class MessageStatus(Enum):
    """Message delivery status - WhatsApp style"""
    SENDING = "sending"              # ⏳ Sending (clock icon)
    SENT = "sent"                   # ✓ Sent (single tick)
    DELIVERED = "delivered"          # ✓✓ Delivered (double tick)
    READ = "read"                   # ✓✓ Read (blue double tick)
    FAILED = "failed"               # ❌ Failed

class NetworkCarrier(Enum):
    """Indian mobile network carriers"""
    JIO = "jio"                     # Reliance Jio
    AIRTEL = "airtel"               # Bharti Airtel  
    VI = "vi"                       # Vodafone Idea
    BSNL = "bsnl"                   # Bharat Sanchar Nigam

class ConnectionStatus(Enum):
    """Network connection status"""
    CONNECTED = "connected"          # Full connectivity
    POOR_CONNECTION = "poor"        # Slow/intermittent  
    DISCONNECTED = "disconnected"   # No connectivity
    ROAMING = "roaming"             # International roaming

@dataclass
class WhatsAppMessage:
    """WhatsApp message structure"""
    message_id: str
    sender_id: str
    receiver_id: str  # Individual or group
    message_type: MessageType
    content: str
    timestamp: datetime
    status: MessageStatus = MessageStatus.SENDING
    is_group_message: bool = False
    group_id: Optional[str] = None
    reply_to_message_id: Optional[str] = None
    
    # Metadata for delivery
    attempts: int = 0
    max_attempts: int = 5
    encrypted: bool = True
    checksum: str = ""
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"MSG_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate message checksum for integrity"""
        data = f"{self.sender_id}{self.receiver_id}{self.content}{self.timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

@dataclass
class MobileUser:
    """WhatsApp user with mobile network simulation"""
    user_id: str
    phone_number: str
    name: str
    carrier: NetworkCarrier
    connection_status: ConnectionStatus = ConnectionStatus.CONNECTED
    location: str = "Mumbai"  # Indian city
    
    # Message storage
    sent_messages: List[WhatsAppMessage] = field(default_factory=list)
    received_messages: List[WhatsAppMessage] = field(default_factory=list)
    pending_messages: queue.Queue = field(default_factory=queue.Queue)
    
    # Network simulation
    last_seen: datetime = field(default_factory=datetime.now)
    message_queue_size: int = 0
    is_online: bool = True
    
    def go_offline(self, reason: str = "Network issue"):
        """Simulate user going offline"""
        self.is_online = False
        self.connection_status = ConnectionStatus.DISCONNECTED
        print(f"📱 {self.name} ({self.carrier.value.upper()}) went offline: {reason}")
    
    def come_online(self):
        """Simulate user coming back online"""
        self.is_online = True
        self.connection_status = ConnectionStatus.CONNECTED
        self.last_seen = datetime.now()
        print(f"📱 {self.name} ({self.carrier.value.upper()}) came online")

class WhatsAppNode:
    """
    WhatsApp server node - represents different data centers
    
    Real WhatsApp has servers in:
    - Singapore (for Asia-Pacific)
    - India (local presence)
    - US (primary)
    - Europe (GDPR compliance)
    """
    
    def __init__(self, node_id: str, location: str, region: str):
        self.node_id = node_id
        self.location = location  # Mumbai, Singapore, US-East, EU-West
        self.region = region
        
        # Message storage
        self.messages: Dict[str, WhatsAppMessage] = {}
        self.user_sessions: Dict[str, MobileUser] = {}
        self.message_queues: Dict[str, List[WhatsAppMessage]] = defaultdict(list)
        
        # Network partition simulation
        self.is_partitioned = False
        self.partition_start_time: Optional[datetime] = None
        self.connected_nodes: Set[str] = set()
        
        # Performance metrics
        self.messages_processed = 0
        self.messages_failed = 0
        self.sync_operations = 0
        
        # Background sync
        self.sync_queue = queue.Queue()
        self.is_running = True
        
        print(f"🌍 WhatsApp node initialized: {node_id} ({location})")

    def add_user_session(self, user: MobileUser):
        """Add user session to this node"""
        self.user_sessions[user.user_id] = user
        print(f"👤 User session added: {user.name} -> {self.node_id}")

    def store_message(self, message: WhatsAppMessage):
        """Store message in node"""
        self.messages[message.message_id] = message
        self.messages_processed += 1
        
        # Add to recipient's queue if they're offline or on different node
        if message.receiver_id in self.user_sessions:
            user = self.user_sessions[message.receiver_id]
            if not user.is_online:
                self.message_queues[message.receiver_id].append(message)

    def simulate_partition(self, duration: int = 10):
        """Simulate network partition"""
        self.is_partitioned = True
        self.partition_start_time = datetime.now()
        print(f"🌐 Node {self.node_id} partitioned for {duration}s")
        
        # Auto-recovery after duration
        def recover():
            time.sleep(duration)
            self.is_partitioned = False
            self.partition_start_time = None
            print(f"🔄 Node {self.node_id} partition recovered")
        
        threading.Thread(target=recover, daemon=True).start()

class WhatsAppPartitionTolerantSystem:
    """
    WhatsApp-style messaging system with partition tolerance
    
    Key features:
    1. Messages stored locally and sync when connected
    2. Multiple delivery attempts with exponential backoff
    3. Eventual consistency across nodes
    4. Offline message queuing
    5. Cross-node message replication
    """
    
    def __init__(self, num_nodes: int = 4):
        self.nodes: Dict[str, WhatsAppNode] = {}
        self.users: Dict[str, MobileUser] = {}
        
        # System metrics
        self.total_messages = 0
        self.delivered_messages = 0
        self.failed_messages = 0
        self.partition_events = 0
        self.sync_operations = 0
        
        # Network simulation
        self.network_issues = defaultdict(list)
        self.is_running = True
        
        # Initialize nodes (simulating global WhatsApp infrastructure)
        self._initialize_nodes()
        self._start_background_processes()
        
        print("💚 WhatsApp Partition Tolerant System initialized")
        print("🌍 Global infrastructure ready for Indian mobile networks")

    def _initialize_nodes(self):
        """Initialize WhatsApp nodes in different regions"""
        node_configs = [
            ("WA_MUMBAI", "Mumbai", "India"),
            ("WA_SINGAPORE", "Singapore", "APAC"), 
            ("WA_US_EAST", "Virginia", "Americas"),
            ("WA_EU_WEST", "Ireland", "Europe")
        ]
        
        for node_id, location, region in node_configs:
            self.nodes[node_id] = WhatsAppNode(node_id, location, region)
        
        # Set up node connections (all nodes connected by default)
        for node_id in self.nodes:
            for other_node_id in self.nodes:
                if node_id != other_node_id:
                    self.nodes[node_id].connected_nodes.add(other_node_id)

    def _start_background_processes(self):
        """Start background processes for message delivery and sync"""
        threading.Thread(target=self._message_delivery_worker, daemon=True).start()
        threading.Thread(target=self._sync_worker, daemon=True).start()
        threading.Thread(target=self._network_simulation_worker, daemon=True).start()
        
        print("🔄 Background processes started (delivery, sync, network simulation)")

    def add_user(self, user: MobileUser) -> str:
        """Add user to the system and assign to optimal node"""
        self.users[user.user_id] = user
        
        # Assign user to node based on location and load balancing
        optimal_node = self._get_optimal_node_for_user(user)
        optimal_node.add_user_session(user)
        
        return optimal_node.node_id

    def _get_optimal_node_for_user(self, user: MobileUser) -> WhatsAppNode:
        """Get optimal node for user based on location and load"""
        # Simplified: Indian users prefer Mumbai node, others get distributed
        if user.location in ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]:
            return self.nodes["WA_MUMBAI"]
        elif user.location in ["Singapore", "Jakarta", "Manila"]:
            return self.nodes["WA_SINGAPORE"] 
        elif user.location in ["New York", "San Francisco", "Toronto"]:
            return self.nodes["WA_US_EAST"]
        else:
            # Load balance among all nodes
            return min(self.nodes.values(), key=lambda n: len(n.user_sessions))

    def send_message(self, sender_id: str, receiver_id: str, content: str, 
                    message_type: MessageType = MessageType.TEXT) -> Tuple[bool, str]:
        """
        Send message with partition tolerance
        
        यह function message को send करने की कोशिश करता है,
        अगर network issue है तो local store करके बाद में sync करता है
        """
        self.total_messages += 1
        
        # Check if sender exists
        if sender_id not in self.users:
            self.failed_messages += 1
            return False, "Sender not found"
        
        if receiver_id not in self.users:
            self.failed_messages += 1
            return False, "Receiver not found"
        
        sender = self.users[sender_id]
        receiver = self.users[receiver_id]
        
        # Create message
        message = WhatsAppMessage(
            message_id="",  # Will be auto-generated
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        
        print(f"\n💬 Sending message from {sender.name} to {receiver.name}")
        print(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        print(f"   Sender network: {sender.carrier.value.upper()} ({sender.connection_status.value})")
        
        # Check sender's network status
        if sender.connection_status == ConnectionStatus.DISCONNECTED:
            # Store message locally for later sending
            message.status = MessageStatus.SENDING
            sender.sent_messages.append(message)
            print(f"   📤 Message queued locally (sender offline)")
            return True, "Message queued - will send when network available"
        
        # Try to deliver message immediately
        success, delivery_message = self._attempt_message_delivery(message)
        
        if success:
            self.delivered_messages += 1
            print(f"   ✅ Message delivered successfully")
            return True, delivery_message
        else:
            # Queue for retry
            self._queue_message_for_retry(message)
            print(f"   📬 Message queued for retry: {delivery_message}")
            return True, "Message acceptance confirmed - delivery in progress"

    def _attempt_message_delivery(self, message: WhatsAppMessage) -> Tuple[bool, str]:
        """
        Attempt to deliver message across the distributed system
        """
        message.attempts += 1
        
        # Find sender's node
        sender_node = self._find_user_node(message.sender_id)
        if not sender_node:
            return False, "Sender node not found"
        
        # Find receiver's node
        receiver_node = self._find_user_node(message.receiver_id)
        if not receiver_node:
            return False, "Receiver node not found"
        
        # Check if nodes are connected (no partition between them)
        if sender_node.is_partitioned or receiver_node.is_partitioned:
            return False, "Network partition detected"
        
        if sender_node.node_id != receiver_node.node_id:
            # Cross-node message delivery
            if receiver_node.node_id not in sender_node.connected_nodes:
                return False, "Inter-node connection unavailable"
        
        # Store message in both nodes for redundancy
        try:
            sender_node.store_message(message)
            if sender_node != receiver_node:
                receiver_node.store_message(message)
            
            # Update message status
            message.status = MessageStatus.SENT
            
            # Check if receiver is online
            receiver = self.users[message.receiver_id]
            if receiver.is_online and receiver.connection_status == ConnectionStatus.CONNECTED:
                # Immediate delivery
                receiver.received_messages.append(message)
                message.status = MessageStatus.DELIVERED
                
                # Simulate read receipt (30% chance of immediate read)
                if random.random() < 0.3:
                    time.sleep(random.uniform(0.1, 2.0))  # Reading time
                    message.status = MessageStatus.READ
                    print(f"   👁️  Message read by {receiver.name}")
            else:
                # Queue for when user comes online
                receiver_node.message_queues[message.receiver_id].append(message)
                print(f"   📥 Message queued for offline user {receiver.name}")
            
            return True, "Message delivered successfully"
        
        except Exception as e:
            message.status = MessageStatus.FAILED
            return False, f"Delivery failed: {e}"

    def _find_user_node(self, user_id: str) -> Optional[WhatsAppNode]:
        """Find which node a user is connected to"""
        for node in self.nodes.values():
            if user_id in node.user_sessions:
                return node
        return None

    def _queue_message_for_retry(self, message: WhatsAppMessage):
        """Queue message for retry with exponential backoff"""
        sender_node = self._find_user_node(message.sender_id)
        if sender_node:
            sender_node.sync_queue.put({
                'type': 'retry_message',
                'message': message,
                'retry_after': datetime.now() + timedelta(seconds=2 ** message.attempts)
            })

    def _message_delivery_worker(self):
        """Background worker for message delivery retries"""
        while self.is_running:
            try:
                for node in self.nodes.values():
                    if not node.sync_queue.empty():
                        try:
                            task = node.sync_queue.get_nowait()
                            
                            if task['type'] == 'retry_message':
                                message = task['message']
                                retry_time = task['retry_after']
                                
                                if datetime.now() >= retry_time:
                                    if message.attempts < message.max_attempts:
                                        success, _ = self._attempt_message_delivery(message)
                                        if not success:
                                            self._queue_message_for_retry(message)
                                    else:
                                        message.status = MessageStatus.FAILED
                                        self.failed_messages += 1
                                        print(f"   ❌ Message {message.message_id} failed after {message.attempts} attempts")
                                else:
                                    # Put back in queue for later
                                    node.sync_queue.put(task)
                        
                        except queue.Empty:
                            continue
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"❌ Message delivery worker error: {e}")
                time.sleep(1)

    def _sync_worker(self):
        """Background worker for cross-node synchronization"""
        while self.is_running:
            try:
                # Sync messages between connected nodes
                for node in self.nodes.values():
                    if not node.is_partitioned:
                        self._sync_node_messages(node)
                
                time.sleep(2)  # Sync every 2 seconds
                
            except Exception as e:
                print(f"❌ Sync worker error: {e}")
                time.sleep(5)

    def _sync_node_messages(self, node: WhatsAppNode):
        """Sync messages from one node to connected nodes"""
        for connected_node_id in node.connected_nodes:
            if connected_node_id in self.nodes:
                connected_node = self.nodes[connected_node_id]
                
                if not connected_node.is_partitioned:
                    # Sync recent messages
                    recent_messages = [
                        msg for msg in node.messages.values()
                        if datetime.now() - msg.timestamp < timedelta(hours=1)
                    ]
                    
                    for message in recent_messages:
                        if message.message_id not in connected_node.messages:
                            connected_node.messages[message.message_id] = message
                            node.sync_operations += 1

    def _network_simulation_worker(self):
        """Simulate real-world network issues for Indian mobile networks"""
        while self.is_running:
            try:
                # Random network issues
                if random.random() < 0.1:  # 10% chance every cycle
                    self._simulate_random_network_issue()
                
                # Random user connectivity changes
                if random.random() < 0.05:  # 5% chance
                    self._simulate_user_network_change()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"❌ Network simulation error: {e}")
                time.sleep(10)

    def _simulate_random_network_issue(self):
        """Simulate random network issues"""
        issue_types = [
            "node_partition",
            "carrier_outage", 
            "metro_tunnel",
            "festival_congestion"
        ]
        
        issue_type = random.choice(issue_types)
        
        if issue_type == "node_partition":
            # Random node partition
            node = random.choice(list(self.nodes.values()))
            if not node.is_partitioned:
                duration = random.randint(5, 30)
                node.simulate_partition(duration)
                self.partition_events += 1
        
        elif issue_type == "carrier_outage":
            # Specific carrier outage
            carrier = random.choice(list(NetworkCarrier))
            affected_users = [u for u in self.users.values() if u.carrier == carrier and u.is_online]
            
            if affected_users:
                print(f"📡 {carrier.value.upper()} network outage affecting {len(affected_users)} users")
                for user in affected_users:
                    user.go_offline(f"{carrier.value.upper()} network outage")
                
                # Recovery after some time
                def recover_carrier():
                    time.sleep(random.randint(10, 60))
                    for user in affected_users:
                        if not user.is_online:  # Only if still offline
                            user.come_online()
                    print(f"✅ {carrier.value.upper()} network restored")
                
                threading.Thread(target=recover_carrier, daemon=True).start()
        
        elif issue_type == "metro_tunnel":
            # Mumbai metro tunnel disconnection
            mumbai_users = [u for u in self.users.values() if u.location == "Mumbai" and u.is_online]
            affected_users = random.sample(mumbai_users, min(3, len(mumbai_users)))
            
            if affected_users:
                print(f"🚇 Metro tunnel: {len(affected_users)} Mumbai users disconnected")
                for user in affected_users:
                    user.go_offline("Metro tunnel")
                
                # Quick recovery (2-5 minutes typical)
                def recover_metro():
                    time.sleep(random.randint(10, 30))
                    for user in affected_users:
                        if not user.is_online:
                            user.come_online()
                    print("🚇 Metro users reconnected")
                
                threading.Thread(target=recover_metro, daemon=True).start()
        
        elif issue_type == "festival_congestion":
            # Festival traffic congestion (affects all carriers)
            all_online_users = [u for u in self.users.values() if u.is_online]
            affected_count = max(1, len(all_online_users) // 3)  # 33% affected
            affected_users = random.sample(all_online_users, affected_count)
            
            print(f"🎊 Festival congestion affecting {len(affected_users)} users")
            for user in affected_users:
                user.connection_status = ConnectionStatus.POOR_CONNECTION
                print(f"📱 {user.name} experiencing poor connection")
            
            # Recovery after festival rush
            def recover_festival():
                time.sleep(random.randint(30, 120))
                for user in affected_users:
                    if user.connection_status == ConnectionStatus.POOR_CONNECTION:
                        user.connection_status = ConnectionStatus.CONNECTED
                        print(f"📱 {user.name} connection restored")
                print("🎊 Festival congestion cleared")
            
            threading.Thread(target=recover_festival, daemon=True).start()

    def _simulate_user_network_change(self):
        """Simulate user network changes (carrier switching, roaming, etc.)"""
        online_users = [u for u in self.users.values() if u.is_online]
        if not online_users:
            return
        
        user = random.choice(online_users)
        
        change_types = ["carrier_switch", "roaming", "poor_connection", "comeback_online"]
        change_type = random.choice(change_types)
        
        if change_type == "carrier_switch":
            old_carrier = user.carrier
            new_carrier = random.choice([c for c in NetworkCarrier if c != old_carrier])
            user.carrier = new_carrier
            print(f"📡 {user.name} switched from {old_carrier.value.upper()} to {new_carrier.value.upper()}")
        
        elif change_type == "roaming":
            if user.connection_status != ConnectionStatus.ROAMING:
                user.connection_status = ConnectionStatus.ROAMING
                print(f"✈️  {user.name} is now roaming")
        
        elif change_type == "poor_connection":
            if user.connection_status == ConnectionStatus.CONNECTED:
                user.connection_status = ConnectionStatus.POOR_CONNECTION
                print(f"📶 {user.name} experiencing poor connection")
        
        elif change_type == "comeback_online":
            if not user.is_online:
                user.come_online()

    def simulate_group_message_flood(self, group_id: str, num_messages: int = 50):
        """
        Simulate group message flood scenario
        
        Indian WhatsApp groups often have message floods during:
        - Cricket matches (India vs Pakistan)
        - Festival celebrations (Diwali, Holi)
        - Political events
        - Wedding celebrations
        """
        print(f"\n🏏 GROUP MESSAGE FLOOD SIMULATION")
        print(f"   Group: {group_id}")
        print(f"   Messages: {num_messages}")
        print("   Scenario: India vs Pakistan cricket match commentary")
        
        # Get random users for the group
        available_users = list(self.users.keys())
        group_members = random.sample(available_users, min(10, len(available_users)))
        
        start_time = time.time()
        
        # Create flood of messages
        message_contents = [
            "What a shot by Kohli! 🏏",
            "Six runs! India is winning! 🇮🇳",
            "Pakistan fighting back 🏏",
            "This match is amazing! 😍",
            "Last over tension! 😰",
            "Dhoni finishes it off! MS Dhoni! 🏆",
            "India wins! Celebration time! 🎉",
            "What a match! Heart attack stuff! ❤️",
            "Kohli man of the match 👑",
            "Next match when? Can't wait! 🤔"
        ]
        
        # Send messages rapidly
        for i in range(num_messages):
            sender = random.choice(group_members)
            content = random.choice(message_contents)
            
            # Simulate rapid messaging
            for receiver in group_members:
                if receiver != sender:
                    self.send_message(sender, receiver, f"{content} #{i+1}", MessageType.TEXT)
            
            # Small delay between messages
            time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 GROUP FLOOD RESULTS:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Messages sent: {num_messages * len(group_members)}")
        print(f"   Rate: {(num_messages * len(group_members))/duration:.1f} messages/second")

    def simulate_cross_border_messaging(self):
        """
        Simulate cross-border messaging with network challenges
        
        Common scenarios:
        - India to Pakistan (political tensions affecting connectivity)
        - India to Middle East (oil workers)
        - India to US (IT professionals)
        - India to UK (students/professionals)
        """
        print(f"\n🌏 CROSS-BORDER MESSAGING SIMULATION")
        
        # Create international users
        international_users = [
            MobileUser("USER_PAK", "+923001234567", "Ahmed Khan", NetworkCarrier.JIO, location="Karachi"),
            MobileUser("USER_UAE", "+971501234567", "Ravi Sharma", NetworkCarrier.AIRTEL, location="Dubai"),
            MobileUser("USER_USA", "+1234567890", "Priya Patel", NetworkCarrier.VI, location="San Francisco"),
            MobileUser("USER_UK", "+447123456789", "Rohit Singh", NetworkCarrier.BSNL, location="London")
        ]
        
        for user in international_users:
            self.users[user.user_id] = user
            node = self._get_optimal_node_for_user(user)
            node.add_user_session(user)
        
        # Indian user sending messages internationally
        indian_user = random.choice([u for u in self.users.values() if u.location in ["Mumbai", "Delhi", "Bangalore"]])
        
        print(f"   Indian user: {indian_user.name} ({indian_user.location})")
        
        # Send messages to different countries
        for intl_user in international_users:
            message_content = f"Hello from {indian_user.location}! How are things in {intl_user.location}?"
            
            print(f"   📤 Sending to {intl_user.name} in {intl_user.location}...")
            success, result = self.send_message(indian_user.user_id, intl_user.user_id, message_content)
            print(f"      Result: {result}")
            
            time.sleep(1)  # Delay between international messages

    def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        active_nodes = sum(1 for node in self.nodes.values() if not node.is_partitioned)
        online_users = sum(1 for user in self.users.values() if user.is_online)
        
        success_rate = 0
        if self.total_messages > 0:
            success_rate = (self.delivered_messages / self.total_messages) * 100
        
        total_stored_messages = sum(len(node.messages) for node in self.nodes.values())
        total_queued_messages = sum(len(node.message_queues) for node in self.nodes.values())
        
        return {
            "total_messages": self.total_messages,
            "delivered_messages": self.delivered_messages,
            "failed_messages": self.failed_messages,
            "success_rate": f"{success_rate:.2f}%",
            "active_nodes": f"{active_nodes}/{len(self.nodes)}",
            "online_users": f"{online_users}/{len(self.users)}",
            "partition_events": self.partition_events,
            "sync_operations": self.sync_operations,
            "stored_messages": total_stored_messages,
            "queued_messages": total_queued_messages
        }

    def print_user_status(self):
        """Print status of all users"""
        print(f"\n👥 USER STATUS REPORT")
        for user in self.users.values():
            status_emoji = "🟢" if user.is_online else "🔴"
            carrier_emoji = {
                NetworkCarrier.JIO: "🔵",
                NetworkCarrier.AIRTEL: "🔴", 
                NetworkCarrier.VI: "🟣",
                NetworkCarrier.BSNL: "🟡"
            }.get(user.carrier, "⚪")
            
            print(f"   {status_emoji} {user.name} ({user.location}) - {carrier_emoji} {user.carrier.value.upper()}")
            print(f"      Connection: {user.connection_status.value}")
            print(f"      Messages sent: {len(user.sent_messages)}")
            print(f"      Messages received: {len(user.received_messages)}")

def main():
    """
    Main demonstration - WhatsApp partition tolerance scenarios
    """
    print("💚 WhatsApp Partition Tolerance System Demo")
    print("=" * 55)
    
    # Initialize system
    whatsapp = WhatsAppPartitionTolerantSystem()
    
    # Add sample Indian users with different carriers
    indian_users = [
        MobileUser("USER001", "+919876543210", "Rajesh Kumar", NetworkCarrier.JIO, location="Mumbai"),
        MobileUser("USER002", "+919123456789", "Priya Sharma", NetworkCarrier.AIRTEL, location="Delhi"),
        MobileUser("USER003", "+919555666777", "Amit Patel", NetworkCarrier.VI, location="Bangalore"),
        MobileUser("USER004", "+919888999000", "Sunita Singh", NetworkCarrier.BSNL, location="Chennai"),
        MobileUser("USER005", "+919111222333", "Rohit Gupta", NetworkCarrier.JIO, location="Hyderabad"),
        MobileUser("USER006", "+919444555666", "Anjali Desai", NetworkCarrier.AIRTEL, location="Pune"),
    ]
    
    for user in indian_users:
        whatsapp.add_user(user)
    
    time.sleep(2)  # Let system initialize
    
    # Scenario 1: Normal messaging
    print("\n💬 SCENARIO 1: Normal Messaging")
    whatsapp.send_message("USER001", "USER002", "Hey Priya! How's Delhi weather?", MessageType.TEXT)
    whatsapp.send_message("USER003", "USER004", "Meeting postponed to tomorrow", MessageType.TEXT)
    whatsapp.send_message("USER005", "USER001", "Flight landed safely in Mumbai 🛬", MessageType.TEXT)
    
    time.sleep(3)
    
    # Scenario 2: Network partition simulation
    print("\n🌐 SCENARIO 2: Network Partition Handling")
    mumbai_node = whatsapp.nodes["WA_MUMBAI"]
    mumbai_node.simulate_partition(10)
    
    # Try sending messages during partition
    time.sleep(1)
    whatsapp.send_message("USER001", "USER006", "Are you getting my messages?", MessageType.TEXT)
    whatsapp.send_message("USER002", "USER001", "Network seems slow today", MessageType.TEXT)
    
    time.sleep(12)  # Wait for partition to recover
    
    # Scenario 3: User connectivity issues
    print("\n📱 SCENARIO 3: User Network Issues")
    whatsapp.users["USER003"].go_offline("Metro tunnel in Bangalore")
    whatsapp.send_message("USER004", "USER003", "Call me when you see this", MessageType.TEXT)
    
    time.sleep(3)
    whatsapp.users["USER003"].come_online()
    
    # Scenario 4: Group message flood
    print("\n🏏 SCENARIO 4: Group Message Flood")
    whatsapp.simulate_group_message_flood("CRICKET_FANS", 20)
    
    # Scenario 5: Cross-border messaging  
    print("\n🌍 SCENARIO 5: International Messaging")
    whatsapp.simulate_cross_border_messaging()
    
    # Let system process for a while
    print("\n⏳ Letting system process messages and handle network issues...")
    time.sleep(10)
    
    # Final metrics and status
    print("\n📊 FINAL SYSTEM METRICS")
    metrics = whatsapp.get_system_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    whatsapp.print_user_status()
    
    print("\n✅ WhatsApp Partition Tolerance demo completed!")
    print("Key learnings:")
    print("1. Messaging apps prioritize availability over consistency")
    print("2. Messages are stored locally and synced when possible")
    print("3. Network partitions are handled with graceful degradation")
    print("4. Multiple delivery attempts with exponential backoff")
    print("5. Cross-node replication ensures message durability")
    print("6. Indian mobile networks require robust partition tolerance")
    print("7. Group messaging creates high load scenarios")
    print("8. International messaging faces additional challenges")

if __name__ == "__main__":
    main()