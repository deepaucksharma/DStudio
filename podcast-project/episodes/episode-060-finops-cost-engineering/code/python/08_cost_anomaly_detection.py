#!/usr/bin/env python3
"""
Advanced Cost Anomaly Detection System
======================================

Hindi Tech Podcast Series - Episode 60: FinOps & Cost Engineering
Machine Learning-powered cost anomaly detection and root cause analysis

Author: Hindi Tech Community
Date: 2025
Version: 1.0

Features:
- ML-based anomaly detection using multiple algorithms
- Root cause analysis and drill-down capabilities
- Seasonal pattern recognition
- Real-time anomaly alerting
- Historical trend analysis
- Service-level anomaly attribution
- Automated investigation workflows

Mumbai Context: Cost anomaly detection जैसे electricity bill में sudden spike
- Normal usage vs abnormal usage detection
- Peak season vs off-season patterns
- Appliance-wise consumption analysis (service-wise cost breakdown)
"""

import asyncio
import boto3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import scipy.stats as stats
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    COST_SPIKE = "cost_spike"
    COST_DROP = "cost_drop"
    USAGE_ANOMALY = "usage_anomaly"
    SERVICE_ANOMALY = "service_anomaly"
    SEASONAL_DEVIATION = "seasonal_deviation"
    TREND_CHANGE = "trend_change"

class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    STATISTICAL = "statistical"
    ISOLATION_FOREST = "isolation_forest"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

@dataclass
class CostAnomaly:
    """Cost anomaly details"""
    anomaly_id: str
    detected_at: datetime
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    actual_cost: float
    expected_cost: float
    deviation_percentage: float
    confidence_score: float
    service: str
    region: str
    time_period: str
    root_causes: List[str]
    impact_assessment: Dict[str, Any]
    recommended_actions: List[str]

@dataclass
class ServiceMetrics:
    """Service-level metrics for anomaly detection"""
    service_name: str
    daily_costs: List[float]
    usage_metrics: List[float]
    request_counts: List[float]
    error_rates: List[float]
    dates: List[str]

class CostAnomalyDetector:
    """
    Advanced Cost Anomaly Detection System
    
    Mumbai Context: यह electricity meter monitoring जैसा है
    - Daily usage pattern tracking
    - Sudden spike detection (AC चालू कर दिया या कोई heavy appliance)
    - Seasonal adjustments (summer vs winter consumption)  
    - Appliance-wise analysis (कौन सा service ज्यादा cost कर रहा)
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize cost anomaly detection system"""
        try:
            self.region = region
            
            # AWS clients
            self.ce_client = boto3.client('ce', region_name=region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            self.sns_client = boto3.client('sns', region_name=region)
            
            # ML models and configuration
            self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
            self.scaler = StandardScaler()
            self.anomaly_history = []
            self.baseline_patterns = {}
            self.seasonal_patterns = {}
            
            # Detection thresholds
            self.thresholds = {
                'cost_spike_percentage': 25.0,  # 25% increase
                'cost_drop_percentage': 30.0,   # 30% decrease
                'z_score_threshold': 2.5,       # Statistical significance
                'isolation_score_threshold': -0.5,
                'confidence_threshold': 0.7
            }
            
            logger.info("Cost Anomaly Detection System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cost Anomaly Detection System: {e}")
            raise

    async def collect_cost_data(self, days_back: int = 30) -> pd.DataFrame:
        """
        Collect comprehensive cost data for analysis
        
        Mumbai Context: Historical electricity bill data collection
        - Last 6 months consumption patterns
        - Service-wise breakdown (lights, AC, fridge, etc.)
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get cost data with service breakdown
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            # Process data into structured format
            cost_data = []
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                
                if result['Groups']:
                    for group in result['Groups']:
                        service = group['Keys'][0] if group['Keys'] else 'Unknown'
                        region = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                        
                        cost = float(group['Metrics']['BlendedCost']['Amount'])
                        usage = float(group['Metrics']['UsageQuantity']['Amount'])
                        
                        cost_data.append({
                            'date': date,
                            'service': service,
                            'region': region,
                            'cost': cost,
                            'usage': usage
                        })
                else:
                    # No grouping, total cost
                    total_cost = float(result['Total']['BlendedCost']['Amount'])
                    total_usage = float(result['Total']['UsageQuantity']['Amount'])
                    
                    cost_data.append({
                        'date': date,
                        'service': 'Total',
                        'region': 'All',
                        'cost': total_cost,
                        'usage': total_usage
                    })
            
            df = pd.DataFrame(cost_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Add time-based features
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
            
            logger.info(f"Collected {len(df)} cost data points")
            return df
            
        except Exception as e:
            logger.error(f"Failed to collect cost data: {e}")
            return pd.DataFrame()

    def build_baseline_patterns(self, df: pd.DataFrame):
        """
        Build baseline patterns for normal cost behavior
        
        Mumbai Context: Normal electricity consumption pattern
        - Weekday vs weekend usage
        - Summer vs winter seasons
        - Daily pattern (morning, afternoon, evening peaks)
        """
        try:
            # Service-wise baseline patterns
            for service in df['service'].unique():
                service_data = df[df['service'] == service].copy()
                
                if len(service_data) < 7:  # Need at least a week of data
                    continue
                
                service_data = service_data.sort_values('date')
                
                # Calculate rolling statistics
                service_data['cost_ma_7'] = service_data['cost'].rolling(window=7).mean()
                service_data['cost_std_7'] = service_data['cost'].rolling(window=7).std()
                service_data['cost_percentile_25'] = service_data['cost'].rolling(window=14).quantile(0.25)
                service_data['cost_percentile_75'] = service_data['cost'].rolling(window=14).quantile(0.75)
                
                # Day-of-week patterns
                dow_pattern = service_data.groupby('day_of_week')['cost'].agg(['mean', 'std']).to_dict()
                
                # Monthly patterns (seasonal)
                monthly_pattern = service_data.groupby('month')['cost'].agg(['mean', 'std']).to_dict()
                
                # Store baseline pattern
                self.baseline_patterns[service] = {
                    'overall_mean': service_data['cost'].mean(),
                    'overall_std': service_data['cost'].std(),
                    'day_of_week_pattern': dow_pattern,
                    'monthly_pattern': monthly_pattern,
                    'percentile_25': service_data['cost'].quantile(0.25),
                    'percentile_75': service_data['cost'].quantile(0.75),
                    'iqr': service_data['cost'].quantile(0.75) - service_data['cost'].quantile(0.25)
                }
            
            logger.info(f"Built baseline patterns for {len(self.baseline_patterns)} services")
            
        except Exception as e:
            logger.error(f"Failed to build baseline patterns: {e}")

    def detect_statistical_anomalies(self, df: pd.DataFrame) -> List[CostAnomaly]:
        """
        Detect anomalies using statistical methods (Z-score, IQR)
        
        Mumbai Context: Statistical analysis जैसे electricity bill का month-over-month comparison
        """
        anomalies = []
        
        try:
            for service in df['service'].unique():
                service_data = df[df['service'] == service].copy()
                
                if len(service_data) < 10:  # Need sufficient data
                    continue
                
                service_data = service_data.sort_values('date')
                
                # Calculate Z-scores
                service_data['z_score'] = np.abs(stats.zscore(service_data['cost']))
                
                # Calculate IQR outliers
                Q1 = service_data['cost'].quantile(0.25)
                Q3 = service_data['cost'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                service_data['is_iqr_outlier'] = (
                    (service_data['cost'] < lower_bound) | 
                    (service_data['cost'] > upper_bound)
                )
                
                # Detect anomalies
                anomalous_points = service_data[
                    (service_data['z_score'] > self.thresholds['z_score_threshold']) |
                    (service_data['is_iqr_outlier'])
                ]
                
                for _, point in anomalous_points.iterrows():
                    # Determine anomaly type
                    mean_cost = service_data['cost'].mean()
                    anomaly_type = AnomalyType.COST_SPIKE if point['cost'] > mean_cost else AnomalyType.COST_DROP
                    
                    # Calculate deviation
                    deviation_pct = abs((point['cost'] - mean_cost) / mean_cost * 100) if mean_cost > 0 else 0
                    
                    # Determine severity
                    severity = self._determine_severity(deviation_pct, point['z_score'])
                    
                    # Generate root cause analysis
                    root_causes = self._analyze_root_causes(service, point, service_data)
                    
                    anomaly = CostAnomaly(
                        anomaly_id=f"stat-{service}-{point['date'].strftime('%Y%m%d')}",
                        detected_at=datetime.now(),
                        anomaly_type=anomaly_type,
                        severity=severity,
                        detection_method=DetectionMethod.STATISTICAL,
                        actual_cost=point['cost'],
                        expected_cost=mean_cost,
                        deviation_percentage=deviation_pct,
                        confidence_score=min(point['z_score'] / 5.0, 1.0),  # Normalize
                        service=service,
                        region=point['region'],
                        time_period=point['date'].strftime('%Y-%m-%d'),
                        root_causes=root_causes,
                        impact_assessment=self._assess_impact(point['cost'], mean_cost),
                        recommended_actions=self._get_recommendations(anomaly_type, service, deviation_pct)
                    )
                    
                    anomalies.append(anomaly)
            
            logger.info(f"Detected {len(anomalies)} statistical anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect statistical anomalies: {e}")
            return []

    def detect_ml_anomalies(self, df: pd.DataFrame) -> List[CostAnomaly]:
        """
        Detect anomalies using machine learning (Isolation Forest)
        
        Mumbai Context: ML-based pattern recognition जैसे smart meter analysis
        """
        anomalies = []
        
        try:
            for service in df['service'].unique():
                service_data = df[df['service'] == service].copy()
                
                if len(service_data) < 20:  # Need sufficient data for ML
                    continue
                
                # Prepare features for ML
                features = service_data[['cost', 'usage', 'day_of_week', 'day_of_month', 'month']].copy()
                
                # Handle missing values
                features = features.fillna(features.mean())
                
                # Scale features
                features_scaled = self.scaler.fit_transform(features)
                
                # Train Isolation Forest
                clf = IsolationForest(contamination=0.1, random_state=42)
                outlier_predictions = clf.fit_predict(features_scaled)
                outlier_scores = clf.decision_function(features_scaled)
                
                # Identify anomalies
                anomaly_indices = np.where(outlier_predictions == -1)[0]
                
                for idx in anomaly_indices:
                    point = service_data.iloc[idx]
                    score = outlier_scores[idx]
                    
                    if score < self.thresholds['isolation_score_threshold']:
                        # Calculate expected cost using recent average
                        recent_data = service_data[service_data['date'] < point['date']].tail(7)
                        expected_cost = recent_data['cost'].mean() if len(recent_data) > 0 else service_data['cost'].mean()
                        
                        deviation_pct = abs((point['cost'] - expected_cost) / expected_cost * 100) if expected_cost > 0 else 0
                        
                        anomaly_type = AnomalyType.COST_SPIKE if point['cost'] > expected_cost else AnomalyType.COST_DROP
                        severity = self._determine_severity(deviation_pct, abs(score))
                        
                        anomaly = CostAnomaly(
                            anomaly_id=f"ml-{service}-{point['date'].strftime('%Y%m%d')}",
                            detected_at=datetime.now(),
                            anomaly_type=anomaly_type,
                            severity=severity,
                            detection_method=DetectionMethod.ISOLATION_FOREST,
                            actual_cost=point['cost'],
                            expected_cost=expected_cost,
                            deviation_percentage=deviation_pct,
                            confidence_score=min(abs(score), 1.0),
                            service=service,
                            region=point['region'],
                            time_period=point['date'].strftime('%Y-%m-%d'),
                            root_causes=self._analyze_root_causes(service, point, service_data),
                            impact_assessment=self._assess_impact(point['cost'], expected_cost),
                            recommended_actions=self._get_recommendations(anomaly_type, service, deviation_pct)
                        )
                        
                        anomalies.append(anomaly)
            
            logger.info(f"Detected {len(anomalies)} ML-based anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect ML anomalies: {e}")
            return []

    def detect_time_series_anomalies(self, df: pd.DataFrame) -> List[CostAnomaly]:
        """
        Detect anomalies using time series analysis
        
        Mumbai Context: Time series patterns जैसे monthly electricity bill trends
        """
        anomalies = []
        
        try:
            for service in df['service'].unique():
                service_data = df[df['service'] == service].copy()
                
                if len(service_data) < 15:  # Need sufficient data for time series
                    continue
                
                service_data = service_data.sort_values('date')
                
                # Calculate moving averages and trends
                service_data['ma_7'] = service_data['cost'].rolling(window=7).mean()
                service_data['ma_14'] = service_data['cost'].rolling(window=14).mean()
                
                # Calculate rate of change
                service_data['cost_diff'] = service_data['cost'].diff()
                service_data['cost_pct_change'] = service_data['cost'].pct_change()
                
                # Detect sudden changes
                change_threshold = service_data['cost_pct_change'].std() * 2
                
                anomalous_changes = service_data[
                    abs(service_data['cost_pct_change']) > change_threshold
                ]
                
                for _, point in anomalous_changes.iterrows():
                    if pd.isna(point['ma_14']):
                        continue
                    
                    expected_cost = point['ma_14']
                    deviation_pct = abs((point['cost'] - expected_cost) / expected_cost * 100) if expected_cost > 0 else 0
                    
                    if deviation_pct > self.thresholds['cost_spike_percentage']:
                        anomaly_type = AnomalyType.TREND_CHANGE
                        severity = self._determine_severity(deviation_pct, abs(point['cost_pct_change']))
                        
                        anomaly = CostAnomaly(
                            anomaly_id=f"ts-{service}-{point['date'].strftime('%Y%m%d')}",
                            detected_at=datetime.now(),
                            anomaly_type=anomaly_type,
                            severity=severity,
                            detection_method=DetectionMethod.TIME_SERIES,
                            actual_cost=point['cost'],
                            expected_cost=expected_cost,
                            deviation_percentage=deviation_pct,
                            confidence_score=min(abs(point['cost_pct_change']) * 10, 1.0),
                            service=service,
                            region=point['region'],
                            time_period=point['date'].strftime('%Y-%m-%d'),
                            root_causes=self._analyze_trend_change_causes(service, point, service_data),
                            impact_assessment=self._assess_impact(point['cost'], expected_cost),
                            recommended_actions=self._get_recommendations(anomaly_type, service, deviation_pct)
                        )
                        
                        anomalies.append(anomaly)
            
            logger.info(f"Detected {len(anomalies)} time series anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect time series anomalies: {e}")
            return []

    def _determine_severity(self, deviation_pct: float, confidence_score: float) -> AnomalySeverity:
        """Determine anomaly severity based on deviation and confidence"""
        if deviation_pct > 100 and confidence_score > 3.0:
            return AnomalySeverity.CRITICAL
        elif deviation_pct > 50 and confidence_score > 2.0:
            return AnomalySeverity.HIGH
        elif deviation_pct > 25 and confidence_score > 1.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _analyze_root_causes(self, service: str, anomaly_point: pd.Series, service_data: pd.DataFrame) -> List[str]:
        """Analyze potential root causes for anomaly"""
        root_causes = []
        
        try:
            # Check if it's a weekend anomaly
            if anomaly_point['is_weekend']:
                root_causes.append("Weekend usage pattern deviation")
            
            # Check if it's month-end
            if anomaly_point['day_of_month'] > 25:
                root_causes.append("Month-end processing or batch jobs")
            
            # Check for usage vs cost correlation
            if anomaly_point['usage'] > 0:
                cost_per_unit = anomaly_point['cost'] / anomaly_point['usage']
                avg_cost_per_unit = (service_data['cost'] / service_data['usage']).mean()
                
                if cost_per_unit > avg_cost_per_unit * 1.5:
                    root_causes.append("Increased pricing or premium instance usage")
                elif anomaly_point['usage'] > service_data['usage'].quantile(0.9):
                    root_causes.append("Unusually high usage volume")
            
            # Service-specific root causes
            service_specific_causes = {
                'EC2': ['Instance type changes', 'Auto-scaling events', 'Reserved instance expiration'],
                'Lambda': ['Function timeout increases', 'High request volume', 'Memory allocation changes'],
                'RDS': ['Database scaling events', 'Backup operations', 'Read replica creation'],
                'S3': ['Data transfer spikes', 'Storage class changes', 'Large file uploads'],
                'CloudFront': ['Traffic spikes', 'Geographic distribution changes', 'Cache miss rates']
            }
            
            if service in service_specific_causes:
                root_causes.extend(service_specific_causes[service][:2])  # Add top 2 specific causes
            
            # Default causes if none identified
            if not root_causes:
                root_causes = ["Requires manual investigation", "Check resource scaling events"]
        
        except Exception as e:
            logger.warning(f"Failed to analyze root causes: {e}")
            root_causes = ["Root cause analysis failed"]
        
        return root_causes

    def _analyze_trend_change_causes(self, service: str, anomaly_point: pd.Series, service_data: pd.DataFrame) -> List[str]:
        """Analyze root causes for trend changes"""
        causes = []
        
        # Check for sustained increase/decrease
        recent_trend = service_data.tail(7)['cost'].mean()
        older_trend = service_data.head(7)['cost'].mean()
        
        if recent_trend > older_trend * 1.2:
            causes.append("Sustained cost increase trend detected")
        elif recent_trend < older_trend * 0.8:
            causes.append("Sustained cost decrease trend detected")
        
        causes.extend([
            "Check for infrastructure changes",
            "Review resource optimization actions",
            "Validate pricing model changes"
        ])
        
        return causes

    def _assess_impact(self, actual_cost: float, expected_cost: float) -> Dict[str, Any]:
        """Assess the impact of the anomaly"""
        cost_impact = actual_cost - expected_cost
        
        return {
            'cost_impact_daily': cost_impact,
            'cost_impact_monthly': cost_impact * 30,
            'cost_impact_annual': cost_impact * 365,
            'percentage_impact': (cost_impact / expected_cost * 100) if expected_cost > 0 else 0,
            'business_impact': self._classify_business_impact(abs(cost_impact))
        }

    def _classify_business_impact(self, cost_impact: float) -> str:
        """Classify business impact based on cost"""
        if cost_impact > 1000:
            return "HIGH - Significant budget impact"
        elif cost_impact > 100:
            return "MEDIUM - Moderate budget impact"
        elif cost_impact > 10:
            return "LOW - Minor budget impact"
        else:
            return "MINIMAL - Negligible impact"

    def _get_recommendations(self, anomaly_type: AnomalyType, service: str, deviation_pct: float) -> List[str]:
        """Get recommended actions for anomaly"""
        recommendations = []
        
        if anomaly_type == AnomalyType.COST_SPIKE:
            recommendations.extend([
                "🔍 Investigate resource scaling events",
                "📊 Review usage metrics for the time period", 
                "⚙️ Check for configuration changes",
                "💰 Consider implementing cost controls"
            ])
            
            if deviation_pct > 50:
                recommendations.insert(0, "🚨 URGENT: Immediate investigation required")
        
        elif anomaly_type == AnomalyType.COST_DROP:
            recommendations.extend([
                "✅ Verify if cost reduction is intentional",
                "🔍 Check for service outages or failures",
                "📈 Monitor for impact on application performance",
                "💡 Document optimization if beneficial"
            ])
        
        elif anomaly_type == AnomalyType.TREND_CHANGE:
            recommendations.extend([
                "📈 Analyze trend direction and sustainability",
                "🎯 Review resource optimization strategies",
                "📅 Plan budget adjustments if trend continues",
                "🔄 Consider automated scaling policies"
            ])
        
        # Service-specific recommendations
        service_recommendations = {
            'EC2': "Consider Reserved Instances or Spot Instances for predictable workloads",
            'Lambda': "Review function memory allocation and timeout settings",
            'RDS': "Analyze query performance and consider read replicas",
            'S3': "Review storage classes and lifecycle policies"
        }
        
        if service in service_recommendations:
            recommendations.append(f"🎯 {service}: {service_recommendations[service]}")
        
        return recommendations

    async def run_comprehensive_detection(self, days_back: int = 30) -> List[CostAnomaly]:
        """
        Run comprehensive anomaly detection using all methods
        
        Mumbai Context: Complete electricity audit जैसे professional energy audit
        """
        try:
            logger.info("Starting comprehensive cost anomaly detection...")
            
            # Collect data
            df = await self.collect_cost_data(days_back)
            if df.empty:
                logger.warning("No cost data available for anomaly detection")
                return []
            
            # Build baseline patterns
            self.build_baseline_patterns(df)
            
            # Run different detection methods
            statistical_anomalies = self.detect_statistical_anomalies(df)
            ml_anomalies = self.detect_ml_anomalies(df)
            ts_anomalies = self.detect_time_series_anomalies(df)
            
            # Combine and deduplicate anomalies
            all_anomalies = statistical_anomalies + ml_anomalies + ts_anomalies
            
            # Remove duplicates based on service, date, and similar deviation
            unique_anomalies = self._deduplicate_anomalies(all_anomalies)
            
            # Sort by severity and confidence
            unique_anomalies.sort(key=lambda x: (x.severity.value, -x.confidence_score), reverse=True)
            
            # Store in history
            self.anomaly_history.extend(unique_anomalies)
            
            logger.info(f"Detected {len(unique_anomalies)} unique cost anomalies")
            return unique_anomalies
            
        except Exception as e:
            logger.error(f"Failed to run comprehensive detection: {e}")
            return []

    def _deduplicate_anomalies(self, anomalies: List[CostAnomaly]) -> List[CostAnomaly]:
        """Remove duplicate anomalies"""
        unique_anomalies = []
        seen_combinations = set()
        
        for anomaly in anomalies:
            # Create unique key based on service, date, and approximate deviation
            key = (
                anomaly.service,
                anomaly.time_period,
                round(anomaly.deviation_percentage / 10) * 10  # Round to nearest 10%
            )
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies

    def generate_anomaly_report(self, anomalies: List[CostAnomaly]) -> str:
        """
        Generate comprehensive anomaly detection report
        
        Mumbai Context: Complete electricity audit report
        """
        try:
            report = f"""
Cost Anomaly Detection Report
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY (Mumbai Style)
===============================
यह report आपके cloud costs में abnormal patterns का complete analysis है
जैसे electricity bill में sudden spike या unexpected drop की investigation

Total Anomalies Detected: {len(anomalies)}
Critical Anomalies: {len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])}
High Priority Anomalies: {len([a for a in anomalies if a.severity == AnomalySeverity.HIGH])}

ANOMALY BREAKDOWN
================
"""
            
            if anomalies:
                # Group by severity
                anomalies_by_severity = {}
                total_cost_impact = 0
                
                for anomaly in anomalies:
                    if anomaly.severity not in anomalies_by_severity:
                        anomalies_by_severity[anomaly.severity] = []
                    anomalies_by_severity[anomaly.severity].append(anomaly)
                    total_cost_impact += anomaly.impact_assessment.get('cost_impact_daily', 0)
                
                # Severity breakdown
                for severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH, AnomalySeverity.MEDIUM, AnomalySeverity.LOW]:
                    if severity in anomalies_by_severity:
                        severity_anomalies = anomalies_by_severity[severity]
                        severity_impact = sum(a.impact_assessment.get('cost_impact_daily', 0) for a in severity_anomalies)
                        
                        emoji = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
                        report += f"""
{emoji.get(severity.value, '•')} {severity.value.upper()} Anomalies: {len(severity_anomalies)}
   Daily Cost Impact: ${severity_impact:.2f}
   Monthly Impact: ${severity_impact * 30:.2f}
"""
                
                # Top anomalies details
                report += f"""

TOP 10 CRITICAL ANOMALIES
========================
"""
                
                sorted_anomalies = sorted(anomalies, key=lambda x: (x.severity.value, -abs(x.impact_assessment.get('cost_impact_daily', 0))), reverse=True)
                
                for i, anomaly in enumerate(sorted_anomalies[:10], 1):
                    impact = anomaly.impact_assessment.get('cost_impact_daily', 0)
                    report += f"""
{i}. {anomaly.service} - {anomaly.time_period}
   Type: {anomaly.anomaly_type.value.replace('_', ' ').title()}
   Severity: {anomaly.severity.value.upper()}
   Method: {anomaly.detection_method.value.replace('_', ' ').title()}
   Actual Cost: ${anomaly.actual_cost:.2f}
   Expected Cost: ${anomaly.expected_cost:.2f}
   Deviation: {anomaly.deviation_percentage:.1f}%
   Daily Impact: ${impact:.2f}
   Confidence: {anomaly.confidence_score:.2f}
   
   Root Causes:
   {chr(10).join([f'   • {cause}' for cause in anomaly.root_causes[:3]])}
   
   Recommended Actions:
   {chr(10).join([f'   • {action}' for action in anomaly.recommended_actions[:3]])}
"""
                
                # Service-wise analysis
                service_anomalies = {}
                for anomaly in anomalies:
                    if anomaly.service not in service_anomalies:
                        service_anomalies[anomaly.service] = []
                    service_anomalies[anomaly.service].append(anomaly)
                
                report += f"""

SERVICE-WISE ANALYSIS
====================
"""
                
                for service, service_anomaly_list in sorted(service_anomalies.items(), key=lambda x: len(x[1]), reverse=True):
                    service_impact = sum(a.impact_assessment.get('cost_impact_daily', 0) for a in service_anomaly_list)
                    avg_deviation = sum(a.deviation_percentage for a in service_anomaly_list) / len(service_anomaly_list)
                    
                    report += f"""
{service} ({len(service_anomaly_list)} anomalies):
   Average Deviation: {avg_deviation:.1f}%
   Daily Impact: ${service_impact:.2f}
   Monthly Impact: ${service_impact * 30:.2f}
   Most Common Type: {max([a.anomaly_type.value for a in service_anomaly_list], key=[a.anomaly_type.value for a in service_anomaly_list].count)}
"""
                
                # Total impact summary
                monthly_impact = total_cost_impact * 30
                annual_impact = total_cost_impact * 365
                
                report += f"""

FINANCIAL IMPACT SUMMARY
=======================
Total Daily Impact: ${total_cost_impact:.2f}
Total Monthly Impact: ${monthly_impact:.2f}
Total Annual Impact: ${annual_impact:.2f}
"""
            
            # Mumbai context analysis
            report += f"""

MUMBAI CONTEXT ANALYSIS
=======================
Cost anomaly detection आपके लिए बिल्कुल electricity bill monitoring जैसा है:

🏠 HOUSEHOLD ANALOGY:
   - Normal usage: Regular daily patterns
   - Spike detection: AC suddenly चालू कर दिया या heavy appliance लगाया
   - Drop detection: Power cut या equipment failure
   - Trend changes: Seasonal changes (summer vs winter)

📊 CURRENT STATUS:
"""
            
            if anomalies:
                critical_count = len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])
                if critical_count > 0:
                    report += f"   🚨 CRITICAL: {critical_count} urgent issues - like electricity meter tampering detected!\n"
                
                high_count = len([a for a in anomalies if a.severity == AnomalySeverity.HIGH])
                if high_count > 0:
                    report += f"   🔴 HIGH: {high_count} significant issues - like AC running 24x7 unexpectedly\n"
                
                medium_count = len([a for a in anomalies if a.severity == AnomalySeverity.MEDIUM])
                if medium_count > 0:
                    report += f"   🟡 MEDIUM: {medium_count} moderate issues - like extra appliance usage\n"
                
                if critical_count == 0 and high_count == 0:
                    report += "   ✅ No critical issues - usage patterns within normal range\n"
            else:
                report += "   🎉 ALL NORMAL: No cost anomalies detected - perfect usage patterns!\n"
            
            report += f"""

DETECTION INSIGHTS
=================
Detection Methods Used:
• Statistical Analysis (Z-score, IQR outliers)
• Machine Learning (Isolation Forest)
• Time Series Analysis (Trend changes)

Pattern Recognition:
• Weekday vs Weekend patterns
• Monthly seasonal adjustments
• Service-specific usage baselines
• Historical trend analysis

REMEDIATION PRIORITIES
=====================
"""
            
            if anomalies:
                critical_anomalies = [a for a in anomalies if a.severity == AnomalySeverity.CRITICAL]
                if critical_anomalies:
                    report += f"""
🚨 IMMEDIATE ACTION (Critical):
• Investigate {len(critical_anomalies)} critical anomalies within 2 hours
• Focus on highest cost impact items first
• Implement emergency cost controls if needed
• Escalate to senior management for budget overruns
"""
                
                high_anomalies = [a for a in anomalies if a.severity == AnomalySeverity.HIGH]
                if high_anomalies:
                    report += f"""
🔴 URGENT ACTION (High Priority):
• Review {len(high_anomalies)} high-priority anomalies within 24 hours
• Analyze root causes and implement fixes
• Set up monitoring for similar patterns
• Consider automated remediation where possible
"""
                
                medium_anomalies = [a for a in anomalies if a.severity == AnomalySeverity.MEDIUM]
                if medium_anomalies:
                    report += f"""
🟡 PLANNED ACTION (Medium Priority):
• Schedule investigation of {len(medium_anomalies)} medium-priority anomalies
• Include in next cost optimization review
• Update baseline patterns if needed
• Enhance monitoring and alerting
"""
            
            report += f"""

AUTOMATION RECOMMENDATIONS
==========================
• Set up real-time anomaly alerting (Slack/Email)
• Implement automated cost controls for critical spikes
• Create service-specific anomaly thresholds
• Enable predictive anomaly detection using forecasting

PREVENTION STRATEGIES
====================
• Regular baseline pattern updates
• Service owner training on cost patterns
• Proactive monitoring of high-risk services
• Integration with deployment pipelines for change correlation

NEXT STEPS
==========
1. Address all critical anomalies immediately
2. Set up automated alerting for future anomalies
3. Review and update detection thresholds monthly
4. Implement cost governance policies
5. Train teams on cost-conscious development practices

Contact: Hindi Tech Community for anomaly investigation support
"""
            
            logger.info("Generated comprehensive cost anomaly report")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate anomaly report: {e}")
            return f"Error generating report: {e}"

# Usage Example
def main():
    """
    Production usage example
    
    Mumbai Context: Complete cost anomaly audit
    """
    try:
        # Initialize anomaly detection system
        print("🔍 Initializing Cost Anomaly Detection System...")
        detector = CostAnomalyDetector()
        
        print("📊 Running comprehensive anomaly detection...")
        
        # Run detection across different time periods
        anomalies = asyncio.run(detector.run_comprehensive_detection(days_back=30))
        
        if anomalies:
            print(f"\n🚨 Detected {len(anomalies)} cost anomalies:")
            
            # Group by severity
            severity_counts = {}
            total_impact = 0
            
            for anomaly in anomalies:
                if anomaly.severity not in severity_counts:
                    severity_counts[anomaly.severity] = 0
                severity_counts[anomaly.severity] += 1
                total_impact += anomaly.impact_assessment.get('cost_impact_daily', 0)
            
            # Show severity breakdown
            for severity, count in severity_counts.items():
                emoji = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"  {emoji.get(severity.value, '•')} {severity.value.title()}: {count}")
            
            print(f"\n💰 Total Daily Cost Impact: ${total_impact:.2f}")
            print(f"💰 Estimated Monthly Impact: ${total_impact * 30:.2f}")
            
            # Show top 5 anomalies
            sorted_anomalies = sorted(anomalies, key=lambda x: abs(x.impact_assessment.get('cost_impact_daily', 0)), reverse=True)
            
            print(f"\n🏆 Top 5 Cost Impact Anomalies:")
            for i, anomaly in enumerate(sorted_anomalies[:5], 1):
                impact = anomaly.impact_assessment.get('cost_impact_daily', 0)
                print(f"  {i}. {anomaly.service}: ${impact:.2f}/day ({anomaly.deviation_percentage:.1f}% deviation)")
        
        else:
            print("✅ No cost anomalies detected - all patterns are normal!")
        
        # Generate comprehensive report
        print("\n📄 Generating cost anomaly analysis report...")
        report = detector.generate_anomaly_report(anomalies)
        
        # Save report
        with open('cost_anomaly_report.txt', 'w') as f:
            f.write(report)
        
        print("✅ Cost anomaly detection completed!")
        print("📄 Report saved to cost_anomaly_report.txt")
        
        # Show Mumbai style summary
        print(f"\n💡 Mumbai Electricity Bill Analogy:")
        if anomalies:
            critical_count = len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])
            if critical_count > 0:
                print("🚨 Like electricity bill doubled suddenly - check meter/appliances immediately!")
            else:
                print("⚠️  Like slightly higher bill - review usage patterns and optimize")
        else:
            print("🎉 Like normal monthly bill - usage patterns are healthy!")
        
        # Show practical recommendations
        if total_impact > 100:
            print(f"\n💰 Cost Impact: ${total_impact * 30:.2f}/month potential savings through anomaly resolution")
            print("🎯 Priority: Focus on highest impact anomalies first")
        
    except Exception as e:
        logger.error(f"Cost anomaly detection failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Production Implementation Guide (Hindi):
========================================

1. Real-time Monitoring:
   - CloudWatch integration for real-time cost metrics
   - Lambda-based anomaly detection triggers
   - SNS notifications for immediate alerts
   - Dashboard integration for visualization

2. Machine Learning Enhancement:
   - Historical data collection (6+ months)
   - Seasonal pattern learning and adjustment
   - Service-specific model training
   - Continuous model improvement

3. Mumbai Business Context:
   - Cultural understanding of cost patterns
   - Local business cycle adjustments
   - Regional pricing variations
   - Compliance with Indian audit requirements

4. Integration Points:
   - ITSM tools for incident creation
   - Slack/Teams for team notifications
   - JIRA for tracking remediation actions
   - Budget management systems

5. Advanced Analytics:
   - Predictive anomaly detection
   - Root cause correlation analysis
   - Impact assessment automation
   - Trend forecasting with confidence intervals

यह system आपके cloud costs को Mumbai electricity meter जैसा intelligent monitoring प्रदान करेगा!
"""