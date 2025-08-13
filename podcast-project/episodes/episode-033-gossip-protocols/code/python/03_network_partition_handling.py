#!/usr/bin/env python3
"""
Network Partition Handling in Gossip Protocols
===============================================

Mumbai Monsoon Network Splits: जब बारिश में कुछ areas cut-off हो जाते हैं
तो gossip protocol कैसे handle करता है network partitions को?

This demonstrates how gossip protocols behave during network partitions
and how they heal once connectivity is restored.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import asyncio
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class PartitionState(Enum):
    """Network partition states"""
    CONNECTED = "connected"
    PARTITIONED = "partitioned"
    HEALING = "healing"


@dataclass
class NetworkMessage:
    """Network message with routing info"""
    message_id: str
    content: str
    sender_id: str
    timestamp: float
    hop_count: int = 0
    max_hops: int = 10


@dataclass
class PartitionEvent:
    """Network partition event"""
    event_type: str  # "split" or "merge"
    affected_nodes: List[str]
    timestamp: float
    cause: str


class MonsoonAffectedNode:
    """
    Mumbai Area Node affected by Monsoon
    
    हर area एक node है जो monsoon के दौरान अपने neighboring areas
    के साथ connectivity lose कर सकता है
    """
    
    def __init__(self, node_id: str, area_name: str, flood_prone: bool = False):
        self.node_id = node_id
        self.area_name = area_name
        self.flood_prone = flood_prone
        
        # Network connectivity
        self.neighbors: Set[str] = set()
        self.active_connections: Set[str] = set()
        self.partition_state = PartitionState.CONNECTED
        
        # Message handling
        self.messages: Dict[str, NetworkMessage] = {}
        self.message_buffer: List[NetworkMessage] = []  # Messages during partition
        self.sequence_number = 0
        
        # Partition detection
        self.last_contact: Dict[str, float] = {}
        self.partition_timeout = 3.0  # seconds
        self.known_partitions: Set[str] = set()
        
        # Metrics
        self.messages_sent = 0
        self.messages_received = 0
        self.partition_events: List[PartitionEvent] = []
        
        # Gossip settings
        self.gossip_interval = 1.0
        self.gossip_fanout = 2
        
    def add_neighbor(self, neighbor_id: str):
        """Add neighboring area"""
        self.neighbors.add(neighbor_id)
        self.active_connections.add(neighbor_id)
        self.last_contact[neighbor_id] = time.time()
        
    def simulate_monsoon_flooding(self, duration: float = 5.0):
        """Simulate monsoon flooding causing network partition"""
        if self.flood_prone:
            print(f"🌧️ {self.area_name} flooded! Network connections lost.")
            self.partition_state = PartitionState.PARTITIONED
            self.active_connections.clear()
            
            # Log partition event
            event = PartitionEvent(
                event_type="split",
                affected_nodes=[self.node_id],
                timestamp=time.time(),
                cause="monsoon_flooding"
            )
            self.partition_events.append(event)
            
            # Schedule healing
            asyncio.create_task(self._heal_after_monsoon(duration))
            
    async def _heal_after_monsoon(self, delay: float):
        """Heal network connections after monsoon"""
        await asyncio.sleep(delay)
        
        print(f"☀️ {self.area_name} connectivity restored!")
        self.partition_state = PartitionState.HEALING
        
        # Restore connections gradually
        for neighbor in self.neighbors:
            await asyncio.sleep(0.5)  # Gradual restoration
            self.active_connections.add(neighbor)
            self.last_contact[neighbor] = time.time()
            
        self.partition_state = PartitionState.CONNECTED
        
        # Log healing event
        event = PartitionEvent(
            event_type="merge",
            affected_nodes=[self.node_id],
            timestamp=time.time(),
            cause="monsoon_ended"
        )
        self.partition_events.append(event)
        
        # Process buffered messages
        await self._process_buffered_messages()
        
    async def _process_buffered_messages(self):
        """Process messages buffered during partition"""
        print(f"📥 {self.area_name} processing {len(self.message_buffer)} buffered messages")
        
        for message in self.message_buffer:
            await self._handle_message(message)
            
        self.message_buffer.clear()
        
    def detect_partitions(self):
        """Detect network partitions based on timeouts"""
        current_time = time.time()
        newly_partitioned = set()
        
        for neighbor_id in self.neighbors:
            if neighbor_id in self.active_connections:
                last_contact = self.last_contact.get(neighbor_id, 0)
                
                if current_time - last_contact > self.partition_timeout:
                    # Neighbor seems partitioned
                    self.active_connections.discard(neighbor_id)
                    newly_partitioned.add(neighbor_id)
                    self.known_partitions.add(neighbor_id)
                    
        if newly_partitioned:
            print(f"🔌 {self.area_name} detected partition from: {newly_partitioned}")
            
    def create_message(self, content: str) -> NetworkMessage:
        """Create new message"""
        self.sequence_number += 1
        message_id = f"{self.node_id}_{self.sequence_number}_{int(time.time() * 1000)}"
        
        return NetworkMessage(
            message_id=message_id,
            content=content,
            sender_id=self.node_id,
            timestamp=time.time()
        )
        
    async def _handle_message(self, message: NetworkMessage):
        """Handle received message"""
        if message.message_id in self.messages:
            return  # Duplicate
            
        self.messages[message.message_id] = message
        self.messages_received += 1
        
        print(f"📨 {self.area_name} received: {message.content[:50]}...")
        
        # Forward message if within hop limit
        if message.hop_count < message.max_hops:
            await self._forward_message(message)
            
    async def _forward_message(self, message: NetworkMessage):
        """Forward message to connected neighbors"""
        if self.partition_state == PartitionState.PARTITIONED:
            # Buffer message for later forwarding
            self.message_buffer.append(message)
            return
            
        # Create forwarded copy
        forwarded_message = NetworkMessage(
            message_id=message.message_id,
            content=message.content,
            sender_id=message.sender_id,
            timestamp=message.timestamp,
            hop_count=message.hop_count + 1,
            max_hops=message.max_hops
        )
        
        # Select targets for forwarding
        targets = self.select_gossip_targets()
        
        for target_id in targets:
            if target_id != message.sender_id:  # Don't send back to sender
                # Simulate sending (would be handled by network simulator)
                pass
                
    def select_gossip_targets(self) -> List[str]:
        """Select targets for gossip considering connectivity"""
        if self.partition_state == PartitionState.PARTITIONED:
            return []
            
        connected_neighbors = list(self.active_connections)
        random.shuffle(connected_neighbors)
        
        return connected_neighbors[:self.gossip_fanout]
        
    def gossip_round(self) -> Dict[str, List[NetworkMessage]]:
        """Perform gossip round"""
        self.detect_partitions()
        
        if self.partition_state == PartitionState.PARTITIONED:
            return {}
            
        # Select messages to gossip
        recent_messages = [
            msg for msg in self.messages.values()
            if time.time() - msg.timestamp < 10.0  # Last 10 seconds
        ]
        
        if not recent_messages:
            return {}
            
        # Select targets
        targets = self.select_gossip_targets()
        
        gossip_plan = {}
        for target_id in targets:
            gossip_plan[target_id] = recent_messages[:3]  # Limit message count
            self.messages_sent += len(recent_messages[:3])
            
        return gossip_plan
        
    def update_contact_time(self, neighbor_id: str):
        """Update last contact time with neighbor"""
        self.last_contact[neighbor_id] = time.time()
        
        # Restore connection if it was marked as partitioned
        if neighbor_id in self.known_partitions:
            self.known_partitions.remove(neighbor_id)
            self.active_connections.add(neighbor_id)
            print(f"🔗 {self.area_name} restored connection to {neighbor_id}")
            
    def get_network_view(self) -> Dict:
        """Get current network view"""
        return {
            "node_id": self.node_id,
            "area": self.area_name,
            "state": self.partition_state.value,
            "total_neighbors": len(self.neighbors),
            "active_connections": len(self.active_connections),
            "known_partitions": len(self.known_partitions),
            "messages_count": len(self.messages),
            "buffered_messages": len(self.message_buffer)
        }
        
    def get_partition_history(self) -> List[Dict]:
        """Get history of partition events"""
        return [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "cause": event.cause,
                "affected_nodes": event.affected_nodes
            }
            for event in self.partition_events
        ]


class MumbaiMonsoonNetwork:
    """Mumbai City Network during Monsoon Season"""
    
    def __init__(self):
        self.nodes: Dict[str, MonsoonAffectedNode] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_round = 0
        self.global_messages: List[NetworkMessage] = []
        
    def create_mumbai_monsoon_topology(self):
        """Create Mumbai city network with flood-prone areas"""
        # Mumbai areas with flood proneness
        areas = [
            ("BAN", "Bandra", False),
            ("JUH", "Juhu", True),      # Near sea, flood prone
            ("VLE", "Vile Parle", False),
            ("ADH", "Andheri", True),   # Low lying area
            ("MLD", "Malad", True),     # Creek area, flood prone
            ("BVI", "Borivali", False),
            ("DHR", "Dahisar", True),   # Near river
            ("GHT", "Ghatkopar", False),
            ("VKH", "Vikhroli", True),  # Creek area
            ("MUL", "Mulund", False),
            ("THN", "Thane", True),     # Low lying, flood prone
            ("KLY", "Kurla", True),     # Near Mithi river
        ]
        
        # Create nodes
        for code, name, flood_prone in areas:
            self.nodes[code] = MonsoonAffectedNode(code, name, flood_prone)
            
        # Create connectivity based on Mumbai geography
        connections = [
            ("BAN", "JUH"), ("JUH", "VLE"), ("VLE", "ADH"),
            ("ADH", "MLD"), ("MLD", "BVI"), ("BVI", "DHR"),
            ("GHT", "VKH"), ("VKH", "MUL"), ("MUL", "THN"),
            ("KLY", "GHT"), ("ADH", "GHT"), ("VLE", "KLY"),
            ("BAN", "KLY"), ("THN", "DHR"), ("JUH", "BAN")
        ]
        
        for node1, node2 in connections:
            self.add_connection(node1, node2)
            
    def add_connection(self, node1: str, node2: str):
        """Add bidirectional connection"""
        if node1 in self.nodes and node2 in self.nodes:
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)
            self.connections.append((node1, node2))
            
    def inject_emergency_message(self, source_node: str, message: str):
        """Inject emergency message during monsoon"""
        if source_node in self.nodes:
            node = self.nodes[source_node]
            msg = node.create_message(message)
            self.global_messages.append(msg)
            
            # Simulate receiving the message
            asyncio.create_task(node._handle_message(msg))
            print(f"🚨 Emergency message from {node.area_name}: {message}")
            
    def simulate_monsoon_events(self):
        """Simulate monsoon-related network events"""
        if self.simulation_round == 3:
            # Heavy rainfall starts
            print("\n🌧️ Heavy monsoon rainfall begins!")
            flood_prone_nodes = [n for n in self.nodes.values() if n.flood_prone]
            
            for node in flood_prone_nodes[:3]:  # First wave of flooding
                node.simulate_monsoon_flooding(6.0)
                
        elif self.simulation_round == 6:
            # More areas get flooded
            print("\n🌊 Flooding spreads to more areas!")
            remaining_flood_nodes = [n for n in self.nodes.values() 
                                   if n.flood_prone and n.partition_state == PartitionState.CONNECTED]
            
            for node in remaining_flood_nodes[:2]:
                node.simulate_monsoon_flooding(4.0)
                
    async def simulate_round(self):
        """Simulate one round of network activity"""
        self.simulation_round += 1
        print(f"\n--- Round {self.simulation_round} ---")
        
        # Simulate monsoon events
        self.simulate_monsoon_events()
        
        # Inject emergency messages
        if self.simulation_round == 4:
            self.inject_emergency_message("BAN", "Road closure due to waterlogging at Bandra")
        elif self.simulation_round == 7:
            self.inject_emergency_message("GHT", "Alternative route available via Eastern Express Highway")
            
        # Collect gossip plans from all nodes
        all_gossip_plans = {}
        for node_id, node in self.nodes.items():
            gossip_plan = node.gossip_round()
            if gossip_plan:
                all_gossip_plans[node_id] = gossip_plan
                
        # Execute gossip (simulate message delivery)
        for sender_id, targets in all_gossip_plans.items():
            for target_id, messages in targets.items():
                if target_id in self.nodes:
                    target_node = self.nodes[target_id]
                    target_node.update_contact_time(sender_id)
                    
                    for message in messages:
                        await target_node._handle_message(message)
                        
    def print_network_status(self):
        """Print current network status"""
        print("\n📊 Mumbai Network Status:")
        
        connected = 0
        partitioned = 0
        healing = 0
        
        for node in self.nodes.values():
            view = node.get_network_view()
            
            if view['state'] == 'connected':
                status_icon = "✅"
                connected += 1
            elif view['state'] == 'partitioned':
                status_icon = "🔌"
                partitioned += 1
            else:
                status_icon = "🔄"
                healing += 1
                
            print(f"  {status_icon} {view['area']}: "
                  f"Active={view['active_connections']}/{view['total_neighbors']}, "
                  f"Messages={view['messages_count']}, "
                  f"Buffered={view['buffered_messages']}")
                  
        print(f"\nOverall: Connected={connected}, Partitioned={partitioned}, Healing={healing}")


async def main():
    """Main simulation function"""
    print("🇮🇳 Mumbai Monsoon Network Partition Simulation")
    print("=" * 50)
    
    # Create network
    network = MumbaiMonsoonNetwork()
    network.create_mumbai_monsoon_topology()
    
    print(f"Created Mumbai network with {len(network.nodes)} areas")
    print(f"Total connections: {len(network.connections)}")
    
    # Simulate for 15 rounds
    for round_num in range(15):
        await network.simulate_round()
        network.print_network_status()
        
        await asyncio.sleep(1)  # 1 second between rounds
        
    # Print partition history
    print("\n📈 Partition Event History:")
    for node in network.nodes.values():
        history = node.get_partition_history()
        if history:
            print(f"\n{node.area_name}:")
            for event in history:
                print(f"  {event['event_type']}: {event['cause']} at {event['timestamp']:.1f}")


if __name__ == "__main__":
    asyncio.run(main())