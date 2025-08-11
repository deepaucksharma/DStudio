#!/usr/bin/env python3
"""
SLA Calculator - Production-Ready Availability & Error Budget Tracking
======================================================================
Calculate uptime percentages, error budgets, and downtime costs for Indian scale systems.

Real-world examples:
- Paytm UPI: 99.9% SLA requirement (8.77 hours downtime/year allowed)
- Flipkart BigBillionDays: 99.99% target (52.6 minutes/year)
- IRCTC booking: 99.5% practical SLA (43.8 hours/year)
- Ola ride matching: 99.95% target (4.38 hours/year)

Features:
- Uptime percentage calculations
- Error budget tracking with alerts
- Downtime cost estimation in INR
- SLA compliance monitoring
- Multi-service SLA aggregation
- Real-time SLA dashboard
- Incident impact analysis
"""

import math
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque, defaultdict


class SLAType(Enum):
    """Types of SLA measurements"""
    AVAILABILITY = "availability"           # Uptime percentage
    RESPONSE_TIME = "response_time"        # Latency SLA
    ERROR_RATE = "error_rate"              # Error percentage
    THROUGHPUT = "throughput"              # Requests per second
    CUSTOMER_SATISFACTION = "csat"         # Customer satisfaction score


class SLASeverity(Enum):
    """SLA violation severity levels"""
    MINOR = "minor"           # < 5% of error budget consumed
    MODERATE = "moderate"     # 5-20% of error budget consumed  
    MAJOR = "major"           # 20-50% of error budget consumed
    CRITICAL = "critical"     # > 50% of error budget consumed


@dataclass
class SLADefinition:
    """SLA definition with thresholds and targets"""
    name: str
    sla_type: SLAType
    target_percentage: float  # e.g., 99.9 for 99.9% uptime
    measurement_window: str   # "monthly", "quarterly", "yearly"
    error_budget_percentage: float  # Derived: 100 - target_percentage
    
    # Business context
    service_name: str
    business_criticality: str  # "low", "medium", "high", "critical"
    cost_per_minute_inr: float  # Revenue loss per minute in INR
    
    # Thresholds for alerts
    warning_threshold: float = 50.0    # % of error budget consumed
    critical_threshold: float = 80.0   # % of error budget consumed


@dataclass
class IncidentRecord:
    """Record of a service incident affecting SLA"""
    incident_id: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime]
    severity: SLASeverity
    description: str
    
    # SLA impact
    affected_sla_types: List[SLAType]
    downtime_minutes: Optional[float] = None
    error_rate_impact: Optional[float] = None
    response_time_impact: Optional[float] = None
    
    # Business impact
    estimated_cost_inr: Optional[float] = None
    customers_affected: Optional[int] = None
    
    # Resolution
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    lessons_learned: List[str] = None
    
    def __post_init__(self):
        if self.lessons_learned is None:
            self.lessons_learned = []
        
        # Calculate downtime if end_time is set
        if self.end_time and not self.downtime_minutes:
            self.downtime_minutes = (self.end_time - self.start_time).total_seconds() / 60


@dataclass
class SLAMetric:
    """Current SLA metrics for a service"""
    service_name: str
    sla_definition: SLADefinition
    measurement_period_start: datetime
    
    # Current metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_downtime_minutes: float = 0.0
    total_measurement_minutes: float = 0.0
    
    # Response time metrics
    response_times: List[float] = None
    p50_response_time: Optional[float] = None
    p95_response_time: Optional[float] = None
    p99_response_time: Optional[float] = None
    
    # Calculated values
    current_availability: Optional[float] = None
    current_error_rate: Optional[float] = None
    error_budget_consumed: Optional[float] = None
    error_budget_remaining: Optional[float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate current SLA metrics"""
        # Calculate availability
        if self.total_measurement_minutes > 0:
            uptime_minutes = self.total_measurement_minutes - self.total_downtime_minutes
            self.current_availability = (uptime_minutes / self.total_measurement_minutes) * 100
            
            # Calculate error budget consumption
            target_uptime = self.sla_definition.target_percentage
            if target_uptime < 100:
                max_allowed_downtime = ((100 - target_uptime) / 100) * self.total_measurement_minutes
                if max_allowed_downtime > 0:
                    self.error_budget_consumed = (self.total_downtime_minutes / max_allowed_downtime) * 100
                    self.error_budget_remaining = max(0, 100 - self.error_budget_consumed)
        
        # Calculate error rate
        if self.total_requests > 0:
            self.current_error_rate = (self.failed_requests / self.total_requests) * 100
        
        # Calculate response time percentiles
        if self.response_times:
            sorted_times = sorted(self.response_times)
            n = len(sorted_times)
            self.p50_response_time = sorted_times[int(n * 0.5)]
            self.p95_response_time = sorted_times[int(n * 0.95)]
            self.p99_response_time = sorted_times[int(n * 0.99)]


class SLACalculator:
    """Main SLA calculation engine"""
    
    def __init__(self):
        self.sla_definitions: Dict[str, SLADefinition] = {}
        self.current_metrics: Dict[str, SLAMetric] = {}
        self.incidents: List[IncidentRecord] = []
        self.historical_data: Dict[str, List[SLAMetric]] = defaultdict(list)
        
    def add_sla_definition(self, sla_def: SLADefinition):
        """Add SLA definition for a service"""
        self.sla_definitions[sla_def.service_name] = sla_def
        
        # Initialize current metrics
        self.current_metrics[sla_def.service_name] = SLAMetric(
            service_name=sla_def.service_name,
            sla_definition=sla_def,
            measurement_period_start=datetime.now()
        )
        
        print(f"✅ SLA definition added for {sla_def.service_name}: {sla_def.target_percentage}% target")
    
    def calculate_availability_sla(self, uptime_minutes: float, total_minutes: float) -> float:
        """Calculate availability SLA percentage"""
        if total_minutes <= 0:
            return 100.0
        
        return (uptime_minutes / total_minutes) * 100
    
    def calculate_error_budget(self, target_percentage: float, measurement_window_hours: float) -> Dict[str, float]:
        """Calculate error budget in various units"""
        error_percentage = 100 - target_percentage
        
        # Convert to time units
        total_minutes = measurement_window_hours * 60
        total_seconds = measurement_window_hours * 3600
        
        error_budget_minutes = (error_percentage / 100) * total_minutes
        error_budget_seconds = (error_percentage / 100) * total_seconds
        
        return {
            'error_percentage': error_percentage,
            'error_budget_minutes': error_budget_minutes,
            'error_budget_seconds': error_budget_seconds,
            'error_budget_hours': error_budget_minutes / 60,
            'error_budget_days': error_budget_minutes / (60 * 24)
        }
    
    def calculate_downtime_cost(self, downtime_minutes: float, cost_per_minute_inr: float,
                               affected_users: Optional[int] = None) -> Dict[str, float]:
        """Calculate business impact of downtime"""
        direct_cost = downtime_minutes * cost_per_minute_inr
        
        # Estimated indirect costs (reputation, customer churn, etc.)
        indirect_multiplier = 1.5  # 50% additional indirect costs
        total_cost = direct_cost * indirect_multiplier
        
        result = {
            'downtime_minutes': downtime_minutes,
            'direct_cost_inr': direct_cost,
            'indirect_cost_inr': total_cost - direct_cost,
            'total_cost_inr': total_cost,
            'cost_per_minute_inr': cost_per_minute_inr
        }
        
        if affected_users:
            result['cost_per_user_inr'] = total_cost / affected_users
            result['affected_users'] = affected_users
        
        return result
    
    def record_incident(self, incident: IncidentRecord):
        """Record an incident and update SLA metrics"""
        self.incidents.append(incident)
        
        # Update current metrics
        if incident.service_name in self.current_metrics:
            metrics = self.current_metrics[incident.service_name]
            
            if incident.downtime_minutes:
                metrics.total_downtime_minutes += incident.downtime_minutes
            
            # Update total measurement time
            time_since_start = (datetime.now() - metrics.measurement_period_start).total_seconds() / 60
            metrics.total_measurement_minutes = time_since_start
            
            # Recalculate metrics
            metrics._calculate_metrics()
            
            # Calculate cost impact
            if not incident.estimated_cost_inr and incident.downtime_minutes:
                sla_def = self.sla_definitions[incident.service_name]
                cost_info = self.calculate_downtime_cost(
                    incident.downtime_minutes,
                    sla_def.cost_per_minute_inr,
                    incident.customers_affected
                )
                incident.estimated_cost_inr = cost_info['total_cost_inr']
        
        print(f"📝 Incident recorded: {incident.incident_id} ({incident.downtime_minutes:.1f}min downtime)")
    
    def check_sla_violations(self) -> List[Dict[str, Any]]:
        """Check for current SLA violations"""
        violations = []
        
        for service_name, metrics in self.current_metrics.items():
            sla_def = self.sla_definitions[service_name]
            
            # Check availability SLA
            if metrics.current_availability and metrics.current_availability < sla_def.target_percentage:
                severity = self._determine_violation_severity(metrics.error_budget_consumed or 0)
                
                violations.append({
                    'service_name': service_name,
                    'sla_type': 'availability',
                    'target': sla_def.target_percentage,
                    'current': metrics.current_availability,
                    'error_budget_consumed': metrics.error_budget_consumed,
                    'severity': severity.value,
                    'time_to_exhaustion_hours': self._calculate_time_to_exhaustion(metrics)
                })
            
            # Check error rate (if applicable)
            if (sla_def.sla_type == SLAType.ERROR_RATE and 
                metrics.current_error_rate and 
                metrics.current_error_rate > (100 - sla_def.target_percentage)):
                
                violations.append({
                    'service_name': service_name,
                    'sla_type': 'error_rate',
                    'target': 100 - sla_def.target_percentage,
                    'current': metrics.current_error_rate,
                    'severity': 'major'
                })
        
        return violations
    
    def _determine_violation_severity(self, error_budget_consumed: float) -> SLASeverity:
        """Determine severity based on error budget consumption"""
        if error_budget_consumed >= 80:
            return SLASeverity.CRITICAL
        elif error_budget_consumed >= 50:
            return SLASeverity.MAJOR
        elif error_budget_consumed >= 20:
            return SLASeverity.MODERATE
        else:
            return SLASeverity.MINOR
    
    def _calculate_time_to_exhaustion(self, metrics: SLAMetric) -> Optional[float]:
        """Calculate hours until error budget is exhausted at current burn rate"""
        if not metrics.error_budget_remaining or metrics.error_budget_remaining <= 0:
            return 0.0
        
        if not metrics.total_downtime_minutes or metrics.total_measurement_minutes <= 0:
            return None
        
        # Calculate current burn rate (downtime per hour)
        measurement_hours = metrics.total_measurement_minutes / 60
        current_burn_rate = metrics.total_downtime_minutes / measurement_hours  # minutes downtime per hour
        
        if current_burn_rate <= 0:
            return None  # No current downtime, can't predict
        
        # Calculate remaining error budget in minutes
        sla_def = metrics.sla_definition
        error_budget_percentage = 100 - sla_def.target_percentage
        
        # For yearly measurement (assuming)
        yearly_minutes = 365 * 24 * 60
        total_error_budget_minutes = (error_budget_percentage / 100) * yearly_minutes
        remaining_error_budget_minutes = (metrics.error_budget_remaining / 100) * total_error_budget_minutes
        
        # Time to exhaustion
        hours_to_exhaustion = remaining_error_budget_minutes / current_burn_rate
        return max(0, hours_to_exhaustion)
    
    def generate_sla_report(self, service_name: Optional[str] = None) -> str:
        """Generate comprehensive SLA report"""
        services_to_report = [service_name] if service_name else list(self.sla_definitions.keys())
        
        report = f"""
📊 SLA MONITORING REPORT
{'='*40}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Services Monitored: {len(services_to_report)}

"""
        
        total_cost_impact = 0.0
        
        for service in services_to_report:
            if service not in self.current_metrics:
                continue
            
            metrics = self.current_metrics[service]
            sla_def = self.sla_definitions[service]
            
            # Calculate measurement period
            measurement_days = metrics.total_measurement_minutes / (60 * 24)
            
            report += f"""
🎯 SERVICE: {service.upper()}
{'-'*30}
SLA Target: {sla_def.target_percentage}%
Business Criticality: {sla_def.business_criticality}
Measurement Period: {measurement_days:.1f} days

Current Metrics:
  Availability: {metrics.current_availability:.3f}% {'✅' if metrics.current_availability and metrics.current_availability >= sla_def.target_percentage else '❌'}
  Total Downtime: {metrics.total_downtime_minutes:.1f} minutes
  Error Budget Consumed: {metrics.error_budget_consumed:.1f}%
  Error Budget Remaining: {metrics.error_budget_remaining:.1f}%
"""
            
            # Error rate if applicable
            if metrics.current_error_rate is not None:
                report += f"  Error Rate: {metrics.current_error_rate:.3f}%\n"
            
            # Response time metrics
            if metrics.p95_response_time:
                report += f"  P95 Response Time: {metrics.p95_response_time:.0f}ms\n"
                report += f"  P99 Response Time: {metrics.p99_response_time:.0f}ms\n"
            
            # Recent incidents for this service
            service_incidents = [i for i in self.incidents if i.service_name == service]
            if service_incidents:
                report += f"\nRecent Incidents: {len(service_incidents)}\n"
                
                total_incident_cost = sum(i.estimated_cost_inr or 0 for i in service_incidents)
                total_cost_impact += total_incident_cost
                
                report += f"Total Incident Cost: ₹{total_incident_cost:,.2f}\n"
                
                # Most recent incident
                latest_incident = max(service_incidents, key=lambda x: x.start_time)
                report += f"Latest Incident: {latest_incident.incident_id} ({latest_incident.severity.value})\n"
        
        # Overall summary
        violations = self.check_sla_violations()
        
        report += f"""

🚨 CURRENT VIOLATIONS
{'-'*21}
Active Violations: {len(violations)}
"""
        
        for violation in violations:
            report += f"""
{violation['service_name']}: {violation['sla_type']}
  Target: {violation['target']:.2f}%
  Current: {violation['current']:.2f}%
  Severity: {violation['severity'].upper()}
  Error Budget: {violation.get('error_budget_consumed', 0):.1f}% consumed
"""
            
            if violation.get('time_to_exhaustion_hours'):
                report += f"  Time to Budget Exhaustion: {violation['time_to_exhaustion_hours']:.1f} hours\n"
        
        report += f"""

💰 BUSINESS IMPACT SUMMARY
{'-'*27}
Total Incident Cost: ₹{total_cost_impact:,.2f}
Average Cost per Incident: ₹{total_cost_impact / max(len(self.incidents), 1):,.2f}
Total Incidents: {len(self.incidents)}

📋 RECOMMENDATIONS
{'-'*18}"""
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        for i, rec in enumerate(recommendations, 1):
            report += f"\n{i}. {rec}"
        
        return report
    
    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on SLA status"""
        recommendations = []
        
        # Critical violations
        critical_violations = [v for v in violations if v.get('severity') == 'critical']
        if critical_violations:
            recommendations.append("🚨 URGENT: Address critical SLA violations immediately")
            recommendations.append("🔄 Implement immediate incident response procedures")
        
        # Error budget recommendations
        high_budget_consumption = [v for v in violations if v.get('error_budget_consumed', 0) > 50]
        if high_budget_consumption:
            recommendations.append("⚠️  High error budget consumption - reduce deployment frequency")
            recommendations.append("🛡️  Implement additional monitoring and alerting")
        
        # General recommendations
        recommendations.append("📈 Review and optimize critical service components")
        recommendations.append("🧪 Conduct chaos engineering experiments")
        recommendations.append("📚 Update incident response documentation")
        recommendations.append("👥 Train team on SLA management best practices")
        
        return recommendations


def create_indian_platform_slas():
    """Create realistic SLA definitions for Indian platforms"""
    
    slas = []
    
    # 1. Paytm UPI Payment System
    slas.append(SLADefinition(
        name="Paytm_UPI_Availability",
        sla_type=SLAType.AVAILABILITY,
        target_percentage=99.9,  # 99.9% uptime
        measurement_window="monthly",
        error_budget_percentage=0.1,
        service_name="paytm_upi",
        business_criticality="critical",
        cost_per_minute_inr=500000,  # ₹5L per minute loss
        warning_threshold=60.0,
        critical_threshold=85.0
    ))
    
    # 2. Flipkart Product Catalog
    slas.append(SLADefinition(
        name="Flipkart_Catalog_Availability", 
        sla_type=SLAType.AVAILABILITY,
        target_percentage=99.95,  # Higher availability for catalog
        measurement_window="monthly",
        error_budget_percentage=0.05,
        service_name="flipkart_catalog",
        business_criticality="high",
        cost_per_minute_inr=200000,  # ₹2L per minute
        warning_threshold=50.0,
        critical_threshold=80.0
    ))
    
    # 3. IRCTC Booking System
    slas.append(SLADefinition(
        name="IRCTC_Booking_Availability",
        sla_type=SLAType.AVAILABILITY,
        target_percentage=99.5,   # More realistic for high-traffic booking
        measurement_window="monthly",
        error_budget_percentage=0.5,
        service_name="irctc_booking",
        business_criticality="high",
        cost_per_minute_inr=100000,  # ₹1L per minute
        warning_threshold=70.0,
        critical_threshold=90.0
    ))
    
    # 4. Ola Ride Matching Response Time
    slas.append(SLADefinition(
        name="Ola_Matching_ResponseTime",
        sla_type=SLAType.RESPONSE_TIME,
        target_percentage=99.0,   # 99% of requests under threshold
        measurement_window="monthly",
        error_budget_percentage=1.0,
        service_name="ola_matching",
        business_criticality="high", 
        cost_per_minute_inr=50000,   # ₹50k per minute
        warning_threshold=60.0,
        critical_threshold=80.0
    ))
    
    # 5. Zomato Delivery Tracking
    slas.append(SLADefinition(
        name="Zomato_Tracking_Availability",
        sla_type=SLAType.AVAILABILITY,
        target_percentage=99.8,
        measurement_window="monthly", 
        error_budget_percentage=0.2,
        service_name="zomato_tracking",
        business_criticality="medium",
        cost_per_minute_inr=25000,   # ₹25k per minute
        warning_threshold=65.0,
        critical_threshold=85.0
    ))
    
    return slas


def simulate_realistic_incidents():
    """Create realistic incident scenarios for Indian platforms"""
    
    incidents = []
    base_time = datetime.now() - timedelta(days=30)  # Last 30 days
    
    # 1. Paytm UPI Database Overload
    incidents.append(IncidentRecord(
        incident_id="INC-2024-001",
        service_name="paytm_upi",
        start_time=base_time + timedelta(days=5, hours=14, minutes=30),
        end_time=base_time + timedelta(days=5, hours=15, minutes=45),
        severity=SLASeverity.MAJOR,
        description="Database connection pool exhaustion during high transaction volume",
        affected_sla_types=[SLAType.AVAILABILITY],
        downtime_minutes=75,
        customers_affected=500000,
        root_cause="Database connection pool misconfiguration",
        resolution_summary="Increased connection pool size and added circuit breakers",
        lessons_learned=[
            "Monitor database connection pool metrics",
            "Implement graceful degradation for high load",
            "Add auto-scaling for database connections"
        ]
    ))
    
    # 2. Flipkart BigBillionDays Load Balancer Failure
    incidents.append(IncidentRecord(
        incident_id="INC-2024-002",
        service_name="flipkart_catalog",
        start_time=base_time + timedelta(days=12, hours=10, minutes=0),
        end_time=base_time + timedelta(days=12, hours=10, minutes=20),
        severity=SLASeverity.CRITICAL,
        description="Load balancer failure during Big Billion Days peak traffic",
        affected_sla_types=[SLAType.AVAILABILITY],
        downtime_minutes=20,
        customers_affected=2000000,
        root_cause="Load balancer health check misconfiguration",
        resolution_summary="Failed over to secondary load balancer, fixed health checks",
        lessons_learned=[
            "Test load balancer failover regularly",
            "Monitor load balancer health check accuracy",
            "Implement instant failover mechanisms"
        ]
    ))
    
    # 3. IRCTC Tatkal Booking Rush Memory Leak
    incidents.append(IncidentRecord(
        incident_id="INC-2024-003", 
        service_name="irctc_booking",
        start_time=base_time + timedelta(days=18, hours=10, minutes=0),  # Tatkal time
        end_time=base_time + timedelta(days=18, hours=12, minutes=30),
        severity=SLASeverity.MAJOR,
        description="Memory leak in booking service during Tatkal rush",
        affected_sla_types=[SLAType.AVAILABILITY, SLAType.RESPONSE_TIME],
        downtime_minutes=150,
        customers_affected=800000,
        root_cause="Memory leak in session management code",
        resolution_summary="Restarted services, deployed memory leak fix",
        lessons_learned=[
            "Implement memory monitoring and alerts",
            "Regular memory profiling for booking services",
            "Auto-restart services on memory threshold breach"
        ]
    ))
    
    # 4. Ola Ride Matching Network Partition
    incidents.append(IncidentRecord(
        incident_id="INC-2024-004",
        service_name="ola_matching",
        start_time=base_time + timedelta(days=22, hours=19, minutes=15),
        end_time=base_time + timedelta(days=22, hours=19, minutes=45),
        severity=SLASeverity.MODERATE,
        description="Network partition between matching service and driver location service",
        affected_sla_types=[SLAType.RESPONSE_TIME],
        response_time_impact=5000,  # 5 second delay
        customers_affected=150000,
        root_cause="Network configuration change caused partition",
        resolution_summary="Restored network connectivity, improved monitoring",
        lessons_learned=[
            "Implement network partition detection",
            "Add fallback mechanisms for network issues",
            "Monitor inter-service network connectivity"
        ]
    ))
    
    # 5. Zomato Delivery Tracking Cache Failure
    incidents.append(IncidentRecord(
        incident_id="INC-2024-005",
        service_name="zomato_tracking", 
        start_time=base_time + timedelta(days=25, hours=13, minutes=0),
        end_time=base_time + timedelta(days=25, hours=14, minutes=15),
        severity=SLASeverity.MINOR,
        description="Redis cache cluster failure affecting delivery tracking",
        affected_sla_types=[SLAType.AVAILABILITY, SLAType.RESPONSE_TIME],
        downtime_minutes=75,
        customers_affected=100000,
        root_cause="Redis cluster failover misconfiguration",
        resolution_summary="Fixed Redis failover, added cache warming",
        lessons_learned=[
            "Test cache failover mechanisms regularly",
            "Implement cache warming strategies", 
            "Add graceful degradation without cache"
        ]
    ))
    
    return incidents


def demo_sla_calculator():
    """Demonstrate SLA calculator with realistic Indian platform data"""
    
    print("📊 SLA CALCULATOR DEMO - INDIAN PLATFORM EDITION")
    print("="*55)
    
    # Initialize SLA calculator
    calculator = SLACalculator()
    
    # Add SLA definitions
    sla_definitions = create_indian_platform_slas()
    print(f"\n📋 Loading {len(sla_definitions)} SLA definitions...")
    
    for sla_def in sla_definitions:
        calculator.add_sla_definition(sla_def)
    
    # Demonstrate error budget calculations
    print(f"\n🎯 ERROR BUDGET EXAMPLES:")
    for target in [99.9, 99.95, 99.5]:
        monthly_hours = 30 * 24  # 30 days
        error_budget = calculator.calculate_error_budget(target, monthly_hours)
        print(f"  {target}% SLA → {error_budget['error_budget_minutes']:.1f} minutes/month allowed downtime")
    
    # Simulate realistic incidents
    incidents = simulate_realistic_incidents()
    print(f"\n📝 Recording {len(incidents)} realistic incidents...")
    
    for incident in incidents:
        calculator.record_incident(incident)
    
    # Calculate costs
    print(f"\n💰 DOWNTIME COST EXAMPLES:")
    cost_examples = [
        (30, 500000, "Paytm UPI 30min outage"),
        (20, 200000, "Flipkart catalog 20min outage"),
        (150, 100000, "IRCTC booking 2.5hr outage")
    ]
    
    total_demo_cost = 0
    for minutes, cost_per_min, description in cost_examples:
        cost_info = calculator.calculate_downtime_cost(minutes, cost_per_min, 500000)
        total_demo_cost += cost_info['total_cost_inr']
        print(f"  {description}: ₹{cost_info['total_cost_inr']:,.0f}")
    
    print(f"  Total Demo Costs: ₹{total_demo_cost:,.0f}")
    
    # Check violations
    violations = calculator.check_sla_violations()
    print(f"\n🚨 SLA Violations: {len(violations)} active")
    
    # Generate comprehensive report
    print(f"\n📊 GENERATING COMPREHENSIVE SLA REPORT...")
    report = calculator.generate_sla_report()
    print(report)
    
    # Demonstrate real-time monitoring setup
    print(f"\n🔄 REAL-TIME SLA MONITORING SETUP:")
    print("  - Error budget burn rate alerts configured")
    print("  - Violation severity escalation rules active")
    print("  - Cost impact tracking enabled")
    print("  - Incident correlation analysis ready")
    
    # Save results
    results = {
        'sla_definitions': [asdict(sla) for sla in sla_definitions],
        'incidents': [asdict(incident) for incident in incidents],
        'current_metrics': {name: asdict(metrics) for name, metrics in calculator.current_metrics.items()},
        'violations': violations,
        'summary': {
            'total_services': len(sla_definitions),
            'total_incidents': len(incidents), 
            'total_cost_impact': total_demo_cost,
            'report_date': datetime.now().isoformat()
        }
    }
    
    with open('sla_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to sla_analysis_results.json")
    
    print(f"\n💡 SLA MANAGEMENT INSIGHTS:")
    print("1. Error budgets provide quantifiable reliability targets")
    print("2. Proactive monitoring prevents SLA violations") 
    print("3. Incident cost tracking justifies reliability investments")
    print("4. Regular SLA reviews ensure business alignment")
    print("5. Automated alerting enables rapid response")
    
    print(f"\n💰 BUSINESS VALUE:")
    print("- Cost visibility: Track reliability investment ROI")
    print("- Risk management: Quantify downtime business impact") 
    print("- Performance optimization: Data-driven improvement")
    print("- Customer satisfaction: Meet reliability expectations")
    print(f"- Potential savings: ₹{total_demo_cost:,.0f}+ prevented through proactive SLA management")


if __name__ == "__main__":
    demo_sla_calculator()