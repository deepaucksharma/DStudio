#!/usr/bin/env python3
"""
State Transition Circuit Breaker
Circuit breaker के states और transitions का detailed implementation

यह code specifically state machine और transitions पर focus करता है
Production systems में proper state management बहुत important होता है
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


class CircuitState(Enum):
    """Circuit breaker के states"""
    CLOSED = "CLOSED"        # Normal operation - सब कुछ ठीक है
    OPEN = "OPEN"            # Circuit open - सभी requests fail
    HALF_OPEN = "HALF_OPEN"  # Testing phase - limited requests allowed


@dataclass
class StateTransition:
    """State transition की information store करता है"""
    from_state: CircuitState
    to_state: CircuitState
    timestamp: datetime
    reason: str
    metrics_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Failure count threshold
    failure_rate_threshold: float = 50.0  # Failure rate percentage
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout_duration: int = 60          # Seconds to wait before half-open
    min_throughput: int = 10            # Minimum requests needed for calculation
    slow_call_threshold: float = 1.0    # Seconds - इससे slow calls को failure माना जाएगा
    max_half_open_calls: int = 5        # Half-open state में maximum calls


class StateTransitionCircuitBreaker:
    """
    Advanced Circuit Breaker with detailed state management
    यह implementation state transitions को track करती है
    और detailed analytics provide करती है
    """
    
    def __init__(self, name: str, config: CircuitConfig = None):
        """
        Args:
            name: Circuit breaker का unique name (monitoring के लिए)
            config: Configuration object
        """
        self.name = name
        self.config = config or CircuitConfig()
        
        # Current state
        self.state = CircuitState.CLOSED
        self.state_entered_time = datetime.now()
        
        # Metrics tracking
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.slow_calls = 0
        self.half_open_calls = 0
        self.half_open_successes = 0
        
        # State transition history
        self.transition_history: List[StateTransition] = []
        self.last_failure_time: Optional[datetime] = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Event callbacks
        self.on_state_transition: Optional[Callable[[StateTransition], None]] = None
        self.on_call_success: Optional[Callable[[float], None]] = None  # duration
        self.on_call_failure: Optional[Callable[[Exception, float], None]] = None
        
        print(f"🔧 Circuit Breaker '{name}' initialized")
        print(f"   - Failure threshold: {self.config.failure_threshold}")
        print(f"   - Failure rate threshold: {self.config.failure_rate_threshold}%")
        print(f"   - Timeout duration: {self.config.timeout_duration}s")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Protected function call with state management"""
        with self._lock:
            # State check और transitions handle करते हैं
            self._handle_state_transitions()
            
            # Current state के according action लेते हैं
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit '{self.name}' is OPEN. "
                    f"Last failure: {self.last_failure_time}"
                )
            
            if self.state == CircuitState.HALF_OPEN:
                # Half-open state में call limit check करते हैं
                if self.half_open_calls >= self.config.max_half_open_calls:
                    raise CircuitBreakerOpenError(
                        f"Circuit '{self.name}' is HALF_OPEN but call limit exceeded"
                    )
            
            # Function execute करते हैं
            return self._execute_protected_call(func, *args, **kwargs)
    
    def _execute_protected_call(self, func: Callable, *args, **kwargs) -> Any:
        """Protected function execution with metrics tracking"""
        start_time = time.time()
        
        try:
            # If half-open, increment call count
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Check if it's a slow call
            if execution_time > self.config.slow_call_threshold:
                self._handle_slow_call(execution_time)
            else:
                self._handle_successful_call(execution_time)
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_failed_call(e, execution_time)
            raise e
    
    def _handle_successful_call(self, execution_time: float):
        """Successful call handling और metrics update"""
        self.total_calls += 1
        self.successful_calls += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            
            # Check if enough successes to close circuit
            if self.half_open_successes >= self.config.success_threshold:
                self._transition_to_closed("Sufficient successful calls in half-open")
        
        # Success callback trigger करते हैं
        if self.on_call_success:
            self.on_call_success(execution_time)
        
        print(f"✅ '{self.name}' - Successful call ({execution_time:.3f}s)")
    
    def _handle_failed_call(self, error: Exception, execution_time: float):
        """Failed call handling और state decisions"""
        self.total_calls += 1
        self.failed_calls += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Half-open में failure का मतलब immediate open
            self._transition_to_open("Failure in half-open state")
        else:
            # Check if failure threshold reached
            self._check_failure_conditions()
        
        # Failure callback trigger करते हैं
        if self.on_call_failure:
            self.on_call_failure(error, execution_time)
        
        print(f"❌ '{self.name}' - Failed call: {str(error)[:50]} ({execution_time:.3f}s)")
    
    def _handle_slow_call(self, execution_time: float):
        """Slow call handling - slow calls को failures की तरह treat करते हैं"""
        self.total_calls += 1
        self.slow_calls += 1
        
        print(f"🐌 '{self.name}' - Slow call detected ({execution_time:.3f}s)")
        
        # Slow calls को failures की तरह handle करते हैं
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open("Slow call in half-open state")
        else:
            self._check_failure_conditions()
    
    def _check_failure_conditions(self):
        """Check करता है कि circuit open करना चाहिए या नहीं"""
        if self.total_calls < self.config.min_throughput:
            return  # Not enough data
        
        # Calculate current failure rate
        total_failures = self.failed_calls + self.slow_calls
        failure_rate = (total_failures / self.total_calls) * 100
        
        # Check conditions for opening circuit
        if (total_failures >= self.config.failure_threshold or 
            failure_rate >= self.config.failure_rate_threshold):
            
            reason = f"Failure rate: {failure_rate:.1f}%, Total failures: {total_failures}"
            self._transition_to_open(reason)
    
    def _handle_state_transitions(self):
        """Automatic state transitions handle करता है"""
        if self.state == CircuitState.OPEN:
            # Check if timeout period has elapsed
            time_in_open = datetime.now() - self.state_entered_time
            if time_in_open.total_seconds() >= self.config.timeout_duration:
                self._transition_to_half_open("Timeout period elapsed")
    
    def _transition_to_open(self, reason: str):
        """Circuit को OPEN state में transition करता है"""
        if self.state == CircuitState.OPEN:
            return  # Already open
        
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_entered_time = datetime.now()
        
        # Reset half-open counters
        self.half_open_calls = 0
        self.half_open_successes = 0
        
        # Record transition
        transition = StateTransition(
            from_state=old_state,
            to_state=CircuitState.OPEN,
            timestamp=datetime.now(),
            reason=reason,
            metrics_snapshot=self._get_metrics_snapshot()
        )
        
        self._record_transition(transition)
        print(f"🔴 '{self.name}' - Circuit OPENED: {reason}")
    
    def _transition_to_half_open(self, reason: str):
        """Circuit को HALF_OPEN state में transition करता है"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_entered_time = datetime.now()
        
        # Reset half-open counters
        self.half_open_calls = 0
        self.half_open_successes = 0
        
        # Record transition
        transition = StateTransition(
            from_state=old_state,
            to_state=CircuitState.HALF_OPEN,
            timestamp=datetime.now(),
            reason=reason,
            metrics_snapshot=self._get_metrics_snapshot()
        )
        
        self._record_transition(transition)
        print(f"🟡 '{self.name}' - Circuit HALF_OPEN: {reason}")
    
    def _transition_to_closed(self, reason: str):
        """Circuit को CLOSED state में transition करता है"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_entered_time = datetime.now()
        
        # Reset metrics for fresh start
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.slow_calls = 0
        self.half_open_calls = 0
        self.half_open_successes = 0
        
        # Record transition
        transition = StateTransition(
            from_state=old_state,
            to_state=CircuitState.CLOSED,
            timestamp=datetime.now(),
            reason=reason,
            metrics_snapshot=self._get_metrics_snapshot()
        )
        
        self._record_transition(transition)
        print(f"✅ '{self.name}' - Circuit CLOSED: {reason}")
    
    def _record_transition(self, transition: StateTransition):
        """State transition को history में record करता है"""
        self.transition_history.append(transition)
        
        # Event callback trigger करते हैं
        if self.on_state_transition:
            self.on_state_transition(transition)
    
    def _get_metrics_snapshot(self) -> Dict[str, Any]:
        """Current metrics का snapshot return करता है"""
        failure_rate = 0.0
        if self.total_calls > 0:
            total_failures = self.failed_calls + self.slow_calls
            failure_rate = (total_failures / self.total_calls) * 100
        
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "slow_calls": self.slow_calls,
            "failure_rate": round(failure_rate, 2),
            "state_duration": (datetime.now() - self.state_entered_time).total_seconds()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Comprehensive metrics return करता है"""
        with self._lock:
            metrics = self._get_metrics_snapshot()
            metrics.update({
                "name": self.name,
                "current_state": self.state.value,
                "state_entered_time": self.state_entered_time.isoformat(),
                "total_transitions": len(self.transition_history),
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "half_open_calls": self.half_open_calls,
                "half_open_successes": self.half_open_successes
            })
            return metrics
    
    def get_transition_history(self) -> List[Dict[str, Any]]:
        """State transition history return करता है"""
        return [
            {
                "from_state": t.from_state.value,
                "to_state": t.to_state.value,
                "timestamp": t.timestamp.isoformat(),
                "reason": t.reason,
                "metrics": t.metrics_snapshot
            }
            for t in self.transition_history
        ]
    
    def force_state(self, new_state: CircuitState, reason: str = "Manual override"):
        """Manually circuit state change करता है (testing के लिए)"""
        with self._lock:
            if new_state == CircuitState.OPEN:
                self._transition_to_open(reason)
            elif new_state == CircuitState.HALF_OPEN:
                self._transition_to_half_open(reason)
            elif new_state == CircuitState.CLOSED:
                self._transition_to_closed(reason)
    
    def reset_metrics(self):
        """Metrics reset करता है"""
        with self._lock:
            self.total_calls = 0
            self.successful_calls = 0
            self.failed_calls = 0
            self.slow_calls = 0
            self.half_open_calls = 0
            self.half_open_successes = 0
            print(f"📊 '{self.name}' - Metrics reset")


class CircuitBreakerOpenError(Exception):
    """Circuit breaker open होने पर throw होता है"""
    pass


# Example usage और comprehensive testing
def flaky_database_service(success_rate: float = 0.3, slow_rate: float = 0.2):
    """
    Database service simulation
    यह service randomly fail होती है और कभी कभी slow भी होती है
    """
    import random
    
    # Random delay simulation
    if random.random() < slow_rate:
        time.sleep(2.0)  # Slow call
    else:
        time.sleep(random.uniform(0.1, 0.3))  # Normal call
    
    if random.random() > success_rate:
        raise Exception("Database connection timeout")
    
    return f"Data retrieved successfully at {datetime.now().strftime('%H:%M:%S')}"


def test_state_transitions():
    """Comprehensive state transition testing"""
    print("🧪 Testing State Transition Circuit Breaker")
    print("=" * 60)
    
    # Custom configuration
    config = CircuitConfig(
        failure_threshold=3,
        failure_rate_threshold=60.0,
        success_threshold=2,
        timeout_duration=5,
        min_throughput=5,
        slow_call_threshold=1.5,
        max_half_open_calls=3
    )
    
    # Circuit breaker with event listeners
    cb = StateTransitionCircuitBreaker("database-service", config)
    
    # Event listeners setup
    def on_transition(transition: StateTransition):
        print(f"🔄 STATE TRANSITION: {transition.from_state.value} → {transition.to_state.value}")
        print(f"   Reason: {transition.reason}")
        print(f"   Metrics: {transition.metrics_snapshot}")
    
    def on_success(duration: float):
        if duration > 1.0:
            print(f"⚠️  Slow success: {duration:.3f}s")
    
    def on_failure(error: Exception, duration: float):
        print(f"💥 Failure callback: {str(error)[:30]} ({duration:.3f}s)")
    
    cb.on_state_transition = on_transition
    cb.on_call_success = on_success
    cb.on_call_failure = on_failure
    
    # Phase 1: Generate enough requests to trigger opening
    print("\n📊 Phase 1: Triggering circuit opening")
    print("-" * 40)
    
    for i in range(15):
        try:
            result = cb.call(flaky_database_service, success_rate=0.2, slow_rate=0.3)
            print(f"✅ Request {i+1}: {result[:30]}...")
        except CircuitBreakerOpenError as e:
            print(f"🚫 Request {i+1}: {str(e)[:50]}...")
        except Exception as e:
            print(f"❌ Request {i+1}: {str(e)[:30]}...")
        
        time.sleep(0.5)
    
    # Current metrics
    print("\n📈 Current Metrics:")
    print(json.dumps(cb.get_metrics(), indent=2, default=str))
    
    # Phase 2: Wait for half-open transition
    print(f"\n⏳ Phase 2: Waiting {config.timeout_duration} seconds for half-open...")
    time.sleep(config.timeout_duration + 1)
    
    # Phase 3: Test half-open behavior
    print("\n📊 Phase 3: Testing half-open behavior")
    print("-" * 40)
    
    for i in range(8):
        try:
            result = cb.call(flaky_database_service, success_rate=0.8, slow_rate=0.1)
            print(f"✅ Recovery {i+1}: {result[:30]}...")
        except CircuitBreakerOpenError as e:
            print(f"🚫 Recovery {i+1}: {str(e)[:50]}...")
        except Exception as e:
            print(f"❌ Recovery {i+1}: {str(e)[:30]}...")
        
        time.sleep(1)
    
    # Phase 4: Manual state transitions
    print("\n📊 Phase 4: Manual state transitions")
    print("-" * 40)
    
    print("Forcing circuit to OPEN...")
    cb.force_state(CircuitState.OPEN, "Manual test")
    time.sleep(2)
    
    print("Forcing circuit to CLOSED...")
    cb.force_state(CircuitState.CLOSED, "Recovery test")
    time.sleep(1)
    
    # Final state and transition history
    print("\n📈 Final Metrics:")
    print(json.dumps(cb.get_metrics(), indent=2, default=str))
    
    print("\n📚 Transition History:")
    history = cb.get_transition_history()
    for i, transition in enumerate(history):
        print(f"{i+1}. {transition['timestamp']}: "
              f"{transition['from_state']} → {transition['to_state']}")
        print(f"   Reason: {transition['reason']}")


if __name__ == "__main__":
    test_state_transitions()