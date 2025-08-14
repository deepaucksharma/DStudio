#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 7: AlertManager for Indian Holiday Season

भारतीय context: Diwali, Holi, Eid जैसे festivals के दौरान smart alerting
जैसे traffic spike expected है but false alerts नहीं भेजना

Real-world scenario: Zomato NYE 2024 की तरह expected load के लिए alert tuning
Challenge: Regional festivals, 10x traffic spikes, cultural sensitivity
"""

import yaml
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import calendar
import pytz
from croniter import croniter
import structlog
import asyncio
from contextlib import asynccontextmanager

# भारतीय festival calendar और alerting rules
class IndianFestival(Enum):
    """भारतीय त्योहारों की comprehensive list"""
    DIWALI = "diwali"
    HOLI = "holi"
    EID_UL_FITR = "eid_ul_fitr"
    EID_UL_ADHA = "eid_ul_adha"
    DURGA_PUJA = "durga_puja"
    NAVRATRI = "navratri"
    KARVA_CHAUTH = "karva_chauth"
    DHANTERAS = "dhanteras"
    RAKSHA_BANDHAN = "raksha_bandhan"
    JANMASHTAMI = "janmashtami"
    GANESH_CHATURTHI = "ganesh_chaturthi"
    DUSSEHRA = "dussehra"
    CHRISTMAS = "christmas"
    NEW_YEAR = "new_year"
    REPUBLIC_DAY = "republic_day"
    INDEPENDENCE_DAY = "independence_day"
    GANDHI_JAYANTI = "gandhi_jayanti"
    
class AlertSeverity(Enum):
    """Alert severity levels for Indian operations"""
    CRITICAL = "critical"      # Business stopping - immediate action
    HIGH = "high"             # Revenue impact - 15 min response
    MEDIUM = "medium"         # Performance degradation - 1 hour
    LOW = "low"              # Informational - next business day
    INFO = "info"            # Metrics tracking - no action needed

@dataclass
class IndianHolidayConfig:
    """भारतीय holiday configuration for alerting"""
    name: str
    date: str  # YYYY-MM-DD format
    duration_days: int
    expected_traffic_multiplier: float
    peak_hours: List[str]  # 24-hour format
    affected_regions: List[str]
    business_impact: str  # high, medium, low
    alert_suppression: bool
    special_monitoring: bool

class IndianHolidayAlertManager:
    """
    Indian Holiday-aware AlertManager
    
    Features:
    - Festival-based alert suppression
    - Regional holiday awareness
    - Business context alerting
    - Cultural sensitivity in messaging
    - Multi-language alert support
    """
    
    def __init__(self, region: str = "pan_india"):
        self.region = region
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.current_time = datetime.now(self.timezone)
        
        # Initialize holiday calendar
        self.holiday_calendar = self._initialize_indian_holiday_calendar()
        
        # Alert configuration
        self.alert_config = self._load_alert_configuration()
        
        # Logger setup
        self.logger = structlog.get_logger("indian-holiday-alertmanager")
        
        # Regional preferences
        self.regional_config = self._setup_regional_preferences()
        
    def _initialize_indian_holiday_calendar(self) -> Dict[str, IndianHolidayConfig]:
        """
        Initialize comprehensive Indian holiday calendar
        
        Includes:
        - National holidays
        - Regional festivals
        - Business seasons (BBD, sale events)
        - Cultural events
        """
        
        current_year = self.current_time.year
        
        holiday_calendar = {
            "diwali_2024": IndianHolidayConfig(
                name="Diwali 2024",
                date="2024-11-01",
                duration_days=5,  # Dhanteras to Bhai Dooj
                expected_traffic_multiplier=8.0,
                peak_hours=["18:00", "19:00", "20:00", "21:00"],
                affected_regions=["north_india", "west_india", "central_india"],
                business_impact="high",
                alert_suppression=True,
                special_monitoring=True
            ),
            
            "holi_2024": IndianHolidayConfig(
                name="Holi 2024",
                date="2024-03-25",
                duration_days=2,
                expected_traffic_multiplier=3.0,
                peak_hours=["10:00", "11:00", "16:00", "17:00"],
                affected_regions=["north_india", "central_india"],
                business_impact="medium",
                alert_suppression=True,
                special_monitoring=False
            ),
            
            "eid_ul_fitr_2024": IndianHolidayConfig(
                name="Eid ul-Fitr 2024",
                date="2024-04-11",
                duration_days=3,
                expected_traffic_multiplier=4.0,
                peak_hours=["12:00", "13:00", "19:00", "20:00"],
                affected_regions=["all_india"],
                business_impact="high",
                alert_suppression=True,
                special_monitoring=True
            ),
            
            "big_billion_days_2024": IndianHolidayConfig(
                name="Big Billion Days 2024",
                date="2024-09-29",
                duration_days=10,
                expected_traffic_multiplier=12.0,  # Highest multiplier
                peak_hours=["00:00", "12:00", "20:00", "23:59"],
                affected_regions=["all_india"],
                business_impact="critical",
                alert_suppression=False,  # Don't suppress, but adjust thresholds
                special_monitoring=True
            ),
            
            "durga_puja_2024": IndianHolidayConfig(
                name="Durga Puja 2024",
                date="2024-10-09",
                duration_days=10,
                expected_traffic_multiplier=5.0,
                peak_hours=["17:00", "18:00", "19:00", "20:00"],
                affected_regions=["east_india"],
                business_impact="high",
                alert_suppression=True,
                special_monitoring=True
            ),
            
            "new_year_eve_2024": IndianHolidayConfig(
                name="New Year Eve 2024",
                date="2024-12-31",
                duration_days=1,
                expected_traffic_multiplier=15.0,  # Zomato-style spike
                peak_hours=["23:00", "23:30", "00:00", "00:30"],
                affected_regions=["all_india"],
                business_impact="critical",
                alert_suppression=False,
                special_monitoring=True
            )
        }
        
        return holiday_calendar
        
    def _load_alert_configuration(self) -> Dict[str, Any]:
        """Load alerting configuration for Indian scenarios"""
        
        return {
            "default_thresholds": {
                "cpu_usage_percent": 80,
                "memory_usage_percent": 85,
                "disk_usage_percent": 90,
                "api_response_time_ms": 200,
                "error_rate_percent": 5,
                "queue_depth": 1000
            },
            
            "festival_thresholds": {
                "cpu_usage_percent": 95,  # Higher tolerance during festivals
                "memory_usage_percent": 95,
                "disk_usage_percent": 95,
                "api_response_time_ms": 500,  # Accept higher latency
                "error_rate_percent": 10,  # Higher error tolerance
                "queue_depth": 5000  # Much higher queue depth
            },
            
            "critical_business_thresholds": {
                # BBD, NYE जैसे critical events के लिए
                "payment_success_rate": 95,  # Never compromise on payments
                "order_success_rate": 90,
                "user_login_success_rate": 95,
                "checkout_conversion_rate": 80
            },
            
            "regional_multipliers": {
                "mumbai": 1.2,     # Higher baseline
                "delhi": 1.1,
                "bangalore": 1.0,
                "chennai": 0.9,
                "kolkata": 0.8,
                "tier2_cities": 0.7,
                "tier3_cities": 0.5
            }
        }
        
    def _setup_regional_preferences(self) -> Dict[str, Dict]:
        """Setup regional preferences for alerts"""
        
        return {
            "north_india": {
                "languages": ["hindi", "english", "punjabi"],
                "business_hours": {"start": "09:00", "end": "21:00"},
                "peak_festivals": ["diwali", "holi", "karva_chauth"],
                "notification_preferences": ["sms", "whatsapp", "email"]
            },
            
            "south_india": {
                "languages": ["english", "tamil", "telugu", "kannada"],
                "business_hours": {"start": "08:30", "end": "20:30"},
                "peak_festivals": ["pongal", "onam", "ugadi"],
                "notification_preferences": ["email", "sms", "push"]
            },
            
            "west_india": {
                "languages": ["english", "hindi", "marathi", "gujarati"],
                "business_hours": {"start": "09:30", "end": "21:30"},
                "peak_festivals": ["diwali", "ganesh_chaturthi", "navratri"],
                "notification_preferences": ["whatsapp", "sms", "email"]
            },
            
            "east_india": {
                "languages": ["english", "bengali", "hindi"],
                "business_hours": {"start": "09:00", "end": "20:00"},
                "peak_festivals": ["durga_puja", "kali_puja", "poila_boishakh"],
                "notification_preferences": ["sms", "email", "whatsapp"]
            }
        }
        
    def check_holiday_status(self, date: datetime = None) -> Dict[str, Any]:
        """
        Check if current/given date falls under any Indian holiday
        
        Returns:
            Holiday information with alerting recommendations
        """
        
        if date is None:
            date = self.current_time
            
        date_str = date.strftime("%Y-%m-%d")
        
        # Check for exact match
        for holiday_key, holiday_config in self.holiday_calendar.items():
            holiday_date = datetime.strptime(holiday_config.date, "%Y-%m-%d")
            holiday_end = holiday_date + timedelta(days=holiday_config.duration_days - 1)
            
            if holiday_date <= date <= holiday_end:
                return {
                    "is_holiday": True,
                    "holiday_name": holiday_config.name,
                    "festival_type": holiday_key.split("_")[0],
                    "day_of_festival": (date - holiday_date).days + 1,
                    "total_days": holiday_config.duration_days,
                    "expected_traffic_multiplier": holiday_config.expected_traffic_multiplier,
                    "alert_suppression_recommended": holiday_config.alert_suppression,
                    "special_monitoring_required": holiday_config.special_monitoring,
                    "peak_hours": holiday_config.peak_hours,
                    "affected_regions": holiday_config.affected_regions,
                    "business_impact": holiday_config.business_impact
                }
        
        # Check for upcoming holidays (within 7 days)
        upcoming_holidays = []
        for holiday_key, holiday_config in self.holiday_calendar.items():
            holiday_date = datetime.strptime(holiday_config.date, "%Y-%m-%d")
            days_until = (holiday_date - date).days
            
            if 0 < days_until <= 7:
                upcoming_holidays.append({
                    "name": holiday_config.name,
                    "days_until": days_until,
                    "expected_multiplier": holiday_config.expected_traffic_multiplier
                })
        
        return {
            "is_holiday": False,
            "upcoming_holidays": upcoming_holidays,
            "alert_suppression_recommended": False,
            "special_monitoring_required": False
        }
        
    def generate_holiday_alert_rules(self, service_name: str) -> Dict[str, Any]:
        """
        Generate Prometheus AlertManager rules for Indian holidays
        
        Args:
            service_name: Name of the service (flipkart-checkout, paytm-payments, etc.)
        """
        
        holiday_status = self.check_holiday_status()
        
        # Base alert rules
        alert_rules = {
            "groups": [
                {
                    "name": f"{service_name}_indian_holiday_alerts",
                    "rules": []
                }
            ]
        }
        
        # Adjust thresholds based on holiday status
        if holiday_status["is_holiday"]:
            thresholds = self.alert_config["festival_thresholds"]
            traffic_multiplier = holiday_status["expected_traffic_multiplier"]
        else:
            thresholds = self.alert_config["default_thresholds"]
            traffic_multiplier = 1.0
        
        # Generate CPU alert rule
        cpu_rule = {
            "alert": f"{service_name}_HighCPU_Holiday",
            "expr": f'avg(cpu_usage_percent{{service="{service_name}"}}) > {thresholds["cpu_usage_percent"]}',
            "for": "2m" if holiday_status["is_holiday"] else "1m",
            "labels": {
                "severity": "medium" if holiday_status["is_holiday"] else "high",
                "service": service_name,
                "holiday_aware": "true",
                "region": self.region
            },
            "annotations": {
                "summary": f"High CPU usage on {service_name}",
                "description": self._generate_holiday_aware_description(
                    "CPU", thresholds["cpu_usage_percent"], holiday_status
                ),
                "hindi_summary": f"{service_name} में CPU usage ज्यादा है",
                "runbook_url": f"https://runbooks.company.com/{service_name}/cpu-high"
            }
        }
        
        # Generate Memory alert rule  
        memory_rule = {
            "alert": f"{service_name}_HighMemory_Holiday",
            "expr": f'avg(memory_usage_percent{{service="{service_name}"}}) > {thresholds["memory_usage_percent"]}',
            "for": "2m" if holiday_status["is_holiday"] else "1m",
            "labels": {
                "severity": "medium" if holiday_status["is_holiday"] else "high",
                "service": service_name,
                "holiday_aware": "true"
            },
            "annotations": {
                "summary": f"High Memory usage on {service_name}",
                "description": self._generate_holiday_aware_description(
                    "Memory", thresholds["memory_usage_percent"], holiday_status
                ),
                "hindi_summary": f"{service_name} में Memory usage ज्यादा है"
            }
        }
        
        # Generate API latency rule
        latency_rule = {
            "alert": f"{service_name}_HighLatency_Holiday",
            "expr": f'histogram_quantile(0.95, api_duration_seconds{{service="{service_name}"}}) * 1000 > {thresholds["api_response_time_ms"]}',
            "for": "5m" if holiday_status["is_holiday"] else "3m",
            "labels": {
                "severity": "high",
                "service": service_name,
                "holiday_aware": "true",
                "business_impact": "customer_experience"
            },
            "annotations": {
                "summary": f"High API latency on {service_name}",
                "description": self._generate_holiday_aware_description(
                    "API Latency", thresholds["api_response_time_ms"], holiday_status
                ),
                "hindi_summary": f"{service_name} API slow चल रहा है"
            }
        }
        
        # Generate payment success rate rule (critical for Indian e-commerce)
        if "payment" in service_name.lower() or "checkout" in service_name.lower():
            payment_rule = {
                "alert": f"{service_name}_PaymentFailures_Holiday",
                "expr": f'(rate(payment_failures_total{{service="{service_name}"}}[5m]) / rate(payment_attempts_total{{service="{service_name}"}}[5m])) * 100 > {100 - self.alert_config["critical_business_thresholds"]["payment_success_rate"]}',
                "for": "1m",  # Payment alerts should be immediate
                "labels": {
                    "severity": "critical",
                    "service": service_name,
                    "business_critical": "true",
                    "holiday_aware": "true"
                },
                "annotations": {
                    "summary": f"Payment failure rate too high on {service_name}",
                    "description": f"Payment success rate dropped below {self.alert_config['critical_business_thresholds']['payment_success_rate']}%",
                    "hindi_summary": f"Payment fail हो रहे हैं {service_name} में",
                    "immediate_action": "Check payment gateway health and bank connectivity",
                    "revenue_impact": "HIGH"
                }
            }
            alert_rules["groups"][0]["rules"].append(payment_rule)
        
        # Add all rules
        alert_rules["groups"][0]["rules"].extend([cpu_rule, memory_rule, latency_rule])
        
        # Add special festival-specific rules
        if holiday_status["is_holiday"] and holiday_status["special_monitoring_required"]:
            festival_rules = self._generate_festival_specific_rules(service_name, holiday_status)
            alert_rules["groups"][0]["rules"].extend(festival_rules)
        
        return alert_rules
        
    def _generate_holiday_aware_description(self, metric_type: str, threshold: float, 
                                          holiday_status: Dict) -> str:
        """Generate context-aware alert descriptions"""
        
        base_desc = f"{metric_type} usage exceeded {threshold}%"
        
        if holiday_status["is_holiday"]:
            festival_name = holiday_status["holiday_name"]
            day_of_festival = holiday_status["day_of_festival"]
            expected_multiplier = holiday_status["expected_traffic_multiplier"]
            
            context_desc = f" during {festival_name} (Day {day_of_festival}). Expected traffic: {expected_multiplier}x normal. Threshold adjusted for festival load."
            
            return base_desc + context_desc
        else:
            return base_desc + ". Normal business day thresholds applied."
            
    def _generate_festival_specific_rules(self, service_name: str, 
                                        holiday_status: Dict) -> List[Dict]:
        """Generate special monitoring rules for festivals"""
        
        festival_rules = []
        
        # Order volume spike detection
        order_spike_rule = {
            "alert": f"{service_name}_OrderVolumeSpike_Festival",
            "expr": f'rate(orders_created_total{{service="{service_name}"}}[1m]) > rate(orders_created_total{{service="{service_name}"}}[1h] offset 24h) * {holiday_status["expected_traffic_multiplier"] * 1.5}',
            "for": "2m",
            "labels": {
                "severity": "info",
                "service": service_name,
                "festival": holiday_status["holiday_name"],
                "type": "capacity_planning"
            },
            "annotations": {
                "summary": f"Order volume spike detected during {holiday_status['holiday_name']}",
                "description": f"Order rate is {holiday_status['expected_traffic_multiplier'] * 1.5}x higher than same time yesterday",
                "hindi_summary": f"{holiday_status['holiday_name']} में order बहुत ज्यादा आ रहे हैं"
            }
        }
        
        # Regional load distribution
        if self.region == "all_india" and holiday_status["affected_regions"]:
            regional_rule = {
                "alert": f"{service_name}_RegionalLoadImbalance_Festival",
                "expr": f'stddev(rate(requests_total{{service="{service_name}"}}[5m]) by (region)) / avg(rate(requests_total{{service="{service_name}"}}[5m]) by (region)) > 0.5',
                "for": "5m",
                "labels": {
                    "severity": "medium",
                    "service": service_name,
                    "festival": holiday_status["holiday_name"],
                    "type": "load_balancing"
                },
                "annotations": {
                    "summary": "Regional load imbalance during festival",
                    "description": "Traffic distribution across regions is highly uneven",
                    "hindi_summary": "कुछ regions में ज्यादा load है"
                }
            }
            festival_rules.append(regional_rule)
        
        festival_rules.append(order_spike_rule)
        return festival_rules
        
    def generate_alertmanager_config(self) -> Dict[str, Any]:
        """Generate AlertManager configuration for Indian scenarios"""
        
        config = {
            "global": {
                "smtp_smarthost": "smtp.gmail.com:587",
                "smtp_from": "alerts@company.com"
            },
            
            "route": {
                "group_by": ["alertname", "service", "region"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default-receiver",
                "routes": [
                    # Critical payment alerts
                    {
                        "match": {"business_critical": "true"},
                        "receiver": "payment-team",
                        "repeat_interval": "5m"
                    },
                    
                    # Holiday-specific routing
                    {
                        "match": {"holiday_aware": "true"},
                        "receiver": "holiday-oncall",
                        "group_interval": "30s"
                    },
                    
                    # Regional routing
                    {
                        "match_re": {"region": "(mumbai|delhi|bangalore)"},
                        "receiver": "metro-team"
                    }
                ]
            },
            
            "receivers": [
                {
                    "name": "default-receiver",
                    "email_configs": [
                        {
                            "to": "oncall@company.com",
                            "subject": "Alert: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ]
                },
                
                {
                    "name": "payment-team",
                    "slack_configs": [
                        {
                            "api_url": "https://hooks.slack.com/services/PAYMENT_WEBHOOK",
                            "channel": "#payments-critical",
                            "title": "🚨 Payment Alert",
                            "text": "{{ .CommonAnnotations.hindi_summary }}\n{{ .CommonAnnotations.description }}"
                        }
                    ],
                    "webhook_configs": [
                        {
                            "url": "https://api.whatsapp.com/business/webhook",
                            "http_config": {
                                "bearer_token": "WHATSAPP_TOKEN"
                            }
                        }
                    ]
                },
                
                {
                    "name": "holiday-oncall",
                    "email_configs": [
                        {
                            "to": "holiday-oncall@company.com",
                            "subject": "🎉 Festival Alert: {{ .GroupLabels.alertname }}",
                            "body": "{{ .CommonAnnotations.hindi_summary }}\n\nFestival Context:\n{{ .CommonAnnotations.description }}"
                        }
                    ]
                },
                
                {
                    "name": "metro-team",
                    "sms_configs": [  # Custom SMS integration
                        {
                            "api_url": "https://api.textlocal.in/send/",
                            "username": "SMS_USERNAME",
                            "password": "SMS_PASSWORD",
                            "message": "{{ .CommonAnnotations.hindi_summary }}"
                        }
                    ]
                }
            ],
            
            "inhibit_rules": [
                # Suppress memory alerts if CPU is critical
                {
                    "source_match": {"alertname": ".*_HighCPU_.*", "severity": "critical"},
                    "target_match": {"alertname": ".*_HighMemory_.*"},
                    "equal": ["service", "region"]
                },
                
                # Suppress individual service alerts if cluster is down
                {
                    "source_match": {"alertname": "ClusterDown"},
                    "target_match_re": {"alertname": ".*_High.*"},
                    "equal": ["region"]
                }
            ]
        }
        
        return config
        
    def create_holiday_dashboard_config(self, service_name: str) -> Dict[str, Any]:
        """Create Grafana dashboard for holiday monitoring"""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": f"{service_name} - Indian Holiday Monitoring",
                "tags": ["holiday", "indian", service_name],
                "timezone": "Asia/Kolkata",
                "refresh": "30s",
                
                "panels": [
                    # Holiday status panel
                    {
                        "id": 1,
                        "title": "Current Holiday Status",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "holiday_status_active",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "overrides": [
                                {
                                    "matcher": {"id": "byValue", "options": "1"},
                                    "properties": [
                                        {"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}},
                                        {"id": "displayName", "value": "🎉 Festival Active"}
                                    ]
                                }
                            ]
                        }
                    },
                    
                    # Traffic multiplier
                    {
                        "id": 2,
                        "title": "Traffic vs Normal (Holiday Multiplier)",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'rate(requests_total{{service="{service_name}"}}[5m]) / rate(requests_total{{service="{service_name}"}}[5m] offset 24h)',
                                "refId": "A",
                                "legendFormat": "Current vs Yesterday"
                            }
                        ]
                    },
                    
                    # Payment success by method
                    {
                        "id": 3,
                        "title": "Payment Success Rate by Method (Holiday Impact)",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'rate(payment_success_total{{service="{service_name}"}}[5m]) / rate(payment_attempts_total{{service="{service_name}"}}[5m]) * 100',
                                "refId": "A",
                                "legendFormat": "{{payment_method}}"
                            }
                        ],
                        "yAxes": [
                            {
                                "min": 90,
                                "max": 100,
                                "unit": "percent"
                            }
                        ]
                    },
                    
                    # Regional performance
                    {
                        "id": 4,
                        "title": "Regional Performance During Festival",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": f'histogram_quantile(0.95, api_duration_seconds{{service="{service_name}"}}) by (region)',
                                "refId": "A"
                            }
                        ]
                    }
                ]
            }
        }
        
        return dashboard

# Test and utility functions
async def test_diwali_alerting_scenario():
    """Test Diwali season alerting configuration"""
    print("🪔 Testing Diwali alerting scenario...")
    
    alert_manager = IndianHolidayAlertManager("all_india")
    
    # Simulate Diwali date
    diwali_date = datetime(2024, 11, 1)
    holiday_status = alert_manager.check_holiday_status(diwali_date)
    
    print(f"📅 Holiday Status: {holiday_status['is_holiday']}")
    if holiday_status['is_holiday']:
        print(f"🎉 Festival: {holiday_status['holiday_name']}")
        print(f"📈 Expected Traffic: {holiday_status['expected_traffic_multiplier']}x")
        print(f"⏰ Peak Hours: {', '.join(holiday_status['peak_hours'])}")
    
    # Generate alert rules
    service_name = "flipkart-checkout"
    alert_rules = alert_manager.generate_holiday_alert_rules(service_name)
    
    print(f"\n📋 Generated {len(alert_rules['groups'][0]['rules'])} alert rules")
    for rule in alert_rules['groups'][0]['rules']:
        print(f"  - {rule['alert']}: {rule['labels']['severity']}")
    
    # Generate AlertManager config
    am_config = alert_manager.generate_alertmanager_config()
    print(f"\n📧 AlertManager receivers: {len(am_config['receivers'])}")
    
    return alert_rules, am_config

def test_upcoming_holidays():
    """Test upcoming holiday detection"""
    print("\n📅 Testing upcoming holiday detection...")
    
    alert_manager = IndianHolidayAlertManager()
    holiday_status = alert_manager.check_holiday_status()
    
    if holiday_status['upcoming_holidays']:
        print("🔮 Upcoming holidays:")
        for holiday in holiday_status['upcoming_holidays']:
            print(f"  - {holiday['name']}: {holiday['days_until']} days ({holiday['expected_multiplier']}x traffic)")
    else:
        print("😴 No major holidays in next 7 days")

def test_regional_preferences():
    """Test regional alerting preferences"""
    print("\n🗺️  Testing regional preferences...")
    
    regions = ["north_india", "south_india", "west_india", "east_india"]
    
    for region in regions:
        alert_manager = IndianHolidayAlertManager(region)
        regional_config = alert_manager.regional_config.get(region, {})
        
        print(f"\n{region.replace('_', ' ').title()}:")
        print(f"  Languages: {', '.join(regional_config.get('languages', []))}")
        print(f"  Peak Festivals: {', '.join(regional_config.get('peak_festivals', []))}")
        print(f"  Notification: {', '.join(regional_config.get('notification_preferences', []))}")

if __name__ == "__main__":
    print("🚀 Episode 16: Indian Holiday-Aware AlertManager")
    print("🇮🇳 Festival के time smart alerting!")
    print("=" * 60)
    
    # Run test scenarios
    asyncio.run(test_diwali_alerting_scenario())
    test_upcoming_holidays()
    test_regional_preferences()
    
    print("\n" + "=" * 60)
    print("✅ Holiday-aware alerting testing completed!")
    print("🎉 Next: Setup festival season monitoring dashboard")
    print("📊 AlertManager UI: http://localhost:9093")