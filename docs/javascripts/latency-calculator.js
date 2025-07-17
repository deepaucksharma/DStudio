// Enhanced Latency Calculator
class LatencyCalculator {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.animationId = null;
    this.particles = [];
    this.init();
  }
  
  init() {
    // Set up event listeners when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupCalculator());
    } else {
      this.setupCalculator();
    }
  }
  
  setupCalculator() {
    // Initialize the visual representation
    this.initVisualization();
    
    // Set up form listeners
    const form = document.getElementById('latency-calc');
    if (form) {
      // Update visualization on any input change
      form.addEventListener('input', () => this.calculateLatency());
      
      // Add route preset buttons
      const routeButtons = document.querySelectorAll('.route-btn');
      routeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
          const distance = e.target.dataset.distance;
          const name = e.target.dataset.route;
          this.setRoute(parseInt(distance), name);
        });
      });
      
      // Add tooltips to form inputs
      this.addTooltips();
      
      // Initial calculation
      this.calculateLatency();
    }
  }
  
  initVisualization() {
    const container = document.getElementById('latency-visualization');
    if (!container) return;
    
    // Create canvas for visualization
    this.canvas = document.createElement('canvas');
    this.canvas.width = container.offsetWidth;
    this.canvas.height = 200;
    this.ctx = this.canvas.getContext('2d');
    container.appendChild(this.canvas);
    
    // Handle resize
    window.addEventListener('resize', () => {
      this.canvas.width = container.offsetWidth;
      this.calculateLatency();
    });
  }
  
  setRoute(distance, routeName) {
    document.getElementById('distance').value = distance;
    document.getElementById('selected-route').textContent = routeName;
    this.calculateLatency();
  }
  
  calculateLatency() {
    const distance = parseFloat(document.getElementById('distance').value) || 0;
    const medium = document.getElementById('medium').value;
    const hops = parseInt(document.getElementById('hops').value) || 0;
    
    // Speed of light and medium factors
    const SPEED_OF_LIGHT = 299792; // km/s
    const mediumFactors = {
      'fiber': 0.67,
      'copper': 0.66,
      'wireless': 1.0
    };
    
    // Device processing times (ms)
    const deviceOverhead = {
      'routers': 0.1,
      'switches': 0.01,
      'firewalls': 0.5,
      'lbs': 0.2
    };
    
    // Calculate propagation delay
    const effectiveSpeed = SPEED_OF_LIGHT * mediumFactors[medium];
    const propagationDelay = (distance / effectiveSpeed) * 1000; // ms
    
    // Calculate processing delay
    let processingDelay = 0;
    for (const [device, overhead] of Object.entries(deviceOverhead)) {
      const input = document.querySelector(`input[name="${device}"]`);
      if (input) {
        const count = parseInt(input.value) || 0;
        processingDelay += count * overhead;
      }
    }
    
    // Serialization delay
    const serializationDelay = hops * 0.1;
    
    // Queueing delay (variable, we'll use a realistic estimate)
    const queueingDelay = hops * 0.5;
    
    // Total latency
    const totalLatency = propagationDelay + processingDelay + serializationDelay + queueingDelay;
    
    // Update visualization
    this.updateVisualization({
      distance,
      propagationDelay,
      processingDelay,
      serializationDelay,
      queueingDelay,
      totalLatency
    });
    
    // Display results
    this.displayResults({
      distance,
      propagationDelay,
      processingDelay,
      serializationDelay,
      queueingDelay,
      totalLatency,
      effectiveSpeed,
      SPEED_OF_LIGHT
    });
  }
  
  updateVisualization(data) {
    if (!this.canvas || !this.ctx) return;
    
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw latency breakdown bar
    const barHeight = 40;
    const barY = height / 2 - barHeight / 2;
    const totalWidth = width - 100;
    
    const components = [
      { name: 'Propagation', value: data.propagationDelay, color: '#5B5FC7' },
      { name: 'Processing', value: data.processingDelay, color: '#10B981' },
      { name: 'Serialization', value: data.serializationDelay, color: '#F59E0B' },
      { name: 'Queueing', value: data.queueingDelay, color: '#EF4444' }
    ];
    
    let x = 50;
    components.forEach(comp => {
      const compWidth = (comp.value / data.totalLatency) * totalWidth;
      
      // Draw component
      ctx.fillStyle = comp.color;
      ctx.fillRect(x, barY, compWidth, barHeight);
      
      // Draw label if wide enough
      if (compWidth > 50) {
        ctx.fillStyle = 'white';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(comp.name, x + compWidth / 2, barY + barHeight / 2 + 4);
      }
      
      x += compWidth;
    });
    
    // Draw total latency label
    ctx.fillStyle = '#4B5563';
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(`Total: ${data.totalLatency.toFixed(2)}ms`, width / 2, barY - 10);
    
    // Animate data packet
    this.animatePacket(data);
  }
  
  animatePacket(data) {
    // Cancel previous animation
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    // Initialize particles
    this.particles = [];
    const particleCount = 5;
    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: 50 - i * 20,
        y: this.canvas.height / 2,
        speed: 2 + Math.random(),
        size: 4 + Math.random() * 2
      });
    }
    
    // Animation loop
    const animate = () => {
      const ctx = this.ctx;
      const width = this.canvas.width;
      const height = this.canvas.height;
      
      // Clear animation area (top part only)
      ctx.clearRect(0, 0, width, height / 2 - 30);
      
      // Update and draw particles
      this.particles.forEach(particle => {
        // Update position
        particle.x += particle.speed;
        
        // Wrap around
        if (particle.x > width - 50) {
          particle.x = 50;
        }
        
        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y - 50, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = '#00BCD4';
        ctx.fill();
        
        // Draw trail
        ctx.beginPath();
        ctx.moveTo(particle.x - 10, particle.y - 50);
        ctx.lineTo(particle.x, particle.y - 50);
        ctx.strokeStyle = 'rgba(0, 188, 212, 0.3)';
        ctx.lineWidth = particle.size;
        ctx.stroke();
      });
      
      this.animationId = requestAnimationFrame(animate);
    };
    
    animate();
  }
  
  displayResults(data) {
    // Update the result values in the existing HTML structure
    document.getElementById('prop-delay').textContent = `${data.propagationDelay.toFixed(2)} ms`;
    document.getElementById('proc-delay').textContent = `${data.processingDelay.toFixed(2)} ms`;
    document.getElementById('serial-delay').textContent = `${data.serializationDelay.toFixed(2)} ms`;
    document.getElementById('total-rtt').textContent = `${(data.totalLatency * 2).toFixed(2)} ms`;
    
    const speedOfLightTime = (data.distance / data.SPEED_OF_LIGHT) * 1000;
    const efficiency = (speedOfLightTime / data.totalLatency) * 100;
    
    resultsDiv.innerHTML = `
      <div class="results-grid">
        <div class="result-card">
          <h4>📊 Latency Breakdown</h4>
          <div class="latency-bars">
            <div class="latency-bar">
              <div class="bar-label">
                <span>Propagation</span>
                <span>${data.propagationDelay.toFixed(2)}ms</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${(data.propagationDelay/data.totalLatency*100)}%; background: #5B5FC7;"></div>
              </div>
            </div>
            <div class="latency-bar">
              <div class="bar-label">
                <span>Processing</span>
                <span>${data.processingDelay.toFixed(2)}ms</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${(data.processingDelay/data.totalLatency*100)}%; background: #10B981;"></div>
              </div>
            </div>
            <div class="latency-bar">
              <div class="bar-label">
                <span>Serialization</span>
                <span>${data.serializationDelay.toFixed(2)}ms</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${(data.serializationDelay/data.totalLatency*100)}%; background: #F59E0B;"></div>
              </div>
            </div>
            <div class="latency-bar">
              <div class="bar-label">
                <span>Queueing</span>
                <span>${data.queueingDelay.toFixed(2)}ms</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width: ${(data.queueingDelay/data.totalLatency*100)}%; background: #EF4444;"></div>
              </div>
            </div>
          </div>
          <div class="total-latency">
            <strong>One-Way Latency:</strong> ${data.totalLatency.toFixed(2)}ms<br>
            <strong>Round-Trip Time:</strong> ${(data.totalLatency * 2).toFixed(2)}ms
          </div>
        </div>
        
        <div class="result-card">
          <h4>💡 Insights & Optimization</h4>
          <div class="insights">
            <div class="insight-item">
              <span class="insight-icon">⚡</span>
              <div>
                <strong>Efficiency Score: ${efficiency.toFixed(1)}%</strong><br>
                <small>vs. theoretical minimum (${speedOfLightTime.toFixed(2)}ms)</small>
              </div>
            </div>
            <div class="insight-item">
              <span class="insight-icon">${data.propagationDelay > data.processingDelay ? '🌍' : '🖥️'}</span>
              <div>
                <strong>${data.propagationDelay > data.processingDelay ? 'Distance-bound' : 'Processing-bound'}</strong><br>
                <small>${data.propagationDelay > data.processingDelay ? 
                  'Consider edge locations or CDN' : 
                  'Optimize network devices and routing'}</small>
              </div>
            </div>
            <div class="insight-item">
              <span class="insight-icon">📈</span>
              <div>
                <strong>Improvement Potential</strong><br>
                <small>${this.getOptimizationTips(data)}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="comparison-section">
        <h4>🌐 Real-World Context</h4>
        <div class="comparison-grid">
          ${this.getLatencyComparisons(data.totalLatency)}
        </div>
      </div>
    `;
  }
  
  getOptimizationTips(data) {
    const tips = [];
    
    if (data.propagationDelay / data.totalLatency > 0.7) {
      tips.push('Deploy closer to users');
    }
    if (data.processingDelay > 5) {
      tips.push('Reduce network hops');
    }
    if (data.queueingDelay > 10) {
      tips.push('Upgrade network capacity');
    }
    
    return tips.join(', ') || 'System is well-optimized';
  }
  
  getLatencyComparisons(latency) {
    const comparisons = [
      { name: 'Human reaction', time: 250, icon: '👤' },
      { name: 'Blink of eye', time: 300, icon: '👁️' },
      { name: 'Google search', time: 100, icon: '🔍' },
      { name: 'Video frame @60fps', time: 16.67, icon: '🎬' },
      { name: 'CPU cache hit', time: 0.001, icon: '💾' }
    ];
    
    return comparisons.map(comp => `
      <div class="comparison-item ${latency < comp.time ? 'faster' : 'slower'}">
        <span class="comparison-icon">${comp.icon}</span>
        <span class="comparison-name">${comp.name}</span>
        <span class="comparison-time">${comp.time}ms</span>
        <span class="comparison-factor">${latency < comp.time ? 
          `${(comp.time / latency).toFixed(1)}x faster` : 
          `${(latency / comp.time).toFixed(1)}x slower`}</span>
      </div>
    `).join('');
  }
  
  addTooltips() {
    const tooltips = {
      'distance': 'Physical distance between endpoints in kilometers',
      'medium': 'The physical medium through which data travels',
      'hops': 'Number of intermediate network devices',
      'routers': 'Layer 3 devices that route between networks',
      'switches': 'Layer 2 devices for local network switching',
      'firewalls': 'Security devices that inspect traffic',
      'lbs': 'Load balancers that distribute traffic'
    };
    
    Object.entries(tooltips).forEach(([id, text]) => {
      const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
      if (element) {
        element.setAttribute('title', text);
      }
    });
  }
}

// Initialize calculator
const calculator = new LatencyCalculator();