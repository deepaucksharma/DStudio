#!/usr/bin/env python3
"""
Anti-Entropy Protocol for Data Synchronization
==============================================

Flipkart Inventory Sync: जब multiple warehouses में same products का
stock track करना हो तो कैसे ensure करें कि सभी में consistent data हो?

Anti-entropy protocols help maintain data consistency across distributed
systems by exchanging and reconciling differences between replicas.

Author: Code Developer Agent
Episode: 33 - Gossip Protocols
"""

import random
import time
import hashlib
import asyncio
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class SyncMethod(Enum):
    """Anti-entropy synchronization methods"""
    PUSH = "push"
    PULL = "pull"
    PUSH_PULL = "push_pull"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    HIGHEST_TIMESTAMP = "highest_timestamp"
    CUSTOM_LOGIC = "custom_logic"
    MANUAL_RESOLUTION = "manual_resolution"


@dataclass
class InventoryItem:
    """Flipkart inventory item"""
    product_id: str
    warehouse_id: str
    quantity: int
    price: float
    last_updated: float
    version: int = 1
    checksum: str = ""
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        if not self.checksum:
            self.checksum = self.calculate_checksum()
            
    def calculate_checksum(self) -> str:
        """Calculate item checksum for integrity verification"""
        data = f"{self.product_id}{self.warehouse_id}{self.quantity}{self.price}{self.version}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
        
    def is_newer_than(self, other: 'InventoryItem') -> bool:
        """Check if this item is newer than another"""
        if self.version > other.version:
            return True
        elif self.version == other.version:
            return self.last_updated > other.last_updated
        return False
        
    def create_conflict_with(self, other: 'InventoryItem') -> bool:
        """Check if this item conflicts with another"""
        return (
            self.product_id == other.product_id and
            self.warehouse_id == other.warehouse_id and
            self.version == other.version and
            (self.quantity != other.quantity or self.price != other.price)
        )


@dataclass
class SyncDelta:
    """Synchronization delta containing differences"""
    added_items: List[InventoryItem] = field(default_factory=list)
    updated_items: List[InventoryItem] = field(default_factory=list)
    deleted_items: List[str] = field(default_factory=list)  # Product IDs
    conflicts: List[Tuple[InventoryItem, InventoryItem]] = field(default_factory=list)


@dataclass
class SyncMetrics:
    """Synchronization performance metrics"""
    sync_rounds: int = 0
    items_synchronized: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    bytes_transferred: int = 0
    sync_duration: float = 0.0
    convergence_achieved: bool = False


class FlipkartWarehouse:
    """
    Flipkart Warehouse Node with Anti-Entropy Protocol
    
    हर warehouse अपना inventory maintain करता है और दूसरे warehouses
    के साथ anti-entropy protocol के through sync करता है
    """
    
    def __init__(self, warehouse_id: str, city: str, region: str):
        self.warehouse_id = warehouse_id
        self.city = city
        self.region = region
        
        # Inventory management
        self.inventory: Dict[str, InventoryItem] = {}
        self.deleted_items: Set[str] = set()
        self.version_vector: Dict[str, int] = {}  # For causality tracking
        
        # Anti-entropy configuration
        self.sync_method = SyncMethod.PUSH_PULL
        self.conflict_resolution = ConflictResolution.LAST_WRITE_WINS
        self.sync_interval = 30.0  # seconds
        self.batch_size = 100  # items per sync batch
        
        # Peer management
        self.peers: Set[str] = set()
        self.peer_priorities: Dict[str, float] = {}
        self.last_sync_times: Dict[str, float] = {}
        
        # Metrics and monitoring
        self.metrics = SyncMetrics()
        self.sync_history: List[Dict] = []
        
        # Consistency tracking
        self.merkle_tree_root: str = ""
        self.update_merkle_tree()
        
    def add_peer(self, peer_id: str, priority: float = 1.0):
        """Add peer warehouse for synchronization"""
        self.peers.add(peer_id)
        self.peer_priorities[peer_id] = priority
        self.version_vector[peer_id] = 0
        self.last_sync_times[peer_id] = 0
        
    def add_inventory_item(self, product_id: str, quantity: int, price: float):
        """Add or update inventory item"""
        item = InventoryItem(
            product_id=product_id,
            warehouse_id=self.warehouse_id,
            quantity=quantity,
            price=price,
            last_updated=time.time(),
            version=self.get_next_version(product_id)
        )
        
        self.inventory[product_id] = item
        self.update_merkle_tree()
        
        print(f"📦 {self.city} warehouse updated: {product_id} x{quantity} @ ₹{price}")
        
    def get_next_version(self, product_id: str) -> int:
        """Get next version number for product"""
        current_item = self.inventory.get(product_id)
        return current_item.version + 1 if current_item else 1
        
    def delete_inventory_item(self, product_id: str):
        """Delete inventory item (tombstone)"""
        if product_id in self.inventory:
            del self.inventory[product_id]
            self.deleted_items.add(product_id)
            self.update_merkle_tree()
            
            print(f"🗑️  {self.city} warehouse deleted: {product_id}")
            
    def update_merkle_tree(self):
        """Update merkle tree root for integrity checking"""
        if not self.inventory:
            self.merkle_tree_root = "empty"
            return
            
        # Simple merkle tree implementation
        checksums = sorted([item.checksum for item in self.inventory.values()])
        combined = "".join(checksums)
        self.merkle_tree_root = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
    def compare_with_peer(self, peer_inventory: Dict[str, InventoryItem], 
                         peer_deleted: Set[str]) -> SyncDelta:
        """Compare local inventory with peer and generate sync delta"""
        delta = SyncDelta()
        
        # Find items to add/update locally
        for product_id, peer_item in peer_inventory.items():
            local_item = self.inventory.get(product_id)
            
            if local_item is None:
                # Item doesn't exist locally
                if product_id not in self.deleted_items:
                    delta.added_items.append(peer_item)
            else:
                # Item exists, check for updates or conflicts
                if peer_item.is_newer_than(local_item):
                    delta.updated_items.append(peer_item)
                elif local_item.create_conflict_with(peer_item):
                    delta.conflicts.append((local_item, peer_item))
                    
        # Find items deleted by peer
        for product_id in peer_deleted:
            if product_id in self.inventory:
                delta.deleted_items.append(product_id)
                
        return delta
        
    def resolve_conflict(self, local_item: InventoryItem, 
                        peer_item: InventoryItem) -> InventoryItem:
        """Resolve conflict between local and peer items"""
        if self.conflict_resolution == ConflictResolution.LAST_WRITE_WINS:
            return peer_item if peer_item.last_updated > local_item.last_updated else local_item
            
        elif self.conflict_resolution == ConflictResolution.HIGHEST_TIMESTAMP:
            return peer_item if peer_item.last_updated > local_item.last_updated else local_item
            
        elif self.conflict_resolution == ConflictResolution.CUSTOM_LOGIC:
            # Custom business logic for Flipkart
            # Prefer higher quantity (stock availability priority)
            if peer_item.quantity > local_item.quantity:
                return peer_item
            elif local_item.quantity > peer_item.quantity:
                return local_item
            else:
                # Same quantity, prefer lower price
                return peer_item if peer_item.price < local_item.price else local_item
                
        else:  # MANUAL_RESOLUTION
            # In real system, this would flag for manual intervention
            print(f"⚠️  Manual resolution needed for {local_item.product_id}")
            return local_item  # Keep local for now
            
    def apply_sync_delta(self, delta: SyncDelta, from_peer: str) -> int:
        """Apply sync delta to local inventory"""
        changes = 0
        
        # Add new items
        for item in delta.added_items:
            self.inventory[item.product_id] = item
            changes += 1
            
        # Update existing items
        for item in delta.updated_items:
            self.inventory[item.product_id] = item
            changes += 1
            
        # Delete items
        for product_id in delta.deleted_items:
            if product_id in self.inventory:
                del self.inventory[product_id]
                self.deleted_items.add(product_id)
                changes += 1
                
        # Resolve conflicts
        for local_item, peer_item in delta.conflicts:
            resolved_item = self.resolve_conflict(local_item, peer_item)
            self.inventory[resolved_item.product_id] = resolved_item
            self.metrics.conflicts_detected += 1
            self.metrics.conflicts_resolved += 1
            changes += 1
            
        if changes > 0:
            self.update_merkle_tree()
            print(f"🔄 {self.city} applied {changes} changes from {from_peer}")
            
        return changes
        
    def create_sync_request(self, peer_id: str) -> Dict:
        """Create synchronization request for peer"""
        # In PULL mode, send our merkle tree root for comparison
        if self.sync_method == SyncMethod.PULL:
            return {
                "type": "sync_request",
                "method": "pull",
                "warehouse_id": self.warehouse_id,
                "merkle_root": self.merkle_tree_root,
                "version_vector": self.version_vector.copy(),
                "item_count": len(self.inventory)
            }
            
        # In PUSH mode, send our inventory changes
        elif self.sync_method == SyncMethod.PUSH:
            # Send items updated since last sync
            last_sync = self.last_sync_times.get(peer_id, 0)
            recent_items = [
                item for item in self.inventory.values()
                if item.last_updated > last_sync
            ]
            
            return {
                "type": "sync_request",
                "method": "push",
                "warehouse_id": self.warehouse_id,
                "items": [self._serialize_item(item) for item in recent_items[:self.batch_size]],
                "deleted_items": list(self.deleted_items),
                "merkle_root": self.merkle_tree_root
            }
            
        # In PUSH_PULL mode, alternate between push and pull
        else:
            if self.metrics.sync_rounds % 2 == 0:
                return self.create_sync_request_push(peer_id)
            else:
                return self.create_sync_request_pull(peer_id)
                
    def create_sync_request_push(self, peer_id: str) -> Dict:
        """Create PUSH sync request"""
        last_sync = self.last_sync_times.get(peer_id, 0)
        recent_items = [
            item for item in self.inventory.values()
            if item.last_updated > last_sync
        ]
        
        return {
            "type": "sync_request",
            "method": "push",
            "warehouse_id": self.warehouse_id,
            "items": [self._serialize_item(item) for item in recent_items[:self.batch_size]],
            "deleted_items": list(self.deleted_items),
            "merkle_root": self.merkle_tree_root
        }
        
    def create_sync_request_pull(self, peer_id: str) -> Dict:
        """Create PULL sync request"""
        return {
            "type": "sync_request",
            "method": "pull",
            "warehouse_id": self.warehouse_id,
            "merkle_root": self.merkle_tree_root,
            "version_vector": self.version_vector.copy(),
            "item_count": len(self.inventory)
        }
        
    def _serialize_item(self, item: InventoryItem) -> Dict:
        """Serialize inventory item for transmission"""
        return {
            "product_id": item.product_id,
            "warehouse_id": item.warehouse_id,
            "quantity": item.quantity,
            "price": item.price,
            "last_updated": item.last_updated,
            "version": item.version,
            "checksum": item.checksum
        }
        
    def _deserialize_item(self, data: Dict) -> InventoryItem:
        """Deserialize inventory item from transmission"""
        return InventoryItem(
            product_id=data["product_id"],
            warehouse_id=data["warehouse_id"],
            quantity=data["quantity"],
            price=data["price"],
            last_updated=data["last_updated"],
            version=data["version"],
            checksum=data["checksum"]
        )
        
    def process_sync_request(self, request: Dict) -> Dict:
        """Process incoming sync request and generate response"""
        method = request["method"]
        from_warehouse = request["warehouse_id"]
        
        if method == "pull":
            # Peer wants our data
            if request["merkle_root"] != self.merkle_tree_root:
                # Data differs, send our inventory
                items_to_send = list(self.inventory.values())[:self.batch_size]
                
                return {
                    "type": "sync_response",
                    "warehouse_id": self.warehouse_id,
                    "items": [self._serialize_item(item) for item in items_to_send],
                    "deleted_items": list(self.deleted_items),
                    "merkle_root": self.merkle_tree_root,
                    "has_more": len(self.inventory) > self.batch_size
                }
            else:
                # Data is same
                return {
                    "type": "sync_response",
                    "warehouse_id": self.warehouse_id,
                    "items": [],
                    "deleted_items": [],
                    "merkle_root": self.merkle_tree_root,
                    "has_more": False
                }
                
        elif method == "push":
            # Peer is sending us data
            peer_items = {
                data["product_id"]: self._deserialize_item(data)
                for data in request["items"]
            }
            peer_deleted = set(request["deleted_items"])
            
            # Compare and apply changes
            delta = self.compare_with_peer(peer_items, peer_deleted)
            changes = self.apply_sync_delta(delta, from_warehouse)
            
            # Update sync time
            self.last_sync_times[from_warehouse] = time.time()
            self.metrics.items_synchronized += changes
            
            return {
                "type": "sync_response",
                "warehouse_id": self.warehouse_id,
                "changes_applied": changes,
                "merkle_root": self.merkle_tree_root
            }
            
    def select_sync_peers(self) -> List[str]:
        """Select peers for synchronization based on priority and staleness"""
        if not self.peers:
            return []
            
        current_time = time.time()
        peer_scores = []
        
        for peer_id in self.peers:
            # Calculate staleness (time since last sync)
            staleness = current_time - self.last_sync_times.get(peer_id, 0)
            priority = self.peer_priorities.get(peer_id, 1.0)
            
            # Score based on staleness and priority
            score = staleness * priority
            peer_scores.append((peer_id, score))
            
        # Sort by score and select top peers
        peer_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select up to 3 peers for this round
        selected_peers = [peer_id for peer_id, _ in peer_scores[:3]]
        return selected_peers
        
    def anti_entropy_round(self) -> Dict[str, Dict]:
        """Perform one anti-entropy synchronization round"""
        self.metrics.sync_rounds += 1
        sync_start = time.time()
        
        selected_peers = self.select_sync_peers()
        sync_requests = {}
        
        for peer_id in selected_peers:
            request = self.create_sync_request(peer_id)
            sync_requests[peer_id] = request
            
        # Update metrics
        self.metrics.sync_duration = time.time() - sync_start
        
        # Log sync round
        sync_round_info = {
            "round": self.metrics.sync_rounds,
            "timestamp": time.time(),
            "peers_contacted": len(selected_peers),
            "inventory_size": len(self.inventory),
            "merkle_root": self.merkle_tree_root
        }
        self.sync_history.append(sync_round_info)
        
        return sync_requests
        
    def get_consistency_status(self) -> Dict:
        """Get current consistency status"""
        return {
            "warehouse_id": self.warehouse_id,
            "city": self.city,
            "inventory_items": len(self.inventory),
            "deleted_items": len(self.deleted_items),
            "merkle_root": self.merkle_tree_root,
            "peers": len(self.peers),
            "sync_rounds": self.metrics.sync_rounds,
            "conflicts_detected": self.metrics.conflicts_detected,
            "convergence_achieved": self.metrics.convergence_achieved
        }


class FlipkartInventoryNetwork:
    """Flipkart Multi-Warehouse Inventory Network"""
    
    def __init__(self):
        self.warehouses: Dict[str, FlipkartWarehouse] = {}
        self.connections: List[Tuple[str, str]] = []
        self.simulation_round = 0
        self.global_convergence = False
        
    def create_warehouse_network(self):
        """Create Flipkart warehouse network topology"""
        # Major Indian cities with Flipkart warehouses
        warehouses = [
            ("MUM01", "Mumbai", "West"),
            ("DEL01", "Delhi", "North"),
            ("BLR01", "Bangalore", "South"),
            ("HYD01", "Hyderabad", "South"),
            ("CHN01", "Chennai", "South"),
            ("KOL01", "Kolkata", "East"),
            ("PUN01", "Pune", "West"),
            ("AHM01", "Ahmedabad", "West"),
            ("JPR01", "Jaipur", "North"),
            ("LKO01", "Lucknow", "North")
        ]
        
        # Create warehouses
        for warehouse_id, city, region in warehouses:
            self.warehouses[warehouse_id] = FlipkartWarehouse(warehouse_id, city, region)
            
        # Create regional connectivity
        connections = [
            # West region cluster
            ("MUM01", "PUN01"), ("MUM01", "AHM01"),
            # North region cluster  
            ("DEL01", "JPR01"), ("DEL01", "LKO01"),
            # South region cluster
            ("BLR01", "HYD01"), ("BLR01", "CHN01"),
            # Inter-regional connections
            ("MUM01", "DEL01"), ("DEL01", "BLR01"),
            ("BLR01", "CHN01"), ("CHN01", "KOL01"),
            ("KOL01", "DEL01"), ("PUN01", "HYD01"),
            # Hub connections
            ("MUM01", "BLR01"), ("DEL01", "CHN01")
        ]
        
        for wh1, wh2 in connections:
            self.add_connection(wh1, wh2)
            
    def add_connection(self, warehouse1: str, warehouse2: str):
        """Add bidirectional sync connection between warehouses"""
        if warehouse1 in self.warehouses and warehouse2 in self.warehouses:
            # Priority based on geographic proximity
            priority = random.uniform(0.8, 1.0)
            
            self.warehouses[warehouse1].add_peer(warehouse2, priority)
            self.warehouses[warehouse2].add_peer(warehouse1, priority)
            self.connections.append((warehouse1, warehouse2))


async def main():
    """Main simulation function"""
    print("🇮🇳 Flipkart Anti-Entropy Inventory Synchronization")
    print("=" * 55)
    
    # Create network
    network = FlipkartInventoryNetwork()
    network.create_warehouse_network()
    
    print(f"Created network with {len(network.warehouses)} warehouses")
    print(f"Total sync connections: {len(network.connections)}")
    
    # Add initial inventory to different warehouses
    products = [
        ("PHONE001", "Samsung Galaxy S23", 50000),
        ("LAPTOP001", "Dell Inspiron 15", 45000),
        ("TV001", "LG 55 OLED", 120000),
        ("BOOK001", "Python Programming", 500),
        ("SHOES001", "Nike Air Max", 8000)
    ]
    
    for warehouse_id, warehouse in network.warehouses.items():
        for product_id, name, price in products:
            quantity = random.randint(10, 100)
            warehouse.add_inventory_item(product_id, quantity, price)
            
        # Add some warehouse-specific products
        for i in range(3):
            product_id = f"LOCAL_{warehouse_id}_{i+1:03d}"
            price = random.uniform(100, 10000)
            quantity = random.randint(5, 50)
            warehouse.add_inventory_item(product_id, quantity, price)
            
    print(f"Added initial inventory to all warehouses")
    
    # Simulate inventory changes and synchronization
    for round_num in range(12):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Simulate inventory changes
        if round_num % 3 == 0:
            # Random updates
            warehouse_ids = list(network.warehouses.keys())
            for _ in range(3):
                warehouse_id = random.choice(warehouse_ids)
                warehouse = network.warehouses[warehouse_id]
                
                if warehouse.inventory:
                    product_id = random.choice(list(warehouse.inventory.keys()))
                    new_quantity = random.randint(0, 150)
                    current_item = warehouse.inventory[product_id]
                    warehouse.add_inventory_item(product_id, new_quantity, current_item.price)
                    
        # Collect anti-entropy sync requests
        all_sync_requests = {}
        for warehouse_id, warehouse in network.warehouses.items():
            sync_requests = warehouse.anti_entropy_round()
            if sync_requests:
                all_sync_requests[warehouse_id] = sync_requests
                
        # Execute synchronization
        total_changes = 0
        for warehouse_id, peer_requests in all_sync_requests.items():
            for peer_id, request in peer_requests.items():
                if peer_id in network.warehouses:
                    peer_warehouse = network.warehouses[peer_id]
                    response = peer_warehouse.process_sync_request(request)
                    
                    # Process response
                    changes = response.get("changes_applied", 0)
                    total_changes += changes
                    
        print(f"Total inventory changes synchronized: {total_changes}")
        
        # Check convergence every few rounds
        if round_num % 4 == 0:
            print(f"\n📊 Convergence Status:")
            
            # Check merkle tree consistency
            merkle_roots = [wh.merkle_tree_root for wh in network.warehouses.values()]
            unique_roots = set(merkle_roots)
            
            if len(unique_roots) == 1:
                print(f"✅ Global convergence achieved! All warehouses synchronized.")
                network.global_convergence = True
            else:
                print(f"⏳ Convergence in progress: {len(unique_roots)} different states")
                
            # Print warehouse status
            for warehouse in list(network.warehouses.values())[:3]:  # Show first 3
                status = warehouse.get_consistency_status()
                print(f"  {status['city']}: "
                      f"Items={status['inventory_items']}, "
                      f"Conflicts={status['conflicts_detected']}, "
                      f"Rounds={status['sync_rounds']}")
                      
        await asyncio.sleep(0.5)
        
    # Final consistency analysis
    print(f"\n📈 Final Consistency Analysis:")
    
    # Merkle tree analysis
    merkle_roots = [wh.merkle_tree_root for wh in network.warehouses.values()]
    unique_roots = set(merkle_roots)
    
    print(f"Unique merkle roots: {len(unique_roots)}")
    print(f"Global convergence: {'✅ YES' if len(unique_roots) == 1 else '❌ NO'}")
    
    # Sync performance metrics
    total_sync_rounds = sum(wh.metrics.sync_rounds for wh in network.warehouses.values())
    total_conflicts = sum(wh.metrics.conflicts_detected for wh in network.warehouses.values())
    
    print(f"Total sync rounds: {total_sync_rounds}")
    print(f"Total conflicts detected: {total_conflicts}")
    
    # Inventory distribution
    total_items = sum(len(wh.inventory) for wh in network.warehouses.values())
    avg_items = total_items / len(network.warehouses)
    
    print(f"Total inventory items: {total_items}")
    print(f"Average items per warehouse: {avg_items:.1f}")
    
    # Show sample of synchronized data
    print(f"\n📋 Sample Synchronized Inventory:")
    sample_warehouse = list(network.warehouses.values())[0]
    for i, (product_id, item) in enumerate(sample_warehouse.inventory.items()):
        if i >= 3:  # Show first 3 items
            break
        print(f"  {product_id}: Qty={item.quantity}, Price=₹{item.price}, v{item.version}")


if __name__ == "__main__":
    asyncio.run(main())