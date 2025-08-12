#!/usr/bin/env python3
"""
Indian UPI Payment Event System
===============================
भारतीय UPI पेमेंट इवेंट सिस्टम

A complete event-driven payment processing system modeling UPI (Unified Payments Interface)
with NPCI, IMPS, and banking integration. This example demonstrates real-world event
patterns used in Indian fintech.

Features:
- UPI payment lifecycle events
- NPCI integration simulation
- IMPS settlement processing
- Banking validation events
- Fraud detection events
- Reconciliation events

Author: Hindi Podcast Series
Episode: 020 - Event-Driven Architecture
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
import logging
from collections import defaultdict
import hashlib

# Configure logging - लॉगिंग कॉन्फ़िगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status enum - पेमेंट स्टेटस"""
    INITIATED = "INITIATED"      # शुरू किया गया
    VALIDATED = "VALIDATED"      # सत्यापित
    PROCESSING = "PROCESSING"    # प्रसंस्करण में
    SETTLED = "SETTLED"          # निपटारा हो गया
    FAILED = "FAILED"           # असफल
    REVERSED = "REVERSED"       # वापस किया गया

class EventType(Enum):
    """Event types for UPI system - UPI सिस्टम के लिए इवेंट टाइप"""
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_VALIDATED = "payment.validated" 
    PAYMENT_PROCESSING = "payment.processing"
    PAYMENT_SETTLED = "payment.settled"
    PAYMENT_FAILED = "payment.failed"
    FRAUD_DETECTED = "fraud.detected"
    BALANCE_UPDATED = "balance.updated"
    NOTIFICATION_SENT = "notification.sent"
    RECONCILIATION_COMPLETE = "reconciliation.complete"

@dataclass
class PaymentEvent:
    """Base payment event class - बेस पेमेंट इवेंट क्लास"""
    event_id: str
    event_type: EventType
    transaction_id: str
    timestamp: str
    data: Dict
    correlation_id: str = None
    
    def to_json(self) -> str:
        """Convert to JSON - JSON में कन्वर्ट करें"""
        return json.dumps(asdict(self), default=str)

@dataclass
class UPIPayment:
    """UPI Payment details - UPI पेमेंट विवरण"""
    transaction_id: str
    payer_vpa: str          # Virtual Payment Address - वर्चुअल पेमेंट एड्रेस
    payee_vpa: str
    amount: float
    currency: str = "INR"
    purpose: str = "P2P"    # P2P, P2M, etc.
    bank_ref: str = None
    npci_ref: str = None
    status: PaymentStatus = PaymentStatus.INITIATED
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class EventBus:
    """Central event bus for payment system - पेमेंट सिस्टम के लिए केंद्रीय इवेंट बस"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_store: List[PaymentEvent] = []
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to event type - इवेंट टाइप को सब्स्क्राइब करें"""
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler for {event_type.value}")
        
    async def publish(self, event: PaymentEvent):
        """Publish event to subscribers - सब्स्क्राइबर्स को इवेंट पब्लिश करें"""
        self.event_store.append(event)
        logger.info(f"Published event: {event.event_type.value} for transaction {event.transaction_id}")
        
        # Notify all subscribers - सभी सब्स्क्राइबर्स को सूचित करें
        for handler in self.subscribers[event.event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type.value}: {e}")

class NPCIGateway:
    """NPCI (National Payments Corporation of India) Gateway simulation"""
    """NPCI (नेशनल पेमेंट्स कॉर्पोरेशन ऑफ इंडिया) गेटवे सिमुलेशन"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.processing_time = 0.5  # seconds - सेकंड्स में
        
    async def validate_payment(self, payment: UPIPayment) -> bool:
        """Validate payment with NPCI - NPCI के साथ पेमेंट सत्यापित करें"""
        logger.info(f"NPCI validating payment {payment.transaction_id}")
        
        # Simulate NPCI validation delay - NPCI सत्यापन देरी का सिमुलेशन
        await asyncio.sleep(self.processing_time)
        
        # Generate NPCI reference - NPCI रेफरेंस जेनरेट करें
        payment.npci_ref = f"NPCI{int(time.time())}{payment.transaction_id[:6]}"
        
        # 95% success rate simulation - 95% सफलता दर सिमुलेशन
        is_valid = hash(payment.transaction_id) % 100 < 95
        
        if is_valid:
            await self.event_bus.publish(PaymentEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.PAYMENT_VALIDATED,
                transaction_id=payment.transaction_id,
                timestamp=datetime.now().isoformat(),
                data={
                    "npci_ref": payment.npci_ref,
                    "validation_status": "SUCCESS",
                    "validation_time": self.processing_time
                }
            ))
            return True
        else:
            await self.event_bus.publish(PaymentEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.PAYMENT_FAILED,
                transaction_id=payment.transaction_id,
                timestamp=datetime.now().isoformat(),
                data={
                    "failure_reason": "NPCI_VALIDATION_FAILED",
                    "error_code": "U01"
                }
            ))
            return False

class BankingService:
    """Banking service for account operations - खाता संचालन के लिए बैंकिंग सेवा"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.account_balances = {
            "user123@paytm": 50000.0,    # Paytm wallet
            "user456@phonepe": 25000.0,  # PhonePe wallet
            "user789@gpay": 75000.0,     # Google Pay
        }
        
    async def check_balance(self, vpa: str, amount: float) -> bool:
        """Check if sufficient balance - पर्याप्त बैलेंस जांचें"""
        current_balance = self.account_balances.get(vpa, 0.0)
        return current_balance >= amount
        
    async def debit_account(self, vpa: str, amount: float, transaction_id: str):
        """Debit amount from account - खाते से राशि डेबिट करें"""
        if await self.check_balance(vpa, amount):
            self.account_balances[vpa] -= amount
            
            await self.event_bus.publish(PaymentEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.BALANCE_UPDATED,
                transaction_id=transaction_id,
                timestamp=datetime.now().isoformat(),
                data={
                    "vpa": vpa,
                    "operation": "DEBIT",
                    "amount": amount,
                    "new_balance": self.account_balances[vpa]
                }
            ))
            return True
        return False
        
    async def credit_account(self, vpa: str, amount: float, transaction_id: str):
        """Credit amount to account - खाते में राशि क्रेडिट करें"""
        if vpa not in self.account_balances:
            self.account_balances[vpa] = 0.0
            
        self.account_balances[vpa] += amount
        
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.BALANCE_UPDATED,
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            data={
                "vpa": vpa,
                "operation": "CREDIT", 
                "amount": amount,
                "new_balance": self.account_balances[vpa]
            }
        ))

class FraudDetectionService:
    """Fraud detection service - फ्रॉड डिटेक्शन सर्विस"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.transaction_history = defaultdict(list)
        self.velocity_limits = {
            "max_amount": 100000.0,      # Max transaction amount - अधिकतम लेन-देन राशि
            "max_daily_count": 20,       # Max transactions per day - दैनिक अधिकतम लेन-देन
            "max_daily_amount": 200000.0 # Max daily amount - दैनिक अधिकतम राशि
        }
        
    async def check_fraud_patterns(self, payment: UPIPayment) -> bool:
        """Check for fraud patterns - फ्रॉड पैटर्न की जांच करें"""
        payer_history = self.transaction_history[payment.payer_vpa]
        
        # Check amount limits - राशि सीमा जांचें
        if payment.amount > self.velocity_limits["max_amount"]:
            await self._report_fraud(payment, "AMOUNT_LIMIT_EXCEEDED")
            return True
            
        # Check daily transaction count - दैनिक लेन-देन संख्या जांचें
        today_transactions = [t for t in payer_history 
                            if t["date"] == datetime.now().date()]
        
        if len(today_transactions) >= self.velocity_limits["max_daily_count"]:
            await self._report_fraud(payment, "DAILY_COUNT_EXCEEDED")
            return True
            
        # Check daily amount limit - दैनिक राशि सीमा जांचें
        daily_amount = sum(t["amount"] for t in today_transactions)
        if daily_amount + payment.amount > self.velocity_limits["max_daily_amount"]:
            await self._report_fraud(payment, "DAILY_AMOUNT_EXCEEDED") 
            return True
            
        # Record transaction for future checks - भविष्य की जांच के लिए लेन-देन रिकॉर्ड करें
        payer_history.append({
            "transaction_id": payment.transaction_id,
            "amount": payment.amount,
            "date": datetime.now().date(),
            "timestamp": datetime.now()
        })
        
        return False
        
    async def _report_fraud(self, payment: UPIPayment, reason: str):
        """Report fraud detection - फ्रॉड डिटेक्शन रिपोर्ट करें"""
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.FRAUD_DETECTED,
            transaction_id=payment.transaction_id,
            timestamp=datetime.now().isoformat(),
            data={
                "fraud_reason": reason,
                "payer_vpa": payment.payer_vpa,
                "amount": payment.amount,
                "risk_score": 0.9
            }
        ))

class NotificationService:
    """Notification service for SMS/Push notifications"""
    """SMS/पुश नोटिफिकेशन के लिए नोटिफिकेशन सेवा"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
    async def send_notification(self, vpa: str, message: str, transaction_id: str):
        """Send notification to user - यूजर को नोटिफिकेशन भेजें"""
        # Simulate SMS/Push notification - SMS/पुश नोटिफिकेशन का सिमुलेशन
        logger.info(f"📱 Notification sent to {vpa}: {message}")
        
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.NOTIFICATION_SENT,
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            data={
                "vpa": vpa,
                "message": message,
                "channel": "SMS_AND_PUSH"
            }
        ))

class IMPSSettlementService:
    """IMPS (Immediate Payment Service) Settlement Service"""
    """IMPS (तत्काल भुगतान सेवा) निपटारा सेवा"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.settlement_batch = []
        self.batch_size = 100
        
    async def add_to_settlement(self, payment: UPIPayment):
        """Add payment to settlement batch - निपटारा बैच में पेमेंट जोड़ें"""
        self.settlement_batch.append(payment)
        
        # Process batch when full - बैच भरने पर प्रक्रिया करें
        if len(self.settlement_batch) >= self.batch_size:
            await self.process_settlement_batch()
            
    async def process_settlement_batch(self):
        """Process settlement batch - निपटारा बैच की प्रक्रिया करें"""
        if not self.settlement_batch:
            return
            
        batch_id = str(uuid.uuid4())
        total_amount = sum(p.amount for p in self.settlement_batch)
        
        logger.info(f"Processing IMPS settlement batch {batch_id} with {len(self.settlement_batch)} transactions")
        
        # Simulate settlement processing - निपटारा प्रक्रिया का सिमुलेशन
        await asyncio.sleep(2.0)
        
        for payment in self.settlement_batch:
            await self.event_bus.publish(PaymentEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.PAYMENT_SETTLED,
                transaction_id=payment.transaction_id,
                timestamp=datetime.now().isoformat(),
                data={
                    "settlement_batch_id": batch_id,
                    "imps_ref": f"IMPS{int(time.time())}{payment.transaction_id[:6]}",
                    "settlement_amount": payment.amount
                }
            ))
            
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.RECONCILIATION_COMPLETE,
            transaction_id=batch_id,
            timestamp=datetime.now().isoformat(),
            data={
                "batch_id": batch_id,
                "transaction_count": len(self.settlement_batch),
                "total_amount": total_amount,
                "settlement_type": "IMPS_BATCH"
            }
        ))
        
        # Clear batch - बैच साफ़ करें
        self.settlement_batch.clear()

class UPIPaymentProcessor:
    """Main UPI Payment Processor - मुख्य UPI पेमेंट प्रोसेसर"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.npci_gateway = NPCIGateway(self.event_bus)
        self.banking_service = BankingService(self.event_bus)
        self.fraud_service = FraudDetectionService(self.event_bus)
        self.notification_service = NotificationService(self.event_bus)
        self.settlement_service = IMPSSettlementService(self.event_bus)
        
        # Payment tracking - पेमेंट ट्रैकिंग
        self.payments: Dict[str, UPIPayment] = {}
        
        # Setup event handlers - इवेंट हैंडलर सेटअप करें
        self._setup_event_handlers()
        
    def _setup_event_handlers(self):
        """Setup event handlers - इवेंट हैंडलर सेटअप करें"""
        
        async def handle_payment_validated(event: PaymentEvent):
            """Handle payment validation - पेमेंट सत्यापन हैंडल करें"""
            payment = self.payments[event.transaction_id]
            payment.status = PaymentStatus.VALIDATED
            
            # Check for fraud - फ्रॉड की जांच करें
            is_fraud = await self.fraud_service.check_fraud_patterns(payment)
            if not is_fraud:
                await self._process_payment(payment)
                
        async def handle_payment_processing(event: PaymentEvent):
            """Handle payment processing - पेमेंट प्रोसेसिंग हैंडल करें"""
            payment = self.payments[event.transaction_id]
            
            # Debit payer account - भुगतानकर्ता का खाता डेबिट करें
            debit_success = await self.banking_service.debit_account(
                payment.payer_vpa, payment.amount, payment.transaction_id
            )
            
            if debit_success:
                # Credit payee account - प्राप्तकर्ता का खाता क्रेडिट करें
                await self.banking_service.credit_account(
                    payment.payee_vpa, payment.amount, payment.transaction_id
                )
                
                # Add to settlement - निपटारे में जोड़ें
                await self.settlement_service.add_to_settlement(payment)
            else:
                payment.status = PaymentStatus.FAILED
                await self.event_bus.publish(PaymentEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.PAYMENT_FAILED,
                    transaction_id=payment.transaction_id,
                    timestamp=datetime.now().isoformat(),
                    data={"failure_reason": "INSUFFICIENT_BALANCE"}
                ))
                
        async def handle_payment_settled(event: PaymentEvent):
            """Handle payment settlement - पेमेंट निपटारा हैंडल करें"""
            payment = self.payments[event.transaction_id]
            payment.status = PaymentStatus.SETTLED
            
            # Send success notifications - सफलता नोटिफिकेशन भेजें
            await self.notification_service.send_notification(
                payment.payer_vpa,
                f"Payment of ₹{payment.amount} sent successfully to {payment.payee_vpa}",
                payment.transaction_id
            )
            
            await self.notification_service.send_notification(
                payment.payee_vpa,
                f"Payment of ₹{payment.amount} received from {payment.payer_vpa}",
                payment.transaction_id
            )
            
        async def handle_fraud_detected(event: PaymentEvent):
            """Handle fraud detection - फ्रॉड डिटेक्शन हैंडल करें"""
            payment = self.payments[event.transaction_id]
            payment.status = PaymentStatus.FAILED
            
            # Send fraud alert - फ्रॉड अलर्ट भेजें
            await self.notification_service.send_notification(
                payment.payer_vpa,
                f"⚠️ Suspicious transaction blocked for security reasons",
                payment.transaction_id
            )
            
        # Subscribe to events - इवेंट्स को सब्स्क्राइब करें
        self.event_bus.subscribe(EventType.PAYMENT_VALIDATED, handle_payment_validated)
        self.event_bus.subscribe(EventType.PAYMENT_PROCESSING, handle_payment_processing)
        self.event_bus.subscribe(EventType.PAYMENT_SETTLED, handle_payment_settled)
        self.event_bus.subscribe(EventType.FRAUD_DETECTED, handle_fraud_detected)
        
    async def initiate_payment(self, payer_vpa: str, payee_vpa: str, 
                              amount: float, purpose: str = "P2P") -> str:
        """Initiate UPI payment - UPI पेमेंट शुरू करें"""
        
        # Create payment object - पेमेंट ऑब्जेक्ट बनाएं
        payment = UPIPayment(
            transaction_id=str(uuid.uuid4()),
            payer_vpa=payer_vpa,
            payee_vpa=payee_vpa,
            amount=amount,
            purpose=purpose
        )
        
        self.payments[payment.transaction_id] = payment
        
        # Publish initiation event - प्रारंभ इवेंट पब्लिश करें
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PAYMENT_INITIATED,
            transaction_id=payment.transaction_id,
            timestamp=datetime.now().isoformat(),
            data={
                "payer_vpa": payer_vpa,
                "payee_vpa": payee_vpa,
                "amount": amount,
                "purpose": purpose
            }
        ))
        
        # Start validation with NPCI - NPCI के साथ सत्यापन शुरू करें
        await self.npci_gateway.validate_payment(payment)
        
        return payment.transaction_id
        
    async def _process_payment(self, payment: UPIPayment):
        """Process validated payment - सत्यापित पेमेंट की प्रक्रिया करें"""
        payment.status = PaymentStatus.PROCESSING
        
        await self.event_bus.publish(PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PAYMENT_PROCESSING,
            transaction_id=payment.transaction_id,
            timestamp=datetime.now().isoformat(),
            data={
                "processing_started": True,
                "npci_ref": payment.npci_ref
            }
        ))
        
    def get_payment_status(self, transaction_id: str) -> Optional[PaymentStatus]:
        """Get payment status - पेमेंट स्टेटस प्राप्त करें"""
        payment = self.payments.get(transaction_id)
        return payment.status if payment else None
        
    def get_account_balance(self, vpa: str) -> float:
        """Get account balance - खाता शेष राशि प्राप्त करें"""
        return self.banking_service.account_balances.get(vpa, 0.0)

async def demonstrate_upi_system():
    """Demonstrate UPI payment system - UPI पेमेंट सिस्टम का प्रदर्शन"""
    
    print("🚀 Starting UPI Payment System Demo")
    print("🚀 UPI पेमेंट सिस्टम डेमो शुरू कर रहे हैं\n")
    
    # Initialize payment processor - पेमेंट प्रोसेसर इनिशियलाइज़ करें
    processor = UPIPaymentProcessor()
    
    # Show initial balances - प्रारंभिक शेष राशि दिखाएं
    print("💰 Initial Account Balances - प्रारंभिक खाता शेष राशि:")
    for vpa in ["user123@paytm", "user456@phonepe", "user789@gpay"]:
        balance = processor.get_account_balance(vpa)
        print(f"   {vpa}: ₹{balance:,.2f}")
    print()
    
    # Test scenarios - टेस्ट परिदृश्य
    test_payments = [
        ("user123@paytm", "user456@phonepe", 5000.0, "Dinner payment - खाना का भुगतान"),
        ("user456@phonepe", "user789@gpay", 15000.0, "Rent payment - किराया भुगतान"),
        ("user789@gpay", "user123@paytm", 2500.0, "Movie tickets - मूवी टिकट"),
        ("user123@paytm", "merchant@swiggy", 850.0, "Food order - खाना ऑर्डर"),
        ("user123@paytm", "user456@phonepe", 150000.0, "High amount (should trigger fraud) - अधिक राशि (फ्रॉड ट्रिगर होना चाहिए)")
    ]
    
    transaction_ids = []
    
    # Process payments - पेमेंट प्रोसेस करें
    for payer, payee, amount, description in test_payments:
        print(f"💳 Initiating payment: {description}")
        print(f"   From: {payer} → To: {payee} → Amount: ₹{amount:,.2f}")
        
        try:
            txn_id = await processor.initiate_payment(payer, payee, amount)
            transaction_ids.append(txn_id)
            print(f"   Transaction ID: {txn_id[:8]}...")
            
            # Wait for processing - प्रसंस्करण की प्रतीक्षा करें
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Wait for all processing to complete - सभी प्रसंस्करण पूरा होने की प्रतीक्षा करें
    print("⏳ Waiting for all transactions to complete...")
    print("⏳ सभी लेन-देन पूरे होने की प्रतीक्षा कर रहे हैं...")
    await asyncio.sleep(3)
    
    # Show final balances - अंतिम शेष राशि दिखाएं
    print("\n💰 Final Account Balances - अंतिम खाता शेष राशि:")
    for vpa in ["user123@paytm", "user456@phonepe", "user789@gpay", "merchant@swiggy"]:
        balance = processor.get_account_balance(vpa)
        print(f"   {vpa}: ₹{balance:,.2f}")
    
    # Show transaction statuses - लेन-देन स्थिति दिखाएं
    print("\n📊 Transaction Status Summary - लेन-देन स्थिति सारांश:")
    for i, txn_id in enumerate(transaction_ids):
        status = processor.get_payment_status(txn_id)
        payment = processor.payments.get(txn_id)
        if payment:
            print(f"   {i+1}. {txn_id[:8]}: {status.value} (₹{payment.amount:,.2f})")
    
    # Show event statistics - इवेंट आंकड़े दिखाएं
    print(f"\n📈 Event Statistics - इवेंट आंकड़े:")
    print(f"   Total Events Published: {len(processor.event_bus.event_store)}")
    
    event_counts = defaultdict(int)
    for event in processor.event_bus.event_store:
        event_counts[event.event_type] += 1
    
    for event_type, count in event_counts.items():
        print(f"   {event_type.value}: {count}")
    
    print("\n✅ UPI Payment System Demo Complete!")
    print("✅ UPI पेमेंट सिस्टम डेमो पूरा हुआ!")

if __name__ == "__main__":
    """
    Run the UPI payment system demonstration
    UPI पेमेंट सिस्टम प्रदर्शन चलाएं
    
    This demonstrates:
    यह प्रदर्शित करता है:
    
    1. Event-driven payment processing - इवेंट-संचालित पेमेंट प्रोसेसिंग
    2. NPCI integration simulation - NPCI इंटीग्रेशन सिमुलेशन
    3. Banking operations (debit/credit) - बैंकिंग ऑपरेशन (डेबिट/क्रेडिट)
    4. Fraud detection patterns - फ्रॉड डिटेक्शन पैटर्न
    5. IMPS settlement processing - IMPS निपटारा प्रसंस्करण
    6. Real-time notifications - रियल-टाइम नोटिफिकेशन
    7. Event sourcing and CQRS patterns - इवेंट सोर्सिंग और CQRS पैटर्न
    
    Key learnings:
    मुख्य सीख:
    
    - Event-driven architecture enables loose coupling - इवेंट-संचालित आर्किटेक्चर loose coupling सक्षम बनाता है
    - Asynchronous processing improves performance - असिंक्रोनस प्रसंस्करण प्रदर्शन में सुधार करता है
    - Event sourcing provides complete audit trail - इवेंट सोर्सिंग पूर्ण ऑडिट ट्रेल प्रदान करता है
    - Real-time fraud detection prevents losses - रियल-टाइम फ्रॉड डिटेक्शन नुकसान रोकता है
    - Batch processing optimizes settlement costs - बैच प्रसंस्करण निपटारा लागत अनुकूलित करता है
    """
    
    try:
        asyncio.run(demonstrate_upi_system())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user - डेमो उपयोगकर्ता द्वारा बाधित")
    except Exception as e:
        print(f"\n❌ Demo failed with error - डेमो त्रुटि के साथ असफल: {e}")
        raise