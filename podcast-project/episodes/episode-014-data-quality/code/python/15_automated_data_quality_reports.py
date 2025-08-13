#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 15
Automated Data Quality Reporting System

Complete automated data quality reporting with dashboards and alerts
Dashboards और alerts के साथ complete automated data quality reporting

Author: DStudio Team
Context: Data quality reporting like Flipkart/Amazon data governance teams
Scale: Generate reports for 100+ TB data across 500+ data sources
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import jinja2
from pathlib import Path
import schedule
import time
import threading

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - डेटा रिपोर्ट - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataQualityScore:
    """Data quality score components"""
    completeness: float  # % of non-null values
    uniqueness: float   # % of unique values where expected
    validity: float     # % of values matching format rules
    consistency: float  # % of consistent values across sources
    timeliness: float   # % of recent/up-to-date records
    accuracy: float     # % of accurate values (if ground truth available)
    overall_score: float = 0.0

@dataclass
class DataSourceReport:
    """Individual data source quality report"""
    source_id: str
    source_name: str
    source_type: str
    total_records: int
    quality_score: DataQualityScore
    issues_found: List[Dict[str, Any]]
    trending: str  # 'improving', 'stable', 'degrading'
    last_updated: datetime
    sla_status: str  # 'met', 'warning', 'breached'

@dataclass
class ExecutiveSummary:
    """Executive summary for data quality reports"""
    report_period: str
    total_sources_monitored: int
    sources_meeting_sla: int
    critical_issues: int
    improvement_opportunities: int
    cost_impact_estimate: float  # in INR
    key_recommendations: List[str]

class AutomatedDataQualityReporter:
    """
    Complete automated data quality reporting system
    Complete automated data quality reporting और dashboard system
    
    Features:
    1. Automated quality score calculation
    2. Trend analysis and anomaly detection
    3. Executive and technical reports
    4. Email/Slack notifications
    5. Interactive dashboards
    6. SLA monitoring and alerting
    
    Scale: Handle reporting for 100+ TB data across 500+ sources
    """
    
    def __init__(self, config: Dict = None):
        """Initialize automated reporting system"""
        
        self.config = config or {}
        
        # Database for storing quality metrics
        self.db_path = self.config.get('db_path', 'dq_reports.db')
        self.db_connection = None
        
        # Report templates
        self.template_dir = Path(self.config.get('template_dir', './templates'))
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
        
        # Email configuration
        self.email_config = self.config.get('email', {})
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 95.0,
            'good': 80.0,
            'acceptable': 70.0,
            'poor': 50.0
        }
        
        # SLA definitions
        self.sla_definitions = {
            'critical': {'min_score': 95.0, 'max_delay_hours': 1},
            'high': {'min_score': 85.0, 'max_delay_hours': 4},
            'medium': {'min_score': 75.0, 'max_delay_hours': 12},
            'low': {'min_score': 60.0, 'max_delay_hours': 24}
        }
        
        # Cost impact models (per issue in INR)
        self.cost_models = {
            'data_downtime': 50000,  # 50k INR per hour
            'incorrect_decisions': 100000,  # 1 lakh per bad decision
            'customer_impact': 25000,  # 25k per affected customer
            'compliance_risk': 200000  # 2 lakh per compliance issue
        }
        
        # Initialize database
        self._init_database()
        
        # Create template directory if not exists
        self.template_dir.mkdir(exist_ok=True)
        self._create_default_templates()
        
        logger.info("Automated Data Quality Reporter initialized - स्वचालित रिपोर्टर तैयार!")

    def _init_database(self):
        """Initialize database for storing reports and metrics"""
        try:
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Quality metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT,
                    source_name TEXT,
                    timestamp DATETIME,
                    completeness REAL,
                    uniqueness REAL,
                    validity REAL,
                    consistency REAL,
                    timeliness REAL,
                    accuracy REAL,
                    overall_score REAL,
                    total_records INTEGER,
                    issues_json TEXT,
                    sla_status TEXT
                )
            ''')
            
            # Reports history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports_history (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT,
                    report_period TEXT,
                    generated_at DATETIME,
                    recipients TEXT,
                    file_path TEXT,
                    summary_json TEXT
                )
            ''')
            
            # SLA breaches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sla_breaches (
                    breach_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    breach_type TEXT,
                    severity TEXT,
                    detected_at DATETIME,
                    resolved_at DATETIME,
                    impact_description TEXT,
                    cost_impact REAL
                )
            ''')
            
            # Alerts log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts_log (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT,
                    source_id TEXT,
                    message TEXT,
                    severity TEXT,
                    sent_at DATETIME,
                    recipients TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Reporting database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _create_default_templates(self):
        """Create default report templates"""
        
        # Executive summary template
        executive_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Quality Executive Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2E86AB; color: white; padding: 20px; }
                .summary-box { background-color: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .metric { display: inline-block; margin: 10px; text-align: center; }
                .metric-value { font-size: 24px; font-weight: bold; }
                .red { color: #d32f2f; }
                .orange { color: #f57c00; }
                .green { color: #388e3c; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Quality Executive Summary</h1>
                <p>Report Period: {{ summary.report_period }}</p>
                <p>Generated: {{ generated_at }}</p>
            </div>
            
            <div class="summary-box">
                <h2>Key Metrics</h2>
                <div class="metric">
                    <div class="metric-value green">{{ summary.sources_meeting_sla }}</div>
                    <div>Sources Meeting SLA</div>
                </div>
                <div class="metric">
                    <div class="metric-value {{ 'red' if summary.critical_issues > 0 else 'green' }}">{{ summary.critical_issues }}</div>
                    <div>Critical Issues</div>
                </div>
                <div class="metric">
                    <div class="metric-value">₹{{ "%.2f"|format(summary.cost_impact_estimate) }}</div>
                    <div>Est. Cost Impact</div>
                </div>
            </div>
            
            <h2>Top Data Sources by Quality Score</h2>
            <table>
                <tr>
                    <th>Source Name</th>
                    <th>Quality Score</th>
                    <th>Status</th>
                    <th>Trend</th>
                    <th>Records</th>
                </tr>
                {% for source in top_sources %}
                <tr>
                    <td>{{ source.source_name }}</td>
                    <td>{{ "%.1f"|format(source.quality_score.overall_score) }}%</td>
                    <td class="{{ source.sla_status }}">{{ source.sla_status.upper() }}</td>
                    <td>{{ source.trending }}</td>
                    <td>{{ "{:,}"|format(source.total_records) }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>Key Recommendations</h2>
            <ul>
                {% for rec in summary.key_recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </body>
        </html>
        '''
        
        # Technical report template
        technical_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technical Data Quality Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #1976D2; color: white; padding: 20px; }
                .source-section { border: 1px solid #ddd; margin: 20px 0; padding: 15px; }
                .quality-scores { display: flex; justify-content: space-between; }
                .score { text-align: center; }
                .score-value { font-size: 18px; font-weight: bold; }
                .issues-list { background-color: #fff3cd; padding: 10px; margin: 10px 0; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Technical Data Quality Report</h1>
                <p>Generated: {{ generated_at }}</p>
                <p>Period: {{ report_period }}</p>
            </div>
            
            {% for source in sources %}
            <div class="source-section">
                <h2>{{ source.source_name }}</h2>
                <p><strong>Source ID:</strong> {{ source.source_id }}</p>
                <p><strong>Type:</strong> {{ source.source_type }}</p>
                <p><strong>Total Records:</strong> {{ "{:,}"|format(source.total_records) }}</p>
                <p><strong>Last Updated:</strong> {{ source.last_updated }}</p>
                
                <h3>Quality Scores</h3>
                <div class="quality-scores">
                    <div class="score">
                        <div class="score-value">{{ "%.1f"|format(source.quality_score.completeness) }}%</div>
                        <div>Completeness</div>
                    </div>
                    <div class="score">
                        <div class="score-value">{{ "%.1f"|format(source.quality_score.validity) }}%</div>
                        <div>Validity</div>
                    </div>
                    <div class="score">
                        <div class="score-value">{{ "%.1f"|format(source.quality_score.uniqueness) }}%</div>
                        <div>Uniqueness</div>
                    </div>
                    <div class="score">
                        <div class="score-value">{{ "%.1f"|format(source.quality_score.overall_score) }}%</div>
                        <div>Overall</div>
                    </div>
                </div>
                
                {% if source.issues_found %}
                <div class="issues-list">
                    <h4>Issues Found ({{ source.issues_found|length }})</h4>
                    <ul>
                        {% for issue in source.issues_found %}
                        <li><strong>{{ issue.type }}:</strong> {{ issue.description }} ({{ issue.severity }})</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </body>
        </html>
        '''
        
        # Save templates
        with open(self.template_dir / 'executive_summary.html', 'w') as f:
            f.write(executive_template)
        
        with open(self.template_dir / 'technical_report.html', 'w') as f:
            f.write(technical_template)

    def calculate_quality_score(self, df: pd.DataFrame, 
                               schema_rules: Dict = None) -> DataQualityScore:
        """
        Calculate comprehensive data quality score
        Comprehensive data quality score calculate करना
        """
        
        if df.empty:
            return DataQualityScore(0, 0, 0, 0, 0, 0, 0)
        
        total_cells = df.size
        total_rows = len(df)
        
        # 1. Completeness - % of non-null values
        non_null_cells = df.count().sum()
        completeness = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
        
        # 2. Uniqueness - for columns that should be unique
        unique_columns = schema_rules.get('unique_columns', []) if schema_rules else []
        uniqueness_scores = []
        
        for col in unique_columns:
            if col in df.columns:
                unique_ratio = len(df[col].dropna().unique()) / len(df[col].dropna())
                uniqueness_scores.append(unique_ratio * 100)
        
        uniqueness = np.mean(uniqueness_scores) if uniqueness_scores else 100
        
        # 3. Validity - format compliance
        validity_scores = []
        format_rules = schema_rules.get('format_rules', {}) if schema_rules else {}
        
        for col, pattern in format_rules.items():
            if col in df.columns:
                valid_count = df[col].astype(str).str.match(pattern).sum()
                total_non_null = df[col].notna().sum()
                if total_non_null > 0:
                    validity_scores.append((valid_count / total_non_null) * 100)
        
        validity = np.mean(validity_scores) if validity_scores else 100
        
        # 4. Consistency - cross-column consistency
        consistency = 100  # Simplified for demo
        
        # 5. Timeliness - freshness of data
        timestamp_cols = schema_rules.get('timestamp_columns', []) if schema_rules else []
        timeliness_scores = []
        
        for col in timestamp_cols:
            if col in df.columns:
                try:
                    timestamps = pd.to_datetime(df[col])
                    now = datetime.now()
                    hours_old = (now - timestamps.max()).total_seconds() / 3600
                    
                    # Score based on how fresh the data is
                    if hours_old <= 1:
                        timeliness_scores.append(100)
                    elif hours_old <= 24:
                        timeliness_scores.append(90)
                    elif hours_old <= 168:  # 1 week
                        timeliness_scores.append(70)
                    else:
                        timeliness_scores.append(50)
                except:
                    timeliness_scores.append(50)
        
        timeliness = np.mean(timeliness_scores) if timeliness_scores else 100
        
        # 6. Accuracy - simplified for demo
        accuracy = 90  # Would be calculated against ground truth
        
        # Overall score - weighted average
        weights = {
            'completeness': 0.25,
            'validity': 0.25,
            'uniqueness': 0.15,
            'consistency': 0.15,
            'timeliness': 0.15,
            'accuracy': 0.05
        }
        
        overall_score = (
            completeness * weights['completeness'] +
            validity * weights['validity'] +
            uniqueness * weights['uniqueness'] +
            consistency * weights['consistency'] +
            timeliness * weights['timeliness'] +
            accuracy * weights['accuracy']
        )
        
        return DataQualityScore(
            completeness=completeness,
            uniqueness=uniqueness,
            validity=validity,
            consistency=consistency,
            timeliness=timeliness,
            accuracy=accuracy,
            overall_score=overall_score
        )

    def detect_quality_issues(self, df: pd.DataFrame, 
                            quality_score: DataQualityScore) -> List[Dict[str, Any]]:
        """
        Detect and categorize data quality issues
        Data quality issues detect और categorize करना
        """
        
        issues = []
        
        # Missing data issues
        null_percentages = (df.isnull().sum() / len(df)) * 100
        for col, null_pct in null_percentages.items():
            if null_pct > 20:
                issues.append({
                    'type': 'High Missing Data',
                    'column': col,
                    'description': f'{col} has {null_pct:.1f}% missing values',
                    'severity': 'high' if null_pct > 50 else 'medium',
                    'affected_records': int((null_pct / 100) * len(df)),
                    'recommendation': f'Investigate source of missing {col} data'
                })
        
        # Duplicate detection
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(df)) * 100
            issues.append({
                'type': 'Duplicate Records',
                'column': 'all',
                'description': f'{duplicate_count} duplicate records found ({duplicate_pct:.1f}%)',
                'severity': 'high' if duplicate_pct > 5 else 'medium',
                'affected_records': duplicate_count,
                'recommendation': 'Implement deduplication logic in data pipeline'
            })
        
        # Outlier detection for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if len(df[col].dropna()) > 10:  # Need enough data for outlier detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
                
                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(df)) * 100
                    if outlier_pct > 5:
                        issues.append({
                            'type': 'Statistical Outliers',
                            'column': col,
                            'description': f'{len(outliers)} outliers in {col} ({outlier_pct:.1f}%)',
                            'severity': 'medium',
                            'affected_records': len(outliers),
                            'recommendation': f'Review outlier values in {col} for data entry errors'
                        })
        
        # Low quality score issues
        if quality_score.overall_score < self.quality_thresholds['acceptable']:
            issues.append({
                'type': 'Low Quality Score',
                'column': 'overall',
                'description': f'Overall quality score {quality_score.overall_score:.1f}% below acceptable threshold',
                'severity': 'critical' if quality_score.overall_score < self.quality_thresholds['poor'] else 'high',
                'affected_records': len(df),
                'recommendation': 'Immediate data quality improvement required'
            })
        
        return issues

    def generate_source_report(self, source_id: str, source_name: str, 
                             source_type: str, df: pd.DataFrame,
                             schema_rules: Dict = None) -> DataSourceReport:
        """
        Generate quality report for a single data source
        Single data source के लिए quality report generate करना
        """
        
        # Calculate quality scores
        quality_score = self.calculate_quality_score(df, schema_rules)
        
        # Detect issues
        issues = self.detect_quality_issues(df, quality_score)
        
        # Determine SLA status
        sla_priority = schema_rules.get('sla_priority', 'medium') if schema_rules else 'medium'
        sla_requirements = self.sla_definitions.get(sla_priority, self.sla_definitions['medium'])
        
        if quality_score.overall_score >= sla_requirements['min_score']:
            sla_status = 'met'
        elif quality_score.overall_score >= sla_requirements['min_score'] - 10:
            sla_status = 'warning'
        else:
            sla_status = 'breached'
        
        # Determine trend (simplified - would compare with historical data)
        trending = 'stable'  # Would calculate from historical scores
        
        report = DataSourceReport(
            source_id=source_id,
            source_name=source_name,
            source_type=source_type,
            total_records=len(df),
            quality_score=quality_score,
            issues_found=issues,
            trending=trending,
            last_updated=datetime.now(),
            sla_status=sla_status
        )
        
        # Store metrics in database
        self._store_quality_metrics(report)
        
        return report

    def _store_quality_metrics(self, report: DataSourceReport):
        """Store quality metrics in database"""
        try:
            if not self.db_connection:
                return
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO quality_metrics
                (source_id, source_name, timestamp, completeness, uniqueness, 
                 validity, consistency, timeliness, accuracy, overall_score,
                 total_records, issues_json, sla_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.source_id,
                report.source_name,
                report.last_updated.isoformat(),
                report.quality_score.completeness,
                report.quality_score.uniqueness,
                report.quality_score.validity,
                report.quality_score.consistency,
                report.quality_score.timeliness,
                report.quality_score.accuracy,
                report.quality_score.overall_score,
                report.total_records,
                json.dumps(report.issues_found),
                report.sla_status
            ))
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Failed to store quality metrics: {e}")

    def generate_executive_summary(self, source_reports: List[DataSourceReport],
                                 report_period: str) -> ExecutiveSummary:
        """
        Generate executive summary from source reports
        Source reports से executive summary generate करना
        """
        
        total_sources = len(source_reports)
        sources_meeting_sla = len([r for r in source_reports if r.sla_status == 'met'])
        
        # Count critical issues
        critical_issues = 0
        for report in source_reports:
            critical_issues += len([i for i in report.issues_found if i['severity'] == 'critical'])
        
        # Estimate cost impact
        cost_impact = 0
        for report in source_reports:
            for issue in report.issues_found:
                if issue['severity'] == 'critical':
                    cost_impact += self.cost_models['incorrect_decisions']
                elif issue['severity'] == 'high':
                    cost_impact += self.cost_models['customer_impact']
        
        # Generate recommendations
        recommendations = []
        
        if sources_meeting_sla / total_sources < 0.8:
            recommendations.append("70%+ sources below SLA - immediate attention required")
        
        if critical_issues > 0:
            recommendations.append(f"{critical_issues} critical issues need immediate resolution")
        
        recommendations.append("Implement automated data quality monitoring")
        recommendations.append("Establish data steward roles for each source")
        
        # Count improvement opportunities
        improvement_opportunities = len([r for r in source_reports 
                                       if r.quality_score.overall_score < self.quality_thresholds['excellent']])
        
        return ExecutiveSummary(
            report_period=report_period,
            total_sources_monitored=total_sources,
            sources_meeting_sla=sources_meeting_sla,
            critical_issues=critical_issues,
            improvement_opportunities=improvement_opportunities,
            cost_impact_estimate=cost_impact,
            key_recommendations=recommendations
        )

    def create_dashboard_visualizations(self, source_reports: List[DataSourceReport]) -> str:
        """
        Create interactive dashboard visualizations
        Interactive dashboard visualizations बनाना
        """
        
        # Prepare data for visualization
        sources_data = []
        for report in source_reports:
            sources_data.append({
                'source_name': report.source_name,
                'overall_score': report.quality_score.overall_score,
                'completeness': report.quality_score.completeness,
                'validity': report.quality_score.validity,
                'uniqueness': report.quality_score.uniqueness,
                'total_records': report.total_records,
                'sla_status': report.sla_status,
                'issues_count': len(report.issues_found)
            })
        
        df_viz = pd.DataFrame(sources_data)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Overall Quality Scores',
                'SLA Status Distribution', 
                'Quality Dimensions Comparison',
                'Issues by Source',
                'Records vs Quality Score',
                'Quality Score Distribution'
            ],
            specs=[[{"secondary_y": False}, {"type": "pie"}],
                   [{"colspan": 2}, None],
                   [{"secondary_y": False}, {"type": "histogram"}]]
        )
        
        # 1. Overall quality scores bar chart
        fig.add_trace(
            go.Bar(
                x=df_viz['source_name'],
                y=df_viz['overall_score'],
                marker_color=df_viz['overall_score'],
                colorscale='RdYlGn',
                name='Quality Score'
            ),
            row=1, col=1
        )
        
        # 2. SLA status pie chart
        sla_counts = df_viz['sla_status'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=sla_counts.index,
                values=sla_counts.values,
                marker_colors=['green', 'orange', 'red']
            ),
            row=1, col=2
        )
        
        # 3. Quality dimensions comparison
        dimensions = ['completeness', 'validity', 'uniqueness']
        for dim in dimensions:
            fig.add_trace(
                go.Scatter(
                    x=df_viz['source_name'],
                    y=df_viz[dim],
                    mode='lines+markers',
                    name=dim.capitalize()
                ),
                row=2, col=1
            )
        
        # 4. Issues by source
        fig.add_trace(
            go.Bar(
                x=df_viz['source_name'],
                y=df_viz['issues_count'],
                marker_color='red',
                name='Issues Count'
            ),
            row=3, col=1
        )
        
        # 5. Quality score distribution
        fig.add_trace(
            go.Histogram(
                x=df_viz['overall_score'],
                nbinsx=10,
                marker_color='lightblue',
                name='Score Distribution'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Data Quality Dashboard",
            showlegend=True
        )
        
        # Add threshold lines
        fig.add_hline(y=self.quality_thresholds['good'], line_dash="dash", 
                     line_color="green", row=1, col=1)
        fig.add_hline(y=self.quality_thresholds['acceptable'], line_dash="dash", 
                     line_color="orange", row=1, col=1)
        
        return fig.to_html(include_plotlyjs='cdn')

    def generate_html_report(self, source_reports: List[DataSourceReport],
                           executive_summary: ExecutiveSummary,
                           report_type: str = 'executive') -> str:
        """
        Generate HTML report using templates
        Templates का use करके HTML report generate करना
        """
        
        try:
            if report_type == 'executive':
                template = self.template_env.get_template('executive_summary.html')
                
                # Get top sources by quality score
                top_sources = sorted(source_reports, 
                                   key=lambda x: x.quality_score.overall_score, 
                                   reverse=True)[:10]
                
                html_content = template.render(
                    summary=executive_summary,
                    top_sources=top_sources,
                    generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            elif report_type == 'technical':
                template = self.template_env.get_template('technical_report.html')
                
                html_content = template.render(
                    sources=source_reports,
                    report_period=executive_summary.report_period,
                    generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            else:
                return "<html><body><h1>Unknown report type</h1></body></html>"
            
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"

    def send_email_report(self, html_content: str, recipients: List[str],
                         subject: str, attachments: List[str] = None):
        """
        Send email report to recipients
        Recipients को email report भेजना
        """
        
        if not self.email_config:
            logger.warning("Email configuration not provided")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(file_path).name}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email report sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False

    def schedule_automated_reports(self):
        """
        Schedule automated report generation
        Automated report generation schedule करना
        """
        
        # Daily technical reports
        schedule.every().day.at("09:00").do(self._generate_daily_technical_report)
        
        # Weekly executive reports
        schedule.every().monday.at("08:00").do(self._generate_weekly_executive_report)
        
        # Monthly comprehensive reports
        schedule.every().month.do(self._generate_monthly_comprehensive_report)
        
        logger.info("Automated report scheduling configured")
        
        # Run scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def _generate_daily_technical_report(self):
        """Generate daily technical report"""
        logger.info("Generating daily technical report...")
        # Implementation would go here
        
    def _generate_weekly_executive_report(self):
        """Generate weekly executive report"""
        logger.info("Generating weekly executive report...")
        # Implementation would go here
        
    def _generate_monthly_comprehensive_report(self):
        """Generate monthly comprehensive report"""
        logger.info("Generating monthly comprehensive report...")
        # Implementation would go here

def create_sample_data_sources() -> List[Tuple[str, str, str, pd.DataFrame, Dict]]:
    """Create sample data sources for Indian e-commerce scenario"""
    
    # Generate sample datasets
    np.random.seed(42)
    
    # Orders dataset
    orders_data = {
        'order_id': [f'ORD-{i:08d}' for i in range(1, 10001)],
        'customer_id': [f'CUST-{np.random.randint(1, 5000):06d}' for _ in range(10000)],
        'customer_email': [f'customer{i}@example.com' if np.random.random() > 0.1 else None 
                          for i in range(10000)],  # 10% missing emails
        'order_amount': np.random.lognormal(mean=6, sigma=1, size=10000),
        'order_date': pd.date_range('2024-01-01', '2024-12-31', periods=10000),
        'payment_method': np.random.choice(['UPI', 'Card', 'COD', 'Net Banking'], 10000),
        'delivery_pincode': [f'{np.random.randint(100000, 999999):06d}' 
                           if np.random.random() > 0.05 else None for _ in range(10000)]
    }
    orders_df = pd.DataFrame(orders_data)
    
    # Add some duplicates
    orders_df = pd.concat([orders_df, orders_df.sample(500)], ignore_index=True)
    
    orders_schema = {
        'unique_columns': ['order_id'],
        'format_rules': {
            'customer_email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'delivery_pincode': r'^\d{6}$'
        },
        'timestamp_columns': ['order_date'],
        'sla_priority': 'critical'
    }
    
    # Products dataset
    products_data = {
        'product_id': [f'PROD-{i:06d}' for i in range(1, 5001)],
        'product_name': [f'Product {i}' for i in range(1, 5001)],
        'category': np.random.choice(['Electronics', 'Fashion', 'Home', 'Books'], 5000),
        'price': np.random.uniform(100, 50000, 5000),
        'stock_quantity': np.random.randint(0, 1000, 5000),
        'last_updated': pd.date_range('2024-12-01', '2024-12-31', periods=5000)
    }
    products_df = pd.DataFrame(products_data)
    
    products_schema = {
        'unique_columns': ['product_id'],
        'timestamp_columns': ['last_updated'],
        'sla_priority': 'high'
    }
    
    # Customers dataset with quality issues
    customers_data = {
        'customer_id': [f'CUST-{i:06d}' for i in range(1, 3001)],
        'customer_name': [f'Customer {i}' if np.random.random() > 0.15 else None 
                         for i in range(3000)],  # 15% missing names
        'phone': [f'+91{np.random.randint(6000000000, 9999999999)}' 
                 if np.random.random() > 0.08 else None for _ in range(3000)],
        'city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'], 3000),
        'registration_date': pd.date_range('2020-01-01', '2024-12-31', periods=3000)
    }
    customers_df = pd.DataFrame(customers_data)
    
    customers_schema = {
        'unique_columns': ['customer_id'],
        'format_rules': {
            'phone': r'^\+91[6-9]\d{9}$'
        },
        'timestamp_columns': ['registration_date'],
        'sla_priority': 'medium'
    }
    
    return [
        ('orders', 'E-commerce Orders', 'database', orders_df, orders_schema),
        ('products', 'Product Catalog', 'database', products_df, products_schema),
        ('customers', 'Customer Database', 'database', customers_df, customers_schema)
    ]

def main():
    """Main execution function - demo of automated reporting system"""
    
    print("📊 Automated Data Quality Reporting System Demo")
    print("स्वचालित डेटा गुणवत्ता रिपोर्टिंग प्रणाली का प्रदर्शन\n")
    
    # Initialize reporter
    config = {
        'db_path': 'demo_dq_reports.db',
        'template_dir': './report_templates',
        'email': {
            'sender': 'data-quality@company.com',
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'username': 'dq_reports',
            'password': 'password'
        }
    }
    
    reporter = AutomatedDataQualityReporter(config)
    
    # Test 1: Generate source reports
    print("Test 1: Generating Data Source Quality Reports")
    print("=" * 45)
    
    sample_sources = create_sample_data_sources()
    source_reports = []
    
    for source_id, source_name, source_type, df, schema in sample_sources:
        print(f"Analyzing {source_name}...")
        report = reporter.generate_source_report(
            source_id, source_name, source_type, df, schema
        )
        source_reports.append(report)
        
        print(f"  Quality Score: {report.quality_score.overall_score:.1f}%")
        print(f"  SLA Status: {report.sla_status}")
        print(f"  Issues Found: {len(report.issues_found)}")
    
    # Test 2: Generate executive summary
    print("\nTest 2: Executive Summary Generation")
    print("=" * 35)
    
    executive_summary = reporter.generate_executive_summary(
        source_reports, "December 2024"
    )
    
    print(f"""
    Executive Summary:
    ==================
    Total Sources Monitored: {executive_summary.total_sources_monitored}
    Sources Meeting SLA: {executive_summary.sources_meeting_sla}
    Critical Issues: {executive_summary.critical_issues}
    Improvement Opportunities: {executive_summary.improvement_opportunities}
    Estimated Cost Impact: ₹{executive_summary.cost_impact_estimate:,.2f}
    
    Key Recommendations:
    {chr(10).join(['- ' + rec for rec in executive_summary.key_recommendations])}
    """)
    
    # Test 3: Generate HTML reports
    print("\nTest 3: HTML Report Generation")
    print("=" * 30)
    
    # Executive report
    executive_html = reporter.generate_html_report(
        source_reports, executive_summary, 'executive'
    )
    
    with open('executive_summary_report.html', 'w', encoding='utf-8') as f:
        f.write(executive_html)
    
    print("Executive summary report saved as 'executive_summary_report.html'")
    
    # Technical report
    technical_html = reporter.generate_html_report(
        source_reports, executive_summary, 'technical'
    )
    
    with open('technical_data_quality_report.html', 'w', encoding='utf-8') as f:
        f.write(technical_html)
    
    print("Technical report saved as 'technical_data_quality_report.html'")
    
    # Test 4: Dashboard visualization
    print("\nTest 4: Dashboard Visualization")
    print("=" * 30)
    
    dashboard_html = reporter.create_dashboard_visualizations(source_reports)
    
    with open('data_quality_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("Interactive dashboard saved as 'data_quality_dashboard.html'")
    
    # Test 5: Quality metrics analysis
    print("\nTest 5: Detailed Quality Analysis")
    print("=" * 35)
    
    for report in source_reports:
        print(f"\n{report.source_name} Quality Breakdown:")
        print(f"  Completeness: {report.quality_score.completeness:.1f}%")
        print(f"  Validity: {report.quality_score.validity:.1f}%")
        print(f"  Uniqueness: {report.quality_score.uniqueness:.1f}%")
        print(f"  Timeliness: {report.quality_score.timeliness:.1f}%")
        print(f"  Overall Score: {report.quality_score.overall_score:.1f}%")
        
        if report.issues_found:
            print(f"  Critical Issues:")
            for issue in report.issues_found:
                if issue['severity'] == 'critical':
                    print(f"    - {issue['description']}")
    
    # Test 6: Simulate scheduled reporting
    print("\nTest 6: Automated Scheduling Setup")
    print("=" * 35)
    
    print("Setting up automated report scheduling...")
    reporter.schedule_automated_reports()
    print("Scheduled reports configured:")
    print("  - Daily technical reports at 09:00")
    print("  - Weekly executive reports on Mondays at 08:00")
    print("  - Monthly comprehensive reports")
    
    print("\n✅ Automated Data Quality Reporting System Demo Complete!")
    print("Production reporting system ready - उत्पादन रिपोर्टिंग सिस्टम तैयार!")
    
    return {
        'source_reports': source_reports,
        'executive_summary': executive_summary,
        'total_issues': sum(len(r.issues_found) for r in source_reports)
    }

if __name__ == "__main__":
    results = main()