#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 8: SLI/SLO Monitoring for Indian E-commerce

भारतीय context: 99.9% uptime maintain करना Indian festivals के दौरान
जैसे BBD में Flipkart का SLA commitment vs reality tracking

Real-world scenario: Paytm UPI के 99.95% availability SLA
Challenge: Regional variations, payment partner SLAs, compliance requirements
"""

import time
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import structlog
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

# भारतीय SLI/SLO categories और compliance requirements
class SLICategory(Enum):
    """Service Level Indicator categories for Indian business"""
    AVAILABILITY = "availability"        # Service uptime
    LATENCY = "latency"                  # Response time
    THROUGHPUT = "throughput"            # Requests per second
    ERROR_RATE = "error_rate"            # Error percentage
    PAYMENT_SUCCESS = "payment_success"   # Payment completion rate
    ORDER_SUCCESS = "order_success"      # Order completion rate
    DATA_FRESHNESS = "data_freshness"    # Real-time data lag
    COMPLIANCE = "compliance"            # Regulatory adherence

class BusinessImpact(Enum):
    """Business impact levels for Indian market"""
    CRITICAL = "critical"      # Revenue stopping - immediate escalation
    HIGH = "high"             # Customer experience impact
    MEDIUM = "medium"         # Performance degradation
    LOW = "low"               # Internal metrics
    
class ComplianceType(Enum):
    """Indian regulatory compliance types"""
    RBI_GUIDELINES = "rbi_guidelines"
    DPDP_ACT = "dpdp_act" 
    IT_ACT = "it_act"
    GST_COMPLIANCE = "gst_compliance"
    KYC_NORMS = "kyc_norms"

@dataclass
class SLIDefinition:
    """Service Level Indicator definition for Indian services"""
    name: str
    category: SLICategory
    description: str
    measurement_query: str  # Prometheus query
    unit: str
    good_threshold: float
    total_threshold: float
    business_impact: BusinessImpact
    regional_variations: Dict[str, float] = field(default_factory=dict)
    compliance_requirements: List[ComplianceType] = field(default_factory=list)
    
@dataclass
class SLOTarget:
    """Service Level Objective target definition"""
    name: str
    sli_name: str
    target_percentage: float  # e.g., 99.9%
    time_window_hours: int    # e.g., 24, 168 (weekly), 720 (monthly)
    error_budget_minutes: float  # Calculated based on target
    alert_threshold_percentage: float  # When to alert (e.g., 50% budget consumed)
    business_justification: str
    cost_per_nine: float  # Cost in INR for additional 9 (99% -> 99.9%)

class IndianSLISLOMonitor:
    """
    Indian E-commerce SLI/SLO Monitoring System
    
    Features:
    - Multi-regional SLI tracking
    - Festival season SLO adjustments
    - Payment partner SLA monitoring
    - Regulatory compliance tracking
    - Error budget management
    - Cost-aware SLO setting
    """
    
    def __init__(self, service_name: str, region: str = "all_india"):
        self.service_name = service_name
        self.region = region
        self.current_time = datetime.now()
        
        # Initialize SLI definitions for Indian e-commerce
        self.sli_definitions = self._initialize_indian_sli_definitions()
        
        # Initialize SLO targets
        self.slo_targets = self._initialize_slo_targets()
        
        # Time-series data storage (in production, use Prometheus/InfluxDB)
        self.sli_data = defaultdict(lambda: deque(maxlen=10080))  # 7 days of minute data
        self.error_budgets = {}
        
        # Regional configurations
        self.regional_config = self._setup_regional_config()
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Logger
        self.logger = structlog.get_logger("indian-sli-slo-monitor")
        
    def _initialize_indian_sli_definitions(self) -> Dict[str, SLIDefinition]:
        """Initialize SLI definitions for Indian e-commerce scenarios"""
        
        sli_definitions = {
            # API Availability SLI
            "api_availability": SLIDefinition(
                name="API Availability",
                category=SLICategory.AVAILABILITY,
                description="Percentage of successful API requests (non-5xx responses)",
                measurement_query='sum(rate(http_requests_total{code!~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100',
                unit="percentage",
                good_threshold=1.0,
                total_threshold=1.0,
                business_impact=BusinessImpact.CRITICAL,
                regional_variations={
                    "mumbai": 99.95,
                    "bangalore": 99.90,
                    "delhi": 99.85,
                    "tier2_cities": 99.70,
                    "tier3_cities": 99.50
                },
                compliance_requirements=[ComplianceType.RBI_GUIDELINES, ComplianceType.IT_ACT]
            ),
            
            # Payment Success Rate SLI (Critical for Indian market)
            "payment_success_rate": SLIDefinition(
                name="Payment Success Rate",
                category=SLICategory.PAYMENT_SUCCESS,
                description="Percentage of successful payment transactions",
                measurement_query='sum(rate(payment_success_total[5m])) / sum(rate(payment_attempts_total[5m])) * 100',
                unit="percentage", 
                good_threshold=1.0,
                total_threshold=1.0,
                business_impact=BusinessImpact.CRITICAL,
                regional_variations={
                    "mumbai": 99.7,  # Higher due to better infrastructure
                    "bangalore": 99.5,
                    "delhi": 99.3,
                    "tier2_cities": 98.5,  # Network issues
                    "tier3_cities": 97.0   # Infrastructure challenges
                },
                compliance_requirements=[ComplianceType.RBI_GUIDELINES, ComplianceType.KYC_NORMS]
            ),
            
            # API Latency SLI
            "api_latency": SLIDefinition(
                name="API Response Latency",
                category=SLICategory.LATENCY,
                description="95th percentile API response time",
                measurement_query='histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000',
                unit="milliseconds",
                good_threshold=200.0,  # < 200ms is good
                total_threshold=float('inf'),
                business_impact=BusinessImpact.HIGH,
                regional_variations={
                    "mumbai": 150,     # Best infrastructure
                    "bangalore": 180,
                    "delhi": 200,
                    "tier2_cities": 300,
                    "tier3_cities": 500  # Higher latency acceptable
                }
            ),
            
            # UPI Transaction Latency (India-specific)
            "upi_transaction_latency": SLIDefinition(
                name="UPI Transaction Latency", 
                category=SLICategory.LATENCY,
                description="Time taken for UPI transaction completion",
                measurement_query='histogram_quantile(0.95, rate(upi_transaction_duration_seconds_bucket[5m])) * 1000',
                unit="milliseconds",
                good_threshold=3000.0,  # UPI guideline: < 3 seconds
                total_threshold=float('inf'),
                business_impact=BusinessImpact.CRITICAL,
                compliance_requirements=[ComplianceType.RBI_GUIDELINES]
            ),
            
            # Order Success Rate
            "order_success_rate": SLIDefinition(
                name="Order Success Rate",
                category=SLICategory.ORDER_SUCCESS,
                description="Percentage of orders successfully placed",
                measurement_query='sum(rate(orders_successful_total[5m])) / sum(rate(orders_attempted_total[5m])) * 100',
                unit="percentage",
                good_threshold=1.0,
                total_threshold=1.0,
                business_impact=BusinessImpact.HIGH,
                regional_variations={
                    "mumbai": 99.2,
                    "bangalore": 99.0,
                    "delhi": 98.8,
                    "tier2_cities": 98.0,
                    "tier3_cities": 97.0
                }
            ),
            
            # Data Freshness (for real-time features)
            "inventory_data_freshness": SLIDefinition(
                name="Inventory Data Freshness",
                category=SLICategory.DATA_FRESHNESS,
                description="Age of inventory data in cache",
                measurement_query='avg(time() - inventory_last_updated_timestamp)',
                unit="seconds",
                good_threshold=300.0,  # < 5 minutes is fresh
                total_threshold=float('inf'),
                business_impact=BusinessImpact.MEDIUM
            ),
            
            # Compliance SLI
            "kyc_completion_rate": SLIDefinition(
                name="KYC Completion Rate",
                category=SLICategory.COMPLIANCE,
                description="Percentage of successful KYC verifications",
                measurement_query='sum(rate(kyc_successful_total[5m])) / sum(rate(kyc_attempted_total[5m])) * 100',
                unit="percentage",
                good_threshold=1.0,
                total_threshold=1.0,
                business_impact=BusinessImpact.CRITICAL,
                compliance_requirements=[ComplianceType.KYC_NORMS, ComplianceType.RBI_GUIDELINES]
            )
        }
        
        return sli_definitions
        
    def _initialize_slo_targets(self) -> Dict[str, List[SLOTarget]]:
        """Initialize SLO targets for different time windows"""
        
        slo_targets = {
            # API Availability SLOs
            "api_availability": [
                SLOTarget(
                    name="API Availability - Daily",
                    sli_name="api_availability",
                    target_percentage=99.9,  # 99.9% daily
                    time_window_hours=24,
                    error_budget_minutes=1.44,  # (100-99.9)/100 * 24 * 60
                    alert_threshold_percentage=50.0,  # Alert when 50% budget consumed
                    business_justification="Critical for customer experience",
                    cost_per_nine=50000  # ₹50k per additional 9
                ),
                SLOTarget(
                    name="API Availability - Weekly",
                    sli_name="api_availability", 
                    target_percentage=99.95,  # 99.95% weekly
                    time_window_hours=168,
                    error_budget_minutes=5.04,  # (100-99.95)/100 * 168 * 60
                    alert_threshold_percentage=25.0,
                    business_justification="Weekly business review metric",
                    cost_per_nine=200000  # ₹2L per additional 9
                )
            ],
            
            # Payment Success Rate SLOs (Most critical)
            "payment_success_rate": [
                SLOTarget(
                    name="Payment Success - Hourly",
                    sli_name="payment_success_rate",
                    target_percentage=99.5,  # 99.5% hourly
                    time_window_hours=1,
                    error_budget_minutes=0.3,  # Very tight budget
                    alert_threshold_percentage=25.0,
                    business_justification="Immediate revenue impact",
                    cost_per_nine=100000  # ₹1L per 9 (expensive but critical)
                ),
                SLOTarget(
                    name="Payment Success - Daily",
                    sli_name="payment_success_rate",
                    target_percentage=99.8,
                    time_window_hours=24,
                    error_budget_minutes=2.88,
                    alert_threshold_percentage=50.0,
                    business_justification="Daily business operations",
                    cost_per_nine=300000  # ₹3L per 9
                )
            ],
            
            # API Latency SLOs
            "api_latency": [
                SLOTarget(
                    name="API Latency - Daily",
                    sli_name="api_latency",
                    target_percentage=95.0,  # 95% of requests < 200ms
                    time_window_hours=24,
                    error_budget_minutes=72.0,  # 5% * 24 * 60
                    alert_threshold_percentage=75.0,
                    business_justification="Customer experience standard",
                    cost_per_nine=25000  # ₹25k per improved percentile
                )
            ],
            
            # UPI Transaction Latency (RBI Compliance)
            "upi_transaction_latency": [
                SLOTarget(
                    name="UPI Latency - Hourly",
                    sli_name="upi_transaction_latency", 
                    target_percentage=98.0,  # 98% < 3 seconds (RBI guideline)
                    time_window_hours=1,
                    error_budget_minutes=1.2,
                    alert_threshold_percentage=10.0,  # Very strict
                    business_justification="RBI compliance requirement",
                    cost_per_nine=150000  # Compliance cost
                )
            ]
        }
        
        # Calculate error budgets for all SLOs
        for sli_name, slos in slo_targets.items():
            for slo in slos:
                # Error budget = (100 - target_percentage) / 100 * time_window_hours * 60
                slo.error_budget_minutes = (100 - slo.target_percentage) / 100 * slo.time_window_hours * 60
                
        return slo_targets
        
    def _setup_regional_config(self) -> Dict[str, Any]:
        """Setup regional SLO configurations"""
        
        return {
            "mumbai": {
                "infrastructure_tier": "tier1",
                "network_quality": "excellent", 
                "payment_partner_sla": 99.8,
                "expected_load": "high",
                "slo_adjustment": 1.0  # No adjustment needed
            },
            "bangalore": {
                "infrastructure_tier": "tier1",
                "network_quality": "good",
                "payment_partner_sla": 99.5,
                "expected_load": "high", 
                "slo_adjustment": 0.98
            },
            "delhi": {
                "infrastructure_tier": "tier1",
                "network_quality": "good",
                "payment_partner_sla": 99.3,
                "expected_load": "medium",
                "slo_adjustment": 0.95
            },
            "tier2_cities": {
                "infrastructure_tier": "tier2",
                "network_quality": "fair",
                "payment_partner_sla": 98.5,
                "expected_load": "medium",
                "slo_adjustment": 0.9
            },
            "tier3_cities": {
                "infrastructure_tier": "tier3", 
                "network_quality": "poor",
                "payment_partner_sla": 97.0,
                "expected_load": "low",
                "slo_adjustment": 0.8
            }
        }
        
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for SLI/SLO monitoring"""
        
        # SLI metrics
        self.sli_gauge = Gauge(
            'sli_current_value',
            'Current SLI value',
            ['service', 'sli_name', 'region'],
            registry=self.registry
        )
        
        # Error budget metrics
        self.error_budget_remaining = Gauge(
            'error_budget_remaining_ratio',
            'Remaining error budget ratio (0-1)',
            ['service', 'slo_name', 'time_window'],
            registry=self.registry
        )
        
        # SLO compliance metrics
        self.slo_compliance = Gauge(
            'slo_compliance_ratio',
            'SLO compliance ratio over time window',
            ['service', 'slo_name', 'time_window'],
            registry=self.registry
        )
        
        # Business impact metrics
        self.business_impact_cost = Gauge(
            'business_impact_cost_inr',
            'Estimated business impact cost in INR',
            ['service', 'sli_name', 'impact_type'],
            registry=self.registry
        )
        
    def record_sli_measurement(self, sli_name: str, value: float, timestamp: datetime = None):
        """Record a new SLI measurement"""
        
        if timestamp is None:
            timestamp = datetime.now()
            
        if sli_name not in self.sli_definitions:
            self.logger.warning(f"Unknown SLI: {sli_name}")
            return
            
        # Store measurement
        self.sli_data[sli_name].append({
            "timestamp": timestamp,
            "value": value,
            "region": self.region
        })
        
        # Update Prometheus metrics
        self.sli_gauge.labels(
            service=self.service_name,
            sli_name=sli_name,
            region=self.region
        ).set(value)
        
        # Check for SLO violations
        self._check_slo_violations(sli_name, value, timestamp)
        
        # Log measurement
        self.logger.info(
            "sli_measurement_recorded",
            sli_name=sli_name,
            value=value,
            service=self.service_name,
            region=self.region
        )
        
    def _check_slo_violations(self, sli_name: str, current_value: float, timestamp: datetime):
        """Check if current measurement violates any SLOs"""
        
        if sli_name not in self.slo_targets:
            return
            
        sli_def = self.sli_definitions[sli_name]
        
        for slo in self.slo_targets[sli_name]:
            # Calculate if this measurement violates SLO
            is_violation = self._is_slo_violation(sli_def, current_value)
            
            if is_violation:
                # Update error budget consumption
                self._consume_error_budget(slo, timestamp)
                
                # Check if we need to alert
                remaining_budget = self.get_error_budget_remaining(slo.name)
                
                if remaining_budget <= (slo.alert_threshold_percentage / 100):
                    self._trigger_slo_alert(slo, remaining_budget, current_value)
                    
    def _is_slo_violation(self, sli_def: SLIDefinition, current_value: float) -> bool:
        """Determine if current value violates SLO based on SLI type"""
        
        # For latency-based SLIs (lower is better)
        if sli_def.category in [SLICategory.LATENCY]:
            return current_value > sli_def.good_threshold
            
        # For percentage-based SLIs (higher is better) 
        elif sli_def.category in [SLICategory.AVAILABILITY, SLICategory.PAYMENT_SUCCESS, 
                                  SLICategory.ORDER_SUCCESS, SLICategory.COMPLIANCE]:
            return current_value < sli_def.good_threshold
            
        # For freshness-based SLIs (lower is better)
        elif sli_def.category in [SLICategory.DATA_FRESHNESS]:
            return current_value > sli_def.good_threshold
            
        return False
        
    def _consume_error_budget(self, slo: SLOTarget, timestamp: datetime):
        """Consume error budget when SLO is violated"""
        
        if slo.name not in self.error_budgets:
            self.error_budgets[slo.name] = {
                "total_budget_minutes": slo.error_budget_minutes,
                "consumed_minutes": 0.0,
                "window_start": timestamp,
                "violations": []
            }
            
        # Add violation (simplified - in reality, calculate actual impact)
        self.error_budgets[slo.name]["consumed_minutes"] += 1.0  # 1 minute per violation
        self.error_budgets[slo.name]["violations"].append({
            "timestamp": timestamp,
            "impact_minutes": 1.0
        })
        
        # Update Prometheus metric
        remaining_ratio = self.get_error_budget_remaining(slo.name)
        self.error_budget_remaining.labels(
            service=self.service_name,
            slo_name=slo.name,
            time_window=f"{slo.time_window_hours}h"
        ).set(remaining_ratio)
        
    def _trigger_slo_alert(self, slo: SLOTarget, remaining_budget: float, current_value: float):
        """Trigger alert when SLO is at risk"""
        
        alert_data = {
            "alert_type": "slo_budget_exhaustion",
            "service": self.service_name,
            "slo_name": slo.name,
            "remaining_budget_percentage": remaining_budget * 100,
            "current_value": current_value,
            "business_justification": slo.business_justification,
            "estimated_cost_impact_inr": self._calculate_cost_impact(slo),
            "alert_timestamp": datetime.now().isoformat(),
            "severity": "critical" if remaining_budget < 0.1 else "high"
        }
        
        # Update business impact metric
        cost_impact = self._calculate_cost_impact(slo)
        self.business_impact_cost.labels(
            service=self.service_name,
            sli_name=slo.sli_name,
            impact_type="slo_violation"
        ).set(cost_impact)
        
        self.logger.critical(
            "slo_alert_triggered",
            **alert_data
        )
        
        # In production, send to alerting system (PagerDuty, Slack, etc.)
        return alert_data
        
    def _calculate_cost_impact(self, slo: SLOTarget) -> float:
        """Calculate estimated cost impact of SLO violation"""
        
        # Simplified cost calculation
        base_cost = slo.cost_per_nine
        
        # Adjust for business impact
        if slo.sli_name == "payment_success_rate":
            # Payment failures have direct revenue impact
            return base_cost * 5  # 5x multiplier for payment issues
        elif slo.sli_name == "api_availability":
            # API downtime affects all users
            return base_cost * 3  # 3x multiplier for availability
        else:
            return base_cost
            
    def get_error_budget_remaining(self, slo_name: str) -> float:
        """Get remaining error budget as ratio (0-1)"""
        
        if slo_name not in self.error_budgets:
            return 1.0  # Full budget available
            
        budget_info = self.error_budgets[slo_name]
        total_budget = budget_info["total_budget_minutes"]
        consumed_budget = budget_info["consumed_minutes"]
        
        remaining = max(0, (total_budget - consumed_budget) / total_budget)
        return remaining
        
    def get_slo_compliance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive SLO compliance report"""
        
        report = {
            "service": self.service_name,
            "region": self.region,
            "report_period": {
                "start": (self.current_time - timedelta(hours=time_window_hours)).isoformat(),
                "end": self.current_time.isoformat(),
                "window_hours": time_window_hours
            },
            "slo_compliance": {},
            "error_budget_status": {},
            "business_impact_summary": {},
            "recommendations": []
        }
        
        for sli_name, slos in self.slo_targets.items():
            for slo in slos:
                if slo.time_window_hours == time_window_hours:
                    
                    # Calculate compliance percentage
                    compliance_pct = self._calculate_slo_compliance(slo, time_window_hours)
                    
                    # Error budget status
                    remaining_budget = self.get_error_budget_remaining(slo.name)
                    
                    # Business impact assessment
                    cost_impact = self._calculate_cost_impact(slo)
                    
                    report["slo_compliance"][slo.name] = {
                        "target_percentage": slo.target_percentage,
                        "actual_percentage": compliance_pct,
                        "met": compliance_pct >= slo.target_percentage,
                        "gap": max(0, slo.target_percentage - compliance_pct)
                    }
                    
                    report["error_budget_status"][slo.name] = {
                        "remaining_ratio": remaining_budget,
                        "remaining_minutes": remaining_budget * slo.error_budget_minutes,
                        "total_budget_minutes": slo.error_budget_minutes,
                        "status": self._get_budget_status(remaining_budget)
                    }
                    
                    report["business_impact_summary"][slo.name] = {
                        "estimated_cost_inr": cost_impact,
                        "business_justification": slo.business_justification,
                        "criticality": self.sli_definitions[sli_name].business_impact.value
                    }
                    
        # Generate recommendations
        report["recommendations"] = self._generate_slo_recommendations(report)
        
        return report
        
    def _calculate_slo_compliance(self, slo: SLOTarget, time_window_hours: int) -> float:
        """Calculate actual SLO compliance percentage"""
        
        # In production, query actual metrics from Prometheus
        # For demo, simulate compliance calculation
        
        base_compliance = 99.5  # Base compliance rate
        
        # Adjust based on regional configuration
        regional_adjustment = self.regional_config.get(self.region, {}).get("slo_adjustment", 1.0)
        
        # Add some randomness for demo
        random_factor = random.uniform(0.95, 1.02)
        
        actual_compliance = min(100.0, base_compliance * regional_adjustment * random_factor)
        
        return round(actual_compliance, 2)
        
    def _get_budget_status(self, remaining_ratio: float) -> str:
        """Get descriptive status for error budget"""
        
        if remaining_ratio > 0.8:
            return "healthy"
        elif remaining_ratio > 0.5:
            return "monitoring"
        elif remaining_ratio > 0.2:
            return "concerning" 
        elif remaining_ratio > 0.05:
            return "critical"
        else:
            return "exhausted"
            
    def _generate_slo_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable SLO recommendations"""
        
        recommendations = []
        
        for slo_name, compliance in report["slo_compliance"].items():
            if not compliance["met"]:
                gap = compliance["gap"]
                
                if "payment" in slo_name.lower():
                    recommendations.append(
                        f"Payment SLO violation detected. Gap: {gap:.2f}%. "
                        "Immediate actions: Check payment gateway health, review bank connectivity, "
                        "verify UPI partner SLAs."
                    )
                elif "availability" in slo_name.lower():
                    recommendations.append(
                        f"Availability SLO violation. Gap: {gap:.2f}%. "
                        "Actions: Review infrastructure scaling, check load balancer health, "
                        "analyze recent deployments."
                    )
                elif "latency" in slo_name.lower():
                    recommendations.append(
                        f"Latency SLO violation. Gap: {gap:.2f}%. "
                        "Actions: Profile slow queries, review cache hit rates, "
                        "check CDN performance, analyze regional routing."
                    )
        
        # Budget exhaustion warnings
        for slo_name, budget in report["error_budget_status"].items():
            if budget["status"] in ["critical", "exhausted"]:
                recommendations.append(
                    f"Error budget {budget['status']} for {slo_name}. "
                    f"Only {budget['remaining_minutes']:.1f} minutes remaining. "
                    "Consider implementing emergency procedures or relaxing non-critical features."
                )
        
        # Regional recommendations
        if self.region in ["tier2_cities", "tier3_cities"]:
            recommendations.append(
                f"Operating in {self.region} with infrastructure limitations. "
                "Consider regional SLO adjustments and targeted infrastructure investments."
            )
        
        return recommendations

# Test and simulation functions
async def simulate_flipkart_bbd_slo_monitoring():
    """Simulate BBD scenario with SLO monitoring"""
    print("🛒 Simulating Flipkart BBD SLO monitoring...")
    
    # Initialize monitor for checkout service
    monitor = IndianSLISLOMonitor("flipkart-checkout", "mumbai")
    
    print(f"📊 Initialized {len(monitor.sli_definitions)} SLIs and {sum(len(slos) for slos in monitor.slo_targets.values())} SLOs")
    
    # Simulate 1 hour of measurements during BBD peak
    simulation_duration_minutes = 60
    measurements_per_minute = 1
    
    print(f"🕒 Simulating {simulation_duration_minutes} minutes of BBD traffic...")
    
    for minute in range(simulation_duration_minutes):
        timestamp = datetime.now() - timedelta(minutes=simulation_duration_minutes - minute)
        
        # BBD traffic characteristics
        if 30 <= minute <= 45:  # Peak 15 minutes
            traffic_multiplier = 10.0
        elif 15 <= minute <= 50:  # High traffic period
            traffic_multiplier = 5.0
        else:  # Normal traffic
            traffic_multiplier = 1.0
        
        # Simulate API availability (degrades under high load)
        base_availability = 99.8
        load_impact = max(0, (traffic_multiplier - 1) * 0.1)  # Each multiplier reduces by 0.1%
        api_availability = base_availability - load_impact + random.uniform(-0.2, 0.1)
        monitor.record_sli_measurement("api_availability", api_availability, timestamp)
        
        # Simulate payment success rate (critical during BBD)
        base_payment_success = 99.5
        # Payment gateways struggle more under load
        payment_load_impact = max(0, (traffic_multiplier - 1) * 0.15)
        payment_success = base_payment_success - payment_load_impact + random.uniform(-0.3, 0.1)
        monitor.record_sli_measurement("payment_success_rate", payment_success, timestamp)
        
        # Simulate API latency (increases with load)
        base_latency = 150  # ms
        latency_increase = (traffic_multiplier - 1) * 50  # 50ms per multiplier
        api_latency = base_latency + latency_increase + random.uniform(-20, 40)
        monitor.record_sli_measurement("api_latency", api_latency, timestamp)
        
        # Simulate UPI transaction latency
        base_upi_latency = 2000  # 2 seconds
        upi_latency_increase = (traffic_multiplier - 1) * 300  # 300ms per multiplier
        upi_latency = base_upi_latency + upi_latency_increase + random.uniform(-200, 500)
        monitor.record_sli_measurement("upi_transaction_latency", upi_latency, timestamp)
        
        if minute % 15 == 0:  # Progress update every 15 minutes
            print(f"  📈 Minute {minute}: Traffic {traffic_multiplier}x, API: {api_availability:.2f}%, Payment: {payment_success:.2f}%, Latency: {api_latency:.0f}ms")
    
    print("✅ BBD simulation completed!")
    
    # Generate compliance report
    report = monitor.get_slo_compliance_report(1)  # 1 hour report
    
    print(f"\n📋 SLO Compliance Report:")
    print(f"Service: {report['service']}")
    print(f"Region: {report['region']}")
    print(f"Report Period: {report['report_period']['window_hours']} hours")
    
    print(f"\n📊 SLO Compliance:")
    for slo_name, compliance in report["slo_compliance"].items():
        status = "✅ MET" if compliance["met"] else "❌ MISSED"
        print(f"  {slo_name}: {status} (Target: {compliance['target_percentage']}%, Actual: {compliance['actual_percentage']}%)")
        
    print(f"\n💰 Error Budget Status:")
    for slo_name, budget in report["error_budget_status"].items():
        status_emoji = {"healthy": "🟢", "monitoring": "🟡", "concerning": "🟠", "critical": "🔴", "exhausted": "💀"}
        emoji = status_emoji.get(budget["status"], "❓")
        print(f"  {slo_name}: {emoji} {budget['status'].upper()} ({budget['remaining_ratio']*100:.1f}% remaining)")
        
    print(f"\n💡 Recommendations:")
    for i, recommendation in enumerate(report["recommendations"], 1):
        print(f"  {i}. {recommendation}")
    
    return monitor, report

def test_regional_slo_variations():
    """Test SLO monitoring across different Indian regions"""
    print("\n🗺️  Testing regional SLO variations...")
    
    regions = ["mumbai", "bangalore", "delhi", "tier2_cities", "tier3_cities"]
    
    for region in regions:
        print(f"\n📍 Region: {region.replace('_', ' ').title()}")
        
        monitor = IndianSLISLOMonitor("paytm-upi", region)
        
        # Simulate some measurements
        for sli_name in ["api_availability", "payment_success_rate", "api_latency"]:
            if sli_name in monitor.sli_definitions:
                regional_config = monitor.regional_config.get(region, {})
                adjustment = regional_config.get("slo_adjustment", 1.0)
                
                # Simulate measurement based on regional capability
                if sli_name == "api_latency":
                    # Higher latency in lower tier regions
                    base_value = 200 / adjustment  # Inverse relationship for latency
                else:
                    # Lower availability/success rates in lower tier regions  
                    base_value = 99.0 * adjustment
                
                monitor.record_sli_measurement(sli_name, base_value)
                
                regional_threshold = monitor.sli_definitions[sli_name].regional_variations.get(region)
                if regional_threshold:
                    print(f"  {sli_name}: {base_value:.2f} (Regional target: {regional_threshold})")

def test_payment_slo_compliance_tracking():
    """Test payment-specific SLO compliance tracking"""
    print("\n💳 Testing payment SLO compliance...")
    
    monitor = IndianSLISLOMonitor("razorpay-gateway", "all_india")
    
    # Simulate payment scenarios
    scenarios = [
        {"name": "Normal Operations", "success_rate": 99.7, "latency": 150},
        {"name": "Bank Server Issues", "success_rate": 97.2, "latency": 300},
        {"name": "Network Congestion", "success_rate": 99.1, "latency": 450},
        {"name": "UPI Maintenance", "success_rate": 95.8, "latency": 600},
        {"name": "Recovery Phase", "success_rate": 99.4, "latency": 200}
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n🎭 Scenario {i+1}: {scenario['name']}")
        
        # Record measurements for this scenario
        monitor.record_sli_measurement("payment_success_rate", scenario["success_rate"])
        monitor.record_sli_measurement("api_latency", scenario["latency"])
        
        # Check error budget impact
        for slo_name in monitor.error_budgets:
            remaining = monitor.get_error_budget_remaining(slo_name)
            print(f"  Error budget remaining for {slo_name}: {remaining*100:.1f}%")

if __name__ == "__main__":
    print("🚀 Episode 16: SLI/SLO Monitoring for Indian E-commerce")
    print("🇮🇳 99.9% uptime ka commitment track karte hain!")
    print("=" * 60)
    
    # Run comprehensive testing
    asyncio.run(simulate_flipkart_bbd_slo_monitoring())
    test_regional_slo_variations()
    test_payment_slo_compliance_tracking()
    
    print("\n" + "=" * 60)
    print("✅ SLI/SLO monitoring testing completed!")
    print("📊 Key Insights:")
    print("  - Festival traffic requires SLO adjustments")
    print("  - Payment SLOs are most critical for revenue")
    print("  - Regional variations need separate targets")
    print("  - Error budget management prevents alert fatigue")
    print("🔍 Next: Implement SLO alerting and dashboards")