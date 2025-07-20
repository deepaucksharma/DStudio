# Circuit Breaker Pattern

<div class="navigation-header">
<div class="breadcrumb">
[Home](/) → [Part III: Patterns](/patterns/) → **Circuit Breaker**
</div>

<div class="pattern-nav">
**Related**: [Retry & Backoff](/patterns/retry-backoff/) • [Bulkhead](/patterns/bulkhead/) • [All Patterns](/patterns/)
</div>
</div>

**Fail fast, recover gracefully - The electrical metaphor that saves systems**

> *"Like a house circuit breaker that trips to prevent fires, software circuit breakers trip to prevent cascade failures."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 1: Latency](/part1-axioms/axiom1-latency/) - Fail fast when latency exceeds budgets
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Prevent cascade failures from spreading

**🔧 Solves These Problems**:
- Cascade failures bringing down entire systems
- Resource exhaustion from retry storms
- Poor user experience during service degradation
- Debugging distributed failure scenarios

**🤝 Works Best With**:
- [Retry & Backoff](/patterns/retry-backoff/) - Complements circuit breaking
- [Bulkhead](/patterns/bulkhead/) - Isolates failure domains
- [Timeout Pattern](/patterns/timeout/) - Sets failure detection bounds
- [Health Check API](/patterns/health-check/) - Enables recovery detection
</div>

---

## 🎯 Level 1: Intuition

### The House Circuit Breaker Analogy

Imagine your home's electrical panel:

```
🏠 Normal Operation (CLOSED)
┌─────────────────┐
│ [●] Kitchen     │  ← Circuit allows electricity to flow
│ [●] Living Room │
│ [●] Bedroom     │
└─────────────────┘

⚡ Overload Detected (OPEN)
┌─────────────────┐
│ [○] Kitchen     │  ← Circuit trips, stops electricity
│ [●] Living Room │
│ [●] Bedroom     │
└─────────────────┘

🔧 Testing Recovery (HALF-OPEN)
┌─────────────────┐
│ [?] Kitchen     │  ← Try small load, see if it works
│ [●] Living Room │
│ [●] Bedroom     │
└─────────────────┘
```

**The Problem**: When a downstream service fails, upstream services waste time waiting for timeouts

**The Solution**: A circuit breaker detects failures and "trips" to prevent wasted requests

### Simple State Machine

| State | Behavior | When to Transition |
|-------|----------|--------------------|
| **CLOSED** | Let requests through | After X failures → OPEN |
| **OPEN** | Reject immediately | After timeout → HALF-OPEN |
| **HALF-OPEN** | Test with few requests | Success → CLOSED, Failure → OPEN |

---

## 🏗️ Level 2: Foundation

### Core Principles

#### Failure Detection
Track failure metrics to determine service health:

| Metric Type | Example | Threshold |
|-------------|---------|----------|
| **Error Rate** | 5 failures in 10 requests | 50% |
| **Timeout Rate** | 3 timeouts in 5 requests | 60% |
| **Response Time** | Average > 5 seconds | 5s |
| **Exception Count** | 10 consecutive errors | 10 |

#### State Transitions

```
Failure Threshold Met
    CLOSED ────────────→ OPEN
       ↑                  │
       │                  │ Recovery Timeout
       │                  ↓
    Success           HALF-OPEN
       ↑                  │
       └──────────────────┘
           Test Success
```

#### Configuration Parameters

| Parameter | Purpose | Typical Value |
|-----------|---------|---------------|
| **Failure Threshold** | Errors before opening | 5-10 failures |
| **Recovery Timeout** | Time before testing | 30-60 seconds |
| **Success Threshold** | Successes to close | 2-5 successes |
| **Test Request Ratio** | % requests in half-open | 10-25% |

### Simple Implementation Logic

```
if circuit_state == CLOSED:
    try:
        result = call_service()
        reset_failure_count()
        return result
    except:
        increment_failure_count()
        if failure_count >= threshold:
            circuit_state = OPEN
            last_failure_time = now()
        raise

elif circuit_state == OPEN:
    if now() - last_failure_time > recovery_timeout:
        circuit_state = HALF_OPEN
        test_count = 0
    else:
        raise CircuitOpenError()

elif circuit_state == HALF_OPEN:
    if test_count < max_test_requests:
        try:
            result = call_service()
            test_count += 1
            if test_count >= success_threshold:
                circuit_state = CLOSED
            return result
        except:
            circuit_state = OPEN
            last_failure_time = now()
            raise
    else:
        raise CircuitOpenError()
```

---

## 🔧 Level 3: Deep Dive

### Advanced Circuit Breaker Types

#### Count-Based Circuit Breaker
Tracks absolute failure counts:

| Window | Failures | Requests | Action |
|--------|----------|----------|---------|
| 1 | 3 | 10 | Continue |
| 2 | 7 | 10 | Continue |
| 3 | 12 | 10 | **TRIP** |

#### Rate-Based Circuit Breaker
Tracks failure percentages:

| Window | Failures | Requests | Rate | Action |
|--------|----------|----------|------|---------|
| 1 | 3 | 10 | 30% | Continue |
| 2 | 6 | 10 | 60% | **TRIP** |

#### Sliding Window Circuit Breaker
Maintains rolling window of recent results:

```
Time →    [S][F][S][F][F][S][F][F][F][S]
                      ↑
                 Current window
           Failure rate: 60% → TRIP
```

### Failure Detection Strategies

#### Exception-Based Detection
```
Detect these as failures:
- TimeoutException
- ConnectionRefusedException  
- ServiceUnavailableException
- HTTP 5xx status codes

Ignore these:
- ValidationException (4xx)
- AuthenticationException
- BusinessLogicException
```

#### Latency-Based Detection
```
Latency Percentiles:
P50: 100ms ← Normal
P95: 500ms ← Warning
P99: 2000ms ← Critical → Count as failure
```

#### Custom Health Checks
```
Health Check Logic:
1. Ping endpoint every 30s
2. If 3 consecutive pings fail → Mark unhealthy
3. If circuit is HALF-OPEN and ping succeeds → Test with real traffic
```

### Fallback Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| **Cached Response** | Read operations | Return last known good data |
| **Default Value** | Configuration | Return system defaults |
| **Degraded Mode** | Complex operations | Simplified algorithm |
| **Alternative Service** | Redundancy | Call backup service |
| **Graceful Degradation** | User experience | Disable non-critical features |

---

## 🚀 Level 4: Expert

### Production Patterns

#### Netflix Hystrix Architecture
```
Application Thread
       │
       ▼
┌─────────────┐
│   Hystrix   │
│   Command   │
└─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│Circuit      │────▶│  Fallback   │
│Breaker      │     │  Method     │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│Thread Pool  │
│Isolation    │
└─────────────┘
       │
       ▼
  Remote Service
```

#### Multi-Level Circuit Breakers
```
Application Level
├── Service A Circuit Breaker
│   ├── Instance A1 Health
│   ├── Instance A2 Health  
│   └── Instance A3 Health
├── Service B Circuit Breaker
│   ├── Instance B1 Health
│   └── Instance B2 Health
└── Database Circuit Breaker
    ├── Read Replica Health
    └── Write Master Health
```

#### Distributed Circuit Breaker State

**Problem**: Individual instances have different views of service health

**Solution**: Shared circuit breaker state

| Approach | Pros | Cons |
|----------|------|------|
| **Redis Store** | Fast, consistent | Single point of failure |
| **Consensus** | Highly available | Complex, slow |
| **Gossip Protocol** | Decentralized | Eventually consistent |
| **Load Balancer** | Centralized control | Vendor lock-in |

### Advanced Failure Cases

#### Thundering Herd on Recovery
```
Problem:
Circuit reopens → All instances send traffic simultaneously

Solution: Gradual Recovery
Half-open: 10% traffic → 25% → 50% → 100%
```

#### False Positives
```
Cause: Temporary network glitch
Result: Circuit opens unnecessarily

Mitigation:
- Require sustained failures
- Different thresholds for different error types
- Jittered recovery times
```

#### Cascade Failures
```
Service A calls Service B calls Service C

C fails → B circuit opens → A circuit opens

Result: Entire request path unusable

Mitigation:
- Different timeout values per layer
- Partial failure handling
- Graceful degradation
```

### Real-World Case Study: Uber's Circuit Breaker

**Problem**: Maps service failures causing rider app crashes

**Implementation**:
- Service-level circuit breakers for each microservice
- Redis-based shared state across instances  
- Fallback to cached map tiles
- Gradual recovery with 5% → 25% → 100% traffic

**Results**:
- 99.9% → 99.99% availability improvement
- 50% reduction in user-visible errors
- 30% faster recovery from incidents

---

## 🎯 Level 5: Mastery

### Next-Generation Patterns

#### Adaptive Circuit Breakers
```
Machine Learning Integration:
- Predict failures before they happen
- Adjust thresholds based on traffic patterns
- Learn from historical incident data

Adaptive Thresholds:
Low traffic period: 3 failures = trip
High traffic period: 50 failures = trip
Deploy period: 1 failure = trip
```

#### Circuit Breaker Mesh
```
Service Mesh Integration:
┌─────────┐    ┌─────────┐    ┌─────────┐
│Service A│◄──►│ Envoy   │◄──►│Service B│
└─────────┘    │Sidecar  │    └─────────┘
               └─────────┘
                    │
                    ▼
              Global Circuit
              Breaker State
```

#### Chaos Engineering Integration
```
Automated Failure Injection:
1. Inject faults during low-traffic periods
2. Verify circuit breakers activate correctly
3. Measure recovery time
4. Tune parameters based on results

Continuous Validation:
- Weekly chaos tests
- Automated threshold adjustment
- Real-time circuit breaker efficacy metrics
```

### Economic Impact Analysis

#### Cost-Benefit Matrix

| Impact | Without Circuit Breaker | With Circuit Breaker |
|--------|------------------------|---------------------|
| **Availability** | 99.9% (8.76h/year down) | 99.99% (52m/year down) |
| **MTTR** | 30 minutes | 5 minutes |
| **User Experience** | Timeouts, errors | Fast failures, fallbacks |
| **Development Cost** | $0 | $50K implementation |
| **Operational Cost** | $2M/year downtime | $200K/year downtime |
| **ROI** | - | 3,600% first year |

#### Circuit Breaker Metrics Dashboard

```
Production Monitoring:

┌─ Circuit Breaker Health ─────────────────────┐
│ Service A: ●CLOSED   (99.9% success rate)   │
│ Service B: ⚠HALF-OPEN (testing recovery)    │  
│ Service C: ○OPEN     (recovering in 45s)    │
└─────────────────────────────────────────────┘

┌─ Performance Impact ────────────────────────┐
│ Prevented cascade failures: 23 this week    │
│ Avg recovery time: 2.3 minutes             │
│ Fallback success rate: 96.7%               │
└─────────────────────────────────────────────┘
```

### Future Directions

#### AI-Powered Circuit Breakers
- **Predictive failure detection** using anomaly detection
- **Auto-tuning parameters** based on service characteristics  
- **Smart fallback selection** using reinforcement learning
- **Cross-service failure correlation** for proactive protection

#### Edge Computing Circuit Breakers
- **Geographic failure isolation** at edge locations
- **Network-aware circuit breaking** based on latency zones
- **Mobile-first circuit breakers** for offline scenarios
- **IoT device circuit breakers** for resource-constrained environments

---

## 📋 Quick Reference

### Decision Framework

| Question | Yes → Use Circuit Breaker | No → Alternative |
|----------|---------------------------|------------------|
| Calling external services? | ✅ Essential | ⚠️ Consider for internal services |
| Risk of cascade failures? | ✅ High priority | ⚠️ Simple retry may suffice |
| Can implement fallbacks? | ✅ Maximum benefit | ⚠️ Still valuable for fast failure |
| Service has SLA? | ✅ Protect your SLA | ⚠️ Monitor and alert instead |
| High traffic volume? | ✅ Prevents resource exhaustion | ⚠️ Simple timeout may work |

### Implementation Checklist

#### Basic Circuit Breaker
- [ ] Define failure criteria (exceptions, timeouts, status codes)
- [ ] Set failure threshold (5-10 failures)
- [ ] Configure recovery timeout (30-60 seconds)
- [ ] Implement basic state machine (CLOSED/OPEN/HALF-OPEN)
- [ ] Add monitoring and alerting

#### Production-Ready Circuit Breaker
- [ ] Thread-safe implementation
- [ ] Configurable parameters via config system
- [ ] Comprehensive metrics (state changes, failure rates)
- [ ] Fallback mechanism integration
- [ ] Graceful degradation strategies
- [ ] Performance testing under load

#### Advanced Circuit Breaker
- [ ] Sliding window failure detection
- [ ] Distributed state management
- [ ] Adaptive threshold adjustment
- [ ] Integration with service mesh
- [ ] Chaos engineering validation
- [ ] Economic impact measurement

### Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|---------|
| **Threshold too low** | False positives | Start with 10-20 failures |
| **Recovery timeout too short** | Constant flapping | Use exponential backoff |
| **No fallback strategy** | Poor user experience | Always implement fallbacks |
| **Ignoring partial failures** | Delayed problem detection | Monitor latency percentiles |
| **Shared circuit breaker** | Resource contention | Use per-service instances |

---

*"The best circuit breaker is invisible when working and obvious when protecting."*

---

## Summary by Level

| Level | Key Takeaway | When You Need It |
|-------|-------------|------------------|
| **Level 1** | Circuit breakers prevent cascade failures like house breakers prevent fires | Starting with circuit breakers |
| **Level 2** | State machine with configurable thresholds and recovery timeouts | Basic production implementation |
| **Level 3** | Advanced detection strategies and fallback patterns | High-traffic production systems |
| **Level 4** | Distributed state management and chaos engineering validation | Mission-critical enterprise systems |
| **Level 5** | AI-powered adaptive circuit breakers with predictive failure detection | Cutting-edge resilience engineering |

## Quick Decision Matrix

| Use Case | Circuit Breaker Type | Key Configuration |
|----------|---------------------|-------------------|
| **Microservice calls** | Basic count-based | 5 failures, 30s timeout |
| **Database connections** | Rate-based | 50% failure rate, 60s timeout |
| **External APIs** | Sliding window | 10-request window, 40% threshold |
| **Critical payments** | Distributed with fallback | Redis state, cached responses |
| **Real-time systems** | Adaptive ML-powered | Dynamic thresholds, 5s timeout |

## Implementation Templates

### Basic Circuit Breaker Configuration
```yaml
circuit_breaker:
  failure_threshold: 5
  recovery_timeout: 30s
  success_threshold: 2
  exceptions:
    - TimeoutException
    - ConnectionException
    - ServiceUnavailableException
```

### Advanced Production Configuration
```yaml
circuit_breaker:
  sliding_window:
    size: 20
    minimum_throughput: 10
  failure_criteria:
    error_rate: 50%
    slow_call_rate: 80%
    slow_call_duration: 5s
  fallback:
    strategy: cached_response
    max_age: 300s
  monitoring:
    metrics_enabled: true
    alerts_enabled: true
```

---

<div class="navigation-footer">
<div class="pattern-implementation">
<h3>🛠️ Implementation Resources</h3>

**📝 Code Examples**:
- [Python Implementation](/patterns/circuit-breaker/#python-implementation) - Production-ready circuit breaker
- [Java/Hystrix Example](/patterns/circuit-breaker/#hystrix-example) - Netflix's battle-tested approach
- [Go Implementation](/patterns/circuit-breaker/#go-implementation) - High-performance breaker
- [Configuration Templates](/patterns/circuit-breaker/#configuration) - Ready-to-use configs

**🧪 Testing & Validation**:
- [Chaos Engineering Tests](/patterns/circuit-breaker/#chaos-tests) - Validate failure scenarios
- [Load Testing](/patterns/circuit-breaker/#load-tests) - Verify threshold settings
- [Monitoring Setup](/patterns/circuit-breaker/#monitoring) - Essential metrics and alerts

**📚 Deep Dive**:
- [Mathematical Analysis](/quantitative/reliability-math/) - Calculate optimal thresholds
- [Failure Mode Analysis](/part1-axioms/axiom3-failure/examples/) - Understanding failure patterns
</div>

<div class="real-world-usage">
<h3>🏢 See It In Production</h3>

**📊 Case Studies**:
- [Netflix Hystrix](/case-studies/#netflix-hystrix) - Pioneering circuit breaker implementation
- [AWS Lambda](/case-studies/#aws-lambda) - Serverless circuit breaking
- [Spotify Backend](/case-studies/#spotify-backend) - Music streaming resilience
- [Uber Microservices](/case-studies/#uber-microservices) - High-scale service protection

**🎯 Common Scenarios**:
- **Database Overload**: Protect DB from query storms
- **External API Failures**: Graceful degradation for third-party services
- **Microservice Cascades**: Prevent service-to-service failure propagation
- **Resource Exhaustion**: Stop requests when resources are depleted
</div>

<div class="pattern-relationships">
<h3>🔗 Related Patterns & Concepts</h3>

**🤝 Complementary Patterns**:
- [Retry & Backoff](/patterns/retry-backoff/) - Use together for robust error handling
- [Bulkhead](/patterns/bulkhead/) - Isolate different failure domains
- [Timeout](/patterns/timeout/) - Set clear failure detection boundaries
- [Health Check](/patterns/health-check/) - Enable automatic recovery detection

**⚖️ Alternative Approaches**:
- [Rate Limiting](/patterns/rate-limiting/) - Prevent overload vs. failing fast
- [Load Shedding](/patterns/load-shedding/) - Drop requests vs. circuit breaking
- [Graceful Degradation](/patterns/graceful-degradation/) - Reduced functionality vs. hard failures

**🧠 Foundational Concepts**:
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Why circuit breakers are necessary
- [Coordination Pillar](/part2-pillars/coordination/) - How circuit breakers aid coordination
- [Reliability Engineering](/human-factors/sre-practices/) - Operational considerations
</div>

<div class="next-steps">
<h3>📚 Continue Learning</h3>

**🎯 Immediate Next Steps**:
1. **Implement**: Start with [basic implementation](/patterns/circuit-breaker/#implementation)
2. **Test**: Try [chaos engineering exercise](/patterns/circuit-breaker/#chaos-tests)
3. **Monitor**: Set up [essential metrics](/patterns/circuit-breaker/#monitoring)

**🚀 Recommended Path**:
- **Next Pattern**: [Retry & Backoff](/patterns/retry-backoff/) - Perfect complement to circuit breaking
- **Deep Dive**: [Failure Analysis](/part1-axioms/axiom3-failure/) - Understand the underlying axiom
- **Apply**: [Netflix Case Study](/case-studies/#netflix) - See large-scale implementation

**🎓 Mastery Check**: Can you explain when circuit breakers make things worse? [Advanced scenarios →](/patterns/circuit-breaker/#anti-patterns)
</div>
</div>

---

*\"The circuit breaker is your system's immune system - it sacrifices individual requests to protect the whole organism.\"*