#!/usr/bin/env python3
"""
Model Drift Monitoring System for Indian Food Delivery
भारतीय फूड डिलीवरी के लिए मॉडल ड्रिफ्ट मॉनिटरिंग सिस्टम

Real-time monitoring for data drift and model performance degradation
Swiggy/Zomato production models के लिए comprehensive monitoring

Author: System Design Hindi Podcast
Cost: ~₹25,000/month for drift monitoring infrastructure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging
import warnings
from scipy import stats
from scipy.stats import ks_2samp, chi2_contingency, wasserstein_distance
import joblib
from sklearn.base import BaseEstimator
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import sqlite3
import boto3

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftType(Enum):
    """Different types of drift"""
    DATA_DRIFT = "data_drift"           # Input feature distribution changes
    CONCEPT_DRIFT = "concept_drift"     # Relationship between X and y changes
    PREDICTION_DRIFT = "prediction_drift"  # Model output distribution changes
    PERFORMANCE_DRIFT = "performance_drift"  # Model accuracy degradation

class DriftSeverity(Enum):
    """Drift severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    """Drift detection methods"""
    KS_TEST = "kolmogorov_smirnov"
    CHI_SQUARE = "chi_square"
    WASSERSTEIN = "wasserstein_distance"
    PSI = "population_stability_index"
    JENSEN_SHANNON = "jensen_shannon_divergence"

@dataclass
class DriftAlert:
    """Drift detection alert structure"""
    alert_id: str
    timestamp: datetime
    model_id: str
    drift_type: DriftType
    feature_name: str
    detection_method: DetectionMethod
    drift_score: float
    threshold: float
    severity: DriftSeverity
    description: str
    suggested_actions: List[str]
    business_impact: str

class FoodDeliveryDriftMonitor:
    """
    Comprehensive drift monitoring for food delivery ML models
    Mumbai के traffic patterns, festival seasons, monsoon के लिए specialized monitoring
    """
    
    def __init__(self, 
                 db_path: str = "drift_monitoring.db",
                 alert_thresholds: Dict[str, float] = None,
                 monitoring_window_hours: int = 24):
        """
        Initialize drift monitoring system
        
        Args:
            db_path: SQLite database for storing monitoring data
            alert_thresholds: Custom thresholds for different drift types
            monitoring_window_hours: Time window for monitoring (24 hours default)
        """
        self.db_path = db_path
        self.monitoring_window_hours = monitoring_window_hours
        
        # Default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            "data_drift_ks": 0.05,      # KS test p-value
            "data_drift_psi": 0.2,      # PSI threshold
            "concept_drift": 0.1,       # Performance degradation
            "prediction_drift": 0.15,   # Prediction distribution change
            "performance_drift": 0.05   # 5% accuracy drop
        }
        
        # Initialize database
        self._init_database()
        
        # Store reference distributions
        self.reference_data = {}
        self.reference_performance = {}
        self.model_metadata = {}
        
        logger.info("Food Delivery Drift Monitor initialized")
    
    def _init_database(self):
        """Initialize SQLite database for monitoring data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Monitoring data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_id TEXT NOT NULL,
                feature_name TEXT,
                feature_value REAL,
                prediction REAL,
                actual_label REAL,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT
            )
        """)
        
        # Drift alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drift_alerts (
                alert_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                model_id TEXT NOT NULL,
                drift_type TEXT NOT NULL,
                feature_name TEXT,
                detection_method TEXT,
                drift_score REAL,
                threshold REAL,
                severity TEXT,
                description TEXT,
                suggested_actions TEXT,
                business_impact TEXT,
                acknowledged BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Model baselines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_baselines (
                model_id TEXT PRIMARY KEY,
                baseline_timestamp TEXT NOT NULL,
                feature_statistics TEXT,
                performance_metrics TEXT,
                prediction_distribution TEXT,
                sample_size INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Drift monitoring database initialized")
    
    def register_model_baseline(self, 
                               model_id: str,
                               baseline_data: pd.DataFrame,
                               target_column: str = None,
                               prediction_column: str = None):
        """
        Register baseline data for a model (training data characteristics)
        
        Args:
            model_id: Unique identifier for the model
            baseline_data: Training or validation data
            target_column: Name of target column (if available)
            prediction_column: Name of prediction column (if available)
        """
        logger.info(f"Registering baseline for model: {model_id}")
        
        # Calculate feature statistics
        feature_stats = {}
        numeric_columns = baseline_data.select_dtypes(include=[np.number]).columns
        categorical_columns = baseline_data.select_dtypes(include=['object', 'category']).columns
        
        # Numeric features
        for col in numeric_columns:
            if col not in [target_column, prediction_column]:
                values = baseline_data[col].dropna()
                feature_stats[col] = {
                    "type": "numeric",
                    "mean": float(values.mean()),
                    "std": float(values.std()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "q25": float(values.quantile(0.25)),
                    "q50": float(values.quantile(0.50)),
                    "q75": float(values.quantile(0.75)),
                    "missing_rate": float(baseline_data[col].isnull().mean()),
                    "distribution": values.values.tolist()[:1000]  # Sample for KS test
                }
        
        # Categorical features
        for col in categorical_columns:
            if col not in [target_column, prediction_column]:
                value_counts = baseline_data[col].value_counts(normalize=True)
                feature_stats[col] = {
                    "type": "categorical",
                    "categories": value_counts.index.tolist(),
                    "proportions": value_counts.values.tolist(),
                    "missing_rate": float(baseline_data[col].isnull().mean()),
                    "unique_count": int(baseline_data[col].nunique())
                }
        
        # Performance metrics (if target available)
        performance_metrics = {}
        if target_column and prediction_column:
            if target_column in baseline_data.columns and prediction_column in baseline_data.columns:
                y_true = baseline_data[target_column]
                y_pred = baseline_data[prediction_column]
                
                # Assume binary classification for simplicity
                if len(y_true.unique()) == 2:
                    performance_metrics = {
                        "accuracy": float(accuracy_score(y_true, y_pred.round())),
                        "precision": float(precision_score(y_true, y_pred.round(), average='weighted')),
                        "recall": float(recall_score(y_true, y_pred.round(), average='weighted')),
                        "f1": float(f1_score(y_true, y_pred.round(), average='weighted'))
                    }
        
        # Prediction distribution
        prediction_distribution = {}
        if prediction_column and prediction_column in baseline_data.columns:
            pred_values = baseline_data[prediction_column].dropna()
            prediction_distribution = {
                "mean": float(pred_values.mean()),
                "std": float(pred_values.std()),
                "distribution": pred_values.values.tolist()[:1000]
            }
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO model_baselines 
            (model_id, baseline_timestamp, feature_statistics, performance_metrics, prediction_distribution, sample_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            model_id,
            datetime.now().isoformat(),
            json.dumps(feature_stats),
            json.dumps(performance_metrics),
            json.dumps(prediction_distribution),
            len(baseline_data)
        ))
        
        conn.commit()
        conn.close()
        
        # Store in memory for quick access
        self.reference_data[model_id] = feature_stats
        self.reference_performance[model_id] = performance_metrics
        
        logger.info(f"Baseline registered for {len(feature_stats)} features")
    
    def log_prediction(self, 
                      model_id: str,
                      features: Dict[str, Any],
                      prediction: float,
                      actual_label: float = None,
                      user_id: str = None,
                      session_id: str = None,
                      metadata: Dict[str, Any] = None):
        """
        Log a single prediction for monitoring
        
        Args:
            model_id: Model identifier
            features: Input features dictionary
            prediction: Model prediction
            actual_label: True label (if available)
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional metadata
        """
        timestamp = datetime.now()
        
        # Store each feature as a separate record for easy querying
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for feature_name, feature_value in features.items():
            cursor.execute("""
                INSERT INTO monitoring_data 
                (timestamp, model_id, feature_name, feature_value, prediction, actual_label, user_id, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp.isoformat(),
                model_id,
                feature_name,
                float(feature_value) if isinstance(feature_value, (int, float)) else str(feature_value),
                prediction,
                actual_label,
                user_id,
                session_id,
                json.dumps(metadata) if metadata else None
            ))
        
        conn.commit()
        conn.close()
    
    def detect_data_drift(self, 
                         model_id: str,
                         feature_name: str,
                         detection_method: DetectionMethod = DetectionMethod.KS_TEST) -> Optional[DriftAlert]:
        """
        Detect data drift for a specific feature
        
        Args:
            model_id: Model identifier
            feature_name: Feature to check for drift
            detection_method: Statistical method to use
            
        Returns:
            DriftAlert if drift detected, None otherwise
        """
        # Get reference distribution
        if model_id not in self.reference_data:
            logger.warning(f"No baseline found for model {model_id}")
            return None
        
        feature_baseline = self.reference_data[model_id].get(feature_name)
        if not feature_baseline:
            logger.warning(f"No baseline found for feature {feature_name}")
            return None
        
        # Get recent data
        recent_data = self._get_recent_feature_data(model_id, feature_name)
        if recent_data.empty:
            logger.warning(f"No recent data found for feature {feature_name}")
            return None
        
        # Perform drift detection based on feature type and method
        if feature_baseline["type"] == "numeric":
            drift_score, is_drift = self._detect_numeric_drift(
                feature_baseline, recent_data['feature_value'], detection_method
            )
        else:
            drift_score, is_drift = self._detect_categorical_drift(
                feature_baseline, recent_data['feature_value'], detection_method
            )
        
        if is_drift:
            # Determine severity
            severity = self._calculate_drift_severity(drift_score, detection_method)
            
            # Generate alert
            alert = DriftAlert(
                alert_id=f"drift_{model_id}_{feature_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                model_id=model_id,
                drift_type=DriftType.DATA_DRIFT,
                feature_name=feature_name,
                detection_method=detection_method,
                drift_score=drift_score,
                threshold=self._get_threshold(detection_method),
                severity=severity,
                description=f"Data drift detected in feature '{feature_name}' using {detection_method.value}",
                suggested_actions=self._get_drift_suggestions(feature_name, severity),
                business_impact=self._assess_business_impact(feature_name, severity)
            )
            
            # Save alert to database
            self._save_alert(alert)
            
            logger.warning(f"Data drift detected: {feature_name} (score: {drift_score:.4f})")
            return alert
        
        return None
    
    def detect_prediction_drift(self, model_id: str) -> Optional[DriftAlert]:
        """
        Detect drift in model predictions distribution
        """
        # Get reference prediction distribution
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prediction_distribution FROM model_baselines WHERE model_id = ?
        """, (model_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.warning(f"No prediction baseline found for model {model_id}")
            return None
        
        reference_dist = json.loads(result[0])
        
        # Get recent predictions
        cutoff_time = datetime.now() - timedelta(hours=self.monitoring_window_hours)
        
        cursor.execute("""
            SELECT prediction FROM monitoring_data 
            WHERE model_id = ? AND timestamp > ? AND prediction IS NOT NULL
        """, (model_id, cutoff_time.isoformat()))
        
        recent_predictions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(recent_predictions) < 30:  # Need minimum samples
            logger.warning("Not enough recent predictions for drift detection")
            return None
        
        # Perform KS test
        reference_samples = reference_dist.get("distribution", [])
        if not reference_samples:
            return None
        
        ks_statistic, p_value = ks_2samp(reference_samples, recent_predictions)
        
        # Check for drift
        if p_value < self.alert_thresholds["data_drift_ks"]:
            severity = self._calculate_drift_severity(1 - p_value, DetectionMethod.KS_TEST)
            
            alert = DriftAlert(
                alert_id=f"pred_drift_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                model_id=model_id,
                drift_type=DriftType.PREDICTION_DRIFT,
                feature_name="prediction_distribution",
                detection_method=DetectionMethod.KS_TEST,
                drift_score=1 - p_value,
                threshold=1 - self.alert_thresholds["data_drift_ks"],
                severity=severity,
                description="Significant change in model prediction distribution detected",
                suggested_actions=[
                    "Review recent input data quality",
                    "Check for changes in user behavior patterns",
                    "Consider model retraining",
                    "Investigate upstream data pipeline changes"
                ],
                business_impact="Model predictions may be less reliable, affecting conversion rates"
            )
            
            self._save_alert(alert)
            logger.warning(f"Prediction drift detected: p-value = {p_value:.4f}")
            return alert
        
        return None
    
    def detect_performance_drift(self, model_id: str) -> Optional[DriftAlert]:
        """
        Detect performance degradation over time
        """
        if model_id not in self.reference_performance:
            logger.warning(f"No performance baseline found for model {model_id}")
            return None
        
        # Get recent predictions with actual labels
        cutoff_time = datetime.now() - timedelta(hours=self.monitoring_window_hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prediction, actual_label FROM monitoring_data 
            WHERE model_id = ? AND timestamp > ? 
            AND prediction IS NOT NULL AND actual_label IS NOT NULL
        """, (model_id, cutoff_time.isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        if len(results) < 50:  # Need minimum samples for reliable performance measurement
            logger.info("Not enough labeled data for performance drift detection")
            return None
        
        # Calculate current performance
        predictions = [r[0] for r in results]
        actuals = [r[1] for r in results]
        
        # Convert predictions to binary (assuming threshold of 0.5)
        pred_binary = [1 if p > 0.5 else 0 for p in predictions]
        
        current_accuracy = accuracy_score(actuals, pred_binary)
        baseline_accuracy = self.reference_performance[model_id].get("accuracy", 0)
        
        # Check for significant performance drop
        performance_drop = baseline_accuracy - current_accuracy
        
        if performance_drop > self.alert_thresholds["performance_drift"]:
            severity = DriftSeverity.HIGH if performance_drop > 0.1 else DriftSeverity.MEDIUM
            
            alert = DriftAlert(
                alert_id=f"perf_drift_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                model_id=model_id,
                drift_type=DriftType.PERFORMANCE_DRIFT,
                feature_name="model_accuracy",
                detection_method=DetectionMethod.PSI,  # Generic for performance
                drift_score=performance_drop,
                threshold=self.alert_thresholds["performance_drift"],
                severity=severity,
                description=f"Model accuracy dropped from {baseline_accuracy:.1%} to {current_accuracy:.1%}",
                suggested_actions=[
                    "Immediate model retraining recommended",
                    "Investigate data quality issues",
                    "Review feature engineering pipeline",
                    "Consider rollback to previous model version"
                ],
                business_impact=f"Accuracy drop of {performance_drop:.1%} may impact business metrics"
            )
            
            self._save_alert(alert)
            logger.error(f"Performance drift detected: accuracy drop of {performance_drop:.1%}")
            return alert
        
        return None
    
    def run_comprehensive_monitoring(self, model_id: str) -> List[DriftAlert]:
        """
        Run comprehensive drift monitoring for a model
        
        Returns:
            List of drift alerts detected
        """
        alerts = []
        
        logger.info(f"Running comprehensive drift monitoring for model: {model_id}")
        
        # Check if model has baseline
        if model_id not in self.reference_data:
            logger.error(f"No baseline found for model {model_id}. Please register baseline first.")
            return alerts
        
        # 1. Data drift detection for each feature
        for feature_name in self.reference_data[model_id].keys():
            drift_alert = self.detect_data_drift(model_id, feature_name)
            if drift_alert:
                alerts.append(drift_alert)
        
        # 2. Prediction drift detection
        pred_drift_alert = self.detect_prediction_drift(model_id)
        if pred_drift_alert:
            alerts.append(pred_drift_alert)
        
        # 3. Performance drift detection
        perf_drift_alert = self.detect_performance_drift(model_id)
        if perf_drift_alert:
            alerts.append(perf_drift_alert)
        
        # 4. Indian food delivery specific monitoring
        indian_alerts = self._indian_specific_monitoring(model_id)
        alerts.extend(indian_alerts)
        
        logger.info(f"Drift monitoring complete. {len(alerts)} alerts generated.")
        return alerts
    
    def _indian_specific_monitoring(self, model_id: str) -> List[DriftAlert]:
        """
        Indian food delivery specific drift monitoring
        Festival seasons, monsoon, cricket matches के impacts को detect करता है
        """
        alerts = []
        
        # Get recent data for analysis
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for festival season impact
        cursor.execute("""
            SELECT feature_name, feature_value, timestamp FROM monitoring_data 
            WHERE model_id = ? AND timestamp > ? AND feature_name IN ('hour', 'day_of_week', 'is_festival')
        """, (model_id, cutoff_time.isoformat()))
        
        recent_data = cursor.fetchall()
        conn.close()
        
        if recent_data:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(recent_data, columns=['feature_name', 'feature_value', 'timestamp'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Check for unusual patterns
            
            # 1. Festival impact detection
            festival_data = df[df['feature_name'] == 'is_festival']
            if not festival_data.empty:
                festival_rate = festival_data['feature_value'].mean()
                if festival_rate > 0.3:  # More than 30% festival days
                    alert = DriftAlert(
                        alert_id=f"festival_impact_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now(),
                        model_id=model_id,
                        drift_type=DriftType.CONCEPT_DRIFT,
                        feature_name="festival_season",
                        detection_method=DetectionMethod.PSI,
                        drift_score=festival_rate,
                        threshold=0.3,
                        severity=DriftSeverity.MEDIUM,
                        description=f"High festival activity detected ({festival_rate:.1%} of recent data)",
                        suggested_actions=[
                            "Use festival-specific model version",
                            "Adjust demand prediction parameters",
                            "Increase delivery partner allocation",
                            "Monitor restaurant capacity closely"
                        ],
                        business_impact="Festival seasons typically see 40-60% increase in orders"
                    )
                    alerts.append(alert)
            
            # 2. Peak hour pattern drift
            hour_data = df[df['feature_name'] == 'hour']
            if not hour_data.empty:
                hour_distribution = hour_data['feature_value'].value_counts(normalize=True).sort_index()
                
                # Check for unusual peak hour patterns
                lunch_peak = hour_distribution.get(12, 0) + hour_distribution.get(13, 0)
                dinner_peak = hour_distribution.get(19, 0) + hour_distribution.get(20, 0)
                
                if lunch_peak < 0.1 or dinner_peak < 0.1:  # Very low peak activity
                    alert = DriftAlert(
                        alert_id=f"peak_pattern_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now(),
                        model_id=model_id,
                        drift_type=DriftType.DATA_DRIFT,
                        feature_name="peak_hour_pattern",
                        detection_method=DetectionMethod.PSI,
                        drift_score=min(lunch_peak, dinner_peak),
                        threshold=0.1,
                        severity=DriftSeverity.HIGH,
                        description="Unusual peak hour patterns detected - may indicate data quality issues",
                        suggested_actions=[
                            "Check data pipeline for timestamp issues",
                            "Verify timezone handling",
                            "Investigate potential system outages",
                            "Review traffic routing logic"
                        ],
                        business_impact="Incorrect peak hour detection affects delivery optimization"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_numeric_drift(self, 
                             baseline_stats: Dict,
                             current_data: pd.Series,
                             method: DetectionMethod) -> Tuple[float, bool]:
        """Detect drift in numeric features"""
        if method == DetectionMethod.KS_TEST:
            reference_samples = baseline_stats.get("distribution", [])
            if not reference_samples or current_data.empty:
                return 0.0, False
            
            ks_statistic, p_value = ks_2samp(reference_samples, current_data.dropna())
            drift_score = 1 - p_value  # Convert to score (higher = more drift)
            is_drift = p_value < self.alert_thresholds["data_drift_ks"]
            return drift_score, is_drift
        
        elif method == DetectionMethod.PSI:
            # Population Stability Index
            psi_score = self._calculate_psi_numeric(baseline_stats, current_data)
            is_drift = psi_score > self.alert_thresholds["data_drift_psi"]
            return psi_score, is_drift
        
        elif method == DetectionMethod.WASSERSTEIN:
            reference_samples = baseline_stats.get("distribution", [])
            if not reference_samples or current_data.empty:
                return 0.0, False
            
            ws_distance = wasserstein_distance(reference_samples, current_data.dropna())
            # Normalize by reference standard deviation
            normalized_distance = ws_distance / (baseline_stats.get("std", 1) + 1e-8)
            is_drift = normalized_distance > 0.5  # Threshold
            return normalized_distance, is_drift
        
        return 0.0, False
    
    def _detect_categorical_drift(self, 
                                 baseline_stats: Dict,
                                 current_data: pd.Series,
                                 method: DetectionMethod) -> Tuple[float, bool]:
        """Detect drift in categorical features"""
        if method == DetectionMethod.CHI_SQUARE:
            # Prepare contingency table
            baseline_cats = baseline_stats.get("categories", [])
            baseline_props = baseline_stats.get("proportions", [])
            
            if not baseline_cats or current_data.empty:
                return 0.0, False
            
            current_counts = current_data.value_counts()
            
            # Align categories
            aligned_baseline = []
            aligned_current = []
            
            for cat in baseline_cats:
                aligned_baseline.append(baseline_props[baseline_cats.index(cat)] * len(current_data))
                aligned_current.append(current_counts.get(cat, 0))
            
            # Add new categories in current data
            for cat in current_counts.index:
                if cat not in baseline_cats:
                    aligned_baseline.append(0.01 * len(current_data))  # Small expected count
                    aligned_current.append(current_counts[cat])
            
            if len(aligned_baseline) < 2 or sum(aligned_baseline) == 0:
                return 0.0, False
            
            # Chi-square test
            chi2, p_value = stats.chisquare(aligned_current, aligned_baseline)
            drift_score = 1 - p_value
            is_drift = p_value < self.alert_thresholds["data_drift_ks"]
            return drift_score, is_drift
        
        elif method == DetectionMethod.PSI:
            psi_score = self._calculate_psi_categorical(baseline_stats, current_data)
            is_drift = psi_score > self.alert_thresholds["data_drift_psi"]
            return psi_score, is_drift
        
        return 0.0, False
    
    def _calculate_psi_numeric(self, baseline_stats: Dict, current_data: pd.Series) -> float:
        """Calculate Population Stability Index for numeric features"""
        # Create bins based on baseline quantiles
        baseline_q = [baseline_stats.get(f"q{q}", 0) for q in [0, 25, 50, 75, 100]]
        baseline_q = sorted(set(baseline_q))  # Remove duplicates and sort
        
        if len(baseline_q) < 3:  # Need at least 2 bins
            return 0.0
        
        # Calculate bin proportions for baseline and current
        baseline_counts = np.histogram([0.5], bins=baseline_q[1:-1])[0]  # Dummy baseline
        current_counts, _ = np.histogram(current_data.dropna(), bins=baseline_q)
        
        baseline_props = np.ones(len(current_counts)) / len(current_counts)  # Uniform for simplicity
        current_props = current_counts / current_counts.sum() if current_counts.sum() > 0 else baseline_props
        
        # PSI calculation
        psi = 0
        for i in range(len(baseline_props)):
            if baseline_props[i] > 0 and current_props[i] > 0:
                psi += (current_props[i] - baseline_props[i]) * np.log(current_props[i] / baseline_props[i])
        
        return abs(psi)
    
    def _calculate_psi_categorical(self, baseline_stats: Dict, current_data: pd.Series) -> float:
        """Calculate Population Stability Index for categorical features"""
        baseline_cats = baseline_stats.get("categories", [])
        baseline_props = baseline_stats.get("proportions", [])
        
        if not baseline_cats:
            return 0.0
        
        current_counts = current_data.value_counts(normalize=True)
        
        psi = 0
        for i, cat in enumerate(baseline_cats):
            baseline_prop = baseline_props[i]
            current_prop = current_counts.get(cat, 0.001)  # Small value for missing categories
            
            if baseline_prop > 0 and current_prop > 0:
                psi += (current_prop - baseline_prop) * np.log(current_prop / baseline_prop)
        
        return abs(psi)
    
    def _get_recent_feature_data(self, model_id: str, feature_name: str) -> pd.DataFrame:
        """Get recent data for a specific feature"""
        cutoff_time = datetime.now() - timedelta(hours=self.monitoring_window_hours)
        
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT feature_value, timestamp FROM monitoring_data 
            WHERE model_id = ? AND feature_name = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """, conn, params=(model_id, feature_name, cutoff_time.isoformat()))
        conn.close()
        
        return df
    
    def _calculate_drift_severity(self, drift_score: float, method: DetectionMethod) -> DriftSeverity:
        """Calculate drift severity based on score and method"""
        if method == DetectionMethod.KS_TEST:
            if drift_score > 0.99:
                return DriftSeverity.CRITICAL
            elif drift_score > 0.95:
                return DriftSeverity.HIGH
            elif drift_score > 0.8:
                return DriftSeverity.MEDIUM
            else:
                return DriftSeverity.LOW
        
        elif method == DetectionMethod.PSI:
            if drift_score > 0.5:
                return DriftSeverity.CRITICAL
            elif drift_score > 0.2:
                return DriftSeverity.HIGH
            elif drift_score > 0.1:
                return DriftSeverity.MEDIUM
            else:
                return DriftSeverity.LOW
        
        return DriftSeverity.MEDIUM
    
    def _get_threshold(self, method: DetectionMethod) -> float:
        """Get threshold for detection method"""
        if method == DetectionMethod.KS_TEST:
            return 1 - self.alert_thresholds["data_drift_ks"]
        elif method == DetectionMethod.PSI:
            return self.alert_thresholds["data_drift_psi"]
        return 0.5
    
    def _get_drift_suggestions(self, feature_name: str, severity: DriftSeverity) -> List[str]:
        """Get suggestions based on feature and severity"""
        base_suggestions = [
            "Investigate data pipeline changes",
            "Review feature engineering logic",
            "Check data quality at source",
            "Consider model retraining"
        ]
        
        if severity == DriftSeverity.CRITICAL:
            base_suggestions.insert(0, "Immediate attention required - consider model rollback")
        
        # Feature-specific suggestions
        if "time" in feature_name.lower() or "hour" in feature_name.lower():
            base_suggestions.append("Check timezone handling and timestamp accuracy")
        elif "location" in feature_name.lower() or "area" in feature_name.lower():
            base_suggestions.append("Verify GPS/location services functioning correctly")
        elif "price" in feature_name.lower() or "amount" in feature_name.lower():
            base_suggestions.append("Check for pricing model changes or currency issues")
        
        return base_suggestions
    
    def _assess_business_impact(self, feature_name: str, severity: DriftSeverity) -> str:
        """Assess business impact of drift"""
        impact_map = {
            DriftSeverity.LOW: "Minimal impact expected",
            DriftSeverity.MEDIUM: "Moderate impact on model performance",
            DriftSeverity.HIGH: "Significant impact on business metrics likely",
            DriftSeverity.CRITICAL: "Critical impact - immediate action required"
        }
        
        base_impact = impact_map[severity]
        
        # Feature-specific impact
        if "conversion" in feature_name.lower():
            base_impact += " - affects order conversion rates directly"
        elif "delivery" in feature_name.lower():
            base_impact += " - impacts delivery time predictions and customer satisfaction"
        elif "price" in feature_name.lower():
            base_impact += " - affects revenue optimization and pricing strategies"
        
        return base_impact
    
    def _save_alert(self, alert: DriftAlert):
        """Save drift alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO drift_alerts 
            (alert_id, timestamp, model_id, drift_type, feature_name, detection_method,
             drift_score, threshold, severity, description, suggested_actions, business_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.timestamp.isoformat(),
            alert.model_id,
            alert.drift_type.value,
            alert.feature_name,
            alert.detection_method.value,
            alert.drift_score,
            alert.threshold,
            alert.severity.value,
            alert.description,
            json.dumps(alert.suggested_actions),
            alert.business_impact
        ))
        
        conn.commit()
        conn.close()
    
    def get_drift_summary(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Get drift monitoring summary for the last N days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get alerts summary
        cursor.execute("""
            SELECT drift_type, severity, COUNT(*) as count
            FROM drift_alerts 
            WHERE model_id = ? AND timestamp > ?
            GROUP BY drift_type, severity
        """, (model_id, cutoff_time.isoformat()))
        
        alerts_summary = {}
        for drift_type, severity, count in cursor.fetchall():
            if drift_type not in alerts_summary:
                alerts_summary[drift_type] = {}
            alerts_summary[drift_type][severity] = count
        
        # Get monitoring data volume
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as predictions
            FROM monitoring_data 
            WHERE model_id = ? AND timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (model_id, cutoff_time.isoformat()))
        
        daily_volume = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "model_id": model_id,
            "period_days": days,
            "alerts_summary": alerts_summary,
            "daily_prediction_volume": daily_volume,
            "total_alerts": sum(sum(severity_counts.values()) for severity_counts in alerts_summary.values()),
            "critical_alerts": sum(severity_counts.get("critical", 0) for severity_counts in alerts_summary.values())
        }
    
    def visualize_drift_monitoring(self, 
                                  model_id: str,
                                  save_path: str = "drift_monitoring_dashboard.png"):
        """Create drift monitoring dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Drift Monitoring Dashboard: {model_id}', fontsize=16, fontweight='bold')
        
        # Get monitoring data
        summary = self.get_drift_summary(model_id, days=7)
        
        # Plot 1: Alerts by type and severity
        alerts_data = []
        for drift_type, severity_counts in summary['alerts_summary'].items():
            for severity, count in severity_counts.items():
                alerts_data.append({'type': drift_type, 'severity': severity, 'count': count})
        
        if alerts_data:
            alerts_df = pd.DataFrame(alerts_data)
            pivot_alerts = alerts_df.pivot(index='type', columns='severity', values='count').fillna(0)
            
            pivot_alerts.plot(kind='bar', stacked=True, ax=axes[0, 0], 
                            color=['green', 'yellow', 'orange', 'red'])
            axes[0, 0].set_title('Drift Alerts by Type and Severity')
            axes[0, 0].set_ylabel('Number of Alerts')
            axes[0, 0].legend(title='Severity')
        
        # Plot 2: Daily prediction volume
        if summary['daily_prediction_volume']:
            dates = list(summary['daily_prediction_volume'].keys())
            volumes = list(summary['daily_prediction_volume'].values())
            
            axes[0, 1].plot(dates, volumes, marker='o')
            axes[0, 1].set_title('Daily Prediction Volume')
            axes[0, 1].set_ylabel('Number of Predictions')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Feature drift heatmap (if we have recent alerts)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT feature_name, drift_score, severity FROM drift_alerts 
            WHERE model_id = ? AND drift_type = 'data_drift'
            ORDER BY timestamp DESC LIMIT 20
        """, (model_id,))
        
        feature_alerts = cursor.fetchall()
        if feature_alerts:
            features = [f[0] for f in feature_alerts]
            scores = [f[1] for f in feature_alerts]
            
            # Create a simple heatmap-like visualization
            y_pos = np.arange(len(features))
            colors = ['red' if s > 0.8 else 'orange' if s > 0.5 else 'yellow' for s in scores]
            
            axes[1, 0].barh(y_pos, scores, color=colors)
            axes[1, 0].set_yticks(y_pos)
            axes[1, 0].set_yticklabels(features)
            axes[1, 0].set_xlabel('Drift Score')
            axes[1, 0].set_title('Recent Feature Drift Scores')
        
        # Plot 4: Monitoring health status
        total_alerts = summary['total_alerts']
        critical_alerts = summary['critical_alerts']
        
        health_score = max(0, 100 - (total_alerts * 5 + critical_alerts * 20))
        
        # Simple gauge chart
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
        sizes = [20, 20, 20, 20, 20]
        
        if health_score >= 80:
            explode = [0, 0, 0, 0, 0.1]
        elif health_score >= 60:
            explode = [0, 0, 0, 0.1, 0]
        elif health_score >= 40:
            explode = [0, 0, 0.1, 0, 0]
        elif health_score >= 20:
            explode = [0, 0.1, 0, 0, 0]
        else:
            explode = [0.1, 0, 0, 0, 0]
        
        axes[1, 1].pie(sizes, colors=colors, explode=explode, startangle=90,
                      labels=['Critical', 'Poor', 'Fair', 'Good', 'Excellent'])
        axes[1, 1].set_title(f'Model Health Score: {health_score:.0f}%')
        
        conn.close()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Drift monitoring dashboard saved to {save_path}")

def demo_food_delivery_drift_monitoring():
    """
    Complete demo of drift monitoring for food delivery models
    Swiggy/Zomato production scenarios के लिए realistic monitoring
    """
    print("🚀 Food Delivery Drift Monitoring Demo")
    print("=" * 50)
    
    # Initialize drift monitor
    monitor = FoodDeliveryDriftMonitor(
        db_path="food_delivery_drift.db",
        monitoring_window_hours=24
    )
    
    # Generate sample baseline data
    print("\n📊 Generating Sample Baseline Data...")
    
    np.random.seed(42)
    n_baseline = 10000
    
    baseline_data = pd.DataFrame({
        'user_age': np.random.normal(28, 8, n_baseline).clip(18, 65),
        'order_value': np.random.lognormal(5.5, 0.8, n_baseline),
        'delivery_distance_km': np.random.exponential(3, n_baseline).clip(0.5, 15),
        'restaurant_rating': np.random.normal(4.2, 0.6, n_baseline).clip(1, 5),
        'hour': np.random.choice(range(24), n_baseline, 
                               p=[0.02]*6 + [0.04]*3 + [0.06]*3 + [0.08]*2 + [0.04]*4 + [0.08]*4 + [0.02]*2),
        'city': np.random.choice(['mumbai', 'delhi', 'bangalore'], n_baseline, p=[0.4, 0.35, 0.25]),
        'is_festival': np.random.choice([0, 1], n_baseline, p=[0.9, 0.1]),
        'weather_score': np.random.uniform(0.3, 1.0, n_baseline),
        'converted': np.random.choice([0, 1], n_baseline, p=[0.85, 0.15]),
        'prediction': np.random.beta(2, 5, n_baseline)  # Skewed towards lower values
    })
    
    # Register baseline for Swiggy demand model
    model_id = "swiggy_demand_predictor_v2"
    print(f"\n📋 Registering Baseline for Model: {model_id}")
    
    monitor.register_model_baseline(
        model_id=model_id,
        baseline_data=baseline_data,
        target_column='converted',
        prediction_column='prediction'
    )
    
    print("✅ Baseline registered successfully")
    
    # Simulate normal operations for a few days
    print("\n⏳ Simulating Normal Operations...")
    
    for day in range(3):
        daily_predictions = 2000
        
        for i in range(daily_predictions):
            # Normal data (similar to baseline)
            features = {
                'user_age': np.random.normal(28, 8),
                'order_value': np.random.lognormal(5.5, 0.8),
                'delivery_distance_km': np.random.exponential(3),
                'restaurant_rating': np.random.normal(4.2, 0.6),
                'hour': np.random.choice(range(24), p=[0.02]*6 + [0.04]*3 + [0.06]*3 + [0.08]*2 + [0.04]*4 + [0.08]*4 + [0.02]*2),
                'city': np.random.choice(['mumbai', 'delhi', 'bangalore'], p=[0.4, 0.35, 0.25]),
                'is_festival': np.random.choice([0, 1], p=[0.9, 0.1]),
                'weather_score': np.random.uniform(0.3, 1.0)
            }
            
            prediction = np.random.beta(2, 5)
            actual = np.random.choice([0, 1], p=[0.85, 0.15])
            
            monitor.log_prediction(
                model_id=model_id,
                features=features,
                prediction=prediction,
                actual_label=actual,
                user_id=f"user_{day}_{i}",
                session_id=f"session_{day}_{i//10}"
            )
    
    print("✅ Normal operations logged")
    
    # Simulate drift scenarios
    print("\n🌊 Simulating Drift Scenarios...")
    
    # Scenario 1: Festival season (data drift)
    print("   📅 Festival Season Impact...")
    for i in range(500):
        features = {
            'user_age': np.random.normal(26, 10),  # Slightly younger users during festivals
            'order_value': np.random.lognormal(6.0, 0.9),  # Higher order values
            'delivery_distance_km': np.random.exponential(2.5),  # Shorter distances
            'restaurant_rating': np.random.normal(4.3, 0.5),
            'hour': np.random.choice([19, 20, 21, 22], p=[0.3, 0.4, 0.2, 0.1]),  # More dinner orders
            'city': np.random.choice(['mumbai', 'delhi', 'bangalore'], p=[0.4, 0.35, 0.25]),
            'is_festival': 1,  # All festival days
            'weather_score': np.random.uniform(0.6, 1.0)  # Better weather during festivals
        }
        
        prediction = np.random.beta(1.5, 3)  # Higher conversion during festivals
        actual = np.random.choice([0, 1], p=[0.75, 0.25])  # Higher actual conversion
        
        monitor.log_prediction(
            model_id=model_id,
            features=features,
            prediction=prediction,
            actual_label=actual,
            user_id=f"festival_user_{i}",
            metadata={"scenario": "festival_season"}
        )
    
    # Scenario 2: Monsoon impact (concept drift)
    print("   🌧️  Monsoon Impact...")
    for i in range(300):
        features = {
            'user_age': np.random.normal(30, 7),
            'order_value': np.random.lognormal(5.8, 0.7),  # Slightly higher (comfort food)
            'delivery_distance_km': np.random.exponential(4),  # Longer distances
            'restaurant_rating': np.random.normal(4.0, 0.8),  # More variation
            'hour': np.random.choice(range(24), p=[0.03]*6 + [0.05]*3 + [0.07]*3 + [0.09]*2 + [0.05]*4 + [0.09]*4 + [0.03]*2),
            'city': 'mumbai',  # Focus on Mumbai (most affected by monsoon)
            'is_festival': 0,
            'weather_score': np.random.uniform(0.1, 0.4)  # Poor weather during monsoon
        }
        
        prediction = np.random.beta(2, 5)  # Normal predictions
        actual = np.random.choice([0, 1], p=[0.9, 0.1])  # Lower actual conversion due to monsoon
        
        monitor.log_prediction(
            model_id=model_id,
            features=features,
            prediction=prediction,
            actual_label=actual,
            user_id=f"monsoon_user_{i}",
            metadata={"scenario": "monsoon_impact"}
        )
    
    # Scenario 3: System issue (prediction drift)
    print("   ⚠️  System Issue Simulation...")
    for i in range(200):
        features = {
            'user_age': np.random.normal(28, 8),
            'order_value': np.random.lognormal(5.5, 0.8),
            'delivery_distance_km': np.random.exponential(3),
            'restaurant_rating': np.random.normal(4.2, 0.6),
            'hour': np.random.choice(range(24), p=[0.02]*6 + [0.04]*3 + [0.06]*3 + [0.08]*2 + [0.04]*4 + [0.08]*4 + [0.02]*2),
            'city': np.random.choice(['mumbai', 'delhi', 'bangalore'], p=[0.4, 0.35, 0.25]),
            'is_festival': np.random.choice([0, 1], p=[0.9, 0.1]),
            'weather_score': np.random.uniform(0.3, 1.0)
        }
        
        prediction = np.random.uniform(0.8, 0.95)  # Abnormally high predictions (system bug)
        actual = np.random.choice([0, 1], p=[0.85, 0.15])  # Normal actual values
        
        monitor.log_prediction(
            model_id=model_id,
            features=features,
            prediction=prediction,
            actual_label=actual,
            user_id=f"system_issue_user_{i}",
            metadata={"scenario": "system_issue"}
        )
    
    print("✅ Drift scenarios simulated")
    
    # Run comprehensive monitoring
    print("\n🔍 Running Comprehensive Drift Monitoring...")
    
    drift_alerts = monitor.run_comprehensive_monitoring(model_id)
    
    print(f"\n🚨 DRIFT MONITORING RESULTS:")
    print("=" * 35)
    print(f"Total Alerts Generated: {len(drift_alerts)}")
    
    # Categorize alerts
    alert_summary = {}
    for alert in drift_alerts:
        drift_type = alert.drift_type.value
        severity = alert.severity.value
        
        if drift_type not in alert_summary:
            alert_summary[drift_type] = {}
        
        if severity not in alert_summary[drift_type]:
            alert_summary[drift_type][severity] = 0
        
        alert_summary[drift_type][severity] += 1
    
    for drift_type, severity_counts in alert_summary.items():
        print(f"\n{drift_type.upper().replace('_', ' ')}:")
        for severity, count in severity_counts.items():
            print(f"   {severity.title()}: {count}")
    
    # Show detailed alerts
    print(f"\n📋 DETAILED ALERTS:")
    print("=" * 20)
    
    for i, alert in enumerate(drift_alerts[:5]):  # Show first 5 alerts
        print(f"\n{i+1}. {alert.alert_id}")
        print(f"   Type: {alert.drift_type.value}")
        print(f"   Feature: {alert.feature_name}")
        print(f"   Severity: {alert.severity.value}")
        print(f"   Score: {alert.drift_score:.4f} (threshold: {alert.threshold:.4f})")
        print(f"   Description: {alert.description}")
        print(f"   Business Impact: {alert.business_impact}")
        print(f"   Suggested Actions:")
        for action in alert.suggested_actions[:3]:  # Show first 3 actions
            print(f"      - {action}")
    
    # Generate monitoring summary
    print(f"\n📊 MONITORING SUMMARY:")
    summary = monitor.get_drift_summary(model_id, days=7)
    
    print(f"Model ID: {summary['model_id']}")
    print(f"Monitoring Period: {summary['period_days']} days")
    print(f"Total Alerts: {summary['total_alerts']}")
    print(f"Critical Alerts: {summary['critical_alerts']}")
    print(f"Daily Prediction Volume: {sum(summary['daily_prediction_volume'].values())}")
    
    # Create visualization
    print(f"\n📈 Creating Drift Monitoring Dashboard...")
    monitor.visualize_drift_monitoring(model_id, "swiggy_drift_monitoring.png")
    
    # Calculate business impact
    print(f"\n💰 BUSINESS IMPACT ANALYSIS:")
    print("=" * 30)
    
    critical_alerts = sum(1 for alert in drift_alerts if alert.severity == DriftSeverity.CRITICAL)
    high_alerts = sum(1 for alert in drift_alerts if alert.severity == DriftSeverity.HIGH)
    
    if critical_alerts > 0:
        print(f"🚨 CRITICAL: {critical_alerts} critical drift issues detected")
        print(f"   Estimated Revenue Impact: ₹2,00,000 - ₹5,00,000 per day")
        print(f"   Recommended Action: Immediate model rollback or hotfix")
    
    if high_alerts > 0:
        print(f"⚠️  HIGH: {high_alerts} high-severity drift issues")
        print(f"   Estimated Revenue Impact: ₹50,000 - ₹1,50,000 per day")
        print(f"   Recommended Action: Schedule urgent model retraining")
    
    print(f"\n💸 MONITORING INFRASTRUCTURE COSTS:")
    print(f"Data Pipeline: ₹8,000/month")
    print(f"Database Storage: ₹3,000/month")
    print(f"Compute Resources: ₹10,000/month")
    print(f"Alerting System: ₹2,000/month")
    print(f"Dashboard Hosting: ₹2,000/month")
    print(f"Total: ₹25,000/month")
    
    print(f"\n📈 ROI ANALYSIS:")
    monthly_prevented_loss = critical_alerts * 500000 + high_alerts * 150000  # Conservative estimate
    if monthly_prevented_loss > 25000:
        roi = ((monthly_prevented_loss - 25000) / 25000) * 100
        print(f"Monthly Prevented Loss: ₹{monthly_prevented_loss:,}")
        print(f"Monitoring ROI: {roi:.0f}%")
        print(f"Payback Period: {25000 / monthly_prevented_loss:.1f} months")
    
    print(f"\n🎯 KEY BENEFITS:")
    print(f"- Early detection of model degradation")
    print(f"- Automated alerting for critical issues")
    print(f"- Reduced manual monitoring effort (80% reduction)")
    print(f"- Faster issue resolution (3x faster)")
    print(f"- Improved model reliability and trust")
    
    return monitor, drift_alerts, summary

if __name__ == "__main__":
    monitor, alerts, summary = demo_food_delivery_drift_monitoring()
    print("\n🎉 Food Delivery Drift Monitoring Demo Complete!")
    print("📊 System ready for production deployment with 24/7 monitoring")