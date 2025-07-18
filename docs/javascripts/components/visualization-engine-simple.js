// Simplified Visualization Engine without external dependencies

(function() {
  'use strict';

  class SimpleVisualizationEngine {
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
        }
      };
    }

    init(app) {
      this.app = app;
      
      // Auto-enhance all visualization containers
      this.enhanceVisualizations();
      
      // Set up mutation observer for dynamic content
      this.observeDynamicContent();
    }

    enhanceVisualizations() {
      // Simple network diagram
      document.querySelectorAll('[data-viz="network-simple"]').forEach(container => {
        this.createSimpleNetwork(container);
      });
      
      // Simple bar chart
      document.querySelectorAll('[data-viz="bar-chart"]').forEach(container => {
        this.createBarChart(container);
      });
      
      // Simple timeline
      document.querySelectorAll('[data-viz="timeline"]').forEach(container => {
        this.createTimeline(container);
      });
    }

    createSimpleNetwork(container) {
      const nodes = parseInt(container.dataset.nodes) || 5;
      const type = container.dataset.type || 'star';
      
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '400');
      svg.setAttribute('viewBox', '0 0 800 400');
      
      const centerX = 400;
      const centerY = 200;
      const radius = 150;
      
      // Create nodes
      const nodeElements = [];
      
      if (type === 'star') {
        // Central node
        const central = this.createNode(centerX, centerY, 'Central', this.config.colors.primary);
        svg.appendChild(central);
        
        // Peripheral nodes
        for (let i = 0; i < nodes - 1; i++) {
          const angle = (i * 2 * Math.PI) / (nodes - 1);
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);
          
          // Draw line first (so it appears behind nodes)
          const line = this.createLine(centerX, centerY, x, y);
          svg.appendChild(line);
          
          const node = this.createNode(x, y, `N${i + 1}`, this.config.colors.secondary);
          svg.appendChild(node);
          nodeElements.push(node);
        }
      } else if (type === 'ring') {
        for (let i = 0; i < nodes; i++) {
          const angle = (i * 2 * Math.PI) / nodes;
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);
          
          // Draw line to next node
          const nextAngle = ((i + 1) % nodes * 2 * Math.PI) / nodes;
          const nextX = centerX + radius * Math.cos(nextAngle);
          const nextY = centerY + radius * Math.sin(nextAngle);
          
          const line = this.createLine(x, y, nextX, nextY);
          svg.appendChild(line);
          
          const node = this.createNode(x, y, `N${i + 1}`, this.config.colors.secondary);
          svg.appendChild(node);
          nodeElements.push(node);
        }
      }
      
      container.appendChild(svg);
      
      // Add info
      const info = document.createElement('div');
      info.className = 'viz-info';
      info.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)} topology with ${nodes} nodes`;
      container.appendChild(info);
    }

    createNode(x, y, label, color) {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${x}, ${y})`);
      
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', '30');
      circle.setAttribute('fill', color);
      circle.setAttribute('stroke', '#fff');
      circle.setAttribute('stroke-width', '2');
      circle.style.cursor = 'pointer';
      
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dy', '.35em');
      text.setAttribute('fill', '#fff');
      text.style.fontSize = '14px';
      text.style.fontWeight = 'bold';
      text.textContent = label;
      
      g.appendChild(circle);
      g.appendChild(text);
      
      // Add hover effect
      g.addEventListener('mouseenter', () => {
        circle.setAttribute('r', '35');
      });
      
      g.addEventListener('mouseleave', () => {
        circle.setAttribute('r', '30');
      });
      
      return g;
    }

    createLine(x1, y1, x2, y2) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', x1);
      line.setAttribute('y1', y1);
      line.setAttribute('x2', x2);
      line.setAttribute('y2', y2);
      line.setAttribute('stroke', this.config.colors.neutral);
      line.setAttribute('stroke-width', '2');
      line.setAttribute('opacity', '0.6');
      
      return line;
    }

    createBarChart(container) {
      const data = JSON.parse(container.dataset.values || '[]');
      if (!data.length) return;
      
      const width = 600;
      const height = 300;
      const barWidth = width / data.length * 0.8;
      const maxValue = Math.max(...data.map(d => d.value));
      
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', height);
      svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
      
      data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * (height - 40);
        const x = index * (width / data.length) + (width / data.length - barWidth) / 2;
        const y = height - barHeight - 20;
        
        // Bar
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', barWidth);
        rect.setAttribute('height', barHeight);
        rect.setAttribute('fill', this.getColorForValue(item.value, maxValue));
        rect.style.transition = 'all 0.3s ease';
        
        // Label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x + barWidth / 2);
        text.setAttribute('y', height - 5);
        text.setAttribute('text-anchor', 'middle');
        text.style.fontSize = '12px';
        text.textContent = item.label;
        
        // Value
        const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        valueText.setAttribute('x', x + barWidth / 2);
        valueText.setAttribute('y', y - 5);
        valueText.setAttribute('text-anchor', 'middle');
        valueText.style.fontSize = '12px';
        valueText.style.fontWeight = 'bold';
        valueText.textContent = item.value;
        
        svg.appendChild(rect);
        svg.appendChild(text);
        svg.appendChild(valueText);
        
        // Hover effect
        rect.addEventListener('mouseenter', () => {
          rect.setAttribute('opacity', '0.8');
        });
        
        rect.addEventListener('mouseleave', () => {
          rect.setAttribute('opacity', '1');
        });
      });
      
      container.appendChild(svg);
    }

    createTimeline(container) {
      const events = JSON.parse(container.dataset.events || '[]');
      if (!events.length) return;
      
      const timeline = document.createElement('div');
      timeline.className = 'simple-timeline';
      
      events.forEach((event, index) => {
        const eventEl = document.createElement('div');
        eventEl.className = 'timeline-event';
        
        const dot = document.createElement('div');
        dot.className = 'timeline-dot';
        dot.style.backgroundColor = this.getEventColor(event.type);
        
        const content = document.createElement('div');
        content.className = 'timeline-content';
        content.innerHTML = `
          <strong>${event.time}ms</strong> - ${event.node}<br>
          <span class="event-detail">${event.type}: ${event.value}</span>
        `;
        
        eventEl.appendChild(dot);
        eventEl.appendChild(content);
        timeline.appendChild(eventEl);
        
        // Animate in
        setTimeout(() => {
          eventEl.classList.add('show');
        }, index * 100);
      });
      
      container.appendChild(timeline);
    }

    getColorForValue(value, max) {
      const ratio = value / max;
      if (ratio > 0.8) return this.config.colors.danger;
      if (ratio > 0.6) return this.config.colors.warning;
      return this.config.colors.success;
    }

    getEventColor(type) {
      const colors = {
        write: this.config.colors.primary,
        read: this.config.colors.secondary,
        sync: this.config.colors.warning,
        commit: this.config.colors.success,
        error: this.config.colors.danger
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
    window.DSApp.register('simple-visualizations', new SimpleVisualizationEngine());
  } else {
    // Standalone initialization
    document.addEventListener('DOMContentLoaded', () => {
      const engine = new SimpleVisualizationEngine();
      engine.enhanceVisualizations();
    });
  }

  // Add styles
  const styles = `
    <style>
    .viz-info {
      text-align: center;
      margin-top: 10px;
      font-size: 14px;
      color: #666;
    }
    
    .simple-timeline {
      position: relative;
      padding: 20px 0;
    }
    
    .simple-timeline::before {
      content: '';
      position: absolute;
      left: 20px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #e0e0e0;
    }
    
    .timeline-event {
      position: relative;
      padding-left: 50px;
      margin-bottom: 20px;
      opacity: 0;
      transform: translateX(-20px);
      transition: all 0.3s ease;
    }
    
    .timeline-event.show {
      opacity: 1;
      transform: translateX(0);
    }
    
    .timeline-dot {
      position: absolute;
      left: 12px;
      top: 5px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      border: 2px solid #fff;
      box-shadow: 0 0 0 2px #e0e0e0;
    }
    
    .timeline-content {
      background: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
      font-size: 14px;
    }
    
    .event-detail {
      font-size: 12px;
      color: #666;
    }
    
    [data-viz] {
      margin: 20px 0;
      padding: 20px;
      background: #fafafa;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
    }
    </style>
  `;
  
  document.head.insertAdjacentHTML('beforeend', styles);

})();