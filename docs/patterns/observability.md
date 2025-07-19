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
```

## THE SOLUTION

```
Three Pillars of Observability:

METRICS          LOGS           TRACES
   ↓               ↓               ↓
What's broken?  Why broken?   How it broke?
   ↓               ↓               ↓
 Grafana       Elasticsearch   Jaeger
```

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
```

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
```

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