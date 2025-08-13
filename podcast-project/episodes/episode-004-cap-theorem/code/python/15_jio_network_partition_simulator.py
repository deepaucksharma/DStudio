#!/usr/bin/env python3
"""
Jio Network Partition Simulator - Episode 4: CAP Theorem
=========================================================

भारतीय mobile network के realistic partition scenarios को simulate करता है
Jio, Airtel, Vi, BSNL networks के real-world partition patterns के साथ
CAP theorem के practical implications को demonstrate करता है

Features:
- Indian mobile network topology (Mumbai, Delhi, Bangalore circles)
- Real carrier patterns (Jio fiber vs 4G, BSNL MTNL legacy)
- Monsoon impact on network reliability
- Festival traffic load patterns
- Partition healing and split-brain scenarios
- Message delivery guarantees across partitions
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid

class CarrierType(Enum):
    JIO = "jio"           # Reliance Jio - fiber + 4G
    AIRTEL = "airtel"     # Bharti Airtel - strong 4G
    VI = "vi"             # Vodafone Idea - mixed network
    BSNL = "bsnl"         # BSNL - legacy + some 4G

class NetworkCircle(Enum):
    MUMBAI = "mumbai"
    DELHI = "delhi"
    BANGALORE = "bangalore"
    CHENNAI = "chennai"
    KOLKATA = "kolkata"
    HYDERABAD = "hyderabad"
    PUNE = "pune"
    AHMEDABAD = "ahmedabad"

class PartitionType(Enum):
    MONSOON = "monsoon"           # Heavy rain causing fiber cuts
    POWER_OUTAGE = "power"        # Power grid failures
    FIBER_CUT = "fiber_cut"       # Physical cable damage
    CONGESTION = "congestion"     # Network overload (festivals)
    MAINTENANCE = "maintenance"   # Planned maintenance
    TOWER_DOWN = "tower_down"     # Tower equipment failure

@dataclass
class NetworkNode:
    """Network node representing carrier infrastructure in a circle"""
    node_id: str
    circle: NetworkCircle
    carrier: CarrierType
    is_primary_gateway: bool = False
    connected_nodes: Set[str] = field(default_factory=set)
    is_online: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.now)
    message_queue: deque = field(default_factory=deque)
    partition_group: Optional[str] = None
    
    # Network characteristics by carrier
    reliability_score: float = field(init=False)
    latency_base_ms: int = field(init=False)
    bandwidth_mbps: int = field(init=False)
    
    def __post_init__(self):
        # Set characteristics based on carrier type
        carrier_profiles = {
            CarrierType.JIO: {"reliability": 0.95, "latency": 25, "bandwidth": 100},
            CarrierType.AIRTEL: {"reliability": 0.93, "latency": 30, "bandwidth": 80},
            CarrierType.VI: {"reliability": 0.88, "latency": 40, "bandwidth": 60},
            CarrierType.BSNL: {"reliability": 0.82, "latency": 60, "bandwidth": 40}
        }
        
        profile = carrier_profiles[self.carrier]
        self.reliability_score = profile["reliability"]
        self.latency_base_ms = profile["latency"]
        self.bandwidth_mbps = profile["bandwidth"]

@dataclass
class Message:
    """Message with delivery guarantees"""
    msg_id: str
    sender: str
    recipient: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    delivery_guarantee: str = "best_effort"  # best_effort, at_least_once, exactly_once
    max_retries: int = 3
    retry_count: int = 0
    is_delivered: bool = False
    delivery_path: List[str] = field(default_factory=list)

@dataclass
class PartitionEvent:
    """Network partition event"""
    event_id: str
    partition_type: PartitionType
    affected_circles: List[NetworkCircle]
    affected_carriers: List[CarrierType] 
    start_time: datetime
    estimated_duration_minutes: int
    actual_end_time: Optional[datetime] = None
    impact_description: str = ""
    
class JioNetworkPartitionSimulator:
    """Main simulator for Indian mobile network partitions"""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.active_partitions: List[PartitionEvent] = []
        self.message_history: List[Message] = []
        self.network_topology: Dict[str, Set[str]] = {}
        
        # Indian festival and event calendar affecting network load
        self.high_traffic_events = {
            "new_year": {"multiplier": 3.0, "duration_hours": 12},
            "diwali": {"multiplier": 4.0, "duration_hours": 24},
            "holi": {"multiplier": 2.5, "duration_hours": 8},
            "ipl_final": {"multiplier": 5.0, "duration_hours": 4},
            "election_results": {"multiplier": 6.0, "duration_hours": 6}
        }
        
        # Monsoon patterns by circle (June-September impact)
        self.monsoon_impact = {
            NetworkCircle.MUMBAI: 0.4,      # High impact - frequent flooding
            NetworkCircle.DELHI: 0.2,       # Moderate impact
            NetworkCircle.BANGALORE: 0.25,  # Moderate impact  
            NetworkCircle.CHENNAI: 0.35,    # High impact - coastal
            NetworkCircle.KOLKATA: 0.3,     # High impact - heavy rains
            NetworkCircle.HYDERABAD: 0.15,  # Lower impact
            NetworkCircle.PUNE: 0.3,        # Moderate-high impact
            NetworkCircle.AHMEDABAD: 0.1    # Low impact
        }
        
        self._setup_network_topology()
        self._initialize_monitoring()
    
    def _setup_network_topology(self):
        """Setup realistic Indian network topology"""
        
        # Major gateway cities and their connections
        gateway_connections = {
            NetworkCircle.MUMBAI: [NetworkCircle.PUNE, NetworkCircle.AHMEDABAD, NetworkCircle.DELHI],
            NetworkCircle.DELHI: [NetworkCircle.MUMBAI, NetworkCircle.BANGALORE, NetworkCircle.KOLKATA],
            NetworkCircle.BANGALORE: [NetworkCircle.CHENNAI, NetworkCircle.HYDERABAD, NetworkCircle.DELHI],
            NetworkCircle.CHENNAI: [NetworkCircle.BANGALORE, NetworkCircle.HYDERABAD],
            NetworkCircle.KOLKATA: [NetworkCircle.DELHI],
            NetworkCircle.HYDERABAD: [NetworkCircle.BANGALORE, NetworkCircle.CHENNAI],
            NetworkCircle.PUNE: [NetworkCircle.MUMBAI],
            NetworkCircle.AHMEDABAD: [NetworkCircle.MUMBAI]
        }
        
        # Create nodes for each carrier in each circle
        for circle in NetworkCircle:
            for carrier in CarrierType:
                node_id = f"{carrier.value}_{circle.value}"
                
                # Determine if this is a primary gateway
                is_gateway = circle in [NetworkCircle.MUMBAI, NetworkCircle.DELHI, NetworkCircle.BANGALORE]
                
                node = NetworkNode(
                    node_id=node_id,
                    circle=circle,
                    carrier=carrier,
                    is_primary_gateway=is_gateway
                )
                
                self.nodes[node_id] = node
        
        # Setup connections based on topology
        for circle, connected_circles in gateway_connections.items():
            for carrier in CarrierType:
                source_node = f"{carrier.value}_{circle.value}"
                
                # Connect to other carriers in same circle (local interconnect)
                for other_carrier in CarrierType:
                    if other_carrier != carrier:
                        target_node = f"{other_carrier.value}_{circle.value}"
                        self.nodes[source_node].connected_nodes.add(target_node)
                
                # Connect to same carrier in other circles
                for connected_circle in connected_circles:
                    target_node = f"{carrier.value}_{connected_circle.value}"
                    self.nodes[source_node].connected_nodes.add(target_node)
                    
                    # Make it bidirectional
                    if target_node in self.nodes:
                        self.nodes[target_node].connected_nodes.add(source_node)
        
        print(f"✅ Network topology setup: {len(self.nodes)} nodes created")
        
        # Print topology summary
        print("\n📡 Network Topology Summary:")
        for carrier in CarrierType:
            carrier_nodes = [n for n in self.nodes.keys() if n.startswith(carrier.value)]
            print(f"  {carrier.value.upper()}: {len(carrier_nodes)} nodes across {len(NetworkCircle)} circles")
    
    def _initialize_monitoring(self):
        """Initialize network monitoring and health checks"""
        self.start_time = datetime.now()
        self.metrics = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_lost": 0,
            "partition_events": 0,
            "healing_events": 0
        }
        
        print("📊 Network monitoring initialized")
    
    def create_partition(self, partition_type: PartitionType, 
                        affected_circles: List[NetworkCircle],
                        duration_minutes: int = 30) -> str:
        """Create a network partition event"""
        
        event_id = f"PARTITION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine affected carriers based on partition type
        if partition_type == PartitionType.FIBER_CUT:
            # Fiber cuts affect all carriers but Jio has better backup
            affected_carriers = [CarrierType.AIRTEL, CarrierType.VI, CarrierType.BSNL]
        elif partition_type == PartitionType.POWER_OUTAGE:
            # Power outages affect everyone
            affected_carriers = list(CarrierType)
        elif partition_type == PartitionType.MONSOON:
            # Monsoon affects terrestrial more than wireless, but BSNL worst
            affected_carriers = [CarrierType.BSNL, CarrierType.VI]
        elif partition_type == PartitionType.CONGESTION:
            # Congestion affects networks with lower capacity more
            affected_carriers = [CarrierType.VI, CarrierType.BSNL]
        else:
            affected_carriers = [random.choice(list(CarrierType))]
        
        # Create partition event
        partition_event = PartitionEvent(
            event_id=event_id,
            partition_type=partition_type,
            affected_circles=affected_circles,
            affected_carriers=affected_carriers,
            start_time=datetime.now(),
            estimated_duration_minutes=duration_minutes,
            impact_description=self._get_impact_description(partition_type, affected_circles)
        )
        
        # Apply partition to affected nodes
        affected_nodes = []
        for circle in affected_circles:
            for carrier in affected_carriers:
                node_id = f"{carrier.value}_{circle.value}"
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    node.is_online = False
                    node.partition_group = event_id
                    affected_nodes.append(node_id)
        
        self.active_partitions.append(partition_event)
        self.metrics["partition_events"] += 1
        
        print(f"\n🔥 PARTITION EVENT CREATED: {event_id}")
        print(f"   Type: {partition_type.value}")
        print(f"   Affected Circles: {[c.value for c in affected_circles]}")
        print(f"   Affected Carriers: {[c.value for c in affected_carriers]}")
        print(f"   Affected Nodes: {len(affected_nodes)}")
        print(f"   Estimated Duration: {duration_minutes} minutes")
        print(f"   Impact: {partition_event.impact_description}")
        
        return event_id
    
    def _get_impact_description(self, partition_type: PartitionType, 
                               affected_circles: List[NetworkCircle]) -> str:
        """Get human-readable impact description in Hindi/English mix"""
        
        circle_names = [c.value.title() for c in affected_circles]
        circles_str = ", ".join(circle_names)
        
        descriptions = {
            PartitionType.MONSOON: f"Heavy monsoon rains causing connectivity issues in {circles_str}. Expect service disruptions.",
            PartitionType.POWER_OUTAGE: f"Power grid failure in {circles_str}. Tower sites running on backup power.",
            PartitionType.FIBER_CUT: f"Fiber optic cable damage in {circles_str}. Traffic being rerouted through backup paths.",
            PartitionType.CONGESTION: f"Network congestion in {circles_str} due to high traffic. Peak usage detected.",
            PartitionType.MAINTENANCE: f"Planned maintenance activity in {circles_str}. Service may be intermittent.",
            PartitionType.TOWER_DOWN: f"Tower equipment failure in {circles_str}. Technicians dispatched for repair."
        }
        
        return descriptions.get(partition_type, f"Network issue in {circles_str}")
    
    def send_message(self, sender_circle: NetworkCircle, sender_carrier: CarrierType,
                     recipient_circle: NetworkCircle, recipient_carrier: CarrierType,
                     content: str, delivery_guarantee: str = "best_effort") -> str:
        """Send message across network with various delivery guarantees"""
        
        msg_id = str(uuid.uuid4())[:8]
        sender_node = f"{sender_carrier.value}_{sender_circle.value}"
        recipient_node = f"{recipient_carrier.value}_{recipient_circle.value}"
        
        message = Message(
            msg_id=msg_id,
            sender=sender_node,
            recipient=recipient_node,
            content=content,
            delivery_guarantee=delivery_guarantee
        )
        
        self.message_history.append(message)
        self.metrics["messages_sent"] += 1
        
        # Attempt delivery
        success, path = self._attempt_delivery(message)
        
        if success:
            message.is_delivered = True
            message.delivery_path = path
            self.metrics["messages_delivered"] += 1
            
            print(f"📱 MESSAGE DELIVERED: {msg_id}")
            print(f"   From: {sender_circle.value} ({sender_carrier.value})")
            print(f"   To: {recipient_circle.value} ({recipient_carrier.value})")
            print(f"   Path: {' → '.join(path)}")
            print(f"   Content: {content[:50]}...")
            
        else:
            if delivery_guarantee in ["at_least_once", "exactly_once"]:
                # Queue for retry
                sender_node_obj = self.nodes.get(sender_node)
                if sender_node_obj:
                    sender_node_obj.message_queue.append(message)
                    print(f"📫 MESSAGE QUEUED for retry: {msg_id}")
            else:
                self.metrics["messages_lost"] += 1
                print(f"❌ MESSAGE FAILED: {msg_id} (best effort - not retrying)")
        
        return msg_id
    
    def _attempt_delivery(self, message: Message) -> Tuple[bool, List[str]]:
        """Attempt to deliver message using available network paths"""
        
        sender_node = self.nodes.get(message.sender)
        recipient_node = self.nodes.get(message.recipient)
        
        if not sender_node or not recipient_node:
            return False, []
        
        # If sender or recipient is offline due to partition, delivery fails
        if not sender_node.is_online or not recipient_node.is_online:
            return False, []
        
        # Find path using BFS (considering partitions)
        path = self._find_path_bfs(message.sender, message.recipient)
        
        if path:
            # Calculate delivery success probability based on path reliability
            success_probability = self._calculate_path_reliability(path)
            
            # Add some randomness for realistic simulation
            if random.random() < success_probability:
                return True, path
        
        return False, []
    
    def _find_path_bfs(self, source: str, destination: str) -> List[str]:
        """Find path between nodes using BFS, considering partition states"""
        
        if source == destination:
            return [source]
        
        visited = set()
        queue = deque([(source, [source])])
        
        while queue:
            current_node, path = queue.popleft()
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            current_node_obj = self.nodes.get(current_node)
            if not current_node_obj or not current_node_obj.is_online:
                continue
            
            for neighbor in current_node_obj.connected_nodes:
                if neighbor == destination:
                    return path + [neighbor]
                
                neighbor_obj = self.nodes.get(neighbor)
                if neighbor_obj and neighbor_obj.is_online and neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def _calculate_path_reliability(self, path: List[str]) -> float:
        """Calculate overall reliability of a network path"""
        
        if not path:
            return 0.0
        
        total_reliability = 1.0
        
        for node_id in path:
            node = self.nodes.get(node_id)
            if node:
                # Base reliability
                reliability = node.reliability_score
                
                # Adjust for current conditions
                if datetime.now().month in [6, 7, 8, 9]:  # Monsoon season
                    monsoon_impact = self.monsoon_impact.get(node.circle, 0.1)
                    reliability *= (1 - monsoon_impact)
                
                total_reliability *= reliability
        
        return total_reliability
    
    def heal_partition(self, event_id: str):
        """Heal a network partition"""
        
        partition_event = None
        for event in self.active_partitions:
            if event.event_id == event_id:
                partition_event = event
                break
        
        if not partition_event:
            print(f"❌ Partition event {event_id} not found")
            return
        
        # Mark partition as healed
        partition_event.actual_end_time = datetime.now()
        
        # Bring affected nodes back online
        healed_nodes = []
        for node_id, node in self.nodes.items():
            if node.partition_group == event_id:
                node.is_online = True
                node.partition_group = None
                healed_nodes.append(node_id)
        
        # Remove from active partitions
        self.active_partitions.remove(partition_event)
        self.metrics["healing_events"] += 1
        
        duration = (partition_event.actual_end_time - partition_event.start_time).total_seconds() / 60
        
        print(f"\n✅ PARTITION HEALED: {event_id}")
        print(f"   Duration: {duration:.1f} minutes")
        print(f"   Nodes restored: {len(healed_nodes)}")
        print(f"   Type: {partition_event.partition_type.value}")
        
        # Process queued messages
        self._process_queued_messages()
    
    def _process_queued_messages(self):
        """Process messages that were queued during partition"""
        
        processed_count = 0
        
        for node in self.nodes.values():
            if not node.is_online:
                continue
                
            while node.message_queue:
                message = node.message_queue.popleft()
                
                if message.retry_count >= message.max_retries:
                    self.metrics["messages_lost"] += 1
                    print(f"❌ Message {message.msg_id} exceeded max retries")
                    continue
                
                message.retry_count += 1
                success, path = self._attempt_delivery(message)
                
                if success:
                    message.is_delivered = True
                    message.delivery_path = path
                    self.metrics["messages_delivered"] += 1
                    processed_count += 1
                    print(f"✅ Queued message delivered: {message.msg_id}")
                else:
                    # Requeue if not at max retries
                    if message.retry_count < message.max_retries:
                        node.message_queue.append(message)
        
        if processed_count > 0:
            print(f"📫 Processed {processed_count} queued messages")
    
    def get_network_status(self) -> Dict:
        """Get comprehensive network status"""
        
        # Count nodes by status
        total_nodes = len(self.nodes)
        online_nodes = sum(1 for node in self.nodes.values() if node.is_online)
        offline_nodes = total_nodes - online_nodes
        
        # Count by carrier
        carrier_status = {}
        for carrier in CarrierType:
            carrier_nodes = [node for node in self.nodes.values() if node.carrier == carrier]
            online_carrier_nodes = sum(1 for node in carrier_nodes if node.is_online)
            carrier_status[carrier.value] = {
                "total": len(carrier_nodes),
                "online": online_carrier_nodes,
                "availability": (online_carrier_nodes / len(carrier_nodes)) * 100 if carrier_nodes else 0
            }
        
        # Count by circle
        circle_status = {}
        for circle in NetworkCircle:
            circle_nodes = [node for node in self.nodes.values() if node.circle == circle]
            online_circle_nodes = sum(1 for node in circle_nodes if node.is_online)
            circle_status[circle.value] = {
                "total": len(circle_nodes),
                "online": online_circle_nodes,
                "availability": (online_circle_nodes / len(circle_nodes)) * 100 if circle_nodes else 0
            }
        
        # Message delivery stats
        total_messages = len(self.message_history)
        delivered_messages = sum(1 for msg in self.message_history if msg.is_delivered)
        delivery_rate = (delivered_messages / total_messages) * 100 if total_messages > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "network_health": {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "offline_nodes": offline_nodes,
                "overall_availability": (online_nodes / total_nodes) * 100
            },
            "carrier_status": carrier_status,
            "circle_status": circle_status,
            "active_partitions": len(self.active_partitions),
            "message_stats": {
                "total_sent": self.metrics["messages_sent"],
                "delivered": self.metrics["messages_delivered"],
                "lost": self.metrics["messages_lost"],
                "delivery_rate_percent": delivery_rate
            },
            "partition_events": {
                "total_events": self.metrics["partition_events"],
                "healing_events": self.metrics["healing_events"]
            }
        }
    
    def print_network_status(self):
        """Print formatted network status"""
        status = self.get_network_status()
        
        print(f"\n📊 Network Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Overall health
        health = status["network_health"]
        availability = health["overall_availability"]
        health_emoji = "🟢" if availability > 95 else "🟡" if availability > 85 else "🔴"
        
        print(f"{health_emoji} Network Health: {availability:.1f}% availability")
        print(f"   Total Nodes: {health['total_nodes']}")
        print(f"   Online: {health['online_nodes']} | Offline: {health['offline_nodes']}")
        
        # Carrier status
        print(f"\n📱 Carrier Status:")
        for carrier, stats in status["carrier_status"].items():
            availability = stats["availability"]
            status_emoji = "🟢" if availability > 95 else "🟡" if availability > 85 else "🔴"
            print(f"   {status_emoji} {carrier.upper()}: {availability:.1f}% "
                  f"({stats['online']}/{stats['total']} nodes)")
        
        # Circle status
        print(f"\n🗺️ Circle Status:")
        for circle, stats in status["circle_status"].items():
            availability = stats["availability"]
            status_emoji = "🟢" if availability > 95 else "🟡" if availability > 85 else "🔴"
            print(f"   {status_emoji} {circle.title()}: {availability:.1f}% "
                  f"({stats['online']}/{stats['total']} nodes)")
        
        # Active partitions
        if status["active_partitions"] > 0:
            print(f"\n🔥 Active Partitions: {status['active_partitions']}")
            for partition in self.active_partitions:
                duration = (datetime.now() - partition.start_time).total_seconds() / 60
                print(f"   • {partition.event_id}: {partition.partition_type.value} "
                      f"({duration:.0f} minutes)")
                print(f"     Affected: {[c.value for c in partition.affected_circles]}")
        else:
            print(f"\n✅ No Active Partitions")
        
        # Message statistics
        msg_stats = status["message_stats"]
        print(f"\n📈 Message Statistics:")
        print(f"   Total Sent: {msg_stats['total_sent']}")
        print(f"   Delivered: {msg_stats['delivered']}")
        print(f"   Lost: {msg_stats['lost']}")
        print(f"   Delivery Rate: {msg_stats['delivery_rate_percent']:.1f}%")
    
    def simulate_festival_traffic(self, event_name: str, duration_hours: int = 4):
        """Simulate high traffic during Indian festivals"""
        
        if event_name not in self.high_traffic_events:
            print(f"❌ Unknown event: {event_name}")
            return
        
        event_config = self.high_traffic_events[event_name]
        traffic_multiplier = event_config["multiplier"]
        
        print(f"\n🎉 FESTIVAL TRAFFIC SIMULATION: {event_name.title()}")
        print(f"   Traffic Multiplier: {traffic_multiplier}x normal")
        print(f"   Duration: {duration_hours} hours")
        
        # Simulate congestion-based partitions
        high_load_circles = [NetworkCircle.MUMBAI, NetworkCircle.DELHI, NetworkCircle.BANGALORE]
        
        for circle in high_load_circles:
            if random.random() < 0.3:  # 30% chance of congestion
                self.create_partition(
                    PartitionType.CONGESTION,
                    [circle],
                    duration_minutes=random.randint(15, 45)
                )
        
        # Simulate increased message traffic
        festival_messages = [
            "Happy Diwali! 🪔 Wishing you prosperity and joy!",
            "Diwali ki hardik shubhkamnayein! 🎆",
            "May this festival of lights bring happiness to your family! ✨",
            "दीवाली मुबारक! आपका जीवन खुशियों से भर जाए! 🪔",
            "Wishing you a very Happy Diwali! 🎊"
        ]
        
        # Generate random messages during festival
        for _ in range(random.randint(10, 20)):
            sender_circle = random.choice(list(NetworkCircle))
            sender_carrier = random.choice(list(CarrierType))
            recipient_circle = random.choice(list(NetworkCircle))
            recipient_carrier = random.choice(list(CarrierType))
            message = random.choice(festival_messages)
            
            self.send_message(sender_circle, sender_carrier, recipient_circle, 
                            recipient_carrier, message, "at_least_once")
            
            time.sleep(0.1)  # Small delay between messages

# Demo function to show realistic Indian network scenarios
def main():
    print("📡 Jio Network Partition Simulator - Indian Mobile Networks")
    print("=" * 65)
    
    # Initialize simulator
    simulator = JioNetworkPartitionSimulator()
    
    print(f"\n{'='*65}")
    print("📊 Initial Network Status:")
    print(f"{'='*65}")
    simulator.print_network_status()
    
    print(f"\n{'='*65}")
    print("🎭 Scenario 1: Mumbai Monsoon Impact")
    print(f"{'='*65}")
    
    # Simulate monsoon affecting Mumbai
    monsoon_partition = simulator.create_partition(
        PartitionType.MONSOON,
        [NetworkCircle.MUMBAI, NetworkCircle.PUNE],
        duration_minutes=45
    )
    
    # Try sending messages during partition
    print("\n📱 Attempting message delivery during monsoon...")
    
    messages = [
        ("Mumbai local train update: Services disrupted due to waterlogging", 
         NetworkCircle.MUMBAI, CarrierType.AIRTEL, NetworkCircle.DELHI, CarrierType.JIO),
        ("Office se ghar jaldi niklo - heavy rain expected", 
         NetworkCircle.MUMBAI, CarrierType.VI, NetworkCircle.PUNE, CarrierType.BSNL),
        ("Meeting postponed due to network issues", 
         NetworkCircle.PUNE, CarrierType.JIO, NetworkCircle.BANGALORE, CarrierType.AIRTEL)
    ]
    
    for content, src_circle, src_carrier, dst_circle, dst_carrier in messages:
        simulator.send_message(src_circle, src_carrier, dst_circle, dst_carrier, 
                             content, "at_least_once")
        time.sleep(1)
    
    simulator.print_network_status()
    
    print(f"\n{'='*65}")
    print("🔧 Healing Monsoon Partition...")
    print(f"{'='*65}")
    
    # Heal the partition
    simulator.heal_partition(monsoon_partition)
    simulator.print_network_status()
    
    print(f"\n{'='*65}")
    print("🎯 Scenario 2: Diwali Festival Traffic")
    print(f"{'='*65}")
    
    # Simulate festival traffic
    simulator.simulate_festival_traffic("diwali", 6)
    time.sleep(2)
    
    simulator.print_network_status()
    
    print(f"\n{'='*65}")
    print("⚡ Scenario 3: Power Outage in Delhi")
    print(f"{'='*65}")
    
    # Create power outage partition
    power_partition = simulator.create_partition(
        PartitionType.POWER_OUTAGE,
        [NetworkCircle.DELHI],
        duration_minutes=30
    )
    
    # Test different delivery guarantees
    print("\n📨 Testing different delivery guarantees...")
    
    test_messages = [
        ("Critical: Payment system alert", "best_effort"),
        ("Banking transaction notification", "at_least_once"), 
        ("Government service update", "exactly_once")
    ]
    
    for content, guarantee in test_messages:
        simulator.send_message(
            NetworkCircle.BANGALORE, CarrierType.JIO,
            NetworkCircle.DELHI, CarrierType.AIRTEL,
            content, guarantee
        )
        time.sleep(0.5)
    
    simulator.print_network_status()
    
    print(f"\n{'='*65}")
    print("🔄 Auto-healing All Partitions...")
    print(f"{'='*65}")
    
    # Heal all remaining partitions
    active_partitions = list(simulator.active_partitions)
    for partition in active_partitions:
        simulator.heal_partition(partition.event_id)
        time.sleep(1)
    
    print(f"\n{'='*65}")
    print("📈 Final Network Status & Statistics:")
    print(f"{'='*65}")
    
    simulator.print_network_status()
    
    # Export detailed status as JSON
    status = simulator.get_network_status()
    
    print(f"\n{'='*65}")
    print("💾 Network Status JSON Export (Sample):")
    print(f"{'='*65}")
    
    json_sample = json.dumps({
        "network_health": status["network_health"],
        "message_stats": status["message_stats"],
        "active_partitions": status["active_partitions"]
    }, indent=2)
    
    print(json_sample)
    
    print(f"\n{'='*65}")
    print("✅ Network Partition Simulation Complete!")
    print(f"{'='*65}")
    
    print("\n🎯 Key CAP Theorem Insights Demonstrated:")
    print("   - Consistency vs Availability trade-offs during partitions")
    print("   - Partition tolerance in real Indian network conditions")
    print("   - Message delivery guarantees under network failures")
    print("   - Realistic failure patterns (monsoon, power, congestion)")
    print("   - Multi-carrier redundancy strategies")
    
    print("\n💡 Production Insights for Indian Networks:")
    print("   - Jio has better partition tolerance due to fiber backbone")
    print("   - BSNL most vulnerable to power outages and monsoon")
    print("   - Festival traffic requires proactive scaling")
    print("   - Cross-carrier redundancy essential for critical services")
    print("   - Monsoon season planning crucial for Mumbai/Chennai operations")

if __name__ == "__main__":
    main()