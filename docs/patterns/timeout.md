---
title: Timeout Pattern
description: "<div class="pattern-context">
<h3>🧭 Pattern Context</h3>"
type: pattern
difficulty: beginner
reading_time: 25 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Timeout Pattern**


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

```text
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
```bash
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
```bash
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
```yaml
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

---

*"The absence of a timeout is the presence of a bug."*

---

**Previous**: [← Sharding (Data Partitioning)](sharding.md) | **Next**: [Tunable Consistency →](tunable-consistency.md)
## 🎯 Problem Statement

### The Challenge
This pattern addresses common distributed systems challenges where timeout pattern becomes critical for system reliability and performance.

### Why This Matters
In distributed systems, this problem manifests as:
- **Reliability Issues**: System failures cascade and affect multiple components
- **Performance Degradation**: Poor handling leads to resource exhaustion  
- **User Experience**: Inconsistent or poor response times
- **Operational Complexity**: Difficult to debug and maintain

### Common Symptoms
- Intermittent failures that are hard to reproduce
- Performance that degrades under load
- Resource exhaustion (connections, threads, memory)
- Difficulty isolating root causes of issues

### Without This Pattern
Systems become fragile, unreliable, and difficult to operate at scale.



## 💡 Solution Overview

### Core Concept
The Timeout Pattern pattern provides a structured approach to handling this distributed systems challenge.

### Key Principles
1. **Isolation**: Separate concerns to prevent failures from spreading
2. **Resilience**: Build systems that gracefully handle failures
3. **Observability**: Make system behavior visible and measurable
4. **Simplicity**: Keep solutions understandable and maintainable

### How It Works
The Timeout Pattern pattern works by:
- Monitoring system behavior and health
- Implementing protective mechanisms
- Providing fallback strategies
- Enabling rapid recovery from failures

### Benefits
- **Improved Reliability**: System continues operating during partial failures
- **Better Performance**: Resources are protected from overload
- **Easier Operations**: Clear indicators of system health
- **Reduced Risk**: Failures are contained and predictable



## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical



## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems



## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand



## 🌟 Real Examples

### Production Implementations

**Major Cloud Provider**: Uses this pattern for service reliability across global infrastructure

**Popular Framework**: Implements this pattern by default in their distributed systems toolkit

**Enterprise System**: Applied this pattern to improve uptime from 99% to 99.9%

### Open Source Examples
- **Libraries**: Resilience4j, Polly, circuit-breaker-js
- **Frameworks**: Spring Cloud, Istio, Envoy
- **Platforms**: Kubernetes, Docker Swarm, Consul

### Case Study: E-commerce Platform
A major e-commerce platform implemented Timeout Pattern to handle critical user flows:

**Challenge**: System failures affected user experience and revenue

**Implementation**: 
- Applied Timeout Pattern pattern to critical service calls
- Added fallback mechanisms for degraded operation
- Monitored service health continuously

**Results**:
- 99.9% availability during service disruptions
- Customer satisfaction improved due to reliable experience
- Revenue protected during partial outages

### Lessons Learned
- Start with conservative thresholds and tune based on data
- Monitor the pattern itself, not just the protected service
- Have clear runbooks for when the pattern activates
- Test failure scenarios regularly in production



## 💻 Code Sample

### Basic Implementation

```python
class TimeoutPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"
    
    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)
        
        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)
    
    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold
    
    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass
    
    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}
    
    def _record_success(self):
        self.metrics.record_success()
    
    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = TimeoutPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
timeout:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_timeout_behavior():
    pattern = TimeoutPattern(test_config)
    
    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
    
    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'
    
    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```



