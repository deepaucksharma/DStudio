#!/usr/bin/env python3
"""
Hystrix-Style Circuit Breaker Implementation
Netflix के Hystrix library जैसा advanced circuit breaker

यह implementation statistical data और sliding window का use करती है
जो production systems में actual में use होता है
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional, Dict
from collections import deque
from dataclasses import dataclass
import statistics
import json


class CircuitState(Enum):
    """Circuit states - Hystrix style"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class RequestMetrics:
    """हर request की metrics store करने के लिए"""
    timestamp: float
    success: bool
    duration_ms: float
    error_type: Optional[str] = None


@dataclass
class CircuitMetrics:
    """Circuit breaker की overall metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_percentage: float = 0.0
    avg_response_time: float = 0.0
    circuit_open_count: int = 0


class HystrixCircuitBreaker:
    """
    Hystrix-style Circuit Breaker
    यह Netflix के production-grade circuit breaker की तरह काम करता है
    Statistical data और sliding window का use करता है
    """
    
    def __init__(
        self,
        request_volume_threshold: int = 20,
        error_threshold_percentage: int = 50,
        sleep_window_ms: int = 5000,
        metrics_rolling_window_ms: int = 10000,
        metrics_rolling_buckets: int = 10,
        timeout_ms: int = 1000,
        max_concurrent_requests: int = 10
    ):
        """
        Args:
            request_volume_threshold: कम से कम इतने requests चाहिए circuit खोलने के लिए
            error_threshold_percentage: इतने % errors पर circuit खुलेगा
            sleep_window_ms: Circuit open रहने का time (milliseconds)
            metrics_rolling_window_ms: Rolling window का size
            metrics_rolling_buckets: Rolling window में कितने buckets
            timeout_ms: Request timeout in milliseconds
            max_concurrent_requests: Maximum concurrent requests allowed
        """
        self.request_volume_threshold = request_volume_threshold
        self.error_threshold_percentage = error_threshold_percentage
        self.sleep_window_ms = sleep_window_ms
        self.metrics_rolling_window_ms = metrics_rolling_window_ms
        self.metrics_rolling_buckets = metrics_rolling_buckets
        self.timeout_ms = timeout_ms
        self.max_concurrent_requests = max_concurrent_requests
        
        # State management
        self.state = CircuitState.CLOSED
        self.circuit_opened_time = None
        self.half_open_success_count = 0
        
        # Metrics storage - sliding window approach
        self.request_history = deque()
        self.concurrent_requests = 0
        self.metrics = CircuitMetrics()
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"🔧 Hystrix Circuit Breaker initialized:")
        print(f"   - Request volume threshold: {request_volume_threshold}")
        print(f"   - Error threshold: {error_threshold_percentage}%")
        print(f"   - Sleep window: {sleep_window_ms}ms")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Protected function call with Hystrix-style circuit breaker
        """
        with self._lock:
            # Current state update करते हैं
            self._update_circuit_state()
            
            # Circuit state check करते हैं
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. Error rate: {self.metrics.error_percentage:.1f}%"
                )
            
            # Concurrent request limit check
            if self.concurrent_requests >= self.max_concurrent_requests:
                raise CircuitBreakerError(
                    f"Too many concurrent requests: {self.concurrent_requests}/{self.max_concurrent_requests}"
                )
            
            # Request execute करते हैं
            return self._execute_request(func, *args, **kwargs)
    
    def _execute_request(self, func: Callable, *args, **kwargs) -> Any:
        """Request execute करता है और metrics collect करता है"""
        start_time = time.time()
        self.concurrent_requests += 1
        
        try:
            # Timeout के साथ function call करते हैं
            result = self._call_with_timeout(func, self.timeout_ms, *args, **kwargs)
            
            # Success metrics record करते हैं
            duration_ms = (time.time() - start_time) * 1000
            self._record_success(duration_ms)
            
            return result
        
        except Exception as e:
            # Failure metrics record करते हैं
            duration_ms = (time.time() - start_time) * 1000
            self._record_failure(duration_ms, str(e))
            raise e
        
        finally:
            self.concurrent_requests -= 1
    
    def _call_with_timeout(self, func: Callable, timeout_ms: int, *args, **kwargs) -> Any:
        """Function को timeout के साथ call करता है"""
        import signal
        
        class TimeoutException(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutException("Request timeout")
        
        # Timeout setup (Unix/Linux systems के लिए)
        try:
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_ms // 1000)  # Convert to seconds
            
            result = func(*args, **kwargs)
            
            signal.alarm(0)  # Cancel alarm
            signal.signal(signal.SIGALRM, old_handler)
            
            return result
        
        except TimeoutException:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            raise Exception(f"Request timeout after {timeout_ms}ms")
    
    def _record_success(self, duration_ms: float):
        """Success metrics record करता है"""
        metrics = RequestMetrics(
            timestamp=time.time(),
            success=True,
            duration_ms=duration_ms
        )
        self.request_history.append(metrics)
        self._clean_old_metrics()
        
        # Half-open state में success count करते हैं
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1
            
            # अगर enough successes हैं तो circuit close करते हैं
            if self.half_open_success_count >= 3:
                self._close_circuit()
    
    def _record_failure(self, duration_ms: float, error_type: str):
        """Failure metrics record करता है"""
        metrics = RequestMetrics(
            timestamp=time.time(),
            success=False,
            duration_ms=duration_ms,
            error_type=error_type
        )
        self.request_history.append(metrics)
        self._clean_old_metrics()
        
        # Half-open state में failure का मतलब circuit open करना है
        if self.state == CircuitState.HALF_OPEN:
            self._open_circuit()
    
    def _clean_old_metrics(self):
        """Sliding window के बाहर के old metrics को clean करता है"""
        current_time = time.time()
        cutoff_time = current_time - (self.metrics_rolling_window_ms / 1000)
        
        while self.request_history and self.request_history[0].timestamp < cutoff_time:
            self.request_history.popleft()
    
    def _update_circuit_state(self):
        """Circuit state को current metrics के basis पर update करता है"""
        if self.state == CircuitState.OPEN:
            # Check if sleep window has elapsed
            if self.circuit_opened_time:
                elapsed_ms = (time.time() - self.circuit_opened_time) * 1000
                if elapsed_ms >= self.sleep_window_ms:
                    self._move_to_half_open()
        
        elif self.state == CircuitState.CLOSED:
            # Check if circuit should be opened based on metrics
            self._update_metrics()
            if self._should_open_circuit():
                self._open_circuit()
    
    def _update_metrics(self):
        """Current metrics calculate करता है sliding window के basis पर"""
        if not self.request_history:
            return
        
        total_requests = len(self.request_history)
        successful_requests = sum(1 for req in self.request_history if req.success)
        failed_requests = total_requests - successful_requests
        
        error_percentage = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Average response time calculate करते हैं
        avg_response_time = statistics.mean([req.duration_ms for req in self.request_history])
        
        self.metrics = CircuitMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            error_percentage=error_percentage,
            avg_response_time=avg_response_time
        )
    
    def _should_open_circuit(self) -> bool:
        """Check करता है कि circuit open करना चाहिए या नहीं"""
        # पहले volume threshold check करते हैं
        if self.metrics.total_requests < self.request_volume_threshold:
            return False
        
        # फिर error percentage check करते हैं
        if self.metrics.error_percentage >= self.error_threshold_percentage:
            return True
        
        return False
    
    def _open_circuit(self):
        """Circuit को open state में move करता है"""
        self.state = CircuitState.OPEN
        self.circuit_opened_time = time.time()
        self.metrics.circuit_open_count += 1
        self.half_open_success_count = 0
        
        print(f"🔴 Circuit OPENED - Error rate: {self.metrics.error_percentage:.1f}%")
    
    def _move_to_half_open(self):
        """Circuit को half-open state में move करता है"""
        self.state = CircuitState.HALF_OPEN
        self.half_open_success_count = 0
        
        print("🟡 Circuit moved to HALF_OPEN - Testing service recovery")
    
    def _close_circuit(self):
        """Circuit को close state में move करता है"""
        self.state = CircuitState.CLOSED
        self.circuit_opened_time = None
        self.half_open_success_count = 0
        
        print("✅ Circuit CLOSED - Service recovered")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Comprehensive metrics return करता है"""
        self._update_metrics()
        
        return {
            "circuit_state": self.state.value,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "error_percentage": round(self.metrics.error_percentage, 2),
            "avg_response_time_ms": round(self.metrics.avg_response_time, 2),
            "concurrent_requests": self.concurrent_requests,
            "circuit_open_count": self.metrics.circuit_open_count,
            "request_volume_threshold": self.request_volume_threshold,
            "error_threshold_percentage": self.error_threshold_percentage
        }
    
    def force_open(self):
        """Circuit को manually open करता है (testing के लिए)"""
        self._open_circuit()
    
    def force_close(self):
        """Circuit को manually close करता है (testing के लिए)"""
        self._close_circuit()


class CircuitBreakerError(Exception):
    """Circuit breaker specific exceptions"""
    pass


# Example usage और testing
def flaky_payment_service(success_rate: float = 0.3):
    """
    Payment service simulation
    यह service randomly fail होती है specified success rate के साथ
    """
    import random
    
    # Response time simulation
    time.sleep(random.uniform(0.1, 0.5))
    
    if random.random() < success_rate:
        return {"status": "success", "transaction_id": f"TXN_{int(time.time())}"}
    else:
        raise Exception("Payment gateway timeout")


def test_hystrix_circuit_breaker():
    """Hystrix circuit breaker का comprehensive test"""
    print("🧪 Testing Hystrix-Style Circuit Breaker")
    print("=" * 60)
    
    # Circuit breaker initialize करते हैं
    cb = HystrixCircuitBreaker(
        request_volume_threshold=10,
        error_threshold_percentage=60,
        sleep_window_ms=3000,
        timeout_ms=800
    )
    
    # Test Phase 1: Generate enough requests to trigger circuit opening
    print("\n📊 Phase 1: Generating requests to trigger circuit opening")
    print("-" * 50)
    
    for i in range(25):
        try:
            result = cb.call(flaky_payment_service, success_rate=0.2)  # 20% success rate
            print(f"✅ Request {i+1}: Payment successful")
        except CircuitBreakerError as e:
            print(f"🚫 Request {i+1}: Circuit breaker blocked")
        except Exception as e:
            print(f"❌ Request {i+1}: Payment failed - {str(e)[:30]}")
        
        # हर 5 requests के बाद metrics show करते हैं
        if (i + 1) % 5 == 0:
            metrics = cb.get_metrics()
            print(f"   📈 Metrics: {metrics['total_requests']} total, "
                  f"{metrics['error_percentage']:.1f}% errors, "
                  f"State: {metrics['circuit_state']}")
        
        time.sleep(0.1)
    
    # Test Phase 2: Wait for half-open and recovery
    print(f"\n⏳ Phase 2: Waiting for circuit to go half-open...")
    time.sleep(4)  # Wait for sleep window
    
    print("\n📊 Phase 3: Testing recovery with improved service")
    print("-" * 50)
    
    for i in range(10):
        try:
            result = cb.call(flaky_payment_service, success_rate=0.9)  # 90% success rate
            print(f"✅ Recovery Request {i+1}: Payment successful")
        except CircuitBreakerError as e:
            print(f"🚫 Recovery Request {i+1}: Circuit breaker blocked")
        except Exception as e:
            print(f"❌ Recovery Request {i+1}: Payment failed")
        
        metrics = cb.get_metrics()
        print(f"   State: {metrics['circuit_state']}")
        time.sleep(0.5)
    
    # Final comprehensive metrics
    print("\n📈 Final Comprehensive Metrics:")
    print("=" * 40)
    final_metrics = cb.get_metrics()
    
    print(json.dumps(final_metrics, indent=2))


if __name__ == "__main__":
    test_hystrix_circuit_breaker()