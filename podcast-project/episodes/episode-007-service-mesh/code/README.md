# Episode 7: Service Mesh Architecture Code Examples

## 🚂 Mumbai Service Mesh - Production-Ready Implementation

Welcome to Episode 7's comprehensive code examples for Service Mesh Architecture! This collection provides production-ready implementations inspired by Mumbai traffic management systems, designed for Indian fintech services like Paytm and PhonePe.

### 📋 Overview

This repository contains 15+ production-ready code examples demonstrating:
- **Istio Service Mesh Configuration** - Complete setup for Kubernetes
- **Envoy Proxy Management** - Dynamic configuration and control
- **mTLS Certificate Management** - Automated certificate rotation
- **Traffic Management** - Intelligent routing with Mumbai-style algorithms
- **Observability Dashboard** - Comprehensive monitoring solution
- **Service Mesh Controller** - Custom Go-based control plane
- **Local Development Environment** - Docker Compose setup

### 🏗️ Architecture

```
Mumbai Service Mesh Architecture
═══════════════════════════════

    ┌─────────────────────────────────────┐
    │        Istio Control Plane          │
    │    (Mumbai Traffic Control Room)    │
    └─────────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐       ┌────▼────┐       ┌────▼────┐
│Service │◄─────►│ Service │◄─────►│ Service │
│   A    │       │    B    │       │    C    │
│(Envoy) │       │ (Envoy) │       │ (Envoy) │
└────────┘       └─────────┘       └─────────┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
    ┌─────────────────────────────────────┐
    │     Mumbai Observability Stack     │
    │  (Prometheus + Jaeger + Grafana)   │
    └─────────────────────────────────────┘
```

### 📁 Directory Structure

```
episode-007-service-mesh/
├── code/
│   ├── kubernetes/              # K8s manifests
│   │   └── istio-installation.yaml
│   ├── python/                  # Python implementations
│   │   ├── 01_envoy_proxy_config_manager.py
│   │   ├── 02_mtls_certificate_manager.py
│   │   ├── 03_traffic_management_system.py
│   │   └── 04_observability_dashboard.py
│   ├── go/                      # Go implementations
│   │   └── 01_service_mesh_controller.go
│   ├── java/                    # Java implementations (pending)
│   ├── tests/                   # Test suites
│   ├── docker-compose.yml       # Local development
│   └── requirements.txt         # Python dependencies
```

### 🚀 Quick Start

#### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Go 1.21+
- Kubernetes cluster (for production)

#### 1. Local Development Setup

```bash
# Start Mumbai service mesh environment
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Run Envoy configuration manager
python python/01_envoy_proxy_config_manager.py

# Check services
curl http://localhost:10000/health
```

#### 2. Production Kubernetes Deployment

```bash
# Deploy Istio control plane
kubectl apply -f kubernetes/istio-installation.yaml

# Verify installation
kubectl get pods -n istio-system

# Check Istio configuration
istioctl analyze
```

### 💡 Code Examples

#### 🔧 1. Envoy Proxy Configuration Manager
**File**: `python/01_envoy_proxy_config_manager.py`

**Mumbai Context**: Like Mumbai traffic control managing signal timing

```python
# Example: Register Paytm-style payment service
payment_endpoints = [
    ServiceEndpoint("10.0.1.10", 8080, weight=100, region="mumbai", az="west"),
    ServiceEndpoint("10.0.1.11", 8080, weight=100, region="mumbai", az="west"), 
    ServiceEndpoint("10.0.2.10", 8080, weight=80, region="mumbai", az="east"),
]

config_manager.register_service("upi-payment-service", payment_endpoints)

# Handle Mumbai peak traffic
is_peak = config_manager.handle_peak_traffic()
selected_instance = config_manager.route_request("upi-payment-service", context)
```

**Features**:
- Dynamic service registration
- Mumbai peak hour traffic management  
- Circuit breaker patterns
- Health check automation
- Kubernetes ConfigMap export

#### 🔒 2. mTLS Certificate Manager
**File**: `python/02_mtls_certificate_manager.py`

**Mumbai Context**: Like Mumbai police radio encryption key management

```python
# Initialize certificate manager
mtls_manager = MumbaiMTLSManager()

# Generate certificate for service
cert_info = mtls_manager.generate_service_certificate("payment-service")

# Auto-rotate expiring certificates
mtls_manager.auto_rotate_expiring_certificates()

# Deploy to Kubernetes
success = mtls_manager.create_kubernetes_secret("payment-service")
```

**Features**:
- Automated certificate generation
- 90-day rotation cycle
- Kubernetes integration
- Mumbai-style service naming
- Production-grade security

#### 🚦 3. Traffic Management System
**File**: `python/03_traffic_management_system.py`

**Mumbai Context**: Mumbai local train routing optimization

```python
# Initialize traffic manager
traffic_manager = MumbaiTrafficManager()

# Register services
traffic_manager.register_service("order-service", instances)

# Implement canary deployment (like testing new train routes)
traffic_manager.implement_canary_deployment("order-service", "v2", 10)

# Route requests based on Mumbai traffic conditions
instance = traffic_manager.route_request("order-service", request_context)
```

**Features**:
- Peak hour routing algorithms
- Canary deployment management
- Circuit breaker implementation
- Mumbai festival traffic handling
- Real-time traffic state monitoring

#### 📊 4. Observability Dashboard
**File**: `python/04_observability_dashboard.py`

**Mumbai Context**: Mumbai traffic control center dashboard

```python
# Initialize dashboard
dashboard = MumbaiObservabilityDashboard()

# Record service metrics
dashboard.record_request("payment-service", "POST", "200", 125.5)

# Get comprehensive status
summary = dashboard.get_dashboard_summary()

# Start web interface
dashboard.start_dashboard(host='0.0.0.0', port=8080)
```

**Features**:
- Prometheus metrics integration
- Jaeger distributed tracing
- Real-time alerting system
- Hindi-friendly interface
- Mumbai-themed monitoring

#### 🏗️ 5. Service Mesh Controller (Go)
**File**: `go/01_service_mesh_controller.go`

**Mumbai Context**: Central traffic command and control

```go
// Create controller
controller := NewMumbaiServiceMeshController()

// Register services
controller.RegisterService("order-service", &ServiceInstance{
    ID:      "order-svc-1",
    Host:    "10.0.1.10", 
    Port:    8080,
    Zone:    "mumbai-west",
    Weight:  100,
})

// Select instance with load balancing
instance, err := controller.SelectInstance("order-service")

// Record request results for circuit breaking
controller.RecordRequestResult("order-service", success)
```

**Features**:
- High-performance Go implementation
- Kubernetes integration
- HTTP API for management
- Mumbai traffic pattern awareness
- Production monitoring

### 🔧 Configuration

#### Environment Variables

```bash
# Service Mesh Configuration
export ISTIO_NAMESPACE=istio-system
export MESH_CONFIG_PATH=/etc/mesh/config
export PROMETHEUS_URL=http://prometheus:9090
export JAEGER_URL=http://jaeger:16686

# Mumbai Context
export REGION=mumbai
export TIMEZONE=Asia/Kolkata
export PEAK_HOURS="7-11,17-22"

# Security
export TLS_CERT_PATH=/etc/ssl/certs
export CA_CERT_VALIDITY_DAYS=3650
export SERVICE_CERT_VALIDITY_DAYS=90
```

#### Mumbai Traffic Patterns

```yaml
# Peak hour configuration
peak_hours:
  morning:
    start: 7
    end: 11
    zone: "mumbai-west"
  evening:
    start: 17
    end: 22
    zone: "mumbai-west"
  lunch:
    start: 12
    end: 14
    zone: "mumbai-central"

# Festival dates (affects traffic patterns)
festivals:
  - "2024-08-19"  # Ganesh Chaturthi
  - "2024-08-29"  # Ganesh Visarjan
  - "2024-11-05"  # Diwali
```

### 📊 Monitoring & Observability

#### Dashboards Available

- **Grafana Dashboard**: http://localhost:3000 (admin/mumbai123)
- **Jaeger UI**: http://localhost:16686
- **Prometheus**: http://localhost:9090
- **Envoy Admin**: http://localhost:9901

#### Key Metrics

```
# Service Mesh Metrics
mumbai_mesh_requests_total{service="payment-service",status="200"}
mumbai_mesh_response_time_seconds{service="order-service"}
mumbai_mesh_active_connections{service="restaurant-service"}
mumbai_mesh_circuit_breaker_state{service="notification-service"}

# Mumbai Traffic Metrics  
mumbai_traffic_state{state="peak_hour"}
mumbai_peak_hour_multiplier{zone="west"}
mumbai_festival_traffic_factor
```

### 🧪 Testing

#### Unit Tests
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_envoy_config_manager.py

# Coverage report
pytest --cov=. --cov-report=html
```

#### Integration Tests
```bash
# Test with real Envoy proxy
docker-compose -f docker-compose.test.yml up -d
python tests/integration/test_envoy_integration.py
```

#### Load Testing
```bash
# Mumbai peak hour simulation
python tests/load/mumbai_peak_hour_test.py

# UPI transaction burst test
python tests/load/upi_transaction_burst.py
```

### 🏭 Production Deployment

#### Kubernetes Manifests

```bash
# Deploy complete service mesh
kubectl apply -f kubernetes/

# Verify deployment
kubectl get pods -n istio-system
kubectl get services -n istio-system

# Check mesh configuration
istioctl analyze
istioctl proxy-config cluster order-service-v1-xxxxx
```

#### Scaling Guidelines

```yaml
# Production scaling recommendations
resources:
  requests:
    cpu: 250m      # Base CPU
    memory: 512Mi  # Base memory
  limits:
    cpu: 1000m     # Max CPU for burst
    memory: 2Gi    # Max memory

replicas:
  min: 2          # High availability
  max: 20         # Peak hour scaling
  target_cpu: 80  # Scale at 80% CPU
```

### 🚨 Troubleshooting

#### Common Issues

**1. Certificate Rotation Failures**
```bash
# Check certificate status
python -c "from python.mtls_certificate_manager import *; mgr = MumbaiMTLSManager(); print(mgr.check_certificate_expiry())"

# Force certificate rotation
kubectl delete secret payment-service-mtls-certs -n mumbai
```

**2. Peak Hour Performance Issues**
```bash
# Check traffic state
curl http://localhost:8088/api/metrics | jq '.traffic_state'

# Review circuit breaker status
kubectl logs -n istio-system mumbai-mesh-controller
```

**3. Service Discovery Issues**
```bash
# Check Envoy configuration
curl http://localhost:9901/config_dump | jq '.configs[0].dynamic_active_clusters'

# Verify service registration
curl http://localhost:8088/services
```

### 📚 Learning Resources

#### Mumbai Service Mesh Concepts
- [Episode 7 Script](../script/episode-script.md) - Complete Hindi explanation
- [Mumbai Traffic Management](../research/mumbai-traffic-patterns.md) - Real-world inspiration
- [Indian Fintech Architecture](../docs/indian-fintech-patterns.md) - Industry patterns

#### Technical Deep Dives
- [Istio Configuration Guide](./docs/istio-configuration.md)
- [Envoy Proxy Patterns](./docs/envoy-patterns.md)  
- [mTLS Best Practices](./docs/mtls-best-practices.md)
- [Observability Setup](./docs/observability-setup.md)

### 🤝 Contributing

#### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd episode-007-service-mesh/code

# Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

#### Code Style
- Python: Black formatter + Flake8 linting
- Go: gofmt + golangci-lint
- Comments: Hindi context explanations welcome!

### 📞 Support

- **Issues**: Create GitHub issues with `[Episode 7]` prefix
- **Questions**: Join the Mumbai Tech Community Discord
- **Documentation**: Check `/docs` directory for detailed guides

### 🏷️ Tags

`#ServiceMesh` `#Istio` `#Envoy` `#Mumbai` `#Indian` `#Fintech` `#Production` `#Kubernetes` `#mTLS` `#Observability` `#Hindi` `#TrafficManagement`

---

## 🚀 Ready to Deploy Your Mumbai Service Mesh?

This codebase provides everything needed to build a production-grade service mesh inspired by Mumbai's efficient traffic management. Each component is designed with Indian context, supporting the scale and reliability requirements of services like Paytm and PhonePe.

**Start with**: `docker-compose up -d` and explore the Mumbai Digital Service Mesh! 🚂