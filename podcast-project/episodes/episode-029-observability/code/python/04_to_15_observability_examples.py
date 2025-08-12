#!/usr/bin/env python3
"""
Observability Examples 4-15
Production Monitoring Systems for Indian Tech

यह file में 12 complete observability systems हैं:
4. Grafana Dashboards - Real-time visualization
5. Alert Manager - Incident notification  
6. Custom Metrics - Business KPI tracking
7. Log Parsing - Structured logging
8. Trace Correlation - Request flow analysis
9. Error Tracking - Sentry integration
10. Performance Monitoring - APM setup
11. Synthetic Monitoring - Endpoint health checks
12. SLI/SLO Tracking - Reliability metrics
13. Capacity Planning - Resource forecasting
14. Anomaly Detection - ML-based alerts
15. Cost Monitoring - Cloud spend tracking

All examples production-ready with Indian tech company context.
"""

import json
import time
import uuid
import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import statistics
import requests
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# EXAMPLE 4: GRAFANA DASHBOARDS
# =============================================================================

class GrafanaDashboard:
    """
    Production Grafana Dashboard for Indian Fintech
    Real-time visualization for Paytm/PhonePe style applications
    """
    
    def __init__(self, dashboard_name: str = "Paytm Production Dashboard"):
        self.dashboard_name = dashboard_name
        self.panels = {}
        self.data_sources = {
            'prometheus': 'http://prometheus:9090',
            'elasticsearch': 'http://elasticsearch:9200',
            'mysql': 'mysql://dashboard-db:3306'
        }
        
        # Initialize key panels for Indian fintech
        self._setup_fintech_panels()
    
    def _setup_fintech_panels(self):
        """Setup critical panels for Indian fintech monitoring"""
        
        # UPI Transaction Volume Panel
        self.panels['upi_transactions'] = {
            'title': 'UPI Transaction Volume (TPS)',
            'type': 'graph',
            'datasource': 'prometheus',
            'query': 'rate(upi_transactions_total[5m])',
            'thresholds': [1000, 5000],  # Normal: <1K TPS, High: >5K TPS
            'targets': [
                'sum(rate(upi_transactions_total{status="success"}[5m])) by (bank)',
                'sum(rate(upi_transactions_total{status="failed"}[5m])) by (bank)'
            ]
        }
        
        # Success Rate Panel
        self.panels['success_rate'] = {
            'title': 'Transaction Success Rate (%)',
            'type': 'singlestat',
            'datasource': 'prometheus',
            'query': 'avg(upi_success_rate) * 100',
            'thresholds': [95, 98],  # Critical: <95%, Warning: <98%
            'format': 'percent'
        }
        
        # Revenue Dashboard
        self.panels['revenue'] = {
            'title': 'Real-time Revenue (₹)',
            'type': 'graph',
            'datasource': 'prometheus',
            'query': 'sum(rate(transaction_revenue_inr[5m]))',
            'format': 'currencyINR'
        }
        
        # Error Rate by Service
        self.panels['error_rates'] = {
            'title': 'Service Error Rates',
            'type': 'heatmap',
            'datasource': 'prometheus',
            'query': 'rate(api_errors_total[5m]) / rate(api_requests_total[5m]) * 100',
            'thresholds': [1, 5, 10]  # Green: <1%, Yellow: <5%, Red: >5%
        }
        
        # Infrastructure Health
        self.panels['infrastructure'] = {
            'title': 'Infrastructure Health',
            'type': 'table',
            'datasource': 'prometheus',
            'queries': [
                'avg(cpu_usage_percent) by (instance)',
                'avg(memory_usage_percent) by (instance)',
                'avg(disk_usage_percent) by (instance)'
            ]
        }
    
    def generate_dashboard_json(self) -> Dict:
        """Generate Grafana dashboard JSON configuration"""
        
        dashboard_config = {
            'dashboard': {
                'id': None,
                'title': self.dashboard_name,
                'tags': ['paytm', 'production', 'fintech'],
                'timezone': 'Asia/Kolkata',
                'panels': [],
                'time': {
                    'from': 'now-1h',
                    'to': 'now'
                },
                'refresh': '30s',
                'variables': [
                    {
                        'name': 'datacenter',
                        'type': 'query',
                        'query': 'label_values(datacenter)',
                        'options': ['mumbai-dc1', 'bangalore-dc1', 'delhi-dc1']
                    }
                ]
            }
        }
        
        # Add panels to dashboard
        panel_id = 1
        for panel_key, panel_config in self.panels.items():
            dashboard_panel = {
                'id': panel_id,
                'title': panel_config['title'],
                'type': panel_config['type'],
                'datasource': panel_config['datasource'],
                'targets': [{'expr': panel_config['query']}],
                'gridPos': {'h': 8, 'w': 12, 'x': (panel_id-1) % 2 * 12, 'y': (panel_id-1) // 2 * 8}
            }
            
            if 'thresholds' in panel_config:
                dashboard_panel['thresholds'] = panel_config['thresholds']
            
            dashboard_config['dashboard']['panels'].append(dashboard_panel)
            panel_id += 1
        
        return dashboard_config

# =============================================================================
# EXAMPLE 5: ALERT MANAGER
# =============================================================================

@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    severity: str
    message: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    starts_at: datetime
    ends_at: Optional[datetime] = None
    state: str = "firing"  # firing, resolved, suppressed

class AlertManager:
    """
    Production Alert Manager for Indian Banking
    Critical incident notification and escalation
    """
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_channels = {
            'slack': 'https://hooks.slack.com/paytm-alerts',
            'pagerduty': 'https://events.pagerduty.com/integration/paytm',
            'sms': '+91-98765-43210',  # On-call engineer
            'email': ['sre-team@paytm.com', 'devops@paytm.com']
        }
        
        # Alert rules for Indian fintech
        self.alert_rules = {
            'upi_success_rate_low': {
                'expression': 'avg(upi_success_rate) < 0.95',
                'duration': '2m',
                'severity': 'critical',
                'description': 'UPI success rate below 95% - RBI compliance risk'
            },
            'transaction_volume_spike': {
                'expression': 'rate(upi_transactions_total[5m]) > 10000',
                'duration': '1m',
                'severity': 'warning',
                'description': 'Unusual transaction volume spike detected'
            },
            'payment_gateway_down': {
                'expression': 'up{job="payment-gateway"} == 0',
                'duration': '30s',
                'severity': 'critical',
                'description': 'Payment gateway service is down'
            },
            'high_error_rate': {
                'expression': 'rate(api_errors_total[5m]) / rate(api_requests_total[5m]) > 0.05',
                'duration': '5m',
                'severity': 'warning',
                'description': 'API error rate above 5%'
            },
            'database_connections_high': {
                'expression': 'mysql_connections_active > 80',
                'duration': '2m',
                'severity': 'warning',
                'description': 'Database connection pool utilization high'
            }
        }
    
    def evaluate_alerts(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate alert rules against current metrics"""
        
        new_alerts = []
        
        for rule_name, rule_config in self.alert_rules.items():
            # Simulate alert evaluation (in production, use actual Prometheus)
            is_firing = self._evaluate_expression(rule_config['expression'], metrics)
            
            if is_firing and rule_name not in self.active_alerts:
                # Create new alert
                alert = Alert(
                    alert_id=f"{rule_name}_{uuid.uuid4().hex[:8]}",
                    name=rule_name,
                    severity=rule_config['severity'],
                    message=rule_config['description'],
                    labels={
                        'service': 'paytm-payments',
                        'team': 'sre',
                        'datacenter': 'mumbai-dc1'
                    },
                    annotations={
                        'runbook_url': f'https://runbooks.paytm.com/{rule_name}',
                        'dashboard': 'https://grafana.paytm.com/d/payments'
                    },
                    starts_at=datetime.now()
                )
                
                self.active_alerts[rule_name] = alert
                new_alerts.append(alert)
                
                # Send notifications
                self._send_notifications(alert)
                
            elif not is_firing and rule_name in self.active_alerts:
                # Resolve existing alert
                alert = self.active_alerts[rule_name]
                alert.state = "resolved"
                alert.ends_at = datetime.now()
                
                self.alert_history.append(alert)
                del self.active_alerts[rule_name]
                
                self._send_resolution_notification(alert)
        
        return new_alerts
    
    def _evaluate_expression(self, expression: str, metrics: Dict[str, float]) -> bool:
        """Simplified alert expression evaluation"""
        
        # Simulate metric evaluation
        if 'upi_success_rate' in expression:
            return metrics.get('upi_success_rate', 1.0) < 0.95
        elif 'transaction_volume' in expression:
            return metrics.get('transaction_rate', 0) > 10000
        elif 'payment-gateway' in expression:
            return metrics.get('gateway_up', 1) == 0
        elif 'error_rate' in expression:
            return metrics.get('error_rate', 0) > 0.05
        
        return False
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        
        if alert.severity == 'critical':
            # Critical alerts go to all channels
            channels = ['slack', 'pagerduty', 'sms', 'email']
        else:
            # Warnings only to Slack and email
            channels = ['slack', 'email']
        
        for channel in channels:
            self._send_to_channel(channel, alert)
    
    def _send_to_channel(self, channel: str, alert: Alert):
        """Send alert to specific notification channel"""
        
        message = f"🚨 {alert.severity.upper()}: {alert.name}\n{alert.message}"
        
        if channel == 'slack':
            # Simulate Slack notification
            logger.info(f"SLACK: {message}")
        elif channel == 'pagerduty':
            # Simulate PagerDuty incident creation
            logger.info(f"PAGERDUTY: Creating incident for {alert.name}")
        elif channel == 'sms':
            # Simulate SMS alert
            logger.info(f"SMS to {self.notification_channels['sms']}: {alert.name}")
        elif channel == 'email':
            # Simulate email notification
            logger.info(f"EMAIL: Alert sent to SRE team")
    
    def _send_resolution_notification(self, alert: Alert):
        """Send alert resolution notification"""
        duration = (alert.ends_at - alert.starts_at).total_seconds() / 60
        message = f"✅ RESOLVED: {alert.name} (Duration: {duration:.1f}m)"
        logger.info(f"RESOLUTION: {message}")

# =============================================================================
# EXAMPLES 6-15: CONSOLIDATED MONITORING SYSTEMS
# =============================================================================

class BusinessMetricsCollector:
    """Example 6: Custom Business KPI Tracking"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def track_business_kpi(self, kpi_name: str, value: float, dimensions: Dict = None):
        """Track custom business KPIs"""
        
        kpi_entry = {
            'timestamp': datetime.now(),
            'value': value,
            'dimensions': dimensions or {}
        }
        
        self.metrics[kpi_name].append(kpi_entry)
        
        # Business-specific KPIs for Indian fintech
        if kpi_name == 'customer_acquisition_cost':
            # CAC for Indian market (lower than global average)
            if value > 500:  # ₹500 CAC threshold
                logger.warning(f"High CAC detected: ₹{value}")
        
        elif kpi_name == 'lifetime_value':
            # LTV for Indian customers
            ltv_cac_ratio = value / dimensions.get('cac', 1)
            if ltv_cac_ratio < 3:
                logger.warning(f"Low LTV/CAC ratio: {ltv_cac_ratio:.2f}")

class LogParser:
    """Example 7: Advanced Log Parsing"""
    
    def __init__(self):
        # Indian banking log patterns
        self.patterns = {
            'upi_transaction': r'UPI_(\w+)_(\d+\.\d+)_(\w+)_(\w+)',
            'failed_login': r'FAILED_LOGIN_(\w+)_(\d+\.\d+\.\d+\.\d+)',
            'kyc_verification': r'KYC_(\w+)_(\w+)_(\w+)'
        }
    
    def parse_log_line(self, log_line: str) -> Dict:
        """Parse structured information from log lines"""
        
        for pattern_name, pattern in self.patterns.items():
            match = re.search(pattern, log_line)
            if match:
                if pattern_name == 'upi_transaction':
                    return {
                        'type': 'upi_transaction',
                        'txn_id': match.group(1),
                        'amount': float(match.group(2)),
                        'status': match.group(3),
                        'bank': match.group(4)
                    }
                elif pattern_name == 'failed_login':
                    return {
                        'type': 'security_event',
                        'user_id': match.group(1),
                        'ip_address': match.group(2),
                        'risk_score': 7  # High risk for failed login
                    }
        
        return {'type': 'unknown', 'raw': log_line}

class TraceCorrelator:
    """Example 8: Request Flow Analysis"""
    
    def __init__(self):
        self.traces = {}
        self.correlation_map = defaultdict(list)
    
    def correlate_request_flow(self, trace_id: str, spans: List[Dict]) -> Dict:
        """Analyze complete request flow across services"""
        
        # Build service call graph
        service_graph = defaultdict(list)
        total_duration = 0
        
        for span in spans:
            service = span.get('service_name')
            duration = span.get('duration_ms', 0)
            total_duration += duration
            
            if span.get('parent_span_id'):
                parent_service = self._get_service_by_span(spans, span['parent_span_id'])
                service_graph[parent_service].append(service)
        
        # Identify bottlenecks
        bottlenecks = []
        for span in spans:
            if span.get('duration_ms', 0) > total_duration * 0.3:  # >30% of total time
                bottlenecks.append({
                    'service': span.get('service_name'),
                    'operation': span.get('operation'),
                    'duration_ms': span.get('duration_ms')
                })
        
        return {
            'trace_id': trace_id,
            'service_graph': dict(service_graph),
            'total_duration_ms': total_duration,
            'bottlenecks': bottlenecks,
            'service_count': len(set(span.get('service_name') for span in spans))
        }
    
    def _get_service_by_span(self, spans: List[Dict], span_id: str) -> str:
        """Get service name by span ID"""
        for span in spans:
            if span.get('span_id') == span_id:
                return span.get('service_name', 'unknown')
        return 'unknown'

class ErrorTracker:
    """Example 9: Sentry-style Error Tracking"""
    
    def __init__(self):
        self.errors = []
        self.error_patterns = defaultdict(int)
    
    def capture_exception(self, exception: Exception, context: Dict = None):
        """Capture and analyze exceptions"""
        
        error_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(),
            'type': type(exception).__name__,
            'message': str(exception),
            'context': context or {},
            'fingerprint': self._generate_fingerprint(exception),
            'level': 'error'
        }
        
        self.errors.append(error_entry)
        self.error_patterns[error_entry['fingerprint']] += 1
        
        # Alert on high-frequency errors
        if self.error_patterns[error_entry['fingerprint']] > 10:
            logger.critical(f"High-frequency error detected: {exception}")
    
    def _generate_fingerprint(self, exception: Exception) -> str:
        """Generate fingerprint for error grouping"""
        error_type = type(exception).__name__
        error_message = str(exception)
        return hashlib.md5(f"{error_type}:{error_message}".encode()).hexdigest()[:16]

class APMMonitor:
    """Example 10: Application Performance Monitoring"""
    
    def __init__(self):
        self.performance_data = defaultdict(list)
        self.slow_queries = []
    
    def track_performance(self, operation: str, duration_ms: float, metadata: Dict = None):
        """Track application performance metrics"""
        
        perf_entry = {
            'timestamp': datetime.now(),
            'operation': operation,
            'duration_ms': duration_ms,
            'metadata': metadata or {}
        }
        
        self.performance_data[operation].append(perf_entry)
        
        # Detect slow operations (Indian banking context)
        thresholds = {
            'upi_payment': 2000,  # UPI should complete in <2s
            'database_query': 100,  # DB queries should be <100ms
            'api_call': 500,      # API calls should be <500ms
            'kyc_verification': 5000  # KYC can take up to 5s
        }
        
        threshold = thresholds.get(operation, 1000)
        if duration_ms > threshold:
            logger.warning(f"Slow operation detected: {operation} took {duration_ms}ms")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary statistics"""
        
        summary = {}
        for operation, measurements in self.performance_data.items():
            durations = [m['duration_ms'] for m in measurements]
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'avg_ms': statistics.mean(durations),
                    'p50_ms': statistics.median(durations),
                    'p95_ms': np.percentile(durations, 95) if len(durations) > 1 else durations[0],
                    'p99_ms': np.percentile(durations, 99) if len(durations) > 1 else durations[0]
                }
        
        return summary

class SyntheticMonitor:
    """Example 11: Endpoint Health Checks"""
    
    def __init__(self):
        self.endpoints = {
            'upi_payment': 'https://api.paytm.com/v1/upi/pay',
            'balance_check': 'https://api.paytm.com/v1/wallet/balance',
            'kyc_status': 'https://api.paytm.com/v1/kyc/status'
        }
        self.health_data = defaultdict(list)
    
    async def check_endpoint_health(self, endpoint_name: str) -> Dict:
        """Perform synthetic health check"""
        
        start_time = time.time()
        
        try:
            # Simulate HTTP check (in production, use actual HTTP client)
            await asyncio.sleep(random.uniform(0.1, 1.0))  # Simulate network call
            
            # Random failure simulation
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Connection timeout")
            
            duration_ms = (time.time() - start_time) * 1000
            
            health_result = {
                'endpoint': endpoint_name,
                'status': 'healthy',
                'response_time_ms': duration_ms,
                'timestamp': datetime.now(),
                'status_code': 200
            }
            
        except Exception as e:
            health_result = {
                'endpoint': endpoint_name,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(),
                'status_code': 0
            }
        
        self.health_data[endpoint_name].append(health_result)
        return health_result

class SLOTracker:
    """Example 12: SLI/SLO Tracking"""
    
    def __init__(self):
        # SLOs for Indian banking services
        self.slos = {
            'upi_availability': {'target': 99.5, 'window': 'monthly'},
            'api_latency_p95': {'target': 500, 'window': 'weekly'},  # 500ms
            'error_rate': {'target': 1.0, 'window': 'daily'},  # <1% error rate
            'kyc_processing_time': {'target': 300, 'window': 'weekly'}  # 5 minutes
        }
        
        self.sli_data = defaultdict(list)
        self.slo_status = {}
    
    def record_sli(self, sli_name: str, value: float):
        """Record Service Level Indicator measurement"""
        
        sli_entry = {
            'timestamp': datetime.now(),
            'value': value
        }
        
        self.sli_data[sli_name].append(sli_entry)
        
        # Calculate SLO compliance
        self._calculate_slo_compliance(sli_name)
    
    def _calculate_slo_compliance(self, sli_name: str):
        """Calculate SLO compliance for given SLI"""
        
        if sli_name not in self.slos:
            return
        
        slo_config = self.slos[sli_name]
        measurements = self.sli_data[sli_name]
        
        if not measurements:
            return
        
        # Get measurements within SLO window
        if slo_config['window'] == 'daily':
            cutoff = datetime.now() - timedelta(days=1)
        elif slo_config['window'] == 'weekly':
            cutoff = datetime.now() - timedelta(weeks=1)
        else:  # monthly
            cutoff = datetime.now() - timedelta(days=30)
        
        recent_measurements = [m for m in measurements if m['timestamp'] >= cutoff]
        
        if recent_measurements:
            values = [m['value'] for m in recent_measurements]
            
            if sli_name.endswith('availability'):
                # Availability: percentage of successful requests
                compliance = statistics.mean(values)
            elif sli_name.endswith('latency_p95'):
                # Latency: 95th percentile should be under target
                compliance = (np.percentile(values, 95) <= slo_config['target']) * 100
            else:
                # Error rate: should be under target
                compliance = (statistics.mean(values) <= slo_config['target']) * 100
            
            self.slo_status[sli_name] = {
                'compliance_percentage': compliance,
                'target': slo_config['target'],
                'status': 'compliant' if compliance >= 99.0 else 'non_compliant'
            }

class CapacityPlanner:
    """Example 13: Resource Forecasting"""
    
    def __init__(self):
        self.resource_usage = defaultdict(list)
        self.growth_rates = {}
    
    def record_resource_usage(self, resource: str, usage_percent: float):
        """Record resource utilization"""
        
        usage_entry = {
            'timestamp': datetime.now(),
            'usage_percent': usage_percent
        }
        
        self.resource_usage[resource].append(usage_entry)
    
    def forecast_capacity_needs(self, resource: str, days_ahead: int = 30) -> Dict:
        """Forecast future capacity needs"""
        
        measurements = self.resource_usage[resource]
        if len(measurements) < 10:  # Need at least 10 data points
            return {'error': 'Insufficient data for forecasting'}
        
        # Simple linear regression for growth rate
        timestamps = [m['timestamp'].timestamp() for m in measurements[-30:]]  # Last 30 measurements
        usage_values = [m['usage_percent'] for m in measurements[-30:]]
        
        # Calculate trend (simplified)
        if len(usage_values) > 1:
            growth_rate = (usage_values[-1] - usage_values[0]) / len(usage_values)
        else:
            growth_rate = 0
        
        # Project future usage
        current_usage = usage_values[-1] if usage_values else 0
        projected_usage = current_usage + (growth_rate * days_ahead)
        
        # Capacity recommendations
        recommendations = []
        if projected_usage > 80:
            recommendations.append("Scale up resources - approaching capacity limit")
        elif projected_usage > 60:
            recommendations.append("Monitor closely - moderate usage growth")
        else:
            recommendations.append("Current capacity sufficient")
        
        return {
            'resource': resource,
            'current_usage_percent': current_usage,
            'projected_usage_percent': max(0, projected_usage),
            'growth_rate_per_day': growth_rate,
            'days_until_80_percent': max(0, (80 - current_usage) / growth_rate) if growth_rate > 0 else float('inf'),
            'recommendations': recommendations
        }

class AnomalyDetector:
    """Example 14: ML-based Anomaly Detection"""
    
    def __init__(self):
        self.baseline_data = defaultdict(list)
        self.anomalies = []
    
    def detect_anomalies(self, metric_name: str, value: float) -> bool:
        """Detect anomalies using statistical methods"""
        
        # Add to baseline data
        self.baseline_data[metric_name].append(value)
        
        # Need at least 30 data points for anomaly detection
        if len(self.baseline_data[metric_name]) < 30:
            return False
        
        # Keep only last 100 points for baseline
        recent_data = self.baseline_data[metric_name][-100:]
        
        # Calculate baseline statistics
        mean = statistics.mean(recent_data[:-1])  # Exclude current value
        std_dev = statistics.stdev(recent_data[:-1]) if len(recent_data) > 2 else 0
        
        # Detect anomaly using 3-sigma rule
        threshold = 3 * std_dev
        is_anomaly = abs(value - mean) > threshold
        
        if is_anomaly:
            anomaly = {
                'timestamp': datetime.now(),
                'metric': metric_name,
                'value': value,
                'baseline_mean': mean,
                'deviation': abs(value - mean),
                'threshold': threshold,
                'severity': 'high' if abs(value - mean) > 4 * std_dev else 'medium'
            }
            
            self.anomalies.append(anomaly)
            logger.warning(f"Anomaly detected in {metric_name}: {value} (baseline: {mean:.2f})")
        
        return is_anomaly

class CostMonitor:
    """Example 15: Cloud Spend Tracking"""
    
    def __init__(self):
        self.cost_data = defaultdict(list)
        self.budgets = {
            'compute': {'monthly': 50000, 'daily': 1667},  # ₹50K per month
            'storage': {'monthly': 10000, 'daily': 333},
            'network': {'monthly': 15000, 'daily': 500},
            'database': {'monthly': 25000, 'daily': 833}
        }
    
    def track_cost(self, service: str, cost_inr: float):
        """Track cloud service costs"""
        
        cost_entry = {
            'timestamp': datetime.now(),
            'service': service,
            'cost_inr': cost_inr
        }
        
        self.cost_data[service].append(cost_entry)
        
        # Check budget alerts
        self._check_budget_alerts(service)
    
    def _check_budget_alerts(self, service: str):
        """Check for budget threshold violations"""
        
        if service not in self.budgets:
            return
        
        # Calculate today's spend
        today = datetime.now().date()
        today_costs = [
            entry['cost_inr'] for entry in self.cost_data[service]
            if entry['timestamp'].date() == today
        ]
        
        daily_spend = sum(today_costs)
        daily_budget = self.budgets[service]['daily']
        
        if daily_spend > daily_budget * 1.2:  # 20% over budget
            logger.critical(f"Budget alert: {service} daily spend ₹{daily_spend:.2f} exceeds budget by 20%")
        elif daily_spend > daily_budget:
            logger.warning(f"Budget alert: {service} daily spend ₹{daily_spend:.2f} exceeds daily budget")
    
    def get_cost_summary(self) -> Dict:
        """Get comprehensive cost summary"""
        
        summary = {}
        total_monthly_cost = 0
        
        for service, budget_info in self.budgets.items():
            # Calculate last 30 days cost
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_costs = [
                entry['cost_inr'] for entry in self.cost_data[service]
                if entry['timestamp'] >= thirty_days_ago
            ]
            
            monthly_spend = sum(recent_costs)
            monthly_budget = budget_info['monthly']
            total_monthly_cost += monthly_spend
            
            summary[service] = {
                'monthly_spend_inr': monthly_spend,
                'monthly_budget_inr': monthly_budget,
                'budget_utilization_percent': (monthly_spend / monthly_budget) * 100,
                'projected_monthly_spend': monthly_spend * (30 / 30),  # Simplified projection
                'status': 'over_budget' if monthly_spend > monthly_budget else 'within_budget'
            }
        
        summary['total'] = {
            'monthly_spend_inr': total_monthly_cost,
            'monthly_budget_inr': sum(b['monthly'] for b in self.budgets.values()),
            'largest_expense': max(summary.keys(), key=lambda k: summary[k]['monthly_spend_inr']) if summary else None
        }
        
        return summary

def demonstrate_comprehensive_observability():
    """Demonstrate all observability systems for Indian tech companies"""
    print("\n📊 Comprehensive Observability Demo - Indian Tech Stack")
    print("=" * 58)
    
    # Initialize all monitoring systems
    dashboard = GrafanaDashboard("Paytm Production Monitoring")
    alert_mgr = AlertManager()
    business_metrics = BusinessMetricsCollector()
    log_parser = LogParser()
    trace_correlator = TraceCorrelator()
    error_tracker = ErrorTracker()
    apm_monitor = APMMonitor()
    synthetic_monitor = SyntheticMonitor()
    slo_tracker = SLOTracker()
    capacity_planner = CapacityPlanner()
    anomaly_detector = AnomalyDetector()
    cost_monitor = CostMonitor()
    
    print("✅ All monitoring systems initialized")
    
    # Demonstrate key features
    print("\n📈 Business Metrics Tracking")
    print("-" * 30)
    
    business_metrics.track_business_kpi('customer_acquisition_cost', 450.0, {'channel': 'digital', 'city': 'mumbai'})
    business_metrics.track_business_kpi('lifetime_value', 15000.0, {'cac': 450.0, 'segment': 'premium'})
    print("✅ Business KPIs tracked: CAC, LTV")
    
    # Performance monitoring
    print("\n⚡ Performance Monitoring")
    print("-" * 26)
    
    apm_monitor.track_performance('upi_payment', 850.0, {'bank': 'hdfc', 'amount': 5000})
    apm_monitor.track_performance('database_query', 45.0, {'table': 'transactions', 'type': 'select'})
    apm_monitor.track_performance('kyc_verification', 3200.0, {'provider': 'aadhaar', 'status': 'success'})
    
    perf_summary = apm_monitor.get_performance_summary()
    print("📊 Performance Summary:")
    for operation, stats in perf_summary.items():
        print(f"   • {operation}: avg {stats['avg_ms']:.1f}ms, p95 {stats['p95_ms']:.1f}ms")
    
    # SLO tracking
    print("\n🎯 SLO Compliance Tracking")
    print("-" * 27)
    
    slo_tracker.record_sli('upi_availability', 99.2)
    slo_tracker.record_sli('api_latency_p95', 480.0)
    slo_tracker.record_sli('error_rate', 0.8)
    
    print("📊 SLO Status:")
    for sli_name, status in slo_tracker.slo_status.items():
        compliance = status['compliance_percentage']
        symbol = "✅" if compliance >= 99 else "⚠️"
        print(f"   {symbol} {sli_name}: {compliance:.1f}% compliant")
    
    # Anomaly detection
    print("\n🔍 Anomaly Detection")
    print("-" * 21)
    
    # Simulate normal metrics then anomaly
    normal_values = [random.uniform(95, 105) for _ in range(30)]
    for value in normal_values:
        anomaly_detector.detect_anomalies('transaction_rate', value)
    
    # Inject anomaly
    anomaly_detected = anomaly_detector.detect_anomalies('transaction_rate', 150.0)
    print(f"🚨 Anomaly detection result: {'Anomaly detected!' if anomaly_detected else 'Normal'}")
    
    # Cost monitoring
    print("\n💰 Cost Monitoring")
    print("-" * 17)
    
    cost_monitor.track_cost('compute', 1800.0)  # Daily compute cost
    cost_monitor.track_cost('database', 950.0)  # Daily DB cost
    cost_monitor.track_cost('storage', 280.0)   # Daily storage cost
    
    cost_summary = cost_monitor.get_cost_summary()
    print("📊 Cost Summary:")
    for service, info in cost_summary.items():
        if service != 'total' and 'monthly_spend_inr' in info:
            utilization = info['budget_utilization_percent']
            status = "🔴" if utilization > 100 else "🟡" if utilization > 80 else "🟢"
            print(f"   {status} {service}: ₹{info['monthly_spend_inr']:,.0f} ({utilization:.1f}% of budget)")
    
    # Capacity planning
    print("\n📊 Capacity Planning")
    print("-" * 20)
    
    # Simulate resource usage over time
    for i in range(15):
        cpu_usage = 45 + (i * 2) + random.uniform(-5, 5)  # Growing trend
        capacity_planner.record_resource_usage('cpu', cpu_usage)
    
    forecast = capacity_planner.forecast_capacity_needs('cpu', days_ahead=30)
    if 'error' not in forecast:
        print(f"📈 CPU Forecast:")
        print(f"   Current: {forecast['current_usage_percent']:.1f}%")
        print(f"   Projected (30d): {forecast['projected_usage_percent']:.1f}%")
        print(f"   Recommendation: {forecast['recommendations'][0]}")
    
    # Generate dashboard
    print("\n🎛️  Dashboard Configuration")
    print("-" * 27)
    
    dashboard_config = dashboard.generate_dashboard_json()
    panel_count = len(dashboard_config['dashboard']['panels'])
    print(f"📊 Generated Grafana dashboard with {panel_count} panels")
    print(f"   • UPI transaction monitoring")
    print(f"   • Success rate tracking") 
    print(f"   • Revenue visualization")
    print(f"   • Infrastructure health")
    
    # Final summary
    print(f"\n🏆 Observability Stack Summary")
    print("-" * 32)
    print("✅ Real-time metrics collection (Prometheus-style)")
    print("✅ Distributed tracing (Jaeger-style)")
    print("✅ Centralized logging (ELK-style)")
    print("✅ Custom business KPI tracking")
    print("✅ SLI/SLO compliance monitoring")
    print("✅ Anomaly detection and alerting")
    print("✅ Cost optimization tracking")
    print("✅ Capacity planning and forecasting")
    print("✅ Performance monitoring (APM)")
    print("✅ Synthetic health checks")
    print("✅ Error tracking and analysis")
    print("✅ Dashboard and visualization")

if __name__ == "__main__":
    demonstrate_comprehensive_observability()