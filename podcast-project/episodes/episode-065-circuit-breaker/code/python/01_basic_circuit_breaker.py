#!/usr/bin/env python3
"""
Basic Circuit Breaker Implementation
सबसे बुनियादी Circuit Breaker pattern का implementation

Circuit breaker एक electrical switch की तरह काम करता है
जो system को protect करता है failures से
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional
import random


class CircuitState(Enum):
    """Circuit breaker के तीन states हैं"""
    CLOSED = "CLOSED"      # सब कुछ normal है, requests pass हो रहे हैं
    OPEN = "OPEN"          # बहुत failures हैं, सभी requests reject
    HALF_OPEN = "HALF_OPEN"  # Testing phase, limited requests allow


class CircuitBreakerError(Exception):
    """Circuit breaker specific exception"""
    pass


class BasicCircuitBreaker:
    """
    Basic Circuit Breaker Implementation
    यह Mumbai की electrical board की तरह काम करता है
    जब overload होता है तो automatic cut हो जाता है
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_duration: int = 60,
        expected_exception: Exception = Exception
    ):
        """
        Args:
            failure_threshold: Kitni failures के बाद circuit open करना है
            timeout_duration: Kitni देर तक circuit open रखना है (seconds)
            expected_exception: कौन से exceptions को failure मानना है
        """
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.expected_exception = expected_exception
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        # Thread safety के लिए lock
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Protected function call with circuit breaker
        यह function actual service call को wrap करता है
        """
        with self._lock:
            # Current state check करते हैं
            current_state = self._get_current_state()
            
            if current_state == CircuitState.OPEN:
                # Circuit open है, request reject करते हैं
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}"
                )
            
            if current_state == CircuitState.HALF_OPEN:
                # Half-open state में limited requests allow करते हैं
                return self._execute_half_open(func, *args, **kwargs)
            
            # CLOSED state - normal execution
            return self._execute_closed(func, *args, **kwargs)
    
    def _get_current_state(self) -> CircuitState:
        """Current state determine करता है timeout के basis पर"""
        if self.state == CircuitState.OPEN:
            if self.last_failure_time:
                time_elapsed = time.time() - self.last_failure_time
                if time_elapsed >= self.timeout_duration:
                    # Timeout हो गया, half-open में जाते हैं
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    print("🔄 Circuit breaker moved to HALF_OPEN state")
        
        return self.state
    
    def _execute_closed(self, func: Callable, *args, **kwargs) -> Any:
        """CLOSED state में function execute करता है"""
        try:
            result = func(*args, **kwargs)
            # Success - failure count reset करते हैं
            self.failure_count = 0
            return result
        
        except self.expected_exception as e:
            # Failure count increase करते हैं
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            print(f"❌ Failure #{self.failure_count}: {str(e)}")
            
            # Threshold check करते हैं
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"🔴 Circuit breaker OPENED after {self.failure_count} failures")
            
            raise e
    
    def _execute_half_open(self, func: Callable, *args, **kwargs) -> Any:
        """HALF_OPEN state में function execute करता है"""
        try:
            result = func(*args, **kwargs)
            # Success in half-open state
            self.success_count += 1
            
            # अगर कुछ successful calls हैं तो circuit close करते हैं
            if self.success_count >= 3:  # 3 successful calls के बाद
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("✅ Circuit breaker CLOSED - Service recovered")
            
            return result
        
        except self.expected_exception as e:
            # Failure in half-open - वापस open करते हैं
            self.state = CircuitState.OPEN
            self.failure_count += 1
            self.last_failure_time = time.time()
            print("🔴 Circuit breaker back to OPEN state")
            raise e
    
    def get_state(self) -> CircuitState:
        """Current circuit state return करता है"""
        return self._get_current_state()
    
    def get_metrics(self) -> dict:
        """Circuit breaker metrics return करता है"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold,
            "timeout_duration": self.timeout_duration
        }


# Example usage और testing
def unreliable_service():
    """
    यह एक unreliable service को simulate करता है
    जैसे कि third-party payment gateway जो randomly fail होता है
    """
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Service temporarily unavailable")
    return "Service call successful"


def test_circuit_breaker():
    """Circuit breaker का complete test"""
    print("🧪 Testing Circuit Breaker Pattern")
    print("=" * 50)
    
    # Circuit breaker initialize करते हैं
    cb = BasicCircuitBreaker(
        failure_threshold=3,
        timeout_duration=5,  # 5 seconds timeout
        expected_exception=Exception
    )
    
    # Test 1: Normal failures until circuit opens
    print("\n📊 Test 1: Failures until circuit opens")
    for i in range(6):
        try:
            result = cb.call(unreliable_service)
            print(f"✅ Call {i+1}: {result}")
        except CircuitBreakerError as e:
            print(f"🚫 Call {i+1}: Circuit breaker blocked - {e}")
        except Exception as e:
            print(f"❌ Call {i+1}: Service error - {e}")
        
        print(f"   State: {cb.get_state().value}")
        time.sleep(0.5)
    
    # Test 2: Wait for timeout and test half-open
    print(f"\n⏳ Waiting {cb.timeout_duration} seconds for circuit to go half-open...")
    time.sleep(cb.timeout_duration + 1)
    
    print("\n📊 Test 2: Half-open state testing")
    for i in range(5):
        try:
            result = cb.call(unreliable_service)
            print(f"✅ Call {i+1}: {result}")
        except CircuitBreakerError as e:
            print(f"🚫 Call {i+1}: Circuit breaker blocked - {e}")
        except Exception as e:
            print(f"❌ Call {i+1}: Service error - {e}")
        
        print(f"   State: {cb.get_state().value}")
        time.sleep(0.5)
    
    # Final metrics
    print("\n📈 Final Metrics:")
    metrics = cb.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_circuit_breaker()