# Episode 6: Microservices - Code Examples

## Complete Collection of 15+ Microservices Patterns with Indian Context

This directory contains comprehensive code examples demonstrating all major microservices patterns with Indian e-commerce scenarios and Mumbai-style metaphors.

## 📁 Directory Structure

```
code/
├── service-discovery/
│   ├── main.go                           # Consul-based service discovery (Go)
│   └── flipkart_product_discovery.py     # Flipkart-style product catalog discovery
├── api-gateway/
│   ├── kong_gateway.py                   # Production-ready API Gateway
│   └── ola_ride_gateway.py              # Ola-style ride matching routing
├── circuit-breaker/
│   ├── circuit_breaker.py               # Production circuit breaker library
│   └── zomato_restaurant_breaker.py     # Zomato restaurant service failures
├── saga-orchestrator/
│   ├── src/main/java/                   # Java Saga implementation
│   └── paytm_payment_saga.py           # PayTM payment flow orchestration
├── event-sourcing/
│   └── flipkart_order_events.py        # Order tracking with event sourcing
├── cqrs/
│   └── flipkart_inventory_cqrs.py       # Inventory management with CQRS
├── service-mesh/
│   └── istio_mumbai_mesh.yaml          # Istio service mesh configuration
├── distributed-tracing/
│   └── jaeger_order_tracing.go         # Jaeger distributed tracing (Go)
├── load-balancing/
│   └── mumbai_load_balancer.py         # Multiple load balancing algorithms
├── health-monitoring/
│   └── mumbai_health_monitor.py        # Comprehensive health monitoring
├── service-versioning/
│   └── api_versioning.py               # API versioning with backward compatibility
└── ecommerce-architecture/
    └── indian_ecommerce_microservices.py # Complete microservices platform
```

## 🚀 Examples Overview

### 1. Service Discovery (Consul/Eureka)
- **Files**: `service-discovery/main.go`, `service-discovery/flipkart_product_discovery.py`
- **Context**: Flipkart-style product catalog discovery
- **Features**: Consul integration, health checking, load balancing
- **Mumbai Metaphor**: जैसे Mumbai local train network में connectivity

### 2. API Gateway Implementation  
- **Files**: `api-gateway/kong_gateway.py`, `api-gateway/ola_ride_gateway.py`
- **Context**: Ola-style ride matching routing
- **Features**: Rate limiting, authentication, circuit breakers
- **Mumbai Metaphor**: जैसे Mumbai CST station का main entry point

### 3. Circuit Breaker Patterns
- **Files**: `circuit-breaker/circuit_breaker.py`, `circuit-breaker/zomato_restaurant_breaker.py`
- **Context**: Zomato restaurant service failures
- **Features**: Multiple failure detection strategies, fallback mechanisms
- **Mumbai Metaphor**: जैसे Mumbai power grid protection

### 4. Saga Orchestration
- **Files**: `saga-orchestrator/src/main/java/`, `saga-orchestrator/paytm_payment_saga.py`
- **Context**: PayTM payment flow examples
- **Features**: Distributed transactions, compensation patterns
- **Mumbai Metaphor**: जैसे Mumbai local train journey coordination

### 5. Event Sourcing
- **Files**: `event-sourcing/flipkart_order_events.py`
- **Context**: Complete order lifecycle tracking
- **Features**: Event store, aggregate reconstruction, replay capability
- **Mumbai Metaphor**: जैसे train journey की complete record keeping

### 6. CQRS Pattern
- **Files**: `cqrs/flipkart_inventory_cqrs.py`
- **Context**: Inventory management with separate read/write models
- **Features**: Command handlers, query projections, event sourcing integration
- **Mumbai Metaphor**: जैसे train ticket booking vs schedule checking

### 7. Service Mesh Basics
- **Files**: `service-mesh/istio_mumbai_mesh.yaml`
- **Context**: Istio configuration for Mumbai-scale services
- **Features**: Traffic management, security policies, observability
- **Mumbai Metaphor**: जैसे Mumbai transport network connectivity

### 8. Distributed Tracing
- **Files**: `distributed-tracing/jaeger_order_tracing.go`
- **Context**: Complete order flow tracing with Jaeger
- **Features**: Span creation, trace propagation, error tracking
- **Mumbai Metaphor**: जैसे train journey tracking across stations

### 9. Load Balancing Strategies
- **Files**: `load-balancing/mumbai_load_balancer.py`
- **Context**: High traffic scenarios with multiple algorithms
- **Features**: Round robin, weighted, geographic, consistent hashing
- **Mumbai Metaphor**: जैसे Mumbai traffic distribution

### 10. Health Checks and Monitoring
- **Files**: `health-monitoring/mumbai_health_monitor.py`
- **Context**: Comprehensive microservices health monitoring
- **Features**: Resource monitoring, dependency checks, alerting
- **Mumbai Metaphor**: जैसे Mumbai local train system monitoring

### 11. Service Versioning
- **Files**: `service-versioning/api_versioning.py`
- **Context**: API evolution with backward compatibility
- **Features**: Multiple versioning strategies, deprecation management
- **Mumbai Metaphor**: जैसे train route upgrades without disruption

### 12. Database per Service Pattern
- **Included in**: `ecommerce-architecture/indian_ecommerce_microservices.py`
- **Context**: Service-specific data ownership
- **Features**: Data consistency, transaction boundaries

### 13. API Composition
- **Included in**: `ecommerce-architecture/indian_ecommerce_microservices.py`
- **Context**: Aggregating data from multiple services
- **Features**: Response composition, error handling

### 14. Bulkhead Pattern
- **Included in**: Various examples (connection pools, resource isolation)
- **Context**: Resource isolation for fault containment
- **Features**: Resource partitioning, failure isolation

### 15. Complete Indian E-commerce Architecture
- **Files**: `ecommerce-architecture/indian_ecommerce_microservices.py`
- **Context**: End-to-end microservices platform
- **Features**: All patterns integrated, Indian market specifics
- **Mumbai Metaphor**: Complete Mumbai transport ecosystem

## 🇮🇳 Indian Market Features

All examples include Indian market specifics:

- **Payment Methods**: UPI, Wallet, Cards, COD, Net Banking
- **GST Integration**: Tax calculations and compliance
- **Regional Availability**: City and tier-based services
- **Multi-language**: Hindi and English support
- **Currency**: INR-based pricing
- **Indian Companies**: Flipkart, Ola, Zomato, PayTM examples

## 🏃 Running the Examples

### Prerequisites

#### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for complete setup)
- **CPU**: 4 cores minimum (8 cores for optimal performance)
- **Disk**: 20GB free space for Docker containers and logs
- **Network**: Stable internet for downloading dependencies

#### Software Prerequisites
```bash
# Python 3.8+ with virtual environment
python3 -m venv microservices_env
source microservices_env/bin/activate  # On Windows: microservices_env\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Go 1.19+ (for Go examples)
go version  # Verify Go installation

# Java 11+ and Maven (for Java examples)
java -version
mvn -version

# Docker and Docker Compose
docker --version
docker-compose --version
```

#### Infrastructure Setup
```bash
# Start supporting services (Redis, Consul, Jaeger)
docker-compose up -d

# Or start individually
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name consul -p 8500:8500 -p 8600:8600/udp consul:1.16
docker run -d --name jaeger -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one:latest

# Start monitoring stack
docker run -d --name prometheus -p 9090:9090 prom/prometheus
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Verify all services are running
docker ps | grep -E "(redis|consul|jaeger|prometheus|grafana)"
```

#### Indian Cloud Setup (Optional)
```bash
# AWS Mumbai region setup
export AWS_DEFAULT_REGION=ap-south-1
aws configure set region ap-south-1

# Google Cloud Mumbai region
gcloud config set compute/region asia-south1
gcloud config set compute/zone asia-south1-a

# Setup cost monitoring for Indian pricing
export CLOUD_PROVIDER=aws_mumbai
export CURRENCY=INR
export HOURLY_RATE=50  # ₹50/hour for medium instance
```

### Running Individual Examples
```bash
# Service Discovery
python service-discovery/flipkart_product_discovery.py demo

# API Gateway
python api-gateway/ola_ride_gateway.py

# Circuit Breaker
python circuit-breaker/zomato_restaurant_breaker.py

# Event Sourcing
python event-sourcing/flipkart_order_events.py

# CQRS Pattern
python cqrs/flipkart_inventory_cqrs.py

# Load Balancer
python load-balancing/mumbai_load_balancer.py

# Health Monitor
python health-monitoring/mumbai_health_monitor.py

# API Versioning
python service-versioning/api_versioning.py

# Complete Platform
python ecommerce-architecture/indian_ecommerce_microservices.py
```

### Running Go Examples
```bash
# Service Discovery
cd service-discovery && go run main.go

# Distributed Tracing
cd distributed-tracing && go run jaeger_order_tracing.go
```

### Running Java Examples
```bash
# Saga Orchestrator
cd saga-orchestrator && mvn spring-boot:run
```

## 📊 Key Patterns Demonstrated

1. **Service Discovery**: Dynamic service registration and lookup
2. **API Gateway**: Centralized routing and cross-cutting concerns
3. **Circuit Breaker**: Fault tolerance and cascade failure prevention
4. **Saga Pattern**: Distributed transaction management
5. **Event Sourcing**: Complete audit trail and state reconstruction
6. **CQRS**: Separate read/write models for optimal performance
7. **Service Mesh**: Service-to-service communication and security
8. **Distributed Tracing**: End-to-end request tracking
9. **Load Balancing**: Traffic distribution across service instances
10. **Health Monitoring**: Continuous service health assessment
11. **API Versioning**: Backward compatible API evolution
12. **Database per Service**: Service-specific data ownership
13. **API Composition**: Aggregating data from multiple services
14. **Bulkhead Pattern**: Resource isolation for fault containment
15. **Complete Architecture**: All patterns working together

## 🎯 Learning Outcomes

After running these examples, you'll understand:

- How to implement production-ready microservices patterns
- Indian market-specific considerations for e-commerce
- Mumbai-scale performance and reliability patterns
- Real-world integration challenges and solutions
- Complete microservices platform architecture
- Cost optimization strategies for Indian cloud providers
- Integration with Indian payment systems (UPI, Razorpay)
- Handling Indian language content in microservices
- Compliance requirements for Indian data regulations

## 📊 Performance Metrics & Indian Market Analysis

### Performance Benchmarks

#### API Gateway Performance
- **Kong Gateway**: 15,000 requests/sec (4-core instance)
- **Nginx**: 25,000 requests/sec (4-core instance)  
- **Envoy**: 20,000 requests/sec (4-core instance)
- **Latency**: P95 < 50ms for Mumbai-Chennai communication

#### Service Discovery
- **Consul**: 10,000 service registrations/sec
- **Eureka**: 8,000 service registrations/sec
- **Health Check Frequency**: Every 10 seconds
- **Service Lookup**: P99 < 5ms

#### Circuit Breaker Efficiency
- **Failure Detection**: < 1 second
- **Recovery Time**: 30-60 seconds (configurable)
- **False Positive Rate**: < 0.1%
- **Resource Savings**: 40-60% during downstream failures

### Indian Cloud Provider Costs (2024)

#### AWS Asia-Pacific (Mumbai)
```yaml
Compute Instances:
  t3.medium: ₹3.2/hour   # 2 vCPU, 4GB RAM
  t3.large:  ₹6.4/hour   # 2 vCPU, 8GB RAM
  c5.large:  ₹7.8/hour   # 2 vCPU, 4GB RAM (compute optimized)
  m5.large:  ₹8.1/hour   # 2 vCPU, 8GB RAM (balanced)

Managed Services:
  RDS MySQL: ₹12-25/hour (db.t3.medium to db.m5.large)
  ElastiCache Redis: ₹8-15/hour (cache.t3.micro to cache.m5.large)
  Load Balancer: ₹1,800/month (Application Load Balancer)
```

#### Google Cloud (Mumbai/Delhi)
```yaml
Compute Engine:
  n1-standard-2: ₹5.8/hour   # 2 vCPU, 7.5GB RAM
  n1-standard-4: ₹11.6/hour  # 4 vCPU, 15GB RAM
  c2-standard-4: ₹13.2/hour  # 4 vCPU, 16GB RAM (compute optimized)

Managed Services:
  Cloud SQL: ₹10-22/hour (db-n1-standard-1 to db-n1-standard-4)
  Memorystore Redis: ₹6-12/hour (1GB to 4GB)
  Load Balancer: ₹1,500/month
```

#### Microsoft Azure (Pune/Chennai)
```yaml
Virtual Machines:
  B2s: ₹4.5/hour      # 2 vCPU, 4GB RAM
  D2s_v3: ₹7.2/hour   # 2 vCPU, 8GB RAM
  F2s_v2: ₹6.8/hour   # 2 vCPU, 4GB RAM (compute optimized)

Managed Services:
  Azure Database: ₹14-28/hour (Basic to Standard)
  Redis Cache: ₹8-18/hour (C1 to C2)
  Application Gateway: ₹2,200/month
```

### Cost Optimization for Indian Startups

#### Small Scale (< 10,000 users/day)
```yaml
Monthly Cost: ₹15,000 - ₹25,000
Infrastructure:
  - 2x t3.medium (API services): ₹4,800
  - 1x Redis cache: ₹6,000
  - 1x RDS MySQL: ₹9,000
  - Load balancer: ₹1,800
  - Monitoring: ₹2,000
  - Network: ₹1,500
```

#### Medium Scale (100,000 users/day)
```yaml
Monthly Cost: ₹45,000 - ₹75,000
Infrastructure:
  - 4x c5.large (API services): ₹22,500
  - 2x Redis cluster: ₹12,000
  - 2x RDS MySQL (master-slave): ₹18,000
  - Application load balancer: ₹1,800
  - CloudWatch/monitoring: ₹5,000
  - CDN (CloudFront): ₹3,000
  - Network: ₹8,000
```

#### Large Scale (1M+ users/day - Flipkart/Ola level)
```yaml
Monthly Cost: ₹2,00,000 - ₹5,00,000
Infrastructure:
  - 20x m5.large (microservices): ₹1,20,000
  - ElastiCache cluster: ₹35,000
  - RDS Multi-AZ: ₹45,000
  - Multiple load balancers: ₹8,000
  - Advanced monitoring: ₹15,000
  - CDN + bandwidth: ₹25,000
  - Backup + disaster recovery: ₹18,000
```

### Indian Market Specific Considerations

#### Payment Integration Costs
- **Razorpay**: 2% transaction fee + ₹2 per transaction
- **PayU**: 1.9% transaction fee + ₹1.5 per transaction  
- **Paytm**: 1.8% transaction fee (for merchants)
- **UPI**: Free for consumers, ₹0.5-2 for merchants

#### Compliance Costs
- **Data Localization**: Additional ₹5,000-15,000/month for Indian data centers
- **RBI Guidelines**: Compliance monitoring ₹10,000-25,000/month
- **GST Integration**: Tax calculation service ₹2,000-5,000/month
- **Audit Requirements**: ₹50,000-1,00,000/year

#### Regional Performance Optimization
```yaml
Latency Benchmarks (from Mumbai):
  - Delhi: 25-35ms
  - Bangalore: 15-25ms  
  - Chennai: 35-45ms
  - Kolkata: 45-55ms
  - Hyderabad: 30-40ms

CDN Edge Locations:
  - Tier 1 cities: < 10ms
  - Tier 2 cities: 15-30ms
  - Tier 3 cities: 30-60ms
```

## 🚂 Mumbai-Style Philosophy

All examples follow the Mumbai transport philosophy:
- **Efficient**: Like Mumbai Dabbawalas' delivery system
- **Resilient**: Like local trains during monsoon
- **Scalable**: Like Mumbai's growing Metro network  
- **Reliable**: Like the punctual suburban railway
- **Practical**: Like Mumbai's jugaad solutions

---

**Total Code Examples**: 15+ comprehensive implementations
**Languages Used**: Python, Java, Go, YAML
**Lines of Code**: 8000+ with extensive Hindi comments
**Indian Context**: 100% examples with local scenarios
**Production Ready**: All patterns include error handling, monitoring, and scalability considerations