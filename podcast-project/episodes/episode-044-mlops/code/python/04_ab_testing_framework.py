#!/usr/bin/env python3
"""
A/B Testing Framework for ML Models - MLOps Episode 44
Production-ready A/B testing for ML model deployments

Author: Claude Code
Context: Flipkart-style A/B testing framework for ML model performance
"""

import uuid
import json
import time
import random
import hashlib
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from scipy import stats
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """A/B experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TrafficAllocation(Enum):
    """Traffic allocation strategies"""
    RANDOM = "random"
    STICKY = "sticky"
    HASH_BASED = "hash_based"
    PERCENTAGE = "percentage"

@dataclass
class ExperimentConfig:
    """A/B experiment configuration"""
    name: str
    description: str
    hypothesis: str
    control_model_id: str
    treatment_model_id: str
    traffic_percentage: float  # 0.1 = 10% of traffic
    allocation_strategy: TrafficAllocation
    primary_metric: str
    secondary_metrics: List[str]
    minimum_sample_size: int
    minimum_duration_hours: int
    maximum_duration_hours: int
    significance_level: float = 0.05
    power: float = 0.8
    tags: List[str] = None

@dataclass
class ExperimentResult:
    """Single experiment result/observation"""
    experiment_id: str
    user_id: str
    variant: str  # 'control' or 'treatment'
    timestamp: datetime
    metrics: Dict[str, float]
    metadata: Dict[str, Any] = None

@dataclass
class StatisticalResult:
    """Statistical analysis result"""
    metric_name: str
    control_mean: float
    treatment_mean: float
    control_std: float
    treatment_std: float
    control_count: int
    treatment_count: int
    difference: float
    relative_difference: float
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    effect_size: float

class FlipkartABTestFramework:
    """
    Production A/B Testing Framework for ML Models
    Mumbai me sabse reliable A/B testing system!
    """
    
    def __init__(self, db_path: str = "ab_testing.db"):
        self.db_path = db_path
        self.active_experiments: Dict[str, ExperimentConfig] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant}
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for experiments"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    hypothesis TEXT,
                    control_model_id TEXT NOT NULL,
                    treatment_model_id TEXT NOT NULL,
                    traffic_percentage REAL NOT NULL,
                    allocation_strategy TEXT NOT NULL,
                    primary_metric TEXT NOT NULL,
                    secondary_metrics TEXT,
                    minimum_sample_size INTEGER NOT NULL,
                    minimum_duration_hours INTEGER NOT NULL,
                    maximum_duration_hours INTEGER NOT NULL,
                    significance_level REAL NOT NULL,
                    power REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    ended_at TEXT,
                    tags TEXT,
                    config_json TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS experiment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    metadata_json TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_assignments (
                    user_id TEXT,
                    experiment_id TEXT,
                    variant TEXT,
                    assigned_at TEXT,
                    PRIMARY KEY (user_id, experiment_id),
                    FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
                )
            ''')
            
            # Create indexes for performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_experiment_results_exp_variant 
                ON experiment_results (experiment_id, variant)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_assignments_user 
                ON user_assignments (user_id)
            ''')
    
    def _calculate_sample_size(self, effect_size: float, alpha: float = 0.05, power: float = 0.8) -> int:
        """
        Calculate required sample size for statistical power
        Mumbai me sample size ka scientific calculation!
        """
        # Using simplified formula for two-sample t-test
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Approximate sample size per group
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        return int(np.ceil(n))
    
    def create_experiment(self, config: ExperimentConfig) -> str:
        """
        Create new A/B experiment
        Mumbai me nayi experiment ki shururat!
        """
        experiment_id = str(uuid.uuid4())
        
        if config.tags is None:
            config.tags = []
        
        # Validate configuration
        if config.traffic_percentage <= 0 or config.traffic_percentage > 1:
            raise ValueError("Traffic percentage must be between 0 and 1")
        
        if config.minimum_sample_size <= 0:
            raise ValueError("Minimum sample size must be positive")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO experiments VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    experiment_id, config.name, config.description, config.hypothesis,
                    config.control_model_id, config.treatment_model_id,
                    config.traffic_percentage, config.allocation_strategy.value,
                    config.primary_metric, json.dumps(config.secondary_metrics),
                    config.minimum_sample_size, config.minimum_duration_hours,
                    config.maximum_duration_hours, config.significance_level,
                    config.power, ExperimentStatus.DRAFT.value,
                    datetime.now().isoformat(), None, None,
                    json.dumps(config.tags), json.dumps(asdict(config))
                ))
            
            logger.info(f"Experiment created: {experiment_id} - {config.name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            raise
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start A/B experiment
        Mumbai Express ki tarah experiment start!
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load experiment config
                cursor = conn.execute(
                    "SELECT config_json FROM experiments WHERE experiment_id = ?",
                    (experiment_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError(f"Experiment not found: {experiment_id}")
                
                config_data = json.loads(row[0])
                config = ExperimentConfig(**config_data)
                
                # Update status
                conn.execute('''
                    UPDATE experiments 
                    SET status = ?, started_at = ?
                    WHERE experiment_id = ?
                ''', (ExperimentStatus.RUNNING.value, datetime.now().isoformat(), experiment_id))
                
                # Store in memory for quick access
                with self.lock:
                    self.active_experiments[experiment_id] = config
                
                logger.info(f"Experiment started: {experiment_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start experiment: {e}")
            return False
    
    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop running experiment"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE experiments 
                    SET status = ?, ended_at = ?
                    WHERE experiment_id = ?
                ''', (ExperimentStatus.COMPLETED.value, datetime.now().isoformat(), experiment_id))
                
                # Remove from memory
                with self.lock:
                    if experiment_id in self.active_experiments:
                        del self.active_experiments[experiment_id]
                
                logger.info(f"Experiment stopped: {experiment_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop experiment: {e}")
            return False
    
    def _hash_user_to_variant(self, user_id: str, experiment_id: str) -> str:
        """
        Hash-based user assignment for consistency
        Mumbai me consistent allocation ka jugaad!
        """
        # Create deterministic hash
        hash_input = f"{user_id}_{experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Map to 0-1 range
        normalized_hash = (hash_value % 10000) / 10000.0
        
        # 50-50 split between control and treatment
        return "control" if normalized_hash < 0.5 else "treatment"
    
    def assign_user_to_variant(self, user_id: str, experiment_id: str) -> Optional[str]:
        """
        Assign user to experiment variant
        Mumbai me user ka group decide karna!
        """
        if experiment_id not in self.active_experiments:
            return None
        
        config = self.active_experiments[experiment_id]
        
        # Check if user should be included (traffic percentage)
        traffic_hash = int(hashlib.md5(f"{user_id}_{experiment_id}_traffic".encode()).hexdigest(), 16)
        traffic_threshold = (traffic_hash % 10000) / 10000.0
        
        if traffic_threshold > config.traffic_percentage:
            return None  # User not included in experiment
        
        # Check existing assignment
        with self.lock:
            if user_id in self.user_assignments and experiment_id in self.user_assignments[user_id]:
                return self.user_assignments[user_id][experiment_id]
        
        # Assign variant based on strategy
        if config.allocation_strategy == TrafficAllocation.HASH_BASED:
            variant = self._hash_user_to_variant(user_id, experiment_id)
        elif config.allocation_strategy == TrafficAllocation.RANDOM:
            variant = random.choice(["control", "treatment"])
        else:
            variant = self._hash_user_to_variant(user_id, experiment_id)  # Default
        
        # Store assignment
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_assignments VALUES (?, ?, ?, ?)
                ''', (user_id, experiment_id, variant, datetime.now().isoformat()))
            
            with self.lock:
                if user_id not in self.user_assignments:
                    self.user_assignments[user_id] = {}
                self.user_assignments[user_id][experiment_id] = variant
            
            return variant
            
        except Exception as e:
            logger.error(f"Failed to assign user to variant: {e}")
            return None
    
    def record_result(self, result: ExperimentResult) -> bool:
        """
        Record experiment result/observation
        Mumbai me result ka record rakhna!
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO experiment_results 
                    (experiment_id, user_id, variant, timestamp, metrics_json, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    result.experiment_id, result.user_id, result.variant,
                    result.timestamp.isoformat(), json.dumps(result.metrics),
                    json.dumps(result.metadata) if result.metadata else None
                ))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record result: {e}")
            return False
    
    def get_experiment_data(self, experiment_id: str) -> pd.DataFrame:
        """Get all experiment data as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT user_id, variant, timestamp, metrics_json, metadata_json
                FROM experiment_results
                WHERE experiment_id = ?
                ORDER BY timestamp
            '''
            
            cursor = conn.execute(query, (experiment_id,))
            rows = cursor.fetchall()
            
            if not rows:
                return pd.DataFrame()
            
            # Parse data
            data = []
            for row in rows:
                user_id, variant, timestamp, metrics_json, metadata_json = row
                metrics = json.loads(metrics_json)
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                record = {
                    'user_id': user_id,
                    'variant': variant,
                    'timestamp': datetime.fromisoformat(timestamp),
                    **metrics,
                    **{f"meta_{k}": v for k, v in metadata.items()}
                }
                data.append(record)
            
            return pd.DataFrame(data)
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Comprehensive statistical analysis of experiment
        Mumbai me experiment ka complete analysis!
        """
        # Get experiment config
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT config_json FROM experiments WHERE experiment_id = ?",
                (experiment_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            config_data = json.loads(row[0])
            config = ExperimentConfig(**config_data)
        
        # Get data
        df = self.get_experiment_data(experiment_id)
        
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        # Separate control and treatment
        control_data = df[df['variant'] == 'control']
        treatment_data = df[df['variant'] == 'treatment']
        
        if len(control_data) == 0 or len(treatment_data) == 0:
            return {'error': 'Insufficient data for both variants'}
        
        # Analyze all metrics
        all_metrics = [config.primary_metric] + config.secondary_metrics
        results = {}
        
        for metric in all_metrics:
            if metric not in df.columns:
                continue
            
            # Statistical analysis
            control_values = control_data[metric].dropna()
            treatment_values = treatment_data[metric].dropna()
            
            if len(control_values) == 0 or len(treatment_values) == 0:
                continue
            
            # T-test
            t_stat, p_value = stats.ttest_ind(treatment_values, control_values)
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(control_values) - 1) * control_values.var() + 
                                 (len(treatment_values) - 1) * treatment_values.var()) / 
                                 (len(control_values) + len(treatment_values) - 2))
            
            effect_size = (treatment_values.mean() - control_values.mean()) / pooled_std
            
            # Confidence interval
            se_diff = np.sqrt(control_values.var()/len(control_values) + 
                             treatment_values.var()/len(treatment_values))
            
            t_critical = stats.t.ppf(1 - config.significance_level/2, 
                                   len(control_values) + len(treatment_values) - 2)
            
            diff = treatment_values.mean() - control_values.mean()
            ci_lower = diff - t_critical * se_diff
            ci_upper = diff + t_critical * se_diff
            
            # Relative difference
            rel_diff = (diff / control_values.mean()) * 100 if control_values.mean() != 0 else 0
            
            result = StatisticalResult(
                metric_name=metric,
                control_mean=control_values.mean(),
                treatment_mean=treatment_values.mean(),
                control_std=control_values.std(),
                treatment_std=treatment_values.std(),
                control_count=len(control_values),
                treatment_count=len(treatment_values),
                difference=diff,
                relative_difference=rel_diff,
                p_value=p_value,
                confidence_interval=(ci_lower, ci_upper),
                is_significant=p_value < config.significance_level,
                effect_size=effect_size
            )
            
            results[metric] = asdict(result)
        
        # Overall summary
        primary_result = results.get(config.primary_metric)
        summary = {
            'experiment_id': experiment_id,
            'total_users': len(df['user_id'].unique()),
            'control_users': len(control_data['user_id'].unique()),
            'treatment_users': len(treatment_data['user_id'].unique()),
            'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600,
            'primary_metric_significant': primary_result['is_significant'] if primary_result else False,
            'primary_metric_improvement': primary_result['relative_difference'] if primary_result else 0,
            'recommendation': self._get_recommendation(results, config),
            'detailed_results': results
        }
        
        return summary
    
    def _get_recommendation(self, results: Dict[str, Any], config: ExperimentConfig) -> str:
        """Generate recommendation based on results"""
        primary_result = results.get(config.primary_metric)
        
        if not primary_result:
            return "Insufficient data for recommendation"
        
        if not primary_result['is_significant']:
            return "No significant difference detected. Consider running longer or increasing sample size."
        
        if primary_result['relative_difference'] > 0:
            return f"Treatment shows {primary_result['relative_difference']:.2f}% improvement. Recommend rolling out."
        else:
            return f"Treatment shows {abs(primary_result['relative_difference']):.2f}% decline. Recommend keeping control."
    
    def list_experiments(self, status: ExperimentStatus = None) -> List[Dict[str, Any]]:
        """List experiments with optional status filter"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT experiment_id, name, status, created_at, started_at, ended_at FROM experiments"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC"
            
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            experiments = []
            for row in cursor.fetchall():
                exp_dict = dict(zip(columns, row))
                experiments.append(exp_dict)
            
            return experiments

def simulate_flipkart_recommendation_experiment():
    """
    Simulate Flipkart recommendation system A/B test
    Mumbai me Flipkart recommendation ka A/B test!
    """
    # Initialize framework
    ab_framework = FlipkartABTestFramework("flipkart_ab_test.db")
    
    # Create experiment configuration
    config = ExperimentConfig(
        name="recommendation_algorithm_v2",
        description="Testing new collaborative filtering algorithm vs current model",
        hypothesis="New CF algorithm will increase click-through rate by 15%",
        control_model_id="flipkart_rec_v1",
        treatment_model_id="flipkart_rec_v2",
        traffic_percentage=0.1,  # 10% of users
        allocation_strategy=TrafficAllocation.HASH_BASED,
        primary_metric="click_through_rate",
        secondary_metrics=["add_to_cart_rate", "purchase_rate", "revenue_per_user"],
        minimum_sample_size=10000,
        minimum_duration_hours=72,
        maximum_duration_hours=168,  # 1 week
        significance_level=0.05,
        power=0.8,
        tags=["recommendation", "ml", "revenue"]
    )
    
    return ab_framework, config

def generate_user_interactions(ab_framework: FlipkartABTestFramework, 
                              experiment_id: str, 
                              n_users: int = 1000,
                              n_days: int = 7) -> List[ExperimentResult]:
    """
    Generate realistic user interaction data
    Mumbai me realistic user behavior simulation!
    """
    results = []
    base_date = datetime.now() - timedelta(days=n_days)
    
    for day in range(n_days):
        current_date = base_date + timedelta(days=day)
        daily_users = n_users // n_days
        
        for i in range(daily_users):
            user_id = f"user_{day*daily_users + i:06d}"
            
            # Assign user to variant
            variant = ab_framework.assign_user_to_variant(user_id, experiment_id)
            
            if variant is None:
                continue  # User not in experiment
            
            # Simulate different performance for control vs treatment
            if variant == "control":
                # Control performance
                click_through_rate = np.random.beta(2, 8)  # Mean ~0.2
                add_to_cart_rate = np.random.beta(1, 9)   # Mean ~0.1
                purchase_rate = np.random.beta(1, 19)     # Mean ~0.05
                revenue_per_user = np.random.gamma(2, 10) # Mean ~20
            else:
                # Treatment performance (improved)
                click_through_rate = np.random.beta(2.5, 7.5)  # Mean ~0.25 (+25%)
                add_to_cart_rate = np.random.beta(1.2, 8.8)    # Mean ~0.12 (+20%)
                purchase_rate = np.random.beta(1.1, 18.9)      # Mean ~0.055 (+10%)
                revenue_per_user = np.random.gamma(2.2, 11)    # Mean ~24 (+20%)
            
            # Add some noise and realistic variations
            hour_boost = 1 + 0.5 * np.sin(2 * np.pi * (current_date.hour - 12) / 24)  # Peak at noon
            weekend_boost = 1.2 if current_date.weekday() >= 5 else 1.0
            
            metrics = {
                'click_through_rate': click_through_rate * hour_boost * weekend_boost,
                'add_to_cart_rate': add_to_cart_rate * hour_boost * weekend_boost,
                'purchase_rate': purchase_rate * hour_boost * weekend_boost,
                'revenue_per_user': revenue_per_user * hour_boost * weekend_boost
            }
            
            # Ensure rates don't exceed 1.0
            for rate_metric in ['click_through_rate', 'add_to_cart_rate', 'purchase_rate']:
                metrics[rate_metric] = min(metrics[rate_metric], 1.0)
            
            result = ExperimentResult(
                experiment_id=experiment_id,
                user_id=user_id,
                variant=variant,
                timestamp=current_date + timedelta(hours=np.random.randint(0, 24)),
                metrics=metrics,
                metadata={
                    'platform': np.random.choice(['mobile', 'web'], p=[0.7, 0.3]),
                    'city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai'], p=[0.3, 0.25, 0.25, 0.2]),
                    'user_segment': np.random.choice(['new', 'returning', 'premium'], p=[0.3, 0.5, 0.2])
                }
            )
            
            results.append(result)
    
    return results

def main():
    """
    Demo Flipkart A/B Testing Framework
    Mumbai ke A/B testing ka demo!
    """
    print("🧪 Starting Flipkart A/B Testing Framework Demo")
    print("=" * 60)
    
    # Initialize framework and create experiment
    ab_framework, config = simulate_flipkart_recommendation_experiment()
    
    print(f"\n📋 Creating experiment: {config.name}")
    experiment_id = ab_framework.create_experiment(config)
    print(f"Experiment ID: {experiment_id}")
    
    # Start experiment
    print(f"\n🚀 Starting experiment...")
    ab_framework.start_experiment(experiment_id)
    
    # Generate user interactions
    print(f"\n👥 Simulating user interactions...")
    results = generate_user_interactions(ab_framework, experiment_id, n_users=5000, n_days=7)
    print(f"Generated {len(results)} user interactions")
    
    # Record results
    print(f"\n📊 Recording experiment results...")
    for result in results:
        ab_framework.record_result(result)
    
    # Analyze experiment
    print(f"\n🔍 Analyzing experiment results...")
    analysis = ab_framework.analyze_experiment(experiment_id)
    
    print(f"\n📈 Experiment Results Summary:")
    print(f"  Total Users: {analysis['total_users']}")
    print(f"  Control Users: {analysis['control_users']}")
    print(f"  Treatment Users: {analysis['treatment_users']}")
    print(f"  Duration: {analysis['duration_hours']:.1f} hours")
    print(f"  Primary Metric Significant: {'✅' if analysis['primary_metric_significant'] else '❌'}")
    print(f"  Primary Metric Improvement: {analysis['primary_metric_improvement']:.2f}%")
    print(f"  Recommendation: {analysis['recommendation']}")
    
    print(f"\n📊 Detailed Metric Results:")
    for metric, result in analysis['detailed_results'].items():
        print(f"\n  {metric.upper()}:")
        print(f"    Control Mean: {result['control_mean']:.4f}")
        print(f"    Treatment Mean: {result['treatment_mean']:.4f}")
        print(f"    Difference: {result['difference']:.4f}")
        print(f"    Relative Improvement: {result['relative_difference']:.2f}%")
        print(f"    P-value: {result['p_value']:.4f}")
        print(f"    Significant: {'✅' if result['is_significant'] else '❌'}")
        print(f"    Effect Size: {result['effect_size']:.4f}")
        print(f"    95% CI: ({result['confidence_interval'][0]:.4f}, {result['confidence_interval'][1]:.4f})")
    
    # Stop experiment
    print(f"\n🛑 Stopping experiment...")
    ab_framework.stop_experiment(experiment_id)
    
    # List all experiments
    print(f"\n📋 All experiments:")
    experiments = ab_framework.list_experiments()
    for exp in experiments:
        print(f"  {exp['experiment_id']}: {exp['name']} - {exp['status']}")
    
    print(f"\n✅ A/B testing demo completed!")
    print("Mumbai me A/B testing bhi scientific method ki tarah accurate!")

if __name__ == "__main__":
    main()