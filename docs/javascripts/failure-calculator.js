// Failure Probability Calculator
class FailureCalculator {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.timelineCanvas = null;
    this.timelineCtx = null;
    this.init();
  }
  
  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupCalculator());
    } else {
      this.setupCalculator();
    }
  }
  
  setupCalculator() {
    const form = document.getElementById('failure-calc');
    if (!form) return;
    
    // Set up event listeners
    form.addEventListener('input', () => this.calculateReliability());
    
    // Handle time period selection
    const timePeriod = document.getElementById('time-period');
    const customTimeGroup = document.getElementById('custom-time-group');
    if (timePeriod && customTimeGroup) {
      timePeriod.addEventListener('change', (e) => {
        customTimeGroup.style.display = e.target.value === 'custom' ? 'block' : 'none';
        this.calculateReliability();
      });
    }
    
    // Initialize visualization
    this.initVisualization();
    
    // Initial calculation
    this.calculateReliability();
  }
  
  initVisualization() {
    // Create main visualization container
    const vizContainer = document.getElementById('failure-visualization');
    if (!vizContainer) return;
    
    // Create canvas for system diagram
    this.canvas = document.createElement('canvas');
    this.canvas.width = 800;
    this.canvas.height = 300;
    this.ctx = this.canvas.getContext('2d');
    vizContainer.appendChild(this.canvas);
    
    // Get timeline canvas
    this.timelineCanvas = document.getElementById('timeline-chart');
    if (this.timelineCanvas) {
      this.timelineCtx = this.timelineCanvas.getContext('2d');
    }
  }
  
  calculateReliability() {
    // Get input values
    const mtbf = parseFloat(document.getElementById('component-mtbf').value) || 10000;
    const mttr = parseFloat(document.getElementById('component-mttr').value) || 4;
    const componentCount = parseInt(document.getElementById('components-count').value) || 5;
    const redundancyType = document.getElementById('redundancy-type').value;
    const failoverTime = parseFloat(document.getElementById('failover-time').value) || 30;
    
    // Get time period in hours
    const timePeriod = document.getElementById('time-period').value;
    let hours;
    switch (timePeriod) {
      case 'hour': hours = 1; break;
      case 'day': hours = 24; break;
      case 'week': hours = 168; break;
      case 'month': hours = 720; break;
      case 'year': hours = 8760; break;
      case 'custom': hours = parseFloat(document.getElementById('custom-hours').value) || 720; break;
      default: hours = 24;
    }
    
    // Calculate component reliability
    const componentAvailability = mtbf / (mtbf + mttr);
    const componentFailureRate = 1 / mtbf;
    const componentReliability = Math.exp(-componentFailureRate * hours);
    
    // Calculate system reliability based on redundancy
    let systemAvailability, systemReliability, expectedFailures;
    
    switch (redundancyType) {
      case 'none':
        // Series system - all components must work
        systemAvailability = Math.pow(componentAvailability, componentCount);
        systemReliability = Math.pow(componentReliability, componentCount);
        expectedFailures = componentCount * componentFailureRate * hours;
        break;
        
      case 'active-standby':
        // One backup for entire system
        const p = componentAvailability;
        systemAvailability = p + (1-p)*p*(mtbf/(mtbf+failoverTime/3600));
        systemReliability = 1 - Math.pow(1 - componentReliability, 2);
        expectedFailures = componentFailureRate * hours * 0.5; // Reduced due to redundancy
        break;
        
      case 'active-active':
        // All components active with load balancing
        systemAvailability = 1 - Math.pow(1 - componentAvailability, componentCount);
        systemReliability = 1 - Math.pow(1 - componentReliability, componentCount);
        expectedFailures = componentFailureRate * hours * 0.3; // Further reduced
        break;
        
      case 'n+1':
        // Can tolerate 1 failure
        systemAvailability = this.calculateNPlusKAvailability(componentAvailability, componentCount, 1);
        systemReliability = this.calculateNPlusKReliability(componentReliability, componentCount, 1);
        expectedFailures = componentFailureRate * hours * 0.4;
        break;
        
      case 'n+2':
        // Can tolerate 2 failures
        systemAvailability = this.calculateNPlusKAvailability(componentAvailability, componentCount, 2);
        systemReliability = this.calculateNPlusKReliability(componentReliability, componentCount, 2);
        expectedFailures = componentFailureRate * hours * 0.2;
        break;
        
      case '2n':
        // Full duplication
        systemAvailability = 1 - Math.pow(1 - componentAvailability, 2);
        systemReliability = 1 - Math.pow(1 - componentReliability, 2);
        expectedFailures = componentFailureRate * hours * 0.1;
        break;
    }
    
    // Calculate failure probability
    const failureProbability = 1 - systemReliability;
    
    // Calculate nines of availability
    const nines = this.calculateNines(systemAvailability);
    
    // Update visualization
    this.drawSystemDiagram(redundancyType, componentCount);
    this.drawTimelineChart(componentFailureRate, hours, redundancyType);
    
    // Display results
    this.displayResults({
      systemAvailability,
      failureProbability,
      expectedFailures,
      nines,
      componentAvailability,
      redundancyType,
      hours,
      mtbf,
      mttr
    });
  }
  
  calculateNPlusKAvailability(p, n, k) {
    // Probability that at least n components out of n+k are working
    let availability = 0;
    const total = n + k;
    
    for (let i = n; i <= total; i++) {
      availability += this.binomial(total, i) * Math.pow(p, i) * Math.pow(1-p, total-i);
    }
    
    return availability;
  }
  
  calculateNPlusKReliability(r, n, k) {
    // Similar to availability but for reliability over time
    let reliability = 0;
    const total = n + k;
    
    for (let i = n; i <= total; i++) {
      reliability += this.binomial(total, i) * Math.pow(r, i) * Math.pow(1-r, total-i);
    }
    
    return reliability;
  }
  
  binomial(n, k) {
    // Calculate binomial coefficient
    if (k > n - k) k = n - k;
    let result = 1;
    for (let i = 0; i < k; i++) {
      result = result * (n - i) / (i + 1);
    }
    return result;
  }
  
  calculateNines(availability) {
    if (availability >= 0.99999) return "Five 9s (99.999%)";
    if (availability >= 0.9999) return "Four 9s (99.99%)";
    if (availability >= 0.999) return "Three 9s (99.9%)";
    if (availability >= 0.99) return "Two 9s (99%)";
    if (availability >= 0.9) return "One 9 (90%)";
    return "< 90%";
  }
  
  drawSystemDiagram(redundancyType, componentCount) {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw title
    ctx.font = '16px Inter';
    ctx.fillStyle = '#111827';
    ctx.textAlign = 'center';
    ctx.fillText(`System Architecture: ${this.getRedundancyTitle(redundancyType)}`, width/2, 30);
    
    // Draw components based on redundancy type
    const boxWidth = 80;
    const boxHeight = 50;
    const spacing = 30;
    
    switch (redundancyType) {
      case 'none':
        // Series configuration
        this.drawSeriesComponents(ctx, componentCount, boxWidth, boxHeight, spacing);
        break;
        
      case 'active-standby':
        // Primary with standby
        this.drawActiveStandby(ctx, componentCount, boxWidth, boxHeight, spacing);
        break;
        
      case 'active-active':
        // Parallel configuration
        this.drawParallelComponents(ctx, componentCount, boxWidth, boxHeight, spacing);
        break;
        
      case 'n+1':
      case 'n+2':
        // N+K configuration
        const k = redundancyType === 'n+1' ? 1 : 2;
        this.drawNPlusK(ctx, componentCount, k, boxWidth, boxHeight, spacing);
        break;
        
      case '2n':
        // Full duplication
        this.draw2N(ctx, componentCount, boxWidth, boxHeight, spacing);
        break;
    }
  }
  
  drawSeriesComponents(ctx, count, boxWidth, boxHeight, spacing) {
    const startX = (this.canvas.width - (count * boxWidth + (count-1) * spacing)) / 2;
    const y = 120;
    
    for (let i = 0; i < count; i++) {
      const x = startX + i * (boxWidth + spacing);
      
      // Draw component box
      ctx.fillStyle = '#E0E7FF';
      ctx.strokeStyle = '#5448C8';
      ctx.lineWidth = 2;
      ctx.fillRect(x, y, boxWidth, boxHeight);
      ctx.strokeRect(x, y, boxWidth, boxHeight);
      
      // Draw label
      ctx.fillStyle = '#111827';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(`C${i+1}`, x + boxWidth/2, y + boxHeight/2 + 5);
      
      // Draw connection
      if (i < count - 1) {
        ctx.strokeStyle = '#6B7280';
        ctx.beginPath();
        ctx.moveTo(x + boxWidth, y + boxHeight/2);
        ctx.lineTo(x + boxWidth + spacing, y + boxHeight/2);
        ctx.stroke();
      }
    }
    
    // Label
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('All components must work (Series)', this.canvas.width/2, y + boxHeight + 30);
  }
  
  drawParallelComponents(ctx, count, boxWidth, boxHeight, spacing) {
    const startX = 200;
    const startY = 80;
    const verticalSpacing = 20;
    
    for (let i = 0; i < count; i++) {
      const y = startY + i * (boxHeight + verticalSpacing);
      
      // Draw component
      ctx.fillStyle = '#D1FAE5';
      ctx.strokeStyle = '#10B981';
      ctx.lineWidth = 2;
      ctx.fillRect(startX, y, boxWidth, boxHeight);
      ctx.strokeRect(startX, y, boxWidth, boxHeight);
      
      // Label
      ctx.fillStyle = '#111827';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(`C${i+1}`, startX + boxWidth/2, y + boxHeight/2 + 5);
    }
    
    // Draw input/output lines
    const centerY = startY + (count-1) * (boxHeight + verticalSpacing) / 2 + boxHeight/2;
    
    ctx.strokeStyle = '#6B7280';
    ctx.lineWidth = 2;
    
    // Input
    ctx.beginPath();
    ctx.moveTo(100, centerY);
    ctx.lineTo(startX, centerY);
    for (let i = 0; i < count; i++) {
      const y = startY + i * (boxHeight + verticalSpacing) + boxHeight/2;
      ctx.moveTo(150, centerY);
      ctx.lineTo(150, y);
      ctx.lineTo(startX, y);
    }
    ctx.stroke();
    
    // Output
    ctx.beginPath();
    for (let i = 0; i < count; i++) {
      const y = startY + i * (boxHeight + verticalSpacing) + boxHeight/2;
      ctx.moveTo(startX + boxWidth, y);
      ctx.lineTo(startX + boxWidth + 50, y);
      ctx.lineTo(startX + boxWidth + 50, centerY);
    }
    ctx.moveTo(startX + boxWidth + 50, centerY);
    ctx.lineTo(startX + boxWidth + 150, centerY);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Any component can handle load (Parallel)', this.canvas.width/2, 250);
  }
  
  drawActiveStandby(ctx, count, boxWidth, boxHeight, spacing) {
    const centerX = this.canvas.width / 2;
    const primaryY = 100;
    const standbyY = 180;
    
    // Primary
    ctx.fillStyle = '#D1FAE5';
    ctx.strokeStyle = '#10B981';
    ctx.lineWidth = 2;
    ctx.fillRect(centerX - boxWidth/2, primaryY, boxWidth, boxHeight);
    ctx.strokeRect(centerX - boxWidth/2, primaryY, boxWidth, boxHeight);
    
    ctx.fillStyle = '#111827';
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Primary', centerX, primaryY + boxHeight/2 + 5);
    
    // Standby
    ctx.fillStyle = '#FEE2E2';
    ctx.strokeStyle = '#EF4444';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.fillRect(centerX - boxWidth/2, standbyY, boxWidth, boxHeight);
    ctx.strokeRect(centerX - boxWidth/2, standbyY, boxWidth, boxHeight);
    ctx.setLineDash([]);
    
    ctx.fillStyle = '#111827';
    ctx.fillText('Standby', centerX, standbyY + boxHeight/2 + 5);
    
    // Failover arrow
    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX + boxWidth/2 + 20, primaryY + boxHeight/2);
    ctx.lineTo(centerX + boxWidth/2 + 40, primaryY + boxHeight/2);
    ctx.lineTo(centerX + boxWidth/2 + 40, standbyY + boxHeight/2);
    ctx.lineTo(centerX + boxWidth/2 + 20, standbyY + boxHeight/2);
    ctx.stroke();
    
    // Arrow head
    ctx.beginPath();
    ctx.moveTo(centerX + boxWidth/2 + 15, standbyY + boxHeight/2 - 5);
    ctx.lineTo(centerX + boxWidth/2 + 20, standbyY + boxHeight/2);
    ctx.lineTo(centerX + boxWidth/2 + 15, standbyY + boxHeight/2 + 5);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Standby takes over on failure', centerX, 260);
  }
  
  drawNPlusK(ctx, n, k, boxWidth, boxHeight, spacing) {
    const totalComponents = n + k;
    const startX = (this.canvas.width - (totalComponents * boxWidth + (totalComponents-1) * spacing)) / 2;
    const y = 120;
    
    for (let i = 0; i < totalComponents; i++) {
      const x = startX + i * (boxWidth + spacing);
      const isSpare = i >= n;
      
      // Draw component
      ctx.fillStyle = isSpare ? '#FEF3C7' : '#D1FAE5';
      ctx.strokeStyle = isSpare ? '#F59E0B' : '#10B981';
      ctx.lineWidth = 2;
      ctx.fillRect(x, y, boxWidth, boxHeight);
      ctx.strokeRect(x, y, boxWidth, boxHeight);
      
      // Label
      ctx.fillStyle = '#111827';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(isSpare ? `Spare ${i-n+1}` : `C${i+1}`, x + boxWidth/2, y + boxHeight/2 + 5);
    }
    
    // Label
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(`${n} required + ${k} spare components`, this.canvas.width/2, y + boxHeight + 30);
  }
  
  draw2N(ctx, count, boxWidth, boxHeight, spacing) {
    const groupSpacing = 50;
    const startX = (this.canvas.width - (2 * count * boxWidth + count * spacing + groupSpacing)) / 2;
    const y = 120;
    
    // Primary group
    ctx.fillStyle = '#D1FAE5';
    ctx.strokeStyle = '#10B981';
    for (let i = 0; i < count; i++) {
      const x = startX + i * (boxWidth + spacing);
      ctx.lineWidth = 2;
      ctx.fillRect(x, y, boxWidth, boxHeight);
      ctx.strokeRect(x, y, boxWidth, boxHeight);
      
      ctx.fillStyle = '#111827';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(`P${i+1}`, x + boxWidth/2, y + boxHeight/2 + 5);
    }
    
    // Backup group
    const backupStartX = startX + count * (boxWidth + spacing) + groupSpacing;
    ctx.fillStyle = '#E0E7FF';
    ctx.strokeStyle = '#5448C8';
    for (let i = 0; i < count; i++) {
      const x = backupStartX + i * (boxWidth + spacing);
      ctx.lineWidth = 2;
      ctx.fillRect(x, y, boxWidth, boxHeight);
      ctx.strokeRect(x, y, boxWidth, boxHeight);
      
      ctx.fillStyle = '#111827';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(`B${i+1}`, x + boxWidth/2, y + boxHeight/2 + 5);
    }
    
    // Label
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Full system duplication (2N)', this.canvas.width/2, y + boxHeight + 30);
  }
  
  getRedundancyTitle(type) {
    const titles = {
      'none': 'No Redundancy',
      'active-standby': 'Active-Standby',
      'active-active': 'Active-Active',
      'n+1': 'N+1 Redundancy',
      'n+2': 'N+2 Redundancy',
      '2n': '2N Redundancy'
    };
    return titles[type] || type;
  }
  
  drawTimelineChart(failureRate, hours, redundancyType) {
    if (!this.timelineCanvas || !this.timelineCtx) return;
    
    const ctx = this.timelineCtx;
    const width = this.timelineCanvas.width;
    const height = this.timelineCanvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw axes
    const padding = 40;
    ctx.strokeStyle = '#4B5563';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // Draw reliability curve
    ctx.strokeStyle = '#5448C8';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const timePoints = 100;
    for (let i = 0; i <= timePoints; i++) {
      const t = (i / timePoints) * hours;
      const reliability = Math.exp(-failureRate * t);
      
      // Apply redundancy factor
      let systemReliability = reliability;
      if (redundancyType !== 'none') {
        systemReliability = 1 - Math.pow(1 - reliability, 2); // Simplified for visualization
      }
      
      const x = padding + (i / timePoints) * (width - 2 * padding);
      const y = height - padding - (systemReliability * (height - 2 * padding));
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
    
    // Draw expected failure points
    const expectedFailureTime = 1 / failureRate;
    if (expectedFailureTime < hours) {
      const failureX = padding + (expectedFailureTime / hours) * (width - 2 * padding);
      
      ctx.strokeStyle = '#EF4444';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(failureX, padding);
      ctx.lineTo(failureX, height - padding);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Label
      ctx.fillStyle = '#EF4444';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('Expected failure', failureX, padding - 5);
    }
    
    // Labels
    ctx.fillStyle = '#4B5563';
    ctx.font = '14px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('Time (hours)', width / 2, height - 5);
    
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Reliability', 0, 0);
    ctx.restore();
  }
  
  displayResults(data) {
    // Update main metrics
    document.getElementById('availability').textContent = `${(data.systemAvailability * 100).toFixed(3)}%`;
    document.getElementById('failure-prob').textContent = `${(data.failureProbability * 100).toFixed(2)}%`;
    document.getElementById('expected-failures').textContent = data.expectedFailures.toFixed(2);
    document.getElementById('nines-uptime').textContent = data.nines;
    
    // Generate insights
    const insights = this.generateInsights(data);
    const insightsList = document.getElementById('reliability-insights');
    if (insightsList) {
      insightsList.innerHTML = insights.map(insight => `<li>${insight}</li>`).join('');
    }
    
    // Generate redundancy comparison
    this.generateRedundancyComparison(data);
  }
  
  generateInsights(data) {
    const insights = [];
    
    // Availability insights
    if (data.systemAvailability >= 0.9999) {
      insights.push('Excellent availability! System meets enterprise-grade requirements.');
    } else if (data.systemAvailability >= 0.999) {
      insights.push('Good availability suitable for most production workloads.');
    } else if (data.systemAvailability >= 0.99) {
      insights.push('Acceptable availability for non-critical systems.');
    } else {
      insights.push('Poor availability - significant improvements needed.');
    }
    
    // Redundancy insights
    if (data.redundancyType === 'none') {
      insights.push('No redundancy - single point of failure risk!');
    } else if (data.redundancyType === '2n') {
      insights.push('Full redundancy provides maximum protection but doubles cost.');
    }
    
    // MTTR insights
    if (data.mttr > 8) {
      insights.push('High MTTR - consider automation to reduce recovery time.');
    } else if (data.mttr < 1) {
      insights.push('Excellent recovery time - well-automated systems.');
    }
    
    // Failure rate insights
    if (data.expectedFailures > 1) {
      insights.push(`Expect ${Math.floor(data.expectedFailures)} failures in the analysis period.`);
    } else if (data.expectedFailures > 0.1) {
      insights.push('Low failure rate but plan for occasional incidents.');
    }
    
    // Time period specific
    const downtime = (1 - data.systemAvailability) * data.hours * 60; // minutes
    if (downtime > 60) {
      insights.push(`Expected downtime: ${(downtime/60).toFixed(1)} hours in the period.`);
    } else if (downtime > 1) {
      insights.push(`Expected downtime: ${downtime.toFixed(0)} minutes in the period.`);
    }
    
    return insights;
  }
  
  generateRedundancyComparison(currentData) {
    const container = document.getElementById('redundancy-comparison');
    if (!container) return;
    
    const redundancyTypes = ['none', 'active-standby', 'active-active', 'n+1', 'n+2', '2n'];
    const comparisons = [];
    
    // Calculate availability for each redundancy type
    redundancyTypes.forEach(type => {
      const availability = this.calculateAvailabilityForType(
        type,
        currentData.componentAvailability,
        parseInt(document.getElementById('components-count').value)
      );
      
      comparisons.push({
        type: this.getRedundancyTitle(type),
        availability: availability,
        isCurrent: type === currentData.redundancyType
      });
    });
    
    // Generate comparison bars
    container.innerHTML = comparisons.map(comp => {
      const percentage = comp.availability * 100;
      const barClass = comp.isCurrent ? 'highlight' : '';
      
      return `
        <div class="comparison-bar ${barClass}">
          <div class="comparison-label">
            <span>${comp.type}</span>
            <span>${percentage.toFixed(3)}%</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${percentage}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }
  
  calculateAvailabilityForType(type, componentAvailability, componentCount) {
    const p = componentAvailability;
    
    switch (type) {
      case 'none':
        return Math.pow(p, componentCount);
      case 'active-standby':
        return p + (1-p)*p*0.99; // Assuming 99% failover success
      case 'active-active':
        return 1 - Math.pow(1-p, componentCount);
      case 'n+1':
        return this.calculateNPlusKAvailability(p, componentCount, 1);
      case 'n+2':
        return this.calculateNPlusKAvailability(p, componentCount, 2);
      case '2n':
        return 1 - Math.pow(1-p, 2);
      default:
        return p;
    }
  }
}

// Initialize calculator
const failureCalculator = new FailureCalculator();