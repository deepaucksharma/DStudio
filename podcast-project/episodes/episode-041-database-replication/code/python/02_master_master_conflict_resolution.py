#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 2: Master-Master Conflict Resolution - UPI Transaction System

यह example UPI जैसे real-time payment system में master-master replication
के conflicts को handle करने का advanced approach दिखाता है।
Multi-master setup में data conflicts का resolution critical होता है।

Real-world Use Case: UPI Payment Processing
- Multiple payment gateways (PhonePe, Paytm, GPay) processing simultaneously
- Conflict resolution using vector clocks and timestamp ordering
- Banking compliance और NPCI guidelines के according
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
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConflictResolutionStrategy(Enum):
    LAST_WRITE_WINS = "last_write_wins"
    VECTOR_CLOCK = "vector_clock"
    BUSINESS_LOGIC = "business_logic"
    MANUAL_RESOLUTION = "manual_resolution"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMMITTED = "committed"
    ABORTED = "aborted"
    CONFLICT = "conflict"

@dataclass
class VectorClock:
    """Vector clock for distributed systems conflict resolution"""
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str):
        """Apne node ka clock increment करना"""
        self.clocks[node_id] = self.clocks.get(node_id, 0) + 1
        
    def update(self, other: 'VectorClock'):
        """Dusre node के clock ke saath merge करना"""
        for node_id, clock_value in other.clocks.items():
            self.clocks[node_id] = max(self.clocks.get(node_id, 0), clock_value)
            
    def compare(self, other: 'VectorClock') -> str:
        """
        Vector clocks comparison
        Returns: 'before', 'after', 'concurrent', or 'equal'
        """
        self_dominates = False
        other_dominates = False
        
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        
        for node in all_nodes:
            self_val = self.clocks.get(node, 0)
            other_val = other.clocks.get(node, 0)
            
            if self_val > other_val:
                self_dominates = True
            elif self_val < other_val:
                other_dominates = True
                
        if self_dominates and not other_dominates:
            return 'after'
        elif other_dominates and not self_dominates:
            return 'before'
        elif not self_dominates and not other_dominates:
            return 'equal'
        else:
            return 'concurrent'

@dataclass
class UPITransaction:
    """UPI transaction with conflict resolution metadata"""
    transaction_id: str
    from_vpa: str  # Virtual Payment Address
    to_vpa: str
    amount: float
    timestamp: datetime
    originating_node: str
    vector_clock: VectorClock
    status: TransactionStatus = TransactionStatus.PENDING
    checksum: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Transaction checksum generation for integrity"""
        content = f"{self.transaction_id}{self.from_vpa}{self.to_vpa}{self.amount}{self.timestamp}"
        self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]

class UPIMasterNode:
    """
    Master node in UPI multi-master setup
    हर node independently transactions process कर सकता है
    """
    
    def __init__(self, node_id: str, region: str):
        self.node_id = node_id
        self.region = region
        self.vector_clock = VectorClock()
        self.peer_nodes: Dict[str, 'UPIMasterNode'] = {}
        
        # Local state
        self.transactions: Dict[str, UPITransaction] = {}
        self.account_balances: Dict[str, float] = defaultdict(float)
        self.pending_conflicts: List[Tuple[str, str]] = []  # (tx_id1, tx_id2)
        
        # Network state
        self.is_active = True
        self.network_partitioned = False
        
        # Performance metrics
        self.processed_transactions = 0
        self.conflicts_resolved = 0
        
        # Initialize with some test accounts (UPI VPAs)
        self._initialize_test_accounts()
        
    def _initialize_test_accounts(self):
        """Test UPI accounts के लिए initial balances"""
        test_accounts = [
            "rajesh@paytm", "priya@phonepe", "amit@googlepay", 
            "sunita@amazonpay", "vikram@bhim", "neha@axis"
        ]
        
        for vpa in test_accounts:
            self.account_balances[vpa] = 10000.0  # ₹10,000 initial balance
            
    def add_peer(self, peer_node: 'UPIMasterNode'):
        """Peer master nodes add करना"""
        self.peer_nodes[peer_node.node_id] = peer_node
        logger.info(f"Peer {peer_node.node_id} added to {self.node_id}")
        
    async def process_transaction(self, from_vpa: str, to_vpa: str, 
                                amount: float, metadata: Dict = None) -> Tuple[bool, str, UPITransaction]:
        """
        UPI transaction processing with conflict detection
        यहाँ NPCI guidelines के according validation होती है
        """
        if not self.is_active:
            return False, "Node is down", None
            
        # Generate transaction ID (UPI format)
        tx_id = f"UPI{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        
        # Increment vector clock
        self.vector_clock.increment(self.node_id)
        
        # Create transaction
        transaction = UPITransaction(
            transaction_id=tx_id,
            from_vpa=from_vpa,
            to_vpa=to_vpa,
            amount=amount,
            timestamp=datetime.now(),
            originating_node=self.node_id,
            vector_clock=VectorClock(self.vector_clock.clocks.copy()),
            metadata=metadata or {}
        )
        
        # Business logic validation
        if not self._validate_transaction(transaction):
            return False, "Transaction validation failed", None
            
        # Check for sufficient balance
        if self.account_balances[from_vpa] < amount:
            return False, f"Insufficient balance. Available: ₹{self.account_balances[from_vpa]}", None
            
        # Store transaction as pending
        self.transactions[tx_id] = transaction
        
        # Propagate to peer nodes
        await self._propagate_to_peers(transaction)
        
        # Process locally if no conflicts
        success = await self._commit_transaction(transaction)
        
        if success:
            self.processed_transactions += 1
            logger.info(f"Transaction {tx_id} processed successfully on {self.node_id}")
            return True, tx_id, transaction
        else:
            transaction.status = TransactionStatus.CONFLICT
            logger.warning(f"Transaction {tx_id} has conflicts, queued for resolution")
            return False, "Transaction in conflict, queued for resolution", transaction
            
    def _validate_transaction(self, transaction: UPITransaction) -> bool:
        """UPI transaction validation rules"""
        # Basic UPI validation
        if transaction.amount <= 0:
            return False
            
        if transaction.amount > 100000:  # UPI daily limit
            return False
            
        if not transaction.from_vpa or not transaction.to_vpa:
            return False
            
        if transaction.from_vpa == transaction.to_vpa:
            return False
            
        # VPA format validation (basic)
        for vpa in [transaction.from_vpa, transaction.to_vpa]:
            if '@' not in vpa:
                return False
                
        return True
        
    async def _propagate_to_peers(self, transaction: UPITransaction):
        """Peer nodes को transaction propagate करना"""
        if self.network_partitioned:
            return
            
        propagation_tasks = []
        
        for peer_id, peer_node in self.peer_nodes.items():
            if peer_node.is_active:
                task = asyncio.create_task(peer_node.receive_transaction(transaction))
                propagation_tasks.append(task)
                
        if propagation_tasks:
            try:
                await asyncio.gather(*propagation_tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Propagation error: {e}")
                
    async def receive_transaction(self, transaction: UPITransaction):
        """
        Peer node से transaction receive करना
        यहाँ conflict detection होती है
        """
        if not self.is_active:
            return
            
        # Update vector clock
        self.vector_clock.update(transaction.vector_clock)
        self.vector_clock.increment(self.node_id)
        
        # Check for conflicts
        conflict_detected = self._detect_conflicts(transaction)
        
        if conflict_detected:
            logger.warning(f"Conflict detected for transaction {transaction.transaction_id} on {self.node_id}")
            self.pending_conflicts.append((transaction.transaction_id, conflict_detected))
            transaction.status = TransactionStatus.CONFLICT
        else:
            # No conflict, can process
            await self._commit_transaction(transaction)
            
        # Store transaction
        self.transactions[transaction.transaction_id] = transaction
        
    def _detect_conflicts(self, new_transaction: UPITransaction) -> Optional[str]:
        """
        Conflict detection logic
        UPI में same account se concurrent transactions का detection
        """
        for existing_id, existing_tx in self.transactions.items():
            if existing_tx.status == TransactionStatus.PENDING:
                
                # Check for double spending
                if (existing_tx.from_vpa == new_transaction.from_vpa and 
                    existing_tx.originating_node != new_transaction.originating_node):
                    
                    # Check if transactions are concurrent using vector clocks
                    clock_comparison = existing_tx.vector_clock.compare(new_transaction.vector_clock)
                    
                    if clock_comparison == 'concurrent':
                        return existing_id
                        
        return None
        
    async def _commit_transaction(self, transaction: UPITransaction) -> bool:
        """Transaction commit करना"""
        try:
            # Double-check balance
            if self.account_balances[transaction.from_vpa] >= transaction.amount:
                
                # Apply transaction
                self.account_balances[transaction.from_vpa] -= transaction.amount
                self.account_balances[transaction.to_vpa] += transaction.amount
                
                transaction.status = TransactionStatus.COMMITTED
                
                logger.info(f"Transaction {transaction.transaction_id} committed on {self.node_id}")
                return True
            else:
                transaction.status = TransactionStatus.ABORTED
                return False
                
        except Exception as e:
            logger.error(f"Commit error for {transaction.transaction_id}: {e}")
            transaction.status = TransactionStatus.ABORTED
            return False
            
    async def resolve_conflicts(self, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.VECTOR_CLOCK):
        """
        Conflict resolution using different strategies
        UPI में real-time conflict resolution critical है
        """
        resolved_count = 0
        
        for conflict_pair in self.pending_conflicts.copy():
            tx_id1, tx_id2 = conflict_pair
            
            if tx_id1 in self.transactions and tx_id2 in self.transactions:
                tx1 = self.transactions[tx_id1]
                tx2 = self.transactions[tx_id2]
                
                winner, loser = self._resolve_conflict_pair(tx1, tx2, strategy)
                
                if winner and loser:
                    # Commit winner, abort loser
                    if await self._commit_transaction(winner):
                        loser.status = TransactionStatus.ABORTED
                        logger.info(f"Conflict resolved: {winner.transaction_id} won, {loser.transaction_id} aborted")
                        resolved_count += 1
                        self.conflicts_resolved += 1
                        
                    # Remove from pending conflicts
                    self.pending_conflicts.remove(conflict_pair)
                    
        return resolved_count
        
    def _resolve_conflict_pair(self, tx1: UPITransaction, tx2: UPITransaction, 
                             strategy: ConflictResolutionStrategy) -> Tuple[UPITransaction, UPITransaction]:
        """Conflict resolution strategies"""
        
        if strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            # Timestamp based resolution
            if tx1.timestamp > tx2.timestamp:
                return tx1, tx2
            else:
                return tx2, tx1
                
        elif strategy == ConflictResolutionStrategy.VECTOR_CLOCK:
            # Vector clock based resolution
            comparison = tx1.vector_clock.compare(tx2.vector_clock)
            
            if comparison == 'after':
                return tx1, tx2
            elif comparison == 'before':
                return tx2, tx1
            else:
                # Fall back to business logic for concurrent events
                return self._business_logic_resolution(tx1, tx2)
                
        elif strategy == ConflictResolutionStrategy.BUSINESS_LOGIC:
            return self._business_logic_resolution(tx1, tx2)
            
        return None, None
        
    def _business_logic_resolution(self, tx1: UPITransaction, tx2: UPITransaction) -> Tuple[UPITransaction, UPITransaction]:
        """
        Business logic based conflict resolution
        UPI specific rules for transaction priority
        """
        # Priority rules for UPI:
        # 1. Higher amount transactions get priority (for bank's revenue)
        # 2. If amounts equal, earlier timestamp wins
        # 3. If timestamp difference < 1ms, node ID based (deterministic)
        
        if tx1.amount > tx2.amount:
            return tx1, tx2
        elif tx2.amount > tx1.amount:
            return tx2, tx1
        else:
            # Equal amounts, use timestamp
            if tx1.timestamp < tx2.timestamp:
                return tx1, tx2
            elif tx2.timestamp < tx1.timestamp:
                return tx2, tx1
            else:
                # Use deterministic ordering based on node ID
                if tx1.originating_node < tx2.originating_node:
                    return tx1, tx2
                else:
                    return tx2, tx1
                    
    def get_node_status(self) -> Dict:
        """Node status information"""
        conflict_count = len(self.pending_conflicts)
        committed_count = len([tx for tx in self.transactions.values() 
                             if tx.status == TransactionStatus.COMMITTED])
        
        return {
            "node_id": self.node_id,
            "region": self.region,
            "active": self.is_active,
            "network_partitioned": self.network_partitioned,
            "vector_clock": self.vector_clock.clocks,
            "total_transactions": len(self.transactions),
            "committed_transactions": committed_count,
            "pending_conflicts": conflict_count,
            "processed_transactions": self.processed_transactions,
            "conflicts_resolved": self.conflicts_resolved,
            "connected_peers": len([p for p in self.peer_nodes.values() if p.is_active])
        }

class UPICluster:
    """Complete UPI multi-master cluster"""
    
    def __init__(self):
        # Create master nodes for different regions
        self.nodes = {
            "UPI-Master-Mumbai": UPIMasterNode("UPI-Master-Mumbai", "West"),
            "UPI-Master-Bangalore": UPIMasterNode("UPI-Master-Bangalore", "South"),
            "UPI-Master-Delhi": UPIMasterNode("UPI-Master-Delhi", "North"),
            "UPI-Master-Hyderabad": UPIMasterNode("UPI-Master-Hyderabad", "South"),
        }
        
        # Setup peer connections (full mesh)
        self._setup_peer_connections()
        
    def _setup_peer_connections(self):
        """Setup peer-to-peer connections between all nodes"""
        node_list = list(self.nodes.values())
        
        for i, node in enumerate(node_list):
            for j, peer in enumerate(node_list):
                if i != j:
                    node.add_peer(peer)
                    
    async def simulate_upi_load(self, transactions_count: int = 50, 
                              conflict_probability: float = 0.2):
        """
        Simulate realistic UPI transaction load
        Mumbai की rush hour में typical UPI usage pattern
        """
        logger.info(f"Starting UPI load simulation: {transactions_count} transactions")
        
        import random
        
        # Common UPI VPAs for testing
        vpas = [
            "rajesh@paytm", "priya@phonepe", "amit@googlepay", 
            "sunita@amazonpay", "vikram@bhim", "neha@axis",
            "deepak@paytm", "kavya@phonepe", "rohit@googlepay"
        ]
        
        # Transaction scenarios
        scenarios = [
            {"amount_range": (100, 1000), "frequency": 0.6, "desc": "Regular payments"},
            {"amount_range": (1000, 5000), "frequency": 0.3, "desc": "Bill payments"},
            {"amount_range": (5000, 25000), "frequency": 0.1, "desc": "Large transfers"}
        ]
        
        tasks = []
        
        for i in range(transactions_count):
            # Select random scenario
            scenario = random.choices(scenarios, weights=[s["frequency"] for s in scenarios])[0]
            amount = round(random.uniform(*scenario["amount_range"]), 2)
            
            # Select random VPAs
            from_vpa = random.choice(vpas)
            to_vpa = random.choice([v for v in vpas if v != from_vpa])
            
            # Select random node (simulating different app usage)
            node = random.choice(list(self.nodes.values()))
            
            # Add some intentional conflicts
            if random.random() < conflict_probability:
                # Create potentially conflicting transaction
                # (same from_vpa, high amount)
                amount = 8000  # High amount to create conflict potential
                
            metadata = {
                "app": random.choice(["PhonePe", "Paytm", "GPay", "BHIM"]),
                "purpose": random.choice(["Food", "Transport", "Bills", "Shopping", "Transfer"]),
                "location": random.choice(["Mumbai", "Delhi", "Bangalore", "Hyderabad"])
            }
            
            task = asyncio.create_task(
                node.process_transaction(from_vpa, to_vpa, amount, metadata)
            )
            tasks.append(task)
            
            # Small delay for realistic timing
            await asyncio.sleep(0.01)
            
        # Wait for all transactions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        successful = sum(1 for r in results if isinstance(r, tuple) and r[0])
        failed = len(results) - successful
        
        logger.info(f"UPI load simulation completed: {successful} successful, {failed} failed/conflicted")
        
        # Resolve conflicts
        total_resolved = 0
        for node in self.nodes.values():
            resolved = await node.resolve_conflicts()
            total_resolved += resolved
            
        logger.info(f"Conflict resolution completed: {total_resolved} conflicts resolved")
        
        return successful, failed, total_resolved
        
    def get_cluster_status(self) -> Dict:
        """Complete cluster status"""
        total_transactions = sum(len(node.transactions) for node in self.nodes.values())
        total_conflicts = sum(len(node.pending_conflicts) for node in self.nodes.values())
        
        return {
            "cluster_size": len(self.nodes),
            "active_nodes": len([n for n in self.nodes.values() if n.is_active]),
            "total_transactions": total_transactions,
            "pending_conflicts": total_conflicts,
            "nodes": {node_id: node.get_node_status() for node_id, node in self.nodes.items()}
        }

# Testing and demonstration
async def demonstrate_master_master_conflicts():
    """
    Complete demonstration of master-master conflict resolution
    Real UPI scenario के साथ comprehensive testing
    """
    print("\n" + "="*70)
    print("UPI Master-Master Conflict Resolution Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*70)
    
    # Initialize UPI cluster
    cluster = UPICluster()
    
    logger.info("UPI Multi-Master Cluster initialized")
    logger.info(f"Nodes: {list(cluster.nodes.keys())}")
    
    # Demonstrate simple transactions first
    logger.info("\n--- Processing Simple UPI Transactions ---")
    
    node_mumbai = cluster.nodes["UPI-Master-Mumbai"]
    node_bangalore = cluster.nodes["UPI-Master-Bangalore"]
    
    # Simple transaction
    success, tx_id, tx = await node_mumbai.process_transaction(
        "rajesh@paytm", "priya@phonepe", 500.0, 
        {"purpose": "Lunch payment", "restaurant": "Toit, Bangalore"}
    )
    print(f"Simple transaction: {'Success' if success else 'Failed'} - {tx_id}")
    
    await asyncio.sleep(1)  # Allow propagation
    
    # Demonstrate intentional conflict
    logger.info("\n--- Creating Intentional Conflicts ---")
    
    # Create concurrent transactions from same account (potential conflict)
    task1 = asyncio.create_task(
        node_mumbai.process_transaction(
            "amit@googlepay", "vikram@bhim", 5000.0,
            {"purpose": "Rent payment", "location": "Mumbai"}
        )
    )
    
    task2 = asyncio.create_task(
        node_bangalore.process_transaction(
            "amit@googlepay", "neha@axis", 4000.0,
            {"purpose": "Shopping", "location": "Bangalore"}
        )
    )
    
    result1, result2 = await asyncio.gather(task1, task2)
    
    print(f"Concurrent Transaction 1: {'Success' if result1[0] else 'Conflict'} - {result1[1]}")
    print(f"Concurrent Transaction 2: {'Success' if result2[0] else 'Conflict'} - {result2[1]}")
    
    # Check for conflicts
    await asyncio.sleep(2)  # Allow conflict detection
    
    logger.info("\n--- Cluster Status Before Conflict Resolution ---")
    status = cluster.get_cluster_status()
    print(f"Total transactions: {status['total_transactions']}")
    print(f"Pending conflicts: {status['pending_conflicts']}")
    
    # Resolve conflicts
    logger.info("\n--- Resolving Conflicts ---")
    
    total_resolved = 0
    for node_id, node in cluster.nodes.items():
        resolved = await node.resolve_conflicts(ConflictResolutionStrategy.VECTOR_CLOCK)
        if resolved > 0:
            print(f"{node_id}: Resolved {resolved} conflicts")
            total_resolved += resolved
            
    print(f"Total conflicts resolved: {total_resolved}")
    
    # Simulate realistic load
    logger.info("\n--- Simulating Realistic UPI Load ---")
    
    successful, failed, resolved = await cluster.simulate_upi_load(
        transactions_count=30, 
        conflict_probability=0.15
    )
    
    print(f"Load simulation results:")
    print(f"  Successful: {successful}")
    print(f"  Failed/Conflicted: {failed}")
    print(f"  Conflicts resolved: {resolved}")
    
    # Final cluster status
    logger.info("\n--- Final Cluster Status ---")
    final_status = cluster.get_cluster_status()
    
    print(f"Cluster Summary:")
    print(f"  Active nodes: {final_status['active_nodes']}/{final_status['cluster_size']}")
    print(f"  Total transactions: {final_status['total_transactions']}")
    print(f"  Pending conflicts: {final_status['pending_conflicts']}")
    
    print(f"\nPer-node Statistics:")
    for node_id, node_status in final_status['nodes'].items():
        print(f"  {node_id}:")
        print(f"    Committed: {node_status['committed_transactions']}")
        print(f"    Conflicts resolved: {node_status['conflicts_resolved']}")
        print(f"    Vector clock: {node_status['vector_clock']}")

if __name__ == "__main__":
    print("UPI Master-Master Conflict Resolution System")
    print("Episode 41: Database Replication Strategies")
    print("Demonstrating advanced conflict resolution in UPI-like systems...")
    
    # Run the demonstration
    asyncio.run(demonstrate_master_master_conflicts())