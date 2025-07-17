# Tools & Calculators

!!! info "Interactive Tools"
    These calculators help you apply the concepts from the axioms and pillars to real-world scenarios.

!!! tip "Quick Navigation"
    [← Home](../index.md) |
    [Latency Calculator →](latency-calculator.md) |
    [Capacity Planner →](capacity-planner.md)

## Available Tools

<div class="grid cards">
  <div class="card">
    <h3>🌍 Latency Calculator</h3>
    <p>Calculate theoretical and practical latencies based on distance, network hops, and processing time.</p>
    <a href="latency-calculator/" class="md-button md-button--primary">Calculate Latency</a>
  </div>

  <div class="card">
    <h3>📊 Capacity Planner</h3>
    <p>Plan system capacity using Little's Law and queueing theory. Visualize saturation curves.</p>
    <a href="capacity-planner/" class="md-button md-button--primary">Plan Capacity</a>
  </div>

  <div class="card">
    <h3>🎯 Failure Probability Calculator</h3>
    <p>Calculate system reliability based on component failure rates and redundancy levels.</p>
    <a href="failure-calculator/" class="md-button md-button--primary">Calculate Reliability</a>
  </div>

  <div class="card">
    <h3>💰 Coordination Cost Estimator</h3>
    <p>Estimate the overhead of different coordination patterns in your system.</p>
    <a href="coordination-cost/" class="md-button md-button--primary">Estimate Costs</a>
  </div>
</div>

## Quick Reference Calculators

### Speed of Light Latency

<div class="calculator-box">
<h4>Minimum Theoretical Latency</h4>

**Formula**: `latency = distance / (speed_of_light * medium_factor)`

Where:
- Speed of light in vacuum: 299,792 km/s
- Medium factors:
  - Fiber optic: 0.67 (200,000 km/s)
  - Copper: 0.66 (198,000 km/s)
  - Wireless: ~1.0 (299,792 km/s)

**Quick Reference**:
- NYC ↔ SF (~4,100 km): 20.5ms minimum
- NYC ↔ London (~5,600 km): 28ms minimum
- Singapore ↔ Sydney (~6,300 km): 31.5ms minimum
</div>

### Little's Law Calculator

<div class="calculator-box">
<h4>Queue Length Estimation</h4>

**Formula**: `L = λ × W`

Where:
- L = Average number of items in system
- λ = Average arrival rate
- W = Average time in system

**Example**:
- 100 requests/second arriving
- 50ms average processing time
- Queue length = 100 × 0.05 = 5 requests
</div>

### Availability Calculator

<div class="calculator-box">
<h4>System Availability</h4>

**Single Component**: `A = MTBF / (MTBF + MTTR)`

**Series (AND)**: `A_total = A₁ × A₂ × ... × Aₙ`

**Parallel (OR)**: `A_total = 1 - (1-A₁) × (1-A₂) × ... × (1-Aₙ)`

**Quick Reference**:
- 99.9% (three nines) = 8.76 hours downtime/year
- 99.99% (four nines) = 52.56 minutes downtime/year
- 99.999% (five nines) = 5.26 minutes downtime/year
</div>

## Implementation Examples

### Python Latency Calculator

```python
class LatencyCalculator:
    SPEED_OF_LIGHT = 299792  # km/s
    
    MEDIUM_FACTORS = {
        'fiber': 0.67,
        'copper': 0.66,
        'wireless': 1.0
    }
    
    PROCESSING_OVERHEAD = {
        'switch': 0.01,    # 10μs
        'router': 0.1,     # 100μs
        'firewall': 0.5,   # 500μs
        'load_balancer': 0.2  # 200μs
    }
    
    @staticmethod
    def calculate_propagation_delay(distance_km, medium='fiber'):
        """Calculate propagation delay in milliseconds"""
        effective_speed = LatencyCalculator.SPEED_OF_LIGHT * \
                         LatencyCalculator.MEDIUM_FACTORS.get(medium, 1.0)
        return (distance_km / effective_speed) * 1000  # Convert to ms
    
    @staticmethod
    def calculate_total_latency(distance_km, hops, devices=None):
        """Calculate total latency including processing"""
        # Propagation delay
        prop_delay = LatencyCalculator.calculate_propagation_delay(distance_km)
        
        # Processing delay
        proc_delay = 0
        if devices:
            for device, count in devices.items():
                overhead = LatencyCalculator.PROCESSING_OVERHEAD.get(device, 0)
                proc_delay += overhead * count
        
        # Serialization delay (simplified)
        serialization_delay = 0.1 * hops  # 100μs per hop
        
        return {
            'propagation_ms': round(prop_delay, 2),
            'processing_ms': round(proc_delay, 2),
            'serialization_ms': round(serialization_delay, 2),
            'total_ms': round(prop_delay + proc_delay + serialization_delay, 2)
        }

# Usage
calc = LatencyCalculator()
result = calc.calculate_total_latency(
    distance_km=4100,  # NYC to SF
    hops=15,
    devices={'router': 10, 'firewall': 2, 'load_balancer': 2}
)
print(f"Total latency: {result['total_ms']}ms")
```

### JavaScript Capacity Planner

```javascript
class CapacityPlanner {
    constructor() {
        this.littlesLaw = {
            queueLength: (arrivalRate, serviceTime) => arrivalRate * serviceTime,
            responseTime: (queueLength, arrivalRate) => queueLength / arrivalRate,
            throughput: (queueLength, responseTime) => queueLength / responseTime
        };
    }
    
    calculateUtilization(arrivalRate, serviceRate, servers = 1) {
        return arrivalRate / (serviceRate * servers);
    }
    
    calculateQueueProbability(utilization, servers = 1) {
        // M/M/c queue probability formulas
        if (servers === 1) {
            // M/M/1 queue
            return {
                p0: 1 - utilization,  // Probability of empty system
                avgQueue: (utilization * utilization) / (1 - utilization),
                avgSystem: utilization / (1 - utilization),
                avgWait: utilization / (serviceRate * (1 - utilization))
            };
        }
        // Simplified for multiple servers
        return {
            utilization: utilization,
            stable: utilization < 1
        };
    }
    
    recommendCapacity(peakLoad, targetUtilization = 0.7, growthRate = 0.2) {
        const currentRequired = Math.ceil(peakLoad / targetUtilization);
        const futureRequired = Math.ceil(currentRequired * (1 + growthRate));
        
        return {
            current: currentRequired,
            future: futureRequired,
            headroom: (currentRequired - peakLoad) / currentRequired * 100
        };
    }
}

// Usage
const planner = new CapacityPlanner();
const capacity = planner.recommendCapacity(
    peakLoad = 1000,  // requests/second
    targetUtilization = 0.7,
    growthRate = 0.3
);
console.log(`Recommended capacity: ${capacity.current} servers`);
```

## Best Practices for Tool Usage

1. **Always Add Safety Margins**
   - Theoretical calculations are best-case
   - Real-world adds 20-50% overhead
   - Plan for peak, not average

2. **Consider All Components**
   - Network is often not the bottleneck
   - Processing and queueing dominate
   - Don't forget serialization delay

3. **Validate with Measurements**
   - Tools provide estimates
   - Always verify with real data
   - Monitor continuously

4. **Account for Failures**
   - Calculate degraded mode capacity
   - Plan for n-1 or n-2 scenarios
   - Include recovery time

## Next Steps

- Try the [Interactive Calculators](latency-calculator.md)
- Review [Reference Sheets](../reference/index.md)
- Apply to your [System Design](../part2-pillars/index.md)