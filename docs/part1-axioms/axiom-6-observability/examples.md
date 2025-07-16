# Observability Examples & Failure Stories

!!! info "Prerequisites"
    - [Axiom 6: Observability Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Observability Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Failure Stories

<div class="failure-vignette">

### 🎬 The Invisible Memory Leak

```yaml
Company: Video streaming platform
Symptom: Random user disconnections, increasing over weeks

Monitoring in place:
- CPU metrics: Normal (40%)
- Memory metrics: Averaged per minute, looked fine
- Network metrics: Normal
- Error logs: Nothing unusual

Investigation timeline:
Week 1: "Must be client-side issues"
Week 2: "Maybe network problems?"
Week 3: Customer complaints spike
Week 4: Engineer notices during manual debug:
  - Memory usage sawtooth pattern
  - Spikes to 95% every 58 seconds
  - Averaged out to 70% in 1-min metrics
  - GC pause during spike: 2 seconds
  - Clients timeout during pause

Root cause: Goroutine leak in WebSocket handler
- Each connection leaked 1MB
- 58 seconds to accumulate ~2GB
- Massive GC pause, connections drop

Fix: 
1. Add per-second memory metrics
2. Add GC pause tracking
3. Fix the leak

Lesson: 1-minute averages hide 1-second disasters

Cost of poor observability:
- 4 weeks of customer impact
- 200+ engineering hours
- $2M in lost revenue
- Reputation damage
```

</div>

<div class="failure-vignette">

### 🎬 The Sampling Catastrophe

```yaml
Company: E-commerce platform
Incident: Black Friday total outage
Year: 2022

Observability setup:
- Distributed tracing: 0.1% sampling
- Logs: Sampled 1 in 1000 for cost
- Metrics: 5-minute aggregation
- Alerts: Based on averages

What happened:
09:00: Black Friday sale starts
09:01: Specific product page starts failing
09:02: 0.1% trace sampling misses all failures
09:05: 5-min metrics show "normal"
09:15: Failures cascade to checkout
09:20: Still no alerts (averaged out)
09:30: Customer complaints flood Twitter
09:45: Manual investigation begins
10:30: Issue found: Unicode in product name
11:00: Fix deployed
11:30: Service restored

Why observability failed:
1. Biased sampling missed edge case
2. Aggressive log sampling lost errors
3. 5-min metrics too coarse
4. No business metrics (revenue/min)

Impact:
- 2.5 hours of partial outage
- $15M in lost sales
- #CompanyFail trending

Fix:
- Adaptive sampling (sample all errors)
- 1-second metrics for critical paths
- Business KPI dashboards
- Synthetic monitoring
```

</div>

<div class="failure-vignette">

### 🎬 The Correlation ID Nightmare

```yaml
Company: Global financial services
System: Microservices (47 services)
Problem: Unable to trace failed transactions

Architecture:
- Frontend → API Gateway → 47 microservices
- Each service had different logging
- No correlation IDs
- No standardized format

Customer complaint:
"Transaction deducted but not credited"

Investigation:
Day 1: Check frontend logs (no error)
Day 2: Check API gateway (request found)
Day 3-5: Manually grep through services
Day 6: Find error in service #31
Day 7: Trace backward to find root cause
Day 8: Discover race condition in service #12

Root cause:
- Distributed transaction
- Service #12 timeout
- Partial completion
- No way to trace automatically

Cost:
- 8 days of senior engineer time
- Customer compensation
- Regulatory scrutiny
- Trust erosion

Solution implemented:
- Correlation ID in every request
- Structured logging standard
- Distributed tracing
- Transaction status service
```

</div>

## Observability Patterns in Practice

### 1. Structured Logging

#### Before (Unstructured)
```
2024-01-15 10:23:45 INFO User login successful for john@example.com
2024-01-15 10:23:46 ERROR Payment failed: Insufficient funds
2024-01-15 10:23:47 INFO Order created: 12345
```

#### After (Structured)
```json
{"timestamp":"2024-01-15T10:23:45Z","level":"INFO","service":"auth","event":"user_login","user_id":"usr_123","email":"john@example.com","ip":"192.168.1.1","correlation_id":"req_abc123"}
{"timestamp":"2024-01-15T10:23:46Z","level":"ERROR","service":"payment","event":"payment_failed","user_id":"usr_123","order_id":"ord_12345","reason":"insufficient_funds","amount":99.99,"correlation_id":"req_abc123"}
{"timestamp":"2024-01-15T10:23:47Z","level":"INFO","service":"order","event":"order_created","user_id":"usr_123","order_id":"ord_12345","total":99.99,"items":3,"correlation_id":"req_abc123"}
```

Benefits:
- Machine parseable
- Queryable by any field
- Correlation across services
- Rich context

### 2. Metrics Aggregation Strategies

#### The Percentile Problem

```python
# WRONG: Average of averages
service_a_avg = 50ms
service_b_avg = 60ms
total_avg = (50 + 60) / 2 = 55ms  # Incorrect!

# RIGHT: Weighted average
service_a: 1000 requests @ 50ms = 50,000ms
service_b: 100 requests @ 60ms = 6,000ms
total_avg = 56,000ms / 1100 requests = 50.9ms

# BETTER: Use histograms
histogram_buckets = [0, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
# Can calculate accurate percentiles across services
```

#### Cardinality Explosion

```yaml
# BAD: Unbounded cardinality
metric: http_requests_total
labels:
  - user_id: "user_123"  # Millions of values!
  - session_id: "sess_abc"  # Billions of values!
  - request_id: "req_xyz"  # Infinite values!

# GOOD: Bounded cardinality
metric: http_requests_total
labels:
  - method: "GET"  # ~10 values
  - endpoint: "/api/users"  # ~100 values
  - status: "200"  # ~20 values
  - region: "us-east-1"  # ~10 values
```

### 3. Distributed Tracing

#### Trace Context Propagation

```python
# Service A (initiator)
def handle_request(request):
    trace_id = generate_trace_id()
    span_id = generate_span_id()
    
    headers = {
        'X-Trace-ID': trace_id,
        'X-Parent-Span-ID': span_id,
        'X-Span-ID': generate_span_id()
    }
    
    # Call Service B
    response = http_client.post(
        'http://service-b/api/process',
        headers=headers,
        json=request.data
    )
    
    return response

# Service B (receiver)
def process_request(request):
    trace_id = request.headers.get('X-Trace-ID')
    parent_span_id = request.headers.get('X-Parent-Span-ID')
    span_id = generate_span_id()
    
    # Create span with parent relationship
    span = tracer.start_span(
        'process_request',
        trace_id=trace_id,
        parent_id=parent_span_id,
        span_id=span_id
    )
    
    try:
        result = do_processing()
        span.set_status('OK')
        return result
    except Exception as e:
        span.set_status('ERROR')
        span.set_attribute('error.message', str(e))
        raise
    finally:
        span.finish()
```

### 4. Adaptive Sampling

```python
class AdaptiveSampler:
    def __init__(self):
        self.error_rate = 0
        self.latency_p99 = 0
        self.base_rate = 0.001  # 0.1% baseline
        
    def should_sample(self, span):
        # Always sample errors
        if span.is_error:
            return True
            
        # Sample slow requests
        if span.duration > self.latency_p99 * 2:
            return True
            
        # Adaptive rate based on system health
        if self.error_rate > 0.01:  # >1% errors
            sample_rate = 0.1  # Sample 10%
        elif self.latency_p99 > 1000:  # >1s P99
            sample_rate = 0.05  # Sample 5%
        else:
            sample_rate = self.base_rate
            
        return random.random() < sample_rate
```

## Real Observability Implementations

### 1. Netflix's Telemetry Pipeline

```yaml
Scale:
- 200M+ subscribers
- 100K+ instances
- Petabytes of logs/day

Architecture:
- Edge: Lightweight metrics aggregation
- Transport: Kafka for reliability
- Storage: Time-series DB for metrics
- Query: Distributed query engine

Key innovations:
- Automated anomaly detection
- Predictive alerting
- Cost attribution per metric
- Adaptive retention
```

### 2. Uber's Observability Platform

```yaml
Requirements:
- 15M+ trips/day
- Sub-second alerting
- Global distribution

Solution:
- Metrics: M3 (custom TSDB)
- Tracing: Jaeger (they created it)
- Logs: ELK with modifications
- Correlation: Custom service

Lessons learned:
- Sampling must be intelligent
- Context propagation is critical
- Cost control needs automation
- Standardization enables scale
```

## Common Observability Anti-Patterns

### 1. The Dashboard Graveyard

```yaml
Symptoms:
- 500+ dashboards
- No naming convention
- No ownership
- Duplicated metrics
- Outdated alerts

Result:
- Can't find relevant dashboard
- Create new one (making it worse)
- Alert fatigue
- Missing real issues

Solution:
- Dashboard registry
- Automated cleanup
- Team ownership
- Standard templates
```

### 2. Alert Fatigue

```yaml
Bad alerting:
- CPU > 80% (too noisy)
- Any 500 error (not actionable)
- Disk will fill in 90 days (too early)
- Response time > 100ms (too strict)

Good alerting:
- Error rate > 1% for 5 minutes
- P99 latency > SLO for 10 minutes
- Disk will fill in 6 hours
- Revenue drop > 10% vs baseline
```

### 3. The Monitoring Tax

```yaml
Hidden costs:
- 30% CPU for metrics collection
- 50GB/day of logs nobody reads
- $100K/month for unused dashboards
- 5 engineers just managing monitoring

Optimization:
- Sample intelligently
- Aggregate at edge
- Drop debug logs in prod
- Automate dashboard lifecycle
```

## Debugging with Observability

### The Scientific Method

```yaml
1. Symptom: Users report slow checkout
2. Hypothesis: Database is slow
3. Test: Check DB metrics
   Result: DB latency normal
   
4. New hypothesis: API gateway bottleneck
5. Test: Check gateway traces
   Result: Gateway adds 2s latency!
   
6. Root cause: Rate limiter misconfiguration
7. Fix: Adjust rate limit
8. Verify: Latency back to normal
```

### Observability-Driven Development

```python
def process_order(order):
    # Instrument from the start
    with tracer.start_span('process_order') as span:
        span.set_attribute('order.id', order.id)
        span.set_attribute('order.total', order.total)
        
        # Structured logging
        logger.info('Processing order', 
                   order_id=order.id,
                   user_id=order.user_id,
                   total=order.total)
        
        # Business metrics
        metrics.increment('orders.processed')
        metrics.histogram('order.value', order.total)
        
        try:
            validate_order(order)
            charge_payment(order)
            fulfill_order(order)
            
            metrics.increment('orders.successful')
            return {'status': 'success'}
            
        except ValidationError as e:
            span.set_status('FAILED')
            logger.error('Order validation failed',
                        order_id=order.id,
                        error=str(e))
            metrics.increment('orders.validation_failed')
            raise
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Averages hide problems** - Always use percentiles
    2. **Sampling can miss critical errors** - Sample all failures
    3. **No correlation = no debugging** - Always use trace IDs
    4. **Cost cutting backfires** - Poor observability costs more
    5. **Tools don't equal observability** - Need practices and standards

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Observability Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 7: Human Interface](../axiom-7-human-interface/index.md) →
    
    **Tools**: [Observability Stack Setup](../../tools/observability-stack.md)