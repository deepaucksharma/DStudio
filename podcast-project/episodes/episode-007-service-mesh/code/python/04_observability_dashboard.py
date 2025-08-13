#!/usr/bin/env python3
"""
Service Mesh Observability Dashboard
Mumbai Traffic Control Dashboard Inspired

Context:
PhonePe/Paytm जैसे services के लिए comprehensive observability
जैसे Mumbai traffic control room में सभी signals और routes की monitoring होती है

Features:
- Real-time metrics collection
- Distributed tracing
- Service health monitoring
- Alert management
- Hindi-friendly dashboard
"""

import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import threading
import queue
import statistics
from flask import Flask, jsonify, render_template_string
import requests
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import jaeger_client

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [मुंबई-Observatory] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mumbai-observability.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MumbaiObservability')

@dataclass
class ServiceMetrics:
    """Service metrics container"""
    service_name: str
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    active_connections: int = 0
    circuit_breaker_state: str = "CLOSED"
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        if self.request_count == 0:
            return 100.0
        return ((self.request_count - self.error_count) / self.request_count) * 100
    
    @property  
    def average_response_time(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count

@dataclass
class TraceSpan:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    service_name: str
    metric: str
    threshold: float
    comparison: str  # "gt", "lt", "eq"
    duration: int    # seconds
    severity: str    # "critical", "warning", "info"
    enabled: bool = True

class PrometheusMetricsCollector:
    """
    Prometheus metrics collector
    Mumbai traffic data collection system की तरह
    """
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Define metrics
        self.request_counter = Counter(
            'mumbai_mesh_requests_total',
            'Total requests processed',
            ['service', 'method', 'status', 'zone'],
            registry=self.registry
        )
        
        self.response_time_histogram = Histogram(
            'mumbai_mesh_response_time_seconds',
            'Response time distribution',
            ['service', 'method'],
            registry=self.registry,
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.active_connections_gauge = Gauge(
            'mumbai_mesh_active_connections',
            'Active connections to service',
            ['service', 'instance'],
            registry=self.registry
        )
        
        self.circuit_breaker_state_gauge = Gauge(
            'mumbai_mesh_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 0.5=half-open)',
            ['service'],
            registry=self.registry
        )
        
        logger.info("📊 Prometheus metrics collector initialized")
    
    def record_request(self, service: str, method: str, status: str, 
                      response_time: float, zone: str = "mumbai"):
        """Record a request"""
        self.request_counter.labels(
            service=service, 
            method=method, 
            status=status, 
            zone=zone
        ).inc()
        
        self.response_time_histogram.labels(
            service=service,
            method=method
        ).observe(response_time)
    
    def update_active_connections(self, service: str, instance: str, count: int):
        """Update active connections gauge"""
        self.active_connections_gauge.labels(
            service=service,
            instance=instance
        ).set(count)
    
    def update_circuit_breaker_state(self, service: str, state: str):
        """Update circuit breaker state"""
        state_value = {"CLOSED": 0, "OPEN": 1, "HALF_OPEN": 0.5}.get(state, 0)
        self.circuit_breaker_state_gauge.labels(service=service).set(state_value)

class JaegerTracingCollector:
    """
    Jaeger distributed tracing collector
    Mumbai route tracking system की तरह
    """
    
    def __init__(self, service_name: str = "mumbai-mesh-dashboard"):
        # Configure Jaeger tracer
        config = jaeger_client.Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'logging': True,
                'local_agent': {
                    'reporting_host': 'localhost',
                    'reporting_port': 14268,
                },
            },
            service_name=service_name,
        )
        
        self.tracer = config.initialize_tracer()
        self.active_traces: Dict[str, TraceSpan] = {}
        
        logger.info("🔍 Jaeger tracing collector initialized")
    
    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None,
                  service_name: str = "unknown", tags: Dict[str, Any] = None) -> TraceSpan:
        """Start a new trace span"""
        span = self.tracer.start_span(operation_name)
        
        # Add Mumbai context tags
        span.set_tag("service.name", service_name)
        span.set_tag("span.kind", "server")
        span.set_tag("location", "mumbai")
        
        if tags:
            for key, value in tags.items():
                span.set_tag(key, value)
        
        # Create TraceSpan object
        trace_span = TraceSpan(
            trace_id=str(span.trace_id),
            span_id=str(span.span_id),
            parent_span_id=parent_span_id,
            service_name=service_name,
            operation_name=operation_name,
            start_time=datetime.now(),
            duration_ms=0,
            tags=tags or {}
        )
        
        self.active_traces[trace_span.span_id] = trace_span
        return trace_span
    
    def finish_span(self, span_id: str, status: str = "ok", logs: List[str] = None):
        """Finish a trace span"""
        if span_id in self.active_traces:
            trace_span = self.active_traces[span_id]
            trace_span.duration_ms = (datetime.now() - trace_span.start_time).total_seconds() * 1000
            
            if logs:
                trace_span.logs.extend(logs)
            
            # Log span completion
            logger.debug("✅ Span completed: %s (%s) - %.2fms", 
                        trace_span.operation_name, trace_span.service_name, 
                        trace_span.duration_ms)
            
            del self.active_traces[span_id]
    
    def get_trace_summary(self, minutes: int = 10) -> Dict[str, Any]:
        """Get trace summary for last N minutes"""
        # This would typically query Jaeger backend
        # For demo, return mock data
        return {
            "total_traces": 1234,
            "services_count": 8,
            "average_trace_duration_ms": 245.6,
            "error_rate": 2.3,
            "top_operations": [
                {"name": "/api/orders", "count": 456, "avg_duration": 120.5},
                {"name": "/api/payments", "count": 234, "avg_duration": 89.2},
                {"name": "/api/restaurants", "count": 189, "avg_duration": 67.8}
            ]
        }

class AlertManager:
    """
    Alert management system
    Mumbai emergency response system की तरह
    """
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_queue = queue.Queue()
        
        # Start alert evaluation thread
        self.evaluation_active = True
        self.evaluation_thread = threading.Thread(target=self._evaluate_alerts)
        self.evaluation_thread.daemon = True
        self.evaluation_thread.start()
        
        logger.info("🚨 Alert manager initialized")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
        logger.info("📋 Alert rule added: %s", rule.name)
    
    def evaluate_metric(self, service_name: str, metric_name: str, value: float):
        """Evaluate metric against alert rules"""
        for rule in self.rules:
            if not rule.enabled or rule.service_name != service_name or rule.metric != metric_name:
                continue
            
            # Check threshold
            triggered = False
            if rule.comparison == "gt" and value > rule.threshold:
                triggered = True
            elif rule.comparison == "lt" and value < rule.threshold:
                triggered = True
            elif rule.comparison == "eq" and value == rule.threshold:
                triggered = True
            
            alert_key = f"{rule.name}_{service_name}"
            
            if triggered:
                if alert_key not in self.active_alerts:
                    # New alert
                    alert = {
                        "rule_name": rule.name,
                        "service_name": service_name,
                        "metric": metric_name,
                        "value": value,
                        "threshold": rule.threshold,
                        "severity": rule.severity,
                        "started_at": datetime.now(),
                        "description": f"मुंबई सेवा {service_name} में {metric_name} = {value} (threshold: {rule.threshold})"
                    }
                    
                    self.active_alerts[alert_key] = alert
                    self.alert_queue.put(alert)
                    
                    logger.warning("🚨 Alert triggered: %s", alert["description"])
            else:
                # Clear alert if it was active
                if alert_key in self.active_alerts:
                    alert = self.active_alerts[alert_key]
                    alert["resolved_at"] = datetime.now()
                    
                    logger.info("✅ Alert resolved: %s", alert["description"])
                    del self.active_alerts[alert_key]
    
    def _evaluate_alerts(self):
        """Background alert evaluation"""
        while self.evaluation_active:
            try:
                time.sleep(30)  # Evaluate every 30 seconds
                # Alert evaluation logic would go here
                # For demo, we just sleep
            except Exception as e:
                logger.error("❌ Alert evaluation error: %s", e)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

class MumbaiObservabilityDashboard:
    """
    Main observability dashboard
    Mumbai traffic control center की तरह central monitoring
    """
    
    def __init__(self):
        self.prometheus = PrometheusMetricsCollector()
        self.jaeger = JaegerTracingCollector()
        self.alert_manager = AlertManager()
        
        # Service metrics storage
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Flask app for web dashboard
        self.app = Flask(__name__)
        self._setup_routes()
        
        # Setup default alert rules
        self._setup_default_alerts()
        
        # Start metrics collection
        self.collection_active = True
        self.collection_thread = threading.Thread(target=self._collect_metrics)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
        logger.info("🎛️ Mumbai observability dashboard initialized")
    
    def _setup_default_alerts(self):
        """Setup default alert rules for Mumbai services"""
        default_rules = [
            AlertRule(
                name="high-error-rate",
                service_name="payment-service",
                metric="error_rate",
                threshold=5.0,
                comparison="gt",
                duration=120,
                severity="critical"
            ),
            AlertRule(
                name="high-response-time",
                service_name="order-service", 
                metric="avg_response_time",
                threshold=1000.0,
                comparison="gt",
                duration=60,
                severity="warning"
            ),
            AlertRule(
                name="circuit-breaker-open",
                service_name="*",  # All services
                metric="circuit_breaker_open",
                threshold=1.0,
                comparison="eq",
                duration=0,
                severity="critical"
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_alert_rule(rule)
    
    def _setup_routes(self):
        """Setup Flask routes for web dashboard"""
        
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML_TEMPLATE)
        
        @self.app.route('/api/metrics')
        def get_metrics():
            """Get current service metrics"""
            metrics_data = {}
            
            for service_name, metrics in self.service_metrics.items():
                metrics_data[service_name] = asdict(metrics)
                
                # Add trend data
                history = list(self.metrics_history[service_name])
                if history:
                    recent_history = history[-10:]  # Last 10 data points
                    metrics_data[service_name]['trends'] = {
                        'success_rate': [h['success_rate'] for h in recent_history],
                        'response_time': [h['avg_response_time'] for h in recent_history],
                        'timestamps': [h['timestamp'] for h in recent_history]
                    }
            
            return jsonify({
                'status': 'success',
                'data': metrics_data,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/traces')
        def get_traces():
            """Get distributed tracing data"""
            trace_summary = self.jaeger.get_trace_summary()
            return jsonify({
                'status': 'success',
                'data': trace_summary,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get active alerts"""
            alerts = self.alert_manager.get_active_alerts()
            return jsonify({
                'status': 'success',
                'data': alerts,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/metrics')
        def prometheus_metrics():
            """Prometheus metrics endpoint"""
            return prometheus_client.generate_latest(self.prometheus.registry)
    
    def record_request(self, service_name: str, method: str, status: str,
                      response_time_ms: float, zone: str = "mumbai"):
        """Record a service request"""
        # Update or create service metrics
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(service_name=service_name)
        
        metrics = self.service_metrics[service_name]
        metrics.request_count += 1
        
        if status.startswith('5') or status == 'error':
            metrics.error_count += 1
        
        metrics.total_response_time += response_time_ms
        metrics.last_updated = datetime.now()
        
        # Record in Prometheus
        self.prometheus.record_request(service_name, method, status, response_time_ms / 1000, zone)
        
        # Evaluate alerts
        self.alert_manager.evaluate_metric(service_name, "error_rate", metrics.success_rate)
        self.alert_manager.evaluate_metric(service_name, "avg_response_time", metrics.average_response_time)
        
        logger.debug("📊 Request recorded: %s %s [%s] %.2fms", 
                    service_name, method, status, response_time_ms)
    
    def update_service_connections(self, service_name: str, instance: str, connections: int):
        """Update active connections for service"""
        if service_name in self.service_metrics:
            self.service_metrics[service_name].active_connections = connections
        
        self.prometheus.update_active_connections(service_name, instance, connections)
    
    def update_circuit_breaker(self, service_name: str, state: str):
        """Update circuit breaker state"""
        if service_name in self.service_metrics:
            self.service_metrics[service_name].circuit_breaker_state = state
        
        self.prometheus.update_circuit_breaker_state(service_name, state)
        
        # Trigger alert if circuit breaker opens
        if state == "OPEN":
            self.alert_manager.evaluate_metric(service_name, "circuit_breaker_open", 1.0)
    
    def _collect_metrics(self):
        """Background metrics collection"""
        while self.collection_active:
            try:
                # Store historical metrics
                timestamp = datetime.now().isoformat()
                
                for service_name, metrics in self.service_metrics.items():
                    history_entry = {
                        'timestamp': timestamp,
                        'success_rate': metrics.success_rate,
                        'avg_response_time': metrics.average_response_time,
                        'request_count': metrics.request_count,
                        'active_connections': metrics.active_connections
                    }
                    
                    self.metrics_history[service_name].append(history_entry)
                
                time.sleep(15)  # Collect every 15 seconds
                
            except Exception as e:
                logger.error("❌ Metrics collection error: %s", e)
                time.sleep(60)
    
    def start_dashboard(self, host: str = '0.0.0.0', port: int = 8080):
        """Start web dashboard"""
        logger.info("🌐 Starting Mumbai observability dashboard at http://%s:%d", host, port)
        self.app.run(host=host, port=port, debug=False, threaded=True)
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary"""
        total_requests = sum(m.request_count for m in self.service_metrics.values())
        total_errors = sum(m.error_count for m in self.service_metrics.values())
        
        overall_success_rate = ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 100
        
        active_alerts = len(self.alert_manager.get_active_alerts())
        
        service_health = {}
        for service_name, metrics in self.service_metrics.items():
            if metrics.success_rate >= 99:
                health = "excellent"
            elif metrics.success_rate >= 95:
                health = "good"
            elif metrics.success_rate >= 90:
                health = "warning"
            else:
                health = "critical"
            
            service_health[service_name] = health
        
        return {
            'overview': {
                'total_services': len(self.service_metrics),
                'total_requests': total_requests,
                'overall_success_rate': round(overall_success_rate, 2),
                'active_alerts': active_alerts,
                'healthy_services': len([h for h in service_health.values() if h in ['excellent', 'good']])
            },
            'service_health': service_health,
            'timestamp': datetime.now().isoformat()
        }

# HTML template for dashboard
DASHBOARD_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚦 Mumbai Service Mesh Observatory</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #ff6b35; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; color: #ff6b35; }
        .metric-label { color: #666; margin-top: 5px; }
        .status-good { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-critical { color: #dc3545; }
        .refresh-btn { background: #ff6b35; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚦 Mumbai Service Mesh Observatory</h1>
        <p>Real-time monitoring dashboard for Mumbai microservices - मुंबई सेवा जाल निगरानी</p>
    </div>
    
    <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
    
    <div id="metrics-container" class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">Loading...</div>
            <div class="metric-label">Initializing Mumbai Observatory</div>
        </div>
    </div>
    
    <script>
        function refreshData() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateDashboard(data.data))
                .catch(error => console.error('Error:', error));
        }
        
        function updateDashboard(services) {
            const container = document.getElementById('metrics-container');
            container.innerHTML = '';
            
            Object.entries(services).forEach(([serviceName, metrics]) => {
                const card = document.createElement('div');
                card.className = 'metric-card';
                
                const statusClass = metrics.success_rate >= 99 ? 'status-good' : 
                                  metrics.success_rate >= 95 ? 'status-warning' : 'status-critical';
                
                card.innerHTML = `
                    <h3>${serviceName}</h3>
                    <div class="metric-value ${statusClass}">${metrics.success_rate.toFixed(1)}%</div>
                    <div class="metric-label">Success Rate</div>
                    <p>Response Time: ${metrics.average_response_time.toFixed(0)}ms</p>
                    <p>Requests: ${metrics.request_count}</p>
                    <p>Circuit Breaker: ${metrics.circuit_breaker_state}</p>
                `;
                
                container.appendChild(card);
            });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        refreshData();
    </script>
</body>
</html>
"""

def main():
    """
    Demo: Mumbai Food Delivery Observability
    Zomato/Swiggy style comprehensive monitoring
    """
    print("🎛️ Mumbai Service Mesh Observability Dashboard")
    print("=" * 55)
    
    # Initialize dashboard
    dashboard = MumbaiObservabilityDashboard()
    
    # Simulate service requests
    print("\n📊 Simulating service requests...")
    
    services = ["order-service", "payment-service", "restaurant-service", "notification-service"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    
    # Generate sample data
    for i in range(50):
        service = services[i % len(services)]
        method = methods[i % len(methods)]
        
        # 90% success rate
        status = "200" if i % 10 != 0 else "500"
        response_time = 50 + (i % 500)  # 50-550ms
        
        dashboard.record_request(service, method, status, response_time)
        
        if i % 10 == 0:
            print(f"  📈 Recorded {i} requests...")
    
    # Update circuit breaker states
    dashboard.update_circuit_breaker("payment-service", "OPEN")
    dashboard.update_service_connections("order-service", "instance-1", 45)
    
    # Show dashboard summary
    print("\n📋 Dashboard Summary:")
    summary = dashboard.get_dashboard_summary()
    
    overview = summary['overview']
    print(f"  Total Services: {overview['total_services']}")
    print(f"  Total Requests: {overview['total_requests']}")
    print(f"  Overall Success Rate: {overview['overall_success_rate']}%")
    print(f"  Active Alerts: {overview['active_alerts']}")
    print(f"  Healthy Services: {overview['healthy_services']}")
    
    print("\n🏥 Service Health Status:")
    for service, health in summary['service_health'].items():
        health_emoji = {"excellent": "✅", "good": "🟢", "warning": "⚠️", "critical": "❌"}
        emoji = health_emoji.get(health, "❓")
        print(f"  {emoji} {service}: {health}")
    
    print(f"\n📊 Metrics available at: http://localhost:8080/metrics")
    print(f"🌐 Dashboard available at: http://localhost:8080/")
    print(f"📡 API endpoints: /api/metrics, /api/traces, /api/alerts")
    
    # Option to start web dashboard
    start_web = input("\n🚀 Start web dashboard? (y/n): ").lower().strip()
    if start_web == 'y':
        print("Starting Mumbai observability dashboard...")
        dashboard.start_dashboard()
    else:
        print("Dashboard initialized but not started. Use dashboard.start_dashboard() to launch.")

if __name__ == "__main__":
    main()