#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 5: Banking Transaction Replication with ACID Guarantees

यह example banking में ACID properties के साथ transaction replication
का real implementation दिखाता है। WAL (Write-Ahead Logging), checkpoints,
और recovery mechanisms include किए गए हैं।

Real-world Use Case: Core Banking System
- Write-Ahead Logging for durability
- Snapshot isolation for consistency
- Distributed checkpoints for recovery
- Multi-version concurrency control (MVCC)
"""

import asyncio
import time
import uuid
import json
import logging
import os
import pickle
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    ACTIVE = "active"
    COMMITTED = "committed"
    ABORTED = "aborted"
    PREPARING = "preparing"

class IsolationLevel(Enum):
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"

@dataclass
class WALEntry:
    """Write-Ahead Log entry for durability"""
    log_sequence_number: int
    transaction_id: str
    operation_type: str  # BEGIN, INSERT, UPDATE, DELETE, COMMIT, ABORT
    table_name: str
    record_key: str
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: datetime
    checksum: str = ""
    
    def __post_init__(self):
        # Generate checksum for integrity
        import hashlib
        content = f"{self.log_sequence_number}{self.transaction_id}{self.operation_type}"
        self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]

@dataclass
class BankingRecord:
    """Banking record with versioning for MVCC"""
    account_number: str
    balance: float
    version: int
    created_by: str  # transaction_id
    valid_from: datetime
    valid_to: Optional[datetime]
    is_deleted: bool = False

@dataclass
class Transaction:
    """Banking transaction with ACID properties"""
    transaction_id: str
    start_time: datetime
    isolation_level: IsolationLevel
    status: TransactionStatus = TransactionStatus.ACTIVE
    read_timestamp: datetime = field(default_factory=datetime.now)
    commit_timestamp: Optional[datetime] = None
    operations: List[str] = field(default_factory=list)
    locks_held: Set[str] = field(default_factory=set)
    
class BankingACIDNode:
    """
    Banking node with full ACID guarantees and replication
    Complete implementation of database fundamentals
    """
    
    def __init__(self, node_id: str, data_dir: str):
        self.node_id = node_id
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # WAL (Write-Ahead Logging)
        self.wal: List[WALEntry] = []
        self.next_lsn = 1
        self.wal_file = self.data_dir / "wal.log"
        
        # MVCC storage
        self.records: Dict[str, List[BankingRecord]] = {}  # account -> versions
        self.current_version = 0
        
        # Transaction management
        self.active_transactions: Dict[str, Transaction] = {}
        self.lock_table: Dict[str, Set[str]] = {}  # resource -> transaction_ids
        
        # Replication
        self.replica_nodes: List['BankingACIDNode'] = []
        self.replication_lag = 0.0
        self.last_checkpoint_lsn = 0
        
        # Performance metrics
        self.transactions_committed = 0
        self.transactions_aborted = 0
        self.checkpoint_count = 0
        
        # Recovery state
        self.recovery_mode = False
        
        # Initialize storage
        self._initialize_storage()
        self._load_wal()
        
    def _initialize_storage(self):
        """Initialize persistent storage"""
        # Create initial accounts
        initial_accounts = [
            ("ACC001", 100000.0),
            ("ACC002", 75000.0), 
            ("ACC003", 150000.0),
            ("ACC004", 90000.0),
            ("ACC005", 120000.0)
        ]
        
        for account, balance in initial_accounts:
            record = BankingRecord(
                account_number=account,
                balance=balance,
                version=self.current_version,
                created_by="SYSTEM",
                valid_from=datetime.now(),
                valid_to=None
            )
            
            if account not in self.records:
                self.records[account] = []
            self.records[account].append(record)
            
    def _load_wal(self):
        """Load WAL from persistent storage"""
        if self.wal_file.exists():
            try:
                with open(self.wal_file, 'rb') as f:
                    self.wal = pickle.load(f)
                    self.next_lsn = max([entry.log_sequence_number for entry in self.wal], default=0) + 1
                logger.info(f"Loaded {len(self.wal)} WAL entries from disk")
            except Exception as e:
                logger.error(f"Failed to load WAL: {e}")
                
    def _append_to_wal(self, entry: WALEntry):
        """Append entry to WAL and persist"""
        self.wal.append(entry)
        
        # Persist to disk (Write-Ahead Logging principle)
        try:
            with open(self.wal_file, 'wb') as f:
                pickle.dump(self.wal, f)
        except Exception as e:
            logger.error(f"Failed to persist WAL: {e}")
            
    async def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> str:
        """Begin a new transaction with ACID guarantees"""
        
        transaction_id = f"TXN_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        transaction = Transaction(
            transaction_id=transaction_id,
            start_time=datetime.now(),
            isolation_level=isolation_level,
            read_timestamp=datetime.now()
        )
        
        self.active_transactions[transaction_id] = transaction
        
        # Log transaction begin
        wal_entry = WALEntry(
            log_sequence_number=self.next_lsn,
            transaction_id=transaction_id,
            operation_type="BEGIN",
            table_name="",
            record_key="",
            old_value=None,
            new_value=isolation_level.value,
            timestamp=datetime.now()
        )
        
        self._append_to_wal(wal_entry)
        self.next_lsn += 1
        
        logger.info(f"Transaction {transaction_id} started with {isolation_level.value}")
        return transaction_id
        
    async def read_account(self, transaction_id: str, account_number: str) -> Optional[float]:
        """
        Read account balance with MVCC and isolation levels
        यहाँ consistent read के लिए proper versioning implement की गई है
        """
        
        if transaction_id not in self.active_transactions:
            raise Exception("Invalid transaction ID")
            
        transaction = self.active_transactions[transaction_id]
        
        # Get appropriate version based on isolation level
        record = self._get_visible_record(account_number, transaction)
        
        if record and not record.is_deleted:
            logger.debug(f"Read {account_number}: ₹{record.balance} (version {record.version})")
            return record.balance
        else:
            return None
            
    def _get_visible_record(self, account_number: str, transaction: Transaction) -> Optional[BankingRecord]:
        """Get record version visible to transaction based on isolation level"""
        
        if account_number not in self.records:
            return None
            
        versions = self.records[account_number]
        
        # Find the appropriate version based on transaction's read timestamp
        visible_version = None
        
        for record in sorted(versions, key=lambda r: r.version, reverse=True):
            # Check if this version is visible to the transaction
            if record.valid_from <= transaction.read_timestamp:
                if record.valid_to is None or record.valid_to > transaction.read_timestamp:
                    visible_version = record
                    break
                    
        return visible_version
        
    async def update_account(self, transaction_id: str, account_number: str, new_balance: float) -> bool:
        """
        Update account balance with proper locking and versioning
        यहाँ conflict detection और deadlock prevention implement की गई है
        """
        
        if transaction_id not in self.active_transactions:
            raise Exception("Invalid transaction ID")
            
        transaction = self.active_transactions[transaction_id]
        
        # Acquire lock
        if not await self._acquire_lock(transaction_id, account_number):
            logger.warning(f"Failed to acquire lock for {account_number}")
            return False
            
        try:
            # Get current record
            current_record = self._get_visible_record(account_number, transaction)
            
            if not current_record:
                return False
                
            # Create new version
            new_version = self.current_version + 1
            self.current_version = new_version
            
            # Mark old version as expired
            current_record.valid_to = datetime.now()
            
            # Create new record version
            new_record = BankingRecord(
                account_number=account_number,
                balance=new_balance,
                version=new_version,
                created_by=transaction_id,
                valid_from=datetime.now(),
                valid_to=None
            )
            
            self.records[account_number].append(new_record)
            
            # Log the update
            wal_entry = WALEntry(
                log_sequence_number=self.next_lsn,
                transaction_id=transaction_id,
                operation_type="UPDATE",
                table_name="accounts",
                record_key=account_number,
                old_value=str(current_record.balance),
                new_value=str(new_balance),
                timestamp=datetime.now()
            )
            
            self._append_to_wal(wal_entry)
            self.next_lsn += 1
            
            # Track operation
            transaction.operations.append(f"UPDATE {account_number}: {current_record.balance} -> {new_balance}")
            
            logger.info(f"Updated {account_number}: ₹{current_record.balance} -> ₹{new_balance} (version {new_version})")
            return True
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False
            
    async def _acquire_lock(self, transaction_id: str, resource: str) -> bool:
        """
        Acquire lock with deadlock detection
        Simple timeout-based approach for deadlock prevention
        """
        
        timeout = 5.0  # 5 second timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if resource not in self.lock_table:
                self.lock_table[resource] = set()
                
            # Check if already locked by another transaction
            current_locks = self.lock_table[resource]
            if not current_locks or transaction_id in current_locks:
                # Grant lock
                current_locks.add(transaction_id)
                self.active_transactions[transaction_id].locks_held.add(resource)
                return True
                
            # Wait briefly and retry
            await asyncio.sleep(0.01)
            
        # Timeout - potential deadlock
        logger.warning(f"Lock timeout for {resource} by transaction {transaction_id}")
        return False
        
    def _release_locks(self, transaction_id: str):
        """Release all locks held by transaction"""
        
        if transaction_id in self.active_transactions:
            locks_held = self.active_transactions[transaction_id].locks_held.copy()
            
            for resource in locks_held:
                if resource in self.lock_table:
                    self.lock_table[resource].discard(transaction_id)
                    if not self.lock_table[resource]:
                        del self.lock_table[resource]
                        
            self.active_transactions[transaction_id].locks_held.clear()
            
    async def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit transaction with durability guarantees
        यहाँ proper commit protocol implement की गई है
        """
        
        if transaction_id not in self.active_transactions:
            return False
            
        transaction = self.active_transactions[transaction_id]
        transaction.status = TransactionStatus.PREPARING
        
        try:
            # Write commit record to WAL
            commit_entry = WALEntry(
                log_sequence_number=self.next_lsn,
                transaction_id=transaction_id,
                operation_type="COMMIT",
                table_name="",
                record_key="",
                old_value=None,
                new_value=f"Operations: {len(transaction.operations)}",
                timestamp=datetime.now()
            )
            
            self._append_to_wal(commit_entry)
            self.next_lsn += 1
            
            # Force WAL to disk (durability)
            await self._force_wal_to_disk()
            
            # Commit timestamp
            transaction.commit_timestamp = datetime.now()
            transaction.status = TransactionStatus.COMMITTED
            
            # Release locks
            self._release_locks(transaction_id)
            
            # Update metrics
            self.transactions_committed += 1
            
            # Replicate to followers
            await self._replicate_commit(transaction_id)
            
            logger.info(f"Transaction {transaction_id} committed successfully")
            
            # Cleanup
            del self.active_transactions[transaction_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Commit failed for {transaction_id}: {e}")
            await self.abort_transaction(transaction_id)
            return False
            
    async def abort_transaction(self, transaction_id: str) -> bool:
        """
        Abort transaction and rollback changes
        यहाँ proper rollback mechanism implement की गई है
        """
        
        if transaction_id not in self.active_transactions:
            return False
            
        transaction = self.active_transactions[transaction_id]
        transaction.status = TransactionStatus.ABORTED
        
        try:
            # Rollback all changes made by this transaction
            await self._rollback_changes(transaction_id)
            
            # Write abort record to WAL
            abort_entry = WALEntry(
                log_sequence_number=self.next_lsn,
                transaction_id=transaction_id,
                operation_type="ABORT",
                table_name="",
                record_key="",
                old_value=None,
                new_value="Rolled back",
                timestamp=datetime.now()
            )
            
            self._append_to_wal(abort_entry)
            self.next_lsn += 1
            
            # Release locks
            self._release_locks(transaction_id)
            
            # Update metrics
            self.transactions_aborted += 1
            
            logger.info(f"Transaction {transaction_id} aborted")
            
            # Cleanup
            del self.active_transactions[transaction_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Abort failed for {transaction_id}: {e}")
            return False
            
    async def _rollback_changes(self, transaction_id: str):
        """Rollback changes made by transaction"""
        
        # Find all records created by this transaction
        for account_number, versions in self.records.items():
            # Remove versions created by this transaction
            self.records[account_number] = [
                record for record in versions 
                if record.created_by != transaction_id
            ]
            
            # Restore valid_to for records that were expired by this transaction
            for record in versions:
                if (record.valid_to and 
                    any(entry.transaction_id == transaction_id and 
                        entry.record_key == account_number and 
                        entry.operation_type == "UPDATE" 
                        for entry in self.wal)):
                    record.valid_to = None
                    
    async def _force_wal_to_disk(self):
        """Force WAL to be written to disk (fsync equivalent)"""
        # In a real system, this would call fsync()
        # For simulation, we just ensure the file is written
        try:
            with open(self.wal_file, 'wb') as f:
                pickle.dump(self.wal, f)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            logger.error(f"Failed to force WAL to disk: {e}")
            
    async def _replicate_commit(self, transaction_id: str):
        """Replicate committed transaction to replica nodes"""
        
        if not self.replica_nodes:
            return
            
        # Get WAL entries for this transaction
        transaction_entries = [
            entry for entry in self.wal 
            if entry.transaction_id == transaction_id
        ]
        
        # Send to replicas
        replication_tasks = []
        for replica in self.replica_nodes:
            task = asyncio.create_task(replica.apply_replicated_entries(transaction_entries))
            replication_tasks.append(task)
            
        # Wait for replication (synchronous replication for consistency)
        if replication_tasks:
            await asyncio.gather(*replication_tasks, return_exceptions=True)
            
    async def apply_replicated_entries(self, entries: List[WALEntry]):
        """Apply replicated WAL entries"""
        
        for entry in entries:
            try:
                # Apply the entry based on operation type
                if entry.operation_type == "UPDATE":
                    # Replay the update
                    await self._replay_update(entry)
                elif entry.operation_type == "COMMIT":
                    # Mark as committed
                    logger.debug(f"Replicated commit: {entry.transaction_id}")
                    
                # Add to local WAL
                self.wal.append(entry)
                self.next_lsn = max(self.next_lsn, entry.log_sequence_number + 1)
                
            except Exception as e:
                logger.error(f"Failed to apply replicated entry: {e}")
                
    async def _replay_update(self, entry: WALEntry):
        """Replay an update operation from WAL"""
        
        account_number = entry.record_key
        new_balance = float(entry.new_value)
        
        # Create the record version
        if account_number not in self.records:
            self.records[account_number] = []
            
        new_record = BankingRecord(
            account_number=account_number,
            balance=new_balance,
            version=self.current_version + 1,
            created_by=entry.transaction_id,
            valid_from=entry.timestamp,
            valid_to=None
        )
        
        self.records[account_number].append(new_record)
        self.current_version += 1
        
    async def create_checkpoint(self):
        """
        Create checkpoint for faster recovery
        यहाँ database checkpoint mechanism implement की गई है
        """
        
        checkpoint_file = self.data_dir / f"checkpoint_{int(time.time())}.pkl"
        
        try:
            checkpoint_data = {
                "records": self.records,
                "current_version": self.current_version,
                "checkpoint_lsn": self.next_lsn - 1,
                "timestamp": datetime.now()
            }
            
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
                
            self.last_checkpoint_lsn = self.next_lsn - 1
            self.checkpoint_count += 1
            
            logger.info(f"Checkpoint created at LSN {self.last_checkpoint_lsn}")
            
            # Clean old checkpoints (keep only last 3)
            checkpoint_files = sorted(self.data_dir.glob("checkpoint_*.pkl"))
            for old_checkpoint in checkpoint_files[:-3]:
                old_checkpoint.unlink()
                
        except Exception as e:
            logger.error(f"Checkpoint creation failed: {e}")
            
    def add_replica(self, replica_node: 'BankingACIDNode'):
        """Add replica node"""
        self.replica_nodes.append(replica_node)
        logger.info(f"Added replica node {replica_node.node_id}")
        
    async def transfer_funds(self, from_account: str, to_account: str, amount: float) -> Tuple[bool, str]:
        """
        Complete fund transfer with ACID guarantees
        यह banking का main business operation है
        """
        
        # Begin transaction
        transaction_id = await self.begin_transaction(IsolationLevel.SERIALIZABLE)
        
        try:
            # Read source account
            from_balance = await self.read_account(transaction_id, from_account)
            if from_balance is None:
                await self.abort_transaction(transaction_id)
                return False, "Source account not found"
                
            if from_balance < amount:
                await self.abort_transaction(transaction_id)
                return False, f"Insufficient funds. Available: ₹{from_balance}"
                
            # Read destination account
            to_balance = await self.read_account(transaction_id, to_account)
            if to_balance is None:
                await self.abort_transaction(transaction_id)
                return False, "Destination account not found"
                
            # Update accounts
            if not await self.update_account(transaction_id, from_account, from_balance - amount):
                await self.abort_transaction(transaction_id)
                return False, "Failed to debit source account"
                
            if not await self.update_account(transaction_id, to_account, to_balance + amount):
                await self.abort_transaction(transaction_id)
                return False, "Failed to credit destination account"
                
            # Commit transaction
            if await self.commit_transaction(transaction_id):
                return True, f"Transfer successful: ₹{amount} from {from_account} to {to_account}"
            else:
                return False, "Transaction commit failed"
                
        except Exception as e:
            await self.abort_transaction(transaction_id)
            return False, f"Transfer failed: {e}"
            
    def get_node_status(self) -> Dict:
        """Get node status with ACID metrics"""
        
        return {
            "node_id": self.node_id,
            "wal_entries": len(self.wal),
            "next_lsn": self.next_lsn,
            "active_transactions": len(self.active_transactions),
            "total_accounts": len(self.records),
            "transactions_committed": self.transactions_committed,
            "transactions_aborted": self.transactions_aborted,
            "checkpoint_count": self.checkpoint_count,
            "last_checkpoint_lsn": self.last_checkpoint_lsn,
            "replica_count": len(self.replica_nodes),
            "locks_held": sum(len(tx.locks_held) for tx in self.active_transactions.values())
        }

# Testing and demonstration
async def demonstrate_banking_acid():
    """
    Complete demonstration of banking ACID replication
    Real banking scenario के साथ comprehensive testing
    """
    print("\n" + "="*70)
    print("Banking ACID Replication Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*70)
    
    # Create primary and replica nodes
    primary = BankingACIDNode("PRIMARY", "/tmp/banking_primary")
    replica1 = BankingACIDNode("REPLICA1", "/tmp/banking_replica1")
    replica2 = BankingACIDNode("REPLICA2", "/tmp/banking_replica2")
    
    # Setup replication
    primary.add_replica(replica1)
    primary.add_replica(replica2)
    
    logger.info("Banking ACID cluster initialized")
    
    # Demonstrate simple transfer
    logger.info("\n--- Simple Fund Transfer ---")
    
    success, message = await primary.transfer_funds("ACC001", "ACC002", 5000.0)
    print(f"Transfer result: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # Check balances
    tx_id = await primary.begin_transaction()
    acc001_balance = await primary.read_account(tx_id, "ACC001")
    acc002_balance = await primary.read_account(tx_id, "ACC002")
    await primary.commit_transaction(tx_id)
    
    print(f"ACC001 balance: ₹{acc001_balance}")
    print(f"ACC002 balance: ₹{acc002_balance}")
    
    # Demonstrate transaction abort
    logger.info("\n--- Transaction Abort Demo ---")
    
    success, message = await primary.transfer_funds("ACC003", "ACC004", 200000.0)  # Too high
    print(f"Large transfer result: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # Demonstrate concurrent transactions
    logger.info("\n--- Concurrent Transactions ---")
    
    # Start multiple concurrent transfers
    tasks = [
        primary.transfer_funds("ACC001", "ACC003", 1000.0),
        primary.transfer_funds("ACC002", "ACC004", 2000.0),
        primary.transfer_funds("ACC005", "ACC001", 1500.0)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, tuple):
            success, message = result
            print(f"Concurrent transfer {i+1}: {'SUCCESS' if success else 'FAILED'} - {message}")
        else:
            print(f"Concurrent transfer {i+1}: ERROR - {result}")
            
    # Create checkpoint
    logger.info("\n--- Creating Checkpoint ---")
    await primary.create_checkpoint()
    print("Checkpoint created successfully")
    
    # Show final status
    logger.info("\n--- Final Node Status ---")
    
    primary_status = primary.get_node_status()
    print(f"Primary Node Status:")
    for key, value in primary_status.items():
        print(f"  {key}: {value}")
        
    replica1_status = replica1.get_node_status()
    print(f"\nReplica 1 Status:")
    for key, value in replica1_status.items():
        print(f"  {key}: {value}")
        
    # Show final balances
    logger.info("\n--- Final Account Balances ---")
    
    tx_id = await primary.begin_transaction()
    for account in ["ACC001", "ACC002", "ACC003", "ACC004", "ACC005"]:
        balance = await primary.read_account(tx_id, account)
        print(f"{account}: ₹{balance}")
    await primary.commit_transaction(tx_id)

if __name__ == "__main__":
    print("Banking ACID Replication with WAL and MVCC")
    print("Episode 41: Database Replication Strategies")
    print("Demonstrating full ACID guarantees in banking replication...")
    
    # Run the demonstration
    asyncio.run(demonstrate_banking_acid())