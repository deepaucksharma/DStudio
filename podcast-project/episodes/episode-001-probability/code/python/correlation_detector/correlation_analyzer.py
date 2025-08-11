#!/usr/bin/env python3
"""
Correlation Detection Algorithm for System Failures
==================================================
Detect hidden dependencies and correlations in system failures.

Real-world examples:
- Facebook BGP failure (Oct 2021): DNS failure caused authentication cascade
- AWS US-East-1 outage (Dec 2021): S3 issues cascaded to Lambda, CloudWatch  
- Cloudflare outage (Jun 2022): Router configuration caused global CDN failure
- Paytm IPO day crash (Nov 2021): Payment gateway overload affected UPI systems

Features:
- Statistical correlation detection (Pearson, Spearman, Kendall)
- Time-lagged correlation analysis (delayed dependencies)  
- Causal inference using Granger causality
- Hidden dependency discovery using mutual information
- Real-time correlation monitoring
- Alert generation for dangerous correlations
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.var_model import VAR
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import warnings
import logging
from collections import defaultdict, deque
import threading
import time
import random

warnings.filterwarnings('ignore')


@dataclass
class CorrelationResult:
    """Result of correlation analysis between two metrics"""
    metric1: str
    metric2: str
    correlation_type: str
    correlation_value: float
    p_value: float
    is_significant: bool
    lag: int = 0  # Time lag in minutes
    confidence_interval: Tuple[float, float] = None
    strength: str = "unknown"  # weak, moderate, strong
    
    def __post_init__(self):
        """Calculate correlation strength"""
        abs_corr = abs(self.correlation_value)
        if abs_corr < 0.3:
            self.strength = "weak"
        elif abs_corr < 0.7:
            self.strength = "moderate"  
        else:
            self.strength = "strong"


@dataclass
class CausalityResult:
    """Result of Granger causality test"""
    cause_metric: str
    effect_metric: str
    p_value: float
    is_causal: bool
    lag: int
    test_statistic: float
    confidence_level: float = 0.95


@dataclass
class DependencyGraph:
    """Dependency graph of services based on correlation analysis"""
    nodes: List[str]
    edges: List[Tuple[str, str, float]]  # (from, to, strength)
    critical_paths: List[List[str]]
    risk_score: Dict[str, float]


class StatisticalCorrelationDetector:
    """Statistical correlation detection using multiple methods"""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.logger = logging.getLogger(__name__)
    
    def calculate_pearson_correlation(self, x: np.ndarray, y: np.ndarray) -> CorrelationResult:
        """Calculate Pearson correlation coefficient"""
        # Remove NaN values
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]
        
        if len(x_clean) < 3:
            return CorrelationResult("", "", "pearson", 0.0, 1.0, False)
        
        corr_coef, p_value = pearsonr(x_clean, y_clean)
        
        # Calculate confidence interval
        n = len(x_clean)
        z = np.arctanh(corr_coef)  # Fisher transformation
        se = 1 / np.sqrt(n - 3)
        z_crit = stats.norm.ppf(1 - self.significance_level / 2)
        
        ci_lower = np.tanh(z - z_crit * se)
        ci_upper = np.tanh(z + z_crit * se)
        
        return CorrelationResult(
            metric1="", metric2="",  # Will be set by caller
            correlation_type="pearson",
            correlation_value=corr_coef,
            p_value=p_value,
            is_significant=p_value < self.significance_level,
            confidence_interval=(ci_lower, ci_upper)
        )
    
    def calculate_spearman_correlation(self, x: np.ndarray, y: np.ndarray) -> CorrelationResult:
        """Calculate Spearman rank correlation (good for non-linear relationships)"""
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]
        
        if len(x_clean) < 3:
            return CorrelationResult("", "", "spearman", 0.0, 1.0, False)
        
        corr_coef, p_value = spearmanr(x_clean, y_clean)
        
        return CorrelationResult(
            metric1="", metric2="",
            correlation_type="spearman", 
            correlation_value=corr_coef,
            p_value=p_value,
            is_significant=p_value < self.significance_level
        )
    
    def calculate_kendall_correlation(self, x: np.ndarray, y: np.ndarray) -> CorrelationResult:
        """Calculate Kendall Tau correlation (robust to outliers)"""
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]
        
        if len(x_clean) < 3:
            return CorrelationResult("", "", "kendall", 0.0, 1.0, False)
        
        corr_coef, p_value = kendalltau(x_clean, y_clean)
        
        return CorrelationResult(
            metric1="", metric2="",
            correlation_type="kendall",
            correlation_value=corr_coef,
            p_value=p_value, 
            is_significant=p_value < self.significance_level
        )
    
    def calculate_mutual_information(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate mutual information (detects non-linear dependencies)"""
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]
        
        if len(x_clean) < 10:
            return 0.0
        
        # Reshape for sklearn
        X = x_clean.reshape(-1, 1)
        y_clean = y_clean.reshape(-1)
        
        try:
            mi = mutual_info_regression(X, y_clean, random_state=42)[0]
            return mi
        except Exception:
            return 0.0


class TimeLaggedCorrelationAnalyzer:
    """Analyze correlations with time lags to detect delayed dependencies"""
    
    def __init__(self, max_lag: int = 60):  # Max lag in minutes
        self.max_lag = max_lag
        self.detector = StatisticalCorrelationDetector()
    
    def find_optimal_lag(self, x: np.ndarray, y: np.ndarray) -> Tuple[int, float]:
        """Find optimal time lag that maximizes correlation"""
        best_lag = 0
        best_correlation = 0.0
        
        for lag in range(0, min(self.max_lag, len(x) - 1)):
            if lag == 0:
                x_lagged, y_lagged = x, y
            else:
                x_lagged = x[:-lag]
                y_lagged = y[lag:]
            
            if len(x_lagged) < 3:
                continue
                
            result = self.detector.calculate_pearson_correlation(x_lagged, y_lagged)
            
            if abs(result.correlation_value) > abs(best_correlation):
                best_correlation = result.correlation_value
                best_lag = lag
        
        return best_lag, best_correlation
    
    def analyze_lagged_correlation(self, x: np.ndarray, y: np.ndarray, 
                                 metric1: str, metric2: str) -> CorrelationResult:
        """Analyze correlation with optimal time lag"""
        best_lag, best_corr = self.find_optimal_lag(x, y)
        
        # Calculate correlation at optimal lag
        if best_lag == 0:
            x_lagged, y_lagged = x, y
        else:
            x_lagged = x[:-best_lag]
            y_lagged = y[best_lag:]
        
        result = self.detector.calculate_pearson_correlation(x_lagged, y_lagged)
        result.metric1 = metric1
        result.metric2 = metric2
        result.lag = best_lag
        result.correlation_type = "lagged_pearson"
        
        return result


class GrangerCausalityAnalyzer:
    """Granger causality analysis to identify causal relationships"""
    
    def __init__(self, max_lag: int = 12):
        self.max_lag = max_lag
        self.logger = logging.getLogger(__name__)
    
    def test_granger_causality(self, cause_series: np.ndarray, 
                              effect_series: np.ndarray,
                              cause_name: str, effect_name: str) -> List[CausalityResult]:
        """Test if cause_series Granger-causes effect_series"""
        
        # Prepare data
        mask = ~(np.isnan(cause_series) | np.isnan(effect_series))
        cause_clean = cause_series[mask]
        effect_clean = effect_series[mask]
        
        if len(cause_clean) < self.max_lag * 3:
            return []
        
        # Create dataframe for Granger test
        data = pd.DataFrame({
            'cause': cause_clean,
            'effect': effect_clean
        })
        
        results = []
        try:
            # Test for various lags
            max_test_lag = min(self.max_lag, len(cause_clean) // 4)
            
            if max_test_lag > 0:
                gc_result = grangercausalitytests(
                    data[['effect', 'cause']], 
                    maxlag=max_test_lag, 
                    verbose=False
                )
                
                for lag in range(1, max_test_lag + 1):
                    if lag in gc_result:
                        test_stats = gc_result[lag][0]
                        
                        # Get F-test results
                        if 'ssr_ftest' in test_stats:
                            f_stat = test_stats['ssr_ftest'][0]
                            p_value = test_stats['ssr_ftest'][1]
                            
                            result = CausalityResult(
                                cause_metric=cause_name,
                                effect_metric=effect_name,
                                p_value=p_value,
                                is_causal=p_value < 0.05,
                                lag=lag,
                                test_statistic=f_stat
                            )
                            results.append(result)
        
        except Exception as e:
            self.logger.warning(f"Granger causality test failed: {e}")
        
        return results


class RealTimeCorrelationMonitor:
    """Real-time correlation monitoring for live systems"""
    
    def __init__(self, window_size: int = 300, update_interval: int = 60):
        self.window_size = window_size  # 5 minutes of data
        self.update_interval = update_interval  # Update every minute
        self.metric_buffers = defaultdict(lambda: deque(maxlen=self.window_size))
        self.correlation_history = []
        self.alert_thresholds = {
            'high_correlation': 0.8,
            'sudden_correlation_change': 0.3
        }
        self.is_running = False
        self.monitor_thread = None
        self.detector = StatisticalCorrelationDetector()
        self.lag_analyzer = TimeLaggedCorrelationAnalyzer(max_lag=30)
    
    def add_metric_data(self, metric_name: str, value: float, timestamp: datetime = None):
        """Add new metric data point"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metric_buffers[metric_name].append((timestamp, value))
    
    def start_monitoring(self):
        """Start real-time correlation monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("🔄 Real-time correlation monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time correlation monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️  Real-time correlation monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._analyze_current_correlations()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _analyze_current_correlations(self):
        """Analyze correlations for current window"""
        metric_names = list(self.metric_buffers.keys())
        
        if len(metric_names) < 2:
            return
        
        current_correlations = []
        
        for i, metric1 in enumerate(metric_names):
            for metric2 in metric_names[i+1:]:
                # Extract values for current window
                values1 = [v for _, v in self.metric_buffers[metric1]]
                values2 = [v for _, v in self.metric_buffers[metric2]]
                
                if len(values1) < 10 or len(values2) < 10:
                    continue
                
                # Ensure same length
                min_len = min(len(values1), len(values2))
                values1 = np.array(values1[-min_len:])
                values2 = np.array(values2[-min_len:])
                
                # Calculate correlation
                result = self.detector.calculate_pearson_correlation(values1, values2)
                result.metric1 = metric1
                result.metric2 = metric2
                
                current_correlations.append(result)
                
                # Check for alerts
                self._check_correlation_alerts(result)
        
        # Store history
        self.correlation_history.append({
            'timestamp': datetime.now(),
            'correlations': current_correlations
        })
        
        # Keep only recent history (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.correlation_history = [
            h for h in self.correlation_history 
            if h['timestamp'] > cutoff_time
        ]
    
    def _check_correlation_alerts(self, correlation: CorrelationResult):
        """Check if correlation result should trigger alerts"""
        abs_corr = abs(correlation.correlation_value)
        
        # High correlation alert
        if (abs_corr > self.alert_thresholds['high_correlation'] and 
            correlation.is_significant):
            
            self._send_alert(
                alert_type="high_correlation",
                message=f"🚨 High correlation detected: {correlation.metric1} ↔ {correlation.metric2} "
                       f"({correlation.correlation_value:.3f})"
            )
        
        # Check for sudden correlation changes
        self._check_correlation_change_alert(correlation)
    
    def _check_correlation_change_alert(self, correlation: CorrelationResult):
        """Check for sudden changes in correlation"""
        if len(self.correlation_history) < 2:
            return
        
        # Find previous correlation between same metrics
        prev_corr = None
        for hist_entry in reversed(self.correlation_history[-5:]):  # Look at last 5 entries
            for corr in hist_entry['correlations']:
                if ((corr.metric1 == correlation.metric1 and corr.metric2 == correlation.metric2) or
                    (corr.metric1 == correlation.metric2 and corr.metric2 == correlation.metric1)):
                    prev_corr = corr.correlation_value
                    break
            if prev_corr is not None:
                break
        
        if prev_corr is not None:
            change = abs(correlation.correlation_value - prev_corr)
            if change > self.alert_thresholds['sudden_correlation_change']:
                self._send_alert(
                    alert_type="correlation_change",
                    message=f"📈 Sudden correlation change: {correlation.metric1} ↔ {correlation.metric2} "
                           f"({prev_corr:.3f} → {correlation.correlation_value:.3f})"
                )
    
    def _send_alert(self, alert_type: str, message: str):
        """Send correlation alert"""
        print(f"🚨 CORRELATION ALERT [{alert_type.upper()}]: {message}")
        
        # In real system, this would send to:
        # - PagerDuty/OpsGenie
        # - Slack/Teams
        # - Email notifications
        # - Monitoring dashboards


class CorrelationAnalysisEngine:
    """Main engine for comprehensive correlation analysis"""
    
    def __init__(self):
        self.statistical_detector = StatisticalCorrelationDetector()
        self.lag_analyzer = TimeLaggedCorrelationAnalyzer()
        self.causality_analyzer = GrangerCausalityAnalyzer()
        self.realtime_monitor = RealTimeCorrelationMonitor()
        self.analysis_results = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_dataset(self, data: pd.DataFrame, 
                       metrics_to_analyze: List[str] = None) -> Dict[str, Any]:
        """Comprehensive correlation analysis of dataset"""
        
        if metrics_to_analyze is None:
            metrics_to_analyze = data.select_dtypes(include=[np.number]).columns.tolist()
        
        self.logger.info(f"Analyzing correlations for {len(metrics_to_analyze)} metrics")
        
        results = {
            'basic_correlations': [],
            'lagged_correlations': [],
            'causality_results': [],
            'dependency_graph': None,
            'risk_assessment': {},
            'recommendations': []
        }
        
        # 1. Basic statistical correlations
        for i, metric1 in enumerate(metrics_to_analyze):
            for metric2 in metrics_to_analyze[i+1:]:
                # Skip if too much missing data
                mask = ~(data[metric1].isna() | data[metric2].isna())
                if mask.sum() < len(data) * 0.5:  # At least 50% data
                    continue
                
                # Calculate multiple correlation types
                x = data[metric1].values
                y = data[metric2].values
                
                # Pearson correlation
                pearson_result = self.statistical_detector.calculate_pearson_correlation(x, y)
                pearson_result.metric1 = metric1
                pearson_result.metric2 = metric2
                
                # Spearman correlation  
                spearman_result = self.statistical_detector.calculate_spearman_correlation(x, y)
                spearman_result.metric1 = metric1
                spearman_result.metric2 = metric2
                
                # Mutual information
                mi_score = self.statistical_detector.calculate_mutual_information(x, y)
                
                results['basic_correlations'].extend([pearson_result, spearman_result])
                
                # Store mutual information
                pearson_result.mutual_information = mi_score
        
        # 2. Time-lagged correlation analysis
        for i, metric1 in enumerate(metrics_to_analyze):
            for metric2 in metrics_to_analyze[i+1:]:
                mask = ~(data[metric1].isna() | data[metric2].isna())
                if mask.sum() < len(data) * 0.5:
                    continue
                
                x = data[metric1].values
                y = data[metric2].values
                
                lagged_result = self.lag_analyzer.analyze_lagged_correlation(x, y, metric1, metric2)
                if lagged_result.lag > 0:  # Only store if there's a significant lag
                    results['lagged_correlations'].append(lagged_result)
        
        # 3. Granger causality analysis
        for i, metric1 in enumerate(metrics_to_analyze):
            for metric2 in metrics_to_analyze[i+1:]:
                mask = ~(data[metric1].isna() | data[metric2].isna())
                if mask.sum() < 100:  # Need sufficient data for causality
                    continue
                
                x = data[metric1].values
                y = data[metric2].values
                
                # Test both directions
                causality_x_to_y = self.causality_analyzer.test_granger_causality(
                    x, y, metric1, metric2
                )
                causality_y_to_x = self.causality_analyzer.test_granger_causality(
                    y, x, metric2, metric1
                )
                
                results['causality_results'].extend(causality_x_to_y)
                results['causality_results'].extend(causality_y_to_x)
        
        # 4. Build dependency graph
        results['dependency_graph'] = self._build_dependency_graph(results)
        
        # 5. Risk assessment
        results['risk_assessment'] = self._assess_correlation_risks(results)
        
        # 6. Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        self.analysis_results.append(results)
        return results
    
    def _build_dependency_graph(self, analysis_results: Dict) -> DependencyGraph:
        """Build dependency graph from correlation and causality results"""
        
        # Collect all metrics
        metrics = set()
        edges = []
        
        # Add edges from significant correlations
        for corr in analysis_results['basic_correlations']:
            if corr.is_significant and abs(corr.correlation_value) > 0.5:
                metrics.add(corr.metric1)
                metrics.add(corr.metric2)
                edges.append((corr.metric1, corr.metric2, abs(corr.correlation_value)))
        
        # Add edges from causality (stronger evidence)
        for caus in analysis_results['causality_results']:
            if caus.is_causal:
                metrics.add(caus.cause_metric)
                metrics.add(caus.effect_metric)
                # Use higher weight for causal relationships
                weight = 1.0 - caus.p_value  # Convert p-value to strength
                edges.append((caus.cause_metric, caus.effect_metric, weight))
        
        # Calculate risk scores (metrics with more dependencies = higher risk)
        risk_scores = {}
        for metric in metrics:
            # Count incoming and outgoing dependencies
            incoming = sum(1 for _, to, _ in edges if to == metric)
            outgoing = sum(1 for from_, _, _ in edges if from_ == metric)
            
            # Risk increases with both incoming and outgoing dependencies
            risk_scores[metric] = (incoming * 1.5 + outgoing) / len(metrics)
        
        # Find critical paths (simplified - metrics with highest risk)
        sorted_metrics = sorted(metrics, key=lambda m: risk_scores.get(m, 0), reverse=True)
        critical_paths = [sorted_metrics[:3]]  # Top 3 as critical path
        
        return DependencyGraph(
            nodes=list(metrics),
            edges=edges,
            critical_paths=critical_paths,
            risk_score=risk_scores
        )
    
    def _assess_correlation_risks(self, analysis_results: Dict) -> Dict[str, Any]:
        """Assess risks based on correlation patterns"""
        
        risks = {
            'cascade_failure_risk': 'low',
            'hidden_dependencies': [],
            'critical_services': [],
            'high_risk_correlations': []
        }
        
        # Find high-risk correlations
        high_risk_correlations = []
        for corr in analysis_results['basic_correlations']:
            if (corr.is_significant and 
                abs(corr.correlation_value) > 0.8 and
                corr.correlation_type == 'pearson'):
                high_risk_correlations.append(corr)
        
        risks['high_risk_correlations'] = high_risk_correlations
        
        # Assess cascade failure risk
        if len(high_risk_correlations) > len(analysis_results['dependency_graph'].nodes) * 0.3:
            risks['cascade_failure_risk'] = 'high'
        elif len(high_risk_correlations) > 0:
            risks['cascade_failure_risk'] = 'medium'
        
        # Identify hidden dependencies (high mutual information, low Pearson)
        hidden_deps = []
        for corr in analysis_results['basic_correlations']:
            if (hasattr(corr, 'mutual_information') and 
                corr.mutual_information > 0.3 and
                abs(corr.correlation_value) < 0.3):
                hidden_deps.append((corr.metric1, corr.metric2, corr.mutual_information))
        
        risks['hidden_dependencies'] = hidden_deps
        
        # Identify critical services
        dependency_graph = analysis_results['dependency_graph']
        if dependency_graph:
            critical_services = sorted(
                dependency_graph.risk_score.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]  # Top 3 most critical
            risks['critical_services'] = critical_services
        
        return risks
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        risks = analysis_results['risk_assessment']
        
        # Cascade failure recommendations
        if risks['cascade_failure_risk'] == 'high':
            recommendations.append(
                "🚨 HIGH RISK: Implement circuit breakers between highly correlated services"
            )
            recommendations.append(
                "🔄 Consider bulkhead pattern to isolate failure propagation"
            )
        
        # Hidden dependency recommendations
        if risks['hidden_dependencies']:
            recommendations.append(
                f"🔍 Investigate {len(risks['hidden_dependencies'])} hidden dependencies detected"
            )
            recommendations.append(
                "📊 Add explicit monitoring for non-linear relationships"
            )
        
        # Critical service recommendations
        if risks['critical_services']:
            top_critical = risks['critical_services'][0][0]
            recommendations.append(
                f"⚠️  Focus reliability efforts on critical service: {top_critical}"
            )
            recommendations.append(
                "🔧 Implement redundancy and failover for critical services"
            )
        
        # Monitoring recommendations
        recommendations.append("📈 Set up correlation monitoring with alerting")
        recommendations.append("🧪 Regular chaos engineering to validate dependency assumptions")
        
        return recommendations
    
    def generate_comprehensive_report(self, analysis_results: Dict = None) -> str:
        """Generate comprehensive correlation analysis report"""
        
        if analysis_results is None:
            analysis_results = self.analysis_results[-1] if self.analysis_results else {}
        
        if not analysis_results:
            return "No analysis results available. Run analyze_dataset() first."
        
        report = f"""
🔍 CORRELATION ANALYSIS REPORT
{'='*50}

Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 CORRELATION SUMMARY
{'-'*25}
Basic Correlations Found: {len(analysis_results.get('basic_correlations', []))}
Significant Correlations: {sum(1 for c in analysis_results.get('basic_correlations', []) if c.is_significant)}
Time-Lagged Correlations: {len(analysis_results.get('lagged_correlations', []))}
Causal Relationships: {sum(1 for c in analysis_results.get('causality_results', []) if c.is_causal)}

🎯 HIGH-RISK CORRELATIONS
{'-'*25}"""
        
        high_risk_corrs = analysis_results['risk_assessment'].get('high_risk_correlations', [])
        for corr in high_risk_corrs[:5]:  # Top 5
            report += f"""
{corr.metric1} ↔ {corr.metric2}
  Correlation: {corr.correlation_value:.3f} ({corr.strength})
  P-value: {corr.p_value:.6f}
  Risk Level: HIGH"""
        
        report += f"""

🔗 DEPENDENCY GRAPH
{'-'*18}
Services/Metrics: {len(analysis_results['dependency_graph'].nodes)}
Dependencies: {len(analysis_results['dependency_graph'].edges)}
Critical Path: {' → '.join(analysis_results['dependency_graph'].critical_paths[0][:3]) if analysis_results['dependency_graph'].critical_paths else 'None'}

⚠️  RISK ASSESSMENT
{'-'*18}
Cascade Failure Risk: {analysis_results['risk_assessment']['cascade_failure_risk'].upper()}
Hidden Dependencies: {len(analysis_results['risk_assessment']['hidden_dependencies'])}
Critical Services: {len(analysis_results['risk_assessment']['critical_services'])}

💡 TOP RECOMMENDATIONS
{'-'*21}"""
        
        for i, rec in enumerate(analysis_results['recommendations'][:5], 1):
            report += f"\n{i}. {rec}"
        
        # Causality insights
        causal_relationships = [c for c in analysis_results.get('causality_results', []) if c.is_causal]
        if causal_relationships:
            report += f"""

🎯 CAUSAL RELATIONSHIPS
{'-'*22}"""
            for caus in causal_relationships[:3]:  # Top 3
                report += f"""
{caus.cause_metric} → {caus.effect_metric}
  Lag: {caus.lag} time periods
  P-value: {caus.p_value:.4f}
  Confidence: {(1-caus.p_value)*100:.1f}%"""
        
        # Time-lagged correlations
        lagged_corrs = analysis_results.get('lagged_correlations', [])
        if lagged_corrs:
            report += f"""

⏰ TIME-LAGGED CORRELATIONS
{'-'*27}"""
            for lag_corr in lagged_corrs[:3]:  # Top 3
                report += f"""
{lag_corr.metric1} → {lag_corr.metric2} (lag: {lag_corr.lag}min)
  Correlation: {lag_corr.correlation_value:.3f}
  Significance: {'Yes' if lag_corr.is_significant else 'No'}"""
        
        report += f"""

💰 BUSINESS IMPACT ESTIMATION
{'-'*29}
High-risk correlations can lead to:
- Cascade failures: ₹1-10Cr lost revenue/hour
- Hidden dependency failures: ₹50L-2Cr impact
- Critical service outages: ₹5-25Cr per incident

🚀 NEXT STEPS
{'-'*13}
1. Implement monitoring for top 5 correlations
2. Set up circuit breakers for high-risk pairs
3. Conduct chaos engineering experiments
4. Review and update dependency documentation
5. Train teams on correlation-aware incident response
"""
        
        return report


def create_sample_system_data():
    """Create sample system metrics data for demonstration"""
    
    # Simulate 7 days of 1-minute intervals
    timestamps = pd.date_range(
        start='2024-01-01', 
        periods=7*24*60, 
        freq='1min'
    )
    
    np.random.seed(42)
    n_points = len(timestamps)
    
    # Create correlated system metrics
    base_load = 0.3 + 0.4 * np.sin(np.arange(n_points) * 2 * np.pi / (24*60))  # Daily cycle
    
    data = {
        'timestamp': timestamps,
        
        # CPU metrics - highly correlated with load
        'cpu_usage': np.clip(
            base_load + 0.2 * np.random.normal(0, 0.1, n_points), 0, 1
        ),
        
        # Memory usage - correlated with CPU but with lag
        'memory_usage': np.clip(
            np.roll(base_load, 30) + 0.15 * np.random.normal(0, 0.1, n_points), 0, 1
        ),
        
        # Network I/O - correlated with load
        'network_io': np.clip(
            base_load * 1.5 + 0.3 * np.random.normal(0, 0.1, n_points), 0, 2
        ),
        
        # Database connections - lagged correlation with load
        'db_connections': np.clip(
            50 + 200 * np.roll(base_load, 15) + 20 * np.random.normal(0, 1, n_points), 0, 300
        ),
        
        # Error rate - inversely correlated with system health
        'error_rate': np.clip(
            0.05 - 0.04 * base_load + 0.02 * np.random.normal(0, 1, n_points), 0, 0.2
        ),
        
        # Response time - correlated with load and errors
        'response_time_ms': np.clip(
            100 + 300 * base_load + 100 * (0.05 - 0.04 * base_load) + 50 * np.random.normal(0, 1, n_points), 
            50, 1000
        ),
        
        # Queue depth - leading indicator of problems
        'queue_depth': np.clip(
            10 * base_load + 5 * np.random.normal(0, 1, n_points), 0, 100
        ),
        
        # Cache hit rate - inversely related to load
        'cache_hit_rate': np.clip(
            0.9 - 0.3 * base_load + 0.1 * np.random.normal(0, 0.05, n_points), 0.3, 1.0
        )
    }
    
    return pd.DataFrame(data)


def demo_indian_platform_analysis():
    """Demo correlation analysis for Indian platform metrics"""
    
    print("🇮🇳 INDIAN PLATFORM CORRELATION ANALYSIS DEMO")
    print("="*55)
    
    # Create sample data representing Indian e-commerce platform
    print("📊 Generating sample metrics data...")
    sample_data = create_sample_system_data()
    
    # Initialize analysis engine
    engine = CorrelationAnalysisEngine()
    
    # Run comprehensive analysis
    print("🔍 Running comprehensive correlation analysis...")
    results = engine.analyze_dataset(
        sample_data, 
        metrics_to_analyze=[
            'cpu_usage', 'memory_usage', 'network_io', 'db_connections',
            'error_rate', 'response_time_ms', 'queue_depth', 'cache_hit_rate'
        ]
    )
    
    # Generate and display report
    report = engine.generate_comprehensive_report(results)
    print(report)
    
    # Demonstrate real-time monitoring
    print("\n🔄 Starting real-time correlation monitoring demo...")
    monitor = engine.realtime_monitor
    
    # Add some sample real-time data
    for i in range(50):
        timestamp = datetime.now()
        
        # Simulate correlated metrics
        base_load = 0.5 + 0.3 * np.sin(i * 0.1)
        
        monitor.add_metric_data('cpu_usage', base_load + random.gauss(0, 0.1), timestamp)
        monitor.add_metric_data('memory_usage', base_load + random.gauss(0, 0.1), timestamp)
        monitor.add_metric_data('response_time', (1 - base_load) * 100 + random.gauss(0, 10), timestamp)
        
        time.sleep(0.1)  # Small delay for demo
    
    # Analyze current correlations
    monitor._analyze_current_correlations()
    
    print("✅ Real-time monitoring demo completed")
    
    # Save results
    with open('correlation_analysis_results.json', 'w') as f:
        # Convert results to JSON-serializable format
        json_results = {
            'basic_correlations': [asdict(c) for c in results['basic_correlations']],
            'risk_assessment': results['risk_assessment'], 
            'recommendations': results['recommendations'],
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'metrics_analyzed': len(sample_data.columns) - 1,  # Exclude timestamp
                'data_points': len(sample_data)
            }
        }
        json.dump(json_results, f, indent=2, default=str)
    
    print("\n📁 Results saved to correlation_analysis_results.json")
    print("\n💡 KEY INSIGHTS:")
    print("- Correlation detection helps prevent cascade failures")
    print("- Time-lagged analysis reveals hidden dependencies") 
    print("- Real-time monitoring enables proactive alerts")
    print("- Causal analysis guides architectural decisions")
    print("💰 Potential savings: ₹5-50Cr by preventing correlated failures")


if __name__ == "__main__":
    demo_indian_platform_analysis()