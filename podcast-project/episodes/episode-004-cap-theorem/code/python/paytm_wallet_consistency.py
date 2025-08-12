#!/usr/bin/env python3
"""
Paytm Wallet Consistency System - Episode 4
Digital wallet में consistency vs availability का practical trade-off

यह system दिखाता है कि कैसे Paytm जैसे Indian digital wallets
different scenarios में CAP theorem का balance करते हैं:

- UPI payments (need availability)
- Wallet top-ups (need consistency) 
- Bill payments (balanced approach)
- Merchant settlements (strong consistency)
- P2P transfers (eventual consistency)
"""

import time
import threading
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
import json
import hashlib
import random
from concurrent.futures import ThreadPoolExecutor

# Set precision for money calculations
getcontext().prec = 10

class PaymentType(Enum):
    """Paytm payment types"""
    WALLET_TOPUP = "wallet_topup"         # Add money to wallet
    UPI_PAYMENT = "upi_payment"           # Pay using UPI
    BILL_PAYMENT = "bill_payment"         # Utility bills
    MERCHANT_PAY = "merchant_payment"     # Pay to merchants
    P2P_TRANSFER = "p2p_transfer"         # Send money to friends
    CASHBACK = "cashback"                 # Cashback credits
    REFUND = "refund"                     # Transaction refunds

class TransactionStatus(Enum):
    """Transaction lifecycle states"""
    INITIATED = "initiated"               # Transaction started
    PENDING = "pending"                   # Processing
    SUCCESS = "success"                   # Completed successfully
    FAILED = "failed"                     # Failed
    REVERSED = "reversed"                 # Reversed/refunded
    TIMEOUT = "timeout"                   # Timed out

class ConsistencyMode(Enum):
    """Different consistency requirements"""
    STRONG = "strong"                     # Bank transfers, wallet topups
    EVENTUAL = "eventual"                 # Cashbacks, P2P transfers
    CAUSAL = "causal"                     # Related transactions
    WEAK = "weak"                         # Analytics, recommendations

@dataclass
class WalletTransaction:
    """Paytm wallet transaction"""
    txn_id: str
    user_id: str
    payment_type: PaymentType
    amount: Decimal
    timestamp: datetime
    description: str
    merchant_id: Optional[str] = None
    upi_ref: Optional[str] = None
    bank_ref: Optional[str] = None
    status: TransactionStatus = TransactionStatus.INITIATED
    consistency_mode: ConsistencyMode = ConsistencyMode.EVENTUAL
    
    def __post_init__(self):
        if not self.txn_id:
            self.txn_id = f"TXN{int(time.time())}{random.randint(1000, 9999)}"

@dataclass
class PaytmWallet:
    """User wallet with balance and transaction history"""
    user_id: str
    phone_number: str
    balance: Decimal = Decimal('0.00')
    kyc_verified: bool = False
    daily_limit: Decimal = Decimal('10000.00')  # ₹10,000 for non-KYC
    monthly_limit: Decimal = Decimal('20000.00') # ₹20,000 for non-KYC
    transaction_history: List[WalletTransaction] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    version: int = 1
    lock_version: int = 0  # For optimistic locking
    
    def __post_init__(self):
        if self.kyc_verified:
            self.daily_limit = Decimal('50000.00')    # ₹50,000 for KYC users
            self.monthly_limit = Decimal('100000.00') # ₹1,00,000 for KYC users

class PaytmWalletSystem:
    """
    Paytm Wallet System with configurable consistency
    
    Different operations need different consistency levels:
    - Wallet topup: Strong consistency (money involved)
    - UPI payments: High availability (user experience)
    - Bill payments: Balanced (neither can fail often)
    - P2P transfers: Eventual consistency (social feature)
    - Cashbacks: Weak consistency (can be delayed)
    """
    
    def __init__(self, num_nodes: int = 3):
        # Multi-datacenter setup
        self.nodes = {
            "MUMBAI_PRIMARY": {"status": "active", "wallets": {}, "pending_txns": []},
            "DELHI_SECONDARY": {"status": "active", "wallets": {}, "pending_txns": []},
            "BANGALORE_DR": {"status": "active", "wallets": {}, "pending_txns": []}
        }
        
        # System configuration
        self.consistency_timeout = {
            ConsistencyMode.STRONG: 30.0,     # 30 seconds max wait
            ConsistencyMode.EVENTUAL: 1.0,    # Accept immediately
            ConsistencyMode.CAUSAL: 5.0,      # 5 seconds wait
            ConsistencyMode.WEAK: 0.1         # Almost immediate
        }
        
        # Metrics
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.consistency_violations = 0
        self.availability_issues = 0
        self.partition_recoveries = 0
        
        # Background processes
        self.replication_thread = None
        self.reconciliation_thread = None
        self.is_running = True
        
        print("💳 Paytm Wallet System initialized")
        print(f"🏢 Nodes: {list(self.nodes.keys())}")
        print("⚖️  Consistency modes: Strong, Eventual, Causal, Weak")
        
        # Initialize sample wallets
        self._initialize_sample_wallets()
        self._start_background_processes()

    def _initialize_sample_wallets(self):
        """Create sample Paytm wallets - typical Indian users"""
        sample_wallets = [
            PaytmWallet(
                user_id="user_raj_001",
                phone_number="+919876543210",
                balance=Decimal('2500.00'),
                kyc_verified=True
            ),
            PaytmWallet(
                user_id="user_priya_002", 
                phone_number="+919123456789",
                balance=Decimal('1500.00'),
                kyc_verified=False
            ),
            PaytmWallet(
                user_id="user_amit_003",
                phone_number="+919555666777",
                balance=Decimal('5000.00'),
                kyc_verified=True
            )
        ]
        
        # Replicate wallets across all nodes
        for wallet in sample_wallets:
            for node in self.nodes:
                self.nodes[node]["wallets"][wallet.user_id] = wallet
        
        print("✅ Sample wallets created and replicated")

    def _start_background_processes(self):
        """Start background replication and reconciliation"""
        self.replication_thread = threading.Thread(target=self._replication_process, daemon=True)
        self.reconciliation_thread = threading.Thread(target=self._reconciliation_process, daemon=True)
        
        self.replication_thread.start()
        self.reconciliation_thread.start()
        print("🔄 Background processes started")

    def process_transaction(self, transaction: WalletTransaction) -> Tuple[bool, str, Dict]:
        """
        Process wallet transaction with appropriate consistency level
        
        यह function transaction type के base पर decide करता है
        कि कितनी consistency चाहिए और कितनी availability
        """
        self.total_transactions += 1
        
        print(f"\n💰 Processing transaction: {transaction.txn_id}")
        print(f"   Type: {transaction.payment_type.value}")
        print(f"   Amount: ₹{transaction.amount}")
        print(f"   User: {transaction.user_id}")
        print(f"   Consistency: {transaction.consistency_mode.value}")
        
        # Choose processing strategy based on consistency requirements
        if transaction.consistency_mode == ConsistencyMode.STRONG:
            return self._process_strong_consistency(transaction)
        elif transaction.consistency_mode == ConsistencyMode.EVENTUAL:
            return self._process_eventual_consistency(transaction)
        elif transaction.consistency_mode == ConsistencyMode.CAUSAL:
            return self._process_causal_consistency(transaction)
        else:  # WEAK
            return self._process_weak_consistency(transaction)

    def _process_strong_consistency(self, transaction: WalletTransaction) -> Tuple[bool, str, Dict]:
        """
        Strong consistency processing - for critical operations like wallet topup
        
        यहाँ हम ensure करते हैं कि transaction सभी nodes में
        consistently apply हो, भले ही availability compromise हो जाए
        """
        start_time = time.time()
        timeout = self.consistency_timeout[ConsistencyMode.STRONG]
        
        # Step 1: Pre-transaction validation
        validation_result = self._validate_transaction(transaction)
        if not validation_result[0]:
            self.failed_transactions += 1
            return False, validation_result[1], {}
        
        # Step 2: Acquire locks across all nodes (2PC preparation)
        acquired_locks = []
        try:
            for node_id in self.nodes:
                if self.nodes[node_id]["status"] == "active":
                    # Simulate distributed locking
                    lock_acquired = self._acquire_node_lock(node_id, transaction.user_id, timeout=5.0)
                    if lock_acquired:
                        acquired_locks.append(node_id)
                    else:
                        # Cannot acquire all locks - rollback
                        self._release_locks(acquired_locks, transaction.user_id)
                        self.availability_issues += 1
                        return False, "Unable to acquire distributed locks", {}
            
            # Step 3: Execute transaction on all nodes
            execution_results = []
            for node_id in acquired_locks:
                result = self._execute_on_node(node_id, transaction)
                execution_results.append((node_id, result))
            
            # Step 4: Check if all nodes succeeded
            failed_nodes = [node for node, (success, _) in execution_results if not success]
            
            if failed_nodes:
                # Rollback on all nodes
                for node_id in acquired_locks:
                    self._rollback_on_node(node_id, transaction)
                self.failed_transactions += 1
                return False, f"Transaction failed on nodes: {failed_nodes}", {}
            
            # Step 5: Commit and release locks
            for node_id in acquired_locks:
                self._commit_on_node(node_id, transaction)
            
            self.successful_transactions += 1
            
            # Return wallet state
            primary_node = list(self.nodes.keys())[0]
            wallet = self.nodes[primary_node]["wallets"][transaction.user_id]
            
            result_data = {
                "transaction_id": transaction.txn_id,
                "new_balance": str(wallet.balance),
                "processing_time": f"{time.time() - start_time:.3f}s",
                "nodes_involved": len(acquired_locks),
                "consistency_level": "STRONG"
            }
            
            return True, "Transaction completed with strong consistency", result_data
        
        finally:
            self._release_locks(acquired_locks, transaction.user_id)

    def _process_eventual_consistency(self, transaction: WalletTransaction) -> Tuple[bool, str, Dict]:
        """
        Eventual consistency processing - for UPI payments and P2P transfers
        
        यहाँ हम availability को prioritize करते हैं।
        Transaction को immediately accept करते हैं और background में sync करते हैं।
        """
        start_time = time.time()
        
        # Step 1: Quick validation
        validation_result = self._validate_transaction(transaction)
        if not validation_result[0]:
            self.failed_transactions += 1
            return False, validation_result[1], {}
        
        # Step 2: Find any available node to process
        available_nodes = [node_id for node_id, data in self.nodes.items() 
                          if data["status"] == "active"]
        
        if not available_nodes:
            self.availability_issues += 1
            return False, "No nodes available", {}
        
        # Step 3: Process on first available node (fast response)
        primary_node = available_nodes[0]
        success, message = self._execute_on_node(primary_node, transaction)
        
        if not success:
            self.failed_transactions += 1
            return False, message, {}
        
        # Step 4: Async replication to other nodes (fire and forget)
        self._async_replicate_transaction(transaction, available_nodes[1:])
        
        self.successful_transactions += 1
        
        # Return immediately for better user experience
        wallet = self.nodes[primary_node]["wallets"][transaction.user_id]
        
        result_data = {
            "transaction_id": transaction.txn_id,
            "new_balance": str(wallet.balance),
            "processing_time": f"{time.time() - start_time:.3f}s",
            "primary_node": primary_node,
            "consistency_level": "EVENTUAL",
            "replication_status": "IN_PROGRESS"
        }
        
        return True, "Transaction accepted - replication in progress", result_data

    def _process_causal_consistency(self, transaction: WalletTransaction) -> Tuple[bool, str, Dict]:
        """
        Causal consistency - for bill payments where order matters
        
        यह ensure करता है कि related transactions का order maintain रहे
        """
        start_time = time.time()
        
        # Step 1: Check for causally related transactions
        related_txns = self._find_related_transactions(transaction)
        
        # Step 2: Wait for related transactions to complete
        for related_txn_id in related_txns:
            self._wait_for_transaction(related_txn_id, timeout=5.0)
        
        # Step 3: Process with moderate consistency (majority of nodes)
        available_nodes = [node_id for node_id, data in self.nodes.items() 
                          if data["status"] == "active"]
        
        if len(available_nodes) < (len(self.nodes) // 2 + 1):
            self.availability_issues += 1
            return False, "Insufficient nodes for causal consistency", {}
        
        # Step 4: Execute on majority of nodes
        majority_count = len(self.nodes) // 2 + 1
        target_nodes = available_nodes[:majority_count]
        
        successful_nodes = []
        for node_id in target_nodes:
            success, message = self._execute_on_node(node_id, transaction)
            if success:
                successful_nodes.append(node_id)
        
        if len(successful_nodes) >= majority_count:
            self.successful_transactions += 1
            
            # Async replication to remaining nodes
            remaining_nodes = [n for n in available_nodes if n not in successful_nodes]
            self._async_replicate_transaction(transaction, remaining_nodes)
            
            wallet = self.nodes[successful_nodes[0]]["wallets"][transaction.user_id]
            
            result_data = {
                "transaction_id": transaction.txn_id,
                "new_balance": str(wallet.balance),
                "processing_time": f"{time.time() - start_time:.3f}s",
                "successful_nodes": len(successful_nodes),
                "consistency_level": "CAUSAL"
            }
            
            return True, "Transaction completed with causal consistency", result_data
        else:
            self.failed_transactions += 1
            return False, "Failed to achieve required consistency level", {}

    def _process_weak_consistency(self, transaction: WalletTransaction) -> Tuple[bool, str, Dict]:
        """
        Weak consistency - for cashbacks and non-critical operations
        
        बस कहीं भी store कर दो, बाकी background में sync हो जाएगा
        """
        start_time = time.time()
        
        # Find any available node
        available_nodes = [node_id for node_id, data in self.nodes.items() 
                          if data["status"] == "active"]
        
        if not available_nodes:
            # Even if no nodes available, accept the request (queue it)
            self.nodes[list(self.nodes.keys())[0]]["pending_txns"].append(transaction)
            self.successful_transactions += 1
            
            return True, "Transaction queued for processing", {
                "transaction_id": transaction.txn_id,
                "status": "QUEUED",
                "consistency_level": "WEAK"
            }
        
        # Process on any node
        node_id = random.choice(available_nodes)
        success, message = self._execute_on_node(node_id, transaction)
        
        # Always return success for weak consistency (best effort)
        self.successful_transactions += 1
        
        if success:
            wallet = self.nodes[node_id]["wallets"][transaction.user_id]
            new_balance = str(wallet.balance)
        else:
            new_balance = "UNKNOWN"
        
        result_data = {
            "transaction_id": transaction.txn_id,
            "new_balance": new_balance,
            "processing_time": f"{time.time() - start_time:.3f}s",
            "processed_on": node_id,
            "consistency_level": "WEAK"
        }
        
        return True, "Transaction accepted with weak consistency", result_data

    def _validate_transaction(self, transaction: WalletTransaction) -> Tuple[bool, str]:
        """Validate transaction before processing"""
        # Check user exists
        primary_node = list(self.nodes.keys())[0]
        if transaction.user_id not in self.nodes[primary_node]["wallets"]:
            return False, "User wallet not found"
        
        wallet = self.nodes[primary_node]["wallets"][transaction.user_id]
        
        # Check balance for debit transactions
        if transaction.payment_type in [PaymentType.UPI_PAYMENT, PaymentType.BILL_PAYMENT, 
                                       PaymentType.MERCHANT_PAY, PaymentType.P2P_TRANSFER]:
            if wallet.balance < transaction.amount:
                return False, "Insufficient balance"
        
        # Check daily limits
        today_amount = self._calculate_daily_spent(wallet)
        if today_amount + transaction.amount > wallet.daily_limit:
            return False, f"Daily limit exceeded. Limit: ₹{wallet.daily_limit}"
        
        # Check minimum transaction amount
        if transaction.amount < Decimal('1.00'):
            return False, "Minimum transaction amount is ₹1"
        
        return True, "Validation successful"

    def _calculate_daily_spent(self, wallet: PaytmWallet) -> Decimal:
        """Calculate today's total spent amount"""
        today = datetime.now().date()
        daily_spent = Decimal('0')
        
        for txn in wallet.transaction_history:
            if (txn.timestamp.date() == today and
                txn.payment_type in [PaymentType.UPI_PAYMENT, PaymentType.BILL_PAYMENT,
                                   PaymentType.MERCHANT_PAY, PaymentType.P2P_TRANSFER] and
                txn.status == TransactionStatus.SUCCESS):
                daily_spent += txn.amount
        
        return daily_spent

    def _acquire_node_lock(self, node_id: str, user_id: str, timeout: float) -> bool:
        """Simulate distributed lock acquisition"""
        # Simplified lock simulation
        time.sleep(random.uniform(0.01, 0.05))  # Network delay
        return random.random() > 0.05  # 95% success rate

    def _release_locks(self, node_ids: List[str], user_id: str):
        """Release locks on specified nodes"""
        pass  # Simplified implementation

    def _execute_on_node(self, node_id: str, transaction: WalletTransaction) -> Tuple[bool, str]:
        """Execute transaction on specific node"""
        try:
            node_data = self.nodes[node_id]
            wallet = node_data["wallets"][transaction.user_id]
            
            # Update balance based on transaction type
            if transaction.payment_type in [PaymentType.WALLET_TOPUP, PaymentType.CASHBACK, PaymentType.REFUND]:
                wallet.balance += transaction.amount
            else:
                wallet.balance -= transaction.amount
            
            # Update transaction history
            transaction.status = TransactionStatus.SUCCESS
            wallet.transaction_history.append(transaction)
            wallet.last_updated = datetime.now()
            wallet.version += 1
            
            return True, "Transaction executed successfully"
            
        except Exception as e:
            return False, f"Execution failed: {e}"

    def _rollback_on_node(self, node_id: str, transaction: WalletTransaction):
        """Rollback transaction on specific node"""
        try:
            node_data = self.nodes[node_id]
            wallet = node_data["wallets"][transaction.user_id]
            
            # Reverse the balance change
            if transaction.payment_type in [PaymentType.WALLET_TOPUP, PaymentType.CASHBACK, PaymentType.REFUND]:
                wallet.balance -= transaction.amount
            else:
                wallet.balance += transaction.amount
            
            # Remove from history
            wallet.transaction_history = [t for t in wallet.transaction_history 
                                         if t.txn_id != transaction.txn_id]
            transaction.status = TransactionStatus.REVERSED
            
        except Exception as e:
            print(f"Rollback failed on node {node_id}: {e}")

    def _commit_on_node(self, node_id: str, transaction: WalletTransaction):
        """Commit transaction on specific node"""
        # Transaction already executed, just mark as committed
        pass

    def _async_replicate_transaction(self, transaction: WalletTransaction, target_nodes: List[str]):
        """Asynchronously replicate transaction to target nodes"""
        def replicate():
            time.sleep(random.uniform(0.1, 0.5))  # Simulate network delay
            
            for node_id in target_nodes:
                if node_id in self.nodes and self.nodes[node_id]["status"] == "active":
                    try:
                        self._execute_on_node(node_id, transaction)
                    except:
                        pass  # Silent failure for async replication
        
        thread = threading.Thread(target=replicate, daemon=True)
        thread.start()

    def _find_related_transactions(self, transaction: WalletTransaction) -> List[str]:
        """Find causally related transactions"""
        # Simplified: return empty list
        return []

    def _wait_for_transaction(self, txn_id: str, timeout: float):
        """Wait for specific transaction to complete"""
        # Simplified implementation
        time.sleep(random.uniform(0.1, timeout))

    def wallet_topup(self, user_id: str, amount: Decimal, payment_method: str = "UPI") -> Tuple[bool, str, Dict]:
        """
        Top up wallet - requires strong consistency
        
        Wallet में paisa add करना critical operation है,
        इसमें strong consistency जरूरी है
        """
        transaction = WalletTransaction(
            txn_id=f"TOPUP_{int(time.time())}_{random.randint(100, 999)}",
            user_id=user_id,
            payment_type=PaymentType.WALLET_TOPUP,
            amount=amount,
            timestamp=datetime.now(),
            description=f"Wallet topup via {payment_method}",
            consistency_mode=ConsistencyMode.STRONG
        )
        
        return self.process_transaction(transaction)

    def upi_payment(self, user_id: str, amount: Decimal, merchant_id: str) -> Tuple[bool, str, Dict]:
        """
        UPI payment - prioritizes availability
        
        UPI payment में user experience important है,
        payment fail नहीं होना चाहिए
        """
        transaction = WalletTransaction(
            txn_id=f"UPI_{int(time.time())}_{random.randint(100, 999)}",
            user_id=user_id,
            payment_type=PaymentType.UPI_PAYMENT,
            amount=amount,
            timestamp=datetime.now(),
            description=f"UPI payment to {merchant_id}",
            merchant_id=merchant_id,
            consistency_mode=ConsistencyMode.EVENTUAL
        )
        
        return self.process_transaction(transaction)

    def bill_payment(self, user_id: str, amount: Decimal, bill_type: str) -> Tuple[bool, str, Dict]:
        """
        Bill payment - balanced consistency approach
        
        Bill payment में neither high consistency nor high availability,
        balanced approach चाहिए
        """
        transaction = WalletTransaction(
            txn_id=f"BILL_{int(time.time())}_{random.randint(100, 999)}",
            user_id=user_id,
            payment_type=PaymentType.BILL_PAYMENT,
            amount=amount,
            timestamp=datetime.now(),
            description=f"{bill_type} bill payment",
            consistency_mode=ConsistencyMode.CAUSAL
        )
        
        return self.process_transaction(transaction)

    def add_cashback(self, user_id: str, amount: Decimal, source: str) -> Tuple[bool, str, Dict]:
        """
        Add cashback - weak consistency is fine
        
        Cashback delay हो जाए तो problem नहीं,
        eventually मिल जाएगा
        """
        transaction = WalletTransaction(
            txn_id=f"CASHBACK_{int(time.time())}_{random.randint(100, 999)}",
            user_id=user_id,
            payment_type=PaymentType.CASHBACK,
            amount=amount,
            timestamp=datetime.now(),
            description=f"Cashback from {source}",
            consistency_mode=ConsistencyMode.WEAK
        )
        
        return self.process_transaction(transaction)

    def get_wallet_balance(self, user_id: str) -> Tuple[bool, Dict]:
        """Get wallet balance with consistency check"""
        balances = {}
        
        # Check balance across all nodes
        for node_id, node_data in self.nodes.items():
            if node_data["status"] == "active" and user_id in node_data["wallets"]:
                wallet = node_data["wallets"][user_id]
                balances[node_id] = {
                    "balance": str(wallet.balance),
                    "last_updated": wallet.last_updated.isoformat(),
                    "version": wallet.version
                }
        
        if not balances:
            return False, {"error": "Wallet not found"}
        
        # Check for consistency
        all_balances = [Decimal(data["balance"]) for data in balances.values()]
        is_consistent = all(b == all_balances[0] for b in all_balances)
        
        primary_wallet = list(balances.values())[0]
        
        result = {
            "user_id": user_id,
            "balance": primary_wallet["balance"],
            "is_consistent": is_consistent,
            "node_balances": balances,
            "consistency_check": "PASSED" if is_consistent else "FAILED"
        }
        
        if not is_consistent:
            self.consistency_violations += 1
        
        return True, result

    def _replication_process(self):
        """Background replication process"""
        while self.is_running:
            try:
                # Process pending transactions
                for node_id, node_data in self.nodes.items():
                    pending_txns = node_data["pending_txns"]
                    if pending_txns:
                        # Process first pending transaction
                        transaction = pending_txns.pop(0)
                        self._execute_on_node(node_id, transaction)
                
                time.sleep(1)  # Replication interval
                
            except Exception as e:
                print(f"Replication error: {e}")
                time.sleep(5)

    def _reconciliation_process(self):
        """Background reconciliation process"""
        while self.is_running:
            try:
                # Check for inconsistencies and resolve them
                for user_id in self._get_all_user_ids():
                    success, balance_data = self.get_wallet_balance(user_id)
                    if success and not balance_data["is_consistent"]:
                        self._reconcile_user_wallet(user_id, balance_data)
                
                time.sleep(30)  # Reconciliation interval
                
            except Exception as e:
                print(f"Reconciliation error: {e}")
                time.sleep(10)

    def _get_all_user_ids(self) -> set:
        """Get all user IDs from all nodes"""
        all_users = set()
        for node_data in self.nodes.values():
            if node_data["status"] == "active":
                all_users.update(node_data["wallets"].keys())
        return all_users

    def _reconcile_user_wallet(self, user_id: str, balance_data: Dict):
        """Reconcile inconsistent wallet across nodes"""
        print(f"🔄 Reconciling wallet for user {user_id}")
        
        # Use the wallet with highest version as source of truth
        source_node = None
        highest_version = -1
        
        for node_id, node_balance in balance_data["node_balances"].items():
            if node_balance["version"] > highest_version:
                highest_version = node_balance["version"]
                source_node = node_id
        
        if source_node:
            source_wallet = self.nodes[source_node]["wallets"][user_id]
            
            # Update other nodes
            for node_id in self.nodes:
                if node_id != source_node and self.nodes[node_id]["status"] == "active":
                    if user_id in self.nodes[node_id]["wallets"]:
                        self.nodes[node_id]["wallets"][user_id] = source_wallet
            
            self.partition_recoveries += 1
            print(f"✅ Wallet reconciled using node {source_node} as source")

    def simulate_partition_recovery(self, failed_node: str, duration: int = 10):
        """Simulate network partition and recovery"""
        print(f"\n🌪️  PARTITION SIMULATION: {failed_node} going offline for {duration}s")
        
        if failed_node not in self.nodes:
            print(f"❌ Node {failed_node} not found")
            return
        
        # Mark node as failed
        original_status = self.nodes[failed_node]["status"]
        self.nodes[failed_node]["status"] = "failed"
        
        print(f"🔴 Node {failed_node} marked as failed")
        
        # Test transactions during partition
        print("Testing transaction processing during partition...")
        
        test_results = []
        for i in range(3):
            success, message, result = self.upi_payment(
                user_id="user_raj_001",
                amount=Decimal('100'),
                merchant_id=f"merchant_{i}"
            )
            test_results.append(success)
            time.sleep(1)
        
        successful_during_partition = sum(test_results)
        print(f"Transactions successful during partition: {successful_during_partition}/3")
        
        # Simulate recovery
        time.sleep(duration)
        
        print(f"🔄 Node {failed_node} recovering...")
        self.nodes[failed_node]["status"] = "recovering"
        time.sleep(2)
        
        self.nodes[failed_node]["status"] = original_status
        print(f"✅ Node {failed_node} fully recovered")

    def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        active_nodes = sum(1 for data in self.nodes.values() 
                          if data["status"] == "active")
        
        success_rate = 0
        if self.total_transactions > 0:
            success_rate = (self.successful_transactions / self.total_transactions) * 100
        
        return {
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "success_rate": f"{success_rate:.2f}%",
            "active_nodes": f"{active_nodes}/{len(self.nodes)}",
            "consistency_violations": self.consistency_violations,
            "availability_issues": self.availability_issues,
            "partition_recoveries": self.partition_recoveries
        }

def main():
    """
    Main demonstration - Paytm wallet consistency scenarios
    """
    print("💳 Paytm Wallet Consistency System Demo")
    print("=" * 50)
    
    # Initialize Paytm system
    paytm = PaytmWalletSystem()
    
    # Scenario 1: Wallet topup (Strong consistency)
    print("\n💰 SCENARIO 1: Wallet Topup (Strong Consistency)")
    success, message, result = paytm.wallet_topup("user_raj_001", Decimal('1000'))
    print(f"Topup result: {message}")
    if success:
        print(f"New balance: ₹{result['new_balance']}")
        print(f"Processing time: {result['processing_time']}")
    
    # Scenario 2: UPI payment (High availability)
    print("\n📱 SCENARIO 2: UPI Payment (High Availability)")
    success, message, result = paytm.upi_payment("user_raj_001", Decimal('250'), "swiggy_merchant")
    print(f"UPI payment result: {message}")
    if success:
        print(f"New balance: ₹{result['new_balance']}")
    
    # Scenario 3: Bill payment (Balanced approach)
    print("\n🧾 SCENARIO 3: Bill Payment (Causal Consistency)")
    success, message, result = paytm.bill_payment("user_priya_002", Decimal('150'), "Electricity")
    print(f"Bill payment result: {message}")
    
    # Scenario 4: Cashback (Weak consistency)
    print("\n🎁 SCENARIO 4: Cashback Addition (Weak Consistency)")
    success, message, result = paytm.add_cashback("user_amit_003", Decimal('50'), "Diwali Offer")
    print(f"Cashback result: {message}")
    
    # Scenario 5: Balance consistency check
    print("\n💵 SCENARIO 5: Balance Consistency Check")
    success, balance_data = paytm.get_wallet_balance("user_raj_001")
    if success:
        print(f"Current balance: ₹{balance_data['balance']}")
        print(f"Consistency status: {balance_data['consistency_check']}")
    
    # Scenario 6: Partition recovery simulation
    print("\n🌪️  SCENARIO 6: Partition Recovery Simulation")
    paytm.simulate_partition_recovery("MUMBAI_PRIMARY", duration=5)
    
    # Scenario 7: System metrics
    print("\n📊 SCENARIO 7: System Health Metrics")
    metrics = paytm.get_system_metrics()
    print("System Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Paytm wallet consistency demo completed!")
    print("Key learnings:")
    print("1. Different operations need different consistency levels")
    print("2. Strong consistency for money operations (topup)")
    print("3. High availability for user experience (UPI)")
    print("4. Balanced approach for bill payments")
    print("5. Weak consistency acceptable for non-critical features")
    print("6. Background reconciliation handles eventual consistency")

if __name__ == "__main__":
    main()