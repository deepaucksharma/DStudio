# Distributed Systems Debugging with Distributed Tracing

## Overview
Debugging distributed systems requires sophisticated approaches due to the complexity of interactions across multiple services. This guide provides comprehensive strategies for debugging distributed systems using distributed tracing and other observability techniques.

## Core Concepts

### Distributed Tracing Fundamentals
- **Trace**: Complete journey of a request through the system
- **Span**: Individual operation within a trace
- **Context Propagation**: Passing trace context between services
- **Sampling**: Controlling data collection volume

### Common Debugging Challenges
- Request flows across multiple services
- Asynchronous processing and message queues
- Network latency and failures
- Complex error propagation
- State inconsistencies across services

## Debugging Strategies

### 1. Correlation ID Strategy

```python
import uuid
import logging
from flask import Flask, request, g

app = Flask(__name__)

class CorrelationIDMiddleware:
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get('X-Correlation-ID') or
            str(uuid.uuid4())
        )
        g.correlation_id = correlation_id
        
        # Add to logging context
        logging.getLogger().addFilter(
            lambda record: setattr(record, 'correlation_id', correlation_id) or True
        )
    
    def after_request(self, response):
        response.headers['X-Correlation-ID'] = g.correlation_id
        return response

# Service-to-service calls
import httpx

async def call_downstream_service(url, data):
    headers = {
        'X-Correlation-ID': g.correlation_id,
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        return response
```

### 2. OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Auto-instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Manual instrumentation for custom operations
@app.route('/process')
def process_request():
    with tracer.start_as_current_span("process_business_logic") as span:
        span.set_attribute("user_id", request.args.get('user_id'))
        span.set_attribute("operation_type", "data_processing")
        
        try:
            # Business logic here
            result = perform_complex_operation()
            span.set_attribute("result_size", len(result))
            return {"status": "success", "data": result}
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise

def perform_complex_operation():
    with tracer.start_as_current_span("database_query"):
        # Database operation
        pass
    
    with tracer.start_as_current_span("external_api_call"):
        # External service call
        pass
```

### 3. Distributed Debugging Patterns

#### Error Context Enrichment
```python
import structlog
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DebugContext:
    service_name: str
    version: str
    deployment_id: str
    trace_id: str
    span_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    feature_flags: Dict[str, Any] = None

class ContextualLogger:
    def __init__(self, context: DebugContext):
        self.context = context
        self.logger = structlog.get_logger(
            service_name=context.service_name,
            version=context.version,
            deployment_id=context.deployment_id,
            trace_id=context.trace_id
        )
    
    def error(self, message: str, **kwargs):
        self.logger.error(
            message,
            user_id=self.context.user_id,
            session_id=self.context.session_id,
            feature_flags=self.context.feature_flags,
            **kwargs
        )

# Usage in request handler
def handle_request():
    context = DebugContext(
        service_name="user-service",
        version="1.2.3",
        deployment_id="prod-us-east-1-abc123",
        trace_id=get_current_trace_id(),
        span_id=get_current_span_id(),
        user_id=request.user_id,
        feature_flags=get_user_feature_flags(request.user_id)
    )
    
    logger = ContextualLogger(context)
    
    try:
        result = process_user_request(request)
        logger.info("Request processed successfully", result_id=result.id)
        return result
    except Exception as e:
        logger.error(
            "Request processing failed",
            error_type=type(e).__name__,
            error_details=str(e),
            request_payload=sanitize_request(request)
        )
        raise
```

## Advanced Debugging Techniques

### 1. Distributed State Inspection

```python
class DistributedStateInspector:
    def __init__(self, services: Dict[str, str]):
        self.services = services  # service_name -> endpoint mapping
    
    async def inspect_request_state(self, correlation_id: str):
        """Inspect state across all services for a request"""
        tasks = []
        
        for service_name, endpoint in self.services.items():
            task = self._get_service_state(service_name, endpoint, correlation_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            service: result 
            for service, result in zip(self.services.keys(), results)
            if not isinstance(result, Exception)
        }
    
    async def _get_service_state(self, service: str, endpoint: str, correlation_id: str):
        url = f"{endpoint}/debug/state/{correlation_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            return response.json()

# Service state endpoint
@app.route('/debug/state/<correlation_id>')
def get_debug_state(correlation_id):
    """Return current state for debugging purposes"""
    return {
        "service": "user-service",
        "correlation_id": correlation_id,
        "active_sessions": get_active_sessions(correlation_id),
        "cache_entries": get_cache_entries(correlation_id),
        "database_connections": get_db_connection_info(),
        "memory_usage": get_memory_stats(),
        "feature_flags": get_current_feature_flags()
    }
```

### 2. Chaos Engineering for Debugging

```python
import random
from enum import Enum

class ChaosType(Enum):
    LATENCY = "latency"
    ERROR = "error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"

class ChaosInstrumentation:
    def __init__(self, enabled: bool = False, chaos_rate: float = 0.01):
        self.enabled = enabled
        self.chaos_rate = chaos_rate
    
    def inject_chaos(self, operation_name: str):
        if not self.enabled or random.random() > self.chaos_rate:
            return
        
        chaos_type = random.choice(list(ChaosType))
        
        with tracer.start_as_current_span("chaos_injection") as span:
            span.set_attribute("chaos_type", chaos_type.value)
            span.set_attribute("target_operation", operation_name)
            
            if chaos_type == ChaosType.LATENCY:
                delay = random.uniform(0.1, 2.0)
                span.set_attribute("injected_delay_seconds", delay)
                time.sleep(delay)
            
            elif chaos_type == ChaosType.ERROR:
                error_msg = f"Chaos engineering error in {operation_name}"
                span.record_exception(Exception(error_msg))
                raise Exception(error_msg)

# Usage
chaos = ChaosInstrumentation(enabled=os.getenv('CHAOS_ENABLED', 'false') == 'true')

@app.route('/api/users/<user_id>')
def get_user(user_id):
    chaos.inject_chaos("get_user")
    
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user_id", user_id)
        # Normal operation
        return get_user_from_db(user_id)
```

## Debugging Workflows

### 1. Request Flow Analysis

```bash
# Jaeger query for request analysis
curl -G "http://jaeger-query:16686/api/traces" \
  --data-urlencode "service=user-service" \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000" \
  --data-urlencode "end=$(date +%s)000000" \
  --data-urlencode "tags={\"error\":\"true\"}"

# Extract trace IDs for failed requests
jq -r '.data[].traces[].traceID' traces.json
```

### 2. Performance Bottleneck Detection

```python
class PerformanceAnalyzer:
    def __init__(self, trace_client):
        self.trace_client = trace_client
    
    def analyze_slow_requests(self, service: str, threshold_ms: int = 1000):
        """Find requests slower than threshold"""
        traces = self.trace_client.search_traces(
            service=service,
            min_duration=f"{threshold_ms}ms"
        )
        
        bottlenecks = {}
        
        for trace in traces:
            for span in trace.spans:
                if span.duration_ms > threshold_ms * 0.8:  # 80% of threshold
                    operation = span.operation_name
                    if operation not in bottlenecks:
                        bottlenecks[operation] = {
                            'count': 0,
                            'total_duration': 0,
                            'max_duration': 0,
                            'examples': []
                        }
                    
                    bottlenecks[operation]['count'] += 1
                    bottlenecks[operation]['total_duration'] += span.duration_ms
                    bottlenecks[operation]['max_duration'] = max(
                        bottlenecks[operation]['max_duration'],
                        span.duration_ms
                    )
                    
                    if len(bottlenecks[operation]['examples']) < 5:
                        bottlenecks[operation]['examples'].append({
                            'trace_id': trace.trace_id,
                            'duration_ms': span.duration_ms,
                            'tags': span.tags
                        })
        
        return bottlenecks
```

## Debugging Tools and Scripts

### 1. Trace Analysis Script

```bash
#!/bin/bash
# trace_analyzer.sh - Analyze distributed traces for debugging

JAEGER_ENDPOINT="http://localhost:16686"
SERVICE_NAME="$1"
TIME_WINDOW="${2:-1h}"

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name> [time-window]"
    exit 1
fi

echo "=== Analyzing traces for $SERVICE_NAME (last $TIME_WINDOW) ==="

# Get error traces
echo "Top error patterns:"
curl -s -G "$JAEGER_ENDPOINT/api/traces" \
  --data-urlencode "service=$SERVICE_NAME" \
  --data-urlencode "lookback=$TIME_WINDOW" \
  --data-urlencode "tags={\"error\":\"true\"}" \
| jq -r '.data[].traces[].spans[] | select(.tags[] | .key == "error" and .value == "true") | .operationName' \
| sort | uniq -c | sort -nr | head -10

# Get slow operations
echo -e "\nSlowest operations:"
curl -s -G "$JAEGER_ENDPOINT/api/traces" \
  --data-urlencode "service=$SERVICE_NAME" \
  --data-urlencode "lookback=$TIME_WINDOW" \
  --data-urlencode "minDuration=1s" \
| jq -r '.data[].traces[].spans[] | "\(.duration/1000)ms \(.operationName)"' \
| sort -nr | head -10

# Service dependency analysis
echo -e "\nService dependencies:"
curl -s -G "$JAEGER_ENDPOINT/api/services" \
| jq -r '.data[]' \
| while read -r service; do
    deps=$(curl -s -G "$JAEGER_ENDPOINT/api/dependencies" \
      --data-urlencode "service=$service" \
      --data-urlencode "lookback=$TIME_WINDOW" \
    | jq -r ".data[] | select(.parent == \"$SERVICE_NAME\" or .child == \"$SERVICE_NAME\") | \"\(.parent) -> \(.child) (calls: \(.callCount))\""
    )
    if [ -n "$deps" ]; then
        echo "$deps"
    fi
done | sort | uniq
```

### 2. Real-time Debug Dashboard

```python
# debug_dashboard.py - Real-time debugging dashboard
import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import aioredis

app = FastAPI()

class DebugDashboard:
    def __init__(self):
        self.redis = None
        self.subscribers = set()
    
    async def initialize(self):
        self.redis = await aioredis.from_url("redis://localhost")
    
    async def subscribe_to_debug_events(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("debug:events")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await self.broadcast_to_subscribers(message['data'])
    
    async def broadcast_to_subscribers(self, data):
        if self.subscribers:
            message = json.loads(data)
            for websocket in self.subscribers.copy():
                try:
                    await websocket.send_json(message)
                except:
                    self.subscribers.remove(websocket)

dashboard = DebugDashboard()

@app.on_startup
async def startup():
    await dashboard.initialize()
    asyncio.create_task(dashboard.subscribe_to_debug_events())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    dashboard.subscribers.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        dashboard.subscribers.remove(websocket)

@app.get("/")
async def get_dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Distributed Systems Debug Dashboard</title>
        <style>
            body { font-family: monospace; background: #000; color: #00ff00; }
            .event { margin: 10px 0; padding: 10px; border: 1px solid #333; }
            .error { border-color: #ff0000; color: #ff0000; }
            .warning { border-color: #ffaa00; color: #ffaa00; }
        </style>
    </head>
    <body>
        <h1>Real-time Debug Events</h1>
        <div id="events"></div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            const events = document.getElementById('events');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const div = document.createElement('div');
                div.className = 'event ' + data.level;
                div.innerHTML = `
                    <strong>${data.timestamp}</strong> - ${data.service}<br>
                    <strong>Trace:</strong> ${data.trace_id}<br>
                    <strong>Message:</strong> ${data.message}<br>
                    <strong>Context:</strong> <pre>${JSON.stringify(data.context, null, 2)}</pre>
                `;
                events.insertBefore(div, events.firstChild);
                
                // Keep only last 50 events
                while (events.children.length > 50) {
                    events.removeChild(events.lastChild);
                }
            };
        </script>
    </body>
    </html>
    """)
```

## Best Practices

### 1. Structured Logging for Debugging
```python
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)

logger = structlog.get_logger()

# Debugging-friendly log structure
def log_debug_event(event_type: str, **context):
    logger.info(
        "debug_event",
        event_type=event_type,
        service_name=os.getenv('SERVICE_NAME'),
        version=os.getenv('SERVICE_VERSION'),
        trace_id=get_current_trace_id(),
        timestamp=datetime.utcnow().isoformat(),
        **context
    )

# Usage examples
log_debug_event(
    "request_processing",
    user_id=user_id,
    endpoint="/api/users",
    processing_time_ms=42
)

log_debug_event(
    "external_service_call",
    target_service="payment-service",
    response_code=200,
    latency_ms=156
)
```

### 2. Health Check Integration
```python
@app.route('/health/debug')
def debug_health():
    """Extended health check for debugging"""
    try:
        return {
            "status": "healthy",
            "debug_info": {
                "active_traces": get_active_trace_count(),
                "error_rate_1m": get_error_rate_last_minute(),
                "avg_response_time_1m": get_avg_response_time(),
                "upstream_services": check_upstream_services(),
                "database_connections": get_db_pool_status(),
                "memory_usage_mb": get_memory_usage(),
                "feature_flags": get_active_feature_flags()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "debug_info": get_emergency_debug_info()
        }, 500
```

## Troubleshooting Checklist

### Pre-Investigation Setup
- [ ] Ensure distributed tracing is properly configured
- [ ] Verify correlation IDs are propagated across services
- [ ] Check log aggregation is working
- [ ] Confirm monitoring dashboards are accessible

### Investigation Process
- [ ] Identify the failing request using trace ID or correlation ID
- [ ] Map the request flow across all involved services
- [ ] Check for error patterns in logs and traces
- [ ] Analyze timing and performance bottlenecks
- [ ] Verify data consistency across services
- [ ] Check resource utilization (CPU, memory, network)

### Resolution Validation
- [ ] Verify fix resolves the root cause
- [ ] Test with synthetic requests
- [ ] Monitor error rates and performance metrics
- [ ] Update runbooks with new insights

## Conclusion

Effective distributed systems debugging requires a combination of proper instrumentation, structured approaches, and the right tools. By implementing distributed tracing, maintaining good logging practices, and using systematic debugging workflows, you can quickly identify and resolve complex issues in distributed environments.

Remember that debugging distributed systems is often about correlation and pattern recognition across multiple data sources. Invest in good observability infrastructure and maintain clear debugging procedures for your team.