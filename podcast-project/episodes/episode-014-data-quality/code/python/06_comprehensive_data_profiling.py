#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 6
Comprehensive Data Profiling Scripts

Complete data profiling system for Indian business datasets
Data की पूरी profiling करने का system like banking data analysis

Author: DStudio Team
Context: Data profiling for Indian datasets like banking/fintech/ecommerce
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json
import warnings
from scipy import stats
from collections import Counter
import re
from dataclasses import dataclass
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - डेटा प्रोफ़ाइल - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataQualityMetric:
    """Data quality metric structure"""
    metric_name: str
    value: float
    threshold: float
    status: str  # 'GOOD', 'WARNING', 'CRITICAL'
    description: str

class ComprehensiveDataProfiler:
    """
    Complete data profiling system for Indian business context
    Indian datasets की comprehensive profiling करने का system
    
    Features:
    1. Column-wise profiling
    2. Data quality assessment
    3. Statistical analysis
    4. Pattern detection
    5. Outlier identification
    6. Business rule validation
    7. Data distribution analysis
    8. Visualization generation
    """
    
    def __init__(self):
        """Initialize data profiler"""
        
        # Quality thresholds for Indian business context
        self.quality_thresholds = {
            'completeness': 0.95,      # 95% completeness required
            'uniqueness': 0.98,        # For unique fields like ID
            'consistency': 0.90,       # Format consistency
            'accuracy': 0.95,          # Business rule accuracy
            'validity': 0.90,          # Format validity
            'timeliness': 0.85,        # Data freshness
            'outlier_percentage': 0.05  # Max 5% outliers acceptable
        }
        
        # Indian specific patterns for validation
        self.indian_patterns = {
            'pincode': r'^\d{6}$',
            'mobile': r'^[6-9]\d{9}$',
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
            'gstin': r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z][Z0-9A-Z]$',
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'aadhaar': r'^\d{12}$'
        }
        
        # Indian business domains for categorization
        self.business_domains = {
            'ecommerce': ['order', 'product', 'customer', 'payment', 'delivery'],
            'banking': ['account', 'transaction', 'loan', 'branch', 'kyc'],
            'telecom': ['subscriber', 'usage', 'tower', 'recharge', 'plan'],
            'transport': ['booking', 'route', 'vehicle', 'driver', 'fare'],
            'education': ['student', 'course', 'fee', 'exam', 'result']
        }
        
        logger.info("Comprehensive Data Profiler initialized - प्रोफ़ाइलर तैयार!")

    def profile_dataset_overview(self, df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
        """
        Generate comprehensive dataset overview
        Dataset का complete overview निकालना
        """
        
        logger.info(f"Profiling dataset overview: {dataset_name}")
        
        overview = {
            'dataset_name': dataset_name,
            'profiling_timestamp': datetime.now().isoformat(),
            'basic_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'duplicate_rows': df.duplicated().sum(),
                'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100
            },
            'column_types': {
                'numeric': len(df.select_dtypes(include=[np.number]).columns),
                'categorical': len(df.select_dtypes(include=['object']).columns),
                'datetime': len(df.select_dtypes(include=['datetime64']).columns),
                'boolean': len(df.select_dtypes(include=['bool']).columns)
            },
            'data_quality_summary': {},
            'business_context': self._identify_business_domain(df.columns.tolist())
        }
        
        # Calculate overall data quality metrics
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        
        overview['data_quality_summary'] = {
            'overall_completeness': ((total_cells - missing_cells) / total_cells) * 100,
            'columns_with_missing': (df.isnull().sum() > 0).sum(),
            'most_missing_column': df.isnull().sum().idxmax() if missing_cells > 0 else None,
            'max_missing_percentage': (df.isnull().sum().max() / len(df)) * 100
        }
        
        return overview

    def profile_column_detailed(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Detailed profiling of individual column
        Individual column की detailed analysis करना
        """
        
        if column not in df.columns:
            return {'error': f'Column {column} not found in dataset'}
        
        col_data = df[column]
        
        profile = {
            'column_name': column,
            'data_type': str(col_data.dtype),
            'total_count': len(col_data),
            'missing_count': col_data.isnull().sum(),
            'missing_percentage': (col_data.isnull().sum() / len(col_data)) * 100,
            'unique_count': col_data.nunique(),
            'uniqueness_percentage': (col_data.nunique() / len(col_data)) * 100,
            'duplicate_count': col_data.duplicated().sum(),
            'most_frequent_values': {},
            'statistical_summary': {},
            'pattern_analysis': {},
            'quality_metrics': []
        }
        
        # Handle different data types
        if col_data.dtype in ['object', 'string']:
            profile.update(self._profile_text_column(col_data))
        elif np.issubdtype(col_data.dtype, np.number):
            profile.update(self._profile_numeric_column(col_data))
        elif np.issubdtype(col_data.dtype, np.datetime64):
            profile.update(self._profile_datetime_column(col_data))
        
        # Most frequent values
        if col_data.dtype == 'object':
            value_counts = col_data.value_counts().head(10)
            profile['most_frequent_values'] = {
                str(k): int(v) for k, v in value_counts.items()
            }
        
        # Quality metrics assessment
        profile['quality_metrics'] = self._assess_column_quality(col_data, column)
        
        return profile

    def _profile_text_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Profile text/categorical column"""
        
        # Remove null values for analysis
        non_null_data = col_data.dropna()
        
        if len(non_null_data) == 0:
            return {'text_analysis': 'No non-null values to analyze'}
        
        text_profile = {
            'text_analysis': {
                'avg_length': non_null_data.astype(str).str.len().mean(),
                'min_length': non_null_data.astype(str).str.len().min(),
                'max_length': non_null_data.astype(str).str.len().max(),
                'empty_strings': (non_null_data.astype(str).str.len() == 0).sum(),
                'whitespace_only': non_null_data.astype(str).str.strip().eq('').sum()
            },
            'pattern_analysis': self._analyze_text_patterns(non_null_data),
            'case_analysis': {
                'uppercase': non_null_data.astype(str).str.isupper().sum(),
                'lowercase': non_null_data.astype(str).str.islower().sum(),
                'title_case': non_null_data.astype(str).str.istitle().sum(),
                'mixed_case': 0  # Will calculate
            }
        }
        
        # Calculate mixed case
        total_alpha = non_null_data.astype(str).str.isalpha().sum()
        pure_cases = (text_profile['case_analysis']['uppercase'] + 
                     text_profile['case_analysis']['lowercase'] + 
                     text_profile['case_analysis']['title_case'])
        text_profile['case_analysis']['mixed_case'] = max(0, total_alpha - pure_cases)
        
        return text_profile

    def _profile_numeric_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Profile numeric column"""
        
        non_null_data = col_data.dropna()
        
        if len(non_null_data) == 0:
            return {'numeric_analysis': 'No non-null values to analyze'}
        
        numeric_profile = {
            'statistical_summary': {
                'mean': float(non_null_data.mean()),
                'median': float(non_null_data.median()),
                'mode': float(non_null_data.mode().iloc[0]) if not non_null_data.mode().empty else None,
                'std_dev': float(non_null_data.std()),
                'variance': float(non_null_data.var()),
                'min_value': float(non_null_data.min()),
                'max_value': float(non_null_data.max()),
                'range': float(non_null_data.max() - non_null_data.min()),
                'q1': float(non_null_data.quantile(0.25)),
                'q3': float(non_null_data.quantile(0.75)),
                'iqr': float(non_null_data.quantile(0.75) - non_null_data.quantile(0.25)),
                'skewness': float(stats.skew(non_null_data)),
                'kurtosis': float(stats.kurtosis(non_null_data))
            },
            'outlier_analysis': self._detect_outliers(non_null_data),
            'distribution_analysis': {
                'is_normal': stats.shapiro(non_null_data.sample(min(5000, len(non_null_data))))[1] > 0.05,
                'zero_count': (non_null_data == 0).sum(),
                'negative_count': (non_null_data < 0).sum(),
                'positive_count': (non_null_data > 0).sum()
            }
        }
        
        return numeric_profile

    def _profile_datetime_column(self, col_data: pd.Series) -> Dict[str, Any]:
        """Profile datetime column"""
        
        non_null_data = col_data.dropna()
        
        if len(non_null_data) == 0:
            return {'datetime_analysis': 'No non-null values to analyze'}
        
        datetime_profile = {
            'datetime_analysis': {
                'earliest_date': non_null_data.min().isoformat(),
                'latest_date': non_null_data.max().isoformat(),
                'date_range_days': (non_null_data.max() - non_null_data.min()).days,
                'future_dates': (non_null_data > datetime.now()).sum(),
                'weekend_count': non_null_data.dt.dayofweek.isin([5, 6]).sum(),
                'business_days': non_null_data.dt.dayofweek.isin(range(5)).sum()
            },
            'temporal_patterns': {
                'year_distribution': non_null_data.dt.year.value_counts().to_dict(),
                'month_distribution': non_null_data.dt.month.value_counts().to_dict(),
                'day_of_week_distribution': non_null_data.dt.dayofweek.value_counts().to_dict(),
                'hour_distribution': non_null_data.dt.hour.value_counts().to_dict() if non_null_data.dt.hour.nunique() > 1 else {}
            }
        }
        
        return datetime_profile

    def _analyze_text_patterns(self, col_data: pd.Series) -> Dict[str, Any]:
        """Analyze text patterns for Indian context"""
        
        pattern_matches = {}
        
        for pattern_name, pattern in self.indian_patterns.items():
            matches = col_data.astype(str).str.match(pattern).sum()
            pattern_matches[pattern_name] = {
                'matches': int(matches),
                'percentage': (matches / len(col_data)) * 100
            }
        
        # Additional pattern analysis
        text_strings = col_data.astype(str)
        
        pattern_analysis = {
            'indian_patterns': pattern_matches,
            'format_consistency': {
                'all_numeric': text_strings.str.isdigit().sum(),
                'all_alpha': text_strings.str.isalpha().sum(),
                'alphanumeric': text_strings.str.isalnum().sum(),
                'contains_special_chars': text_strings.str.contains(r'[^a-zA-Z0-9\s]').sum(),
                'email_format': text_strings.str.contains(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').sum(),
                'phone_format': text_strings.str.contains(r'^[\+]?[0-9]{10,15}$').sum()
            }
        }
        
        return pattern_analysis

    def _detect_outliers(self, col_data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using multiple methods"""
        
        outlier_analysis = {}
        
        # IQR method
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_outliers = ((col_data < lower_bound) | (col_data > upper_bound)).sum()
        
        # Z-score method
        z_scores = np.abs(stats.zscore(col_data))
        z_outliers = (z_scores > 3).sum()
        
        # Modified Z-score method
        median = col_data.median()
        mad = np.median(np.abs(col_data - median))
        modified_z_scores = 0.6745 * (col_data - median) / mad
        modified_z_outliers = (np.abs(modified_z_scores) > 3.5).sum()
        
        outlier_analysis = {
            'iqr_method': {
                'outlier_count': int(iqr_outliers),
                'outlier_percentage': (iqr_outliers / len(col_data)) * 100,
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            },
            'z_score_method': {
                'outlier_count': int(z_outliers),
                'outlier_percentage': (z_outliers / len(col_data)) * 100
            },
            'modified_z_score_method': {
                'outlier_count': int(modified_z_outliers),
                'outlier_percentage': (modified_z_outliers / len(col_data)) * 100
            }
        }
        
        return outlier_analysis

    def _assess_column_quality(self, col_data: pd.Series, column_name: str) -> List[DataQualityMetric]:
        """Assess data quality metrics for column"""
        
        metrics = []
        
        # Completeness
        completeness = (1 - col_data.isnull().sum() / len(col_data)) * 100
        metrics.append(DataQualityMetric(
            'Completeness',
            completeness,
            self.quality_thresholds['completeness'] * 100,
            'GOOD' if completeness >= self.quality_thresholds['completeness'] * 100 else 'WARNING' if completeness >= 80 else 'CRITICAL',
            f'Column has {completeness:.2f}% complete values'
        ))
        
        # Uniqueness (for potential ID columns)
        if 'id' in column_name.lower() or 'key' in column_name.lower():
            uniqueness = (col_data.nunique() / col_data.count()) * 100
            metrics.append(DataQualityMetric(
                'Uniqueness',
                uniqueness,
                self.quality_thresholds['uniqueness'] * 100,
                'GOOD' if uniqueness >= self.quality_thresholds['uniqueness'] * 100 else 'WARNING' if uniqueness >= 90 else 'CRITICAL',
                f'Column has {uniqueness:.2f}% unique values'
            ))
        
        # Validity (for known patterns)
        if col_data.dtype == 'object':
            for pattern_name, pattern in self.indian_patterns.items():
                if pattern_name in column_name.lower():
                    valid_count = col_data.astype(str).str.match(pattern).sum()
                    validity = (valid_count / col_data.count()) * 100
                    metrics.append(DataQualityMetric(
                        f'{pattern_name.upper()} Format Validity',
                        validity,
                        self.quality_thresholds['validity'] * 100,
                        'GOOD' if validity >= self.quality_thresholds['validity'] * 100 else 'WARNING' if validity >= 70 else 'CRITICAL',
                        f'Column has {validity:.2f}% valid {pattern_name.upper()} format'
                    ))
                    break
        
        # Outlier percentage (for numeric columns)
        if np.issubdtype(col_data.dtype, np.number):
            non_null_data = col_data.dropna()
            if len(non_null_data) > 0:
                Q1 = non_null_data.quantile(0.25)
                Q3 = non_null_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((non_null_data < Q1 - 1.5 * IQR) | (non_null_data > Q3 + 1.5 * IQR)).sum()
                outlier_percentage = (outliers / len(non_null_data)) * 100
                
                metrics.append(DataQualityMetric(
                    'Outlier Percentage',
                    outlier_percentage,
                    self.quality_thresholds['outlier_percentage'] * 100,
                    'GOOD' if outlier_percentage <= self.quality_thresholds['outlier_percentage'] * 100 else 'WARNING' if outlier_percentage <= 10 else 'CRITICAL',
                    f'Column has {outlier_percentage:.2f}% outliers'
                ))
        
        return metrics

    def _identify_business_domain(self, column_names: List[str]) -> str:
        """Identify business domain based on column names"""
        
        column_names_lower = [col.lower() for col in column_names]
        domain_scores = {}
        
        for domain, keywords in self.business_domains.items():
            score = sum(1 for keyword in keywords 
                       if any(keyword in col for col in column_names_lower))
            domain_scores[domain] = score
        
        if not domain_scores or max(domain_scores.values()) == 0:
            return 'general'
        
        return max(domain_scores, key=domain_scores.get)

    def generate_data_quality_report(self, df: pd.DataFrame, 
                                   dataset_name: str = "Dataset",
                                   sample_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report
        Complete data quality report generate करना
        """
        
        logger.info(f"Generating comprehensive data quality report for {dataset_name}")
        
        # Overall dataset overview
        overview = self.profile_dataset_overview(df, dataset_name)
        
        # Column-wise profiling
        columns_to_profile = sample_columns if sample_columns else df.columns.tolist()
        if len(columns_to_profile) > 20:  # Limit to prevent overwhelming reports
            columns_to_profile = columns_to_profile[:20]
            logger.info(f"Profiling limited to first 20 columns")
        
        column_profiles = {}
        for col in columns_to_profile:
            column_profiles[col] = self.profile_column_detailed(df, col)
        
        # Aggregate quality metrics
        all_metrics = []
        for col_profile in column_profiles.values():
            all_metrics.extend(col_profile.get('quality_metrics', []))
        
        quality_summary = {
            'total_metrics': len(all_metrics),
            'good_metrics': len([m for m in all_metrics if m.status == 'GOOD']),
            'warning_metrics': len([m for m in all_metrics if m.status == 'WARNING']),
            'critical_metrics': len([m for m in all_metrics if m.status == 'CRITICAL']),
        }
        
        quality_summary['overall_quality_score'] = (
            (quality_summary['good_metrics'] * 100 + quality_summary['warning_metrics'] * 60) / 
            quality_summary['total_metrics'] if quality_summary['total_metrics'] > 0 else 0
        )
        
        # Data quality recommendations
        recommendations = self._generate_recommendations(overview, column_profiles, quality_summary)
        
        comprehensive_report = {
            'report_metadata': {
                'dataset_name': dataset_name,
                'generation_timestamp': datetime.now().isoformat(),
                'profiled_columns': len(columns_to_profile),
                'total_columns': len(df.columns)
            },
            'dataset_overview': overview,
            'column_profiles': column_profiles,
            'quality_summary': quality_summary,
            'recommendations': recommendations,
            'executive_summary': self._create_executive_summary(overview, quality_summary)
        }
        
        logger.info(f"Report generated with quality score: {quality_summary['overall_quality_score']:.2f}%")
        
        return comprehensive_report

    def _generate_recommendations(self, overview: Dict, column_profiles: Dict, 
                                quality_summary: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Overall data quality
        if quality_summary['overall_quality_score'] < 70:
            recommendations.append(
                "CRITICAL: Overall data quality is below acceptable levels. "
                "Implement immediate data quality improvements."
            )
        elif quality_summary['overall_quality_score'] < 85:
            recommendations.append(
                "WARNING: Data quality needs improvement. "
                "Consider implementing data validation at source."
            )
        
        # Missing data
        if overview['data_quality_summary']['overall_completeness'] < 90:
            recommendations.append(
                f"Address missing data issues. Overall completeness is "
                f"{overview['data_quality_summary']['overall_completeness']:.2f}%. "
                f"Focus on column: {overview['data_quality_summary']['most_missing_column']}"
            )
        
        # Duplicate data
        if overview['basic_info']['duplicate_percentage'] > 5:
            recommendations.append(
                f"High duplicate rate detected: {overview['basic_info']['duplicate_percentage']:.2f}%. "
                "Implement deduplication processes."
            )
        
        # Column-specific recommendations
        for col_name, col_profile in column_profiles.items():
            critical_metrics = [m for m in col_profile.get('quality_metrics', []) if m.status == 'CRITICAL']
            if critical_metrics:
                for metric in critical_metrics:
                    recommendations.append(
                        f"Column '{col_name}': {metric.description} - {metric.metric_name} needs attention."
                    )
        
        # Business domain specific recommendations
        business_domain = overview['business_context']
        if business_domain == 'banking':
            recommendations.append(
                "Banking domain detected. Ensure IFSC, account numbers, and transaction amounts are validated."
            )
        elif business_domain == 'ecommerce':
            recommendations.append(
                "E-commerce domain detected. Validate product IDs, customer emails, and order amounts."
            )
        
        if not recommendations:
            recommendations.append("Data quality looks good! Continue monitoring regularly.")
        
        return recommendations

    def _create_executive_summary(self, overview: Dict, quality_summary: Dict) -> str:
        """Create executive summary"""
        
        summary = f"""
        Data Quality Executive Summary:
        
        Dataset: {overview['dataset_name']}
        Records: {overview['basic_info']['total_rows']:,}
        Columns: {overview['basic_info']['total_columns']}
        
        Overall Quality Score: {quality_summary['overall_quality_score']:.2f}%
        Completeness: {overview['data_quality_summary']['overall_completeness']:.2f}%
        Duplicate Rate: {overview['basic_info']['duplicate_percentage']:.2f}%
        
        Quality Status: {'EXCELLENT' if quality_summary['overall_quality_score'] > 90 
                        else 'GOOD' if quality_summary['overall_quality_score'] > 75
                        else 'NEEDS IMPROVEMENT'}
        
        Business Context: {overview['business_context'].title()}
        """
        
        return summary.strip()

    def create_visualizations(self, df: pd.DataFrame, report: Dict[str, Any], 
                            output_dir: str = "./profiling_charts") -> Dict[str, str]:
        """
        Create visualization charts for the profiling report
        Report के लिए charts बनाना
        """
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        chart_files = {}
        
        # 1. Data Quality Overview Chart
        quality_metrics = ['good_metrics', 'warning_metrics', 'critical_metrics']
        values = [report['quality_summary'][metric] for metric in quality_metrics]
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        
        fig = go.Figure(data=[go.Bar(
            x=['Good', 'Warning', 'Critical'],
            y=values,
            marker_color=colors
        )])
        
        fig.update_layout(
            title='Data Quality Metrics Overview',
            xaxis_title='Quality Status',
            yaxis_title='Number of Metrics'
        )
        
        chart_path = os.path.join(output_dir, 'quality_overview.html')
        fig.write_html(chart_path)
        chart_files['quality_overview'] = chart_path
        
        # 2. Missing Data Heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=True, yticklabels=False, cmap='viridis')
        plt.title('Missing Data Pattern')
        plt.tight_layout()
        
        missing_chart_path = os.path.join(output_dir, 'missing_data_heatmap.png')
        plt.savefig(missing_chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files['missing_data'] = missing_chart_path
        
        # 3. Completeness by Column
        completeness_data = []
        for col in df.columns:
            completeness = (1 - df[col].isnull().sum() / len(df)) * 100
            completeness_data.append({'Column': col, 'Completeness': completeness})
        
        completeness_df = pd.DataFrame(completeness_data)
        
        fig = px.bar(completeness_df, x='Column', y='Completeness',
                     title='Data Completeness by Column',
                     color='Completeness',
                     color_continuous_scale='RdYlGn')
        fig.update_xaxis(tickangle=45)
        
        completeness_chart_path = os.path.join(output_dir, 'completeness_by_column.html')
        fig.write_html(completeness_chart_path)
        chart_files['completeness'] = completeness_chart_path
        
        logger.info(f"Visualizations created in {output_dir}")
        
        return chart_files

def create_sample_indian_dataset(num_records: int = 5000) -> pd.DataFrame:
    """Create sample Indian business dataset for profiling demo"""
    
    import random
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    random.seed(42)
    
    # Indian cities and states
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
    states = ['MH', 'DL', 'KA', 'TN', 'WB', 'TG', 'MH', 'GJ']
    
    # Generate sample data
    data = {
        'customer_id': [f'CUST{i:08d}' for i in range(1, num_records + 1)],
        'customer_name': [f'Customer {i}' for i in range(1, num_records + 1)],
        'email': [f'customer{i}@{"gmail.com" if i % 3 == 0 else "yahoo.com" if i % 3 == 1 else "rediffmail.com"}' for i in range(1, num_records + 1)],
        'mobile': [f'{random.choice([6,7,8,9])}{random.randint(100000000, 999999999)}' for _ in range(num_records)],
        'pan': [f'{"ABCDEFGHIJ"[i%10]}{"ABCDEFGHIJ"[(i+1)%10]}{"ABCDEFGHIJ"[(i+2)%10]}{"ABCDEFGHIJ"[(i+3)%10]}{"ABCDEFGHIJ"[(i+4)%10]}{random.randint(1000, 9999)}{"ABCDEFGHIJ"[(i+5)%10]}' for i in range(num_records)],
        'account_balance': np.random.exponential(scale=50000, size=num_records),
        'transaction_amount': np.random.lognormal(mean=7, sigma=1.5, size=num_records),
        'city': np.random.choice(cities, num_records),
        'state': [states[cities.index(city)] for city in np.random.choice(cities, num_records)],
        'pincode': [f'{random.randint(100000, 999999)}' for _ in range(num_records)],
        'registration_date': pd.date_range(
            start=datetime.now() - timedelta(days=2*365),
            end=datetime.now(),
            periods=num_records
        ),
        'is_active': np.random.choice([True, False], num_records, p=[0.85, 0.15]),
        'credit_score': np.random.normal(750, 100, num_records).astype(int)
    }
    
    # Introduce some data quality issues for realistic profiling
    
    # Missing values
    missing_indices = np.random.choice(num_records, size=num_records//20, replace=False)
    for idx in missing_indices[:num_records//40]:
        data['email'][idx] = None
    for idx in missing_indices[num_records//40:]:
        data['mobile'][idx] = None
    
    # Invalid formats
    for i in range(num_records//50):
        data['mobile'][i] = f'123456789{i}'  # Invalid mobile
        data['pan'][i] = f'INVALID{i:06d}'   # Invalid PAN
        data['pincode'][i] = f'{random.randint(10000, 99999)}'  # Invalid pincode (5 digits)
    
    # Outliers
    outlier_indices = np.random.choice(num_records, size=num_records//100, replace=False)
    for idx in outlier_indices:
        data['account_balance'][idx] = random.randint(10000000, 50000000)  # Very high balance
        data['credit_score'][idx] = random.choice([300, 900])  # Extreme credit scores
    
    # Duplicates
    duplicate_indices = np.random.choice(num_records-100, size=20, replace=False)
    for i, idx in enumerate(duplicate_indices):
        data['customer_id'][idx + 100] = data['customer_id'][idx]  # Duplicate IDs
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of data profiling system"""
    
    print("📊 Comprehensive Data Profiling System Demo")
    print("डेटा प्रोफ़ाइलिंग प्रणाली का प्रदर्शन\n")
    
    # Initialize profiler
    profiler = ComprehensiveDataProfiler()
    
    # Create sample dataset
    print("Creating sample Indian business dataset...")
    sample_df = create_sample_indian_dataset(1000)
    print(f"Sample dataset created with {len(sample_df)} records and {len(sample_df.columns)} columns\n")
    
    # Generate comprehensive report
    print("Generating comprehensive data quality report...")
    report = profiler.generate_data_quality_report(
        sample_df, 
        dataset_name="Indian Customer Banking Data",
        sample_columns=sample_df.columns.tolist()[:10]  # Profile first 10 columns
    )
    
    # Display executive summary
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    print(report['executive_summary'])
    
    # Display quality summary
    print("\n" + "="*60)
    print("QUALITY METRICS SUMMARY")
    print("="*60)
    quality_summary = report['quality_summary']
    print(f"Overall Quality Score: {quality_summary['overall_quality_score']:.2f}%")
    print(f"Total Metrics Evaluated: {quality_summary['total_metrics']}")
    print(f"Good Metrics: {quality_summary['good_metrics']} ✅")
    print(f"Warning Metrics: {quality_summary['warning_metrics']} ⚠️")
    print(f"Critical Metrics: {quality_summary['critical_metrics']} ❌")
    
    # Display dataset overview
    print("\n" + "="*60)
    print("DATASET OVERVIEW")
    print("="*60)
    overview = report['dataset_overview']
    basic_info = overview['basic_info']
    print(f"Total Rows: {basic_info['total_rows']:,}")
    print(f"Total Columns: {basic_info['total_columns']}")
    print(f"Memory Usage: {basic_info['memory_usage_mb']:.2f} MB")
    print(f"Duplicate Rows: {basic_info['duplicate_rows']} ({basic_info['duplicate_percentage']:.2f}%)")
    print(f"Business Domain: {overview['business_context'].title()}")
    
    print(f"\nData Quality Summary:")
    dq_summary = overview['data_quality_summary']
    print(f"Overall Completeness: {dq_summary['overall_completeness']:.2f}%")
    print(f"Columns with Missing Data: {dq_summary['columns_with_missing']}")
    if dq_summary['most_missing_column']:
        print(f"Most Missing Column: {dq_summary['most_missing_column']} ({dq_summary['max_missing_percentage']:.2f}%)")
    
    # Display sample column profiles
    print("\n" + "="*60)
    print("SAMPLE COLUMN PROFILES")
    print("="*60)
    
    sample_columns = ['customer_id', 'email', 'account_balance']
    for col in sample_columns:
        if col in report['column_profiles']:
            col_profile = report['column_profiles'][col]
            print(f"\nColumn: {col}")
            print(f"  Data Type: {col_profile['data_type']}")
            print(f"  Missing: {col_profile['missing_count']} ({col_profile['missing_percentage']:.2f}%)")
            print(f"  Unique Values: {col_profile['unique_count']} ({col_profile['uniqueness_percentage']:.2f}%)")
            
            # Show quality metrics
            if col_profile['quality_metrics']:
                print("  Quality Metrics:")
                for metric in col_profile['quality_metrics']:
                    status_emoji = "✅" if metric.status == "GOOD" else "⚠️" if metric.status == "WARNING" else "❌"
                    print(f"    {metric.metric_name}: {metric.value:.2f}% {status_emoji}")
    
    # Display recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Create visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    try:
        chart_files = profiler.create_visualizations(sample_df, report)
        print("Visualizations created:")
        for chart_name, file_path in chart_files.items():
            print(f"  {chart_name}: {file_path}")
    except Exception as e:
        print(f"Visualization creation failed: {str(e)}")
    
    # Save report to JSON
    report_file = "data_quality_report.json"
    try:
        # Convert DataQualityMetric objects to dictionaries for JSON serialization
        json_report = json.loads(json.dumps(report, default=lambda x: x.__dict__ if hasattr(x, '__dict__') else str(x)))
        
        with open(report_file, 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"Report saving failed: {str(e)}")
    
    print("\n✅ Comprehensive Data Profiling Demo Complete!")
    print("प्रणाली तैयार है - Ready for production data profiling!")
    
    return {
        'report': report,
        'sample_data': sample_df,
        'chart_files': chart_files if 'chart_files' in locals() else {}
    }

if __name__ == "__main__":
    results = main()