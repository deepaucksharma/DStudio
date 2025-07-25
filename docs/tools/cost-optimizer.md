# Cost Optimization Calculator

<div class="calculator-container">
<div class="calc-header">
<h2>💵 Distributed Systems Cost Optimizer</h2>
<p>Compare on-premise vs cloud costs, calculate TCO, and find optimal resource allocation for your distributed system.</p>
</div>

## Interactive Calculator

<div class="calculator-tool">
<form id="costCalc">

### Workload Characteristics
<div class="input-group">
<label for="avgRequestsPerSec">Average requests per second:</label>
<input type="number" id="avgRequestsPerSec" value="1000" min="0" step="100">
</div>

<div class="input-group">
<label for="peakMultiplier">Peak traffic multiplier:</label>
<input type="number" id="peakMultiplier" value="3" min="1" step="0.5">
<span class="help">Peak traffic as multiple of average</span>
</div>

<div class="input-group">
<label for="dataStorageGB">Data storage required (GB):</label>
<input type="number" id="dataStorageGB" value="1000" min="0" step="100">
</div>

<div class="input-group">
<label for="monthlyDataGrowth">Monthly data growth (%):</label>
<input type="number" id="monthlyDataGrowth" value="10" min="0" step="1">
</div>

<div class="input-group">
<label for="dataTransferGB">Monthly data transfer (GB):</label>
<input type="number" id="dataTransferGB" value="5000" min="0" step="500">
</div>

### Resource Requirements
<div class="input-group">
<label for="cpuPerRequest">CPU milliseconds per request:</label>
<input type="number" id="cpuPerRequest" value="50" min="1" step="10">
</div>

<div class="input-group">
<label for="memoryPerRequest">Memory MB per concurrent request:</label>
<input type="number" id="memoryPerRequest" value="10" min="1" step="1">
</div>

<div class="input-group">
<label for="availabilityTarget">Availability target (%):</label>
<select id="availabilityTarget">
<option value="99">99% (2 nines)</option>
<option value="99.9">99.9% (3 nines)</option>
<option value="99.95">99.95%</option>
<option value="99.99" selected>99.99% (4 nines)</option>
<option value="99.999">99.999% (5 nines)</option>
</select>
</div>

### Cost Parameters
<div class="input-group">
<label for="cloudProvider">Cloud provider:</label>
<select id="cloudProvider">
<option value="aws">AWS</option>
<option value="gcp">Google Cloud</option>
<option value="azure">Azure</option>
<option value="onprem">On-Premise</option>
</select>
</div>

<div class="input-group">
<label for="region">Deployment region:</label>
<select id="region">
<option value="single">Single region</option>
<option value="multi-2">2 regions (active-standby)</option>
<option value="multi-3">3 regions (active-active)</option>
<option value="global">Global (5+ regions)</option>
</select>
</div>

<div class="input-group">
<label for="planningHorizon">Planning horizon (years):</label>
<input type="number" id="planningHorizon" value="3" min="1" max="5" step="1">
</div>

<button type="button" onclick="calculateCosts()" class="calc-button">Calculate Optimal Cost Strategy</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>
</div>

## Cost Optimization Strategies

<div class="strategy-grid">
<div class="strategy-card">
<h4>💾 Storage Optimization</h4>
<ul>
<li>Hot/Cold tiering</li>
<li>Compression</li>
<li>Deduplication</li>
<li>Lifecycle policies</li>
</ul>
<p><strong>Savings:</strong> 30-70%</p>
</div>

<div class="strategy-card">
<h4>🖥️ Compute Optimization</h4>
<ul>
<li>Reserved instances</li>
<li>Spot instances</li>
<li>Auto-scaling</li>
<li>Right-sizing</li>
</ul>
<p><strong>Savings:</strong> 40-80%</p>
</div>

<div class="strategy-card">
<h4>🌐 Network Optimization</h4>
<ul>
<li>CDN usage</li>
<li>Regional caching</li>
<li>Compression</li>
<li>Peering agreements</li>
</ul>
<p><strong>Savings:</strong> 20-60%</p>
</div>

<div class="strategy-card">
<h4>🏗️ Architecture Optimization</h4>
<ul>
<li>Serverless adoption</li>
<li>Container density</li>
<li>Service consolidation</li>
<li>Event-driven design</li>
</ul>
<p><strong>Savings:</strong> 30-50%</p>
</div>
</div>

## Hidden Costs to Consider

<div class="hidden-costs">
<div class="cost-category">
<h4>👥 Operational Costs</h4>
<ul>
<li>On-call staffing</li>
<li>Training and certification</li>
<li>Monitoring tools</li>
<li>Incident response</li>
</ul>
</div>

<div class="cost-category">
<h4>🔄 Migration Costs</h4>
<ul>
<li>Data transfer fees</li>
<li>Dual running period</li>
<li>Application refactoring</li>
<li>Testing and validation</li>
</ul>
</div>

<div class="cost-category">
<h4>🛡️ Security & Compliance</h4>
<ul>
<li>Security tools</li>
<li>Compliance audits</li>
<li>Data encryption</li>
<li>Access management</li>
</ul>
</div>

<div class="cost-category">
<h4>📈 Growth Costs</h4>
<ul>
<li>Capacity headroom</li>
<li>Performance testing</li>
<li>Disaster recovery</li>
<li>Global expansion</li>
</ul>
</div>
</div>

## Related Resources

- [Economic Reality Law](/part1-axioms/law7-economics/)
- FinOps Best Practices (Coming Soon)
- Multi-Region Architecture (Coming Soon)
- [Storage Economics](/quantitative/storage-economics)
- [Cache Economics](/quantitative/cache-economics)

<script>
// Simplified cloud pricing model (real pricing is more complex)
const cloudPricing = {
    aws: {
        compute: { vcpu: 0.05, memory: 0.005 }, // per hour
        storage: { ssd: 0.10, hdd: 0.025 }, // per GB per month
        transfer: { egress: 0.09, ingress: 0 }, // per GB
        loadBalancer: 25, // per month
        multiRegionPremium: 1.2
    },
    gcp: {
        compute: { vcpu: 0.045, memory: 0.0045 },
        storage: { ssd: 0.09, hdd: 0.02 },
        transfer: { egress: 0.08, ingress: 0 },
        loadBalancer: 20,
        multiRegionPremium: 1.15
    },
    azure: {
        compute: { vcpu: 0.048, memory: 0.0048 },
        storage: { ssd: 0.095, hdd: 0.022 },
        transfer: { egress: 0.087, ingress: 0 },
        loadBalancer: 22,
        multiRegionPremium: 1.18
    },
    onprem: {
        serverCost: 5000, // per server
        serverLifespan: 3, // years
        powerCooling: 200, // per server per month
        networkHardware: 50000, // one-time
        staffMultiplier: 1.5 // vs cloud
    }
};

function calculateCosts() {
    // Get inputs
    const avgRPS = parseFloat(document.getElementById('avgRequestsPerSec').value);
    const peakMultiplier = parseFloat(document.getElementById('peakMultiplier').value);
    const storageGB = parseFloat(document.getElementById('dataStorageGB').value);
    const monthlyGrowth = parseFloat(document.getElementById('monthlyDataGrowth').value) / 100;
    const transferGB = parseFloat(document.getElementById('dataTransferGB').value);
    const cpuPerRequest = parseFloat(document.getElementById('cpuPerRequest').value);
    const memoryPerRequest = parseFloat(document.getElementById('memoryPerRequest').value);
    const availabilityTarget = parseFloat(document.getElementById('availabilityTarget').value);
    const provider = document.getElementById('cloudProvider').value;
    const region = document.getElementById('region').value;
    const planYears = parseInt(document.getElementById('planningHorizon').value);
    
    // Calculate resource requirements
    const peakRPS = avgRPS * peakMultiplier;
    const avgConcurrentRequests = avgRPS * (cpuPerRequest / 1000); // Little's Law
    const peakConcurrentRequests = peakRPS * (cpuPerRequest / 1000);
    
    // CPU requirements (with 70% target utilization)
    const vcpusNeeded = Math.ceil((peakRPS * cpuPerRequest / 1000) / 0.7);
    
    // Memory requirements
    const memoryGB = Math.ceil((peakConcurrentRequests * memoryPerRequest) / 1024);
    
    // Redundancy for availability
    let redundancyFactor = 1;
    if (availabilityTarget >= 99.99) redundancyFactor = 2;
    if (availabilityTarget >= 99.999) redundancyFactor = 3;
    
    // Regional multiplier
    let regionMultiplier = 1;
    if (region === 'multi-2') regionMultiplier = 2;
    if (region === 'multi-3') regionMultiplier = 3;
    if (region === 'global') regionMultiplier = 5;
    
    // Calculate costs for each option
    const costBreakdown = {};
    
    if (provider === 'onprem') {
        // On-premise calculation
        const serversNeeded = Math.ceil((vcpusNeeded * redundancyFactor) / 16); // 16 vCPUs per server
        const totalServers = serversNeeded * regionMultiplier;
        
        costBreakdown.onprem = calculateOnPremCosts(
            totalServers,
            storageGB,
            transferGB,
            planYears,
            monthlyGrowth
        );
    } else {
        // Cloud calculation
        costBreakdown.cloud = calculateCloudCosts(
            provider,
            vcpusNeeded * redundancyFactor * regionMultiplier,
            memoryGB * redundancyFactor * regionMultiplier,
            storageGB,
            transferGB,
            region,
            planYears,
            monthlyGrowth
        );
        
        // Also calculate comparison with other providers
        ['aws', 'gcp', 'azure'].forEach(p => {
            if (p !== provider) {
                costBreakdown[p] = calculateCloudCosts(
                    p,
                    vcpusNeeded * redundancyFactor * regionMultiplier,
                    memoryGB * redundancyFactor * regionMultiplier,
                    storageGB,
                    transferGB,
                    region,
                    planYears,
                    monthlyGrowth
                );
            }
        });
    }
    
    // Generate results
    displayCostResults(costBreakdown, {
        avgRPS,
        peakRPS,
        vcpusNeeded: vcpusNeeded * redundancyFactor * regionMultiplier,
        memoryGB: memoryGB * redundancyFactor * regionMultiplier,
        storageGB,
        planYears,
        provider,
        region
    });
}

function calculateCloudCosts(provider, vcpus, memoryGB, storageGB, transferGB, region, years, growthRate) {
    const pricing = cloudPricing[provider];
    const monthlyHours = 730;
    
    // Compute costs
    const computeMonthly = (vcpus * pricing.compute.vcpu + memoryGB * pricing.compute.memory) * monthlyHours;
    
    // Storage costs (assuming 80% SSD, 20% HDD)
    const storageMonthly = storageGB * (0.8 * pricing.storage.ssd + 0.2 * pricing.storage.hdd);
    
    // Transfer costs
    const transferMonthly = transferGB * pricing.transfer.egress;
    
    // Additional services
    const servicesMonthly = pricing.loadBalancer * (region === 'single' ? 1 : parseInt(region.split('-')[1] || 5));
    
    // Apply regional premium
    const regionPremium = region !== 'single' ? pricing.multiRegionPremium : 1;
    
    // Calculate total over time with growth
    let totalCost = 0;
    let monthlyBreakdown = [];
    
    for (let month = 0; month < years * 12; month++) {
        const growthFactor = Math.pow(1 + growthRate, month);
        const monthCost = (computeMonthly + storageMonthly * growthFactor + transferMonthly + servicesMonthly) * regionPremium;
        totalCost += monthCost;
        
        if (month % 12 === 0) {
            monthlyBreakdown.push({
                year: month / 12 + 1,
                monthly: monthCost,
                compute: computeMonthly * regionPremium,
                storage: storageMonthly * growthFactor * regionPremium,
                transfer: transferMonthly * regionPremium,
                services: servicesMonthly * regionPremium
            });
        }
    }
    
    return {
        total: totalCost,
        monthlyAverage: totalCost / (years * 12),
        breakdown: monthlyBreakdown,
        provider: provider
    };
}

function calculateOnPremCosts(servers, storageGB, transferGB, years, growthRate) {
    const pricing = cloudPricing.onprem;
    
    // Capital expenses
    const serverCapex = servers * pricing.serverCost;
    const networkCapex = pricing.networkHardware;
    const storageCapex = (storageGB / 1000) * 2000; // $2/GB for enterprise storage
    
    // Operating expenses per month
    const powerCoolingMonthly = servers * pricing.powerCooling;
    const bandwidthMonthly = transferGB * 0.02; // Assuming $0.02/GB
    const staffingMonthly = 15000 * pricing.staffMultiplier; // Assuming base cloud staffing of $15k/month
    
    // Calculate total over time
    let totalCost = serverCapex + networkCapex + storageCapex;
    let monthlyBreakdown = [];
    
    for (let month = 0; month < years * 12; month++) {
        const growthFactor = Math.pow(1 + growthRate, month);
        
        // Additional storage capex every year for growth
        if (month > 0 && month % 12 === 0) {
            totalCost += (storageGB * (Math.pow(1 + growthRate, 12) - 1) / 1000) * 2000;
        }
        
        // Monthly opex
        const monthCost = powerCoolingMonthly + bandwidthMonthly + staffingMonthly;
        totalCost += monthCost;
        
        if (month % 12 === 0) {
            monthlyBreakdown.push({
                year: month / 12 + 1,
                monthly: monthCost,
                capex: month === 0 ? serverCapex + networkCapex + storageCapex : 0,
                opex: monthCost,
                cumulative: totalCost
            });
        }
    }
    
    return {
        total: totalCost,
        monthlyAverage: totalCost / (years * 12),
        breakdown: monthlyBreakdown,
        provider: 'onprem',
        capex: serverCapex + networkCapex + storageCapex
    };
}

function displayCostResults(costBreakdown, params) {
    let resultsHTML = `
        <h3>💰 Cost Optimization Analysis</h3>
        
        <div class="summary-section">
            <h4>Workload Summary</h4>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">Average Load:</span>
                    <span class="value">${params.avgRPS.toLocaleString()} RPS</span>
                </div>
                <div class="summary-item">
                    <span class="label">Peak Load:</span>
                    <span class="value">${params.peakRPS.toLocaleString()} RPS</span>
                </div>
                <div class="summary-item">
                    <span class="label">Compute:</span>
                    <span class="value">${params.vcpusNeeded} vCPUs</span>
                </div>
                <div class="summary-item">
                    <span class="label">Memory:</span>
                    <span class="value">${params.memoryGB} GB</span>
                </div>
                <div class="summary-item">
                    <span class="label">Storage:</span>
                    <span class="value">${params.storageGB.toLocaleString()} GB</span>
                </div>
                <div class="summary-item">
                    <span class="label">Regions:</span>
                    <span class="value">${params.region}</span>
                </div>
            </div>
        </div>
        
        <div class="cost-comparison">
            <h4>Total Cost Comparison (${params.planYears} years)</h4>
            <div class="comparison-cards">
    `;
    
    // Sort providers by total cost
    const sortedProviders = Object.entries(costBreakdown)
        .sort((a, b) => a[1].total - b[1].total);
    
    sortedProviders.forEach(([provider, costs], index) => {
        const isLowest = index === 0;
        const monthlyAvg = costs.monthlyAverage;
        
        resultsHTML += `
            <div class="provider-card ${isLowest ? 'lowest-cost' : ''}">
                <h5>${provider.toUpperCase()} ${isLowest ? '✅' : ''}</h5>
                <div class="cost-total">$${costs.total.toLocaleString()}</div>
                <div class="cost-monthly">$${monthlyAvg.toFixed(0).toLocaleString()}/month avg</div>
                ${costs.capex ? `<div class="cost-capex">Capex: $${costs.capex.toLocaleString()}</div>` : ''}
                <div class="cost-savings">${isLowest ? 'BEST VALUE' : `+${(((costs.total / sortedProviders[0][1].total) - 1) * 100).toFixed(0)}% vs best`}</div>
            </div>
        `;
    });
    
    resultsHTML += `
            </div>
        </div>
        
        <div class="optimization-recommendations">
            <h4>💡 Cost Optimization Recommendations</h4>
            <ul>
    `;
    
    // Generate recommendations based on analysis
    const lowestCost = sortedProviders[0][1].total;
    const currentProvider = costBreakdown[params.provider] || costBreakdown.cloud;
    
    if (currentProvider && currentProvider.total > lowestCost * 1.1) {
        resultsHTML += `<li class="urgent">⚠️ Consider switching to ${sortedProviders[0][0].toUpperCase()} for ${(((currentProvider.total / lowestCost) - 1) * 100).toFixed(0)}% cost savings</li>`;
    }
    
    if (params.avgRPS < params.peakRPS * 0.3) {
        resultsHTML += '<li>High peak-to-average ratio (3x) - consider auto-scaling or serverless</li>';
    }
    
    if (params.storageGB > 5000) {
        resultsHTML += '<li>Large storage footprint - implement tiered storage (hot/warm/cold)</li>';
    }
    
    if (params.region !== 'single' && params.provider !== 'onprem') {
        resultsHTML += '<li>Multi-region deployment - use reserved instances for baseline capacity</li>';
    }
    
    resultsHTML += `
                <li>Implement aggressive auto-scaling to reduce idle capacity</li>
                <li>Use spot instances for batch workloads (up to 90% savings)</li>
                <li>Compress data transfers to reduce egress costs</li>
                <li>Review and optimize unused resources monthly</li>
            </ul>
        </div>
        
        <div class="cost-breakdown-chart">
            <h4>Cost Breakdown by Category</h4>
            <canvas id="costChart" width="600" height="300"></canvas>
        </div>
        
        <div class="savings-opportunities">
            <h4>Quick Win Opportunities</h4>
            <table>
                <tr>
                    <th>Action</th>
                    <th>Effort</th>
                    <th>Potential Savings</th>
                    <th>Time to Implement</th>
                </tr>
                <tr>
                    <td>Right-size instances</td>
                    <td>Low</td>
                    <td>10-30%</td>
                    <td>1 week</td>
                </tr>
                <tr>
                    <td>Reserved instances</td>
                    <td>Low</td>
                    <td>30-60%</td>
                    <td>Immediate</td>
                </tr>
                <tr>
                    <td>Storage tiering</td>
                    <td>Medium</td>
                    <td>40-70%</td>
                    <td>2-4 weeks</td>
                </tr>
                <tr>
                    <td>CDN implementation</td>
                    <td>Medium</td>
                    <td>20-50%</td>
                    <td>2-3 weeks</td>
                </tr>
                <tr>
                    <td>Serverless migration</td>
                    <td>High</td>
                    <td>50-80%</td>
                    <td>2-6 months</td>
                </tr>
            </table>
        </div>
    `;
    
    document.getElementById('results').innerHTML = resultsHTML;
    
    // Draw cost breakdown chart
    if (sortedProviders.length > 0) {
        drawCostChart(sortedProviders[0][1]);
    }
}

function drawCostChart(providerCosts) {
    const canvas = document.getElementById('costChart');
    if (!canvas || !providerCosts.breakdown || providerCosts.breakdown.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Prepare data
    const categories = providerCosts.breakdown[0].compute !== undefined 
        ? ['compute', 'storage', 'transfer', 'services']
        : ['capex', 'opex'];
    
    const colors = {
        compute: '#5448C8',
        storage: '#00BCD4',
        transfer: '#4CAF50',
        services: '#FF9800',
        capex: '#F44336',
        opex: '#9C27B0'
    };
    
    // Draw bars for first year costs
    const firstYear = providerCosts.breakdown[0];
    const values = categories.map(cat => firstYear[cat] || 0);
    const maxValue = Math.max(...values);
    
    const barWidth = (width - 2 * padding) / categories.length - 20;
    const barSpacing = 20;
    
    categories.forEach((category, i) => {
        const value = values[i];
        const barHeight = (value / maxValue) * (height - 2 * padding);
        const x = padding + i * (barWidth + barSpacing);
        const y = height - padding - barHeight;
        
        // Draw bar
        ctx.fillStyle = colors[category];
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Draw label
        ctx.fillStyle = '#333';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(category.charAt(0).toUpperCase() + category.slice(1), x + barWidth / 2, height - padding + 20);
        
        // Draw value
        ctx.fillText(`$${(value / 1000).toFixed(0)}k`, x + barWidth / 2, y - 5);
    });
    
    // Title
    ctx.font = '14px sans-serif';
    ctx.fillText('Monthly Cost Breakdown (Year 1)', width / 2, padding / 2);
}
</script>

<style>
.calculator-container {
    max-width: 1000px;
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

.summary-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.summary-item {
    text-align: center;
}

.summary-item .label {
    display: block;
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
}

.summary-item .value {
    display: block;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--md-primary-fg-color);
}

.cost-comparison {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.comparison-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.provider-card {
    padding: 1.5rem;
    background: var(--md-default-bg-color);
    border: 2px solid var(--md-default-fg-color--lighter);
    border-radius: 8px;
    text-align: center;
}

.provider-card.lowest-cost {
    border-color: #51cf66;
    background: #d3f9d8;
}

.provider-card h5 {
    margin: 0 0 1rem 0;
    color: var(--md-primary-fg-color);
}

.cost-total {
    font-size: 2rem;
    font-weight: 700;
    color: var(--md-primary-fg-color);
}

.cost-monthly {
    font-size: 0.875rem;
    color: var(--md-default-fg-color--light);
    margin: 0.5rem 0;
}

.cost-capex {
    font-size: 0.875rem;
    color: var(--md-warning-fg-color);
}

.cost-savings {
    margin-top: 1rem;
    padding: 0.5rem;
    background: var(--md-primary-fg-color--light);
    border-radius: 4px;
    font-weight: 600;
}

.optimization-recommendations {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.optimization-recommendations ul {
    list-style: none;
    padding: 0;
}

.optimization-recommendations li {
    padding: 0.75rem 0;
    padding-left: 2rem;
    position: relative;
}

.optimization-recommendations li:before {
    content: "→";
    position: absolute;
    left: 0.5rem;
}

.optimization-recommendations li.urgent {
    color: var(--md-error-fg-color);
    font-weight: 600;
}

.cost-breakdown-chart {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

#costChart {
    max-width: 100%;
    height: auto;
}

.savings-opportunities {
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--md-code-bg-color);
    border-radius: 8px;
}

.savings-opportunities table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

.savings-opportunities th,
.savings-opportunities td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--md-default-fg-color--lighter);
}

.savings-opportunities th {
    font-weight: 600;
    background: var(--md-default-bg-color);
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

.hidden-costs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.cost-category {
    padding: 1.5rem;
    background: var(--md-warning-bg-color);
    border-radius: 8px;
    border-left: 4px solid var(--md-warning-fg-color);
}

.cost-category h4 {
    margin-top: 0;
    color: var(--md-warning-fg-color);
}

.cost-category ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 1rem;
    }
    
    .strategy-grid, .hidden-costs {
        grid-template-columns: 1fr;
    }
}
</style>
</div>