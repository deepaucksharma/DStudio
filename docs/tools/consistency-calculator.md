# Consistency Calculator

<div class="calculator-container">
<div class="calc-header">
<h2>🔄 Consistency Trade-off Calculator</h2>
<p>Explore CAP theorem trade-offs, calculate consistency guarantees, and understand the costs of different consistency models.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="consistencyCalc">

### System Configuration
<div class="input-group">
<label for="replicationFactor">Replication factor:</label>
<input type="number" id="replicationFactor" value="3" min="1" max="10" step="1">
<span class="help">Number of data replicas</span>
</div>

<div class="input-group">
<label for="totalNodes">Total nodes in cluster:</label>
<input type="number" id="totalNodes" value="5" min="1" max="100" step="1">
<span class="help">Total number of nodes in the system</span>
</div>

<div class="input-group">
<label for="networkLatency">Network latency between nodes (ms):</label>
<input type="number" id="networkLatency" value="5" min="0.1" max="1000" step="0.1">
<span class="help">Average RTT between nodes</span>
</div>

### Consistency Model
<div class="input-group">
<label for="consistencyModel">Consistency model:</label>
<select id="consistencyModel">
<option value="strong">Strong Consistency</option>
<option value="bounded">Bounded Staleness</option>
<option value="session">Session Consistency</option>
<option value="consistent-prefix">Consistent Prefix</option>
<option value="eventual">Eventual Consistency</option>
</select>
</div>

<div class="input-group" id="quorumConfig">
<label for="writeQuorum">Write quorum (W):</label>
<input type="number" id="writeQuorum" value="2" min="1" max="10" step="1">
<span class="help">Nodes that must acknowledge writes</span>
</div>

<div class="input-group">
<label for="readQuorum">Read quorum (R):</label>
<input type="number" id="readQuorum" value="2" min="1" max="10" step="1">
<span class="help">Nodes that must respond to reads</span>
</div>

<div class="input-group" id="stalenessConfig" style="display: none;">
<label for="maxStaleness">Maximum staleness window (seconds):</label>
<input type="number" id="maxStaleness" value="5" min="1" max="3600" step="1">
<span class="help">For bounded staleness model</span>
</div>

### Workload Characteristics
<div class="input-group">
<label for="readWriteRatio">Read:Write ratio:</label>
<select id="readWriteRatio">
<option value="1:1">1:1 (Balanced)</option>
<option value="10:1">10:1 (Read-heavy)</option>
<option value="100:1">100:1 (Cache-friendly)</option>
<option value="1:10">1:10 (Write-heavy)</option>
</select>
</div>

<div class="input-group">
<label for="dataSize">Average data size (KB):</label>
<input type="number" id="dataSize" value="10" min="0.1" max="10000" step="0.1">
<span class="help">Size of typical read/write</span>
</div>

<div class="input-group">
<label for="throughput">Target throughput (ops/sec):</label>
<input type="number" id="throughput" value="1000" min="1" max="1000000" step="100">
</div>

### Failure Tolerance
<div class="input-group">
<label for="nodeFailureRate">Node failure rate (per year):</label>
<input type="number" id="nodeFailureRate" value="0.1" min="0" max="1" step="0.01">
<span class="help">Probability of node failure</span>
</div>

<div class="input-group">
<label for="networkPartitionRate">Network partition rate (per year):</label>
<input type="number" id="networkPartitionRate" value="0.05" min="0" max="1" step="0.01">
<span class="help">Probability of network splits</span>
</div>

<button type="button" onclick="calculateConsistency()" class="calc-button">Calculate Trade-offs</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## CAP Theorem Visualizer

<div class="cap-visualizer">
<svg id="capTriangle" width="400" height="350" viewBox="0 0 400 350">
<!-- CAP Triangle will be drawn here -->
</svg>
</div>

## Understanding Consistency Models

### Consistency Spectrum

<div class="consistency-spectrum">
<div class="spectrum-item strong">
<h4>Strong Consistency</h4>
<ul>
<li>All nodes see same data simultaneously</li>
<li>Linearizability guarantee</li>
<li>Highest latency, lowest availability</li>
</ul>
</div>

<div class="spectrum-item bounded">
<h4>Bounded Staleness</h4>
<ul>
<li>Consistent within time/version bounds</li>
<li>Predictable staleness window</li>
<li>Good for geo-distribution</li>
</ul>
</div>

<div class="spectrum-item session">
<h4>Session Consistency</h4>
<ul>
<li>Read your own writes</li>
<li>Monotonic reads within session</li>
<li>Default for many systems</li>
</ul>
</div>

<div class="spectrum-item prefix">
<h4>Consistent Prefix</h4>
<ul>
<li>Writes appear in order</li>
<li>No gaps in update sequence</li>
<li>Good for event streams</li>
</ul>
</div>

<div class="spectrum-item eventual">
<h4>Eventual Consistency</h4>
<ul>
<li>Convergence guaranteed eventually</li>
<li>Lowest latency, highest availability</li>
<li>Suitable for many use cases</li>
</ul>
</div>
</div>

## Quorum Mathematics

### Basic Quorum Rules

For N replicas with write quorum W and read quorum R:

**Strong Consistency Requirement:**
```
W + R > N
```

**Write Availability:**
```
Available if at least W nodes are up
P(available) = Σ(k=W to N) C(N,k) × p^k × (1-p)^(N-k)
```

**Read Availability:**
```
Available if at least R nodes are up
P(available) = Σ(k=R to N) C(N,k) × p^k × (1-p)^(N-k)
```

### Common Quorum Configurations

<table class="quorum-table">
<tr>
<th>Configuration</th>
<th>N</th>
<th>W</th>
<th>R</th>
<th>Consistency</th>
<th>Write Latency</th>
<th>Read Latency</th>
<th>Fault Tolerance</th>
</tr>
<tr>
<td>Read One, Write All</td>
<td>3</td>
<td>3</td>
<td>1</td>
<td>Strong</td>
<td>High</td>
<td>Low</td>
<td>0 for writes</td>
</tr>
<tr>
<td>Majority Quorum</td>
<td>3</td>
<td>2</td>
<td>2</td>
<td>Strong</td>
<td>Medium</td>
<td>Medium</td>
<td>1 node</td>
</tr>
<tr>
<td>Write One, Read All</td>
<td>3</td>
<td>1</td>
<td>3</td>
<td>Strong</td>
<td>Low</td>
<td>High</td>
<td>0 for reads</td>
</tr>
<tr>
<td>Eventual (W=1, R=1)</td>
<td>3</td>
<td>1</td>
<td>1</td>
<td>Eventual</td>
<td>Low</td>
<td>Low</td>
<td>2 nodes</td>
</tr>
</table>

## Decision Framework

<div class="decision-tree">
<h3>When to Use Each Consistency Model</h3>

<div class="decision-box">
<h4>Choose Strong Consistency When:</h4>
<ul>
<li>Financial transactions or inventory management</li>
<li>Sequential ID generation</li>
<li>Configuration management</li>
<li>Any scenario where stale reads cause business impact</li>
</ul>
<p class="trade-off">⚠️ Trade-off: Higher latency, reduced availability during partitions</p>
</div>

<div class="decision-box">
<h4>Choose Eventual Consistency When:</h4>
<ul>
<li>Social media feeds and timelines</li>
<li>Product catalogs and descriptions</li>
<li>Analytics and metrics collection</li>
<li>Caching layers</li>
</ul>
<p class="trade-off">✅ Benefit: Maximum availability and performance</p>
</div>

<div class="decision-box">
<h4>Choose Session Consistency When:</h4>
<ul>
<li>Shopping carts and user sessions</li>
<li>User profile updates</li>
<li>Collaborative editing (with conflict resolution)</li>
<li>Most user-facing applications</li>
</ul>
<p class="trade-off">⚖️ Balance: Good UX with reasonable performance</p>
</div>
</div>

## Real-World Examples

<div class="example-grid">
<div class="example-card">
<h4>🛒 E-commerce Cart</h4>
<ul>
<li><strong>Model:</strong> Session consistency</li>
<li><strong>Config:</strong> N=3, W=2, R=1</li>
<li><strong>Latency:</strong> ~10ms writes, ~5ms reads</li>
<li><strong>Rationale:</strong> Users see their updates immediately</li>
</ul>
</div>

<div class="example-card">
<h4>💰 Payment Processing</h4>
<ul>
<li><strong>Model:</strong> Strong consistency</li>
<li><strong>Config:</strong> N=5, W=3, R=3</li>
<li><strong>Latency:</strong> ~50ms for all operations</li>
<li><strong>Rationale:</strong> Cannot tolerate inconsistency</li>
</ul>
</div>

<div class="example-card">
<h4>📊 Analytics Pipeline</h4>
<ul>
<li><strong>Model:</strong> Eventual consistency</li>
<li><strong>Config:</strong> N=3, W=1, R=1</li>
<li><strong>Latency:</strong> ~5ms for all operations</li>
<li><strong>Rationale:</strong> Speed over precision</li>
</ul>
</div>

<div class="example-card">
<h4>📱 Social Feed</h4>
<ul>
<li><strong>Model:</strong> Bounded staleness (5 min)</li>
<li><strong>Config:</strong> Async replication</li>
<li><strong>Latency:</strong> ~10ms local reads</li>
<li><strong>Rationale:</strong> Fresh enough for users</li>
</ul>
</div>
</div>

## Related Resources

- [CAP Theorem Deep Dive](/part1-axioms/distributed-knowledge/)
- [State Distribution Patterns](/part2-pillars/state/)
- [Truth Distribution](/part2-pillars/truth/)
- [PACELC Framework](/patterns/pacelc/)

<script>
// Initialize CAP triangle on page load
document.addEventListener('DOMContentLoaded', function() {
    drawCAPTriangle();
    setupModelListeners();
});

function setupModelListeners() {
    const modelSelect = document.getElementById('consistencyModel');
    const stalenessConfig = document.getElementById('stalenessConfig');
    const quorumConfig = document.getElementById('quorumConfig');
    
    modelSelect.addEventListener('change', function() {
        if (this.value === 'bounded') {
            stalenessConfig.style.display = 'block';
        } else {
            stalenessConfig.style.display = 'none';
        }
        
        // Auto-adjust quorum settings based on model
        const repFactor = parseInt(document.getElementById('replicationFactor').value);
        switch(this.value) {
            case 'strong':
                document.getElementById('writeQuorum').value = Math.ceil(repFactor / 2) + 1;
                document.getElementById('readQuorum').value = Math.ceil(repFactor / 2) + 1;
                break;
            case 'eventual':
                document.getElementById('writeQuorum').value = 1;
                document.getElementById('readQuorum').value = 1;
                break;
            case 'session':
                document.getElementById('writeQuorum').value = Math.ceil(repFactor / 2);
                document.getElementById('readQuorum').value = 1;
                break;
        }
    });
}

function drawCAPTriangle() {
    const svg = document.getElementById('capTriangle');
    const width = 400;
    const height = 350;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 150;
    
    // Clear existing content
    svg.innerHTML = '';
    
    // Calculate triangle vertices
    const vertices = [
        { x: centerX, y: centerY - radius, label: 'Consistency', color: '#5448C8' },
        { x: centerX - radius * Math.cos(Math.PI / 6), y: centerY + radius * Math.sin(Math.PI / 6), label: 'Availability', color: '#00BCD4' },
        { x: centerX + radius * Math.cos(Math.PI / 6), y: centerY + radius * Math.sin(Math.PI / 6), label: 'Partition\nTolerance', color: '#FF9800' }
    ];
    
    // Draw triangle
    const triangle = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    triangle.setAttribute('d', `M ${vertices[0].x} ${vertices[0].y} L ${vertices[1].x} ${vertices[1].y} L ${vertices[2].x} ${vertices[2].y} Z`);
    triangle.setAttribute('fill', 'none');
    triangle.setAttribute('stroke', '#333');
    triangle.setAttribute('stroke-width', '2');
    svg.appendChild(triangle);
    
    // Draw vertices and labels
    vertices.forEach((vertex, index) => {
        // Vertex circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', vertex.x);
        circle.setAttribute('cy', vertex.y);
        circle.setAttribute('r', '8');
        circle.setAttribute('fill', vertex.color);
        svg.appendChild(circle);
        
        // Label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', vertex.x);
        text.setAttribute('y', vertex.y + (index === 0 ? -20 : 30));
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '14');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', vertex.color);
        
        // Handle multi-line text
        const lines = vertex.label.split('\n');
        lines.forEach((line, i) => {
            const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
            tspan.textContent = line;
            tspan.setAttribute('x', vertex.x);
            tspan.setAttribute('dy', i === 0 ? 0 : '1.2em');
            text.appendChild(tspan);
        });
        
        svg.appendChild(text);
    });
    
    // Draw center point
    const center = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    center.setAttribute('cx', centerX);
    center.setAttribute('cy', centerY);
    center.setAttribute('r', '5');
    center.setAttribute('fill', '#666');
    svg.appendChild(center);
    
    // Add "Pick 2" text
    const pickText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    pickText.setAttribute('x', centerX);
    pickText.setAttribute('y', centerY + 5);
    pickText.setAttribute('text-anchor', 'middle');
    pickText.setAttribute('font-size', '12');
    pickText.setAttribute('fill', '#666');
    pickText.textContent = 'Pick 2';
    svg.appendChild(pickText);
}

function validateConsistencyInputs() {
    const inputs = {
        replicationFactor: parseInt(document.getElementById('replicationFactor').value),
        totalNodes: parseInt(document.getElementById('totalNodes').value),
        networkLatency: parseFloat(document.getElementById('networkLatency').value),
        writeQuorum: parseInt(document.getElementById('writeQuorum').value),
        readQuorum: parseInt(document.getElementById('readQuorum').value),
        dataSize: parseFloat(document.getElementById('dataSize').value),
        throughput: parseInt(document.getElementById('throughput').value),
        nodeFailureRate: parseFloat(document.getElementById('nodeFailureRate').value),
        networkPartitionRate: parseFloat(document.getElementById('networkPartitionRate').value)
    };
    
    const errors = [];
    
    if (inputs.replicationFactor > inputs.totalNodes) {
        errors.push('Replication factor cannot exceed total nodes');
    }
    
    if (inputs.writeQuorum > inputs.replicationFactor) {
        errors.push('Write quorum cannot exceed replication factor');
    }
    
    if (inputs.readQuorum > inputs.replicationFactor) {
        errors.push('Read quorum cannot exceed replication factor');
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function calculateConsistency() {
    const validation = validateConsistencyInputs();
    if (!validation.valid) {
        displayErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    const model = document.getElementById('consistencyModel').value;
    const readWriteRatio = document.getElementById('readWriteRatio').value;
    
    // Calculate consistency guarantees
    const isStronglyConsistent = inputs.writeQuorum + inputs.readQuorum > inputs.replicationFactor;
    
    // Calculate latencies
    const writeLatency = calculateQuorumLatency(inputs.writeQuorum, inputs.networkLatency, inputs.dataSize);
    const readLatency = calculateQuorumLatency(inputs.readQuorum, inputs.networkLatency, inputs.dataSize);
    
    // Calculate availability
    const writeAvailability = calculateQuorumAvailability(inputs.writeQuorum, inputs.replicationFactor, inputs.nodeFailureRate);
    const readAvailability = calculateQuorumAvailability(inputs.readQuorum, inputs.replicationFactor, inputs.nodeFailureRate);
    
    // Calculate costs
    const costs = calculateConsistencyCosts(inputs, readWriteRatio);
    
    // Calculate staleness for eventual consistency
    const staleness = calculateStaleness(model, inputs);
    
    // Display results
    displayConsistencyResults({
        model,
        isStronglyConsistent,
        writeLatency,
        readLatency,
        writeAvailability,
        readAvailability,
        costs,
        staleness,
        inputs
    });
    
    // Update CAP visualization
    updateCAPVisualization(model, inputs);
    
    // Show results
    const resultsPanel = document.getElementById('results');
    resultsPanel.style.display = 'block';
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function calculateQuorumLatency(quorum, networkLatency, dataSize) {
    // Base network latency for quorum nodes
    const baseLatency = networkLatency * Math.log2(quorum);
    
    // Add serialization overhead
    const serializationOverhead = dataSize * 0.01; // 0.01ms per KB
    
    // Add coordination overhead
    const coordinationOverhead = quorum * 0.5; // 0.5ms per node
    
    return baseLatency + serializationOverhead + coordinationOverhead;
}

function calculateQuorumAvailability(quorum, replicationFactor, nodeFailureRate) {
    // Calculate using binomial distribution
    let availability = 0;
    const nodeAvailability = 1 - nodeFailureRate;
    
    for (let k = quorum; k <= replicationFactor; k++) {
        availability += binomialCoefficient(replicationFactor, k) * 
                       Math.pow(nodeAvailability, k) * 
                       Math.pow(nodeFailureRate, replicationFactor - k);
    }
    
    return availability;
}

function calculateConsistencyCosts(inputs, readWriteRatio) {
    const ratios = {
        '1:1': { read: 0.5, write: 0.5 },
        '10:1': { read: 0.91, write: 0.09 },
        '100:1': { read: 0.99, write: 0.01 },
        '1:10': { read: 0.09, write: 0.91 }
    };
    
    const ratio = ratios[readWriteRatio];
    
    // Storage cost (all replicas)
    const storageCost = inputs.replicationFactor * inputs.dataSize * 0.001; // Cost per KB
    
    // Network cost (quorum operations)
    const networkCost = (inputs.writeQuorum * ratio.write + inputs.readQuorum * ratio.read) * 
                       inputs.dataSize * 0.0001;
    
    // Compute cost (coordination)
    const computeCost = (inputs.writeQuorum + inputs.readQuorum) * 0.01;
    
    return {
        storage: storageCost,
        network: networkCost,
        compute: computeCost,
        total: storageCost + networkCost + computeCost
    };
}

function calculateStaleness(model, inputs) {
    switch(model) {
        case 'strong':
            return { min: 0, max: 0, typical: 0 };
        case 'bounded':
            const maxStaleness = parseInt(document.getElementById('maxStaleness').value);
            return { min: 0, max: maxStaleness * 1000, typical: maxStaleness * 500 };
        case 'session':
            return { min: 0, max: inputs.networkLatency * 10, typical: inputs.networkLatency * 2 };
        case 'eventual':
            return { 
                min: inputs.networkLatency, 
                max: inputs.networkLatency * 100, 
                typical: inputs.networkLatency * 10 
            };
        default:
            return { min: 0, max: inputs.networkLatency * 50, typical: inputs.networkLatency * 5 };
    }
}

function displayConsistencyResults(results) {
    let html = `
        <h3>🎯 Consistency Analysis Results</h3>
        
        <div class="results-summary">
            <div class="summary-card ${results.isStronglyConsistent ? 'strong-consistency' : 'weak-consistency'}">
                <h4>Consistency Guarantee</h4>
                <div class="big-value">${results.isStronglyConsistent ? 'Strong' : results.model.charAt(0).toUpperCase() + results.model.slice(1)}</div>
                <p>${results.isStronglyConsistent ? 'W + R > N satisfied' : 'Weaker consistency model'}</p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h4>⏱️ Write Latency</h4>
                <div class="metric-value">${results.writeLatency.toFixed(1)} ms</div>
                <div class="metric-bar">
                    <div class="bar-fill" style="width: ${Math.min(results.writeLatency / 100 * 100, 100)}%; background: #FF9800;"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h4>📖 Read Latency</h4>
                <div class="metric-value">${results.readLatency.toFixed(1)} ms</div>
                <div class="metric-bar">
                    <div class="bar-fill" style="width: ${Math.min(results.readLatency / 100 * 100, 100)}%; background: #00BCD4;"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h4>✅ Write Availability</h4>
                <div class="metric-value">${(results.writeAvailability * 100).toFixed(3)}%</div>
                <div class="metric-bar">
                    <div class="bar-fill" style="width: ${results.writeAvailability * 100}%; background: #4CAF50;"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h4>📊 Read Availability</h4>
                <div class="metric-value">${(results.readAvailability * 100).toFixed(3)}%</div>
                <div class="metric-bar">
                    <div class="bar-fill" style="width: ${results.readAvailability * 100}%; background: #4CAF50;"></div>
                </div>
            </div>
        </div>
        
        <div class="staleness-analysis">
            <h4>⏰ Data Staleness Window</h4>
            <div class="staleness-ranges">
                <div class="range-item">
                    <span class="label">Minimum:</span>
                    <span class="value">${results.staleness.min} ms</span>
                </div>
                <div class="range-item">
                    <span class="label">Typical:</span>
                    <span class="value">${results.staleness.typical} ms</span>
                </div>
                <div class="range-item">
                    <span class="label">Maximum:</span>
                    <span class="value">${results.staleness.max} ms</span>
                </div>
            </div>
        </div>
        
        <div class="cost-breakdown">
            <h4>💰 Operational Costs (Relative)</h4>
            <canvas id="costChart" width="400" height="200"></canvas>
            <div class="cost-details">
                <p>Storage: ${results.costs.storage.toFixed(2)} units</p>
                <p>Network: ${results.costs.network.toFixed(2)} units</p>
                <p>Compute: ${results.costs.compute.toFixed(2)} units</p>
                <p><strong>Total: ${results.costs.total.toFixed(2)} units</strong></p>
            </div>
        </div>
        
        <div class="recommendations">
            <h4>💡 Recommendations</h4>
            ${generateRecommendations(results)}
        </div>
        
        <div class="cap-analysis">
            <h4>🔺 CAP Trade-offs</h4>
            ${generateCAPAnalysis(results)}
        </div>
    `;
    
    document.getElementById('results').innerHTML = html;
    
    // Draw cost chart
    drawCostChart(results.costs);
}

function generateRecommendations(results) {
    const recommendations = [];
    
    // Consistency recommendations
    if (!results.isStronglyConsistent && results.model === 'strong') {
        recommendations.push({
            type: 'error',
            text: 'Configuration does not guarantee strong consistency! Increase quorum sizes.'
        });
    }
    
    // Latency recommendations
    if (results.writeLatency > 50) {
        recommendations.push({
            type: 'warning',
            text: 'High write latency detected. Consider reducing write quorum or using eventual consistency for non-critical data.'
        });
    }
    
    if (results.readLatency > 30) {
        recommendations.push({
            type: 'warning',
            text: 'High read latency. Consider caching, read replicas, or reducing read quorum.'
        });
    }
    
    // Availability recommendations
    if (results.writeAvailability < 0.999) {
        recommendations.push({
            type: 'warning',
            text: `Write availability is ${(results.writeAvailability * 100).toFixed(2)}%. Consider reducing write quorum or adding more replicas.`
        });
    }
    
    // Model-specific recommendations
    switch(results.model) {
        case 'eventual':
            recommendations.push({
                type: 'info',
                text: 'Using eventual consistency. Ensure your application can handle stale reads and implement conflict resolution.'
            });
            break;
        case 'strong':
            if (results.inputs.totalNodes < 5) {
                recommendations.push({
                    type: 'info',
                    text: 'For better fault tolerance with strong consistency, consider deploying to at least 5 nodes.'
                });
            }
            break;
    }
    
    // Cost optimization
    if (results.inputs.replicationFactor > 3 && results.model === 'eventual') {
        recommendations.push({
            type: 'info',
            text: 'High replication factor with eventual consistency. You might reduce replicas without impacting consistency.'
        });
    }
    
    let html = '<ul>';
    recommendations.forEach(rec => {
        html += `<li class="recommendation-${rec.type}">${rec.text}</li>`;
    });
    html += '</ul>';
    
    return html;
}

function generateCAPAnalysis(results) {
    let analysis = '<div class="cap-breakdown">';
    
    if (results.isStronglyConsistent) {
        analysis += `
            <div class="cap-choice">
                <h5>Your Configuration: CP System</h5>
                <p>✅ <strong>Consistency:</strong> Strong guarantees with quorum consensus</p>
                <p>⚠️ <strong>Availability:</strong> System unavailable if less than ${results.inputs.writeQuorum} nodes for writes</p>
                <p>✅ <strong>Partition Tolerance:</strong> Handles network splits with degraded availability</p>
            </div>
        `;
    } else if (results.model === 'eventual') {
        analysis += `
            <div class="cap-choice">
                <h5>Your Configuration: AP System</h5>
                <p>⚠️ <strong>Consistency:</strong> Eventually consistent, temporary divergence possible</p>
                <p>✅ <strong>Availability:</strong> High availability even during partitions</p>
                <p>✅ <strong>Partition Tolerance:</strong> Continues operating during network splits</p>
            </div>
        `;
    } else {
        analysis += `
            <div class="cap-choice">
                <h5>Your Configuration: Balanced Trade-offs</h5>
                <p>⚖️ <strong>Consistency:</strong> ${results.model} consistency model</p>
                <p>⚖️ <strong>Availability:</strong> Moderate availability based on quorum settings</p>
                <p>✅ <strong>Partition Tolerance:</strong> Handles partitions with defined behavior</p>
            </div>
        `;
    }
    
    analysis += '</div>';
    return analysis;
}

function drawCostChart(costs) {
    const canvas = document.getElementById('costChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Data
    const data = [
        { label: 'Storage', value: costs.storage, color: '#5448C8' },
        { label: 'Network', value: costs.network, color: '#00BCD4' },
        { label: 'Compute', value: costs.compute, color: '#FF9800' }
    ];
    
    // Calculate bar dimensions
    const barWidth = width / (data.length * 2);
    const maxValue = Math.max(...data.map(d => d.value));
    const scale = (height - 40) / maxValue;
    
    // Draw bars
    data.forEach((item, index) => {
        const x = (index * 2 + 0.5) * barWidth;
        const barHeight = item.value * scale;
        const y = height - 20 - barHeight;
        
        // Draw bar
        ctx.fillStyle = item.color;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Draw label
        ctx.fillStyle = '#333';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(item.label, x + barWidth / 2, height - 5);
        
        // Draw value
        ctx.fillText(item.value.toFixed(2), x + barWidth / 2, y - 5);
    });
}

function updateCAPVisualization(model, inputs) {
    const svg = document.getElementById('capTriangle');
    
    // Remove existing highlight
    const existingHighlight = svg.querySelector('.model-highlight');
    if (existingHighlight) {
        existingHighlight.remove();
    }
    
    // Add new highlight based on model
    const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    highlight.setAttribute('class', 'model-highlight');
    highlight.setAttribute('r', '12');
    highlight.setAttribute('fill', 'rgba(84, 72, 200, 0.3)');
    highlight.setAttribute('stroke', '#5448C8');
    highlight.setAttribute('stroke-width', '2');
    
    // Position based on consistency model
    const centerX = 200;
    const centerY = 175;
    let x, y;
    
    switch(model) {
        case 'strong':
            x = centerX;
            y = centerY - 100; // Near Consistency vertex
            break;
        case 'eventual':
            x = centerX - 50;
            y = centerY + 50; // Between Availability and Partition Tolerance
            break;
        default:
            x = centerX;
            y = centerY; // Center
    }
    
    highlight.setAttribute('cx', x);
    highlight.setAttribute('cy', y);
    svg.appendChild(highlight);
}

function binomialCoefficient(n, k) {
    if (k > n) return 0;
    if (k === 0 || k === n) return 1;
    
    let result = 1;
    for (let i = 0; i < k; i++) {
        result = result * (n - i) / (i + 1);
    }
    return result;
}

function displayErrors(errors) {
    let errorHTML = '<div class="error-container"><h4>⚠️ Validation Errors</h4><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    
    document.getElementById('results').innerHTML = errorHTML;
    document.getElementById('results').style.display = 'block';
}

// Real-time validation
document.addEventListener('DOMContentLoaded', function() {
    const replicationInput = document.getElementById('replicationFactor');
    const writeQuorumInput = document.getElementById('writeQuorum');
    const readQuorumInput = document.getElementById('readQuorum');
    
    function updateQuorumLimits() {
        const maxQuorum = parseInt(replicationInput.value);
        writeQuorumInput.max = maxQuorum;
        readQuorumInput.max = maxQuorum;
        
        if (parseInt(writeQuorumInput.value) > maxQuorum) {
            writeQuorumInput.value = maxQuorum;
        }
        if (parseInt(readQuorumInput.value) > maxQuorum) {
            readQuorumInput.value = maxQuorum;
        }
    }
    
    replicationInput.addEventListener('input', updateQuorumLimits);
});
</script>

<style>
.calculator-container {
    max-width: 1200px;
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
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    border: 2px solid var(--md-default-fg-color--lighter);
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.input-group input:focus, .input-group select:focus {
    outline: none;
    border-color: var(--md-primary-fg-color);
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
    transition: all 0.3s ease;
}

.calc-button:hover {
    background: var(--md-primary-fg-color--dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.results-panel {
    margin-top: 2rem;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    display: none;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.cap-visualizer {
    text-align: center;
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

#capTriangle {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.consistency-spectrum {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin: 2rem 0;
    position: relative;
}

.consistency-spectrum::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(to right, #5448C8, #00BCD4, #4CAF50, #FF9800, #F44336);
    z-index: 0;
}

.spectrum-item {
    flex: 1;
    padding: 1rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: relative;
    z-index: 1;
}

.spectrum-item h4 {
    margin-top: 0;
    font-size: 1rem;
}

.spectrum-item ul {
    font-size: 0.875rem;
    margin: 0;
    padding-left: 1.5rem;
}

.quorum-table {
    width: 100%;
    margin: 2rem 0;
    border-collapse: collapse;
}

.quorum-table th {
    background: var(--md-primary-fg-color);
    color: white;
    padding: 0.75rem;
    text-align: left;
}

.quorum-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--md-default-fg-color--lighter);
}

.quorum-table tr:hover {
    background: var(--md-code-bg-color);
}

.decision-tree {
    margin: 2rem 0;
}

.decision-box {
    margin: 1rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    border-left: 4px solid var(--md-primary-fg-color);
}

.decision-box h4 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.decision-box .trade-off {
    margin-top: 1rem;
    padding: 0.5rem;
    background: var(--md-default-bg-color);
    border-radius: 4px;
    font-style: italic;
}

.example-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.example-card {
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.example-card h4 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.results-summary {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
}

.summary-card {
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    min-width: 300px;
}

.summary-card.strong-consistency {
    background: linear-gradient(135deg, #e8eaf6, #c5cae9);
    border: 2px solid #5448C8;
}

.summary-card.weak-consistency {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border: 2px solid #FF9800;
}

.summary-card h4 {
    margin: 0 0 1rem 0;
}

.big-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
    margin: 0.5rem 0;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.metric-card {
    padding: 1.5rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-card h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-bar {
    height: 8px;
    background: var(--md-default-fg-color--lighter);
    border-radius: 4px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    transition: width 0.5s ease;
}

.staleness-analysis {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-default-bg-color);
    border-radius: 8px;
}

.staleness-ranges {
    display: flex;
    justify-content: space-around;
    margin-top: 1rem;
}

.range-item {
    text-align: center;
}

.range-item .label {
    display: block;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

.range-item .value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
    margin-top: 0.5rem;
}

.cost-breakdown {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-default-bg-color);
    border-radius: 8px;
}

.cost-details {
    margin-top: 1rem;
    font-size: 0.9rem;
}

.recommendations {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-default-bg-color);
    border-radius: 8px;
}

.recommendations ul {
    margin: 0;
    padding-left: 1.5rem;
}

.recommendations li {
    margin: 0.5rem 0;
    padding: 0.5rem;
    border-radius: 4px;
}

.recommendation-error {
    background: #ffebee;
    color: #c62828;
    font-weight: 600;
}

.recommendation-warning {
    background: #fff8e1;
    color: #f57c00;
}

.recommendation-info {
    background: #e3f2fd;
    color: #1565c0;
}

.cap-analysis {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-default-bg-color);
    border-radius: 8px;
}

.cap-choice {
    padding: 1rem;
    background: white;
    border-radius: 8px;
}

.cap-choice h5 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.error-container {
    padding: 1.5rem;
    background: #ffebee;
    border: 2px solid #f44336;
    border-radius: 8px;
    margin: 1rem 0;
}

.error-container h4 {
    margin-top: 0;
    color: #c62828;
}

.model-highlight {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 0.3; }
    50% { opacity: 0.8; }
    100% { opacity: 0.3; }
}

@media (max-width: 768px) {
    .consistency-spectrum {
        flex-direction: column;
    }
    
    .consistency-spectrum::before {
        display: none;
    }
    
    .example-grid, .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .staleness-ranges {
        flex-direction: column;
        gap: 1rem;
    }
}
</style>
</div>