# Observability Stacks

**You can't fix what you can't see**

## The Observability Triad

```
        Metrics
          ↑
       INSIGHTS
      ↙        ↘
   Logs ←----→ Traces

Metrics: What is broken
Logs: Why it's broken  
Traces: Where it's broken
```

## Modern Observability Stack

### Metrics Layer

Collection → Storage → Query → Visualization → Alerting

**Popular Stack:**
- Collection: Prometheus exporters, StatsD
- Storage: Prometheus, InfluxDB, M3
- Query: PromQL, Flux
- Visualization: Grafana
- Alerting: Alertmanager

**Key Decisions:**
- Push vs Pull model
- Retention period (15d default)
- Cardinality limits
- Aggregation strategy

### Logging Layer

Generation → Collection → Processing → Storage → Analysis

**Popular Stack:**
- Generation: Structured logging (JSON)
- Collection: Fluentd, Logstash, Vector
- Processing: Stream processing
- Storage: Elasticsearch, Loki, S3
- Analysis: Kibana, Grafana

**Key Decisions:**
- Structured vs unstructured
- Sampling rate
- Retention policy  
- Index strategy

### Tracing Layer

Instrumentation → Collection → Storage → Analysis

**Popular Stack:**
- Instrumentation: OpenTelemetry
- Collection: Jaeger agent, OTLP
- Storage: Cassandra, Elasticsearch
- Analysis: Jaeger UI, Grafana Tempo

**Key Decisions:**
- Sampling strategy
- Trace context propagation
- Storage retention
- Head vs tail sampling

## Reference Architecture

```
                    Applications
                         ↓
              [OpenTelemetry SDK/Agents]
                    ↓    ↓    ↓
                Metrics Logs Traces
                   ↓     ↓     ↓
              [OTLP Collector Cluster]
                ↙      ↓        ↘
        Prometheus  Loki    Jaeger/Tempo
              ↘      ↓        ↙
                  Grafana
                     ↓
              📊 Dashboards
              🚨 Alerts
              🔍 Exploration
```

## Implementation Guide

### 1. Instrument Applications

```python
# Metrics
from prometheus_client import Histogram, Counter

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'route', 'status']
)

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'route', 'status']
)

# Usage
@request_duration.time()
def handle_request(request):
    # Process request
    request_count.labels(
        method=request.method,
        route=request.path,
        status=response.status
    ).inc()
```

```python
# Logs (structured)
import structlog

logger = structlog.get_logger()

logger.info('Request processed',
    request_id=req.id,
    user_id=user.id,
    duration=duration,
    status=res.statusCode,
    correlation_id=req.correlation_id
)
```

```python
# Traces
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span('process_payment') as span:
    span.set_attributes({
        'payment.amount': amount,
        'payment.currency': currency,
        'payment.method': method
    })
    
    # Process payment
    result = process_payment_internal(amount)
    
    span.set_attribute('payment.success', result.success)
```

### 2. Optimize Collection

```yaml
# Collector Configuration
processors:
  batch:
    send_batch_size: 1000
    timeout: 10s
  
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  
  sampling:
    decision_cache_size: 10000
    trace_id_ratio: 0.1  # 10% sampling

# Resource optimization:
# - Batch to reduce network calls
# - Sample to control volume
# - Filter noise early
# - Compress where possible
```

### 3. Design Dashboards

**Dashboard Hierarchy:**

**1. Service Overview (RED metrics)**
- Rate: Requests per second
- Errors: Error percentage  
- Duration: Latency percentiles

**2. Infrastructure View**
- CPU, Memory, Disk, Network
- Saturation indicators
- Capacity remaining

**3. Business Metrics**
- Conversion rates
- Revenue impact
- User experience scores

**4. Detailed Debugging**
- Log aggregations
- Trace analysis
- Error breakdowns

## Observability Patterns

### 1. Correlation IDs

```python
# Flow: Request → Generate ID → Pass to all services → Include in all telemetry

def correlation_id_middleware(request, response, next):
    # Get or generate correlation ID
    correlation_id = request.headers.get('x-correlation-id') or str(uuid4())
    
    # Add to response
    response.headers['x-correlation-id'] = correlation_id
    
    # Add to all telemetry
    logger = logger.bind(correlation_id=correlation_id)
    span = trace.get_current_span()
    if span:
        span.set_attribute('correlation.id', correlation_id)
    
    # Add to metrics labels (carefully - cardinality!)
    metrics.labels(correlation_id=correlation_id)
    
    return next(request, response)
```

### 2. Service Dependency Mapping

Automatic discovery through:
- Trace analysis (who calls whom)
- Network traffic analysis
- Service mesh data
- DNS queries

Visualization:
- Force-directed graphs
- Sankey diagrams
- Heat maps for call volume

### 3. Anomaly Detection

**Statistical approach:**
- Baseline normal behavior
- Detect deviations (3-sigma)
- Seasonal adjustment
- Trend analysis

**ML approach:**
- Train on historical data
- Predict expected values
- Alert on anomalies
- Reduce false positives

## Cost Optimization

### Metrics Costs

**Factors:**
- Cardinality (unique label combinations)
- Retention period
- Query frequency

**Optimizations:**
```python
# Limit label cardinality
# Bad: user_id as label (millions of values)
# Good: status_code as label (handful of values)

# Pre-aggregate common queries
recording_rules:
  - record: job:request_rate5m
    expr: rate(http_requests_total[5m])

# Downsample old data
downsampling:
  - resolution: 5m
    retention: 30d
  - resolution: 1h
    retention: 90d
```

**Example savings:**
- Before: 10M series × 15d = $5000/month
- After: 1M series × 15d + aggregates = $800/month

### Log Costs

**Factors:**
- Volume (GB/day)
- Retention
- Indexing

**Optimizations:**
```python
# Log sampling
if log_level == 'INFO' and random() > 0.1:
    return  # Sample 90% of info logs

# Tiered storage
hot_storage: 7 days (SSD)
warm_storage: 30 days (HDD)
cold_storage: 1 year (S3)

# Index only searchable fields
indexed_fields: [timestamp, level, service, correlation_id]
stored_fields: [*]  # Store all, index few
```

**Example savings:**
- Before: 1TB/day × 30d = $15000/month
- After: 100GB/day × 7d hot + S3 = $2000/month

### Trace Costs

**Factors:**
- Trace volume
- Span cardinality
- Retention

**Optimizations:**
```python
# Tail-based sampling
def should_sample(trace):
    # Always sample errors
    if trace.has_error:
        return True
    
    # Sample slow requests
    if trace.duration > 1000:  # 1 second
        return True
    
    # Random sample others
    return random() < 0.01  # 1%

# Trace aggregation
# Store full traces short-term, aggregates long-term
```

**Example savings:**
- Before: 100% traces = $8000/month
- After: 1% baseline + errors = $1200/month

## Troubleshooting with Observability

### Investigation Flow

```
1. Alert fires: "Payment service error rate high"

2. Check metrics dashboard:
   - Error rate: 15% (normal: <1%)
   - Latency: p99 = 5s (normal: 100ms)
   - Started: 10:42 AM

3. Query logs:
   - Filter: service="payment" level="error" @timestamp>10:40
   - Finding: "Database connection timeout"
   - Pattern: All errors from payment-db-2

4. Analyze traces:
   - Filter: service="payment" error=true
   - Finding: payment-db-2 responding in 5s
   - Root span: Database query stuck

5. Check infrastructure:
   - payment-db-2 CPU: 100%
   - Disk I/O: Saturated
   - Finding: Backup job running

Resolution: Kill backup job, reschedule for off-peak
```

## Observability Maturity

### Level 1: Reactive
- Basic logging to files
- Manual log searching
- CPU/memory graphs
- Email alerts

### Level 2: Proactive
- Centralized logging
- Basic dashboards
- Threshold alerts
- Some tracing

### Level 3: Predictive
- Full observability stack
- Correlation across signals
- Anomaly detection
- SLO-based alerts

### Level 4: Prescriptive
- AIOps integration
- Automated remediation
- Predictive scaling
- Cost optimization

## Best Practices

1. **Structured Everything**
   - JSON logs
   - Tagged metrics
   - Attributed traces

2. **Correlation is Key**
   - Use correlation IDs
   - Link metrics to traces
   - Connect logs to requests

3. **Sample Intelligently**
   - Keep all errors
   - Sample success cases
   - Adaptive sampling

4. **Dashboard Discipline**
   - Standard layouts
   - Consistent naming
   - Regular review

5. **Alert Thoughtfully**
   - SLO-based alerts
   - Business impact focus
   - Actionable messages

## Key Takeaways

- **Three pillars work together** - Metrics, logs, and traces complement each other
- **Standards matter** - OpenTelemetry provides vendor-neutral instrumentation
- **Cost grows quickly** - Plan for optimization from day one
- **Correlation enables debugging** - Connect the dots across signals
- **Culture drives adoption** - Teams must value observability

Remember: Observability is not a product you buy, but a property of systems you build.