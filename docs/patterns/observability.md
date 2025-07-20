---
title: Observability Patterns
description: "Implement comprehensive monitoring, logging, and tracing to understand system behavior in production"
type: pattern
difficulty: intermediate
reading_time: 20 min
prerequisites: []
pattern_type: "operations"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Observability Patterns**

# Observability Patterns

**You can't fix what you can't see**

## THE PROBLEM

```
Production mystery:
- "The site is slow" → Which part?
- "Errors are spiking" → Where? Why?
- "We're losing data" → When? How much?
- "It worked yesterday" → What changed?

Flying blind in production = Pain
```bash
## THE SOLUTION

```
Three Pillars of Observability:

METRICS          LOGS           TRACES
   ↓               ↓               ↓
What's broken?  Why broken?   How it broke?
   ↓               ↓               ↓
 Grafana       Elasticsearch   Jaeger
```bash
## The Observability Stack

```
1. INSTRUMENTATION (Generate data)
   Metrics, logs, traces from code

2. COLLECTION (Gather data)
   Agents, sidecars, SDKs

3. STORAGE (Keep data)
   Time-series DB, log storage

4. ANALYSIS (Use data)
   Dashboards, alerts, queries
```bash
## IMPLEMENTATION

```python
# Structured logging
import structlog
import time
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc import (
    trace_exporter, metrics_exporter
)

class ObservableService:
    def __init__(self, service_name: str):
        self.service_name = service_name

        # Initialize structured logger
        self.logger = structlog.get_logger(
            service=service_name,
            version="1.0.0"
        )

        # Initialize tracer
        self.tracer = trace.get_tracer(service_name)

        # Initialize metrics
        meter = metrics.get_meter(service_name)
        self.request_counter = meter.create_counter(
            "requests_total",
            description="Total requests",
            unit="1"
        )
        self.request_duration = meter.create_histogram(
            "request_duration_seconds",
            description="Request duration",
            unit="s"
        )
        self.active_requests = meter.create_up_down_counter(
            "active_requests",
            description="Active requests",
            unit="1"
        )

    async def handle_request(self, request):
        """Observable request handling"""

        # Start span for distributed tracing
        with self.tracer.start_as_current_span(
            "handle_request",
            kind=trace.SpanKind.SERVER
        ) as span:

            # Add request metadata to span
            span.set_attributes({
                "http.method": request.method,
                "http.url": request.url,
                "http.user_agent": request.headers.get("User-Agent"),
                "user.id": request.user_id
            })

            # Increment metrics
            self.request_counter.add(1, {
                "method": request.method,
                "endpoint": request.endpoint
            })
            self.active_requests.add(1)

            # Structured logging with context
            self.logger.info(
                "request_started",
                request_id=request.id,
                method=request.method,
                path=request.path,
                user_id=request.user_id
            )

            start_time = time.time()

            try:
                # Process request
                result = await self.process(request)

                # Log success
                self.logger.info(
                    "request_completed",
                    request_id=request.id,
                    duration=time.time() - start_time,
                    status_code=result.status_code
                )

                # Update span
                span.set_status(trace.Status(trace.StatusCode.OK))
                span.set_attribute("http.status_code", result.status_code)

                return result

            except Exception as e:
                # Log error with full context
                self.logger.error(
                    "request_failed",
                    request_id=request.id,
                    duration=time.time() - start_time,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )

                # Update span with error
                span.record_exception(e)
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, str(e))
                )

                # Record error metric
                self.request_counter.add(1, {
                    "method": request.method,
                    "endpoint": request.endpoint,
                    "status": "error"
                })

                raise

            finally:
                # Record duration
                duration = time.time() - start_time
                self.request_duration.record(duration, {
                    "method": request.method,
                    "endpoint": request.endpoint
                })
                self.active_requests.add(-1)

# Custom metrics collection
class MetricsCollector:
    def __init__(self):
        self.meter = metrics.get_meter("custom_metrics")
        self.metrics = {}

    def create_business_metrics(self):
        """Create business-specific metrics"""

        # Revenue metrics
        self.metrics['revenue'] = self.meter.create_counter(
            "business.revenue.total",
            description="Total revenue",
            unit="USD"
        )

        # User activity metrics
        self.metrics['active_users'] = self.meter.create_observable_gauge(
            "business.users.active",
            callbacks=[self._observe_active_users],
            description="Currently active users"
        )

        # Performance metrics
        self.metrics['cache_hit_ratio'] = self.meter.create_observable_gauge(
            "performance.cache.hit_ratio",
            callbacks=[self._observe_cache_ratio],
            description="Cache hit ratio"
        )

    async def _observe_active_users(self, options):
        """Callback for active users metric"""
        count = await self.count_active_users()
        yield metrics.Observation(count, {})

    async def _observe_cache_ratio(self, options):
        """Callback for cache hit ratio"""
        hits = await self.get_cache_hits()
        misses = await self.get_cache_misses()

        if hits + misses > 0:
            ratio = hits / (hits + misses)
            yield metrics.Observation(ratio, {})

# Distributed tracing
class DistributedTracer:
    def __init__(self):
        self.tracer = trace.get_tracer("distributed_system")

    async def traced_database_query(self, query: str, params: dict):
        """Database query with tracing"""

        with self.tracer.start_as_current_span(
            "database.query",
            kind=trace.SpanKind.CLIENT
        ) as span:

            # Add query details
            span.set_attributes({
                "db.system": "postgresql",
                "db.statement": query,
                "db.operation": self._extract_operation(query)
            })

            try:
                start = time.time()
                result = await self.execute_query(query, params)

                span.set_attribute("db.rows_affected", len(result))
                return result

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                raise

    async def traced_http_call(self, url: str, method: str = "GET"):
        """HTTP call with tracing propagation"""

        with self.tracer.start_as_current_span(
            f"http.{method.lower()}",
            kind=trace.SpanKind.CLIENT
        ) as span:

            span.set_attributes({
                "http.method": method,
                "http.url": url
            })

            # Inject trace context into headers
            headers = {}
            trace.propagate.inject(headers)

            response = await self.http_client.request(
                method, url, headers=headers
            )

            span.set_attribute("http.status_code", response.status)
            return response

# Log aggregation patterns
class LogAggregator:
    def __init__(self):
        self.buffer = []
        self.batch_size = 100
        self.flush_interval = 5.0

    async def log(self, level: str, message: str, **context):
        """Buffer and batch logs"""

        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "service": context.get("service", "unknown"),
            "trace_id": self._get_trace_id(),
            **context
        }

        self.buffer.append(log_entry)

        if len(self.buffer) >= self.batch_size:
            await self.flush()

    async def flush(self):
        """Send logs to aggregation service"""

        if not self.buffer:
            return

        batch = self.buffer[:self.batch_size]
        self.buffer = self.buffer[self.batch_size:]

        # Send to log aggregation service
        await self.send_to_elasticsearch(batch)

    def _get_trace_id(self):
        """Get current trace ID if in traced context"""
        span = trace.get_current_span()
        if span and span.is_recording():
            return span.get_span_context().trace_id
        return None

# Alerting patterns
class AlertManager:
    def __init__(self):
        self.rules = []
        self.alert_channels = []

    def add_rule(self, rule):
        """Add alerting rule"""
        self.rules.append(rule)

    async def evaluate_rules(self, metrics):
        """Check metrics against rules"""

        for rule in self.rules:
            if rule.evaluate(metrics):
                alert = Alert(
                    name=rule.name,
                    severity=rule.severity,
                    message=rule.format_message(metrics),
                    labels=rule.labels,
                    annotations=rule.annotations
                )

                await self.fire_alert(alert)

    async def fire_alert(self, alert):
        """Send alert to configured channels"""

        # Deduplication
        if self.is_duplicate(alert):
            return

        # Route based on severity
        channels = self.route_alert(alert)

        # Send to channels
        for channel in channels:
            await channel.send(alert)

        # Record alert
        self.record_alert(alert)

# SLI/SLO monitoring
class SLOMonitor:
    def __init__(self, slo_config):
        self.slos = slo_config
        self.error_budget = {}

    def calculate_error_budget(self, slo_name: str, time_window: int):
        """Calculate remaining error budget"""

        slo = self.slos[slo_name]
        target = slo['target']  # e.g., 99.9%

        # Get metrics for time window
        success_rate = self.get_success_rate(slo_name, time_window)

        # Calculate budget
        allowed_errors = (1 - target) * time_window
        actual_errors = (1 - success_rate) * time_window

        remaining_budget = allowed_errors - actual_errors

        return {
            'slo': slo_name,
            'target': target,
            'current': success_rate,
            'budget_remaining': remaining_budget,
            'budget_remaining_percent': (remaining_budget / allowed_errors) * 100
        }
```bash
## Advanced Observability

```python
# Continuous profiling
class ContinuousProfiler:
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.enabled = False

    async def profile_periodically(self, duration=30, interval=300):
        """Profile application periodically"""

        while True:
            # Enable profiling
            self.profiler.enable()

            # Profile for duration
            await asyncio.sleep(duration)

            # Disable and collect
            self.profiler.disable()

            # Send profile data
            await self.send_profile_data()

            # Wait before next profile
            await asyncio.sleep(interval - duration)

    async def send_profile_data(self):
        """Send profile to analysis service"""

        s = StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()

        profile_data = s.getvalue()

        # Send to profiling service
        await self.profile_service.upload(profile_data)

# Correlation analysis
class CorrelationAnalyzer:
    def __init__(self):
        self.metrics_store = MetricsStore()

    async def find_correlations(self, anomaly_time, window=3600):
        """Find metrics correlated with anomaly"""

        # Get all metrics around anomaly time
        start = anomaly_time - window
        end = anomaly_time + window

        all_metrics = await self.metrics_store.query_range(start, end)

        correlations = []

        # Check each metric for correlation
        for metric in all_metrics:
            correlation = self.calculate_correlation(
                metric,
                anomaly_time,
                window
            )

            if correlation > 0.7:  # Strong correlation
                correlations.append({
                    'metric': metric.name,
                    'correlation': correlation,
                    'lag': self.find_lag(metric, anomaly_time)
                })

        return sorted(correlations, key=lambda x: x['correlation'], reverse=True)
```

## ✓ CHOOSE THIS WHEN:
• Running production systems
• Need debugging capabilities
• Want to prevent incidents
• Tracking SLIs/SLOs
• Compliance requirements

## ⚠️ BEWARE OF:
• Instrumentation overhead
• Storage costs at scale
• Alert fatigue
• Privacy in logs
• Cardinality explosion

## REAL EXAMPLES
• **Google**: Dapper tracing
• **Twitter**: Observability 2.0
• **Netflix**: Atlas metrics

---

**Previous**: [← Load Shedding Pattern](load-shedding.md) | **Next**: [Outbox Pattern →](outbox.md)
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

## 💻 Code Sample

### Basic Implementation

```python
class ObservabilityPattern:
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
pattern = ObservabilityPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
observability:
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
def test_observability_behavior():
    pattern = ObservabilityPattern(test_config)

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
