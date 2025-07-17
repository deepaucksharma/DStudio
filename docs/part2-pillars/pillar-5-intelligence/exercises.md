# Intelligence Distribution Exercises

!!! info "Prerequisites"
    - Completed [Intelligence Concepts](index.md)
    - Reviewed [Intelligence Examples](examples.md)
    - Basic understanding of ML concepts

!!! tip "Quick Navigation"
    [← Examples](examples.md) |
    [↑ Pillars Overview](../index.md) |
    [Part 3 →](../../part3-patterns/index.md)

## Learning Objectives

By completing these exercises, you will:

1. **Build** anomaly detection systems
2. **Implement** predictive scaling
3. **Create** adaptive routing algorithms
4. **Design** feedback control systems
5. **Develop** ML-driven optimizations

---

## Exercise 1: Anomaly Detection System

Build a statistical anomaly detection system for API latencies.

### Requirements

1. Detect latency anomalies in real-time
2. Adapt to changing baselines
3. Minimize false positives
4. Provide explainable alerts

### Implementation

```python
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

@dataclass
class Anomaly:
    timestamp: float
    value: float
    expected_range: Tuple[float, float]
    severity: float
    explanation: str

class AdaptiveAnomalyDetector:
    def __init__(self, 
                 window_size: int = 100,
                 sensitivity: float = 3.0,
                 adaptation_rate: float = 0.1):
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.adaptation_rate = adaptation_rate
        
        self.values = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        
        # Adaptive statistics
        self.mean = 0
        self.std = 1
        self.trend = 0
        
    def add_value(self, value: float, timestamp: Optional[float] = None) -> Optional[Anomaly]:
        """Add new value and check for anomalies"""
        if timestamp is None:
            timestamp = time.time()
            
        self.values.append(value)
        self.timestamps.append(timestamp)
        
        if len(self.values) < 10:  # Need minimum data
            return None
            
        # Update statistics
        self._update_statistics()
        
        # Check for anomaly
        return self._check_anomaly(value, timestamp)
        
    def _update_statistics(self):
        """Update adaptive statistics"""
        if len(self.values) < 2:
            return
            
        # Calculate current statistics
        current_mean = np.mean(self.values)
        current_std = np.std(self.values)
        
        # Adaptive update
        self.mean = (1 - self.adaptation_rate) * self.mean + self.adaptation_rate * current_mean
        self.std = (1 - self.adaptation_rate) * self.std + self.adaptation_rate * current_std
        
        # Calculate trend
        if len(self.values) >= 10:
            recent = list(self.values)[-10:]
            older = list(self.values)[-20:-10] if len(self.values) >= 20 else list(self.values)[:10]
            self.trend = np.mean(recent) - np.mean(older)
            
    def _check_anomaly(self, value: float, timestamp: float) -> Optional[Anomaly]:
        """Check if value is anomalous"""
        # Z-score calculation
        z_score = abs((value - self.mean) / max(self.std, 0.001))
        
        if z_score > self.sensitivity:
            # Calculate expected range
            expected_min = self.mean - self.sensitivity * self.std
            expected_max = self.mean + self.sensitivity * self.std
            
            # Severity based on deviation
            severity = min(1.0, (z_score - self.sensitivity) / self.sensitivity)
            
            # Generate explanation
            explanation = self._generate_explanation(value, z_score)
            
            return Anomaly(
                timestamp=timestamp,
                value=value,
                expected_range=(expected_min, expected_max),
                severity=severity,
                explanation=explanation
            )
            
        return None
        
    def _generate_explanation(self, value: float, z_score: float) -> str:
        """Generate human-readable explanation"""
        deviation = value - self.mean
        direction = "above" if deviation > 0 else "below"
        
        explanation = f"Value {value:.2f} is {abs(deviation):.2f} {direction} "
        explanation += f"the expected mean of {self.mean:.2f} "
        explanation += f"({z_score:.1f} standard deviations)"
        
        if abs(self.trend) > self.std * 0.1:
            trend_dir = "increasing" if self.trend > 0 else "decreasing"
            explanation += f". Note: Values have been {trend_dir} recently"
            
        return explanation

# Advanced: Multi-dimensional anomaly detection
class MultiDimensionalAnomalyDetector:
    def __init__(self, dimensions: List[str], correlation_threshold: float = 0.8):
        self.dimensions = dimensions
        self.correlation_threshold = correlation_threshold
        self.detectors = {dim: AdaptiveAnomalyDetector() for dim in dimensions}
        self.correlation_matrix = np.eye(len(dimensions))
        
    def add_values(self, values: dict) -> List[Anomaly]:
        """Add multi-dimensional values and detect anomalies"""
        anomalies = []
        
        # Check each dimension
        for dim, value in values.items():
            if dim in self.detectors:
                anomaly = self.detectors[dim].add_value(value)
                if anomaly:
                    anomalies.append(anomaly)
                    
        # Check for correlation anomalies
        if len(anomalies) > 1:
            corr_anomaly = self._check_correlation_anomaly(values)
            if corr_anomaly:
                anomalies.append(corr_anomaly)
                
        return anomalies
        
    def _check_correlation_anomaly(self, values: dict) -> Optional[Anomaly]:
        """Check if correlations between dimensions are anomalous"""
        # Implementation of correlation analysis
        pass

# Usage example
detector = AdaptiveAnomalyDetector(sensitivity=2.5)

# Simulate API latencies
for i in range(200):
    # Normal latency with some variation
    latency = 100 + np.random.normal(0, 10)
    
    # Inject anomalies
    if i == 50:
        latency = 200  # Spike
    elif i == 100:
        latency = 20   # Drop
        
    anomaly = detector.add_value(latency)
    if anomaly:
        print(f"Anomaly detected: {anomaly.explanation}")
```

### Extension Challenges

1. Add seasonal pattern detection
2. Implement multivariate anomaly detection
3. Add predictive anomaly warnings
4. Create automated remediation triggers

---

## Exercise 2: Predictive Auto-scaling

Build a system that predicts future load and scales preemptively.

### Requirements

1. Learn from historical patterns
2. Predict load 10-30 minutes ahead
3. Account for special events
4. Minimize over/under provisioning

### Implementation

```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class PredictiveAutoScaler:
    def __init__(self, 
                 prediction_horizon: int = 30,  # minutes
                 scale_threshold: float = 0.8):
        self.prediction_horizon = prediction_horizon
        self.scale_threshold = scale_threshold
        
        self.model = RandomForestRegressor(n_estimators=100)
        self.history = []
        self.is_trained = False
        
    def add_observation(self, timestamp: float, metrics: dict):
        """Add new observation to history"""
        observation = {
            'timestamp': timestamp,
            'cpu': metrics.get('cpu', 0),
            'memory': metrics.get('memory', 0),
            'requests_per_sec': metrics.get('rps', 0),
            'response_time': metrics.get('response_time', 0),
            # Derived features
            'hour': pd.Timestamp(timestamp, unit='s').hour,
            'day_of_week': pd.Timestamp(timestamp, unit='s').dayofweek,
            'minute_of_day': pd.Timestamp(timestamp, unit='s').hour * 60 + 
                            pd.Timestamp(timestamp, unit='s').minute
        }
        
        self.history.append(observation)
        
        # Retrain periodically
        if len(self.history) > 1000 and len(self.history) % 100 == 0:
            self._train_model()
            
    def predict_load(self, current_metrics: dict) -> dict:
        """Predict future load"""
        if not self.is_trained:
            return self._reactive_prediction(current_metrics)
            
        # Prepare features
        features = self._prepare_features(current_metrics)
        
        # Predict multiple horizons
        predictions = {}
        for minutes_ahead in [10, 20, 30]:
            future_features = self._adjust_features_for_future(features, minutes_ahead)
            pred = self.model.predict([future_features])[0]
            predictions[f'{minutes_ahead}min'] = {
                'cpu': pred,
                'confidence': self._calculate_confidence(features, minutes_ahead)
            }
            
        return predictions
        
    def get_scaling_decision(self, predictions: dict, current_capacity: int) -> dict:
        """Decide on scaling action based on predictions"""
        max_predicted_load = max(p['cpu'] for p in predictions.values())
        confidence = np.mean([p['confidence'] for p in predictions.values()])
        
        # Calculate required capacity
        required_capacity = int(np.ceil(max_predicted_load / self.scale_threshold))
        
        # Add safety margin based on confidence
        safety_margin = 1.0 + (1.0 - confidence) * 0.2
        required_capacity = int(required_capacity * safety_margin)
        
        decision = {
            'action': 'none',
            'target_capacity': current_capacity,
            'reason': 'Load within normal range'
        }
        
        if required_capacity > current_capacity:
            decision = {
                'action': 'scale_up',
                'target_capacity': required_capacity,
                'reason': f'Predicted load {max_predicted_load:.1f}% in next 30min'
            }
        elif required_capacity < current_capacity * 0.6:
            decision = {
                'action': 'scale_down',
                'target_capacity': required_capacity,
                'reason': 'Predicted low load allows capacity reduction'
            }
            
        return decision
        
    def _train_model(self):
        """Train the prediction model"""
        if len(self.history) < 100:
            return
            
        # Prepare training data
        df = pd.DataFrame(self.history)
        
        # Create target variable (CPU usage X minutes in future)
        target_col = f'cpu_plus_{self.prediction_horizon}min'
        df[target_col] = df['cpu'].shift(-self.prediction_horizon)
        
        # Remove incomplete rows
        df = df.dropna()
        
        # Select features
        feature_cols = ['cpu', 'memory', 'requests_per_sec', 'response_time',
                       'hour', 'day_of_week', 'minute_of_day']
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        
    def _calculate_confidence(self, features: list, horizon: int) -> float:
        """Calculate prediction confidence"""
        # Simple confidence based on horizon and data availability
        base_confidence = 0.9
        horizon_penalty = horizon * 0.01
        data_bonus = min(0.1, len(self.history) / 10000)
        
        return max(0.5, base_confidence - horizon_penalty + data_bonus)

# Advanced: Event-aware prediction
class EventAwarePredictiveScaler(PredictiveAutoScaler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.known_events = []
        
    def add_known_event(self, timestamp: float, expected_impact: float):
        """Add known future event (e.g., marketing campaign)"""
        self.known_events.append({
            'timestamp': timestamp,
            'impact': expected_impact
        })
        
    def predict_load(self, current_metrics: dict) -> dict:
        predictions = super().predict_load(current_metrics)
        
        # Adjust for known events
        current_time = time.time()
        for event in self.known_events:
            if current_time < event['timestamp'] < current_time + self.prediction_horizon * 60:
                for key in predictions:
                    predictions[key]['cpu'] *= (1 + event['impact'])
                    predictions[key]['confidence'] *= 0.8  # Lower confidence
                    
        return predictions

# Usage
scaler = EventAwarePredictiveScaler(prediction_horizon=30)

# Add historical data
# ... (add observations over time)

# Add known event (e.g., Black Friday sale)
scaler.add_known_event(
    timestamp=black_friday_timestamp,
    expected_impact=2.5  # 250% increase expected
)

# Get scaling decision
current_metrics = {'cpu': 65, 'memory': 70, 'rps': 1000}
predictions = scaler.predict_load(current_metrics)
decision = scaler.get_scaling_decision(predictions, current_capacity=10)
print(f"Scaling decision: {decision}")
```

---

## Exercise 3: Intelligent Request Routing

Build an ML-based request router that learns optimal backend selection.

### Requirements

1. Route based on request characteristics
2. Learn from response times and errors
3. Adapt to backend performance changes
4. Balance load while optimizing latency

### Implementation

```python
class IntelligentRouter:
    def __init__(self, backends: List[str]):
        self.backends = backends
        self.routing_model = self._build_model()
        self.performance_history = defaultdict(list)
        self.feature_extractors = self._build_feature_extractors()
        
    def route(self, request: dict) -> str:
        """Route request to optimal backend"""
        # Extract features
        features = self._extract_features(request)
        
        # Get predictions for each backend
        backend_scores = {}
        for backend in self.backends:
            backend_features = features + self._get_backend_features(backend)
            score = self.routing_model.predict([backend_features])[0]
            backend_scores[backend] = score
            
        # Apply exploration (epsilon-greedy)
        if random.random() < 0.1:  # 10% exploration
            return random.choice(self.backends)
        else:
            return min(backend_scores, key=backend_scores.get)
            
    def record_result(self, request: dict, backend: str, 
                     response_time: float, success: bool):
        """Record routing result for learning"""
        self.performance_history[backend].append({
            'timestamp': time.time(),
            'response_time': response_time,
            'success': success,
            'request_size': len(str(request)),
            'features': self._extract_features(request)
        })
        
        # Retrain periodically
        if sum(len(h) for h in self.performance_history.values()) % 1000 == 0:
            self._retrain_model()
            
    def _extract_features(self, request: dict) -> List[float]:
        """Extract features from request"""
        features = []
        
        # Request size
        features.append(len(str(request)))
        
        # Request type features
        features.append(1.0 if request.get('method') == 'GET' else 0.0)
        features.append(1.0 if request.get('method') == 'POST' else 0.0)
        
        # Path-based features
        path = request.get('path', '')
        features.append(1.0 if '/api/' in path else 0.0)
        features.append(1.0 if '/static/' in path else 0.0)
        
        # Time-based features
        now = pd.Timestamp.now()
        features.append(now.hour)
        features.append(now.dayofweek)
        
        return features
        
    def _get_backend_features(self, backend: str) -> List[float]:
        """Get current backend performance features"""
        history = self.performance_history[backend][-100:]  # Last 100 requests
        
        if not history:
            return [0, 0, 1, 0]  # Default features
            
        recent_response_times = [h['response_time'] for h in history]
        recent_successes = [h['success'] for h in history]
        
        return [
            np.mean(recent_response_times),
            np.percentile(recent_response_times, 95),
            np.mean(recent_successes),
            len(history) / 100.0  # Load indicator
        ]

# Test the intelligent router
router = IntelligentRouter(['backend-1', 'backend-2', 'backend-3'])

# Simulate requests
for i in range(1000):
    request = {
        'method': random.choice(['GET', 'POST']),
        'path': random.choice(['/api/users', '/api/orders', '/static/image.jpg']),
        'size': random.randint(100, 10000)
    }
    
    backend = router.route(request)
    
    # Simulate response (backend-2 is slower for large requests)
    if backend == 'backend-2' and request['size'] > 5000:
        response_time = random.uniform(200, 500)
    else:
        response_time = random.uniform(50, 150)
        
    router.record_result(request, backend, response_time, success=True)
```

---

## Exercise 4: AIOps Incident Prediction

Build a system that predicts incidents before they occur.

### Task

Create an incident prediction system that:
1. Analyzes multiple signals (metrics, logs, events)
2. Identifies patterns preceding incidents
3. Provides early warnings with explanations
4. Learns from false positives/negatives

---

## Exercise 5: Self-Optimizing Cache

Implement a cache that learns access patterns and optimizes itself.

### Requirements

1. Learn access patterns over time
2. Predictively load frequently accessed items
3. Adapt eviction policy based on workload
4. Optimize for hit rate and latency

---

## Summary & Best Practices

After completing these exercises, you should understand:

1. **Anomaly Detection**
   - Statistical baselines
   - Adaptive thresholds
   - Multi-dimensional analysis

2. **Predictive Systems**
   - Time series forecasting
   - Feature engineering
   - Confidence estimation

3. **Learning Systems**
   - Online learning
   - Exploration vs exploitation
   - Feedback loops

4. **Operational ML**
   - Model deployment
   - Monitoring and retraining
   - Fallback mechanisms

5. **Real-world Considerations**
   - Cold start problems
   - Concept drift
   - Explainability

## Next Steps

- Deploy these patterns in test environments
- Measure impact on system metrics
- Iterate based on real-world feedback
- Share learnings with your team

Continue to [Part 3: Patterns →](../../part3-patterns/index.md) to explore architectural patterns built on these foundations.