#!/usr/bin/env python3
"""
Complex Sensor DAG for Flipkart Inventory Management
Focus: Multiple sensor types, conditional logic, dynamic task generation

Ye DAG Flipkart ke inventory management ke liye sensors ka use karta hai.
Mumbai ke stock market jaise real-time monitoring!

Production Ready: Yes
Testing Required: Yes
Dependencies: Apache Airflow, S3, HTTP APIs, Database
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.s3_key_sensor import S3KeySensor
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.sensors.postgres import PostgresSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sensors.time_sensor import TimeSensor
from airflow.sensors.date_time_sensor import DateTimeSensor
from airflow.utils.dates import days_ago
from airflow.utils.decorators import task
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.exceptions import AirflowSkipException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DAG configuration
default_args = {
    'owner': 'flipkart-inventory-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['inventory@flipkart.com', 'ops@flipkart.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(hours=6)
}

# Create DAG
dag = DAG(
    'flipkart_complex_inventory_sensors',
    default_args=default_args,
    description='Complex Sensor DAG for Flipkart Inventory Management',
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    tags=['flipkart', 'inventory', 'sensors', 'complex'],
    catchup=False,
    doc_md="""
    # Flipkart Complex Inventory Sensor DAG
    
    Ye DAG multiple types ke sensors use karta hai:
    1. File sensors for vendor data uploads
    2. HTTP sensors for API health checks
    3. Database sensors for data freshness
    4. Time sensors for business hour operations
    5. S3 sensors for large file processing
    
    Mumbai ke inventory management jaise efficient!
    """,
)

# Configuration variables
INVENTORY_THRESHOLD = int(Variable.get("inventory_threshold", default_var=100))
VENDOR_COUNT = int(Variable.get("active_vendor_count", default_var=50))
BUSINESS_HOURS_START = Variable.get("business_hours_start", default_var="09:00")
BUSINESS_HOURS_END = Variable.get("business_hours_end", default_var="21:00")

def create_file_sensor_group() -> TaskGroup:
    """Create task group for file sensors"""
    
    with TaskGroup(group_id='file_sensors', dag=dag) as group:
        
        # Sensor for vendor inventory files
        vendor_inventory_sensor = FileSensor(
            task_id='wait_for_vendor_inventory',
            filepath='/data/flipkart/inventory/vendor_stock_{{ ds }}.csv',
            poke_interval=60,  # Check every minute
            timeout=1800,  # 30 minutes timeout
            soft_fail=True,
            mode='poke'
        )
        
        # Sensor for product catalog updates
        product_catalog_sensor = FileSensor(
            task_id='wait_for_product_catalog',
            filepath='/data/flipkart/catalog/products_{{ ds }}.json',
            poke_interval=120,
            timeout=3600,  # 1 hour timeout
            soft_fail=False,
            mode='reschedule'  # Use reschedule mode for long waits
        )
        
        # Sensor for pricing data
        pricing_data_sensor = FileSensor(
            task_id='wait_for_pricing_data',
            filepath='/data/flipkart/pricing/price_updates_{{ ds }}.parquet',
            poke_interval=300,  # 5 minutes
            timeout=7200,  # 2 hours timeout
            soft_fail=True
        )
        
        # Process files after all are available
        @task
        def validate_file_integrity(**context):
            """Validate integrity of all received files"""
            import os
            import pandas as pd
            
            ds = context['ds']
            files_to_check = [
                f'/data/flipkart/inventory/vendor_stock_{ds}.csv',
                f'/data/flipkart/catalog/products_{ds}.json',
                f'/data/flipkart/pricing/price_updates_{ds}.parquet'
            ]
            
            validation_results = {}
            
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    validation_results[file_path] = {
                        'exists': True,
                        'size_mb': file_size / (1024 * 1024),
                        'valid': file_size > 1024  # At least 1KB
                    }
                    
                    # Additional validation based on file type
                    if file_path.endswith('.csv'):
                        try:
                            df = pd.read_csv(file_path, nrows=5)
                            validation_results[file_path]['columns'] = len(df.columns)
                            validation_results[file_path]['rows_sample'] = len(df)
                        except Exception as e:
                            validation_results[file_path]['error'] = str(e)
                            validation_results[file_path]['valid'] = False
                            
                else:
                    validation_results[file_path] = {
                        'exists': False,
                        'valid': False
                    }
            
            logger.info(f"File validation results: {validation_results}")
            
            # Check if all files are valid
            all_valid = all(result['valid'] for result in validation_results.values())
            
            if not all_valid:
                invalid_files = [f for f, r in validation_results.items() if not r['valid']]
                raise Exception(f"Invalid files detected: {invalid_files}")
            
            return validation_results
        
        file_validation = validate_file_integrity()
        
        # Set dependencies
        [vendor_inventory_sensor, product_catalog_sensor, pricing_data_sensor] >> file_validation
    
    return group

def create_http_sensor_group() -> TaskGroup:
    """Create task group for HTTP API sensors"""
    
    with TaskGroup(group_id='http_sensors', dag=dag) as group:
        
        # Check Flipkart API health
        flipkart_api_sensor = HttpSensor(
            task_id='check_flipkart_api_health',
            http_conn_id='flipkart_api',
            endpoint='health',
            poke_interval=30,
            timeout=300,
            soft_fail=False
        )
        
        # Check vendor API availability
        vendor_api_sensor = HttpSensor(
            task_id='check_vendor_apis',
            http_conn_id='vendor_integration_api',
            endpoint='status',
            poke_interval=60,
            timeout=600,
            soft_fail=True,
            request_params={'service': 'inventory'}
        )
        
        # Check payment gateway
        payment_gateway_sensor = HttpSensor(
            task_id='check_payment_gateway',
            http_conn_id='payment_gateway',
            endpoint='ping',
            poke_interval=45,
            timeout=300,
            headers={'Authorization': 'Bearer {{ var.value.payment_api_token }}'},
            soft_fail=True
        )
        
        # Check recommendation service
        recommendation_service_sensor = HttpSensor(
            task_id='check_recommendation_service',
            http_conn_id='ml_recommendation_service',
            endpoint='health',
            poke_interval=30,
            timeout=180,
            soft_fail=True
        )
        
        @task
        def evaluate_service_health(**context):
            """Evaluate overall service health"""
            
            # Get task instances to check their states
            task_instances = context['dag_run'].get_task_instances()
            sensor_states = {}
            
            sensor_tasks = [
                'http_sensors.check_flipkart_api_health',
                'http_sensors.check_vendor_apis',
                'http_sensors.check_payment_gateway',
                'http_sensors.check_recommendation_service'
            ]
            
            for ti in task_instances:
                if ti.task_id in [t.split('.')[-1] for t in sensor_tasks]:
                    sensor_states[ti.task_id] = ti.state
            
            # Calculate health score
            total_sensors = len(sensor_tasks)
            successful_sensors = sum(1 for state in sensor_states.values() if state == 'success')
            health_score = (successful_sensors / total_sensors) * 100
            
            logger.info(f"Service health score: {health_score}%")
            logger.info(f"Sensor states: {sensor_states}")
            
            # Set XCom value for downstream tasks
            context['task_instance'].xcom_push(key='health_score', value=health_score)
            context['task_instance'].xcom_push(key='sensor_states', value=sensor_states)
            
            return health_score
        
        health_evaluation = evaluate_service_health()
        
        # All HTTP sensors run in parallel, then health evaluation
        [flipkart_api_sensor, vendor_api_sensor, payment_gateway_sensor, 
         recommendation_service_sensor] >> health_evaluation
    
    return group

def create_database_sensor_group() -> TaskGroup:
    """Create task group for database sensors"""
    
    with TaskGroup(group_id='database_sensors', dag=dag) as group:
        
        # Check for fresh inventory data
        inventory_freshness_sensor = PostgresSensor(
            task_id='check_inventory_freshness',
            postgres_conn_id='flipkart_inventory_db',
            sql="""
                SELECT COUNT(*) 
                FROM inventory_updates 
                WHERE updated_at >= NOW() - INTERVAL '2 hours'
                HAVING COUNT(*) > 100
            """,
            poke_interval=120,
            timeout=1800,
            soft_fail=False
        )
        
        # Check for vendor data completeness
        vendor_data_sensor = PostgresSensor(
            task_id='check_vendor_data_completeness',
            postgres_conn_id='flipkart_inventory_db',
            sql=f"""
                SELECT COUNT(DISTINCT vendor_id) 
                FROM vendor_inventory 
                WHERE DATE(last_sync) = CURRENT_DATE
                HAVING COUNT(DISTINCT vendor_id) >= {VENDOR_COUNT}
            """,
            poke_interval=300,
            timeout=3600,
            soft_fail=True
        )
        
        # Check for low stock alerts
        low_stock_sensor = PostgresSensor(
            task_id='check_low_stock_items',
            postgres_conn_id='flipkart_inventory_db',
            sql=f"""
                SELECT COUNT(*) 
                FROM products p 
                JOIN inventory i ON p.product_id = i.product_id 
                WHERE i.available_stock <= {INVENTORY_THRESHOLD}
                AND p.is_active = true
                HAVING COUNT(*) > 0
            """,
            poke_interval=180,
            timeout=900,
            soft_fail=True
        )
        
        # Check data quality metrics
        data_quality_sensor = PostgresSensor(
            task_id='check_data_quality_metrics',
            postgres_conn_id='flipkart_analytics_db',
            sql="""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN price > 0 THEN 1 END) as products_with_price,
                    COUNT(CASE WHEN inventory_count >= 0 THEN 1 END) as products_with_inventory
                FROM product_analytics 
                WHERE DATE(updated_at) = CURRENT_DATE
                HAVING 
                    COUNT(*) > 10000 AND
                    COUNT(CASE WHEN price > 0 THEN 1 END) / COUNT(*) > 0.95 AND
                    COUNT(CASE WHEN inventory_count >= 0 THEN 1 END) / COUNT(*) > 0.98
            """,
            poke_interval=240,
            timeout=1200,
            soft_fail=False
        )
        
        @task
        def analyze_database_metrics(**context):
            """Analyze database metrics and generate insights"""
            
            hook = PostgresHook(postgres_conn_id='flipkart_inventory_db')
            
            # Get current inventory statistics
            inventory_stats = hook.get_first("""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN available_stock <= %s THEN 1 END) as low_stock_count,
                    AVG(available_stock) as avg_stock,
                    MAX(available_stock) as max_stock,
                    MIN(available_stock) as min_stock,
                    COUNT(CASE WHEN available_stock = 0 THEN 1 END) as out_of_stock_count
                FROM inventory 
                WHERE is_active = true
            """, parameters=(INVENTORY_THRESHOLD,))
            
            # Get vendor performance
            vendor_stats = hook.get_first("""
                SELECT 
                    COUNT(DISTINCT vendor_id) as active_vendors,
                    AVG(sync_frequency_hours) as avg_sync_frequency,
                    COUNT(CASE WHEN last_sync >= NOW() - INTERVAL '24 hours' THEN 1 END) as vendors_synced_today
                FROM vendor_inventory 
            """)
            
            # Get category distribution
            category_stats = hook.get_records("""
                SELECT 
                    category,
                    COUNT(*) as product_count,
                    AVG(available_stock) as avg_stock,
                    COUNT(CASE WHEN available_stock <= %s THEN 1 END) as low_stock_count
                FROM products p 
                JOIN inventory i ON p.product_id = i.product_id 
                WHERE p.is_active = true
                GROUP BY category 
                ORDER BY product_count DESC 
                LIMIT 10
            """, parameters=(INVENTORY_THRESHOLD,))
            
            analysis_result = {
                'inventory_stats': {
                    'total_products': inventory_stats[0],
                    'low_stock_count': inventory_stats[1],
                    'avg_stock': float(inventory_stats[2]) if inventory_stats[2] else 0,
                    'max_stock': inventory_stats[3],
                    'min_stock': inventory_stats[4],
                    'out_of_stock_count': inventory_stats[5],
                    'low_stock_percentage': (inventory_stats[1] / inventory_stats[0] * 100) if inventory_stats[0] > 0 else 0
                },
                'vendor_stats': {
                    'active_vendors': vendor_stats[0],
                    'avg_sync_frequency': float(vendor_stats[1]) if vendor_stats[1] else 0,
                    'vendors_synced_today': vendor_stats[2],
                    'sync_compliance': (vendor_stats[2] / vendor_stats[0] * 100) if vendor_stats[0] > 0 else 0
                },
                'category_stats': [
                    {
                        'category': row[0],
                        'product_count': row[1],
                        'avg_stock': float(row[2]) if row[2] else 0,
                        'low_stock_count': row[3],
                        'low_stock_percentage': (row[3] / row[1] * 100) if row[1] > 0 else 0
                    } for row in category_stats
                ]
            }
            
            logger.info(f"Database analysis completed: {analysis_result}")
            
            # Push to XCom for downstream tasks
            context['task_instance'].xcom_push(key='database_analysis', value=analysis_result)
            
            return analysis_result
        
        database_analysis = analyze_database_metrics()
        
        # Set dependencies
        [inventory_freshness_sensor, vendor_data_sensor, 
         low_stock_sensor, data_quality_sensor] >> database_analysis
    
    return group

def create_time_sensor_group() -> TaskGroup:
    """Create task group for time-based sensors"""
    
    with TaskGroup(group_id='time_sensors', dag=dag) as group:
        
        # Business hours sensor
        business_hours_sensor = TimeSensor(
            task_id='wait_for_business_hours',
            target_time=datetime.strptime(BUSINESS_HOURS_START, '%H:%M').time(),
            poke_interval=300,  # 5 minutes
            timeout=3600,
            soft_fail=True
        )
        
        # Peak hours sensor (lunch time - high traffic)
        peak_hours_sensor = TimeSensor(
            task_id='wait_for_peak_hours',
            target_time=datetime.strptime('12:00', '%H:%M').time(),
            poke_interval=600,  # 10 minutes
            timeout=7200,
            soft_fail=True
        )
        
        # End of business hours sensor
        end_business_sensor = TimeSensor(
            task_id='wait_for_end_business_hours', 
            target_time=datetime.strptime(BUSINESS_HOURS_END, '%H:%M').time(),
            poke_interval=300,
            timeout=1800,
            soft_fail=True
        )
        
        # Specific datetime sensor for scheduled maintenance
        @task
        def check_maintenance_window(**context):
            """Check if we're in maintenance window"""
            current_time = datetime.now()
            
            # Define maintenance windows (IST)
            maintenance_windows = [
                ('02:00', '04:00'),  # Night maintenance
                ('14:30', '15:00'),  # Afternoon maintenance
            ]
            
            current_time_str = current_time.strftime('%H:%M')
            
            for start, end in maintenance_windows:
                if start <= current_time_str <= end:
                    logger.info(f"Currently in maintenance window: {start} - {end}")
                    context['task_instance'].xcom_push(key='in_maintenance', value=True)
                    context['task_instance'].xcom_push(key='maintenance_window', value=f"{start}-{end}")
                    return True
            
            logger.info("Not in maintenance window")
            context['task_instance'].xcom_push(key='in_maintenance', value=False)
            return False
        
        maintenance_check = check_maintenance_window()
        
        @task
        def determine_processing_strategy(**context):
            """Determine processing strategy based on time"""
            current_hour = datetime.now().hour
            
            # Get maintenance status
            in_maintenance = context['task_instance'].xcom_pull(
                task_ids='time_sensors.check_maintenance_window',
                key='in_maintenance'
            )
            
            if in_maintenance:
                strategy = 'maintenance_mode'
            elif 9 <= current_hour <= 21:  # Business hours
                if 12 <= current_hour <= 14 or 19 <= current_hour <= 21:  # Peak hours
                    strategy = 'peak_processing'
                else:
                    strategy = 'normal_processing'
            else:  # Off hours
                strategy = 'batch_processing'
            
            logger.info(f"Selected processing strategy: {strategy}")
            
            context['task_instance'].xcom_push(key='processing_strategy', value=strategy)
            return strategy
        
        processing_strategy = determine_processing_strategy()
        
        # Dependencies
        [business_hours_sensor, peak_hours_sensor, end_business_sensor, 
         maintenance_check] >> processing_strategy
    
    return group

def create_s3_sensor_group() -> TaskGroup:
    """Create task group for S3 sensors"""
    
    with TaskGroup(group_id='s3_sensors', dag=dag) as group:
        
        # Large vendor data files
        vendor_bulk_data_sensor = S3KeySensor(
            task_id='wait_for_vendor_bulk_data',
            bucket_name='flipkart-vendor-data',
            bucket_key='bulk-updates/{{ ds }}/vendor_inventory.parquet',
            aws_conn_id='aws_default',
            poke_interval=300,
            timeout=3600,
            soft_fail=True
        )
        
        # Product images
        product_images_sensor = S3KeySensor(
            task_id='wait_for_product_images',
            bucket_name='flipkart-product-assets',
            bucket_key='images/{{ ds }}/batch_upload_complete.flag',
            aws_conn_id='aws_default',
            poke_interval=600,
            timeout=7200,
            soft_fail=True
        )
        
        # Analytics reports
        analytics_reports_sensor = S3KeySensor(
            task_id='wait_for_analytics_reports',
            bucket_name='flipkart-analytics',
            bucket_key='daily-reports/{{ ds }}/inventory_report.json',
            aws_conn_id='aws_default',
            poke_interval=180,
            timeout=1800,
            soft_fail=False
        )
        
        @task
        def validate_s3_data(**context):
            """Validate S3 data completeness and integrity"""
            
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client('s3')
            ds = context['ds']
            
            validation_results = {}
            
            # Check files
            files_to_check = [
                {
                    'bucket': 'flipkart-vendor-data',
                    'key': f'bulk-updates/{ds}/vendor_inventory.parquet',
                    'min_size': 10 * 1024 * 1024  # 10MB minimum
                },
                {
                    'bucket': 'flipkart-product-assets',
                    'key': f'images/{ds}/batch_upload_complete.flag',
                    'min_size': 1
                },
                {
                    'bucket': 'flipkart-analytics',
                    'key': f'daily-reports/{ds}/inventory_report.json',
                    'min_size': 1024  # 1KB minimum
                }
            ]
            
            for file_info in files_to_check:
                try:
                    response = s3_client.head_object(
                        Bucket=file_info['bucket'],
                        Key=file_info['key']
                    )
                    
                    file_size = response['ContentLength']
                    validation_results[file_info['key']] = {
                        'exists': True,
                        'size_bytes': file_size,
                        'size_mb': file_size / (1024 * 1024),
                        'valid': file_size >= file_info['min_size'],
                        'last_modified': response['LastModified'].isoformat()
                    }
                    
                except ClientError as e:
                    validation_results[file_info['key']] = {
                        'exists': False,
                        'valid': False,
                        'error': str(e)
                    }
            
            logger.info(f"S3 validation results: {validation_results}")
            
            # Check overall validity
            all_valid = all(result.get('valid', False) for result in validation_results.values())
            
            context['task_instance'].xcom_push(key='s3_validation', value=validation_results)
            context['task_instance'].xcom_push(key='all_s3_valid', value=all_valid)
            
            return validation_results
        
        s3_validation = validate_s3_data()
        
        # Dependencies
        [vendor_bulk_data_sensor, product_images_sensor, analytics_reports_sensor] >> s3_validation
    
    return group

# Branching operator for conditional execution
@task.branch
def decide_processing_path(**context):
    """Decide processing path based on sensor results"""
    
    # Get health score from HTTP sensors
    health_score = context['task_instance'].xcom_pull(
        task_ids='http_sensors.evaluate_service_health',
        key='health_score'
    )
    
    # Get processing strategy from time sensors
    processing_strategy = context['task_instance'].xcom_pull(
        task_ids='time_sensors.determine_processing_strategy',
        key='processing_strategy'
    )
    
    # Get S3 validation results
    all_s3_valid = context['task_instance'].xcom_pull(
        task_ids='s3_sensors.validate_s3_data',
        key='all_s3_valid'
    )
    
    logger.info(f"Decision factors - Health: {health_score}%, Strategy: {processing_strategy}, S3 Valid: {all_s3_valid}")
    
    # Decision logic
    if health_score is None or health_score < 70:
        return 'degraded_processing'
    elif processing_strategy == 'maintenance_mode':
        return 'maintenance_processing'
    elif processing_strategy == 'peak_processing' and all_s3_valid:
        return 'high_priority_processing'
    elif all_s3_valid:
        return 'normal_processing'
    else:
        return 'partial_processing'

# Processing task groups based on decision
normal_processing = DummyOperator(
    task_id='normal_processing',
    dag=dag
)

high_priority_processing = DummyOperator(
    task_id='high_priority_processing',
    dag=dag
)

degraded_processing = DummyOperator(
    task_id='degraded_processing',
    dag=dag
)

maintenance_processing = DummyOperator(
    task_id='maintenance_processing',
    dag=dag
)

partial_processing = DummyOperator(
    task_id='partial_processing',
    dag=dag
)

# Final reporting task
@task(trigger_rule=TriggerRule.NONE_FAILED_OR_SKIPPED)
def generate_sensor_report(**context):
    """Generate comprehensive sensor execution report"""
    
    # Collect all sensor results
    sensor_results = {}
    
    # Get results from different sensor groups
    try:
        sensor_results['health_score'] = context['task_instance'].xcom_pull(
            task_ids='http_sensors.evaluate_service_health', key='health_score'
        )
        sensor_results['processing_strategy'] = context['task_instance'].xcom_pull(
            task_ids='time_sensors.determine_processing_strategy', key='processing_strategy'
        )
        sensor_results['database_analysis'] = context['task_instance'].xcom_pull(
            task_ids='database_sensors.analyze_database_metrics', key='database_analysis'
        )
        sensor_results['s3_validation'] = context['task_instance'].xcom_pull(
            task_ids='s3_sensors.validate_s3_data', key='s3_validation'
        )
    except Exception as e:
        logger.error(f"Error collecting sensor results: {e}")
        sensor_results['error'] = str(e)
    
    # Generate report
    report = f"""
    # Flipkart Inventory Sensor Execution Report
    
    **Execution Date:** {context['ds']}
    **Execution Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ## Service Health
    - Overall Health Score: {sensor_results.get('health_score', 'N/A')}%
    
    ## Processing Strategy
    - Selected Strategy: {sensor_results.get('processing_strategy', 'N/A')}
    
    ## Database Analysis
    {sensor_results.get('database_analysis', 'No database analysis available')}
    
    ## S3 Validation
    {sensor_results.get('s3_validation', 'No S3 validation available')}
    
    ## Recommendations
    - Monitor low stock items regularly
    - Ensure vendor sync compliance
    - Validate data quality metrics daily
    """
    
    logger.info("Sensor execution report generated")
    logger.info(report)
    
    return report

final_report = generate_sensor_report()

# Create task groups
file_sensors = create_file_sensor_group()
http_sensors = create_http_sensor_group()
database_sensors = create_database_sensor_group()
time_sensors = create_time_sensor_group()
s3_sensors = create_s3_sensor_group()

# Decision point
processing_decision = decide_processing_path()

# DAG structure
[file_sensors, http_sensors, database_sensors, time_sensors, s3_sensors] >> processing_decision

processing_decision >> [normal_processing, high_priority_processing, degraded_processing, 
                       maintenance_processing, partial_processing]

[normal_processing, high_priority_processing, degraded_processing, 
 maintenance_processing, partial_processing] >> final_report

"""
Mumbai Learning Notes:
1. Complex sensor orchestration with multiple sensor types
2. File, HTTP, Database, Time, and S3 sensors integration
3. Conditional branching based on sensor results
4. Task groups for organized sensor management
5. Real-time health monitoring and decision making
6. Indian business context with Flipkart inventory management
7. Error handling and soft failures for resilience
8. Comprehensive reporting and monitoring
9. Dynamic task generation based on conditions
10. Production-ready sensor patterns for enterprise ETL

Production Considerations:
- Configure appropriate timeouts based on business SLAs
- Set up proper alerting for sensor failures
- Monitor sensor performance and adjust poke intervals
- Implement circuit breakers for external dependencies
- Add comprehensive logging for troubleshooting
- Set up proper connection management for external systems
- Configure retry logic based on failure patterns
"""