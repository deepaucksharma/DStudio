// Enhanced Capacity Planner
class CapacityPlanner {
  constructor() {
    this.chartCanvas = null;
    this.chartCtx = null;
    this.animationId = null;
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupPlanner());
    } else {
      this.setupPlanner();
    }
  }
  
  setupPlanner() {
    const form = document.getElementById('capacity-calc');
    if (!form) return;
    
    // Set up event listeners
    form.addEventListener('input', () => this.calculateCapacity());
    
    // Add real-time input validation
    this.addInputValidation();
    
    // Initialize visualization
    this.initVisualization();
    
    // Initial calculation
    this.calculateCapacity();
  }
  
  initVisualization() {
    // Get or create canvas container
    let canvasContainer = document.getElementById('capacity-visualization');
    if (!canvasContainer) {
      canvasContainer = document.createElement('div');
      canvasContainer.id = 'capacity-visualization';
      canvasContainer.className = 'visualization-container';
      
      const form = document.getElementById('capacity-calc');
      form.parentNode.insertBefore(canvasContainer, form.nextSibling);
    }
    
    // Create canvas
    this.chartCanvas = document.createElement('canvas');
    this.chartCanvas.width = canvasContainer.offsetWidth || 600;
    this.chartCanvas.height = 400;
    this.chartCtx = this.chartCanvas.getContext('2d');
    canvasContainer.innerHTML = '';
    canvasContainer.appendChild(this.chartCanvas);
    
    // Handle resize
    window.addEventListener('resize', () => {
      this.chartCanvas.width = canvasContainer.offsetWidth;
      this.calculateCapacity();
    });
  }
  
  addInputValidation() {
    const inputs = {
      'arrival-rate': { min: 1, max: 1000000, step: 10 },
      'service-time': { min: 1, max: 10000, step: 5 },
      'servers': { min: 1, max: 10000, step: 1 },
      'target-util': { min: 10, max: 95, step: 5 }
    };
    
    Object.entries(inputs).forEach(([id, constraints]) => {
      const input = document.getElementById(id);
      if (input) {
        input.addEventListener('change', (e) => {
          const value = parseFloat(e.target.value);
          if (value < constraints.min) e.target.value = constraints.min;
          if (value > constraints.max) e.target.value = constraints.max;
        });
      }
    });
  }
  
  calculateCapacity() {
    // Get input values
    const arrivalRate = parseFloat(document.getElementById('arrival-rate').value) || 0;
    const serviceTimeMs = parseFloat(document.getElementById('service-time').value) || 50;
    const servers = parseInt(document.getElementById('servers').value) || 1;
    const targetUtil = parseFloat(document.getElementById('target-util').value) / 100 || 0.7;
    
    // Convert service time to rate
    const serviceRate = 1000 / serviceTimeMs; // requests/second per server
    const totalServiceRate = serviceRate * servers;
    
    // Calculate utilization
    const utilization = arrivalRate / totalServiceRate;
    
    // Calculate queue metrics using M/M/c formulas
    let responseTime, queueLength, queueWait, avgSystemLength;
    
    if (utilization >= 1) {
      // System is unstable
      responseTime = Infinity;
      queueLength = Infinity;
      queueWait = Infinity;
      avgSystemLength = Infinity;
    } else {
      // For simplicity, using M/M/1 approximation scaled by servers
      // In production, use proper M/M/c formulas
      const rho = utilization;
      
      // Average number in system (Little's Law)
      avgSystemLength = rho / (1 - rho);
      
      // Response time
      responseTime = serviceTimeMs / (1 - rho);
      
      // Queue metrics
      queueWait = responseTime - serviceTimeMs;
      queueLength = arrivalRate * (queueWait / 1000);
    }
    
    // Capacity recommendations
    const requiredServers = Math.ceil(arrivalRate / (serviceRate * targetUtil));
    const headroom = ((totalServiceRate - arrivalRate) / totalServiceRate * 100);
    const maxSustainableLoad = totalServiceRate * 0.9; // 90% max recommended
    
    // Update visualizations
    this.drawCapacityChart({
      utilization,
      servers,
      arrivalRate,
      totalServiceRate,
      serviceTimeMs
    });
    
    // Display results
    this.displayResults({
      utilization,
      responseTime,
      queueLength,
      queueWait,
      avgSystemLength,
      headroom,
      requiredServers,
      servers,
      totalServiceRate,
      maxSustainableLoad,
      targetUtil,
      serviceRate
    });
  }
  
  drawCapacityChart(data) {
    const ctx = this.chartCtx;
    const width = this.chartCanvas.width;
    const height = this.chartCanvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Set up chart dimensions
    const padding = 60;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // Draw background grid
    this.drawGrid(ctx, padding, chartWidth, chartHeight);
    
    // Draw axes
    ctx.strokeStyle = '#4B5563';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw response time curve
    this.drawResponseCurve(ctx, padding, chartWidth, chartHeight, data.serviceTimeMs);
    
    // Draw utilization zones
    this.drawUtilizationZones(ctx, padding, chartWidth, chartHeight);
    
    // Mark current point
    if (data.utilization < 1) {
      const x = padding + (data.utilization * chartWidth);
      const responseTime = data.serviceTimeMs / (1 - data.utilization);
      const maxY = data.serviceTimeMs * 20; // Cap at 20x service time for display
      const y = height - padding - (Math.min(responseTime, maxY) / maxY * chartHeight);
      
      // Draw current point
      ctx.fillStyle = data.utilization > 0.8 ? '#EF4444' : 
                      data.utilization > 0.7 ? '#F59E0B' : '#10B981';
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      // Add label
      ctx.fillStyle = '#111827';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(`${(data.utilization * 100).toFixed(0)}%`, x, y - 15);
    }
    
    // Draw capacity line
    const capacityX = padding + (1.0 * chartWidth);
    ctx.strokeStyle = '#EF4444';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(capacityX, padding);
    ctx.lineTo(capacityX, height - padding);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Labels
    ctx.fillStyle = '#4B5563';
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Utilization (%)', width / 2, height - 10);
    
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Response Time (ms)', 0, 0);
    ctx.restore();
    
    // Title
    ctx.font = '16px Inter';
    ctx.fillStyle = '#111827';
    ctx.textAlign = 'left';
    ctx.fillText('Response Time vs Utilization', padding, 30);
    
    // Legend
    this.drawLegend(ctx, width - 200, 40);
  }
  
  drawGrid(ctx, padding, width, height) {
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;
    
    // Vertical lines (10% intervals)
    for (let i = 0; i <= 10; i++) {
      const x = padding + (i / 10) * width;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, padding + height);
      ctx.stroke();
    }
    
    // Horizontal lines
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i / 5) * height;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + width, y);
      ctx.stroke();
    }
  }
  
  drawResponseCurve(ctx, padding, width, height, serviceTime) {
    ctx.strokeStyle = '#5B5FC7';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const maxY = serviceTime * 20; // Cap display at 20x service time
    
    for (let u = 0; u <= 0.99; u += 0.001) {
      const responseTime = serviceTime / (1 - u);
      const x = padding + (u * width);
      const y = padding + height - (Math.min(responseTime, maxY) / maxY * height);
      
      if (u === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  }
  
  drawUtilizationZones(ctx, padding, width, height) {
    const zones = [
      { start: 0, end: 0.7, color: 'rgba(16, 185, 129, 0.1)', label: 'Optimal' },
      { start: 0.7, end: 0.8, color: 'rgba(245, 158, 11, 0.1)', label: 'Caution' },
      { start: 0.8, end: 1.0, color: 'rgba(239, 68, 68, 0.1)', label: 'Danger' }
    ];
    
    zones.forEach(zone => {
      const startX = padding + (zone.start * width);
      const endX = padding + (zone.end * width);
      
      ctx.fillStyle = zone.color;
      ctx.fillRect(startX, padding, endX - startX, height);
    });
  }
  
  drawLegend(ctx, x, y) {
    const items = [
      { color: '#5B5FC7', label: 'Response Time' },
      { color: '#10B981', label: 'Optimal Zone' },
      { color: '#F59E0B', label: 'Caution Zone' },
      { color: '#EF4444', label: 'Danger Zone' }
    ];
    
    ctx.font = '12px Inter';
    items.forEach((item, i) => {
      const itemY = y + i * 20;
      
      // Color box
      ctx.fillStyle = item.color;
      ctx.fillRect(x, itemY, 15, 15);
      
      // Label
      ctx.fillStyle = '#4B5563';
      ctx.textAlign = 'left';
      ctx.fillText(item.label, x + 20, itemY + 12);
    });
  }
  
  displayResults(data) {
    const resultsDiv = document.getElementById('capacity-results');
    if (!resultsDiv) return;
    
    // Determine system health
    let healthStatus, healthClass, healthIcon;
    if (data.utilization >= 1) {
      healthStatus = 'OVERLOADED - System Unstable!';
      healthClass = 'health-critical';
      healthIcon = '🔥';
    } else if (data.utilization > 0.9) {
      healthStatus = 'Critical - Near Saturation';
      healthClass = 'health-critical';
      healthIcon = '🚨';
    } else if (data.utilization > 0.8) {
      healthStatus = 'Warning - High Utilization';
      healthClass = 'health-warning';
      healthIcon = '⚠️';
    } else if (data.utilization > 0.7) {
      healthStatus = 'Caution - Approaching Limits';
      healthClass = 'health-caution';
      healthIcon = '📊';
    } else {
      healthStatus = 'Healthy - Good Capacity';
      healthClass = 'health-good';
      healthIcon = '✅';
    }
    
    resultsDiv.innerHTML = `
      <div class="capacity-health ${healthClass}">
        <span class="health-icon">${healthIcon}</span>
        <div class="health-info">
          <h4>${healthStatus}</h4>
          <p>Current utilization: ${(data.utilization * 100).toFixed(1)}%</p>
        </div>
      </div>
      
      <div class="results-grid">
        <div class="result-card">
          <h4>📊 Current Capacity</h4>
          <div class="metric-grid">
            <div class="metric-item">
              <span class="metric-label">Utilization</span>
              <span class="metric-value">${(data.utilization * 100).toFixed(1)}%</span>
              <div class="utilization-bar">
                <div class="utilization-fill" style="width: ${Math.min(data.utilization * 100, 100)}%; background: ${
                  data.utilization > 0.8 ? '#EF4444' : 
                  data.utilization > 0.7 ? '#F59E0B' : '#10B981'
                }"></div>
              </div>
            </div>
            <div class="metric-item">
              <span class="metric-label">Max Capacity</span>
              <span class="metric-value">${data.totalServiceRate.toFixed(0)} req/s</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Current Load</span>
              <span class="metric-value">${document.getElementById('arrival-rate').value} req/s</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Headroom</span>
              <span class="metric-value">${data.headroom > 0 ? data.headroom.toFixed(1) : 0}%</span>
            </div>
          </div>
        </div>
        
        <div class="result-card">
          <h4>⏱️ Performance Metrics</h4>
          <div class="metric-grid">
            <div class="metric-item">
              <span class="metric-label">Avg Response Time</span>
              <span class="metric-value">${
                isFinite(data.responseTime) ? data.responseTime.toFixed(1) + ' ms' : 'UNSTABLE'
              }</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Queue Wait Time</span>
              <span class="metric-value">${
                isFinite(data.queueWait) ? data.queueWait.toFixed(1) + ' ms' : 'INFINITE'
              }</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Queue Length</span>
              <span class="metric-value">${
                isFinite(data.queueLength) ? data.queueLength.toFixed(0) + ' requests' : 'UNBOUNDED'
              }</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">System Length</span>
              <span class="metric-value">${
                isFinite(data.avgSystemLength) ? data.avgSystemLength.toFixed(1) + ' requests' : 'UNBOUNDED'
              }</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="recommendations-section">
        <h4>💡 Recommendations</h4>
        <div class="recommendation-grid">
          <div class="recommendation-card">
            <h5>Optimal Configuration</h5>
            <p>For ${(data.targetUtil * 100).toFixed(0)}% target utilization:</p>
            <ul>
              <li>Required servers: <strong>${data.requiredServers}</strong></li>
              <li>Current servers: <strong>${data.servers}</strong></li>
              <li>${data.requiredServers > data.servers ? 
                `Add ${data.requiredServers - data.servers} servers` : 
                data.requiredServers < data.servers ?
                `Can remove ${data.servers - data.requiredServers} servers` :
                'Current configuration is optimal'}</li>
            </ul>
          </div>
          
          <div class="recommendation-card">
            <h5>Scaling Triggers</h5>
            <ul>
              <li>Scale up at: ${(data.targetUtil * 100 * 1.1).toFixed(0)}% utilization</li>
              <li>Scale down at: ${(data.targetUtil * 100 * 0.7).toFixed(0)}% utilization</li>
              <li>Max sustainable: ${data.maxSustainableLoad.toFixed(0)} req/s</li>
              <li>Per-server capacity: ${data.serviceRate.toFixed(1)} req/s</li>
            </ul>
          </div>
        </div>
        
        ${this.getInsights(data)}
      </div>
    `;
  }
  
  getInsights(data) {
    const insights = [];
    
    if (data.utilization >= 1) {
      insights.push({
        type: 'critical',
        icon: '🔥',
        text: 'System is overloaded! Add servers immediately or reduce load.'
      });
    } else if (data.utilization > 0.9) {
      insights.push({
        type: 'warning',
        icon: '🚨',
        text: 'Dangerously high utilization. Response times are degrading exponentially.'
      });
    } else if (data.utilization > 0.8) {
      insights.push({
        type: 'warning',
        icon: '⚠️',
        text: 'Consider adding capacity soon. Limited buffer for traffic spikes.'
      });
    }
    
    if (data.headroom < 20 && data.utilization < 1) {
      insights.push({
        type: 'info',
        icon: '📈',
        text: `Only ${data.headroom.toFixed(0)}% headroom remaining for growth.`
      });
    }
    
    if (data.responseTime > 200 && isFinite(data.responseTime)) {
      insights.push({
        type: 'info',
        icon: '⏰',
        text: 'Response times exceed 200ms. Consider optimizing service time or adding servers.'
      });
    }
    
    if (data.servers > data.requiredServers * 1.5) {
      insights.push({
        type: 'success',
        icon: '💰',
        text: 'Significant over-provisioning detected. Consider cost optimization.'
      });
    }
    
    if (insights.length === 0) {
      insights.push({
        type: 'success',
        icon: '✅',
        text: 'System is well-configured with appropriate capacity and headroom.'
      });
    }
    
    return `
      <div class="insights-container">
        ${insights.map(insight => `
          <div class="insight-card ${insight.type}">
            <span class="insight-icon">${insight.icon}</span>
            <p>${insight.text}</p>
          </div>
        `).join('')}
      </div>
    `;
  }
}

// Initialize planner
const capacityPlanner = new CapacityPlanner();