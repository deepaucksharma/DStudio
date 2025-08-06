---
title: Geo-Distribution Planner
description: Multi-region latency optimization, data residency, and cost analysis
type: documentation
---

# Geo-Distribution Planner



## Overview

Geo-Distribution Planner
description: Multi-region latency optimization, data residency, and cost analysis
type: documentation
---

# Geo-Distribution Planner

## Table of Contents

- [Interactive Planner](#interactive-planner)
  - [Global Traffic Distribution](#global-traffic-distribution)
  - [Latency Requirements](#latency-requirements)
  - [Data Residency & Compliance](#data-residency-compliance)
  - [Cost Optimization](#cost-optimization)
  - [Infrastructure Configuration](#infrastructure-configuration)
- [Understanding Geographic Distribution](#understanding-geographic-distribution)
  - [Latency Components](#latency-components)
  - [Regional Considerations](#regional-considerations)
  - [Cost Optimization Strategies](#cost-optimization-strategies)
- [Related Resources](#related-resources)



! Advanced Geographic Distribution Calculator"
    <h2>🌍 Multi-Region Deployment Planner</h2>
    <p>Optimize global infrastructure deployment with latency analysis, data residency compliance, and cost optimization.

**Reading time:** ~17 minutes

## Table of Contents

- [Interactive Planner](#interactive-planner)
  - [Global Traffic Distribution](#global-traffic-distribution)
  - [Latency Requirements](#latency-requirements)
  - [Data Residency & Compliance](#data-residency-compliance)
  - [Cost Optimization](#cost-optimization)
  - [Infrastructure Configuration](#infrastructure-configuration)
- [Understanding Geographic Distribution](#understanding-geographic-distribution)
  - [Latency Components](#latency-components)
  - [Regional Considerations](#regional-considerations)
  - [Cost Optimization Strategies](#cost-optimization-strategies)
- [Related Resources](#related-resources)



!!! info "Advanced Geographic Distribution Calculator"
    <h2>🌍 Multi-Region Deployment Planner</h2>
    <p>Optimize global infrastructure deployment with latency analysis, data residency compliance, and cost optimization.</p>

## Interactive Planner

<div class="calculator-tool">
<form id="geoDistributionCalc">

### Global Traffic Distribution

<label for="globalTraffic">Total daily requests (millions):</label>
<input type="number" id="globalTraffic" value="100" min="1" step="1">
*Daily request volume across all regions*

<div class="region-config">
<h4>Regional Traffic Distribution</h4>
<div id="regionTraffic">
<div class="region-row">
    <select class="region-select">
        <option value="us-east-1">US East (N. Virginia)</option>
        <option value="us-west-2">US West (Oregon)</option>
        <option value="eu-west-1">Europe (Ireland)</option>
        <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
        <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
        <option value="ap-south-1">Asia Pacific (Mumbai)</option>
        <option value="sa-east-1">South America (São Paulo)</option>
        <option value="af-south-1">Africa (Cape Town)</option>
        <option value="me-south-1">Middle East (Bahrain)</option>
        <option value="ca-central-1">Canada (Central)</option>
        <option value="eu-central-1">Europe (Frankfurt)</option>
        <option value="ap-southeast-2">Asia Pacific (Sydney)</option>
    </select>
    <input type="number" class="traffic-percentage" placeholder="Traffic %" min="0" max="100" value="30">
    <label>% of traffic</label>
    <button type="button" onclick="removeRegion(this)" class="remove-region">×</button>
</div>
</div>
<button type="button" onclick="addRegion()" class="add-region">+ Add Region</button>
</div>

### Latency Requirements

<label for="targetLatency">Target P95 latency (ms):</label>
<input type="number" id="targetLatency" value="200" min="10" step="10">
*95th percentile response time requirement*

<label for="cdnEnabled">CDN Configuration:</label>
<select id="cdnEnabled">
<option value="none">No CDN</option>
<option value="basic">Basic CDN (static assets)</option>
<option value="dynamic">Dynamic acceleration</option>
<option value="edge-compute">Edge computing</option>
</select>

### Data Residency & Compliance

<div class="compliance-section">
<h4>Regulatory Requirements</h4>
<label><input type="checkbox" id="gdprCompliance" checked> GDPR (EU data residency)</label>
<label><input type="checkbox" id="ccpaCompliance"> CCPA (California)</label>
<label><input type="checkbox" id="pipdpCompliance"> PIPDP (Singapore)</label>
<label><input type="checkbox" id="lgpdCompliance"> LGPD (Brazil)</label>
<label><input type="checkbox" id="pipedaCompliance"> PIPEDA (Canada)</label>
</div>

<label for="dataClassification">Data classification:</label>
<select id="dataClassification">
<option value="public">Public data</option>
<option value="internal">Internal data</option>
<option value="confidential">Confidential data</option>
<option value="restricted">Restricted/PII data</option>
</select>

### Cost Optimization

<label for="budgetConstraint">Monthly budget constraint ($):</label>
<input type="number" id="budgetConstraint" value="50000" min="1000" step="1000">
*Maximum monthly infrastructure cost*

<label for="costPriority">Cost optimization priority:</label>
<select id="costPriority">
<option value="performance">Performance first</option>
<option value="balanced">Balanced approach</option>
<option value="cost">Cost minimization</option>
</select>

<label for="scalingPattern">Traffic scaling pattern:</label>
<select id="scalingPattern">
<option value="steady">Steady traffic</option>
<option value="daily">Daily peaks (3x base)</option>
<option value="weekly">Weekly cycles (2x base)</option>
<option value="seasonal">Seasonal spikes (5x base)</option>
<option value="viral">Viral potential (10x base)</option>
</select>

### Infrastructure Configuration

<label for="computeType">Compute requirements:</label>
<select id="computeType">
<option value="light">Light (web servers)</option>
<option value="moderate">Moderate (API services)</option>
<option value="heavy">Heavy (data processing)</option>
<option value="gpu">GPU intensive</option>
</select>

<label for="storageType">Primary storage type:</label>
<select id="storageType">
<option value="ssd">SSD block storage</option>
<option value="object">Object storage</option>
<option value="database">Managed database</option>
<option value="cache">In-memory cache</option>
</select>

<label for="replicationStrategy">Data replication:</label>
<select id="replicationStrategy">
<option value="none">No replication</option>
<option value="async">Asynchronous replication</option>
<option value="sync">Synchronous replication</option>
<option value="eventual">Eventually consistent</option>
</select>

<button type="button" onclick="calculateGeoDistribution()" class="calc-button">Analyze Distribution</button>
<button type="button" onclick="exportResults()" class="export-button">Export Results</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Geographic Distribution

### Latency Components

**Network Latency Factors:**
```
Total Latency = Propagation + Transmission + Processing + Queueing
```

**Distance Impact:**
- Speed of light: ~200,000 km/s in fiber
- Round-trip time ≈ 2 × distance / speed of light
- US East to West: ~70ms base latency
- US to Europe: ~120ms base latency
- US to Asia: ~180ms base latency

### Regional Considerations

<div class="strategy-card">
<div>
<h4>🇺🇸 North America</h4>
<ul>
<li>Primary: us-east-1 (Virginia)</li>
<li>Secondary: us-west-2 (Oregon)</li>
<li>Compliance: CCPA, SOX, HIPAA</li>
<li>Cost: Moderate to low</li>
</ul>
</div>

<div>
<h4>🇪🇺 Europe</h4>
<ul>
<li>Primary: eu-west-1 (Ireland)</li>
<li>Secondary: eu-central-1 (Frankfurt)</li>
<li>Compliance: GDPR mandatory</li>
<li>Cost: 10-15% premium</li>
</ul>
</div>

<div>
<h4>🌏 Asia Pacific</h4>
<ul>
<li>Primary: ap-southeast-1 (Singapore)</li>
<li>Secondary: ap-northeast-1 (Tokyo)</li>
<li>Compliance: PIPDP, local regulations</li>
<li>Cost: 15-25% premium</li>
</ul>
</div>

<div>
<h4>🌎 Emerging Markets</h4>
<ul>
<li>Africa: af-south-1 (Cape Town)</li>
<li>Middle East: me-south-1 (Bahrain)</li>
<li>South America: sa-east-1 (São Paulo)</li>
<li>Cost: 20-30% premium, limited services</li>
</ul>
</div>
</div>

### Cost Optimization Strategies

<table class="responsive-table">
<thead>
<tr>
<th>Strategy</th>
<th>Cost Savings</th>
<th>Complexity</th>
<th>Performance Impact</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Strategy">Reserved Instances</td>
<td data-label="Cost Savings">30-60%</td>
<td data-label="Complexity">Low</td>
<td data-label="Performance Impact">None</td>
</tr>
<tr>
<td data-label="Strategy">Spot Instances</td>
<td data-label="Cost Savings">50-90%</td>
<td data-label="Complexity">High</td>
<td data-label="Performance Impact">Variable</td>
</tr>
<tr>
<td data-label="Strategy">Auto Scaling</td>
<td data-label="Cost Savings">20-40%</td>
<td data-label="Complexity">Medium</td>
<td data-label="Performance Impact">Positive</td>
</tr>
<tr>
<td data-label="Strategy">Edge Caching</td>
<td data-label="Cost Savings">10-30%</td>
<td data-label="Complexity">Medium</td>
<td data-label="Performance Impact">Very Positive</td>
</tr>
</tbody>
</table>

## Related Resources

- [Latency Calculator](latency-calculator.md)
- [Cost Optimizer](cost-optimizer.md)
- [Availability Calculator](availability-calculator.md)
- [CDN Architecture Patterns](../../pattern-library/scaling/caching-strategies.md)

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let distributionChart = null;
let latencyChart = null;
let costChart = null;

/ Region data with latency information
const regionData = {
    'us-east-1': { name: 'US East (N. Virginia)', lat: 39.0458, lng: -77.5077, cost: 1.0, availability: 99.99 },
    'us-west-2': { name: 'US West (Oregon)', lat: 45.5152, lng: -122.6784, cost: 1.0, availability: 99.99 },
    'eu-west-1': { name: 'Europe (Ireland)', lat: 53.3498, lng: -6.2603, cost: 1.15, availability: 99.99 },
    'eu-central-1': { name: 'Europe (Frankfurt)', lat: 50.1109, lng: 8.6821, cost: 1.12, availability: 99.99 },
    'ap-southeast-1': { name: 'Asia Pacific (Singapore)', lat: 1.3521, lng: 103.8198, cost: 1.20, availability: 99.95 },
    'ap-northeast-1': { name: 'Asia Pacific (Tokyo)', lat: 35.6762, lng: 139.6503, cost: 1.25, availability: 99.99 },
    'ap-south-1': { name: 'Asia Pacific (Mumbai)', lat: 19.0760, lng: 72.8777, cost: 1.10, availability: 99.95 },
    'sa-east-1': { name: 'South America (São Paulo)', lat: -23.5505, lng: -46.6333, cost: 1.30, availability: 99.9 },
    'af-south-1': { name: 'Africa (Cape Town)', lat: -33.9249, lng: 18.4241, cost: 1.35, availability: 99.9 },
    'me-south-1': { name: 'Middle East (Bahrain)', lat: 26.0667, lng: 50.5577, cost: 1.28, availability: 99.95 },
    'ca-central-1': { name: 'Canada (Central)', lat: 43.6532, lng: -79.3832, cost: 1.08, availability: 99.99 },
    'ap-southeast-2': { name: 'Asia Pacific (Sydney)', lat: -33.8688, lng: 151.2093, cost: 1.22, availability: 99.99 }
};

function addRegion() {
    const container = document.getElementById('regionTraffic');
    const newRow = document.createElement('div');
    newRow.className = 'region-row';
    newRow.innerHTML = `
        <select class="region-select">
            <option value="us-east-1">US East (N. Virginia)</option>
            <option value="us-west-2">US West (Oregon)</option>
            <option value="eu-west-1">Europe (Ireland)</option>
            <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
            <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
            <option value="ap-south-1">Asia Pacific (Mumbai)</option>
            <option value="sa-east-1">South America (São Paulo)</option>
            <option value="af-south-1">Africa (Cape Town)</option>
            <option value="me-south-1">Middle East (Bahrain)</option>
            <option value="ca-central-1">Canada (Central)</option>
            <option value="eu-central-1">Europe (Frankfurt)</option>
            <option value="ap-southeast-2">Asia Pacific (Sydney)</option>
        </select>
        <input type="number" class="traffic-percentage" placeholder="Traffic %" min="0" max="100" value="10">
        <label>% of traffic</label>
        <button type="button" onclick="removeRegion(this)" class="remove-region">×</button>
    `;
    container.appendChild(newRow);
}

function removeRegion(button) {
    const regionRows = document.querySelectorAll('.region-row');
    if (regionRows.length > 1) {
        button.parentElement.remove();
    }
}

function validateGeoInputs() {
    const inputs = {
        globalTraffic: { value: parseFloat(document.getElementById('globalTraffic').value), min: 1, name: 'Global traffic' },
        targetLatency: { value: parseFloat(document.getElementById('targetLatency').value), min: 10, max: 5000, name: 'Target latency' },
        budgetConstraint: { value: parseFloat(document.getElementById('budgetConstraint').value), min: 1000, name: 'Budget constraint' }
    };
    
    const errors = [];
    
    / Validate numeric inputs
    for (const [key, input] of Object.entries(inputs)) {
        if (isNaN(input.value)) {
            errors.push(`${input.name} must be a number`);
        } else if (input.min !== undefined && input.max !== undefined && 
                   (input.value < input.min || input.value > input.max)) {
            errors.push(`${input.name} must be between ${input.min} and ${input.max}`);
        } else if (input.min !== undefined && input.value < input.min) {
            errors.push(`${input.name} must be at least ${input.min}`);
        }
    }
    
    / Validate traffic percentages
    const trafficPercentages = Array.from(document.querySelectorAll('.traffic-percentage'));
    const totalTraffic = trafficPercentages.reduce((sum, input) => {
        const value = parseFloat(input.value) || 0;
        return sum + value;
    }, 0);
    
    if (Math.abs(totalTraffic - 100) > 0.01) {
        errors.push(`Traffic percentages must sum to 100% (currently ${totalTraffic}%)`);
    }
    
    / Check for duplicate regions
    const selectedRegions = Array.from(document.querySelectorAll('.region-select')).map(select => select.value);
    const uniqueRegions = new Set(selectedRegions);
    if (selectedRegions.length !== uniqueRegions.size) {
        errors.push('Duplicate regions are not allowed');
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function calculateLatencyBetweenRegions(region1, region2) {
    const r1 = regionData[region1];
    const r2 = regionData[region2];
    
    if (!r1 || !r2) return 0;
    
    / Calculate great circle distance
    const toRad = (deg) => deg * (Math.PI / 180);
    const R = 6371; / Earth's radius in km
    
    const dLat = toRad(r2.lat - r1.lat);
    const dLng = toRad(r2.lng - r1.lng);
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(toRad(r1.lat)) * Math.cos(toRad(r2.lat)) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    const distance = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    
    / Base latency calculation (speed of light in fiber ~200,000 km/s)
    const baseLatency = (distance / 200000) * 1000 * 2; / Round trip in ms
    
    / Add processing overhead (10-50ms per hop)
    const processingOverhead = 25 + Math.random() * 25;
    
    return Math.round(baseLatency + processingOverhead);
}

function calculateGeoDistribution() {
    const validation = validateGeoInputs();
    if (!validation.valid) {
        displayGeoErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    
    / Collect region configuration
    const regionRows = document.querySelectorAll('.region-row');
    const regionConfig = [];
    
    regionRows.forEach(row => {
        const region = row.querySelector('.region-select').value;
        const traffic = parseFloat(row.querySelector('.traffic-percentage').value) || 0;
        regionConfig.push({ region, traffic, data: regionData[region] });
    });
    
    const cdnEnabled = document.getElementById('cdnEnabled').value;
    const targetLatency = inputs.targetLatency.value;
    const budgetConstraint = inputs.budgetConstraint.value;
    const globalTraffic = inputs.globalTraffic.value;
    
    / Calculate CDN impact
    let cdnLatencyReduction = 0;
    let cdnCostMultiplier = 1.0;
    
    switch(cdnEnabled) {
        case 'basic':
            cdnLatencyReduction = 30; / 30% reduction for static assets
            cdnCostMultiplier = 1.1;
            break;
        case 'dynamic':
            cdnLatencyReduction = 50; / 50% reduction with dynamic acceleration
            cdnCostMultiplier = 1.2;
            break;
        case 'edge-compute':
            cdnLatencyReduction = 70; / 70% reduction with edge computing
            cdnCostMultiplier = 1.4;
            break;
    }
    
    / Calculate costs and latencies for each region
    const analysis = regionConfig.map((config, index) => {
        const baseInstanceCost = 100; / Base cost per month
        const trafficCost = (globalTraffic * config.traffic / 100) * 0.01; / $0.01 per million requests
        
        const monthlyCost = (baseInstanceCost * config.data.cost + trafficCost) * cdnCostMultiplier;
        
        / Calculate average latency to other regions
        const interRegionLatencies = regionConfig.map((otherConfig, otherIndex) => {
            if (index === otherIndex) return 5; / Internal latency
            return calculateLatencyBetweenRegions(config.region, otherConfig.region);
        });
        
        const avgLatency = interRegionLatencies.reduce((sum, lat, idx) => 
            sum + lat * (regionConfig[idx].traffic / 100), 0
        );
        
        const effectiveLatency = avgLatency * (1 - cdnLatencyReduction / 100);
        
        return {
            ...config,
            monthlyCost,
            avgLatency,
            effectiveLatency,
            meetsTarget: effectiveLatency <= targetLatency
        };
    });
    
    const totalCost = analysis.reduce((sum, region) => sum + region.monthlyCost, 0);
    const withinBudget = totalCost <= budgetConstraint;
    
    / Generate compliance analysis
    const complianceChecks = {
        gdpr: document.getElementById('gdprCompliance').checked,
        ccpa: document.getElementById('ccpaCompliance').checked,
        pipdp: document.getElementById('pipdpCompliance').checked,
        lgpd: document.getElementById('lgpdCompliance').checked,
        pipeda: document.getElementById('pipedaCompliance').checked
    };
    
    let resultsHTML = generateGeoResults(analysis, totalCost, withinBudget, complianceChecks, targetLatency);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawDistributionChart(analysis);
        drawLatencyChart(analysis);
        drawCostChart(analysis);
    }, 100);
}

function generateGeoResults(analysis, totalCost, withinBudget, compliance, targetLatency) {
    const avgLatency = analysis.reduce((sum, region) => 
        sum + region.effectiveLatency * (region.traffic / 100), 0
    );
    
    const regionsCount = analysis.length;
    const regionsInTarget = analysis.filter(r => r.meetsTarget).length;
    
    return `
        <h3>🌍 Geographic Distribution Analysis</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                ${regionsCount} Regions
                <div style="font-size: 0.4em; margin-top: 10px;">
                    Average P95 Latency: ${avgLatency.toFixed(0)}ms
                </div>
            </div>
            <div class="cost-summary">
                <span class="cost-label">Monthly Cost:</span>
                <span class="cost-value ${withinBudget ? 'within-budget' : 'over-budget'}">
                    $${totalCost.toLocaleString()}
                </span>
                <span class="budget-status">
                    ${withinBudget ? '✅ Within budget' : '❌ Over budget'}
                </span>
            </div>
        </div>
        
        <h4>Regional Analysis</h4>
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Region</th>
                    <th>Traffic %</th>
                    <th>Latency (ms)</th>
                    <th>Monthly Cost</th>
                    <th>Target Met</th>
                </tr>
            </thead>
            <tbody>
                ${analysis.map(region => `
                    <tr class="${region.meetsTarget ? 'target-met' : 'target-missed'}">
                        <td data-label="Region">${region.data.name}</td>
                        <td data-label="Traffic %">${region.traffic}%</td>
                        <td data-label="Latency">${region.effectiveLatency.toFixed(0)}ms</td>
                        <td data-label="Monthly Cost">$${region.monthlyCost.toLocaleString()}</td>
                        <td data-label="Target Met">${region.meetsTarget ? '✅' : '❌'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Traffic Distribution</h4>
                <canvas id="distributionChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Latency Analysis</h4>
                <canvas id="latencyChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Cost Breakdown</h4>
                <canvas id="costChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <h4>📋 Compliance Summary</h4>
        <div class="compliance-grid">
            ${Object.entries(compliance).map(([key, enabled]) => 
                enabled ? `<div class="compliance-item enabled">✅ ${key.toUpperCase()}</div>` : 
                         `<div class="compliance-item disabled">❌ ${key.toUpperCase()}</div>`
            ).join('')}
        </div>
        
        <h4>💡 Recommendations</h4>
        <ul class="recommendations">
            ${generateRecommendations(analysis, totalCost, withinBudget, avgLatency, targetLatency)}
        </ul>
        
        <h4>🔍 What-If Scenarios</h4>
        <div class="scenario-buttons">
            <button onclick="runScenario('add-region')" class="scenario-btn">Add Region</button>
            <button onclick="runScenario('enable-cdn')" class="scenario-btn">Enable CDN</button>
            <button onclick="runScenario('optimize-cost')" class="scenario-btn">Optimize Cost</button>
            <button onclick="runScenario('peak-traffic')" class="scenario-btn">Peak Traffic</button>
        </div>
    `;
}

function generateRecommendations(analysis, totalCost, withinBudget, avgLatency, targetLatency) {
    const recommendations = [];
    
    if (!withinBudget) {
        recommendations.push('<li class="urgent">⚠️ Consider reducing regions or optimizing instance types to meet budget</li>');
    }
    
    if (avgLatency > targetLatency) {
        recommendations.push('<li class="urgent">⚠️ Enable CDN or add edge locations to meet latency targets</li>');
    }
    
    const underutilizedRegions = analysis.filter(r => r.traffic < 5);
    if (underutilizedRegions.length > 0) {
        recommendations.push('<li>Consider consolidating regions with less than 5% traffic</li>');
    }
    
    const highCostRegions = analysis.filter(r => r.data.cost > 1.2);
    if (highCostRegions.length > 0) {
        recommendations.push('<li>Monitor costs in premium regions: ' + 
                           highCostRegions.map(r => r.data.name).join(', ') + '</li>');
    }
    
    if (analysis.length < 3 && totalCost < withinBudget * 0.8) {
        recommendations.push('<li>Consider adding redundant regions for better availability</li>');
    }
    
    return recommendations.join('');
}

function displayGeoErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawDistributionChart(analysis) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: analysis.map(r => r.data.name.split('(')[0].trim()),
            datasets: [{
                data: analysis.map(r => r.traffic),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                    '#4BC0C0', '#36A2EB', '#FFCE56', '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.label}: ${context.parsed}%`
                    }
                }
            }
        }
    });
}

function drawLatencyChart(analysis) {
    const ctx = document.getElementById('latencyChart');
    if (!ctx) return;
    
    if (latencyChart) {
        latencyChart.destroy();
    }
    
    latencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: analysis.map(r => r.data.name.split('(')[0].trim()),
            datasets: [{
                label: 'Effective Latency (ms)',
                data: analysis.map(r => r.effectiveLatency),
                backgroundColor: analysis.map(r => r.meetsTarget ? '#51cf66' : '#ff6b6b'),
                borderColor: analysis.map(r => r.meetsTarget ? '#40c057' : '#e03131'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Latency (ms)'
                    }
                }
            }
        }
    });
}

function drawCostChart(analysis) {
    const ctx = document.getElementById('costChart');
    if (!ctx) return;
    
    if (costChart) {
        costChart.destroy();
    }
    
    costChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: analysis.map(r => r.data.name.split('(')[0].trim()),
            datasets: [{
                label: 'Monthly Cost ($)',
                data: analysis.map(r => r.monthlyCost),
                backgroundColor: '#36A2EB',
                borderColor: '#2E86AB',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Monthly Cost ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function runScenario(scenarioType) {
    / Implementation for what-if scenarios
    console.log('Running scenario:', scenarioType);
    / This would modify the inputs and recalculate
}

function exportResults() {
    const results = {
        timestamp: new Date().toISOString(),
        configuration: {
            globalTraffic: document.getElementById('globalTraffic').value,
            targetLatency: document.getElementById('targetLatency').value,
            budgetConstraint: document.getElementById('budgetConstraint').value,
            regions: Array.from(document.querySelectorAll('.region-row')).map(row => ({
                region: row.querySelector('.region-select').value,
                traffic: row.querySelector('.traffic-percentage').value
            }))
        },
        analysis: 'Results would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'geo-distribution-analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/ Initialize with default regions
document.addEventListener('DOMContentLoaded', function() {
    const defaultRegions = [
        { region: 'us-east-1', traffic: 30 },
        { region: 'eu-west-1', traffic: 25 },
        { region: 'ap-southeast-1', traffic: 45 }
    ];
    
    const container = document.getElementById('regionTraffic');
    const firstRow = container.querySelector('.region-row');
    
    / Update first row
    firstRow.querySelector('.region-select').value = defaultRegions[0].region;
    firstRow.querySelector('.traffic-percentage').value = defaultRegions[0].traffic;
    
    / Add additional rows
    for (let i = 1; i < defaultRegions.length; i++) {
        addRegion();
        const newRow = container.lastElementChild;
        newRow.querySelector('.region-select').value = defaultRegions[i].region;
        newRow.querySelector('.traffic-percentage').value = defaultRegions[i].traffic;
    }
});
</script>

<style>
.calculator-tool {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.region-config {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border: 1px solid #ddd;
}

.region-row {
    display: grid;
    grid-template-columns: 2fr 100px 1fr 30px;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 4px;
}

.region-select {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.traffic-percentage {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    text-align: center;
}

.remove-region {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 25px;
    height: 25px;
    cursor: pointer;
    font-weight: bold;
}

.add-region {
    background: #28a745;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
}

.compliance-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
    border-left: 4px solid #007bff;
}

.compliance-section label {
    display: block;
    margin: 8px 0;
}

.compliance-section input[type="checkbox"] {
    margin-right: 8px;
}

.calc-button, .export-button {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin: 10px 10px 10px 0;
}

.export-button {
    background: #28a745;
}

.calc-button:hover {
    background: #0056b3;
}

.export-button:hover {
    background: #1e7e34;
}

.results-panel {
    margin-top: 20px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.big-metric {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    margin-bottom: 20px;
}

.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    line-height: 1.2;
}

.cost-summary {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 10px;
    align-items: center;
    margin-top: 15px;
    font-size: 1.1em;
}

.cost-value.within-budget {
    color: #51cf66;
    font-weight: bold;
}

.cost-value.over-budget {
    color: #ff6b6b;
    font-weight: bold;
}

.target-met {
    background: #d4edda;
}

.target-missed {
    background: #f8d7da;
}

.charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.chart-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.compliance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
    margin: 15px 0;
}

.compliance-item {
    padding: 10px;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
}

.compliance-item.enabled {
    background: #d4edda;
    color: #155724;
}

.compliance-item.disabled {
    background: #f8d7da;
    color: #721c24;
}

.recommendations {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
}

.recommendations li.urgent {
    color: #e74c3c;
    font-weight: bold;
}

.scenario-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin: 15px 0;
}

.scenario-btn {
    background: #6c757d;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
}

.scenario-btn:hover {
    background: #5a6268;
}

.responsive-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

.responsive-table th,
.responsive-table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

.responsive-table th {
    background: #f8f9fa;
    font-weight: bold;
}

.error-panel {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 15px;
    border-radius: 4px;
    margin: 10px 0;
}

.strategy-card {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.strategy-card > div {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 10px;
    }
    
    .region-row {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    .cost-summary {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .scenario-buttons {
        grid-template-columns: 1fr 1fr;
    }
}
</style>

</div>