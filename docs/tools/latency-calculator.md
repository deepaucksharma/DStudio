# Latency Calculator

!!! info "Calculate Network Latencies"
    This tool helps you estimate end-to-end latencies based on physical distance, network topology, and processing overhead.

!!! tip "Quick Navigation"
    [← Tools Home](index.md) |
    [Capacity Planner →](capacity-planner.md) |
    [Reference →](../reference/index.md)

## Interactive Calculator

<div class="calculator-container">
<h3>🌍 Global Latency Estimator</h3>

<form id="latency-calc">
  <div class="form-group">
    <label for="distance">Distance (km):</label>
    <input type="number" id="distance" name="distance" value="4100" min="1" max="20000">
    <small>NYC to SF: 4100km, NYC to London: 5600km, Earth circumference: 40,075km</small>
  </div>

  <div class="form-group">
    <label for="medium">Medium:</label>
    <select id="medium" name="medium">
      <option value="fiber" selected>Fiber Optic (0.67c)</option>
      <option value="copper">Copper (0.66c)</option>
      <option value="wireless">Wireless (1.0c)</option>
    </select>
  </div>

  <div class="form-group">
    <label for="hops">Network Hops:</label>
    <input type="number" id="hops" name="hops" value="15" min="1" max="50">
    <small>Typical: Local 1-5, Regional 5-15, Global 15-30</small>
  </div>

  <div class="form-group">
    <label>Network Devices:</label>
    <div class="device-inputs">
      <label>Routers: <input type="number" name="routers" value="10" min="0" max="50"></label>
      <label>Switches: <input type="number" name="switches" value="5" min="0" max="50"></label>
      <label>Firewalls: <input type="number" name="firewalls" value="2" min="0" max="10"></label>
      <label>Load Balancers: <input type="number" name="lbs" value="2" min="0" max="10"></label>
    </div>
  </div>

  <button type="button" onclick="calculateLatency()" class="md-button md-button--primary">Calculate</button>
</form>

<div id="results" class="results-container"></div>
</div>

<script>
function calculateLatency() {
    const distance = parseFloat(document.getElementById('distance').value);
    const medium = document.getElementById('medium').value;
    const hops = parseInt(document.getElementById('hops').value);
    
    // Speed of light and medium factors
    const SPEED_OF_LIGHT = 299792; // km/s
    const mediumFactors = {
        'fiber': 0.67,
        'copper': 0.66,
        'wireless': 1.0
    };
    
    // Device processing times (ms)
    const deviceOverhead = {
        'routers': 0.1,
        'switches': 0.01,
        'firewalls': 0.5,
        'lbs': 0.2
    };
    
    // Calculate propagation delay
    const effectiveSpeed = SPEED_OF_LIGHT * mediumFactors[medium];
    const propagationDelay = (distance / effectiveSpeed) * 1000; // ms
    
    // Calculate processing delay
    let processingDelay = 0;
    for (const [device, overhead] of Object.entries(deviceOverhead)) {
        const count = parseInt(document.querySelector(`input[name="${device}"]`).value);
        processingDelay += count * overhead;
    }
    
    // Serialization delay (simplified)
    const serializationDelay = hops * 0.1; // 100μs per hop
    
    // Total latency
    const totalLatency = propagationDelay + processingDelay + serializationDelay;
    
    // Display results
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <h4>Latency Breakdown</h4>
        <table>
            <tr>
                <td>Propagation Delay:</td>
                <td>${propagationDelay.toFixed(2)} ms</td>
                <td>${(propagationDelay/totalLatency*100).toFixed(1)}%</td>
            </tr>
            <tr>
                <td>Processing Delay:</td>
                <td>${processingDelay.toFixed(2)} ms</td>
                <td>${(processingDelay/totalLatency*100).toFixed(1)}%</td>
            </tr>
            <tr>
                <td>Serialization Delay:</td>
                <td>${serializationDelay.toFixed(2)} ms</td>
                <td>${(serializationDelay/totalLatency*100).toFixed(1)}%</td>
            </tr>
            <tr class="total-row">
                <td><strong>Total One-Way Latency:</strong></td>
                <td><strong>${totalLatency.toFixed(2)} ms</strong></td>
                <td>100%</td>
            </tr>
            <tr class="total-row">
                <td><strong>Round-Trip Time (RTT):</strong></td>
                <td><strong>${(totalLatency * 2).toFixed(2)} ms</strong></td>
                <td>-</td>
            </tr>
        </table>
        
        <div class="insight-box">
            <h5>💡 Insights</h5>
            <ul>
                <li>Theoretical minimum (speed of light): ${(distance/SPEED_OF_LIGHT*1000).toFixed(2)} ms</li>
                <li>Your latency is ${(totalLatency/(distance/SPEED_OF_LIGHT*1000)).toFixed(1)}x the theoretical minimum</li>
                <li>${propagationDelay > processingDelay ? 'Propagation delay dominates - consider edge locations' : 'Processing delay dominates - optimize network path'}</li>
            </ul>
        </div>
    `;
}

// Calculate on page load
window.onload = calculateLatency;
</script>

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