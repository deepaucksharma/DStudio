---
title: "Recipe Cards: Step-by-Step Procedures"
description: Practical, actionable guides for implementing patterns and solving common distributed systems problems.
type: reference
difficulty: beginner
reading_time: 55 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Reference](index.md) → **Recipe Cards: Step-by-Step Procedures**

# Recipe Cards: Step-by-Step Procedures

---

## 🔧 Pattern Implementation Recipes

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

**Case Studies**: [Netflix's Resilience Patterns](../case-studies/netflix-chaos.md), [Circuit Breaker Pattern](../patterns/circuit-breaker.md)

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

**Case Studies**: [Amazon DynamoDB Outage](../case-studies/amazon-dynamo.md), [Facebook's Metastable Failures](../case-studies/consistent-hashing.md)

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

## 📊 Monitoring Setup Recipes

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

**Learn More**: [Observability Best Practices](../patterns/observability.md), [Monitoring Patterns](../patterns/observability.md)

---

## ⚡ Performance Tuning Recipes

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

## 📈 Capacity Planning Recipes

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

**Tools**: [Capacity Planning Calculator](../tools/capacity-calculator.md), [Little's Law Calculator](../tools/latency-calculator.md)


---

