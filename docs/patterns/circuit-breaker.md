---
title: Circuit Breaker Pattern
description: Prevent cascade failures in distributed systems by failing fast when services are unhealthy
type: pattern
difficulty: intermediate
reading_time: 45 min
prerequisites: []
pattern_type: "resilience"
when_to_use: "External service calls, microservice communication, database connections"
when_not_to_use: "Internal method calls, non-network operations, CPU-bound tasks"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Circuit Breaker Pattern**

# Circuit Breaker Pattern

**Prevent cascade failures by failing fast when services are unhealthy**

## 🎯 Level 1: Intuition

### Core Concept

Like electrical circuit breakers that trip to prevent fires, software circuit breakers detect failures and "trip" to stop wasting resources on doomed requests.

```text
CLOSED: Allow requests → Track failures → Trip after threshold
OPEN: Reject immediately → Wait for recovery timeout
HALF-OPEN: Test with limited requests → Success=CLOSED, Failure=OPEN
```

| State | Behavior | Transition |
|-------|----------|-----------|
| **CLOSED** | Normal operation | X failures → OPEN |
| **OPEN** | Fail fast | Timeout → HALF-OPEN |
| **HALF-OPEN** | Test recovery | Success → CLOSED, Failure → OPEN |

---

## 🏗️ Level 2: Foundation

### Failure Detection & Configuration

| Metric | Example Threshold | Parameter | Typical Value |
|--------|------------------|-----------|---------------|
| **Error Rate** | 50% (5/10 requests) | **Failure Threshold** | 5-10 failures |
| **Timeout Rate** | 60% (3/5 requests) | **Recovery Timeout** | 30-60 seconds |
| **Response Time** | >5 seconds average | **Success Threshold** | 2-5 successes |
| **Consecutive Errors** | 10 in a row | **Test Request Ratio** | 10-25% |

### Implementation Flow

```text
CLOSED State:
  Request → Try call → Success: Reset counter
                    → Failure: Count++ → Threshold? → OPEN

OPEN State:
  Request → Timeout expired? → Yes: HALF-OPEN
                            → No: Reject immediately

HALF-OPEN State:
  Request → Test call → Success: Count++ → Enough? → CLOSED
                     → Failure: OPEN
```

---

## 🔧 Level 3: Deep Dive

### Circuit Breaker Types

| Type | Tracks | Example | Use Case |
|------|--------|---------|----------|
| **Count-Based** | Absolute failures | 12 failures → TRIP | Simple scenarios |
| **Rate-Based** | Failure percentage | 60% failure rate → TRIP | Variable traffic |
| **Sliding Window** | Rolling metrics | Last N requests | Most accurate |

### Failure Detection Strategies

**Exception-Based**: Count TimeoutException, ConnectionRefused, 5xx errors as failures. Ignore 4xx client errors.

**Latency-Based**: P99 > 2000ms = failure

**Health Checks**: Ping every 30s, 3 consecutive failures = unhealthy

### Fallback Strategies

- **Cached Response**: Return last known good data
- **Default Value**: Use system defaults
- **Degraded Mode**: Simplified algorithm
- **Alternative Service**: Call backup
- **Graceful Degradation**: Disable non-critical features

---

## 🚀 Level 4: Expert

### Production Patterns

#### Netflix Hystrix Architecture

- **Protection Layers**: Circuit Breaker → Thread Pool Isolation → Fallback Method
- **Flow**: Request → Check Circuit → If closed: Try service → Success/Failure
- **Fallback**: Circuit open or service failure → Return cached/default response

#### Multi-Level Circuit Breakers

- **Application Level**: Global circuit breaker
- **Service Level**: Per-service circuit breakers (Service A, B, Database)
- **Instance Level**: Per-instance health tracking
- **Benefit**: Granular failure isolation - instance failure doesn't affect entire service

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
```text
Problem:
Circuit reopens → All instances send traffic simultaneously

Solution: Gradual Recovery
Half-open: 10% traffic → 25% → 50% → 100%
```

#### False Positives
```text
Cause: Temporary network glitch
Result: Circuit opens unnecessarily

Mitigation:
- Require sustained failures
- Different thresholds for different error types
- Jittered recovery times
```

#### Cascade Failures
```text
Service A calls Service B calls Service C

C fails → B circuit opens → A circuit opens

Result: Entire request path unusable

Mitigation:
- Different timeout values per layer
- Partial failure handling
- Graceful degradation
```

### Case Study: Uber

**Problem**: Maps service failures crashed rider app

**Solution**: Service-level circuit breakers with Redis shared state, cached map tile fallbacks, gradual recovery (5%→25%→100%)

**Results**: 99.9%→99.99% availability, 50% fewer errors, 30% faster recovery

---

## 🎯 Level 5: Mastery

### Next-Generation Patterns

#### Adaptive Circuit Breakers
```dockerfile
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
```proto
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
```yaml
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

<div class="decision-box">
<h4>🎯 Production Monitoring Dashboard</h4>

**Circuit Breaker Health Status**

| Service | State | Success Rate | Status |
|---------|-------|--------------|--------|
| Service A | 🟢 CLOSED | 99.9% | Healthy, normal operation |
| Service B | 🟡 HALF-OPEN | Testing | Testing recovery with limited traffic |
| Service C | 🔴 OPEN | 0% | Failed, recovering in 45s |

**Performance Impact Metrics**

| Metric | Value | Trend |
|--------|-------|-------|
| Prevented Cascade Failures | 23 this week | ↓ 15% |
| Average Recovery Time | 2.3 minutes | ↓ 0.5 min |
| Fallback Success Rate | 96.7% | ↑ 2.1% |
| Circuit Trip Events | 45 this week | ↓ 8% |

</div>

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

## Summary

- **Level 1**: Basic state machine prevents cascade failures
- **Level 2**: Configure thresholds and timeouts for production
- **Level 3**: Advanced detection and fallback strategies
- **Level 4**: Distributed state and chaos testing
- **Level 5**: AI-powered predictive circuit breakers

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

---

*\"The circuit breaker is your system's immune system - it sacrifices individual requests to protect the whole organism.\"*

---

**Previous**: [← Change Data Capture (CDC)](cdc.md) | **Next**: [Consensus Pattern →](consensus.md)

**Related**: [Retry Backoff](retry-backoff.md) • [Bulkhead](bulkhead.md) • [Timeout](timeout.md)
