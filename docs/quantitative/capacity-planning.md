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
!!! abstract "📏 Current State Assessment"

 <div class="measurement-form">
 <div>
 <div>
 <strong>Traffic Metrics:</strong>
 <table class="responsive-table">
 <tr><td>Peak traffic:</td><td>_______</td><td>req/s</td></tr>
 <tr><td>Average traffic:</td><td>_______</td><td>req/s</td></tr>
 <tr><td>Peak/Average ratio:</td><td>_______</td><td>x</td></tr>
 </table>
 <div>
 <strong>Growth & Storage:</strong>
 <table class="responsive-table">
 <tr><td>Storage used:</td><td>_______</td><td>GB</td></tr>
 <tr><td>Growth rate:</td><td>_______</td><td>% monthly</td></tr>
 <tr><td>Retention:</td><td>_______</td><td>days</td></tr>
 </table>
 </div>
 </div>
 
 <div>
 <strong>Resource Usage at Peak:</strong>
 <svg viewBox="0 0 500 200" role="img" aria-label="Resource usage gauges showing CPU, Memory, Network, and Disk I/O percentages at peak load">
 <title>Resource Usage at Peak</title>
 <desc>Interactive gauge visualization displaying current resource utilization levels for CPU, Memory, Network bandwidth, and Disk I/O operations</desc>
 <!-- CPU gauge -->
 <g transform="translate(50, 50)">
 <text x="50" y="-10" text-anchor="middle" font-weight="bold">CPU</text>
 <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
 <rect x="0" y="0" width="0" height="30" fill="#4CAF50" rx="3" id="cpu-bar"/>
 <text x="50" y="50" text-anchor="middle">_____%</text>
 </g>
 
 <!-- Memory gauge -->
 <g transform="translate(200, 50)">
 <text x="50" y="-10" text-anchor="middle" font-weight="bold">Memory</text>
 <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
 <rect x="0" y="0" width="0" height="30" fill="#2196F3" rx="3" id="mem-bar"/>
 <text x="50" y="50" text-anchor="middle">_____%</text>
 </g>
 
 <!-- Network gauge -->
 <g transform="translate(350, 50)">
 <text x="50" y="-10" text-anchor="middle" font-weight="bold">Network</text>
 <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
 <rect x="0" y="0" width="0" height="30" fill="#FF9800" rx="3" id="net-bar"/>
 <text x="50" y="50" text-anchor="middle">_____ Mbps</text>
 </g>
 
 <!-- Disk I/O gauge -->
 <g transform="translate(125, 120)">
 <text x="50" y="-10" text-anchor="middle" font-weight="bold">Disk I/O</text>
 <rect x="0" y="0" width="100" height="30" fill="#E0E0E0" rx="3"/>
 <rect x="0" y="0" width="0" height="30" fill="#9C27B0" rx="3" id="disk-bar"/>
 <text x="50" y="50" text-anchor="middle">_____ IOPS</text>
 </g>
 </svg>
 </div>
</div>
</div>

### Step 2: Growth Projection
!!! note "📈 Growth Model Selection"
 <div>
 <h5>Linear Growth</h5>
 <div>
 <span>Future = Current × (1 + rate × months)</span>
 <svg viewBox="0 0 150 100" role="img" aria-label="Linear growth model graph">
 <title>Linear Growth</title>
 <line x1="10" y1="80" x2="140" y2="20" stroke="#4CAF50" stroke-width="3"/>
 <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
 <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
 </svg>
 <p>Steady, predictable growth</p>
 
 <div>
 <h5>Exponential Growth</h5>
 <div>
 <span>Future = Current × (1 + rate)^months</span>
 </div>
 <svg viewBox="0 0 150 100" role="img" aria-label="Exponential growth model graph">
 <title>Exponential Growth</title>
 <path d="M 10,80 Q 50,75 140,20" stroke="#FF9800" stroke-width="3" fill="none"/>
 <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
 <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
 </svg>
 <p>Viral/compound growth</p>
 </div>
 
 <div>
 <h5>S-Curve Growth</h5>
 <div>
 <span>Future = Cap / (1 + e^(-k×(t-t0)))</span>
 </div>
 <svg viewBox="0 0 150 100" role="img" aria-label="S-curve growth model graph">
 <title>S-Curve Growth</title>
 <path d="M 10,80 C 30,80 50,50 70,30 S 120,20 140,20" stroke="#2196F3" stroke-width="3" fill="none"/>
 <line x1="10" y1="90" x2="140" y2="90" stroke="#333" stroke-width="1"/>
 <line x1="10" y1="90" x2="10" y2="10" stroke="#333" stroke-width="1"/>
 </svg>
 <p>Market saturation</p>
 </div>
</div>

<strong>Interactive Growth Calculator:</strong>
<div class="calculator-tool">
 <form id="growthCalc">
 <table class="responsive-table">
 <tr>
 <td><label for="currentValue">Current value:</label></td>
 <td><input type="number" id="currentValue" min="0" step="1"/></td>
 <td><label for="growthRate">Growth rate:</label></td>
 <td><input type="number" id="growthRate" min="0" max="100" step="0.1"/>%</td>
 <td><label for="months">Months:</label></td>
 <td><input type="number" id="months" min="1" max="60" step="1"/></td>
 </tr>
 </table>
 <button type="button" onclick="calculateGrowth()" class="calc-button">Calculate Growth</button>
 </form>
 
 <div id="growthResults" class="results-panel" style="display: none;">
 <h4>Growth Projections</h4>
 <div class="metric-cards-grid">
 <div class="metric-card">
 <h4>Linear Growth</h4>
 <div class="metric-value" id="linearResult">______</div>
 </div>
 <div class="metric-card">
 <h4>Exponential Growth</h4>
 <div class="metric-value" id="exponentialResult">______</div>
 </div>
 <div class="metric-card">
 <h4>S-Curve Growth</h4>
 <div class="metric-value" id="scurveResult">______</div>
 </div>
 </div>
 </div>
</div>

<script>
function calculateGrowth() {
 const current = parseFloat(document.getElementById('currentValue').value);
 const rate = parseFloat(document.getElementById('growthRate').value) / 100;
 const months = parseInt(document.getElementById('months').value);
 
 if (isNaN(current) || isNaN(rate) || isNaN(months)) {
 alert('Please enter valid numbers');
 return;
 }
 
 // Linear growth
 const linear = current * (1 + rate * months);
 
 // Exponential growth
 const exponential = current * Math.pow(1 + rate, months);
 
 // S-Curve (simplified)
 const cap = current * 10; // Assume 10x max capacity
 const k = 0.5; // Growth rate constant
 const t0 = months / 2; // Midpoint
 const scurve = cap / (1 + Math.exp(-k * (months - t0)));
 
 // Display results
 document.getElementById('linearResult').textContent = linear.toFixed(0);
 document.getElementById('exponentialResult').textContent = exponential.toFixed(0);
 document.getElementById('scurveResult').textContent = scurve.toFixed(0);
 
 document.getElementById('growthResults').style.display = 'block';
}
</script>
</div>

### Step 3: Safety Margins
!!! info "🛟️ Safety Margin Guidelines"
 <svg viewBox="0 0 600 300" role="img" aria-label="Bar chart showing recommended safety margins for different system components">
 <title>Recommended Safety Margins by Component</title>
 <desc>Horizontal bar chart displaying recommended usage percentages and safety margins for CPU (60% usage, 40% margin), Memory (70% usage, 30% margin), Network (50% usage, 50% margin), Storage (50% usage, 50% margin), and Database Connections (70% usage, 30% margin)</desc>
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

<div class="margin-rationale">
 <strong>💡 Why These Margins?</strong>
 <ul>
 <li><strong>CPU:</strong> Handles traffic spikes, batch jobs, and unexpected load</li>
 <li><strong>Memory:</strong> Prevents OOM during garbage collection cycles</li>
 <li><strong>Network:</strong> Absorbs DDoS attacks and flash crowds</li>
 <li><strong>Storage:</strong> Accommodates log rotation and unexpected data growth</li>
 <li><strong>DB Connections:</strong> Handles reconnection storms after outages</li>
 </ul>
</div>

## Workload Characterization

```python
# Traffic Patterns
Peak hour: _____ (e.g., 2 PM)
Peak/average ratio: _____ (e.g., 3x)
Weekend factor: _____ (e.g., 0.6x)
Black Friday: _____x normal

# Request Mix
Operation % Traffic Impact
Read (cached) 60% Low (1x)
Read (DB) 20% Medium (3x)
Write 15% High (5x)
Analytics 5% Very High (10x)

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
!!! note "📊 Capacity Growth Timeline"
 <svg viewBox="0 0 700 400" role="img" aria-label="Line chart showing 12-month traffic growth projection with cost impact and architecture change indicators">
 <title>12-Month Capacity Projection</title>
 <desc>Line chart projecting traffic growth from 1000 to 5000 requests per second over 12 months, with markers indicating architecture change needed at month 6 and associated cost increases from $10k to $50k monthly</desc>
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

<div class="planning-table">
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Month</th>
 <th>Traffic</th>
 <th>CPU Need</th>
 <th>Instances</th>
 <th>Monthly Cost</th>
 <th>Action Required</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Month">0</td>
 <td data-label="Traffic">1,000 rps</td>
 <td data-label="CPU Need">800 cores</td>
 <td data-label="Instances">100</td>
 <td data-label="Monthly Cost">$10k</td>
 <td data-label="Action Required">✅ Current state</td>
 </tr>
 <tr>
 <td data-label="Month">3</td>
 <td data-label="Traffic">1,500 rps</td>
 <td data-label="CPU Need">1,200 cores</td>
 <td data-label="Instances">150</td>
 <td data-label="Monthly Cost">$15k</td>
 <td data-label="Action Required">⚡ Scale horizontally</td>
 </tr>
 <tr>
 <td data-label="Month">6</td>
 <td data-label="Traffic">2,250 rps</td>
 <td data-label="CPU Need">1,800 cores</td>
 <td data-label="Instances">225</td>
 <td data-label="Monthly Cost">$22k</td>
 <td data-label="Action Required">🔧 Architecture review</td>
 </tr>
 <tr>
 <td data-label="Month">12</td>
 <td data-label="Traffic">5,000 rps</td>
 <td data-label="CPU Need">4,000 cores</td>
 <td data-label="Instances">500</td>
 <td data-label="Monthly Cost">$50k</td>
 <td data-label="Action Required">🚨 Major redesign</td>
 </tr>
 </tbody>
</table>

⚠️ <strong>Critical Decision Point:</strong> Month 6 - Linear scaling becomes cost-prohibitive. Consider:
 <ul>
 <li>Microservices architecture</li>
 <li>Caching layer implementation</li>
 <li>Database sharding</li>
 <li>CDN offloading</li>
 </ul>
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
 total_cpu = peak_cpu / 0.5 # 50% target utilization

 return total_cpu
```

### Memory Capacity Planning
```python
def calculate_memory_needs():
# Static components
 os_memory = 2 # GB
 app_runtime = 4 # GB

# Dynamic components
 connection_pool = connections * 10 # MB per connection
 cache_size = hot_data_size * 1.2 # 20% overhead
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
 index_size = data_size * 0.3 # 30% typical

# Future margin
 margin = total * 0.5 # 50% headroom

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
