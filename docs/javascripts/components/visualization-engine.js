// Advanced Visualization Engine for Interactive Diagrams

(function() {
  'use strict';

class VisualizationEngine {
  constructor() {
    this.visualizations = new Map();
    
    // Get colors from CSS custom properties
    const rootStyles = getComputedStyle(document.documentElement);
    
    this.config = {
      colors: {
        primary: rootStyles.getPropertyValue('--primary-600').trim() || '#3F51B5',
        secondary: rootStyles.getPropertyValue('--info-500').trim() || '#2196F3',
        success: rootStyles.getPropertyValue('--success-500').trim() || '#4CAF50',
        warning: rootStyles.getPropertyValue('--warning-500').trim() || '#FF9800',
        danger: rootStyles.getPropertyValue('--error-500').trim() || '#F44336',
        neutral: rootStyles.getPropertyValue('--gray-500').trim() || '#9E9E9E'
      },
      animations: {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
      }
    };
  }

  init(app) {
    this.app = app;
    
    // Initialize Mermaid
    mermaid.initialize({
      startOnLoad: true,
      theme: 'base',
      themeVariables: {
        primaryColor: this.config.colors.primary,
        primaryBorderColor: this.config.colors.primary,
        primaryTextColor: '#fff',
        lineColor: this.config.colors.neutral,
        secondaryColor: this.config.colors.secondary,
        tertiaryColor: '#f5f5f5'
      }
    });
    
    // Auto-enhance all visualization containers
    this.enhanceVisualizations();
    
    // Set up mutation observer for dynamic content
    this.observeDynamicContent();
  }

  enhanceVisualizations() {
    // Network topology visualizations
    document.querySelectorAll('[data-viz="network-topology"]').forEach(container => {
      this.createNetworkTopology(container);
    });
    
    // Consistency timeline visualizations
    document.querySelectorAll('[data-viz="consistency-timeline"]').forEach(container => {
      this.createConsistencyTimeline(container);
    });
    
    // Load distribution charts
    document.querySelectorAll('[data-viz="load-distribution"]').forEach(container => {
      this.createLoadDistribution(container);
    });
    
    // Latency heatmaps
    document.querySelectorAll('[data-viz="latency-heatmap"]').forEach(container => {
      this.createLatencyHeatmap(container);
    });
    
    // Failure cascade animations
    document.querySelectorAll('[data-viz="failure-cascade"]').forEach(container => {
      this.createFailureCascade(container);
    });
  }

  createNetworkTopology(container) {
    const topology = container.dataset.topology || 'mesh';
    const nodes = parseInt(container.dataset.nodes) || 6;
    
    const width = container.clientWidth;
    const height = 400;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);
    
    // Create topology based on type
    const nodeData = this.generateTopologyNodes(topology, nodes, width, height);
    const linkData = this.generateTopologyLinks(topology, nodeData);
    
    // Create force simulation
    const simulation = d3.forceSimulation(nodeData)
      .force('link', d3.forceLink(linkData).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));
    
    // Add links
    const links = svg.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(linkData)
      .enter().append('line')
      .attr('stroke', this.config.colors.neutral)
      .attr('stroke-width', 2)
      .attr('opacity', 0.6);
    
    // Add nodes
    const nodes_g = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodeData)
      .enter().append('g')
      .call(this.drag(simulation));
    
    nodes_g.append('circle')
      .attr('r', 25)
      .attr('fill', d => d.type === 'master' ? this.config.colors.primary : this.config.colors.secondary)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);
    
    nodes_g.append('text')
      .text(d => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('fill', '#fff')
      .style('font-size', '12px')
      .style('font-weight', 'bold');
    
    // Add tooltips
    this.addTooltips(nodes_g, d => `
      <strong>Node ${d.id}</strong><br>
      Type: ${d.type}<br>
      Connections: ${d.connections || 0}
    `);
    
    // Update positions on tick
    simulation.on('tick', () => {
      links
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      
      nodes_g
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Add controls
    this.addTopologyControls(container, simulation, nodeData, linkData);
  }

  generateTopologyNodes(topology, count, width, height) {
    const nodes = [];
    
    switch (topology) {
      case 'star':
        // Central node
        nodes.push({ id: 'C', type: 'master', x: width / 2, y: height / 2 });
        // Peripheral nodes
        for (let i = 0; i < count - 1; i++) {
          const angle = (i * 2 * Math.PI) / (count - 1);
          nodes.push({
            id: `N${i + 1}`,
            type: 'slave',
            x: width / 2 + 150 * Math.cos(angle),
            y: height / 2 + 150 * Math.sin(angle)
          });
        }
        break;
        
      case 'ring':
        for (let i = 0; i < count; i++) {
          const angle = (i * 2 * Math.PI) / count;
          nodes.push({
            id: `N${i + 1}`,
            type: 'peer',
            x: width / 2 + 150 * Math.cos(angle),
            y: height / 2 + 150 * Math.sin(angle)
          });
        }
        break;
        
      case 'mesh':
      default:
        // Random positions
        for (let i = 0; i < count; i++) {
          nodes.push({
            id: `N${i + 1}`,
            type: 'peer',
            x: Math.random() * (width - 100) + 50,
            y: Math.random() * (height - 100) + 50
          });
        }
    }
    
    return nodes;
  }

  generateTopologyLinks(topology, nodes) {
    const links = [];
    
    switch (topology) {
      case 'star':
        // Connect all nodes to center
        const center = nodes.find(n => n.type === 'master');
        nodes.filter(n => n !== center).forEach(node => {
          links.push({ source: center.id, target: node.id });
        });
        break;
        
      case 'ring':
        // Connect in a circle
        for (let i = 0; i < nodes.length; i++) {
          links.push({
            source: nodes[i].id,
            target: nodes[(i + 1) % nodes.length].id
          });
        }
        break;
        
      case 'mesh':
      default:
        // Connect each node to 2-3 random others
        nodes.forEach((node, i) => {
          const connections = 2 + Math.floor(Math.random() * 2);
          const targets = new Set();
          
          while (targets.size < connections && targets.size < nodes.length - 1) {
            const targetIndex = Math.floor(Math.random() * nodes.length);
            if (targetIndex !== i) {
              targets.add(targetIndex);
            }
          }
          
          targets.forEach(targetIndex => {
            if (!links.some(l => 
              (l.source === node.id && l.target === nodes[targetIndex].id) ||
              (l.target === node.id && l.source === nodes[targetIndex].id)
            )) {
              links.push({ source: node.id, target: nodes[targetIndex].id });
            }
          });
        });
    }
    
    return links;
  }

  createConsistencyTimeline(container) {
    const events = JSON.parse(container.dataset.events || '[]');
    
    const margin = { top: 20, right: 20, bottom: 30, left: 50 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const xScale = d3.scaleLinear()
      .domain([0, d3.max(events, d => d.time)])
      .range([0, width]);
    
    const yScale = d3.scaleBand()
      .domain(events.map(d => d.node))
      .range([0, height])
      .padding(0.1);
    
    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d => d + 'ms'));
    
    svg.append('g')
      .call(d3.axisLeft(yScale));
    
    // Events
    const eventGroups = svg.selectAll('.event')
      .data(events)
      .enter().append('g')
      .attr('class', 'event')
      .attr('transform', d => `translate(${xScale(d.time)},${yScale(d.node)})`);
    
    eventGroups.append('circle')
      .attr('r', 6)
      .attr('fill', d => this.getEventColor(d.type))
      .attr('opacity', 0)
      .transition()
      .duration(500)
      .delay((d, i) => i * 100)
      .attr('opacity', 1);
    
    eventGroups.append('text')
      .text(d => d.value)
      .attr('x', 10)
      .attr('dy', '.35em')
      .style('font-size', '12px');
    
    // Causality arrows
    const arrows = events.filter(e => e.causes);
    svg.selectAll('.arrow')
      .data(arrows)
      .enter().append('line')
      .attr('class', 'arrow')
      .attr('x1', d => xScale(d.causes.time))
      .attr('y1', d => yScale(d.causes.node) + yScale.bandwidth() / 2)
      .attr('x2', d => xScale(d.time))
      .attr('y2', d => yScale(d.node) + yScale.bandwidth() / 2)
      .attr('stroke', this.config.colors.neutral)
      .attr('stroke-width', 1)
      .attr('marker-end', 'url(#arrowhead)')
      .attr('opacity', 0.5);
  }

  createLoadDistribution(container) {
    const data = JSON.parse(container.dataset.distribution || '[]');
    
    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const xScale = d3.scaleBand()
      .domain(data.map(d => d.server))
      .range([0, width])
      .padding(0.1);
    
    const yScale = d3.scaleLinear()
      .domain([0, 100])
      .range([height, 0]);
    
    // Color scale for load levels
    const colorScale = d3.scaleSequential()
      .domain([0, 100])
      .interpolator(d3.interpolateRdYlGn)
      .clamp(true);
    
    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale));
    
    svg.append('g')
      .call(d3.axisLeft(yScale).tickFormat(d => d + '%'));
    
    // Bars
    const bars = svg.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.server))
      .attr('width', xScale.bandwidth())
      .attr('y', height)
      .attr('height', 0)
      .attr('fill', d => colorScale(100 - d.load));
    
    // Animate bars
    bars.transition()
      .duration(1000)
      .delay((d, i) => i * 100)
      .attr('y', d => yScale(d.load))
      .attr('height', d => height - yScale(d.load));
    
    // Load labels
    svg.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => xScale(d.server) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.load) - 5)
      .attr('text-anchor', 'middle')
      .text(d => d.load + '%')
      .style('font-size', '12px')
      .attr('opacity', 0)
      .transition()
      .delay(1500)
      .attr('opacity', 1);
    
    // Add threshold line
    const threshold = 80;
    svg.append('line')
      .attr('class', 'threshold')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', yScale(threshold))
      .attr('y2', yScale(threshold))
      .attr('stroke', this.config.colors.danger)
      .attr('stroke-dasharray', '5,5')
      .attr('opacity', 0.7);
    
    // Update animation
    if (container.dataset.animate === 'true') {
      setInterval(() => {
        const newData = data.map(d => ({
          ...d,
          load: Math.max(0, Math.min(100, d.load + (Math.random() - 0.5) * 20))
        }));
        
        bars.data(newData)
          .transition()
          .duration(500)
          .attr('y', d => yScale(d.load))
          .attr('height', d => height - yScale(d.load))
          .attr('fill', d => colorScale(100 - d.load));
        
        svg.selectAll('.label')
          .data(newData)
          .text(d => Math.round(d.load) + '%')
          .attr('y', d => yScale(d.load) - 5);
      }, 2000);
    }
  }

  createLatencyHeatmap(container) {
    const regions = JSON.parse(container.dataset.regions || '[]');
    const latencies = JSON.parse(container.dataset.latencies || '[]');
    
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = width; // Square heatmap
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const xScale = d3.scaleBand()
      .domain(regions)
      .range([0, width])
      .padding(0.05);
    
    const yScale = d3.scaleBand()
      .domain(regions)
      .range([0, height])
      .padding(0.05);
    
    // Color scale
    const colorScale = d3.scaleSequential()
      .domain([0, d3.max(latencies, d => d.value)])
      .interpolator(d3.interpolateViridis);
    
    // Cells
    svg.selectAll('.cell')
      .data(latencies)
      .enter().append('rect')
      .attr('class', 'cell')
      .attr('x', d => xScale(d.from))
      .attr('y', d => yScale(d.to))
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.value))
      .attr('opacity', 0)
      .transition()
      .duration(1000)
      .delay((d, i) => i * 10)
      .attr('opacity', 0.9);
    
    // Text labels
    svg.selectAll('.text')
      .data(latencies)
      .enter().append('text')
      .attr('x', d => xScale(d.from) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.to) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .text(d => d.value + 'ms')
      .style('font-size', '10px')
      .style('fill', d => d.value > 100 ? 'white' : 'black')
      .attr('opacity', 0)
      .transition()
      .delay(1500)
      .attr('opacity', 1);
    
    // X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .style('text-anchor', 'middle');
    
    // Y axis
    svg.append('g')
      .call(d3.axisLeft(yScale));
    
    // Legend
    this.addColorLegend(svg, colorScale, width, 'Latency (ms)');
  }

  createFailureCascade(container) {
    const nodes = JSON.parse(container.dataset.nodes || '[]');
    const dependencies = JSON.parse(container.dataset.dependencies || '[]');
    
    const width = container.clientWidth;
    const height = 400;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
    
    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(dependencies).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));
    
    // Add links
    const links = svg.append('g')
      .selectAll('line')
      .data(dependencies)
      .enter().append('line')
      .attr('stroke', this.config.colors.neutral)
      .attr('stroke-width', 2)
      .attr('opacity', 0.6);
    
    // Add nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(this.drag(simulation));
    
    node.append('circle')
      .attr('r', 30)
      .attr('fill', d => d.status === 'healthy' ? this.config.colors.success : this.config.colors.danger)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);
    
    node.append('text')
      .text(d => d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .style('fill', '#fff')
      .style('font-size', '12px')
      .style('font-weight', 'bold');
    
    // Update positions
    simulation.on('tick', () => {
      links
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Add failure cascade animation
    if (container.dataset.animate === 'true') {
      this.animateFailureCascade(nodes, node, dependencies);
    }
  }

  animateFailureCascade(nodes, nodeElements, dependencies) {
    const failNode = (nodeId) => {
      const node = nodes.find(n => n.id === nodeId);
      if (node && node.status === 'healthy') {
        node.status = 'failed';
        
        // Update visual
        nodeElements.filter(d => d.id === nodeId)
          .select('circle')
          .transition()
          .duration(300)
          .attr('fill', this.config.colors.danger);
        
        // Find dependent nodes
        const dependents = dependencies
          .filter(d => d.target.id === nodeId)
          .map(d => d.source.id);
        
        // Cascade failure with delay
        dependents.forEach((depId, i) => {
          setTimeout(() => failNode(depId), 500 * (i + 1));
        });
      }
    };
    
    // Simulate random failure
    const startFailure = () => {
      // Reset all nodes
      nodes.forEach(n => n.status = 'healthy');
      nodeElements.selectAll('circle')
        .attr('fill', this.config.colors.success);
      
      // Pick random node to fail
      const randomNode = nodes[Math.floor(Math.random() * nodes.length)];
      setTimeout(() => failNode(randomNode.id), 1000);
    };
    
    // Start animation
    startFailure();
    setInterval(startFailure, 10000);
  }

  // Utility functions
  drag(simulation) {
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  addTooltips(selection, contentFn) {
    const tooltip = d3.select('body').append('div')
      .attr('class', 'viz-tooltip')
      .style('opacity', 0);
    
    selection
      .on('mouseover', (event, d) => {
        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        tooltip.html(contentFn(d))
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', () => {
        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      });
  }

  addColorLegend(svg, colorScale, width, label) {
    const legendWidth = 200;
    const legendHeight = 10;
    
    const legend = svg.append('g')
      .attr('transform', `translate(${width - legendWidth}, -30)`);
    
    // Create gradient
    const gradientId = 'gradient-' + Math.random().toString(36).substr(2, 9);
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', gradientId);
    
    const steps = 10;
    for (let i = 0; i <= steps; i++) {
      gradient.append('stop')
        .attr('offset', i / steps)
        .attr('stop-color', colorScale(colorScale.domain()[0] + 
          (colorScale.domain()[1] - colorScale.domain()[0]) * i / steps));
    }
    
    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', `url(#${gradientId})`);
    
    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -5)
      .attr('text-anchor', 'middle')
      .text(label)
      .style('font-size', '12px');
  }

  addTopologyControls(container, simulation, nodes, links) {
    const controls = document.createElement('div');
    controls.className = 'viz-controls';
    controls.innerHTML = `
      <button class="viz-btn" data-action="pause">⏸️ Pause</button>
      <button class="viz-btn" data-action="restart">🔄 Restart</button>
      <button class="viz-btn" data-action="add-node">➕ Add Node</button>
      <button class="viz-btn" data-action="remove-node">➖ Remove Node</button>
    `;
    
    container.appendChild(controls);
    
    controls.addEventListener('click', (e) => {
      const action = e.target.dataset.action;
      
      switch (action) {
        case 'pause':
          simulation.stop();
          e.target.textContent = '▶️ Resume';
          e.target.dataset.action = 'resume';
          break;
          
        case 'resume':
          simulation.restart();
          e.target.textContent = '⏸️ Pause';
          e.target.dataset.action = 'pause';
          break;
          
        case 'restart':
          simulation.alpha(1).restart();
          break;
          
        case 'add-node':
          // Add new node logic
          break;
          
        case 'remove-node':
          // Remove node logic
          break;
      }
    });
  }

  getEventColor(type) {
    const colors = {
      write: this.config.colors.primary,
      read: this.config.colors.secondary,
      sync: this.config.colors.warning,
      commit: this.config.colors.success,
      abort: this.config.colors.danger
    };
    return colors[type] || this.config.colors.neutral;
  }

  observeDynamicContent() {
    const observer = new MutationObserver(() => {
      this.enhanceVisualizations();
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
}

// Register with app
if (window.DSApp) {
  window.DSApp.register('visualizations', new VisualizationEngine());
}

// Add visualization styles
const vizStyles = `
<style>
.viz-tooltip {
  position: absolute;
  text-align: left;
  padding: 8px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  pointer-events: none;
  z-index: 1000;
}

.viz-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
}

.viz-btn {
  padding: 5px 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.viz-btn:hover {
  background: #f0f0f0;
  transform: translateY(-1px);
}

[data-viz] {
  position: relative;
  min-height: 400px;
  margin: 20px 0;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', vizStyles);

})();