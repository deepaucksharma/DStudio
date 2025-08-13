#!/usr/bin/env python3
"""
Database-based Distributed Locks
================================

Production-ready database-based distributed locking implementation.
Simple but effective approach used by many organizations as first step to distributed locking.

Mumbai Context: Database locks = Mumbai local train के पास system जैसे है!
Every platform has a signal system जो trains को coordinate करता है.
Database भी वैसे ही multiple processes को coordinate करता है.

Real-world usage:
- Job scheduling systems (like Airflow)
- Batch processing coordination
- Migration scripts coordination
- Background task management
"""

import time
import threading
import logging
import sqlite3
import psycopg2
import mysql.connector
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from contextlib import contextmanager
import uuid
import json
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    db_type: str  # 'sqlite', 'postgresql', 'mysql'
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = 'distributed_locks'
    username: Optional[str] = None
    password: Optional[str] = None
    sqlite_path: str = 'locks.db'

class DatabaseLockError(Exception):
    """Database lock specific exceptions"""
    pass

class DatabaseConnectionManager(ABC):
    """Abstract base class for database connections"""
    
    @abstractmethod
    def get_connection(self):
        """Get database connection"""
        pass
    
    @abstractmethod
    def create_lock_table(self):
        """Create lock table if not exists"""
        pass

class SQLiteConnectionManager(DatabaseConnectionManager):
    """SQLite connection manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.create_lock_table()
    
    def get_connection(self):
        return sqlite3.connect(
            self.config.sqlite_path,
            timeout=10.0,
            isolation_level=None  # Autocommit mode
        )
    
    def create_lock_table(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS distributed_locks (
                    lock_name TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON distributed_locks(expires_at)
            """)

class PostgreSQLConnectionManager(DatabaseConnectionManager):
    """PostgreSQL connection manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.create_lock_table()
    
    def get_connection(self):
        return psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password
        )
    
    def create_lock_table(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS distributed_locks (
                        lock_name VARCHAR(255) PRIMARY KEY,
                        owner_id VARCHAR(255) NOT NULL,
                        acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON distributed_locks(expires_at)
                """)

class DatabaseDistributedLock:
    """
    Database-based distributed lock implementation
    
    Mumbai Metaphor: यह Mumbai railway के signal box जैसा है - हर train को
    पता होना चाहिए कि कौन सा track free है. Database में भी हर process को
    पता होना चाहिए कि कौन सा resource locked है!
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        
        # Initialize appropriate connection manager
        if config.db_type == 'sqlite':
            self.conn_manager = SQLiteConnectionManager(config)
        elif config.db_type == 'postgresql':
            self.conn_manager = PostgreSQLConnectionManager(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def acquire_lock(self, resource: str, ttl: int = 30, retry_count: int = 3) -> Optional[Dict]:
        """
        Acquire distributed lock using database row-level locking
        
        Args:
            resource: Resource name to lock
            ttl: Lock time-to-live in seconds
            retry_count: Number of retry attempts
            
        Returns:
            Lock info if successful, None otherwise
        """
        lock_name = f"lock:{resource}"
        owner_id = f"{self.session_id}:{threading.current_thread().ident}"
        expires_at = time.time() + ttl
        
        metadata = {
            'resource': resource,
            'session_id': self.session_id,
            'thread_id': threading.current_thread().ident,
            'acquired_at': time.time()
        }
        
        for attempt in range(retry_count):
            try:
                with self.conn_manager.get_connection() as conn:
                    if self.config.db_type == 'sqlite':
                        cursor = conn.cursor()
                        
                        # Clean expired locks first
                        cursor.execute(
                            "DELETE FROM distributed_locks WHERE expires_at < ?",
                            (time.time(),)
                        )
                        
                        # Try to insert lock
                        try:
                            cursor.execute("""
                                INSERT INTO distributed_locks 
                                (lock_name, owner_id, expires_at, metadata)
                                VALUES (?, ?, ?, ?)
                            """, (lock_name, owner_id, expires_at, json.dumps(metadata)))
                            
                            lock_info = {
                                'resource': resource,
                                'lock_name': lock_name,
                                'owner_id': owner_id,
                                'expires_at': expires_at,
                                'metadata': metadata,
                                'acquired_at': time.time()
                            }
                            
                            logger.info(f"🔒 Database lock acquired: {resource} (expires: {expires_at})")
                            return lock_info
                            
                        except sqlite3.IntegrityError:
                            # Lock already exists - check if it's expired
                            cursor.execute(
                                "SELECT owner_id, expires_at FROM distributed_locks WHERE lock_name = ?",
                                (lock_name,)
                            )
                            
                            result = cursor.fetchone()
                            if result:
                                current_owner, current_expires = result
                                if current_expires < time.time():
                                    # Lock expired, try to replace it
                                    cursor.execute("""
                                        UPDATE distributed_locks 
                                        SET owner_id = ?, expires_at = ?, metadata = ?, acquired_at = CURRENT_TIMESTAMP
                                        WHERE lock_name = ? AND expires_at < ?
                                    """, (owner_id, expires_at, json.dumps(metadata), lock_name, time.time()))
                                    
                                    if cursor.rowcount > 0:
                                        lock_info = {
                                            'resource': resource,
                                            'lock_name': lock_name,
                                            'owner_id': owner_id,
                                            'expires_at': expires_at,
                                            'metadata': metadata,
                                            'acquired_at': time.time()
                                        }
                                        
                                        logger.info(f"🔒 Database lock acquired (replaced expired): {resource}")
                                        return lock_info
                                else:
                                    logger.warning(f"❌ Lock held by: {current_owner}")
                    
                    elif self.config.db_type == 'postgresql':
                        with conn.cursor() as cur:
                            # Clean expired locks first
                            cur.execute(
                                "DELETE FROM distributed_locks WHERE expires_at < to_timestamp(%s)",
                                (time.time(),)
                            )
                            
                            # Try to insert lock
                            try:
                                cur.execute("""
                                    INSERT INTO distributed_locks 
                                    (lock_name, owner_id, expires_at, metadata)
                                    VALUES (%s, %s, to_timestamp(%s), %s)
                                """, (lock_name, owner_id, expires_at, json.dumps(metadata)))
                                
                                conn.commit()
                                
                                lock_info = {
                                    'resource': resource,
                                    'lock_name': lock_name,
                                    'owner_id': owner_id,
                                    'expires_at': expires_at,
                                    'metadata': metadata,
                                    'acquired_at': time.time()
                                }
                                
                                logger.info(f"🔒 Database lock acquired: {resource}")
                                return lock_info
                                
                            except psycopg2.IntegrityError:
                                conn.rollback()
                                # Similar logic for PostgreSQL...
                                pass
                
            except Exception as e:
                logger.warning(f"Lock acquisition attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
        
        logger.warning(f"❌ Failed to acquire lock for {resource} after {retry_count} attempts")
        return None
    
    def release_lock(self, lock_info: Dict) -> bool:
        """
        Release distributed lock
        
        Args:
            lock_info: Lock information from acquire_lock
            
        Returns:
            True if successfully released
        """
        try:
            with self.conn_manager.get_connection() as conn:
                if self.config.db_type == 'sqlite':
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM distributed_locks WHERE lock_name = ? AND owner_id = ?",
                        (lock_info['lock_name'], lock_info['owner_id'])
                    )
                    
                    if cursor.rowcount > 0:
                        logger.info(f"🔓 Database lock released: {lock_info['resource']}")
                        return True
                
                elif self.config.db_type == 'postgresql':
                    with conn.cursor() as cur:
                        cur.execute(
                            "DELETE FROM distributed_locks WHERE lock_name = %s AND owner_id = %s",
                            (lock_info['lock_name'], lock_info['owner_id'])
                        )
                        conn.commit()
                        
                        if cur.rowcount > 0:
                            logger.info(f"🔓 Database lock released: {lock_info['resource']}")
                            return True
            
            logger.warning(f"⚠️ Lock not found or not owned by us: {lock_info['resource']}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to release lock: {e}")
            return False
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up expired locks"""
        def cleanup_expired_locks():
            while True:
                try:
                    with self.conn_manager.get_connection() as conn:
                        if self.config.db_type == 'sqlite':
                            cursor = conn.cursor()
                            cursor.execute(
                                "DELETE FROM distributed_locks WHERE expires_at < ?",
                                (time.time(),)
                            )
                            if cursor.rowcount > 0:
                                logger.debug(f"Cleaned up {cursor.rowcount} expired locks")
                        
                        elif self.config.db_type == 'postgresql':
                            with conn.cursor() as cur:
                                cur.execute(
                                    "DELETE FROM distributed_locks WHERE expires_at < to_timestamp(%s)",
                                    (time.time(),)
                                )
                                conn.commit()
                                if cur.rowcount > 0:
                                    logger.debug(f"Cleaned up {cur.rowcount} expired locks")
                
                except Exception as e:
                    logger.warning(f"Lock cleanup failed: {e}")
                
                time.sleep(10)  # Cleanup every 10 seconds
        
        cleanup_thread = threading.Thread(target=cleanup_expired_locks, daemon=True)
        cleanup_thread.start()
    
    @contextmanager
    def lock_context(self, resource: str, ttl: int = 30):
        """
        Context manager for automatic lock management
        
        Usage:
            with db_lock.lock_context("resource_name"):
                # Critical section
                pass
        """
        lock_info = self.acquire_lock(resource, ttl)
        if not lock_info:
            raise DatabaseLockError(f"Failed to acquire lock for {resource}")
        
        try:
            yield lock_info
        finally:
            self.release_lock(lock_info)

class PayUTransactionProcessor:
    """
    PayU transaction processing with database locks
    
    Mumbai Story: PayU जैसे payment gateways में हजारों transactions per second
    होते हैं. Database locks ensure करते हैं कि duplicate transactions न हों
    और balance updates correctly हों!
    """
    
    def __init__(self, db_lock: DatabaseDistributedLock):
        self.db_lock = db_lock
        self.user_balances = {
            f"user_{i:04d}": 10000.0  # Starting balance: ₹10,000
            for i in range(100)
        }
        self.transaction_history = []
        self.processing_stats = {
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'duplicate_prevented': 0,
            'balance_conflicts_prevented': 0
        }
    
    def process_payment(self, transaction_id: str, from_user: str, to_user: str, 
                       amount: float) -> Dict:
        """
        Process payment transaction with database locking
        
        Args:
            transaction_id: Unique transaction identifier
            from_user: Sender user ID
            to_user: Receiver user ID
            amount: Transaction amount
            
        Returns:
            Transaction result
        """
        self.processing_stats['total_transactions'] += 1
        
        # Lock transaction ID to prevent duplicates
        duplicate_lock_resource = f"transaction_{transaction_id}"
        
        try:
            with self.db_lock.lock_context(duplicate_lock_resource, ttl=60):
                # Check if transaction already processed
                existing_txn = next(
                    (t for t in self.transaction_history if t['transaction_id'] == transaction_id),
                    None
                )
                
                if existing_txn:
                    self.processing_stats['duplicate_prevented'] += 1
                    return {
                        'success': False,
                        'message': 'Transaction already processed',
                        'error_code': 'DUPLICATE_TRANSACTION',
                        'original_result': existing_txn
                    }
                
                # Lock both user accounts in a consistent order to prevent deadlock
                users_to_lock = sorted([from_user, to_user])
                balance_lock_resource = f"balance_{users_to_lock[0]}_{users_to_lock[1]}"
                
                try:
                    with self.db_lock.lock_context(balance_lock_resource, ttl=30):
                        # Validate users exist
                        if from_user not in self.user_balances or to_user not in self.user_balances:
                            self.processing_stats['failed_transactions'] += 1
                            return {
                                'success': False,
                                'message': 'Invalid user account',
                                'error_code': 'INVALID_USER'
                            }
                        
                        # Check sufficient balance
                        if self.user_balances[from_user] < amount:
                            self.processing_stats['failed_transactions'] += 1
                            return {
                                'success': False,
                                'message': f'Insufficient balance. Available: ₹{self.user_balances[from_user]:.2f}',
                                'error_code': 'INSUFFICIENT_BALANCE'
                            }
                        
                        # Process transaction
                        self.user_balances[from_user] -= amount
                        self.user_balances[to_user] += amount
                        
                        # Record transaction
                        transaction_record = {
                            'transaction_id': transaction_id,
                            'from_user': from_user,
                            'to_user': to_user,
                            'amount': amount,
                            'timestamp': time.time(),
                            'status': 'completed'
                        }
                        
                        self.transaction_history.append(transaction_record)
                        self.processing_stats['successful_transactions'] += 1
                        self.processing_stats['balance_conflicts_prevented'] += 1
                        
                        logger.info(f"💰 Payment processed: {transaction_id} - ₹{amount:.2f} from {from_user} to {to_user}")
                        
                        return {
                            'success': True,
                            'transaction_id': transaction_id,
                            'message': f'Payment of ₹{amount:.2f} completed successfully',
                            'from_balance': self.user_balances[from_user],
                            'to_balance': self.user_balances[to_user],
                            'timestamp': transaction_record['timestamp']
                        }
                        
                except DatabaseLockError as e:
                    self.processing_stats['failed_transactions'] += 1
                    return {
                        'success': False,
                        'message': 'Unable to process payment - system busy',
                        'error_code': 'BALANCE_LOCK_TIMEOUT'
                    }
                
        except DatabaseLockError as e:
            self.processing_stats['failed_transactions'] += 1
            return {
                'success': False,
                'message': 'Transaction processing failed - please retry',
                'error_code': 'TRANSACTION_LOCK_TIMEOUT'
            }
    
    def get_user_balance(self, user_id: str) -> float:
        """Get user balance with read lock"""
        try:
            with self.db_lock.lock_context(f"balance_read_{user_id}", ttl=5):
                return self.user_balances.get(user_id, 0.0)
        except DatabaseLockError:
            # Return cached balance if lock fails
            return self.user_balances.get(user_id, 0.0)
    
    def get_processing_stats(self) -> Dict:
        """Get transaction processing statistics"""
        success_rate = (
            self.processing_stats['successful_transactions'] / 
            max(1, self.processing_stats['total_transactions'])
        ) * 100
        
        return {
            **self.processing_stats,
            'success_rate': success_rate,
            'total_amount_processed': sum(t['amount'] for t in self.transaction_history)
        }

def simulate_payu_payment_processing():
    """
    Simulate PayU payment gateway processing
    
    Mumbai Scenario: Festival season में UPI payments का volume बहुत बढ़ जाता है.
    Database locks ensure करते हैं कि transactions safely process हों!
    """
    # Initialize database lock with SQLite
    db_config = DatabaseConfig(
        db_type='sqlite',
        sqlite_path='payu_transactions.db'
    )
    
    db_lock = DatabaseDistributedLock(db_config)
    payment_processor = PayUTransactionProcessor(db_lock)
    
    # Generate test transactions
    import random
    
    def generate_transaction():
        """Generate random transaction"""
        users = [f"user_{i:04d}" for i in range(100)]
        from_user = random.choice(users)
        to_user = random.choice([u for u in users if u != from_user])
        amount = round(random.uniform(10, 1000), 2)
        transaction_id = f"TXN_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
        
        return transaction_id, from_user, to_user, amount
    
    def process_single_transaction():
        """Process single transaction in thread"""
        txn_id, from_user, to_user, amount = generate_transaction()
        result = payment_processor.process_payment(txn_id, from_user, to_user, amount)
        
        if result['success']:
            logger.debug(f"✅ {txn_id}: ₹{amount} {from_user} → {to_user}")
        else:
            logger.debug(f"❌ {txn_id}: {result['message']}")
        
        return result
    
    # Simulate concurrent payment processing
    threads = []
    num_transactions = 50
    
    logger.info(f"💳 Starting PayU payment processing simulation ({num_transactions} transactions)...")
    start_time = time.time()
    
    # Create concurrent transaction threads
    for i in range(num_transactions):
        thread = threading.Thread(target=process_single_transaction)
        threads.append(thread)
        thread.start()
        time.sleep(0.01)  # Small delay between transactions
    
    # Wait for all transactions to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # Show results
    stats = payment_processor.get_processing_stats()
    
    logger.info(f"\n📊 PayU Payment Processing Results:")
    logger.info(f"Total transactions attempted: {stats['total_transactions']}")
    logger.info(f"Successful transactions: {stats['successful_transactions']}")
    logger.info(f"Failed transactions: {stats['failed_transactions']}")
    logger.info(f"Duplicate transactions prevented: {stats['duplicate_prevented']}")
    logger.info(f"Balance conflicts prevented: {stats['balance_conflicts_prevented']}")
    logger.info(f"Success rate: {stats['success_rate']:.2f}%")
    logger.info(f"Total amount processed: ₹{stats['total_amount_processed']:.2f}")
    logger.info(f"Processing time: {end_time - start_time:.2f} seconds")
    
    # Show sample balances
    sample_users = ['user_0001', 'user_0002', 'user_0003']
    logger.info(f"\n💰 Sample user balances:")
    for user in sample_users:
        balance = payment_processor.get_user_balance(user)
        logger.info(f"{user}: ₹{balance:.2f}")

if __name__ == "__main__":
    try:
        simulate_payu_payment_processing()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()