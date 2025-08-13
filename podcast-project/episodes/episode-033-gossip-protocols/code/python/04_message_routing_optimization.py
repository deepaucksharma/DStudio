#!/usr/bin/env python3
"""
Message Routing Optimization in Gossip Protocols
=================================================

Flipkart Delivery Network Optimization: जब millions of orders हों तो
कैसे efficiently gossip messages को route करें कि सब को जल्दी मिले?

This implements various optimization techniques for gossip-based routing:
- Push-Pull gossip
- Anti-entropy protocols
- Rumor mongering with dampening
- Adaptive fanout

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import math
import asyncio
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import heapq


class GossipMode(Enum):
    """Gossip protocol modes"""
    PUSH = "push"           # केवल भेजना
    PULL = "pull"           # केवल मांगना
    PUSH_PULL = "push_pull" # दोनों


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1    # Order cancellation
    HIGH = 2        # Delivery update
    NORMAL = 3      # Product updates
    LOW = 4         # Marketing messages


@dataclass
class DeliveryUpdate:
    """Flipkart delivery update message"""
    message_id: str
    order_id: str
    customer_id: str
    hub_id: str
    status: str
    timestamp: float
    priority: MessagePriority
    hop_count: int = 0
    version: int = 1
    size_bytes: int = 256  # Simulated message size


@dataclass
class GossipStats:
    """Statistics for gossip protocol performance"""
    total_messages: int = 0
    unique_messages: int = 0
    duplicate_messages: int = 0
    bytes_transmitted: int = 0
    convergence_time: float = 0.0
    network_efficiency: float = 0.0


class FlipkartDeliveryHub:
    """
    Flipkart Delivery Hub Node
    
    हर hub अपने nearby hubs के साथ delivery updates
    को efficiently share करता है
    """
    
    def __init__(self, hub_id: str, city: str, zone: str):
        self.hub_id = hub_id
        self.city = city
        self.zone = zone
        
        # Gossip configuration
        self.gossip_mode = GossipMode.PUSH_PULL
        self.base_fanout = 3
        self.adaptive_fanout = True
        self.max_fanout = 6
        
        # Message management
        self.messages: Dict[str, DeliveryUpdate] = {}
        self.version_vector: Dict[str, int] = {}  # For anti-entropy
        self.priority_queues: Dict[MessagePriority, List[DeliveryUpdate]] = {
            priority: [] for priority in MessagePriority
        }
        
        # Network topology
        self.neighbors: Set[str] = set()
        self.neighbor_weights: Dict[str, float] = {}  # Connection quality
        self.recent_contacts: Dict[str, float] = {}
        
        # Optimization features
        self.rumor_temperature: Dict[str, float] = {}  # For dampening
        self.bandwidth_limit = 1024 * 10  # 10KB per round
        self.congestion_control = True
        
        # Performance tracking
        self.stats = GossipStats()
        self.round_number = 0
        
        # Message filtering
        self.bloom_filter_size = 1000
        self.message_fingerprints: Set[str] = set()
        
    def add_neighbor(self, neighbor_id: str, weight: float = 1.0):
        """Add neighbor hub with connection quality weight"""
        self.neighbors.add(neighbor_id)
        self.neighbor_weights[neighbor_id] = weight
        self.version_vector[neighbor_id] = 0
        
    def create_delivery_update(self, order_id: str, customer_id: str, 
                              status: str, priority: MessagePriority) -> DeliveryUpdate:
        """Create new delivery update message"""
        message_id = f"{self.hub_id}_{order_id}_{int(time.time() * 1000)}"
        
        update = DeliveryUpdate(
            message_id=message_id,
            order_id=order_id,
            customer_id=customer_id,
            hub_id=self.hub_id,
            status=status,
            timestamp=time.time(),
            priority=priority
        )
        
        # Add to local storage
        self.add_message(update)
        return update
        
    def add_message(self, message: DeliveryUpdate):
        """Add message to local storage with priority queuing"""
        if message.message_id not in self.messages:
            self.messages[message.message_id] = message
            
            # Add to priority queue
            heapq.heappush(
                self.priority_queues[message.priority],
                (message.timestamp, message)
            )
            
            # Initialize rumor temperature
            self.rumor_temperature[message.message_id] = 1.0
            
            # Update stats
            self.stats.unique_messages += 1
            self.stats.bytes_transmitted += message.size_bytes
            
            # Add fingerprint for duplicate detection
            fingerprint = self._create_message_fingerprint(message)
            self.message_fingerprints.add(fingerprint)
            
    def _create_message_fingerprint(self, message: DeliveryUpdate) -> str:
        """Create compact fingerprint for message"""
        return f"{message.order_id}_{message.status}_{message.version}"
        
    def calculate_adaptive_fanout(self) -> int:
        """Calculate adaptive fanout based on network conditions"""
        if not self.adaptive_fanout:
            return self.base_fanout
            
        # Factors affecting fanout
        message_urgency = self._get_average_message_priority()
        network_congestion = self._estimate_network_congestion()
        neighbor_connectivity = len(self.neighbors) / 10.0  # Normalize
        
        # Adaptive formula
        urgency_factor = 2.0 if message_urgency <= 2 else 1.0  # High priority
        congestion_factor = 0.5 if network_congestion > 0.7 else 1.0
        connectivity_factor = min(neighbor_connectivity, 1.0)
        
        adaptive_fanout = int(
            self.base_fanout * urgency_factor * 
            congestion_factor * connectivity_factor
        )
        
        return min(max(adaptive_fanout, 1), self.max_fanout)
        
    def _get_average_message_priority(self) -> float:
        """Get average priority of recent messages"""
        recent_messages = [
            msg for msg in self.messages.values()
            if time.time() - msg.timestamp < 5.0
        ]
        
        if not recent_messages:
            return MessagePriority.NORMAL.value
            
        priorities = [msg.priority.value for msg in recent_messages]
        return sum(priorities) / len(priorities)
        
    def _estimate_network_congestion(self) -> float:
        """Estimate network congestion based on message delays"""
        current_time = time.time()
        recent_delays = []
        
        for neighbor_id, last_contact in self.recent_contacts.items():
            delay = current_time - last_contact
            if delay < 10.0:  # Recent contact
                recent_delays.append(delay)
                
        if not recent_delays:
            return 0.5  # Assume moderate congestion
            
        avg_delay = sum(recent_delays) / len(recent_delays)
        return min(avg_delay / 3.0, 1.0)  # Normalize to 0-1
        
    def select_gossip_targets(self, fanout: int, mode: GossipMode) -> List[str]:
        """Select optimal targets for gossip"""
        if not self.neighbors:
            return []
            
        # Weight-based selection considering:
        # 1. Connection quality
        # 2. Recent contact frequency
        # 3. Geographic proximity (simulated)
        
        neighbor_scores = {}
        current_time = time.time()
        
        for neighbor_id in self.neighbors:
            base_weight = self.neighbor_weights.get(neighbor_id, 1.0)
            
            # Penalty for recent contact (avoid redundancy)
            last_contact = self.recent_contacts.get(neighbor_id, 0)
            recency_penalty = max(0.1, 1.0 - (current_time - last_contact) / 5.0)
            
            # Bonus for high-quality connections
            quality_bonus = base_weight
            
            final_score = base_weight * recency_penalty * quality_bonus
            neighbor_scores[neighbor_id] = final_score
            
        # Select top candidates
        sorted_neighbors = sorted(
            neighbor_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        selected = [neighbor_id for neighbor_id, _ in sorted_neighbors[:fanout]]
        
        # Update recent contacts
        for neighbor_id in selected:
            self.recent_contacts[neighbor_id] = current_time
            
        return selected
        
    def select_messages_for_gossip(self, byte_limit: int) -> List[DeliveryUpdate]:
        """Select messages for gossip with priority and bandwidth limits"""
        selected_messages = []
        total_bytes = 0
        
        # Process by priority order
        for priority in MessagePriority:
            priority_queue = self.priority_queues[priority].copy()
            
            while priority_queue and total_bytes < byte_limit:
                timestamp, message = heapq.heappop(priority_queue)
                
                # Check rumor temperature (dampening)
                temp = self.rumor_temperature.get(message.message_id, 0)
                if temp < 0.1:  # Message is "cold"
                    continue
                    
                # Check message age
                if time.time() - message.timestamp > 30.0:  # 30 seconds max
                    continue
                    
                if total_bytes + message.size_bytes <= byte_limit:
                    selected_messages.append(message)
                    total_bytes += message.size_bytes
                    
                    # Cool down the rumor
                    self.rumor_temperature[message.message_id] *= 0.8
                    
        return selected_messages
        
    def create_push_payload(self, target_id: str) -> Dict:
        """Create PUSH payload for target"""
        fanout = self.calculate_adaptive_fanout()
        byte_limit = self.bandwidth_limit // fanout
        
        messages = self.select_messages_for_gossip(byte_limit)
        
        return {
            "type": "PUSH",
            "sender_id": self.hub_id,
            "target_id": target_id,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "order_id": msg.order_id,
                    "status": msg.status,
                    "priority": msg.priority.value,
                    "timestamp": msg.timestamp,
                    "version": msg.version
                }
                for msg in messages
            ],
            "version_vector": self.version_vector.copy(),
            "round_number": self.round_number
        }
        
    def create_pull_request(self, target_id: str) -> Dict:
        """Create PULL request for target"""
        return {
            "type": "PULL_REQUEST",
            "sender_id": self.hub_id,
            "target_id": target_id,
            "version_vector": self.version_vector.copy(),
            "message_fingerprints": list(self.message_fingerprints)[-50:]  # Recent fingerprints
        }
        
    def process_push_message(self, payload: Dict) -> int:
        """Process received PUSH message"""
        updates = 0
        
        for msg_data in payload.get("messages", []):
            # Check if message is new using fingerprint
            fingerprint = f"{msg_data['order_id']}_{msg_data['status']}_{msg_data['version']}"
            
            if fingerprint not in self.message_fingerprints:
                # Create message object
                message = DeliveryUpdate(
                    message_id=msg_data["message_id"],
                    order_id=msg_data["order_id"],
                    customer_id="",  # Not included in gossip for privacy
                    hub_id=payload["sender_id"],
                    status=msg_data["status"],
                    timestamp=msg_data["timestamp"],
                    priority=MessagePriority(msg_data["priority"]),
                    version=msg_data["version"]
                )
                
                self.add_message(message)
                updates += 1
                
        # Update version vector for anti-entropy
        sender_id = payload["sender_id"]
        sender_version = payload.get("version_vector", {}).get(sender_id, 0)
        self.version_vector[sender_id] = max(
            self.version_vector.get(sender_id, 0),
            sender_version
        )
        
        self.stats.total_messages += len(payload.get("messages", []))
        return updates
        
    def process_pull_request(self, payload: Dict) -> Dict:
        """Process PULL request and return response"""
        sender_id = payload["sender_id"]
        sender_fingerprints = set(payload.get("message_fingerprints", []))
        
        # Find messages that sender doesn't have
        missing_messages = []
        
        for message in self.messages.values():
            fingerprint = self._create_message_fingerprint(message)
            
            if fingerprint not in sender_fingerprints:
                # Check if message is worth sending
                temp = self.rumor_temperature.get(message.message_id, 0)
                if temp > 0.1 and time.time() - message.timestamp < 30.0:
                    missing_messages.append(message)
                    
        # Limit response size
        if len(missing_messages) > 10:
            # Prioritize by priority and recency
            missing_messages.sort(
                key=lambda x: (x.priority.value, -x.timestamp)
            )
            missing_messages = missing_messages[:10]
            
        return {
            "type": "PULL_RESPONSE",
            "sender_id": self.hub_id,
            "target_id": sender_id,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "order_id": msg.order_id,
                    "status": msg.status,
                    "priority": msg.priority.value,
                    "timestamp": msg.timestamp,
                    "version": msg.version
                }
                for msg in missing_messages
            ]
        }
        
    def gossip_round(self) -> Dict:
        """Perform optimized gossip round"""
        self.round_number += 1
        
        fanout = self.calculate_adaptive_fanout()
        targets = self.select_gossip_targets(fanout, self.gossip_mode)
        
        gossip_plan = {}
        
        for target_id in targets:
            if self.gossip_mode == GossipMode.PUSH:
                gossip_plan[target_id] = self.create_push_payload(target_id)
                
            elif self.gossip_mode == GossipMode.PULL:
                gossip_plan[target_id] = self.create_pull_request(target_id)
                
            elif self.gossip_mode == GossipMode.PUSH_PULL:
                # Alternate between push and pull
                if self.round_number % 2 == 0:
                    gossip_plan[target_id] = self.create_push_payload(target_id)
                else:
                    gossip_plan[target_id] = self.create_pull_request(target_id)
                    
        return gossip_plan
        
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        total_neighbors = len(self.neighbors)
        active_neighbors = len([
            n for n, last_contact in self.recent_contacts.items()
            if time.time() - last_contact < 10.0
        ])
        
        return {
            "hub_id": self.hub_id,
            "city": self.city,
            "total_messages": len(self.messages),
            "unique_messages": self.stats.unique_messages,
            "bytes_transmitted": self.stats.bytes_transmitted,
            "fanout": self.calculate_adaptive_fanout(),
            "active_neighbors": f"{active_neighbors}/{total_neighbors}",
            "avg_priority": self._get_average_message_priority(),
            "network_congestion": self._estimate_network_congestion()
        }


class FlipkartDeliveryNetwork:
    """Flipkart Delivery Network Simulator"""
    
    def __init__(self):
        self.hubs: Dict[str, FlipkartDeliveryHub] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_round = 0
        
    def create_delivery_network(self):
        """Create Indian delivery network topology"""
        # Major Indian cities with delivery hubs
        cities = [
            ("MUM", "Mumbai", "West"),
            ("DEL", "Delhi", "North"),
            ("BLR", "Bangalore", "South"),
            ("HYD", "Hyderabad", "South"),
            ("CHN", "Chennai", "South"),
            ("KOL", "Kolkata", "East"),
            ("PUN", "Pune", "West"),
            ("AHM", "Ahmedabad", "West"),
            ("SUK", "Surat", "West"),
            ("JPR", "Jaipur", "North"),
            ("LKO", "Lucknow", "North"),
            ("KAN", "Kanpur", "North"),
            ("NGP", "Nagpur", "Central"),
            ("IND", "Indore", "Central"),
            ("THN", "Thane", "West"),
            ("VDR", "Vadodara", "West"),
            ("AGR", "Agra", "North"),
            ("NAS", "Nashik", "West"),
            ("RJT", "Rajkot", "West"),
            ("MSR", "Mysore", "South")
        ]
        
        # Create hubs
        for code, city, zone in cities:
            self.hubs[code] = FlipkartDeliveryHub(code, city, zone)
            
        # Create connections based on geographic proximity and business logic
        connections = [
            # Mumbai cluster
            ("MUM", "PUN"), ("MUM", "THN"), ("MUM", "NAS"),
            # Delhi cluster  
            ("DEL", "JPR"), ("DEL", "LKO"), ("DEL", "KAN"), ("DEL", "AGR"),
            # South cluster
            ("BLR", "HYD"), ("BLR", "CHN"), ("BLR", "MSR"),
            # West corridor
            ("MUM", "AHM"), ("AHM", "SUK"), ("AHM", "RJT"), ("AHM", "VDR"),
            # Central connections
            ("NGP", "IND"), ("NGP", "MUM"), ("NGP", "DEL"),
            # Major intercity connections
            ("MUM", "DEL"), ("MUM", "BLR"), ("DEL", "BLR"),
            ("DEL", "KOL"), ("BLR", "CHN"), ("CHN", "KOL"),
            # Regional connections
            ("PUN", "AHM"), ("HYD", "CHN"), ("LKO", "KAN")
        ]
        
        for hub1, hub2 in connections:
            self.add_connection(hub1, hub2)
            
    def add_connection(self, hub1: str, hub2: str, weight: float = 1.0):
        """Add bidirectional connection between hubs"""
        if hub1 in self.hubs and hub2 in self.hubs:
            self.hubs[hub1].add_neighbor(hub2, weight)
            self.hubs[hub2].add_neighbor(hub1, weight)
            self.connections.append((hub1, hub2))


async def main():
    """Main simulation function"""
    print("🇮🇳 Flipkart Delivery Network Gossip Optimization Simulation")
    print("=" * 60)
    
    # Create network
    network = FlipkartDeliveryNetwork()
    network.create_delivery_network()
    
    print(f"Created network with {len(network.hubs)} delivery hubs")
    print(f"Total connections: {len(network.connections)}")
    
    # Inject some delivery updates
    updates = [
        ("MUM", "ORD001", "CUST001", "out_for_delivery", MessagePriority.HIGH),
        ("DEL", "ORD002", "CUST002", "shipped", MessagePriority.NORMAL),
        ("BLR", "ORD003", "CUST003", "cancelled", MessagePriority.CRITICAL),
        ("CHN", "ORD004", "CUST004", "delivered", MessagePriority.HIGH),
        ("PUN", "ORD005", "CUST005", "in_transit", MessagePriority.NORMAL),
    ]
    
    for hub_id, order_id, customer_id, status, priority in updates:
        if hub_id in network.hubs:
            hub = network.hubs[hub_id]
            hub.create_delivery_update(order_id, customer_id, status, priority)
            print(f"📦 Created {priority.name} update at {hub.city}: {order_id} - {status}")
    
    # Simulate gossip rounds
    for round_num in range(12):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Collect gossip plans
        all_plans = {}
        for hub_id, hub in network.hubs.items():
            plan = hub.gossip_round()
            if plan:
                all_plans[hub_id] = plan
                
        # Execute gossip
        total_updates = 0
        for sender_id, targets in all_plans.items():
            for target_id, payload in targets.items():
                if target_id in network.hubs:
                    target_hub = network.hubs[target_id]
                    
                    if payload["type"] == "PUSH":
                        updates = target_hub.process_push_message(payload)
                        total_updates += updates
                    elif payload["type"] == "PULL_REQUEST":
                        response = target_hub.process_pull_request(payload)
                        # Send response back
                        if response["messages"]:
                            push_payload = {
                                "type": "PUSH",
                                "sender_id": response["sender_id"],
                                "messages": response["messages"],
                                "version_vector": {},
                                "round_number": round_num
                            }
                            sender_hub = network.hubs[sender_id]
                            updates = sender_hub.process_push_message(push_payload)
                            total_updates += updates
                            
        print(f"Total message updates: {total_updates}")
        
        # Print metrics for key hubs
        key_hubs = ["MUM", "DEL", "BLR", "CHN"]
        for hub_id in key_hubs:
            if hub_id in network.hubs:
                metrics = network.hubs[hub_id].get_performance_metrics()
                print(f"{metrics['city']}: "
                      f"Messages={metrics['total_messages']}, "
                      f"Fanout={metrics['fanout']}, "
                      f"Congestion={metrics['network_congestion']:.2f}")
                      
        await asyncio.sleep(0.5)
        
    # Final convergence analysis
    print("\n📊 Final Network State:")
    total_unique_messages = sum(
        hub.stats.unique_messages for hub in network.hubs.values()
    )
    total_bytes = sum(
        hub.stats.bytes_transmitted for hub in network.hubs.values()
    )
    
    print(f"Total unique messages: {total_unique_messages}")
    print(f"Total bytes transmitted: {total_bytes / 1024:.1f} KB")
    print(f"Average messages per hub: {total_unique_messages / len(network.hubs):.1f}")


if __name__ == "__main__":
    asyncio.run(main())