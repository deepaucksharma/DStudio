// Hero Network Visualization Animation
class NetworkVisualization {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = [];
    this.connections = [];
    this.animationId = null;
    
    // Get colors from CSS custom properties
    const rootStyles = getComputedStyle(document.documentElement);
    this.colors = {
      primary: rootStyles.getPropertyValue('--primary-500').trim() || '#3F51B5',
      primaryLight: rootStyles.getPropertyValue('--primary-300').trim() || '#7986CB',
      primaryDark: rootStyles.getPropertyValue('--primary-700').trim() || '#303F9F',
      accent: rootStyles.getPropertyValue('--info-500').trim() || '#2196F3'
    };
    
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
  
  hexToRgb(hex) {
    // Remove # if present
    hex = hex.replace(/^#/, '');
    
    // Parse hex values
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    
    return { r, g, b };
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
      // Use primary color with low opacity for connections
      const primaryRGB = this.hexToRgb(this.colors.primary);
      this.ctx.strokeStyle = `rgba(${primaryRGB.r}, ${primaryRGB.g}, ${primaryRGB.b}, 0.1)`;
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
      this.ctx.fillStyle = this.colors.accent;
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
      const primaryLightRGB = this.hexToRgb(this.colors.primaryLight);
      this.ctx.fillStyle = `rgba(${primaryLightRGB.r}, ${primaryLightRGB.g}, ${primaryLightRGB.b}, 0.8)`;
      this.ctx.arc(node.x, node.y, pulseRadius, 0, Math.PI * 2);
      this.ctx.fill();
      
      // Inner circle
      this.ctx.beginPath();
      this.ctx.fillStyle = this.colors.primaryDark;
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
  // Skip animation on mobile devices for performance
  const isMobile = window.innerWidth <= 768 || ('ontouchstart' in window);
  
  if (isMobile) {
    // Hide animation container on mobile
    const container = document.querySelector('.hero-animation');
    if (container) {
      container.style.display = 'none';
    }
    return;
  }
  
  const canvas = document.getElementById('network-visualization');
  if (canvas) {
    new NetworkVisualization(canvas);
  }
});