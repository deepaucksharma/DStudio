# Event-Driven Architecture - Production-Ready Code Examples

Complete collection of 15+ production-ready code examples demonstrating Event-Driven Architecture patterns with Indian context (Flipkart, Paytm, Ola, etc.).

## 🎯 Overview

This repository contains comprehensive implementations of Event-Driven Architecture patterns used in real-world Indian applications:

- **Basic Event Publisher/Subscriber** (Python, Java, Go)
- **Apache Kafka Producer/Consumer** 
- **Event Sourcing with Event Store**
- **Saga Pattern for Distributed Transactions**
- **Dead Letter Queue Handling**
- **Event Schema Versioning**
- **Exactly-Once Delivery Guarantees**
- **Circuit Breaker for Event Processing**
- **CQRS Read/Write Model Separation**
- **Real-time Event Streaming with WebSockets**
- **Advanced Event Sourcing with Snapshots**
- **SAGA Orchestration for IRCTC Booking**
- **Event-Driven Microservices with Kafka**
- **Complex Event Processing (CEP)**
- **Indian Payment Event Systems**

## 📁 Repository Structure

```
episode-020-event-driven/
├── code/
│   ├── python/                    # Python implementations
│   │   ├── 01_basic_pubsub.py            # Basic Publisher/Subscriber
│   │   ├── 02_kafka_producer_consumer.py # Kafka Implementation
│   │   ├── 03_event_sourcing.py          # Event Sourcing Pattern
│   │   ├── 04_saga_pattern.py            # Saga Coordinator
│   │   ├── 05_dead_letter_queue.py       # DLQ Implementation
│   │   ├── 06_event_schema_versioning.py # Schema Evolution
│   │   ├── 07_exactly_once_delivery.py   # Exactly-Once Semantics
│   │   ├── 08_circuit_breaker.py         # Circuit Breaker Pattern
│   │   ├── 09_cqrs_pattern.py            # CQRS Implementation
│   │   ├── 10_websocket_streaming.py     # Real-time WebSocket Streaming
│   │   ├── 11_indian_payment_event_system.py # UPI Payment Event System
│   │   ├── 12_advanced_event_sourcing_snapshots.py # Event Sourcing with Snapshots
│   │   ├── 13_saga_orchestration_irctc_booking.py # SAGA Orchestration for IRCTC
│   │   ├── 14_kafka_microservices_zerodha_trading.py # Kafka Microservices
│   │   └── 15_complex_event_processing_mumbai_traffic.py # Complex Event Processing
│   ├── java/                      # Java implementations
│   │   ├── BasicPubSub.java              # Basic Publisher/Subscriber
│   │   └── KafkaOlaRideSystem.java       # Kafka PhonePe UPI System
│   ├── go/                        # Go implementations
│   │   └── 01_basic_pubsub.go            # Basic Publisher/Subscriber
│   └── tests/                     # Test files
├── quality/                       # Quality assurance files
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Java 11+ (for Java examples)**
   ```bash
   java --version
   ```

3. **Go 1.19+ (for Go examples)**
   ```bash
   go version
   ```

4. **Docker (for Kafka/Redis examples)**
   ```bash
   docker --version
   ```

### Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd episode-020-event-driven/code
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Java Dependencies (Maven)**
   ```bash
   # For Java examples, add to pom.xml:
   # - Apache Kafka Client
   # - Jackson JSON
   # - Lombok
   # - SLF4J Logging
   ```

4. **Go Dependencies**
   ```bash
   go mod init event-driven-examples
   go get github.com/google/uuid
   ```

## 🐳 Infrastructure Setup

### Apache Kafka Setup
```bash
# Start Zookeeper
docker run -d --name zookeeper -p 2181:2181 \
  -e ZOOKEEPER_CLIENT_PORT=2181 \
  confluentinc/cp-zookeeper:latest

# Start Kafka
docker run -d --name kafka -p 9092:9092 \
  --link zookeeper \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  confluentinc/cp-kafka:latest
```

### Redis Setup
```bash
# Start Redis for DLQ and Exactly-Once examples
docker run -d --name redis -p 6379:6379 redis:latest
```

### Database Setup (SQLite)
```bash
# SQLite databases are created automatically by the examples
# No separate setup required
```

## 📚 Example Details

### 1. Basic Event Publisher/Subscriber
**Files:** `python/01_basic_pubsub.py`, `java/BasicPubSub.java`, `go/01_basic_pubsub.go`

**Context:** Flipkart order processing with multiple services

**Features:**
- In-memory event bus implementation
- Async/sync handler support
- Event history tracking
- Error handling and retries

**Usage:**
```bash
# Python
python python/01_basic_pubsub.py

# Java
javac java/BasicPubSub.java && java BasicPubSub

# Go
go run go/01_basic_pubsub.go
```

**Key Learning:**
- Event-driven communication patterns
- Decoupling services through events
- Error handling in event systems

---

### 2. Apache Kafka Producer/Consumer
**Files:** `python/02_kafka_producer_consumer.py`, `java/KafkaOlaRideSystem.java`

**Context:** Ola ride booking and PhonePe UPI transactions

**Features:**
- Production-ready Kafka configuration
- Consumer groups and partitioning
- Error handling and retries
- Exactly-once semantics

**Prerequisites:**
- Kafka cluster running (see setup above)

**Usage:**
```bash
# Start Kafka first
# Then run examples:
python python/02_kafka_producer_consumer.py
```

**Key Learning:**
- Kafka producer/consumer patterns
- Partition key strategies
- Consumer group management
- At-least-once vs exactly-once delivery

---

### 3. Event Sourcing Implementation
**File:** `python/03_event_sourcing.py`

**Context:** Zerodha portfolio management with complete audit trail

**Features:**
- Immutable event store
- Event replay and reconstruction
- Point-in-time queries
- Snapshot optimization

**Usage:**
```bash
python python/03_event_sourcing.py
```

**Key Learning:**
- Event sourcing fundamentals
- Aggregate reconstruction
- Time-travel debugging
- Regulatory compliance through events

---

### 4. Saga Pattern Coordinator
**File:** `python/04_saga_pattern.py`

**Context:** BigBasket order processing with distributed transactions

**Features:**
- Orchestrator-based saga pattern
- Compensation actions
- Failure handling and rollback
- Step-by-step coordination

**Usage:**
```bash
python python/04_saga_pattern.py
```

**Key Learning:**
- Distributed transaction management
- Compensation patterns
- Long-running processes
- Failure recovery strategies

---

### 5. Dead Letter Queue Implementation
**File:** `python/05_dead_letter_queue.py`

**Context:** Swiggy notification delivery with retry logic

**Features:**
- Redis-based DLQ implementation
- Exponential backoff retry
- Manual intervention support
- Monitoring and alerting

**Prerequisites:**
- Redis running (see setup above)

**Usage:**
```bash
python python/05_dead_letter_queue.py
```

**Key Learning:**
- Message reliability patterns
- Retry strategies
- Dead letter queue management
- Monitoring failed messages

---

### 6. Event Schema Versioning
**File:** `python/06_event_schema_versioning.py`

**Context:** Paytm transaction events with evolving schemas

**Features:**
- Schema registry implementation
- Backward/forward compatibility
- Event transformation
- Version migration strategies

**Usage:**
```bash
python python/06_event_schema_versioning.py
```

**Key Learning:**
- Schema evolution strategies
- Compatibility patterns
- Event transformation
- Consumer migration

---

### 7. Exactly-Once Delivery
**File:** `python/07_exactly_once_delivery.py`

**Context:** HDFC bank fund transfers with duplicate prevention

**Features:**
- Idempotency key management
- Distributed locking
- Duplicate detection
- Transaction integrity

**Prerequisites:**
- Redis running (see setup above)

**Usage:**
```bash
python python/07_exactly_once_delivery.py
```

**Key Learning:**
- Idempotency patterns
- Distributed state management
- Duplicate prevention
- Financial transaction safety

---

### 8. Circuit Breaker Pattern
**File:** `python/08_circuit_breaker.py`

**Context:** BookMyShow ticket booking with service protection

**Features:**
- Circuit breaker state machine
- Failure threshold configuration
- Automatic recovery testing
- Fallback mechanisms

**Usage:**
```bash
python python/08_circuit_breaker.py
```

**Key Learning:**
- Fault tolerance patterns
- Cascade failure prevention
- Service resilience
- Graceful degradation

---

### 9. CQRS Implementation
**File:** `python/09_cqrs_pattern.py`

**Context:** Amazon India product catalog with read/write separation

**Features:**
- Command/query separation
- Event-driven synchronization
- Optimized read models
- Analytics capabilities

**Usage:**
```bash
python python/09_cqrs_pattern.py
```

**Key Learning:**
- Read/write model separation
- Event-driven projections
- Performance optimization
- Complex query support

---

### 10. WebSocket Event Streaming
**File:** `python/10_websocket_streaming.py`

**Context:** NSE stock exchange real-time price updates

**Features:**
- WebSocket server implementation
- Real-time event broadcasting
- Subscription management
- Market data simulation

**Usage:**
```bash
python python/10_websocket_streaming.py
```

**Key Learning:**
- Real-time communication
- WebSocket patterns
- Subscription management
- Live data streaming

## 🔧 Configuration

### Environment Variables
```bash
# Kafka Configuration
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis Configuration  
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Database Configuration
export DB_PATH=./data/

# Logging Level
export LOG_LEVEL=INFO
```

### Application Configuration
Most examples include configuration parameters that can be modified:

```python
# Example: Circuit Breaker Configuration
config = CircuitBreakerConfig(
    failure_threshold=5,      # Failures to trigger OPEN
    recovery_timeout=60,      # Seconds before HALF_OPEN
    success_threshold=3,      # Successes to CLOSE
    timeout_duration=10.0     # Request timeout
)
```

## 🧪 Testing

### Unit Tests
```bash
# Run all Python tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_basic_pubsub.py -v
```

### Integration Tests
```bash
# Start infrastructure first
docker-compose up -d

# Run integration tests
python -m pytest tests/integration/ -v
```

### Load Testing
```bash
# Example: Kafka load test
python tests/load/kafka_load_test.py --producers 10 --messages 10000
```

## 📊 Monitoring and Metrics

### Application Metrics
- Event processing rates
- Error rates and types
- Queue depths
- Response times

### Infrastructure Metrics
- Kafka consumer lag
- Redis memory usage
- Database performance
- WebSocket connections

### Logging
All examples include structured logging:
```python
logger.info("Event processed", extra={
    "event_id": event.event_id,
    "event_type": event.event_type,
    "processing_time_ms": processing_time
})
```

## 🚨 Production Considerations

### Security
- API authentication and authorization
- Event encryption for sensitive data
- Network security (VPCs, firewalls)
- Secret management for credentials

### Scalability
- Horizontal scaling of consumers
- Database sharding strategies
- Load balancing considerations
- Caching layers

### Reliability
- Multi-region deployment
- Backup and disaster recovery
- Health checks and monitoring
- Circuit breakers and timeouts

### Performance
- Batch processing optimizations
- Connection pooling
- Message compression
- Efficient serialization

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Issues**
   ```bash
   # Check Kafka status
   docker logs kafka
   
   # Verify connectivity
   telnet localhost 9092
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # View Redis logs
   docker logs redis
   ```

3. **WebSocket Connection Issues**
   ```bash
   # Check port availability
   netstat -tulpn | grep 8765
   
   # Test WebSocket connection
   wscat -c ws://localhost:8765
   ```

4. **High Memory Usage**
   ```bash
   # Monitor Python memory
   python -m memory_profiler example.py
   
   # Check database size
   du -sh *.db
   ```

### Performance Tuning

1. **Kafka Performance**
   ```properties
   # Producer settings
   batch.size=16384
   linger.ms=10
   compression.type=gzip
   
   # Consumer settings
   fetch.min.bytes=1024
   max.poll.records=500
   ```

2. **Database Performance**
   ```sql
   -- SQLite optimizations
   PRAGMA journal_mode=WAL;
   PRAGMA synchronous=NORMAL;
   PRAGMA cache_size=10000;
   ```

3. **Redis Performance**
   ```bash
   # Redis configuration
   maxmemory-policy allkeys-lru
   save 900 1
   ```

## 📖 Learning Path

### Beginner
1. Start with Basic PubSub (01)
2. Understand Event Sourcing (03)
3. Learn Circuit Breaker (08)

### Intermediate
4. Kafka Implementation (02)
5. Dead Letter Queue (05)
6. Schema Versioning (06)

### Advanced
7. Saga Pattern (04)
8. Exactly-Once Delivery (07)
9. CQRS Pattern (09)
10. WebSocket Streaming (10)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style
- Follow language-specific conventions
- Include comprehensive Hindi comments
- Add Indian context examples
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Additional Resources

### Books
- "Designing Event-Driven Systems" by Ben Stopford
- "Building Event-Driven Microservices" by Adam Bellemare
- "Microservices Patterns" by Chris Richardson

### Documentation
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Redis Documentation](https://redis.io/documentation)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)

### Indian Tech Blogs
- [Flipkart Engineering](https://blog.flipkart.tech/)
- [PayTM Engineering](https://blog.paytm.com/)
- [Ola Engineering](https://blog.olacabs.com/)

## 📞 Support

For questions and support:
- Create GitHub Issues for bugs
- Use Discussions for questions
- Join our Slack community
- Email: support@example.com

---

## 🎯 Success Metrics

After completing these examples, you should be able to:

✅ Design event-driven architectures for Indian scale applications  
✅ Implement reliable message processing with Kafka  
✅ Handle distributed transactions with Saga pattern  
✅ Build resilient systems with circuit breakers  
✅ Ensure exactly-once delivery semantics  
✅ Design evolving schemas for long-term compatibility  
✅ Implement real-time streaming applications  
✅ Monitor and troubleshoot event-driven systems  

---

**Happy Coding! 🚀**

*"Mumbai local train system से सीखें - हर station पर सही message, सही time पर पहुंचना जरूरी है!"*