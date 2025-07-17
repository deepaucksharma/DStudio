// Interactive Journey Map
class JourneyMap {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.detailsPanel = document.getElementById('journey-details');
    this.nodes = this.defineNodes();
    this.edges = this.defineEdges();
    this.selectedNode = null;
    
    this.init();
  }
  
  defineNodes() {
    return [
      // Axioms
      { id: 'axiom-1', type: 'axiom', label: 'Latency', icon: '⚡', 
        description: 'The speed of light creates fundamental constraints',
        link: '/part1-axioms/axiom-1-latency/', x: 200, y: 100 },
      { id: 'axiom-2', type: 'axiom', label: 'Capacity', icon: '📦', 
        description: 'Every resource has finite limits',
        link: '/part1-axioms/axiom-2-capacity/', x: 400, y: 100 },
      { id: 'axiom-3', type: 'axiom', label: 'Failure', icon: '💥', 
        description: 'Components will fail; design for it',
        link: '/part1-axioms/axiom-3-failure/', x: 600, y: 100 },
      { id: 'axiom-4', type: 'axiom', label: 'Concurrency', icon: '🔄', 
        description: 'Multiple things happen at once',
        link: '/part1-axioms/axiom-4-concurrency/', x: 800, y: 100 },
      { id: 'axiom-5', type: 'axiom', label: 'Coordination', icon: '🤝', 
        description: 'Agreement requires communication',
        link: '/part1-axioms/axiom-5-coordination/', x: 200, y: 250 },
      { id: 'axiom-6', type: 'axiom', label: 'Observability', icon: '👁️', 
        description: 'You can only control what you can measure',
        link: '/part1-axioms/axiom-6-observability/', x: 400, y: 250 },
      { id: 'axiom-7', type: 'axiom', label: 'Human Interface', icon: '👤', 
        description: 'Humans operate the systems',
        link: '/part1-axioms/axiom-7-human-interface/', x: 600, y: 250 },
      { id: 'axiom-8', type: 'axiom', label: 'Economics', icon: '💰', 
        description: 'Every decision has a cost',
        link: '/part1-axioms/axiom-8-economics/', x: 800, y: 250 },
      
      // Pillars
      { id: 'pillar-1', type: 'pillar', label: 'Work Distribution', icon: '⚙️',
        description: 'How to divide and conquer problems',
        link: '/part2-pillars/pillar-1-work/', x: 150, y: 400 },
      { id: 'pillar-2', type: 'pillar', label: 'State Distribution', icon: '💾',
        description: 'Managing data across nodes',
        link: '/part2-pillars/pillar-2-state/', x: 350, y: 400 },
      { id: 'pillar-3', type: 'pillar', label: 'Truth Distribution', icon: '✓',
        description: 'Achieving consensus and consistency',
        link: '/part2-pillars/pillar-3-truth/', x: 550, y: 400 },
      { id: 'pillar-4', type: 'pillar', label: 'Control Distribution', icon: '🎯',
        description: 'Orchestration vs choreography',
        link: '/part2-pillars/pillar-4-control/', x: 750, y: 400 },
      { id: 'pillar-5', type: 'pillar', label: 'Intelligence Distribution', icon: '🧠',
        description: 'Smart endpoints vs smart networks',
        link: '/part2-pillars/pillar-5-intelligence/', x: 350, y: 550 },
      { id: 'pillar-6', type: 'pillar', label: 'Trust Distribution', icon: '🔐',
        description: 'Security in distributed systems',
        link: '/part2-pillars/pillar-6-trust/', x: 550, y: 550 },
      
      // Tools
      { id: 'tool-1', type: 'tool', label: 'Latency Calculator', icon: '🧮',
        description: 'Calculate real-world latencies',
        link: '/tools/latency-calculator/', x: 200, y: 700 },
      { id: 'tool-2', type: 'tool', label: 'Capacity Planner', icon: '📊',
        description: 'Plan your system capacity',
        link: '/tools/capacity-planner/', x: 600, y: 700 }
    ];
  }
  
  defineEdges() {
    return [
      // Axioms to Pillars connections
      { from: 'axiom-1', to: 'pillar-1' },
      { from: 'axiom-2', to: 'pillar-1' },
      { from: 'axiom-2', to: 'pillar-2' },
      { from: 'axiom-3', to: 'pillar-3' },
      { from: 'axiom-4', to: 'pillar-3' },
      { from: 'axiom-5', to: 'pillar-4' },
      { from: 'axiom-6', to: 'pillar-5' },
      { from: 'axiom-7', to: 'pillar-4' },
      { from: 'axiom-8', to: 'pillar-5' },
      
      // Pillars to Tools
      { from: 'pillar-1', to: 'tool-1' },
      { from: 'pillar-2', to: 'tool-2' },
      
      // Cross connections
      { from: 'axiom-1', to: 'axiom-5' },
      { from: 'axiom-3', to: 'axiom-6' },
      { from: 'pillar-3', to: 'pillar-6' }
    ];
  }
  
  init() {
    const svg = this.createSVG();
    this.container.innerHTML = svg;
    this.attachEventListeners();
    this.animateEntrance();
  }
  
  createSVG() {
    const width = 1000;
    const height = 800;
    
    let svg = `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">`;
    
    // Add gradient definitions
    svg += `
      <defs>
        <linearGradient id="axiomGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#5B5FC7;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#818CF8;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="pillarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#10B981;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#34D399;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="toolGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#FCD34D;stop-opacity:1" />
        </linearGradient>
        
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
    `;
    
    // Draw edges
    svg += '<g class="edges">';
    this.edges.forEach(edge => {
      const fromNode = this.nodes.find(n => n.id === edge.from);
      const toNode = this.nodes.find(n => n.id === edge.to);
      
      svg += `
        <line 
          x1="${fromNode.x}" y1="${fromNode.y}" 
          x2="${toNode.x}" y2="${toNode.y}"
          stroke="rgba(129, 140, 248, 0.2)"
          stroke-width="2"
          stroke-dasharray="5,5"
          class="edge-line"
          data-from="${edge.from}"
          data-to="${edge.to}"
        />
      `;
    });
    svg += '</g>';
    
    // Draw nodes
    svg += '<g class="nodes">';
    this.nodes.forEach(node => {
      const fillUrl = `url(#${node.type}Gradient)`;
      
      svg += `
        <g class="node" data-node-id="${node.id}" transform="translate(${node.x}, ${node.y})">
          <circle 
            r="40" 
            fill="${fillUrl}"
            stroke="white"
            stroke-width="3"
            filter="url(#glow)"
            class="node-circle"
          />
          <text 
            y="-5" 
            text-anchor="middle" 
            font-size="24"
            class="node-icon"
          >${node.icon}</text>
          <text 
            y="60" 
            text-anchor="middle" 
            font-size="14"
            font-weight="600"
            fill="var(--ds-text-primary)"
            class="node-label"
          >${node.label}</text>
        </g>
      `;
    });
    svg += '</g>';
    
    svg += '</svg>';
    return svg;
  }
  
  attachEventListeners() {
    const nodeElements = this.container.querySelectorAll('.node');
    
    nodeElements.forEach(elem => {
      elem.addEventListener('click', (e) => {
        const nodeId = elem.getAttribute('data-node-id');
        const node = this.nodes.find(n => n.id === nodeId);
        this.selectNode(node);
      });
      
      elem.addEventListener('mouseenter', (e) => {
        elem.querySelector('.node-circle').style.transform = 'scale(1.1)';
      });
      
      elem.addEventListener('mouseleave', (e) => {
        if (elem.getAttribute('data-node-id') !== this.selectedNode?.id) {
          elem.querySelector('.node-circle').style.transform = 'scale(1)';
        }
      });
    });
  }
  
  selectNode(node) {
    // Update visual selection
    const allNodes = this.container.querySelectorAll('.node-circle');
    allNodes.forEach(n => n.style.transform = 'scale(1)');
    
    const selectedElem = this.container.querySelector(`[data-node-id="${node.id}"] .node-circle`);
    selectedElem.style.transform = 'scale(1.15)';
    
    this.selectedNode = node;
    
    // Update details panel
    this.detailsPanel.innerHTML = `
      <h3>${node.icon} ${node.label}</h3>
      <p>${node.description}</p>
      <a href="${node.link}" class="journey-link">
        Explore ${node.label} →
      </a>
    `;
    
    // Highlight connected nodes
    this.highlightConnections(node.id);
  }
  
  highlightConnections(nodeId) {
    // Reset all edges
    const edges = this.container.querySelectorAll('.edge-line');
    edges.forEach(e => {
      e.style.stroke = 'rgba(129, 140, 248, 0.2)';
      e.style.strokeWidth = '2';
    });
    
    // Highlight connected edges
    edges.forEach(edge => {
      const from = edge.getAttribute('data-from');
      const to = edge.getAttribute('data-to');
      
      if (from === nodeId || to === nodeId) {
        edge.style.stroke = 'rgba(129, 140, 248, 0.6)';
        edge.style.strokeWidth = '3';
      }
    });
  }
  
  animateEntrance() {
    const nodes = this.container.querySelectorAll('.node');
    nodes.forEach((node, index) => {
      node.style.opacity = '0';
      const transform = node.getAttribute('transform');
      const match = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
      if (match) {
        const x = parseFloat(match[1]);
        const y = parseFloat(match[2]);
        node.setAttribute('transform', `translate(${x}, ${y + 20})`);
        
        setTimeout(() => {
          node.style.transition = 'all 0.5s ease-out';
          node.style.opacity = '1';
          node.setAttribute('transform', `translate(${x}, ${y})`);
        }, index * 50);
      }
    });
  }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('journey-map')) {
    new JourneyMap('journey-map');
  }
});