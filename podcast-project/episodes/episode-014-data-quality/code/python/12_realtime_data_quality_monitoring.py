#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 12
Real-time Data Quality Monitoring System

Real-time data quality monitoring for streaming data systems
Real-time streaming data के लिए data quality monitoring system

Author: DStudio Team
Context: Real-time monitoring like Flipkart/Amazon order streams
Scale: 1+ million records per minute real-time validation
"""

import asyncio
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, AsyncGenerator
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
import threading
import time
import queue
import websocket
import redis
from kafka import KafkaConsumer, KafkaProducer
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - रियल-टाइम जांच - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataQualityMetrics:
    """Real-time data quality metrics structure"""
    timestamp: datetime
    total_records: int
    valid_records: int
    invalid_records: int
    validity_rate: float
    error_types: Dict[str, int]
    processing_latency: float
    throughput: float
    alert_conditions: List[str] = field(default_factory=list)

@dataclass
class QualityRule:
    """Data quality rule definition"""
    rule_id: str
    rule_name: str
    field_name: str
    rule_type: str  # 'not_null', 'range', 'regex', 'custom'
    parameters: Dict
    severity: str  # 'critical', 'warning', 'info'
    enabled: bool = True

class RealTimeDataQualityMonitor:
    """
    Real-time data quality monitoring system for streaming data
    Streaming data के लिए real-time data quality monitoring
    
    Features:
    1. Real-time validation of streaming data
    2. Configurable quality rules
    3. Alert system for quality degradation
    4. Performance metrics (throughput, latency)
    5. Dashboard for visualization
    6. Integration with Kafka, Redis, databases
    
    Scale: Handles 1+ million records/minute like e-commerce platforms
    """
    
    def __init__(self, config: Dict = None):
        """Initialize real-time monitoring system"""
        
        self.config = config or {}
        
        # Quality rules registry - गुणवत्ता नियम रजिस्ट्री
        self.quality_rules = {}
        
        # Metrics collection
        self.metrics_window = deque(maxlen=1000)  # Last 1000 metric points
        self.current_metrics = DataQualityMetrics(
            timestamp=datetime.now(),
            total_records=0,
            valid_records=0,
            invalid_records=0,
            validity_rate=100.0,
            error_types={},
            processing_latency=0.0,
            throughput=0.0
        )
        
        # Prometheus metrics for monitoring
        self.prometheus_metrics = {
            'records_processed': Counter('dq_records_processed_total', 'Total records processed'),
            'records_valid': Counter('dq_records_valid_total', 'Valid records'),
            'records_invalid': Counter('dq_records_invalid_total', 'Invalid records'),
            'processing_latency': Histogram('dq_processing_latency_seconds', 'Processing latency'),
            'throughput': Gauge('dq_throughput_records_per_second', 'Records per second'),
            'validity_rate': Gauge('dq_validity_rate_percent', 'Data validity rate')
        }
        
        # Alert thresholds - अलर्ट थ्रेशोल्ड
        self.alert_thresholds = {
            'validity_rate_min': 95.0,  # Alert if validity < 95%
            'throughput_min': 100,      # Alert if throughput < 100 records/sec
            'latency_max': 1.0,         # Alert if latency > 1 second
            'error_rate_max': 5.0       # Alert if error rate > 5%
        }
        
        # Database connection for storing metrics
        self.db_connection = None
        self._init_database()
        
        # Redis connection for caching and pub/sub
        try:
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # Processing queue for incoming data
        self.processing_queue = queue.Queue(maxsize=10000)
        
        # Threading for real-time processing
        self.processing_thread = None
        self.metrics_thread = None
        self.running = False
        
        # Load default quality rules
        self._load_default_rules()
        
        logger.info("Real-time Data Quality Monitor initialized - रियल-टाइम मॉनिटर तैयार!")

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            self.db_connection = sqlite3.connect('data_quality_metrics.db', check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    total_records INTEGER,
                    valid_records INTEGER,
                    invalid_records INTEGER,
                    validity_rate REAL,
                    processing_latency REAL,
                    throughput REAL,
                    error_types TEXT
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    metrics TEXT
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_default_rules(self):
        """Load default data quality rules for Indian e-commerce"""
        
        default_rules = [
            QualityRule(
                rule_id='order_id_not_null',
                rule_name='Order ID Not Null',
                field_name='order_id',
                rule_type='not_null',
                parameters={},
                severity='critical'
            ),
            QualityRule(
                rule_id='email_format',
                rule_name='Email Format Validation',
                field_name='customer_email',
                rule_type='regex',
                parameters={'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
                severity='critical'
            ),
            QualityRule(
                rule_id='phone_indian_format',
                rule_name='Indian Phone Format',
                field_name='customer_phone',
                rule_type='regex',
                parameters={'pattern': r'^(\+91|91|0)?[6-9]\d{9}$'},
                severity='warning'
            ),
            QualityRule(
                rule_id='order_amount_range',
                rule_name='Order Amount Range',
                field_name='order_amount',
                rule_type='range',
                parameters={'min': 1, 'max': 1000000},
                severity='critical'
            ),
            QualityRule(
                rule_id='pincode_format',
                rule_name='Indian Pincode Format',
                field_name='delivery_pincode',
                rule_type='regex',
                parameters={'pattern': r'^\d{6}$'},
                severity='warning'
            ),
            QualityRule(
                rule_id='order_date_recent',
                rule_name='Order Date Validation',
                field_name='order_date',
                rule_type='custom',
                parameters={'function': 'validate_recent_date'},
                severity='critical'
            )
        ]
        
        for rule in default_rules:
            self.quality_rules[rule.rule_id] = rule
        
        logger.info(f"Loaded {len(default_rules)} default quality rules")

    def add_quality_rule(self, rule: QualityRule):
        """Add a new data quality rule"""
        self.quality_rules[rule.rule_id] = rule
        logger.info(f"Added quality rule: {rule.rule_name}")

    def validate_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single record against all quality rules
        एक record को सभी quality rules के against validate करना
        """
        
        is_valid = True
        errors = []
        
        for rule_id, rule in self.quality_rules.items():
            if not rule.enabled:
                continue
            
            field_value = record.get(rule.field_name)
            
            try:
                if rule.rule_type == 'not_null':
                    if field_value is None or field_value == '':
                        is_valid = False
                        errors.append(f"{rule.field_name} cannot be null/empty")
                
                elif rule.rule_type == 'regex':
                    if field_value and not re.match(rule.parameters['pattern'], str(field_value)):
                        is_valid = False
                        errors.append(f"{rule.field_name} format invalid")
                
                elif rule.rule_type == 'range':
                    if field_value is not None:
                        try:
                            value = float(field_value)
                            min_val = rule.parameters.get('min')
                            max_val = rule.parameters.get('max')
                            
                            if min_val is not None and value < min_val:
                                is_valid = False
                                errors.append(f"{rule.field_name} below minimum: {min_val}")
                            
                            if max_val is not None and value > max_val:
                                is_valid = False
                                errors.append(f"{rule.field_name} above maximum: {max_val}")
                        except ValueError:
                            is_valid = False
                            errors.append(f"{rule.field_name} not a valid number")
                
                elif rule.rule_type == 'custom':
                    # Custom validation function
                    if rule.parameters.get('function') == 'validate_recent_date':
                        if not self._validate_recent_date(field_value):
                            is_valid = False
                            errors.append(f"{rule.field_name} date is not recent")
            
            except Exception as e:
                logger.error(f"Error validating rule {rule_id}: {e}")
                errors.append(f"Validation error for {rule.field_name}")
        
        return is_valid, errors

    def _validate_recent_date(self, date_value) -> bool:
        """Custom validation for recent dates"""
        try:
            if isinstance(date_value, str):
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            elif isinstance(date_value, datetime):
                date_obj = date_value
            else:
                return False
            
            # Check if date is within last 30 days and not future
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)
            
            return thirty_days_ago <= date_obj <= now
            
        except Exception:
            return False

    async def process_streaming_data(self, data_stream: AsyncGenerator[Dict, None]):
        """
        Process streaming data with real-time quality monitoring
        Streaming data को real-time quality monitoring के साथ process करना
        """
        
        start_time = time.time()
        processed_count = 0
        valid_count = 0
        invalid_count = 0
        error_counts = defaultdict(int)
        
        async for record in data_stream:
            process_start = time.time()
            
            # Validate record
            is_valid, errors = self.validate_record(record)
            
            # Update counters
            processed_count += 1
            if is_valid:
                valid_count += 1
                self.prometheus_metrics['records_valid'].inc()
            else:
                invalid_count += 1
                self.prometheus_metrics['records_invalid'].inc()
                
                # Count error types
                for error in errors:
                    error_type = error.split(':')[0] if ':' in error else error
                    error_counts[error_type] += 1
            
            self.prometheus_metrics['records_processed'].inc()
            
            # Calculate processing latency
            processing_latency = time.time() - process_start
            self.prometheus_metrics['processing_latency'].observe(processing_latency)
            
            # Update metrics every 100 records or 5 seconds
            if processed_count % 100 == 0 or (time.time() - start_time) >= 5:
                await self._update_metrics(
                    processed_count, valid_count, invalid_count,
                    error_counts, time.time() - start_time
                )
                
                # Reset counters for next window
                start_time = time.time()
                processed_count = 0
                valid_count = 0
                invalid_count = 0
                error_counts = defaultdict(int)

    async def _update_metrics(self, total: int, valid: int, invalid: int,
                            error_counts: Dict, elapsed_time: float):
        """Update real-time metrics"""
        
        validity_rate = (valid / total * 100) if total > 0 else 100
        throughput = total / elapsed_time if elapsed_time > 0 else 0
        avg_latency = elapsed_time / total if total > 0 else 0
        
        # Create metrics object
        metrics = DataQualityMetrics(
            timestamp=datetime.now(),
            total_records=total,
            valid_records=valid,
            invalid_records=invalid,
            validity_rate=validity_rate,
            error_types=dict(error_counts),
            processing_latency=avg_latency,
            throughput=throughput
        )
        
        # Add to metrics window
        self.metrics_window.append(metrics)
        self.current_metrics = metrics
        
        # Update Prometheus metrics
        self.prometheus_metrics['throughput'].set(throughput)
        self.prometheus_metrics['validity_rate'].set(validity_rate)
        
        # Check for alerts
        alerts = self._check_alert_conditions(metrics)
        if alerts:
            await self._send_alerts(alerts, metrics)
        
        # Store in database
        if self.db_connection:
            self._store_metrics_db(metrics)
        
        # Publish to Redis
        if self.redis_client:
            self._publish_metrics_redis(metrics)
        
        logger.info(f"""
        Real-time Metrics Update:
        ========================
        Records: {total} | Valid: {valid} | Invalid: {invalid}
        Validity Rate: {validity_rate:.2f}%
        Throughput: {throughput:.2f} records/sec
        Latency: {avg_latency:.4f} seconds
        """)

    def _check_alert_conditions(self, metrics: DataQualityMetrics) -> List[str]:
        """Check if any alert conditions are met"""
        
        alerts = []
        
        # Validity rate alert
        if metrics.validity_rate < self.alert_thresholds['validity_rate_min']:
            alerts.append(f"Low validity rate: {metrics.validity_rate:.2f}%")
        
        # Throughput alert
        if metrics.throughput < self.alert_thresholds['throughput_min']:
            alerts.append(f"Low throughput: {metrics.throughput:.2f} records/sec")
        
        # Latency alert
        if metrics.processing_latency > self.alert_thresholds['latency_max']:
            alerts.append(f"High latency: {metrics.processing_latency:.4f} seconds")
        
        # Error rate alert
        error_rate = (metrics.invalid_records / metrics.total_records * 100) if metrics.total_records > 0 else 0
        if error_rate > self.alert_thresholds['error_rate_max']:
            alerts.append(f"High error rate: {error_rate:.2f}%")
        
        return alerts

    async def _send_alerts(self, alerts: List[str], metrics: DataQualityMetrics):
        """Send alerts for quality issues"""
        
        for alert in alerts:
            alert_data = {
                'timestamp': metrics.timestamp.isoformat(),
                'alert_type': 'data_quality',
                'severity': 'warning',
                'message': alert,
                'metrics': asdict(metrics)
            }
            
            # Store alert in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO quality_alerts (timestamp, alert_type, severity, message, metrics)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp,
                    'data_quality',
                    'warning',
                    alert,
                    json.dumps(asdict(metrics))
                ))
                self.db_connection.commit()
            
            # Publish alert to Redis
            if self.redis_client:
                self.redis_client.publish('data_quality_alerts', json.dumps(alert_data))
            
            logger.warning(f"DATA QUALITY ALERT: {alert}")

    def _store_metrics_db(self, metrics: DataQualityMetrics):
        """Store metrics in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO quality_metrics 
                (timestamp, total_records, valid_records, invalid_records, 
                 validity_rate, processing_latency, throughput, error_types)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.total_records,
                metrics.valid_records,
                metrics.invalid_records,
                metrics.validity_rate,
                metrics.processing_latency,
                metrics.throughput,
                json.dumps(metrics.error_types)
            ))
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Failed to store metrics in database: {e}")

    def _publish_metrics_redis(self, metrics: DataQualityMetrics):
        """Publish metrics to Redis for real-time dashboards"""
        try:
            metrics_data = asdict(metrics)
            metrics_data['timestamp'] = metrics.timestamp.isoformat()
            
            self.redis_client.publish('data_quality_metrics', json.dumps(metrics_data))
            self.redis_client.setex(
                'latest_data_quality_metrics', 
                300,  # 5 minutes TTL
                json.dumps(metrics_data)
            )
        except Exception as e:
            logger.error(f"Failed to publish metrics to Redis: {e}")

    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for specified time period"""
        
        if not self.db_connection:
            return {'error': 'Database not available'}
        
        try:
            cursor = self.db_connection.cursor()
            since_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_measurements,
                    AVG(validity_rate) as avg_validity_rate,
                    MIN(validity_rate) as min_validity_rate,
                    MAX(validity_rate) as max_validity_rate,
                    AVG(throughput) as avg_throughput,
                    AVG(processing_latency) as avg_latency,
                    SUM(total_records) as total_records_processed
                FROM quality_metrics 
                WHERE timestamp >= ?
            ''', (since_time,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'period_hours': hours,
                    'total_measurements': result[0],
                    'avg_validity_rate': round(result[1] or 0, 2),
                    'min_validity_rate': round(result[2] or 0, 2),
                    'max_validity_rate': round(result[3] or 0, 2),
                    'avg_throughput': round(result[4] or 0, 2),
                    'avg_latency': round(result[5] or 0, 4),
                    'total_records_processed': result[6] or 0
                }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {'error': str(e)}
        
        return {'error': 'No data found'}

    def create_dashboard(self, hours: int = 24) -> str:
        """Create HTML dashboard for data quality metrics"""
        
        if not self.db_connection:
            return "<html><body><h1>Database not available</h1></body></html>"
        
        try:
            cursor = self.db_connection.cursor()
            since_time = datetime.now() - timedelta(hours=hours)
            
            # Get time series data
            cursor.execute('''
                SELECT timestamp, validity_rate, throughput, processing_latency
                FROM quality_metrics 
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (since_time,))
            
            data = cursor.fetchall()
            
            if not data:
                return "<html><body><h1>No data available</h1></body></html>"
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'validity_rate', 'throughput', 'latency'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=['Validity Rate (%)', 'Throughput (records/sec)', 'Processing Latency (seconds)'],
                vertical_spacing=0.1
            )
            
            # Validity rate plot
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['validity_rate'], 
                          name='Validity Rate', line=dict(color='green')),
                row=1, col=1
            )
            
            # Throughput plot
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['throughput'], 
                          name='Throughput', line=dict(color='blue')),
                row=2, col=1
            )
            
            # Latency plot
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['latency'], 
                          name='Latency', line=dict(color='red')),
                row=3, col=1
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                title_text=f"Data Quality Dashboard - Last {hours} Hours",
                showlegend=False
            )
            
            # Add alert threshold lines
            fig.add_hline(y=self.alert_thresholds['validity_rate_min'], 
                         line_dash="dash", line_color="red", row=1, col=1)
            
            # Convert to HTML
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return f"<html><body><h1>Error creating dashboard: {e}</h1></body></html>"

async def simulate_streaming_data(num_records: int = 1000) -> AsyncGenerator[Dict, None]:
    """Simulate streaming e-commerce data for testing"""
    
    import random
    
    # Indian cities and states
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune']
    states = ['MH', 'DL', 'KA', 'TN', 'WB', 'TG', 'MH']
    
    for i in range(num_records):
        # Generate realistic data with some errors
        record = {
            'order_id': f'ORD-{i:08d}',
            'customer_email': f'customer{i}@example.com',
            'customer_phone': f'+91{random.randint(6000000000, 9999999999)}',
            'order_amount': random.uniform(100, 50000),
            'delivery_city': random.choice(cities),
            'delivery_state': random.choice(states),
            'delivery_pincode': f'{random.randint(100000, 999999):06d}',
            'order_date': datetime.now().isoformat(),
            'payment_method': random.choice(['UPI', 'Card', 'COD', 'Net Banking'])
        }
        
        # Introduce errors randomly (10% error rate)
        if random.random() < 0.1:
            error_type = random.choice(['null_email', 'invalid_phone', 'future_date', 'negative_amount'])
            
            if error_type == 'null_email':
                record['customer_email'] = None
            elif error_type == 'invalid_phone':
                record['customer_phone'] = '123456789'  # Invalid format
            elif error_type == 'future_date':
                record['order_date'] = (datetime.now() + timedelta(days=1)).isoformat()
            elif error_type == 'negative_amount':
                record['order_amount'] = -100
        
        yield record
        await asyncio.sleep(0.01)  # Simulate processing delay

def main():
    """Main execution function - demo of real-time monitoring system"""
    
    print("📊 Real-time Data Quality Monitoring System Demo")
    print("रियल-टाइम डेटा गुणवत्ता निगरानी प्रणाली का प्रदर्शन\n")
    
    # Initialize monitor
    monitor = RealTimeDataQualityMonitor()
    
    # Test 1: Quality rules validation
    print("Test 1: Quality Rules Validation")
    print("=" * 35)
    
    test_records = [
        {
            'order_id': 'ORD-12345678',
            'customer_email': 'user@example.com',
            'customer_phone': '+919876543210',
            'order_amount': 1500,
            'delivery_pincode': '400001',
            'order_date': datetime.now().isoformat()
        },
        {
            'order_id': None,  # Error: null order_id
            'customer_email': 'invalid-email',  # Error: invalid email
            'customer_phone': '123',  # Error: invalid phone
            'order_amount': -100,  # Error: negative amount
            'delivery_pincode': '12345',  # Error: invalid pincode
            'order_date': (datetime.now() + timedelta(days=1)).isoformat()  # Error: future date
        }
    ]
    
    for i, record in enumerate(test_records):
        is_valid, errors = monitor.validate_record(record)
        print(f"""
    Record {i+1}:
    Valid: {'✅' if is_valid else '❌'}
    Errors: {len(errors)}
    Details: {errors if errors else 'No errors'}
        """)
    
    # Test 2: Custom quality rule
    print("\nTest 2: Adding Custom Quality Rule")
    print("=" * 35)
    
    # Add custom rule for Indian state codes
    custom_rule = QualityRule(
        rule_id='indian_state_code',
        rule_name='Indian State Code Validation',
        field_name='delivery_state',
        rule_type='regex',
        parameters={'pattern': r'^(AP|AR|AS|BR|CT|GA|GJ|HR|HP|JH|KA|KL|MP|MH|MN|ML|MZ|NL|OR|PB|RJ|SK|TN|TG|TR|UP|UT|WB|AN|CH|DH|DD|LD|JK|LA|PY)$'},
        severity='warning'
    )
    
    monitor.add_quality_rule(custom_rule)
    
    # Test with state code
    test_record_state = {
        'order_id': 'ORD-87654321',
        'customer_email': 'test@example.com',
        'customer_phone': '+919876543210',
        'order_amount': 2500,
        'delivery_pincode': '400001',
        'delivery_state': 'MH',  # Valid Maharashtra code
        'order_date': datetime.now().isoformat()
    }
    
    is_valid, errors = monitor.validate_record(test_record_state)
    print(f"""
    State Code Test:
    Valid: {'✅' if is_valid else '❌'}
    Errors: {errors if errors else 'No errors'}
    """)
    
    # Test 3: Simulated streaming data processing
    print("\nTest 3: Simulated Streaming Data Processing")
    print("=" * 45)
    
    async def run_streaming_test():
        print("Processing streaming data for 10 seconds...")
        
        # Process streaming data
        data_stream = simulate_streaming_data(500)
        
        # Run for limited time
        try:
            await asyncio.wait_for(
                monitor.process_streaming_data(data_stream),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print("Streaming test completed (timeout reached)")
        
        # Show final metrics
        current_metrics = monitor.current_metrics
        print(f"""
        Final Streaming Metrics:
        =======================
        Total Records: {current_metrics.total_records}
        Valid Records: {current_metrics.valid_records}
        Invalid Records: {current_metrics.invalid_records}
        Validity Rate: {current_metrics.validity_rate:.2f}%
        Throughput: {current_metrics.throughput:.2f} records/sec
        Avg Latency: {current_metrics.processing_latency:.4f} seconds
        Error Types: {current_metrics.error_types}
        """)
    
    # Run async streaming test
    asyncio.run(run_streaming_test())
    
    # Test 4: Metrics summary
    print("\nTest 4: Metrics Summary")
    print("=" * 25)
    
    summary = monitor.get_metrics_summary(hours=1)
    if 'error' not in summary:
        print(f"""
        Metrics Summary (Last 1 Hour):
        ==============================
        Total Measurements: {summary['total_measurements']}
        Average Validity Rate: {summary['avg_validity_rate']}%
        Min Validity Rate: {summary['min_validity_rate']}%
        Max Validity Rate: {summary['max_validity_rate']}%
        Average Throughput: {summary['avg_throughput']} records/sec
        Average Latency: {summary['avg_latency']} seconds
        Total Records Processed: {summary['total_records_processed']}
        """)
    else:
        print(f"Metrics summary error: {summary['error']}")
    
    # Test 5: Dashboard creation
    print("\nTest 5: Dashboard Creation")
    print("=" * 25)
    
    dashboard_html = monitor.create_dashboard(hours=1)
    
    # Save dashboard to file
    with open('data_quality_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("Dashboard created and saved as 'data_quality_dashboard.html'")
    print("Open this file in a web browser to view the real-time dashboard")
    
    print("\n✅ Real-time Data Quality Monitoring System Demo Complete!")
    print("Production monitoring system ready - उत्पादन निगरानी सिस्टम तैयार!")
    
    return {
        'current_metrics': monitor.current_metrics,
        'summary': summary,
        'rules_count': len(monitor.quality_rules)
    }

if __name__ == "__main__":
    results = main()