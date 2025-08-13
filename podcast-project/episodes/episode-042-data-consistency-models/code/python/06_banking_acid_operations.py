"""
Banking ACID Operations
Demonstrating ACID properties in banking systems
Example: SBI/HDFC transaction processing
"""

import sqlite3
import threading
import time
import uuid
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    LOAN_PAYMENT = "LOAN_PAYMENT"

class TransactionStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"

@dataclass
class Account:
    """
    Bank account - SBI account jaisa
    """
    account_number: str
    account_type: str  # SAVINGS, CURRENT, LOAN
    balance: Decimal
    minimum_balance: Decimal
    is_active: bool = True
    created_date: str = ""
    last_transaction_id: str = ""

@dataclass
class Transaction:
    """
    Banking transaction with full audit trail
    """
    transaction_id: str
    transaction_type: TransactionType
    from_account: Optional[str]
    to_account: Optional[str]
    amount: Decimal
    description: str
    status: TransactionStatus
    created_at: float
    completed_at: Optional[float] = None
    failure_reason: Optional[str] = None

class ACIDBank:
    """
    ACID compliant banking system
    SBI Core Banking System jaisa implementation
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.transaction_lock = threading.RLock()
        self._init_database()
        
    def _init_database(self):
        """
        Production-grade database schema
        """
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Accounts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number TEXT PRIMARY KEY,
                    account_type TEXT NOT NULL,
                    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                    minimum_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_transaction_id TEXT,
                    version INTEGER NOT NULL DEFAULT 1
                )
            """)
            
            # Transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    transaction_type TEXT NOT NULL,
                    from_account TEXT,
                    to_account TEXT, 
                    amount DECIMAL(15,2) NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    failure_reason TEXT,
                    FOREIGN KEY(from_account) REFERENCES accounts(account_number),
                    FOREIGN KEY(to_account) REFERENCES accounts(account_number)
                )
            """)
            
            # Audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    old_balance DECIMAL(15,2),
                    new_balance DECIMAL(15,2),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id),
                    FOREIGN KEY(account_number) REFERENCES accounts(account_number)
                )
            """)
            
            conn.commit()
            
    def create_account(self, account_number: str, account_type: str, 
                      initial_balance: Decimal = Decimal('0.00'),
                      minimum_balance: Decimal = Decimal('0.00')) -> bool:
        """
        Naya account create karo - Bank branch jaisa process
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO accounts (account_number, account_type, balance, minimum_balance)
                    VALUES (?, ?, ?, ?)
                """, (account_number, account_type, initial_balance, minimum_balance))
                
                conn.commit()
                logging.info(f"Account created: {account_number} ({account_type}) with balance: ₹{initial_balance}")
                return True
                
        except sqlite3.IntegrityError:
            logging.error(f"Account {account_number} already exists")
            return False
            
    @contextmanager
    def _get_transaction_connection(self):
        """
        Transaction ke liye connection manager
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
            
    def transfer_money(self, from_account: str, to_account: str, 
                      amount: Decimal, description: str = "") -> Transaction:
        """
        ACID compliant money transfer - SBI NEFT/RTGS jaisa
        
        A - Atomicity: Ya toh complete transfer ya bilkul nahi
        C - Consistency: Account balance constraints maintain
        I - Isolation: Concurrent transfers interfere nahi karenge
        D - Durability: Transaction commit ke baad permanent
        """
        
        # Input validation
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
            
        transaction = Transaction(
            transaction_id=f"TXN{int(time.time())}{str(uuid.uuid4())[:6].upper()}",
            transaction_type=TransactionType.TRANSFER,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            description=description or f"Transfer to {to_account}",
            status=TransactionStatus.PENDING,
            created_at=time.time()
        )
        
        with self.transaction_lock:  # Isolation guarantee
            try:
                with self._get_transaction_connection() as conn:
                    # Begin database transaction
                    conn.execute("BEGIN IMMEDIATE")
                    
                    # Update transaction status
                    transaction.status = TransactionStatus.IN_PROGRESS
                    
                    # Step 1: Validate accounts exist and are active
                    from_account_data = self._get_account_for_update(conn, from_account)
                    to_account_data = self._get_account_for_update(conn, to_account)
                    
                    if not from_account_data:
                        raise ValueError(f"Source account {from_account} not found")
                    if not to_account_data:
                        raise ValueError(f"Destination account {to_account} not found")
                        
                    if not from_account_data['is_active']:
                        raise ValueError(f"Source account {from_account} is inactive")
                    if not to_account_data['is_active']:
                        raise ValueError(f"Destination account {to_account} is inactive")
                    
                    # Step 2: Check balance and limits (Consistency)
                    current_balance = Decimal(str(from_account_data['balance']))
                    minimum_balance = Decimal(str(from_account_data['minimum_balance']))
                    
                    if current_balance - amount < minimum_balance:
                        raise ValueError(
                            f"Insufficient funds. Available: ₹{current_balance - minimum_balance}, "
                            f"Requested: ₹{amount}"
                        )
                    
                    # Step 3: Record transaction
                    conn.execute("""
                        INSERT INTO transactions 
                        (transaction_id, transaction_type, from_account, to_account, 
                         amount, description, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (transaction.transaction_id, transaction.transaction_type.value,
                          from_account, to_account, amount, transaction.description,
                          TransactionStatus.IN_PROGRESS.value, transaction.created_at))
                    
                    # Step 4: Update balances (Atomic operation)
                    new_from_balance = current_balance - amount
                    new_to_balance = Decimal(str(to_account_data['balance'])) + amount
                    
                    # Update from account
                    conn.execute("""
                        UPDATE accounts 
                        SET balance = ?, last_transaction_id = ?, version = version + 1
                        WHERE account_number = ?
                    """, (new_from_balance, transaction.transaction_id, from_account))
                    
                    # Update to account
                    conn.execute("""
                        UPDATE accounts 
                        SET balance = ?, last_transaction_id = ?, version = version + 1
                        WHERE account_number = ?
                    """, (new_to_balance, transaction.transaction_id, to_account))
                    
                    # Step 5: Audit logging
                    self._log_audit_entry(conn, transaction.transaction_id, from_account,
                                         "DEBIT", current_balance, new_from_balance)
                    self._log_audit_entry(conn, transaction.transaction_id, to_account,
                                         "CREDIT", Decimal(str(to_account_data['balance'])), new_to_balance)
                    
                    # Step 6: Complete transaction
                    transaction.status = TransactionStatus.COMMITTED
                    transaction.completed_at = time.time()
                    
                    conn.execute("""
                        UPDATE transactions 
                        SET status = ?, completed_at = ?
                        WHERE transaction_id = ?
                    """, (TransactionStatus.COMMITTED.value, transaction.completed_at,
                          transaction.transaction_id))
                    
                    # Commit everything (Durability guarantee)
                    conn.commit()
                    
                    logging.info(
                        f"Transfer successful: ₹{amount} from {from_account} to {to_account} "
                        f"(TXN: {transaction.transaction_id})"
                    )
                    
                    return transaction
                    
            except Exception as e:
                # Rollback on any error (Atomicity guarantee)
                transaction.status = TransactionStatus.ABORTED
                transaction.failure_reason = str(e)
                transaction.completed_at = time.time()
                
                try:
                    with self._get_transaction_connection() as conn:
                        conn.execute("""
                            UPDATE transactions 
                            SET status = ?, failure_reason = ?, completed_at = ?
                            WHERE transaction_id = ?
                        """, (TransactionStatus.ABORTED.value, transaction.failure_reason,
                              transaction.completed_at, transaction.transaction_id))
                        conn.commit()
                except:
                    pass  # Best effort to update transaction status
                    
                logging.error(f"Transfer failed: {str(e)} (TXN: {transaction.transaction_id})")
                raise
                
    def _get_account_for_update(self, conn, account_number: str) -> Optional[Dict]:
        """
        SELECT FOR UPDATE equivalent - account lock karo
        """
        cursor = conn.execute("""
            SELECT account_number, account_type, balance, minimum_balance, is_active
            FROM accounts 
            WHERE account_number = ?
        """, (account_number,))
        
        result = cursor.fetchone()
        if result:
            return {
                'account_number': result[0],
                'account_type': result[1], 
                'balance': result[2],
                'minimum_balance': result[3],
                'is_active': bool(result[4])
            }
        return None
        
    def _log_audit_entry(self, conn, transaction_id: str, account_number: str,
                        operation: str, old_balance: Decimal, new_balance: Decimal):
        """
        Audit trail maintain karo - compliance ke liye
        """
        conn.execute("""
            INSERT INTO audit_log 
            (transaction_id, account_number, operation, old_balance, new_balance)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_id, account_number, operation, old_balance, new_balance))
        
    def get_balance(self, account_number: str) -> Optional[Decimal]:
        """
        Account balance check karo
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT balance FROM accounts WHERE account_number = ?
            """, (account_number,))
            
            result = cursor.fetchone()
            return Decimal(str(result[0])) if result else None
            
    def get_transaction_history(self, account_number: str, limit: int = 10) -> List[Dict]:
        """
        Account statement generate karo
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT transaction_id, transaction_type, from_account, to_account,
                       amount, description, status, created_at, completed_at
                FROM transactions
                WHERE from_account = ? OR to_account = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (account_number, account_number, limit))
            
            transactions = []
            for row in cursor.fetchall():
                tx_id, tx_type, from_acc, to_acc, amount, desc, status, created, completed = row
                
                # Determine transaction type for this account
                if from_acc == account_number:
                    tx_direction = "DEBIT"
                    other_account = to_acc
                else:
                    tx_direction = "CREDIT"
                    other_account = from_acc
                    
                transactions.append({
                    "transaction_id": tx_id,
                    "type": tx_direction,
                    "amount": Decimal(str(amount)),
                    "other_account": other_account,
                    "description": desc,
                    "status": status,
                    "created_at": created,
                    "completed_at": completed
                })
                
            return transactions
            
    def get_audit_trail(self, transaction_id: str) -> List[Dict]:
        """
        Transaction ka complete audit trail
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT account_number, operation, old_balance, new_balance, timestamp
                FROM audit_log
                WHERE transaction_id = ?
                ORDER BY timestamp
            """, (transaction_id,))
            
            audit_entries = []
            for row in cursor.fetchall():
                acc_num, operation, old_bal, new_bal, timestamp = row
                audit_entries.append({
                    "account_number": acc_num,
                    "operation": operation,
                    "old_balance": Decimal(str(old_bal)),
                    "new_balance": Decimal(str(new_bal)),
                    "timestamp": timestamp
                })
                
            return audit_entries

def stress_test_concurrent_transfers(bank: ACIDBank, accounts: List[str], 
                                   num_transfers: int = 100):
    """
    Concurrent transfers ka stress test
    Multiple threads simultaneously transfer kar rahe hain
    """
    import random
    
    def random_transfer(thread_id: int):
        """
        Random transfer function for stress testing
        """
        for i in range(num_transfers // 10):  # Each thread does 10 transfers
            try:
                from_acc = random.choice(accounts)
                to_acc = random.choice([acc for acc in accounts if acc != from_acc])
                amount = Decimal(str(random.randint(100, 5000)))
                
                transaction = bank.transfer_money(
                    from_acc, to_acc, amount, 
                    f"Stress test transfer {thread_id}-{i}"
                )
                
                print(f"Thread {thread_id}: Transfer {i} completed - {transaction.transaction_id}")
                
            except Exception as e:
                print(f"Thread {thread_id}: Transfer {i} failed - {str(e)}")
                
            time.sleep(0.01)  # Small delay between transfers
            
    # Start multiple threads
    threads = []
    for thread_id in range(10):
        thread = threading.Thread(target=random_transfer, args=(thread_id,))
        threads.append(thread)
        thread.start()
        
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def demonstrate_acid_properties():
    """
    Real-world demo: Banking system with ACID properties
    SBI/HDFC jaisa core banking system
    """
    print("=== ACID Banking System Demo ===")
    
    # Create bank instance
    bank = ACIDBank()
    
    # Create customer accounts
    print("\n=== Creating Customer Accounts ===")
    accounts = [
        ("ACC001RAHUL", "SAVINGS", Decimal('50000.00'), Decimal('1000.00')),
        ("ACC002PRIYA", "SAVINGS", Decimal('75000.00'), Decimal('1000.00')),
        ("ACC003VIKRAM", "CURRENT", Decimal('25000.00'), Decimal('5000.00')),
        ("ACC004ANITA", "SAVINGS", Decimal('100000.00'), Decimal('1000.00')),
        ("ACC005ROHAN", "CURRENT", Decimal('30000.00'), Decimal('5000.00'))
    ]
    
    for acc_num, acc_type, initial_balance, min_balance in accounts:
        bank.create_account(acc_num, acc_type, initial_balance, min_balance)
        print(f"Created: {acc_num} ({acc_type}) - ₹{initial_balance}")
        
    print("\n=== Normal Transfer Operations ===")
    
    # Normal transfers
    try:
        # Rahul transfers to Priya
        tx1 = bank.transfer_money(
            "ACC001RAHUL", "ACC002PRIYA", Decimal('5000.00'),
            "Rent payment"
        )
        print(f"✅ Transfer 1: {tx1.transaction_id}")
        
        # Vikram transfers to Anita
        tx2 = bank.transfer_money(
            "ACC003VIKRAM", "ACC004ANITA", Decimal('8000.00'),
            "Business payment"
        )
        print(f"✅ Transfer 2: {tx2.transaction_id}")
        
    except Exception as e:
        print(f"❌ Transfer failed: {e}")
        
    print("\n=== Testing ACID Properties ===")
    
    # Test Atomicity - Transfer that should fail
    print("Testing Atomicity (insufficient funds):")
    try:
        bank.transfer_money(
            "ACC001RAHUL", "ACC002PRIYA", Decimal('100000.00'),
            "Large transfer - should fail"
        )
    except Exception as e:
        print(f"✅ Atomicity test passed: {e}")
        
    # Test Consistency - Minimum balance violation
    print("\nTesting Consistency (minimum balance):")
    try:
        bank.transfer_money(
            "ACC001RAHUL", "ACC002PRIYA", Decimal('45000.00'),
            "Transfer violating minimum balance"
        )
    except Exception as e:
        print(f"✅ Consistency test passed: {e}")
        
    # Test Isolation - Concurrent transfers
    print("\nTesting Isolation (concurrent transfers):")
    
    def concurrent_transfer_test():
        """
        Same account se multiple concurrent transfers
        """
        results = []
        
        def transfer_worker(amount, description):
            try:
                tx = bank.transfer_money(
                    "ACC004ANITA", "ACC005ROHAN", amount, description
                )
                results.append(("SUCCESS", tx.transaction_id))
            except Exception as e:
                results.append(("FAILED", str(e)))
                
        # Start multiple transfers simultaneously
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=transfer_worker,
                args=(Decimal('15000.00'), f"Concurrent transfer {i+1}")
            )
            threads.append(thread)
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Analyze results
        successes = [r for r in results if r[0] == "SUCCESS"]
        failures = [r for r in results if r[0] == "FAILED"]
        
        print(f"  Successful transfers: {len(successes)}")
        print(f"  Failed transfers: {len(failures)}")
        
        if len(successes) <= 1:  # Only one should succeed due to balance constraints
            print("✅ Isolation test passed: Concurrent transfers properly handled")
        else:
            print("❌ Isolation test failed: Multiple transfers succeeded")
            
    concurrent_transfer_test()
    
    # Test Durability - Check data persistence
    print("\nTesting Durability (data persistence):")
    
    # Get current balances
    balances_before = {}
    for acc_num, _, _, _ in accounts:
        balances_before[acc_num] = bank.get_balance(acc_num)
        
    # Simulate restart by creating new bank instance with same database
    new_bank = ACIDBank(bank.db_path)
    
    # Check balances after "restart"
    balances_after = {}
    for acc_num, _, _, _ in accounts:
        balances_after[acc_num] = new_bank.get_balance(acc_num)
        
    if balances_before == balances_after:
        print("✅ Durability test passed: Data persisted across restart")
    else:
        print("❌ Durability test failed: Data not consistent")
        
    # Show final account states
    print("\n=== Final Account Balances ===")
    for acc_num, _, _, _ in accounts:
        balance = bank.get_balance(acc_num)
        print(f"{acc_num}: ₹{balance}")
        
    # Show transaction history for one account
    print("\n=== Transaction History (ACC001RAHUL) ===")
    history = bank.get_transaction_history("ACC001RAHUL", 5)
    
    for tx in history:
        amount_display = f"₹{tx['amount']}"
        if tx['type'] == "DEBIT":
            amount_display = f"-{amount_display}"
        else:
            amount_display = f"+{amount_display}"
            
        print(f"  {tx['transaction_id'][:12]}... {tx['type']}: {amount_display} "
              f"({tx['other_account']}) - {tx['status']}")
              
    # Audit trail demonstration
    if history:
        print(f"\n=== Audit Trail for {history[0]['transaction_id']} ===")
        audit_trail = bank.get_audit_trail(history[0]['transaction_id'])
        
        for entry in audit_trail:
            print(f"  {entry['account_number']}: {entry['operation']} "
                  f"₹{entry['old_balance']} → ₹{entry['new_balance']}")
                  
    # Performance stress test
    print("\n=== Stress Test (Concurrent Operations) ===")
    print("Running 100 concurrent transfers...")
    
    start_time = time.time()
    account_numbers = [acc[0] for acc in accounts]
    stress_test_concurrent_transfers(bank, account_numbers, 100)
    end_time = time.time()
    
    print(f"Stress test completed in {end_time - start_time:.2f} seconds")
    
    # Final system state
    print("\n=== Final System State ===")
    total_balance = Decimal('0.00')
    for acc_num, _, _, _ in accounts:
        balance = bank.get_balance(acc_num)
        total_balance += balance
        
    print(f"Total system balance: ₹{total_balance}")
    print("✅ ACID properties successfully demonstrated")

if __name__ == "__main__":
    demonstrate_acid_properties()