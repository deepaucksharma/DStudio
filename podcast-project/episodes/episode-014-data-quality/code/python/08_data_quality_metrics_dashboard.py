#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 8
Data Quality Metrics Dashboard with Indian KPIs

Real-time dashboard system for monitoring data quality metrics
Indian business context में data quality को monitor करने का dashboard

Author: DStudio Team
Context: Real-time quality monitoring for Indian enterprises like banks/fintech
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import threading
import time
import random

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - डैशबोर्ड - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QualityMetric:
    """Data quality metric structure"""
    name: str
    current_value: float
    target_value: float
    unit: str
    status: str  # 'GOOD', 'WARNING', 'CRITICAL'
    trend: str   # 'UP', 'DOWN', 'STABLE'
    description: str

class IndianDataQualityDashboard:
    """
    Comprehensive data quality dashboard for Indian business context
    Indian enterprises के लिए complete quality monitoring dashboard
    
    Features:
    1. Real-time quality metrics
    2. Indian business KPIs
    3. Compliance monitoring
    4. Trend analysis
    5. Alert management
    6. Performance tracking
    7. Custom metric definitions
    8. Multi-dataset monitoring
    """
    
    def __init__(self):
        """Initialize dashboard system"""
        
        # Indian business quality benchmarks
        self.quality_benchmarks = {
            'banking': {
                'completeness': 99.5,
                'accuracy': 99.9,
                'consistency': 99.0,
                'timeliness': 95.0,
                'validity': 98.0,
                'uniqueness': 99.8
            },
            'ecommerce': {
                'completeness': 95.0,
                'accuracy': 97.0,
                'consistency': 90.0,
                'timeliness': 85.0,
                'validity': 95.0,
                'uniqueness': 98.0
            },
            'telecom': {
                'completeness': 98.0,
                'accuracy': 96.0,
                'consistency': 92.0,
                'timeliness': 90.0,
                'validity': 97.0,
                'uniqueness': 99.0
            }
        }
        
        # Indian compliance metrics
        self.compliance_metrics = {
            'kyc_completeness': {'target': 100.0, 'threshold': 95.0},
            'aadhaar_validation_rate': {'target': 99.0, 'threshold': 95.0},
            'pan_validation_rate': {'target': 98.0, 'threshold': 90.0},
            'gstin_validation_rate': {'target': 97.0, 'threshold': 90.0},
            'mobile_validation_rate': {'target': 95.0, 'threshold': 85.0},
            'email_validation_rate': {'target': 90.0, 'threshold': 80.0}
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'critical': 0.85,  # Below 85% is critical
            'warning': 0.90,   # Below 90% is warning
            'good': 0.95       # Above 95% is good
        }
        
        # Initialize database for metrics storage
        self.init_database()
        
        # Start background metric collection
        self.start_metric_collection()
        
        logger.info("Indian Data Quality Dashboard initialized - डैशबोर्ड तैयार!")

    def init_database(self):
        """Initialize SQLite database for storing metrics"""
        
        self.db_path = 'data_quality_metrics.db'
        conn = sqlite3.connect(self.db_path)
        
        # Create metrics table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            dataset_name TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_target REAL,
            metric_status TEXT,
            business_domain TEXT,
            record_count INTEGER,
            metadata TEXT
        )
        ''')
        
        # Create alerts table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS quality_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            dataset_name TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            alert_level TEXT NOT NULL,
            current_value REAL NOT NULL,
            threshold_value REAL NOT NULL,
            message TEXT,
            is_resolved BOOLEAN DEFAULT FALSE,
            resolved_at DATETIME
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized for metrics storage")

    def calculate_quality_metrics(self, df: pd.DataFrame, 
                                dataset_name: str = "Dataset",
                                business_domain: str = "general") -> Dict[str, QualityMetric]:
        """
        Calculate comprehensive data quality metrics
        Complete quality metrics calculate करना
        """
        
        if df.empty:
            return {}
        
        metrics = {}
        record_count = len(df)
        
        # Get domain benchmarks
        benchmarks = self.quality_benchmarks.get(business_domain, self.quality_benchmarks['ecommerce'])
        
        # 1. Completeness
        total_cells = record_count * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        metrics['completeness'] = QualityMetric(
            name='Completeness',
            current_value=completeness,
            target_value=benchmarks['completeness'],
            unit='%',
            status=self._determine_status(completeness, benchmarks['completeness']),
            trend='STABLE',
            description='Percentage of non-null values across all fields'
        )
        
        # 2. Uniqueness (for ID columns)
        id_columns = [col for col in df.columns if 'id' in col.lower()]
        if id_columns:
            id_col = id_columns[0]  # Take first ID column
            unique_count = df[id_col].nunique()
            total_count = df[id_col].count()
            uniqueness = (unique_count / total_count) * 100 if total_count > 0 else 0
            
            metrics['uniqueness'] = QualityMetric(
                name='Uniqueness',
                current_value=uniqueness,
                target_value=benchmarks['uniqueness'],
                unit='%',
                status=self._determine_status(uniqueness, benchmarks['uniqueness']),
                trend='STABLE',
                description=f'Uniqueness of {id_col} values'
            )
        
        # 3. Validity (format validation)
        validity_scores = []
        
        # Email validity
        email_cols = [col for col in df.columns if 'email' in col.lower()]
        if email_cols:
            email_col = email_cols[0]
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            valid_emails = df[email_col].astype(str).str.match(email_pattern).sum()
            total_emails = df[email_col].count()
            email_validity = (valid_emails / total_emails) * 100 if total_emails > 0 else 100
            validity_scores.append(email_validity)
        
        # Mobile validity
        mobile_cols = [col for col in df.columns if 'mobile' in col.lower() or 'phone' in col.lower()]
        if mobile_cols:
            mobile_col = mobile_cols[0]
            mobile_pattern = r'^[6-9]\d{9}$'
            valid_mobiles = df[mobile_col].astype(str).str.match(mobile_pattern).sum()
            total_mobiles = df[mobile_col].count()
            mobile_validity = (valid_mobiles / total_mobiles) * 100 if total_mobiles > 0 else 100
            validity_scores.append(mobile_validity)
        
        # PAN validity
        pan_cols = [col for col in df.columns if 'pan' in col.lower()]
        if pan_cols:
            pan_col = pan_cols[0]
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            valid_pans = df[pan_col].astype(str).str.match(pan_pattern).sum()
            total_pans = df[pan_col].count()
            pan_validity = (valid_pans / total_pans) * 100 if total_pans > 0 else 100
            validity_scores.append(pan_validity)
        
        overall_validity = np.mean(validity_scores) if validity_scores else 100
        
        metrics['validity'] = QualityMetric(
            name='Validity',
            current_value=overall_validity,
            target_value=benchmarks['validity'],
            unit='%',
            status=self._determine_status(overall_validity, benchmarks['validity']),
            trend='STABLE',
            description='Percentage of values matching expected formats'
        )
        
        # 4. Consistency (data type consistency)
        consistency_scores = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check string length consistency
                lengths = df[col].astype(str).str.len()
                if len(lengths) > 1:
                    cv = lengths.std() / lengths.mean() if lengths.mean() > 0 else 0
                    consistency_score = max(0, 100 - (cv * 100))
                    consistency_scores.append(consistency_score)
        
        overall_consistency = np.mean(consistency_scores) if consistency_scores else 100
        
        metrics['consistency'] = QualityMetric(
            name='Consistency',
            current_value=overall_consistency,
            target_value=benchmarks['consistency'],
            unit='%',
            status=self._determine_status(overall_consistency, benchmarks['consistency']),
            trend='STABLE',
            description='Consistency of data formats and patterns'
        )
        
        # 5. Timeliness (for timestamp columns)
        timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        if timestamp_cols:
            timestamp_col = timestamp_cols[0]
            try:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col])
                now = datetime.now()
                recent_data = df[df[timestamp_col] > now - timedelta(days=1)]
                timeliness = (len(recent_data) / len(df)) * 100
                
                metrics['timeliness'] = QualityMetric(
                    name='Timeliness',
                    current_value=timeliness,
                    target_value=benchmarks['timeliness'],
                    unit='%',
                    status=self._determine_status(timeliness, benchmarks['timeliness']),
                    trend='STABLE',
                    description='Percentage of recent data (within 24 hours)'
                )
            except:
                pass
        
        # 6. Accuracy (business rule compliance)
        accuracy_scores = []
        
        # Amount field accuracy
        amount_cols = [col for col in df.columns if 'amount' in col.lower()]
        if amount_cols:
            amount_col = amount_cols[0]
            positive_amounts = (df[amount_col] > 0).sum()
            total_amounts = df[amount_col].count()
            amount_accuracy = (positive_amounts / total_amounts) * 100 if total_amounts > 0 else 100
            accuracy_scores.append(amount_accuracy)
        
        overall_accuracy = np.mean(accuracy_scores) if accuracy_scores else 100
        
        metrics['accuracy'] = QualityMetric(
            name='Accuracy',
            current_value=overall_accuracy,
            target_value=benchmarks['accuracy'],
            unit='%',
            status=self._determine_status(overall_accuracy, benchmarks['accuracy']),
            trend='STABLE',
            description='Compliance with business rules and constraints'
        )
        
        # Store metrics in database
        self._store_metrics_to_db(dataset_name, business_domain, metrics, record_count)
        
        return metrics

    def calculate_indian_compliance_metrics(self, df: pd.DataFrame, 
                                          dataset_name: str = "Dataset") -> Dict[str, QualityMetric]:
        """
        Calculate Indian compliance-specific metrics
        Indian compliance के specific metrics calculate करना
        """
        
        compliance_metrics = {}
        
        # KYC Completeness
        kyc_fields = ['name', 'mobile', 'email', 'address']
        available_kyc_fields = [field for field in kyc_fields if field in df.columns]
        
        if available_kyc_fields:
            kyc_complete_records = df[available_kyc_fields].notna().all(axis=1).sum()
            kyc_completeness = (kyc_complete_records / len(df)) * 100
            
            compliance_metrics['kyc_completeness'] = QualityMetric(
                name='KYC Completeness',
                current_value=kyc_completeness,
                target_value=self.compliance_metrics['kyc_completeness']['target'],
                unit='%',
                status=self._determine_compliance_status(
                    kyc_completeness, 
                    self.compliance_metrics['kyc_completeness']['threshold']
                ),
                trend='STABLE',
                description='Percentage of records with complete KYC information'
            )
        
        # Aadhaar Validation Rate
        aadhaar_cols = [col for col in df.columns if 'aadhaar' in col.lower()]
        if aadhaar_cols:
            aadhaar_col = aadhaar_cols[0]
            aadhaar_pattern = r'^\d{12}$'
            valid_aadhaars = df[aadhaar_col].astype(str).str.match(aadhaar_pattern).sum()
            total_aadhaars = df[aadhaar_col].count()
            aadhaar_validation_rate = (valid_aadhaars / total_aadhaars) * 100 if total_aadhaars > 0 else 0
            
            compliance_metrics['aadhaar_validation'] = QualityMetric(
                name='Aadhaar Validation Rate',
                current_value=aadhaar_validation_rate,
                target_value=self.compliance_metrics['aadhaar_validation_rate']['target'],
                unit='%',
                status=self._determine_compliance_status(
                    aadhaar_validation_rate,
                    self.compliance_metrics['aadhaar_validation_rate']['threshold']
                ),
                trend='STABLE',
                description='Percentage of valid Aadhaar number formats'
            )
        
        # PAN Validation Rate
        pan_cols = [col for col in df.columns if 'pan' in col.lower()]
        if pan_cols:
            pan_col = pan_cols[0]
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            valid_pans = df[pan_col].astype(str).str.match(pan_pattern).sum()
            total_pans = df[pan_col].count()
            pan_validation_rate = (valid_pans / total_pans) * 100 if total_pans > 0 else 0
            
            compliance_metrics['pan_validation'] = QualityMetric(
                name='PAN Validation Rate',
                current_value=pan_validation_rate,
                target_value=self.compliance_metrics['pan_validation_rate']['target'],
                unit='%',
                status=self._determine_compliance_status(
                    pan_validation_rate,
                    self.compliance_metrics['pan_validation_rate']['threshold']
                ),
                trend='STABLE',
                description='Percentage of valid PAN number formats'
            )
        
        # GSTIN Validation Rate
        gstin_cols = [col for col in df.columns if 'gstin' in col.lower() or 'gst' in col.lower()]
        if gstin_cols:
            gstin_col = gstin_cols[0]
            gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z][Z0-9A-Z]$'
            valid_gstins = df[gstin_col].astype(str).str.match(gstin_pattern).sum()
            total_gstins = df[gstin_col].count()
            gstin_validation_rate = (valid_gstins / total_gstins) * 100 if total_gstins > 0 else 0
            
            compliance_metrics['gstin_validation'] = QualityMetric(
                name='GSTIN Validation Rate',
                current_value=gstin_validation_rate,
                target_value=self.compliance_metrics['gstin_validation_rate']['target'],
                unit='%',
                status=self._determine_compliance_status(
                    gstin_validation_rate,
                    self.compliance_metrics['gstin_validation_rate']['threshold']
                ),
                trend='STABLE',
                description='Percentage of valid GSTIN formats'
            )
        
        return compliance_metrics

    def create_dashboard_app(self) -> dash.Dash:
        """
        Create comprehensive Dash application for quality dashboard
        Complete dashboard app बनाना
        """
        
        # Initialize Dash app with Bootstrap theme
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Dashboard layout
        app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Indian Data Quality Dashboard", className="text-center mb-4"),
                    html.H4("डेटा गुणवत्ता निगरानी डैशबोर्ड", className="text-center text-muted mb-4")
                ])
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Control Panel"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Dataset:"),
                                    dcc.Dropdown(
                                        id='dataset-dropdown',
                                        options=[
                                            {'label': 'Banking Transactions', 'value': 'banking'},
                                            {'label': 'E-commerce Orders', 'value': 'ecommerce'},
                                            {'label': 'Telecom Subscribers', 'value': 'telecom'},
                                            {'label': 'Customer KYC', 'value': 'kyc'}
                                        ],
                                        value='banking'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Time Range:"),
                                    dcc.Dropdown(
                                        id='time-range-dropdown',
                                        options=[
                                            {'label': 'Last Hour', 'value': '1h'},
                                            {'label': 'Last 24 Hours', 'value': '24h'},
                                            {'label': 'Last Week', 'value': '7d'},
                                            {'label': 'Last Month', 'value': '30d'}
                                        ],
                                        value='24h'
                                    )
                                ], width=6)
                            ]),
                            html.Div([
                                dbc.Button("Refresh Data", id="refresh-btn", color="primary", className="me-2"),
                                dbc.Button("Generate Report", id="report-btn", color="success")
                            ], className="mt-3")
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Key Metrics Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="completeness-value", className="text-primary"),
                            html.P("Completeness", className="card-text"),
                            html.Small(id="completeness-status", className="text-muted")
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="accuracy-value", className="text-success"),
                            html.P("Accuracy", className="card-text"),
                            html.Small(id="accuracy-status", className="text-muted")
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="validity-value", className="text-warning"),
                            html.P("Validity", className="card-text"),
                            html.Small(id="validity-status", className="text-muted")
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="consistency-value", className="text-info"),
                            html.P("Consistency", className="card-text"),
                            html.Small(id="consistency-status", className="text-muted")
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="timeliness-value", className="text-secondary"),
                            html.P("Timeliness", className="card-text"),
                            html.Small(id="timeliness-status", className="text-muted")
                        ])
                    ])
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="uniqueness-value", className="text-dark"),
                            html.P("Uniqueness", className="card-text"),
                            html.Small(id="uniqueness-status", className="text-muted")
                        ])
                    ])
                ], width=2)
            ], className="mb-4"),
            
            # Charts Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Quality Trends"),
                        dbc.CardBody([
                            dcc.Graph(id="quality-trends-chart")
                        ])
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Quality Distribution"),
                        dbc.CardBody([
                            dcc.Graph(id="quality-distribution-chart")
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Indian Compliance Metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Indian Compliance Metrics"),
                        dbc.CardBody([
                            dcc.Graph(id="compliance-metrics-chart")
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Alerts Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Active Alerts"),
                        dbc.CardBody([
                            html.Div(id="alerts-container")
                        ])
                    ])
                ])
            ]),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # 30 seconds
                n_intervals=0
            )
            
        ], fluid=True)
        
        # Callbacks
        self._setup_callbacks(app)
        
        return app

    def _setup_callbacks(self, app: dash.Dash):
        """Setup dashboard callbacks"""
        
        @app.callback(
            [Output('completeness-value', 'children'),
             Output('completeness-status', 'children'),
             Output('accuracy-value', 'children'),
             Output('accuracy-status', 'children'),
             Output('validity-value', 'children'),
             Output('validity-status', 'children'),
             Output('consistency-value', 'children'),
             Output('consistency-status', 'children'),
             Output('timeliness-value', 'children'),
             Output('timeliness-status', 'children'),
             Output('uniqueness-value', 'children'),
             Output('uniqueness-status', 'children'),
             Output('quality-trends-chart', 'figure'),
             Output('quality-distribution-chart', 'figure'),
             Output('compliance-metrics-chart', 'figure'),
             Output('alerts-container', 'children')],
            [Input('interval-component', 'n_intervals'),
             Input('dataset-dropdown', 'value'),
             Input('time-range-dropdown', 'value'),
             Input('refresh-btn', 'n_clicks')]
        )
        def update_dashboard(n_intervals, dataset, time_range, refresh_clicks):
            # Generate sample data for demo
            sample_data = self._generate_sample_data(dataset)
            
            # Calculate metrics
            quality_metrics = self.calculate_quality_metrics(
                sample_data, dataset, dataset
            )
            compliance_metrics = self.calculate_indian_compliance_metrics(
                sample_data, dataset
            )
            
            # Update metric cards
            metric_updates = []
            for metric_name in ['completeness', 'accuracy', 'validity', 'consistency', 'timeliness', 'uniqueness']:
                if metric_name in quality_metrics:
                    metric = quality_metrics[metric_name]
                    metric_updates.extend([
                        f"{metric.current_value:.1f}%",
                        f"Target: {metric.target_value:.1f}% | {metric.status}"
                    ])
                else:
                    metric_updates.extend(["N/A", "No data"])
            
            # Create charts
            trends_chart = self._create_trends_chart(quality_metrics)
            distribution_chart = self._create_distribution_chart(quality_metrics)
            compliance_chart = self._create_compliance_chart(compliance_metrics)
            
            # Generate alerts
            alerts = self._generate_alerts(quality_metrics, compliance_metrics)
            
            return metric_updates + [trends_chart, distribution_chart, compliance_chart, alerts]

    def _determine_status(self, current_value: float, target_value: float) -> str:
        """Determine status based on current vs target value"""
        ratio = current_value / target_value
        if ratio >= self.alert_thresholds['good']:
            return 'GOOD'
        elif ratio >= self.alert_thresholds['warning']:
            return 'WARNING'
        else:
            return 'CRITICAL'

    def _determine_compliance_status(self, current_value: float, threshold: float) -> str:
        """Determine compliance status"""
        if current_value >= threshold:
            return 'COMPLIANT'
        elif current_value >= threshold * 0.9:
            return 'WARNING'
        else:
            return 'NON_COMPLIANT'

    def _store_metrics_to_db(self, dataset_name: str, business_domain: str, 
                           metrics: Dict[str, QualityMetric], record_count: int):
        """Store metrics to database"""
        
        conn = sqlite3.connect(self.db_path)
        
        for metric_name, metric in metrics.items():
            conn.execute('''
                INSERT INTO quality_metrics 
                (dataset_name, metric_name, metric_value, metric_target, 
                 metric_status, business_domain, record_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_name, metric_name, metric.current_value, 
                metric.target_value, metric.status, business_domain, record_count
            ))
        
        conn.commit()
        conn.close()

    def _generate_sample_data(self, dataset_type: str) -> pd.DataFrame:
        """Generate sample data for demo purposes"""
        
        np.random.seed(int(time.time()) % 1000)  # Different seed each time
        
        base_size = 1000
        
        if dataset_type == 'banking':
            return pd.DataFrame({
                'account_id': [f'ACC{i:08d}' for i in range(base_size)],
                'customer_name': [f'Customer {i}' for i in range(base_size)],
                'mobile': [f'{random.choice([6,7,8,9])}{random.randint(100000000, 999999999)}' for _ in range(base_size)],
                'email': [f'customer{i}@{"gmail.com" if i%3==0 else "yahoo.com"}' for i in range(base_size)],
                'pan': [f'{"ABCDE"[i%5]}{"FGHIJ"[i%5]}{"KLMNO"[i%5]}{"PQRST"[i%5]}{"UVWXY"[i%5]}{random.randint(1000,9999)}{"Z"[0]}' for i in range(base_size)],
                'aadhaar': [f'{random.randint(100000000000, 999999999999)}' for _ in range(base_size)],
                'amount': np.random.exponential(10000, base_size),
                'timestamp': pd.date_range(start=datetime.now()-timedelta(days=7), end=datetime.now(), periods=base_size)
            })
        
        elif dataset_type == 'ecommerce':
            return pd.DataFrame({
                'order_id': [f'ORD{i:08d}' for i in range(base_size)],
                'customer_id': [f'CUST{i:06d}' for i in range(base_size//10)] * (base_size//100) + [f'CUST{i:06d}' for i in range(base_size % (base_size//100))],
                'product_name': [f'Product {i}' for i in range(base_size)],
                'amount': np.random.lognormal(7, 1, base_size),
                'mobile': [f'{random.choice([6,7,8,9])}{random.randint(100000000, 999999999)}' for _ in range(base_size)],
                'email': [f'customer{i}@domain.com' for i in range(base_size)],
                'timestamp': pd.date_range(start=datetime.now()-timedelta(days=7), end=datetime.now(), periods=base_size)
            })
        
        else:  # Default
            return pd.DataFrame({
                'id': range(base_size),
                'name': [f'Record {i}' for i in range(base_size)],
                'value': np.random.normal(100, 20, base_size),
                'timestamp': pd.date_range(start=datetime.now()-timedelta(days=7), end=datetime.now(), periods=base_size)
            })

    def _create_trends_chart(self, metrics: Dict[str, QualityMetric]) -> go.Figure:
        """Create quality trends chart"""
        
        fig = go.Figure()
        
        metric_names = list(metrics.keys())
        current_values = [metrics[name].current_value for name in metric_names]
        target_values = [metrics[name].target_value for name in metric_names]
        
        fig.add_trace(go.Scatter(
            x=metric_names,
            y=current_values,
            mode='lines+markers',
            name='Current',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=metric_names,
            y=target_values,
            mode='lines+markers',
            name='Target',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title='Quality Metrics Trends',
            xaxis_title='Metrics',
            yaxis_title='Percentage',
            yaxis=dict(range=[0, 100])
        )
        
        return fig

    def _create_distribution_chart(self, metrics: Dict[str, QualityMetric]) -> go.Figure:
        """Create quality distribution pie chart"""
        
        status_counts = {'GOOD': 0, 'WARNING': 0, 'CRITICAL': 0}
        
        for metric in metrics.values():
            status_counts[metric.status] += 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            marker_colors=['green', 'orange', 'red']
        )])
        
        fig.update_layout(title='Quality Status Distribution')
        
        return fig

    def _create_compliance_chart(self, compliance_metrics: Dict[str, QualityMetric]) -> go.Figure:
        """Create compliance metrics chart"""
        
        if not compliance_metrics:
            return go.Figure().add_annotation(text="No compliance data available", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        metric_names = list(compliance_metrics.keys())
        current_values = [compliance_metrics[name].current_value for name in metric_names]
        target_values = [compliance_metrics[name].target_value for name in metric_names]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metric_names,
            y=current_values,
            name='Current',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            x=metric_names,
            y=target_values,
            name='Target',
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title='Indian Compliance Metrics',
            xaxis_title='Compliance Areas',
            yaxis_title='Percentage',
            barmode='group'
        )
        
        return fig

    def _generate_alerts(self, quality_metrics: Dict[str, QualityMetric], 
                        compliance_metrics: Dict[str, QualityMetric]) -> html.Div:
        """Generate alerts based on metrics"""
        
        alerts = []
        
        # Quality metric alerts
        for metric in quality_metrics.values():
            if metric.status == 'CRITICAL':
                alerts.append(
                    dbc.Alert([
                        html.H5(f"Critical: {metric.name}", className="alert-heading"),
                        html.P(f"Current: {metric.current_value:.1f}% | Target: {metric.target_value:.1f}%"),
                        html.P(metric.description)
                    ], color="danger", dismissable=True)
                )
            elif metric.status == 'WARNING':
                alerts.append(
                    dbc.Alert([
                        html.H5(f"Warning: {metric.name}", className="alert-heading"),
                        html.P(f"Current: {metric.current_value:.1f}% | Target: {metric.target_value:.1f}%")
                    ], color="warning", dismissable=True)
                )
        
        # Compliance alerts
        for metric in compliance_metrics.values():
            if metric.status == 'NON_COMPLIANT':
                alerts.append(
                    dbc.Alert([
                        html.H5(f"Compliance Issue: {metric.name}", className="alert-heading"),
                        html.P(f"Current: {metric.current_value:.1f}% | Required: {metric.target_value:.1f}%")
                    ], color="danger", dismissable=True)
                )
        
        if not alerts:
            alerts.append(
                dbc.Alert("All metrics are within acceptable ranges! ✅", color="success")
            )
        
        return html.Div(alerts)

    def start_metric_collection(self):
        """Start background metric collection"""
        
        def collect_metrics():
            while True:
                try:
                    # Simulate metric collection
                    logger.info("Collecting quality metrics...")
                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    logger.error(f"Metric collection error: {e}")
        
        # Start in background thread
        collection_thread = threading.Thread(target=collect_metrics, daemon=True)
        collection_thread.start()

    def run_dashboard(self, host: str = "127.0.0.1", port: int = 8050, debug: bool = True):
        """Run the dashboard application"""
        
        app = self.create_dashboard_app()
        
        logger.info(f"Starting dashboard at http://{host}:{port}")
        print(f"\n🚀 Data Quality Dashboard Starting...")
        print(f"📊 Access dashboard at: http://{host}:{port}")
        print(f"🔄 Auto-refresh every 30 seconds")
        print(f"📱 Mobile responsive design")
        print(f"🇮🇳 Indian compliance metrics included\n")
        
        app.run_server(host=host, port=port, debug=debug)

def main():
    """Main execution function - demo of quality dashboard"""
    
    print("📊 Indian Data Quality Dashboard Demo")
    print("डेटा गुणवत्ता डैशबोर्ड प्रदर्शन\n")
    
    # Initialize dashboard
    dashboard = IndianDataQualityDashboard()
    
    # Generate sample data for testing
    print("Generating sample datasets...")
    banking_data = dashboard._generate_sample_data('banking')
    ecommerce_data = dashboard._generate_sample_data('ecommerce')
    
    # Calculate quality metrics
    print("Calculating quality metrics...")
    banking_metrics = dashboard.calculate_quality_metrics(banking_data, 'Banking Data', 'banking')
    ecommerce_metrics = dashboard.calculate_quality_metrics(ecommerce_data, 'E-commerce Data', 'ecommerce')
    
    # Calculate compliance metrics
    banking_compliance = dashboard.calculate_indian_compliance_metrics(banking_data, 'Banking Data')
    
    # Display results
    print("\n" + "="*60)
    print("BANKING DATA QUALITY METRICS")
    print("="*60)
    for name, metric in banking_metrics.items():
        status_emoji = "✅" if metric.status == "GOOD" else "⚠️" if metric.status == "WARNING" else "❌"
        print(f"{metric.name}: {metric.current_value:.2f}% (Target: {metric.target_value:.2f}%) {status_emoji}")
        print(f"  {metric.description}")
    
    print("\n" + "="*60)
    print("BANKING COMPLIANCE METRICS")
    print("="*60)
    for name, metric in banking_compliance.items():
        status_emoji = "✅" if metric.status == "COMPLIANT" else "⚠️" if metric.status == "WARNING" else "❌"
        print(f"{metric.name}: {metric.current_value:.2f}% (Target: {metric.target_value:.2f}%) {status_emoji}")
    
    print("\n" + "="*60)
    print("E-COMMERCE DATA QUALITY METRICS")
    print("="*60)
    for name, metric in ecommerce_metrics.items():
        status_emoji = "✅" if metric.status == "GOOD" else "⚠️" if metric.status == "WARNING" else "❌"
        print(f"{metric.name}: {metric.current_value:.2f}% (Target: {metric.target_value:.2f}%) {status_emoji}")
    
    # Dashboard launch option
    print("\n" + "="*60)
    print("DASHBOARD LAUNCH")
    print("="*60)
    print("Dashboard system initialized successfully!")
    print("Features available:")
    print("✅ Real-time quality monitoring")
    print("✅ Indian compliance metrics")
    print("✅ Interactive charts and trends")
    print("✅ Automated alerting system")
    print("✅ Multi-dataset support")
    print("✅ Mobile responsive design")
    
    launch_dashboard = input("\nWould you like to launch the interactive dashboard? (y/N): ").lower().strip()
    
    if launch_dashboard == 'y':
        print("\n🚀 Launching interactive dashboard...")
        print("Press Ctrl+C to stop the dashboard")
        try:
            dashboard.run_dashboard()
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped by user")
    else:
        print("\n✅ Dashboard demo complete!")
        print("To launch dashboard later, call: dashboard.run_dashboard()")
    
    print("\n✅ Indian Data Quality Dashboard Demo Complete!")
    print("प्रणाली तैयार है - Ready for production quality monitoring!")
    
    return {
        'banking_metrics': banking_metrics,
        'banking_compliance': banking_compliance,
        'ecommerce_metrics': ecommerce_metrics,
        'dashboard': dashboard
    }

if __name__ == "__main__":
    results = main()