#!/usr/bin/env python3
"""
Write-Through Cache Pattern Implementation
Bank transaction system के लिए consistent write-through caching

Key Features:
- Write-through cache pattern
- ACID transaction compliance
- Database और cache synchronization
- High consistency guarantees
- Banking grade reliability
- Mumbai banking system simulation

Use Cases:
- HDFC Bank account balance caching
- UPI transaction history
- Credit card transaction processing
- Financial audit trail maintenance

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (Write-Through Pattern)
"""

import sqlite3
import redis
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BankAccount:
    """Bank account model"""
    account_number: str
    customer_name: str
    balance: Decimal
    account_type: str  # SAVINGS, CURRENT, FIXED_DEPOSIT
    branch_code: str
    ifsc_code: str
    is_active: bool
    created_at: str
    updated_at: str

@dataclass
class Transaction:
    """Bank transaction model"""
    transaction_id: str
    from_account: str
    to_account: Optional[str]
    amount: Decimal
    transaction_type: str  # CREDIT, DEBIT, TRANSFER
    description: str
    reference_number: str
    timestamp: str
    status: str  # PENDING, SUCCESS, FAILED
    fee_amount: Decimal = Decimal('0.00')

class DatabaseConnection:
    """
    Database connection manager for banking system
    Banking data के लिए SQLite database wrapper
    """
    
    def __init__(self, db_path: str = "mumbai_bank.db"):
        self.db_path = db_path
        self.init_database()
        logger.info("🏦 Database initialized")
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                    account_type TEXT NOT NULL,
                    branch_code TEXT NOT NULL,
                    ifsc_code TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    from_account TEXT NOT NULL,
                    to_account TEXT,
                    amount DECIMAL(15,2) NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    reference_number TEXT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fee_amount DECIMAL(15,2) DEFAULT 0.00,
                    FOREIGN KEY (from_account) REFERENCES accounts (account_number)
                )
            """)
            
            # Index for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(from_account)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_transaction(self, queries: List[Tuple[str, tuple]], isolation_level='DEFERRED'):
        """Execute multiple queries in a transaction"""
        with sqlite3.connect(self.db_path, isolation_level=isolation_level) as conn:
            cursor = conn.cursor()
            try:
                for query, params in queries:
                    cursor.execute(query, params)
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {str(e)}")
                raise

class WriteThroughCache:
    """
    Write-Through Cache implementation for banking system
    Banking transactions के लिए high-consistency write-through cache
    """
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=1,  # Use DB 1 for banking
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis connection established for write-through cache")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {str(e)}")
            self.redis_available = False
            # Fallback to in-memory cache
            self.memory_cache = {}
        
        # Cache configuration
        self.cache_ttl = {
            'account': 3600,      # 1 hour for account data
            'transaction': 7200,  # 2 hours for transaction data
            'balance': 1800,      # 30 minutes for balance
        }
        
        # Statistics
        self.stats = {
            'reads': 0,
            'writes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'database_writes': 0,
            'cache_writes': 0
        }
        
        # Thread lock for consistency
        self.write_lock = threading.RLock()
    
    def _cache_key(self, entity_type: str, entity_id: str) -> str:
        """Generate cache key"""
        return f"mumbai_bank:{entity_type}:{entity_id}"
    
    def _get_from_cache(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            if self.redis_available:
                return self.redis_client.get(key)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache read error: {str(e)}")
            return None
    
    def _set_to_cache(self, key: str, value: str, ttl: int):
        """Set value to cache"""
        try:
            if self.redis_available:
                self.redis_client.setex(key, ttl, value)
            else:
                self.memory_cache[key] = value
            
            self.stats['cache_writes'] += 1
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")
    
    def _delete_from_cache(self, key: str):
        """Delete value from cache"""
        try:
            if self.redis_available:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
    
    def get_account(self, account_number: str) -> Optional[BankAccount]:
        """
        Get account with write-through cache
        पहले cache check करते हैं, फिर database से fetch करते हैं
        """
        self.stats['reads'] += 1
        cache_key = self._cache_key("account", account_number)
        
        # Try cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Account cache hit: {account_number}")
            self.stats['cache_hits'] += 1
            account_data = json.loads(cached_data)
            # Convert balance back to Decimal
            account_data['balance'] = Decimal(str(account_data['balance']))
            return BankAccount(**account_data)
        
        # Cache miss - read from database
        logger.debug(f"Account cache miss: {account_number}")
        self.stats['cache_misses'] += 1
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM accounts WHERE account_number = ?",
                (account_number,)
            )
            row = cursor.fetchone()
            
            if row:
                account = BankAccount(
                    account_number=row['account_number'],
                    customer_name=row['customer_name'],
                    balance=Decimal(str(row['balance'])),
                    account_type=row['account_type'],
                    branch_code=row['branch_code'],
                    ifsc_code=row['ifsc_code'],
                    is_active=bool(row['is_active']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                
                # Cache the result
                account_dict = asdict(account)
                account_dict['balance'] = str(account.balance)  # JSON serializable
                self._set_to_cache(cache_key, json.dumps(account_dict), self.cache_ttl['account'])
                
                return account
        
        return None
    
    def create_account(self, account: BankAccount) -> bool:
        """
        Create account with write-through cache
        Database में write करते हैं और साथ में cache भी update करते हैं
        """
        with self.write_lock:
            self.stats['writes'] += 1
            self.stats['database_writes'] += 1
            
            try:
                # Write to database first (Write-Through pattern)
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO accounts 
                        (account_number, customer_name, balance, account_type, 
                         branch_code, ifsc_code, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        account.account_number,
                        account.customer_name,
                        str(account.balance),
                        account.account_type,
                        account.branch_code,
                        account.ifsc_code,
                        account.is_active,
                        account.created_at,
                        account.updated_at
                    ))
                    conn.commit()
                
                # Write to cache (Write-Through)
                cache_key = self._cache_key("account", account.account_number)
                account_dict = asdict(account)
                account_dict['balance'] = str(account.balance)
                self._set_to_cache(cache_key, json.dumps(account_dict), self.cache_ttl['account'])
                
                logger.info(f"✅ Account created: {account.account_number} - {account.customer_name}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Account creation failed: {str(e)}")
                return False
    
    def update_account_balance(self, account_number: str, new_balance: Decimal) -> bool:
        """
        Update account balance with write-through cache
        Balance update - database और cache दोनों में synchronously update करते हैं
        """
        with self.write_lock:
            self.stats['writes'] += 1
            self.stats['database_writes'] += 1
            
            try:
                updated_at = datetime.now().isoformat()
                
                # Write to database first
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE accounts 
                        SET balance = ?, updated_at = ?
                        WHERE account_number = ?
                    """, (str(new_balance), updated_at, account_number))
                    
                    if cursor.rowcount == 0:
                        logger.error(f"Account not found: {account_number}")
                        return False
                    
                    conn.commit()
                
                # Update cache (Write-Through)
                cache_key = self._cache_key("account", account_number)
                
                # Get current account data
                account = self.get_account(account_number)
                if account:
                    account.balance = new_balance
                    account.updated_at = updated_at
                    
                    account_dict = asdict(account)
                    account_dict['balance'] = str(account.balance)
                    self._set_to_cache(cache_key, json.dumps(account_dict), self.cache_ttl['account'])
                
                # Also update balance-specific cache
                balance_key = self._cache_key("balance", account_number)
                self._set_to_cache(balance_key, str(new_balance), self.cache_ttl['balance'])
                
                logger.info(f"💰 Balance updated: {account_number} -> ₹{new_balance}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Balance update failed: {str(e)}")
                return False
    
    def record_transaction(self, transaction: Transaction) -> bool:
        """
        Record transaction with write-through cache
        Transaction recording - complete ACID compliance के साथ
        """
        with self.write_lock:
            self.stats['writes'] += 1
            self.stats['database_writes'] += 1
            
            try:
                # Begin database transaction
                queries = []
                
                # Insert transaction record
                queries.append(("""
                    INSERT INTO transactions 
                    (transaction_id, from_account, to_account, amount, transaction_type,
                     description, reference_number, timestamp, status, fee_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.transaction_id,
                    transaction.from_account,
                    transaction.to_account,
                    str(transaction.amount),
                    transaction.transaction_type,
                    transaction.description,
                    transaction.reference_number,
                    transaction.timestamp,
                    transaction.status,
                    str(transaction.fee_amount)
                )))
                
                # Execute database transaction
                self.db.execute_transaction(queries)
                
                # Write to cache (Write-Through)
                cache_key = self._cache_key("transaction", transaction.transaction_id)
                transaction_dict = asdict(transaction)
                transaction_dict['amount'] = str(transaction.amount)
                transaction_dict['fee_amount'] = str(transaction.fee_amount)
                self._set_to_cache(cache_key, json.dumps(transaction_dict), self.cache_ttl['transaction'])
                
                logger.info(f"💳 Transaction recorded: {transaction.transaction_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Transaction recording failed: {str(e)}")
                return False
    
    def transfer_money(self, from_account: str, to_account: str, amount: Decimal, 
                      description: str = "Fund Transfer") -> Optional[str]:
        """
        Money transfer with write-through cache
        Complete money transfer - ACID compliance के साथ
        """
        with self.write_lock:
            transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            reference_number = f"REF_{int(time.time())}"
            
            try:
                # Validate accounts
                from_acc = self.get_account(from_account)
                to_acc = self.get_account(to_account)
                
                if not from_acc or not from_acc.is_active:
                    logger.error(f"Invalid from account: {from_account}")
                    return None
                
                if not to_acc or not to_acc.is_active:
                    logger.error(f"Invalid to account: {to_account}")
                    return None
                
                # Check sufficient balance
                fee_amount = Decimal('5.00')  # ₹5 transfer fee
                total_debit = amount + fee_amount
                
                if from_acc.balance < total_debit:
                    logger.error(f"Insufficient balance: {from_acc.balance} < {total_debit}")
                    return None
                
                # Calculate new balances
                new_from_balance = from_acc.balance - total_debit
                new_to_balance = to_acc.balance + amount
                
                # Prepare database transaction
                timestamp = datetime.now().isoformat()
                
                queries = []
                
                # Update from account balance
                queries.append((
                    "UPDATE accounts SET balance = ?, updated_at = ? WHERE account_number = ?",
                    (str(new_from_balance), timestamp, from_account)
                ))
                
                # Update to account balance
                queries.append((
                    "UPDATE accounts SET balance = ?, updated_at = ? WHERE account_number = ?",
                    (str(new_to_balance), timestamp, to_account)
                ))
                
                # Record debit transaction
                queries.append(("""
                    INSERT INTO transactions 
                    (transaction_id, from_account, to_account, amount, transaction_type,
                     description, reference_number, timestamp, status, fee_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{transaction_id}_DEBIT",
                    from_account,
                    to_account,
                    str(amount),
                    "DEBIT",
                    f"Transfer to {to_account}: {description}",
                    reference_number,
                    timestamp,
                    "SUCCESS",
                    str(fee_amount)
                )))
                
                # Record credit transaction
                queries.append(("""
                    INSERT INTO transactions 
                    (transaction_id, from_account, to_account, amount, transaction_type,
                     description, reference_number, timestamp, status, fee_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{transaction_id}_CREDIT",
                    to_account,
                    from_account,
                    str(amount),
                    "CREDIT",
                    f"Transfer from {from_account}: {description}",
                    reference_number,
                    timestamp,
                    "SUCCESS",
                    str(Decimal('0.00'))
                )))
                
                # Execute all queries in single transaction
                self.db.execute_transaction(queries, isolation_level='IMMEDIATE')
                
                # Update cache (Write-Through)
                self.update_account_balance(from_account, new_from_balance)
                self.update_account_balance(to_account, new_to_balance)
                
                # Cache transaction records
                debit_txn = Transaction(
                    transaction_id=f"{transaction_id}_DEBIT",
                    from_account=from_account,
                    to_account=to_account,
                    amount=amount,
                    transaction_type="DEBIT",
                    description=f"Transfer to {to_account}: {description}",
                    reference_number=reference_number,
                    timestamp=timestamp,
                    status="SUCCESS",
                    fee_amount=fee_amount
                )
                
                credit_txn = Transaction(
                    transaction_id=f"{transaction_id}_CREDIT",
                    from_account=to_account,
                    to_account=from_account,
                    amount=amount,
                    transaction_type="CREDIT",
                    description=f"Transfer from {from_account}: {description}",
                    reference_number=reference_number,
                    timestamp=timestamp,
                    status="SUCCESS",
                    fee_amount=Decimal('0.00')
                )
                
                # Cache both transactions
                for txn in [debit_txn, credit_txn]:
                    cache_key = self._cache_key("transaction", txn.transaction_id)
                    txn_dict = asdict(txn)
                    txn_dict['amount'] = str(txn.amount)
                    txn_dict['fee_amount'] = str(txn.fee_amount)
                    self._set_to_cache(cache_key, json.dumps(txn_dict), self.cache_ttl['transaction'])
                
                logger.info(f"💸 Money transfer completed: ₹{amount} from {from_account} to {to_account}")
                return reference_number
                
            except Exception as e:
                logger.error(f"❌ Money transfer failed: {str(e)}")
                return None
    
    def get_transaction_history(self, account_number: str, limit: int = 10) -> List[Transaction]:
        """
        Get transaction history for account
        Account के transaction history को retrieve करते हैं
        """
        self.stats['reads'] += 1
        
        # For transaction history, we read directly from database for consistency
        # Cache individual transactions as they are accessed
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE from_account = ? OR to_account = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (account_number, account_number, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = Transaction(
                    transaction_id=row['transaction_id'],
                    from_account=row['from_account'],
                    to_account=row['to_account'],
                    amount=Decimal(str(row['amount'])),
                    transaction_type=row['transaction_type'],
                    description=row['description'],
                    reference_number=row['reference_number'],
                    timestamp=row['timestamp'],
                    status=row['status'],
                    fee_amount=Decimal(str(row['fee_amount']))
                )
                
                # Cache individual transaction
                cache_key = self._cache_key("transaction", transaction.transaction_id)
                txn_dict = asdict(transaction)
                txn_dict['amount'] = str(transaction.amount)
                txn_dict['fee_amount'] = str(transaction.fee_amount)
                self._set_to_cache(cache_key, json.dumps(txn_dict), self.cache_ttl['transaction'])
                
                transactions.append(transaction)
            
            return transactions
    
    def get_cache_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        total_operations = self.stats['reads'] + self.stats['writes']
        hit_ratio = (self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100) if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0
        
        return {
            'cache_type': 'Write-Through',
            'stats': self.stats,
            'hit_ratio_percent': round(hit_ratio, 2),
            'total_operations': total_operations,
            'redis_available': self.redis_available,
            'cache_ttl_config': self.cache_ttl
        }

def demo_write_through_cache():
    """
    Demo write-through cache with banking transactions
    Mumbai banking system का comprehensive demo
    """
    print("🏦 Write-Through Cache Pattern Demo")
    print("🇮🇳 Mumbai Banking System Simulation")
    print("=" * 60)
    
    # Initialize system
    db = DatabaseConnection()
    cache = WriteThroughCache(db)
    
    print("\n1. Creating Bank Accounts")
    print("-" * 30)
    
    # Create test accounts
    accounts = [
        BankAccount(
            account_number="ACC_001_MUMBAI",
            customer_name="राहुल शर्मा", 
            balance=Decimal('50000.00'),
            account_type="SAVINGS",
            branch_code="MUMBAI_001",
            ifsc_code="HDFC0000123",
            is_active=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        ),
        BankAccount(
            account_number="ACC_002_MUMBAI",
            customer_name="प्रिया पटेल",
            balance=Decimal('75000.00'),
            account_type="CURRENT",
            branch_code="MUMBAI_002", 
            ifsc_code="HDFC0000124",
            is_active=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    ]
    
    for account in accounts:
        if cache.create_account(account):
            print(f"✅ Account created: {account.customer_name} - ₹{account.balance}")
    
    print("\n2. Account Retrieval (Cache Testing)")
    print("-" * 40)
    
    # Test cache hits and misses
    for account_num in ["ACC_001_MUMBAI", "ACC_002_MUMBAI"]:
        # First access (cache miss expected)
        start_time = time.time()
        account = cache.get_account(account_num)
        first_access_time = (time.time() - start_time) * 1000
        
        # Second access (cache hit expected)
        start_time = time.time()
        account = cache.get_account(account_num)
        second_access_time = (time.time() - start_time) * 1000
        
        print(f"📊 {account.customer_name}: First={first_access_time:.2f}ms, Second={second_access_time:.2f}ms")
    
    print("\n3. Money Transfer Operations")
    print("-" * 35)
    
    # Perform money transfers
    transfers = [
        ("ACC_001_MUMBAI", "ACC_002_MUMBAI", Decimal('5000.00'), "Monthly rent payment"),
        ("ACC_002_MUMBAI", "ACC_001_MUMBAI", Decimal('3000.00'), "Freelance payment"),
        ("ACC_001_MUMBAI", "ACC_002_MUMBAI", Decimal('2000.00'), "Birthday gift")
    ]
    
    for from_acc, to_acc, amount, desc in transfers:
        ref_num = cache.transfer_money(from_acc, to_acc, amount, desc)
        if ref_num:
            print(f"💸 Transfer: ₹{amount} - Ref: {ref_num}")
        else:
            print(f"❌ Transfer failed: ₹{amount}")
    
    print("\n4. Account Balances After Transfers")
    print("-" * 40)
    
    for account_num in ["ACC_001_MUMBAI", "ACC_002_MUMBAI"]:
        account = cache.get_account(account_num)
        print(f"💰 {account.customer_name}: ₹{account.balance}")
    
    print("\n5. Transaction History")
    print("-" * 25)
    
    for account_num in ["ACC_001_MUMBAI", "ACC_002_MUMBAI"]:
        account = cache.get_account(account_num)
        transactions = cache.get_transaction_history(account_num, 5)
        
        print(f"\n📋 {account.customer_name} - Last {len(transactions)} transactions:")
        for txn in transactions:
            symbol = "💸" if txn.transaction_type == "DEBIT" else "💰"
            print(f"   {symbol} ₹{txn.amount} - {txn.description}")
    
    print("\n6. Cache Performance Statistics")
    print("-" * 35)
    
    stats = cache.get_cache_stats()
    print(f"📊 Cache Type: {stats['cache_type']}")
    print(f"🎯 Hit Ratio: {stats['hit_ratio_percent']}%")
    print(f"✅ Cache Hits: {stats['stats']['cache_hits']}")
    print(f"❌ Cache Misses: {stats['stats']['cache_misses']}")
    print(f"📝 Database Writes: {stats['stats']['database_writes']}")
    print(f"💾 Cache Writes: {stats['stats']['cache_writes']}")
    print(f"🔄 Total Operations: {stats['total_operations']}")
    
    print("\n" + "=" * 60)
    print("🎉 Write-Through Cache Demo Completed!")
    print("💡 Key Benefits:")
    print("   - Data consistency guaranteed")
    print("   - Read performance improved")
    print("   - Write latency slightly higher (but consistent)")
    print("   - Perfect for financial/banking systems")
    print("   - ACID compliance maintained")

if __name__ == "__main__":
    demo_write_through_cache()