#!/usr/bin/env python3
"""
Advanced Circuit Breaker with Probability Analysis
=================================================

Production-grade circuit breaker implementation with statistical analysis.
Real examples: Paytm payment protection, Zomato order processing, IRCTC booking protection

मुख्य concepts:
1. Circuit breaker states (Closed, Open, Half-Open)
2. Failure threshold probability calculations
3. Recovery time optimization using statistics
4. Indian system load patterns

Mumbai analogy: Traffic signal system that adapts to congestion
Author: Hindi Tech Podcast Series
"""

import asyncio
import time
import random
import statistics
from dataclasses import dataclass
from typing import Optional, Callable, Any, Dict, List, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import threading
from collections import deque, defaultdict
import math

# Hindi comments के साथ advanced circuit breaker implementation

class CircuitBreakerState(Enum):
    """Circuit breaker की तीन main states"""
    CLOSED = "CLOSED"        # Normal operation - सब ठीक है
    OPEN = "OPEN"           # Failing fast - तुरंत fail कर रहे हैं
    HALF_OPEN = "HALF_OPEN" # Testing recovery - recovery test कर रहे हैं

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5              # कितनी failures के बाद open करें
    recovery_timeout: int = 60              # कितनी seconds बाद recovery try करें
    success_threshold: int = 3              # Half-open से closed जाने के लिए कितनी successes
    timeout_duration: float = 30.0         # Request timeout in seconds
    sliding_window_size: int = 100          # Rolling window size for statistics
    statistical_analysis: bool = True       # Enable advanced probability analysis

@dataclass
class RequestMetrics:
    """Individual request metrics"""
    timestamp: datetime
    duration: float          # Request duration in milliseconds
    success: bool           # Request success/failure
    error_type: Optional[str] # Error type if failed
    component: str          # Which component (payment, database, etc.)

class IndianCircuitBreaker:
    """
    Advanced circuit breaker with Indian system characteristics
    Mumbai traffic जैसा adaptive behavior - traffic jam में alternate route लेते हैं
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # Circuit breaker state management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Advanced metrics tracking
        self.request_history = deque(maxlen=self.config.sliding_window_size)
        self.failure_types = defaultdict(int)
        
        # Statistical analysis components
        self.failure_probability = 0.0
        self.mean_response_time = 0.0
        self.response_time_std = 0.0
        self.reliability_score = 1.0
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Indian context - भारतीय systems के special patterns
        self.monsoon_active = self._is_monsoon_season()
        self.peak_hour_multiplier = 1.0
        self.festival_season_active = False
        
        print(f"🔧 Advanced Circuit Breaker '{self.name}' initialized")
        print(f"⚡ Failure threshold: {self.config.failure_threshold}")
        print(f"🕰️ Recovery timeout: {self.config.recovery_timeout}s")
        print(f"🌧️ Monsoon awareness: {'Active' if self.monsoon_active else 'Inactive'}")
        
    def _is_monsoon_season(self) -> bool:
        """Check if current time is monsoon season in Mumbai"""
        current_month = datetime.now().month
        return current_month in [6, 7, 8, 9]  # June to September
        
    def _get_current_load_multiplier(self) -> float:
        """
        Calculate current load multiplier based on time
        Mumbai के traffic patterns के अनुसार
        """
        current_hour = datetime.now().hour
        
        # Peak hours - office rush times
        if 9 <= current_hour <= 11 or 18 <= current_hour <= 20:
            return 1.5  # 50% higher load during peak hours
        elif 12 <= current_hour <= 14:
            return 1.2  # Lunch hour moderate increase
        elif 22 <= current_hour or current_hour <= 6:
            return 0.6  # Night time low load
        else:
            return 1.0  # Normal hours
            
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker protection
        Circuit breaker के through function call करते हैं
        """
        with self.lock:
            # Check current state
            if self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    print(f"🔄 {self.name}: Transitioning to HALF_OPEN for testing recovery")
                else:
                    # Still in open state, fail fast
                    self._record_fast_failure()
                    raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is OPEN")
                    
        # Attempt to execute the function
        start_time = time.time()
        request_start = datetime.now()
        
        try:
            # Add timeout protection
            result = await asyncio.wait_for(
                self._execute_with_timeout(func, *args, **kwargs),
                timeout=self.config.timeout_duration
            )
            
            # Calculate metrics
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Record success
            self._record_success(request_start, duration)
            
            return result
            
        except asyncio.TimeoutError:
            duration = (time.time() - start_time) * 1000
            self._record_failure(request_start, duration, "TIMEOUT")
            raise CircuitBreakerTimeoutException(f"Request timeout after {self.config.timeout_duration}s")
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_type = type(e).__name__
            self._record_failure(request_start, duration, error_type)
            raise e
            
    async def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with proper async/sync handling"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Execute sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
            
    def _record_success(self, timestamp: datetime, duration: float) -> None:
        """Record successful request"""
        with self.lock:
            # Create metrics record
            metrics = RequestMetrics(
                timestamp=timestamp,
                duration=duration,
                success=True,
                error_type=None,
                component=self.name
            )
            
            self.request_history.append(metrics)
            
            # Update state based on current state
            if self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
                
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                
                # Check if we have enough successes to close circuit
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    print(f"✅ {self.name}: Circuit breaker CLOSED after successful recovery")
                    
            self.last_success_time = timestamp
            
            # Update statistical analysis
            if self.config.statistical_analysis:
                self._update_statistics()
                
    def _record_failure(self, timestamp: datetime, duration: float, error_type: str) -> None:
        """Record failed request"""
        with self.lock:
            # Create metrics record
            metrics = RequestMetrics(
                timestamp=timestamp,
                duration=duration,
                success=False,
                error_type=error_type,
                component=self.name
            )
            
            self.request_history.append(metrics)
            self.failure_types[error_type] += 1
            
            # Update failure count
            self.failure_count += 1
            self.last_failure_time = timestamp
            
            # Apply Indian context multipliers
            adjusted_threshold = self._get_adjusted_failure_threshold()
            
            # Check state transitions
            if self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= adjusted_threshold:
                    self.state = CircuitBreakerState.OPEN
                    print(f"🚨 {self.name}: Circuit breaker OPENED after {self.failure_count} failures")
                    print(f"   Monsoon factor: {self.monsoon_active}")
                    print(f"   Peak hour factor: {self._get_current_load_multiplier()}")
                    
            elif self.state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open immediately goes back to open
                self.state = CircuitBreakerState.OPEN
                self.success_count = 0
                print(f"🔄 {self.name}: Circuit breaker back to OPEN after failure during testing")
                
            # Update statistical analysis
            if self.config.statistical_analysis:
                self._update_statistics()
                
    def _record_fast_failure(self) -> None:
        """Record fast failure when circuit is open"""
        timestamp = datetime.now()
        metrics = RequestMetrics(
            timestamp=timestamp,
            duration=0.0,  # Fast failure, no actual duration
            success=False,
            error_type="CIRCUIT_OPEN",
            component=self.name
        )
        
        self.request_history.append(metrics)
        self.failure_types["CIRCUIT_OPEN"] += 1
        
    def _get_adjusted_failure_threshold(self) -> int:
        """
        Get failure threshold adjusted for Indian conditions
        भारतीय conditions के अनुसार threshold adjust करते हैं
        """
        base_threshold = self.config.failure_threshold
        
        # Monsoon adjustment - बारिश में ज्यादा tolerance
        if self.monsoon_active:
            base_threshold = int(base_threshold * 1.5)  # 50% more tolerance
            
        # Peak hour adjustment - rush hour में ज्यादा tolerance
        load_multiplier = self._get_current_load_multiplier()
        if load_multiplier > 1.3:
            base_threshold = int(base_threshold * 1.3)  # 30% more tolerance
            
        # Festival season adjustment
        if self.festival_season_active:
            base_threshold = int(base_threshold * 1.4)  # 40% more tolerance
            
        return max(1, base_threshold)  # At least 1 failure required
        
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset from OPEN to HALF_OPEN"""
        if not self.last_failure_time:
            return False
            
        time_since_failure = datetime.now() - self.last_failure_time
        
        # Adjust recovery timeout based on Indian conditions
        adjusted_timeout = self._get_adjusted_recovery_timeout()
        
        return time_since_failure.total_seconds() >= adjusted_timeout
        
    def _get_adjusted_recovery_timeout(self) -> int:
        """
        Get recovery timeout adjusted for Indian conditions
        Indian infrastructure के हिसाब से recovery time adjust करते हैं
        """
        base_timeout = self.config.recovery_timeout
        
        # Monsoon adjustment - बारिश में ज्यादा time लगता है
        if self.monsoon_active:
            base_timeout = int(base_timeout * 1.8)  # 80% longer recovery
            
        # Peak hour adjustment - peak hours में slower recovery
        load_multiplier = self._get_current_load_multiplier()
        if load_multiplier > 1.3:
            base_timeout = int(base_timeout * 1.4)  # 40% longer recovery
            
        return base_timeout
        
    def _update_statistics(self) -> None:
        """
        Update statistical metrics for probability analysis
        Statistics update करके probability analysis करते हैं
        """
        if len(self.request_history) < 5:  # Need minimum data
            return
            
        recent_requests = list(self.request_history)
        
        # Calculate failure probability
        total_requests = len(recent_requests)
        failed_requests = sum(1 for req in recent_requests if not req.success)
        self.failure_probability = failed_requests / total_requests
        
        # Calculate response time statistics
        successful_requests = [req for req in recent_requests if req.success]
        if successful_requests:
            response_times = [req.duration for req in successful_requests]
            self.mean_response_time = statistics.mean(response_times)
            
            if len(response_times) > 1:
                self.response_time_std = statistics.stdev(response_times)
            else:
                self.response_time_std = 0.0
        
        # Calculate reliability score (0.0 to 1.0)
        # Factors: success rate, response time consistency, error diversity
        success_rate = 1.0 - self.failure_probability
        
        # Penalize high response time variance
        time_consistency = 1.0
        if self.mean_response_time > 0:
            coefficient_of_variation = self.response_time_std / self.mean_response_time
            time_consistency = max(0.0, 1.0 - coefficient_of_variation)
            
        # Penalize diverse error types (indicates systemic issues)
        error_diversity_penalty = min(0.3, len(self.failure_types) * 0.05)
        
        self.reliability_score = success_rate * time_consistency * (1.0 - error_diversity_penalty)
        
    def get_circuit_status(self) -> Dict:
        """
        Get comprehensive circuit breaker status
        Circuit breaker की complete status return करते हैं
        """
        with self.lock:
            recent_requests = list(self.request_history)
            
            # Calculate time-windowed metrics
            last_hour = datetime.now() - timedelta(hours=1)
            recent_hour_requests = [req for req in recent_requests if req.timestamp >= last_hour]
            
            status = {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
                
                # Statistical metrics
                'failure_probability': self.failure_probability,
                'mean_response_time_ms': self.mean_response_time,
                'response_time_std_ms': self.response_time_std,
                'reliability_score': self.reliability_score,
                
                # Request metrics
                'total_requests': len(recent_requests),
                'requests_last_hour': len(recent_hour_requests),
                
                # Error analysis
                'failure_types': dict(self.failure_types),
                
                # Indian context
                'monsoon_active': self.monsoon_active,
                'current_load_multiplier': self._get_current_load_multiplier(),
                'adjusted_failure_threshold': self._get_adjusted_failure_threshold(),
                'adjusted_recovery_timeout': self._get_adjusted_recovery_timeout(),
                
                # Health indicators
                'health_indicators': self._get_health_indicators()
            }
            
            return status
            
    def _get_health_indicators(self) -> Dict[str, str]:
        """
        Get system health indicators
        System की health indicators return करते हैं
        """
        indicators = {}
        
        # Overall health based on reliability score
        if self.reliability_score >= 0.95:
            indicators['overall_health'] = "EXCELLENT 🟢"
        elif self.reliability_score >= 0.85:
            indicators['overall_health'] = "GOOD 🟡"
        elif self.reliability_score >= 0.70:
            indicators['overall_health'] = "CONCERNING 🟠"
        else:
            indicators['overall_health'] = "POOR 🔴"
            
        # Response time health
        if self.mean_response_time < 100:
            indicators['response_time'] = "FAST ⚡"
        elif self.mean_response_time < 500:
            indicators['response_time'] = "NORMAL 📊"
        elif self.mean_response_time < 2000:
            indicators['response_time'] = "SLOW 🐌"
        else:
            indicators['response_time'] = "VERY_SLOW 🔴"
            
        # Error rate health
        if self.failure_probability < 0.01:
            indicators['error_rate'] = "EXCELLENT 🎯"
        elif self.failure_probability < 0.05:
            indicators['error_rate'] = "ACCEPTABLE ✅"
        elif self.failure_probability < 0.15:
            indicators['error_rate'] = "HIGH ⚠️"
        else:
            indicators['error_rate'] = "CRITICAL 🚨"
            
        return indicators
        
    def reset(self) -> None:
        """
        Manually reset circuit breaker
        Circuit breaker को manually reset करते हैं
        """
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            print(f"🔄 {self.name}: Circuit breaker manually reset to CLOSED")
            
    def generate_report(self) -> str:
        """Generate comprehensive circuit breaker report"""
        status = self.get_circuit_status()
        
        report = []
        report.append(f"🔧 CIRCUIT BREAKER REPORT: {self.name}")
        report.append("=" * 50)
        report.append(f"Current State: {status['state']}")
        report.append(f"Overall Health: {status['health_indicators']['overall_health']}")
        report.append("")
        
        # Statistics section
        report.append("📊 STATISTICAL ANALYSIS")
        report.append("-" * 30)
        report.append(f"Failure Probability: {status['failure_probability']:.4f} ({status['failure_probability']*100:.2f}%)")
        report.append(f"Reliability Score: {status['reliability_score']:.3f}")
        report.append(f"Mean Response Time: {status['mean_response_time_ms']:.1f}ms")
        report.append(f"Response Time StdDev: {status['response_time_std_ms']:.1f}ms")
        report.append("")
        
        # Performance indicators
        report.append("🏥 HEALTH INDICATORS")
        report.append("-" * 30)
        for indicator, value in status['health_indicators'].items():
            report.append(f"{indicator.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Indian context section
        report.append("🇮🇳 INDIAN CONTEXT FACTORS")
        report.append("-" * 30)
        report.append(f"Monsoon Season: {'Active 🌧️' if status['monsoon_active'] else 'Inactive ☀️'}")
        report.append(f"Current Load Multiplier: {status['current_load_multiplier']:.1f}x")
        report.append(f"Adjusted Failure Threshold: {status['adjusted_failure_threshold']}")
        report.append(f"Adjusted Recovery Timeout: {status['adjusted_recovery_timeout']}s")
        report.append("")
        
        # Error analysis
        if status['failure_types']:
            report.append("🚨 ERROR TYPE ANALYSIS")
            report.append("-" * 30)
            total_failures = sum(status['failure_types'].values())
            for error_type, count in sorted(status['failure_types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_failures) * 100
                report.append(f"{error_type}: {count} ({percentage:.1f}%)")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        
        if status['failure_probability'] > 0.1:
            report.append("🔧 High failure rate detected - investigate root cause")
            
        if status['mean_response_time_ms'] > 1000:
            report.append("⚡ Slow response times - optimize performance")
            
        if len(status['failure_types']) > 3:
            report.append("🎯 Multiple error types - systemic issues likely")
            
        if status['monsoon_active'] and status['failure_probability'] > 0.05:
            report.append("🌧️ Monsoon season - consider additional redundancy")
            
        report.append("📱 Monitor like Mumbai traffic apps - real-time updates crucial")
        report.append("🚊 Be reliable like Mumbai local trains (most of the time!)")
        
        return "\n".join(report)

# Custom exceptions
class CircuitBreakerException(Exception):
    """Base exception for circuit breaker"""
    pass

class CircuitBreakerOpenException(CircuitBreakerException):
    """Exception when circuit breaker is open"""
    pass

class CircuitBreakerTimeoutException(CircuitBreakerException):
    """Exception when request times out"""
    pass

# Demo functions for testing
async def unreliable_payment_service(amount: float, user_id: str) -> Dict:
    """
    Simulated unreliable payment service (like real Indian payment gateways!)
    कभी-कभी fail होने वाला payment service
    """
    # Simulate different failure scenarios
    failure_scenarios = {
        0.15: "NETWORK_ERROR",      # 15% network issues
        0.10: "TIMEOUT",           # 10% timeouts  
        0.08: "BANK_ERROR",        # 8% bank issues
        0.05: "INSUFFICIENT_FUNDS", # 5% insufficient funds
        0.02: "SYSTEM_ERROR"       # 2% system errors
    }
    
    # Check for failure
    random_val = random.random()
    cumulative_prob = 0.0
    
    for prob, error_type in failure_scenarios.items():
        cumulative_prob += prob
        if random_val <= cumulative_prob:
            # Simulate processing time before failure
            await asyncio.sleep(random.uniform(0.1, 2.0))
            raise Exception(f"Payment failed: {error_type}")
    
    # Success case
    processing_time = random.uniform(0.5, 1.5)  # 0.5-1.5 seconds
    await asyncio.sleep(processing_time)
    
    return {
        'transaction_id': f'TXN_{int(time.time())}_{user_id}',
        'amount': amount,
        'user_id': user_id,
        'status': 'SUCCESS',
        'processing_time': processing_time
    }

async def demo_circuit_breaker():
    """
    Comprehensive circuit breaker demonstration
    Complete demo with Indian payment scenarios
    """
    print("🔧 Advanced Circuit Breaker Demo - Indian Payment System")
    print("=" * 60)
    
    # Create circuit breaker for payment service
    config = CircuitBreakerConfig(
        failure_threshold=3,        # Lower threshold for demo
        recovery_timeout=10,        # Quick recovery for demo
        success_threshold=2,        # Quick close for demo
        timeout_duration=3.0,       # 3 second timeout
        sliding_window_size=50,     # Smaller window for demo
        statistical_analysis=True
    )
    
    payment_breaker = IndianCircuitBreaker("PaymentService", config)
    
    print(f"🚀 Testing payment service with circuit breaker protection...")
    print(f"💰 Simulating PhonePe/Paytm-like payment failures\n")
    
    successful_payments = 0
    failed_payments = 0
    
    # Simulate 30 payment attempts
    for i in range(30):
        user_id = f"USER_{i:03d}"
        amount = random.uniform(100, 5000)  # ₹100 to ₹5000
        
        try:
            # Attempt payment through circuit breaker
            result = await payment_breaker.call(
                unreliable_payment_service,
                amount,
                user_id
            )
            
            successful_payments += 1
            print(f"✅ Payment {i+1:2d}: ₹{amount:7.2f} for {user_id} - SUCCESS")
            
        except CircuitBreakerOpenException as e:
            failed_payments += 1
            print(f"⚡ Payment {i+1:2d}: ₹{amount:7.2f} for {user_id} - CIRCUIT_OPEN")
            
        except CircuitBreakerTimeoutException as e:
            failed_payments += 1
            print(f"⏰ Payment {i+1:2d}: ₹{amount:7.2f} for {user_id} - TIMEOUT")
            
        except Exception as e:
            failed_payments += 1
            print(f"❌ Payment {i+1:2d}: ₹{amount:7.2f} for {user_id} - {str(e)[:30]}...")
            
        # Small delay between requests
        await asyncio.sleep(0.1)
        
        # Show status every 10 requests
        if (i + 1) % 10 == 0:
            status = payment_breaker.get_circuit_status()
            print(f"\n📊 Status after {i+1} requests:")
            print(f"   State: {status['state']}")
            print(f"   Success Rate: {((i+1-failed_payments)/(i+1))*100:.1f}%")
            print(f"   Failure Probability: {status['failure_probability']:.3f}")
            print(f"   Mean Response Time: {status['mean_response_time_ms']:.1f}ms\n")
    
    # Final report
    print("\n" + "="*60)
    print(f"🎯 FINAL RESULTS")
    print(f"Total Payments Attempted: {successful_payments + failed_payments}")
    print(f"Successful Payments: {successful_payments}")
    print(f"Failed Payments: {failed_payments}")
    print(f"Success Rate: {(successful_payments/(successful_payments + failed_payments))*100:.1f}%")
    
    # Generate comprehensive report
    report = payment_breaker.generate_report()
    print("\n" + report)
    
    print("\n🎉 Circuit breaker demo completed!")
    print("🏙️ Just like Mumbai traffic signals - adapts to congestion!")
    print("💡 Circuit breakers prevent cascade failures in production systems!")

async def main():
    """Main demonstration function"""
    await demo_circuit_breaker()

if __name__ == "__main__":
    asyncio.run(main())