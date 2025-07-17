# Latency Calculator

!!! info "Interactive Tool"
    Use this calculator to understand how distance, network hops, and data size affect latency in distributed systems.

<div id="latency-calculator" class="interactive-tool">
  <form id="latency-calc">
    <div class="tool-inputs">
      <div class="form-group">
        <label>Quick Routes:</label>
        <div class="route-presets">
          <button type="button" class="route-btn" data-distance="4129" data-route="NYC ↔ SF">NYC ↔ SF</button>
          <button type="button" class="route-btn" data-distance="5567" data-route="NYC ↔ London">NYC ↔ London</button>
          <button type="button" class="route-btn" data-distance="8280" data-route="SF ↔ Tokyo">SF ↔ Tokyo</button>
          <button type="button" class="route-btn" data-distance="16983" data-route="London ↔ Sydney">London ↔ Sydney</button>
        </div>
        <div id="selected-route" class="selected-route"></div>
      </div>
      
      <div class="input-group">
        <label for="distance">Distance (km)</label>
        <input type="number" id="distance" value="1000" min="0" max="20000">
        <small>Geographic distance between nodes</small>
      </div>
      
      <div class="input-group">
        <label for="medium">Network Medium</label>
        <select id="medium" class="medium-select">
          <option value="fiber">Fiber Optic Cable</option>
          <option value="copper">Copper Wire</option>
          <option value="wireless">Wireless</option>
        </select>
        <small>Physical transmission medium</small>
      </div>
      
      <div class="input-group">
        <label for="hops">Network Hops</label>
        <input type="number" id="hops" value="5" min="1" max="50">
        <small>Number of routers/switches</small>
      </div>
      
      <div class="input-group">
        <label>Network Devices</label>
        <div class="device-inputs">
          <label><input type="number" name="routers" value="3" min="0" max="20"> Routers</label>
          <label><input type="number" name="switches" value="2" min="0" max="20"> Switches</label>
          <label><input type="number" name="firewalls" value="1" min="0" max="10"> Firewalls</label>
          <label><input type="number" name="lbs" value="1" min="0" max="10"> Load Balancers</label>
        </div>
      </div>
    </div>
  </form>
  
  <div id="latency-visualization" class="tool-visualization">
    <!-- Canvas will be created here by JavaScript -->
  </div>
  
  <div class="tool-results">
    <h3>Results</h3>
    <div class="result-grid">
      <div class="result-item">
        <span class="result-label">Propagation Delay</span>
        <span class="result-value" id="prop-delay">0 ms</span>
      </div>
      <div class="result-item">
        <span class="result-label">Processing Delay</span>
        <span class="result-value" id="proc-delay">0 ms</span>
      </div>
      <div class="result-item">
        <span class="result-label">Serialization Delay</span>
        <span class="result-value" id="serial-delay">0 ms</span>
      </div>
      <div class="result-item highlight">
        <span class="result-label">Total RTT</span>
        <span class="result-value" id="total-rtt">0 ms</span>
      </div>
    </div>
    
    <div class="result-insights">
      <h4>💡 Insights</h4>
      <ul id="insights-list">
        <!-- Dynamically populated -->
      </ul>
    </div>
    
    <div class="comparison-chart">
      <h4>Real-World Comparison</h4>
      <div id="comparison-bars">
        <!-- Dynamically populated -->
      </div>
    </div>
  </div>
</div>

## Common Latency Scenarios

### Regional Data Centers

| Route | Distance | Fiber RTT | With Processing | Typical Range |
|-------|----------|-----------|-----------------|---------------|
| NYC ↔ Boston | 300 km | 3 ms | 5-8 ms | 8-15 ms |
| SF ↔ LA | 600 km | 6 ms | 8-12 ms | 10-20 ms |
| London ↔ Paris | 350 km | 3.5 ms | 6-10 ms | 8-18 ms |
| Tokyo ↔ Osaka | 500 km | 5 ms | 7-11 ms | 10-20 ms |

### Cross-Continental

| Route | Distance | Fiber RTT | With Processing | Typical Range |
|-------|----------|-----------|-----------------|---------------|
| NYC ↔ SF | 4,100 km | 41 ms | 45-55 ms | 60-80 ms |
| NYC ↔ London | 5,600 km | 56 ms | 60-70 ms | 75-100 ms |
| London ↔ Singapore | 10,800 km | 108 ms | 115-130 ms | 140-180 ms |
| Sydney ↔ LA | 12,000 km | 120 ms | 130-150 ms | 160-200 ms |

## Latency Optimization Strategies

### 1. Reduce Physical Distance

<div class="strategy-box">
<h4>Edge Deployment</h4>

Deploy services closer to users:
- **CDN**: Static content at edge locations
- **Edge Compute**: Process at edge POPs
- **Regional Deployments**: Multiple geographic regions

**Impact**: Can reduce latency by 50-80% for end users
</div>

### 2. Optimize Network Path

<div class="strategy-box">
<h4>Network Optimization</h4>

Reduce hops and processing:
- **Direct Peering**: Connect directly to ISPs
- **Premium Transit**: Use optimized routes
- **Anycast**: Route to nearest location

**Impact**: 10-30% latency reduction
</div>

### 3. Protocol Optimization

<div class="strategy-box">
<h4>Protocol Selection</h4>

Choose efficient protocols:
- **HTTP/3 + QUIC**: 0-RTT connection establishment
- **gRPC**: Binary protocol, multiplexing
- **WebSocket**: Persistent connections

**Impact**: Save 1-3 RTTs per request
</div>

## Code Examples

### Python Latency Profiler

```python
import time
import statistics
from typing import List, Dict, Callable

class LatencyProfiler:
    def __init__(self):
        self.measurements = {}
    
    def measure(self, name: str, func: Callable, iterations: int = 100) -> Dict:
        """Measure function latency over multiple iterations"""
        latencies = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms
        
        self.measurements[name] = {
            'min': min(latencies),
            'max': max(latencies),
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'p95': statistics.quantiles(latencies, n=20)[18],  # 95th percentile
            'p99': statistics.quantiles(latencies, n=100)[98],  # 99th percentile
        }
        
        return self.measurements[name]
    
    def compare(self, baseline: str, *others: str) -> Dict:
        """Compare latencies against baseline"""
        if baseline not in self.measurements:
            raise ValueError(f"Baseline '{baseline}' not found")
        
        base_median = self.measurements[baseline]['median']
        comparison = {}
        
        for name in others:
            if name in self.measurements:
                other_median = self.measurements[name]['median']
                comparison[name] = {
                    'median_ms': other_median,
                    'vs_baseline': f"{(other_median/base_median - 1)*100:+.1f}%",
                    'difference_ms': other_median - base_median
                }
        
        return comparison

# Usage example
profiler = LatencyProfiler()

# Measure different operations
profiler.measure('disk_read', lambda: read_file('test.txt'))
profiler.measure('memory_read', lambda: read_memory_cache())
profiler.measure('network_call', lambda: make_api_call())

# Compare results
comparison = profiler.compare('memory_read', 'disk_read', 'network_call')
print(f"Network call is {comparison['network_call']['vs_baseline']} slower than memory")
```

### Real-time Latency Monitor

```javascript
class LatencyMonitor {
    constructor(windowSize = 100) {
        this.windowSize = windowSize;
        this.measurements = new Map();
    }
    
    async measureEndpoint(url, options = {}) {
        const start = performance.now();
        
        try {
            const response = await fetch(url, options);
            const end = performance.now();
            const latency = end - start;
            
            this.recordMeasurement(url, latency, response.ok);
            
            return {
                url,
                latency,
                status: response.status,
                timestamp: new Date()
            };
        } catch (error) {
            const end = performance.now();
            const latency = end - start;
            
            this.recordMeasurement(url, latency, false);
            
            return {
                url,
                latency,
                error: error.message,
                timestamp: new Date()
            };
        }
    }
    
    recordMeasurement(endpoint, latency, success) {
        if (!this.measurements.has(endpoint)) {
            this.measurements.set(endpoint, {
                latencies: [],
                successes: [],
                failures: 0
            });
        }
        
        const data = this.measurements.get(endpoint);
        
        // Sliding window
        if (data.latencies.length >= this.windowSize) {
            data.latencies.shift();
            data.successes.shift();
        }
        
        data.latencies.push(latency);
        data.successes.push(success);
        if (!success) data.failures++;
    }
    
    getStats(endpoint) {
        const data = this.measurements.get(endpoint);
        if (!data || data.latencies.length === 0) return null;
        
        const sorted = [...data.latencies].sort((a, b) => a - b);
        const len = sorted.length;
        
        return {
            count: len,
            min: sorted[0],
            max: sorted[len - 1],
            mean: sorted.reduce((a, b) => a + b) / len,
            median: sorted[Math.floor(len / 2)],
            p95: sorted[Math.floor(len * 0.95)],
            p99: sorted[Math.floor(len * 0.99)],
            successRate: data.successes.filter(s => s).length / len,
            failures: data.failures
        };
    }
}

// Usage
const monitor = new LatencyMonitor();

// Monitor multiple endpoints
setInterval(async () => {
    const endpoints = [
        'https://api.example.com/health',
        'https://cdn.example.com/ping',
        'https://db.example.com/status'
    ];
    
    for (const endpoint of endpoints) {
        const result = await monitor.measureEndpoint(endpoint);
        console.log(`${endpoint}: ${result.latency.toFixed(2)}ms`);
    }
    
    // Get statistics
    const stats = monitor.getStats(endpoints[0]);
    if (stats) {
        console.log(`API Stats - P95: ${stats.p95.toFixed(2)}ms, Success: ${(stats.successRate * 100).toFixed(1)}%`);
    }
}, 5000);
```

## Key Takeaways

1. **Physics Sets the Floor**: You cannot beat the speed of light
2. **Processing Adds Up**: Each hop and device adds delay
3. **Distance Matters**: Co-location and edge deployment are powerful
4. **Measure Everything**: Real-world is always higher than theoretical
5. **Optimize Holistically**: Network, protocol, and application layers

## Related Resources

- [Axiom 1: Latency](../part1-axioms/axiom-1-latency/index.md)
- [Capacity Planner](capacity-planner.md)
- [Network Optimization Guide](../reference/network-optimization.md)