#!/usr/bin/env python3
"""
Advanced Airflow DAG for IRCTC Data Pipeline
Focus: Complex DAG patterns, dynamic task generation, error handling

Ye Airflow DAG IRCTC ke complex data pipeline ke liye hai.
Mumbai local train ke schedule jaise precise aur reliable!

Production Ready: Yes
Dependencies: Apache Airflow, PostgreSQL, Redis, Spark
Indian Context: IRCTC booking, train schedules, passenger data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import logging
from dataclasses import dataclass

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.s3_key_sensor import S3KeySensor
from airflow.providers.spark.operators.spark_submit import SparkSubmitOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.utils.decorators import task
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IRCTCPipelineConfig:
    """Configuration for IRCTC data pipeline"""
    database_conn_id: str = "irctc_postgres"
    api_conn_id: str = "irctc_api"
    spark_conn_id: str = "spark_default"
    email_list: List[str] = None
    data_sources: List[str] = None
    batch_size: int = 10000
    max_retries: int = 3
    retry_delay: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.email_list is None:
            self.email_list = ["data-team@irctc.co.in", "alerts@irctc.co.in"]
        if self.data_sources is None:
            self.data_sources = ["bookings", "trains", "stations", "passengers", "payments"]

# DAG default arguments - Mumbai mein sab kuch time pe hona chahiye!
default_args = {
    'owner': 'IRCTC-Data-Team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['data-team@irctc.co.in'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(hours=3)
}

# Create the DAG
dag = DAG(
    'irctc_advanced_data_pipeline',
    default_args=default_args,
    description='Advanced IRCTC Data Pipeline - Mumbai Local Train Scale!',
    schedule_interval='0 2 * * *',  # Daily at 2 AM IST
    tags=['irctc', 'railway', 'etl', 'mumbai', 'production'],
    catchup=False,
    doc_md="""
    # IRCTC Advanced Data Pipeline
    
    Ye pipeline IRCTC ke saare data sources ko process karta hai:
    1. Booking data from multiple sources
    2. Train schedules and real-time updates  
    3. Station information and capacity
    4. Passenger analytics and preferences
    5. Payment and refund processing
    
    Mumbai local train jaise reliable aur efficient!
    """,
)

# Initialize configuration
config = IRCTCPipelineConfig()

# Task Groups for better organization
def create_data_extraction_tasks() -> TaskGroup:
    """Create data extraction task group"""
    
    with TaskGroup(group_id='data_extraction', dag=dag) as extraction_group:
        
        # Check data freshness
        @task
        def check_data_freshness(**context):
            """Check if new data is available - Mumbai local frequency check!"""
            hook = PostgresHook(postgres_conn_id=config.database_conn_id)
            
            # Check last update timestamp for each data source
            freshness_results = {}
            for source in config.data_sources:
                query = f"""
                SELECT 
                    MAX(updated_at) as last_update,
                    COUNT(*) as record_count,
                    EXTRACT(EPOCH FROM (NOW() - MAX(updated_at)))/3600 as hours_since_update
                FROM {source}_raw 
                WHERE DATE(updated_at) = CURRENT_DATE
                """
                
                result = hook.get_first(query)
                freshness_results[source] = {
                    'last_update': result[0],
                    'record_count': result[1],
                    'hours_since_update': result[2]
                }
                
                logger.info(f"Data source {source}: {result[1]} records, {result[2]:.2f} hours old")
            
            # Push results to XCom for downstream tasks
            context['task_instance'].xcom_push(key='freshness_results', value=freshness_results)
            return freshness_results
        
        # Extract booking data - Big volume like Big Billion Day!
        extract_bookings = PythonOperator(
            task_id='extract_booking_data',
            python_callable=extract_irctc_bookings,
            op_kwargs={'batch_size': config.batch_size},
        )
        
        # Extract train schedules
        extract_trains = PythonOperator(
            task_id='extract_train_schedules',
            python_callable=extract_train_schedules,
        )
        
        # Extract station data
        extract_stations = PythonOperator(
            task_id='extract_station_data',
            python_callable=extract_station_data,
        )
        
        # Extract passenger data
        extract_passengers = PythonOperator(
            task_id='extract_passenger_data',
            python_callable=extract_passenger_data,
        )
        
        # Extract payment data
        extract_payments = PythonOperator(
            task_id='extract_payment_data',
            python_callable=extract_payment_data,
        )
        
        # Wait for all extractions to complete
        extraction_complete = DummyOperator(
            task_id='extraction_complete',
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # Set task dependencies
        check_data_freshness() >> [extract_bookings, extract_trains, extract_stations, 
                                   extract_passengers, extract_payments] >> extraction_complete
    
    return extraction_group

def create_data_transformation_tasks() -> TaskGroup:
    """Create data transformation task group"""
    
    with TaskGroup(group_id='data_transformation', dag=dag) as transformation_group:
        
        # Data quality checks - Mumbai quality control!
        data_quality_check = PythonOperator(
            task_id='data_quality_check',
            python_callable=run_data_quality_checks,
        )
        
        # Transform booking data
        transform_bookings = SparkSubmitOperator(
            task_id='transform_booking_data',
            application='/opt/spark/apps/transform_bookings.py',
            conn_id=config.spark_conn_id,
            application_args=[
                '--input-path', '/data/raw/bookings',
                '--output-path', '/data/transformed/bookings',
                '--date', '{{ ds }}'
            ],
            conf={
                'spark.sql.adaptive.enabled': 'true',
                'spark.sql.adaptive.coalescePartitions.enabled': 'true',
                'spark.serializer': 'org.apache.spark.serializer.KryoSerializer'
            }
        )
        
        # Generate passenger analytics
        passenger_analytics = PythonOperator(
            task_id='generate_passenger_analytics',
            python_callable=generate_passenger_analytics,
        )
        
        # Calculate route optimization
        route_optimization = PythonOperator(
            task_id='calculate_route_optimization',
            python_callable=calculate_route_optimization,
        )
        
        # Revenue analysis
        revenue_analysis = PythonOperator(
            task_id='revenue_analysis',
            python_callable=perform_revenue_analysis,
        )
        
        # Capacity planning
        capacity_planning = PythonOperator(
            task_id='capacity_planning',
            python_callable=capacity_planning_analysis,
        )
        
        # Transformation complete marker
        transformation_complete = DummyOperator(
            task_id='transformation_complete',
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # Set dependencies
        data_quality_check >> [transform_bookings, passenger_analytics, 
                              route_optimization, revenue_analysis, 
                              capacity_planning] >> transformation_complete
    
    return transformation_group

def create_data_loading_tasks() -> TaskGroup:
    """Create data loading task group"""
    
    with TaskGroup(group_id='data_loading', dag=dag) as loading_group:
        
        # Load to data warehouse
        load_to_warehouse = PostgresOperator(
            task_id='load_to_data_warehouse',
            postgres_conn_id=config.database_conn_id,
            sql="""
            INSERT INTO irctc_analytics.daily_summary 
            SELECT * FROM irctc_staging.processed_data 
            WHERE processing_date = '{{ ds }}'
            ON CONFLICT (date, metric_type) DO UPDATE SET
                metric_value = EXCLUDED.metric_value,
                updated_at = CURRENT_TIMESTAMP;
            """
        )
        
        # Update materialized views
        refresh_views = PostgresOperator(
            task_id='refresh_materialized_views',
            postgres_conn_id=config.database_conn_id,
            sql="""
            REFRESH MATERIALIZED VIEW CONCURRENTLY irctc_analytics.passenger_trends;
            REFRESH MATERIALIZED VIEW CONCURRENTLY irctc_analytics.route_performance;
            REFRESH MATERIALIZED VIEW CONCURRENTLY irctc_analytics.revenue_metrics;
            """
        )
        
        # Generate reports
        generate_reports = PythonOperator(
            task_id='generate_daily_reports',
            python_callable=generate_daily_reports,
        )
        
        # Send notifications
        send_success_notification = EmailOperator(
            task_id='send_success_notification',
            to=config.email_list,
            subject='IRCTC Data Pipeline - Daily Processing Complete',
            html_content="""
            <h3>IRCTC Data Pipeline Success</h3>
            <p>Daily data processing completed successfully for {{ ds }}</p>
            <ul>
                <li>Processing Date: {{ ds }}</li>
                <li>Execution Time: {{ ts }}</li>
                <li>Duration: {{ macros.timedelta(seconds=ti.duration) }}</li>
            </ul>
            """,
        )
        
        # Loading complete
        loading_complete = DummyOperator(
            task_id='loading_complete',
            trigger_rule=TriggerRule.ALL_SUCCESS
        )
        
        # Set dependencies
        [load_to_warehouse, refresh_views] >> generate_reports >> send_success_notification >> loading_complete
    
    return loading_group

def create_error_handling_tasks() -> TaskGroup:
    """Create error handling and monitoring task group"""
    
    with TaskGroup(group_id='error_handling', dag=dag) as error_group:
        
        # Check for failures
        @task
        def check_pipeline_health(**context):
            """Check overall pipeline health"""
            failed_tasks = []
            dag_run = context['dag_run']
            
            for task_instance in dag_run.get_task_instances():
                if task_instance.state == 'failed':
                    failed_tasks.append(task_instance.task_id)
            
            if failed_tasks:
                logger.error(f"Failed tasks: {failed_tasks}")
                return 'send_failure_alert'
            else:
                logger.info("All tasks completed successfully")
                return 'pipeline_success'
        
        # Send failure alert
        send_failure_alert = EmailOperator(
            task_id='send_failure_alert',
            to=config.email_list + ['engineering-oncall@irctc.co.in'],
            subject='URGENT: IRCTC Data Pipeline Failed',
            html_content="""
            <h3>IRCTC Data Pipeline Failure Alert</h3>
            <p><strong>URGENT:</strong> Data pipeline failed for {{ ds }}</p>
            <ul>
                <li>DAG ID: {{ dag.dag_id }}</li>
                <li>Execution Date: {{ ds }}</li>
                <li>Failed Time: {{ ts }}</li>
                <li>Log URL: {{ ti.log_url }}</li>
            </ul>
            <p>Please check logs and take immediate action.</p>
            """,
            trigger_rule=TriggerRule.ONE_FAILED
        )
        
        # Success marker
        pipeline_success = DummyOperator(
            task_id='pipeline_success'
        )
        
        # Health check branching
        health_check = BranchPythonOperator(
            task_id='check_pipeline_health',
            python_callable=check_pipeline_health,
        )
        
        health_check >> [send_failure_alert, pipeline_success]
    
    return error_group

# Python functions for tasks
def extract_irctc_bookings(**context):
    """Extract IRCTC booking data - Mumbai ke rush hour jaise volume!"""
    batch_size = context.get('batch_size', 10000)
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    # Extract bookings in batches
    query = f"""
    SELECT 
        booking_id, user_id, train_no, from_station, to_station,
        journey_date, booking_date, passenger_count, total_fare,
        payment_status, booking_status, class_type,
        quota_type, tatkal_flag, senior_citizen_flag
    FROM bookings 
    WHERE DATE(booking_date) = '{{{{ ds }}}}'
    AND booking_status IN ('CONFIRMED', 'WAITING', 'RAC')
    ORDER BY booking_date
    LIMIT {batch_size}
    """
    
    results = hook.get_records(query)
    
    # Store in staging area
    staging_query = """
    INSERT INTO staging.booking_data VALUES %s
    ON CONFLICT (booking_id) DO UPDATE SET
        booking_status = EXCLUDED.booking_status,
        updated_at = CURRENT_TIMESTAMP
    """
    
    hook.insert_rows(table='staging.booking_data', rows=results)
    
    logger.info(f"Extracted {len(results)} booking records")
    return len(results)

def extract_train_schedules(**context):
    """Extract train schedule data"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    query = """
    SELECT 
        train_no, train_name, from_station, to_station,
        departure_time, arrival_time, running_days,
        distance_km, duration_minutes, train_type,
        zone, rake_sharing, pantry_car
    FROM train_schedules 
    WHERE status = 'ACTIVE'
    """
    
    results = hook.get_records(query)
    logger.info(f"Extracted {len(results)} train schedule records")
    return results

def extract_station_data(**context):
    """Extract station data with capacity information"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    query = """
    SELECT 
        station_code, station_name, zone, division,
        state, platforms, electrified,
        longitude, latitude, altitude,
        yearly_passenger_count, peak_hour_capacity
    FROM stations 
    WHERE status = 'OPERATIONAL'
    """
    
    results = hook.get_records(query)
    logger.info(f"Extracted {len(results)} station records")
    return results

def extract_passenger_data(**context):
    """Extract passenger analytics data"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    query = """
    SELECT 
        user_id, age_group, gender, preferred_class,
        booking_frequency, average_journey_distance,
        preferred_routes, payment_preference,
        cancellation_rate, no_show_rate
    FROM passenger_analytics 
    WHERE last_updated >= '{{ ds }}'
    """
    
    results = hook.get_records(query)
    logger.info(f"Extracted {len(results)} passenger analytics records")
    return results

def extract_payment_data(**context):
    """Extract payment and refund data"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    query = """
    SELECT 
        payment_id, booking_id, amount, payment_method,
        payment_status, transaction_id, gateway_response,
        payment_date, refund_amount, refund_status,
        processing_fee, convenience_fee
    FROM payments 
    WHERE DATE(payment_date) = '{{ ds }}'
    """
    
    results = hook.get_records(query)
    logger.info(f"Extracted {len(results)} payment records")
    return results

def run_data_quality_checks(**context):
    """Run comprehensive data quality checks - Mumbai ki quality standards!"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    quality_checks = {
        'booking_completeness': """
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN user_id IS NULL THEN 1 END) as missing_users,
                COUNT(CASE WHEN train_no IS NULL THEN 1 END) as missing_trains,
                COUNT(CASE WHEN total_fare IS NULL OR total_fare <= 0 THEN 1 END) as invalid_fares
            FROM staging.booking_data
        """,
        'payment_consistency': """
            SELECT 
                COUNT(*) as total_payments,
                COUNT(CASE WHEN payment_status = 'SUCCESS' AND refund_amount > 0 THEN 1 END) as inconsistent_refunds,
                AVG(amount) as avg_payment_amount,
                COUNT(CASE WHEN amount > 50000 THEN 1 END) as high_value_payments
            FROM staging.payment_data
        """,
        'schedule_validity': """
            SELECT 
                COUNT(*) as total_schedules,
                COUNT(CASE WHEN departure_time >= arrival_time THEN 1 END) as invalid_times,
                COUNT(CASE WHEN distance_km <= 0 THEN 1 END) as invalid_distances
            FROM staging.schedule_data
        """
    }
    
    quality_results = {}
    for check_name, query in quality_checks.items():
        result = hook.get_first(query)
        quality_results[check_name] = result
        logger.info(f"Quality check {check_name}: {result}")
    
    # Push results for monitoring
    context['task_instance'].xcom_push(key='quality_results', value=quality_results)
    
    # Fail if critical quality issues found
    if quality_results['booking_completeness'][1] > 100:  # More than 100 missing users
        raise ValueError("Too many bookings with missing user information!")
    
    return quality_results

def generate_passenger_analytics(**context):
    """Generate passenger analytics - Mumbai commuter insights!"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    # Passenger segmentation analysis
    analytics_queries = {
        'frequent_travelers': """
            INSERT INTO analytics.passenger_segments
            SELECT 
                'frequent_travelers' as segment,
                user_id, booking_frequency, preferred_routes,
                AVG(total_fare) as avg_spend,
                COUNT(*) as trip_count
            FROM staging.booking_data 
            WHERE booking_frequency >= 20
            GROUP BY user_id, booking_frequency, preferred_routes
        """,
        'route_popularity': """
            INSERT INTO analytics.route_metrics
            SELECT 
                CONCAT(from_station, '-', to_station) as route,
                COUNT(*) as booking_count,
                AVG(total_fare) as avg_fare,
                COUNT(DISTINCT user_id) as unique_passengers,
                COUNT(CASE WHEN tatkal_flag = true THEN 1 END) as tatkal_bookings
            FROM staging.booking_data
            GROUP BY from_station, to_station
        """,
        'class_preference': """
            INSERT INTO analytics.class_preferences
            SELECT 
                class_type,
                COUNT(*) as booking_count,
                AVG(total_fare) as avg_fare,
                AVG(passenger_count) as avg_passengers,
                COUNT(CASE WHEN senior_citizen_flag = true THEN 1 END) as senior_citizen_bookings
            FROM staging.booking_data
            GROUP BY class_type
        """
    }
    
    for analytics_name, query in analytics_queries.items():
        hook.run(query)
        logger.info(f"Generated analytics: {analytics_name}")
    
    return "Passenger analytics generated successfully"

def calculate_route_optimization(**context):
    """Calculate route optimization metrics"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    # Route optimization calculations
    query = """
    INSERT INTO analytics.route_optimization
    SELECT 
        route,
        current_capacity,
        demand_forecast,
        revenue_potential,
        CASE 
            WHEN demand_forecast > current_capacity * 1.2 THEN 'ADD_TRAINS'
            WHEN demand_forecast < current_capacity * 0.8 THEN 'REDUCE_FREQUENCY'
            ELSE 'MAINTAIN'
        END as recommendation
    FROM (
        SELECT 
            CONCAT(from_station, '-', to_station) as route,
            COUNT(*) as current_bookings,
            AVG(passenger_count) * 365 as demand_forecast,
            SUM(total_fare) as revenue_potential,
            -- Assuming average train capacity
            COUNT(DISTINCT train_no) * 1000 as current_capacity
        FROM staging.booking_data
        GROUP BY from_station, to_station
    ) route_stats
    """
    
    hook.run(query)
    logger.info("Route optimization calculations completed")
    return "Route optimization completed"

def perform_revenue_analysis(**context):
    """Perform revenue analysis - Mumbai business insights!"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    # Revenue analysis queries
    revenue_queries = [
        """
        INSERT INTO analytics.daily_revenue
        SELECT 
            '{{ ds }}' as date,
            'total' as category,
            SUM(total_fare) as revenue,
            COUNT(*) as booking_count,
            AVG(total_fare) as avg_booking_value
        FROM staging.booking_data
        """,
        """
        INSERT INTO analytics.revenue_by_class
        SELECT 
            '{{ ds }}' as date,
            class_type,
            SUM(total_fare) as revenue,
            COUNT(*) as booking_count,
            SUM(passenger_count) as passenger_count
        FROM staging.booking_data
        GROUP BY class_type
        """,
        """
        INSERT INTO analytics.payment_method_revenue
        SELECT 
            '{{ ds }}' as date,
            p.payment_method,
            SUM(b.total_fare) as revenue,
            COUNT(*) as transaction_count,
            AVG(p.processing_fee) as avg_processing_fee
        FROM staging.booking_data b
        JOIN staging.payment_data p ON b.booking_id = p.booking_id
        GROUP BY p.payment_method
        """
    ]
    
    for query in revenue_queries:
        hook.run(query)
    
    logger.info("Revenue analysis completed")
    return "Revenue analysis completed"

def capacity_planning_analysis(**context):
    """Capacity planning analysis for future demand"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    query = """
    INSERT INTO analytics.capacity_planning
    SELECT 
        route,
        current_date,
        predicted_demand,
        current_supply,
        capacity_utilization,
        CASE 
            WHEN capacity_utilization > 90 THEN 'CRITICAL'
            WHEN capacity_utilization > 75 THEN 'HIGH'
            WHEN capacity_utilization > 50 THEN 'MEDIUM'
            ELSE 'LOW'
        END as demand_level,
        CASE 
            WHEN capacity_utilization > 90 THEN 'IMMEDIATE_ACTION_REQUIRED'
            WHEN capacity_utilization > 75 THEN 'PLAN_ADDITIONAL_SERVICES'
            ELSE 'MONITOR'
        END as recommendation
    FROM (
        SELECT 
            CONCAT(from_station, '-', to_station) as route,
            CURRENT_DATE as current_date,
            COUNT(*) * 1.2 as predicted_demand, -- 20% growth assumption
            COUNT(DISTINCT train_no) * 1000 as current_supply,
            (COUNT(*) * 1.0 / (COUNT(DISTINCT train_no) * 1000)) * 100 as capacity_utilization
        FROM staging.booking_data
        WHERE DATE(journey_date) >= CURRENT_DATE
        GROUP BY from_station, to_station
    ) capacity_stats
    """
    
    hook.run(query)
    logger.info("Capacity planning analysis completed")
    return "Capacity planning completed"

def generate_daily_reports(**context):
    """Generate daily reports for management"""
    hook = PostgresHook(postgres_conn_id=config.database_conn_id)
    
    # Generate executive summary
    summary_query = """
    SELECT 
        COUNT(*) as total_bookings,
        SUM(total_fare) as total_revenue,
        COUNT(DISTINCT user_id) as unique_passengers,
        AVG(total_fare) as avg_booking_value,
        COUNT(CASE WHEN tatkal_flag = true THEN 1 END) as tatkal_bookings,
        COUNT(CASE WHEN booking_status = 'CONFIRMED' THEN 1 END) as confirmed_bookings,
        COUNT(CASE WHEN booking_status = 'WAITING' THEN 1 END) as waiting_bookings
    FROM staging.booking_data
    """
    
    summary = hook.get_first(summary_query)
    
    # Store summary
    insert_summary = """
    INSERT INTO analytics.daily_summary 
    VALUES ('{{ ds }}', %s, %s, %s, %s, %s, %s, %s)
    """
    
    hook.run(insert_summary, parameters=summary)
    
    logger.info(f"Daily summary generated: {summary}")
    return summary

# Create task groups
extraction_group = create_data_extraction_tasks()
transformation_group = create_data_transformation_tasks()
loading_group = create_data_loading_tasks()
error_handling_group = create_error_handling_tasks()

# Pipeline start and end markers
pipeline_start = DummyOperator(
    task_id='pipeline_start',
    dag=dag
)

pipeline_end = DummyOperator(
    task_id='pipeline_end',
    dag=dag,
    trigger_rule=TriggerRule.NONE_FAILED_OR_SKIPPED
)

# Set main pipeline dependencies
pipeline_start >> extraction_group >> transformation_group >> loading_group >> error_handling_group >> pipeline_end

# Add monitoring and alerting
def pipeline_success_callback(context):
    """Success callback for pipeline completion"""
    logger.info("🎉 IRCTC Data Pipeline completed successfully!")

def pipeline_failure_callback(context):
    """Failure callback for pipeline errors"""
    logger.error("❌ IRCTC Data Pipeline failed!")
    # Additional alerting logic here

# Set callbacks
dag.on_success_callback = pipeline_success_callback
dag.on_failure_callback = pipeline_failure_callback

"""
Mumbai Learning Notes:
1. Complex DAG structure with task groups for organization
2. Dynamic task generation based on data sources
3. Error handling and monitoring patterns
4. XCom usage for inter-task communication
5. Branch operators for conditional logic
6. Email notifications for success/failure scenarios
7. Database operators for data warehouse operations
8. Spark integration for heavy transformations
9. Data quality checks with automated failure handling
10. Indian railway domain-specific business logic

Production Considerations:
- Set up proper Airflow cluster with Redis/PostgreSQL
- Configure connection credentials securely
- Set up monitoring dashboards
- Implement proper logging and alerting
- Add data lineage tracking
- Set resource limits for Spark jobs
- Configure backup and disaster recovery
- Add compliance and audit logging
"""