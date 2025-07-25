---
title: "Axiom 6 Exercises: Master the Art of Observability"
description: "Hands-on labs to build production-grade observability systems. Learn to implement distributed tracing, structured logging, and intelligent alerting while managing costs and avoiding data overload."
type: axiom
difficulty: advanced
reading_time: 45 min
prerequisites: [axiom1-latency, axiom2-capacity, axiom3-failure, axiom4-concurrency, axiom5-coordination, axiom6-observability]
status: complete
completion_percentage: 100
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 6](index.md) → **Observability Exercises**

# Observability Exercises

**From blind debugging to x-ray vision: build observability that illuminates without overwhelming**

---

## 🧪 Hands-On Labs

### Lab 1: Production-Grade Structured Logging

**Build a logging system that developers actually want to use**

#### Exercise 1.1: Implement Structured Logger

```python
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextvars import ContextVar
import uuid

# Context for correlation IDs
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredLogger:
    """Production-ready structured logger"""
    
    def __init__(self, service_name: str, environment: str):
        self.service_name = service_name
        self.environment = environment
        self.default_fields = {
            'service': service_name,
            'env': environment,
            'version': self.get_service_version(),
            'hostname': self.get_hostname()
        }
        
    def log(self, level: str, message: str, **fields):
        """Core logging method"""
        # TODO: Implement structured logging with:
        # 1. Automatic timestamp in ISO format
        # 2. Correlation ID from context
        # 3. User ID from context
        # 4. Automatic error serialization
        # 5. Performance metrics (execution time)
        # 6. Sampling for high-volume logs
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'correlation_id': correlation_id_var.get(),
            'user_id': user_id_var.get(),
            **self.default_fields,
            **fields
        }
        
        # Your implementation here
        pass
        
    def with_context(self, **context_fields):
        """Create child logger with additional context"""
        # TODO: Implement context propagation
        pass
        
    def error(self, message: str, error: Optional[Exception] = None, **fields):
        """Log error with automatic exception handling"""
        # TODO: Extract stack trace, error type, etc.
        pass
        
    def performance(self, operation: str):
        """Context manager for performance logging"""
        # TODO: Implement timing decorator/context manager
        pass

# Exercise: Complete the logger implementation
logger = StructuredLogger("payment-service", "production")

# Test scenarios
def test_structured_logging():
    # Scenario 1: Basic logging
    logger.info("Processing payment", 
               amount=99.99, 
               currency="USD",
               payment_method="credit_card")
    
    # Scenario 2: Error logging with context
    try:
        process_payment()
    except Exception as e:
        logger.error("Payment failed", 
                    error=e,
                    amount=99.99,
                    retry_count=3)
    
    # Scenario 3: Performance logging
    with logger.performance("database_query"):
        # Simulate slow query
        time.sleep(0.1)
```

#### Exercise 1.2: Log Aggregation Pipeline

```python
class LogAggregator:
    """Aggregate logs for analysis"""
    
    def __init__(self):
        self.buffer = []
        self.aggregation_rules = {}
        
    def add_aggregation_rule(self, name: str, 
                           pattern: Dict[str, Any],
                           window_seconds: int,
                           threshold: int):
        """Define when to alert on log patterns"""
        # TODO: Implement pattern matching rules
        # Example: Alert if >100 errors in 60 seconds
        pass
        
    def process_log(self, log_entry: Dict[str, Any]):
        """Process incoming log entry"""
        # TODO: 
        # 1. Buffer logs for time window
        # 2. Check against aggregation rules
        # 3. Trigger alerts if thresholds exceeded
        # 4. Calculate statistics
        pass
        
    def get_statistics(self, time_window_minutes: int = 5):
        """Get log statistics for monitoring"""
        # TODO: Return stats like:
        # - Log volume by level
        # - Error rate
        # - Top error messages
        # - Performance percentiles
        pass

# Exercise: Build log aggregation system
aggregator = LogAggregator()

# Add rules for common issues
aggregator.add_aggregation_rule(
    "high_error_rate",
    pattern={"level": "ERROR"},
    window_seconds=60,
    threshold=100
)

aggregator.add_aggregation_rule(
    "payment_failures",
    pattern={"level": "ERROR", "message": "Payment failed"},
    window_seconds=300,
    threshold=50
)
```

---

### Lab 2: Distributed Tracing Implementation

**Build a tracing system that follows requests across services**

#### Exercise 2.1: Basic Tracer

```python
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from contextlib import contextmanager
import threading

@dataclass
class Span:
    """Represents a unit of work in a trace"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

class Tracer:
    """Distributed tracer implementation"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.active_spans = {}  # thread_id -> span
        self.completed_spans = []
        self.sampling_rate = 1.0  # 100% sampling initially
        
    def start_span(self, operation_name: str, 
                   parent_span: Optional[Span] = None) -> Span:
        """Start a new span"""
        # TODO: Implement span creation with:
        # 1. Unique trace_id (or inherit from parent)
        # 2. Unique span_id
        # 3. Parent relationship tracking
        # 4. Automatic service name tagging
        pass
        
    def finish_span(self, span: Span):
        """Complete a span"""
        # TODO: 
        # 1. Set end time
        # 2. Calculate duration
        # 3. Send to backend (or buffer)
        # 4. Remove from active spans
        pass
        
    @contextmanager
    def trace(self, operation_name: str, **tags):
        """Context manager for tracing"""
        # TODO: Implement automatic span lifecycle
        span = self.start_span(operation_name)
        try:
            yield span
        except Exception as e:
            span.tags['error'] = True
            span.logs.append({
                'timestamp': time.time(),
                'message': str(e),
                'stack': traceback.format_exc()
            })
            raise
        finally:
            self.finish_span(span)
            
    def inject_headers(self, span: Span) -> Dict[str, str]:
        """Inject trace context into HTTP headers"""
        # TODO: Implement W3C Trace Context or similar
        return {
            'X-Trace-Id': span.trace_id,
            'X-Parent-Span-Id': span.span_id,
            'X-Sampling-Priority': '1' if self.should_sample() else '0'
        }
        
    def extract_headers(self, headers: Dict[str, str]) -> Optional[Span]:
        """Extract trace context from HTTP headers"""
        # TODO: Parse incoming trace context
        pass

# Exercise: Complete tracer and test with mock services
class MockService:
    def __init__(self, name: str, tracer: Tracer):
        self.name = name
        self.tracer = tracer
        
    async def handle_request(self, headers: Dict[str, str]):
        # Extract parent context
        parent_span = self.tracer.extract_headers(headers)
        
        with self.tracer.trace(f"{self.name}.handle_request") as span:
            # Simulate work
            await self.database_query()
            await self.call_downstream_service()
            
    async def database_query(self):
        with self.tracer.trace("database.query", 
                              db_type="postgres",
                              query="SELECT * FROM users"):
            # Simulate query time
            await asyncio.sleep(random.uniform(0.01, 0.1))
```

#### Exercise 2.2: Trace Analysis

```python
class TraceAnalyzer:
    """Analyze traces to find performance issues"""
    
    def __init__(self):
        self.traces = {}  # trace_id -> List[Span]
        
    def add_span(self, span: Span):
        """Add span to trace"""
        if span.trace_id not in self.traces:
            self.traces[span.trace_id] = []
        self.traces[span.trace_id].append(span)
        
    def analyze_trace(self, trace_id: str) -> Dict[str, Any]:
        """Analyze a single trace"""
        # TODO: Calculate:
        # 1. Total duration
        # 2. Critical path (longest chain)
        # 3. Service breakdown (time per service)
        # 4. Operation breakdown (time per operation type)
        # 5. Error analysis
        pass
        
    def find_bottlenecks(self, percentile: float = 0.95) -> List[Dict]:
        """Find slowest operations across all traces"""
        # TODO: Identify operations that:
        # 1. Take longest time (p95)
        # 2. Are called most frequently
        # 3. Have highest error rate
        # 4. Have most variability
        pass
        
    def generate_service_map(self) -> Dict[str, List[str]]:
        """Generate service dependency map from traces"""
        # TODO: Build graph of service dependencies
        pass

# Exercise: Analyze trace data
analyzer = TraceAnalyzer()

# Load sample trace data
for span in sample_spans:
    analyzer.add_span(span)
    
# Find performance issues
bottlenecks = analyzer.find_bottlenecks()
print(f"Top bottlenecks: {bottlenecks}")

# Generate service map
service_map = analyzer.generate_service_map()
print(f"Service dependencies: {service_map}")
```

---

### Lab 3: Metrics Collection and Analysis

**Build a metrics system that scales**

#### Exercise 3.1: Time Series Database

```python
from collections import defaultdict
import bisect
import statistics

class TimeSeriesDB:
    """Simple time series database for metrics"""
    
    def __init__(self):
        # metric_name -> [(timestamp, value)]
        self.data = defaultdict(list)
        self.retention_seconds = 3600  # 1 hour
        
    def write(self, metric: str, value: float, 
              timestamp: Optional[float] = None,
              tags: Optional[Dict[str, str]] = None):
        """Write a data point"""
        # TODO: Implement:
        # 1. Tag handling (convert to metric name)
        # 2. Sorted insertion for efficiency
        # 3. Automatic old data cleanup
        # 4. Downsampling for older data
        pass
        
    def query(self, metric: str, 
              start_time: float,
              end_time: float,
              aggregation: str = 'avg') -> List[Tuple[float, float]]:
        """Query time series data"""
        # TODO: Implement:
        # 1. Binary search for time range
        # 2. Aggregation functions (avg, sum, max, min, p95)
        # 3. Downsampling for large ranges
        # 4. Interpolation for missing data
        pass
        
    def downsample(self, data: List[Tuple[float, float]], 
                   target_points: int = 1000) -> List[Tuple[float, float]]:
        """Downsample data for visualization"""
        # TODO: Implement LTTB algorithm or similar
        pass

# Exercise: Build a complete metrics pipeline
class MetricsCollector:
    def __init__(self, db: TimeSeriesDB):
        self.db = db
        self.counters = defaultdict(int)
        self.gauges = {}
        self.histograms = defaultdict(list)
        
    def increment_counter(self, name: str, value: int = 1, **tags):
        """Increment a counter metric"""
        # TODO: Handle counter metrics
        pass
        
    def set_gauge(self, name: str, value: float, **tags):
        """Set a gauge metric"""
        # TODO: Handle gauge metrics
        pass
        
    def record_histogram(self, name: str, value: float, **tags):
        """Record a histogram value"""
        # TODO: Calculate percentiles efficiently
        pass
        
    def flush(self):
        """Flush metrics to database"""
        # TODO: Write all metrics to DB
        # Reset counters, keep gauges, rotate histograms
        pass
```

#### Exercise 3.2: Alert Rule Engine

```python
class AlertRule:
    """Define alert conditions"""
    
    def __init__(self, name: str, metric: str, 
                 condition: str, threshold: float,
                 duration_seconds: int = 300):
        self.name = name
        self.metric = metric
        self.condition = condition  # '>', '<', '=='
        self.threshold = threshold
        self.duration = duration_seconds
        self.firing = False
        self.fired_at = None
        
class AlertEngine:
    """Evaluate alert rules against metrics"""
    
    def __init__(self, db: TimeSeriesDB):
        self.db = db
        self.rules = []
        self.alert_history = []
        
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
        
    def evaluate_rules(self):
        """Check all rules against current metrics"""
        # TODO: Implement:
        # 1. Query metrics for each rule
        # 2. Check if condition met for duration
        # 3. Handle state transitions (pending -> firing -> resolved)
        # 4. Deduplication and flap detection
        # 5. Alert notification routing
        pass
        
    def predict_alerts(self, hours_ahead: int = 1) -> List[Dict]:
        """Predict future alerts based on trends"""
        # TODO: Use linear regression or similar
        # to predict when thresholds will be crossed
        pass

# Exercise: Create intelligent alerting
engine = AlertEngine(db)

# Define SLO-based alerts
engine.add_rule(AlertRule(
    name="High Error Rate",
    metric="http_requests_errors_per_second",
    condition=">",
    threshold=10,
    duration_seconds=300
))

engine.add_rule(AlertRule(
    name="Latency SLO Violation",
    metric="http_request_duration_p99",
    condition=">",
    threshold=500,  # 500ms
    duration_seconds=600
))
```

---

### Lab 4: Observability Cost Optimization

**Balance visibility with budget constraints**

#### Exercise 4.1: Adaptive Sampling

```python
class AdaptiveSampler:
    """Intelligent trace sampling to reduce costs"""
    
    def __init__(self, target_rate: float = 100.0):  # traces per second
        self.target_rate = target_rate
        self.current_rate = 0
        self.sampling_decisions = {}
        self.priority_rules = []
        
    def should_sample(self, trace_attributes: Dict[str, Any]) -> bool:
        """Decide whether to sample this trace"""
        # TODO: Implement adaptive sampling:
        # 1. Always sample errors
        # 2. Sample slow requests (>p95)
        # 3. Sample new endpoints
        # 4. Sample based on business importance
        # 5. Adjust rate to meet target
        
        # Priority sampling
        for rule in self.priority_rules:
            if rule.matches(trace_attributes):
                return True
                
        # Rate-based sampling
        if self.current_rate >= self.target_rate:
            return False
            
        # Probabilistic sampling for the rest
        sample_probability = self.calculate_probability(trace_attributes)
        return random.random() < sample_probability
        
    def add_priority_rule(self, name: str, 
                         condition: Callable[[Dict], bool],
                         reason: str):
        """Add rule for priority sampling"""
        # TODO: Implement priority rules
        pass
        
    def calculate_cost_savings(self) -> Dict[str, float]:
        """Estimate cost savings from sampling"""
        # TODO: Calculate:
        # 1. Data ingestion savings
        # 2. Storage savings
        # 3. Query cost savings
        # 4. Value of traces kept vs discarded
        pass

# Exercise: Design cost-effective sampling
sampler = AdaptiveSampler(target_rate=1000)  # 1000 traces/sec budget

# Priority rules
sampler.add_priority_rule(
    "errors",
    lambda attrs: attrs.get('error', False),
    "Always sample errors for debugging"
)

sampler.add_priority_rule(
    "slow_requests", 
    lambda attrs: attrs.get('duration_ms', 0) > 1000,
    "Sample slow requests for performance analysis"
)

sampler.add_priority_rule(
    "vip_customers",
    lambda attrs: attrs.get('customer_tier') == 'vip',
    "Sample VIP customer requests"
)
```

#### Exercise 4.2: Data Retention Optimizer

```python
class RetentionOptimizer:
    """Optimize data retention for cost and compliance"""
    
    def __init__(self, storage_costs: Dict[str, float]):
        self.storage_costs = storage_costs  # $/GB/month by tier
        self.data_categories = {}
        self.compliance_requirements = {}
        
    def define_data_category(self, name: str,
                           daily_volume_gb: float,
                           query_frequency: str,  # 'high', 'medium', 'low'
                           business_value: str):  # 'critical', 'important', 'nice'
        """Define a category of observability data"""
        # TODO: Track data categories for optimization
        pass
        
    def optimize_retention(self) -> Dict[str, Dict]:
        """Recommend optimal retention per category"""
        # TODO: For each category, recommend:
        # 1. Hot storage duration (fast, expensive)
        # 2. Warm storage duration (slower, cheaper)
        # 3. Cold storage duration (slow, cheap)
        # 4. Aggregation strategy (raw vs rollups)
        # 5. Deletion timeline
        #
        # Consider:
        # - Query patterns
        # - Compliance requirements
        # - Storage costs
        # - Business value
        pass
        
    def calculate_monthly_cost(self, retention_policy: Dict) -> float:
        """Calculate cost of retention policy"""
        # TODO: Sum up storage costs across tiers
        pass

# Exercise: Design retention strategy
optimizer = RetentionOptimizer({
    'hot': 0.10,   # $/GB/month
    'warm': 0.03,  # $/GB/month  
    'cold': 0.01   # $/GB/month
})

# Define data categories
optimizer.define_data_category(
    "application_logs",
    daily_volume_gb=100,
    query_frequency='high',
    business_value='important'
)

optimizer.define_data_category(
    "trace_data",
    daily_volume_gb=500,
    query_frequency='medium',
    business_value='important'
)

optimizer.define_data_category(
    "metrics",
    daily_volume_gb=50,
    query_frequency='high',
    business_value='critical'
)

# Get recommendations
recommendations = optimizer.optimize_retention()
print(f"Optimized retention: {recommendations}")
print(f"Monthly cost: ${optimizer.calculate_monthly_cost(recommendations):,.2f}")
```

---

## 💪 Challenge Problems

### Challenge 1: Distributed System Debugger

**Build a tool that can debug issues across 100 microservices**

```python
class DistributedDebugger:
    """Debug issues in distributed systems"""
    
    def __init__(self):
        self.services = {}
        self.traces = {}
        self.logs = defaultdict(list)
        self.metrics = {}
        
    def investigate_issue(self, error_trace_id: str) -> Dict:
        """Automatically investigate an error"""
        # TODO: Implement investigation that:
        # 1. Collects the full trace
        # 2. Gathers logs from all involved services
        # 3. Correlates with metrics anomalies
        # 4. Identifies root cause service
        # 5. Suggests fix based on patterns
        #
        # Return investigation report with:
        # - Timeline of events
        # - Service interaction diagram
        # - Error propagation path
        # - Similar past incidents
        # - Recommended actions
        pass
        
    def find_cascade_failures(self, time_window: Tuple[float, float]) -> List[Dict]:
        """Identify cascade failure patterns"""
        # TODO: Analyze how failures propagate
        pass
        
    def generate_debug_notebook(self, incident_id: str):
        """Generate Jupyter notebook for incident"""
        # TODO: Create interactive debugging session
        pass

# Challenge: Debug a complex distributed system failure
# involving payment service, inventory, shipping, and notifications
```

### Challenge 2: Observability Without Observability

```python
"""
Scenario: You have a legacy system with:
- No structured logging
- No distributed tracing  
- Basic system metrics only
- Cannot modify application code
- Budget: $1000/month

Design an observability solution that:
1. Provides visibility into the system
2. Can detect and diagnose issues
3. Works within budget constraints
4. Requires no code changes

# Your solution here
"""

class LegacyObservability:
    # Design your solution
    pass
```

### Challenge 3: The Observability Paradox

```python
"""
Your observability system is so successful that it now:
- Generates 10TB of data per day
- Costs $500K/month
- Takes 30 minutes to query
- Has become critical infrastructure
- Is harder to debug than the actual system

Design a meta-observability system that:
1. Observes the observers
2. Optimizes itself automatically
3. Provides value/cost metrics
4. Can't become another problem
"""

class MetaObservability:
    # Your implementation
    pass
```

---

## 🔬 Research Projects

### Project 1: ML-Powered Anomaly Detection

```python
class AnomalyDetector:
    """Detect anomalies without manual thresholds"""
    
    def __init__(self):
        self.models = {}  # metric -> model
        self.training_data = defaultdict(list)
        
    def train(self, metric_name: str, 
              historical_data: List[Tuple[float, float]]):
        """Train anomaly detection model"""
        # TODO: Implement using:
        # 1. Seasonal decomposition
        # 2. LSTM for time series
        # 3. Isolation forests
        # 4. Auto-encoders
        #
        # Handle:
        # - Seasonal patterns
        # - Trend changes
        # - Known events (deployments)
        pass
        
    def detect_anomalies(self, metric_name: str,
                        recent_data: List[Tuple[float, float]]) -> List[Dict]:
        """Detect anomalies in recent data"""
        # TODO: Return anomalies with:
        # - Confidence score
        # - Likely cause
        # - Business impact
        # - Similar past anomalies
        pass

# Research: Compare different algorithms on production data
```

### Project 2: Distributed Tracing Compression

```python
"""
Research project: Traces are too large!

Develop compression algorithm that:
1. Reduces trace size by 90%+
2. Preserves critical path
3. Maintains error details
4. Allows similarity search
5. Enables aggregation

Bonus: Make it streamable (compress as traces arrive)
"""

class TraceCompressor:
    # Your research implementation
    pass
```

### Project 3: Cost-Aware Observability

```python
class CostAwareObservability:
    """Observability that optimizes for value/cost"""
    
    def __init__(self, monthly_budget: float):
        self.budget = monthly_budget
        self.value_model = {}  # How much is each insight worth?
        
    def calculate_insight_value(self, insight_type: str) -> float:
        """Calculate $ value of an insight"""
        # TODO: Model based on:
        # - Incidents prevented
        # - MTTR reduction
        # - Performance improvements
        # - Customer satisfaction
        pass
        
    def optimize_observability_mix(self) -> Dict:
        """Optimize what to observe given budget"""
        # TODO: Solve optimization problem:
        # Maximize: insight_value
        # Subject to: cost <= budget
        #
        # Consider:
        # - Sampling rates
        # - Retention periods
        # - Aggregation levels
        # - Which services to monitor
        pass

# Research: Quantify observability ROI
```

---

## 📑 Quick Reference Cards

### Observability Decision Tree

```python
def choose_observability_strategy(system_attributes: Dict) -> Dict:
    """Quick decision tree for observability"""
    
    if system_attributes['requests_per_day'] < 1_000_000:
        # Small scale
        return {
            'logging': 'application_logs_only',
            'tracing': 'sample_errors_only',
            'metrics': 'basic_RED_metrics',
            'cost': '$100-500/month'
        }
    elif system_attributes['requests_per_day'] < 100_000_000:
        # Medium scale
        return {
            'logging': 'structured_with_sampling',
            'tracing': '1%_sampling',
            'metrics': 'full_golden_signals',
            'cost': '$5K-20K/month'
        }
    else:
        # Large scale
        return {
            'logging': 'edge_sampling_with_aggregation',
            'tracing': 'adaptive_sampling',
            'metrics': 'hierarchical_aggregation',
            'cost': '$50K+/month'
        }
```

### Cost Optimization Checklist

```python
observability_cost_checklist = [
    "Implement sampling (can reduce costs 10-100x)",
    "Use different retention for different data types",
    "Pre-aggregate metrics at collection time",
    "Drop debug logs in production",
    "Use columnar storage for logs",
    "Implement trace sampling by importance",
    "Archive to cold storage after N days",
    "Use approximate algorithms for percentiles",
    "Deduplicate similar log messages",
    "Compress data before storage"
]
```

---

## 🏆 Skills Assessment

Rate your understanding (1-5):
- [ ] Can implement structured logging
- [ ] Understand distributed tracing concepts
- [ ] Can build basic metrics collection
- [ ] Know how to sample effectively
- [ ] Can debug distributed systems
- [ ] Understand observability costs
- [ ] Can implement SLO-based alerts
- [ ] Can build anomaly detection

**Score: ___/40** (32+ = Expert, 24-32 = Proficient, 16-24 = Intermediate, <16 = Keep practicing!)

---

## 🎯 Final Challenge: Production Observability System

```python
"""
The Ultimate Test: Build Complete Observability for a Bank

Requirements:
- 1M transactions/day
- 99.99% availability SLO
- <500ms transaction SLO
- Regulatory compliance (7 year retention)
- $50K/month budget
- 50 microservices
- 5 geographic regions

Your system must:
1. Detect fraud in real-time
2. Debug any transaction
3. Prove compliance
4. Alert before SLO breach
5. Stay within budget

Extra credit:
- Predict failures before they happen
- Auto-remediate common issues
- Generate executive dashboards
"""

class BankingObservability:
    # Your implementation here
    pass
```

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 7: Human Interface](/part1-axioms/archive-old-8-axiom-structure/axiom7-human/)

**Related**: [Service Mesh](/patterns/service-mesh) • [API Gateway](/patterns/api-gateway) • [Circuit Breaker](/patterns/circuit-breaker) • [Bulkhead](/patterns/bulkhead)
