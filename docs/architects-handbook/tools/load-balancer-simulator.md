---
title: Load Balancer Simulator
description: Algorithm comparison, health check impact, connection pooling simulation
type: documentation
---

# Load Balancer Simulator

!!! info "Advanced Load Balancing Analysis"
    <h2>⚖️ Load Balancer Algorithm Simulator</h2>
    <p>Simulate and compare load balancing algorithms with real-time traffic patterns, health checks, and connection pooling analysis.</p>

## Interactive Simulator

<div class="calculator-tool">
<form id="loadBalancerCalc">

### Infrastructure Configuration

<label for="numServers">Number of backend servers:</label>
<input type="number" id="numServers" value="5" min="2" max="50" step="1">
*Backend server instances*

<label for="serverCapacity">Server capacity (req/sec):</label>
<input type="number" id="serverCapacity" value="1000" min="100" step="100">
*Maximum requests per second per server*

<div class="server-config">
<h4>🖥️ Server Heterogeneity</h4>
<label for="serverVariation">Server capacity variation:</label>
<select id="serverVariation">
<option value="uniform">Uniform (all servers identical)</option>
<option value="slight">Slight variation (±10%)</option>
<option value="moderate">Moderate variation (±25%)</option>
<option value="high">High variation (±50%)</option>
<option value="mixed">Mixed (small + large instances)</option>
</select>

<label for="serverLocations">Server locations:</label>
<select id="serverLocations">
<option value="single-dc">Single data center</option>
<option value="multi-az">Multiple availability zones</option>
<option value="multi-region">Multiple regions</option>
<option value="edge-locations">Edge locations</option>
</select>
</div>

### Load Balancing Algorithms

<div class="algorithm-selection">
<h4>📊 Algorithm Configuration</h4>

<label for="primaryAlgorithm">Primary algorithm:</label>
<select id="primaryAlgorithm">
<option value="round-robin">Round Robin</option>
<option value="weighted-round-robin">Weighted Round Robin</option>
<option value="least-connections">Least Connections</option>
<option value="weighted-least-connections">Weighted Least Connections</option>
<option value="least-response-time">Least Response Time</option>
<option value="ip-hash">IP Hash</option>
<option value="consistent-hash">Consistent Hashing</option>
<option value="random">Random</option>
<option value="power-of-two">Power of Two Choices</option>
<option value="adaptive">Adaptive Load Balancing</option>
</select>

<div id="weightedConfig" class="algorithm-config" style="display: none;">
<h5>Weighted Configuration</h5>
<div id="serverWeights">
<!-- Dynamic server weight inputs will be added here -->
</div>
</div>

<div id="hashConfig" class="algorithm-config" style="display: none;">
<h5>Hash Configuration</h5>
<label for="hashFunction">Hash function:</label>
<select id="hashFunction">
<option value="md5">MD5</option>
<option value="sha1">SHA-1</option>
<option value="sha256">SHA-256</option>
<option value="murmur">MurmurHash</option>
<option value="consistent">Consistent Hash Ring</option>
</select>

<label for="virtualNodes">Virtual nodes (for consistent hashing):</label>
<input type="number" id="virtualNodes" value="150" min="50" max="500" step="10">
</div>

<div id="adaptiveConfig" class="algorithm-config" style="display: none;">
<h5>Adaptive Configuration</h5>
<label for="adaptiveMetric">Primary metric:</label>
<select id="adaptiveMetric">
<option value="response-time">Response time</option>
<option value="cpu-utilization">CPU utilization</option>
<option value="memory-usage">Memory usage</option>
<option value="active-connections">Active connections</option>
<option value="composite">Composite score</option>
</select>

<label for="adaptationSpeed">Adaptation speed:</label>
<select id="adaptationSpeed">
<option value="slow">Slow (conservative)</option>
<option value="moderate">Moderate</option>
<option value="fast">Fast (reactive)</option>
</select>
</div>
</div>

### Traffic Patterns

<label for="requestRate">Average request rate (req/sec):</label>
<input type="number" id="requestRate" value="5000" min="100" step="100">
*Baseline request rate*

<label for="trafficPattern">Traffic pattern:</label>
<select id="trafficPattern">
<option value="steady">Steady state</option>
<option value="bursty">Bursty (sudden spikes)</option>
<option value="periodic">Periodic waves</option>
<option value="gradual-increase">Gradual increase</option>
<option value="flash-crowd">Flash crowd event</option>
<option value="mixed">Mixed patterns</option>
</select>

<label for="sessionAffinity">Session affinity:</label>
<select id="sessionAffinity">
<option value="none">No affinity</option>
<option value="cookie">Cookie-based</option>
<option value="ip">IP-based</option>
<option value="session-id">Session ID</option>
</select>

<label for="keepAlive">Connection keep-alive:</label>
<select id="keepAlive">
<option value="disabled">Disabled</option>
<option value="short">Short (1-5 seconds)</option>
<option value="medium">Medium (30 seconds)</option>
<option value="long">Long (5 minutes)</option>
</select>

### Health Checks & Failover

<div class="health-check-config">
<h4>🏥 Health Check Configuration</h4>

<label for="healthCheckEnabled">Health checks:</label>
<select id="healthCheckEnabled">
<option value="enabled">Enabled</option>
<option value="disabled">Disabled</option>
</select>

<div id="healthCheckDetails">
<label for="healthCheckInterval">Check interval (seconds):</label>
<input type="number" id="healthCheckInterval" value="30" min="1" max="300" step="1">

<label for="healthCheckTimeout">Check timeout (seconds):</label>
<input type="number" id="healthCheckTimeout" value="5" min="1" max="30" step="1">

<label for="failureThreshold">Failure threshold:</label>
<input type="number" id="failureThreshold" value="3" min="1" max="10" step="1">
*Consecutive failures before marking unhealthy*

<label for="healthCheckType">Health check type:</label>
<select id="healthCheckType">
<option value="http">HTTP GET</option>
<option value="tcp">TCP connection</option>
<option value="ping">ICMP ping</option>
<option value="custom">Custom script</option>
</select>

<label for="failoverStrategy">Failover strategy:</label>
<select id="failoverStrategy">
<option value="immediate">Immediate removal</option>
<option value="graceful">Graceful draining</option>
<option value="retry">Retry with backoff</option>
</select>
</div>
</div>

### Performance Requirements

<label for="targetLatency">Target P95 latency (ms):</label>
<input type="number" id="targetLatency" value="100" min="1" step="1">
*95th percentile response time*

<label for="maxConnections">Max concurrent connections:</label>
<input type="number" id="maxConnections" value="10000" min="100" step="100">
*Connection pool limit*

<label for="connectionTimeout">Connection timeout (seconds):</label>
<input type="number" id="connectionTimeout" value="30" min="1" max="300" step="1">
*Client connection timeout*

<button type="button" onclick="simulateLoadBalancer()" class="calc-button">Run Simulation</button>
<button type="button" onclick="compareAlgorithms()" class="compare-button">Compare Algorithms</button>
<button type="button" onclick="stressTestScenario()" class="stress-button">Stress Test</button>
<button type="button" onclick="exportLoadBalancerResults()" class="export-button">Export Results</button>
</form>

<div id="results" class="results-panel">
<!-- Results will appear here -->
</div>

## Understanding Load Balancing Algorithms

### Algorithm Comparison Matrix

<table class="responsive-table">
<thead>
<tr>
<th>Algorithm</th>
<th>Distribution</th>
<th>Server State</th>
<th>Session Affinity</th>
<th>Complexity</th>
<th>Best Use Case</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Algorithm">Round Robin</td>
<td data-label="Distribution">Even</td>
<td data-label="Server State">Stateless</td>
<td data-label="Session Affinity">None</td>
<td data-label="Complexity">O(1)</td>
<td data-label="Best Use Case">Identical servers</td>
</tr>
<tr>
<td data-label="Algorithm">Weighted Round Robin</td>
<td data-label="Distribution">Proportional</td>
<td data-label="Server State">Semi-stateful</td>
<td data-label="Session Affinity">Limited</td>
<td data-label="Complexity">O(1)</td>
<td data-label="Best Use Case">Different server capacities</td>
</tr>
<tr>
<td data-label="Algorithm">Least Connections</td>
<td data-label="Distribution">Dynamic</td>
<td data-label="Server State">Stateful</td>
<td data-label="Session Affinity">Poor</td>
<td data-label="Complexity">O(n)</td>
<td data-label="Best Use Case">Long-lived connections</td>
</tr>
<tr>
<td data-label="Algorithm">Least Response Time</td>
<td data-label="Distribution">Performance-based</td>
<td data-label="Server State">Stateful</td>
<td data-label="Session Affinity">Poor</td>
<td data-label="Complexity">O(n)</td>
<td data-label="Best Use Case">Variable response times</td>
</tr>
<tr>
<td data-label="Algorithm">IP Hash</td>
<td data-label="Distribution">Deterministic</td>
<td data-label="Server State">Stateless</td>
<td data-label="Session Affinity">Excellent</td>
<td data-label="Complexity">O(1)</td>
<td data-label="Best Use Case">Session persistence</td>
</tr>
<tr>
<td data-label="Algorithm">Consistent Hashing</td>
<td data-label="Distribution">Consistent</td>
<td data-label="Server State">Stateless</td>
<td data-label="Session Affinity">Good</td>
<td data-label="Complexity">O(log n)</td>
<td data-label="Best Use Case">Dynamic server pools</td>
</tr>
<tr>
<td data-label="Algorithm">Power of Two</td>
<td data-label="Distribution">Near-optimal</td>
<td data-label="Server State">Stateful</td>
<td data-label="Session Affinity">Poor</td>
<td data-label="Complexity">O(1)</td>
<td data-label="Best Use Case">High-throughput systems</td>
</tr>
</tbody>
</table>

### Load Balancing Patterns

<div class="pattern-grid">
<div class="pattern-card">
<h4>🔄 Layer 4 (Transport)</h4>
<ul>
<li>Operates at TCP/UDP level</li>
<li>Fast forwarding decisions</li>
<li>Source/destination IP and port</li>
<li>No application awareness</li>
</ul>
<p><strong>Latency:</strong> 1-5ms | <strong>Throughput:</strong> Very High</p>
</div>

<div class="pattern-card">
<h4>🌐 Layer 7 (Application)</h4>
<ul>
<li>HTTP/HTTPS content inspection</li>
<li>Path-based routing</li>
<li>SSL termination</li>
<li>Request modification</li>
</ul>
<p><strong>Latency:</strong> 10-50ms | <strong>Features:</strong> Rich</p>
</div>

<div class="pattern-card">
<h4>🔗 Connection Pooling</h4>
<ul>
<li>Reuse persistent connections</li>
<li>Reduce connection overhead</li>
<li>Multiplexing support</li>
<li>Connection limits</li>
</ul>
<p><strong>Efficiency:</strong> High | <strong>Resource Usage:</strong> Optimized</p>
</div>

<div class="pattern-card">
<h4>📍 Geographic Routing</h4>
<ul>
<li>Route by client location</li>
<li>Minimize network latency</li>
<li>Data residency compliance</li>
<li>CDN integration</li>
</ul>
<p><strong>Global:</strong> Yes | <strong>Latency:</strong> Minimized</p>
</div>
</div>

### Failover Strategies

<div class="strategy-card">
<div>
<h4>⚡ Immediate Failover</h4>
<ul>
<li>Instant server removal on failure</li>
<li>Fast recovery time</li>
<li>Potential request loss</li>
<li>Simple implementation</li>
</ul>
<p><strong>RTO:</strong> < 1 second</p>
</div>

<div>
<h4>🌊 Graceful Draining</h4>
<ul>
<li>Complete existing connections</li>
<li>No new requests to failed server</li>
<li>Zero request loss</li>
<li>Longer recovery time</li>
</ul>
<p><strong>RTO:</strong> 30-60 seconds</p>
</div>

<div>
<h4>🔄 Circuit Breaker</h4>
<ul>
<li>Automatic failure detection</li>
<li>Temporary request blocking</li>
<li>Gradual recovery testing</li>
<li>Prevents cascade failures</li>
</ul>
<p><strong>Self-healing:</strong> Yes</p>
</div>

<div>
<h4>🎯 Active Health Checks</h4>
<ul>
<li>Proactive server monitoring</li>
<li>Custom health endpoints</li>
<li>Configurable check intervals</li>
<li>Multi-metric evaluation</li>
</ul>
<p><strong>Detection Time:</strong> Configurable</p>
</div>
</div>

## Related Resources

- [Availability Calculator](availability-calculator.md)
- [Throughput Calculator](throughput-calculator.md)
- [Rate Limiting Calculator](rate-limiting-calculator.md)
- [Load Balancing Patterns](../../pattern-library/scaling/load-balancing.md)

<script src="https:/cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let distributionChart = null;
let performanceChart = null;
let latencyChart = null;
let comparisonChart = null;

/ Algorithm implementations and characteristics
const algorithms = {
    'round-robin': {
        name: 'Round Robin',
        stateful: false,
        complexity: 'O(1)',
        sessionAffinity: 'none',
        implementation: (servers, currentIndex) => (currentIndex + 1) % servers.length
    },
    'weighted-round-robin': {
        name: 'Weighted Round Robin',
        stateful: true,
        complexity: 'O(1)',
        sessionAffinity: 'limited',
        implementation: (servers, state) => {
            / Simplified weighted implementation
            state.weightedIndex = (state.weightedIndex || 0) + 1;
            let totalWeight = servers.reduce((sum, server) => sum + server.weight, 0);
            let currentWeight = state.weightedIndex % totalWeight;
            
            let cumulativeWeight = 0;
            for (let i = 0; i < servers.length; i++) {
                cumulativeWeight += servers[i].weight;
                if (currentWeight < cumulativeWeight) {
                    return i;
                }
            }
            return 0;
        }
    },
    'least-connections': {
        name: 'Least Connections',
        stateful: true,
        complexity: 'O(n)',
        sessionAffinity: 'poor',
        implementation: (servers) => {
            let minConnections = Math.min(...servers.map(s => s.activeConnections));
            return servers.findIndex(s => s.activeConnections === minConnections);
        }
    },
    'weighted-least-connections': {
        name: 'Weighted Least Connections',
        stateful: true,
        complexity: 'O(n)',
        sessionAffinity: 'poor',
        implementation: (servers) => {
            let minRatio = Math.min(...servers.map(s => s.activeConnections / s.weight));
            return servers.findIndex(s => (s.activeConnections / s.weight) === minRatio);
        }
    },
    'least-response-time': {
        name: 'Least Response Time',
        stateful: true,
        complexity: 'O(n)',
        sessionAffinity: 'poor',
        implementation: (servers) => {
            let minResponseTime = Math.min(...servers.map(s => s.avgResponseTime));
            return servers.findIndex(s => s.avgResponseTime === minResponseTime);
        }
    },
    'ip-hash': {
        name: 'IP Hash',
        stateful: false,
        complexity: 'O(1)',
        sessionAffinity: 'excellent',
        implementation: (servers, clientIP) => {
            const hash = simpleHash(clientIP);
            return hash % servers.length;
        }
    },
    'consistent-hash': {
        name: 'Consistent Hashing',
        stateful: false,
        complexity: 'O(log n)',
        sessionAffinity: 'good',
        implementation: (servers, clientIP, virtualNodes = 150) => {
            const hash = simpleHash(clientIP);
            / Simplified consistent hashing
            const ring = [];
            servers.forEach((server, index) => {
                for (let i = 0; i < virtualNodes; i++) {
                    ring.push({ hash: simpleHash(`${index}-${i}`), serverIndex: index });
                }
            });
            ring.sort((a, b) => a.hash - b.hash);
            
            for (let node of ring) {
                if (node.hash >= hash) {
                    return node.serverIndex;
                }
            }
            return ring[0].serverIndex;
        }
    },
    'random': {
        name: 'Random',
        stateful: false,
        complexity: 'O(1)',
        sessionAffinity: 'none',
        implementation: (servers) => Math.floor(Math.random() * servers.length)
    },
    'power-of-two': {
        name: 'Power of Two Choices',
        stateful: true,
        complexity: 'O(1)',
        sessionAffinity: 'poor',
        implementation: (servers) => {
            const choice1 = Math.floor(Math.random() * servers.length);
            const choice2 = Math.floor(Math.random() * servers.length);
            
            if (servers[choice1].activeConnections <= servers[choice2].activeConnections) {
                return choice1;
            }
            return choice2;
        }
    },
    'adaptive': {
        name: 'Adaptive Load Balancing',
        stateful: true,
        complexity: 'O(n)',
        sessionAffinity: 'poor',
        implementation: (servers, metric = 'response-time') => {
            / Calculate composite score based on multiple metrics
            const scores = servers.map((server, index) => {
                let score = 0;
                switch (metric) {
                    case 'response-time':
                        score = 1 / (server.avgResponseTime + 1);
                        break;
                    case 'cpu-utilization':
                        score = 1 - (server.cpuUsage / 100);
                        break;
                    case 'active-connections':
                        score = 1 / (server.activeConnections + 1);
                        break;
                    case 'composite':
                        score = (1 / (server.avgResponseTime + 1)) * 
                               (1 - server.cpuUsage / 100) * 
                               (1 / (server.activeConnections + 1));
                        break;
                }
                return { index, score };
            });
            
            scores.sort((a, b) => b.score - a.score);
            return scores[0].index;
        }
    }
};

/ Show/hide algorithm-specific configurations
document.getElementById('primaryAlgorithm').addEventListener('change', function() {
    const algorithm = this.value;
    
    / Hide all configs
    document.querySelectorAll('.algorithm-config').forEach(config => {
        config.style.display = 'none';
    });
    
    / Show relevant config
    if (algorithm.includes('weighted')) {
        document.getElementById('weightedConfig').style.display = 'block';
        updateServerWeights();
    } else if (algorithm.includes('hash')) {
        document.getElementById('hashConfig').style.display = 'block';
    } else if (algorithm === 'adaptive') {
        document.getElementById('adaptiveConfig').style.display = 'block';
    }
});

/ Update server weight inputs when server count changes
document.getElementById('numServers').addEventListener('change', function() {
    if (document.getElementById('primaryAlgorithm').value.includes('weighted')) {
        updateServerWeights();
    }
});

function updateServerWeights() {
    const numServers = parseInt(document.getElementById('numServers').value);
    const container = document.getElementById('serverWeights');
    container.innerHTML = '';
    
    for (let i = 1; i <= numServers; i++) {
        const weightDiv = document.createElement('div');
        weightDiv.className = 'server-weight';
        weightDiv.innerHTML = `
            <label for="server${i}Weight">Server ${i} weight:</label>
            <input type="number" id="server${i}Weight" value="1" min="1" max="10" step="1">
        `;
        container.appendChild(weightDiv);
    }
}

function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; / Convert to 32-bit integer
    }
    return Math.abs(hash);
}

function validateLoadBalancerInputs() {
    const inputs = {
        numServers: { value: parseInt(document.getElementById('numServers').value), min: 2, max: 50, name: 'Number of servers' },
        serverCapacity: { value: parseInt(document.getElementById('serverCapacity').value), min: 100, name: 'Server capacity' },
        requestRate: { value: parseInt(document.getElementById('requestRate').value), min: 100, name: 'Request rate' },
        targetLatency: { value: parseInt(document.getElementById('targetLatency').value), min: 1, name: 'Target latency' },
        maxConnections: { value: parseInt(document.getElementById('maxConnections').value), min: 100, name: 'Max connections' }
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
    
    / Check if total server capacity can handle request rate
    const totalCapacity = inputs.numServers.value * inputs.serverCapacity.value;
    if (inputs.requestRate.value > totalCapacity * 0.8) {
        errors.push('Request rate exceeds 80% of total server capacity');
    }
    
    return { valid: errors.length === 0, errors, inputs };
}

function simulateLoadBalancer() {
    const validation = validateLoadBalancerInputs();
    if (!validation.valid) {
        displayLoadBalancerErrors(validation.errors);
        return;
    }
    
    const config = getLoadBalancerConfiguration();
    const servers = initializeServers(config);
    const trafficPattern = generateTrafficPattern(config);
    const simulationResults = runSimulation(config, servers, trafficPattern);
    const performanceAnalysis = analyzePerformance(simulationResults, config);
    const recommendations = generateLoadBalancerRecommendations(config, performanceAnalysis);
    
    const results = {
        config,
        servers,
        traffic: trafficPattern,
        simulation: simulationResults,
        performance: performanceAnalysis,
        recommendations
    };
    
    let resultsHTML = generateLoadBalancerResults(results);
    document.getElementById('results').innerHTML = resultsHTML;
    
    / Draw charts
    setTimeout(() => {
        drawDistributionChart(simulationResults);
        drawPerformanceChart(trafficPattern, simulationResults);
        drawLatencyChart(simulationResults);
    }, 100);
}

function getLoadBalancerConfiguration() {
    const config = {
        numServers: parseInt(document.getElementById('numServers').value),
        serverCapacity: parseInt(document.getElementById('serverCapacity').value),
        serverVariation: document.getElementById('serverVariation').value,
        serverLocations: document.getElementById('serverLocations').value,
        primaryAlgorithm: document.getElementById('primaryAlgorithm').value,
        requestRate: parseInt(document.getElementById('requestRate').value),
        trafficPattern: document.getElementById('trafficPattern').value,
        sessionAffinity: document.getElementById('sessionAffinity').value,
        keepAlive: document.getElementById('keepAlive').value,
        healthCheckEnabled: document.getElementById('healthCheckEnabled').value === 'enabled',
        healthCheckInterval: parseInt(document.getElementById('healthCheckInterval').value),
        healthCheckTimeout: parseInt(document.getElementById('healthCheckTimeout').value),
        failureThreshold: parseInt(document.getElementById('failureThreshold').value),
        healthCheckType: document.getElementById('healthCheckType').value,
        failoverStrategy: document.getElementById('failoverStrategy').value,
        targetLatency: parseInt(document.getElementById('targetLatency').value),
        maxConnections: parseInt(document.getElementById('maxConnections').value),
        connectionTimeout: parseInt(document.getElementById('connectionTimeout').value)
    };
    
    / Add algorithm-specific configuration
    if (config.primaryAlgorithm.includes('weighted')) {
        config.serverWeights = [];
        for (let i = 1; i <= config.numServers; i++) {
            const weightInput = document.getElementById(`server${i}Weight`);
            config.serverWeights.push(weightInput ? parseInt(weightInput.value) : 1);
        }
    }
    
    if (config.primaryAlgorithm.includes('hash')) {
        config.hashFunction = document.getElementById('hashFunction').value;
        config.virtualNodes = parseInt(document.getElementById('virtualNodes').value);
    }
    
    if (config.primaryAlgorithm === 'adaptive') {
        config.adaptiveMetric = document.getElementById('adaptiveMetric').value;
        config.adaptationSpeed = document.getElementById('adaptationSpeed').value;
    }
    
    return config;
}

function initializeServers(config) {
    const servers = [];
    
    for (let i = 0; i < config.numServers; i++) {
        let capacity = config.serverCapacity;
        
        / Apply capacity variation
        switch (config.serverVariation) {
            case 'slight':
                capacity *= (0.9 + Math.random() * 0.2); / ±10%
                break;
            case 'moderate':
                capacity *= (0.75 + Math.random() * 0.5); / ±25%
                break;
            case 'high':
                capacity *= (0.5 + Math.random() * 1.0); / ±50%
                break;
            case 'mixed':
                capacity *= i < config.numServers / 2 ? 0.5 : 1.5; / Small and large instances
                break;
        }
        
        / Add location-based latency
        let baseLatency = 5; / 5ms base latency
        switch (config.serverLocations) {
            case 'multi-az':
                baseLatency += Math.random() * 10; / +0-10ms
                break;
            case 'multi-region':
                baseLatency += Math.random() * 50; / +0-50ms
                break;
            case 'edge-locations':
                baseLatency += Math.random() * 20; / +0-20ms
                break;
        }
        
        servers.push({
            id: i,
            capacity: Math.round(capacity),
            baseLatency,
            activeConnections: 0,
            totalRequests: 0,
            avgResponseTime: baseLatency,
            cpuUsage: 0,
            memoryUsage: 0,
            healthy: true,
            weight: config.serverWeights ? config.serverWeights[i] : 1,
            requestHistory: [],
            failureCount: 0
        });
    }
    
    return servers;
}

function generateTrafficPattern(config) {
    const duration = 300; / 5-minute simulation
    const timePoints = [];
    const requestRates = [];
    const clientIPs = [];
    
    / Generate unique client IPs for session affinity testing
    const numClients = Math.min(1000, config.requestRate);
    const uniqueIPs = [];
    for (let i = 0; i < numClients; i++) {
        uniqueIPs.push(`192.168.${Math.floor(i/254)}.${i%254}`);
    }
    
    for (let t = 0; t < duration; t++) {
        timePoints.push(t);
        
        let rate = config.requestRate;
        
        / Apply traffic pattern
        switch (config.trafficPattern) {
            case 'bursty':
                / Random bursts
                if (Math.random() < 0.1) {
                    rate *= (2 + Math.random() * 3); / 2x to 5x burst
                }
                break;
                
            case 'periodic':
                / Sine wave pattern
                rate *= (1 + 0.5 * Math.sin(t / 30));
                break;
                
            case 'gradual-increase':
                / Linear increase
                rate *= (1 + t / duration);
                break;
                
            case 'flash-crowd':
                / Single large spike
                if (t >= 150 && t <= 180) {
                    rate *= 5;
                }
                break;
                
            case 'mixed':
                / Combination of patterns
                rate *= (1 + 0.3 * Math.sin(t / 20) + (Math.random() < 0.05 ? 2 : 0));
                break;
        }
        
        requestRates.push(Math.round(rate));
        
        / Generate client IPs for this time period
        const timeClientIPs = [];
        for (let i = 0; i < Math.min(rate / 10, uniqueIPs.length); i++) {
            timeClientIPs.push(uniqueIPs[Math.floor(Math.random() * uniqueIPs.length)]);
        }
        clientIPs.push(timeClientIPs);
    }
    
    return { timePoints, requestRates, clientIPs };
}

function runSimulation(config, servers, trafficPattern) {
    const algorithm = algorithms[config.primaryAlgorithm];
    const results = {
        serverMetrics: servers.map(s => ({ ...s, requestCounts: [], latencies: [], utilizationHistory: [] })),
        overallMetrics: {
            totalRequests: 0,
            averageLatency: 0,
            p95Latency: 0,
            p99Latency: 0,
            errorRate: 0,
            throughput: []
        },
        distributionHistory: []
    };
    
    let state = {}; / For stateful algorithms
    
    trafficPattern.timePoints.forEach((t, timeIndex) => {
        const requestsThisSecond = trafficPattern.requestRates[timeIndex];
        const clientIPs = trafficPattern.clientIPs[timeIndex];
        
        let secondRequests = [];
        let secondLatencies = [];
        
        / Process requests for this time period
        for (let reqIndex = 0; reqIndex < requestsThisSecond; reqIndex++) {
            const clientIP = clientIPs[reqIndex % clientIPs.length] || '192.168.1.1';
            
            / Select server using the algorithm
            let serverIndex;
            try {
                if (algorithm.implementation) {
                    if (config.primaryAlgorithm === 'consistent-hash') {
                        serverIndex = algorithm.implementation(
                            results.serverMetrics.filter(s => s.healthy),
                            clientIP,
                            config.virtualNodes
                        );
                    } else if (config.primaryAlgorithm.includes('hash')) {
                        serverIndex = algorithm.implementation(
                            results.serverMetrics.filter(s => s.healthy),
                            clientIP
                        );
                    } else {
                        serverIndex = algorithm.implementation(
                            results.serverMetrics.filter(s => s.healthy),
                            state
                        );
                    }
                } else {
                    serverIndex = 0; / Fallback
                }
            } catch (e) {
                serverIndex = 0; / Fallback on error
            }
            
            / Ensure serverIndex is valid
            serverIndex = Math.max(0, Math.min(serverIndex, results.serverMetrics.length - 1));
            
            const server = results.serverMetrics[serverIndex];
            
            / Check if server can handle request
            if (server.healthy && server.activeConnections < server.capacity) {
                / Process request
                const latency = calculateRequestLatency(server, config);
                
                server.activeConnections++;
                server.totalRequests++;
                secondRequests.push(serverIndex);
                secondLatencies.push(latency);
                
                / Update server metrics
                server.requestCounts[timeIndex] = (server.requestCounts[timeIndex] || 0) + 1;
                server.latencies.push(latency);
                server.avgResponseTime = server.latencies.reduce((sum, l) => sum + l, 0) / server.latencies.length;
                
                / Update utilization
                server.cpuUsage = Math.min(100, (server.activeConnections / server.capacity) * 100);
                server.utilizationHistory[timeIndex] = server.cpuUsage;
                
                / Connection cleanup (simplified)
                setTimeout(() => {
                    if (server.activeConnections > 0) {
                        server.activeConnections--;
                    }
                }, latency);
                
            } else {
                / Request failed - server overloaded or unhealthy
                results.overallMetrics.errorRate++;
            }
        }
        
        / Update overall metrics
        results.overallMetrics.totalRequests += requestsThisSecond;
        results.overallMetrics.throughput.push(secondRequests.length);
        
        / Calculate distribution for this time period
        const distribution = Array(config.numServers).fill(0);
        secondRequests.forEach(serverIndex => {
            distribution[serverIndex]++;
        });
        results.distributionHistory.push(distribution);
        
        / Simulate health checks
        if (config.healthCheckEnabled && t % config.healthCheckInterval === 0) {
            simulateHealthChecks(results.serverMetrics, config);
        }
    });
    
    / Calculate final metrics
    const allLatencies = results.serverMetrics.flatMap(s => s.latencies);
    if (allLatencies.length > 0) {
        allLatencies.sort((a, b) => a - b);
        results.overallMetrics.averageLatency = allLatencies.reduce((sum, l) => sum + l, 0) / allLatencies.length;
        results.overallMetrics.p95Latency = allLatencies[Math.floor(allLatencies.length * 0.95)];
        results.overallMetrics.p99Latency = allLatencies[Math.floor(allLatencies.length * 0.99)];
    }
    
    results.overallMetrics.errorRate = (results.overallMetrics.errorRate / results.overallMetrics.totalRequests) * 100;
    
    return results;
}

function calculateRequestLatency(server, config) {
    / Base latency from server location
    let latency = server.baseLatency;
    
    / Add processing time based on current load
    const loadFactor = server.activeConnections / server.capacity;
    latency += loadFactor * 20; / Up to 20ms additional latency under full load
    
    / Add network jitter
    latency += Math.random() * 5;
    
    / Connection pooling benefits
    if (config.keepAlive !== 'disabled') {
        const keepAliveReduction = config.keepAlive === 'short' ? 0.1 : 
                                  config.keepAlive === 'medium' ? 0.2 : 0.3;
        latency *= (1 - keepAliveReduction);
    }
    
    return Math.max(1, latency); / Minimum 1ms latency
}

function simulateHealthChecks(servers, config) {
    servers.forEach(server => {
        / Simulate health check failure based on server utilization
        const failureProb = Math.max(0, (server.cpuUsage - 80) / 20 * 0.1); / Higher failure chance at high utilization
        
        if (Math.random() < failureProb) {
            server.failureCount++;
            if (server.failureCount >= config.failureThreshold) {
                server.healthy = false;
            }
        } else {
            server.failureCount = Math.max(0, server.failureCount - 1);
            if (server.failureCount === 0 && !server.healthy) {
                server.healthy = true; / Recovery
            }
        }
    });
}

function analyzePerformance(simulationResults, config) {
    const metrics = simulationResults.overallMetrics;
    const serverMetrics = simulationResults.serverMetrics;
    
    / Calculate distribution balance
    const requestCounts = serverMetrics.map(s => s.totalRequests);
    const maxRequests = Math.max(...requestCounts);
    const minRequests = Math.min(...requestCounts);
    const balance = minRequests / maxRequests;
    
    / Calculate server utilization stats
    const avgUtilizations = serverMetrics.map(s => 
        s.utilizationHistory.reduce((sum, u) => sum + (u || 0), 0) / s.utilizationHistory.length
    );
    const maxUtilization = Math.max(...avgUtilizations);
    const avgUtilization = avgUtilizations.reduce((sum, u) => sum + u, 0) / avgUtilizations.length;
    
    / Performance scoring
    const latencyScore = metrics.p95Latency <= config.targetLatency ? 100 : 
                        Math.max(0, 100 - (metrics.p95Latency - config.targetLatency) / config.targetLatency * 100);
    
    const throughputScore = metrics.errorRate <= 1 ? 100 : Math.max(0, 100 - metrics.errorRate * 10);
    
    const balanceScore = balance * 100;
    
    const overallScore = (latencyScore + throughputScore + balanceScore) / 3;
    
    return {
        latencyScore,
        throughputScore,
        balanceScore,
        overallScore,
        balance,
        maxUtilization,
        avgUtilization,
        healthyServers: serverMetrics.filter(s => s.healthy).length,
        bottlenecks: identifyBottlenecks(serverMetrics, config)
    };
}

function identifyBottlenecks(serverMetrics, config) {
    const bottlenecks = [];
    
    / High utilization servers
    const highUtilServers = serverMetrics.filter(s => 
        s.utilizationHistory.some(u => u > 90)
    );
    if (highUtilServers.length > 0) {
        bottlenecks.push(`${highUtilServers.length} servers experiencing high utilization (>90%)`);
    }
    
    / Unhealthy servers
    const unhealthyServers = serverMetrics.filter(s => !s.healthy);
    if (unhealthyServers.length > 0) {
        bottlenecks.push(`${unhealthyServers.length} servers are currently unhealthy`);
    }
    
    / Load imbalance
    const requestCounts = serverMetrics.map(s => s.totalRequests);
    const maxRequests = Math.max(...requestCounts);
    const minRequests = Math.min(...requestCounts);
    if (maxRequests > minRequests * 2) {
        bottlenecks.push('Significant load imbalance detected between servers');
    }
    
    return bottlenecks;
}

function generateLoadBalancerRecommendations(config, performance) {
    const recommendations = [];
    
    / Performance recommendations
    if (performance.latencyScore < 70) {
        recommendations.push({
            category: 'Latency',
            priority: 'High',
            title: 'High latency detected',
            description: 'P95 latency exceeds target requirements',
            actions: [
                'Consider adding more server instances',
                'Optimize application response times',
                'Implement connection pooling',
                'Use faster server instances'
            ]
        });
    }
    
    if (performance.throughputScore < 70) {
        recommendations.push({
            category: 'Throughput',
            priority: 'High',
            title: 'High error rate detected',
            description: 'Servers are rejecting too many requests',
            actions: [
                'Increase server capacity',
                'Implement auto-scaling',
                'Add circuit breaker patterns',
                'Optimize resource allocation'
            ]
        });
    }
    
    if (performance.balanceScore < 70) {
        recommendations.push({
            category: 'Balance',
            priority: 'Medium',
            title: 'Load distribution imbalance',
            description: 'Requests are not evenly distributed across servers',
            actions: [
                'Review load balancing algorithm choice',
                'Consider weighted algorithms for heterogeneous servers',
                'Check for session affinity issues',
                'Implement consistent hashing for better distribution'
            ]
        });
    }
    
    / Health check recommendations
    if (performance.healthyServers < config.numServers) {
        recommendations.push({
            category: 'Reliability',
            priority: 'High',
            title: 'Server health issues',
            description: 'Some servers are marked as unhealthy',
            actions: [
                'Investigate root cause of server failures',
                'Adjust health check sensitivity',
                'Implement graceful degradation',
                'Add automatic server replacement'
            ]
        });
    }
    
    return recommendations;
}

function generateLoadBalancerResults(results) {
    const { config, simulation, performance, recommendations } = results;
    const algorithm = algorithms[config.primaryAlgorithm];
    
    return `
        <h3>⚖️ Load Balancer Simulation Results</h3>
        
        <div class="big-metric">
            <div class="metric-value">
                ${algorithm.name}
                <div style="font-size: 0.4em; margin-top: 10px;">
                    ${config.numServers} servers | ${config.trafficPattern} traffic
                </div>
            </div>
            <div class="performance-summary">
                <div class="perf-item">
                    <span class="perf-label">Performance Score:</span>
                    <span class="perf-value ${performance.overallScore >= 80 ? 'good' : performance.overallScore >= 60 ? 'warning' : 'critical'}">
                        ${performance.overallScore.toFixed(0)}/100
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">P95 Latency:</span>
                    <span class="perf-value ${simulation.overallMetrics.p95Latency <= config.targetLatency ? 'good' : 'warning'}">
                        ${simulation.overallMetrics.p95Latency.toFixed(1)}ms
                    </span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">Error Rate:</span>
                    <span class="perf-value ${simulation.overallMetrics.errorRate <= 1 ? 'good' : 'warning'}">
                        ${simulation.overallMetrics.errorRate.toFixed(2)}%
                    </span>
                </div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metrics-card">
                <h4>📊 Traffic Metrics</h4>
                <div class="metric-row">
                    <span>Total Requests:</span>
                    <span>${simulation.overallMetrics.totalRequests.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                    <span>Average Latency:</span>
                    <span>${simulation.overallMetrics.averageLatency.toFixed(2)}ms</span>
                </div>
                <div class="metric-row">
                    <span>P99 Latency:</span>
                    <span>${simulation.overallMetrics.p99Latency.toFixed(2)}ms</span>
                </div>
                <div class="metric-row">
                    <span>Peak Throughput:</span>
                    <span>${Math.max(...simulation.overallMetrics.throughput).toLocaleString()} req/s</span>
                </div>
            </div>
            
            <div class="metrics-card">
                <h4>🎯 Distribution Analysis</h4>
                <div class="metric-row">
                    <span>Load Balance Score:</span>
                    <span class="${performance.balanceScore >= 80 ? 'good' : performance.balanceScore >= 60 ? 'warning' : 'critical'}">
                        ${performance.balanceScore.toFixed(1)}/100
                    </span>
                </div>
                <div class="metric-row">
                    <span>Max Server Utilization:</span>
                    <span class="${performance.maxUtilization <= 80 ? 'good' : 'warning'}">
                        ${performance.maxUtilization.toFixed(1)}%
                    </span>
                </div>
                <div class="metric-row">
                    <span>Healthy Servers:</span>
                    <span class="${performance.healthyServers === config.numServers ? 'good' : 'warning'}">
                        ${performance.healthyServers}/${config.numServers}
                    </span>
                </div>
            </div>
            
            <div class="metrics-card">
                <h4>⚙️ Algorithm Properties</h4>
                <div class="metric-row">
                    <span>Complexity:</span>
                    <span>${algorithm.complexity}</span>
                </div>
                <div class="metric-row">
                    <span>Session Affinity:</span>
                    <span>${algorithm.sessionAffinity}</span>
                </div>
                <div class="metric-row">
                    <span>State Required:</span>
                    <span>${algorithm.stateful ? 'Yes' : 'No'}</span>
                </div>
            </div>
        </div>
        
        <h4>🖥️ Server Performance</h4>
        <table class="responsive-table">
            <thead>
                <tr>
                    <th>Server</th>
                    <th>Requests Handled</th>
                    <th>Avg Latency</th>
                    <th>Peak Utilization</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${simulation.serverMetrics.map(server => `
                    <tr>
                        <td data-label="Server">Server ${server.id + 1}</td>
                        <td data-label="Requests">${server.totalRequests.toLocaleString()}</td>
                        <td data-label="Latency">${server.avgResponseTime.toFixed(2)}ms</td>
                        <td data-label="Utilization" class="${Math.max(...(server.utilizationHistory || [0])) <= 80 ? 'good' : 'warning'}">
                            ${Math.max(...(server.utilizationHistory || [0])).toFixed(1)}%
                        </td>
                        <td data-label="Status" class="${server.healthy ? 'good' : 'critical'}">
                            ${server.healthy ? '✅ Healthy' : '❌ Unhealthy'}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Request Distribution</h4>
                <canvas id="distributionChart" width="600" height="300"></canvas>
            </div>
            
            <div class="chart-section">
                <h4>Performance Over Time</h4>
                <canvas id="performanceChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-section">
                <h4>Latency Distribution</h4>
                <canvas id="latencyChart" width="600" height="300"></canvas>
            </div>
        </div>
        
        ${performance.bottlenecks.length > 0 ? `
        <h4>🚨 Identified Bottlenecks</h4>
        <div class="bottleneck-analysis">
            ${performance.bottlenecks.map(bottleneck => `
                <div class="bottleneck-item">⚠️ ${bottleneck}</div>
            `).join('')}
        </div>
        ` : ''}
        
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

function displayLoadBalancerErrors(errors) {
    const resultsDiv = document.getElementById('results');
    let errorHTML = '<div class="error-panel"><h3>❌ Validation Errors</h3><ul>';
    errors.forEach(error => {
        errorHTML += `<li>${error}</li>`;
    });
    errorHTML += '</ul></div>';
    resultsDiv.innerHTML = errorHTML;
}

function drawDistributionChart(simulationResults) {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;
    
    if (distributionChart) {
        distributionChart.destroy();
    }
    
    const serverLabels = simulationResults.serverMetrics.map((_, i) => `Server ${i + 1}`);
    const requestCounts = simulationResults.serverMetrics.map(s => s.totalRequests);
    
    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: serverLabels,
            datasets: [{
                label: 'Requests Handled',
                data: requestCounts,
                backgroundColor: requestCounts.map((count, i) => {
                    const maxCount = Math.max(...requestCounts);
                    const ratio = count / maxCount;
                    return ratio > 0.8 ? '#51cf66' : ratio > 0.5 ? '#ffd43b' : '#ff6b6b';
                }),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Request Distribution Across Servers'
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
                        text: 'Number of Requests'
                    }
                }
            }
        }
    });
}

function drawPerformanceChart(trafficPattern, simulationResults) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trafficPattern.timePoints,
            datasets: [
                {
                    label: 'Request Rate (req/sec)',
                    data: trafficPattern.requestRates,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Actual Throughput (req/sec)',
                    data: simulationResults.overallMetrics.throughput,
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y',
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
                        text: 'Time (seconds)'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Requests per Second'
                    }
                }
            }
        }
    });
}

function drawLatencyChart(simulationResults) {
    const ctx = document.getElementById('latencyChart');
    if (!ctx) return;
    
    if (latencyChart) {
        latencyChart.destroy();
    }
    
    / Collect all latencies and create histogram
    const allLatencies = simulationResults.serverMetrics.flatMap(s => s.latencies);
    const latencyBins = createLatencyHistogram(allLatencies);
    
    latencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: latencyBins.labels,
            datasets: [{
                label: 'Request Count',
                data: latencyBins.counts,
                backgroundColor: '#FFCE56',
                borderColor: '#FFB000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Latency Distribution'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Latency Range (ms)'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Requests'
                    }
                }
            }
        }
    });
}

function createLatencyHistogram(latencies) {
    if (latencies.length === 0) {
        return { labels: ['0-10ms'], counts: [0] };
    }
    
    const max = Math.max(...latencies);
    const binSize = Math.ceil(max / 10); / Create 10 bins
    const bins = [];
    const labels = [];
    
    for (let i = 0; i < 10; i++) {
        bins.push(0);
        const start = i * binSize;
        const end = (i + 1) * binSize;
        labels.push(`${start}-${end}ms`);
    }
    
    latencies.forEach(latency => {
        const binIndex = Math.min(Math.floor(latency / binSize), 9);
        bins[binIndex]++;
    });
    
    return { labels, counts: bins };
}

function compareAlgorithms() {
    const config = getLoadBalancerConfiguration();
    const algorithmNames = ['round-robin', 'least-connections', 'weighted-round-robin', 'ip-hash'];
    
    let comparisonHTML = `
        <div class="comparison-results">
            <h3>🔄 Load Balancing Algorithm Comparison</h3>
            <p>Comparison based on current configuration with ${config.numServers} servers and ${config.requestRate} req/sec</p>
            
            <table class="responsive-table">
                <thead>
                    <tr>
                        <th>Algorithm</th>
                        <th>Distribution Quality</th>
                        <th>Session Affinity</th>
                        <th>Complexity</th>
                        <th>Best For</th>
                    </tr>
                </thead>
                <tbody>
                    ${algorithmNames.map(algName => {
                        const alg = algorithms[algName];
                        return `
                            <tr>
                                <td data-label="Algorithm">${alg.name}</td>
                                <td data-label="Distribution">
                                    ${algName === 'round-robin' || algName === 'weighted-round-robin' ? 'Excellent' :
                                      algName === 'least-connections' ? 'Very Good' :
                                      algName === 'ip-hash' ? 'Good' : 'Variable'}
                                </td>
                                <td data-label="Session Affinity">${alg.sessionAffinity}</td>
                                <td data-label="Complexity">${alg.complexity}</td>
                                <td data-label="Best For">
                                    ${algName === 'round-robin' ? 'Uniform servers, stateless apps' :
                                      algName === 'weighted-round-robin' ? 'Different server capacities' :
                                      algName === 'least-connections' ? 'Long-lived connections' :
                                      algName === 'ip-hash' ? 'Session persistence' : 'General purpose'}
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    document.getElementById('results').innerHTML = comparisonHTML;
}

function stressTestScenario() {
    alert('Stress test will simulate extreme traffic scenarios including DDoS attacks, server failures, and traffic spikes to evaluate load balancer resilience.');
}

function exportLoadBalancerResults() {
    const config = getLoadBalancerConfiguration();
    const results = {
        timestamp: new Date().toISOString(),
        configuration: config,
        analysis: 'Load balancer simulation results would be exported here'
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'load-balancer-simulation.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/ Initialize configuration
document.addEventListener('DOMContentLoaded', function() {
    / Set up initial algorithm configuration
    document.getElementById('primaryAlgorithm').dispatchEvent(new Event('change'));
    
    / Set up health check toggle
    document.getElementById('healthCheckEnabled').addEventListener('change', function() {
        const healthCheckDetails = document.getElementById('healthCheckDetails');
        if (this.value === 'enabled') {
            healthCheckDetails.style.display = 'block';
        } else {
            healthCheckDetails.style.display = 'none';
        }
    });
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

.server-config,
.algorithm-selection,
.health-check-config {
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

.server-weight {
    display: grid;
    grid-template-columns: 1fr 100px;
    gap: 10px;
    align-items: center;
    margin: 10px 0;
}

.server-weight label {
    font-weight: bold;
}

.server-weight input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.calc-button, .compare-button, .stress-button, .export-button {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin: 10px 10px 10px 0;
}

.compare-button {
    background: #fd7e14;
}

.stress-button {
    background: #dc3545;
}

.export-button {
    background: #28a745;
}

.calc-button:hover {
    background: #0056b3;
}

.compare-button:hover {
    background: #e8590c;
}

.stress-button:hover {
    background: #c82333;
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

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.metrics-card {
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

.pattern-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.pattern-card {
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

.recommendation-card.latency {
    border-left-color: #e74c3c;
}

.recommendation-card.throughput {
    border-left-color: #f39c12;
}

.recommendation-card.balance {
    border-left-color: #9b59b6;
}

.recommendation-card.reliability {
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
    
    .server-weight {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .performance-summary {
        grid-template-columns: 1fr;
    }
    
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    .metrics-grid,
    .pattern-grid {
        grid-template-columns: 1fr;
    }
    
    .rec-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}
</style>

</div>