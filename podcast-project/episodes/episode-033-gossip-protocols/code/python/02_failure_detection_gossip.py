#!/usr/bin/env python3
"""
Failure Detection using Gossip Protocol (Cassandra-style)
=========================================================

WhatsApp Server Farm Failure Detection: जब कोई server down हो जाए तो
कैसे पता चले कि वो fail हो गया है या सिर्फ slow network है?

This implements SWIM (Scalable Weakly-consistent Infection-style Process Group
Membership) protocol similar to what Cassandra uses for failure detection.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import asyncio
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class NodeStatus(Enum):
    """Node status in failure detector"""
    ALIVE = "alive"
    SUSPECTED = "suspected"  # शक है कि fail हो गया
    FAILED = "failed"        # confirm fail हो गया


@dataclass
class HeartbeatInfo:
    """Heartbeat information for each node"""
    node_id: str
    sequence_number: int
    timestamp: float
    status: NodeStatus
    incarnation: int = 0  # Version number for conflict resolution


@dataclass
class GossipPayload:
    """Gossip message payload"""
    sender_id: str
    heartbeats: List[HeartbeatInfo]
    timestamp: float
    round_number: int


class WhatsAppServerNode:
    """
    WhatsApp Server Node with Failure Detection
    
    हर server अपने neighbors के साथ heartbeat information
    share करता है और failed nodes को detect करता है
    """
    
    def __init__(self, node_id: str, server_name: str, region: str = "mumbai"):
        self.node_id = node_id
        self.server_name = server_name
        self.region = region
        
        # Failure detection parameters
        self.heartbeat_table: Dict[str, HeartbeatInfo] = {}
        self.sequence_number = 0
        self.incarnation = 0
        
        # Gossip protocol settings
        self.gossip_interval = 1.0  # seconds
        self.gossip_fanout = 3      # number of nodes to gossip with
        self.failure_timeout = 5.0  # seconds to declare failure
        self.suspect_timeout = 2.0  # seconds to suspect failure
        
        # Network simulation
        self.alive = True
        self.network_delay = 0.1    # simulated network delay
        self.failure_probability = 0.01  # 1% chance of temporary failure
        
        # Monitoring
        self.gossip_round = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        self.neighbors: Set[str] = set()
        
        # Initialize own heartbeat
        self.update_own_heartbeat()
        
    def update_own_heartbeat(self):
        """Update own heartbeat information"""
        self.sequence_number += 1
        self.heartbeat_table[self.node_id] = HeartbeatInfo(
            node_id=self.node_id,
            sequence_number=self.sequence_number,
            timestamp=time.time(),
            status=NodeStatus.ALIVE if self.alive else NodeStatus.FAILED,
            incarnation=self.incarnation
        )
        
    def add_neighbor(self, neighbor_id: str):
        """Add neighbor server"""
        self.neighbors.add(neighbor_id)
        
    def simulate_failure(self, duration: float = 3.0):
        """Simulate server failure for testing"""
        self.alive = False
        print(f"💀 {self.server_name} failed!")
        
        # Schedule recovery
        asyncio.create_task(self._recover_after_delay(duration))
        
    async def _recover_after_delay(self, delay: float):
        """Recover server after delay"""
        await asyncio.sleep(delay)
        self.alive = True
        self.incarnation += 1  # Increase incarnation on recovery
        print(f"🔄 {self.server_name} recovered!")
        self.update_own_heartbeat()
        
    def merge_heartbeat_info(self, received_heartbeat: HeartbeatInfo) -> bool:
        """
        Merge received heartbeat information
        Returns True if information was updated
        """
        node_id = received_heartbeat.node_id
        current_info = self.heartbeat_table.get(node_id)
        
        if current_info is None:
            # New node discovered
            self.heartbeat_table[node_id] = received_heartbeat
            print(f"🔍 {self.server_name} discovered new node: {node_id}")
            return True
            
        # Check if received info is newer
        if self._is_newer_heartbeat(received_heartbeat, current_info):
            self.heartbeat_table[node_id] = received_heartbeat
            return True
            
        return False
        
    def _is_newer_heartbeat(self, new_hb: HeartbeatInfo, current_hb: HeartbeatInfo) -> bool:
        """Check if new heartbeat is newer than current"""
        # Higher incarnation always wins
        if new_hb.incarnation > current_hb.incarnation:
            return True
        elif new_hb.incarnation < current_hb.incarnation:
            return False
            
        # Same incarnation, check sequence number
        return new_hb.sequence_number > current_hb.sequence_number
        
    def detect_failures(self):
        """Detect failed nodes based on heartbeat timeouts"""
        current_time = time.time()
        updates = []
        
        for node_id, heartbeat in self.heartbeat_table.items():
            if node_id == self.node_id:
                continue  # Skip self
                
            time_since_heartbeat = current_time - heartbeat.timestamp
            
            if heartbeat.status == NodeStatus.ALIVE:
                if time_since_heartbeat > self.failure_timeout:
                    # Declare failed
                    heartbeat.status = NodeStatus.FAILED
                    updates.append(f"💀 Detected failure: {node_id}")
                elif time_since_heartbeat > self.suspect_timeout:
                    # Mark as suspected
                    heartbeat.status = NodeStatus.SUSPECTED
                    updates.append(f"⚠️  Suspecting failure: {node_id}")
                    
        for update in updates:
            print(f"{self.server_name}: {update}")
            
    def create_gossip_payload(self) -> GossipPayload:
        """Create gossip payload with current heartbeat table"""
        # Select subset of heartbeats to send (limit message size)
        heartbeats = list(self.heartbeat_table.values())
        
        # Always include own heartbeat
        selected_heartbeats = [hb for hb in heartbeats if hb.node_id == self.node_id]
        
        # Add random selection of others
        other_heartbeats = [hb for hb in heartbeats if hb.node_id != self.node_id]
        random.shuffle(other_heartbeats)
        selected_heartbeats.extend(other_heartbeats[:self.gossip_fanout * 2])
        
        return GossipPayload(
            sender_id=self.node_id,
            heartbeats=selected_heartbeats,
            timestamp=time.time(),
            round_number=self.gossip_round
        )
        
    def process_gossip_message(self, payload: GossipPayload) -> int:
        """
        Process received gossip message
        Returns number of updates made
        """
        self.messages_received += 1
        updates = 0
        
        for heartbeat in payload.heartbeats:
            if self.merge_heartbeat_info(heartbeat):
                updates += 1
                
        return updates
        
    def select_gossip_targets(self) -> List[str]:
        """Select random neighbors for gossip"""
        if not self.neighbors:
            return []
            
        targets = list(self.neighbors)
        random.shuffle(targets)
        return targets[:self.gossip_fanout]
        
    def gossip_round_step(self) -> Dict[str, GossipPayload]:
        """
        Perform one gossip round
        Returns messages to send to each target
        """
        if not self.alive:
            return {}  # Dead nodes don't gossip
            
        self.gossip_round += 1
        self.update_own_heartbeat()
        self.detect_failures()
        
        # Create gossip payload
        payload = self.create_gossip_payload()
        
        # Select targets
        targets = self.select_gossip_targets()
        
        # Create gossip plan
        gossip_plan = {}
        for target in targets:
            gossip_plan[target] = payload
            self.messages_sent += 1
            
        return gossip_plan
        
    def get_cluster_view(self) -> Dict:
        """Get current view of cluster state"""
        alive_nodes = []
        suspected_nodes = []
        failed_nodes = []
        
        for heartbeat in self.heartbeat_table.values():
            if heartbeat.status == NodeStatus.ALIVE:
                alive_nodes.append(heartbeat.node_id)
            elif heartbeat.status == NodeStatus.SUSPECTED:
                suspected_nodes.append(heartbeat.node_id)
            else:
                failed_nodes.append(heartbeat.node_id)
                
        return {
            "node_id": self.node_id,
            "alive": alive_nodes,
            "suspected": suspected_nodes,
            "failed": failed_nodes,
            "total_known": len(self.heartbeat_table)
        }
        
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            "node_id": self.node_id,
            "gossip_round": self.gossip_round,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "neighbors": len(self.neighbors),
            "known_nodes": len(self.heartbeat_table),
            "alive": self.alive
        }


class WhatsAppServerCluster:
    """WhatsApp Server Cluster Simulator"""
    
    def __init__(self):
        self.nodes: Dict[str, WhatsAppServerNode] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_time = 0
        
    def create_whatsapp_cluster(self, num_servers: int = 8):
        """Create WhatsApp server cluster topology"""
        regions = ["mumbai", "delhi", "bangalore", "chennai"]
        
        for i in range(num_servers):
            region = regions[i % len(regions)]
            node_id = f"wa-{region}-{i+1:02d}"
            server_name = f"WhatsApp-{region.capitalize()}-{i+1}"
            
            self.nodes[node_id] = WhatsAppServerNode(node_id, server_name, region)
            
        # Create mesh-like topology with some randomness
        node_ids = list(self.nodes.keys())
        for i, node_id in enumerate(node_ids):
            # Connect to next 3 nodes in circle
            for j in range(1, 4):
                neighbor_idx = (i + j) % len(node_ids)
                neighbor_id = node_ids[neighbor_idx]
                self.add_connection(node_id, neighbor_id)
                
        # Add some random cross-connections
        for _ in range(num_servers // 2):
            node1 = random.choice(node_ids)
            node2 = random.choice(node_ids)
            if node1 != node2:
                self.add_connection(node1, node2)
                
    def add_connection(self, node1: str, node2: str):
        """Add bidirectional connection"""
        if node1 in self.nodes and node2 in self.nodes:
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)
            if (node1, node2) not in self.connections and (node2, node1) not in self.connections:
                self.connections.append((node1, node2))
                
    def simulate_round(self) -> int:
        """
        Simulate one gossip round
        Returns total number of messages processed
        """
        self.simulation_time += 1
        
        # Collect all gossip plans
        all_gossip_plans = {}
        for node_id, node in self.nodes.items():
            gossip_plan = node.gossip_round_step()
            if gossip_plan:
                all_gossip_plans[node_id] = gossip_plan
                
        # Execute gossip
        total_messages = 0
        for sender_id, targets in all_gossip_plans.items():
            for target_id, payload in targets.items():
                if target_id in self.nodes:
                    updates = self.nodes[target_id].process_gossip_message(payload)
                    total_messages += 1
                    
        return total_messages
        
    def print_cluster_status(self):
        """Print current cluster status"""
        print(f"\n📊 Cluster Status (Round {self.simulation_time}):")
        
        for node in self.nodes.values():
            view = node.get_cluster_view()
            status_icon = "✅" if node.alive else "💀"
            print(f"  {status_icon} {node.server_name}: "
                  f"Alive={len(view['alive'])}, "
                  f"Suspected={len(view['suspected'])}, "
                  f"Failed={len(view['failed'])}")
                  
    def inject_failures(self):
        """Inject some failures for testing"""
        if self.simulation_time == 5:
            # Fail Mumbai server
            mumbai_nodes = [n for n in self.nodes.values() if "mumbai" in n.node_id]
            if mumbai_nodes:
                mumbai_nodes[0].simulate_failure(4.0)
                
        if self.simulation_time == 10:
            # Fail Delhi server
            delhi_nodes = [n for n in self.nodes.values() if "delhi" in n.node_id]
            if delhi_nodes:
                delhi_nodes[0].simulate_failure(6.0)


async def main():
    """Main simulation function"""
    print("🇮🇳 WhatsApp Server Cluster Failure Detection Simulation")
    print("=" * 60)
    
    # Create cluster
    cluster = WhatsAppServerCluster()
    cluster.create_whatsapp_cluster(8)
    
    print(f"Created cluster with {len(cluster.nodes)} servers")
    print(f"Total connections: {len(cluster.connections)}")
    
    # Simulate for 20 rounds
    for round_num in range(20):
        messages = cluster.simulate_round()
        cluster.print_cluster_status()
        
        # Inject failures for testing
        cluster.inject_failures()
        
        print(f"Messages this round: {messages}")
        await asyncio.sleep(1)  # 1 second between rounds
        
    # Final metrics
    print("\n📈 Final Metrics:")
    for node in cluster.nodes.values():
        metrics = node.get_metrics()
        print(f"  {node.server_name}: "
              f"Sent={metrics['messages_sent']}, "
              f"Received={metrics['messages_received']}, "
              f"Known={metrics['known_nodes']}")


if __name__ == "__main__":
    asyncio.run(main())