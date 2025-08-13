"""
Production Airflow Configuration for Indian Infrastructure
Episode 12: Airflow Orchestration - Production Configuration

यह file production-grade Airflow configuration provide करती है जो
Indian infrastructure और business requirements के लिए optimized है।

Author: Code Developer Agent
Language: Python with Hindi Comments
Context: Production Airflow setup for Indian tech companies
"""

import os
from datetime import timedelta
from typing import Dict, Any, List
import logging

# =============================================================================
# Core Airflow Configuration
# =============================================================================

class ProductionAirflowConfig:
    """Production Airflow configuration for Indian deployments"""
    
    # Core Airflow settings
    AIRFLOW_CONFIG = {
        # Core configuration
        'core': {
            'dags_folder': '/opt/airflow/dags',
            'base_log_folder': '/opt/airflow/logs',
            'remote_logging': 'True',
            'remote_log_conn_id': 's3_logging',
            'remote_base_log_folder': 's3://airflow-logs-india/logs',
            'logging_level': 'INFO',
            'fab_logging_level': 'WARN',
            'log_filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log',
            'log_processor_filename_template': '{{ filename }}.log',
            'dag_processor_manager_log_location': '/opt/airflow/logs/dag_processor_manager/dag_processor_manager.log',
            'hostname_callable': 'airflow.utils.net.get_hostname',
            'default_timezone': 'Asia/Kolkata',  # Indian Standard Time
            'executor': 'CeleryExecutor',
            'sql_alchemy_conn': 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow',
            'sql_alchemy_pool_enabled': 'True',
            'sql_alchemy_pool_size': '10',
            'sql_alchemy_max_overflow': '20',
            'sql_alchemy_pool_recycle': '1800',  # 30 minutes
            'sql_alchemy_pool_pre_ping': 'True',
            'parallelism': '64',  # Increased for Indian scale
            'dag_concurrency': '32',
            'dags_are_paused_at_creation': 'False',
            'non_pooled_task_slot_count': '128',
            'max_active_runs_per_dag': '16',
            'load_examples': 'False',
            'plugins_folder': '/opt/airflow/plugins',
            'fernet_key': '{{ AIRFLOW_FERNET_KEY }}',  # Environment variable
            'donot_pickle': 'False',
            'dagbag_import_timeout': '300',  # 5 minutes for complex DAGs
            'dagbag_import_error_tracebacks': 'True',
            'dagbag_import_error_traceback_depth': '2',
            'dag_file_processor_timeout': '300',
            'task_runner': 'StandardTaskRunner',
            'default_task_retries': '3',  # More retries for Indian infrastructure
            'task_retry_delay': '300',  # 5 minutes
            'max_task_retry_delay': '86400',  # 1 day max
            'store_serialized_dags': 'True',
            'max_num_rendered_ti_fields_per_task': '30',
            'check_slas': 'True',
            'xcom_backend': 'airflow.models.xcom.BaseXCom',
            'lazy_load_plugins': 'True',
            'lazy_discover_providers': 'True'
        },
        
        # Celery Executor Configuration (for scaling)
        'celery': {
            'broker_url': 'redis://redis:6379/0',
            'result_backend': 'redis://redis:6379/0',
            'worker_concurrency': '16',  # Optimized for Indian workloads
            'worker_log_server_port': '8793',
            'broker_transport_options': json.dumps({
                'priority_steps': list(range(10)),
                'sep': ':',
                'queue_order_strategy': 'priority'
            }),
            'task_track_started': 'True',
            'task_acks_late': 'True',
            'worker_prefetch_multiplier': '4',  # Reduced for memory efficiency
            'task_default_queue': 'default',
            'task_default_exchange_type': 'direct',
            'task_default_routing_key': 'default',
            'task_routes': json.dumps({
                'airflow.executors.celery_executor.execute_command': {
                    'queue': 'airflow'
                }
            }),
            'worker_autoscale': '16,4',  # Scale between 4-16 workers
            'worker_enable_remote_control': 'True',
            'worker_send_task_events': 'True',
            'task_send_sent_event': 'True',
            'result_expires': '86400',  # 24 hours
            'task_compression': 'gzip',
            'result_compression': 'gzip',
            'accept_content': 'json',
            'task_serializer': 'json',
            'result_serializer': 'json'
        },
        
        # Scheduler Configuration
        'scheduler': {
            'job_heartbeat_sec': '5',
            'scheduler_heartbeat_sec': '5',
            'num_runs': '-1',  # Run indefinitely
            'processor_poll_interval': '1',
            'min_file_process_interval': '30',
            'dag_dir_list_interval': '300',  # 5 minutes
            'print_stats_interval': '30',
            'pool_metrics_interval': '5.0',
            'scheduler_health_check_threshold': '30',
            'child_process_timeout': '600',  # 10 minutes
            'scheduler_zombie_task_threshold': '300',  # 5 minutes
            'catchup_by_default': 'False',  # Don't catch up by default
            'max_tis_per_query': '512',
            'use_row_level_locking': 'True',
            'max_dagruns_to_create_per_loop': '10',
            'max_dagruns_per_loop_to_schedule': '20',
            'schedule_after_task_execution': 'True',
            'parsing_processes': '4',  # Parallel DAG parsing
            'file_parsing_sort_mode': 'modified_time',
            'allow_trigger_in_future': 'False'
        },
        
        # Webserver Configuration
        'webserver': {
            'base_url': 'https://airflow.company.co.in',  # Indian domain
            'default_ui_timezone': 'Asia/Kolkata',
            'web_server_host': '0.0.0.0',
            'web_server_port': '8080',
            'web_server_ssl_cert': '/opt/airflow/ssl/airflow.crt',
            'web_server_ssl_key': '/opt/airflow/ssl/airflow.key',
            'web_server_worker_timeout': '120',
            'worker_refresh_batch_size': '1',
            'worker_refresh_interval': '30',
            'secret_key': '{{ AIRFLOW_SECRET_KEY }}',
            'workers': '4',  # Gunicorn workers
            'worker_class': 'sync',
            'access_logfile': '-',
            'error_logfile': '-',
            'expose_config': 'False',  # Security
            'authenticate': 'True',
            'auth_backend': 'airflow.contrib.auth.backends.google_auth',  # Or LDAP for enterprises
            'filter_by_owner': 'True',
            'owner_mode': 'ldapgroup',  # For enterprise setups
            'dag_default_view': 'graph',
            'dag_orientation': 'TB',
            'log_fetch_timeout_sec': '5',
            'hide_paused_dags_by_default': 'False',
            'page_size': '25',
            'navbar_color': '#1E88E5',  # Indian blue theme
            'default_dag_run_display_number': '25',
            'enable_proxy_fix': 'True',  # For load balancers
            'proxy_fix_x_for': '1',
            'proxy_fix_x_proto': '1',
            'proxy_fix_x_host': '1',
            'proxy_fix_x_port': '1',
            'proxy_fix_x_prefix': '1',
            'cookie_secure': 'True',
            'cookie_samesite': 'Lax',
            'session_lifetime_minutes': '43200',  # 30 days
            'audit_logs': 'True',
            'auto_refresh_interval': '3'  # seconds
        },
        
        # Email Configuration for Indian providers
        'email': {
            'email_backend': 'airflow.providers.sendgrid.utils.emailer.send_email',
            'email_conn_id': 'sendgrid_default',
            'default_email_on_retry': 'True',
            'default_email_on_failure': 'True',
            'from_email': 'airflow@company.co.in',
            'subject_template': '[Airflow] {{ dag.dag_id }} - {{ task.task_id }} - {{ ds }}',
            'html_content_template': '''
            <h2>Task Failed: {{ task_instance.task_id }}</h2>
            <p><strong>DAG:</strong> {{ dag.dag_id }}</p>
            <p><strong>Execution Date:</strong> {{ ds }}</p>
            <p><strong>Log URL:</strong> <a href="{{ task_instance.log_url }}">View Logs</a></p>
            <p><strong>Error:</strong> {{ task_instance.log }}</p>
            ''',
            'email_retry_limit': '3',
            'email_retry_delay': '300'  # 5 minutes
        },
        
        # Operators Configuration
        'operators': {
            'default_owner': 'data-engineering-team',
            'default_cpus': '1',
            'default_ram': '2048',  # 2GB RAM
            'default_disk': '10',   # 10GB disk
            'default_gpus': '0'
        },
        
        # Logging Configuration
        'logging': {
            'logging_level': 'INFO',
            'fab_logging_level': 'WARN',
            'logging_config_class': 'airflow.config_templates.airflow_local_settings.LOGGING_CONFIG',
            'colored_console_log': 'True',
            'colored_log_format': '[%(blue)s%(asctime)s%(reset)s] {%(blue)s%(filename)s:%(lineno)d%(reset)s} %(log_color)s%(levelname)s%(reset)s - %(log_color)s%(message)s%(reset)s',
            'colored_formatter_class': 'airflow.utils.log.colored_log.CustomTTYColoredFormatter',
            'log_format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            'simple_log_format': '%(asctime)s %(levelname)s - %(message)s',
            'log_filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log',
            'log_processor_filename_template': '{{ filename }}.log',
            'dag_processor_manager_log_location': '/opt/airflow/logs/dag_processor_manager/dag_processor_manager.log',
            'task_log_prefix_template': '',
            'enable_task_context_logger': 'True'
        },
        
        # Metrics and Monitoring (StatsD for Indian monitoring systems)
        'metrics': {
            'statsd_on': 'True',
            'statsd_host': 'statsd.monitoring.company.co.in',
            'statsd_port': '8125',
            'statsd_prefix': 'airflow_india',
            'statsd_allow_list': '',
            'stat_name_handler': 'airflow.stats.SafeStatsdLogger.safe_name',
            'statsd_datadog_enabled': 'False',
            'statsd_datadog_tags': '',
            'statsd_custom_client_path': ''
        },
        
        # Lineage Configuration
        'lineage': {
            'backend': 'airflow.lineage.backend.atlas.AtlasBackend'  # Apache Atlas for data lineage
        },
        
        # Atlas Configuration (for data governance)
        'atlas': {
            'host': 'atlas.company.co.in',
            'port': '21000',
            'username': 'airflow',
            'password': '{{ ATLAS_PASSWORD }}'
        },
        
        # Kubernetes Configuration (for cloud deployments)
        'kubernetes': {
            'airflow_configmap': 'airflow-configmap',
            'worker_container_repository': 'registry.company.co.in/airflow-worker',
            'worker_container_tag': 'latest',
            'namespace': 'airflow-production',
            'delete_worker_pods': 'True',
            'delete_worker_pods_on_failure': 'False',
            'worker_pods_creation_batch_size': '10',
            'multi_namespace_mode': 'False',
            'in_cluster': 'True',
            'cluster_context': 'india-production',
            'config_file': '/opt/airflow/.kube/config',
            'node_selectors': json.dumps({
                'cloud.google.com/gke-nodepool': 'airflow-workers'  # For GKE
            }),
            'tolerations': json.dumps([]),
            'affinity': json.dumps({
                'nodeAffinity': {
                    'requiredDuringSchedulingIgnoredDuringExecution': {
                        'nodeSelectorTerms': [{
                            'matchExpressions': [{
                                'key': 'node-type',
                                'operator': 'In',
                                'values': ['airflow-worker']
                            }]
                        }]
                    }
                }
            }),
            'image_pull_secrets': 'registry-secret',
            'gcp_service_account_keys': '/opt/airflow/service-account.json',
            'enable_tcp_keepalive': 'True',
            'tcp_keep_idle': '600',
            'tcp_keep_intvl': '30',
            'tcp_keep_cnt': '6'
        },
        
        # Security Configuration
        'security': {
            'secure_mode': 'True',
            'ssl_active': 'True',
            'ssl_cert': '/opt/airflow/ssl/airflow.crt',
            'ssl_key': '/opt/airflow/ssl/airflow.key',
            'ssl_cacert': '/opt/airflow/ssl/ca.crt'
        },
        
        # Smart Sensors (for efficient resource usage)
        'smart_sensor': {
            'use_smart_sensor': 'True',
            'shard_code_upper_limit': '10000',
            'shards': '5',
            'sensors_enabled': json.dumps([
                'airflow.sensors.filesystem.FileSensor',
                'airflow.sensors.s3_key_sensor.S3KeySensor',
                'airflow.sensors.sql_sensor.SqlSensor'
            ])
        }
    }
    
    # Indian Business-Specific Pools
    RESOURCE_POOLS = {
        'banking_pool': {
            'slots': 8,
            'description': 'Resource pool for banking and financial operations'
        },
        'ecommerce_pool': {
            'slots': 16,
            'description': 'Resource pool for e-commerce data processing'
        },
        'ml_training_pool': {
            'slots': 4,
            'description': 'Resource pool for ML model training (GPU intensive)'
        },
        'data_extraction_pool': {
            'slots': 12,
            'description': 'Resource pool for data extraction operations'
        },
        'compliance_pool': {
            'slots': 6,
            'description': 'Resource pool for regulatory compliance checks'
        },
        'disaster_response_pool': {
            'slots': 20,
            'description': 'High-priority pool for disaster recovery operations'
        },
        'recovery_pool': {
            'slots': 10,
            'description': 'Resource pool for standard recovery operations'
        },
        'ml_processing_pool': {
            'slots': 8,
            'description': 'Resource pool for ML data processing'
        },
        'festival_surge_pool': {
            'slots': 24,
            'description': 'Additional capacity for festival season surge'
        }
    }
    
    # Indian Business Variables
    AIRFLOW_VARIABLES = {
        # Business Configuration
        'indian_business_hours_start': '9',
        'indian_business_hours_end': '18',
        'lunch_break_start': '13',
        'lunch_break_end': '14',
        
        # Regional Configuration
        'primary_regions': json.dumps(['Mumbai', 'Bangalore', 'Delhi', 'Chennai', 'Hyderabad']),
        'backup_regions': json.dumps(['Pune', 'Kolkata', 'Ahmedabad']),
        'disaster_recovery_region': 'Bangalore',
        
        # Festival Season Configuration
        'festival_months': json.dumps([10, 11, 12]),  # Oct-Dec
        'monsoon_months': json.dumps([6, 7, 8, 9]),   # Jun-Sep
        'summer_months': json.dumps([3, 4, 5]),       # Mar-May
        
        # Compliance Configuration
        'rbi_reporting_enabled': 'True',
        'sebi_reporting_enabled': 'True',
        'high_value_transaction_threshold': '200000',  # ₹2 lakh
        'kyc_validity_days': '365',
        'aml_check_enabled': 'True',
        
        # Performance Configuration
        'max_retry_attempts': '3',
        'retry_delay_seconds': '300',  # 5 minutes
        'sla_miss_email_list': json.dumps([
            'sre@company.co.in',
            'data-engineering@company.co.in'
        ]),
        
        # Cost Optimization
        'auto_scaling_enabled': 'True',
        'cost_optimization_enabled': 'True',
        'off_peak_hours': json.dumps(list(range(22, 24)) + list(range(0, 6))),
        'peak_hours': json.dumps(list(range(9, 21))),
        
        # Monitoring Configuration
        'monitoring_enabled': 'True',
        'slack_alerts_enabled': 'True',
        'pagerduty_enabled': 'True',
        'grafana_dashboard_url': 'https://grafana.company.co.in/d/airflow',
        
        # Data Storage Configuration
        'data_lake_bucket': 's3://datalake-india-prod',
        'backup_bucket': 's3://backups-india-prod',
        'logs_bucket': 's3://airflow-logs-india',
        'temp_storage_path': '/tmp/airflow-temp',
        
        # External Service Configuration
        'payment_gateway_timeout': '30',  # seconds
        'sms_provider_timeout': '10',
        'email_provider_timeout': '15',
        'database_connection_timeout': '30',
        'api_rate_limit_per_minute': '1000',
        
        # Indian Telecom Configuration
        'primary_sms_provider': 'textlocal',
        'backup_sms_providers': json.dumps(['msg91', 'routemobile']),
        'dnd_filtering_enabled': 'True',
        'unicode_sms_enabled': 'True',
        
        # Banking Integration Configuration
        'razorpay_timeout': '30',
        'payu_timeout': '45',
        'ccavenue_timeout': '60',
        'upi_timeout': '20',
        'netbanking_timeout': '120',
        
        # Regional Language Support
        'supported_languages': json.dumps([
            'hindi', 'english', 'tamil', 'telugu', 'marathi', 
            'gujarati', 'bengali', 'kannada', 'malayalam'
        ]),
        'default_language': 'english',
        'auto_language_detection': 'True'
    }
    
    # Connection Configurations for Indian Services
    CONNECTIONS = {
        # Database Connections
        'postgres_prod': {
            'conn_type': 'postgres',
            'host': 'postgres.prod.company.co.in',
            'schema': 'production',
            'login': 'airflow_user',
            'password': '{{ POSTGRES_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'connect_timeout': 30,
                'application_name': 'airflow_production'
            })
        },
        
        # Redis Connection
        'redis_prod': {
            'conn_type': 'redis',
            'host': 'redis.prod.company.co.in',
            'port': 6379,
            'password': '{{ REDIS_PASSWORD }}',
            'extra': json.dumps({
                'db': 0,
                'ssl': True,
                'ssl_cert_reqs': 'required'
            })
        },
        
        # AWS Connections
        'aws_india': {
            'conn_type': 'aws',
            'extra': json.dumps({
                'aws_access_key_id': '{{ AWS_ACCESS_KEY_ID }}',
                'aws_secret_access_key': '{{ AWS_SECRET_ACCESS_KEY }}',
                'region_name': 'ap-south-1'  # Mumbai region
            })
        },
        
        # Google Cloud Connection
        'gcp_india': {
            'conn_type': 'google_cloud_platform',
            'extra': json.dumps({
                'extra__google_cloud_platform__project': 'company-india-prod',
                'extra__google_cloud_platform__key_path': '/opt/airflow/gcp-service-account.json',
                'extra__google_cloud_platform__scope': 'https://www.googleapis.com/auth/cloud-platform'
            })
        },
        
        # Indian Payment Gateways
        'razorpay_api': {
            'conn_type': 'http',
            'host': 'https://api.razorpay.com',
            'extra': json.dumps({
                'headers': {
                    'Authorization': 'Basic {{ RAZORPAY_API_KEY }}:{{ RAZORPAY_API_SECRET }}'
                }
            })
        },
        
        'payu_api': {
            'conn_type': 'http',
            'host': 'https://secure.payu.in',
            'extra': json.dumps({
                'timeout': 45,
                'verify': True
            })
        },
        
        # Indian SMS Providers
        'textlocal_sms': {
            'conn_type': 'http',
            'host': 'https://api.textlocal.in',
            'extra': json.dumps({
                'apikey': '{{ TEXTLOCAL_API_KEY }}',
                'sender': 'COMPNY'
            })
        },
        
        'msg91_sms': {
            'conn_type': 'http',
            'host': 'https://api.msg91.com',
            'extra': json.dumps({
                'authkey': '{{ MSG91_AUTH_KEY }}',
                'route': '4'  # Promotional route
            })
        },
        
        # Slack for Indian Team
        'slack_india_alerts': {
            'conn_type': 'http',
            'host': 'https://hooks.slack.com',
            'password': '{{ SLACK_WEBHOOK_TOKEN }}',  # Webhook token
            'extra': json.dumps({
                'channel': '#airflow-alerts-india',
                'username': 'Airflow-India-Bot'
            })
        },
        
        # Monitoring Systems
        'grafana_india': {
            'conn_type': 'http',
            'host': 'https://grafana.company.co.in',
            'login': 'airflow',
            'password': '{{ GRAFANA_PASSWORD }}',
            'extra': json.dumps({
                'timeout': 30,
                'verify': True
            })
        },
        
        # Indian Banking Systems
        'banking_db': {
            'conn_type': 'postgres',
            'host': 'banking-db.secure.company.co.in',
            'schema': 'banking',
            'login': 'airflow_banking',
            'password': '{{ BANKING_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'sslcert': '/opt/airflow/ssl/banking-client.crt',
                'sslkey': '/opt/airflow/ssl/banking-client.key',
                'sslrootcert': '/opt/airflow/ssl/banking-ca.crt'
            })
        },
        
        'compliance_db': {
            'conn_type': 'postgres',
            'host': 'compliance-db.secure.company.co.in',
            'schema': 'compliance',
            'login': 'airflow_compliance',
            'password': '{{ COMPLIANCE_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'connect_timeout': 30
            })
        },
        
        # E-commerce Systems
        'ecommerce_db': {
            'conn_type': 'postgres',
            'host': 'ecommerce-db.company.co.in',
            'schema': 'ecommerce',
            'login': 'airflow_ecommerce',
            'password': '{{ ECOMMERCE_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'prefer',
                'connect_timeout': 30,
                'application_name': 'airflow_ecommerce_pipeline'
            })
        },
        
        # Customer Database
        'customer_db': {
            'conn_type': 'postgres',
            'host': 'customer-db.company.co.in',
            'schema': 'customers',
            'login': 'airflow_customer',
            'password': '{{ CUSTOMER_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'connect_timeout': 30
            })
        },
        
        # Disaster Recovery Database
        'disaster_recovery_db': {
            'conn_type': 'postgres',
            'host': 'dr-db.company.co.in',
            'schema': 'disaster_recovery',
            'login': 'airflow_dr',
            'password': '{{ DR_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'connect_timeout': 30
            })
        },
        
        # Payment Database
        'payments_db': {
            'conn_type': 'postgres',
            'host': 'payments-db.secure.company.co.in',
            'schema': 'payments',
            'login': 'airflow_payments',
            'password': '{{ PAYMENTS_DB_PASSWORD }}',
            'port': 5432,
            'extra': json.dumps({
                'sslmode': 'require',
                'sslcert': '/opt/airflow/ssl/payments-client.crt',
                'sslkey': '/opt/airflow/ssl/payments-client.key'
            })
        },
        
        # Monitoring API
        'monitoring_api': {
            'conn_type': 'http',
            'host': 'https://monitoring.company.co.in',
            'extra': json.dumps({
                'headers': {
                    'Authorization': 'Bearer {{ MONITORING_API_TOKEN }}'
                },
                'timeout': 30
            })
        }
    }

# =============================================================================
# Environment-Specific Configurations
# =============================================================================

class EnvironmentConfigs:
    """Environment-specific configurations for different deployment stages"""
    
    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """Development environment configuration"""
        config = ProductionAirflowConfig.AIRFLOW_CONFIG.copy()
        
        # Override for development
        config['core']['logging_level'] = 'DEBUG'
        config['core']['parallelism'] = '8'
        config['core']['dag_concurrency'] = '4'
        config['core']['max_active_runs_per_dag'] = '2'
        config['core']['load_examples'] = 'True'
        
        config['celery']['worker_concurrency'] = '4'
        config['celery']['worker_autoscale'] = '4,2'
        
        config['scheduler']['parsing_processes'] = '1'
        config['scheduler']['max_dagruns_to_create_per_loop'] = '2'
        
        config['webserver']['workers'] = '2'
        config['webserver']['authenticate'] = 'False'
        
        return config
    
    @staticmethod
    def get_staging_config() -> Dict[str, Any]:
        """Staging environment configuration"""
        config = ProductionAirflowConfig.AIRFLOW_CONFIG.copy()
        
        # Override for staging
        config['core']['parallelism'] = '32'
        config['core']['dag_concurrency'] = '16'
        config['core']['max_active_runs_per_dag'] = '8'
        
        config['celery']['worker_concurrency'] = '8'
        config['celery']['worker_autoscale'] = '8,2'
        
        config['scheduler']['parsing_processes'] = '2'
        
        config['webserver']['workers'] = '2'
        
        return config
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """Production environment configuration (default)"""
        return ProductionAirflowConfig.AIRFLOW_CONFIG

# =============================================================================
# Indian Infrastructure Optimization
# =============================================================================

class IndianInfrastructureOptimizer:
    """Optimize Airflow for Indian infrastructure patterns"""
    
    @staticmethod
    def get_monsoon_season_config() -> Dict[str, Any]:
        """Configuration adjustments for monsoon season"""
        return {
            'task_retry_delay': '600',  # 10 minutes (longer delays during monsoon)
            'max_task_retry_delay': '3600',  # 1 hour max
            'default_task_retries': '5',  # More retries during monsoon
            'scheduler_zombie_task_threshold': '600',  # 10 minutes
            'dagbag_import_timeout': '600',  # 10 minutes for network issues
        }
    
    @staticmethod
    def get_festival_season_config() -> Dict[str, Any]:
        """Configuration adjustments for festival season (high traffic)"""
        return {
            'parallelism': '128',  # Double normal capacity
            'dag_concurrency': '64',
            'non_pooled_task_slot_count': '256',
            'max_active_runs_per_dag': '32',
            'celery': {
                'worker_concurrency': '32',
                'worker_autoscale': '32,8'
            },
            'webserver': {
                'workers': '8'
            }
        }
    
    @staticmethod
    def get_network_optimized_config() -> Dict[str, Any]:
        """Configuration for poor network conditions"""
        return {
            'sql_alchemy_pool_recycle': '600',  # 10 minutes (shorter recycle)
            'sql_alchemy_pool_pre_ping': 'True',
            'dag_file_processor_timeout': '600',
            'kubernetes': {
                'enable_tcp_keepalive': 'True',
                'tcp_keep_idle': '300',  # 5 minutes
                'tcp_keep_intvl': '15',
                'tcp_keep_cnt': '3'
            }
        }

# =============================================================================
# Security Configuration for Indian Compliance
# =============================================================================

class IndianSecurityConfig:
    """Security configurations for Indian regulatory compliance"""
    
    SECURITY_SETTINGS = {
        # Data Privacy (for Aadhaar, PAN, etc.)
        'data_privacy': {
            'mask_sensitive_fields': True,
            'encrypt_xcom': True,
            'audit_logs': True,
            'access_control': 'rbac',
            'sensitive_field_patterns': [
                r'\b\d{4}\s\d{4}\s\d{4}\b',  # Aadhaar pattern
                r'\b[A-Z]{5}\d{4}[A-Z]\b',   # PAN pattern
                r'\b[A-Z]{4}0[A-Z0-9]{6}\b'  # IFSC pattern
            ]
        },
        
        # Network Security
        'network': {
            'ssl_required': True,
            'certificate_validation': True,
            'allowed_ips': [
                '10.0.0.0/8',     # Private networks
                '172.16.0.0/12',
                '192.168.0.0/16'
            ],
            'blocked_countries': ['CN', 'RU', 'KP'],  # Geoblocking
            'rate_limiting': {
                'requests_per_minute': 1000,
                'burst_size': 100
            }
        },
        
        # Authentication
        'authentication': {
            'multi_factor_required': True,
            'session_timeout_minutes': 480,  # 8 hours
            'password_policy': {
                'min_length': 12,
                'require_special_chars': True,
                'require_numbers': True,
                'require_uppercase': True,
                'password_history': 10
            },
            'lockout_policy': {
                'max_attempts': 5,
                'lockout_duration_minutes': 30
            }
        },
        
        # Compliance Logging
        'compliance_logging': {
            'log_all_access': True,
            'log_data_changes': True,
            'log_admin_actions': True,
            'retention_days': 2555,  # 7 years as per Indian regulations
            'export_format': 'json',
            'encryption': 'AES-256'
        }
    }

# =============================================================================
# Usage Examples
# =============================================================================

def generate_airflow_config_file(environment: str = 'production') -> str:
    """Generate complete airflow.cfg file for specified environment"""
    
    if environment == 'development':
        config = EnvironmentConfigs.get_development_config()
    elif environment == 'staging':
        config = EnvironmentConfigs.get_staging_config()
    else:
        config = EnvironmentConfigs.get_production_config()
    
    config_lines = []
    config_lines.append("# Generated Airflow Configuration for Indian Infrastructure")
    config_lines.append(f"# Environment: {environment.upper()}")
    config_lines.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    config_lines.append("")
    
    for section, settings in config.items():
        config_lines.append(f"[{section}]")
        for key, value in settings.items():
            config_lines.append(f"{key} = {value}")
        config_lines.append("")
    
    return "\n".join(config_lines)

def create_indian_pools_script() -> str:
    """Generate SQL script to create Indian business pools"""
    
    sql_commands = []
    sql_commands.append("-- Create Indian Business Resource Pools")
    sql_commands.append("-- Run this after Airflow database initialization")
    sql_commands.append("")
    
    for pool_name, config in ProductionAirflowConfig.RESOURCE_POOLS.items():
        sql_commands.append(f"""
INSERT INTO slot_pool (pool, slots, description) 
VALUES ('{pool_name}', {config['slots']}, '{config['description']}')
ON CONFLICT (pool) DO UPDATE SET 
    slots = EXCLUDED.slots,
    description = EXCLUDED.description;
        """.strip())
    
    return "\n".join(sql_commands)

def create_indian_variables_script() -> str:
    """Generate SQL script to create Indian business variables"""
    
    sql_commands = []
    sql_commands.append("-- Create Indian Business Variables")
    sql_commands.append("")
    
    for var_name, var_value in ProductionAirflowConfig.AIRFLOW_VARIABLES.items():
        # Escape single quotes in values
        escaped_value = str(var_value).replace("'", "''")
        sql_commands.append(f"""
INSERT INTO variable (key, val) 
VALUES ('{var_name}', '{escaped_value}')
ON CONFLICT (key) DO UPDATE SET val = EXCLUDED.val;
        """.strip())
    
    return "\n".join(sql_commands)

# Export configuration for use in deployment scripts
if __name__ == "__main__":
    # Generate production configuration
    print("# Production Airflow Configuration for Indian Infrastructure")
    print(generate_airflow_config_file('production'))
    
    print("\n# Resource Pools Setup")
    print(create_indian_pools_script())
    
    print("\n# Variables Setup") 
    print(create_indian_variables_script())

"""
Production Airflow Configuration Summary
=======================================

यह comprehensive configuration file Indian tech companies के लिए
production-ready Airflow setup provide करती है:

### Key Features:
1. **Indian Context**: IST timezone, business hours, festival seasons
2. **Scalability**: Optimized for Indian scale (millions of users)
3. **Security**: Compliance with Indian data protection regulations
4. **Monitoring**: Integration with Indian monitoring systems
5. **Disaster Recovery**: Multi-region setup for Indian geography
6. **Cost Optimization**: Resource management for cost efficiency

### Environment Support:
- Development: Reduced resources, debug logging
- Staging: Medium scale for testing
- Production: Full scale with all features

### Indian Infrastructure Optimizations:
- Monsoon season adjustments (network issues, power outages)
- Festival season scaling (traffic spikes)
- Regional deployment patterns
- Indian payment gateway integration
- Compliance with RBI, SEBI regulations

### Security Features:
- PII data masking (Aadhaar, PAN)
- Multi-factor authentication
- Audit logging for compliance
- Network security controls

### Usage:
```bash
# Generate production config
python production_airflow_config.py > airflow.cfg

# Setup pools and variables
python production_airflow_config.py | grep -A 1000 "Resource Pools" > setup_pools.sql
```

यह configuration Indian tech ecosystem की complexity को handle करते हुए
enterprise-grade Airflow deployment provide करती है।
"""