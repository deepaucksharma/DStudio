"""
Event Streaming Episode - Event Sourcing Pattern Implementation
Production-ready event sourcing with complete event store and replay capability

Author: Hindi Tech Podcast Series
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import sqlite3
import threading
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for Paytm wallet system"""
    WALLET_CREATED = "WALLET_CREATED"
    MONEY_ADDED = "MONEY_ADDED"
    PAYMENT_MADE = "PAYMENT_MADE"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CASHBACK_RECEIVED = "CASHBACK_RECEIVED"
    WALLET_FROZEN = "WALLET_FROZEN"
    WALLET_UNFROZEN = "WALLET_UNFROZEN"
    KYC_VERIFIED = "KYC_VERIFIED"

@dataclass
class Event:
    """
    Base Event class - सभी domain events का blueprint
    Event sourcing में हर state change को event के रूप में store करते हैं
    """
    event_id: str
    event_type: EventType
    aggregate_id: str  # Entity की ID जिसके लिए event है
    aggregate_version: int
    event_data: Dict[str, Any]
    timestamp: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Event को dictionary format में convert करते हैं storage के लिए"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'aggregate_id': self.aggregate_id,
            'aggregate_version': self.aggregate_version,
            'event_data': json.dumps(self.event_data),
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'correlation_id': self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Dictionary से Event object बनाते हैं"""
        return cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            aggregate_id=data['aggregate_id'],
            aggregate_version=data['aggregate_version'],
            event_data=json.loads(data['event_data']),
            timestamp=data['timestamp'],
            user_id=data['user_id'],
            correlation_id=data['correlation_id']
        )

class EventStore:
    """
    Event Store - सभी events को persist करने के लिए
    Production में यह dedicated database (EventStoreDB/PostgreSQL) होगा
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """Event store initialize करते हैं SQLite के साथ"""
        self.db_path = db_path
        self.lock = threading.Lock()  # Thread safety के लिए
        self._init_database()
        
        logger.info(f"Event Store initialized with database: {db_path}")
    
    def _init_database(self):
        """Database schema create करते हैं"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    aggregate_id TEXT NOT NULL,
                    aggregate_version INTEGER NOT NULL,
                    event_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    correlation_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for fast queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_aggregate_id_version 
                ON events (aggregate_id, aggregate_version)
            """)
            
            # Index for timestamp based queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON events (timestamp)
            """)
            
            conn.commit()
    
    def append_event(self, event: Event) -> bool:
        """
        Event को store में append करते हैं
        Optimistic concurrency control के साथ
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Check for version conflicts - Concurrent updates handle करने के लिए
                    cursor = conn.execute(
                        "SELECT MAX(aggregate_version) FROM events WHERE aggregate_id = ?",
                        (event.aggregate_id,)
                    )
                    
                    current_version = cursor.fetchone()[0] or 0
                    
                    # Version check - Concurrency conflict detect करें
                    if current_version >= event.aggregate_version:
                        logger.error(f"Version conflict: Expected {event.aggregate_version}, "
                                   f"but current is {current_version}")
                        return False
                    
                    # Event insert करें
                    conn.execute("""
                        INSERT INTO events 
                        (event_id, event_type, aggregate_id, aggregate_version, 
                         event_data, timestamp, user_id, correlation_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.event_id,
                        event.event_type.value,
                        event.aggregate_id,
                        event.aggregate_version,
                        json.dumps(event.event_data),
                        event.timestamp,
                        event.user_id,
                        event.correlation_id
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"✅ Event stored: {event.event_type.value} for "
                               f"aggregate {event.aggregate_id} v{event.aggregate_version}")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Error storing event: {e}")
                return False
    
    def get_events(self, aggregate_id: str, 
                   from_version: int = 0) -> List[Event]:
        """
        Specific aggregate के सभी events retrieve करते हैं
        State reconstruction के लिए use होता है
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Dict-like access
                
                cursor = conn.execute("""
                    SELECT * FROM events 
                    WHERE aggregate_id = ? AND aggregate_version > ?
                    ORDER BY aggregate_version ASC
                """, (aggregate_id, from_version))
                
                events = []
                for row in cursor.fetchall():
                    event_data = {
                        'event_id': row['event_id'],
                        'event_type': row['event_type'],
                        'aggregate_id': row['aggregate_id'],
                        'aggregate_version': row['aggregate_version'],
                        'event_data': row['event_data'],
                        'timestamp': row['timestamp'],
                        'user_id': row['user_id'],
                        'correlation_id': row['correlation_id']
                    }
                    events.append(Event.from_dict(event_data))
                
                logger.info(f"📚 Retrieved {len(events)} events for aggregate {aggregate_id}")
                return events
                
        except Exception as e:
            logger.error(f"❌ Error retrieving events: {e}")
            return []
    
    def get_all_events(self, from_timestamp: Optional[str] = None) -> List[Event]:
        """
        सभी events retrieve करते हैं event replay के लिए
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if from_timestamp:
                    cursor = conn.execute("""
                        SELECT * FROM events 
                        WHERE timestamp >= ?
                        ORDER BY timestamp ASC, aggregate_version ASC
                    """, (from_timestamp,))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM events 
                        ORDER BY timestamp ASC, aggregate_version ASC
                    """)
                
                events = []
                for row in cursor.fetchall():
                    event_data = {
                        'event_id': row['event_id'],
                        'event_type': row['event_type'],
                        'aggregate_id': row['aggregate_id'],
                        'aggregate_version': row['aggregate_version'],
                        'event_data': row['event_data'],
                        'timestamp': row['timestamp'],
                        'user_id': row['user_id'],
                        'correlation_id': row['correlation_id']
                    }
                    events.append(Event.from_dict(event_data))
                
                logger.info(f"📚 Retrieved {len(events)} total events from store")
                return events
                
        except Exception as e:
            logger.error(f"❌ Error retrieving all events: {e}")
            return []

class PaytmWallet:
    """
    Paytm Wallet Aggregate - Event sourcing pattern के साथ
    State को events से reconstruct करते हैं, direct state store नहीं करते
    """
    
    def __init__(self, wallet_id: str):
        """Wallet initialize करते हैं empty state के साथ"""
        self.wallet_id = wallet_id
        self.version = 0
        self.balance = 0.0
        self.status = "INACTIVE"
        self.kyc_verified = False
        self.created_at = None
        self.transactions = []
        
        # Uncommitted events - Batch में save करने के लिए
        self.uncommitted_events = []
    
    def create_wallet(self, user_id: str, phone_number: str, 
                     initial_balance: float = 0.0) -> bool:
        """
        New wallet create करते हैं
        Event sourcing में यह एक WALLET_CREATED event generate करेगा
        """
        if self.status != "INACTIVE":
            logger.error(f"Wallet {self.wallet_id} already exists")
            return False
        
        event_data = {
            'user_id': user_id,
            'phone_number': phone_number,
            'initial_balance': initial_balance,
            'currency': 'INR'
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WALLET_CREATED,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id
        )
        
        # Event apply करते हैं और uncommitted events में add करते हैं
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.info(f"🎉 Wallet created: {self.wallet_id} for user {user_id}")
        return True
    
    def add_money(self, amount: float, source: str, 
                  transaction_id: str, user_id: str) -> bool:
        """
        Wallet में money add करते हैं
        Bank transfer, UPI, Card से money आ सकता है
        """
        if self.status != "ACTIVE":
            logger.error(f"Wallet {self.wallet_id} is not active")
            return False
        
        if amount <= 0:
            logger.error("Amount must be positive")
            return False
        
        event_data = {
            'amount': amount,
            'source': source,  # 'BANK_TRANSFER', 'UPI', 'CARD'
            'transaction_id': transaction_id,
            'previous_balance': self.balance,
            'new_balance': self.balance + amount
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.MONEY_ADDED,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            correlation_id=transaction_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.info(f"💰 Money added: ₹{amount} to wallet {self.wallet_id}")
        return True
    
    def make_payment(self, amount: float, merchant_id: str, 
                    transaction_id: str, user_id: str, 
                    description: str = "") -> bool:
        """
        Payment करते हैं wallet से
        Insufficient balance check करते हैं
        """
        if self.status != "ACTIVE":
            logger.error(f"Wallet {self.wallet_id} is not active")
            return False
        
        if amount <= 0:
            logger.error("Payment amount must be positive")
            return False
        
        if self.balance < amount:
            # Payment failed event generate करते हैं
            self._create_payment_failed_event(amount, merchant_id, 
                                            transaction_id, user_id, 
                                            "INSUFFICIENT_BALANCE")
            return False
        
        event_data = {
            'amount': amount,
            'merchant_id': merchant_id,
            'transaction_id': transaction_id,
            'description': description,
            'previous_balance': self.balance,
            'new_balance': self.balance - amount
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PAYMENT_MADE,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            correlation_id=transaction_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.info(f"💳 Payment made: ₹{amount} to merchant {merchant_id}")
        return True
    
    def receive_cashback(self, amount: float, source_transaction_id: str, 
                        user_id: str, cashback_type: str = "TRANSACTION") -> bool:
        """
        Cashback receive करते हैं
        Paytm में अक्सर cashback मिलता है transactions पर
        """
        if self.status != "ACTIVE":
            logger.error(f"Wallet {self.wallet_id} is not active")
            return False
        
        event_data = {
            'amount': amount,
            'source_transaction_id': source_transaction_id,
            'cashback_type': cashback_type,  # 'TRANSACTION', 'REFERRAL', 'PROMOTIONAL'
            'previous_balance': self.balance,
            'new_balance': self.balance + amount
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.CASHBACK_RECEIVED,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            correlation_id=source_transaction_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.info(f"🎁 Cashback received: ₹{amount} in wallet {self.wallet_id}")
        return True
    
    def verify_kyc(self, user_id: str, kyc_document_id: str) -> bool:
        """
        KYC verification complete करते हैं
        Higher transaction limits enable हो जाती हैं
        """
        if self.kyc_verified:
            logger.info(f"KYC already verified for wallet {self.wallet_id}")
            return True
        
        event_data = {
            'kyc_document_id': kyc_document_id,
            'verification_timestamp': datetime.now(timezone.utc).isoformat(),
            'verification_method': 'AADHAAR_OTP'
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.KYC_VERIFIED,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.info(f"✅ KYC verified for wallet {self.wallet_id}")
        return True
    
    def _create_payment_failed_event(self, amount: float, merchant_id: str,
                                   transaction_id: str, user_id: str, 
                                   failure_reason: str):
        """Payment failure event create करते हैं"""
        event_data = {
            'amount': amount,
            'merchant_id': merchant_id,
            'transaction_id': transaction_id,
            'failure_reason': failure_reason,
            'current_balance': self.balance
        }
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PAYMENT_FAILED,
            aggregate_id=self.wallet_id,
            aggregate_version=self.version + 1,
            event_data=event_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            correlation_id=transaction_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        logger.warning(f"❌ Payment failed: ₹{amount} - {failure_reason}")
    
    def _apply_event(self, event: Event):
        """
        Event को current state पर apply करते हैं
        यह method state reconstruction के लिए भी use होता है
        """
        if event.event_type == EventType.WALLET_CREATED:
            self.status = "ACTIVE"
            self.balance = event.event_data['initial_balance']
            self.created_at = event.timestamp
            
        elif event.event_type == EventType.MONEY_ADDED:
            self.balance = event.event_data['new_balance']
            self.transactions.append({
                'type': 'CREDIT',
                'amount': event.event_data['amount'],
                'timestamp': event.timestamp,
                'source': event.event_data['source']
            })
            
        elif event.event_type == EventType.PAYMENT_MADE:
            self.balance = event.event_data['new_balance']
            self.transactions.append({
                'type': 'DEBIT',
                'amount': event.event_data['amount'],
                'timestamp': event.timestamp,
                'merchant_id': event.event_data['merchant_id']
            })
            
        elif event.event_type == EventType.CASHBACK_RECEIVED:
            self.balance = event.event_data['new_balance']
            self.transactions.append({
                'type': 'CASHBACK',
                'amount': event.event_data['amount'],
                'timestamp': event.timestamp,
                'cashback_type': event.event_data['cashback_type']
            })
            
        elif event.event_type == EventType.KYC_VERIFIED:
            self.kyc_verified = True
            
        elif event.event_type == EventType.WALLET_FROZEN:
            self.status = "FROZEN"
            
        elif event.event_type == EventType.WALLET_UNFROZEN:
            self.status = "ACTIVE"
        
        # Version increment करें
        self.version = event.aggregate_version
    
    def load_from_history(self, events: List[Event]):
        """
        Event history से wallet state reconstruct करते हैं
        यह event sourcing का core concept है
        """
        logger.info(f"🔄 Reconstructing wallet {self.wallet_id} from {len(events)} events")
        
        for event in events:
            self._apply_event(event)
        
        logger.info(f"✅ Wallet {self.wallet_id} reconstructed - "
                   f"Balance: ₹{self.balance}, Version: {self.version}")
    
    def get_uncommitted_events(self) -> List[Event]:
        """Uncommitted events return करते हैं save करने के लिए"""
        return self.uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Events को committed mark करते हैं save करने के बाद"""
        self.uncommitted_events.clear()
    
    def get_wallet_summary(self) -> Dict[str, Any]:
        """Wallet की current state summary return करते हैं"""
        return {
            'wallet_id': self.wallet_id,
            'balance': self.balance,
            'status': self.status,
            'kyc_verified': self.kyc_verified,
            'version': self.version,
            'total_transactions': len(self.transactions),
            'created_at': self.created_at
        }

class WalletService:
    """
    Wallet Service - Event sourcing with repository pattern
    Business logic और event store के बीच abstraction layer
    """
    
    def __init__(self, event_store: EventStore):
        """Service initialize करते हैं event store के साथ"""
        self.event_store = event_store
        logger.info("💼 Wallet Service initialized")
    
    def create_wallet(self, wallet_id: str, user_id: str, 
                     phone_number: str) -> Optional[PaytmWallet]:
        """New wallet create करते हैं"""
        wallet = PaytmWallet(wallet_id)
        
        if wallet.create_wallet(user_id, phone_number):
            # Events को store में save करते हैं
            for event in wallet.get_uncommitted_events():
                if self.event_store.append_event(event):
                    wallet.mark_events_as_committed()
                else:
                    logger.error(f"Failed to save wallet creation events")
                    return None
            
            return wallet
        
        return None
    
    def get_wallet(self, wallet_id: str) -> Optional[PaytmWallet]:
        """
        Wallet को event store से load करते हैं
        Event sourcing में यह state reconstruction है
        """
        events = self.event_store.get_events(wallet_id)
        
        if not events:
            logger.warning(f"No events found for wallet {wallet_id}")
            return None
        
        wallet = PaytmWallet(wallet_id)
        wallet.load_from_history(events)
        
        return wallet
    
    def save_wallet(self, wallet: PaytmWallet) -> bool:
        """Wallet के uncommitted events को save करते हैं"""
        events = wallet.get_uncommitted_events()
        
        if not events:
            return True  # No changes to save
        
        # सभी events को atomically save करने की कोशिश करें
        saved_events = []
        for event in events:
            if self.event_store.append_event(event):
                saved_events.append(event)
            else:
                # Rollback logic यहाँ implement कर सकते हैं
                logger.error(f"Failed to save event {event.event_id}")
                return False
        
        wallet.mark_events_as_committed()
        logger.info(f"💾 Saved {len(saved_events)} events for wallet {wallet.wallet_id}")
        return True

def simulate_paytm_wallet_operations():
    """
    Paytm wallet operations simulate करते हैं Event Sourcing के साथ
    Real-world scenarios demonstrate करते हैं
    """
    print("🏦 Starting Paytm Wallet Event Sourcing Simulation...")
    print("💳 Demonstrating event-driven wallet operations")
    print("-" * 60)
    
    # Event store और service initialize करें
    event_store = EventStore("paytm_wallet_events.db")
    wallet_service = WalletService(event_store)
    
    # Sample user data
    user_id = "user_mumbai_001"
    wallet_id = f"wallet_{user_id}"
    phone_number = "+91-9876543210"
    
    try:
        # 1. Wallet create करें
        print("\n1️⃣ Creating new Paytm wallet...")
        wallet = wallet_service.create_wallet(wallet_id, user_id, phone_number)
        if wallet:
            print(f"✅ Wallet created: {wallet.get_wallet_summary()}")
        
        # 2. Money add करें from different sources
        print("\n2️⃣ Adding money to wallet...")
        wallet.add_money(1000.0, "BANK_TRANSFER", "txn_001", user_id)
        wallet.add_money(500.0, "UPI", "txn_002", user_id)
        wallet_service.save_wallet(wallet)
        
        print(f"✅ Money added. Current balance: ₹{wallet.balance}")
        
        # 3. KYC verification
        print("\n3️⃣ Verifying KYC...")
        wallet.verify_kyc(user_id, "aadhaar_123456789")
        wallet_service.save_wallet(wallet)
        
        print(f"✅ KYC verified: {wallet.kyc_verified}")
        
        # 4. Make payments
        print("\n4️⃣ Making payments...")
        payments = [
            (200.0, "merchant_swiggy", "Swiggy food order"),
            (150.0, "merchant_uber", "Uber cab ride"),
            (300.0, "merchant_bigbasket", "Grocery shopping"),
            (50.0, "merchant_bookmyshow", "Movie tickets")
        ]
        
        for amount, merchant, description in payments:
            txn_id = f"pay_{merchant}_{int(datetime.now().timestamp())}"
            success = wallet.make_payment(amount, merchant, txn_id, user_id, description)
            print(f"   {'✅' if success else '❌'} Payment ₹{amount} to {merchant}: {success}")
        
        wallet_service.save_wallet(wallet)
        
        # 5. Receive cashbacks
        print("\n5️⃣ Receiving cashbacks...")
        cashbacks = [
            (20.0, "pay_merchant_swiggy", "TRANSACTION"),
            (15.0, "pay_merchant_uber", "TRANSACTION"),
            (50.0, "referral_bonus", "REFERRAL")
        ]
        
        for amount, source_txn, cb_type in cashbacks:
            wallet.receive_cashback(amount, source_txn, user_id, cb_type)
            print(f"   🎁 Cashback ₹{amount} received from {cb_type}")
        
        wallet_service.save_wallet(wallet)
        
        # 6. Final wallet state
        print(f"\n6️⃣ Final wallet state:")
        summary = wallet.get_wallet_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # 7. Event sourcing demonstration - Wallet reconstruction
        print(f"\n7️⃣ Demonstrating Event Sourcing - State Reconstruction...")
        print("   Loading wallet from event history...")
        
        # Fresh wallet instance load करें events से
        fresh_wallet = wallet_service.get_wallet(wallet_id)
        if fresh_wallet:
            fresh_summary = fresh_wallet.get_wallet_summary()
            print(f"   ✅ Wallet reconstructed from events:")
            print(f"      Balance: ₹{fresh_summary['balance']}")
            print(f"      Version: {fresh_summary['version']}")
            print(f"      Total events replayed: {fresh_summary['version']}")
        
        # 8. Event replay demonstration
        print(f"\n8️⃣ Event Replay Demonstration...")
        all_events = event_store.get_all_events()
        print(f"   📚 Total events in store: {len(all_events)}")
        
        print("   📖 Event History:")
        for event in all_events:
            print(f"      v{event.aggregate_version}: {event.event_type.value} - "
                 f"{event.timestamp[:19]}")
        
        # 9. Point-in-time recovery demonstration
        print(f"\n9️⃣ Point-in-time Recovery Demonstration...")
        print("   Reconstructing wallet state after first 3 events...")
        
        point_in_time_wallet = PaytmWallet(wallet_id)
        point_in_time_wallet.load_from_history(all_events[:3])
        
        pit_summary = point_in_time_wallet.get_wallet_summary()
        print(f"   💰 Balance after 3 events: ₹{pit_summary['balance']}")
        print(f"   📊 Transactions after 3 events: {pit_summary['total_transactions']}")
        
        print(f"\n✅ Event Sourcing demonstration completed successfully!")
        print(f"💡 Key benefits demonstrated:")
        print(f"   - Complete audit trail of all changes")
        print(f"   - Ability to reconstruct state from events")
        print(f"   - Point-in-time recovery capability") 
        print(f"   - Event replay for debugging and analytics")
        
    except Exception as e:
        logger.error(f"❌ Error in wallet simulation: {e}")
        print(f"❌ Simulation failed: {e}")

if __name__ == "__main__":
    simulate_paytm_wallet_operations()