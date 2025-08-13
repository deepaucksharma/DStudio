#!/usr/bin/env python3
"""
Episode 21: CQRS/Event Sourcing - Event Store with PostgreSQL
Author: Code Developer Agent
Description: Production-ready Event Store implementation using PostgreSQL for Paytm transactions

Event Store है हमारे system का central nervous system
यहाँ सभी domain events store होते हैं chronological order में
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

class TransactionType(Enum):
    WALLET_TOPUP = "wallet_topup"
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"

# Domain Events for Paytm Wallet
@dataclass
class PaytmEvent:
    """Base event class for all Paytm events"""
    event_id: str
    aggregate_id: str
    event_type: str
    event_data: Dict
    version: int
    created_at: datetime
    metadata: Dict = None

@dataclass
class WalletCreatedEvent:
    wallet_id: str
    user_id: str
    phone_number: str
    created_at: datetime

@dataclass
class WalletTopupEvent:
    wallet_id: str
    amount: float
    transaction_id: str
    payment_method: str
    created_at: datetime

@dataclass
class PaymentMadeEvent:
    wallet_id: str
    amount: float
    merchant_id: str
    transaction_id: str
    purpose: str
    created_at: datetime

@dataclass
class RefundProcessedEvent:
    wallet_id: str
    amount: float
    original_transaction_id: str
    refund_transaction_id: str
    reason: str
    created_at: datetime

class EventStore:
    """PostgreSQL-based Event Store for Paytm transactions"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def initialize(self):
        """Database connection और tables initialize करें"""
        self.connection = psycopg2.connect(
            self.connection_string,
            cursor_factory=RealDictCursor
        )
        self.connection.autocommit = True
        
        await self._create_tables()
        print("✅ Event Store initialized successfully")
    
    async def _create_tables(self):
        """Event store tables create करें"""
        cursor = self.connection.cursor()
        
        # Main events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id UUID PRIMARY KEY,
                aggregate_id VARCHAR(255) NOT NULL,
                aggregate_type VARCHAR(100) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB NOT NULL,
                metadata JSONB,
                version INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                UNIQUE(aggregate_id, version)
            )
        """)
        
        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_aggregate_id 
            ON events(aggregate_id, version)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_type 
            ON events(event_type, created_at)
        """)
        
        # Snapshots table (for performance optimization)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                aggregate_id VARCHAR(255) PRIMARY KEY,
                aggregate_type VARCHAR(100) NOT NULL,
                snapshot_data JSONB NOT NULL,
                version INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """)
        
        cursor.close()
    
    async def append_event(self, aggregate_id: str, aggregate_type: str, 
                          event_type: str, event_data: Dict, 
                          expected_version: int, metadata: Dict = None) -> str:
        """
        Event को store में append करें
        Optimistic concurrency control के साथ
        """
        event_id = str(uuid.uuid4())
        cursor = self.connection.cursor()
        
        try:
            # Version check for concurrency control
            cursor.execute("""
                SELECT MAX(version) as max_version 
                FROM events 
                WHERE aggregate_id = %s
            """, (aggregate_id,))
            
            result = cursor.fetchone()
            current_version = result['max_version'] if result['max_version'] else 0
            
            if current_version != expected_version:
                raise Exception(f"Concurrency conflict: expected version {expected_version}, "
                              f"but current version is {current_version}")
            
            new_version = current_version + 1
            
            # Event insert करें
            cursor.execute("""
                INSERT INTO events (
                    event_id, aggregate_id, aggregate_type, event_type,
                    event_data, metadata, version, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_id, aggregate_id, aggregate_type, event_type,
                json.dumps(event_data), json.dumps(metadata or {}),
                new_version, datetime.now()
            ))
            
            print(f"📝 Event {event_type} appended for aggregate {aggregate_id} (v{new_version})")
            
            cursor.close()
            return event_id
            
        except Exception as e:
            cursor.close()
            raise e
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[PaytmEvent]:
        """Aggregate के सभी events fetch करें"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM events 
            WHERE aggregate_id = %s AND version > %s
            ORDER BY version
        """, (aggregate_id, from_version))
        
        rows = cursor.fetchall()
        cursor.close()
        
        events = []
        for row in rows:
            event = PaytmEvent(
                event_id=row['event_id'],
                aggregate_id=row['aggregate_id'],
                event_type=row['event_type'],
                event_data=row['event_data'],
                version=row['version'],
                created_at=row['created_at'],
                metadata=row['metadata']
            )
            events.append(event)
        
        return events
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[PaytmEvent]:
        """Specific event type के सभी events fetch करें"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM events 
            WHERE event_type = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (event_type, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        
        events = []
        for row in rows:
            event = PaytmEvent(
                event_id=row['event_id'],
                aggregate_id=row['aggregate_id'],
                event_type=row['event_type'],
                event_data=row['event_data'],
                version=row['version'],
                created_at=row['created_at'],
                metadata=row['metadata']
            )
            events.append(event)
        
        return events
    
    async def save_snapshot(self, aggregate_id: str, aggregate_type: str, 
                           snapshot_data: Dict, version: int):
        """Performance के लिए snapshot save करें"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO snapshots (aggregate_id, aggregate_type, snapshot_data, version, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (aggregate_id) 
            DO UPDATE SET 
                snapshot_data = EXCLUDED.snapshot_data,
                version = EXCLUDED.version,
                created_at = EXCLUDED.created_at
        """, (
            aggregate_id, aggregate_type, json.dumps(snapshot_data), 
            version, datetime.now()
        ))
        
        cursor.close()
        print(f"📸 Snapshot saved for {aggregate_id} at version {version}")
    
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict]:
        """Latest snapshot retrieve करें"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM snapshots WHERE aggregate_id = %s
        """, (aggregate_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'data': row['snapshot_data'],
                'version': row['version'],
                'created_at': row['created_at']
            }
        
        return None

# Paytm Wallet Aggregate using Event Sourcing
class PaytmWallet:
    """Event Sourced Paytm Wallet"""
    
    def __init__(self, wallet_id: str):
        self.wallet_id = wallet_id
        self.user_id = None
        self.phone_number = None
        self.balance = 0.0
        self.transaction_history = []
        self.version = 0
        self._uncommitted_events = []
    
    def create_wallet(self, user_id: str, phone_number: str):
        """नया wallet create करें"""
        event_data = {
            'wallet_id': self.wallet_id,
            'user_id': user_id,
            'phone_number': phone_number,
            'created_at': datetime.now().isoformat()
        }
        
        self._apply_event('WalletCreated', event_data)
    
    def topup_wallet(self, amount: float, payment_method: str):
        """Wallet में money add करें"""
        if amount <= 0:
            raise ValueError("Amount should be positive")
        
        transaction_id = f"TOPUP_{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'wallet_id': self.wallet_id,
            'amount': amount,
            'transaction_id': transaction_id,
            'payment_method': payment_method,
            'created_at': datetime.now().isoformat()
        }
        
        self._apply_event('WalletToppedUp', event_data)
        return transaction_id
    
    def make_payment(self, amount: float, merchant_id: str, purpose: str):
        """Payment करें"""
        if amount <= 0:
            raise ValueError("Amount should be positive")
        
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        
        transaction_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'wallet_id': self.wallet_id,
            'amount': amount,
            'merchant_id': merchant_id,
            'transaction_id': transaction_id,
            'purpose': purpose,
            'created_at': datetime.now().isoformat()
        }
        
        self._apply_event('PaymentMade', event_data)
        return transaction_id
    
    def process_refund(self, amount: float, original_transaction_id: str, reason: str):
        """Refund process करें"""
        if amount <= 0:
            raise ValueError("Refund amount should be positive")
        
        refund_transaction_id = f"REFUND_{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'wallet_id': self.wallet_id,
            'amount': amount,
            'original_transaction_id': original_transaction_id,
            'refund_transaction_id': refund_transaction_id,
            'reason': reason,
            'created_at': datetime.now().isoformat()
        }
        
        self._apply_event('RefundProcessed', event_data)
        return refund_transaction_id
    
    def _apply_event(self, event_type: str, event_data: Dict):
        """Event को apply करें (internal state update)"""
        self.version += 1
        
        # State update करें based on event type
        if event_type == 'WalletCreated':
            self.user_id = event_data['user_id']
            self.phone_number = event_data['phone_number']
        
        elif event_type == 'WalletToppedUp':
            self.balance += event_data['amount']
            self.transaction_history.append({
                'type': 'TOPUP',
                'amount': event_data['amount'],
                'transaction_id': event_data['transaction_id'],
                'timestamp': event_data['created_at']
            })
        
        elif event_type == 'PaymentMade':
            self.balance -= event_data['amount']
            self.transaction_history.append({
                'type': 'PAYMENT',
                'amount': -event_data['amount'],
                'merchant_id': event_data['merchant_id'],
                'transaction_id': event_data['transaction_id'],
                'purpose': event_data['purpose'],
                'timestamp': event_data['created_at']
            })
        
        elif event_type == 'RefundProcessed':
            self.balance += event_data['amount']
            self.transaction_history.append({
                'type': 'REFUND',
                'amount': event_data['amount'],
                'original_transaction_id': event_data['original_transaction_id'],
                'transaction_id': event_data['refund_transaction_id'],
                'reason': event_data['reason'],
                'timestamp': event_data['created_at']
            })
        
        # Uncommitted events list में add करें
        self._uncommitted_events.append({
            'event_type': event_type,
            'event_data': event_data
        })
    
    def get_uncommitted_events(self):
        """Uncommitted events return करें"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Events को committed mark करें"""
        self._uncommitted_events.clear()
    
    def apply_historical_events(self, events: List[PaytmEvent]):
        """Historical events से state rebuild करें"""
        for event in events:
            self._apply_event(event.event_type, event.event_data)
        
        # Clear uncommitted events क्योंकि ये historical हैं
        self._uncommitted_events.clear()

# Wallet Repository with Event Store
class PaytmWalletRepository:
    """Event Store के साथ wallet repository"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    async def save(self, wallet: PaytmWallet):
        """Wallet की सभी uncommitted events को store करें"""
        uncommitted_events = wallet.get_uncommitted_events()
        
        for event in uncommitted_events:
            await self.event_store.append_event(
                aggregate_id=wallet.wallet_id,
                aggregate_type="PaytmWallet",
                event_type=event['event_type'],
                event_data=event['event_data'],
                expected_version=wallet.version - 1,  # Version before this event
                metadata={'aggregate_type': 'PaytmWallet'}
            )
        
        wallet.mark_events_as_committed()
        
        # Snapshot save करें हर 10 events के बाद
        if wallet.version % 10 == 0:
            snapshot_data = {
                'wallet_id': wallet.wallet_id,
                'user_id': wallet.user_id,
                'phone_number': wallet.phone_number,
                'balance': wallet.balance,
                'transaction_history': wallet.transaction_history
            }
            
            await self.event_store.save_snapshot(
                wallet.wallet_id, "PaytmWallet", snapshot_data, wallet.version
            )
    
    async def get_by_id(self, wallet_id: str) -> PaytmWallet:
        """Wallet ID से wallet load करें"""
        wallet = PaytmWallet(wallet_id)
        
        # पहले snapshot check करें
        snapshot = await self.event_store.get_snapshot(wallet_id)
        from_version = 0
        
        if snapshot:
            # Snapshot से state load करें
            data = snapshot['data']
            wallet.user_id = data['user_id']
            wallet.phone_number = data['phone_number']
            wallet.balance = data['balance']
            wallet.transaction_history = data['transaction_history']
            wallet.version = snapshot['version']
            from_version = snapshot['version']
        
        # Snapshot के बाद के events load करें
        events = await self.event_store.get_events(wallet_id, from_version)
        wallet.apply_historical_events(events)
        
        return wallet

# Demo Function
async def demonstrate_paytm_event_store():
    """Paytm Event Store का comprehensive demonstration"""
    print("💰 Paytm Wallet Event Store Demo")
    print("=" * 50)
    
    # Mock database connection (in production, use real PostgreSQL)
    connection_string = "postgresql://user:password@localhost:5432/paytm_events"
    
    # For demo, we'll simulate the database operations
    print("📦 Initializing Event Store...")
    event_store = MockEventStore()  # Using mock for demo
    wallet_repository = PaytmWalletRepository(event_store)
    
    # 1. Create new wallet
    wallet_id = f"WALLET_{uuid.uuid4().hex[:8].upper()}"
    wallet = PaytmWallet(wallet_id)
    
    print(f"\n👤 Creating wallet {wallet_id}")
    wallet.create_wallet("USER001", "+91-9876543210")
    await wallet_repository.save(wallet)
    
    # 2. Topup wallet
    print(f"\n💳 Topping up wallet with ₹1000")
    transaction_id = wallet.topup_wallet(1000.0, "UPI")
    await wallet_repository.save(wallet)
    
    # 3. Make payment
    print(f"\n🛒 Making payment of ₹299 to Flipkart")
    payment_id = wallet.make_payment(299.0, "FLIPKART", "Mobile Purchase")
    await wallet_repository.save(wallet)
    
    # 4. Process refund
    print(f"\n↩️ Processing refund of ₹50")
    refund_id = wallet.process_refund(50.0, payment_id, "Partial refund")
    await wallet_repository.save(wallet)
    
    print(f"\n💼 Final wallet state:")
    print(f"  Balance: ₹{wallet.balance}")
    print(f"  Transactions: {len(wallet.transaction_history)}")
    print(f"  Version: {wallet.version}")
    
    # 5. Reload wallet from events (demonstrating event sourcing)
    print(f"\n🔄 Reloading wallet from event store...")
    reloaded_wallet = await wallet_repository.get_by_id(wallet_id)
    
    print(f"  Reloaded Balance: ₹{reloaded_wallet.balance}")
    print(f"  Reloaded Version: {reloaded_wallet.version}")
    print(f"  Transaction History:")
    
    for i, tx in enumerate(reloaded_wallet.transaction_history, 1):
        print(f"    {i}. {tx['type']}: ₹{tx['amount']} | ID: {tx.get('transaction_id', 'N/A')}")
    
    print("\n✅ Event Store Demo completed successfully!")

# Mock Event Store for demonstration (replace with real PostgreSQL in production)
class MockEventStore:
    """Mock Event Store for demonstration purposes"""
    
    def __init__(self):
        self.events = []
        self.snapshots = {}
    
    async def append_event(self, aggregate_id: str, aggregate_type: str, 
                          event_type: str, event_data: Dict, 
                          expected_version: int, metadata: Dict = None) -> str:
        event_id = str(uuid.uuid4())
        
        current_events = [e for e in self.events if e['aggregate_id'] == aggregate_id]
        current_version = len(current_events)
        
        if current_version != expected_version:
            raise Exception(f"Concurrency conflict: expected {expected_version}, got {current_version}")
        
        event = {
            'event_id': event_id,
            'aggregate_id': aggregate_id,
            'aggregate_type': aggregate_type,
            'event_type': event_type,
            'event_data': event_data,
            'metadata': metadata or {},
            'version': current_version + 1,
            'created_at': datetime.now()
        }
        
        self.events.append(event)
        print(f"📝 Event {event_type} saved with ID {event_id}")
        return event_id
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[PaytmEvent]:
        filtered_events = [
            e for e in self.events 
            if e['aggregate_id'] == aggregate_id and e['version'] > from_version
        ]
        
        events = []
        for event_data in filtered_events:
            event = PaytmEvent(
                event_id=event_data['event_id'],
                aggregate_id=event_data['aggregate_id'],
                event_type=event_data['event_type'],
                event_data=event_data['event_data'],
                version=event_data['version'],
                created_at=event_data['created_at'],
                metadata=event_data['metadata']
            )
            events.append(event)
        
        return events
    
    async def save_snapshot(self, aggregate_id: str, aggregate_type: str, 
                           snapshot_data: Dict, version: int):
        self.snapshots[aggregate_id] = {
            'data': snapshot_data,
            'version': version,
            'created_at': datetime.now()
        }
        print(f"📸 Snapshot saved for {aggregate_id}")
    
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict]:
        return self.snapshots.get(aggregate_id)

if __name__ == "__main__":
    """
    Key Event Store Benefits:
    1. Complete audit trail of all changes
    2. Point-in-time state reconstruction
    3. Event replay capabilities
    4. Horizontal scaling with partitioning
    5. Natural backup and disaster recovery
    """
    asyncio.run(demonstrate_paytm_event_store())