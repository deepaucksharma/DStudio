#!/usr/bin/env python3
"""
ELT Pipeline with Snowflake - Warehouse-first Transformation
===========================================================

Traditional ETL के उल्ट - पहले raw data load करो, फिर warehouse में transform करो।
जैसे Amazon या Flipkart अपने data को handle करते हैं - massive scale पे।

Real-world use case: E-commerce analytics warehouse 
Daily data volume: 50TB+, Processing: Petabyte scale analytics

Author: DStudio Engineering Team
Episode: 11 - ETL & Data Integration Patterns  
"""

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas, pd_writer
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import pandas as pd
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path

@dataclass
class ELTMetrics:
    """ELT pipeline performance metrics"""
    pipeline_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Extract metrics
    sources_processed: int = 0
    raw_records_loaded: int = 0
    extract_duration_seconds: float = 0.0
    
    # Load metrics  
    load_duration_seconds: float = 0.0
    warehouse_tables_created: int = 0
    
    # Transform metrics
    transform_duration_seconds: float = 0.0
    analytics_tables_created: int = 0
    business_rules_applied: int = 0
    
    # Overall metrics
    data_freshness_minutes: float = 0.0
    cost_estimate_usd: float = 0.0
    
    def total_duration_minutes(self) -> float:
        """Total pipeline duration in minutes"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0.0

class SnowflakeELTPipeline:
    """
    Modern ELT Pipeline with Snowflake
    =================================
    
    Cloud-native approach:
    1. Extract multiple sources (APIs, Files, Databases)
    2. Load raw data directly to Snowflake (no transformation)
    3. Transform using Snowflake's compute power (SQL/Python)
    """
    
    def __init__(self, snowflake_config: Dict, aws_config: Dict = None):
        self.snowflake_config = snowflake_config
        self.aws_config = aws_config or {}
        self.logger = self._setup_logging()
        
        # Snowflake connections
        self.snowflake_conn = None
        self.sqlalchemy_engine = None
        
        # AWS clients (for S3 staging)
        self.s3_client = None
        
        # Pipeline state
        self.metrics = None
        self.pipeline_id = f"ELT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Business configuration - E-commerce analytics
        self.warehouse_config = {
            'raw_database': 'ECOMMERCE_RAW',
            'analytics_database': 'ECOMMERCE_ANALYTICS',
            'staging_database': 'ECOMMERCE_STAGING',
            'warehouse_size': 'LARGE',  # For heavy transformations
            'auto_suspend': 300,        # 5 minutes auto-suspend
            'auto_resume': True,
            'multi_cluster_warehouse': True
        }
    
    def _setup_logging(self):
        """Production-grade logging setup"""
        logger = logging.getLogger("SnowflakeELT")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler for audit
            file_handler = logging.FileHandler(
                f"snowflake_elt_{datetime.now().strftime('%Y%m%d')}.log"
            )
            console_handler = logging.StreamHandler()
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(pipeline_id)s] - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def initialize_connections(self):
        """Initialize Snowflake and AWS connections"""
        try:
            # Snowflake connection
            self.snowflake_conn = snowflake.connector.connect(
                **self.snowflake_config,
                client_session_keep_alive=True,
                autocommit=False
            )
            
            # SQLAlchemy engine for pandas integration
            snowflake_url = URL(
                account=self.snowflake_config['account'],
                user=self.snowflake_config['user'],
                password=self.snowflake_config['password'],
                database=self.warehouse_config['raw_database'],
                warehouse=self.snowflake_config.get('warehouse', 'COMPUTE_WH'),
                role=self.snowflake_config.get('role', 'ACCOUNTADMIN')
            )
            self.sqlalchemy_engine = create_engine(snowflake_url)
            
            # AWS S3 client (for external staging)
            if self.aws_config:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_config.get('access_key'),
                    aws_secret_access_key=self.aws_config.get('secret_key'),
                    region_name=self.aws_config.get('region', 'us-east-1')
                )
            
            self.logger.info("✅ All connections initialized successfully", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.logger.error(f"❌ Connection initialization failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def setup_warehouse_infrastructure(self):
        """
        Snowflake warehouse infrastructure setup
        =======================================
        
        Databases, schemas, warehouses, stages सब setup करना।
        """
        self.logger.info("🏗️ Setting up Snowflake warehouse infrastructure...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        cursor = self.snowflake_conn.cursor()
        
        try:
            # 1. Create databases
            databases = [
                self.warehouse_config['raw_database'],
                self.warehouse_config['analytics_database'], 
                self.warehouse_config['staging_database']
            ]
            
            for db in databases:
                cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {db}
                COMMENT = 'E-commerce ELT Pipeline Database - {db}'
                """)
                self.logger.info(f"✅ Database created/verified: {db}", 
                               extra={'pipeline_id': self.pipeline_id})
            
            # 2. Create schemas in raw database
            raw_schemas = [
                'ORDERS', 'CUSTOMERS', 'PRODUCTS', 'INVENTORY',
                'PAYMENTS', 'REVIEWS', 'ANALYTICS_EVENTS', 'LOGS'
            ]
            
            for schema in raw_schemas:
                cursor.execute(f"""
                CREATE SCHEMA IF NOT EXISTS {self.warehouse_config['raw_database']}.{schema}
                COMMENT = 'Raw data schema for {schema} domain'
                """)
            
            # 3. Create analytics schemas
            analytics_schemas = [
                'CUSTOMER_360', 'PRODUCT_ANALYTICS', 'ORDER_ANALYTICS',
                'REVENUE_METRICS', 'OPERATIONAL_METRICS', 'ML_FEATURES'
            ]
            
            for schema in analytics_schemas:
                cursor.execute(f"""
                CREATE SCHEMA IF NOT EXISTS {self.warehouse_config['analytics_database']}.{schema}
                COMMENT = 'Analytics schema for {schema} domain'
                """)
            
            # 4. Create compute warehouse for transformations
            cursor.execute(f"""
            CREATE WAREHOUSE IF NOT EXISTS {self.warehouse_config['warehouse_size']}_TRANSFORM_WH
            WITH
                WAREHOUSE_SIZE = '{self.warehouse_config['warehouse_size']}'
                AUTO_SUSPEND = {self.warehouse_config['auto_suspend']}
                AUTO_RESUME = {self.warehouse_config['auto_resume']}
                INITIALLY_SUSPENDED = TRUE
                COMMENT = 'Warehouse for ELT transformations'
            """)
            
            # 5. Create file format for JSON data (common in APIs)
            cursor.execute(f"""
            CREATE FILE FORMAT IF NOT EXISTS {self.warehouse_config['raw_database']}.PUBLIC.JSON_FORMAT
            TYPE = JSON
            STRIP_OUTER_ARRAY = TRUE
            COMMENT = 'JSON file format for API data ingestion'
            """)
            
            # 6. Create external stage (S3 integration)
            if self.aws_config.get('bucket'):
                cursor.execute(f"""
                CREATE STAGE IF NOT EXISTS {self.warehouse_config['raw_database']}.PUBLIC.S3_STAGE
                URL = 's3://{self.aws_config['bucket']}/raw-data/'
                CREDENTIALS = (
                    AWS_KEY_ID = '{self.aws_config['access_key']}'
                    AWS_SECRET_KEY = '{self.aws_config['secret_key']}'
                )
                FILE_FORMAT = {self.warehouse_config['raw_database']}.PUBLIC.JSON_FORMAT
                COMMENT = 'External stage for S3 data ingestion'
                """)
            
            self.snowflake_conn.commit()
            self.logger.info("🏗️ Warehouse infrastructure setup completed", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.snowflake_conn.rollback()
            self.logger.error(f"❌ Infrastructure setup failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
        finally:
            cursor.close()
    
    def extract_from_flipkart_apis(self) -> Dict[str, pd.DataFrame]:
        """
        Multiple Flipkart APIs से data extract करना
        ==========================================
        
        E-commerce के multiple data sources से parallel extraction।
        """
        self.logger.info("📡 Starting data extraction from Flipkart APIs...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        # API endpoints configuration
        api_endpoints = {
            'orders': {
                'url': 'https://api.flipkart.com/v1/orders',
                'params': {'date_range': '24h', 'status': 'all'},
                'expected_records': 100000
            },
            'customers': {
                'url': 'https://api.flipkart.com/v1/customers', 
                'params': {'updated_since': '24h', 'include_profile': True},
                'expected_records': 50000
            },
            'products': {
                'url': 'https://api.flipkart.com/v1/products',
                'params': {'category': 'all', 'include_inventory': True},
                'expected_records': 200000
            },
            'reviews': {
                'url': 'https://api.flipkart.com/v1/reviews',
                'params': {'date_range': '24h', 'include_ratings': True}, 
                'expected_records': 25000
            },
            'analytics_events': {
                'url': 'https://api.flipkart.com/v1/events',
                'params': {'event_types': 'page_view,add_to_cart,purchase'},
                'expected_records': 1000000
            }
        }
        
        extracted_data = {}
        
        # Parallel extraction using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(self._extract_single_api, source, config): source
                for source, config in api_endpoints.items()
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    data = future.result()
                    extracted_data[source] = data
                    
                    self.logger.info(f"✅ Extracted {len(data)} records from {source}", 
                                   extra={'pipeline_id': self.pipeline_id})
                    self.metrics.sources_processed += 1
                    self.metrics.raw_records_loaded += len(data)
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to extract from {source}: {str(e)}", 
                                    extra={'pipeline_id': self.pipeline_id})
        
        total_records = sum(len(df) for df in extracted_data.values())
        self.logger.info(f"📊 Total extraction completed: {total_records:,} records from {len(extracted_data)} sources", 
                        extra={'pipeline_id': self.pipeline_id})
        
        return extracted_data
    
    def _extract_single_api(self, source: str, config: Dict) -> pd.DataFrame:
        """Single API endpoint से data extraction"""
        try:
            # API call with proper headers
            headers = {
                'Authorization': f"Bearer {self.flipkart_api_token}",
                'Content-Type': 'application/json',
                'User-Agent': 'Flipkart-ELT-Pipeline/1.0'
            }
            
            response = requests.get(
                config['url'],
                params=config['params'],
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Convert to DataFrame
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                records = data['data']
            else:
                records = data
            
            df = pd.DataFrame(records)
            
            # Add extraction metadata
            df['_extracted_at'] = datetime.now()
            df['_source_system'] = source
            df['_pipeline_id'] = self.pipeline_id
            
            return df
            
        except Exception as e:
            self.logger.error(f"API extraction failed for {source}: {str(e)}")
            # Return empty DataFrame to maintain pipeline flow
            return pd.DataFrame()
    
    def load_raw_data_to_snowflake(self, extracted_data: Dict[str, pd.DataFrame]):
        """
        Raw data को directly Snowflake में load करना (No transformation)
        =============================================================
        
        ELT approach - transformation बाद में warehouse में करेंगे।
        """
        self.logger.info("📦 Loading raw data to Snowflake warehouse...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        load_start_time = time.time()
        
        try:
            for source_name, df in extracted_data.items():
                if df.empty:
                    self.logger.warning(f"⚠️ No data to load for {source_name}", 
                                      extra={'pipeline_id': self.pipeline_id})
                    continue
                
                # Dynamic table name based on current date
                table_name = f"RAW_{source_name.upper()}_{datetime.now().strftime('%Y%m%d')}"
                schema = source_name.upper()
                
                self.logger.info(f"📋 Loading {len(df)} records to {schema}.{table_name}", 
                               extra={'pipeline_id': self.pipeline_id})
                
                # Use Snowflake's pandas integration for fast bulk loading
                success, nchunks, nrows, _ = write_pandas(
                    conn=self.snowflake_conn,
                    df=df,
                    table_name=table_name,
                    database=self.warehouse_config['raw_database'],
                    schema=schema,
                    chunk_size=10000,  # Process in 10k record chunks
                    compression='gzip',
                    on_error='continue',  # Skip errors and continue
                    parallel=4,  # Parallel loading threads
                    auto_create_table=True,
                    overwrite=True  # Replace daily tables
                )
                
                if success:
                    self.logger.info(f"✅ Successfully loaded {nrows:,} rows in {nchunks} chunks to {table_name}", 
                                   extra={'pipeline_id': self.pipeline_id})
                    self.metrics.warehouse_tables_created += 1
                else:
                    self.logger.error(f"❌ Failed to load data to {table_name}", 
                                    extra={'pipeline_id': self.pipeline_id})
            
            self.metrics.load_duration_seconds = time.time() - load_start_time
            self.logger.info(f"📦 Raw data loading completed in {self.metrics.load_duration_seconds:.2f} seconds", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.logger.error(f"❌ Raw data loading failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
    
    def transform_in_warehouse(self):
        """
        Snowflake में SQL-based transformations
        =====================================
        
        Raw data से analytics-ready tables बनाना।
        Modern cloud warehouse की power का उपयोग करना।
        """
        self.logger.info("🔄 Starting warehouse transformations...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        transform_start_time = time.time()
        cursor = self.snowflake_conn.cursor()
        
        try:
            # Use dedicated warehouse for transformations
            cursor.execute(f"USE WAREHOUSE {self.warehouse_config['warehouse_size']}_TRANSFORM_WH")
            cursor.execute(f"ALTER WAREHOUSE {self.warehouse_config['warehouse_size']}_TRANSFORM_WH RESUME")
            
            # Transformation pipeline
            transformations = [
                self._create_customer_360_view,
                self._create_order_analytics_table,
                self._create_product_performance_metrics,
                self._create_revenue_analytics,
                self._create_operational_metrics,
                self._create_ml_feature_store
            ]
            
            for transform_func in transformations:
                try:
                    result = transform_func(cursor)
                    if result:
                        self.metrics.analytics_tables_created += 1
                        self.metrics.business_rules_applied += 1
                        
                except Exception as e:
                    self.logger.error(f"❌ Transformation failed in {transform_func.__name__}: {str(e)}", 
                                    extra={'pipeline_id': self.pipeline_id})
            
            # Commit all transformations
            self.snowflake_conn.commit()
            
            self.metrics.transform_duration_seconds = time.time() - transform_start_time
            self.logger.info(f"🔄 Warehouse transformations completed in {self.metrics.transform_duration_seconds:.2f} seconds", 
                           extra={'pipeline_id': self.pipeline_id})
            
        except Exception as e:
            self.snowflake_conn.rollback()
            self.logger.error(f"❌ Warehouse transformation failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
        finally:
            # Auto-suspend warehouse to save costs
            cursor.execute(f"ALTER WAREHOUSE {self.warehouse_config['warehouse_size']}_TRANSFORM_WH SUSPEND")
            cursor.close()
    
    def _create_customer_360_view(self, cursor) -> bool:
        """Customer 360 degree view - Complete customer profile"""
        self.logger.info("👥 Creating Customer 360 analytics table...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        customer_360_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.CUSTOMER_360.CUSTOMER_PROFILE AS
        WITH customer_base AS (
            SELECT 
                customer_id,
                customer_email,
                customer_name,
                registration_date,
                city,
                state,
                pincode,
                phone_number,
                _extracted_at
            FROM {self.warehouse_config['raw_database']}.CUSTOMERS.RAW_CUSTOMERS_{today}
            WHERE customer_id IS NOT NULL
        ),
        
        order_metrics AS (
            SELECT 
                customer_id,
                COUNT(*) as total_orders,
                SUM(order_value) as lifetime_value,
                AVG(order_value) as avg_order_value,
                MAX(order_date) as last_order_date,
                MIN(order_date) as first_order_date,
                COUNT(DISTINCT product_category) as categories_purchased,
                SUM(CASE WHEN order_status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_orders,
                SUM(CASE WHEN order_status = 'RETURNED' THEN 1 ELSE 0 END) as returned_orders
            FROM {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today}
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        ),
        
        review_metrics AS (
            SELECT 
                customer_id,
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating_given,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_reviews,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_reviews
            FROM {self.warehouse_config['raw_database']}.REVIEWS.RAW_REVIEWS_{today}
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        )
        
        SELECT 
            c.*,
            COALESCE(o.total_orders, 0) as total_orders,
            COALESCE(o.lifetime_value, 0) as customer_lifetime_value,
            COALESCE(o.avg_order_value, 0) as avg_order_value,
            o.last_order_date,
            o.first_order_date,
            DATEDIFF('day', o.first_order_date, CURRENT_DATE()) as customer_tenure_days,
            DATEDIFF('day', o.last_order_date, CURRENT_DATE()) as days_since_last_order,
            COALESCE(o.categories_purchased, 0) as product_categories_bought,
            COALESCE(o.cancelled_orders, 0) as cancelled_orders_count,
            COALESCE(o.returned_orders, 0) as returned_orders_count,
            COALESCE(r.total_reviews, 0) as reviews_written,
            COALESCE(r.avg_rating_given, 0) as avg_rating_given,
            
            -- Customer segmentation
            CASE 
                WHEN COALESCE(o.lifetime_value, 0) > 100000 THEN 'VIP'
                WHEN COALESCE(o.lifetime_value, 0) > 50000 THEN 'Premium'  
                WHEN COALESCE(o.lifetime_value, 0) > 10000 THEN 'Regular'
                WHEN COALESCE(o.total_orders, 0) > 0 THEN 'New Customer'
                ELSE 'Prospect'
            END as customer_segment,
            
            -- Churn risk calculation
            CASE 
                WHEN DATEDIFF('day', o.last_order_date, CURRENT_DATE()) > 180 THEN 'High Risk'
                WHEN DATEDIFF('day', o.last_order_date, CURRENT_DATE()) > 90 THEN 'Medium Risk'
                WHEN DATEDIFF('day', o.last_order_date, CURRENT_DATE()) > 30 THEN 'Low Risk'
                ELSE 'Active'
            END as churn_risk,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM customer_base c
        LEFT JOIN order_metrics o ON c.customer_id = o.customer_id
        LEFT JOIN review_metrics r ON c.customer_id = r.customer_id
        """
        
        cursor.execute(customer_360_sql)
        result = cursor.fetchone()
        
        self.logger.info("✅ Customer 360 analytics table created successfully", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def _create_order_analytics_table(self, cursor) -> bool:
        """Order analytics with business intelligence"""
        self.logger.info("📊 Creating Order Analytics table...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        order_analytics_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.ORDER_ANALYTICS.DAILY_ORDER_METRICS AS
        WITH order_base AS (
            SELECT 
                order_id,
                customer_id,
                order_date,
                order_value,
                discount_applied,
                payment_method,
                order_status,
                delivery_city,
                delivery_state,
                product_category,
                seller_id,
                delivery_date,
                _extracted_at
            FROM {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today}
            WHERE order_id IS NOT NULL
        )
        
        SELECT 
            DATE(order_date) as order_date,
            delivery_state,
            product_category,
            payment_method,
            order_status,
            
            -- Volume metrics
            COUNT(*) as total_orders,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT seller_id) as unique_sellers,
            
            -- Revenue metrics  
            SUM(order_value) as gross_revenue,
            SUM(order_value - discount_applied) as net_revenue,
            SUM(discount_applied) as total_discounts,
            AVG(order_value) as avg_order_value,
            MEDIAN(order_value) as median_order_value,
            
            -- Performance metrics
            COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) as delivered_orders,
            COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) as cancelled_orders,
            COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) as returned_orders,
            
            -- Calculate success rates
            (COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) * 100.0 / COUNT(*)) as delivery_success_rate,
            (COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) * 100.0 / COUNT(*)) as cancellation_rate,
            (COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) * 100.0 / COUNT(*)) as return_rate,
            
            -- Delivery performance
            AVG(CASE 
                WHEN delivery_date IS NOT NULL AND order_status = 'DELIVERED'
                THEN DATEDIFF('day', order_date, delivery_date)
            END) as avg_delivery_days,
            
            -- Payment method analysis
            COUNT(CASE WHEN payment_method = 'COD' THEN 1 END) as cod_orders,
            COUNT(CASE WHEN payment_method = 'UPI' THEN 1 END) as upi_orders,
            COUNT(CASE WHEN payment_method = 'CARD' THEN 1 END) as card_orders,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM order_base
        GROUP BY 
            DATE(order_date), delivery_state, product_category, 
            payment_method, order_status
        ORDER BY order_date DESC, gross_revenue DESC
        """
        
        cursor.execute(order_analytics_sql)
        
        self.logger.info("✅ Order Analytics table created successfully", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def _create_product_performance_metrics(self, cursor) -> bool:
        """Product performance और catalog analytics"""
        self.logger.info("🛍️ Creating Product Performance metrics...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        product_metrics_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.PRODUCT_ANALYTICS.PRODUCT_PERFORMANCE AS
        WITH product_sales AS (
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                p.brand,
                p.price,
                p.seller_id,
                COUNT(o.order_id) as total_orders,
                SUM(o.quantity) as total_quantity_sold,
                SUM(o.order_value) as total_revenue,
                AVG(o.order_value) as avg_selling_price,
                COUNT(DISTINCT o.customer_id) as unique_buyers
            FROM {self.warehouse_config['raw_database']}.PRODUCTS.RAW_PRODUCTS_{today} p
            LEFT JOIN {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today} o 
                ON p.product_id = o.product_id
            GROUP BY p.product_id, p.product_name, p.category, p.brand, p.price, p.seller_id
        ),
        
        product_reviews AS (
            SELECT 
                product_id,
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_reviews,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_reviews,
                MAX(review_date) as latest_review_date
            FROM {self.warehouse_config['raw_database']}.REVIEWS.RAW_REVIEWS_{today}
            GROUP BY product_id
        )
        
        SELECT 
            ps.*,
            COALESCE(pr.total_reviews, 0) as review_count,
            COALESCE(pr.avg_rating, 0) as average_rating,
            COALESCE(pr.positive_reviews, 0) as positive_review_count,
            COALESCE(pr.negative_reviews, 0) as negative_review_count,
            pr.latest_review_date,
            
            -- Performance calculations
            (ps.total_revenue / NULLIF(ps.total_orders, 0)) as revenue_per_order,
            (ps.unique_buyers / NULLIF(ps.total_orders, 0)) as buyer_conversion_rate,
            
            -- Product ranking within category
            RANK() OVER (PARTITION BY ps.category ORDER BY ps.total_revenue DESC) as revenue_rank_in_category,
            RANK() OVER (PARTITION BY ps.category ORDER BY ps.total_orders DESC) as order_rank_in_category,
            RANK() OVER (PARTITION BY ps.category ORDER BY COALESCE(pr.avg_rating, 0) DESC) as rating_rank_in_category,
            
            -- Product classification
            CASE 
                WHEN ps.total_revenue > 100000 THEN 'High Performer'
                WHEN ps.total_revenue > 10000 THEN 'Medium Performer'  
                WHEN ps.total_revenue > 1000 THEN 'Low Performer'
                ELSE 'New/No Sales'
            END as performance_tier,
            
            CASE 
                WHEN COALESCE(pr.avg_rating, 0) >= 4.0 AND ps.total_orders > 50 THEN 'Top Rated'
                WHEN COALESCE(pr.avg_rating, 0) >= 3.5 THEN 'Good Rating'
                WHEN COALESCE(pr.avg_rating, 0) >= 2.5 THEN 'Average Rating'
                WHEN COALESCE(pr.avg_rating, 0) > 0 THEN 'Poor Rating'
                ELSE 'Not Rated'
            END as rating_tier,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM product_sales ps
        LEFT JOIN product_reviews pr ON ps.product_id = pr.product_id
        ORDER BY ps.total_revenue DESC
        """
        
        cursor.execute(product_metrics_sql)
        
        self.logger.info("✅ Product Performance metrics table created", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def _create_revenue_analytics(self, cursor) -> bool:
        """Revenue और financial metrics"""
        self.logger.info("💰 Creating Revenue Analytics...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        revenue_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.REVENUE_METRICS.DAILY_REVENUE AS
        SELECT 
            DATE(order_date) as revenue_date,
            delivery_state,
            product_category,
            
            -- Revenue metrics
            SUM(order_value) as gross_revenue,
            SUM(order_value - discount_applied) as net_revenue,
            SUM(discount_applied) as total_discounts_given,
            
            -- Commission calculations (assumed 10% commission)
            SUM(order_value * 0.10) as estimated_commission,
            SUM((order_value - discount_applied) * 0.10) as net_commission,
            
            -- Order metrics
            COUNT(*) as total_transactions,
            AVG(order_value) as avg_transaction_value,
            
            -- Payment method revenue split
            SUM(CASE WHEN payment_method = 'UPI' THEN order_value ELSE 0 END) as upi_revenue,
            SUM(CASE WHEN payment_method = 'COD' THEN order_value ELSE 0 END) as cod_revenue,
            SUM(CASE WHEN payment_method = 'CARD' THEN order_value ELSE 0 END) as card_revenue,
            
            -- Growth calculations (compared to previous day)
            LAG(SUM(order_value), 1) OVER (
                PARTITION BY delivery_state, product_category 
                ORDER BY DATE(order_date)
            ) as prev_day_revenue,
            
            ((SUM(order_value) - LAG(SUM(order_value), 1) OVER (
                PARTITION BY delivery_state, product_category 
                ORDER BY DATE(order_date)
            )) / NULLIF(LAG(SUM(order_value), 1) OVER (
                PARTITION BY delivery_state, product_category 
                ORDER BY DATE(order_date)
            ), 0)) * 100 as revenue_growth_percent,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today}
        WHERE order_status = 'DELIVERED'
        GROUP BY DATE(order_date), delivery_state, product_category
        ORDER BY revenue_date DESC, gross_revenue DESC
        """
        
        cursor.execute(revenue_sql)
        
        self.logger.info("✅ Revenue Analytics table created", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def _create_operational_metrics(self, cursor) -> bool:
        """Operational KPIs और performance metrics"""
        self.logger.info("⚙️ Creating Operational Metrics...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        ops_metrics_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.OPERATIONAL_METRICS.DAILY_OPS_KPI AS
        WITH daily_ops AS (
            SELECT 
                DATE(order_date) as ops_date,
                delivery_state,
                
                -- Volume metrics
                COUNT(*) as total_orders_processed,
                COUNT(DISTINCT customer_id) as unique_customers_served,
                COUNT(DISTINCT seller_id) as active_sellers,
                
                -- Fulfillment metrics
                COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) as orders_delivered,
                COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) as orders_cancelled,
                COUNT(CASE WHEN order_status = 'RETURNED' THEN 1 END) as orders_returned,
                COUNT(CASE WHEN order_status = 'PENDING' THEN 1 END) as orders_pending,
                
                -- Delivery performance
                AVG(CASE 
                    WHEN delivery_date IS NOT NULL AND order_status = 'DELIVERED'
                    THEN DATEDIFF('day', order_date, delivery_date)
                END) as avg_delivery_time_days,
                
                COUNT(CASE 
                    WHEN delivery_date IS NOT NULL AND order_status = 'DELIVERED'
                    AND DATEDIFF('day', order_date, delivery_date) <= 2
                    THEN 1 
                END) as on_time_deliveries,
                
                -- Payment success rates
                COUNT(CASE WHEN payment_status = 'SUCCESS' THEN 1 END) as successful_payments,
                COUNT(CASE WHEN payment_status = 'FAILED' THEN 1 END) as failed_payments,
                
                SUM(order_value) as total_gmv
                
            FROM {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today}
            GROUP BY DATE(order_date), delivery_state
        )
        
        SELECT 
            *,
            
            -- Calculate operational KPIs
            (orders_delivered * 100.0 / total_orders_processed) as fulfillment_rate,
            (orders_cancelled * 100.0 / total_orders_processed) as cancellation_rate,
            (orders_returned * 100.0 / orders_delivered) as return_rate,
            (on_time_deliveries * 100.0 / orders_delivered) as on_time_delivery_rate,
            (successful_payments * 100.0 / (successful_payments + failed_payments)) as payment_success_rate,
            
            -- Efficiency metrics
            (total_gmv / total_orders_processed) as average_order_value,
            (total_orders_processed / active_sellers) as orders_per_seller,
            (total_gmv / unique_customers_served) as revenue_per_customer,
            
            -- Operational health score (0-100)
            LEAST(100, 
                (fulfillment_rate * 0.3) +
                ((100 - cancellation_rate) * 0.2) + 
                ((100 - return_rate) * 0.2) +
                (on_time_delivery_rate * 0.2) +
                (payment_success_rate * 0.1)
            ) as operational_health_score,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM daily_ops
        ORDER BY ops_date DESC, total_gmv DESC
        """
        
        cursor.execute(ops_metrics_sql)
        
        self.logger.info("✅ Operational Metrics table created", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def _create_ml_feature_store(self, cursor) -> bool:
        """ML models के लिए feature store"""
        self.logger.info("🤖 Creating ML Feature Store...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        today = datetime.now().strftime('%Y%m%d')
        
        ml_features_sql = f"""
        CREATE OR REPLACE TABLE {self.warehouse_config['analytics_database']}.ML_FEATURES.CUSTOMER_FEATURES AS
        WITH customer_behavior AS (
            SELECT 
                customer_id,
                COUNT(*) as total_orders,
                SUM(order_value) as total_spent,
                AVG(order_value) as avg_order_value,
                MAX(order_date) as last_order_date,
                MIN(order_date) as first_order_date,
                COUNT(DISTINCT product_category) as categories_explored,
                COUNT(DISTINCT DATE(order_date)) as active_days,
                
                -- Behavioral patterns
                COUNT(CASE WHEN HOUR(order_timestamp) BETWEEN 9 AND 17 THEN 1 END) as business_hours_orders,
                COUNT(CASE WHEN DAYOFWEEK(order_date) IN (1,7) THEN 1 END) as weekend_orders,
                COUNT(CASE WHEN payment_method = 'COD' THEN 1 END) as cod_preference,
                
                -- Engagement metrics
                AVG(DATEDIFF('day', LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date), order_date)) as avg_days_between_orders,
                STDDEV(order_value) as order_value_variance,
                
                -- Recent activity (last 30 days)
                COUNT(CASE WHEN order_date >= DATEADD('day', -30, CURRENT_DATE()) THEN 1 END) as orders_last_30_days,
                SUM(CASE WHEN order_date >= DATEADD('day', -30, CURRENT_DATE()) THEN order_value ELSE 0 END) as spent_last_30_days
                
            FROM {self.warehouse_config['raw_database']}.ORDERS.RAW_ORDERS_{today}
            GROUP BY customer_id
        ),
        
        review_behavior AS (
            SELECT 
                customer_id,
                COUNT(*) as reviews_written,
                AVG(rating) as avg_rating_given,
                STDDEV(rating) as rating_variance,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_reviews
            FROM {self.warehouse_config['raw_database']}.REVIEWS.RAW_REVIEWS_{today}
            GROUP BY customer_id
        )
        
        SELECT 
            cb.*,
            COALESCE(rb.reviews_written, 0) as reviews_written,
            COALESCE(rb.avg_rating_given, 0) as avg_rating_given,
            COALESCE(rb.rating_variance, 0) as rating_variance,
            COALESCE(rb.positive_reviews, 0) as positive_reviews_count,
            
            -- Derived features for ML
            DATEDIFF('day', cb.last_order_date, CURRENT_DATE()) as days_since_last_order,
            DATEDIFF('day', cb.first_order_date, CURRENT_DATE()) as customer_lifetime_days,
            
            -- Behavioral scores (0-1 scale)
            LEAST(1.0, cb.total_orders / 50.0) as order_frequency_score,
            LEAST(1.0, cb.total_spent / 100000.0) as spending_score,
            LEAST(1.0, cb.categories_explored / 10.0) as exploration_score,
            LEAST(1.0, COALESCE(rb.reviews_written, 0) / 20.0) as engagement_score,
            
            -- Churn prediction features
            CASE 
                WHEN DATEDIFF('day', cb.last_order_date, CURRENT_DATE()) > 90 THEN 1 
                ELSE 0 
            END as is_churned,
            
            -- Segmentation features
            CASE 
                WHEN cb.total_spent > 50000 AND cb.total_orders > 20 THEN 'High_Value'
                WHEN cb.total_spent > 10000 OR cb.total_orders > 5 THEN 'Regular'
                ELSE 'Low_Value'
            END as value_segment,
            
            CURRENT_TIMESTAMP() as created_at,
            '{self.pipeline_id}' as pipeline_id
            
        FROM customer_behavior cb
        LEFT JOIN review_behavior rb ON cb.customer_id = rb.customer_id
        """
        
        cursor.execute(ml_features_sql)
        
        self.logger.info("✅ ML Feature Store table created", 
                        extra={'pipeline_id': self.pipeline_id})
        return True
    
    def run_elt_pipeline(self) -> ELTMetrics:
        """
        Complete ELT Pipeline Execution
        ==============================
        
        Modern cloud-native ELT approach का complete implementation।
        """
        self.logger.info("🚀 Starting Snowflake ELT Pipeline...", 
                        extra={'pipeline_id': self.pipeline_id})
        
        self.metrics = ELTMetrics(
            pipeline_name="Flipkart E-commerce ELT",
            start_time=datetime.now()
        )
        
        try:
            # Step 1: Initialize infrastructure
            self.logger.info("📍 Step 1/4: Infrastructure Setup", 
                           extra={'pipeline_id': self.pipeline_id})
            self.initialize_connections()
            self.setup_warehouse_infrastructure()
            
            # Step 2: Extract from multiple sources
            self.logger.info("📍 Step 2/4: Data Extraction", 
                           extra={'pipeline_id': self.pipeline_id})
            extract_start = time.time()
            extracted_data = self.extract_from_flipkart_apis()
            self.metrics.extract_duration_seconds = time.time() - extract_start
            
            # Step 3: Load raw data to warehouse
            self.logger.info("📍 Step 3/4: Raw Data Loading", 
                           extra={'pipeline_id': self.pipeline_id})
            self.load_raw_data_to_snowflake(extracted_data)
            
            # Step 4: Transform in warehouse
            self.logger.info("📍 Step 4/4: Warehouse Transformations", 
                           extra={'pipeline_id': self.pipeline_id})
            self.transform_in_warehouse()
            
            # Calculate final metrics
            self.metrics.end_time = datetime.now()
            self.metrics.data_freshness_minutes = (
                datetime.now() - min(df['_extracted_at'].min() for df in extracted_data.values() if not df.empty)
            ).total_seconds() / 60
            
            # Estimate costs (Snowflake pricing)
            compute_cost = self.metrics.transform_duration_seconds / 3600 * 2.0  # $2/hour for LARGE warehouse
            storage_cost = self.metrics.raw_records_loaded * 0.000023  # $23/TB/month
            self.metrics.cost_estimate_usd = compute_cost + storage_cost
            
            self.logger.info("🎉 ELT Pipeline completed successfully!", 
                           extra={'pipeline_id': self.pipeline_id})
            
            self._log_pipeline_summary()
            return self.metrics
            
        except Exception as e:
            self.metrics.end_time = datetime.now()
            self.logger.error(f"💥 ELT Pipeline failed: {str(e)}", 
                            extra={'pipeline_id': self.pipeline_id})
            raise
        
        finally:
            self._cleanup_connections()
    
    def _log_pipeline_summary(self):
        """Pipeline execution summary logging"""
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
        self.logger.info("📋 ELT PIPELINE SUMMARY", extra={'pipeline_id': self.pipeline_id})
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Pipeline ID: {self.pipeline_id}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Total Duration: {self.metrics.total_duration_minutes():.2f} minutes", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Records Processed: {self.metrics.raw_records_loaded:,}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Sources Integrated: {self.metrics.sources_processed}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Analytics Tables Created: {self.metrics.analytics_tables_created}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Data Freshness: {self.metrics.data_freshness_minutes:.1f} minutes", extra={'pipeline_id': self.pipeline_id})
        self.logger.info(f"Estimated Cost: ${self.metrics.cost_estimate_usd:.2f}", extra={'pipeline_id': self.pipeline_id})
        self.logger.info("=" * 70, extra={'pipeline_id': self.pipeline_id})
    
    def _cleanup_connections(self):
        """Cleanup all connections"""
        if self.snowflake_conn:
            self.snowflake_conn.close()
        if self.sqlalchemy_engine:
            self.sqlalchemy_engine.dispose()
        
        self.logger.info("🧹 Connections cleaned up", 
                        extra={'pipeline_id': self.pipeline_id})

def main():
    """
    Production Snowflake ELT Pipeline
    ================================
    
    Modern cloud data warehouse का power use करके ELT।
    """
    
    print("❄️ Snowflake Modern ELT Pipeline")
    print("=" * 45)
    
    # Production Snowflake configuration
    snowflake_config = {
        'account': 'flipkart.us-east-1',
        'user': 'etl_service_user',
        'password': 'secure_snowflake_password',
        'warehouse': 'LARGE_COMPUTE_WH',
        'database': 'ECOMMERCE_RAW',
        'schema': 'PUBLIC',
        'role': 'ETL_ROLE'
    }
    
    # AWS S3 configuration for external data
    aws_config = {
        'access_key': 'AKIAIOSFODNN7EXAMPLE',
        'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'bucket': 'flipkart-data-lake',
        'region': 'us-east-1'
    }
    
    # Initialize ELT pipeline
    elt_pipeline = SnowflakeELTPipeline(snowflake_config, aws_config)
    
    try:
        # Run complete ELT pipeline
        metrics = elt_pipeline.run_elt_pipeline()
        
        print("\n📊 Pipeline Results:")
        print("=" * 30)
        print(f"✅ Duration: {metrics.total_duration_minutes():.2f} minutes")
        print(f"📦 Records Processed: {metrics.raw_records_loaded:,}")
        print(f"🏭 Analytics Tables: {metrics.analytics_tables_created}")
        print(f"💰 Estimated Cost: ${metrics.cost_estimate_usd:.2f}")
        print(f"⚡ Data Freshness: {metrics.data_freshness_minutes:.1f} minutes")
        
        if metrics.analytics_tables_created >= 5:
            print("\n🎉 ELT Pipeline completed successfully!")
            print("📊 Analytics-ready data available in Snowflake")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


# Production Deployment Guide:
"""
🏗️ Production Snowflake ELT Architecture:

┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources (Extract)                      │
├─────────────────────────────────────────────────────────────────┤
│  • APIs (REST/GraphQL)     • Databases (MySQL/Postgres)       │
│  • File Systems (S3/HDFS)  • Streaming (Kafka/Kinesis)       │
│  • SaaS Tools (Salesforce) • Event Logs (Application)        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Snowflake Data Warehouse                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RAW LAYER (Landing Zone):                                     │
│  • JSON/Parquet files as-is                                   │
│  • No transformations applied                                  │
│  • Schema-on-read approach                                     │
│  • Time-travel enabled (7 days)                               │
│                                                                 │
│  ANALYTICS LAYER (Curated Zone):                              │
│  • Business logic applied                                      │
│  • Dimension & Fact tables                                     │
│  • Aggregated metrics tables                                   │
│  • ML feature stores                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

📊 Scale Numbers:
- Daily data ingestion: 50TB+
- Query performance: Sub-second for dashboards
- Concurrent users: 1000+ analysts
- Data retention: 7 years (compliance)
- Compute auto-scaling: 1-50 nodes based on workload

💰 Cost Optimization:
- Storage: $25/TB/month (compressed)
- Compute: $2-40/hour (based on warehouse size)
- Auto-suspend: 5 minutes idle time
- Result caching: 24 hours (free repeated queries)
- Total monthly cost: ₹15-25 lakhs for 1PB scale

⚡ Performance Features:
- Automatic clustering for large tables
- Materialized views for complex aggregations
- Query result caching
- Zero-copy cloning for dev/test
- Time-travel for data recovery
- Column-level security & masking

ELT > ETL क्यों?
1. **Scalability**: Cloud warehouse की unlimited compute power
2. **Flexibility**: Raw data available for ad-hoc analysis
3. **Speed**: Parallel processing, faster than traditional ETL
4. **Cost**: Pay only for compute used, storage is cheap
5. **Agility**: Schema changes don't break pipelines

Modern data architecture - यही है future! ❄️🚀
"""