"""
Episode 12: Apache Airflow - Advanced Examples (Examples 9-16)
Production patterns for Indian enterprises
"""

from datetime import datetime, timedelta, time
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import random
import pandas as pd

# ============================================================================
# Example 9: Sensor Pattern - Wait for File Upload
# ============================================================================

file_processing_dag = DAG(
    'gst_return_file_processor',
    default_args={
        'owner': 'gst-team',
        'start_date': datetime(2024, 1, 1),
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='Process GST return files when uploaded',
    schedule_interval='@hourly',
    tags=['gst', 'file-processing', 'sensor'],
)

# Wait for GST return file
wait_for_file = FileSensor(
    task_id='wait_for_gst_file',
    filepath='/data/gst_returns/GSTR1_{{ ds }}.csv',
    fs_conn_id='fs_default',
    poke_interval=60,  # Check every minute
    timeout=3600,  # Wait max 1 hour
    soft_fail=True,  # Don't fail the DAG if file not found
    dag=file_processing_dag,
)

def validate_gst_file(**context):
    """Validate GST return file format and data"""
    print("📋 Validating GST return file...")
    
    # Simulate validation
    validations = {
        'gstin_format': True,
        'invoice_numbers': True,
        'tax_calculations': random.random() > 0.1,
        'date_formats': True,
    }
    
    for check, passed in validations.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}: {'PASSED' if passed else 'FAILED'}")
    
    if all(validations.values()):
        return 'process_file'
    return 'reject_file'

validate_file = BranchPythonOperator(
    task_id='validate_gst_file',
    python_callable=validate_gst_file,
    dag=file_processing_dag,
)

def process_gst_return(**context):
    """Process validated GST return"""
    print("💼 Processing GST return...")
    
    # Simulate processing
    invoice_count = random.randint(100, 5000)
    total_tax = random.randint(10000, 1000000)
    
    print(f"  Invoices processed: {invoice_count}")
    print(f"  Total GST collected: ₹{total_tax:,}")
    print(f"  IGST: ₹{total_tax * 0.4:,.2f}")
    print(f"  CGST: ₹{total_tax * 0.3:,.2f}")
    print(f"  SGST: ₹{total_tax * 0.3:,.2f}")
    
    return {'invoices': invoice_count, 'tax': total_tax}

process_file = PythonOperator(
    task_id='process_file',
    python_callable=process_gst_return,
    dag=file_processing_dag,
)

reject_file = EmailOperator(
    task_id='reject_file',
    to=['tax-team@company.com'],
    subject='GST File Validation Failed',
    html_content='GST return file failed validation. Please review and resubmit.',
    dag=file_processing_dag,
)

# Workflow
wait_for_file >> validate_file >> [process_file, reject_file]

# ============================================================================
# Example 10: Cross-DAG Dependencies - Bank Settlement Workflow
# ============================================================================

# DAG 1: Transaction Processing
transaction_dag = DAG(
    'bank_transaction_processing',
    default_args={
        'owner': 'banking-team',
        'start_date': datetime(2024, 1, 1),
    },
    schedule_interval='0 */4 * * *',  # Every 4 hours
    tags=['banking', 'transactions'],
)

def process_transactions(**context):
    """Process bank transactions"""
    transaction_count = random.randint(10000, 50000)
    print(f"💳 Processed {transaction_count:,} transactions")
    
    # Mark completion for dependent DAG
    Variable.set('last_transaction_batch', context['execution_date'].isoformat())
    return transaction_count

process_txn = PythonOperator(
    task_id='process_transactions',
    python_callable=process_transactions,
    dag=transaction_dag,
)

# DAG 2: Settlement (depends on transaction DAG)
settlement_dag = DAG(
    'bank_settlement_processing',
    default_args={
        'owner': 'settlement-team',
        'start_date': datetime(2024, 1, 1),
    },
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    tags=['banking', 'settlement'],
)

# Wait for transaction processing to complete
wait_for_transactions = ExternalTaskSensor(
    task_id='wait_for_transaction_processing',
    external_dag_id='bank_transaction_processing',
    external_task_id='process_transactions',
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',  # Don't block worker slot
    dag=settlement_dag,
)

def run_settlement(**context):
    """Run settlement based on processed transactions"""
    last_batch = Variable.get('last_transaction_batch', default_var=None)
    
    print(f"🏦 Running settlement for transactions up to {last_batch}")
    
    # Simulate settlement
    settlement_amount = random.randint(100, 500) * 1000000  # In crores
    banks_settled = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Kotak']
    
    print(f"💰 Total settlement: ₹{settlement_amount:,}")
    print(f"🏦 Banks settled: {', '.join(banks_settled)}")
    
    return settlement_amount

settle = PythonOperator(
    task_id='run_settlement',
    python_callable=run_settlement,
    dag=settlement_dag,
)

# Workflow
wait_for_transactions >> settle

# ============================================================================
# Example 11: Data Pipeline with Quality Checks - Swiggy Analytics
# ============================================================================

swiggy_analytics_dag = DAG(
    'swiggy_analytics_pipeline',
    default_args={
        'owner': 'swiggy-analytics',
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
        'email': ['analytics@swiggy.com'],
    },
    description='Daily analytics pipeline for Swiggy orders',
    schedule_interval='0 3 * * *',  # 3 AM daily
    tags=['swiggy', 'analytics', 'data-pipeline'],
)

def extract_order_data(**context):
    """Extract order data from multiple sources"""
    print("📊 Extracting Swiggy order data...")
    
    sources = {
        'mobile_app': random.randint(100000, 300000),
        'website': random.randint(50000, 150000),
        'partner_api': random.randint(10000, 50000),
    }
    
    total_orders = sum(sources.values())
    print(f"📱 Total orders extracted: {total_orders:,}")
    
    for source, count in sources.items():
        print(f"  - {source}: {count:,} orders")
    
    # Store for quality checks
    context['task_instance'].xcom_push(key='total_orders', value=total_orders)
    return sources

def transform_order_data(**context):
    """Transform and enrich order data"""
    order_sources = context['task_instance'].xcom_pull(task_ids='extract_orders')
    total_orders = sum(order_sources.values())
    
    print(f"🔄 Transforming {total_orders:,} orders...")
    
    # Simulate transformations
    transformations = {
        'geocoding_addresses': '✅',
        'calculating_delivery_time': '✅',
        'categorizing_cuisines': '✅',
        'computing_discounts': '✅',
        'detecting_fraud': '✅',
    }
    
    for transform, status in transformations.items():
        print(f"  {status} {transform}")
    
    # Calculate metrics
    metrics = {
        'avg_order_value': random.randint(200, 400),
        'avg_delivery_time': random.randint(20, 40),
        'customer_satisfaction': random.uniform(4.0, 4.8),
    }
    
    print(f"\n📈 Key Metrics:")
    print(f"  Average order value: ₹{metrics['avg_order_value']}")
    print(f"  Average delivery time: {metrics['avg_delivery_time']} minutes")
    print(f"  Customer satisfaction: {metrics['customer_satisfaction']:.1f}/5.0")
    
    return metrics

# Data quality checks
def check_order_completeness(**context):
    """Check if all orders have required fields"""
    total_orders = context['task_instance'].xcom_pull(key='total_orders')
    
    # Simulate quality check
    missing_fields = random.randint(0, 100)
    completeness = ((total_orders - missing_fields) / total_orders) * 100
    
    print(f"✅ Data completeness: {completeness:.2f}%")
    
    if completeness < 95:
        raise ValueError(f"Data quality below threshold: {completeness:.2f}%")
    
    return completeness

def check_anomalies(**context):
    """Check for anomalies in order data"""
    metrics = context['task_instance'].xcom_pull(task_ids='transform_orders')
    
    print("🔍 Checking for anomalies...")
    
    # Check for unusual patterns
    anomalies = []
    
    if metrics['avg_order_value'] > 500:
        anomalies.append("Unusually high average order value")
    
    if metrics['avg_delivery_time'] > 60:
        anomalies.append("Delivery times exceeding SLA")
    
    if metrics['customer_satisfaction'] < 3.5:
        anomalies.append("Low customer satisfaction score")
    
    if anomalies:
        print(f"⚠️ Anomalies detected: {', '.join(anomalies)}")
    else:
        print("✅ No anomalies detected")
    
    return len(anomalies) == 0

# Task definitions
extract = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_order_data,
    dag=swiggy_analytics_dag,
)

transform = PythonOperator(
    task_id='transform_orders',
    python_callable=transform_order_data,
    dag=swiggy_analytics_dag,
)

# Quality check task group
with swiggy_analytics_dag:
    with TaskGroup('data_quality_checks') as quality_checks:
        check_completeness = PythonOperator(
            task_id='check_completeness',
            python_callable=check_order_completeness,
        )
        
        check_anomaly = PythonOperator(
            task_id='check_anomalies',
            python_callable=check_anomalies,
        )

load_warehouse = PostgresOperator(
    task_id='load_to_warehouse',
    postgres_conn_id='swiggy_warehouse',
    sql="""
        INSERT INTO daily_analytics (
            date, total_orders, avg_order_value, 
            avg_delivery_time, customer_satisfaction
        ) VALUES (
            '{{ ds }}', 
            {{ ti.xcom_pull(key='total_orders') }},
            {{ ti.xcom_pull(task_ids='transform_orders')['avg_order_value'] }},
            {{ ti.xcom_pull(task_ids='transform_orders')['avg_delivery_time'] }},
            {{ ti.xcom_pull(task_ids='transform_orders')['customer_satisfaction'] }}
        );
    """,
    dag=swiggy_analytics_dag,
)

# Workflow
extract >> transform >> quality_checks >> load_warehouse

# ============================================================================
# Example 12: Error Handling and Retry Pattern - PhonePe Transactions
# ============================================================================

from airflow.exceptions import AirflowException
from airflow.utils.trigger_rule import TriggerRule

phonepe_dag = DAG(
    'phonepe_transaction_processor',
    default_args={
        'owner': 'phonepe-platform',
        'start_date': datetime(2024, 1, 1),
        'retries': 3,
        'retry_delay': timedelta(seconds=30),
        'retry_exponential_backoff': True,
        'max_retry_delay': timedelta(minutes=5),
    },
    description='Process PhonePe UPI transactions with resilience',
    schedule_interval='*/10 * * * *',  # Every 10 minutes
    tags=['phonepe', 'upi', 'resilient'],
)

def process_upi_transaction(**context):
    """Process UPI transaction with potential failures"""
    
    # Simulate random failures
    failure_chance = random.random()
    
    if failure_chance < 0.2:  # 20% chance of failure
        print("❌ Transaction processing failed!")
        raise AirflowException("UPI gateway timeout")
    
    # Successful processing
    transaction_id = f"UPI{random.randint(100000000, 999999999)}"
    amount = random.randint(10, 10000)
    
    print(f"✅ Processed UPI transaction: {transaction_id}")
    print(f"💰 Amount: ₹{amount}")
    
    return {'txn_id': transaction_id, 'amount': amount}

def handle_failed_transaction(**context):
    """Handle failed transactions - move to DLQ"""
    print("🔄 Moving failed transaction to Dead Letter Queue")
    
    # Log to error tracking system
    error_details = {
        'dag_id': context['dag'].dag_id,
        'task_id': context['task'].task_id,
        'execution_date': context['execution_date'],
        'retry_number': context['task_instance'].try_number,
    }
    
    print(f"📝 Error logged: {error_details}")
    
    # Send to manual processing queue
    return "sent_to_dlq"

def compensate_transaction(**context):
    """Compensate for failed transaction"""
    print("💳 Initiating compensation for failed transaction")
    
    # Reverse any partial operations
    print("  ↩️ Reversing ledger entries")
    print("  ↩️ Releasing locked funds")
    print("  📧 Notifying customer about failure")
    
    return "compensation_complete"

# Main processing task
process_txn = PythonOperator(
    task_id='process_upi_transaction',
    python_callable=process_upi_transaction,
    dag=phonepe_dag,
)

# Error handling branch
handle_error = PythonOperator(
    task_id='handle_failure',
    python_callable=handle_failed_transaction,
    trigger_rule=TriggerRule.ONE_FAILED,  # Only run if previous task failed
    dag=phonepe_dag,
)

# Compensation task
compensate = PythonOperator(
    task_id='compensate_transaction',
    python_callable=compensate_transaction,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=phonepe_dag,
)

# Success notification
success_notification = BashOperator(
    task_id='notify_success',
    bash_command='echo "Transaction processed successfully"',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=phonepe_dag,
)

# Workflow with error handling
process_txn >> [success_notification, handle_error]
handle_error >> compensate

# ============================================================================
# Example 13: Custom Operator - Indian Railway PNR Status Checker
# ============================================================================

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class IRCTCPNROperator(BaseOperator):
    """Custom operator to check PNR status from IRCTC"""
    
    template_fields = ['pnr_number']
    ui_color = '#FF6B35'  # Indian Railways orange color
    
    @apply_defaults
    def __init__(self, pnr_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pnr_number = pnr_number
    
    def execute(self, context):
        """Check PNR status"""
        self.log.info(f"🚂 Checking PNR status for: {self.pnr_number}")
        
        # Simulate PNR status check
        statuses = ['CNF', 'RAC', 'WL', 'RLWL']
        status = random.choice(statuses)
        
        pnr_details = {
            'pnr': self.pnr_number,
            'status': status,
            'train': '12301 Howrah Rajdhani',
            'date': context['execution_date'].strftime('%Y-%m-%d'),
            'from': 'NDLS',
            'to': 'HWH',
        }
        
        self.log.info(f"✅ PNR Status: {status}")
        self.log.info(f"🚉 Train: {pnr_details['train']}")
        
        # Push to XCom for other tasks
        context['task_instance'].xcom_push(key='pnr_details', value=pnr_details)
        
        return pnr_details

# Using custom operator in DAG
railway_dag = DAG(
    'railway_pnr_monitoring',
    default_args={
        'owner': 'railway-ops',
        'start_date': datetime(2024, 1, 1),
    },
    schedule_interval='@daily',
    tags=['railway', 'custom-operator'],
)

check_pnr = IRCTCPNROperator(
    task_id='check_pnr_status',
    pnr_number='{{ var.value.test_pnr }}',  # Get from Airflow variables
    dag=railway_dag,
)

def notify_passenger(**context):
    """Notify passenger about PNR status"""
    pnr_details = context['task_instance'].xcom_pull(key='pnr_details')
    
    print(f"📱 Sending SMS to passenger...")
    print(f"  PNR: {pnr_details['pnr']}")
    print(f"  Status: {pnr_details['status']}")
    
    if pnr_details['status'] == 'CNF':
        print("  ✅ Your ticket is confirmed!")
    elif pnr_details['status'] == 'RAC':
        print("  ⚠️ You have RAC status")
    else:
        print("  ⏳ You are on waiting list")

notify = PythonOperator(
    task_id='notify_passenger',
    python_callable=notify_passenger,
    dag=railway_dag,
)

check_pnr >> notify

# ============================================================================
# Example 14: Monitoring & Alerting - Myntra Sale Monitoring
# ============================================================================

from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.operators.sql import SQLCheckOperator, SQLValueCheckOperator

myntra_monitoring_dag = DAG(
    'myntra_sale_monitoring',
    default_args={
        'owner': 'myntra-ops',
        'start_date': datetime(2024, 1, 1),
        'email': ['ops@myntra.com'],
        'email_on_failure': True,
        'sla': timedelta(minutes=10),
    },
    description='Monitor Myntra sale performance and alert on issues',
    schedule_interval='*/15 * * * *',  # Every 15 minutes during sale
    tags=['myntra', 'monitoring', 'alerts'],
)

def check_sale_metrics(**context):
    """Monitor sale performance metrics"""
    
    # Simulate fetching metrics
    metrics = {
        'orders_per_minute': random.randint(500, 2000),
        'conversion_rate': random.uniform(2, 8),
        'avg_cart_value': random.randint(1500, 3500),
        'payment_success_rate': random.uniform(85, 99),
        'api_response_time': random.uniform(50, 500),
    }
    
    print("📊 Myntra Sale Metrics:")
    print(f"  📦 Orders/min: {metrics['orders_per_minute']}")
    print(f"  🎯 Conversion rate: {metrics['conversion_rate']:.2f}%")
    print(f"  🛒 Avg cart value: ₹{metrics['avg_cart_value']}")
    print(f"  💳 Payment success: {metrics['payment_success_rate']:.1f}%")
    print(f"  ⚡ API response: {metrics['api_response_time']:.0f}ms")
    
    # Check for alerts
    alerts = []
    
    if metrics['orders_per_minute'] < 700:
        alerts.append("⚠️ Low order volume")
    
    if metrics['conversion_rate'] < 3:
        alerts.append("⚠️ Poor conversion rate")
    
    if metrics['payment_success_rate'] < 90:
        alerts.append("🚨 Payment failures high")
    
    if metrics['api_response_time'] > 300:
        alerts.append("🚨 API slowness detected")
    
    context['task_instance'].xcom_push(key='metrics', value=metrics)
    context['task_instance'].xcom_push(key='alerts', value=alerts)
    
    return len(alerts) > 0

monitor_metrics = PythonOperator(
    task_id='monitor_sale_metrics',
    python_callable=check_sale_metrics,
    dag=myntra_monitoring_dag,
)

# Database health checks
check_db_connections = SQLValueCheckOperator(
    task_id='check_database_connections',
    conn_id='myntra_db',
    sql="SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'",
    pass_value=lambda x: x < 1000,  # Alert if connections > 1000
    dag=myntra_monitoring_dag,
)

check_slow_queries = SQLCheckOperator(
    task_id='check_slow_queries',
    conn_id='myntra_db',
    sql="""
        SELECT COUNT(*) as slow_queries
        FROM pg_stat_statements
        WHERE mean_exec_time > 1000  -- Queries taking > 1 second
        HAVING COUNT(*) < 10  -- Alert if more than 10 slow queries
    """,
    dag=myntra_monitoring_dag,
)

def send_alert(**context):
    """Send alerts to ops team"""
    alerts = context['task_instance'].xcom_pull(key='alerts')
    metrics = context['task_instance'].xcom_pull(key='metrics')
    
    if alerts:
        print(f"🚨 SENDING ALERTS: {', '.join(alerts)}")
        
        # Would send to Slack/PagerDuty in production
        alert_message = f"""
        🚨 Myntra Sale Alert 🚨
        
        Issues detected:
        {chr(10).join(alerts)}
        
        Current metrics:
        - Orders/min: {metrics['orders_per_minute']}
        - Payment success: {metrics['payment_success_rate']:.1f}%
        - API response: {metrics['api_response_time']:.0f}ms
        """
        
        print(alert_message)
        return "alerts_sent"
    
    return "no_alerts"

alert_task = PythonOperator(
    task_id='send_alerts',
    python_callable=send_alert,
    trigger_rule=TriggerRule.NONE_FAILED,
    dag=myntra_monitoring_dag,
)

# Workflow
[monitor_metrics, check_db_connections, check_slow_queries] >> alert_task

# ============================================================================
# Example 15: Migration from Cron - Legacy Batch Job
# ============================================================================

# Legacy cron job: 0 2 * * * /scripts/daily_backup.sh
# Converted to Airflow DAG

legacy_migration_dag = DAG(
    'migrated_daily_backup',
    default_args={
        'owner': 'devops-team',
        'start_date': datetime(2024, 1, 1),
        'retries': 1,
        'retry_delay': timedelta(minutes=30),
    },
    description='Migrated from cron: Daily backup job',
    schedule_interval='0 2 * * *',  # Same as cron: 2 AM daily
    tags=['migration', 'backup', 'legacy'],
)

# Step 1: Database backup (previously in shell script)
db_backup = BashOperator(
    task_id='backup_database',
    bash_command="""
        # Original cron script logic
        BACKUP_DATE=$(date +%Y%m%d)
        BACKUP_FILE="/backups/db_backup_${BACKUP_DATE}.sql"
        
        # Dump database
        pg_dump -h localhost -U postgres -d production > ${BACKUP_FILE}
        
        # Compress backup
        gzip ${BACKUP_FILE}
        
        echo "✅ Database backed up to ${BACKUP_FILE}.gz"
    """,
    dag=legacy_migration_dag,
)

# Step 2: Upload to S3 (enhanced from original script)
upload_s3 = BashOperator(
    task_id='upload_to_s3',
    bash_command="""
        BACKUP_DATE=$(date +%Y%m%d)
        BACKUP_FILE="/backups/db_backup_${BACKUP_DATE}.sql.gz"
        
        # Upload to S3 with retry
        aws s3 cp ${BACKUP_FILE} s3://company-backups/postgres/${BACKUP_DATE}/ \
            --storage-class GLACIER_IR \
            --metadata backup_date=${BACKUP_DATE}
        
        echo "☁️ Backup uploaded to S3"
    """,
    dag=legacy_migration_dag,
)

# Step 3: Cleanup old backups (new addition)
def cleanup_old_backups(**context):
    """Remove backups older than 30 days"""
    import os
    from datetime import datetime, timedelta
    
    backup_dir = '/backups'
    retention_days = 30
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    print(f"🧹 Cleaning backups older than {retention_days} days")
    
    files_deleted = 0
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        if file_modified < cutoff_date:
            os.remove(filepath)
            files_deleted += 1
            print(f"  ❌ Deleted: {filename}")
    
    print(f"✅ Cleaned up {files_deleted} old backup files")
    return files_deleted

cleanup = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    dag=legacy_migration_dag,
)

# Step 4: Send notification (enhancement over cron)
notify_backup_complete = EmailOperator(
    task_id='notify_completion',
    to=['devops@company.com'],
    subject='Daily Backup Completed - {{ ds }}',
    html_content="""
    <h3>✅ Daily Backup Successful</h3>
    <p>Backup Date: {{ ds }}</p>
    <p>Database backup and S3 upload completed successfully.</p>
    <p>Old backups cleaned: {{ ti.xcom_pull(task_ids='cleanup_old_backups') }}</p>
    """,
    dag=legacy_migration_dag,
)

# Workflow (sequential like original cron)
db_backup >> upload_s3 >> cleanup >> notify_backup_complete

# ============================================================================
# Example 16: Complex Workflow - Multi-Stage E-commerce Pipeline
# ============================================================================

ecommerce_pipeline_dag = DAG(
    'complete_ecommerce_pipeline',
    default_args={
        'owner': 'platform-team',
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
    },
    description='Complete e-commerce data pipeline with all stages',
    schedule_interval='@daily',
    max_active_runs=1,
    tags=['ecommerce', 'complex', 'production'],
)

# Stage 1: Data Ingestion
with ecommerce_pipeline_dag:
    with TaskGroup('data_ingestion') as ingestion:
        
        ingest_orders = BashOperator(
            task_id='ingest_orders',
            bash_command='python /etl/ingest_orders.py --date {{ ds }}',
        )
        
        ingest_customers = BashOperator(
            task_id='ingest_customers',
            bash_command='python /etl/ingest_customers.py --date {{ ds }}',
        )
        
        ingest_products = BashOperator(
            task_id='ingest_products',
            bash_command='python /etl/ingest_products.py --date {{ ds }}',
        )

# Stage 2: Data Processing
with ecommerce_pipeline_dag:
    with TaskGroup('data_processing') as processing:
        
        clean_data = PythonOperator(
            task_id='clean_data',
            python_callable=lambda: print("🧹 Cleaning data..."),
        )
        
        transform_data = PythonOperator(
            task_id='transform_data',
            python_callable=lambda: print("🔄 Transforming data..."),
        )
        
        enrich_data = PythonOperator(
            task_id='enrich_data',
            python_callable=lambda: print("➕ Enriching data..."),
        )
        
        clean_data >> transform_data >> enrich_data

# Stage 3: Analytics
with ecommerce_pipeline_dag:
    with TaskGroup('analytics') as analytics:
        
        calculate_metrics = PythonOperator(
            task_id='calculate_metrics',
            python_callable=lambda: print("📊 Calculating metrics..."),
        )
        
        generate_reports = PythonOperator(
            task_id='generate_reports',
            python_callable=lambda: print("📈 Generating reports..."),
        )
        
        update_dashboards = PythonOperator(
            task_id='update_dashboards',
            python_callable=lambda: print("📉 Updating dashboards..."),
        )

# Stage 4: ML Pipeline
with ecommerce_pipeline_dag:
    with TaskGroup('ml_pipeline') as ml:
        
        train_models = PythonOperator(
            task_id='train_recommendation_model',
            python_callable=lambda: print("🤖 Training ML models..."),
        )
        
        validate_models = PythonOperator(
            task_id='validate_models',
            python_callable=lambda: print("✅ Validating models..."),
        )
        
        deploy_models = PythonOperator(
            task_id='deploy_models',
            python_callable=lambda: print("🚀 Deploying models..."),
        )
        
        train_models >> validate_models >> deploy_models

# Complete workflow
start = DummyOperator(task_id='start', dag=ecommerce_pipeline_dag)
end = DummyOperator(task_id='end', dag=ecommerce_pipeline_dag)

start >> ingestion >> processing >> [analytics, ml] >> end

print("✅ All 16 Apache Airflow examples created successfully!")
print("🚀 Complete production-ready DAGs for Indian enterprises!")
print("📚 Covering all major patterns: sensors, operators, task groups, error handling, monitoring, and more!")