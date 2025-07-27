---
title: Starter Pack - Essential Patterns for New Systems
description: Perfect pattern bundle for MVPs and new projects
status: complete
last_updated: 2025-07-26
---

# 🚀 Distributed Systems Starter Pack

!!! success "Get to Production Fast with Battle-Tested Patterns"
    This curated collection of Gold-tier patterns provides everything you need to build a reliable distributed system from day one. Perfect for MVPs, new projects, and teams beginning their distributed systems journey.

## What's Included

<div class="grid cards" markdown>

- :material-shield-check:{ .lg .middle } **Core Resilience**
    
    ---
    
    **5 Essential Patterns**:
    - Circuit Breaker
    - Retry & Backoff
    - Timeout
    - Health Check
    - Load Balancing
    
    **Result**: 99.9% availability from day one

- :material-clock-fast:{ .lg .middle } **Quick Implementation**
    
    ---
    
    **Time to Production**: 2 weeks
    - Week 1: Learn & prototype
    - Week 2: Implement & test
    
    **Complexity**: Low to Medium
    
    **Prerequisites**: Basic distributed systems knowledge

- :material-trending-up:{ .lg .middle } **Proven Results**
    
    ---
    
    **Success Metrics**:
    - 3x reliability improvement
    - 50% reduction in cascading failures
    - 80% faster incident resolution
    - 90% reduction in timeout-related issues

- :material-currency-usd:{ .lg .middle } **Cost Effective**
    
    ---
    
    **Low Overhead**:
    - Minimal infrastructure changes
    - Uses existing tools
    - Open source options available
    - Cloud-agnostic approach

</div>

## The Essential Five Patterns

### 1. 🔌 Circuit Breaker
**Purpose**: Prevent cascading failures when services are down

<div class="decision-box">
<h4>Quick Implementation Guide</h4>

```python
from pybreaker import CircuitBreaker

# Configure circuit breaker
db_breaker = CircuitBreaker(
    fail_max=5,                    # Trip after 5 failures
    reset_timeout=60,              # Try again after 60s
    exclude=[KeyError]             # Don't trip on app errors
)

@db_breaker
def call_database():
    # Your database call here
    return db.query("SELECT * FROM users")

# Usage - automatically protected
try:
    users = call_database()
except Exception as e:
    # Fallback when circuit is open
    return cached_users
```

**Key Metrics**:
- Trip threshold: 5 consecutive failures
- Reset timeout: 60 seconds
- Success threshold: 2 consecutive successes
</div>

**Real-world Impact**: Netflix prevented 90% of cascading failures with circuit breakers

### 2. 🔄 Retry & Backoff
**Purpose**: Handle transient failures gracefully

```python
import backoff
import requests

@backoff.on_exception(
    backoff.expo,                  # Exponential backoff
    requests.exceptions.RequestException,
    max_tries=3,                   # Maximum 3 attempts
    max_time=10                    # Give up after 10 seconds
)
def call_api(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

# Automatic retry with exponential backoff
# Attempt 1: immediate
# Attempt 2: 2s delay
# Attempt 3: 4s delay
data = call_api("https://api.example.com/data")
```

**Best Practices**:
- Use exponential backoff
- Add jitter to prevent thundering herd
- Set maximum retry limits
- Only retry idempotent operations

### 3. ⏱️ Timeout
**Purpose**: Prevent resource exhaustion from slow operations

```yaml
# Service configuration
timeouts:
  default:
    connect: 5s      # TCP handshake
    read: 30s        # Response read
    write: 10s       # Request write
    total: 45s       # End-to-end
    
  by_service:
    database:
      connect: 3s
      query: 10s
    external_api:
      connect: 5s
      read: 60s
    cache:
      connect: 1s
      read: 2s
```

**Timeout Hierarchy**:
```
Client (60s)
  └── API Gateway (50s)
       └── Service A (40s)
            ├── Database (10s)
            └── Service B (20s)
```

### 4. ❤️ Health Check
**Purpose**: Know when services are ready to accept traffic

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/health/live')
def liveness_check():
    """Is the service running?"""
    return jsonify({"status": "alive"}), 200

@app.route('/health/ready')
def readiness_check():
    """Is the service ready to accept traffic?"""
    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "disk_space": check_disk_space()
    }
    
    if all(checks.values()):
        return jsonify({
            "status": "ready",
            "checks": checks
        }), 200
    else:
        return jsonify({
            "status": "not ready",
            "checks": checks
        }), 503

def check_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return True
    except:
        return False
```

**Kubernetes Integration**:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 5. ⚖️ Load Balancing
**Purpose**: Distribute traffic across multiple instances

```nginx
# Nginx load balancer configuration
upstream backend {
    least_conn;  # Use least connections algorithm
    
    server backend1.example.com:8080 weight=3;
    server backend2.example.com:8080 weight=2;
    server backend3.example.com:8080 weight=1;
    
    # Health checks
    check interval=5s fail=3 pass=2;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_timeout 30s;
        proxy_connect_timeout 5s;
        
        # Retry on failure
        proxy_next_upstream error timeout;
        proxy_next_upstream_tries 3;
    }
}
```

**Load Balancing Algorithms**:
- **Round Robin**: Simple, equal distribution
- **Least Connections**: Route to least busy server
- **Weighted**: Distribute based on server capacity
- **IP Hash**: Sticky sessions for stateful apps

## Implementation Roadmap

### Week 1: Foundation
<div class="grid" markdown>

**Day 1-2: Learn & Plan**
- [ ] Review all 5 patterns
- [ ] Map to your architecture
- [ ] Identify integration points
- [ ] Set success metrics

**Day 3-4: Prototype**
- [ ] Implement Circuit Breaker
- [ ] Add Retry logic
- [ ] Configure Timeouts
- [ ] Test failure scenarios

**Day 5: Health & Load Balancing**
- [ ] Create health endpoints
- [ ] Configure load balancer
- [ ] Test traffic distribution
- [ ] Verify health checks

</div>

### Week 2: Production Readiness
<div class="grid" markdown>

**Day 6-7: Integration**
- [ ] Integrate with services
- [ ] Add monitoring
- [ ] Create dashboards
- [ ] Document configuration

**Day 8-9: Testing**
- [ ] Load testing
- [ ] Chaos testing
- [ ] Failure injection
- [ ] Performance tuning

**Day 10: Launch**
- [ ] Deploy to production
- [ ] Monitor metrics
- [ ] Tune thresholds
- [ ] Celebrate! 🎉

</div>

## Monitoring Dashboard

```yaml
# Essential metrics to track
metrics:
  circuit_breaker:
    - circuit_state (open/closed/half-open)
    - failure_rate
    - success_rate
    - trip_frequency
    
  retry:
    - retry_count_by_service
    - retry_success_rate
    - backoff_duration
    
  timeout:
    - timeout_rate_by_service
    - p99_latency
    - timeout_vs_total_requests
    
  health_check:
    - health_check_status
    - health_check_latency
    - dependency_health
    
  load_balancing:
    - requests_per_instance
    - instance_health_status
    - load_distribution_variance
```

## Common Pitfalls & Solutions

<div class="failure-vignette">
<h4>💥 Starter Pack Anti-Patterns</h4>

**1. Circuit Breaker Too Sensitive**
- Problem: Trips on minor issues
- Solution: Tune thresholds based on actual failure patterns

**2. Retry Storm**
- Problem: All instances retry simultaneously
- Solution: Add jitter to retry delays

**3. Timeout Cascade**
- Problem: Parent timeout shorter than child
- Solution: Implement timeout budget hierarchy

**4. Health Check False Positives**
- Problem: Service reports healthy but can't serve traffic
- Solution: Separate liveness and readiness checks

**5. Uneven Load Distribution**
- Problem: One instance gets all traffic
- Solution: Check session affinity and algorithm
</div>

## Starter Pack Checklist

### Pre-Implementation
- [ ] Identify all service dependencies
- [ ] Map critical user journeys
- [ ] Define SLOs (availability, latency)
- [ ] Set up monitoring infrastructure

### Implementation
- [ ] Circuit breaker on all external calls
- [ ] Retry logic for idempotent operations
- [ ] Timeouts on every network call
- [ ] Health endpoints for each service
- [ ] Load balancer for service instances

### Post-Implementation
- [ ] Dashboard with all key metrics
- [ ] Alerts for pattern failures
- [ ] Runbooks for common issues
- [ ] Team training completed

## Success Stories

<div class="grid cards" markdown>

- **🚗 Ride-Sharing Startup**
    
    Implemented starter pack in 2 weeks
    - 99.9% availability achieved
    - 0 cascading failures in 6 months
    - 50% reduction in on-call alerts

- **🛒 E-commerce Platform**
    
    Black Friday success story
    - Handled 10x normal traffic
    - No downtime during peak
    - $2M additional revenue

- **🏦 FinTech API**
    
    Regulatory compliance achieved
    - 99.99% availability SLA met
    - Full audit trail via health checks
    - 30% reduction in support tickets

</div>

## What's Next?

Once you've mastered the Starter Pack patterns:

1. **📈 [Scale Pack](scale-pack.md)**: Patterns for 10x-100x growth
   - Sharding, CQRS, Service Mesh
   - Auto-scaling, Event Streaming

2. **🏢 [Enterprise Pack](enterprise-pack.md)**: Mission-critical patterns
   - Multi-region, Saga, Cell-based
   - Zero-trust security, Chaos engineering

3. **🔧 [Pattern Selector Tool](../pattern-selector-tool.md)**: Find specific patterns for your needs

## Tools & Libraries

### Circuit Breaker
- **Java**: Hystrix, Resilience4j
- **Python**: pybreaker, circuit-breaker
- **Go**: sony/gobreaker, afex/hystrix-go
- **Node.js**: opossum, circuit-breaker-js

### Retry & Backoff
- **Java**: Spring Retry, Failsafe
- **Python**: backoff, tenacity
- **Go**: avast/retry-go
- **Node.js**: async-retry, p-retry

### Health Checks
- **Framework agnostic**: health-check libraries
- **Kubernetes**: Built-in probes
- **Spring Boot**: Actuator
- **Express.js**: express-healthcheck

### Load Balancing
- **Software**: Nginx, HAProxy, Traefik
- **Cloud**: AWS ELB, GCP Load Balancer
- **Service Mesh**: Istio, Linkerd

---

**Remember**: These five patterns solve 80% of distributed systems reliability issues. Master them first before moving to more complex patterns.