#!/usr/bin/env python3
"""
Circuit Breaker with Advanced Metrics Collection
Comprehensive monitoring और analytics के लिए detailed metrics

Production systems में proper monitoring essential है
यह implementation detailed metrics collect करती है performance analysis के लिए
"""

import time
import threading
import json
import sqlite3
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import uuid
import os


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"           # Incrementing count (requests, failures)
    GAUGE = "gauge"              # Current value (active connections, queue size)
    HISTOGRAM = "histogram"       # Distribution of values (response times)
    TIMER = "timer"              # Timing measurements
    PERCENTAGE = "percentage"     # Percentage values (success rate, error rate)


class TimeWindow(Enum):
    """Time windows for metric aggregation"""
    SECOND = "1s"
    MINUTE = "1m" 
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"


@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass 
class CircuitBreakerMetrics:
    """Comprehensive circuit breaker metrics"""
    # Basic counters
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_open_events: int = 0
    circuit_close_events: int = 0
    circuit_half_open_events: int = 0
    
    # Timing metrics
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # State tracking
    time_in_closed: float = 0.0
    time_in_open: float = 0.0
    time_in_half_open: float = 0.0
    
    # Recent metrics (sliding window)
    recent_success_rate: float = 0.0
    recent_failure_rate: float = 0.0
    recent_avg_response_time: float = 0.0
    
    # Percentiles
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    
    # Error breakdown
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Health score (0-100)
    health_score: float = 100.0


class MetricsCollector:
    """
    Advanced metrics collection system
    Real-time metrics collection और historical data storage
    """
    
    def __init__(
        self,
        name: str,
        db_path: Optional[str] = None,
        max_memory_points: int = 10000,
        enable_percentiles: bool = True
    ):
        self.name = name
        self.max_memory_points = max_memory_points
        self.enable_percentiles = enable_percentiles
        
        # In-memory storage for recent metrics
        self.metric_points: deque = deque(maxlen=max_memory_points)
        self.response_times: deque = deque(maxlen=1000)  # For percentile calculation
        
        # Database storage for historical data
        self.db_path = db_path or f"{name}_metrics.db"
        self._init_database()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Background thread for metrics processing
        self._stop_background_thread = threading.Event()
        self._background_thread = threading.Thread(target=self._background_processor)
        self._background_thread.daemon = True
        self._background_thread.start()
        
        print(f"📊 Metrics Collector '{name}' initialized")
        print(f"   - Database: {self.db_path}")
        print(f"   - Max memory points: {max_memory_points}")
        print(f"   - Percentiles enabled: {enable_percentiles}")
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    labels TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                ON metrics(name, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
    
    def record_metric(
        self, 
        name: str, 
        value: float, 
        metric_type: MetricType = MetricType.GAUGE,
        labels: Dict[str, str] = None,
        persist: bool = True
    ):
        """Record a single metric point"""
        timestamp = datetime.now()
        labels = labels or {}
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=timestamp,
            labels=labels,
            metric_type=metric_type
        )
        
        with self._lock:
            # Add to in-memory storage
            self.metric_points.append(metric_point)
            
            # Add response times for percentile calculation
            if name.endswith('_response_time') or name.endswith('_duration'):
                self.response_times.append(value)
        
        # Persist to database if enabled
        if persist:
            self._persist_metric(metric_point)
    
    def _persist_metric(self, metric_point: MetricPoint):
        """Persist metric point to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO metrics (name, value, timestamp, metric_type, labels)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric_point.name,
                    metric_point.value,
                    metric_point.timestamp.isoformat(),
                    metric_point.metric_type.value,
                    json.dumps(metric_point.labels)
                ))
        except Exception as e:
            print(f"⚠️  Failed to persist metric: {e}")
    
    def increment_counter(self, name: str, labels: Dict[str, str] = None, amount: float = 1.0):
        """Increment a counter metric"""
        self.record_metric(name, amount, MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        self.record_metric(name, value, MetricType.GAUGE, labels)
    
    def record_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Record a timing measurement"""
        self.record_metric(name, duration, MetricType.TIMER, labels)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        self.record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    def get_recent_metrics(self, time_window: timedelta = timedelta(minutes=5)) -> List[MetricPoint]:
        """Get metrics from recent time window"""
        cutoff_time = datetime.now() - time_window
        
        with self._lock:
            return [
                point for point in self.metric_points 
                if point.timestamp >= cutoff_time
            ]
    
    def get_metrics_by_name(self, name: str, time_window: timedelta = timedelta(hours=1)) -> List[MetricPoint]:
        """Get metrics for specific name"""
        recent_metrics = self.get_recent_metrics(time_window)
        return [point for point in recent_metrics if point.name == name]
    
    def calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for given values"""
        if not values or not self.enable_percentiles:
            return {}
        
        sorted_values = sorted(values)
        
        def percentile(data: List[float], p: float) -> float:
            if not data:
                return 0.0
            k = (len(data) - 1) * p
            f = int(k)
            c = k - f
            if f == len(data) - 1:
                return data[f]
            return data[f] * (1 - c) + data[f + 1] * c
        
        return {
            'p50': percentile(sorted_values, 0.5),
            'p75': percentile(sorted_values, 0.75),
            'p90': percentile(sorted_values, 0.9),
            'p95': percentile(sorted_values, 0.95),
            'p99': percentile(sorted_values, 0.99)
        }
    
    def get_aggregated_metrics(self, time_window: timedelta = timedelta(minutes=5)) -> Dict[str, Any]:
        """Get aggregated metrics for time window"""
        recent_metrics = self.get_recent_metrics(time_window)
        
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for point in recent_metrics:
            metrics_by_name[point.name].append(point.value)
        
        aggregated = {}
        
        for metric_name, values in metrics_by_name.items():
            if not values:
                continue
            
            agg_data = {
                'count': len(values),
                'sum': sum(values),
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'last': values[-1] if values else 0
            }
            
            # Add standard deviation if we have enough data points
            if len(values) > 1:
                agg_data['stddev'] = statistics.stdev(values)
            
            # Add percentiles for timing metrics
            if (metric_name.endswith('_time') or 
                metric_name.endswith('_duration') or
                metric_name.endswith('_latency')):
                percentiles = self.calculate_percentiles(values)
                agg_data.update(percentiles)
            
            aggregated[metric_name] = agg_data
        
        return aggregated
    
    def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        aggregated = self.get_aggregated_metrics()
        prometheus_output = []
        
        for metric_name, data in aggregated.items():
            # Counter metrics
            if '_total' in metric_name or '_count' in metric_name:
                prometheus_output.append(f"# TYPE {metric_name} counter")
                prometheus_output.append(f"{metric_name} {data['sum']}")
            
            # Gauge metrics
            elif '_current' in metric_name or '_active' in metric_name:
                prometheus_output.append(f"# TYPE {metric_name} gauge")
                prometheus_output.append(f"{metric_name} {data['last']}")
            
            # Histogram metrics (response times)
            elif '_time' in metric_name or '_duration' in metric_name:
                prometheus_output.append(f"# TYPE {metric_name} histogram")
                prometheus_output.append(f"{metric_name}_count {data['count']}")
                prometheus_output.append(f"{metric_name}_sum {data['sum']}")
                
                # Add percentile buckets if available
                if 'p50' in data:
                    for p in ['p50', 'p75', 'p90', 'p95', 'p99']:
                        if p in data:
                            prometheus_output.append(f"{metric_name}{{quantile=\"0.{p[1:]}\"}} {data[p]}")
        
        return '\n'.join(prometheus_output)
    
    def _background_processor(self):
        """Background thread for processing metrics"""
        while not self._stop_background_thread.wait(60):  # Process every minute
            try:
                self._cleanup_old_metrics()
                self._calculate_derived_metrics()
            except Exception as e:
                print(f"⚠️  Background processing error: {e}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics from database"""
        cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM metrics 
                    WHERE timestamp < ? AND name NOT LIKE '%_daily_%'
                """, (cutoff_date,))
        except Exception as e:
            print(f"⚠️  Failed to cleanup old metrics: {e}")
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics like rates, trends"""
        # This could include calculations like:
        # - Request rate per second
        # - Error rate trends
        # - Performance degradation detection
        pass
    
    def shutdown(self):
        """Shutdown metrics collector"""
        self._stop_background_thread.set()
        if self._background_thread.is_alive():
            self._background_thread.join(timeout=5)
        print(f"📊 Metrics Collector '{self.name}' shutdown")


class MetricsCircuitBreaker:
    """
    Circuit Breaker with comprehensive metrics collection
    Production-grade monitoring और alerting के लिए
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        metrics_db_path: Optional[str] = None
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        # Circuit state
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.state_changed_time = datetime.now()
        
        # Metrics collection
        self.metrics_collector = MetricsCollector(
            name=f"circuit_breaker_{name}",
            db_path=metrics_db_path
        )
        
        # Circuit breaker specific metrics
        self.cb_metrics = CircuitBreakerMetrics()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize baseline metrics
        self._record_state_change("CLOSED", "INITIALIZATION")
        
        print(f"📊 Metrics Circuit Breaker '{name}' initialized")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with comprehensive metrics collection"""
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Record request start
        self.metrics_collector.increment_counter(
            "requests_total",
            labels={"circuit": self.name, "request_id": request_id}
        )
        
        with self._lock:
            # Check circuit state
            if self._should_reject_request():
                self._record_rejection(request_id)
                raise CircuitBreakerOpenError(f"Circuit '{self.name}' is OPEN")
        
        # Execute function with detailed timing
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success metrics
            self._record_success(request_id, execution_time)
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure metrics
            self._record_failure(request_id, e, execution_time)
            
            raise e
    
    def _should_reject_request(self) -> bool:
        """Check if request should be rejected with state transition tracking"""
        current_time = time.time()
        
        if self.state == "CLOSED":
            return False
        
        if self.state == "OPEN":
            if self.last_failure_time and (current_time - self.last_failure_time) >= self.recovery_timeout:
                self._transition_to_half_open()
                return False
            return True
        
        # HALF_OPEN state
        return False
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state"""
        old_state = self.state
        self.state = "HALF_OPEN"
        self._record_state_change(old_state, "HALF_OPEN")
        print(f"🟡 Circuit '{self.name}' moved to HALF_OPEN")
    
    def _transition_to_open(self, reason: str):
        """Transition circuit to open state"""
        old_state = self.state
        self.state = "OPEN"
        self.last_failure_time = time.time()
        self._record_state_change(old_state, "OPEN", reason)
        print(f"🔴 Circuit '{self.name}' OPENED: {reason}")
    
    def _transition_to_closed(self, reason: str):
        """Transition circuit to closed state"""
        old_state = self.state
        self.state = "CLOSED"
        self.failure_count = 0
        self._record_state_change(old_state, "CLOSED", reason)
        print(f"✅ Circuit '{self.name}' CLOSED: {reason}")
    
    def _record_state_change(self, from_state: str, to_state: str, reason: str = ""):
        """Record circuit state transitions"""
        now = datetime.now()
        time_in_state = (now - self.state_changed_time).total_seconds()
        
        # Update time spent in previous state
        if from_state == "CLOSED":
            self.cb_metrics.time_in_closed += time_in_state
        elif from_state == "OPEN":
            self.cb_metrics.time_in_open += time_in_state
        elif from_state == "HALF_OPEN":
            self.cb_metrics.time_in_half_open += time_in_state
        
        # Record state transition metrics
        self.metrics_collector.increment_counter(
            f"state_transitions_total",
            labels={
                "circuit": self.name,
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason
            }
        )
        
        # Update event counters
        if to_state == "OPEN":
            self.cb_metrics.circuit_open_events += 1
        elif to_state == "CLOSED":
            self.cb_metrics.circuit_close_events += 1
        elif to_state == "HALF_OPEN":
            self.cb_metrics.circuit_half_open_events += 1
        
        # Record current state gauge
        state_value = {"CLOSED": 0, "HALF_OPEN": 1, "OPEN": 2}.get(to_state, 0)
        self.metrics_collector.set_gauge(
            "circuit_state",
            state_value,
            labels={"circuit": self.name}
        )
        
        self.state_changed_time = now
    
    def _record_success(self, request_id: str, execution_time: float):
        """Record successful request metrics"""
        # Update basic counters
        self.cb_metrics.total_requests += 1
        self.cb_metrics.successful_requests += 1
        
        # Update timing metrics
        self.cb_metrics.total_response_time += execution_time
        self.cb_metrics.min_response_time = min(self.cb_metrics.min_response_time, execution_time)
        self.cb_metrics.max_response_time = max(self.cb_metrics.max_response_time, execution_time)
        
        # Record detailed metrics
        self.metrics_collector.increment_counter(
            "requests_successful_total",
            labels={"circuit": self.name}
        )
        
        self.metrics_collector.record_timer(
            "request_duration_seconds",
            execution_time,
            labels={"circuit": self.name, "status": "success"}
        )
        
        # Calculate and record success rate
        success_rate = (self.cb_metrics.successful_requests / self.cb_metrics.total_requests) * 100
        self.metrics_collector.set_gauge(
            "success_rate_percent",
            success_rate,
            labels={"circuit": self.name}
        )
        
        # Handle circuit state transitions on success
        if self.state == "HALF_OPEN":
            # Multiple successes needed to close circuit
            if self.cb_metrics.successful_requests % 3 == 0:  # Every 3rd success
                self._transition_to_closed("Multiple successful requests in half-open")
        elif self.state == "CLOSED":
            # Reset failure count on success
            self.failure_count = 0
        
        # Update health score
        self._calculate_health_score()
        
        print(f"✅ Request {request_id}: Success ({execution_time:.3f}s)")
    
    def _record_failure(self, request_id: str, exception: Exception, execution_time: float):
        """Record failed request metrics"""
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Update basic counters
        self.cb_metrics.total_requests += 1
        self.cb_metrics.failed_requests += 1
        self.failure_count += 1
        
        # Update error breakdown
        if error_type not in self.cb_metrics.error_types:
            self.cb_metrics.error_types[error_type] = 0
        self.cb_metrics.error_types[error_type] += 1
        
        # Record detailed metrics
        self.metrics_collector.increment_counter(
            "requests_failed_total",
            labels={"circuit": self.name, "error_type": error_type}
        )
        
        self.metrics_collector.record_timer(
            "request_duration_seconds",
            execution_time,
            labels={"circuit": self.name, "status": "failure"}
        )
        
        # Calculate and record failure rate
        failure_rate = (self.cb_metrics.failed_requests / self.cb_metrics.total_requests) * 100
        self.metrics_collector.set_gauge(
            "failure_rate_percent",
            failure_rate,
            labels={"circuit": self.name}
        )
        
        # Record failure count
        self.metrics_collector.set_gauge(
            "consecutive_failures",
            self.failure_count,
            labels={"circuit": self.name}
        )
        
        # Handle circuit state transitions on failure
        if self.state == "CLOSED" and self.failure_count >= self.failure_threshold:
            self._transition_to_open(f"Failure threshold reached: {self.failure_count}")
        elif self.state == "HALF_OPEN":
            self._transition_to_open("Failure in half-open state")
        
        # Update health score
        self._calculate_health_score()
        
        print(f"❌ Request {request_id}: Failed - {error_type} ({execution_time:.3f}s)")
    
    def _record_rejection(self, request_id: str):
        """Record rejected request due to open circuit"""
        self.metrics_collector.increment_counter(
            "requests_rejected_total",
            labels={"circuit": self.name, "reason": "circuit_open"}
        )
        
        print(f"🚫 Request {request_id}: Rejected - Circuit is OPEN")
    
    def _calculate_health_score(self):
        """Calculate overall health score (0-100)"""
        if self.cb_metrics.total_requests == 0:
            self.cb_metrics.health_score = 100.0
            return
        
        # Base score from success rate
        success_rate = (self.cb_metrics.successful_requests / self.cb_metrics.total_requests) * 100
        health_score = success_rate
        
        # Penalize for circuit being open
        if self.state == "OPEN":
            health_score *= 0.5  # 50% penalty for open circuit
        elif self.state == "HALF_OPEN":
            health_score *= 0.8  # 20% penalty for half-open circuit
        
        # Penalize for high response times
        if self.cb_metrics.total_requests > 0:
            avg_response_time = self.cb_metrics.total_response_time / self.cb_metrics.total_requests
            if avg_response_time > 5.0:  # More than 5 seconds
                health_score *= 0.7
            elif avg_response_time > 2.0:  # More than 2 seconds
                health_score *= 0.9
        
        self.cb_metrics.health_score = max(0.0, min(100.0, health_score))
        
        # Record health score metric
        self.metrics_collector.set_gauge(
            "health_score",
            self.cb_metrics.health_score,
            labels={"circuit": self.name}
        )
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get all metrics in comprehensive format"""
        # Calculate recent metrics
        recent_metrics = self.metrics_collector.get_aggregated_metrics(timedelta(minutes=5))
        
        # Calculate averages
        avg_response_time = 0.0
        if self.cb_metrics.total_requests > 0:
            avg_response_time = self.cb_metrics.total_response_time / self.cb_metrics.total_requests
        
        return {
            "circuit_name": self.name,
            "current_state": self.state,
            "timestamp": datetime.now().isoformat(),
            
            # Basic metrics
            "requests": {
                "total": self.cb_metrics.total_requests,
                "successful": self.cb_metrics.successful_requests,
                "failed": self.cb_metrics.failed_requests,
                "success_rate": round((self.cb_metrics.successful_requests / max(self.cb_metrics.total_requests, 1)) * 100, 2)
            },
            
            # Timing metrics
            "response_times": {
                "average": round(avg_response_time, 3),
                "min": round(self.cb_metrics.min_response_time, 3) if self.cb_metrics.min_response_time != float('inf') else 0,
                "max": round(self.cb_metrics.max_response_time, 3)
            },
            
            # State metrics
            "circuit_events": {
                "open_events": self.cb_metrics.circuit_open_events,
                "close_events": self.cb_metrics.circuit_close_events,
                "half_open_events": self.cb_metrics.circuit_half_open_events
            },
            
            # Time in states
            "state_durations": {
                "closed": round(self.cb_metrics.time_in_closed, 2),
                "open": round(self.cb_metrics.time_in_open, 2), 
                "half_open": round(self.cb_metrics.time_in_half_open, 2)
            },
            
            # Error breakdown
            "error_types": dict(self.cb_metrics.error_types),
            
            # Health score
            "health_score": round(self.cb_metrics.health_score, 1),
            
            # Recent aggregated metrics
            "recent_metrics": recent_metrics
        }
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        return self.metrics_collector.export_metrics_prometheus()
    
    def get_metrics_for_dashboard(self) -> Dict[str, Any]:
        """Get metrics formatted for dashboard display"""
        metrics = self.get_comprehensive_metrics()
        
        return {
            "circuit_name": metrics["circuit_name"],
            "status": {
                "state": metrics["current_state"],
                "health_score": metrics["health_score"],
                "color": self._get_status_color(metrics["current_state"], metrics["health_score"])
            },
            "throughput": {
                "total_requests": metrics["requests"]["total"],
                "success_rate": metrics["requests"]["success_rate"],
                "failure_count": metrics["requests"]["failed"]
            },
            "performance": {
                "avg_response_time": metrics["response_times"]["average"],
                "min_response_time": metrics["response_times"]["min"],
                "max_response_time": metrics["response_times"]["max"]
            },
            "incidents": {
                "circuit_opens": metrics["circuit_events"]["open_events"],
                "total_downtime": metrics["state_durations"]["open"],
                "recovery_count": metrics["circuit_events"]["close_events"]
            },
            "top_errors": sorted(
                metrics["error_types"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def _get_status_color(self, state: str, health_score: float) -> str:
        """Get status color for dashboard"""
        if state == "OPEN":
            return "red"
        elif state == "HALF_OPEN":
            return "yellow"
        elif health_score >= 90:
            return "green"
        elif health_score >= 70:
            return "yellow"
        else:
            return "orange"
    
    def shutdown(self):
        """Shutdown circuit breaker and metrics collection"""
        self.metrics_collector.shutdown()
        print(f"📊 Metrics Circuit Breaker '{self.name}' shutdown")


class CircuitBreakerOpenError(Exception):
    """Circuit breaker is open"""
    pass


# Example services for metrics testing
def payment_service(payment_id: str, amount: float, failure_rate: float = 0.3) -> Dict[str, Any]:
    """Payment service with configurable failure rate"""
    import random
    
    # Simulate variable response times
    response_time = random.uniform(0.5, 3.0)
    time.sleep(response_time)
    
    if random.random() < failure_rate:
        errors = [
            "PaymentGatewayTimeout",
            "InsufficientFunds", 
            "CardExpired",
            "NetworkError",
            "ServiceUnavailable"
        ]
        raise Exception(random.choice(errors))
    
    return {
        "payment_id": payment_id,
        "amount": amount,
        "status": "completed",
        "processing_time": response_time
    }


def test_metrics_circuit_breaker():
    """Test circuit breaker with comprehensive metrics"""
    print("🧪 Testing Metrics Circuit Breaker")
    print("=" * 70)
    
    # Create circuit breaker with metrics
    cb = MetricsCircuitBreaker(
        name="payment_service",
        failure_threshold=3,
        recovery_timeout=10.0
    )
    
    print("\n📊 Phase 1: Normal operation with mixed results")
    print("-" * 60)
    
    # Generate varied traffic pattern
    for i in range(20):
        try:
            # Vary failure rate over time
            failure_rate = 0.1 + (i / 20) * 0.6  # Gradually increase failure rate
            result = cb.call(payment_service, f"PAY_{i+1}", 100.0 + (i * 10), failure_rate)
            print(f"✅ Payment {i+1}: Success")
        except CircuitBreakerOpenError as e:
            print(f"🚫 Payment {i+1}: Circuit blocked")
        except Exception as e:
            print(f"❌ Payment {i+1}: {type(e).__name__}")
        
        # Show periodic metrics
        if (i + 1) % 5 == 0:
            dashboard_metrics = cb.get_metrics_for_dashboard()
            print(f"\n📈 Metrics Update (Request {i+1}):")
            print(f"   State: {dashboard_metrics['status']['state']} "
                  f"(Health: {dashboard_metrics['status']['health_score']})")
            print(f"   Success Rate: {dashboard_metrics['throughput']['success_rate']:.1f}%")
            print(f"   Avg Response Time: {dashboard_metrics['performance']['avg_response_time']:.3f}s")
            print()
        
        time.sleep(0.5)
    
    print("\n📊 Phase 2: Circuit recovery testing")
    print("-" * 60)
    
    # Wait for circuit recovery
    if cb.state == "OPEN":
        print("Waiting for circuit recovery...")
        time.sleep(11)
    
    # Test recovery with improved service
    for i in range(10):
        try:
            result = cb.call(payment_service, f"RECOVERY_{i+1}", 200.0, 0.1)  # Low failure rate
            print(f"✅ Recovery {i+1}: Success")
        except Exception as e:
            print(f"❌ Recovery {i+1}: {type(e).__name__}")
        
        time.sleep(0.5)
    
    print("\n📊 Phase 3: Load testing for performance metrics")
    print("-" * 60)
    
    # Quick burst of requests
    import concurrent.futures
    
    def make_payment_request(payment_id: int):
        try:
            result = cb.call(payment_service, f"LOAD_{payment_id}", 50.0, 0.2)
            return f"✅ Load {payment_id}: Success"
        except Exception as e:
            return f"❌ Load {payment_id}: {type(e).__name__}"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_payment_request, i) for i in range(1, 21)]
        
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
    
    print("\n📈 Final Comprehensive Metrics:")
    print("=" * 60)
    final_metrics = cb.get_comprehensive_metrics()
    print(json.dumps(final_metrics, indent=2, default=str))
    
    print("\n📊 Dashboard View:")
    print("=" * 40)
    dashboard = cb.get_metrics_for_dashboard()
    print(json.dumps(dashboard, indent=2, default=str))
    
    print("\n📋 Prometheus Export (Sample):")
    print("=" * 40)
    prometheus_metrics = cb.export_prometheus_metrics()
    print(prometheus_metrics[:500] + "..." if len(prometheus_metrics) > 500 else prometheus_metrics)
    
    # Cleanup
    cb.shutdown()


if __name__ == "__main__":
    test_metrics_circuit_breaker()