#!/usr/bin/env python3
"""
Basic Gossip Protocol Implementation
=====================================

Mumbai Train Network Gossip: जब एक स्टेशन पर delay की information सभी stations तक पहुंचानी हो

This implementation demonstrates how information spreads through a network
like how news spreads in Mumbai local trains from station to station.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import json
import asyncio
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class NodeState(Enum):
    """Node states in gossip protocol"""
    SUSCEPTIBLE = "susceptible"  # अभी तक नहीं मिली जानकारी
    INFECTED = "infected"      # जानकारी मिल गई, अब फैला रहा है
    REMOVED = "removed"        # जानकारी फैला चुका, अब शांत


@dataclass
class GossipMessage:
    """Gossip message structure"""
    message_id: str
    content: str
    timestamp: float
    sender_id: str
    ttl: int = 10  # Time to live - कितनी बार forward करना है
    version: int = 1


class MumbaiTrainGossipNode:
    """
    Mumbai Train Station Gossip Node
    
    हर station एक node है जो अपने neighboring stations के साथ
    delay/updates की information share करता है
    """
    
    def __init__(self, node_id: str, station_name: str):
        self.node_id = node_id
        self.station_name = station_name
        self.state = NodeState.SUSCEPTIBLE
        self.neighbors: Set[str] = set()
        self.messages: Dict[str, GossipMessage] = {}
        self.received_messages: Set[str] = set()
        self.gossip_probability = 0.8  # 80% chance to gossip
        self.active = True
        
    def add_neighbor(self, neighbor_id: str):
        """Add neighboring station"""
        self.neighbors.add(neighbor_id)
        
    def receive_message(self, message: GossipMessage) -> bool:
        """
        Receive gossip message from neighbor
        Returns True if message is new
        """
        if message.message_id in self.received_messages:
            return False  # पहले से पता है
            
        if message.ttl <= 0:
            return False  # Message expired
            
        self.received_messages.add(message.message_id)
        self.messages[message.message_id] = message
        
        # State transition: SUSCEPTIBLE -> INFECTED
        if self.state == NodeState.SUSCEPTIBLE:
            self.state = NodeState.INFECTED
            print(f"🚂 Station {self.station_name} received: {message.content}")
            
        return True
        
    def create_gossip_message(self, content: str) -> GossipMessage:
        """Create new gossip message"""
        message_id = f"{self.node_id}_{int(time.time() * 1000)}"
        return GossipMessage(
            message_id=message_id,
            content=content,
            timestamp=time.time(),
            sender_id=self.node_id
        )
        
    def get_messages_to_gossip(self) -> List[GossipMessage]:
        """Get messages that should be gossiped"""
        gossip_messages = []
        
        for msg in self.messages.values():
            if msg.ttl > 0 and random.random() < self.gossip_probability:
                # Decrease TTL
                msg.ttl -= 1
                gossip_messages.append(msg)
                
        return gossip_messages
        
    def select_gossip_targets(self, fanout: int = 2) -> List[str]:
        """
        Select random neighbors to gossip with
        Default fanout = 2 (typical in real systems)
        """
        if not self.neighbors:
            return []
            
        targets = list(self.neighbors)
        random.shuffle(targets)
        return targets[:min(fanout, len(targets))]
        
    def gossip_round(self) -> Dict[str, List[GossipMessage]]:
        """
        Perform one round of gossip
        Returns messages to send to each target
        """
        if self.state != NodeState.INFECTED or not self.active:
            return {}
            
        messages_to_send = self.get_messages_to_gossip()
        if not messages_to_send:
            # No more messages to send, become REMOVED
            self.state = NodeState.REMOVED
            return {}
            
        targets = self.select_gossip_targets()
        gossip_plan = {}
        
        for target in targets:
            gossip_plan[target] = messages_to_send.copy()
            
        return gossip_plan
        
    def get_status(self) -> Dict:
        """Get node status for monitoring"""
        return {
            "node_id": self.node_id,
            "station": self.station_name,
            "state": self.state.value,
            "neighbors": len(self.neighbors),
            "messages": len(self.messages),
            "active": self.active
        }


class MumbaiTrainNetwork:
    """Mumbai Local Train Network Simulator"""
    
    def __init__(self):
        self.nodes: Dict[str, MumbaiTrainGossipNode] = {}
        self.connections: List[tuple] = []
        self.round_count = 0
        
    def create_mumbai_network(self):
        """Create Mumbai train network topology"""
        # Main stations on Western Line
        stations = [
            ("VT", "Chhatrapati Shivaji Terminus"),
            ("MS", "Masjid Station"),
            ("BYR", "Byculla"),
            ("PR", "Parel"),
            ("CLA", "Currey Road"),
            ("BMD", "Bandra"),
            ("VLE", "Vile Parle"),
            ("ADH", "Andheri"),
            ("JGS", "Jogeshwari"),
            ("BVI", "Borivali"),
            ("VR", "Virar")
        ]
        
        # Create nodes
        for code, name in stations:
            self.nodes[code] = MumbaiTrainGossipNode(code, name)
            
        # Create linear connections (like train route)
        for i in range(len(stations) - 1):
            current = stations[i][0]
            next_station = stations[i + 1][0]
            self.add_connection(current, next_station)
            
        # Add some cross connections (like connecting lines)
        self.add_connection("BMD", "PR")  # Bandra-Parel connection
        self.add_connection("ADH", "VT")  # Andheri-CST direct
        
    def add_connection(self, node1: str, node2: str):
        """Add bidirectional connection between nodes"""
        if node1 in self.nodes and node2 in self.nodes:
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)
            self.connections.append((node1, node2))
            
    def inject_message(self, start_node: str, content: str):
        """Inject initial message at a station"""
        if start_node in self.nodes:
            node = self.nodes[start_node]
            message = node.create_gossip_message(content)
            node.receive_message(message)
            print(f"📢 Message injected at {node.station_name}: {content}")
            
    def simulate_round(self) -> bool:
        """
        Simulate one gossip round
        Returns True if there's still activity
        """
        self.round_count += 1
        print(f"\n--- Round {self.round_count} ---")
        
        # Collect all gossip plans
        all_gossip_plans = {}
        for node_id, node in self.nodes.items():
            gossip_plan = node.gossip_round()
            if gossip_plan:
                all_gossip_plans[node_id] = gossip_plan
                
        # Execute gossip plans
        activity = False
        for sender_id, targets in all_gossip_plans.items():
            for target_id, messages in targets.items():
                if target_id in self.nodes:
                    for message in messages:
                        received = self.nodes[target_id].receive_message(message)
                        if received:
                            activity = True
                            
        return activity
        
    def simulate_gossip_spread(self, max_rounds: int = 20):
        """Simulate complete gossip spread"""
        print("🚂 Starting Mumbai Train Network Gossip Simulation")
        
        for round_num in range(max_rounds):
            has_activity = self.simulate_round()
            
            # Print current status
            self.print_network_status()
            
            if not has_activity:
                print(f"\n✅ Gossip completed in {round_num + 1} rounds!")
                break
                
            time.sleep(0.5)  # Small delay for visualization
            
    def print_network_status(self):
        """Print current status of all nodes"""
        print("\nNetwork Status:")
        for node in self.nodes.values():
            status = node.get_status()
            print(f"  {status['station']}: {status['state']} "
                  f"(msgs: {status['messages']})")
                  
    def get_convergence_metrics(self) -> Dict:
        """Get metrics about gossip convergence"""
        states = [node.state for node in self.nodes.values()]
        return {
            "total_nodes": len(self.nodes),
            "susceptible": len([s for s in states if s == NodeState.SUSCEPTIBLE]),
            "infected": len([s for s in states if s == NodeState.INFECTED]),
            "removed": len([s for s in states if s == NodeState.REMOVED]),
            "convergence_ratio": len([s for s in states if s != NodeState.SUSCEPTIBLE]) / len(states)
        }


def main():
    """Main simulation function"""
    print("🇮🇳 Mumbai Train Network Gossip Protocol Simulation")
    print("=" * 50)
    
    # Create network
    network = MumbaiTrainNetwork()
    network.create_mumbai_network()
    
    # Inject delay message at Bandra station
    delay_msg = "Central Line delay of 15 minutes due to technical issue at Kurla"
    network.inject_message("BMD", delay_msg)
    
    # Simulate gossip spread
    network.simulate_gossip_spread()
    
    # Final metrics
    metrics = network.get_convergence_metrics()
    print(f"\n📊 Final Metrics:")
    print(f"  Convergence: {metrics['convergence_ratio']:.2%}")
    print(f"  Nodes informed: {metrics['infected'] + metrics['removed']}/{metrics['total_nodes']}")


if __name__ == "__main__":
    main()