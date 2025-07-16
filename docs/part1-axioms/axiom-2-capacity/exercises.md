# Capacity Exercises

!!! info "Prerequisites"
    - [Axiom 2: Capacity Core Concepts](index.md)
    - [Capacity Examples](examples.md)
    - Basic understanding of queueing theory

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Capacity Home](index.md) |
    [→ Next Axiom](../axiom-3-failure/index.md)

## Exercise 1: Find Your Breaking Point

### 🔧 Try This: Local Load Test

```python
# Simple web server to test
from flask import Flask, jsonify
import time
import random

app = Flask(__name__)

# Simulate variable processing time
@app.route('/api/process')
def process():
    # Simulate work (50-150ms)
    time.sleep(random.uniform(0.05, 0.15))
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)
```

Now test it:

```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Find the breaking point
# Install apache bench: apt-get install apache2-utils

# Test 1: Baseline (1 concurrent user)
ab -n 1000 -c 1 http://localhost:5000/api/process

# Test 2: Moderate load
ab -n 1000 -c 10 http://localhost:5000/api/process

# Test 3: Heavy load  
ab -n 1000 -c 50 http://localhost:5000/api/process

# Test 4: Find the cliff
ab -n 1000 -c 100 http://localhost:5000/api/process

# Monitor in Terminal 3:
htop  # Watch CPU
```

<details>
<summary>Expected Results</summary>

```
Concurrency 1:
- Requests/sec: ~10
- Mean latency: 100ms
- CPU: 10%

Concurrency 10:
- Requests/sec: ~80  
- Mean latency: 125ms
- CPU: 60%

Concurrency 50:
- Requests/sec: ~90
- Mean latency: 550ms
- CPU: 95%

Concurrency 100:
- Requests/sec: ~85 (decreasing!)
- Mean latency: 1200ms
- Failed requests: >0
- CPU: 100%

Observation: Performance degrades after ~80% CPU
```

</details>

## Exercise 2: Little's Law Calculator

### 🔧 Try This: Verify Little's Law

```python
class SystemMonitor:
    def __init__(self):
        self.arrivals = []
        self.departures = []
        self.in_system = 0
        
    def arrival(self, time):
        self.arrivals.append(time)
        self.in_system += 1
        
    def departure(self, time):
        self.departures.append(time)
        self.in_system -= 1
        
    def calculate_littles_law(self):
        if not self.departures:
            return None
            
        # L = Average number in system
        L = sum(self.in_system_over_time()) / len(self.in_system_over_time())
        
        # λ = Arrival rate
        duration = self.departures[-1] - self.arrivals[0]
        λ = len(self.arrivals) / duration
        
        # W = Average time in system
        total_time = sum(d - a for a, d in zip(self.arrivals, self.departures))
        W = total_time / len(self.departures)
        
        # Verify: L = λ × W
        calculated_L = λ * W
        
        return {
            'L_observed': L,
            'L_calculated': calculated_L,
            'λ': λ,
            'W': W,
            'error': abs(L - calculated_L) / L * 100
        }

# Exercise: Simulate a coffee shop
import random
import heapq

def simulate_coffee_shop(arrival_rate=1.0, service_rate=1.2, duration=3600):
    """
    Simulate a coffee shop queue
    arrival_rate: customers per minute
    service_rate: customers served per minute  
    duration: simulation time in seconds
    """
    monitor = SystemMonitor()
    time = 0
    events = []
    
    # Schedule first arrival
    next_arrival = random.expovariate(arrival_rate / 60)
    heapq.heappush(events, (next_arrival, 'arrival'))
    
    server_free = True
    queue = []
    
    while time < duration and events:
        time, event_type = heapq.heappop(events)
        
        if event_type == 'arrival':
            monitor.arrival(time)
            queue.append(time)
            
            # Schedule next arrival
            next_arrival = time + random.expovariate(arrival_rate / 60)
            if next_arrival < duration:
                heapq.heappush(events, (next_arrival, 'arrival'))
            
            # Start service if server free
            if server_free and queue:
                server_free = False
                service_time = random.expovariate(service_rate / 60)
                heapq.heappush(events, (time + service_time, 'departure'))
                
        elif event_type == 'departure':
            if queue:
                queue.pop(0)
                monitor.departure(time)
            
            # Serve next customer
            if queue:
                service_time = random.expovariate(service_rate / 60)
                heapq.heappush(events, (time + service_time, 'departure'))
            else:
                server_free = True
    
    return monitor.calculate_littles_law()

# Run simulation
results = simulate_coffee_shop()
print(f"Little's Law Verification:")
print(f"L (observed) = {results['L_observed']:.2f}")
print(f"λ × W = {results['λ']:.2f} × {results['W']:.2f} = {results['L_calculated']:.2f}")
print(f"Error: {results['error']:.2f}%")
```

<details>
<summary>Solution Insights</summary>

Little's Law holds with < 5% error in stable systems.

Key observations:
1. Works for any arrival distribution
2. Works for any service distribution  
3. Works for multi-server systems
4. Only requirement: system stability (λ < μ)

Real-world applications:
- Database connection pools: connections = arrival_rate × hold_time
- Thread pools: threads = request_rate × processing_time
- Cache sizing: entries = miss_rate × fetch_time
</details>

## Exercise 3: Capacity Planning

### 🔧 Try This: Design a System

```python
# Scenario: Design video streaming infrastructure
# Requirements:
# - 1M concurrent viewers
# - 1080p streams (5 Mbps each)
# - Global audience
# - 99.9% availability

def capacity_planner():
    # Your task: Calculate required infrastructure
    
    # Given constraints
    viewers = 1_000_000
    bitrate_mbps = 5
    availability_target = 0.999
    
    # Infrastructure limits
    server_bandwidth_gbps = 10
    server_connections = 10_000
    cdn_pop_bandwidth_gbps = 100
    region_count = 20
    
    # TODO: Calculate requirements
    # 1. Total bandwidth needed
    # 2. Number of origin servers  
    # 3. CDN capacity per region
    # 4. Redundancy factor for 99.9%
    
    total_bandwidth_gbps = 0  # Calculate this
    origin_servers = 0  # Calculate this
    cdn_pops_per_region = 0  # Calculate this
    redundancy_factor = 0  # Calculate this
    
    return {
        'total_bandwidth_gbps': total_bandwidth_gbps,
        'origin_servers': origin_servers,
        'cdn_pops_per_region': cdn_pops_per_region,
        'redundancy_factor': redundancy_factor,
        'total_cost_per_hour': 0  # Bonus: estimate cost
    }

# Implement your solution above
```

<details>
<summary>Solution</summary>

```python
def capacity_planner():
    # Given constraints
    viewers = 1_000_000
    bitrate_mbps = 5
    availability_target = 0.999
    
    # Infrastructure limits
    server_bandwidth_gbps = 10
    server_connections = 10_000
    cdn_pop_bandwidth_gbps = 100
    region_count = 20
    
    # 1. Total bandwidth needed
    total_bandwidth_gbps = (viewers * bitrate_mbps) / 1000
    # = 1M * 5 Mbps / 1000 = 5000 Gbps
    
    # 2. Number of origin servers (bandwidth limited)
    servers_for_bandwidth = total_bandwidth_gbps / server_bandwidth_gbps
    # = 5000 / 10 = 500 servers
    
    # But also check connection limit
    servers_for_connections = viewers / server_connections  
    # = 1M / 10K = 100 servers
    
    # Need maximum of both
    origin_servers = max(servers_for_bandwidth, servers_for_connections)
    # = 500 servers
    
    # 3. CDN capacity per region (assume even distribution)
    bandwidth_per_region = total_bandwidth_gbps / region_count
    # = 5000 / 20 = 250 Gbps per region
    
    cdn_pops_per_region = bandwidth_per_region / cdn_pop_bandwidth_gbps
    # = 250 / 100 = 2.5, round up to 3
    cdn_pops_per_region = 3
    
    # 4. Redundancy for 99.9% availability
    # For 99.9%, need to handle 1 failure
    # N+1 redundancy minimum
    redundancy_factor = 1.5  # 50% extra capacity
    
    # Adjust numbers for redundancy
    origin_servers = int(origin_servers * redundancy_factor)
    # = 500 * 1.5 = 750 servers
    
    # Cost estimation (rough)
    server_cost_per_hour = 1.0  # $1/hour per server
    bandwidth_cost_per_gbps_hour = 0.02  # $0.02/Gbps/hour
    
    total_cost_per_hour = (
        origin_servers * server_cost_per_hour +
        total_bandwidth_gbps * bandwidth_cost_per_gbps_hour
    )
    # = 750 * $1 + 5000 * $0.02 = $750 + $100 = $850/hour
    
    return {
        'total_bandwidth_gbps': total_bandwidth_gbps,
        'origin_servers': origin_servers,
        'cdn_pops_per_region': cdn_pops_per_region,
        'redundancy_factor': redundancy_factor,
        'total_cost_per_hour': total_cost_per_hour
    }

result = capacity_planner()
print(f"""
Video Streaming Capacity Plan:
- Total bandwidth: {result['total_bandwidth_gbps']} Gbps
- Origin servers: {result['origin_servers']}
- CDN PoPs per region: {result['cdn_pops_per_region']}  
- Redundancy factor: {result['redundancy_factor']}x
- Estimated cost: ${result['total_cost_per_hour']}/hour

Monthly cost: ${result['total_cost_per_hour'] * 24 * 30:,.0f}
""")
```

</details>

## Exercise 4: Queue Simulation

### 🔧 Try This: Compare Queue Disciplines

```python
import heapq
from collections import deque
import random

class QueueSimulator:
    def __init__(self, discipline='FIFO'):
        self.discipline = discipline
        self.queue = deque() if discipline == 'FIFO' else []
        self.completed = []
        self.dropped = []
        
    def enqueue(self, job):
        if self.discipline == 'FIFO':
            self.queue.append(job)
        elif self.discipline == 'LIFO':
            self.queue.append(job)
        elif self.discipline == 'Priority':
            heapq.heappush(self.queue, job)
            
    def dequeue(self):
        if not self.queue:
            return None
            
        if self.discipline == 'FIFO':
            return self.queue.popleft()
        elif self.discipline == 'LIFO':
            return self.queue.pop()
        elif self.discipline == 'Priority':
            return heapq.heappop(self.queue)

# Exercise: Compare different queue disciplines
def compare_disciplines():
    disciplines = ['FIFO', 'LIFO', 'Priority']
    results = {}
    
    for disc in disciplines:
        sim = QueueSimulator(disc)
        
        # Generate jobs with different priorities
        jobs = []
        for i in range(1000):
            arrival_time = i * 0.1  # 10 jobs/second
            priority = random.choice([1, 2, 3])  # 1=high
            processing_time = random.uniform(0.05, 0.2)
            
            job = {
                'id': i,
                'arrival': arrival_time,
                'priority': priority,
                'processing': processing_time
            }
            
            # For priority queue, use (priority, arrival, job)
            if disc == 'Priority':
                jobs.append((priority, arrival_time, job))
            else:
                jobs.append(job)
        
        # TODO: Simulate processing
        # - Track average wait time
        # - Track wait time by priority
        # - Track maximum wait time
        
        results[disc] = {
            'avg_wait': 0,  # Calculate this
            'max_wait': 0,  # Calculate this
            'priority_wait': {}  # Wait by priority
        }
    
    return results

# Implement the simulation logic
```

<details>
<summary>Solution</summary>

```python
def compare_disciplines():
    disciplines = ['FIFO', 'LIFO', 'Priority']
    results = {}
    
    for disc in disciplines:
        sim = QueueSimulator(disc)
        
        # Generate jobs
        jobs = []
        for i in range(1000):
            arrival_time = i * 0.1
            priority = random.choice([1, 2, 3])
            processing_time = random.uniform(0.05, 0.2)
            
            job = {
                'id': i,
                'arrival': arrival_time,
                'priority': priority,
                'processing': processing_time,
                'start': None,
                'end': None
            }
            
            if disc == 'Priority':
                jobs.append((priority, arrival_time, job))
            else:
                jobs.append(job)
        
        # Simulate processing
        current_time = 0
        server_free_at = 0
        completed = []
        
        job_index = 0
        
        while job_index < len(jobs) or sim.queue:
            # Enqueue all jobs that have arrived
            while job_index < len(jobs):
                if disc == 'Priority':
                    _, arrival, _ = jobs[job_index]
                else:
                    arrival = jobs[job_index]['arrival']
                    
                if arrival <= current_time:
                    sim.enqueue(jobs[job_index])
                    job_index += 1
                else:
                    break
            
            # Process next job if server is free
            if server_free_at <= current_time:
                next_job = sim.dequeue()
                if next_job:
                    if disc == 'Priority':
                        _, _, job = next_job
                    else:
                        job = next_job
                    
                    job['start'] = current_time
                    job['end'] = current_time + job['processing']
                    job['wait'] = job['start'] - job['arrival']
                    
                    server_free_at = job['end']
                    completed.append(job)
            
            # Advance time
            current_time += 0.01
            
            # Prevent infinite loop
            if current_time > 200:
                break
        
        # Calculate metrics
        wait_times = [j['wait'] for j in completed]
        avg_wait = sum(wait_times) / len(wait_times)
        max_wait = max(wait_times)
        
        # Wait time by priority
        priority_waits = {1: [], 2: [], 3: []}
        for job in completed:
            priority_waits[job['priority']].append(job['wait'])
        
        priority_avg = {}
        for p, waits in priority_waits.items():
            if waits:
                priority_avg[p] = sum(waits) / len(waits)
        
        results[disc] = {
            'avg_wait': avg_wait,
            'max_wait': max_wait,
            'priority_wait': priority_avg
        }
    
    # Display results
    print("Queue Discipline Comparison:\n")
    print(f"{'Discipline':<10} {'Avg Wait':<10} {'Max Wait':<10} {'P1 Wait':<10} {'P2 Wait':<10} {'P3 Wait':<10}")
    print("-" * 60)
    
    for disc, metrics in results.items():
        print(f"{disc:<10} {metrics['avg_wait']:<10.2f} {metrics['max_wait']:<10.2f}", end=" ")
        for p in [1, 2, 3]:
            wait = metrics['priority_wait'].get(p, 0)
            print(f"{wait:<10.2f}", end=" ")
        print()
    
    print("\nInsights:")
    print("- FIFO: Fair but high-priority jobs wait")
    print("- LIFO: Recent jobs served first, old jobs starve")  
    print("- Priority: High-priority jobs have low wait, but P3 starves")

compare_disciplines()
```

</details>

## Exercise 5: Autoscaling Design

### 🔧 Try This: Build an Autoscaler

```python
class Autoscaler:
    def __init__(self, min_instances=2, max_instances=100, 
                 target_cpu=70, scale_up_threshold=80,
                 scale_down_threshold=60):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.current_instances = min_instances
        self.cooldown_until = 0
        
    def decide(self, current_cpu, current_rps, current_time):
        """
        Decide whether to scale up, down, or maintain
        
        TODO: Implement scaling logic that:
        1. Scales up when CPU > scale_up_threshold
        2. Scales down when CPU < scale_down_threshold  
        3. Respects cooldown periods
        4. Predicts future load based on RPS trend
        5. Never exceeds min/max bounds
        """
        if current_time < self.cooldown_until:
            return self.current_instances
            
        # Your implementation here
        new_instances = self.current_instances
        
        return new_instances

# Test your autoscaler
def test_autoscaler():
    scaler = Autoscaler()
    
    # Simulate traffic pattern
    for hour in range(24):
        # Morning spike
        if 8 <= hour <= 10:
            rps = 1000 + hour * 100
        # Lunch spike  
        elif 12 <= hour <= 13:
            rps = 1500
        # Evening steady
        elif 17 <= hour <= 22:
            rps = 800
        # Night low
        else:
            rps = 200
            
        # CPU correlates with RPS
        cpu_per_instance = rps / scaler.current_instances * 0.1
        
        new_instances = scaler.decide(
            cpu_per_instance, 
            rps, 
            hour
        )
        
        print(f"Hour {hour:02d}: RPS={rps}, "
              f"CPU={cpu_per_instance:.1f}%, "
              f"Instances={new_instances}")
```

<details>
<summary>Solution</summary>

```python
class Autoscaler:
    def __init__(self, min_instances=2, max_instances=100, 
                 target_cpu=70, scale_up_threshold=80,
                 scale_down_threshold=60):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.current_instances = min_instances
        self.cooldown_until = 0
        self.cooldown_period = 5  # minutes
        self.rps_history = []
        
    def predict_future_load(self, current_rps):
        """Simple trend prediction"""
        self.rps_history.append(current_rps)
        if len(self.rps_history) > 3:
            self.rps_history.pop(0)
            
        if len(self.rps_history) < 2:
            return current_rps
            
        # Calculate trend
        trend = (self.rps_history[-1] - self.rps_history[0]) / len(self.rps_history)
        predicted_rps = current_rps + trend * 5  # 5 minute prediction
        
        return max(0, predicted_rps)
        
    def decide(self, current_cpu, current_rps, current_time):
        if current_time < self.cooldown_until:
            return self.current_instances
            
        predicted_rps = self.predict_future_load(current_rps)
        predicted_cpu = predicted_rps / self.current_instances * 0.1
        
        new_instances = self.current_instances
        
        # Scale up conditions
        if current_cpu > self.scale_up_threshold or predicted_cpu > self.scale_up_threshold:
            # Calculate instances needed for target CPU
            desired_instances = int(current_rps / (self.target_cpu * 10))
            
            # Scale up by 20% or to desired, whichever is larger
            scale_up_by = max(
                int(self.current_instances * 0.2),
                desired_instances - self.current_instances,
                1  # At least 1
            )
            
            new_instances = min(
                self.current_instances + scale_up_by,
                self.max_instances
            )
            
            if new_instances != self.current_instances:
                self.cooldown_until = current_time + self.cooldown_period
                print(f"  SCALE UP: {self.current_instances} → {new_instances}")
                
        # Scale down conditions
        elif current_cpu < self.scale_down_threshold and predicted_cpu < self.scale_down_threshold:
            # Only scale down if we've been low for a while
            if all(rps < current_rps * 1.2 for rps in self.rps_history):
                # Scale down by 10%
                scale_down_by = max(int(self.current_instances * 0.1), 1)
                
                new_instances = max(
                    self.current_instances - scale_down_by,
                    self.min_instances
                )
                
                if new_instances != self.current_instances:
                    self.cooldown_until = current_time + self.cooldown_period
                    print(f"  SCALE DOWN: {self.current_instances} → {new_instances}")
        
        self.current_instances = new_instances
        return new_instances

# Test with realistic pattern
def test_autoscaler():
    scaler = Autoscaler()
    
    print("Hour | RPS  | CPU  | Instances | Action")
    print("-" * 45)
    
    for minute in range(24 * 60):  # Full day simulation
        hour = minute / 60
        
        # More realistic traffic pattern with noise
        base_rps = 200
        if 8 <= hour <= 10:
            base_rps = 1000 + (hour - 8) * 500
        elif 12 <= hour <= 13:
            base_rps = 1500
        elif 17 <= hour <= 22:
            base_rps = 800
        elif 3 <= hour <= 5:
            base_rps = 100  # Maintenance window
            
        # Add some noise
        rps = int(base_rps + random.uniform(-50, 50))
        
        # CPU correlates with RPS
        cpu_per_instance = rps / scaler.current_instances * 0.1
        cpu_per_instance = min(100, cpu_per_instance)  # Cap at 100%
        
        new_instances = scaler.decide(
            cpu_per_instance, 
            rps, 
            minute
        )
        
        # Print every 30 minutes
        if minute % 30 == 0:
            print(f"{hour:04.1f} | {rps:4d} | {cpu_per_instance:4.1f} | {new_instances:9d} |")

test_autoscaler()
```

</details>

## Challenge Problems

### 1. The Connection Pool Optimizer 🎯

Design a dynamic connection pool that adjusts its size based on:
- Current usage patterns
- Response time targets
- Database load
- Cost constraints

### 2. The Global Load Balancer 🌍

Given:
- 5 regions with different costs
- Variable latencies between regions
- Time-based traffic patterns
- Capacity constraints per region

Design an algorithm that minimizes cost while maintaining SLAs.

### 3. The Cascade Preventer 🛡️

Build a system that detects and prevents cascade failures by:
- Monitoring resource utilization
- Predicting failure propagation
- Implementing automatic circuit breakers
- Graceful degradation

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Finding system breaking points
    - ✅ Applying Little's Law
    - ✅ Capacity planning with constraints
    - ✅ Queue discipline trade-offs
    - ✅ Autoscaling algorithms

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 3: Partial Failure](../axiom-3-failure/index.md) →
    
    **Back to**: [Capacity Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Tools](../../tools/capacity-planner.md) | [Part II](../../part2-pillars/index.md)