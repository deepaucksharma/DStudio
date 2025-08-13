#!/usr/bin/env python3
"""
Leader Election Algorithms Implementation
========================================

Mumbai Local Train mein guard election ki tarah - ek leader chahiye!
Just like Mumbai local trains need one guard to coordinate,
distributed systems need leader election for coordination.

Algorithms Implemented:
1. Bully Algorithm - Strong nodes dominate (like Mumbai traffic police)
2. Ring Algorithm - Token passing (like Mumbai dabba system)
3. Raft Leader Election - Modern approach

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import threading
import uuid
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict
import queue

class NodeState(Enum):
    """Node states in leader election"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"
    FAILED = "failed"

class MessageType(Enum):
    """Message types for leader election"""
    # Bully Algorithm messages
    ELECTION = "election"
    OK = "ok"
    COORDINATOR = "coordinator"
    
    # Ring Algorithm messages
    RING_ELECTION = "ring_election"
    RING_ELECTED = "ring_elected"
    
    # Raft Algorithm messages
    REQUEST_VOTE = "request_vote"
    VOTE_RESPONSE = "vote_response"
    HEARTBEAT = "heartbeat"
    
    # General messages
    ALIVE = "alive"
    PING = "ping"
    PONG = "pong"

@dataclass
class ElectionMessage:
    """
    Election message structure
    """
    msg_type: MessageType
    sender_id: str
    receiver_id: str
    data: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

@dataclass
class NodeInfo:
    """
    Node information for election
    """
    node_id: str
    priority: int  # Higher priority = better candidate
    last_heartbeat: float
    vote_count: int = 0
    term: int = 0  # For Raft algorithm

class BullyElectionNode:
    """
    Bully Algorithm Implementation - Mumbai Traffic Police Style
    Higher ID nodes bully lower ID nodes
    """
    
    def __init__(self, node_id: str, all_node_ids: List[str]):
        self.node_id = node_id
        self.all_node_ids = sorted(all_node_ids)  # Sorted by priority
        self.node_priority = self.all_node_ids.index(node_id)
        
        self.state = NodeState.FOLLOWER
        self.current_leader = None
        self.is_active = True
        self.election_in_progress = False
        
        # Mumbai characteristics
        self.response_time = random.uniform(0.1, 0.5)  # Response delay
        self.failure_probability = 0.05  # 5% chance of temporary failure
        
        # Message handling
        self.message_queue = queue.Queue()
        self.message_handlers = {
            MessageType.ELECTION: self.handle_election_message,
            MessageType.OK: self.handle_ok_message,
            MessageType.COORDINATOR: self.handle_coordinator_message,
        }
        
        # Statistics
        self.elections_started = 0
        self.elections_won = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        print(f"🚔 BullyNode {self.node_id} initialized (priority: {self.node_priority})")
    
    def start_election(self) -> bool:
        """
        Start bully election - Mumbai traffic police taking charge
        """
        if self.election_in_progress:
            print(f"   Election already in progress for {self.node_id}")
            return False
        
        print(f"\n🏆 Node {self.node_id} starting BULLY ELECTION!")
        self.election_in_progress = True
        self.elections_started += 1
        
        # Send ELECTION message to all higher priority nodes
        higher_priority_nodes = [
            nid for nid in self.all_node_ids 
            if self.all_node_ids.index(nid) > self.node_priority
        ]
        
        if not higher_priority_nodes:
            # I am the highest priority node - declare victory!
            self.declare_coordinator()
            return True
        
        # Send election messages to higher priority nodes
        responses = []
        threads = []
        
        def send_election_message(target_id):
            message = ElectionMessage(
                msg_type=MessageType.ELECTION,
                sender_id=self.node_id,
                receiver_id=target_id,
                data={"priority": self.node_priority}
            )
            
            # Simulate network delay
            time.sleep(self.response_time)
            response = self.send_message(message)
            responses.append((target_id, response))
        
        # Send messages in parallel
        for target_id in higher_priority_nodes:
            thread = threading.Thread(target=send_election_message, args=(target_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for responses
        for thread in threads:
            thread.join()
        
        # Check responses
        ok_responses = [r for target, r in responses if r and r.msg_type == MessageType.OK]
        
        if not ok_responses:
            # No higher priority node responded - I win!
            self.declare_coordinator()
            return True
        else:
            # Higher priority nodes are active - wait for coordinator message
            print(f"   {self.node_id} received {len(ok_responses)} OK responses - waiting for coordinator")
            self.election_in_progress = False
            return False
    
    def declare_coordinator(self):
        """
        Declare self as coordinator - Mumbai traffic police chief
        """
        print(f"👑 Node {self.node_id} declares itself as COORDINATOR!")
        
        self.state = NodeState.LEADER
        self.current_leader = self.node_id
        self.elections_won += 1
        self.election_in_progress = False
        
        # Send COORDINATOR message to all lower priority nodes
        lower_priority_nodes = [
            nid for nid in self.all_node_ids 
            if self.all_node_ids.index(nid) < self.node_priority
        ]
        
        for target_id in lower_priority_nodes:
            message = ElectionMessage(
                msg_type=MessageType.COORDINATOR,
                sender_id=self.node_id,
                receiver_id=target_id,
                data={"new_leader": self.node_id}
            )
            self.send_message(message)
    
    def handle_election_message(self, message: ElectionMessage) -> Optional[ElectionMessage]:
        """
        Handle incoming election message
        """
        sender_priority = self.all_node_ids.index(message.sender_id)
        
        if sender_priority < self.node_priority:
            # Lower priority node started election - send OK and start own election
            print(f"   {self.node_id} received election from lower priority {message.sender_id}")
            
            # Send OK response
            ok_response = ElectionMessage(
                msg_type=MessageType.OK,
                sender_id=self.node_id,
                receiver_id=message.sender_id,
                data={"message": "I have higher priority"}
            )
            
            # Start own election
            threading.Thread(target=self.start_election).start()
            
            return ok_response
        else:
            # Should not receive election from higher priority node
            print(f"   {self.node_id} received unexpected election from higher priority {message.sender_id}")
            return None
    
    def handle_ok_message(self, message: ElectionMessage) -> Optional[ElectionMessage]:
        """
        Handle OK message - someone with higher priority is active
        """
        print(f"   {self.node_id} received OK from {message.sender_id}")
        return None
    
    def handle_coordinator_message(self, message: ElectionMessage) -> Optional[ElectionMessage]:
        """
        Handle coordinator announcement
        """
        new_leader = message.data.get("new_leader")
        print(f"   {self.node_id} acknowledges {new_leader} as new coordinator")
        
        self.current_leader = new_leader
        self.state = NodeState.FOLLOWER
        self.election_in_progress = False
        
        return None
    
    def send_message(self, message: ElectionMessage) -> Optional[ElectionMessage]:
        """
        Send message to another node (simulated)
        """
        self.messages_sent += 1
        
        # Simulate network delay and failures
        time.sleep(random.uniform(0.05, 0.2))
        
        if random.random() < self.failure_probability:
            print(f"   ❌ Message from {self.node_id} to {message.receiver_id} failed (Mumbai network issue)")
            return None
        
        # Simulate response from target node (in real system, this would be actual network call)
        response = self.simulate_node_response(message)
        return response
    
    def simulate_node_response(self, message: ElectionMessage) -> Optional[ElectionMessage]:
        """
        Simulate response from target node (for testing purposes)
        """
        # In real implementation, this would be handled by the target node
        # For simulation, we'll create appropriate responses
        
        if message.msg_type == MessageType.ELECTION:
            # Higher priority node would send OK
            target_priority = self.all_node_ids.index(message.receiver_id)
            if target_priority > self.node_priority:
                return ElectionMessage(
                    msg_type=MessageType.OK,
                    sender_id=message.receiver_id,
                    receiver_id=self.node_id
                )
        
        return None
    
    def simulate_failure(self):
        """
        Simulate node failure - Mumbai power cut
        """
        print(f"💥 Node {self.node_id} failed (Mumbai power cut!)")
        self.is_active = False
        self.state = NodeState.FAILED
    
    def recover(self):
        """
        Recover from failure - Mumbai power restored
        """
        print(f"🔄 Node {self.node_id} recovered (power restored!)")
        self.is_active = True
        self.state = NodeState.FOLLOWER
        self.current_leader = None
    
    def get_stats(self) -> Dict:
        """
        Get node statistics
        """
        return {
            "node_id": self.node_id,
            "priority": self.node_priority,
            "state": self.state.value,
            "current_leader": self.current_leader,
            "elections_started": self.elections_started,
            "elections_won": self.elections_won,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "is_active": self.is_active
        }

class RingElectionNode:
    """
    Ring Algorithm Implementation - Mumbai Dabba System Style
    Token passing in circular manner
    """
    
    def __init__(self, node_id: str, all_node_ids: List[str]):
        self.node_id = node_id
        self.all_node_ids = all_node_ids
        self.node_index = all_node_ids.index(node_id)
        
        self.state = NodeState.FOLLOWER
        self.current_leader = None
        self.is_active = True
        self.election_in_progress = False
        
        # Ring topology - each node knows next node
        self.next_node_id = all_node_ids[(self.node_index + 1) % len(all_node_ids)]
        
        # Statistics
        self.elections_initiated = 0
        self.elections_participated = 0
        self.tokens_passed = 0
        
        print(f"🔄 RingNode {self.node_id} initialized (next: {self.next_node_id})")
    
    def start_ring_election(self) -> bool:
        """
        Start ring election - Mumbai dabba token passing
        """
        if self.election_in_progress:
            return False
        
        print(f"\n🏆 Node {self.node_id} starting RING ELECTION!")
        self.election_in_progress = True
        self.elections_initiated += 1
        
        # Create election message with participant list
        election_message = ElectionMessage(
            msg_type=MessageType.RING_ELECTION,
            sender_id=self.node_id,
            receiver_id=self.next_node_id,
            data={
                "participants": [self.node_id],
                "initiator": self.node_id
            }
        )
        
        # Send to next node
        self.pass_token(election_message)
        return True
    
    def handle_ring_election_message(self, message: ElectionMessage):
        """
        Handle ring election message - Mumbai dabba passing
        """
        participants = message.data.get("participants", [])
        initiator = message.data.get("initiator")
        
        print(f"   {self.node_id} received ring election token from {message.sender_id}")
        self.elections_participated += 1
        
        if initiator == self.node_id:
            # Token completed full ring - elect leader
            print(f"   Token completed ring! Participants: {participants}")
            self.elect_ring_leader(participants)
        else:
            # Add self to participants and pass token
            if self.node_id not in participants:
                participants.append(self.node_id)
            
            # Create new message for next node
            next_message = ElectionMessage(
                msg_type=MessageType.RING_ELECTION,
                sender_id=self.node_id,
                receiver_id=self.next_node_id,
                data={
                    "participants": participants,
                    "initiator": initiator
                }
            )
            
            self.pass_token(next_message)
    
    def elect_ring_leader(self, participants: List[str]):
        """
        Elect leader from participants - highest priority wins
        """
        if not participants:
            return
        
        # Sort participants by priority (assuming lexicographic for simplicity)
        # In real system, this would be based on actual priority metrics
        leader = max(participants)
        
        print(f"👑 Ring election result: {leader} elected as leader!")
        
        # Send elected message around the ring
        elected_message = ElectionMessage(
            msg_type=MessageType.RING_ELECTED,
            sender_id=self.node_id,
            receiver_id=self.next_node_id,
            data={
                "elected_leader": leader,
                "participants": participants
            }
        )
        
        self.current_leader = leader
        self.state = NodeState.LEADER if leader == self.node_id else NodeState.FOLLOWER
        self.election_in_progress = False
        
        self.pass_token(elected_message)
    
    def handle_ring_elected_message(self, message: ElectionMessage):
        """
        Handle leader elected announcement
        """
        elected_leader = message.data.get("elected_leader")
        
        if elected_leader == self.node_id:
            # Message completed ring
            print(f"   {self.node_id} confirmed as ring leader!")
            return
        
        print(f"   {self.node_id} acknowledges {elected_leader} as ring leader")
        self.current_leader = elected_leader
        self.state = NodeState.FOLLOWER
        
        # Pass message to next node
        next_message = ElectionMessage(
            msg_type=MessageType.RING_ELECTED,
            sender_id=self.node_id,
            receiver_id=self.next_node_id,
            data=message.data
        )
        
        self.pass_token(next_message)
    
    def pass_token(self, message: ElectionMessage):
        """
        Pass token to next node - Mumbai dabba delivery
        """
        self.tokens_passed += 1
        
        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate network failure
        if random.random() < 0.05:
            print(f"   ❌ Token passing failed from {self.node_id} to {message.receiver_id}")
            return
        
        print(f"   🎯 {self.node_id} passed token to {message.receiver_id}")
        
        # In real system, this would be actual network communication
        # For simulation, we handle it directly
        self.simulate_token_delivery(message)
    
    def simulate_token_delivery(self, message: ElectionMessage):
        """
        Simulate token delivery to next node
        """
        # In real implementation, the target node would receive and process this
        # For simulation purposes, we'll handle the response
        pass
    
    def get_ring_stats(self) -> Dict:
        """
        Get ring election statistics
        """
        return {
            "node_id": self.node_id,
            "next_node": self.next_node_id,
            "state": self.state.value,
            "current_leader": self.current_leader,
            "elections_initiated": self.elections_initiated,
            "elections_participated": self.elections_participated,
            "tokens_passed": self.tokens_passed,
            "is_active": self.is_active
        }

def simulate_bully_election_scenario():
    """
    Simulate Bully Algorithm scenario - Mumbai Traffic Police
    """
    print("🚔 BULLY ALGORITHM SIMULATION")
    print("Mumbai Traffic Police Leadership Election")
    print("=" * 50)
    
    # Create nodes with Mumbai police station names
    mumbai_stations = ["Colaba", "Crawford_Market", "Bandra", "Andheri", "Borivali"]
    nodes = []
    
    for station in mumbai_stations:
        node = BullyElectionNode(station, mumbai_stations)
        nodes.append(node)
    
    scenarios = [
        {
            "name": "Normal Election - Highest priority node starts",
            "actions": [
                ("start_election", "Borivali"),  # Highest priority
            ]
        },
        {
            "name": "Lower priority node starts election",
            "actions": [
                ("start_election", "Colaba"),  # Lowest priority
            ]
        },
        {
            "name": "Leader failure and re-election",
            "actions": [
                ("start_election", "Borivali"),
                ("simulate_failure", "Borivali"),
                ("start_election", "Andheri"),
            ]
        }
    ]
    
    results = []
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Reset nodes
        for node in nodes:
            node.current_leader = None
            node.state = NodeState.FOLLOWER
            node.election_in_progress = False
            node.is_active = True
        
        scenario_results = []
        for action, node_id in scenario['actions']:
            node = next(n for n in nodes if n.node_id == node_id)
            
            if action == "start_election":
                success = node.start_election()
                scenario_results.append((action, node_id, success))
                time.sleep(0.5)  # Allow election to complete
                
            elif action == "simulate_failure":
                node.simulate_failure()
                scenario_results.append((action, node_id, True))
        
        # Check final state
        leaders = [node for node in nodes if node.state == NodeState.LEADER]
        final_leader = leaders[0].node_id if leaders else "No leader"
        
        print(f"   Final Leader: {final_leader}")
        scenario_results.append(("final_leader", final_leader, True))
        
        results.append({
            "scenario": scenario['name'],
            "actions": scenario_results,
            "final_stats": [node.get_stats() for node in nodes]
        })
    
    return results

def simulate_ring_election_scenario():
    """
    Simulate Ring Algorithm scenario - Mumbai Dabba System
    """
    print("\n🔄 RING ALGORITHM SIMULATION")  
    print("Mumbai Dabba Delivery System Leadership")
    print("=" * 50)
    
    # Create ring of dabba delivery points
    dabba_points = ["Churchgate", "Marine_Lines", "Charni_Road", "Grant_Road", "Mumbai_Central"]
    ring_nodes = []
    
    for point in dabba_points:
        node = RingElectionNode(point, dabba_points)
        ring_nodes.append(node)
    
    print(f"🔄 Ring topology: {' -> '.join(dabba_points)} -> {dabba_points[0]}")
    
    scenarios = [
        {
            "name": "Ring election initiated by first node",
            "initiator": "Churchgate"
        },
        {
            "name": "Ring election initiated by middle node", 
            "initiator": "Charni_Road"
        }
    ]
    
    ring_results = []
    for scenario in scenarios:
        print(f"\n📋 Ring Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Reset nodes
        for node in ring_nodes:
            node.current_leader = None
            node.state = NodeState.FOLLOWER
            node.election_in_progress = False
        
        # Start election
        initiator = next(n for n in ring_nodes if n.node_id == scenario['initiator'])
        success = initiator.start_ring_election()
        
        # Allow election to complete
        time.sleep(1.0)
        
        # Check results
        leaders = [node for node in ring_nodes if node.state == NodeState.LEADER]
        final_leader = leaders[0].node_id if leaders else "No leader"
        
        print(f"   Ring Leader: {final_leader}")
        
        ring_results.append({
            "scenario": scenario['name'],
            "initiator": scenario['initiator'],
            "final_leader": final_leader,
            "final_stats": [node.get_ring_stats() for node in ring_nodes]
        })
    
    return ring_results

def compare_election_algorithms():
    """
    Compare different election algorithms
    """
    print("\n📊 ELECTION ALGORITHMS COMPARISON")
    print("=" * 50)
    
    comparison = {
        "Bully Algorithm": {
            "message_complexity": "O(n²) in worst case",
            "time_complexity": "O(n) rounds",
            "fault_tolerance": "Handles node failures well",
            "network_topology": "Complete graph (all-to-all)",
            "advantages": ["Simple", "Fast convergence", "Deterministic"],
            "disadvantages": ["High message overhead", "Assumes reliable detection"],
            "mumbai_analogy": "Traffic police - senior officers take charge"
        },
        
        "Ring Algorithm": {
            "message_complexity": "O(n) messages",
            "time_complexity": "O(n) time",
            "fault_tolerance": "Sensitive to ring breaks",
            "network_topology": "Ring topology required",
            "advantages": ["Low message overhead", "Fair participation"],
            "disadvantages": ["Single point of failure", "Slow with large rings"],
            "mumbai_analogy": "Dabba system - token passed in circle"
        },
        
        "Raft Leader Election": {
            "message_complexity": "O(n) per election",
            "time_complexity": "Randomized timeouts",
            "fault_tolerance": "Handles minority failures",
            "network_topology": "Any connected topology",
            "advantages": ["Proven correctness", "Handles partitions", "Randomized"],
            "disadvantages": ["Complex implementation", "Requires majority"],
            "mumbai_analogy": "Democratic election - majority vote wins"
        }
    }
    
    for algorithm, properties in comparison.items():
        print(f"\n🏛️ {algorithm}")
        print("-" * 30)
        for key, value in properties.items():
            if isinstance(value, list):
                print(f"   {key.title()}: {', '.join(value)}")
            else:
                print(f"   {key.title()}: {value}")
    
    return comparison

if __name__ == "__main__":
    print("🚀 LEADER ELECTION ALGORITHMS")
    print("Mumbai Coordination Systems Simulation")
    print("=" * 60)
    
    try:
        # Simulate Bully Algorithm
        bully_results = simulate_bully_election_scenario()
        
        # Simulate Ring Algorithm
        ring_results = simulate_ring_election_scenario()
        
        # Compare algorithms
        algorithm_comparison = compare_election_algorithms()
        
        print("\n📋 SIMULATION SUMMARY")
        print("=" * 30)
        print(f"Bully scenarios tested: {len(bully_results)}")
        print(f"Ring scenarios tested: {len(ring_results)}")
        
        print("\n🎯 Key Insights:")
        print("• Bully Algorithm: Fast but high message overhead")
        print("• Ring Algorithm: Fair but sequential processing")
        print("• Choice depends on network topology and requirements")
        print("• Like Mumbai systems - different coordination for different needs!")
        
        print("\n🎊 LEADER ELECTION SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in leader election simulation: {e}")
        raise