#!/usr/bin/env python3
"""
Model Drift Detection System - MLOps Episode 44
Production-ready model drift detection and alerting system

Author: Claude Code
Context: Automated model drift detection for ML models in production
"""

import json
import time
import uuid
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import logging
import warnings
from collections import defaultdict, deque
import threading
from abc import ABC, abstractmethod
warnings.filterwarnings('ignore')

# Statistical imports
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"

class DriftSeverity(Enum):
    """Drift severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class DriftMetric:
    """Single drift measurement"""
    metric_name: str
    value: float
    threshold: float
    is_drift_detected: bool
    severity: DriftSeverity
    timestamp: datetime

@dataclass
class DriftAlert:
    """Drift detection alert"""
    alert_id: str
    model_id: str
    drift_type: DriftType
    severity: DriftSeverity
    metrics: List[DriftMetric]
    description: str
    recommendations: List[str]
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

@dataclass
class ModelSnapshot:
    """Snapshot of model state for comparison"""
    snapshot_id: str
    model_id: str
    timestamp: datetime
    feature_statistics: Dict[str, Dict[str, float]]
    prediction_distribution: Dict[str, float]
    performance_metrics: Dict[str, float]
    data_sample: pd.DataFrame

class DriftDetector(ABC):
    """Abstract base class for drift detectors"""
    
    @abstractmethod
    def detect_drift(self, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> List[DriftMetric]:
        pass

class KSDriftDetector(DriftDetector):
    """
    Kolmogorov-Smirnov test for data drift detection
    Mumbai me statistical drift detection!
    """
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
    
    def detect_drift(self, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> List[DriftMetric]:
        """Detect drift using KS test"""
        drift_metrics = []
        
        for column in reference_data.columns:
            if column not in current_data.columns:
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(reference_data[column]):
                continue
            
            ref_values = reference_data[column].dropna()
            curr_values = current_data[column].dropna()
            
            if len(ref_values) == 0 or len(curr_values) == 0:
                continue
            
            # Perform KS test
            ks_statistic, p_value = stats.ks_2samp(ref_values, curr_values)
            
            is_drift = p_value < self.threshold
            
            # Determine severity based on KS statistic
            if ks_statistic > 0.5:
                severity = DriftSeverity.CRITICAL
            elif ks_statistic > 0.3:
                severity = DriftSeverity.HIGH
            elif ks_statistic > 0.1:
                severity = DriftSeverity.MEDIUM
            else:
                severity = DriftSeverity.LOW
            
            metric = DriftMetric(
                metric_name=f"ks_test_{column}",
                value=ks_statistic,
                threshold=self.threshold,
                is_drift_detected=is_drift,
                severity=severity,
                timestamp=datetime.now()
            )
            
            drift_metrics.append(metric)
        
        return drift_metrics

class PSIDriftDetector(DriftDetector):
    """
    Population Stability Index (PSI) for drift detection
    Mumbai me PSI-based drift detection!
    """
    
    def __init__(self, threshold: float = 0.1, bins: int = 10):
        self.threshold = threshold
        self.bins = bins
    
    def _calculate_psi(self, expected: np.ndarray, actual: np.ndarray) -> float:
        """Calculate Population Stability Index"""
        # Create bins based on expected distribution
        bin_edges = np.percentile(expected, np.linspace(0, 100, self.bins + 1))
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf
        
        # Calculate expected and actual percentages
        expected_counts, _ = np.histogram(expected, bins=bin_edges)
        actual_counts, _ = np.histogram(actual, bins=bin_edges)
        
        expected_pct = expected_counts / len(expected)
        actual_pct = actual_counts / len(actual)
        
        # Avoid division by zero
        expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
        actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
        
        # Calculate PSI
        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        
        return psi
    
    def detect_drift(self, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> List[DriftMetric]:
        """Detect drift using PSI"""
        drift_metrics = []
        
        for column in reference_data.columns:
            if column not in current_data.columns:
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(reference_data[column]):
                continue
            
            ref_values = reference_data[column].dropna().values
            curr_values = current_data[column].dropna().values
            
            if len(ref_values) == 0 or len(curr_values) == 0:
                continue
            
            # Calculate PSI
            psi_value = self._calculate_psi(ref_values, curr_values)
            
            is_drift = psi_value > self.threshold
            
            # Determine severity based on PSI value
            if psi_value > 0.25:
                severity = DriftSeverity.CRITICAL
            elif psi_value > 0.2:
                severity = DriftSeverity.HIGH
            elif psi_value > 0.1:
                severity = DriftSeverity.MEDIUM
            else:
                severity = DriftSeverity.LOW
            
            metric = DriftMetric(
                metric_name=f"psi_{column}",
                value=psi_value,
                threshold=self.threshold,
                is_drift_detected=is_drift,
                severity=severity,
                timestamp=datetime.now()
            )
            
            drift_metrics.append(metric)
        
        return drift_metrics

class PerformanceDriftDetector(DriftDetector):
    """
    Performance-based drift detection
    Mumbai me performance monitoring!
    """
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
    
    def detect_drift(self, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> List[DriftMetric]:
        """Detect performance drift"""
        drift_metrics = []
        
        # Assuming the data contains predictions and actuals
        if 'predictions' not in reference_data.columns or 'actuals' not in reference_data.columns:
            return drift_metrics
        
        if 'predictions' not in current_data.columns or 'actuals' not in current_data.columns:
            return drift_metrics
        
        # Calculate performance metrics for both periods
        ref_accuracy = accuracy_score(reference_data['actuals'], reference_data['predictions'])
        curr_accuracy = accuracy_score(current_data['actuals'], current_data['predictions'])
        
        # Calculate drift
        accuracy_drift = abs(ref_accuracy - curr_accuracy)
        is_drift = accuracy_drift > self.threshold
        
        # Determine severity
        if accuracy_drift > 0.2:
            severity = DriftSeverity.CRITICAL
        elif accuracy_drift > 0.1:
            severity = DriftSeverity.HIGH
        elif accuracy_drift > 0.05:
            severity = DriftSeverity.MEDIUM
        else:
            severity = DriftSeverity.LOW
        
        metric = DriftMetric(
            metric_name="accuracy_drift",
            value=accuracy_drift,
            threshold=self.threshold,
            is_drift_detected=is_drift,
            severity=severity,
            timestamp=datetime.now()
        )
        
        drift_metrics.append(metric)
        
        return drift_metrics

class ModelDriftMonitor:
    """
    Production Model Drift Monitoring System
    Mumbai me sabse advanced drift monitoring!
    """
    
    def __init__(self, db_path: str = "model_drift_monitor.db"):
        self.db_path = db_path
        self.detectors = {
            DriftType.DATA_DRIFT: [
                KSDriftDetector(threshold=0.05),
                PSIDriftDetector(threshold=0.1)
            ],
            DriftType.PERFORMANCE_DRIFT: [
                PerformanceDriftDetector(threshold=0.05)
            ]
        }
        
        # Model snapshots for comparison
        self.model_snapshots: Dict[str, List[ModelSnapshot]] = defaultdict(list)
        self.drift_history: Dict[str, List[DriftAlert]] = defaultdict(list)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.lock = threading.Lock()
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[DriftAlert], None]] = []
        
        self._init_database()
    
    def _init_database(self):
        """Initialize drift monitoring database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    feature_statistics TEXT,
                    prediction_distribution TEXT,
                    performance_metrics TEXT,
                    data_sample_path TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS drift_alerts (
                    alert_id TEXT PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    drift_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    metrics TEXT,
                    description TEXT,
                    recommendations TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    acknowledged_at TEXT,
                    resolved_at TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS drift_metrics (
                    metric_id TEXT PRIMARY KEY,
                    alert_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    is_drift_detected INTEGER NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (alert_id) REFERENCES drift_alerts (alert_id)
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_model_time ON model_snapshots (model_id, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_model ON drift_alerts (model_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON drift_alerts (status)')
    
    def add_alert_callback(self, callback: Callable[[DriftAlert], None]):
        """Add callback function for drift alerts"""
        self.alert_callbacks.append(callback)
    
    def create_model_snapshot(self, model_id: str, data: pd.DataFrame, predictions: np.ndarray, actuals: np.ndarray = None) -> str:
        """
        Create snapshot of model state
        Mumbai me model ka snapshot lena!
        """
        snapshot_id = str(uuid.uuid4())
        
        # Calculate feature statistics
        feature_stats = {}
        for column in data.columns:
            if pd.api.types.is_numeric_dtype(data[column]):
                stats_dict = {
                    'mean': float(data[column].mean()),
                    'std': float(data[column].std()),
                    'min': float(data[column].min()),
                    'max': float(data[column].max()),
                    'median': float(data[column].median()),
                    'skewness': float(data[column].skew()),
                    'kurtosis': float(data[column].kurtosis()),
                    'null_count': int(data[column].isnull().sum()),
                    'unique_count': int(data[column].nunique())
                }
                feature_stats[column] = stats_dict
        
        # Prediction distribution
        if len(predictions.shape) == 1:
            # Binary or regression
            pred_dist = {
                'mean': float(np.mean(predictions)),
                'std': float(np.std(predictions)),
                'min': float(np.min(predictions)),
                'max': float(np.max(predictions)),
                'percentiles': {
                    '25': float(np.percentile(predictions, 25)),
                    '50': float(np.percentile(predictions, 50)),
                    '75': float(np.percentile(predictions, 75)),
                    '95': float(np.percentile(predictions, 95))
                }
            }
        else:
            # Multi-class
            pred_dist = {
                'class_distribution': [float(x) for x in np.mean(predictions, axis=0)]
            }
        
        # Performance metrics
        perf_metrics = {}
        if actuals is not None:
            if len(np.unique(actuals)) <= 10:  # Classification
                perf_metrics = {
                    'accuracy': float(accuracy_score(actuals, np.argmax(predictions, axis=1) if len(predictions.shape) > 1 else predictions.round())),
                    'precision': float(precision_score(actuals, np.argmax(predictions, axis=1) if len(predictions.shape) > 1 else predictions.round(), average='weighted')),
                    'recall': float(recall_score(actuals, np.argmax(predictions, axis=1) if len(predictions.shape) > 1 else predictions.round(), average='weighted')),
                    'f1_score': float(f1_score(actuals, np.argmax(predictions, axis=1) if len(predictions.shape) > 1 else predictions.round(), average='weighted'))
                }
            else:  # Regression
                perf_metrics = {
                    'mse': float(np.mean((predictions - actuals) ** 2)),
                    'mae': float(np.mean(np.abs(predictions - actuals))),
                    'rmse': float(np.sqrt(np.mean((predictions - actuals) ** 2))),
                    'r2': float(1 - np.sum((actuals - predictions) ** 2) / np.sum((actuals - np.mean(actuals)) ** 2))
                }
        
        # Create snapshot
        snapshot = ModelSnapshot(
            snapshot_id=snapshot_id,
            model_id=model_id,
            timestamp=datetime.now(),
            feature_statistics=feature_stats,
            prediction_distribution=pred_dist,
            performance_metrics=perf_metrics,
            data_sample=data.sample(min(1000, len(data)))  # Sample for storage
        )
        
        # Store in memory and database
        with self.lock:
            self.model_snapshots[model_id].append(snapshot)
            # Keep only last 10 snapshots in memory
            if len(self.model_snapshots[model_id]) > 10:
                self.model_snapshots[model_id] = self.model_snapshots[model_id][-10:]
        
        self._store_snapshot(snapshot)
        
        logger.info(f"Created snapshot {snapshot_id} for model {model_id}")
        return snapshot_id
    
    def _store_snapshot(self, snapshot: ModelSnapshot):
        """Store snapshot in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO model_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot.snapshot_id,
                    snapshot.model_id,
                    snapshot.timestamp.isoformat(),
                    json.dumps(snapshot.feature_statistics),
                    json.dumps(snapshot.prediction_distribution),
                    json.dumps(snapshot.performance_metrics),
                    f"samples/{snapshot.snapshot_id}.parquet"  # Could save to file
                ))
        except Exception as e:
            logger.error(f"Failed to store snapshot: {e}")
    
    def detect_drift(self, model_id: str, current_data: pd.DataFrame, current_predictions: np.ndarray, current_actuals: np.ndarray = None) -> List[DriftAlert]:
        """
        Detect drift for a model
        Mumbai me drift detection ka main function!
        """
        alerts = []
        
        # Get reference snapshot
        model_snapshots = self.model_snapshots.get(model_id, [])
        if not model_snapshots:
            logger.warning(f"No reference snapshots found for model {model_id}")
            return alerts
        
        reference_snapshot = model_snapshots[-1]  # Use latest snapshot as reference
        
        # Prepare data for comparison
        reference_data = reference_snapshot.data_sample
        
        # Add predictions and actuals to current data for performance drift detection
        current_data_with_preds = current_data.copy()
        if len(current_predictions.shape) == 1:
            current_data_with_preds['predictions'] = current_predictions
        else:
            current_data_with_preds['predictions'] = np.argmax(current_predictions, axis=1)
        
        if current_actuals is not None:
            current_data_with_preds['actuals'] = current_actuals
        
        # Add predictions to reference data if available
        reference_data_with_preds = reference_data.copy()
        if 'predictions' not in reference_data_with_preds.columns and reference_snapshot.performance_metrics:
            # Simulate reference predictions (in production, these would be stored)
            if 'accuracy' in reference_snapshot.performance_metrics:
                # Classification
                n_samples = len(reference_data_with_preds)
                reference_data_with_preds['predictions'] = np.random.randint(0, 2, n_samples)
                reference_data_with_preds['actuals'] = np.random.randint(0, 2, n_samples)
        
        # Run drift detection for each type
        for drift_type, detectors in self.detectors.items():
            type_metrics = []
            
            for detector in detectors:
                if drift_type == DriftType.PERFORMANCE_DRIFT:
                    # Use data with predictions
                    if 'predictions' in reference_data_with_preds.columns and 'predictions' in current_data_with_preds.columns:
                        metrics = detector.detect_drift(reference_data_with_preds, current_data_with_preds)
                        type_metrics.extend(metrics)
                else:
                    # Use original data
                    metrics = detector.detect_drift(reference_data, current_data)
                    type_metrics.extend(metrics)
            
            # Check if any drift detected
            drift_detected_metrics = [m for m in type_metrics if m.is_drift_detected]
            
            if drift_detected_metrics:
                # Determine overall severity
                severities = [m.severity for m in drift_detected_metrics]
                if DriftSeverity.CRITICAL in severities:
                    overall_severity = DriftSeverity.CRITICAL
                elif DriftSeverity.HIGH in severities:
                    overall_severity = DriftSeverity.HIGH
                elif DriftSeverity.MEDIUM in severities:
                    overall_severity = DriftSeverity.MEDIUM
                else:
                    overall_severity = DriftSeverity.LOW
                
                # Generate recommendations
                recommendations = self._generate_recommendations(drift_type, drift_detected_metrics)
                
                # Create alert
                alert = DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    drift_type=drift_type,
                    severity=overall_severity,
                    metrics=type_metrics,
                    description=self._generate_description(drift_type, drift_detected_metrics),
                    recommendations=recommendations,
                    status=AlertStatus.ACTIVE,
                    created_at=datetime.now()
                )
                
                alerts.append(alert)
                
                # Store alert
                self._store_alert(alert)
                
                # Trigger callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Alert callback failed: {e}")
        
        return alerts
    
    def _generate_description(self, drift_type: DriftType, metrics: List[DriftMetric]) -> str:
        """Generate human-readable description"""
        if drift_type == DriftType.DATA_DRIFT:
            features = [m.metric_name.split('_')[-1] for m in metrics]
            return f"Data drift detected in features: {', '.join(features)}"
        elif drift_type == DriftType.PERFORMANCE_DRIFT:
            return f"Performance degradation detected: {metrics[0].metric_name}"
        else:
            return f"{drift_type.value} detected"
    
    def _generate_recommendations(self, drift_type: DriftType, metrics: List[DriftMetric]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if drift_type == DriftType.DATA_DRIFT:
            recommendations.extend([
                "Investigate data quality and preprocessing pipeline",
                "Check for changes in data sources or collection methods",
                "Consider retraining the model with recent data",
                "Implement feature scaling or normalization adjustments"
            ])
        elif drift_type == DriftType.PERFORMANCE_DRIFT:
            recommendations.extend([
                "Retrain model with recent data",
                "Investigate model degradation causes",
                "Consider ensemble methods or model updating",
                "Review feature engineering pipeline"
            ])
        
        # Add severity-specific recommendations
        critical_metrics = [m for m in metrics if m.severity == DriftSeverity.CRITICAL]
        if critical_metrics:
            recommendations.insert(0, "URGENT: Immediate model retraining required")
        
        return recommendations
    
    def _store_alert(self, alert: DriftAlert):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store alert
                conn.execute('''
                    INSERT INTO drift_alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    alert.model_id,
                    alert.drift_type.value,
                    alert.severity.value,
                    json.dumps([asdict(m) for m in alert.metrics], default=str),
                    alert.description,
                    json.dumps(alert.recommendations),
                    alert.status.value,
                    alert.created_at.isoformat(),
                    alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    alert.resolved_at.isoformat() if alert.resolved_at else None
                ))
                
                # Store individual metrics
                for metric in alert.metrics:
                    conn.execute('''
                        INSERT INTO drift_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        alert.alert_id,
                        metric.metric_name,
                        metric.value,
                        metric.threshold,
                        int(metric.is_drift_detected),
                        metric.severity.value,
                        metric.timestamp.isoformat()
                    ))
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge drift alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE drift_alerts 
                    SET status = ?, acknowledged_at = ?
                    WHERE alert_id = ?
                ''', (AlertStatus.ACKNOWLEDGED.value, datetime.now().isoformat(), alert_id))
            
            logger.info(f"Alert {alert_id} acknowledged")
            return True
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE drift_alerts 
                    SET status = ?, resolved_at = ?
                    WHERE alert_id = ?
                ''', (AlertStatus.RESOLVED.value, datetime.now().isoformat(), alert_id))
            
            logger.info(f"Alert {alert_id} resolved")
            return True
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def get_alerts(self, model_id: str = None, status: AlertStatus = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get drift alerts with filters"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM drift_alerts"
            params = []
            conditions = []
            
            if model_id:
                conditions.append("model_id = ?")
                params.append(model_id)
            
            if status:
                conditions.append("status = ?")
                params.append(status.value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            alerts = []
            for row in cursor.fetchall():
                alert_dict = dict(zip(columns, row))
                alerts.append(alert_dict)
            
            return alerts
    
    def get_drift_summary(self, model_id: str) -> Dict[str, Any]:
        """Get drift monitoring summary for model"""
        with sqlite3.connect(self.db_path) as conn:
            # Alert statistics
            cursor = conn.execute('''
                SELECT 
                    drift_type,
                    severity,
                    COUNT(*) as count
                FROM drift_alerts 
                WHERE model_id = ?
                GROUP BY drift_type, severity
            ''', (model_id,))
            
            alert_stats = defaultdict(lambda: defaultdict(int))
            for row in cursor.fetchall():
                alert_stats[row[0]][row[1]] = row[2]
            
            # Recent metrics
            cursor = conn.execute('''
                SELECT 
                    dm.metric_name,
                    AVG(dm.value) as avg_value,
                    MAX(dm.value) as max_value,
                    COUNT(*) as count
                FROM drift_metrics dm
                JOIN drift_alerts da ON dm.alert_id = da.alert_id
                WHERE da.model_id = ? AND dm.timestamp > ?
                GROUP BY dm.metric_name
            ''', (model_id, (datetime.now() - timedelta(days=7)).isoformat()))
            
            recent_metrics = {}
            for row in cursor.fetchall():
                recent_metrics[row[0]] = {
                    'avg_value': row[1],
                    'max_value': row[2],
                    'count': row[3]
                }
            
            return {
                'model_id': model_id,
                'alert_statistics': dict(alert_stats),
                'recent_metrics': recent_metrics,
                'total_snapshots': len(self.model_snapshots.get(model_id, [])),
                'last_snapshot': self.model_snapshots[model_id][-1].timestamp.isoformat() if self.model_snapshots.get(model_id) else None
            }

def sample_alert_handler(alert: DriftAlert):
    """Sample alert handler function"""
    print(f"\n🚨 DRIFT ALERT TRIGGERED!")
    print(f"   Model: {alert.model_id}")
    print(f"   Type: {alert.drift_type.value}")
    print(f"   Severity: {alert.severity.value}")
    print(f"   Description: {alert.description}")
    print(f"   Recommendations: {', '.join(alert.recommendations[:2])}")

def generate_sample_data_with_drift():
    """
    Generate sample data with simulated drift
    Mumbai me drift simulation!
    """
    np.random.seed(42)
    
    # Original data distribution
    n_samples = 1000
    original_data = pd.DataFrame({
        'feature_1': np.random.normal(50, 10, n_samples),
        'feature_2': np.random.exponential(2, n_samples),
        'feature_3': np.random.uniform(0, 100, n_samples),
        'feature_4': np.random.gamma(2, 2, n_samples)
    })
    
    # Create target variable
    original_data['target'] = (
        0.3 * original_data['feature_1'] + 
        0.2 * original_data['feature_2'] + 
        0.1 * original_data['feature_3'] + 
        np.random.normal(0, 5, n_samples)
    )
    original_data['target'] = (original_data['target'] > original_data['target'].median()).astype(int)
    
    # Drifted data (simulate distribution shift)
    drifted_data = pd.DataFrame({
        'feature_1': np.random.normal(60, 15, n_samples),  # Mean shift and increased variance
        'feature_2': np.random.exponential(3, n_samples),   # Scale change
        'feature_3': np.random.uniform(20, 120, n_samples), # Range shift
        'feature_4': np.random.gamma(3, 1.5, n_samples)     # Shape change
    })
    
    # Create target with changed relationship (concept drift)
    drifted_data['target'] = (
        0.2 * drifted_data['feature_1'] +  # Reduced importance
        0.4 * drifted_data['feature_2'] +  # Increased importance
        0.15 * drifted_data['feature_3'] + 
        np.random.normal(0, 8, n_samples)  # Increased noise
    )
    drifted_data['target'] = (drifted_data['target'] > drifted_data['target'].median()).astype(int)
    
    return original_data, drifted_data

def main():
    """
    Demo Model Drift Detection System
    Mumbai ke drift detection ka demo!
    """
    print("📊 Starting Model Drift Detection Demo")
    print("=" * 50)
    
    # Initialize drift monitor
    monitor = ModelDriftMonitor("drift_demo.db")
    
    # Add alert handler
    monitor.add_alert_callback(sample_alert_handler)
    
    # Generate sample data
    print("\n📈 Generating sample data with drift...")
    original_data, drifted_data = generate_sample_data_with_drift()
    
    print(f"Original data shape: {original_data.shape}")
    print(f"Drifted data shape: {drifted_data.shape}")
    
    # Simulate model predictions
    print("\n🤖 Simulating model predictions...")
    
    # Original predictions (simulate a trained model)
    from sklearn.ensemble import RandomForestClassifier
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    X_orig = original_data.drop('target', axis=1)
    y_orig = original_data['target']
    
    model.fit(X_orig, y_orig)
    orig_predictions = model.predict_proba(X_orig)
    
    # Create baseline snapshot
    print("\n📸 Creating baseline model snapshot...")
    snapshot_id = monitor.create_model_snapshot(
        model_id="flipkart_recommendation_model",
        data=X_orig,
        predictions=orig_predictions,
        actuals=y_orig.values
    )
    
    print(f"Baseline snapshot created: {snapshot_id}")
    
    # Simulate drift scenario 1: Data drift only
    print("\n🔄 Scenario 1: Data Drift Detection...")
    X_drift = drifted_data.drop('target', axis=1)
    drift_predictions = model.predict_proba(X_drift)
    
    alerts = monitor.detect_drift(
        model_id="flipkart_recommendation_model",
        current_data=X_drift,
        current_predictions=drift_predictions
    )
    
    print(f"Detected {len(alerts)} drift alerts")
    
    # Show detailed alert information
    for i, alert in enumerate(alerts, 1):
        print(f"\n  Alert {i}:")
        print(f"    Type: {alert.drift_type.value}")
        print(f"    Severity: {alert.severity.value}")
        print(f"    Description: {alert.description}")
        print(f"    Metrics with drift: {len([m for m in alert.metrics if m.is_drift_detected])}")
        
        # Show top drift metrics
        drift_metrics = [m for m in alert.metrics if m.is_drift_detected]
        drift_metrics.sort(key=lambda x: x.value, reverse=True)
        
        print(f"    Top drift metrics:")
        for metric in drift_metrics[:3]:
            print(f"      - {metric.metric_name}: {metric.value:.4f} (threshold: {metric.threshold})")
    
    # Simulate scenario 2: Performance drift
    print(f"\n⚠️  Scenario 2: Performance Drift Simulation...")
    
    # Create degraded predictions (simulate model performance drop)
    y_drift = drifted_data['target']
    degraded_predictions = orig_predictions.copy()
    
    # Add noise to simulate performance degradation
    noise_mask = np.random.random(len(degraded_predictions)) < 0.3  # 30% of predictions get noise
    degraded_predictions[noise_mask] = 1 - degraded_predictions[noise_mask]  # Flip predictions
    
    # Create new snapshot with degraded performance
    snapshot_id_2 = monitor.create_model_snapshot(
        model_id="flipkart_recommendation_model",
        data=X_drift,
        predictions=degraded_predictions,
        actuals=y_drift.values
    )
    
    # Detect performance drift
    perf_alerts = monitor.detect_drift(
        model_id="flipkart_recommendation_model",
        current_data=X_drift,
        current_predictions=degraded_predictions,
        current_actuals=y_drift.values
    )
    
    print(f"Performance drift alerts: {len(perf_alerts)}")
    
    # Alert management demo
    print(f"\n📋 Alert Management Demo...")
    all_alerts = monitor.get_alerts(model_id="flipkart_recommendation_model")
    print(f"Total alerts for model: {len(all_alerts)}")
    
    # Acknowledge first alert
    if all_alerts:
        first_alert_id = all_alerts[0]['alert_id']
        monitor.acknowledge_alert(first_alert_id)
        print(f"Acknowledged alert: {first_alert_id}")
        
        # Resolve alert
        monitor.resolve_alert(first_alert_id)
        print(f"Resolved alert: {first_alert_id}")
    
    # Drift summary
    print(f"\n📊 Drift Monitoring Summary:")
    summary = monitor.get_drift_summary("flipkart_recommendation_model")
    
    print(f"  Model ID: {summary['model_id']}")
    print(f"  Total Snapshots: {summary['total_snapshots']}")
    print(f"  Last Snapshot: {summary['last_snapshot']}")
    
    print(f"  Alert Statistics:")
    for drift_type, severities in summary['alert_statistics'].items():
        print(f"    {drift_type}:")
        for severity, count in severities.items():
            print(f"      {severity}: {count} alerts")
    
    if summary['recent_metrics']:
        print(f"  Recent Drift Metrics:")
        for metric_name, stats in summary['recent_metrics'].items():
            print(f"    {metric_name}: avg={stats['avg_value']:.4f}, max={stats['max_value']:.4f}")
    
    # Performance comparison
    print(f"\n⚡ Performance Metrics:")
    
    # Calculate actual performance differences
    orig_accuracy = accuracy_score(y_orig, model.predict(X_orig))
    drift_accuracy = accuracy_score(y_drift, model.predict(X_drift))
    
    print(f"  Original Model Accuracy: {orig_accuracy:.4f}")
    print(f"  Drifted Data Accuracy: {drift_accuracy:.4f}")
    print(f"  Performance Drop: {orig_accuracy - drift_accuracy:.4f}")
    
    # Feature drift analysis
    print(f"\n📈 Feature Drift Analysis:")
    
    ks_detector = KSDriftDetector()
    feature_drift = ks_detector.detect_drift(X_orig, X_drift)
    
    print(f"  Features with significant drift:")
    for metric in sorted(feature_drift, key=lambda x: x.value, reverse=True):
        if metric.is_drift_detected:
            feature_name = metric.metric_name.replace('ks_test_', '')
            print(f"    {feature_name}: KS statistic = {metric.value:.4f} ({metric.severity.value})")
    
    print(f"\n✅ Model drift detection demo completed!")
    print("Mumbai me drift detection bhi early warning system ki tarah important!")

if __name__ == "__main__":
    main()