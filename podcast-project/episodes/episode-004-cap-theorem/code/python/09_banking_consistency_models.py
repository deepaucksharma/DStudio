#!/usr/bin/env python3
"""
Banking System Consistency Models - Episode 4
भारतीय Banking System में विभिन्न Consistency Models का उपयोग

यह example दिखाता है कि कैसे विभिन्न banking operations के लिए
अलग-अलग consistency requirements होती हैं।

Indian Banking Context:
- NEFT/RTGS: Strong consistency (पैसा duplicate नहीं हो सकता)
- UPI: Eventual consistency (speed के लिए)
- Account Balance Check: Weak consistency acceptable (real-time नहीं चाहिए)
"""

import time
import threading
from decimal import Decimal, getcontext
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import uuid
import hashlib
import json

# Set decimal precision for financial calculations
getcontext().prec = 10

class TransactionType(Enum):
    """Different types of banking transactions"""
    NEFT = "neft"           # National Electronic Funds Transfer
    RTGS = "rtgs"          # Real Time Gross Settlement  
    UPI = "upi"            # Unified Payments Interface
    IMPS = "imps"          # Immediate Payment Service
    BALANCE_CHECK = "balance_check"
    ATM_WITHDRAWAL = "atm_withdrawal"

class ConsistencyLevel(Enum):
    """Banking के लिए consistency levels"""
    STRONG = "strong"           # NEFT/RTGS के लिए
    BOUNDED_STALENESS = "bounded_staleness"  # ATM balance
    EVENTUAL = "eventual"       # UPI notifications
    SESSION = "session"         # User session के अंदर consistent

@dataclass
class BankAccount:
    """Indian bank account representation"""
    account_number: str
    holder_name: str
    ifsc_code: str  # Indian Financial System Code
    balance: Decimal = Decimal('0.00')
    bank_name: str = "State Bank of India"
    branch: str = "Mumbai Main"
    last_updated: float = field(default_factory=time.time)
    version: int = 0  # For optimistic locking
    
    def __post_init__(self):
        # Generate account checksum for integrity
        account_data = f"{self.account_number}{self.holder_name}{self.ifsc_code}"
        self.checksum = hashlib.md5(account_data.encode()).hexdigest()

@dataclass
class Transaction:
    """Banking transaction with Indian context"""
    txn_id: str
    txn_type: TransactionType
    from_account: str
    to_account: str
    amount: Decimal
    timestamp: float
    status: str = "PENDING"  # PENDING, SUCCESS, FAILED, REVERSED
    utr_number: str = ""  # Unique Transaction Reference (for NEFT/RTGS)
    merchant_id: str = ""  # For UPI merchants
    remarks: str = ""
    
    def __post_init__(self):
        if not self.utr_number and self.txn_type in [TransactionType.NEFT, TransactionType.RTGS]:
            # Generate UTR number for NEFT/RTGS
            timestamp_str = str(int(self.timestamp))
            self.utr_number = f"SBIN{timestamp_str[-6:]}{self.from_account[-4:]}"

class BankingNode:
    """
    Banking system node - represents different bank branches/data centers
    Each node maintains account data with different consistency guarantees
    """
    
    def __init__(self, node_id: str, region: str = "Mumbai"):
        self.node_id = node_id
        self.region = region
        self.accounts: Dict[str, BankAccount] = {}
        self.transaction_log: List[Transaction] = []
        self.is_active = True
        self.last_heartbeat = time.time()
        self.pending_transactions: List[Transaction] = []
        
        print(f"🏦 Banking Node {node_id} initialized in {region}")

    def create_account(self, account_number: str, holder_name: str, 
                      ifsc_code: str, initial_balance: Decimal = Decimal('1000.00')):
        """Create new bank account with KYC compliance"""
        
        if len(account_number) != 11:  # Indian account numbers are typically 11 digits
            raise ValueError("Invalid account number format")
        
        if not ifsc_code.startswith(('SBIN', 'ICIC', 'HDFC', 'AXIS', 'PUNB')):
            raise ValueError("Invalid IFSC code - not a recognized Indian bank")
            
        account = BankAccount(
            account_number=account_number,
            holder_name=holder_name,
            ifsc_code=ifsc_code,
            balance=initial_balance
        )
        
        self.accounts[account_number] = account
        print(f"✅ Account created: {holder_name} ({account_number}) with ₹{initial_balance}")
        return account

    def get_balance(self, account_number: str, consistency_level: ConsistencyLevel) -> Tuple[bool, Optional[Decimal]]:
        """
        Get account balance with different consistency levels
        
        Strong: Real-time balance (for large transactions)
        Bounded Staleness: ATM balance (can be few minutes old)
        Eventual: Mobile app balance (for quick display)
        """
        
        if account_number not in self.accounts:
            return False, None
            
        account = self.accounts[account_number]
        
        if consistency_level == ConsistencyLevel.STRONG:
            # Strong consistency - wait for all pending transactions to complete
            self._wait_for_pending_transactions(account_number)
            print(f"💪 Strong consistency balance for {account_number}: ₹{account.balance}")
            return True, account.balance
            
        elif consistency_level == ConsistencyLevel.BOUNDED_STALENESS:
            # Bounded staleness - balance can be up to 5 minutes old (ATM use case)
            staleness_limit = 300  # 5 minutes in seconds
            if time.time() - account.last_updated < staleness_limit:
                print(f"⏰ Bounded staleness balance for {account_number}: ₹{account.balance}")
                return True, account.balance
            else:
                # Need to refresh
                self._refresh_account_data(account_number)
                return True, account.balance
                
        elif consistency_level == ConsistencyLevel.EVENTUAL:
            # Eventual consistency - return immediately available balance
            print(f"⚡ Eventually consistent balance for {account_number}: ₹{account.balance}")
            return True, account.balance
            
        else:  # SESSION consistency
            # Session consistency - consistent within user session
            session_balance = self._get_session_balance(account_number)
            return True, session_balance

    def transfer_money(self, from_account: str, to_account: str, 
                      amount: Decimal, txn_type: TransactionType,
                      remarks: str = "") -> Tuple[bool, str]:
        """
        Money transfer with different consistency requirements based on transaction type
        """
        
        if from_account not in self.accounts:
            return False, "Source account not found"
        
        if amount <= 0:
            return False, "Invalid amount"
            
        # Create transaction record
        txn = Transaction(
            txn_id=str(uuid.uuid4()),
            txn_type=txn_type,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            timestamp=time.time(),
            remarks=remarks
        )
        
        if txn_type in [TransactionType.NEFT, TransactionType.RTGS]:
            # Strong consistency required for NEFT/RTGS
            return self._process_strong_consistency_transfer(txn)
        elif txn_type == TransactionType.UPI:
            # Eventual consistency for UPI (speed over strong consistency)
            return self._process_eventual_consistency_transfer(txn)
        elif txn_type == TransactionType.IMPS:
            # Bounded staleness for IMPS
            return self._process_bounded_staleness_transfer(txn)
        else:
            return False, "Unsupported transaction type"

    def _process_strong_consistency_transfer(self, txn: Transaction) -> Tuple[bool, str]:
        """
        Strong consistency transfer - NEFT/RTGS
        All nodes must agree before transaction completes
        """
        print(f"🔐 Processing strong consistency transfer: ₹{txn.amount}")
        print(f"   Type: {txn.txn_type.value.upper()}")
        print(f"   UTR: {txn.utr_number}")
        
        from_account = self.accounts.get(txn.from_account)
        if not from_account:
            return False, "Source account not found"
        
        # Check sufficient balance with strong consistency
        if from_account.balance < txn.amount:
            txn.status = "FAILED"
            self.transaction_log.append(txn)
            return False, "Insufficient balance"
        
        # Simulate two-phase commit for strong consistency
        # Phase 1: Prepare
        prepare_success = self._prepare_transaction(txn)
        if not prepare_success:
            txn.status = "FAILED"
            self.transaction_log.append(txn)
            return False, "Transaction preparation failed"
        
        # Phase 2: Commit
        try:
            from_account.balance -= txn.amount
            from_account.version += 1
            from_account.last_updated = time.time()
            
            # In real system, this would update destination account too
            # For simulation, we just log the transaction
            txn.status = "SUCCESS"
            self.transaction_log.append(txn)
            
            print(f"✅ NEFT/RTGS transfer successful: ₹{txn.amount}")
            print(f"   Remaining balance: ₹{from_account.balance}")
            
            return True, txn.utr_number
            
        except Exception as e:
            # Rollback on any error
            from_account.balance += txn.amount
            from_account.version -= 1
            txn.status = "FAILED"
            self.transaction_log.append(txn)
            return False, f"Transaction failed: {str(e)}"

    def _process_eventual_consistency_transfer(self, txn: Transaction) -> Tuple[bool, str]:
        """
        Eventual consistency transfer - UPI
        Fast processing, eventual consistency across nodes
        """
        print(f"⚡ Processing UPI transfer: ₹{txn.amount}")
        
        from_account = self.accounts.get(txn.from_account)
        if not from_account:
            return False, "Source account not found"
        
        # Quick balance check (might be slightly stale)
        if from_account.balance < txn.amount:
            return False, "Insufficient balance"
        
        # Process immediately for better user experience
        from_account.balance -= txn.amount
        from_account.last_updated = time.time()
        
        txn.status = "SUCCESS"
        self.transaction_log.append(txn)
        
        # Schedule background reconciliation
        self._schedule_reconciliation(txn)
        
        print(f"✅ UPI transfer completed: ₹{txn.amount}")
        print(f"   Transaction ID: {txn.txn_id}")
        
        return True, txn.txn_id

    def _process_bounded_staleness_transfer(self, txn: Transaction) -> Tuple[bool, str]:
        """
        Bounded staleness transfer - IMPS
        Balance can be up to few minutes old, but transaction is atomic
        """
        print(f"⏰ Processing IMPS transfer: ₹{txn.amount}")
        
        from_account = self.accounts.get(txn.from_account)
        if not from_account:
            return False, "Source account not found"
        
        # Check balance with bounded staleness (5 minutes)
        if time.time() - from_account.last_updated > 300:  # 5 minutes
            self._refresh_account_data(txn.from_account)
        
        if from_account.balance < txn.amount:
            return False, "Insufficient balance"
        
        # Process with optimistic locking
        old_version = from_account.version
        from_account.balance -= txn.amount
        from_account.version += 1
        from_account.last_updated = time.time()
        
        # Simulate version check failure
        if old_version != from_account.version - 1:
            # Conflict detected, rollback
            from_account.balance += txn.amount
            from_account.version = old_version
            return False, "Transaction conflict, please retry"
        
        txn.status = "SUCCESS"
        self.transaction_log.append(txn)
        
        print(f"✅ IMPS transfer successful: ₹{txn.amount}")
        return True, txn.txn_id

    def _wait_for_pending_transactions(self, account_number: str):
        """Wait for all pending transactions to complete"""
        # Simulate waiting for pending transactions
        pending_count = len([t for t in self.pending_transactions 
                           if t.from_account == account_number and t.status == "PENDING"])
        if pending_count > 0:
            print(f"⏳ Waiting for {pending_count} pending transactions to complete...")
            time.sleep(0.1 * pending_count)  # Simulate processing time

    def _refresh_account_data(self, account_number: str):
        """Refresh account data from authoritative source"""
        print(f"🔄 Refreshing account data for {account_number}")
        time.sleep(0.05)  # Simulate network latency
        if account_number in self.accounts:
            self.accounts[account_number].last_updated = time.time()

    def _get_session_balance(self, account_number: str) -> Decimal:
        """Get balance consistent within user session"""
        # In real implementation, this would maintain session-level consistency
        return self.accounts[account_number].balance

    def _prepare_transaction(self, txn: Transaction) -> bool:
        """Two-phase commit preparation phase"""
        print(f"📝 Preparing transaction {txn.txn_id}")
        # Simulate preparation time and potential failures
        time.sleep(0.1)
        return True  # Simplified - in real system might fail

    def _schedule_reconciliation(self, txn: Transaction):
        """Schedule background reconciliation for eventual consistency"""
        def reconcile():
            time.sleep(0.5)  # Simulate reconciliation delay
            print(f"🔄 Background reconciliation completed for {txn.txn_id}")
        
        thread = threading.Thread(target=reconcile)
        thread.daemon = True
        thread.start()

    def print_account_summary(self, account_number: str):
        """Print detailed account summary"""
        if account_number not in self.accounts:
            print(f"❌ Account {account_number} not found")
            return
        
        account = self.accounts[account_number]
        print(f"\n" + "="*50)
        print(f"📊 ACCOUNT SUMMARY")
        print(f"="*50)
        print(f"Account Number: {account.account_number}")
        print(f"Holder Name: {account.holder_name}")
        print(f"IFSC Code: {account.ifsc_code}")
        print(f"Bank: {account.bank_name}")
        print(f"Branch: {account.branch}")
        print(f"Current Balance: ₹{account.balance}")
        print(f"Last Updated: {time.ctime(account.last_updated)}")
        print(f"Version: {account.version}")
        print(f"Checksum: {account.checksum}")
        
        # Recent transactions
        recent_txns = [t for t in self.transaction_log 
                      if t.from_account == account_number or t.to_account == account_number][-5:]
        
        if recent_txns:
            print(f"\n📋 RECENT TRANSACTIONS (Last 5):")
            for txn in recent_txns:
                direction = "DEBIT" if txn.from_account == account_number else "CREDIT"
                print(f"  {direction}: ₹{txn.amount} | {txn.txn_type.value.upper()} | {txn.status}")

def main():
    """
    Main demonstration of banking consistency models
    """
    print("🏦 Indian Banking System - Consistency Models Demo")
    print("="*55)
    
    # Initialize banking node
    sbi_mumbai = BankingNode("SBI_MUMBAI_001", "Mumbai")
    
    # Create sample accounts
    print("\n👤 Creating sample accounts...")
    
    # Account 1: Rajesh Kumar (SBI)
    rajesh_account = sbi_mumbai.create_account(
        account_number="12345678901",
        holder_name="Rajesh Kumar",
        ifsc_code="SBIN0001234",
        initial_balance=Decimal('50000.00')
    )
    
    # Account 2: Priya Sharma (SBI)
    priya_account = sbi_mumbai.create_account(
        account_number="12345678902", 
        holder_name="Priya Sharma",
        ifsc_code="SBIN0001234",
        initial_balance=Decimal('25000.00')
    )
    
    print(f"\n💰 Initial Account Balances:")
    print(f"Rajesh: ₹{rajesh_account.balance}")
    print(f"Priya: ₹{priya_account.balance}")
    
    # Scenario 1: NEFT Transfer (Strong Consistency)
    print(f"\n🔐 SCENARIO 1: NEFT Transfer (Strong Consistency)")
    print(f"Rajesh sending ₹10,000 to Priya via NEFT")
    
    success, ref_number = sbi_mumbai.transfer_money(
        from_account="12345678901",
        to_account="12345678902",
        amount=Decimal('10000.00'),
        txn_type=TransactionType.NEFT,
        remarks="Loan repayment"
    )
    
    print(f"NEFT Result: {'SUCCESS' if success else 'FAILED'}")
    if success:
        print(f"UTR Number: {ref_number}")
    
    # Check balances with strong consistency
    success, balance = sbi_mumbai.get_balance("12345678901", ConsistencyLevel.STRONG)
    print(f"Rajesh balance (strong consistency): ₹{balance}")
    
    # Scenario 2: UPI Transfer (Eventual Consistency)
    print(f"\n⚡ SCENARIO 2: UPI Transfer (Eventual Consistency)")
    print(f"Priya sending ₹2,000 to Rajesh via UPI")
    
    success, txn_id = sbi_mumbai.transfer_money(
        from_account="12345678902",
        to_account="12345678901", 
        amount=Decimal('2000.00'),
        txn_type=TransactionType.UPI,
        remarks="Dinner split"
    )
    
    print(f"UPI Result: {'SUCCESS' if success else 'FAILED'}")
    if success:
        print(f"Transaction ID: {txn_id}")
    
    # Check balance with eventual consistency (fast)
    success, balance = sbi_mumbai.get_balance("12345678902", ConsistencyLevel.EVENTUAL)
    print(f"Priya balance (eventual consistency): ₹{balance}")
    
    # Scenario 3: ATM Balance Check (Bounded Staleness)
    print(f"\n⏰ SCENARIO 3: ATM Balance Check (Bounded Staleness)")
    
    success, balance = sbi_mumbai.get_balance("12345678901", ConsistencyLevel.BOUNDED_STALENESS)
    print(f"Rajesh ATM balance: ₹{balance}")
    
    # Scenario 4: Multiple UPI transactions (stress test)
    print(f"\n🚀 SCENARIO 4: Multiple UPI Transactions (Stress Test)")
    
    def parallel_upi_transfers():
        """Simulate multiple parallel UPI transfers"""
        amounts = [Decimal('500'), Decimal('750'), Decimal('1000')]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, amount in enumerate(amounts):
                future = executor.submit(
                    sbi_mumbai.transfer_money,
                    "12345678901",  # Rajesh sending
                    "12345678902",  # To Priya
                    amount,
                    TransactionType.UPI,
                    f"UPI transfer #{i+1}"
                )
                futures.append(future)
            
            # Wait for all transfers to complete
            results = [future.result() for future in futures]
            return results
    
    upi_results = parallel_upi_transfers()
    successful_transfers = sum(1 for success, _ in upi_results if success)
    print(f"Parallel UPI transfers completed: {successful_transfers}/3 successful")
    
    # Final account summaries
    print(f"\n📊 FINAL ACCOUNT SUMMARIES:")
    sbi_mumbai.print_account_summary("12345678901")  # Rajesh
    sbi_mumbai.print_account_summary("12345678902")  # Priya
    
    # Consistency Analysis
    print(f"\n🎯 CONSISTENCY MODEL ANALYSIS:")
    print(f"="*40)
    print(f"✅ NEFT/RTGS: Strong consistency")
    print(f"   - No double spending possible")
    print(f"   - Higher latency, guaranteed correctness")
    print(f"   - Used for: Large transfers, business payments")
    
    print(f"\n⚡ UPI: Eventual consistency")
    print(f"   - Fast user experience")  
    print(f"   - Background reconciliation")
    print(f"   - Used for: Small retail payments")
    
    print(f"\n⏰ ATM: Bounded staleness")
    print(f"   - Balance can be few minutes old")
    print(f"   - Good for: Balance inquiries")
    print(f"   - Acceptable staleness for user experience")
    
    print(f"\n💡 Key Insights:")
    print(f"1. Different banking operations need different consistency levels")
    print(f"2. Strong consistency = Lower availability during failures")  
    print(f"3. Eventual consistency = Better availability, eventual correctness")
    print(f"4. Choose consistency level based on business requirements")

if __name__ == "__main__":
    main()