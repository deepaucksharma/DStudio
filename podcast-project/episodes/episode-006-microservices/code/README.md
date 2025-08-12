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
```bash
# Python dependencies
pip install flask fastapi uvicorn aiohttp aioredis redis asyncio

# Go dependencies (for Go examples)
go mod tidy

# Java dependencies (for Java examples)
mvn install

# Docker for supporting services
docker run -d -p 6379:6379 redis
docker run -d -p 8500:8500 consul
docker run -d -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one:latest
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