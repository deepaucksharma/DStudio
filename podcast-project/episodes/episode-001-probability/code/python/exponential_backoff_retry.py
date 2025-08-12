#!/usr/bin/env python3
"""
Exponential Backoff Retry Mechanism with Jitter
भारतीय payment systems के लिए intelligent retry logic

Indian Context: UPI, NEFT, RTGS payment failures के लिए retry patterns
Mumbai Example: BEST bus pass recharge failures के दौरान retry strategy
"""

import random
import time
import math
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class RetryAttempt:
    """Single retry attempt का data structure"""
    attempt_number: int
    delay_seconds: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    response_time: float = 0.0

class ExponentialBackoffRetry:
    def __init__(self,
                 base_delay: float = 1.0,           # Initial delay in seconds
                 max_delay: float = 60.0,           # Maximum delay cap
                 max_attempts: int = 5,             # Maximum retry attempts
                 backoff_factor: float = 2.0,       # Exponential multiplier
                 jitter_range: float = 0.1):        # Random jitter percentage
        """
        Exponential backoff retry mechanism
        
        Mumbai BEST bus analogy:
        base_delay = बस आने का minimum time
        max_delay = Maximum kitna wait करेंगे
        max_attempts = Kitni बार bus stop पर check करेंगे
        jitter_range = Random variation जैसे Mumbai traffic
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.jitter_range = jitter_range
        
        # Indian payment system error patterns
        self.retriable_errors = {
            "NETWORK_TIMEOUT",
            "SERVER_BUSY", 
            "TEMPORARY_UNAVAILABLE",
            "RATE_LIMIT_EXCEEDED",
            "GATEWAY_TIMEOUT",
            "CONNECTION_RESET"
        }
        
        self.non_retriable_errors = {
            "INSUFFICIENT_BALANCE",
            "INVALID_CREDENTIALS", 
            "ACCOUNT_BLOCKED",
            "FRAUD_DETECTED",
            "INVALID_REQUEST"
        }

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number
        Formula: min(base_delay * (backoff_factor ^ attempt), max_delay) + jitter
        """
        # Basic exponential backoff
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        
        # Apply maximum delay cap
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd problem
        # Mumbai traffic की तरह - exactly same time पर सभी नहीं आते
        jitter = delay * self.jitter_range * (2 * random.random() - 1)
        delay_with_jitter = max(0.1, delay + jitter)  # Minimum 100ms delay
        
        return delay_with_jitter

    def is_retriable_error(self, error: Exception) -> bool:
        """
        Check if error is retriable या permanent failure है
        """
        error_message = str(error).upper()
        
        # Check non-retriable errors first
        for non_retriable in self.non_retriable_errors:
            if non_retriable in error_message:
                return False
                
        # Check retriable errors
        for retriable in self.retriable_errors:
            if retriable in error_message:
                return True
                
        # Default: treat unknown errors as retriable (cautious approach)
        return True

    def execute_with_retry(self, 
                          func: Callable[[], Any],
                          context: str = "Operation") -> Dict:
        """
        Execute function with exponential backoff retry logic
        
        Args:
            func: Function to execute (should raise exception on failure)
            context: Human-readable context for logging
            
        Returns:
            Dictionary with execution results and retry statistics
        """
        
        print(f"🔄 Starting '{context}' with exponential backoff retry")
        print(f"   Max attempts: {self.max_attempts}")
        print(f"   Base delay: {self.base_delay}s, Max delay: {self.max_delay}s")
        
        attempts: List[RetryAttempt] = []
        last_error = None
        
        for attempt_num in range(1, self.max_attempts + 1):
            start_time = datetime.now()
            
            try:
                print(f"\n📞 Attempt {attempt_num}/{self.max_attempts}...")
                
                # Execute the function
                result = func()
                
                # Success case
                response_time = (datetime.now() - start_time).total_seconds()
                
                attempt = RetryAttempt(
                    attempt_number=attempt_num,
                    delay_seconds=0,  # No delay needed, success!
                    timestamp=start_time,
                    success=True,
                    response_time=response_time
                )
                attempts.append(attempt)
                
                print(f"✅ Success in {response_time:.2f}s")
                
                return {
                    "success": True,
                    "result": result,
                    "total_attempts": attempt_num,
                    "total_time": sum(a.delay_seconds + a.response_time for a in attempts),
                    "attempts": attempts
                }
                
            except Exception as error:
                response_time = (datetime.now() - start_time).total_seconds()
                last_error = error
                
                # Check if this error is retriable
                if not self.is_retriable_error(error):
                    print(f"❌ Non-retriable error: {error}")
                    
                    attempt = RetryAttempt(
                        attempt_number=attempt_num,
                        delay_seconds=0,
                        timestamp=start_time,
                        success=False,
                        error_message=str(error),
                        response_time=response_time
                    )
                    attempts.append(attempt)
                    
                    return {
                        "success": False,
                        "error": str(error),
                        "total_attempts": attempt_num,
                        "total_time": sum(a.delay_seconds + a.response_time for a in attempts),
                        "attempts": attempts,
                        "retry_exhausted": False
                    }
                
                print(f"⚠️  Attempt {attempt_num} failed: {error}")
                
                # Calculate delay for next attempt (if not the last attempt)
                delay_seconds = 0
                if attempt_num < self.max_attempts:
                    delay_seconds = self.calculate_delay(attempt_num)
                    print(f"⏰ Waiting {delay_seconds:.2f}s before next attempt...")
                    time.sleep(delay_seconds)
                
                attempt = RetryAttempt(
                    attempt_number=attempt_num,
                    delay_seconds=delay_seconds,
                    timestamp=start_time,
                    success=False,
                    error_message=str(error),
                    response_time=response_time
                )
                attempts.append(attempt)
        
        # All attempts exhausted
        print(f"❌ All {self.max_attempts} attempts failed. Last error: {last_error}")
        
        return {
            "success": False,
            "error": str(last_error),
            "total_attempts": self.max_attempts,
            "total_time": sum(a.delay_seconds + a.response_time for a in attempts),
            "attempts": attempts,
            "retry_exhausted": True
        }

# Indian payment system simulators for testing

class UPIPaymentSimulator:
    """UPI payment system simulator with realistic failure patterns"""
    
    def __init__(self, failure_rate: float = 0.3):
        self.failure_rate = failure_rate
        self.call_count = 0
    
    def make_payment(self, amount: float, upi_id: str) -> Dict:
        """Simulate UPI payment with realistic failures"""
        self.call_count += 1
        
        # Simulate processing time
        processing_time = random.uniform(1.0, 3.0)
        time.sleep(processing_time)
        
        # Different failure scenarios based on call count (eventually succeeds)
        if self.call_count <= 2 and random.random() < self.failure_rate:
            # Common failures in first few attempts
            failures = [
                "NETWORK_TIMEOUT", 
                "SERVER_BUSY",
                "GATEWAY_TIMEOUT"
            ]
            raise Exception(random.choice(failures))
        elif self.call_count == 3 and random.random() < 0.1:
            # Rare permanent failures
            raise Exception("INSUFFICIENT_BALANCE")
        
        # Success case
        return {
            "transaction_id": f"UPI{random.randint(100000, 999999)}",
            "amount": amount,
            "upi_id": upi_id,
            "status": "SUCCESS",
            "processing_time": processing_time
        }

class IRCTCBookingSimulator:
    """IRCTC tatkal booking simulator with realistic failure patterns"""
    
    def __init__(self):
        self.attempt_count = 0
        
    def book_ticket(self, train_number: str, date: str) -> Dict:
        """Simulate IRCTC booking with typical failures"""
        self.attempt_count += 1
        
        # Simulate IRCTC response time (usually slow)
        response_time = random.uniform(5.0, 15.0)
        time.sleep(response_time)
        
        # Peak tatkal booking failures (gets better with retries)
        if self.attempt_count <= 3:
            failure_probability = 0.8 - (self.attempt_count * 0.2)  # Decreasing failure
            
            if random.random() < failure_probability:
                failures = [
                    "SERVER_BUSY",
                    "NETWORK_TIMEOUT", 
                    "TEMPORARY_UNAVAILABLE",
                    "RATE_LIMIT_EXCEEDED"
                ]
                raise Exception(random.choice(failures))
        
        # Success case
        return {
            "pnr": f"PNR{random.randint(1000000000, 9999999999)}",
            "train_number": train_number,
            "date": date,
            "status": "CONFIRMED",
            "attempt_count": self.attempt_count
        }

def demonstrate_retry_patterns():
    """Demonstrate different retry patterns with Indian examples"""
    
    print("🇮🇳 Indian Payment Systems Retry Pattern Demonstration")
    print("=" * 60)
    
    # 1. UPI Payment Retry Example
    print("\n💳 UPI Payment Example (₹500 PhonePe transfer)")
    print("-" * 40)
    
    upi_simulator = UPIPaymentSimulator(failure_rate=0.6)
    upi_retry = ExponentialBackoffRetry(
        base_delay=2.0,     # 2 seconds initial delay
        max_delay=30.0,     # Max 30 seconds wait
        max_attempts=4,     # 4 attempts total
        backoff_factor=2.0, # Double each time
        jitter_range=0.2    # 20% random variation
    )
    
    result = upi_retry.execute_with_retry(
        lambda: upi_simulator.make_payment(500.0, "user@paytm"),
        "UPI Payment to user@paytm"
    )
    
    print(f"\n📊 UPI Payment Results:")
    print(f"   Success: {result['success']}")
    print(f"   Total attempts: {result['total_attempts']}")
    print(f"   Total time: {result['total_time']:.2f}s")
    
    if result['success']:
        print(f"   Transaction ID: {result['result']['transaction_id']}")
    
    # 2. IRCTC Booking Retry Example  
    print("\n🚂 IRCTC Tatkal Booking Example")
    print("-" * 40)
    
    irctc_simulator = IRCTCBookingSimulator()
    irctc_retry = ExponentialBackoffRetry(
        base_delay=5.0,     # 5 seconds initial (IRCTC is slow)
        max_delay=60.0,     # Max 1 minute wait
        max_attempts=5,     # 5 attempts (tatkal में patience चाहिए)
        backoff_factor=1.5, # Slower growth (conservative)
        jitter_range=0.3    # Higher jitter (IRCTC unpredictable)
    )
    
    result = irctc_retry.execute_with_retry(
        lambda: irctc_simulator.book_ticket("12953", "2024-08-15"),
        "IRCTC Mumbai-Delhi Rajdhani Tatkal Booking"
    )
    
    print(f"\n📊 IRCTC Booking Results:")
    print(f"   Success: {result['success']}")
    print(f"   Total attempts: {result['total_attempts']}")
    print(f"   Total time: {result['total_time']:.2f}s")
    
    if result['success']:
        print(f"   PNR: {result['result']['pnr']}")
        print(f"   Status: {result['result']['status']}")

    # 3. Retry Pattern Analysis
    print("\n📈 Retry Pattern Analysis")
    print("-" * 40)
    
    print("Delay progression example (base=1s, factor=2.0, max=60s):")
    basic_retry = ExponentialBackoffRetry(base_delay=1.0, max_delay=60.0, backoff_factor=2.0)
    
    for attempt in range(1, 8):
        delay = basic_retry.calculate_delay(attempt)
        print(f"   Attempt {attempt}: {delay:.2f}s delay")
    
    # Mumbai analogies
    print(f"\n🏙️ Mumbai Analogies:")
    print(f"   Exponential backoff = BEST bus frequency during rush hour")
    print(f"   Jitter = Mumbai traffic unpredictability")
    print(f"   Max attempts = Kitni बार Virar local miss कर सकते हैं")
    print(f"   Non-retriable errors = Wrong platform पर खड़े हैं")

def simulate_different_strategies():
    """Compare different retry strategies"""
    
    print(f"\n🔬 Retry Strategy Comparison")
    print("=" * 50)
    
    # Test with same failure function
    def flaky_service():
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("SERVER_BUSY")
        return "Success!"
    
    strategies = [
        ("Conservative", ExponentialBackoffRetry(1, 30, 3, 1.5, 0.1)),
        ("Aggressive", ExponentialBackoffRetry(0.5, 10, 6, 2.0, 0.0)),
        ("Balanced", ExponentialBackoffRetry(1, 60, 4, 2.0, 0.2)),
        ("Patient", ExponentialBackoffRetry(2, 120, 8, 1.8, 0.3))
    ]
    
    for strategy_name, retry_instance in strategies:
        print(f"\n🎯 Testing {strategy_name} Strategy:")
        
        # Reset flaky service
        random.seed(42)  # Consistent test
        
        start_time = time.time()
        result = retry_instance.execute_with_retry(flaky_service, f"{strategy_name} Test")
        end_time = time.time()
        
        print(f"   Result: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"   Attempts: {result['total_attempts']}")
        print(f"   Wall time: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    # Demonstrate retry patterns
    demonstrate_retry_patterns()
    
    # Compare different strategies
    simulate_different_strategies()
    
    print(f"\n💡 Key Learnings:")
    print(f"   1. Use exponential backoff for thundering herd prevention")
    print(f"   2. Add jitter to prevent synchronized retries")
    print(f"   3. Distinguish between retriable and non-retriable errors")
    print(f"   4. Set reasonable maximum attempts and delays")
    print(f"   5. Monitor retry patterns to optimize parameters")