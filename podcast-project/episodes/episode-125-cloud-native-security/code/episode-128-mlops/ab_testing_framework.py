#!/usr/bin/env python3
"""
A/B Testing Framework for Food Delivery Platforms
फूड डिलीवरी प्लेटफॉर्म के लिए A/B टेस्टिंग फ्रेमवर्क

Statistical A/B testing for Zomato/Swiggy style experiments
Mumbai food delivery optimization के लिए production-ready system

Author: System Design Hindi Podcast
Cost: ~₹40,000/month for A/B testing infrastructure
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import scipy.stats as stats
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging
import hashlib
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """A/B experiment की different states"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MetricType(Enum):
    """Different types of metrics for A/B testing"""
    CONVERSION_RATE = "conversion_rate"  # Order conversion
    REVENUE_PER_USER = "revenue_per_user"  # Average revenue
    RETENTION_RATE = "retention_rate"  # User retention
    TIME_TO_DELIVERY = "time_to_delivery"  # Delivery time
    CUSTOMER_SATISFACTION = "customer_satisfaction"  # Rating
    CART_ABANDONMENT = "cart_abandonment"  # Cart drop rate

class StatisticalTest(Enum):
    """Statistical tests for different metric types"""
    Z_TEST = "z_test"  # For proportions
    T_TEST = "t_test"  # For means
    MANN_WHITNEY = "mann_whitney"  # Non-parametric
    CHI_SQUARE = "chi_square"  # Categorical data

@dataclass
class ExperimentConfig:
    """A/B experiment का configuration"""
    experiment_id: str
    name: str
    description: str
    hypothesis: str
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    traffic_split: Dict[str, float]  # {"control": 0.5, "treatment": 0.5}
    min_sample_size: int
    confidence_level: float
    power: float
    expected_effect_size: float
    duration_days: int
    target_audience: Dict[str, Any]
    created_by: str
    created_at: datetime

@dataclass
class ExperimentResult:
    """A/B test का result"""
    experiment_id: str
    variant: str
    metric: MetricType
    sample_size: int
    mean_value: float
    std_dev: float
    confidence_interval: Tuple[float, float]
    p_value: float
    statistical_significance: bool
    practical_significance: bool
    effect_size: float
    lift_percentage: float

class FoodDeliveryABTester:
    """
    Food delivery platforms के लिए comprehensive A/B testing framework
    Zomato, Swiggy जैसे platforms के specific use cases के लिए optimized
    """
    
    def __init__(self, 
                 default_confidence_level: float = 0.95,
                 default_power: float = 0.8,
                 min_effect_size: float = 0.05):
        """
        Initialize A/B testing framework
        
        Args:
            default_confidence_level: Default statistical confidence (95%)
            default_power: Statistical power (80%)
            min_effect_size: Minimum detectable effect size (5%)
        """
        self.default_confidence_level = default_confidence_level
        self.default_power = default_power
        self.min_effect_size = min_effect_size
        
        # Storage for experiments and results
        self.experiments = {}
        self.experiment_data = {}
        self.results_cache = {}
        
        logger.info("Food Delivery A/B Testing Framework initialized")
    
    def create_experiment(self, 
                         name: str,
                         description: str,
                         hypothesis: str,
                         primary_metric: MetricType,
                         traffic_split: Dict[str, float] = None,
                         secondary_metrics: List[MetricType] = None,
                         expected_effect_size: float = None,
                         duration_days: int = 14,
                         target_audience: Dict[str, Any] = None,
                         created_by: str = "data_scientist") -> str:
        """
        Create new A/B experiment
        
        Returns:
            experiment_id: Unique identifier for the experiment
        """
        # Generate unique experiment ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        experiment_id = f"exp_{timestamp}_{experiment_hash}"
        
        # Default traffic split (50-50)
        if traffic_split is None:
            traffic_split = {"control": 0.5, "treatment": 0.5}
        
        # Validate traffic split
        if abs(sum(traffic_split.values()) - 1.0) > 0.001:
            raise ValueError("Traffic split must sum to 1.0")
        
        # Calculate minimum sample size
        effect_size = expected_effect_size or self.min_effect_size
        min_sample_size = self.calculate_sample_size(
            effect_size=effect_size,
            power=self.default_power,
            confidence_level=self.default_confidence_level
        )
        
        # Create experiment configuration
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            traffic_split=traffic_split,
            min_sample_size=min_sample_size,
            confidence_level=self.default_confidence_level,
            power=self.default_power,
            expected_effect_size=effect_size,
            duration_days=duration_days,
            target_audience=target_audience or {},
            created_by=created_by,
            created_at=datetime.now()
        )
        
        self.experiments[experiment_id] = config
        self.experiment_data[experiment_id] = pd.DataFrame()
        
        logger.info(f"Experiment created: {experiment_id} - {name}")
        logger.info(f"Minimum sample size: {min_sample_size} per variant")
        
        return experiment_id
    
    def calculate_sample_size(self, 
                             effect_size: float,
                             power: float = 0.8,
                             confidence_level: float = 0.95,
                             metric_type: MetricType = MetricType.CONVERSION_RATE) -> int:
        """
        Calculate minimum sample size for statistical significance
        
        Args:
            effect_size: Expected effect size (e.g., 0.05 for 5% improvement)
            power: Statistical power (1 - Type II error rate)
            confidence_level: Confidence level (1 - Type I error rate)
            metric_type: Type of metric being tested
        """
        alpha = 1 - confidence_level
        beta = 1 - power
        
        # Get critical values
        z_alpha = stats.norm.ppf(1 - alpha/2)  # Two-tailed test
        z_beta = stats.norm.ppf(power)
        
        if metric_type == MetricType.CONVERSION_RATE:
            # Sample size for proportion test
            # Assuming baseline conversion rate of 10% (typical for food delivery)
            p1 = 0.10  # Baseline conversion rate
            p2 = p1 * (1 + effect_size)  # Treatment conversion rate
            
            p_pooled = (p1 + p2) / 2
            
            n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (p2 - p1)**2
            
        else:
            # Sample size for continuous metrics (t-test)
            # Cohen's d effect size
            d = effect_size
            n = (2 * (z_alpha + z_beta)**2) / (d**2)
        
        return max(int(np.ceil(n)), 100)  # Minimum 100 samples
    
    def assign_user_to_variant(self, 
                              experiment_id: str,
                              user_id: str,
                              user_attributes: Dict[str, Any] = None) -> str:
        """
        Assign user to experiment variant using consistent hashing
        
        Args:
            experiment_id: ID of the experiment
            user_id: Unique user identifier
            user_attributes: User attributes for targeting
            
        Returns:
            variant: Assigned variant name ("control" or "treatment")
        """
        config = self.experiments.get(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Check targeting criteria
        if config.target_audience and user_attributes:
            if not self._check_targeting_criteria(user_attributes, config.target_audience):
                return None  # User doesn't match targeting criteria
        
        # Consistent hash assignment
        hash_input = f"{experiment_id}_{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        random_value = (hash_value % 10000) / 10000  # 0-1 range
        
        # Assign to variant based on traffic split
        cumulative_split = 0
        for variant, split_percentage in config.traffic_split.items():
            cumulative_split += split_percentage
            if random_value <= cumulative_split:
                return variant
        
        # Fallback to control
        return "control"
    
    def record_event(self, 
                    experiment_id: str,
                    user_id: str,
                    variant: str,
                    metric_data: Dict[str, Any],
                    timestamp: datetime = None):
        """
        Record experiment event data
        
        Args:
            experiment_id: ID of the experiment
            user_id: User who performed the action
            variant: Experiment variant
            metric_data: Metric values for this event
            timestamp: Event timestamp
        """
        if experiment_id not in self.experiment_data:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create event record
        event = {
            'user_id': user_id,
            'variant': variant,
            'timestamp': timestamp,
            **metric_data
        }
        
        # Add to experiment data
        self.experiment_data[experiment_id] = pd.concat([
            self.experiment_data[experiment_id],
            pd.DataFrame([event])
        ], ignore_index=True)
        
        # Clear results cache
        if experiment_id in self.results_cache:
            del self.results_cache[experiment_id]
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, List[ExperimentResult]]:
        """
        Analyze A/B experiment results with statistical tests
        
        Returns:
            results: Dictionary of results by metric
        """
        if experiment_id in self.results_cache:
            return self.results_cache[experiment_id]
        
        config = self.experiments.get(experiment_id)
        data = self.experiment_data.get(experiment_id)
        
        if not config or data.empty:
            raise ValueError(f"No data found for experiment {experiment_id}")
        
        results = {}
        
        # Analyze primary metric
        primary_results = self._analyze_metric(
            data, config.primary_metric, config.confidence_level
        )
        results[config.primary_metric.value] = primary_results
        
        # Analyze secondary metrics
        for metric in config.secondary_metrics:
            secondary_results = self._analyze_metric(
                data, metric, config.confidence_level
            )
            results[metric.value] = secondary_results
        
        # Cache results
        self.results_cache[experiment_id] = results
        
        return results
    
    def _analyze_metric(self, 
                       data: pd.DataFrame,
                       metric: MetricType,
                       confidence_level: float) -> List[ExperimentResult]:
        """
        Analyze specific metric across variants
        """
        results = []
        variants = data['variant'].unique()
        
        # Group data by variant
        variant_data = {}
        for variant in variants:
            variant_data[variant] = data[data['variant'] == variant]
        
        # Get metric column name
        metric_col = self._get_metric_column(metric)
        
        if metric_col not in data.columns:
            logger.warning(f"Metric column {metric_col} not found in data")
            return results
        
        # Calculate statistics for each variant
        variant_stats = {}
        for variant in variants:
            vdata = variant_data[variant]
            if len(vdata) > 0 and metric_col in vdata.columns:
                values = vdata[metric_col].dropna()
                if len(values) > 0:
                    variant_stats[variant] = {
                        'sample_size': len(values),
                        'mean': values.mean(),
                        'std': values.std(),
                        'values': values
                    }
        
        # Perform pairwise comparisons (control vs each treatment)
        control_variant = 'control' if 'control' in variant_stats else list(variant_stats.keys())[0]
        
        for variant in variant_stats:
            if variant == control_variant:
                continue
            
            # Statistical test
            p_value, test_statistic = self._perform_statistical_test(
                variant_stats[control_variant]['values'],
                variant_stats[variant]['values'],
                metric
            )
            
            # Effect size calculation
            control_mean = variant_stats[control_variant]['mean']
            treatment_mean = variant_stats[variant]['mean']
            
            if metric in [MetricType.CONVERSION_RATE, MetricType.RETENTION_RATE]:
                # For rates, use difference in proportions
                effect_size = treatment_mean - control_mean
                lift_percentage = ((treatment_mean - control_mean) / control_mean) * 100 if control_mean > 0 else 0
            else:
                # For continuous metrics, use Cohen's d
                pooled_std = np.sqrt(
                    ((variant_stats[control_variant]['std']**2 + variant_stats[variant]['std']**2) / 2)
                )
                effect_size = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
                lift_percentage = ((treatment_mean - control_mean) / control_mean) * 100 if control_mean > 0 else 0
            
            # Confidence interval
            alpha = 1 - confidence_level
            if metric in [MetricType.CONVERSION_RATE, MetricType.RETENTION_RATE]:
                # Confidence interval for proportion
                n = variant_stats[variant]['sample_size']
                p = treatment_mean
                margin_of_error = stats.norm.ppf(1 - alpha/2) * np.sqrt(p * (1 - p) / n)
                ci_lower = p - margin_of_error
                ci_upper = p + margin_of_error
            else:
                # Confidence interval for mean
                n = variant_stats[variant]['sample_size']
                mean = treatment_mean
                std = variant_stats[variant]['std']
                margin_of_error = stats.t.ppf(1 - alpha/2, n-1) * (std / np.sqrt(n))
                ci_lower = mean - margin_of_error
                ci_upper = mean + margin_of_error
            
            # Statistical significance
            statistical_significance = p_value < alpha
            
            # Practical significance (effect size threshold)
            practical_significance = abs(effect_size) > self.min_effect_size
            
            result = ExperimentResult(
                experiment_id=f"{control_variant}_vs_{variant}",
                variant=variant,
                metric=metric,
                sample_size=variant_stats[variant]['sample_size'],
                mean_value=treatment_mean,
                std_dev=variant_stats[variant]['std'],
                confidence_interval=(ci_lower, ci_upper),
                p_value=p_value,
                statistical_significance=statistical_significance,
                practical_significance=practical_significance,
                effect_size=effect_size,
                lift_percentage=lift_percentage
            )
            
            results.append(result)
        
        return results
    
    def _perform_statistical_test(self, 
                                 control_data: pd.Series,
                                 treatment_data: pd.Series,
                                 metric: MetricType) -> Tuple[float, float]:
        """
        Perform appropriate statistical test based on metric type
        """
        if metric in [MetricType.CONVERSION_RATE, MetricType.RETENTION_RATE, MetricType.CART_ABANDONMENT]:
            # Proportion test (z-test)
            n1, n2 = len(control_data), len(treatment_data)
            p1, p2 = control_data.mean(), treatment_data.mean()
            
            # Pooled proportion
            p_pool = (control_data.sum() + treatment_data.sum()) / (n1 + n2)
            
            # Standard error
            se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
            
            if se > 0:
                z_stat = (p2 - p1) / se
                p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))  # Two-tailed
            else:
                z_stat = 0
                p_value = 1.0
            
            return p_value, z_stat
        
        else:
            # Continuous metrics - check for normality and equal variances
            # Shapiro-Wilk test for normality (if sample size < 5000)
            if len(control_data) < 5000 and len(treatment_data) < 5000:
                _, p_norm_control = stats.shapiro(control_data.sample(min(len(control_data), 5000)))
                _, p_norm_treatment = stats.shapiro(treatment_data.sample(min(len(treatment_data), 5000)))
                
                # If both are normal, use t-test; otherwise use Mann-Whitney U
                if p_norm_control > 0.05 and p_norm_treatment > 0.05:
                    # t-test
                    t_stat, p_value = ttest_ind(control_data, treatment_data, equal_var=False)
                    return p_value, t_stat
            
            # Non-parametric test (Mann-Whitney U)
            u_stat, p_value = mannwhitneyu(control_data, treatment_data, alternative='two-sided')
            return p_value, u_stat
    
    def _get_metric_column(self, metric: MetricType) -> str:
        """Get column name for metric"""
        metric_columns = {
            MetricType.CONVERSION_RATE: 'converted',
            MetricType.REVENUE_PER_USER: 'revenue',
            MetricType.RETENTION_RATE: 'retained',
            MetricType.TIME_TO_DELIVERY: 'delivery_time_minutes',
            MetricType.CUSTOMER_SATISFACTION: 'rating',
            MetricType.CART_ABANDONMENT: 'cart_abandoned'
        }
        return metric_columns.get(metric, metric.value)
    
    def _check_targeting_criteria(self, 
                                 user_attributes: Dict[str, Any],
                                 target_criteria: Dict[str, Any]) -> bool:
        """Check if user matches targeting criteria"""
        for key, target_value in target_criteria.items():
            user_value = user_attributes.get(key)
            
            if isinstance(target_value, list):
                if user_value not in target_value:
                    return False
            elif isinstance(target_value, dict):
                # Range checks (e.g., age: {"min": 18, "max": 65})
                if "min" in target_value and user_value < target_value["min"]:
                    return False
                if "max" in target_value and user_value > target_value["max"]:
                    return False
            else:
                if user_value != target_value:
                    return False
        
        return True
    
    def generate_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive experiment report
        """
        config = self.experiments.get(experiment_id)
        data = self.experiment_data.get(experiment_id)
        
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Analyze results
        results = self.analyze_experiment(experiment_id)
        
        # Calculate experiment health metrics
        total_users = len(data['user_id'].unique()) if not data.empty else 0
        days_running = (datetime.now() - config.created_at).days
        
        # Sample size check
        min_sample_reached = all(
            len(data[data['variant'] == variant]) >= config.min_sample_size 
            for variant in config.traffic_split.keys()
            if not data.empty
        )
        
        report = {
            "experiment_info": {
                "id": experiment_id,
                "name": config.name,
                "description": config.description,
                "hypothesis": config.hypothesis,
                "created_by": config.created_by,
                "created_at": config.created_at.isoformat(),
                "duration_days": config.duration_days,
                "days_running": days_running
            },
            "experiment_health": {
                "total_users": total_users,
                "min_sample_size_reached": min_sample_reached,
                "traffic_split_actual": self._calculate_actual_traffic_split(data),
                "data_quality_score": self._calculate_data_quality_score(data)
            },
            "results_summary": {},
            "recommendations": [],
            "statistical_summary": {}
        }
        
        # Process results
        if results:
            primary_metric_results = results.get(config.primary_metric.value, [])
            
            if primary_metric_results:
                primary_result = primary_metric_results[0]  # First comparison
                
                report["results_summary"] = {
                    "primary_metric": config.primary_metric.value,
                    "statistical_significance": primary_result.statistical_significance,
                    "practical_significance": primary_result.practical_significance,
                    "p_value": primary_result.p_value,
                    "effect_size": primary_result.effect_size,
                    "lift_percentage": primary_result.lift_percentage,
                    "confidence_interval": primary_result.confidence_interval,
                    "sample_size": primary_result.sample_size
                }
                
                # Recommendations
                if primary_result.statistical_significance and primary_result.practical_significance:
                    if primary_result.lift_percentage > 0:
                        report["recommendations"].append("✅ LAUNCH: Treatment shows significant positive impact")
                    else:
                        report["recommendations"].append("❌ DON'T LAUNCH: Treatment shows significant negative impact")
                elif primary_result.statistical_significance and not primary_result.practical_significance:
                    report["recommendations"].append("🤔 MARGINAL: Statistically significant but small effect size")
                elif not min_sample_reached:
                    report["recommendations"].append("⏳ CONTINUE: Need more data to reach statistical power")
                else:
                    report["recommendations"].append("🔄 ITERATE: No significant difference detected")
        
        return report
    
    def _calculate_actual_traffic_split(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate actual traffic split from data"""
        if data.empty:
            return {}
        
        total_users = len(data)
        actual_split = {}
        
        for variant, count in data['variant'].value_counts().items():
            actual_split[variant] = count / total_users
        
        return actual_split
    
    def _calculate_data_quality_score(self, data: pd.DataFrame) -> float:
        """Calculate data quality score (0-1)"""
        if data.empty:
            return 0.0
        
        score = 1.0
        
        # Check for missing values
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        score -= missing_ratio * 0.3
        
        # Check for extreme outliers (simplified)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in data.columns:
                q99 = data[col].quantile(0.99)
                q01 = data[col].quantile(0.01)
                outlier_ratio = ((data[col] > q99) | (data[col] < q01)).sum() / len(data)
                if outlier_ratio > 0.05:  # More than 5% outliers
                    score -= 0.1
        
        return max(0.0, score)
    
    def visualize_experiment_results(self, 
                                   experiment_id: str,
                                   save_path: str = "ab_test_results.png"):
        """
        Create visualization for A/B test results
        """
        config = self.experiments[experiment_id]
        data = self.experiment_data[experiment_id]
        results = self.analyze_experiment(experiment_id)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'A/B Test Results: {config.name}', fontsize=16, fontweight='bold')
        
        # Plot 1: Sample sizes by variant
        variant_counts = data['variant'].value_counts()
        axes[0, 0].bar(variant_counts.index, variant_counts.values, 
                      color=['blue', 'orange', 'green'][:len(variant_counts)])
        axes[0, 0].set_title('Sample Size by Variant')
        axes[0, 0].set_ylabel('Number of Users')
        
        # Add minimum sample size line
        axes[0, 0].axhline(y=config.min_sample_size, color='red', linestyle='--', 
                          label=f'Min Sample Size: {config.min_sample_size}')
        axes[0, 0].legend()
        
        # Plot 2: Primary metric distribution
        primary_metric_col = self._get_metric_column(config.primary_metric)
        if primary_metric_col in data.columns:
            for variant in data['variant'].unique():
                variant_data = data[data['variant'] == variant][primary_metric_col].dropna()
                if len(variant_data) > 0:
                    axes[0, 1].hist(variant_data, alpha=0.7, label=variant, bins=30)
            
            axes[0, 1].set_title(f'Distribution: {config.primary_metric.value}')
            axes[0, 1].set_xlabel('Value')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].legend()
        
        # Plot 3: Time series of conversions
        if 'timestamp' in data.columns:
            data['date'] = pd.to_datetime(data['timestamp']).dt.date
            daily_conversions = data.groupby(['date', 'variant'])[primary_metric_col].mean().unstack()
            
            if not daily_conversions.empty:
                daily_conversions.plot(ax=axes[1, 0], marker='o')
                axes[1, 0].set_title('Daily Conversion Rate Trend')
                axes[1, 0].set_ylabel('Conversion Rate')
                axes[1, 0].legend(title='Variant')
        
        # Plot 4: Effect size and confidence intervals
        if results and config.primary_metric.value in results:
            primary_results = results[config.primary_metric.value]
            
            variants = [r.variant for r in primary_results]
            effect_sizes = [r.effect_size for r in primary_results]
            ci_lower = [r.confidence_interval[0] - r.mean_value for r in primary_results]
            ci_upper = [r.confidence_interval[1] - r.mean_value for r in primary_results]
            
            if variants:
                x_pos = np.arange(len(variants))
                axes[1, 1].bar(x_pos, effect_sizes, color=['green' if es > 0 else 'red' for es in effect_sizes])
                axes[1, 1].errorbar(x_pos, effect_sizes, yerr=[ci_lower, ci_upper], 
                                   fmt='none', color='black', capsize=5)
                axes[1, 1].set_title('Effect Size with Confidence Intervals')
                axes[1, 1].set_xlabel('Variant')
                axes[1, 1].set_ylabel('Effect Size')
                axes[1, 1].set_xticks(x_pos)
                axes[1, 1].set_xticklabels(variants)
                axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"A/B test results visualization saved to {save_path}")

def demo_food_delivery_ab_testing():
    """
    Complete demo of A/B testing for food delivery platform
    Zomato/Swiggy style experiments के लिए realistic scenarios
    """
    print("🚀 Food Delivery A/B Testing Demo")
    print("=" * 50)
    
    # Initialize A/B testing framework
    ab_tester = FoodDeliveryABTester(
        default_confidence_level=0.95,
        default_power=0.8,
        min_effect_size=0.05
    )
    
    # Experiment 1: Zomato Restaurant Ranking Algorithm
    print("\n📊 Creating Zomato Restaurant Ranking Experiment...")
    
    ranking_exp = ab_tester.create_experiment(
        name="zomato_ranking_algorithm_v2",
        description="Test new ML-based restaurant ranking vs current popularity-based ranking",
        hypothesis="ML-based ranking will increase order conversion rate by at least 8%",
        primary_metric=MetricType.CONVERSION_RATE,
        secondary_metrics=[MetricType.REVENUE_PER_USER, MetricType.CUSTOMER_SATISFACTION],
        traffic_split={"control": 0.5, "treatment": 0.5},
        expected_effect_size=0.08,
        duration_days=21,
        target_audience={
            "city": ["mumbai", "delhi", "bangalore"],
            "user_type": ["regular", "premium"],
            "app_version": "v4.5+"
        },
        created_by="ml_team_mumbai"
    )
    
    print(f"✅ Experiment created: {ranking_exp}")
    
    # Experiment 2: Swiggy Delivery Time Prediction UI
    print("\n🚚 Creating Swiggy Delivery Time Experiment...")
    
    delivery_exp = ab_tester.create_experiment(
        name="swiggy_delivery_time_display",
        description="Show accurate delivery time predictions vs generic time ranges",
        hypothesis="Accurate delivery time display will reduce cart abandonment by 15%",
        primary_metric=MetricType.CART_ABANDONMENT,
        secondary_metrics=[MetricType.CONVERSION_RATE, MetricType.CUSTOMER_SATISFACTION],
        traffic_split={"control": 0.4, "treatment_a": 0.3, "treatment_b": 0.3},
        expected_effect_size=0.15,
        duration_days=14,
        target_audience={
            "city": ["bangalore", "hyderabad", "pune"],
            "order_frequency": ["high", "medium"]
        },
        created_by="product_team_bangalore"
    )
    
    print(f"✅ Experiment created: {delivery_exp}")
    
    # Generate sample data for experiments
    print("\n📈 Generating Sample Experiment Data...")
    
    # Generate Zomato ranking experiment data
    np.random.seed(42)
    n_users = 5000
    
    print(f"Simulating {n_users} users for restaurant ranking experiment...")
    
    for i in range(n_users):
        user_id = f"user_{i:05d}"
        
        # User attributes
        user_attrs = {
            "city": np.random.choice(["mumbai", "delhi", "bangalore"], p=[0.4, 0.35, 0.25]),
            "user_type": np.random.choice(["regular", "premium"], p=[0.8, 0.2]),
            "app_version": "v4.5+",
            "age": np.random.randint(18, 55),
            "order_history": np.random.randint(1, 100)
        }
        
        # Assign to variant
        variant = ab_tester.assign_user_to_variant(ranking_exp, user_id, user_attrs)
        
        if variant:
            # Simulate user behavior
            base_conversion_rate = 0.12  # 12% baseline conversion
            
            if variant == "treatment":
                # ML ranking improves conversion by 8%
                conversion_rate = base_conversion_rate * 1.08
            else:
                conversion_rate = base_conversion_rate
            
            # Add some randomness based on user attributes
            if user_attrs["user_type"] == "premium":
                conversion_rate *= 1.3  # Premium users convert more
            
            if user_attrs["city"] == "mumbai":
                conversion_rate *= 1.1  # Mumbai users slightly more likely to convert
            
            # Simulate conversion
            converted = np.random.random() < conversion_rate
            
            # Generate revenue (if converted)
            if converted:
                base_revenue = 350  # Average order value ₹350
                revenue = np.random.lognormal(np.log(base_revenue), 0.5)
                if user_attrs["user_type"] == "premium":
                    revenue *= 1.4  # Premium users order more expensive items
            else:
                revenue = 0
            
            # Generate satisfaction score (1-5)
            if variant == "treatment":
                satisfaction = np.random.normal(4.2, 0.8)  # ML ranking gives better experience
            else:
                satisfaction = np.random.normal(3.9, 0.9)
            satisfaction = np.clip(satisfaction, 1, 5)
            
            # Record event
            ab_tester.record_event(
                ranking_exp, user_id, variant,
                {
                    "converted": 1 if converted else 0,
                    "revenue": revenue,
                    "rating": satisfaction
                },
                datetime.now() - timedelta(days=np.random.randint(0, 21))
            )
    
    # Generate Swiggy delivery time experiment data
    print(f"Simulating users for delivery time experiment...")
    
    for i in range(3000):
        user_id = f"delivery_user_{i:05d}"
        
        user_attrs = {
            "city": np.random.choice(["bangalore", "hyderabad", "pune"], p=[0.5, 0.3, 0.2]),
            "order_frequency": np.random.choice(["high", "medium"], p=[0.3, 0.7])
        }
        
        variant = ab_tester.assign_user_to_variant(delivery_exp, user_id, user_attrs)
        
        if variant:
            # Base cart abandonment rate: 25%
            base_abandonment = 0.25
            
            if variant == "treatment_a":
                # Accurate delivery time reduces abandonment by 15%
                abandonment_rate = base_abandonment * 0.85
                conversion_rate = 0.15 * 1.1  # Slight conversion boost
            elif variant == "treatment_b":
                # Another variant with different UI
                abandonment_rate = base_abandonment * 0.88
                conversion_rate = 0.15 * 1.05
            else:
                abandonment_rate = base_abandonment
                conversion_rate = 0.15
            
            # Simulate behavior
            cart_abandoned = np.random.random() < abandonment_rate
            
            if not cart_abandoned:
                converted = np.random.random() < conversion_rate
                if converted:
                    revenue = np.random.lognormal(np.log(280), 0.6)  # Lower AOV than restaurant search
                else:
                    revenue = 0
                
                # Satisfaction (delivery time accuracy)
                if variant in ["treatment_a", "treatment_b"]:
                    satisfaction = np.random.normal(4.3, 0.7)
                else:
                    satisfaction = np.random.normal(3.8, 1.0)
                satisfaction = np.clip(satisfaction, 1, 5)
            else:
                converted = 0
                revenue = 0
                satisfaction = np.random.normal(2.5, 1.0)  # Low satisfaction if abandoned
                satisfaction = np.clip(satisfaction, 1, 5)
            
            ab_tester.record_event(
                delivery_exp, user_id, variant,
                {
                    "cart_abandoned": 1 if cart_abandoned else 0,
                    "converted": 1 if converted else 0,
                    "revenue": revenue,
                    "rating": satisfaction
                },
                datetime.now() - timedelta(days=np.random.randint(0, 14))
            )
    
    # Analyze experiments
    print("\n🔍 Analyzing Experiment Results...")
    
    # Restaurant ranking experiment analysis
    print(f"\n📊 ZOMATO RESTAURANT RANKING RESULTS:")
    print("=" * 40)
    
    ranking_results = ab_tester.analyze_experiment(ranking_exp)
    ranking_report = ab_tester.generate_experiment_report(ranking_exp)
    
    print(f"Experiment: {ranking_report['experiment_info']['name']}")
    print(f"Total Users: {ranking_report['experiment_health']['total_users']}")
    print(f"Days Running: {ranking_report['experiment_health']['days_running']}")
    
    if 'conversion_rate' in ranking_results:
        conv_result = ranking_results['conversion_rate'][0]
        print(f"\nPrimary Metric - Conversion Rate:")
        print(f"  Treatment Mean: {conv_result.mean_value:.1%}")
        print(f"  Lift: {conv_result.lift_percentage:+.1f}%")
        print(f"  P-value: {conv_result.p_value:.4f}")
        print(f"  Statistical Significance: {'✅ YES' if conv_result.statistical_significance else '❌ NO'}")
        print(f"  Practical Significance: {'✅ YES' if conv_result.practical_significance else '❌ NO'}")
        print(f"  95% CI: [{conv_result.confidence_interval[0]:.1%}, {conv_result.confidence_interval[1]:.1%}]")
    
    print(f"\nRecommendations:")
    for rec in ranking_report['recommendations']:
        print(f"  {rec}")
    
    # Delivery time experiment analysis
    print(f"\n🚚 SWIGGY DELIVERY TIME RESULTS:")
    print("=" * 35)
    
    delivery_results = ab_tester.analyze_experiment(delivery_exp)
    delivery_report = ab_tester.generate_experiment_report(delivery_exp)
    
    print(f"Experiment: {delivery_report['experiment_info']['name']}")
    print(f"Total Users: {delivery_report['experiment_health']['total_users']}")
    
    if 'cart_abandonment' in delivery_results:
        for i, result in enumerate(delivery_results['cart_abandonment']):
            print(f"\nVariant: {result.variant}")
            print(f"  Cart Abandonment Rate: {result.mean_value:.1%}")
            print(f"  Change: {result.lift_percentage:+.1f}%")
            print(f"  P-value: {result.p_value:.4f}")
            print(f"  Significant: {'✅ YES' if result.statistical_significance else '❌ NO'}")
    
    # Create visualizations
    print(f"\n📊 Creating Experiment Visualizations...")
    ab_tester.visualize_experiment_results(ranking_exp, "zomato_ranking_ab_test.png")
    ab_tester.visualize_experiment_results(delivery_exp, "swiggy_delivery_ab_test.png")
    
    # Calculate business impact
    print(f"\n💰 Business Impact Analysis:")
    print("=" * 30)
    
    # Zomato ranking impact
    if 'conversion_rate' in ranking_results:
        conv_result = ranking_results['conversion_rate'][0]
        daily_users = 50000  # Assume 50k daily users in test cities
        
        if conv_result.statistical_significance and conv_result.lift_percentage > 0:
            daily_extra_orders = daily_users * 0.5 * (conv_result.lift_percentage / 100) * 0.12  # 50% in treatment, base 12% conversion
            monthly_extra_orders = daily_extra_orders * 30
            avg_order_value = 350  # ₹350
            monthly_extra_revenue = monthly_extra_orders * avg_order_value
            
            print(f"Zomato Ranking Impact:")
            print(f"  Daily Extra Orders: {daily_extra_orders:.0f}")
            print(f"  Monthly Extra Revenue: ₹{monthly_extra_revenue:,.0f}")
            print(f"  Annual Impact: ₹{monthly_extra_revenue * 12:,.0f}")
    
    # Swiggy delivery impact
    if 'cart_abandonment' in delivery_results:
        abandon_result = delivery_results['cart_abandonment'][0]  # First treatment
        daily_users = 30000  # Assume 30k daily users
        
        if abandon_result.statistical_significance and abandon_result.lift_percentage < 0:  # Negative is good for abandonment
            base_abandonment = 0.25
            treatment_abandonment = abandon_result.mean_value
            abandonment_reduction = base_abandonment - treatment_abandonment
            
            daily_saved_orders = daily_users * 0.3 * abandonment_reduction  # 30% in treatment A
            monthly_saved_orders = daily_saved_orders * 30
            avg_order_value = 280
            monthly_saved_revenue = monthly_saved_orders * avg_order_value
            
            print(f"\nSwiggy Delivery Time Impact:")
            print(f"  Daily Orders Saved: {daily_saved_orders:.0f}")
            print(f"  Monthly Revenue Saved: ₹{monthly_saved_revenue:,.0f}")
            print(f"  Annual Impact: ₹{monthly_saved_revenue * 12:,.0f}")
    
    print(f"\n💸 A/B Testing Infrastructure Costs:")
    print(f"Data Pipeline: ₹15,000/month")
    print(f"Analytics Platform: ₹10,000/month")
    print(f"Statistical Analysis: ₹8,000/month")
    print(f"Visualization Tools: ₹4,000/month")
    print(f"Engineering Time: ₹3,000/month")
    print(f"Total: ₹40,000/month")
    
    print(f"\n📈 ROI Analysis:")
    total_monthly_impact = 0
    if 'conversion_rate' in ranking_results and ranking_results['conversion_rate'][0].statistical_significance:
        total_monthly_impact += monthly_extra_revenue if 'monthly_extra_revenue' in locals() else 0
    if 'cart_abandonment' in delivery_results and delivery_results['cart_abandonment'][0].statistical_significance:
        total_monthly_impact += monthly_saved_revenue if 'monthly_saved_revenue' in locals() else 0
    
    if total_monthly_impact > 40000:
        roi = ((total_monthly_impact - 40000) / 40000) * 100
        print(f"Monthly ROI: {roi:.0f}%")
        print(f"Payback Period: {40000 / total_monthly_impact:.1f} months")
    
    return ab_tester, ranking_exp, delivery_exp

if __name__ == "__main__":
    ab_tester, ranking_exp, delivery_exp = demo_food_delivery_ab_testing()
    print("\n🎉 Food Delivery A/B Testing Demo Complete!")
    print("📊 Framework ready for production experimentation")