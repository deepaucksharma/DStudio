# Episode 8: API Gateway Patterns Code Examples

## 🏛️ Mumbai Digital Gateway - Production-Ready Implementation

Welcome to Episode 8's comprehensive code examples for API Gateway Patterns! This collection provides production-ready implementations inspired by Mumbai's Gateway of India, designed for Indian fintech services like Paytm, Razorpay, and PhonePe.

### 📋 Overview

This repository contains 15+ production-ready code examples demonstrating:
- **Kong API Gateway Configuration** - Complete Kubernetes setup
- **Rate Limiting & Throttling** - UPI-compliant transaction limits
- **Authentication & Authorization** - JWT, OAuth2, API Keys
- **Request/Response Transformation** - Indian API format standards
- **Load Balancing** - Mumbai traffic-inspired algorithms
- **Circuit Breakers** - Failsafe patterns for high availability
- **API Versioning** - Backward compatibility management
- **Monitoring & Analytics** - Comprehensive observability

### 🏗️ Architecture

```
Mumbai Digital Gateway Architecture
═══════════════════════════════════

    ┌─────────────────────────────────────┐
    │         Internet Traffic           │
    │    (Mobile Apps, Web, Partners)    │
    └─────────────┬───────────────────────┘
                  │
    ┌─────────────▼───────────────────────┐
    │        Kong API Gateway            │
    │    (Digital Gateway of India)      │
    ├─────────────────────────────────────┤
    │ Rate Limiting │ Auth │ Transform   │
    │ Load Balance │ CORS │ Monitoring   │
    └─────────────┬───────────────────────┘
                  │
    ┌─────────────▼───────────────────────┐
    │         Service Routing            │
    └──┬────────┬────────┬────────┬───────┘
       │        │        │        │
   ┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼────┐
   │Payment│ │Order │ │User  │ │Notify │
   │Service│ │Service│ │Service│ │Service│ 
   └───────┘ └──────┘ └──────┘ └───────┘
       │        │        │        │
   ┌───▼────────▼────────▼────────▼───┐
   │        Backend Services          │
   │  (PostgreSQL, Redis, MongoDB)    │
   └─────────────────────────────────────┘
```

### 📁 Directory Structure

```
episode-008-api-gateway/
├── code/
│   ├── kubernetes/              # K8s manifests
│   │   └── kong-gateway-setup.yaml
│   ├── python/                  # Python implementations
│   │   ├── 01_kong_api_management.py
│   │   ├── 02_rate_limiting_system.py
│   │   ├── 03_auth_middleware.py
│   │   ├── 04_request_transformer.py
│   │   ├── 05_circuit_breaker.py
│   │   ├── 06_api_versioning.py
│   │   ├── 07_load_balancer.py
│   │   └── 08_gateway_analytics.py
│   ├── go/                      # Go implementations
│   │   ├── 01_custom_plugin.go
│   │   ├── 02_middleware_chain.go
│   │   ├── 03_health_checker.go
│   │   ├── 04_metrics_collector.go
│   │   └── 05_gateway_controller.go
│   ├── java/                    # Java implementations
│   │   ├── SpringCloudGateway.java
│   │   ├── APIGatewayFilter.java
│   │   └── GatewayConfiguration.java
│   ├── config/                  # Configuration files
│   │   ├── kong/
│   │   ├── nginx/
│   │   └── prometheus/
│   ├── tests/                   # Test suites
│   ├── docker-compose.yml       # Local development
│   └── requirements.txt         # Dependencies
```

### 🚀 Quick Start

#### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Go 1.21+
- Java 17+ (for Spring examples)
- Kubernetes cluster (for production)

#### 1. Local Development Setup

```bash
# Start Mumbai API Gateway environment
docker-compose up -d

# Wait for Kong to be ready
docker-compose logs -f kong-gateway

# Install Python dependencies
pip install -r requirements.txt

# Initialize Kong with Mumbai configuration
python python/01_kong_api_management.py
```

#### 2. Verify Gateway Setup

```bash
# Check Kong Admin API
curl http://localhost:8001/status

# Test proxy endpoint
curl http://localhost:8000/health

# View Kong Manager UI
open http://localhost:8002
```

### 💡 Code Examples

#### 🔧 1. Kong API Management
**File**: `python/01_kong_api_management.py`

**Mumbai Context**: Digital Gateway of India management system

```python
# Initialize Kong manager
kong_manager = MumbaiKongManager()

# Setup UPI Payment API with RBI compliance  
upi_setup = kong_manager.setup_upi_payment_api()

# Configure rate limiting for UPI transactions
rate_limit_plugin = PluginConfig(
    name="rate-limiting",
    config={
        "minute": 20,      # Max 20 UPI transactions per minute
        "hour": 100,       # Max 100 per hour
        "day": 1000,       # Max 1000 per day (RBI limit)
        "policy": "redis"
    }
)
```

**Features**:
- Complete Kong configuration
- RBI-compliant UPI setup
- Service registration automation
- Plugin management system
- Health monitoring integration

#### 🚫 2. Rate Limiting System
**File**: `python/02_rate_limiting_system.py`

**Mumbai Context**: Traffic signal timing control

```python
# Initialize rate limiter with Mumbai patterns
rate_limiter = MumbaiRateLimiter(
    redis_url="redis://localhost:6379",
    default_limits={
        "upi_transactions": "20/minute",
        "api_calls": "100/minute", 
        "file_uploads": "5/minute"
    }
)

# Apply UPI-specific limits
@rate_limiter.limit("upi_transactions")
def process_upi_payment(request):
    return {"status": "processing", "txn_id": "UPI123456"}

# Mumbai peak hour adjustments
rate_limiter.apply_peak_hour_limits()
```

**Features**:
- Redis-based distributed limiting
- UPI transaction compliance
- Peak hour adjustments
- Sliding window algorithms
- Custom limit definitions

#### 🔐 3. Authentication Middleware
**File**: `python/03_auth_middleware.py`

**Mumbai Context**: Gateway security checkpoint system

```python
# Setup authentication for Indian services
auth_middleware = MumbaiAuthMiddleware()

# JWT validation for UPI apps
@auth_middleware.jwt_required(
    issuer="mumbai-gateway.com",
    audience="upi-apps",
    algorithms=["RS256"]
)
def upi_endpoint(request):
    user_id = request.jwt_claims["sub"]
    return process_payment(user_id)

# API key validation for partners
@auth_middleware.api_key_required(
    header_name="X-API-Key",
    validate_permissions=True
)
def partner_api(request):
    partner_id = request.api_key_info["partner_id"]
    return get_partner_data(partner_id)
```

**Features**:
- JWT token validation
- API key management
- OAuth2 integration
- Role-based access control
- Indian compliance features

#### 🔄 4. Request Transformer
**File**: `python/04_request_transformer.py`

**Mumbai Context**: Format standardization for Indian APIs

```python
# Transform requests for Indian context
transformer = MumbaiRequestTransformer()

# Add Indian headers automatically
transformer.add_default_headers({
    "X-Country": "IN",
    "X-Currency": "INR",
    "X-Timezone": "Asia/Kolkata",
    "X-Gateway": "Mumbai-Digital-Gateway"
})

# Transform mobile numbers to E.164 format
@transformer.transform_request
def standardize_mobile(request_data):
    if "mobile" in request_data:
        request_data["mobile"] = format_indian_mobile(request_data["mobile"])
    return request_data
```

**Features**:
- Automatic header injection
- Mobile number formatting
- Currency conversion
- Timezone handling
- Request validation

#### ⚡ 5. Circuit Breaker
**File**: `python/05_circuit_breaker.py`

**Mumbai Context**: Traffic diversion during failures

```python
# Setup circuit breakers for Mumbai services
circuit_breaker = MumbaiCircuitBreaker()

@circuit_breaker.protect(
    service_name="payment-service",
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=PaymentServiceError
)
def call_payment_service(payment_data):
    return payment_service.process(payment_data)

# Fallback for UPI failures
@circuit_breaker.fallback("payment-service")
def payment_fallback():
    return {"status": "retry_later", "message": "Payment service temporarily unavailable"}
```

**Features**:
- Configurable failure thresholds
- Automatic recovery detection
- Service-specific fallbacks
- Metrics integration
- Mumbai traffic-inspired patterns

### 🔧 Configuration Examples

#### Kong Gateway Configuration

```yaml
# Kong service for UPI payments
services:
- name: upi-payment-service
  url: http://upi-backend:8080
  protocol: http
  retries: 3
  connect_timeout: 30000
  write_timeout: 30000
  read_timeout: 30000

# Routes for UPI endpoints  
routes:
- name: upi-routes
  service: upi-payment-service
  protocols: [https]
  methods: [POST]
  hosts: [payments.mumbai-gateway.com]
  paths: ["/api/upi", "/api/v1/upi"]

# Plugins for compliance
plugins:
- name: rate-limiting
  config:
    minute: 20
    hour: 100
    day: 1000
    policy: redis
    redis_host: redis.mumbai.svc
- name: jwt
  config:
    claims_to_verify: [exp, aud, sub]
    maximum_expiration: 3600
```

#### Environment Configuration

```bash
# Mumbai Gateway Configuration
export GATEWAY_NAME="Mumbai Digital Gateway"
export GATEWAY_REGION="mumbai"
export GATEWAY_TIMEZONE="Asia/Kolkata"

# Kong Configuration
export KONG_ADMIN_URL="http://localhost:8001"
export KONG_PROXY_URL="http://localhost:8000"
export KONG_DATABASE_URL="postgres://kong:kong123@postgres:5432/kong"

# Redis Configuration (for rate limiting)
export REDIS_URL="redis://redis:6379"
export REDIS_PASSWORD="mumbai123"

# Compliance Settings
export RBI_COMPLIANCE=true
export UPI_RATE_LIMIT="20/minute"
export MAX_DAILY_TRANSACTIONS=1000

# Monitoring
export PROMETHEUS_URL="http://prometheus:9090"
export JAEGER_URL="http://jaeger:16686"
```

### 📊 API Gateway Patterns

#### 1. Mumbai Traffic-Inspired Load Balancing

```python
# Load balancing based on Mumbai local train patterns
class MumbaiLoadBalancer:
    def select_instance(self, instances, request_context):
        current_hour = datetime.now().hour
        
        # Peak hour routing (7-11 AM, 5-10 PM)
        if self.is_peak_hour(current_hour):
            return self.select_local_instance(instances)
        
        # Festival routing - distribute evenly
        if self.is_festival_day():
            return self.round_robin_select(instances)
        
        # Normal weighted routing
        return self.weighted_select(instances)
```

#### 2. UPI Transaction Rate Limiting

```python
# RBI-compliant UPI rate limiting
upi_limits = {
    "per_minute": 20,    # Max 20 transactions per minute
    "per_hour": 100,     # Max 100 per hour
    "per_day": 1000,     # Max 1000 per day
    "per_month": 20000   # Max 20,000 per month
}

# Apply limits with sliding window
rate_limiter.configure_sliding_window(
    window_size=60,      # 60 seconds
    max_requests=20,
    burst_allowance=5    # Allow small bursts
)
```

#### 3. API Versioning Strategy

```python
# Version management for Mumbai APIs
version_manager = APIVersionManager()

# Support multiple API versions
version_manager.register_version("v1", {
    "deprecation_date": "2024-12-31",
    "support_level": "full",
    "breaking_changes": []
})

version_manager.register_version("v2", {
    "introduction_date": "2024-06-01", 
    "new_features": ["enhanced_upi", "multi_currency"],
    "default": True
})

# Route based on version header or URL
@version_manager.route_version
def payment_endpoint(request, version):
    if version == "v1":
        return legacy_payment_processor(request)
    else:
        return enhanced_payment_processor(request)
```

### 📈 Monitoring & Analytics

#### Dashboard Access Points

- **Kong Manager**: http://localhost:8002
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/mumbai123)
- **Jaeger UI**: http://localhost:16686

#### Key Metrics

```
# API Gateway Metrics
kong_http_requests_total{service="upi-payment",method="POST"}
kong_latency{service="order-service",type="request"}
kong_bandwidth{service="restaurant-service",type="egress"}
mumbai_gateway_active_connections
mumbai_gateway_error_rate

# UPI-Specific Metrics
upi_transactions_total{status="success"}
upi_transactions_per_minute{limit="20"}
upi_compliance_violations{type="rate_limit"}
```

#### Alert Rules

```yaml
# Mumbai Gateway Alerts
groups:
- name: mumbai-gateway-alerts
  rules:
  - alert: HighUPIErrorRate
    expr: rate(upi_transactions_total{status="error"}[5m]) > 0.1
    labels:
      severity: critical
      service: upi-payment
    annotations:
      summary: "High UPI transaction error rate"
      
  - alert: RateLimitExceeded
    expr: rate(kong_http_requests_total{code="429"}[1m]) > 10
    labels:
      severity: warning
    annotations:
      summary: "Rate limiting frequently triggered"
```

### 🧪 Testing

#### Load Testing UPI Endpoints

```python
# UPI transaction load test
import asyncio
from locust import HttpUser, task, between

class UPILoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Get JWT token
        self.token = self.get_auth_token()
    
    @task(3)
    def upi_payment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/upi/pay", json={
            "amount": 100,
            "from_vpa": "test@upi",
            "to_vpa": "merchant@upi"
        }, headers=headers)
    
    @task(1)
    def check_balance(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/upi/balance", headers=headers)

# Run load test
# locust -f upi_load_test.py --host=http://localhost:8000
```

#### Circuit Breaker Testing

```python
# Test circuit breaker behavior
def test_circuit_breaker():
    circuit_breaker = MumbaiCircuitBreaker()
    
    # Trigger failures
    for i in range(6):  # Exceed threshold of 5
        try:
            circuit_breaker.call_service("failing-service")
        except CircuitBreakerOpenException:
            assert i >= 5  # Should open after 5 failures
    
    # Test recovery
    time.sleep(31)  # Wait for recovery timeout
    assert circuit_breaker.get_state("failing-service") == "HALF_OPEN"
```

### 🚀 Production Deployment

#### Kubernetes Deployment

```bash
# Deploy Kong Gateway
kubectl apply -f kubernetes/kong-gateway-setup.yaml

# Verify deployment
kubectl get pods -n mumbai-api-gateway
kubectl get services -n mumbai-api-gateway

# Configure Kong
python scripts/setup_production_kong.py

# Test deployment
curl -H "Host: api.mumbai-gateway.com" \
     http://$(kubectl get svc kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/health
```

#### High Availability Setup

```yaml
# Kong deployment with HA
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  
# PostgreSQL with replication
postgresql:
  architecture: replication
  master:
    persistence:
      size: 100Gi
  slave:
    replicaCount: 2
```

### 📚 Documentation

#### API Documentation

- **OpenAPI Spec**: [api-spec.yaml](./docs/api-spec.yaml)
- **Postman Collection**: [mumbai-gateway.postman.json](./docs/postman/)
- **Rate Limits**: [rate-limiting-guide.md](./docs/rate-limiting-guide.md)

#### Integration Guides

- **Kong Plugin Development**: [plugin-development.md](./docs/plugin-development.md)
- **UPI Integration**: [upi-integration.md](./docs/upi-integration.md)
- **Authentication Setup**: [auth-setup.md](./docs/auth-setup.md)

### 🛠️ Development

#### Setup Development Environment

```bash
# Clone and setup
git clone <repository>
cd episode-008-api-gateway/code

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Go environment
go mod tidy
go build ./go/...

# Start development stack
docker-compose -f docker-compose.dev.yml up -d
```

#### Create Custom Plugin

```python
# Custom Kong plugin example
class MumbaiCustomPlugin:
    def __init__(self):
        self.name = "mumbai-custom"
        self.version = "1.0.0"
    
    def access(self, kong, request):
        # Add Mumbai-specific processing
        if request.headers.get("X-Source") == "mumbai-app":
            request.headers["X-Priority"] = "high"
        
        return kong.response.ok()
```

### 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/mumbai-enhancement`
3. Commit changes: `git commit -am 'Add Mumbai-specific feature'`
4. Push branch: `git push origin feature/mumbai-enhancement`
5. Create Pull Request

### 📞 Support & Community

- **Issues**: GitHub Issues with `[Episode 8]` prefix
- **Discussions**: Mumbai Tech Community Discord
- **Documentation**: `/docs` directory
- **Examples**: `/examples` directory

### 🏷️ Tags

`#APIGateway` `#Kong` `#Mumbai` `#Gateway` `#RateLimiting` `#UPI` `#Authentication` `#Microservices` `#LoadBalancing` `#CircuitBreaker` `#Indian` `#Fintech` `#Production`

---

## 🚀 Ready to Deploy Your Mumbai Digital Gateway?

This comprehensive codebase provides everything needed to build a production-grade API Gateway inspired by Mumbai's iconic Gateway of India. Each component is designed with Indian context, supporting the scale and compliance requirements of services like Paytm, Razorpay, and PhonePe.

**Start with**: `docker-compose up -d` and explore the Mumbai Digital Gateway! 🏛️