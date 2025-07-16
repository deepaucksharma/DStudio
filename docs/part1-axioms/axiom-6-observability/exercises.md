# Observability Exercises

!!! info "Prerequisites"
    - [Axiom 6: Observability Core Concepts](index.md)
    - [Observability Examples](examples.md)
    - Basic understanding of logging and metrics

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Observability Home](index.md) |
    [→ Next Axiom](../axiom-7-human-interface/index.md)

## Exercise 1: Build a Structured Logger

### 🔧 Try This: Implement Context-Aware Logging

```python
import json
import time
import uuid
from datetime import datetime
from contextlib import contextmanager
import threading

class StructuredLogger:
    def __init__(self, service_name):
        self.service = service_name
        self.context = threading.local()
        
    def set_correlation_id(self, correlation_id):
        """Set correlation ID for current thread"""
        # TODO: Implement thread-local storage
        pass
    
    def add_context(self, **kwargs):
        """Add context that will be included in all logs"""
        # TODO: Implement context management
        pass
    
    @contextmanager
    def operation(self, operation_name):
        """Context manager for timing operations"""
        # TODO: Implement operation timing
        # Should log start, end, duration
        # Should handle exceptions
        pass
    
    def log(self, level, message, **kwargs):
        """Log with structure and context"""
        # TODO: Implement structured logging
        # Include: timestamp, level, service, correlation_id
        # Include: thread context, kwargs
        pass

# Exercise: Use the logger in a realistic scenario
def test_structured_logging():
    logger = StructuredLogger('payment-service')
    
    # Simulate a request flow
    correlation_id = str(uuid.uuid4())
    logger.set_correlation_id(correlation_id)
    logger.add_context(user_id='user_123', region='us-east-1')
    
    with logger.operation('process_payment'):
        logger.log('INFO', 'Payment initiated', amount=99.99, currency='USD')
        
        # Simulate processing
        time.sleep(0.1)
        
        # Simulate error
        logger.log('ERROR', 'Payment failed', 
                  error='Insufficient funds',
                  available_balance=50.00)
```

<details>
<summary>Solution</summary>

```python
import json
import time
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
import threading
import sys
import traceback

class StructuredLogger:
    def __init__(self, service_name, output=sys.stdout):
        self.service = service_name
        self.context = threading.local()
        self.output = output
        self._initialize_context()
        
    def _initialize_context(self):
        """Initialize thread-local context"""
        if not hasattr(self.context, 'data'):
            self.context.data = {}
            self.context.correlation_id = None
            
    def set_correlation_id(self, correlation_id):
        """Set correlation ID for current thread"""
        self._initialize_context()
        self.context.correlation_id = correlation_id
        
    def add_context(self, **kwargs):
        """Add context that will be included in all logs"""
        self._initialize_context()
        self.context.data.update(kwargs)
        
    def clear_context(self):
        """Clear thread-local context"""
        self._initialize_context()
        self.context.data = {}
        self.context.correlation_id = None
        
    @contextmanager
    def operation(self, operation_name):
        """Context manager for timing operations"""
        start_time = time.time()
        operation_id = str(uuid.uuid4())[:8]
        
        # Log operation start
        self.log('INFO', f'{operation_name} started', 
                operation=operation_name,
                operation_id=operation_id)
        
        try:
            yield operation_id
            
            # Log successful completion
            duration = (time.time() - start_time) * 1000
            self.log('INFO', f'{operation_name} completed',
                    operation=operation_name,
                    operation_id=operation_id,
                    duration_ms=round(duration, 2),
                    status='success')
                    
        except Exception as e:
            # Log failure
            duration = (time.time() - start_time) * 1000
            self.log('ERROR', f'{operation_name} failed',
                    operation=operation_name,
                    operation_id=operation_id,
                    duration_ms=round(duration, 2),
                    status='failed',
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stacktrace=traceback.format_exc())
            raise
            
    def log(self, level, message, **kwargs):
        """Log with structure and context"""
        self._initialize_context()
        
        # Build log entry
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': level,
            'service': self.service,
            'message': message,
            'thread': threading.current_thread().name,
        }
        
        # Add correlation ID if set
        if self.context.correlation_id:
            entry['correlation_id'] = self.context.correlation_id
            
        # Add thread-local context
        entry.update(self.context.data)
        
        # Add specific log kwargs
        entry.update(kwargs)
        
        # Output as JSON
        json.dump(entry, self.output)
        self.output.write('\n')
        self.output.flush()
        
    # Convenience methods
    def debug(self, message, **kwargs):
        self.log('DEBUG', message, **kwargs)
        
    def info(self, message, **kwargs):
        self.log('INFO', message, **kwargs)
        
    def warning(self, message, **kwargs):
        self.log('WARNING', message, **kwargs)
        
    def error(self, message, **kwargs):
        self.log('ERROR', message, **kwargs)

# Enhanced testing
def test_structured_logging():
    import io
    
    # Capture logs for testing
    output = io.StringIO()
    logger = StructuredLogger('payment-service', output=output)
    
    print("=== Structured Logging Test ===\n")
    
    # Test 1: Basic logging
    logger.info('Service started', version='1.2.3', environment='production')
    
    # Test 2: Request flow with correlation
    correlation_id = str(uuid.uuid4())
    logger.set_correlation_id(correlation_id)
    logger.add_context(user_id='user_123', region='us-east-1')
    
    with logger.operation('process_payment') as op_id:
        logger.info('Payment initiated', 
                   amount=99.99, 
                   currency='USD',
                   payment_method='credit_card')
        
        # Simulate processing steps
        with logger.operation('validate_card'):
            time.sleep(0.05)
            logger.info('Card validated', last_four='1234')
            
        with logger.operation('check_fraud'):
            time.sleep(0.03)
            logger.info('Fraud check passed', risk_score=0.15)
            
        try:
            with logger.operation('charge_card'):
                time.sleep(0.02)
                # Simulate failure
                raise ValueError("Insufficient funds")
        except ValueError:
            logger.error('Payment failed', 
                        error='Insufficient funds',
                        available_balance=50.00,
                        requested_amount=99.99)
    
    # Test 3: Concurrent logging
    def worker(worker_id):
        worker_logger = StructuredLogger(f'worker-{worker_id}', output=output)
        worker_logger.set_correlation_id(f'work-{worker_id}')
        
        with worker_logger.operation(f'process_task_{worker_id}'):
            time.sleep(0.1)
            worker_logger.info(f'Task completed', items_processed=100)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    
    # Parse and display results
    output.seek(0)
    logs = [json.loads(line) for line in output.readlines()]
    
    print(f"Total logs generated: {len(logs)}\n")
    
    # Show sample logs
    print("Sample structured logs:")
    for log in logs[:5]:
        print(json.dumps(log, indent=2))
        print()
    
    # Analyze logs
    print("\nLog Analysis:")
    print(f"- Info logs: {sum(1 for l in logs if l['level'] == 'INFO')}")
    print(f"- Error logs: {sum(1 for l in logs if l['level'] == 'ERROR')}")
    print(f"- Unique correlations: {len(set(l.get('correlation_id', 'none') for l in logs))}")
    print(f"- Operations tracked: {sum(1 for l in logs if 'operation' in l)}")
    
    # Find slowest operation
    operations = [l for l in logs if 'duration_ms' in l]
    if operations:
        slowest = max(operations, key=lambda x: x['duration_ms'])
        print(f"\nSlowest operation: {slowest['operation']} ({slowest['duration_ms']}ms)")

# Run the test
test_structured_logging()

# Real-world example
def payment_service_example():
    logger = StructuredLogger('payment-service')
    
    # Simulate incoming request
    request_id = str(uuid.uuid4())
    logger.set_correlation_id(request_id)
    
    # Add request context
    logger.add_context(
        user_id='user_456',
        session_id='sess_789',
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0...'
    )
    
    try:
        with logger.operation('handle_payment_request'):
            # Validate input
            with logger.operation('validate_input'):
                logger.info('Validating payment request', 
                           amount=150.00,
                           merchant_id='merchant_123')
            
            # Check rate limits
            with logger.operation('check_rate_limits'):
                logger.info('Rate limit check', 
                           current_rate=45,
                           limit=100)
            
            # Process payment
            with logger.operation('process_payment'):
                logger.info('Processing payment',
                           processor='stripe',
                           amount=150.00)
                
                # Simulate success
                logger.info('Payment successful',
                           transaction_id='txn_abc123',
                           processing_time_ms=234)
                
    except Exception as e:
        logger.error('Request failed', 
                    error=str(e),
                    refund_initiated=True)

print("\n\n=== Real-world Payment Service Example ===")
payment_service_example()
```

</details>

## Exercise 2: Implement Metrics Collection

### 🔧 Try This: Build a Metrics System

```python
import time
from collections import defaultdict
from threading import Lock

class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.lock = Lock()
        
    def increment(self, metric_name, value=1, labels=None):
        """Increment a counter metric"""
        # TODO: Implement counter with labels
        pass
        
    def gauge(self, metric_name, value, labels=None):
        """Set a gauge metric"""
        # TODO: Implement gauge with labels
        pass
        
    def histogram(self, metric_name, value, labels=None):
        """Record a histogram value"""
        # TODO: Implement histogram with percentile calculation
        pass
        
    def get_metrics(self):
        """Get all metrics in Prometheus format"""
        # TODO: Export metrics in standard format
        pass

# Exercise: Instrument a web service
class WebService:
    def __init__(self):
        self.metrics = MetricsCollector()
        
    def handle_request(self, endpoint, method):
        start_time = time.time()
        
        # TODO: Instrument the request handling
        # - Count requests by endpoint and method
        # - Record latency histogram
        # - Track concurrent requests (gauge)
        # - Count errors by type
        
        # Simulate processing
        time.sleep(0.1)
        
        # Simulate occasional errors
        import random
        if random.random() < 0.1:
            raise Exception("Internal error")

# Test the metrics system
def test_metrics():
    service = WebService()
    
    # Simulate traffic
    for i in range(100):
        try:
            service.handle_request('/api/users', 'GET')
        except:
            pass
            
    # Get metrics report
    print(service.metrics.get_metrics())
```

<details>
<summary>Solution</summary>

```python
import time
import statistics
from collections import defaultdict
from threading import Lock
import random

class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(lambda: defaultdict(int))
        self.gauges = defaultdict(lambda: defaultdict(float))
        self.histograms = defaultdict(lambda: defaultdict(list))
        self.lock = Lock()
        
    def _labels_key(self, labels):
        """Convert labels dict to hashable key"""
        if not labels:
            return ''
        return ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        
    def increment(self, metric_name, value=1, labels=None):
        """Increment a counter metric"""
        with self.lock:
            labels_key = self._labels_key(labels)
            self.counters[metric_name][labels_key] += value
            
    def gauge(self, metric_name, value, labels=None):
        """Set a gauge metric"""
        with self.lock:
            labels_key = self._labels_key(labels)
            self.gauges[metric_name][labels_key] = value
            
    def histogram(self, metric_name, value, labels=None):
        """Record a histogram value"""
        with self.lock:
            labels_key = self._labels_key(labels)
            self.histograms[metric_name][labels_key].append(value)
            
    def _calculate_percentiles(self, values):
        """Calculate percentiles for histogram"""
        if not values:
            return {}
            
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def percentile(p):
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < n:
                return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
            else:
                return sorted_values[f]
                
        return {
            'count': n,
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': statistics.mean(sorted_values),
            'p50': percentile(0.50),
            'p95': percentile(0.95),
            'p99': percentile(0.99),
            'p999': percentile(0.999),
        }
        
    def get_metrics(self):
        """Get all metrics in Prometheus format"""
        lines = []
        
        with self.lock:
            # Export counters
            for metric_name, label_values in self.counters.items():
                lines.append(f'# TYPE {metric_name} counter')
                for labels_key, value in label_values.items():
                    if labels_key:
                        lines.append(f'{metric_name}{{{labels_key}}} {value}')
                    else:
                        lines.append(f'{metric_name} {value}')
                        
            # Export gauges
            for metric_name, label_values in self.gauges.items():
                lines.append(f'# TYPE {metric_name} gauge')
                for labels_key, value in label_values.items():
                    if labels_key:
                        lines.append(f'{metric_name}{{{labels_key}}} {value}')
                    else:
                        lines.append(f'{metric_name} {value}')
                        
            # Export histograms
            for metric_name, label_values in self.histograms.items():
                lines.append(f'# TYPE {metric_name} histogram')
                for labels_key, values in label_values.items():
                    stats = self._calculate_percentiles(values)
                    
                    # Export percentiles
                    for percentile, value in [
                        ('0.5', stats.get('p50', 0)),
                        ('0.95', stats.get('p95', 0)),
                        ('0.99', stats.get('p99', 0)),
                        ('0.999', stats.get('p999', 0)),
                    ]:
                        if labels_key:
                            lines.append(f'{metric_name}{{quantile="{percentile}",{labels_key}}} {value:.6f}')
                        else:
                            lines.append(f'{metric_name}{{quantile="{percentile}"}} {value:.6f}')
                            
                    # Export sum and count
                    total = sum(values) if values else 0
                    count = len(values)
                    if labels_key:
                        lines.append(f'{metric_name}_sum{{{labels_key}}} {total:.6f}')
                        lines.append(f'{metric_name}_count{{{labels_key}}} {count}')
                    else:
                        lines.append(f'{metric_name}_sum {total:.6f}')
                        lines.append(f'{metric_name}_count {count}')
                        
        return '\n'.join(lines)

# Enhanced WebService with proper instrumentation
class WebService:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.concurrent_requests = 0
        self.request_lock = Lock()
        
    def handle_request(self, endpoint, method, user_id=None):
        # Track concurrent requests
        with self.request_lock:
            self.concurrent_requests += 1
            self.metrics.gauge('http_concurrent_requests', self.concurrent_requests)
            
        start_time = time.time()
        status = '200'
        
        try:
            # Count request
            self.metrics.increment('http_requests_total', 
                                 labels={'endpoint': endpoint, 'method': method})
            
            # Simulate processing with variable latency
            base_latency = 0.05
            if endpoint == '/api/users':
                latency = base_latency + random.uniform(0, 0.05)
            elif endpoint == '/api/orders':
                latency = base_latency + random.uniform(0, 0.15)
            else:
                latency = base_latency + random.uniform(0, 0.02)
                
            time.sleep(latency)
            
            # Simulate occasional errors
            error_rate = 0.05 if endpoint == '/api/orders' else 0.02
            if random.random() < error_rate:
                if random.random() < 0.7:
                    status = '500'
                    raise Exception("Internal server error")
                else:
                    status = '503'
                    raise Exception("Service unavailable")
                    
            # Simulate client errors
            if random.random() < 0.01:
                status = '400'
                raise ValueError("Bad request")
                
            return {'status': 'success', 'data': 'response'}
            
        except ValueError:
            self.metrics.increment('http_errors_total',
                                 labels={'endpoint': endpoint, 'method': method, 'error': 'client'})
            raise
            
        except Exception as e:
            self.metrics.increment('http_errors_total',
                                 labels={'endpoint': endpoint, 'method': method, 'error': 'server'})
            raise
            
        finally:
            # Record latency
            duration = time.time() - start_time
            self.metrics.histogram('http_request_duration_seconds',
                                 duration,
                                 labels={'endpoint': endpoint, 'method': method, 'status': status})
            
            # Update concurrent requests
            with self.request_lock:
                self.concurrent_requests -= 1
                self.metrics.gauge('http_concurrent_requests', self.concurrent_requests)

# Advanced metrics test
def test_advanced_metrics():
    print("=== Advanced Metrics Collection Test ===\n")
    
    service = WebService()
    
    # Simulate realistic traffic patterns
    endpoints = [
        ('/api/users', 'GET', 0.7),
        ('/api/users', 'POST', 0.1),
        ('/api/orders', 'GET', 0.15),
        ('/api/orders', 'POST', 0.05),
    ]
    
    # Generate load
    total_requests = 1000
    successful = 0
    failed = 0
    
    print(f"Simulating {total_requests} requests...")
    
    for i in range(total_requests):
        # Choose endpoint based on weights
        r = random.random()
        cumulative = 0
        for endpoint, method, weight in endpoints:
            cumulative += weight
            if r < cumulative:
                break
                
        try:
            service.handle_request(endpoint, method, user_id=f'user_{i % 100}')
            successful += 1
        except:
            failed += 1
            
        # Simulate concurrent requests
        if i % 10 == 0:
            time.sleep(0.001)  # Brief pause to simulate real traffic
    
    print(f"\nResults:")
    print(f"  Successful requests: {successful}")
    print(f"  Failed requests: {failed}")
    print(f"  Success rate: {successful/total_requests:.1%}")
    
    # Display metrics
    print("\n" + "="*60)
    print("METRICS OUTPUT (Prometheus Format)")
    print("="*60)
    print(service.metrics.get_metrics())
    
    # Calculate SLIs
    print("\n" + "="*60)
    print("SERVICE LEVEL INDICATORS")
    print("="*60)
    
    # Get error rate
    with service.metrics.lock:
        total_requests_by_endpoint = {}
        total_errors_by_endpoint = {}
        
        for labels_key, count in service.metrics.counters['http_requests_total'].items():
            if labels_key:
                # Parse endpoint from labels
                for label in labels_key.split(','):
                    if label.startswith('endpoint='):
                        endpoint = label.split('"')[1]
                        total_requests_by_endpoint[endpoint] = total_requests_by_endpoint.get(endpoint, 0) + count
                        
        for labels_key, count in service.metrics.counters['http_errors_total'].items():
            if labels_key:
                for label in labels_key.split(','):
                    if label.startswith('endpoint='):
                        endpoint = label.split('"')[1]
                        total_errors_by_endpoint[endpoint] = total_errors_by_endpoint.get(endpoint, 0) + count
    
    for endpoint in total_requests_by_endpoint:
        total = total_requests_by_endpoint[endpoint]
        errors = total_errors_by_endpoint.get(endpoint, 0)
        error_rate = errors / total if total > 0 else 0
        print(f"\n{endpoint}:")
        print(f"  Total requests: {total}")
        print(f"  Error rate: {error_rate:.2%}")
        print(f"  Success rate: {(1-error_rate):.2%}")

# Run the test
test_advanced_metrics()

# Demonstrate cardinality issues
def demonstrate_cardinality():
    print("\n\n=== Cardinality Demonstration ===\n")
    
    # Bad: High cardinality
    bad_metrics = MetricsCollector()
    print("Bad practice - High cardinality metrics:")
    
    for i in range(100):
        # This creates unique label combination for each user
        bad_metrics.increment('user_requests', 
                            labels={'user_id': f'user_{i}', 
                                   'session_id': f'session_{i}'})
    
    bad_output = bad_metrics.get_metrics()
    print(f"Lines of output: {len(bad_output.splitlines())}")
    print("(Each unique label combination creates a new time series!)\n")
    
    # Good: Bounded cardinality
    good_metrics = MetricsCollector()
    print("Good practice - Bounded cardinality:")
    
    for i in range(100):
        # Limited set of label values
        good_metrics.increment('requests', 
                             labels={'endpoint': '/api/users',
                                    'method': 'GET',
                                    'status': '200'})
    
    good_output = good_metrics.get_metrics()
    print(f"Lines of output: {len(good_output.splitlines())}")
    print("(Fixed set of labels keeps cardinality bounded)")

demonstrate_cardinality()
```

</details>

## Exercise 3: Distributed Tracing

### 🔧 Try This: Implement Trace Propagation

```python
import uuid
import time
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict = None
    logs: List = None
    
class Tracer:
    def __init__(self):
        self.spans = []
        
    def start_span(self, operation_name, parent_span=None):
        """Start a new span"""
        # TODO: Implement span creation
        # Generate IDs, set parent relationship
        pass
        
    def inject(self, span, carrier):
        """Inject trace context into carrier (e.g., HTTP headers)"""
        # TODO: Implement context injection
        pass
        
    def extract(self, carrier):
        """Extract trace context from carrier"""
        # TODO: Implement context extraction
        pass

# Exercise: Trace a distributed operation
class DistributedSystem:
    def __init__(self):
        self.tracer = Tracer()
        
    def frontend_service(self, request):
        """Simulate frontend service"""
        # TODO: Start root span
        # Call backend service
        # Propagate trace context
        pass
        
    def backend_service(self, request, trace_context):
        """Simulate backend service"""
        # TODO: Extract trace context
        # Start child span
        # Call database
        pass
        
    def database_operation(self, query, trace_context):
        """Simulate database operation"""
        # TODO: Create span for DB operation
        pass

# Test distributed tracing
def test_tracing():
    system = DistributedSystem()
    
    # Simulate request flow
    request = {'user_id': 'user_123', 'action': 'get_profile'}
    system.frontend_service(request)
    
    # Visualize trace
    # TODO: Show parent-child relationships
    # Calculate total latency, identify bottlenecks
```

<details>
<summary>Solution</summary>

```python
import uuid
import time
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
import threading

@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict = field(default_factory=dict)
    logs: List = field(default_factory=list)
    
    def set_tag(self, key: str, value: Any):
        """Set a tag on the span"""
        self.tags[key] = value
        
    def log(self, message: str, **fields):
        """Add a log entry to the span"""
        self.logs.append({
            'timestamp': time.time(),
            'message': message,
            'fields': fields
        })
        
    def finish(self):
        """Mark span as finished"""
        if self.end_time is None:
            self.end_time = time.time()
            
    @property
    def duration_ms(self):
        """Get span duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None

class TraceContext:
    def __init__(self, trace_id: str, span_id: str, parent_span_id: Optional[str] = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id

class Tracer:
    def __init__(self):
        self.spans: List[Span] = []
        self.current_span = threading.local()
        
    def start_span(self, operation_name: str, 
                   service_name: str,
                   parent_context: Optional[TraceContext] = None) -> Span:
        """Start a new span"""
        if parent_context:
            trace_id = parent_context.trace_id
            parent_span_id = parent_context.span_id
        else:
            trace_id = str(uuid.uuid4())
            parent_span_id = None
            
        span_id = str(uuid.uuid4())
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            start_time=time.time()
        )
        
        self.spans.append(span)
        return span
        
    @contextmanager
    def span(self, operation_name: str, service_name: str, 
             parent_context: Optional[TraceContext] = None):
        """Context manager for spans"""
        span = self.start_span(operation_name, service_name, parent_context)
        self.current_span.span = span
        
        try:
            yield span
        except Exception as e:
            span.set_tag('error', True)
            span.set_tag('error.type', type(e).__name__)
            span.set_tag('error.message', str(e))
            raise
        finally:
            span.finish()
            
    def inject(self, span: Span, carrier: Dict[str, str]):
        """Inject trace context into carrier (e.g., HTTP headers)"""
        carrier['X-Trace-ID'] = span.trace_id
        carrier['X-Span-ID'] = span.span_id
        if span.parent_span_id:
            carrier['X-Parent-Span-ID'] = span.parent_span_id
            
    def extract(self, carrier: Dict[str, str]) -> Optional[TraceContext]:
        """Extract trace context from carrier"""
        trace_id = carrier.get('X-Trace-ID')
        parent_span_id = carrier.get('X-Span-ID')  # The sender's span becomes parent
        
        if trace_id:
            return TraceContext(
                trace_id=trace_id,
                span_id=None,  # Will be generated
                parent_span_id=parent_span_id
            )
        return None
        
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        return [s for s in self.spans if s.trace_id == trace_id]
        
    def print_trace(self, trace_id: str):
        """Print trace in a tree format"""
        spans = self.get_trace(trace_id)
        if not spans:
            print(f"No trace found with ID: {trace_id}")
            return
            
        # Build span tree
        root_spans = [s for s in spans if s.parent_span_id is None]
        
        def print_span_tree(span: Span, indent: int = 0):
            duration = f"{span.duration_ms:.2f}ms" if span.duration_ms else "ongoing"
            prefix = "  " * indent + "└─ " if indent > 0 else ""
            
            print(f"{prefix}[{span.service_name}] {span.operation_name} ({duration})")
            
            # Print tags
            if span.tags:
                for key, value in span.tags.items():
                    print(f"{'  ' * (indent + 1)}  {key}: {value}")
                    
            # Find children
            children = [s for s in spans if s.parent_span_id == span.span_id]
            for child in sorted(children, key=lambda x: x.start_time):
                print_span_tree(child, indent + 1)
                
        for root in root_spans:
            print(f"\nTrace ID: {root.trace_id}")
            print(f"Total Duration: {self.calculate_trace_duration(trace_id):.2f}ms")
            print("Trace Tree:")
            print_span_tree(root)
            
    def calculate_trace_duration(self, trace_id: str) -> float:
        """Calculate total trace duration"""
        spans = self.get_trace(trace_id)
        if not spans:
            return 0
            
        start = min(s.start_time for s in spans)
        end = max(s.end_time or s.start_time for s in spans)
        return (end - start) * 1000

# Distributed system with proper tracing
class DistributedSystem:
    def __init__(self):
        self.tracer = Tracer()
        
    def frontend_service(self, request: Dict) -> Dict:
        """Simulate frontend service"""
        with self.tracer.span('handle_request', 'frontend') as span:
            span.set_tag('http.method', 'GET')
            span.set_tag('http.path', '/api/profile')
            span.set_tag('user.id', request.get('user_id'))
            
            # Validate request
            time.sleep(0.01)  # Simulate validation
            span.log('Request validated')
            
            # Call backend service
            headers = {}
            self.tracer.inject(span, headers)
            
            response = self.backend_service(request, headers)
            
            span.set_tag('http.status_code', 200)
            return response
            
    def backend_service(self, request: Dict, headers: Dict) -> Dict:
        """Simulate backend service"""
        # Extract trace context
        parent_context = self.tracer.extract(headers)
        
        with self.tracer.span('process_request', 'backend', parent_context) as span:
            span.set_tag('request.type', request.get('action'))
            
            # Business logic
            time.sleep(0.02)  # Simulate processing
            span.log('Business logic executed')
            
            # Call database
            db_headers = {}
            self.tracer.inject(span, db_headers)
            
            user_data = self.database_operation(
                f"SELECT * FROM users WHERE id = '{request['user_id']}'",
                db_headers
            )
            
            # Call cache service in parallel
            cache_data = self.cache_service(request['user_id'], db_headers)
            
            span.set_tag('cache.hit', cache_data is not None)
            
            return {
                'user': user_data,
                'cached_preferences': cache_data
            }
            
    def database_operation(self, query: str, headers: Dict) -> Dict:
        """Simulate database operation"""
        parent_context = self.tracer.extract(headers)
        
        with self.tracer.span('db_query', 'database', parent_context) as span:
            span.set_tag('db.type', 'postgresql')
            span.set_tag('db.statement', query)
            
            # Simulate query execution
            time.sleep(0.05)  # Databases are slower
            
            span.set_tag('db.rows_affected', 1)
            
            return {
                'id': 'user_123',
                'name': 'John Doe',
                'email': 'john@example.com'
            }
            
    def cache_service(self, key: str, headers: Dict) -> Optional[Dict]:
        """Simulate cache service"""
        parent_context = self.tracer.extract(headers)
        
        with self.tracer.span('cache_lookup', 'cache', parent_context) as span:
            span.set_tag('cache.key', key)
            
            # Simulate cache miss 30% of the time
            import random
            if random.random() < 0.3:
                time.sleep(0.001)  # Fast miss
                span.set_tag('cache.hit', False)
                return None
            else:
                time.sleep(0.003)  # Slightly slower hit
                span.set_tag('cache.hit', True)
                return {'theme': 'dark', 'language': 'en'}

# Advanced tracing test
def test_distributed_tracing():
    print("=== Distributed Tracing Test ===\n")
    
    system = DistributedSystem()
    
    # Simulate multiple requests
    requests = [
        {'user_id': 'user_123', 'action': 'get_profile'},
        {'user_id': 'user_456', 'action': 'get_profile'},
        {'user_id': 'user_789', 'action': 'get_profile'},
    ]
    
    trace_ids = []
    
    for request in requests:
        print(f"Processing request for {request['user_id']}...")
        response = system.frontend_service(request)
        
        # Get trace ID from the first span
        if system.tracer.spans:
            trace_ids.append(system.tracer.spans[-1].trace_id)
    
    # Display traces
    print("\n" + "="*60)
    print("TRACE VISUALIZATION")
    print("="*60)
    
    for trace_id in set(trace_ids):
        system.tracer.print_trace(trace_id)
        
    # Analyze performance
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS")
    print("="*60)
    
    # Find slowest operations
    all_spans = sorted(system.tracer.spans, 
                      key=lambda x: x.duration_ms or 0, 
                      reverse=True)
    
    print("\nSlowest Operations:")
    for span in all_spans[:5]:
        if span.duration_ms:
            print(f"  {span.service_name}/{span.operation_name}: {span.duration_ms:.2f}ms")
    
    # Service-level metrics
    service_times = defaultdict(list)
    for span in system.tracer.spans:
        if span.duration_ms:
            service_times[span.service_name].append(span.duration_ms)
    
    print("\nService Performance:")
    for service, times in service_times.items():
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
        print(f"  {service}:")
        print(f"    Average: {avg_time:.2f}ms")
        print(f"    P95: {p95_time:.2f}ms")
    
    # Error analysis
    error_spans = [s for s in system.tracer.spans if s.tags.get('error')]
    if error_spans:
        print(f"\nErrors detected: {len(error_spans)}")
        for span in error_spans:
            print(f"  {span.service_name}/{span.operation_name}: {span.tags.get('error.message')}")

# Run the test
test_distributed_tracing()

# Demonstrate sampling strategies
def demonstrate_sampling():
    print("\n\n=== Sampling Strategies ===\n")
    
    class SamplingTracer(Tracer):
        def __init__(self, sampling_rate=0.1):
            super().__init__()
            self.sampling_rate = sampling_rate
            self.sampled_traces = set()
            
        def should_sample(self, trace_id: str, span: Span) -> bool:
            """Determine if span should be sampled"""
            # Always sample errors
            if span.tags.get('error'):
                return True
                
            # Always sample slow operations (>100ms)
            if span.duration_ms and span.duration_ms > 100:
                return True
                
            # Sample based on trace ID (consistent sampling)
            if trace_id in self.sampled_traces:
                return True
                
            # Random sampling for new traces
            if random.random() < self.sampling_rate:
                self.sampled_traces.add(trace_id)
                return True
                
            return False
    
    # Test sampling
    sampler = SamplingTracer(sampling_rate=0.1)
    
    sampled = 0
    total = 1000
    
    for i in range(total):
        trace_id = str(uuid.uuid4())
        span = Span(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=None,
            operation_name='test_op',
            service_name='test_service',
            start_time=time.time()
        )
        
        # Simulate some errors and slow operations
        if i % 50 == 0:
            span.set_tag('error', True)
        if i % 20 == 0:
            span.end_time = span.start_time + 0.150  # 150ms
            
        span.finish()
        
        if sampler.should_sample(trace_id, span):
            sampled += 1
            
    print(f"Sampling Results:")
    print(f"  Total spans: {total}")
    print(f"  Sampled: {sampled}")
    print(f"  Sampling rate: {sampled/total:.1%}")
    print(f"  (Higher than 10% due to error and latency sampling)")

demonstrate_sampling()
```

</details>

## Exercise 4: Build an Alert System

### 🔧 Try This: Implement Smart Alerting

```python
class AlertRule:
    def __init__(self, name, condition, threshold, duration):
        self.name = name
        self.condition = condition  # function that returns current value
        self.threshold = threshold
        self.duration = duration  # how long condition must be true
        
class AlertManager:
    def __init__(self):
        self.rules = []
        self.alerts = []
        
    def add_rule(self, rule):
        """Add an alert rule"""
        # TODO: Implement rule management
        pass
        
    def evaluate(self, metrics):
        """Evaluate all rules against current metrics"""
        # TODO: Check conditions
        # Track duration of violations
        # Avoid flapping
        pass
        
    def send_alert(self, alert):
        """Send alert (mock)"""
        # TODO: Implement alert routing
        # Consider severity, on-call schedule
        # Avoid alert storms
        pass

# Exercise: Create realistic alert rules
def create_alert_rules():
    # TODO: Define alerts for:
    # - High error rate (>1% for 5 minutes)
    # - Slow response time (P95 > 1s for 10 minutes)
    # - Resource saturation (CPU > 80% for 15 minutes)
    # - Business metrics (orders/min < 10 for 5 minutes)
    pass

# Test alerting system
def test_alerting():
    manager = AlertManager()
    
    # Add rules
    # Simulate metrics over time
    # Verify alerts fire correctly
    # Test alert suppression
    pass
```

<details>
<summary>Solution</summary>

```python
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional, Any
from collections import defaultdict, deque
import statistics

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    PAGE = "page"  # Wake someone up

class AlertState(Enum):
    INACTIVE = "inactive"
    PENDING = "pending"  # Condition met, waiting for duration
    FIRING = "firing"
    RESOLVED = "resolved"

class AlertRule:
    def __init__(self, 
                 name: str,
                 condition: Callable[[Dict], bool],
                 value_func: Callable[[Dict], float],
                 threshold: float,
                 duration_seconds: int,
                 severity: AlertSeverity = AlertSeverity.WARNING,
                 labels: Dict = None,
                 annotations: Dict = None):
        self.name = name
        self.condition = condition
        self.value_func = value_func
        self.threshold = threshold
        self.duration_seconds = duration_seconds
        self.severity = severity
        self.labels = labels or {}
        self.annotations = annotations or {}
        
        # State tracking
        self.state = AlertState.INACTIVE
        self.pending_since = None
        self.firing_since = None
        self.resolved_at = None
        self.current_value = None
        
class Alert:
    def __init__(self, rule: AlertRule, timestamp: datetime):
        self.rule = rule
        self.fired_at = timestamp
        self.resolved_at = None
        self.alert_id = f"{rule.name}_{timestamp.timestamp()}"
        self.values_when_fired = []
        
    def resolve(self, timestamp: datetime):
        self.resolved_at = timestamp
        
    @property
    def duration(self) -> Optional[timedelta]:
        if self.resolved_at:
            return self.resolved_at - self.fired_at
        return None

class AlertManager:
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.suppression_rules = []
        self.notification_channels = []
        
        # For flap detection
        self.state_changes = defaultdict(lambda: deque(maxlen=10))
        
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules.append(rule)
        
    def add_suppression_rule(self, suppression_func: Callable):
        """Add rule to suppress alerts (e.g., during maintenance)"""
        self.suppression_rules.append(suppression_func)
        
    def add_notification_channel(self, channel: Callable):
        """Add notification channel (email, Slack, PagerDuty, etc.)"""
        self.notification_channels.append(channel)
        
    def evaluate(self, metrics: Dict, timestamp: datetime = None):
        """Evaluate all rules against current metrics"""
        if timestamp is None:
            timestamp = datetime.now()
            
        for rule in self.rules:
            try:
                # Get current value
                current_value = rule.value_func(metrics)
                rule.current_value = current_value
                
                # Check condition
                condition_met = rule.condition(metrics)
                
                # State machine
                if rule.state == AlertState.INACTIVE:
                    if condition_met:
                        rule.state = AlertState.PENDING
                        rule.pending_since = timestamp
                        self._record_state_change(rule.name, AlertState.PENDING, timestamp)
                        
                elif rule.state == AlertState.PENDING:
                    if not condition_met:
                        # Condition cleared before duration
                        rule.state = AlertState.INACTIVE
                        rule.pending_since = None
                        self._record_state_change(rule.name, AlertState.INACTIVE, timestamp)
                    else:
                        # Check if duration exceeded
                        elapsed = (timestamp - rule.pending_since).total_seconds()
                        if elapsed >= rule.duration_seconds:
                            # Fire alert!
                            rule.state = AlertState.FIRING
                            rule.firing_since = timestamp
                            self._fire_alert(rule, timestamp)
                            
                elif rule.state == AlertState.FIRING:
                    if not condition_met:
                        # Resolve alert
                        rule.state = AlertState.RESOLVED
                        rule.resolved_at = timestamp
                        self._resolve_alert(rule, timestamp)
                        
                elif rule.state == AlertState.RESOLVED:
                    if condition_met:
                        # Re-triggered
                        rule.state = AlertState.PENDING
                        rule.pending_since = timestamp
                        self._record_state_change(rule.name, AlertState.PENDING, timestamp)
                    else:
                        # Reset to inactive after some time
                        elapsed = (timestamp - rule.resolved_at).total_seconds()
                        if elapsed > 300:  # 5 minutes
                            rule.state = AlertState.INACTIVE
                            rule.resolved_at = None
                            self._record_state_change(rule.name, AlertState.INACTIVE, timestamp)
                            
            except Exception as e:
                print(f"Error evaluating rule {rule.name}: {e}")
                
    def _record_state_change(self, rule_name: str, new_state: AlertState, timestamp: datetime):
        """Record state change for flap detection"""
        self.state_changes[rule_name].append((timestamp, new_state))
        
    def _is_flapping(self, rule_name: str) -> bool:
        """Detect if alert is flapping"""
        changes = self.state_changes[rule_name]
        if len(changes) < 6:
            return False
            
        # Count state transitions in last 5 minutes
        five_min_ago = datetime.now() - timedelta(minutes=5)
        recent_changes = [c for c in changes if c[0] > five_min_ago]
        
        return len(recent_changes) >= 6  # Flapping if 6+ changes in 5 min
        
    def _should_suppress(self, rule: AlertRule, timestamp: datetime) -> bool:
        """Check if alert should be suppressed"""
        for suppress_func in self.suppression_rules:
            if suppress_func(rule, timestamp):
                return True
                
        # Suppress if flapping
        if self._is_flapping(rule.name):
            print(f"Suppressing {rule.name} due to flapping")
            return True
            
        return False
        
    def _fire_alert(self, rule: AlertRule, timestamp: datetime):
        """Fire an alert"""
        if self._should_suppress(rule, timestamp):
            return
            
        alert = Alert(rule, timestamp)
        alert.values_when_fired.append(rule.current_value)
        
        self.active_alerts[rule.name] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        self._send_notifications(alert, "FIRING")
        
    def _resolve_alert(self, rule: AlertRule, timestamp: datetime):
        """Resolve an alert"""
        if rule.name in self.active_alerts:
            alert = self.active_alerts[rule.name]
            alert.resolve(timestamp)
            del self.active_alerts[rule.name]
            
            # Send notifications
            self._send_notifications(alert, "RESOLVED")
            
    def _send_notifications(self, alert: Alert, status: str):
        """Send notifications through all channels"""
        for channel in self.notification_channels:
            try:
                channel(alert, status)
            except Exception as e:
                print(f"Failed to send notification: {e}")
                
    def get_alert_summary(self) -> Dict:
        """Get summary of alert system state"""
        return {
            'active_alerts': len(self.active_alerts),
            'rules_total': len(self.rules),
            'rules_pending': sum(1 for r in self.rules if r.state == AlertState.PENDING),
            'rules_firing': sum(1 for r in self.rules if r.state == AlertState.FIRING),
            'alerts_last_hour': sum(1 for a in self.alert_history 
                                   if a.fired_at > datetime.now() - timedelta(hours=1)),
        }

# Create comprehensive alert rules
def create_production_alert_rules():
    rules = []
    
    # 1. High error rate
    rules.append(AlertRule(
        name="high_error_rate",
        condition=lambda m: m.get('error_rate', 0) > 0.01,
        value_func=lambda m: m.get('error_rate', 0) * 100,
        threshold=1.0,  # 1%
        duration_seconds=300,  # 5 minutes
        severity=AlertSeverity.CRITICAL,
        labels={'team': 'platform', 'service': 'api'},
        annotations={
            'summary': 'High error rate detected',
            'description': 'Error rate is {{ .Value }}% which is above 1% threshold'
        }
    ))
    
    # 2. Slow response time
    rules.append(AlertRule(
        name="slow_response_time",
        condition=lambda m: m.get('latency_p95', 0) > 1000,
        value_func=lambda m: m.get('latency_p95', 0),
        threshold=1000,  # 1 second
        duration_seconds=600,  # 10 minutes
        severity=AlertSeverity.WARNING,
        labels={'team': 'platform', 'service': 'api'},
        annotations={
            'summary': 'Response time degraded',
            'description': 'P95 latency is {{ .Value }}ms'
        }
    ))
    
    # 3. CPU saturation
    rules.append(AlertRule(
        name="high_cpu_usage",
        condition=lambda m: m.get('cpu_usage', 0) > 80,
        value_func=lambda m: m.get('cpu_usage', 0),
        threshold=80,
        duration_seconds=900,  # 15 minutes
        severity=AlertSeverity.WARNING,
        labels={'team': 'infrastructure'},
        annotations={
            'summary': 'CPU usage is high',
            'description': 'CPU at {{ .Value }}%'
        }
    ))
    
    # 4. Business metric - low order rate
    rules.append(AlertRule(
        name="low_order_rate",
        condition=lambda m: m.get('orders_per_minute', 100) < 10,
        value_func=lambda m: m.get('orders_per_minute', 0),
        threshold=10,
        duration_seconds=300,  # 5 minutes
        severity=AlertSeverity.PAGE,  # This is money!
        labels={'team': 'business', 'revenue_impact': 'high'},
        annotations={
            'summary': 'Order rate critically low',
            'description': 'Only {{ .Value }} orders/min',
            'runbook': 'https://wiki/low-order-rate-runbook'
        }
    ))
    
    # 5. Memory pressure
    rules.append(AlertRule(
        name="memory_pressure",
        condition=lambda m: m.get('memory_usage', 0) > 85,
        value_func=lambda m: m.get('memory_usage', 0),
        threshold=85,
        duration_seconds=300,
        severity=AlertSeverity.WARNING,
        labels={'team': 'infrastructure'},
        annotations={
            'summary': 'Memory usage is high',
            'description': 'Memory at {{ .Value }}%, possible OOM risk'
        }
    ))
    
    # 6. Disk space prediction
    rules.append(AlertRule(
        name="disk_will_fill_soon",
        condition=lambda m: m.get('disk_fill_hours', 999) < 6,
        value_func=lambda m: m.get('disk_fill_hours', 999),
        threshold=6,  # Hours until full
        duration_seconds=60,  # 1 minute (urgent!)
        severity=AlertSeverity.CRITICAL,
        labels={'team': 'infrastructure'},
        annotations={
            'summary': 'Disk will fill soon',
            'description': 'Disk will be full in {{ .Value }} hours'
        }
    ))
    
    return rules

# Test the alerting system
def test_comprehensive_alerting():
    print("=== Comprehensive Alerting System Test ===\n")
    
    manager = AlertManager()
    
    # Add rules
    rules = create_production_alert_rules()
    for rule in rules:
        manager.add_rule(rule)
    
    # Add notification channels
    def console_notifier(alert: Alert, status: str):
        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.PAGE: "📟"
        }
        
        emoji = severity_emoji.get(alert.rule.severity, "❓")
        
        if status == "FIRING":
            print(f"\n{emoji} ALERT FIRING: {alert.rule.name}")
            print(f"   Severity: {alert.rule.severity.value}")
            print(f"   Value: {alert.rule.current_value}")
            print(f"   Threshold: {alert.rule.threshold}")
            print(f"   Labels: {alert.rule.labels}")
        else:
            duration = alert.duration
            print(f"\n✅ ALERT RESOLVED: {alert.rule.name}")
            if duration:
                print(f"   Duration: {duration}")
    
    manager.add_notification_channel(console_notifier)
    
    # Add suppression rule (maintenance window)
    maintenance_start = datetime.now() + timedelta(hours=2)
    maintenance_end = maintenance_start + timedelta(hours=1)
    
    def maintenance_suppression(rule: AlertRule, timestamp: datetime) -> bool:
        return maintenance_start <= timestamp <= maintenance_end
    
    manager.add_suppression_rule(maintenance_suppression)
    
    # Simulate metrics over time
    print("Simulating system metrics over time...\n")
    
    # Normal → High Error → Recovery → CPU Spike → Normal
    scenarios = [
        # Normal operation
        {'error_rate': 0.002, 'latency_p95': 200, 'cpu_usage': 45, 
         'memory_usage': 60, 'orders_per_minute': 50, 'disk_fill_hours': 72},
         
        # Error rate spike (should fire after 5 min)
        {'error_rate': 0.025, 'latency_p95': 500, 'cpu_usage': 65,
         'memory_usage': 70, 'orders_per_minute': 30, 'disk_fill_hours': 48},
         
        # Sustained high error
        {'error_rate': 0.03, 'latency_p95': 800, 'cpu_usage': 75,
         'memory_usage': 75, 'orders_per_minute': 20, 'disk_fill_hours': 36},
         
        # Recovery begins
        {'error_rate': 0.008, 'latency_p95': 300, 'cpu_usage': 50,
         'memory_usage': 65, 'orders_per_minute': 45, 'disk_fill_hours': 48},
         
        # Normal again
        {'error_rate': 0.001, 'latency_p95': 150, 'cpu_usage': 40,
         'memory_usage': 55, 'orders_per_minute': 55, 'disk_fill_hours': 72},
         
        # CPU spike
        {'error_rate': 0.002, 'latency_p95': 200, 'cpu_usage': 88,
         'memory_usage': 60, 'orders_per_minute': 50, 'disk_fill_hours': 72},
         
        # Disk filling
        {'error_rate': 0.001, 'latency_p95': 180, 'cpu_usage': 45,
         'memory_usage': 58, 'orders_per_minute': 52, 'disk_fill_hours': 4},
    ]
    
    # Run simulation
    base_time = datetime.now()
    
    for minute in range(len(scenarios) * 6):  # 6 minutes per scenario
        scenario_idx = minute // 6
        if scenario_idx >= len(scenarios):
            break
            
        metrics = scenarios[scenario_idx]
        current_time = base_time + timedelta(minutes=minute)
        
        # Add some noise
        import random
        for key in metrics:
            if key != 'disk_fill_hours':
                metrics[key] *= (1 + random.uniform(-0.1, 0.1))
        
        # Evaluate rules
        manager.evaluate(metrics, current_time)
        
        # Print status every 2 minutes
        if minute % 2 == 0:
            summary = manager.get_alert_summary()
            print(f"\nTime: +{minute}min | "
                  f"Active: {summary['active_alerts']} | "
                  f"Pending: {summary['rules_pending']} | "
                  f"Firing: {summary['rules_firing']}")
    
    # Final summary
    print("\n" + "="*60)
    print("ALERT SUMMARY")
    print("="*60)
    
    print(f"\nTotal alerts fired: {len(manager.alert_history)}")
    
    # Group by rule
    alerts_by_rule = defaultdict(list)
    for alert in manager.alert_history:
        alerts_by_rule[alert.rule.name].append(alert)
    
    print("\nAlerts by rule:")
    for rule_name, alerts in alerts_by_rule.items():
        avg_duration = statistics.mean([
            a.duration.total_seconds() 
            for a in alerts 
            if a.duration
        ] or [0])
        
        print(f"  {rule_name}:")
        print(f"    Count: {len(alerts)}")
        print(f"    Avg duration: {avg_duration:.1f}s")

# Run the test
test_comprehensive_alerting()
```

</details>

## Exercise 5: Observability Dashboard

### 🔧 Try This: Design a Monitoring Dashboard

```python
class Dashboard:
    def __init__(self, title):
        self.title = title
        self.panels = []
        
    def add_panel(self, panel):
        self.panels.append(panel)
        
    def render(self, metrics):
        """Render dashboard with current metrics"""
        # TODO: Create text-based dashboard
        # Show four golden signals
        # Include sparklines for trends
        # Highlight anomalies
        pass

class Panel:
    def __init__(self, title, metric_name, panel_type='graph'):
        self.title = title
        self.metric_name = metric_name
        self.panel_type = panel_type
        self.history = []
        
    def update(self, value):
        """Update panel with new value"""
        # TODO: Maintain history
        # Calculate statistics
        pass
        
    def render(self):
        """Render panel as text"""
        # TODO: Create ASCII visualization
        pass

# Exercise: Create a service dashboard
def create_service_dashboard():
    dashboard = Dashboard("API Service Health")
    
    # TODO: Add panels for:
    # - Request rate (graph)
    # - Error rate (graph with threshold)
    # - P50/P95/P99 latency (multi-line)
    # - CPU/Memory usage (gauge)
    # - Active connections (counter)
    
    return dashboard

# Test dashboard rendering
def test_dashboard():
    dashboard = create_service_dashboard()
    
    # Simulate metrics updates
    # Render dashboard
    # Show how metrics change over time
    pass
```

<details>
<summary>Solution</summary>

```python
import time
import random
from collections import deque
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import math

class Panel:
    def __init__(self, title: str, metric_name: str, 
                 panel_type: str = 'graph',
                 width: int = 50, height: int = 10,
                 threshold: Optional[float] = None):
        self.title = title
        self.metric_name = metric_name
        self.panel_type = panel_type
        self.width = width
        self.height = height
        self.threshold = threshold
        self.history = deque(maxlen=width)
        self.current_value = 0
        
    def update(self, value: float):
        """Update panel with new value"""
        self.current_value = value
        self.history.append(value)
        
    def render(self) -> List[str]:
        """Render panel as text"""
        lines = []
        lines.append(f"┌{'─' * (self.width + 2)}┐")
        lines.append(f"│ {self.title:<{self.width}} │")
        lines.append(f"├{'─' * (self.width + 2)}┤")
        
        if self.panel_type == 'graph':
            lines.extend(self._render_graph())
        elif self.panel_type == 'gauge':
            lines.extend(self._render_gauge())
        elif self.panel_type == 'counter':
            lines.extend(self._render_counter())
        elif self.panel_type == 'heatmap':
            lines.extend(self._render_heatmap())
            
        lines.append(f"└{'─' * (self.width + 2)}┘")
        return lines
        
    def _render_graph(self) -> List[str]:
        """Render line graph"""
        if not self.history:
            return [f"│ {'No data':<{self.width}} │"]
            
        lines = []
        values = list(self.history)
        
        if len(values) > 0:
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val
            
            if range_val == 0:
                range_val = 1
                
            # Create graph
            graph_height = self.height - 4
            graph = [[' ' for _ in range(len(values))] for _ in range(graph_height)]
            
            # Plot points
            for i, val in enumerate(values):
                y = int((val - min_val) / range_val * (graph_height - 1))
                y = graph_height - 1 - y  # Invert Y axis
                if 0 <= y < graph_height:
                    graph[y][i] = '●'
                    
            # Add threshold line if specified
            if self.threshold is not None and min_val <= self.threshold <= max_val:
                y = int((self.threshold - min_val) / range_val * (graph_height - 1))
                y = graph_height - 1 - y
                if 0 <= y < graph_height:
                    for x in range(len(values)):
                        if graph[y][x] == ' ':
                            graph[y][x] = '─'
                            
            # Convert to lines
            for row in graph:
                line = ''.join(row)
                lines.append(f"│ {line:<{self.width}} │")
                
            # Add labels
            lines.append(f"│ {f'Max: {max_val:.2f}':<{self.width//2}} "
                        f"{f'Current: {self.current_value:.2f}':>{self.width//2}} │")
                        
        return lines
        
    def _render_gauge(self) -> List[str]:
        """Render gauge/progress bar"""
        lines = []
        
        # Assume gauge goes from 0 to 100
        percent = min(100, max(0, self.current_value))
        filled = int(self.width * percent / 100)
        
        bar = '█' * filled + '░' * (self.width - filled)
        lines.append(f"│ {bar} │")
        lines.append(f"│ {f'{percent:.1f}%':^{self.width}} │")
        
        return lines
        
    def _render_counter(self) -> List[str]:
        """Render single value counter"""
        lines = []
        
        # Format large numbers
        if self.current_value >= 1_000_000:
            display = f"{self.current_value/1_000_000:.2f}M"
        elif self.current_value >= 1_000:
            display = f"{self.current_value/1_000:.2f}K"
        else:
            display = f"{self.current_value:.2f}"
            
        lines.append(f"│ {display:^{self.width}} │")
        
        # Add trend if we have history
        if len(self.history) > 1:
            trend = self.current_value - self.history[-2]
            if trend > 0:
                trend_str = f"↑ +{trend:.1f}"
            elif trend < 0:
                trend_str = f"↓ {trend:.1f}"
            else:
                trend_str = "→ 0.0"
            lines.append(f"│ {trend_str:^{self.width}} │")
            
        return lines
        
    def _render_heatmap(self) -> List[str]:
        """Render heatmap for percentiles"""
        lines = []
        
        if isinstance(self.current_value, dict):
            # Expecting dict with p50, p95, p99
            p50 = self.current_value.get('p50', 0)
            p95 = self.current_value.get('p95', 0)
            p99 = self.current_value.get('p99', 0)
            
            lines.append(f"│ {'P50:':<10} {p50:>8.1f}ms {' ' * (self.width - 20)} │")
            lines.append(f"│ {'P95:':<10} {p95:>8.1f}ms {' ' * (self.width - 20)} │")
            lines.append(f"│ {'P99:':<10} {p99:>8.1f}ms {' ' * (self.width - 20)} │")
            
        return lines

class Dashboard:
    def __init__(self, title: str):
        self.title = title
        self.panels: List[Panel] = []
        self.last_update = datetime.now()
        
    def add_panel(self, panel: Panel):
        self.panels.append(panel)
        
    def update(self, metrics: Dict[str, float]):
        """Update all panels with new metrics"""
        for panel in self.panels:
            if panel.metric_name in metrics:
                panel.update(metrics[panel.metric_name])
                
        self.last_update = datetime.now()
        
    def render(self) -> str:
        """Render complete dashboard"""
        output = []
        
        # Header
        output.append("=" * 80)
        output.append(f"{self.title:^80}")
        output.append(f"Last Update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
        output.append("")
        
        # Arrange panels in grid
        panels_per_row = 2
        for i in range(0, len(self.panels), panels_per_row):
            row_panels = self.panels[i:i + panels_per_row]
            
            # Get rendered lines for each panel
            rendered_panels = [panel.render() for panel in row_panels]
            
            # Find max height
            max_height = max(len(p) for p in rendered_panels)
            
            # Pad panels to same height
            for panel_lines in rendered_panels:
                while len(panel_lines) < max_height:
                    panel_lines.append(" " * len(panel_lines[0]))
                    
            # Combine horizontally
            for line_idx in range(max_height):
                line = "  ".join(panel_lines[panel_idx][line_idx] 
                               for panel_idx in range(len(rendered_panels)))
                output.append(line)
                
            output.append("")  # Space between rows
            
        return "\n".join(output)

def create_service_dashboard() -> Dashboard:
    """Create a comprehensive service dashboard"""
    dashboard = Dashboard("API Service Health Dashboard")
    
    # Request rate
    dashboard.add_panel(Panel(
        title="Request Rate (req/s)",
        metric_name="request_rate",
        panel_type="graph",
        width=35,
        height=8
    ))
    
    # Error rate with threshold
    dashboard.add_panel(Panel(
        title="Error Rate (%)",
        metric_name="error_rate",
        panel_type="graph",
        width=35,
        height=8,
        threshold=1.0  # 1% threshold
    ))
    
    # Latency percentiles
    dashboard.add_panel(Panel(
        title="Latency Percentiles",
        metric_name="latency",
        panel_type="heatmap",
        width=35,
        height=6
    ))
    
    # Active connections
    dashboard.add_panel(Panel(
        title="Active Connections",
        metric_name="active_connections",
        panel_type="counter",
        width=35,
        height=6
    ))
    
    # CPU usage
    dashboard.add_panel(Panel(
        title="CPU Usage",
        metric_name="cpu_usage",
        panel_type="gauge",
        width=35,
        height=4
    ))
    
    # Memory usage
    dashboard.add_panel(Panel(
        title="Memory Usage",
        metric_name="memory_usage",
        panel_type="gauge",
        width=35,
        height=4
    ))
    
    return dashboard

def simulate_metrics(base_metrics: Dict, time_factor: float) -> Dict:
    """Simulate realistic metric changes over time"""
    
    # Add daily pattern
    hour_of_day = (time_factor * 24) % 24
    traffic_multiplier = 0.5 + 0.5 * math.sin((hour_of_day - 6) * math.pi / 12)
    
    # Add some randomness
    metrics = {
        'request_rate': base_metrics['request_rate'] * traffic_multiplier * 
                       (1 + random.uniform(-0.2, 0.2)),
        'error_rate': base_metrics['error_rate'] * 
                     (1 + random.uniform(-0.5, 2.0)),
        'active_connections': int(base_metrics['active_connections'] * 
                                 traffic_multiplier * 
                                 (1 + random.uniform(-0.1, 0.1))),
        'cpu_usage': min(95, base_metrics['cpu_usage'] * traffic_multiplier * 
                        (1 + random.uniform(-0.1, 0.3))),
        'memory_usage': min(95, base_metrics['memory_usage'] + 
                           random.uniform(-5, 5)),
        'latency': {
            'p50': base_metrics['latency']['p50'] * 
                   (1 + random.uniform(-0.1, 0.2)),
            'p95': base_metrics['latency']['p95'] * 
                   (1 + random.uniform(-0.1, 0.3)),
            'p99': base_metrics['latency']['p99'] * 
                   (1 + random.uniform(-0.1, 0.5)),
        }
    }
    
    # Simulate occasional spikes
    if random.random() < 0.05:  # 5% chance of spike
        metrics['error_rate'] *= 5
        metrics['latency']['p99'] *= 2
        
    return metrics

def test_dashboard():
    """Test dashboard with simulated metrics"""
    dashboard = create_service_dashboard()
    
    # Base metrics
    base_metrics = {
        'request_rate': 1000,
        'error_rate': 0.5,
        'active_connections': 250,
        'cpu_usage': 45,
        'memory_usage': 60,
        'latency': {
            'p50': 50,
            'p95': 150,
            'p99': 300
        }
    }
    
    print("Starting dashboard simulation (Press Ctrl+C to stop)...\n")
    
    try:
        time_factor = 0
        while True:
            # Simulate metrics
            current_metrics = simulate_metrics(base_metrics, time_factor)
            
            # Update dashboard
            dashboard.update(current_metrics)
            
            # Clear screen (platform-specific)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Render dashboard
            print(dashboard.render())
            
            # Add alerts section
            print("\n" + "="*80)
            print("ALERTS")
            print("="*80)
            
            if current_metrics['error_rate'] > 1.0:
                print("🚨 HIGH ERROR RATE: {:.2f}% (threshold: 1%)".format(
                    current_metrics['error_rate']))
                
            if current_metrics['cpu_usage'] > 80:
                print("⚠️  HIGH CPU USAGE: {:.1f}%".format(
                    current_metrics['cpu_usage']))
                
            if current_metrics['latency']['p99'] > 500:
                print("⚠️  HIGH LATENCY: P99 = {:.1f}ms".format(
                    current_metrics['latency']['p99']))
                
            # Sleep and update time
            time.sleep(1)
            time_factor += 0.01
            
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")

# Create a static dashboard example for non-interactive display
def create_static_dashboard_example():
    """Create a static example of the dashboard"""
    dashboard = create_service_dashboard()
    
    # Add some sample data
    sample_data = [
        {'request_rate': 950, 'error_rate': 0.3, 'active_connections': 240,
         'cpu_usage': 42, 'memory_usage': 58, 
         'latency': {'p50': 45, 'p95': 120, 'p99': 250}},
        {'request_rate': 980, 'error_rate': 0.4, 'active_connections': 245,
         'cpu_usage': 44, 'memory_usage': 59,
         'latency': {'p50': 48, 'p95': 125, 'p99': 260}},
        {'request_rate': 1020, 'error_rate': 0.5, 'active_connections': 255,
         'cpu_usage': 48, 'memory_usage': 60,
         'latency': {'p50': 52, 'p95': 140, 'p99': 280}},
        {'request_rate': 1050, 'error_rate': 1.2, 'active_connections': 265,
         'cpu_usage': 52, 'memory_usage': 62,
         'latency': {'p50': 58, 'p95': 160, 'p99': 350}},
        {'request_rate': 1100, 'error_rate': 1.8, 'active_connections': 275,
         'cpu_usage': 58, 'memory_usage': 64,
         'latency': {'p50': 65, 'p95': 180, 'p99': 420}},
    ]
    
    # Populate history
    for metrics in sample_data:
        dashboard.update(metrics)
        
    # Print static example
    print(dashboard.render())

# Run static example
print("=== Static Dashboard Example ===\n")
create_static_dashboard_example()

# Uncomment to run interactive dashboard
# test_dashboard()
```

</details>

## Challenge Problems

### 1. The Observability Pipeline 🚰

Design a complete observability pipeline that:
- Collects logs, metrics, and traces
- Handles 1M events/second
- Keeps costs under control
- Provides sub-second alerting

### 2. The Anomaly Detector 🔍

Build an anomaly detection system that:
- Learns normal patterns
- Detects unusual behavior
- Minimizes false positives
- Explains why something is anomalous

### 3. The Cost Optimizer 💰

Create a system that:
- Analyzes observability costs
- Identifies wasteful metrics/logs
- Suggests optimizations
- Maintains effectiveness

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Building structured logging systems
    - ✅ Implementing metrics collection
    - ✅ Creating distributed tracing
    - ✅ Designing smart alerting
    - ✅ Building monitoring dashboards

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 7: Human Interface](../axiom-7-human-interface/index.md) →
    
    **Back to**: [Observability Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Observability Tools](../../tools/observability-setup.md) | [Part II](../../part2-pillars/index.md)