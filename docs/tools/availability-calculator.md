# Availability Calculator

<div class="calculator-container">
<div class="calc-header">
<h2>✅ System Availability Calculator</h2>
<p>Calculate system availability, redundancy requirements, and the impact of failures on uptime.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="availabilityCalc">

### Component Reliability
<div class="input-group">
<label for="componentMTBF">Component MTBF (hours):</label>
<input type="number" id="componentMTBF" value="10000" min="1" step="100">
<span class="help">Mean Time Between Failures</span>
</div>

<div class="input-group">
<label for="componentMTTR">Component MTTR (hours):</label>
<input type="number" id="componentMTTR" value="2" min="0.1" step="0.1">
<span class="help">Mean Time To Repair</span>
</div>

<div class="input-group">
<label for="numComponents">Number of components in series:</label>
<input type="number" id="numComponents" value="5" min="1" step="1">
<span class="help">Components that all must work</span>
</div>

### Redundancy Configuration
<div class="input-group">
<label for="redundancyType">Redundancy type:</label>
<select id="redundancyType">
<option value="none">No redundancy</option>
<option value="active-standby">Active-Standby (1+1)</option>
<option value="n-plus-1">N+1 redundancy</option>
<option value="n-plus-2">N+2 redundancy</option>
<option value="active-active">Active-Active (2N)</option>
</select>
</div>

<div class="input-group">
<label for="failoverTime">Failover time (minutes):</label>
<input type="number" id="failoverTime" value="5" min="0" step="1">
<span class="help">Time to switch to backup</span>
</div>

### System Configuration
<div class="input-group">
<label for="numRegions">Number of regions:</label>
<input type="number" id="numRegions" value="1" min="1" max="10" step="1">
</div>

<div class="input-group">
<label for="regionFailureRate">Region failure rate (per year):</label>
<input type="number" id="regionFailureRate" value="0.01" min="0" max="1" step="0.001">
<span class="help">Major outages like natural disasters</span>
</div>

<div class="input-group">
<label for="targetSLA">Target SLA (%):</label>
<select id="targetSLA">
<option value="99">99% (3.65 days/year downtime)</option>
<option value="99.9">99.9% (8.77 hours/year)</option>
<option value="99.95">99.95% (4.38 hours/year)</option>
<option value="99.99">99.99% (52.6 minutes/year)</option>
<option value="99.999">99.999% (5.26 minutes/year)</option>
</select>
</div>

<button type="button" onclick="calculateAvailability()" class="calc-button">Calculate Availability</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## Understanding Availability

### Key Concepts

**Availability Formula:**
```
Availability = MTBF / (MTBF + MTTR)
```

**Serial Components (AND):**
```
A_total = A₁ × A₂ × ... × Aₙ
```

**Parallel Components (OR):**
```
A_total = 1 - (1-A₁) × (1-A₂) × ... × (1-Aₙ)
```

### Common Availability Targets

<div class="availability-table">
<table class="responsive-table">
  <thead>
    <tr>
<th>Availability</th>
<th>Downtime/Year</th>
<th>Downtime/Month</th>
<th>Typical Use Case</th>
</tr>
  </thead>
  <tbody>
    <tr>
<td data-label="Availability">90% (1 nine)</td>
<td data-label="Downtime/Year">36.5 days</td>
<td data-label="Downtime/Month">3 days</td>
<td data-label="Typical Use Case">Internal tools, batch jobs</td>
</tr>
    <tr>
<td data-label="Availability">99% (2 nines)</td>
<td data-label="Downtime/Year">3.65 days</td>
<td data-label="Downtime/Month">7.3 hours</td>
<td data-label="Typical Use Case">Non-critical services</td>
</tr>
    <tr>
<td data-label="Availability">99.9% (3 nines)</td>
<td data-label="Downtime/Year">8.77 hours</td>
<td data-label="Downtime/Month">43.8 min</td>
<td data-label="Typical Use Case">Business applications</td>
</tr>
    <tr>
<td data-label="Availability">99.99% (4 nines)</td>
<td data-label="Downtime/Year">52.6 minutes</td>
<td data-label="Downtime/Month">4.38 min</td>
<td data-label="Typical Use Case">E-commerce, SaaS</td>
</tr>
    <tr>
<td data-label="Availability">99.999% (5 nines)</td>
<td data-label="Downtime/Year">5.26 minutes</td>
<td data-label="Downtime/Month">26.3 sec</td>
<td data-label="Typical Use Case">Critical infrastructure</td>
</tr>
  </tbody>
</table>
</div>

## Strategies to Improve Availability

<div class="strategy-grid">
<div class="strategy-card">
<h4>🔧 Reduce MTTR</h4>
<ul>
<li>Automated recovery</li>
<li>Better monitoring</li>
<li>Runbook automation</li>
<li>Faster deployment</li>
</ul>
<p><strong>Impact:</strong> Linear improvement</p>
</div>

<div class="strategy-card">
<h4>📈 Increase MTBF</h4>
<ul>
<li>Better testing</li>
<li>Code reviews</li>
<li>Chaos engineering</li>
<li>Capacity planning</li>
</ul>
<p><strong>Impact:</strong> Reduces failure rate</p>
</div>

<div class="strategy-card">
<h4>🔄 Add Redundancy</h4>
<ul>
<li>Multiple instances</li>
<li>Cross-region failover</li>
<li>Data replication</li>
<li>Load balancing</li>
</ul>
<p><strong>Impact:</strong> Exponential improvement</p>
</div>

<div class="strategy-card">
<h4>🎯 Eliminate SPOFs</h4>
<ul>
<li>Redundant networking</li>
<li>Multiple providers</li>
<li>Distributed state</li>
<li>Circuit breakers</li>
</ul>
<p><strong>Impact:</strong> Prevents cascades</p>
</div>
</div>

## Real-World Examples

<div class="example-box">
<h4>Example: E-commerce Platform</h4>
<ul>
<li><strong>Web Tier:</strong> 99.9% (N+1 redundancy)</li>
<li><strong>Database:</strong> 99.95% (Active-standby)</li>
<li><strong>CDN:</strong> 99.99% (Global distribution)</li>
<li><strong>Overall:</strong> ~99.84% availability</li>
</ul>
</div>

<div class="example-box">
<h4>Example: Banking System</h4>
<ul>
<li><strong>Core Banking:</strong> 99.999% (Active-active)</li>
<li><strong>ATM Network:</strong> 99.99% (Regional redundancy)</li>
<li><strong>Mobile App:</strong> 99.9% (Multi-region)</li>
<li><strong>Disaster Recovery:</strong> RPO < 1 hour</li>
</ul>
</div>

## Related Resources

- [Availability Math Deep Dive](/quantitative/availability-math)
- [MTBF and MTTR Explained](/quantitative/mtbf-mttr)
- [Failover Pattern](/patterns/failover)
- Multi-Region Architecture (Coming Soon)
- [Chaos Engineering](/human-factors/chaos-engineering)

<script>
// Enhanced availability calculator with validation and visualizations
let availChart = null;

function validateAvailabilityInputs() {
    const inputs = {
        mtbf: { value: parseFloat(document.getElementById('componentMTBF').value), min: 1, max: 1000000, name: 'MTBF' },
        mttr: { value: parseFloat(document.getElementById('componentMTTR').value), min: 0.1, max: 1000, name: 'MTTR' },
        numComponents: { value: parseInt(document.getElementById('numComponents').value), min: 1, max: 100, name: 'Components' },
        redundancyType: { value: document.getElementById('redundancyType').value, name: 'Redundancy type' },
        failoverTime: { value: parseFloat(document.getElementById('failoverTime').value), min: 0, max: 60, name: 'Failover time' },
        numRegions: { value: parseInt(document.getElementById('numRegions').value), min: 1, max: 10, name: 'Regions' },
        regionFailureRate: { value: parseFloat(document.getElementById('regionFailureRate').value), min: 0, max: 1, name: 'Region failure rate' },
        targetSLA: { value: parseFloat(document.getElementById('targetSLA').value), min: 90, max: 99.999, name: 'Target SLA' }
    };
    
    const errors = [];
    
    // Validate numeric inputs
    for (const [key, input] of Object.entries(inputs)) {
        if (key === 'redundancyType') continue;
        
        if (isNaN(input.value)) {
            errors.push(`${input.name} must be a number`);
        } else if (input.min !== undefined && input.max !== undefined && 
                   (input.value < input.min || input.value > input.max)) {
            errors.push(`${input.name} must be between ${input.min} and ${input.max}`);
        }
    }
    
    // Validate MTBF > MTTR
    if (inputs.mtbf.value <= inputs.mttr.value) {
        errors.push('MTBF must be greater than MTTR');
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function calculateAvailability() {
    // Validate inputs
    const validation = validateAvailabilityInputs();
    if (!validation.valid) {
        displayAvailabilityErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    const failoverTimeHours = inputs.failoverTime.value / 60; // Convert to hours
    
    // Calculate base component availability
    const componentAvailability = mtbf / (mtbf + mttr);
    
    // Calculate serial system availability
    const serialAvailability = Math.pow(componentAvailability, numComponents);
    
    // Apply redundancy
    let systemAvailability = serialAvailability;
    let redundancyFactor = 1;
    
    switch(redundancyType) {
        case 'active-standby':
            // 1+1 redundancy with failover time
            const effectiveMTTR = failoverTime;
            const redundantAvailability = 1 - Math.pow(1 - (mtbf / (mtbf + effectiveMTTR)), 2);
            systemAvailability = Math.pow(redundantAvailability, numComponents);
            redundancyFactor = 2;
            break;
            
        case 'n-plus-1':
            // N+1 redundancy
            systemAvailability = 1 - Math.pow(1 - serialAvailability, 2);
            redundancyFactor = 1.1;
            break;
            
        case 'n-plus-2':
            // N+2 redundancy
            systemAvailability = 1 - Math.pow(1 - serialAvailability, 3);
            redundancyFactor = 1.2;
            break;
            
        case 'active-active':
            // 2N redundancy
            systemAvailability = 1 - Math.pow(1 - serialAvailability, 2);
            redundancyFactor = 2;
            break;
    }
    
    // Apply multi-region configuration
    if (numRegions > 1) {
        const regionAvailability = 1 - regionFailureRate;
        const multiRegionAvailability = 1 - Math.pow(1 - (systemAvailability * regionAvailability), numRegions);
        systemAvailability = multiRegionAvailability;
    }
    
    // Calculate downtime
    const yearlyHours = 8760;
    const downtimeHours = (1 - systemAvailability) * yearlyHours;
    const downtimeMinutes = downtimeHours * 60;
    
    // Calculate nines
    const nines = -Math.log10(1 - systemAvailability);
    
    // Generate results
    let resultsHTML = `
        <h3>📊 Availability Analysis</h3>
        
        <div class="availability-summary">
            <div class="big-metric">
                <div class="metric-value">${(systemAvailability * 100).toFixed(4)}%</div>
                <div class="metric-label">System Availability</div>
                <div class="metric-detail">${nines.toFixed(1)} nines</div>
            </div>
            
            <div class="downtime-metrics">
                <div class="downtime-item">
                    <span class="label">Yearly Downtime:</span>
                    <span class="value">${formatDowntime(downtimeHours)}</span>
                </div>
                <div class="downtime-item">
                    <span class="label">Monthly Downtime:</span>
                    <span class="value">${formatDowntime(downtimeHours / 12)}</span>
                </div>
                <div class="downtime-item">
                    <span class="label">Daily Downtime:</span>
                    <span class="value">${formatDowntime(downtimeHours / 365)}</span>
                </div>
            </div>
        </div>
        
        <div class="component-breakdown">
            <h4>Component Analysis</h4>
            <table class="responsive-table">
  <thead>
    <tr>
                    <th>Component</th>
                    <th>Availability</th>
                    <th>Downtime/Year</th>
                </tr>
  </thead>
  <tbody>
    <tr>
                    <td data-label="Component">Single Component</td>
                    <td data-label="Availability">${(componentAvailability * 100).toFixed(3)}%</td>
                    <td data-label="Downtime/Year">${formatDowntime((1 - componentAvailability) * yearlyHours)}</td>
                </tr>
    <tr>
                    <td data-label="Component">Serial System (${numComponents} components)</td>
                    <td data-label="Availability">${(serialAvailability * 100).toFixed(3)}%</td>
                    <td data-label="Downtime/Year">${formatDowntime((1 - serialAvailability) * yearlyHours)}</td>
                </tr>
    <tr>
                    <td data-label="Component">With ${redundancyType.replace('-', ' ')}</td>
                    <td data-label="Availability">${(systemAvailability * 100).toFixed(4)}%</td>
                    <td data-label="Downtime/Year">${formatDowntime(downtimeHours)}</td>
                </tr>
  </tbody>
</table>
        </div>
        
        <div class="sla-comparison">
            <h4>SLA Target Comparison</h4>
    `;
    
    if (systemAvailability >= targetSLA / 100) {
        resultsHTML += `
            <div class="sla-met">
                ✅ System meets ${targetSLA}% SLA target
                <p>Margin: ${((systemAvailability - targetSLA/100) * yearlyHours * 60).toFixed(1)} minutes/year</p>
            </div>
        `;
    } else {
        const gap = (targetSLA/100 - systemAvailability) * yearlyHours;
        resultsHTML += `
            <div class="sla-not-met">
                ❌ System does not meet ${targetSLA}% SLA target
                <p>Gap: ${formatDowntime(gap)} additional uptime needed</p>
            </div>
        `;
    }
    
    resultsHTML += `
        </div>
        
        <div class="cost-analysis">
            <h4>💰 Cost-Benefit Analysis</h4>
            <table class="responsive-table">
  <thead>
    <tr>
                    <th>Configuration</th>
                    <th>Availability</th>
                    <th>Resource Multiplier</th>
                    <th>Cost Impact</th>
                </tr>
  </thead>
  <tbody>
    <tr>
                    <td data-label="Configuration">No Redundancy</td>
                    <td data-label="Availability">${(serialAvailability * 100).toFixed(2)}%</td>
                    <td data-label="Resource Multiplier">1x</td>
                    <td data-label="Cost Impact">Baseline</td>
                </tr>
    <tr>
                    <td data-label="Configuration">Current (${redundancyType})</td>
                    <td data-label="Availability">${(systemAvailability * 100).toFixed(3)}%</td>
                    <td data-label="Resource Multiplier">${redundancyFactor}x</td>
                    <td data-label="Cost Impact">+${((redundancyFactor - 1) * 100).toFixed(0)}%</td>
                </tr>
    <tr>
                    <td data-label="Configuration">Add Region</td>
                    <td data-label="Availability">${calculateNextRegion(systemAvailability, regionFailureRate)}%</td>
                    <td data-label="Resource Multiplier">${(redundancyFactor * 2).toFixed(1)}x</td>
                    <td data-label="Cost Impact">+${((redundancyFactor * 2 - 1) * 100).toFixed(0)}%</td>
                </tr>
  </tbody>
</table>
        </div>
        
        <div class="recommendations">
            <h4>💡 Recommendations</h4>
            <ul>
    `;
    
    // Add specific recommendations
    if (systemAvailability < targetSLA / 100) {
        resultsHTML += '<li class="urgent">⚠️ Immediate action needed to meet SLA target</li>';
        
        if (redundancyType === 'none') {
            resultsHTML += '<li>Add redundancy - even Active-Standby would improve availability significantly</li>';
        }
        
        if (numRegions === 1) {
            resultsHTML += '<li>Consider multi-region deployment for major availability gains</li>';
        }
        
        if (mttr > 4) {
            resultsHTML += '<li>Reduce MTTR through automation - current ${mttr}h is high</li>';
        }
    }
    
    if (numComponents > 3 && redundancyType === 'none') {
        resultsHTML += '<li>High component count without redundancy is risky - consider redundancy</li>';
    }
    
    if (failoverTime > 10 && redundancyType !== 'none') {
        resultsHTML += '<li>Failover time of ${failoverTime} minutes is high - aim for under 5 minutes</li>';
    }
    
    resultsHTML += `
            </ul>
        </div>
        
        <div class="visualization">
            <h4>Availability Over Time</h4>
            <canvas id="availChart" width="600" height="200"></canvas>
        </div>
    `;
    
    document.getElementById('results').innerHTML = resultsHTML;
    
    // Draw availability chart
    drawAvailabilityChart(systemAvailability);
}

function formatDowntime(hours) {
    if (hours >= 24) {
        return `${(hours / 24).toFixed(1)} days`;
    } else if (hours >= 1) {
        return `${hours.toFixed(1)} hours`;
    } else {
        return `${(hours * 60).toFixed(1)} minutes`;
    }
}

function calculateNextRegion(currentAvail, regionFailureRate) {
    const regionAvail = 1 - regionFailureRate;
    const twoRegionAvail = 1 - Math.pow(1 - (currentAvail * regionAvail), 2);
    return (twoRegionAvail * 100).toFixed(3);
}

function drawAvailabilityChart(availability) {
    const canvas = document.getElementById('availChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw availability bar
    const barHeight = 40;
    const barY = height / 2 - barHeight / 2;
    
    // Background (downtime)
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(0, barY, width, barHeight);
    
    // Availability portion
    ctx.fillStyle = '#51cf66';
    ctx.fillRect(0, barY, width * availability, barHeight);
    
    // Draw scale
    ctx.fillStyle = '#333';
    ctx.font = '12px sans-serif';
    
    // SLA markers
    const slaMarkers = [0.99, 0.999, 0.9999, 0.99999];
    slaMarkers.forEach(sla => {
        const x = width * sla;
        ctx.strokeStyle = '#666';
        ctx.beginPath();
        ctx.moveTo(x, barY - 10);
        ctx.lineTo(x, barY + barHeight + 10);
        ctx.stroke();
        
        ctx.fillText(`${(sla * 100)}%`, x - 20, barY - 15);
    });
    
    // Current position
    const currentX = width * availability;
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(currentX, barY - 5);
    ctx.lineTo(currentX, barY + barHeight + 5);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = '#000';
    ctx.font = 'bold 14px sans-serif';
    ctx.fillText('Current', currentX - 25, barY + barHeight + 25);
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

.availability-summary {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
    margin: 2rem 0;
    padding: 2rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.big-metric {
    text-align: center;
}

.metric-value {
    font-size: 3rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
}

.metric-label {
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.metric-detail {
    font-size: 1rem;
    color: var(--md-default-fg-color--light);
}

.downtime-metrics {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.downtime-item {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--md-default-fg-color--lighter);
}

.downtime-item:last-child {
    border-bottom: none;
}

.downtime-item .label {
    font-weight: 600;
    margin-right: 1rem;
}

.downtime-item .value {
    float: right;
    color: var(--md-primary-fg-color);
}

.component-breakdown, .sla-comparison, .cost-analysis, .recommendations {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
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

.sla-met {
    padding: 1rem;
    background: #d3f9d8;
    color: #2b8a3e;
    border-radius: 4px;
    font-weight: 600;
}

.sla-not-met {
    padding: 1rem;
    background: #ffe3e3;
    color: #c92a2a;
    border-radius: 4px;
    font-weight: 600;
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

.recommendations li.urgent {
    color: var(--md-error-fg-color);
    font-weight: 600;
}

.availability-table {
    margin: 2rem 0;
}

.availability-table table {
    width: 100%;
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

.example-box {
    padding: 1.5rem;
    margin: 1rem 0;
    background: var(--md-primary-fg-color--light);
    border-radius: 8px;
}

.example-box h4 {
    margin-top: 0;
}

.visualization {
    margin-top: 2rem;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

# availChart {
    max-width: 100%;
    height: auto;
    margin-top: 1rem;
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 1rem;
    }
    
    .availability-summary {
        grid-template-columns: 1fr;
    }
    
    .strategy-grid {
        grid-template-columns: 1fr;
    }
}
</style>
</div>