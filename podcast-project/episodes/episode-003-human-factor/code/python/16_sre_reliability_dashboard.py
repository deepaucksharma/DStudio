#!/usr/bin/env python3
"""
SRE Reliability Dashboard - Episode 3: Human Factor in Tech  
===========================================================

Indian companies (Flipkart, Paytm, HDFC) के लिए comprehensive SRE dashboard
Site Reliability Engineering metrics with Indian business context
Festival seasons, sale events, और regional patterns के साथ

Features:
- Indian business event awareness (Diwali sale, IPL season, monsoon impact)
- Multi-region monitoring (Mumbai, Bangalore, Delhi, Hyderabad)  
- SLA tracking with Indian holiday calendar
- Error budget management with cultural context
- Team burnout prevention with work-life balance
- Real-time alerting with Hindi/English support
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics

class ServiceTier(Enum):
    CRITICAL = "critical"      # Payment, Login - 99.99% SLA
    HIGH = "high"             # Search, Catalog - 99.9% SLA  
    MEDIUM = "medium"         # Analytics, Reports - 99.5% SLA
    LOW = "low"               # Batch jobs, Logs - 99% SLA

class AlertSeverity(Enum):
    CRITICAL = "critical"     # Page immediately
    HIGH = "high"            # Call within 15 min
    MEDIUM = "medium"        # Slack notification
    LOW = "low"              # Email summary

class Region(Enum):
    MUMBAI = "mumbai"
    BANGALORE = "bangalore"
    DELHI = "delhi"
    HYDERABAD = "hyderabad"
    PUNE = "pune"

@dataclass
class ServiceLevel:
    """SLA definition for a service"""
    service_name: str
    tier: ServiceTier
    target_availability: float  # 99.99 = 99.99%
    target_latency_p95: float  # milliseconds
    target_latency_p99: float  # milliseconds
    error_rate_threshold: float  # 0.01 = 1%
    monthly_error_budget: float  # hours of downtime allowed per month

@dataclass  
class Metric:
    """Time-series metric data point"""
    timestamp: datetime
    value: float
    service: str
    region: Region
    metric_type: str  # latency, availability, error_rate, throughput

@dataclass
class Alert:
    """Alert with Indian context"""
    id: str
    service: str
    severity: AlertSeverity
    message: str
    message_hindi: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    region: Optional[Region] = None
    business_impact: str = ""
    customer_impact: str = ""

@dataclass
class IndianBusinessEvent:
    """Indian business events that impact system load"""
    name: str
    start_date: datetime  
    end_date: datetime
    expected_traffic_multiplier: float  # 1.0 = normal, 5.0 = 5x traffic
    affected_services: List[str]
    regions_affected: List[Region]
    description: str

class SREReliabilityDashboard:
    """Main SRE dashboard with Indian business context"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.services: Dict[str, ServiceLevel] = {}
        self.metrics: List[Metric] = []
        self.alerts: Dict[str, Alert] = {}
        self.business_events: List[IndianBusinessEvent] = []
        
        # Regional patterns
        self.regional_patterns = {
            Region.MUMBAI: {"baseline_latency": 45, "monsoon_impact": 1.4, "financial_peak": True},
            Region.BANGALORE: {"baseline_latency": 35, "monsoon_impact": 1.2, "financial_peak": False}, 
            Region.DELHI: {"baseline_latency": 50, "monsoon_impact": 1.3, "financial_peak": False},
            Region.HYDERABAD: {"baseline_latency": 40, "monsoon_impact": 1.1, "financial_peak": False},
            Region.PUNE: {"baseline_latency": 38, "monsoon_impact": 1.3, "financial_peak": False},
        }
        
        # Initialize with common Indian business events
        self._setup_indian_business_calendar()
        
        # SRE team information
        self.sre_team = {
            "mumbai": {"on_call": "Rajesh Kumar", "backup": "Priya Sharma", "load": 0.7},
            "bangalore": {"on_call": "Amit Patel", "backup": "Sneha Reddy", "load": 0.6},
            "delhi": {"on_call": "Vikram Singh", "backup": "Kavya Nair", "load": 0.8},
            "hyderabad": {"on_call": "Arjun Das", "backup": "Riya Gupta", "load": 0.5},
        }
    
    def _setup_indian_business_calendar(self):
        """Setup Indian business events calendar for 2024"""
        events = [
            IndianBusinessEvent(
                "Republic Day Sale",
                datetime(2024, 1, 24), datetime(2024, 1, 28),
                3.5, ["ecommerce", "payment", "cart"], 
                [Region.MUMBAI, Region.DELHI, Region.BANGALORE],
                "Republic Day weekend sales across e-commerce"
            ),
            IndianBusinessEvent(
                "IPL Season Start",
                datetime(2024, 3, 22), datetime(2024, 5, 26), 
                2.8, ["streaming", "fantasy", "payment"],
                list(Region), 
                "Cricket streaming and fantasy sports peak traffic"
            ),
            IndianBusinessEvent(
                "Summer Sale (Amazon/Flipkart)",
                datetime(2024, 5, 10), datetime(2024, 5, 17),
                4.2, ["ecommerce", "payment", "search", "cart"],
                list(Region),
                "Major e-commerce summer sale event"
            ),
            IndianBusinessEvent(
                "Monsoon Impact Period",
                datetime(2024, 6, 15), datetime(2024, 9, 30),
                1.0, ["delivery", "logistics"], 
                [Region.MUMBAI, Region.DELHI, Region.PUNE],
                "Monsoon affects delivery and logistics services"
            ),
            IndianBusinessEvent(
                "Festive Season (Navratri to Diwali)",
                datetime(2024, 10, 3), datetime(2024, 11, 15),
                5.0, ["ecommerce", "payment", "gift", "food"],
                list(Region),
                "Peak festive season with Dussehra, Diwali shopping"
            ),
            IndianBusinessEvent(
                "New Year Sale",
                datetime(2024, 12, 26), datetime(2025, 1, 2),
                3.8, ["ecommerce", "travel", "payment"],
                list(Region),
                "Year-end sales and New Year bookings"
            )
        ]
        self.business_events = events
    
    def add_service(self, service_level: ServiceLevel):
        """Add a service with its SLA definition"""
        self.services[service_level.service_name] = service_level
        print(f"✅ Added service: {service_level.service_name} ({service_level.tier.value})")
        print(f"   SLA: {service_level.target_availability}% availability")
        print(f"   Error Budget: {service_level.monthly_error_budget} hours/month")
    
    def add_metric(self, metric: Metric):
        """Add metric data point"""
        self.metrics.append(metric)
        
        # Check SLA violations and create alerts if needed
        self._check_sla_violations(metric)
    
    def _check_sla_violations(self, metric: Metric):
        """Check if metric violates SLA and create alerts"""
        service_sla = self.services.get(metric.service)
        if not service_sla:
            return
            
        alert_created = False
        
        # Check availability violations
        if metric.metric_type == "availability" and metric.value < service_sla.target_availability:
            severity = AlertSeverity.CRITICAL if metric.value < 95 else AlertSeverity.HIGH
            self._create_alert(
                metric.service,
                severity,
                f"Availability dropped to {metric.value:.2f}% (SLA: {service_sla.target_availability}%)",
                f"उपलब्धता गिरकर {metric.value:.2f}% हो गई है (SLA: {service_sla.target_availability}%)",
                metric.region,
                f"Service availability below SLA threshold"
            )
            alert_created = True
            
        # Check latency violations  
        elif metric.metric_type == "latency_p95" and metric.value > service_sla.target_latency_p95:
            severity = AlertSeverity.HIGH if metric.value > service_sla.target_latency_p95 * 1.5 else AlertSeverity.MEDIUM
            self._create_alert(
                metric.service,
                severity,
                f"P95 latency {metric.value:.0f}ms exceeds SLA {service_sla.target_latency_p95:.0f}ms",
                f"P95 विलंबता {metric.value:.0f}ms SLA {service_sla.target_latency_p95:.0f}ms से अधिक है",
                metric.region,
                f"Response time degradation affecting user experience"
            )
            alert_created = True
            
        # Check error rate violations
        elif metric.metric_type == "error_rate" and metric.value > service_sla.error_rate_threshold:
            severity = AlertSeverity.CRITICAL if metric.value > 0.05 else AlertSeverity.HIGH
            self._create_alert(
                metric.service,
                severity,
                f"Error rate {metric.value:.2%} above threshold {service_sla.error_rate_threshold:.2%}",
                f"त्रुटि दर {metric.value:.2%} सीमा {service_sla.error_rate_threshold:.2%} से अधिक है",
                metric.region,
                f"Increased error rate impacting customer transactions"
            )
            alert_created = True
        
        if alert_created:
            self._assign_alert_to_oncall(metric.region)
    
    def _create_alert(self, service: str, severity: AlertSeverity, message: str, 
                     message_hindi: str, region: Region, business_impact: str):
        """Create a new alert"""
        alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.alerts)}"
        
        alert = Alert(
            id=alert_id,
            service=service,
            severity=severity, 
            message=message,
            message_hindi=message_hindi,
            created_at=datetime.now(),
            region=region,
            business_impact=business_impact
        )
        
        self.alerts[alert_id] = alert
        
        # Auto-assign to on-call engineer for the region
        region_key = region.value if region else "bangalore"  # Default region
        oncall_info = self.sre_team.get(region_key, {})
        if oncall_info:
            alert.assigned_to = oncall_info.get("on_call")
        
        print(f"🚨 ALERT CREATED: {alert_id}")
        print(f"   Service: {service} | Severity: {severity.value}")
        print(f"   Region: {region.value if region else 'All'}")
        print(f"   Message: {message}")
        if alert.assigned_to:
            print(f"   Assigned to: {alert.assigned_to}")
    
    def _assign_alert_to_oncall(self, region: Region):
        """Assign alert to on-call engineer and check load"""
        region_key = region.value if region else "bangalore"
        team_info = self.sre_team.get(region_key, {})
        
        if team_info:
            current_load = team_info.get("load", 0.5)
            oncall_engineer = team_info.get("on_call", "Unknown")
            
            # Check if engineer is overloaded
            if current_load > 0.8:
                backup_engineer = team_info.get("backup", "Unknown") 
                print(f"⚠️ {oncall_engineer} overloaded (load: {current_load:.1f})")
                print(f"   Consider escalating to backup: {backup_engineer}")
    
    def calculate_availability(self, service: str, start_time: datetime, end_time: datetime) -> float:
        """Calculate availability for a service in given time period"""
        service_metrics = [
            m for m in self.metrics 
            if m.service == service and m.metric_type == "availability"
            and start_time <= m.timestamp <= end_time
        ]
        
        if not service_metrics:
            return 100.0
        
        return statistics.mean([m.value for m in service_metrics])
    
    def calculate_error_budget_burn(self, service: str) -> Dict:
        """Calculate error budget consumption for a service"""
        service_sla = self.services.get(service)
        if not service_sla:
            return {}
        
        # Calculate for current month
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        
        # Get availability metrics for current month
        current_availability = self.calculate_availability(service, month_start, now)
        
        # Calculate downtime in hours
        hours_in_month = (now - month_start).total_seconds() / 3600
        actual_uptime_hours = hours_in_month * (current_availability / 100)
        target_uptime_hours = hours_in_month * (service_sla.target_availability / 100)
        downtime_hours = hours_in_month - actual_uptime_hours
        
        # Error budget consumption
        error_budget_used = downtime_hours
        error_budget_remaining = max(0, service_sla.monthly_error_budget - error_budget_used)
        error_budget_burn_rate = (error_budget_used / service_sla.monthly_error_budget) * 100
        
        # Days remaining in month
        import calendar
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        day_of_month = now.day
        days_remaining = days_in_month - day_of_month
        
        return {
            "service": service,
            "current_availability": current_availability,
            "error_budget_total": service_sla.monthly_error_budget,
            "error_budget_used": error_budget_used,
            "error_budget_remaining": error_budget_remaining,
            "burn_rate_percent": error_budget_burn_rate,
            "days_remaining": days_remaining,
            "projected_burn": (error_budget_burn_rate / day_of_month) * days_in_month if day_of_month > 0 else 0
        }
    
    def get_current_business_events(self) -> List[IndianBusinessEvent]:
        """Get currently active business events"""
        now = datetime.now()
        return [
            event for event in self.business_events
            if event.start_date <= now <= event.end_date
        ]
    
    def get_upcoming_business_events(self, days_ahead: int = 7) -> List[IndianBusinessEvent]:
        """Get upcoming business events"""
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        return [
            event for event in self.business_events
            if now <= event.start_date <= future_date
        ]
    
    def generate_reliability_report(self) -> str:
        """Generate comprehensive SRE reliability report"""
        report = f"📊 SRE Reliability Dashboard - {self.company_name}\n"
        report += "=" * 60 + "\n"
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n\n"
        
        # Current business events
        current_events = self.get_current_business_events()
        if current_events:
            report += "🎯 Active Business Events:\n"
            for event in current_events:
                report += f"   • {event.name} (Traffic: {event.expected_traffic_multiplier}x)\n"
                report += f"     {event.description}\n"
            report += "\n"
        
        # Upcoming events
        upcoming_events = self.get_upcoming_business_events()
        if upcoming_events:
            report += "📅 Upcoming Events (Next 7 Days):\n"
            for event in upcoming_events:
                days_until = (event.start_date - datetime.now()).days
                report += f"   • {event.name} in {days_until} days\n"
                report += f"     Expected Traffic: {event.expected_traffic_multiplier}x\n"
            report += "\n"
        
        # Service availability summary
        report += "🎯 Service Availability (Current Month):\n"
        report += "-" * 40 + "\n"
        
        for service_name, service_sla in self.services.items():
            availability = self.calculate_availability(
                service_name, 
                datetime(datetime.now().year, datetime.now().month, 1),
                datetime.now()
            )
            
            status_emoji = "✅" if availability >= service_sla.target_availability else "🚨"
            report += f"{status_emoji} {service_name}: {availability:.3f}% "
            report += f"(SLA: {service_sla.target_availability}%)\n"
            
            # Error budget info
            error_budget = self.calculate_error_budget_burn(service_name)
            if error_budget:
                budget_status = "🟢" if error_budget["burn_rate_percent"] < 50 else "🟡" if error_budget["burn_rate_percent"] < 80 else "🔴"
                report += f"   {budget_status} Error Budget: {error_budget['error_budget_remaining']:.2f}h remaining "
                report += f"({error_budget['burn_rate_percent']:.1f}% used)\n"
        
        report += "\n"
        
        # Regional health
        report += "🗺️ Regional Health Status:\n"
        report += "-" * 30 + "\n"
        
        for region in Region:
            region_alerts = [a for a in self.alerts.values() if a.region == region and not a.resolved_at]
            critical_alerts = len([a for a in region_alerts if a.severity == AlertSeverity.CRITICAL])
            
            health_emoji = "🟢" if critical_alerts == 0 else "🔴" if critical_alerts > 2 else "🟡"
            report += f"{health_emoji} {region.value.title()}: "
            
            if critical_alerts == 0:
                report += "All systems operational\n"
            else:
                report += f"{critical_alerts} critical alert(s) active\n"
            
            # Regional pattern info
            pattern = self.regional_patterns.get(region, {})
            baseline = pattern.get("baseline_latency", 40)
            report += f"   Baseline latency: {baseline}ms\n"
        
        report += "\n"
        
        # Active alerts summary
        active_alerts = [a for a in self.alerts.values() if not a.resolved_at]
        if active_alerts:
            report += f"🚨 Active Alerts ({len(active_alerts)}):\n"
            report += "-" * 25 + "\n"
            
            # Group by severity
            alert_by_severity = defaultdict(list)
            for alert in active_alerts:
                alert_by_severity[alert.severity].append(alert)
            
            for severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM, AlertSeverity.LOW]:
                alerts = alert_by_severity[severity]
                if alerts:
                    severity_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🔵"}
                    report += f"{severity_emoji[severity.value]} {severity.value.upper()}: {len(alerts)} alert(s)\n"
                    
                    for alert in alerts[:3]:  # Show top 3 per severity
                        age = datetime.now() - alert.created_at
                        hours = int(age.total_seconds() // 3600)
                        minutes = int((age.total_seconds() % 3600) // 60)
                        report += f"   • {alert.service}: {alert.message[:50]}... "
                        report += f"({hours}h {minutes}m old)\n"
                        if alert.assigned_to:
                            report += f"     Assigned to: {alert.assigned_to}\n"
        else:
            report += "✅ No Active Alerts - All systems healthy!\n"
        
        report += "\n"
        
        # SRE team load
        report += "👥 SRE Team Status:\n"
        report += "-" * 20 + "\n"
        
        for region_name, team_info in self.sre_team.items():
            load = team_info["load"]
            load_emoji = "🟢" if load < 0.6 else "🟡" if load < 0.8 else "🔴"
            
            report += f"{load_emoji} {region_name.title()}: {team_info['on_call']} "
            report += f"(Load: {load:.1f})\n"
            
            if load > 0.8:
                report += f"   ⚠️ High load - backup available: {team_info['backup']}\n"
        
        report += "\n"
        
        # Recommendations
        report += "💡 Recommendations:\n"
        report += "-" * 18 + "\n"
        
        recommendations = []
        
        # Check for overloaded regions
        overloaded_regions = [
            region for region, info in self.sre_team.items()
            if info["load"] > 0.8
        ]
        if overloaded_regions:
            recommendations.append(f"🎯 Redistribute load from overloaded regions: {', '.join(overloaded_regions)}")
        
        # Check error budget burn
        high_burn_services = []
        for service_name in self.services.keys():
            error_budget = self.calculate_error_budget_burn(service_name)
            if error_budget and error_budget["burn_rate_percent"] > 80:
                high_burn_services.append(service_name)
        
        if high_burn_services:
            recommendations.append(f"⚡ Focus on reliability for: {', '.join(high_burn_services)}")
        
        # Upcoming event preparations
        upcoming = self.get_upcoming_business_events(14)  # Next 2 weeks
        high_impact_events = [e for e in upcoming if e.expected_traffic_multiplier > 3.0]
        if high_impact_events:
            recommendations.append(f"📈 Prepare for high-traffic events: {', '.join([e.name for e in high_impact_events])}")
        
        # General recommendations
        if len(active_alerts) > 10:
            recommendations.append("🔔 Consider alert fatigue - review alert thresholds")
        
        recommendations.append("🌟 Regular SRE postmortems for continuous improvement")
        recommendations.append("📚 Update runbooks for Indian business event patterns")
        
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def simulate_metrics(self, duration_hours: int = 24):
        """Simulate realistic metrics for demo"""
        start_time = datetime.now() - timedelta(hours=duration_hours)
        
        # Check if we're in a business event period
        traffic_multiplier = 1.0
        current_events = self.get_current_business_events()
        if current_events:
            traffic_multiplier = max([e.expected_traffic_multiplier for e in current_events])
        
        for service_name, service_sla in self.services.items():
            for hour in range(duration_hours):
                timestamp = start_time + timedelta(hours=hour)
                
                for region in Region:
                    # Get regional baseline
                    regional_pattern = self.regional_patterns.get(region, {})
                    baseline_latency = regional_pattern.get("baseline_latency", 40)
                    
                    # Simulate availability (usually high, occasional dips)
                    if random.random() < 0.05:  # 5% chance of availability drop
                        availability = random.uniform(95.0, 99.5)
                    else:
                        availability = random.uniform(99.8, 100.0)
                    
                    self.add_metric(Metric(
                        timestamp=timestamp,
                        value=availability,
                        service=service_name,
                        region=region,
                        metric_type="availability"
                    ))
                    
                    # Simulate latency (affected by traffic and region)
                    base_latency = baseline_latency
                    traffic_impact = (traffic_multiplier - 1.0) * 20  # +20ms per 1x traffic
                    random_variation = random.uniform(-10, 25)  # Some randomness
                    p95_latency = base_latency + traffic_impact + random_variation
                    
                    # Monsoon impact (if applicable)
                    if datetime.now().month in [6, 7, 8, 9]:  # Monsoon months
                        monsoon_impact = regional_pattern.get("monsoon_impact", 1.0)
                        p95_latency *= monsoon_impact
                    
                    self.add_metric(Metric(
                        timestamp=timestamp,
                        value=p95_latency,
                        service=service_name,
                        region=region, 
                        metric_type="latency_p95"
                    ))
                    
                    # Simulate error rate (usually low, spikes during issues)
                    if random.random() < 0.02:  # 2% chance of error spike
                        error_rate = random.uniform(0.01, 0.08)
                    else:
                        error_rate = random.uniform(0.0001, 0.005)
                    
                    self.add_metric(Metric(
                        timestamp=timestamp,
                        value=error_rate,
                        service=service_name,
                        region=region,
                        metric_type="error_rate"
                    ))

# Demo function
def main():
    print("📊 SRE Reliability Dashboard Demo - Indian E-commerce Context")
    print("=" * 65)
    
    # Initialize dashboard for a fictional Indian e-commerce company
    dashboard = SREReliabilityDashboard("भारत E-Commerce Ltd")
    
    # Define services with realistic SLAs
    services = [
        ServiceLevel("payment-service", ServiceTier.CRITICAL, 99.99, 100, 200, 0.001, 0.73),  # 99.99% = ~43 min/month
        ServiceLevel("user-auth", ServiceTier.CRITICAL, 99.95, 150, 300, 0.005, 3.65),      # 99.95% = ~3.6 hrs/month  
        ServiceLevel("product-catalog", ServiceTier.HIGH, 99.9, 200, 400, 0.01, 7.31),     # 99.9% = ~7.3 hrs/month
        ServiceLevel("search-service", ServiceTier.HIGH, 99.9, 250, 500, 0.01, 7.31),
        ServiceLevel("recommendation", ServiceTier.MEDIUM, 99.5, 500, 1000, 0.02, 36.5),   # 99.5% = ~36.5 hrs/month
        ServiceLevel("analytics", ServiceTier.LOW, 99.0, 1000, 2000, 0.05, 73.0),          # 99.0% = ~73 hrs/month
    ]
    
    for service in services:
        dashboard.add_service(service)
    
    print(f"\n{'='*65}")
    print("📈 Simulating 48 Hours of Metrics...")
    print(f"{'='*65}")
    
    # Simulate metrics for the last 48 hours
    dashboard.simulate_metrics(48)
    
    print(f"✅ Generated {len(dashboard.metrics)} metrics")
    print(f"🚨 Created {len(dashboard.alerts)} alerts")
    
    print(f"\n{'='*65}")
    print("📋 SRE Reliability Report:")
    print(f"{'='*65}")
    
    # Generate and print comprehensive report
    report = dashboard.generate_reliability_report()
    print(report)
    
    print(f"{'='*65}")
    print("🔍 Detailed Alert Analysis:")
    print(f"{'='*65}")
    
    # Show detailed alert information
    active_alerts = [a for a in dashboard.alerts.values() if not a.resolved_at]
    if active_alerts:
        for i, alert in enumerate(sorted(active_alerts, key=lambda x: x.created_at, reverse=True)[:5], 1):
            print(f"\n{i}. Alert ID: {alert.id}")
            print(f"   Service: {alert.service} | Severity: {alert.severity.value}")
            print(f"   Region: {alert.region.value if alert.region else 'All'}")
            print(f"   Message: {alert.message}")
            print(f"   Hindi: {alert.message_hindi}")
            print(f"   Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if alert.assigned_to:
                print(f"   Assigned to: {alert.assigned_to}")
            print(f"   Business Impact: {alert.business_impact}")
    
    print(f"\n{'='*65}")
    print("💼 Business Context Analysis:")
    print(f"{'='*65}")
    
    # Show business event impact
    current_events = dashboard.get_current_business_events()
    if current_events:
        print("🎯 Currently Active Business Events:")
        for event in current_events:
            print(f"   • {event.name}")
            print(f"     Duration: {event.start_date.strftime('%Y-%m-%d')} to {event.end_date.strftime('%Y-%m-%d')}")
            print(f"     Traffic Impact: {event.expected_traffic_multiplier}x normal")
            print(f"     Affected Services: {', '.join(event.affected_services)}")
            print(f"     Description: {event.description}")
            print()
    
    upcoming_events = dashboard.get_upcoming_business_events(30)  # Next 30 days
    if upcoming_events:
        print("📅 Upcoming Business Events (Next 30 Days):")
        for event in upcoming_events:
            days_until = (event.start_date - datetime.now()).days
            print(f"   • {event.name} in {days_until} days")
            print(f"     Expected Traffic: {event.expected_traffic_multiplier}x")
    
    print(f"\n{'='*65}")
    print("✅ SRE Dashboard Demo Complete!")
    print(f"{'='*65}")
    
    print("\n🎯 Key Features Demonstrated:")
    print("   - Indian business event awareness (festivals, sales, IPL)")
    print("   - Multi-region monitoring with cultural context")
    print("   - SLA tracking with realistic Indian scenarios")
    print("   - Error budget management and burn rate calculation") 
    print("   - Regional patterns (monsoon impact, traffic variations)")
    print("   - Hindi language support for alerts")
    print("   - Team workload balancing with on-call rotations")
    print("   - Business impact analysis for incidents")
    
    print("\n💡 Production Implementation Tips:")
    print("   - Integrate with existing monitoring tools (Grafana, DataDog)")
    print("   - Set up automated alert routing based on severity")
    print("   - Configure business event calendar updates")
    print("   - Implement error budget alerting and automation")
    print("   - Add team escalation policies with backup coverage")

if __name__ == "__main__":
    main()