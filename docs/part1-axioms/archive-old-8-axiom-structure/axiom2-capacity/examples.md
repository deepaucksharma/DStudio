---
title: Capacity Examples
description: Real-world examples demonstrating finite capacity constraints and their impact on distributed systems
type: axiom
difficulty: beginner
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 2](index.md) → **Capacity Examples**

# Capacity Examples

**Learn from real failures and successes in managing finite capacity**

> *"Every resource has a limit. The art is knowing where it is before you hit it."*

---

## 🎯 Real-World Failures

### The Great Reddit Hug of Death (2023)

**What Happened**: A small blog post about woodworking hit Reddit's front page. Within minutes:
- 10 req/sec → 50,000 req/sec (5000x spike)
- Single server with 2 CPU cores
- Database connection pool: 10 connections
- Result: Total site failure in 47 seconds

**Root Cause Analysis**:
```python
# The failing configuration
MAX_DB_CONNECTIONS = 10
WORKER_THREADS = 100

# What happened:
# 1. 100 workers compete for 10 connections
# 2. 90 workers block waiting
# 3. Active connections slow due to CPU overload
# 4. Connection timeout cascade
# 5. Complete system lockup
```

**Lessons Learned**:
1. **Connection pools must match worker counts**
2. **CPU saturation affects all operations**
3. **Timeouts prevent cascade failures**
4. **Graceful degradation saves systems**

---

### Uber's New Year's Eve Crisis (2016)

**The Challenge**: Predictable but extreme demand spike
- Normal: 100K rides/hour
- NYE Peak: 2M rides/hour (20x)
- Duration: 2 hours around midnight

**Capacity Constraints Hit**:
```yaml
Driver Location Updates:
  Normal: 50K updates/sec
  Peak: 1M updates/sec
  Bottleneck: Geospatial index updates

Payment Processing:
  Normal: 2K transactions/sec
  Peak: 40K transactions/sec
  Bottleneck: Bank API rate limits

Surge Calculation:
  Normal: Every 5 minutes
  Peak: Every 30 seconds
  Bottleneck: Real-time data aggregation
```

**Solution Architecture**:
```python
class SurgeCapacityManager:
    def __init__(self):
        self.normal_pool = ResourcePool(size=1000)
        self.surge_pool = ResourcePool(size=9000)  # 10x capacity
        self.surge_active = False
    
    def handle_request(self, request):
        if self.should_activate_surge():
            self.activate_surge_mode()
        
        pool = self.surge_pool if self.surge_active else self.normal_pool
        
        if pool.utilization() > 0.8:
            # Start shedding non-critical load
            if not request.is_critical():
                return self.reject_with_retry(request)
        
        return pool.process(request)
    
    def should_activate_surge(self):
        # Predictive activation based on historical patterns
        return (
            self.current_load() > self.baseline * 3 or
            self.time_until_expected_peak() < timedelta(minutes=30)
        )
```

**Results**:
- 99.9% availability during peak
- Average wait time: 3.2 minutes
- Zero payment failures
- $150M in rides processed

---

### Database Connection Pool Exhaustion at Scale

**Company**: Major e-commerce platform (Black Friday 2022)

**The Setup**:
```python
# Application servers: 500 instances
# Connections per server: 20
# Total connections: 10,000
# Database max_connections: 5,000 (oops!)
```

**Timeline of Failure**:
```
00:00 - Black Friday sale starts
00:02 - Traffic spike begins (10x normal)
00:05 - Database connections: 4,800/5,000
00:07 - First "connection pool exhausted" errors
00:09 - Retry storm begins
00:12 - Database CPU: 100%
00:15 - Complete outage
00:45 - Service restored with reduced capacity
```

**The Fix**:
```python
class SmartConnectionPool:
    def __init__(self, min_size=5, max_size=20):
        self.min_size = min_size
        self.max_size = max_size
        self.connections = []
        self.available = Queue()
        self.metrics = PoolMetrics()
        
    def acquire(self, timeout=5.0):
        try:
            # Try to get existing connection
            conn = self.available.get(timeout=timeout)
            
            # Health check before returning
            if self.is_healthy(conn):
                return conn
            else:
                conn.close()
                return self.create_new_connection()
                
        except Empty:
            # Pool exhausted
            if len(self.connections) < self.max_size:
                # Room to grow
                return self.create_new_connection()
            else:
                # At capacity - apply backpressure
                self.metrics.record_pool_exhaustion()
                raise PoolExhausted("Connection pool at capacity")
    
    def release(self, conn):
        if self.should_close_connection(conn):
            conn.close()
            self.connections.remove(conn)
        else:
            self.available.put(conn)
    
    def should_close_connection(self, conn):
        # Reduce pool size if underutilized
        return (
            len(self.connections) > self.min_size and
            self.available.qsize() > self.min_size and
            conn.age() > timedelta(minutes=5)
        )
```

---

## 💻 Code Examples

### Understanding Queue Saturation

```python
import time
import threading
from collections import deque
from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class QueueMetrics:
    """Track queue behavior over time"""
    timestamps: list
    queue_depths: list
    response_times: list
    utilizations: list

class CapacitySimulator:
    """Simulate how utilization affects response time"""
    
    def __init__(self, service_time=0.1, capacity=10):
        self.service_time = service_time
        self.capacity = capacity
        self.queue = deque()
        self.metrics = QueueMetrics([], [], [], [])
        self.processing = False
        
    def arrival_rate_for_utilization(self, target_util):
        """Calculate arrival rate for target utilization"""
        # Utilization = arrival_rate * service_time
        return target_util * self.capacity / self.service_time
    
    def simulate(self, utilization, duration=60):
        """Run simulation at given utilization"""
        arrival_rate = self.arrival_rate_for_utilization(utilization)
        inter_arrival_time = 1.0 / arrival_rate
        
        print(f"\nSimulating {utilization*100}% utilization:")
        print(f"  Arrival rate: {arrival_rate:.1f} req/sec")
        print(f"  Service rate: {1/self.service_time:.1f} req/sec")
        
        # Reset metrics
        self.metrics = QueueMetrics([], [], [], [])
        
        # Generate arrivals
        start_time = time.time()
        next_arrival = start_time
        
        while time.time() - start_time < duration:
            current_time = time.time()
            
            # Add new arrivals
            while current_time >= next_arrival:
                self.queue.append(next_arrival)
                next_arrival += inter_arrival_time
            
            # Process requests
            if self.queue and not self.processing:
                arrival_time = self.queue.popleft()
                wait_time = current_time - arrival_time
                
                # Record metrics
                self.metrics.timestamps.append(current_time - start_time)
                self.metrics.queue_depths.append(len(self.queue))
                self.metrics.response_times.append(wait_time + self.service_time)
                self.metrics.utilizations.append(utilization)
                
                # Simulate processing
                self.processing = True
                threading.Timer(self.service_time, self.complete_processing).start()
            
            time.sleep(0.01)  # Small sleep to prevent CPU spinning
    
    def complete_processing(self):
        self.processing = False
    
    def plot_results(self):
        """Visualize queue behavior"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Queue depth over time
        ax1.plot(self.metrics.timestamps, self.metrics.queue_depths)
        ax1.set_ylabel('Queue Depth')
        ax1.set_title('Queue Depth Over Time')
        ax1.grid(True)
        
        # Response time over time
        ax2.plot(self.metrics.timestamps, self.metrics.response_times)
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Response Time (seconds)')
        ax2.set_title('Response Time Over Time')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()

# Demonstrate the knee of the curve
def demonstrate_utilization_impact():
    """Show how response time explodes at high utilization"""
    
    utilizations = [0.5, 0.7, 0.8, 0.9, 0.95]
    avg_response_times = []
    p99_response_times = []
    
    for util in utilizations:
        sim = CapacitySimulator()
        sim.simulate(util, duration=30)
        
        if sim.metrics.response_times:
            avg_rt = sum(sim.metrics.response_times) / len(sim.metrics.response_times)
            p99_rt = sorted(sim.metrics.response_times)[int(len(sim.metrics.response_times) * 0.99)]
            
            avg_response_times.append(avg_rt)
            p99_response_times.append(p99_rt)
            
            print(f"\nUtilization: {util*100}%")
            print(f"  Avg Response Time: {avg_rt:.3f}s")
            print(f"  P99 Response Time: {p99_rt:.3f}s")
            print(f"  Max Queue Depth: {max(sim.metrics.queue_depths)}")
```

### Little's Law in Practice

```python
class LittlesLawCalculator:
    """
    Little's Law: L = λ * W
    L = Average number of items in system
    λ = Average arrival rate
    W = Average time in system
    """
    
    @staticmethod
    def required_capacity(arrival_rate, target_response_time, utilization_target=0.8):
        """
        Calculate required capacity to meet response time target
        """
        # For M/M/1 queue: W = 1/(μ-λ)
        # Where μ is service rate (capacity)
        # Rearranging: μ = λ + 1/W
        
        service_time = target_response_time * (1 - utilization_target)
        required_service_rate = arrival_rate / utilization_target
        
        return {
            'required_capacity': required_service_rate,
            'service_time_budget': service_time,
            'expected_queue_length': arrival_rate * target_response_time,
            'number_of_servers': max(1, int(required_service_rate * service_time))
        }
    
    @staticmethod
    def predict_response_time(arrival_rate, service_rate):
        """
        Predict response time given arrival and service rates
        """
        if arrival_rate >= service_rate:
            return float('inf')  # System unstable
        
        utilization = arrival_rate / service_rate
        service_time = 1 / service_rate
        wait_time = (utilization * service_time) / (1 - utilization)
        response_time = service_time + wait_time
        
        return {
            'utilization': utilization,
            'service_time': service_time,
            'wait_time': wait_time,
            'response_time': response_time,
            'queue_length': arrival_rate * wait_time
        }

# Real-world example: API Gateway capacity planning
def plan_api_gateway_capacity():
    """Plan capacity for an API gateway"""
    
    calculator = LittlesLawCalculator()
    
    # Current state
    current_rps = 1000  # requests per second
    current_capacity = 1500  # max requests per second
    
    # Analyze current state
    current = calculator.predict_response_time(current_rps, current_capacity)
    print("Current State:")
    print(f"  Utilization: {current['utilization']*100:.1f}%")
    print(f"  Response Time: {current['response_time']*1000:.1f}ms")
    print(f"  Queue Length: {current['queue_length']:.1f}")
    
    # Plan for 2x growth
    future_rps = 2000
    target_response_time = 0.1  # 100ms
    
    required = calculator.required_capacity(future_rps, target_response_time)
    print(f"\nCapacity needed for {future_rps} RPS with {target_response_time*1000}ms target:")
    print(f"  Required Capacity: {required['required_capacity']:.0f} RPS")
    print(f"  Number of Servers: {required['number_of_servers']}")
    print(f"  Expected Queue Length: {required['expected_queue_length']:.1f}")
```

### Implementing Backpressure

```python
import asyncio
from enum import Enum
from typing import Optional

class LoadLevel(Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"

class BackpressureController:
    """
    Implement backpressure to protect system capacity
    """
    
    def __init__(self, 
                 capacity: int = 1000,
                 normal_threshold: float = 0.6,
                 elevated_threshold: float = 0.8,
                 high_threshold: float = 0.9):
        
        self.capacity = capacity
        self.current_load = 0
        self.thresholds = {
            LoadLevel.NORMAL: normal_threshold,
            LoadLevel.ELEVATED: elevated_threshold,
            LoadLevel.HIGH: high_threshold,
            LoadLevel.CRITICAL: 1.0
        }
        
        # Different strategies for different load levels
        self.strategies = {
            LoadLevel.NORMAL: self.accept_all,
            LoadLevel.ELEVATED: self.apply_rate_limiting,
            LoadLevel.HIGH: self.shed_non_critical,
            LoadLevel.CRITICAL: self.emergency_mode
        }
        
    def get_load_level(self) -> LoadLevel:
        """Determine current load level"""
        utilization = self.current_load / self.capacity
        
        if utilization < self.thresholds[LoadLevel.NORMAL]:
            return LoadLevel.NORMAL
        elif utilization < self.thresholds[LoadLevel.ELEVATED]:
            return LoadLevel.ELEVATED
        elif utilization < self.thresholds[LoadLevel.HIGH]:
            return LoadLevel.HIGH
        else:
            return LoadLevel.CRITICAL
    
    async def handle_request(self, request):
        """Apply appropriate backpressure strategy"""
        load_level = self.get_load_level()
        strategy = self.strategies[load_level]
        
        return await strategy(request)
    
    async def accept_all(self, request):
        """Normal operation - accept all requests"""
        self.current_load += 1
        try:
            return await self.process_request(request)
        finally:
            self.current_load -= 1
    
    async def apply_rate_limiting(self, request):
        """Elevated load - apply rate limiting"""
        # Implement token bucket
        if self.token_bucket.try_acquire():
            return await self.accept_all(request)
        else:
            return self.reject_with_retry_after(request, retry_after=1)
    
    async def shed_non_critical(self, request):
        """High load - only accept critical requests"""
        if request.priority == "critical":
            return await self.accept_all(request)
        else:
            # Probabilistic rejection based on priority
            acceptance_prob = {
                "high": 0.5,
                "normal": 0.2,
                "low": 0.0
            }
            
            if random.random() < acceptance_prob.get(request.priority, 0):
                return await self.accept_all(request)
            else:
                return self.reject_with_retry_after(request, retry_after=5)
    
    async def emergency_mode(self, request):
        """Critical load - accept only essential requests"""
        if request.is_health_check():
            # Always respond to health checks
            return {"status": "overloaded"}
        elif request.is_essential():
            # Queue essential requests with timeout
            try:
                return await asyncio.wait_for(
                    self.accept_all(request),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                return self.reject_overloaded(request)
        else:
            return self.reject_overloaded(request)
    
    def reject_with_retry_after(self, request, retry_after: int):
        """Reject with Retry-After header"""
        return {
            "status": 503,
            "headers": {"Retry-After": str(retry_after)},
            "body": {
                "error": "Service temporarily unavailable",
                "retry_after": retry_after
            }
        }
    
    def reject_overloaded(self, request):
        """Reject due to overload"""
        return {
            "status": 503,
            "body": {
                "error": "Service overloaded",
                "message": "Please try again later"
            }
        }
```

---

## 📊 Capacity Patterns in Production

### Netflix's Adaptive Capacity Management

Netflix handles massive scale with intelligent capacity management:

```python
class NetflixCapacityManager:
    """
    Netflix's approach to capacity management
    """
    
    def __init__(self):
        self.regions = {}
        self.predictive_scaler = PredictiveScaler()
        self.chaos_monkey = ChaosMonkey()
        
    def handle_regional_failure(self, failed_region):
        """
        Redistribute load when a region fails
        """
        failed_load = self.regions[failed_region].current_load
        healthy_regions = [r for r in self.regions if r != failed_region]
        
        # Calculate spare capacity in each region
        spare_capacity = {}
        for region in healthy_regions:
            spare = self.regions[region].capacity - self.regions[region].current_load
            spare_capacity[region] = spare
        
        total_spare = sum(spare_capacity.values())
        
        if total_spare < failed_load:
            # Not enough spare capacity - activate surge mode
            self.activate_global_surge_mode()
        
        # Distribute load proportionally
        for region, spare in spare_capacity.items():
            additional_load = failed_load * (spare / total_spare)
            self.regions[region].add_load(additional_load)
    
    def predictive_scaling(self):
        """
        Scale based on predicted demand
        """
        for region in self.regions:
            # Predict load for next hour
            predicted_load = self.predictive_scaler.predict(
                region=region,
                lookahead=timedelta(hours=1)
            )
            
            # Calculate required capacity (target 70% utilization)
            required_capacity = predicted_load / 0.7
            
            # Scale if needed (with 10% buffer)
            if required_capacity > self.regions[region].capacity * 0.9:
                self.scale_region(region, required_capacity * 1.1)
```

### Database Connection Pooling Best Practices

```python
class ProductionConnectionPool:
    """
    Production-grade connection pool with monitoring
    """
    
    def __init__(self, 
                 min_size: int = 5,
                 max_size: int = 20,
                 max_overflow: int = 10,
                 timeout: float = 30.0):
        
        self.min_size = min_size
        self.max_size = max_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        
        # Metrics
        self.metrics = {
            'acquisitions': 0,
            'timeouts': 0,
            'high_water_mark': 0,
            'total_wait_time': 0
        }
        
    def calculate_optimal_pool_size(self, 
                                   concurrent_requests: int,
                                   avg_query_time: float,
                                   target_wait_time: float) -> int:
        """
        Calculate optimal pool size using Little's Law
        """
        # Average connections in use = concurrent_requests * avg_query_time
        avg_connections_needed = concurrent_requests * avg_query_time
        
        # Add buffer for variance (30%)
        with_buffer = avg_connections_needed * 1.3
        
        # Round up and enforce limits
        optimal = int(math.ceil(with_buffer))
        return max(self.min_size, min(optimal, self.max_size))
    
    def auto_tune(self):
        """
        Automatically adjust pool size based on metrics
        """
        if self.metrics['timeouts'] > 0:
            # Experienced timeouts - need more connections
            new_size = min(self.max_size, self.current_size + 2)
            self.resize(new_size)
            
        elif self.metrics['high_water_mark'] < self.current_size * 0.5:
            # Underutilized - can reduce
            new_size = max(self.min_size, self.current_size - 1)
            self.resize(new_size)
```

---

## 🎓 Key Lessons

### 1. **The 80% Rule**
Never run production systems above 80% capacity:
- 50% utilization → 2x service time
- 80% utilization → 5x service time  
- 90% utilization → 10x service time
- 95% utilization → 20x service time

### 2. **Cascade Failures**
Capacity exhaustion in one component cascades:
```
Connection Pool Full → Threads Block → 
CPU Idle → Requests Queue → 
Timeouts → Retries → More Load → 
Complete Failure
```

### 3. **Backpressure Saves Systems**
Better to reject some requests than crash entirely:
- Fail fast at the edge
- Preserve core functionality
- Communicate clearly with retry guidance

### 4. **Monitor the Right Metrics**
- **Utilization**: Current load / capacity
- **Saturation**: Queue depth
- **Errors**: Timeout and rejection rates
- **Latency**: Response time percentiles

### 5. **Capacity != Just Servers**
Every resource has capacity limits:
- CPU cycles
- Memory (RAM and heap)
- Network bandwidth
- Disk I/O
- Database connections
- Thread pools
- File descriptors
- API rate limits

---

## 📚 References

1. [Google SRE Book - Managing Load](https://sre.google/sre-book/handling-overload/)
2. [AWS Well-Architected - Capacity Planning](https://wa.aws.amazon.com/wat.concept.capacity.en.html)
3. [The USE Method](http://www.brendangregg.com/usemethod.html)
4. [Queueing Theory in Practice](https://www.cs.cmu.edu/~harchol/Performance/book.html)

---

**Previous**: [Overview](./) | **Next**: [Exercises](exercises.md)

**Related Patterns**: 
- [Auto Scaling](/patterns/auto-scaling) - Dynamic capacity management
- [Load Balancing](/patterns/load-balancing) - Distributing load across capacity  
- [Circuit Breaker](/patterns/circuit-breaker) - Failing fast when capacity exceeded
- [Bulkhead](/patterns/bulkhead) - Isolating capacity failures