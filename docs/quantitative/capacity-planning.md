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


# Capacity Planning Worksheet

**Right-sizing for the future**

## Capacity Planning Framework

### Step 1: Baseline Measurement
<div class="law-box">
<h4>📏 Current State Assessment</h4>

<div class="measurement-form" style="background: #F3E5F5; padding: 20px; border-radius: 5px;">
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
    <div>
      <strong>Traffic Metrics:</strong>
      <table style="width: 100%; margin-top: 10px;">
        <tr><td>Peak traffic:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>req/s</td></tr>
        <tr><td>Average traffic:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>req/s</td></tr>
        <tr><td>Peak/Average ratio:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>x</td></tr>
      </table>
    </div>
    <div>
      <strong>Growth & Storage:</strong>
      <table style="width: 100%; margin-top: 10px;">
        <tr><td>Storage used:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>GB</td></tr>
        <tr><td>Growth rate:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>% monthly</td></tr>
        <tr><td>Retention:</td><td style="border-bottom: 1px solid #999; text-align: center;">_______</td><td>days</td></tr>
      </table>
    </div>
  </div>
  
  <div style="margin-top: 20px;">
    <strong>Resource Usage at Peak:</strong>
    <svg viewBox="0 0 500 200" style="width: 100%; max-width: 500px; margin-top: 10px;">
      <!-- CPU gauge -->
      <g transform="translate(50, 50)">
        <text x="50" y="-10" text-anchor="middle" font-weight="bold">CPU</text>
        <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
        <rect x="0" y="0" width="0" height="30" fill="#4CAF50" rx="3" id="cpu-bar"/>
        <text x="50" y="50" text-anchor="middle" style="border-bottom: 1px solid #999;">_____%</text>
      </g>
      
      <!-- Memory gauge -->
      <g transform="translate(200, 50)">
        <text x="50" y="-10" text-anchor="middle" font-weight="bold">Memory</text>
        <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
        <rect x="0" y="0" width="0" height="30" fill="#2196F3" rx="3" id="mem-bar"/>
        <text x="50" y="50" text-anchor="middle" style="border-bottom: 1px solid #999;">_____%</text>
      </g>
      
      <!-- Network gauge -->
      <g transform="translate(350, 50)">
        <text x="50" y="-10" text-anchor="middle" font-weight="bold">Network</text>
        <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
        <rect x="0" y="0" width="0" height="30" fill="#FF9800" rx="3" id="net-bar"/>
        <text x="50" y="50" text-anchor="middle" style="border-bottom: 1px solid #999;">_____ Mbps</text>
      </g>
      
      <!-- Disk I/O gauge -->
      <g transform="translate(125, 120)">
        <text x="50" y="-10" text-anchor="middle" font-weight="bold">Disk I/O</text>
        <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
        <rect x="0" y="0" width="0" height="30" fill="#9C27B0" rx="3" id="disk-bar"/>
        <text x="50" y="50" text-anchor="middle" style="border-bottom: 1px solid #999;">_____ IOPS</text>
      </g>
    </svg>
  </div>
</div>
</div>

### Step 2: Growth Projection
<div class="decision-box">
<h4>📈 Growth Model Selection</h4>

<div class="growth-models" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 15px 0;">
  <div style="background: #E8F5E9; padding: 15px; border-radius: 5px;">
    <h5 style="margin: 0;">Linear Growth</h5>
    <div style="text-align: center; margin: 10px 0;">
      <span style="font-size: 1.2em; color: #4CAF50;">Future = Current × (1 + rate × months)</span>
    </div>
    <svg viewBox="0 0 150 100" style="width: 100%;">
      <line x1="10" y1="80" x2="140" y2="20" stroke="#4CAF50" stroke-width="3"/>
      <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
      <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
    </svg>
    <p style="font-size: 0.9em; margin: 5px 0;">Steady, predictable growth</p>
  </div>
  
  <div style="background: #FFF3E0; padding: 15px; border-radius: 5px;">
    <h5 style="margin: 0;">Exponential Growth</h5>
    <div style="text-align: center; margin: 10px 0;">
      <span style="font-size: 1.2em; color: #FF9800;">Future = Current × (1 + rate)^months</span>
    </div>
    <svg viewBox="0 0 150 100" style="width: 100%;">
      <path d="M 10,80 Q 50,75 140,20" stroke="#FF9800" stroke-width="3" fill="none"/>
      <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
      <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
    </svg>
    <p style="font-size: 0.9em; margin: 5px 0;">Viral/compound growth</p>
  </div>
  
  <div style="background: #E3F2FD; padding: 15px; border-radius: 5px;">
    <h5 style="margin: 0;">S-Curve Growth</h5>
    <div style="text-align: center; margin: 10px 0;">
      <span style="font-size: 1.2em; color: #2196F3;">Future = Cap / (1 + e^(-k×(t-t0)))</span>
    </div>
    <svg viewBox="0 0 150 100" style="width: 100%;">
      <path d="M 10,80 C 30,80 50,50 70,30 S 120,20 140,20" stroke="#2196F3" stroke-width="3" fill="none"/>
      <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
      <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
    </svg>
    <p style="font-size: 0.9em; margin: 5px 0;">Market saturation</p>
  </div>
</div>

<div class="growth-calculator" style="background: #F5F5F5; padding: 15px; border-radius: 5px;">
  <strong>Interactive Growth Calculator:</strong>
  <table style="width: 100%; margin-top: 10px;">
    <tr>
      <td>Current value:</td>
      <td><input type="text" style="width: 100px; border-bottom: 1px solid #999;"/></td>
      <td>Growth rate:</td>
      <td><input type="text" style="width: 80px; border-bottom: 1px solid #999;"/>%</td>
      <td>Months:</td>
      <td><input type="text" style="width: 60px; border-bottom: 1px solid #999;"/></td>
    </tr>
  </table>
  
  <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 15px;">
    <div style="text-align: center; padding: 10px; background: #E8F5E9; border-radius: 5px;">
      <strong>Linear:</strong><br>
      <span style="font-size: 1.2em;">______</span>
    </div>
    <div style="text-align: center; padding: 10px; background: #FFF3E0; border-radius: 5px;">
      <strong>Exponential:</strong><br>
      <span style="font-size: 1.2em;">______</span>
    </div>
    <div style="text-align: center; padding: 10px; background: #E3F2FD; border-radius: 5px;">
      <strong>S-Curve:</strong><br>
      <span style="font-size: 1.2em;">______</span>
    </div>
  </div>
</div>
</div>

### Step 3: Safety Margins
<div class="truth-box">
<h4>🛟️ Safety Margin Guidelines</h4>

<div class="safety-margins-chart" style="margin: 20px 0;">
  <svg viewBox="0 0 600 300" style="width: 100%; max-width: 600px;">
    <!-- Title -->
    <text x="300" y="20" text-anchor="middle" font-weight="bold">Recommended Safety Margins by Component</text>
    
    <!-- CPU -->
    <g transform="translate(50, 50)">
      <text x="0" y="15" font-weight="bold">CPU</text>
      <rect x="100" y="0" width="300" height="30" fill="#E0E0E0" rx="3"/>
      <rect x="100" y="0" width="180" height="30" fill="#4CAF50" rx="3"/>
      <rect x="280" y="0" width="120" height="30" fill="#81C784" rx="3" opacity="0.7"/>
      <text x="190" y="20" text-anchor="middle" fill="white">60% Usage</text>
      <text x="340" y="20" text-anchor="middle" fill="white">40% Margin</text>
      <text x="420" y="20" font-size="12">Burst handling</text>
    </g>
    
    <!-- Memory -->
    <g transform="translate(50, 90)">
      <text x="0" y="15" font-weight="bold">Memory</text>
      <rect x="100" y="0" width="300" height="30" fill="#E0E0E0" rx="3"/>
      <rect x="100" y="0" width="210" height="30" fill="#2196F3" rx="3"/>
      <rect x="310" y="0" width="90" height="30" fill="#64B5F6" rx="3" opacity="0.7"/>
      <text x="205" y="20" text-anchor="middle" fill="white">70% Usage</text>
      <text x="355" y="20" text-anchor="middle" fill="white">30% Margin</text>
      <text x="420" y="20" font-size="12">GC headroom</text>
    </g>
    
    <!-- Network -->
    <g transform="translate(50, 130)">
      <text x="0" y="15" font-weight="bold">Network</text>
      <rect x="100" y="0" width="300" height="30" fill="#E0E0E0" rx="3"/>
      <rect x="100" y="0" width="150" height="30" fill="#FF9800" rx="3"/>
      <rect x="250" y="0" width="150" height="30" fill="#FFB74D" rx="3" opacity="0.7"/>
      <text x="175" y="20" text-anchor="middle" fill="white">50% Usage</text>
      <text x="325" y="20" text-anchor="middle" fill="white">50% Margin</text>
      <text x="420" y="20" font-size="12">DDoS/spikes</text>
    </g>
    
    <!-- Storage -->
    <g transform="translate(50, 170)">
      <text x="0" y="15" font-weight="bold">Storage</text>
      <rect x="100" y="0" width="300" height="30" fill="#E0E0E0" rx="3"/>
      <rect x="100" y="0" width="150" height="30" fill="#9C27B0" rx="3"/>
      <rect x="250" y="0" width="150" height="30" fill="#BA68C8" rx="3" opacity="0.7"/>
      <text x="175" y="20" text-anchor="middle" fill="white">50% Usage</text>
      <text x="325" y="20" text-anchor="middle" fill="white">50% Margin</text>
      <text x="420" y="20" font-size="12">Log growth</text>
    </g>
    
    <!-- DB Connections -->
    <g transform="translate(50, 210)">
      <text x="0" y="15" font-weight="bold">DB Conn</text>
      <rect x="100" y="0" width="300" height="30" fill="#E0E0E0" rx="3"/>
      <rect x="100" y="0" width="210" height="30" fill="#795548" rx="3"/>
      <rect x="310" y="0" width="90" height="30" fill="#A1887F" rx="3" opacity="0.7"/>
      <text x="205" y="20" text-anchor="middle" fill="white">70% Usage</text>
      <text x="355" y="20" text-anchor="middle" fill="white">30% Margin</text>
      <text x="420" y="20" font-size="12">Connection storms</text>
    </g>
  </svg>
</div>

<div class="margin-rationale" style="background: #F5F5F5; padding: 15px; border-radius: 5px;">
  <strong>💡 Why These Margins?</strong>
  <ul style="margin: 10px 0 0 20px;">
    <li><strong>CPU:</strong> Handles traffic spikes, batch jobs, and unexpected load</li>
    <li><strong>Memory:</strong> Prevents OOM during garbage collection cycles</li>
    <li><strong>Network:</strong> Absorbs DDoS attacks and flash crowds</li>
    <li><strong>Storage:</strong> Accommodates log rotation and unexpected data growth</li>
    <li><strong>DB Connections:</strong> Handles reconnection storms after outages</li>
  </ul>
</div>
</div>

## Workload Characterization

```python
# Traffic Patterns
Peak hour: _____ (e.g., 2 PM)
Peak/average ratio: _____ (e.g., 3x)
Weekend factor: _____ (e.g., 0.6x)
Black Friday: _____x normal

# Request Mix
Operation         % Traffic    Impact
Read (cached)     60%         Low (1x)
Read (DB)         20%         Medium (3x)
Write             15%         High (5x)
Analytics         5%          Very High (10x)

Weighted usage: 0.6×1 + 0.2×3 + 0.15×5 + 0.05×10 = 2.45 units/request
```

## Scaling Strategies

```text
Vertical: 8→16 CPU, 32→64GB RAM
  Cost: 2.2x (non-linear), Limit: 96 CPU/768GB

Horizontal: 10→15 instances
  Cost: 1.5x (linear), Limit: unlimited
```

### Resource Planning Table
<div class="decision-box">
<h4>📊 Capacity Growth Timeline</h4>

<div class="planning-visualization" style="margin: 20px 0;">
  <svg viewBox="0 0 700 400" style="width: 100%; max-width: 700px;">
    <!-- Title -->
    <text x="350" y="20" text-anchor="middle" font-weight="bold">12-Month Capacity Projection</text>
    
    <!-- Axes -->
    <line x1="60" y1="320" x2="650" y2="320" stroke="#333" stroke-width="2"/>
    <line x1="60" y1="320" x2="60" y2="40" stroke="#333" stroke-width="2"/>
    
    <!-- Y-axis labels (Traffic) -->
    <text x="40" y="325" text-anchor="end" font-size="10">0</text>
    <text x="40" y="265" text-anchor="end" font-size="10">1000</text>
    <text x="40" y="205" text-anchor="end" font-size="10">2000</text>
    <text x="40" y="145" text-anchor="end" font-size="10">3000</text>
    <text x="40" y="85" text-anchor="end" font-size="10">4000</text>
    <text x="40" y="45" text-anchor="end" font-size="10">5000</text>
    <text x="20" y="180" text-anchor="middle" transform="rotate(-90 20 180)" font-size="12">Traffic (rps)</text>
    
    <!-- X-axis labels (Months) -->
    <text x="60" y="340" text-anchor="middle" font-size="10">0</text>
    <text x="210" y="340" text-anchor="middle" font-size="10">3</text>
    <text x="360" y="340" text-anchor="middle" font-size="10">6</text>
    <text x="510" y="340" text-anchor="middle" font-size="10">9</text>
    <text x="650" y="340" text-anchor="middle" font-size="10">12</text>
    <text x="350" y="365" text-anchor="middle" font-size="12">Months</text>
    
    <!-- Traffic growth curve -->
    <path d="M 60,260 L 210,230 L 360,180 L 510,120 L 650,60" 
          stroke="#2196F3" stroke-width="3" fill="none"/>
    
    <!-- Data points -->
    <circle cx="60" cy="260" r="5" fill="#2196F3"/>
    <circle cx="210" cy="230" r="5" fill="#2196F3"/>
    <circle cx="360" cy="180" r="5" fill="#FF5722"/>
    <circle cx="650" cy="60" r="5" fill="#F44336"/>
    
    <!-- Architecture change indicator -->
    <line x1="360" y1="40" x2="360" y2="320" stroke="#FF5722" stroke-width="2" stroke-dasharray="5,5"/>
    <rect x="280" y="50" width="160" height="30" fill="#FFE0B2" rx="3"/>
    <text x="360" y="70" text-anchor="middle" font-weight="bold">Architecture Change</text>
    
    <!-- Cost indicators -->
    <g transform="translate(680, 100)">
      <text x="0" y="0" font-size="10" font-weight="bold">Cost Impact</text>
      <text x="0" y="20" font-size="9">Month 0: $10k</text>
      <text x="0" y="40" font-size="9">Month 3: $15k</text>
      <text x="0" y="60" font-size="9" fill="#FF5722">Month 6: $22k</text>
      <text x="0" y="80" font-size="9" fill="#F44336">Month 12: $50k</text>
    </g>
  </svg>
</div>

<div class="planning-table" style="background: #F5F5F5; padding: 15px; border-radius: 5px;">
  <table style="width: 100%; text-align: center;">
    <tr style="background: #E0E0E0;">
      <th>Month</th>
      <th>Traffic</th>
      <th>CPU Need</th>
      <th>Instances</th>
      <th>Monthly Cost</th>
      <th>Action Required</th>
    </tr>
    <tr style="background: #E8F5E9;">
      <td>0</td>
      <td>1,000 rps</td>
      <td>800 cores</td>
      <td>100</td>
      <td>$10k</td>
      <td>✅ Current state</td>
    </tr>
    <tr>
      <td>3</td>
      <td>1,500 rps</td>
      <td>1,200 cores</td>
      <td>150</td>
      <td>$15k</td>
      <td>⚡ Scale horizontally</td>
    </tr>
    <tr style="background: #FFE0B2;">
      <td>6</td>
      <td>2,250 rps</td>
      <td>1,800 cores</td>
      <td>225</td>
      <td>$22k</td>
      <td>🔧 Architecture review</td>
    </tr>
    <tr style="background: #FFCDD2;">
      <td>12</td>
      <td>5,000 rps</td>
      <td>4,000 cores</td>
      <td>500</td>
      <td>$50k</td>
      <td>🚨 Major redesign</td>
    </tr>
  </table>
</div>

<div class="decision-point" style="background: #FFE0B2; padding: 15px; margin-top: 15px; border-left: 4px solid #FF5722;">
  ⚠️ <strong>Critical Decision Point:</strong> Month 6 - Linear scaling becomes cost-prohibitive. Consider:
  <ul style="margin: 10px 0 0 20px;">
    <li>Microservices architecture</li>
    <li>Caching layer implementation</li>
    <li>Database sharding</li>
    <li>CDN offloading</li>
  </ul>
</div>
</div>

## Capacity Planning Tools

```python
# Little's Law
Concurrent users = Requests/sec × Session duration
DB connections = Queries/sec × Query time
Memory = Objects/sec × Object lifetime × Size

# Queue Theory
Utilization > 70% → Exponential response time
Servers needed = Load / (Capacity × 0.7)
```

## Real Example: E-Commerce Platform

```python
# Current: 10K users, 100/300 rps avg/peak, 50GB DB, 1TB storage
# Growth: 20% users, 30% data monthly

# 6-Month Projection
Users: 10K × 1.2^6 = 30K
Peak: 300 × 3 = 900 rps
DB: 50 × 1.3^6 = 230GB
Storage: 1 × 1.3^6 = 4.6TB

Infrastructure: Apps 10→30, DB needs sharding, Cache 10→50GB, CDN required
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

```text
Web App: 1 CPU = 100 rps, 1GB = 500 sessions, 10 Mbps/100 rps
API: 1 CPU = 1000 rps JSON, 1GB = 10k connections
Database: 1 CPU = 1000 queries/s, RAM = working set + indexes
Queue: 1 CPU = 10k msg/s, Storage = rate × size × retention
```

## Capacity Triggers

```python
# Immediate Action
CPU > 80%, Memory > 90%, Storage > 80%, Network > 70%, Errors > 1%

# Planning Required  
3-month projection hits limit, growth accelerating, new features/regions

# Architecture Change
Vertical limit reached, super-linear costs, higher availability needed
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

1. **Using average instead of peak** → Plan for 95th percentile
2. **Forgetting hidden resources** → File descriptors, thread pools, kernel buffers
3. **Linear growth assumptions** → Plan for exponential/viral growth
4. **Ignoring batch jobs** → Include overnight processing
5. **Not testing limits** → Load test actual capacity

## Key Takeaways

1. **Measure everything** → No data, no planning
2. **Plan for peaks** → Average misleads
3. **Include safety margins** → 30-50% headroom
4. **Monitor growth changes** → Watch inflection points
5. **Test assumptions** → Reality ≠ theory
