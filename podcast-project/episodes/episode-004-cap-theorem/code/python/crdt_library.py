#!/usr/bin/env python3
"""
CRDT Library Implementation - Episode 4
व्यावहारिक Conflict-free Replicated Data Types

यह library different CRDT types का production-ready implementation है।
CRDT का मतलब है कि data automatically merge हो जाता है बिना conflicts के।

Indian Context Examples:
- Google Docs collaborate editing (multiple users)
- WhatsApp group participant count
- Flipkart shopping cart items (across devices)
- Zomato restaurant rating aggregation
- UPI transaction counters across banks

CRDT Types implemented:
1. G-Counter (Grow-only Counter) - like view counts
2. PN-Counter (Increment/Decrement Counter) - like likes/dislikes
3. LWW-Register (Last-Write-Wins Register) - like user status
4. OR-Set (Observed-Remove Set) - like shopping cart items
"""

import time
import uuid
from typing import Dict, Set, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
import json
import random

class CRDT(ABC):
    """
    Base CRDT interface - सभी CRDT types का common interface
    """
    
    @abstractmethod
    def merge(self, other: 'CRDT') -> 'CRDT':
        """दो CRDT states को merge करना"""
        pass
    
    @abstractmethod
    def clone(self) -> 'CRDT':
        """Deep copy बनाना"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict:
        """Serialization के लिए"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict) -> 'CRDT':
        """Deserialization के लिए"""
        pass

@dataclass
class GCounter(CRDT):
    """
    G-Counter (Grow-only Counter) - सिर्फ increment हो सकता है
    
    Use cases:
    - YouTube video views
    - Website page visits  
    - App download counter
    - Flipkart product views
    
    Algorithm:
    - हर node का अपना counter होता है
    - Merge करते time maximum values लेते हैं
    - Monotonically increasing (कभी decrease नहीं होता)
    """
    
    node_id: str
    counters: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize करने के बाद अपना counter 0 से start करें"""
        if self.node_id not in self.counters:
            self.counters[self.node_id] = 0
    
    def increment(self, amount: int = 1) -> int:
        """
        Counter को increment करना
        
        Example: Flipkart product पर click count बढ़ाना
        """
        if amount < 0:
            raise ValueError("G-Counter can only increment (amount must be >= 0)")
        
        self.counters[self.node_id] += amount
        current_value = self.value()
        
        print(f"📈 Node {self.node_id}: Incremented by {amount}, total = {current_value}")
        return current_value
    
    def value(self) -> int:
        """
        Current counter value - सभी nodes का sum
        """
        return sum(self.counters.values())
    
    def merge(self, other: 'GCounter') -> 'GCounter':
        """
        दो G-Counters को merge करना
        
        Rule: हर node के लिए maximum value लें
        """
        if not isinstance(other, GCounter):
            raise TypeError("Can only merge with another GCounter")
        
        merged_counters = {}
        all_nodes = set(self.counters.keys()) | set(other.counters.keys())
        
        for node in all_nodes:
            self_value = self.counters.get(node, 0)
            other_value = other.counters.get(node, 0)
            merged_counters[node] = max(self_value, other_value)
        
        result = GCounter(self.node_id, merged_counters)
        
        print(f"🔄 G-Counter merge: {self.value()} + {other.value()} = {result.value()}")
        return result
    
    def clone(self) -> 'GCounter':
        """Deep copy"""
        return GCounter(self.node_id, self.counters.copy())
    
    def to_dict(self) -> Dict:
        """Serialization"""
        return {
            'type': 'GCounter',
            'node_id': self.node_id,
            'counters': self.counters
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GCounter':
        """Deserialization"""
        return cls(data['node_id'], data['counters'])
    
    def __str__(self) -> str:
        return f"GCounter(node={self.node_id}, value={self.value()}, counters={self.counters})"

@dataclass 
class PNCounter(CRDT):
    """
    PN-Counter (Positive-Negative Counter) - increment और decrement दोनों
    
    Use cases:
    - Social media likes/dislikes
    - Shopping cart quantity
    - Bank account balance (simplified)
    - Zomato restaurant ratings
    
    Algorithm:
    - दो G-Counters का combination: P (positive) और N (negative)
    - Value = P.value() - N.value()
    """
    
    node_id: str
    p_counter: GCounter = field(default_factory=lambda: None)
    n_counter: GCounter = field(default_factory=lambda: None)
    
    def __post_init__(self):
        """Initialize P and N counters"""
        if self.p_counter is None:
            self.p_counter = GCounter(self.node_id)
        if self.n_counter is None:
            self.n_counter = GCounter(self.node_id)
    
    def increment(self, amount: int = 1) -> int:
        """
        Counter को increment करना
        
        Example: Instagram post को like करना
        """
        if amount < 0:
            raise ValueError("Use decrement() for negative amounts")
        
        self.p_counter.increment(amount)
        current_value = self.value()
        
        print(f"👍 Node {self.node_id}: Liked +{amount}, total = {current_value}")
        return current_value
    
    def decrement(self, amount: int = 1) -> int:
        """
        Counter को decrement करना
        
        Example: Instagram post को dislike करना
        """
        if amount < 0:
            raise ValueError("Decrement amount must be positive")
        
        self.n_counter.increment(amount)
        current_value = self.value()
        
        print(f"👎 Node {self.node_id}: Disliked +{amount}, total = {current_value}")
        return current_value
    
    def value(self) -> int:
        """Current counter value = P - N"""
        return self.p_counter.value() - self.n_counter.value()
    
    def merge(self, other: 'PNCounter') -> 'PNCounter':
        """
        दो PN-Counters को merge करना
        """
        if not isinstance(other, PNCounter):
            raise TypeError("Can only merge with another PNCounter")
        
        merged_p = self.p_counter.merge(other.p_counter)
        merged_n = self.n_counter.merge(other.n_counter)
        
        result = PNCounter(self.node_id)
        result.p_counter = merged_p
        result.n_counter = merged_n
        
        print(f"🔄 PN-Counter merge: {self.value()} + {other.value()} = {result.value()}")
        return result
    
    def clone(self) -> 'PNCounter':
        """Deep copy"""
        result = PNCounter(self.node_id)
        result.p_counter = self.p_counter.clone()
        result.n_counter = self.n_counter.clone()
        return result
    
    def to_dict(self) -> Dict:
        """Serialization"""
        return {
            'type': 'PNCounter',
            'node_id': self.node_id,
            'p_counter': self.p_counter.to_dict(),
            'n_counter': self.n_counter.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PNCounter':
        """Deserialization"""
        result = cls(data['node_id'])
        result.p_counter = GCounter.from_dict(data['p_counter'])
        result.n_counter = GCounter.from_dict(data['n_counter'])
        return result
    
    def __str__(self) -> str:
        return f"PNCounter(node={self.node_id}, value={self.value()}, +{self.p_counter.value()}, -{self.n_counter.value()})"

@dataclass
class LWWRegister(CRDT):
    """
    LWW-Register (Last-Write-Wins Register) - timestamp के base पर value store
    
    Use cases:
    - User profile information
    - Document title/metadata
    - Configuration settings
    - WhatsApp status message
    
    Algorithm:
    - हर value के साथ timestamp store करते हैं
    - Merge करते time latest timestamp वाला value लेते हैं
    - Ties में node_id से decide करते हैं (deterministic)
    """
    
    node_id: str
    value: Any = None
    timestamp: float = 0.0
    writer_node: str = ""
    
    def write(self, value: Any) -> Any:
        """
        नई value write करना
        
        Example: WhatsApp status update करना
        """
        self.value = value
        self.timestamp = time.time()
        self.writer_node = self.node_id
        
        print(f"✍️ Node {self.node_id}: Wrote '{value}' at {self.timestamp:.3f}")
        return value
    
    def read(self) -> Any:
        """Current value read करना"""
        return self.value
    
    def merge(self, other: 'LWWRegister') -> 'LWWRegister':
        """
        दो LWW-Registers को merge करना
        
        Rule: Latest timestamp wins, ties में lexicographically smaller node_id wins
        """
        if not isinstance(other, LWWRegister):
            raise TypeError("Can only merge with another LWWRegister")
        
        result = LWWRegister(self.node_id)
        
        # Compare timestamps
        if self.timestamp > other.timestamp:
            result.value = self.value
            result.timestamp = self.timestamp
            result.writer_node = self.writer_node
            winner = "self"
        elif self.timestamp < other.timestamp:
            result.value = other.value
            result.timestamp = other.timestamp
            result.writer_node = other.writer_node
            winner = "other"
        else:
            # Timestamp tie - use node_id for deterministic resolution
            if self.writer_node <= other.writer_node:
                result.value = self.value
                result.timestamp = self.timestamp
                result.writer_node = self.writer_node
                winner = "self (tie-break)"
            else:
                result.value = other.value
                result.timestamp = other.timestamp
                result.writer_node = other.writer_node
                winner = "other (tie-break)"
        
        print(f"🔄 LWW-Register merge: Winner = {winner}, Value = '{result.value}'")
        return result
    
    def clone(self) -> 'LWWRegister':
        """Deep copy"""
        result = LWWRegister(self.node_id)
        result.value = self.value
        result.timestamp = self.timestamp
        result.writer_node = self.writer_node
        return result
    
    def to_dict(self) -> Dict:
        """Serialization"""
        return {
            'type': 'LWWRegister',
            'node_id': self.node_id,
            'value': self.value,
            'timestamp': self.timestamp,
            'writer_node': self.writer_node
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LWWRegister':
        """Deserialization"""
        result = cls(data['node_id'])
        result.value = data['value']
        result.timestamp = data['timestamp']
        result.writer_node = data['writer_node']
        return result
    
    def __str__(self) -> str:
        return f"LWWRegister(node={self.node_id}, value='{self.value}', ts={self.timestamp:.3f}, writer={self.writer_node})"

@dataclass
class ORSet(CRDT):
    """
    OR-Set (Observed-Remove Set) - elements को add/remove कर सकते हैं
    
    Use cases:
    - Shopping cart items
    - Group chat participants
    - Collaborative document tags
    - Flipkart wishlist items
    
    Algorithm:
    - हर element के साथ unique tag (UUID) assign करते हैं
    - Added set में (element, tag) pairs store करते हैं
    - Removed set में removed tags store करते हैं
    - Element present है अगर कोई non-removed tag exists
    """
    
    node_id: str
    added: Dict[Any, Set[str]] = field(default_factory=dict)  # element -> {tags}
    removed: Set[str] = field(default_factory=set)  # {removed_tags}
    
    def add(self, element: Any) -> str:
        """
        Element को set में add करना
        
        Example: Flipkart cart में item add करना
        """
        # Generate unique tag for this add operation
        tag = f"{self.node_id}_{uuid.uuid4().hex[:8]}_{int(time.time() * 1000)}"
        
        if element not in self.added:
            self.added[element] = set()
        
        self.added[element].add(tag)
        
        print(f"➕ Node {self.node_id}: Added '{element}' with tag {tag}")
        return tag
    
    def remove(self, element: Any) -> bool:
        """
        Element को set से remove करना
        
        Example: Cart से item remove करना
        """
        if element not in self.added:
            print(f"❌ Node {self.node_id}: Cannot remove '{element}' - not present")
            return False
        
        # Remove all non-removed tags for this element
        tags_to_remove = self.added[element] - self.removed
        if not tags_to_remove:
            print(f"❌ Node {self.node_id}: Cannot remove '{element}' - already removed")
            return False
        
        self.removed.update(tags_to_remove)
        
        print(f"➖ Node {self.node_id}: Removed '{element}' (removed {len(tags_to_remove)} tags)")
        return True
    
    def contains(self, element: Any) -> bool:
        """
        Check करना कि element present है या नहीं
        """
        if element not in self.added:
            return False
        
        # Element present है अगर कोई non-removed tag exists
        active_tags = self.added[element] - self.removed
        return len(active_tags) > 0
    
    def elements(self) -> Set[Any]:
        """
        Current set के सभी elements
        """
        result = set()
        for element, tags in self.added.items():
            active_tags = tags - self.removed
            if active_tags:  # At least one non-removed tag exists
                result.add(element)
        return result
    
    def size(self) -> int:
        """Set का current size"""
        return len(self.elements())
    
    def merge(self, other: 'ORSet') -> 'ORSet':
        """
        दो OR-Sets को merge करना
        
        Rule: 
        - Added sets का union
        - Removed sets का union
        """
        if not isinstance(other, ORSet):
            raise TypeError("Can only merge with another ORSet")
        
        result = ORSet(self.node_id)
        
        # Merge added elements
        all_elements = set(self.added.keys()) | set(other.added.keys())
        for element in all_elements:
            self_tags = self.added.get(element, set())
            other_tags = other.added.get(element, set())
            result.added[element] = self_tags | other_tags
        
        # Merge removed tags
        result.removed = self.removed | other.removed
        
        print(f"🔄 OR-Set merge: {self.size()} + {other.size()} = {result.size()} elements")
        print(f"   Self elements: {self.elements()}")
        print(f"   Other elements: {other.elements()}")
        print(f"   Merged elements: {result.elements()}")
        
        return result
    
    def clone(self) -> 'ORSet':
        """Deep copy"""
        result = ORSet(self.node_id)
        result.added = {k: v.copy() for k, v in self.added.items()}
        result.removed = self.removed.copy()
        return result
    
    def to_dict(self) -> Dict:
        """Serialization"""
        return {
            'type': 'ORSet',
            'node_id': self.node_id,
            'added': {str(k): list(v) for k, v in self.added.items()},
            'removed': list(self.removed)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ORSet':
        """Deserialization"""
        result = cls(data['node_id'])
        result.added = {k: set(v) for k, v in data['added'].items()}
        result.removed = set(data['removed'])
        return result
    
    def __str__(self) -> str:
        return f"ORSet(node={self.node_id}, elements={self.elements()}, size={self.size()})"

class CRDTReplicationSystem:
    """
    CRDT Replication System - Multiple nodes के बीच CRDT synchronization
    
    Production use case: Distributed shopping cart across mobile app और website
    """
    
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.crdts: Dict[str, Dict[str, CRDT]] = {}  # node_id -> {crdt_name -> crdt}
        self.message_queue: List[Dict] = []  # Simulated network messages
        self.sync_stats = {
            'messages_sent': 0,
            'merges_performed': 0,
            'conflicts_resolved': 0
        }
        
        # Initialize empty CRDT stores for each node
        for node in nodes:
            self.crdts[node] = {}
        
        print(f"🌐 CRDT Replication System initialized with nodes: {nodes}")
    
    def create_crdt(self, node_id: str, crdt_name: str, crdt_type: str, **kwargs) -> CRDT:
        """
        नया CRDT create करना
        """
        if node_id not in self.crdts:
            raise ValueError(f"Unknown node: {node_id}")
        
        if crdt_type == 'GCounter':
            crdt = GCounter(node_id, **kwargs)
        elif crdt_type == 'PNCounter':
            crdt = PNCounter(node_id, **kwargs)
        elif crdt_type == 'LWWRegister':
            crdt = LWWRegister(node_id, **kwargs)
        elif crdt_type == 'ORSet':
            crdt = ORSet(node_id, **kwargs)
        else:
            raise ValueError(f"Unknown CRDT type: {crdt_type}")
        
        self.crdts[node_id][crdt_name] = crdt
        
        print(f"🆕 Created {crdt_type} '{crdt_name}' on node {node_id}")
        return crdt
    
    def get_crdt(self, node_id: str, crdt_name: str) -> Optional[CRDT]:
        """
        Node से CRDT retrieve करना
        """
        return self.crdts.get(node_id, {}).get(crdt_name)
    
    def sync_crdt(self, from_node: str, to_node: str, crdt_name: str) -> bool:
        """
        दो nodes के बीच specific CRDT को sync करना
        """
        source_crdt = self.get_crdt(from_node, crdt_name)
        target_crdt = self.get_crdt(to_node, crdt_name)
        
        if not source_crdt:
            print(f"❌ Source CRDT '{crdt_name}' not found on node {from_node}")
            return False
        
        if not target_crdt:
            # Create new CRDT on target node
            target_crdt = source_crdt.clone()
            target_crdt.node_id = to_node
            self.crdts[to_node][crdt_name] = target_crdt
            print(f"🆕 Created new CRDT '{crdt_name}' on node {to_node}")
        else:
            # Merge CRDTs
            merged_crdt = target_crdt.merge(source_crdt)
            merged_crdt.node_id = to_node  # Maintain target node identity
            self.crdts[to_node][crdt_name] = merged_crdt
            self.sync_stats['merges_performed'] += 1
        
        self.sync_stats['messages_sent'] += 1
        print(f"🔄 Synced '{crdt_name}' from {from_node} to {to_node}")
        return True
    
    def broadcast_sync(self, source_node: str, crdt_name: str):
        """
        एक node से सभी other nodes को CRDT broadcast करना
        """
        print(f"📡 Broadcasting '{crdt_name}' from {source_node}")
        
        for target_node in self.nodes:
            if target_node != source_node:
                self.sync_crdt(source_node, target_node, crdt_name)
    
    def eventual_consistency_simulation(self, duration: int = 10):
        """
        Eventual consistency का simulation - random sync operations
        """
        print(f"\n🔄 Running eventual consistency simulation for {duration}s")
        
        start_time = time.time()
        operations = 0
        
        while time.time() - start_time < duration:
            # Random CRDT operation on random node
            node = random.choice(self.nodes)
            crdt_name = random.choice(list(self.crdts[node].keys())) if self.crdts[node] else None
            
            if crdt_name:
                crdt = self.crdts[node][crdt_name]
                
                # Random operation based on CRDT type
                if isinstance(crdt, GCounter):
                    crdt.increment(random.randint(1, 5))
                elif isinstance(crdt, PNCounter):
                    if random.random() < 0.7:  # 70% increment, 30% decrement
                        crdt.increment(random.randint(1, 3))
                    else:
                        crdt.decrement(random.randint(1, 2))
                elif isinstance(crdt, LWWRegister):
                    crdt.write(f"status_{random.randint(100, 999)}")
                elif isinstance(crdt, ORSet):
                    if random.random() < 0.8:  # 80% add, 20% remove
                        crdt.add(f"item_{random.randint(1, 20)}")
                    else:
                        elements = list(crdt.elements())
                        if elements:
                            crdt.remove(random.choice(elements))
                
                # Random sync to other nodes
                if random.random() < 0.3:  # 30% chance of sync
                    target = random.choice([n for n in self.nodes if n != node])
                    self.sync_crdt(node, target, crdt_name)
                
                operations += 1
            
            time.sleep(0.1)  # Small delay
        
        print(f"✅ Simulation complete: {operations} operations performed")
        self.print_sync_stats()
    
    def check_convergence(self) -> Dict[str, bool]:
        """
        सभी nodes पर same CRDT का convergence check करना
        """
        convergence_results = {}
        
        # Get all unique CRDT names across all nodes
        all_crdt_names = set()
        for node_crdts in self.crdts.values():
            all_crdt_names.update(node_crdts.keys())
        
        for crdt_name in all_crdt_names:
            # Get CRDT values from all nodes
            values = []
            for node in self.nodes:
                crdt = self.get_crdt(node, crdt_name)
                if crdt:
                    if isinstance(crdt, (GCounter, PNCounter)):
                        values.append(crdt.value())
                    elif isinstance(crdt, LWWRegister):
                        values.append((crdt.read(), crdt.timestamp))
                    elif isinstance(crdt, ORSet):
                        values.append(frozenset(crdt.elements()))
            
            # Check if all values are equal
            if len(values) > 1:
                converged = len(set(values)) == 1
            else:
                converged = True  # Single or no replicas
            
            convergence_results[crdt_name] = converged
            
            print(f"📊 CRDT '{crdt_name}' convergence: {'✅' if converged else '❌'}")
            if not converged:
                print(f"   Values across nodes: {values}")
        
        return convergence_results
    
    def print_system_state(self):
        """
        Current system state का detailed view
        """
        print("\n🔍 SYSTEM STATE")
        print("=" * 50)
        
        for node in self.nodes:
            print(f"\nNode {node}:")
            if not self.crdts[node]:
                print("  (no CRDTs)")
                continue
            
            for crdt_name, crdt in self.crdts[node].items():
                print(f"  {crdt_name}: {crdt}")
    
    def print_sync_stats(self):
        """
        Synchronization statistics
        """
        print(f"\n📈 SYNCHRONIZATION STATS")
        print(f"Messages sent: {self.sync_stats['messages_sent']}")
        print(f"Merges performed: {self.sync_stats['merges_performed']}")
        print(f"Conflicts resolved: {self.sync_stats['conflicts_resolved']}")

def flipkart_shopping_cart_demo():
    """
    Flipkart Shopping Cart - OR-Set का practical use case
    """
    print("\n🛒 DEMO: Flipkart Shopping Cart with CRDT")
    print("-" * 45)
    
    # Create replication system
    nodes = ["mobile_app", "website", "tablet_app"]
    system = CRDTReplicationSystem(nodes)
    
    # Create shopping carts on different devices
    for node in nodes:
        system.create_crdt(node, "shopping_cart", "ORSet")
    
    # User adds items from different devices
    mobile_cart = system.get_crdt("mobile_app", "shopping_cart")
    website_cart = system.get_crdt("website", "shopping_cart")
    tablet_cart = system.get_crdt("tablet_app", "shopping_cart")
    
    # Add items from mobile
    mobile_cart.add("iPhone 14 Pro")
    mobile_cart.add("AirPods Pro")
    
    # Add items from website (concurrent)
    website_cart.add("MacBook Pro")
    website_cart.add("iPhone 14 Pro")  # Duplicate add - different tag
    
    # Add items from tablet
    tablet_cart.add("iPad Air")
    
    print(f"\nBefore sync:")
    system.print_system_state()
    
    # Sync carts across devices
    system.broadcast_sync("mobile_app", "shopping_cart")
    system.sync_crdt("website", "mobile_app", "shopping_cart")
    system.sync_crdt("tablet_app", "website", "shopping_cart")
    system.broadcast_sync("website", "shopping_cart")
    
    print(f"\nAfter sync:")
    system.print_system_state()
    
    # Remove item and sync
    print(f"\nRemoving iPhone from mobile app...")
    mobile_cart = system.get_crdt("mobile_app", "shopping_cart")
    mobile_cart.remove("iPhone 14 Pro")
    
    system.broadcast_sync("mobile_app", "shopping_cart")
    
    print(f"\nFinal state:")
    system.print_system_state()

def youtube_view_counter_demo():
    """
    YouTube View Counter - G-Counter का use case
    """
    print("\n📹 DEMO: YouTube View Counter with G-Counter")
    print("-" * 45)
    
    nodes = ["cdn_mumbai", "cdn_delhi", "cdn_bangalore"]
    system = CRDTReplicationSystem(nodes)
    
    # Create view counters
    for node in nodes:
        system.create_crdt(node, "video_views", "GCounter")
    
    # Simulate views from different CDN nodes
    mumbai_counter = system.get_crdt("cdn_mumbai", "video_views")
    delhi_counter = system.get_crdt("cdn_delhi", "video_views")
    bangalore_counter = system.get_crdt("cdn_bangalore", "video_views")
    
    # Views from different regions
    mumbai_counter.increment(1500)  # Mumbai viewers
    delhi_counter.increment(2000)   # Delhi viewers  
    bangalore_counter.increment(1200)  # Bangalore viewers
    
    print(f"\nBefore sync - Views per region:")
    system.print_system_state()
    
    # Sync view counts
    system.broadcast_sync("cdn_mumbai", "video_views")
    system.broadcast_sync("cdn_delhi", "video_views") 
    system.broadcast_sync("cdn_bangalore", "video_views")
    
    print(f"\nAfter sync - Total views:")
    system.print_system_state()

def whatsapp_status_demo():
    """
    WhatsApp Status - LWW-Register का use case
    """
    print("\n💬 DEMO: WhatsApp Status with LWW-Register")
    print("-" * 45)
    
    nodes = ["phone", "web_whatsapp", "whatsapp_business"]
    system = CRDTReplicationSystem(nodes)
    
    # Create status registers
    for node in nodes:
        system.create_crdt(node, "user_status", "LWWRegister")
    
    # Update status from different devices
    phone_status = system.get_crdt("phone", "user_status")
    web_status = system.get_crdt("web_whatsapp", "user_status")
    business_status = system.get_crdt("whatsapp_business", "user_status")
    
    phone_status.write("Busy in meeting")
    time.sleep(0.1)
    web_status.write("Available for chat")
    time.sleep(0.1)  
    business_status.write("At Flipkart office")
    
    print(f"\nBefore sync:")
    system.print_system_state()
    
    # Sync status across devices
    system.broadcast_sync("phone", "user_status")
    system.broadcast_sync("web_whatsapp", "user_status")
    system.broadcast_sync("whatsapp_business", "user_status")
    
    print(f"\nAfter sync (latest wins):")
    system.print_system_state()

def instagram_likes_demo():
    """
    Instagram Likes/Dislikes - PN-Counter का use case
    """
    print("\n❤️ DEMO: Instagram Likes with PN-Counter")
    print("-" * 45)
    
    nodes = ["server_us", "server_india", "server_europe"]
    system = CRDTReplicationSystem(nodes)
    
    # Create like counters
    for node in nodes:
        system.create_crdt(node, "post_likes", "PNCounter")
    
    # Likes/dislikes from different regions
    us_likes = system.get_crdt("server_us", "post_likes")
    india_likes = system.get_crdt("server_india", "post_likes")
    europe_likes = system.get_crdt("server_europe", "post_likes")
    
    # Simulate user interactions
    us_likes.increment(500)      # US users like
    us_likes.decrement(50)       # Some dislikes
    
    india_likes.increment(2000)  # India users love it!
    india_likes.decrement(100)   # Some dislikes
    
    europe_likes.increment(800)  # Europe users like
    europe_likes.decrement(80)   # Some dislikes
    
    print(f"\nBefore sync - Regional reactions:")
    system.print_system_state()
    
    # Sync like counts globally
    system.broadcast_sync("server_us", "post_likes")
    system.broadcast_sync("server_india", "post_likes")
    system.broadcast_sync("server_europe", "post_likes")
    
    print(f"\nAfter sync - Global likes:")
    system.print_system_state()

def main():
    """
    Main demonstration with Indian tech company scenarios
    """
    print("🇮🇳 CRDT Library - Indian Tech Context")
    print("=" * 50)
    
    # Individual CRDT demos
    flipkart_shopping_cart_demo()
    youtube_view_counter_demo()
    whatsapp_status_demo()
    instagram_likes_demo()
    
    # Advanced: Eventual consistency simulation
    print("\n🔬 ADVANCED: Eventual Consistency Simulation")
    print("-" * 50)
    
    nodes = ["node_mumbai", "node_delhi", "node_bangalore"]
    system = CRDTReplicationSystem(nodes)
    
    # Create mixed CRDTs
    for node in nodes:
        system.create_crdt(node, "page_views", "GCounter")
        system.create_crdt(node, "user_rating", "PNCounter") 
        system.create_crdt(node, "config_setting", "LWWRegister")
        system.create_crdt(node, "active_features", "ORSet")
    
    # Run simulation
    system.eventual_consistency_simulation(duration=5)
    
    # Check final convergence
    print(f"\nConvergence check:")
    convergence = system.check_convergence()
    
    if all(convergence.values()):
        print("🎉 All CRDTs have converged!")
    else:
        print("⚠️ Some CRDTs have not converged yet")
        # Force full sync
        for crdt_name in convergence:
            for node in nodes:
                system.broadcast_sync(node, crdt_name)
        
        print("After forced sync:")
        system.check_convergence()
    
    print("\n✅ CRDT Library demonstration complete!")
    
    print("\n📚 KEY LEARNINGS:")
    print("1. CRDTs automatically resolve conflicts without coordination")
    print("2. Different CRDT types for different use cases:")
    print("   • G-Counter: View counts, downloads")
    print("   • PN-Counter: Likes/dislikes, ratings")
    print("   • LWW-Register: User status, configuration")
    print("   • OR-Set: Shopping carts, collections")
    print("3. Perfect for eventually consistent systems")
    print("4. Trade-off: Memory overhead vs conflict resolution")
    print("5. Used by: Redis, Riak, Amazon DynamoDB")

if __name__ == "__main__":
    main()