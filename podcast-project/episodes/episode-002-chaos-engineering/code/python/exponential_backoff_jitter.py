#!/usr/bin/env python3
"""
Exponential Backoff with Jitter - Episode 2
जिटर के साथ एक्सपोनेंशियल बैकऑफ

Production-ready exponential backoff implementation to prevent thundering herd
Thundering herd को रोकने के लिए production-ready exponential backoff

जैसे IRCTC Tatkal booking में हज़ारों लोग एक साथ try करते हैं - 
अगर सभी एक साथ retry करें तो server crash हो जाता है!
इसलिए smart retry strategy चाहिए।

Author: Code Developer Agent A5-C-002
Indian Context: IRCTC retry patterns, Zomato order failures, Flipkart flash sales
"""

import random
import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import math
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s | समय: %(asctime)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backoff_retry.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class BackoffStrategy(Enum):
    """Backoff strategies - बैकऑफ रणनीतियां"""
    EXPONENTIAL = "exponential"           # एक्सपोनेंशियल - 1s, 2s, 4s, 8s...
    LINEAR = "linear"                     # रैखिक - 1s, 2s, 3s, 4s...
    FIXED = "fixed"                       # स्थिर - 1s, 1s, 1s, 1s...
    EXPONENTIAL_JITTER = "exponential_jitter"  # एक्सपोनेंशियल + jitter
    DECORRELATED_JITTER = "decorrelated_jitter"  # Decorrelated jitter
    MUMBAI_MONSOON = "mumbai_monsoon"     # मुंबई मानसून - unpredictable delays

class JitterType(Enum):
    """Types of jitter - जिटर के प्रकार"""
    NONE = "none"                 # बिना jitter
    FULL = "full"                 # पूर्ण jitter - 0 to calculated delay
    EQUAL = "equal"               # समान jitter - base + (0 to base)
    DECORRELATED = "decorrelated" # Decorrelated jitter - more sophisticated

@dataclass
class RetryConfig:
    """Configuration for retry mechanism - retry mechanism के लिए कॉन्फ़िगरेशन"""
    
    # Basic retry settings
    max_attempts: int = 5                      # अधिकतम प्रयास
    base_delay_seconds: float = 1.0            # आधार विलंब
    max_delay_seconds: float = 300.0           # अधिकतम विलंब (5 minutes)
    backoff_multiplier: float = 2.0            # बैकऑफ गुणक
    
    # Jitter settings
    jitter_type: JitterType = JitterType.FULL
    jitter_max: float = 1.0                    # Maximum jitter factor
    
    # Strategy
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    
    # Exception handling
    retryable_exceptions: tuple = (ConnectionError, TimeoutError, requests.exceptions.RequestException)
    
    # Indian context settings
    consider_peak_hours: bool = True           # Peak hours में अलग behavior
    festival_season_multiplier: float = 1.5   # त्योहारी सीज़न में अधिक delay
    regional_adjustment: bool = True           # Regional network conditions
    
    # Success criteria
    success_threshold: float = 0.8             # 80% success rate to consider healthy
    circuit_breaker_threshold: int = 10        # After 10 consecutive failures, stop

@dataclass
class RetryAttempt:
    """Information about a retry attempt - retry प्रयास की जानकारी"""
    attempt_number: int
    delay_before_attempt: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    jitter_applied: float = 0.0

@dataclass
class RetryStats:
    """Statistics for retry operations - retry operations के आंकड़े"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_attempts: int = 0
    total_delay_seconds: float = 0.0
    average_attempts_per_operation: float = 0.0
    success_rate: float = 0.0
    
    # Indian context stats
    peak_hour_operations: int = 0
    festival_season_operations: int = 0
    regional_stats: Dict[str, int] = None
    
    def __post_init__(self):
        if self.regional_stats is None:
            self.regional_stats = {}

class ThunderingHerdDetector:
    """Detects and prevents thundering herd scenarios - Thundering herd scenarios का पता लगाता है"""
    
    def __init__(self, time_window_seconds: int = 60):
        self.time_window = time_window_seconds
        self.request_timestamps = []
        self.lock = threading.Lock()
        
        # Thundering herd thresholds
        self.normal_rate = 100      # Normal requests per minute
        self.warning_rate = 500     # Warning threshold
        self.critical_rate = 1000   # Critical threshold - likely thundering herd
        
    def record_request(self) -> str:
        """Record a request and check for thundering herd - Request record करें और thundering herd check करें"""
        
        current_time = time.time()
        
        with self.lock:
            # Add current request
            self.request_timestamps.append(current_time)
            
            # Remove old requests outside time window
            cutoff_time = current_time - self.time_window
            self.request_timestamps = [t for t in self.request_timestamps if t > cutoff_time]
            
            # Calculate current rate
            current_rate = len(self.request_timestamps)
            
            if current_rate >= self.critical_rate:
                logger.warning(f"🚨 THUNDERING HERD DETECTED: {current_rate} requests/min | " +
                              f"Thundering herd का पता चला: {current_rate} requests/min")
                return "critical"
            elif current_rate >= self.warning_rate:
                logger.warning(f"⚠️  High request rate: {current_rate} requests/min | " +
                              f"उच्च request rate: {current_rate} requests/min")
                return "warning"
            elif current_rate >= self.normal_rate:
                return "elevated"
            else:
                return "normal"

class IRCTCStyleRetryHandler:
    """IRCTC-style retry handler with smart backoff - स्मार्ट बैकऑफ के साथ IRCTC-style retry handler"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.stats = RetryStats()
        self.thundering_herd_detector = ThunderingHerdDetector()
        self.circuit_breaker_state = "closed"  # closed, open, half-open
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.operation_history: List[RetryAttempt] = []
        
        # Indian context data
        self.peak_hours = [(8, 11), (18, 21)]  # Morning and evening peak
        self.festival_months = [3, 4, 10, 11]  # Festival seasons (Mar, Apr, Oct, Nov)
        self.regional_latency = {
            'mumbai': 1.0,     # Base latency
            'delhi': 1.2,      # 20% higher latency
            'bangalore': 1.1,  # 10% higher latency
            'kolkata': 1.5,    # 50% higher latency
            'chennai': 1.3,    # 30% higher latency
            'tier2': 2.0       # Tier 2 cities have double latency
        }
        
        logger.info(f"🔄 Retry handler initialized | Retry handler शुरू")
        logger.info(f"   Strategy: {config.strategy.value} | रणनीति: {config.strategy.value}")
        logger.info(f"   Max attempts: {config.max_attempts} | अधिकतम प्रयास: {config.max_attempts}")
        logger.info(f"   Jitter type: {config.jitter_type.value} | Jitter प्रकार: {config.jitter_type.value}")
    
    def calculate_delay(self, attempt_number: int, previous_delay: float = 0) -> float:
        """Calculate delay for next attempt - अगले प्रयास के लिए विलंब की गणना"""
        
        if self.config.strategy == BackoffStrategy.FIXED:
            base_delay = self.config.base_delay_seconds
        elif self.config.strategy == BackoffStrategy.LINEAR:
            base_delay = self.config.base_delay_seconds * attempt_number
        elif self.config.strategy in [BackoffStrategy.EXPONENTIAL, BackoffStrategy.EXPONENTIAL_JITTER]:
            base_delay = self.config.base_delay_seconds * (self.config.backoff_multiplier ** (attempt_number - 1))
        elif self.config.strategy == BackoffStrategy.DECORRELATED_JITTER:
            # Decorrelated jitter: random between base_delay and previous_delay * 3
            base_delay = random.uniform(self.config.base_delay_seconds, previous_delay * 3)
        elif self.config.strategy == BackoffStrategy.MUMBAI_MONSOON:
            # Unpredictable like Mumbai monsoon
            base_delay = self._mumbai_monsoon_delay(attempt_number)
        else:
            base_delay = self.config.base_delay_seconds
        
        # Apply Indian context adjustments
        base_delay = self._apply_indian_context_adjustments(base_delay)
        
        # Apply jitter
        jittered_delay, jitter_applied = self._apply_jitter(base_delay)
        
        # Ensure within bounds
        final_delay = min(jittered_delay, self.config.max_delay_seconds)
        
        logger.debug(f"Delay calculation: base={base_delay:.2f}s, jittered={jittered_delay:.2f}s, final={final_delay:.2f}s")
        
        return final_delay
    
    def _mumbai_monsoon_delay(self, attempt_number: int) -> float:
        """Calculate delay using Mumbai monsoon pattern - मुंबई मानसून पैटर्न का उपयोग करके विलंब"""
        
        # Mumbai monsoon is unpredictable - sometimes light, sometimes heavy
        current_month = datetime.now().month
        
        if current_month in [6, 7, 8, 9]:  # Monsoon months
            # Heavy monsoon - longer delays
            intensity = random.choice(['light', 'moderate', 'heavy', 'very_heavy'])
            
            if intensity == 'light':
                multiplier = 1.5
            elif intensity == 'moderate':
                multiplier = 3.0
            elif intensity == 'heavy':
                multiplier = 6.0
            else:  # very_heavy
                multiplier = 12.0
                
            base_delay = self.config.base_delay_seconds * multiplier
            logger.info(f"🌧️ Mumbai monsoon delay: {intensity} rain, multiplier={multiplier}")
            
        else:
            # Normal weather
            base_delay = self.config.base_delay_seconds * (1.5 ** attempt_number)
        
        return base_delay
    
    def _apply_indian_context_adjustments(self, base_delay: float) -> float:
        """Apply Indian context adjustments - भारतीय संदर्भ adjustments लागू करें"""
        
        adjusted_delay = base_delay
        
        # Peak hours adjustment
        if self.config.consider_peak_hours:
            current_hour = datetime.now().hour
            for start_hour, end_hour in self.peak_hours:
                if start_hour <= current_hour <= end_hour:
                    adjusted_delay *= 1.5  # 50% longer delays during peak hours
                    logger.debug(f"Peak hour adjustment applied: {adjusted_delay:.2f}s")
                    self.stats.peak_hour_operations += 1
                    break
        
        # Festival season adjustment
        current_month = datetime.now().month
        if current_month in self.festival_months:
            adjusted_delay *= self.config.festival_season_multiplier
            logger.debug(f"Festival season adjustment: {adjusted_delay:.2f}s")
            self.stats.festival_season_operations += 1
        
        # Regional adjustment (simulated based on user location)
        # In real implementation, this would be based on actual user location
        simulated_region = random.choice(['mumbai', 'delhi', 'bangalore', 'kolkata', 'tier2'])
        if self.config.regional_adjustment:
            region_multiplier = self.regional_latency.get(simulated_region, 1.0)
            adjusted_delay *= region_multiplier
            
            self.stats.regional_stats[simulated_region] = self.stats.regional_stats.get(simulated_region, 0) + 1
            
            if region_multiplier > 1.5:
                logger.debug(f"High latency region {simulated_region}: {adjusted_delay:.2f}s")
        
        return adjusted_delay
    
    def _apply_jitter(self, base_delay: float) -> tuple[float, float]:
        """Apply jitter to delay - विलंब पर jitter लागू करें"""
        
        if self.config.jitter_type == JitterType.NONE:
            return base_delay, 0.0
        
        elif self.config.jitter_type == JitterType.FULL:
            # Full jitter: random between 0 and base_delay
            jitter = random.uniform(0, base_delay)
            return jitter, base_delay - jitter
        
        elif self.config.jitter_type == JitterType.EQUAL:
            # Equal jitter: base_delay + random(0, base_delay)
            jitter = random.uniform(0, base_delay)
            return base_delay + jitter, jitter
        
        elif self.config.jitter_type == JitterType.DECORRELATED:
            # Decorrelated jitter: more sophisticated randomization
            jitter = random.uniform(0, base_delay * self.config.jitter_max)
            return base_delay + jitter, jitter
        
        return base_delay, 0.0
    
    def should_retry(self, attempt_number: int, exception: Exception) -> bool:
        """Determine if operation should be retried - क्या operation को retry करना चाहिए"""
        
        # Check attempt limit
        if attempt_number >= self.config.max_attempts:
            logger.info(f"Max attempts ({self.config.max_attempts}) reached | अधिकतम प्रयास पूर्ण")
            return False
        
        # Check circuit breaker
        if self.circuit_breaker_state == "open":
            logger.warning("Circuit breaker open - not retrying | Circuit breaker खुला है")
            return False
        
        # Check if exception is retryable
        if not isinstance(exception, self.config.retryable_exceptions):
            logger.info(f"Non-retryable exception: {type(exception).__name__} | Non-retryable exception: {type(exception).__name__}")
            return False
        
        # Check thundering herd condition
        herd_status = self.thundering_herd_detector.record_request()
        if herd_status == "critical":
            # During thundering herd, reduce retry probability
            if random.random() < 0.7:  # 70% chance to skip retry
                logger.warning("Skipping retry due to thundering herd | Thundering herd के कारण retry skip")
                return False
        
        return True
    
    def update_circuit_breaker(self, success: bool):
        """Update circuit breaker state - Circuit breaker स्थिति अपडेट करें"""
        
        if success:
            if self.circuit_breaker_state == "half-open":
                self.circuit_breaker_state = "closed"
                logger.info("Circuit breaker closed - service recovered | Service ठीक हो गई")
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.last_failure_time = datetime.now()
            
            if self.consecutive_failures >= self.config.circuit_breaker_threshold:
                if self.circuit_breaker_state == "closed":
                    self.circuit_breaker_state = "open"
                    logger.warning(f"Circuit breaker opened after {self.consecutive_failures} failures | " +
                                  f"{self.consecutive_failures} failures के बाद circuit breaker खुला")
        
        # Check if circuit breaker should move to half-open
        if (self.circuit_breaker_state == "open" and 
            self.last_failure_time and 
            datetime.now() - self.last_failure_time > timedelta(minutes=5)):
            self.circuit_breaker_state = "half-open"
            logger.info("Circuit breaker half-open - testing service | Service test कर रहे हैं")
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry and backoff - Retry और backoff के साथ function execute करें"""
        
        operation_start = time.time()
        attempts = []
        last_exception = None
        previous_delay = 0.0
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.info(f"🔄 Attempt {attempt}/{self.config.max_attempts} | प्रयास {attempt}/{self.config.max_attempts}")
                
                # Record attempt start
                attempt_start = time.time()
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Record successful attempt
                attempt_duration = time.time() - attempt_start
                attempt_info = RetryAttempt(
                    attempt_number=attempt,
                    delay_before_attempt=previous_delay,
                    timestamp=datetime.now(),
                    success=True,
                    response_time=attempt_duration
                )
                attempts.append(attempt_info)
                
                # Update stats and circuit breaker
                self.stats.successful_operations += 1
                self.update_circuit_breaker(True)
                
                logger.info(f"✅ Operation succeeded on attempt {attempt} | प्रयास {attempt} में सफल")
                return result
                
            except Exception as e:
                last_exception = e
                attempt_duration = time.time() - attempt_start
                
                # Record failed attempt
                attempt_info = RetryAttempt(
                    attempt_number=attempt,
                    delay_before_attempt=previous_delay,
                    timestamp=datetime.now(),
                    success=False,
                    error_message=str(e),
                    response_time=attempt_duration
                )
                attempts.append(attempt_info)
                
                logger.warning(f"❌ Attempt {attempt} failed: {str(e)[:100]} | प्रयास {attempt} असफल: {str(e)[:100]}")
                
                # Check if should retry
                if not self.should_retry(attempt, e):
                    break
                
                # Calculate delay for next attempt
                delay = self.calculate_delay(attempt + 1, previous_delay)
                previous_delay = delay
                
                logger.info(f"⏳ Waiting {delay:.2f}s before next attempt | अगले प्रयास से पहले {delay:.2f}s प्रतीक्षा")
                time.sleep(delay)
                
                self.stats.total_delay_seconds += delay
        
        # Operation failed after all attempts
        self.stats.failed_operations += 1
        self.stats.total_attempts += len(attempts)
        self.operation_history.extend(attempts)
        
        # Update circuit breaker
        self.update_circuit_breaker(False)
        
        operation_duration = time.time() - operation_start
        logger.error(f"❌ Operation failed after {len(attempts)} attempts in {operation_duration:.2f}s | " +
                    f"{len(attempts)} प्रयासों के बाद {operation_duration:.2f}s में असफल")
        
        raise last_exception
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics - व्यापक आंकड़े प्राप्त करें"""
        
        total_ops = self.stats.total_operations = (self.stats.successful_operations + 
                                                   self.stats.failed_operations)
        
        if total_ops > 0:
            self.stats.success_rate = self.stats.successful_operations / total_ops
            self.stats.average_attempts_per_operation = self.stats.total_attempts / total_ops
        
        return {
            'total_operations': total_ops,
            'successful_operations': self.stats.successful_operations,
            'failed_operations': self.stats.failed_operations,
            'success_rate_percentage': self.stats.success_rate * 100,
            'total_attempts': self.stats.total_attempts,
            'average_attempts_per_operation': self.stats.average_attempts_per_operation,
            'total_delay_seconds': self.stats.total_delay_seconds,
            'circuit_breaker_state': self.circuit_breaker_state,
            'consecutive_failures': self.consecutive_failures,
            
            # Indian context stats
            'peak_hour_operations': self.stats.peak_hour_operations,
            'festival_season_operations': self.stats.festival_season_operations,
            'regional_distribution': dict(self.stats.regional_stats),
            
            # Recent attempts
            'recent_attempts': [asdict(attempt) for attempt in self.operation_history[-10:]]
        }

# Decorator for automatic retry
def retry_with_exponential_backoff(config: RetryConfig = None):
    """Decorator for automatic retry with exponential backoff - स्वचालित retry के लिए decorator"""
    
    if config is None:
        config = RetryConfig()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = IRCTCStyleRetryHandler(config)
            return retry_handler.retry_with_backoff(func, *args, **kwargs)
        return wrapper
    return decorator

# Sample functions to demonstrate retry behavior
class IRCTCBookingSimulator:
    """Simulates IRCTC booking with various failure scenarios - विभिन्न failure scenarios के साथ IRCTC booking simulate करता है"""
    
    def __init__(self):
        self.server_load = 0.5  # 0.0 to 1.0
        self.network_stability = 0.8  # 0.0 to 1.0
        self.booking_success_rate = 0.6  # Base success rate
    
    def book_tatkal_ticket(self, from_station: str, to_station: str, 
                          passenger_count: int = 1, user_type: str = "regular") -> Dict[str, Any]:
        """Simulate tatkal ticket booking - Tatkal ticket booking simulate करें"""
        
        # Simulate various failure scenarios
        failure_scenarios = [
            (0.3, "Server overloaded - high traffic"),
            (0.2, "Network timeout - poor connectivity"), 
            (0.15, "Database connection failed"),
            (0.1, "Payment gateway error"),
            (0.05, "Seat not available"),
            (0.1, "Session expired"),
            (0.1, "Invalid captcha")
        ]
        
        # Adjust success rate based on conditions
        adjusted_success_rate = self.booking_success_rate
        
        # Peak hour adjustment (Tatkal booking time: 10 AM)
        current_hour = datetime.now().hour
        if current_hour == 10:  # Tatkal booking hour
            adjusted_success_rate *= 0.3  # Much lower success rate
        elif 9 <= current_hour <= 11:
            adjusted_success_rate *= 0.7
        
        # User type adjustment
        if user_type == "premium":
            adjusted_success_rate *= 1.2
        elif user_type == "bulk":
            adjusted_success_rate *= 0.8
        
        # Network stability impact
        adjusted_success_rate *= self.network_stability
        
        # Server load impact
        adjusted_success_rate *= (1.0 - self.server_load * 0.5)
        
        # Simulate response time
        response_time = random.uniform(2, 8)  # 2-8 seconds
        time.sleep(response_time / 1000)  # Simulate brief delay
        
        # Determine if operation succeeds
        if random.random() < adjusted_success_rate:
            # Success
            pnr = f"PNR{random.randint(1000000, 9999999)}"
            return {
                'status': 'SUCCESS',
                'pnr': pnr,
                'from_station': from_station,
                'to_station': to_station,
                'passenger_count': passenger_count,
                'booking_time': datetime.now().isoformat(),
                'response_time_ms': response_time
            }
        else:
            # Failure - choose random failure scenario
            failure_prob = random.random()
            cumulative_prob = 0
            selected_error = "Unknown error"
            
            for prob, error_msg in failure_scenarios:
                cumulative_prob += prob
                if failure_prob <= cumulative_prob:
                    selected_error = error_msg
                    break
            
            # Simulate different exception types
            if "network" in selected_error.lower() or "timeout" in selected_error.lower():
                raise requests.exceptions.Timeout(selected_error)
            elif "connection" in selected_error.lower():
                raise ConnectionError(selected_error)
            elif "server" in selected_error.lower():
                raise requests.exceptions.HTTPError(f"503 Service Unavailable: {selected_error}")
            else:
                raise Exception(selected_error)

def main():
    """Main function to demonstrate exponential backoff with jitter - मुख्य function"""
    
    print("🔄 Exponential Backoff with Jitter Demo - Episode 2")
    print("जिटर के साथ एक्सपोनेंशियल बैकऑफ डेमो - एपिसोड 2\n")
    
    # Create IRCTC booking simulator
    booking_simulator = IRCTCBookingSimulator()
    
    # Test different backoff strategies
    strategies_to_test = [
        ("Conservative Strategy", RetryConfig(
            strategy=BackoffStrategy.EXPONENTIAL_JITTER,
            jitter_type=JitterType.FULL,
            max_attempts=3,
            base_delay_seconds=1.0,
            backoff_multiplier=2.0
        )),
        ("Aggressive Strategy", RetryConfig(
            strategy=BackoffStrategy.EXPONENTIAL_JITTER,
            jitter_type=JitterType.EQUAL,
            max_attempts=7,
            base_delay_seconds=0.5,
            backoff_multiplier=1.5
        )),
        ("Mumbai Monsoon Strategy", RetryConfig(
            strategy=BackoffStrategy.MUMBAI_MONSOON,
            jitter_type=JitterType.DECORRELATED,
            max_attempts=5,
            base_delay_seconds=2.0
        )),
        ("Anti-Thundering Herd", RetryConfig(
            strategy=BackoffStrategy.DECORRELATED_JITTER,
            jitter_type=JitterType.DECORRELATED,
            max_attempts=4,
            base_delay_seconds=1.0,
            circuit_breaker_threshold=5
        ))
    ]
    
    print("Testing different backoff strategies:")
    for i, (name, _) in enumerate(strategies_to_test, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "="*80)
    
    # Test each strategy
    for strategy_name, config in strategies_to_test:
        print(f"\n🧪 TESTING: {strategy_name}")
        print(f"परीक्षण: {strategy_name}")
        print("-" * 50)
        
        retry_handler = IRCTCStyleRetryHandler(config)
        
        # Test scenarios
        test_scenarios = [
            ("Mumbai to Delhi Rajdhani", "Mumbai Central", "New Delhi Railway Station", 1, "premium"),
            ("Bangalore to Chennai Express", "Bangalore City", "Chennai Central", 2, "regular"),
            ("Kolkata to Howrah Local", "Sealdah", "Howrah", 1, "regular"),
            ("Delhi to Agra Shatabdi", "New Delhi", "Agra Cantt", 4, "regular"),
            ("Tatkal Emergency Booking", "Andheri", "Borivali", 1, "premium")
        ]
        
        successful_bookings = 0
        failed_bookings = 0
        
        for i, (booking_name, from_station, to_station, passengers, user_type) in enumerate(test_scenarios, 1):
            print(f"\n📋 Scenario {i}: {booking_name}")
            print(f"   Route: {from_station} → {to_station} ({passengers} passengers)")
            print(f"   User Type: {user_type}")
            
            try:
                result = retry_handler.retry_with_backoff(
                    booking_simulator.book_tatkal_ticket,
                    from_station=from_station,
                    to_station=to_station,
                    passenger_count=passengers,
                    user_type=user_type
                )
                
                print(f"   ✅ SUCCESS: PNR {result['pnr']}")
                print(f"      Booking time: {result['booking_time']}")
                successful_bookings += 1
                
            except Exception as e:
                print(f"   ❌ FAILED: {str(e)[:80]}...")
                failed_bookings += 1
            
            # Small delay between scenarios
            time.sleep(0.5)
        
        # Print strategy summary
        print(f"\n📊 STRATEGY SUMMARY: {strategy_name}")
        stats = retry_handler.get_stats_summary()
        
        print(f"   Successful Operations: {stats['successful_operations']}")
        print(f"   Failed Operations: {stats['failed_operations']}")
        print(f"   Success Rate: {stats['success_rate_percentage']:.1f}%")
        print(f"   Average Attempts: {stats['average_attempts_per_operation']:.1f}")
        print(f"   Total Delay: {stats['total_delay_seconds']:.1f}s")
        print(f"   Circuit Breaker: {stats['circuit_breaker_state']}")
        
        if stats['regional_distribution']:
            print(f"   Regional Distribution:")
            for region, count in stats['regional_distribution'].items():
                print(f"     {region}: {count} operations")
    
    print(f"\n{'='*80}")
    print("DECORATOR EXAMPLE | DECORATOR उदाहरण")  
    print('='*80)
    
    # Demonstrate decorator usage
    @retry_with_exponential_backoff(RetryConfig(
        strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        max_attempts=4,
        base_delay_seconds=1.0,
        jitter_type=JitterType.FULL
    ))
    def book_ticket_with_decorator(route: str, passenger_type: str) -> str:
        """Function with automatic retry using decorator - Decorator के साथ स्वचालित retry वाला function"""
        
        # Simulate booking operation
        success_rate = 0.4  # 40% success rate to show retries
        
        if random.random() < success_rate:
            pnr = f"PNR{random.randint(1000000, 9999999)}"
            return f"Ticket booked successfully! PNR: {pnr} for {route} ({passenger_type})"
        else:
            error_messages = [
                "Server temporarily unavailable",
                "Network connectivity issue", 
                "Database timeout",
                "High traffic - please retry"
            ]
            raise requests.exceptions.RequestException(random.choice(error_messages))
    
    print("\nTesting decorator-based retry:")
    
    decorator_scenarios = [
        ("Mumbai-Pune Deccan Queen", "Adult"),
        ("Delhi-Jaipur Shatabdi", "Senior Citizen"),
        ("Howrah-Puri Jagannath Express", "Child")
    ]
    
    for route, passenger_type in decorator_scenarios:
        try:
            print(f"\n🎫 Booking: {route} ({passenger_type})")
            result = book_ticket_with_decorator(route, passenger_type)
            print(f"   ✅ {result}")
        except Exception as e:
            print(f"   ❌ Booking failed: {str(e)}")
    
    # Performance comparison
    print(f"\n{'='*80}")
    print("PERFORMANCE COMPARISON | प्रदर्शन तुलना")
    print('='*80)
    
    comparison_configs = [
        ("No Jitter", RetryConfig(strategy=BackoffStrategy.EXPONENTIAL, jitter_type=JitterType.NONE)),
        ("Full Jitter", RetryConfig(strategy=BackoffStrategy.EXPONENTIAL, jitter_type=JitterType.FULL)),
        ("Equal Jitter", RetryConfig(strategy=BackoffStrategy.EXPONENTIAL, jitter_type=JitterType.EQUAL)),
        ("Decorrelated Jitter", RetryConfig(strategy=BackoffStrategy.DECORRELATED_JITTER, jitter_type=JitterType.DECORRELATED))
    ]
    
    print(f"{'Strategy':<20} {'Attempts':<10} {'Success Rate':<12} {'Avg Delay':<12}")
    print("-" * 54)
    
    for strategy_name, config in comparison_configs:
        retry_handler = IRCTCStyleRetryHandler(config)
        
        # Run 5 test operations
        for _ in range(5):
            try:
                retry_handler.retry_with_backoff(
                    booking_simulator.book_tatkal_ticket,
                    from_station="Test Station A",
                    to_station="Test Station B"
                )
            except:
                pass  # Ignore failures for comparison
        
        stats = retry_handler.get_stats_summary()
        print(f"{strategy_name:<20} {stats['average_attempts_per_operation']:<10.1f} "
              f"{stats['success_rate_percentage']:<11.1f}% {stats['total_delay_seconds']:<11.1f}s")
    
    print(f"\n🎉 Exponential Backoff demonstration completed!")
    print("एक्सपोनेंशियल बैकऑफ प्रदर्शन पूर्ण!")
    
    print(f"\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:")
    print("1. Jitter prevents thundering herd by spreading retry attempts")
    print("   Jitter retry attempts को फैलाकर thundering herd को रोकता है")
    print("2. Different jitter types suit different scenarios")
    print("   अलग-अलग jitter प्रकार अलग-अलग परिस्थितियों के लिए उपयुक्त हैं")
    print("3. Circuit breaker prevents cascade failures")
    print("   Circuit breaker cascade failures को रोकता है")
    print("4. Regional and contextual adjustments improve success rates")
    print("   क्षेत्रीय और संदर्भित adjustments सफलता दर में सुधार करते हैं")

if __name__ == "__main__":
    main()