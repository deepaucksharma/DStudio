# Throughput Optimizer

<div class="calculator-container">
<div class="calc-header">
<h2>🚀 Throughput Optimization Calculator</h2>
<p>Find optimal batch sizes, concurrency levels, and pipeline configurations for maximum throughput.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="throughputCalc">

### System Characteristics
<div class="input-group">
<label for="taskTime">Average task processing time (ms):</label>
<input type="number" id="taskTime" value="50" min="1" step="10">
</div>

<div class="input-group">
<label for="setupTime">Setup/teardown time per batch (ms):</label>
<input type="number" id="setupTime" value="100" min="0" step="10">
<span class="help">Connection setup, initialization, etc.</span>
</div>

<div class="input-group">
<label for="maxConcurrency">Maximum concurrent workers:</label>
<input type="number" id="maxConcurrency" value="10" min="1" max="1000" step="1">
</div>

<div class="input-group">
<label for="coordinationOverhead">Coordination overhead (%):</label>
<input type="number" id="coordinationOverhead" value="5" min="0" max="50" step="1">
<span class="help">Based on Universal Scalability Law</span>
</div>

### Resource Constraints
<div class="input-group">
<label for="memoryPerTask">Memory per task (MB):</label>
<input type="number" id="memoryPerTask" value="10" min="0.1" step="1">
</div>

<div class="input-group">
<label for="totalMemory">Total available memory (GB):</label>
<input type="number" id="totalMemory" value="16" min="1" step="1">
</div>

<div class="input-group">
<label for="networkBandwidth">Network bandwidth (Mbps):</label>
<input type="number" id="networkBandwidth" value="1000" min="10" step="100">
</div>

<div class="input-group">
<label for="payloadSize">Average payload size (KB):</label>
<input type="number" id="payloadSize" value="100" min="1" step="10">
</div>

### Optimization Goals
<div class="input-group">
<label for="optimizeFor">Optimize for:</label>
<select id="optimizeFor">
<option value="throughput">Maximum Throughput</option>
<option value="latency">Minimum Latency</option>
<option value="efficiency">Resource Efficiency</option>
<option value="cost">Minimum Cost</option>
</select>
</div>

<button type="button" onclick="calculateThroughput()" class="calc-button">Calculate Optimal Configuration</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## Throughput Optimization Principles

### 1. Amdahl's Law
```
Speedup = 1 / (s + p/n)

Where:
- s = serial fraction
- p = parallel fraction
- n = number of processors
```

### 2. Universal Scalability Law
```
C(N) = N / (1 + α(N-1) + βN(N-1))

Where:
- N = concurrency level
- α = contention coefficient
- β = coherence coefficient
```

### 3. Little's Law for Throughput
```
Throughput = Concurrency / Response Time
```

## Optimization Strategies

<div class="strategy-grid">
<div class="strategy-card">
<h4>📦 Batching</h4>
<ul>
<li>Amortize fixed costs</li>
<li>Reduce context switches</li>
<li>Improve cache locality</li>
<li>Network efficiency</li>
</ul>
<p><strong>Trade-off:</strong> Latency vs throughput</p>
</div>

<div class="strategy-card">
<h4>🔄 Pipelining</h4>
<ul>
<li>Stage parallelism</li>
<li>Hide I/O latency</li>
<li>CPU/GPU overlap</li>
<li>Async processing</li>
</ul>
<p><strong>Trade-off:</strong> Complexity vs performance</p>
</div>

<div class="strategy-card">
<h4>⚡ Concurrency</h4>
<ul>
<li>Thread pools</li>
<li>Async/await</li>
<li>Work stealing</li>
<li>Lock-free algorithms</li>
</ul>
<p><strong>Trade-off:</strong> Coordination vs speedup</p>
</div>

<div class="strategy-card">
<h4>💾 Caching</h4>
<ul>
<li>Result caching</li>
<li>Connection pooling</li>
<li>Precomputation</li>
<li>Memoization</li>
</ul>
<p><strong>Trade-off:</strong> Memory vs computation</p>
</div>
</div>

## Common Bottlenecks

<div class="bottleneck-list">
<div class="bottleneck-item">
<span class="icon">🔒</span>
<strong>Lock Contention</strong>
<p>Threads waiting for shared resources. Solution: Reduce critical sections, use lock-free structures.</p>
</div>

<div class="bottleneck-item">
<span class="icon">💾</span>
<strong>Memory Bandwidth</strong>
<p>Data transfer limitations. Solution: Improve cache locality, reduce memory footprint.</p>
</div>

<div class="bottleneck-item">
<span class="icon">🌐</span>
<strong>Network I/O</strong>
<p>Bandwidth or latency limits. Solution: Compression, batching, connection pooling.</p>
</div>

<div class="bottleneck-item">
<span class="icon">💽</span>
<strong>Disk I/O</strong>
<p>Storage speed limitations. Solution: SSDs, write batching, async I/O.</p>
</div>
</div>

## Related Resources

- [Universal Scalability Law](/quantitative/universal-scalability)
- [Little's Law](/quantitative/littles-law)
- [Performance Modeling](/quantitative/performance-modeling)
- [Load Balancing Pattern](/patterns/load-balancing)
- Queue Performance (Coming Soon)

<script>
function calculateThroughput() {
    // Get inputs
    const taskTime = parseFloat(document.getElementById('taskTime').value);
    const setupTime = parseFloat(document.getElementById('setupTime').value);
    const maxConcurrency = parseInt(document.getElementById('maxConcurrency').value);
    const coordinationOverhead = parseFloat(document.getElementById('coordinationOverhead').value) / 100;
    const memoryPerTask = parseFloat(document.getElementById('memoryPerTask').value);
    const totalMemory = parseFloat(document.getElementById('totalMemory').value) * 1024; // Convert to MB
    const networkBandwidth = parseFloat(document.getElementById('networkBandwidth').value);
    const payloadSize = parseFloat(document.getElementById('payloadSize').value);
    const optimizeFor = document.getElementById('optimizeFor').value;
    
    // Calculate constraints
    const memoryConstrainedConcurrency = Math.floor(totalMemory / memoryPerTask);
    const effectiveConcurrency = Math.min(maxConcurrency, memoryConstrainedConcurrency);
    
    // Calculate optimal batch sizes for different scenarios
    let optimalConfigs = [];
    
    for (let batchSize = 1; batchSize <= 1000; batchSize *= 2) {
        for (let concurrency = 1; concurrency <= effectiveConcurrency; concurrency++) {
            // Apply Universal Scalability Law
            const alpha = coordinationOverhead;
            const beta = coordinationOverhead / 10; // Coherence is typically smaller
            const scalability = concurrency / (1 + alpha * (concurrency - 1) + beta * concurrency * (concurrency - 1));
            
            // Calculate effective processing time
            const batchProcessingTime = batchSize * taskTime + setupTime;
            const effectiveTaskTime = batchProcessingTime / batchSize;
            
            // Calculate throughput
            const singleThreadThroughput = 1000 / effectiveTaskTime; // tasks per second
            const totalThroughput = singleThreadThroughput * scalability;
            
            // Calculate latency
            const queueTime = batchSize * taskTime / (2 * concurrency); // Average queue time
            const totalLatency = effectiveTaskTime + queueTime;
            
            // Calculate network usage
            const networkUsage = (totalThroughput * payloadSize * 8) / 1000; // Mbps
            const networkUtilization = networkUsage / networkBandwidth;
            
            // Calculate efficiency
            const efficiency = scalability / concurrency;
            const costEfficiency = totalThroughput / concurrency; // Throughput per worker
            
            // Score based on optimization goal
            let score;
            switch(optimizeFor) {
                case 'throughput':
                    score = totalThroughput;
                    break;
                case 'latency':
                    score = -totalLatency;
                    break;
                case 'efficiency':
                    score = efficiency * totalThroughput;
                    break;
                case 'cost':
                    score = costEfficiency;
                    break;
            }
            
            if (networkUtilization <= 0.8) { // Don't saturate network
                optimalConfigs.push({
                    batchSize: batchSize,
                    concurrency: concurrency,
                    throughput: totalThroughput,
                    latency: totalLatency,
                    efficiency: efficiency,
                    networkUtilization: networkUtilization,
                    score: score
                });
            }
        }
    }
    
    // Sort by score
    optimalConfigs.sort((a, b) => b.score - a.score);
    const optimal = optimalConfigs[0];
    
    // Generate results
    let resultsHTML = `
        <h3>📊 Throughput Optimization Results</h3>
        
        <div class="optimal-config">
            <h4>Optimal Configuration (${optimizeFor})</h4>
            <div class="config-grid">
                <div class="config-item">
                    <span class="label">Batch Size:</span>
                    <span class="value">${optimal.batchSize}</span>
                </div>
                <div class="config-item">
                    <span class="label">Concurrency:</span>
                    <span class="value">${optimal.concurrency} workers</span>
                </div>
                <div class="config-item">
                    <span class="label">Throughput:</span>
                    <span class="value">${optimal.throughput.toFixed(0)} tasks/sec</span>
                </div>
                <div class="config-item">
                    <span class="label">Latency:</span>
                    <span class="value">${optimal.latency.toFixed(1)} ms</span>
                </div>
                <div class="config-item">
                    <span class="label">Efficiency:</span>
                    <span class="value">${(optimal.efficiency * 100).toFixed(1)}%</span>
                </div>
                <div class="config-item">
                    <span class="label">Network Usage:</span>
                    <span class="value">${(optimal.networkUtilization * 100).toFixed(1)}%</span>
                </div>
            </div>
        </div>
        
        <div class="performance-chart">
            <h4>Throughput vs Concurrency</h4>
            <canvas id="perfChart" width="600" height="300"></canvas>
        </div>
        
        <div class="constraints-analysis">
            <h4>Constraint Analysis</h4>
            <table class="responsive-table">
  <thead>
    <tr>
                    <th>Resource</th>
                    <th>Limit</th>
                    <th>Usage</th>
                    <th>Status</th>
                </tr>
  </thead>
  <tbody>
    <tr>
                    <td data-label="Resource">Memory</td>
                    <td data-label="Limit">${memoryConstrainedConcurrency} concurrent tasks</td>
                    <td data-label="Usage">${optimal.concurrency} workers</td>
                    <td data-label="Status">${optimal.concurrency < memoryConstrainedConcurrency ? '✅ OK' : '⚠️ Limited'}</td>
                </tr>
    <tr>
                    <td data-label="Resource">CPU/Workers</td>
                    <td data-label="Limit">${maxConcurrency} max</td>
                    <td data-label="Usage">${optimal.concurrency} workers</td>
                    <td data-label="Status">${optimal.concurrency < maxConcurrency ? '✅ OK' : '⚠️ At limit'}</td>
                </tr>
    <tr>
                    <td data-label="Resource">Network</td>
                    <td data-label="Limit">${networkBandwidth} Mbps</td>
                    <td data-label="Usage">${(optimal.networkUtilization * networkBandwidth).toFixed(0)} Mbps</td>
                    <td data-label="Status">${optimal.networkUtilization < 0.8 ? '✅ OK' : '⚠️ High usage'}</td>
                </tr>
  </tbody>
</table>
        </div>
        
        <div class="recommendations">
            <h4>💡 Optimization Recommendations</h4>
            <ul>
    `;
    
    // Add specific recommendations
    if (optimal.batchSize > 1) {
        resultsHTML += `<li>Batching ${optimal.batchSize} tasks reduces overhead by ${((1 - taskTime/((optimal.batchSize * taskTime + setupTime)/optimal.batchSize)) * 100).toFixed(0)}%</li>`;
    }
    
    if (optimal.efficiency < 0.7) {
        resultsHTML += '<li class="warning">⚠️ Low efficiency indicates high coordination overhead. Consider reducing contention.</li>';
    }
    
    if (optimal.concurrency < maxConcurrency * 0.5) {
        resultsHTML += '<li>System is not using full concurrency potential. Check for bottlenecks.</li>';
    }
    
    if (memoryConstrainedConcurrency < maxConcurrency) {
        resultsHTML += `<li>Memory-constrained to ${memoryConstrainedConcurrency} workers. Adding RAM could improve throughput.</li>`;
    }
    
    if (optimal.networkUtilization > 0.6) {
        resultsHTML += '<li>High network utilization. Consider compression or larger batches.</li>';
    }
    
    // Alternative configurations
    resultsHTML += `
            </ul>
        </div>
        
        <div class="alternatives">
            <h4>Alternative Configurations</h4>
            <table class="responsive-table">
  <thead>
    <tr>
                    <th>Batch Size</th>
                    <th>Concurrency</th>
                    <th>Throughput</th>
                    <th>Latency</th>
                    <th>Efficiency</th>
                </tr>
  </thead>
  <tbody>
    <tr ${i === 0 ? 'class="optimal"' : ''}>
                <td data-label="Batch Size">${config.batchSize}</td>
                <td data-label="Concurrency">${config.concurrency}</td>
                <td data-label="Throughput">${config.throughput.toFixed(0)} tps</td>
                <td data-label="Latency">${config.latency.toFixed(1)} ms</td>
                <td data-label="Efficiency">${(config.efficiency * 100).toFixed(1)}%</td>
            </tr>
  </tbody>
</table>
        </div>
    `;
    
    document.getElementById('results').innerHTML = resultsHTML;
    
    // Draw performance chart
    drawPerformanceChart(optimalConfigs, optimal);
}

function drawPerformanceChart(configs, optimal) {
    const canvas = document.getElementById('perfChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Group by concurrency
    const concurrencyMap = {};
    configs.forEach(config => {
        if (!concurrencyMap[config.concurrency]) {
            concurrencyMap[config.concurrency] = [];
        }
        concurrencyMap[config.concurrency].push(config);
    });
    
    // Get best throughput for each concurrency level
    const dataPoints = Object.keys(concurrencyMap).map(c => {
        const best = concurrencyMap[c].reduce((a, b) => a.throughput > b.throughput ? a : b);
        return { concurrency: parseInt(c), throughput: best.throughput };
    }).sort((a, b) => a.concurrency - b.concurrency);
    
    if (dataPoints.length === 0) return;
    
    // Find scales
    const maxConcurrency = Math.max(...dataPoints.map(d => d.concurrency));
    const maxThroughput = Math.max(...dataPoints.map(d => d.throughput));
    
    // Draw axes
    ctx.strokeStyle = '#666';
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw throughput curve
    ctx.strokeStyle = '#5448C8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    dataPoints.forEach((point, i) => {
        const x = padding + (point.concurrency / maxConcurrency) * (width - 2 * padding);
        const y = height - padding - (point.throughput / maxThroughput) * (height - 2 * padding);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    // Mark optimal point
    const optimalX = padding + (optimal.concurrency / maxConcurrency) * (width - 2 * padding);
    const optimalY = height - padding - (optimal.throughput / maxThroughput) * (height - 2 * padding);
    
    ctx.fillStyle = '#ff6b6b';
    ctx.beginPath();
    ctx.arc(optimalX, optimalY, 5, 0, 2 * Math.PI);
    ctx.fill();
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = '12px sans-serif';
    ctx.fillText('Concurrency', width / 2 - 30, height - 10);
    
    ctx.save();
    ctx.translate(10, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Throughput (tasks/sec)', 0, 0);
    ctx.restore();
    
    // Optimal label
    ctx.fillStyle = '#ff6b6b';
    ctx.fillText('Optimal', optimalX - 20, optimalY - 10);
}
</script>

<style>
.calculator-container {
    max-width: 900px;
    margin: 0 auto;
}

.calc-header {
    text-align: center;
    margin-bottom: 2rem;
}

.calculator-tool {
    background: var(--md-code-bg-color);
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.input-group {
    margin-bottom: 1.5rem;
}

.input-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.input-group input, .input-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--md-default-fg-color--lighter);
    border-radius: 4px;
    font-size: 1rem;
}

.input-group .help {
    display: block;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
    margin-top: 0.25rem;
}

.calc-button {
    width: 100%;
    padding: 1rem;
    background: var(--md-primary-fg-color);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
}

.calc-button:hover {
    background: var(--md-primary-fg-color--dark);
}

.results-panel {
    margin-top: 2rem;
}

.optimal-config {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.config-item {
    text-align: center;
    padding: 1rem;
    background: var(--md-primary-fg-color--light);
    border-radius: 4px;
}

.config-item .label {
    display: block;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

.config-item .value {
    display: block;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--md-primary-fg-color);
    margin-top: 0.5rem;
}

.performance-chart, .constraints-analysis, .recommendations, .alternatives {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

# perfChart {
    max-width: 100%;
    height: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--md-default-fg-color--lighter);
}

th {
    font-weight: 600;
    background: var(--md-default-bg-color);
}

tr.optimal {
    background: var(--md-primary-fg-color--light);
}

.recommendations ul {
    list-style: none;
    padding: 0;
}

.recommendations li {
    padding: 0.75rem 0;
    padding-left: 2rem;
    position: relative;
}

.recommendations li:before {
    content: "→";
    position: absolute;
    left: 0.5rem;
}

.recommendations li.warning {
    color: var(--md-warning-fg-color);
    font-weight: 600;
}

.strategy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.strategy-card {
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.strategy-card h4 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.strategy-card p {
    margin-top: 1rem;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

.bottleneck-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.bottleneck-item {
    padding: 1rem;
    background: var(--md-warning-bg-color);
    border-radius: 8px;
    border-left: 4px solid var(--md-warning-fg-color);
}

.bottleneck-item .icon {
    font-size: 1.5rem;
    margin-right: 0.5rem;
}

.bottleneck-item strong {
    display: inline-block;
    margin-bottom: 0.5rem;
}

.bottleneck-item p {
    margin: 0;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 1rem;
    }
    
    .strategy-grid, .bottleneck-list {
        grid-template-columns: 1fr;
    }
}
</style>
</div>