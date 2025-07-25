---
title: "Axiom 3 Exercises: Master Failure Engineering"
description: "Hands-on labs, challenge problems, and real-world scenarios to build your failure handling expertise. Learn to create systems that thrive despite failures."
type: axiom
difficulty: intermediate
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 3](index.md) → **Partial Failure Exercises**

# Partial Failure Exercises

**Master the art of building resilient systems through hands-on failure engineering**

---

## Hands-On Labs

### Lab 1: Chaos Engineering Workshop

**Build and test your own chaos engineering toolkit**

#### Exercise 1.1: Network Chaos Simulator

```python
import random
import time
import asyncio
from enum import Enum
from typing import Optional, Dict, Any

class FailureMode(Enum):
    NONE = "none"
    LATENCY = "latency"
    PACKET_LOSS = "packet_loss"
    PARTITION = "partition"
    CORRUPTION = "corruption"

class ChaosNetwork:
    def __init__(self):
        self.failure_modes: Dict[str, FailureMode] = {}
        self.latency_ms = 50
        self.packet_loss_rate = 0.1
        self.corruption_rate = 0.01
        
    def inject_failure(self, service: str, mode: FailureMode):
        """Inject a specific failure mode for a service"""
        self.failure_modes[service] = mode
        print(f"💥 Injected {mode.value} failure for {service}")
        
    async def send_request(self, from_service: str, to_service: str, data: Any) -> Optional[Any]:
        """Simulate network request with potential failures"""
        failure_mode = self.failure_modes.get(to_service, FailureMode.NONE)
        
        if failure_mode == FailureMode.PARTITION:
            raise ConnectionError(f"Network partition: Cannot reach {to_service}")
            
        if failure_mode == FailureMode.PACKET_LOSS:
            if random.random() < self.packet_loss_rate:
                raise TimeoutError(f"Request to {to_service} timed out")
                
        if failure_mode == FailureMode.LATENCY:
            delay = self.latency_ms + random.randint(0, 100)
            await asyncio.sleep(delay / 1000)
            
        if failure_mode == FailureMode.CORRUPTION:
            if random.random() < self.corruption_rate:
                return {"error": "corrupted_data", "original": data}
                
# Simulate normal processing time
        await asyncio.sleep(0.01)
        return {"response": f"OK from {to_service}", "data": data}

# Exercise: Implement service resilience
class ResilientService:
    def __init__(self, name: str, network: ChaosNetwork):
        self.name = name
        self.network = network
        self.circuit_breaker_state = "closed"
        self.failure_count = 0
        self.success_count = 0
        
    async def call_service(self, target: str, data: Any, timeout_ms: int = 1000):
        """TODO: Implement resilient service call with:
        1. Circuit breaker pattern
        2. Retry with exponential backoff
        3. Timeout handling
        4. Fallback mechanism
        """
# Your implementation here
        pass

# Test scenarios
async def chaos_test_suite():
    network = ChaosNetwork()
    service_a = ResilientService("ServiceA", network)
    service_b = ResilientService("ServiceB", network)
    
# Scenario 1: Normal operation
    print("\n📊 Scenario 1: Normal operation")
    result = await service_a.call_service("ServiceB", {"test": 1})
    print(f"Result: {result}")
    
# Scenario 2: High latency
    print("\n📊 Scenario 2: High latency")
    network.inject_failure("ServiceB", FailureMode.LATENCY)
    network.latency_ms = 2000
    result = await service_a.call_service("ServiceB", {"test": 2})
    print(f"Result: {result}")
    
# Scenario 3: Network partition
    print("\n📊 Scenario 3: Network partition")
    network.inject_failure("ServiceB", FailureMode.PARTITION)
    result = await service_a.call_service("ServiceB", {"test": 3})
    print(f"Result: {result}")

# Run: asyncio.run(chaos_test_suite())
```

#### Exercise 1.2: Failure Injection Framework

```python
class FailureInjector:
    """Build a comprehensive failure injection framework"""
    
    def __init__(self):
        self.rules = []
        self.metrics = {
            'injections': 0,
            'affected_requests': 0,
            'recovery_times': []
        }
        
    def add_rule(self, rule):
        """Add a failure injection rule"""
        self.rules.append(rule)
        
    def should_fail(self, context):
        """Determine if request should fail based on rules"""
        for rule in self.rules:
            if rule.matches(context) and rule.should_trigger():
                self.metrics['injections'] += 1
                return rule.failure_type
        return None

# Exercise: Implement these failure rules
class PercentageRule:
    """Fail X% of requests"""
    def __init__(self, percentage, failure_type):
        self.percentage = percentage
        self.failure_type = failure_type
        
    def matches(self, context):
        return True  # Applies to all requests
        
    def should_trigger(self):
# TODO: Implement percentage-based triggering
        pass

class TimeWindowRule:
    """Fail during specific time windows"""
    def __init__(self, start_time, duration_seconds, failure_type):
        self.start_time = start_time
        self.duration = duration_seconds
        self.failure_type = failure_type
        
    def matches(self, context):
# TODO: Check if current time is within window
        pass
        
    def should_trigger(self):
        return True

class PatternRule:
    """Fail requests matching specific patterns"""
    def __init__(self, pattern, failure_type):
        self.pattern = pattern
        self.failure_type = failure_type
        
    def matches(self, context):
# TODO: Match request against pattern
        pass
```

---

### Lab 2: Advanced Circuit Breaker Implementation

**Build a production-ready circuit breaker with monitoring**

```python
import time
from enum import Enum
from collections import deque
from datetime import datetime, timedelta
import threading

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = threading.Lock()
        
# Metrics
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0,
            'state_transitions': []
        }
        
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        with self._lock:
            self.metrics['total_calls'] += 1
            
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
                else:
                    self.metrics['rejected_calls'] += 1
                    raise Exception("Circuit breaker is OPEN")
            
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
            
    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.metrics['successful_calls'] += 1
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.CLOSED)
                
    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.metrics['failed_calls'] += 1
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                
    def _should_attempt_reset(self):
        """Check if we should try to recover"""
        return (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.recovery_timeout)
                
    def _transition_to(self, new_state: CircuitState):
        """Transition to new state"""
        old_state = self.state
        self.state = new_state
        self.metrics['state_transitions'].append({
            'from': old_state.value,
            'to': new_state.value,
            'timestamp': datetime.now().isoformat()
        })
        print(f"🔄 Circuit breaker: {old_state.value} → {new_state.value}")

# Exercise: Extend with these features
class AdvancedCircuitBreaker(CircuitBreaker):
    """TODO: Implement these advanced features:
    1. Sliding window for failure rate calculation
    2. Different thresholds for different error types  
    3. Gradual recovery (slowly increase traffic in half-open)
    4. Metrics dashboard integration
    5. Fallback function support
    """
    pass

# Test harness
def test_circuit_breaker():
# Flaky service simulation
    failure_count = 0
    
    def flaky_service(fail_times=0):
        nonlocal failure_count
        if failure_count < fail_times:
            failure_count += 1
            raise Exception("Service unavailable")
        return "Success!"
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
# Test sequence
    print("Testing circuit breaker behavior...")
    
# Should work initially
    for i in range(2):
        try:
            result = cb.call(flaky_service, 0)
            print(f"Call {i+1}: {result}")
        except Exception as e:
            print(f"Call {i+1}: Failed - {e}")
    
# Trigger failures
    for i in range(5):
        try:
            result = cb.call(flaky_service, 10)
            print(f"Call {i+3}: {result}")
        except Exception as e:
            print(f"Call {i+3}: Failed - {e}")
    
    print(f"\nMetrics: {cb.metrics}")
```

---

### Lab 3: Distributed Timeout Coordination

**Design and implement timeout hierarchies for microservices**

```python
class TimeoutBudget:
    """Manage timeout budgets across service calls"""
    
    def __init__(self, total_timeout_ms: int):
        self.total_timeout = total_timeout_ms
        self.start_time = time.time() * 1000
        self.allocations = []
        
    def allocate(self, operation: str, percentage: float) -> int:
        """Allocate portion of remaining budget"""
        elapsed = (time.time() * 1000) - self.start_time
        remaining = max(0, self.total_timeout - elapsed)
        
        allocated = int(remaining * percentage)
        self.allocations.append({
            'operation': operation,
            'allocated_ms': allocated,
            'remaining_ms': remaining
        })
        
        return allocated
        
    def get_remaining(self) -> int:
        """Get remaining timeout budget"""
        elapsed = (time.time() * 1000) - self.start_time
        return max(0, self.total_timeout - elapsed)

# Exercise: Implement timeout propagation
class ServiceCallChain:
    """TODO: Implement service call chain with timeout propagation
    
    Requirements:
    1. Each service gets a portion of the remaining timeout
    2. Timeouts must account for network latency
    3. Early termination if budget exhausted
    4. Timeout headers propagation (like Envoy's x-envoy-timeout-ms)
    """
    
    async def call_chain(self, services: list, initial_timeout_ms: int):
        budget = TimeoutBudget(initial_timeout_ms)
        results = []
        
        for i, service in enumerate(services):
# TODO: Implement timeout allocation strategy
# Consider:
# - Equal distribution
# - Priority-based allocation
# - Dynamic based on historical latency
            pass
            
        return results

# Test scenario
async def test_timeout_coordination():
    services = [
        {"name": "Auth", "expected_latency": 50},
        {"name": "Database", "expected_latency": 100},
        {"name": "Cache", "expected_latency": 20},
        {"name": "External API", "expected_latency": 200}
    ]
    
    chain = ServiceCallChain()
    
# Test with different timeout budgets
    for total_timeout in [100, 300, 500, 1000]:
        print(f"\nTesting with {total_timeout}ms budget:")
        results = await chain.call_chain(services, total_timeout)
        print(f"Results: {results}")
```

---

## 💪 Challenge Problems

### Challenge 1: Multi-Region Availability Calculator

**Calculate system availability with complex failure scenarios**

```python
class AvailabilityCalculator:
    """Calculate distributed system availability"""
    
    def __init__(self):
        self.components = {}
        self.dependencies = {}
        
    def add_component(self, name: str, availability: float, mttr_hours: float):
        """Add system component with availability metrics"""
        self.components[name] = {
            'availability': availability,
            'mttr': mttr_hours,
            'mtbf': mttr_hours * availability / (1 - availability)
        }
        
    def add_dependency(self, from_component: str, to_component: str, 
                      dependency_type: str = 'serial'):
        """Add dependency between components"""
        if from_component not in self.dependencies:
            self.dependencies[from_component] = []
        self.dependencies[from_component].append({
            'to': to_component,
            'type': dependency_type  # 'serial' or 'parallel'
        })

# Challenge: Calculate these scenarios
scenarios = [
    {
        "name": "Single Region",
        "components": [
            ("LoadBalancer", 0.9999, 0.5),
            ("WebServer1", 0.999, 1.0),
            ("WebServer2", 0.999, 1.0),
            ("Database", 0.9995, 2.0),
            ("Cache", 0.999, 0.5)
        ],
        "topology": "Calculate availability for: LB → (WS1 || WS2) → (DB & Cache)"
    },
    {
        "name": "Multi-Region Active-Active",
        "components": [
            ("Region1", 0.999, 4.0),
            ("Region2", 0.999, 4.0),
            ("GlobalDB", 0.9999, 1.0)
        ],
        "question": "What's the availability if either region can serve traffic?"
    },
    {
        "name": "Microservices Mesh",
        "services": 25,
        "avg_availability": 0.999,
        "critical_path_length": 5,
        "question": "What's the end-to-end availability?"
    }
]

# Your task: Implement availability calculation for each scenario
```

### Challenge 2: Retry Storm Prevention

**Design a retry strategy that prevents cascading failures**

```python
import math
import random
from dataclasses import dataclass
from typing import Optional

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 10000
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1

class SmartRetryStrategy:
    """TODO: Implement smart retry strategy that prevents retry storms
    
    Requirements:
    1. Exponential backoff with jitter
    2. Circuit breaker integration
    3. Retry budget (max retries per time window)
    4. Adaptive retry based on system load
    5. Retry storm detection and mitigation
    """
    
    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self.retry_budget = RetryBudget()
        self.load_monitor = LoadMonitor()
        
    def should_retry(self, attempt: int, error: Exception) -> tuple[bool, Optional[int]]:
        """Determine if we should retry and delay if yes
        
        Returns: (should_retry, delay_ms)
        """
# TODO: Implement smart retry logic
        pass

class RetryBudget:
    """Limit total retries to prevent storms"""
    def __init__(self, window_size_seconds: int = 60, max_retries: int = 1000):
        self.window_size = window_size_seconds
        self.max_retries = max_retries
        self.attempts = deque()
        
    def try_acquire(self) -> bool:
        """Try to acquire retry permit"""
# TODO: Implement sliding window retry budget
        pass

class LoadMonitor:
    """Monitor system load to adapt retry behavior"""
    def __init__(self):
        self.cpu_usage = 0.5
        self.error_rate = 0.01
        self.queue_depth = 100
        
    def get_retry_multiplier(self) -> float:
        """Get retry delay multiplier based on system load"""
# TODO: Implement adaptive retry based on:
# - CPU usage
# - Error rate
# - Queue depth
# - Time of day
        pass

# Test scenario: Simulate retry storm
def simulate_retry_storm():
    """Simulate what happens when backend fails"""
# 1000 clients, backend fails, everyone retries
# Show how smart retry prevents storm
    pass
```

### Challenge 3: Intelligent Health Checking

**Implement adaptive health checks that don't cause failures**

```python
class HealthChecker:
    """Advanced health checking system"""
    
    def __init__(self):
        self.checks = {}
        self.history = {}
        self.adaptive_intervals = {}
        
    def register_check(self, name: str, check_func, initial_interval_ms: int):
        """Register a health check"""
        self.checks[name] = {
            'func': check_func,
            'interval': initial_interval_ms,
            'consecutive_failures': 0,
            'last_check': 0
        }
        
# TODO: Implement these features
# 1. Adaptive check intervals (check less when healthy, more when flaky)
# 2. Deep vs shallow checks based on system state
# 3. Dependency-aware checking (don't check DB if network is down)
# 4. Circuit breaker for health checks themselves
# 5. Health check budget to prevent overload

# Exercise: Design health check strategies for:
health_scenarios = [
    {
        "service": "Database",
        "challenge": "Health checks cause connection pool exhaustion",
        "solution": "?"
    },
    {
        "service": "External API",
        "challenge": "Health checks cost money (metered API)",
        "solution": "?"
    },
    {
        "service": "Distributed Cache",
        "challenge": "Health of one node doesn't reflect cluster health",
        "solution": "?"
    }
]
```

---

## Research Projects

### Project 1: Failure Pattern Analysis

**Analyze real production failures and build detection algorithms**

```python
class FailurePatternDetector:
    """Detect failure patterns in production systems"""
    
    def __init__(self):
        self.patterns = {
            'cascading_failure': CascadingFailureDetector(),
            'retry_storm': RetryStormDetector(),
            'death_spiral': DeathSpiralDetector(),
            'thundering_herd': ThunderingHerdDetector()
        }
        
    def analyze_metrics(self, metrics_stream):
        """Analyze metrics stream for failure patterns"""
# TODO: Implement pattern detection
        pass

# Research task: Implement detection for these patterns
class CascadingFailureDetector:
    """Detect when failure spreads through system
    
    Signals:
    - Error rate correlation between services
    - Increasing latency propagation
    - Connection pool exhaustion spreading
    """
    pass

class RetryStormDetector:
    """Detect excessive retries causing more failures
    
    Signals:
    - Exponential increase in request rate
    - High correlation between errors and request rate
    - Bimodal latency distribution
    """
    pass
```

### Project 2: Chaos Engineering Game

**Build a game where players design systems to survive failures**

```python
class ChaosGame:
    """Distributed systems survival game"""
    
    def __init__(self):
        self.budget = 100000  # Dollar budget
        self.components = []  # Player's system
        self.chaos_events = []  # Random failures
        self.score = 0
        
    def design_phase(self):
        """Players design their system"""
# Choose components:
# - Load balancers ($1000/month, 99.99% uptime)
# - Servers ($500/month, 99.9% uptime)
# - Databases ($2000/month, 99.95% uptime)
# - Regions ($5000/month base cost)
        pass
        
    def chaos_phase(self):
        """System faces random failures"""
        events = [
            "Region 1 network partition",
            "Database corruption",
            "100x traffic spike",
            "Cascading service failures",
            "Security breach attempt"
        ]
# Score based on system resilience
        pass

# Challenge: Create scoring system that rewards:
# - High availability during failures
# - Cost efficiency
# - Fast recovery
# - Minimal user impact
```

---

## Failure Metrics Dashboard

**Build monitoring for failure patterns**

```yaml
Key Metrics to Track:
  
  Availability Metrics:
    - Service uptime percentage
    - Error rates by type
    - Success rates by endpoint
    - Partial failure rates
    
  Resilience Metrics:
    - Circuit breaker state changes
    - Retry rates and success
    - Timeout frequencies
    - Fallback usage
    
  Recovery Metrics:
    - Mean time to detection (MTTD)
    - Mean time to recovery (MTTR)
    - Failure impact radius
    - Auto-recovery success rate
    
  System Health Score:
    - Composite metric combining:
      * Current error rate
      * Recent failures
      * Recovery velocity
      * Dependency health
```

---

## Capstone Project: Build a Resilient Service

**Combine all concepts into a production-ready service**

Requirements:
1. Handle 10,000 requests/second
2. Maintain 99.9% availability
3. Recover from any single component failure in <30 seconds
4. Prevent cascading failures
5. Provide meaningful error messages

```python
# Your mission: Build this service
class ResilientWebService:
    """Production-ready web service with all resilience patterns"""
    
    def __init__(self):
# TODO: Initialize all resilience components
        pass
        
    async def handle_request(self, request):
        """Handle incoming request with full resilience"""
# TODO: Implement request handling with:
# - Circuit breakers
# - Retries
# - Timeouts
# - Fallbacks
# - Load shedding
# - Graceful degradation
        pass

# Test harness will throw everything at your service:
# - Network failures
# - Dependency failures
# - Traffic spikes
# - Malformed requests
# - Coordinated failures
```

---

## Skills Assessment

Rate your understanding (1-5):
- [ ] Can implement circuit breakers
- [ ] Understand timeout hierarchies
- [ ] Can calculate system availability
- [ ] Know how to prevent retry storms
- [ ] Can design for graceful degradation
- [ ] Understand failure domains
- [ ] Can implement chaos engineering
- [ ] Know health check best practices

**Score: ___/40** (32+ = Expert, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 4: Concurrency](/part1-axioms/archive-old-8-axiom-structure/axiom4-concurrency/)

**Related**: [Circuit Breaker](/patterns/circuit-breaker) • [Retry Backoff](/patterns/retry-backoff) • [Bulkhead](/patterns/bulkhead) • [Health Check](/patterns/health-check) • [Timeout](/patterns/timeout)

## References

¹ [Google SRE Book: Chapter 3 - Embracing Risk](https://sre.google/sre-book/embracing-risk/)

² [Netflix Technology Blog: The Netflix Simian Army](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116)

³ [AWS Well-Architected Framework: Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)

⁴ [Principles of Chaos Engineering](https://principlesofchaos.org/)

⁵ [Martin Fowler: Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
