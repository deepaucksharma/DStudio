---
title: Auto-scaling Pattern
description: Pattern for distributed systems coordination and reliability
type: pattern
category: performance
difficulty: beginner
reading_time: 25 min
prerequisites: []
when_to_use: When dealing with performance challenges
when_not_to_use: When simpler solutions suffice
status: complete
last_updated: 2025-07-20
---

# Auto-scaling Pattern

**Dynamic resource allocation based on demand**

> *"The best infrastructure is invisible—it grows when needed, shrinks when not."*

---

## Level 1: Intuition

### Core Concept

Auto-scaling automatically adjusts computing resources based on demand, like restaurant staffing that expands during rush hours and contracts during quiet periods.

### Basic Implementation

```python
class SimpleAutoScaler:
    def __init__(self, min_instances=2, max_instances=10, target_cpu=70.0):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu
        self.instances = []

    def check_scaling_needed(self) -> str:
        """Determine scaling action based on CPU usage"""
        avg_cpu = sum(i.cpu_usage for i in self.instances) / len(self.instances)
        
        if avg_cpu > self.target_cpu + 10:  # 80%
            return "scale_up"
        elif avg_cpu < self.target_cpu - 20:  # 50%
            return "scale_down"
        return "no_change"

    def scale_up(self):
        if len(self.instances) < self.max_instances:
            self.instances.append(Instance(f"instance-{len(self.instances)}"))

    def scale_down(self):
        if len(self.instances) > self.min_instances:
            self.instances.pop()
```

---

## Level 2: Foundation

| Strategy | Trigger | Use Case | Response Time |
|----------|---------|----------|---------------|
| **Reactive** | Current metrics | Predictable load | Minutes |
| **Proactive** | Predicted metrics | Known patterns | Preemptive |
| **Scheduled** | Time-based | Business hours | Exact timing |
| **Event-driven** | External events | Marketing campaigns | Immediate |


### Metric-Based Auto-scaling

```python
class MetricBasedAutoScaler:
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.scaling_policies = []
        self.cooldown_period = 300  # 5 minutes
        self.last_scaling_time = 0

    def add_scaling_policy(self, metric: str, scale_up: float, scale_down: float):
        self.scaling_policies.append({
            'metric': metric,
            'scale_up': scale_up,
            'scale_down': scale_down
        })

    def evaluate_scaling_decision(self) -> str:
        """Evaluate policies with cooldown and majority voting"""
        if time.time() - self.last_scaling_time < self.cooldown_period:
            return "cooldown"

        votes = {'scale_up': 0, 'scale_down': 0}
        
        for policy in self.scaling_policies:
            metric_avg = self._get_metric_average(policy['metric'])
            if metric_avg > policy['scale_up']:
                votes['scale_up'] += 1
            elif metric_avg < policy['scale_down']:
                votes['scale_down'] += 1

# Majority vote decides
        if votes['scale_up'] > len(self.scaling_policies) / 2:
            self.last_scaling_time = time.time()
            return "scale_up"
        elif votes['scale_down'] > len(self.scaling_policies) / 2:
            self.last_scaling_time = time.time()
            return "scale_down"
            
        return "no_change"
```

---

## Level 3: Deep Dive

### Advanced Auto-scaling Patterns

#### Predictive Auto-scaling

```python
class PredictiveAutoScaler:
    """ML-based predictive scaling"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.training_data = []

    def extract_features(self, timestamp: datetime) -> list:
        """Time-based features for prediction"""
        return [
            timestamp.hour,
            timestamp.weekday(),
            int(timestamp.weekday() in [5, 6]),  # Weekend
            int(9 <= timestamp.hour < 17)  # Business hours
        ]

    def train_model(self):
        if len(self.training_data) < 100:
            return
            
        X = np.array([x[0] for x in self.training_data])
        y = np.array([x[1] for x in self.training_data])
        self.model.fit(X, y)

    def predict_and_scale(self, lead_time_minutes=5) -> dict:
        """Predict future load and recommend scaling"""
        future_time = datetime.now() + timedelta(minutes=lead_time_minutes)
        features = self.extract_features(future_time)
        predicted_load = self.model.predict([features])[0]
        
        current_capacity = self.get_current_capacity()
        required_capacity = predicted_load * 1.2  # 20% buffer
        
        if required_capacity > current_capacity * 1.1:
            return {'action': 'scale_up', 'predicted_load': predicted_load}
        elif required_capacity < current_capacity * 0.7:
            return {'action': 'scale_down', 'predicted_load': predicted_load}
            
        return {'action': 'no_change', 'predicted_load': predicted_load}
```

#### Multi-Dimensional Auto-scaling

```python
def calculate_scaling_score(metrics: dict) -> float:
    """Weighted scoring across multiple dimensions"""
    dimensions = {
        'cpu': {'weight': 0.4, 'target': 70, 'threshold': 10},
        'memory': {'weight': 0.3, 'target': 80, 'threshold': 10},
        'network': {'weight': 0.2, 'target': 60, 'threshold': 15},
        'disk_io': {'weight': 0.1, 'target': 50, 'threshold': 20}
    }
    
    total_score = 0
    for dim, config in dimensions.items():
        if dim in metrics:
            value = metrics[dim]
            deviation = (value - config['target']) / config['threshold']
            score = max(-1, min(1, deviation))  # Clamp to [-1, 1]
            total_score += score * config['weight']
    
    return total_score

def multi_dimensional_scaling(metrics: dict) -> dict:
    score = calculate_scaling_score(metrics)
    
    if score > 0.3:
        return {'action': 'scale_up', 'instances': int(score * 5) + 1}
    elif score < -0.3:
        return {'action': 'scale_down', 'instances': int(abs(score) * 3) + 1}
    
    return {'action': 'no_change', 'score': score}
```

---

## Level 4: Expert

### Production Auto-scaling Systems

#### Netflix's Scryer: Predictive Auto-scaling

```python
def scryer_predict(historical_data: np.array) -> dict:
    """Netflix's ensemble prediction approach"""
    predictors = {
        'fft': FFTPredictor(),       # Frequency analysis
        'linear': LinearPredictor(), # Trend analysis  
        'neural': NeuralPredictor()  # Deep learning
    }
    
    predictions = {}
    for name, predictor in predictors.items():
        predictions[name] = predictor.predict(historical_data, horizon=3600)
    
# Ensemble average
    ensemble_pred = np.mean(list(predictions.values()), axis=0)
    
    return {
        'predicted_load': ensemble_pred,
        'confidence': calculate_confidence(predictions),
        'scale_at': find_scale_points(ensemble_pred)
    }
```
#### Kubernetes HPA Algorithm

```python
def hpa_calculate_replicas(current: int, metrics: list) -> int:
    """K8s HPA scaling algorithm"""
    desired_replicas = []
    
    for metric in metrics:
        current_value = get_metric_value(metric['type'])
        ratio = current_value / metric['target_value']
        desired = int(np.ceil(current * ratio))
        desired_replicas.append(desired)
    
# Take max to satisfy all metrics
    desired = max(desired_replicas)
    
# Apply bounds and scale-down limit
    desired = max(min_replicas, min(max_replicas, desired))
    if desired < current:
        desired = max(desired, current - current // 2)  # Max 50% scale-down
    
    return desired
```
### Real-World Case Study: AWS Auto Scaling

```python
def aws_scaling_policy(policy_type: str, **config) -> dict:
    """AWS ASG policy types"""
    if policy_type == 'target_tracking':
        return {
            'type': 'TargetTrackingScaling',
            'targetValue': config['target_value'],
            'predefinedMetricType': config['metric']
        }
    elif policy_type == 'step_scaling':
        return {
            'type': 'StepScaling',
            'steps': config['steps'],
            'adjustmentType': config.get('adjustment_type', 'ChangeInCapacity')
        }
    elif policy_type == 'predictive':
        return {
            'type': 'PredictiveScaling',
            'mode': config.get('mode', 'ForecastAndScale'),
            'bufferTime': config.get('buffer', 600)
        }

def combine_scaling_decisions(policies: list) -> dict:
    """AWS takes most aggressive scaling action"""
    scale_out = [p for p in policies if p['action'] == 'scale_out']
    scale_in = [p for p in policies if p['action'] == 'scale_in']
    
    if scale_out:
        return max(scale_out, key=lambda x: x['adjustment'])
    elif scale_in:
        return min(scale_in, key=lambda x: abs(x['adjustment']))
    
    return {'action': 'none'}
```
---

## Level 5: Mastery

### Theoretical Optimal Auto-scaling

```python
def optimal_control_scaling(predicted_load: np.array, constraints: dict) -> np.array:
    """Model Predictive Control for auto-scaling"""
    n_steps = len(predicted_load)
    
# Decision variables
    instances = cp.Variable(n_steps, integer=True)
    
# Objective: minimize cost + SLA penalties
    cost = 0
    for t in range(n_steps):
        instance_cost = constraints['instance_cost'] * instances[t]
        
# Simple response time model
        response_time = predicted_load[t] / (instances[t] * constraints['capacity_per_instance'])
        sla_violation = cp.maximum(0, response_time - constraints['sla_target'])
        
        cost += instance_cost + constraints['sla_penalty'] * sla_violation
    
# Constraints
    constraints_list = [
        instances >= constraints['min_instances'],
        instances <= constraints['max_instances'],
    ]
    
# Rate limiting
    for t in range(1, n_steps):
        constraints_list.append(
            cp.abs(instances[t] - instances[t-1]) <= constraints['max_change']
        )
    
# Solve
    problem = cp.Problem(cp.Minimize(cost), constraints_list)
    problem.solve()
    
    return instances.value
```

### Future Directions

- **Serverless Auto-scaling**: Instant 0-to-N scaling
- **Cross-Region Scaling**: Global capacity management
- **Carbon-Aware**: Scale based on renewable energy
- **ML-Driven**: Self-tuning scaling parameters

---

## Quick Reference

| Workload Type | Strategy | Key Metrics |
|---------------|----------|-------------|
| Web API | Target tracking | CPU, request rate |
| Batch processing | Scheduled | Queue depth, time |
| Real-time | Predictive | Historical patterns |
| Bursty | Step scaling | Rapid response |
| Cost-sensitive | Spot + on-demand | Price, availability |


### Implementation Checklist

- [ ] Define metrics and thresholds
- [ ] Set min/max limits (e.g., 2-100 instances)
- [ ] Configure cooldown (300s typical)
- [ ] Implement health checks
- [ ] Test scaling scenarios
- [ ] Monitor scaling events
- [ ] Set cost alerts

---

---

*"The best scaling is the scaling you don't notice."*

---

**Next**: [Bulkhead Pattern →](bulkhead.md)
---