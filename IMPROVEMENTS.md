# DStudio Compendium: Static Site Enhancement Roadmap

## 1. Executive Summary

This document provides an ultra-detailed implementation plan for enhancing the DStudio Compendium as a static GitHub Pages site. All enhancements focus on client-side interactivity, visual improvements, and content organization without requiring any backend services or user authentication.

---

## 2. Phase 1: Visual Design & Brand Identity Enhancement (Week 1-2)

### 2.1 Hero Section Transformation

**Current State**: Static text introduction
**Target State**: Animated, visually compelling hero with CSS/JS animations

#### Implementation Files:
- `docs/index.md`
- `docs/stylesheets/extra.css`
- `docs/javascripts/hero-animation.js` (new)

#### Detailed Changes:

```markdown
<!-- docs/index.md - New Hero Section -->
# The Compendium of Distributed Systems

<div class="hero-container">
  <div class="hero-animation">
    <canvas id="network-visualization"></canvas>
  </div>
  <div class="hero-content">
    <h1 class="hero-title">Master Distributed Systems from <span class="highlight">First Principles</span></h1>
    <p class="hero-subtitle">Derive patterns from physics, not memorization</p>
    <div class="hero-stats">
      <div class="stat-item">
        <span class="stat-number">8</span>
        <span class="stat-label">Fundamental Axioms</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">6</span>
        <span class="stat-label">Core Pillars</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">50+</span>
        <span class="stat-label">Real-World Cases</span>
      </div>
    </div>
  </div>
</div>
```

```css
/* docs/stylesheets/extra.css - Hero Styles */
.hero-container {
  position: relative;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  margin: 2rem 0;
}

.hero-animation {
  position: absolute;
  inset: 0;
  opacity: 0.3;
}

#network-visualization {
  width: 100%;
  height: 100%;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #fff 0%, #818CF8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: fadeInUp 0.8s ease-out;
}

.highlight {
  color: #00BCD4;
  -webkit-text-fill-color: #00BCD4;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.stat-item {
  text-align: center;
  animation: fadeIn 1s ease-out;
  animation-fill-mode: both;
}

.stat-item:nth-child(1) { animation-delay: 0.2s; }
.stat-item:nth-child(2) { animation-delay: 0.4s; }
.stat-item:nth-child(3) { animation-delay: 0.6s; }

.stat-number {
  display: block;
  font-size: 3rem;
  font-weight: 800;
  color: #00BCD4;
}

.stat-label {
  display: block;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 0.5rem;
}
```

```javascript
// docs/javascripts/hero-animation.js
class NetworkVisualization {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = [];
    this.connections = [];
    this.animationId = null;
    
    this.resize();
    this.init();
    this.animate();
    
    window.addEventListener('resize', () => this.resize());
  }
  
  resize() {
    this.canvas.width = this.canvas.offsetWidth * window.devicePixelRatio;
    this.canvas.height = this.canvas.offsetHeight * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }
  
  init() {
    // Create nodes representing distributed systems
    const nodeCount = 8; // One for each axiom
    for (let i = 0; i < nodeCount; i++) {
      this.nodes.push({
        x: Math.random() * this.canvas.offsetWidth,
        y: Math.random() * this.canvas.offsetHeight,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: 4 + Math.random() * 4,
        pulsePhase: Math.random() * Math.PI * 2
      });
    }
    
    // Create connections
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < nodeCount; j++) {
        if (Math.random() < 0.3) {
          this.connections.push({
            from: i,
            to: j,
            progress: 0,
            speed: 0.01 + Math.random() * 0.02
          });
        }
      }
    }
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.offsetWidth, this.canvas.offsetHeight);
    
    // Update and draw connections
    this.connections.forEach(conn => {
      const from = this.nodes[conn.from];
      const to = this.nodes[conn.to];
      
      // Draw connection line
      this.ctx.beginPath();
      this.ctx.strokeStyle = 'rgba(129, 140, 248, 0.1)';
      this.ctx.lineWidth = 1;
      this.ctx.moveTo(from.x, from.y);
      this.ctx.lineTo(to.x, to.y);
      this.ctx.stroke();
      
      // Draw data packet animation
      conn.progress += conn.speed;
      if (conn.progress > 1) conn.progress = 0;
      
      const packetX = from.x + (to.x - from.x) * conn.progress;
      const packetY = from.y + (to.y - from.y) * conn.progress;
      
      this.ctx.beginPath();
      this.ctx.fillStyle = '#00BCD4';
      this.ctx.arc(packetX, packetY, 2, 0, Math.PI * 2);
      this.ctx.fill();
    });
    
    // Update and draw nodes
    this.nodes.forEach(node => {
      // Update position
      node.x += node.vx;
      node.y += node.vy;
      
      // Bounce off walls
      if (node.x < node.radius || node.x > this.canvas.offsetWidth - node.radius) {
        node.vx *= -1;
      }
      if (node.y < node.radius || node.y > this.canvas.offsetHeight - node.radius) {
        node.vy *= -1;
      }
      
      // Draw node with pulse effect
      node.pulsePhase += 0.05;
      const pulseRadius = node.radius + Math.sin(node.pulsePhase) * 2;
      
      this.ctx.beginPath();
      this.ctx.fillStyle = 'rgba(129, 140, 248, 0.8)';
      this.ctx.arc(node.x, node.y, pulseRadius, 0, Math.PI * 2);
      this.ctx.fill();
      
      // Inner circle
      this.ctx.beginPath();
      this.ctx.fillStyle = '#5B5FC7';
      this.ctx.arc(node.x, node.y, node.radius * 0.6, 0, Math.PI * 2);
      this.ctx.fill();
    });
    
    this.animationId = requestAnimationFrame(() => this.animate());
  }
  
  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('network-visualization');
  if (canvas) {
    new NetworkVisualization(canvas);
  }
});
```

### 2.2 Dark Mode Implementation

#### Implementation Files:
- `mkdocs.yml`
- `docs/stylesheets/extra.css`
- `docs/javascripts/theme-toggle.js` (new)

#### Detailed Changes:

```yaml
# mkdocs.yml - Enable palette toggle
theme:
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: cyan
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: cyan
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
```

```css
/* docs/stylesheets/extra.css - CSS Variables for Theming */
:root {
  /* Light mode colors */
  --ds-bg-primary: #ffffff;
  --ds-bg-secondary: #f5f5f5;
  --ds-text-primary: #111827;
  --ds-text-secondary: #4B5563;
  --ds-border-color: #E5E7EB;
  --ds-shadow-color: rgba(0, 0, 0, 0.1);
  
  /* Component specific */
  --axiom-bg: rgba(84, 72, 200, 0.05);
  --axiom-border: #5448C8;
  --decision-bg: rgba(16, 185, 129, 0.05);
  --decision-border: #10B981;
  --failure-bg: rgba(239, 68, 68, 0.05);
  --failure-border: #EF4444;
}

[data-md-color-scheme="slate"] {
  /* Dark mode colors */
  --ds-bg-primary: #1a1a2e;
  --ds-bg-secondary: #16213e;
  --ds-text-primary: #F9FAFB;
  --ds-text-secondary: #D1D5DB;
  --ds-border-color: #374151;
  --ds-shadow-color: rgba(0, 0, 0, 0.3);
  
  /* Component specific */
  --axiom-bg: rgba(129, 140, 248, 0.1);
  --axiom-border: #818CF8;
  --decision-bg: rgba(52, 211, 153, 0.1);
  --decision-border: #34D399;
  --failure-bg: rgba(248, 113, 113, 0.1);
  --failure-border: #F87171;
}

/* Apply variables to components */
.axiom-box {
  background: var(--axiom-bg);
  border-left-color: var(--axiom-border);
  color: var(--ds-text-primary);
}

.decision-box {
  background: var(--decision-bg);
  border-left-color: var(--decision-border);
  color: var(--ds-text-primary);
}

.failure-vignette {
  background: var(--failure-bg);
  border-color: var(--failure-border);
  color: var(--ds-text-primary);
}
```

---

## 3. Phase 2: Interactive Journey Map (Week 3-4)

### 3.1 Clickable Network Diagram

**Implementation**: Pure CSS/JS interactive diagram showing axiom relationships

#### Files:
- `docs/index.md`
- `docs/javascripts/journey-map.js` (new)
- `docs/stylesheets/journey-map.css` (new)

#### Detailed Implementation:

```markdown
<!-- docs/index.md - Interactive Journey Section -->
## 🗺️ Your Learning Journey

<div id="journey-map-container">
  <div class="journey-legend">
    <div class="legend-item">
      <span class="legend-dot axiom"></span>
      <span>Core Axiom</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot pillar"></span>
      <span>Foundational Pillar</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot tool"></span>
      <span>Interactive Tool</span>
    </div>
  </div>
  
  <div id="journey-map" class="journey-map">
    <!-- SVG will be injected here -->
  </div>
  
  <div class="journey-details" id="journey-details">
    <h3>Click any node to explore</h3>
    <p>Navigate through axioms, pillars, and tools to build your understanding.</p>
  </div>
</div>
```

```javascript
// docs/javascripts/journey-map.js
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
    this.edges.forEach(edge => {
      if (edge.from === nodeId || edge.to === nodeId) {
        const edgeElem = this.container.querySelector(
          `line[x1="${this.nodes.find(n => n.id === edge.from).x}"][y1="${this.nodes.find(n => n.id === edge.from).y}"]`
        );
        if (edgeElem) {
          edgeElem.style.stroke = 'rgba(129, 140, 248, 0.6)';
          edgeElem.style.strokeWidth = '3';
        }
      }
    });
  }
  
  animateEntrance() {
    const nodes = this.container.querySelectorAll('.node');
    nodes.forEach((node, index) => {
      node.style.opacity = '0';
      node.style.transform = `translate(${node.transform.baseVal[0].matrix.e}px, ${node.transform.baseVal[0].matrix.f + 20}px)`;
      
      setTimeout(() => {
        node.style.transition = 'all 0.5s ease-out';
        node.style.opacity = '1';
        node.style.transform = `translate(${node.transform.baseVal[0].matrix.e}px, ${node.transform.baseVal[0].matrix.f}px)`;
      }, index * 50);
    });
  }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('journey-map')) {
    new JourneyMap('journey-map');
  }
});
```

```css
/* docs/stylesheets/journey-map.css */
#journey-map-container {
  margin: 3rem 0;
  padding: 2rem;
  background: var(--ds-bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
}

.journey-legend {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--ds-text-secondary);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.axiom {
  background: linear-gradient(135deg, #5B5FC7 0%, #818CF8 100%);
}

.legend-dot.pillar {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
}

.legend-dot.tool {
  background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
}

#journey-map {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto 2rem;
  cursor: grab;
}

#journey-map:active {
  cursor: grabbing;
}

.node {
  cursor: pointer;
  transition: all 0.3s ease;
}

.node-circle {
  transition: all 0.3s ease;
}

.node-icon {
  pointer-events: none;
  user-select: none;
}

.node-label {
  pointer-events: none;
  user-select: none;
}

.edge-line {
  transition: all 0.3s ease;
  pointer-events: none;
}

.journey-details {
  background: var(--ds-bg-primary);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  border: 1px solid var(--ds-border-color);
}

.journey-details h3 {
  margin-top: 0;
  font-size: 1.5rem;
  color: var(--ds-text-primary);
}

.journey-details p {
  color: var(--ds-text-secondary);
  margin: 1rem 0;
}

.journey-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #5B5FC7 0%, #818CF8 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.journey-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(91, 95, 199, 0.3);
}

/* Responsive design */
@media (max-width: 768px) {
  #journey-map-container {
    padding: 1rem;
  }
  
  .journey-legend {
    font-size: 0.8rem;
    gap: 1rem;
  }
  
  .journey-details {
    padding: 1rem;
  }
}
```

---

## 4. Phase 3: Content Enhancement & Visual Breaks (Week 5-6)

### 4.1 Enhanced Content Components

#### Key Takeaway Boxes

```css
/* docs/stylesheets/extra.css - Key Takeaway Component */
.key-takeaway {
  position: relative;
  margin: 2rem 0;
  padding: 1.5rem 1.5rem 1.5rem 4rem;
  background: linear-gradient(135deg, var(--ds-bg-secondary) 0%, var(--ds-bg-primary) 100%);
  border-radius: 12px;
  border-left: 4px solid #00BCD4;
  box-shadow: var(--shadow-md);
}

.key-takeaway::before {
  content: '💡';
  position: absolute;
  left: 1rem;
  top: 1.5rem;
  font-size: 2rem;
}

.key-takeaway h4 {
  margin: 0 0 0.5rem 0;
  color: #00BCD4;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.key-takeaway ul {
  margin: 0;
  padding-left: 1.5rem;
}

.key-takeaway li {
  margin-bottom: 0.5rem;
  color: var(--ds-text-primary);
}
```

Usage example in content:
```markdown
<!-- docs/part1-axioms/axiom-1-latency/index.md -->
<div class="key-takeaway">
<h4>Key Takeaways</h4>
<ul>
<li>Latency is bounded by the speed of light (299,792 km/s)</li>
<li>Network distance ≠ geographic distance due to routing</li>
<li>Every hop adds processing delay beyond propagation</li>
<li>Caching is a fundamental latency mitigation strategy</li>
</ul>
</div>
```

#### Interactive Concept Cards

```html
<!-- Template for concept cards -->
<div class="concept-card-grid">
  <div class="concept-card" data-concept="latency-formula">
    <div class="concept-icon">🎯</div>
    <h4>The Latency Formula</h4>
    <div class="concept-content">
      <code>Total Latency = Propagation + Transmission + Processing + Queuing</code>
    </div>
    <div class="concept-hover-detail">
      <p><strong>Propagation:</strong> Distance ÷ Speed of Light</p>
      <p><strong>Transmission:</strong> Data Size ÷ Bandwidth</p>
      <p><strong>Processing:</strong> Computation Time</p>
      <p><strong>Queuing:</strong> Wait Time in Buffers</p>
    </div>
  </div>
  
  <div class="concept-card" data-concept="latency-impact">
    <div class="concept-icon">⚡</div>
    <h4>Real-World Impact</h4>
    <div class="concept-content">
      <span class="metric">+100ms latency</span>
      <span class="impact">= -1% revenue (Amazon)</span>
    </div>
    <div class="concept-hover-detail">
      <p>Every 100ms of latency costs Amazon 1% in sales</p>
      <p>Google found 500ms delays caused 20% drop in traffic</p>
    </div>
  </div>
</div>
```

```css
/* docs/stylesheets/extra.css - Concept Cards */
.concept-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.concept-card {
  position: relative;
  padding: 2rem;
  background: var(--ds-bg-primary);
  border: 2px solid var(--ds-border-color);
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.concept-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #5B5FC7 0%, #00BCD4 100%);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.concept-card:hover::before {
  transform: scaleX(1);
}

.concept-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: #5B5FC7;
}

.concept-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.concept-card h4 {
  margin: 0 0 1rem 0;
  color: var(--ds-text-primary);
  font-size: 1.25rem;
}

.concept-content {
  color: var(--ds-text-secondary);
}

.concept-content code {
  display: block;
  margin: 0.5rem 0;
  padding: 0.5rem;
  background: var(--ds-bg-secondary);
  border-radius: 4px;
  font-size: 0.9rem;
}

.concept-hover-detail {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  padding: 1.5rem;
  background: var(--ds-bg-primary);
  border: 2px solid #5B5FC7;
  border-top: none;
  border-radius: 0 0 16px 16px;
  opacity: 0;
  transform: translateY(-100%);
  transition: all 0.3s ease;
  pointer-events: none;
}

.concept-card:hover .concept-hover-detail {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.metric {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #EF4444;
  margin-bottom: 0.5rem;
}

.impact {
  display: block;
  font-size: 1.1rem;
  color: var(--ds-text-primary);
}
```

### 4.2 Progressive Disclosure for Dense Content

```html
<!-- Template for collapsible deep dives -->
<details class="deep-dive">
  <summary>
    <span class="deep-dive-icon">🔍</span>
    <span class="deep-dive-title">Deep Dive: Mathematical Proof of CAP Theorem</span>
    <span class="deep-dive-duration">10 min read</span>
  </summary>
  <div class="deep-dive-content">
    <!-- Advanced content here -->
  </div>
</details>
```

```css
/* docs/stylesheets/extra.css - Deep Dive Sections */
.deep-dive {
  margin: 2rem 0;
  border: 1px solid var(--ds-border-color);
  border-radius: 12px;
  overflow: hidden;
  background: var(--ds-bg-secondary);
}

.deep-dive summary {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s ease;
}

.deep-dive summary:hover {
  background-color: var(--ds-bg-primary);
}

.deep-dive summary::-webkit-details-marker {
  display: none;
}

.deep-dive-icon {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.deep-dive[open] .deep-dive-icon {
  transform: rotate(45deg);
}

.deep-dive-title {
  flex: 1;
  font-weight: 600;
  color: var(--ds-text-primary);
}

.deep-dive-duration {
  font-size: 0.9rem;
  color: var(--ds-text-secondary);
  background: var(--ds-bg-primary);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
}

.deep-dive-content {
  padding: 0 1.5rem 1.5rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 5. Phase 4: Static Interactive Tools (Week 7-8)

### 5.1 Client-Side Latency Calculator

```html
<!-- docs/tools/latency-calculator.md -->
# Latency Calculator

<div id="latency-calculator" class="interactive-tool">
  <div class="tool-inputs">
    <div class="input-group">
      <label for="distance">Distance (km)</label>
      <input type="number" id="distance" value="1000" min="0" max="20000">
      <small>Geographic distance between nodes</small>
    </div>
    
    <div class="input-group">
      <label for="hops">Network Hops</label>
      <input type="number" id="hops" value="5" min="1" max="50">
      <small>Number of routers/switches</small>
    </div>
    
    <div class="input-group">
      <label for="processing">Processing Time (ms)</label>
      <input type="number" id="processing" value="2" min="0" max="100" step="0.1">
      <small>Per-hop processing delay</small>
    </div>
    
    <div class="input-group">
      <label for="bandwidth">Bandwidth (Mbps)</label>
      <input type="number" id="bandwidth" value="1000" min="1" max="100000">
      <small>Link bandwidth</small>
    </div>
    
    <div class="input-group">
      <label for="payload">Payload Size (KB)</label>
      <input type="number" id="payload" value="1" min="0.1" max="1000" step="0.1">
      <small>Data size to transfer</small>
    </div>
  </div>
  
  <div class="tool-visualization">
    <canvas id="latency-viz"></canvas>
  </div>
  
  <div class="tool-results">
    <h3>Results</h3>
    <div class="result-grid">
      <div class="result-item">
        <span class="result-label">Propagation Delay</span>
        <span class="result-value" id="prop-delay">0 ms</span>
      </div>
      <div class="result-item">
        <span class="result-label">Processing Delay</span>
        <span class="result-value" id="proc-delay">0 ms</span>
      </div>
      <div class="result-item">
        <span class="result-label">Transmission Delay</span>
        <span class="result-value" id="trans-delay">0 ms</span>
      </div>
      <div class="result-item highlight">
        <span class="result-label">Total Latency</span>
        <span class="result-value" id="total-delay">0 ms</span>
      </div>
    </div>
    
    <div class="result-insights">
      <h4>💡 Insights</h4>
      <ul id="insights-list">
        <!-- Dynamically populated -->
      </ul>
    </div>
  </div>
</div>

<script src="/javascripts/latency-calculator.js"></script>
```

```javascript
// docs/javascripts/latency-calculator.js
class LatencyCalculator {
  constructor() {
    this.inputs = {
      distance: document.getElementById('distance'),
      hops: document.getElementById('hops'),
      processing: document.getElementById('processing'),
      bandwidth: document.getElementById('bandwidth'),
      payload: document.getElementById('payload')
    };
    
    this.results = {
      propDelay: document.getElementById('prop-delay'),
      procDelay: document.getElementById('proc-delay'),
      transDelay: document.getElementById('trans-delay'),
      totalDelay: document.getElementById('total-delay')
    };
    
    this.canvas = document.getElementById('latency-viz');
    this.ctx = this.canvas.getContext('2d');
    this.insightsList = document.getElementById('insights-list');
    
    this.SPEED_OF_LIGHT = 299792; // km/s
    this.FIBER_SPEED = this.SPEED_OF_LIGHT * 0.67; // Speed in fiber optic
    
    this.init();
  }
  
  init() {
    // Set up canvas
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    
    // Attach event listeners
    Object.values(this.inputs).forEach(input => {
      input.addEventListener('input', () => this.calculate());
    });
    
    // Initial calculation
    this.calculate();
  }
  
  resizeCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = 300;
  }
  
  calculate() {
    const distance = parseFloat(this.inputs.distance.value);
    const hops = parseInt(this.inputs.hops.value);
    const processing = parseFloat(this.inputs.processing.value);
    const bandwidth = parseFloat(this.inputs.bandwidth.value);
    const payload = parseFloat(this.inputs.payload.value);
    
    // Calculate delays
    const propagationDelay = (distance / this.FIBER_SPEED) * 1000; // ms
    const processingDelay = hops * processing; // ms
    const transmissionDelay = (payload * 8) / bandwidth; // ms (KB to Mb)
    const totalDelay = propagationDelay + processingDelay + transmissionDelay;
    
    // Update results
    this.results.propDelay.textContent = `${propagationDelay.toFixed(2)} ms`;
    this.results.procDelay.textContent = `${processingDelay.toFixed(2)} ms`;
    this.results.transDelay.textContent = `${transmissionDelay.toFixed(2)} ms`;
    this.results.totalDelay.textContent = `${totalDelay.toFixed(2)} ms`;
    
    // Update visualization
    this.drawVisualization({
      propagation: propagationDelay,
      processing: processingDelay,
      transmission: transmissionDelay,
      total: totalDelay
    });
    
    // Generate insights
    this.generateInsights({
      distance, hops, totalDelay, 
      propagationDelay, processingDelay, transmissionDelay
    });
  }
  
  drawVisualization(delays) {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background
    ctx.fillStyle = getComputedStyle(document.documentElement)
      .getPropertyValue('--ds-bg-secondary');
    ctx.fillRect(0, 0, width, height);
    
    // Calculate proportions
    const total = delays.total;
    const propWidth = (delays.propagation / total) * (width - 40);
    const procWidth = (delays.processing / total) * (width - 40);
    const transWidth = (delays.transmission / total) * (width - 40);
    
    // Draw stacked bar
    const barHeight = 60;
    const barY = height / 2 - barHeight / 2;
    let currentX = 20;
    
    // Propagation delay
    ctx.fillStyle = '#5B5FC7';
    ctx.fillRect(currentX, barY, propWidth, barHeight);
    
    // Processing delay
    currentX += propWidth;
    ctx.fillStyle = '#00BCD4';
    ctx.fillRect(currentX, barY, procWidth, barHeight);
    
    // Transmission delay
    currentX += procWidth;
    ctx.fillStyle = '#10B981';
    ctx.fillRect(currentX, barY, transWidth, barHeight);
    
    // Draw labels
    ctx.fillStyle = getComputedStyle(document.documentElement)
      .getPropertyValue('--ds-text-primary');
    ctx.font = '14px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    
    // Legend
    const legendY = barY + barHeight + 40;
    const legendItems = [
      { color: '#5B5FC7', label: 'Propagation' },
      { color: '#00BCD4', label: 'Processing' },
      { color: '#10B981', label: 'Transmission' }
    ];
    
    legendItems.forEach((item, index) => {
      const legendX = width / 2 - 150 + index * 100;
      
      // Color box
      ctx.fillStyle = item.color;
      ctx.fillRect(legendX - 40, legendY - 10, 20, 20);
      
      // Label
      ctx.fillStyle = getComputedStyle(document.documentElement)
        .getPropertyValue('--ds-text-primary');
      ctx.textAlign = 'left';
      ctx.fillText(item.label, legendX - 15, legendY);
    });
    
    // Draw percentage labels on bars if they're wide enough
    ctx.fillStyle = 'white';
    ctx.font = '12px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    
    currentX = 20;
    if (propWidth > 50) {
      const percentage = ((delays.propagation / total) * 100).toFixed(1);
      ctx.fillText(`${percentage}%`, currentX + propWidth / 2, barY + barHeight / 2 + 5);
    }
    
    currentX += propWidth;
    if (procWidth > 50) {
      const percentage = ((delays.processing / total) * 100).toFixed(1);
      ctx.fillText(`${percentage}%`, currentX + procWidth / 2, barY + barHeight / 2 + 5);
    }
    
    currentX += procWidth;
    if (transWidth > 50) {
      const percentage = ((delays.transmission / total) * 100).toFixed(1);
      ctx.fillText(`${percentage}%`, currentX + transWidth / 2, barY + barHeight / 2 + 5);
    }
  }
  
  generateInsights(data) {
    const insights = [];
    
    // Dominant factor analysis
    const factors = [
      { name: 'propagation', value: data.propagationDelay },
      { name: 'processing', value: data.processingDelay },
      { name: 'transmission', value: data.transmissionDelay }
    ];
    
    const dominant = factors.reduce((max, factor) => 
      factor.value > max.value ? factor : max
    );
    
    if (dominant.name === 'propagation') {
      insights.push(`Distance is your primary constraint. Consider edge computing or CDNs to reduce geographic distance.`);
    } else if (dominant.name === 'processing') {
      insights.push(`Processing delay dominates (${(dominant.value / data.totalDelay * 100).toFixed(1)}%). Reduce network hops or upgrade router performance.`);
    } else {
      insights.push(`Transmission delay is significant. Consider increasing bandwidth or compressing data.`);
    }
    
    // RTT calculation
    const rtt = data.totalDelay * 2;
    insights.push(`Round-trip time (RTT): ${rtt.toFixed(2)} ms`);
    
    // Geographic context
    if (data.distance > 10000) {
      insights.push(`This is intercontinental distance. Expect minimum ${(data.distance / this.FIBER_SPEED * 1000).toFixed(0)}ms due to physics alone.`);
    } else if (data.distance > 1000) {
      insights.push(`Regional distance detected. Consider multi-region deployment for better latency.`);
    }
    
    // Performance thresholds
    if (rtt > 100) {
      insights.push(`⚠️ RTT > 100ms will noticeably impact user experience for interactive applications.`);
    }
    
    if (data.hops > 15) {
      insights.push(`High hop count (${data.hops}) suggests suboptimal routing. Direct peering could help.`);
    }
    
    // Update insights list
    this.insightsList.innerHTML = insights
      .map(insight => `<li>${insight}</li>`)
      .join('');
  }
}

// Initialize calculator when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('latency-calculator')) {
    new LatencyCalculator();
  }
});
```

```css
/* docs/stylesheets/extra.css - Interactive Tools */
.interactive-tool {
  margin: 2rem 0;
  padding: 2rem;
  background: var(--ds-bg-secondary);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
}

.tool-inputs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: var(--ds-text-primary);
  margin-bottom: 0.5rem;
}

.input-group input {
  padding: 0.75rem;
  border: 2px solid var(--ds-border-color);
  border-radius: 8px;
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #5B5FC7;
}

.input-group small {
  margin-top: 0.25rem;
  color: var(--ds-text-secondary);
  font-size: 0.85rem;
}

.tool-visualization {
  margin: 2rem 0;
  padding: 1rem;
  background: var(--ds-bg-primary);
  border-radius: 12px;
  border: 1px solid var(--ds-border-color);
}

.tool-visualization canvas {
  width: 100%;
  height: 300px;
}

.tool-results {
  margin-top: 2rem;
}

.tool-results h3 {
  margin-bottom: 1rem;
  color: var(--ds-text-primary);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.result-item {
  padding: 1.5rem;
  background: var(--ds-bg-primary);
  border-radius: 12px;
  border: 1px solid var(--ds-border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.result-item.highlight {
  background: linear-gradient(135deg, #5B5FC7 0%, #818CF8 100%);
  border: none;
  color: white;
}

.result-label {
  font-size: 0.9rem;
  color: var(--ds-text-secondary);
  margin-bottom: 0.5rem;
}

.result-item.highlight .result-label {
  color: rgba(255, 255, 255, 0.9);
}

.result-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--ds-text-primary);
}

.result-item.highlight .result-value {
  color: white;
}

.result-insights {
  padding: 1.5rem;
  background: var(--ds-bg-primary);
  border-radius: 12px;
  border: 1px solid var(--ds-border-color);
}

.result-insights h4 {
  margin-top: 0;
  color: var(--ds-text-primary);
}

.result-insights ul {
  margin: 0;
  padding-left: 1.5rem;
}

.result-insights li {
  margin-bottom: 0.75rem;
  color: var(--ds-text-secondary);
  line-height: 1.6;
}
```

### 5.2 Inline Mini-Calculators

```javascript
// docs/javascripts/inline-calculators.js
class InlineCalculator {
  constructor(element) {
    this.element = element;
    this.type = element.dataset.calculatorType;
    this.init();
  }
  
  init() {
    switch (this.type) {
      case 'latency':
        this.initLatencyCalc();
        break;
      case 'capacity':
        this.initCapacityCalc();
        break;
      case 'availability':
        this.initAvailabilityCalc();
        break;
    }
  }
  
  initLatencyCalc() {
    this.element.innerHTML = `
      <div class="inline-calc">
        <h4>Quick Latency Check</h4>
        <div class="calc-row">
          <label>Distance (km):</label>
          <input type="number" class="calc-input" data-param="distance" value="1000">
        </div>
        <div class="calc-result">
          <span>Minimum latency:</span>
          <strong class="calc-output">3.34 ms</strong>
        </div>
      </div>
    `;
    
    const input = this.element.querySelector('.calc-input');
    const output = this.element.querySelector('.calc-output');
    
    input.addEventListener('input', () => {
      const distance = parseFloat(input.value);
      const latency = (distance / 200000) * 1000; // Approx fiber speed
      output.textContent = `${latency.toFixed(2)} ms`;
    });
  }
  
  initCapacityCalc() {
    this.element.innerHTML = `
      <div class="inline-calc">
        <h4>Throughput Calculator</h4>
        <div class="calc-row">
          <label>Requests/sec:</label>
          <input type="number" class="calc-input" data-param="rps" value="1000">
        </div>
        <div class="calc-row">
          <label>Latency (ms):</label>
          <input type="number" class="calc-input" data-param="latency" value="50">
        </div>
        <div class="calc-result">
          <span>Concurrent requests:</span>
          <strong class="calc-output">50</strong>
        </div>
      </div>
    `;
    
    const inputs = this.element.querySelectorAll('.calc-input');
    const output = this.element.querySelector('.calc-output');
    
    const calculate = () => {
      const rps = parseFloat(inputs[0].value);
      const latency = parseFloat(inputs[1].value);
      const concurrent = rps * (latency / 1000);
      output.textContent = Math.ceil(concurrent);
    };
    
    inputs.forEach(input => {
      input.addEventListener('input', calculate);
    });
  }
  
  initAvailabilityCalc() {
    this.element.innerHTML = `
      <div class="inline-calc">
        <h4>System Availability</h4>
        <div class="calc-row">
          <label>Components:</label>
          <input type="number" class="calc-input" data-param="components" value="3">
        </div>
        <div class="calc-row">
          <label>Each availability:</label>
          <input type="number" class="calc-input" data-param="availability" value="99.9" step="0.1">
        </div>
        <div class="calc-result">
          <span>System availability:</span>
          <strong class="calc-output">99.7%</strong>
        </div>
        <div class="calc-note">
          Downtime: <span class="downtime-output">2.63 hours/year</span>
        </div>
      </div>
    `;
    
    const inputs = this.element.querySelectorAll('.calc-input');
    const output = this.element.querySelector('.calc-output');
    const downtimeOutput = this.element.querySelector('.downtime-output');
    
    const calculate = () => {
      const components = parseInt(inputs[0].value);
      const availability = parseFloat(inputs[1].value) / 100;
      const systemAvail = Math.pow(availability, components) * 100;
      
      output.textContent = `${systemAvail.toFixed(2)}%`;
      
      // Calculate downtime
      const yearlyHours = 365 * 24;
      const downtime = yearlyHours * (1 - systemAvail / 100);
      
      if (downtime < 1) {
        downtimeOutput.textContent = `${(downtime * 60).toFixed(1)} minutes/year`;
      } else if (downtime < 24) {
        downtimeOutput.textContent = `${downtime.toFixed(1)} hours/year`;
      } else {
        downtimeOutput.textContent = `${(downtime / 24).toFixed(1)} days/year`;
      }
    };
    
    inputs.forEach(input => {
      input.addEventListener('input', calculate);
    });
    
    calculate();
  }
}

// Initialize all inline calculators
document.addEventListener('DOMContentLoaded', () => {
  const calculators = document.querySelectorAll('[data-calculator-type]');
  calculators.forEach(calc => new InlineCalculator(calc));
});
```

```css
/* docs/stylesheets/extra.css - Inline Calculators */
.inline-calc {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background: var(--ds-bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--ds-border-color);
  max-width: 400px;
}

.inline-calc h4 {
  margin: 0 0 1rem 0;
  color: var(--ds-text-primary);
  font-size: 1.1rem;
}

.calc-row {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.calc-row label {
  flex: 1;
  color: var(--ds-text-secondary);
  font-size: 0.9rem;
}

.calc-input {
  width: 100px;
  padding: 0.5rem;
  border: 1px solid var(--ds-border-color);
  border-radius: 6px;
  background: var(--ds-bg-primary);
  color: var(--ds-text-primary);
  text-align: right;
}

.calc-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--ds-border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calc-result span {
  color: var(--ds-text-secondary);
}

.calc-output {
  font-size: 1.5rem;
  color: #5B5FC7;
}

.calc-note {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--ds-text-secondary);
}

.downtime-output {
  color: #EF4444;
  font-weight: 600;
}
```

---

## 6. Phase 5: Navigation & Information Architecture (Week 9-10)

### 6.1 Enhanced Breadcrumbs

```javascript
// docs/javascripts/breadcrumbs.js
class BreadcrumbNav {
  constructor() {
    this.init();
  }
  
  init() {
    const breadcrumbContainer = this.createBreadcrumbContainer();
    const mainContent = document.querySelector('.md-content');
    
    if (mainContent && mainContent.firstChild) {
      mainContent.insertBefore(breadcrumbContainer, mainContent.firstChild);
    }
    
    this.updateBreadcrumbs();
  }
  
  createBreadcrumbContainer() {
    const container = document.createElement('nav');
    container.className = 'breadcrumb-nav';
    container.setAttribute('aria-label', 'Breadcrumb');
    return container;
  }
  
  updateBreadcrumbs() {
    const container = document.querySelector('.breadcrumb-nav');
    const path = window.location.pathname;
    const segments = path.split('/').filter(s => s);
    
    let breadcrumbHTML = '<ol class="breadcrumb-list">';
    breadcrumbHTML += '<li class="breadcrumb-item"><a href="/">Home</a></li>';
    
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === segments.length - 1;
      
      // Format segment name
      const name = this.formatSegmentName(segment);
      
      if (isLast) {
        breadcrumbHTML += `<li class="breadcrumb-item active" aria-current="page">${name}</li>`;
      } else {
        breadcrumbHTML += `<li class="breadcrumb-item"><a href="${currentPath}/">${name}</a></li>`;
      }
    });
    
    breadcrumbHTML += '</ol>';
    container.innerHTML = breadcrumbHTML;
  }
  
  formatSegmentName(segment) {
    // Special cases
    const nameMap = {
      'part1-axioms': 'Part I: Axioms',
      'part2-pillars': 'Part II: Pillars',
      'axiom-1-latency': 'Axiom 1: Latency',
      'axiom-2-capacity': 'Axiom 2: Capacity',
      'axiom-3-failure': 'Axiom 3: Failure',
      'axiom-4-concurrency': 'Axiom 4: Concurrency',
      'axiom-5-coordination': 'Axiom 5: Coordination',
      'axiom-6-observability': 'Axiom 6: Observability',
      'axiom-7-human-interface': 'Axiom 7: Human Interface',
      'axiom-8-economics': 'Axiom 8: Economics',
      'pillar-1-work': 'Pillar 1: Work',
      'pillar-2-state': 'Pillar 2: State',
      'pillar-3-truth': 'Pillar 3: Truth',
      'pillar-4-control': 'Pillar 4: Control',
      'pillar-5-intelligence': 'Pillar 5: Intelligence',
      'pillar-6-trust': 'Pillar 6: Trust'
    };
    
    return nameMap[segment] || segment
      .replace(/-/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }
}

// Initialize breadcrumbs
document.addEventListener('DOMContentLoaded', () => {
  new BreadcrumbNav();
});
```

```css
/* docs/stylesheets/extra.css - Breadcrumbs */
.breadcrumb-nav {
  margin-bottom: 2rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--ds-border-color);
}

.breadcrumb-list {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
  font-size: 0.9rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: '›';
  margin: 0 0.75rem;
  color: var(--ds-text-secondary);
}

.breadcrumb-item a {
  color: var(--ds-text-secondary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-item a:hover {
  color: #5B5FC7;
}

.breadcrumb-item.active {
  color: var(--ds-text-primary);
  font-weight: 600;
}
```

### 6.2 Reading Progress Indicator

```javascript
// docs/javascripts/reading-progress.js
class ReadingProgress {
  constructor() {
    this.createProgressBar();
    this.attachScrollListener();
  }
  
  createProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = `
      <div class="reading-progress-bar"></div>
      <div class="reading-progress-text">
        <span class="progress-percentage">0%</span>
        <span class="time-remaining">~15 min left</span>
      </div>
    `;
    
    document.body.appendChild(progressBar);
    
    this.progressBar = progressBar.querySelector('.reading-progress-bar');
    this.progressText = progressBar.querySelector('.progress-percentage');
    this.timeText = progressBar.querySelector('.time-remaining');
  }
  
  attachScrollListener() {
    let ticking = false;
    
    const updateProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrollTop = window.scrollY;
      
      const progress = Math.min((scrollTop / documentHeight) * 100, 100);
      
      this.progressBar.style.width = `${progress}%`;
      this.progressText.textContent = `${Math.round(progress)}%`;
      
      // Update time remaining
      const wordsPerMinute = 200;
      const remainingHeight = documentHeight - scrollTop;
      const remainingWords = (remainingHeight / windowHeight) * 500; // Estimate
      const remainingMinutes = Math.ceil(remainingWords / wordsPerMinute);
      
      if (remainingMinutes > 0) {
        this.timeText.textContent = `~${remainingMinutes} min left`;
      } else {
        this.timeText.textContent = 'Complete!';
      }
      
      ticking = false;
    };
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateProgress);
        ticking = true;
      }
    });
    
    // Initial update
    updateProgress();
  }
}

// Initialize reading progress
document.addEventListener('DOMContentLoaded', () => {
  // Only show on content pages, not on homepage
  if (!window.location.pathname.match(/^\/?$/)) {
    new ReadingProgress();
  }
});
```

```css
/* docs/stylesheets/extra.css - Reading Progress */
.reading-progress {
  position: fixed;
  top: 64px; /* Below header */
  left: 0;
  right: 0;
  height: 40px;
  background: var(--ds-bg-primary);
  border-bottom: 1px solid var(--ds-border-color);
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 0 2rem;
  box-shadow: var(--shadow-sm);
}

.reading-progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #5B5FC7 0%, #00BCD4 100%);
  transition: width 0.3s ease;
}

.reading-progress-text {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 0.85rem;
}

.progress-percentage {
  color: #5B5FC7;
  font-weight: 600;
}

.time-remaining {
  color: var(--ds-text-secondary);
}

/* Adjust content margin when progress bar is present */
.reading-progress ~ .md-container {
  margin-top: 40px;
}

/* Hide on mobile */
@media (max-width: 768px) {
  .reading-progress {
    height: 30px;
    padding: 0 1rem;
  }
  
  .reading-progress-text {
    font-size: 0.75rem;
  }
}
```

### 6.3 Table of Contents Enhancement

```javascript
// docs/javascripts/toc-enhancement.js
class EnhancedTOC {
  constructor() {
    this.tocContainer = document.querySelector('.md-sidebar--secondary');
    if (!this.tocContainer) return;
    
    this.enhanceTOC();
    this.addScrollSpy();
  }
  
  enhanceTOC() {
    // Add reading time estimates
    const tocItems = this.tocContainer.querySelectorAll('.md-nav__item');
    
    tocItems.forEach(item => {
      const link = item.querySelector('.md-nav__link');
      if (!link) return;
      
      const targetId = link.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      
      if (targetSection) {
        const wordCount = this.countWords(targetSection);
        const readingTime = Math.ceil(wordCount / 200);
        
        if (readingTime > 0) {
          const timeSpan = document.createElement('span');
          timeSpan.className = 'toc-reading-time';
          timeSpan.textContent = `${readingTime} min`;
          link.appendChild(timeSpan);
        }
      }
    });
  }
  
  countWords(element) {
    const text = element.textContent || '';
    return text.trim().split(/\s+/).length;
  }
  
  addScrollSpy() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const id = entry.target.getAttribute('id');
          const tocLink = this.tocContainer.querySelector(`a[href="#${id}"]`);
          
          if (tocLink) {
            if (entry.isIntersecting) {
              // Remove active class from all
              this.tocContainer.querySelectorAll('.md-nav__link--active')
                .forEach(link => link.classList.remove('md-nav__link--active'));
              
              // Add active class
              tocLink.classList.add('md-nav__link--active');
              
              // Scroll TOC to keep active item visible
              const tocNav = tocLink.closest('.md-nav');
              if (tocNav) {
                const linkRect = tocLink.getBoundingClientRect();
                const navRect = tocNav.getBoundingClientRect();
                
                if (linkRect.top < navRect.top || linkRect.bottom > navRect.bottom) {
                  tocLink.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
              }
            }
          }
        });
      },
      { 
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
      }
    );
    
    // Observe all sections with IDs
    document.querySelectorAll('section[id], h2[id], h3[id], h4[id]').forEach(section => {
      observer.observe(section);
    });
  }
}

// Initialize enhanced TOC
document.addEventListener('DOMContentLoaded', () => {
  new EnhancedTOC();
});
```

```css
/* docs/stylesheets/extra.css - Enhanced TOC */
.toc-reading-time {
  margin-left: auto;
  padding-left: 1rem;
  font-size: 0.75rem;
  color: var(--ds-text-secondary);
  opacity: 0.7;
}

.md-nav__link--active {
  color: #5B5FC7 !important;
  font-weight: 600;
  position: relative;
}

.md-nav__link--active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #5B5FC7;
  border-radius: 2px;
}

/* Smooth scrolling for TOC */
.md-sidebar--secondary {
  scroll-behavior: smooth;
}

/* TOC progress indicator */
.md-nav--secondary {
  position: relative;
}

.md-nav--secondary::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 1px;
  height: 100%;
  background: var(--ds-border-color);
}
```

---

## 7. Phase 6: Mobile Optimization (Week 11)

### 7.1 Mobile Navigation

```css
/* docs/stylesheets/extra.css - Mobile Navigation */
@media (max-width: 768px) {
  /* Bottom tab navigation */
  .mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: var(--ds-bg-primary);
    border-top: 1px solid var(--ds-border-color);
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 200;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .mobile-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-decoration: none;
    color: var(--ds-text-secondary);
    transition: color 0.3s ease;
  }
  
  .mobile-nav-item.active {
    color: #5B5FC7;
  }
  
  .mobile-nav-icon {
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
  }
  
  .mobile-nav-label {
    font-size: 0.75rem;
  }
  
  /* Adjust content for bottom nav */
  .md-container {
    padding-bottom: 70px;
  }
  
  /* Swipe navigation hints */
  .swipe-hint {
    position: fixed;
    bottom: 70px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
  }
  
  .swipe-hint.show {
    opacity: 1;
  }
}

/* Touch-friendly components */
@media (hover: none) {
  .concept-card {
    min-height: 120px;
  }
  
  .node {
    cursor: default;
  }
  
  .deep-dive summary {
    padding: 1.5rem;
    -webkit-tap-highlight-color: rgba(91, 95, 199, 0.1);
  }
  
  .calc-input {
    font-size: 16px; /* Prevent zoom on iOS */
  }
}
```

```javascript
// docs/javascripts/mobile-nav.js
class MobileNavigation {
  constructor() {
    if (window.innerWidth > 768) return;
    
    this.createBottomNav();
    this.initSwipeGestures();
  }
  
  createBottomNav() {
    const nav = document.createElement('nav');
    nav.className = 'mobile-bottom-nav';
    
    const items = [
      { icon: '🏠', label: 'Home', href: '/' },
      { icon: '⚡', label: 'Axioms', href: '/part1-axioms/' },
      { icon: '🏛️', label: 'Pillars', href: '/part2-pillars/' },
      { icon: '🧮', label: 'Tools', href: '/tools/' },
      { icon: '📚', label: 'Reference', href: '/reference/' }
    ];
    
    items.forEach(item => {
      const link = document.createElement('a');
      link.className = 'mobile-nav-item';
      link.href = item.href;
      
      if (window.location.pathname.startsWith(item.href) && item.href !== '/') {
        link.classList.add('active');
      } else if (item.href === '/' && window.location.pathname === '/') {
        link.classList.add('active');
      }
      
      link.innerHTML = `
        <span class="mobile-nav-icon">${item.icon}</span>
        <span class="mobile-nav-label">${item.label}</span>
      `;
      
      nav.appendChild(link);
    });
    
    document.body.appendChild(nav);
  }
  
  initSwipeGestures() {
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      this.handleSwipe();
    });
    
    // Swipe hint
    const hint = document.createElement('div');
    hint.className = 'swipe-hint';
    hint.textContent = 'Swipe to navigate';
    document.body.appendChild(hint);
    
    // Show hint on first visit
    if (!localStorage.getItem('swipeHintShown')) {
      setTimeout(() => {
        hint.classList.add('show');
        setTimeout(() => {
          hint.classList.remove('show');
          localStorage.setItem('swipeHintShown', 'true');
        }, 3000);
      }, 2000);
    }
  }
  
  handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchEndX - touchStartX;
    
    if (Math.abs(diff) < swipeThreshold) return;
    
    // Get current page navigation
    const prevLink = document.querySelector('.md-footer__link--prev');
    const nextLink = document.querySelector('.md-footer__link--next');
    
    if (diff > 0 && prevLink) {
      // Swipe right - go to previous
      window.location.href = prevLink.href;
    } else if (diff < 0 && nextLink) {
      // Swipe left - go to next
      window.location.href = nextLink.href;
    }
  }
}

// Initialize mobile navigation
document.addEventListener('DOMContentLoaded', () => {
  new MobileNavigation();
});
```

---

## 8. Phase 7: Performance & Polish (Week 12)

### 8.1 Image Lazy Loading

```javascript
// docs/javascripts/lazy-loading.js
class LazyLoader {
  constructor() {
    this.images = document.querySelectorAll('img[data-src]');
    this.diagrams = document.querySelectorAll('.mermaid[data-lazy]');
    
    this.imageObserver = new IntersectionObserver(
      this.loadImages.bind(this),
      { rootMargin: '50px' }
    );
    
    this.diagramObserver = new IntersectionObserver(
      this.loadDiagrams.bind(this),
      { rootMargin: '100px' }
    );
    
    this.observe();
  }
  
  observe() {
    this.images.forEach(img => this.imageObserver.observe(img));
    this.diagrams.forEach(diagram => this.diagramObserver.observe(diagram));
  }
  
  loadImages(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        this.imageObserver.unobserve(img);
      }
    });
  }
  
  loadDiagrams(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const diagram = entry.target;
        // Trigger Mermaid rendering
        if (window.mermaid) {
          mermaid.init(undefined, diagram);
        }
        this.diagramObserver.unobserve(diagram);
      }
    });
  }
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', () => {
  new LazyLoader();
});
```

### 8.2 Print Styles

```css
/* docs/stylesheets/extra.css - Print Styles */
@media print {
  /* Hide navigation elements */
  .md-header,
  .md-sidebar,
  .md-footer,
  .breadcrumb-nav,
  .reading-progress,
  .mobile-bottom-nav,
  .journey-map-container {
    display: none !important;
  }
  
  /* Optimize content for print */
  .md-content {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Page breaks */
  h1, h2 {
    page-break-before: always;
  }
  
  h3, h4, h5, h6 {
    page-break-after: avoid;
  }
  
  .axiom-box,
  .decision-box,
  .failure-vignette,
  .concept-card {
    page-break-inside: avoid;
  }
  
  /* Print-friendly colors */
  * {
    color: #000 !important;
    background: #fff !important;
  }
  
  .axiom-box,
  .decision-box,
  .failure-vignette {
    border: 2px solid #000 !important;
    padding: 1rem !important;
  }
  
  /* Links */
  a {
    text-decoration: underline;
  }
  
  a[href^="http"]:after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
  }
  
  /* Code blocks */
  pre {
    white-space: pre-wrap;
    border: 1px solid #000;
  }
  
  /* Interactive elements as static */
  .interactive-tool {
    display: none;
  }
  
  /* Add page numbers */
  @page {
    margin: 2cm;
    @bottom-right {
      content: counter(page);
    }
  }
}
```

### 8.3 Service Worker for Offline Access

```javascript
// docs/service-worker.js
const CACHE_NAME = 'compendium-v1';
const urlsToCache = [
  '/',
  '/part1-axioms/',
  '/part2-pillars/',
  '/stylesheets/extra.css',
  '/javascripts/hero-animation.js',
  '/javascripts/journey-map.js',
  '/javascripts/latency-calculator.js',
  // Add all critical resources
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        
        // Clone the request
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then(response => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// Clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

---

## 9. Configuration Updates

### 9.1 MkDocs Configuration

```yaml
# mkdocs.yml - Add JavaScript and CSS files
extra_css:
  - stylesheets/extra.css
  - stylesheets/journey-map.css

extra_javascript:
  - javascripts/hero-animation.js
  - javascripts/journey-map.js
  - javascripts/theme-toggle.js
  - javascripts/breadcrumbs.js
  - javascripts/reading-progress.js
  - javascripts/toc-enhancement.js
  - javascripts/inline-calculators.js
  - javascripts/latency-calculator.js
  - javascripts/mobile-nav.js
  - javascripts/lazy-loading.js

# Enable additional features
theme:
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.top
    - navigation.indexes
    - search.highlight
    - search.share
    - content.code.annotate
    - content.tabs.link
```

### 9.2 GitHub Actions Workflow Update

```yaml
# .github/workflows/deploy.yml - Add optimization steps
- name: Optimize Assets
  run: |
    # Minify CSS
    npm install -g cssnano-cli
    find site -name "*.css" -exec cssnano {} {} \;
    
    # Minify JavaScript
    npm install -g terser
    find site -name "*.js" -exec terser {} -o {} -c -m \;
    
    # Optimize images
    npm install -g imagemin-cli
    imagemin site/images/* --out-dir=site/images
```

---

## 10. Implementation Checklist

### Phase 1: Visual Design (Week 1-2)
- [ ] Implement animated hero section
- [ ] Add dark mode with CSS variables
- [ ] Update all component styles for theming
- [ ] Add hover animations and transitions

### Phase 2: Interactive Journey (Week 3-4)
- [ ] Build clickable journey map
- [ ] Add node selection and details panel
- [ ] Implement connection highlighting
- [ ] Create entrance animations

### Phase 3: Content Enhancement (Week 5-6)
- [ ] Add key takeaway boxes to all axioms
- [ ] Create concept card templates
- [ ] Implement progressive disclosure
- [ ] Add visual content breaks

### Phase 4: Interactive Tools (Week 7-8)
- [ ] Build latency calculator
- [ ] Create inline mini-calculators
- [ ] Add capacity planner
- [ ] Implement availability calculator

### Phase 5: Navigation (Week 9-10)
- [ ] Add breadcrumb navigation
- [ ] Implement reading progress bar
- [ ] Enhance table of contents
- [ ] Add scroll spy functionality

### Phase 6: Mobile (Week 11)
- [ ] Create bottom tab navigation
- [ ] Implement swipe gestures
- [ ] Optimize touch targets
- [ ] Test on multiple devices

### Phase 7: Performance (Week 12)
- [ ] Implement lazy loading
- [ ] Add service worker
- [ ] Optimize print styles
- [ ] Performance testing

---

## 11. Success Metrics

### Quantitative Metrics
- Page load time < 2s on 3G
- Lighthouse score > 95 for all categories
- Time to Interactive < 3s
- First Contentful Paint < 1.5s

### Qualitative Metrics
- Improved visual hierarchy
- Enhanced content scanability
- Better mobile experience
- Increased engagement with interactive elements

### Content Metrics
- Average time on page > 5 minutes
- Scroll depth > 80%
- Tool interaction rate > 50%
- Journey map click rate > 30%

---

This comprehensive plan transforms the DStudio Compendium into a modern, interactive learning platform while maintaining its static site architecture. All enhancements are client-side only, requiring no backend services or user authentication, making it perfect for GitHub Pages hosting.