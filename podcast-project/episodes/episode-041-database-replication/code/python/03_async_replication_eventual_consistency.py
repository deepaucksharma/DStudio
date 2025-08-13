#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 3: Asynchronous Replication with Eventual Consistency - Flipkart Inventory

यह example Flipkart जैसे e-commerce platform की inventory management में
async replication और eventual consistency का real implementation दिखाता है।
High throughput के लिए async replication critical होती है।

Real-world Use Case: Flipkart Inventory Management
- Product inventory across multiple warehouses
- Eventual consistency for better performance
- Conflict-free replicated data types (CRDTs)
- Regional inventory distribution
"""

import asyncio
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InventoryOperation(Enum):
    ADD_STOCK = "add_stock"
    REMOVE_STOCK = "remove_stock"
    RESERVE_STOCK = "reserve_stock"
    RELEASE_STOCK = "release_stock"
    UPDATE_PRICE = "update_price"

class ReplicationState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class InventoryEvent:
    """Inventory change event for CRDT-based replication"""
    event_id: str
    product_id: str
    warehouse_id: str
    operation: InventoryOperation
    quantity: int
    price: Optional[float]
    timestamp: datetime
    originating_node: str
    vector_timestamp: Dict[str, int] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"EVT_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

@dataclass
class Product:
    """Product information in Flipkart inventory"""
    product_id: str
    name: str
    category: str
    brand: str
    base_price: float
    warehouses: Dict[str, int] = field(default_factory=dict)  # warehouse_id -> quantity
    reserved: Dict[str, int] = field(default_factory=dict)   # warehouse_id -> reserved_qty
    last_updated: datetime = field(default_factory=datetime.now)

class GCounterCRDT:
    """
    Grow-only Counter CRDT for inventory quantities
    Only supports increment operations (useful for stock additions)
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counters: Dict[str, int] = defaultdict(int)
        
    def increment(self, value: int = 1):
        """Increment counter (add stock)"""
        self.counters[self.node_id] += value
        
    def merge(self, other: 'GCounterCRDT'):
        """Merge with another GCounter"""
        for node_id, value in other.counters.items():
            self.counters[node_id] = max(self.counters[node_id], value)
            
    def value(self) -> int:
        """Get current counter value"""
        return sum(self.counters.values())

class PNCounterCRDT:
    """
    Positive-Negative Counter CRDT for inventory that can increase/decrease
    Suitable for tracking available quantities with additions and removals
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.positive = GCounterCRDT(node_id)
        self.negative = GCounterCRDT(node_id)
        
    def increment(self, value: int):
        """Add stock"""
        if value > 0:
            self.positive.increment(value)
        else:
            self.negative.increment(-value)
            
    def decrement(self, value: int):
        """Remove stock"""
        if value > 0:
            self.negative.increment(value)
        else:
            self.positive.increment(-value)
            
    def merge(self, other: 'PNCounterCRDT'):
        """Merge with another PNCounter"""
        self.positive.merge(other.positive)
        self.negative.merge(other.negative)
        
    def value(self) -> int:
        """Get current counter value"""
        return max(0, self.positive.value() - self.negative.value())

class FlipkartInventoryNode:
    """
    Flipkart inventory node with async replication
    हर warehouse का अपना node होता है eventual consistency के साथ
    """
    
    def __init__(self, node_id: str, warehouse_location: str):
        self.node_id = node_id
        self.warehouse_location = warehouse_location
        self.products: Dict[str, Product] = {}
        
        # CRDT counters for inventory tracking
        self.inventory_counters: Dict[str, PNCounterCRDT] = {}
        
        # Event log for replication
        self.event_log: List[InventoryEvent] = []
        self.vector_clock: Dict[str, int] = defaultdict(int)
        
        # Peer nodes for replication
        self.peer_nodes: Dict[str, 'FlipkartInventoryNode'] = {}
        
        # Asynchronous replication queue
        self.replication_queue: asyncio.Queue = asyncio.Queue()
        self.replication_running = True
        
        # Network simulation
        self.network_latency = 0.05  # 50ms typical inter-city latency
        self.network_failures = 0
        
        # Performance metrics
        self.events_processed = 0
        self.events_replicated = 0
        self.consistency_lag = 0.0
        
        # Initialize with popular products
        self._initialize_products()
        
    def _initialize_products(self):
        """Initialize with popular Flipkart products"""
        popular_products = [
            {"id": "MOBGXY001", "name": "Samsung Galaxy S24", "category": "Mobile", "brand": "Samsung", "price": 74999},
            {"id": "LPTDELL01", "name": "Dell Inspiron 15", "category": "Laptop", "brand": "Dell", "price": 45999},
            {"id": "TVLG55001", "name": "LG 55 4K Smart TV", "category": "TV", "brand": "LG", "price": 42999},
            {"id": "WMAMAZON1", "name": "Amazon Echo Dot", "category": "Electronics", "brand": "Amazon", "price": 3999},
            {"id": "SHOENIK01", "name": "Nike Air Max", "category": "Footwear", "brand": "Nike", "price": 8999}
        ]
        
        for product_data in popular_products:
            product = Product(
                product_id=product_data["id"],
                name=product_data["name"],
                category=product_data["category"],
                brand=product_data["brand"],
                base_price=product_data["price"]
            )
            
            self.products[product.product_id] = product
            
            # Initialize CRDT counter for this product
            self.inventory_counters[product.product_id] = PNCounterCRDT(self.node_id)
            
            # Add initial stock (random for simulation)
            import random
            initial_stock = random.randint(50, 200)
            self.inventory_counters[product.product_id].increment(initial_stock)
            product.warehouses[self.node_id] = initial_stock
            
    def add_peer(self, peer_node: 'FlipkartInventoryNode'):
        """Add peer warehouse node"""
        self.peer_nodes[peer_node.node_id] = peer_node
        logger.info(f"Peer {peer_node.warehouse_location} ({peer_node.node_id}) added to {self.warehouse_location}")
        
    async def process_inventory_operation(self, product_id: str, operation: InventoryOperation,
                                        quantity: int = 0, price: Optional[float] = None,
                                        metadata: Dict = None) -> Tuple[bool, str]:
        """
        Process inventory operation with eventual consistency
        यहाँ Flipkart के actual inventory operations simulate किए गए हैं
        """
        
        # Create event
        event = InventoryEvent(
            event_id="",  # Will be auto-generated
            product_id=product_id,
            warehouse_id=self.node_id,
            operation=operation,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            originating_node=self.node_id,
            vector_timestamp=self.vector_clock.copy(),
            metadata=metadata or {}
        )
        
        # Increment vector clock
        self.vector_clock[self.node_id] += 1
        event.vector_timestamp = self.vector_clock.copy()
        
        # Validate operation
        if not self._validate_operation(event):
            return False, "Invalid operation"
            
        # Apply operation locally
        success = await self._apply_operation(event)
        
        if success:
            # Add to event log
            self.event_log.append(event)
            self.events_processed += 1
            
            # Queue for async replication
            await self.replication_queue.put(event)
            
            logger.info(f"Operation processed: {operation.value} {quantity} units of {product_id} at {self.warehouse_location}")
            return True, event.event_id
        else:
            return False, "Operation failed"
            
    def _validate_operation(self, event: InventoryEvent) -> bool:
        """Validate inventory operation"""
        if event.product_id not in self.products:
            logger.warning(f"Unknown product: {event.product_id}")
            return False
            
        # Check for negative inventory (business rule)
        if event.operation in [InventoryOperation.REMOVE_STOCK, InventoryOperation.RESERVE_STOCK]:
            current_quantity = self.inventory_counters[event.product_id].value()
            reserved_quantity = self.products[event.product_id].reserved.get(self.node_id, 0)
            available = current_quantity - reserved_quantity
            
            if available < event.quantity:
                logger.warning(f"Insufficient stock for {event.product_id}: available={available}, requested={event.quantity}")
                return False
                
        return True
        
    async def _apply_operation(self, event: InventoryEvent) -> bool:
        """Apply inventory operation locally"""
        try:
            product = self.products[event.product_id]
            counter = self.inventory_counters[event.product_id]
            
            if event.operation == InventoryOperation.ADD_STOCK:
                counter.increment(event.quantity)
                product.warehouses[self.node_id] = counter.value()
                
            elif event.operation == InventoryOperation.REMOVE_STOCK:
                counter.decrement(event.quantity)
                product.warehouses[self.node_id] = counter.value()
                
            elif event.operation == InventoryOperation.RESERVE_STOCK:
                product.reserved[self.node_id] = product.reserved.get(self.node_id, 0) + event.quantity
                
            elif event.operation == InventoryOperation.RELEASE_STOCK:
                product.reserved[self.node_id] = max(0, product.reserved.get(self.node_id, 0) - event.quantity)
                
            elif event.operation == InventoryOperation.UPDATE_PRICE:
                if event.price:
                    product.base_price = event.price
                    
            product.last_updated = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply operation {event.event_id}: {e}")
            return False
            
    async def start_replication(self):
        """Start async replication process"""
        logger.info(f"Starting async replication for {self.warehouse_location}")
        
        while self.replication_running:
            try:
                # Wait for events to replicate
                event = await asyncio.wait_for(self.replication_queue.get(), timeout=1.0)
                
                # Replicate to all peers asynchronously
                replication_tasks = []
                for peer_id, peer_node in self.peer_nodes.items():
                    task = asyncio.create_task(self._replicate_to_peer(peer_node, event))
                    replication_tasks.append(task)
                    
                if replication_tasks:
                    # Fire and forget - don't wait for completion (async replication)
                    asyncio.gather(*replication_tasks, return_exceptions=True)
                    
                self.events_replicated += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Replication error: {e}")
                
    async def _replicate_to_peer(self, peer_node: 'FlipkartInventoryNode', event: InventoryEvent):
        """Replicate event to peer node"""
        try:
            # Simulate network latency
            await asyncio.sleep(self.network_latency)
            
            # Random network failures (1% failure rate)
            import random
            if random.random() < 0.01:
                self.network_failures += 1
                raise Exception("Network failure simulation")
                
            # Send event to peer
            await peer_node.receive_replicated_event(event)
            
        except Exception as e:
            logger.error(f"Failed to replicate to {peer_node.warehouse_location}: {e}")
            raise
            
    async def receive_replicated_event(self, event: InventoryEvent):
        """
        Receive replicated event from peer
        यहाँ eventual consistency achieve होती है
        """
        try:
            # Update vector clock
            for node_id, timestamp in event.vector_timestamp.items():
                self.vector_clock[node_id] = max(self.vector_clock[node_id], timestamp)
                
            # Check if we've already processed this event
            existing_event = next((e for e in self.event_log if e.event_id == event.event_id), None)
            if existing_event:
                return  # Already processed
                
            # Apply event if valid
            if self._validate_replicated_event(event):
                await self._apply_operation(event)
                self.event_log.append(event)
                
                # Merge CRDT states for eventual consistency
                if event.product_id in self.inventory_counters:
                    # Create temporary counter for incoming data
                    temp_counter = PNCounterCRDT(event.originating_node)
                    
                    if event.operation == InventoryOperation.ADD_STOCK:
                        temp_counter.increment(event.quantity)
                    elif event.operation == InventoryOperation.REMOVE_STOCK:
                        temp_counter.decrement(event.quantity)
                        
                    # Merge with local counter
                    self.inventory_counters[event.product_id].merge(temp_counter)
                    
                logger.debug(f"Replicated event {event.event_id} applied at {self.warehouse_location}")
                
        except Exception as e:
            logger.error(f"Failed to apply replicated event {event.event_id}: {e}")
            
    def _validate_replicated_event(self, event: InventoryEvent) -> bool:
        """Validate replicated event"""
        # Basic validation for replicated events
        return event.product_id in self.products
        
    def get_product_inventory(self, product_id: str) -> Dict:
        """Get current inventory for a product across all warehouses"""
        if product_id not in self.products:
            return {}
            
        product = self.products[product_id]
        local_quantity = self.inventory_counters[product_id].value()
        reserved_quantity = product.reserved.get(self.node_id, 0)
        available_quantity = local_quantity - reserved_quantity
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "warehouse": self.warehouse_location,
            "total_quantity": local_quantity,
            "reserved_quantity": reserved_quantity,
            "available_quantity": available_quantity,
            "last_updated": product.last_updated.isoformat()
        }
        
    def get_warehouse_status(self) -> Dict:
        """Get warehouse node status"""
        total_products = len(self.products)
        total_inventory = sum(counter.value() for counter in self.inventory_counters.values())
        
        return {
            "node_id": self.node_id,
            "warehouse_location": self.warehouse_location,
            "total_products": total_products,
            "total_inventory": total_inventory,
            "events_processed": self.events_processed,
            "events_replicated": self.events_replicated,
            "network_failures": self.network_failures,
            "vector_clock": dict(self.vector_clock),
            "connected_peers": len(self.peer_nodes),
            "replication_queue_size": self.replication_queue.qsize()
        }
        
    async def check_consistency(self) -> Dict:
        """
        Check eventual consistency across warehouses
        Calculate consistency lag and convergence status
        """
        consistency_report = {
            "warehouse": self.warehouse_location,
            "products": {},
            "overall_consistent": True,
            "max_lag_seconds": 0
        }
        
        for product_id in self.products:
            local_count = self.inventory_counters[product_id].value()
            
            # Compare with peers (for demonstration)
            peer_counts = {}
            max_timestamp_diff = 0
            
            for peer_id, peer_node in self.peer_nodes.items():
                if product_id in peer_node.inventory_counters:
                    peer_count = peer_node.inventory_counters[product_id].value()
                    peer_counts[peer_node.warehouse_location] = peer_count
                    
                    # Check timestamp difference
                    local_time = self.products[product_id].last_updated
                    peer_time = peer_node.products[product_id].last_updated
                    time_diff = abs((local_time - peer_time).total_seconds())
                    max_timestamp_diff = max(max_timestamp_diff, time_diff)
                    
            # Check if counts are consistent
            all_counts = [local_count] + list(peer_counts.values())
            is_consistent = len(set(all_counts)) <= 1  # All counts are same
            
            consistency_report["products"][product_id] = {
                "local_count": local_count,
                "peer_counts": peer_counts,
                "consistent": is_consistent,
                "max_timestamp_diff": max_timestamp_diff
            }
            
            if not is_consistent:
                consistency_report["overall_consistent"] = False
                
            consistency_report["max_lag_seconds"] = max(
                consistency_report["max_lag_seconds"], 
                max_timestamp_diff
            )
            
        return consistency_report

class FlipkartInventoryCluster:
    """Complete Flipkart inventory cluster with multiple warehouses"""
    
    def __init__(self):
        # Create warehouse nodes
        self.warehouses = {
            "WAREHOUSE_MUMBAI": FlipkartInventoryNode("WH_MUM", "Mumbai Distribution Center"),
            "WAREHOUSE_DELHI": FlipkartInventoryNode("WH_DEL", "Delhi Regional Hub"),
            "WAREHOUSE_BANGALORE": FlipkartInventoryNode("WH_BLR", "Bangalore Tech Hub"),
            "WAREHOUSE_CHENNAI": FlipkartInventoryNode("WH_CHE", "Chennai South Hub"),
            "WAREHOUSE_KOLKATA": FlipkartInventoryNode("WH_KOL", "Kolkata East Hub"),
        }
        
        # Setup peer connections
        self._setup_peer_network()
        
    def _setup_peer_network(self):
        """Setup peer-to-peer connections between warehouses"""
        warehouse_list = list(self.warehouses.values())
        
        for warehouse in warehouse_list:
            for peer in warehouse_list:
                if warehouse != peer:
                    warehouse.add_peer(peer)
                    
    async def start_cluster(self):
        """Start all replication processes"""
        logger.info("Starting Flipkart Inventory Cluster...")
        
        replication_tasks = []
        for warehouse in self.warehouses.values():
            task = asyncio.create_task(warehouse.start_replication())
            replication_tasks.append(task)
            
        logger.info(f"Started replication for {len(self.warehouses)} warehouses")
        return replication_tasks
        
    async def simulate_flipkart_operations(self, duration_minutes: int = 3):
        """
        Simulate realistic Flipkart inventory operations
        High volume operations जैसे sale time पर होते हैं
        """
        logger.info(f"Starting Flipkart operations simulation for {duration_minutes} minutes...")
        
        import random
        start_time = time.time()
        operations_count = 0
        
        # Popular products for simulation
        product_ids = list(next(iter(self.warehouses.values())).products.keys())
        
        while (time.time() - start_time) < (duration_minutes * 60):
            # Select random warehouse and product
            warehouse = random.choice(list(self.warehouses.values()))
            product_id = random.choice(product_ids)
            
            # Simulate different operation patterns
            operation_type = random.choices(
                [InventoryOperation.ADD_STOCK, InventoryOperation.REMOVE_STOCK, 
                 InventoryOperation.RESERVE_STOCK, InventoryOperation.RELEASE_STOCK],
                weights=[0.2, 0.4, 0.3, 0.1]  # More removals and reservations (realistic)
            )[0]
            
            quantity = random.randint(1, 20)
            
            # Metadata based on operation
            metadata = {
                "source": "Flipkart App",
                "operation_id": f"OP_{int(time.time() * 1000)}",
                "reason": self._get_operation_reason(operation_type)
            }
            
            try:
                success, result = await warehouse.process_inventory_operation(
                    product_id, operation_type, quantity, metadata=metadata
                )
                
                if success:
                    operations_count += 1
                    
            except Exception as e:
                logger.error(f"Operation failed: {e}")
                
            # High frequency operations
            await asyncio.sleep(0.05)  # 20 operations per second
            
        logger.info(f"Operations simulation completed: {operations_count} operations processed")
        return operations_count
        
    def _get_operation_reason(self, operation: InventoryOperation) -> str:
        """Get realistic reason for operation"""
        reasons = {
            InventoryOperation.ADD_STOCK: ["New shipment", "Returned items", "Vendor restocking"],
            InventoryOperation.REMOVE_STOCK: ["Customer order", "Damage", "Quality issue"],
            InventoryOperation.RESERVE_STOCK: ["Cart addition", "Order placement", "Pending payment"],
            InventoryOperation.RELEASE_STOCK: ["Cart abandonment", "Payment failure", "Order cancellation"]
        }
        
        import random
        return random.choice(reasons.get(operation, ["Unknown"]))
        
    async def check_cluster_consistency(self) -> Dict:
        """Check eventual consistency across entire cluster"""
        logger.info("Checking cluster consistency...")
        
        consistency_reports = {}
        for warehouse_id, warehouse in self.warehouses.items():
            report = await warehouse.check_consistency()
            consistency_reports[warehouse_id] = report
            
        # Overall cluster consistency analysis
        cluster_consistent = all(report["overall_consistent"] for report in consistency_reports.values())
        max_lag = max(report["max_lag_seconds"] for report in consistency_reports.values())
        
        return {
            "cluster_consistent": cluster_consistent,
            "max_consistency_lag": max_lag,
            "warehouse_reports": consistency_reports
        }
        
    def get_cluster_status(self) -> Dict:
        """Get complete cluster status"""
        total_events = sum(wh.events_processed for wh in self.warehouses.values())
        total_replications = sum(wh.events_replicated for wh in self.warehouses.values())
        total_failures = sum(wh.network_failures for wh in self.warehouses.values())
        
        return {
            "cluster_size": len(self.warehouses),
            "total_events_processed": total_events,
            "total_replications": total_replications,
            "total_network_failures": total_failures,
            "warehouses": {wh_id: wh.get_warehouse_status() for wh_id, wh in self.warehouses.items()}
        }

# Testing and demonstration
async def demonstrate_async_replication():
    """
    Complete demonstration of async replication with eventual consistency
    Real Flipkart inventory scenario
    """
    print("\n" + "="*75)
    print("Flipkart Async Replication with Eventual Consistency Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*75)
    
    # Initialize cluster
    cluster = FlipkartInventoryCluster()
    
    # Start replication
    replication_tasks = await cluster.start_cluster()
    
    # Show initial inventory status
    logger.info("\n--- Initial Warehouse Status ---")
    for warehouse_id, warehouse in cluster.warehouses.items():
        status = warehouse.get_warehouse_status()
        print(f"{warehouse.warehouse_location}: {status['total_inventory']} total items")
        
    # Demonstrate manual operations
    logger.info("\n--- Manual Inventory Operations ---")
    
    mumbai_warehouse = cluster.warehouses["WAREHOUSE_MUMBAI"]
    delhi_warehouse = cluster.warehouses["WAREHOUSE_DELHI"]
    
    # Add stock in Mumbai
    success, event_id = await mumbai_warehouse.process_inventory_operation(
        "MOBGXY001", InventoryOperation.ADD_STOCK, 50,
        metadata={"reason": "New Samsung shipment from Korea"}
    )
    print(f"Mumbai stock addition: {'Success' if success else 'Failed'} - {event_id}")
    
    # Remove stock in Delhi (concurrent operation)
    success, event_id = await delhi_warehouse.process_inventory_operation(
        "MOBGXY001", InventoryOperation.REMOVE_STOCK, 10,
        metadata={"reason": "Customer orders during sale"}
    )
    print(f"Delhi stock removal: {'Success' if success else 'Failed'} - {event_id}")
    
    # Wait for replication
    await asyncio.sleep(2)
    
    # Check inventory after operations
    logger.info("\n--- Inventory After Manual Operations ---")
    for warehouse_id, warehouse in cluster.warehouses.items():
        inventory = warehouse.get_product_inventory("MOBGXY001")
        print(f"{warehouse.warehouse_location}: {inventory['available_quantity']} Samsung Galaxy S24 available")
        
    # Simulate high-volume operations
    logger.info("\n--- High-Volume Operations Simulation ---")
    operations_count = await cluster.simulate_flipkart_operations(duration_minutes=1)
    print(f"Processed {operations_count} high-frequency operations")
    
    # Wait for eventual consistency
    logger.info("\n--- Waiting for Eventual Consistency ---")
    await asyncio.sleep(3)
    
    # Check consistency
    consistency_report = await cluster.check_cluster_consistency()
    print(f"Cluster consistency: {'✓ Consistent' if consistency_report['cluster_consistent'] else '✗ Inconsistent'}")
    print(f"Maximum consistency lag: {consistency_report['max_consistency_lag']:.2f} seconds")
    
    # Final cluster status
    logger.info("\n--- Final Cluster Status ---")
    final_status = cluster.get_cluster_status()
    
    print(f"Cluster Summary:")
    print(f"  Total events processed: {final_status['total_events_processed']}")
    print(f"  Total replications: {final_status['total_replications']}")
    print(f"  Network failures: {final_status['total_network_failures']}")
    
    print(f"\nWarehouse Performance:")
    for wh_id, wh_status in final_status['warehouses'].items():
        print(f"  {wh_status['warehouse_location']}:")
        print(f"    Events: {wh_status['events_processed']}")
        print(f"    Replications: {wh_status['events_replicated']}")
        print(f"    Queue size: {wh_status['replication_queue_size']}")
        
    # Show detailed consistency report
    logger.info("\n--- Detailed Consistency Analysis ---")
    for warehouse_id, report in consistency_report['warehouse_reports'].items():
        print(f"\n{cluster.warehouses[warehouse_id].warehouse_location}:")
        for product_id, product_report in report['products'].items():
            product_name = cluster.warehouses[warehouse_id].products[product_id].name
            print(f"  {product_name}: Local={product_report['local_count']}, " +
                  f"Consistent={'✓' if product_report['consistent'] else '✗'}")
    
    # Cleanup
    for warehouse in cluster.warehouses.values():
        warehouse.replication_running = False

if __name__ == "__main__":
    print("Flipkart Async Replication with Eventual Consistency")
    print("Episode 41: Database Replication Strategies")
    print("Demonstrating high-performance async replication in e-commerce...")
    
    # Run the demonstration
    asyncio.run(demonstrate_async_replication())