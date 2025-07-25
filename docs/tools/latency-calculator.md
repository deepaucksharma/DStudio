# Latency Calculator

<div class="calculator-container">
<div class="calc-header">
<h2>⏱️ End-to-End Latency Calculator</h2>
<p>Calculate total system latency including network delays, processing time, and queueing effects.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="latencyCalc">

### Network Latency
<div class="input-group">
<label for="distance">Distance between nodes (km):</label>
<input type="number" id="distance" value="1000" min="0" step="100">
<span class="help">Speed of light in fiber: ~200,000 km/s</span>
</div>

<div class="input-group">
<label for="hops">Number of network hops:</label>
<input type="number" id="hops" value="5" min="1" step="1">
<span class="help">Each hop adds routing delay</span>
</div>

<div class="input-group">
<label for="hopDelay">Per-hop delay (ms):</label>
<input type="number" id="hopDelay" value="0.5" min="0" step="0.1">
</div>

### Processing Time
<div class="input-group">
<label for="serviceTime">Service time per request (ms):</label>
<input type="number" id="serviceTime" value="10" min="0" step="1">
<span class="help">Time to process when not queued</span>
</div>

<div class="input-group">
<label for="throughput">Request rate (req/sec):</label>
<input type="number" id="throughput" value="80" min="0" step="10">
</div>

<div class="input-group">
<label for="servers">Number of servers:</label>
<input type="number" id="servers" value="1" min="1" step="1">
</div>

### Additional Delays
<div class="input-group">
<label for="serialization">Serialization/Deserialization (ms):</label>
<input type="number" id="serialization" value="2" min="0" step="0.5">
</div>

<div class="input-group">
<label for="diskIO">Disk I/O time (ms):</label>
<input type="number" id="diskIO" value="5" min="0" step="1">
</div>

<button type="button" onclick="calculateLatency()" class="calc-button">Calculate Latency</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## Understanding the Components

### 1. Network Latency
- **Speed of Light Delay**: Fundamental physics limit (~5ms per 1000km in fiber)
- **Routing Delays**: Each network hop adds processing time
- **Protocol Overhead**: TCP handshakes, packet headers

### 2. Processing Latency
- **Service Time**: CPU time needed to handle request
- **Queueing Delay**: Wait time when system is under load (Little's Law)
- **Concurrency Effects**: Contention for shared resources

### 3. I/O Latency
- **Disk Access**: SSD (~0.1ms) vs HDD (~10ms)
- **Database Queries**: Network + query processing
- **Cache Misses**: RAM vs disk access time difference

## Latency Reduction Strategies

Based on your calculated results, consider these optimizations:

<div class="strategy-grid">
<div class="strategy-card">
<h4>🌍 Reduce Distance</h4>
<ul>
<li>Deploy edge servers</li>
<li>Use CDNs</li>
<li>Multi-region deployment</li>
</ul>
</div>

<div class="strategy-card">
<h4>🔄 Minimize Hops</h4>
<ul>
<li>Direct peering</li>
<li>Optimize routing</li>
<li>Reduce microservice calls</li>
</ul>
</div>

<div class="strategy-card">
<h4>⚡ Speed Processing</h4>
<ul>
<li>Optimize algorithms</li>
<li>Add caching layers</li>
<li>Parallelize work</li>
</ul>
</div>

<div class="strategy-card">
<h4>📊 Handle Load</h4>
<ul>
<li>Auto-scaling</li>
<li>Load balancing</li>
<li>Request prioritization</li>
</ul>
</div>
</div>

## Mathematical Foundation

This calculator uses several key formulas:

### Network Delay
```
Network Delay = (Distance / Speed of Light) + (Hops × Hop Delay)
```

### Queueing Delay (M/M/c model)
```
ρ = λ / (c × μ)  // Utilization
Lq = Queue Length (complex formula based on ρ)
Wq = Lq / λ      // Little's Law
```

Where:
- λ = arrival rate (requests/sec)
- μ = service rate (1/service_time)
- c = number of servers

### Total Latency
```
Total = Network + Queueing + Processing + Serialization + I/O
```

## Real-World Examples

<div class="example-box">
<h4>Example 1: Cross-Region API Call</h4>
<ul>
<li>Distance: 5000km (US East to West)</li>
<li>Network: 25ms (speed of light)</li>
<li>Processing: 10ms</li>
<li>Total: ~40ms best case</li>
</ul>
</div>

<div class="example-box">
<h4>Example 2: Microservices Chain</h4>
<ul>
<li>5 service hops</li>
<li>10ms per service</li>
<li>2ms network each</li>
<li>Total: ~60ms</li>
</ul>
</div>

## Related Resources

- [Little's Law in Practice](/quantitative/littles-law)
- [Latency Numbers Every Programmer Should Know](/quantitative/latency-ladder)
- [Performance Patterns](/patterns/#performance-scaling)
- Network Optimization Pattern (Coming Soon)

<script>
// Global variables for chart
let latencyChart = null;

function validateLatencyInputs() {
    const inputs = {
        distance: { value: parseFloat(document.getElementById('distance').value), min: 0, max: 40000, name: 'Distance' },
        hops: { value: parseInt(document.getElementById('hops').value), min: 1, max: 100, name: 'Network hops' },
        hopDelay: { value: parseFloat(document.getElementById('hopDelay').value), min: 0, max: 100, name: 'Hop delay' },
        serviceTime: { value: parseFloat(document.getElementById('serviceTime').value), min: 0.1, max: 10000, name: 'Service time' },
        throughput: { value: parseFloat(document.getElementById('throughput').value), min: 0, max: 1000000, name: 'Request rate' },
        servers: { value: parseInt(document.getElementById('servers').value), min: 1, max: 1000, name: 'Servers' },
        serialization: { value: parseFloat(document.getElementById('serialization').value), min: 0, max: 1000, name: 'Serialization' },
        diskIO: { value: parseFloat(document.getElementById('diskIO').value), min: 0, max: 10000, name: 'Disk I/O' }
    };
    
    const errors = [];
    
    for (const [key, input] of Object.entries(inputs)) {
        if (isNaN(input.value)) {
            errors.push(`${input.name} must be a number`);
        } else if (input.value < input.min || input.value > input.max) {
            errors.push(`${input.name} must be between ${input.min} and ${input.max}`);
        }
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function calculateLatency() {
    // Clear any previous error messages
    const errorDiv = document.getElementById('error-messages');
    if (errorDiv) errorDiv.innerHTML = '';
    
    // Validate inputs
    const validation = validateLatencyInputs();
    if (!validation.valid) {
        displayErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    
    // Calculate network delay
    const speedOfLight = 200000; // km/s in fiber
    const propagationDelay = (inputs.distance.value / speedOfLight) * 1000; // convert to ms
    const routingDelay = inputs.hops.value * inputs.hopDelay.value;
    const networkDelay = propagationDelay + routingDelay;
    
    // Calculate queueing delay using M/M/c approximation
    const serviceRate = 1000 / inputs.serviceTime.value; // requests per second
    const utilization = inputs.throughput.value / (inputs.servers.value * serviceRate);
    
    let queueingDelay = 0;
    if (utilization < 1 && utilization > 0) {
        // More accurate M/M/c waiting time calculation
        queueingDelay = calculateMMcQueueingDelay(
            inputs.throughput.value,
            serviceRate,
            inputs.servers.value,
            utilization
        );
    } else if (utilization >= 1) {
        queueingDelay = Infinity;
    }
    
    // Total latency
    const totalLatency = networkDelay + inputs.serviceTime.value + queueingDelay + 
                        inputs.serialization.value + inputs.diskIO.value;
    
    // Prepare data for visualization
    const latencyComponents = [
        { name: 'Network Propagation', value: propagationDelay, color: '#5448C8' },
        { name: 'Routing Delays', value: routingDelay, color: '#7B68EE' },
        { name: 'Processing Time', value: inputs.serviceTime.value, color: '#00BCD4' },
        { name: 'Queueing Delay', value: utilization < 1 ? queueingDelay : 0, color: '#FF9800' },
        { name: 'Serialization', value: inputs.serialization.value, color: '#4CAF50' },
        { name: 'Disk I/O', value: inputs.diskIO.value, color: '#F44336' }
    ];
    
    // Display results
    displayLatencyResults(latencyComponents, totalLatency, utilization, inputs);
    
    // Draw interactive chart
    drawLatencyChart(latencyComponents, totalLatency);
    
    // Show results panel with animation
    const resultsPanel = document.getElementById('results');
    resultsPanel.style.display = 'block';
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function calculateMMcQueueingDelay(arrivalRate, serviceRate, servers, utilization) {
    // Erlang C formula for M/M/c queue
    const rho = utilization;
    const c = servers;
    const a = arrivalRate / serviceRate;
    
    // Calculate P0 (probability of empty system)
    let sum = 0;
    for (let k = 0; k < c; k++) {
        sum += Math.pow(a, k) / factorial(k);
    }
    sum += (Math.pow(a, c) / factorial(c)) * (1 / (1 - rho));
    const p0 = 1 / sum;
    
    // Calculate Pq (probability of queueing)
    const pq = (Math.pow(a, c) / (factorial(c) * (1 - rho))) * p0;
    
    // Calculate average waiting time in queue
    const wq = (pq / (c * serviceRate * (1 - rho))) * 1000; // Convert to ms
    
    return wq;
}

function displayLatencyResults(components, totalLatency, utilization, inputs) {
    let resultsHTML = `
        <h3>📊 Latency Breakdown</h3>
        <div class="latency-summary">
            <div class="summary-card ${utilization >= 1 ? 'error' : utilization > 0.8 ? 'warning' : 'success'}">
                <div class="card-header">Total Latency</div>
                <div class="card-value">${utilization < 1 ? totalLatency.toFixed(2) : '∞'} ms</div>
                <div class="card-subtitle">System Utilization: ${(utilization * 100).toFixed(1)}%</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="latencyChart" width="800" height="400"></canvas>
        </div>
        
        <div class="latency-breakdown">
    `;
    
    // Add detailed breakdown with animated bars
    components.forEach((component, index) => {
        const percentage = utilization < 1 ? (component.value / totalLatency * 100) : 
                          component.name === 'Queueing Delay' ? 100 : 0;
        resultsHTML += `
            <div class="latency-item" style="animation-delay: ${index * 0.1}s">
                <div class="item-header">
                    <span class="label">${component.name}:</span>
                    <span class="value">${component.value.toFixed(2)} ms</span>
                </div>
                <div class="bar-container">
                    <div class="bar" style="width: 0%; background: ${component.color};" 
                         data-width="${percentage}%"></div>
                    <span class="percentage">${percentage.toFixed(1)}%</span>
                </div>
            </div>
        `;
    });
    
    resultsHTML += `
        </div>
        
        <div class="insights">
            <h4>💡 Insights & Recommendations</h4>
            <ul>
    `;
    
    // Generate intelligent insights
    const insights = generateLatencyInsights(components, totalLatency, utilization, inputs);
    insights.forEach(insight => {
        resultsHTML += `<li class="${insight.type}">${insight.message}</li>`;
    });
    
    resultsHTML += `
            </ul>
        </div>
        
        <div class="interactive-analysis">
            <h4>🔍 What-If Analysis</h4>
            <div class="analysis-grid">
                <div class="analysis-card">
                    <h5>Reduce Distance by 50%</h5>
                    <p>Latency reduction: <strong>${(components[0].value * 0.5).toFixed(1)} ms</strong></p>
                    <p class="suggestion">Deploy in ${inputs.distance.value < 5000 ? 'edge locations' : 'regional data centers'}</p>
                </div>
                <div class="analysis-card">
                    <h5>Double Server Count</h5>
                    <p>New utilization: <strong>${(utilization * 50).toFixed(1)}%</strong></p>
                    <p class="suggestion">${utilization > 0.5 ? 'Significant improvement' : 'Marginal benefit'}</p>
                </div>
                <div class="analysis-card">
                    <h5>Optimize Processing</h5>
                    <p>If reduced by 30%: <strong>-${(inputs.serviceTime.value * 0.3).toFixed(1)} ms</strong></p>
                    <p class="suggestion">Focus on ${inputs.serviceTime.value > 20 ? 'algorithm optimization' : 'caching'}</p>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('results').innerHTML = resultsHTML;
    
    // Animate progress bars after a short delay
    setTimeout(() => {
        document.querySelectorAll('.bar').forEach(bar => {
            bar.style.width = bar.getAttribute('data-width');
        });
    }, 100);
}

function generateLatencyInsights(components, totalLatency, utilization, inputs) {
    const insights = [];
    
    // Utilization insights
    if (utilization >= 1) {
        insights.push({
            type: 'error',
            message: '⚠️ CRITICAL: System is overloaded! Requests will queue indefinitely. Immediate action required.'
        });
    } else if (utilization > 0.8) {
        insights.push({
            type: 'warning',
            message: '⚠️ High utilization detected. System vulnerable to traffic spikes. Consider scaling soon.'
        });
    } else if (utilization < 0.3) {
        insights.push({
            type: 'info',
            message: 'ℹ️ Low utilization indicates over-provisioning. Consider reducing servers to save costs.'
        });
    }
    
    // Component-specific insights
    const dominantComponent = components.reduce((prev, current) => 
        prev.value > current.value ? prev : current
    );
    
    if (dominantComponent.name === 'Network Propagation' && dominantComponent.value > totalLatency * 0.4) {
        insights.push({
            type: 'important',
            message: `Network distance dominates latency (${(dominantComponent.value / totalLatency * 100).toFixed(0)}%). Consider CDN or edge deployment.`
        });
    }
    
    if (components[3].value > totalLatency * 0.3 && utilization < 1) { // Queueing delay
        insights.push({
            type: 'warning',
            message: 'Significant queueing delays detected. Add servers or optimize processing time.'
        });
    }
    
    if (inputs.diskIO.value > inputs.serviceTime.value) {
        insights.push({
            type: 'important',
            message: 'I/O time exceeds processing time. Consider SSD storage, caching, or async I/O.'
        });
    }
    
    // Network optimization
    if (inputs.hops.value > 10) {
        insights.push({
            type: 'info',
            message: `High hop count (${inputs.hops.value}). Consider direct peering or optimized routing.`
        });
    }
    
    // Best practices
    if (totalLatency < 100 && utilization < 0.7) {
        insights.push({
            type: 'success',
            message: '✅ Excellent performance! System is well-optimized for current load.'
        });
    }
    
    return insights;
}

function drawLatencyChart(components, totalLatency) {
    const canvas = document.getElementById('latencyChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Clear previous chart
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Configuration
    const padding = 60;
    const width = canvas.width;
    const height = canvas.height;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // Draw axes
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw pie chart for component breakdown
    const centerX = width * 0.3;
    const centerY = height * 0.5;
    const radius = Math.min(chartWidth, chartHeight) * 0.3;
    
    let currentAngle = -Math.PI / 2;
    
    components.forEach((component, index) => {
        const percentage = component.value / totalLatency;
        const angle = percentage * 2 * Math.PI;
        
        // Draw slice
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + angle);
        ctx.closePath();
        ctx.fillStyle = component.color;
        ctx.fill();
        
        // Draw label if slice is large enough
        if (percentage > 0.05) {
            const labelAngle = currentAngle + angle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
            const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
            
            ctx.fillStyle = 'white';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`${(percentage * 100).toFixed(0)}%`, labelX, labelY);
        }
        
        currentAngle += angle;
    });
    
    // Draw legend
    const legendX = width * 0.6;
    let legendY = padding;
    
    ctx.font = '14px sans-serif';
    components.forEach((component, index) => {
        // Color box
        ctx.fillStyle = component.color;
        ctx.fillRect(legendX, legendY, 20, 15);
        
        // Label
        ctx.fillStyle = '#333';
        ctx.textAlign = 'left';
        ctx.fillText(`${component.name}: ${component.value.toFixed(1)} ms`, legendX + 30, legendY + 12);
        
        legendY += 25;
    });
    
    // Title
    ctx.font = 'bold 16px sans-serif';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';
    ctx.fillText('Latency Component Distribution', width / 2, 30);
}

function displayErrors(errors) {
    let errorHTML = '<div class="error-container"><h4>⚠️ Input Validation Errors</h4><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = errorHTML;
    resultsDiv.style.display = 'block';
}

function factorial(n) {
    if (n <= 1) return 1;
    if (n > 170) return Infinity; // Prevent overflow
    return n * factorial(n - 1);
}

// Add real-time input validation
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            
            if (isNaN(value) || value < min || value > max) {
                this.style.borderColor = '#ff6b6b';
            } else {
                this.style.borderColor = '#51cf66';
            }
        });
    });
});
</script>

</div>