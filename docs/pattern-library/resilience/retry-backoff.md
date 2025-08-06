---
title: Retry with Exponential Backoff
category: resilience
excellence_tier: silver
pattern_status: recommended
introduced: 1980-01
current_relevance: mainstream
---
# Retry with Exponential Backoff

!!! success "🏆 Gold Standard Pattern"
**Implementation available in production systems**

## Essential Question
**How do we distinguish between transient and permanent failures, retrying the former without creating thundering herds?**

## When to Use / When NOT to Use

### Use When
| Scenario | Example | Success Rate |
|----------|---------|--------------|
| Network timeouts | API calls | 95%+ recovery |
| Rate limiting | 429 errors | 99%+ recovery |
| Temporary unavailability | 503 errors | 90%+ recovery |
| Database deadlocks | Lock timeouts | 85%+ recovery |
| Service overload | 500 errors | 80%+ recovery |

### DON'T Use When
| Scenario | Why | Alternative |
|----------|-----|-------------|
| Business logic errors | Won't fix with retry | Fix the logic |
| Authentication failures | Credentials won't improve | Refresh token |
| Data validation errors | Bad data stays bad | Validate first |
| Resource not found | 404 won't change | Handle missing resource |
| Client errors (4xx) | Client issue won't resolve | Fix request |

### The Story
Imagine calling a busy restaurant. First busy signal? Try again in 1 second. 
Still busy? Wait 2 seconds. Then 4, 8, 16... Eventually you get through 
without overwhelming their phone system.

### Visual Metaphor
### Exponential Backoff Visualization
### Thundering Herd Prevention
### Core Insight
<div class="axiom-box">
<h4>⚛️ Without Jitter = Thundering Herd</h4>

All clients retry at exactly 1s, 2s, 4s → synchronized storm → service dies.

**With Jitter**: Clients spread across 0.8-1.2s, 1.6-2.4s → gradual recovery.
</div>

### Key Formula
**Implementation Concept:** See production systems for actual code

### Architecture Components
| Component | Purpose | Typical Values |
|-----------|---------|----------------|
| Base delay | Starting wait time | 100-1000ms |
| Multiplier | Growth factor | 2 (exponential) |
| Jitter | Randomization | ±25% of delay |
| Max retries | Failure limit | 3-5 attempts |
| Max delay | Cap on wait time | 30-60 seconds |

### Basic Implementation
### Comparison of Strategies
| Strategy | Delay Pattern | Use Case | Thundering Herd Risk |
|----------|---------------|----------|---------------------|
| Fixed | 1s, 1s, 1s | Predictable outages | High |
| Linear | 1s, 2s, 3s | Gradual recovery | Medium |
| Exponential | 1s, 2s, 4s, 8s | Unknown duration | Low (with jitter) |
| Decorrelated | Random based on previous | AWS recommended | Lowest |

### Retry Decision Tree
### Retry Strategy Comparison
### Common Pitfalls

<div class="failure-vignette">
<h4>💥 The Retry Storm of 2019</h4>

A major e-commerce platform experienced a 15-minute database slowdown. Without jitter, 
all 10,000 application servers retried at exactly 1s, 2s, 4s intervals. The synchronized 
retry waves created 10x normal load, turning a minor slowdown into a 3-hour outage.

**Lesson**: Always add jitter. Always.
</div>

#### Circuit Breaker Integration
<details>
<summary>📄 View python code (6 lines)</summary>

**Concept:** See production implementations

</details>

#### Retry Budget
**Process Overview:** See production implementations for details

<details>
<summary>📄 View implementation code</summary>

class RetryBudget:
**Implementation available in production systems**

</details>

### Production Strategies

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| Circuit Breaker Integration | Repeated failures | Skip retries when circuit open |
| Adaptive Retry | Variable load | Adjust based on success rate |
| Priority-based | Mixed importance | High-priority gets more retries |
| Hedged Requests | Low latency critical | Parallel retry before timeout |
| Retry Budget | Prevent overload | Limit retry overhead to 10% |

#### AWS SDK Approach
#### Netflix Resilience4j
<details>
<summary>📄 View java code (9 lines)</summary>

**Concept:** See production implementations

</details>

### Monitoring & Observability
#### Intelligent Error Classification
**Process Overview:** See production implementations for details

<details>
<summary>📄 View implementation code</summary>

class RetryClassifier:
**Implementation available in production systems**

</details>

#### Production-Grade Implementation
**Process Overview:** See production implementations for details

<details>
<summary>📄 View implementation code</summary>

class ProductionRetryClient:
**Implementation available in production systems**

</details>

### Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 3 | Moderate complexity with backoff algorithms, jitter, and retry classification |
| **Performance Impact** | 4 | Excellent recovery from transient failures with minimal overhead when implemented correctly |
| **Operational Overhead** | 3 | Requires monitoring retry rates, tuning backoff parameters, and preventing retry storms |
| **Team Expertise Required** | 3 | Understanding of failure types, backoff strategies, and distributed systems timing |
| **Scalability** | 5 | Essential for scalable systems - prevents cascade failures and enables graceful degradation |

**Overall Recommendation**: ✅ **RECOMMENDED** - Gold standard pattern essential for any distributed system dealing with transient failures.

## Related Laws

This pattern directly addresses several fundamental distributed systems laws:

- **[Law 2: Asynchronous Reality](../../core-principles/laws/asynchronous-reality/index.md)**: Retries handle the reality that network delays and processing times are unpredictable, and temporary failures are inevitable in distributed systems
- **[Law 3: Emergent Chaos](../../core-principles/laws/emergent-chaos/index.md)**: Without proper backoff, synchronized retries can create thundering herds and retry storms that amplify system chaos rather than resolve it
- **[Law 4: Multidimensional Optimization](../../core-principles/laws/multidimensional-optimization/index.md)**: Retry strategies embody trade-offs between availability (retry more), latency (retry less), and system load (careful backoff)
- **[Law 7: Economic Reality](../../core-principles/laws/economic-reality/index.md)**: Proper retry patterns prevent wasted resources while maximizing successful operations, directly impacting system costs and efficiency

### Migration Strategy

**Process Steps:**
- Initialize system
- Process requests
- Handle responses
- Manage failures

