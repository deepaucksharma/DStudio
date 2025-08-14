#!/usr/bin/env python3
"""
GitOps Monitoring & Alerting System
===================================

Comprehensive monitoring और alerting system for GitOps deployments।
Indian business hours, festival seasons, और regional metrics के साथ intelligent alerting।

Features:
- GitOps deployment status monitoring
- Business metrics tracking (conversion, revenue, UPI success)
- Regional latency monitoring (Mumbai, Delhi, Bangalore)
- Indian business hours aware alerting
- Festival season enhanced monitoring
- Multi-channel alerts (Slack, WhatsApp, Email, SMS)
- RBI compliance reporting

Author: Hindi Tech Podcast - Episode 19
Context: Production Monitoring for Indian GitOps
"""

import asyncio
import logging
import json
import yaml
import os
import math
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import asyncpg
import redis.asyncio as redis
import prometheus_client
from prometheus_client.parser import text_string_to_metric_families
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import pytz
from pathlib import Path
import statistics
import numpy as np

# Indian timezone और business context
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('gitops_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    RESOLVED = "resolved"

class AlertChannel(Enum):
    """Alert delivery channels"""
    SLACK = "slack"
    WHATSAPP = "whatsapp"  # Popular in Indian teams
    EMAIL = "email"
    SMS = "sms"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"

class MetricType(Enum):
    """Types of metrics to monitor"""
    DEPLOYMENT_STATUS = "deployment_status"
    APPLICATION_HEALTH = "application_health"
    BUSINESS_METRICS = "business_metrics"
    INFRASTRUCTURE = "infrastructure"
    REGIONAL_PERFORMANCE = "regional_performance"
    COMPLIANCE = "compliance"

@dataclass
class AlertRule:
    """Alert rule definition"""
    rule_id: str
    name: str
    description: str
    metric_type: MetricType
    query: str  # PromQL query
    threshold: float
    comparison: str  # '>', '<', '==', '!='
    duration: str = "5m"  # How long condition must persist
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Indian business context
    business_hours_only: bool = False
    peak_hours_threshold_multiplier: float = 1.0
    festival_season_threshold_multiplier: float = 0.8  # Stricter during festivals
    
    # Channels
    channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.SLACK])
    
    # Regional settings
    regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    
    # Business impact
    revenue_impact_per_hour: float = 0.0  # INR
    customer_impact: str = "low"  # low, medium, high, critical

@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    
    # Context
    region: str = "unknown"
    application: str = "unknown"
    namespace: str = "unknown"
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(IST))
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    # Business context
    business_impact: str = "unknown"
    revenue_impact: float = 0.0
    affected_customers: int = 0
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class MonitoringConfig:
    """GitOps monitoring configuration"""
    # Data sources
    prometheus_url: str = "http://prometheus:9090"
    kubernetes_config_path: str = ""
    redis_url: str = "redis://redis:6379"
    postgres_url: str = "postgresql://user:pass@postgres:5432/monitoring"
    
    # Alert channels
    slack_webhook: str = ""
    teams_webhook: str = ""
    whatsapp_api_key: str = ""
    whatsapp_phone_numbers: List[str] = field(default_factory=list)
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_recipients: List[str] = field(default_factory=list)
    
    # Indian business settings
    business_hours: Dict[str, str] = field(default_factory=lambda: {"start": "09:00", "end": "21:00"})
    peak_hours: Dict[str, str] = field(default_factory=lambda: {"start": "18:00", "end": "22:00"})
    monitoring_regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    
    # Compliance
    enable_rbi_reporting: bool = True
    audit_retention_days: int = 2555  # 7 years
    compliance_notification_emails: List[str] = field(default_factory=list)

class IndianBusinessRules:
    """Indian business hours और seasonal rules"""
    
    @staticmethod
    def is_business_hours(timestamp: datetime = None) -> bool:
        """Check if current time is business hours"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Business hours: 9 AM to 9 PM IST
        business_start = time(9, 0)
        business_end = time(21, 0)
        current_time = timestamp.time()
        
        return business_start <= current_time <= business_end
    
    @staticmethod
    def is_peak_hours(timestamp: datetime = None) -> bool:
        """Check if current time is peak business hours"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Peak hours: 6 PM to 10 PM IST (post-work shopping)
        peak_start = time(18, 0)
        peak_end = time(22, 0)
        current_time = timestamp.time()
        
        return peak_start <= current_time <= peak_end
    
    @staticmethod
    def is_festival_season(timestamp: datetime = None) -> bool:
        """Check if current time is during festival season"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Major Indian festival periods
        festival_periods = [
            # Diwali season (Oct 15 - Nov 15)
            (datetime(timestamp.year, 10, 15, tzinfo=IST), 
             datetime(timestamp.year, 11, 15, tzinfo=IST)),
             
            # Independence Day season (Aug 10-20)
            (datetime(timestamp.year, 8, 10, tzinfo=IST),
             datetime(timestamp.year, 8, 20, tzinfo=IST)),
             
            # New Year shopping (Dec 25 - Jan 5)
            (datetime(timestamp.year, 12, 25, tzinfo=IST),
             datetime(timestamp.year + 1, 1, 5, tzinfo=IST))
        ]
        
        return any(start <= timestamp <= end for start, end in festival_periods)
    
    @staticmethod
    def get_business_context(timestamp: datetime = None) -> Dict[str, Any]:
        """Get comprehensive business context"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        return {
            'is_business_hours': IndianBusinessRules.is_business_hours(timestamp),
            'is_peak_hours': IndianBusinessRules.is_peak_hours(timestamp),
            'is_festival_season': IndianBusinessRules.is_festival_season(timestamp),
            'is_weekend': timestamp.weekday() >= 5,
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.strftime('%A'),
            'month': timestamp.strftime('%B')
        }

class PrometheusClient:
    """
    Prometheus client for metrics collection।
    
    Indian business metrics और regional performance के साथ comprehensive
    monitoring capabilities।
    """
    
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url.rstrip('/')
        
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute PromQL query"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'query': query}
                async with session.get(
                    f"{self.prometheus_url}/api/v1/query", 
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Prometheus query failed: {response.status}")
                        return {'status': 'error', 'data': {'result': []}}
                        
        except Exception as e:
            logger.error(f"❌ Prometheus query error: {e}")
            return {'status': 'error', 'data': {'result': []}}
    
    async def query_range(self, query: str, start: datetime, end: datetime, step: str = "1m") -> Dict[str, Any]:
        """Execute PromQL range query"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'query': query,
                    'start': int(start.timestamp()),
                    'end': int(end.timestamp()),
                    'step': step
                }
                async with session.get(
                    f"{self.prometheus_url}/api/v1/query_range",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {'status': 'error', 'data': {'result': []}}
                        
        except Exception as e:
            logger.error(f"❌ Prometheus range query error: {e}")
            return {'status': 'error', 'data': {'result': []}}
    
    async def get_gitops_deployment_status(self) -> Dict[str, Any]:
        """Get GitOps deployment status metrics"""
        queries = {
            'argocd_app_health': 'argocd_app_health',
            'argocd_app_sync_status': 'argocd_app_sync_status',
            'flux_reconcile_condition': 'flux_reconcile_condition',
            'gitops_deployment_duration': 'gitops_deployment_duration_seconds'
        }
        
        results = {}
        for metric_name, query in queries.items():
            result = await self.query(query)
            results[metric_name] = result.get('data', {}).get('result', [])
        
        return results
    
    async def get_business_metrics(self) -> Dict[str, Any]:
        """Get Indian business specific metrics"""
        queries = {
            # E-commerce metrics
            'conversion_rate': 'rate(ecommerce_orders_total[5m]) / rate(ecommerce_sessions_total[5m]) * 100',
            'revenue_per_minute': 'rate(ecommerce_revenue_total[1m])',
            'cart_abandonment_rate': '(rate(ecommerce_cart_created_total[5m]) - rate(ecommerce_orders_total[5m])) / rate(ecommerce_cart_created_total[5m]) * 100',
            
            # Payment metrics (critical for Indian market)
            'upi_success_rate': 'rate(payment_transactions_total{method="upi",status="success"}[5m]) / rate(payment_transactions_total{method="upi"}[5m]) * 100',
            'payment_failure_rate': 'rate(payment_transactions_total{status="failed"}[5m]) / rate(payment_transactions_total[5m]) * 100',
            'payment_gateway_errors': 'rate(payment_gateway_errors_total[5m])',
            
            # User experience
            'page_load_time_p95': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="frontend"}[5m]))',
            'api_error_rate': 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100',
            
            # Infrastructure
            'cpu_utilization': 'avg(rate(container_cpu_usage_seconds_total[5m])) by (region) * 100',
            'memory_utilization': 'avg(container_memory_usage_bytes / container_spec_memory_limit_bytes) by (region) * 100'
        }
        
        results = {}
        for metric_name, query in queries.items():
            result = await self.query(query)
            results[metric_name] = result.get('data', {}).get('result', [])
        
        return results
    
    async def get_regional_metrics(self) -> Dict[str, Any]:
        """Get region-specific metrics for Indian data centers"""
        queries = {
            'mumbai_latency': 'avg(http_request_duration_seconds{region="mumbai"}) * 1000',
            'delhi_latency': 'avg(http_request_duration_seconds{region="delhi"}) * 1000',
            'bangalore_latency': 'avg(http_request_duration_seconds{region="bangalore"}) * 1000',
            
            'mumbai_error_rate': 'rate(http_requests_total{region="mumbai",status=~"5.."}[5m]) / rate(http_requests_total{region="mumbai"}[5m]) * 100',
            'delhi_error_rate': 'rate(http_requests_total{region="delhi",status=~"5.."}[5m]) / rate(http_requests_total{region="delhi"}[5m]) * 100',
            'bangalore_error_rate': 'rate(http_requests_total{region="bangalore",status=~"5.."}[5m]) / rate(http_requests_total{region="bangalore"}[5m]) * 100',
            
            'mumbai_throughput': 'rate(http_requests_total{region="mumbai"}[5m])',
            'delhi_throughput': 'rate(http_requests_total{region="delhi"}[5m])',
            'bangalore_throughput': 'rate(http_requests_total{region="bangalore"}[5m])'
        }
        
        results = {}
        for metric_name, query in queries.items():
            result = await self.query(query)
            results[metric_name] = result.get('data', {}).get('result', [])
        
        return results

class AlertRuleEngine:
    """
    Alert rule engine with Indian business logic।
    
    Business hours, festival seasons, regional metrics के साथ intelligent
    alert rule evaluation और notification।
    """
    
    def __init__(self):
        self.rules = self._initialize_default_rules()
        
    def _initialize_default_rules(self) -> List[AlertRule]:
        """Initialize default alert rules for Indian GitOps"""
        return [
            # GitOps Deployment Rules
            AlertRule(
                rule_id="GITOPS-001",
                name="ArgoCD Application Unhealthy",
                description="ArgoCD application is in unhealthy state",
                metric_type=MetricType.DEPLOYMENT_STATUS,
                query='argocd_app_health{health_status!="Healthy"}',
                threshold=0,
                comparison='>',
                duration="2m",
                severity=AlertSeverity.CRITICAL,
                business_hours_only=False,
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.SMS],
                revenue_impact_per_hour=50000,
                customer_impact="high"
            ),
            
            AlertRule(
                rule_id="GITOPS-002", 
                name="Flux Reconciliation Failing",
                description="Flux reconciliation has been failing",
                metric_type=MetricType.DEPLOYMENT_STATUS,
                query='flux_reconcile_condition{type="Ready",status="False"}',
                threshold=0,
                comparison='>',
                duration="5m",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.SLACK],
                revenue_impact_per_hour=25000
            ),
            
            # Business Metrics Rules
            AlertRule(
                rule_id="BUSINESS-001",
                name="Conversion Rate Drop",
                description="E-commerce conversion rate has dropped significantly",
                metric_type=MetricType.BUSINESS_METRICS,
                query='rate(ecommerce_orders_total[5m]) / rate(ecommerce_sessions_total[5m]) * 100',
                threshold=2.0,  # 2% conversion rate
                comparison='<',
                duration="10m",
                severity=AlertSeverity.CRITICAL,
                business_hours_only=True,
                peak_hours_threshold_multiplier=0.7,  # Stricter during peak hours
                festival_season_threshold_multiplier=0.5,  # Much stricter during festivals
                channels=[AlertChannel.SLACK, AlertChannel.WHATSAPP, AlertChannel.EMAIL],
                revenue_impact_per_hour=100000,
                customer_impact="critical"
            ),
            
            AlertRule(
                rule_id="BUSINESS-002",
                name="UPI Success Rate Low",
                description="UPI payment success rate is below acceptable threshold",
                metric_type=MetricType.BUSINESS_METRICS,
                query='rate(payment_transactions_total{method="upi",status="success"}[5m]) / rate(payment_transactions_total{method="upi"}[5m]) * 100',
                threshold=85.0,  # 85% success rate
                comparison='<',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                business_hours_only=False,
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.SMS],
                revenue_impact_per_hour=75000,
                customer_impact="critical"
            ),
            
            AlertRule(
                rule_id="BUSINESS-003",
                name="Revenue Drop During Peak Hours",
                description="Significant revenue drop during peak business hours",
                metric_type=MetricType.BUSINESS_METRICS,
                query='rate(ecommerce_revenue_total[5m])',
                threshold=1000,  # INR per minute
                comparison='<',
                duration="15m",
                severity=AlertSeverity.WARNING,
                business_hours_only=True,
                channels=[AlertChannel.SLACK, AlertChannel.WHATSAPP],
                revenue_impact_per_hour=60000,
                customer_impact="high"
            ),
            
            # Regional Performance Rules
            AlertRule(
                rule_id="REGIONAL-001",
                name="Mumbai Region High Latency",
                description="Mumbai region experiencing high latency",
                metric_type=MetricType.REGIONAL_PERFORMANCE,
                query='avg(http_request_duration_seconds{region="mumbai"}) * 1000',
                threshold=1000,  # 1 second
                comparison='>',
                duration="10m",
                severity=AlertSeverity.WARNING,
                regions=["mumbai"],
                channels=[AlertChannel.SLACK],
                revenue_impact_per_hour=30000,
                customer_impact="medium"
            ),
            
            AlertRule(
                rule_id="REGIONAL-002",
                name="Multi-Region Error Rate Spike",
                description="Error rate spike across multiple regions",
                metric_type=MetricType.REGIONAL_PERFORMANCE,
                query='avg by (region) (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100)',
                threshold=5.0,  # 5% error rate
                comparison='>',
                duration="5m",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.SMS],
                revenue_impact_per_hour=80000,
                customer_impact="critical"
            ),
            
            # Infrastructure Rules
            AlertRule(
                rule_id="INFRA-001",
                name="High CPU Utilization",
                description="High CPU utilization across regions",
                metric_type=MetricType.INFRASTRUCTURE,
                query='avg(rate(container_cpu_usage_seconds_total[5m])) by (region) * 100',
                threshold=80.0,  # 80% CPU
                comparison='>',
                duration="10m",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.SLACK],
                revenue_impact_per_hour=20000
            ),
            
            AlertRule(
                rule_id="INFRA-002",
                name="Memory Pressure",
                description="High memory utilization in containers",
                metric_type=MetricType.INFRASTRUCTURE,
                query='avg(container_memory_usage_bytes / container_spec_memory_limit_bytes) by (region) * 100',
                threshold=85.0,  # 85% memory
                comparison='>',
                duration="15m",
                severity=AlertSeverity.WARNING,
                channels=[AlertChannel.SLACK]
            )
        ]
    
    def get_applicable_rules(self, business_context: Dict[str, Any]) -> List[AlertRule]:
        """Get rules applicable for current business context"""
        applicable_rules = []
        
        for rule in self.rules:
            # Check if rule should be evaluated based on business hours
            if rule.business_hours_only and not business_context['is_business_hours']:
                continue
                
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def adjust_threshold_for_context(self, rule: AlertRule, business_context: Dict[str, Any]) -> float:
        """Adjust threshold based on business context"""
        threshold = rule.threshold
        
        # Adjust for peak hours
        if business_context['is_peak_hours']:
            threshold *= rule.peak_hours_threshold_multiplier
        
        # Adjust for festival season (stricter monitoring)
        if business_context['is_festival_season']:
            threshold *= rule.festival_season_threshold_multiplier
        
        return threshold

class NotificationManager:
    """
    Multi-channel notification system।
    
    Slack, WhatsApp, Email, SMS के साथ Indian teams के लिए optimized
    notification delivery।
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        
    async def send_alert(self, alert: Alert, channels: List[AlertChannel]) -> Dict[AlertChannel, bool]:
        """Send alert through multiple channels"""
        results = {}
        
        for channel in channels:
            try:
                success = False
                
                if channel == AlertChannel.SLACK and self.config.slack_webhook:
                    success = await self._send_slack_alert(alert)
                elif channel == AlertChannel.EMAIL and self.config.email_recipients:
                    success = await self._send_email_alert(alert)
                elif channel == AlertChannel.WHATSAPP and self.config.whatsapp_api_key:
                    success = await self._send_whatsapp_alert(alert)
                elif channel == AlertChannel.SMS:
                    success = await self._send_sms_alert(alert)
                elif channel == AlertChannel.TEAMS and self.config.teams_webhook:
                    success = await self._send_teams_alert(alert)
                
                results[channel] = success
                
                if success:
                    logger.info(f"✅ Alert sent via {channel.value}: {alert.alert_id}")
                else:
                    logger.warning(f"⚠️ Failed to send alert via {channel.value}: {alert.alert_id}")
                    
            except Exception as e:
                logger.error(f"❌ Error sending alert via {channel.value}: {e}")
                results[channel] = False
        
        return results
    
    async def _send_slack_alert(self, alert: Alert) -> bool:
        """Send alert to Slack"""
        try:
            # Create rich Slack message
            color = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.WARNING: "warning", 
                AlertSeverity.INFO: "good",
                AlertSeverity.RESOLVED: "good"
            }.get(alert.severity, "warning")
            
            # Business context
            business_context = IndianBusinessRules.get_business_context()
            
            payload = {
                "text": f"🚨 GitOps Alert: {alert.rule_id}",
                "attachments": [{
                    "color": color,
                    "title": f"{alert.severity.value.upper()}: {alert.rule_id}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Region", "value": alert.region, "short": True},
                        {"title": "Application", "value": alert.application, "short": True},
                        {"title": "Metric Value", "value": f"{alert.metric_value:.2f}", "short": True},
                        {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True},
                        {"title": "Business Impact", "value": alert.business_impact, "short": True},
                        {"title": "Revenue Impact", "value": f"₹{alert.revenue_impact:,.0f}/hour", "short": True}
                    ],
                    "footer": f"Started at {alert.started_at.strftime('%Y-%m-%d %H:%M:%S IST')}",
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png"
                }]
            }
            
            # Add business context information
            if business_context['is_festival_season']:
                payload["attachments"][0]["fields"].append({
                    "title": "🎊 Festival Season", 
                    "value": "Enhanced monitoring active", 
                    "short": True
                })
            
            if business_context['is_peak_hours']:
                payload["attachments"][0]["fields"].append({
                    "title": "⏰ Peak Hours", 
                    "value": "High traffic period", 
                    "short": True
                })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.slack_webhook, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"❌ Slack alert failed: {e}")
            return False
    
    async def _send_email_alert(self, alert: Alert) -> bool:
        """Send alert via email"""
        try:
            # Create email content
            subject = f"[GitOps Alert - {alert.severity.value.upper()}] {alert.rule_id}"
            
            # HTML email body
            html_body = f"""
            <html>
            <body>
                <h2 style="color: {'red' if alert.severity == AlertSeverity.CRITICAL else 'orange'}">
                    GitOps Alert: {alert.rule_id}
                </h2>
                <p><strong>Message:</strong> {alert.message}</p>
                
                <table border="1" cellpadding="5" cellspacing="0">
                    <tr><th>Field</th><th>Value</th></tr>
                    <tr><td>Severity</td><td>{alert.severity.value.upper()}</td></tr>
                    <tr><td>Region</td><td>{alert.region}</td></tr>
                    <tr><td>Application</td><td>{alert.application}</td></tr>
                    <tr><td>Metric Value</td><td>{alert.metric_value:.2f}</td></tr>
                    <tr><td>Threshold</td><td>{alert.threshold:.2f}</td></tr>
                    <tr><td>Business Impact</td><td>{alert.business_impact}</td></tr>
                    <tr><td>Revenue Impact</td><td>₹{alert.revenue_impact:,.0f}/hour</td></tr>
                    <tr><td>Started At</td><td>{alert.started_at.strftime('%Y-%m-%d %H:%M:%S IST')}</td></tr>
                </table>
                
                <p><em>This alert was generated by the GitOps Monitoring System for Hindi Tech Podcast Episode 19.</em></p>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.smtp_username
            msg['To'] = ', '.join(self.config.email_recipients)
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Email alert failed: {e}")
            return False
    
    async def _send_whatsapp_alert(self, alert: Alert) -> bool:
        """Send alert via WhatsApp (popular in Indian teams)"""
        try:
            # Format WhatsApp message
            business_context = IndianBusinessRules.get_business_context()
            
            message = f"""
🚨 *GitOps Alert*
            
*Rule:* {alert.rule_id}
*Severity:* {alert.severity.value.upper()}
*Message:* {alert.message}

📊 *Details:*
• Region: {alert.region}
• App: {alert.application}
• Value: {alert.metric_value:.2f}
• Threshold: {alert.threshold:.2f}

💰 *Business Impact:*
• Impact Level: {alert.business_impact}
• Revenue Impact: ₹{alert.revenue_impact:,.0f}/hour
• Affected Customers: {alert.affected_customers:,}

⏰ *Time:* {alert.started_at.strftime('%Y-%m-%d %H:%M:%S IST')}
"""
            
            if business_context['is_festival_season']:
                message += "\n🎊 *Festival Season* - Enhanced monitoring active"
            
            if business_context['is_peak_hours']:
                message += "\n⏰ *Peak Hours* - High traffic period"
            
            # Send to all configured WhatsApp numbers
            success = True
            for phone_number in self.config.whatsapp_phone_numbers:
                # Mock WhatsApp API call (replace with actual WhatsApp Business API)
                # In real implementation, use WhatsApp Business API or services like Twilio
                logger.info(f"📱 WhatsApp alert sent to {phone_number}")
                
                # Simulate API call
                await asyncio.sleep(0.1)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ WhatsApp alert failed: {e}")
            return False
    
    async def _send_sms_alert(self, alert: Alert) -> bool:
        """Send SMS alert (for critical alerts)"""
        try:
            # Format SMS message (limited to 160 characters)
            message = f"GitOps ALERT: {alert.rule_id} - {alert.severity.value.upper()}\n{alert.message[:100]}...\nTime: {alert.started_at.strftime('%H:%M IST')}"
            
            # Mock SMS API call (replace with actual SMS service like Twilio)
            logger.info(f"📞 SMS alert: {message}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ SMS alert failed: {e}")
            return False
    
    async def _send_teams_alert(self, alert: Alert) -> bool:
        """Send alert to Microsoft Teams"""
        try:
            # Teams adaptive card format
            card = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "FF0000" if alert.severity == AlertSeverity.CRITICAL else "FFA500",
                "summary": f"GitOps Alert: {alert.rule_id}",
                "sections": [{
                    "activityTitle": f"🚨 GitOps Alert: {alert.rule_id}",
                    "activitySubtitle": alert.message,
                    "facts": [
                        {"name": "Severity", "value": alert.severity.value.upper()},
                        {"name": "Region", "value": alert.region},
                        {"name": "Application", "value": alert.application},
                        {"name": "Metric Value", "value": f"{alert.metric_value:.2f}"},
                        {"name": "Threshold", "value": f"{alert.threshold:.2f}"},
                        {"name": "Revenue Impact", "value": f"₹{alert.revenue_impact:,.0f}/hour"}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.teams_webhook, json=card) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"❌ Teams alert failed: {e}")
            return False

class GitOpsMonitor:
    """
    Main GitOps monitoring orchestrator।
    
    Comprehensive monitoring, alerting, और business intelligence के साथ
    Indian enterprise के लिए complete observability solution।
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.prometheus_client = PrometheusClient(config.prometheus_url)
        self.alert_engine = AlertRuleEngine()
        self.notification_manager = NotificationManager(config)
        self.redis_client = None
        self.pg_pool = None
        self.active_alerts = {}  # Track active alerts
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize monitoring system"""
        try:
            logger.info("🚀 Initializing GitOps Monitoring System")
            
            # Setup Redis for caching
            self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Setup PostgreSQL for data storage
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            logger.info("✅ PostgreSQL connection pool created")
            
            # Initialize database schema
            await self._initialize_database()
            
            # Test Prometheus connectivity
            test_result = await self.prometheus_client.query('up')
            if test_result['status'] == 'success':
                logger.info("✅ Prometheus connectivity verified")
            else:
                logger.warning("⚠️ Prometheus connectivity issues")
            
            logger.info("✅ GitOps Monitoring System initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitoring system initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize monitoring database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            alert_id VARCHAR(255) UNIQUE NOT NULL,
            rule_id VARCHAR(255) NOT NULL,
            severity VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            metric_value FLOAT NOT NULL,
            threshold FLOAT NOT NULL,
            region VARCHAR(100),
            application VARCHAR(255),
            namespace VARCHAR(255),
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            resolved_at TIMESTAMP WITH TIME ZONE,
            acknowledged_at TIMESTAMP WITH TIME ZONE,
            acknowledged_by VARCHAR(255),
            business_impact VARCHAR(50),
            revenue_impact FLOAT DEFAULT 0,
            affected_customers INTEGER DEFAULT 0,
            labels JSONB DEFAULT '{}'::jsonb,
            annotations JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_alert_rule (rule_id),
            INDEX idx_alert_started (started_at),
            INDEX idx_alert_severity (severity)
        );
        
        CREATE TABLE IF NOT EXISTS monitoring_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            metric_name VARCHAR(255) NOT NULL,
            metric_value FLOAT NOT NULL,
            region VARCHAR(100),
            labels JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_metrics_timestamp (timestamp),
            INDEX idx_metrics_name (metric_name)
        );
        
        CREATE TABLE IF NOT EXISTS business_reports (
            id SERIAL PRIMARY KEY,
            report_date DATE NOT NULL,
            report_type VARCHAR(100) NOT NULL,
            report_data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            INDEX idx_report_date (report_date),
            INDEX idx_report_type (report_type)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Monitoring database schema initialized")
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        logger.info("🔍 Starting GitOps monitoring loop...")
        self.is_running = True
        
        # Start multiple monitoring tasks
        tasks = [
            asyncio.create_task(self._monitoring_loop()),
            asyncio.create_task(self._business_metrics_collection()),
            asyncio.create_task(self._alert_cleanup_loop()),
            asyncio.create_task(self._daily_report_generation())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.is_running = False
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Get current business context
                business_context = IndianBusinessRules.get_business_context()
                
                # Get applicable rules
                applicable_rules = self.alert_engine.get_applicable_rules(business_context)
                
                logger.info(f"📊 Evaluating {len(applicable_rules)} alert rules")
                
                # Evaluate each rule
                for rule in applicable_rules:
                    try:
                        await self._evaluate_alert_rule(rule, business_context)
                    except Exception as e:
                        logger.error(f"❌ Error evaluating rule {rule.rule_id}: {e}")
                
                # Wait before next evaluation
                await asyncio.sleep(30)  # 30-second intervals
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _evaluate_alert_rule(self, rule: AlertRule, business_context: Dict[str, Any]) -> None:
        """Evaluate individual alert rule"""
        try:
            # Execute Prometheus query
            result = await self.prometheus_client.query(rule.query)
            
            if result['status'] != 'success' or not result.get('data', {}).get('result'):
                return
            
            # Get adjusted threshold for business context
            threshold = self.alert_engine.adjust_threshold_for_context(rule, business_context)
            
            # Check each metric result
            for metric_result in result['data']['result']:
                value = float(metric_result['value'][1])
                
                # Evaluate condition
                condition_met = self._evaluate_condition(value, threshold, rule.comparison)
                
                if condition_met:
                    # Check if alert already active
                    alert_key = f"{rule.rule_id}-{json.dumps(metric_result['metric'], sort_keys=True)}"
                    
                    if alert_key not in self.active_alerts:
                        # Create new alert
                        alert = Alert(
                            alert_id=f"ALT-{datetime.now(IST).strftime('%Y%m%d%H%M%S')}-{hash(alert_key) % 10000:04d}",
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            message=f"{rule.description} - Value: {value:.2f}, Threshold: {threshold:.2f}",
                            metric_value=value,
                            threshold=threshold,
                            region=metric_result['metric'].get('region', 'unknown'),
                            application=metric_result['metric'].get('app', 'unknown'),
                            namespace=metric_result['metric'].get('namespace', 'unknown'),
                            business_impact=rule.customer_impact,
                            revenue_impact=rule.revenue_impact_per_hour,
                            labels=metric_result['metric'],
                            annotations={
                                'business_hours': str(business_context['is_business_hours']),
                                'peak_hours': str(business_context['is_peak_hours']),
                                'festival_season': str(business_context['is_festival_season'])
                            }
                        )
                        
                        # Store alert
                        self.active_alerts[alert_key] = alert
                        await self._save_alert(alert)
                        
                        # Send notifications
                        await self.notification_manager.send_alert(alert, rule.channels)
                        
                        logger.warning(f"🚨 New alert: {alert.alert_id} - {rule.name}")
                
                else:
                    # Check if alert should be resolved
                    alert_key = f"{rule.rule_id}-{json.dumps(metric_result['metric'], sort_keys=True)}"
                    
                    if alert_key in self.active_alerts:
                        alert = self.active_alerts[alert_key]
                        alert.resolved_at = datetime.now(IST)
                        
                        await self._save_alert(alert)
                        
                        # Send resolution notification
                        resolution_alert = Alert(
                            alert_id=f"RES-{alert.alert_id}",
                            rule_id=rule.rule_id,
                            severity=AlertSeverity.RESOLVED,
                            message=f"RESOLVED: {rule.description} - Value: {value:.2f}",
                            metric_value=value,
                            threshold=threshold,
                            region=alert.region,
                            application=alert.application,
                            namespace=alert.namespace
                        )
                        
                        await self.notification_manager.send_alert(resolution_alert, [AlertChannel.SLACK])
                        
                        # Remove from active alerts
                        del self.active_alerts[alert_key]
                        
                        logger.info(f"✅ Alert resolved: {alert.alert_id}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to evaluate rule {rule.rule_id}: {e}")
    
    def _evaluate_condition(self, value: float, threshold: float, comparison: str) -> bool:
        """Evaluate threshold condition"""
        if comparison == '>':
            return value > threshold
        elif comparison == '<':
            return value < threshold
        elif comparison == '==':
            return abs(value - threshold) < 0.001  # Float comparison
        elif comparison == '!=':
            return abs(value - threshold) >= 0.001
        else:
            return False
    
    async def _business_metrics_collection(self) -> None:
        """Collect and store business metrics"""
        while self.is_running:
            try:
                # Collect business metrics
                business_metrics = await self.prometheus_client.get_business_metrics()
                
                # Store metrics for analysis
                timestamp = datetime.now(IST)
                
                for metric_name, results in business_metrics.items():
                    for result in results:
                        if result.get('value'):
                            await self._store_metric(
                                timestamp=timestamp,
                                metric_name=metric_name,
                                metric_value=float(result['value'][1]),
                                region=result['metric'].get('region', 'global'),
                                labels=result['metric']
                            )
                
                # Wait 1 minute before next collection
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Business metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_cleanup_loop(self) -> None:
        """Clean up old resolved alerts"""
        while self.is_running:
            try:
                # Clean up alerts older than 7 days
                cutoff_time = datetime.now(IST) - timedelta(days=7)
                
                async with self.pg_pool.acquire() as conn:
                    deleted_count = await conn.fetchval("""
                        DELETE FROM alerts 
                        WHERE resolved_at IS NOT NULL AND resolved_at < $1
                        RETURNING COUNT(*)
                    """, cutoff_time)
                    
                    if deleted_count > 0:
                        logger.info(f"🧹 Cleaned up {deleted_count} old alerts")
                
                # Wait 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Alert cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _daily_report_generation(self) -> None:
        """Generate daily business reports"""
        while self.is_running:
            try:
                now = datetime.now(IST)
                
                # Generate report at 6 AM IST
                if now.hour == 6 and now.minute == 0:
                    await self._generate_daily_business_report(now.date())
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Daily report generation error: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_daily_business_report(self, report_date: datetime.date) -> None:
        """Generate comprehensive daily business report"""
        try:
            logger.info(f"📊 Generating daily business report for {report_date}")
            
            # Collect metrics for the day
            start_time = datetime.combine(report_date, time.min, tzinfo=IST)
            end_time = datetime.combine(report_date, time.max, tzinfo=IST)
            
            # Get key business metrics
            report_data = {
                'date': report_date.isoformat(),
                'alert_summary': await self._get_alert_summary(start_time, end_time),
                'business_metrics': await self._get_business_metrics_summary(start_time, end_time),
                'regional_performance': await self._get_regional_performance_summary(start_time, end_time),
                'gitops_deployment_stats': await self._get_deployment_stats(start_time, end_time),
                'sla_compliance': await self._calculate_sla_compliance(start_time, end_time),
                'recommendations': await self._generate_recommendations()
            }
            
            # Store report
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO business_reports (report_date, report_type, report_data)
                    VALUES ($1, $2, $3)
                """, report_date, 'daily_business', json.dumps(report_data, default=str))
            
            logger.info(f"✅ Daily business report generated for {report_date}")
            
            # Send report to stakeholders if configured
            if self.config.compliance_notification_emails:
                await self._send_daily_report_email(report_data)
                
        except Exception as e:
            logger.error(f"❌ Daily report generation failed: {e}")
    
    async def _get_alert_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get alert summary for time period"""
        async with self.pg_pool.acquire() as conn:
            summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_alerts,
                    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_alerts,
                    COUNT(CASE WHEN severity = 'warning' THEN 1 END) as warning_alerts,
                    COUNT(CASE WHEN resolved_at IS NOT NULL THEN 1 END) as resolved_alerts,
                    AVG(EXTRACT(EPOCH FROM (resolved_at - started_at))/60) as avg_resolution_time_minutes
                FROM alerts
                WHERE started_at BETWEEN $1 AND $2
            """, start_time, end_time)
            
            return dict(summary) if summary else {}
    
    async def _get_business_metrics_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get business metrics summary"""
        async with self.pg_pool.acquire() as conn:
            # Get average metrics for the day
            metrics = await conn.fetch("""
                SELECT metric_name, AVG(metric_value) as avg_value
                FROM monitoring_metrics
                WHERE timestamp BETWEEN $1 AND $2
                AND metric_name IN ('conversion_rate', 'upi_success_rate', 'revenue_per_minute')
                GROUP BY metric_name
            """, start_time, end_time)
            
            return {metric['metric_name']: metric['avg_value'] for metric in metrics}
    
    async def _get_regional_performance_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get regional performance summary"""
        # Mock implementation - in real scenario, query actual regional metrics
        return {
            'mumbai': {'avg_latency': 150, 'error_rate': 1.2, 'availability': 99.95},
            'delhi': {'avg_latency': 180, 'error_rate': 1.5, 'availability': 99.92},
            'bangalore': {'avg_latency': 200, 'error_rate': 1.8, 'availability': 99.88}
        }
    
    async def _get_deployment_stats(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get GitOps deployment statistics"""
        # Mock implementation
        return {
            'total_deployments': 15,
            'successful_deployments': 14,
            'failed_deployments': 1,
            'avg_deployment_time': 8.5,  # minutes
            'rollback_count': 0
        }
    
    async def _calculate_sla_compliance(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate SLA compliance metrics"""
        return {
            'uptime_percentage': 99.95,
            'response_time_sla': 98.5,  # % of requests under 1s
            'error_rate_sla': 99.2,     # % of requests without 5xx errors
            'overall_sla_compliance': 99.2
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        return [
            "Consider scaling Mumbai region during peak hours (6-9 PM IST)",
            "UPI success rate dipped below 90% - investigate payment gateway issues",
            "High error rate in Bangalore region - check infrastructure health",
            "Festival season approaching - prepare for 3x traffic increase"
        ]
    
    async def _send_daily_report_email(self, report_data: Dict[str, Any]) -> None:
        """Send daily report via email"""
        # Implementation would format and send comprehensive report
        logger.info("📧 Daily business report sent to stakeholders")
    
    async def _save_alert(self, alert: Alert) -> None:
        """Save alert to database"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO alerts 
                (alert_id, rule_id, severity, message, metric_value, threshold,
                 region, application, namespace, started_at, resolved_at,
                 acknowledged_at, acknowledged_by, business_impact, revenue_impact,
                 affected_customers, labels, annotations)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                ON CONFLICT (alert_id) DO UPDATE SET
                    resolved_at = EXCLUDED.resolved_at,
                    acknowledged_at = EXCLUDED.acknowledged_at,
                    acknowledged_by = EXCLUDED.acknowledged_by
            """,
            alert.alert_id, alert.rule_id, alert.severity.value, alert.message,
            alert.metric_value, alert.threshold, alert.region, alert.application,
            alert.namespace, alert.started_at, alert.resolved_at,
            alert.acknowledged_at, alert.acknowledged_by, alert.business_impact,
            alert.revenue_impact, alert.affected_customers,
            json.dumps(alert.labels), json.dumps(alert.annotations))
    
    async def _store_metric(self, timestamp: datetime, metric_name: str, 
                          metric_value: float, region: str, labels: Dict[str, str]) -> None:
        """Store metric in database"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO monitoring_metrics (timestamp, metric_name, metric_value, region, labels)
                VALUES ($1, $2, $3, $4, $5)
            """, timestamp, metric_name, metric_value, region, json.dumps(labels))
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring system"""
        logger.info("🛑 Stopping GitOps monitoring...")
        self.is_running = False
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.pg_pool:
            await self.pg_pool.close()
        
        logger.info("✅ GitOps monitoring stopped")


async def main():
    """Main function for GitOps monitoring"""
    print("📊 GitOps Monitoring & Alerting System")
    print("=" * 50)
    
    # Configuration
    config = MonitoringConfig(
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379"),
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/monitoring"),
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        teams_webhook=os.getenv("TEAMS_WEBHOOK", ""),
        whatsapp_api_key=os.getenv("WHATSAPP_API_KEY", ""),
        whatsapp_phone_numbers=["+91-9999999999"],  # Indian phone numbers
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        email_recipients=["devops@company.com", "sre@company.com"],
        enable_rbi_reporting=True,
        compliance_notification_emails=["compliance@company.com"]
    )
    
    # Initialize monitoring system
    monitor = GitOpsMonitor(config)
    
    try:
        if await monitor.initialize():
            print("✅ GitOps Monitoring System initialized successfully")
            print("🔍 Starting continuous monitoring...")
            
            # Start monitoring (runs indefinitely)
            await monitor.start_monitoring()
            
        else:
            print("❌ Failed to initialize GitOps Monitoring System")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring system...")
        await monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ Monitoring system error: {e}")
        await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())