---
title: Intelligence & Learning Exercises
description: <details>
<summary>Solution</summary>
type: pillar
difficulty: beginner
reading_time: 25 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Intelligence](/part2-pillars/intelligence/) → **Intelligence & Learning Exercises**


# Intelligence & Learning Exercises

## Exercise 1: Build a Learning Load Balancer

**Challenge**: Implement a load balancer that learns from response times and error rates.

```python
class LearningLoadBalancer:
    def __init__(self, backends):
        """
        Initialize load balancer with learning capabilities
        
        Args:
            backends: List of backend server addresses
        """
        self.backends = backends
        self.weights = {}  # backend -> weight
        self.history = {}  # backend -> performance history
        
    def select_backend(self):
        """
        Select backend using learned weights
        
        TODO:
        1. Use epsilon-greedy for exploration
        2. Weight selection by performance
        3. Handle new backends gracefully
        """
        pass
    
    def update_performance(self, backend, latency, success):
        """
        Update backend performance metrics
        
        TODO:
        1. Store performance history
        2. Update weights based on performance
        3. Implement decay for old data
        """
        pass
    
    def predict_latency(self, backend):
        """Predict expected latency for backend"""
        pass
```

<details>
<summary>Solution</summary>

```python
import time
import random
import numpy as np
from collections import deque, defaultdict
from datetime import datetime, timedelta

class LearningLoadBalancer:
    def __init__(self, backends, learning_rate=0.1, exploration_rate=0.1):
        self.backends = backends
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        
        # Initialize weights uniformly
        self.weights = {b: 1.0 / len(backends) for b in backends}
        
        # Performance history
        self.history = defaultdict(lambda: {
            'latencies': deque(maxlen=1000),
            'errors': deque(maxlen=1000),
            'timestamps': deque(maxlen=1000)
        })
        
        # Statistics
        self.total_requests = 0
        self.backend_requests = defaultdict(int)
        
    def select_backend(self):
        """Select backend using epsilon-greedy strategy"""
        self.total_requests += 1
        
        # Exploration: random selection
        if random.random() < self.exploration_rate:
            backend = random.choice(self.backends)
            self.backend_requests[backend] += 1
            return backend
        
        # Exploitation: weighted selection based on performance
        # Calculate selection probabilities
        total_weight = sum(self.weights.values())
        if total_weight == 0:
            # All weights are zero, select randomly
            backend = random.choice(self.backends)
            self.backend_requests[backend] += 1
            return backend
        
        # Normalize weights to probabilities
        probabilities = {b: w / total_weight for b, w in self.weights.items()}
        
        # Select based on probabilities
        r = random.random()
        cumulative = 0
        for backend, prob in probabilities.items():
            cumulative += prob
            if r <= cumulative:
                self.backend_requests[backend] += 1
                return backend
        
        # Fallback
        backend = self.backends[-1]
        self.backend_requests[backend] += 1
        return backend
    
    def update_performance(self, backend, latency, success):
        """Update backend performance and adjust weights"""
        timestamp = time.time()
        
        # Record performance
        history = self.history[backend]
        history['latencies'].append(latency if success else None)
        history['errors'].append(0 if success else 1)
        history['timestamps'].append(timestamp)
        
        # Calculate performance score
        score = self._calculate_performance_score(backend)
        
        # Update weight using exponential moving average
        old_weight = self.weights[backend]
        self.weights[backend] = (
            (1 - self.learning_rate) * old_weight + 
            self.learning_rate * score
        )
        
        # Ensure weights don't go negative
        self.weights[backend] = max(0.001, self.weights[backend])
        
        # Periodically normalize weights
        if self.total_requests % 100 == 0:
            self._normalize_weights()
    
    def _calculate_performance_score(self, backend):
        """Calculate performance score for backend"""
        history = self.history[backend]
        
        if not history['timestamps']:
            return 0.5  # Neutral score for no data
        
        # Consider only recent data (last 5 minutes)
        cutoff_time = time.time() - 300
        recent_indices = [
            i for i, t in enumerate(history['timestamps'])
            if t > cutoff_time
        ]
        
        if not recent_indices:
            return 0.5
        
        # Calculate metrics
        recent_latencies = [
            history['latencies'][i] 
            for i in recent_indices 
            if history['latencies'][i] is not None
        ]
        recent_errors = [history['errors'][i] for i in recent_indices]
        
        # Error rate (0 is best, 1 is worst)
        error_rate = sum(recent_errors) / len(recent_errors) if recent_errors else 0
        
        # Latency score (normalize to 0-1, lower is better)
        if recent_latencies:
            avg_latency = np.mean(recent_latencies)
            p95_latency = np.percentile(recent_latencies, 95)
            
            # Score based on SLA targets
            target_latency = 100  # ms
            latency_score = 1.0 / (1.0 + avg_latency / target_latency)
            
            # Penalize high variance
            latency_variance = np.var(recent_latencies)
            variance_penalty = 1.0 / (1.0 + latency_variance / 1000)
        else:
            latency_score = 0.5
            variance_penalty = 1.0
        
        # Combine scores
        score = (
            0.5 * (1 - error_rate) +  # 50% weight on reliability
            0.3 * latency_score +      # 30% weight on latency
            0.2 * variance_penalty     # 20% weight on consistency
        )
        
        return score
    
    def predict_latency(self, backend):
        """Predict expected latency using simple time series model"""
        history = self.history[backend]
        
        if not history['latencies']:
            return 100  # Default prediction
        
        # Get recent successful requests
        recent_latencies = [
            l for l in history['latencies'][-50:]
            if l is not None
        ]
        
        if not recent_latencies:
            return 100
        
        # Simple prediction: weighted average with recency bias
        weights = np.exp(np.linspace(0, 1, len(recent_latencies)))
        weights /= weights.sum()
        
        predicted = np.average(recent_latencies, weights=weights)
        
        # Add confidence interval
        std_dev = np.std(recent_latencies)
        
        return {
            'mean': predicted,
            'lower_bound': predicted - std_dev,
            'upper_bound': predicted + std_dev,
            'confidence': min(len(recent_latencies) / 50, 1.0)
        }
    
    def _normalize_weights(self):
        """Normalize weights to sum to 1"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {b: w / total for b, w in self.weights.items()}
    
    def get_stats(self):
        """Get load balancer statistics"""
        stats = {
            'total_requests': self.total_requests,
            'backend_stats': {}
        }
        
        for backend in self.backends:
            history = self.history[backend]
            recent_latencies = [
                l for l in history['latencies']
                if l is not None
            ]
            
            stats['backend_stats'][backend] = {
                'requests': self.backend_requests[backend],
                'weight': self.weights[backend],
                'error_rate': sum(history['errors']) / len(history['errors']) if history['errors'] else 0,
                'avg_latency': np.mean(recent_latencies) if recent_latencies else None,
                'p95_latency': np.percentile(recent_latencies, 95) if recent_latencies else None
            }
        
        return stats

# Test the implementation
def simulate_backend(backend_id, base_latency, error_rate, variance):
    """Simulate backend with specific characteristics"""
    if random.random() < error_rate:
        return None, False  # Error
    
    # Simulate latency with some variance
    latency = base_latency + random.gauss(0, variance)
    latency = max(1, latency)  # Minimum 1ms
    
    return latency, True

def test_learning_load_balancer():
    # Create load balancer with 3 backends
    backends = ['backend1', 'backend2', 'backend3']
    lb = LearningLoadBalancer(backends)
    
    # Backend characteristics
    backend_profiles = {
        'backend1': {'base_latency': 50, 'error_rate': 0.01, 'variance': 10},  # Fast, reliable
        'backend2': {'base_latency': 100, 'error_rate': 0.05, 'variance': 30}, # Medium
        'backend3': {'base_latency': 200, 'error_rate': 0.1, 'variance': 50}   # Slow, unreliable
    }
    
    # Simulate requests
    for i in range(1000):
        # Select backend
        backend = lb.select_backend()
        
        # Simulate request
        profile = backend_profiles[backend]
        latency, success = simulate_backend(
            backend,
            profile['base_latency'],
            profile['error_rate'],
            profile['variance']
        )
        
        # Update performance
        if success:
            lb.update_performance(backend, latency, True)
        else:
            lb.update_performance(backend, 0, False)
        
        # Print progress
        if (i + 1) % 100 == 0:
            print(f"\nAfter {i + 1} requests:")
            stats = lb.get_stats()
            for backend, bstats in stats['backend_stats'].items():
                print(f"{backend}: weight={bstats['weight']:.3f}, "
                      f"requests={bstats['requests']}, "
                      f"error_rate={bstats['error_rate']:.3f}, "
                      f"avg_latency={bstats['avg_latency']:.1f if bstats['avg_latency'] else 'N/A'}")
    
    # Test predictions
    print("\nLatency predictions:")
    for backend in backends:
        prediction = lb.predict_latency(backend)
        print(f"{backend}: {prediction['mean']:.1f}ms "
              f"(±{prediction['upper_bound'] - prediction['mean']:.1f}ms, "
              f"confidence={prediction['confidence']:.2f})")

if __name__ == "__main__":
    test_learning_load_balancer()
```

</details>

## Exercise 2: Implement Anomaly Detection

**Challenge**: Build a system that learns normal behavior and detects anomalies.

```python
class AnomalyDetector:
    def __init__(self, window_size=1000):
        """
        Initialize anomaly detector
        
        Args:
            window_size: Size of sliding window for statistics
        """
        self.window_size = window_size
        self.data_points = []
        self.model = None
        
    def add_point(self, timestamp, metrics):
        """
        Add new data point
        
        Args:
            timestamp: Unix timestamp
            metrics: Dict of metric values
            
        TODO:
        1. Maintain sliding window
        2. Update statistical model
        3. Detect seasonality
        """
        pass
    
    def is_anomalous(self, metrics):
        """
        Check if metrics are anomalous
        
        TODO:
        1. Compare against learned baseline
        2. Account for time of day/week
        3. Return anomaly score
        """
        pass
```

<details>
<summary>Solution</summary>

```python
import numpy as np
from collections import deque
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    def __init__(self, window_size=1000, contamination=0.05):
        self.window_size = window_size
        self.contamination = contamination  # Expected anomaly rate
        
        # Sliding window of data points
        self.data_points = deque(maxlen=window_size)
        
        # Models for different time periods
        self.hourly_models = {}  # hour -> model
        self.daily_models = {}   # day_of_week -> model
        
        # Feature statistics
        self.feature_stats = {}
        self.scaler = StandardScaler()
        
        # Anomaly threshold
        self.threshold_percentile = 95
        self.anomaly_scores = deque(maxlen=window_size)
        
    def add_point(self, timestamp, metrics):
        """Add new data point and update models"""
        # Extract time features
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour
        day_of_week = dt.weekday()
        minute = dt.minute
        
        # Create feature vector
        features = self._extract_features(timestamp, metrics)
        
        # Store data point
        self.data_points.append({
            'timestamp': timestamp,
            'metrics': metrics,
            'features': features,
            'hour': hour,
            'day_of_week': day_of_week
        })
        
        # Update models periodically
        if len(self.data_points) % 100 == 0:
            self._update_models()
    
    def is_anomalous(self, metrics, timestamp=None):
        """Check if metrics are anomalous"""
        if timestamp is None:
            timestamp = time.time()
        
        # Extract features
        features = self._extract_features(timestamp, metrics)
        
        # Get anomaly scores from different models
        scores = []
        
        # Global model score
        if hasattr(self, 'global_model'):
            global_score = self._get_anomaly_score(self.global_model, features)
            scores.append(global_score)
        
        # Time-specific model scores
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # Hourly model
        if hour in self.hourly_models:
            hourly_score = self._get_anomaly_score(self.hourly_models[hour], features)
            scores.append(hourly_score)
        
        # Daily model
        if day_of_week in self.daily_models:
            daily_score = self._get_anomaly_score(self.daily_models[day_of_week], features)
            scores.append(daily_score)
        
        # Combine scores
        if not scores:
            return {
                'is_anomaly': False,
                'score': 0,
                'reason': 'Insufficient data'
            }
        
        # Use maximum score (most suspicious)
        anomaly_score = max(scores)
        
        # Determine threshold dynamically
        self.anomaly_scores.append(anomaly_score)
        if len(self.anomaly_scores) > 100:
            threshold = np.percentile(self.anomaly_scores, self.threshold_percentile)
        else:
            threshold = 0.5  # Default threshold
        
        is_anomaly = anomaly_score > threshold
        
        # Find which metrics contributed most to anomaly
        anomalous_metrics = []
        if is_anomaly:
            anomalous_metrics = self._identify_anomalous_metrics(metrics, timestamp)
        
        return {
            'is_anomaly': is_anomaly,
            'score': anomaly_score,
            'threshold': threshold,
            'anomalous_metrics': anomalous_metrics,
            'confidence': min(len(self.data_points) / self.window_size, 1.0)
        }
    
    def _extract_features(self, timestamp, metrics):
        """Extract features from raw metrics"""
        features = []
        
        # Raw metrics
        for key in sorted(metrics.keys()):
            features.append(metrics[key])
        
        # Time-based features
        dt = datetime.fromtimestamp(timestamp)
        features.extend([
            dt.hour,
            dt.weekday(),
            dt.minute / 60.0,  # Fraction of hour
            int(dt.weekday() >= 5),  # Is weekend
        ])
        
        # Rate of change features (if we have history)
        if len(self.data_points) > 0:
            last_point = self.data_points[-1]
            time_delta = timestamp - last_point['timestamp']
            
            if time_delta > 0:
                for key in sorted(metrics.keys()):
                    if key in last_point['metrics']:
                        rate = (metrics[key] - last_point['metrics'][key]) / time_delta
                        features.append(rate)
            else:
                # No rate features
                features.extend([0] * len(metrics))
        else:
            # No rate features
            features.extend([0] * len(metrics))
        
        return np.array(features)
    
    def _update_models(self):
        """Update anomaly detection models"""
        if len(self.data_points) < 50:
            return  # Not enough data
        
        # Prepare training data
        X = np.array([p['features'] for p in self.data_points])
        
        # Fit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Train global model
        self.global_model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        self.global_model.fit(X_scaled)
        
        # Train time-specific models
        # Hourly models
        hourly_data = defaultdict(list)
        for i, point in enumerate(self.data_points):
            hourly_data[point['hour']].append(X_scaled[i])
        
        for hour, hour_data in hourly_data.items():
            if len(hour_data) >= 20:  # Minimum samples
                self.hourly_models[hour] = IsolationForest(
                    contamination=self.contamination * 2,  # Higher contamination for smaller dataset
                    random_state=42,
                    n_estimators=50
                )
                self.hourly_models[hour].fit(np.array(hour_data))
        
        # Daily models
        daily_data = defaultdict(list)
        for i, point in enumerate(self.data_points):
            daily_data[point['day_of_week']].append(X_scaled[i])
        
        for day, day_data in daily_data.items():
            if len(day_data) >= 20:
                self.daily_models[day] = IsolationForest(
                    contamination=self.contamination * 2,
                    random_state=42,
                    n_estimators=50
                )
                self.daily_models[day].fit(np.array(day_data))
    
    def _get_anomaly_score(self, model, features):
        """Get anomaly score from model"""
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get anomaly score (lower is more anomalous)
        score = model.score_samples(features_scaled)[0]
        
        # Convert to 0-1 range (1 is most anomalous)
        # Isolation Forest scores are typically between -0.5 and 0.5
        normalized_score = 1 - (score + 0.5)
        return max(0, min(1, normalized_score))
    
    def _identify_anomalous_metrics(self, metrics, timestamp):
        """Identify which metrics are anomalous"""
        anomalous = []
        
        # Compare each metric against historical distribution
        metric_history = defaultdict(list)
        for point in self.data_points:
            for key, value in point['metrics'].items():
                metric_history[key].append(value)
        
        for key, value in metrics.items():
            if key in metric_history and len(metric_history[key]) > 10:
                history = np.array(metric_history[key])
                mean = np.mean(history)
                std = np.std(history)
                
                if std > 0:
                    z_score = abs(value - mean) / std
                    if z_score > 3:  # 3 standard deviations
                        anomalous.append({
                            'metric': key,
                            'value': value,
                            'expected_range': (mean - 2*std, mean + 2*std),
                            'z_score': z_score
                        })
        
        return anomalous

class MetricSimulator:
    """Simulate metrics with anomalies"""
    def __init__(self):
        self.time = 0
        self.anomaly_prob = 0.02
        
    def generate_metrics(self):
        """Generate realistic metrics with patterns"""
        self.time += 60  # 1 minute intervals
        
        dt = datetime.fromtimestamp(self.time)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # Base patterns
        cpu_base = 30 + 20 * np.sin(hour * np.pi / 12)  # Daily pattern
        if day_of_week >= 5:  # Weekend
            cpu_base *= 0.6
        
        memory_base = 60 + 10 * np.sin(hour * np.pi / 12)
        
        requests_base = 100 + 50 * np.sin(hour * np.pi / 12)
        if 9 <= hour <= 17 and day_of_week < 5:  # Business hours
            requests_base *= 2
        
        # Add noise
        cpu = max(0, cpu_base + np.random.normal(0, 5))
        memory = max(0, memory_base + np.random.normal(0, 3))
        requests = max(0, int(requests_base + np.random.normal(0, 10)))
        
        # Inject anomalies
        if random.random() < self.anomaly_prob:
            anomaly_type = random.choice(['spike', 'drop', 'pattern'])
            
            if anomaly_type == 'spike':
                # Sudden spike in one metric
                metric = random.choice(['cpu', 'memory', 'requests'])
                if metric == 'cpu':
                    cpu = min(100, cpu * random.uniform(2, 4))
                elif metric == 'memory':
                    memory = min(100, memory * random.uniform(1.5, 2.5))
                else:
                    requests = int(requests * random.uniform(3, 5))
            
            elif anomaly_type == 'drop':
                # Sudden drop
                requests = int(requests * random.uniform(0.1, 0.3))
            
            else:  # pattern
                # Unusual correlation
                cpu = memory * 1.5  # CPU tracks memory (unusual)
        
        return {
            'cpu': cpu,
            'memory': memory,
            'requests': requests,
            'response_time': 50 + (cpu / 10) + np.random.normal(0, 5)
        }

# Test the anomaly detector
def test_anomaly_detector():
    detector = AnomalyDetector(window_size=500)
    simulator = MetricSimulator()
    
    print("Training anomaly detector...")
    anomalies_detected = []
    
    # Generate and process metrics
    for i in range(1000):
        metrics = simulator.generate_metrics()
        timestamp = simulator.time
        
        # Add to detector
        detector.add_point(timestamp, metrics)
        
        # Check for anomalies after warmup
        if i > 100:
            result = detector.is_anomalous(metrics, timestamp)
            
            if result['is_anomaly']:
                anomalies_detected.append({
                    'timestamp': timestamp,
                    'metrics': metrics,
                    'result': result
                })
                
                dt = datetime.fromtimestamp(timestamp)
                print(f"\nAnomaly detected at {dt}:")
                print(f"  Score: {result['score']:.3f} (threshold: {result['threshold']:.3f})")
                print(f"  Metrics: {metrics}")
                
                if result['anomalous_metrics']:
                    print("  Anomalous metrics:")
                    for am in result['anomalous_metrics']:
                        print(f"    - {am['metric']}: {am['value']:.1f} "
                              f"(expected: {am['expected_range'][0]:.1f}-{am['expected_range'][1]:.1f}, "
                              f"z-score: {am['z_score']:.1f})")
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} data points...")
    
    print(f"\nTotal anomalies detected: {len(anomalies_detected)}")
    print(f"Detection rate: {len(anomalies_detected) / 900:.1%}")

if __name__ == "__main__":
    test_anomaly_detector()
```

</details>

## Exercise 3: Build a Predictive Autoscaler

**Challenge**: Implement an autoscaler that predicts future load and scales proactively.

```python
class PredictiveAutoscaler:
    def __init__(self, min_instances=1, max_instances=100):
        """
        Initialize predictive autoscaler
        
        Args:
            min_instances: Minimum number of instances
            max_instances: Maximum number of instances
        """
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.history = []
        self.model = None
        
    def record_metrics(self, timestamp, metrics):
        """
        Record current system metrics
        
        TODO:
        1. Store time series data
        2. Extract seasonality patterns
        3. Update prediction model
        """
        pass
    
    def predict_load(self, horizon_minutes=30):
        """
        Predict future load
        
        TODO:
        1. Use historical patterns
        2. Account for trends
        3. Return confidence intervals
        """
        pass
    
    def get_scaling_decision(self, current_instances):
        """
        Decide how many instances we need
        
        TODO:
        1. Predict future load
        2. Calculate required capacity
        3. Consider scaling constraints
        """
        pass
```

<details>
<summary>Solution</summary>

```python
import numpy as np
import pandas as pd
from collections import deque
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class PredictiveAutoscaler:
    def __init__(self, min_instances=1, max_instances=100, 
                 scale_up_threshold=80, scale_down_threshold=40):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        # Historical data
        self.history = deque(maxlen=10080)  # 1 week of minute data
        
        # Models
        self.short_term_model = None  # Next 5-30 minutes
        self.pattern_model = None     # Daily/weekly patterns
        
        # Scaling history
        self.scaling_history = deque(maxlen=100)
        self.last_scale_time = 0
        self.cooldown_period = 300  # 5 minutes
        
    def record_metrics(self, timestamp, metrics):
        """Record current system metrics"""
        # Calculate derived metrics
        cpu_per_instance = metrics.get('avg_cpu', 0)
        total_requests = metrics.get('requests_per_second', 0)
        current_instances = metrics.get('instances', 1)
        
        # Store data point
        data_point = {
            'timestamp': timestamp,
            'cpu': cpu_per_instance,
            'requests': total_requests,
            'instances': current_instances,
            'requests_per_instance': total_requests / current_instances if current_instances > 0 else 0,
            'response_time': metrics.get('avg_response_time', 100),
            'hour': datetime.fromtimestamp(timestamp).hour,
            'day_of_week': datetime.fromtimestamp(timestamp).weekday(),
            'minute_of_day': datetime.fromtimestamp(timestamp).hour * 60 + datetime.fromtimestamp(timestamp).minute
        }
        
        self.history.append(data_point)
        
        # Update models periodically
        if len(self.history) > 100 and len(self.history) % 60 == 0:
            self._update_models()
    
    def predict_load(self, horizon_minutes=30):
        """Predict future load"""
        if len(self.history) < 60:
            return {
                'predictions': [],
                'confidence': 0,
                'method': 'insufficient_data'
            }
        
        current_time = self.history[-1]['timestamp']
        predictions = []
        
        # Generate future timestamps
        future_times = [
            current_time + i * 60 
            for i in range(1, horizon_minutes + 1)
        ]
        
        # Method 1: Pattern-based prediction
        pattern_predictions = self._predict_using_patterns(future_times)
        
        # Method 2: Trend-based prediction
        trend_predictions = self._predict_using_trends(future_times)
        
        # Method 3: ML-based prediction
        ml_predictions = self._predict_using_ml(future_times)
        
        # Ensemble predictions
        for i, timestamp in enumerate(future_times):
            # Weighted average of different methods
            weights = {
                'pattern': 0.4,
                'trend': 0.3,
                'ml': 0.3
            }
            
            if pattern_predictions:
                pred_requests = (
                    weights['pattern'] * pattern_predictions[i]['requests'] +
                    weights['trend'] * trend_predictions[i]['requests']
                )
                
                if ml_predictions:
                    pred_requests = (
                        (weights['pattern'] + weights['trend']) * pred_requests +
                        weights['ml'] * ml_predictions[i]['requests']
                    ) / sum(weights.values())
                
                pred_cpu = (
                    weights['pattern'] * pattern_predictions[i]['cpu'] +
                    weights['trend'] * trend_predictions[i]['cpu']
                )
                
                if ml_predictions:
                    pred_cpu = (
                        (weights['pattern'] + weights['trend']) * pred_cpu +
                        weights['ml'] * ml_predictions[i]['cpu']
                    ) / sum(weights.values())
            else:
                # Fallback to simple prediction
                pred_requests = self.history[-1]['requests']
                pred_cpu = self.history[-1]['cpu']
            
            predictions.append({
                'timestamp': timestamp,
                'requests': pred_requests,
                'cpu': pred_cpu,
                'confidence': self._calculate_confidence(i)
            })
        
        return {
            'predictions': predictions,
            'confidence': np.mean([p['confidence'] for p in predictions]),
            'method': 'ensemble'
        }
    
    def _predict_using_patterns(self, future_times):
        """Predict using daily/weekly patterns"""
        if len(self.history) < 1440:  # Less than 1 day
            return None
        
        predictions = []
        
        # Convert history to DataFrame for easier analysis
        df = pd.DataFrame(list(self.history))
        
        for timestamp in future_times:
            dt = datetime.fromtimestamp(timestamp)
            hour = dt.hour
            minute = dt.minute
            day_of_week = dt.weekday()
            minute_of_day = hour * 60 + minute
            
            # Find similar time points in history
            similar_points = df[
                (df['hour'] == hour) & 
                (df['day_of_week'] == day_of_week)
            ]
            
            if len(similar_points) == 0:
                # Fallback to same hour any day
                similar_points = df[df['hour'] == hour]
            
            if len(similar_points) > 0:
                # Use recent similar points with decay
                weights = np.exp(-np.arange(len(similar_points)) * 0.1)
                weights = weights / weights.sum()
                
                pred_requests = np.average(similar_points['requests'].values, weights=weights)
                pred_cpu = np.average(similar_points['cpu'].values, weights=weights)
            else:
                # Use overall average
                pred_requests = df['requests'].mean()
                pred_cpu = df['cpu'].mean()
            
            predictions.append({
                'requests': pred_requests,
                'cpu': pred_cpu
            })
        
        return predictions
    
    def _predict_using_trends(self, future_times):
        """Predict using recent trends"""
        # Use last hour of data
        recent_points = list(self.history)[-60:]
        if len(recent_points) < 10:
            return [{'requests': self.history[-1]['requests'], 
                    'cpu': self.history[-1]['cpu']} 
                   for _ in future_times]
        
        # Fit linear trend
        X = np.array([i for i in range(len(recent_points))]).reshape(-1, 1)
        y_requests = np.array([p['requests'] for p in recent_points])
        y_cpu = np.array([p['cpu'] for p in recent_points])
        
        model_requests = LinearRegression()
        model_cpu = LinearRegression()
        
        model_requests.fit(X, y_requests)
        model_cpu.fit(X, y_cpu)
        
        predictions = []
        base_idx = len(recent_points)
        
        for i, timestamp in enumerate(future_times):
            # Extrapolate trend
            future_idx = base_idx + i
            pred_requests = model_requests.predict([[future_idx]])[0]
            pred_cpu = model_cpu.predict([[future_idx]])[0]
            
            # Apply bounds
            pred_requests = max(0, pred_requests)
            pred_cpu = max(0, min(100, pred_cpu))
            
            predictions.append({
                'requests': pred_requests,
                'cpu': pred_cpu
            })
        
        return predictions
    
    def _predict_using_ml(self, future_times):
        """Predict using machine learning model"""
        if self.short_term_model is None or len(self.history) < 1000:
            return None
        
        predictions = []
        
        for timestamp in future_times:
            # Extract features for future timestamp
            dt = datetime.fromtimestamp(timestamp)
            features = [
                dt.hour,
                dt.weekday(),
                dt.minute,
                int(dt.weekday() >= 5),  # Is weekend
                np.sin(2 * np.pi * dt.hour / 24),  # Cyclic hour encoding
                np.cos(2 * np.pi * dt.hour / 24),
                np.sin(2 * np.pi * dt.weekday() / 7),  # Cyclic day encoding
                np.cos(2 * np.pi * dt.weekday() / 7)
            ]
            
            # Predict
            pred_requests = self.short_term_model['requests'].predict([features])[0]
            pred_cpu = self.short_term_model['cpu'].predict([features])[0]
            
            predictions.append({
                'requests': max(0, pred_requests),
                'cpu': max(0, min(100, pred_cpu))
            })
        
        return predictions
    
    def _update_models(self):
        """Update prediction models"""
        if len(self.history) < 1000:
            return
        
        # Prepare training data
        df = pd.DataFrame(list(self.history))
        
        # Features for ML model
        features = []
        targets_requests = []
        targets_cpu = []
        
        for i in range(len(df) - 30):  # Predict 30 minutes ahead
            row = df.iloc[i]
            target_row = df.iloc[i + 30]
            
            dt = datetime.fromtimestamp(row['timestamp'])
            
            feature_vec = [
                dt.hour,
                dt.weekday(),
                dt.minute,
                int(dt.weekday() >= 5),
                np.sin(2 * np.pi * dt.hour / 24),
                np.cos(2 * np.pi * dt.hour / 24),
                np.sin(2 * np.pi * dt.weekday() / 7),
                np.cos(2 * np.pi * dt.weekday() / 7)
            ]
            
            features.append(feature_vec)
            targets_requests.append(target_row['requests'])
            targets_cpu.append(target_row['cpu'])
        
        X = np.array(features)
        y_requests = np.array(targets_requests)
        y_cpu = np.array(targets_cpu)
        
        # Train models
        self.short_term_model = {
            'requests': RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42),
            'cpu': RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
        }
        
        self.short_term_model['requests'].fit(X, y_requests)
        self.short_term_model['cpu'].fit(X, y_cpu)
    
    def get_scaling_decision(self, current_instances):
        """Decide how many instances we need"""
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_scale_time < self.cooldown_period:
            return {
                'action': 'wait',
                'target_instances': current_instances,
                'reason': 'cooldown_period'
            }
        
        # Get predictions
        predictions = self.predict_load(horizon_minutes=15)
        
        if predictions['confidence'] < 0.5:
            # Low confidence, use reactive scaling
            return self._reactive_scaling(current_instances)
        
        # Find peak predicted load in next 15 minutes
        peak_cpu = max(p['cpu'] for p in predictions['predictions'])
        peak_requests = max(p['requests'] for p in predictions['predictions'])
        
        # Calculate required instances based on predictions
        # Aim to keep CPU below threshold even at peak
        required_for_cpu = int(np.ceil(
            current_instances * peak_cpu / self.scale_up_threshold
        ))
        
        # Also consider request rate (assume 100 req/s per instance capacity)
        requests_per_instance_capacity = 100
        required_for_requests = int(np.ceil(
            peak_requests / requests_per_instance_capacity
        ))
        
        required_instances = max(required_for_cpu, required_for_requests)
        
        # Apply constraints
        required_instances = max(self.min_instances, 
                               min(self.max_instances, required_instances))
        
        # Determine action
        if required_instances > current_instances * 1.1:  # Scale up if >10% increase needed
            action = 'scale_up'
            self.last_scale_time = current_time
        elif required_instances < current_instances * 0.9:  # Scale down if >10% decrease possible
            # Check if we've been stable
            recent_cpu = np.mean([p['cpu'] for p in list(self.history)[-30:]])
            if recent_cpu < self.scale_down_threshold:
                action = 'scale_down'
                self.last_scale_time = current_time
            else:
                action = 'wait'
        else:
            action = 'wait'
        
        # Record decision
        self.scaling_history.append({
            'timestamp': current_time,
            'current': current_instances,
            'target': required_instances,
            'action': action,
            'peak_cpu_predicted': peak_cpu,
            'peak_requests_predicted': peak_requests
        })
        
        return {
            'action': action,
            'target_instances': required_instances,
            'reason': 'predictive',
            'predictions': predictions['predictions'][:5],  # Next 5 minutes
            'confidence': predictions['confidence']
        }
    
    def _reactive_scaling(self, current_instances):
        """Fallback reactive scaling"""
        if len(self.history) == 0:
            return {
                'action': 'wait',
                'target_instances': current_instances,
                'reason': 'no_data'
            }
        
        # Use recent metrics
        recent_metrics = list(self.history)[-5:]
        avg_cpu = np.mean([m['cpu'] for m in recent_metrics])
        
        if avg_cpu > self.scale_up_threshold:
            target = min(self.max_instances, int(current_instances * 1.5))
            return {
                'action': 'scale_up',
                'target_instances': target,
                'reason': 'reactive_high_cpu'
            }
        elif avg_cpu < self.scale_down_threshold:
            target = max(self.min_instances, int(current_instances * 0.8))
            return {
                'action': 'scale_down',
                'target_instances': target,
                'reason': 'reactive_low_cpu'
            }
        
        return {
            'action': 'wait',
            'target_instances': current_instances,
            'reason': 'reactive_stable'
        }
    
    def _calculate_confidence(self, minutes_ahead):
        """Calculate prediction confidence based on lookahead time"""
        # Confidence decreases with time
        base_confidence = min(len(self.history) / 1440, 1.0)  # Based on data amount
        time_decay = np.exp(-minutes_ahead / 30)  # Exponential decay
        
        return base_confidence * time_decay

# Test the predictive autoscaler
def simulate_load_pattern(hour, day_of_week):
    """Simulate realistic load patterns"""
    # Base load with daily pattern
    base_load = 50 + 30 * np.sin((hour - 6) * np.pi / 12)
    
    # Weekday vs weekend
    if day_of_week < 5:  # Weekday
        if 9 <= hour <= 17:  # Business hours
            base_load *= 1.5
        if hour == 12:  # Lunch spike
            base_load *= 1.2
    else:  # Weekend
        base_load *= 0.6
    
    # Add noise
    noise = np.random.normal(0, 5)
    
    return max(10, base_load + noise)

def test_predictive_autoscaler():
    autoscaler = PredictiveAutoscaler(min_instances=2, max_instances=20)
    
    # Simulate 3 days of data
    current_time = time.time() - 3 * 24 * 3600  # Start 3 days ago
    current_instances = 5
    
    print("Simulating load and autoscaling decisions...")
    
    for i in range(3 * 24 * 60):  # 3 days of minutes
        dt = datetime.fromtimestamp(current_time)
        
        # Simulate load
        load = simulate_load_pattern(dt.hour, dt.weekday())
        requests = load * 10  # Convert to requests/second
        cpu = min(95, load * current_instances / current_instances)  # CPU based on load/capacity
        
        # Add some spikes
        if random.random() < 0.01:  # 1% chance of spike
            requests *= random.uniform(2, 3)
            cpu = min(95, cpu * 1.5)
        
        # Record metrics
        metrics = {
            'avg_cpu': cpu,
            'requests_per_second': requests,
            'instances': current_instances,
            'avg_response_time': 50 + (cpu / 10)
        }
        
        autoscaler.record_metrics(current_time, metrics)
        
        # Get scaling decision every 5 minutes
        if i % 5 == 0 and i > 60:
            decision = autoscaler.get_scaling_decision(current_instances)
            
            if decision['action'] != 'wait':
                old_instances = current_instances
                current_instances = decision['target_instances']
                
                print(f"\n{dt}: Scaling decision")
                print(f"  Action: {decision['action']}")
                print(f"  Instances: {old_instances} -> {current_instances}")
                print(f"  Reason: {decision['reason']}")
                print(f"  Current CPU: {cpu:.1f}%")
                print(f"  Current requests: {requests:.0f}/s")
                
                if 'predictions' in decision:
                    print("  Predictions:")
                    for pred in decision['predictions'][:3]:
                        pred_dt = datetime.fromtimestamp(pred['timestamp'])
                        print(f"    {pred_dt.strftime('%H:%M')}: "
                              f"CPU={pred['cpu']:.1f}%, "
                              f"Requests={pred['requests']:.0f}/s")
        
        # Progress
        if (i + 1) % 1440 == 0:
            day = (i + 1) // 1440
            print(f"\nCompleted day {day}")
            print(f"Current instances: {current_instances}")
            print(f"Average CPU: {np.mean([h['cpu'] for h in list(autoscaler.history)[-1440:]]):.1f}%")
        
        current_time += 60  # Next minute

if __name__ == "__main__":
    test_predictive_autoscaler()
```

</details>

## Exercise 4: Build a Learning Cache

**Challenge**: Implement a cache that learns access patterns and pre-fetches data.

```python
class LearningCache:
    def __init__(self, max_size=1000):
        """
        Initialize learning cache
        
        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self.cache = {}
        self.access_history = []
        
    def get(self, key):
        """
        Get value from cache
        
        TODO:
        1. Track access patterns
        2. Update access predictions
        3. Trigger prefetch if needed
        """
        pass
    
    def predict_next_access(self, key):
        """
        Predict when key will be accessed next
        
        TODO:
        1. Analyze access patterns
        2. Identify periodic accesses
        3. Return predicted time
        """
        pass
    
    def prefetch(self):
        """
        Prefetch data likely to be needed soon
        
        TODO:
        1. Identify candidates for prefetching
        2. Consider cache space
        3. Fetch most valuable items
        """
        pass
```

## Exercise 5: Implement Reinforcement Learning for Resource Allocation

**Challenge**: Build a system that learns optimal resource allocation through trial and error.

```python
class ResourceAllocator:
    def __init__(self, resources, services):
        """
        Initialize RL-based resource allocator
        
        Args:
            resources: List of available resources
            services: List of services needing resources
        """
        self.resources = resources
        self.services = services
        self.q_table = {}  # State-action values
        
    def allocate(self, state):
        """
        Allocate resources based on current state
        
        TODO:
        1. Choose action using epsilon-greedy
        2. Apply resource allocation
        3. Return allocation decisions
        """
        pass
    
    def update_q_value(self, state, action, reward, next_state):
        """
        Update Q-values based on observed reward
        
        TODO:
        1. Implement Q-learning update
        2. Handle exploration vs exploitation
        3. Decay learning rate over time
        """
        pass
```

## Exercise 6: Build an Intelligent Request Router

**Challenge**: Route requests to services based on learned performance characteristics.

```python
class IntelligentRouter:
    def __init__(self, services):
        """
        Initialize intelligent request router
        
        Args:
            services: List of available services
        """
        self.services = services
        self.performance_history = {}
        self.routing_model = None
        
    def route_request(self, request):
        """
        Route request to best service
        
        TODO:
        1. Extract request features
        2. Predict performance for each service
        3. Select optimal service
        """
        pass
    
    def learn_from_outcome(self, request, service, outcome):
        """
        Update model based on routing outcome
        
        TODO:
        1. Record performance data
        2. Update predictive model
        3. Adjust routing strategy
        """
        pass
```

## Exercise 7: Implement Distributed Learning

**Challenge**: Build a system where multiple nodes collaboratively learn patterns.

```python
class DistributedLearner:
    def __init__(self, node_id, peers):
        """
        Initialize distributed learning node
        
        Args:
            node_id: Unique node identifier
            peers: List of peer nodes
        """
        self.node_id = node_id
        self.peers = peers
        self.local_model = None
        self.peer_models = {}
        
    def train_local_model(self, data):
        """
        Train model on local data
        
        TODO:
        1. Train on local dataset
        2. Extract model parameters
        3. Prepare for sharing
        """
        pass
    
    def federated_average(self):
        """
        Combine models from all peers
        
        TODO:
        1. Collect model updates from peers
        2. Average parameters
        3. Update local model
        """
        pass
```

## Thought Experiments

### 1. The Cold Start Problem
Your learning system has no historical data.
- How do you bootstrap learning?
- What's the cost of early bad decisions?
- Design a solution that balances exploration with safety.

### 2. The Adversarial User
Users discover your caching predictions and start gaming the system.
- How do you detect adversarial behavior?
- Should the system adapt or resist?
- Design a robust learning mechanism.

### 3. The Concept Drift
Your system learned patterns, but user behavior suddenly changes (e.g., pandemic).
- How quickly should the system adapt?
- How do you distinguish temporary spikes from permanent changes?
- Design an adaptive learning rate mechanism.

## Practical Scenarios

### Scenario 1: Smart CDN
Design a CDN that learns content popularity patterns to:
- Pre-position content at edge locations
- Predict viral content before it spikes
- Optimize storage allocation
- Minimize cache misses

### Scenario 2: Intelligent Database
Build a database system that:
- Learns query patterns
- Automatically creates indexes
- Adjusts query plans based on history
- Predicts resource needs

### Scenario 3: Self-Tuning Application
Create an application that:
- Learns optimal configuration values
- Adjusts parameters based on workload
- Predicts performance impacts
- Prevents configuration drift

## Research Questions

1. **How do you prevent feedback loops in learning systems?**
   - What happens when predictions influence behavior?
   - How do you maintain stability?

2. **When is learning worth the complexity?**
   - What's the break-even point?
   - How do you measure learning effectiveness?

3. **How do you handle privacy in distributed learning?**
   - Can you learn without seeing raw data?
   - What about differential privacy?

## Key Concepts to Master

1. **Exploration vs Exploitation**
   - Thompson Sampling
   - Upper Confidence Bounds
   - Epsilon-greedy strategies

2. **Online Learning**
   - Incremental updates
   - Concept drift detection
   - Adaptive learning rates

3. **Distributed Learning**
   - Federated learning
   - Model aggregation
   - Privacy preservation

## Reflection

After completing these exercises:

1. What makes distributed learning different from centralized ML?

2. How do you handle the uncertainty inherent in predictions?

3. When should systems learn automatically vs. require human input?

4. What are the risks of autonomous learning systems?

Remember: Intelligence in distributed systems isn't about perfect predictions—it's about continuous improvement and adaptation. Start simple, measure everything, and let the system teach you what it needs to learn.
