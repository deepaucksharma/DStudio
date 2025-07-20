---
title: Auto-scaling Pattern
description: Pattern for distributed systems coordination and reliability
type: pattern
difficulty: beginner
reading_time: 25 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Auto-scaling Pattern**

# Auto-scaling Pattern

**Dynamic resource allocation based on demand**

> *"The best infrastructure is invisible—it grows when needed, shrinks when not."*

---

## 🎯 Level 1: Intuition

### The Restaurant Staff Analogy

Auto-scaling is like restaurant staffing:
- **Lunch rush**: More servers appear
- **Quiet afternoon**: Some servers go home
- **Unexpected party**: Call in extra staff
- **Closing time**: Minimum crew remains

### Basic Auto-scaling

```python
import time
from typing import List
from dataclasses import dataclass

@dataclass
class Instance:
    id: str
    cpu_usage: float
    memory_usage: float
    request_count: int

class SimpleAutoScaler:
    def __init__(self,
                 min_instances: int = 2,
                 max_instances: int = 10,
                 target_cpu: float = 70.0):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu = target_cpu
        self.instances: List[Instance] = []

        # Start with minimum
        for i in range(min_instances):
            self.instances.append(Instance(f"instance-{i}", 0, 0, 0))

    def check_scaling_needed(self) -> str:
        """Determine if scaling is needed"""
        avg_cpu = sum(i.cpu_usage for i in self.instances) / len(self.instances)

        if avg_cpu > self.target_cpu + 10:  # 80%
            return "scale_up"
        elif avg_cpu < self.target_cpu - 20:  # 50%
            return "scale_down"
        else:
            return "no_change"

    def scale_up(self):
        """Add instance if under max"""
        if len(self.instances) < self.max_instances:
            new_id = f"instance-{len(self.instances)}"
            self.instances.append(Instance(new_id, 0, 0, 0))
            print(f"Scaled up to {len(self.instances)} instances")

    def scale_down(self):
        """Remove instance if above min"""
        if len(self.instances) > self.min_instances:
            self.instances.pop()
            print(f"Scaled down to {len(self.instances)} instances")
```

---

## 🏗️ Level 2: Foundation

### Auto-scaling Strategies

| Strategy | Trigger | Use Case | Response Time |
|----------|---------|----------|---------------|
| **Reactive** | Current metrics | Predictable load | Minutes |
| **Proactive** | Predicted metrics | Known patterns | Preemptive |
| **Scheduled** | Time-based | Business hours | Exact timing |
| **Event-driven** | External events | Marketing campaigns | Immediate |

### Implementing Metric-Based Auto-scaling

```python
from enum import Enum
from collections import deque
import statistics

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    CUSTOM = "custom"

class MetricBasedAutoScaler:
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.scaling_policies = []
        self.cooldown_period = 300  # 5 minutes
        self.last_scaling_time = 0

    def add_scaling_policy(self,
                          metric: MetricType,
                          scale_up_threshold: float,
                          scale_down_threshold: float,
                          statistic: str = "average",
                          period_seconds: int = 300):
        """Add a scaling policy"""
        self.scaling_policies.append({
            'metric': metric,
            'scale_up': scale_up_threshold,
            'scale_down': scale_down_threshold,
            'statistic': statistic,
            'period': period_seconds
        })

    def record_metric(self, metric: MetricType, value: float):
        """Record a metric value"""
        self.metrics_history[metric].append({
            'value': value,
            'timestamp': time.time()
        })

    def evaluate_scaling_decision(self) -> str:
        """Evaluate all policies and decide on scaling"""
        # Check cooldown
        if time.time() - self.last_scaling_time < self.cooldown_period:
            return "cooldown"

        scale_up_votes = 0
        scale_down_votes = 0

        for policy in self.scaling_policies:
            decision = self._evaluate_policy(policy)
            if decision == "scale_up":
                scale_up_votes += 1
            elif decision == "scale_down":
                scale_down_votes += 1

        # Require majority vote
        if scale_up_votes > len(self.scaling_policies) / 2:
            self.last_scaling_time = time.time()
            return "scale_up"
        elif scale_down_votes > len(self.scaling_policies) / 2:
            self.last_scaling_time = time.time()
            return "scale_down"

        return "no_change"

    def _evaluate_policy(self, policy: dict) -> str:
        """Evaluate a single policy"""
        metric_data = self.metrics_history[policy['metric']]

        # Filter to period
        cutoff = time.time() - policy['period']
        recent_values = [
            m['value'] for m in metric_data
            if m['timestamp'] > cutoff
        ]

        if not recent_values:
            return "no_change"

        # Calculate statistic
        if policy['statistic'] == 'average':
            value = statistics.mean(recent_values)
        elif policy['statistic'] == 'max':
            value = max(recent_values)
        elif policy['statistic'] == 'min':
            value = min(recent_values)
        else:
            value = statistics.mean(recent_values)

        # Compare to thresholds
        if value > policy['scale_up']:
            return "scale_up"
        elif value < policy['scale_down']:
            return "scale_down"

        return "no_change"
```

---

## 🔧 Level 3: Deep Dive

### Advanced Auto-scaling Patterns

#### Predictive Auto-scaling
```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class PredictiveAutoScaler:
    """Use ML to predict future load and scale proactively"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.training_data = []
        self.is_trained = False

    def record_load(self, timestamp: datetime, load: float):
        """Record historical load data"""
        features = self._extract_features(timestamp)
        self.training_data.append((features, load))

        # Retrain periodically
        if len(self.training_data) > 1000 and len(self.training_data) % 100 == 0:
            self._train_model()

    def _extract_features(self, timestamp: datetime) -> List[float]:
        """Extract time-based features"""
        return [
            timestamp.hour,
            timestamp.weekday(),
            timestamp.day,
            timestamp.month,
            int(timestamp.weekday() in [5, 6]),  # Weekend
            int(timestamp.hour in range(9, 17)),  # Business hours
        ]

    def _train_model(self):
        """Train the prediction model"""
        if len(self.training_data) < 100:
            return

        X = np.array([x[0] for x in self.training_data])
        y = np.array([x[1] for x in self.training_data])

        self.model.fit(X, y)
        self.is_trained = True

    def predict_load(self, future_time: datetime) -> float:
        """Predict load at future time"""
        if not self.is_trained:
            return 0.0

        features = self._extract_features(future_time)
        return self.model.predict([features])[0]

    def get_scaling_recommendation(self,
                                  lead_time_minutes: int = 5) -> dict:
        """Get scaling recommendation based on prediction"""
        future_time = datetime.now() + timedelta(minutes=lead_time_minutes)
        predicted_load = self.predict_load(future_time)
        current_capacity = self.get_current_capacity()

        # Calculate required capacity (with buffer)
        required_capacity = predicted_load * 1.2  # 20% buffer

        if required_capacity > current_capacity * 1.1:
            scale_factor = required_capacity / current_capacity
            return {
                'action': 'scale_up',
                'factor': scale_factor,
                'predicted_load': predicted_load,
                'confidence': self.model.score(X, y) if hasattr(self, 'X') else 0.5
            }
        elif required_capacity < current_capacity * 0.7:
            scale_factor = required_capacity / current_capacity
            return {
                'action': 'scale_down',
                'factor': scale_factor,
                'predicted_load': predicted_load,
                'confidence': self.model.score(X, y) if hasattr(self, 'X') else 0.5
            }

        return {'action': 'no_change', 'predicted_load': predicted_load}
```

#### Multi-Dimensional Auto-scaling
```python
class MultiDimensionalAutoScaler:
    """Scale based on multiple resource dimensions"""

    def __init__(self):
        self.dimensions = {
            'cpu': {'weight': 0.4, 'target': 70, 'threshold': 10},
            'memory': {'weight': 0.3, 'target': 80, 'threshold': 10},
            'network': {'weight': 0.2, 'target': 60, 'threshold': 15},
            'disk_io': {'weight': 0.1, 'target': 50, 'threshold': 20}
        }

    def calculate_scaling_score(self, metrics: dict) -> float:
        """Calculate weighted scaling score"""
        total_score = 0
        total_weight = 0

        for dimension, config in self.dimensions.items():
            if dimension in metrics:
                value = metrics[dimension]
                target = config['target']
                threshold = config['threshold']
                weight = config['weight']

                # Calculate dimension score (-1 to 1)
                if value > target + threshold:
                    # Need to scale up
                    score = (value - target) / threshold
                    score = min(score, 1.0)
                elif value < target - threshold:
                    # Can scale down
                    score = (value - target) / threshold
                    score = max(score, -1.0)
                else:
                    # Within target range
                    score = 0

                total_score += score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    def get_scaling_decision(self, metrics: dict) -> dict:
        """Make scaling decision based on all dimensions"""
        score = self.calculate_scaling_score(metrics)

        if score > 0.3:
            # Scale up
            instances_to_add = int(score * 5) + 1  # 1-5 instances
            return {
                'action': 'scale_up',
                'instances': instances_to_add,
                'reason': self._get_bottleneck_dimension(metrics)
            }
        elif score < -0.3:
            # Scale down
            instances_to_remove = int(abs(score) * 3) + 1  # 1-3 instances
            return {
                'action': 'scale_down',
                'instances': instances_to_remove,
                'reason': 'All resources under-utilized'
            }

        return {'action': 'no_change', 'score': score}
```

### Auto-scaling Anti-Patterns

---

## 🚀 Level 4: Expert

### Production Auto-scaling Systems

#### Netflix's Scryer: Predictive Auto-scaling
```python
class ScryerAutoScaler:
    """
    Netflix's predictive auto-scaling approach
    """

    def __init__(self):
        self.predictors = {
            'fft': FFTPredictor(),          # Frequency analysis
            'linear': LinearPredictor(),     # Trend analysis
            'neural': NeuralPredictor(),     # Deep learning
            'ensemble': EnsemblePredictor()  # Combination
        }
        self.prediction_horizon = 3600  # 1 hour

    def predict_capacity_needs(self,
                              historical_data: np.array,
                              metadata: dict) -> dict:
        """Predict future capacity requirements"""
        predictions = {}

        # Run all predictors
        for name, predictor in self.predictors.items():
            try:
                pred = predictor.predict(
                    historical_data,
                    self.prediction_horizon,
                    metadata
                )
                predictions[name] = pred
            except Exception as e:
                print(f"Predictor {name} failed: {e}")

        # Ensemble prediction
        if predictions:
            ensemble_pred = self._ensemble_predictions(predictions)

            # Add confidence intervals
            return {
                'predicted_load': ensemble_pred,
                'confidence_interval': self._calculate_confidence(predictions),
                'recommendations': self._generate_recommendations(ensemble_pred)
            }

        return {'error': 'All predictors failed'}

    def _generate_recommendations(self, predicted_load: np.array) -> List[dict]:
        """Generate scaling recommendations from predictions"""
        recommendations = []
        current_capacity = self.get_current_capacity()

        for i, load in enumerate(predicted_load):
            time_offset = i * 60  # Minutes
            required_capacity = load * 1.15  # 15% buffer

            if required_capacity > current_capacity:
                recommendations.append({
                    'time': time_offset,
                    'action': 'scale_up',
                    'target_capacity': required_capacity,
                    'reason': f'Predicted load spike to {load:.0f}'
                })
            elif required_capacity < current_capacity * 0.7:
                recommendations.append({
                    'time': time_offset,
                    'action': 'scale_down',
                    'target_capacity': required_capacity,
                    'reason': f'Predicted load drop to {load:.0f}'
                })

        return self._optimize_recommendations(recommendations)
```bash
#### Kubernetes Horizontal Pod Autoscaler
```python
class HorizontalPodAutoscaler:
    """
    Kubernetes HPA implementation
    """

    def __init__(self,
                 min_replicas: int = 1,
                 max_replicas: int = 10):
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.metrics = []
        self.current_replicas = min_replicas

    def add_metric(self,
                   metric_type: str,
                   target_value: float,
                   target_type: str = "average"):
        """Add scaling metric"""
        self.metrics.append({
            'type': metric_type,
            'target_value': target_value,
            'target_type': target_type
        })

    def calculate_desired_replicas(self) -> int:
        """Calculate desired number of replicas"""
        if not self.metrics:
            return self.current_replicas

        desired_replicas_list = []

        for metric in self.metrics:
            current_value = self.get_metric_value(metric['type'])

            if metric['target_type'] == 'average':
                # Standard HPA algorithm
                ratio = current_value / metric['target_value']
                desired = int(np.ceil(self.current_replicas * ratio))
            else:
                # Custom scaling logic
                desired = self.custom_scaling_logic(metric, current_value)

            desired_replicas_list.append(desired)

        # Take maximum to ensure all metrics are satisfied
        desired = max(desired_replicas_list)

        # Apply bounds
        desired = max(self.min_replicas, min(self.max_replicas, desired))

        # Apply scale-down restrictions
        if desired < self.current_replicas:
            # Don't scale down by more than 50% at once
            max_scale_down = max(1, self.current_replicas // 2)
            desired = max(desired, self.current_replicas - max_scale_down)

        return desired

    def should_scale(self) -> bool:
        """Determine if scaling is needed"""
        desired = self.calculate_desired_replicas()

        # Add tolerance to prevent flapping
        tolerance = 0.1
        ratio = desired / self.current_replicas

        return ratio > (1 + tolerance) or ratio < (1 - tolerance)
```bash
### Real-World Case Study: AWS Auto Scaling

```python
class AWSAutoScalingGroup:
    """
    AWS Auto Scaling Group implementation patterns
    """

    def __init__(self, config: dict):
        self.config = config
        self.instances = []
        self.scaling_policies = []
        self.lifecycle_hooks = []

    def add_scaling_policy(self, policy_type: str, **kwargs):
        """Add various types of scaling policies"""
        if policy_type == 'target_tracking':
            policy = TargetTrackingPolicy(
                metric=kwargs['metric'],
                target_value=kwargs['target_value'],
                scale_out_cooldown=kwargs.get('scale_out_cooldown', 300),
                scale_in_cooldown=kwargs.get('scale_in_cooldown', 300)
            )
        elif policy_type == 'step_scaling':
            policy = StepScalingPolicy(
                metric=kwargs['metric'],
                steps=kwargs['steps'],
                adjustment_type=kwargs.get('adjustment_type', 'ChangeInCapacity')
            )
        elif policy_type == 'predictive':
            policy = PredictiveScalingPolicy(
                metric=kwargs['metric'],
                mode=kwargs.get('mode', 'ForecastAndScale'),
                scheduling_buffer_time=kwargs.get('buffer', 600)
            )

        self.scaling_policies.append(policy)

    def handle_instance_launch(self, instance_id: str):
        """Handle new instance launch with lifecycle hooks"""
        # Run lifecycle hooks
        for hook in self.lifecycle_hooks:
            if hook['transition'] == 'autoscaling:EC2_INSTANCE_LAUNCHING':
                # Wait for hook completion
                self.wait_for_lifecycle_action(instance_id, hook)

        # Warm up instance
        self.warm_up_instance(instance_id)

        # Register with load balancer
        self.register_with_load_balancer(instance_id)

    def calculate_scaling_adjustment(self) -> dict:
        """Calculate scaling adjustment from all policies"""
        adjustments = []

        for policy in self.scaling_policies:
            adj = policy.evaluate()
            if adj:
                adjustments.append(adj)

        if not adjustments:
            return {'action': 'none'}

        # Combine adjustments (AWS takes most aggressive)
        if any(a['action'] == 'scale_out' for a in adjustments):
            # Find largest scale-out
            scale_out_adjs = [a for a in adjustments if a['action'] == 'scale_out']
            return max(scale_out_adjs, key=lambda x: x['adjustment'])
        else:
            # Find smallest scale-in
            scale_in_adjs = [a for a in adjustments if a['action'] == 'scale_in']
            return min(scale_in_adjs, key=lambda x: abs(x['adjustment']))
```yaml
---

## 🎯 Level 5: Mastery

### Theoretical Optimal Auto-scaling

```python
import cvxpy as cp
from scipy.optimize import minimize

class OptimalAutoScaler:
    """
    Optimal auto-scaling using control theory
    """

    def __init__(self):
        self.state_space_model = None
        self.mpc_horizon = 10  # Model Predictive Control horizon

    def learn_system_dynamics(self,
                            historical_data: np.array,
                            instance_counts: np.array,
                            response_times: np.array):
        """Learn system dynamics using system identification"""
        # State: [load, instances, response_time]
        # Input: [instance_change]
        # Output: [response_time]

        # Fit ARMAX model
        self.state_space_model = self.fit_armax_model(
            historical_data,
            instance_counts,
            response_times
        )

    def optimal_control_scaling(self,
                              current_state: np.array,
                              predicted_load: np.array,
                              constraints: dict) -> np.array:
        """
        Solve optimal control problem for scaling
        """
        n_steps = len(predicted_load)

        # Decision variables
        instances = cp.Variable(n_steps, integer=True)

        # Objective: minimize cost + performance penalty
        cost = 0
        for t in range(n_steps):
            # Instance cost
            instance_cost = constraints['instance_cost'] * instances[t]

            # Performance penalty (using learned model)
            expected_response_time = self.predict_response_time(
                predicted_load[t],
                instances[t]
            )

            sla_violation = cp.maximum(
                0,
                expected_response_time - constraints['sla_response_time']
            )

            performance_penalty = constraints['sla_penalty'] * sla_violation

            cost += instance_cost + performance_penalty

        # Constraints
        constraints_list = [
            instances >= constraints['min_instances'],
            instances <= constraints['max_instances']
        ]

        # Rate of change constraints
        for t in range(1, n_steps):
            constraints_list.append(
                cp.abs(instances[t] - instances[t-1]) <= constraints['max_change_rate']
            )

        # Solve optimization problem
        problem = cp.Problem(cp.Minimize(cost), constraints_list)
        problem.solve()

        return instances.value

    def reinforcement_learning_scaler(self):
        """
        Use RL for auto-scaling decisions
        """
        # State: (current_load, current_instances, time_of_day, day_of_week)
        # Action: scale_up, scale_down, no_change
        # Reward: -cost - sla_violations

        class AutoScalingEnvironment:
            def __init__(self):
                self.state = None
                self.instance_cost = 0.1
                self.sla_penalty = 10.0

            def step(self, action):
                # Apply action
                if action == 0:  # scale_up
                    self.state['instances'] += 1
                elif action == 1:  # scale_down
                    self.state['instances'] -= 1
                # action == 2: no change

                # Calculate reward
                cost = self.state['instances'] * self.instance_cost

                # Simulate response time based on load and instances
                response_time = self.simulate_response_time(
                    self.state['load'],
                    self.state['instances']
                )

                sla_violation = max(0, response_time - 100)  # 100ms SLA
                penalty = sla_violation * self.sla_penalty

                reward = -(cost + penalty)

                # Update state with new load
                self.state['load'] = self.get_next_load()

                return self.state, reward, False, {}

        # Train DQN agent
        env = AutoScalingEnvironment()
        agent = DQNAgent(state_size=4, action_size=3)

        # Training loop
        for episode in range(1000):
            state = env.reset()
            total_reward = 0

            for step in range(100):
                action = agent.act(state)
                next_state, reward, done, _ = env.step(action)
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

                if done:
                    break

            agent.replay()

        return agent
```

### Future Directions

1. **Serverless Auto-scaling**: Instant scaling to zero and back
2. **Cross-Region Auto-scaling**: Global capacity management
3. **Carbon-Aware Scaling**: Scale based on renewable energy availability
4. **Quantum-Inspired Scaling**: Superposition of scaling states

---

## 📋 Quick Reference

### Auto-scaling Strategy Selection

| Workload Type | Strategy | Key Metrics |
|---------------|----------|-------------|
| Web API | Target tracking | CPU, request rate |
| Batch processing | Scheduled | Queue depth, time |
| Real-time | Predictive | Historical patterns |
| Bursty | Step scaling | Rapid response |
| Cost-sensitive | Spot + on-demand | Price, availability |

### Implementation Checklist

- [ ] Define scaling metrics and thresholds
- [ ] Set min/max instance limits
- [ ] Configure cooldown periods
- [ ] Implement health checks
- [ ] Test scale-up scenarios
- [ ] Test scale-down scenarios
- [ ] Monitor scaling events
- [ ] Set up cost alerts

---

---

*"The best scaling is the scaling you don't notice."*

---

**Next**: [Bulkhead Pattern →](bulkhead.md)
---
