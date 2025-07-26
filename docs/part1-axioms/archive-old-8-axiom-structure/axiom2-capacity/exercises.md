---
title: Capacity Exercises
description: Hands-on exercises to understand capacity limits, queue behavior, and system performance under load
type: axiom
difficulty: beginner
reading_time: 30 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms) → [Axiom 2](index.md) → **Capacity Exercises**

# Capacity Exercises

**Build intuition about capacity through hands-on experimentation**

> *"The best way to understand capacity is to exceed it."*

---

## Lab 1: Queue Simulation Visualizer

### Objective
Build a visual queue simulator to understand how utilization affects response time.

### Background
The relationship between utilization and response time is non-linear. This lab helps you see why systems collapse at high utilization.

### Exercise

```python
# starter_code.py
import time
import random
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np

class VisualQueueSimulator:
    """
    TODO: Complete this queue simulator with real-time visualization
    """
    
    def __init__(self, service_rate=10):
        self.service_rate = service_rate  # requests per second
        self.queue = deque()
        self.metrics = {
            'queue_lengths': [],
            'response_times': [],
            'timestamps': []
        }
        self.running = False
        
    def set_arrival_rate(self, arrival_rate):
        """
        TODO: Implement arrival rate control
        Hint: Use Poisson process for realistic arrival patterns
        """
        pass
    
    def process_request(self):
        """
        TODO: Implement request processing
        - Dequeue request
        - Simulate processing time (exponential distribution)
        - Record metrics
        """
        pass
    
    def visualize_live(self):
        """
        TODO: Create live visualization showing:
        1. Queue length over time
        2. Response time distribution
        3. Current utilization
        """
        pass

# Your task: Complete the implementation
```

### Success Criteria
1. ✅ Simulator accurately models M/M/1 queue
2. ✅ Live visualization updates in real-time
3. ✅ Can demonstrate the "knee" at 80% utilization
4. ✅ Shows both average and percentile metrics

### Bonus Challenge
Add multiple queue disciplines (FIFO, LIFO, Priority) and compare their impact on response time distribution.

---

## Lab 2: Little's Law Calculator

### Objective
Build a capacity planning tool using Little's Law.

### Background
Little's Law states: L = λW (items in system = arrival rate × time in system)

### Exercise

```python
class CapacityPlanner:
    """
    Build a tool that helps plan system capacity
    """
    
    def plan_capacity(self, requirements):
        """
        TODO: Given requirements, calculate needed capacity
        
        Requirements format:
        {
            'peak_requests_per_second': 1000,
            'average_request_size_kb': 10,
            'target_response_time_ms': 100,
            'target_availability': 0.999,
            'growth_rate_monthly': 0.1
        }
        
        Should return:
        {
            'servers_needed': 10,
            'connections_per_server': 100,
            'memory_per_server_gb': 16,
            'network_bandwidth_gbps': 1,
            'database_connections': 500,
            'cache_size_gb': 100,
            'cost_estimate_monthly': 5000
        }
        """
# Hint: Account for:
# - Peak vs average load
# - Growth over time
# - Failure scenarios (n+1, n+2)
# - Cascade effects
        pass
    
    def simulate_failure_scenarios(self, current_capacity, failure_mode):
        """
        TODO: Simulate what happens when components fail
        
        Failure modes:
        - 'single_server': One server fails
        - 'entire_az': Entire availability zone fails
        - 'database_primary': Database primary fails
        - 'cache_layer': Entire cache layer fails
        """
        pass

# Test scenarios to implement:
scenarios = [
    "E-commerce site preparing for Black Friday",
    "Video streaming service launching new show",
    "Financial trading platform during market open",
    "Social media platform during major event"
]
```

### Success Criteria
1. ✅ Correctly applies Little's Law
2. ✅ Accounts for peak traffic patterns  
3. ✅ Includes failure scenario planning
4. ✅ Provides cost-optimized recommendations

---

## Lab 3: Load Testing Workshop

### Objective
Find the breaking point of a system through systematic load testing.

### Background
Every system has a cliff where performance degrades catastrophically. Finding it safely is crucial.

### Exercise

```python
import aiohttp
import asyncio
import time
from dataclasses import dataclass
from typing import List

@dataclass
class LoadTestResult:
    requests_per_second: float
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_types: dict

class LoadTester:
    """
    Build a load testing framework that finds system limits
    """
    
    async def find_breaking_point(self, 
                                  target_url: str,
                                  start_rps: int = 10,
                                  step_size: int = 10,
                                  step_duration: int = 30) -> List[LoadTestResult]:
        """
        TODO: Implement adaptive load testing
        
        Algorithm:
        1. Start at start_rps
        2. Run for step_duration seconds
        3. If success_rate > 99% and p95 < target, increase load
        4. If errors or high latency, record breaking point
        5. Return full results for analysis
        """
        results = []
        
# Your implementation here
        
        return results
    
    async def generate_load(self, 
                           target_url: str, 
                           requests_per_second: int,
                           duration: int) -> LoadTestResult:
        """
        TODO: Generate precise load at specified RPS
        
        Challenges:
        - Maintain consistent request rate
        - Handle connection pooling 
        - Accurate latency measurement
        - Classify different error types
        """
        pass
    
    def analyze_results(self, results: List[LoadTestResult]):
        """
        TODO: Analyze results to find:
        1. Maximum sustainable throughput
        2. Optimal operating point (best latency/throughput)
        3. Warning thresholds
        4. Cliff detection
        """
        pass

# Test targets to implement:
test_targets = {
    'api_endpoint': 'https://api.example.com/search',
    'database_query': 'SELECT * FROM products WHERE category = ?',
    'cache_operation': 'GET user:*',
    'message_queue': 'PUBLISH events.user.action'
}
```

### Success Criteria
1. ✅ Accurately generates specified load
2. ✅ Identifies breaking point without crashing system
3. ✅ Produces clear visualization of results
4. ✅ Provides actionable recommendations

### Real-World Scenario
Test your load tester against this mock service:

```python
# mock_service.py - A service that degrades at high load
class MockService:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.current_load = 0
        self.connection_pool = []
        
    async def handle_request(self):
# Simulate realistic degradation
        utilization = self.current_load / self.capacity
        
        if utilization > 0.95:
            raise Exception("Service Unavailable")
        elif utilization > 0.9:
            await asyncio.sleep(random.uniform(1, 5))  # High latency
        elif utilization > 0.8:
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Degraded
        else:
            await asyncio.sleep(0.01)  # Normal
```

---

## Lab 4: Backpressure Implementation

### Objective
Implement a production-grade backpressure system.

### Background
Backpressure prevents cascade failures by rejecting load early when capacity is exceeded.

### Exercise

```python
class BackpressureSystem:
    """
    Implement a multi-level backpressure system
    """
    
    def __init__(self):
        self.levels = {
            'green': {'threshold': 0.6, 'action': 'accept_all'},
            'yellow': {'threshold': 0.8, 'action': 'rate_limit'},
            'orange': {'threshold': 0.9, 'action': 'priority_only'},
            'red': {'threshold': 0.95, 'action': 'essential_only'}
        }
        
    def implement_token_bucket(self, rate: int, burst: int):
        """
        TODO: Implement token bucket algorithm
        - Tokens added at 'rate' per second
        - Bucket holds maximum 'burst' tokens
        - Each request consumes one token
        - No tokens = reject request
        """
        pass
    
    def implement_adaptive_concurrency(self):
        """
        TODO: Implement Netflix's adaptive concurrency limits
        
        Algorithm:
        1. Start with initial limit
        2. Measure latency continuously 
        3. If latency low, increase limit
        4. If latency high, decrease limit
        5. Find optimal concurrency dynamically
        """
        pass
    
    def implement_circuit_breaker(self):
        """
        TODO: Implement circuit breaker pattern
        
        States:
        - Closed: Normal operation
        - Open: All requests fail fast
        - Half-Open: Test if service recovered
        
        Transitions based on error rate
        """
        pass

# Test scenarios:
scenarios = [
    "Gradual traffic increase",
    "Sudden spike (10x normal)",
    "Oscillating load",
    "Sustained overload"
]
```

### Success Criteria
1. ✅ Prevents cascade failures
2. ✅ Maintains service for priority traffic
3. ✅ Provides clear feedback to clients
4. ✅ Automatically recovers when load decreases

---

## Challenge Problems

### Challenge 1: The Connection Pool Puzzle

You have:
- 100 application servers
- Each can handle 50 concurrent requests
- Average request takes 100ms
- Database supports 1000 connections max

Questions:
1. What's the maximum requests/second you can handle?
2. How many connections should each server have?
3. What happens if request time increases to 200ms?
4. Design a solution that handles 2x load without adding database connections

### Challenge 2: The Cascading Failure

Given this architecture:
```
Load Balancer (10K RPS capacity)
    ↓
Web Servers (100 instances, 100 RPS each)
    ↓
Cache Layer (50K RPS capacity)
    ↓
Database (1K RPS capacity)
```

If cache fails:
1. Calculate time until database overload
2. Design automatic mitigation strategy
3. Calculate business impact ($1000/minute downtime cost)
4. Propose architecture changes to prevent cascade

### Challenge 3: Multi-Region Capacity

Design capacity for a global service:
- 3 regions: US (50% traffic), EU (30%), APAC (20%)
- Each region must survive others failing
- 100ms latency target within region
- 24x7 operation (follow the sun)

Calculate:
1. Capacity per region with failure scenarios
2. Cost optimization strategies
3. Data replication bandwidth needed
4. Handling region-specific traffic spikes

---

## 🤔 Thought Experiments

### 1. The Infinite Queue Paradox
"If I have infinite queue space, I never drop requests. Is this good?"

Consider:
- What happens to request latency?
- How do timeouts cascade?
- When is dropping better than queueing?

### 2. The Utilization Dilemma
"Running at 50% utilization wastes half my resources. Running at 95% risks collapse."

Explore:
- Cost vs reliability trade-offs
- Different utilization targets for different resources
- How to justify "waste" to management

### 3. The Horizontal Scaling Trap
"Just add more servers" seems like universal solution.

What about:
- Shared resource bottlenecks?
- Coordination overhead?
- Data consistency costs?

### 4. The Perfect Capacity
"What if I could predict exact future load?"

Investigate:
- Spin-up time vs cost
- Prediction accuracy limits
- Black swan events

---

## Mini-Project: Build Your Own Autoscaler

### Requirements
Build an autoscaler that:

1. **Monitors** multiple metrics:
   - CPU utilization
   - Request queue depth
   - Response time percentiles
   - Error rates

2. **Predicts** future needs:
   - Time-series analysis
   - Seasonal patterns
   - Growth trends

3. **Scales** intelligently:
   - Not too aggressive (flapping)
   - Not too conservative (missing SLA)
   - Cost-aware decisions

4. **Handles** edge cases:
   - Thundering herd
   - Cold start penalty
   - Maximum capacity limits

### Starter Template

```python
class IntelligentAutoscaler:
    def __init__(self):
        self.metrics_history = []
        self.scaling_decisions = []
        
    def collect_metrics(self) -> dict:
        """Gather current system metrics"""
        pass
        
    def predict_load(self, lookahead_minutes: int) -> float:
        """Predict future load based on patterns"""
        pass
        
    def calculate_required_capacity(self, predicted_load: float) -> int:
        """Convert load to instance count"""
        pass
        
    def make_scaling_decision(self) -> str:
        """Decide: scale_up, scale_down, or hold"""
        pass
        
    def execute_scaling(self, decision: str):
        """Actually perform the scaling action"""
        pass

# Bonus: Add machine learning for better predictions
```

---

## Reflection Questions

After completing these exercises, consider:

1. **What surprised you most about capacity behavior?**
2. **How would you explain the 80% rule to a non-technical manager?**
3. **What's the most dangerous capacity-related assumption you've seen?**
4. **How do you balance cost efficiency with reliability?**

---

## 🎓 What You've Learned

Through these exercises, you've gained practical experience with:

- **Queue Theory**: How utilization drives response time
- **Capacity Planning**: Using Little's Law and growth projections
- **Load Testing**: Finding limits safely
- **Backpressure**: Protecting systems from overload
- **Autoscaling**: Dynamically managing capacity
- **Failure Scenarios**: Planning for cascade effects

These skills are fundamental to building reliable distributed systems that gracefully handle load variations.

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 3](/part1-axioms/archive-old-8-axiom-structure/axiom3-failure)

**Related Patterns**: 
- [Auto Scaling](/patterns/auto-scaling) - Implement what you learned
- [Circuit Breaker](/patterns/circuit-breaker) - Backpressure in practice
- [Bulkhead](/patterns/bulkhead) - Isolate capacity failures