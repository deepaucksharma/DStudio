---
title: Database Sharding Calculator
description: Shard key selection, distribution analysis, and rebalancing cost estimation
type: documentation
---

# Database Sharding Calculator

!!! info "Advanced Database Sharding Analysis"
    <h2>🗃️ Database Sharding Strategy Calculator</h2>
    <p>Analyze shard key effectiveness, distribution patterns, hotspot detection, and rebalancing costs for horizontal database scaling.</p>

## Interactive Calculator

<div class="calculator-tool">
<form id="shardingCalc">

### Database Configuration

<label for="databaseType">Database type:</label>
<select id="databaseType">
<option value="mongodb">MongoDB</option>
<option value="postgresql">PostgreSQL</option>
<option value="mysql">MySQL</option>
<option value="cassandra">Apache Cassandra</option>
<option value="dynamodb">Amazon DynamoDB</option>
<option value="redis">Redis Cluster</option>
<option value="custom">Custom NoSQL</option>
</select>

<label for="totalDataSize">Total data size (GB):</label>
<input type="number" id="totalDataSize" value="1000" min="1" step="10">
*Current database size*

<label for="dailyGrowth">Daily growth rate (GB/day):</label>
<input type="number" id="dailyGrowth" value="10" min="0" step="0.5">
*Data growth per day*

<label for="readWriteRatio">Read/Write ratio:</label>
<select id="readWriteRatio">
<option value="read-heavy">Read Heavy (90/10)</option>
<option value="balanced">Balanced (70/30)</option>
<option value="write-heavy">Write Heavy (50/50)</option>
<option value="write-intensive">Write Intensive (30/70)</option>
</select>

### Sharding Strategy

<div class="sharding-config">
<h4>🔑 Shard Key Configuration</h4>

<label for="primaryShardKey">Primary shard key:</label>
<select id="primaryShardKey">
<option value="user_id">User ID (Hash-based)</option>
<option value="tenant_id">Tenant ID (Range-based)</option>
<option value="timestamp">Timestamp (Time-based)</option>
<option value="geographic">Geographic Region</option>
<option value="category">Category/Type</option>
<option value="composite">Composite Key</option>
<option value="custom">Custom Strategy</option>
</select>

<label for="shardKeyCardinality">Shard key cardinality:</label>
<select id="shardKeyCardinality">
<option value="low">Low (< 1K unique values)</option>
<option value="medium">Medium (1K - 100K values)</option>
<option value="high">High (100K - 10M values)</option>
<option value="very-high">Very High (> 10M values)</option>
</select>

<label for="distributionPattern">Data distribution pattern:</label>
<select id="distributionPattern">
<option value="uniform">Uniform distribution</option>
<option value="normal">Normal distribution</option>
<option value="skewed">Skewed (80/20 rule)</option>
<option value="temporal">Temporal clustering</option>
<option value="hotspot">Known hotspots</option>
</select>

<div id="compositeKeyConfig" style="display: none;">
<h5>Composite Key Components</h5>
<div id="keyComponents">
    <div class="key-component">
        <select class="component-field">
            <option value="user_id">User ID</option>
            <option value="timestamp">Timestamp</option>
            <option value="category">Category</option>
            <option value="region">Region</option>
        </select>
        <select class="component-weight">
            <option value="1">Primary (1st level)</option>
            <option value="2">Secondary (2nd level)</option>
            <option value="3">Tertiary (3rd level)</option>
        </select>
        <button type="button" onclick="removeKeyComponent(this)" class="remove-component">×</button>
    </div>
</div>
<button type="button" onclick="addKeyComponent()" class="add-component">+ Add Component</button>
</div>
</div>

### Cluster Configuration

<label for="numShards">Number of shards:</label>
<input type="number" id="numShards" value="16" min="2" max="1000" step="1">
*Current or planned shard count*

<label for="replicationFactor">Replication factor:</label>
<select id="replicationFactor">
<option value="1">No replication</option>
<option value="2">2x replication</option>
<option value="3">3x replication (recommended)</option>
<option value="5">5x replication (high availability)</option>
</select>

<label for="shardingMethod">Sharding method:</label>
<select id="shardingMethod">
<option value="hash">Hash-based sharding</option>
<option value="range">Range-based sharding</option>
<option value="directory">Directory-based sharding</option>
<option value="consistent">Consistent hashing</option>
</select>

### Performance Requirements

<label for="targetThroughput">Target throughput (ops/sec):</label>
<input type="number" id="targetThroughput" value="10000" min="100" step="100">
*Combined read + write operations*

<label for="latencyRequirement">Latency requirement:</label>
<select id="latencyRequirement">
<option value="relaxed">Relaxed (< 100ms)</option>
<option value="standard">Standard (< 50ms)</option>
<option value="strict">Strict (< 20ms)</option>
<option value="realtime">Real-time (< 5ms)</option>
</select>

<label for="consistencyModel">Consistency model:</label>
<select id="consistencyModel">
<option value="eventual">Eventual consistency</option>
<option value="strong">Strong consistency</option>
<option value="causal">Causal consistency</option>
<option value="session">Session consistency</option>
</select>

### Cost & Infrastructure

<label for="instanceType">Instance type per shard:</label>
<select id="instanceType">
<option value="small">Small (2 vCPU, 8GB RAM) - $100/month</option>
<option value="medium">Medium (4 vCPU, 16GB RAM) - $200/month</option>
<option value="large">Large (8 vCPU, 32GB RAM) - $400/month</option>
<option value="xlarge">X-Large (16 vCPU, 64GB RAM) - $800/month</option>
</select>

<label for="storageType">Storage type:</label>
<select id="storageType">
<option value="ssd">SSD (fast, $0.20/GB/month)</option>
<option value="nvme">NVMe (fastest, $0.40/GB/month)</option>
<option value="hdd">HDD (cheap, $0.05/GB/month)</option>
</select>

<button type="button" onclick="analyzeSharding()" class="calc-button">Analyze Sharding Strategy</button>
<button type="button" onclick="runDistributionSimulation()" class="simulation-button">Run Distribution Simulation</button>
<button type="button" onclick="exportShardingResults()" class="export-button">Export Analysis</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Database Sharding

### Sharding Strategies

**Hash-based Sharding:**
```
shard = hash(shard_key) % num_shards
```
- Pros: Even distribution, simple implementation
- Cons: Range queries across shards, fixed key space

**Range-based Sharding:**
```
if key >= range_start and key < range_end: shard_id
```
- Pros: Range queries efficient, natural partitioning
- Cons: Hotspots, uneven distribution

**Directory-based Sharding:**
```
shard = lookup_service.get_shard(shard_key)
```
- Pros: Flexible, supports resharding
- Cons: Additional complexity, lookup overhead

### Shard Key Selection Criteria

<div class="strategy-card">
<div>
<h4>📊 High Cardinality</h4>
<ul>
<li>Many unique values</li>
<li>Enables fine-grained distribution</li>
<li>Avoids single-shard bottlenecks</li>
<li>Example: user_id, order_id</li>
</ul>
<p><strong>Impact:</strong> Better distribution</p>
</div>

<div>
<h4>🎯 Query Efficiency</h4>
<ul>
<li>Used in most queries</li>
<li>Enables single-shard operations</li>
<li>Reduces cross-shard joins</li>
<li>Improves performance predictability</li>
</ul>
<p><strong>Impact:</strong> Faster queries</p>
</div>

<div>
<h4>⚡ Monotonic Growth</h4>
<ul>
<li>Avoid timestamp-only keys</li>
<li>Prevent write hotspots</li>
<li>Consider composite keys</li>
<li>Balance distribution over time</li>
</ul>
<p><strong>Impact:</strong> Sustainable performance</p>
</div>

<div>
<h4>🔄 Change Frequency</h4>
<ul>
<li>Immutable preferred</li>
<li>Avoid frequently changing keys</li>
<li>Consider update patterns</li>
<li>Plan for key evolution</li>
</ul>
<p><strong>Impact:</strong> Operational stability</p>
</div>
</div>

### Rebalancing Strategies

<table class="responsive-table">
<thead>
<tr>
<th>Strategy</th>
<th>Complexity</th>
<th>Downtime</th>
<th>Data Movement</th>
<th>Use Case</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Strategy">Split Shard</td>
<td data-label="Complexity">Medium</td>
<td data-label="Downtime">Low</td>
<td data-label="Data Movement">~50% of shard</td>
<td data-label="Use Case">Single shard hotspot</td>
</tr>
<tr>
<td data-label="Strategy">Move Shard</td>
<td data-label="Complexity">Low</td>
<td data-label="Downtime">Medium</td>
<td data-label="Data Movement">100% of shard</td>
<td data-label="Use Case">Hardware upgrade</td>
</tr>
<tr>
<td data-label="Strategy">Merge Shards</td>
<td data-label="Complexity">High</td>
<td data-label="Downtime">Medium</td>
<td data-label="Data Movement">100% of both</td>
<td data-label="Use Case">Under-utilized shards</td>
</tr>
<tr>
<td data-label="Strategy">Rehash All</td>
<td data-label="Complexity">Very High</td>
<td data-label="Downtime">High</td>
<td data-label="Data Movement">~75% of data</td>
<td data-label="Use Case">Major architecture change</td>
</tr>
</tbody>
</table>

## Related Resources

- [Consistency Calculator](consistency-calculator.md)
- [Throughput Calculator](throughput-calculator.md)
- [CAP Theorem](../../pattern-library/architecture/cap-theorem.md)
- [Data Distribution Patterns](../../pattern-library/data-management/sharding.md)

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let distributionChart = null;
let hotspotChart = null;
let costChart = null;
let simulationChart = null;

const databaseSpecs = {
    mongodb: { baseThroughput: 1000, latencyMultiplier: 1.0, costMultiplier: 1.0 },
    postgresql: { baseThroughput: 800, latencyMultiplier: 1.2, costMultiplier: 0.8 },
    mysql: { baseThroughput: 750, latencyMultiplier: 1.3, costMultiplier: 0.7 },
    cassandra: { baseThroughput: 2000, latencyMultiplier: 0.8, costMultiplier: 1.2 },
    dynamodb: { baseThroughput: 1500, latencyMultiplier: 0.9, costMultiplier: 1.5 },
    redis: { baseThroughput: 5000, latencyMultiplier: 0.3, costMultiplier: 2.0 },
    custom: { baseThroughput: 1000, latencyMultiplier: 1.0, costMultiplier: 1.0 }
};

const instanceCosts = {
    small: { cost: 100, vcpu: 2, ram: 8, throughput: 1000 },
    medium: { cost: 200, vcpu: 4, ram: 16, throughput: 2500 },
    large: { cost: 400, vcpu: 8, ram: 32, throughput: 5000 },
    xlarge: { cost: 800, vcpu: 16, ram: 64, throughput: 10000 }
};

const storageCosts = {
    ssd: { costPerGB: 0.20, iopsPerGB: 100, latencyMs: 5 },
    nvme: { costPerGB: 0.40, iopsPerGB: 300, latencyMs: 1 },
    hdd: { costPerGB: 0.05, iopsPerGB: 10, latencyMs: 20 }
};

/ Show/hide composite key config
document.getElementById('primaryShardKey').addEventListener('change', function() {
    const compositeConfig = document.getElementById('compositeKeyConfig');
    if (this.value === 'composite') {
        compositeConfig.style.display = 'block';
    } else {
        compositeConfig.style.display = 'none';
    }
});

function addKeyComponent() {
    const container = document.getElementById('keyComponents');
    const newComponent = document.createElement('div');
    newComponent.className = 'key-component';
    newComponent.innerHTML = `
        <select class="component-field">
            <option value="user_id">User ID</option>
            <option value="timestamp">Timestamp</option>
            <option value="category">Category</option>
            <option value="region">Region</option>
        </select>
        <select class="component-weight">
            <option value="1">Primary (1st level)</option>
            <option value="2">Secondary (2nd level)</option>
            <option value="3">Tertiary (3rd level)</option>
        </select>
        <button type="button" onclick="removeKeyComponent(this)" class="remove-component">×</button>
    `;
    container.appendChild(newComponent);
}

function removeKeyComponent(button) {
    const components = document.querySelectorAll('.key-component');
    if (components.length > 1) {
        button.parentElement.remove();
    }
}

function validateShardingInputs() {
    const inputs = {
        totalDataSize: { value: parseFloat(document.getElementById('totalDataSize').value), min: 1, name: 'Total data size' },
        dailyGrowth: { value: parseFloat(document.getElementById('dailyGrowth').value), min: 0, name: 'Daily growth' },
        numShards: { value: parseInt(document.getElementById('numShards').value), min: 2, max: 1000, name: 'Number of shards' },
        targetThroughput: { value: parseFloat(document.getElementById('targetThroughput').value), min: 100, name: 'Target throughput' }
    };
    
    const errors = [];
    
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
    
    return { valid: errors.length === 0, errors, inputs };
}

function analyzeSharding() {
    const validation = validateShardingInputs();
    if (!validation.valid) {
        displayShardingErrors(validation.errors);
        return;
    }
    
    const inputs = validation.inputs;
    const config = getShardingConfiguration();
    
    / Calculate shard distribution
    const distribution = calculateShardDistribution(inputs, config);
    
    / Analyze hotspots
    const hotspotAnalysis = analyzeHotspots(distribution, config);
    
    / Calculate costs
    const costAnalysis = calculateShardingCosts(inputs, config);
    
    / Performance analysis
    const performanceAnalysis = analyzePerformance(inputs, config, distribution);
    
    / Rebalancing analysis
    const rebalancingAnalysis = analyzeRebalancing(distribution, inputs, config);
    
    / Generate results
    const results = {
        distribution,
        hotspots: hotspotAnalysis,
        costs: costAnalysis,
        performance: performanceAnalysis,
        rebalancing: rebalancingAnalysis
    };
    
    let resultsHTML = generateShardingResults(results, config);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawDistributionChart(distribution);
        drawHotspotChart(hotspotAnalysis);
        drawCostChart(costAnalysis);
    }, 100);
}

function getShardingConfiguration() {
    return {
        databaseType: document.getElementById('databaseType').value,
        primaryShardKey: document.getElementById('primaryShardKey').value,
        shardKeyCardinality: document.getElementById('shardKeyCardinality').value,
        distributionPattern: document.getElementById('distributionPattern').value,
        numShards: parseInt(document.getElementById('numShards').value),
        replicationFactor: parseInt(document.getElementById('replicationFactor').value),
        shardingMethod: document.getElementById('shardingMethod').value,
        instanceType: document.getElementById('instanceType').value,
        storageType: document.getElementById('storageType').value,
        readWriteRatio: document.getElementById('readWriteRatio').value,
        latencyRequirement: document.getElementById('latencyRequirement').value,
        consistencyModel: document.getElementById('consistencyModel').value
    };
}

function calculateShardDistribution(inputs, config) {
    const numShards = config.numShards;
    const totalData = inputs.totalDataSize.value;
    const distributionPattern = config.distributionPattern;
    
    let distribution = [];
    
    switch (distributionPattern) {
        case 'uniform':
            / Even distribution
            const evenSize = totalData / numShards;
            for (let i = 0; i < numShards; i++) {
                distribution.push({
                    shardId: i,
                    dataSize: evenSize * (0.9 + Math.random() * 0.2), / ±10% variance
                    requestRate: inputs.targetThroughput.value / numShards,
                    hotspotRisk: 'low'
                });
            }
            break;
            
        case 'normal':
            / Normal distribution with center bias
            for (let i = 0; i < numShards; i++) {
                const position = (i + 0.5) / numShards;
                const normalFactor = Math.exp(-Math.pow((position - 0.5) * 3, 2)) + 0.3;
                distribution.push({
                    shardId: i,
                    dataSize: (totalData / numShards) * normalFactor,
                    requestRate: (inputs.targetThroughput.value / numShards) * normalFactor,
                    hotspotRisk: normalFactor > 1.2 ? 'high' : normalFactor > 1.0 ? 'medium' : 'low'
                });
            }
            break;
            
        case 'skewed':
            / 80/20 distribution (Pareto)
            const sizes = [];
            for (let i = 0; i < numShards; i++) {
                sizes.push(Math.pow(Math.random(), 3)); / Skewed random
            }
            const totalWeight = sizes.reduce((sum, size) => sum + size, 0);
            
            for (let i = 0; i < numShards; i++) {
                const proportion = sizes[i] / totalWeight;
                distribution.push({
                    shardId: i,
                    dataSize: totalData * proportion,
                    requestRate: inputs.targetThroughput.value * proportion,
                    hotspotRisk: proportion > 0.2 ? 'high' : proportion > 0.1 ? 'medium' : 'low'
                });
            }
            break;
            
        case 'temporal':
            / Recent data gets more traffic
            for (let i = 0; i < numShards; i++) {
                const recency = Math.max(0, 1 - (i / numShards)); / Newer shards get more
                const temporalFactor = 0.3 + recency * 2;
                distribution.push({
                    shardId: i,
                    dataSize: (totalData / numShards) * (0.8 + recency * 0.4),
                    requestRate: (inputs.targetThroughput.value / numShards) * temporalFactor,
                    hotspotRisk: temporalFactor > 1.5 ? 'high' : 'medium'
                });
            }
            break;
            
        case 'hotspot':
            / Known hotspots (first few shards)
            for (let i = 0; i < numShards; i++) {
                const hotspotFactor = i < 3 ? 3 : 0.5; / First 3 shards are hotspots
                distribution.push({
                    shardId: i,
                    dataSize: (totalData / numShards) * (0.5 + hotspotFactor * 0.5),
                    requestRate: (inputs.targetThroughput.value / numShards) * hotspotFactor,
                    hotspotRisk: i < 3 ? 'critical' : 'low'
                });
            }
            break;
    }
    
    return distribution;
}

function analyzeHotspots(distribution, config) {
    const avgRequestRate = distribution.reduce((sum, shard) => sum + shard.requestRate, 0) / distribution.length;
    const threshold = avgRequestRate * 1.5; / 50% above average
    
    const hotspots = distribution.filter(shard => shard.requestRate > threshold);
    const severityLevels = { critical: 0, high: 0, medium: 0, low: 0 };
    
    distribution.forEach(shard => {
        if (shard.hotspotRisk in severityLevels) {
            severityLevels[shard.hotspotRisk]++;
        }
    });
    
    const recommendations = [];
    if (hotspots.length > 0) {
        recommendations.push(`${hotspots.length} shards identified as hotspots`);
        recommendations.push('Consider splitting hotspot shards');
    }
    
    if (severityLevels.critical > 0) {
        recommendations.push('Critical hotspots require immediate attention');
    }
    
    return {
        hotspots,
        severity: severityLevels,
        recommendations,
        imbalanceRatio: Math.max(...distribution.map(s => s.requestRate)) / Math.min(...distribution.map(s => s.requestRate))
    };
}

function calculateShardingCosts(inputs, config) {
    const instance = instanceCosts[config.instanceType];
    const storage = storageCosts[config.storageType];
    const numShards = config.numShards;
    const replicationFactor = config.replicationFactor;
    
    / Instance costs
    const instanceCostPerShard = instance.cost;
    const totalInstanceCosts = instanceCostPerShard * numShards * replicationFactor;
    
    / Storage costs
    const dataPerShard = inputs.totalDataSize.value / numShards;
    const storageCostPerShard = dataPerShard * storage.costPerGB;
    const totalStorageCosts = storageCostPerShard * numShards * replicationFactor;
    
    / Network costs (cross-shard communication)
    const crossShardTraffic = inputs.targetThroughput.value * 0.2; / 20% cross-shard
    const networkCosts = crossShardTraffic * 0.001 * 24 * 30; / $0.001 per 1000 requests
    
    / Operational costs
    const operationalCosts = (totalInstanceCosts + totalStorageCosts) * 0.15; / 15% overhead
    
    const monthlyCosts = {
        instances: totalInstanceCosts,
        storage: totalStorageCosts,
        network: networkCosts,
        operational: operationalCosts,
        total: totalInstanceCosts + totalStorageCosts + networkCosts + operationalCosts
    };
    
    / Growth projections
    const growthProjections = calculateGrowthCosts(inputs, config, monthlyCosts);
    
    return {
        monthly: monthlyCosts,
        growth: growthProjections,
        costPerShard: monthlyCosts.total / numShards,
        costPerGB: monthlyCosts.total / inputs.totalDataSize.value
    };
}

function calculateGrowthCosts(inputs, config, baseCosts) {
    const dailyGrowth = inputs.dailyGrowth.value;
    const monthlyGrowth = dailyGrowth * 30;
    const yearlyGrowth = monthlyGrowth * 12;
    
    const projections = [];
    const timeframes = [6, 12, 24]; / months
    
    timeframes.forEach(months => {
        const totalGrowth = monthlyGrowth * months;
        const newTotalSize = inputs.totalDataSize.value + totalGrowth;
        const growthRatio = newTotalSize / inputs.totalDataSize.value;
        
        / Assume linear scaling for storage, some efficiency for instances
        const instanceScaling = Math.pow(growthRatio, 0.8); / Economies of scale
        const storageScaling = growthRatio;
        
        const projectedCosts = {
            instances: baseCosts.instances * instanceScaling,
            storage: baseCosts.storage * storageScaling,
            network: baseCosts.network * growthRatio,
            operational: baseCosts.operational * Math.sqrt(growthRatio),
            total: 0
        };
        
        projectedCosts.total = Object.values(projectedCosts).slice(0, -1).reduce((sum, cost) => sum + cost, 0);
        
        projections.push({
            months,
            dataSize: newTotalSize,
            costs: projectedCosts,
            recommendedShards: Math.ceil(config.numShards * Math.sqrt(growthRatio))
        });
    });
    
    return projections;
}

function analyzePerformance(inputs, config, distribution) {
    const dbSpec = databaseSpecs[config.databaseType];
    const instance = instanceCosts[config.instanceType];
    const storage = storageCosts[config.storageType];
    
    / Calculate per-shard throughput capacity
    const baseCapacity = Math.min(instance.throughput, storage.iopsPerGB * 100); / Assume 100GB avg per shard
    const actualCapacity = baseCapacity * dbSpec.baseThroughput / 1000;
    
    / Latency analysis
    const baseLatency = storage.latencyMs * dbSpec.latencyMultiplier;
    const consistencyOverhead = config.consistencyModel === 'strong' ? 10 : 
                               config.consistencyModel === 'causal' ? 5 : 0;
    const replicationLatency = config.replicationFactor > 1 ? 
                              (config.replicationFactor - 1) * 2 : 0;
    
    const totalLatency = baseLatency + consistencyOverhead + replicationLatency;
    
    / Identify performance bottlenecks
    const bottlenecks = [];
    const maxRequestRate = Math.max(...distribution.map(s => s.requestRate));
    
    if (maxRequestRate > actualCapacity) {
        bottlenecks.push('Hotspot shards exceed instance capacity');
    }
    
    if (totalLatency > getLatencyTarget(config.latencyRequirement)) {
        bottlenecks.push('Latency exceeds requirements');
    }
    
    const crossShardQueries = calculateCrossShardQueries(config);
    if (crossShardQueries > 20) {
        bottlenecks.push('High cross-shard query percentage');
    }
    
    return {
        perShardCapacity: Math.round(actualCapacity),
        estimatedLatency: Math.round(totalLatency),
        maxUtilization: Math.round((maxRequestRate / actualCapacity) * 100),
        crossShardQueries: crossShardQueries,
        bottlenecks,
        recommendations: generatePerformanceRecommendations(bottlenecks, config)
    };
}

function getLatencyTarget(requirement) {
    const targets = {
        relaxed: 100,
        standard: 50,
        strict: 20,
        realtime: 5
    };
    return targets[requirement] || 50;
}

function calculateCrossShardQueries(config) {
    / Simplified estimation based on shard key choice
    const crossShardRates = {
        user_id: 5,      / Most queries by user
        tenant_id: 10,   / Some cross-tenant queries
        timestamp: 30,   / Many range queries
        geographic: 15,  / Some region-spanning queries
        category: 25,    / Cross-category queries common
        composite: 8,    / Well-designed composite keys
        custom: 15       / Unknown, assume moderate
    };
    
    return crossShardRates[config.primaryShardKey] || 15;
}

function analyzeRebalancing(distribution, inputs, config) {
    const imbalanceThreshold = 1.5;
    const currentImbalance = Math.max(...distribution.map(s => s.dataSize)) / 
                            Math.min(...distribution.map(s => s.dataSize));
    
    const needsRebalancing = currentImbalance > imbalanceThreshold;
    
    if (!needsRebalancing) {
        return {
            needed: false,
            strategy: null,
            cost: 0,
            downtime: 0,
            dataMovement: 0
        };
    }
    
    / Determine best rebalancing strategy
    const strategies = [
        {
            name: 'Split Hotspots',
            cost: 5000,
            downtime: 30, / minutes
            dataMovement: distribution.reduce((sum, s) => sum + s.dataSize, 0) * 0.1,
            complexity: 'medium'
        },
        {
            name: 'Add Shards',
            cost: 10000,
            downtime: 120,
            dataMovement: inputs.totalDataSize.value * 0.3,
            complexity: 'high'
        },
        {
            name: 'Full Resharding',
            cost: 25000,
            downtime: 480,
            dataMovement: inputs.totalDataSize.value * 0.8,
            complexity: 'very high'
        }
    ];
    
    const recommendedStrategy = strategies[0]; / Simplified selection
    
    return {
        needed: true,
        currentImbalance,
        recommendedStrategy,
        alternatives: strategies.slice(1),
        estimatedTimeline: calculateRebalancingTimeline(recommendedStrategy, inputs.totalDataSize.value)
    };
}

function calculateRebalancingTimeline(strategy, totalDataSize) {
    const migrationRate = 100; / GB per hour
    const migrationHours = strategy.dataMovement / migrationRate;
    
    return {
        preparation: '1-2 weeks',
        migration: `${Math.ceil(migrationHours)} hours`,
        validation: '2-3 days',
        total: `${Math.ceil(migrationHours / 24) + 14} days`
    };
}

function generatePerformanceRecommendations(bottlenecks, config) {
    const recommendations = [];
    
    bottlenecks.forEach(bottleneck => {
        switch (bottleneck) {
            case 'Hotspot shards exceed instance capacity':
                recommendations.push('Scale up instance types for hotspot shards');
                recommendations.push('Consider shard splitting or load redistribution');
                break;
            case 'Latency exceeds requirements':
                recommendations.push('Upgrade to faster storage (NVMe)');
                recommendations.push('Optimize read replicas placement');
                break;
            case 'High cross-shard query percentage':
                recommendations.push('Reconsider shard key strategy');
                recommendations.push('Implement query result caching');
                break;
        }
    });
    
    return recommendations;
}

function generateShardingResults(results, config) {
    const { distribution, hotspots, costs, performance, rebalancing } = results;
    
    return `
        <h3>🗃️ Database Sharding Analysis</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                ${config.numShards} Shards
                <div style="font-size: 0.4em; margin-top: 10px;">
                    ${config.databaseType.toUpperCase()} | ${config.shardingMethod} sharding
                </div>
            </div>
            <div class="performance-summary">
                <div class="perf-item">
                    <span class="perf-label">Est. Latency:</span>
                    <span class="perf-value ${performance.estimatedLatency <= getLatencyTarget(config.latencyRequirement) ? 'good' : 'warning'}">
                        ${performance.estimatedLatency}ms
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Max Utilization:</span>
                    <span class="perf-value ${performance.maxUtilization <= 80 ? 'good' : 'warning'}">
                        ${performance.maxUtilization}%
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Monthly Cost:</span>
                    <span class="perf-value">$${costs.monthly.total.toLocaleString()}</span>
                </div>
            </div>
        </div>
        
        <div class="analysis-grid">
            <div class="analysis-card">
                <h4>📊 Distribution Analysis</h4>
                <div class="metric-row">
                    <span>Imbalance Ratio:</span>
                    <span class="${hotspots.imbalanceRatio <= 2 ? 'good' : hotspots.imbalanceRatio <= 5 ? 'warning' : 'critical'}">
                        ${hotspots.imbalanceRatio.toFixed(2)}:1
                    </span>
                </div>
                <div class="metric-row">
                    <span>Hotspot Shards:</span>
                    <span class="${hotspots.hotspots.length === 0 ? 'good' : 'warning'}">
                        ${hotspots.hotspots.length}
                    </span>
                </div>
                <div class="metric-row">
                    <span>Cross-shard Queries:</span>
                    <span class="${performance.crossShardQueries <= 15 ? 'good' : 'warning'}">
                        ${performance.crossShardQueries}%
                    </span>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>💰 Cost Analysis</h4>
                <div class="cost-breakdown-mini">
                    <div class="cost-row">
                        <span>Instances:</span>
                        <span>$${costs.monthly.instances.toLocaleString()}</span>
                    </div>
                    <div class="cost-row">
                        <span>Storage:</span>
                        <span>$${costs.monthly.storage.toLocaleString()}</span>
                    </div>
                    <div class="cost-row">
                        <span>Network:</span>
                        <span>$${Math.round(costs.monthly.network).toLocaleString()}</span>
                    </div>
                    <div class="cost-row total">
                        <span>Total:</span>
                        <span>$${costs.monthly.total.toLocaleString()}</span>
                    </div>
                </div>
                <p class="cost-efficiency">
                    $${costs.costPerGB.toFixed(2)}/GB | $${Math.round(costs.costPerShard).toLocaleString()}/shard
                </p>
            </div>
            
            <div class="analysis-card">
                <h4>🔄 Rebalancing Status</h4>
                ${rebalancing.needed ? `
                    <div class="rebalancing-needed">
                        <p class="status warning">⚠️ Rebalancing recommended</p>
                        <p><strong>Strategy:</strong> ${rebalancing.recommendedStrategy.name}</p>
                        <p><strong>Est. Cost:</strong> $${rebalancing.recommendedStrategy.cost.toLocaleString()}</p>
                        <p><strong>Downtime:</strong> ${rebalancing.recommendedStrategy.downtime} minutes</p>
                    </div>
                ` : `
                    <div class="rebalancing-good">
                        <p class="status good">✅ Well balanced</p>
                        <p>No immediate rebalancing needed</p>
                    </div>
                `}
            </div>
        </div>
        
        <h4>📈 Shard Distribution</h4>
        <div class="charts-container">
            <div class="chart-section">
                <canvas id="distributionChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <h4>🔥 Hotspot Analysis</h4>
        <div class="charts-container">
            <div class="chart-section">
                <canvas id="hotspotChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <h4>💰 Cost Projections</h4>
        <div class="charts-container">
            <div class="chart-section">
                <canvas id="costChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <h4>🎯 Performance Bottlenecks</h4>
        <div class="bottleneck-analysis">
            ${performance.bottlenecks.length > 0 ? 
                performance.bottlenecks.map(bottleneck => `<div class="bottleneck-item">⚠️ ${bottleneck}</div>`).join('') :
                '<div class="no-bottlenecks">✅ No significant bottlenecks identified</div>'
            }
        </div>
        
        <h4>💡 Recommendations</h4>
        <div class="recommendations-grid">
            ${generateShardingRecommendations(results, config)}
        </div>
        
        <h4>📊 Growth Planning</h4>
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Timeframe</th>
                    <th>Data Size</th>
                    <th>Monthly Cost</th>
                    <th>Recommended Shards</th>
                </tr>
            </thead>
            <tbody>
                ${costs.growth.map(projection => `
                    <tr>
                        <td data-label="Timeframe">${projection.months} months</td>
                        <td data-label="Data Size">${Math.round(projection.dataSize)} GB</td>
                        <td data-label="Monthly Cost">$${projection.costs.total.toLocaleString()}</td>
                        <td data-label="Recommended Shards">${projection.recommendedShards}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generateShardingRecommendations(results, config) {
    const recommendations = [];
    const { hotspots, performance, costs, rebalancing } = results;
    
    if (hotspots.hotspots.length > 0) {
        recommendations.push({
            type: 'performance',
            title: 'Address Hotspot Shards',
            description: `${hotspots.hotspots.length} shards are handling disproportionate load`,
            priority: 'high',
            actions: ['Consider shard splitting', 'Review shard key strategy', 'Add read replicas']
        });
    }
    
    if (performance.maxUtilization > 85) {
        recommendations.push({
            type: 'capacity',
            title: 'Scale Instance Capacity',
            description: 'Some shards are approaching capacity limits',
            priority: 'medium',
            actions: ['Upgrade instance types', 'Add horizontal scaling', 'Optimize queries']
        });
    }
    
    if (costs.costPerGB > 1.0) {
        recommendations.push({
            type: 'cost',
            title: 'Optimize Storage Costs',
            description: 'Storage costs are higher than typical',
            priority: 'low',
            actions: ['Consider different storage tiers', 'Implement data archiving', 'Review replication factor']
        });
    }
    
    if (performance.crossShardQueries > 25) {
        recommendations.push({
            type: 'architecture',
            title: 'Reduce Cross-Shard Queries',
            description: 'High percentage of queries span multiple shards',
            priority: 'high',
            actions: ['Redesign shard key', 'Add denormalization', 'Implement caching layer']
        });
    }
    
    return recommendations.map(rec => `
        <div class="recommendation-card ${rec.type}">
            <div class="rec-header">
                <h5>${rec.title}</h5>
                <span class="priority ${rec.priority}">${rec.priority.toUpperCase()}</span>
            </div>
            <p>${rec.description}</p>
            <ul class="action-list">
                ${rec.actions.map(action => `<li>${action}</li>`).join('')}
            </ul>
        </div>
    `).join('');
}

function displayShardingErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawDistributionChart(distribution) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: distribution.map(s => `Shard ${s.shardId}`),
            datasets: [
                {
                    label: 'Data Size (GB)',
                    data: distribution.map(s => Math.round(s.dataSize)),
                    backgroundColor: '#36A2EB',
                    yAxisID: 'y'
                },
                {
                    label: 'Request Rate (ops/sec)',
                    data: distribution.map(s => Math.round(s.requestRate)),
                    backgroundColor: '#FF6384',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Shard ID'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Data Size (GB)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Request Rate (ops/sec)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function drawHotspotChart(hotspotAnalysis) {
    const ctx = document.getElementById('hotspotChart');
    if (!ctx) return;
    
    if (hotspotChart) {
        hotspotChart.destroy();
    }
    
    const severityData = hotspotAnalysis.severity;
    
    hotspotChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [severityData.critical, severityData.high, severityData.medium, severityData.low],
                backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Hotspot Risk Distribution'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function drawCostChart(costAnalysis) {
    const ctx = document.getElementById('costChart');
    if (!ctx) return;
    
    if (costChart) {
        costChart.destroy();
    }
    
    const growthData = costAnalysis.growth;
    
    costChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Current', ...growthData.map(p => `${p.months} months`)],
            datasets: [{
                label: 'Monthly Cost ($)',
                data: [costAnalysis.monthly.total, ...growthData.map(p => p.costs.total)],
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Cost Growth Projection'
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

function runDistributionSimulation() {
    / Placeholder for advanced simulation
    alert('Distribution simulation will analyze various shard key strategies and their impact on data distribution patterns.');
}

function exportShardingResults() {
    const results = {
        timestamp: new Date().toISOString(),
        configuration: getShardingConfiguration(),
        analysis: 'Detailed analysis results would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sharding-analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
</script>

<style>
.calculator-tool {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.sharding-config {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border: 1px solid #ddd;
}

.key-component {
    display: grid;
    grid-template-columns: 2fr 1fr 30px;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 4px;
}

.component-field,
.component-weight {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.remove-component {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 25px;
    height: 25px;
    cursor: pointer;
    font-weight: bold;
}

.add-component {
    background: #28a745;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
}

.calc-button, .simulation-button, .export-button {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin: 10px 10px 10px 0;
}

.simulation-button {
    background: #6f42c1;
}

.export-button {
    background: #28a745;
}

.calc-button:hover {
    background: #0056b3;
}

.simulation-button:hover {
    background: #5a2d91;
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

.performance-summary {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
    font-size: 0.9em;
}

.perf-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.perf-label {
    font-size: 0.8em;
    opacity: 0.9;
}

.perf-value {
    font-weight: bold;
    font-size: 1.2em;
    margin-top: 4px;
}

.perf-value.good {
    color: #51cf66;
}

.perf-value.warning {
    color: #ffd43b;
}

.analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.analysis-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.cost-breakdown-mini {
    font-size: 0.9em;
}

.cost-row {
    display: flex;
    justify-content: space-between;
    margin: 5px 0;
    padding: 5px 0;
}

.cost-row.total {
    border-top: 2px solid #007bff;
    font-weight: bold;
    margin-top: 10px;
    padding-top: 10px;
}

.cost-efficiency {
    text-align: center;
    margin-top: 10px;
    color: #6c757d;
    font-size: 0.8em;
}

.rebalancing-needed .status.warning {
    color: #e74c3c;
    font-weight: bold;
}

.rebalancing-good .status.good {
    color: #27ae60;
    font-weight: bold;
}

.good {
    color: #28a745;
    font-weight: bold;
}

.warning {
    color: #ffc107;
    font-weight: bold;
}

.critical {
    color: #dc3545;
    font-weight: bold;
}

.charts-container {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
    margin: 20px 0;
}

.chart-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.bottleneck-analysis {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
}

.bottleneck-item {
    color: #856404;
    margin: 5px 0;
    font-weight: bold;
}

.no-bottlenecks {
    color: #155724;
    font-weight: bold;
    text-align: center;
}

.recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.recommendation-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #007bff;
}

.recommendation-card.performance {
    border-left-color: #e74c3c;
}

.recommendation-card.capacity {
    border-left-color: #f39c12;
}

.recommendation-card.cost {
    border-left-color: #2ecc71;
}

.recommendation-card.architecture {
    border-left-color: #9b59b6;
}

.rec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.priority {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: bold;
}

.priority.high {
    background: #ffebee;
    color: #c62828;
}

.priority.medium {
    background: #fff8e1;
    color: #ef6c00;
}

.priority.low {
    background: #e8f5e8;
    color: #2e7d32;
}

.action-list {
    margin-top: 10px;
    padding-left: 20px;
}

.action-list li {
    margin: 5px 0;
    color: #555;
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
    
    .performance-summary {
        grid-template-columns: 1fr;
    }
    
    .analysis-grid {
        grid-template-columns: 1fr;
    }
    
    .key-component {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .rec-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
}
</style>

</div>