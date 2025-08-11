#!/usr/bin/env python3
"""
Multi-Version Concurrency Control (MVCC) System - Episode 4
व्यावहारिक MVCC का production-ready implementation

MVCC allows multiple versions of data को maintain करता है,
जिससे readers और writers block नहीं करते एक-दूसरे को।

Indian Context Examples:
- Paytm transaction history with snapshot isolation
- Flipkart order processing with concurrent reads/writes
- IRCTC seat booking with versioned availability
- WhatsApp message threads with edit history

MVCC Benefits:
1. Readers never block writers
2. Writers never block readers  
3. Snapshot isolation
4. Historical data access
5. No lock contention

MVCC Components:
- Version Timestamps
- Visibility Rules
- Garbage Collection
- Snapshot Management
"""

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict
import bisect

class TransactionStatus(Enum):
    """Transaction states in MVCC"""
    ACTIVE = "active"
    COMMITTED = "committed"
    ABORTED = "aborted"

@dataclass
class DataVersion:
    """Represents a single version of a data item"""
    key: str
    value: Any
    version_id: int
    created_by_txn: str
    created_timestamp: float
    deleted_by_txn: Optional[str] = None
    deleted_timestamp: Optional[float] = None
    is_deleted: bool = False

@dataclass
class Transaction:
    """MVCC Transaction"""
    txn_id: str
    start_timestamp: float
    commit_timestamp: Optional[float] = None
    status: TransactionStatus = TransactionStatus.ACTIVE
    read_set: set = field(default_factory=set)  # Keys read by this transaction
    write_set: set = field(default_factory=set)  # Keys written by this transaction
    session_id: str = ""
    user_context: str = ""  # Business context like "paytm_payment" or "flipkart_order"

@dataclass
class ReadResult:
    """Result of a read operation"""
    key: str
    value: Any
    version_id: int
    timestamp: float
    found: bool

@dataclass
class MVCCStats:
    """MVCC System statistics"""
    total_transactions: int = 0
    committed_transactions: int = 0
    aborted_transactions: int = 0
    total_reads: int = 0
    total_writes: int = 0
    version_count: int = 0
    gc_runs: int = 0
    avg_transaction_time: float = 0.0

class MVCCSystem:
    """
    Multi-Version Concurrency Control System
    
    Production use cases:
    - Database snapshot isolation
    - Version control systems
    - Collaborative editing
    - Financial transaction processing
    """
    
    def __init__(self, gc_threshold: int = 1000):
        # Version storage: key -> list of DataVersions sorted by version_id
        self.versions: Dict[str, List[DataVersion]] = defaultdict(list)
        
        # Transaction management
        self.active_transactions: Dict[str, Transaction] = {}
        self.completed_transactions: Dict[str, Transaction] = {}
        
        # Global timestamp counter (logical clock)
        self.timestamp_counter = 0
        self.timestamp_lock = threading.Lock()
        
        # Version ID counter
        self.version_counter = 0
        self.version_lock = threading.Lock()
        
        # Garbage collection
        self.gc_threshold = gc_threshold  # Run GC after this many versions
        self.min_active_timestamp = 0.0
        
        # Statistics
        self.stats = MVCCStats()
        
        # Thread safety
        self.global_lock = threading.RLock()
        
        print("🕰️ MVCC System initialized")
        print(f"📊 GC threshold: {gc_threshold} versions")
    
    def begin_transaction(self, user_context: str = "unknown", session_id: str = "") -> Transaction:
        """
        Start a new transaction with snapshot timestamp
        
        Example: Paytm payment transaction starting
        """
        with self.timestamp_lock:
            self.timestamp_counter += 1
            start_timestamp = self.timestamp_counter
        
        txn_id = str(uuid.uuid4())
        
        transaction = Transaction(
            txn_id=txn_id,
            start_timestamp=start_timestamp,
            user_context=user_context,
            session_id=session_id
        )
        
        with self.global_lock:
            self.active_transactions[txn_id] = transaction
            self.stats.total_transactions += 1
        
        print(f"🚀 Transaction {txn_id[:8]} started at timestamp {start_timestamp} ({user_context})")
        return transaction
    
    def read(self, txn: Transaction, key: str) -> ReadResult:
        """
        Read data with snapshot isolation
        
        Returns the latest version visible to this transaction
        """
        if txn.status != TransactionStatus.ACTIVE:
            raise Exception(f"Transaction {txn.txn_id} is not active")
        
        with self.global_lock:
            txn.read_set.add(key)
            self.stats.total_reads += 1
            
            # Find the latest version visible to this transaction
            visible_version = self._find_visible_version(key, txn.start_timestamp)
            
            if visible_version is None:
                print(f"📖 Transaction {txn.txn_id[:8]}: READ {key} = NULL (not found)")
                return ReadResult(key, None, -1, 0, False)
            
            print(f"📖 Transaction {txn.txn_id[:8]}: READ {key} = {visible_version.value} (v{visible_version.version_id})")
            return ReadResult(
                key=key,
                value=visible_version.value,
                version_id=visible_version.version_id,
                timestamp=visible_version.created_timestamp,
                found=True
            )
    
    def write(self, txn: Transaction, key: str, value: Any) -> bool:
        """
        Write data with versioning
        
        Creates a new version of the data item
        """
        if txn.status != TransactionStatus.ACTIVE:
            raise Exception(f"Transaction {txn.txn_id} is not active")
        
        with self.version_lock:
            self.version_counter += 1
            version_id = self.version_counter
        
        with self.global_lock:
            txn.write_set.add(key)
            self.stats.total_writes += 1
            
            # Create new version
            new_version = DataVersion(
                key=key,
                value=value,
                version_id=version_id,
                created_by_txn=txn.txn_id,
                created_timestamp=txn.start_timestamp
            )
            
            # Add to version list (maintain sorted order by version_id)
            version_list = self.versions[key]
            bisect.insort(version_list, new_version, key=lambda v: v.version_id)
            
            self.stats.version_count += 1
            
            print(f"✍️ Transaction {txn.txn_id[:8]}: WRITE {key} = {value} (v{version_id})")
            
            # Check if GC is needed
            if self.stats.version_count > self.gc_threshold:
                self._schedule_garbage_collection()
            
            return True
    
    def commit(self, txn: Transaction) -> bool:
        """
        Commit transaction with validation
        
        Validates no write-write conflicts occurred
        """
        if txn.status != TransactionStatus.ACTIVE:
            raise Exception(f"Transaction {txn.txn_id} is not active")
        
        start_time = time.time()
        
        with self.timestamp_lock:
            self.timestamp_counter += 1
            commit_timestamp = self.timestamp_counter
        
        with self.global_lock:
            # Validation phase - check for write-write conflicts
            if not self._validate_transaction(txn, commit_timestamp):
                return self.abort(txn)
            
            # Commit phase - make writes visible
            txn.commit_timestamp = commit_timestamp
            txn.status = TransactionStatus.COMMITTED
            
            # Update version timestamps to commit timestamp
            for key in txn.write_set:
                for version in self.versions[key]:
                    if version.created_by_txn == txn.txn_id:
                        version.created_timestamp = commit_timestamp
                        break
            
            # Move from active to completed
            del self.active_transactions[txn.txn_id]
            self.completed_transactions[txn.txn_id] = txn
            
            self.stats.committed_transactions += 1
            transaction_time = time.time() - start_time
            self._update_avg_transaction_time(transaction_time)
            
            print(f"✅ Transaction {txn.txn_id[:8]} COMMITTED at timestamp {commit_timestamp}")
            return True
    
    def abort(self, txn: Transaction) -> bool:
        """
        Abort transaction and cleanup its versions
        """
        if txn.status != TransactionStatus.ACTIVE:
            return True  # Already aborted/committed
        
        with self.global_lock:
            txn.status = TransactionStatus.ABORTED
            
            # Remove versions created by this transaction
            for key in txn.write_set:
                version_list = self.versions[key]
                self.versions[key] = [v for v in version_list if v.created_by_txn != txn.txn_id]
                
            # Move from active to completed
            del self.active_transactions[txn.txn_id]
            self.completed_transactions[txn.txn_id] = txn
            
            self.stats.aborted_transactions += 1
            
            print(f"❌ Transaction {txn.txn_id[:8]} ABORTED")
            return True
    
    def _find_visible_version(self, key: str, snapshot_timestamp: float) -> Optional[DataVersion]:
        """
        Find the latest version of key visible at snapshot_timestamp
        """
        version_list = self.versions.get(key, [])
        if not version_list:
            return None
        
        # Find latest version with created_timestamp <= snapshot_timestamp
        # and not deleted before snapshot_timestamp
        visible_version = None
        
        for version in reversed(version_list):  # Start from latest
            # Version must be created before or at snapshot time
            if version.created_timestamp > snapshot_timestamp:
                continue
                
            # Version must not be deleted before snapshot time
            if (version.is_deleted and 
                version.deleted_timestamp and 
                version.deleted_timestamp <= snapshot_timestamp):
                continue
            
            visible_version = version
            break
        
        return visible_version
    
    def _validate_transaction(self, txn: Transaction, commit_timestamp: float) -> bool:
        """
        Validate transaction for write-write conflicts
        
        Check if any key written by this transaction was also written
        by another transaction that committed after our start time
        """
        for key in txn.write_set:
            # Check if there are any committed writes to this key
            # after our start timestamp
            for version in self.versions[key]:
                if (version.created_by_txn != txn.txn_id and
                    version.created_timestamp > txn.start_timestamp):
                    
                    # Check if the other transaction committed
                    other_txn = self.completed_transactions.get(version.created_by_txn)
                    if other_txn and other_txn.status == TransactionStatus.COMMITTED:
                        print(f"💥 Write-write conflict detected for key {key}")
                        return False
        
        return True
    
    def _schedule_garbage_collection(self):
        """
        Schedule garbage collection to remove old versions
        """
        # Run GC in background thread to avoid blocking
        gc_thread = threading.Thread(target=self._garbage_collect)
        gc_thread.daemon = True
        gc_thread.start()
    
    def _garbage_collect(self):
        """
        Garbage collect old versions that are no longer visible
        """
        with self.global_lock:
            # Calculate minimum active timestamp
            min_timestamp = float('inf')
            
            for txn in self.active_transactions.values():
                min_timestamp = min(min_timestamp, txn.start_timestamp)
            
            if min_timestamp == float('inf'):
                min_timestamp = self.timestamp_counter
            
            # Remove versions older than min active timestamp
            versions_removed = 0
            
            for key, version_list in self.versions.items():
                # Keep versions that might still be visible
                new_version_list = []
                
                for version in version_list:
                    # Keep version if:
                    # 1. It might be visible to active transactions
                    # 2. It's the only version for this key
                    if (version.created_timestamp >= min_timestamp or 
                        len(version_list) == 1):
                        new_version_list.append(version)
                    else:
                        versions_removed += 1
                
                self.versions[key] = new_version_list
            
            self.stats.version_count -= versions_removed
            self.stats.gc_runs += 1
            
            if versions_removed > 0:
                print(f"🧹 Garbage collection: Removed {versions_removed} old versions")
    
    def _update_avg_transaction_time(self, transaction_time: float):
        """Update rolling average of transaction time"""
        if self.stats.avg_transaction_time == 0:
            self.stats.avg_transaction_time = transaction_time
        else:
            # Simple exponential moving average
            alpha = 0.1
            self.stats.avg_transaction_time = (
                alpha * transaction_time + 
                (1 - alpha) * self.stats.avg_transaction_time
            )
    
    def get_version_history(self, key: str) -> List[DataVersion]:
        """
        Get complete version history for a key
        
        Useful for auditing and debugging
        """
        with self.global_lock:
            return list(self.versions.get(key, []))
    
    def print_statistics(self):
        """Print comprehensive MVCC statistics"""
        stats = self.stats
        
        print(f"\n📊 MVCC SYSTEM STATISTICS")
        print("=" * 40)
        print(f"Total transactions: {stats.total_transactions}")
        print(f"Committed: {stats.committed_transactions}")
        print(f"Aborted: {stats.aborted_transactions}")
        print(f"Success rate: {(stats.committed_transactions/max(stats.total_transactions,1)*100):.1f}%")
        print(f"Total reads: {stats.total_reads}")
        print(f"Total writes: {stats.total_writes}")
        print(f"Current versions: {stats.version_count}")
        print(f"GC runs: {stats.gc_runs}")
        print(f"Avg transaction time: {stats.avg_transaction_time*1000:.1f}ms")
        
        # Active transactions
        with self.global_lock:
            active_count = len(self.active_transactions)
            completed_count = len(self.completed_transactions)
        
        print(f"Active transactions: {active_count}")
        print(f"Completed transactions: {completed_count}")
    
    def print_version_info(self, key: str):
        """Print version information for a specific key"""
        versions = self.get_version_history(key)
        
        print(f"\n📋 VERSION HISTORY FOR '{key}'")
        print("-" * 40)
        
        if not versions:
            print("No versions found")
            return
        
        for version in versions:
            status = "DELETED" if version.is_deleted else "ACTIVE"
            print(f"v{version.version_id}: {version.value} "
                  f"(txn: {version.created_by_txn[:8]}, "
                  f"ts: {version.created_timestamp}, "
                  f"status: {status})")

def paytm_wallet_mvcc_demo():
    """
    Demonstrate MVCC with Paytm wallet transactions
    """
    print("💰 DEMO: Paytm Wallet with MVCC")
    print("-" * 35)
    
    mvcc = MVCCSystem(gc_threshold=50)
    
    # Initialize wallet balance
    init_txn = mvcc.begin_transaction("wallet_initialization")
    mvcc.write(init_txn, "user_rajesh_balance", 10000)
    mvcc.commit(init_txn)
    
    print(f"\n💳 Initial wallet balance set to ₹10,000")
    
    # Concurrent transactions
    def payment_transaction():
        """Payment of ₹2000"""
        txn = mvcc.begin_transaction("paytm_payment", "user_session_1")
        try:
            # Read current balance
            result = mvcc.read(txn, "user_rajesh_balance")
            if result.found and result.value >= 2000:
                new_balance = result.value - 2000
                mvcc.write(txn, "user_rajesh_balance", new_balance)
                mvcc.write(txn, "last_transaction", f"payment_2000_at_{time.time()}")
                success = mvcc.commit(txn)
                
                if success:
                    print(f"💸 Payment successful: ₹2000 deducted")
                else:
                    print(f"❌ Payment failed: Transaction aborted")
            else:
                print(f"❌ Payment failed: Insufficient balance")
                mvcc.abort(txn)
        except Exception as e:
            print(f"❌ Payment error: {e}")
            mvcc.abort(txn)
    
    def cashback_transaction():
        """Cashback of ₹500"""
        txn = mvcc.begin_transaction("paytm_cashback", "system_session")
        try:
            result = mvcc.read(txn, "user_rajesh_balance")
            if result.found:
                new_balance = result.value + 500
                mvcc.write(txn, "user_rajesh_balance", new_balance)
                mvcc.write(txn, "last_transaction", f"cashback_500_at_{time.time()}")
                success = mvcc.commit(txn)
                
                if success:
                    print(f"💰 Cashback successful: ₹500 added")
                else:
                    print(f"❌ Cashback failed: Transaction aborted")
            else:
                print(f"❌ Cashback failed: Account not found")
                mvcc.abort(txn)
        except Exception as e:
            print(f"❌ Cashback error: {e}")
            mvcc.abort(txn)
    
    def balance_inquiry():
        """Balance inquiry"""
        txn = mvcc.begin_transaction("balance_inquiry", "user_session_2")
        try:
            result = mvcc.read(txn, "user_rajesh_balance")
            if result.found:
                print(f"💳 Current balance: ₹{result.value}")
            else:
                print(f"💳 Balance: Account not found")
            mvcc.commit(txn)
        except Exception as e:
            print(f"❌ Balance inquiry error: {e}")
            mvcc.abort(txn)
    
    # Run concurrent transactions
    threads = []
    
    # Payment transaction
    payment_thread = threading.Thread(target=payment_transaction)
    threads.append(payment_thread)
    
    # Cashback transaction
    cashback_thread = threading.Thread(target=cashback_transaction)  
    threads.append(cashback_thread)
    
    # Multiple balance inquiries
    for i in range(3):
        inquiry_thread = threading.Thread(target=balance_inquiry)
        threads.append(inquiry_thread)
    
    # Start all transactions
    print(f"\n🔄 Running concurrent transactions...")
    for thread in threads:
        thread.start()
        time.sleep(0.1)  # Small stagger
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    time.sleep(0.5)  # Let everything settle
    
    # Final balance check
    final_txn = mvcc.begin_transaction("final_balance_check")
    result = mvcc.read(final_txn, "user_rajesh_balance")
    mvcc.commit(final_txn)
    
    print(f"\n💰 Final balance: ₹{result.value if result.found else 'UNKNOWN'}")
    
    # Show version history
    mvcc.print_version_info("user_rajesh_balance")
    mvcc.print_statistics()

def flipkart_order_mvcc_demo():
    """
    Demonstrate MVCC with Flipkart order processing
    """
    print("\n🛒 DEMO: Flipkart Order Processing with MVCC")
    print("-" * 45)
    
    mvcc = MVCCSystem(gc_threshold=30)
    
    # Initialize product inventory
    init_txn = mvcc.begin_transaction("inventory_init")
    mvcc.write(init_txn, "iphone14_stock", 50)
    mvcc.write(init_txn, "iphone14_price", 79999)
    mvcc.commit(init_txn)
    
    print(f"📦 Initial inventory: iPhone 14 stock = 50, price = ₹79,999")
    
    def place_order(order_id: str, customer: str, quantity: int = 1):
        """Place an order for iPhone"""
        txn = mvcc.begin_transaction(f"order_{order_id}", f"customer_{customer}")
        try:
            # Read current stock and price
            stock_result = mvcc.read(txn, "iphone14_stock")
            price_result = mvcc.read(txn, "iphone14_price")
            
            if stock_result.found and stock_result.value >= quantity:
                # Reserve inventory
                new_stock = stock_result.value - quantity
                mvcc.write(txn, "iphone14_stock", new_stock)
                
                # Create order record
                order_value = {
                    "customer": customer,
                    "quantity": quantity,
                    "total_price": price_result.value * quantity,
                    "timestamp": time.time()
                }
                mvcc.write(txn, f"order_{order_id}", order_value)
                
                success = mvcc.commit(txn)
                if success:
                    print(f"✅ Order {order_id} placed by {customer}: {quantity} iPhone(s)")
                else:
                    print(f"❌ Order {order_id} failed: Commit failed")
            else:
                print(f"❌ Order {order_id} failed: Insufficient stock ({stock_result.value} available)")
                mvcc.abort(txn)
        except Exception as e:
            print(f"❌ Order {order_id} error: {e}")
            mvcc.abort(txn)
    
    def update_price(new_price: int):
        """Update product price"""
        txn = mvcc.begin_transaction("price_update", "admin_session")
        try:
            mvcc.write(txn, "iphone14_price", new_price)
            success = mvcc.commit(txn)
            if success:
                print(f"💰 Price updated to ₹{new_price}")
            else:
                print(f"❌ Price update failed")
        except Exception as e:
            print(f"❌ Price update error: {e}")
            mvcc.abort(txn)
    
    def check_inventory():
        """Check current inventory"""
        txn = mvcc.begin_transaction("inventory_check")
        try:
            stock_result = mvcc.read(txn, "iphone14_stock") 
            price_result = mvcc.read(txn, "iphone14_price")
            mvcc.commit(txn)
            
            print(f"📊 Current inventory: Stock = {stock_result.value}, Price = ₹{price_result.value}")
        except Exception as e:
            print(f"❌ Inventory check error: {e}")
            mvcc.abort(txn)
    
    # Simulate concurrent operations
    threads = []
    
    # Customer orders
    customers = ["rajesh", "priya", "amit", "sneha", "vikram"]
    for i, customer in enumerate(customers):
        order_thread = threading.Thread(target=place_order, args=(f"ORD00{i+1}", customer, 1))
        threads.append(order_thread)
    
    # Price update
    price_thread = threading.Thread(target=update_price, args=(75999,))
    threads.append(price_thread)
    
    # Inventory checks
    for i in range(3):
        check_thread = threading.Thread(target=check_inventory)
        threads.append(check_thread)
    
    print(f"\n🔄 Processing concurrent orders and updates...")
    
    # Start all operations
    for thread in threads:
        thread.start()
        time.sleep(0.05)  # Small delays
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    time.sleep(0.5)
    
    # Final inventory check
    print(f"\n📊 Final Status:")
    check_inventory()
    
    # Show version histories
    mvcc.print_version_info("iphone14_stock")
    mvcc.print_statistics()

def main():
    """
    Main demonstration of MVCC system
    """
    print("🇮🇳 Multi-Version Concurrency Control - Indian Tech Context")
    print("=" * 65)
    
    print("🎯 MVCC enables:")
    print("   • Readers never block writers")
    print("   • Writers never block readers") 
    print("   • Snapshot isolation")
    print("   • Historical data access")
    print("   • High concurrency")
    
    # Demo 1: Paytm wallet transactions
    paytm_wallet_mvcc_demo()
    
    # Demo 2: Flipkart order processing  
    flipkart_order_mvcc_demo()
    
    print(f"\n✅ MVCC system demonstrations complete!")
    
    print(f"\n📚 KEY LEARNINGS:")
    print(f"1. MVCC maintains multiple versions of each data item")
    print(f"2. Each transaction sees consistent snapshot at start time")
    print(f"3. No read-write blocking improves concurrency")
    print(f"4. Write-write conflicts detected at commit time")
    print(f"5. Garbage collection removes old, invisible versions")
    print(f"6. Indian use cases:")
    print(f"   • Paytm wallet: Concurrent balance updates")
    print(f"   • Flipkart orders: Inventory with price changes")
    print(f"   • IRCTC booking: Seat availability versioning")
    print(f"   • WhatsApp: Message edit history")
    print(f"7. Benefits:")
    print(f"   ✅ High read concurrency")
    print(f"   ✅ Consistent snapshots")
    print(f"   ✅ Historical queries")
    print(f"8. Trade-offs:")
    print(f"   ❌ Storage overhead (multiple versions)")
    print(f"   ❌ Garbage collection complexity")
    print(f"   ❌ Write conflicts need retry logic")
    print(f"9. Used by: PostgreSQL, Oracle, SQL Server, CockroachDB")

if __name__ == "__main__":
    main()