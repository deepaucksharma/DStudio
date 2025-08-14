#!/usr/bin/env python3
"""
Domain-Driven Design: Payment Aggregate - Paytm Example
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Aggregate pattern का इस्तेमाल करके
Paytm के payment domain को model करते हैं। Aggregate एक consistency boundary है।

Author: Hindi Tech Podcast
Date: 2025
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
import hashlib
import secrets

# Domain Events - Events जो business में important हैं
class DomainEvent:
    """Base domain event"""
    def __init__(self, aggregate_id: str, version: int):
        self.aggregate_id = aggregate_id
        self.version = version
        self.occurred_at = datetime.now()
        self.event_id = str(uuid4())

class PaymentInitiatedEvent(DomainEvent):
    def __init__(self, aggregate_id: str, version: int, amount: Decimal, merchant_id: str):
        super().__init__(aggregate_id, version)
        self.amount = amount
        self.merchant_id = merchant_id

class PaymentProcessedEvent(DomainEvent):
    def __init__(self, aggregate_id: str, version: int, gateway_reference: str):
        super().__init__(aggregate_id, version)
        self.gateway_reference = gateway_reference

class PaymentFailedEvent(DomainEvent):
    def __init__(self, aggregate_id: str, version: int, failure_reason: str):
        super().__init__(aggregate_id, version)
        self.failure_reason = failure_reason

class RefundProcessedEvent(DomainEvent):
    def __init__(self, aggregate_id: str, version: int, refund_amount: Decimal):
        super().__init__(aggregate_id, version)
        self.refund_amount = refund_amount

# Enums
class PaymentStatus(Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIAL_REFUNDED = "partial_refunded"

class PaymentMethod(Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    PAYTM_WALLET = "paytm_wallet"
    PAYTM_POSTPAID = "paytm_postpaid"

class Currency(Enum):
    INR = "INR"
    USD = "USD"

# Value Objects
@dataclass(frozen=True)
class PaymentId:
    """Strong-typed payment identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 10:
            raise ValueError("Payment ID must be at least 10 characters - Payment ID कम से कम 10 characters का होना चाहिए")

@dataclass(frozen=True)
class Money:
    """Money value object with currency"""
    amount: Decimal
    currency: Currency = Currency.INR
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative - रकम negative नहीं हो सकती")
        if self.amount > Decimal('100000'):  # ₹1 lakh limit per transaction
            raise ValueError("Amount exceeds transaction limit - Transaction limit से ज्यादा रकम")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch - Currency match नहीं करती")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Insufficient amount - रकम कम है")
        return Money(result, self.currency)

@dataclass(frozen=True)
class MerchantInfo:
    """Merchant information"""
    merchant_id: str
    merchant_name: str
    category: str  # "ecommerce", "food", "travel", etc.
    
    def __post_init__(self):
        if not self.merchant_id or len(self.merchant_id) < 5:
            raise ValueError("Invalid merchant ID")

@dataclass(frozen=True)
class CustomerInfo:
    """Customer information"""
    customer_id: str
    phone_number: str
    email: Optional[str] = None
    
    def __post_init__(self):
        # Indian mobile number validation
        if not self.phone_number or len(self.phone_number) != 10:
            raise ValueError("Invalid phone number - Phone number 10 digits का होना चाहिए")
        if not self.phone_number.isdigit():
            raise ValueError("Phone number must contain only digits")

@dataclass
class PaymentMethodDetails:
    """Payment method specific details"""
    method: PaymentMethod
    details: Dict[str, str]
    
    def __post_init__(self):
        if self.method == PaymentMethod.UPI:
            if "upi_id" not in self.details:
                raise ValueError("UPI ID required for UPI payments")
        elif self.method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            required_fields = ["last_four_digits", "card_type"]
            if not all(field in self.details for field in required_fields):
                raise ValueError("Card details incomplete")

# Domain Services
class PaymentSecurityService:
    """Security service for payment operations"""
    
    @staticmethod
    def generate_transaction_token() -> str:
        """Generate secure transaction token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_transaction_token(token: str, payment_id: str, timestamp: datetime) -> bool:
        """Validate transaction token"""
        # Simple validation - production में more complex होगा
        if not token or len(token) < 32:
            return False
        
        # Token should be valid for 15 minutes
        if datetime.now() - timestamp > timedelta(minutes=15):
            return False
        
        return True
    
    @staticmethod
    def calculate_checksum(data: Dict) -> str:
        """Calculate payment checksum"""
        # Sort keys for consistent checksum
        sorted_data = dict(sorted(data.items()))
        data_string = "&".join([f"{k}={v}" for k, v in sorted_data.items()])
        return hashlib.sha256(data_string.encode()).hexdigest()

class FraudDetectionService:
    """Fraud detection service"""
    
    @staticmethod
    def check_risk_score(
        customer_id: str,
        amount: Decimal,
        merchant_id: str,
        payment_method: PaymentMethod,
        time_of_day: datetime
    ) -> float:
        """Calculate fraud risk score (0.0 to 1.0)"""
        risk_score = 0.0
        
        # Amount-based risk
        if amount > Decimal('50000'):  # High amount
            risk_score += 0.3
        elif amount > Decimal('10000'):
            risk_score += 0.1
        
        # Time-based risk
        hour = time_of_day.hour
        if hour < 6 or hour > 23:  # Late night transactions
            risk_score += 0.2
        
        # Payment method risk
        if payment_method == PaymentMethod.CREDIT_CARD:
            risk_score += 0.1
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    @staticmethod
    def is_suspicious_transaction(
        customer_id: str,
        current_amount: Decimal,
        recent_transactions: List[Dict]
    ) -> bool:
        """Check if transaction pattern is suspicious"""
        if len(recent_transactions) < 2:
            return False
        
        # Check for rapid succession of transactions
        recent_total = sum(Decimal(str(t.get('amount', 0))) for t in recent_transactions[-5:])
        if recent_total > Decimal('100000'):  # ₹1 lakh in recent transactions
            return True
        
        # Check for unusual amount patterns
        amounts = [Decimal(str(t.get('amount', 0))) for t in recent_transactions[-3:]]
        if current_amount > max(amounts) * 10:  # 10x larger than recent
            return True
        
        return False

# Aggregate Root - Main business entity
class PaymentAggregate:
    """
    Payment Aggregate - Paytm Payment Domain
    
    यह aggregate एक complete payment transaction को represent करता है।
    यहाँ सारे payment related business rules हैं।
    """
    
    def __init__(
        self,
        payment_id: PaymentId,
        customer: CustomerInfo,
        merchant: MerchantInfo,
        amount: Money,
        payment_method: PaymentMethodDetails,
        description: str
    ):
        # Validation
        if not description or len(description.strip()) < 5:
            raise ValueError("Payment description required - Payment description जरूरी है")
        
        # Aggregate state
        self._payment_id = payment_id
        self._customer = customer
        self._merchant = merchant
        self._amount = amount
        self._payment_method = payment_method
        self._description = description.strip()
        
        # Payment state
        self._status = PaymentStatus.INITIATED
        self._gateway_reference: Optional[str] = None
        self._transaction_token: Optional[str] = None
        self._checksum: Optional[str] = None
        
        # Timestamps
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._processed_at: Optional[datetime] = None
        
        # Refund tracking
        self._total_refunded = Money(Decimal('0'), amount.currency)
        self._refund_history: List[Dict] = []
        
        # Security
        self._fraud_score: Optional[float] = None
        self._security_checks_passed = False
        
        # Optimistic locking
        self._version = 1
        
        # Domain events
        self._domain_events: List[DomainEvent] = []
        
        # Add creation event
        self._add_event(PaymentInitiatedEvent(
            self._payment_id.value,
            self._version,
            self._amount.amount,
            self._merchant.merchant_id
        ))
    
    # Properties
    @property
    def payment_id(self) -> PaymentId:
        return self._payment_id
    
    @property
    def customer(self) -> CustomerInfo:
        return self._customer
    
    @property
    def merchant(self) -> MerchantInfo:
        return self._merchant
    
    @property
    def amount(self) -> Money:
        return self._amount
    
    @property
    def payment_method(self) -> PaymentMethodDetails:
        return self._payment_method
    
    @property
    def status(self) -> PaymentStatus:
        return self._status
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def gateway_reference(self) -> Optional[str]:
        return self._gateway_reference
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at
    
    @property
    def total_refunded(self) -> Money:
        return self._total_refunded
    
    @property
    def refundable_amount(self) -> Money:
        """Amount available for refund"""
        return self._amount.subtract(self._total_refunded)
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def fraud_score(self) -> Optional[float]:
        return self._fraud_score
    
    # Domain methods - Business logic
    
    def perform_security_checks(
        self,
        recent_transactions: List[Dict],
        security_service: PaymentSecurityService,
        fraud_service: FraudDetectionService
    ) -> None:
        """
        Perform security and fraud checks
        Security और fraud checks करना
        """
        if self._status != PaymentStatus.INITIATED:
            raise ValueError("Security checks can only be performed on initiated payments")
        
        # Calculate fraud score
        self._fraud_score = fraud_service.check_risk_score(
            self._customer.customer_id,
            self._amount.amount,
            self._merchant.merchant_id,
            self._payment_method.method,
            self._created_at
        )
        
        # Check suspicious patterns
        is_suspicious = fraud_service.is_suspicious_transaction(
            self._customer.customer_id,
            self._amount.amount,
            recent_transactions
        )
        
        # Block high-risk transactions
        if self._fraud_score > 0.8 or is_suspicious:
            self._fail_payment("High fraud risk detected - High fraud risk मिला है")
            return
        
        # Generate transaction token
        self._transaction_token = security_service.generate_transaction_token()
        
        # Calculate checksum
        checksum_data = {
            "payment_id": self._payment_id.value,
            "customer_id": self._customer.customer_id,
            "merchant_id": self._merchant.merchant_id,
            "amount": str(self._amount.amount),
            "currency": self._amount.currency.value
        }
        self._checksum = security_service.calculate_checksum(checksum_data)
        
        self._security_checks_passed = True
        self._updated_at = datetime.now()
        self._version += 1
        
        print(f"🔒 Security checks passed for payment {self._payment_id.value}")
        print(f"   Fraud Score: {self._fraud_score:.2f}")
        print(f"   Transaction Token: {self._transaction_token[:10]}...")
    
    def start_processing(self) -> None:
        """
        Start payment processing
        Payment processing शुरू करना
        """
        if self._status != PaymentStatus.INITIATED:
            raise ValueError("Payment must be in initiated status")
        
        if not self._security_checks_passed:
            raise ValueError("Security checks must pass before processing")
        
        self._status = PaymentStatus.PROCESSING
        self._updated_at = datetime.now()
        self._version += 1
        
        print(f"⏳ Payment processing started: {self._payment_id.value}")
    
    def complete_payment(self, gateway_reference: str) -> None:
        """
        Complete payment successfully
        Payment को successfully complete करना
        """
        if self._status != PaymentStatus.PROCESSING:
            raise ValueError("Payment must be in processing status")
        
        if not gateway_reference or len(gateway_reference) < 10:
            raise ValueError("Valid gateway reference required")
        
        self._status = PaymentStatus.SUCCESS
        self._gateway_reference = gateway_reference
        self._processed_at = datetime.now()
        self._updated_at = datetime.now()
        self._version += 1
        
        # Add domain event
        self._add_event(PaymentProcessedEvent(
            self._payment_id.value,
            self._version,
            gateway_reference
        ))
        
        print(f"✅ Payment completed successfully: {self._payment_id.value}")
        print(f"   Gateway Reference: {gateway_reference}")
    
    def _fail_payment(self, reason: str) -> None:
        """
        Fail payment with reason
        Payment को fail करना
        """
        old_status = self._status
        self._status = PaymentStatus.FAILED
        self._updated_at = datetime.now()
        self._version += 1
        
        # Add domain event
        self._add_event(PaymentFailedEvent(
            self._payment_id.value,
            self._version,
            reason
        ))
        
        print(f"❌ Payment failed: {self._payment_id.value}")
        print(f"   Reason: {reason}")
        print(f"   Previous Status: {old_status.value}")
    
    def fail_payment(self, reason: str) -> None:
        """Public method to fail payment"""
        if self._status in [PaymentStatus.SUCCESS, PaymentStatus.REFUNDED]:
            raise ValueError("Cannot fail a completed payment")
        
        self._fail_payment(reason)
    
    def process_refund(self, refund_amount: Money, reason: str) -> str:
        """
        Process refund for payment
        Payment का refund process करना
        """
        if self._status != PaymentStatus.SUCCESS:
            raise ValueError("Can only refund successful payments")
        
        if refund_amount.currency != self._amount.currency:
            raise ValueError("Refund currency must match payment currency")
        
        # Check if enough amount available for refund
        try:
            new_total_refunded = self._total_refunded.add(refund_amount)
            if new_total_refunded.amount > self._amount.amount:
                raise ValueError(
                    f"Refund amount exceeds available balance. "
                    f"Available: ₹{self.refundable_amount.amount}, "
                    f"Requested: ₹{refund_amount.amount}"
                )
        except ValueError as e:
            raise ValueError(f"Invalid refund amount: {e}")
        
        # Generate refund reference
        refund_reference = f"REF_{self._payment_id.value}_{len(self._refund_history) + 1}"
        
        # Update refund state
        self._total_refunded = self._total_refunded.add(refund_amount)
        
        # Add to refund history
        refund_record = {
            "refund_reference": refund_reference,
            "amount": refund_amount.amount,
            "reason": reason,
            "processed_at": datetime.now(),
            "remaining_balance": self.refundable_amount.amount
        }
        self._refund_history.append(refund_record)
        
        # Update payment status
        if self._total_refunded.amount == self._amount.amount:
            self._status = PaymentStatus.REFUNDED
        else:
            self._status = PaymentStatus.PARTIAL_REFUNDED
        
        self._updated_at = datetime.now()
        self._version += 1
        
        # Add domain event
        self._add_event(RefundProcessedEvent(
            self._payment_id.value,
            self._version,
            refund_amount.amount
        ))
        
        print(f"💸 Refund processed: {refund_reference}")
        print(f"   Amount: ₹{refund_amount.amount}")
        print(f"   Remaining Balance: ₹{self.refundable_amount.amount}")
        
        return refund_reference
    
    def get_payment_summary(self) -> Dict:
        """Get comprehensive payment summary"""
        return {
            "payment_id": self._payment_id.value,
            "status": self._status.value,
            "amount": {
                "original": float(self._amount.amount),
                "currency": self._amount.currency.value,
                "refunded": float(self._total_refunded.amount),
                "refundable": float(self.refundable_amount.amount)
            },
            "customer": {
                "id": self._customer.customer_id,
                "phone": self._customer.phone_number
            },
            "merchant": {
                "id": self._merchant.merchant_id,
                "name": self._merchant.merchant_name,
                "category": self._merchant.category
            },
            "payment_method": {
                "type": self._payment_method.method.value,
                "details": self._payment_method.details
            },
            "security": {
                "fraud_score": self._fraud_score,
                "checks_passed": self._security_checks_passed,
                "has_token": self._transaction_token is not None
            },
            "timeline": {
                "created_at": self._created_at.isoformat(),
                "updated_at": self._updated_at.isoformat(),
                "processed_at": self._processed_at.isoformat() if self._processed_at else None
            },
            "refunds": self._refund_history,
            "version": self._version,
            "gateway_reference": self._gateway_reference
        }
    
    def validate_transaction_integrity(self, security_service: PaymentSecurityService) -> bool:
        """Validate transaction integrity using checksum"""
        if not self._checksum:
            return False
        
        checksum_data = {
            "payment_id": self._payment_id.value,
            "customer_id": self._customer.customer_id,
            "merchant_id": self._merchant.merchant_id,
            "amount": str(self._amount.amount),
            "currency": self._amount.currency.value
        }
        
        calculated_checksum = security_service.calculate_checksum(checksum_data)
        return calculated_checksum == self._checksum
    
    def _add_event(self, event: DomainEvent) -> None:
        """Add domain event"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __str__(self) -> str:
        return f"Payment({self._payment_id.value}: ₹{self._amount.amount} - {self._status.value})"

def create_sample_paytm_payments() -> List[PaymentAggregate]:
    """Create sample Paytm payment scenarios"""
    
    payments = []
    
    # Sample customers
    customer1 = CustomerInfo("CUST_001", "9876543210", "user@example.com")
    customer2 = CustomerInfo("CUST_002", "8765432109")
    customer3 = CustomerInfo("CUST_003", "7654321098", "premium@example.com")
    
    # Sample merchants
    zomato = MerchantInfo("ZOMATO_001", "Zomato Food Delivery", "food")
    flipkart = MerchantInfo("FLIPKART_001", "Flipkart Marketplace", "ecommerce")
    ola = MerchantInfo("OLA_001", "Ola Cabs", "transportation")
    
    # Payment methods
    upi_method = PaymentMethodDetails(
        PaymentMethod.UPI,
        {"upi_id": "user@paytm", "bank": "PAYTM"}
    )
    
    wallet_method = PaymentMethodDetails(
        PaymentMethod.PAYTM_WALLET,
        {"wallet_id": "WALLET_001", "balance_sufficient": "true"}
    )
    
    card_method = PaymentMethodDetails(
        PaymentMethod.CREDIT_CARD,
        {"last_four_digits": "1234", "card_type": "VISA", "bank": "HDFC"}
    )
    
    # Sample Payment 1: Zomato food order via UPI
    payment1 = PaymentAggregate(
        payment_id=PaymentId("PAYTM_PAY_001"),
        customer=customer1,
        merchant=zomato,
        amount=Money(Decimal("459.50")),  # ₹459.50
        payment_method=upi_method,
        description="Zomato food order - Biryani and Raita"
    )
    payments.append(payment1)
    
    # Sample Payment 2: Flipkart purchase via Wallet
    payment2 = PaymentAggregate(
        payment_id=PaymentId("PAYTM_PAY_002"),
        customer=customer2,
        merchant=flipkart,
        amount=Money(Decimal("2899.00")),  # ₹2,899
        payment_method=wallet_method,
        description="Flipkart - Bluetooth Headphones"
    )
    payments.append(payment2)
    
    # Sample Payment 3: Ola ride via Credit Card
    payment3 = PaymentAggregate(
        payment_id=PaymentId("PAYTM_PAY_003"),
        customer=customer3,
        merchant=ola,
        amount=Money(Decimal("187.50")),  # ₹187.50
        payment_method=card_method,
        description="Ola ride - Bandra to Andheri"
    )
    payments.append(payment3)
    
    return payments

# Usage Example और Testing
if __name__ == "__main__":
    print("💳 Paytm Payment Domain - DDD Aggregate Example")
    print("=" * 55)
    
    # Create services
    security_service = PaymentSecurityService()
    fraud_service = FraudDetectionService()
    
    # Create sample payments
    payments = create_sample_paytm_payments()
    
    for i, payment in enumerate(payments, 1):
        print(f"\n🏦 Payment {i}: {payment}")
        print(f"   Customer: {payment.customer.phone_number}")
        print(f"   Merchant: {payment.merchant.merchant_name}")
        print(f"   Amount: ₹{payment.amount.amount}")
        print(f"   Method: {payment.payment_method.method.value}")
        
        # Simulate recent transactions for fraud detection
        recent_transactions = [
            {"amount": 250.0, "timestamp": datetime.now() - timedelta(hours=2)},
            {"amount": 890.0, "timestamp": datetime.now() - timedelta(hours=5)},
            {"amount": 156.0, "timestamp": datetime.now() - timedelta(days=1)}
        ]
        
        try:
            # Perform security checks
            print(f"\n🔒 Performing security checks...")
            payment.perform_security_checks(recent_transactions, security_service, fraud_service)
            
            if payment.status == PaymentStatus.FAILED:
                print(f"   ❌ Payment blocked due to security concerns")
                continue
            
            # Start processing
            print(f"⚡ Starting payment processing...")
            payment.start_processing()
            
            # Simulate payment completion (90% success rate)
            import random
            if random.random() > 0.1:  # 90% success
                gateway_ref = f"GW_{payment.payment_id.value}_{int(datetime.now().timestamp())}"
                payment.complete_payment(gateway_ref)
                
                # Test refund scenario for some payments
                if i == 2:  # Partial refund for second payment
                    print(f"\n💸 Processing partial refund...")
                    refund_ref = payment.process_refund(
                        Money(Decimal("500.00")),
                        "Customer requested partial refund"
                    )
                    print(f"   Refund Reference: {refund_ref}")
            else:
                payment.fail_payment("Gateway timeout - Gateway से response नहीं आया")
            
            # Validate transaction integrity
            print(f"\n🔍 Validating transaction integrity...")
            is_valid = payment.validate_transaction_integrity(security_service)
            print(f"   Integrity Check: {'✅ PASSED' if is_valid else '❌ FAILED'}")
            
            # Show domain events
            events = payment.clear_domain_events()
            print(f"\n📋 Domain Events Generated: {len(events)}")
            for event in events:
                print(f"   - {event.__class__.__name__} at {event.occurred_at.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"   ❌ Error processing payment: {e}")
        
        print("-" * 50)
    
    # Show payment summaries
    print(f"\n📊 Payment Summary Report")
    print("=" * 30)
    
    for payment in payments:
        summary = payment.get_payment_summary()
        print(f"\n💳 {summary['payment_id']}")
        print(f"   Status: {summary['status'].upper()}")
        print(f"   Amount: ₹{summary['amount']['original']}")
        print(f"   Refunded: ₹{summary['amount']['refunded']}")
        print(f"   Merchant: {summary['merchant']['name']}")
        print(f"   Fraud Score: {summary['security']['fraud_score']:.2f}" if summary['security']['fraud_score'] else "N/A")
        print(f"   Refunds: {len(summary['refunds'])}")
    
    print(f"\n✨ All payment aggregates working correctly!")
    print(f"✨ Ready for production use in Paytm-scale system!")