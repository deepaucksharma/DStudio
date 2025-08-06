---
title: Cache Hierarchy Optimizer
description: Multi-level cache optimization, hit ratio analysis, and performance tuning
type: documentation
---

# Cache Hierarchy Optimizer

!!! info "Advanced Cache Optimization Analysis"
    <h2>🗄️ Multi-Level Cache Hierarchy Optimizer</h2>
    <p>Optimize cache hierarchies with hit ratio analysis, eviction policy comparison, and multi-tier performance modeling.</p>

## Interactive Optimizer

<div class="calculator-tool">
<form id="cacheOptimizerCalc">

### Application Profile

<label for="applicationPattern">Application access pattern:</label>
<select id="applicationPattern">
<option value="web-app">Web Application (temporal locality)</option>
<option value="api-service">API Service (mixed patterns)</option>
<option value="data-analytics">Data Analytics (sequential)</option>
<option value="gaming">Gaming (hot-cold data)</option>
<option value="e-commerce">E-commerce (seasonal patterns)</option>
<option value="cdn">CDN (geographic locality)</option>
<option value="database">Database (range queries)</option>
<option value="custom">Custom Pattern</option>
</select>

<label for="requestRate">Requests per second:</label>
<input type="number" id="requestRate" value="10000" min="1" step="100">
*Peak request rate*

<label for="dataSetSize">Total dataset size (GB):</label>
<input type="number" id="dataSetSize" value="1000" min="1" step="10">
*Size of complete working set*

<label for="workingSetSize">Working set size (GB):</label>
<input type="number" id="workingSetSize" value="100" min="1" step="5">
*Frequently accessed data size*

<label for="keyDistribution">Key access distribution:</label>
<select id="keyDistribution">
<option value="uniform">Uniform (all keys equally likely)</option>
<option value="zipfian">Zipfian (80/20 rule)</option>
<option value="normal">Normal (bell curve)</option>
<option value="bimodal">Bimodal (hot and cold)</option>
<option value="temporal">Temporal clustering</option>
<option value="seasonal">Seasonal patterns</option>
</select>

### Cache Hierarchy Configuration

<div class="cache-levels">
<h4>🏗️ Cache Tier Configuration</h4>

<div id="cacheTiers">
<div class="cache-tier" data-tier="1">
    <h5>L1 Cache (CPU/Memory)</h5>
    <div class="tier-config">
        <label>Size (MB):</label>
        <input type="number" class="cache-size" value="512" min="1" step="1">
        
        <label>Latency (μs):</label>
        <input type="number" class="cache-latency" value="0.1" min="0.001" step="0.001">
        
        <label>Eviction Policy:</label>
        <select class="eviction-policy">
            <option value="lru">LRU (Least Recently Used)</option>
            <option value="lfu">LFU (Least Frequently Used)</option>
            <option value="fifo">FIFO (First In First Out)</option>
            <option value="random">Random</option>
            <option value="arc">ARC (Adaptive Replacement)</option>
            <option value="lirs">LIRS (Low Inter-reference Recency)</option>
        </select>
        
        <label>Technology:</label>
        <select class="cache-technology">
            <option value="cpu-cache">CPU Cache</option>
            <option value="memory">In-Memory (HashMap)</option>
            <option value="off-heap">Off-Heap Memory</option>
        </select>
        
        <button type="button" onclick="removeCacheTier(this)" class="remove-tier">Remove Tier</button>
    </div>
</div>

<div class="cache-tier" data-tier="2">
    <h5>L2 Cache (Local)</h5>
    <div class="tier-config">
        <label>Size (GB):</label>
        <input type="number" class="cache-size" value="8" min="0.1" step="0.1">
        
        <label>Latency (ms):</label>
        <input type="number" class="cache-latency" value="0.5" min="0.001" step="0.001">
        
        <label>Eviction Policy:</label>
        <select class="eviction-policy">
            <option value="lru" selected>LRU (Least Recently Used)</option>
            <option value="lfu">LFU (Least Frequently Used)</option>
            <option value="fifo">FIFO (First In First Out)</option>
            <option value="random">Random</option>
            <option value="arc">ARC (Adaptive Replacement)</option>
            <option value="lirs">LIRS (Low Inter-reference Recency)</option>
        </select>
        
        <label>Technology:</label>
        <select class="cache-technology">
            <option value="memory" selected>In-Memory (HashMap)</option>
            <option value="off-heap">Off-Heap Memory</option>
            <option value="ssd">SSD Cache</option>
            <option value="nvme">NVMe Storage</option>
        </select>
        
        <button type="button" onclick="removeCacheTier(this)" class="remove-tier">Remove Tier</button>
    </div>
</div>
</div>

<button type="button" onclick="addCacheTier()" class="add-tier">+ Add Cache Tier</button>
</div>

### Data Characteristics

<label for="averageObjectSize">Average object size (KB):</label>
<input type="number" id="averageObjectSize" value="4" min="0.1" step="0.1">
*Average size of cached objects*

<label for="objectSizeVariation">Object size variation:</label>
<select id="objectSizeVariation">
<option value="uniform">Uniform (consistent size)</option>
<option value="normal">Normal distribution</option>
<option value="power-law">Power law (few large objects)</option>
<option value="bimodal">Bimodal (small and large)</option>
</select>

<label for="readWriteRatio">Read/Write ratio:</label>
<select id="readWriteRatio">
<option value="read-heavy">Read Heavy (90/10)</option>
<option value="read-mostly">Read Mostly (80/20)</option>
<option value="balanced">Balanced (70/30)</option>
<option value="write-heavy">Write Heavy (60/40)</option>
<option value="write-intensive">Write Intensive (50/50)</option>
</select>

<label for="dataVolatility">Data volatility:</label>
<select id="dataVolatility">
<option value="static">Static (rarely changes)</option>
<option value="low">Low volatility (hourly changes)</option>
<option value="medium">Medium volatility (minute changes)</option>
<option value="high">High volatility (second changes)</option>
<option value="real-time">Real-time (continuous)</option>
</select>

### Performance Requirements

<label for="targetLatency">Target P99 latency (ms):</label>
<input type="number" id="targetLatency" value="10" min="0.1" step="0.1">
*99th percentile latency requirement*

<label for="targetHitRatio">Target overall hit ratio (%):</label>
<input type="number" id="targetHitRatio" value="95" min="50" max="99.9" step="0.1">
*Combined hit ratio across all tiers*

<label for="consistencyModel">Cache consistency:</label>
<select id="consistencyModel">
<option value="eventual">Eventual consistency</option>
<option value="strong">Strong consistency</option>
<option value="session">Session consistency</option>
<option value="weak">Weak consistency</option>
</select>

### Cost Constraints

<label for="memoryBudget">Memory budget ($/month):</label>
<input type="number" id="memoryBudget" value="5000" min="100" step="100">
*Monthly cost constraint for memory*

<label for="storageBudget">Storage budget ($/month):</label>
<input type="number" id="storageBudget" value="2000" min="50" step="50">
*Monthly cost constraint for storage*

<label for="networkBudget">Network budget ($/month):</label>
<input type="number" id="networkBudget" value="1000" min="50" step="50">
*Monthly cost for cache coherence traffic*

<button type="button" onclick="optimizeCacheHierarchy()" class="calc-button">Optimize Cache Hierarchy</button>
<button type="button" onclick="simulateCachePerformance()" class="simulation-button">Run Cache Simulation</button>
<button type="button" onclick="compareEvictionPolicies()" class="compare-button">Compare Eviction Policies</button>
<button type="button" onclick="exportCacheResults()" class="export-button">Export Analysis</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Cache Hierarchies

### Multi-Level Cache Benefits

<div class="benefit-grid">
<div class="benefit-card">
<h4>⚡ Latency Reduction</h4>
<ul>
<li>L1: 0.1μs (CPU cache)</li>
<li>L2: 0.5ms (Memory)</li>
<li>L3: 5ms (SSD)</li>
<li>Database: 50ms+ (Network + Disk)</li>
</ul>
<p><strong>Impact:</strong> 500x improvement with cache hits</p>
</div>

<div class="benefit-card">
<h4>🎯 Hit Ratio Multiplication</h4>
<ul>
<li>L1 Hit: 70% × Fast access</li>
<li>L2 Hit: 20% × Medium access</li>
<li>L3 Hit: 8% × Slow access</li>
<li>Miss: 2% × Database access</li>
</ul>
<p><strong>Result:</strong> 98% cache hit ratio</p>
</div>

<div class="benefit-card">
<h4>💰 Cost Efficiency</h4>
<ul>
<li>Memory: $1/GB/month</li>
<li>SSD: $0.20/GB/month</li>
<li>HDD: $0.05/GB/month</li>
<li>Network: Reduced bandwidth</li>
</ul>
<p><strong>Savings:</strong> 80% cost reduction</p>
</div>

<div class="benefit-card">
<h4>🔄 Load Distribution</h4>
<ul>
<li>Database load reduction</li>
<li>Network traffic optimization</li>
<li>CPU utilization balance</li>
<li>Memory pressure management</li>
</ul>
<p><strong>Benefit:</strong> Better scalability</p>
</div>
</div>

### Eviction Policy Comparison

<table class="responsive-table">
<thead>
<tr>
<th>Policy</th>
<th>Temporal Locality</th>
<th>Scan Resistance</th>
<th>Implementation</th>
<th>Memory Overhead</th>
<th>Best Use Case</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Policy">LRU</td>
<td data-label="Temporal Locality">Excellent</td>
<td data-label="Scan Resistance">Poor</td>
<td data-label="Implementation">Medium</td>
<td data-label="Memory Overhead">O(n)</td>
<td data-label="Best Use Case">General purpose</td>
</tr>
<tr>
<td data-label="Policy">LFU</td>
<td data-label="Temporal Locality">Good</td>
<td data-label="Scan Resistance">Excellent</td>
<td data-label="Implementation">Complex</td>
<td data-label="Memory Overhead">O(n)</td>
<td data-label="Best Use Case">Stable access patterns</td>
</tr>
<tr>
<td data-label="Policy">ARC</td>
<td data-label="Temporal Locality">Excellent</td>
<td data-label="Scan Resistance">Good</td>
<td data-label="Implementation">Complex</td>
<td data-label="Memory Overhead">O(n)</td>
<td data-label="Best Use Case">Adaptive workloads</td>
</tr>
<tr>
<td data-label="Policy">LIRS</td>
<td data-label="Temporal Locality">Excellent</td>
<td data-label="Scan Resistance">Excellent</td>
<td data-label="Implementation">Very Complex</td>
<td data-label="Memory Overhead">O(n)</td>
<td data-label="Best Use Case">Mixed workloads</td>
</tr>
<tr>
<td data-label="Policy">FIFO</td>
<td data-label="Temporal Locality">Poor</td>
<td data-label="Scan Resistance">Good</td>
<td data-label="Implementation">Simple</td>
<td data-label="Memory Overhead">O(1)</td>
<td data-label="Best Use Case">Sequential access</td>
</tr>
<tr>
<td data-label="Policy">Random</td>
<td data-label="Temporal Locality">Poor</td>
<td data-label="Scan Resistance">Good</td>
<td data-label="Implementation">Simple</td>
<td data-label="Memory Overhead">O(1)</td>
<td data-label="Best Use Case">Uniform access</td>
</tr>
</tbody>
</table>

### Cache Coherence Strategies

<div class="strategy-card">
<div>
<h4>🔄 Write-Through</h4>
<ul>
<li>Write to cache and storage simultaneously</li>
<li>Strong consistency guarantee</li>
<li>Higher write latency</li>
<li>Simple implementation</li>
</ul>
<p><strong>Use case:</strong> Strong consistency required</p>
</div>

<div>
<h4>⚡ Write-Back</h4>
<ul>
<li>Write to cache, lazy write to storage</li>
<li>Lower write latency</li>
<li>Risk of data loss</li>
<li>Complex implementation</li>
</ul>
<p><strong>Use case:</strong> Performance critical</p>
</div>

<div>
<h4>🕳️ Write-Around</h4>
<ul>
<li>Write directly to storage</li>
<li>Avoids cache pollution</li>
<li>Cache miss on immediate read</li>
<li>Good for write-heavy workloads</li>
</ul>
<p><strong>Use case:</strong> Infrequent re-reads</p>
</div>

<div>
<h4>📝 Write-Allocate</h4>
<ul>
<li>Load on cache miss during write</li>
<li>Better for temporal locality</li>
<li>Higher initial latency</li>
<li>Benefits subsequent reads</li>
</ul>
<p><strong>Use case:</strong> Read-after-write patterns</p>
</div>
</div>

## Related Resources

- [Throughput Calculator](throughput-calculator.md)
- [Latency Calculator](latency-calculator.md)
- [Caching Strategies](../../pattern-library/scaling/caching-strategies.md)
- [Performance Optimization](../architects-handbook/implementation-playbooks/implementation-guides/performance-optimization.md)

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let hierarchyChart = null;
let hitRatioChart = null;
let latencyChart = null;
let costChart = null;

/ Cache technology specifications
const cacheTechnologies = {
    'cpu-cache': { costPerGB: 10000, latency: 0.001, bandwidth: 1000000 },
    'memory': { costPerGB: 30, latency: 0.1, bandwidth: 100000 },
    'off-heap': { costPerGB: 25, latency: 0.2, bandwidth: 80000 },
    'ssd': { costPerGB: 0.2, latency: 1, bandwidth: 5000 },
    'nvme': { costPerGB: 0.5, latency: 0.1, bandwidth: 15000 },
    'network-cache': { costPerGB: 50, latency: 2, bandwidth: 10000 }
};

/ Eviction policy characteristics
const evictionPolicies = {
    'lru': { 
        name: 'LRU',
        temporalScore: 90,
        scanResistance: 30,
        complexity: 'Medium',
        overhead: 'O(n)'
    },
    'lfu': { 
        name: 'LFU',
        temporalScore: 75,
        scanResistance: 95,
        complexity: 'High',
        overhead: 'O(n)'
    },
    'arc': { 
        name: 'ARC',
        temporalScore: 95,
        scanResistance: 80,
        complexity: 'High',
        overhead: 'O(n)'
    },
    'lirs': { 
        name: 'LIRS',
        temporalScore: 95,
        scanResistance: 90,
        complexity: 'Very High',
        overhead: 'O(n)'
    },
    'fifo': { 
        name: 'FIFO',
        temporalScore: 40,
        scanResistance: 75,
        complexity: 'Low',
        overhead: 'O(1)'
    },
    'random': { 
        name: 'Random',
        temporalScore: 50,
        scanResistance: 85,
        complexity: 'Low',
        overhead: 'O(1)'
    }
};

/ Application pattern characteristics
const applicationPatterns = {
    'web-app': { temporalWeight: 0.8, spatialWeight: 0.3, zipfAlpha: 0.8 },
    'api-service': { temporalWeight: 0.6, spatialWeight: 0.4, zipfAlpha: 1.0 },
    'data-analytics': { temporalWeight: 0.2, spatialWeight: 0.9, zipfAlpha: 0.5 },
    'gaming': { temporalWeight: 0.7, spatialWeight: 0.2, zipfAlpha: 1.2 },
    'e-commerce': { temporalWeight: 0.6, spatialWeight: 0.3, zipfAlpha: 1.1 },
    'cdn': { temporalWeight: 0.4, spatialWeight: 0.8, zipfAlpha: 0.9 },
    'database': { temporalWeight: 0.5, spatialWeight: 0.7, zipfAlpha: 0.7 }
};

let tierCounter = 3;

function addCacheTier() {
    const container = document.getElementById('cacheTiers');
    const newTier = document.createElement('div');
    newTier.className = 'cache-tier';
    newTier.setAttribute('data-tier', tierCounter);
    
    newTier.innerHTML = `
        <h5>L${tierCounter} Cache (Custom)</h5>
        <div class="tier-config">
            <label>Size (GB):</label>
            <input type="number" class="cache-size" value="50" min="0.1" step="0.1">
            
            <label>Latency (ms):</label>
            <input type="number" class="cache-latency" value="10" min="0.001" step="0.001">
            
            <label>Eviction Policy:</label>
            <select class="eviction-policy">
                <option value="lru">LRU (Least Recently Used)</option>
                <option value="lfu">LFU (Least Frequently Used)</option>
                <option value="fifo">FIFO (First In First Out)</option>
                <option value="random">Random</option>
                <option value="arc">ARC (Adaptive Replacement)</option>
                <option value="lirs">LIRS (Low Inter-reference Recency)</option>
            </select>
            
            <label>Technology:</label>
            <select class="cache-technology">
                <option value="memory">In-Memory (HashMap)</option>
                <option value="off-heap">Off-Heap Memory</option>
                <option value="ssd">SSD Cache</option>
                <option value="nvme">NVMe Storage</option>
                <option value="network-cache">Network Cache</option>
            </select>
            
            <button type="button" onclick="removeCacheTier(this)" class="remove-tier">Remove Tier</button>
        </div>
    `;
    
    container.appendChild(newTier);
    tierCounter++;
}

function removeCacheTier(button) {
    const tiers = document.querySelectorAll('.cache-tier');
    if (tiers.length > 1) {
        button.closest('.cache-tier').remove();
    }
}

function validateCacheInputs() {
    const inputs = {
        requestRate: { value: parseFloat(document.getElementById('requestRate').value), min: 1, name: 'Request rate' },
        dataSetSize: { value: parseFloat(document.getElementById('dataSetSize').value), min: 1, name: 'Dataset size' },
        workingSetSize: { value: parseFloat(document.getElementById('workingSetSize').value), min: 1, name: 'Working set size' },
        averageObjectSize: { value: parseFloat(document.getElementById('averageObjectSize').value), min: 0.1, name: 'Average object size' },
        targetLatency: { value: parseFloat(document.getElementById('targetLatency').value), min: 0.1, name: 'Target latency' },
        targetHitRatio: { value: parseFloat(document.getElementById('targetHitRatio').value), min: 50, max: 99.9, name: 'Target hit ratio' },
        memoryBudget: { value: parseFloat(document.getElementById('memoryBudget').value), min: 100, name: 'Memory budget' }
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
    
    / Validate working set vs dataset size
    if (inputs.workingSetSize.value > inputs.dataSetSize.value) {
        errors.push('Working set size cannot exceed dataset size');
    }
    
    / Validate cache tier configurations
    const cacheTiers = document.querySelectorAll('.cache-tier');
    cacheTiers.forEach((tier, index) => {
        const size = parseFloat(tier.querySelector('.cache-size').value);
        const latency = parseFloat(tier.querySelector('.cache-latency').value);
        
        if (isNaN(size) || size <= 0) {
            errors.push(`Cache tier ${index + 1}: Size must be a positive number`);
        }
        
        if (isNaN(latency) || latency <= 0) {
            errors.push(`Cache tier ${index + 1}: Latency must be a positive number`);
        }
    });
    
    return { valid: errors.length === 0, errors, inputs };
}

function optimizeCacheHierarchy() {
    const validation = validateCacheInputs();
    if (!validation.valid) {
        displayCacheErrors(validation.errors);
        return;
    }
    
    const config = getCacheConfiguration();
    const accessPattern = analyzeAccessPattern(config);
    const hierarchyAnalysis = analyzeCurrentHierarchy(config, accessPattern);
    const optimizations = generateOptimizations(config, hierarchyAnalysis);
    const costAnalysis = analyzeCacheCosts(config, hierarchyAnalysis);
    const recommendations = generateCacheRecommendations(config, hierarchyAnalysis, costAnalysis);
    
    const results = {
        config,
        accessPattern,
        hierarchy: hierarchyAnalysis,
        optimizations,
        costs: costAnalysis,
        recommendations
    };
    
    let resultsHTML = generateCacheResults(results);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawHierarchyChart(hierarchyAnalysis);
        drawHitRatioChart(hierarchyAnalysis);
        drawLatencyChart(hierarchyAnalysis);
        drawCostChart(costAnalysis);
    }, 100);
}

function getCacheConfiguration() {
    const cacheTiers = [];
    document.querySelectorAll('.cache-tier').forEach((tier, index) => {
        const sizeInput = tier.querySelector('.cache-size');
        const latencyInput = tier.querySelector('.cache-latency');
        const size = parseFloat(sizeInput.value);
        
        / Convert size based on tier level (L1 in MB, others in GB)
        const sizeInGB = index === 0 ? size / 1024 : size;
        
        cacheTiers.push({
            level: index + 1,
            size: sizeInGB,
            latency: parseFloat(latencyInput.value),
            evictionPolicy: tier.querySelector('.eviction-policy').value,
            technology: tier.querySelector('.cache-technology').value
        });
    });
    
    return {
        applicationPattern: document.getElementById('applicationPattern').value,
        requestRate: parseFloat(document.getElementById('requestRate').value),
        dataSetSize: parseFloat(document.getElementById('dataSetSize').value),
        workingSetSize: parseFloat(document.getElementById('workingSetSize').value),
        keyDistribution: document.getElementById('keyDistribution').value,
        averageObjectSize: parseFloat(document.getElementById('averageObjectSize').value),
        objectSizeVariation: document.getElementById('objectSizeVariation').value,
        readWriteRatio: document.getElementById('readWriteRatio').value,
        dataVolatility: document.getElementById('dataVolatility').value,
        targetLatency: parseFloat(document.getElementById('targetLatency').value),
        targetHitRatio: parseFloat(document.getElementById('targetHitRatio').value),
        consistencyModel: document.getElementById('consistencyModel').value,
        memoryBudget: parseFloat(document.getElementById('memoryBudget').value),
        storageBudget: parseFloat(document.getElementById('storageBudget').value),
        networkBudget: parseFloat(document.getElementById('networkBudget').value),
        cacheTiers
    };
}

function analyzeAccessPattern(config) {
    const pattern = applicationPatterns[config.applicationPattern] || applicationPatterns['api-service'];
    
    / Calculate locality characteristics
    const temporalLocality = pattern.temporalWeight * 100;
    const spatialLocality = pattern.spatialWeight * 100;
    const zipfianParameter = pattern.zipfAlpha;
    
    / Estimate working set characteristics
    const workingSetRatio = config.workingSetSize / config.dataSetSize;
    const estimatedUniqueObjects = config.workingSetSize * 1024 * 1024 / (config.averageObjectSize * 1024); / Convert to objects
    
    return {
        temporalLocality,
        spatialLocality,
        zipfianParameter,
        workingSetRatio,
        estimatedUniqueObjects,
        accessFrequency: config.requestRate
    };
}

function analyzeCurrentHierarchy(config, accessPattern) {
    const tiers = config.cacheTiers;
    const analysis = [];
    let cumulativeHitRatio = 0;
    let cumulativeMissRatio = 1;
    
    tiers.forEach((tier, index) => {
        / Calculate individual tier hit ratio
        const tierCapacityRatio = tier.size / config.workingSetSize;
        const evictionPolicy = evictionPolicies[tier.evictionPolicy];
        
        / Base hit ratio calculation using cache size and access pattern
        let baseHitRatio = calculateTierHitRatio(tierCapacityRatio, accessPattern, config.keyDistribution);
        
        / Apply eviction policy effectiveness
        const policyMultiplier = calculatePolicyEffectiveness(evictionPolicy, accessPattern);
        baseHitRatio *= policyMultiplier;
        
        / Consider remaining miss ratio from previous tiers
        const effectiveHitRatio = Math.min(baseHitRatio * cumulativeMissRatio, cumulativeMissRatio);
        
        cumulativeHitRatio += effectiveHitRatio;
        cumulativeMissRatio -= effectiveHitRatio;
        
        / Calculate performance metrics
        const avgLatency = calculateAverageLatency(tier, cacheTechnologies[tier.technology]);
        const throughput = calculateTierThroughput(tier, cacheTechnologies[tier.technology], config.requestRate);
        
        analysis.push({
            tier: tier.level,
            size: tier.size,
            technology: tier.technology,
            evictionPolicy: tier.evictionPolicy,
            hitRatio: effectiveHitRatio * 100,
            cumulativeHitRatio: cumulativeHitRatio * 100,
            avgLatency,
            throughput,
            requestsServed: effectiveHitRatio * config.requestRate
        });
    });
    
    / Calculate overall metrics
    const overallHitRatio = cumulativeHitRatio * 100;
    const overallLatency = calculateOverallLatency(analysis, config.requestRate);
    const performanceScore = calculatePerformanceScore(overallHitRatio, overallLatency, config);
    
    return {
        tiers: analysis,
        overallHitRatio,
        overallLatency,
        performanceScore,
        meetsTargets: {
            hitRatio: overallHitRatio >= config.targetHitRatio,
            latency: overallLatency <= config.targetLatency
        }
    };
}

function calculateTierHitRatio(capacityRatio, accessPattern, keyDistribution) {
    / Base hit ratio calculation based on cache size and access pattern
    let baseHitRatio = 0;
    
    switch (keyDistribution) {
        case 'uniform':
            baseHitRatio = Math.min(capacityRatio, 1.0);
            break;
        case 'zipfian':
            / Zipfian distribution - few keys accessed frequently
            const alpha = accessPattern.zipfianParameter;
            baseHitRatio = Math.min(Math.pow(capacityRatio, 1/alpha), 1.0);
            break;
        case 'normal':
            / Normal distribution around mean
            baseHitRatio = Math.min(capacityRatio * 1.2, 1.0);
            break;
        case 'bimodal':
            / Hot and cold data
            if (capacityRatio < 0.2) {
                baseHitRatio = capacityRatio * 4; / Hot data
            } else {
                baseHitRatio = 0.8 + (capacityRatio - 0.2) * 0.25; / + Cold data
            }
            break;
        case 'temporal':
            / Time-based clustering
            baseHitRatio = Math.min(capacityRatio * (1 + accessPattern.temporalLocality / 100), 1.0);
            break;
        default:
            baseHitRatio = Math.min(capacityRatio * 1.1, 1.0);
    }
    
    return Math.max(0, Math.min(baseHitRatio, 1.0));
}

function calculatePolicyEffectiveness(evictionPolicy, accessPattern) {
    / Calculate how well the eviction policy matches the access pattern
    const temporalWeight = accessPattern.temporalLocality / 100;
    const spatialWeight = accessPattern.spatialLocality / 100;
    
    let effectiveness = 1.0;
    
    switch (evictionPolicy.name) {
        case 'LRU':
            effectiveness = 0.8 + temporalWeight * 0.3;
            break;
        case 'LFU':
            effectiveness = 0.7 + (1 - temporalWeight) * 0.4;
            break;
        case 'ARC':
            effectiveness = 0.9 + Math.max(temporalWeight, 1 - temporalWeight) * 0.2;
            break;
        case 'LIRS':
            effectiveness = 0.95 + temporalWeight * spatialWeight * 0.1;
            break;
        case 'FIFO':
            effectiveness = 0.6 + spatialWeight * 0.3;
            break;
        case 'Random':
            effectiveness = 0.7; / Consistent regardless of pattern
            break;
    }
    
    return Math.max(0.5, Math.min(effectiveness, 1.2));
}

function calculateAverageLatency(tier, technology) {
    / Base latency from technology + tier configuration overhead
    return tier.latency + technology.latency;
}

function calculateTierThroughput(tier, technology, requestRate) {
    / Estimate tier throughput based on technology bandwidth and request rate
    const maxThroughput = technology.bandwidth;
    const actualThroughput = Math.min(maxThroughput, requestRate);
    return actualThroughput;
}

function calculateOverallLatency(tierAnalysis, requestRate) {
    let weightedLatency = 0;
    let totalWeight = 0;
    
    tierAnalysis.forEach(tier => {
        const weight = tier.requestsServed / requestRate;
        weightedLatency += tier.avgLatency * weight;
        totalWeight += weight;
    });
    
    / Add database latency for cache misses
    const missRatio = 1 - totalWeight;
    const databaseLatency = 50; / Assumed database latency in ms
    weightedLatency += databaseLatency * missRatio;
    
    return weightedLatency;
}

function calculatePerformanceScore(hitRatio, latency, config) {
    / Composite score based on hit ratio and latency targets
    const hitRatioScore = Math.min(hitRatio / config.targetHitRatio, 1.0) * 50;
    const latencyScore = Math.max(0, (1 - latency / (config.targetLatency * 2)) * 50);
    
    return hitRatioScore + latencyScore;
}

function generateOptimizations(config, hierarchyAnalysis) {
    const optimizations = [];
    
    / Check if targets are met
    if (!hierarchyAnalysis.meetsTargets.hitRatio) {
        optimizations.push({
            type: 'capacity',
            priority: 'high',
            title: 'Increase cache capacity',
            description: `Current hit ratio (${hierarchyAnalysis.overallHitRatio.toFixed(1)}%) below target (${config.targetHitRatio}%)`,
            impact: 'Increase L1 cache size by 2x',
            estimatedImprovement: '10-15% hit ratio increase'
        });
    }
    
    if (!hierarchyAnalysis.meetsTargets.latency) {
        optimizations.push({
            type: 'performance',
            priority: 'high',
            title: 'Optimize latency',
            description: `Current latency (${hierarchyAnalysis.overallLatency.toFixed(2)}ms) exceeds target (${config.targetLatency}ms)`,
            impact: 'Upgrade to faster storage technology',
            estimatedImprovement: '20-30% latency reduction'
        });
    }
    
    / Analyze eviction policy effectiveness
    const inefficientTiers = hierarchyAnalysis.tiers.filter(tier => tier.hitRatio < 60);
    if (inefficientTiers.length > 0) {
        optimizations.push({
            type: 'algorithm',
            priority: 'medium',
            title: 'Optimize eviction policies',
            description: `${inefficientTiers.length} tiers have low hit ratios`,
            impact: 'Switch to ARC or LIRS eviction policies',
            estimatedImprovement: '5-10% hit ratio increase'
        });
    }
    
    return optimizations;
}

function analyzeCacheCosts(config, hierarchyAnalysis) {
    const monthlyCosts = {
        memory: 0,
        storage: 0,
        network: 0,
        operational: 0
    };
    
    / Calculate costs for each tier
    hierarchyAnalysis.tiers.forEach(tier => {
        const technology = cacheTechnologies[tier.technology];
        const tierCost = tier.size * technology.costPerGB;
        
        if (tier.technology.includes('memory') || tier.technology === 'cpu-cache') {
            monthlyCosts.memory += tierCost;
        } else {
            monthlyCosts.storage += tierCost;
        }
    });
    
    / Network costs for cache coherence
    const coherenceTraffic = config.requestRate * 0.1 * 0.001; / 10% coherence traffic, $0.001 per 1000 requests
    monthlyCosts.network = coherenceTraffic * 24 * 30;
    
    / Operational overhead (10% of hardware costs)
    monthlyCosts.operational = (monthlyCosts.memory + monthlyCosts.storage) * 0.1;
    
    const totalCost = Object.values(monthlyCosts).reduce((sum, cost) => sum + cost, 0);
    
    / Calculate cost efficiency metrics
    const costPerHitRatio = totalCost / hierarchyAnalysis.overallHitRatio;
    const costPerRequest = totalCost / (config.requestRate * 24 * 30 * 3600); / Per request per month
    
    return {
        monthly: monthlyCosts,
        total: totalCost,
        efficiency: {
            costPerHitRatio,
            costPerRequest: costPerRequest * 1000000 / Per million requests
        },
        withinBudget: {
            memory: monthlyCosts.memory <= config.memoryBudget,
            storage: monthlyCosts.storage <= config.storageBudget,
            network: monthlyCosts.network <= config.networkBudget
        }
    };
}

function generateCacheRecommendations(config, hierarchyAnalysis, costAnalysis) {
    const recommendations = [];
    
    / Performance recommendations
    if (hierarchyAnalysis.performanceScore < 70) {
        recommendations.push({
            category: 'Performance',
            priority: 'High',
            title: 'Improve cache hierarchy performance',
            description: 'Current performance score is below optimal',
            actions: [
                'Consider adding an intermediate cache tier',
                'Upgrade slower tiers to faster technology',
                'Optimize eviction policies for access patterns'
            ]
        });
    }
    
    / Cost optimization recommendations
    if (!costAnalysis.withinBudget.memory || !costAnalysis.withinBudget.storage) {
        recommendations.push({
            category: 'Cost',
            priority: 'Medium',
            title: 'Optimize cache costs',
            description: 'Current configuration exceeds budget constraints',
            actions: [
                'Consider tiered storage with cheaper technologies for larger tiers',
                'Implement more aggressive eviction policies',
                'Evaluate cost-benefit of additional cache tiers'
            ]
        });
    }
    
    / Architecture recommendations
    const tierCount = hierarchyAnalysis.tiers.length;
    if (tierCount < 2 && config.workingSetSize > 10) {
        recommendations.push({
            category: 'Architecture',
            priority: 'Medium',
            title: 'Add cache tiers',
            description: 'Single-tier cache may not be optimal for large working sets',
            actions: [
                'Add L2 cache with SSD or NVMe technology',
                'Implement write-through or write-back policies',
                'Consider distributed caching for scalability'
            ]
        });
    }
    
    return recommendations;
}

function generateCacheResults(results) {
    const { config, hierarchy, costs, recommendations, optimizations } = results;
    
    return `
        <h3>🗄️ Cache Hierarchy Analysis</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                ${hierarchy.tiers.length} Tiers
                <div style="font-size: 0.4em; margin-top: 10px;">
                    Overall Hit Ratio: ${hierarchy.overallHitRatio.toFixed(1)}% | Avg Latency: ${hierarchy.overallLatency.toFixed(2)}ms
                </div>
            </div>
            <div class="performance-summary">
                <div class="perf-item">
                    <span class="perf-label">Performance Score:</span>
                    <span class="perf-value ${hierarchy.performanceScore >= 80 ? 'good' : hierarchy.performanceScore >= 60 ? 'warning' : 'critical'}">
                        ${hierarchy.performanceScore.toFixed(0)}/100
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Monthly Cost:</span>
                    <span class="perf-value">$${costs.total.toLocaleString()}</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Targets Met:</span>
                    <span class="perf-value ${hierarchy.meetsTargets.hitRatio && hierarchy.meetsTargets.latency ? 'good' : 'warning'}">
                        ${hierarchy.meetsTargets.hitRatio && hierarchy.meetsTargets.latency ? '✅' : '⚠️'}
                    </span>
                </div>
            </div>
        </div>
        
        <h4>📊 Tier Analysis</h4>
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Tier</th>
                    <th>Size</th>
                    <th>Technology</th>
                    <th>Hit Ratio</th>
                    <th>Latency</th>
                    <th>Throughput</th>
                </tr>
            </thead>
            <tbody>
                ${hierarchy.tiers.map(tier => `
                    <tr>
                        <td data-label="Tier">L${tier.tier}</td>
                        <td data-label="Size">${tier.size < 1 ? (tier.size * 1024).toFixed(0) + ' MB' : tier.size.toFixed(1) + ' GB'}</td>
                        <td data-label="Technology">${tier.technology.replace('-', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</td>
                        <td data-label="Hit Ratio" class="${tier.hitRatio >= 70 ? 'good' : tier.hitRatio >= 50 ? 'warning' : 'critical'}">${tier.hitRatio.toFixed(1)}%</td>
                        <td data-label="Latency">${tier.avgLatency < 1 ? (tier.avgLatency * 1000).toFixed(1) + 'μs' : tier.avgLatency.toFixed(2) + 'ms'}</td>
                        <td data-label="Throughput">${(tier.throughput / 1000).toFixed(1)}K req/s</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Cache Hierarchy Overview</h4>
                <canvas id="hierarchyChart" width="600" height="300"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Hit Ratio Distribution</h4>
                <canvas id="hitRatioChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Latency Analysis</h4>
                <canvas id="latencyChart" width="600" height="300"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Cost Breakdown</h4>
                <canvas id="costChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <h4>⚡ Performance Optimizations</h4>
        <div class="optimizations-grid">
            ${optimizations.map(opt => `
                <div class="optimization-card ${opt.type}">
                    <div class="opt-header">
                        <h5>${opt.title}</h5>
                        <span class="priority ${opt.priority}">${opt.priority.toUpperCase()}</span>
                    </div>
                    <p>${opt.description}</p>
                    <div class="opt-details">
                        <p><strong>Impact:</strong> ${opt.impact}</p>
                        <p><strong>Improvement:</strong> ${opt.estimatedImprovement}</p>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <h4>💰 Cost Analysis</h4>
        <div class="cost-analysis-grid">
            <div class="cost-card">
                <h5>Monthly Costs</h5>
                <div class="cost-breakdown">
                    <div class="cost-item">
                        <span>Memory:</span>
                        <span class="${costs.withinBudget.memory ? 'good' : 'warning'}">$${costs.monthly.memory.toLocaleString()}</span>
                    </div>
                    <div class="cost-item">
                        <span>Storage:</span>
                        <span class="${costs.withinBudget.storage ? 'good' : 'warning'}">$${costs.monthly.storage.toLocaleString()}</span>
                    </div>
                    <div class="cost-item">
                        <span>Network:</span>
                        <span class="${costs.withinBudget.network ? 'good' : 'warning'}">$${Math.round(costs.monthly.network).toLocaleString()}</span>
                    </div>
                    <div class="cost-item">
                        <span>Operational:</span>
                        <span>$${Math.round(costs.monthly.operational).toLocaleString()}</span>
                    </div>
                    <div class="cost-item total">
                        <span>Total:</span>
                        <span>$${costs.total.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <div class="cost-card">
                <h5>Efficiency Metrics</h5>
                <div class="efficiency-metrics">
                    <div class="metric-item">
                        <span>Cost per Hit Ratio %:</span>
                        <span>$${costs.efficiency.costPerHitRatio.toFixed(2)}</span>
                    </div>
                    <div class="metric-item">
                        <span>Cost per Million Requests:</span>
                        <span>$${costs.efficiency.costPerRequest.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <h4>💡 Recommendations</h4>
        <div class="recommendations-grid">
            ${recommendations.map(rec => `
                <div class="recommendation-card ${rec.category.toLowerCase()}">
                    <div class="rec-header">
                        <h5>${rec.title}</h5>
                        <span class="priority ${rec.priority.toLowerCase()}">${rec.priority.toUpperCase()}</span>
                    </div>
                    <p>${rec.description}</p>
                    <ul class="action-list">
                        ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    `;
}

function displayCacheErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawHierarchyChart(hierarchyAnalysis) {
    const ctx = document.getElementById('hierarchyChart');
    if (!ctx) return;
    
    if (hierarchyChart) {
        hierarchyChart.destroy();
    }
    
    hierarchyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hierarchyAnalysis.tiers.map(tier => `L${tier.tier}`),
            datasets: [
                {
                    label: 'Cache Size (GB)',
                    data: hierarchyAnalysis.tiers.map(tier => tier.size),
                    backgroundColor: '#36A2EB',
                    yAxisID: 'y'
                },
                {
                    label: 'Hit Ratio (%)',
                    data: hierarchyAnalysis.tiers.map(tier => tier.hitRatio),
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
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Cache Size (GB)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Hit Ratio (%)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    max: 100
                }
            }
        }
    });
}

function drawHitRatioChart(hierarchyAnalysis) {
    const ctx = document.getElementById('hitRatioChart');
    if (!ctx) return;
    
    if (hitRatioChart) {
        hitRatioChart.destroy();
    }
    
    hitRatioChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                ...hierarchyAnalysis.tiers.map(tier => `L${tier.tier} Hits`),
                'Database Misses'
            ],
            datasets: [{
                data: [
                    ...hierarchyAnalysis.tiers.map(tier => tier.hitRatio),
                    100 - hierarchyAnalysis.overallHitRatio
                ],
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#C9CBCF'
                ].slice(0, hierarchyAnalysis.tiers.length + 1)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Request Distribution Across Cache Tiers'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function drawLatencyChart(hierarchyAnalysis) {
    const ctx = document.getElementById('latencyChart');
    if (!ctx) return;
    
    if (latencyChart) {
        latencyChart.destroy();
    }
    
    latencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hierarchyAnalysis.tiers.map(tier => `L${tier.tier}`),
            datasets: [{
                label: 'Average Latency (ms)',
                data: hierarchyAnalysis.tiers.map(tier => tier.avgLatency),
                backgroundColor: hierarchyAnalysis.tiers.map(tier => 
                    tier.avgLatency < 1 ? '#51cf66' : 
                    tier.avgLatency < 5 ? '#ffd43b' : '#ff6b6b'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Latency by Cache Tier'
                },
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

function drawCostChart(costAnalysis) {
    const ctx = document.getElementById('costChart');
    if (!ctx) return;
    
    if (costChart) {
        costChart.destroy();
    }
    
    costChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Memory', 'Storage', 'Network', 'Operational'],
            datasets: [{
                data: [
                    costAnalysis.monthly.memory,
                    costAnalysis.monthly.storage,
                    costAnalysis.monthly.network,
                    costAnalysis.monthly.operational
                ],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Monthly Cost Breakdown'
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const percentage = ((context.parsed / costAnalysis.total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function simulateCachePerformance() {
    alert('Cache simulation will model various access patterns and evaluate performance under different workload scenarios.');
}

function compareEvictionPolicies() {
    const config = getCacheConfiguration();
    const policies = ['lru', 'lfu', 'arc', 'lirs'];
    
    / Generate comparison data (simplified)
    const comparisonData = policies.map(policy => {
        const policySpec = evictionPolicies[policy];
        const baseHitRatio = 75; / Simplified base calculation
        const hitRatio = baseHitRatio * (policySpec.temporalScore / 90);
        
        return {
            name: policySpec.name,
            hitRatio: hitRatio.toFixed(1),
            complexity: policySpec.complexity,
            overhead: policySpec.overhead,
            scanResistance: policySpec.scanResistance
        };
    });
    
    let comparisonHTML = `
        <div class="comparison-results">
            <h3>🔄 Eviction Policy Comparison</h3>
            <table class="responsive-table">
                <thead>
                    <tr>
                        <th>Policy</th>
                        <th>Estimated Hit Ratio</th>
                        <th>Complexity</th>
                        <th>Memory Overhead</th>
                        <th>Scan Resistance</th>
                    </tr>
                </thead>
                <tbody>
                    ${comparisonData.map(data => `
                        <tr>
                            <td data-label="Policy">${data.name}</td>
                            <td data-label="Hit Ratio">${data.hitRatio}%</td>
                            <td data-label="Complexity">${data.complexity}</td>
                            <td data-label="Memory Overhead">${data.overhead}</td>
                            <td data-label="Scan Resistance">${data.scanResistance}/100</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('results').innerHTML = comparisonHTML;
}

function exportCacheResults() {
    const config = getCacheConfiguration();
    const results = {
        timestamp: new Date().toISOString(),
        configuration: config,
        analysis: 'Detailed cache hierarchy analysis would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cache-hierarchy-analysis.json';
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

.cache-levels {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border: 1px solid #ddd;
}

.cache-tier {
    background: #f8f9fa;
    margin: 15px 0;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.tier-config {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    align-items: end;
    margin-top: 10px;
}

.tier-config label {
    font-weight: bold;
    margin-bottom: 5px;
    display: block;
}

.tier-config input,
.tier-config select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.remove-tier {
    background: #dc3545;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}

.add-tier {
    background: #28a745;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 15px;
}

.calc-button, .simulation-button, .compare-button, .export-button {
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

.compare-button {
    background: #fd7e14;
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

.compare-button:hover {
    background: #e8590c;
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

.perf-value.critical {
    color: #ff6b6b;
}

.benefit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.benefit-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.chart-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.optimizations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.optimization-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #007bff;
}

.optimization-card.capacity {
    border-left-color: #e74c3c;
}

.optimization-card.performance {
    border-left-color: #f39c12;
}

.optimization-card.algorithm {
    border-left-color: #9b59b6;
}

.opt-header {
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

.opt-details {
    margin-top: 10px;
    font-size: 0.9em;
}

.opt-details p {
    margin: 5px 0;
    color: #555;
}

.cost-analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.cost-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.cost-breakdown {
    font-size: 0.9em;
}

.cost-item {
    display: flex;
    justify-content: space-between;
    margin: 8px 0;
    padding: 5px 0;
}

.cost-item.total {
    border-top: 2px solid #007bff;
    font-weight: bold;
    margin-top: 10px;
    padding-top: 10px;
}

.efficiency-metrics {
    font-size: 0.9em;
}

.metric-item {
    display: flex;
    justify-content: space-between;
    margin: 8px 0;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
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

.action-list {
    margin-top: 10px;
    padding-left: 20px;
}

.action-list li {
    margin: 5px 0;
    color: #555;
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

.comparison-results {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

@media (max-width: 768px) {
    .calculator-tool {
        padding: 10px;
    }
    
    .tier-config {
        grid-template-columns: 1fr;
    }
    
    .performance-summary {
        grid-template-columns: 1fr;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    .benefit-grid,
    .optimizations-grid,
    .cost-analysis-grid {
        grid-template-columns: 1fr;
    }
    
    .opt-header,
    .rec-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}
</style>

</div>