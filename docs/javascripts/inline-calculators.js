// Inline Mini-Calculators for distributed systems concepts
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
      case 'littles-law':
        this.initLittlesLaw();
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
      const distance = parseFloat(input.value) || 0;
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
      const rps = parseFloat(inputs[0].value) || 0;
      const latency = parseFloat(inputs[1].value) || 0;
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
      const components = parseInt(inputs[0].value) || 1;
      const availability = parseFloat(inputs[1].value) / 100 || 0;
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
  
  initLittlesLaw() {
    this.element.innerHTML = `
      <div class="inline-calc">
        <h4>Little's Law Calculator</h4>
        <div class="calc-formula">L = λ × W</div>
        <div class="calc-row">
          <label>Arrival Rate (λ):</label>
          <input type="number" class="calc-input" data-param="lambda" value="100">
          <small>requests/second</small>
        </div>
        <div class="calc-row">
          <label>Response Time (W):</label>
          <input type="number" class="calc-input" data-param="w" value="50">
          <small>milliseconds</small>
        </div>
        <div class="calc-result">
          <span>Avg Items in System (L):</span>
          <strong class="calc-output">5</strong>
        </div>
      </div>
    `;
    
    const inputs = this.element.querySelectorAll('.calc-input');
    const output = this.element.querySelector('.calc-output');
    
    const calculate = () => {
      const lambda = parseFloat(inputs[0].value) || 0;
      const w = parseFloat(inputs[1].value) / 1000 || 0; // Convert ms to seconds
      const l = lambda * w;
      output.textContent = l.toFixed(1);
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