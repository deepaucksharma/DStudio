#!/usr/bin/env python3
"""
Advanced XCom Patterns for Paytm Payment Processing
Focus: Complex data passing, custom XCom backends, data serialization

Ye DAG Paytm payment processing ke liye advanced XCom patterns use karta hai.
Mumbai ke hawala system jaise secure data transfer!

Production Ready: Yes
Testing Required: Yes
Dependencies: Apache Airflow, Redis, PostgreSQL, Custom XCom Backend
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
import json
import pickle
import hashlib
from dataclasses import dataclass, asdict
from decimal import Decimal

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.utils.decorators import task
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable, XCom
from airflow.models.baseoperator import BaseOperator
from airflow.configuration import conf
from airflow.utils.context import Context

# Custom imports for XCom handling
from airflow.models.xcom import BaseXCom
from airflow.utils.session import provide_session
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Payment data models
@dataclass
class PaymentTransaction:
    transaction_id: str
    user_id: str
    amount: Decimal
    currency: str
    payment_method: str
    merchant_id: str
    status: str
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class FraudAnalysisResult:
    transaction_id: str
    risk_score: float
    risk_level: str
    flagged_reasons: List[str]
    recommended_action: str
    analysis_timestamp: datetime

@dataclass
class SettlementBatch:
    batch_id: str
    merchant_id: str
    transactions: List[str]
    total_amount: Decimal
    settlement_date: datetime
    status: str
    processing_fee: Decimal

# Custom XCom Backend for large data
class RedisXComBackend(BaseXCom):
    """Custom XCom backend using Redis for large data storage"""
    
    @staticmethod
    def serialize_value(value, **kwargs) -> Any:
        """Serialize value for storage"""
        if isinstance(value, (dict, list)) and len(json.dumps(value)) > 1024:  # > 1KB
            # Store in Redis and return reference
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, db=1)
            
            # Generate unique key
            key = f"xcom:{hashlib.md5(json.dumps(value, default=str).encode()).hexdigest()}"
            
            # Store in Redis with 24h expiry
            redis_client.setex(key, 86400, json.dumps(value, default=str))
            
            return {'__redis_key__': key, '__type__': 'redis_reference'}
        
        return BaseXCom.serialize_value(value, **kwargs)
    
    @staticmethod
    def deserialize_value(result) -> Any:
        """Deserialize value from storage"""
        if isinstance(result, dict) and result.get('__type__') == 'redis_reference':
            # Retrieve from Redis
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, db=1)
            
            key = result['__redis_key__']
            data = redis_client.get(key)
            
            if data:
                return json.loads(data)
            else:
                logger.warning(f"Redis key {key} not found, returning None")
                return None
        
        return BaseXCom.deserialize_value(result)

# DAG configuration
default_args = {
    'owner': 'paytm-payments-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['payments@paytm.com', 'fraud@paytm.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'catchup': False,
    'max_active_runs': 1
}

# Create DAG
dag = DAG(
    'paytm_xcom_patterns_payment_processing',
    default_args=default_args,
    description='Advanced XCom Patterns for Paytm Payment Processing',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    tags=['paytm', 'payments', 'xcom', 'advanced'],
    catchup=False,
    doc_md="""
    # Paytm Advanced XCom Patterns DAG
    
    Ye DAG multiple XCom patterns demonstrate karta hai:
    1. Simple XCom passing
    2. Complex object serialization
    3. Custom XCom backends
    4. Large data handling
    5. Cross-task-group communication
    6. XCom cleanup and management
    
    Mumbai ke payment system jaise secure aur efficient!
    """,
)

def create_payment_ingestion_group() -> TaskGroup:
    """Create task group for payment data ingestion with XCom patterns"""
    
    with TaskGroup(group_id='payment_ingestion', dag=dag) as group:
        
        @task
        def fetch_pending_payments(**context) -> Dict[str, Any]:
            """Fetch pending payments and return via XCom"""
            
            # Simulate fetching payments from database/API
            import random
            
            payments = []
            payment_methods = ['UPI', 'CARD', 'WALLET', 'NET_BANKING']
            statuses = ['PENDING', 'PROCESSING', 'INITIATED']
            
            for i in range(random.randint(50, 200)):
                payment = PaymentTransaction(
                    transaction_id=f"TXN_{datetime.now().strftime('%Y%m%d')}_{i:06d}",
                    user_id=f"USER_{random.randint(1, 10000):08d}",
                    amount=Decimal(str(random.uniform(10, 10000))),
                    currency='INR',
                    payment_method=random.choice(payment_methods),
                    merchant_id=f"MERCHANT_{random.randint(1, 1000):06d}",
                    status=random.choice(statuses),
                    created_at=datetime.now() - timedelta(minutes=random.randint(1, 60)),
                    metadata={
                        'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        'device_type': random.choice(['mobile', 'web', 'tablet']),
                        'location': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad']),
                        'user_agent': 'PaytmApp/1.0'
                    }
                )
                payments.append(asdict(payment))
            
            logger.info(f"Fetched {len(payments)} pending payments")
            
            # Store summary in regular XCom
            summary = {
                'total_payments': len(payments),
                'total_amount': sum(Decimal(p['amount']) for p in payments),
                'payment_methods': {method: sum(1 for p in payments if p['payment_method'] == method) 
                                   for method in payment_methods},
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            # Store detailed payments in custom XCom (will use Redis for large data)
            context['task_instance'].xcom_push(key='payment_details', value=payments)
            context['task_instance'].xcom_push(key='payment_summary', value=summary)
            
            return summary
        
        @task
        def categorize_payments(**context) -> Dict[str, List[Dict]]:
            """Categorize payments by type and priority"""
            
            # Pull payment details from XCom
            payments = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.fetch_pending_payments',
                key='payment_details'
            )
            
            if not payments:
                logger.error("No payment data received from upstream task")
                return {}
            
            # Categorize payments
            categorized = {
                'high_value': [],
                'regular': [],
                'micro_payments': [],
                'suspicious': []
            }
            
            for payment in payments:
                amount = float(payment['amount'])
                
                # High value transactions
                if amount >= 10000:
                    categorized['high_value'].append(payment)
                # Micro payments
                elif amount <= 100:
                    categorized['micro_payments'].append(payment)
                # Check for suspicious patterns
                elif (payment['payment_method'] == 'UPI' and amount > 5000 and 
                      payment['metadata']['device_type'] == 'web'):
                    categorized['suspicious'].append(payment)
                else:
                    categorized['regular'].append(payment)
            
            # Log categorization results
            category_counts = {cat: len(transactions) for cat, transactions in categorized.items()}
            logger.info(f"Payment categorization: {category_counts}")
            
            # Store each category separately for parallel processing
            for category, transactions in categorized.items():
                context['task_instance'].xcom_push(key=f'{category}_payments', value=transactions)
            
            context['task_instance'].xcom_push(key='categorization_summary', value=category_counts)
            
            return category_counts
        
        @task
        def validate_payment_data(**context) -> Dict[str, Any]:
            """Validate payment data quality"""
            
            payment_summary = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.fetch_pending_payments',
                key='payment_summary'
            )
            
            categorization = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.categorize_payments',
                key='categorization_summary'
            )
            
            validation_results = {
                'total_payments_match': (
                    payment_summary['total_payments'] == sum(categorization.values())
                ),
                'data_quality_score': 0.0,
                'validation_timestamp': datetime.now().isoformat(),
                'issues': []
            }
            
            # Data quality checks
            quality_score = 100.0
            
            if payment_summary['total_payments'] == 0:
                validation_results['issues'].append('No payments found')
                quality_score -= 50
            
            if categorization.get('suspicious', 0) > payment_summary['total_payments'] * 0.1:
                validation_results['issues'].append('High suspicious transaction rate')
                quality_score -= 20
            
            if not validation_results['total_payments_match']:
                validation_results['issues'].append('Payment count mismatch between tasks')
                quality_score -= 30
            
            validation_results['data_quality_score'] = max(quality_score, 0.0)
            
            logger.info(f"Data validation completed: {validation_results}")
            
            return validation_results
        
        # Task dependencies
        payments_fetch = fetch_pending_payments()
        payments_categorization = categorize_payments()
        data_validation = validate_payment_data()
        
        payments_fetch >> payments_categorization >> data_validation
    
    return group

def create_fraud_analysis_group() -> TaskGroup:
    """Create task group for fraud analysis using XCom data"""
    
    with TaskGroup(group_id='fraud_analysis', dag=dag) as group:
        
        @task
        def analyze_high_value_transactions(**context) -> List[Dict]:
            """Analyze high value transactions for fraud"""
            
            # Pull high value payments from previous task group
            high_value_payments = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.categorize_payments',
                key='high_value_payments'
            )
            
            if not high_value_payments:
                logger.info("No high value transactions to analyze")
                return []
            
            fraud_results = []
            
            for payment in high_value_payments:
                risk_score = 0.0
                flagged_reasons = []
                
                # Risk scoring algorithm
                amount = float(payment['amount'])
                
                # Amount-based risk
                if amount > 50000:
                    risk_score += 30
                    flagged_reasons.append('Very high amount')
                elif amount > 25000:
                    risk_score += 15
                    flagged_reasons.append('High amount')
                
                # Time-based risk
                created_at = datetime.fromisoformat(payment['created_at'].replace('Z', '+00:00'))
                current_hour = created_at.hour
                if current_hour < 6 or current_hour > 23:
                    risk_score += 20
                    flagged_reasons.append('Unusual transaction time')
                
                # Location-based risk
                location = payment['metadata']['location']
                if location not in ['Mumbai', 'Delhi', 'Bangalore']:
                    risk_score += 10
                    flagged_reasons.append('Unusual location')
                
                # Payment method risk
                if payment['payment_method'] == 'NET_BANKING' and amount > 30000:
                    risk_score += 15
                    flagged_reasons.append('High value net banking')
                
                # Device risk
                if payment['metadata']['device_type'] == 'web' and amount > 20000:
                    risk_score += 10
                    flagged_reasons.append('High value web transaction')
                
                # Determine risk level and action
                if risk_score >= 60:
                    risk_level = 'HIGH'
                    action = 'BLOCK'
                elif risk_score >= 35:
                    risk_level = 'MEDIUM'
                    action = 'MANUAL_REVIEW'
                elif risk_score >= 15:
                    risk_level = 'LOW'
                    action = 'MONITOR'
                else:
                    risk_level = 'MINIMAL'
                    action = 'APPROVE'
                
                fraud_result = FraudAnalysisResult(
                    transaction_id=payment['transaction_id'],
                    risk_score=risk_score,
                    risk_level=risk_level,
                    flagged_reasons=flagged_reasons,
                    recommended_action=action,
                    analysis_timestamp=datetime.now()
                )
                
                fraud_results.append(asdict(fraud_result))
            
            logger.info(f"Analyzed {len(fraud_results)} high value transactions")
            
            # Store detailed results and summary
            blocked_count = sum(1 for r in fraud_results if r['recommended_action'] == 'BLOCK')
            review_count = sum(1 for r in fraud_results if r['recommended_action'] == 'MANUAL_REVIEW')
            
            summary = {
                'total_analyzed': len(fraud_results),
                'blocked_transactions': blocked_count,
                'manual_review_required': review_count,
                'avg_risk_score': sum(r['risk_score'] for r in fraud_results) / len(fraud_results) if fraud_results else 0
            }
            
            context['task_instance'].xcom_push(key='fraud_analysis_details', value=fraud_results)
            context['task_instance'].xcom_push(key='fraud_analysis_summary', value=summary)
            
            return fraud_results
        
        @task
        def analyze_suspicious_patterns(**context) -> Dict[str, Any]:
            """Analyze suspicious transaction patterns"""
            
            # Pull suspicious payments
            suspicious_payments = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.categorize_payments',
                key='suspicious_payments'
            )
            
            if not suspicious_payments:
                return {'pattern_analysis': 'No suspicious transactions found'}
            
            # Pattern analysis
            patterns = {
                'ip_frequency': {},
                'user_frequency': {},
                'merchant_frequency': {},
                'time_patterns': {'night_transactions': 0, 'weekend_transactions': 0}
            }
            
            for payment in suspicious_payments:
                ip = payment['metadata']['ip_address']
                user_id = payment['user_id']
                merchant_id = payment['merchant_id']
                
                # IP frequency
                patterns['ip_frequency'][ip] = patterns['ip_frequency'].get(ip, 0) + 1
                
                # User frequency
                patterns['user_frequency'][user_id] = patterns['user_frequency'].get(user_id, 0) + 1
                
                # Merchant frequency
                patterns['merchant_frequency'][merchant_id] = patterns['merchant_frequency'].get(merchant_id, 0) + 1
                
                # Time patterns
                created_at = datetime.fromisoformat(payment['created_at'].replace('Z', '+00:00'))
                if created_at.hour < 6 or created_at.hour > 22:
                    patterns['time_patterns']['night_transactions'] += 1
                if created_at.weekday() >= 5:  # Weekend
                    patterns['time_patterns']['weekend_transactions'] += 1
            
            # Find high-frequency entities (potential fraud rings)
            high_freq_ips = {ip: count for ip, count in patterns['ip_frequency'].items() if count >= 5}
            high_freq_users = {user: count for user, count in patterns['user_frequency'].items() if count >= 3}
            high_freq_merchants = {merchant: count for merchant, count in patterns['merchant_frequency'].items() if count >= 10}
            
            pattern_analysis = {
                'total_suspicious': len(suspicious_payments),
                'high_frequency_ips': high_freq_ips,
                'high_frequency_users': high_freq_users,
                'high_frequency_merchants': high_freq_merchants,
                'time_patterns': patterns['time_patterns'],
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Suspicious pattern analysis: {pattern_analysis}")
            
            return pattern_analysis
        
        @task
        def generate_fraud_alerts(**context) -> List[Dict]:
            """Generate fraud alerts based on analysis"""
            
            # Pull analysis results
            fraud_analysis = context['task_instance'].xcom_pull(
                task_ids='fraud_analysis.analyze_high_value_transactions',
                key='fraud_analysis_summary'
            )
            
            pattern_analysis = context['task_instance'].xcom_pull(
                task_ids='fraud_analysis.analyze_suspicious_patterns'
            )
            
            alerts = []
            
            # High risk transaction alerts
            if fraud_analysis and fraud_analysis['blocked_transactions'] > 0:
                alerts.append({
                    'alert_type': 'HIGH_RISK_TRANSACTIONS',
                    'severity': 'CRITICAL',
                    'message': f"{fraud_analysis['blocked_transactions']} transactions blocked due to high fraud risk",
                    'details': fraud_analysis,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Manual review alerts
            if fraud_analysis and fraud_analysis['manual_review_required'] > 10:
                alerts.append({
                    'alert_type': 'HIGH_MANUAL_REVIEW_VOLUME',
                    'severity': 'HIGH',
                    'message': f"{fraud_analysis['manual_review_required']} transactions require manual review",
                    'details': fraud_analysis,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Pattern-based alerts
            if pattern_analysis and isinstance(pattern_analysis, dict):
                if pattern_analysis.get('high_frequency_ips'):
                    alerts.append({
                        'alert_type': 'SUSPICIOUS_IP_PATTERN',
                        'severity': 'MEDIUM',
                        'message': f"Detected {len(pattern_analysis['high_frequency_ips'])} high-frequency IPs",
                        'details': pattern_analysis['high_frequency_ips'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                if pattern_analysis['time_patterns']['night_transactions'] > 20:
                    alerts.append({
                        'alert_type': 'UNUSUAL_TIME_PATTERN',
                        'severity': 'MEDIUM',
                        'message': f"{pattern_analysis['time_patterns']['night_transactions']} night transactions detected",
                        'details': pattern_analysis['time_patterns'],
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.info(f"Generated {len(alerts)} fraud alerts")
            
            return alerts
        
        # Task dependencies
        fraud_analysis_task = analyze_high_value_transactions()
        pattern_analysis_task = analyze_suspicious_patterns()
        alerts_task = generate_fraud_alerts()
        
        [fraud_analysis_task, pattern_analysis_task] >> alerts_task
    
    return group

def create_settlement_processing_group() -> TaskGroup:
    """Create task group for settlement processing with complex XCom usage"""
    
    with TaskGroup(group_id='settlement_processing', dag=dag) as group:
        
        @task
        def create_settlement_batches(**context) -> List[Dict]:
            """Create settlement batches from approved payments"""
            
            # Pull categorized payments and fraud analysis
            regular_payments = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.categorize_payments',
                key='regular_payments'
            ) or []
            
            high_value_payments = context['task_instance'].xcom_pull(
                task_ids='payment_ingestion.categorize_payments',
                key='high_value_payments'
            ) or []
            
            fraud_details = context['task_instance'].xcom_pull(
                task_ids='fraud_analysis.analyze_high_value_transactions',
                key='fraud_analysis_details'
            ) or []
            
            # Filter approved high value payments
            fraud_dict = {r['transaction_id']: r for r in fraud_details}
            approved_high_value = []
            
            for payment in high_value_payments:
                fraud_result = fraud_dict.get(payment['transaction_id'], {})
                if fraud_result.get('recommended_action') in ['APPROVE', 'MONITOR']:
                    approved_high_value.append(payment)
            
            # Combine approved payments
            all_approved = regular_payments + approved_high_value
            
            if not all_approved:
                logger.info("No approved payments for settlement")
                return []
            
            # Group by merchant for settlement batches
            merchant_groups = {}
            for payment in all_approved:
                merchant_id = payment['merchant_id']
                if merchant_id not in merchant_groups:
                    merchant_groups[merchant_id] = []
                merchant_groups[merchant_id].append(payment)
            
            settlement_batches = []
            
            for merchant_id, payments in merchant_groups.items():
                # Create settlement batch
                total_amount = sum(Decimal(p['amount']) for p in payments)
                processing_fee = total_amount * Decimal('0.02')  # 2% processing fee
                
                batch = SettlementBatch(
                    batch_id=f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{merchant_id}",
                    merchant_id=merchant_id,
                    transactions=[p['transaction_id'] for p in payments],
                    total_amount=total_amount - processing_fee,
                    settlement_date=datetime.now() + timedelta(days=1),  # T+1 settlement
                    status='PENDING',
                    processing_fee=processing_fee
                )
                
                settlement_batches.append(asdict(batch))
            
            logger.info(f"Created {len(settlement_batches)} settlement batches")
            
            # Store batch details and summary
            batch_summary = {
                'total_batches': len(settlement_batches),
                'total_settlement_amount': sum(float(b['total_amount']) for b in settlement_batches),
                'total_processing_fees': sum(float(b['processing_fee']) for b in settlement_batches),
                'merchants_count': len(merchant_groups),
                'creation_timestamp': datetime.now().isoformat()
            }
            
            context['task_instance'].xcom_push(key='settlement_batches', value=settlement_batches)
            context['task_instance'].xcom_push(key='settlement_summary', value=batch_summary)
            
            return settlement_batches
        
        @task
        def validate_settlement_batches(**context) -> Dict[str, Any]:
            """Validate settlement batches"""
            
            settlement_batches = context['task_instance'].xcom_pull(
                task_ids='settlement_processing.create_settlement_batches',
                key='settlement_batches'
            )
            
            if not settlement_batches:
                return {'validation_status': 'NO_BATCHES', 'issues': ['No settlement batches to validate']}
            
            validation_results = {
                'validation_status': 'PASSED',
                'issues': [],
                'batch_validations': [],
                'validation_timestamp': datetime.now().isoformat()
            }
            
            for batch in settlement_batches:
                batch_validation = {
                    'batch_id': batch['batch_id'],
                    'is_valid': True,
                    'issues': []
                }
                
                # Validate batch structure
                if not batch['transactions']:
                    batch_validation['is_valid'] = False
                    batch_validation['issues'].append('No transactions in batch')
                
                # Validate amounts
                if float(batch['total_amount']) <= 0:
                    batch_validation['is_valid'] = False
                    batch_validation['issues'].append('Invalid total amount')
                
                if float(batch['processing_fee']) < 0:
                    batch_validation['is_valid'] = False
                    batch_validation['issues'].append('Invalid processing fee')
                
                # Validate settlement date
                settlement_date = datetime.fromisoformat(batch['settlement_date'].replace('Z', '+00:00'))
                if settlement_date <= datetime.now():
                    batch_validation['is_valid'] = False
                    batch_validation['issues'].append('Settlement date should be in future')
                
                validation_results['batch_validations'].append(batch_validation)
                
                if not batch_validation['is_valid']:
                    validation_results['validation_status'] = 'FAILED'
                    validation_results['issues'].extend(batch_validation['issues'])
            
            logger.info(f"Settlement validation: {validation_results['validation_status']}")
            
            return validation_results
        
        @task
        def process_settlements(**context) -> Dict[str, Any]:
            """Process validated settlement batches"""
            
            # Pull validation results
            validation_results = context['task_instance'].xcom_pull(
                task_ids='settlement_processing.validate_settlement_batches'
            )
            
            if validation_results['validation_status'] != 'PASSED':
                logger.error(f"Settlement validation failed: {validation_results['issues']}")
                return {'processing_status': 'FAILED', 'error': 'Validation failed'}
            
            # Pull settlement batches
            settlement_batches = context['task_instance'].xcom_pull(
                task_ids='settlement_processing.create_settlement_batches',
                key='settlement_batches'
            )
            
            processing_results = {
                'processing_status': 'SUCCESS',
                'processed_batches': 0,
                'failed_batches': 0,
                'total_amount_processed': 0.0,
                'processing_timestamp': datetime.now().isoformat(),
                'batch_results': []
            }
            
            for batch in settlement_batches:
                try:
                    # Simulate settlement processing
                    batch_result = {
                        'batch_id': batch['batch_id'],
                        'merchant_id': batch['merchant_id'],
                        'status': 'PROCESSED',
                        'processed_amount': batch['total_amount'],
                        'transaction_count': len(batch['transactions']),
                        'processing_time': datetime.now().isoformat()
                    }
                    
                    processing_results['processed_batches'] += 1
                    processing_results['total_amount_processed'] += float(batch['total_amount'])
                    processing_results['batch_results'].append(batch_result)
                    
                    logger.info(f"Processed settlement batch: {batch['batch_id']}")
                    
                except Exception as e:
                    batch_result = {
                        'batch_id': batch['batch_id'],
                        'merchant_id': batch['merchant_id'],
                        'status': 'FAILED',
                        'error': str(e),
                        'processing_time': datetime.now().isoformat()
                    }
                    
                    processing_results['failed_batches'] += 1
                    processing_results['batch_results'].append(batch_result)
                    
                    logger.error(f"Failed to process settlement batch {batch['batch_id']}: {e}")
            
            return processing_results
        
        # Task dependencies
        create_batches = create_settlement_batches()
        validate_batches = validate_settlement_batches()
        process_batches = process_settlements()
        
        create_batches >> validate_batches >> process_batches
    
    return group

@task
def generate_final_report(**context) -> Dict[str, Any]:
    """Generate final processing report using all XCom data"""
    
    # Collect data from all task groups
    report_data = {
        'execution_summary': {
            'dag_run_id': context['dag_run'].dag_id,
            'execution_date': context['ds'],
            'start_time': context['dag_run'].start_date.isoformat() if context['dag_run'].start_date else None,
            'report_generated_at': datetime.now().isoformat()
        }
    }
    
    # Payment ingestion data
    try:
        payment_summary = context['task_instance'].xcom_pull(
            task_ids='payment_ingestion.fetch_pending_payments',
            key='payment_summary'
        )
        categorization = context['task_instance'].xcom_pull(
            task_ids='payment_ingestion.categorize_payments',
            key='categorization_summary'
        )
        validation = context['task_instance'].xcom_pull(
            task_ids='payment_ingestion.validate_payment_data'
        )
        
        report_data['payment_ingestion'] = {
            'summary': payment_summary,
            'categorization': categorization,
            'validation': validation
        }
    except Exception as e:
        report_data['payment_ingestion'] = {'error': str(e)}
    
    # Fraud analysis data
    try:
        fraud_summary = context['task_instance'].xcom_pull(
            task_ids='fraud_analysis.analyze_high_value_transactions',
            key='fraud_analysis_summary'
        )
        pattern_analysis = context['task_instance'].xcom_pull(
            task_ids='fraud_analysis.analyze_suspicious_patterns'
        )
        fraud_alerts = context['task_instance'].xcom_pull(
            task_ids='fraud_analysis.generate_fraud_alerts'
        )
        
        report_data['fraud_analysis'] = {
            'summary': fraud_summary,
            'patterns': pattern_analysis,
            'alerts': fraud_alerts
        }
    except Exception as e:
        report_data['fraud_analysis'] = {'error': str(e)}
    
    # Settlement processing data
    try:
        settlement_summary = context['task_instance'].xcom_pull(
            task_ids='settlement_processing.create_settlement_batches',
            key='settlement_summary'
        )
        settlement_validation = context['task_instance'].xcom_pull(
            task_ids='settlement_processing.validate_settlement_batches'
        )
        settlement_processing = context['task_instance'].xcom_pull(
            task_ids='settlement_processing.process_settlements'
        )
        
        report_data['settlement_processing'] = {
            'summary': settlement_summary,
            'validation': settlement_validation,
            'processing': settlement_processing
        }
    except Exception as e:
        report_data['settlement_processing'] = {'error': str(e)}
    
    # Generate insights
    insights = []
    
    if report_data.get('payment_ingestion', {}).get('summary'):
        total_amount = report_data['payment_ingestion']['summary'].get('total_amount', 0)
        insights.append(f"Total payment value processed: ₹{total_amount:,.2f}")
    
    if report_data.get('fraud_analysis', {}).get('summary'):
        blocked = report_data['fraud_analysis']['summary'].get('blocked_transactions', 0)
        if blocked > 0:
            insights.append(f"Blocked {blocked} high-risk transactions")
    
    if report_data.get('settlement_processing', {}).get('processing'):
        processed_amount = report_data['settlement_processing']['processing'].get('total_amount_processed', 0)
        if processed_amount > 0:
            insights.append(f"Successfully settled ₹{processed_amount:,.2f}")
    
    report_data['insights'] = insights
    
    logger.info(f"Final report generated with {len(insights)} insights")
    logger.info(f"Report data keys: {list(report_data.keys())}")
    
    return report_data

@task
def cleanup_xcom_data(**context) -> Dict[str, int]:
    """Clean up old XCom data to prevent storage bloat"""
    
    from airflow.models import XCom
    from airflow.utils.session import provide_session
    from sqlalchemy.orm import Session
    
    @provide_session
    def cleanup_old_xcom(session: Session) -> int:
        # Delete XCom entries older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        
        deleted_count = session.query(XCom).filter(
            XCom.timestamp < cutoff_date
        ).count()
        
        session.query(XCom).filter(
            XCom.timestamp < cutoff_date
        ).delete()
        
        session.commit()
        return deleted_count
    
    deleted_count = cleanup_old_xcom()
    
    # Also cleanup Redis XCom data
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=1)
        
        # Get all XCom keys older than 7 days
        pattern = "xcom:*"
        keys = redis_client.keys(pattern)
        
        redis_deleted = 0
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl < 0 or ttl < 604800:  # Less than 7 days TTL remaining
                redis_client.delete(key)
                redis_deleted += 1
                
    except Exception as e:
        logger.warning(f"Redis cleanup failed: {e}")
        redis_deleted = 0
    
    cleanup_results = {
        'database_xcom_deleted': deleted_count,
        'redis_xcom_deleted': redis_deleted,
        'cleanup_timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"XCom cleanup completed: {cleanup_results}")
    
    return cleanup_results

# Create task groups
payment_ingestion = create_payment_ingestion_group()
fraud_analysis = create_fraud_analysis_group()
settlement_processing = create_settlement_processing_group()

# Final tasks
final_report = generate_final_report()
xcom_cleanup = cleanup_xcom_data()

# DAG structure
payment_ingestion >> fraud_analysis >> settlement_processing >> final_report >> xcom_cleanup

"""
Mumbai Learning Notes:
1. Advanced XCom patterns for complex data passing
2. Custom XCom backends for large data storage (Redis)
3. Cross-task-group communication strategies
4. Data serialization and deserialization patterns
5. XCom cleanup and maintenance for production systems
6. Paytm payment processing business logic integration
7. Complex object handling with dataclasses
8. Performance optimization for large XCom data
9. Error handling in XCom data retrieval
10. Comprehensive reporting using collected XCom data

Production Considerations:
- Implement proper XCom data encryption for sensitive payment data
- Set up monitoring for XCom storage usage and cleanup
- Configure Redis clustering for XCom backend high availability
- Add proper error handling for XCom serialization failures
- Implement data retention policies for compliance
- Add comprehensive logging for XCom operations
- Set up proper access controls for XCom data
- Monitor performance impact of custom XCom backends
"""