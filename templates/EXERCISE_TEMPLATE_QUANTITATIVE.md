# Exercise Template: Quantitative Methods

This template ensures rigorous, calculation-based exercises for quantitative content.

## Structure

```markdown
# [Quantitative Topic] Exercises

## 🧮 Fundamental Calculations

### Problem Set 1: [Basic Concepts]
**Difficulty**: ⭐⭐ (Beginner)
**Time**: 30 minutes
**Tools**: Calculator, Python/Excel (optional)

#### Problem 1.1: [Direct Application]
**Given**:
- Parameter A = [specific value with units]
- Parameter B = [specific value with units]
- Parameter C = [specific value with units]

**Calculate**:
a) [Specific calculation request]
b) [Related calculation]
c) [Analysis question based on results]

**Show Your Work**: Full credit requires showing steps

<details>
<summary>Solution</summary>

**Part a)**
```
Step 1: Identify the formula
[Formula with explanation]

Step 2: Substitute values
[Show substitution]

Step 3: Calculate
[Show arithmetic]

Result: [Answer with units]
```

**Part b)**
[Similar detailed steps]

**Part c) Analysis**
[Interpretation of results in context]

**Key Insight**: [What this calculation teaches us]
</details>

#### Problem 1.2: [Variations and Sensitivity]
Using the scenario from Problem 1.1:

**Investigate**:
a) How does the result change if Parameter A doubles?
b) What value of Parameter B would give Result = X?
c) Plot the relationship between A and Result for A ∈ [range]

[Similar solution structure]

### Problem Set 2: [Real-World Application]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 45 minutes
**Context**: Real system parameters

#### Problem 2.1: [Company] System Analysis
**Background**: [Company] reported these metrics in their engineering blog:
- Metric 1: [actual value from real system]
- Metric 2: [actual value from real system]
- Metric 3: [actual value from real system]

**Tasks**:
a) Calculate [derived metric]
b) Determine if their system is [property]
c) Recommend optimizations based on calculations

[Detailed solution with real-world context]

## 📊 Data Analysis Exercises

### Exercise 1: [Analyzing Production Data]
**Difficulty**: ⭐⭐⭐ (Intermediate)
**Time**: 60 minutes
**Tools**: Python with pandas, numpy, matplotlib

#### Dataset Provided
```python
# load_production_data.py
import pandas as pd

# Dataset contains 1 week of production metrics
# Columns: timestamp, requests, latency_p50, latency_p99, 
#          errors, cpu_usage, memory_usage
data = pd.read_csv('production_metrics.csv')
```

#### Analysis Tasks

##### Task 1: Statistical Characterization (20 min)
Calculate and interpret:
```python
# TODO: Your analysis code here
def analyze_metrics(data):
    # 1. Basic statistics (mean, std, percentiles)
    # 2. Distributions (histogram, QQ plots)
    # 3. Correlations between metrics
    # 4. Time-based patterns
    pass
```

##### Task 2: Capacity Analysis (20 min)
Determine:
1. Current utilization levels
2. Headroom before saturation
3. Scaling triggers

##### Task 3: Anomaly Detection (20 min)
Identify:
1. Outlier events
2. Unusual patterns
3. Potential issues

#### Deliverables
- Jupyter notebook with analysis
- Summary report with findings
- Recommendations based on data

<details>
<summary>Reference Analysis</summary>

[Complete notebook with professional data analysis]
</details>

### Exercise 2: [Predictive Modeling]
**Difficulty**: ⭐⭐⭐⭐ (Advanced)
**Time**: 90 minutes

[Similar structure for building predictive models]

## 🔬 Experimental Design

### Lab 1: [Performance Testing]
**Objective**: Design and execute controlled experiments
**Time**: 2 hours
**Tools**: Load testing framework, monitoring

#### Experiment Design

##### Hypothesis
"[Specific hypothesis about system behavior]"

##### Variables
- **Independent**: [What you'll change]
- **Dependent**: [What you'll measure]
- **Controlled**: [What you'll keep constant]

##### Methodology
1. **Baseline Establishment**
   ```bash
   # Run baseline test
   load_test --users 100 --duration 5m --rate constant
   ```

2. **Variable Manipulation**
   ```bash
   # Test different conditions
   for users in 100 200 400 800 1600; do
       load_test --users $users --duration 5m --rate constant
       collect_metrics > results_${users}.json
   done
   ```

3. **Data Collection**
   Metrics to collect:
   - Response time percentiles
   - Throughput
   - Error rates
   - Resource utilization

#### Analysis Framework

##### Statistical Tests
```python
from scipy import stats

def analyze_experiment(baseline, treatment):
    # 1. Test for statistical significance
    # 2. Calculate effect size
    # 3. Check assumptions
    # 4. Report confidence intervals
    pass
```

##### Visualization Requirements
1. Response time vs load
2. Throughput vs load  
3. Universal scalability law fit
4. Resource utilization heatmap

<details>
<summary>Expected Results and Interpretation</summary>

[Detailed analysis of what students should find]
</details>

### Lab 2: [A/B Testing]
**Difficulty**: ⭐⭐⭐⭐ (Advanced)
**Time**: 2 hours

[Similar structure for A/B testing methodology]

## 🎯 Optimization Problems

### Problem 1: [Cost Optimization]
**Scenario**: You manage a distributed system with these characteristics:
- Current costs: $X/month
- Usage patterns: [specific patterns]
- Constraints: [specific constraints]

#### Part A: Model Current Costs
Build a cost model:
```python
def calculate_monthly_cost(
    compute_hours,
    storage_gb,
    network_gb,
    requests
):
    # TODO: Implement cost model
    pass
```

#### Part B: Optimization
Find the configuration that minimizes cost while meeting SLAs:
- Latency ≤ 100ms (p99)
- Availability ≥ 99.9%
- Throughput ≥ 10k req/s

Use linear programming, gradient descent, or other optimization techniques.

#### Part C: Sensitivity Analysis
How sensitive is your solution to:
1. Price changes
2. Load variations
3. SLA requirements

<details>
<summary>Solution Approach</summary>

[Detailed optimization solution with code]
</details>

### Problem 2: [Performance Optimization]
**Difficulty**: ⭐⭐⭐⭐⭐ (Expert)

[Complex multi-objective optimization problem]

## 📈 Modeling Exercises

### Exercise 1: [Queue Theory Application]
**Time**: 90 minutes
**Objective**: Model real system using queue theory

#### System Description
[Detailed system description with parameters]

#### Tasks

##### Task 1: Model Selection (30 min)
1. Identify system characteristics
2. Choose appropriate queue model (M/M/1, M/M/c, etc.)
3. Justify your choice
4. State assumptions

##### Task 2: Analysis (30 min)
Calculate:
1. Average queue length
2. Average wait time
3. Server utilization
4. Probability of queuing

##### Task 3: Validation (30 min)
```python
# Simulate system to validate model
import simpy
import numpy as np

def simulate_queue_system():
    # TODO: Implement simulation
    pass

# Compare theoretical vs simulation results
```

### Exercise 2: [Scaling Model]
**Build and validate a scaling model for distributed system**

[Similar structure with focus on scaling laws]

## 🏆 Challenge Problems

### Challenge 1: [The Distributed Counter]
**Difficulty**: ⭐⭐⭐⭐⭐ (Expert)
**Time**: 3 hours

Design a distributed counter that:
- Handles 1M increments/second
- Provides eventual consistency
- Minimizes coordination overhead

**Quantitative Requirements**:
1. Model the trade-off between accuracy and performance
2. Calculate optimal sync intervals
3. Prove bounded error mathematically
4. Implement and validate model

### Challenge 2: [The Capacity Planning Problem]
**Based on**: Real capacity planning at [Company]

[Complex, multi-faceted problem requiring various quantitative techniques]

## 📚 Research Projects

### Project 1: [Reproduce Published Results]
**Paper**: "[Paper Title]" by [Authors]
**Objective**: Reproduce key quantitative results

#### Tasks
1. Implement models from paper
2. Reproduce key figures
3. Validate on your own data
4. Extend analysis

### Project 2: [Original Analysis]
**Topic**: [Current hot topic in distributed systems]
**Objective**: Perform novel quantitative analysis

[Guidelines for original research]

## 🧪 Tools and Utilities

### Provided Tools
```python
# utils.py - Helper functions for exercises

def little_law_calculator(arrival_rate, service_time):
    """Calculate queue metrics using Little's Law"""
    pass

def universal_scalability_law(N, alpha, beta):
    """Calculate speedup using USL"""
    pass

def simulate_poisson_arrivals(rate, duration):
    """Generate Poisson arrival times"""
    pass

# More utility functions...
```

### Jupyter Notebook Templates
- Data analysis template
- Experiment analysis template
- Optimization template
- Visualization template

## 📊 Visualization Requirements

### Every Exercise Should Include
1. **Clear Plots** with:
   - Labeled axes with units
   - Legends
   - Error bars where appropriate
   - Professional styling

2. **Multiple Views**:
   - Time series
   - Distributions
   - Correlations
   - Model fits

3. **Interactive Elements** (where appropriate):
   - Sliders for parameters
   - Zoom/pan for exploration
   - Tooltips with details

Example:
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_scaling_analysis(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Throughput vs cores
    ax1.plot(data['cores'], data['throughput'], 'o-')
    ax1.plot(data['cores'], data['theoretical'], '--', alpha=0.7)
    ax1.set_xlabel('Number of Cores')
    ax1.set_ylabel('Throughput (req/s)')
    ax1.set_title('Measured vs Theoretical Scaling')
    ax1.legend(['Measured', 'USL Model'])
    
    # Efficiency
    ax2.plot(data['cores'], data['efficiency'], 's-')
    ax2.axhline(y=0.8, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Number of Cores')
    ax2.set_ylabel('Efficiency')
    ax2.set_title('Scaling Efficiency')
    
    plt.tight_layout()
    return fig
```

## Assessment Rubric

### Calculation Problems
| Criteria | Excellent (4) | Good (3) | Adequate (2) | Needs Work (1) |
|----------|---------------|----------|---------------|----------------|
| Accuracy | All calculations correct | Minor errors | Major errors | Incorrect approach |
| Method | Clear, efficient approach | Good approach | Works but inefficient | Poor method |
| Interpretation | Deep insights | Good analysis | Basic interpretation | Missing analysis |
| Presentation | Professional, clear | Well organized | Adequate | Poorly presented |

### Programming Exercises
[Similar rubric for code-based problems]
```

## Usage Guidelines

1. **Real Data**: Use actual production data where possible
2. **Show Work**: Require students to show calculations, not just answers
3. **Multiple Methods**: Encourage solving problems multiple ways
4. **Validation**: Always validate theoretical results with simulation/data
5. **Context**: Connect calculations to real engineering decisions
6. **Tools**: Provide starter code and utilities
7. **Visualization**: Require professional-quality plots

## Quality Checklist

- [ ] Mix of hand calculations and programming
- [ ] Real-world data and scenarios
- [ ] Progressive difficulty within each section
- [ ] Clear rubrics for assessment
- [ ] Validation through multiple approaches
- [ ] Professional visualization requirements
- [ ] Research and experimentation components
- [ ] Provided tools and templates
- [ ] Connection to engineering decisions
- [ ] Both individual and team exercises