# Latency Exercises

!!! info "Prerequisites"
    - [Axiom 1: Latency Core Concepts](index.md)
    - [Latency Examples](examples.md)
    - Basic programming knowledge

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Latency Home](index.md) |
    [→ Next Axiom](../axiom-2-capacity/index.md)

## Exercise 1: Calculate Minimum Latency

### 🔧 Try This: Geographic Latency Calculator

```python
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth"""
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def minimum_latency_ms(lat1, lon1, lat2, lon2):
    """Calculate theoretical minimum latency between two coordinates"""
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)
    SPEED_OF_LIGHT_FIBER = 200_000  # km/s
    return (distance_km / SPEED_OF_LIGHT_FIBER) * 1000

# Exercise: Calculate latency between major cities
cities = {
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "São Paulo": (-23.5505, -46.6333),
    "Mumbai": (19.0760, 72.8777),
}

# TODO: Calculate minimum latency between all city pairs
# Expected output format:
# New York ↔ London: 27.8ms minimum
```

<details>
<summary>Solution</summary>

```python
# Solution
for city1, coords1 in cities.items():
    for city2, coords2 in cities.items():
        if city1 < city2:  # Avoid duplicates
            latency = minimum_latency_ms(coords1[0], coords1[1], 
                                        coords2[0], coords2[1])
            print(f"{city1} ↔ {city2}: {latency:.1f}ms minimum")

# Output:
# London ↔ New York: 27.8ms minimum
# London ↔ São Paulo: 48.1ms minimum
# London ↔ Sydney: 84.9ms minimum
# London ↔ Tokyo: 47.6ms minimum
# Mumbai ↔ New York: 60.5ms minimum
# Mumbai ↔ São Paulo: 72.9ms minimum
# Mumbai ↔ Sydney: 50.3ms minimum
# Mumbai ↔ Tokyo: 29.6ms minimum
# New York ↔ São Paulo: 38.2ms minimum
# New York ↔ Sydney: 79.8ms minimum
# New York ↔ Tokyo: 54.2ms minimum
# Sydney ↔ São Paulo: 82.0ms minimum
# Sydney ↔ Tokyo: 38.6ms minimum
# São Paulo ↔ Tokyo: 92.4ms minimum
```

</details>

## Exercise 2: Latency Budget Analysis

### 🔧 Try This: Budget Your Application

```python
class LatencyBudget:
    def __init__(self, total_budget_ms):
        self.total_budget = total_budget_ms
        self.spent = 0
        self.operations = []
    
    def add_operation(self, name, latency_ms):
        self.operations.append((name, latency_ms))
        self.spent += latency_ms
        remaining = self.total_budget - self.spent
        
        status = "✓" if remaining >= 0 else "✗"
        print(f"{status} {name}: {latency_ms}ms (Remaining: {remaining}ms)")
        
        return remaining
    
    def analyze(self):
        print(f"\n{'='*50}")
        print(f"Total Budget: {self.total_budget}ms")
        print(f"Total Spent: {self.spent}ms")
        print(f"Margin: {self.total_budget - self.spent}ms")
        
        if self.spent > self.total_budget:
            print(f"⚠️  OVER BUDGET by {self.spent - self.total_budget}ms!")
            print("\nOptimization suggestions:")
            # Sort by latency to find biggest contributors
            sorted_ops = sorted(self.operations, key=lambda x: x[1], reverse=True)
            for name, latency in sorted_ops[:3]:
                print(f"  - Optimize '{name}' (currently {latency}ms)")

# Exercise: Budget a typical e-commerce checkout flow
# Goal: Keep under 1000ms for good user experience

budget = LatencyBudget(1000)

# TODO: Add realistic operations for checkout
# Consider: page load, auth check, inventory check, 
# payment processing, order creation, email notification

# Example start:
budget.add_operation("Page render", 50)
# Add more operations...
```

<details>
<summary>Solution</summary>

```python
# Realistic checkout flow
budget = LatencyBudget(1000)

# Frontend operations
budget.add_operation("Page render", 50)
budget.add_operation("Form validation", 10)

# API calls (assuming 30ms RTT to servers)
budget.add_operation("Auth token validation", 35)
budget.add_operation("Load user profile", 45)
budget.add_operation("Fetch cart contents", 40)
budget.add_operation("Validate inventory (3 items)", 120)  # 40ms each
budget.add_operation("Calculate shipping", 60)
budget.add_operation("Calculate taxes", 55)
budget.add_operation("Payment authorization", 250)  # External API
budget.add_operation("Create order record", 80)
budget.add_operation("Update inventory", 90)
budget.add_operation("Queue email notification", 25)  # Async
budget.add_operation("Return confirmation", 30)

budget.analyze()

# Optimization strategies:
# 1. Parallel inventory checks: 120ms → 40ms
# 2. Cache user profile: 45ms → 5ms  
# 3. Pre-calculate shipping: 60ms → 10ms
# 4. Batch inventory + order: 170ms → 100ms
```

</details>

## Exercise 3: Implement a Latency-Aware Cache

### 🔧 Try This: Smart Geographic Cache

```python
import time
import random
from datetime import datetime, timedelta

class GeoCache:
    def __init__(self):
        self.cache = {}
        self.latency_map = {
            'local': 1,      # Same datacenter
            'regional': 20,  # Same region
            'global': 100,   # Cross-region
        }
    
    def get(self, key, user_location='local'):
        # TODO: Implement cache retrieval with simulated latency
        # - Check if key exists
        # - Simulate network latency based on location
        # - Track cache hits/misses
        # - Implement TTL expiration
        pass
    
    def set(self, key, value, ttl_seconds=300):
        # TODO: Implement cache setting with TTL
        pass
    
    def get_with_fallback(self, key, fetch_func, user_location='local'):
        # TODO: Implement cache-aside pattern
        # - Try cache first
        # - On miss, call fetch_func
        # - Cache the result
        # - Return value with total latency
        pass

# Exercise: Implement and test the cache
cache = GeoCache()

def slow_database_fetch(key):
    """Simulates a slow database query"""
    time.sleep(0.2)  # 200ms database latency
    return f"Data for {key}"

# Test scenarios:
# 1. First request (cache miss)
# 2. Second request (cache hit)
# 3. Request from different region
# 4. Request after TTL expiration
```

<details>
<summary>Solution</summary>

```python
class GeoCache:
    def __init__(self):
        self.cache = {}
        self.latency_map = {
            'local': 1,
            'regional': 20,
            'global': 100,
        }
        self.stats = {'hits': 0, 'misses': 0}
    
    def _simulate_latency(self, location):
        """Simulate network latency"""
        latency_ms = self.latency_map.get(location, 100)
        time.sleep(latency_ms / 1000)
        return latency_ms
    
    def get(self, key, user_location='local'):
        start_time = time.time()
        
        # Simulate network latency to cache
        network_ms = self._simulate_latency(user_location)
        
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                self.stats['hits'] += 1
                total_ms = (time.time() - start_time) * 1000
                print(f"Cache HIT: {key} ({total_ms:.1f}ms total, {network_ms}ms network)")
                return value
            else:
                # Expired
                del self.cache[key]
        
        self.stats['misses'] += 1
        total_ms = (time.time() - start_time) * 1000
        print(f"Cache MISS: {key} ({total_ms:.1f}ms total)")
        return None
    
    def set(self, key, value, ttl_seconds=300):
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self.cache[key] = (value, expiry)
    
    def get_with_fallback(self, key, fetch_func, user_location='local'):
        start_time = time.time()
        
        # Try cache first
        cached = self.get(key, user_location)
        if cached is not None:
            return cached
        
        # Cache miss - fetch from source
        print(f"Fetching {key} from source...")
        value = fetch_func(key)
        
        # Cache for future requests
        self.set(key, value)
        
        total_ms = (time.time() - start_time) * 1000
        print(f"Total latency: {total_ms:.1f}ms")
        print(f"Cache stats: {self.stats}")
        
        return value

# Test the implementation
cache = GeoCache()

print("Test 1: First request (cache miss)")
result1 = cache.get_with_fallback('user:123', slow_database_fetch, 'local')

print("\nTest 2: Second request (cache hit)")
result2 = cache.get_with_fallback('user:123', slow_database_fetch, 'local')

print("\nTest 3: Request from different region")
result3 = cache.get_with_fallback('user:123', slow_database_fetch, 'global')

print("\nTest 4: Different key")
result4 = cache.get_with_fallback('user:456', slow_database_fetch, 'regional')

# Advanced: Implement cache warming for predicted keys
def warm_cache(cache, keys, fetch_func):
    """Pre-populate cache with likely-needed keys"""
    for key in keys:
        if cache.get(key) is None:
            value = fetch_func(key)
            cache.set(key, value)
            print(f"Pre-warmed cache with {key}")

# Warm cache with likely keys
likely_keys = ['user:789', 'user:101', 'user:202']
warm_cache(cache, likely_keys, slow_database_fetch)
```

</details>

## Exercise 4: Measure Real-World Latency

### 🔧 Try This: Build a Latency Monitor

```bash
#!/bin/bash
# Exercise: Create a latency monitoring script

# TODO: Implement a script that:
# 1. Measures latency to multiple endpoints
# 2. Calculates percentiles (p50, p95, p99)
# 3. Detects latency anomalies
# 4. Generates a report

# Skeleton:
measure_latency() {
    local host=$1
    local count=$2
    # Your implementation here
}

calculate_percentiles() {
    local latencies=($@)
    # Your implementation here
}

# Test with these hosts:
hosts=(
    "google.com"
    "amazon.com"
    "cloudflare.com"
    "8.8.8.8"
)
```

<details>
<summary>Solution</summary>

```bash
#!/bin/bash

# Latency monitoring script
measure_latency() {
    local host=$1
    local count=$2
    local latencies=()
    
    echo "Measuring latency to $host..."
    
    for i in $(seq 1 $count); do
        # Extract time from ping
        result=$(ping -c 1 -W 2 $host 2>/dev/null | grep 'time=' | sed 's/.*time=\([0-9.]*\).*/\1/')
        
        if [ ! -z "$result" ]; then
            latencies+=($result)
            echo -n "."
        else
            echo -n "X"
        fi
    done
    echo
    
    echo "${latencies[@]}"
}

calculate_percentiles() {
    local values=($@)
    local count=${#values[@]}
    
    if [ $count -eq 0 ]; then
        echo "No data"
        return
    fi
    
    # Sort the array
    IFS=$'\n' sorted=($(sort -n <<<"${values[*]}"))
    unset IFS
    
    # Calculate indices
    local p50_idx=$((count * 50 / 100))
    local p95_idx=$((count * 95 / 100))
    local p99_idx=$((count * 99 / 100))
    
    # Ensure indices are valid
    [ $p50_idx -ge $count ] && p50_idx=$((count - 1))
    [ $p95_idx -ge $count ] && p95_idx=$((count - 1))
    [ $p99_idx -ge $count ] && p99_idx=$((count - 1))
    
    echo "Results for $count samples:"
    echo "  Min: ${sorted[0]}ms"
    echo "  P50: ${sorted[$p50_idx]}ms"
    echo "  P95: ${sorted[$p95_idx]}ms"
    echo "  P99: ${sorted[$p99_idx]}ms"
    echo "  Max: ${sorted[$((count-1))]}ms"
}

# Main monitoring loop
hosts=(
    "google.com"
    "amazon.com"
    "cloudflare.com"
    "8.8.8.8"
)

echo "Latency Monitoring Report"
echo "========================"
echo "Timestamp: $(date)"
echo

for host in "${hosts[@]}"; do
    echo "Host: $host"
    latencies=$(measure_latency $host 20)
    calculate_percentiles $latencies
    echo
done

# Advanced: Detect anomalies
detect_anomalies() {
    local values=($@)
    local count=${#values[@]}
    
    if [ $count -lt 10 ]; then
        return
    fi
    
    # Calculate mean
    local sum=0
    for val in "${values[@]}"; do
        sum=$(echo "$sum + $val" | bc)
    done
    local mean=$(echo "scale=2; $sum / $count" | bc)
    
    # Find outliers (> 2x mean)
    echo "Anomaly Detection:"
    for i in "${!values[@]}"; do
        if (( $(echo "${values[$i]} > $mean * 2" | bc -l) )); then
            echo "  WARNING: Sample $((i+1)) = ${values[$i]}ms ($(echo "scale=1; ${values[$i]} / $mean" | bc)x mean)"
        fi
    done
}

# Example with anomaly detection
echo "Detailed Analysis for google.com:"
latencies=($(measure_latency "google.com" 50))
calculate_percentiles "${latencies[@]}"
detect_anomalies "${latencies[@]}"
```

</details>

## Exercise 5: Design Exercise - Global Service

### 🔧 Try This: Architecture Planning

```markdown
# Exercise: Design a globally distributed video conferencing system

## Requirements:
- Maximum 150ms latency for good conversation flow
- Support users worldwide
- 99.9% availability
- Minimize infrastructure cost

## Your Task:
1. Calculate minimum number of regions needed
2. Determine optimal placement
3. Design fallback strategy
4. Estimate costs

## Constraints:
- Each region costs $50K/month
- Inter-region bandwidth: $0.02/GB
- Users generate 1GB/hour of video
- 24-hour usage pattern (follow the sun)

## Deliverables:
- [ ] Region placement map
- [ ] Latency matrix between regions
- [ ] Cost analysis
- [ ] Failure scenarios
```

<details>
<summary>Solution Approach</summary>

```python
# Solution: Global Video Conferencing Architecture

# Step 1: Calculate coverage for 150ms RTT (75ms one-way)
# At 200,000 km/s in fiber, 75ms = 15,000km radius

regions = {
    'us-east': {'lat': 39.0458, 'lon': -77.6413, 'cost': 50000},
    'us-west': {'lat': 37.4419, 'lon': -122.1430, 'cost': 50000},
    'eu-west': {'lat': 50.1109, 'lon': 8.6821, 'cost': 50000},
    'asia-northeast': {'lat': 35.6762, 'lon': 139.6503, 'cost': 50000},
    'asia-southeast': {'lat': 1.3521, 'lon': 103.8198, 'cost': 50000},
    'south-america': {'lat': -23.5505, 'lon': -46.6333, 'cost': 50000},
    'australia': {'lat': -33.8688, 'lon': 151.2093, 'cost': 50000},
}

# Step 2: Build latency matrix
def can_reach_in_time(region1, region2, max_ms=75):
    """Check if regions can communicate within latency budget"""
    lat1, lon1 = regions[region1]['lat'], regions[region1]['lon']
    lat2, lon2 = regions[region2]['lat'], regions[region2]['lon']
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)
    latency_ms = (distance_km / 200_000) * 1000
    return latency_ms <= max_ms

# Step 3: Minimum set cover problem
# Need to ensure every region can reach at least 2 others within 75ms
# This provides redundancy and global coverage

selected_regions = ['us-east', 'eu-west', 'asia-northeast', 'asia-southeast']

# Step 4: Cost analysis
base_cost = len(selected_regions) * 50000  # $200K/month

# Traffic patterns (follow the sun)
traffic_pattern = {
    '00-08': 'asia',      # Asia prime time
    '08-16': 'europe',    # Europe prime time  
    '16-24': 'americas',  # Americas prime time
}

# Bandwidth costs
# Assume 30% of traffic is inter-region
inter_region_gb_per_month = 1000000 * 0.3  # 1M users, 1GB/hour, 30% cross-region
bandwidth_cost = inter_region_gb_per_month * 0.02  # $6K/month

total_monthly_cost = base_cost + bandwidth_cost  # $206K/month

# Step 5: Failure scenarios
print("Failure Analysis:")
print("- Single region failure: Users route to next closest (max 150ms)")
print("- Network partition: Each partition continues operating independently")
print("- Cascading failure prevention: Rate limit inter-region traffic")

# Step 6: Optimization opportunities
print("\nOptimizations:")
print("1. Use anycast for automatic routing")
print("2. Place TURN servers at edge locations")
print("3. Implement SFU (Selective Forwarding Unit) to reduce bandwidth")
print("4. Use WebRTC for peer-to-peer when possible")
```

</details>

## Challenge Problems

### 1. The Speed of Light Detective 🔍

Given only ping times between servers, can you determine their geographic locations?

```python
# You have these RTT measurements (in ms):
measurements = {
    ('A', 'B'): 40,
    ('A', 'C'): 100,
    ('A', 'D'): 140,
    ('B', 'C'): 120,
    ('B', 'D'): 160,
    ('C', 'D'): 80,
}

# Challenge: Determine relative positions of servers A, B, C, D
# Hint: Use trilateration
```

### 2. The Optimal Cache Placement Problem 🎯

```python
# You have a budget for 3 cache servers
# User distribution and their coordinates:
users = {
    'NYC': {'count': 1000000, 'lat': 40.7, 'lon': -74.0},
    'LA': {'count': 800000, 'lat': 34.0, 'lon': -118.2},
    'Chicago': {'count': 500000, 'lat': 41.8, 'lon': -87.6},
    'Houston': {'count': 400000, 'lat': 29.7, 'lon': -95.3},
    'Phoenix': {'count': 300000, 'lat': 33.4, 'lon': -112.0},
}

# Where should you place the 3 caches to minimize average latency?
```

### 3. The Time Zone Arbitrage Problem ⏰

Design a system that processes batch jobs by following the sun to minimize latency and cost.

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Calculating theoretical minimum latencies
    - ✅ Building latency budgets
    - ✅ Implementing geographic caching
    - ✅ Measuring real-world latencies
    - ✅ Designing global architectures

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 2: Finite Capacity](../axiom-2-capacity/index.md) →
    
    **Back to**: [Latency Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Tools](../../tools/latency-calculator.md) | [Part II](../../part2-pillars/index.md)