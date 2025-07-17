# Capacity Planner

!!! info "Plan System Capacity"
    Use Little's Law and queueing theory to determine optimal system capacity and predict performance under load.

!!! tip "Quick Navigation"
    [← Latency Calculator](latency-calculator.md) |
    [Tools Home](index.md) |
    [Failure Calculator →](failure-calculator.md)

## Interactive Capacity Planner

<div class="calculator-container">
<h3>📊 System Capacity Calculator</h3>

<form id="capacity-calc">
  <div class="form-group">
    <label for="arrival-rate">Arrival Rate (requests/second):</label>
    <input type="number" id="arrival-rate" name="arrival_rate" value="1000" min="1" step="10">
    <small>Average number of requests arriving per second</small>
  </div>

  <div class="form-group">
    <label for="service-time">Service Time (milliseconds):</label>
    <input type="number" id="service-time" name="service_time" value="50" min="1" step="5">
    <small>Average time to process one request</small>
  </div>

  <div class="form-group">
    <label for="servers">Number of Servers:</label>
    <input type="number" id="servers" name="servers" value="10" min="1" max="1000">
    <small>Parallel processing units available</small>
  </div>

  <div class="form-group">
    <label for="target-util">Target Utilization (%):</label>
    <input type="number" id="target-util" name="target_util" value="70" min="10" max="95" step="5">
    <small>Recommended: 70% for latency-sensitive, 85% for throughput</small>
  </div>

  <button type="button" class="md-button md-button--primary calculate-btn">Calculate</button>
</form>

<div id="capacity-visualization" class="visualization-container"></div>

<div id="capacity-results" class="results-container"></div>
</div>

<!-- Enhanced Capacity Planner loads from external JS file -->

<script style="display:none;">
// Legacy script disabled - using enhanced version
function calculateCapacity() {
    const arrivalRate = parseFloat(document.getElementById('arrival-rate').value);
    const serviceTimeMs = parseFloat(document.getElementById('service-time').value);
    const servers = parseInt(document.getElementById('servers').value);
    const targetUtil = parseFloat(document.getElementById('target-util').value) / 100;
    
    // Convert service time to rate
    const serviceRate = 1000 / serviceTimeMs; // requests/second per server
    const totalServiceRate = serviceRate * servers;
    
    // Calculate utilization
    const utilization = arrivalRate / totalServiceRate;
    
    // Little's Law calculations
    const responseTime = serviceTimeMs / (1 - utilization);
    const queueLength = arrivalRate * (responseTime / 1000);
    const queueWait = responseTime - serviceTimeMs;
    
    // Capacity recommendations
    const currentCapacity = totalServiceRate;
    const requiredServers = Math.ceil(arrivalRate / (serviceRate * targetUtil));
    const headroom = ((totalServiceRate - arrivalRate) / totalServiceRate * 100);
    
    // Display results
    const resultsDiv = document.getElementById('capacity-results');
    
    let statusClass = 'status-good';
    let statusText = 'Healthy';
    if (utilization > 0.9) {
        statusClass = 'status-critical';
        statusText = 'Critical - Near saturation!';
    } else if (utilization > 0.8) {
        statusClass = 'status-warning';
        statusText = 'Warning - High utilization';
    }
    
    resultsDiv.innerHTML = `
        <h4>Capacity Analysis</h4>
        
        <div class="${statusClass}">
            <strong>System Status: ${statusText}</strong>
        </div>
        
        <table>
            <tr>
                <td>Current Utilization:</td>
                <td><strong>${(utilization * 100).toFixed(1)}%</strong></td>
            </tr>
            <tr>
                <td>Max Sustainable Load:</td>
                <td>${currentCapacity.toFixed(0)} req/s</td>
            </tr>
            <tr>
                <td>Current Headroom:</td>
                <td>${headroom.toFixed(1)}%</td>
            </tr>
        </table>
        
        <h5>Performance Metrics (Little's Law)</h5>
        <table>
            <tr>
                <td>Average Response Time:</td>
                <td>${utilization < 1 ? responseTime.toFixed(1) + ' ms' : 'UNSTABLE'}</td>
            </tr>
            <tr>
                <td>Average Queue Length:</td>
                <td>${utilization < 1 ? queueLength.toFixed(1) + ' requests' : 'UNBOUNDED'}</td>
            </tr>
            <tr>
                <td>Average Queue Wait:</td>
                <td>${utilization < 1 ? queueWait.toFixed(1) + ' ms' : 'INFINITE'}</td>
            </tr>
        </table>
        
        <h5>Recommendations</h5>
        <table>
            <tr>
                <td>Servers for ${(targetUtil*100).toFixed(0)}% utilization:</td>
                <td><strong>${requiredServers}</strong></td>
            </tr>
            <tr>
                <td>Add servers:</td>
                <td>${Math.max(0, requiredServers - servers)}</td>
            </tr>
            <tr>
                <td>Safe maximum load:</td>
                <td>${(serviceRate * requiredServers * targetUtil).toFixed(0)} req/s</td>
            </tr>
        </table>
        
        <div class="insight-box">
            <h5>💡 Insights</h5>
            <ul>
                ${utilization > targetUtil ? '<li class="warning">⚠️ System is over target utilization!</li>' : ''}
                ${utilization > 0.8 ? '<li>Response times increase exponentially above 80% utilization</li>' : ''}
                ${headroom < 20 ? '<li>Limited headroom for traffic spikes</li>' : ''}
                <li>Each server can handle ${serviceRate.toFixed(1)} req/s</li>
                <li>Total system capacity: ${totalServiceRate.toFixed(0)} req/s</li>
            </ul>
        </div>
    `;
    
    // Draw saturation curve
    drawSaturationCurve(serviceTimeMs, utilization);
}

function drawSaturationCurve(baseServiceTime, currentUtil) {
    const canvas = document.getElementById('saturation-chart');
    const ctx = canvas.getContext('2d');
    canvas.style.display = 'block';
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set up dimensions
    const padding = 40;
    const width = canvas.width - 2 * padding;
    const height = canvas.height - 2 * padding;
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();
    
    // Draw saturation curve
    ctx.strokeStyle = '#5448C8';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    for (let u = 0; u <= 0.99; u += 0.01) {
        const responseTime = baseServiceTime / (1 - u);
        const x = padding + (u * width);
        const y = canvas.height - padding - (Math.min(responseTime, baseServiceTime * 20) / (baseServiceTime * 20) * height);
        
        if (u === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
    
    // Mark current utilization
    if (currentUtil < 1) {
        const currentX = padding + (currentUtil * width);
        const currentY = canvas.height - padding - (Math.min(baseServiceTime / (1 - currentUtil), baseServiceTime * 20) / (baseServiceTime * 20) * height);
        
        ctx.fillStyle = currentUtil > 0.8 ? '#ff4444' : '#44ff44';
        ctx.beginPath();
        ctx.arc(currentX, currentY, 6, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = '14px Arial';
    ctx.fillText('Utilization (%)', canvas.width / 2 - 40, canvas.height - 10);
    ctx.save();
    ctx.translate(15, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Response Time', -60, 0);
    ctx.restore();
    
    // Title
    ctx.font = '16px Arial';
    ctx.fillText('Response Time vs Utilization (Saturation Curve)', padding, 25);
}

// Legacy script disabled
</script>

## Capacity Planning Fundamentals

### Little's Law

<div class="formula-box">
<h4>The Universal Law of Queues</h4>

**L = λ × W**

Where:
- **L** = Average number of items in the system
- **λ** (lambda) = Average arrival rate
- **W** = Average time in system

**Variations**:
- Queue Length: **Lq = λ × Wq** (items in queue only)
- In Service: **Ls = λ × Ws** (items being served)

**Example**: 
- 100 requests/second arriving (λ)
- 50ms average response time (W)
- Average 5 requests in system (L)
</div>

### Utilization and Response Time

<div class="formula-box">
<h4>M/M/1 Queue Response Time</h4>

**R = S / (1 - ρ)**

Where:
- **R** = Response time
- **S** = Service time
- **ρ** (rho) = Utilization (λ/μ)

**Key Points**:
- At 50% utilization: response time = 2x service time
- At 80% utilization: response time = 5x service time
- At 90% utilization: response time = 10x service time
- Above 90%: exponential growth
</div>

## Capacity Planning Strategies

### 1. The 70% Rule

<div class="strategy-box">
<h4>Target 70% Utilization</h4>

**Why 70%?**
- Provides headroom for spikes (1.4x capacity)
- Keeps response times reasonable (2.3x base)
- Allows for maintenance and failures
- Cost-effective balance

**When to adjust:**
- Batch processing: Can go to 85-90%
- User-facing: Stay at 60-70%
- Critical systems: May need 50-60%
</div>

### 2. N+1 and N+2 Planning

<div class="strategy-box">
<h4>Redundancy Planning</h4>

**N+1**: Can lose one unit
- Minimum for high availability
- Utilization = N/(N+1) at full load

**N+2**: Can lose two units
- For critical systems
- Allows maintenance + failure
- Utilization = N/(N+2) at full load

**Example** (1000 req/s, 100 req/s per server):
- Minimum: 10 servers
- N+1: 11 servers (91% util at peak)
- N+2: 12 servers (83% util at peak)
- 70% target: 15 servers
</div>

### 3. Peak Planning

<div class="strategy-box">
<h4>Handle Traffic Patterns</h4>

**Daily Patterns**:
- Typical peak: 2-3x average
- Plan for: 3-4x average
- Auto-scale between bounds

**Special Events**:
- Black Friday: 10-20x normal
- Breaking news: 50-100x normal
- Game launches: 100x+ normal

**Strategies**:
- Pre-scaling for known events
- Graceful degradation
- Queue and retry patterns
</div>

## Implementation Examples

### Python Capacity Model

```python
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CapacityScenario:
    name: str
    arrival_rate: float  # requests/second
    service_time: float  # seconds
    servers: int
    
class CapacityPlanner:
    def __init__(self):
        self.scenarios = []
    
    def analyze_scenario(self, scenario: CapacityScenario) -> dict:
        """Analyze a capacity scenario using queueing theory"""
        # Basic calculations
        service_rate = 1 / scenario.service_time
        total_capacity = service_rate * scenario.servers
        utilization = scenario.arrival_rate / total_capacity
        
        # M/M/c queue calculations (approximation for multi-server)
        if scenario.servers == 1:
            # M/M/1 exact formulas
            if utilization < 1:
                avg_response_time = scenario.service_time / (1 - utilization)
                avg_queue_length = utilization / (1 - utilization)
                avg_queue_time = avg_response_time - scenario.service_time
            else:
                avg_response_time = float('inf')
                avg_queue_length = float('inf')
                avg_queue_time = float('inf')
        else:
            # M/M/c approximation
            if utilization < 1:
                # Erlang C formula (simplified)
                p0 = 1 / sum([(scenario.arrival_rate/service_rate)**n / 
                            np.math.factorial(n) for n in range(scenario.servers)])
                
                avg_queue_time = (p0 * (utilization**scenario.servers) / 
                                (np.math.factorial(scenario.servers) * 
                                (1 - utilization)**2)) / scenario.arrival_rate
                avg_response_time = avg_queue_time + scenario.service_time
                avg_queue_length = scenario.arrival_rate * avg_queue_time
            else:
                avg_response_time = float('inf')
                avg_queue_length = float('inf')
                avg_queue_time = float('inf')
        
        return {
            'scenario': scenario.name,
            'utilization': utilization,
            'capacity': total_capacity,
            'headroom': max(0, (total_capacity - scenario.arrival_rate)),
            'avg_response_time': avg_response_time,
            'avg_queue_length': avg_queue_length,
            'avg_queue_time': avg_queue_time,
            'stable': utilization < 1,
            'recommended_servers': self.recommend_servers(
                scenario.arrival_rate, 
                service_rate, 
                target_utilization=0.7
            )
        }
    
    def recommend_servers(self, arrival_rate: float, 
                         service_rate: float, 
                         target_utilization: float = 0.7) -> int:
        """Recommend number of servers for target utilization"""
        return int(np.ceil(arrival_rate / (service_rate * target_utilization)))
    
    def capacity_curve(self, max_load: float, 
                      service_time: float, 
                      servers: int) -> List[Tuple[float, float]]:
        """Generate utilization vs response time curve"""
        curve = []
        service_rate = 1 / service_time
        
        for load in np.linspace(0, max_load, 100):
            utilization = load / (service_rate * servers)
            if utilization < 0.99:
                response_time = service_time / (1 - utilization)
                curve.append((utilization, response_time))
            else:
                curve.append((utilization, float('inf')))
                
        return curve

# Usage example
planner = CapacityPlanner()

# Analyze current state
current = CapacityScenario(
    name="Current Production",
    arrival_rate=1000,  # 1000 req/s
    service_time=0.05,  # 50ms
    servers=60
)

result = planner.analyze_scenario(current)
print(f"Current utilization: {result['utilization']:.1%}")
print(f"Recommended servers: {result['recommended_servers']}")

# Plan for growth
growth_scenarios = [
    CapacityScenario("6 months", 1500, 0.05, 60),
    CapacityScenario("1 year", 2000, 0.05, 60),
    CapacityScenario("Peak event", 5000, 0.05, 60)
]

for scenario in growth_scenarios:
    result = planner.analyze_scenario(scenario)
    print(f"\n{scenario.name}:")
    print(f"  Utilization: {result['utilization']:.1%}")
    print(f"  Stable: {result['stable']}")
    print(f"  Need {result['recommended_servers']} servers")
```

### Auto-scaling Logic

```python
class AutoScaler:
    def __init__(self, 
                 min_servers: int = 2,
                 max_servers: int = 100,
                 target_cpu: float = 70.0,
                 scale_up_threshold: float = 80.0,
                 scale_down_threshold: float = 50.0):
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.target_cpu = target_cpu
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_seconds = 300  # 5 minutes
        self.last_scale_time = 0
        
    def decide_scaling(self, 
                      current_servers: int,
                      metrics: dict,
                      current_time: float) -> int:
        """Decide how many servers we should have"""
        
        # Check cooldown
        if current_time - self.last_scale_time < self.cooldown_seconds:
            return current_servers
            
        # Get key metrics
        avg_cpu = metrics.get('avg_cpu', 0)
        avg_response_time = metrics.get('avg_response_time', 0)
        queue_depth = metrics.get('queue_depth', 0)
        
        # Calculate desired servers based on CPU
        if avg_cpu > self.scale_up_threshold:
            # Scale up
            scale_factor = avg_cpu / self.target_cpu
            desired = int(np.ceil(current_servers * scale_factor))
        elif avg_cpu < self.scale_down_threshold:
            # Scale down
            scale_factor = avg_cpu / self.target_cpu
            desired = int(np.floor(current_servers * scale_factor))
        else:
            # No change
            return current_servers
            
        # Apply limits
        desired = max(self.min_servers, min(desired, self.max_servers))
        
        # Conservative scaling
        if desired > current_servers:
            # Scale up faster (add 20% or at least 1)
            change = max(1, int(current_servers * 0.2))
            new_servers = min(current_servers + change, desired)
        else:
            # Scale down slower (remove 10% or at least 1)
            change = max(1, int(current_servers * 0.1))
            new_servers = max(current_servers - change, desired)
            
        if new_servers != current_servers:
            self.last_scale_time = current_time
            
        return new_servers
```

## Best Practices

### 1. Measurement is Key

- Monitor actual utilization continuously
- Track response time percentiles (p50, p95, p99)
- Measure queue depths
- Record scaling events

### 2. Plan for Failure

- N+1 minimum for availability
- Test failure scenarios
- Graceful degradation paths
- Circuit breakers for overload

### 3. Cost Optimization

- Right-size instances
- Use spot/preemptible for batch
- Schedule scaling for known patterns
- Consider reserved capacity discounts

## Key Takeaways

1. **70% Rule**: Target 70% utilization for production
2. **Little's Law**: L = λW is universal
3. **Exponential Growth**: Response time explodes near 100%
4. **Plan for Peaks**: Size for maximum, scale for average
5. **Monitor Everything**: You can't optimize what you don't measure

## Related Resources

- [Axiom 2: Capacity](../part1-axioms/axiom-2-capacity/index.md)
- [Failure Calculator](failure-calculator.md)
- [Performance Tuning Guide](../reference/performance-tuning.md)