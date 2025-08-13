#!/usr/bin/env python3
"""
Circuit Breaker Pattern Implementation - Episode 50: System Design Interview Mastery
IRCTC Payment Gateway Circuit Breaker System

Circuit breaker जैसे घर का electrical circuit breaker है।
जब बहुत ज्यादा load आता है तो automatically switch off हो जाता है।

Author: Hindi Podcast Series
Topic: Circuit Breaker Pattern with Indian Service Examples
"""

import time
import threading
import random
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
import logging
import json
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states - Switch की अवस्थाएं"""
    CLOSED = "closed"         # Normal operation - सब कुछ ठीक
    OPEN = "open"            # Circuit open - Service blocked
    HALF_OPEN = "half_open"  # Testing phase - Limited requests allowed

class FailureType(Enum):
    """Types of failures that can trigger circuit breaker"""
    TIMEOUT = "timeout"                    # Request timeout
    CONNECTION_ERROR = "connection_error" # Network issues
    SERVER_ERROR = "server_error"        # 5xx HTTP errors
    RATE_LIMIT = "rate_limit"           # Rate limiting
    AUTHENTICATION = "authentication"    # Auth failures
    BUSINESS_LOGIC = "business_logic"   # Business rule violations

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5              # Failures needed to open circuit
    success_threshold: int = 3              # Successes needed to close circuit
    timeout_duration: float = 5.0          # Request timeout in seconds
    recovery_timeout: float = 60.0         # Time before trying half-open
    monitoring_window: int = 60             # Monitoring window in seconds
    half_open_max_calls: int = 3           # Max calls in half-open state
    failure_rate_threshold: float = 50.0   # Failure rate % to open circuit

@dataclass
class CallResult:
    """Result of a service call"""
    success: bool
    response_time: float
    error_type: Optional[FailureType] = None
    error_message: str = ""
    timestamp: float = field(default_factory=time.time)

class CircuitBreakerStats:
    """Statistics tracking for circuit breaker"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.call_history: deque = deque()
        self.lock = threading.Lock()
        self.reset_stats()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.timeouts = 0
        self.circuit_open_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        self.failure_types = defaultdict(int)
    
    def record_call(self, result: CallResult):
        """Record a service call result"""
        with self.lock:
            current_time = time.time()
            
            # Remove old entries outside window
            while (self.call_history and 
                   current_time - self.call_history[0].timestamp > self.window_size):
                old_result = self.call_history.popleft()
                if old_result.success:
                    self.successful_calls = max(0, self.successful_calls - 1)
                else:
                    self.failed_calls = max(0, self.failed_calls - 1)
                    if old_result.error_type:
                        self.failure_types[old_result.error_type] = max(0, 
                            self.failure_types[old_result.error_type] - 1)
                self.total_calls = max(0, self.total_calls - 1)
            
            # Add new result
            self.call_history.append(result)
            self.total_calls += 1
            
            if result.success:
                self.successful_calls += 1
                self.last_success_time = current_time
            else:
                self.failed_calls += 1
                self.last_failure_time = current_time
                if result.error_type:
                    self.failure_types[result.error_type] += 1
                    if result.error_type == FailureType.TIMEOUT:
                        self.timeouts += 1
    
    def get_failure_rate(self) -> float:
        """Get current failure rate percentage"""
        if self.total_calls == 0:
            return 0.0
        return (self.failed_calls / self.total_calls) * 100
    
    def get_recent_failures(self, seconds: int = 10) -> int:
        """Get number of failures in recent seconds"""
        current_time = time.time()
        recent_failures = 0
        
        for result in reversed(self.call_history):
            if current_time - result.timestamp > seconds:
                break
            if not result.success:
                recent_failures += 1
        
        return recent_failures

class CircuitBreaker:
    """Circuit Breaker Pattern Implementation - IRCTC Style"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        """Initialize circuit breaker"""
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats(self.config.monitoring_window)
        self.last_failure_time = 0
        self.half_open_calls = 0
        self.lock = threading.RLock()
        
        # State transition callbacks
        self.on_state_change: List[Callable] = []
        
        logger.info(f"🔌 Circuit Breaker '{name}' initialized in {self.state.value.upper()} state")
    
    def add_state_change_listener(self, callback: Callable):
        """Add callback for state changes"""
        self.on_state_change.append(callback)
    
    def _transition_to_state(self, new_state: CircuitState, reason: str = ""):
        """Transition to new state with logging"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            
            logger.info(f"🔄 Circuit '{self.name}': {old_state.value.upper()} → {new_state.value.upper()}")
            if reason:
                logger.info(f"   Reason: {reason}")
            
            # Notify listeners
            for callback in self.on_state_change:
                try:
                    callback(self.name, old_state, new_state, reason)
                except Exception as e:
                    logger.error(f"State change callback error: {e}")
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Check failure threshold
        recent_failures = self.stats.get_recent_failures(seconds=30)
        if recent_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate
        failure_rate = self.stats.get_failure_rate()
        if (failure_rate >= self.config.failure_rate_threshold and 
            self.stats.total_calls >= 10):  # Minimum calls for rate calculation
            return True
        
        return False
    
    def _should_close_circuit(self) -> bool:
        """Determine if circuit should be closed from half-open state"""
        # Need consecutive successes in half-open state
        recent_results = list(self.stats.call_history)[-self.config.success_threshold:]
        if len(recent_results) < self.config.success_threshold:
            return False
        
        return all(result.success for result in recent_results)
    
    def _can_attempt_call(self) -> bool:
        """Check if call can be attempted in current state"""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                self._transition_to_state(CircuitState.HALF_OPEN, 
                                        "Recovery timeout expired")
                self.half_open_calls = 0
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function call with circuit breaker protection"""
        with self.lock:
            # Check if call can be attempted
            if not self._can_attempt_call():
                self.stats.circuit_open_count += 1
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN - calls blocked"
                )
            
            # Track half-open calls
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
        
        # Execute the actual call
        start_time = time.time()
        result = None
        
        try:
            # Apply timeout
            if self.config.timeout_duration > 0:
                result = self._call_with_timeout(func, self.config.timeout_duration, 
                                               *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record successful call
            call_result = CallResult(
                success=True,
                response_time=time.time() - start_time
            )
            self._handle_success(call_result)
            
            return result
        
        except TimeoutError:
            call_result = CallResult(
                success=False,
                response_time=time.time() - start_time,
                error_type=FailureType.TIMEOUT,
                error_message="Request timeout"
            )
            self._handle_failure(call_result)
            raise
        
        except Exception as e:
            # Classify the error
            error_type = self._classify_error(e)
            call_result = CallResult(
                success=False,
                response_time=time.time() - start_time,
                error_type=error_type,
                error_message=str(e)
            )
            self._handle_failure(call_result)
            raise
    
    def _call_with_timeout(self, func: Callable, timeout: float, *args, **kwargs):
        """Execute function with timeout"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                raise TimeoutError(f"Function call exceeded {timeout}s timeout")
    
    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type for circuit breaker logic"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            return FailureType.TIMEOUT
        elif 'connection' in error_str or 'network' in error_str:
            return FailureType.CONNECTION_ERROR
        elif 'server error' in error_str or '5' in error_str:
            return FailureType.SERVER_ERROR
        elif 'rate limit' in error_str:
            return FailureType.RATE_LIMIT
        elif 'authentication' in error_str or 'unauthorized' in error_str:
            return FailureType.AUTHENTICATION
        else:
            return FailureType.BUSINESS_LOGIC
    
    def _handle_success(self, call_result: CallResult):
        """Handle successful call"""
        with self.lock:
            self.stats.record_call(call_result)
            
            if self.state == CircuitState.HALF_OPEN:
                if self._should_close_circuit():
                    self._transition_to_state(CircuitState.CLOSED, 
                                            f"Consecutive successes achieved")
            elif self.state == CircuitState.OPEN:
                # Shouldn't happen, but just in case
                self._transition_to_state(CircuitState.HALF_OPEN, "Unexpected success")
    
    def _handle_failure(self, call_result: CallResult):
        """Handle failed call"""
        with self.lock:
            self.stats.record_call(call_result)
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.CLOSED:
                if self._should_open_circuit():
                    self._transition_to_state(CircuitState.OPEN, 
                                            f"Failure threshold exceeded")
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state opens the circuit
                self._transition_to_state(CircuitState.OPEN, 
                                        "Failure in half-open state")
                self.half_open_calls = 0
    
    def get_stats(self) -> Dict:
        """Get circuit breaker statistics"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'total_calls': self.stats.total_calls,
                'successful_calls': self.stats.successful_calls,
                'failed_calls': self.stats.failed_calls,
                'failure_rate': self.stats.get_failure_rate(),
                'circuit_open_count': self.stats.circuit_open_count,
                'last_failure_time': self.stats.last_failure_time,
                'last_success_time': self.stats.last_success_time,
                'failure_types': dict(self.stats.failure_types),
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'timeout_duration': self.config.timeout_duration
                }
            }
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        with self.lock:
            old_state = self.state
            self.state = CircuitState.CLOSED
            self.stats.reset_stats()
            self.half_open_calls = 0
            self.last_failure_time = 0
            
            logger.info(f"🔄 Circuit '{self.name}' manually reset from {old_state.value.upper()}")

class CircuitBreakerOpenException(Exception):
    """Exception thrown when circuit breaker is open"""
    pass

class IRCTCPaymentGateway:
    """IRCTC Payment Gateway with Circuit Breaker Protection"""
    
    def __init__(self):
        """Initialize IRCTC payment gateway services"""
        
        # Different payment services with different reliability profiles
        self.payment_services = {
            'hdfc_bank': {
                'name': 'HDFC Bank Gateway',
                'reliability': 0.95,  # 95% success rate
                'avg_response_time': 0.8,
                'circuit_breaker': CircuitBreaker(
                    'hdfc_bank',
                    CircuitBreakerConfig(
                        failure_threshold=3,
                        recovery_timeout=30.0,
                        timeout_duration=5.0
                    )
                )
            },
            'sbi_bank': {
                'name': 'SBI Bank Gateway', 
                'reliability': 0.88,  # 88% success rate
                'avg_response_time': 1.2,
                'circuit_breaker': CircuitBreaker(
                    'sbi_bank',
                    CircuitBreakerConfig(
                        failure_threshold=5,
                        recovery_timeout=45.0,
                        timeout_duration=6.0
                    )
                )
            },
            'paytm_wallet': {
                'name': 'Paytm Wallet',
                'reliability': 0.92,  # 92% success rate
                'avg_response_time': 0.5,
                'circuit_breaker': CircuitBreaker(
                    'paytm_wallet',
                    CircuitBreakerConfig(
                        failure_threshold=4,
                        recovery_timeout=20.0,
                        timeout_duration=3.0
                    )
                )
            },
            'upi_gateway': {
                'name': 'UPI Gateway',
                'reliability': 0.90,  # 90% success rate 
                'avg_response_time': 1.0,
                'circuit_breaker': CircuitBreaker(
                    'upi_gateway',
                    CircuitBreakerConfig(
                        failure_threshold=6,
                        recovery_timeout=60.0,
                        timeout_duration=4.0
                    )
                )
            }
        }
        
        # Add state change listeners
        for service_id, service in self.payment_services.items():
            service['circuit_breaker'].add_state_change_listener(self._on_circuit_state_change)
        
        self.payment_stats = defaultdict(int)
        
        print("🚂 IRCTC Payment Gateway initialized with Circuit Breaker protection")
        for service_id, service in self.payment_services.items():
            print(f"   {service['name']}: {service['reliability']*100:.0f}% reliability")
    
    def _on_circuit_state_change(self, service_name: str, old_state: CircuitState, 
                                new_state: CircuitState, reason: str):
        """Handle circuit state changes"""
        if new_state == CircuitState.OPEN:
            logger.warning(f"🚨 Payment service '{service_name}' circuit OPENED: {reason}")
            self._notify_operations_team(service_name, "CIRCUIT_OPEN", reason)
        elif new_state == CircuitState.CLOSED and old_state != CircuitState.CLOSED:
            logger.info(f"✅ Payment service '{service_name}' circuit CLOSED: Service recovered")
            self._notify_operations_team(service_name, "CIRCUIT_CLOSED", "Service recovered")
    
    def _notify_operations_team(self, service: str, event: str, details: str):
        """Simulate operations team notification"""
        print(f"📧 ALERT: {event} for {service} - {details}")
    
    def _simulate_payment_call(self, service_id: str, amount: float, pnr: str) -> Dict:
        """Simulate payment gateway call with realistic failures"""
        service = self.payment_services[service_id]
        
        # Simulate network latency
        response_time = service['avg_response_time'] + random.uniform(-0.2, 0.3)
        time.sleep(response_time)
        
        # Simulate success/failure based on reliability
        success = random.random() < service['reliability']
        
        if success:
            return {
                'status': 'success',
                'transaction_id': f'TXN_{int(time.time())}_{service_id}',
                'amount': amount,
                'pnr': pnr,
                'gateway': service['name'],
                'response_time': response_time
            }
        else:
            # Simulate different types of failures
            failure_types = [
                ('timeout', 'Payment gateway timeout'),
                ('server_error', 'Internal server error'),
                ('connection_error', 'Network connection failed'), 
                ('rate_limit', 'Rate limit exceeded'),
                ('authentication', 'Authentication failed')
            ]
            
            failure_type, error_msg = random.choice(failure_types)
            
            if failure_type == 'timeout':
                raise TimeoutError(error_msg)
            elif failure_type == 'server_error':
                raise Exception(f"Server Error: {error_msg}")
            elif failure_type == 'connection_error':
                raise Exception(f"Connection Error: {error_msg}")
            else:
                raise Exception(f"{failure_type}: {error_msg}")
    
    def process_payment(self, pnr: str, amount: float, preferred_gateway: str = None) -> Dict:
        """Process payment with circuit breaker protection and fallback"""
        
        # Determine payment gateway order
        if preferred_gateway and preferred_gateway in self.payment_services:
            gateway_order = [preferred_gateway]
            # Add other gateways as fallback
            gateway_order.extend([gw for gw in self.payment_services.keys() 
                                if gw != preferred_gateway])
        else:
            # Default order by reliability
            gateway_order = sorted(
                self.payment_services.keys(),
                key=lambda x: self.payment_services[x]['reliability'],
                reverse=True
            )
        
        last_error = None
        
        for gateway_id in gateway_order:
            service = self.payment_services[gateway_id]
            circuit_breaker = service['circuit_breaker']
            
            try:
                # Use circuit breaker to protect the call
                result = circuit_breaker.call(
                    self._simulate_payment_call,
                    gateway_id, amount, pnr
                )
                
                self.payment_stats['successful_payments'] += 1
                self.payment_stats[f'{gateway_id}_success'] += 1
                
                logger.info(f"💳 Payment successful via {service['name']}: PNR {pnr}, ₹{amount}")
                return result
            
            except CircuitBreakerOpenException as e:
                logger.warning(f"⚡ {service['name']} circuit breaker is OPEN, trying next gateway")
                self.payment_stats['circuit_breaker_blocks'] += 1
                last_error = e
                continue
            
            except Exception as e:
                logger.error(f"💥 Payment failed via {service['name']}: {e}")
                self.payment_stats['failed_payments'] += 1
                self.payment_stats[f'{gateway_id}_failure'] += 1
                last_error = e
                continue
        
        # All gateways failed
        self.payment_stats['total_payment_failures'] += 1
        raise Exception(f"All payment gateways failed. Last error: {last_error}")
    
    def get_gateway_health(self) -> Dict:
        """Get health status of all payment gateways"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'gateways': {},
            'stats': dict(self.payment_stats)
        }
        
        open_circuits = 0
        
        for service_id, service in self.payment_services.items():
            cb_stats = service['circuit_breaker'].get_stats()
            gateway_health = {
                'name': service['name'],
                'circuit_state': cb_stats['state'],
                'success_rate': 100 - cb_stats['failure_rate'],
                'total_calls': cb_stats['total_calls'],
                'failed_calls': cb_stats['failed_calls'],
                'last_failure': datetime.fromtimestamp(cb_stats['last_failure_time']).isoformat() if cb_stats['last_failure_time'] > 0 else None
            }
            
            if cb_stats['state'] == 'open':
                open_circuits += 1
                gateway_health['status'] = 'down'
            elif cb_stats['state'] == 'half_open':
                gateway_health['status'] = 'recovering'
            else:
                gateway_health['status'] = 'healthy'
            
            health_report['gateways'][service_id] = gateway_health
        
        # Determine overall status
        if open_circuits >= len(self.payment_services):
            health_report['overall_status'] = 'critical'
        elif open_circuits > 0:
            health_report['overall_status'] = 'degraded'
        
        return health_report
    
    def reset_all_circuit_breakers(self):
        """Reset all circuit breakers - Emergency operation"""
        for service_id, service in self.payment_services.items():
            service['circuit_breaker'].reset()
        
        logger.info("🔄 All payment gateway circuit breakers reset")

def demonstrate_circuit_breaker_basic():
    """Demonstrate basic circuit breaker functionality"""
    print("🔌 Circuit Breaker Basic Demo - Simple Service Protection")
    print("=" * 65)
    
    # Create a circuit breaker for a flaky service
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=10.0,
        timeout_duration=2.0
    )
    
    circuit_breaker = CircuitBreaker("demo_service", config)
    
    def flaky_service(success_rate: float = 0.7) -> str:
        """Simulate a flaky service"""
        time.sleep(random.uniform(0.5, 1.5))  # Simulate work
        
        if random.random() < success_rate:
            return "Service call successful"
        else:
            raise Exception("Service temporarily unavailable")
    
    print(f"\n🧪 Testing circuit breaker with flaky service (70% success rate)")
    print("-" * 60)
    
    # Test normal operation
    for i in range(10):
        try:
            result = circuit_breaker.call(flaky_service, 0.7)
            print(f"   Call {i+1:2d}: ✅ {result}")
        except CircuitBreakerOpenException:
            print(f"   Call {i+1:2d}: 🚫 Circuit breaker is OPEN")
        except Exception as e:
            print(f"   Call {i+1:2d}: ❌ {e}")
        
        time.sleep(0.5)
    
    # Show circuit breaker stats
    stats = circuit_breaker.get_stats()
    print(f"\n📊 Circuit Breaker Statistics:")
    print(f"   State: {stats['state'].upper()}")
    print(f"   Total Calls: {stats['total_calls']}")
    print(f"   Success Rate: {100 - stats['failure_rate']:.1f}%")
    print(f"   Circuit Opens: {stats['circuit_open_count']}")

def demonstrate_irctc_payment_gateway():
    """Demonstrate IRCTC payment gateway with circuit breakers"""
    print("\n🚂 IRCTC Payment Gateway Demo - Multi-Service Circuit Protection")
    print("=" * 75)
    
    # Initialize IRCTC payment gateway
    irctc_gateway = IRCTCPaymentGateway()
    
    # Simulate train bookings with payments
    bookings = [
        {'pnr': 'PNR001', 'amount': 1250.0, 'preferred_gateway': 'hdfc_bank'},
        {'pnr': 'PNR002', 'amount': 850.0, 'preferred_gateway': 'sbi_bank'},
        {'pnr': 'PNR003', 'amount': 2100.0, 'preferred_gateway': 'paytm_wallet'},
        {'pnr': 'PNR004', 'amount': 1500.0, 'preferred_gateway': 'upi_gateway'},
        {'pnr': 'PNR005', 'amount': 950.0, 'preferred_gateway': 'hdfc_bank'},
        {'pnr': 'PNR006', 'amount': 1750.0, 'preferred_gateway': None},  # Auto-select
        {'pnr': 'PNR007', 'amount': 1200.0, 'preferred_gateway': 'sbi_bank'},
        {'pnr': 'PNR008', 'amount': 800.0, 'preferred_gateway': 'paytm_wallet'},
    ]
    
    print(f"\n💳 Processing {len(bookings)} train bookings...")
    print("-" * 50)
    
    successful_payments = 0
    failed_payments = 0
    
    for booking in bookings:
        try:
            result = irctc_gateway.process_payment(
                pnr=booking['pnr'],
                amount=booking['amount'],
                preferred_gateway=booking['preferred_gateway']
            )
            
            successful_payments += 1
            gateway_name = result['gateway']
            print(f"   {booking['pnr']}: ✅ ₹{booking['amount']:>6.0f} via {gateway_name}")
            
        except Exception as e:
            failed_payments += 1
            print(f"   {booking['pnr']}: ❌ ₹{booking['amount']:>6.0f} - {e}")
        
        # Add delay between payments
        time.sleep(0.5)
    
    print(f"\n📈 Payment Processing Summary:")
    print(f"   Successful: {successful_payments}/{len(bookings)}")
    print(f"   Failed: {failed_payments}/{len(bookings)}")
    print(f"   Success Rate: {successful_payments/len(bookings)*100:.1f}%")
    
    # Show gateway health
    print(f"\n🏥 Gateway Health Report:")
    print("-" * 30)
    
    health = irctc_gateway.get_gateway_health()
    print(f"   Overall Status: {health['overall_status'].upper()}")
    
    for gateway_id, gateway_health in health['gateways'].items():
        status_emoji = {
            'healthy': '✅',
            'recovering': '🔄',
            'down': '🚫'
        }
        
        emoji = status_emoji.get(gateway_health['status'], '❓')
        print(f"   {emoji} {gateway_health['name']:<20}: {gateway_health['circuit_state'].upper():<10} "
              f"({gateway_health['success_rate']:.1f}% success)")
    
    return irctc_gateway

def demonstrate_high_load_circuit_breaker():
    """Demonstrate circuit breaker under high load"""
    print("\n⚡ High Load Circuit Breaker Demo - Tatkal Booking Rush")
    print("=" * 65)
    
    irctc_gateway = IRCTCPaymentGateway()
    
    def simulate_booking_user(user_id: int) -> Dict:
        """Simulate individual user booking"""
        pnr = f"TATKAL_{user_id:04d}"
        amount = random.uniform(500, 3000)
        
        try:
            result = irctc_gateway.process_payment(pnr, amount)
            return {'success': True, 'amount': amount, 'gateway': result['gateway']}
        except Exception as e:
            return {'success': False, 'amount': amount, 'error': str(e)}
    
    print(f"🎯 Simulating Tatkal booking rush (100 concurrent users)...")
    
    # Run concurrent bookings
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(simulate_booking_user, i) for i in range(100)]
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if len(results) % 20 == 0:
                print(f"   Progress: {len(results)}/100 bookings processed")
    
    end_time = time.time()
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 High Load Test Results:")
    print("-" * 30)
    print(f"   Total Bookings: 100")
    print(f"   Successful: {len(successful)} ({len(successful)/100*100:.1f}%)")
    print(f"   Failed: {len(failed)} ({len(failed)/100*100:.1f}%)")
    print(f"   Total Time: {end_time - start_time:.2f}s")
    print(f"   Throughput: {100/(end_time - start_time):.1f} bookings/sec")
    
    # Gateway usage analysis
    gateway_usage = defaultdict(int)
    for result in successful:
        gateway_usage[result['gateway']] += 1
    
    print(f"\n🏦 Gateway Usage Distribution:")
    print("-" * 30)
    for gateway, count in sorted(gateway_usage.items()):
        print(f"   {gateway:<25}: {count:>3} bookings ({count/len(successful)*100:.1f}%)")
    
    # Final health check
    final_health = irctc_gateway.get_gateway_health()
    print(f"\n🚑 Final Gateway Health:")
    print("-" * 25)
    for gateway_id, health in final_health['gateways'].items():
        print(f"   {health['name']:<20}: {health['circuit_state'].upper():<10} "
              f"({health['total_calls']} calls)")
    
    # Reset circuit breakers for cleanup
    irctc_gateway.reset_all_circuit_breakers()

def demonstrate_circuit_breaker_recovery():
    """Demonstrate circuit breaker recovery process"""
    print("\n🔄 Circuit Breaker Recovery Demo - Service Recovery Simulation")
    print("=" * 70)
    
    # Create circuit breaker with short recovery time for demo
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=5.0,  # Short recovery time
        success_threshold=2,
        timeout_duration=1.0
    )
    
    circuit_breaker = CircuitBreaker("recovery_demo", config)
    
    def unreliable_service(phase: str = "failing") -> str:
        """Service that fails initially then recovers"""
        if phase == "failing":
            time.sleep(0.2)
            raise Exception("Service is down for maintenance")
        elif phase == "recovering": 
            time.sleep(0.3)
            if random.random() < 0.6:  # 60% success during recovery
                return "Service recovering successfully"
            else:
                raise Exception("Service still unstable")
        else:  # healthy
            time.sleep(0.1)
            return "Service is fully operational"
    
    print(f"🔧 Phase 1: Service Failing (triggering circuit breaker)")
    print("-" * 55)
    
    # Phase 1: Service failing
    for i in range(8):
        try:
            result = circuit_breaker.call(unreliable_service, "failing")
            print(f"   Call {i+1}: ✅ {result}")
        except CircuitBreakerOpenException:
            print(f"   Call {i+1}: 🚫 Circuit breaker is OPEN - calls blocked")
        except Exception as e:
            print(f"   Call {i+1}: ❌ Service error: {e}")
        
        time.sleep(0.5)
    
    print(f"\n🔧 Phase 2: Waiting for Recovery Period ({config.recovery_timeout}s)")
    print("-" * 60)
    print(f"   ⏳ Circuit breaker in OPEN state, waiting for recovery timeout...")
    time.sleep(config.recovery_timeout + 1)
    
    print(f"\n🔧 Phase 3: Service Recovery (HALF-OPEN state testing)")
    print("-" * 55)
    
    # Phase 3: Service recovering
    for i in range(6):
        try:
            result = circuit_breaker.call(unreliable_service, "recovering")
            print(f"   Call {i+1}: ✅ {result}")
        except CircuitBreakerOpenException:
            print(f"   Call {i+1}: 🚫 Circuit breaker is OPEN")
        except Exception as e:
            print(f"   Call {i+1}: ❌ Service error: {e}")
        
        time.sleep(0.8)
    
    print(f"\n🔧 Phase 4: Service Fully Recovered (CLOSED state)")
    print("-" * 50)
    
    # Phase 4: Service healthy
    for i in range(5):
        try:
            result = circuit_breaker.call(unreliable_service, "healthy")
            print(f"   Call {i+1}: ✅ {result}")
        except Exception as e:
            print(f"   Call {i+1}: ❌ Unexpected error: {e}")
        
        time.sleep(0.3)
    
    # Final statistics
    final_stats = circuit_breaker.get_stats()
    print(f"\n📈 Final Recovery Statistics:")
    print("-" * 30)
    print(f"   Final State: {final_stats['state'].upper()}")
    print(f"   Total Calls: {final_stats['total_calls']}")
    print(f"   Success Rate: {100 - final_stats['failure_rate']:.1f}%")
    print(f"   Recovery Cycles: {final_stats['circuit_open_count']}")

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_circuit_breaker_basic()
    
    print("\n" + "="*80 + "\n")
    
    irctc_payment_gateway = demonstrate_irctc_payment_gateway()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_high_load_circuit_breaker()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_circuit_breaker_recovery()
    
    print(f"\n✅ Circuit Breaker Pattern Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Circuit States - CLOSED, OPEN, HALF-OPEN transitions")
    print(f"   • Failure Detection - Threshold-based circuit opening") 
    print(f"   • Auto-Recovery - Time-based recovery attempts")
    print(f"   • Fail-Fast - Quick failure when circuit is OPEN")
    print(f"   • Fallback Mechanisms - Multiple service providers")
    print(f"   • Statistics Tracking - Failure rates and call counts")
    print(f"   • State Change Notifications - Operations team alerts")
    print(f"   • Indian Context - IRCTC, payment gateways, banking services")
    print(f"   • High Load Handling - Concurrent request protection")