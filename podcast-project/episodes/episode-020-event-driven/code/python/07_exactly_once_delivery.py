#!/usr/bin/env python3
"""
Exactly-Once Delivery Guarantees Implementation
उदाहरण: HDFC bank के fund transfer events के लिए exactly-once semantics

Setup:
pip install redis asyncio hashlib

Indian Context: Banking transactions मein duplicate processing fatal है:
- Fund transfers (₹1 lakh accidentally transferred twice)
- Bill payments (electricity bill paid multiple times)
- Insurance premium deductions
- Loan EMI processing

Exactly-Once Challenges:
- Network failures causing retries
- Consumer crashes mid-processing
- Message broker failures
- Idempotency key management
- Distributed state consistency
"""

import asyncio
import hashlib
import json
import logging
import redis
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set
import random

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageState(Enum):
    """Message processing states"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BankingEvent:
    """Banking event structure with exactly-once semantics"""
    event_id: str
    transaction_id: str
    idempotency_key: str
    event_type: str
    account_from: str
    account_to: str
    amount: float
    currency: str = "INR"
    reference: str = None
    timestamp: str = None
    retry_count: int = 0
    checksum: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.reference:
            self.reference = f"REF_{uuid.uuid4().hex[:8].upper()}"
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Event integrity के लिए checksum calculate करना"""
        data = f"{self.transaction_id}{self.account_from}{self.account_to}{self.amount}{self.currency}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class IdempotencyManager:
    """
    Idempotency key management with Redis
    Mumbai railway ticket counter की तरह - एक बार ticket मिला तो दोबारा नहीं
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.key_prefix = "hdfc:idempotency"
        self.processing_prefix = "hdfc:processing"
        self.ttl_seconds = 24 * 60 * 60  # 24 hours retention
        
        try:
            self.redis_client.ping()
            logger.info("✅ Connected to Redis for idempotency management")
        except redis.ConnectionError:
            logger.error("❌ Failed to connect to Redis")
            raise
    
    async def is_duplicate(self, idempotency_key: str) -> bool:
        """Check if message is duplicate based on idempotency key"""
        key = f"{self.key_prefix}:{idempotency_key}"
        return bool(self.redis_client.exists(key))
    
    async def mark_processing(self, idempotency_key: str, event_data: Dict[str, Any]) -> bool:
        """
        Mark message as being processed
        Returns False if already being processed by another consumer
        """
        processing_key = f"{self.processing_prefix}:{idempotency_key}"
        
        # Use SET with NX (not exists) and EX (expiry) for atomic operation
        success = self.redis_client.set(
            processing_key, 
            json.dumps(event_data),
            nx=True,  # Only set if key doesn't exist
            ex=300   # 5 minutes expiry (processing timeout)
        )
        
        if success:
            logger.info(f"🔒 Message marked as processing: {idempotency_key}")
            return True
        else:
            logger.warning(f"⚠️ Message already being processed: {idempotency_key}")
            return False
    
    async def mark_completed(self, idempotency_key: str, result: Dict[str, Any]) -> None:
        """Mark message as completed successfully"""
        completed_key = f"{self.key_prefix}:{idempotency_key}"
        processing_key = f"{self.processing_prefix}:{idempotency_key}"
        
        # Store completion result
        self.redis_client.setex(
            completed_key, 
            self.ttl_seconds,
            json.dumps({
                'status': 'completed',
                'result': result,
                'completed_at': datetime.now().isoformat()
            })
        )
        
        # Remove from processing
        self.redis_client.delete(processing_key)
        
        logger.info(f"✅ Message marked as completed: {idempotency_key}")
    
    async def mark_failed(self, idempotency_key: str, error: str) -> None:
        """Mark message as failed"""
        processing_key = f"{self.processing_prefix}:{idempotency_key}"
        
        # Remove from processing (will allow retry)
        self.redis_client.delete(processing_key)
        
        logger.error(f"❌ Message processing failed: {idempotency_key} - {error}")
    
    async def get_previous_result(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Get previous processing result if exists"""
        key = f"{self.key_prefix}:{idempotency_key}"
        result_json = self.redis_client.get(key)
        
        if result_json:
            return json.loads(result_json)
        return None
    
    def cleanup_expired_processing(self) -> int:
        """Cleanup expired processing locks"""
        pattern = f"{self.processing_prefix}:*"
        keys = self.redis_client.keys(pattern)
        
        expired_count = 0
        for key in keys:
            ttl = self.redis_client.ttl(key)
            if ttl == -1:  # No expiry set (shouldn't happen)
                self.redis_client.delete(key)
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"🧹 Cleaned up {expired_count} expired processing locks")
        
        return expired_count

class ExactlyOnceProcessor:
    """
    Exactly-once message processor
    Bank teller की तरह - हर transaction को carefully handle करना
    """
    
    def __init__(self, idempotency_manager: IdempotencyManager):
        self.idempotency_manager = idempotency_manager
        self.account_balances = {
            "HDFC_RAHUL_001": 250000.0,
            "HDFC_PRIYA_002": 180000.0,
            "HDFC_AMIT_003": 95000.0,
            "HDFC_NEHA_004": 320000.0
        }
    
    async def process_event(self, event: BankingEvent) -> Dict[str, Any]:
        """
        Process banking event with exactly-once guarantee
        """
        logger.info(f"💳 Processing banking event: {event.transaction_id}")
        logger.info(f"   🔑 Idempotency Key: {event.idempotency_key}")
        logger.info(f"   💰 Amount: ₹{event.amount}")
        logger.info(f"   📊 From: {event.account_from} → To: {event.account_to}")
        
        # Step 1: Check for duplicate
        if await self.idempotency_manager.is_duplicate(event.idempotency_key):
            logger.info(f"🔄 Duplicate detected - returning previous result")
            previous_result = await self.idempotency_manager.get_previous_result(event.idempotency_key)
            
            if previous_result and previous_result.get('status') == 'completed':
                return previous_result['result']
            else:
                # Previous processing might have failed - allow retry
                logger.info(f"🔄 Previous processing failed - allowing retry")
        
        # Step 2: Mark as processing (distributed lock)
        event_data = asdict(event)
        can_process = await self.idempotency_manager.mark_processing(
            event.idempotency_key, event_data
        )
        
        if not can_process:
            # Another instance is processing this event
            logger.warning(f"⚠️ Event already being processed by another consumer")
            
            # Wait and check for completion
            for attempt in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                previous_result = await self.idempotency_manager.get_previous_result(event.idempotency_key)
                if previous_result and previous_result.get('status') == 'completed':
                    return previous_result['result']
            
            raise Exception("Event processing timeout - another consumer may have failed")
        
        try:
            # Step 3: Validate event integrity
            if event.checksum != event._calculate_checksum():
                raise Exception("Event checksum mismatch - data corruption detected")
            
            # Step 4: Actual business logic
            result = await self._execute_fund_transfer(event)
            
            # Step 5: Mark as completed
            await self.idempotency_manager.mark_completed(event.idempotency_key, result)
            
            logger.info(f"✅ Event processed successfully: {event.transaction_id}")
            return result
            
        except Exception as e:
            # Step 6: Mark as failed (releases processing lock)
            await self.idempotency_manager.mark_failed(event.idempotency_key, str(e))
            raise
    
    async def _execute_fund_transfer(self, event: BankingEvent) -> Dict[str, Any]:
        """Execute the actual fund transfer"""
        from_account = event.account_from
        to_account = event.account_to
        amount = event.amount
        
        # Account validation
        if from_account not in self.account_balances:
            raise Exception(f"Source account not found: {from_account}")
        
        if to_account not in self.account_balances:
            raise Exception(f"Destination account not found: {to_account}")
        
        # Balance check
        current_balance = self.account_balances[from_account]
        if current_balance < amount:
            raise Exception(f"Insufficient funds: ₹{current_balance} < ₹{amount}")
        
        # Simulate processing time and potential failure
        await asyncio.sleep(0.5)
        
        # Random failure simulation (5% chance)
        if random.random() < 0.05:
            raise Exception("Banking service temporarily unavailable")
        
        # Execute transfer atomically
        self.account_balances[from_account] -= amount
        self.account_balances[to_account] += amount
        
        # Generate transaction reference
        transaction_ref = f"TXN_{uuid.uuid4().hex[:8].upper()}"
        
        result = {
            'transaction_id': event.transaction_id,
            'transaction_ref': transaction_ref,
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount,
            'new_balance_from': self.account_balances[from_account],
            'new_balance_to': self.account_balances[to_account],
            'processed_at': datetime.now().isoformat(),
            'status': 'success'
        }
        
        logger.info(f"💸 Transfer executed: ₹{amount} from {from_account} to {to_account}")
        logger.info(f"   📊 New balances: {from_account}: ₹{result['new_balance_from']}, "
                   f"{to_account}: ₹{result['new_balance_to']}")
        
        return result

class MessageProducer:
    """Message producer with idempotency key generation"""
    
    def __init__(self):
        self.messages = []
    
    def create_fund_transfer_event(self, from_account: str, to_account: str, 
                                  amount: float, customer_reference: str = None) -> BankingEvent:
        """Create fund transfer event with idempotency key"""
        transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
        
        # Idempotency key based on business logic
        # Same transfer attempt should have same key
        idempotency_data = f"{from_account}:{to_account}:{amount}:{customer_reference or ''}"
        idempotency_key = hashlib.sha256(idempotency_data.encode()).hexdigest()[:32]
        
        event = BankingEvent(
            event_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            idempotency_key=idempotency_key,
            event_type="fund.transfer",
            account_from=from_account,
            account_to=to_account,
            amount=amount,
            reference=customer_reference
        )
        
        logger.info(f"📤 Created fund transfer event: {transaction_id}")
        logger.info(f"   🔑 Idempotency Key: {idempotency_key}")
        
        return event
    
    async def publish_event(self, event: BankingEvent):
        """Publish event to queue"""
        self.messages.append(event)
        logger.info(f"📡 Event published: {event.transaction_id}")
    
    def get_pending_messages(self) -> List[BankingEvent]:
        """Get all pending messages"""
        pending = self.messages[:]
        self.messages.clear()
        return pending

async def hdfc_exactly_once_demo():
    """HDFC exactly-once delivery demo"""
    print("🏦 HDFC Bank Exactly-Once Delivery Demo")
    print("=" * 50)
    print("📋 Make sure Redis is running on localhost:6379")
    print()
    
    # Initialize components
    idempotency_manager = IdempotencyManager()
    processor = ExactlyOnceProcessor(idempotency_manager)
    producer = MessageProducer()
    
    # Display initial account balances
    print("💰 Initial Account Balances:")
    for account, balance in processor.account_balances.items():
        print(f"   {account}: ₹{balance:,.2f}")
    print()
    
    # Create fund transfer events
    transfers = [
        ("HDFC_RAHUL_001", "HDFC_PRIYA_002", 25000.0, "Loan repayment"),
        ("HDFC_PRIYA_002", "HDFC_AMIT_003", 15000.0, "Birthday gift"),
        ("HDFC_AMIT_003", "HDFC_NEHA_004", 8000.0, "Rent payment"),
        ("HDFC_NEHA_004", "HDFC_RAHUL_001", 50000.0, "Investment"),
    ]
    
    events = []
    for from_acc, to_acc, amount, reference in transfers:
        event = producer.create_fund_transfer_event(from_acc, to_acc, amount, reference)
        await producer.publish_event(event)
        events.append(event)
    
    print("📤 Fund Transfer Events Created:")
    for event in events:
        print(f"   💸 {event.transaction_id}: ₹{event.amount} "
              f"{event.account_from} → {event.account_to}")
    print()
    
    # Process events normally
    print("⚙️ Processing Events (Normal Flow):")
    print("-" * 30)
    
    pending_messages = producer.get_pending_messages()
    successful_events = []
    
    for event in pending_messages:
        try:
            result = await processor.process_event(event)
            successful_events.append((event, result))
            print(f"✅ Processed: {event.transaction_id} - Ref: {result['transaction_ref']}")
        except Exception as e:
            print(f"❌ Failed: {event.transaction_id} - {e}")
    
    print()
    
    # Display updated balances
    print("💰 Updated Account Balances:")
    for account, balance in processor.account_balances.items():
        print(f"   {account}: ₹{balance:,.2f}")
    print()
    
    # Demonstrate exactly-once semantics with duplicates
    print("🔄 Exactly-Once Semantics Demo (Duplicate Events):")
    print("-" * 50)
    
    # Simulate duplicate events (network retry scenario)
    print("📡 Simulating duplicate events due to network retries...")
    
    duplicate_events = []
    for event, _ in successful_events[:2]:  # Take first 2 successful events
        # Create duplicate with same idempotency key
        duplicate = BankingEvent(
            event_id=str(uuid.uuid4()),  # Different event ID
            transaction_id=event.transaction_id,  # Same transaction ID
            idempotency_key=event.idempotency_key,  # SAME idempotency key
            event_type=event.event_type,
            account_from=event.account_from,
            account_to=event.account_to,
            amount=event.amount,
            reference=event.reference + " (RETRY)"
        )
        duplicate_events.append(duplicate)
    
    print(f"🔄 Processing {len(duplicate_events)} duplicate events...")
    
    for duplicate in duplicate_events:
        try:
            result = await processor.process_event(duplicate)
            print(f"🔄 Duplicate handled: {duplicate.transaction_id}")
            print(f"   ✅ Returned previous result: Ref {result['transaction_ref']}")
            print(f"   💡 No double processing occurred!")
        except Exception as e:
            print(f"❌ Duplicate processing failed: {duplicate.transaction_id} - {e}")
    
    print()
    
    # Verify balances unchanged
    print("💰 Final Account Balances (Should be unchanged from duplicates):")
    for account, balance in processor.account_balances.items():
        print(f"   {account}: ₹{balance:,.2f}")
    print()
    
    # Concurrent processing demo
    print("🏃‍♂️ Concurrent Processing Demo:")
    print("-" * 30)
    
    # Create new event for concurrent processing test
    concurrent_event = producer.create_fund_transfer_event(
        "HDFC_RAHUL_001", "HDFC_PRIYA_002", 5000.0, "Concurrent test"
    )
    
    print(f"🚀 Starting concurrent processing of: {concurrent_event.transaction_id}")
    
    # Start multiple processors concurrently (simulating multiple instances)
    async def concurrent_processor(processor_id: int, event: BankingEvent):
        try:
            logger.info(f"🔄 Processor {processor_id} starting...")
            result = await processor.process_event(event)
            logger.info(f"✅ Processor {processor_id} completed: {result['transaction_ref']}")
            return f"Processor {processor_id}", result
        except Exception as e:
            logger.info(f"❌ Processor {processor_id} failed: {e}")
            return f"Processor {processor_id}", None
    
    # Start 3 concurrent processors
    tasks = [
        concurrent_processor(1, concurrent_event),
        concurrent_processor(2, concurrent_event),
        concurrent_processor(3, concurrent_event)
    ]
    
    results = await asyncio.gather(*tasks)
    
    successful_processors = [r for r in results if r[1] is not None]
    failed_processors = [r for r in results if r[1] is None]
    
    print(f"✅ Successful processors: {len(successful_processors)}")
    print(f"❌ Failed processors: {len(failed_processors)} (expected - only one should succeed)")
    
    if successful_processors:
        winner, result = successful_processors[0]
        print(f"🏆 Winner: {winner} - Transaction Ref: {result['transaction_ref']}")
    
    print()
    
    # Statistics
    print("📊 Exactly-Once Statistics:")
    print("-" * 25)
    
    # Check idempotency manager stats
    all_keys = idempotency_manager.redis_client.keys(f"{idempotency_manager.key_prefix}:*")
    processing_keys = idempotency_manager.redis_client.keys(f"{idempotency_manager.processing_prefix}:*")
    
    print(f"   🔑 Total Idempotency Keys: {len(all_keys)}")
    print(f"   ⚙️ Currently Processing: {len(processing_keys)}")
    
    # Cleanup
    cleaned_count = idempotency_manager.cleanup_expired_processing()
    print(f"   🧹 Cleaned Expired Locks: {cleaned_count}")
    
    print()
    print("🎯 Key Benefits Demonstrated:")
    print("   ✅ No duplicate processing despite retries")
    print("   ✅ Concurrent processing protection")
    print("   ✅ Idempotency key-based deduplication")
    print("   ✅ Automatic cleanup of expired locks")
    print("   ✅ Fast duplicate detection with Redis")
    print("   ✅ Previous result caching for duplicates")

async def failure_recovery_demo():
    """Demonstrate failure recovery scenarios"""
    print("\n" + "="*50)
    print("🛠️ Failure Recovery Demo")
    print("="*50)
    
    idempotency_manager = IdempotencyManager()
    processor = ExactlyOnceProcessor(idempotency_manager)
    
    # Simulate a processing failure scenario
    print("💥 Simulating processing failure and recovery...")
    
    # Create event
    event = BankingEvent(
        event_id=str(uuid.uuid4()),
        transaction_id=f"TXN_FAIL_{uuid.uuid4().hex[:8].upper()}",
        idempotency_key=f"fail_test_{uuid.uuid4().hex[:16]}",
        event_type="fund.transfer",
        account_from="HDFC_RAHUL_001",
        account_to="HDFC_PRIYA_002",
        amount=1000.0
    )
    
    # Manually mark as processing (simulate crash during processing)
    await idempotency_manager.mark_processing(event.idempotency_key, asdict(event))
    print(f"🔒 Event marked as processing: {event.idempotency_key}")
    
    # Try to process (should detect ongoing processing)
    try:
        result = await processor.process_event(event)
        print(f"❓ Unexpected success: {result}")
    except Exception as e:
        print(f"⚠️ Expected failure: {e}")
    
    # Simulate expiry (cleanup processing lock)
    processing_key = f"{idempotency_manager.processing_prefix}:{event.idempotency_key}"
    idempotency_manager.redis_client.delete(processing_key)
    print("🧹 Simulated processing lock expiry")
    
    # Now retry should succeed
    try:
        result = await processor.process_event(event)
        print(f"✅ Recovery successful: {result['transaction_ref']}")
    except Exception as e:
        print(f"❌ Recovery failed: {e}")

if __name__ == "__main__":
    asyncio.run(hdfc_exactly_once_demo())
    asyncio.run(failure_recovery_demo())