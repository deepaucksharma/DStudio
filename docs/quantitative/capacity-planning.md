---
title: Capacity Planning Worksheet
description: "Systematic approach to planning infrastructure capacity using mathematical models and real-world usage patterns"
type: quantitative
difficulty: beginner
reading_time: 45 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part IV: Quantitative](index.md) → **Capacity Planning Worksheet**

# Capacity Planning Worksheet

**Right-sizing for the future**

## Capacity Planning Framework

### Step 1: Baseline Measurement
```python
Current State:
- Peak traffic: _______ requests/second
- Average traffic: _______ requests/second
- Storage used: _______ GB
- Growth rate: _______% monthly

Resource Usage at Peak:
- CPU: _______%
- Memory: _______%
- Network: _______ Mbps
- Disk I/O: _______ IOPS
```

### Step 2: Growth Projection
```python
Linear Growth:
Future = Current × (1 + monthly_rate × months)

Exponential Growth:
Future = Current × (1 + monthly_rate)^months

S-Curve Growth:
Future = Capacity / (1 + e^(-k×(t-t0)))
```

### Step 3: Safety Margins
```python
Component          Margin    Reason
---------          ------    ------
CPU                40%       Burst handling
Memory             30%       GC headroom
Network            50%       DDoS/spikes
Storage            50%       Log growth
Database Conn      30%       Connection storms
```

## Workload Characterization

### Traffic Patterns
```python
Daily Pattern:
- Peak hour: _____ (e.g., 2 PM)
- Peak/average ratio: _____ (e.g., 3x)
- Weekend factor: _____ (e.g., 0.6x)

Seasonal Pattern:
- Black Friday: _____x normal
- Holiday season: _____x normal
- Summer lull: _____x normal
```

### Request Mix
```python
Operation         % of Traffic    Resource Impact
---------         ------------    ---------------
Read (cached)     60%            Low
Read (DB)         20%            Medium
Write             15%            High
Analytics         5%             Very High

Weighted resource usage:
0.6×1 + 0.2×3 + 0.15×5 + 0.05×10 = 2.45 units/request
```

## Scaling Strategies

### Vertical vs Horizontal
```text
Vertical (Bigger boxes):
Current: 8 CPU, 32GB RAM
Next: 16 CPU, 64GB RAM
Cost: 2.2x (not linear!)
Limit: 96 CPU, 768GB RAM

Horizontal (More boxes):
Current: 10 × small instances
Next: 15 × small instances
Cost: 1.5x (linear)
Limit: Practically unlimited
```

### Resource Planning Table
```bash
Month    Traffic    CPU Need    Instances    Cost
-----    -------    --------    ---------    ----
0        1000 rps   800 cores   100          $10k
3        1500 rps   1200 cores  150          $15k
6        2250 rps   1800 cores  225          $22k
12       5000 rps   4000 cores  500          $50k

Decision point: Month 6 - need architecture change
```

## Capacity Planning Tools

### Little's Law Application
```python
Concurrent users = Requests/sec × Session duration
Database connections = Queries/sec × Query time
Memory needed = Objects/sec × Object lifetime × Size
```

### Queue Theory Application
```python
If utilization > 70%:
  Response time increases exponentially
  Plan for maximum 70% steady state

Servers needed = Load / (Capacity × 0.7)
```

## Real Example: E-Commerce Platform

### Current Baseline
```python
- 10,000 concurrent users
- 100 requests/second average
- 300 requests/second peak
- 50GB database
- 1TB object storage
```

### Growth Assumptions
```python
- User growth: 20% monthly
- Data growth: 30% monthly
- Feature complexity: +10% resources
```

### 6-Month Projection
```python
Users: 10,000 × 1.2^6 = 30,000
Requests: 300 × 3 = 900 peak
Database: 50 × 1.3^6 = 230GB
Storage: 1 × 1.3^6 = 4.6TB

Required Infrastructure:
- App servers: 10 → 30
- Database: Needs sharding
- Cache: 10GB → 50GB
- CDN: Essential
```

## Detailed Capacity Models

### CPU Capacity Planning
```python
def calculate_cpu_needs(current_load, growth_rate, months):
    future_load = current_load * ((1 + growth_rate) ** months)

    # Account for:
    # - Base OS overhead: 10%
    # - Safety margin: 40%
    # - Peak factor: 3x

    average_cpu = future_load * cpu_per_request
    peak_cpu = average_cpu * 3
    total_cpu = peak_cpu / 0.5  # 50% target utilization

    return total_cpu
```

### Memory Capacity Planning
```python
def calculate_memory_needs():
    # Static components
    os_memory = 2  # GB
    app_runtime = 4  # GB

    # Dynamic components
    connection_pool = connections * 10  # MB per connection
    cache_size = hot_data_size * 1.2  # 20% overhead
    session_storage = concurrent_users * session_size

    # Safety margins
    gc_headroom = total * 0.3

    return sum([os_memory, app_runtime, connection_pool,
                cache_size, session_storage, gc_headroom])
```

### Storage Capacity Planning
```python
def calculate_storage_needs():
    # Data growth projection
    data_growth = compound_growth(current_data, rate, time)

    # Log storage (often overlooked)
    log_size = requests_per_day * log_entry_size * retention_days

    # Backup storage
    backup_size = data_size * backup_generations

    # Indexes and overhead
    index_size = data_size * 0.3  # 30% typical

    # Future margin
    margin = total * 0.5  # 50% headroom

    return sum([data_growth, log_size, backup_size,
                index_size, margin])
```

## Capacity Planning by Service Type

### Web Application
```redis
Capacity factors:
- Request rate
- Response size
- Session duration
- Static asset ratio

Rules of thumb:
- 1 CPU core: ~100 req/s simple pages
- 1 GB RAM: ~500 concurrent sessions
- Network: 10 Mbps per 100 req/s
```

### API Service
```python
Capacity factors:
- Call rate
- Payload size
- Processing complexity
- External dependencies

Rules of thumb:
- 1 CPU core: ~1000 req/s simple JSON
- 1 GB RAM: ~10k connections
- Network: Response size × req/s × 8
```

### Database
```redis
Capacity factors:
- Query complexity
- Data size
- Index size
- Connection count

Rules of thumb:
- 1 CPU: ~1000 simple queries/s
- RAM: Working set + indexes
- Storage: Data × 3 (data + indexes + backups)
```

### Message Queue
```proto
Capacity factors:
- Message rate
- Message size
- Retention period
- Consumer count

Rules of thumb:
- 1 CPU: ~10k messages/s
- RAM: In-flight messages
- Storage: Rate × size × retention
```

## Capacity Triggers

### Scaling Triggers
```python
Immediate action required:
- CPU > 80% sustained
- Memory > 90%
- Storage > 80%
- Network > 70%
- Error rate > 1%

Planning required:
- 3-month projection hits limit
- Growth rate accelerating
- New feature launch
- Regional expansion
```

### Architecture Change Triggers
```python
Consider architecture change when:
- Vertical scaling hits limit
- Costs growing super-linearly
- Availability requirements increase
- Geographic expansion needed
- Performance degrading
```

## Capacity Planning Checklist

```redis
□ Current metrics collected
□ Growth rates calculated
□ Peak patterns identified
□ Resource limits known
□ Scaling triggers defined
□ Budget approved
□ Architecture reviewed
□ Runbooks updated
□ Team trained
□ Vendors notified
```

## Common Mistakes

1. **Using average instead of peak**
   - Systems fail at peak, not average
   - Plan for 95th percentile

2. **Forgetting hidden resources**
   - File descriptors
   - Thread pools
   - Kernel buffers

3. **Linear growth assumptions**
   - Viral growth happens
   - Plan for exponential

4. **Ignoring batch jobs**
   - Overnight batches affect capacity
   - Include in planning

5. **Not testing limits**
   - Load test to find real limits
   - Don't trust specifications

## Key Takeaways

1. **Measure everything** - You can't plan without data
2. **Plan for peaks** - Average is misleading
3. **Include safety margins** - Things go wrong
4. **Monitor growth rate changes** - Inflection points matter
5. **Test scaling assumptions** - Reality differs from theory

Remember: Capacity planning is continuous. Set up monitoring, define triggers, and review regularly.
