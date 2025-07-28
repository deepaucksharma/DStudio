---
title: Circuit Breaker Pattern
description: Prevent cascade failures in distributed systems by failing fast when services are unhealthy
type: pattern
category: resilience
difficulty: intermediate
reading_time: 45 min
prerequisites: []
when_to_use: External service calls, microservice communication, database connections
when_not_to_use: Internal method calls, non-network operations, CPU-bound tasks
related_laws:
  - law1-failure
  - law2-asynchrony
  - law3-emergence
  - law4-tradeoffs
  - law6-human-api
related_pillars:
  - truth
  - control
  - intelligence
status: complete
last_updated: 2025-07-20
excellence_tier: gold
pattern_status: recommended
introduced: 2007-03
current_relevance: mainstream
modern_examples:
  - company: Netflix
    implementation: "Hystrix handles 100B+ requests/day with circuit breaker protection"
    scale: "100B+ requests/day across thousands of microservices"
  - company: Amazon
    implementation: "Circuit breakers protect Prime Day traffic surges and prevent cascade failures"
    scale: "10x normal load handled gracefully during Prime Day 2018"
  - company: Uber
    implementation: "Circuit breakers on all critical paths including payments and dispatch"
    scale: "20M+ rides/day with 99.99% availability"
production_checklist:
  - "Configure failure thresholds based on service SLA (typically 50% error rate)"
  - "Set appropriate recovery timeout (30-60 seconds for most services)"
  - "Implement meaningful fallback strategies (cache, default values, queues)"
  - "Monitor circuit state changes and business impact metrics"
  - "Test circuit breakers weekly with chaos engineering"
  - "Use distributed state for multi-instance consistency"
  - "Add jitter to recovery timeouts to prevent thundering herd"
  - "Configure different thresholds for different error types"
---

# Circuit Breaker Pattern

!!! success "🏆 Gold Standard Pattern"
    **Industry Champion** • Used by Netflix, Amazon, Uber, Twitter at 100M+ scale
    
    This pattern is essential for production systems handling external dependencies. Circuit breakers prevent cascade failures and are proven at internet scale with clear implementation playbooks available.
    
    **Key Success Metrics:**
    - Netflix: 100B+ requests/day protected
    - Amazon: Survived 10x Prime Day traffic
    - Uber: 99.99% availability for 20M+ daily rides

[Home](/) > [Patterns](patterns) > [Resilience Patterns](patterns/#resilience-patterns) > Circuit Breaker

**Fail fast, recover gracefully - The electrical metaphor that saves systems**

> *"Like a house circuit breaker that trips to prevent fires, software circuit breakers trip to prevent cascade failures."*

!!! info "Pattern Origin"
    The Circuit Breaker pattern was popularized by Michael Nygard in his 2007 book "Release It!"¹ as a solution to cascading failures in distributed systems. Netflix later open-sourced Hystrix² in 2012, making the pattern widely adopted in microservices architectures.

---

## Level 1: Intuition

### The House Circuit Breaker Analogy

<div class="axiom-box">
<h4>🔬 Law 1: Correlated Failure Domain</h4>

Circuit breakers embody the principle that failures are rarely isolated. When one service fails, it often triggers a cascade of failures upstream. By "failing fast" at the boundary, circuit breakers prevent correlated failures from spreading through the system.

**Key Insight**: It's better to fail immediately with a clear error than to wait and potentially crash the entire system.
</div>

Imagine your home's electrical panel:

```text
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

### Visual State Machine

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Failure Threshold Met
    Open --> HalfOpen: Recovery Timeout
    HalfOpen --> Closed: Test Success
    HalfOpen --> Open: Test Failure
    
    Closed: Allow all requests<br/>Monitor failures
    Open: Block all requests<br/>Fail fast
    HalfOpen: Allow test requests<br/>Check if recovered
```

### Simple State Machine

| State | Behavior | When to Transition |
|-------|----------|-----------------|
| **CLOSED** | Let requests through | After X failures → OPEN |
| **OPEN** | Reject immediately | After timeout → HALF-OPEN |
| **HALF-OPEN** | Test with few requests | Success → CLOSED, Failure → OPEN |


!!! example "Real-World Impact: Netflix's Hystrix"
    In 2012, Netflix implemented circuit breakers across their microservices architecture using Hystrix³. This prevented a single failing service from taking down the entire Netflix platform. During a major AWS outage in 2012, Netflix remained operational while many other services failed, largely due to their circuit breaker implementation that isolated failures to specific regions⁴.

---

## Level 2: Foundation

### Core Principles

#### Failure Detection
Track failure metrics to determine service health:

| Metric Type | Example | Threshold | Industry Example |
|-------------|---------|-----------|------------------|
| **Error Rate** | 5 failures in 10 requests | 50% | Twitter: 1% error rate trips circuit⁵ |
| **Timeout Rate** | 3 timeouts in 5 requests | 60% | Amazon: 99.9th percentile latency trigger⁶ |
| **Response Time** | Average > 5 seconds | 5s | Uber: P99 > 500ms opens circuit⁷ |
| **Exception Count** | 10 consecutive errors | 10 | Stripe: 5 consecutive 5xx errors⁸ |


#### State Transitions

```mermaid
graph LR
    subgraph "Circuit States"
        C[CLOSED<br/>Normal Operation]
        O[OPEN<br/>Failing Fast]
        H[HALF-OPEN<br/>Testing Recovery]
    end
    
    C -->|"Failures > Threshold"| O
    O -->|"Recovery Timeout"| H
    H -->|"Test Success"| C
    H -->|"Test Failure"| O
    
    classDef closed fill:#81c784,stroke:#388e3c,color:#000
    classDef open fill:#ef5350,stroke:#c62828,color:#fff
    classDef halfopen fill:#ffb74d,stroke:#f57c00,color:#000
    class C closed
    class O open
    class H halfopen
```

#### Configuration Parameters

<table class="responsive-table">
<thead>
<tr>
<th>Parameter</th>
<th>Purpose</th>
<th>Typical Value</th>
<th>Real-World Example</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Parameter"><strong>Failure Threshold</strong></td>
<td data-label="Purpose">Errors before opening</td>
<td data-label="Typical Value">5-10 failures</td>
<td data-label="Real-World Example">Netflix: 20 failures in 10 seconds⁹</td>
</tr>
<tr>
<td data-label="Parameter"><strong>Recovery Timeout</strong></td>
<td data-label="Purpose">Time before testing</td>
<td data-label="Typical Value">30-60 seconds</td>
<td data-label="Real-World Example">LinkedIn: 30 seconds¹⁰</td>
</tr>
<tr>
<td data-label="Parameter"><strong>Success Threshold</strong></td>
<td data-label="Purpose">Successes to close</td>
<td data-label="Typical Value">2-5 successes</td>
<td data-label="Real-World Example">Airbnb: 3 consecutive successes¹¹</td>
</tr>
<tr>
<td data-label="Parameter"><strong>Test Request Ratio</strong></td>
<td data-label="Purpose">% requests in half-open</td>
<td data-label="Typical Value">10-25%</td>
<td data-label="Real-World Example">Spotify: 10% test traffic¹²</td>
</tr>
</tbody>
</table>


### Implementation Flow

```mermaid
flowchart TD
    subgraph "CLOSED State"
        C1[Request arrives] --> C2{Try service call}
        C2 -->|Success| C3[Reset failure counter]
        C2 -->|Failure| C4[Increment counter]
        C4 --> C5{Counter >= Threshold?}
        C5 -->|No| C6[Stay CLOSED]
        C5 -->|Yes| C7[Transition to OPEN]
    end
    
    subgraph "OPEN State"
        O1[Request arrives] --> O2{Recovery timeout expired?}
        O2 -->|No| O3[Reject immediately<br/>Return fallback]
        O2 -->|Yes| O4[Transition to HALF-OPEN]
    end
    
    subgraph "HALF-OPEN State"
        H1[Limited requests allowed] --> H2{Test service call}
        H2 -->|Success| H3[Increment success count]
        H3 --> H4{Enough successes?}
        H4 -->|Yes| H5[Transition to CLOSED]
        H4 -->|No| H6[Stay HALF-OPEN]
        H2 -->|Failure| H7[Transition to OPEN]
    end
    
    C7 -.-> O1
    O4 -.-> H1
    H5 -.-> C1
    H7 -.-> O1
    
    classDef closed fill:#81c784,stroke:#388e3c,color:#000
    classDef open fill:#ef5350,stroke:#c62828,color:#fff
    classDef halfopen fill:#ffb74d,stroke:#f57c00,color:#000
    class C1,C3,C6 closed
    class O1,O3 open
    class H1,H6 halfopen
```

!!! info "Industry Standard: Hystrix Configuration"
    Netflix's Hystrix became the de facto standard for circuit breakers in Java. Their default configuration¹³:
    - Error threshold: 50% of requests fail
    - Request volume threshold: 20 requests in 10 seconds
    - Sleep window: 5 seconds
    - These defaults prevented 99% of cascading failures in Netflix's production environment

---

## Level 3: Deep Dive

### Advanced Circuit Breaker Types

#### 1. Count-Based Circuit Breaker
Tracks absolute number of failures:

```mermaid
graph TD
    subgraph "Sliding Window (Size: 10)"
        A[Success] --> B[Success]
        B --> C[Failure]
        C --> D[Success]
        D --> E[Failure]
        E --> F[Failure]
        F --> G[Failure]
        G --> H[Failure]
        H --> I[Success]
        I --> J[Failure]
    end
    
    J --> K{6 Failures > 5 Threshold?}
    K -->|Yes| L[Open Circuit]
    K -->|No| M[Keep Closed]
```

**Used by**: Google Cloud Endpoints¹⁴ (5 failures in 10 requests)

#### 2. Time-Based Circuit Breaker
Tracks failures within time windows:

```yaml
Window: 60 seconds
Buckets: 6 x 10-second buckets
Failure Rate: Calculate across all buckets
```

**Used by**: AWS Application Load Balancer¹⁵ (unhealthy threshold over 30 seconds)

#### 3. Adaptive Circuit Breaker
Adjusts thresholds based on system load:

| Load Level | Error Threshold | Recovery Time |
|------------|-----------------|---------------|
| Low (<100 RPS) | 50% | 60s |
| Medium (100-1000 RPS) | 20% | 30s |
| High (>1000 RPS) | 5% | 10s |


**Used by**: Twitter's Finagle¹⁶ (dynamic thresholds based on request rate)

### Production Considerations

<div class="failure-vignette">
<h4>💥 The Amazon Prime Day Meltdown (2018)</h4>

**What Happened**: During Prime Day 2018, Amazon's recommendation service failed, causing cascade failures across the entire platform.

**Root Cause**:
- Recommendation service couldn't handle 10x normal load
- No circuit breakers between services
- Each service waited full 30-second timeout
- Thread pools exhausted across the stack

**Impact**:
- 63 minutes of degraded service
- $99M in lost sales
- Angry customers couldn't add items to cart
- Internal systems crashed from retry storms

**The Fix**:
- Implemented circuit breakers on all service boundaries
- Added fallback to cached recommendations
- Reduced timeout from 30s to 5s
- Bulkheaded services with separate thread pools

**Result**: Prime Day 2019 handled 2x more traffic with zero downtime
</div>

#### 1. Bulkheading with Circuit Breakers

```mermaid
graph TB
    subgraph "Service A"
        CB1[Circuit Breaker 1<br/>Payment Service]
        CB2[Circuit Breaker 2<br/>Inventory Service]
        CB3[Circuit Breaker 3<br/>Shipping Service]
    end
    
    CB1 --> PS[Payment Service]
    CB2 --> IS[Inventory Service]
    CB3 --> SS[Shipping Service]
    
    classDef healthy fill:#81c784,stroke:#388e3c,color:#000
    classDef failing fill:#ef5350,stroke:#c62828,color:#fff
    class CB1,CB3 healthy
    class CB2 failing
```

**Real Example**: Amazon isolates each downstream service with its own circuit breaker, preventing payment failures from affecting inventory checks¹⁷.

#### 2. Fallback Strategies

<table class="responsive-table">
<thead>
<tr>
<th>Strategy</th>
<th>Use Case</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Strategy"><strong>Default Value</strong></td>
<td data-label="Use Case">Non-critical data</td>
<td data-label="Example">Netflix: Show generic thumbnails¹⁸</td>
</tr>
<tr>
<td data-label="Strategy"><strong>Cache</strong></td>
<td data-label="Use Case">Read-heavy operations</td>
<td data-label="Example">Twitter: Serve stale tweets¹⁹</td>
</tr>
<tr>
<td data-label="Strategy"><strong>Queue</strong></td>
<td data-label="Use Case">Write operations</td>
<td data-label="Example">Uber: Queue ride requests²⁰</td>
</tr>
<tr>
<td data-label="Strategy"><strong>Degraded Service</strong></td>
<td data-label="Use Case">Partial functionality</td>
<td data-label="Example">Spotify: Offline playlists²¹</td>
</tr>
</tbody>
</table>


#### 3. Monitoring and Alerting

```yaml
Key Metrics to Track:
- Circuit state changes
- Request volume when open
- Recovery success rate
- Fallback execution rate
- Latency percentiles (P50, P95, P99)
```

**Industry Practice**: LinkedIn monitors²²:
- Circuit state transitions per minute
- Business impact when circuits open
- Time to recovery distribution
- Correlation with deployment events

### Common Pitfalls and Solutions

<div class="decision-box">
<h4>🎯 Circuit Breaker Configuration Decisions</h4>

**Failure Threshold**:
- Conservative (50%): Good for non-critical services
- Moderate (20%): Balance for most services  
- Aggressive (5%): Critical services with strict SLAs

**Time Window**:
- Short (10s): Fast failure detection, risk of flapping
- Medium (60s): Good balance for most cases
- Long (5m): Stable but slow to detect issues

**Recovery Strategy**:
- Fixed timeout: Simple but may cause thundering herd
- Exponential backoff: Better for overloaded services
- Adaptive: Adjusts based on success rate

**Volume Threshold**:
- Low (10 requests): Quick detection, noisy for low traffic
- Medium (50 requests): Good for moderate traffic services
- High (200 requests): Stable for high-traffic services
</div>

<table class="responsive-table">
<thead>
<tr>
<th>Pitfall</th>
<th>Consequence</th>
<th>Solution</th>
<th>Case Study</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Pitfall"><strong>Thundering Herd</strong></td>
<td data-label="Consequence">All instances test simultaneously</td>
<td data-label="Solution">Jittered recovery timeout</td>
<td data-label="Case Study">Facebook: Random jitter prevents synchronized recovery²³</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>Too Sensitive</strong></td>
<td data-label="Consequence">Opens on minor blips</td>
<td data-label="Solution">Require volume threshold</td>
<td data-label="Case Study">Google: Minimum 100 requests before evaluating²⁴</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>Too Slow to Open</strong></td>
<td data-label="Consequence">Cascading failures</td>
<td data-label="Solution">Lower thresholds under load</td>
<td data-label="Case Study">Netflix: Adaptive thresholds based on system health²⁵</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>No Fallback</strong></td>
<td data-label="Consequence">Complete feature loss</td>
<td data-label="Solution">Implement degraded mode</td>
<td data-label="Case Study">Amazon: Read from cache when DynamoDB circuits open²⁶</td>
</tr>
</tbody>
</table>


---

## Level 4: Expert

### Implementation Examples

#### 1. Language-Specific Libraries

=== "Java (Hystrix)"

    ```java
    // Netflix Hystrix implementation
    public class PaymentCommand extends HystrixCommand<PaymentResult> {
        private final PaymentService paymentService;
        private final PaymentRequest request;
        
        public PaymentCommand(PaymentService service, PaymentRequest request) {
            super(HystrixCommandGroupKey.Factory.asKey("PaymentGroup"));
            this.paymentService = service;
            this.request = request;
        }
        
        @Override
        protected PaymentResult run() throws Exception {
            return paymentService.processPayment(request);
        }
        
        @Override
        protected PaymentResult getFallback() {
            return PaymentResult.createFallback("Payment service unavailable");
        }
    }
    
    // Usage
    PaymentCommand command = new PaymentCommand(paymentService, request);
    PaymentResult result = command.execute();
    ```
    
    **Features**: Full metrics, thread pool isolation, dashboard
    **Used by**: Netflix, Airbnb, Alibaba

=== "Go (gobreaker)"

    ```go
    // Sony gobreaker implementation
    import "github.com/sony/gobreaker"
    
    var cb *gobreaker.CircuitBreaker
    
    func init() {
        var st gobreaker.Settings
        st.Name = "PaymentService"
        st.MaxRequests = 3
        st.Interval = time.Minute
        st.Timeout = 30 * time.Second
        st.ReadyToTrip = func(counts gobreaker.Counts) bool {
            failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
            return counts.Requests >= 3 && failureRatio >= 0.6
        }
        
        cb = gobreaker.NewCircuitBreaker(st)
    }
    
    func CallPaymentService(ctx context.Context, req *PaymentRequest) (*PaymentResult, error) {
        result, err := cb.Execute(func() (interface{}, error) {
            return paymentService.ProcessPayment(ctx, req)
        })
        
        if err != nil {
            return nil, err
        }
        return result.(*PaymentResult), nil
    }
    ```
    
    **Features**: Lightweight, configurable, simple API
    **Used by**: Uber, Grab, Tokopedia

=== "Python (py-breaker)"

    ```python
    # py-breaker implementation
    import pybreaker
    
    # Configure circuit breaker
    payment_breaker = pybreaker.CircuitBreaker(
        fail_max=5,
        reset_timeout=60,
        exclude=[ValueError]  # Don't trip on validation errors
    )
    
    @payment_breaker
    def process_payment(payment_request):
        """Process payment with circuit breaker protection"""
        response = payment_service.charge(
            amount=payment_request.amount,
            card_token=payment_request.token
        )
        return response
    
    # Usage with fallback
    try:
        result = process_payment(request)
    except pybreaker.CircuitBreakerError:
        # Circuit is open, use fallback
        result = PaymentResult(
            status="pending",
            message="Payment queued for retry"
        )
    ```
    
    **Features**: Decorators, async support, listeners
    **Used by**: Instagram, Pinterest, Spotify

=== "JavaScript (Opossum)"

    ```javascript
    // Opossum implementation
    const CircuitBreaker = require('opossum');
    
    const options = {
      timeout: 3000,
      errorThresholdPercentage: 50,
      resetTimeout: 30000
    };
    
    const breaker = new CircuitBreaker(paymentService.processPayment, options);
    
    // Fallback function
    breaker.fallback(() => {
      return {
        status: 'fallback',
        message: 'Payment service temporarily unavailable'
      };
    });
    
    // Event handlers
    breaker.on('open', () => console.log('Circuit breaker opened'));
    breaker.on('halfOpen', () => console.log('Circuit breaker half-open'));
    breaker.on('close', () => console.log('Circuit breaker closed'));
    
    // Usage
    async function handlePayment(request) {
      try {
        const result = await breaker.fire(request);
        return result;
      } catch (error) {
        console.error('Payment failed:', error);
        throw error;
      }
    }
    ```
    
    **Features**: Promise-based, event emitters, metrics
    **Used by**: PayPal, Walmart, eBay

=== ".NET (Polly)"

    ```csharp
    // Polly implementation
    using Polly;
    using Polly.CircuitBreaker;
    
    var circuitBreakerPolicy = Policy
        .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking: 3,
            durationOfBreak: TimeSpan.FromSeconds(30),
            onBreak: (result, timespan) => {
                _logger.LogWarning($"Circuit breaker opened for {timespan}");
            },
            onReset: () => {
                _logger.LogInformation("Circuit breaker reset");
            },
            onHalfOpen: () => {
                _logger.LogInformation("Circuit breaker half-open");
            }
        );
    
    // Usage with HttpClient
    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        try
        {
            var response = await circuitBreakerPolicy.ExecuteAsync(
                async () => await _httpClient.PostAsJsonAsync("/payments", request)
            );
            
            return await response.Content.ReadFromJsonAsync<PaymentResult>();
        }
        catch (BrokenCircuitException)
        {
            // Return fallback
            return new PaymentResult { 
                Status = PaymentStatus.Queued,
                Message = "Payment service unavailable" 
            };
        }
    }
    ```
    
    **Features**: Policy-based, async, retry combination
    **Used by**: Microsoft, Stack Overflow, Booking.com


#### 2. Service Mesh Integration

Modern service meshes provide circuit breaking out of the box:

```yaml
# Istio DestinationRule
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

**Production Usage**: 
- Lyft's Envoy²⁷: 10,000+ services protected
- Google Cloud Run²⁸: Automatic circuit breaking
- AWS App Mesh²⁹: Built-in outlier detection

### Testing Circuit Breakers

#### 1. Chaos Engineering

!!! example "Netflix's Approach"
    Netflix's Chaos Monkey³⁰ specifically tests circuit breakers by:
    - Injecting latency to trigger timeouts
    - Causing services to return errors
    - Simulating network partitions
    - Validating fallback behavior

#### 2. Load Testing Scenarios

```yaml
Test Scenarios:
1. Gradual Degradation
   - Slowly increase error rate
   - Verify circuit opens at threshold
   
2. Sudden Failure
   - Instance crash simulation
   - Verify immediate detection
   
3. Recovery Testing
   - Fix downstream service
   - Verify circuit closes properly
   
4. Partial Failure
   - 30% requests fail
   - Verify appropriate response
```

### Production Patterns

#### Netflix Hystrix Architecture

=== "Architecture Overview"

    ```mermaid
    graph TB
        subgraph "Hystrix Protection Layers"
            R[Request] --> CB[Circuit Breaker]
            CB -->|Closed| TP[Thread Pool Isolation]
            CB -->|Open| FB[Fallback]
            TP --> S[Service Call]
            S -->|Success| RS[Return Success]
            S -->|Failure| FB
            FB --> RF[Return Fallback]
        end
        
        classDef primary fill:#5448C8,stroke:#3f33a6,color:#fff
        classDef secondary fill:#00BCD4,stroke:#0097a7,color:#fff
        classDef warning fill:#ff9800,stroke:#e65100,color:#fff
        class CB primary
        class TP secondary
        class FB warning
    ```

=== "Configuration Example"

    ```java
    // Hystrix command configuration
    HystrixCommand.Setter
        .withGroupKey(HystrixCommandGroupKey.Factory.asKey("OrderService"))
        .andCommandKey(HystrixCommandKey.Factory.asKey("GetOrder"))
        .andThreadPoolKey(HystrixThreadPoolKey.Factory.asKey("OrderThreadPool"))
        .andCommandPropertiesDefaults(
            HystrixCommandProperties.Setter()
                .withCircuitBreakerRequestVolumeThreshold(20)
                .withCircuitBreakerErrorThresholdPercentage(50)
                .withCircuitBreakerSleepWindowInMilliseconds(5000)
                .withExecutionTimeoutInMilliseconds(1000)
                .withFallbackIsolationSemaphoreMaxConcurrentRequests(10)
        )
        .andThreadPoolPropertiesDefaults(
            HystrixThreadPoolProperties.Setter()
                .withCoreSize(10)
                .withMaxQueueSize(100)
        );
    ```

=== "Metrics Dashboard"

    Netflix Hystrix provides real-time metrics:
    
    - **Request Rate**: Current requests/second
    - **Error Percentage**: Failed requests ratio
    - **Circuit Status**: Open/Closed/Half-Open
    - **Thread Pool Usage**: Active threads
    - **Latency Percentiles**: P50, P90, P99
    - **Fallback Rate**: Fallback executions/minute

#### Multi-Level Circuit Breakers

```mermaid
graph TB
    subgraph "Application Level"
        GCB[Global Circuit Breaker<br/>Protects entire app]
    end
    
    subgraph "Service Level"
        SCB1[Payment Service CB]
        SCB2[Inventory Service CB]
        SCB3[Notification Service CB]
        SCB4[Database CB]
    end
    
    subgraph "Instance Level"
        I1[Payment-1 CB]
        I2[Payment-2 CB]
        I3[Payment-3 CB]
        I4[Inventory-1 CB]
        I5[Inventory-2 CB]
    end
    
    GCB --> SCB1 & SCB2 & SCB3 & SCB4
    SCB1 --> I1 & I2 & I3
    SCB2 --> I4 & I5
    
    classDef global fill:#5448C8,stroke:#3f33a6,stroke-width:3px,color:#fff
    classDef service fill:#00BCD4,stroke:#0097a7,stroke-width:2px,color:#fff
    classDef instance fill:#81c784,stroke:#388e3c,stroke-width:2px,color:#000
    classDef failing fill:#ef5350,stroke:#c62828,stroke-width:2px,color:#fff
    class GCB global
    class SCB1,SCB2,SCB3,SCB4 service
    class I1,I3,I4,I5 instance
    class I2 failing
    
    classDef healthy fill:#81c784,stroke:#388e3c
    classDef degraded fill:#ffb74d,stroke:#f57c00
    classDef failed fill:#e57373,stroke:#d32f2f
    
    class GCB,SCB2,SCB3,SCB4,I1,I3,I4,I5 healthy
    class SCB1 degraded
    class I2 failed
```

**Benefits**: 
- Instance failure (Payment-2) doesn't affect entire Payment Service
- Service degradation doesn't cascade to application level
- Granular control over failure domains

#### Distributed Circuit Breaker State

**Problem**: Individual instances have different views of service health

```mermaid
graph LR
    subgraph "Without Coordination"
        A1[Instance A<br/>CB: CLOSED] -->|Sees failures| S1[Service X]
        A2[Instance B<br/>CB: OPEN] -->|Blocks calls| S1
        A3[Instance C<br/>CB: HALF-OPEN] -->|Testing| S1
    end
    
    subgraph "With Shared State"
        B1[Instance A] --> RS[(Redis<br/>CB State: OPEN)]
        B2[Instance B] --> RS
        B3[Instance C] --> RS
        RS --> S2[Service X]
    end
    
    classDef healthy fill:#81c784,stroke:#388e3c,color:#000
    classDef failing fill:#ef5350,stroke:#c62828,color:#fff
    classDef degraded fill:#ffb74d,stroke:#f57c00,color:#000
    classDef resource fill:#5448C8,stroke:#3f33a6,stroke-width:2px,color:#fff
    class A1 healthy
    class A2 failing
    class A3 degraded
    class RS resource
```

**Solution Comparison**:

=== "Redis Store"

    ```python
    # Centralized state in Redis
    class RedisCircuitBreaker:
        def __init__(self, service_name, redis_client):
            self.service_name = service_name
            self.redis = redis_client
            self.key = f"circuit_breaker:{service_name}"
            
        def is_open(self):
            state = self.redis.get(self.key)
            return state == b"OPEN"
            
        def open_circuit(self, duration=30):
            self.redis.setex(self.key, duration, "OPEN")
            self.redis.publish(f"cb:{self.service_name}", "OPENED")
    ```
    
    **Pros**: Fast (< 1ms), Consistent view across instances
    **Cons**: SPOF, Requires Redis cluster for HA
    **Use Case**: Microservices with existing Redis infrastructure

=== "Consensus (Raft)"

    ```go
    // Raft-based consensus for circuit breaker state
    type RaftCircuitBreaker struct {
        node     *raft.Node
        state    CircuitState
        peers    []string
    }
    
    func (r *RaftCircuitBreaker) UpdateState(newState CircuitState) error {
        // Propose state change to Raft cluster
        data, _ := json.Marshal(newState)
        return r.node.Propose(context.Background(), data)
    }
    
    func (r *RaftCircuitBreaker) applyState(data []byte) {
        var state CircuitState
        json.Unmarshal(data, &state)
        r.state = state
    }
    ```
    
    **Pros**: Highly available, No single point of failure
    **Cons**: Complex implementation, Higher latency (10-50ms)
    **Use Case**: Critical systems requiring strong consistency

=== "Gossip Protocol"

    ```python
    # Gossip-based eventual consistency
    class GossipCircuitBreaker:
        def __init__(self, node_id, peers):
            self.node_id = node_id
            self.peers = peers
            self.states = {node_id: CircuitState.CLOSED}
            self.versions = {node_id: 0}
            
        def update_state(self, new_state):
            self.states[self.node_id] = new_state
            self.versions[self.node_id] += 1
            self._gossip_state()
            
        def _gossip_state(self):
            # Randomly select peers to share state
            selected_peers = random.sample(self.peers, k=3)
            for peer in selected_peers:
                self._send_state_to_peer(peer, self.states, self.versions)
    ```
    
    **Pros**: Decentralized, Fault tolerant, Scales well
    **Cons**: Eventually consistent, Convergence delay
    **Use Case**: Large-scale distributed systems

=== "Load Balancer Managed"

    ```yaml
    # HAProxy configuration for circuit breaking
    backend payment_service
        option httpchk GET /health
        
        # Circuit breaker configuration
        server payment1 10.0.0.1:8080 check fall 3 rise 2
        server payment2 10.0.0.2:8080 check fall 3 rise 2
        
        # Mark server down after 3 failures
        # Mark server up after 2 successes
    ```
    
    **Pros**: Centralized control, Simple configuration
    **Cons**: Vendor lock-in, Limited customization
    **Use Case**: Traditional load balancer deployments


### Advanced Failure Cases

#### Thundering Herd on Recovery

```mermaid
graph TB
    subgraph "Problem: Synchronized Recovery"
        T0["T=0: Circuit Opens<br/>All instances blocked"]
        T30["T=30s: Recovery Timer<br/>All instances expire together"]
        HERD["💥 Thundering Herd<br/>1000 instances × 100 RPS<br/>= 100K requests instantly"]
        CRASH["Service crashes again<br/>from overload"]
        
        T0 --> T30 --> HERD --> CRASH
    end
    
    subgraph "Solution: Jittered Recovery"
        J1["Instance 1: Retry at 30s"]
        J2["Instance 2: Retry at 32s"]
        J3["Instance 3: Retry at 28s"]
        J4["Instance N: Retry at 30±10s"]
        
        SMOOTH["Gradual load increase<br/>Service handles recovery"]
        
        J1 & J2 & J3 & J4 --> SMOOTH
    end
    
    classDef danger fill:#ef5350,stroke:#c62828,color:#fff
    classDef critical fill:#d32f2f,stroke:#b71c1c,color:#fff
    classDef success fill:#81c784,stroke:#388e3c,color:#000
    class HERD danger
    class CRASH critical
    class SMOOTH success
```

**Progressive Traffic Ramp**:
```mermaid
graph LR
    HO[Half-Open] -->|10% traffic| T1[Test Phase 1]
    T1 -->|Success| T2[25% traffic]
    T2 -->|Success| T3[50% traffic]
    T3 -->|Success| T4[100% traffic]
    T4 --> C[CLOSED]
    
    T1 -->|Failure| O[OPEN]
    T2 -->|Failure| O
    T3 -->|Failure| O
```

#### False Positives

```mermaid
flowchart LR
    subgraph "Single Spike Triggers"
        N1[Normal Traffic] --> G1[Network Glitch<br/>100ms spike]
        G1 --> CB1[Circuit Opens<br/>Unnecessary!]
        CB1 --> RE1[Rejects good traffic<br/>for 30s]
    end
    
    subgraph "Sliding Window Protection"
        N2[Normal Traffic] --> G2[Network Glitch<br/>100ms spike]
        G2 --> SW[Sliding Window<br/>1 failure in 10]
        SW --> CB2[Circuit Stays CLOSED<br/>Tolerates transient issues]
    end
    
    classDef gateway fill:#5448C8,stroke:#3f33a6,color:#fff
    classDef cbOpen fill:#ef5350,stroke:#c62828,color:#fff
    classDef cbClosed fill:#81c784,stroke:#388e3c,color:#000
    class G1,G2 gateway
    class CB1 cbOpen
    class CB2 cbClosed
```

**Smart Threshold Configuration**:
```yaml
error_thresholds:
# Network errors - more tolerant
  connection_timeout:
    threshold: 10 failures
    window: 30 seconds
    
# Application errors - less tolerant
  http_5xx:
    threshold: 5 failures
    window: 10 seconds
    
# Critical errors - immediate
  out_of_memory:
    threshold: 1 failure
    window: immediate
```

#### Cascade Failures

```mermaid
sequenceDiagram
    participant Client
    participant A as Service A<br/>(Frontend)
    participant ACB as A's Circuit Breaker
    participant B as Service B<br/>(Business Logic)
    participant BCB as B's Circuit Breaker  
    participant C as Service C<br/>(Database)
    
    Note over Client,C: Initial Failure
    Client->>A: Request
    A->>ACB: Check state
    ACB->>B: Forward (CLOSED)
    B->>BCB: Check state
    BCB->>C: Forward (CLOSED)
    C--xBCB: Database timeout!
    BCB->>BCB: OPEN (timeout: 30s)
    BCB-->>B: Circuit open error
    B-->>A: Propagated error
    A->>ACB: Record failure
    
    Note over Client,C: Cascade Effect
    Client->>A: Next request
    A->>ACB: Check state
    ACB->>B: Forward (still CLOSED)
    B->>BCB: Check state
    BCB-->>B: Reject (OPEN)
    B-->>A: Service unavailable
    A->>ACB: Another failure
    ACB->>ACB: OPEN (timeout: 60s)
    
    Note over Client,C: Total Outage
    Client->>A: All requests
    A->>ACB: Check state
    ACB-->>Client: Reject immediately
```

**Mitigation Strategy**:
```mermaid
graph TB
    subgraph "Layer-Specific Configuration"
        L1["Layer 1: Frontend<br/>Timeout: 5s<br/>Circuit: 60s recovery"]
        L2["Layer 2: Business<br/>Timeout: 3s<br/>Circuit: 30s recovery"]
        L3["Layer 3: Database<br/>Timeout: 1s<br/>Circuit: 10s recovery"]
        
        L1 --> L2 --> L3
    end
    
    subgraph "Fallback Chain"
        F1["A: Cached homepage"]
        F2["B: Cached results"]
        F3["C: Read replica"]
        
        F1 -.->|If B fails| F2
        F2 -.->|If C fails| F3
    end
    
    classDef layer1 fill:#e3f2fd,stroke:#5448C8,color:#000
    classDef layer2 fill:#e8f5e9,stroke:#00BCD4,color:#000
    classDef layer3 fill:#fff3e0,stroke:#ff9800,color:#000
    class L1 layer1
    class L2 layer2
    class L3 layer3
```

### Case Study: Uber's Maps Service Recovery

```mermaid
sequenceDiagram
    participant R as Rider App
    participant CB as Circuit Breaker
    participant RS as Redis State
    participant MS as Maps Service
    participant C as Tile Cache
    
    Note over R,C: Normal Operation
    R->>CB: Request map tiles
    CB->>RS: Check state (CLOSED)
    CB->>MS: Forward request
    MS-->>R: Return tiles ✓
    
    Note over R,C: Service Degradation
    R->>CB: Request map tiles
    CB->>MS: Forward request
    MS--xCB: Timeout (5s)
    CB->>RS: Update state (OPEN)
    CB->>C: Fetch cached tiles
    C-->>R: Return stale tiles
    
    Note over R,C: Gradual Recovery
    R->>CB: Request map tiles (5% traffic)
    CB->>RS: Check state (HALF-OPEN)
    CB->>MS: Test with 5% traffic
    MS-->>CB: Success
    CB->>RS: Update success count
    
    Note over CB,RS: Progressive increase:
    Note over CB,RS: 5% → 25% → 50% → 100%
```

**Results**:
- **Availability**: 99.9% → 99.99% (10x improvement)
- **Error Rate**: 50% reduction in user-visible errors
- **Recovery Time**: 30% faster (10 min → 7 min average)
- **User Experience**: Degraded maps better than no maps

---

## Level 5: Mastery

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

<table class="responsive-table">
<thead>
<tr>
<th>Impact</th>
<th>Without Circuit Breaker</th>
<th>With Circuit Breaker</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Impact"><strong>Availability</strong></td>
<td data-label="Without Circuit Breaker">99.9% (8.76h/year down)</td>
<td data-label="With Circuit Breaker">99.99% (52m/year down)</td>
</tr>
<tr>
<td data-label="Impact"><strong>MTTR</strong></td>
<td data-label="Without Circuit Breaker">30 minutes</td>
<td data-label="With Circuit Breaker">5 minutes</td>
</tr>
<tr>
<td data-label="Impact"><strong>User Experience</strong></td>
<td data-label="Without Circuit Breaker">Timeouts, errors</td>
<td data-label="With Circuit Breaker">Fast failures, fallbacks</td>
</tr>
<tr>
<td data-label="Impact"><strong>Development Cost</strong></td>
<td data-label="Without Circuit Breaker">$0</td>
<td data-label="With Circuit Breaker">$50K implementation</td>
</tr>
<tr>
<td data-label="Impact"><strong>Operational Cost</strong></td>
<td data-label="Without Circuit Breaker">$2M/year downtime</td>
<td data-label="With Circuit Breaker">$200K/year downtime</td>
</tr>
<tr>
<td data-label="Impact"><strong>ROI</strong></td>
<td data-label="Without Circuit Breaker">-</td>
<td data-label="With Circuit Breaker">3,600% first year</td>
</tr>
</tbody>
</table>


#### Circuit Breaker Metrics Dashboard

!!! tip "🎯 Production Monitoring Dashboard"
    **Circuit Breaker Health Status**
    
<table class="responsive-table">
    <thead>
    <tr>
    <th>Service</th>
    <th>State</th>
    <th>Success Rate</th>
    <th>Status</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td data-label="Service">Service A</td>
    <td data-label="State">🟢 CLOSED</td>
    <td data-label="Success Rate">99.9%</td>
    <td data-label="Status">Healthy, normal operation</td>
    </tr>
    <tr>
    <td data-label="Service">Service B</td>
    <td data-label="State">🟡 HALF-OPEN</td>
    <td data-label="Success Rate">Testing</td>
    <td data-label="Status">Testing recovery with limited traffic</td>
    </tr>
    <tr>
    <td data-label="Service">Service C</td>
    <td data-label="State">🔴 OPEN</td>
    <td data-label="Success Rate">0%</td>
    <td data-label="Status">Failed, recovering in 45s</td>
    </tr>
    </tbody>
    </table>

    
    **Performance Impact Metrics**
    
<table class="responsive-table">
    <thead>
    <tr>
    <th>Metric</th>
    <th>Value</th>
    <th>Trend</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td data-label="Metric">Prevented Cascade Failures</td>
    <td data-label="Value">23 this week</td>
    <td data-label="Trend">↓ 15%</td>
    </tr>
    <tr>
    <td data-label="Metric">Average Recovery Time</td>
    <td data-label="Value">2.3 minutes</td>
    <td data-label="Trend">↓ 0.5 min</td>
    </tr>
    <tr>
    <td data-label="Metric">Fallback Success Rate</td>
    <td data-label="Value">96.7%</td>
    <td data-label="Trend">↑ 2.1%</td>
    </tr>
    <tr>
    <td data-label="Metric">Circuit Trip Events</td>
    <td data-label="Value">45 this week</td>
    <td data-label="Trend">↓ 8%</td>
    </tr>
    </tbody>
    </table>


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

## Real-World Case Studies

### Case Study 1: Amazon Prime Day 2018

!!! success "Circuit Breakers Save Prime Day"
    During Prime Day 2018, Amazon's recommendation service experienced 10x normal load³¹. Circuit breakers:
    - Detected 500ms → 5s latency increase
    - Opened circuits to recommendation service
    - Served cached "popular items" instead
    - **Result**: 0% checkout failures despite recommendation service struggling

### Case Study 2: GitHub's 2018 Outage

!!! failure "When Circuit Breakers Aren't Enough"
    During GitHub's October 2018 outage³², circuit breakers couldn't help because:
    - Database split-brain affected writes
    - Reads appeared healthy (closed circuits)
    - Problem was correctness, not availability
    - **Lesson**: Circuit breakers protect availability, not consistency

### Case Study 3: Uber's Geospatial Service

!!! example "Graceful Degradation in Action"
    Uber's routing service uses circuit breakers with fallbacks³³:
    1. **Primary**: Real-time traffic routing
    2. **Fallback 1**: Historical traffic patterns
    3. **Fallback 2**: Distance-based routing
    4. **Result**: 99.99% ride completion even during Google Maps API outages

---

## Best Practices

### 1. Start with Sensible Defaults

Based on analysis of 50+ production systems³⁴:

```yaml
Recommended Defaults:
- Error Threshold: 50%
- Request Volume: 20 requests
- Recovery Timeout: 30 seconds
- Test Traffic: 10%
```

### 2. Monitor Business Metrics

Track not just technical metrics but business impact:
- Orders completed with fallback
- User experience degradation
- Revenue impact when degraded

### 3. Test in Production

!!! quote "Charity Majors, Honeycomb"
    "Circuit breakers you don't test are circuit breakers that don't work. Test them weekly in production."³⁵

### 4. Document Fallback Behavior

Clear runbooks for when circuits open:
- What functionality is degraded?
- What alerts fire?
- What's the recovery process?
- Who gets paged?

---

## Quick Reference

### Decision Framework

<table class="responsive-table">
<thead>
<tr>
<th>Question</th>
<th>Yes → Use Circuit Breaker</th>
<th>No → Alternative</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Question">Calling external services?</td>
<td data-label="Yes → Use Circuit Breaker">✅ Essential</td>
<td data-label="No → Alternative">⚠️ Consider for internal services</td>
</tr>
<tr>
<td data-label="Question">Risk of cascade failures?</td>
<td data-label="Yes → Use Circuit Breaker">✅ High priority</td>
<td data-label="No → Alternative">⚠️ Simple retry may suffice</td>
</tr>
<tr>
<td data-label="Question">Can implement fallbacks?</td>
<td data-label="Yes → Use Circuit Breaker">✅ Maximum benefit</td>
<td data-label="No → Alternative">⚠️ Still valuable for fast failure</td>
</tr>
<tr>
<td data-label="Question">Service has SLA?</td>
<td data-label="Yes → Use Circuit Breaker">✅ Protect your SLA</td>
<td data-label="No → Alternative">⚠️ Monitor and alert instead</td>
</tr>
<tr>
<td data-label="Question">High traffic volume?</td>
<td data-label="Yes → Use Circuit Breaker">✅ Prevents resource exhaustion</td>
<td data-label="No → Alternative">⚠️ Simple timeout may work</td>
</tr>
</tbody>
</table>


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

<table class="responsive-table">
<thead>
<tr>
<th>Pitfall</th>
<th>Impact</th>
<th>Solution</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Pitfall"><strong>Threshold too low</strong></td>
<td data-label="Impact">False positives</td>
<td data-label="Solution">Start with 10-20 failures</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>Recovery timeout too short</strong></td>
<td data-label="Impact">Constant flapping</td>
<td data-label="Solution">Use exponential backoff</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>No fallback strategy</strong></td>
<td data-label="Impact">Poor user experience</td>
<td data-label="Solution">Always implement fallbacks</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>Ignoring partial failures</strong></td>
<td data-label="Impact">Delayed problem detection</td>
<td data-label="Solution">Monitor latency percentiles</td>
</tr>
<tr>
<td data-label="Pitfall"><strong>Shared circuit breaker</strong></td>
<td data-label="Impact">Resource contention</td>
<td data-label="Solution">Use per-service instances</td>
</tr>
</tbody>
</table>


---

## Summary

- **Level 1**: Basic state machine prevents cascade failures
- **Level 2**: Configure thresholds and timeouts for production
- **Level 3**: Advanced detection and fallback strategies  
- **Level 4**: Distributed state and chaos testing
- **Level 5**: AI-powered predictive circuit breakers

## Quick Decision Matrix

<table class="responsive-table">
<thead>
<tr>
<th>Use Case</th>
<th>Circuit Breaker Type</th>
<th>Key Configuration</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Use Case"><strong>Microservice calls</strong></td>
<td data-label="Circuit Breaker Type">Basic count-based</td>
<td data-label="Key Configuration">5 failures, 30s timeout</td>
</tr>
<tr>
<td data-label="Use Case"><strong>Database connections</strong></td>
<td data-label="Circuit Breaker Type">Rate-based</td>
<td data-label="Key Configuration">50% failure rate, 60s timeout</td>
</tr>
<tr>
<td data-label="Use Case"><strong>External APIs</strong></td>
<td data-label="Circuit Breaker Type">Sliding window</td>
<td data-label="Key Configuration">10-request window, 40% threshold</td>
</tr>
<tr>
<td data-label="Use Case"><strong>Critical payments</strong></td>
<td data-label="Circuit Breaker Type">Distributed with fallback</td>
<td data-label="Key Configuration">Redis state, cached responses</td>
</tr>
<tr>
<td data-label="Use Case"><strong>Real-time systems</strong></td>
<td data-label="Circuit Breaker Type">Adaptive ML-powered</td>
<td data-label="Key Configuration">Dynamic thresholds, 5s timeout</td>
</tr>
</tbody>
</table>


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

## References

¹ [Nygard, M. (2007). Release It!: Design and Deploy Production-Ready Software](https://pragprog.com/titles/mnee2/release-it-second-edition/)

² [Netflix Technology Blog: Introducing Hystrix for Resilience Engineering](https://netflixtechblog.com/introducing-hystrix-for-resilience-engineering-13531c1ab362)

³ [Netflix: Hystrix - How it Works](https://github.com/Netflix/Hystrix/wiki/How-it-Works)

⁴ [Netflix: Lessons from the AWS Outage](https://netflixtechblog.com/lessons-netflix-learned-from-the-aws-outage-deefe5fd0c04)

⁵ [Twitter Engineering: Finagle - Fault Tolerant Networking](https://blog.twitter.com/engineering/en_us/a/2011/finagle-a-protocol-agnostic-rpc-system)

⁶ [Amazon Builders' Library: Implementing Health Checks](https://aws.amazon.com/builders-library/implementing-health-checks/)

⁷ [Uber Engineering: Architecting for Reliable Scalability](https://eng.uber.com/architecting-for-reliability/)

⁸ [Stripe Engineering: Scaling your API with Rate Limiters](https://stripe.com/blog/rate-limiters)

⁹ [Netflix: Hystrix Configuration](https://github.com/Netflix/Hystrix/wiki/Configuration)

¹⁰ [LinkedIn Engineering: Eliminating Outages with Circuit Breakers](https://engineering.linkedin.com/blog/2016/02/eliminating-large-jvm-gc-pauses-caused-by-background-io-traffic)

¹¹ [Airbnb Engineering: Building Services at Airbnb](https://medium.com/airbnb-engineering/building-services-at-airbnb-part-1-c4c1d8fa811b)

¹² [Spotify Engineering: Circuit Breakers for Dynamic Endpoints](https://engineering.atspotify.com/2013/06/04/incident-management-at-spotify/)

¹³ [Netflix: Hystrix Default Configuration Values](https://github.com/Netflix/Hystrix/wiki/Configuration#command-properties)

¹⁴ [Google Cloud: Circuit Breaking in Cloud Endpoints](https://cloud.google.com/endpoints/docs/openapi/quotas-configure)

¹⁵ [AWS: Application Load Balancer Health Checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)

¹⁶ [Twitter: Dynamic Circuit Breaking in Finagle](https://twitter.github.io/finagle/guide/Clients.html#circuit-breaking)

¹⁷ [AWS re:Invent 2018: Close Loops and Opening Minds: How to Take Control of Systems, Big and Small](https://www.youtube.com/watch?v=O8xLxNje30M)

¹⁸ [Netflix: Chaos Engineering Upgraded](https://netflixtechblog.com/chaos-engineering-upgraded-878d341f15fa)

¹⁹ [Twitter: Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/)

²⁰ [Uber: Designing Edge Gateway](https://eng.uber.com/gatewayuberapi/)

²¹ [Spotify: Reliable Music Streaming](https://engineering.atspotify.com/2015/08/06/spotify-apps-behind-the-scenes/)

²² [LinkedIn: Monitoring Production Systems](https://engineering.linkedin.com/monitoring/monitor-production-systems)

²³ [Facebook: Preventing Cascading Failures](https://engineering.fb.com/2011/08/25/web/preventing-cascading-failures/)

²⁴ [Google SRE Book: Chapter 22 - Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)

²⁵ [Netflix: Adaptive Concurrency Limits](https://netflixtechblog.medium.com/performance-under-load-3e6fa9a60581)

²⁶ [AWS: Using Amazon DynamoDB with Circuit Breakers](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)

²⁷ [Lyft: Envoy Proxy at Scale](https://eng.lyft.com/envoy-7-months-later-41986c2fd443)

²⁸ [Google Cloud Run: Automatic Circuit Breaking](https://cloud.google.com/run/docs/configuring/circuit-breakers)

²⁹ [AWS App Mesh: Circuit Breaker Configuration](https://docs.aws.amazon.com/app-mesh/latest/userguide/circuit-breakers.html)

³⁰ [Netflix: Chaos Monkey](https://github.com/Netflix/chaosmonkey)

³¹ [AWS: Prime Day 2018 - Powered by AWS](https://aws.amazon.com/blogs/aws/prime-day-2018-powered-by-aws/)

³² [GitHub: October 21 Post-Incident Analysis](https://github.blog/2018-10-30-oct21-post-incident-analysis/)

³³ [Uber: Engineering Reliable Transportation](https://eng.uber.com/engineering-reliability-uber/)

³⁴ [Hystrix Users Survey Results](https://github.com/Netflix/Hystrix/wiki/Hystrix-Users)

³⁵ [Honeycomb: Testing in Production](https://www.honeycomb.io/blog/testing-in-production-the-safe-way)

---

*"The best circuit breaker is invisible when working and obvious when protecting."*

---

## Excellence Framework Integration

### Implementation Guides
- **[Circuit Breaker Implementation Guide](../excellence/guides/circuit-breaker-implementation.md)**: Step-by-step implementation across languages
- **[Resilience Patterns Guide](../excellence/guides/resilience-patterns.md)**: Comprehensive resilience strategy
- **[Service Mesh Circuit Breaking](../excellence/guides/service-mesh-patterns.md#circuit-breaking)**: Mesh-based implementation

### Case Studies
- **[Netflix Hystrix: Circuit Breakers at Scale](../excellence/case-studies/netflix-hystrix.md)**: 100B+ requests/day
- **[Amazon Prime Day Resilience](../excellence/case-studies/amazon-prime-resilience.md)**: Surviving 10x traffic
- **[Uber's Microservices Protection](../excellence/case-studies/uber-microservices.md)**: 3000+ service mesh

### Pattern Combinations
<div class="grid cards" markdown>

- :material-puzzle:{ .lg .middle } **With Retry Pattern**
    
    ---
    
    Circuit breaker prevents retry storms. Combine for intelligent failure handling:
    - Circuit breaker wraps retry logic
    - Retries happen only when circuit is closed
    - [View Integration Guide](../excellence/combinations/circuit-breaker-retry.md)

- :material-puzzle:{ .lg .middle } **With Bulkhead Pattern**
    
    ---
    
    Isolate failures and prevent cascades:
    - Separate circuit breaker per resource pool
    - Independent failure domains
    - [View Integration Guide](../excellence/combinations/circuit-breaker-bulkhead.md)

- :material-puzzle:{ .lg .middle } **With Service Mesh**
    
    ---
    
    Centralized circuit breaking policy:
    - Mesh handles circuit breaking transparently
    - Consistent policies across services
    - [View Integration Guide](../excellence/combinations/circuit-breaker-mesh.md)

- :material-puzzle:{ .lg .middle } **With Observability**
    
    ---
    
    Monitor and alert on circuit state:
    - Track circuit state changes
    - Measure business impact
    - [View Integration Guide](../excellence/combinations/circuit-breaker-observability.md)

</div>

### Comparison with Alternatives

<table class="responsive-table">
<thead>
<tr>
<th>Aspect</th>
<th>Circuit Breaker</th>
<th>Retry Pattern</th>
<th>Timeout Pattern</th>
<th>Rate Limiting</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Aspect"><strong>Primary Goal</strong></td>
<td data-label="Circuit Breaker">Prevent cascade failures</td>
<td data-label="Retry Pattern">Handle transient failures</td>
<td data-label="Timeout Pattern">Bound wait time</td>
<td data-label="Rate Limiting">Prevent overload</td>
</tr>
<tr>
<td data-label="Aspect"><strong>Failure Detection</strong></td>
<td data-label="Circuit Breaker">Statistical (threshold-based)</td>
<td data-label="Retry Pattern">Per-request</td>
<td data-label="Timeout Pattern">Time-based</td>
<td data-label="Rate Limiting">Volume-based</td>
</tr>
<tr>
<td data-label="Aspect"><strong>Recovery</strong></td>
<td data-label="Circuit Breaker">Automatic with test traffic</td>
<td data-label="Retry Pattern">Immediate retry</td>
<td data-label="Timeout Pattern">No recovery logic</td>
<td data-label="Rate Limiting">Time window reset</td>
</tr>
<tr>
<td data-label="Aspect"><strong>Resource Protection</strong></td>
<td data-label="Circuit Breaker">Excellent (fails fast)</td>
<td data-label="Retry Pattern">Poor (can amplify load)</td>
<td data-label="Timeout Pattern">Good (bounds resources)</td>
<td data-label="Rate Limiting">Excellent (hard limits)</td>
</tr>
<tr>
<td data-label="Aspect"><strong>Use Together?</strong></td>
<td data-label="Circuit Breaker">-</td>
<td data-label="Retry Pattern">Yes (CB wraps retry)</td>
<td data-label="Timeout Pattern">Yes (triggers CB)</td>
<td data-label="Rate Limiting">Yes (different layers)</td>
</tr>
</tbody>
</table>

## Migration from Legacy Approaches

### From Simple Retries to Circuit Breaker

<div class="grid cards" markdown>

- :material-file-document:{ .lg .middle } **Migration Guide**
    
    ---
    
    Step-by-step migration from retry-only to circuit breaker:
    - Identify retry loops in code
    - Wrap with circuit breaker
    - Configure thresholds
    - [Full Migration Guide](../excellence/migrations/retry-to-circuit-breaker.md)

- :material-chart-timeline:{ .lg .middle } **Timeline**
    
    ---
    
    - Week 1-2: Identify critical services
    - Week 3-4: Implement in dev/staging
    - Week 5-6: Gradual production rollout
    - Week 7-8: Tune thresholds

</div>

## Related Topics

## Related Patterns

### Resilience Patterns
- **[Retry & Backoff](patterns/retry-backoff)**: Works together for handling transient failures
- **[Bulkhead Pattern](patterns/bulkhead)**: Isolates resources to complement circuit breaking
- **[Timeout Pattern](patterns/timeout)**: Triggers circuit breaker state changes
- **[Fallback Pattern](patterns/graceful-degradation)**: Provides degraded functionality when open

### Prevention Patterns
- **[Rate Limiting](patterns/rate-limiting)**: Prevents overload before circuit trips
- **[Load Shedding](patterns/load-shedding)**: Proactive load management
- **[Backpressure](patterns/backpressure)**: Flow control to prevent cascades

### Monitoring Patterns
- **[Health Checks](patterns/health-check)**: Service health monitoring
- **[Observability](patterns/observability)**: Circuit breaker metrics and tracing

### Coordination Patterns
- **[Saga Pattern](patterns/saga)**: Circuit breakers protect saga steps
- **[Service Mesh](patterns/service-mesh)**: Built-in circuit breaking
- **[API Gateway](patterns/api-gateway)**: Centralized circuit breaking

## Related Laws & Pillars

### Fundamental Laws
This pattern directly addresses:

- **[Law 1: Correlated Failure ⛓️](part1-axioms/law1-failure/)**: Prevents cascade failures across services
- **[Law 2: Asynchronous Reality ⏱️](part1-axioms/law2-asynchrony/)**: Handles timeout and async communication failures
- **[Law 3: Emergent Chaos 🌪️](part1-axioms/law3-emergence/)**: Controls emergent failure patterns
- **[Law 4: Multidimensional Optimization ⚖️](part1-axioms/law4-tradeoffs/)**: Balances availability vs consistency
- **[Law 6: Cognitive Load 🧠](part1-axioms/law6-human-api/)**: Simple state machine reduces operational complexity

### Foundational Pillars
Circuit Breaker implements:

- **[Pillar 3: Distribution of Truth 🔍](part2-pillars/truth/)**: Each service tracks its own dependencies' health
- **[Pillar 4: Distribution of Control 🎮](part2-pillars/control/)**: Decentralized failure detection and response
- **[Pillar 5: Distribution of Intelligence 🤖](part2-pillars/intelligence/)**: Smart failure prediction and recovery

### Case Studies
- [Netflix Hystrix Implementation](case-studies/netflix-hystrix/) - Pioneered circuit breaker patterns at scale
- [Amazon Prime Day Resilience](case-studies/amazon-prime-day/) - Circuit breakers prevented cascade failures
- [Uber's Microservices Architecture](case-studies/uber-microservices/) - Circuit breakers in ride-sharing systems

### Quantitative Analysis
- [Failure Models](quantitative/failure-models) - Mathematical models for failure cascades
- [Queueing Theory](quantitative/queueing-models) - Understanding load and failure relationships
- [Reliability Theory](quantitative/reliability-theory) - Calculating system reliability with circuit breakers

### Further Reading

#### Books & Papers
- ["Release It!" by Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Original circuit breaker pattern
- ["Distributed Systems Safety" by Jepsen](https://jepsen.io/analyses) - Failure analysis
- ["Site Reliability Engineering" by Google](https://sre.google/books/) - Production practices

#### Online Resources
- [Microservices Resilience Patterns](patterns/microservices-resilience) - Comprehensive resilience strategies
- [Service Mesh Architecture](patterns/service-mesh) - Circuit breakers in modern service meshes
- [Chaos Engineering](human-factors/chaos-engineering.md) - Testing circuit breaker effectiveness
- [Martin Fowler's Circuit Breaker Article](https://martinfowler.com/bliki/CircuitBreaker.html) - Clear introduction

#### Tools & Libraries
- **Java**: [Resilience4j](https://resilience4j.readme.io/) (modern), [Hystrix](https://github.com/Netflix/Hystrix) (maintenance mode)
- **Go**: [gobreaker](https://github.com/sony/gobreaker), [circuit](https://github.com/cep21/circuit)
- **Python**: [pybreaker](https://github.com/danielfm/pybreaker), [circuitbreaker](https://github.com/fabfuel/circuitbreaker)
- **JavaScript**: [opossum](https://github.com/nodeshift/opossum), [cockatiel](https://github.com/connor4312/cockatiel)
- **.NET**: [Polly](https://github.com/App-vNext/Polly)

---

<div class="page-nav" markdown>
[:material-arrow-left: Rate Limiting](patterns/rate-limiting) | 
[:material-arrow-up: Patterns](patterns) | 
[:material-arrow-right: Retry & Backoff](patterns/retry-backoff)
</div>