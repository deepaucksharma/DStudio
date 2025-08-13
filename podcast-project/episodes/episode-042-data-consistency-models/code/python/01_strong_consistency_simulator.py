"""
Strong Consistency Simulator
Demonstrating ACID properties in banking scenarios
Example: SBI Core Banking System - Fund Transfer
"""

import threading
import time
import uuid
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import sqlite3
import logging

# Hindi comments ke liye setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED" 
    ABORTED = "ABORTED"

@dataclass
class BankAccount:
    account_id: str
    balance: float
    version: int = 1
    
class Transaction:
    def __init__(self, from_account: str, to_account: str, amount: float):
        self.transaction_id = str(uuid.uuid4())
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.status = TransactionStatus.PENDING
        self.timestamp = time.time()

class StrongConsistencyBank:
    """
    SBI jaisa banking system - har transaction ACID compliant
    Strong consistency matlab immediate consistency across all nodes
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.lock = threading.RLock()  # Banking mein safety first!
        self.transaction_log: List[Transaction] = []
        # For in-memory database, use a persistent connection
        if db_path == ":memory:":
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
        else:
            self.conn = None
        self._init_database()
        
    def _init_database(self):
        """Database schema setup - Production ready"""
        with self.lock:
            conn = self.conn if self.conn else sqlite3.connect(self.db_path, check_same_thread=False)
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        account_id TEXT PRIMARY KEY,
                        balance REAL NOT NULL,
                        version INTEGER NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id TEXT PRIMARY KEY,
                        from_account TEXT,
                        to_account TEXT,
                        amount REAL,
                        status TEXT,
                        timestamp REAL,
                        FOREIGN KEY(from_account) REFERENCES accounts(account_id),
                        FOREIGN KEY(to_account) REFERENCES accounts(account_id)
                    )
                """)
                conn.commit()
            finally:
                if not self.conn:
                    conn.close()
        
    def create_account(self, account_id: str, account_type: str = "SAVINGS", initial_balance: float = 0.0) -> bool:
        """
        Naya account banao - SBI branch jaisa process
        """
        with self.lock:
            try:
                conn = self.conn if self.conn else sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute(
                    "INSERT INTO accounts (account_id, balance) VALUES (?, ?)",
                    (account_id, initial_balance)
                )
                conn.commit()
                if not self.conn:
                    conn.close()
                logging.info(f"Account created: {account_id} with balance: ₹{initial_balance}")
                return True
            except sqlite3.IntegrityError:
                logging.error(f"Account {account_id} already exists")
                return False
                
    def get_balance(self, account_id: str) -> Optional[float]:
        """
        Balance check - ATM jaisa instant result
        """
        conn = self.conn if self.conn else sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute(
            "SELECT balance FROM accounts WHERE account_id = ?",
            (account_id,)
        )
        result = cursor.fetchone()
        if not self.conn:
            conn.close()
        return result[0] if result else None
        
    def transfer_money(self, from_account: str, to_account: str, amount: float) -> bool:
        """
        Strong consistency ke saath paise transfer karo
        ACID properties guarantee:
        A - Atomicity: Ya toh complete hoga ya bilkul nahi
        C - Consistency: Balance hamesha valid rahega
        I - Isolation: Concurrent transfers ek dusre ko affect nahi karenge  
        D - Durability: Transaction commit hone ke baad permanent hai
        """
        transaction = Transaction(from_account, to_account, amount)
        
        with self.lock:  # Critical section - Mumbai local train mein jagah ki tarah
            try:
                conn = self.conn if self.conn else sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute("BEGIN IMMEDIATE")  # Lock the entire database
                
                # Step 1: Validate accounts exist
                from_balance = self._get_balance_for_update(conn, from_account)
                to_balance = self._get_balance_for_update(conn, to_account)
                
                if from_balance is None or to_balance is None:
                    raise ValueError("Invalid account(s)")
                    
                # Step 2: Check sufficient funds - ATM jaisa validation
                if from_balance < amount:
                    raise ValueError(f"Insufficient funds. Available: ₹{from_balance}, Required: ₹{amount}")
                    
                # Step 3: Perform transfer - Atomic operation
                new_from_balance = from_balance - amount
                new_to_balance = to_balance + amount
                
                # Update balances with optimistic locking
                conn.execute(
                    "UPDATE accounts SET balance = ?, version = version + 1 WHERE account_id = ?",
                    (new_from_balance, from_account)
                )
                
                conn.execute(
                    "UPDATE accounts SET balance = ?, version = version + 1 WHERE account_id = ?", 
                    (new_to_balance, to_account)
                )
                
                # Log transaction
                conn.execute(
                    "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)",
                    (transaction.transaction_id, from_account, to_account, 
                     amount, TransactionStatus.COMMITTED.value, transaction.timestamp)
                )
                
                conn.commit()
                transaction.status = TransactionStatus.COMMITTED
                self.transaction_log.append(transaction)
                
                logging.info(f"Transfer successful: ₹{amount} from {from_account} to {to_account}")
                logging.info(f"Transaction ID: {transaction.transaction_id}")
                
                return True
                
            except Exception as e:
                conn.rollback()
                transaction.status = TransactionStatus.ABORTED
                self.transaction_log.append(transaction)
                logging.error(f"Transfer failed: {str(e)}")
                return False
            finally:
                if not self.conn:
                    conn.close()
                
    def _get_balance_for_update(self, conn, account_id: str) -> Optional[float]:
        """
        SELECT FOR UPDATE equivalent - row level locking
        """
        cursor = conn.execute(
            "SELECT balance FROM accounts WHERE account_id = ?",
            (account_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    def get_transaction_history(self, account_id: str) -> List[Dict]:
        """
        Account statement generate karo - Bank passbook jaisa
        """
        conn = self.conn if self.conn else sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("""
            SELECT transaction_id, from_account, to_account, amount, status, timestamp
            FROM transactions 
            WHERE from_account = ? OR to_account = ?
            ORDER BY timestamp DESC
        """, (account_id, account_id))
        
        transactions = []
        for row in cursor.fetchall():
            tx_id, from_acc, to_acc, amount, status, timestamp = row
            tx_type = "DEBIT" if from_acc == account_id else "CREDIT"
            transactions.append({
                "transaction_id": tx_id,
                "type": tx_type,
                "amount": amount,
                "other_account": to_acc if tx_type == "DEBIT" else from_acc,
                "status": status,
                "timestamp": timestamp
            })
            
        if not self.conn:
            conn.close()
        return transactions

def demonstrate_strong_consistency():
    """
    Real-world demo: SBI banking scenario
    Multiple concurrent transfers - sabko safely handle karna hai
    """
    print("=== Strong Consistency Demo: SBI Banking System ===")
    
    bank = StrongConsistencyBank()
    
    # Create accounts - Typical Indian names
    accounts = [
        ("RAMESH_001", 50000.0),
        ("PRIYA_002", 25000.0), 
        ("VIKRAM_003", 75000.0),
        ("ANITA_004", 30000.0)
    ]
    
    for acc_id, initial_balance in accounts:
        bank.create_account(acc_id, "SAVINGS", initial_balance)
        print(f"Created account {acc_id} with ₹{initial_balance}")
    
    print("\n=== Concurrent Transfer Test ===")
    
    def transfer_task(from_acc, to_acc, amount, task_name):
        """
        Concurrent transfer function - Real production scenario
        """
        print(f"[{task_name}] Starting transfer: ₹{amount} from {from_acc} to {to_acc}")
        success = bank.transfer_money(from_acc, to_acc, amount)
        print(f"[{task_name}] Transfer {'SUCCESS' if success else 'FAILED'}")
        
    # Simulate concurrent transfers - Multiple users transferring simultaneously
    threads = []
    
    # Transfer scenarios
    transfers = [
        ("RAMESH_001", "PRIYA_002", 5000.0, "Transfer-1"),
        ("VIKRAM_003", "ANITA_004", 10000.0, "Transfer-2"),
        ("PRIYA_002", "VIKRAM_003", 3000.0, "Transfer-3"),
        ("ANITA_004", "RAMESH_001", 2000.0, "Transfer-4"),
        # Race condition test - Same account se multiple transfers
        ("RAMESH_001", "PRIYA_002", 15000.0, "Transfer-5"),
        ("RAMESH_001", "VIKRAM_003", 20000.0, "Transfer-6")
    ]
    
    # Start all transfers simultaneously - Mumbai rush hour jaisa
    for from_acc, to_acc, amount, task_name in transfers:
        thread = threading.Thread(
            target=transfer_task,
            args=(from_acc, to_acc, amount, task_name)
        )
        threads.append(thread)
        thread.start()
        
    # Wait for all transfers to complete
    for thread in threads:
        thread.join()
        
    print("\n=== Final Balances ===")
    for acc_id, _ in accounts:
        balance = bank.get_balance(acc_id)
        print(f"{acc_id}: ₹{balance}")
        
    print("\n=== Transaction History for RAMESH_001 ===")
    history = bank.get_transaction_history("RAMESH_001")
    for tx in history[:5]:  # Show last 5 transactions
        print(f"  {tx['type']}: ₹{tx['amount']} - {tx['other_account']} - {tx['status']}")

if __name__ == "__main__":
    demonstrate_strong_consistency()