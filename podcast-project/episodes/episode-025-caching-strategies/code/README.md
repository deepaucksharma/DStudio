# Episode 25: Caching Strategies - Code Examples

🇮🇳 **Hindi Tech Podcast Series - Production-Ready Caching Implementations**

यह episode comprehensive caching strategies पर detailed code examples प्रदान करता है। सभी examples Indian e-commerce और banking context में हैं।

## 📋 Examples Overview

### Python Examples

1. **`01_flipkart_redis_cache.py`** - Multi-Tier Redis Caching System
   - L1 (CPU) + L2 (Redis) caching hierarchy
   - Cache warming for Big Billion Day
   - Product catalog caching
   - Shopping cart persistence
   - Cache promotion strategies

2. **`02_irctc_memcached_availability.py`** - IRCTC Memcached Implementation
   - High-availability ticket booking
   - Distributed caching setup
   - Real-time availability tracking
   - Mumbai-Delhi route optimization

3. **`03_hotstar_cdn_video_delivery.py`** - CDN Video Delivery System
   - Multi-tier CDN caching
   - Video content optimization
   - Geographic distribution
   - Edge server management

4. **`04_write_through_cache.py`** - Write-Through Cache Pattern
   - Banking transaction caching
   - ACID compliance with caching
   - Consistent write operations
   - HDFC Bank simulation

5. **`05_write_behind_cache.py`** - Write-Behind Cache Pattern
   - High-throughput analytics caching
   - Async database writes
   - User behavior tracking
   - Flipkart analytics simulation

6. **`06_multi_level_cache_hierarchy.py`** - 4-Tier Cache Hierarchy
   - L1: CPU Cache (1ms)
   - L2: Local Redis (5ms)
   - L3: Distributed Redis (20ms)
   - L4: CDN Cache (50ms)
   - Automatic cache promotion

### Java Examples

1. **`CacheAsidePattern.java`** - Cache-Aside Implementation
   - HDFC Bank account caching
   - LRU cache with TTL
   - Thread-safe operations
   - Cache statistics monitoring

### Go Examples

1. **`distributed_cache_cluster.go`** - Distributed Cache Cluster
   - Redis Cluster simulation
   - Consistent hashing
   - Multi-region setup (Mumbai-Delhi-Bangalore)
   - Automatic failover
   - Geo-distributed caching

## 🚀 Quick Start

### Prerequisites

```bash
# Python dependencies
pip install redis memcached pymemcache flask sqlite3

# Java dependencies
# Requires Java 11+ and Maven

# Go dependencies
go mod init caching-strategies
go mod tidy

# Redis installation
sudo apt-get install redis-server

# Memcached installation
sudo apt-get install memcached
```

### Running Examples

#### Python Examples

```bash
# Multi-tier Redis caching
cd python/
python 01_flipkart_redis_cache.py

# Write-through cache pattern
python 04_write_through_cache.py

# Write-behind cache pattern
python 05_write_behind_cache.py

# Multi-level cache hierarchy
python 06_multi_level_cache_hierarchy.py
```

#### Java Examples

```bash
# Cache-aside pattern
cd java/
javac CacheAsidePattern.java
java CacheAsidePattern
```

#### Go Examples

```bash
# Distributed cache cluster
cd go/
go run distributed_cache_cluster.go
```

## 🔧 Cache Patterns Implemented

### 1. Cache-Aside Pattern
- **Example**: HDFC Bank Account Caching
- **Use Case**: Read-heavy workloads
- **Benefits**: Simple implementation, application controls cache
- **Drawbacks**: Potential cache inconsistency

### 2. Write-Through Cache
- **Example**: Banking Transaction System
- **Use Case**: Strong consistency requirements
- **Benefits**: Data consistency guaranteed
- **Drawbacks**: Higher write latency

### 3. Write-Behind (Write-Back) Cache
- **Example**: User Analytics System
- **Use Case**: High write throughput
- **Benefits**: Low write latency, high performance
- **Drawbacks**: Risk of data loss, eventual consistency

### 4. Multi-Level Cache Hierarchy
- **Example**: Product Catalog System
- **Use Case**: Varying latency requirements
- **Benefits**: Optimal performance per cost
- **Drawbacks**: Complex cache management

### 5. Distributed Cache
- **Example**: Multi-Region E-commerce
- **Use Case**: Large-scale applications
- **Benefits**: High availability, scalability
- **Drawbacks**: Network latency, complexity

## 📊 Performance Benchmarks

### Cache Hit Ratios (Expected)

| Cache Type | Hit Ratio | Latency | Use Case |
|------------|-----------|---------|----------|
| L1 (CPU) | 60-80% | <1ms | Hot data |
| L2 (Local Redis) | 70-90% | 1-5ms | Warm data |
| L3 (Distributed) | 80-95% | 10-50ms | Cold data |
| L4 (CDN) | 85-99% | 50-200ms | Static content |

### Throughput Comparison

| Pattern | Reads/sec | Writes/sec | Memory Usage |
|---------|-----------|------------|--------------|
| Cache-Aside | 10,000+ | 5,000+ | 512MB |
| Write-Through | 8,000+ | 3,000+ | 256MB |
| Write-Behind | 15,000+ | 10,000+ | 1GB |
| Multi-Level | 20,000+ | 8,000+ | 2GB |

## 🔧 Configuration

### Redis Configuration

```bash
# redis.conf optimizations for Indian e-commerce
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# For Mumbai data center
bind 0.0.0.0
port 6379
timeout 300
```

### Memcached Configuration

```bash
# memcached settings
-m 1024    # 1GB memory
-p 11211   # port
-l 0.0.0.0 # listen on all interfaces
-c 1024    # max connections
```

### Environment Variables

```bash
# Cache Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password

MEMCACHED_HOST=localhost
MEMCACHED_PORT=11211

# TTL Settings (seconds)
PRODUCT_TTL=3600        # 1 hour
SEARCH_TTL=1800         # 30 minutes
USER_SESSION_TTL=86400  # 24 hours
CART_TTL=604800         # 7 days

# Multi-region setup
MUMBAI_REDIS=mumbai-redis:6379
DELHI_REDIS=delhi-redis:6379
BANGALORE_REDIS=bangalore-redis:6379
```

## 🧪 Testing

### Unit Tests

```bash
# Python tests
cd python/tests/
python -m pytest test_caching_strategies.py -v

# Java tests
cd java/
mvn test

# Go tests
cd go/
go test ./...
```

### Performance Tests

```bash
# Cache performance testing
python test_cache_performance.py

# Load testing with concurrent users
python load_test_cache.py --users=100 --duration=300
```

### Integration Tests

```bash
# Redis cluster testing
python test_redis_cluster.py

# Failover testing
python test_cache_failover.py
```

## 📈 Monitoring and Metrics

### Redis Monitoring

```bash
# Redis info
redis-cli info memory
redis-cli info stats
redis-cli info replication

# Key patterns
redis-cli --scan --pattern "flipkart:product:*" | wc -l
redis-cli --scan --pattern "user:cart:*" | wc -l
```

### Application Metrics

```python
# Prometheus metrics collection
from prometheus_client import Counter, Histogram, Gauge

cache_hits = Counter('cache_hits_total', 'Cache hits', ['cache_level'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['cache_level'])
cache_latency = Histogram('cache_latency_seconds', 'Cache operation latency')
cache_size = Gauge('cache_size_bytes', 'Cache size in bytes', ['cache_level'])
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
- name: cache_alerts
  rules:
  - alert: CacheHitRatioLow
    expr: cache_hits_total / (cache_hits_total + cache_misses_total) < 0.8
    for: 5m
    annotations:
      summary: "Cache hit ratio is below 80%"
      
  - alert: CacheLatencyHigh
    expr: cache_latency_seconds > 0.1
    for: 2m
    annotations:
      summary: "Cache latency is above 100ms"
```

## 🛡️ Security Considerations

### Redis Security

```bash
# Enable authentication
requirepass your-strong-password

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""

# Network security
bind 127.0.0.1 10.0.0.1
port 6379
protected-mode yes
```

### Data Encryption

```python
# Encrypt sensitive cache data
import json
from cryptography.fernet import Fernet

def encrypt_cache_value(value, key):
    f = Fernet(key)
    return f.encrypt(json.dumps(value).encode())

def decrypt_cache_value(encrypted_value, key):
    f = Fernet(key)
    return json.loads(f.decrypt(encrypted_value).decode())
```

## 🌍 Multi-Region Setup

### Geographic Distribution

```yaml
# Mumbai Data Center
mumbai_cache:
  redis_cluster:
    nodes:
      - mumbai-redis-1:6379
      - mumbai-redis-2:6379
      - mumbai-redis-3:6379
  latency_target: 1ms
  
# Delhi Data Center  
delhi_cache:
  redis_cluster:
    nodes:
      - delhi-redis-1:6379
      - delhi-redis-2:6379
      - delhi-redis-3:6379
  latency_target: 5ms

# Bangalore Data Center
bangalore_cache:
  redis_cluster:
    nodes:
      - bangalore-redis-1:6379
      - bangalore-redis-2:6379
      - bangalore-redis-3:6379
  latency_target: 3ms
```

### Data Locality Strategy

```python
# Route requests to nearest cache
def get_nearest_cache(user_location):
    cache_locations = {
        'mumbai': mumbai_cache,
        'delhi': delhi_cache,
        'bangalore': bangalore_cache
    }
    
    # Find nearest cache based on user location
    return cache_locations.get(user_location.lower(), mumbai_cache)
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
# Redis Cache Dockerfile
FROM redis:7-alpine

COPY redis.conf /usr/local/etc/redis/redis.conf
COPY scripts/ /usr/local/bin/

EXPOSE 6379
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cache
spec:
  serviceName: redis-cache
  replicas: 3
  selector:
    matchLabels:
      app: redis-cache
  template:
    metadata:
      labels:
        app: redis-cache
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

### High Availability Setup

```bash
# Redis Sentinel for HA
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 60000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1
```

## 📚 Best Practices

### Cache Key Design

```python
# Good key naming conventions
def generate_cache_key(entity_type, entity_id, version=None):
    key = f"flipkart:{entity_type}:{entity_id}"
    if version:
        key += f":v{version}"
    return key

# Examples:
# flipkart:product:MOBILE123:v1
# flipkart:user:USER456:cart
# flipkart:search:smartphones:page:1
```

### TTL Strategy

```python
# Dynamic TTL based on data type
TTL_STRATEGIES = {
    'product': 3600,        # 1 hour - moderate updates
    'price': 300,           # 5 minutes - frequent updates
    'inventory': 60,        # 1 minute - real-time data
    'user_profile': 86400,  # 24 hours - infrequent updates
    'search_results': 1800, # 30 minutes - balanced
}
```

### Cache Invalidation

```python
# Tag-based invalidation
def invalidate_by_tags(tags):
    for tag in tags:
        pattern = f"*:tag:{tag}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)

# Example usage:
# Cache key: flipkart:product:MOBILE123:tag:electronics:tag:smartphone
# Invalidate all electronics: invalidate_by_tags(['electronics'])
```

## 🔗 Related Topics

- **Episode 24**: API Design Patterns
- **Episode 26**: Database Sharding
- **Episode 27**: Load Balancing
- **Episode 28**: Security Architecture

## 🎯 Learning Objectives

After studying these examples, you will understand:

1. **Cache Patterns**: When to use each caching strategy
2. **Performance Optimization**: Multi-level cache hierarchies
3. **Consistency Models**: Trade-offs between consistency and performance
4. **Scaling Strategies**: Distributed caching and geo-distribution
5. **Monitoring**: Cache metrics and alerting
6. **Security**: Cache security best practices
7. **Production Deployment**: Real-world deployment strategies

## 📞 Support

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Restart Redis
   sudo systemctl restart redis
   ```

2. **High Memory Usage**
   ```bash
   # Check Redis memory usage
   redis-cli info memory
   
   # Set memory limit
   redis-cli config set maxmemory 2gb
   ```

3. **Cache Stampede**
   ```python
   # Use cache locking to prevent stampede
   def get_with_lock(key, fetch_function):
       lock_key = f"lock:{key}"
       if redis_client.set(lock_key, "1", nx=True, ex=60):
           try:
               value = fetch_function()
               redis_client.setex(key, 3600, value)
               return value
           finally:
               redis_client.delete(lock_key)
       else:
           time.sleep(0.1)  # Wait and retry
           return get_from_cache(key)
   ```

### Performance Tuning

1. **Optimize Redis Configuration**
   ```bash
   # For better performance
   echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
   echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
   sysctl -p
   ```

2. **Connection Pooling**
   ```python
   # Use connection pooling
   import redis
   
   pool = redis.ConnectionPool(
       host='localhost',
       port=6379,
       max_connections=20,
       retry_on_timeout=True
   )
   redis_client = redis.Redis(connection_pool=pool)
   ```

---

**🇮🇳 Made with ❤️ for Indian Tech Community**

*This episode demonstrates production-ready caching strategies used by Indian unicorns like Flipkart, Paytm, and Zomato.*