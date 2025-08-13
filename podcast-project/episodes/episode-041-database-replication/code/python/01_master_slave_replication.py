#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 1: Master-Slave Replication Simulator - HDFC Bank Scenario

Isme humne HDFC Bank ke transaction processing ka master-slave setup simulate kiya hai.
Master node pe sabhi writes hote hain, aur slave nodes pe reads distribute kiye jaate hain.
यह real-world banking scenario है जहां consistency critical है।

Real-world Use Case: HDFC Bank's core banking system
- Master handles all transaction writes
- Slaves handle customer balance inquiries and reports
- Replication lag monitoring for compliance
"""

import asyncio
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReplicationStatus(Enum):
    HEALTHY = "healthy"
    LAGGING = "lagging"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class Transaction:
    """Banking transaction data structure"""
    transaction_id: str
    account_number: str
    transaction_type: str  # DEBIT, CREDIT, TRANSFER
    amount: float
    timestamp: datetime
    metadata: Dict
    
class BankingMasterNode:
    """
    Master node for HDFC banking system
    सभी write operations यहाँ process होते हैं
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.accounts: Dict[str, float] = {}  # Account balances
        self.transaction_log: List[Transaction] = []
        self.slave_nodes: List['BankingSlaveNode'] = []
        self.is_active = True
        self.replication_queue: asyncio.Queue = asyncio.Queue()
        
        # Mumbai banking hours simulation
        self.peak_hours = [(9, 11), (14, 16), (19, 21)]  # Rush hours
        
    def add_slave(self, slave_node: 'BankingSlaveNode'):
        """नया slave node add करना"""
        self.slave_nodes.append(slave_node)
        logger.info(f"Slave node {slave_node.node_id} को master {self.node_id} के साथ जोड़ा गया")
        
    async def process_transaction(self, account_number: str, transaction_type: str, 
                                amount: float, metadata: Dict = None) -> Tuple[bool, str]:
        """
        Banking transaction processing
        यहाँ actual HDFC banking logic simulate की गई है
        """
        if not self.is_active:
            return False, "Master node is down"
            
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Account balance validation
        if account_number not in self.accounts:
            self.accounts[account_number] = 0.0
            
        current_balance = self.accounts[account_number]
        
        # Transaction validation (जैसे HDFC में होता है)
        if transaction_type == "DEBIT" and current_balance < amount:
            return False, f"Insufficient balance. Current: ₹{current_balance}, Required: ₹{amount}"
            
        # Apply transaction
        if transaction_type == "DEBIT":
            self.accounts[account_number] -= amount
        elif transaction_type == "CREDIT":
            self.accounts[account_number] += amount
            
        # Create transaction record
        transaction = Transaction(
            transaction_id=transaction_id,
            account_number=account_number,
            transaction_type=transaction_type,
            amount=amount,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        self.transaction_log.append(transaction)
        
        # Queue for replication to slaves
        await self.replication_queue.put(transaction)
        
        logger.info(f"Transaction processed: {transaction_id} - {transaction_type} ₹{amount} for account {account_number}")
        
        return True, transaction_id
        
    async def replicate_to_slaves(self):
        """
        Asynchronous replication to slave nodes
        यह background में continuously चलता रहता है
        """
        while self.is_active:
            try:
                # Wait for transaction to replicate
                transaction = await asyncio.wait_for(self.replication_queue.get(), timeout=1.0)
                
                # Replicate to all healthy slaves
                replication_tasks = []
                for slave in self.slave_nodes:
                    if slave.status == ReplicationStatus.HEALTHY:
                        task = asyncio.create_task(slave.receive_replication(transaction))
                        replication_tasks.append(task)
                
                if replication_tasks:
                    # Wait for all replications to complete
                    results = await asyncio.gather(*replication_tasks, return_exceptions=True)
                    
                    # Check for failed replications
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Replication failed to slave {self.slave_nodes[i].node_id}: {result}")
                            self.slave_nodes[i].status = ReplicationStatus.FAILED
                            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Replication error: {e}")
                
    def get_master_status(self) -> Dict:
        """Master node की current status"""
        return {
            "node_id": self.node_id,
            "active": self.is_active,
            "total_accounts": len(self.accounts),
            "total_transactions": len(self.transaction_log),
            "connected_slaves": len([s for s in self.slave_nodes if s.status == ReplicationStatus.HEALTHY]),
            "queue_size": self.replication_queue.qsize()
        }

class BankingSlaveNode:
    """
    Slave node for read operations
    यहाँ balance inquiries और reports generate होते हैं
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.accounts: Dict[str, float] = {}
        self.transaction_log: List[Transaction] = []
        self.status = ReplicationStatus.HEALTHY
        self.last_sync_time = datetime.now()
        self.replication_lag = 0.0  # milliseconds
        
        # Mumbai branch simulation
        self.branch_location = f"Mumbai Branch {node_id[-1]}"
        
    async def receive_replication(self, transaction: Transaction):
        """
        Master से replication data receive करना
        यहाँ eventual consistency maintain होती है
        """
        start_time = time.time()
        
        try:
            # Simulate network latency (Mumbai to Pune datacenter)
            await asyncio.sleep(0.01)  # 10ms latency
            
            # Apply transaction to local state
            if transaction.account_number not in self.accounts:
                self.accounts[transaction.account_number] = 0.0
                
            if transaction.transaction_type == "DEBIT":
                self.accounts[transaction.account_number] -= transaction.amount
            elif transaction.transaction_type == "CREDIT":
                self.accounts[transaction.account_number] += transaction.amount
                
            self.transaction_log.append(transaction)
            self.last_sync_time = datetime.now()
            
            # Calculate replication lag
            self.replication_lag = (time.time() - start_time) * 1000
            
            logger.info(f"Slave {self.node_id}: Replicated transaction {transaction.transaction_id}")
            
        except Exception as e:
            self.status = ReplicationStatus.FAILED
            raise e
            
    def get_account_balance(self, account_number: str) -> Optional[float]:
        """
        Customer balance inquiry (read operation)
        यह operation slave पर होता है load distribution के लिए
        """
        if self.status != ReplicationStatus.HEALTHY:
            raise Exception(f"Slave node {self.node_id} is not healthy")
            
        return self.accounts.get(account_number, 0.0)
        
    def generate_statement(self, account_number: str, 
                         start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Account statement generation
        Heavy read operation जो slave पर efficiently होता है
        """
        if self.status != ReplicationStatus.HEALTHY:
            raise Exception(f"Slave node {self.node_id} is not healthy")
            
        statement = []
        for transaction in self.transaction_log:
            if (transaction.account_number == account_number and 
                start_date <= transaction.timestamp <= end_date):
                statement.append({
                    "transaction_id": transaction.transaction_id,
                    "type": transaction.transaction_type,
                    "amount": transaction.amount,
                    "timestamp": transaction.timestamp.isoformat(),
                    "branch": self.branch_location
                })
                
        return statement
        
    def get_slave_status(self) -> Dict:
        """Slave node की health status"""
        return {
            "node_id": self.node_id,
            "branch": self.branch_location,
            "status": self.status.value,
            "last_sync": self.last_sync_time.isoformat(),
            "replication_lag_ms": self.replication_lag,
            "total_accounts": len(self.accounts),
            "total_transactions": len(self.transaction_log)
        }

class HDFCBankingCluster:
    """
    Complete HDFC banking cluster simulation
    Master-Slave architecture with monitoring
    """
    
    def __init__(self):
        self.master = BankingMasterNode("HDFC-Master-Mumbai")
        self.slaves = [
            BankingSlaveNode("HDFC-Slave-Pune"),
            BankingSlaveNode("HDFC-Slave-Delhi"),
            BankingSlaveNode("HDFC-Slave-Bangalore")
        ]
        
        # Add slaves to master
        for slave in self.slaves:
            self.master.add_slave(slave)
            
        self.monitoring_enabled = True
        
    async def start_cluster(self):
        """Cluster startup"""
        logger.info("Starting HDFC Banking Cluster...")
        
        # Start master replication process
        replication_task = asyncio.create_task(self.master.replicate_to_slaves())
        
        # Start monitoring
        monitoring_task = asyncio.create_task(self.monitor_cluster())
        
        return replication_task, monitoring_task
        
    async def monitor_cluster(self):
        """
        Cluster health monitoring
        Real-time replication lag और node health check
        """
        while self.monitoring_enabled:
            await asyncio.sleep(5)  # Monitor every 5 seconds
            
            master_status = self.master.get_master_status()
            logger.info(f"Master Status: {master_status}")
            
            for slave in self.slaves:
                slave_status = slave.get_slave_status()
                
                # Check for high replication lag (>100ms is concerning)
                if slave_status["replication_lag_ms"] > 100:
                    logger.warning(f"High replication lag detected on {slave.node_id}: "
                                 f"{slave_status['replication_lag_ms']:.2f}ms")
                    slave.status = ReplicationStatus.LAGGING
                    
                logger.info(f"Slave Status: {slave_status}")
                
    async def simulate_banking_load(self, duration_minutes: int = 5):
        """
        Simulate realistic banking load
        Mumbai banking hours में typical transaction pattern
        """
        logger.info(f"Starting banking load simulation for {duration_minutes} minutes...")
        
        start_time = time.time()
        transaction_count = 0
        
        while (time.time() - start_time) < (duration_minutes * 60):
            # Generate random banking transactions
            account_number = f"HDFC{uuid.uuid4().hex[:8].upper()}"
            
            # Simulate different transaction types
            import random
            transaction_type = random.choice(["CREDIT", "DEBIT", "CREDIT", "DEBIT", "CREDIT"])
            amount = round(random.uniform(100, 50000), 2)
            
            metadata = {
                "branch": "Mumbai Central",
                "channel": random.choice(["ATM", "Net Banking", "Mobile App", "Branch"]),
                "city": "Mumbai"
            }
            
            success, result = await self.master.process_transaction(
                account_number, transaction_type, amount, metadata
            )
            
            if success:
                transaction_count += 1
            else:
                logger.warning(f"Transaction failed: {result}")
                
            # Simulate realistic transaction frequency
            await asyncio.sleep(0.1)  # 10 TPS
            
        logger.info(f"Load simulation completed. Processed {transaction_count} transactions.")

# Testing and demonstration functions
async def demonstrate_master_slave_replication():
    """
    Complete demonstration of master-slave replication
    यह function real HDFC banking scenario को simulate करता है
    """
    print("\n" + "="*60)
    print("HDFC Bank Master-Slave Replication Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*60)
    
    # Initialize cluster
    cluster = HDFCBankingCluster()
    
    # Start cluster
    replication_task, monitoring_task = await cluster.start_cluster()
    
    # Simulate some banking transactions
    logger.info("\n--- Processing Sample Banking Transactions ---")
    
    # Sample customer transactions
    sample_transactions = [
        ("HDFC12345678", "CREDIT", 50000, {"type": "Salary", "employer": "TCS"}),
        ("HDFC12345678", "DEBIT", 5000, {"type": "ATM Withdrawal", "location": "Bandra"}),
        ("HDFC87654321", "CREDIT", 25000, {"type": "FD Maturity"}),
        ("HDFC12345678", "DEBIT", 15000, {"type": "UPI Transfer", "beneficiary": "Zomato"}),
        ("HDFC87654321", "DEBIT", 8000, {"type": "Credit Card Payment"}),
    ]
    
    for account, tx_type, amount, metadata in sample_transactions:
        success, result = await cluster.master.process_transaction(account, tx_type, amount, metadata)
        print(f"Transaction: {tx_type} ₹{amount} - {'Success' if success else 'Failed'}: {result}")
        await asyncio.sleep(1)  # Small delay for replication
        
    # Wait for replication to complete
    await asyncio.sleep(2)
    
    # Demonstrate read operations from slaves
    logger.info("\n--- Reading from Slave Nodes ---")
    
    for slave in cluster.slaves:
        try:
            balance = slave.get_account_balance("HDFC12345678")
            print(f"{slave.branch_location} - Account Balance: ₹{balance}")
            
            # Generate statement
            statement = slave.generate_statement(
                "HDFC12345678", 
                datetime.now() - timedelta(hours=1),
                datetime.now()
            )
            print(f"{slave.branch_location} - Statement entries: {len(statement)}")
            
        except Exception as e:
            print(f"Error reading from {slave.node_id}: {e}")
            
    # Run load simulation
    await cluster.simulate_banking_load(duration_minutes=1)
    
    # Final cluster status
    logger.info("\n--- Final Cluster Status ---")
    print(f"Master: {cluster.master.get_master_status()}")
    for slave in cluster.slaves:
        print(f"Slave: {slave.get_slave_status()}")
        
    # Cleanup
    cluster.monitoring_enabled = False
    cluster.master.is_active = False

if __name__ == "__main__":
    print("HDFC Bank Master-Slave Replication Simulator")
    print("Episode 41: Database Replication Strategies")
    print("Simulating real-world banking transaction replication...")
    
    # Run the demonstration
    asyncio.run(demonstrate_master_slave_replication())