# Episode 24: API Design Patterns - Code Examples

🇮🇳 **Hindi Tech Podcast Series - Production-Ready API Design Examples**

यह episode API Design patterns पर comprehensive code examples प्रदान करता है। सभी examples Indian e-commerce context में हैं।

## 📋 Examples Overview

### Python Examples

1. **`01_irctc_rest_api.py`** - IRCTC Train Booking REST API
   - Complete REST API implementation
   - Mumbai to Delhi train booking
   - Tatkal booking support
   - PNR status checking
   - Error handling और validation

2. **`02_flipkart_graphql_api.py`** - Flipkart GraphQL API
   - Product catalog GraphQL implementation
   - Flexible querying capabilities
   - Real-time subscriptions
   - Optimized data fetching

3. **`03_upi_grpc_service.py`** - UPI gRPC Payment Service
   - High-performance payment processing
   - Protocol Buffers implementation
   - Stream processing support
   - Bank integration simulation

4. **`09_kong_api_gateway.py`** - Kong API Gateway Configuration
   - Microservices routing
   - Rate limiting और authentication
   - Circuit breaker patterns
   - Load balancing strategies

5. **`10_api_monitoring_metrics.py`** - Comprehensive API Monitoring
   - Prometheus metrics integration
   - Real-time performance tracking
   - Alerting और notification system
   - Production-grade monitoring

6. **`11_oauth2_implementation.py`** - OAuth2 Server Implementation
   - Complete OAuth2 flow
   - JWT token management
   - Scope-based access control
   - Indian compliance (DPDP Act)

7. **`12_api_testing_framework.py`** - API Testing Framework
   - Automated testing suite
   - Performance benchmarking
   - Security testing
   - Load testing capabilities

### Java Examples

1. **`CircuitBreakerAPIClient.java`** - Circuit Breaker Pattern
   - Resilient API client implementation
   - Automatic failure detection
   - Fallback mechanisms
   - Health monitoring

### Go Examples

1. **`grpc_payment_service.go`** - gRPC Payment Service
   - UPI payment processing
   - Multi-bank integration
   - Fraud detection system
   - High-performance implementation

## 🚀 Quick Start

### Prerequisites

```bash
# Python dependencies
pip install flask fastapi redis requests jwt prometheus_client

# Java dependencies (Maven)
mvn clean install

# Go dependencies
go mod tidy
```

### Running Examples

#### Python Examples

```bash
# IRCTC REST API
cd python/
python 01_irctc_rest_api.py

# Access API at: http://localhost:8000
# Test endpoints:
# GET /api/v1/trains/search?source=Mumbai&destination=Delhi&journey_date=2025-01-15
# POST /api/v1/booking/create
```

#### Java Examples

```bash
# Circuit Breaker Pattern
cd java/
javac CircuitBreakerAPIClient.java
java CircuitBreakerAPIClient
```

#### Go Examples

```bash
# gRPC Payment Service
cd go/
go run grpc_payment_service.go
```

## 📊 API Design Patterns Covered

### 1. REST API Design
- **Example**: IRCTC Train Booking
- **Features**: Resource-based URLs, HTTP methods, Status codes
- **Best Practices**: Indian railway booking workflow

### 2. GraphQL Implementation
- **Example**: Flipkart Product Catalog
- **Features**: Flexible queries, Real-time subscriptions
- **Benefits**: Optimized data fetching, Single endpoint

### 3. gRPC Services
- **Example**: UPI Payment Processing
- **Features**: Protocol Buffers, Streaming, High performance
- **Use Cases**: Inter-service communication, Mobile apps

### 4. API Gateway Patterns
- **Example**: Kong Gateway Configuration
- **Features**: Routing, Authentication, Rate limiting
- **Benefits**: Centralized management, Security

### 5. Circuit Breaker Pattern
- **Example**: Resilient API Client
- **Features**: Failure detection, Fallback mechanisms
- **Benefits**: System stability, Graceful degradation

### 6. OAuth2 Authentication
- **Example**: E-commerce OAuth Server
- **Features**: Secure token-based auth, Scope management
- **Compliance**: DPDP Act compliance for Indian users

## 🔧 Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=api_design_demo

# JWT Configuration
JWT_SECRET=your-super-secure-secret-key
JWT_EXPIRY=3600

# API Gateway
KONG_ADMIN_URL=http://localhost:8001
```

### Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Test connection
redis-cli ping
```

### Database Setup

```bash
# PostgreSQL setup for production examples
sudo apt-get install postgresql
sudo -u postgres createdb api_design_demo

# MongoDB for product catalog
sudo apt-get install mongodb
mongod --dbpath /var/lib/mongodb
```

## 🧪 Testing

### Unit Tests

```bash
# Python tests
cd python/tests/
python -m pytest test_*.py -v

# Java tests
cd java/
mvn test

# Go tests
cd go/
go test ./...
```

### Integration Tests

```bash
# API Testing Framework
python 12_api_testing_framework.py

# Load Testing
# Uses built-in load testing capabilities
```

### Performance Benchmarks

```bash
# API Monitoring
python 10_api_monitoring_metrics.py

# Prometheus metrics available at:
# http://localhost:8090/metrics
```

## 📈 Performance Metrics

### Expected Performance (Single Instance)

| API Type | Requests/Second | Latency (p95) | Memory Usage |
|----------|----------------|---------------|--------------|
| REST API | 1,000+ RPS | < 100ms | 256MB |
| GraphQL | 800+ RPS | < 150ms | 512MB |
| gRPC | 5,000+ RPS | < 50ms | 128MB |

### Scaling Recommendations

- **Horizontal Scaling**: Use load balancers
- **Caching**: Redis for session data
- **Database**: Read replicas for scaling
- **Monitoring**: Prometheus + Grafana

## 🛡️ Security Features

### Authentication & Authorization
- JWT token-based authentication
- OAuth2 implementation
- Scope-based access control
- Rate limiting per user

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

### Indian Compliance
- DPDP Act 2023 compliance
- Data localization support
- Audit logging
- User consent management

## 🌍 Production Deployment

### Docker Deployment

```dockerfile
# Example Dockerfile for REST API
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "01_irctc_rest_api.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: irctc-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: irctc-api
  template:
    metadata:
      labels:
        app: irctc-api
    spec:
      containers:
      - name: irctc-api
        image: irctc-api:latest
        ports:
        - containerPort: 8000
```

### Monitoring Setup

```bash
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-metrics'
    static_configs:
      - targets: ['localhost:8090']
```

## 📚 Documentation

### API Documentation

All REST APIs include OpenAPI/Swagger documentation:

```bash
# Generate API docs
python -c "
from 01_irctc_rest_api import app
from flask import jsonify

@app.route('/docs')
def docs():
    return jsonify({'message': 'API Documentation', 'endpoints': [...]})
"
```

### Code Documentation

Each example includes comprehensive inline documentation:
- Hindi comments for key concepts
- Indian context explanations
- Production best practices
- Error handling strategies

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python
- Use Google Style Guide for Java
- Follow Go conventions for Go code
- Include Hindi comments for Indian context

### Testing Requirements
- Unit tests for all functions
- Integration tests for API endpoints
- Performance tests for scalability
- Security tests for vulnerabilities

## 📞 Support

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Solution: Start Redis server
   redis-server
   ```

2. **Port Already in Use**
   ```bash
   # Solution: Change port in configuration
   export API_PORT=8001
   ```

3. **Database Connection Issues**
   ```bash
   # Solution: Check database status
   sudo systemctl status postgresql
   ```

### Performance Tuning

1. **High Memory Usage**
   - Reduce cache size
   - Enable garbage collection
   - Use connection pooling

2. **High Latency**
   - Enable caching
   - Add database indexes
   - Use async processing

3. **Low Throughput**
   - Increase worker processes
   - Enable horizontal scaling
   - Optimize database queries

## 🎯 Learning Objectives

After studying these examples, you will understand:

1. **REST API Design**: Resource modeling, HTTP methods, Status codes
2. **GraphQL Benefits**: Flexible querying, Real-time updates
3. **gRPC Advantages**: High performance, Type safety, Streaming
4. **API Gateway Patterns**: Centralized management, Security
5. **Resilience Patterns**: Circuit breakers, Retries, Fallbacks
6. **Authentication**: OAuth2, JWT, Scope management
7. **Testing Strategies**: Unit, Integration, Performance testing
8. **Production Deployment**: Scaling, Monitoring, Security

## 🔗 Related Episodes

- **Episode 23**: Container Orchestration
- **Episode 25**: Caching Strategies  
- **Episode 26**: Database Sharding
- **Episode 27**: Load Balancing

---

**🇮🇳 Made with ❤️ for Indian Tech Community**

*This episode is part of the Hindi Tech Podcast series focused on production-ready system design patterns.*