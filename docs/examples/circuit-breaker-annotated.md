---
title: Circuit Breaker - Annotated Implementation
description: Step-by-step annotated code example of a circuit breaker
tags:
  - pattern
  - resilience
  - code-example
  - intermediate
---

# Circuit Breaker: Annotated Implementation

This page demonstrates MkDocs Material's code annotation feature with a complete circuit breaker implementation.

## Python Implementation with Annotations

```python
import time
import threading
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # (1)!
    OPEN = "open"          # (2)!
    HALF_OPEN = "half_open" # (3)!

class CircuitBreaker:
    """
    A thread-safe circuit breaker implementation
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,    # (4)!
        recovery_timeout: int = 60,    # (5)!
        expected_exception: type = Exception,
        name: Optional[str] = None
    ):
        self.name = name or "CircuitBreaker"
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._lock = threading.RLock()  # (6)!
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():  # (7)!
                    self._state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)  # (8)!
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        return (
            self._last_failure_time and 
            datetime.now() >= self._last_failure_time + timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self._failure_count = 0  # (9)!
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            
            if self._failure_count >= self.failure_threshold:  # (10)!
                self._state = CircuitState.OPEN

# Usage Example
@CircuitBreaker(failure_threshold=3, recovery_timeout=30)  # (11)!
def risky_api_call(url: str) -> dict:
    """Make an API call that might fail"""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

# Advanced usage with fallback
def call_with_fallback(url: str) -> dict:
    try:
        return risky_api_call(url)  # (12)!
    except Exception as e:
        # Return cached or default data
        return {"status": "degraded", "cached": True}
```

1. **CLOSED State**: Normal operation - all requests pass through to the service. The circuit monitors for failures.

2. **OPEN State**: Circuit has tripped - all requests fail immediately without calling the service. This prevents overloading a failing service.

3. **HALF_OPEN State**: Recovery testing - allows a limited number of requests through to test if the service has recovered.

4. **Failure Threshold**: Number of consecutive failures before the circuit opens. Lower values make the circuit more sensitive.

5. **Recovery Timeout**: Time in seconds to wait before attempting recovery. Should be long enough for the service to recover.

6. **Thread Safety**: RLock (reentrant lock) ensures thread-safe state transitions in concurrent environments.

7. **Recovery Check**: After the timeout period, the circuit moves to HALF_OPEN to test if the service has recovered.

8. **Function Execution**: The actual service call happens here. If it succeeds, we reset the failure count.

9. **Success Handling**: Reset failure count on success. If we were in HALF_OPEN state, close the circuit.

10. **Failure Threshold Check**: Open the circuit if we've hit the failure threshold.

11. **Decorator Usage**: Configure the circuit breaker with custom thresholds. This creates a reusable protected function.

12. **Fallback Pattern**: Combine circuit breaker with fallback for graceful degradation.

## Go Implementation with Annotations

```go
package circuitbreaker

import (
    "errors"
    "sync"
    "time"
)

type State int

const (
    StateClosed State = iota  // (1)!
    StateOpen                 // (2)!
    StateHalfOpen            // (3)!
)

type CircuitBreaker struct {
    name            string
    maxFailures     uint      // (4)!
    resetTimeout    time.Duration // (5)!
    
    mu              sync.Mutex    // (6)!
    state           State
    failures        uint
    lastFailureTime time.Time
    counts          Counts        // (7)!
}

type Counts struct {
    Requests             uint
    TotalSuccesses       uint
    TotalFailures        uint
    ConsecutiveSuccesses uint
    ConsecutiveFailures  uint
}

func NewCircuitBreaker(name string, maxFailures uint, resetTimeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        name:         name,
        maxFailures:  maxFailures,
        resetTimeout: resetTimeout,
        state:        StateClosed,
    }
}

func (cb *CircuitBreaker) Execute(fn func() (interface{}, error)) (interface{}, error) {
    if err := cb.beforeRequest(); err != nil {  // (8)!
        return nil, err
    }
    
    result, err := fn()  // (9)!
    cb.afterRequest(err == nil)
    return result, err
}

func (cb *CircuitBreaker) beforeRequest() error {
    cb.mu.Lock()
    defer cb.mu.Unlock()
    
    switch cb.state {
    case StateOpen:
        if time.Since(cb.lastFailureTime) > cb.resetTimeout {  // (10)!
            cb.state = StateHalfOpen
            cb.counts = Counts{}  // (11)!
        } else {
            return errors.New("circuit breaker is open")
        }
    }
    
    cb.counts.Requests++
    return nil
}

func (cb *CircuitBreaker) afterRequest(success bool) {
    cb.mu.Lock()
    defer cb.mu.Unlock()
    
    if success {
        cb.onSuccess()
    } else {
        cb.onFailure()
    }
}

func (cb *CircuitBreaker) onSuccess() {
    cb.counts.TotalSuccesses++
    cb.counts.ConsecutiveSuccesses++
    cb.counts.ConsecutiveFailures = 0
    
    if cb.state == StateHalfOpen {  // (12)!
        cb.state = StateClosed
    }
}

func (cb *CircuitBreaker) onFailure() {
    cb.counts.TotalFailures++
    cb.counts.ConsecutiveFailures++
    cb.counts.ConsecutiveSuccesses = 0
    cb.lastFailureTime = time.Now()
    
    if cb.counts.ConsecutiveFailures >= cb.maxFailures {  // (13)!
        cb.state = StateOpen
    }
}

// Usage example
func main() {
    cb := NewCircuitBreaker("payment-service", 5, 30*time.Second)  // (14)!
    
    result, err := cb.Execute(func() (interface{}, error) {
        // Your service call here
        return callPaymentAPI()
    })
    
    if err != nil {
        // Handle with fallback
        return handleWithFallback()
    }
}
```

1. **State Enumeration**: Using iota for clean state definition. StateClosed = 0, StateOpen = 1, StateHalfOpen = 2.

2. **StateOpen**: Prevents all requests from reaching the failing service.

3. **StateHalfOpen**: Test state to check if service has recovered.

4. **Max Failures**: Configurable threshold for opening the circuit.

5. **Reset Timeout**: Duration type for type-safe time handling.

6. **Mutex**: Ensures thread-safe access to circuit breaker state.

7. **Counts Structure**: Detailed metrics for monitoring and debugging.

8. **Pre-Request Check**: Validates if request should proceed based on current state.

9. **Function Execution**: The actual service call wrapped in circuit breaker logic.

10. **Timeout Check**: Time-based recovery mechanism using Go's time package.

11. **Reset Counts**: Clear statistics when entering half-open state.

12. **Recovery Success**: If test request succeeds, close the circuit.

13. **Failure Threshold**: Open circuit when consecutive failures exceed threshold.

14. **Initialization**: Create circuit breaker with name for logging and monitoring.

## Key Design Decisions

!!! info "Thread Safety"
    Both implementations use locks to ensure thread-safe state transitions. This is critical in production where multiple goroutines/threads may be using the same circuit breaker.

!!! warning "Error Types"
    The Python version allows specifying which exceptions trigger the circuit breaker. The Go version treats all errors equally. Choose based on your error handling needs.

!!! tip "Monitoring Integration"
    Both implementations provide hooks for metrics collection. In production, export these to Prometheus, DataDog, or your monitoring system of choice.

## Testing Strategies

```python
# Test circuit breaker state transitions
def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    failing_func = lambda: (_ for _ in ()).throw(Exception("Service down"))
    
    # First failure
    with pytest.raises(Exception):
        cb.call(failing_func)
    
    # Second failure - should open circuit
    with pytest.raises(Exception):
        cb.call(failing_func)
    
    # Third call - should fail fast
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        cb.call(failing_func)
        
    # Wait for recovery timeout
    time.sleep(1.1)
    
    # Should now be in HALF_OPEN state
    # Next call will determine if circuit closes or reopens
```

## Production Checklist

- [ ] Configure appropriate thresholds based on service SLAs
- [ ] Implement comprehensive fallback strategies
- [ ] Add metrics and alerting for circuit state changes
- [ ] Test under various failure scenarios
- [ ] Document expected behavior for operations team
- [ ] Consider bulkheading - separate circuit breakers per dependency
- [ ] Implement request volume thresholds to prevent premature opening
- [ ] Add jitter to recovery timeouts to prevent thundering herd