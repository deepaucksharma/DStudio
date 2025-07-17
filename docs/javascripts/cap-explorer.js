// CAP Theorem Interactive Explorer
class CAPExplorer {
  constructor() {
    this.selectedCombination = null;
    this.scenarios = [];
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupExplorer());
    } else {
      this.setupExplorer();
    }
  }
  
  setupExplorer() {
    const container = document.getElementById('cap-explorer');
    if (!container) return;
    
    // Create CAP triangle
    this.createCAPTriangle(container);
    
    // Create scenario selector
    this.createScenarioPanel(container);
    
    // Create results display
    this.createResultsPanel(container);
    
    // Create examples panel
    this.createExamplesPanel(container);
  }
  
  createCAPTriangle(container) {
    const triangleContainer = document.createElement('div');
    triangleContainer.className = 'cap-triangle-container';
    triangleContainer.innerHTML = `
      <svg width="400" height="350" viewBox="0 0 400 350" class="cap-triangle">
        <!-- Triangle -->
        <path d="M 200 50 L 350 300 L 50 300 Z" 
              fill="none" 
              stroke="#E5E7EB" 
              stroke-width="3"/>
        
        <!-- CP Edge -->
        <path d="M 200 50 L 350 300" 
              class="cap-edge" 
              data-selection="CP" 
              stroke="#3B82F6" 
              stroke-width="8" 
              opacity="0.3"/>
        
        <!-- CA Edge -->
        <path d="M 200 50 L 50 300" 
              class="cap-edge" 
              data-selection="CA" 
              stroke="#10B981" 
              stroke-width="8" 
              opacity="0.3"/>
        
        <!-- AP Edge -->
        <path d="M 50 300 L 350 300" 
              class="cap-edge" 
              data-selection="AP" 
              stroke="#F59E0B" 
              stroke-width="8" 
              opacity="0.3"/>
        
        <!-- Vertices -->
        <circle cx="200" cy="50" r="30" fill="#5448C8" class="cap-vertex" data-vertex="C"/>
        <circle cx="50" cy="300" r="30" fill="#5448C8" class="cap-vertex" data-vertex="A"/>
        <circle cx="350" cy="300" r="30" fill="#5448C8" class="cap-vertex" data-vertex="P"/>
        
        <!-- Labels -->
        <text x="200" y="20" text-anchor="middle" class="cap-label">Consistency</text>
        <text x="200" y="57" text-anchor="middle" class="cap-vertex-label">C</text>
        
        <text x="30" y="340" text-anchor="middle" class="cap-label">Availability</text>
        <text x="50" y="307" text-anchor="middle" class="cap-vertex-label">A</text>
        
        <text x="370" y="340" text-anchor="middle" class="cap-label">Partition Tolerance</text>
        <text x="350" y="307" text-anchor="middle" class="cap-vertex-label">P</text>
        
        <!-- Selection Labels -->
        <text x="275" y="175" text-anchor="middle" class="cap-selection-label" data-label="CP">CP System</text>
        <text x="125" y="175" text-anchor="middle" class="cap-selection-label" data-label="CA">CA System</text>
        <text x="200" y="315" text-anchor="middle" class="cap-selection-label" data-label="AP">AP System</text>
      </svg>
      
      <div class="cap-description">
        <h4>Select a combination to explore:</h4>
        <p>Click on the edges of the triangle to select different CAP combinations</p>
      </div>
    `;
    container.appendChild(triangleContainer);
    
    // Add interactivity
    const edges = triangleContainer.querySelectorAll('.cap-edge');
    edges.forEach(edge => {
      edge.addEventListener('click', (e) => {
        this.selectCombination(e.target.dataset.selection);
      });
      
      edge.addEventListener('mouseenter', (e) => {
        e.target.style.opacity = '0.6';
        e.target.style.cursor = 'pointer';
      });
      
      edge.addEventListener('mouseleave', (e) => {
        e.target.style.opacity = this.selectedCombination === e.target.dataset.selection ? '0.8' : '0.3';
      });
    });
  }
  
  createScenarioPanel(container) {
    const panel = document.createElement('div');
    panel.className = 'cap-scenario-panel';
    panel.innerHTML = `
      <h3>Test Scenarios</h3>
      <div class="scenario-buttons">
        <button class="scenario-btn" data-scenario="normal">
          <span class="scenario-icon">🌐</span>
          <span>Normal Operation</span>
        </button>
        <button class="scenario-btn" data-scenario="partition">
          <span class="scenario-icon">🔀</span>
          <span>Network Partition</span>
        </button>
        <button class="scenario-btn" data-scenario="node-failure">
          <span class="scenario-icon">💥</span>
          <span>Node Failure</span>
        </button>
        <button class="scenario-btn" data-scenario="high-load">
          <span class="scenario-icon">📈</span>
          <span>High Load</span>
        </button>
      </div>
      
      <div class="scenario-visualization">
        <canvas id="scenario-canvas" width="600" height="300"></canvas>
      </div>
    `;
    container.appendChild(panel);
    
    // Add event listeners
    const buttons = panel.querySelectorAll('.scenario-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const scenario = e.currentTarget.dataset.scenario;
        this.runScenario(scenario);
      });
    });
    
    // Initialize canvas
    this.canvas = document.getElementById('scenario-canvas');
    this.ctx = this.canvas.getContext('2d');
  }
  
  createResultsPanel(container) {
    const panel = document.createElement('div');
    panel.className = 'cap-results-panel';
    panel.innerHTML = `
      <h3>Analysis Results</h3>
      
      <div class="cap-metrics">
        <div class="metric-card">
          <div class="metric-icon">🔒</div>
          <div class="metric-content">
            <h4>Consistency</h4>
            <div class="metric-value" id="consistency-metric">-</div>
            <div class="metric-description" id="consistency-desc">Select a CAP combination</div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">✅</div>
          <div class="metric-content">
            <h4>Availability</h4>
            <div class="metric-value" id="availability-metric">-</div>
            <div class="metric-description" id="availability-desc">Select a CAP combination</div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🌍</div>
          <div class="metric-content">
            <h4>Partition Tolerance</h4>
            <div class="metric-value" id="partition-metric">-</div>
            <div class="metric-description" id="partition-desc">Select a CAP combination</div>
          </div>
        </div>
      </div>
      
      <div class="trade-offs-panel">
        <h4>Trade-offs & Implications</h4>
        <div id="trade-offs-content" class="trade-offs-content">
          <p>Select a CAP combination to see the trade-offs</p>
        </div>
      </div>
      
      <div class="implementation-notes">
        <h4>Implementation Strategies</h4>
        <div id="implementation-content" class="implementation-content">
          <p>Select a CAP combination to see implementation strategies</p>
        </div>
      </div>
    `;
    container.appendChild(panel);
  }
  
  createExamplesPanel(container) {
    const panel = document.createElement('div');
    panel.className = 'cap-examples-panel';
    panel.innerHTML = `
      <h3>Real-World Examples</h3>
      
      <div class="examples-grid" id="examples-grid">
        <div class="example-card placeholder">
          <h4>Select a CAP combination to see examples</h4>
        </div>
      </div>
    `;
    container.appendChild(panel);
  }
  
  selectCombination(combination) {
    this.selectedCombination = combination;
    
    // Update triangle visualization
    const edges = document.querySelectorAll('.cap-edge');
    edges.forEach(edge => {
      edge.style.opacity = edge.dataset.selection === combination ? '0.8' : '0.3';
    });
    
    // Update labels
    const labels = document.querySelectorAll('.cap-selection-label');
    labels.forEach(label => {
      label.style.display = label.dataset.label === combination ? 'block' : 'none';
    });
    
    // Update metrics
    this.updateMetrics(combination);
    
    // Update examples
    this.updateExamples(combination);
    
    // Clear scenario
    this.clearScenario();
  }
  
  updateMetrics(combination) {
    const metrics = {
      CP: {
        consistency: { value: 'Strong', desc: 'All nodes see the same data simultaneously' },
        availability: { value: 'Limited', desc: 'May reject requests during partitions' },
        partition: { value: 'Tolerant', desc: 'Continues operating when network splits' }
      },
      CA: {
        consistency: { value: 'Strong', desc: 'All nodes see the same data' },
        availability: { value: 'High', desc: 'Always accepts requests' },
        partition: { value: 'Intolerant', desc: 'Cannot handle network splits' }
      },
      AP: {
        consistency: { value: 'Eventual', desc: 'Nodes may temporarily disagree' },
        availability: { value: 'High', desc: 'Always accepts requests' },
        partition: { value: 'Tolerant', desc: 'Continues during network splits' }
      }
    };
    
    const selected = metrics[combination];
    
    document.getElementById('consistency-metric').textContent = selected.consistency.value;
    document.getElementById('consistency-desc').textContent = selected.consistency.desc;
    
    document.getElementById('availability-metric').textContent = selected.availability.value;
    document.getElementById('availability-desc').textContent = selected.availability.desc;
    
    document.getElementById('partition-metric').textContent = selected.partition.value;
    document.getElementById('partition-desc').textContent = selected.partition.desc;
    
    // Update trade-offs
    this.updateTradeOffs(combination);
    
    // Update implementation
    this.updateImplementation(combination);
  }
  
  updateTradeOffs(combination) {
    const tradeOffs = {
      CP: `
        <ul>
          <li><strong>✅ Pros:</strong>
            <ul>
              <li>Strong consistency guarantees</li>
              <li>No data conflicts or divergence</li>
              <li>Simpler application logic</li>
              <li>Good for critical data (financial, inventory)</li>
            </ul>
          </li>
          <li><strong>❌ Cons:</strong>
            <ul>
              <li>May become unavailable during partitions</li>
              <li>Higher latency due to synchronization</li>
              <li>Lower throughput</li>
              <li>Complex failure handling</li>
            </ul>
          </li>
        </ul>
      `,
      CA: `
        <ul>
          <li><strong>✅ Pros:</strong>
            <ul>
              <li>Strong consistency when network is stable</li>
              <li>High availability in single datacenter</li>
              <li>Low latency operations</li>
              <li>Traditional database guarantees</li>
            </ul>
          </li>
          <li><strong>❌ Cons:</strong>
            <ul>
              <li>Cannot handle network partitions</li>
              <li>Limited to single datacenter deployments</li>
              <li>No geo-distribution capabilities</li>
              <li>Single point of failure risks</li>
            </ul>
          </li>
        </ul>
      `,
      AP: `
        <ul>
          <li><strong>✅ Pros:</strong>
            <ul>
              <li>Always available for reads and writes</li>
              <li>Survives network partitions</li>
              <li>Good for geo-distributed systems</li>
              <li>High performance and scalability</li>
            </ul>
          </li>
          <li><strong>❌ Cons:</strong>
            <ul>
              <li>Eventual consistency complexities</li>
              <li>Potential for conflicting updates</li>
              <li>Complex conflict resolution needed</li>
              <li>Harder application logic</li>
            </ul>
          </li>
        </ul>
      `
    };
    
    document.getElementById('trade-offs-content').innerHTML = tradeOffs[combination];
  }
  
  updateImplementation(combination) {
    const implementations = {
      CP: `
        <div class="implementation-strategy">
          <h5>Common Patterns:</h5>
          <ul>
            <li><strong>Consensus Protocols:</strong> Raft, Paxos, ZAB</li>
            <li><strong>Quorum Systems:</strong> Majority writes/reads</li>
            <li><strong>Two-Phase Commit:</strong> Distributed transactions</li>
            <li><strong>Leader Election:</strong> Single writer pattern</li>
          </ul>
          
          <h5>Best Practices:</h5>
          <ul>
            <li>Use timeouts to detect partitions quickly</li>
            <li>Implement circuit breakers for availability</li>
            <li>Design for graceful degradation</li>
            <li>Monitor consensus health continuously</li>
          </ul>
          
          <h5>Code Example:</h5>
          <pre><code>// CP System with Raft consensus
class CPDataStore {
  async write(key, value) {
    // Propose to leader
    const proposal = { key, value, timestamp: Date.now() };
    
    // Wait for majority acknowledgment
    const acks = await this.raft.propose(proposal);
    
    if (acks < this.majority) {
      throw new ConsistencyError('Insufficient replicas');
    }
    
    return { success: true, version: proposal.timestamp };
  }
  
  async read(key) {
    // Read from majority for consistency
    const values = await this.raft.readFromMajority(key);
    return this.resolveLatestValue(values);
  }
}</code></pre>
        </div>
      `,
      CA: `
        <div class="implementation-strategy">
          <h5>Common Patterns:</h5>
          <ul>
            <li><strong>Traditional RDBMS:</strong> ACID transactions</li>
            <li><strong>Master-Slave:</strong> Synchronous replication</li>
            <li><strong>Shared Storage:</strong> SAN/NAS systems</li>
            <li><strong>Lock-based:</strong> Distributed locking</li>
          </ul>
          
          <h5>Best Practices:</h5>
          <ul>
            <li>Keep all nodes in same datacenter</li>
            <li>Use low-latency interconnects</li>
            <li>Implement fast failure detection</li>
            <li>Regular backup for disaster recovery</li>
          </ul>
          
          <h5>Code Example:</h5>
          <pre><code>// CA System with traditional locking
class CADataStore {
  async write(key, value) {
    // Acquire distributed lock
    const lock = await this.lockManager.acquire(key);
    
    try {
      // Synchronous replication to all nodes
      await Promise.all(
        this.replicas.map(replica => 
          replica.write(key, value)
        )
      );
      
      return { success: true };
    } finally {
      await lock.release();
    }
  }
  
  async read(key) {
    // Read from any node (all are consistent)
    return this.localNode.read(key);
  }
}</code></pre>
        </div>
      `,
      AP: `
        <div class="implementation-strategy">
          <h5>Common Patterns:</h5>
          <ul>
            <li><strong>Eventual Consistency:</strong> CRDTs, Vector clocks</li>
            <li><strong>Gossip Protocols:</strong> State dissemination</li>
            <li><strong>Multi-Master:</strong> Conflict resolution</li>
            <li><strong>Read Repair:</strong> Lazy synchronization</li>
          </ul>
          
          <h5>Best Practices:</h5>
          <ul>
            <li>Design idempotent operations</li>
            <li>Use vector clocks for causality</li>
            <li>Implement conflict resolution strategies</li>
            <li>Provide consistency levels per operation</li>
          </ul>
          
          <h5>Code Example:</h5>
          <pre><code>// AP System with eventual consistency
class APDataStore {
  async write(key, value) {
    // Write locally first
    const version = this.vectorClock.increment();
    await this.localNode.write(key, value, version);
    
    // Async replication to others
    setImmediate(() => {
      this.gossip.broadcast({
        key, value, version,
        node: this.nodeId
      });
    });
    
    return { success: true, version };
  }
  
  async read(key, consistency = 'eventual') {
    if (consistency === 'eventual') {
      // Read from local node
      return this.localNode.read(key);
    } else {
      // Read from quorum for stronger consistency
      return this.readWithQuorum(key);
    }
  }
}</code></pre>
        </div>
      `
    };
    
    document.getElementById('implementation-content').innerHTML = implementations[combination];
  }
  
  updateExamples(combination) {
    const examples = {
      CP: [
        {
          name: 'Apache ZooKeeper',
          desc: 'Distributed coordination service',
          use: 'Configuration management, service discovery'
        },
        {
          name: 'etcd',
          desc: 'Distributed key-value store',
          use: 'Kubernetes configuration, distributed locks'
        },
        {
          name: 'Google Spanner',
          desc: 'Globally distributed database',
          use: 'Financial transactions, global consistency'
        },
        {
          name: 'CockroachDB',
          desc: 'Distributed SQL database',
          use: 'ACID transactions across regions'
        }
      ],
      CA: [
        {
          name: 'Traditional RDBMS',
          desc: 'PostgreSQL, MySQL, Oracle',
          use: 'Single datacenter deployments'
        },
        {
          name: 'Neo4j (single instance)',
          desc: 'Graph database',
          use: 'Relationship-heavy data models'
        },
        {
          name: 'Redis (single master)',
          desc: 'In-memory data store',
          use: 'Caching, session storage'
        },
        {
          name: 'MongoDB (replica set)',
          desc: 'Document database',
          use: 'Single region deployments'
        }
      ],
      AP: [
        {
          name: 'Apache Cassandra',
          desc: 'Wide-column store',
          use: 'Time-series data, high write throughput'
        },
        {
          name: 'Amazon DynamoDB',
          desc: 'Managed NoSQL database',
          use: 'Web applications, mobile backends'
        },
        {
          name: 'Riak',
          desc: 'Distributed key-value store',
          use: 'High availability requirements'
        },
        {
          name: 'CouchDB',
          desc: 'Document database',
          use: 'Offline-first applications'
        }
      ]
    };
    
    const grid = document.getElementById('examples-grid');
    grid.innerHTML = '';
    
    examples[combination].forEach(example => {
      const card = document.createElement('div');
      card.className = 'example-card';
      card.innerHTML = `
        <h4>${example.name}</h4>
        <p class="example-desc">${example.desc}</p>
        <p class="example-use"><strong>Use case:</strong> ${example.use}</p>
      `;
      grid.appendChild(card);
    });
  }
  
  runScenario(scenario) {
    if (!this.selectedCombination) {
      alert('Please select a CAP combination first');
      return;
    }
    
    // Clear previous scenario
    this.clearScenario();
    
    // Run new scenario
    switch (scenario) {
      case 'normal':
        this.runNormalScenario();
        break;
      case 'partition':
        this.runPartitionScenario();
        break;
      case 'node-failure':
        this.runNodeFailureScenario();
        break;
      case 'high-load':
        this.runHighLoadScenario();
        break;
    }
  }
  
  clearScenario() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Reset any animations
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }
  
  runNormalScenario() {
    const nodes = [
      { x: 150, y: 150, id: 'A', status: 'active' },
      { x: 300, y: 100, id: 'B', status: 'active' },
      { x: 450, y: 150, id: 'C', status: 'active' }
    ];
    
    const animate = () => {
      this.drawNodes(nodes);
      this.drawConnections(nodes, 'normal');
      
      // Simulate data flow
      const time = Date.now() / 1000;
      this.drawDataFlow(nodes, time);
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  runPartitionScenario() {
    const nodes = [
      { x: 150, y: 150, id: 'A', status: 'active', partition: 1 },
      { x: 300, y: 100, id: 'B', status: 'active', partition: 2 },
      { x: 450, y: 150, id: 'C', status: 'active', partition: 2 }
    ];
    
    const animate = () => {
      this.drawNodes(nodes);
      this.drawConnections(nodes, 'partition');
      
      // Show behavior based on CAP selection
      this.showPartitionBehavior(nodes);
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  runNodeFailureScenario() {
    const nodes = [
      { x: 150, y: 150, id: 'A', status: 'active' },
      { x: 300, y: 100, id: 'B', status: 'failed' },
      { x: 450, y: 150, id: 'C', status: 'active' }
    ];
    
    const animate = () => {
      this.drawNodes(nodes);
      this.drawConnections(nodes, 'failure');
      
      // Show failure handling based on CAP
      this.showFailureBehavior(nodes);
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  runHighLoadScenario() {
    const nodes = [
      { x: 150, y: 150, id: 'A', status: 'active', load: 0.9 },
      { x: 300, y: 100, id: 'B', status: 'active', load: 0.95 },
      { x: 450, y: 150, id: 'C', status: 'active', load: 0.85 }
    ];
    
    const animate = () => {
      this.drawNodes(nodes);
      this.drawConnections(nodes, 'normal');
      
      // Show load handling based on CAP
      this.showLoadBehavior(nodes);
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  drawNodes(nodes) {
    const ctx = this.ctx;
    
    nodes.forEach(node => {
      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, 30, 0, 2 * Math.PI);
      
      if (node.status === 'failed') {
        ctx.fillStyle = '#EF4444';
      } else if (node.load && node.load > 0.9) {
        ctx.fillStyle = '#F59E0B';
      } else {
        ctx.fillStyle = '#10B981';
      }
      
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 3;
      ctx.stroke();
      
      // Node label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 16px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`Node ${node.id}`, node.x, node.y);
      
      // Load indicator
      if (node.load) {
        ctx.fillStyle = '#4B5563';
        ctx.font = '12px Inter';
        ctx.fillText(`${Math.round(node.load * 100)}%`, node.x, node.y + 45);
      }
    });
  }
  
  drawConnections(nodes, type) {
    const ctx = this.ctx;
    
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const node1 = nodes[i];
        const node2 = nodes[j];
        
        // Skip if partitioned
        if (type === 'partition' && node1.partition !== node2.partition) {
          // Draw broken line
          ctx.setLineDash([5, 5]);
          ctx.strokeStyle = '#EF4444';
          ctx.lineWidth = 2;
        } else if (node1.status === 'failed' || node2.status === 'failed') {
          ctx.setLineDash([5, 5]);
          ctx.strokeStyle = '#F59E0B';
          ctx.lineWidth = 2;
        } else {
          ctx.setLineDash([]);
          ctx.strokeStyle = '#E5E7EB';
          ctx.lineWidth = 2;
        }
        
        ctx.beginPath();
        ctx.moveTo(node1.x, node1.y);
        ctx.lineTo(node2.x, node2.y);
        ctx.stroke();
      }
    }
    
    ctx.setLineDash([]);
  }
  
  drawDataFlow(nodes, time) {
    const ctx = this.ctx;
    
    // Simulate data propagation
    const progress = (time % 2) / 2;
    
    if (progress < 0.5) {
      // Node A to B
      const x = nodes[0].x + (nodes[1].x - nodes[0].x) * (progress * 2);
      const y = nodes[0].y + (nodes[1].y - nodes[0].y) * (progress * 2);
      
      ctx.fillStyle = '#3B82F6';
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, 2 * Math.PI);
      ctx.fill();
    }
  }
  
  showPartitionBehavior(nodes) {
    const ctx = this.ctx;
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    
    if (this.selectedCombination === 'CP') {
      ctx.fillStyle = '#EF4444';
      ctx.fillText('❌ Writes Rejected', 300, 250);
      ctx.fillText('Maintaining Consistency', 300, 270);
    } else if (this.selectedCombination === 'AP') {
      ctx.fillStyle = '#F59E0B';
      ctx.fillText('⚠️ Split Brain', 300, 250);
      ctx.fillText('Both partitions accept writes', 300, 270);
    } else if (this.selectedCombination === 'CA') {
      ctx.fillStyle = '#EF4444';
      ctx.fillText('💥 System Down', 300, 250);
      ctx.fillText('Cannot handle partition', 300, 270);
    }
  }
  
  showFailureBehavior(nodes) {
    const ctx = this.ctx;
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    
    if (this.selectedCombination === 'CP') {
      ctx.fillStyle = '#10B981';
      ctx.fillText('✅ Consensus with A & C', 300, 250);
      ctx.fillText('Continues with majority', 300, 270);
    } else if (this.selectedCombination === 'AP') {
      ctx.fillStyle = '#10B981';
      ctx.fillText('✅ Continues Operating', 300, 250);
      ctx.fillText('Handles node failure gracefully', 300, 270);
    } else if (this.selectedCombination === 'CA') {
      ctx.fillStyle = '#F59E0B';
      ctx.fillText('⚠️ Degraded Mode', 300, 250);
      ctx.fillText('Reduced redundancy', 300, 270);
    }
  }
  
  showLoadBehavior(nodes) {
    const ctx = this.ctx;
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    
    if (this.selectedCombination === 'CP') {
      ctx.fillStyle = '#F59E0B';
      ctx.fillText('🐌 Increased Latency', 300, 250);
      ctx.fillText('Consensus takes longer', 300, 270);
    } else if (this.selectedCombination === 'AP') {
      ctx.fillStyle = '#10B981';
      ctx.fillText('⚡ Load Distributed', 300, 250);
      ctx.fillText('Each node handles independently', 300, 270);
    } else if (this.selectedCombination === 'CA') {
      ctx.fillStyle = '#EF4444';
      ctx.fillText('🔒 Contention Issues', 300, 250);
      ctx.fillText('Lock conflicts increase', 300, 270);
    }
  }
}

// Initialize CAP Explorer
const capExplorer = new CAPExplorer();