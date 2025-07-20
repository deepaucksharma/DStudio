---
title: Intelligence & Learning Examples
description: "Real-world examples of intelligent and adaptive systems in distributed computing"
type: pillar
difficulty: beginner
reading_time: 15 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Intelligence](/part2-pillars/intelligence/) → **Intelligence & Learning Examples**

# Intelligence & Learning Examples

## Real-World Case Studies

### 1. Google's Borg: Learning from History

**Problem**: Predict resource requirements for better bin packing

**Solution**: Machine learning on historical usage patterns

```python
class BorgResourcePredictor:
    def __init__(self):
        self.job_history = defaultdict(list)
        self.models = {}

    def record_job_execution(self, job_id, requested, actual_usage):
        """Record actual vs requested resources"""
        self.job_history[job_id].append({
            'timestamp': time.time(),
            'requested': requested,
            'actual': actual_usage,
            'ratio': {
                'cpu': actual_usage['cpu'] / requested['cpu'],
                'memory': actual_usage['memory'] / requested['memory']
            }
        })

        # Retrain model periodically
        if len(self.job_history[job_id]) % 100 == 0:
            self.train_model(job_id)

    def train_model(self, job_id):
        """Train prediction model for specific job type"""
        history = self.job_history[job_id]

        if len(history) < 10:
            return

        # Extract features and labels
        X = []  # Features: time of day, day of week, requested resources
        y_cpu = []  # Labels: actual CPU usage
        y_mem = []  # Labels: actual memory usage

        for record in history:
            timestamp = record['timestamp']
            dt = datetime.fromtimestamp(timestamp)

            features = [
                dt.hour,  # Hour of day
                dt.weekday(),  # Day of week
                record['requested']['cpu'],
                record['requested']['memory'],
                len(history)  # Job run count (for learning curves)
            ]
            X.append(features)
            y_cpu.append(record['actual']['cpu'])
            y_mem.append(record['actual']['memory'])

        # Simple linear regression (in practice, use more sophisticated models)
        from sklearn.linear_model import LinearRegression

        cpu_model = LinearRegression()
        cpu_model.fit(X, y_cpu)

        mem_model = LinearRegression()
        mem_model.fit(X, y_mem)

        self.models[job_id] = {
            'cpu': cpu_model,
            'memory': mem_model,
            'trained_on': len(history)
        }

    def predict_resources(self, job_id, requested_resources):
        """Predict actual resource usage"""
        if job_id not in self.models:
            # No model yet, use heuristic
            return {
                'cpu': requested_resources['cpu'] * 0.7,  # Most jobs overrequest
                'memory': requested_resources['memory'] * 0.85
            }

        # Prepare features
        dt = datetime.now()
        features = [[
            dt.hour,
            dt.weekday(),
            requested_resources['cpu'],
            requested_resources['memory'],
            self.models[job_id]['trained_on']
        ]]

        # Predict
        predicted = {
            'cpu': self.models[job_id]['cpu'].predict(features)[0],
            'memory': self.models[job_id]['memory'].predict(features)[0]
        }

        # Bound predictions to reasonable ranges
        predicted['cpu'] = max(0.1, min(predicted['cpu'], requested_resources['cpu']))
        predicted['memory'] = max(0.1, min(predicted['memory'], requested_resources['memory']))

        return predicted

class IntelligentScheduler:
    def __init__(self):
        self.predictor = BorgResourcePredictor()
        self.placement_history = []

    def schedule_job(self, job, available_machines):
        """Schedule job using predictions"""
        # Get predicted actual usage
        predicted_usage = self.predictor.predict_resources(
            job.id,
            job.requested_resources
        )

        # Find best fit using predicted values
        best_machine = None
        best_score = float('inf')

        for machine in available_machines:
            if self.can_fit(machine, predicted_usage):
                # Score based on resource fragmentation
                score = self.fragmentation_score(machine, predicted_usage)
                if score < best_score:
                    best_score = score
                    best_machine = machine

        if best_machine:
            # Place job
            self.place_job(best_machine, job, predicted_usage)

            # Record placement for learning
            self.placement_history.append({
                'job': job.id,
                'machine': best_machine.id,
                'predicted': predicted_usage,
                'timestamp': time.time()
            })

        return best_machine

    def fragmentation_score(self, machine, resources):
        """Calculate resource fragmentation if job placed"""
        cpu_remaining = machine.available_cpu - resources['cpu']
        mem_remaining = machine.available_memory - resources['memory']

        # Penalize unbalanced resource usage
        cpu_frag = cpu_remaining / machine.total_cpu
        mem_frag = mem_remaining / machine.total_memory

        imbalance = abs(cpu_frag - mem_frag)
        waste = min(cpu_frag, mem_frag)  # Resources that can't be used

        return imbalance + waste
```

### 2. Netflix's Adaptive Streaming: Real-time Quality Optimization

**Problem**: Optimize video quality based on network conditions

**Solution**: Reinforcement learning for bitrate adaptation

```python
class AdaptiveBitrateAgent:
    def __init__(self):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.1

        # State features
        self.bandwidth_buckets = [0.5, 1, 2, 5, 10, 20]  # Mbps
        self.buffer_buckets = [0, 5, 10, 20, 30]  # seconds
        self.bitrates = [0.4, 0.8, 1.4, 2.4, 4.3, 6.0]  # Mbps

    def get_state(self, bandwidth, buffer_level, current_bitrate):
        """Discretize continuous state"""
        # Bucket bandwidth
        bw_bucket = 0
        for i, threshold in enumerate(self.bandwidth_buckets):
            if bandwidth >= threshold:
                bw_bucket = i

        # Bucket buffer
        buf_bucket = 0
        for i, threshold in enumerate(self.buffer_buckets):
            if buffer_level >= threshold:
                buf_bucket = i

        # Current quality level
        quality_level = self.bitrates.index(
            min(self.bitrates, key=lambda x: abs(x - current_bitrate))
        )

        return (bw_bucket, buf_bucket, quality_level)

    def choose_action(self, state):
        """Epsilon-greedy action selection"""
        if random.random() < self.exploration_rate:
            # Explore: random bitrate
            return random.randint(0, len(self.bitrates) - 1)
        else:
            # Exploit: best known action
            return max(
                range(len(self.bitrates)),
                key=lambda a: self.q_table[state][a]
            )

    def calculate_reward(self, bitrate, rebuffering_time, quality_change):
        """Reward function balancing quality and smoothness"""
        # Reward for high quality
        quality_reward = bitrate / max(self.bitrates)

        # Penalty for rebuffering (stalls)
        rebuffer_penalty = rebuffering_time * 10

        # Penalty for quality changes (smoothness)
        change_penalty = abs(quality_change) * 0.5

        return quality_reward - rebuffer_penalty - change_penalty

    def update_q_value(self, state, action, reward, next_state):
        """Q-learning update"""
        current_q = self.q_table[state][action]

        # Best Q-value for next state
        max_next_q = max(
            self.q_table[next_state].values()
        ) if self.q_table[next_state] else 0

        # Q-learning formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state][action] = new_q

    def adapt_bitrate(self, current_state, network_stats):
        """Main adaptation logic"""
        state = self.get_state(
            network_stats['bandwidth'],
            network_stats['buffer_level'],
            network_stats['current_bitrate']
        )

        # Choose action
        action = self.choose_action(state)
        new_bitrate = self.bitrates[action]

        return new_bitrate

class VideoStreamingSession:
    def __init__(self):
        self.agent = AdaptiveBitrateAgent()
        self.buffer = 0
        self.current_bitrate = 0.8  # Start conservative
        self.total_watch_time = 0
        self.total_rebuffer_time = 0
        self.quality_switches = 0

    def simulate_streaming(self, duration_seconds):
        """Simulate a streaming session"""
        for t in range(duration_seconds):
            # Simulate varying network conditions
            bandwidth = self.simulate_bandwidth(t)

            # Get current state
            state = self.agent.get_state(
                bandwidth,
                self.buffer,
                self.current_bitrate
            )

            # Agent chooses bitrate
            action = self.agent.choose_action(state)
            new_bitrate = self.agent.bitrates[action]

            # Simulate buffer dynamics
            download_rate = min(bandwidth, new_bitrate * 1.2)  # Some overhead

            if self.buffer > 0:
                # Playing video
                self.buffer -= 1
                self.total_watch_time += 1

                # Download while playing
                self.buffer += download_rate / new_bitrate
            else:
                # Rebuffering (stalled)
                self.total_rebuffer_time += 1
                self.buffer += download_rate / new_bitrate

            # Track quality switches
            if new_bitrate != self.current_bitrate:
                self.quality_switches += 1
                quality_change = new_bitrate - self.current_bitrate
            else:
                quality_change = 0

            # Calculate reward
            rebuffer_penalty = 1 if self.buffer <= 0 else 0
            reward = self.agent.calculate_reward(
                new_bitrate,
                rebuffer_penalty,
                quality_change
            )

            # Update Q-values
            next_state = self.agent.get_state(
                bandwidth,
                self.buffer,
                new_bitrate
            )
            self.agent.update_q_value(state, action, reward, next_state)

            # Update state
            self.current_bitrate = new_bitrate

            # Cap buffer
            self.buffer = min(self.buffer, 30)

        # Calculate QoE metrics
        qoe_score = (
            self.total_watch_time / duration_seconds * 100 -
            self.total_rebuffer_time * 10 -
            self.quality_switches * 0.5
        )

        return {
            'qoe_score': qoe_score,
            'avg_bitrate': self.current_bitrate,
            'rebuffer_ratio': self.total_rebuffer_time / duration_seconds,
            'switches': self.quality_switches
        }

    def simulate_bandwidth(self, time):
        """Simulate realistic bandwidth variations"""
        # Base bandwidth with variations
        base = 5.0  # Mbps

        # Periodic congestion
        if time % 300 < 60:  # Every 5 minutes, 1 minute of congestion
            base *= 0.3

        # Random variations
        noise = random.uniform(0.8, 1.2)

        # Sudden drops
        if random.random() < 0.02:  # 2% chance
            base *= 0.1

        return max(0.1, base * noise)
```

### 3. Cloudflare's Intelligent DDoS Mitigation

**Problem**: Distinguish DDoS traffic from legitimate traffic

**Solution**: Adaptive learning with traffic fingerprinting

```python
class DDoSMitigationSystem:
    def __init__(self):
        self.traffic_profiles = {}
        self.anomaly_detector = AnomalyDetector()
        self.mitigation_rules = []

    class TrafficProfile:
        def __init__(self):
            self.request_rates = []
            self.packet_sizes = []
            self.geo_distribution = defaultdict(int)
            self.user_agents = defaultdict(int)
            self.path_distribution = defaultdict(int)

        def update(self, request):
            """Update profile with new request"""
            self.request_rates.append(time.time())
            self.packet_sizes.append(request.size)
            self.geo_distribution[request.country] += 1
            self.user_agents[request.user_agent] += 1
            self.path_distribution[request.path] += 1

            # Keep sliding window
            cutoff = time.time() - 3600  # 1 hour
            self.request_rates = [t for t in self.request_rates if t > cutoff]

        def get_features(self):
            """Extract statistical features"""
            if not self.request_rates:
                return None

            # Request rate statistics
            intervals = []
            for i in range(1, len(self.request_rates)):
                intervals.append(self.request_rates[i] - self.request_rates[i-1])

            features = {
                'request_rate': len(self.request_rates) / 3600,
                'rate_variance': np.var(intervals) if intervals else 0,
                'avg_packet_size': np.mean(self.packet_sizes) if self.packet_sizes else 0,
                'geo_entropy': self.calculate_entropy(self.geo_distribution),
                'ua_entropy': self.calculate_entropy(self.user_agents),
                'path_entropy': self.calculate_entropy(self.path_distribution),
                'top_geo_concentration': max(self.geo_distribution.values()) / sum(self.geo_distribution.values()) if self.geo_distribution else 0
            }

            return features

        def calculate_entropy(self, distribution):
            """Calculate Shannon entropy"""
            total = sum(distribution.values())
            if total == 0:
                return 0

            entropy = 0
            for count in distribution.values():
                if count > 0:
                    p = count / total
                    entropy -= p * np.log2(p)

            return entropy

    def analyze_traffic(self, source_ip, request):
        """Analyze request and decide if legitimate"""
        # Get or create profile
        if source_ip not in self.traffic_profiles:
            self.traffic_profiles[source_ip] = self.TrafficProfile()

        profile = self.traffic_profiles[source_ip]
        profile.update(request)

        # Extract features
        features = profile.get_features()
        if not features:
            return True  # Not enough data

        # Check against learned patterns
        is_anomaly = self.anomaly_detector.is_anomaly(features)

        # Apply specific rules
        if is_anomaly:
            threat_score = self.calculate_threat_score(features, profile)

            if threat_score > 0.8:
                # High confidence attack
                self.block_ip(source_ip, duration=3600)
                return False
            elif threat_score > 0.5:
                # Suspicious, apply challenge
                self.apply_challenge(source_ip)
                return 'challenge'

        return True

    def calculate_threat_score(self, features, profile):
        """Calculate likelihood of being an attack"""
        score = 0

        # High request rate
        if features['request_rate'] > 100:  # 100 req/hour
            score += 0.3

        # Low entropy (automated behavior)
        if features['ua_entropy'] < 0.5:
            score += 0.2
        if features['path_entropy'] < 1.0:
            score += 0.2

        # Geographic concentration
        if features['top_geo_concentration'] > 0.9:
            score += 0.2

        # Request patterns
        if features['rate_variance'] < 0.001:  # Very regular intervals
            score += 0.3

        return min(1.0, score)

    def apply_challenge(self, source_ip):
        """Apply progressive challenges"""
        challenge_level = self.get_challenge_level(source_ip)

        if challenge_level == 1:
            # JavaScript challenge
            return JavaScriptChallenge()
        elif challenge_level == 2:
            # CAPTCHA
            return CaptchaChallenge()
        else:
            # Proof of work
            return ProofOfWorkChallenge(difficulty=challenge_level)

class AnomalyDetector:
    """Isolation Forest for anomaly detection"""
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.trees = []
        self.training_data = []

    def fit(self, normal_traffic_features):
        """Train on normal traffic"""
        self.training_data = normal_traffic_features

        # Build isolation trees
        n_trees = 100
        sample_size = min(256, len(normal_traffic_features))

        for _ in range(n_trees):
            # Random subsample
            sample_indices = np.random.choice(
                len(normal_traffic_features),
                sample_size,
                replace=False
            )
            sample = [normal_traffic_features[i] for i in sample_indices]

            # Build tree
            tree = self.build_isolation_tree(sample)
            self.trees.append(tree)

    def is_anomaly(self, features):
        """Check if features represent anomaly"""
        # Average path length across all trees
        path_lengths = []

        for tree in self.trees:
            path_length = self.get_path_length(tree, features)
            path_lengths.append(path_length)

        avg_path_length = np.mean(path_lengths)

        # Normalize by expected path length
        n = len(self.training_data)
        expected_path = 2 * (np.log(n - 1) + 0.5772) - (2 * (n - 1) / n)

        anomaly_score = 2 ** (-avg_path_length / expected_path)

        return anomaly_score > 0.6  # Threshold
```

### 4. Amazon's Predictive Auto-scaling

**Problem**: Scale resources before demand spike hits

**Solution**: Time-series forecasting with multiple signals

```python
class PredictiveAutoScaler:
    def __init__(self):
        self.history_window = 4 * 7 * 24  # 4 weeks of hourly data
        self.forecast_horizon = 24  # 24 hours ahead
        self.metrics_history = defaultdict(list)

    def record_metrics(self, timestamp, metrics):
        """Record system metrics"""
        self.metrics_history['timestamps'].append(timestamp)

        for metric_name, value in metrics.items():
            self.metrics_history[metric_name].append(value)

        # Maintain sliding window
        self.prune_old_data()

    def forecast_demand(self):
        """Forecast future resource needs"""
        # Use Prophet for time-series forecasting
        from fbprophet import Prophet

        # Prepare data
        df = pd.DataFrame({
            'ds': pd.to_datetime(self.metrics_history['timestamps'], unit='s'),
            'y': self.metrics_history['cpu_usage']
        })

        # Add additional regressors
        df['hour'] = df['ds'].dt.hour
        df['dayofweek'] = df['ds'].dt.dayofweek
        df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)

        # Handle special events (e.g., sales, holidays)
        holidays = self.get_holiday_calendar()

        # Build model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            holidays=holidays,
            changepoint_prior_scale=0.05  # More resistant to outliers
        )

        # Add custom seasonalities
        model.add_seasonality(
            name='hourly',
            period=1,
            fourier_order=3
        )

        # Fit model
        model.fit(df)

        # Make forecast
        future = model.make_future_dataframe(periods=self.forecast_horizon, freq='H')
        forecast = model.predict(future)

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(self.forecast_horizon)

    def decide_scaling_action(self, current_resources, forecast):
        """Decide how many instances to add/remove"""
        # Get peak predicted demand in next N hours
        lookahead_hours = 2  # Look 2 hours ahead
        peak_demand = forecast.head(lookahead_hours)['yhat_upper'].max()

        # Calculate required resources
        # Assume linear relationship between CPU and instances needed
        cpu_per_instance = 80  # Target 80% CPU utilization
        required_instances = int(np.ceil(peak_demand / cpu_per_instance))

        # Add safety margin for prediction uncertainty
        safety_margin = 1.2
        required_instances = int(required_instances * safety_margin)

        # Consider scale-up/down time
        scale_up_time = 5  # minutes
        current_demand = self.metrics_history['cpu_usage'][-1]

        # If demand is rising quickly, be more aggressive
        if len(self.metrics_history['cpu_usage']) > 10:
            recent_trend = np.polyfit(range(10), self.metrics_history['cpu_usage'][-10:], 1)[0]
            if recent_trend > 5:  # CPU increasing >5% per measurement
                required_instances = int(required_instances * 1.3)

        # Calculate delta
        delta = required_instances - current_resources['instances']

        # Apply hysteresis to prevent flapping
        if abs(delta) < 2:
            delta = 0

        return {
            'action': 'scale_up' if delta > 0 else 'scale_down' if delta < 0 else 'maintain',
            'delta': abs(delta),
            'target_instances': required_instances,
            'reason': f"Predicted peak demand: {peak_demand:.1f}%",
            'confidence': self.calculate_confidence(forecast)
        }

    def calculate_confidence(self, forecast):
        """Calculate confidence in prediction"""
        # Wider confidence intervals = less confidence
        uncertainty = (forecast['yhat_upper'] - forecast['yhat_lower']).mean()
        base_value = forecast['yhat'].mean()

        relative_uncertainty = uncertainty / base_value if base_value > 0 else 1
        confidence = max(0, 1 - relative_uncertainty)

        return confidence

class MultiSignalPredictor:
    """Combine multiple signals for better predictions"""

    def __init__(self):
        self.predictors = {
            'time_series': PredictiveAutoScaler(),
            'business_events': EventBasedPredictor(),
            'external_signals': ExternalSignalPredictor(),
            'ml_model': MLBasedPredictor()
        }
        self.ensemble_weights = {
            'time_series': 0.4,
            'business_events': 0.3,
            'external_signals': 0.2,
            'ml_model': 0.1
        }

    def predict(self, context):
        """Ensemble prediction"""
        predictions = {}

        for name, predictor in self.predictors.items():
            try:
                pred = predictor.predict(context)
                predictions[name] = pred
            except Exception as e:
                print(f"Predictor {name} failed: {e}")
                predictions[name] = None

        # Weighted average of predictions
        weighted_sum = 0
        total_weight = 0

        for name, pred in predictions.items():
            if pred is not None:
                weight = self.ensemble_weights[name]
                weighted_sum += pred * weight
                total_weight += weight

        if total_weight > 0:
            ensemble_prediction = weighted_sum / total_weight
        else:
            # Fallback to simple heuristic
            ensemble_prediction = context['current_load'] * 1.2

        return ensemble_prediction
```

### 5. Adaptive Load Balancing with Multi-Armed Bandits

**Problem**: Route traffic to best performing backend without knowing performance a priori

**Solution**: Thompson Sampling for exploration/exploitation

```python
class ThompsonSamplingLoadBalancer:
    def __init__(self, backends):
        self.backends = backends
        # Beta distribution parameters for each backend
        self.successes = defaultdict(lambda: 1)  # Alpha
        self.failures = defaultdict(lambda: 1)   # Beta

    def select_backend(self):
        """Select backend using Thompson Sampling"""
        # Sample from Beta distribution for each backend
        samples = {}

        for backend in self.backends:
            # Sample from Beta(successes + 1, failures + 1)
            sample = np.random.beta(
                self.successes[backend],
                self.failures[backend]
            )
            samples[backend] = sample

        # Select backend with highest sample
        selected = max(samples, key=samples.get)

        return selected, samples

    def update_reward(self, backend, success, response_time=None):
        """Update backend statistics"""
        if success and response_time < 100:  # Success = fast response
            self.successes[backend] += 1
        else:
            self.failures[backend] += 1

    def get_backend_stats(self):
        """Get current estimates for each backend"""
        stats = {}

        for backend in self.backends:
            # Expected success rate (mean of Beta distribution)
            success_rate = self.successes[backend] / (
                self.successes[backend] + self.failures[backend]
            )

            # Confidence interval
            alpha = self.successes[backend]
            beta = self.failures[backend]

            # 95% credible interval
            lower = scipy.stats.beta.ppf(0.025, alpha, beta)
            upper = scipy.stats.beta.ppf(0.975, alpha, beta)

            stats[backend] = {
                'success_rate': success_rate,
                'confidence_interval': (lower, upper),
                'total_requests': alpha + beta - 2
            }

        return stats

class ContextualBanditLoadBalancer:
    """Consider context (user location, request type) in routing"""

    def __init__(self, backends, contexts):
        self.backends = backends
        self.contexts = contexts  # e.g., ['mobile', 'desktop', 'api']

        # Maintain separate stats per context
        self.context_bandits = {
            context: ThompsonSamplingLoadBalancer(backends)
            for context in contexts
        }

    def select_backend(self, request_context):
        """Route based on request context"""
        # Identify context
        context = self.classify_context(request_context)

        # Use appropriate bandit
        if context in self.context_bandits:
            return self.context_bandits[context].select_backend()
        else:
            # Unknown context, use uniform random
            return random.choice(self.backends), {}

    def classify_context(self, request_context):
        """Classify request into context bucket"""
        if request_context.get('is_mobile'):
            return 'mobile'
        elif request_context.get('is_api'):
            return 'api'
        else:
            return 'desktop'
```

## Learning System Implementations

### 1. Anomaly Detection in Metrics

```python
class MetricAnomalyDetector:
    def __init__(self, sensitivity=3):
        self.sensitivity = sensitivity  # Number of standard deviations
        self.models = {}

    class TimeSeriesModel:
        def __init__(self):
            self.values = []
            self.timestamps = []
            self.seasonal_pattern = None
            self.trend = None

        def add_point(self, timestamp, value):
            self.values.append(value)
            self.timestamps.append(timestamp)

            # Keep only recent data (e.g., 2 weeks)
            cutoff = timestamp - (14 * 24 * 3600)
            while self.timestamps and self.timestamps[0] < cutoff:
                self.timestamps.pop(0)
                self.values.pop(0)

            # Retrain periodically
            if len(self.values) > 100 and len(self.values) % 100 == 0:
                self.train()

        def train(self):
            """Decompose time series into trend + seasonal + residual"""
            if len(self.values) < 48:  # Need at least 2 days
                return

            # Simple decomposition
            # 1. Extract trend using moving average
            window = 24  # Daily for hourly data
            trend = []

            for i in range(len(self.values)):
                start = max(0, i - window // 2)
                end = min(len(self.values), i + window // 2)
                trend.append(np.mean(self.values[start:end]))

            self.trend = trend

            # 2. Extract seasonal pattern
            detrended = [v - t for v, t in zip(self.values, trend)]

            # Average by hour of day
            hourly_pattern = defaultdict(list)
            for i, val in enumerate(detrended):
                hour = (self.timestamps[i] // 3600) % 24
                hourly_pattern[hour].append(val)

            self.seasonal_pattern = {
                hour: np.mean(values) if values else 0
                for hour, values in hourly_pattern.items()
            }

        def predict(self, timestamp):
            """Predict expected value at timestamp"""
            if not self.trend or not self.seasonal_pattern:
                # Not enough data, use simple average
                return np.mean(self.values) if self.values else 0

            # Extrapolate trend
            trend_value = self.trend[-1]  # Simple: use last trend value

            # Add seasonal component
            hour = (timestamp // 3600) % 24
            seasonal_value = self.seasonal_pattern.get(hour, 0)

            return trend_value + seasonal_value

        def is_anomaly(self, timestamp, value):
            """Check if value is anomalous"""
            if len(self.values) < 10:
                return False  # Not enough data

            predicted = self.predict(timestamp)

            # Calculate residuals for recent points
            recent_residuals = []
            for i in range(max(0, len(self.values) - 100), len(self.values)):
                pred = self.predict(self.timestamps[i])
                residual = self.values[i] - pred
                recent_residuals.append(residual)

            # Anomaly if outside N standard deviations
            std_dev = np.std(recent_residuals) if recent_residuals else 1
            residual = value - predicted

            return abs(residual) > 3 * std_dev

    def check_metric(self, metric_name, timestamp, value):
        """Check if metric value is anomalous"""
        if metric_name not in self.models:
            self.models[metric_name] = self.TimeSeriesModel()

        model = self.models[metric_name]
        is_anomaly = model.is_anomaly(timestamp, value)

        # Add point after checking (to not bias detection)
        model.add_point(timestamp, value)

        if is_anomaly:
            return {
                'is_anomaly': True,
                'expected': model.predict(timestamp),
                'actual': value,
                'severity': self.calculate_severity(model, timestamp, value)
            }

        return {'is_anomaly': False}

    def calculate_severity(self, model, timestamp, value):
        """Calculate anomaly severity (0-1)"""
        predicted = model.predict(timestamp)

        # Get recent standard deviation
        recent_values = model.values[-100:] if len(model.values) > 100 else model.values
        std_dev = np.std(recent_values) if recent_values else 1

        # Number of standard deviations away
        z_score = abs(value - predicted) / std_dev if std_dev > 0 else 0

        # Convert to 0-1 scale
        severity = min(1.0, z_score / 10)  # 10 std devs = max severity

        return severity
```

### 2. Intelligent Caching with Learning

```python
class IntelligentCache:
    def __init__(self, max_size):
        self.max_size = max_size
        self.cache = {}
        self.access_history = defaultdict(list)
        self.predictor = CachePredictor()

    def get(self, key):
        """Get value from cache"""
        timestamp = time.time()

        if key in self.cache:
            # Record hit
            self.access_history[key].append(timestamp)
            self.cache[key]['last_access'] = timestamp
            self.cache[key]['access_count'] += 1

            return self.cache[key]['value']

        # Record miss
        self.predictor.record_miss(key, timestamp)
        return None

    def put(self, key, value, cost=1):
        """Put value in cache with eviction if needed"""
        if len(self.cache) >= self.max_size:
            self.evict()

        self.cache[key] = {
            'value': value,
            'cost': cost,  # Cost to regenerate
            'size': len(str(value)),
            'insert_time': time.time(),
            'last_access': time.time(),
            'access_count': 0,
            'predicted_reuse': self.predictor.predict_reuse_probability(key)
        }

    def evict(self):
        """Evict based on learned patterns"""
        # Score each cached item
        scores = {}

        for key, item in self.cache.items():
            # Combine multiple factors
            recency = time.time() - item['last_access']
            frequency = item['access_count']

            # Learned reuse probability
            reuse_prob = self.predictor.predict_reuse_probability(key)

            # Cost-aware scoring
            # Higher score = more valuable to keep
            score = (
                frequency * 0.3 +
                (1 / (recency + 1)) * 0.2 +
                reuse_prob * 0.3 +
                (item['cost'] / item['size']) * 0.2  # Value density
            )

            scores[key] = score

        # Evict lowest scoring item
        evict_key = min(scores, key=scores.get)

        # Learn from eviction
        self.predictor.record_eviction(
            evict_key,
            self.cache[evict_key],
            was_accessed_again=False  # Will update if accessed later
        )

        del self.cache[evict_key]

class CachePredictor:
    """Learn cache access patterns"""

    def __init__(self):
        self.feature_extractors = {
            'hour_of_day': lambda k, t: datetime.fromtimestamp(t).hour,
            'day_of_week': lambda k, t: datetime.fromtimestamp(t).weekday(),
            'key_prefix': lambda k, t: k.split(':')[0] if ':' in k else 'default',
            'key_length': lambda k, t: len(k)
        }

        self.access_patterns = defaultdict(lambda: defaultdict(list))

    def predict_reuse_probability(self, key):
        """Predict probability that key will be accessed again soon"""
        features = self.extract_features(key, time.time())

        # Look for similar access patterns
        pattern_key = (features['key_prefix'], features['hour_of_day'])

        if pattern_key in self.access_patterns:
            # Calculate reuse probability from historical data
            reuse_intervals = self.access_patterns[pattern_key]['reuse_intervals']

            if reuse_intervals:
                # Probability of reuse within 5 minutes
                reuses_within_5min = sum(1 for i in reuse_intervals if i < 300)
                prob = reuses_within_5min / len(reuse_intervals)
                return prob

        # Default probability for unknown patterns
        return 0.5

    def extract_features(self, key, timestamp):
        """Extract features for learning"""
        return {
            name: extractor(key, timestamp)
            for name, extractor in self.feature_extractors.items()
        }
```

## Key Takeaways

1. **Learning systems adapt to changing conditions** - Static rules eventually fail

2. **Exploration vs exploitation** - Must try new things to learn

3. **Feature engineering matters** - Good features enable good predictions

4. **Ensemble methods win** - Multiple models better than one

5. **Feedback loops can destabilize** - Monitor for negative spirals

Remember: Intelligence in distributed systems means learning from the past to make better decisions in the future. Start simple and add sophistication as you learn what matters.
