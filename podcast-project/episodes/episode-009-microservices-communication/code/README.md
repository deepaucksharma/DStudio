# Episode 9: Microservices Communication Patterns

## Overview
This directory contains production-ready code examples for Episode 9 of the Hindi Tech Podcast series, focusing on advanced microservices communication patterns used in Indian tech companies.

## 🎯 Learning Objectives
- Master different microservices communication patterns
- Understand production-grade service-to-service communication
- Implement real-world examples from Indian companies (Paytm, Zomato, Ola, etc.)
- Learn advanced patterns like service mesh, event streaming, and GraphQL

## 📁 Code Structure

### Python Examples
- **01_grpc_paytm_wallet_service.py** - gRPC wallet service implementation
- **02_rest_api_zomato_ordering.py** - RESTful API for food ordering
- **03_graphql_flipkart_catalog.py** - GraphQL product catalog service
- **04_kafka_ola_ride_events.py** - Event streaming with Apache Kafka
- **05_websocket_swiggy_realtime.py** - Real-time order tracking with WebSockets
- **06_rabbitmq_irctc_booking.py** - Message queuing with RabbitMQ
- **07_service_mesh_istio_demo.py** - Service mesh implementation demo

### Go Examples
- **01_grpc_phonepe_payments.go** - High-performance gRPC payment service
- **02_http_bigbasket_catalog.go** - HTTP REST API with middleware

### Java Examples
- **01_SpringBoot_Myntra_Inventory.java** - Spring Boot microservice

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Go 1.19+
- Java 11+
- Docker (for infrastructure services)

### Python Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run individual examples
python python/01_grpc_paytm_wallet_service.py
python python/02_rest_api_zomato_ordering.py
```

### Go Setup
```bash
# Initialize Go module
go mod init microservices-demo

# Install dependencies
go mod tidy

# Run examples
go run go/01_grpc_phonepe_payments.go
go run go/02_http_bigbasket_catalog.go
```

### Java Setup
```bash
# Compile Java examples
javac -cp ".:libs/*" java/*.java

# Run examples
java -cp ".:libs/*" SpringBoot_Myntra_Inventory
```

## 🏗️ Infrastructure Setup

### Start Required Services
```bash
# Apache Kafka
docker run -p 9092:9092 apache/kafka

# RabbitMQ
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Redis (for caching)
docker run -p 6379:6379 redis:alpine

# Neo4j (for graph examples)
docker run -p 7474:7474 -p 7687:7687 neo4j:latest
```

## 📋 Example Descriptions

### 1. gRPC Services
**Files:** `01_grpc_paytm_wallet_service.py`, `01_grpc_phonepe_payments.go`

Production-grade gRPC implementations showing:
- Type-safe service definitions
- Streaming capabilities
- Error handling and timeouts
- Performance optimizations
- Hindi comments for better understanding

**Key Features:**
- UPI payment processing simulation
- Concurrent request handling
- Circuit breaker pattern
- Metrics collection

### 2. REST APIs
**Files:** `02_rest_api_zomato_ordering.py`, `02_http_bigbasket_catalog.go`

RESTful API implementations featuring:
- Proper HTTP status codes
- JWT authentication
- Input validation
- Rate limiting
- CORS support
- Pagination and filtering

**Indian Context:**
- Zomato-style food ordering
- BigBasket grocery catalog
- Indian payment methods
- Local address formats

### 3. GraphQL APIs
**Files:** `03_graphql_flipkart_catalog.py`

Advanced GraphQL implementation showing:
- Schema-first development
- Complex nested queries
- Real-time subscriptions
- Query optimization
- Type safety

**Features:**
- Flipkart product catalog simulation
- Dynamic pricing
- Inventory management
- Recommendation engine integration

### 4. Event Streaming
**Files:** `04_kafka_ola_ride_events.py`

Apache Kafka implementation for:
- Real-time event processing
- Ride booking workflow
- Event sourcing patterns
- Fault tolerance
- Scalable message processing

**Ola Ride Booking Flow:**
1. Ride request events
2. Driver assignment
3. Real-time location updates
4. Payment processing
5. Trip completion

### 5. Real-time Communication
**Files:** `05_websocket_swiggy_realtime.py`

WebSocket implementation for:
- Bidirectional communication
- Real-time order tracking
- Live chat support
- Connection management
- Scalable broadcasting

### 6. Message Queues
**Files:** `06_rabbitmq_irctc_booking.py`

RabbitMQ implementation showing:
- Work queues
- Topic exchanges
- Dead letter queues
- Message persistence
- Reliable delivery

**IRCTC Booking Simulation:**
- Seat availability checking
- Booking confirmation
- Waitlist management
- Payment processing

### 7. Service Mesh
**Files:** `07_service_mesh_istio_demo.py`

Advanced service mesh concepts:
- Traffic management
- Circuit breaker patterns
- Retry policies
- Canary deployments
- Distributed tracing
- Security policies

## 🎯 Production Considerations

### Performance Optimization
- Connection pooling
- Caching strategies
- Load balancing
- Compression
- Streaming responses

### Security
- Authentication and authorization
- Input validation and sanitization
- Rate limiting
- HTTPS/TLS encryption
- API security best practices

### Monitoring and Observability
- Structured logging
- Metrics collection
- Distributed tracing
- Health checks
- Error tracking

### Scalability
- Horizontal scaling patterns
- Database partitioning
- Caching layers
- CDN integration
- Auto-scaling configuration

## 📊 Performance Benchmarks

### gRPC vs REST API
- gRPC: 7x faster binary protocol
- 60% less bandwidth usage
- Built-in load balancing
- Streaming capabilities

### Message Queue Throughput
- Kafka: 1M+ messages/second
- RabbitMQ: 100K+ messages/second
- Redis Streams: 500K+ messages/second

### WebSocket Connections
- Single server: 10K+ concurrent connections
- With clustering: 100K+ connections
- Sub-millisecond latency

## 🧪 Testing

### Unit Tests
```bash
# Python tests
python -m pytest tests/

# Go tests
go test ./...

# Java tests
mvn test
```

### Integration Tests
```bash
# Start test infrastructure
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
python tests/integration_tests.py
```

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load tests
artillery run load_tests/api_load_test.yml
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check occupied ports
   netstat -tulpn | grep :8080
   
   # Kill process
   kill -9 <PID>
   ```

2. **Docker Container Issues**
   ```bash
   # Check container status
   docker ps -a
   
   # View logs
   docker logs <container_name>
   
   # Restart container
   docker restart <container_name>
   ```

3. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install <package_name>
   go get <package_name>
   ```

### Performance Tuning

1. **Database Connections**
   - Use connection pooling
   - Set appropriate timeout values
   - Monitor connection usage

2. **Memory Management**
   - Profile memory usage
   - Set appropriate heap sizes
   - Use streaming for large datasets

3. **Network Optimization**
   - Enable compression
   - Use CDN for static assets
   - Implement caching layers

## 📚 Additional Resources

### Documentation
- [gRPC Official Documentation](https://grpc.io/docs/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [GraphQL Specification](https://spec.graphql.org/)
- [Istio Service Mesh](https://istio.io/latest/docs/)

### Indian Tech Blogs
- [PayTM Engineering](https://blog.paytm.com/tagged/engineering)
- [Flipkart Tech](https://tech.flipkart.com/)
- [Ola Engineering](https://blog.olacabs.com/tagged/engineering)
- [Zomato Tech](https://www.zomato.com/blog/category/technology)

### Books
- "Microservices Patterns" by Chris Richardson
- "Building Event-Driven Microservices" by Adam Bellemare
- "gRPC Up and Running" by Kasun Indrasiri

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add Hindi comments
4. Include test cases
5. Submit pull request

## 📄 License

This code is provided for educational purposes. Please respect the terms and conditions.

---

**Note:** All examples are simplified for educational purposes. In production, additional security, monitoring, and error handling would be required.