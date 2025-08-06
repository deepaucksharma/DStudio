---
title: Observability Cost Calculator
description: Metrics, logs, traces volume and cost estimation
type: documentation
---

# Observability Cost Calculator

!!! info "Advanced Observability Cost Analysis"
    <h2>📊 Observability Platform Cost Calculator</h2>
    <p>Estimate the cost and volume requirements for metrics, logs, traces, and alerts across your infrastructure.</p>

## Interactive Calculator

<div class="calculator-tool">
<form id="observabilityCalc">

### Infrastructure Scale

<label for="numServices">Number of services:</label>
<input type="number" id="numServices" value="50" min="1" step="1">
*Microservices and applications*

<label for="numInstances">Average instances per service:</label>
<input type="number" id="numInstances" value="3" min="1" step="1">
*Containers, VMs, or processes*

<label for="requestRate">Requests per second (total):</label>
<input type="number" id="requestRate" value="10000" min="1" step="100">
*Aggregate across all services*

<label for="environment">Environment type:</label>
<select id="environment">
<option value="development">Development (1x)</option>
<option value="staging">Staging (2x)</option>
<option value="production">Production (5x)</option>
<option value="enterprise">Enterprise (10x)</option>
</select>

### Metrics Configuration

<div class="metrics-section">
<h4>📈 Metrics Collection</h4>

<label for="metricsEnabled">Metrics collection:</label>
<select id="metricsEnabled">
<option value="basic">Basic (system metrics only)</option>
<option value="standard">Standard (system + application)</option>
<option value="detailed">Detailed (custom metrics)</option>
<option value="comprehensive">Comprehensive (high cardinality)</option>
</select>

<label for="metricsRetention">Metrics retention (days):</label>
<select id="metricsRetention">
<option value="7">7 days</option>
<option value="30">30 days</option>
<option value="90">90 days</option>
<option value="365">1 year</option>
<option value="1095">3 years</option>
</select>

<label for="metricsResolution">Metrics resolution:</label>
<select id="metricsResolution">
<option value="60">1 minute</option>
<option value="15">15 seconds</option>
<option value="5">5 seconds</option>
<option value="1">1 second</option>
</select>

<label for="customMetrics">Custom metrics per service:</label>
<input type="number" id="customMetrics" value="20" min="0" step="5">
*Application-specific metrics*
</div>

### Logging Configuration

<div class="logging-section">
<h4>📝 Log Management</h4>

<label for="logLevel">Default log level:</label>
<select id="logLevel">
<option value="error">ERROR (lowest volume)</option>
<option value="warn">WARN</option>
<option value="info">INFO</option>
<option value="debug">DEBUG (highest volume)</option>
</select>

<label for="logRetention">Log retention (days):</label>
<select id="logRetention">
<option value="7">7 days</option>
<option value="30">30 days</option>
<option value="90">90 days</option>
<option value="365">1 year</option>
<option value="2555">7 years (compliance)</option>
</select>

<label for="structuredLogging">Structured logging:</label>
<select id="structuredLogging">
<option value="none">Plain text</option>
<option value="json">JSON structured</option>
<option value="optimized">Optimized binary</option>
</select>

<label for="logSampling">Log sampling rate:</label>
<select id="logSampling">
<option value="1.0">100% (no sampling)</option>
<option value="0.5">50% sampling</option>
<option value="0.1">10% sampling</option>
<option value="0.01">1% sampling</option>
</select>

<div class="log-volume-config">
<h5>Log Volume Estimation</h5>
<label for="avgLogSize">Average log entry size (bytes):</label>
<input type="number" id="avgLogSize" value="512" min="50" step="50">

<label for="logsPerRequest">Log entries per request:</label>
<input type="number" id="logsPerRequest" value="5" min="1" step="1">
</div>
</div>

### Distributed Tracing

<div class="tracing-section">
<h4>🔍 Distributed Tracing</h4>

<label for="tracingEnabled">Tracing collection:</label>
<select id="tracingEnabled">
<option value="none">Disabled</option>
<option value="head">Head-based sampling</option>
<option value="tail">Tail-based sampling</option>
<option value="adaptive">Adaptive sampling</option>
</select>

<label for="tracingSampleRate">Base sampling rate:</label>
<select id="tracingSampleRate">
<option value="0.001">0.1% (errors only)</option>
<option value="0.01">1%</option>
<option value="0.05">5%</option>
<option value="0.1">10%</option>
<option value="1.0">100% (debug only)</option>
</select>

<label for="traceRetention">Trace retention (days):</label>
<select id="traceRetention">
<option value="1">1 day</option>
<option value="7">7 days</option>
<option value="30">30 days</option>
<option value="90">90 days</option>
</select>

<label for="avgSpansPerTrace">Average spans per trace:</label>
<input type="number" id="avgSpansPerTrace" value="15" min="1" step="1">
*Number of service calls per request*
</div>

### Alerting Configuration

<div class="alerting-section">
<h4>🚨 Alerting & Monitoring</h4>

<label for="alertRules">Number of alert rules:</label>
<input type="number" id="alertRules" value="100" min="1" step="5">
*Total alerting rules across all services*

<label for="alertEvaluationFreq">Alert evaluation frequency:</label>
<select id="alertEvaluationFreq">
<option value="300">5 minutes</option>
<option value="60">1 minute</option>
<option value="30">30 seconds</option>
<option value="10">10 seconds</option>
</select>

<label for="notificationChannels">Notification channels:</label>
<input type="number" id="notificationChannels" value="5" min="1" step="1">
*Slack, email, PagerDuty, etc.*
</div>

### Platform Selection

<div class="platform-section">
<h4>🛠️ Observability Platform</h4>

<label for="platform">Primary platform:</label>
<select id="platform">
<option value="datadog">Datadog</option>
<option value="newrelic">New Relic</option>
<option value="dynatrace">Dynatrace</option>
<option value="splunk">Splunk</option>
<option value="elastic">Elastic Stack</option>
<option value="grafana">Grafana Cloud</option>
<option value="prometheus">Prometheus + Grafana (self-hosted)</option>
<option value="jaeger">Jaeger + ELK (self-hosted)</option>
<option value="custom">Custom solution</option>
</select>

<label for="redundancy">Data redundancy:</label>
<select id="redundancy">
<option value="none">Single region</option>
<option value="backup">Backup region</option>
<option value="active">Multi-region active</option>
</select>
</div>

<button type="button" onclick="calculateObservabilityCost()" class="calc-button">Calculate Costs</button>
<button type="button" onclick="exportObservabilityResults()" class="export-button">Export Analysis</button>
<button type="button" onclick="generateOptimizationPlan()" class="optimize-button">Generate Optimization Plan</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Observability Costs

### Cost Components

**Metrics Costs:**
```
Cost = (Metrics Count × Resolution × Retention) × Platform Rate
```

**Logs Costs:**
```
Cost = (Log Volume GB × Retention Days) × Storage Rate + Ingestion Rate
```

**Traces Costs:**
```
Cost = (Trace Volume × Sample Rate × Retention) × Processing Rate
```

### Optimization Strategies

<div class="strategy-card">
<div>
<h4>📊 Metrics Optimization</h4>
<ul>
<li>Reduce high-cardinality metrics</li>
<li>Use recording rules for aggregations</li>
<li>Implement metric namespacing</li>
<li>Configure appropriate retention tiers</li>
</ul>
<p><strong>Savings:</strong> 30-60% reduction</p>
</div>

<div>
<h4>📝 Log Optimization</h4>
<ul>
<li>Implement sampling for non-critical logs</li>
<li>Use structured logging efficiently</li>
<li>Archive old logs to cold storage</li>
<li>Filter noise at source</li>
</ul>
<p><strong>Savings:</strong> 40-70% reduction</p>
</div>

<div>
<h4>🔍 Trace Optimization</h4>
<ul>
<li>Intelligent sampling strategies</li>
<li>Context-aware sampling</li>
<li>Error trace prioritization</li>
<li>Span filtering and aggregation</li>
</ul>
<p><strong>Savings:</strong> 50-80% reduction</p>
</div>

<div>
<h4>🚨 Alert Optimization</h4>
<ul>
<li>Consolidate related alerts</li>
<li>Use composite alerting</li>
<li>Optimize evaluation frequency</li>
<li>Implement alert fatigue prevention</li>
</ul>
<p><strong>Savings:</strong> 20-40% reduction</p>
</div>
</div>

### Platform Comparison

<table class="responsive-table">
<thead>
<tr>
<th>Platform</th>
<th>Metrics ($/month)</th>
<th>Logs ($/GB)</th>
<th>Traces ($/million)</th>
<th>Strengths</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Platform">Datadog</td>
<td data-label="Metrics">$15/host</td>
<td data-label="Logs">$1.70/GB</td>
<td data-label="Traces">$1.35/million</td>
<td data-label="Strengths">All-in-one, great UX</td>
</tr>
<tr>
<td data-label="Platform">New Relic</td>
<td data-label="Metrics">$0.25/100 GB</td>
<td data-label="Logs">$0.25/GB</td>
<td data-label="Traces">$0.25/million</td>
<td data-label="Strengths">Unified platform</td>
</tr>
<tr>
<td data-label="Platform">Grafana Cloud</td>
<td data-label="Metrics">$8/month base</td>
<td data-label="Logs">$0.50/GB</td>
<td data-label="Traces">$0.50/million</td>
<td data-label="Strengths">Open source, flexible</td>
</tr>
<tr>
<td data-label="Platform">Self-hosted</td>
<td data-label="Metrics">$2/month/host</td>
<td data-label="Logs">$0.10/GB</td>
<td data-label="Traces">$0.05/million</td>
<td data-label="Strengths">Full control, lowest cost</td>
</tr>
</tbody>
</table>

## Related Resources

- [Performance Optimization](../architects-handbook/implementation-playbooks/implementation-guides/performance-optimization.md)
- [Operational Excellence](../architects-handbook/implementation-playbooks/implementation-guides/operational-excellence.md)
- [Monitoring Patterns](../../pattern-library/resilience/monitoring.md)

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let costBreakdownChart = null;
let volumeChart = null;
let optimizationChart = null;

/ Platform pricing data (simplified)
const platformPricing = {
    datadog: {
        metrics: 15, / per host per month
        logs: 1.70, / per GB ingested
        traces: 1.35, / per million spans
        alerts: 5 / per rule per month
    },
    newrelic: {
        metrics: 0.0025, / per data point
        logs: 0.25,
        traces: 0.25,
        alerts: 0
    },
    dynatrace: {
        metrics: 21, / per host
        logs: 2.50,
        traces: 11, / per million PurePaths
        alerts: 0
    },
    splunk: {
        metrics: 150, / per GB/day
        logs: 2000, / per GB/day
        traces: 1.50,
        alerts: 0
    },
    elastic: {
        metrics: 95, / per deployment
        logs: 0.109, / per GB
        traces: 0.109,
        alerts: 0
    },
    grafana: {
        metrics: 8, / base + usage
        logs: 0.50,
        traces: 0.50,
        alerts: 0
    },
    prometheus: {
        metrics: 50, / infrastructure cost per month
        logs: 20, / ELK infrastructure
        traces: 15, / Jaeger infrastructure
        alerts: 0
    },
    jaeger: {
        metrics: 50,
        logs: 20,
        traces: 10,
        alerts: 0
    },
    custom: {
        metrics: 30,
        logs: 15,
        traces: 10,
        alerts: 5
    }
};

function validateObservabilityInputs() {
    const inputs = {
        numServices: { value: parseInt(document.getElementById('numServices').value), min: 1, name: 'Number of services' },
        numInstances: { value: parseInt(document.getElementById('numInstances').value), min: 1, name: 'Instances per service' },
        requestRate: { value: parseFloat(document.getElementById('requestRate').value), min: 1, name: 'Request rate' },
        customMetrics: { value: parseInt(document.getElementById('customMetrics').value), min: 0, name: 'Custom metrics' },
        avgLogSize: { value: parseInt(document.getElementById('avgLogSize').value), min: 50, name: 'Average log size' },
        logsPerRequest: { value: parseInt(document.getElementById('logsPerRequest').value), min: 1, name: 'Logs per request' },
        avgSpansPerTrace: { value: parseInt(document.getElementById('avgSpansPerTrace').value), min: 1, name: 'Spans per trace' },
        alertRules: { value: parseInt(document.getElementById('alertRules').value), min: 1, name: 'Alert rules' },
        notificationChannels: { value: parseInt(document.getElementById('notificationChannels').value), min: 1, name: 'Notification channels' }
    };
    
    const errors = [];
    
    for (const [key, input] of Object.entries(inputs)) {
        if (isNaN(input.value)) {
            errors.push(`${input.name} must be a number`);
        } else if (input.min !== undefined && input.value < input.min) {
            errors.push(`${input.name} must be at least ${input.min}`);
        }
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function calculateObservabilityCost() {
    const validation = validateObservabilityInputs();
    if (!validation.valid) {
        displayObservabilityErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    const platform = document.getElementById('platform').value;
    const pricing = platformPricing[platform];
    
    / Environment multiplier
    const envMultipliers = { development: 1, staging: 2, production: 5, enterprise: 10 };
    const envMultiplier = envMultipliers[document.getElementById('environment').value];
    
    / Calculate metrics costs
    const metricsConfig = calculateMetricsCosts(inputs, pricing, envMultiplier);
    
    / Calculate logs costs
    const logsConfig = calculateLogsCosts(inputs, pricing, envMultiplier);
    
    / Calculate traces costs
    const tracesConfig = calculateTracesCosts(inputs, pricing, envMultiplier);
    
    / Calculate alerting costs
    const alertingConfig = calculateAlertingCosts(inputs, pricing, envMultiplier);
    
    const totalCosts = {
        metrics: metricsConfig.monthlyCost,
        logs: logsConfig.monthlyCost,
        traces: tracesConfig.monthlyCost,
        alerts: alertingConfig.monthlyCost,
        total: metricsConfig.monthlyCost + logsConfig.monthlyCost + 
               tracesConfig.monthlyCost + alertingConfig.monthlyCost
    };
    
    const volumes = {
        metricsPoints: metricsConfig.pointsPerMonth,
        logVolumeGB: logsConfig.volumeGBPerMonth,
        traceSpans: tracesConfig.spansPerMonth,
        alertEvaluations: alertingConfig.evaluationsPerMonth
    };
    
    const redundancy = document.getElementById('redundancy').value;
    const redundancyMultiplier = redundancy === 'backup' ? 1.2 : redundancy === 'active' ? 2.0 : 1.0;
    
    / Apply redundancy costs
    Object.keys(totalCosts).forEach(key => {
        if (key !== 'total') totalCosts[key] *= redundancyMultiplier;
    });
    totalCosts.total = Object.values(totalCosts).slice(0, -1).reduce((sum, cost) => sum + cost, 0);
    
    / Generate optimization recommendations
    const optimizations = generateOptimizationRecommendations(volumes, totalCosts, platform);
    
    let resultsHTML = generateObservabilityResults(totalCosts, volumes, optimizations, platform, envMultiplier);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawCostBreakdownChart(totalCosts);
        drawVolumeChart(volumes);
        drawOptimizationChart(optimizations);
    }, 100);
}

function calculateMetricsCosts(inputs, pricing, envMultiplier) {
    const metricsEnabled = document.getElementById('metricsEnabled').value;
    const retention = parseInt(document.getElementById('metricsRetention').value);
    const resolution = parseInt(document.getElementById('metricsResolution').value);
    
    / Base metrics per host
    const baseMetricsMultipliers = { basic: 50, standard: 150, detailed: 300, comprehensive: 800 };
    const baseMetrics = baseMetricsMultipliers[metricsEnabled];
    
    const totalHosts = inputs.numServices.value * inputs.numInstances.value;
    const customMetrics = inputs.customMetrics.value * inputs.numServices.value;
    const totalMetrics = (baseMetrics * totalHosts + customMetrics) * envMultiplier;
    
    / Calculate data points per month
    const pointsPerSecond = totalMetrics / resolution;
    const pointsPerMonth = pointsPerSecond * 60 * 60 * 24 * 30;
    
    / Storage requirements
    const retentionMultiplier = Math.log(retention + 1) / Math.log(31); / Logarithmic cost scaling
    const storagePoints = pointsPerMonth * retentionMultiplier;
    
    / Platform-specific cost calculation
    let monthlyCost;
    if (pricing.metrics < 1) {
        / Per-datapoint pricing
        monthlyCost = storagePoints * pricing.metrics;
    } else if (pricing.metrics < 100) {
        / Per-host pricing
        monthlyCost = totalHosts * pricing.metrics;
    } else {
        / Per-GB pricing
        const sizeGB = storagePoints * 8 / (1024 * 1024 * 1024); / 8 bytes per point
        monthlyCost = sizeGB * pricing.metrics;
    }
    
    return {
        pointsPerMonth: Math.round(pointsPerMonth),
        monthlyCost: Math.round(monthlyCost),
        totalMetrics,
        retention
    };
}

function calculateLogsCosts(inputs, pricing, envMultiplier) {
    const logLevel = document.getElementById('logLevel').value;
    const retention = parseInt(document.getElementById('logRetention').value);
    const structuredLogging = document.getElementById('structuredLogging').value;
    const sampling = parseFloat(document.getElementById('logSampling').value);
    
    / Log volume multipliers by level
    const logLevelMultipliers = { error: 0.1, warn: 0.3, info: 1.0, debug: 3.0 };
    const levelMultiplier = logLevelMultipliers[logLevel];
    
    / Structured logging overhead
    const structuredMultipliers = { none: 1.0, json: 1.3, optimized: 1.1 };
    const structuredMultiplier = structuredMultipliers[structuredLogging];
    
    const dailyRequests = inputs.requestRate.value * 86400; / requests per day
    const logsPerDay = dailyRequests * inputs.logsPerRequest.value * levelMultiplier * envMultiplier;
    const sampledLogsPerDay = logsPerDay * sampling;
    
    const bytesPerDay = sampledLogsPerDay * inputs.avgLogSize.value * structuredMultiplier;
    const gbPerDay = bytesPerDay / (1024 * 1024 * 1024);
    const volumeGBPerMonth = gbPerDay * 30;
    
    / Storage cost with retention
    const retentionCostMultiplier = Math.min(retention / 30, 10); / Cap at 10x for very long retention
    const monthlyCost = volumeGBPerMonth * pricing.logs * retentionCostMultiplier;
    
    return {
        volumeGBPerMonth: Math.round(volumeGBPerMonth * 10) / 10,
        monthlyCost: Math.round(monthlyCost),
        logsPerDay: Math.round(sampledLogsPerDay),
        retention
    };
}

function calculateTracesCosts(inputs, pricing, envMultiplier) {
    const tracingEnabled = document.getElementById('tracingEnabled').value;
    
    if (tracingEnabled === 'none') {
        return { spansPerMonth: 0, monthlyCost: 0, tracesPerMonth: 0, retention: 0 };
    }
    
    const samplingRate = parseFloat(document.getElementById('tracingSampleRate').value);
    const retention = parseInt(document.getElementById('traceRetention').value);
    
    const dailyRequests = inputs.requestRate.value * 86400;
    const tracesPerDay = dailyRequests * samplingRate * envMultiplier;
    const spansPerDay = tracesPerDay * inputs.avgSpansPerTrace.value;
    const spansPerMonth = spansPerDay * 30;
    
    / Retention impact on cost
    const retentionMultiplier = Math.log(retention + 1) / Math.log(8); / Log scale for retention
    const monthlyCost = (spansPerMonth / 1000000) * pricing.traces * retentionMultiplier;
    
    return {
        spansPerMonth: Math.round(spansPerMonth),
        monthlyCost: Math.round(monthlyCost),
        tracesPerMonth: Math.round(tracesPerDay * 30),
        retention
    };
}

function calculateAlertingCosts(inputs, pricing, envMultiplier) {
    const evaluationFreq = parseInt(document.getElementById('alertEvaluationFreq').value);
    
    const evaluationsPerMonth = inputs.alertRules.value * (30 * 24 * 3600 / evaluationFreq) * envMultiplier;
    const monthlyCost = inputs.alertRules.value * pricing.alerts;
    
    return {
        evaluationsPerMonth: Math.round(evaluationsPerMonth),
        monthlyCost: Math.round(monthlyCost),
        alertRules: inputs.alertRules.value
    };
}

function generateOptimizationRecommendations(volumes, costs, platform) {
    const optimizations = [];
    
    / Metrics optimizations
    if (costs.metrics > costs.total * 0.4) {
        optimizations.push({
            type: 'metrics',
            title: 'Reduce high-cardinality metrics',
            description: 'Metrics account for a large portion of costs',
            savings: Math.round(costs.metrics * 0.3),
            effort: 'Medium'
        });
    }
    
    / Logs optimizations  
    if (costs.logs > costs.total * 0.5) {
        optimizations.push({
            type: 'logs',
            title: 'Implement intelligent log sampling',
            description: 'Log storage costs are very high',
            savings: Math.round(costs.logs * 0.5),
            effort: 'High'
        });
    }
    
    / Traces optimizations
    if (volumes.traceSpans > 1000000 && costs.traces > 1000) {
        optimizations.push({
            type: 'traces',
            title: 'Optimize trace sampling strategy',
            description: 'High trace volume detected',
            savings: Math.round(costs.traces * 0.6),
            effort: 'Medium'
        });
    }
    
    / Platform-specific optimizations
    if (['datadog', 'dynatrace', 'splunk'].includes(platform) && costs.total > 5000) {
        optimizations.push({
            type: 'platform',
            title: 'Consider open-source alternatives',
            description: 'Significant cost savings possible with self-hosted solutions',
            savings: Math.round(costs.total * 0.7),
            effort: 'Very High'
        });
    }
    
    return optimizations;
}

function generateObservabilityResults(costs, volumes, optimizations, platform, envMultiplier) {
    const costPercentages = {
        metrics: (costs.metrics / costs.total * 100).toFixed(1),
        logs: (costs.logs / costs.total * 100).toFixed(1),
        traces: (costs.traces / costs.total * 100).toFixed(1),
        alerts: (costs.alerts / costs.total * 100).toFixed(1)
    };
    
    return `
        <h3>📊 Observability Cost Analysis</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                $${costs.total.toLocaleString()}/month
                <div style="font-size: 0.4em; margin-top: 10px;">
                    Platform: ${platform.toUpperCase()} | Environment: ${document.getElementById('environment').value}
                </div>
            </div>
            
            <div class="cost-breakdown">
                <div class="cost-item">
                    <span class="cost-label">Metrics:</span>
                    <span class="cost-value">$${costs.metrics.toLocaleString()} (${costPercentages.metrics}%)</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label">Logs:</span>
                    <span class="cost-value">$${costs.logs.toLocaleString()} (${costPercentages.logs}%)</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label">Traces:</span>
                    <span class="cost-value">$${costs.traces.toLocaleString()} (${costPercentages.traces}%)</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label">Alerts:</span>
                    <span class="cost-value">$${costs.alerts.toLocaleString()} (${costPercentages.alerts}%)</span>
                </div>
            </div>
        </div>
        
        <h4>📈 Volume Analysis</h4>
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Telemetry Type</th>
                    <th>Volume/Month</th>
                    <th>Storage Requirements</th>
                    <th>Cost/Unit</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td data-label="Type">Metrics</td>
                    <td data-label="Volume">${volumes.metricsPoints.toLocaleString()} points</td>
                    <td data-label="Storage">${Math.round(volumes.metricsPoints * 8 / (1024*1024*1024))} GB</td>
                    <td data-label="Cost">${(costs.metrics / volumes.metricsPoints * 1000000).toFixed(4)}/million</td>
                </tr>
                <tr>
                    <td data-label="Type">Logs</td>
                    <td data-label="Volume">${volumes.logVolumeGB.toLocaleString()} GB</td>
                    <td data-label="Storage">${Math.round(volumes.logVolumeGB * parseInt(document.getElementById('logRetention').value) / 30)} GB</td>
                    <td data-label="Cost">${(costs.logs / volumes.logVolumeGB).toFixed(2)}/GB</td>
                </tr>
                <tr>
                    <td data-label="Type">Traces</td>
                    <td data-label="Volume">${volumes.traceSpans.toLocaleString()} spans</td>
                    <td data-label="Storage">${Math.round(volumes.traceSpans * 256 / (1024*1024*1024))} GB</td>
                    <td data-label="Cost">${(costs.traces / (volumes.traceSpans/1000000)).toFixed(2)}/million</td>
                </tr>
                <tr>
                    <td data-label="Type">Alerts</td>
                    <td data-label="Volume">${volumes.alertEvaluations.toLocaleString()} evaluations</td>
                    <td data-label="Storage">Negligible</td>
                    <td data-label="Cost">${(costs.alerts / (volumes.alertEvaluations/1000000)).toFixed(4)}/million</td>
                </tr>
            </tbody>
        </table>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Cost Breakdown</h4>
                <canvas id="costBreakdownChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Volume Distribution</h4>
                <canvas id="volumeChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Optimization Potential</h4>
                <canvas id="optimizationChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <h4>🚀 Optimization Recommendations</h4>
        <div class="optimization-grid">
            ${optimizations.map(opt => `
                <div class="optimization-card ${opt.type}">
                    <h5>${opt.title}</h5>
                    <p>${opt.description}</p>
                    <div class="optimization-metrics">
                        <span class="savings">Potential savings: $${opt.savings.toLocaleString()}/month</span>
                        <span class="effort">Effort: ${opt.effort}</span>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <h4>📊 Platform Comparison</h4>
        <div class="platform-comparison">
            ${generatePlatformComparison(volumes)}
        </div>
        
        <h4>📈 Growth Projections</h4>
        <div class="growth-analysis">
            <table class="responsive-table">
                <thead>
                    <tr>
                        <th>Growth Rate</th>
                        <th>6 Months</th>
                        <th>1 Year</th>
                        <th>2 Years</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td data-label="Growth">Conservative (20%/year)</td>
                        <td data-label="6 Months">$${Math.round(costs.total * 1.1).toLocaleString()}</td>
                        <td data-label="1 Year">$${Math.round(costs.total * 1.2).toLocaleString()}</td>
                        <td data-label="2 Years">$${Math.round(costs.total * 1.44).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <td data-label="Growth">Moderate (50%/year)</td>
                        <td data-label="6 Months">$${Math.round(costs.total * 1.22).toLocaleString()}</td>
                        <td data-label="1 Year">$${Math.round(costs.total * 1.5).toLocaleString()}</td>
                        <td data-label="2 Years">$${Math.round(costs.total * 2.25).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <td data-label="Growth">Aggressive (100%/year)</td>
                        <td data-label="6 Months">$${Math.round(costs.total * 1.41).toLocaleString()}</td>
                        <td data-label="1 Year">$${Math.round(costs.total * 2).toLocaleString()}</td>
                        <td data-label="2 Years">$${Math.round(costs.total * 4).toLocaleString()}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

function generatePlatformComparison(volumes) {
    const platforms = ['datadog', 'newrelic', 'grafana', 'prometheus'];
    const comparison = platforms.map(platform => {
        const pricing = platformPricing[platform];
        const estimatedCost = Math.round(
            (volumes.metricsPoints * 0.000001 * pricing.metrics) +
            (volumes.logVolumeGB * pricing.logs) +
            (volumes.traceSpans * 0.000001 * pricing.traces)
        );
        
        return { platform: platform.charAt(0).toUpperCase() + platform.slice(1), cost: estimatedCost };
    });
    
    return `
        <div class="platform-grid">
            ${comparison.map(p => `
                <div class="platform-card">
                    <h5>${p.platform}</h5>
                    <div class="platform-cost">$${p.cost.toLocaleString()}/month</div>
                </div>
            `).join('')}
        </div>
    `;
}

function displayObservabilityErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawCostBreakdownChart(costs) {
    const ctx = document.getElementById('costBreakdownChart');
    if (!ctx) return;
    
    if (costBreakdownChart) {
        costBreakdownChart.destroy();
    }
    
    costBreakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Metrics', 'Logs', 'Traces', 'Alerts'],
            datasets: [{
                data: [costs.metrics, costs.logs, costs.traces, costs.alerts],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
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
                        label: (context) => {
                            const percentage = ((context.parsed / costs.total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function drawVolumeChart(volumes) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
    if (volumeChart) {
        volumeChart.destroy();
    }
    
    / Normalize volumes for comparison
    const maxVolume = Math.max(volumes.metricsPoints, volumes.logVolumeGB * 1000, volumes.traceSpans);
    
    volumeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Metrics (points)', 'Logs (GB×1000)', 'Traces (spans)'],
            datasets: [{
                label: 'Monthly Volume',
                data: [volumes.metricsPoints, volumes.logVolumeGB * 1000, volumes.traceSpans],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                borderColor: ['#FF4757', '#2E86AB', '#F39C12'],
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
                        text: 'Volume'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function drawOptimizationChart(optimizations) {
    const ctx = document.getElementById('optimizationChart');
    if (!ctx) return;
    
    if (optimizationChart) {
        optimizationChart.destroy();
    }
    
    if (optimizations.length === 0) {
        ctx.getContext('2d').fillText('No optimizations identified', 10, 50);
        return;
    }
    
    optimizationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: optimizations.map(opt => opt.title.substring(0, 20) + '...'),
            datasets: [{
                label: 'Potential Monthly Savings ($)',
                data: optimizations.map(opt => opt.savings),
                backgroundColor: '#51cf66',
                borderColor: '#40c057',
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
                        text: 'Savings ($)'
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

function exportObservabilityResults() {
    const results = {
        timestamp: new Date().toISOString(),
        configuration: {
            numServices: document.getElementById('numServices').value,
            numInstances: document.getElementById('numInstances').value,
            requestRate: document.getElementById('requestRate').value,
            platform: document.getElementById('platform').value,
            environment: document.getElementById('environment').value
        },
        analysis: 'Full analysis would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'observability-cost-analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function generateOptimizationPlan() {
    alert('Optimization plan generation coming soon! This will create a detailed step-by-step plan for reducing observability costs.');
}
</script>

<style>
.calculator-tool {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.metrics-section,
.logging-section,
.tracing-section,
.alerting-section,
.platform-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border: 1px solid #ddd;
}

.log-volume-config {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
    border: 1px solid #e9ecef;
}

.calc-button, .export-button, .optimize-button {
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

.optimize-button {
    background: #ffc107;
    color: #212529;
}

.calc-button:hover {
    background: #0056b3;
}

.export-button:hover {
    background: #1e7e34;
}

.optimize-button:hover {
    background: #e0a800;
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

.cost-breakdown {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-top: 20px;
    font-size: 0.9em;
}

.cost-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.cost-label {
    font-weight: bold;
}

.cost-value {
    color: #ffd700;
    font-weight: bold;
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

.optimization-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.optimization-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.optimization-card.metrics {
    border-left-color: #FF6384;
}

.optimization-card.logs {
    border-left-color: #36A2EB;
}

.optimization-card.traces {
    border-left-color: #FFCE56;
}

.optimization-card.platform {
    border-left-color: #4BC0C0;
}

.optimization-metrics {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 0.9em;
}

.savings {
    color: #28a745;
    font-weight: bold;
}

.effort {
    color: #6c757d;
}

.platform-comparison {
    margin: 20px 0;
}

.platform-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.platform-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
    text-align: center;
}

.platform-cost {
    font-size: 1.5em;
    color: #007bff;
    font-weight: bold;
    margin-top: 10px;
}

.growth-analysis {
    margin: 20px 0;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
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
    
    .cost-breakdown {
        grid-template-columns: 1fr;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    .optimization-grid,
    .platform-grid {
        grid-template-columns: 1fr;
    }
    
    .optimization-metrics {
        flex-direction: column;
        gap: 5px;
    }
}
</style>

</div>