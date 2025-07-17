// Interactive Consistency Trade-off Visualizer
class ConsistencyVisualizer {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.nodes = [];
    this.messages = [];
    this.selectedMode = 'strong';
    this.animationSpeed = 1;
    this.isPlaying = false;
    this.animationId = null;
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupVisualizer());
    } else {
      this.setupVisualizer();
    }
  }
  
  setupVisualizer() {
    const container = document.getElementById('consistency-visualizer');
    if (!container) return;
    
    // Create UI controls
    this.createControls(container);
    
    // Create canvas
    const canvasContainer = document.createElement('div');
    canvasContainer.className = 'consistency-canvas-container';
    this.canvas = document.createElement('canvas');
    this.canvas.width = 800;
    this.canvas.height = 400;
    this.ctx = this.canvas.getContext('2d');
    canvasContainer.appendChild(this.canvas);
    container.appendChild(canvasContainer);
    
    // Initialize nodes
    this.initializeNodes();
    
    // Create results display
    this.createResultsDisplay(container);
    
    // Start animation
    this.animate();
    
    // Handle resize
    window.addEventListener('resize', () => {
      const containerWidth = canvasContainer.offsetWidth;
      if (containerWidth > 0) {
        this.canvas.width = Math.min(containerWidth, 800);
        this.initializeNodes();
      }
    });
  }
  
  createControls(container) {
    const controls = document.createElement('div');
    controls.className = 'consistency-controls';
    controls.innerHTML = `
      <div class="control-group">
        <label>Consistency Model:</label>
        <select id="consistency-mode" class="consistency-select">
          <option value="strong">Strong Consistency</option>
          <option value="eventual">Eventual Consistency</option>
          <option value="causal">Causal Consistency</option>
          <option value="weak">Weak Consistency</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>Animation Speed:</label>
        <input type="range" id="animation-speed" min="0.1" max="3" step="0.1" value="1" class="speed-slider">
        <span id="speed-value">1x</span>
      </div>
      
      <div class="control-group">
        <button id="play-pause" class="control-btn primary">▶️ Play</button>
        <button id="reset" class="control-btn">🔄 Reset</button>
      </div>
      
      <div class="scenario-buttons">
        <button class="scenario-btn" data-scenario="write">Write Operation</button>
        <button class="scenario-btn" data-scenario="concurrent">Concurrent Writes</button>
        <button class="scenario-btn" data-scenario="partition">Network Partition</button>
      </div>
    `;
    container.appendChild(controls);
    
    // Attach event listeners
    document.getElementById('consistency-mode').addEventListener('change', (e) => {
      this.selectedMode = e.target.value;
      this.reset();
    });
    
    document.getElementById('animation-speed').addEventListener('input', (e) => {
      this.animationSpeed = parseFloat(e.target.value);
      document.getElementById('speed-value').textContent = `${this.animationSpeed}x`;
    });
    
    document.getElementById('play-pause').addEventListener('click', () => {
      this.togglePlayPause();
    });
    
    document.getElementById('reset').addEventListener('click', () => {
      this.reset();
    });
    
    // Scenario buttons
    const scenarioButtons = controls.querySelectorAll('.scenario-btn');
    scenarioButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const scenario = e.target.dataset.scenario;
        this.runScenario(scenario);
      });
    });
  }
  
  initializeNodes() {
    const nodeCount = 3;
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const radius = Math.min(this.canvas.width, this.canvas.height) * 0.3;
    
    this.nodes = [];
    for (let i = 0; i < nodeCount; i++) {
      const angle = (i * 2 * Math.PI) / nodeCount - Math.PI / 2;
      this.nodes.push({
        id: i,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        value: 'A',
        version: 1,
        lastUpdate: 0,
        pending: false,
        color: '#10B981'
      });
    }
  }
  
  createResultsDisplay(container) {
    const results = document.createElement('div');
    results.className = 'consistency-results';
    results.innerHTML = `
      <h4>System State</h4>
      <div class="state-grid">
        <div class="state-item">
          <span class="state-label">Model:</span>
          <span class="state-value" id="current-model">Strong Consistency</span>
        </div>
        <div class="state-item">
          <span class="state-label">Latency:</span>
          <span class="state-value" id="latency-value">High</span>
        </div>
        <div class="state-item">
          <span class="state-label">Availability:</span>
          <span class="state-value" id="availability-value">Medium</span>
        </div>
        <div class="state-item">
          <span class="state-label">Consistency:</span>
          <span class="state-value" id="consistency-value">Strong</span>
        </div>
      </div>
      
      <div class="trade-offs">
        <h5>Trade-offs</h5>
        <div id="trade-off-bars">
          <div class="trade-off-bar">
            <span>Consistency</span>
            <div class="bar-track">
              <div class="bar-fill consistency-bar" style="width: 100%"></div>
            </div>
          </div>
          <div class="trade-off-bar">
            <span>Availability</span>
            <div class="bar-track">
              <div class="bar-fill availability-bar" style="width: 60%"></div>
            </div>
          </div>
          <div class="trade-off-bar">
            <span>Partition Tolerance</span>
            <div class="bar-track">
              <div class="bar-fill partition-bar" style="width: 80%"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="insights">
        <h5>💡 Insights</h5>
        <ul id="insights-list">
          <li>Strong consistency ensures all nodes see the same data at the same time</li>
          <li>Higher latency due to synchronization requirements</li>
          <li>May become unavailable during network partitions</li>
        </ul>
      </div>
    `;
    container.appendChild(results);
  }
  
  animate() {
    const draw = () => {
      this.drawVisualization();
      this.updateMessages();
      this.animationId = requestAnimationFrame(draw);
    };
    draw();
  }
  
  drawVisualization() {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw connections
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 2;
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        ctx.beginPath();
        ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
        ctx.lineTo(this.nodes[j].x, this.nodes[j].y);
        ctx.stroke();
      }
    }
    
    // Draw messages
    this.messages.forEach(msg => {
      const progress = (Date.now() - msg.startTime) / msg.duration;
      if (progress <= 1) {
        const x = msg.fromX + (msg.toX - msg.fromX) * progress;
        const y = msg.fromY + (msg.toY - msg.fromY) * progress;
        
        ctx.fillStyle = msg.color;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();
        
        // Draw value
        ctx.fillStyle = 'white';
        ctx.font = 'bold 10px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(msg.value, x, y);
      }
    });
    
    // Draw nodes
    this.nodes.forEach(node => {
      // Node circle
      ctx.fillStyle = node.pending ? '#F59E0B' : node.color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, 30, 0, 2 * Math.PI);
      ctx.fill();
      
      // Node border
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 3;
      ctx.stroke();
      
      // Node label
      ctx.fillStyle = 'white';
      ctx.font = 'bold 20px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.value, node.x, node.y);
      
      // Version number
      ctx.font = '12px Inter';
      ctx.fillText(`v${node.version}`, node.x, node.y + 40);
      
      // Node ID
      ctx.fillStyle = '#4B5563';
      ctx.fillText(`Node ${node.id + 1}`, node.x, node.y - 40);
    });
    
    // Clean up old messages
    this.messages = this.messages.filter(msg => 
      (Date.now() - msg.startTime) <= msg.duration
    );
  }
  
  updateMessages() {
    // Process arrived messages
    this.messages.forEach(msg => {
      const progress = (Date.now() - msg.startTime) / msg.duration;
      if (progress >= 1 && !msg.processed) {
        msg.processed = true;
        this.applyMessage(msg);
      }
    });
  }
  
  applyMessage(msg) {
    const node = this.nodes[msg.toNode];
    
    switch (this.selectedMode) {
      case 'strong':
        // Apply immediately and notify others
        node.value = msg.value;
        node.version = msg.version;
        node.pending = false;
        node.color = '#10B981';
        break;
        
      case 'eventual':
        // Apply with delay
        setTimeout(() => {
          if (msg.version > node.version) {
            node.value = msg.value;
            node.version = msg.version;
          }
          node.pending = false;
          node.color = '#10B981';
        }, Math.random() * 1000);
        break;
        
      case 'causal':
        // Apply if causally ready
        if (msg.version === node.version + 1) {
          node.value = msg.value;
          node.version = msg.version;
          node.pending = false;
          node.color = '#10B981';
        }
        break;
        
      case 'weak':
        // Apply immediately without coordination
        node.value = msg.value;
        node.version = Math.max(node.version, msg.version);
        node.pending = false;
        node.color = '#10B981';
        break;
    }
  }
  
  sendMessage(fromNode, toNode, value, version, color = '#3B82F6') {
    const from = this.nodes[fromNode];
    const to = this.nodes[toNode];
    
    // Calculate duration based on consistency model
    let duration = 500; // base duration
    if (this.selectedMode === 'strong') {
      duration *= 2; // Slower for strong consistency
    } else if (this.selectedMode === 'eventual') {
      duration *= 1.5;
    }
    
    duration /= this.animationSpeed;
    
    this.messages.push({
      fromNode,
      toNode,
      fromX: from.x,
      fromY: from.y,
      toX: to.x,
      toY: to.y,
      value,
      version,
      color,
      startTime: Date.now(),
      duration,
      processed: false
    });
  }
  
  runScenario(scenario) {
    this.reset();
    this.isPlaying = true;
    document.getElementById('play-pause').textContent = '⏸️ Pause';
    
    switch (scenario) {
      case 'write':
        this.runWriteScenario();
        break;
      case 'concurrent':
        this.runConcurrentScenario();
        break;
      case 'partition':
        this.runPartitionScenario();
        break;
    }
  }
  
  runWriteScenario() {
    // Node 0 writes 'B'
    const node0 = this.nodes[0];
    node0.pending = true;
    
    setTimeout(() => {
      node0.value = 'B';
      node0.version++;
      node0.pending = false;
      
      // Propagate based on consistency model
      if (this.selectedMode === 'strong') {
        // Synchronous replication
        node0.color = '#F59E0B'; // Orange while waiting
        this.sendMessage(0, 1, 'B', node0.version);
        this.sendMessage(0, 2, 'B', node0.version);
        
        // Wait for acknowledgments
        setTimeout(() => {
          node0.color = '#10B981'; // Green when confirmed
        }, 1000 / this.animationSpeed);
      } else {
        // Asynchronous replication
        node0.color = '#10B981';
        setTimeout(() => {
          this.sendMessage(0, 1, 'B', node0.version);
          this.sendMessage(0, 2, 'B', node0.version);
        }, 100);
      }
    }, 500 / this.animationSpeed);
  }
  
  runConcurrentScenario() {
    // Node 0 writes 'B', Node 1 writes 'C' simultaneously
    this.nodes[0].pending = true;
    this.nodes[1].pending = true;
    
    setTimeout(() => {
      // Both nodes update locally
      this.nodes[0].value = 'B';
      this.nodes[0].version++;
      this.nodes[1].value = 'C';
      this.nodes[1].version++;
      
      if (this.selectedMode === 'strong') {
        // Conflict - one must wait
        this.nodes[0].color = '#EF4444'; // Red for conflict
        this.nodes[1].color = '#EF4444';
        
        // Resolve conflict (node 0 wins)
        setTimeout(() => {
          this.nodes[1].value = 'B';
          this.nodes[1].version = this.nodes[0].version;
          this.sendMessage(0, 1, 'B', this.nodes[0].version);
          this.sendMessage(0, 2, 'B', this.nodes[0].version);
          
          setTimeout(() => {
            this.nodes.forEach(n => n.color = '#10B981');
          }, 1000 / this.animationSpeed);
        }, 500 / this.animationSpeed);
      } else {
        // Allow concurrent updates
        this.nodes[0].pending = false;
        this.nodes[1].pending = false;
        
        // Exchange updates
        this.sendMessage(0, 1, 'B', this.nodes[0].version);
        this.sendMessage(0, 2, 'B', this.nodes[0].version);
        this.sendMessage(1, 0, 'C', this.nodes[1].version);
        this.sendMessage(1, 2, 'C', this.nodes[1].version);
      }
    }, 500 / this.animationSpeed);
  }
  
  runPartitionScenario() {
    // Simulate network partition between node 0 and others
    const originalSendMessage = this.sendMessage.bind(this);
    
    // Override sendMessage to drop messages
    this.sendMessage = (from, to, value, version, color) => {
      if ((from === 0 && to > 0) || (from > 0 && to === 0)) {
        // Partition - drop message
        return;
      }
      originalSendMessage(from, to, value, version, color);
    };
    
    // Node 0 tries to write
    this.nodes[0].pending = true;
    
    setTimeout(() => {
      if (this.selectedMode === 'strong') {
        // Cannot complete write - unavailable
        this.nodes[0].color = '#EF4444';
        this.nodes[0].pending = true; // Stays pending
        
        // Show timeout
        setTimeout(() => {
          this.nodes[0].pending = false;
          this.updateTradeOffs();
        }, 2000 / this.animationSpeed);
      } else {
        // Can write locally
        this.nodes[0].value = 'B';
        this.nodes[0].version++;
        this.nodes[0].pending = false;
        this.nodes[0].color = '#F59E0B'; // Orange for disconnected
        
        // Nodes 1 and 2 can still communicate
        this.nodes[1].value = 'C';
        this.nodes[1].version++;
        this.sendMessage(1, 2, 'C', this.nodes[1].version);
      }
    }, 500 / this.animationSpeed);
    
    // Restore after 3 seconds
    setTimeout(() => {
      this.sendMessage = originalSendMessage;
      // Heal partition - exchange updates
      if (this.selectedMode !== 'strong') {
        this.sendMessage(0, 1, this.nodes[0].value, this.nodes[0].version, '#10B981');
        this.sendMessage(0, 2, this.nodes[0].value, this.nodes[0].version, '#10B981');
        this.sendMessage(1, 0, this.nodes[1].value, this.nodes[1].version, '#10B981');
      }
    }, 3000 / this.animationSpeed);
  }
  
  updateTradeOffs() {
    const tradeOffs = {
      strong: { consistency: 100, availability: 60, partition: 80 },
      eventual: { consistency: 40, availability: 100, partition: 100 },
      causal: { consistency: 70, availability: 80, partition: 90 },
      weak: { consistency: 20, availability: 100, partition: 100 }
    };
    
    const model = tradeOffs[this.selectedMode];
    
    // Update bars
    document.querySelector('.consistency-bar').style.width = `${model.consistency}%`;
    document.querySelector('.availability-bar').style.width = `${model.availability}%`;
    document.querySelector('.partition-bar').style.width = `${model.partition}%`;
    
    // Update labels
    document.getElementById('current-model').textContent = 
      this.selectedMode.charAt(0).toUpperCase() + this.selectedMode.slice(1) + ' Consistency';
    
    document.getElementById('latency-value').textContent = 
      model.consistency > 80 ? 'High' : model.consistency > 50 ? 'Medium' : 'Low';
    
    document.getElementById('availability-value').textContent = 
      model.availability > 80 ? 'High' : model.availability > 50 ? 'Medium' : 'Low';
    
    document.getElementById('consistency-value').textContent = 
      model.consistency > 80 ? 'Strong' : model.consistency > 50 ? 'Moderate' : 'Weak';
    
    // Update insights
    const insights = this.getInsights(this.selectedMode);
    document.getElementById('insights-list').innerHTML = 
      insights.map(i => `<li>${i}</li>`).join('');
  }
  
  getInsights(mode) {
    const insights = {
      strong: [
        'All nodes see the same data at the same time',
        'Higher latency due to synchronization requirements',
        'May become unavailable during network partitions',
        'Best for: Financial transactions, inventory management'
      ],
      eventual: [
        'Nodes may temporarily have different values',
        'Low latency - updates happen asynchronously',
        'Highly available even during partitions',
        'Best for: Social media feeds, analytics data'
      ],
      causal: [
        'Preserves cause-and-effect relationships',
        'Balance between consistency and availability',
        'More complex to implement than other models',
        'Best for: Collaborative editing, chat applications'
      ],
      weak: [
        'No ordering guarantees between operations',
        'Lowest latency and highest availability',
        'May see updates out of order',
        'Best for: Caching, session data'
      ]
    };
    
    return insights[mode] || [];
  }
  
  togglePlayPause() {
    this.isPlaying = !this.isPlaying;
    const btn = document.getElementById('play-pause');
    btn.textContent = this.isPlaying ? '⏸️ Pause' : '▶️ Play';
  }
  
  reset() {
    this.messages = [];
    this.initializeNodes();
    this.updateTradeOffs();
    this.isPlaying = false;
    document.getElementById('play-pause').textContent = '▶️ Play';
  }
}

// Initialize visualizer
const consistencyVisualizer = new ConsistencyVisualizer();