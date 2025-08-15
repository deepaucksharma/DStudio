#!/usr/bin/env python3
"""
Circuit Breaker with Advanced Timeout Handling
Timeout scenarios और edge cases का comprehensive handling

Production systems में timeout एक बहुत common cause है failures का
इस implementation में विभिन्न timeout scenarios handle करते हैं
"""

import time
import threading
import signal
import asyncio
from enum import Enum
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import concurrent.futures
import functools
import inspect


class TimeoutType(Enum):
    """Different types of timeouts"""
    FUNCTION_TIMEOUT = "function_timeout"      # Function execution timeout
    CIRCUIT_TIMEOUT = "circuit_timeout"       # Circuit open timeout
    CONNECTION_TIMEOUT = "connection_timeout" # Connection establishment timeout
    READ_TIMEOUT = "read_timeout"             # Data read timeout
    OVERALL_TIMEOUT = "overall_timeout"       # Overall request timeout


@dataclass
class TimeoutConfig:
    """Timeout configuration for different scenarios"""
    function_timeout: float = 5.0       # Function execution timeout (seconds)
    connection_timeout: float = 3.0     # Connection timeout
    read_timeout: float = 10.0          # Read timeout
    circuit_open_timeout: float = 30.0  # Circuit breaker open timeout
    overall_timeout: float = 15.0       # Overall request timeout
    
    # Timeout escalation settings
    enable_timeout_escalation: bool = True
    escalation_factor: float = 1.5       # Increase timeout by this factor on repeated failures
    max_escalation_factor: float = 3.0   # Maximum escalation
    escalation_reset_window: float = 300.0  # Reset escalation after this time (seconds)


@dataclass
class TimeoutMetrics:
    """Timeout related metrics"""
    total_timeouts: int = 0
    function_timeouts: int = 0
    connection_timeouts: int = 0
    read_timeouts: int = 0
    circuit_timeouts: int = 0
    avg_timeout_duration: float = 0.0
    max_timeout_duration: float = 0.0
    timeout_escalations: int = 0


class TimeoutCircuitBreaker:
    """
    Advanced Circuit Breaker with comprehensive timeout handling
    यह implementation विभिन्न प्रकार के timeouts handle करती है
    और production-grade timeout management provide करती है
    """
    
    def __init__(
        self, 
        name: str,
        timeout_config: TimeoutConfig = None,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ):
        self.name = name
        self.timeout_config = timeout_config or TimeoutConfig()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        # Circuit state
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_opened_time = None
        
        # Timeout tracking
        self.timeout_metrics = TimeoutMetrics()
        self.current_escalation = 1.0
        self.last_escalation_time = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Timeout history for analysis
        self.timeout_history = []
        
        print(f"🔧 Timeout Circuit Breaker '{name}' initialized")
        print(f"   - Function timeout: {self.timeout_config.function_timeout}s")
        print(f"   - Connection timeout: {self.timeout_config.connection_timeout}s")
        print(f"   - Overall timeout: {self.timeout_config.overall_timeout}s")
    
    def call(self, func: Callable, *args, timeout_type: TimeoutType = TimeoutType.FUNCTION_TIMEOUT, **kwargs) -> Any:
        """
        Execute function with timeout protection and circuit breaker
        """
        with self._lock:
            # Check circuit state
            if self._should_reject_request():
                raise CircuitBreakerError(
                    f"Circuit '{self.name}' is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
            
            # Get current timeout value (with escalation)
            timeout_value = self._get_escalated_timeout(timeout_type)
            
            # Execute with timeout
            return self._execute_with_timeout(
                func, timeout_value, timeout_type, *args, **kwargs
            )
    
    async def call_async(
        self, 
        func: Callable, 
        *args, 
        timeout_type: TimeoutType = TimeoutType.FUNCTION_TIMEOUT, 
        **kwargs
    ) -> Any:
        """
        Async version of call method
        """
        with self._lock:
            if self._should_reject_request():
                raise CircuitBreakerError(f"Circuit '{self.name}' is OPEN")
            
            timeout_value = self._get_escalated_timeout(timeout_type)
        
        return await self._execute_async_with_timeout(
            func, timeout_value, timeout_type, *args, **kwargs
        )
    
    def _should_reject_request(self) -> bool:
        """Check if request should be rejected due to circuit state"""
        if self.state == "CLOSED":
            return False
        
        if self.state == "OPEN":
            # Check if enough time has passed to try half-open
            if self.circuit_opened_time:
                elapsed = time.time() - self.circuit_opened_time
                if elapsed >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    print(f"🟡 Circuit '{self.name}' moved to HALF_OPEN")
                    return False
            return True
        
        # HALF_OPEN state - allow limited requests
        return False
    
    def _get_escalated_timeout(self, timeout_type: TimeoutType) -> float:
        """Get timeout value with escalation applied"""
        base_timeout = self._get_base_timeout(timeout_type)
        
        if not self.timeout_config.enable_timeout_escalation:
            return base_timeout
        
        # Check if escalation should be reset
        if self.last_escalation_time:
            elapsed = time.time() - self.last_escalation_time
            if elapsed >= self.timeout_config.escalation_reset_window:
                self.current_escalation = 1.0
                self.last_escalation_time = None
                print(f"🔄 Timeout escalation reset for '{self.name}'")
        
        escalated_timeout = base_timeout * self.current_escalation
        
        if self.current_escalation > 1.0:
            print(f"⏰ Using escalated timeout: {escalated_timeout:.2f}s "
                  f"(factor: {self.current_escalation:.2f})")
        
        return escalated_timeout
    
    def _get_base_timeout(self, timeout_type: TimeoutType) -> float:
        """Get base timeout value for given type"""
        timeout_map = {
            TimeoutType.FUNCTION_TIMEOUT: self.timeout_config.function_timeout,
            TimeoutType.CONNECTION_TIMEOUT: self.timeout_config.connection_timeout,
            TimeoutType.READ_TIMEOUT: self.timeout_config.read_timeout,
            TimeoutType.CIRCUIT_TIMEOUT: self.timeout_config.circuit_open_timeout,
            TimeoutType.OVERALL_TIMEOUT: self.timeout_config.overall_timeout
        }
        return timeout_map.get(timeout_type, self.timeout_config.function_timeout)
    
    def _execute_with_timeout(
        self, 
        func: Callable, 
        timeout_value: float, 
        timeout_type: TimeoutType,
        *args, 
        **kwargs
    ) -> Any:
        """Execute function with timeout using ThreadPoolExecutor"""
        start_time = time.time()
        
        try:
            # Check if function is async
            if inspect.iscoroutinefunction(func):
                # Handle async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        asyncio.wait_for(
                            func(*args, **kwargs), 
                            timeout=timeout_value
                        )
                    )
                finally:
                    loop.close()
            else:
                # Handle sync function with ThreadPoolExecutor
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, *args, **kwargs)
                    result = future.result(timeout=timeout_value)
            
            # Success handling
            execution_time = time.time() - start_time
            self._handle_success(execution_time)
            
            return result
        
        except (concurrent.futures.TimeoutError, asyncio.TimeoutError) as e:
            # Timeout handling
            execution_time = time.time() - start_time
            self._handle_timeout(timeout_type, execution_time, timeout_value)
            raise TimeoutError(
                f"Function timed out after {execution_time:.2f}s "
                f"(limit: {timeout_value:.2f}s, type: {timeout_type.value})"
            )
        
        except Exception as e:
            # Other failure handling
            execution_time = time.time() - start_time
            self._handle_failure(e, execution_time)
            raise e
    
    async def _execute_async_with_timeout(
        self,
        func: Callable,
        timeout_value: float,
        timeout_type: TimeoutType,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with timeout"""
        start_time = time.time()
        
        try:
            if inspect.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_value
                )
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    functools.partial(func, *args, **kwargs)
                )
            
            execution_time = time.time() - start_time
            self._handle_success(execution_time)
            
            return result
        
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self._handle_timeout(timeout_type, execution_time, timeout_value)
            raise TimeoutError(
                f"Async function timed out after {execution_time:.2f}s "
                f"(limit: {timeout_value:.2f}s, type: {timeout_type.value})"
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_failure(e, execution_time)
            raise e
    
    def _handle_success(self, execution_time: float):
        """Handle successful execution"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            self.circuit_opened_time = None
            print(f"✅ Circuit '{self.name}' CLOSED - Service recovered")
        
        # Reset escalation on success
        if self.current_escalation > 1.0:
            self.current_escalation = max(1.0, self.current_escalation * 0.9)
    
    def _handle_timeout(self, timeout_type: TimeoutType, execution_time: float, timeout_limit: float):
        """Handle timeout scenarios"""
        self.timeout_metrics.total_timeouts += 1
        
        # Update specific timeout counters
        if timeout_type == TimeoutType.FUNCTION_TIMEOUT:
            self.timeout_metrics.function_timeouts += 1
        elif timeout_type == TimeoutType.CONNECTION_TIMEOUT:
            self.timeout_metrics.connection_timeouts += 1
        elif timeout_type == TimeoutType.READ_TIMEOUT:
            self.timeout_metrics.read_timeouts += 1
        
        # Update timeout duration metrics
        self.timeout_metrics.max_timeout_duration = max(
            self.timeout_metrics.max_timeout_duration, 
            execution_time
        )
        
        # Add to timeout history
        self.timeout_history.append({
            'timestamp': datetime.now(),
            'type': timeout_type.value,
            'duration': execution_time,
            'limit': timeout_limit,
            'escalation_factor': self.current_escalation
        })
        
        # Keep only recent history
        if len(self.timeout_history) > 100:
            self.timeout_history = self.timeout_history[-100:]
        
        # Escalate timeout for future requests
        self._escalate_timeout()
        
        # Handle as failure for circuit breaker logic
        self._handle_failure(TimeoutError("Timeout occurred"), execution_time)
        
        print(f"⏰ Timeout in '{self.name}': {timeout_type.value} "
              f"({execution_time:.2f}s / {timeout_limit:.2f}s)")
    
    def _escalate_timeout(self):
        """Escalate timeout for future requests"""
        if not self.timeout_config.enable_timeout_escalation:
            return
        
        old_escalation = self.current_escalation
        self.current_escalation = min(
            self.current_escalation * self.timeout_config.escalation_factor,
            self.timeout_config.max_escalation_factor
        )
        
        if self.current_escalation != old_escalation:
            self.timeout_metrics.timeout_escalations += 1
            self.last_escalation_time = time.time()
            print(f"📈 Timeout escalated: {old_escalation:.2f} → {self.current_escalation:.2f}")
    
    def _handle_failure(self, error: Exception, execution_time: float):
        """Handle failure scenarios"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Check if circuit should be opened
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.circuit_opened_time = time.time()
            print(f"🔴 Circuit '{self.name}' OPENED after {self.failure_count} failures")
        
        print(f"❌ Failure in '{self.name}': {str(error)[:50]} ({execution_time:.3f}s)")
    
    def get_timeout_metrics(self) -> Dict[str, Any]:
        """Get comprehensive timeout metrics"""
        # Calculate average timeout duration
        if self.timeout_history:
            avg_duration = sum(t['duration'] for t in self.timeout_history) / len(self.timeout_history)
            self.timeout_metrics.avg_timeout_duration = avg_duration
        
        return {
            'name': self.name,
            'state': self.state,
            'total_timeouts': self.timeout_metrics.total_timeouts,
            'function_timeouts': self.timeout_metrics.function_timeouts,
            'connection_timeouts': self.timeout_metrics.connection_timeouts,
            'read_timeouts': self.timeout_metrics.read_timeouts,
            'avg_timeout_duration': round(self.timeout_metrics.avg_timeout_duration, 3),
            'max_timeout_duration': round(self.timeout_metrics.max_timeout_duration, 3),
            'current_escalation_factor': round(self.current_escalation, 2),
            'timeout_escalations': self.timeout_metrics.timeout_escalations,
            'failure_count': self.failure_count,
            'recent_timeouts': len([t for t in self.timeout_history 
                                  if (datetime.now() - t['timestamp']).seconds < 300])
        }
    
    def get_timeout_analysis(self) -> Dict[str, Any]:
        """Get detailed timeout analysis"""
        if not self.timeout_history:
            return {"message": "No timeout history available"}
        
        recent_timeouts = [t for t in self.timeout_history 
                          if (datetime.now() - t['timestamp']).seconds < 300]
        
        timeout_by_type = {}
        for timeout in self.timeout_history:
            timeout_type = timeout['type']
            if timeout_type not in timeout_by_type:
                timeout_by_type[timeout_type] = []
            timeout_by_type[timeout_type].append(timeout['duration'])
        
        analysis = {
            'total_timeout_history': len(self.timeout_history),
            'recent_timeouts_5min': len(recent_timeouts),
            'timeout_types_breakdown': {},
            'escalation_effectiveness': self._analyze_escalation_effectiveness()
        }
        
        for timeout_type, durations in timeout_by_type.items():
            analysis['timeout_types_breakdown'][timeout_type] = {
                'count': len(durations),
                'avg_duration': round(sum(durations) / len(durations), 3),
                'max_duration': round(max(durations), 3),
                'min_duration': round(min(durations), 3)
            }
        
        return analysis
    
    def _analyze_escalation_effectiveness(self) -> Dict[str, Any]:
        """Analyze if timeout escalation is helping"""
        if len(self.timeout_history) < 2:
            return {"message": "Insufficient data"}
        
        escalated_timeouts = [t for t in self.timeout_history if t['escalation_factor'] > 1.0]
        normal_timeouts = [t for t in self.timeout_history if t['escalation_factor'] == 1.0]
        
        if not escalated_timeouts:
            return {"message": "No escalated timeouts"}
        
        escalated_success_rate = len([t for t in escalated_timeouts if t['duration'] < t['limit']]) / len(escalated_timeouts)
        normal_success_rate = len([t for t in normal_timeouts if t['duration'] < t['limit']]) / len(normal_timeouts) if normal_timeouts else 0
        
        return {
            'escalated_timeouts': len(escalated_timeouts),
            'normal_timeouts': len(normal_timeouts),
            'escalated_success_rate': round(escalated_success_rate * 100, 2),
            'normal_success_rate': round(normal_success_rate * 100, 2),
            'escalation_helping': escalated_success_rate > normal_success_rate
        }
    
    def reset_escalation(self):
        """Manually reset timeout escalation"""
        self.current_escalation = 1.0
        self.last_escalation_time = None
        self.timeout_metrics.timeout_escalations = 0
        print(f"🔄 Timeout escalation reset for '{self.name}'")


class CircuitBreakerError(Exception):
    """Circuit breaker is open"""
    pass


# Example services for testing
def slow_database_query(query: str, delay: float = 2.0):
    """Simulates a slow database query"""
    print(f"🔍 Executing query: {query}")
    time.sleep(delay)
    return f"Query result for: {query}"


def flaky_api_call(endpoint: str, fail_rate: float = 0.3, timeout_rate: float = 0.4):
    """Simulates a flaky API call"""
    import random
    
    print(f"🌐 Calling API: {endpoint}")
    
    # Simulate various delays
    if random.random() < timeout_rate:
        time.sleep(8.0)  # Will timeout
    else:
        time.sleep(random.uniform(0.5, 2.0))
    
    if random.random() < fail_rate:
        raise Exception(f"API {endpoint} returned 500 error")
    
    return f"API response from {endpoint}"


async def async_service_call(service: str, delay: float = 1.0):
    """Async service call simulation"""
    print(f"⚡ Async call to: {service}")
    await asyncio.sleep(delay)
    return f"Async response from {service}"


# Testing functions
def test_timeout_circuit_breaker():
    """Test timeout circuit breaker with various scenarios"""
    print("🧪 Testing Timeout Circuit Breaker")
    print("=" * 60)
    
    # Custom timeout configuration
    timeout_config = TimeoutConfig(
        function_timeout=3.0,
        connection_timeout=2.0,
        overall_timeout=5.0,
        enable_timeout_escalation=True,
        escalation_factor=1.5,
        max_escalation_factor=3.0
    )
    
    cb = TimeoutCircuitBreaker("test-service", timeout_config, failure_threshold=3)
    
    print("\n📊 Phase 1: Testing different timeout scenarios")
    print("-" * 50)
    
    # Test cases with different timeout types
    test_cases = [
        ("Normal Query", lambda: slow_database_query("SELECT * FROM users", 1.0), TimeoutType.FUNCTION_TIMEOUT),
        ("Slow Query", lambda: slow_database_query("SELECT * FROM big_table", 4.0), TimeoutType.FUNCTION_TIMEOUT),
        ("API Call", lambda: flaky_api_call("/users", 0.2, 0.6), TimeoutType.CONNECTION_TIMEOUT),
        ("Another API", lambda: flaky_api_call("/orders", 0.3, 0.5), TimeoutType.READ_TIMEOUT),
    ]
    
    for i, (name, func, timeout_type) in enumerate(test_cases):
        for attempt in range(3):
            try:
                result = cb.call(func, timeout_type=timeout_type)
                print(f"✅ {name} (Attempt {attempt+1}): Success")
            except TimeoutError as e:
                print(f"⏰ {name} (Attempt {attempt+1}): {str(e)[:60]}...")
            except CircuitBreakerError as e:
                print(f"🚫 {name} (Attempt {attempt+1}): {str(e)[:60]}...")
            except Exception as e:
                print(f"❌ {name} (Attempt {attempt+1}): {str(e)[:60]}...")
            
            time.sleep(0.5)
        
        # Show metrics after each test case
        if i % 2 == 1:
            print("\n📈 Current Timeout Metrics:")
            metrics = cb.get_timeout_metrics()
            for key, value in metrics.items():
                print(f"   {key}: {value}")
            print()
    
    # Wait for circuit recovery
    if cb.state == "OPEN":
        print(f"\n⏳ Waiting for circuit recovery...")
        time.sleep(cb.recovery_timeout + 1)
    
    # Test escalation effectiveness
    print("\n📊 Phase 2: Testing timeout escalation")
    print("-" * 50)
    
    for i in range(5):
        try:
            result = cb.call(
                lambda: slow_database_query(f"Query {i+1}", 2.5),
                timeout_type=TimeoutType.FUNCTION_TIMEOUT
            )
            print(f"✅ Escalation Test {i+1}: Success")
        except Exception as e:
            print(f"❌ Escalation Test {i+1}: {str(e)[:50]}...")
        
        time.sleep(1.0)
    
    # Final analysis
    print("\n📈 Final Timeout Metrics:")
    final_metrics = cb.get_timeout_metrics()
    for key, value in final_metrics.items():
        print(f"   {key}: {value}")
    
    print("\n🔍 Timeout Analysis:")
    analysis = cb.get_timeout_analysis()
    import json
    print(json.dumps(analysis, indent=2, default=str))


async def test_async_timeout_circuit_breaker():
    """Test async timeout circuit breaker"""
    print("\n🧪 Testing Async Timeout Circuit Breaker")
    print("=" * 60)
    
    timeout_config = TimeoutConfig(
        function_timeout=2.0,
        overall_timeout=3.0,
        enable_timeout_escalation=True
    )
    
    cb = TimeoutCircuitBreaker("async-service", timeout_config)
    
    # Test async calls
    test_cases = [
        ("Fast Service", lambda: async_service_call("fast-api", 0.5)),
        ("Medium Service", lambda: async_service_call("medium-api", 2.5)),
        ("Slow Service", lambda: async_service_call("slow-api", 4.0)),
    ]
    
    for name, func in test_cases:
        for attempt in range(2):
            try:
                result = await cb.call_async(func)
                print(f"✅ {name} (Attempt {attempt+1}): Success")
            except Exception as e:
                print(f"❌ {name} (Attempt {attempt+1}): {str(e)[:50]}...")
            
            await asyncio.sleep(0.5)
    
    print("\n📈 Async Timeout Metrics:")
    metrics = cb.get_timeout_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    # Test sync version
    test_timeout_circuit_breaker()
    
    # Test async version
    asyncio.run(test_async_timeout_circuit_breaker())