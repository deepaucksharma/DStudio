# Law 6: Law of Cognitive Load - Exercises

## Overview

These exercises focus on designing human-friendly distributed systems that minimize cognitive load while maximizing operational effectiveness. You'll practice creating interfaces, alerts, and automation that respect human limitations.

## Exercise 1: Redesigning Error Messages for Clarity

### Background
Poor error messages increase cognitive load and delay incident resolution. This exercise practices transforming technical errors into actionable messages.

### Task
Transform the following technical error messages into human-friendly versions that:
- Clearly state what went wrong
- Explain the impact
- Provide actionable next steps
- Include relevant context

```python
# Error Message Redesign Framework
class ErrorMessageDesigner:
    def __init__(self):
        self.context_cache = {}
        
    def transform_error(self, technical_error, context=None):
        """Transform technical error into human-friendly message"""
        
# Parse technical error
        error_type = self._identify_error_type(technical_error)
        
# Build human-friendly message
        message = {
            'what': self._explain_what_happened(error_type, technical_error),
            'impact': self._assess_impact(error_type, context),
            'action': self._suggest_actions(error_type, context),
            'details': self._provide_context(technical_error, context)
        }
        
        return self._format_message(message)
    
    def _identify_error_type(self, error):
        """Categorize error for appropriate handling"""
        error_patterns = {
            'connection': ['ECONNREFUSED', 'timeout', 'unreachable'],
            'capacity': ['OOM', 'disk full', 'queue full'],
            'permission': ['403', 'unauthorized', 'denied'],
            'data': ['validation', 'parse', 'corrupt']
        }
        
        for category, patterns in error_patterns.items():
            if any(p in str(error).lower() for p in patterns):
                return category
        return 'unknown'
    
    def _explain_what_happened(self, error_type, technical_error):
        """Plain English explanation of the error"""
        explanations = {
            'connection': "Unable to connect to the service",
            'capacity': "System resources are exhausted",
            'permission': "Access was denied",
            'data': "Data processing failed"
        }
        return explanations.get(error_type, "An unexpected error occurred")
    
    def _assess_impact(self, error_type, context):
        """Describe user/business impact"""
        if not context:
            return "Service functionality may be limited"
            
        impacts = {
            'connection': f"Users cannot access {context.get('service', 'the service')}",
            'capacity': f"New requests are being rejected",
            'permission': f"Operation cannot be completed",
            'data': f"Data may be incomplete or incorrect"
        }
        return impacts.get(error_type, "Unknown impact")
    
    def _suggest_actions(self, error_type, context):
        """Provide actionable next steps"""
        actions = {
            'connection': [
                "Check if the service is running",
                "Verify network connectivity",
                "Review recent deployments"
            ],
            'capacity': [
                "Scale up resources",
                "Clear old data/logs",
                "Investigate resource usage spike"
            ],
            'permission': [
                "Verify credentials are correct",
                "Check permission settings",
                "Contact service owner"
            ],
            'data': [
                "Validate input data format",
                "Check for recent schema changes",
                "Review data pipeline health"
            ]
        }
        return actions.get(error_type, ["Check logs for more details"])
    
    def _provide_context(self, technical_error, context):
        """Include helpful technical details"""
        return {
            'original_error': str(technical_error),
            'timestamp': context.get('timestamp') if context else None,
            'service': context.get('service') if context else None,
            'request_id': context.get('request_id') if context else None
        }
    
    def _format_message(self, message):
        """Format message for display"""
        formatted = f"""
🚨 {message['what']}

Impact: {message['impact']}

Recommended Actions:
{chr(10).join(f"  • {action}" for action in message['action'])}

Technical Details:
  Error: {message['details']['original_error']}
  Service: {message['details'].get('service', 'N/A')}
  Time: {message['details'].get('timestamp', 'N/A')}
  Request ID: {message['details'].get('request_id', 'N/A')}
"""
        return formatted.strip()

# Exercise: Transform these errors
technical_errors = [
    "Error: ECONNREFUSED 10.0.1.5:5432",
    "java.lang.OutOfMemoryError: Java heap space",
    "HTTP 403 Forbidden: Access denied to /api/users",
    "JSON parse error: Unexpected token at position 42"
]

designer = ErrorMessageDesigner()
for error in technical_errors:
    print("Original:", error)
    print("Transformed:")
    print(designer.transform_error(error, {'service': 'user-service'}))
    print("-" * 50)
```

### Questions
1. How does the transformed message reduce cognitive load?
2. What additional context would be helpful for each error type?
3. How would you adapt messages for different audiences (developers vs. operators)?

## Exercise 2: Creating Progressive Disclosure Dashboards

### Background
Information overload is a major source of cognitive load. Progressive disclosure shows essential information first, with details available on demand.

### Task
Design a monitoring dashboard that uses progressive disclosure principles.

```python
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class AlertLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    trend: str  # 'up', 'down', 'stable'
    
    @property
    def status(self) -> AlertLevel:
        if self.value >= self.threshold_critical:
            return AlertLevel.CRITICAL
        elif self.value >= self.threshold_warning:
            return AlertLevel.WARNING
        return AlertLevel.INFO

class ProgressiveDisclosureDashboard:
    """Dashboard that reveals information progressively based on context"""
    
    def __init__(self):
        self.metrics = {}
        self.drill_down_cache = {}
        
    def add_metric(self, metric: Metric):
        """Add a metric to track"""
        self.metrics[metric.name] = metric
        
    def get_overview(self) -> Dict:
        """Level 1: High-level system health"""
        critical_count = sum(1 for m in self.metrics.values() 
                           if m.status == AlertLevel.CRITICAL)
        warning_count = sum(1 for m in self.metrics.values() 
                          if m.status == AlertLevel.WARNING)
        
        overall_status = "healthy"
        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "degraded"
            
        return {
            'status': overall_status,
            'summary': {
                'critical': critical_count,
                'warning': warning_count,
                'healthy': len(self.metrics) - critical_count - warning_count
            },
            'action_required': critical_count > 0 or warning_count > 2
        }
    
    def get_problem_summary(self) -> List[Dict]:
        """Level 2: Summary of problems requiring attention"""
        problems = []
        
        for metric in self.metrics.values():
            if metric.status in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                problems.append({
                    'metric': metric.name,
                    'severity': metric.status.value,
                    'value': f"{metric.value} {metric.unit}",
                    'threshold': metric.threshold_critical if metric.status == AlertLevel.CRITICAL else metric.threshold_warning,
                    'trend': metric.trend,
                    'quick_action': self._suggest_quick_action(metric)
                })
                
# Sort by severity and value
        problems.sort(key=lambda x: (
            0 if x['severity'] == 'critical' else 1,
            -float(x['value'].split()[0])
        ))
        
        return problems[:5]  # Show top 5 problems
    
    def get_metric_details(self, metric_name: str) -> Dict:
        """Level 3: Detailed view of specific metric"""
        metric = self.metrics.get(metric_name)
        if not metric:
            return {}
            
        return {
            'name': metric.name,
            'current': {
                'value': metric.value,
                'unit': metric.unit,
                'status': metric.status.value
            },
            'thresholds': {
                'warning': metric.threshold_warning,
                'critical': metric.threshold_critical
            },
            'trend': {
                'direction': metric.trend,
                'prediction': self._predict_threshold_breach(metric)
            },
            'related_metrics': self._find_related_metrics(metric_name),
            'historical_context': self._get_historical_context(metric_name),
            'remediation': self._get_remediation_steps(metric)
        }
    
    def _suggest_quick_action(self, metric: Metric) -> str:
        """Suggest immediate action based on metric"""
        actions = {
            'cpu_usage': "Scale horizontally or optimize hot paths",
            'memory_usage': "Increase memory or fix memory leaks",
            'error_rate': "Check recent deployments and rollback if needed",
            'latency_p99': "Enable caching or optimize database queries",
            'queue_depth': "Increase consumers or reduce producer rate"
        }
        return actions.get(metric.name, "Investigate root cause")
    
    def _predict_threshold_breach(self, metric: Metric) -> Dict:
        """Predict when metric might breach threshold"""
        if metric.trend == 'up':
# Simplified linear prediction
            rate = metric.value * 0.1  # 10% growth rate
            time_to_warning = max(0, (metric.threshold_warning - metric.value) / rate)
            time_to_critical = max(0, (metric.threshold_critical - metric.value) / rate)
            
            return {
                'warning_in': f"{int(time_to_warning)} minutes" if time_to_warning > 0 else "Already breached",
                'critical_in': f"{int(time_to_critical)} minutes" if time_to_critical > 0 else "Already breached"
            }
        return {'status': 'No threshold breach predicted'}
    
    def _find_related_metrics(self, metric_name: str) -> List[str]:
        """Find metrics that might be related"""
        relationships = {
            'cpu_usage': ['memory_usage', 'request_rate', 'thread_count'],
            'memory_usage': ['cpu_usage', 'gc_time', 'heap_size'],
            'error_rate': ['latency_p99', 'request_rate', 'retry_rate'],
            'latency_p99': ['cpu_usage', 'db_connection_pool', 'cache_hit_rate']
        }
        return relationships.get(metric_name, [])
    
    def _get_historical_context(self, metric_name: str) -> Dict:
        """Provide historical context for the metric"""
# Simulated historical data
        return {
            'usual_range': f"{70}-{85}%",
            'last_incident': "2 days ago (resolved by scaling)",
            'weekly_pattern': "Peaks during business hours",
            'anomaly': "Current value is 2.5 std devs above normal"
        }
    
    def _get_remediation_steps(self, metric: Metric) -> List[str]:
        """Detailed remediation steps"""
        if metric.status == AlertLevel.CRITICAL:
            return [
                f"1. Immediate: {self._suggest_quick_action(metric)}",
                "2. Notify on-call engineer if not already alerted",
                "3. Check related services for cascade failures",
                "4. Prepare rollback if recent deployment",
                "5. Document actions taken for post-mortem"
            ]
        elif metric.status == AlertLevel.WARNING:
            return [
                "1. Monitor trend over next 15 minutes",
                "2. Review recent changes that might impact this metric",
                "3. Consider preventive scaling if trend continues",
                "4. Update capacity planning projections"
            ]
        return ["No action required - metric within normal range"]
    
    def render_cli_dashboard(self):
        """Render dashboard in CLI with progressive disclosure"""
# Level 1: Overview
        overview = self.get_overview()
        print("\n" + "="*60)
        print(f"SYSTEM STATUS: {overview['status'].upper()}")
        print("="*60)
        
        if overview['status'] == 'healthy':
            print("✅ All systems operational")
            return
            
# Level 2: Problem Summary (shown when issues exist)
        print("\n⚠️  ISSUES REQUIRING ATTENTION:")
        problems = self.get_problem_summary()
        for i, problem in enumerate(problems, 1):
            icon = "🔴" if problem['severity'] == 'critical' else "🟡"
            print(f"\n{icon} {i}. {problem['metric']}: {problem['value']}")
            print(f"   Trend: {problem['trend']} | Action: {problem['quick_action']}")
            
# Level 3: Prompt for details
        print("\n" + "-"*60)
        choice = input("\nEnter number for details (or 'q' to quit): ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(problems):
            problem = problems[int(choice)-1]
            details = self.get_metric_details(problem['metric'])
            
            print(f"\n📊 DETAILED VIEW: {details['name']}")
            print("-"*40)
            print(f"Current: {details['current']['value']} {details['current']['unit']}")
            print(f"Status: {details['current']['status']}")
            print(f"Trend: {details['trend']['direction']}")
            print(f"Prediction: {details['trend']['prediction']}")
            
            print("\n🔗 Related Metrics:")
            for related in details['related_metrics']:
                print(f"  - {related}")
                
            print("\n📈 Historical Context:")
            for key, value in details['historical_context'].items():
                print(f"  - {key}: {value}")
                
            print("\n🛠️  Remediation Steps:")
            for step in details['remediation']:
                print(f"  {step}")

# Demo the dashboard
dashboard = ProgressiveDisclosureDashboard()

# Add sample metrics
dashboard.add_metric(Metric('cpu_usage', 92, '%', 80, 90, 'up'))
dashboard.add_metric(Metric('memory_usage', 78, '%', 75, 85, 'stable'))
dashboard.add_metric(Metric('error_rate', 5.2, '%', 2, 5, 'up'))
dashboard.add_metric(Metric('latency_p99', 450, 'ms', 300, 500, 'up'))
dashboard.add_metric(Metric('queue_depth', 15000, 'messages', 10000, 20000, 'up'))

# Render the dashboard
dashboard.render_cli_dashboard()
```

### Questions
1. How does progressive disclosure reduce initial cognitive load?
2. What information should always be visible vs. available on demand?
3. How would you adapt this for mobile vs. desktop viewing?

## Exercise 3: Building Alert Prioritization Systems

### Background
Alert fatigue is a major cause of incidents. This exercise focuses on building systems that prioritize alerts based on business impact and urgency.

### Task
Create an alert prioritization system that reduces noise and highlights what matters.

```python
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import heapq
from dataclasses import dataclass, field

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    source: str
    timestamp: datetime
    tags: Set[str] = field(default_factory=set)
    business_impact: Optional[str] = None
    affected_users: int = 0
    related_alerts: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
# For priority queue comparison
        return self.priority_score > other.priority_score

class AlertPrioritizationSystem:
    """Intelligent alert prioritization to reduce cognitive load"""
    
    def __init__(self):
        self.alerts = {}
        self.alert_history = []
        self.suppression_rules = []
        self.business_context = {}
        
    def add_alert(self, alert: Alert) -> bool:
        """Add alert if not suppressed"""
# Check suppression rules
        if self._should_suppress(alert):
            return False
            
# Check for deduplication
        if self._is_duplicate(alert):
            self._merge_with_existing(alert)
            return False
            
# Calculate priority score
        alert.priority_score = self._calculate_priority(alert)
        
# Store alert
        self.alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        return True
    
    def _calculate_priority(self, alert: Alert) -> float:
        """Calculate priority score based on multiple factors"""
        score = 0.0
        
# Base severity score
        severity_scores = {
            'critical': 100,
            'high': 70,
            'medium': 40,
            'low': 10
        }
        score += severity_scores.get(alert.severity, 0)
        
# Business impact multiplier
        if alert.business_impact:
            impact_multipliers = {
                'revenue_loss': 3.0,
                'data_loss': 2.5,
                'service_degradation': 2.0,
                'internal_only': 1.0
            }
            score *= impact_multipliers.get(alert.business_impact, 1.0)
        
# User impact factor
        if alert.affected_users > 0:
# Logarithmic scale for user impact
            import math
            user_factor = 1 + math.log10(max(1, alert.affected_users))
            score *= user_factor
        
# Time decay (recent alerts are more important)
        age = datetime.now() - alert.timestamp
        if age < timedelta(minutes=5):
            score *= 1.5  # Boost for very recent
        elif age > timedelta(hours=1):
            score *= 0.7  # Decay for older alerts
            
# Alert storm detection (reduce score if many similar alerts)
        similar_count = self._count_similar_recent_alerts(alert)
        if similar_count > 5:
            score *= 0.5  # Reduce priority in alert storms
            
# Known false positive patterns
        if self._matches_false_positive_pattern(alert):
            score *= 0.3
            
        return score
    
    def _should_suppress(self, alert: Alert) -> bool:
        """Check if alert should be suppressed"""
# Maintenance window suppression
        if self._in_maintenance_window(alert.source):
            return True
            
# Rate limiting
        if self._exceeds_rate_limit(alert):
            return True
            
# Business hours suppression for low priority
        if alert.severity == 'low' and not self._is_business_hours():
            return True
            
        return False
    
    def _is_duplicate(self, alert: Alert) -> bool:
        """Check if this is a duplicate of recent alert"""
        recent_window = datetime.now() - timedelta(minutes=15)
        
        for existing_alert in self.alert_history:
            if existing_alert.timestamp < recent_window:
                continue
                
# Similar title and source
            if (existing_alert.title == alert.title and 
                existing_alert.source == alert.source):
                return True
                
# Fuzzy matching for similar alerts
            if self._similarity_score(existing_alert, alert) > 0.8:
                return True
                
        return False
    
    def _merge_with_existing(self, new_alert: Alert):
        """Merge new alert with existing similar alert"""
        for alert_id, existing in self.alerts.items():
            if self._similarity_score(existing, new_alert) > 0.8:
# Update affected users
                existing.affected_users += new_alert.affected_users
# Add to related alerts
                existing.related_alerts.append(new_alert.id)
# Update timestamp to keep it fresh
                existing.timestamp = new_alert.timestamp
# Recalculate priority
                existing.priority_score = self._calculate_priority(existing)
                break
    
    def _count_similar_recent_alerts(self, alert: Alert) -> int:
        """Count similar alerts in recent time window"""
        count = 0
        recent_window = datetime.now() - timedelta(minutes=30)
        
        for historical in self.alert_history:
            if historical.timestamp < recent_window:
                continue
            if historical.source == alert.source and historical.severity == alert.severity:
                count += 1
                
        return count
    
    def _matches_false_positive_pattern(self, alert: Alert) -> bool:
        """Check if alert matches known false positive patterns"""
        false_positive_patterns = [
            ('health_check', 'timeout'),  # Health checks often timeout
            ('test', 'failure'),          # Test environment issues
            ('dev', 'error'),             # Development environment
        ]
        
        alert_text = f"{alert.title} {alert.description}".lower()
        for pattern in false_positive_patterns:
            if all(word in alert_text for word in pattern):
                return True
                
        return False
    
    def _similarity_score(self, alert1: Alert, alert2: Alert) -> float:
        """Calculate similarity between two alerts"""
        score = 0.0
        
# Same source
        if alert1.source == alert2.source:
            score += 0.3
            
# Same severity
        if alert1.severity == alert2.severity:
            score += 0.2
            
# Title similarity (simple word overlap)
        words1 = set(alert1.title.lower().split())
        words2 = set(alert2.title.lower().split())
        if words1 and words2:
            overlap = len(words1 & words2) / len(words1 | words2)
            score += 0.3 * overlap
            
# Tag overlap
        if alert1.tags and alert2.tags:
            tag_overlap = len(alert1.tags & alert2.tags) / len(alert1.tags | alert2.tags)
            score += 0.2 * tag_overlap
            
        return score
    
    def _in_maintenance_window(self, source: str) -> bool:
        """Check if source is in maintenance window"""
# Simulate maintenance windows
        maintenance_windows = {
            'database-backup': (2, 4),  # 2 AM - 4 AM
            'batch-processing': (1, 5),  # 1 AM - 5 AM
        }
        
        current_hour = datetime.now().hour
        if source in maintenance_windows:
            start, end = maintenance_windows[source]
            if start <= current_hour < end:
                return True
                
        return False
    
    def _exceeds_rate_limit(self, alert: Alert) -> bool:
        """Check if alert exceeds rate limit"""
# Count alerts from same source in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_count = sum(1 for a in self.alert_history 
                         if a.source == alert.source and a.timestamp > one_hour_ago)
        
# Rate limits by severity
        rate_limits = {
            'critical': 999,  # No limit for critical
            'high': 20,
            'medium': 10,
            'low': 5
        }
        
        return recent_count >= rate_limits.get(alert.severity, 10)
    
    def _is_business_hours(self) -> bool:
        """Check if current time is business hours"""
        now = datetime.now()
# Monday = 0, Sunday = 6
        if now.weekday() >= 5:  # Weekend
            return False
# 9 AM - 6 PM
        return 9 <= now.hour < 18
    
    def get_prioritized_alerts(self, limit: int = 5) -> List[Alert]:
        """Get top priority alerts for operator attention"""
# Filter active alerts
        active_alerts = []
        stale_threshold = datetime.now() - timedelta(hours=4)
        
        for alert in self.alerts.values():
            if alert.timestamp > stale_threshold:
                heapq.heappush(active_alerts, alert)
        
# Return top N
        return heapq.nsmallest(limit, active_alerts)
    
    def get_alert_summary(self) -> Dict:
        """Get cognitive-load-friendly summary"""
        active_alerts = self.get_prioritized_alerts(10)
        
        if not active_alerts:
            return {
                'status': 'all_clear',
                'message': 'No active alerts',
                'action_required': False
            }
        
        critical_count = sum(1 for a in active_alerts if a.severity == 'critical')
        
        summary = {
            'status': 'critical' if critical_count > 0 else 'warning',
            'total_active': len(active_alerts),
            'requires_immediate_action': critical_count,
            'top_issues': []
        }
        
# Group by source for easier understanding
        by_source = {}
        for alert in active_alerts[:5]:  # Top 5 only
            if alert.source not in by_source:
                by_source[alert.source] = []
            by_source[alert.source].append(alert)
        
        for source, alerts in by_source.items():
            summary['top_issues'].append({
                'source': source,
                'count': len(alerts),
                'most_severe': max(a.severity for a in alerts),
                'primary_issue': alerts[0].title,
                'affected_users': sum(a.affected_users for a in alerts)
            })
        
        return summary
    
    def render_alert_dashboard(self):
        """Render alerts in cognitive-load-friendly format"""
        summary = self.get_alert_summary()
        
        print("\n" + "="*60)
        print(f"ALERT DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        if summary['status'] == 'all_clear':
            print("\n✅ " + summary['message'])
            return
        
# High-level summary
        status_icon = "🔴" if summary['status'] == 'critical' else "🟡"
        print(f"\n{status_icon} Status: {summary['status'].upper()}")
        print(f"Active Alerts: {summary['total_active']}")
        print(f"Immediate Action Required: {summary['requires_immediate_action']}")
        
# Top issues grouped by source
        print("\n📊 TOP ISSUES BY SERVICE:")
        print("-"*40)
        
        for issue in summary['top_issues']:
            severity_icon = "🔴" if issue['most_severe'] == 'critical' else "🟡"
            print(f"\n{severity_icon} {issue['source']}")
            print(f"  Issues: {issue['count']}")
            print(f"  Primary: {issue['primary_issue']}")
            if issue['affected_users'] > 0:
                print(f"  Affected Users: {issue['affected_users']:,}")
        
# Detailed view of top alerts
        print("\n\n🚨 PRIORITY ALERTS:")
        print("-"*40)
        
        top_alerts = self.get_prioritized_alerts(3)
        for i, alert in enumerate(top_alerts, 1):
            print(f"\n{i}. [{alert.severity.upper()}] {alert.title}")
            print(f"   Source: {alert.source}")
            print(f"   Time: {alert.timestamp.strftime('%H:%M')}")
            if alert.business_impact:
                print(f"   Impact: {alert.business_impact}")
            if alert.affected_users > 0:
                print(f"   Users Affected: {alert.affected_users:,}")
            if alert.tags:
                print(f"   Tags: {', '.join(alert.tags)}")

# Demo the alert system
alert_system = AlertPrioritizationSystem()

# Simulate various alerts
test_alerts = [
    Alert('1', 'Database connection pool exhausted', 'No connections available', 
          'critical', 'user-service', datetime.now(), {'database', 'capacity'},
          'revenue_loss', 5000),
    
    Alert('2', 'High memory usage', 'Memory at 85%', 
          'high', 'api-gateway', datetime.now() - timedelta(minutes=10), 
          {'memory', 'performance'}, 'service_degradation', 1000),
    
    Alert('3', 'Slow query detected', 'Query took 5s', 
          'medium', 'analytics-db', datetime.now() - timedelta(minutes=5),
          {'database', 'performance'}, 'internal_only', 0),
    
    Alert('4', 'Health check timeout', 'Endpoint /health timed out', 
          'low', 'monitoring', datetime.now() - timedelta(minutes=2),
          {'health', 'monitoring'}, None, 0),
    
    Alert('5', 'Spike in error rate', 'Error rate increased to 15%', 
          'critical', 'payment-service', datetime.now() - timedelta(minutes=1),
          {'errors', 'payment'}, 'revenue_loss', 10000),
    
# Duplicate alert (should be merged)
    Alert('6', 'Database connection pool exhausted', 'No connections available', 
          'critical', 'user-service', datetime.now() + timedelta(seconds=30), 
          {'database', 'capacity'}, 'revenue_loss', 2000),
]

# Add alerts to system
for alert in test_alerts:
    added = alert_system.add_alert(alert)
    if not added:
        print(f"Alert '{alert.title}' was suppressed or merged")

# Display the dashboard
alert_system.render_alert_dashboard()
```

### Questions
1. How does alert grouping reduce cognitive load?
2. What factors should influence alert priority?
3. How would you handle alert fatigue during major incidents?

## Exercise 4: Designing Runbook Automation with Human Oversight

### Background
Effective automation reduces cognitive load while maintaining human control for critical decisions.

### Task
Build a runbook automation system that guides operators through incident response.

```python
import json
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import time

class StepType(Enum):
    AUTOMATED = "automated"
    HUMAN_DECISION = "human_decision"
    HUMAN_VALIDATION = "human_validation"
    NOTIFICATION = "notification"

@dataclass
class RunbookStep:
    id: str
    name: str
    description: str
    step_type: StepType
    action: Optional[Callable] = None
    validation: Optional[Callable] = None
    rollback: Optional[Callable] = None
    timeout_seconds: int = 300
    required_context: List[str] = field(default_factory=list)
    
class RunbookAutomation:
    """Automated runbook with human-in-the-loop for critical decisions"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps = []
        self.context = {}
        self.execution_log = []
        
    def add_step(self, step: RunbookStep):
        """Add a step to the runbook"""
        self.steps.append(step)
        
    def execute(self, initial_context: Dict = None):
        """Execute runbook with human oversight"""
        if initial_context:
            self.context.update(initial_context)
            
        print(f"\n{'='*60}")
        print(f"RUNBOOK: {self.name}")
        print(f"{'='*60}")
        print(f"Description: {self.description}\n")
        
# Pre-flight checks
        if not self._preflight_check():
            print("❌ Pre-flight checks failed. Aborting runbook.")
            return False
            
# Execute steps
        for i, step in enumerate(self.steps):
            print(f"\n{'─'*40}")
            print(f"Step {i+1}/{len(self.steps)}: {step.name}")
            print(f"{'─'*40}")
            
            success = self._execute_step(step)
            
            if not success:
                print(f"\n❌ Step failed: {step.name}")
                if self._should_rollback():
                    self._rollback_to_step(i)
                return False
                
        print(f"\n✅ Runbook completed successfully!")
        self._generate_summary()
        return True
    
    def _preflight_check(self) -> bool:
        """Verify preconditions before execution"""
        print("🔍 Running pre-flight checks...")
        
        checks = [
            ("Required permissions", self._check_permissions),
            ("System dependencies", self._check_dependencies),
            ("Context validation", self._validate_context),
            ("Rollback capability", self._verify_rollback_capability)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            result = check_func()
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
                
        return all_passed
    
    def _execute_step(self, step: RunbookStep) -> bool:
        """Execute a single step with appropriate handling"""
        print(f"\n📋 {step.description}")
        
# Check required context
        missing_context = [ctx for ctx in step.required_context 
                          if ctx not in self.context]
        if missing_context:
            print(f"⚠️  Missing required context: {missing_context}")
            return False
        
# Execute based on step type
        start_time = time.time()
        
        try:
            if step.step_type == StepType.AUTOMATED:
                result = self._execute_automated_step(step)
                
            elif step.step_type == StepType.HUMAN_DECISION:
                result = self._execute_human_decision_step(step)
                
            elif step.step_type == StepType.HUMAN_VALIDATION:
                result = self._execute_human_validation_step(step)
                
            elif step.step_type == StepType.NOTIFICATION:
                result = self._execute_notification_step(step)
                
            else:
                print(f"❌ Unknown step type: {step.step_type}")
                result = False
                
# Log execution
            execution_time = time.time() - start_time
            self.execution_log.append({
                'step': step.name,
                'success': result,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing step: {e}")
            return False
    
    def _execute_automated_step(self, step: RunbookStep) -> bool:
        """Execute automated step with progress indication"""
        print("🤖 Executing automated step...")
        
        if not step.action:
            print("❌ No action defined for automated step")
            return False
            
# Show what will be done
        print(f"   Action: {step.action.__name__}")
        
# Execute with timeout
        try:
            result = step.action(self.context)
            
# Validate if validation function provided
            if step.validation:
                print("   Validating result...")
                if not step.validation(result, self.context):
                    print("   ❌ Validation failed")
                    return False
                    
            print("   ✅ Step completed successfully")
            
# Update context with result
            if isinstance(result, dict):
                self.context.update(result)
                
            return True
            
        except Exception as e:
            print(f"   ❌ Execution failed: {e}")
            return False
    
    def _execute_human_decision_step(self, step: RunbookStep) -> bool:
        """Execute step requiring human decision"""
        print("👤 Human decision required:")
        
# Present context and options
        print("\n   Current context:")
        for key, value in self.context.items():
            if not key.startswith('_'):  # Skip internal keys
                print(f"     • {key}: {value}")
        
# Get decision
        print(f"\n   Question: {step.description}")
        
        if step.action:
# Custom decision handler
            decision = step.action(self.context)
        else:
# Default yes/no decision
            decision = input("   Proceed? (yes/no): ").lower().strip() == 'yes'
            
        self.context[f'{step.id}_decision'] = decision
        
        if decision:
            print("   ✅ Decision: Proceed")
            return True
        else:
            print("   ⏸️  Decision: Do not proceed")
            return False
    
    def _execute_human_validation_step(self, step: RunbookStep) -> bool:
        """Execute step requiring human validation"""
        print("👁️  Human validation required:")
        
# Execute action if provided
        if step.action:
            print("   Performing action...")
            result = step.action(self.context)
            
# Display result for validation
            print("\n   Result:")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"     • {key}: {value}")
            else:
                print(f"     {result}")
        
# Get validation
        print(f"\n   Please validate: {step.description}")
        validation = input("   Is the result correct? (yes/no): ").lower().strip() == 'yes'
        
        if validation:
            print("   ✅ Validation passed")
            return True
        else:
            print("   ❌ Validation failed")
            
# Offer to provide details
            details = input("   Provide details (optional): ")
            if details:
                self.context[f'{step.id}_validation_details'] = details
                
            return False
    
    def _execute_notification_step(self, step: RunbookStep) -> bool:
        """Execute notification step"""
        print("📢 Sending notifications...")
        
        if step.action:
            try:
                step.action(self.context)
                print("   ✅ Notifications sent")
                return True
            except Exception as e:
                print(f"   ❌ Failed to send notifications: {e}")
                return False
        else:
            print("   ⚠️  No notification handler configured")
            return True
    
    def _should_rollback(self) -> bool:
        """Ask operator if rollback should be performed"""
        print("\n⚠️  Step failed. Rollback is available.")
        response = input("Perform rollback? (yes/no): ").lower().strip()
        return response == 'yes'
    
    def _rollback_to_step(self, failed_step_index: int):
        """Rollback executed steps"""
        print("\n🔄 Starting rollback...")
        
# Rollback in reverse order
        for i in range(failed_step_index, -1, -1):
            step = self.steps[i]
            
            if step.rollback:
                print(f"\n  Rolling back: {step.name}")
                try:
                    step.rollback(self.context)
                    print(f"  ✅ Rolled back successfully")
                except Exception as e:
                    print(f"  ❌ Rollback failed: {e}")
                    print("  ⚠️  Manual intervention may be required")
    
    def _generate_summary(self):
        """Generate execution summary"""
        print(f"\n{'='*60}")
        print("EXECUTION SUMMARY")
        print(f"{'='*60}")
        
        total_time = sum(log['execution_time'] for log in self.execution_log)
        
        print(f"\nRunbook: {self.name}")
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Steps executed: {len(self.execution_log)}")
        
        print("\nStep details:")
        for log in self.execution_log:
            status = "✅" if log['success'] else "❌"
            print(f"  {status} {log['step']} ({log['execution_time']:.2f}s)")
        
# Key decisions made
        print("\nKey decisions:")
        for key, value in self.context.items():
            if '_decision' in key:
                print(f"  • {key}: {value}")
    
    def _check_permissions(self) -> bool:
        """Simulate permission check"""
# In real implementation, check actual permissions
        return True
    
    def _check_dependencies(self) -> bool:
        """Check system dependencies"""
# In real implementation, check actual dependencies
        return True
    
    def _validate_context(self) -> bool:
        """Validate required context is present"""
# In real implementation, validate context thoroughly
        return True
    
    def _verify_rollback_capability(self) -> bool:
        """Verify rollback is possible"""
# Check that critical steps have rollback defined
        critical_steps = [s for s in self.steps 
                         if s.step_type in [StepType.AUTOMATED, StepType.HUMAN_VALIDATION]]
        
        steps_with_rollback = [s for s in critical_steps if s.rollback is not None]
        
        if len(steps_with_rollback) < len(critical_steps) * 0.5:
            print("  ⚠️  Less than 50% of critical steps have rollback defined")
            
        return True

# Example: Database failover runbook
def create_database_failover_runbook() -> RunbookAutomation:
    """Create a runbook for database failover with human oversight"""
    
    runbook = RunbookAutomation(
        "Database Failover",
        "Failover primary database to standby with validation"
    )
    
# Step 1: Check current state
    def check_database_health(context):
        print("   Checking primary database health...")
# Simulate health check
        time.sleep(2)
        return {
            'primary_status': 'degraded',
            'standby_status': 'healthy',
            'replication_lag': '2 seconds',
            'last_transaction': '12:34:56'
        }
    
    runbook.add_step(RunbookStep(
        'health_check',
        'Check Database Health',
        'Verify current state of primary and standby databases',
        StepType.AUTOMATED,
        action=check_database_health
    ))
    
# Step 2: Human decision on failover
    def failover_decision(context):
        print(f"\n   Primary status: {context['primary_status']}")
        print(f"   Standby status: {context['standby_status']}")
        print(f"   Replication lag: {context['replication_lag']}")
        
        return input("\n   Proceed with failover? (yes/no): ").lower() == 'yes'
    
    runbook.add_step(RunbookStep(
        'failover_decision',
        'Failover Decision',
        'Decide whether to proceed with failover based on current state',
        StepType.HUMAN_DECISION,
        action=failover_decision
    ))
    
# Step 3: Stop writes to primary
    def stop_writes(context):
        print("   Setting primary to read-only mode...")
        time.sleep(2)
        print("   Waiting for in-flight transactions to complete...")
        time.sleep(3)
        return {'writes_stopped': True, 'pending_transactions': 0}
    
    def rollback_stop_writes(context):
        print("   Re-enabling writes to primary...")
        time.sleep(1)
        return {'writes_stopped': False}
    
    runbook.add_step(RunbookStep(
        'stop_writes',
        'Stop Writes to Primary',
        'Put primary database in read-only mode',
        StepType.AUTOMATED,
        action=stop_writes,
        rollback=rollback_stop_writes,
        required_context=['primary_status']
    ))
    
# Step 4: Verify replication caught up
    def verify_replication(context):
        print("   Checking replication status...")
        time.sleep(2)
        
# Simulate checking
        lag_seconds = 2
        for i in range(3):
            print(f"   Replication lag: {lag_seconds} seconds")
            time.sleep(1)
            lag_seconds = max(0, lag_seconds - 1)
            
        return {'replication_caught_up': lag_seconds == 0, 'final_lag': lag_seconds}
    
    def validate_replication(result, context):
        return result['replication_caught_up']
    
    runbook.add_step(RunbookStep(
        'verify_replication',
        'Verify Replication',
        'Ensure standby has caught up with primary',
        StepType.AUTOMATED,
        action=verify_replication,
        validation=validate_replication
    ))
    
# Step 5: Promote standby
    def promote_standby(context):
        print("   Promoting standby to primary...")
        time.sleep(3)
        return {'promotion_complete': True, 'new_primary': 'db-standby-1'}
    
    def rollback_promote_standby(context):
        print("   Demoting back to standby...")
        time.sleep(2)
        return {'promotion_complete': False}
    
    runbook.add_step(RunbookStep(
        'promote_standby',
        'Promote Standby',
        'Promote standby database to primary role',
        StepType.AUTOMATED,
        action=promote_standby,
        rollback=rollback_promote_standby,
        required_context=['replication_caught_up']
    ))
    
# Step 6: Update application configuration
    def update_app_config(context):
        print("   Updating application database endpoints...")
        time.sleep(2)
        
        apps_updated = ['web-frontend', 'api-service', 'batch-processor']
        for app in apps_updated:
            print(f"     ✓ {app}")
            time.sleep(0.5)
            
        return {'apps_updated': apps_updated, 'config_version': 'v2.1'}
    
    runbook.add_step(RunbookStep(
        'update_config',
        'Update Application Configuration',
        'Point applications to new primary database',
        StepType.AUTOMATED,
        action=update_app_config,
        required_context=['new_primary']
    ))
    
# Step 7: Validate failover
    def validate_failover(context):
        print("   Running validation checks...")
        
        checks = [
            ('Database accessibility', True),
            ('Write operations', True),
            ('Application connectivity', True),
            ('Performance metrics', True)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"     {status} {check_name}")
            if not passed:
                all_passed = False
            time.sleep(0.5)
            
        return {'validation_passed': all_passed, 'checks': checks}
    
    runbook.add_step(RunbookStep(
        'validate',
        'Validate Failover',
        'Confirm failover completed successfully',
        StepType.HUMAN_VALIDATION,
        action=validate_failover
    ))
    
# Step 8: Send notifications
    def send_notifications(context):
        print("   Notifying stakeholders...")
        
        notifications = [
            ('Ops team', 'Slack #ops-alerts'),
            ('On-call engineer', 'PagerDuty'),
            ('Database team', 'Email'),
            ('Status page', 'Public update')
        ]
        
        for recipient, channel in notifications:
            print(f"     → {recipient} via {channel}")
            time.sleep(0.5)
            
        return {'notifications_sent': len(notifications)}
    
    runbook.add_step(RunbookStep(
        'notify',
        'Send Notifications',
        'Notify relevant teams about failover completion',
        StepType.NOTIFICATION,
        action=send_notifications
    ))
    
    return runbook

# Execute the runbook
runbook = create_database_failover_runbook()
runbook.execute({
    'incident_id': 'INC-2024-001',
    'operator': 'john.doe',
    'reason': 'Primary database performance degradation'
})
```

### Questions
1. How does the runbook reduce cognitive load during incidents?
2. What decisions should always require human approval?
3. How would you handle runbook failures or timeouts?

## Exercise 5: Simulating Incident Response Under Stress

### Background
Cognitive load increases dramatically during incidents. This exercise simulates incident response scenarios to practice load management.

### Task
Build an incident response simulator that introduces stress factors and measures performance.

```python
import random
import threading
from datetime import datetime, timedelta
import queue
import time

class IncidentSimulator:
    """Simulate incident response scenarios with increasing cognitive load"""
    
    def __init__(self, operator_name: str):
        self.operator_name = operator_name
        self.incident_queue = queue.Queue()
        self.metrics = {
            'response_times': [],
            'errors': 0,
            'correct_actions': 0,
            'stress_level': 0,
            'decisions_made': []
        }
        self.active_incidents = {}
        self.simulation_running = False
        
    def start_simulation(self, difficulty: str = 'medium'):
        """Start incident simulation"""
        print(f"\n{'='*60}")
        print(f"INCIDENT RESPONSE SIMULATION")
        print(f"Operator: {self.operator_name}")
        print(f"Difficulty: {difficulty.upper()}")
        print(f"{'='*60}")
        
        print("\nSimulation will present various incidents.")
        print("Respond quickly and accurately to maintain system health.")
        print("\nCommands:")
        print("  investigate <incident_id> - Gather more information")
        print("  mitigate <incident_id> <action> - Take mitigation action")
        print("  escalate <incident_id> - Escalate to senior engineer")
        print("  resolve <incident_id> - Mark incident as resolved")
        print("  status - View current incidents")
        print("  quit - End simulation")
        
        input("\nPress Enter to start...")
        
        self.simulation_running = True
        
# Start incident generator thread
        generator = threading.Thread(
            target=self._generate_incidents,
            args=(difficulty,),
            daemon=True
        )
        generator.start()
        
# Start stress factor thread
        stressor = threading.Thread(
            target=self._apply_stress_factors,
            daemon=True
        )
        stressor.start()
        
# Main command loop
        self._command_loop()
        
# Show results
        self._show_results()
    
    def _generate_incidents(self, difficulty: str):
        """Generate incidents based on difficulty"""
        
# Incident templates
        incident_types = [
            {
                'type': 'high_latency',
                'title': 'API latency spike detected',
                'severity': 'high',
                'correct_action': 'scale',
                'investigation': 'Load balancer showing uneven distribution',
                'wrong_action_impact': 'latency_increase'
            },
            {
                'type': 'error_rate',
                'title': 'Error rate increasing',
                'severity': 'critical',
                'correct_action': 'rollback',
                'investigation': 'Recent deployment 30 minutes ago',
                'wrong_action_impact': 'error_cascade'
            },
            {
                'type': 'database_slow',
                'title': 'Database queries timing out',
                'severity': 'critical',
                'correct_action': 'kill_queries',
                'investigation': 'Long-running analytical query blocking others',
                'wrong_action_impact': 'data_inconsistency'
            },
            {
                'type': 'memory_leak',
                'title': 'Memory usage climbing',
                'severity': 'medium',
                'correct_action': 'restart',
                'investigation': 'Memory growing 10% per hour',
                'wrong_action_impact': 'service_crash'
            },
            {
                'type': 'ddos',
                'title': 'Unusual traffic spike',
                'severity': 'critical',
                'correct_action': 'enable_protection',
                'investigation': 'Traffic from single IP range',
                'wrong_action_impact': 'service_unavailable'
            }
        ]
        
# Difficulty settings
        settings = {
            'easy': {'interval': 30, 'simultaneous': 1, 'noise': 0.1},
            'medium': {'interval': 20, 'simultaneous': 2, 'noise': 0.3},
            'hard': {'interval': 10, 'simultaneous': 3, 'noise': 0.5},
            'chaos': {'interval': 5, 'simultaneous': 5, 'noise': 0.8}
        }
        
        config = settings.get(difficulty, settings['medium'])
        incident_id = 1000
        
        time.sleep(3)  # Initial delay
        
        while self.simulation_running:
# Generate incident
            if len(self.active_incidents) < config['simultaneous']:
                incident_template = random.choice(incident_types)
                
                incident = {
                    'id': f'INC-{incident_id}',
                    'timestamp': datetime.now(),
                    'type': incident_template['type'],
                    'title': incident_template['title'],
                    'severity': incident_template['severity'],
                    'correct_action': incident_template['correct_action'],
                    'investigation_result': incident_template['investigation'],
                    'wrong_action_impact': incident_template['wrong_action_impact'],
                    'investigated': False,
                    'status': 'active'
                }
                
                self.active_incidents[incident['id']] = incident
                incident_id += 1
                
# Alert operator
                self._alert_operator(incident)
                
# Add noise (false alarms)
                if random.random() < config['noise']:
                    self._generate_noise_alert()
            
# Wait before next incident
            time.sleep(config['interval'] + random.randint(-5, 5))
    
    def _apply_stress_factors(self):
        """Apply stress factors during simulation"""
        stress_events = [
            "🔔 Phone ringing - CEO asking for update",
            "⚠️  Another team reporting related issues",
            "📧 Urgent email from customer about impact",
            "🚨 Monitoring system showing cascade effects",
            "💬 Multiple Slack messages asking for status",
            "📱 On-call phone buzzing with alerts"
        ]
        
        while self.simulation_running:
            time.sleep(random.randint(15, 30))
            
            if self.active_incidents and random.random() < 0.6:
                print(f"\n{random.choice(stress_events)}")
                self.metrics['stress_level'] += 1
                print("> ", end='', flush=True)
    
    def _alert_operator(self, incident: Dict):
        """Alert operator about new incident"""
        severity_icons = {
            'critical': '🔴',
            'high': '🟡',
            'medium': '🟠'
        }
        
        print(f"\n\n{severity_icons.get(incident['severity'], '⚪')} NEW INCIDENT: {incident['id']}")
        print(f"   {incident['title']}")
        print(f"   Severity: {incident['severity'].upper()}")
        print(f"   Time: {incident['timestamp'].strftime('%H:%M:%S')}")
        print("\n> ", end='', flush=True)
    
    def _generate_noise_alert(self):
        """Generate false alarm to increase cognitive load"""
        noise_alerts = [
            "⚡ Spike in CPU usage (temporary)",
            "📊 Unusual pattern in metrics (benign)",
            "🔍 Security scan detected (authorized)",
            "🌡️  Temperature warning in rack 3 (HVAC cycling)"
        ]
        
        print(f"\n{random.choice(noise_alerts)}")
        print("> ", end='', flush=True)
    
    def _command_loop(self):
        """Process operator commands"""
        while self.simulation_running:
            try:
                command = input("> ").strip().lower()
                
                if command == 'quit':
                    self.simulation_running = False
                    break
                elif command == 'status':
                    self._show_status()
                elif command.startswith('investigate '):
                    incident_id = command.split()[1].upper()
                    self._investigate(incident_id)
                elif command.startswith('mitigate '):
                    parts = command.split()
                    if len(parts) >= 3:
                        incident_id = parts[1].upper()
                        action = parts[2]
                        self._mitigate(incident_id, action)
                elif command.startswith('escalate '):
                    incident_id = command.split()[1].upper()
                    self._escalate(incident_id)
                elif command.startswith('resolve '):
                    incident_id = command.split()[1].upper()
                    self._resolve(incident_id)
                else:
                    print("Unknown command. Type 'status' for current incidents.")
                    
            except (KeyboardInterrupt, EOFError):
                self.simulation_running = False
                break
            except Exception as e:
                print(f"Error processing command: {e}")
                self.metrics['errors'] += 1
    
    def _show_status(self):
        """Show current incident status"""
        if not self.active_incidents:
            print("\n✅ No active incidents")
            return
            
        print(f"\n{'='*50}")
        print("ACTIVE INCIDENTS")
        print(f"{'='*50}")
        
        for incident in self.active_incidents.values():
            if incident['status'] == 'active':
                icon = '🔴' if incident['severity'] == 'critical' else '🟡'
                investigated = '🔍' if incident['investigated'] else ''
                age = (datetime.now() - incident['timestamp']).seconds
                
                print(f"{icon} {incident['id']}: {incident['title']} {investigated}")
                print(f"   Age: {age}s | Severity: {incident['severity']}")
    
    def _investigate(self, incident_id: str):
        """Investigate an incident"""
        start_time = time.time()
        
        incident = self.active_incidents.get(incident_id)
        if not incident:
            print(f"❌ Unknown incident: {incident_id}")
            self.metrics['errors'] += 1
            return
            
        print(f"\n🔍 Investigating {incident_id}...")
        time.sleep(2)  # Simulate investigation time
        
        print(f"   Finding: {incident['investigation_result']}")
        incident['investigated'] = True
        
# Log response time
        response_time = time.time() - start_time
        self.metrics['response_times'].append(response_time)
        
# Suggest actions based on type
        suggestions = {
            'high_latency': ['scale - Add more instances', 'restart - Restart services', 'cache - Enable caching'],
            'error_rate': ['rollback - Revert deployment', 'disable - Disable feature', 'restart - Restart services'],
            'database_slow': ['kill_queries - Kill long queries', 'scale - Add read replicas', 'optimize - Run optimizer'],
            'memory_leak': ['restart - Rolling restart', 'scale - Add instances', 'gc - Force garbage collection'],
            'ddos': ['enable_protection - Enable DDoS protection', 'block - Block IP range', 'scale - Add capacity']
        }
        
        print("\n   Possible actions:")
        for action in suggestions.get(incident['type'], []):
            print(f"     • {action}")
    
    def _mitigate(self, incident_id: str, action: str):
        """Apply mitigation action"""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            print(f"❌ Unknown incident: {incident_id}")
            self.metrics['errors'] += 1
            return
            
        print(f"\n⚡ Applying mitigation: {action} to {incident_id}")
        time.sleep(3)  # Simulate action time
        
# Check if correct action
        if action == incident['correct_action']:
            print(f"✅ Mitigation successful! {incident['title']} improving.")
            incident['status'] = 'mitigated'
            self.metrics['correct_actions'] += 1
            
# Auto-resolve after successful mitigation
            time.sleep(2)
            print(f"✅ {incident_id} auto-resolved after successful mitigation")
            incident['status'] = 'resolved'
        else:
            print(f"⚠️  Mitigation had limited effect.")
            print(f"   Impact: {incident['wrong_action_impact']}")
            self.metrics['errors'] += 1
            
# Increase stress
            self.metrics['stress_level'] += 2
            
        self.metrics['decisions_made'].append({
            'incident': incident_id,
            'action': action,
            'correct': action == incident['correct_action'],
            'timestamp': datetime.now()
        })
    
    def _escalate(self, incident_id: str):
        """Escalate incident"""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            print(f"❌ Unknown incident: {incident_id}")
            return
            
        print(f"\n📞 Escalating {incident_id} to senior engineer...")
        time.sleep(2)
        
        print(f"✅ Incident escalated. Senior engineer taking over.")
        incident['status'] = 'escalated'
        
# Neutral outcome - neither correct nor wrong
        self.metrics['decisions_made'].append({
            'incident': incident_id,
            'action': 'escalate',
            'correct': None,  # Neutral
            'timestamp': datetime.now()
        })
    
    def _resolve(self, incident_id: str):
        """Resolve incident"""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            print(f"❌ Unknown incident: {incident_id}")
            return
            
        if incident['status'] == 'active':
            print(f"⚠️  Resolving incident without mitigation may cause recurrence")
            
        incident['status'] = 'resolved'
        print(f"✅ {incident_id} marked as resolved")
    
    def _show_results(self):
        """Show simulation results"""
        print(f"\n\n{'='*60}")
        print("SIMULATION RESULTS")
        print(f"{'='*60}")
        
# Calculate metrics
        total_incidents = len(self.active_incidents)
        resolved = sum(1 for i in self.active_incidents.values() 
                      if i['status'] in ['resolved', 'mitigated'])
        escalated = sum(1 for i in self.active_incidents.values() 
                       if i['status'] == 'escalated')
        
        if self.metrics['response_times']:
            avg_response = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        else:
            avg_response = 0
            
        correct_decisions = sum(1 for d in self.metrics['decisions_made'] 
                               if d['correct'] is True)
        total_decisions = len([d for d in self.metrics['decisions_made'] 
                              if d['correct'] is not None])
        
# Display results
        print(f"\nIncident Handling:")
        print(f"  Total incidents: {total_incidents}")
        print(f"  Resolved/Mitigated: {resolved}")
        print(f"  Escalated: {escalated}")
        print(f"  Unresolved: {total_incidents - resolved - escalated}")
        
        print(f"\nPerformance Metrics:")
        print(f"  Average response time: {avg_response:.1f}s")
        print(f"  Correct actions: {self.metrics['correct_actions']}")
        print(f"  Errors: {self.metrics['errors']}")
        print(f"  Stress events: {self.metrics['stress_level']}")
        
        if total_decisions > 0:
            accuracy = (correct_decisions / total_decisions) * 100
            print(f"  Decision accuracy: {accuracy:.1f}%")
        
# Performance rating
        score = 0
        score += min(30, resolved * 10)  # Up to 30 points for resolution
        score += min(20, (5 - self.metrics['errors']) * 4)  # Up to 20 for few errors
        score += min(30, (10 - avg_response) * 3)  # Up to 30 for fast response
        score += min(20, self.metrics['correct_actions'] * 5)  # Up to 20 for correct actions
        
        rating = "Expert" if score >= 80 else "Proficient" if score >= 60 else "Developing"
        
        print(f"\nOverall Rating: {rating} ({score}/100)")
        
# Recommendations
        print("\nRecommendations:")
        if avg_response > 10:
            print("  • Practice quick incident triage")
        if self.metrics['errors'] > 3:
            print("  • Double-check commands before execution")
        if self.metrics['stress_level'] > 5:
            print("  • Develop stress management techniques")
        if correct_decisions < total_decisions * 0.7:
            print("  • Study incident patterns and correct mitigations")

# Run the simulation
simulator = IncidentSimulator("Alice")
simulator.start_simulation(difficulty='medium')
```

### Questions
1. How did stress factors affect your decision-making?
2. What strategies helped manage multiple simultaneous incidents?
3. How would you design alerts to minimize cognitive load during incidents?

## Summary

These exercises demonstrate practical approaches to implementing the Law of Cognitive Load in distributed systems:

1. **Clear Communication**: Transform technical errors into actionable messages
2. **Progressive Disclosure**: Show only what's needed, when it's needed
3. **Smart Prioritization**: Surface what matters, suppress the noise
4. **Guided Automation**: Automate routine tasks while keeping humans in control
5. **Stress Testing**: Practice operating under cognitive load before real incidents

Remember: The goal is not to eliminate cognitive load entirely, but to manage it effectively so operators can make good decisions when it matters most.

## Next Steps

1. Implement these patterns in your own systems
2. Measure cognitive load through response times and error rates
3. Continuously refine based on operator feedback
4. Share learnings with your team to build better human-system interfaces

The best systems are not just technically sound—they're designed for the humans who operate them.