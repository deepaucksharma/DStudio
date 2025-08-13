#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 1: Prometheus UPI Transaction Monitoring System

भारतीय UPI ecosystem के लिए real-time monitoring solution
Paytm/PhonePe style transaction tracking with bank-wise metrics

Author: Hindi Tech Podcast
Context: Indian payment systems monitoring at scale
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    CollectorRegistry, generate_latest,
    start_http_server, Info
)
from prometheus_client.core import InfoMetricFamily
import structlog

# Hindi comments के साथ logging setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class UPIBank(Enum):
    """
    भारतीय banks की enum list
    Major UPI supporting banks के साथ
    """
    SBI = "sbi"           # State Bank of India - largest market share
    HDFC = "hdfc"         # HDFC Bank - premium segment
    ICICI = "icici"       # ICICI Bank - urban focus
    KOTAK = "kotak"       # Kotak Mahindra - affluent customers
    AXIS = "axis"         # Axis Bank - digital first
    PNB = "pnb"          # Punjab National Bank - government
    BOI = "boi"          # Bank of India - traditional
    CANARA = "canara"     # Canara Bank - south focus
    UNION = "union"       # Union Bank - rural reach
    IOB = "iob"          # Indian Overseas Bank - regional

class UPITransactionType(Enum):
    """UPI transaction types जो monitor करते हैं"""
    P2P = "person_to_person"      # Person to Person transfer
    P2M = "person_to_merchant"    # Person to Merchant payment
    BILL = "bill_payment"         # Bill payments (electricity, mobile)
    RECHARGE = "mobile_recharge"  # Mobile/DTH recharge
    INVESTMENT = "investment"     # Mutual fund, SIP investments
    INSURANCE = "insurance"       # Insurance premium payments
    ECOMMERCE = "ecommerce"       # E-commerce payments
    FOOD = "food_delivery"        # Food delivery payments

@dataclass
class UPITransaction:
    """
    UPI transaction का data structure
    Monitoring के लिए required fields
    """
    transaction_id: str
    bank: UPIBank
    transaction_type: UPITransactionType
    amount: float
    currency: str = "INR"
    timestamp: datetime = None
    success: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: float = 0.0
    user_city: str = "Mumbai"
    merchant_category: Optional[str] = None
    retry_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class UPIPrometheusCollector:
    """
    Prometheus metrics collector for UPI transactions
    भारतीय scale के लिए optimized metrics collection
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._setup_metrics()
        
        # Indian context के लिए special labels
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur",
            "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal"
        ]
        
        logger.info("UPI Prometheus Collector initialized", 
                   supported_banks=len(UPIBank), 
                   supported_cities=len(self.indian_cities))

    def _setup_metrics(self):
        """
        Core UPI metrics setup
        Business और technical metrics दोनों के लिए
        """
        
        # Transaction count metrics
        self.upi_transactions_total = Counter(
            'upi_transactions_total',
            'Total UPI transactions processed', 
            ['bank', 'transaction_type', 'status', 'city'],
            registry=self.registry
        )
        
        # Transaction amount metrics (INR में)
        self.upi_transaction_amount = Counter(
            'upi_transaction_amount_inr_total',
            'Total transaction amount in INR',
            ['bank', 'transaction_type', 'city'],
            registry=self.registry
        )
        
        # Response time histogram
        self.upi_response_time = Histogram(
            'upi_response_time_seconds',
            'UPI transaction response time in seconds',
            ['bank', 'transaction_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        # Success rate gauge (percentage)
        self.upi_success_rate = Gauge(
            'upi_success_rate_percentage',
            'UPI transaction success rate by bank',
            ['bank', 'time_window'],
            registry=self.registry
        )
        
        # Error metrics by type
        self.upi_errors_total = Counter(
            'upi_errors_total',
            'Total UPI transaction errors',
            ['bank', 'error_code', 'error_type'],
            registry=self.registry
        )
        
        # Bank availability gauge
        self.bank_availability = Gauge(
            'upi_bank_availability',
            'Bank UPI service availability (1=up, 0=down)',
            ['bank'],
            registry=self.registry
        )
        
        # Festival season metrics
        self.festival_transaction_spike = Gauge(
            'upi_festival_transaction_multiplier',
            'Transaction volume multiplier during festivals',
            ['festival', 'date'],
            registry=self.registry
        )
        
        # Regulatory compliance metrics
        self.rbi_reporting_lag = Gauge(
            'upi_rbi_reporting_lag_seconds',
            'RBI transaction reporting lag in seconds',
            ['bank'],
            registry=self.registry
        )
        
        # Peak hour metrics (10-11 AM, 7-9 PM Indian peak hours)
        self.peak_hour_load = Gauge(
            'upi_peak_hour_transaction_rate',
            'Transactions per second during peak hours',
            ['hour', 'day_type'],
            registry=self.registry
        )

    async def record_transaction(self, transaction: UPITransaction):
        """
        Record a UPI transaction में metrics
        Async method for high-throughput processing
        """
        try:
            start_time = time.time()
            
            # Basic transaction count
            status = "success" if transaction.success else "failure"
            self.upi_transactions_total.labels(
                bank=transaction.bank.value,
                transaction_type=transaction.transaction_type.value,
                status=status,
                city=transaction.user_city
            ).inc()
            
            # Transaction amount (only for successful transactions)
            if transaction.success:
                self.upi_transaction_amount.labels(
                    bank=transaction.bank.value,
                    transaction_type=transaction.transaction_type.value,
                    city=transaction.user_city
                ).inc(transaction.amount)
            
            # Response time tracking
            response_time_seconds = transaction.response_time_ms / 1000.0
            self.upi_response_time.labels(
                bank=transaction.bank.value,
                transaction_type=transaction.transaction_type.value
            ).observe(response_time_seconds)
            
            # Error tracking for failed transactions
            if not transaction.success and transaction.error_code:
                error_type = self._categorize_error(transaction.error_code)
                self.upi_errors_total.labels(
                    bank=transaction.bank.value,
                    error_code=transaction.error_code,
                    error_type=error_type
                ).inc()
            
            # Peak hour detection
            current_hour = datetime.now().hour
            if current_hour in [10, 11, 19, 20, 21]:  # Indian peak hours
                day_type = "weekday" if datetime.now().weekday() < 5 else "weekend"
                self.peak_hour_load.labels(
                    hour=current_hour,
                    day_type=day_type
                ).set(self._get_current_tps())
            
            processing_time = time.time() - start_time
            logger.info("Transaction recorded", 
                       transaction_id=transaction.transaction_id,
                       bank=transaction.bank.value,
                       amount=transaction.amount,
                       success=transaction.success,
                       processing_time_ms=processing_time * 1000)
                       
        except Exception as e:
            logger.error("Failed to record transaction metrics", 
                        transaction_id=transaction.transaction_id,
                        error=str(e))

    def _categorize_error(self, error_code: str) -> str:
        """
        Error codes को categories में बांटता है
        Indian banking error patterns के according
        """
        error_categories = {
            "BANK_TIMEOUT": ["BT01", "BT02", "TIMEOUT"],
            "INSUFFICIENT_FUNDS": ["IF01", "BALANCE_LOW", "NSF"],
            "INVALID_PIN": ["IP01", "WRONG_PIN", "AUTH_FAIL"],
            "NETWORK_ERROR": ["NE01", "CONN_FAIL", "NET_DOWN"],
            "BANK_MAINTENANCE": ["BM01", "MAINT", "SERVICE_DOWN"],
            "LIMIT_EXCEEDED": ["LE01", "DAILY_LIMIT", "TXN_LIMIT"],
            "FRAUD_SUSPECTED": ["FS01", "SUSPICIOUS", "BLOCKED"],
            "TECHNICAL_ERROR": ["TE01", "SYSTEM_ERROR", "UNKNOWN"]
        }
        
        for category, codes in error_categories.items():
            if any(code in error_code.upper() for code in codes):
                return category
        
        return "OTHER"

    def _get_current_tps(self) -> float:
        """
        Current transactions per second calculate करता है
        Moving window approach के साथ
        """
        # Simplified TPS calculation
        # Real implementation में proper window-based calculation होगी
        return random.uniform(100, 1000)  # Simulated TPS

    def update_bank_availability(self, bank: UPIBank, is_available: bool):
        """
        Bank की availability status update करता है
        Health check results के base पर
        """
        availability = 1.0 if is_available else 0.0
        self.bank_availability.labels(bank=bank.value).set(availability)
        
        logger.info("Bank availability updated", 
                   bank=bank.value, 
                   available=is_available)

    def update_success_rates(self):
        """
        Success rates को calculate और update करता है
        Different time windows के लिए
        """
        time_windows = ["1m", "5m", "15m", "1h"]
        
        for bank in UPIBank:
            for window in time_windows:
                # Mock calculation - real implementation में
                # actual metrics से calculate होगा
                success_rate = random.uniform(85.0, 99.5)
                self.upi_success_rate.labels(
                    bank=bank.value,
                    time_window=window
                ).set(success_rate)

    def set_festival_metrics(self, festival_name: str, multiplier: float):
        """
        Festival season के दौरान traffic spike को track करता है
        Diwali, BBD, NYE जैसे events के लिए
        """
        today = datetime.now().strftime("%Y-%m-%d")
        self.festival_transaction_spike.labels(
            festival=festival_name,
            date=today
        ).set(multiplier)
        
        logger.info("Festival metrics updated", 
                   festival=festival_name, 
                   multiplier=multiplier)

    def update_rbi_compliance_lag(self, bank: UPIBank, lag_seconds: float):
        """
        RBI reporting compliance की lag को track करता है
        Regulatory requirements के लिए important
        """
        self.rbi_reporting_lag.labels(bank=bank.value).set(lag_seconds)

class UPIMonitoringService:
    """
    Complete UPI monitoring service
    Production deployment के लिए ready
    """
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.collector = UPIPrometheusCollector()
        self.running = False
        
        # Test transactions के लिए sample data
        self.sample_transactions = self._generate_sample_data()

    def _generate_sample_data(self) -> List[UPITransaction]:
        """
        Realistic sample UPI transactions generate करता है
        Testing और demo के लिए
        """
        transactions = []
        
        for i in range(100):
            bank = random.choice(list(UPIBank))
            txn_type = random.choice(list(UPITransactionType))
            
            # Indian transaction amount patterns
            if txn_type == UPITransactionType.P2P:
                amount = random.uniform(100, 50000)  # ₹100 to ₹50,000
            elif txn_type == UPITransactionType.ECOMMERCE:
                amount = random.uniform(500, 10000)  # ₹500 to ₹10,000
            elif txn_type == UPITransactionType.BILL:
                amount = random.uniform(200, 5000)   # ₹200 to ₹5,000
            else:
                amount = random.uniform(50, 2000)    # ₹50 to ₹2,000
            
            # Success rate varies by bank (realistic Indian patterns)
            bank_success_rates = {
                UPIBank.SBI: 0.96,
                UPIBank.HDFC: 0.97,
                UPIBank.ICICI: 0.95,
                UPIBank.KOTAK: 0.98,
                UPIBank.AXIS: 0.94,
            }
            
            success_rate = bank_success_rates.get(bank, 0.90)
            success = random.random() < success_rate
            
            # Error codes for failed transactions
            error_code = None
            error_message = None
            if not success:
                errors = [
                    ("BT01", "Bank gateway timeout"),
                    ("IF01", "Insufficient funds"),
                    ("NE01", "Network connectivity issue"),
                    ("LE01", "Daily transaction limit exceeded")
                ]
                error_code, error_message = random.choice(errors)
            
            city = random.choice(self.collector.indian_cities)
            response_time = random.uniform(500, 8000)  # 0.5 to 8 seconds
            
            transaction = UPITransaction(
                transaction_id=f"UPI{int(time.time())}{i:04d}",
                bank=bank,
                transaction_type=txn_type,
                amount=amount,
                success=success,
                error_code=error_code,
                error_message=error_message,
                response_time_ms=response_time,
                user_city=city,
                retry_count=random.randint(0, 3) if not success else 0
            )
            
            transactions.append(transaction)
        
        return transactions

    async def start_monitoring(self):
        """
        Monitoring service को start करता है
        HTTP server और background tasks के साथ
        """
        self.running = True
        
        # Start Prometheus HTTP server
        start_http_server(self.port, registry=self.collector.registry)
        logger.info("Prometheus metrics server started", port=self.port)
        
        # Background tasks start करें
        tasks = [
            self._transaction_simulator(),
            self._periodic_updates(),
            self._bank_health_checker()
        ]
        
        await asyncio.gather(*tasks)

    async def _transaction_simulator(self):
        """
        Sample transactions को simulate करता है
        Real-world patterns के साथ
        """
        while self.running:
            try:
                # Random transaction select करें
                transaction = random.choice(self.sample_transactions)
                
                # Regenerate transaction ID for uniqueness
                transaction.transaction_id = f"UPI{int(time.time())}{random.randint(1000, 9999)}"
                transaction.timestamp = datetime.utcnow()
                
                # Peak hour simulation (Indian timing)
                current_hour = datetime.now().hour
                if current_hour in [10, 11, 19, 20, 21]:
                    # Peak hours में ज्यादा transactions
                    await asyncio.sleep(0.1)  # 10 TPS
                else:
                    # Normal hours में कम transactions
                    await asyncio.sleep(0.5)   # 2 TPS
                
                await self.collector.record_transaction(transaction)
                
            except Exception as e:
                logger.error("Transaction simulation error", error=str(e))
                await asyncio.sleep(1)

    async def _periodic_updates(self):
        """
        Periodic metrics updates
        Success rates, compliance metrics, etc.
        """
        while self.running:
            try:
                # Success rates update करें
                self.collector.update_success_rates()
                
                # Festival detection और metrics
                today = datetime.now()
                if today.month == 11:  # November - Diwali season
                    self.collector.set_festival_metrics("Diwali", 8.5)
                elif today.month == 10:  # October - BBD season
                    self.collector.set_festival_metrics("BigBillionDays", 12.0)
                elif today.month == 12 and today.day == 31:  # NYE
                    self.collector.set_festival_metrics("NewYearEve", 6.0)
                
                # RBI compliance lag simulation
                for bank in UPIBank:
                    lag = random.uniform(0, 300)  # 0 to 5 minutes lag
                    self.collector.update_rbi_compliance_lag(bank, lag)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error("Periodic updates error", error=str(e))
                await asyncio.sleep(60)

    async def _bank_health_checker(self):
        """
        Bank availability को check करता है
        Health check API calls के through
        """
        while self.running:
            try:
                for bank in UPIBank:
                    # Simulate bank health check
                    # Real implementation में actual API calls होंगी
                    is_healthy = random.random() > 0.05  # 95% uptime simulation
                    self.collector.update_bank_availability(bank, is_healthy)
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error("Bank health check error", error=str(e))
                await asyncio.sleep(30)

    def stop_monitoring(self):
        """Monitoring service को gracefully stop करता है"""
        self.running = False
        logger.info("UPI monitoring service stopped")

def main():
    """
    Main function - UPI monitoring service run करता है
    Production deployment के लिए entry point
    """
    print("🚀 Starting UPI Prometheus Monitoring System")
    print("📊 Metrics available at: http://localhost:8000/metrics")
    print("🏦 Monitoring Indian banks: SBI, HDFC, ICICI, Kotak, Axis")
    print("💳 Transaction types: P2P, P2M, Bill Payment, E-commerce")
    print("🌟 Festival awareness: Diwali, BBD, NYE traffic spikes")
    print("\nPress Ctrl+C to stop the service\n")
    
    service = UPIMonitoringService(port=8000)
    
    try:
        asyncio.run(service.start_monitoring())
    except KeyboardInterrupt:
        print("\n🛑 Stopping UPI monitoring service...")
        service.stop_monitoring()
        print("✅ Service stopped successfully!")

if __name__ == "__main__":
    main()

"""
Production Deployment Notes:

1. Environment Variables:
   export PROMETHEUS_PORT=8000
   export LOG_LEVEL=INFO
   export INDIAN_REGION=true

2. Docker Deployment:
   docker build -t upi-prometheus-monitor .
   docker run -p 8000:8000 upi-prometheus-monitor

3. Kubernetes Deployment:
   - Add service discovery annotations
   - Configure resource limits
   - Set up proper RBAC

4. Monitoring Targets:
   - Bank APIs health endpoints
   - Payment gateway status
   - RBI compliance systems
   - Regional performance nodes

5. Alert Rules:
   - UPI success rate < 95%
   - Bank availability = 0
   - Response time > 5 seconds
   - Error rate > 5%

6. Indian Context Optimizations:
   - Festival season scaling
   - Regional performance tracking
   - Multi-language error handling
   - Compliance reporting automation

Example PromQL Queries:
- Bank success rate: rate(upi_transactions_total{status="success"}[5m]) / rate(upi_transactions_total[5m]) * 100
- P95 response time: histogram_quantile(0.95, rate(upi_response_time_seconds_bucket[5m]))
- Festival traffic spike: upi_festival_transaction_multiplier > 5
- Regional performance: avg by (city) (rate(upi_response_time_seconds_sum[5m]) / rate(upi_response_time_seconds_count[5m]))
"""