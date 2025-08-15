#!/usr/bin/env python3
"""
Paytm-style Payment Gateway Circuit Breaker
Indian payment ecosystem के लिए specialized circuit breaker

Paytm जैसे payment systems में different types की failures होती हैं
यह implementation Indian payment gateway की real challenges handle करती है
"""

import time
import random
import threading
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import hashlib


class PaymentMethod(Enum):
    """Different payment methods in India"""
    UPI = "upi"                    # UPI payments (PhonePe, GPay, Paytm)
    CREDIT_CARD = "credit_card"    # Credit card payments
    DEBIT_CARD = "debit_card"      # Debit card payments
    NET_BANKING = "net_banking"    # Internet banking
    WALLET = "wallet"              # Digital wallets
    BNPL = "buy_now_pay_later"     # Buy Now Pay Later


class BankProvider(Enum):
    """Major Indian banks and payment providers"""
    SBI = "sbi"                    # State Bank of India
    HDFC = "hdfc"                  # HDFC Bank
    ICICI = "icici"                # ICICI Bank
    AXIS = "axis"                  # Axis Bank
    KOTAK = "kotak"                # Kotak Bank
    PAYTM = "paytm"                # Paytm Bank
    PHONEPE = "phonepe"            # PhonePe
    GPAY = "gpay"                  # Google Pay
    BHIM = "bhim"                  # BHIM UPI


class PaymentError(Enum):
    """Common payment errors in Indian ecosystem"""
    UPI_TIMEOUT = "upi_transaction_timeout"
    INSUFFICIENT_BALANCE = "insufficient_account_balance"
    INVALID_VPA = "invalid_virtual_payment_address"
    BANK_SERVER_DOWN = "bank_server_unavailable"
    DAILY_LIMIT_EXCEEDED = "daily_transaction_limit_exceeded"
    KYC_REQUIRED = "kyc_verification_required"
    NETWORK_ISSUE = "network_connectivity_issue"
    OTP_FAILED = "otp_verification_failed"
    CARD_EXPIRED = "card_expired"
    FRAUDULENT_TRANSACTION = "transaction_flagged_as_fraud"


@dataclass
class PaymentRequest:
    """Payment request structure"""
    transaction_id: str
    amount: float
    currency: str = "INR"
    payment_method: PaymentMethod = PaymentMethod.UPI
    bank_provider: BankProvider = BankProvider.PAYTM
    merchant_id: str = "PAYTM_MERCHANT_001"
    customer_id: str = ""
    upi_id: Optional[str] = None
    card_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PaymentResponse:
    """Payment response structure"""
    transaction_id: str
    status: str  # SUCCESS, FAILED, PENDING
    amount: float
    gateway_response_code: str
    gateway_message: str
    bank_ref_number: Optional[str] = None
    processed_at: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0


@dataclass
class CircuitBreakerConfig:
    """Paytm-specific circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: float = 30.0
    max_concurrent_requests: int = 1000
    
    # Indian payment specific settings
    festival_season_multiplier: float = 2.0    # Diwali, Holi के time ज्यादा traffic
    cricket_match_multiplier: float = 1.5      # IPL matches के during high load
    salary_day_multiplier: float = 1.8         # Month end में ज्यादा transactions
    
    # Bank-specific failure rates (based on historical data)
    bank_reliability: Dict[BankProvider, float] = field(default_factory=lambda: {
        BankProvider.SBI: 0.95,       # SBI most reliable but slow
        BankProvider.HDFC: 0.98,      # HDFC very reliable
        BankProvider.ICICI: 0.97,     # ICICI good reliability
        BankProvider.AXIS: 0.94,      # Axis decent
        BankProvider.KOTAK: 0.96,     # Kotak good
        BankProvider.PAYTM: 0.99,     # Paytm wallet most reliable
        BankProvider.PHONEPE: 0.98,   # PhonePe very good
        BankProvider.GPAY: 0.98,      # GPay very good
        BankProvider.BHIM: 0.92       # BHIM NPCI official but slower
    })


class PaytmCircuitBreaker:
    """
    Paytm-style Payment Gateway Circuit Breaker
    Indian payment ecosystem की complexity को handle करता है
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        
        # Circuit states per bank/payment method combination
        self.circuit_states: Dict[str, str] = {}  # key = f"{bank}_{method}"
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, float] = {}
        
        # Performance metrics per circuit
        self.metrics: Dict[str, Dict] = {}
        
        # Active requests tracking
        self.active_requests: Dict[str, int] = {}  # per circuit
        
        # Special event handling
        self.current_load_multiplier = 1.0
        self.is_festival_season = False
        self.is_cricket_match_time = False
        self.is_salary_day = False
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize all circuits
        self._initialize_circuits()
        
        print("💳 Paytm Payment Circuit Breaker initialized")
        print(f"   - Supporting {len(PaymentMethod)} payment methods")
        print(f"   - Supporting {len(BankProvider)} bank providers")
        print(f"   - Total circuits: {len(self.circuit_states)}")
    
    def _initialize_circuits(self):
        """Initialize circuit breaker for each bank-payment method combination"""
        for payment_method in PaymentMethod:
            for bank in BankProvider:
                circuit_key = f"{bank.value}_{payment_method.value}"
                
                self.circuit_states[circuit_key] = "CLOSED"
                self.failure_counts[circuit_key] = 0
                self.success_counts[circuit_key] = 0
                self.last_failure_times[circuit_key] = 0
                self.active_requests[circuit_key] = 0
                
                self.metrics[circuit_key] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_response_time": 0.0,
                    "last_24h_success_rate": 100.0,
                    "peak_concurrent_requests": 0
                }
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process payment through appropriate circuit breaker
        """
        circuit_key = f"{request.bank_provider.value}_{request.payment_method.value}"
        start_time = time.time()
        
        # Check load conditions and adjust thresholds
        self._adjust_for_load_conditions()
        
        with self._lock:
            # Check if circuit should reject request
            if self._should_reject_request(circuit_key, request):
                return self._create_failure_response(
                    request, 
                    "CIRCUIT_BREAKER_OPEN",
                    f"Payment route {circuit_key} is temporarily unavailable"
                )
            
            # Check concurrent request limits
            if self.active_requests[circuit_key] >= self._get_adjusted_limit(circuit_key):
                return self._create_failure_response(
                    request,
                    "RATE_LIMITED", 
                    "Too many concurrent requests. Please try again."
                )
            
            # Track active request
            self.active_requests[circuit_key] += 1
            self.metrics[circuit_key]["peak_concurrent_requests"] = max(
                self.metrics[circuit_key]["peak_concurrent_requests"],
                self.active_requests[circuit_key]
            )
        
        try:
            # Process payment through simulated gateway
            response = self._process_payment_internal(request, circuit_key)
            
            # Record success
            processing_time = time.time() - start_time
            self._record_success(circuit_key, processing_time)
            
            return response
        
        except Exception as e:
            # Record failure
            processing_time = time.time() - start_time
            self._record_failure(circuit_key, str(e), processing_time)
            
            return self._create_failure_response(request, "GATEWAY_ERROR", str(e))
        
        finally:
            with self._lock:
                self.active_requests[circuit_key] -= 1
    
    def _should_reject_request(self, circuit_key: str, request: PaymentRequest) -> bool:
        """Check if request should be rejected based on circuit state"""
        state = self.circuit_states[circuit_key]
        
        if state == "CLOSED":
            return False
        
        if state == "OPEN":
            # Check if timeout has passed for recovery
            last_failure = self.last_failure_times[circuit_key]
            if time.time() - last_failure >= self.config.timeout_seconds:
                self.circuit_states[circuit_key] = "HALF_OPEN"
                self.success_counts[circuit_key] = 0
                print(f"🟡 Circuit {circuit_key} moved to HALF_OPEN")
                return False
            return True
        
        # HALF_OPEN state - allow limited requests
        return False
    
    def _get_adjusted_limit(self, circuit_key: str) -> int:
        """Get adjusted concurrent request limit based on current conditions"""
        base_limit = self.config.max_concurrent_requests // len(self.circuit_states)
        adjusted_limit = base_limit * self.current_load_multiplier
        
        # Bank-specific adjustments
        bank = circuit_key.split('_')[0]
        try:
            bank_enum = BankProvider(bank)
            bank_reliability = self.config.bank_reliability.get(bank_enum, 0.95)
            adjusted_limit *= bank_reliability
        except ValueError:
            pass
        
        return max(1, int(adjusted_limit))
    
    def _adjust_for_load_conditions(self):
        """Adjust circuit breaker behavior based on external conditions"""
        current_hour = datetime.now().hour
        current_date = datetime.now().date()
        
        # Reset multiplier
        self.current_load_multiplier = 1.0
        
        # Festival season detection (approximate)
        if current_date.month in [10, 11]:  # Diwali season
            self.is_festival_season = True
            self.current_load_multiplier *= self.config.festival_season_multiplier
            
        # Cricket match time (evening hours during cricket season)
        if current_hour in [19, 20, 21, 22] and current_date.month in [3, 4, 5]:  # IPL season
            self.is_cricket_match_time = True
            self.current_load_multiplier *= self.config.cricket_match_multiplier
            
        # Salary day (end of month)
        if current_date.day >= 28:
            self.is_salary_day = True
            self.current_load_multiplier *= self.config.salary_day_multiplier
    
    def _process_payment_internal(self, request: PaymentRequest, circuit_key: str) -> PaymentResponse:
        """
        Internal payment processing simulation
        Different banks और payment methods के लिए different behavior
        """
        bank = BankProvider(circuit_key.split('_')[0])
        method = PaymentMethod(circuit_key.split('_')[1])
        
        # Simulate network delay based on bank and method
        processing_delay = self._get_processing_delay(bank, method)
        time.sleep(processing_delay)
        
        # Simulate failures based on bank reliability and current load
        failure_probability = self._calculate_failure_probability(bank, method)
        
        if random.random() < failure_probability:
            # Generate realistic Indian payment errors
            error = self._generate_realistic_error(bank, method)
            raise Exception(f"{error.value}")
        
        # Generate successful response
        return PaymentResponse(
            transaction_id=request.transaction_id,
            status="SUCCESS",
            amount=request.amount,
            gateway_response_code="00",  # Success code
            gateway_message="Transaction completed successfully",
            bank_ref_number=f"BRN{random.randint(100000000000, 999999999999)}",
            processing_time_ms=processing_delay * 1000
        )
    
    def _get_processing_delay(self, bank: BankProvider, method: PaymentMethod) -> float:
        """Get realistic processing delay based on bank and payment method"""
        base_delays = {
            PaymentMethod.UPI: 2.0,
            PaymentMethod.CREDIT_CARD: 5.0,
            PaymentMethod.DEBIT_CARD: 4.0,
            PaymentMethod.NET_BANKING: 8.0,
            PaymentMethod.WALLET: 1.0,
            PaymentMethod.BNPL: 10.0
        }
        
        bank_speed_factors = {
            BankProvider.SBI: 1.5,      # SBI slower
            BankProvider.HDFC: 0.8,     # HDFC faster
            BankProvider.ICICI: 0.9,    # ICICI good speed
            BankProvider.AXIS: 1.1,     # Axis moderate
            BankProvider.KOTAK: 0.9,    # Kotak good
            BankProvider.PAYTM: 0.5,    # Paytm wallet fastest
            BankProvider.PHONEPE: 0.6,  # PhonePe very fast
            BankProvider.GPAY: 0.6,     # GPay very fast
            BankProvider.BHIM: 1.3      # BHIM slower (NPCI)
        }
        
        base_delay = base_delays.get(method, 3.0)
        speed_factor = bank_speed_factors.get(bank, 1.0)
        
        # Add load-based delay
        load_delay = (self.current_load_multiplier - 1.0) * 2.0
        
        # Add random jitter
        jitter = random.uniform(0.1, 0.5)
        
        total_delay = (base_delay * speed_factor) + load_delay + jitter
        return max(0.5, total_delay)
    
    def _calculate_failure_probability(self, bank: BankProvider, method: PaymentMethod) -> float:
        """Calculate failure probability based on various factors"""
        # Base failure rate
        base_failure_rate = 1.0 - self.config.bank_reliability.get(bank, 0.95)
        
        # Method-specific adjustments
        method_risk_factors = {
            PaymentMethod.UPI: 1.0,         # Standard risk
            PaymentMethod.CREDIT_CARD: 0.8, # Lower risk, better fraud detection
            PaymentMethod.DEBIT_CARD: 1.1,  # Slightly higher risk
            PaymentMethod.NET_BANKING: 1.2, # Higher risk, more complex
            PaymentMethod.WALLET: 0.3,      # Lowest risk, pre-funded
            PaymentMethod.BNPL: 1.5         # Highest risk, credit checks
        }
        
        method_factor = method_risk_factors.get(method, 1.0)
        
        # Load-based failure increase
        load_factor = (self.current_load_multiplier - 1.0) * 0.5 + 1.0
        
        # Time-based factors (Indian banking hours)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Night time
            time_factor = 1.3  # Higher failure rate during maintenance
        elif 9 <= current_hour <= 17:  # Banking hours
            time_factor = 0.8  # Lower failure rate
        else:
            time_factor = 1.0
        
        total_failure_rate = base_failure_rate * method_factor * load_factor * time_factor
        return min(0.9, total_failure_rate)  # Cap at 90%
    
    def _generate_realistic_error(self, bank: BankProvider, method: PaymentMethod) -> PaymentError:
        """Generate realistic payment errors based on context"""
        if method == PaymentMethod.UPI:
            return random.choice([
                PaymentError.UPI_TIMEOUT,
                PaymentError.INSUFFICIENT_BALANCE, 
                PaymentError.INVALID_VPA,
                PaymentError.DAILY_LIMIT_EXCEEDED,
                PaymentError.NETWORK_ISSUE
            ])
        
        elif method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            return random.choice([
                PaymentError.CARD_EXPIRED,
                PaymentError.INSUFFICIENT_BALANCE,
                PaymentError.OTP_FAILED,
                PaymentError.FRAUDULENT_TRANSACTION,
                PaymentError.DAILY_LIMIT_EXCEEDED
            ])
        
        elif method == PaymentMethod.NET_BANKING:
            return random.choice([
                PaymentError.BANK_SERVER_DOWN,
                PaymentError.OTP_FAILED,
                PaymentError.NETWORK_ISSUE,
                PaymentError.INSUFFICIENT_BALANCE
            ])
        
        elif method == PaymentMethod.WALLET:
            return random.choice([
                PaymentError.INSUFFICIENT_BALANCE,
                PaymentError.KYC_REQUIRED,
                PaymentError.DAILY_LIMIT_EXCEEDED
            ])
        
        else:  # BNPL
            return random.choice([
                PaymentError.KYC_REQUIRED,
                PaymentError.FRAUDULENT_TRANSACTION,
                PaymentError.INSUFFICIENT_BALANCE
            ])
    
    def _create_failure_response(self, request: PaymentRequest, error_code: str, message: str) -> PaymentResponse:
        """Create failure response"""
        return PaymentResponse(
            transaction_id=request.transaction_id,
            status="FAILED",
            amount=request.amount,
            gateway_response_code=error_code,
            gateway_message=message
        )
    
    def _record_success(self, circuit_key: str, processing_time: float):
        """Record successful payment"""
        with self._lock:
            metrics = self.metrics[circuit_key]
            metrics["total_requests"] += 1
            metrics["successful_requests"] += 1
            
            # Update average response time
            total_requests = metrics["total_requests"]
            old_avg = metrics["avg_response_time"]
            metrics["avg_response_time"] = ((old_avg * (total_requests - 1)) + processing_time) / total_requests
            
            # Circuit state management
            state = self.circuit_states[circuit_key]
            if state == "HALF_OPEN":
                self.success_counts[circuit_key] += 1
                if self.success_counts[circuit_key] >= self.config.success_threshold:
                    self.circuit_states[circuit_key] = "CLOSED"
                    self.failure_counts[circuit_key] = 0
                    print(f"✅ Circuit {circuit_key} CLOSED - Service recovered")
            elif state == "CLOSED":
                self.failure_counts[circuit_key] = 0  # Reset on success
    
    def _record_failure(self, circuit_key: str, error: str, processing_time: float):
        """Record failed payment"""
        with self._lock:
            metrics = self.metrics[circuit_key]
            metrics["total_requests"] += 1
            
            self.failure_counts[circuit_key] += 1
            self.last_failure_times[circuit_key] = time.time()
            
            # Circuit state management
            state = self.circuit_states[circuit_key]
            adjusted_threshold = int(self.config.failure_threshold / self.current_load_multiplier)
            
            if state == "CLOSED" and self.failure_counts[circuit_key] >= adjusted_threshold:
                self.circuit_states[circuit_key] = "OPEN"
                print(f"🔴 Circuit {circuit_key} OPENED - {error}")
            elif state == "HALF_OPEN":
                self.circuit_states[circuit_key] = "OPEN"
                self.success_counts[circuit_key] = 0
                print(f"🔴 Circuit {circuit_key} back to OPEN - {error}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        total_circuits = len(self.circuit_states)
        closed_circuits = sum(1 for state in self.circuit_states.values() if state == "CLOSED")
        open_circuits = sum(1 for state in self.circuit_states.values() if state == "OPEN")
        half_open_circuits = total_circuits - closed_circuits - open_circuits
        
        # Calculate overall success rates by payment method and bank
        method_stats = {}
        bank_stats = {}
        
        for circuit_key, metrics in self.metrics.items():
            bank, method = circuit_key.split('_', 1)
            total_req = metrics["total_requests"]
            success_req = metrics["successful_requests"]
            
            if total_req > 0:
                success_rate = (success_req / total_req) * 100
                
                if method not in method_stats:
                    method_stats[method] = {"total": 0, "successful": 0}
                method_stats[method]["total"] += total_req
                method_stats[method]["successful"] += success_req
                
                if bank not in bank_stats:
                    bank_stats[bank] = {"total": 0, "successful": 0}
                bank_stats[bank]["total"] += total_req
                bank_stats[bank]["successful"] += success_req
        
        # Calculate success rates
        for method in method_stats:
            if method_stats[method]["total"] > 0:
                method_stats[method]["success_rate"] = (
                    method_stats[method]["successful"] / method_stats[method]["total"] * 100
                )
        
        for bank in bank_stats:
            if bank_stats[bank]["total"] > 0:
                bank_stats[bank]["success_rate"] = (
                    bank_stats[bank]["successful"] / bank_stats[bank]["total"] * 100
                )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "circuit_health": {
                "total_circuits": total_circuits,
                "healthy_circuits": closed_circuits,
                "degraded_circuits": half_open_circuits,
                "failed_circuits": open_circuits,
                "overall_health_percentage": (closed_circuits / total_circuits) * 100
            },
            "load_conditions": {
                "current_multiplier": self.current_load_multiplier,
                "is_festival_season": self.is_festival_season,
                "is_cricket_match_time": self.is_cricket_match_time,
                "is_salary_day": self.is_salary_day
            },
            "payment_method_stats": method_stats,
            "bank_provider_stats": bank_stats,
            "top_failing_circuits": self._get_top_failing_circuits(),
            "recommended_actions": self._get_recommended_actions()
        }
    
    def _get_top_failing_circuits(self) -> List[Dict[str, Any]]:
        """Get circuits with highest failure rates"""
        failing_circuits = []
        
        for circuit_key, metrics in self.metrics.items():
            total_req = metrics["total_requests"]
            if total_req >= 10:  # Only consider circuits with significant traffic
                success_rate = (metrics["successful_requests"] / total_req) * 100
                if success_rate < 80:  # Consider circuits with <80% success rate as failing
                    failing_circuits.append({
                        "circuit": circuit_key,
                        "success_rate": round(success_rate, 2),
                        "total_requests": total_req,
                        "state": self.circuit_states[circuit_key],
                        "avg_response_time": round(metrics["avg_response_time"], 3)
                    })
        
        return sorted(failing_circuits, key=lambda x: x["success_rate"])[:5]
    
    def _get_recommended_actions(self) -> List[str]:
        """Get recommended actions based on system state"""
        recommendations = []
        
        open_circuits = sum(1 for state in self.circuit_states.values() if state == "OPEN")
        total_circuits = len(self.circuit_states)
        
        if open_circuits > total_circuits * 0.3:
            recommendations.append("🚨 High circuit failure rate - Consider enabling backup payment routes")
        
        if self.current_load_multiplier > 1.5:
            recommendations.append("📈 High load detected - Consider scaling payment infrastructure")
        
        if self.is_festival_season:
            recommendations.append("🎉 Festival season - Monitor UPI and wallet transactions closely")
        
        if self.is_cricket_match_time:
            recommendations.append("🏏 Cricket match time - Expect higher betting/payment traffic")
        
        failing_circuits = self._get_top_failing_circuits()
        if failing_circuits:
            recommendations.append(f"⚠️  {len(failing_circuits)} circuits showing high failure rates")
        
        return recommendations


def test_paytm_circuit_breaker():
    """Test Paytm payment circuit breaker with realistic scenarios"""
    print("🧪 Testing Paytm Payment Gateway Circuit Breaker")
    print("=" * 70)
    
    # Create Paytm circuit breaker with Indian payment configuration
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=15.0,
        max_concurrent_requests=100
    )
    
    pcb = PaytmCircuitBreaker(config)
    
    # Set festival season for testing
    pcb.is_festival_season = True
    pcb._adjust_for_load_conditions()
    
    print("\n📊 Phase 1: Testing different payment methods")
    print("-" * 60)
    
    # Test various Indian payment scenarios
    test_payments = [
        # UPI Payments
        PaymentRequest("TXN_001", 500.0, "INR", PaymentMethod.UPI, BankProvider.PAYTM, upi_id="user@paytm"),
        PaymentRequest("TXN_002", 1000.0, "INR", PaymentMethod.UPI, BankProvider.PHONEPE, upi_id="user@ybl"),
        PaymentRequest("TXN_003", 2000.0, "INR", PaymentMethod.UPI, BankProvider.GPAY, upi_id="user@okicici"),
        
        # Card Payments
        PaymentRequest("TXN_004", 5000.0, "INR", PaymentMethod.CREDIT_CARD, BankProvider.HDFC, card_number="****1234"),
        PaymentRequest("TXN_005", 3000.0, "INR", PaymentMethod.DEBIT_CARD, BankProvider.SBI, card_number="****5678"),
        
        # Net Banking
        PaymentRequest("TXN_006", 10000.0, "INR", PaymentMethod.NET_BANKING, BankProvider.ICICI),
        
        # Wallet
        PaymentRequest("TXN_007", 500.0, "INR", PaymentMethod.WALLET, BankProvider.PAYTM),
        
        # BNPL
        PaymentRequest("TXN_008", 15000.0, "INR", PaymentMethod.BNPL, BankProvider.PAYTM)
    ]
    
    for payment in test_payments:
        response = pcb.process_payment(payment)
        
        status_emoji = "✅" if response.status == "SUCCESS" else "❌"
        print(f"{status_emoji} {payment.transaction_id}: {payment.payment_method.value.upper()} "
              f"via {payment.bank_provider.value.upper()} - ₹{payment.amount} - {response.status}")
        
        if response.status == "FAILED":
            print(f"   Error: {response.gateway_message}")
        
        time.sleep(0.5)
    
    print("\n📊 Phase 2: Load testing UPI payments (Diwali scenario)")
    print("-" * 60)
    
    # Simulate Diwali rush - lots of UPI payments
    successful_payments = 0
    failed_payments = 0
    
    for i in range(25):
        banks = [BankProvider.PAYTM, BankProvider.PHONEPE, BankProvider.GPAY, BankProvider.BHIM]
        selected_bank = random.choice(banks)
        
        payment = PaymentRequest(
            f"DIWALI_TXN_{i+1:03d}",
            random.uniform(100, 5000),
            "INR",
            PaymentMethod.UPI,
            selected_bank,
            upi_id=f"user{i}@{selected_bank.value}"
        )
        
        response = pcb.process_payment(payment)
        
        if response.status == "SUCCESS":
            successful_payments += 1
            print(f"✅ Diwali payment {i+1}: ₹{payment.amount:.0f} via {selected_bank.value}")
        else:
            failed_payments += 1
            print(f"❌ Diwali payment {i+1}: Failed - {response.gateway_response_code}")
        
        time.sleep(0.2)  # Fast payments during rush
    
    print(f"\n🎉 Diwali Rush Results:")
    print(f"   Successful: {successful_payments}")
    print(f"   Failed: {failed_payments}")
    print(f"   Success Rate: {(successful_payments/(successful_payments+failed_payments)*100):.1f}%")
    
    print("\n📊 Phase 3: Testing circuit recovery")
    print("-" * 60)
    
    # Wait for some circuits to recover
    print("Waiting for circuit recovery...")
    time.sleep(16)
    
    # Test recovery with reliable payments
    print("Testing recovery with wallet payments (most reliable):")
    for i in range(5):
        payment = PaymentRequest(
            f"RECOVERY_TXN_{i+1}",
            1000.0,
            "INR",
            PaymentMethod.WALLET,
            BankProvider.PAYTM
        )
        
        response = pcb.process_payment(payment)
        status_emoji = "✅" if response.status == "SUCCESS" else "❌"
        print(f"{status_emoji} Recovery payment {i+1}: {response.status}")
        
        time.sleep(1)
    
    print("\n📈 System Health Report:")
    print("=" * 60)
    
    health_report = pcb.get_system_health()
    
    print("🏥 Circuit Health:")
    circuit_health = health_report["circuit_health"]
    print(f"   Total Circuits: {circuit_health['total_circuits']}")
    print(f"   Healthy: {circuit_health['healthy_circuits']} "
          f"({circuit_health['overall_health_percentage']:.1f}%)")
    print(f"   Degraded: {circuit_health['degraded_circuits']}")
    print(f"   Failed: {circuit_health['failed_circuits']}")
    
    print("\n💳 Payment Method Performance:")
    for method, stats in health_report["payment_method_stats"].items():
        if stats["total"] > 0:
            print(f"   {method.upper()}: {stats['success_rate']:.1f}% "
                  f"({stats['successful']}/{stats['total']})")
    
    print("\n🏦 Bank Provider Performance:")
    for bank, stats in health_report["bank_provider_stats"].items():
        if stats["total"] > 0:
            print(f"   {bank.upper()}: {stats['success_rate']:.1f}% "
                  f"({stats['successful']}/{stats['total']})")
    
    if health_report["top_failing_circuits"]:
        print("\n⚠️  Top Failing Circuits:")
        for circuit in health_report["top_failing_circuits"]:
            print(f"   {circuit['circuit']}: {circuit['success_rate']:.1f}% "
                  f"(State: {circuit['state']})")
    
    print("\n🎯 Recommendations:")
    for recommendation in health_report["recommended_actions"]:
        print(f"   {recommendation}")
    
    print("\n💡 Indian Payment Insights:")
    print("   - UPI transactions are fastest but can timeout during peak hours")
    print("   - Wallet payments are most reliable due to pre-funded nature")
    print("   - Net banking has highest processing time but good success rate")
    print("   - BNPL requires additional KYC checks, hence higher failure rate")
    print("   - Festival seasons see 2x normal traffic with higher UPI usage")


if __name__ == "__main__":
    test_paytm_circuit_breaker()