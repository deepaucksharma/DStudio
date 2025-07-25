# Capacity Planning Calculator

<div class="calculator-container">
<div class="calc-header">
<h2>📈 Capacity Planning Calculator</h2>
<p>Plan resource allocation and predict scaling needs based on workload patterns and growth projections.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="capacityCalc">

### Current System Metrics
<div class="input-group">
<label for="currentRPS">Current request rate (req/sec):</label>
<input type="number" id="currentRPS" value="1000" min="0" step="100">
</div>

<div class="input-group">
<label for="avgResponseTime">Average response time (ms):</label>
<input type="number" id="avgResponseTime" value="50" min="1" step="10">
</div>

<div class="input-group">
<label for="currentServers">Current number of servers:</label>
<input type="number" id="currentServers" value="10" min="1" step="1">
</div>

<div class="input-group">
<label for="cpuUtilization">Current CPU utilization (%):</label>
<input type="number" id="cpuUtilization" value="60" min="0" max="100" step="5">
</div>

<div class="input-group">
<label for="memoryUsageGB">Memory usage per server (GB):</label>
<input type="number" id="memoryUsageGB" value="8" min="0" step="1">
</div>

### Growth Projections
<div class="input-group">
<label for="growthRate">Monthly growth rate (%):</label>
<input type="number" id="growthRate" value="10" min="0" step="1">
</div>

<div class="input-group">
<label for="planningHorizon">Planning horizon (months):</label>
<input type="number" id="planningHorizon" value="12" min="1" max="36" step="1">
</div>

<div class="input-group">
<label for="peakMultiplier">Peak traffic multiplier:</label>
<input type="number" id="peakMultiplier" value="2.5" min="1" step="0.1">
<span class="help">Peak traffic as multiple of average</span>
</div>

### Resource Constraints
<div class="input-group">
<label for="maxCPU">Target max CPU utilization (%):</label>
<input type="number" id="maxCPU" value="70" min="10" max="90" step="5">
<span class="help">Leave headroom for spikes</span>
</div>

<div class="input-group">
<label for="serverCost">Cost per server per month ($):</label>
<input type="number" id="serverCost" value="500" min="0" step="50">
</div>

<div class="input-group">
<label for="slaTarget">SLA availability target (%):</label>
<input type="number" id="slaTarget" value="99.9" min="90" max="99.999" step="0.1">
</div>

<button type="button" onclick="calculateCapacity()" class="calc-button">Calculate Capacity Plan</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## Capacity Planning Principles

### 1. Little's Law Application
```
L = λ × W

Where:
- L = Number of requests in system
- λ = Arrival rate (req/sec)
- W = Average time in system
```

### 2. Utilization Law
```
U = (Service Time × Arrival Rate) / Number of Servers
```

### 3. Response Time Modeling
```
Response Time = Service Time / (1 - Utilization)
```
*Note: This assumes M/M/1 queue; actual systems are more complex*

### 4. Scaling Laws
- **Linear Scaling**: Ideal case, rarely achieved
- **Amdahl's Law**: Limited by serial portions
- **Universal Scalability Law**: Accounts for coherency delays

## Capacity Planning Strategies

<div class="strategy-grid">
<div class="strategy-card">
<h4>📊 Vertical Scaling</h4>
<ul>
<li>Upgrade CPU/Memory</li>
<li>Faster storage (NVMe)</li>
<li>Network optimization</li>
<li>Database tuning</li>
</ul>
<p><strong>Best for:</strong> Stateful services, databases</p>
</div>

<div class="strategy-card">
<h4>🔄 Horizontal Scaling</h4>
<ul>
<li>Add more servers</li>
<li>Load balancing</li>
<li>Sharding/Partitioning</li>
<li>Service replication</li>
</ul>
<p><strong>Best for:</strong> Stateless services, web tiers</p>
</div>

<div class="strategy-card">
<h4>⚡ Performance Optimization</h4>
<ul>
<li>Caching layers</li>
<li>Query optimization</li>
<li>Async processing</li>
<li>Connection pooling</li>
</ul>
<p><strong>Best for:</strong> Cost-effective gains</p>
</div>

<div class="strategy-card">
<h4>🌐 Geographic Distribution</h4>
<ul>
<li>Multi-region deployment</li>
<li>CDN for static content</li>
<li>Edge computing</li>
<li>Regional databases</li>
</ul>
<p><strong>Best for:</strong> Global services</p>
</div>
</div>

## Warning Signs

Watch for these indicators that capacity planning is needed:

<div class="warning-grid">
<div class="warning-item">
<span class="warning-icon">⚠️</span>
<strong>Response Time Degradation</strong>
<p>P95 latency increasing week-over-week</p>
</div>

<div class="warning-item">
<span class="warning-icon">⚠️</span>
<strong>High Resource Utilization</strong>
<p>CPU or memory consistently >80%</p>
</div>

<div class="warning-item">
<span class="warning-icon">⚠️</span>
<strong>Queue Buildup</strong>
<p>Message queues growing unbounded</p>
</div>

<div class="warning-item">
<span class="warning-icon">⚠️</span>
<strong>Error Rate Increase</strong>
<p>Timeouts and failures rising</p>
</div>
</div>

## Related Resources

- [Little's Law](/quantitative/littles-law)
- [Universal Scalability Law](/quantitative/universal-scalability)
- [Capacity Planning Guide](/quantitative/capacity-planning)
- [Auto-Scaling Pattern](/patterns/auto-scaling)
- [Load Balancing Pattern](/patterns/load-balancing)

<script>
// Enhanced capacity calculator with input validation and real-time updates
let capacityChart = null;

function validateCapacityInputs() {
    const inputs = {
        currentRPS: { value: parseFloat(document.getElementById('currentRPS').value), min: 1, max: 1000000, name: 'Request rate' },
        avgResponseTime: { value: parseFloat(document.getElementById('avgResponseTime').value), min: 1, max: 10000, name: 'Response time' },
        currentServers: { value: parseInt(document.getElementById('currentServers').value), min: 1, max: 10000, name: 'Current servers' },
        cpuUtilization: { value: parseFloat(document.getElementById('cpuUtilization').value), min: 0, max: 100, name: 'CPU utilization' },
        memoryUsageGB: { value: parseFloat(document.getElementById('memoryUsageGB').value), min: 0.1, max: 1000, name: 'Memory usage' },
        growthRate: { value: parseFloat(document.getElementById('growthRate').value), min: 0, max: 100, name: 'Growth rate' },
        planningHorizon: { value: parseInt(document.getElementById('planningHorizon').value), min: 1, max: 36, name: 'Planning horizon' },
        peakMultiplier: { value: parseFloat(document.getElementById('peakMultiplier').value), min: 1, max: 10, name: 'Peak multiplier' },
        maxCPU: { value: parseFloat(document.getElementById('maxCPU').value), min: 10, max: 90, name: 'Max CPU target' },
        serverCost: { value: parseFloat(document.getElementById('serverCost').value), min: 0, max: 100000, name: 'Server cost' },
        slaTarget: { value: parseFloat(document.getElementById('slaTarget').value), min: 90, max: 99.999, name: 'SLA target' }
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

function calculateCapacity() {
    // Validate inputs
    const validation = validateCapacityInputs();
    if (!validation.valid) {
        displayCapacityErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    const growthRate = inputs.growthRate.value / 100;
    
    // Calculate current metrics
    const currentCapacityRPS = inputs.currentRPS.value / (inputs.cpuUtilization.value / 100);
    const rpsPerServer = currentCapacityRPS / inputs.currentServers.value;
    
    // Calculate memory constraints
    const totalMemoryGB = inputs.memoryUsageGB.value * inputs.currentServers.value;
    const memoryPerRPS = totalMemoryGB / inputs.currentRPS.value;
    
    // Project growth with advanced modeling
    let projections = [];
    let cumulativeCost = 0;
    
    for (let month = 0; month <= inputs.planningHorizon.value; month++) {
        const growthFactor = Math.pow(1 + growthRate, month);
        const projectedRPS = inputs.currentRPS.value * growthFactor;
        const peakRPS = projectedRPS * inputs.peakMultiplier.value;
        
        // Calculate required servers (considering both CPU and memory)
        const cpuBasedServers = Math.ceil((peakRPS / rpsPerServer) / (inputs.maxCPU.value / 100));
        const memoryBasedServers = Math.ceil((peakRPS * memoryPerRPS) / inputs.memoryUsageGB.value);
        const requiredServers = Math.max(cpuBasedServers, memoryBasedServers);
        
        // Calculate costs
        const monthlyCost = requiredServers * inputs.serverCost.value;
        cumulativeCost += monthlyCost;
        
        // Calculate actual utilization
        const cpuUtilization = (peakRPS / (requiredServers * rpsPerServer)) * 100;
        const memoryUtilization = (peakRPS * memoryPerRPS) / (requiredServers * inputs.memoryUsageGB.value) * 100;
        const actualUtilization = Math.max(cpuUtilization, memoryUtilization);
        const headroom = 100 - actualUtilization;
        
        projections.push({
            month: month,
            avgRPS: projectedRPS,
            peakRPS: peakRPS,
            servers: requiredServers,
            cost: monthlyCost,
            cumulativeCost: cumulativeCost,
            cpuUtilization: cpuUtilization,
            memoryUtilization: memoryUtilization,
            utilization: actualUtilization,
            headroom: headroom,
            constraintType: cpuBasedServers > memoryBasedServers ? 'CPU' : 'Memory'
        });
    }
    
    // Calculate availability based on redundancy
    const n = projections[inputs.planningHorizon.value].servers;
    const redundancy = Math.max(1, Math.floor(n * 0.1)); // 10% redundancy
    const availability = calculateAvailability(n, redundancy);
    
    // Prepare data for visualization
    const capacityData = {
        projections: projections,
        currentState: {
            rpsPerServer: rpsPerServer,
            currentCapacityRPS: currentCapacityRPS,
            cpuUtilization: inputs.cpuUtilization.value,
            servers: inputs.currentServers.value,
            headroom: 100 - inputs.cpuUtilization.value
        },
        recommendations: generateCapacityRecommendations(projections, inputs, availability),
        availability: availability,
        redundancy: redundancy
    };
    
    // Display results
    displayCapacityResults(capacityData, inputs);
    
    // Show results panel with animation
    const resultsPanel = document.getElementById('results');
    resultsPanel.style.display = 'block';
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function generateCapacityRecommendations(projections, inputs, availability) {
    const recommendations = [];
    
    // Growth rate analysis
    if (inputs.growthRate.value > 15) {
        recommendations.push({
            type: 'warning',
            message: 'High growth rate detected. Consider implementing auto-scaling to handle volatility.'
        });
    }
    
    // Short-term capacity needs
    const sixMonthProjection = projections[Math.min(6, projections.length - 1)];
    if (sixMonthProjection.servers > inputs.currentServers.value * 1.5) {
        recommendations.push({
            type: 'urgent',
            message: `⚠️ Significant scaling needed within 6 months (${sixMonthProjection.servers} servers). Start capacity planning immediately.`
        });
    }
    
    // Utilization analysis
    if (inputs.cpuUtilization.value > 70) {
        recommendations.push({
            type: 'important',
            message: 'Current utilization is high. Consider adding servers proactively to maintain stability.'
        });
    } else if (inputs.cpuUtilization.value < 30) {
        recommendations.push({
            type: 'info',
            message: 'Low utilization detected. You may be over-provisioned and could reduce costs.'
        });
    }
    
    // Availability vs SLA
    if (availability < inputs.slaTarget.value / 100) {
        const additionalServers = Math.ceil(projections[projections.length - 1].servers * 0.15);
        recommendations.push({
            type: 'error',
            message: `Current redundancy insufficient for ${inputs.slaTarget.value}% SLA. Add ${additionalServers} redundant servers.`
        });
    }
    
    // Cost optimization
    const totalCost = projections[projections.length - 1].cumulativeCost;
    const avgMonthlyCost = totalCost / projections.length;
    if (avgMonthlyCost > inputs.serverCost.value * inputs.currentServers.value * 2) {
        recommendations.push({
            type: 'important',
            message: 'Infrastructure costs will more than double. Consider architectural optimizations to reduce server requirements.'
        });
    }
    
    return recommendations;
}

function displayCapacityResults(data, inputs) {
    let resultsHTML = `
        <h3>📊 Capacity Planning Analysis</h3>
        
        <div class="capacity-summary">
            <div class="summary-cards-grid">
                <div class="summary-metric-card">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-content">
                        <div class="metric-value">${data.currentState.rpsPerServer.toFixed(0)}</div>
                        <div class="metric-label">RPS per Server</div>
                    </div>
                </div>
                <div class="summary-metric-card">
                    <div class="metric-icon">📈</div>
                    <div class="metric-content">
                        <div class="metric-value">${data.currentState.currentCapacityRPS.toFixed(0)}</div>
                        <div class="metric-label">Max Capacity (RPS)</div>
                    </div>
                </div>
                <div class="summary-metric-card ${data.currentState.headroom < 30 ? 'warning' : 'success'}">
                    <div class="metric-icon">💨</div>
                    <div class="metric-content">
                        <div class="metric-value">${data.currentState.headroom.toFixed(1)}%</div>
                        <div class="metric-label">Current Headroom</div>
                    </div>
                </div>
                <div class="summary-metric-card">
                    <div class="metric-icon">✅</div>
                    <div class="metric-content">
                        <div class="metric-value">${(data.availability * 100).toFixed(3)}%</div>
                        <div class="metric-label">Projected Availability</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="projection-summary">
            <h4>📅 ${inputs.planningHorizon.value}-Month Projection</h4>
            <div class="projection-cards">
                <div class="projection-card growth">
                    <div class="card-icon">📈</div>
                    <h5>Traffic Growth</h5>
                    <div class="big-number">${((Math.pow(1 + inputs.growthRate.value / 100, inputs.planningHorizon.value) - 1) * 100).toFixed(0)}%</div>
                    <div class="card-details">
                        <p>From ${inputs.currentRPS.value.toLocaleString()} to ${data.projections[data.projections.length - 1].avgRPS.toFixed(0).toLocaleString()} RPS</p>
                        <p class="peak-info">Peak: ${data.projections[data.projections.length - 1].peakRPS.toFixed(0).toLocaleString()} RPS</p>
                    </div>
                </div>
                <div class="projection-card servers">
                    <div class="card-icon">🖥️</div>
                    <h5>Infrastructure Scale</h5>
                    <div class="big-number">${data.projections[data.projections.length - 1].servers}</div>
                    <div class="card-details">
                        <p>Up from ${inputs.currentServers.value} servers</p>
                        <p class="increase">+${((data.projections[data.projections.length - 1].servers / inputs.currentServers.value - 1) * 100).toFixed(0)}% increase</p>
                    </div>
                </div>
                <div class="projection-card cost">
                    <div class="card-icon">💰</div>
                    <h5>Total Investment</h5>
                    <div class="big-number">$${(data.projections[data.projections.length - 1].cumulativeCost / 1000).toFixed(0)}k</div>
                    <div class="card-details">
                        <p>Monthly avg: $${(data.projections[data.projections.length - 1].cost).toLocaleString()}</p>
                        <p class="roi">Per server: $${inputs.serverCost.value}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h4>📊 Capacity Growth Timeline</h4>
                <canvas id="capacityChart" width="800" height="400"></canvas>
            </div>
            <div class="chart-container">
                <h4>💵 Cost Projection</h4>
                <canvas id="costChart" width="800" height="300"></canvas>
            </div>
        </div>
        
        <div class="recommendations-section">
            <h4>💡 Strategic Recommendations</h4>
            <div class="recommendations-grid">
    `;
    
    // Add intelligent recommendations
    data.recommendations.forEach(rec => {
        resultsHTML += `
            <div class="recommendation-card ${rec.type}">
                <div class="rec-icon">${rec.type === 'urgent' ? '🚨' : rec.type === 'error' ? '❌' : rec.type === 'warning' ? '⚠️' : rec.type === 'important' ? '📌' : 'ℹ️'}</div>
                <div class="rec-content">${rec.message}</div>
            </div>
        `;
    });
    
    resultsHTML += `
            </div>
        </div>
        
        <div class="scaling-roadmap">
            <h4>🗺️ Scaling Roadmap</h4>
            <div class="timeline">
                <div class="timeline-item immediate">
                    <div class="timeline-marker">Now</div>
                    <div class="timeline-content">
                        <h5>Quick Wins</h5>
                        <ul>
                            <li>Optimize queries & indexes</li>
                            <li>Enable compression</li>
                            <li>Tune connection pools</li>
                        </ul>
                        <div class="impact">10-20% improvement</div>
                    </div>
                </div>
                <div class="timeline-item short-term">
                    <div class="timeline-marker">1-3 mo</div>
                    <div class="timeline-content">
                        <h5>Tactical Improvements</h5>
                        <ul>
                            <li>Implement caching layer</li>
                            <li>Add read replicas</li>
                            <li>Enable auto-scaling</li>
                        </ul>
                        <div class="impact">30-50% capacity gain</div>
                    </div>
                </div>
                <div class="timeline-item medium-term">
                    <div class="timeline-marker">3-6 mo</div>
                    <div class="timeline-content">
                        <h5>Strategic Scaling</h5>
                        <ul>
                            <li>Horizontal partitioning</li>
                            <li>Microservices split</li>
                            <li>CDN deployment</li>
                        </ul>
                        <div class="impact">2-5x capacity</div>
                    </div>
                </div>
                <div class="timeline-item long-term">
                    <div class="timeline-marker">6-12 mo</div>
                    <div class="timeline-content">
                        <h5>Architecture Evolution</h5>
                        <ul>
                            <li>Event-driven design</li>
                            <li>Serverless migration</li>
                            <li>Global distribution</li>
                        </ul>
                        <div class="impact">10x+ scalability</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="detailed-projections">
            <h4>📋 Detailed Monthly Projections</h4>
            <div class="projection-table-container">
                <table class="projection-table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Avg RPS</th>
                            <th>Peak RPS</th>
                            <th>Servers</th>
                            <th>CPU %</th>
                            <th>Memory %</th>
                            <th>Monthly Cost</th>
                            <th>Constraint</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Show key milestone months
    const milestones = [0, 3, 6, 12, 18, 24, data.projections.length - 1];
    milestones.forEach(month => {
        if (month < data.projections.length) {
            const proj = data.projections[month];
            resultsHTML += `
                <tr class="${proj.utilization > 80 ? 'high-util' : ''}">
                    <td>${month}</td>
                    <td>${proj.avgRPS.toFixed(0).toLocaleString()}</td>
                    <td>${proj.peakRPS.toFixed(0).toLocaleString()}</td>
                    <td>${proj.servers}</td>
                    <td>${proj.cpuUtilization.toFixed(1)}%</td>
                    <td>${proj.memoryUtilization.toFixed(1)}%</td>
                    <td>$${proj.cost.toLocaleString()}</td>
                    <td><span class="constraint-badge ${proj.constraintType.toLowerCase()}">${proj.constraintType}</span></td>
                </tr>
            `;
        }
    });
    
    resultsHTML += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    document.getElementById('results').innerHTML = resultsHTML;
    
    // Draw interactive charts
    drawCapacityChart(data.projections);
    drawCostChart(data.projections);
}

function displayCapacityErrors(errors) {
    let errorHTML = '<div class="error-container"><h4>⚠️ Input Validation Errors</h4><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = errorHTML;
    resultsDiv.style.display = 'block';
}

function calculateAvailability(servers, redundancy) {
    // Simplified availability calculation
    const serverAvailability = 0.99; // 99% per server
    const requiredServers = servers - redundancy;
    
    // Probability that at least requiredServers are available
    let availability = 0;
    for (let k = requiredServers; k <= servers; k++) {
        availability += binomial(servers, k) * 
                       Math.pow(serverAvailability, k) * 
                       Math.pow(1 - serverAvailability, servers - k);
    }
    
    return availability;
}

function binomial(n, k) {
    return factorial(n) / (factorial(k) * factorial(n - k));
}

function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

function drawCapacityChart(projections) {
    const canvas = document.getElementById('capacityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 60;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Find max values for scaling
    const maxServers = Math.max(...projections.map(p => p.servers));
    const maxRPS = Math.max(...projections.map(p => p.peakRPS));
    const maxUtil = 100;
    
    // Draw grid lines
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {
        const y = padding + (i / 10) * (height - 2 * padding);
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Draw axes
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw server count line
    ctx.strokeStyle = '#5448C8';
    ctx.lineWidth = 3;
    ctx.beginPath();
    projections.forEach((p, i) => {
        const x = padding + (i / (projections.length - 1)) * (width - 2 * padding);
        const y = height - padding - (p.servers / maxServers) * (height - 2 * padding);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        
        // Draw data points
        ctx.fillStyle = '#5448C8';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
    });
    ctx.stroke();
    
    // Draw RPS line
    ctx.strokeStyle = '#00BCD4';
    ctx.lineWidth = 3;
    ctx.beginPath();
    projections.forEach((p, i) => {
        const x = padding + (i / (projections.length - 1)) * (width - 2 * padding);
        const y = height - padding - (p.peakRPS / maxRPS) * (height - 2 * padding);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    // Draw utilization line
    ctx.strokeStyle = '#FF9800';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    projections.forEach((p, i) => {
        const x = padding + (i / (projections.length - 1)) * (width - 2 * padding);
        const y = height - padding - (p.utilization / maxUtil) * (height - 2 * padding);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw labels
    ctx.fillStyle = '#333';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Months', width / 2, height - 20);
    
    // Y-axis labels
    ctx.textAlign = 'right';
    ctx.font = '12px sans-serif';
    for (let i = 0; i <= 5; i++) {
        const y = height - padding - (i / 5) * (height - 2 * padding);
        ctx.fillText(`${Math.round(maxServers * i / 5)}`, padding - 10, y + 4);
    }
    
    // Legend
    const legendX = width - 200;
    const legendY = padding;
    
    ctx.fillStyle = '#5448C8';
    ctx.fillRect(legendX, legendY, 20, 3);
    ctx.fillStyle = '#333';
    ctx.textAlign = 'left';
    ctx.fillText('Servers', legendX + 30, legendY + 5);
    
    ctx.fillStyle = '#00BCD4';
    ctx.fillRect(legendX, legendY + 20, 20, 3);
    ctx.fillStyle = '#333';
    ctx.fillText('Peak RPS', legendX + 30, legendY + 25);
    
    ctx.strokeStyle = '#FF9800';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(legendX, legendY + 42);
    ctx.lineTo(legendX + 20, legendY + 42);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#333';
    ctx.fillText('Utilization %', legendX + 30, legendY + 45);
    
    // Title
    ctx.font = 'bold 16px sans-serif';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';
    ctx.fillText('Infrastructure Growth Projection', width / 2, 30);
}

function drawCostChart(projections) {
    const canvas = document.getElementById('costChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 60;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    const maxCost = Math.max(...projections.map(p => p.cost));
    const maxCumulative = projections[projections.length - 1].cumulativeCost;
    
    // Draw axes
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw monthly cost bars
    const barWidth = (width - 2 * padding) / projections.length - 5;
    projections.forEach((p, i) => {
        const x = padding + i * ((width - 2 * padding) / projections.length) + 2.5;
        const barHeight = (p.cost / maxCost) * (height - 2 * padding);
        const y = height - padding - barHeight;
        
        // Draw bar
        const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
        gradient.addColorStop(0, '#4CAF50');
        gradient.addColorStop(1, '#2E7D32');
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Add cost label on significant months
        if (i % Math.ceil(projections.length / 6) === 0) {
            ctx.fillStyle = '#333';
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`$${(p.cost / 1000).toFixed(0)}k`, x + barWidth / 2, y - 5);
        }
    });
    
    // Draw cumulative cost line
    ctx.strokeStyle = '#F44336';
    ctx.lineWidth = 3;
    ctx.beginPath();
    projections.forEach((p, i) => {
        const x = padding + (i / (projections.length - 1)) * (width - 2 * padding);
        const y = height - padding - (p.cumulativeCost / maxCumulative) * (height - 2 * padding);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Months', width / 2, height - 20);
    
    // Title
    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Cost Projection Analysis', width / 2, 30);
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

.input-group input {
    width: 100%;
    padding: 0.5rem;
    border: 2px solid var(--md-default-fg-color--lighter);
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.input-group input:focus {
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
    display: none;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.capacity-summary {
    margin-bottom: 2rem;
}

.summary-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.summary-metric-card {
    display: flex;
    align-items: center;
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.summary-metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.summary-metric-card.warning {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
    border: 2px solid #ffc107;
}

.summary-metric-card.success {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border: 2px solid #4caf50;
}

.metric-icon {
    font-size: 2.5rem;
    margin-right: 1rem;
}

.metric-content {
    flex: 1;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
    line-height: 1;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
    margin-top: 0.25rem;
}

.projection-summary {
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 12px;
}

.projection-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.projection-card {
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.projection-card.growth {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}

.projection-card.servers {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
}

.projection-card.cost {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
}

.card-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.projection-card h5 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    color: var(--md-default-fg-color);
}

.big-number {
    font-size: 3rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
    margin: 0.5rem 0;
}

.card-details p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.card-details .peak-info {
    color: var(--md-default-fg-color--light);
    font-size: 0.8rem;
}

.card-details .increase {
    color: #f57c00;
    font-weight: 600;
}

.card-details .roi {
    color: var(--md-default-fg-color--light);
}

.charts-section {
    margin: 2rem 0;
}

.chart-container {
    margin-bottom: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.chart-container h4 {
    margin-top: 0;
    margin-bottom: 1rem;
    color: var(--md-primary-fg-color);
}

# capacityChart, #costChart {
    max-width: 100%;
    height: auto;
}

.recommendations-section {
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 12px;
}

.recommendations-grid {
    display: grid;
    gap: 1rem;
    margin-top: 1rem;
}

.recommendation-card {
    display: flex;
    align-items: center;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.recommendation-card:hover {
    transform: translateX(4px);
}

.recommendation-card.urgent {
    background: #ffebee;
    border-left: 4px solid #f44336;
}

.recommendation-card.error {
    background: #ffcdd2;
    border-left: 4px solid #d32f2f;
}

.recommendation-card.warning {
    background: #fff8e1;
    border-left: 4px solid #ffc107;
}

.recommendation-card.important {
    background: #e8eaf6;
    border-left: 4px solid #3f51b5;
}

.recommendation-card.info {
    background: #e3f2fd;
    border-left: 4px solid #2196f3;
}

.rec-icon {
    font-size: 1.5rem;
    margin-right: 1rem;
}

.rec-content {
    flex: 1;
    font-size: 0.95rem;
}

.scaling-roadmap {
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 12px;
}

.timeline {
    position: relative;
    padding-left: 40px;
}

.timeline:before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--md-primary-fg-color);
}

.timeline-item {
    position: relative;
    margin-bottom: 2rem;
    padding-left: 30px;
}

.timeline-marker {
    position: absolute;
    left: -25px;
    top: 0;
    background: var(--md-primary-fg-color);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.timeline-content {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.timeline-content h5 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.timeline-content ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.timeline-content .impact {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: var(--md-primary-fg-color--light);
    border-radius: 4px;
    font-weight: 600;
    text-align: center;
}

.detailed-projections {
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 12px;
}

.projection-table-container {
    overflow-x: auto;
    margin-top: 1rem;
}

.projection-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

.projection-table thead {
    background: var(--md-primary-fg-color);
    color: white;
}

.projection-table th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.projection-table td {
    padding: 1rem;
    border-bottom: 1px solid var(--md-default-fg-color--lighter);
}

.projection-table tr.high-util {
    background: #fff3cd;
}

.constraint-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.constraint-badge.cpu {
    background: #e3f2fd;
    color: #1976d2;
}

.constraint-badge.memory {
    background: #f3e5f5;
    color: #7b1fa2;
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

.error-container ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.error-container li {
    color: #c62828;
}

.strategy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.strategy-card {
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
    transition: transform 0.3s ease;
}

.strategy-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.strategy-card h4 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

.strategy-card ul {
    margin: 0.5rem 0;
}

.strategy-card p {
    margin-top: 1rem;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

.warning-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.warning-item {
    padding: 1rem;
    background: var(--md-warning-bg-color);
    border-radius: 8px;
    border-left: 4px solid var(--md-warning-fg-color);
    transition: transform 0.3s ease;
}

.warning-item:hover {
    transform: translateX(4px);
}

.warning-icon {
    font-size: 1.5rem;
    margin-right: 0.5rem;
}

.warning-item strong {
    display: block;
    margin: 0.5rem 0;
}

.warning-item p {
    margin: 0;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 1rem;
    }
    
    .summary-cards-grid,
    .projection-cards,
    .strategy-grid,
    .warning-grid {
        grid-template-columns: 1fr;
    }
    
    .big-number {
        font-size: 2rem;
    }
    
    .timeline {
        padding-left: 20px;
    }
    
    .timeline-item {
        padding-left: 20px;
    }
    
    .projection-table {
        font-size: 0.875rem;
    }
    
    .projection-table th,
    .projection-table td {
        padding: 0.5rem;
    }
}
</style>
</div>