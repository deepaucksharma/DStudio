---
title: Latency Exercises
description: ""
type: axiom
difficulty: advanced
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 1](index.md) → **Latency Exercises**

# Latency Exercises

## 🧪 Hands-On Labs

### Lab 1: Measure Your Physics Tax
Use ping and traceroute to understand real-world latency.

### Speed of Light Calculator

Calculate theoretical minimum latency between two points:

```python
import math

def calculate_min_latency(distance_km):
    """Calculate minimum theoretical latency"""
    speed_of_light_km_ms = 300  # km/millisecond

    # One-way latency
    one_way = distance_km / speed_of_light_km_ms

    # Round-trip time
    rtt = one_way * 2

    # Add realistic overhead (routers, processing)
    # Typically 1.5-2x theoretical minimum
    realistic_rtt = rtt * 1.5

    return {
        'theoretical_one_way_ms': round(one_way, 2),
        'theoretical_rtt_ms': round(rtt, 2),
        'realistic_rtt_ms': round(realistic_rtt, 2)
    }

# Example: NYC to London
nyc_london_km = 5585
print(calculate_min_latency(nyc_london_km))
# Output: {'theoretical_one_way_ms': 18.62, 'theoretical_rtt_ms': 37.23, 'realistic_rtt_ms': 55.85}
```

### Lab 2: Build a Latency Budget

Create a latency budget for a sample application:

```python
class LatencyBudget:
    def __init__(self, total_budget_ms):
        self.total_budget = total_budget_ms
        self.allocations = {}
        self.remaining = total_budget_ms

    def allocate(self, component, latency_ms):
        """Allocate latency budget to component"""
        if latency_ms > self.remaining:
            raise ValueError(f"Insufficient budget: {latency_ms}ms requested, {self.remaining}ms available")

        self.allocations[component] = latency_ms
        self.remaining -= latency_ms

    def analyze(self):
        """Analyze budget allocation"""
        return {
            'total_budget': self.total_budget,
            'allocated': sum(self.allocations.values()),
            'remaining': self.remaining,
            'breakdown': self.allocations,
            'utilization': f"{(sum(self.allocations.values()) / self.total_budget) * 100:.1f}%"
        }

# Example: E-commerce checkout
budget = LatencyBudget(1000)  # 1 second total
budget.allocate('network_rtt', 50)
budget.allocate('load_balancer', 5)
budget.allocate('auth_service', 20)
budget.allocate('inventory_check', 30)
budget.allocate('payment_processing', 200)
budget.allocate('order_creation', 50)
budget.allocate('database_writes', 100)
budget.allocate('notification_service', 25)

print(budget.analyze())
```

### Lab 3: Network Latency Simulation

Simulate different network conditions:

```python
import time
import random
import asyncio

class NetworkSimulator:
    def __init__(self, base_latency_ms, jitter_ms, packet_loss_rate):
        self.base_latency = base_latency_ms / 1000  # Convert to seconds
        self.jitter = jitter_ms / 1000
        self.packet_loss_rate = packet_loss_rate

    async def simulate_request(self, data):
        """Simulate network request with latency and loss"""
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            raise Exception("Packet lost")

        # Calculate latency with jitter
        latency = self.base_latency + random.uniform(-self.jitter, self.jitter)

        # Simulate network delay
        await asyncio.sleep(latency)

        return f"Response for: {data}"

    async def benchmark(self, num_requests=100):
        """Benchmark network performance"""
        latencies = []
        failures = 0

        for i in range(num_requests):
            start = time.time()
            try:
                await self.simulate_request(f"Request {i}")
                latency = (time.time() - start) * 1000  # Convert to ms
                latencies.append(latency)
            except:
                failures += 1

        if latencies:
            return {
                'avg_latency_ms': sum(latencies) / len(latencies),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies),
                'packet_loss_rate': failures / num_requests,
                'successful_requests': len(latencies)
            }
        else:
            return {'error': 'All requests failed'}

# Example: Simulate different network conditions
async def test_networks():
    networks = {
        'local_datacenter': NetworkSimulator(1, 0.5, 0.0001),
        'cross_region': NetworkSimulator(50, 10, 0.001),
        'satellite': NetworkSimulator(600, 100, 0.01),
        'congested': NetworkSimulator(100, 50, 0.05)
    }

    for name, network in networks.items():
        print(f"\n{name}:")
        results = await network.benchmark()
        print(results)

# Run simulation
# asyncio.run(test_networks())
```

## 💻 Implementation Challenges

### Challenge 1: Multi-Region Load Balancer
Build a latency-aware load balancer that routes requests to the nearest healthy region.

### Challenge 2: Adaptive Timeout Calculator
Create a system that dynamically adjusts timeouts based on observed latency patterns.

### Challenge 3: Global Cache Warming
Design a cache warming strategy that respects latency budgets across regions.

## 🧮 Calculation Problems

### 1. The Latency Budget Crisis
**Scenario**: Your e-commerce site's checkout is failing SLA.

```python
# Current measurements:
components = {
    'user_to_cdn': 20,      # ms
    'cdn_to_lb': 5,         # ms
    'lb_to_api': 2,         # ms
    'api_processing': 50,   # ms
    'api_to_db': 10,        # ms
    'db_query': 150,        # ms
    'api_to_payment': 100,  # ms
    'payment_process': 200, # ms
    'response_path': 37     # ms (all return paths)
}

# SLA: 500ms P99
# Current P99: sum(components.values()) = ???
```

!!! task "Your Mission"
    1. Calculate current P99 latency
    2. You have $100k budget. Options:
       - Cache DB queries (saves 140ms, costs $30k)
       - Regional payment processor (saves 150ms, costs $80k)
       - Optimize API (saves 30ms, costs $50k)
       - Premium CDN (saves 15ms, costs $40k)
    3. What's the optimal combination to meet SLA?

### 2. The Global Gaming Challenge
**Problem**: Design server placement for a global FPS game.

```python
player_distribution = {
    'north_america': 5_000_000,
    'europe': 4_000_000,
    'asia_pacific': 8_000_000,
    'south_america': 2_000_000,
    'africa': 1_000_000
}

# Requirement: 90% of players < 50ms latency
# Budget: 10 data center locations
```

!!! challenge "Calculate"
    Using great circle distances and fiber optic speeds:
    1. Where do you place your 10 servers?
    2. What percentage of players meet the latency requirement?
    3. What's the minimum number of locations needed for 95% coverage?

### 3. The Distributed Lock Dilemma
**Setup**: 5-node cluster with measured latencies:

```text
    NODE1  NODE2  NODE3  NODE4  NODE5
N1    0     10     25     40     35
N2   10      0     15     30     25
N3   25     15      0     20     15
N4   40     30     20      0     10
N5   35     25     15     10      0
```

!!! problem "Analysis Required"
    For different consensus requirements:
    1. Majority quorum (3 nodes): What's the expected latency?
    2. Super-majority (4 nodes): What's the worst-case latency?
    3. If Node1 is the leader, which followers minimize commit latency?
    4. Where should you place the leader to minimize average case?

## 🤔 Thought Experiments

### 1. Mars Colony System
**Challenge**: Design a distributed system architecture that works across Earth and Mars with 14-24 minute one-way latency.

!!! question "Consider These Constraints"
    - No real-time communication possible
    - All interactions must be asynchronous
    - Local autonomy is mandatory
    - How do you handle:
      - Authentication across planets?
      - Data consistency?
      - Software updates?
      - Emergency protocols?

**Hint**: Think about how Git works offline and syncs later. What other systems work this way?

### 2. The Speed of Light Bankruptcy
**Scenario**: Your high-frequency trading firm discovers a competitor has a faster link between exchanges.

!!! exercise "Business Impact Analysis"
    Given:
    - Your latency: NYC ↔ Chicago = 7.5ms
    - Competitor's new microwave link: 6.8ms
    - Average trade opportunity window: 2ms
    - Your current profit: $10M/month

    Questions:
    1. What percentage of trades will you now lose?
    2. What's the maximum you should pay for a matching link?
    3. Are there alternative strategies besides speed?

### 3. The Streaming Service Dilemma
**Your Task**: Netflix wants to stream to Antarctica research station (2000 people).

!!! challenge "Design Decisions"
    Constraints:
    - Satellite link only: 600ms latency, 100Mbps total
    - -40°C affects equipment
    - Limited technical staff on-site
    - Power is extremely expensive

    Design a system that provides good user experience despite these constraints.
    Consider: Caching strategy, Update mechanism, Failure handling, Content prioritization

## 🔬 Research Projects

### 1. The Great Latency Hunt
**Project**: Profile a real distributed application

!!! lab "Hands-On Investigation"
    Tools needed: Wireshark, traceroute, dig, curl

    Pick a service (e.g., gmail.com) and measure:
    1. DNS resolution time
    2. TCP handshake duration
    3. TLS negotiation overhead
    4. Time to first byte
    5. Total page load time

    Create a detailed breakdown showing where time is spent.
    Bonus: Compare HTTP/2 vs HTTP/3 performance

### 2. Build Your Own CDN
**Project**: Implement a micro-CDN with latency-based routing

```python
# Starter code
class MicroCDN:
    def __init__(self):
        self.edges = {}  # location -> EdgeServer
        self.latency_map = {}  # (src, dst) -> latency_ms

    def add_edge(self, location, capacity):
        """Add an edge server"""
        pass

    def route_request(self, client_location, content_id):
        """Find optimal edge for client"""
        # TODO: Implement latency-aware routing
        # Consider: Cache hits, Server load, Network distance
        pass

    def simulate_day(self, request_pattern):
        """Simulate 24 hours of traffic"""
        # TODO: Calculate cache hit rates, Average latency, Cost
        pass
```

!!! challenge "Requirements"
    - Support 10 edge locations
    - Handle 1M requests/day
    - Optimize for <50ms P95 latency
    - Minimize bandwidth costs
    - Implement cache warming strategy

### 3. The Time Travel Debugger
**Advanced Project**: Build a distributed system debugger that accounts for latency

!!! info "The Problem"
    In distributed systems, events that appear simultaneous might not be.
    Build a tool that:
    1. Collects events from multiple nodes
    2. Accounts for clock skew and network latency
    3. Reconstructs true event ordering
    4. Visualizes causality chains

    Use Lamport timestamps or vector clocks.
    Test with a simulated distributed system with artificial delays.

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 2](../axiom2-capacity/index.md)

**Related**: [Timeout](../../patterns/timeout.md) • [Circuit Breaker](../../patterns/circuit-breaker.md) • [Caching Strategies](../../patterns/caching-strategies.md)
