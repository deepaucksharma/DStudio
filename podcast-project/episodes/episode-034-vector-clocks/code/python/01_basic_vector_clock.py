#!/usr/bin/env python3
"""
Basic Vector Clock Implementation
Real-world application: Distributed system event ordering and causality tracking

यह implementation vector clocks को demonstrate करती है
जैसे कि distributed databases में event ordering के लिए इस्तेमाल होती है
"""

import time
import copy
import json
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class EventType(Enum):
    LOCAL = "local"
    SEND = "send"
    RECEIVE = "receive"

class ComparisonResult(Enum):
    BEFORE = "before"      # a < b (a happened before b)
    AFTER = "after"        # a > b (a happened after b) 
    CONCURRENT = "concurrent"  # a || b (concurrent events)
    EQUAL = "equal"        # a = b (same event)

@dataclass
class VectorClock:
    """
    Vector Clock implementation
    हर node का अपना vector clock होता है जो event ordering track करता है
    """
    
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.nodes = sorted(nodes)  # Consistent ordering
        
        # Initialize clock vector - all zeros
        self.clock: Dict[str, int] = {node: 0 for node in self.nodes}
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def tick(self) -> 'VectorClock':
        """
        Increment local clock for local event
        Local event के लिए अपना counter बढ़ाते हैं
        """
        with self.lock:
            self.clock[self.node_id] += 1
        return self
    
    def update(self, other_clock: 'VectorClock') -> 'VectorClock':
        """
        Update clock when receiving message from another node
        Message receive करते वक्त clock को update करते हैं
        """
        with self.lock:
            # Take maximum of each component
            for node in self.nodes:
                self.clock[node] = max(self.clock[node], other_clock.clock.get(node, 0))
            
            # Increment own counter
            self.clock[self.node_id] += 1
        
        return self
    
    def compare(self, other_clock: 'VectorClock') -> ComparisonResult:
        """
        Compare two vector clocks to determine causal relationship
        Do clocks के बीच causal relationship पता करते हैं
        """
        if not isinstance(other_clock, VectorClock):
            raise TypeError("Can only compare with another VectorClock")
        
        # Check if clocks are equal
        if self.clock == other_clock.clock:
            return ComparisonResult.EQUAL
        
        # Check if self happened before other
        self_before_other = True
        other_before_self = True
        
        for node in self.nodes:
            self_val = self.clock.get(node, 0)
            other_val = other_clock.clock.get(node, 0)
            
            if self_val > other_val:
                other_before_self = False
            if self_val < other_val:
                self_before_other = False
        
        if self_before_other:
            return ComparisonResult.BEFORE
        elif other_before_self:
            return ComparisonResult.AFTER
        else:
            return ComparisonResult.CONCURRENT
    
    def copy(self) -> 'VectorClock':
        """Create a copy of this vector clock"""
        new_clock = VectorClock(self.node_id, self.nodes)
        new_clock.clock = self.clock.copy()
        return new_clock
    
    def get_timestamp(self) -> Dict[str, int]:
        """Get current timestamp as dictionary"""
        with self.lock:
            return self.clock.copy()
    
    def __str__(self) -> str:
        """String representation of vector clock"""
        clock_str = ', '.join([f"{node}:{self.clock[node]}" for node in self.nodes])
        return f"VectorClock({self.node_id}): [{clock_str}]"
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class Event:
    """Distributed system event with vector clock timestamp"""
    event_id: str
    event_type: EventType
    node_id: str
    timestamp: VectorClock
    content: Dict[str, Any]
    real_time: float = 0.0
    
    def __post_init__(self):
        if self.real_time == 0.0:
            self.real_time = time.time()

class DistributedNode:
    """
    Distributed system node with vector clock
    हर node distributed system में vector clock maintain करता है
    """
    
    def __init__(self, node_id: str, all_nodes: List[str]):
        self.node_id = node_id
        self.all_nodes = all_nodes
        
        # Initialize vector clock
        self.vector_clock = VectorClock(node_id, all_nodes)
        
        # Event history
        self.events: List[Event] = []
        self.message_queue: List[Tuple[str, Event]] = []
        
        # Network simulation
        self.network: Dict[str, 'DistributedNode'] = {}
        
        # Statistics
        self.events_processed = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        print(f"🕰️ Node {node_id} initialized with vector clock")
    
    def set_network(self, network: Dict[str, 'DistributedNode']):
        """Set network connections to other nodes"""
        self.network = network
    
    def local_event(self, event_content: Dict[str, Any]) -> Event:
        """
        Process a local event
        Local event के लिए vector clock को tick करते हैं
        """
        # Tick vector clock
        self.vector_clock.tick()
        
        # Create event
        event = Event(
            event_id=f"evt_{self.node_id}_{len(self.events)}",
            event_type=EventType.LOCAL,
            node_id=self.node_id,
            timestamp=self.vector_clock.copy(),
            content=event_content
        )
        
        # Add to history
        self.events.append(event)
        self.events_processed += 1
        
        print(f"📝 {self.node_id}: Local event {event.event_id} at {event.timestamp}")
        
        return event
    
    def send_message(self, target_node_id: str, message_content: Dict[str, Any]) -> Event:
        """
        Send message to another node
        Message send करते वक्त vector clock पर timestamp लगाते हैं
        """
        if target_node_id not in self.network:
            print(f"❌ {self.node_id}: Target node {target_node_id} not found in network")
            return None
        
        # Tick vector clock for send event
        self.vector_clock.tick()
        
        # Create send event
        send_event = Event(
            event_id=f"send_{self.node_id}_to_{target_node_id}_{len(self.events)}",
            event_type=EventType.SEND,
            node_id=self.node_id,
            timestamp=self.vector_clock.copy(),
            content={
                "message": message_content,
                "target": target_node_id,
                "sender_clock": self.vector_clock.get_timestamp()
            }
        )
        
        # Add to history
        self.events.append(send_event)
        self.events_processed += 1
        self.messages_sent += 1
        
        # Send message to target node (simulate network delay)
        target_node = self.network[target_node_id]
        
        def delayed_delivery():
            time.sleep(random.uniform(0.01, 0.1))  # 10-100ms delay
            target_node.receive_message(self.node_id, send_event)
        
        threading.Thread(target=delayed_delivery).start()
        
        print(f"📤 {self.node_id} → {target_node_id}: Sent message with clock {send_event.timestamp}")
        
        return send_event
    
    def receive_message(self, sender_id: str, message_event: Event):
        """
        Receive message from another node
        Message receive करते वक्त vector clock को update करते हैं
        """
        # Extract sender's clock from message
        sender_clock_data = message_event.content.get("sender_clock", {})
        sender_clock = VectorClock(sender_id, self.all_nodes)
        sender_clock.clock = sender_clock_data
        
        # Update vector clock with received clock
        old_clock = self.vector_clock.copy()
        self.vector_clock.update(sender_clock)
        
        # Create receive event
        receive_event = Event(
            event_id=f"recv_{sender_id}_to_{self.node_id}_{len(self.events)}",
            event_type=EventType.RECEIVE,
            node_id=self.node_id,
            timestamp=self.vector_clock.copy(),
            content={
                "message": message_event.content["message"],
                "sender": sender_id,
                "sender_event_id": message_event.event_id
            }
        )
        
        # Add to history
        self.events.append(receive_event)
        self.events_processed += 1
        self.messages_received += 1
        
        print(f"📥 {self.node_id} ← {sender_id}: Received message, clock updated from {old_clock} to {self.vector_clock}")
        
        return receive_event
    
    def get_causal_history(self) -> List[Event]:
        """Get events sorted by causal order (where possible)"""
        # Sort events by vector clock comparison
        sorted_events = []
        
        for event in self.events:
            # Insert event in causal order
            inserted = False
            for i, existing_event in enumerate(sorted_events):
                comparison = event.timestamp.compare(existing_event.timestamp)
                if comparison == ComparisonResult.BEFORE:
                    sorted_events.insert(i, event)
                    inserted = True
                    break
            
            if not inserted:
                sorted_events.append(event)
        
        return sorted_events
    
    def find_concurrent_events(self) -> List[Tuple[Event, Event]]:
        """Find pairs of concurrent events"""
        concurrent_pairs = []
        
        for i, event1 in enumerate(self.events):
            for j, event2 in enumerate(self.events[i+1:], i+1):
                comparison = event1.timestamp.compare(event2.timestamp)
                if comparison == ComparisonResult.CONCURRENT:
                    concurrent_pairs.append((event1, event2))
        
        return concurrent_pairs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get node statistics"""
        return {
            "node_id": self.node_id,
            "current_clock": self.vector_clock.get_timestamp(),
            "events_processed": self.events_processed,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "total_events": len(self.events),
            "concurrent_event_pairs": len(self.find_concurrent_events())
        }

def simulate_chat_application():
    """
    Simulate WhatsApp-style chat application with vector clocks
    यह simulation messaging app में message ordering को demonstrate करता है
    """
    print("🇮🇳 Vector Clock Chat Application - WhatsApp Message Ordering")
    print("📱 Scenario: Group chat with message causality tracking")
    print("=" * 60)
    
    # Create chat participants
    participants = ["alice", "bob", "charlie"]
    
    # Initialize nodes
    chat_nodes = {}
    for participant in participants:
        chat_nodes[participant] = DistributedNode(participant, participants)
    
    # Set network connections
    for node in chat_nodes.values():
        node.set_network(chat_nodes)
    
    print(f"\n👥 Chat participants: {participants}")
    
    # Simulate chat conversation
    print(f"\n💬 Starting group chat conversation...")
    
    # Alice starts the conversation
    alice = chat_nodes["alice"]
    bob = chat_nodes["bob"]
    charlie = chat_nodes["charlie"]
    
    # Message sequence
    time.sleep(0.1)
    alice.local_event({"action": "typing", "message": "Hey everyone!"})
    
    time.sleep(0.1)
    alice.send_message("bob", {"text": "Hey Bob, how's your day?"})
    alice.send_message("charlie", {"text": "Hey Charlie, how's your day?"})
    
    time.sleep(0.2)
    bob.send_message("alice", {"text": "Hi Alice! Going great, thanks!"})
    bob.send_message("charlie", {"text": "Hey Charlie, Alice asked about our day"})
    
    time.sleep(0.2)
    charlie.send_message("alice", {"text": "Hi Alice! Busy with work"})
    charlie.send_message("bob", {"text": "Hi Bob! Yeah, she did"})
    
    time.sleep(0.1)
    alice.send_message("bob", {"text": "That's good to hear!"})
    alice.send_message("charlie", {"text": "Don't work too hard!"})
    
    # Wait for all messages to be delivered
    time.sleep(0.5)
    
    # Show final state
    print(f"\n📊 Chat Session Results:")
    print("=" * 40)
    
    for participant, node in chat_nodes.items():
        stats = node.get_statistics()
        
        print(f"\n👤 {participant.title()}:")
        print(f"   Final clock: {stats['current_clock']}")
        print(f"   Events processed: {stats['events_processed']}")
        print(f"   Messages sent: {stats['messages_sent']}")
        print(f"   Messages received: {stats['messages_received']}")
        print(f"   Concurrent events: {stats['concurrent_event_pairs']}")
    
    # Analyze causal relationships
    print(f"\n🔍 Causal Analysis:")
    
    # Get some events for comparison
    alice_events = alice.events
    bob_events = bob.events
    
    if len(alice_events) > 0 and len(bob_events) > 0:
        alice_first = alice_events[0]
        bob_first = bob_events[0]
        
        comparison = alice_first.timestamp.compare(bob_first.timestamp)
        
        print(f"   Alice's first event vs Bob's first event: {comparison.value}")
        print(f"   Alice: {alice_first.timestamp}")
        print(f"   Bob: {bob_first.timestamp}")
    
    # Show concurrent events
    print(f"\n🔄 Concurrent Events Analysis:")
    for participant, node in chat_nodes.items():
        concurrent_pairs = node.find_concurrent_events()
        if concurrent_pairs:
            print(f"   {participant.title()} has {len(concurrent_pairs)} concurrent event pairs")
            for event1, event2 in concurrent_pairs[:2]:  # Show first 2 pairs
                print(f"     - {event1.event_id} || {event2.event_id}")

def simulate_distributed_bank_transactions():
    """
    Simulate distributed banking system with vector clocks
    यह example banking system में transaction ordering को demonstrate करता है
    """
    print("\n" + "="*60)
    print("🇮🇳 Distributed Banking - Transaction Causality")
    print("🏦 Scenario: Multi-branch banking with causal consistency")
    print("=" * 60)
    
    # Create bank branches
    branches = ["mumbai-branch", "delhi-branch", "bangalore-branch"]
    
    # Initialize bank nodes
    bank_nodes = {}
    for branch in branches:
        bank_nodes[branch] = DistributedNode(branch, branches)
    
    # Set network connections
    for node in bank_nodes.values():
        node.set_network(bank_nodes)
    
    print(f"\n🏦 Bank branches: {branches}")
    
    # Simulate banking operations
    print(f"\n💳 Processing banking transactions...")
    
    mumbai = bank_nodes["mumbai-branch"]
    delhi = bank_nodes["delhi-branch"]
    bangalore = bank_nodes["bangalore-branch"]
    
    # Transaction sequence
    time.sleep(0.05)
    mumbai.local_event({"action": "account_created", "account": "ACC001", "balance": 10000})
    
    time.sleep(0.05)
    mumbai.send_message("delhi-branch", {
        "transaction_type": "balance_inquiry",
        "account": "ACC001",
        "amount": 0
    })
    
    time.sleep(0.05)
    delhi.send_message("mumbai-branch", {
        "transaction_type": "withdrawal",
        "account": "ACC001", 
        "amount": 2000
    })
    
    time.sleep(0.05)
    mumbai.send_message("bangalore-branch", {
        "transaction_type": "transfer_out",
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 1500
    })
    
    time.sleep(0.05)
    bangalore.send_message("delhi-branch", {
        "transaction_type": "transfer_in",
        "from_account": "ACC001", 
        "to_account": "ACC002",
        "amount": 1500
    })
    
    time.sleep(0.05)
    delhi.local_event({"action": "compliance_check", "account": "ACC001"})
    
    # Wait for all transactions to process
    time.sleep(0.3)
    
    # Show final banking state
    print(f"\n📊 Banking System State:")
    print("=" * 40)
    
    for branch, node in bank_nodes.items():
        stats = node.get_statistics()
        
        print(f"\n🏦 {branch.replace('-', ' ').title()}:")
        print(f"   Vector clock: {stats['current_clock']}")
        print(f"   Total events: {stats['total_events']}")
        print(f"   Messages sent: {stats['messages_sent']}")
        print(f"   Messages received: {stats['messages_received']}")
    
    # Analyze transaction causality
    print(f"\n🔍 Transaction Causality Analysis:")
    
    # Compare some key events
    mumbai_events = mumbai.events
    delhi_events = delhi.events
    bangalore_events = bangalore.events
    
    if len(mumbai_events) > 1 and len(delhi_events) > 0:
        mumbai_create = mumbai_events[0]  # Account creation
        delhi_withdrawal = delhi_events[0]  # First Delhi transaction
        
        comparison = mumbai_create.timestamp.compare(delhi_withdrawal.timestamp)
        
        print(f"   Account creation vs Delhi withdrawal: {comparison.value}")
        print(f"   This ensures proper causality - account must exist before withdrawal")
    
    # Show causal ordering
    print(f"\n🔄 Event Ordering (Mumbai Branch):")
    causal_history = mumbai.get_causal_history()
    for i, event in enumerate(causal_history[:5]):  # Show first 5 events
        event_desc = event.content.get('action', event.event_type.value)
        print(f"   {i+1}. {event.event_id}: {event_desc} at {event.timestamp}")

if __name__ == "__main__":
    # Run chat application simulation
    simulate_chat_application()
    
    # Run banking system simulation
    simulate_distributed_bank_transactions()
    
    print("\n" + "="*60)
    print("🇮🇳 Vector Clock Key Benefits:")
    print("1. Captures causal relationships between events")
    print("2. Detects concurrent (independent) events")
    print("3. Enables consistent ordering in distributed systems")
    print("4. Used in distributed databases and message systems")
    print("5. Provides logical time without clock synchronization")
    print("6. Essential for conflict-free replicated data types (CRDTs)")