# Work Distribution Exercises

!!! info "Prerequisites"
    - Completed [Work Distribution Concepts](index.md)
    - Reviewed [Work Distribution Examples](examples.md)
    - Basic understanding of load balancing

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Pillars Overview](../index.md) |
    [→ Next: State Distribution](../pillar-2-state/index.md)

## Exercise 1: Build a Work Stealer

### Objective
Implement a work-stealing queue system that automatically balances work across workers.

### Requirements
- Multiple workers with local queues
- Workers can steal from others when idle
- Minimize contention between workers
- Track stealing statistics

### Starter Code
```python
import threading
import time
import random
from collections import deque
from dataclasses import dataclass

@dataclass
class WorkItem:
    id: int
    complexity: float  # seconds to process
    
class WorkStealingQueue:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.queues = [deque() for _ in range(num_workers)]
        self.locks = [threading.Lock() for _ in range(num_workers)]
        self.stats = {
            'processed': [0] * num_workers,
            'stolen': [0] * num_workers,
            'steal_attempts': [0] * num_workers
        }
        
    def add_work(self, worker_id, work_item):
        """Add work to a specific worker's queue"""
        with self.locks[worker_id]:
            self.queues[worker_id].append(work_item)
    
    def get_work(self, worker_id):
        """Get work, stealing if necessary"""
        # Try own queue first
        with self.locks[worker_id]:
            if self.queues[worker_id]:
                return self.queues[worker_id].popleft()
        
        # Try stealing
        # TODO: Implement stealing logic
        # - Find busiest queue
        # - Steal half their work
        # - Update statistics
        pass
    
    def worker_thread(self, worker_id):
        """Worker thread implementation"""
        while True:
            work = self.get_work(worker_id)
            if work:
                # Process work
                time.sleep(work.complexity)
                self.stats['processed'][worker_id] += 1
            else:
                # No work available
                time.sleep(0.01)
    
    def print_stats(self):
        """Print work distribution statistics"""
        print(f"Processed: {self.stats['processed']}")
        print(f"Stolen: {self.stats['stolen']}")
        print(f"Steal attempts: {self.stats['steal_attempts']}")

# Test your implementation
queue = WorkStealingQueue(4)

# Add uneven work distribution
for i in range(100):
    worker = 0 if i < 70 else random.randint(1, 3)
    complexity = random.uniform(0.01, 0.1)
    queue.add_work(worker, WorkItem(i, complexity))

# Run workers and measure performance
```

### Expected Behavior
- Work should be automatically balanced
- No worker should be idle while others have work
- Stealing should be efficient (minimal contention)

## Exercise 2: Implement Consistent Hashing with Virtual Nodes

### Objective
Build a consistent hashing system that handles node additions/removals gracefully.

### Requirements
- Support adding/removing nodes
- Virtual nodes for better distribution
- Analyze key redistribution on changes
- Support weighted nodes

### Starter Template
```python
class ConsistentHashRing:
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self.nodes = {}  # node -> weight
        
    def add_node(self, node, weight=1.0):
        """Add a node with given weight"""
        # TODO: Add virtual nodes proportional to weight
        pass
        
    def remove_node(self, node):
        """Remove a node and its virtual nodes"""
        # TODO: Remove all virtual nodes
        pass
        
    def get_node(self, key):
        """Find node responsible for key"""
        # TODO: Find the right node using binary search
        pass
        
    def get_key_distribution(self):
        """Analyze how keys are distributed"""
        # TODO: Return distribution statistics
        pass
        
    def simulate_redistribution(self, node_to_remove):
        """Simulate what happens when a node is removed"""
        # TODO: Calculate how many keys move where
        pass

# Test scenarios
ring = ConsistentHashRing(virtual_nodes=150)

# Add nodes with different capacities
ring.add_node("server1", weight=1.0)
ring.add_node("server2", weight=2.0)  # 2x capacity
ring.add_node("server3", weight=0.5)  # Half capacity

# Test distribution
keys = [f"user_{i}" for i in range(10000)]
distribution = {}
for key in keys:
    node = ring.get_node(key)
    distribution[node] = distribution.get(node, 0) + 1

print("Key distribution:", distribution)

# Simulate node failure
print("\nRemoving server1...")
affected = ring.simulate_redistribution("server1")
print(f"Keys that would move: {affected}")
```

## Exercise 3: Build an Adaptive Load Balancer

### Objective
Create a load balancer that learns from response times and error rates.

### Requirements
- Track performance metrics per backend
- Adjust routing probability based on performance
- Handle backend failures gracefully
- Support different routing algorithms

### Implementation Framework
```python
import heapq
import statistics
from abc import ABC, abstractmethod

class RoutingAlgorithm(ABC):
    @abstractmethod
    def select_backend(self, backends, stats):
        pass

class WeightedRoundRobin(RoutingAlgorithm):
    def __init__(self):
        self.current_weights = {}
        
    def select_backend(self, backends, stats):
        # TODO: Implement weighted round-robin
        pass

class LeastConnections(RoutingAlgorithm):
    def select_backend(self, backends, stats):
        # TODO: Select backend with least active connections
        pass

class AdaptiveP2C(RoutingAlgorithm):
    """Power of Two Choices with adaptive weights"""
    def select_backend(self, backends, stats):
        # TODO: Pick 2 random backends, choose better one
        pass

class LoadBalancer:
    def __init__(self, backends, algorithm):
        self.backends = backends
        self.algorithm = algorithm
        self.stats = {
            backend: {
                'requests': 0,
                'errors': 0,
                'response_times': deque(maxlen=100),
                'active_connections': 0
            }
            for backend in backends
        }
        
    def route_request(self):
        """Select a backend for the request"""
        backend = self.algorithm.select_backend(
            self.backends, 
            self.stats
        )
        self.stats[backend]['active_connections'] += 1
        return backend
        
    def complete_request(self, backend, response_time, error=False):
        """Record request completion"""
        stats = self.stats[backend]
        stats['requests'] += 1
        stats['active_connections'] -= 1
        
        if error:
            stats['errors'] += 1
        else:
            stats['response_times'].append(response_time)
    
    def get_health_scores(self):
        """Calculate health score for each backend"""
        scores = {}
        for backend, stats in self.stats.items():
            # TODO: Calculate health score based on:
            # - Error rate
            # - P95 response time
            # - Current load
            pass
        return scores

# Test different algorithms
backends = ['api1', 'api2', 'api3']
algorithms = [
    WeightedRoundRobin(),
    LeastConnections(),
    AdaptiveP2C()
]

for algo in algorithms:
    lb = LoadBalancer(backends, algo)
    # Simulate traffic and compare performance
```

## Exercise 4: Implement a Circuit Breaker

### Objective
Build a circuit breaker that prevents cascading failures.

### Requirements
- Three states: Closed, Open, Half-Open
- Configurable failure threshold and timeout
- Support for different failure criteria
- Metrics collection

### Advanced Implementation
```python
from enum import Enum
from datetime import datetime, timedelta
import threading

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class FailureCriteria:
    def __init__(self, 
                 error_threshold=0.5,
                 response_time_threshold=1.0,
                 consecutive_failures=5):
        self.error_threshold = error_threshold
        self.response_time_threshold = response_time_threshold
        self.consecutive_failures = consecutive_failures

class CircuitBreaker:
    def __init__(self, 
                 name,
                 failure_criteria,
                 recovery_timeout=60,
                 half_open_requests=3):
        self.name = name
        self.criteria = failure_criteria
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.half_open_successes = 0
        
        self._lock = threading.RLock()
        
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        if not self._can_proceed():
            raise Exception(f"Circuit {self.name} is OPEN")
            
        try:
            start = time.time()
            result = func(*args, **kwargs)
            response_time = time.time() - start
            
            self._record_success(response_time)
            return result
            
        except Exception as e:
            self._record_failure()
            raise
    
    def _can_proceed(self):
        """Check if request can proceed"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
                
            elif self.state == CircuitState.OPEN:
                # Check if we should try half-open
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_successes = 0
                    return True
                return False
                
            else:  # HALF_OPEN
                # Allow limited requests
                return self.half_open_successes < self.half_open_requests
    
    def _should_attempt_reset(self):
        """Check if enough time has passed"""
        # TODO: Implement timeout check
        pass
    
    def _record_success(self, response_time):
        """Record successful call"""
        with self._lock:
            # TODO: Update metrics and state
            pass
    
    def _record_failure(self):
        """Record failed call"""
        with self._lock:
            # TODO: Update metrics and check if should open
            pass
    
    def get_metrics(self):
        """Return circuit breaker metrics"""
        with self._lock:
            return {
                'state': self.state.value,
                'failures': self.failures,
                'successes': self.successes,
                'error_rate': self._calculate_error_rate()
            }

# Test the circuit breaker
cb = CircuitBreaker(
    "payment-service",
    FailureCriteria(error_threshold=0.5, consecutive_failures=3),
    recovery_timeout=30
)

def flaky_service():
    if random.random() < 0.3:  # 30% failure rate
        raise Exception("Service error")
    return "Success"

# Simulate requests
for i in range(100):
    try:
        result = cb.call(flaky_service)
        print(f"Request {i}: Success")
    except Exception as e:
        print(f"Request {i}: {e}")
    
    if i % 10 == 0:
        print(f"Metrics: {cb.get_metrics()}")
    
    time.sleep(0.1)
```

## Exercise 5: Build an Autoscaler

### Objective
Implement an autoscaling system with multiple scaling strategies.

### Requirements
- Support reactive and predictive scaling
- Implement cool-down periods
- Handle scale-up and scale-down differently
- Cost-aware scaling decisions

### Complete System
```python
class AutoScaler:
    def __init__(self, 
                 min_instances=2,
                 max_instances=100,
                 target_cpu=70,
                 scale_up_threshold=80,
                 scale_down_threshold=40):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        self.current_instances = min_instances
        self.metrics_history = deque(maxlen=300)  # 5 minutes
        self.scaling_history = []
        self.last_scale_time = None
        self.cool_down_period = 180  # 3 minutes
        
    def add_metrics(self, timestamp, metrics):
        """Add current metrics"""
        self.metrics_history.append({
            'timestamp': timestamp,
            'cpu': metrics['cpu'],
            'memory': metrics['memory'],
            'requests_per_second': metrics['rps'],
            'response_time_p95': metrics['p95']
        })
    
    def should_scale(self):
        """Determine if scaling is needed"""
        if self._in_cool_down():
            return 0
            
        current_cpu = self._get_average_cpu()
        predicted_cpu = self._predict_cpu()
        
        # TODO: Implement scaling logic
        # Consider:
        # - Current vs predicted metrics
        # - Cost of scaling
        # - SLA requirements
        pass
    
    def _predict_cpu(self):
        """Predict future CPU usage"""
        # TODO: Implement prediction
        # - Linear regression on recent data
        # - Time-of-day patterns
        # - Day-of-week patterns
        pass
    
    def scale(self, direction):
        """Execute scaling action"""
        if direction > 0:
            # Scale up
            new_instances = min(
                self.current_instances + direction,
                self.max_instances
            )
        else:
            # Scale down
            new_instances = max(
                self.current_instances + direction,
                self.min_instances
            )
        
        if new_instances != self.current_instances:
            self.scaling_history.append({
                'timestamp': datetime.now(),
                'from': self.current_instances,
                'to': new_instances,
                'reason': self._get_scaling_reason()
            })
            
            self.current_instances = new_instances
            self.last_scale_time = datetime.now()
    
    def calculate_cost(self):
        """Calculate current hourly cost"""
        instance_cost = 0.0416  # t3.medium
        return self.current_instances * instance_cost

# Test autoscaler with simulated load
scaler = AutoScaler(min_instances=2, max_instances=20)

# Simulate daily traffic pattern
for hour in range(24):
    # Morning ramp-up, afternoon peak, evening decline
    base_load = 30
    if 8 <= hour <= 10:
        load = base_load + (hour - 8) * 20
    elif 11 <= hour <= 14:
        load = base_load + 40
    elif 15 <= hour <= 18:
        load = base_load + 30 - (hour - 15) * 10
    else:
        load = base_load
    
    # Add some randomness
    load += random.uniform(-5, 5)
    
    metrics = {
        'cpu': load * 1.5,
        'memory': load * 0.8,
        'rps': load * 10,
        'p95': 50 + load * 0.5
    }
    
    scaler.add_metrics(datetime.now(), metrics)
    scale_decision = scaler.should_scale()
    
    if scale_decision != 0:
        scaler.scale(scale_decision)
        print(f"Hour {hour}: Scaled to {scaler.current_instances} instances")
        print(f"Hourly cost: ${scaler.calculate_cost():.2f}")
```

## Project: Complete Work Distribution System

### Objective
Design and implement a complete work distribution system for a video processing platform.

### Requirements
1. **Work Queue**: Persistent queue for video jobs
2. **Worker Pool**: Auto-scaling workers
3. **Load Balancing**: Smart job distribution
4. **Monitoring**: Real-time metrics
5. **Fault Tolerance**: Handle worker failures

### System Design
```python
class VideoProcessingSystem:
    def __init__(self):
        self.job_queue = PersistentQueue()
        self.worker_pool = WorkerPool()
        self.load_balancer = AdaptiveLoadBalancer()
        self.monitor = SystemMonitor()
        
    def submit_job(self, video_url, processing_options):
        """Submit a video for processing"""
        job = VideoJob(
            id=generate_job_id(),
            video_url=video_url,
            options=processing_options,
            priority=self.calculate_priority(processing_options)
        )
        
        # Estimate processing time
        estimated_time = self.estimate_processing_time(job)
        
        # Find optimal worker
        worker = self.load_balancer.select_worker(
            job, 
            self.worker_pool.get_available_workers()
        )
        
        # Assign job
        self.job_queue.enqueue(job, worker)
        
        return {
            'job_id': job.id,
            'estimated_time': estimated_time,
            'assigned_worker': worker.id
        }
    
    def handle_worker_failure(self, worker_id):
        """Redistribute work from failed worker"""
        # TODO: Implement failure handling
        # - Identify jobs on failed worker
        # - Redistribute to healthy workers
        # - Update job status
        pass
    
    def optimize_distribution(self):
        """Periodically rebalance work"""
        # TODO: Implement optimization
        # - Identify imbalanced workers
        # - Calculate optimal distribution
        # - Migrate jobs if beneficial
        pass

# Implement each component
class PersistentQueue:
    """Durable job queue with priorities"""
    pass

class WorkerPool:
    """Auto-scaling pool of video processors"""
    pass

class AdaptiveLoadBalancer:
    """Smart job placement based on worker capabilities"""
    pass

class SystemMonitor:
    """Real-time monitoring and alerting"""
    pass
```

### Evaluation Criteria
- Throughput (videos processed/hour)
- Latency (time to start processing)
- Efficiency (CPU utilization)
- Resilience (handling failures)
- Cost (infrastructure spend)

## Reflection Questions

After completing exercises:

1. **Scaling Trade-offs**: Where did you choose simplicity over perfect distribution?

2. **Failure Handling**: How does your system behave under worker failures?

3. **Cost vs Performance**: What scaling decisions impact cost most?

4. **Monitoring**: What metrics are most important for work distribution?

5. **Real-world Application**: How would you adapt these patterns for your use case?

## Navigation

!!! tip "Continue Learning"
    
    **Next Pillar**: [Distribution of State](../pillar-2-state/index.md) →
    
    **Related Axioms**: [Capacity](../../part1-axioms/axiom-2-capacity/index.md) | [Failure](../../part1-axioms/axiom-3-failure/index.md)
    
    **Back to**: [Pillars Overview](../index.md)