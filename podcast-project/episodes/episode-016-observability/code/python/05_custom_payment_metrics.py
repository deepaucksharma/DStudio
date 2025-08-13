#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 5: Custom Metrics for Indian Payment Systems

भारतीय payment ecosystem के लिए specialized metrics
UPI, Cards, Wallets, RBI compliance tracking

Author: Hindi Tech Podcast
Context: Indian payment systems comprehensive monitoring
"""

import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Enum as PrometheusEnum,
    CollectorRegistry, generate_latest, start_http_server
)
import structlog

logger = structlog.get_logger()

class PaymentMethod(Enum):
    """भारतीय payment methods की comprehensive list"""
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    DIGITAL_WALLET = "digital_wallet"
    PREPAID_CARD = "prepaid_card"
    GIFT_CARD = "gift_card"
    EMI = "emi"
    BNPL = "buy_now_pay_later"  # Buy Now Pay Later
    COD = "cash_on_delivery"

class UPIProvider(Enum):
    """Major UPI service providers"""
    PHONEPE = "phonepe"
    PAYTM = "paytm"
    GOOGLEPAY = "googlepay"
    AMAZON_PAY = "amazon_pay"
    BHIM = "bhim"
    MOBIKWIK = "mobikwik"
    FREECHARGE = "freecharge"
    CRED = "cred"
    OTHER = "other"

class BankCode(Enum):
    """Major Indian banks for UPI"""
    SBI = "sbi"           # State Bank of India
    HDFC = "hdfc"         # HDFC Bank
    ICICI = "icici"       # ICICI Bank
    AXIS = "axis"         # Axis Bank
    KOTAK = "kotak"       # Kotak Mahindra Bank
    PNB = "pnb"          # Punjab National Bank
    BOI = "boi"          # Bank of India
    CANARA = "canara"     # Canara Bank
    UNION = "union"       # Union Bank
    IOB = "iob"          # Indian Overseas Bank

class RBICategory(Enum):
    """RBI transaction categories for compliance"""
    PEER_TO_PEER = "p2p"
    PEER_TO_MERCHANT = "p2m"
    BILL_PAYMENT = "bill_payment"
    MOBILE_RECHARGE = "mobile_recharge"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    ECOMMERCE = "ecommerce"
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"

@dataclass
class PaymentTransaction:
    """Complete payment transaction data structure"""
    transaction_id: str
    payment_method: PaymentMethod
    amount: float
    currency: str = "INR"
    
    # UPI specific
    upi_provider: Optional[UPIProvider] = None
    bank_code: Optional[BankCode] = None
    vpa: Optional[str] = None  # Virtual Payment Address
    
    # Geographic context
    merchant_city: str = "Mumbai"
    customer_city: str = "Mumbai"
    merchant_mcc: str = "5999"  # Merchant Category Code
    
    # RBI compliance
    rbi_category: RBICategory = RBICategory.PEER_TO_MERCHANT
    
    # Transaction metadata
    is_successful: bool = True
    error_code: Optional[str] = None
    processing_time_ms: float = 1000.0
    retry_count: int = 0
    
    # Security
    risk_score: float = 0.1  # 0.0 (safe) to 1.0 (high risk)
    is_fraud_flagged: bool = False
    kyc_verified: bool = True
    
    # Timestamp
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class IndianPaymentMetricsCollector:
    """
    भारतीय payment systems के लिए comprehensive metrics collector
    RBI compliance और business intelligence के साथ
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._setup_payment_metrics()
        self._setup_compliance_metrics()
        self._setup_business_metrics()
        self._setup_security_metrics()
        
        logger.info("Indian Payment Metrics Collector initialized")

    def _setup_payment_metrics(self):
        """Core payment metrics setup"""
        
        # Transaction volume and success rates
        self.payment_transactions_total = Counter(
            'payment_transactions_total',
            'Total payment transactions by method and status',
            ['payment_method', 'status', 'city', 'merchant_mcc'],
            registry=self.registry
        )
        
        # Transaction amounts (business metrics)
        self.payment_amount_inr_total = Counter(
            'payment_amount_inr_total',
            'Total payment amount in INR',
            ['payment_method', 'rbi_category', 'city'],
            registry=self.registry
        )
        
        # UPI specific metrics
        self.upi_transactions_by_provider = Counter(
            'upi_transactions_by_provider_total',
            'UPI transactions by provider and bank',
            ['upi_provider', 'bank_code', 'status'],
            registry=self.registry
        )
        
        # Processing time distribution
        self.payment_processing_time = Histogram(
            'payment_processing_time_seconds',
            'Payment processing time in seconds',
            ['payment_method', 'bank_code'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        # Error tracking
        self.payment_errors_total = Counter(
            'payment_errors_total',
            'Payment errors by type and method',
            ['payment_method', 'error_code', 'bank_code'],
            registry=self.registry
        )
        
        # Success rate gauge (rolling 5-minute window)
        self.payment_success_rate = Gauge(
            'payment_success_rate_percentage',
            'Payment success rate by method (5min window)',
            ['payment_method', 'time_window'],
            registry=self.registry
        )

    def _setup_compliance_metrics(self):
        """RBI compliance और regulatory metrics"""
        
        # RBI category distribution
        self.rbi_category_distribution = Counter(
            'rbi_transaction_category_total',
            'RBI transaction categories',
            ['rbi_category', 'payment_method', 'amount_range'],
            registry=self.registry
        )
        
        # Daily transaction limits tracking
        self.daily_transaction_limits = Gauge(
            'daily_transaction_limits_utilization',
            'Daily transaction limits utilization per user',
            ['limit_type', 'payment_method'],
            registry=self.registry
        )
        
        # KYC verification metrics
        self.kyc_verification_rate = Gauge(
            'kyc_verification_rate_percentage',
            'KYC verification rate',
            ['verification_type', 'city'],
            registry=self.registry
        )
        
        # Regulatory reporting lag
        self.rbi_reporting_lag_seconds = Gauge(
            'rbi_reporting_lag_seconds',
            'RBI reporting lag in seconds',
            ['report_type', 'bank_code'],
            registry=self.registry
        )
        
        # Compliance score
        self.compliance_score = Gauge(
            'payment_compliance_score',
            'Overall compliance score (0-100)',
            ['compliance_type'],
            registry=self.registry
        )

    def _setup_business_metrics(self):
        """Business intelligence और revenue metrics"""
        
        # Revenue by merchant category
        self.revenue_by_mcc = Counter(
            'revenue_by_merchant_category_inr',
            'Revenue by merchant category in INR',
            ['mcc_code', 'city', 'payment_method'],
            registry=self.registry
        )
        
        # Payment method adoption rate
        self.payment_method_adoption = Gauge(
            'payment_method_adoption_percentage',
            'Payment method adoption rate by region',
            ['payment_method', 'city', 'age_group'],
            registry=self.registry
        )
        
        # Peak hour performance
        self.peak_hour_metrics = Gauge(
            'peak_hour_transaction_rate',
            'Transaction rate during peak hours',
            ['hour', 'day_type', 'payment_method'],
            registry=self.registry
        )
        
        # Festival season multiplier
        self.festival_transaction_multiplier = Gauge(
            'festival_transaction_multiplier',
            'Transaction volume multiplier during festivals',
            ['festival', 'payment_method'],
            registry=self.registry
        )
        
        # Customer lifetime value impact
        self.customer_ltv_impact = Histogram(
            'customer_ltv_impact_inr',
            'Customer lifetime value impact from payment methods',
            ['payment_method', 'customer_segment'],
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000],
            registry=self.registry
        )

    def _setup_security_metrics(self):
        """Security और fraud detection metrics"""
        
        # Fraud detection metrics
        self.fraud_detection_rate = Counter(
            'fraud_detection_total',
            'Fraud detection events',
            ['detection_type', 'payment_method', 'risk_level'],
            registry=self.registry
        )
        
        # Risk score distribution
        self.risk_score_distribution = Histogram(
            'transaction_risk_score',
            'Transaction risk score distribution',
            ['payment_method', 'amount_range'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # Security incident response time
        self.security_response_time = Histogram(
            'security_incident_response_time_seconds',
            'Security incident response time',
            ['incident_type', 'severity'],
            buckets=[60, 300, 900, 1800, 3600, 7200],
            registry=self.registry
        )
        
        # Account lockout metrics
        self.account_lockouts = Counter(
            'account_lockouts_total',
            'Account lockouts due to security reasons',
            ['lockout_reason', 'payment_method'],
            registry=self.registry
        )

    async def record_payment_transaction(self, transaction: PaymentTransaction):
        """
        Payment transaction को comprehensive metrics में record करता है
        """
        try:
            start_time = time.time()
            
            # Basic transaction metrics
            status = "success" if transaction.is_successful else "failure"
            self.payment_transactions_total.labels(
                payment_method=transaction.payment_method.value,
                status=status,
                city=transaction.customer_city,
                merchant_mcc=transaction.merchant_mcc
            ).inc()
            
            # Amount tracking (only for successful transactions)
            if transaction.is_successful:
                self.payment_amount_inr_total.labels(
                    payment_method=transaction.payment_method.value,
                    rbi_category=transaction.rbi_category.value,
                    city=transaction.customer_city
                ).inc(transaction.amount)
            
            # UPI specific tracking
            if transaction.payment_method == PaymentMethod.UPI and transaction.upi_provider:
                self.upi_transactions_by_provider.labels(
                    upi_provider=transaction.upi_provider.value,
                    bank_code=transaction.bank_code.value if transaction.bank_code else "unknown",
                    status=status
                ).inc()
            
            # Processing time
            processing_time_seconds = transaction.processing_time_ms / 1000.0
            self.payment_processing_time.labels(
                payment_method=transaction.payment_method.value,
                bank_code=transaction.bank_code.value if transaction.bank_code else "na"
            ).observe(processing_time_seconds)
            
            # Error tracking
            if not transaction.is_successful and transaction.error_code:
                self.payment_errors_total.labels(
                    payment_method=transaction.payment_method.value,
                    error_code=transaction.error_code,
                    bank_code=transaction.bank_code.value if transaction.bank_code else "na"
                ).inc()
            
            # RBI compliance metrics
            amount_range = self._get_amount_range(transaction.amount)
            self.rbi_category_distribution.labels(
                rbi_category=transaction.rbi_category.value,
                payment_method=transaction.payment_method.value,
                amount_range=amount_range
            ).inc()
            
            # Revenue by merchant category
            if transaction.is_successful:
                self.revenue_by_mcc.labels(
                    mcc_code=transaction.merchant_mcc,
                    city=transaction.merchant_city,
                    payment_method=transaction.payment_method.value
                ).inc(transaction.amount)
            
            # Security metrics
            if transaction.risk_score > 0:
                risk_level = self._get_risk_level(transaction.risk_score)
                
                self.risk_score_distribution.labels(
                    payment_method=transaction.payment_method.value,
                    amount_range=amount_range
                ).observe(transaction.risk_score)
                
                if transaction.is_fraud_flagged:
                    self.fraud_detection_rate.labels(
                        detection_type="ml_model",
                        payment_method=transaction.payment_method.value,
                        risk_level=risk_level
                    ).inc()
            
            # Peak hour detection
            current_hour = transaction.timestamp.hour
            if current_hour in [10, 11, 19, 20, 21]:  # Indian peak hours
                day_type = "weekday" if transaction.timestamp.weekday() < 5 else "weekend"
                self.peak_hour_metrics.labels(
                    hour=current_hour,
                    day_type=day_type,
                    payment_method=transaction.payment_method.value
                ).set(self._get_current_tps(transaction.payment_method))
            
            processing_time = time.time() - start_time
            logger.info("Payment transaction recorded",
                       transaction_id=transaction.transaction_id,
                       payment_method=transaction.payment_method.value,
                       amount=transaction.amount,
                       success=transaction.is_successful,
                       processing_time_ms=processing_time * 1000)
                       
        except Exception as e:
            logger.error("Failed to record payment transaction",
                        transaction_id=transaction.transaction_id,
                        error=str(e))

    def _get_amount_range(self, amount: float) -> str:
        """Amount को range categories में classify करता है"""
        if amount <= 100:
            return "micro"      # Micro payments (₹0-100)
        elif amount <= 1000:
            return "small"      # Small payments (₹100-1000)
        elif amount <= 10000:
            return "medium"     # Medium payments (₹1000-10000)
        elif amount <= 100000:
            return "large"      # Large payments (₹10000-100000)
        else:
            return "bulk"       # Bulk payments (₹100000+)

    def _get_risk_level(self, risk_score: float) -> str:
        """Risk score को risk level में convert करता है"""
        if risk_score <= 0.3:
            return "low"
        elif risk_score <= 0.6:
            return "medium"
        elif risk_score <= 0.8:
            return "high"
        else:
            return "critical"

    def _get_current_tps(self, payment_method: PaymentMethod) -> float:
        """Current transactions per second estimate करता है"""
        # Realistic TPS based on payment method
        base_tps = {
            PaymentMethod.UPI: random.uniform(100, 1000),
            PaymentMethod.CREDIT_CARD: random.uniform(50, 300),
            PaymentMethod.DEBIT_CARD: random.uniform(30, 200),
            PaymentMethod.NET_BANKING: random.uniform(10, 100),
            PaymentMethod.DIGITAL_WALLET: random.uniform(20, 150)
        }
        
        return base_tps.get(payment_method, random.uniform(10, 100))

    def update_compliance_metrics(self):
        """
        Compliance metrics को update करता है
        RBI guidelines के according
        """
        # KYC verification rates by city
        indian_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
        for city in indian_cities:
            kyc_rate = random.uniform(85, 98)  # 85-98% KYC compliance
            self.kyc_verification_rate.labels(
                verification_type="full_kyc",
                city=city
            ).set(kyc_rate)
        
        # RBI reporting lag for different banks
        for bank in BankCode:
            reporting_lag = random.uniform(0, 300)  # 0-5 minutes lag
            self.rbi_reporting_lag_seconds.labels(
                report_type="transaction_summary",
                bank_code=bank.value
            ).set(reporting_lag)
        
        # Overall compliance score
        compliance_score = random.uniform(92, 99)  # High compliance target
        self.compliance_score.labels(
            compliance_type="rbi_guidelines"
        ).set(compliance_score)

    def update_business_metrics(self):
        """
        Business intelligence metrics को update करता है
        """
        # Payment method adoption by region
        payment_methods = list(PaymentMethod)
        cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
        age_groups = ["18-25", "26-35", "36-45", "46-55", "55+"]
        
        for method in payment_methods:
            for city in cities:
                for age_group in age_groups:
                    # UPI has higher adoption in younger demographics
                    if method == PaymentMethod.UPI and age_group in ["18-25", "26-35"]:
                        adoption_rate = random.uniform(70, 90)
                    elif method == PaymentMethod.CREDIT_CARD and age_group in ["36-45", "46-55"]:
                        adoption_rate = random.uniform(60, 80)
                    else:
                        adoption_rate = random.uniform(20, 60)
                    
                    self.payment_method_adoption.labels(
                        payment_method=method.value,
                        city=city,
                        age_group=age_group
                    ).set(adoption_rate)

    def set_festival_multipliers(self):
        """
        Festival season के दौरान transaction multipliers set करता है
        """
        current_month = datetime.now().month
        
        festivals = {
            10: ("dussehra", 3.5),      # October - Dussehra/BBD
            11: ("diwali", 8.0),        # November - Diwali
            12: ("christmas", 4.0),     # December - Christmas/NYE
            3: ("holi", 2.5),          # March - Holi
            8: ("raksha_bandhan", 2.0), # August - Raksha Bandhan
        }
        
        if current_month in festivals:
            festival_name, multiplier = festivals[current_month]
            
            for method in PaymentMethod:
                # UPI and Digital Wallets see higher growth during festivals
                if method in [PaymentMethod.UPI, PaymentMethod.DIGITAL_WALLET]:
                    festival_multiplier = multiplier * 1.2
                else:
                    festival_multiplier = multiplier
                
                self.festival_transaction_multiplier.labels(
                    festival=festival_name,
                    payment_method=method.value
                ).set(festival_multiplier)

class PaymentTransactionGenerator:
    """
    Realistic payment transactions generate करता है
    Indian payment patterns के according
    """
    
    def __init__(self):
        self.cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur"
        ]
        
        self.merchant_categories = {
            "5411": "Grocery Stores",
            "5812": "Eating Places",
            "5541": "Service Stations",
            "5732": "Electronics Stores",
            "5651": "Family Clothing Stores",
            "5999": "Miscellaneous Retail",
            "5912": "Drug Stores",
            "5200": "Home Supply Warehouse",
            "7011": "Hotels/Motels",
            "4112": "Passenger Railways"
        }

    def generate_transaction(self, 
                           payment_method: PaymentMethod = None,
                           amount_range: str = "random") -> PaymentTransaction:
        """
        Realistic payment transaction generate करता है
        """
        if payment_method is None:
            # UPI dominance in Indian market (70%+ adoption)
            payment_method = random.choices(
                list(PaymentMethod),
                weights=[50, 15, 10, 8, 7, 3, 2, 2, 2, 1]  # UPI heavily weighted
            )[0]
        
        # Amount generation based on payment method and range
        amount = self._generate_amount(payment_method, amount_range)
        
        # UPI provider and bank selection
        upi_provider = None
        bank_code = None
        if payment_method == PaymentMethod.UPI:
            upi_provider = random.choice(list(UPIProvider))
            bank_code = random.choice(list(BankCode))
        
        # Geographic selection
        customer_city = random.choice(self.cities)
        merchant_city = customer_city if random.random() < 0.8 else random.choice(self.cities)
        
        # Merchant category
        mcc = random.choice(list(self.merchant_categories.keys()))
        
        # RBI category based on MCC
        rbi_category = self._get_rbi_category(mcc)
        
        # Success rate varies by payment method
        success_rates = {
            PaymentMethod.UPI: 0.96,
            PaymentMethod.DIGITAL_WALLET: 0.98,
            PaymentMethod.CREDIT_CARD: 0.88,
            PaymentMethod.DEBIT_CARD: 0.85,
            PaymentMethod.NET_BANKING: 0.82,
            PaymentMethod.COD: 0.99
        }
        
        success_rate = success_rates.get(payment_method, 0.90)
        is_successful = random.random() < success_rate
        
        # Error generation for failed transactions
        error_code = None
        if not is_successful:
            errors = [
                "INSUFFICIENT_FUNDS", "CARD_DECLINED", "BANK_TIMEOUT",
                "INVALID_PIN", "LIMIT_EXCEEDED", "TECHNICAL_ERROR"
            ]
            error_code = random.choice(errors)
        
        # Processing time varies by method
        processing_times = {
            PaymentMethod.UPI: random.uniform(2000, 8000),
            PaymentMethod.DIGITAL_WALLET: random.uniform(1000, 3000),
            PaymentMethod.CREDIT_CARD: random.uniform(3000, 12000),
            PaymentMethod.NET_BANKING: random.uniform(10000, 30000)
        }
        
        processing_time = processing_times.get(payment_method, random.uniform(2000, 10000))
        
        # Risk scoring
        risk_score = self._calculate_risk_score(amount, customer_city, payment_method)
        is_fraud_flagged = risk_score > 0.7
        
        return PaymentTransaction(
            transaction_id=f"TXN{int(time.time())}{random.randint(1000, 9999)}",
            payment_method=payment_method,
            amount=amount,
            upi_provider=upi_provider,
            bank_code=bank_code,
            merchant_city=merchant_city,
            customer_city=customer_city,
            merchant_mcc=mcc,
            rbi_category=rbi_category,
            is_successful=is_successful,
            error_code=error_code,
            processing_time_ms=processing_time,
            risk_score=risk_score,
            is_fraud_flagged=is_fraud_flagged,
            kyc_verified=random.random() < 0.95
        )

    def _generate_amount(self, payment_method: PaymentMethod, amount_range: str) -> float:
        """Payment method के according realistic amount generate करता है"""
        
        if amount_range == "micro":
            return random.uniform(10, 100)
        elif amount_range == "small":
            return random.uniform(100, 1000)
        elif amount_range == "medium":
            return random.uniform(1000, 10000)
        elif amount_range == "large":
            return random.uniform(10000, 100000)
        elif amount_range == "bulk":
            return random.uniform(100000, 1000000)
        
        # Default: realistic amounts by payment method
        if payment_method == PaymentMethod.UPI:
            return random.uniform(50, 5000)  # Most common UPI range
        elif payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            return random.uniform(500, 50000)  # Card payments typically higher
        elif payment_method == PaymentMethod.DIGITAL_WALLET:
            return random.uniform(100, 2000)   # Wallet recharges and small purchases
        else:
            return random.uniform(200, 10000)  # Other methods

    def _get_rbi_category(self, mcc: str) -> RBICategory:
        """MCC code के based पर RBI category determine करता है"""
        
        category_mapping = {
            "5411": RBICategory.ECOMMERCE,
            "5812": RBICategory.ECOMMERCE,
            "5541": RBICategory.BILL_PAYMENT,
            "5732": RBICategory.ECOMMERCE,
            "5651": RBICategory.ECOMMERCE,
            "5999": RBICategory.ECOMMERCE,
            "5912": RBICategory.HEALTHCARE,
            "7011": RBICategory.ECOMMERCE,
            "4112": RBICategory.ECOMMERCE
        }
        
        return category_mapping.get(mcc, RBICategory.PEER_TO_MERCHANT)

    def _calculate_risk_score(self, amount: float, city: str, 
                            payment_method: PaymentMethod) -> float:
        """Transaction risk score calculate करता है"""
        
        risk_score = 0.1  # Base risk
        
        # Amount-based risk
        if amount > 100000:
            risk_score += 0.3
        elif amount > 50000:
            risk_score += 0.2
        elif amount > 10000:
            risk_score += 0.1
        
        # Payment method risk
        method_risk = {
            PaymentMethod.UPI: 0.05,
            PaymentMethod.DIGITAL_WALLET: 0.05,
            PaymentMethod.CREDIT_CARD: 0.15,
            PaymentMethod.DEBIT_CARD: 0.10,
            PaymentMethod.NET_BANKING: 0.20
        }
        
        risk_score += method_risk.get(payment_method, 0.10)
        
        # Geographic risk (Tier-3 cities have higher risk)
        tier1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune"]
        if city not in tier1_cities:
            risk_score += 0.05
        
        return min(risk_score, 1.0)  # Cap at 1.0

async def main():
    """
    Main function - Payment metrics demonstration
    """
    print("💳 Indian Payment Systems Metrics Collector")
    print("🏦 Comprehensive monitoring for UPI, Cards, Wallets")
    print("📊 RBI compliance और business intelligence")
    print("\nFeatures:")
    print("  ✅ Multi-payment method tracking")
    print("  ✅ UPI provider और bank analysis")
    print("  ✅ RBI compliance monitoring")
    print("  ✅ Fraud detection metrics")
    print("  ✅ Festival season analytics")
    print("  ✅ Regional performance tracking")
    print("\nAccess URLs:")
    print("  📊 Metrics: http://localhost:8001/metrics")
    print("\nStarting payment simulation...\n")
    
    # Initialize collector
    collector = IndianPaymentMetricsCollector()
    generator = PaymentTransactionGenerator()
    
    # Start HTTP server for metrics
    start_http_server(8001, registry=collector.registry)
    
    # Simulate transactions
    for i in range(100):
        # Generate random transaction
        transaction = generator.generate_transaction()
        
        # Record metrics
        await collector.record_payment_transaction(transaction)
        
        if i % 10 == 0:
            print(f"📈 Processed {i+1} transactions...")
            
            # Update periodic metrics
            collector.update_compliance_metrics()
            collector.update_business_metrics()
            collector.set_festival_multipliers()
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
    
    print("\n🎉 Payment metrics demonstration completed!")
    print("Check http://localhost:8001/metrics for detailed metrics")
    
    # Keep server running
    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

"""
Production Deployment Notes:

1. Metrics Collection Strategy:
   - High-frequency payment events (10K+ TPS)
   - Efficient cardinality management
   - Batch processing for performance
   - Real-time alerting for critical metrics

2. RBI Compliance Integration:
   - Automated compliance reporting
   - Real-time limit monitoring
   - KYC verification tracking
   - Audit trail maintenance

3. Security Considerations:
   - PII data anonymization
   - Risk score calculation
   - Fraud detection integration
   - Incident response metrics

4. Business Intelligence:
   - Payment method adoption trends
   - Regional performance analysis
   - Festival season planning
   - Revenue optimization insights

5. Alert Rules:
   - Payment success rate < 95%
   - Fraud detection rate > 2%
   - RBI reporting lag > 5 minutes
   - Compliance score < 90%

Sample PromQL Queries:
- UPI success rate: rate(upi_transactions_by_provider_total{status="success"}[5m]) / rate(upi_transactions_by_provider_total[5m]) * 100
- Payment method distribution: rate(payment_transactions_total[1h]) by (payment_method)
- Regional performance: avg by (city) (payment_processing_time_seconds)
- Fraud detection trends: rate(fraud_detection_total[1h]) by (detection_type)
"""