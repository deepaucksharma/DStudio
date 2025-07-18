// Coordination Cost Estimator
class CoordinationCostEstimator {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.scalingCanvas = null;
    this.scalingCtx = null;
    this.nodes = [];
    this.edges = [];
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupCalculator());
    } else {
      this.setupCalculator();
    }
  }
  
  setupCalculator() {
    const form = document.getElementById('coordination-calc');
    if (!form) return;
    
    // Set up event listeners
    form.addEventListener('input', () => this.calculateCosts());
    
    // Handle connectivity factor slider
    const slider = document.getElementById('connectivity-factor');
    const valueDisplay = document.getElementById('connectivity-value');
    if (slider && valueDisplay) {
      slider.addEventListener('input', (e) => {
        valueDisplay.textContent = `${Math.round(e.target.value * 100)}%`;
        this.calculateCosts();
      });
    }
    
    // Handle topology type changes
    const topologySelect = document.getElementById('topology-type');
    const connectivityGroup = document.querySelector('.input-group:has(#connectivity-factor)');
    if (topologySelect && connectivityGroup) {
      topologySelect.addEventListener('change', (e) => {
        connectivityGroup.style.display = e.target.value === 'partial-mesh' ? 'block' : 'none';
        this.calculateCosts();
      });
    }
    
    // Initialize visualization
    this.initVisualization();
    
    // Initial calculation
    this.calculateCosts();
  }
  
  initVisualization() {
    const vizContainer = document.getElementById('coordination-visualization');
    if (!vizContainer) return;
    
    // Create main network visualization
    this.canvas = document.createElement('canvas');
    this.canvas.width = 800;
    this.canvas.height = 400;
    this.ctx = this.canvas.getContext('2d');
    vizContainer.appendChild(this.canvas);
    
    // Get scaling chart canvas
    this.scalingCanvas = document.getElementById('scaling-chart');
    if (this.scalingCanvas) {
      this.scalingCtx = this.scalingCanvas.getContext('2d');
    }
    
    // Handle canvas resize
    window.addEventListener('resize', () => {
      const containerWidth = vizContainer.offsetWidth;
      if (containerWidth > 0) {
        this.canvas.width = Math.min(containerWidth, 800);
        this.calculateCosts();
      }
    });
  }
  
  calculateCosts() {
    // Get input values
    const nodeCount = parseInt(document.getElementById('node-count').value) || 5;
    const topologyType = document.getElementById('topology-type').value;
    const connectivityFactor = parseFloat(document.getElementById('connectivity-factor').value) || 0.3;
    const consensusType = document.getElementById('consensus-type').value;
    const messageSize = parseInt(document.getElementById('message-size').value) || 1024;
    const coordinationFrequency = parseFloat(document.getElementById('coordination-frequency').value) || 10;
    const networkLatency = parseFloat(document.getElementById('network-latency').value) || 5;
    const bandwidthPerLink = parseInt(document.getElementById('bandwidth-per-link').value) || 1000;
    const failureRate = parseFloat(document.getElementById('failure-rate').value) / 100 || 0.001;
    
    // Calculate number of edges based on topology
    let edgeCount = this.calculateEdgeCount(nodeCount, topologyType, connectivityFactor);
    
    // Calculate messages per operation based on consensus algorithm
    const messagesPerOp = this.calculateMessagesPerOperation(nodeCount, consensusType);
    
    // Calculate total messages per second
    const totalMessagesPerSecond = messagesPerOp * coordinationFrequency * (1 + failureRate);
    
    // Calculate bandwidth usage (in Mbps)
    const bandwidthUsageBits = totalMessagesPerSecond * messageSize * 8;
    const bandwidthUsageMbps = bandwidthUsageBits / 1_000_000;
    
    // Calculate coordination latency
    const consensusRounds = this.getConsensusRounds(consensusType);
    const coordinationLatency = networkLatency * consensusRounds * (1 + failureRate);
    
    // Calculate overhead percentage (bandwidth used vs available)
    const totalAvailableBandwidth = edgeCount * bandwidthPerLink;
    const overheadPercent = (bandwidthUsageMbps / totalAvailableBandwidth) * 100;
    
    // Update visualization
    this.drawNetworkTopology(nodeCount, topologyType, connectivityFactor);
    this.drawScalingChart(topologyType, consensusType);
    
    // Display results
    this.displayResults({
      totalMessagesPerSecond,
      bandwidthUsageMbps,
      coordinationLatency,
      overheadPercent,
      nodeCount,
      edgeCount,
      topologyType,
      consensusType,
      messagesPerOp,
      failureRate
    });
  }
  
  calculateEdgeCount(nodeCount, topology, connectivityFactor) {
    switch (topology) {
      case 'full-mesh':
        return (nodeCount * (nodeCount - 1)) / 2;
      case 'star':
        return nodeCount - 1;
      case 'ring':
        return nodeCount;
      case 'tree':
        return nodeCount - 1;
      case 'partial-mesh':
        const maxEdges = (nodeCount * (nodeCount - 1)) / 2;
        return Math.floor(maxEdges * connectivityFactor);
      default:
        return nodeCount;
    }
  }
  
  calculateMessagesPerOperation(nodeCount, consensusType) {
    switch (consensusType) {
      case 'none':
        return 0;
      case '2pc':
        return 3 * nodeCount;
      case '3pc':
        return 5 * nodeCount;
      case 'paxos':
        return 4 * nodeCount; // Simplified average
      case 'raft':
        return 2 * nodeCount;
      case 'pbft':
        return 3 * nodeCount * nodeCount; // O(n²)
      default:
        return nodeCount;
    }
  }
  
  getConsensusRounds(consensusType) {
    const rounds = {
      'none': 0,
      '2pc': 2,
      '3pc': 3,
      'paxos': 2,
      'raft': 2,
      'pbft': 3
    };
    return rounds[consensusType] || 1;
  }
  
  drawNetworkTopology(nodeCount, topology, connectivityFactor) {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Limit visualization to reasonable number of nodes
    const displayNodes = Math.min(nodeCount, 20);
    
    // Generate node positions based on topology
    this.nodes = this.generateNodePositions(displayNodes, topology, width, height);
    this.edges = this.generateEdges(displayNodes, topology, connectivityFactor);
    
    // Draw edges
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;
    this.edges.forEach(edge => {
      const node1 = this.nodes[edge[0]];
      const node2 = this.nodes[edge[1]];
      ctx.beginPath();
      ctx.moveTo(node1.x, node1.y);
      ctx.lineTo(node2.x, node2.y);
      ctx.stroke();
    });
    
    // Draw nodes
    this.nodes.forEach((node, index) => {
      // Node circle
      ctx.fillStyle = node.isHub ? '#5448C8' : '#00BCD4';
      ctx.beginPath();
      ctx.arc(node.x, node.y, 15, 0, 2 * Math.PI);
      ctx.fill();
      
      // Node label
      ctx.fillStyle = 'white';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(index + 1, node.x, node.y);
    });
    
    // Draw title
    ctx.fillStyle = '#111827';
    ctx.font = '16px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(`${this.getTopologyName(topology)} Topology (${nodeCount} nodes)`, width/2, 30);
    
    if (nodeCount > displayNodes) {
      ctx.fillStyle = '#6B7280';
      ctx.font = '12px Inter';
      ctx.fillText(`Showing first ${displayNodes} nodes`, width/2, height - 20);
    }
  }
  
  generateNodePositions(nodeCount, topology, width, height) {
    const nodes = [];
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;
    
    switch (topology) {
      case 'star':
        // Central hub
        nodes.push({ x: centerX, y: centerY, isHub: true });
        // Surrounding nodes
        for (let i = 1; i < nodeCount; i++) {
          const angle = (i - 1) * (2 * Math.PI / (nodeCount - 1));
          nodes.push({
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
            isHub: false
          });
        }
        break;
        
      case 'ring':
      case 'full-mesh':
      case 'partial-mesh':
        // Circular arrangement
        for (let i = 0; i < nodeCount; i++) {
          const angle = i * (2 * Math.PI / nodeCount);
          nodes.push({
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
            isHub: false
          });
        }
        break;
        
      case 'tree':
        // Hierarchical layout
        const levels = Math.ceil(Math.log2(nodeCount + 1));
        let nodeIndex = 0;
        
        for (let level = 0; level < levels && nodeIndex < nodeCount; level++) {
          const nodesInLevel = Math.pow(2, level);
          const levelY = 80 + level * ((height - 120) / (levels - 1));
          
          for (let i = 0; i < nodesInLevel && nodeIndex < nodeCount; i++) {
            const levelX = (i + 0.5) * (width / nodesInLevel);
            nodes.push({
              x: levelX,
              y: levelY,
              isHub: level === 0
            });
            nodeIndex++;
          }
        }
        break;
        
      default:
        // Grid layout fallback
        const cols = Math.ceil(Math.sqrt(nodeCount));
        for (let i = 0; i < nodeCount; i++) {
          const row = Math.floor(i / cols);
          const col = i % cols;
          nodes.push({
            x: 100 + col * ((width - 200) / (cols - 1)),
            y: 100 + row * ((height - 200) / (Math.ceil(nodeCount / cols) - 1)),
            isHub: false
          });
        }
    }
    
    return nodes;
  }
  
  generateEdges(nodeCount, topology, connectivityFactor) {
    const edges = [];
    
    switch (topology) {
      case 'star':
        // Connect all nodes to hub (node 0)
        for (let i = 1; i < nodeCount; i++) {
          edges.push([0, i]);
        }
        break;
        
      case 'ring':
        // Connect each node to next
        for (let i = 0; i < nodeCount; i++) {
          edges.push([i, (i + 1) % nodeCount]);
        }
        break;
        
      case 'full-mesh':
        // Connect every node to every other node
        for (let i = 0; i < nodeCount; i++) {
          for (let j = i + 1; j < nodeCount; j++) {
            edges.push([i, j]);
          }
        }
        break;
        
      case 'partial-mesh':
        // Randomly connect nodes based on connectivity factor
        const maxEdges = (nodeCount * (nodeCount - 1)) / 2;
        const targetEdges = Math.floor(maxEdges * connectivityFactor);
        const possibleEdges = [];
        
        for (let i = 0; i < nodeCount; i++) {
          for (let j = i + 1; j < nodeCount; j++) {
            possibleEdges.push([i, j]);
          }
        }
        
        // Shuffle and take required number
        for (let i = possibleEdges.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [possibleEdges[i], possibleEdges[j]] = [possibleEdges[j], possibleEdges[i]];
        }
        
        edges.push(...possibleEdges.slice(0, targetEdges));
        break;
        
      case 'tree':
        // Binary tree connections
        for (let i = 0; i < nodeCount; i++) {
          const leftChild = 2 * i + 1;
          const rightChild = 2 * i + 2;
          
          if (leftChild < nodeCount) edges.push([i, leftChild]);
          if (rightChild < nodeCount) edges.push([i, rightChild]);
        }
        break;
    }
    
    return edges;
  }
  
  getTopologyName(topology) {
    const names = {
      'full-mesh': 'Full Mesh',
      'star': 'Star',
      'ring': 'Ring',
      'tree': 'Tree',
      'partial-mesh': 'Partial Mesh'
    };
    return names[topology] || topology;
  }
  
  drawScalingChart(topology, consensusType) {
    if (!this.scalingCanvas || !this.scalingCtx) return;
    
    const ctx = this.scalingCtx;
    const width = this.scalingCanvas.width;
    const height = this.scalingCanvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw axes
    const padding = 50;
    ctx.strokeStyle = '#4B5563';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // Calculate scaling curves
    const maxNodes = 100;
    const nodeRange = Array.from({length: 20}, (_, i) => (i + 1) * 5);
    
    // Draw curves for different topologies
    const topologies = ['star', 'ring', 'partial-mesh', 'full-mesh'];
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'];
    
    topologies.forEach((topo, index) => {
      ctx.strokeStyle = colors[index];
      ctx.lineWidth = topo === topology ? 3 : 2;
      ctx.globalAlpha = topo === topology ? 1 : 0.5;
      ctx.beginPath();
      
      nodeRange.forEach((nodes, i) => {
        const messages = this.calculateMessagesPerOperation(nodes, consensusType);
        const edges = this.calculateEdgeCount(nodes, topo, 0.3);
        const cost = messages * Math.log(edges + 1); // Simplified cost model
        
        const x = padding + (i / (nodeRange.length - 1)) * (width - 2 * padding);
        const y = height - padding - (Math.log(cost + 1) / Math.log(1000)) * (height - 2 * padding);
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.stroke();
      ctx.globalAlpha = 1;
    });
    
    // Draw legend
    ctx.font = '12px Inter';
    topologies.forEach((topo, index) => {
      ctx.fillStyle = colors[index];
      ctx.fillRect(width - 150, 20 + index * 20, 15, 15);
      ctx.fillStyle = '#4B5563';
      ctx.textAlign = 'left';
      ctx.fillText(this.getTopologyName(topo), width - 130, 30 + index * 20);
    });
    
    // Labels
    ctx.fillStyle = '#4B5563';
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Number of Nodes', width / 2, height - 10);
    
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Coordination Cost (log scale)', 0, 0);
    ctx.restore();
    
    // Title
    ctx.font = '16px Inter';
    ctx.fillStyle = '#111827';
    ctx.textAlign = 'center';
    ctx.fillText(`Scaling Analysis - ${this.getConsensusName(consensusType)}`, width / 2, 30);
  }
  
  getConsensusName(consensus) {
    const names = {
      'none': 'No Consensus',
      '2pc': 'Two-Phase Commit',
      '3pc': 'Three-Phase Commit',
      'paxos': 'Paxos',
      'raft': 'Raft',
      'pbft': 'PBFT'
    };
    return names[consensus] || consensus;
  }
  
  displayResults(data) {
    // Update main metrics
    document.getElementById('total-messages').textContent = 
      data.totalMessagesPerSecond >= 1000 ? 
      `${(data.totalMessagesPerSecond/1000).toFixed(1)}k` : 
      data.totalMessagesPerSecond.toFixed(0);
    
    document.getElementById('bandwidth-usage').textContent = 
      data.bandwidthUsageMbps >= 1000 ?
      `${(data.bandwidthUsageMbps/1000).toFixed(1)} Gbps` :
      `${data.bandwidthUsageMbps.toFixed(1)} Mbps`;
    
    document.getElementById('coord-latency').textContent = `${data.coordinationLatency.toFixed(1)} ms`;
    document.getElementById('overhead-percent').textContent = `${data.overheadPercent.toFixed(1)}%`;
    
    // Generate insights
    const insights = this.generateInsights(data);
    const insightsList = document.getElementById('coordination-insights');
    if (insightsList) {
      insightsList.innerHTML = insights.map(insight => `<li>${insight}</li>`).join('');
    }
    
    // Generate algorithm comparison
    this.generateAlgorithmComparison(data);
  }
  
  generateInsights(data) {
    const insights = [];
    
    // Message volume insights
    if (data.totalMessagesPerSecond > 10000) {
      insights.push('Very high message volume - consider batching or reducing coordination frequency');
    } else if (data.totalMessagesPerSecond > 1000) {
      insights.push('Moderate message volume - monitor network capacity');
    }
    
    // Bandwidth insights
    if (data.overheadPercent > 50) {
      insights.push('High bandwidth utilization - network may become a bottleneck');
    } else if (data.overheadPercent > 20) {
      insights.push('Significant bandwidth usage - consider message compression');
    }
    
    // Latency insights
    if (data.coordinationLatency > 100) {
      insights.push('High coordination latency - consider eventual consistency');
    } else if (data.coordinationLatency > 50) {
      insights.push('Moderate latency - may impact user experience');
    }
    
    // Topology insights
    if (data.topologyType === 'full-mesh' && data.nodeCount > 10) {
      insights.push('Full mesh with many nodes creates O(n²) connections - consider partial mesh');
    } else if (data.topologyType === 'star') {
      insights.push('Star topology creates a single point of failure at the hub');
    }
    
    // Consensus insights
    if (data.consensusType === 'pbft' && data.nodeCount > 10) {
      insights.push('PBFT has O(n²) message complexity - consider using only for small clusters');
    } else if (data.consensusType === 'none') {
      insights.push('No consensus algorithm - ensure application can handle inconsistencies');
    }
    
    // Scaling insights
    const scalingFactor = data.messagesPerOp / data.nodeCount;
    if (scalingFactor > data.nodeCount) {
      insights.push(`Quadratic scaling detected - coordination costs grow as O(n²)`);
    } else if (scalingFactor > 1) {
      insights.push(`Linear scaling - coordination costs grow as O(n)`);
    }
    
    return insights;
  }
  
  generateAlgorithmComparison(currentData) {
    const container = document.getElementById('algorithm-comparison');
    if (!container) return;
    
    const algorithms = ['none', '2pc', '3pc', 'paxos', 'raft', 'pbft'];
    const comparisons = [];
    
    algorithms.forEach(algo => {
      const messages = this.calculateMessagesPerOperation(currentData.nodeCount, algo);
      const rounds = this.getConsensusRounds(algo);
      const latency = currentData.networkLatency * rounds * (1 + currentData.failureRate);
      
      comparisons.push({
        algorithm: this.getConsensusName(algo),
        messages,
        latency,
        isCurrent: algo === currentData.consensusType
      });
    });
    
    // Sort by message count
    comparisons.sort((a, b) => a.messages - b.messages);
    
    // Generate comparison display
    container.innerHTML = comparisons.map(comp => {
      const messageBar = Math.min((comp.messages / comparisons[comparisons.length-1].messages) * 100, 100);
      const latencyBar = Math.min((comp.latency / comparisons[comparisons.length-1].latency) * 100, 100);
      const highlightClass = comp.isCurrent ? 'highlight' : '';
      
      return `
        <div class="algorithm-comparison-item ${highlightClass}">
          <h5>${comp.algorithm}</h5>
          <div class="comparison-metrics">
            <div class="metric-row">
              <span class="metric-label">Messages:</span>
              <span class="metric-value">${comp.messages}</span>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${messageBar}%"></div>
              </div>
            </div>
            <div class="metric-row">
              <span class="metric-label">Latency:</span>
              <span class="metric-value">${comp.latency.toFixed(1)}ms</span>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${latencyBar}%"></div>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }
}

// Initialize calculator
const coordinationCostEstimator = new CoordinationCostEstimator();