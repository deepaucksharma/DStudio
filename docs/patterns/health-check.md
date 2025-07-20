---
title: Health Check Pattern
description: "<div class="pattern-context">
<h3>🧭 Pattern Context</h3>"
type: pattern
difficulty: advanced
reading_time: 25 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Health Check Pattern**


# Health Check Pattern

**Monitoring service health for reliable systems**

> *"A system that doesn't know it's sick can't heal itself."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Detecting failures proactively
- [Axiom 6: Observability](/part1-axioms/axiom6-observability/) - System introspection

**🔧 Solves These Problems**:
- Detecting service degradation before total failure
- Automated recovery and routing decisions
- Load balancer health decisions
- Dependency failure cascades

**🤝 Works Best With**:
- [Circuit Breaker](/patterns/circuit-breaker/) - Health checks inform circuit state
- [Service Discovery](/patterns/service-discovery/) - Register/deregister based on health
- [Load Balancing](/patterns/load-balancing/) - Route based on health status
</div>

---

## 🎯 Level 1: Intuition

### The Medical Checkup Analogy

Health checks are like regular medical checkups:
- **Basic vitals**: Is the service responding? (pulse check)
- **Specific tests**: Can it connect to the database? (blood test)
- **Comprehensive exam**: Full system validation (annual physical)

### Simple Health Check

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/health')
def basic_health():
    """Simple liveness check - is the service running?"""
    return jsonify({"status": "healthy"}), 200

@app.route('/health/ready')
def readiness_check():
    """Readiness check - can the service handle requests?"""
    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "disk_space": check_disk_space()
    }
    
    # All checks must pass
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return jsonify({
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }), status_code

def check_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return True
    except:
        return False
```

---

## 🏗️ Level 2: Foundation

### Types of Health Checks

| Check Type | Purpose | Frequency | Timeout |
|------------|---------|-----------|---------|
| **Liveness** | Is process alive? | 10-30s | 1-2s |
| **Readiness** | Can handle traffic? | 5-10s | 2-5s |
| **Startup** | Initialization complete? | 1-5s | 30-60s |
| **Deep** | Full dependency check | 30-60s | 10-20s |

### Health Check Response Standards

```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "1.2.3",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45
    },
    "cache": {
      "status": "degraded",
      "message": "High latency detected",
      "response_time_ms": 250
    },
    "disk": {
      "status": "healthy",
      "free_space_gb": 45.2,
      "usage_percent": 65
    }
  }
}
```

### Implementing Comprehensive Health Checks

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: Optional[str] = None
    response_time_ms: Optional[float] = None
    metadata: Optional[Dict] = None

class HealthChecker:
    def __init__(self):
        self.checks = []
        
    def register_check(self, name: str, check_func, critical: bool = True):
        """Register a health check function"""
        self.checks.append({
            'name': name,
            'func': check_func,
            'critical': critical
        })
    
    async def run_checks(self, timeout: float = 5.0) -> Dict:
        """Run all registered health checks"""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        # Run checks in parallel with timeout
        tasks = []
        for check in self.checks:
            task = self._run_single_check(check, timeout)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Determine overall status
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Check timed out or failed
                result = HealthCheckResult(
                    name=self.checks[i]['name'],
                    status=HealthStatus.UNHEALTHY,
                    message=str(result)
                )
            
            if result.status == HealthStatus.UNHEALTHY:
                if self.checks[i]['critical']:
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status != HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif result.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        return {
            'status': overall_status.value,
            'timestamp': time.time(),
            'checks': {r.name: r.__dict__ for r in results}
        }
    
    async def _run_single_check(self, check: Dict, timeout: float) -> HealthCheckResult:
        """Run a single check with timeout"""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                check['func'](),
                timeout=timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=check['name'],
                status=result.get('status', HealthStatus.HEALTHY),
                message=result.get('message'),
                response_time_ms=response_time,
                metadata=result.get('metadata')
            )
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=check['name'],
                status=HealthStatus.UNHEALTHY,
                message=f"Check timed out after {timeout}s"
            )
        except Exception as e:
            return HealthCheckResult(
                name=check['name'],
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
```

---

## 🔧 Level 3: Deep Dive

### Advanced Health Check Patterns

#### Dependency Health Aggregation
```python
class DependencyHealthChecker:
    """Check health of all dependencies with smart aggregation"""
    
    def __init__(self):
        self.dependencies = {}
        self.weights = {}  # Importance weights
    
    def add_dependency(self, name: str, 
                      health_url: str, 
                      weight: float = 1.0,
                      required: bool = True):
        self.dependencies[name] = {
            'url': health_url,
            'required': required
        }
        self.weights[name] = weight
    
    async def check_all_dependencies(self) -> Dict:
        """Check all dependencies and calculate weighted health score"""
        results = {}
        total_weight = 0
        healthy_weight = 0
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for name, config in self.dependencies.items():
                task = self._check_dependency(session, name, config)
                tasks.append(task)
            
            dep_results = await asyncio.gather(*tasks)
            
            for name, result in zip(self.dependencies.keys(), dep_results):
                results[name] = result
                
                if result['healthy']:
                    healthy_weight += self.weights[name]
                elif self.dependencies[name]['required']:
                    # Required dependency is down
                    return {
                        'status': 'unhealthy',
                        'score': 0,
                        'dependencies': results
                    }
                
                total_weight += self.weights[name]
        
        # Calculate health score
        health_score = healthy_weight / total_weight if total_weight > 0 else 0
        
        if health_score >= 0.9:
            status = 'healthy'
        elif health_score >= 0.7:
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'score': health_score,
            'dependencies': results
        }
```

#### Circuit Breaker Integration
```python
class CircuitBreakerHealthCheck:
    """Health checks that integrate with circuit breakers"""
    
    def __init__(self, circuit_breaker):
        self.circuit_breaker = circuit_breaker
        self.consecutive_failures = 0
        self.failure_threshold = 3
    
    async def health_check_with_circuit_breaker(self):
        """Health check that can trip circuit breaker"""
        try:
            # Perform health check
            result = await self.perform_health_check()
            
            if result['status'] == 'healthy':
                self.consecutive_failures = 0
                # If circuit is open, consider closing it
                if self.circuit_breaker.state == 'open':
                    self.circuit_breaker.transition_to_half_open()
            else:
                self.consecutive_failures += 1
                
                # Trip circuit breaker if threshold exceeded
                if self.consecutive_failures >= self.failure_threshold:
                    self.circuit_breaker.trip()
                    
            return result
            
        except Exception as e:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.failure_threshold:
                self.circuit_breaker.trip()
            raise
```

### Health Check Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Common Health Check Mistakes</h3>

1. **Expensive Health Checks**
   ```python
   # BAD: Running full test suite in health check
   @app.route('/health')
   def bad_health_check():
       run_all_integration_tests()  # Takes 30 seconds!
       return "OK"
   
   # GOOD: Lightweight checks only
   @app.route('/health')
   def good_health_check():
       # Quick checks only
       return jsonify({"status": "healthy"}), 200
   ```

2. **Cascading Health Failures**
   ```python
   # BAD: Health check calls other services' health checks
   def cascading_health():
       # This can cause cascading failures!
       service_a_health = requests.get('http://service-a/health')
       service_b_health = requests.get('http://service-b/health')
       
   # GOOD: Check only direct dependencies
   def direct_health():
       # Only check what this service directly needs
       db_ok = check_database_connection()
       cache_ok = check_cache_connection()
   ```

3. **No Caching of Results**
   ```python
   # BAD: Heavy checks on every request
   @app.route('/health/deep')
   def uncached_deep_check():
       return expensive_system_validation()  # Called 100x/second!
   
   # GOOD: Cache expensive check results
   @app.route('/health/deep')
   @cache_for_seconds(30)
   def cached_deep_check():
       return expensive_system_validation()  # Called max 2x/minute
   ```
</div>

---

## 🚀 Level 4: Expert

### Production Health Check Strategies

#### Adaptive Health Checks
```python
class AdaptiveHealthCheck:
    """
    Adjusts health check aggressiveness based on system state
    """
    
    def __init__(self):
        self.recent_results = deque(maxlen=100)
        self.check_interval = 10  # seconds
        self.deep_check_probability = 0.1
        
    def should_run_deep_check(self) -> bool:
        """Determine if deep health check is needed"""
        # More deep checks if recent failures
        failure_rate = sum(1 for r in self.recent_results if not r) / len(self.recent_results) if self.recent_results else 0
        
        if failure_rate > 0.1:
            # System unstable, increase deep checks
            return random.random() < 0.5
        elif failure_rate > 0.05:
            # Some instability
            return random.random() < 0.2
        else:
            # System stable
            return random.random() < self.deep_check_probability
    
    async def adaptive_health_check(self):
        """Run appropriate health check based on system state"""
        if self.should_run_deep_check():
            result = await self.deep_health_check()
        else:
            result = await self.shallow_health_check()
        
        self.recent_results.append(result['healthy'])
        self.adjust_check_interval(result)
        
        return result
    
    def adjust_check_interval(self, result):
        """Adjust how frequently health checks run"""
        if not result['healthy']:
            # Check more frequently when unhealthy
            self.check_interval = max(5, self.check_interval * 0.8)
        else:
            # Check less frequently when stable
            self.check_interval = min(60, self.check_interval * 1.1)
```bash
#### Kubernetes-Style Health Probes
```python
class KubernetesHealthProbes:
    """
    Implement Kubernetes-style liveness, readiness, and startup probes
    """
    
    def __init__(self, app):
        self.app = app
        self.startup_complete = False
        self.startup_tasks = []
        
    async def startup_probe(self) -> Dict:
        """Check if application has started successfully"""
        if self.startup_complete:
            return {"status": "started", "ready": True}
        
        # Check startup tasks
        completed = sum(1 for task in self.startup_tasks if task.done())
        total = len(self.startup_tasks)
        
        if completed == total:
            self.startup_complete = True
            return {"status": "started", "ready": True}
        else:
            return {
                "status": "starting",
                "ready": False,
                "progress": f"{completed}/{total}",
                "message": f"Startup in progress: {completed}/{total} tasks complete"
            }
    
    async def liveness_probe(self) -> Dict:
        """Check if application is alive and should not be restarted"""
        try:
            # Basic checks that should always work
            # Avoid checking external dependencies here
            
            # Check event loop responsiveness
            start = time.time()
            await asyncio.sleep(0)
            event_loop_delay = time.time() - start
            
            if event_loop_delay > 1.0:
                return {
                    "status": "unhealthy",
                    "reason": "Event loop blocked",
                    "event_loop_delay_ms": event_loop_delay * 1000
                }
            
            # Check critical internal components
            if not self.app.critical_component_healthy():
                return {
                    "status": "unhealthy",
                    "reason": "Critical component failure"
                }
            
            return {"status": "healthy"}
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "reason": str(e)
            }
    
    async def readiness_probe(self) -> Dict:
        """Check if application is ready to serve traffic"""
        if not self.startup_complete:
            return {"status": "not_ready", "reason": "Still starting up"}
        
        # Check all dependencies needed to serve traffic
        checks = {
            "database": await self.check_database_ready(),
            "cache": await self.check_cache_ready(),
            "downstream_services": await self.check_downstream_ready()
        }
        
        all_ready = all(check["ready"] for check in checks.values())
        
        return {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks
        }
```bash
### Real-World Case Study: Netflix's Deep Health Checks

```python
class NetflixDeepHealthCheck:
    """
    Netflix's approach to comprehensive health checking
    """
    
    def __init__(self):
        self.metrics = PrometheusMetrics()
        self.cache = HealthCheckCache(ttl=30)
        
    async def zuul_health_check(self):
        """
        Zuul (API Gateway) health check strategy
        """
        # Level 1: Basic process health
        basic_health = await self.basic_process_check()
        if not basic_health['healthy']:
            return basic_health
        
        # Level 2: Critical path validation
        critical_path = await self.validate_critical_path()
        if not critical_path['healthy']:
            return {
                **critical_path,
                'degraded': True,
                'serving_traffic': True  # Still serve with degradation
            }
        
        # Level 3: Capacity checks
        capacity = await self.check_capacity_health()
        
        # Level 4: Predictive health
        predicted_issues = await self.ml_health_prediction()
        
        return {
            'status': self.calculate_overall_status(
                basic_health,
                critical_path,
                capacity,
                predicted_issues
            ),
            'components': {
                'basic': basic_health,
                'critical_path': critical_path,
                'capacity': capacity,
                'predictions': predicted_issues
            },
            'metrics': {
                'request_rate': self.metrics.get_request_rate(),
                'error_rate': self.metrics.get_error_rate(),
                'latency_p99': self.metrics.get_latency_p99()
            }
        }
    
    async def validate_critical_path(self):
        """Test actual user-facing functionality"""
        try:
            # Simulate real user request
            test_user_id = "health_check_user"
            
            # Can we authenticate?
            auth_token = await self.auth_service.get_token(test_user_id)
            
            # Can we fetch user data?
            user_data = await self.user_service.get_profile(
                test_user_id,
                auth_token
            )
            
            # Can we get recommendations?
            recommendations = await self.recommendation_service.get_titles(
                test_user_id,
                limit=1
            )
            
            return {
                'healthy': True,
                'critical_path_latency_ms': self.timer.elapsed_ms()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'critical_path_failed': True
            }
```yaml
---

## 🎯 Level 5: Mastery

### Theoretical Optimal Health Checking

```python
class OptimalHealthChecker:
    """
    Information theory optimal health checking
    """
    
    def __init__(self):
        self.failure_probability_model = self.load_ml_model()
        self.check_costs = {}  # Cost in ms for each check
        self.information_gains = {}  # Bits of information per check
        
    def calculate_optimal_check_sequence(self, time_budget_ms: float) -> List[str]:
        """
        Find optimal sequence of health checks given time budget
        Using information theory and dynamic programming
        """
        # Calculate information gain per unit time for each check
        check_efficiency = {}
        for check_name, cost_ms in self.check_costs.items():
            info_gain = self.information_gains[check_name]
            efficiency = info_gain / cost_ms  # Bits per millisecond
            check_efficiency[check_name] = efficiency
        
        # Dynamic programming to find optimal subset
        checks = list(self.check_costs.keys())
        n = len(checks)
        
        # dp[i][t] = max information gain using first i checks with time budget t
        dp = [[0.0 for _ in range(int(time_budget_ms) + 1)] for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            check = checks[i - 1]
            cost = int(self.check_costs[check])
            gain = self.information_gains[check]
            
            for t in range(int(time_budget_ms) + 1):
                # Don't include this check
                dp[i][t] = dp[i-1][t]
                
                # Include this check if we have time
                if t >= cost:
                    dp[i][t] = max(dp[i][t], dp[i-1][t-cost] + gain)
        
        # Backtrack to find which checks to run
        selected_checks = []
        t = int(time_budget_ms)
        for i in range(n, 0, -1):
            if dp[i][t] != dp[i-1][t]:
                selected_checks.append(checks[i-1])
                t -= int(self.check_costs[checks[i-1]])
        
        # Sort by efficiency for execution order
        selected_checks.sort(
            key=lambda x: check_efficiency[x],
            reverse=True
        )
        
        return selected_checks
    
    def calculate_information_gain(self, check_name: str) -> float:
        """
        Calculate information gain (entropy reduction) from a health check
        """
        # P(system_healthy | check_passes)
        p_healthy_given_pass = self.get_conditional_probability(
            check_name, 
            'pass'
        )
        
        # P(system_healthy | check_fails)
        p_healthy_given_fail = self.get_conditional_probability(
            check_name,
            'fail'
        )
        
        # P(check_passes)
        p_check_passes = self.get_check_success_rate(check_name)
        
        # Calculate entropy before and after check
        h_before = self.binary_entropy(self.get_system_health_rate())
        
        h_after = (
            p_check_passes * self.binary_entropy(p_healthy_given_pass) +
            (1 - p_check_passes) * self.binary_entropy(p_healthy_given_fail)
        )
        
        information_gain = h_before - h_after
        
        return information_gain
    
    @staticmethod
    def binary_entropy(p: float) -> float:
        """Calculate binary entropy H(p)"""
        if p == 0 or p == 1:
            return 0
        return -p * math.log2(p) - (1-p) * math.log2(1-p)
```

### Future Directions

1. **Quantum Health Checks**: Superposition of health states
2. **AI-Driven Health Prediction**: Predict failures before they happen
3. **Distributed Consensus Health**: Byzantine fault tolerant health checking
4. **Self-Healing Integration**: Automatic remediation based on health

---

## 📋 Quick Reference

### Health Check Design Principles

1. **Fast**: Health checks should complete quickly (< 5 seconds)
2. **Isolated**: Don't cascade health check failures
3. **Meaningful**: Check actual functionality, not just process existence
4. **Cached**: Cache expensive checks appropriately
5. **Graceful**: Differentiate between degraded and failed

### Implementation Checklist

- [ ] Implement separate liveness and readiness endpoints
- [ ] Add timeout to all health checks
- [ ] Include version information in response
- [ ] Log health check failures for debugging
- [ ] Monitor health check latency
- [ ] Test health checks under load
- [ ] Document what each check validates

---

---

*"The best time to check health is before you get sick."*

---

**Previous**: [← GraphQL Federation](graphql-federation.md) | **Next**: [Idempotent Receiver Pattern →](idempotent-receiver.md)
## 🎯 Problem Statement

### The Challenge
This pattern addresses common distributed systems challenges where health check pattern becomes critical for system reliability and performance.

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
The Health Check Pattern pattern provides a structured approach to handling this distributed systems challenge.

### Key Principles
1. **Isolation**: Separate concerns to prevent failures from spreading
2. **Resilience**: Build systems that gracefully handle failures
3. **Observability**: Make system behavior visible and measurable
4. **Simplicity**: Keep solutions understandable and maintainable

### How It Works
The Health Check Pattern pattern works by:
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
A major e-commerce platform implemented Health Check Pattern to handle critical user flows:

**Challenge**: System failures affected user experience and revenue

**Implementation**: 
- Applied Health Check Pattern pattern to critical service calls
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
class Health_CheckPattern:
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
pattern = Health_CheckPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
health_check:
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
def test_health_check_behavior():
    pattern = Health_CheckPattern(test_config)
    
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



