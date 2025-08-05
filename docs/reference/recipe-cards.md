---
title: 'Recipe Cards: Step-by-Step Procedures'
description: Practical, actionable guides for implementing patterns and solving common
  distributed systems problems.
type: reference
difficulty: beginner
reading_time: 55 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Recipe Cards: Step-by-Step Procedures

---

## Pattern Implementation Recipes

### Recipe: Implementing Circuit Breaker

**Difficulty**: ⭐⭐⭐ | **Time**: 2-4 hours

**Steps**:

1. **Define Circuit Breaker States**
   ```python
   from enum import Enum

   class CircuitState(Enum):
       CLOSED = "CLOSED"      # Normal operation
       OPEN = "OPEN"          # Failing fast
       HALF_OPEN = "HALF_OPEN"  # Testing recovery
   ```

2. **Implement Core Logic**
   ```python
   class CircuitBreaker:
       def __init__(self, failure_threshold=5, timeout=60, success_threshold=3):
           self.failure_threshold = failure_threshold
           self.timeout = timeout
           self.success_threshold = success_threshold
           self.state = CircuitState.CLOSED
           self.failures = 0
           self.successes = 0
           self.last_failure_time = None
   ```

3. **Add Call Wrapper**
   ```python
   def call(self, func, *args, **kwargs):
       if self.state == CircuitState.OPEN:
           if self._should_attempt_reset():
               self.state = CircuitState.HALF_OPEN
           else:
               raise CircuitOpenError("Circuit breaker is OPEN")

       try:
           result = func(*args, **kwargs)
           self._on_success()
           return result
       except Exception as e:
           self._on_failure()
           raise
   ```

4. **Configure Monitoring**
   - Track state changes
   - Monitor failure rates
   - Alert on circuit opening

5. **Test Scenarios**
   - Normal operation
   - Failure threshold triggering
   - Recovery behavior
   - Half-open state testing

5. **Test Scenarios**: Normal operation, failure threshold, recovery, half-open state

**Related Laws**: Law 1 (Correlated Failure ⛓️), Law 3 (Emergent Chaos 🌪️)

**Case Studies**: [Netflix's Resilience Patterns](case-studies/netflix-chaos), [Circuit Breaker Pattern](pattern-library/circuit-breaker)

---

### Recipe: Implementing Retry with Exponential Backoff

**Difficulty**: ⭐⭐ | **Time**: 1-2 hours

1. **Calculate Backoff Delay**
   ```python
   import random
   import time

   def exponential_backoff(attempt, base_delay=1.0, max_delay=60.0, jitter=True):
       delay = min(base_delay * (2 ** attempt), max_delay)
       if jitter:
           delay = delay * (0.5 + random.random() * 0.5)
       return delay
   ```

2. **Implement Retry Decorator**
   ```python
   def retry_with_backoff(max_attempts=3, exceptions=(Exception,)):
       def decorator(func):
           def wrapper(*args, **kwargs):
               for attempt in range(max_attempts):
                   try:
                       return func(*args, **kwargs)
                   except exceptions as e:
                       if attempt == max_attempts - 1:
                           raise
                       delay = exponential_backoff(attempt)
                       time.sleep(delay)
           return wrapper
       return decorator
   ```

3. **Usage Example**
   ```python
   @retry_with_backoff(max_attempts=5, exceptions=(ConnectionError,))
   def call_external_api():
# API call that might fail
       return requests.get("https://api.example.com/data")
   ```

3. **Usage Example**
   ```python
   @retry_with_backoff(max_attempts=5, exceptions=(ConnectionError,))
   def call_external_api():
       return requests.get("https://api.example.com/data")
   ```

---

## 🐛 Debugging Procedures

### Recipe: Debugging Distributed System Failures

**Difficulty**: ⭐⭐⭐⭐ | **Time**: Variable

1. **Gather Information**: Start time? User impact? Affected services? Recent deployments?

2. **Check Service Health Dashboard**
   ```bash
# Health check script
   services=("user-service" "order-service" "payment-service")
   for service in "${services[@]}"; do
       echo "Checking $service..."
       curl -f "http://$service/health" || echo "$service is DOWN"
   done
   ```

3. **Analyze Request Flow**: Find failing trace, identify failure point, check timing/errors

4. **Examine Error Patterns**
   ```bash
# Query logs for error patterns
   kubectl logs -l app=user-service | grep ERROR | tail -100
   ```

5. **Check Resources**: CPU/Memory, Network, Database connections, Queue depths

6. **Validate Dependencies**: External APIs, Database, Cache, Network

7. **Form Hypothesis**: Based on evidence, consider scenarios, prioritize by likelihood

8. **Test & Verify**: Minimal changes, monitor impact, rollback if needed

**Common Causes**: Network issues, Resource exhaustion, Database locks, External failures, Config changes, Bad deployments, Traffic spikes, Cascades

**Consider**: Law 1 (Correlated Failure ⛓️) for cascade analysis, Law 2 (Asynchronous Reality ⏳) for timing issues

**Case Studies**: [Amazon DynamoDB Outage](case-studies/amazon-dynamo), [Facebook's Metastable Failures](case-studies/consistent-hashing)

---

### Recipe: Performance Investigation

**Difficulty**: ⭐⭐⭐ | **Time**: 2-8 hours

1. **Establish Baseline**
   ```bash
# Capture current performance metrics
   curl -s "http://metrics-server/api/v1/query?query=response_time_p95"
   ```

2. **Identify Bottlenecks**: CPU per service, DB queries, Network latency, GC metrics

3. **Load Test Current State**
   ```bash
# Simple load test
   hey -n 1000 -c 10 http://your-service/api/endpoint
   ```

4. **Profile Application**: CPU profiling, Memory allocation, Query plans, Algorithm complexity

5. **Test Optimizations**: Enable caching, Optimize queries, Tune pools, Add circuit breakers

6. **Measure Impact**: Compare metrics, Validate under load, Check regressions

---

## Monitoring Setup Recipes

### Recipe: Essential Observability Stack

**Difficulty**: ⭐⭐⭐ | **Time**: 4-8 hours

1. **Deploy Prometheus**
   ```yaml
# prometheus-config.yml
   global:
     scrape_interval: 15s
   scrape_configs:
     - job_name: 'application'
       static_configs:
         - targets: ['app:8080']
   ```

2. **Configure Application Metrics**
   ```python
   from prometheus_client import Counter, Histogram, start_http_server

   REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
   REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

   @REQUEST_LATENCY.time()
   def handle_request():
       REQUEST_COUNT.labels(method='GET', endpoint='/api').inc()
# Your application logic
   ```

3. **Create Dashboards**: Golden signals, Service metrics, Infrastructure

4. **Set Up Alerting Rules**
   ```yaml
# Alert on high error rate
   groups:
   - name: application.rules
     rules:
     - alert: HighErrorRate
       expr: rate(requests_total{status=~"5.."}[5m]) > 0.1
       for: 2m
   ```

4. **Set Up Alerting Rules**
   ```yaml
   groups:
   - name: application.rules
     rules:
     - alert: HighErrorRate
       expr: rate(requests_total{status=~"5.."}[5m]) > 0.1
       for: 2m
   ```

**Related Laws**: Law 5 (Distributed Knowledge 🧠) for observability, Law 6 (Cognitive Load 🤯) for operator experience

**Learn More**: [Observability Best Practices](pattern-library/observability), [Monitoring Patterns](pattern-library/observability)

---

## Performance Tuning Recipes

### Recipe: Database Performance Optimization

**Difficulty**: ⭐⭐⭐ | **Time**: 2-6 hours

1. **Analyze Query Performance**
   ```sql
   -- Find slow queries
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

2. **Add Strategic Indexes**
   ```sql
   -- Create composite index for common query pattern
   CREATE INDEX idx_orders_customer_date
   ON orders(customer_id, created_at);
   ```

3. **Optimize Connection Pooling**
   ```python
# Configure connection pool
   DATABASE_URL = "postgresql://user:pass@host:5432/db?max_connections=20&min_connections=5"
   ```

4. **Implement Query Caching**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_user_profile(user_id):
       return db.query("SELECT * FROM users WHERE id = %s", user_id)
   ```

5. **Monitor Results**: Query plans, Connection usage, Cache hit rates

---

### Recipe: API Performance Optimization

**Difficulty**: ⭐⭐ | **Time**: 2-4 hours

1. **Enable Response Compression**
   ```python
   from flask_compress import Compress

   app = Flask(__name__)
   Compress(app)  # Enables gzip compression
   ```

2. **Implement Response Caching**
   ```python
   from flask_caching import Cache

   cache = Cache(app, config={'CACHE_TYPE': 'redis'})

   @app.route('/api/data')
   @cache.cached(timeout=300)
   def get_data():
       return jsonify(expensive_computation())
   ```

3. **Optimize Serialization**
   ```python
# Use faster JSON serialization
   import orjson

   def fast_json_response(data):
       return Response(orjson.dumps(data), mimetype='application/json')
   ```

4. **Add Request Batching**
   ```python
   @app.route('/api/batch', methods=['POST'])
   def batch_endpoint():
       requests = request.json['requests']
       responses = []
       for req in requests:
           responses.append(process_single_request(req))
       return jsonify(responses)
   ```

---

## 🔐 Security Implementation Recipes

### Recipe: API Security Hardening

**Difficulty**: ⭐⭐⭐ | **Time**: 3-6 hours

1. **Implement Rate Limiting**
   ```python
   from flask_limiter import Limiter

   limiter = Limiter(
       app,
       key_func=lambda: request.remote_addr,
       default_limits=["100 per hour"]
   )

   @app.route('/api/sensitive')
   @limiter.limit("10 per minute")
   def sensitive_endpoint():
       return jsonify({"data": "sensitive"})
   ```

2. **Add Input Validation**
   ```python
   from marshmallow import Schema, fields, validate

   class UserSchema(Schema):
       email = fields.Email(required=True)
       age = fields.Integer(validate=validate.Range(min=18, max=120))
   ```

3. **Implement JWT Authentication**
   ```python
   import jwt
   from functools import wraps

   def token_required(f):
       @wraps(f)
       def decorated(*args, **kwargs):
           token = request.headers.get('Authorization')
           if not token:
               return jsonify({'message': 'Token missing'}), 401

           try:
               data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
           except:
               return jsonify({'message': 'Token invalid'}), 401

           return f(*args, **kwargs)
       return decorated
   ```

---

## Capacity Planning Recipes

### Recipe: Determining System Capacity

**Difficulty**: ⭐⭐⭐ | **Time**: 4-8 hours

1. **Gather Current Metrics**
   ```bash
# Extract usage patterns
   curl "http://prometheus:9090/api/v1/query_range?query=rate(requests_total[5m])&start=$(date -d '7 days ago' +%s)&end=$(date +%s)&step=3600"
   ```

2. **Identify Patterns**: Daily peaks, Weekly patterns, Seasonal variations, Growth trends

3. **Calculate Resource Requirements**
   ```python
# Simple capacity calculation
   current_rps = 1000  # requests per second
   growth_factor = 2.0  # expected growth
   safety_margin = 1.5  # buffer for spikes

   required_capacity = current_rps * growth_factor * safety_margin
   print(f"Required capacity: {required_capacity} RPS")
   ```

4. **Plan Scaling**: Horizontal vs vertical, Auto-scaling thresholds, Regional distribution

5. **Test Plan**: Load test at target, Validate auto-scaling, Measure response times

**Related Laws**: Law 4 (Multidimensional Optimization ⚖️) for trade-offs, Law 7 (Economic Reality 💰) for cost planning

**Tools**: [Capacity Planning Calculator](../architects-handbook/tools/capacity-calculator.md), [Little's Law Calculator](../architects-handbook/tools/latency-calculator.md)

---

### Recipe: Distributed Tracing Implementation

**Difficulty**: ⭐⭐⭐ | **Time**: 4-6 hours

1. **Install Tracing Infrastructure**
   ```bash
   # Deploy Jaeger using Helm
   helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
   helm install jaeger jaegertracing/jaeger \
     --set cassandra.config.max_heap_size=1024M \
     --set cassandra.config.heap_new_size=256M
   ```

2. **Instrument Applications**
   ```python
   from opentelemetry import trace
   from opentelemetry.exporter.jaeger import JaegerExporter
   
   tracer = trace.get_tracer(__name__)
   
   @app.route('/api/users/<user_id>')
   def get_user(user_id):
       with tracer.start_as_current_span("get_user") as span:
           span.set_attribute("user.id", user_id)
           # Your code here
   ```

3. **Propagate Context**
   ```python
   # Automatic context propagation
   from opentelemetry.propagate import inject
   
   headers = {}
   inject(headers)  # Injects trace context
   response = requests.get(downstream_url, headers=headers)
   ```

4. **Set Sampling Strategy**
   ```yaml
   sampling:
     default_strategy:
       type: probabilistic
       param: 0.1  # Sample 10% of traces
     per_operation_strategies:
       - operation: "critical_payment_flow"
         type: probabilistic
         param: 1.0  # Sample 100% of payment traces
   ```

5. **Monitor and Alert**: Trace duration P99, Error traces, Missing spans

**Related Patterns**: [Observability](../pattern-library/resilience/health-check.md), [Service Mesh](../pattern-library/communication/service-mesh.md)

---

### Recipe: Zero-Downtime Database Migration

**Difficulty**: ⭐⭐⭐⭐ | **Time**: 2-4 days

1. **Dual Write Pattern**
   ```python
   def save_user(user_data):
       # Phase 1: Write to both databases
       old_db.save(user_data)
       new_db.save(user_data)
       
       # Phase 2: Read from old, verify against new
       # Phase 3: Read from new, old as fallback
       # Phase 4: Remove old database writes
   ```

2. **Add Background Sync**
   ```python
   class DataMigrator:
       def sync_batch(self, offset, limit):
           old_records = old_db.query(
               "SELECT * FROM users LIMIT %s OFFSET %s",
               limit, offset
           )
           
           for record in old_records:
               if not new_db.exists(record.id):
                   new_db.insert(record)
               elif record.updated > new_db.get(record.id).updated:
                   new_db.update(record)
   ```

3. **Implement Verification**
   ```python
   def verify_migration():
       sample_size = 1000
       sample_ids = old_db.query(
           "SELECT id FROM users ORDER BY RANDOM() LIMIT %s",
           sample_size
       )
       
       mismatches = []
       for id in sample_ids:
           old_record = old_db.get(id)
           new_record = new_db.get(id)
           if not records_match(old_record, new_record):
               mismatches.append(id)
       
       accuracy = (sample_size - len(mismatches)) / sample_size
       return accuracy > 0.999  # 99.9% accuracy required
   ```

4. **Traffic Shifting**
   ```nginx
   # Gradual traffic shift using nginx
   upstream old_db_service { server old-db:5432 weight=90; }
   upstream new_db_service { server new-db:5432 weight=10; }
   ```

5. **Rollback Plan**: Keep old database running, Maintain dual writes, Quick config switch

**Related Laws**: Law 2 (Asynchronous Reality ⏱️) for sync delays, Law 5 (Distributed Knowledge 🧠) for consistency

---

### Recipe: Circuit Breaker Pattern

**Difficulty**: ⭐⭐ | **Time**: 2-3 hours

1. **Implement Basic Circuit Breaker**
   ```python
   class CircuitBreaker:
       def __init__(self, failure_threshold=5, timeout=60):
           self.failure_threshold = failure_threshold
           self.timeout = timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
           
       def call(self, func, *args, **kwargs):
           if self.state == 'OPEN':
               if time.time() - self.last_failure_time > self.timeout:
                   self.state = 'HALF_OPEN'
               else:
                   raise CircuitOpenError()
           
           try:
               result = func(*args, **kwargs)
               if self.state == 'HALF_OPEN':
                   self.state = 'CLOSED'
                   self.failure_count = 0
               return result
           except Exception as e:
               self.record_failure()
               raise e
   ```

2. **Add Hystrix-style Fallbacks**
   ```python
   @circuit_breaker.protect(fallback=get_cached_data)
   def get_user_data(user_id):
       return external_service.get_user(user_id)
   
   def get_cached_data(user_id):
       return cache.get(f"user:{user_id}", default={"status": "degraded"})
   ```

3. **Configure Thresholds**
   ```yaml
   circuit_breaker:
     payment_service:
       error_threshold: 50%
       request_volume_threshold: 20
       sleep_window: 5000ms
       timeout: 1000ms
   ```

4. **Add Metrics**
   ```python
   circuit_breaker_state = Gauge(
       'circuit_breaker_state',
       'Circuit breaker state (0=closed, 1=open, 2=half-open)',
       ['service']
   )
   ```

5. **Test the Breaker**: Inject failures, Verify opens at threshold, Confirm recovery behavior

**Related Patterns**: [Bulkhead](../pattern-library/resilience/bulkhead.md), [Retry with Backoff](../pattern-library/resilience/retry-backoff.md)

---

## Quick Recipe Index

### By Time Required
- **< 1 hour**: Health checks, Basic caching, Logging setup
- **1-4 hours**: Circuit breakers, Rate limiting, API optimization
- **4-8 hours**: Service mesh, Distributed tracing, Load testing
- **Days**: Database migration, Multi-region setup, Security hardening

### By Difficulty
- **⭐ Beginner**: Health checks, Basic monitoring, Caching
- **⭐⭐ Intermediate**: Circuit breakers, Rate limiting, Tracing
- **⭐⭐⭐ Advanced**: Service mesh, Capacity planning, Chaos testing
- **⭐⭐⭐⭐ Expert**: Database migration, Multi-region, Custom protocols

### By Problem Domain
- **Reliability**: Circuit breakers, Health checks, Bulkheads
- **Performance**: Caching, CDN setup, Database optimization
- **Scalability**: Load balancing, Sharding, Capacity planning
- **Operations**: Monitoring, Tracing, Incident response

---

## Creating Your Own Recipes

### Recipe Template
```markdown
### Recipe: [Name]

**Difficulty**: ⭐ to ⭐⭐⭐⭐ | **Time**: X hours/days

1. **Step Name**
   ```language
   # Code or commands
   ```
   Explanation of what this does

2. **Next Step**
   Continue pattern...

3. **Verification**
   How to know it worked

4. **Monitoring**
   What to watch

5. **Rollback**
   How to undo if needed

**Related Laws**: Which fundamental laws apply
**Related Patterns**: Links to detailed patterns
**Tools**: Relevant calculators or tools
```

### Best Practices
1. **Start simple**: Show the minimal working version first
2. **Include verification**: How to test each step
3. **Provide rollback**: Always include undo instructions
4. **Link concepts**: Connect to laws and patterns
5. **Real examples**: Use actual commands and code

---

## Next Steps

1. **Pick a recipe** matching your current challenge
2. **Follow step-by-step** in a test environment first
3. **Adapt to your needs** - recipes are starting points
4. **Share your recipes** - contribute back improvements

For deeper understanding:
- [Patterns](../pattern-library/architects-handbook/case-studies/index.md) - Real-world implementations
- [Tools](../architects-handbook/tools/index.md) - Interactive calculators
- [Cheat Sheets](../reference/cheat-sheets.md) - Quick reference

---

*Practical recipes for common distributed systems challenges. Each recipe tested in production environments.*

