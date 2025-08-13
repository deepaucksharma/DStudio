#!/usr/bin/env python3
"""
DataOps Example 05: Data Pipeline Monitoring and Alerting System
Real-time monitoring and alerting for Indian data operations
Focus: IRCTC booking monitoring, UPI transaction alerting, Flipkart inventory tracking

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import json
import time
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import seaborn as sns
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary
import psutil
import redis
from kafka import KafkaProducer, KafkaConsumer
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dataops/monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class MetricType(Enum):
    """Types of metrics for Indian data operations"""
    DATA_FRESHNESS = "data_freshness"
    PIPELINE_LATENCY = "pipeline_latency"
    ERROR_RATE = "error_rate"
    DATA_QUALITY_SCORE = "data_quality_score"
    COST_TRACKING = "cost_tracking"
    THROUGHPUT = "throughput"
    SYSTEM_HEALTH = "system_health"
    BUSINESS_KPI = "business_kpi"

@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    company: str
    business_impact: str
    runbook_url: str
    notification_channels: List[str]
    created_at: datetime
    resolved_at: Optional[datetime] = None

@dataclass
class MetricValue:
    """Metric value with metadata"""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    company: str
    business_context: str

# Prometheus metrics for Indian companies
METRICS = {
    # IRCTC metrics
    'irctc_booking_latency': Histogram('irctc_booking_latency_seconds', 'IRCTC booking response time', ['route', 'class']),
    'irctc_booking_success_rate': Gauge('irctc_booking_success_rate', 'IRCTC booking success rate percentage'),
    'irctc_concurrent_users': Gauge('irctc_concurrent_users', 'Number of concurrent users on IRCTC'),
    
    # UPI transaction metrics
    'upi_transaction_count': Counter('upi_transactions_total', 'Total UPI transactions', ['bank', 'status']),
    'upi_transaction_amount': Gauge('upi_transaction_amount_inr', 'UPI transaction amount in INR'),
    'upi_error_rate': Gauge('upi_error_rate_percent', 'UPI transaction error rate'),
    
    # Flipkart inventory metrics
    'flipkart_inventory_count': Gauge('flipkart_inventory_items', 'Flipkart inventory count', ['category', 'warehouse']),
    'flipkart_order_processing_time': Histogram('flipkart_order_processing_seconds', 'Order processing time'),
    'flipkart_delivery_sla': Gauge('flipkart_delivery_sla_compliance', 'Delivery SLA compliance percentage'),
    
    # General data pipeline metrics
    'data_pipeline_lag': Gauge('data_pipeline_lag_minutes', 'Data pipeline lag in minutes', ['pipeline', 'stage']),
    'data_quality_score': Gauge('data_quality_score', 'Data quality score percentage', ['dataset']),
    'processing_cost_inr': Gauge('processing_cost_inr', 'Processing cost in INR', ['pipeline'])
}

class DataOpsMonitoring:
    """
    Comprehensive monitoring system for Indian data operations
    """
    
    def __init__(self, company_name: str, config: Dict[str, Any]):
        self.company_name = company_name
        self.config = config
        self.alerts = {}
        self.active_alerts = {}
        
        # Initialize notification clients
        self.setup_notification_clients()
        
        # Initialize metrics storage
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            decode_responses=True
        )
        
        # Start Prometheus metrics server
        start_http_server(config.get('prometheus_port', 8000))
        
        logger.info(f"DataOps monitoring initialized for {company_name}")
    
    def setup_notification_clients(self):
        """Setup notification clients for Indian teams"""
        try:
            # Slack client
            slack_token = self.config.get('slack_token')
            if slack_token:
                self.slack_client = WebClient(token=slack_token)
            else:
                self.slack_client = None
                logger.warning("Slack token not provided")
            
            # Email configuration for Indian companies
            self.email_config = {
                'smtp_server': self.config.get('smtp_server', 'smtp.gmail.com'),
                'smtp_port': self.config.get('smtp_port', 587),
                'email': self.config.get('notification_email'),
                'password': self.config.get('email_password')
            }
            
            # Teams webhook
            self.teams_webhook = self.config.get('teams_webhook_url')
            
        except Exception as e:
            logger.error(f"Notification setup failed: {e}")
    
    def register_alert(self, alert: Alert):
        """Register a new alert rule"""
        try:
            self.alerts[alert.alert_id] = alert
            logger.info(f"Alert registered: {alert.name} for {alert.company}")
        except Exception as e:
            logger.error(f"Alert registration failed: {e}")
    
    def record_metric(self, metric: MetricValue):
        """Record a metric value"""
        try:
            # Store in Redis for real-time access
            metric_key = f"metric:{metric.company}:{metric.metric_name}"
            metric_data = {
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'labels': json.dumps(metric.labels),
                'business_context': metric.business_context
            }
            
            self.redis_client.hset(metric_key, mapping=metric_data)
            self.redis_client.expire(metric_key, 86400)  # 24 hours
            
            # Update Prometheus metrics
            self.update_prometheus_metrics(metric)
            
            # Check alert conditions
            self.check_alert_conditions(metric)
            
        except Exception as e:
            logger.error(f"Metric recording failed: {e}")
    
    def update_prometheus_metrics(self, metric: MetricValue):
        """Update Prometheus metrics"""
        try:
            metric_name = metric.metric_name
            
            if metric_name in METRICS:
                prometheus_metric = METRICS[metric_name]
                
                # Update based on metric type
                if isinstance(prometheus_metric, Gauge):
                    if metric.labels:
                        prometheus_metric.labels(**metric.labels).set(metric.value)
                    else:
                        prometheus_metric.set(metric.value)
                        
                elif isinstance(prometheus_metric, Counter):
                    if metric.labels:
                        prometheus_metric.labels(**metric.labels).inc(metric.value)
                    else:
                        prometheus_metric.inc(metric.value)
                        
                elif isinstance(prometheus_metric, Histogram):
                    if metric.labels:
                        prometheus_metric.labels(**metric.labels).observe(metric.value)
                    else:
                        prometheus_metric.observe(metric.value)
            
        except Exception as e:
            logger.error(f"Prometheus metric update failed: {e}")
    
    def check_alert_conditions(self, metric: MetricValue):
        """Check if metric triggers any alerts"""
        try:
            for alert_id, alert in self.alerts.items():
                if alert.metric_name == metric.metric_name and alert.company == metric.company:
                    
                    triggered = False
                    
                    if alert.comparison == 'gt' and metric.value > alert.threshold:
                        triggered = True
                    elif alert.comparison == 'lt' and metric.value < alert.threshold:
                        triggered = True
                    elif alert.comparison == 'eq' and metric.value == alert.threshold:
                        triggered = True
                    
                    if triggered and alert_id not in self.active_alerts:
                        # New alert triggered
                        self.active_alerts[alert_id] = {
                            'alert': alert,
                            'triggered_at': datetime.now(),
                            'metric_value': metric.value
                        }
                        self.send_alert_notification(alert, metric)
                        
                    elif not triggered and alert_id in self.active_alerts:
                        # Alert resolved
                        alert.resolved_at = datetime.now()
                        self.send_resolution_notification(alert, metric)
                        del self.active_alerts[alert_id]
        
        except Exception as e:
            logger.error(f"Alert condition check failed: {e}")
    
    def send_alert_notification(self, alert: Alert, metric: MetricValue):
        """Send alert notifications"""
        try:
            alert_message = self.format_alert_message(alert, metric)
            
            for channel in alert.notification_channels:
                if channel == 'slack' and self.slack_client:
                    self.send_slack_alert(alert, alert_message)
                elif channel == 'email':
                    self.send_email_alert(alert, alert_message)
                elif channel == 'teams':
                    self.send_teams_alert(alert, alert_message)
                elif channel == 'sms':
                    self.send_sms_alert(alert, alert_message)
            
            logger.warning(f"Alert triggered: {alert.name} - {alert_message}")
            
        except Exception as e:
            logger.error(f"Alert notification failed: {e}")
    
    def format_alert_message(self, alert: Alert, metric: MetricValue) -> str:
        """Format alert message for Indian context"""
        
        # Add Indian context and business impact
        business_context = ""
        if alert.company.lower() == 'irctc':
            business_context = "🚂 This may affect train booking experience for millions of passengers"
        elif alert.company.lower() == 'paytm':
            business_context = "💳 This may impact UPI transactions across India"
        elif alert.company.lower() == 'flipkart':
            business_context = "📦 This may affect order fulfillment and delivery times"
        
        message = f"""
🚨 **{alert.severity.value.upper()} ALERT** 🚨

**Company**: {alert.company}
**Alert**: {alert.name}
**Description**: {alert.description}

**Metric**: {alert.metric_name}
**Current Value**: {metric.value:.2f}
**Threshold**: {alert.threshold:.2f}
**Comparison**: {alert.comparison}

**Business Impact**: {alert.business_impact}
{business_context}

**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
**Runbook**: {alert.runbook_url}

**Action Required**: Please check the system and follow the runbook for resolution.
        """.strip()
        
        return message
    
    def send_slack_alert(self, alert: Alert, message: str):
        """Send alert to Slack"""
        try:
            channel = self.config.get('slack_channel', '#alerts')
            
            # Color based on severity
            color_map = {
                AlertSeverity.CRITICAL: 'danger',
                AlertSeverity.HIGH: 'warning',
                AlertSeverity.MEDIUM: 'good',
                AlertSeverity.LOW: '#808080'
            }
            
            self.slack_client.chat_postMessage(
                channel=channel,
                text=f"Alert: {alert.name}",
                attachments=[{
                    'color': color_map.get(alert.severity, 'warning'),
                    'text': message,
                    'footer': f"{self.company_name} DataOps Monitoring",
                    'ts': int(datetime.now().timestamp())
                }]
            )
            
        except SlackApiError as e:
            logger.error(f"Slack notification failed: {e}")
    
    def send_email_alert(self, alert: Alert, message: str):
        """Send alert via email"""
        try:
            if not self.email_config.get('email'):
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.config.get('alert_email', 'ops@company.com')
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name} - {self.company_name}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['email'], msg['To'], text)
            server.quit()
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
    
    def send_teams_alert(self, alert: Alert, message: str):
        """Send alert to Microsoft Teams"""
        try:
            if not self.teams_webhook:
                return
            
            # Color based on severity
            color_map = {
                AlertSeverity.CRITICAL: 'FF0000',
                AlertSeverity.HIGH: 'FFA500',
                AlertSeverity.MEDIUM: 'FFFF00',
                AlertSeverity.LOW: '808080'
            }
            
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color_map.get(alert.severity, 'FFA500'),
                "summary": f"{alert.name} Alert",
                "sections": [{
                    "activityTitle": f"🚨 {alert.severity.value.upper()} Alert",
                    "activitySubtitle": alert.name,
                    "text": message,
                    "markdown": True
                }],
                "potentialAction": [{
                    "@type": "OpenUri",
                    "name": "View Runbook",
                    "targets": [{
                        "os": "default",
                        "uri": alert.runbook_url
                    }]
                }]
            }
            
            response = requests.post(self.teams_webhook, json=teams_message)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Teams notification failed: {e}")
    
    def send_sms_alert(self, alert: Alert, message: str):
        """Send SMS alert for critical issues"""
        try:
            if alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                return
            
            # Use Indian SMS gateway services like TextLocal, MSG91, etc.
            sms_api_key = self.config.get('sms_api_key')
            sms_numbers = self.config.get('sms_alert_numbers', [])
            
            if not sms_api_key or not sms_numbers:
                return
            
            # Shorten message for SMS
            short_message = f"ALERT: {alert.name} at {self.company_name}. Value: {alert.metric_name}. Check runbook: {alert.runbook_url}"
            
            # Example using TextLocal API (popular in India)
            for number in sms_numbers:
                sms_data = {
                    'apikey': sms_api_key,
                    'numbers': number,
                    'message': short_message,
                    'sender': 'DATAOPS'
                }
                
                response = requests.post('https://api.textlocal.in/send/', data=sms_data)
                
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")
    
    def send_resolution_notification(self, alert: Alert, metric: MetricValue):
        """Send alert resolution notification"""
        try:
            resolution_message = f"""
✅ **ALERT RESOLVED** ✅

**Company**: {alert.company}
**Alert**: {alert.name}
**Metric**: {alert.metric_name}
**Current Value**: {metric.value:.2f}
**Threshold**: {alert.threshold:.2f}

**Resolved At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

The issue has been resolved automatically.
            """.strip()
            
            # Send to same channels but with lower priority
            for channel in alert.notification_channels:
                if channel == 'slack' and self.slack_client:
                    self.slack_client.chat_postMessage(
                        channel=self.config.get('slack_channel', '#alerts'),
                        text=resolution_message
                    )
            
            logger.info(f"Alert resolved: {alert.name}")
            
        except Exception as e:
            logger.error(f"Resolution notification failed: {e}")
    
    def get_system_metrics(self) -> Dict[str, MetricValue]:
        """Collect system-level metrics"""
        try:
            current_time = datetime.now()
            metrics = {}
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics['cpu_usage'] = MetricValue(
                metric_name='system_cpu_usage_percent',
                value=cpu_percent,
                timestamp=current_time,
                labels={'host': os.uname().nodename},
                company=self.company_name,
                business_context='System performance monitoring'
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = MetricValue(
                metric_name='system_memory_usage_percent',
                value=memory.percent,
                timestamp=current_time,
                labels={'host': os.uname().nodename},
                company=self.company_name,
                business_context='System performance monitoring'
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = MetricValue(
                metric_name='system_disk_usage_percent',
                value=(disk.used / disk.total) * 100,
                timestamp=current_time,
                labels={'host': os.uname().nodename, 'mount': '/'},
                company=self.company_name,
                business_context='System performance monitoring'
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {}
    
    async def monitor_continuously(self, interval_seconds: int = 30):
        """Continuously monitor metrics"""
        logger.info(f"Starting continuous monitoring with {interval_seconds}s interval")
        
        while True:
            try:
                # Collect system metrics
                system_metrics = self.get_system_metrics()
                
                for metric in system_metrics.values():
                    self.record_metric(metric)
                
                # Collect business metrics (would be implemented based on company)
                business_metrics = self.collect_business_metrics()
                
                for metric in business_metrics:
                    self.record_metric(metric)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def collect_business_metrics(self) -> List[MetricValue]:
        """Collect business-specific metrics"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # Simulate business metrics for different Indian companies
            if self.company_name.lower() == 'irctc':
                # IRCTC specific metrics
                metrics.extend([
                    MetricValue(
                        metric_name='irctc_booking_success_rate',
                        value=np.random.uniform(85, 98),  # 85-98% success rate
                        timestamp=current_time,
                        labels={'service': 'booking'},
                        company='irctc',
                        business_context='Booking system health'
                    ),
                    MetricValue(
                        metric_name='irctc_concurrent_users',
                        value=np.random.randint(50000, 200000),  # 50K-200K users
                        timestamp=current_time,
                        labels={'platform': 'web'},
                        company='irctc',
                        business_context='User load monitoring'
                    )
                ])
                
            elif self.company_name.lower() == 'paytm':
                # Paytm specific metrics
                metrics.extend([
                    MetricValue(
                        metric_name='upi_transaction_amount',
                        value=np.random.uniform(1000, 50000),  # ₹1K-50K
                        timestamp=current_time,
                        labels={'payment_method': 'upi'},
                        company='paytm',
                        business_context='Transaction volume monitoring'
                    ),
                    MetricValue(
                        metric_name='upi_error_rate',
                        value=np.random.uniform(0.5, 5.0),  # 0.5-5% error rate
                        timestamp=current_time,
                        labels={'bank': 'sbi'},
                        company='paytm',
                        business_context='Payment reliability'
                    )
                ])
                
            elif self.company_name.lower() == 'flipkart':
                # Flipkart specific metrics
                metrics.extend([
                    MetricValue(
                        metric_name='flipkart_delivery_sla',
                        value=np.random.uniform(88, 96),  # 88-96% SLA compliance
                        timestamp=current_time,
                        labels={'region': 'mumbai'},
                        company='flipkart',
                        business_context='Delivery performance'
                    ),
                    MetricValue(
                        metric_name='flipkart_inventory_count',
                        value=np.random.randint(100000, 500000),  # 100K-500K items
                        timestamp=current_time,
                        labels={'category': 'electronics', 'warehouse': 'mumbai'},
                        company='flipkart',
                        business_context='Inventory management'
                    )
                ])
            
        except Exception as e:
            logger.error(f"Business metrics collection failed: {e}")
        
        return metrics

def setup_indian_company_alerts(monitoring_system: DataOpsMonitoring, company: str):
    """Setup alerts specific to Indian companies"""
    
    current_time = datetime.now()
    
    if company.lower() == 'irctc':
        # IRCTC alerts
        alerts = [
            Alert(
                alert_id="irctc_booking_success_low",
                name="IRCTC Booking Success Rate Low",
                description="IRCTC booking success rate dropped below threshold",
                severity=AlertSeverity.HIGH,
                metric_name="irctc_booking_success_rate",
                threshold=90.0,
                comparison="lt",
                company="irctc",
                business_impact="Passengers unable to book train tickets",
                runbook_url="https://runbook.irctc.com/booking-issues",
                notification_channels=["slack", "email", "teams"],
                created_at=current_time
            ),
            Alert(
                alert_id="irctc_high_load",
                name="IRCTC High User Load",
                description="Concurrent users exceeded safe threshold",
                severity=AlertSeverity.MEDIUM,
                metric_name="irctc_concurrent_users",
                threshold=180000,
                comparison="gt",
                company="irctc",
                business_impact="System may slow down during peak booking hours",
                runbook_url="https://runbook.irctc.com/scaling",
                notification_channels=["slack", "teams"],
                created_at=current_time
            )
        ]
        
    elif company.lower() == 'paytm':
        # Paytm alerts
        alerts = [
            Alert(
                alert_id="upi_error_rate_high",
                name="UPI Error Rate High",
                description="UPI transaction error rate exceeded threshold",
                severity=AlertSeverity.CRITICAL,
                metric_name="upi_error_rate",
                threshold=3.0,
                comparison="gt",
                company="paytm",
                business_impact="Users unable to complete payments",
                runbook_url="https://runbook.paytm.com/upi-errors",
                notification_channels=["slack", "email", "teams", "sms"],
                created_at=current_time
            )
        ]
        
    elif company.lower() == 'flipkart':
        # Flipkart alerts
        alerts = [
            Alert(
                alert_id="delivery_sla_breach",
                name="Delivery SLA Breach",
                description="Delivery SLA compliance dropped below threshold",
                severity=AlertSeverity.HIGH,
                metric_name="flipkart_delivery_sla",
                threshold=90.0,
                comparison="lt",
                company="flipkart",
                business_impact="Customer satisfaction may be affected",
                runbook_url="https://runbook.flipkart.com/delivery-sla",
                notification_channels=["slack", "email"],
                created_at=current_time
            ),
            Alert(
                alert_id="low_inventory_warning",
                name="Low Inventory Warning",
                description="Inventory count dropped below reorder threshold",
                severity=AlertSeverity.MEDIUM,
                metric_name="flipkart_inventory_count",
                threshold=150000,
                comparison="lt",
                company="flipkart",
                business_impact="Stock-outs may occur for popular items",
                runbook_url="https://runbook.flipkart.com/inventory",
                notification_channels=["slack"],
                created_at=current_time
            )
        ]
    else:
        alerts = []
    
    # Register all alerts
    for alert in alerts:
        monitoring_system.register_alert(alert)

def main():
    """Demonstrate monitoring and alerting for Indian companies"""
    
    print("📊 Starting DataOps Monitoring and Alerting Demo")
    print("=" * 60)
    
    # Configuration for monitoring system
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'prometheus_port': 8000,
        'slack_token': 'xoxb-your-slack-token',  # Replace with actual token
        'slack_channel': '#dataops-alerts',
        'notification_email': 'alerts@company.com',
        'email_password': 'your-email-password',
        'teams_webhook_url': 'https://outlook.office.com/webhook/your-webhook',
        'sms_api_key': 'your-sms-api-key',
        'sms_alert_numbers': ['+919876543210'],
        'alert_email': 'ops-team@company.com'
    }
    
    # Demo for different Indian companies
    companies = ['irctc', 'paytm', 'flipkart']
    
    for company in companies:
        print(f"\n🏢 Setting up monitoring for {company.upper()}")
        
        # Initialize monitoring system
        monitoring = DataOpsMonitoring(company, config)
        
        # Setup company-specific alerts
        setup_indian_company_alerts(monitoring, company)
        
        print(f"   ✅ Monitoring system initialized")
        print(f"   ✅ Alert rules configured")
        print(f"   ✅ Notification channels setup")
        
        # Simulate some metrics
        print(f"   📈 Simulating metrics for {company}...")
        
        # Generate sample business metrics
        business_metrics = monitoring.collect_business_metrics()
        
        for metric in business_metrics:
            monitoring.record_metric(metric)
            print(f"      📊 {metric.metric_name}: {metric.value:.2f}")
        
        # Simulate an alert condition
        if company == 'paytm':
            print("   🚨 Simulating UPI error rate alert...")
            high_error_metric = MetricValue(
                metric_name='upi_error_rate',
                value=5.5,  # Above threshold of 3.0
                timestamp=datetime.now(),
                labels={'bank': 'sbi'},
                company='paytm',
                business_context='Payment reliability'
            )
            monitoring.record_metric(high_error_metric)
            print("      ⚠️  Alert triggered: UPI Error Rate High")
        
        elif company == 'irctc':
            print("   🚨 Simulating booking success rate alert...")
            low_success_metric = MetricValue(
                metric_name='irctc_booking_success_rate',
                value=85.0,  # Below threshold of 90.0
                timestamp=datetime.now(),
                labels={'service': 'booking'},
                company='irctc',
                business_context='Booking system health'
            )
            monitoring.record_metric(low_success_metric)
            print("      ⚠️  Alert triggered: IRCTC Booking Success Rate Low")
        
        print(f"   📊 Prometheus metrics available at: http://localhost:8000")
    
    print("\n💡 Monitoring Features Demonstrated:")
    print("   ✓ Real-time metric collection")
    print("   ✓ Company-specific alert rules")
    print("   ✓ Multi-channel notifications (Slack, Email, Teams, SMS)")
    print("   ✓ Indian business context awareness")
    print("   ✓ Prometheus metrics integration")
    print("   ✓ Redis-based metric storage")
    print("   ✓ Automated alert resolution")
    print("   ✓ Business impact assessment")
    
    print("\n📊 Sample Alert Rules:")
    print("   • IRCTC: Booking success rate < 90%")
    print("   • Paytm: UPI error rate > 3%")
    print("   • Flipkart: Delivery SLA < 90%")
    
    print("\n✅ DataOps Monitoring and Alerting Demo Completed!")

if __name__ == "__main__":
    main()