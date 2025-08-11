#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 7
Anomaly Detection for Indian Financial Data

ML-based anomaly detection system for financial datasets
Indian financial data में anomalies detect करने का system like fraud detection

Author: DStudio Team
Context: Fraud detection and anomaly monitoring for Indian fintech/banking
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.covariance import EllipticEnvelope
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - विसंगति जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class IndianFinancialAnomalyDetector:
    """
    Comprehensive anomaly detection system for Indian financial data
    Indian financial datasets में anomalies detect करने का advanced system
    
    Features:
    1. Statistical anomaly detection
    2. ML-based anomaly detection
    3. Time series anomaly detection
    4. Business rule-based anomaly detection
    5. Real-time anomaly scoring
    6. Fraud pattern detection
    7. Transaction behavior analysis
    8. Multi-dimensional anomaly detection
    """
    
    def __init__(self):
        """Initialize anomaly detection system"""
        
        # Indian business context thresholds
        self.financial_thresholds = {
            'upi_transaction_limit': 200000,      # UPI daily limit
            'rtgs_minimum': 200000,               # RTGS minimum amount
            'neft_maximum': 25000000,             # NEFT maximum
            'cash_transaction_limit': 200000,     # Cash transaction reporting limit
            'suspicious_round_amount': 10000,     # Round amounts above this are suspicious
            'daily_transaction_count_limit': 100, # Suspicious if more than 100 transactions/day
            'velocity_threshold': 0.8,            # Transaction velocity threshold
            'amount_deviation_threshold': 3.0     # Standard deviations for amount anomalies
        }
        
        # Anomaly detection models
        self.models = {
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'elliptic_envelope': EllipticEnvelope(contamination=0.1, random_state=42),
            'dbscan': DBSCAN(eps=0.5, min_samples=5)
        }
        
        # Scalers for different scenarios
        self.scalers = {
            'standard': StandardScaler(),
            'robust': RobustScaler()  # Better for outliers
        }
        
        # Indian financial patterns
        self.suspicious_patterns = {
            'round_amounts': [50000, 100000, 200000, 500000, 1000000],
            'frequent_small_amounts': [1000, 2000, 5000, 9000],  # Just below reporting limits
            'timing_patterns': ['late_night', 'early_morning', 'weekends'],
            'velocity_patterns': ['burst_transactions', 'regular_intervals']
        }
        
        logger.info("Indian Financial Anomaly Detector initialized - विसंगति डिटेक्टर तैयार!")

    def detect_statistical_anomalies(self, df: pd.DataFrame, 
                                   amount_column: str = 'amount') -> Dict[str, Any]:
        """
        Statistical anomaly detection using Z-score and IQR methods
        Statistical methods से anomalies detect करना
        """
        
        logger.info(f"Running statistical anomaly detection on {len(df)} records")
        
        if amount_column not in df.columns:
            return {'error': f'Column {amount_column} not found'}
        
        amounts = df[amount_column].dropna()
        
        results = {
            'total_transactions': len(df),
            'analyzed_transactions': len(amounts),
            'anomaly_methods': {},
            'summary': {}
        }
        
        # Z-Score Method
        z_scores = np.abs(stats.zscore(amounts))
        z_anomalies = z_scores > self.financial_thresholds['amount_deviation_threshold']
        
        results['anomaly_methods']['z_score'] = {
            'anomaly_count': int(z_anomalies.sum()),
            'anomaly_percentage': (z_anomalies.sum() / len(amounts)) * 100,
            'anomaly_indices': amounts[z_anomalies].index.tolist(),
            'threshold': self.financial_thresholds['amount_deviation_threshold']
        }
        
        # IQR Method
        Q1 = amounts.quantile(0.25)
        Q3 = amounts.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_anomalies = (amounts < lower_bound) | (amounts > upper_bound)
        
        results['anomaly_methods']['iqr'] = {
            'anomaly_count': int(iqr_anomalies.sum()),
            'anomaly_percentage': (iqr_anomalies.sum() / len(amounts)) * 100,
            'anomaly_indices': amounts[iqr_anomalies].index.tolist(),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound)
        }
        
        # Modified Z-Score (MAD - Median Absolute Deviation)
        median = amounts.median()
        mad = np.median(np.abs(amounts - median))
        modified_z_scores = 0.6745 * (amounts - median) / mad
        mad_anomalies = np.abs(modified_z_scores) > 3.5
        
        results['anomaly_methods']['modified_z_score'] = {
            'anomaly_count': int(mad_anomalies.sum()),
            'anomaly_percentage': (mad_anomalies.sum() / len(amounts)) * 100,
            'anomaly_indices': amounts[mad_anomalies].index.tolist(),
            'threshold': 3.5
        }
        
        # Percentile-based detection (99th percentile)
        percentile_99 = amounts.quantile(0.99)
        percentile_anomalies = amounts > percentile_99
        
        results['anomaly_methods']['percentile_99'] = {
            'anomaly_count': int(percentile_anomalies.sum()),
            'anomaly_percentage': (percentile_anomalies.sum() / len(amounts)) * 100,
            'anomaly_indices': amounts[percentile_anomalies].index.tolist(),
            'threshold': float(percentile_99)
        }
        
        # Summary statistics
        results['summary'] = {
            'max_anomalies_method': max(results['anomaly_methods'].keys(), 
                                      key=lambda k: results['anomaly_methods'][k]['anomaly_count']),
            'consensus_anomalies': self._find_consensus_anomalies(results['anomaly_methods']),
            'amount_statistics': {
                'mean': float(amounts.mean()),
                'median': float(amounts.median()),
                'std': float(amounts.std()),
                'min': float(amounts.min()),
                'max': float(amounts.max()),
                'q1': float(Q1),
                'q3': float(Q3)
            }
        }
        
        logger.info(f"Statistical anomaly detection complete - {len(results['summary']['consensus_anomalies'])} consensus anomalies found")
        
        return results

    def detect_ml_anomalies(self, df: pd.DataFrame, 
                           feature_columns: List[str]) -> Dict[str, Any]:
        """
        ML-based anomaly detection using multiple algorithms
        Machine Learning से anomalies detect करना
        """
        
        logger.info(f"Running ML anomaly detection with {len(feature_columns)} features")
        
        # Validate feature columns
        available_columns = [col for col in feature_columns if col in df.columns]
        if not available_columns:
            return {'error': 'No valid feature columns found'}
        
        # Prepare data
        feature_data = df[available_columns].select_dtypes(include=[np.number])
        feature_data = feature_data.dropna()
        
        if len(feature_data) < 10:
            return {'error': 'Insufficient data for ML anomaly detection'}
        
        results = {
            'total_records': len(df),
            'analyzed_records': len(feature_data),
            'feature_columns': available_columns,
            'ml_methods': {}
        }
        
        # Scale the data
        scaled_data = self.scalers['robust'].fit_transform(feature_data)
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        iso_predictions = iso_forest.fit_predict(scaled_data)
        iso_anomalies = iso_predictions == -1
        
        results['ml_methods']['isolation_forest'] = {
            'anomaly_count': int(iso_anomalies.sum()),
            'anomaly_percentage': (iso_anomalies.sum() / len(feature_data)) * 100,
            'anomaly_indices': feature_data.index[iso_anomalies].tolist(),
            'anomaly_scores': iso_forest.decision_function(scaled_data).tolist()
        }
        
        # One-Class SVM (Elliptic Envelope)
        elliptic_env = EllipticEnvelope(contamination=0.1, random_state=42)
        elliptic_predictions = elliptic_env.fit_predict(scaled_data)
        elliptic_anomalies = elliptic_predictions == -1
        
        results['ml_methods']['elliptic_envelope'] = {
            'anomaly_count': int(elliptic_anomalies.sum()),
            'anomaly_percentage': (elliptic_anomalies.sum() / len(feature_data)) * 100,
            'anomaly_indices': feature_data.index[elliptic_anomalies].tolist()
        }
        
        # DBSCAN Clustering (outliers as anomalies)
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(scaled_data)
        dbscan_anomalies = dbscan_labels == -1
        
        results['ml_methods']['dbscan'] = {
            'anomaly_count': int(dbscan_anomalies.sum()),
            'anomaly_percentage': (dbscan_anomalies.sum() / len(feature_data)) * 100,
            'anomaly_indices': feature_data.index[dbscan_anomalies].tolist(),
            'n_clusters': len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
        }
        
        # Local Outlier Factor (LOF) - simplified implementation
        from sklearn.neighbors import LocalOutlierFactor
        lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
        lof_predictions = lof.fit_predict(scaled_data)
        lof_anomalies = lof_predictions == -1
        
        results['ml_methods']['local_outlier_factor'] = {
            'anomaly_count': int(lof_anomalies.sum()),
            'anomaly_percentage': (lof_anomalies.sum() / len(feature_data)) * 100,
            'anomaly_indices': feature_data.index[lof_anomalies].tolist(),
            'lof_scores': lof.negative_outlier_factor_.tolist()
        }
        
        # Ensemble method - consensus from multiple algorithms
        consensus_anomalies = self._ml_consensus_anomalies(results['ml_methods'])
        results['consensus_anomalies'] = consensus_anomalies
        
        logger.info(f"ML anomaly detection complete - {len(consensus_anomalies)} consensus anomalies")
        
        return results

    def detect_business_rule_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Business rule-based anomaly detection for Indian financial context
        Business rules के आधार पर anomalies detect करना
        """
        
        logger.info("Running business rule-based anomaly detection")
        
        anomalies = {
            'rule_violations': {},
            'suspicious_patterns': {},
            'compliance_issues': {},
            'summary': {}
        }
        
        # Rule 1: Amount-based anomalies
        if 'amount' in df.columns:
            amounts = df['amount']
            
            # UPI limit violations
            upi_violations = amounts > self.financial_thresholds['upi_transaction_limit']
            anomalies['rule_violations']['upi_limit_exceeded'] = {
                'count': int(upi_violations.sum()),
                'percentage': (upi_violations.sum() / len(df)) * 100,
                'indices': df.index[upi_violations].tolist()
            }
            
            # Suspicious round amounts
            round_amount_threshold = self.financial_thresholds['suspicious_round_amount']
            round_amounts = (amounts >= round_amount_threshold) & (amounts % round_amount_threshold == 0)
            anomalies['suspicious_patterns']['round_amounts'] = {
                'count': int(round_amounts.sum()),
                'percentage': (round_amounts.sum() / len(df)) * 100,
                'indices': df.index[round_amounts].tolist()
            }
            
            # Just-below-limit amounts (possible structuring)
            for limit in [50000, 200000]:  # Common reporting thresholds
                near_limit = (amounts >= limit * 0.95) & (amounts < limit)
                anomalies['suspicious_patterns'][f'near_limit_{limit}'] = {
                    'count': int(near_limit.sum()),
                    'percentage': (near_limit.sum() / len(df)) * 100,
                    'indices': df.index[near_limit].tolist()
                }
        
        # Rule 2: Time-based anomalies
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            
            # Late night transactions (12 AM - 5 AM)
            late_night = df['hour'].isin([0, 1, 2, 3, 4, 5])
            anomalies['suspicious_patterns']['late_night_transactions'] = {
                'count': int(late_night.sum()),
                'percentage': (late_night.sum() / len(df)) * 100,
                'indices': df.index[late_night].tolist()
            }
            
            # Weekend transactions (if business account)
            weekend_transactions = df['day_of_week'].isin([5, 6])  # Saturday, Sunday
            anomalies['suspicious_patterns']['weekend_transactions'] = {
                'count': int(weekend_transactions.sum()),
                'percentage': (weekend_transactions.sum() / len(df)) * 100,
                'indices': df.index[weekend_transactions].tolist()
            }
        
        # Rule 3: Frequency-based anomalies
        if 'customer_id' in df.columns and 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            daily_transaction_counts = df.groupby(['customer_id', 'date']).size()
            
            # High frequency transactions
            high_frequency = daily_transaction_counts > self.financial_thresholds['daily_transaction_count_limit']
            if high_frequency.any():
                high_freq_customers = daily_transaction_counts[high_frequency].index.get_level_values('customer_id').unique()
                anomalies['rule_violations']['high_frequency_transactions'] = {
                    'affected_customers': len(high_freq_customers),
                    'customer_ids': high_freq_customers.tolist()
                }
        
        # Rule 4: Pattern-based anomalies
        if 'amount' in df.columns and 'customer_id' in df.columns:
            # Same amount repeated frequently
            customer_amount_counts = df.groupby(['customer_id', 'amount']).size()
            repeated_amounts = customer_amount_counts > 5  # Same amount more than 5 times
            
            if repeated_amounts.any():
                anomalies['suspicious_patterns']['repeated_amounts'] = {
                    'pattern_count': int(repeated_amounts.sum()),
                    'affected_customers': len(repeated_amounts[repeated_amounts].index.get_level_values('customer_id').unique())
                }
        
        # Rule 5: Velocity-based anomalies (rapid successive transactions)
        if all(col in df.columns for col in ['customer_id', 'timestamp', 'amount']):
            df_sorted = df.sort_values(['customer_id', 'timestamp'])
            df_sorted['time_diff'] = df_sorted.groupby('customer_id')['timestamp'].diff()
            
            # Transactions within 1 minute
            rapid_transactions = df_sorted['time_diff'] < pd.Timedelta(minutes=1)
            anomalies['suspicious_patterns']['rapid_transactions'] = {
                'count': int(rapid_transactions.sum()),
                'percentage': (rapid_transactions.sum() / len(df)) * 100,
                'indices': df_sorted.index[rapid_transactions].tolist()
            }
        
        # Summary
        total_rule_violations = sum(
            violation.get('count', 0) 
            for violation in anomalies['rule_violations'].values()
            if isinstance(violation, dict)
        )
        
        total_suspicious_patterns = sum(
            pattern.get('count', 0) 
            for pattern in anomalies['suspicious_patterns'].values()
            if isinstance(pattern, dict)
        )
        
        anomalies['summary'] = {
            'total_rule_violations': total_rule_violations,
            'total_suspicious_patterns': total_suspicious_patterns,
            'total_anomalies': total_rule_violations + total_suspicious_patterns,
            'anomaly_rate': ((total_rule_violations + total_suspicious_patterns) / len(df)) * 100
        }
        
        logger.info(f"Business rule anomaly detection complete - {anomalies['summary']['total_anomalies']} total anomalies")
        
        return anomalies

    def detect_time_series_anomalies(self, df: pd.DataFrame, 
                                   timestamp_column: str = 'timestamp',
                                   value_column: str = 'amount') -> Dict[str, Any]:
        """
        Time series anomaly detection
        Time series data में anomalies detect करना
        """
        
        logger.info("Running time series anomaly detection")
        
        if not all(col in df.columns for col in [timestamp_column, value_column]):
            return {'error': f'Required columns {timestamp_column}, {value_column} not found'}
        
        # Prepare time series data
        ts_data = df[[timestamp_column, value_column]].copy()
        ts_data[timestamp_column] = pd.to_datetime(ts_data[timestamp_column])
        ts_data = ts_data.sort_values(timestamp_column)
        
        # Aggregate to hourly data
        ts_hourly = ts_data.set_index(timestamp_column).resample('H')[value_column].agg(['sum', 'count', 'mean'])
        ts_hourly = ts_hourly.fillna(0)
        
        results = {
            'time_series_length': len(ts_hourly),
            'analysis_period': {
                'start': ts_data[timestamp_column].min().isoformat(),
                'end': ts_data[timestamp_column].max().isoformat()
            },
            'anomaly_methods': {}
        }
        
        # Method 1: Moving average deviation
        window_size = 24  # 24-hour window
        if len(ts_hourly) > window_size:
            ts_hourly['moving_avg'] = ts_hourly['sum'].rolling(window=window_size, center=True).mean()
            ts_hourly['deviation'] = np.abs(ts_hourly['sum'] - ts_hourly['moving_avg'])
            
            # Detect anomalies based on deviation threshold
            deviation_threshold = ts_hourly['deviation'].quantile(0.95)
            moving_avg_anomalies = ts_hourly['deviation'] > deviation_threshold
            
            results['anomaly_methods']['moving_average_deviation'] = {
                'anomaly_count': int(moving_avg_anomalies.sum()),
                'anomaly_percentage': (moving_avg_anomalies.sum() / len(ts_hourly)) * 100,
                'threshold': float(deviation_threshold),
                'anomaly_timestamps': ts_hourly.index[moving_avg_anomalies].tolist()
            }
        
        # Method 2: Seasonal decomposition anomalies (if enough data)
        if len(ts_hourly) > 48:  # At least 2 days of data
            try:
                from statsmodels.tsa.seasonal import seasonal_decompose
                
                # Decompose the time series
                decomposition = seasonal_decompose(ts_hourly['sum'], model='additive', period=24)
                residuals = decomposition.resid.dropna()
                
                # Detect anomalies in residuals
                residual_threshold = residuals.std() * 2
                seasonal_anomalies = np.abs(residuals) > residual_threshold
                
                results['anomaly_methods']['seasonal_decomposition'] = {
                    'anomaly_count': int(seasonal_anomalies.sum()),
                    'anomaly_percentage': (seasonal_anomalies.sum() / len(residuals)) * 100,
                    'threshold': float(residual_threshold),
                    'anomaly_timestamps': residuals.index[seasonal_anomalies].tolist()
                }
                
            except Exception as e:
                logger.warning(f"Seasonal decomposition failed: {str(e)}")
        
        # Method 3: Change point detection (simple)
        if len(ts_hourly) > 10:
            values = ts_hourly['sum'].values
            
            # Calculate rolling statistics
            window = min(24, len(values) // 4)
            rolling_mean = pd.Series(values).rolling(window=window).mean()
            rolling_std = pd.Series(values).rolling(window=window).std()
            
            # Detect significant changes
            mean_changes = np.abs(np.diff(rolling_mean.dropna())) > rolling_std.mean()
            
            if len(mean_changes) > 0:
                results['anomaly_methods']['change_point_detection'] = {
                    'change_points': int(mean_changes.sum()),
                    'change_percentage': (mean_changes.sum() / len(mean_changes)) * 100
                }
        
        return results

    def calculate_anomaly_scores(self, df: pd.DataFrame, 
                                feature_columns: List[str]) -> pd.DataFrame:
        """
        Calculate comprehensive anomaly scores for each record
        हर record के लिए anomaly score calculate करना
        """
        
        logger.info("Calculating comprehensive anomaly scores")
        
        # Initialize scores
        df_scored = df.copy()
        df_scored['anomaly_score'] = 0.0
        df_scored['anomaly_reasons'] = ''
        
        # Statistical anomaly scores
        if 'amount' in df.columns:
            amounts = df['amount']
            z_scores = np.abs(stats.zscore(amounts.fillna(amounts.mean())))
            df_scored['statistical_score'] = np.minimum(z_scores / 3.0, 1.0)  # Normalize to 0-1
            df_scored['anomaly_score'] += df_scored['statistical_score'] * 0.3
        
        # ML-based anomaly scores
        available_features = [col for col in feature_columns if col in df.columns and df[col].dtype in ['int64', 'float64']]
        if len(available_features) >= 2:
            feature_data = df[available_features].fillna(df[available_features].mean())
            
            if len(feature_data) > 10:
                scaled_data = self.scalers['robust'].fit_transform(feature_data)
                
                # Isolation Forest scores
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                iso_scores = iso_forest.fit(scaled_data).decision_function(scaled_data)
                # Convert to 0-1 scale (lower scores = more anomalous)
                iso_scores_normalized = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
                df_scored['ml_score'] = 1 - iso_scores_normalized  # Invert so higher = more anomalous
                df_scored['anomaly_score'] += df_scored['ml_score'] * 0.4
        
        # Business rule scores
        business_score = 0.0
        reasons = []
        
        if 'amount' in df.columns:
            amounts = df['amount']
            
            # UPI limit violations
            upi_violations = amounts > self.financial_thresholds['upi_transaction_limit']
            business_score += upi_violations * 0.5
            
            # Round amount suspicion
            round_amounts = (amounts >= 10000) & (amounts % 10000 == 0)
            business_score += round_amounts * 0.2
        
        if 'timestamp' in df.columns:
            hour = pd.to_datetime(df['timestamp']).dt.hour
            
            # Late night transactions
            late_night = hour.isin([0, 1, 2, 3, 4, 5])
            business_score += late_night * 0.1
        
        df_scored['business_rule_score'] = business_score
        df_scored['anomaly_score'] += business_score * 0.3
        
        # Normalize final score to 0-1
        df_scored['anomaly_score'] = np.minimum(df_scored['anomaly_score'], 1.0)
        
        # Classify anomaly levels
        df_scored['anomaly_level'] = pd.cut(
            df_scored['anomaly_score'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['LOW', 'MEDIUM', 'HIGH']
        )
        
        logger.info(f"Anomaly scoring complete - Level distribution: {df_scored['anomaly_level'].value_counts().to_dict()}")
        
        return df_scored

    def _find_consensus_anomalies(self, methods_results: Dict) -> List[int]:
        """Find consensus anomalies across multiple methods"""
        
        all_indices = set()
        for method_result in methods_results.values():
            if 'anomaly_indices' in method_result:
                all_indices.update(method_result['anomaly_indices'])
        
        # Count occurrences
        index_counts = {}
        for method_result in methods_results.values():
            if 'anomaly_indices' in method_result:
                for idx in method_result['anomaly_indices']:
                    index_counts[idx] = index_counts.get(idx, 0) + 1
        
        # Return indices found by at least 2 methods
        consensus_threshold = max(2, len(methods_results) // 2)
        consensus_anomalies = [idx for idx, count in index_counts.items() if count >= consensus_threshold]
        
        return consensus_anomalies

    def _ml_consensus_anomalies(self, ml_methods: Dict) -> List[int]:
        """Find consensus anomalies from ML methods"""
        return self._find_consensus_anomalies(ml_methods)

    def create_anomaly_visualizations(self, df_scored: pd.DataFrame, 
                                    output_dir: str = "./anomaly_charts") -> Dict[str, str]:
        """Create anomaly detection visualizations"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        chart_files = {}
        
        # 1. Anomaly Score Distribution
        fig = px.histogram(df_scored, x='anomaly_score', nbins=50,
                          title='Distribution of Anomaly Scores')
        fig.update_layout(xaxis_title='Anomaly Score', yaxis_title='Count')
        
        score_dist_path = os.path.join(output_dir, 'anomaly_score_distribution.html')
        fig.write_html(score_dist_path)
        chart_files['score_distribution'] = score_dist_path
        
        # 2. Anomaly Level Pie Chart
        level_counts = df_scored['anomaly_level'].value_counts()
        fig = px.pie(values=level_counts.values, names=level_counts.index,
                     title='Anomaly Level Distribution')
        
        level_pie_path = os.path.join(output_dir, 'anomaly_level_pie.html')
        fig.write_html(level_pie_path)
        chart_files['level_distribution'] = level_pie_path
        
        # 3. Amount vs Anomaly Score Scatter
        if 'amount' in df_scored.columns:
            fig = px.scatter(df_scored, x='amount', y='anomaly_score',
                           color='anomaly_level',
                           title='Transaction Amount vs Anomaly Score',
                           log_x=True)
            fig.update_layout(xaxis_title='Transaction Amount (Log Scale)', 
                            yaxis_title='Anomaly Score')
            
            amount_scatter_path = os.path.join(output_dir, 'amount_vs_anomaly.html')
            fig.write_html(amount_scatter_path)
            chart_files['amount_scatter'] = amount_scatter_path
        
        # 4. Time Series of High Anomalies
        if 'timestamp' in df_scored.columns:
            high_anomalies = df_scored[df_scored['anomaly_level'] == 'HIGH']
            if not high_anomalies.empty:
                daily_high_anomalies = high_anomalies.set_index(
                    pd.to_datetime(high_anomalies['timestamp'])
                ).resample('D').size()
                
                fig = px.line(x=daily_high_anomalies.index, y=daily_high_anomalies.values,
                             title='Daily High Anomaly Count')
                fig.update_layout(xaxis_title='Date', yaxis_title='High Anomaly Count')
                
                timeseries_path = os.path.join(output_dir, 'daily_high_anomalies.html')
                fig.write_html(timeseries_path)
                chart_files['timeseries'] = timeseries_path
        
        logger.info(f"Anomaly visualizations created in {output_dir}")
        
        return chart_files

def create_sample_financial_dataset(num_records: int = 10000) -> pd.DataFrame:
    """Create sample Indian financial dataset with known anomalies"""
    
    np.random.seed(42)
    
    # Normal transaction patterns
    base_data = {
        'transaction_id': [f'TXN{i:010d}' for i in range(num_records)],
        'customer_id': np.random.choice([f'CUST{i:06d}' for i in range(1, 1001)], num_records),
        'amount': np.random.exponential(scale=5000, size=num_records),
        'timestamp': pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            periods=num_records
        ),
        'transaction_type': np.random.choice(['UPI', 'NEFT', 'RTGS', 'IMPS'], num_records, p=[0.6, 0.2, 0.1, 0.1]),
        'merchant_category': np.random.choice(['Grocery', 'Fuel', 'Restaurant', 'Online', 'ATM'], num_records),
        'location_city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'], num_records)
    }
    
    df = pd.DataFrame(base_data)
    
    # Introduce known anomalies
    
    # 1. High amount anomalies (1% of data)
    high_amount_indices = np.random.choice(num_records, size=num_records//100, replace=False)
    for idx in high_amount_indices:
        df.loc[idx, 'amount'] = np.random.uniform(500000, 2000000)  # Very high amounts
    
    # 2. Round amount anomalies (2% of data)
    round_amount_indices = np.random.choice(num_records, size=num_records//50, replace=False)
    for idx in round_amount_indices:
        df.loc[idx, 'amount'] = np.random.choice([50000, 100000, 200000, 500000])
    
    # 3. Late night transaction anomalies (1% of data)
    late_night_indices = np.random.choice(num_records, size=num_records//100, replace=False)
    for idx in late_night_indices:
        # Set time between 2 AM and 5 AM
        late_hour = np.random.choice([2, 3, 4, 5])
        df.loc[idx, 'timestamp'] = df.loc[idx, 'timestamp'].replace(hour=late_hour)
    
    # 4. Burst transaction pattern (same customer, rapid transactions)
    burst_customer = 'CUST000001'
    burst_indices = df[df['customer_id'] == burst_customer].index[:20]  # First 20 transactions for this customer
    base_time = datetime.now() - timedelta(days=1)
    for i, idx in enumerate(burst_indices):
        df.loc[idx, 'timestamp'] = base_time + timedelta(minutes=i*2)  # Every 2 minutes
        df.loc[idx, 'amount'] = 9900  # Just below 10k limit
    
    # 5. Repeated amount pattern
    repeated_amount_customer = 'CUST000002'
    repeated_indices = df[df['customer_id'] == repeated_amount_customer].index[:10]
    for idx in repeated_indices:
        df.loc[idx, 'amount'] = 15000  # Same amount multiple times
    
    return df

def main():
    """Main execution function - demo of anomaly detection system"""
    
    print("🔍 Indian Financial Anomaly Detection System Demo")
    print("वित्तीय विसंगति पहचान प्रणाली का प्रदर्शन\n")
    
    # Initialize detector
    detector = IndianFinancialAnomalyDetector()
    
    # Create sample dataset with known anomalies
    print("Creating sample financial dataset with known anomalies...")
    sample_df = create_sample_financial_dataset(5000)
    print(f"Sample dataset created with {len(sample_df)} transactions\n")
    
    # 1. Statistical Anomaly Detection
    print("=" * 60)
    print("STATISTICAL ANOMALY DETECTION")
    print("=" * 60)
    
    statistical_results = detector.detect_statistical_anomalies(sample_df, 'amount')
    
    print(f"Total Transactions Analyzed: {statistical_results['analyzed_transactions']}")
    print("\nMethod-wise Results:")
    for method, results in statistical_results['anomaly_methods'].items():
        print(f"  {method.upper()}: {results['anomaly_count']} anomalies ({results['anomaly_percentage']:.2f}%)")
    
    print(f"\nConsensus Anomalies: {len(statistical_results['summary']['consensus_anomalies'])}")
    print(f"Amount Statistics:")
    stats = statistical_results['summary']['amount_statistics']
    print(f"  Mean: ₹{stats['mean']:,.2f}")
    print(f"  Median: ₹{stats['median']:,.2f}")
    print(f"  Max: ₹{stats['max']:,.2f}")
    
    # 2. ML-based Anomaly Detection
    print("\n" + "=" * 60)
    print("ML-BASED ANOMALY DETECTION")
    print("=" * 60)
    
    feature_columns = ['amount']
    ml_results = detector.detect_ml_anomalies(sample_df, feature_columns)
    
    print(f"Records Analyzed: {ml_results['analyzed_records']}")
    print(f"Features Used: {ml_results['feature_columns']}")
    print("\nMethod-wise Results:")
    for method, results in ml_results['ml_methods'].items():
        print(f"  {method.upper()}: {results['anomaly_count']} anomalies ({results['anomaly_percentage']:.2f}%)")
    
    print(f"\nConsensus Anomalies: {len(ml_results['consensus_anomalies'])}")
    
    # 3. Business Rule Anomaly Detection
    print("\n" + "=" * 60)
    print("BUSINESS RULE ANOMALY DETECTION")
    print("=" * 60)
    
    business_results = detector.detect_business_rule_anomalies(sample_df)
    
    print("Rule Violations:")
    for rule, results in business_results['rule_violations'].items():
        if isinstance(results, dict) and 'count' in results:
            print(f"  {rule.replace('_', ' ').title()}: {results['count']} violations ({results['percentage']:.2f}%)")
    
    print("\nSuspicious Patterns:")
    for pattern, results in business_results['suspicious_patterns'].items():
        if isinstance(results, dict) and 'count' in results:
            print(f"  {pattern.replace('_', ' ').title()}: {results['count']} patterns ({results['percentage']:.2f}%)")
    
    print(f"\nTotal Business Rule Anomalies: {business_results['summary']['total_anomalies']}")
    print(f"Overall Anomaly Rate: {business_results['summary']['anomaly_rate']:.2f}%")
    
    # 4. Time Series Anomaly Detection
    print("\n" + "=" * 60)
    print("TIME SERIES ANOMALY DETECTION")
    print("=" * 60)
    
    timeseries_results = detector.detect_time_series_anomalies(sample_df)
    
    print(f"Time Series Length: {timeseries_results['time_series_length']} hours")
    print(f"Analysis Period: {timeseries_results['analysis_period']['start']} to {timeseries_results['analysis_period']['end']}")
    
    if timeseries_results['anomaly_methods']:
        print("\nTime Series Anomalies:")
        for method, results in timeseries_results['anomaly_methods'].items():
            if 'anomaly_count' in results:
                print(f"  {method.replace('_', ' ').title()}: {results['anomaly_count']} anomalies ({results['anomaly_percentage']:.2f}%)")
    
    # 5. Comprehensive Anomaly Scoring
    print("\n" + "=" * 60)
    print("COMPREHENSIVE ANOMALY SCORING")
    print("=" * 60)
    
    df_scored = detector.calculate_anomaly_scores(sample_df, ['amount'])
    
    level_distribution = df_scored['anomaly_level'].value_counts()
    print("Anomaly Level Distribution:")
    for level, count in level_distribution.items():
        percentage = (count / len(df_scored)) * 100
        print(f"  {level}: {count} ({percentage:.2f}%)")
    
    # Top anomalies
    top_anomalies = df_scored.nlargest(10, 'anomaly_score')
    print(f"\nTop 10 Anomalous Transactions:")
    print("Transaction ID | Amount | Score | Level")
    print("-" * 45)
    for _, row in top_anomalies.iterrows():
        print(f"{row['transaction_id']} | ₹{row['amount']:8,.0f} | {row['anomaly_score']:.3f} | {row['anomaly_level']}")
    
    # 6. Generate Visualizations
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    
    try:
        chart_files = detector.create_anomaly_visualizations(df_scored)
        print("Visualizations created:")
        for chart_name, file_path in chart_files.items():
            print(f"  {chart_name}: {file_path}")
    except Exception as e:
        print(f"Visualization creation failed: {str(e)}")
    
    # Summary Report
    print("\n" + "=" * 60)
    print("ANOMALY DETECTION SUMMARY REPORT")
    print("=" * 60)
    
    total_high_anomalies = len(df_scored[df_scored['anomaly_level'] == 'HIGH'])
    total_medium_anomalies = len(df_scored[df_scored['anomaly_level'] == 'MEDIUM'])
    
    print(f"""
    Dataset: {len(sample_df)} financial transactions
    Analysis Period: 30 days
    
    Anomaly Detection Results:
    ========================
    High Risk Anomalies: {total_high_anomalies} ({(total_high_anomalies/len(sample_df))*100:.2f}%)
    Medium Risk Anomalies: {total_medium_anomalies} ({(total_medium_anomalies/len(sample_df))*100:.2f}%)
    
    Detection Methods Used:
    - Statistical Analysis (Z-score, IQR, MAD)
    - Machine Learning (Isolation Forest, LOF, DBSCAN)
    - Business Rules (UPI limits, round amounts, timing)
    - Time Series Analysis (moving averages, seasonal)
    
    Recommendations:
    1. Investigate {total_high_anomalies} high-risk transactions immediately
    2. Monitor {total_medium_anomalies} medium-risk transactions
    3. Implement real-time anomaly scoring for new transactions
    4. Set up alerts for anomaly scores above 0.6
    """)
    
    print("\n✅ Indian Financial Anomaly Detection Demo Complete!")
    print("प्रणाली तैयार है - Ready for production fraud detection!")
    
    return {
        'statistical_results': statistical_results,
        'ml_results': ml_results,
        'business_results': business_results,
        'timeseries_results': timeseries_results,
        'scored_data': df_scored
    }

if __name__ == "__main__":
    results = main()