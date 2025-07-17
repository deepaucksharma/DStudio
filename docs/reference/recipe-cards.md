# Recipe Cards for Common Distributed Systems Scenarios

!!! info "How to Use Recipe Cards"
    Each recipe card provides a tested approach for common distributed systems challenges. Follow the ingredients and instructions, then adapt to your specific needs.

## 🌍 Recipe: Global Low-Latency Service

### Ingredients
- [ ] 3+ geographic regions
- [ ] Load balancer with geo-routing
- [ ] CDN for static content
- [ ] Regional databases with replication
- [ ] Health checking and failover system

### Instructions

1. **Measure User Distribution**
   ```python
   # Analyze user geography from logs
   user_locations = analyze_access_logs()
   top_regions = user_locations.most_common(5)
   ```

2. **Select Regions Using Latency Matrix**
   ```
   Optimal regions for coverage:
   - Americas: US-East (Virginia) or US-West (Oregon)
   - Europe: EU-West (Ireland) or EU-Central (Frankfurt)
   - Asia: AP-Southeast (Singapore) or AP-Northeast (Tokyo)
   ```

3. **Deploy Services**
   ```yaml
   # Terraform example
   regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
   
   for region in regions:
     - Deploy application servers
     - Set up RDS read replicas
     - Configure regional load balancers
   ```

4. **Configure Geo-Routing**
   ```
   Route 53 Geolocation Routing:
   - North America → us-east-1
   - Europe → eu-west-1
   - Asia → ap-southeast-1
   - Default → closest healthy region
   ```

5. **Implement Health Checks**
   ```python
   @health_check(interval=30, timeout=5)
   def regional_health():
       return {
           "database": check_db_connection(),
           "cache": check_redis_connection(),
           "dependencies": check_external_apis()
       }
   ```

### Variations

**Budget-Conscious**: 2 regions + aggressive CDN caching
**High Availability**: All regions active-active with instant failover
**Compliance-Heavy**: Data residency requirements may override latency

### Expected Results
- Global P95 latency < 100ms
- Regional failover < 30 seconds
- Cost increase: 2.5-3x single region

---

## 🔄 Recipe: Handling Retry Storms

### Ingredients
- [ ] Exponential backoff implementation
- [ ] Circuit breaker library
- [ ] Request ID tracking
- [ ] Retry budget system
- [ ] Monitoring and alerting

### Instructions

1. **Implement Exponential Backoff**
   ```python
   import random
   import time
   
   def exponential_backoff_retry(func, max_retries=5):
       for attempt in range(max_retries):
           try:
               return func()
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               
               # Exponential backoff with jitter
               base_delay = 2 ** attempt
               jitter = random.uniform(0, base_delay * 0.1)
               delay = min(base_delay + jitter, 60)  # Cap at 60s
               
               time.sleep(delay)
   ```

2. **Add Circuit Breakers**
   ```python
   from pybreaker import CircuitBreaker
   
   db_breaker = CircuitBreaker(
       fail_max=5,
       reset_timeout=60,
       expected_exception=DatabaseError
   )
   
   @db_breaker
   def call_database():
       # Your database call
       pass
   ```

3. **Implement Retry Budgets**
   ```python
   class RetryBudget:
       def __init__(self, budget_percent=10):
           self.budget_percent = budget_percent
           self.requests = 0
           self.retries = 0
           
       def can_retry(self):
           if self.requests == 0:
               return True
           retry_rate = (self.retries / self.requests) * 100
           return retry_rate < self.budget_percent
           
       def record_request(self):
           self.requests += 1
           
       def record_retry(self):
           self.retries += 1
   ```

4. **Add Monitoring**
   ```yaml
   alerts:
     - name: retry_storm_detected
       condition: retry_rate > 20%
       window: 5m
       action: page_oncall
       
     - name: circuit_breaker_open
       condition: circuit_breaker.state == "open"
       action: notify_team
   ```

### Variations

**Aggressive**: Shorter timeouts, faster circuit breaker
**Conservative**: Longer backoff, higher retry budget
**Adaptive**: Adjust parameters based on system load

### Expected Results
- Retry storms contained within 30 seconds
- System recovers without manual intervention
- Backend load reduced by 70-90% during incidents

---

## 📊 Recipe: Distributed Tracing Setup

### Ingredients
- [ ] OpenTelemetry SDK
- [ ] Trace collector (Jaeger/Zipkin)
- [ ] Trace storage (Elasticsearch/Cassandra)
- [ ] Correlation ID generator
- [ ] Sampling strategy

### Instructions

1. **Install OpenTelemetry**
   ```bash
   pip install opentelemetry-api
   pip install opentelemetry-sdk
   pip install opentelemetry-instrumentation
   ```

2. **Initialize Tracing**
   ```python
   from opentelemetry import trace
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   from opentelemetry.exporter.jaeger import JaegerExporter
   
   # Setup
   trace.set_tracer_provider(TracerProvider())
   tracer = trace.get_tracer(__name__)
   
   # Configure exporter
   jaeger_exporter = JaegerExporter(
       agent_host_name="localhost",
       agent_port=6831,
   )
   
   span_processor = BatchSpanProcessor(jaeger_exporter)
   trace.get_tracer_provider().add_span_processor(span_processor)
   ```

3. **Instrument Your Code**
   ```python
   @tracer.start_as_current_span("process_request")
   def process_request(request_id):
       span = trace.get_current_span()
       span.set_attribute("request.id", request_id)
       
       # Your business logic
       with tracer.start_as_current_span("database_query"):
           result = query_database()
           
       with tracer.start_as_current_span("cache_update"):
           update_cache(result)
           
       return result
   ```

4. **Implement Sampling**
   ```python
   from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
   
   # Sample 10% of traces
   sampler = TraceIdRatioBased(0.1)
   
   # Or adaptive sampling
   class AdaptiveSampler:
       def should_sample(self, context, trace_id, name):
           # Always sample errors
           if context.get("error"):
               return True
               
           # Sample slow requests
           if context.get("duration_ms", 0) > 1000:
               return True
               
           # Default sampling rate
           return random.random() < 0.01
   ```

5. **Propagate Context**
   ```python
   # HTTP headers
   def inject_trace_context(headers):
       propagator = TraceContextTextMapPropagator()
       propagator.inject(headers)
       return headers
       
   # Message queues
   def publish_with_trace(message, topic):
       headers = {}
       inject_trace_context(headers)
       publish(topic, message, headers)
   ```

### Variations

**High-Volume**: Lower sampling rate, focus on errors
**Debug Mode**: 100% sampling for specific users/requests
**Cost-Optimized**: Local aggregation before sending

### Expected Results
- End-to-end request visibility
- P99 latency attribution
- Dependency mapping
- Error root cause in < 5 minutes

---

## 🔐 Recipe: Zero-Downtime Deployment

### Ingredients
- [ ] Load balancer with health checks
- [ ] Blue-green deployment capability
- [ ] Database migration strategy
- [ ] Feature flags system
- [ ] Rollback plan

### Instructions

1. **Setup Blue-Green Infrastructure**
   ```yaml
   # Kubernetes example
   apiVersion: v1
   kind: Service
   metadata:
     name: app-service
   spec:
     selector:
       app: myapp
       version: $ACTIVE_VERSION  # blue or green
   ```

2. **Implement Health Checks**
   ```python
   @app.route("/health")
   def health_check():
       checks = {
           "database": check_db(),
           "cache": check_cache(),
           "version": APP_VERSION
       }
       
       if all(checks.values()):
           return jsonify(checks), 200
       else:
           return jsonify(checks), 503
   ```

3. **Database Migration Strategy**
   ```sql
   -- Step 1: Add new column (backward compatible)
   ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
   
   -- Step 2: Deploy new code that writes to both old and new
   -- Step 3: Backfill data
   UPDATE users SET email_verified = (email_status = 'verified');
   
   -- Step 4: Deploy code that reads from new column
   -- Step 5: Remove old column
   ALTER TABLE users DROP COLUMN email_status;
   ```

4. **Feature Flag Deployment**
   ```python
   class FeatureFlags:
       def __init__(self):
           self.flags = {
               "new_algorithm": {
                   "enabled": True,
                   "rollout_percentage": 10,
                   "whitelist": ["beta_users"]
               }
           }
           
       def is_enabled(self, flag_name, user_id=None):
           flag = self.flags.get(flag_name, {})
           
           if not flag.get("enabled"):
               return False
               
           if user_id in flag.get("whitelist", []):
               return True
               
           if user_id:
               hash_value = hash(f"{flag_name}:{user_id}") % 100
               return hash_value < flag.get("rollout_percentage", 0)
               
           return False
   ```

5. **Automated Rollback**
   ```bash
   #!/bin/bash
   # deploy.sh
   
   HEALTH_ENDPOINT="https://api.example.com/health"
   OLD_VERSION=$(kubectl get deployment app -o jsonpath='{.spec.template.spec.containers[0].image}')
   
   # Deploy new version
   kubectl set image deployment/app app=$NEW_VERSION
   
   # Wait for rollout
   kubectl rollout status deployment/app --timeout=10m
   
   # Health check loop
   for i in {1..30}; do
       if curl -f $HEALTH_ENDPOINT; then
           echo "Deployment successful"
           exit 0
       fi
       sleep 10
   done
   
   # Rollback on failure
   echo "Health checks failed, rolling back"
   kubectl set image deployment/app app=$OLD_VERSION
   kubectl rollout status deployment/app
   ```

### Variations

**Canary**: Route percentage of traffic to new version
**Rolling**: Update instances one at a time
**Instant**: All instances at once (requires downtime)

### Expected Results
- Zero user-facing downtime
- Rollback capability < 60 seconds
- No data loss or corruption
- Clear audit trail

---

## 🎯 Recipe: Auto-Scaling Based on Business Metrics

### Ingredients
- [ ] Custom metrics collection
- [ ] Scaling policy engine
- [ ] Predictive algorithms
- [ ] Cost constraints
- [ ] Performance targets

### Instructions

1. **Define Business Metrics**
   ```python
   class BusinessMetrics:
       def __init__(self):
           self.metrics = {
               "checkout_queue_depth": 0,
               "payment_processing_time": 0,
               "inventory_sync_lag": 0,
               "revenue_per_minute": 0
           }
           
       def get_scaling_score(self):
           # Combine metrics into scaling decision
           if self.metrics["checkout_queue_depth"] > 100:
               return 2.0  # Double capacity
           
           if self.metrics["payment_processing_time"] > 5000:
               return 1.5  # 50% more capacity
               
           if self.metrics["revenue_per_minute"] > 10000:
               return 1.2  # Proactive scaling
               
           return 1.0  # No change
   ```

2. **Implement Predictive Scaling**
   ```python
   from prophet import Prophet
   import pandas as pd
   
   def predict_load(historical_data):
       # Prepare data for Prophet
       df = pd.DataFrame({
           'ds': historical_data['timestamp'],
           'y': historical_data['requests_per_second']
       })
       
       # Train model
       model = Prophet(daily_seasonality=True)
       model.fit(df)
       
       # Predict next hour
       future = model.make_future_dataframe(periods=60, freq='min')
       forecast = model.predict(future)
       
       return forecast[['ds', 'yhat', 'yhat_upper']]
   ```

3. **Create Scaling Policies**
   ```yaml
   scaling_policies:
     - name: business_hours_scaling
       schedule: "0 9 * * MON-FRI"
       min_instances: 20
       max_instances: 100
       
     - name: flash_sale_scaling
       trigger: manual
       scale_factor: 5
       duration: 4h
       
     - name: cost_aware_scaling
       metric: cost_per_request
       target: 0.002
       scale_down_cooldown: 300
   ```

4. **Implement Cost Controls**
   ```python
   class CostAwareScaler:
       def __init__(self, budget_per_hour=1000):
           self.budget = budget_per_hour
           self.instance_cost = 0.10  # per hour
           
       def calculate_max_instances(self):
           return int(self.budget / self.instance_cost)
           
       def should_scale_up(self, current_instances, desired_instances):
           max_allowed = self.calculate_max_instances()
           
           if desired_instances > max_allowed:
               logger.warning(
                   f"Budget constraint: wanted {desired_instances}, "
                   f"max allowed {max_allowed}"
               )
               return min(desired_instances, max_allowed)
               
           return desired_instances
   ```

### Variations

**Aggressive**: Scale on leading indicators
**Conservative**: Require sustained metrics
**Hybrid**: Combine reactive and predictive

### Expected Results
- Response time SLO: 99% < 200ms
- Scale response time: < 90 seconds
- Cost efficiency: Within 10% of optimal
- No capacity-related outages

---

## 📚 More Recipes Coming Soon

- Implementing Saga Patterns
- Multi-Region Database Sync
- Event Sourcing at Scale
- Service Mesh Migration
- Observability Stack Setup
- Chaos Engineering Program

---

!!! tip "Contributing Recipes"
    Have a tested recipe for a common scenario? Submit a PR with:
    - Clear ingredients list
    - Step-by-step instructions
    - Code examples
    - Expected results
    - Common variations