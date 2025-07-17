# Failure Probability Calculator

!!! info "Calculate System Reliability"
    Use probability theory to calculate system failure rates and design for resilience.

<div id="failure-calculator" class="interactive-tool">
  <form id="failure-calc">
    <div class="tool-inputs">
      <h3>Component Configuration</h3>
      
      <div class="component-section">
        <h4>Individual Components</h4>
        <div class="input-group">
          <label for="component-mtbf">Component MTBF (hours)</label>
          <input type="number" id="component-mtbf" value="10000" min="1" max="1000000">
          <small>Mean Time Between Failures</small>
        </div>
        
        <div class="input-group">
          <label for="component-mttr">Component MTTR (hours)</label>
          <input type="number" id="component-mttr" value="4" min="0.1" max="100" step="0.1">
          <small>Mean Time To Repair</small>
        </div>
        
        <div class="input-group">
          <label for="components-count">Number of Components</label>
          <input type="number" id="components-count" value="5" min="1" max="100">
          <small>Total components in system</small>
        </div>
      </div>
      
      <div class="redundancy-section">
        <h4>Redundancy Configuration</h4>
        <div class="input-group">
          <label for="redundancy-type">Redundancy Type</label>
          <select id="redundancy-type">
            <option value="none">No Redundancy</option>
            <option value="active-standby">Active-Standby</option>
            <option value="active-active">Active-Active</option>
            <option value="n+1">N+1 Redundancy</option>
            <option value="n+2">N+2 Redundancy</option>
            <option value="2n">2N Redundancy</option>
          </select>
          <small>Redundancy strategy</small>
        </div>
        
        <div class="input-group">
          <label for="failover-time">Failover Time (seconds)</label>
          <input type="number" id="failover-time" value="30" min="0" max="3600" step="1">
          <small>Time to switch to backup</small>
        </div>
      </div>
      
      <div class="timeframe-section">
        <h4>Analysis Timeframe</h4>
        <div class="input-group">
          <label for="time-period">Time Period</label>
          <select id="time-period">
            <option value="hour">1 Hour</option>
            <option value="day" selected>1 Day</option>
            <option value="week">1 Week</option>
            <option value="month">1 Month</option>
            <option value="year">1 Year</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        
        <div class="input-group" id="custom-time-group" style="display: none;">
          <label for="custom-hours">Custom Period (hours)</label>
          <input type="number" id="custom-hours" value="720" min="1" max="87600">
        </div>
      </div>
    </div>
  </form>
  
  <div id="failure-visualization" class="tool-visualization">
    <!-- Visualization will be rendered here -->
  </div>
  
  <div class="tool-results">
    <h3>Reliability Analysis</h3>
    
    <div class="result-grid">
      <div class="result-item">
        <span class="result-label">System Availability</span>
        <span class="result-value" id="availability">0%</span>
      </div>
      <div class="result-item">
        <span class="result-label">Failure Probability</span>
        <span class="result-value" id="failure-prob">0%</span>
      </div>
      <div class="result-item">
        <span class="result-label">Expected Failures</span>
        <span class="result-value" id="expected-failures">0</span>
      </div>
      <div class="result-item highlight">
        <span class="result-label">Uptime (9s)</span>
        <span class="result-value" id="nines-uptime">0 nines</span>
      </div>
    </div>
    
    <div class="result-insights">
      <h4>💡 Reliability Insights</h4>
      <ul id="reliability-insights">
        <!-- Dynamically populated -->
      </ul>
    </div>
    
    <div class="comparison-chart">
      <h4>Redundancy Impact</h4>
      <div id="redundancy-comparison">
        <!-- Dynamically populated -->
      </div>
    </div>
    
    <div class="failure-timeline">
      <h4>Failure Timeline Visualization</h4>
      <canvas id="timeline-chart" width="800" height="200"></canvas>
    </div>
  </div>
</div>

## Understanding System Reliability

### Key Concepts

<div class="concept-box">
<h4>MTBF (Mean Time Between Failures)</h4>

The average time between system failures:
- **Higher is better** - more reliable
- Measured in hours of operation
- Example: MTBF of 10,000 hours = ~416 days

**Calculation**: MTBF = Total Operating Time / Number of Failures
</div>

<div class="concept-box">
<h4>MTTR (Mean Time To Repair)</h4>

The average time to restore service after failure:
- **Lower is better** - faster recovery
- Includes detection, diagnosis, and repair
- Example: MTTR of 4 hours = 4 hour outage

**Calculation**: MTTR = Total Repair Time / Number of Repairs
</div>

<div class="concept-box">
<h4>Availability</h4>

The percentage of time a system is operational:

**A = MTBF / (MTBF + MTTR)**

Examples:
- 99% = 87.6 hours downtime/year
- 99.9% = 8.76 hours downtime/year
- 99.99% = 52.56 minutes downtime/year
- 99.999% = 5.26 minutes downtime/year
</div>

## Redundancy Strategies

### 1. Active-Standby

<div class="strategy-box">
One active component with passive backup:
- **Pros**: Simple, predictable capacity
- **Cons**: Wasted resources, failover delay
- **Availability**: ~99.9% with proper monitoring
</div>

### 2. Active-Active

<div class="strategy-box">
All components actively serving traffic:
- **Pros**: No wasted capacity, instant failover
- **Cons**: Complex state synchronization
- **Availability**: ~99.95% with good design
</div>

### 3. N+K Redundancy

<div class="strategy-box">
N required components plus K spares:
- **N+1**: Survive 1 failure
- **N+2**: Survive 2 simultaneous failures
- **2N**: Full duplication
- **Availability**: Varies from 99.9% to 99.999%
</div>

## Failure Probability Calculations

### Series Systems (AND)
All components must work:

```
P(system works) = P(A) × P(B) × P(C) × ...
P(system fails) = 1 - P(system works)
```

### Parallel Systems (OR)
At least one component must work:

```
P(system fails) = P(A fails) × P(B fails) × ...
P(system works) = 1 - P(system fails)
```

### Complex Systems
Combination of series and parallel:
- Use reliability block diagrams
- Apply reduction techniques
- Consider common cause failures

## Best Practices

### 1. Design for Failure
- Assume components will fail
- Build in redundancy
- Automate recovery
- Test failure scenarios

### 2. Monitor Everything
- Track MTBF trends
- Alert on degradation
- Measure actual availability
- Log all incidents

### 3. Reduce MTTR
- Automate detection
- Streamline diagnosis
- Practice recovery
- Document procedures

### 4. Common Patterns
- **Circuit breakers**: Prevent cascade failures
- **Bulkheads**: Isolate failures
- **Timeouts**: Fail fast
- **Retries**: Handle transient failures

## Related Resources

- [Axiom 3: Partial Failure](../part1-axioms/axiom-3-failure/index.md)
- [Capacity Planner](capacity-planner.md)
- [Recovery-Oriented Computing](../reference/recovery-oriented.md)