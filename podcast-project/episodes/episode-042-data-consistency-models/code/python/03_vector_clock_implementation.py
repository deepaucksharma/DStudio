"""
Vector Clock Implementation
Used in distributed systems for tracking causality
Example: WhatsApp message ordering, Git version control
"""

import uuid
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from copy import deepcopy
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class VectorClock:
    """
    Vector clock for distributed systems
    Har node ka apna counter hota hai - WhatsApp server jaisa
    """
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str) -> 'VectorClock':
        """
        Node ka counter badhao - message send karte time
        """
        new_clocks = self.clocks.copy()
        new_clocks[node_id] = new_clocks.get(node_id, 0) + 1
        return VectorClock(new_clocks)
        
    def update(self, other: 'VectorClock', node_id: str) -> 'VectorClock':
        """
        Dusre node se message receive karne par update karo
        WhatsApp mein message receive karne jaisa
        """
        new_clocks = {}
        
        # Sabhi nodes ka maximum lo
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        for node in all_nodes:
            self_time = self.clocks.get(node, 0)
            other_time = other.clocks.get(node, 0)
            new_clocks[node] = max(self_time, other_time)
            
        # Apna counter increment karo
        new_clocks[node_id] = new_clocks.get(node_id, 0) + 1
        
        return VectorClock(new_clocks)
        
    def compare(self, other: 'VectorClock') -> str:
        """
        Do vector clocks compare karo
        Returns: "before", "after", "concurrent", "equal"
        """
        if self.clocks == other.clocks:
            return "equal"
            
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        
        self_less_equal = True
        self_greater_equal = True
        
        for node in all_nodes:
            self_time = self.clocks.get(node, 0)
            other_time = other.clocks.get(node, 0)
            
            if self_time > other_time:
                self_less_equal = False
            if self_time < other_time:
                self_greater_equal = False
                
        if self_less_equal and self_greater_equal:
            return "equal"
        elif self_less_equal:
            return "before"
        elif self_greater_equal:
            return "after"
        else:
            return "concurrent"
            
    def __str__(self) -> str:
        return json.dumps(self.clocks, sort_keys=True)

@dataclass
class Message:
    """
    Distributed message with vector clock
    WhatsApp message jaisa - timestamp ke saath causality info
    """
    message_id: str
    sender: str
    receiver: str
    content: str
    vector_clock: VectorClock
    timestamp: float = field(default_factory=time.time)

class DistributedNode:
    """
    Distributed system mein ek node
    WhatsApp server ya Git repository jaisa
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector_clock = VectorClock()
        self.message_log: List[Message] = []
        self.received_messages: List[Message] = []
        
    def send_message(self, receiver_id: str, content: str) -> Message:
        """
        Message bhejo - WhatsApp jaisa
        """
        # Pehle apna clock increment karo
        self.vector_clock = self.vector_clock.increment(self.node_id)
        
        message = Message(
            message_id=str(uuid.uuid4())[:8],
            sender=self.node_id,
            receiver=receiver_id,
            content=content,
            vector_clock=deepcopy(self.vector_clock)
        )
        
        self.message_log.append(message)
        logging.info(f"{self.node_id} sent: '{content}' to {receiver_id} [VC: {self.vector_clock}]")
        
        return message
        
    def receive_message(self, message: Message):
        """
        Message receive karo aur vector clock update karo
        """
        # Received message ka clock ke saath merge karo
        self.vector_clock = self.vector_clock.update(message.vector_clock, self.node_id)
        self.received_messages.append(message)
        
        logging.info(f"{self.node_id} received: '{message.content}' from {message.sender} [VC: {self.vector_clock}]")
        
    def get_causal_order(self) -> List[Message]:
        """
        Messages ko causal order mein arrange karo
        WhatsApp mein proper message sequence jaisa
        """
        all_messages = self.message_log + self.received_messages
        
        # Sort by vector clock causality
        sorted_messages = []
        remaining_messages = all_messages.copy()
        
        while remaining_messages:
            # Find message with earliest causality
            earliest_idx = 0
            for i in range(1, len(remaining_messages)):
                comparison = remaining_messages[i].vector_clock.compare(
                    remaining_messages[earliest_idx].vector_clock
                )
                if comparison == "before":
                    earliest_idx = i
                    
            sorted_messages.append(remaining_messages.pop(earliest_idx))
            
        return sorted_messages
        
    def detect_concurrent_messages(self) -> List[Tuple[Message, Message]]:
        """
        Concurrent messages detect karo - conflict resolution ke liye
        """
        all_messages = self.message_log + self.received_messages
        concurrent_pairs = []
        
        for i in range(len(all_messages)):
            for j in range(i + 1, len(all_messages)):
                msg1, msg2 = all_messages[i], all_messages[j]
                if msg1.vector_clock.compare(msg2.vector_clock) == "concurrent":
                    concurrent_pairs.append((msg1, msg2))
                    
        return concurrent_pairs

class WhatsAppSimulator:
    """
    WhatsApp jaisa messaging system with vector clocks
    Group chat scenario - multiple users simultaneously messaging
    """
    
    def __init__(self):
        self.nodes: Dict[str, DistributedNode] = {}
        self.message_queue: List[Tuple[str, Message]] = []  # (receiver, message)
        
    def add_user(self, user_id: str):
        """
        Naya user add karo - WhatsApp account jaisa
        """
        self.nodes[user_id] = DistributedNode(user_id)
        logging.info(f"User {user_id} joined the chat")
        
    def send_message(self, sender: str, receiver: str, content: str):
        """
        Message send karo - network delay simulate karte hain
        """
        if sender not in self.nodes:
            logging.error(f"Sender {sender} not found")
            return
            
        sender_node = self.nodes[sender]
        message = sender_node.send_message(receiver, content)
        
        # Add to queue for async delivery
        self.message_queue.append((receiver, message))
        
    def deliver_pending_messages(self):
        """
        Pending messages deliver karo - network ke baad
        """
        while self.message_queue:
            receiver, message = self.message_queue.pop(0)
            
            if receiver in self.nodes:
                self.nodes[receiver].receive_message(message)
            else:
                logging.warning(f"Receiver {receiver} not found")
                
    def analyze_causality(self, user_id: str):
        """
        User ke liye message causality analyze karo
        """
        if user_id not in self.nodes:
            return
            
        user = self.nodes[user_id]
        ordered_messages = user.get_causal_order()
        concurrent_pairs = user.detect_concurrent_messages()
        
        print(f"\n=== Causality Analysis for {user_id} ===")
        print("Messages in causal order:")
        for msg in ordered_messages:
            print(f"  {msg.sender} -> {msg.receiver}: '{msg.content}' [VC: {msg.vector_clock}]")
            
        if concurrent_pairs:
            print("\nConcurrent messages detected:")
            for msg1, msg2 in concurrent_pairs:
                print(f"  Concurrent: '{msg1.content}' vs '{msg2.content}'")
                
    def get_global_state(self) -> Dict:
        """
        Poore system ka state - debugging ke liye
        """
        state = {}
        for user_id, node in self.nodes.items():
            state[user_id] = {
                "vector_clock": str(node.vector_clock),
                "sent_messages": len(node.message_log),
                "received_messages": len(node.received_messages)
            }
        return state

def demonstrate_vector_clocks():
    """
    Real-world demo: WhatsApp group chat scenario
    Mumbai college friends ka group chat
    """
    print("=== Vector Clock Demo: WhatsApp Group Chat ===")
    
    # Create WhatsApp simulator
    whatsapp = WhatsAppSimulator()
    
    # Add users - Mumbai college friends
    users = ["Rahul", "Priya", "Vikram", "Anita", "Rohan"]
    for user in users:
        whatsapp.add_user(user)
        
    print(f"\nUsers added: {', '.join(users)}")
    
    # Scenario 1: Simple message exchange
    print("\n=== Scenario 1: Simple Messages ===")
    whatsapp.send_message("Rahul", "Priya", "Hey, how's the weather in Mumbai?")
    whatsapp.deliver_pending_messages()
    
    whatsapp.send_message("Priya", "Rahul", "It's raining heavily! Stay home.")
    whatsapp.deliver_pending_messages()
    
    whatsapp.send_message("Rahul", "Vikram", "Priya says it's raining")
    whatsapp.deliver_pending_messages()
    
    # Scenario 2: Concurrent messages - Group chat chaos
    print("\n=== Scenario 2: Concurrent Group Messages ===")
    
    # Everyone sends messages simultaneously (before delivery)
    whatsapp.send_message("Vikram", "Anita", "Movie plan for tonight?")
    whatsapp.send_message("Anita", "Rohan", "Let's meet at Cafe Coffee Day")
    whatsapp.send_message("Rohan", "Rahul", "I'm stuck in traffic")
    whatsapp.send_message("Priya", "Vikram", "Which movie are we watching?")
    
    # Now deliver all at once
    whatsapp.deliver_pending_messages()
    
    # Scenario 3: Response chain
    print("\n=== Scenario 3: Response Chain ===")
    whatsapp.send_message("Rahul", "Anita", "Got your cafe message, coming!")
    whatsapp.deliver_pending_messages()
    
    whatsapp.send_message("Anita", "Priya", "Rahul is coming to cafe")
    whatsapp.deliver_pending_messages()
    
    whatsapp.send_message("Priya", "Vikram", "Everyone's meeting at cafe")
    whatsapp.deliver_pending_messages()
    
    # Analyze causality for each user
    print("\n" + "="*50)
    for user in users:
        whatsapp.analyze_causality(user)
        
    # Show global state
    print("\n=== Global System State ===")
    state = whatsapp.get_global_state()
    for user, info in state.items():
        print(f"{user}: VC={info['vector_clock']}, Sent={info['sent_messages']}, Received={info['received_messages']}")
        
    # Demonstrate conflict detection
    print("\n=== Conflict Detection Example ===")
    
    # Create conflicting updates
    node1 = DistributedNode("Mumbai_Server")
    node2 = DistributedNode("Delhi_Server")
    
    # Both servers update same user's status simultaneously
    msg1 = node1.send_message("Global", "User Rahul is online")
    msg2 = node2.send_message("Global", "User Rahul is offline")
    
    # Check if they're concurrent (conflict)
    comparison = msg1.vector_clock.compare(msg2.vector_clock)
    print(f"Server messages comparison: {comparison}")
    
    if comparison == "concurrent":
        print("⚠️ Conflict detected! Need resolution strategy.")
        print(f"Mumbai says: {msg1.content}")
        print(f"Delhi says: {msg2.content}")
        print("Resolution: Use timestamp or prefer specific server")

if __name__ == "__main__":
    demonstrate_vector_clocks()