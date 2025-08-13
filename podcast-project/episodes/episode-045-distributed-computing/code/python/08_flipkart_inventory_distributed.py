#!/usr/bin/env python3
"""
Flipkart Distributed Inventory Management System
Episode 45: Distributed Computing at Scale

यह example Flipkart का distributed inventory management system दिखाता है
Multiple warehouses, real-time synchronization, और distributed transactions
के साथ consistent inventory tracking across India।

Production Stats:
- Flipkart: 150M+ products across 1500+ warehouses
- Inventory updates: 100,000+ per minute
- Geographic distribution: 500+ cities
- Consistency requirement: Strong consistency for inventory
- Availability: 99.9% uptime during sales events
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import hashlib
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import socket

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    UNKNOWN = "UNKNOWN"

@dataclass
class Product:
    """Product information"""
    product_id: str
    name: str
    category: str
    brand: str
    price: float
    weight: float
    dimensions: Dict[str, float]  # length, width, height

@dataclass
class InventoryItem:
    """Inventory item at a specific warehouse"""
    warehouse_id: str
    product_id: str
    quantity: int
    reserved_quantity: int
    location_in_warehouse: str
    last_updated: datetime
    version: int  # For optimistic locking
    
    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

@dataclass
class InventoryTransaction:
    """Distributed inventory transaction"""
    transaction_id: str
    participant_warehouses: List[str]
    operations: List[Dict[str, Any]]  # List of inventory operations
    status: TransactionStatus
    coordinator_node: str
    timestamp: datetime
    timeout_seconds: int = 30

@dataclass
class Warehouse:
    """Warehouse node in distributed system"""
    warehouse_id: str
    location: str
    city: str
    state: str
    coordinates: Tuple[float, float]  # lat, lng
    capacity: int
    current_utilization: int
    is_active: bool
    node_address: str  # IP:Port for distributed communication

class DistributedConsensus:
    """Simplified Raft-like consensus for inventory updates"""
    
    def __init__(self, node_id: str, peer_nodes: List[str]):
        self.node_id = node_id
        self.peer_nodes = peer_nodes
        self.current_term = 0
        self.voted_for = None
        self.log = []  # Replicated log
        self.commit_index = 0
        self.last_applied = 0
        self.is_leader = False
        
        # Leader state
        self.next_index = {}  # For each server, index of next log entry to send
        self.match_index = {}  # For each server, index of highest log entry known to be replicated
        
        for peer in peer_nodes:
            self.next_index[peer] = 0
            self.match_index[peer] = 0
    
    async def append_entry(self, entry: Dict[str, Any]) -> bool:
        """Append entry to replicated log (simplified)"""
        if not self.is_leader:
            logger.warning(f"Node {self.node_id} is not leader, cannot append entry")
            return False
        
        # Add to local log
        log_entry = {
            "term": self.current_term,
            "entry": entry,
            "index": len(self.log),
            "timestamp": datetime.now().isoformat()
        }
        self.log.append(log_entry)
        
        # Replicate to majority of nodes (simplified)
        success_count = 1  # Self
        for peer in self.peer_nodes:
            try:
                # In real implementation, this would be network call
                # For demo, simulate with random success
                if await self._send_append_entries(peer, log_entry):
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to replicate to {peer}: {e}")
        
        # Check if majority agreed
        majority = (len(self.peer_nodes) + 1) // 2 + 1
        if success_count >= majority:
            self.commit_index = len(self.log) - 1
            logger.info(f"Entry committed at index {self.commit_index}")
            return True
        else:
            # Rollback entry
            self.log.pop()
            logger.warning(f"Failed to achieve consensus, rolled back entry")
            return False
    
    async def _send_append_entries(self, peer: str, entry: Dict[str, Any]) -> bool:
        """Send append entries RPC to peer (simplified)"""
        # Simulate network call with random success/failure
        await asyncio.sleep(0.01)  # Simulate network delay
        return random.random() < 0.8  # 80% success rate

class TwoPhaseCommitCoordinator:
    """Two-Phase Commit coordinator for distributed transactions"""
    
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.active_transactions = {}  # transaction_id -> transaction_state
    
    async def execute_distributed_transaction(self, transaction: InventoryTransaction,
                                            participants: Dict[str, 'WarehouseNode']) -> bool:
        """Execute distributed transaction using 2PC protocol"""
        
        logger.info(f"🔄 Starting 2PC transaction {transaction.transaction_id}")
        
        try:
            # Phase 1: Prepare
            prepare_results = await self._phase1_prepare(transaction, participants)
            
            # Check if all participants are prepared
            all_prepared = all(prepare_results.values())
            
            if all_prepared:
                # Phase 2: Commit
                logger.info(f"✅ All participants prepared, committing transaction {transaction.transaction_id}")
                commit_results = await self._phase2_commit(transaction, participants)
                
                # Update transaction status
                transaction.status = TransactionStatus.COMMITTED
                success = all(commit_results.values())
                
                if success:
                    logger.info(f"✅ Transaction {transaction.transaction_id} committed successfully")
                    return True
                else:
                    logger.error(f"❌ Some participants failed to commit {transaction.transaction_id}")
                    return False
            else:
                # Phase 2: Abort
                logger.warning(f"❌ Not all participants prepared, aborting transaction {transaction.transaction_id}")
                await self._phase2_abort(transaction, participants)
                transaction.status = TransactionStatus.ABORTED
                return False
                
        except Exception as e:
            logger.error(f"❌ Transaction {transaction.transaction_id} failed: {e}")
            await self._phase2_abort(transaction, participants)
            transaction.status = TransactionStatus.ABORTED
            return False
    
    async def _phase1_prepare(self, transaction: InventoryTransaction, 
                            participants: Dict[str, 'WarehouseNode']) -> Dict[str, bool]:
        """Phase 1: Send prepare requests to all participants"""
        prepare_tasks = []
        
        for warehouse_id in transaction.participant_warehouses:
            if warehouse_id in participants:
                task = participants[warehouse_id].prepare_transaction(transaction)
                prepare_tasks.append((warehouse_id, task))
        
        results = {}
        for warehouse_id, task in prepare_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=transaction.timeout_seconds)
                results[warehouse_id] = result
                logger.info(f"📋 Warehouse {warehouse_id} prepare result: {result}")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Prepare timeout for warehouse {warehouse_id}")
                results[warehouse_id] = False
            except Exception as e:
                logger.error(f"❌ Prepare failed for warehouse {warehouse_id}: {e}")
                results[warehouse_id] = False
        
        return results
    
    async def _phase2_commit(self, transaction: InventoryTransaction,
                           participants: Dict[str, 'WarehouseNode']) -> Dict[str, bool]:
        """Phase 2: Send commit requests to all participants"""
        commit_tasks = []
        
        for warehouse_id in transaction.participant_warehouses:
            if warehouse_id in participants:
                task = participants[warehouse_id].commit_transaction(transaction)
                commit_tasks.append((warehouse_id, task))
        
        results = {}
        for warehouse_id, task in commit_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=transaction.timeout_seconds)
                results[warehouse_id] = result
                logger.info(f"✅ Warehouse {warehouse_id} commit result: {result}")
            except Exception as e:
                logger.error(f"❌ Commit failed for warehouse {warehouse_id}: {e}")
                results[warehouse_id] = False
        
        return results
    
    async def _phase2_abort(self, transaction: InventoryTransaction,
                          participants: Dict[str, 'WarehouseNode']) -> None:
        """Phase 2: Send abort requests to all participants"""
        abort_tasks = []
        
        for warehouse_id in transaction.participant_warehouses:
            if warehouse_id in participants:
                task = participants[warehouse_id].abort_transaction(transaction)
                abort_tasks.append(task)
        
        # Wait for all abort operations to complete
        if abort_tasks:
            await asyncio.gather(*abort_tasks, return_exceptions=True)

class WarehouseNode:
    """Individual warehouse node in distributed inventory system"""
    
    def __init__(self, warehouse: Warehouse):
        self.warehouse = warehouse
        self.inventory = {}  # product_id -> InventoryItem
        self.prepared_transactions = {}  # transaction_id -> prepared_operations
        self.lock = asyncio.Lock()
        self.consensus = DistributedConsensus(
            warehouse.warehouse_id, 
            []  # Peer nodes would be provided in real system
        )
        
        # Initialize with some sample inventory
        self._initialize_inventory()
    
    def _initialize_inventory(self):
        """Initialize warehouse with sample inventory"""
        sample_products = [
            {"id": "PHONE001", "name": "iPhone 15", "category": "Electronics", "brand": "Apple"},
            {"id": "LAPTOP001", "name": "MacBook Air", "category": "Electronics", "brand": "Apple"},
            {"id": "BOOK001", "name": "System Design", "category": "Books", "brand": "Tech Books"},
            {"id": "SHIRT001", "name": "Cotton Shirt", "category": "Fashion", "brand": "Brand X"},
            {"id": "SHOES001", "name": "Running Shoes", "category": "Fashion", "brand": "Nike"},
        ]
        
        for product_info in sample_products:
            inventory_item = InventoryItem(
                warehouse_id=self.warehouse.warehouse_id,
                product_id=product_info["id"],
                quantity=random.randint(50, 500),
                reserved_quantity=0,
                location_in_warehouse=f"Aisle-{random.randint(1, 20)}-Shelf-{random.randint(1, 10)}",
                last_updated=datetime.now(),
                version=1
            )
            self.inventory[product_info["id"]] = inventory_item
    
    async def prepare_transaction(self, transaction: InventoryTransaction) -> bool:
        """Prepare phase of 2PC - check if transaction can be executed"""
        async with self.lock:
            try:
                logger.info(f"📋 Preparing transaction {transaction.transaction_id} at warehouse {self.warehouse.warehouse_id}")
                
                prepared_operations = []
                
                # Check each operation in the transaction
                for operation in transaction.operations:
                    if operation.get("warehouse_id") != self.warehouse.warehouse_id:
                        continue  # Skip operations for other warehouses
                    
                    product_id = operation["product_id"]
                    op_type = operation["type"]  # reserve, release, transfer
                    quantity = operation["quantity"]
                    
                    if product_id not in self.inventory:
                        logger.error(f"❌ Product {product_id} not found in warehouse {self.warehouse.warehouse_id}")
                        return False
                    
                    item = self.inventory[product_id]
                    
                    if op_type == "reserve":
                        if item.available_quantity < quantity:
                            logger.error(f"❌ Insufficient inventory for {product_id}: available={item.available_quantity}, requested={quantity}")
                            return False
                        prepared_operations.append({
                            "product_id": product_id,
                            "type": "reserve",
                            "quantity": quantity,
                            "old_reserved": item.reserved_quantity
                        })
                    
                    elif op_type == "release":
                        if item.reserved_quantity < quantity:
                            logger.error(f"❌ Cannot release {quantity} units of {product_id}, only {item.reserved_quantity} reserved")
                            return False
                        prepared_operations.append({
                            "product_id": product_id,
                            "type": "release", 
                            "quantity": quantity,
                            "old_reserved": item.reserved_quantity
                        })
                    
                    elif op_type == "transfer_out":
                        if item.quantity < quantity:
                            logger.error(f"❌ Insufficient inventory for transfer: {product_id}, available={item.quantity}, requested={quantity}")
                            return False
                        prepared_operations.append({
                            "product_id": product_id,
                            "type": "transfer_out",
                            "quantity": quantity,
                            "old_quantity": item.quantity
                        })
                    
                    elif op_type == "transfer_in":
                        prepared_operations.append({
                            "product_id": product_id,
                            "type": "transfer_in",
                            "quantity": quantity,
                            "old_quantity": item.quantity if product_id in self.inventory else 0
                        })
                
                # Store prepared operations
                self.prepared_transactions[transaction.transaction_id] = prepared_operations
                
                logger.info(f"✅ Transaction {transaction.transaction_id} prepared successfully at warehouse {self.warehouse.warehouse_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to prepare transaction {transaction.transaction_id}: {e}")
                return False
    
    async def commit_transaction(self, transaction: InventoryTransaction) -> bool:
        """Commit phase of 2PC - execute the prepared operations"""
        async with self.lock:
            try:
                logger.info(f"✅ Committing transaction {transaction.transaction_id} at warehouse {self.warehouse.warehouse_id}")
                
                if transaction.transaction_id not in self.prepared_transactions:
                    logger.error(f"❌ Transaction {transaction.transaction_id} not prepared")
                    return False
                
                prepared_ops = self.prepared_transactions[transaction.transaction_id]
                
                # Execute all prepared operations
                for op in prepared_ops:
                    product_id = op["product_id"]
                    op_type = op["type"]
                    quantity = op["quantity"]
                    
                    if product_id not in self.inventory:
                        # For transfer_in, create new inventory item
                        if op_type == "transfer_in":
                            self.inventory[product_id] = InventoryItem(
                                warehouse_id=self.warehouse.warehouse_id,
                                product_id=product_id,
                                quantity=0,
                                reserved_quantity=0,
                                location_in_warehouse=f"Aisle-{random.randint(1, 20)}-Shelf-{random.randint(1, 10)}",
                                last_updated=datetime.now(),
                                version=1
                            )
                        else:
                            logger.error(f"❌ Product {product_id} not found during commit")
                            return False
                    
                    item = self.inventory[product_id]
                    
                    if op_type == "reserve":
                        item.reserved_quantity += quantity
                    elif op_type == "release":
                        item.reserved_quantity -= quantity
                        item.quantity -= quantity  # Actually remove from inventory
                    elif op_type == "transfer_out":
                        item.quantity -= quantity
                    elif op_type == "transfer_in":
                        item.quantity += quantity
                    
                    # Update metadata
                    item.last_updated = datetime.now()
                    item.version += 1
                    
                    logger.info(f"📦 Updated {product_id}: quantity={item.quantity}, reserved={item.reserved_quantity}")
                
                # Clean up prepared transaction
                del self.prepared_transactions[transaction.transaction_id]
                
                logger.info(f"✅ Transaction {transaction.transaction_id} committed at warehouse {self.warehouse.warehouse_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to commit transaction {transaction.transaction_id}: {e}")
                return False
    
    async def abort_transaction(self, transaction: InventoryTransaction) -> bool:
        """Abort phase - rollback any prepared operations"""
        async with self.lock:
            try:
                logger.info(f"❌ Aborting transaction {transaction.transaction_id} at warehouse {self.warehouse.warehouse_id}")
                
                # Simply remove the prepared transaction (no changes were made yet)
                if transaction.transaction_id in self.prepared_transactions:
                    del self.prepared_transactions[transaction.transaction_id]
                    logger.info(f"❌ Transaction {transaction.transaction_id} aborted at warehouse {self.warehouse.warehouse_id}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to abort transaction {transaction.transaction_id}: {e}")
                return False
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get current inventory status for this warehouse"""
        total_products = len(self.inventory)
        total_quantity = sum(item.quantity for item in self.inventory.values())
        total_reserved = sum(item.reserved_quantity for item in self.inventory.values())
        
        return {
            "warehouse_id": self.warehouse.warehouse_id,
            "location": f"{self.warehouse.city}, {self.warehouse.state}",
            "total_products": total_products,
            "total_quantity": total_quantity,
            "total_reserved": total_reserved,
            "utilization": f"{(total_quantity / self.warehouse.capacity * 100):.1f}%",
            "active_transactions": len(self.prepared_transactions)
        }

class DistributedInventorySystem:
    """Complete distributed inventory management system"""
    
    def __init__(self):
        self.warehouses = {}  # warehouse_id -> WarehouseNode
        self.coordinator = TwoPhaseCommitCoordinator("coordinator_001")
        self.transaction_log = []
        
        # Initialize Indian warehouses
        self._initialize_warehouses()
        
        # System metrics
        self.metrics = {
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "average_transaction_time": 0.0,
            "system_uptime": datetime.now()
        }
    
    def _initialize_warehouses(self):
        """Initialize warehouses across India"""
        indian_warehouses = [
            {"id": "WH_MUM_001", "city": "Mumbai", "state": "Maharashtra", "coords": (19.0760, 72.8777)},
            {"id": "WH_DEL_001", "city": "Delhi", "state": "Delhi", "coords": (28.7041, 77.1025)},
            {"id": "WH_BLR_001", "city": "Bangalore", "state": "Karnataka", "coords": (12.9716, 77.5946)},
            {"id": "WH_HYD_001", "city": "Hyderabad", "state": "Telangana", "coords": (17.3850, 78.4867)},
            {"id": "WH_CHN_001", "city": "Chennai", "state": "Tamil Nadu", "coords": (13.0827, 80.2707)},
            {"id": "WH_KOL_001", "city": "Kolkata", "state": "West Bengal", "coords": (22.5726, 88.3639)},
            {"id": "WH_PUN_001", "city": "Pune", "state": "Maharashtra", "coords": (18.5204, 73.8567)},
            {"id": "WH_AHM_001", "city": "Ahmedabad", "state": "Gujarat", "coords": (23.0225, 72.5714)},
        ]
        
        for wh_info in indian_warehouses:
            warehouse = Warehouse(
                warehouse_id=wh_info["id"],
                location=f"{wh_info['city']}, {wh_info['state']}",
                city=wh_info["city"],
                state=wh_info["state"],
                coordinates=wh_info["coords"],
                capacity=10000,  # 10k units capacity
                current_utilization=0,
                is_active=True,
                node_address=f"192.168.1.{len(self.warehouses) + 10}:8080"
            )
            
            warehouse_node = WarehouseNode(warehouse)
            self.warehouses[wh_info["id"]] = warehouse_node
            
            logger.info(f"🏭 Initialized warehouse {wh_info['id']} in {wh_info['city']}")
    
    async def reserve_inventory(self, product_id: str, quantity: int, 
                              preferred_warehouses: List[str] = None) -> Optional[str]:
        """Reserve inventory across distributed warehouses"""
        
        # Find warehouses with sufficient inventory
        available_warehouses = []
        
        search_warehouses = preferred_warehouses if preferred_warehouses else list(self.warehouses.keys())
        
        for wh_id in search_warehouses:
            warehouse_node = self.warehouses[wh_id]
            if product_id in warehouse_node.inventory:
                item = warehouse_node.inventory[product_id]
                if item.available_quantity >= quantity:
                    available_warehouses.append(wh_id)
        
        if not available_warehouses:
            logger.error(f"❌ No warehouse has sufficient inventory for {product_id} (quantity: {quantity})")
            return None
        
        # Choose best warehouse (closest or highest availability)
        selected_warehouse = available_warehouses[0]  # Simplified selection
        
        # Create distributed transaction
        transaction_id = str(uuid.uuid4())
        transaction = InventoryTransaction(
            transaction_id=transaction_id,
            participant_warehouses=[selected_warehouse],
            operations=[{
                "warehouse_id": selected_warehouse,
                "product_id": product_id,
                "type": "reserve",
                "quantity": quantity
            }],
            status=TransactionStatus.UNKNOWN,
            coordinator_node="coordinator_001",
            timestamp=datetime.now()
        )
        
        # Execute transaction
        start_time = time.time()
        success = await self.coordinator.execute_distributed_transaction(transaction, self.warehouses)
        execution_time = time.time() - start_time
        
        # Update metrics
        self.metrics["total_transactions"] += 1
        if success:
            self.metrics["successful_transactions"] += 1
            self.transaction_log.append(transaction)
            logger.info(f"✅ Reserved {quantity} units of {product_id} from {selected_warehouse}")
            return transaction_id
        else:
            self.metrics["failed_transactions"] += 1
            logger.error(f"❌ Failed to reserve {quantity} units of {product_id}")
            return None
    
    async def transfer_inventory(self, product_id: str, quantity: int,
                               source_warehouse: str, target_warehouse: str) -> Optional[str]:
        """Transfer inventory between warehouses"""
        
        if source_warehouse not in self.warehouses or target_warehouse not in self.warehouses:
            logger.error(f"❌ Invalid warehouse IDs: {source_warehouse}, {target_warehouse}")
            return None
        
        # Check if source has sufficient inventory
        source_node = self.warehouses[source_warehouse]
        if product_id not in source_node.inventory:
            logger.error(f"❌ Product {product_id} not found in source warehouse {source_warehouse}")
            return None
        
        if source_node.inventory[product_id].quantity < quantity:
            logger.error(f"❌ Insufficient inventory in source warehouse for transfer")
            return None
        
        # Create distributed transaction for transfer
        transaction_id = str(uuid.uuid4())
        transaction = InventoryTransaction(
            transaction_id=transaction_id,
            participant_warehouses=[source_warehouse, target_warehouse],
            operations=[
                {
                    "warehouse_id": source_warehouse,
                    "product_id": product_id,
                    "type": "transfer_out",
                    "quantity": quantity
                },
                {
                    "warehouse_id": target_warehouse,
                    "product_id": product_id,
                    "type": "transfer_in",
                    "quantity": quantity
                }
            ],
            status=TransactionStatus.UNKNOWN,
            coordinator_node="coordinator_001",
            timestamp=datetime.now()
        )
        
        # Execute transaction
        start_time = time.time()
        success = await self.coordinator.execute_distributed_transaction(transaction, self.warehouses)
        execution_time = time.time() - start_time
        
        # Update metrics
        self.metrics["total_transactions"] += 1
        if success:
            self.metrics["successful_transactions"] += 1
            self.transaction_log.append(transaction)
            logger.info(f"✅ Transferred {quantity} units of {product_id} from {source_warehouse} to {target_warehouse}")
            return transaction_id
        else:
            self.metrics["failed_transactions"] += 1
            logger.error(f"❌ Failed to transfer inventory between warehouses")
            return None
    
    def get_global_inventory_status(self) -> Dict[str, Any]:
        """Get system-wide inventory status"""
        system_status = {
            "total_warehouses": len(self.warehouses),
            "active_warehouses": sum(1 for wh in self.warehouses.values() if wh.warehouse.is_active),
            "warehouse_details": {},
            "global_metrics": self.metrics.copy(),
            "recent_transactions": len([t for t in self.transaction_log 
                                     if (datetime.now() - t.timestamp).seconds < 3600])  # Last hour
        }
        
        # Add individual warehouse details
        for wh_id, warehouse_node in self.warehouses.items():
            system_status["warehouse_details"][wh_id] = warehouse_node.get_inventory_status()
        
        return system_status
    
    def print_system_dashboard(self):
        """Print comprehensive system dashboard"""
        status = self.get_global_inventory_status()
        
        print(f"\n{'='*80}")
        print(f"📦 FLIPKART DISTRIBUTED INVENTORY MANAGEMENT SYSTEM 📦")
        print(f"{'='*80}")
        
        print(f"🏭 System Overview:")
        print(f"   Total Warehouses: {status['total_warehouses']}")
        print(f"   Active Warehouses: {status['active_warehouses']}")
        print(f"   Recent Transactions (1hr): {status['recent_transactions']}")
        
        print(f"\n📊 Transaction Metrics:")
        metrics = status['global_metrics']
        print(f"   Total Transactions: {metrics['total_transactions']}")
        print(f"   Successful: {metrics['successful_transactions']}")
        print(f"   Failed: {metrics['failed_transactions']}")
        
        if metrics['total_transactions'] > 0:
            success_rate = (metrics['successful_transactions'] / metrics['total_transactions']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🏪 Warehouse Status:")
        for wh_id, wh_status in status['warehouse_details'].items():
            print(f"   {wh_id} ({wh_status['location']}):")
            print(f"     Products: {wh_status['total_products']}")
            print(f"     Total Quantity: {wh_status['total_quantity']:,}")
            print(f"     Reserved: {wh_status['total_reserved']:,}")
            print(f"     Utilization: {wh_status['utilization']}")
            print(f"     Active Transactions: {wh_status['active_transactions']}")
        
        uptime = datetime.now() - metrics['system_uptime']
        print(f"\n⏰ System Uptime: {uptime}")
        print(f"🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

async def simulate_flipkart_operations(system: DistributedInventorySystem, duration_minutes: int = 5):
    """Simulate realistic Flipkart inventory operations"""
    logger.info(f"🛒 Starting Flipkart inventory simulation for {duration_minutes} minutes")
    
    products = ["PHONE001", "LAPTOP001", "BOOK001", "SHIRT001", "SHOES001"]
    warehouses = list(system.warehouses.keys())
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    operation_count = 0
    
    try:
        while time.time() < end_time:
            operation_count += 1
            
            # Simulate different types of operations
            operation_type = random.choice(["reserve", "transfer", "status_check"])
            
            if operation_type == "reserve":
                # Customer order - reserve inventory
                product = random.choice(products)
                quantity = random.randint(1, 5)
                preferred_warehouses = random.sample(warehouses, 3)  # Check 3 warehouses
                
                logger.info(f"🛒 Customer order: Reserving {quantity} units of {product}")
                transaction_id = await system.reserve_inventory(product, quantity, preferred_warehouses)
                
                if transaction_id:
                    logger.info(f"✅ Order successful: transaction {transaction_id}")
                else:
                    logger.warning(f"❌ Order failed: insufficient inventory")
            
            elif operation_type == "transfer":
                # Inventory rebalancing between warehouses
                product = random.choice(products)
                quantity = random.randint(5, 20)
                source_wh = random.choice(warehouses)
                target_wh = random.choice([wh for wh in warehouses if wh != source_wh])
                
                logger.info(f"🚛 Inventory rebalancing: {quantity} units of {product} from {source_wh} to {target_wh}")
                transaction_id = await system.transfer_inventory(product, quantity, source_wh, target_wh)
                
                if transaction_id:
                    logger.info(f"✅ Transfer successful: transaction {transaction_id}")
                else:
                    logger.warning(f"❌ Transfer failed")
            
            elif operation_type == "status_check":
                # Print system status every few operations
                if operation_count % 20 == 0:
                    system.print_system_dashboard()
            
            # Add realistic delay between operations
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 Simulation completed! Processed {operation_count} operations")
    
    # Final system status
    system.print_system_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Flipkart Distributed Inventory Management System")
    print("📦 Complete distributed system with 2PC, consensus, और ACID transactions")
    print("🏭 Managing inventory across 8 warehouses in India...\n")
    
    # Initialize distributed system
    system = DistributedInventorySystem()
    
    print(f"✅ System initialized with {len(system.warehouses)} warehouses")
    
    # Print initial status
    system.print_system_dashboard()
    
    try:
        # Run simulation
        await simulate_flipkart_operations(system, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Handle 100,000+ inventory operations per minute")
        print(f"   - Strong consistency across 1500+ warehouses") 
        print(f"   - ACID transaction guarantees")
        print(f"   - Geographic distribution across India")
        print(f"   - 99.9% availability during high-traffic events")
        print(f"   - Real-time inventory synchronization")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the distributed inventory system demo
    asyncio.run(main())