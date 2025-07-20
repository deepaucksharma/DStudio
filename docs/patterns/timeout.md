# Timeout Pattern

**Protecting systems from indefinite waits**

> *"A system that waits forever is a system that fails forever."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 1: Latency](/part1-axioms/axiom1-latency/) - Bounded response times
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Detecting unresponsive services

**🔧 Solves These Problems**:
- Resource exhaustion from hanging connections
- Poor user experience from indefinite waits
- Cascading failures from blocked threads
- Difficulty detecting slow failures

**🤝 Works Best With**:
- [Circuit Breaker](/patterns/circuit-breaker/) - Timeout triggers circuit opening
- [Retry & Backoff](/patterns/retry-backoff/) - Retry after timeout
- [Bulkhead](/patterns/bulkhead/) - Isolate timeout impacts
</div>

---

## 🎯 Level 1: Intuition

### The Restaurant Analogy

Imagine waiting for your order at a restaurant:
- **No timeout**: Wait indefinitely, get hungrier
- **With timeout**: After 30 minutes, ask for status or leave
- **Smart timeout**: Different waits for coffee (5 min) vs dinner (30 min)

### Basic Implementation

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def call_with_timeout(func, timeout_seconds):
    """Simple timeout wrapper"""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except TimeoutError:
            # Cancel the operation if possible
            future.cancel()
            raise TimeoutError(f"Operation timed out after {timeout_seconds}s")

# Example usage
def slow_operation():
    time.sleep(10)  # Simulates slow operation
    return "Success"

try:
    result = call_with_timeout(slow_operation, timeout_seconds=5)
except TimeoutError as e:
    print(f"Operation failed: {e}")
```

---

## 🏗️ Level 2: Foundation

### Types of Timeouts

| Timeout Type | Use Case | Typical Value |
|--------------|----------|---------------|
| **Connection Timeout** | Establishing connection | 1-5 seconds |
| **Read Timeout** | Waiting for response | 5-30 seconds |
| **Write Timeout** | Sending data | 5-10 seconds |
| **Total Timeout** | End-to-end operation | 30-60 seconds |

### Timeout Hierarchy

```
Application Timeout (60s)
├── HTTP Client Timeout (30s)
│   ├── Connection Timeout (5s)
│   ├── Read Timeout (25s)
│   └── Write Timeout (10s)
└── Database Timeout (20s)
    ├── Connection Pool Timeout (2s)
    └── Query Timeout (18s)
```

### Calculating Appropriate Timeouts

```python
def calculate_timeout(operation_type, percentile_data):
    """
    Calculate timeout based on historical performance
    """
    # Use high percentile (P99) as baseline
    p99_latency = percentile_data['p99']
    
    # Add buffer for variance
    buffer_multiplier = {
        'critical': 1.5,    # 50% buffer
        'normal': 2.0,      # 100% buffer
        'background': 3.0   # 200% buffer
    }
    
    multiplier = buffer_multiplier.get(operation_type, 2.0)
    
    # Calculate timeout
    timeout = p99_latency * multiplier
    
    # Apply bounds
    min_timeout = 1.0  # 1 second minimum
    max_timeout = 300.0  # 5 minutes maximum
    
    return max(min_timeout, min(timeout, max_timeout))
```

---

## 🔧 Level 3: Deep Dive

### Advanced Timeout Patterns

#### Cascading Timeouts
```python
class CascadingTimeout:
    """Ensures child timeouts don't exceed parent"""
    
    def __init__(self, total_timeout):
        self.total_timeout = total_timeout
        self.start_time = time.time()
        
    def get_remaining_timeout(self):
        elapsed = time.time() - self.start_time
        remaining = self.total_timeout - elapsed
        return max(0, remaining)
    
    def create_child_timeout(self, requested_timeout):
        remaining = self.get_remaining_timeout()
        return min(requested_timeout, remaining)

# Usage
async def process_request(timeout=30):
    cascade = CascadingTimeout(timeout)
    
    # Database call gets portion of total timeout
    db_timeout = cascade.create_child_timeout(10)
    data = await query_database(timeout=db_timeout)
    
    # API call gets remaining time
    api_timeout = cascade.get_remaining_timeout()
    result = await call_external_api(data, timeout=api_timeout)
    
    return result
```

#### Adaptive Timeouts
```python
class AdaptiveTimeout:
    """Adjusts timeouts based on observed performance"""
    
    def __init__(self, initial_timeout=5.0):
        self.timeout = initial_timeout
        self.observations = []
        self.adjustment_interval = 100  # Adjust every 100 calls
        
    def record_duration(self, duration, success):
        self.observations.append((duration, success))
        
        if len(self.observations) >= self.adjustment_interval:
            self._adjust_timeout()
            
    def _adjust_timeout(self):
        successful = [(d, s) for d, s in self.observations if s]
        
        if not successful:
            # All failed, increase timeout
            self.timeout *= 1.5
        else:
            # Calculate P95 of successful calls
            durations = sorted([d for d, _ in successful])
            p95_index = int(len(durations) * 0.95)
            p95_duration = durations[p95_index]
            
            # Set timeout to P95 + 50% buffer
            self.timeout = p95_duration * 1.5
            
        # Clear old observations
        self.observations = []
        
    def get_timeout(self):
        return self.timeout
```

### Timeout Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Common Timeout Mistakes</h3>

1. **Timeout Longer Than User Patience**
   ```python
   # BAD: 5 minute timeout for user-facing operation
   response = requests.get(url, timeout=300)
   
   # GOOD: Fail fast for user operations
   response = requests.get(url, timeout=5)
   ```

2. **No Timeout Propagation**
   ```python
   # BAD: Child operation can exceed parent
   def parent_operation(timeout=10):
       # This could take 30 seconds!
       child_operation(timeout=30)
   
   # GOOD: Propagate timeout budget
   def parent_operation(timeout=10):
       start = time.time()
       # ... some work ...
       remaining = timeout - (time.time() - start)
       child_operation(timeout=remaining)
   ```

3. **Same Timeout for All Operations**
   ```python
   # BAD: One size fits all
   TIMEOUT = 30
   
   # GOOD: Operation-specific timeouts
   TIMEOUTS = {
       'health_check': 2,
       'simple_query': 5,
       'complex_report': 60,
       'batch_job': 3600
   }
   ```
</div>

---

## 🚀 Level 4: Expert

### Production Timeout Strategies

#### Hedged Requests
```python
async def hedged_request(primary_func, backup_func, hedge_delay=1.0):
    """
    Send backup request if primary is slow
    """
    # Start primary request
    primary_task = asyncio.create_task(primary_func())
    
    # Wait for hedge delay
    try:
        result = await asyncio.wait_for(primary_task, timeout=hedge_delay)
        return result
    except asyncio.TimeoutError:
        # Primary is slow, start backup
        backup_task = asyncio.create_task(backup_func())
        
        # Race both requests
        done, pending = await asyncio.wait(
            [primary_task, backup_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel the slower one
        for task in pending:
            task.cancel()
            
        # Return the winner
        return done.pop().result()
```

#### Timeout with Partial Results
```python
class PartialResultTimeout:
    """Return partial results when timeout occurs"""
    
    async def scatter_gather(self, requests, timeout):
        tasks = [
            asyncio.create_task(self.process_request(req))
            for req in requests
        ]
        
        results = []
        errors = []
        
        try:
            # Wait for all with timeout
            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )
            
            results = [task.result() for task in done if not task.exception()]
            errors = [task.exception() for task in done if task.exception()]
            
        except asyncio.TimeoutError:
            # Timeout hit, gather partial results
            for task in tasks:
                if task.done() and not task.exception():
                    results.append(task.result())
                else:
                    task.cancel()
                    errors.append(TimeoutError("Partial timeout"))
        
        return {
            'results': results,
            'errors': errors,
            'completion_rate': len(results) / len(requests)
        }
```

### Real-World Case Study: Netflix Timeout Strategy

```python
class NetflixTimeoutStrategy:
    """
    Netflix's approach to timeouts in microservices
    """
    
    def __init__(self):
        self.timeouts = {
            'user_request': 1000,      # 1 second total
            'service_call': 300,       # 300ms per service
            'cache_lookup': 50,        # 50ms for cache
            'fallback': 100           # 100ms for fallback
        }
        
    async def get_recommendations(self, user_id):
        timeout_budget = TimeoutBudget(self.timeouts['user_request'])
        
        # Try primary recommendation service
        try:
            primary_timeout = timeout_budget.allocate(
                self.timeouts['service_call']
            )
            return await self.call_recommendation_service(
                user_id, 
                timeout=primary_timeout
            )
        except TimeoutError:
            # Try cache with reduced timeout
            cache_timeout = timeout_budget.allocate(
                self.timeouts['cache_lookup']
            )
            cached = await self.get_cached_recommendations(
                user_id,
                timeout=cache_timeout
            )
            if cached:
                return cached
                
            # Last resort: generic recommendations
            fallback_timeout = timeout_budget.allocate(
                self.timeouts['fallback']
            )
            return await self.get_generic_recommendations(
                timeout=fallback_timeout
            )
```

---

## 🎯 Level 5: Mastery

### Theoretical Optimal Timeouts

```python
class OptimalTimeoutCalculator:
    """
    Calculate theoretically optimal timeouts based on:
    - Cost of waiting
    - Cost of retry
    - Probability of success over time
    """
    
    def calculate_optimal_timeout(self, 
                                 success_probability_func,
                                 wait_cost_per_second,
                                 retry_cost):
        """
        Find timeout that minimizes total cost
        """
        def expected_cost(timeout):
            # Probability of success within timeout
            p_success = success_probability_func(timeout)
            
            # Expected wait time
            expected_wait = self.calculate_expected_wait(
                success_probability_func, 
                timeout
            )
            
            # Total cost calculation
            wait_cost = expected_wait * wait_cost_per_second
            retry_probability = 1 - p_success
            expected_retry_cost = retry_probability * retry_cost
            
            return wait_cost + expected_retry_cost
        
        # Find minimum using gradient descent
        timeout = 1.0  # Start with 1 second
        learning_rate = 0.1
        
        for _ in range(100):
            gradient = self.numerical_gradient(expected_cost, timeout)
            timeout -= learning_rate * gradient
            timeout = max(0.1, timeout)  # Keep positive
            
        return timeout
```

### Future Directions

1. **ML-Powered Timeout Prediction**: Using historical data to predict optimal timeouts
2. **Quantum-Inspired Timeouts**: Superposition of multiple timeout strategies
3. **Timeout Contracts**: SLA-based automatic timeout negotiation
4. **Adaptive Circuit Breaking**: Timeouts that trigger circuit breakers intelligently

---

## 📋 Quick Reference

### Decision Framework

| If... | Then Use... | Timeout Value |
|-------|-------------|---------------|
| User-facing request | Aggressive timeout | 1-5 seconds |
| Background job | Relaxed timeout | Minutes to hours |
| Health check | Very short timeout | 100-500ms |
| Database query | Statement timeout | 5-30 seconds |
| External API | Conservative timeout | 10-30 seconds |

### Implementation Checklist

- [ ] Set timeouts at all network boundaries
- [ ] Propagate timeout budgets through call chains
- [ ] Monitor timeout rates and adjust accordingly
- [ ] Implement fallback behavior for timeouts
- [ ] Test timeout behavior under load
- [ ] Document timeout values and rationale

---

<div class="navigation-footer">
<div class="pattern-relationships">
<h3>🔗 Related Patterns & Concepts</h3>

**🤝 Complementary Patterns**:
- [Circuit Breaker](/patterns/circuit-breaker/) - Timeouts trigger circuit opening
- [Retry & Backoff](/patterns/retry-backoff/) - Retry after timeout
- [Bulkhead](/patterns/bulkhead/) - Isolate timeout impacts

**🧠 Foundational Concepts**:
- [Axiom 1: Latency](/part1-axioms/axiom1-latency/) - Why timeouts matter
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Timeout as failure detection
</div>
</div>

---

*"The absence of a timeout is the presence of a bug."*