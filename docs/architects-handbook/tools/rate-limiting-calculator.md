---
title: Rate Limiting Calculator
description: Token bucket, sliding window, distributed rate limiting algorithms analysis
type: documentation
---

# Rate Limiting Calculator



## Overview

Rate Limiting Calculator
description: Token bucket, sliding window, distributed rate limiting algorithms analysis
type: documentation
---

# Rate Limiting Calculator

## Table of Contents

- [Interactive Calculator](#interactive-calculator)
  - [Traffic Patterns](#traffic-patterns)
  - [Rate Limiting Strategy](#rate-limiting-strategy)
  - [Granularity & Scope](#granularity-scope)
  - [Response Strategy](#response-strategy)
  - [Performance Requirements](#performance-requirements)
- [Understanding Rate Limiting Algorithms](#understanding-rate-limiting-algorithms)
  - [Algorithm Comparison](#algorithm-comparison)
  - [Distributed Rate Limiting Challenges](#distributed-rate-limiting-challenges)
  - [Implementation Patterns](#implementation-patterns)
- [Related Resources](#related-resources)



! Advanced Rate Limiting Analysis"
    <h2>🚦 Rate Limiting Strategy Calculator</h2>
    <p>Design and analyze rate limiting strategies with token bucket, sliding window, fixed window, and distributed algorithms.

**Reading time:** ~26 minutes

## Table of Contents

- [Interactive Calculator](#interactive-calculator)
  - [Traffic Patterns](#traffic-patterns)
  - [Rate Limiting Strategy](#rate-limiting-strategy)
  - [Granularity & Scope](#granularity-scope)
  - [Response Strategy](#response-strategy)
  - [Performance Requirements](#performance-requirements)
- [Understanding Rate Limiting Algorithms](#understanding-rate-limiting-algorithms)
  - [Algorithm Comparison](#algorithm-comparison)
  - [Distributed Rate Limiting Challenges](#distributed-rate-limiting-challenges)
  - [Implementation Patterns](#implementation-patterns)
- [Related Resources](#related-resources)



!!! info "Advanced Rate Limiting Analysis"
    <h2>🚦 Rate Limiting Strategy Calculator</h2>
    <p>Design and analyze rate limiting strategies with token bucket, sliding window, fixed window, and distributed algorithms.</p>

## Interactive Calculator

<div class="calculator-tool">
<form id="rateLimitingCalc">

### Traffic Patterns

<label for="avgRequestRate">Average request rate (req/sec):</label>
<input type="number" id="avgRequestRate" value="1000" min="1" step="10">
*Baseline traffic under normal conditions*

<label for="peakMultiplier">Peak traffic multiplier:</label>
<select id="peakMultiplier">
<option value="2">2x (moderate peaks)</option>
<option value="3">3x (high peaks)</option>
<option value="5">5x (very high peaks)</option>
<option value="10">10x (viral/DDoS)</option>
<option value="20">20x (extreme events)</option>
</select>

<label for="burstDuration">Typical burst duration:</label>
<select id="burstDuration">
<option value="5">5 seconds</option>
<option value="30">30 seconds</option>
<option value="60">1 minute</option>
<option value="300">5 minutes</option>
<option value="900">15 minutes</option>
</select>

<label for="trafficPattern">Traffic pattern:</label>
<select id="trafficPattern">
<option value="steady">Steady state</option>
<option value="daily-peaks">Daily peaks (business hours)</option>
<option value="weekly-cycles">Weekly cycles</option>
<option value="seasonal">Seasonal variations</option>
<option value="event-driven">Event-driven spikes</option>
<option value="bursty">Randomly bursty</option>
</select>

### Rate Limiting Strategy

<div class="algorithm-selection">
<h4>🔧 Algorithm Configuration</h4>

<label for="rateLimitAlgorithm">Primary algorithm:</label>
<select id="rateLimitAlgorithm" onchange="toggleAlgorithmConfig()">
<option value="token-bucket">Token Bucket</option>
<option value="sliding-window-log">Sliding Window Log</option>
<option value="sliding-window-counter">Sliding Window Counter</option>
<option value="fixed-window">Fixed Window</option>
<option value="leaky-bucket">Leaky Bucket</option>
<option value="adaptive">Adaptive Rate Limiting</option>
<option value="distributed-consistent">Distributed Consistent</option>
</select>

<div id="tokenBucketConfig" class="algorithm-config">
<h5>Token Bucket Parameters</h5>
<label for="bucketCapacity">Bucket capacity (tokens):</label>
<input type="number" id="bucketCapacity" value="1000" min="1" step="10">
<label for="refillRate">Refill rate (tokens/sec):</label>
<input type="number" id="refillRate" value="100" min="1" step="1">
<label for="tokensPerRequest">Tokens per request:</label>
<input type="number" id="tokensPerRequest" value="1" min="1" step="1">
</div>

<div id="slidingWindowConfig" class="algorithm-config" style="display: none;">
<h5>Sliding Window Parameters</h5>
<label for="windowSize">Window size (seconds):</label>
<select id="windowSize">
<option value="60">1 minute</option>
<option value="300">5 minutes</option>
<option value="900">15 minutes</option>
<option value="3600">1 hour</option>
</select>
<label for="requestLimit">Request limit per window:</label>
<input type="number" id="requestLimit" value="6000" min="1" step="100">
<label for="subWindowCount">Sub-windows (for counter):</label>
<input type="number" id="subWindowCount" value="60" min="1" max="3600" step="1">
</div>

<div id="fixedWindowConfig" class="algorithm-config" style="display: none;">
<h5>Fixed Window Parameters</h5>
<label for="fixedWindowSize">Window size (seconds):</label>
<select id="fixedWindowSize">
<option value="1">1 second</option>
<option value="60">1 minute</option>
<option value="300">5 minutes</option>
<option value="3600">1 hour</option>
</select>
<label for="fixedRequestLimit">Requests per window:</label>
<input type="number" id="fixedRequestLimit" value="1000" min="1" step="10">
</div>

<div id="adaptiveConfig" class="algorithm-config" style="display: none;">
<h5>Adaptive Parameters</h5>
<label for="baseLimit">Base limit (req/sec):</label>
<input type="number" id="baseLimit" value="1000" min="1" step="10">
<label for="adaptationFactor">Adaptation factor:</label>
<select id="adaptationFactor">
<option value="0.1">Conservative (0.1)</option>
<option value="0.2">Moderate (0.2)</option>
<option value="0.5">Aggressive (0.5)</option>
</select>
<label for="successThreshold">Success threshold:</label>
<input type="number" id="successThreshold" value="95" min="50" max="100" step="1">
*Percentage of successful requests*
</div>
</div>

### Granularity & Scope

<label for="rateLimitScope">Rate limit scope:</label>
<select id="rateLimitScope">
<option value="global">Global (entire system)</option>
<option value="per-user">Per user</option>
<option value="per-ip">Per IP address</option>
<option value="per-api-key">Per API key</option>
<option value="per-tenant">Per tenant</option>
<option value="per-resource">Per resource/endpoint</option>
<option value="hierarchical">Hierarchical (multi-level)</option>
</select>

<label for="distributedNodes">Number of nodes:</label>
<input type="number" id="distributedNodes" value="3" min="1" max="100" step="1">
*For distributed rate limiting*

<label for="syncStrategy">Synchronization strategy:</label>
<select id="syncStrategy">
<option value="local-only">Local only (no sync)</option>
<option value="periodic-sync">Periodic sync</option>
<option value="real-time-sync">Real-time sync</option>
<option value="consensus">Consensus-based</option>
<option value="gossip">Gossip protocol</option>
</select>

### Response Strategy

<label for="exceedAction">When limit exceeded:</label>
<select id="exceedAction">
<option value="reject">Reject request (429)</option>
<option value="queue">Queue request</option>
<option value="throttle">Throttle (slow down)</option>
<option value="prioritize">Prioritize by user tier</option>
<option value="graceful-degradation">Graceful degradation</option>
</select>

<label for="queueConfig" id="queueConfigLabel" style="display: none;">Queue capacity:</label>
<input type="number" id="queueCapacity" value="1000" min="10" step="10" style="display: none;">

<label for="backoffStrategy">Backoff strategy:</label>
<select id="backoffStrategy">
<option value="none">No backoff</option>
<option value="linear">Linear backoff</option>
<option value="exponential">Exponential backoff</option>
<option value="adaptive">Adaptive backoff</option>
</select>

### Performance Requirements

<label for="targetLatency">Target latency overhead (ms):</label>
<select id="targetLatency">
<option value="1">< 1ms (in-memory)</option>
<option value="5">< 5ms (local cache)</option>
<option value="10">< 10ms (Redis)</option>
<option value="20">< 20ms (database)</option>
</select>

<label for="consistencyRequirement">Consistency requirement:</label>
<select id="consistencyRequirement">
<option value="eventual">Eventual consistency</option>
<option value="bounded">Bounded staleness</option>
<option value="strong">Strong consistency</option>
</select>

<label for="storageBackend">Storage backend:</label>
<select id="storageBackend">
<option value="memory">In-memory</option>
<option value="redis">Redis</option>
<option value="hazelcast">Hazelcast</option>
<option value="database">Database</option>
<option value="distributed-cache">Distributed cache</option>
</select>

<button type="button" onclick="analyzeRateLimiting()" class="calc-button">Analyze Strategy</button>
<button type="button" onclick="simulateTraffic()" class="simulation-button">Run Traffic Simulation</button>
<button type="button" onclick="compareAlgorithms()" class="compare-button">Compare Algorithms</button>
<button type="button" onclick="exportRateLimitingResults()" class="export-button">Export Analysis</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Rate Limiting Algorithms

### Algorithm Comparison

<div class="algorithm-grid">
<div class="algorithm-card">
<h4>🪣 Token Bucket</h4>
<ul>
<li><strong>Pros:</strong> Allows bursts, smooth rate</li>
<li><strong>Cons:</strong> Complex state management</li>
<li><strong>Best for:</strong> APIs with burst tolerance</li>
<li><strong>Memory:</strong> O(1) per bucket</li>
</ul>
<div class="algorithm-formula">
<code>allow = (tokens >= cost) && refill()</code>
</div>
</div>

<div class="algorithm-card">
<h4>🪟 Sliding Window Log</h4>
<ul>
<li><strong>Pros:</strong> Precise, no boundary effects</li>
<li><strong>Cons:</strong> High memory usage</li>
<li><strong>Best for:</strong> Strict accuracy requirements</li>
<li><strong>Memory:</strong> O(request_count)</li>
</ul>
<div class="algorithm-formula">
<code>allow = (count_in_window < limit)</code>
</div>
</div>

<div class="algorithm-card">
<h4>📊 Sliding Window Counter</h4>
<ul>
<li><strong>Pros:</strong> Memory efficient, reasonably accurate</li>
<li><strong>Cons:</strong> Approximation, boundary smoothing</li>
<li><strong>Best for:</strong> High-traffic scenarios</li>
<li><strong>Memory:</strong> O(sub_windows)</li>
</ul>
<div class="algorithm-formula">
<code>estimate = prev_window * overlap + curr_window</code>
</div>
</div>

<div class="algorithm-card">
<h4>⏰ Fixed Window</h4>
<ul>
<li><strong>Pros:</strong> Simple, low memory</li>
<li><strong>Cons:</strong> Boundary burst problem</li>
<li><strong>Best for:</strong> Simple use cases</li>
<li><strong>Memory:</strong> O(1)</li>
</ul>
<div class="algorithm-formula">
<code>allow = (current_window_count < limit)</code>
</div>
</div>

<div class="algorithm-card">
<h4>💧 Leaky Bucket</h4>
<ul>
<li><strong>Pros:</strong> Smooth output rate</li>
<li><strong>Cons:</strong> No burst accommodation</li>
<li><strong>Best for:</strong> Steady rate requirements</li>
<li><strong>Memory:</strong> O(1)</li>
</ul>
<div class="algorithm-formula">
<code>queue_size = min(capacity, size + requests - leaked)</code>
</div>
</div>

<div class="algorithm-card">
<h4>🧠 Adaptive</h4>
<ul>
<li><strong>Pros:</strong> Self-adjusting, responsive</li>
<li><strong>Cons:</strong> Complex tuning</li>
<li><strong>Best for:</strong> Variable load patterns</li>
<li><strong>Memory:</strong> O(1) + state</li>
</ul>
<div class="algorithm-formula">
<code>limit = base_limit * (1 + success_rate * factor)</code>
</div>
</div>
</div>

### Distributed Rate Limiting Challenges

<table class="responsive-table">
<thead>
<tr>
<th>Challenge</th>
<th>Impact</th>
<th>Solutions</th>
<th>Complexity</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Challenge">Synchronization Latency</td>
<td data-label="Impact">Stale counters, overage</td>
<td data-label="Solutions">Local quotas, periodic sync</td>
<td data-label="Complexity">Medium</td>
</tr>
<tr>
<td data-label="Challenge">Network Partitions</td>
<td data-label="Impact">Split brain, inconsistency</td>
<td data-label="Solutions">Eventual consistency, degradation</td>
<td data-label="Complexity">High</td>
</tr>
<tr>
<td data-label="Challenge">Hot Keys</td>
<td data-label="Impact">Bottlenecks, poor scaling</td>
<td data-label="Solutions">Sharding, consistent hashing</td>
<td data-label="Complexity">Medium</td>
</tr>
<tr>
<td data-label="Challenge">Clock Skew</td>
<td data-label="Impact">Window misalignment</td>
<td data-label="Solutions">NTP sync, logical clocks</td>
<td data-label="Complexity">Low</td>
</tr>
</tbody>
</table>

### Implementation Patterns

<div class="strategy-card">
<div>
<h4>🎯 Client-Side Rate Limiting</h4>
<ul>
<li>Implement in SDK/client library</li>
<li>Reduce server load</li>
<li>Fast feedback to user</li>
<li>Cannot be fully trusted</li>
</ul>
<p><strong>Use case:</strong> User experience optimization</p>
</div>

<div>
<h4>🚪 Gateway Rate Limiting</h4>
<ul>
<li>Single enforcement point</li>
<li>Protocol independent</li>
<li>Easy to configure</li>
<li>Potential bottleneck</li>
</ul>
<p><strong>Use case:</strong> API management</p>
</div>

<div>
<h4>🏗️ Service-Level Rate Limiting</h4>
<ul>
<li>Fine-grained control</li>
<li>Resource-specific limits</li>
<li>Better performance</li>
<li>Distributed complexity</li>
</ul>
<p><strong>Use case:</strong> Microservices architecture</p>
</div>

<div>
<h4>🌐 CDN Rate Limiting</h4>
<ul>
<li>Edge-based protection</li>
<li>Geographic distribution</li>
<li>DDoS mitigation</li>
<li>Limited customization</li>
</ul>
<p><strong>Use case:</strong> Global applications</p>
</div>
</div>

## Related Resources

- [Load Balancer Simulator](load-balancer-simulator.md)
- [Throughput Calculator](throughput-calculator.md)
- [API Gateway Patterns](../../pattern-library/communication/api-gateway.md)
- [Backpressure Strategies](../../pattern-library/scaling/backpressure.md)

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let algorithmChart = null;
let performanceChart = null;
let simulationChart = null;
let comparisonChart = null;

/ Algorithm configurations and characteristics
const algorithmSpecs = {
    'token-bucket': {
        name: 'Token Bucket',
        memoryComplexity: 'O(1)',
        accuracy: 95,
        burstTolerance: 90,
        implementationComplexity: 'Medium',
        latencyOverhead: 1
    },
    'sliding-window-log': {
        name: 'Sliding Window Log',
        memoryComplexity: 'O(N)',
        accuracy: 100,
        burstTolerance: 60,
        implementationComplexity: 'High',
        latencyOverhead: 5
    },
    'sliding-window-counter': {
        name: 'Sliding Window Counter',
        memoryComplexity: 'O(K)',
        accuracy: 85,
        burstTolerance: 70,
        implementationComplexity: 'Medium',
        latencyOverhead: 2
    },
    'fixed-window': {
        name: 'Fixed Window',
        memoryComplexity: 'O(1)',
        accuracy: 70,
        burstTolerance: 40,
        implementationComplexity: 'Low',
        latencyOverhead: 1
    },
    'leaky-bucket': {
        name: 'Leaky Bucket',
        memoryComplexity: 'O(1)',
        accuracy: 95,
        burstTolerance: 20,
        implementationComplexity: 'Low',
        latencyOverhead: 1
    },
    'adaptive': {
        name: 'Adaptive',
        memoryComplexity: 'O(1)',
        accuracy: 80,
        burstTolerance: 85,
        implementationComplexity: 'Very High',
        latencyOverhead: 3
    },
    'distributed-consistent': {
        name: 'Distributed Consistent',
        memoryComplexity: 'O(1)',
        accuracy: 95,
        burstTolerance: 75,
        implementationComplexity: 'Very High',
        latencyOverhead: 10
    }
};

/ Show/hide queue configuration based on exceed action
document.getElementById('exceedAction').addEventListener('change', function() {
    const queueElements = [
        document.getElementById('queueConfigLabel'),
        document.getElementById('queueCapacity')
    ];
    
    if (this.value === 'queue') {
        queueElements.forEach(el => el.style.display = 'block');
    } else {
        queueElements.forEach(el => el.style.display = 'none');
    }
});

function toggleAlgorithmConfig() {
    / Hide all algorithm configs
    const configs = document.querySelectorAll('.algorithm-config');
    configs.forEach(config => config.style.display = 'none');
    
    const selectedAlgorithm = document.getElementById('rateLimitAlgorithm').value;
    
    / Show relevant config
    switch (selectedAlgorithm) {
        case 'token-bucket':
            document.getElementById('tokenBucketConfig').style.display = 'block';
            break;
        case 'sliding-window-log':
        case 'sliding-window-counter':
            document.getElementById('slidingWindowConfig').style.display = 'block';
            break;
        case 'fixed-window':
            document.getElementById('fixedWindowConfig').style.display = 'block';
            break;
        case 'adaptive':
            document.getElementById('adaptiveConfig').style.display = 'block';
            break;
    }
}

function validateRateLimitingInputs() {
    const inputs = {
        avgRequestRate: { value: parseFloat(document.getElementById('avgRequestRate').value), min: 1, name: 'Average request rate' },
        distributedNodes: { value: parseInt(document.getElementById('distributedNodes').value), min: 1, max: 100, name: 'Number of nodes' }
    };
    
    / Algorithm-specific validations
    const algorithm = document.getElementById('rateLimitAlgorithm').value;
    
    if (algorithm === 'token-bucket') {
        inputs.bucketCapacity = { 
            value: parseInt(document.getElementById('bucketCapacity').value), 
            min: 1, 
            name: 'Bucket capacity' 
        };
        inputs.refillRate = { 
            value: parseFloat(document.getElementById('refillRate').value), 
            min: 1, 
            name: 'Refill rate' 
        };
    }
    
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

function analyzeRateLimiting() {
    const validation = validateRateLimitingInputs();
    if (!validation.valid) {
        displayRateLimitingErrors(validation.errors);
        return;
    }
    
    const config = getRateLimitingConfiguration();
    const trafficAnalysis = analyzeTrafficPatterns(config);
    const algorithmAnalysis = analyzeAlgorithmPerformance(config, trafficAnalysis);
    const distributedAnalysis = analyzeDistributedChallenges(config);
    const recommendations = generateRateLimitingRecommendations(config, algorithmAnalysis, distributedAnalysis);
    
    const results = {
        config,
        traffic: trafficAnalysis,
        algorithm: algorithmAnalysis,
        distributed: distributedAnalysis,
        recommendations
    };
    
    let resultsHTML = generateRateLimitingResults(results);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawAlgorithmChart(algorithmAnalysis);
        drawPerformanceChart(trafficAnalysis, algorithmAnalysis);
    }, 100);
}

function getRateLimitingConfiguration() {
    return {
        avgRequestRate: parseFloat(document.getElementById('avgRequestRate').value),
        peakMultiplier: parseFloat(document.getElementById('peakMultiplier').value),
        burstDuration: parseInt(document.getElementById('burstDuration').value),
        trafficPattern: document.getElementById('trafficPattern').value,
        rateLimitAlgorithm: document.getElementById('rateLimitAlgorithm').value,
        rateLimitScope: document.getElementById('rateLimitScope').value,
        distributedNodes: parseInt(document.getElementById('distributedNodes').value),
        syncStrategy: document.getElementById('syncStrategy').value,
        exceedAction: document.getElementById('exceedAction').value,
        backoffStrategy: document.getElementById('backoffStrategy').value,
        targetLatency: parseFloat(document.getElementById('targetLatency').value),
        consistencyRequirement: document.getElementById('consistencyRequirement').value,
        storageBackend: document.getElementById('storageBackend').value,
        / Algorithm-specific parameters
        bucketCapacity: parseInt(document.getElementById('bucketCapacity').value) || 1000,
        refillRate: parseFloat(document.getElementById('refillRate').value) || 100,
        tokensPerRequest: parseInt(document.getElementById('tokensPerRequest').value) || 1,
        windowSize: parseInt(document.getElementById('windowSize').value) || 60,
        requestLimit: parseInt(document.getElementById('requestLimit').value) || 6000,
        subWindowCount: parseInt(document.getElementById('subWindowCount').value) || 60
    };
}

function analyzeTrafficPatterns(config) {
    const baseRate = config.avgRequestRate;
    const peakRate = baseRate * config.peakMultiplier;
    const burstDuration = config.burstDuration;
    
    / Generate traffic pattern simulation
    const timePoints = [];
    const requestRates = [];
    const duration = 3600; / 1 hour simulation
    
    for (let t = 0; t < duration; t += 60) { / 1-minute intervals
        timePoints.push(t / 60); / Convert to minutes
        
        let rate = baseRate;
        
        switch (config.trafficPattern) {
            case 'steady':
                rate = baseRate + (Math.random() - 0.5) * baseRate * 0.1; / ±5% noise
                break;
            case 'daily-peaks':
                / Simulate business hours peak
                const hour = (t / 3600) % 24;
                const businessHoursFactor = (hour >= 9 && hour <= 17) ? 1.5 : 0.7;
                rate = baseRate * businessHoursFactor;
                break;
            case 'event-driven':
                / Random spikes
                if (Math.random() < 0.1) { / 10% chance of spike
                    rate = peakRate;
                } else {
                    rate = baseRate;
                }
                break;
            case 'bursty':
                / Bursty pattern with varying intensities
                const burstFactor = 1 + Math.sin(t / 300) * 0.5 + Math.random() * 0.3;
                rate = baseRate * burstFactor;
                break;
            default:
                rate = baseRate;
        }
        
        requestRates.push(Math.max(0, rate));
    }
    
    const maxRate = Math.max(...requestRates);
    const avgRate = requestRates.reduce((sum, rate) => sum + rate, 0) / requestRates.length;
    const variance = requestRates.reduce((sum, rate) => sum + Math.pow(rate - avgRate, 2), 0) / requestRates.length;
    
    return {
        timePoints,
        requestRates,
        maxRate,
        avgRate,
        variance: Math.sqrt(variance),
        burstFrequency: requestRates.filter(rate => rate > avgRate * 1.5).length / requestRates.length
    };
}

function analyzeAlgorithmPerformance(config, trafficAnalysis) {
    const algorithm = config.rateLimitAlgorithm;
    const spec = algorithmSpecs[algorithm];
    
    / Simulate algorithm behavior
    const simulation = simulateAlgorithm(config, trafficAnalysis);
    
    / Calculate effectiveness metrics
    const totalRequests = trafficAnalysis.requestRates.reduce((sum, rate) => sum + rate * 60, 0); / Convert rate to total requests
    const acceptedRequests = simulation.acceptedRequests;
    const rejectedRequests = totalRequests - acceptedRequests;
    
    const acceptanceRate = (acceptedRequests / totalRequests) * 100;
    const fairnessScore = calculateFairnessScore(simulation.bucketStates);
    const burstHandling = calculateBurstHandling(config, trafficAnalysis, simulation);
    
    return {
        algorithm,
        spec,
        totalRequests: Math.round(totalRequests),
        acceptedRequests: Math.round(acceptedRequests),
        rejectedRequests: Math.round(rejectedRequests),
        acceptanceRate,
        fairnessScore,
        burstHandling,
        latencyOverhead: spec.latencyOverhead,
        memoryUsage: calculateMemoryUsage(algorithm, config),
        simulation
    };
}

function simulateAlgorithm(config, trafficAnalysis) {
    const algorithm = config.rateLimitAlgorithm;
    let totalAccepted = 0;
    const bucketStates = [];
    const acceptanceRates = [];
    
    / Initialize algorithm state
    let state = initializeAlgorithmState(algorithm, config);
    
    trafficAnalysis.requestRates.forEach((requestRate, index) => {
        const requestsThisMinute = requestRate * 60; / Convert rate to actual requests
        let acceptedThisMinute = 0;
        
        / Simulate each request in this minute
        for (let i = 0; i < requestsThisMinute; i++) {
            if (shouldAcceptRequest(algorithm, state, config)) {
                acceptedThisMinute++;
            }
            updateAlgorithmState(algorithm, state, config);
        }
        
        totalAccepted += acceptedThisMinute;
        bucketStates.push({ ...state });
        acceptanceRates.push((acceptedThisMinute / requestsThisMinute) * 100);
    });
    
    return {
        acceptedRequests: totalAccepted,
        bucketStates,
        acceptanceRates
    };
}

function initializeAlgorithmState(algorithm, config) {
    switch (algorithm) {
        case 'token-bucket':
            return {
                tokens: config.bucketCapacity,
                lastRefill: Date.now()
            };
        case 'sliding-window-log':
            return {
                requests: [] / Array of timestamps
            };
        case 'sliding-window-counter':
            return {
                windows: new Array(config.subWindowCount).fill(0),
                currentWindow: 0
            };
        case 'fixed-window':
            return {
                count: 0,
                windowStart: Math.floor(Date.now() / 1000)
            };
        default:
            return {};
    }
}

function shouldAcceptRequest(algorithm, state, config) {
    switch (algorithm) {
        case 'token-bucket':
            return state.tokens >= config.tokensPerRequest;
        case 'sliding-window-log':
            const now = Date.now();
            const windowStart = now - (config.windowSize * 1000);
            const validRequests = state.requests.filter(timestamp => timestamp > windowStart);
            return validRequests.length < config.requestLimit;
        case 'sliding-window-counter':
            const totalRequests = state.windows.reduce((sum, count) => sum + count, 0);
            return totalRequests < config.requestLimit;
        case 'fixed-window':
            return state.count < config.requestLimit;
        default:
            return true;
    }
}

function updateAlgorithmState(algorithm, state, config) {
    const now = Date.now();
    
    switch (algorithm) {
        case 'token-bucket':
            / Refill tokens
            const timePassed = (now - state.lastRefill) / 1000;
            const tokensToAdd = timePassed * config.refillRate;
            state.tokens = Math.min(config.bucketCapacity, state.tokens + tokensToAdd);
            state.lastRefill = now;
            
            / Consume token if request was accepted
            if (state.tokens >= config.tokensPerRequest) {
                state.tokens -= config.tokensPerRequest;
            }
            break;
            
        case 'sliding-window-log':
            state.requests.push(now);
            / Clean old requests
            const windowStart = now - (config.windowSize * 1000);
            state.requests = state.requests.filter(timestamp => timestamp > windowStart);
            break;
            
        case 'sliding-window-counter':
            state.windows[state.currentWindow]++;
            / Advance window periodically (simplified)
            if (Math.random() < 0.01) { / 1% chance to advance window
                state.currentWindow = (state.currentWindow + 1) % config.subWindowCount;
                state.windows[state.currentWindow] = 0;
            }
            break;
            
        case 'fixed-window':
            state.count++;
            / Reset window periodically (simplified)
            const currentWindowStart = Math.floor(now / 1000);
            if (currentWindowStart > state.windowStart) {
                state.windowStart = currentWindowStart;
                state.count = 1;
            }
            break;
    }
}

function calculateFairnessScore(bucketStates) {
    / Simplified fairness calculation based on bucket state consistency
    if (bucketStates.length < 2) return 100;
    
    const variations = [];
    for (let i = 1; i < bucketStates.length; i++) {
        if (bucketStates[i].tokens !== undefined) {
            variations.push(Math.abs(bucketStates[i].tokens - bucketStates[i-1].tokens));
        }
    }
    
    if (variations.length === 0) return 100;
    
    const avgVariation = variations.reduce((sum, v) => sum + v, 0) / variations.length;
    return Math.max(0, 100 - avgVariation); / Simplified scoring
}

function calculateBurstHandling(config, trafficAnalysis, simulation) {
    const burstThreshold = config.avgRequestRate * 1.5;
    const burstPeriods = trafficAnalysis.requestRates.map((rate, index) => ({
        index,
        rate,
        isBurst: rate > burstThreshold,
        acceptanceRate: simulation.acceptanceRates[index]
    })).filter(period => period.isBurst);
    
    if (burstPeriods.length === 0) return 100;
    
    const avgBurstAcceptance = burstPeriods.reduce((sum, period) => sum + period.acceptanceRate, 0) / burstPeriods.length;
    return avgBurstAcceptance;
}

function calculateMemoryUsage(algorithm, config) {
    switch (algorithm) {
        case 'token-bucket':
        case 'fixed-window':
        case 'leaky-bucket':
            return '8 bytes'; / Simple counter/state
        case 'sliding-window-counter':
            return `${config.subWindowCount * 4} bytes`; / Array of counters
        case 'sliding-window-log':
            return `${config.requestLimit * 8} bytes (worst case)`; / Timestamps
        case 'adaptive':
            return '32 bytes'; / Multiple state variables
        case 'distributed-consistent':
            return '64 bytes'; / Additional metadata
        default:
            return 'Unknown';
    }
}

function analyzeDistributedChallenges(config) {
    if (config.distributedNodes === 1) {
        return {
            applicable: false,
            challenges: [],
            recommendations: []
        };
    }
    
    const challenges = [];
    const recommendations = [];
    
    / Synchronization overhead
    const syncOverhead = calculateSyncOverhead(config.syncStrategy, config.distributedNodes);
    if (syncOverhead > 10) {
        challenges.push('High synchronization overhead');
        recommendations.push('Consider local quotas with periodic reconciliation');
    }
    
    / Consistency concerns
    if (config.consistencyRequirement === 'strong' && config.distributedNodes > 3) {
        challenges.push('Strong consistency with many nodes affects performance');
        recommendations.push('Evaluate if eventual consistency is acceptable');
    }
    
    / Hot key problems
    if (config.rateLimitScope === 'global') {
        challenges.push('Global rate limiting creates hot keys');
        recommendations.push('Implement consistent hashing or sharding');
    }
    
    return {
        applicable: true,
        syncOverhead,
        challenges,
        recommendations,
        estimatedLatency: calculateDistributedLatency(config)
    };
}

function calculateSyncOverhead(strategy, nodes) {
    const baseOverhead = {
        'local-only': 0,
        'periodic-sync': 5,
        'real-time-sync': 20,
        'consensus': 50,
        'gossip': 15
    };
    
    return (baseOverhead[strategy] || 10) * Math.log(nodes);
}

function calculateDistributedLatency(config) {
    const baseLatency = config.targetLatency;
    const nodeLatency = Math.log(config.distributedNodes) * 2;
    const syncLatency = calculateSyncOverhead(config.syncStrategy, config.distributedNodes);
    
    return baseLatency + nodeLatency + syncLatency;
}

function generateRateLimitingRecommendations(config, algorithmAnalysis, distributedAnalysis) {
    const recommendations = [];
    
    / Algorithm-specific recommendations
    if (algorithmAnalysis.acceptanceRate < 80) {
        recommendations.push({
            type: 'algorithm',
            priority: 'high',
            title: 'Low acceptance rate detected',
            description: 'Consider increasing rate limits or switching to more burst-tolerant algorithm',
            actions: ['Review rate limit settings', 'Consider token bucket algorithm', 'Implement adaptive limits']
        });
    }
    
    if (algorithmAnalysis.burstHandling < 70) {
        recommendations.push({
            type: 'performance',
            priority: 'medium',
            title: 'Poor burst handling',
            description: 'Algorithm struggles with traffic bursts',
            actions: ['Increase bucket capacity', 'Implement queueing', 'Add burst credits']
        });
    }
    
    / Distributed recommendations
    if (distributedAnalysis.applicable && distributedAnalysis.estimatedLatency > config.targetLatency * 2) {
        recommendations.push({
            type: 'distributed',
            priority: 'high',
            title: 'High distributed latency',
            description: 'Distributed setup adds significant latency overhead',
            actions: ['Optimize synchronization strategy', 'Use local quotas', 'Consider edge-based limiting']
        });
    }
    
    / Storage recommendations
    if (config.storageBackend === 'database' && config.avgRequestRate > 1000) {
        recommendations.push({
            type: 'storage',
            priority: 'medium',
            title: 'Database storage may be bottleneck',
            description: 'High request rate with database storage can cause performance issues',
            actions: ['Switch to Redis', 'Use in-memory cache', 'Implement write-through caching']
        });
    }
    
    return recommendations;
}

function generateRateLimitingResults(results) {
    const { config, traffic, algorithm, distributed, recommendations } = results;
    
    return `
        <h3>🚦 Rate Limiting Analysis</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                ${algorithm.algorithm.replace('-', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}
                <div style="font-size: 0.4em; margin-top: 10px;">
                    ${config.rateLimitScope} scope | ${config.distributedNodes} nodes
                </div>
            </div>
            <div class="performance-summary">
                <div class="perf-item">
                    <span class="perf-label">Acceptance Rate:</span>
                    <span class="perf-value ${algorithm.acceptanceRate >= 90 ? 'good' : algorithm.acceptanceRate >= 70 ? 'warning' : 'critical'}">
                        ${algorithm.acceptanceRate.toFixed(1)}%
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Burst Handling:</span>
                    <span class="perf-value ${algorithm.burstHandling >= 80 ? 'good' : 'warning'}">
                        ${algorithm.burstHandling.toFixed(1)}%
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Latency:</span>
                    <span class="perf-value ${algorithm.latencyOverhead <= config.targetLatency ? 'good' : 'warning'}">
                        ${algorithm.latencyOverhead}ms
                    </span>
                </div>
            </div>
        </div>
        
        <div class="analysis-grid">
            <div class="analysis-card">
                <h4>📊 Traffic Analysis</h4>
                <div class="metric-row">
                    <span>Avg Rate:</span>
                    <span>${Math.round(traffic.avgRate)} req/sec</span>
                </div>
                <div class="metric-row">
                    <span>Max Rate:</span>
                    <span>${Math.round(traffic.maxRate)} req/sec</span>
                </div>
                <div class="metric-row">
                    <span>Burst Frequency:</span>
                    <span>${(traffic.burstFrequency * 100).toFixed(1)}%</span>
                </div>
                <div class="metric-row">
                    <span>Variance:</span>
                    <span>${Math.round(traffic.variance)} req/sec</span>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>⚙️ Algorithm Performance</h4>
                <div class="metric-row">
                    <span>Total Requests:</span>
                    <span>${algorithm.totalRequests.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span>Accepted:</span>
                    <span class="good">${algorithm.acceptedRequests.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span>Rejected:</span>
                    <span class="warning">${algorithm.rejectedRequests.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span>Memory Usage:</span>
                    <span>${algorithm.memoryUsage}</span>
                </div>
            </div>
            
            ${distributed.applicable ? `
            <div class="analysis-card">
                <h4>🌐 Distributed Analysis</h4>
                <div class="metric-row">
                    <span>Sync Overhead:</span>
                    <span class="${distributed.syncOverhead <= 10 ? 'good' : 'warning'}">${distributed.syncOverhead}ms</span>
                </div>
                <div class="metric-row">
                    <span>Est. Latency:</span>
                    <span class="${distributed.estimatedLatency <= config.targetLatency * 2 ? 'good' : 'warning'}">${distributed.estimatedLatency}ms</span>
                </div>
                <div class="metric-row">
                    <span>Challenges:</span>
                    <span class="${distributed.challenges.length === 0 ? 'good' : 'warning'}">${distributed.challenges.length}</span>
                </div>
            </div>
            ` : ''}
        </div>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Algorithm Performance Comparison</h4>
                <canvas id="algorithmChart" width="600" height="300"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Traffic vs Acceptance Rate</h4>
                <canvas id="performanceChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <h4>💡 Recommendations</h4>
        <div class="recommendations-grid">
            ${recommendations.map(rec => `
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
            `).join('')}
        </div>
        
        <h4>📋 Implementation Checklist</h4>
        <div class="implementation-checklist">
            ${generateImplementationChecklist(config, algorithm)}
        </div>
    `;
}

function generateImplementationChecklist(config, algorithm) {
    const checklist = [
        'Define rate limit policies per user tier',
        'Implement monitoring and alerting',
        'Add rate limit headers to responses',
        'Design graceful degradation strategy',
        'Test with realistic traffic patterns',
        'Document rate limit policies for clients',
        'Implement bypass mechanism for emergencies',
        'Set up log analysis for rate limit effectiveness'
    ];
    
    / Add algorithm-specific items
    switch (config.rateLimitAlgorithm) {
        case 'token-bucket':
            checklist.push('Configure bucket refill rates carefully');
            checklist.push('Handle bucket state persistence');
            break;
        case 'sliding-window-log':
            checklist.push('Implement efficient log cleanup');
            checklist.push('Monitor memory usage for request logs');
            break;
        case 'distributed-consistent':
            checklist.push('Set up distributed state synchronization');
            checklist.push('Handle network partition scenarios');
            break;
    }
    
    return checklist.map(item => `
        <div class="checklist-item">
            <input type="checkbox" id="check-${item.replace(/\\s+/g, '-')}" />
            <label for="check-${item.replace(/\\s+/g, '-')}">${item}</label>
        </div>
    `).join('');
}

function displayRateLimitingErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawAlgorithmChart(algorithmAnalysis) {
    const ctx = document.getElementById('algorithmChart');
    if (!ctx) return;
    
    if (algorithmChart) {
        algorithmChart.destroy();
    }
    
    / Compare current algorithm with others
    const algorithms = Object.keys(algorithmSpecs);
    const accuracyData = algorithms.map(alg => algorithmSpecs[alg].accuracy);
    const burstToleranceData = algorithms.map(alg => algorithmSpecs[alg].burstTolerance);
    const latencyData = algorithms.map(alg => algorithmSpecs[alg].latencyOverhead);
    
    algorithmChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: algorithms.map(alg => algorithmSpecs[alg].name),
            datasets: [
                {
                    label: 'Accuracy',
                    data: accuracyData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Burst Tolerance',
                    data: burstToleranceData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Algorithm Characteristics'
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function drawPerformanceChart(trafficAnalysis, algorithmAnalysis) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trafficAnalysis.timePoints,
            datasets: [
                {
                    label: 'Request Rate (req/sec)',
                    data: trafficAnalysis.requestRates,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Acceptance Rate (%)',
                    data: algorithmAnalysis.simulation.acceptanceRates,
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4
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
                        text: 'Time (minutes)'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Request Rate (req/sec)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Acceptance Rate (%)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

function simulateTraffic() {
    alert('Traffic simulation will model various attack patterns and evaluate rate limiting effectiveness under different scenarios.');
}

function compareAlgorithms() {
    / Generate comparison data
    const config = getRateLimitingConfiguration();
    const trafficAnalysis = analyzeTrafficPatterns(config);
    
    const algorithms = ['token-bucket', 'sliding-window-counter', 'fixed-window'];
    const comparisonData = algorithms.map(alg => {
        const tempConfig = { ...config, rateLimitAlgorithm: alg };
        const analysis = analyzeAlgorithmPerformance(tempConfig, trafficAnalysis);
        return {
            name: algorithmSpecs[alg].name,
            acceptanceRate: analysis.acceptanceRate,
            burstHandling: analysis.burstHandling,
            latency: analysis.latencyOverhead,
            memory: analysis.memoryUsage
        };
    });
    
    / Display comparison results
    let comparisonHTML = `
        <div class="comparison-results">
            <h3>🔄 Algorithm Comparison</h3>
            <table class="responsive-table">
                <thead>
                    <tr>
                        <th>Algorithm</th>
                        <th>Acceptance Rate</th>
                        <th>Burst Handling</th>
                        <th>Latency</th>
                        <th>Memory</th>
                    </tr>
                </thead>
                <tbody>
                    ${comparisonData.map(data => `
                        <tr>
                            <td data-label="Algorithm">${data.name}</td>
                            <td data-label="Acceptance Rate">${data.acceptanceRate.toFixed(1)}%</td>
                            <td data-label="Burst Handling">${data.burstHandling.toFixed(1)}%</td>
                            <td data-label="Latency">${data.latency}ms</td>
                            <td data-label="Memory">${data.memory}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('results').innerHTML = comparisonHTML;
}

function exportRateLimitingResults() {
    const config = getRateLimitingConfiguration();
    const results = {
        timestamp: new Date().toISOString(),
        configuration: config,
        analysis: 'Detailed analysis results would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rate-limiting-analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/ Initialize algorithm config visibility
document.addEventListener('DOMContentLoaded', function() {
    toggleAlgorithmConfig();
});
</script>

<style>
.calculator-tool {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.algorithm-selection {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border: 1px solid #ddd;
}

.algorithm-config {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
    border: 1px solid #e9ecef;
}

.algorithm-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.algorithm-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.algorithm-formula {
    background: #2d3748;
    color: #e2e8f0;
    padding: 10px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    margin-top: 10px;
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

.recommendation-card.algorithm {
    border-left-color: #e74c3c;
}

.recommendation-card.performance {
    border-left-color: #f39c12;
}

.recommendation-card.distributed {
    border-left-color: #9b59b6;
}

.recommendation-card.storage {
    border-left-color: #2ecc71;
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

.implementation-checklist {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.checklist-item {
    display: flex;
    align-items: center;
    margin: 10px 0;
    padding: 8px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e9ecef;
}

.checklist-item input[type="checkbox"] {
    margin-right: 10px;
    transform: scale(1.2);
}

.checklist-item label {
    margin: 0;
    cursor: pointer;
    flex-grow: 1;
}

.comparison-results {
    background: white;
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
    
    .performance-summary {
        grid-template-columns: 1fr;
    }
    
    .analysis-grid,
    .algorithm-grid {
        grid-template-columns: 1fr;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    .rec-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    
    .checklist-item {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .checklist-item input[type="checkbox"] {
        margin-bottom: 5px;
    }
}
</style>

</div>