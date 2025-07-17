// Enhanced Interactive Journey Map with Zoom, Keyboard Navigation, and Better Layout
class EnhancedJourneyMap {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.detailsPanel = document.getElementById('journey-details');
    this.nodes = this.defineNodes();
    this.edges = this.defineEdges();
    this.selectedNode = null;
    this.scale = 1;
    this.translateX = 0;
    this.translateY = 0;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    
    this.init();
  }
  
  defineNodes() {
    // Improved layout with better spacing to prevent overlaps
    return [
      // Axioms - Top two rows with better spacing
      { id: 'axiom-1', type: 'axiom', label: 'Latency', icon: '⚡', 
        description: 'The speed of light creates fundamental constraints',
        link: '/part1-axioms/axiom-1-latency/', x: 150, y: 100 },
      { id: 'axiom-2', type: 'axiom', label: 'Capacity', icon: '📦', 
        description: 'Every resource has finite limits',
        link: '/part1-axioms/axiom-2-capacity/', x: 350, y: 100 },
      { id: 'axiom-3', type: 'axiom', label: 'Failure', icon: '💥', 
        description: 'Components will fail; design for it',
        link: '/part1-axioms/axiom-3-failure/', x: 550, y: 100 },
      { id: 'axiom-4', type: 'axiom', label: 'Concurrency', icon: '🔄', 
        description: 'Multiple things happen at once',
        link: '/part1-axioms/axiom-4-concurrency/', x: 750, y: 100 },
      { id: 'axiom-5', type: 'axiom', label: 'Coordination', icon: '🤝', 
        description: 'Agreement requires communication',
        link: '/part1-axioms/axiom-5-coordination/', x: 150, y: 280 },
      { id: 'axiom-6', type: 'axiom', label: 'Observability', icon: '👁️', 
        description: 'You can only control what you can measure',
        link: '/part1-axioms/axiom-6-observability/', x: 350, y: 280 },
      { id: 'axiom-7', type: 'axiom', label: 'Human Interface', icon: '👤', 
        description: 'Humans operate the systems',
        link: '/part1-axioms/axiom-7-human-interface/', x: 550, y: 280 },
      { id: 'axiom-8', type: 'axiom', label: 'Economics', icon: '💰', 
        description: 'Every decision has a cost',
        link: '/part1-axioms/axiom-8-economics/', x: 750, y: 280 },
      
      // Pillars - Middle two rows with improved spacing
      { id: 'pillar-1', type: 'pillar', label: 'Work Distribution', icon: '⚙️',
        description: 'How to divide and conquer problems',
        link: '/part2-pillars/pillar-1-work/', x: 150, y: 460 },
      { id: 'pillar-2', type: 'pillar', label: 'State Distribution', icon: '💾',
        description: 'Managing data across nodes',
        link: '/part2-pillars/pillar-2-state/', x: 350, y: 460 },
      { id: 'pillar-3', type: 'pillar', label: 'Truth Distribution', icon: '✓',
        description: 'Achieving consensus and consistency',
        link: '/part2-pillars/pillar-3-truth/', x: 550, y: 460 },
      { id: 'pillar-4', type: 'pillar', label: 'Control Distribution', icon: '🎯',
        description: 'Orchestration vs choreography',
        link: '/part2-pillars/pillar-4-control/', x: 750, y: 460 },
      { id: 'pillar-5', type: 'pillar', label: 'Intelligence Distribution', icon: '🧠',
        description: 'Smart endpoints vs smart networks',
        link: '/part2-pillars/pillar-5-intelligence/', x: 250, y: 640 },
      { id: 'pillar-6', type: 'pillar', label: 'Trust Distribution', icon: '🔐',
        description: 'Security in distributed systems',
        link: '/part2-pillars/pillar-6-trust/', x: 650, y: 640 },
      
      // Tools - Bottom row
      { id: 'tool-1', type: 'tool', label: 'Latency Calculator', icon: '🧮',
        description: 'Calculate real-world latencies',
        link: '/tools/latency-calculator/', x: 250, y: 820 },
      { id: 'tool-2', type: 'tool', label: 'Capacity Planner', icon: '📊',
        description: 'Plan your system capacity',
        link: '/tools/capacity-planner/', x: 450, y: 820 },
      { id: 'tool-3', type: 'tool', label: 'Consistency Visualizer', icon: '🔄',
        description: 'Visualize consistency models',
        link: '/tools/consistency-visualizer/', x: 650, y: 820 }
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
      { from: 'pillar-3', to: 'tool-3' },
      
      // Cross connections
      { from: 'axiom-1', to: 'axiom-5' },
      { from: 'axiom-3', to: 'axiom-6' },
      { from: 'pillar-3', to: 'pillar-6' }
    ];
  }
  
  init() {
    this.createControls();
    const svg = this.createSVG();
    this.container.innerHTML += svg;
    this.svgElement = this.container.querySelector('svg');
    this.viewportGroup = this.svgElement.querySelector('.viewport');
    this.attachEventListeners();
    this.animateEntrance();
    this.setupKeyboardNavigation();
  }
  
  createControls() {
    const controls = `
      <div class="journey-controls" role="toolbar" aria-label="Journey map controls">
        <button class="journey-control-btn zoom-in" aria-label="Zoom in" title="Zoom in (Plus key)">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 5v5m-5 0h10m5 0a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
        </button>
        <button class="journey-control-btn zoom-out" aria-label="Zoom out" title="Zoom out (Minus key)">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M5 10h10m5 0a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
        </button>
        <button class="journey-control-btn zoom-reset" aria-label="Reset zoom" title="Reset zoom (0 key)">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M4 4v6h6M16 16v-6h-6" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
        </button>
        <button class="journey-control-btn fullscreen" aria-label="Toggle fullscreen" title="Toggle fullscreen (F key)">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M3 7V3h4M17 7V3h-4M3 13v4h4m10-4v4h-4" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
        </button>
      </div>
    `;
    this.container.innerHTML = controls;
  }
  
  createSVG() {
    const width = 900;
    const height = 920;
    
    let svg = `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Interactive journey map of distributed systems concepts">`;
    
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
        
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(0,0,0,0.05)" stroke-width="1"/>
        </pattern>
      </defs>
    `;
    
    // Add viewport group for pan and zoom
    svg += '<g class="viewport">';
    
    // Add background grid
    svg += `<rect width="${width}" height="${height}" fill="url(#grid)" opacity="0.5"/>`;
    
    // Draw edges
    svg += '<g class="edges">';
    this.edges.forEach(edge => {
      const fromNode = this.nodes.find(n => n.id === edge.from);
      const toNode = this.nodes.find(n => n.id === edge.to);
      
      // Calculate curved path
      const dx = toNode.x - fromNode.x;
      const dy = toNode.y - fromNode.y;
      const dr = Math.sqrt(dx * dx + dy * dy);
      
      svg += `
        <path 
          d="M${fromNode.x},${fromNode.y} Q${(fromNode.x + toNode.x) / 2},${(fromNode.y + toNode.y) / 2 + dr * 0.1} ${toNode.x},${toNode.y}"
          fill="none"
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
    this.nodes.forEach((node, index) => {
      const fillUrl = `url(#${node.type}Gradient)`;
      
      svg += `
        <g class="node" 
           data-node-id="${node.id}" 
           transform="translate(${node.x}, ${node.y})"
           tabindex="0"
           role="button"
           aria-label="${node.label}: ${node.description}"
           aria-describedby="node-${node.id}-desc">
          <circle 
            r="45" 
            fill="${fillUrl}"
            stroke="white"
            stroke-width="3"
            filter="url(#glow)"
            class="node-circle"
          />
          <text 
            y="-5" 
            text-anchor="middle" 
            font-size="28"
            class="node-icon"
            aria-hidden="true"
          >${node.icon}</text>
          <text 
            y="65" 
            text-anchor="middle" 
            font-size="14"
            font-weight="600"
            fill="var(--ds-text-primary)"
            class="node-label"
          >${node.label}</text>
          <desc id="node-${node.id}-desc">${node.description}</desc>
        </g>
      `;
    });
    svg += '</g>';
    
    svg += '</g>'; // End viewport group
    svg += '</svg>';
    return svg;
  }
  
  attachEventListeners() {
    // Node interactions
    const nodeElements = this.container.querySelectorAll('.node');
    
    nodeElements.forEach(elem => {
      elem.addEventListener('click', (e) => {
        const nodeId = elem.getAttribute('data-node-id');
        const node = this.nodes.find(n => n.id === nodeId);
        this.selectNode(node);
      });
      
      elem.addEventListener('mouseenter', (e) => {
        if (!this.selectedNode || elem.getAttribute('data-node-id') !== this.selectedNode.id) {
          elem.querySelector('.node-circle').style.transform = 'scale(1.1)';
        }
      });
      
      elem.addEventListener('mouseleave', (e) => {
        if (!this.selectedNode || elem.getAttribute('data-node-id') !== this.selectedNode.id) {
          elem.querySelector('.node-circle').style.transform = 'scale(1)';
        }
      });
    });
    
    // Control buttons
    this.container.querySelector('.zoom-in').addEventListener('click', () => this.zoom(1.2));
    this.container.querySelector('.zoom-out').addEventListener('click', () => this.zoom(0.8));
    this.container.querySelector('.zoom-reset').addEventListener('click', () => this.resetZoom());
    this.container.querySelector('.fullscreen').addEventListener('click', () => this.toggleFullscreen());
    
    // Pan functionality
    this.setupPanning();
    
    // Mouse wheel zoom
    this.svgElement.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      this.zoom(delta);
    });
  }
  
  setupPanning() {
    this.svgElement.addEventListener('mousedown', (e) => {
      if (e.target === this.svgElement || e.target.parentNode === this.viewportGroup) {
        this.isDragging = true;
        this.startX = e.clientX - this.translateX;
        this.startY = e.clientY - this.translateY;
        this.svgElement.style.cursor = 'grabbing';
      }
    });
    
    this.svgElement.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      
      this.translateX = e.clientX - this.startX;
      this.translateY = e.clientY - this.startY;
      this.updateTransform();
    });
    
    this.svgElement.addEventListener('mouseup', () => {
      this.isDragging = false;
      this.svgElement.style.cursor = 'grab';
    });
    
    this.svgElement.addEventListener('mouseleave', () => {
      this.isDragging = false;
      this.svgElement.style.cursor = 'grab';
    });
  }
  
  setupKeyboardNavigation() {
    const nodes = this.container.querySelectorAll('.node');
    let currentIndex = -1;
    
    // Keyboard navigation for nodes
    nodes.forEach((node, index) => {
      node.addEventListener('keydown', (e) => {
        switch(e.key) {
          case 'Enter':
          case ' ':
            e.preventDefault();
            node.click();
            break;
          case 'ArrowRight':
          case 'ArrowDown':
            e.preventDefault();
            currentIndex = (index + 1) % nodes.length;
            nodes[currentIndex].focus();
            break;
          case 'ArrowLeft':
          case 'ArrowUp':
            e.preventDefault();
            currentIndex = (index - 1 + nodes.length) % nodes.length;
            nodes[currentIndex].focus();
            break;
        }
      });
    });
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (!this.container.contains(document.activeElement)) return;
      
      switch(e.key) {
        case '+':
        case '=':
          e.preventDefault();
          this.zoom(1.2);
          break;
        case '-':
          e.preventDefault();
          this.zoom(0.8);
          break;
        case '0':
          e.preventDefault();
          this.resetZoom();
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          this.toggleFullscreen();
          break;
      }
    });
  }
  
  zoom(factor) {
    this.scale *= factor;
    this.scale = Math.max(0.5, Math.min(3, this.scale)); // Limit zoom range
    this.updateTransform();
  }
  
  resetZoom() {
    this.scale = 1;
    this.translateX = 0;
    this.translateY = 0;
    this.updateTransform();
  }
  
  updateTransform() {
    this.viewportGroup.setAttribute('transform', 
      `translate(${this.translateX}, ${this.translateY}) scale(${this.scale})`);
  }
  
  toggleFullscreen() {
    if (!document.fullscreenElement) {
      this.container.requestFullscreen().catch(err => {
        console.error('Error attempting to enable fullscreen:', err);
      });
    } else {
      document.exitFullscreen();
    }
  }
  
  selectNode(node) {
    // Update visual selection
    const allNodes = this.container.querySelectorAll('.node-circle');
    allNodes.forEach(n => n.style.transform = 'scale(1)');
    
    const selectedElem = this.container.querySelector(`[data-node-id="${node.id}"] .node-circle`);
    selectedElem.style.transform = 'scale(1.15)';
    
    this.selectedNode = node;
    
    // Update details panel with enhanced information
    this.detailsPanel.innerHTML = `
      <h3>${node.icon} ${node.label}</h3>
      <p>${node.description}</p>
      <div class="journey-connections">
        <h4>Connected Concepts:</h4>
        <ul>
          ${this.getConnectedNodes(node.id).map(n => 
            `<li><a href="${n.link}">${n.icon} ${n.label}</a></li>`
          ).join('')}
        </ul>
      </div>
      <a href="${node.link}" class="journey-link">
        Explore ${node.label} →
      </a>
    `;
    
    // Highlight connected nodes
    this.highlightConnections(node.id);
    
    // Announce selection for screen readers
    this.announceSelection(node);
  }
  
  getConnectedNodes(nodeId) {
    const connected = new Set();
    this.edges.forEach(edge => {
      if (edge.from === nodeId) {
        connected.add(edge.to);
      } else if (edge.to === nodeId) {
        connected.add(edge.from);
      }
    });
    
    return Array.from(connected).map(id => 
      this.nodes.find(n => n.id === id)
    ).filter(Boolean);
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
  
  announceSelection(node) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = `Selected ${node.label}. ${node.description}`;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
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

// Initialize enhanced journey map
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('journey-map')) {
    // Replace the old journey map with the enhanced version
    new EnhancedJourneyMap('journey-map');
  }
});