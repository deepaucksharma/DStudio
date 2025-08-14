#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 14: Performance Regression Detection System

भारतीय context: Swiggy delivery time regression detection
जैसे festival season में delivery time बढ़ना या app response slow होना

Real-world scenario: Flipkart checkout performance regression during BBD
Challenge: Baseline establishment, Statistical significance, Business impact assessment
"""

import time
import json
import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pandas as pd
from scipy import stats
import structlog

# भारतीय performance metrics categories
class PerformanceMetric(Enum):
    """Performance metrics for Indian applications"""
    API_RESPONSE_TIME = "api_response_time"              # API latency
    PAGE_LOAD_TIME = "page_load_time"                    # Web page load time
    APP_LAUNCH_TIME = "app_launch_time"                  # Mobile app launch
    DATABASE_QUERY_TIME = "database_query_time"          # DB performance
    PAYMENT_SUCCESS_RATE = "payment_success_rate"        # Payment completion rate
    ORDER_COMPLETION_TIME = "order_completion_time"      # E-commerce order flow
    SEARCH_RESPONSE_TIME = "search_response_time"        # Search functionality
    LOGIN_SUCCESS_RATE = "login_success_rate"           # Authentication success
    DELIVERY_TIME = "delivery_time"                      # Food/package delivery
    UPI_TRANSACTION_TIME = "upi_transaction_time"       # UPI payment speed

class RegressionSeverity(Enum):
    """Severity levels for performance regressions"""
    CRITICAL = "critical"      # >50% degradation - immediate action
    HIGH = "high"             # 25-50% degradation - urgent attention
    MEDIUM = "medium"         # 10-25% degradation - investigate soon
    LOW = "low"              # 5-10% degradation - monitor closely
    INFO = "info"            # <5% degradation - informational

class DetectionMethod(Enum):
    """Statistical methods for regression detection"""
    PERCENTAGE_CHANGE = "percentage_change"      # Simple percentage comparison
    Z_SCORE = "z_score"                         # Z-score statistical test
    T_TEST = "t_test"                           # Student's t-test
    MANN_WHITNEY = "mann_whitney"               # Non-parametric test
    CHANGEPOINT = "changepoint"                 # Change point detection
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"  # Seasonal analysis

@dataclass
class PerformanceSnapshot:
    """Single performance measurement snapshot"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    service: str
    region: str
    device_type: Optional[str] = None
    user_segment: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BaselinePeriod:
    """Performance baseline definition"""
    start_time: datetime
    end_time: datetime
    metric_name: str
    service: str
    region: str
    sample_count: int
    mean_value: float
    std_deviation: float
    percentiles: Dict[str, float]  # p50, p90, p95, p99
    confidence_interval: Tuple[float, float]
    seasonal_pattern: Optional[Dict[str, float]] = None

@dataclass
class PerformanceRegression:
    """Detected performance regression"""
    regression_id: str
    detection_time: datetime
    metric_name: str
    service: str
    region: str
    severity: RegressionSeverity
    detection_method: DetectionMethod
    baseline_value: float
    current_value: float
    percentage_change: float
    statistical_significance: float  # p-value
    confidence_level: float
    business_impact: Dict[str, Any]
    root_cause_candidates: List[str]
    recommended_actions: List[str]
    false_positive_probability: float

class IndianPerformanceRegressionDetector:
    """
    Indian Scale Performance Regression Detection System
    
    Features:
    - Multi-metric baseline establishment
    - Statistical significance testing
    - Regional performance comparison
    - Business context awareness
    - Festival season adjustments
    - Mobile network variations
    - Auto-remediation suggestions
    """
    
    def __init__(self, service_name: str, region: str = "india"):
        self.service_name = service_name
        self.region = region
        self.current_time = datetime.now()
        
        # Data storage
        self.performance_data = defaultdict(lambda: deque(maxlen=50000))  # 50k samples per metric
        self.baselines = {}  # metric_key -> BaselinePeriod
        self.detected_regressions = deque(maxlen=10000)  # Recent regressions
        
        # Configuration
        self.detection_config = self._initialize_detection_config()
        self.indian_context = self._initialize_indian_context()
        self.business_rules = self._initialize_business_rules()
        
        # Statistical models
        self.statistical_models = self._initialize_statistical_models()
        
        # Logger
        self.logger = structlog.get_logger("indian-performance-regression")
        
    def _initialize_detection_config(self) -> Dict[str, Any]:
        """Initialize detection configuration"""
        
        return {
            "baseline_requirements": {
                "minimum_samples": 1000,        # Min 1000 samples for baseline
                "baseline_duration_hours": 168,  # 7 days baseline period
                "baseline_stability_threshold": 0.15,  # 15% CV threshold
                "confidence_level": 0.95,       # 95% confidence
                "refresh_interval_hours": 24    # Refresh baseline every 24h
            },
            
            "detection_thresholds": {
                "critical_degradation_percent": 50,    # 50%+ degradation
                "high_degradation_percent": 25,        # 25%+ degradation
                "medium_degradation_percent": 10,      # 10%+ degradation
                "low_degradation_percent": 5,          # 5%+ degradation
                "statistical_significance_threshold": 0.05  # p-value < 0.05
            },
            
            "detection_methods": {
                "primary": DetectionMethod.T_TEST,
                "secondary": [DetectionMethod.Z_SCORE, DetectionMethod.PERCENTAGE_CHANGE],
                "non_parametric": DetectionMethod.MANN_WHITNEY,
                "change_detection": DetectionMethod.CHANGEPOINT
            },
            
            "sampling_config": {
                "measurement_interval_seconds": 60,    # 1 minute intervals
                "aggregation_window_minutes": 5,      # 5-minute aggregations
                "retention_days": 30,                 # 30 days data retention
                "outlier_removal": True,              # Remove statistical outliers
                "outlier_threshold_sigma": 3          # 3-sigma outlier detection
            }
        }
        
    def _initialize_indian_context(self) -> Dict[str, Any]:
        """Initialize Indian market context"""
        
        return {
            "regional_variations": {
                "mumbai": {"network_quality": 0.9, "device_capability": 0.8, "peak_hours": ["09-12", "18-22"]},
                "bangalore": {"network_quality": 0.95, "device_capability": 0.9, "peak_hours": ["08-11", "17-21"]},
                "delhi": {"network_quality": 0.85, "device_capability": 0.75, "peak_hours": ["09-12", "19-23"]},
                "tier2_cities": {"network_quality": 0.7, "device_capability": 0.6, "peak_hours": ["18-21"]},
                "tier3_cities": {"network_quality": 0.5, "device_capability": 0.4, "peak_hours": ["19-21"]}
            },
            
            "festival_adjustments": {
                "diwali": {"expected_degradation": 0.3, "duration_days": 5},
                "holi": {"expected_degradation": 0.2, "duration_days": 2},
                "eid": {"expected_degradation": 0.25, "duration_days": 3},
                "new_year": {"expected_degradation": 0.4, "duration_days": 2},
                "big_billion_days": {"expected_degradation": 0.5, "duration_days": 8}
            },
            
            "device_segments": {
                "flagship": {"performance_expectation": 1.0, "market_share": 0.15},
                "premium": {"performance_expectation": 0.8, "market_share": 0.25},
                "mid_range": {"performance_expectation": 0.6, "market_share": 0.45},
                "budget": {"performance_expectation": 0.4, "market_share": 0.15}
            },
            
            "network_conditions": {
                "4g": {"latency_factor": 1.0, "reliability": 0.9},
                "3g": {"latency_factor": 2.5, "reliability": 0.7},
                "2g": {"latency_factor": 10.0, "reliability": 0.5},
                "wifi": {"latency_factor": 0.5, "reliability": 0.95}
            }
        }
        
    def _initialize_business_rules(self) -> Dict[str, Dict]:
        """Initialize business impact rules"""
        
        return {
            "payment_performance": {
                "critical_threshold_ms": 5000,    # 5s payment timeout is critical
                "revenue_impact_per_ms": 10,      # ₹10 revenue impact per ms delay
                "user_abandonment_rate": 0.05,   # 5% abandon for each second delay
                "business_criticality": "critical"
            },
            
            "search_performance": {
                "critical_threshold_ms": 2000,    # 2s search timeout
                "conversion_impact_per_ms": 0.001, # 0.1% conversion drop per ms
                "user_abandonment_rate": 0.02,
                "business_criticality": "high"
            },
            
            "page_load_performance": {
                "critical_threshold_ms": 3000,    # 3s page load timeout
                "bounce_rate_increase": 0.03,     # 3% bounce rate increase per second
                "seo_impact": True,               # Affects SEO rankings
                "business_criticality": "medium"
            },
            
            "delivery_performance": {
                "critical_threshold_minutes": 60, # 60 min delivery SLA
                "customer_satisfaction_impact": 0.1, # 10% satisfaction drop per 10 min delay
                "refund_rate_increase": 0.05,     # 5% refund increase per 15 min delay
                "business_criticality": "high"
            }
        }
        
    def _initialize_statistical_models(self) -> Dict[str, Any]:
        """Initialize statistical detection models"""
        
        return {
            "change_point_detection": {
                "algorithm": "cumulative_sum",
                "sensitivity": 0.5,
                "minimum_change_magnitude": 0.1
            },
            
            "anomaly_detection": {
                "method": "isolation_forest",
                "contamination": 0.1,  # 10% anomaly rate expected
                "seasonal_adjustment": True
            },
            
            "trend_analysis": {
                "window_size": 168,    # 7 days
                "trend_threshold": 0.05, # 5% trend significance
                "seasonal_periods": [24, 168]  # Hourly, weekly patterns
            }
        }
        
    def record_performance_measurement(self, measurement: PerformanceSnapshot):
        """Record a performance measurement"""
        
        # Create storage key
        key = f"{measurement.service}_{measurement.region}_{measurement.metric_name}"
        
        # Store measurement
        self.performance_data[key].append(measurement)
        
        # Check if we need to update baseline
        if self._should_refresh_baseline(key):
            self._update_baseline(key)
        
        # Check for regressions
        regression = self._detect_regression(measurement)
        
        if regression:
            self.detected_regressions.append(regression)
            
            # Log regression detection
            self.logger.warning(
                "performance_regression_detected",
                regression_id=regression.regression_id,
                service=regression.service,
                metric=regression.metric_name,
                severity=regression.severity.value,
                percentage_change=regression.percentage_change
            )
        
        # Log measurement
        self.logger.debug(
            "performance_measurement_recorded",
            service=measurement.service,
            metric=measurement.metric_name,
            value=measurement.value,
            region=measurement.region
        )
        
    def _should_refresh_baseline(self, key: str) -> bool:
        """Check if baseline should be refreshed"""
        
        if key not in self.baselines:
            return True
            
        baseline = self.baselines[key]
        hours_since_refresh = (datetime.now() - baseline.end_time).total_seconds() / 3600
        
        return hours_since_refresh >= self.detection_config["baseline_requirements"]["refresh_interval_hours"]
        
    def _update_baseline(self, key: str):
        """Update performance baseline for metric"""
        
        # Get recent data for baseline
        measurements = list(self.performance_data[key])
        
        if len(measurements) < self.detection_config["baseline_requirements"]["minimum_samples"]:
            self.logger.info(f"Insufficient data for baseline: {key} ({len(measurements)} samples)")
            return
        
        # Extract baseline period (exclude most recent data to avoid including regressions)
        baseline_cutoff = datetime.now() - timedelta(hours=24)  # Exclude last 24 hours
        baseline_measurements = [
            m for m in measurements 
            if m.timestamp <= baseline_cutoff
        ][-self.detection_config["baseline_requirements"]["minimum_samples"]:]
        
        if len(baseline_measurements) < self.detection_config["baseline_requirements"]["minimum_samples"]:
            return
        
        # Calculate baseline statistics
        values = [m.value for m in baseline_measurements]
        
        mean_value = np.mean(values)
        std_deviation = np.std(values)
        
        # Check for baseline stability (coefficient of variation)
        cv = std_deviation / mean_value if mean_value > 0 else float('inf')
        stability_threshold = self.detection_config["baseline_requirements"]["baseline_stability_threshold"]
        
        if cv > stability_threshold:
            self.logger.warning(
                f"Baseline unstable for {key}: CV={cv:.3f} > {stability_threshold}"
            )
            return
        
        # Calculate percentiles
        percentiles = {
            "p50": np.percentile(values, 50),
            "p75": np.percentile(values, 75),
            "p90": np.percentile(values, 90),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99)
        }
        
        # Calculate confidence interval
        confidence_level = self.detection_config["baseline_requirements"]["confidence_level"]
        alpha = 1 - confidence_level
        sem = stats.sem(values)  # Standard error of mean
        confidence_interval = stats.t.interval(
            confidence_level, len(values)-1, loc=mean_value, scale=sem
        )
        
        # Create baseline
        baseline = BaselinePeriod(
            start_time=baseline_measurements[0].timestamp,
            end_time=baseline_measurements[-1].timestamp,
            metric_name=baseline_measurements[0].metric_name,
            service=baseline_measurements[0].service,
            region=baseline_measurements[0].region,
            sample_count=len(baseline_measurements),
            mean_value=mean_value,
            std_deviation=std_deviation,
            percentiles=percentiles,
            confidence_interval=confidence_interval
        )
        
        self.baselines[key] = baseline
        
        self.logger.info(
            "baseline_updated",
            key=key,
            mean_value=mean_value,
            std_deviation=std_deviation,
            sample_count=len(baseline_measurements),
            cv=cv
        )
        
    def _detect_regression(self, measurement: PerformanceSnapshot) -> Optional[PerformanceRegression]:
        """Detect performance regression using statistical methods"""
        
        key = f"{measurement.service}_{measurement.region}_{measurement.metric_name}"
        
        if key not in self.baselines:
            return None  # No baseline available
            
        baseline = self.baselines[key]
        
        # Get recent measurements for comparison
        recent_measurements = [
            m for m in list(self.performance_data[key])[-100:]  # Last 100 measurements
            if (measurement.timestamp - m.timestamp).total_seconds() <= 3600  # Last hour
        ]
        
        if len(recent_measurements) < 10:  # Need minimum samples
            return None
            
        recent_values = [m.value for m in recent_measurements]
        current_mean = np.mean(recent_values)
        
        # Apply business context adjustments
        adjusted_baseline = self._adjust_baseline_for_context(baseline, measurement)
        
        # Detect regression using multiple methods
        detection_results = {}
        
        # Method 1: Percentage change
        percentage_change = ((current_mean - adjusted_baseline.mean_value) / adjusted_baseline.mean_value) * 100
        detection_results["percentage_change"] = {
            "significant": abs(percentage_change) >= self.detection_config["detection_thresholds"]["low_degradation_percent"],
            "value": percentage_change
        }
        
        # Method 2: T-test
        baseline_values = self._get_baseline_values(key)
        if baseline_values:
            t_stat, p_value = stats.ttest_ind(recent_values, baseline_values)
            detection_results["t_test"] = {
                "significant": p_value < self.detection_config["detection_thresholds"]["statistical_significance_threshold"],
                "p_value": p_value,
                "t_statistic": t_stat
            }
        
        # Method 3: Z-score
        z_score = (current_mean - adjusted_baseline.mean_value) / adjusted_baseline.std_deviation
        detection_results["z_score"] = {
            "significant": abs(z_score) > 2.0,  # 2-sigma threshold
            "value": z_score
        }
        
        # Determine if regression is detected
        primary_method = self.detection_config["detection_methods"]["primary"]
        is_regression = False
        statistical_significance = 1.0
        
        if primary_method == DetectionMethod.T_TEST and "t_test" in detection_results:
            is_regression = detection_results["t_test"]["significant"]
            statistical_significance = detection_results["t_test"]["p_value"]
        elif primary_method == DetectionMethod.PERCENTAGE_CHANGE:
            is_regression = detection_results["percentage_change"]["significant"] and percentage_change > 0
            statistical_significance = 0.05 if is_regression else 0.5
        
        if not is_regression:
            return None
            
        # Determine severity
        severity = self._determine_regression_severity(abs(percentage_change))
        
        # Calculate business impact
        business_impact = self._calculate_business_impact(measurement.metric_name, percentage_change, measurement)
        
        # Generate root cause candidates
        root_cause_candidates = self._generate_root_cause_candidates(measurement, percentage_change)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(measurement.metric_name, severity, percentage_change)
        
        # Calculate false positive probability
        false_positive_prob = self._estimate_false_positive_probability(
            detection_results, baseline, recent_values
        )
        
        # Create regression object
        regression = PerformanceRegression(
            regression_id=f"REG_{int(time.time())}_{random.randint(1000, 9999)}",
            detection_time=measurement.timestamp,
            metric_name=measurement.metric_name,
            service=measurement.service,
            region=measurement.region,
            severity=severity,
            detection_method=primary_method,
            baseline_value=adjusted_baseline.mean_value,
            current_value=current_mean,
            percentage_change=percentage_change,
            statistical_significance=statistical_significance,
            confidence_level=self.detection_config["baseline_requirements"]["confidence_level"],
            business_impact=business_impact,
            root_cause_candidates=root_cause_candidates,
            recommended_actions=recommended_actions,
            false_positive_probability=false_positive_prob
        )
        
        return regression
        
    def _adjust_baseline_for_context(self, baseline: BaselinePeriod, 
                                   measurement: PerformanceSnapshot) -> BaselinePeriod:
        """Adjust baseline for Indian business context"""
        
        adjusted_baseline = baseline
        
        # Festival adjustments
        if self._is_festival_period(measurement.timestamp):
            festival_name = self._get_current_festival(measurement.timestamp)
            if festival_name in self.indian_context["festival_adjustments"]:
                expected_degradation = self.indian_context["festival_adjustments"][festival_name]["expected_degradation"]
                
                # Adjust baseline expectation
                adjusted_mean = baseline.mean_value * (1 + expected_degradation)
                adjusted_baseline = BaselinePeriod(
                    start_time=baseline.start_time,
                    end_time=baseline.end_time,
                    metric_name=baseline.metric_name,
                    service=baseline.service,
                    region=baseline.region,
                    sample_count=baseline.sample_count,
                    mean_value=adjusted_mean,
                    std_deviation=baseline.std_deviation * (1 + expected_degradation * 0.5),
                    percentiles=baseline.percentiles,
                    confidence_interval=baseline.confidence_interval
                )
        
        # Regional adjustments
        if measurement.region in self.indian_context["regional_variations"]:
            regional_config = self.indian_context["regional_variations"][measurement.region]
            
            # Adjust for network quality
            network_factor = 1 / regional_config["network_quality"]  # Lower quality = higher expected latency
            
            adjusted_baseline.mean_value *= network_factor
            adjusted_baseline.std_deviation *= network_factor
        
        return adjusted_baseline
        
    def _determine_regression_severity(self, percentage_change: float) -> RegressionSeverity:
        """Determine regression severity based on percentage change"""
        
        thresholds = self.detection_config["detection_thresholds"]
        
        if percentage_change >= thresholds["critical_degradation_percent"]:
            return RegressionSeverity.CRITICAL
        elif percentage_change >= thresholds["high_degradation_percent"]:
            return RegressionSeverity.HIGH
        elif percentage_change >= thresholds["medium_degradation_percent"]:
            return RegressionSeverity.MEDIUM
        elif percentage_change >= thresholds["low_degradation_percent"]:
            return RegressionSeverity.LOW
        else:
            return RegressionSeverity.INFO
            
    def _calculate_business_impact(self, metric_name: str, percentage_change: float, 
                                 measurement: PerformanceSnapshot) -> Dict[str, Any]:
        """Calculate business impact of performance regression"""
        
        impact = {
            "estimated_revenue_loss_inr": 0,
            "estimated_user_impact": 0,
            "conversion_rate_impact": 0,
            "customer_satisfaction_impact": 0,
            "brand_impact": "minimal"
        }
        
        # Map metric to business rules
        business_rule_key = None
        if "payment" in metric_name.lower():
            business_rule_key = "payment_performance"
        elif "search" in metric_name.lower():
            business_rule_key = "search_performance"
        elif "page_load" in metric_name.lower():
            business_rule_key = "page_load_performance"
        elif "delivery" in metric_name.lower():
            business_rule_key = "delivery_performance"
            
        if business_rule_key and business_rule_key in self.business_rules:
            rule = self.business_rules[business_rule_key]
            
            # Calculate revenue impact
            if "revenue_impact_per_ms" in rule:
                degradation_ms = (measurement.value * percentage_change / 100)
                daily_transactions = 100000  # Estimate
                impact["estimated_revenue_loss_inr"] = degradation_ms * rule["revenue_impact_per_ms"] * daily_transactions
                
            # Calculate user impact
            if "user_abandonment_rate" in rule:
                abandonment_increase = percentage_change * rule["user_abandonment_rate"]
                impact["estimated_user_impact"] = abandonment_increase
                
            # Determine brand impact
            if percentage_change > 50:
                impact["brand_impact"] = "severe"
            elif percentage_change > 25:
                impact["brand_impact"] = "moderate"
            elif percentage_change > 10:
                impact["brand_impact"] = "minor"
        
        return impact
        
    def _generate_root_cause_candidates(self, measurement: PerformanceSnapshot, 
                                      percentage_change: float) -> List[str]:
        """Generate potential root cause candidates"""
        
        candidates = []
        
        # Common root causes based on metric type
        if "api_response" in measurement.metric_name:
            candidates.extend([
                "Database query performance degradation",
                "Increased traffic load",
                "Network connectivity issues",
                "Memory leak in application",
                "Third-party service latency"
            ])
            
        elif "page_load" in measurement.metric_name:
            candidates.extend([
                "Large JavaScript bundle size",
                "Unoptimized images",
                "CDN performance issues",
                "Browser compatibility issues",
                "Third-party script delays"
            ])
            
        elif "payment" in measurement.metric_name:
            candidates.extend([
                "Payment gateway latency",
                "Bank server performance issues",
                "Network timeout configurations",
                "Authentication service delays",
                "Fraud detection system overhead"
            ])
            
        elif "delivery" in measurement.metric_name:
            candidates.extend([
                "Driver allocation algorithm changes",
                "Traffic congestion patterns",
                "Restaurant preparation delays",
                "GPS tracking accuracy issues",
                "Logistics partner performance"
            ])
        
        # Context-specific candidates
        if measurement.region in ["tier2_cities", "tier3_cities"]:
            candidates.append("Poor network infrastructure in tier-2/3 cities")
            
        if self._is_festival_period(measurement.timestamp):
            candidates.append("Festival season traffic spike overwhelming infrastructure")
            
        # Severity-specific candidates
        if percentage_change > 50:
            candidates.extend([
                "Critical system component failure",
                "Database connection pool exhaustion",
                "Memory exhaustion causing GC pressure",
                "Network partition or connectivity loss"
            ])
        
        return candidates
        
    def _generate_recommended_actions(self, metric_name: str, severity: RegressionSeverity, 
                                    percentage_change: float) -> List[str]:
        """Generate recommended actions for regression"""
        
        actions = []
        
        # Severity-based immediate actions
        if severity == RegressionSeverity.CRITICAL:
            actions.extend([
                "IMMEDIATE: Escalate to on-call engineer",
                "Consider rolling back recent deployments",
                "Scale up infrastructure resources temporarily",
                "Enable circuit breakers for downstream dependencies"
            ])
            
        elif severity == RegressionSeverity.HIGH:
            actions.extend([
                "Alert development team within 30 minutes",
                "Review recent code deployments for issues",
                "Check system resource utilization",
                "Analyze error logs for anomalies"
            ])
            
        elif severity == RegressionSeverity.MEDIUM:
            actions.extend([
                "Schedule investigation within 2 hours",
                "Run performance profiling on affected services",
                "Check for configuration changes",
                "Review third-party service SLAs"
            ])
        
        # Metric-specific actions
        if "api_response" in metric_name:
            actions.extend([
                "Analyze database query execution plans",
                "Review API endpoint caching strategies",
                "Check connection pool configurations",
                "Profile CPU and memory usage patterns"
            ])
            
        elif "payment" in metric_name:
            actions.extend([
                "Contact payment gateway support team",
                "Review payment timeout configurations",
                "Analyze payment method success rates",
                "Check fraud detection rule impacts"
            ])
            
        elif "delivery" in metric_name:
            actions.extend([
                "Review driver assignment algorithms",
                "Check traffic data integration",
                "Analyze restaurant partner performance",
                "Verify GPS tracking accuracy"
            ])
        
        # Regional actions
        actions.append("Compare performance across different regions")
        actions.append("Implement feature flags for gradual rollback if needed")
        
        return actions
        
    def _estimate_false_positive_probability(self, detection_results: Dict, 
                                           baseline: BaselinePeriod, 
                                           recent_values: List[float]) -> float:
        """Estimate probability that detection is a false positive"""
        
        # Start with statistical significance
        base_fp_prob = detection_results.get("t_test", {}).get("p_value", 0.1)
        
        # Adjust based on baseline stability
        cv = baseline.std_deviation / baseline.mean_value if baseline.mean_value > 0 else 1.0
        if cv > 0.2:  # High baseline variability
            base_fp_prob *= 1.5
            
        # Adjust based on sample size
        sample_size = len(recent_values)
        if sample_size < 30:  # Small sample size
            base_fp_prob *= 1.3
            
        # Adjust based on business context
        if self._is_festival_period(datetime.now()):
            base_fp_prob *= 1.2  # Higher FP rate during festivals
            
        return min(1.0, base_fp_prob)  # Cap at 100%
        
    def _get_baseline_values(self, key: str) -> Optional[List[float]]:
        """Get baseline values for statistical comparison"""
        
        if key not in self.baselines:
            return None
            
        baseline = self.baselines[key]
        
        # Get measurements from baseline period
        measurements = [
            m for m in list(self.performance_data[key])
            if baseline.start_time <= m.timestamp <= baseline.end_time
        ]
        
        return [m.value for m in measurements]
        
    def _is_festival_period(self, timestamp: datetime) -> bool:
        """Check if timestamp falls during Indian festival period"""
        
        # Simplified festival detection (in production, use proper calendar)
        month = timestamp.month
        day = timestamp.day
        
        # Diwali season (October-November)
        if month in [10, 11]:
            return True
            
        # Holi season (March)
        if month == 3 and 15 <= day <= 25:
            return True
            
        # New Year
        if month == 1 and day <= 2:
            return True
        if month == 12 and day >= 30:
            return True
            
        return False
        
    def _get_current_festival(self, timestamp: datetime) -> Optional[str]:
        """Get current festival name if in festival period"""
        
        month = timestamp.month
        day = timestamp.day
        
        if month in [10, 11]:
            return "diwali"
        elif month == 3 and 15 <= day <= 25:
            return "holi"
        elif (month == 1 and day <= 2) or (month == 12 and day >= 30):
            return "new_year"
            
        return None
        
    def get_performance_regression_report(self, hours_lookback: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance regression report"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours_lookback)
        recent_regressions = [r for r in self.detected_regressions if r.detection_time >= cutoff_time]
        
        report = {
            "service_name": self.service_name,
            "region": self.region,
            "report_period": {
                "start_time": cutoff_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "hours_analyzed": hours_lookback
            },
            "regression_summary": self._get_regression_summary(recent_regressions),
            "severity_breakdown": self._get_severity_breakdown(recent_regressions),
            "metric_performance": self._get_metric_performance_summary(),
            "business_impact_analysis": self._get_business_impact_analysis(recent_regressions),
            "root_cause_analysis": self._get_root_cause_analysis(recent_regressions),
            "baseline_health": self._get_baseline_health_summary(),
            "recommendations": self._get_report_recommendations(recent_regressions),
            "false_positive_analysis": self._get_false_positive_analysis(recent_regressions)
        }
        
        return report
        
    def _get_regression_summary(self, regressions: List[PerformanceRegression]) -> Dict[str, Any]:
        """Get regression summary statistics"""
        
        if not regressions:
            return {"total_regressions": 0}
            
        return {
            "total_regressions": len(regressions),
            "unique_services_affected": len(set(r.service for r in regressions)),
            "unique_metrics_affected": len(set(r.metric_name for r in regressions)),
            "avg_degradation_percentage": np.mean([abs(r.percentage_change) for r in regressions]),
            "max_degradation_percentage": max([abs(r.percentage_change) for r in regressions]),
            "detection_methods_used": list(set(r.detection_method.value for r in regressions)),
            "avg_statistical_significance": np.mean([r.statistical_significance for r in regressions])
        }
        
    def _get_severity_breakdown(self, regressions: List[PerformanceRegression]) -> Dict[str, int]:
        """Get breakdown by severity"""
        
        severity_counts = defaultdict(int)
        for regression in regressions:
            severity_counts[regression.severity.value] += 1
            
        return dict(severity_counts)
        
    def _get_metric_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all metrics"""
        
        metric_summary = {}
        
        for key, baseline in self.baselines.items():
            recent_measurements = list(self.performance_data[key])[-100:]  # Last 100 measurements
            
            if recent_measurements:
                recent_values = [m.value for m in recent_measurements]
                current_mean = np.mean(recent_values)
                
                metric_summary[key] = {
                    "baseline_value": baseline.mean_value,
                    "current_value": current_mean,
                    "percentage_change": ((current_mean - baseline.mean_value) / baseline.mean_value) * 100,
                    "sample_count": len(recent_measurements),
                    "last_measurement": recent_measurements[-1].timestamp.isoformat()
                }
                
        return metric_summary
        
    def _get_business_impact_analysis(self, regressions: List[PerformanceRegression]) -> Dict[str, Any]:
        """Analyze total business impact"""
        
        total_revenue_impact = 0
        total_user_impact = 0
        
        for regression in regressions:
            business_impact = regression.business_impact
            total_revenue_impact += business_impact.get("estimated_revenue_loss_inr", 0)
            total_user_impact += business_impact.get("estimated_user_impact", 0)
            
        return {
            "total_estimated_revenue_loss_inr": total_revenue_impact,
            "total_estimated_user_impact_percentage": total_user_impact,
            "services_with_severe_brand_impact": len([
                r for r in regressions 
                if r.business_impact.get("brand_impact") == "severe"
            ]),
            "critical_business_functions_affected": len([
                r for r in regressions 
                if r.severity in [RegressionSeverity.CRITICAL, RegressionSeverity.HIGH]
            ])
        }
        
    def _get_root_cause_analysis(self, regressions: List[PerformanceRegression]) -> Dict[str, int]:
        """Analyze common root causes"""
        
        root_cause_counts = defaultdict(int)
        
        for regression in regressions:
            for cause in regression.root_cause_candidates:
                root_cause_counts[cause] += 1
                
        return dict(sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True))
        
    def _get_baseline_health_summary(self) -> Dict[str, Any]:
        """Get baseline health summary"""
        
        total_baselines = len(self.baselines)
        healthy_baselines = 0
        
        for key, baseline in self.baselines.items():
            cv = baseline.std_deviation / baseline.mean_value if baseline.mean_value > 0 else 1.0
            if cv <= 0.15:  # Stable baseline
                healthy_baselines += 1
                
        return {
            "total_baselines": total_baselines,
            "healthy_baselines": healthy_baselines,
            "baseline_health_percentage": (healthy_baselines / total_baselines) * 100 if total_baselines > 0 else 0,
            "baselines_requiring_refresh": total_baselines - healthy_baselines,
            "oldest_baseline_age_hours": self._get_oldest_baseline_age_hours()
        }
        
    def _get_oldest_baseline_age_hours(self) -> float:
        """Get age of oldest baseline in hours"""
        
        if not self.baselines:
            return 0
            
        oldest_baseline = min(self.baselines.values(), key=lambda b: b.end_time)
        return (datetime.now() - oldest_baseline.end_time).total_seconds() / 3600
        
    def _get_report_recommendations(self, regressions: List[PerformanceRegression]) -> List[str]:
        """Get report-level recommendations"""
        
        recommendations = []
        
        critical_regressions = [r for r in regressions if r.severity == RegressionSeverity.CRITICAL]
        
        if len(critical_regressions) > 0:
            recommendations.append(
                f"{len(critical_regressions)} critical performance regressions detected. "
                "Immediate escalation and remediation required."
            )
            
        if len(regressions) > 10:
            recommendations.append(
                f"{len(regressions)} regressions in 24 hours indicates systemic issues. "
                "Review recent deployments and infrastructure changes."
            )
            
        # Festival-specific recommendations
        if self._is_festival_period(datetime.now()):
            recommendations.append(
                "Festival season performance degradation expected. "
                "Adjust baselines and thresholds accordingly."
            )
            
        # False positive recommendations
        high_fp_regressions = [r for r in regressions if r.false_positive_probability > 0.3]
        
        if len(high_fp_regressions) > len(regressions) * 0.5:
            recommendations.append(
                "High false positive rate detected. "
                "Review detection thresholds and baseline stability."
            )
            
        return recommendations
        
    def _get_false_positive_analysis(self, regressions: List[PerformanceRegression]) -> Dict[str, Any]:
        """Analyze false positive rates"""
        
        if not regressions:
            return {"estimated_false_positive_rate": 0}
            
        avg_fp_probability = np.mean([r.false_positive_probability for r in regressions])
        high_confidence_regressions = len([r for r in regressions if r.false_positive_probability < 0.1])
        
        return {
            "estimated_false_positive_rate": avg_fp_probability * 100,
            "high_confidence_detections": high_confidence_regressions,
            "total_detections": len(regressions),
            "confidence_percentage": (high_confidence_regressions / len(regressions)) * 100
        }

# Test and simulation functions
async def simulate_swiggy_delivery_regression():
    """Simulate Swiggy delivery time regression detection"""
    print("🍔 Simulating Swiggy delivery time regression detection...")
    
    detector = IndianPerformanceRegressionDetector("swiggy-delivery", "mumbai")
    
    # Simulate normal delivery times for baseline
    print("📊 Establishing baseline with normal delivery times...")
    
    base_delivery_time = 25.0  # 25 minutes average
    
    for i in range(1500):  # Build good baseline
        # Add some natural variation
        delivery_time = base_delivery_time + random.gauss(0, 3)  # ±3 min standard deviation
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=1500-i),
            metric_name="delivery_time",
            value=max(10, delivery_time),  # Minimum 10 minutes
            unit="minutes",
            service="delivery",
            region="mumbai",
            device_type="android",
            business_context={"meal_type": "lunch", "restaurant_type": "fast_food"}
        )
        
        detector.record_performance_measurement(measurement)
    
    print(f"✅ Baseline established with {len(detector.baselines)} baselines")
    
    # Simulate gradual regression (kitchen delays during dinner rush)
    print("\n🔄 Simulating gradual performance regression...")
    
    regression_factor = 1.0
    detected_regressions = []
    
    for i in range(60):  # 60 measurements over time
        # Gradual degradation
        regression_factor += 0.02  # 2% degradation per measurement
        
        degraded_delivery_time = base_delivery_time * regression_factor + random.gauss(0, 4)
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=60-i),
            metric_name="delivery_time",
            value=max(10, degraded_delivery_time),
            unit="minutes",
            service="delivery",
            region="mumbai",
            device_type="android",
            business_context={"meal_type": "dinner", "restaurant_type": "casual_dining"}
        )
        
        detector.record_performance_measurement(measurement)
        
        # Check if regression was detected
        if detector.detected_regressions:
            latest_regression = detector.detected_regressions[-1]
            if latest_regression.regression_id not in [r.regression_id for r in detected_regressions]:
                detected_regressions.append(latest_regression)
                print(f"⚠️  Regression detected at measurement {i+1}:")
                print(f"   Severity: {latest_regression.severity.value}")
                print(f"   Degradation: {latest_regression.percentage_change:.1f}%")
                print(f"   Current value: {latest_regression.current_value:.1f} minutes")
    
    # Generate report
    print("\n📋 Generating performance regression report...")
    report = detector.get_performance_regression_report(2)  # Last 2 hours
    
    print(f"\n📊 Regression Analysis Summary:")
    summary = report['regression_summary']
    print(f"Total Regressions: {summary['total_regressions']}")
    print(f"Avg Degradation: {summary['avg_degradation_percentage']:.1f}%")
    print(f"Max Degradation: {summary['max_degradation_percentage']:.1f}%")
    
    print(f"\n💰 Business Impact:")
    business_impact = report['business_impact_analysis']
    print(f"Estimated Revenue Loss: ₹{business_impact['total_estimated_revenue_loss_inr']:,.0f}")
    print(f"User Impact: {business_impact['total_estimated_user_impact_percentage']:.1f}%")
    
    return detector, report

def test_payment_performance_regression():
    """Test payment performance regression detection"""
    print("\n💳 Testing payment performance regression detection...")
    
    detector = IndianPerformanceRegressionDetector("paytm-payments", "india")
    
    # Establish baseline for payment success rate
    base_success_rate = 99.2  # 99.2% success rate
    
    for i in range(1000):
        success_rate = base_success_rate + random.gauss(0, 0.3)  # Small variation
        success_rate = max(95, min(100, success_rate))  # Clamp between 95-100%
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=1000-i),
            metric_name="payment_success_rate", 
            value=success_rate,
            unit="percentage",
            service="payments",
            region="india",
            business_context={"payment_method": "upi", "amount_range": "small"}
        )
        
        detector.record_performance_measurement(measurement)
    
    print(f"✅ Payment baseline established")
    
    # Simulate payment gateway issues
    print("🚨 Simulating payment gateway degradation...")
    
    degraded_success_rate = 96.5  # Significant drop
    
    for i in range(20):
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=20-i),
            metric_name="payment_success_rate",
            value=degraded_success_rate + random.gauss(0, 0.5),
            unit="percentage",
            service="payments",
            region="india",
            business_context={"payment_method": "upi", "amount_range": "small"}
        )
        
        detector.record_performance_measurement(measurement)
    
    # Check for detection
    if detector.detected_regressions:
        latest_regression = detector.detected_regressions[-1]
        print(f"✅ Payment regression detected:")
        print(f"   Severity: {latest_regression.severity.value}")
        print(f"   Success rate drop: {abs(latest_regression.percentage_change):.2f}%")
        print(f"   Business impact: {latest_regression.business_impact}")
    else:
        print("❌ No regression detected")

def test_api_latency_regression():
    """Test API latency regression detection"""
    print("\n🌐 Testing API latency regression detection...")
    
    detector = IndianPerformanceRegressionDetector("flipkart-api", "bangalore")
    
    # Build baseline for API response times
    base_latency = 120  # 120ms average
    
    for i in range(800):
        latency = base_latency + random.exponential(30)  # Exponential tail
        latency = min(1000, latency)  # Cap at 1 second
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=800-i),
            metric_name="api_response_time",
            value=latency,
            unit="milliseconds", 
            service="web_api",
            region="bangalore",
            business_context={"endpoint": "/api/products", "user_type": "premium"}
        )
        
        detector.record_performance_measurement(measurement)
    
    print("✅ API latency baseline established")
    
    # Simulate database performance degradation
    print("⚠️ Simulating database performance impact on API...")
    
    for i in range(30):
        # Gradual degradation due to database issues
        degradation_factor = 1 + (i * 0.05)  # 5% degradation per measurement
        degraded_latency = base_latency * degradation_factor + random.exponential(50)
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(minutes=30-i),
            metric_name="api_response_time",
            value=min(2000, degraded_latency),
            unit="milliseconds",
            service="web_api", 
            region="bangalore",
            business_context={"endpoint": "/api/products", "user_type": "premium"}
        )
        
        detector.record_performance_measurement(measurement)
    
    # Check detection results
    recent_regressions = [r for r in detector.detected_regressions 
                         if r.metric_name == "api_response_time"]
    
    if recent_regressions:
        regression = recent_regressions[-1]
        print(f"✅ API latency regression detected:")
        print(f"   Latency increase: {regression.percentage_change:.1f}%") 
        print(f"   Baseline: {regression.baseline_value:.0f}ms")
        print(f"   Current: {regression.current_value:.0f}ms")
        print(f"   Root causes: {regression.root_cause_candidates[:2]}")
    else:
        print("❌ No latency regression detected")

async def test_festival_season_adjustments():
    """Test festival season baseline adjustments"""
    print("\n🎉 Testing festival season baseline adjustments...")
    
    detector = IndianPerformanceRegressionDetector("zomato-orders", "delhi")
    
    # Normal performance baseline
    base_order_time = 35  # 35 minutes average order processing
    
    # Build baseline
    for i in range(500):
        order_time = base_order_time + random.gauss(0, 5)
        
        measurement = PerformanceSnapshot(
            timestamp=datetime.now() - timedelta(days=20, minutes=i),  # 20 days ago
            metric_name="order_completion_time",
            value=max(15, order_time),
            unit="minutes",
            service="order_processing",
            region="delhi"
        )
        
        detector.record_performance_measurement(measurement)
    
    print("✅ Normal baseline established")
    
    # Simulate Diwali season performance (expected degradation)
    print("🪔 Simulating Diwali season performance...")
    
    # During Diwali, 30% degradation is expected
    diwali_order_time = base_order_time * 1.3  # 30% slower
    
    for i in range(100):
        order_time = diwali_order_time + random.gauss(0, 7)  # More variation during festival
        
        # Mock Diwali date
        diwali_timestamp = datetime(2024, 11, 1) + timedelta(minutes=i)
        
        measurement = PerformanceSnapshot(
            timestamp=diwali_timestamp,
            metric_name="order_completion_time", 
            value=max(15, order_time),
            unit="minutes",
            service="order_processing",
            region="delhi",
            business_context={"festival_season": "diwali"}
        )
        
        detector.record_performance_measurement(measurement)
    
    # Check if festival adjustment prevented false alarms
    festival_regressions = [r for r in detector.detected_regressions 
                           if "order_completion_time" in r.metric_name]
    
    print(f"📊 Festival adjustment results:")
    print(f"   Regressions detected during Diwali: {len(festival_regressions)}")
    print(f"   Expected: Few or none due to baseline adjustment")
    
    if festival_regressions:
        regression = festival_regressions[-1]
        print(f"   Latest detection severity: {regression.severity.value}")
        print(f"   Adjusted baseline applied: {regression.baseline_value:.1f} minutes")

if __name__ == "__main__":
    print("🚀 Episode 16: Performance Regression Detection System")
    print("🇮🇳 Swiggy se Flipkart tak, performance regression ko pakadna!")
    print("=" * 60)
    
    # Run comprehensive testing
    asyncio.run(simulate_swiggy_delivery_regression())
    test_payment_performance_regression()
    test_api_latency_regression()
    asyncio.run(test_festival_season_adjustments())
    
    print("\n" + "=" * 60)
    print("✅ Performance regression detection testing completed!")
    print("📊 Key Insights:")
    print("  - Statistical significance prevents false positives")
    print("  - Business context adjustments reduce alert noise")
    print("  - Multi-method detection increases accuracy")
    print("  - Festival season adjustments prevent false alarms")
    print("🔍 Next: Deploy regression detection in production monitoring")