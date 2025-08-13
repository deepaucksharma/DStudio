# Episode 50: System Design Interview Mastery

## 🎯 Production-Ready System Design Examples with Indian Context

Welcome to the comprehensive code repository for Episode 50 of the Hindi Tech Podcast Series. This episode covers essential system design patterns and implementations with real-world Indian examples like IRCTC, Paytm, Flipkart, Ola, and Zomato.

## 📚 What You'll Learn

This repository contains 15+ production-ready code examples demonstrating key system design concepts:

- **Load Balancing** - Mumbai Railway traffic management
- **Distributed Caching** - Flipkart product cache with LRU eviction  
- **Rate Limiting** - UPI transaction controls with RBI compliance
- **Database Connection Pooling** - IRCTC booking system optimization
- **Database Sharding** - Indian phone number and geographic partitioning
- **Circuit Breaker Pattern** - Payment gateway failure protection
- **Retry Mechanisms** - Exponential backoff for API resilience
- **Distributed Locking** - Zomato restaurant table booking
- **Time-Series Database** - Ola cab metrics with IST timezone

## 🗂️ Repository Structure

```
episode-050-system-design-interviews/
├── code/
│   ├── python/                           # Python implementations
│   │   ├── 01_load_balancer_implementation.py
│   │   ├── 04_message_queue_implementation.py  
│   │   ├── 07_service_discovery_system.py
│   │   ├── 09_notification_system.py
│   │   ├── 10_rate_limiter_system.py
│   │   ├── 11_distributed_cache_lru.py
│   │   ├── 12_database_connection_pool.py
│   │   ├── 13_sharding_system_india.py
│   │   ├── 14_circuit_breaker_pattern.py
│   │   ├── 15_retry_exponential_backoff.py
│   │   ├── 16_distributed_lock_manager.py
│   │   └── 17_time_series_database_ist.py
│   ├── java/                            # Java implementations
│   │   ├── 02_ConsistentHashingAlgorithm.java
│   │   ├── 05_DatabaseShardingSystem.java
│   │   └── 08_URLShortenerService.java
│   ├── go/                              # Go implementations
│   │   ├── 03_distributed_cache_system.go
│   │   └── 06_rate_limiting_framework.go
│   ├── requirements.txt                 # Python dependencies
│   └── README.md                        # This file
└── script/                              # Episode script and notes
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Redis (for distributed examples)
- PostgreSQL (for database examples)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd episode-050-system-design-interviews/code
   ```

2. **Set up Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up IST timezone (for time-series examples):**
   ```bash
   export TZ=Asia/Kolkata
   ```

### Running Examples

Each Python file is self-contained and can be run independently:

```bash
# Load Balancer Example
python python/01_load_balancer_implementation.py

# Rate Limiter Example  
python python/10_rate_limiter_system.py

# Distributed Cache Example
python python/11_distributed_cache_lru.py

# Database Connection Pool Example
python python/12_database_connection_pool.py

# Sharding System Example
python python/13_sharding_system_india.py

# Circuit Breaker Example
python python/14_circuit_breaker_pattern.py

# Retry Mechanism Example
python python/15_retry_exponential_backoff.py

# Distributed Lock Manager Example
python python/16_distributed_lock_manager.py

# Time-Series Database Example
python python/17_time_series_database_ist.py
```

## 📋 Detailed Examples Overview

### 1. Load Balancer Implementation (01_load_balancer_implementation.py)
**Context**: Mumbai Railway Station Platform Management
- **Strategies**: Round Robin, Weighted Round Robin, Least Connections, Consistent Hashing
- **Features**: Health checking, automatic failover, metrics collection
- **Indian Example**: CST to Andheri train route load distribution

**Key Concepts Demonstrated:**
- Multiple load balancing algorithms
- Health check mechanisms
- Mumbai railway metaphors for traffic distribution
- Real-time platform status monitoring

### 2. Rate Limiter System (10_rate_limiter_system.py)
**Context**: UPI Transaction Rate Limiting (RBI Compliant)
- **Algorithms**: Token Bucket, Sliding Window, Fixed Window
- **Features**: Per-user limits, burst handling, RBI compliance
- **Indian Example**: Daily UPI transaction limits (₹1,00,000 individual)

**Key Concepts Demonstrated:**
- Token bucket algorithm with refill rates
- Sliding window counters for precise limiting
- Indian UPI payment limits and regulations
- High-throughput rate limiting

### 3. Distributed Cache with LRU (11_distributed_cache_lru.py)
**Context**: Flipkart Product Cache System
- **Features**: LRU eviction, consistent hashing, memory management
- **Distribution**: Regional cache nodes across Indian cities
- **Indian Example**: Product caching for Big Billion Day sale

**Key Concepts Demonstrated:**
- LRU (Least Recently Used) eviction policy
- Consistent hash ring for cache distribution
- Memory-based eviction policies
- Regional data distribution across India

### 4. Database Connection Pooling (12_database_connection_pool.py)
**Context**: IRCTC Database Connection Management
- **Features**: Connection lifecycle, health validation, pool sizing
- **Databases**: PostgreSQL, MySQL, MongoDB support
- **Indian Example**: Tatkal booking system optimization

**Key Concepts Demonstrated:**
- Connection pool sizing strategies
- Connection validation and cleanup
- Multi-database connection management
- High-concurrency connection handling

### 5. Database Sharding (13_sharding_system_india.py)
**Context**: Paytm User Data Sharding
- **Strategies**: Phone number sharding, geographic sharding
- **Features**: Indian phone number validation, regional distribution
- **Indian Example**: Shard by mobile number prefixes and Indian states

**Key Concepts Demonstrated:**
- Phone number-based sharding logic
- Indian geographic region mapping
- Consistent shard key generation
- Cross-shard query optimization

### 6. Circuit Breaker Pattern (14_circuit_breaker_pattern.py)
**Context**: IRCTC Payment Gateway Protection
- **States**: CLOSED, OPEN, HALF_OPEN transitions
- **Features**: Failure detection, auto-recovery, fallback mechanisms
- **Indian Example**: Multiple payment gateway failover (HDFC, SBI, UPI)

**Key Concepts Demonstrated:**
- State machine implementation
- Failure threshold monitoring
- Automatic recovery mechanisms
- Multi-service fallback strategies

### 7. Retry with Exponential Backoff (15_retry_exponential_backoff.py)
**Context**: Flipkart Order Processing Resilience
- **Strategies**: Exponential, Linear, Fibonacci, Jittered backoff
- **Features**: Configurable retry policies, failure classification
- **Indian Example**: Order processing pipeline with inventory, payment, shipping

**Key Concepts Demonstrated:**
- Multiple backoff algorithms
- Retry condition classification
- Decorator pattern for easy integration
- High-load retry scenarios

### 8. Distributed Lock Manager (16_distributed_lock_manager.py)
**Context**: Zomato Restaurant Table Booking
- **Lock Types**: Exclusive, Shared, Reentrant locks
- **Features**: Lease-based expiration, context managers, deadlock prevention
- **Indian Example**: Mumbai restaurant table reservation system

**Key Concepts Demonstrated:**
- Distributed locking algorithms
- Lock lease management
- Context manager integration
- High-concurrency booking scenarios

### 9. Time-Series Database (17_time_series_database_ist.py)
**Context**: Ola Cab Ride Metrics Collection
- **Features**: IST timezone support, data aggregation, retention policies
- **Aggregations**: Sum, Average, Min, Max, Percentiles
- **Indian Example**: Real-time cab metrics across Indian cities

**Key Concepts Demonstrated:**
- Time-series data organization
- IST (Indian Standard Time) handling
- Peak hour analysis patterns
- High-throughput metrics ingestion

## 🇮🇳 Indian Context Features

All examples include authentic Indian context:

### Geographic Context
- **Cities**: Mumbai, Delhi, Bangalore, Chennai, Kolkata, Pune, Hyderabad
- **Regions**: North, South, East, West, Northeast, Central India
- **Locations**: Specific areas like BKC Mumbai, Koregaon Park Pune

### Business Context
- **Companies**: IRCTC, Paytm, Flipkart, Ola, Zomato, PhonePe, GPay
- **Services**: UPI payments, railway booking, food delivery, cab rides
- **Regulations**: RBI payment limits, Indian banking compliance

### Cultural Context
- **Language**: Hindi comments and explanations (Roman script)
- **Metaphors**: Mumbai local trains, dabbawalas, street vendors
- **Examples**: Diwali sale traffic, Tatkal booking rush, monsoon patterns

### Technical Context
- **Phone Numbers**: Indian mobile number validation (+91 format)
- **Currency**: INR (Indian Rupees) calculations
- **Timezone**: IST (Indian Standard Time) handling
- **Data**: Indian PIN codes, state mappings, regional patterns

## 🛠️ Advanced Setup

### Redis Configuration (for distributed examples)
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
brew install redis                  # macOS

# Start Redis
redis-server

# Test connection
redis-cli ping
```

### PostgreSQL Configuration (for database examples)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu
brew install postgresql                              # macOS

# Create database
sudo -u postgres createdb irctc_demo

# Test connection
psql -U postgres -d irctc_demo -c "SELECT version();"
```

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=irctc_demo
DB_USER=postgres
DB_PASSWORD=your_password

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379

# Indian Context
TIMEZONE=Asia/Kolkata
CURRENCY=INR
COUNTRY_CODE=IN
EOF
```

## 🧪 Testing

Run individual tests for each component:

```bash
# Test Load Balancer
python -c "
import python.load_balancer_implementation as lb
print('Testing Load Balancer...')
# Run load balancer demo
"

# Test Rate Limiter
python -c "
import python.rate_limiter_system as rl
print('Testing Rate Limiter...')
# Run rate limiter demo
"

# Test all examples
for file in python/*.py; do
    echo "Testing $(basename $file)..."
    python "$file"
done
```

## 📊 Performance Benchmarks

Expected performance characteristics on modern hardware:

| Component | Throughput | Latency | Memory |
|-----------|------------|---------|--------|
| Load Balancer | 50K+ req/sec | <1ms | <100MB |
| Rate Limiter | 100K+ req/sec | <0.5ms | <50MB |
| Distributed Cache | 200K+ ops/sec | <0.1ms | Configurable |
| Connection Pool | 10K+ conn/sec | <10ms | <200MB |
| Circuit Breaker | 80K+ req/sec | <0.5ms | <20MB |
| Retry Mechanism | 30K+ retry/sec | Variable | <10MB |
| Distributed Lock | 20K+ lock/sec | <5ms | <50MB |
| Time-Series DB | 500K+ points/sec | <1ms | Configurable |

## 🐳 Docker Support

Run examples in containerized environment:

```bash
# Build Docker image
docker build -t system-design-examples .

# Run with Redis and PostgreSQL
docker-compose up -d

# Run specific example
docker run --rm system-design-examples python python/10_rate_limiter_system.py
```

Sample docker-compose.yml:
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: irctc_demo
      POSTGRES_USER: postgres  
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
  
  app:
    build: .
    depends_on:
      - redis
      - postgres
    environment:
      - TZ=Asia/Kolkata
```

## 🔧 Configuration

### Load Balancer Configuration
```python
load_balancer_config = {
    'strategy': 'weighted_round_robin',
    'health_check_interval': 30,
    'failure_threshold': 3,
    'recovery_time': 60
}
```

### Rate Limiter Configuration
```python
rate_limit_config = {
    'individual_daily_limit': 1000000,  # ₹10 lakh
    'merchant_daily_limit': 50000000,   # ₹5 crore
    'window_size': 86400,               # 24 hours
    'strategy': 'sliding_window'
}
```

### Cache Configuration
```python
cache_config = {
    'max_size': 10000,
    'max_memory_mb': 100,
    'eviction_policy': 'lru',
    'ttl_seconds': 3600
}
```

## 📈 Monitoring and Observability

All examples include comprehensive monitoring:

### Metrics Collected
- **Throughput**: Requests/operations per second
- **Latency**: P50, P95, P99 response times
- **Error Rates**: Success/failure ratios
- **Resource Usage**: Memory, CPU, connections
- **Business Metrics**: UPI limits, booking success rates

### Logging
- **Structured Logging**: JSON format with IST timestamps
- **Correlation IDs**: Request tracing across components
- **Indian Context**: Hindi explanations in logs
- **Error Categories**: Transient vs permanent failures

### Alerting
- **Health Checks**: Component availability monitoring
- **Threshold Alerts**: Performance degradation detection
- **Business Alerts**: UPI limit violations, booking failures
- **Recovery Notifications**: Service restoration alerts

## 🚀 Production Deployment

### Performance Tuning
- **Connection Pools**: Size based on expected load
- **Cache Sizing**: Memory allocation per service
- **Rate Limits**: Aligned with business requirements
- **Retry Policies**: Optimized for upstream SLAs

### Security Considerations
- **Input Validation**: Phone numbers, currencies, timestamps
- **Rate Limiting**: DDoS protection and abuse prevention
- **Data Encryption**: Sensitive Indian payment data
- **Audit Logging**: Regulatory compliance tracking

### Scalability Patterns
- **Horizontal Scaling**: Multi-instance deployment
- **Database Sharding**: Geographic and functional partitioning
- **Cache Distribution**: Regional cache placement
- **Load Balancing**: Cross-region failover

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. **Indian Context**: Include authentic Indian examples
2. **Code Quality**: Follow PEP 8 and include type hints
3. **Documentation**: Hindi comments for concept explanation
4. **Testing**: Include unit tests and integration tests
5. **Performance**: Benchmark against expected throughput

### Code Style
```python
# Good: Hindi explanation with Indian context
def validate_indian_phone(phone_number: str) -> bool:
    """
    Indian mobile number validate करना - +91 format check
    Mumbai की sabse zyada phone numbers validate करते हैं
    """
    pass

# Bad: Generic implementation without context
def validate_phone(phone: str) -> bool:
    pass
```

## 📚 Additional Resources

### Learning Path
1. **System Design Basics**: Start with load balancer example
2. **Distributed Systems**: Progress to cache and sharding
3. **Resilience Patterns**: Circuit breaker and retry mechanisms
4. **Performance**: Connection pooling and rate limiting
5. **Advanced Topics**: Distributed locking and time-series

### Reference Architecture
- **IRCTC-like System**: High-load booking platform
- **Paytm-like Payments**: UPI transaction processing
- **Flipkart-like E-commerce**: Product catalog and ordering
- **Ola-like Rides**: Real-time location and matching
- **Zomato-like Food**: Restaurant and delivery management

### Books and Papers
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu
- "Building Microservices" by Sam Newman
- Google SRE Book and SRE Workbook
- Papers on consistent hashing, gossip protocols, consensus

## 🐛 Troubleshooting

### Common Issues

**Redis Connection Failed:**
```bash
# Check Redis status
redis-cli ping
# Should return PONG

# Start Redis if stopped
redis-server /usr/local/etc/redis/redis.conf
```

**PostgreSQL Connection Failed:**
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Create database if missing
createdb irctc_demo
```

**Python Import Errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

**IST Timezone Issues:**
```bash
# Set timezone environment variable
export TZ=Asia/Kolkata

# Verify timezone
python -c "import time; print(time.tzname)"
```

### Performance Issues

**High Memory Usage:**
- Reduce cache sizes in configuration
- Enable memory limits on connection pools
- Use data sampling for large datasets

**Slow Response Times:**
- Check database connection pool sizes
- Verify Redis connectivity and latency
- Enable connection reuse

**Rate Limit Errors:**
- Review rate limit configurations
- Check for burst traffic patterns
- Implement jittered backoff

## 📄 License

This code is part of the Hindi Tech Podcast Series educational content. Feel free to use for learning and development purposes.

## 📞 Support

For questions or issues:
- Create GitHub issues for bugs
- Discussion forum for architecture questions
- Follow Hindi Tech Podcast for updates

---

## 🎉 Happy System Designing!

These examples demonstrate production-ready implementations of essential system design patterns with authentic Indian context. Each example is designed to be educational while showcasing real-world complexity and considerations.

Whether you're preparing for system design interviews at Indian tech companies or building scalable systems for the Indian market, these examples provide practical starting points with culturally relevant context.

**Remember**: System design is about trade-offs. Understanding the business context (Indian regulations, user patterns, infrastructure constraints) is as important as technical implementation.

Good luck with your system design journey! 🚀

---

*Last Updated: January 2025*  
*Episode 50 - Hindi Tech Podcast Series*  
*Theme: System Design Interview Mastery*