#!/usr/bin/env python3
"""
HDFC Bank Consistency Models - Episode 4
भारतीय banking system में consistency का practical implementation

यह example दिखाता है कि कैसे HDFC Bank जैसे Indian banks
distributed transactions handle करते हैं with strong consistency.

Real scenarios:
- ATM withdrawal across different locations
- IMPS/NEFT transfers between banks
- Credit card transactions during network issues
- Account balance synchronization
"""

import time
import threading
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from decimal import Decimal, getcontext
import hashlib

# Set decimal precision for banking calculations
getcontext().prec = 10

class TransactionType(Enum):
    """Indian banking transaction types"""
    DEPOSIT = "deposit"           # Cash/cheque deposit
    WITHDRAWAL = "withdrawal"     # ATM/branch withdrawal  
    TRANSFER = "transfer"         # IMPS/NEFT/RTGS
    CARD_PAYMENT = "card_payment" # Credit/debit card
    UPI_PAYMENT = "upi_payment"   # UPI transactions

class AccountType(Enum):
    """HDFC account types"""
    SAVINGS = "savings"           # Savings account
    CURRENT = "current"           # Current account
    SALARY = "salary"             # Salary account
    CREDIT_CARD = "credit_card"   # Credit card account

class ConsistencyLevel(Enum):
    """Banking consistency requirements"""
    ACID_STRICT = "acid_strict"   # Core banking operations
    SEQUENTIAL = "sequential"     # Branch transactions
    CAUSAL = "causal"            # Related transactions
    EVENTUAL = "eventual"        # Statement generation

@dataclass
class Transaction:
    """Banking transaction representation"""
    txn_id: str
    account_number: str
    transaction_type: TransactionType
    amount: Decimal
    timestamp: datetime
    description: str
    reference_number: str
    branch_code: str = "HDFC001"
    channel: str = "ATM"          # ATM, Internet, Mobile, Branch
    status: str = "pending"       # pending, completed, failed, reversed
    
    def __post_init__(self):
        if not self.txn_id:
            self.txn_id = str(uuid.uuid4())
        if not self.reference_number:
            self.reference_number = f"HDFC{int(time.time())}"

@dataclass
class Account:
    """HDFC Bank account representation"""
    account_number: str
    account_type: AccountType
    balance: Decimal
    customer_name: str
    branch_code: str
    ifsc_code: str = "HDFC0000001"
    minimum_balance: Decimal = Decimal('10000')
    daily_limit: Decimal = Decimal('50000')
    transaction_history: List[Transaction] = None
    last_updated: datetime = None
    version: int = 1  # For optimistic locking
    
    def __post_init__(self):
        if self.transaction_history is None:
            self.transaction_history = []
        if self.last_updated is None:
            self.last_updated = datetime.now()

class HDFCBankingSystem:
    """
    HDFC Bank distributed consistency implementation
    
    Features:
    - ACID compliance for critical operations
    - Distributed transaction coordination  
    - Conflict detection and resolution
    - Audit trail for compliance
    - Real-time balance synchronization
    """
    
    def __init__(self, num_nodes: int = 3):
        self.nodes = {}  # node_id -> accounts data
        self.transaction_log = []
        self.pending_transactions = {}
        self.locks = {}  # account_number -> lock
        self.node_locks = {}  # node-level locks
        
        # Initialize banking nodes (data centers)
        for i in range(num_nodes):
            node_id = f"HDFC_DC_{i+1}"  # Mumbai, Delhi, Bangalore
            self.nodes[node_id] = {
                "accounts": {},
                "local_transactions": [],
                "last_sync": datetime.now(),
                "status": "active"
            }
            self.node_locks[node_id] = threading.Lock()
        
        print(f"🏦 HDFC Banking System initialized with {num_nodes} data centers")
        print(f"📍 Locations: Mumbai (Primary), Delhi (DR), Bangalore (Backup)")
        
        # Create sample accounts
        self._create_sample_accounts()

    def _create_sample_accounts(self):
        """Create sample HDFC accounts - Indian customer examples"""
        sample_accounts = [
            {
                "account_number": "50100123456789",
                "customer_name": "Rajesh Kumar Sharma",
                "account_type": AccountType.SAVINGS,
                "balance": Decimal('85000'),
                "branch_code": "HDFC_MUMBAI_001"
            },
            {
                "account_number": "50100987654321", 
                "customer_name": "Priya Singh",
                "account_type": AccountType.SALARY,
                "balance": Decimal('125000'),
                "branch_code": "HDFC_DELHI_002"
            },
            {
                "account_number": "50100555666777",
                "customer_name": "Amit Patel",
                "account_type": AccountType.CURRENT,
                "balance": Decimal('275000'),
                "branch_code": "HDFC_BANGALORE_003"
            }
        ]
        
        for acc_data in sample_accounts:
            account = Account(**acc_data)
            # Replicate account across all nodes
            for node_id in self.nodes:
                self.nodes[node_id]["accounts"][account.account_number] = account
        
        print("✅ Sample accounts created and replicated across all data centers")

    def process_transaction(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Process banking transaction with ACID compliance
        
        यह function India की banking regulations के अनुसार
        transaction को safely process करता है।
        """
        print(f"\n💳 Processing transaction: {transaction.txn_id}")
        print(f"   Account: {transaction.account_number}")
        print(f"   Type: {transaction.transaction_type.value}")
        print(f"   Amount: ₹{transaction.amount}")
        print(f"   Channel: {transaction.channel}")
        
        # Step 1: Pre-transaction validation
        validation_result = self._validate_transaction(transaction)
        if not validation_result[0]:
            return False, validation_result[1]
        
        # Step 2: Acquire distributed locks
        lock_acquired = self._acquire_distributed_lock(transaction.account_number)
        if not lock_acquired:
            return False, "Unable to acquire lock - concurrent transaction in progress"
        
        try:
            # Step 3: Two-phase commit for consistency
            prepare_result = self._prepare_transaction(transaction)
            if not prepare_result[0]:
                return False, prepare_result[1]
            
            # Step 4: Commit transaction across all nodes
            commit_result = self._commit_transaction(transaction)
            if commit_result[0]:
                # Step 5: Update audit log
                self._update_audit_log(transaction, "COMPLETED")
                print(f"✅ Transaction {transaction.txn_id} completed successfully")
                return True, "Transaction completed successfully"
            else:
                # Step 6: Rollback on failure
                self._rollback_transaction(transaction)
                return False, commit_result[1]
        
        finally:
            # Step 7: Release locks
            self._release_distributed_lock(transaction.account_number)

    def _validate_transaction(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Banking transaction validation - Indian compliance checks
        """
        account_number = transaction.account_number
        
        # Check if account exists
        primary_node = list(self.nodes.keys())[0]
        if account_number not in self.nodes[primary_node]["accounts"]:
            return False, "Account not found"
        
        account = self.nodes[primary_node]["accounts"][account_number]
        
        # Check minimum balance (Indian banking requirement)
        if transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
            remaining_balance = account.balance - transaction.amount
            if remaining_balance < account.minimum_balance:
                return False, f"Insufficient balance. Minimum balance requirement: ₹{account.minimum_balance}"
        
        # Check daily transaction limit (RBI compliance)
        daily_total = self._calculate_daily_transactions(account_number)
        if daily_total + transaction.amount > account.daily_limit:
            return False, f"Daily transaction limit exceeded. Limit: ₹{account.daily_limit}"
        
        # Check business hours for high-value transactions
        if transaction.amount > Decimal('200000'):  # ₹2 lakh
            current_hour = datetime.now().hour
            if current_hour < 9 or current_hour > 18:  # 9 AM to 6 PM
                return False, "High-value transactions allowed only during business hours"
        
        print(f"✅ Transaction validation passed for account {account_number}")
        return True, "Validation successful"

    def _calculate_daily_transactions(self, account_number: str) -> Decimal:
        """Calculate today's total transaction amount"""
        today = datetime.now().date()
        daily_total = Decimal('0')
        
        for node_id in self.nodes:
            for txn in self.nodes[node_id]["local_transactions"]:
                if (txn.account_number == account_number and 
                    txn.timestamp.date() == today and
                    txn.status == "completed"):
                    daily_total += txn.amount
        
        return daily_total

    def _acquire_distributed_lock(self, account_number: str) -> bool:
        """
        Distributed locking mechanism for banking consistency
        
        यह ensure करता है कि same account पर concurrent transactions
        safely handle हों - जैसे ATM और internet banking simultaneously use हो रहे हों।
        """
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            all_locks_acquired = True
            acquired_locks = []
            
            try:
                # Try to acquire locks on all nodes
                for node_id in self.nodes:
                    node_lock = self.node_locks[node_id]
                    if node_lock.acquire(timeout=1.0):
                        acquired_locks.append(node_id)
                        
                        # Check if account is already locked
                        if account_number in self.locks:
                            all_locks_acquired = False
                            break
                    else:
                        all_locks_acquired = False
                        break
                
                if all_locks_acquired:
                    # Successfully acquired all locks
                    self.locks[account_number] = {
                        "timestamp": datetime.now(),
                        "thread_id": threading.get_ident(),
                        "nodes": acquired_locks
                    }
                    print(f"🔒 Distributed lock acquired for account {account_number}")
                    return True
                else:
                    # Release any acquired locks
                    for node_id in acquired_locks:
                        self.node_locks[node_id].release()
                    
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
            
            except Exception as e:
                # Release any acquired locks
                for node_id in acquired_locks:
                    try:
                        self.node_locks[node_id].release()
                    except:
                        pass
                print(f"❌ Lock acquisition error: {e}")
                break
        
        print(f"❌ Failed to acquire distributed lock for account {account_number}")
        return False

    def _release_distributed_lock(self, account_number: str):
        """Release distributed locks across all nodes"""
        if account_number in self.locks:
            lock_info = self.locks[account_number]
            
            # Release node locks
            for node_id in lock_info["nodes"]:
                try:
                    self.node_locks[node_id].release()
                except:
                    pass
            
            del self.locks[account_number]
            print(f"🔓 Distributed lock released for account {account_number}")

    def _prepare_transaction(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Two-phase commit preparation phase
        
        यह phase में सभी nodes को transaction के लिए ready करते हैं
        """
        account_number = transaction.account_number
        prepared_nodes = []
        
        try:
            for node_id in self.nodes:
                node = self.nodes[node_id]
                if node["status"] != "active":
                    continue
                
                account = node["accounts"].get(account_number)
                if not account:
                    return False, f"Account not found in node {node_id}"
                
                # Simulate preparation (validation, resource allocation)
                if transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
                    if account.balance < transaction.amount:
                        return False, "Insufficient balance during prepare phase"
                
                # Mark as prepared
                transaction.status = "prepared"
                prepared_nodes.append(node_id)
                
                print(f"📋 Node {node_id} prepared for transaction {transaction.txn_id}")
        
        except Exception as e:
            # Rollback preparation
            for node_id in prepared_nodes:
                transaction.status = "failed"
            return False, f"Preparation failed: {e}"
        
        return True, "All nodes prepared successfully"

    def _commit_transaction(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Two-phase commit - actual transaction execution
        
        यहाँ actual balance update होता है सभी nodes में consistently
        """
        account_number = transaction.account_number
        committed_nodes = []
        
        try:
            for node_id in self.nodes:
                node = self.nodes[node_id]
                if node["status"] != "active":
                    continue
                
                account = node["accounts"][account_number]
                original_balance = account.balance
                
                # Execute transaction based on type
                if transaction.transaction_type == TransactionType.DEPOSIT:
                    account.balance += transaction.amount
                elif transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER, 
                                                    TransactionType.CARD_PAYMENT, TransactionType.UPI_PAYMENT]:
                    account.balance -= transaction.amount
                
                # Update metadata
                account.last_updated = datetime.now()
                account.version += 1
                
                # Add to transaction history
                transaction.status = "completed"
                account.transaction_history.append(transaction)
                node["local_transactions"].append(transaction)
                
                committed_nodes.append(node_id)
                
                print(f"💰 Node {node_id}: Balance updated from ₹{original_balance} to ₹{account.balance}")
        
        except Exception as e:
            # Rollback committed nodes
            self._rollback_committed_nodes(transaction, committed_nodes)
            return False, f"Commit failed: {e}"
        
        return True, "Transaction committed successfully across all nodes"

    def _rollback_committed_nodes(self, transaction: Transaction, committed_nodes: List[str]):
        """Rollback transaction in committed nodes"""
        print(f"🔄 Rolling back transaction {transaction.txn_id} in {len(committed_nodes)} nodes")
        
        account_number = transaction.account_number
        
        for node_id in committed_nodes:
            try:
                node = self.nodes[node_id]
                account = node["accounts"][account_number]
                
                # Reverse the transaction
                if transaction.transaction_type == TransactionType.DEPOSIT:
                    account.balance -= transaction.amount
                elif transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER,
                                                    TransactionType.CARD_PAYMENT, TransactionType.UPI_PAYMENT]:
                    account.balance += transaction.amount
                
                # Remove from history
                account.transaction_history = [t for t in account.transaction_history if t.txn_id != transaction.txn_id]
                node["local_transactions"] = [t for t in node["local_transactions"] if t.txn_id != transaction.txn_id]
                
                print(f"↩️  Rollback completed for node {node_id}")
            
            except Exception as e:
                print(f"❌ Rollback failed for node {node_id}: {e}")

    def _rollback_transaction(self, transaction: Transaction):
        """Full transaction rollback"""
        transaction.status = "failed" 
        self._update_audit_log(transaction, "ROLLED_BACK")
        print(f"🔄 Transaction {transaction.txn_id} rolled back")

    def _update_audit_log(self, transaction: Transaction, status: str):
        """Update audit log for compliance - RBI requirement"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction.txn_id,
            "account_number": transaction.account_number,
            "transaction_type": transaction.transaction_type.value,
            "amount": str(transaction.amount),
            "channel": transaction.channel,
            "branch_code": transaction.branch_code,
            "status": status,
            "checksum": self._calculate_checksum(transaction)
        }
        
        self.transaction_log.append(audit_entry)

    def _calculate_checksum(self, transaction: Transaction) -> str:
        """Calculate transaction checksum for integrity"""
        data = f"{transaction.txn_id}{transaction.account_number}{transaction.amount}{transaction.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def check_balance(self, account_number: str, node_id: str = None) -> Tuple[bool, Dict]:
        """
        Check account balance with consistency verification
        
        यह function different nodes से balance check करके
        consistency verify करता है
        """
        if not node_id:
            node_id = list(self.nodes.keys())[0]  # Primary node
        
        if node_id not in self.nodes:
            return False, {"error": "Invalid node"}
        
        if account_number not in self.nodes[node_id]["accounts"]:
            return False, {"error": "Account not found"}
        
        account = self.nodes[node_id]["accounts"][account_number]
        
        # Verify consistency across nodes
        balances = {}
        for nid in self.nodes:
            if nid in self.nodes and account_number in self.nodes[nid]["accounts"]:
                balances[nid] = self.nodes[nid]["accounts"][account_number].balance
        
        # Check for inconsistencies
        all_balances = list(balances.values())
        is_consistent = all(balance == all_balances[0] for balance in all_balances)
        
        result = {
            "account_number": account_number,
            "customer_name": account.customer_name,
            "current_balance": str(account.balance),
            "account_type": account.account_type.value,
            "branch_code": account.branch_code,
            "last_updated": account.last_updated.isoformat(),
            "is_consistent": is_consistent,
            "node_balances": {k: str(v) for k, v in balances.items()},
            "daily_transaction_limit": str(account.daily_limit),
            "minimum_balance": str(account.minimum_balance)
        }
        
        if not is_consistent:
            print(f"⚠️  CONSISTENCY WARNING: Balance mismatch detected for account {account_number}")
            result["consistency_error"] = "Balance mismatch across nodes"
        
        return True, result

    def simulate_concurrent_transactions(self, account_number: str, num_transactions: int = 5):
        """
        Simulate concurrent transactions - जैसे ATM और mobile banking साथ में use हो रहे हों
        """
        print(f"\n🔥 Simulating {num_transactions} concurrent transactions for account {account_number}")
        
        def create_transaction(txn_type: TransactionType, amount: Decimal, channel: str):
            return Transaction(
                txn_id=str(uuid.uuid4()),
                account_number=account_number,
                transaction_type=txn_type,
                amount=amount,
                timestamp=datetime.now(),
                description=f"Concurrent {txn_type.value} via {channel}",
                reference_number=f"CONC{int(time.time())}{random.randint(100, 999)}",
                channel=channel
            )
        
        # Create concurrent transactions
        transactions = []
        channels = ["ATM", "Mobile Banking", "Internet Banking", "Branch", "UPI"]
        types = [TransactionType.WITHDRAWAL, TransactionType.DEPOSIT, TransactionType.UPI_PAYMENT]
        
        for i in range(num_transactions):
            txn_type = types[i % len(types)]
            amount = Decimal(str(random.randint(1000, 5000)))
            channel = channels[i % len(channels)]
            
            transactions.append(create_transaction(txn_type, amount, channel))
        
        # Execute transactions concurrently
        results = []
        threads = []
        
        for transaction in transactions:
            def execute_txn(txn):
                result = self.process_transaction(txn)
                results.append((txn.txn_id, result))
            
            thread = threading.Thread(target=execute_txn, args=(transaction,))
            threads.append(thread)
            thread.start()
        
        # Wait for all transactions to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful = sum(1 for _, result in results if result[0])
        failed = len(results) - successful
        
        print(f"\n📊 Concurrent Transaction Results:")
        print(f"   Total: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        # Check final consistency
        balance_result = self.check_balance(account_number)
        if balance_result[0]:
            balance_info = balance_result[1]
            print(f"   Final Balance: ₹{balance_info['current_balance']}")
            print(f"   Consistency: {'✅ CONSISTENT' if balance_info['is_consistent'] else '❌ INCONSISTENT'}")

    def generate_account_statement(self, account_number: str, days: int = 30) -> Dict:
        """
        Generate account statement - Indian banking format
        """
        if account_number not in self.nodes[list(self.nodes.keys())[0]]["accounts"]:
            return {"error": "Account not found"}
        
        account = self.nodes[list(self.nodes.keys())[0]]["accounts"][account_number]
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter transactions
        transactions = []
        for txn in account.transaction_history:
            if txn.timestamp >= cutoff_date:
                transactions.append({
                    "date": txn.timestamp.strftime("%d-%m-%Y"),
                    "description": txn.description,
                    "reference": txn.reference_number,
                    "debit": str(txn.amount) if txn.transaction_type in [
                        TransactionType.WITHDRAWAL, TransactionType.TRANSFER, 
                        TransactionType.CARD_PAYMENT, TransactionType.UPI_PAYMENT
                    ] else "",
                    "credit": str(txn.amount) if txn.transaction_type == TransactionType.DEPOSIT else "",
                    "balance": str(account.balance),  # Simplified - should calculate running balance
                    "channel": txn.channel
                })
        
        statement = {
            "account_number": account_number,
            "customer_name": account.customer_name,
            "account_type": account.account_type.value,
            "statement_period": f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}",
            "opening_balance": str(account.balance),  # Simplified
            "closing_balance": str(account.balance),
            "total_transactions": len(transactions),
            "transactions": transactions
        }
        
        return statement

import random

def main():
    """
    Main demo - HDFC Bank consistency scenarios
    """
    print("🏦 HDFC Bank Distributed Consistency Demo")
    print("=" * 50)
    
    # Initialize banking system
    hdfc_system = HDFCBankingSystem(num_nodes=3)
    
    # Scenario 1: Normal transaction processing
    print("\n💳 SCENARIO 1: Normal ATM Withdrawal")
    atm_withdrawal = Transaction(
        txn_id="TXN001",
        account_number="50100123456789",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=Decimal('5000'),
        timestamp=datetime.now(),
        description="ATM Withdrawal - Connaught Place",
        reference_number="ATM123456",
        channel="ATM"
    )
    
    success, message = hdfc_system.process_transaction(atm_withdrawal)
    print(f"Result: {message}")
    
    # Check balance consistency
    balance_result = hdfc_system.check_balance("50100123456789")
    if balance_result[0]:
        print(f"Updated Balance: ₹{balance_result[1]['current_balance']}")
    
    # Scenario 2: UPI Payment
    print("\n📱 SCENARIO 2: UPI Payment")
    upi_payment = Transaction(
        txn_id="TXN002",
        account_number="50100987654321",
        transaction_type=TransactionType.UPI_PAYMENT,
        amount=Decimal('1500'),
        timestamp=datetime.now(),
        description="UPI Payment to Zomato",
        reference_number="UPI789012",
        channel="Mobile Banking"
    )
    
    success, message = hdfc_system.process_transaction(upi_payment)
    print(f"Result: {message}")
    
    # Scenario 3: Concurrent transactions simulation
    print("\n🔥 SCENARIO 3: Concurrent Transactions Test")
    hdfc_system.simulate_concurrent_transactions("50100555666777", num_transactions=3)
    
    # Scenario 4: Account statement generation
    print("\n📄 SCENARIO 4: Account Statement Generation")
    statement = hdfc_system.generate_account_statement("50100123456789")
    print(f"Statement generated for: {statement['customer_name']}")
    print(f"Total transactions: {statement['total_transactions']}")
    print(f"Current balance: ₹{statement['closing_balance']}")
    
    print("\n✅ HDFC Banking consistency demo completed!")
    print("\nKey learnings:")
    print("1. Banking requires ACID compliance for data integrity")
    print("2. Distributed locking prevents concurrent access issues") 
    print("3. Two-phase commit ensures consistency across data centers")
    print("4. Audit logging is mandatory for regulatory compliance")
    print("5. Real-time balance synchronization prevents overdrafts")

if __name__ == "__main__":
    main()